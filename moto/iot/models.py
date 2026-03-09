import hashlib
import json
import re
import time
from collections import OrderedDict
from collections.abc import Iterable
from dataclasses import asdict, dataclass, field, replace
from datetime import datetime, timedelta
from json import JSONDecodeError
from re import Pattern
from typing import (
    TYPE_CHECKING,
    Any,
    Optional,
    Union,
)

from cryptography import x509
from cryptography.hazmat._oid import NameOID
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa

from moto.core.base_backend import BackendDict, BaseBackend
from moto.core.common_models import BaseModel, CloudFormationModel
from moto.core.utils import utcnow
from moto.moto_api._internal import mock_random as random
from moto.settings import iot_use_valid_cert
from moto.utilities.paginator import paginate
from moto.utilities.utils import get_partition

from .exceptions import (
    CertificateStateException,
    ConflictException,
    DeleteConflictException,
    InvalidRequestException,
    InvalidStateTransitionException,
    ResourceAlreadyExistsException,
    ResourceNotFoundException,
    ThingStillAttached,
    VersionConflictException,
    VersionsLimitExceededException,
)
from .utils import PAGINATION_MODEL, decapitalize_dict

if TYPE_CHECKING:
    from moto.iotdata.models import FakeShadow


class FakeThing(CloudFormationModel):
    def __init__(
        self,
        thing_name: str,
        thing_type: Optional["FakeThingType"],
        attributes: dict[str, Any],
        account_id: str,
        region_name: str,
        billing_group_name: Optional[str] = None,
    ):
        self.region_name = region_name
        self.account_id = account_id
        self.thing_id = str(random.uuid4())
        self.thing_name = thing_name
        self.thing_type = thing_type
        self.attributes = attributes
        self.arn = f"arn:{get_partition(region_name)}:iot:{region_name}:{account_id}:thing/{thing_name}"
        self.version = 1
        self.billing_group_name = billing_group_name
        # TODO: we need to handle "version"?

        # for iot-data
        self.thing_shadows: dict[Optional[str], FakeShadow] = {}

    def _matches_single_query(self, query_string: str) -> bool:
        if query_string == "*":
            return True
        if query_string.startswith("thingTypeName:"):
            if not self.thing_type:
                return False
            qs = query_string[14:].replace("*", ".*").replace("?", ".")
            return re.search(f"^{qs}$", self.thing_type.thing_type_name) is not None
        if query_string.startswith("thingName:"):
            qs = query_string[10:].replace("*", ".*").replace("?", ".")
            return re.search(f"^{qs}$", self.thing_name) is not None
        if query_string.startswith("thingGroupNames:"):
            thing_group_to_find = query_string.removeprefix("thingGroupNames:")
            thing_group_match = re.compile(f"^{thing_group_to_find}$")

            # Billing group are matched in thingGroupNames field too
            if self.billing_group_name and thing_group_match.match(
                self.billing_group_name
            ):
                return True

            backend = iot_backends[self.account_id][self.region_name]
            all_thing_groups = backend.list_thing_groups(None, None, None)
            for thing_group in all_thing_groups:
                if not thing_group_match.match(thing_group.thing_group_name):
                    continue
                if self.arn in thing_group.things:
                    return True
            return False
        if query_string.startswith("attributes."):
            try:
                k, v = query_string[11:].split(":", 1)
                return self.attributes.get(k) == v
            except ValueError:
                return False
        return query_string in self.thing_name

    def matches(self, query_string: str) -> bool:
        if not query_string.strip():
            return False
        if query_string == "*":
            return True

        # Replace "-" sign at the beginning of a term with a regular NOT operator
        query_string = re.sub(r"(^|\s)-", r"\1NOT ", query_string)

        # Tokenize by spaces, and treat parentheses as separate tokens
        tokens = query_string.replace("(", " ( ").replace(")", " ) ").split()
        # Filter out empty tokens that may result from multiple spaces
        tokens = [token for token in tokens if token]

        precedence = {"OR": 1, "AND": 2, "NOT": 3}
        output_queue: list[str] = []
        operator_stack: list[str] = []

        # Implicit AND handling
        # If a token is an operand, and the previous token was also an operand, we insert an AND operator.
        prev_token_is_operand = False
        processed_tokens = []
        for token in tokens:
            is_operand = token.upper() not in ["AND", "OR", "NOT"] and token not in [
                "(",
                ")",
            ]
            if is_operand and prev_token_is_operand:
                processed_tokens.append("AND")
            processed_tokens.append(token)
            prev_token_is_operand = is_operand
        tokens = processed_tokens

        # Convert to Reverse Polish Notation
        for token in tokens:
            if token.upper() in ("AND", "OR"):
                while (
                    operator_stack
                    and operator_stack[-1] != "("
                    and precedence.get(operator_stack[-1].upper(), 0)
                    >= precedence.get(token.upper(), 0)
                ):
                    output_queue.append(operator_stack.pop())
                operator_stack.append(token)
            elif token.upper() == "NOT":
                operator_stack.append(token)
            elif token == "(":
                operator_stack.append(token)
            elif token == ")":
                while operator_stack and operator_stack[-1] != "(":
                    output_queue.append(operator_stack.pop())
                if not operator_stack or operator_stack[-1] != "(":
                    raise InvalidRequestException("Mismatched parentheses")
                operator_stack.pop()  # Pop '('
            else:  # operand
                output_queue.append(token)

        while operator_stack:
            op = operator_stack.pop()
            if op == "(":
                raise InvalidRequestException("Mismatched parentheses")
            output_queue.append(op)

        # Now evaluate the RPN expression in output_queue
        eval_stack: list[bool] = []
        for token in output_queue:
            if token.upper() == "AND":
                if len(eval_stack) < 2:
                    raise InvalidRequestException("Invalid query syntax")
                stack_op2 = eval_stack.pop()
                stack_op1 = eval_stack.pop()
                eval_stack.append(stack_op1 and stack_op2)
            elif token.upper() == "OR":
                if len(eval_stack) < 2:
                    raise InvalidRequestException("Invalid query syntax")
                stack_op2 = eval_stack.pop()
                stack_op1 = eval_stack.pop()
                eval_stack.append(stack_op1 or stack_op2)
            elif token.upper() == "NOT":
                if len(eval_stack) < 1:
                    raise InvalidRequestException("Invalid query syntax")
                eval_stack.append(not eval_stack.pop())
            else:
                eval_stack.append(self._matches_single_query(token))

        if len(eval_stack) != 1:
            raise InvalidRequestException("Invalid query syntax")

        return eval_stack[0]

    def to_dict(
        self,
        include_default_client_id: bool = False,
        include_connectivity: bool = False,
        include_thing_id: bool = False,
        include_thing_group_names: bool = False,
        include_shadows_as_json: bool = False,
    ) -> dict[str, Any]:
        obj = {
            "thingName": self.thing_name,
            "thingArn": self.arn,
            "attributes": self.attributes,
            "version": self.version,
        }
        if self.thing_type:
            obj["thingTypeName"] = self.thing_type.thing_type_name
        if self.billing_group_name:
            obj["billingGroupName"] = self.billing_group_name
        if include_default_client_id:
            obj["defaultClientId"] = self.thing_name
        if include_connectivity:
            obj["connectivity"] = {
                "connected": True,
                "timestamp": time.mktime(utcnow().timetuple()),
            }
        if include_thing_id:
            obj["thingId"] = self.thing_id
        if include_thing_group_names:
            iot_backend = iot_backends[self.account_id][self.region_name]
            obj["thingGroupNames"] = [
                thing_group.thing_group_name
                for thing_group in iot_backend.list_thing_groups(None, None, None)
                if self.arn in thing_group.things
            ]
        if include_shadows_as_json:
            named_shadows = {
                shadow_name: shadow.to_dict()
                for shadow_name, shadow in self.thing_shadows.items()
                if shadow_name is not None
            }
            converted_response_format = {
                shadow_name: {
                    **shadow_data["state"],
                    "metadata": shadow_data["metadata"],
                    "version": shadow_data["version"],
                    "hasDelta": "delta" in shadow_data["state"],
                }
                for shadow_name, shadow_data in named_shadows.items()
            }
            obj["shadow"] = json.dumps({"name": converted_response_format})
        return obj

    @staticmethod
    def cloudformation_name_type() -> str:
        return "Thing"

    @staticmethod
    def cloudformation_type() -> str:
        return "AWS::IoT::Thing"

    @classmethod
    def has_cfn_attr(cls, attr: str) -> bool:
        return attr in [
            "Arn",
            "Id",
        ]

    def get_cfn_attribute(self, attribute_name: str) -> Any:
        from moto.cloudformation.exceptions import UnformattedGetAttTemplateException

        if attribute_name == "Arn":
            return self.arn
        elif attribute_name == "Id":
            return self.thing_id
        raise UnformattedGetAttTemplateException()

    @classmethod
    def create_from_cloudformation_json(  # type: ignore[misc]
        cls,
        resource_name: str,
        cloudformation_json: Any,
        account_id: str,
        region_name: str,
        **kwargs: Any,
    ) -> "FakeThing":
        iot_backend = iot_backends[account_id][region_name]
        properties = cloudformation_json["Properties"]

        thing_name = properties.get("ThingName", resource_name)
        attribute_payload = properties.get("AttributePayload", "")
        try:
            attributes = json.loads(attribute_payload)
        except JSONDecodeError:
            attributes = None

        return iot_backend.create_thing(
            thing_name=thing_name,
            thing_type_name="",
            attribute_payload=attributes,
        )

    @classmethod
    def update_from_cloudformation_json(  # type: ignore[misc]
        cls,
        original_resource: "FakeThing",
        new_resource_name: str,
        cloudformation_json: Any,
        account_id: str,
        region_name: str,
    ) -> "FakeThing":
        iot_backend = iot_backends[account_id][region_name]
        properties = cloudformation_json["Properties"]
        thing_name = properties.get("ThingName", new_resource_name)
        attribute_payload = properties.get("AttributePayload", "")
        try:
            attributes = json.loads(attribute_payload)
        except JSONDecodeError:
            attributes = None

        if thing_name != original_resource.thing_name:
            iot_backend.delete_thing(original_resource.thing_name)
            return cls.create_from_cloudformation_json(
                new_resource_name, cloudformation_json, account_id, region_name
            )
        else:
            iot_backend.update_thing(
                thing_name=thing_name,
                thing_type_name="",
                attribute_payload=attributes,
                remove_thing_type=False,
            )
            return original_resource

    @classmethod
    def delete_from_cloudformation_json(  # type: ignore[misc]
        cls,
        resource_name: str,
        cloudformation_json: Any,
        account_id: str,
        region_name: str,
    ) -> None:
        iot_backend = iot_backends[account_id][region_name]
        properties = cloudformation_json["Properties"]
        thing_name = properties.get("ThingName", resource_name)

        iot_backend.delete_thing(thing_name=thing_name)


class FakeThingType(CloudFormationModel):
    def __init__(
        self,
        thing_type_name: str,
        thing_type_properties: Optional[dict[str, Any]],
        account_id: str,
        region_name: str,
    ):
        self.account_id = account_id
        self.region_name = region_name
        self.thing_type_name = thing_type_name
        self.thing_type_properties = thing_type_properties
        self.thing_type_id = str(random.uuid4())  # I don't know the rule of id
        self.metadata: dict[str, Any] = {
            "deprecated": False,
            "creationDate": utcnow(),
        }
        self.arn = f"arn:{get_partition(self.region_name)}:iot:{self.region_name}:{self.account_id}:thingtype/{thing_type_name}"

    def to_dict(self) -> dict[str, Any]:
        return {
            "thingTypeName": self.thing_type_name,
            "thingTypeId": self.thing_type_id,
            "thingTypeProperties": self.thing_type_properties,
            "thingTypeMetadata": self.metadata,
            "thingTypeArn": self.arn,
        }

    @staticmethod
    def cloudformation_name_type() -> str:
        return "ThingType"

    @staticmethod
    def cloudformation_type() -> str:
        return "AWS::IoT::ThingType"

    @classmethod
    def has_cfn_attr(cls, attr: str) -> bool:
        return attr in [
            "Arn",
            "Id",
        ]

    def get_cfn_attribute(self, attribute_name: str) -> Any:
        from moto.cloudformation.exceptions import UnformattedGetAttTemplateException

        if attribute_name == "Arn":
            return self.arn
        elif attribute_name == "Id":
            return self.thing_type_id
        raise UnformattedGetAttTemplateException()

    @classmethod
    def create_from_cloudformation_json(  # type: ignore[misc]
        cls,
        resource_name: str,
        cloudformation_json: Any,
        account_id: str,
        region_name: str,
        **kwargs: Any,
    ) -> "FakeThingType":
        iot_backend = iot_backends[account_id][region_name]
        properties = cloudformation_json["Properties"]

        thing_type_name = properties.get("ThingTypeName", resource_name)
        thing_type_properties = properties.get("ThingTypeProperties", {})

        type_name, type_arn = iot_backend.create_thing_type(
            thing_type_name=thing_type_name, thing_type_properties=thing_type_properties
        )
        return iot_backend.thing_types[type_arn]

    @classmethod
    def update_from_cloudformation_json(  # type: ignore[misc]
        cls,
        original_resource: "FakeThingType",
        new_resource_name: str,
        cloudformation_json: Any,
        account_id: str,
        region_name: str,
    ) -> "FakeThingType":
        iot_backend = iot_backends[account_id][region_name]

        iot_backend.delete_thing_type(thing_type_name=original_resource.thing_type_name)
        return cls.create_from_cloudformation_json(
            new_resource_name, cloudformation_json, account_id, region_name
        )

    @classmethod
    def delete_from_cloudformation_json(  # type: ignore[misc]
        cls,
        resource_name: str,
        cloudformation_json: Any,
        account_id: str,
        region_name: str,
    ) -> None:
        properties = cloudformation_json["Properties"]
        thing_type_name = properties.get("ThingTypeName", resource_name)

        iot_backend = iot_backends[account_id][region_name]
        iot_backend.delete_thing_type(thing_type_name=thing_type_name)


class FakeThingGroup(BaseModel):
    def __init__(
        self,
        thing_group_name: str,
        parent_group_name: str,
        thing_group_properties: dict[str, str],
        account_id: str,
        region_name: str,
        thing_groups: dict[str, "FakeThingGroup"],
    ):
        self.account_id = account_id
        self.region_name = region_name
        self.thing_group_name = thing_group_name
        self.thing_group_id = str(random.uuid4())  # I don't know the rule of id
        self.version = 1  # TODO: tmp
        self.parent_group_name = parent_group_name
        self.thing_group_properties = thing_group_properties or {}
        self.metadata: dict[str, Any] = {"creationDate": utcnow()}
        if parent_group_name:
            self.metadata["parentGroupName"] = parent_group_name
            # initilize rootToParentThingGroups
            if "rootToParentThingGroups" not in self.metadata:
                self.metadata["rootToParentThingGroups"] = []
            # search for parent arn
            for thing_group in thing_groups.values():
                if thing_group.thing_group_name == parent_group_name:
                    parent_thing_group_structure = thing_group
                    break
            # if parent arn found (should always be found)
            if parent_thing_group_structure:
                # copy parent's rootToParentThingGroups
                if "rootToParentThingGroups" in parent_thing_group_structure.metadata:
                    self.metadata["rootToParentThingGroups"].extend(
                        parent_thing_group_structure.metadata["rootToParentThingGroups"]
                    )
                self.metadata["rootToParentThingGroups"].extend(
                    [
                        {
                            "groupName": parent_group_name,
                            "groupArn": parent_thing_group_structure.arn,  # type: ignore
                        }
                    ]
                )
        self.arn = f"arn:{get_partition(self.region_name)}:iot:{self.region_name}:{self.account_id}:thinggroup/{thing_group_name}"
        self.things: dict[str, FakeThing] = OrderedDict()

    def to_dict(self) -> dict[str, Any]:
        return {
            "thingGroupName": self.thing_group_name,
            "thingGroupId": self.thing_group_id,
            "version": self.version,
            "thingGroupProperties": self.thing_group_properties,
            "thingGroupMetadata": self.metadata,
            "thingGroupArn": self.arn,
        }


class FakeBillingGroup(CloudFormationModel):
    def __init__(
        self,
        billing_group_name: str,
        billing_group_properties: Optional[dict[str, Any]],
        account_id: str,
        region_name: str,
    ):
        self.account_id = account_id
        self.region_name = region_name
        self.billing_group_name = billing_group_name
        self.billing_group_properties = billing_group_properties or {}
        self.billing_group_id = str(random.uuid4())
        self.arn = f"arn:{get_partition(self.region_name)}:iot:{self.region_name}:{self.account_id}:billinggroup/{billing_group_name}"
        self.version = 1
        self.things: list[str] = []
        self.metadata: dict[str, Any] = {"creationDate": utcnow()}

    def to_dict(self) -> dict[str, Any]:
        return {
            "billingGroupName": self.billing_group_name,
            "billingGroupArn": self.arn,
            "billingGroupId": self.billing_group_id,
        }

    def to_short_dict(self) -> dict[str, Any]:
        return {
            "groupName": self.billing_group_name,
            "groupArn": self.arn,
        }

    def to_description_dict(self) -> dict[str, Any]:
        return {
            "billingGroupName": self.billing_group_name,
            "billingGroupId": self.billing_group_id,
            "billingGroupArn": self.arn,
            "billingGroupProperties": self.billing_group_properties,
            "billingGroupMetadata": self.metadata,
        }

    @staticmethod
    def cloudformation_name_type() -> str:
        return "BillingGroup"

    @staticmethod
    def cloudformation_type() -> str:
        return "AWS::IoT::BillingGroup"

    @classmethod
    def has_cfn_attr(cls, attr: str) -> bool:
        return attr in ["Arn", "Id"]

    def get_cfn_attribute(self, attribute_name: str) -> Any:
        from moto.cloudformation.exceptions import UnformattedGetAttTemplateException

        if attribute_name == "Arn":
            return self.arn
        elif attribute_name == "Id":
            return self.billing_group_id
        raise UnformattedGetAttTemplateException()

    @classmethod
    def create_from_cloudformation_json(  # type: ignore[misc]
        cls,
        resource_name: str,
        cloudformation_json: Any,
        account_id: str,
        region_name: str,
        **kwargs: Any,
    ) -> "FakeBillingGroup":
        iot_backend = iot_backends[account_id][region_name]
        properties = cloudformation_json.get("Properties", {})
        billing_group_name = properties.get("BillingGroupName", resource_name)
        billing_group_properties = properties.get("BillingGroupProperties")

        return iot_backend.create_billing_group(
            billing_group_name=billing_group_name,
            billing_group_properties=billing_group_properties,
        )

    @classmethod
    def update_from_cloudformation_json(  # type: ignore[misc]
        cls,
        original_resource: "FakeBillingGroup",
        new_resource_name: str,
        cloudformation_json: Any,
        account_id: str,
        region_name: str,
    ) -> "FakeBillingGroup":
        iot_backend = iot_backends[account_id][region_name]
        properties = cloudformation_json.get("Properties", {})
        billing_group_name = properties.get("BillingGroupName", new_resource_name)
        billing_group_properties = properties.get("BillingGroupProperties")

        if billing_group_name != original_resource.billing_group_name:
            iot_backend.delete_billing_group(original_resource.billing_group_name)
            return cls.create_from_cloudformation_json(
                new_resource_name, cloudformation_json, account_id, region_name
            )
        else:
            iot_backend.update_billing_group(
                billing_group_name=billing_group_name,
                billing_group_properties=billing_group_properties,
                expected_version=original_resource.version,
            )
            return original_resource

    @classmethod
    def delete_from_cloudformation_json(  # type: ignore[misc]
        cls,
        resource_name: str,
        cloudformation_json: Any,
        account_id: str,
        region_name: str,
    ) -> None:
        iot_backend = iot_backends[account_id][region_name]
        properties = cloudformation_json.get("Properties", {})
        billing_group_name = properties.get("BillingGroupName", resource_name)
        iot_backend.delete_billing_group(billing_group_name=billing_group_name)


class FakeCertificate(BaseModel):
    def __init__(
        self,
        certificate_pem: str,
        status: str,
        account_id: str,
        region_name: str,
        ca_certificate_id: Optional[str] = None,
    ):
        self.certificate_id = self.compute_cert_id(certificate_pem)
        self.arn = f"arn:{get_partition(region_name)}:iot:{region_name}:{account_id}:cert/{self.certificate_id}"
        self.certificate_pem = certificate_pem

        self.status = status

        self.owner = account_id
        self.transfer_data: dict[str, str] = {}
        self.creation_date = utcnow()
        self.last_modified_date = self.creation_date
        self.validity_not_before = utcnow() - timedelta(days=1)
        self.validity_not_after = utcnow() + timedelta(days=1)
        self.ca_certificate_id = ca_certificate_id

    def compute_cert_id(self, certificate_pem: str) -> str:
        if iot_use_valid_cert():
            return self.compute_der_cert_id(certificate_pem)
        else:
            return self.compute_pem_cert_id(certificate_pem)

    def compute_pem_cert_id(self, certificate_pem: str) -> str:
        """
        Original (incorrect) PEM-based hash kept for backwards compatibility
        with existing tests which may or may not use valid certs. Also useful
        for simplifying tests that don't require a real cert.
        """
        m = hashlib.sha256()
        m.update(certificate_pem.encode("utf-8"))
        return m.hexdigest()

    def compute_der_cert_id(self, certificate_pem: str) -> str:
        """
        Compute the certificate hash based on DER encoding
        """
        return hashlib.sha256(
            x509.load_pem_x509_certificate(
                certificate_pem.encode("utf-8")
            ).public_bytes(serialization.Encoding.DER)
        ).hexdigest()

    def to_dict(self) -> dict[str, Any]:
        return {
            "certificateArn": self.arn,
            "certificateId": self.certificate_id,
            "caCertificateId": self.ca_certificate_id,
            "status": self.status,
            "creationDate": self.creation_date,
        }

    def to_description_dict(self) -> dict[str, Any]:
        """
        You might need keys below in some situation
          - caCertificateId
          - previousOwnedBy
        """
        return {
            "certificateArn": self.arn,
            "certificateId": self.certificate_id,
            "status": self.status,
            "certificatePem": self.certificate_pem,
            "ownedBy": self.owner,
            "creationDate": self.creation_date,
            "lastModifiedDate": self.last_modified_date,
            "validity": {
                "notBefore": self.validity_not_before,
                "notAfter": self.validity_not_after,
            },
            "transferData": self.transfer_data,
        }


class FakeCaCertificate(FakeCertificate):
    def __init__(
        self,
        ca_certificate: str,
        status: str,
        account_id: str,
        region_name: str,
        registration_config: dict[str, str],
    ):
        super().__init__(
            certificate_pem=ca_certificate,
            status=status,
            account_id=account_id,
            region_name=region_name,
            ca_certificate_id=None,
        )
        self.registration_config = registration_config


class FakePolicy(CloudFormationModel):
    def __init__(
        self,
        name: str,
        document: dict[str, Any],
        account_id: str,
        region_name: str,
        default_version_id: str = "1",
    ):
        self.name = name
        self.document = document
        self.arn = f"arn:{get_partition(region_name)}:iot:{region_name}:{account_id}:policy/{name}"
        self.default_version_id = default_version_id
        self.versions = [
            FakePolicyVersion(self.name, document, True, account_id, region_name)
        ]
        self._max_version_id = self.versions[0]._version_id

    def to_get_dict(self) -> dict[str, Any]:
        return {
            "policyName": self.name,
            "policyArn": self.arn,
            "policyDocument": self.document,
            "defaultVersionId": self.default_version_id,
        }

    def to_dict_at_creation(self) -> dict[str, Any]:
        return {
            "policyName": self.name,
            "policyArn": self.arn,
            "policyDocument": self.document,
            "policyVersionId": self.default_version_id,
        }

    def to_dict(self) -> dict[str, str]:
        return {"policyName": self.name, "policyArn": self.arn}

    @staticmethod
    def cloudformation_name_type() -> str:
        return "Policy"

    @staticmethod
    def cloudformation_type() -> str:
        return "AWS::IoT::Policy"

    @classmethod
    def has_cfn_attr(cls, attr: str) -> bool:
        return attr in [
            "Arn",
            "Id",
        ]

    def get_cfn_attribute(self, attribute_name: str) -> Any:
        from moto.cloudformation.exceptions import UnformattedGetAttTemplateException

        if attribute_name == "Arn":
            return self.arn
        elif attribute_name == "Id":
            return self.name + "_" + str(self._max_version_id)
        raise UnformattedGetAttTemplateException()

    @classmethod
    def create_from_cloudformation_json(  # type: ignore[misc]
        cls,
        resource_name: str,
        cloudformation_json: Any,
        account_id: str,
        region_name: str,
        **kwargs: Any,
    ) -> "FakePolicy":
        iot_backend = iot_backends[account_id][region_name]
        properties = cloudformation_json["Properties"]

        policy_name = properties.get("PolicyName", resource_name)
        policy_document = properties.get("PolicyDocument", {})

        return iot_backend.create_policy(
            policy_name=policy_name, policy_document=policy_document
        )

    @classmethod
    def update_from_cloudformation_json(  # type: ignore[misc]
        cls,
        original_resource: "FakePolicy",
        new_resource_name: str,
        cloudformation_json: Any,
        account_id: str,
        region_name: str,
    ) -> "FakePolicy":
        iot_backend = iot_backends[account_id][region_name]
        properties = cloudformation_json["Properties"]
        new_policy_name = properties.get("PolicyName", new_resource_name)
        policy_document = properties.get("PolicyDocument", {})

        if original_resource.name != new_policy_name:
            iot_backend.delete_policy(policy_name=original_resource.name)
            return iot_backend.create_policy(
                policy_name=new_policy_name, policy_document=policy_document
            )
        else:
            iot_backend.create_policy_version(
                policy_name=original_resource.name,
                policy_document=policy_document,
                set_as_default=True,
            )
            return original_resource

    @classmethod
    def delete_from_cloudformation_json(  # type: ignore[misc]
        cls,
        resource_name: str,
        cloudformation_json: Any,
        account_id: str,
        region_name: str,
    ) -> None:
        properties = cloudformation_json["Properties"]
        policy_name = properties.get("PolicyName", resource_name)

        iot_backend = iot_backends[account_id][region_name]
        iot_backend.delete_policy(policy_name=policy_name)


class FakePolicyVersion:
    def __init__(
        self,
        policy_name: str,
        document: dict[str, Any],
        is_default: bool,
        account_id: str,
        region_name: str,
        version_id: int = 1,
    ):
        self.name = policy_name
        self.arn = f"arn:{get_partition(region_name)}:iot:{region_name}:{account_id}:policy/{policy_name}"
        self.document = document or {}
        self.is_default = is_default
        self._version_id = version_id

        self.create_datetime = utcnow()
        self.last_modified_datetime = utcnow()

    @property
    def version_id(self) -> str:
        return str(self._version_id)

    def to_get_dict(self) -> dict[str, Any]:
        return {
            "policyName": self.name,
            "policyArn": self.arn,
            "policyDocument": self.document,
            "policyVersionId": self.version_id,
            "isDefaultVersion": self.is_default,
            "creationDate": self.create_datetime,
            "lastModifiedDate": self.last_modified_datetime,
            "generationId": self.version_id,
        }

    def to_dict_at_creation(self) -> dict[str, Any]:
        return {
            "policyArn": self.arn,
            "policyDocument": self.document,
            "policyVersionId": self.version_id,
            "isDefaultVersion": self.is_default,
        }

    def to_dict(self) -> dict[str, Any]:
        return {
            "versionId": self.version_id,
            "isDefaultVersion": self.is_default,
            "createDate": self.create_datetime,
        }


class FakeJob(BaseModel):
    JOB_ID_REGEX_PATTERN = "[a-zA-Z0-9_-]"
    JOB_ID_REGEX = re.compile(JOB_ID_REGEX_PATTERN)

    def __init__(
        self,
        job_id: str,
        targets: list[str],
        document_source: str,
        document: str,
        description: str,
        presigned_url_config: dict[str, Any],
        target_selection: str,
        job_executions_rollout_config: dict[str, Any],
        document_parameters: dict[str, str],
        abort_config: dict[str, list[dict[str, Any]]],
        job_execution_retry_config: dict[str, Any],
        scheduling_config: dict[str, Any],
        timeout_config: dict[str, Any],
        account_id: str,
        region_name: str,
    ):
        if not self._job_id_matcher(self.JOB_ID_REGEX, job_id):
            raise InvalidRequestException()

        self.account_id = account_id
        self.region_name = region_name
        self.job_id = job_id
        self.job_arn = f"arn:{get_partition(self.region_name)}:iot:{self.region_name}:{self.account_id}:job/{job_id}"
        self.targets = targets
        self.document_source = document_source
        self.document = document
        self.force = False
        self.description = description
        self.presigned_url_config = presigned_url_config
        self.target_selection = target_selection
        self.job_executions_rollout_config = job_executions_rollout_config
        self.abort_config = abort_config
        self.job_execution_retry_config = job_execution_retry_config
        self.scheduling_config = scheduling_config
        self.timeout_config = timeout_config
        self.status = "QUEUED"  # IN_PROGRESS | CANCELED | COMPLETED
        self.comment: Optional[str] = None
        self.reason_code: Optional[str] = None
        self.created_at = utcnow()
        self.last_updated_at = utcnow()
        self.completed_at = None
        self.job_process_details = {
            "processingTargets": targets,
            "numberOfQueuedThings": 1,
            "numberOfCanceledThings": 0,
            "numberOfSucceededThings": 0,
            "numberOfFailedThings": 0,
            "numberOfRejectedThings": 0,
            "numberOfInProgressThings": 0,
            "numberOfRemovedThings": 0,
        }
        self.document_parameters = document_parameters

    def to_dict(self) -> dict[str, Any]:
        obj = {
            "jobArn": self.job_arn,
            "jobId": self.job_id,
            "targets": self.targets,
            "description": self.description,
            "presignedUrlConfig": self.presigned_url_config,
            "targetSelection": self.target_selection,
            "timeoutConfig": self.timeout_config,
            "status": self.status,
            "comment": self.comment,
            "forceCanceled": self.force,
            "reasonCode": self.reason_code,
            "createdAt": self.created_at,
            "lastUpdatedAt": self.last_updated_at,
            "completedAt": self.completed_at,
            "jobProcessDetails": self.job_process_details,
            "documentParameters": self.document_parameters,
            "document": self.document,
            "documentSource": self.document_source,
        }

        return obj

    def _job_id_matcher(self, regex: Pattern[str], argument: str) -> bool:
        regex_match = regex.match(argument) is not None
        length_match = len(argument) <= 64
        return regex_match and length_match


class FakeJobExecution(BaseModel):
    def __init__(
        self,
        job_id: str,
        thing_arn: str,
        status: str = "QUEUED",
        force_canceled: bool = False,
        status_details_map: Optional[dict[str, Any]] = None,
    ):
        self.job_id = job_id
        self.status = status  # IN_PROGRESS | CANCELED | COMPLETED
        self.force_canceled = force_canceled
        self.status_details_map = status_details_map or {}
        self.thing_arn = thing_arn
        self.queued_at = utcnow()
        self.started_at = utcnow()
        self.last_updated_at = utcnow()
        self.execution_number = 123
        self.version_number = 123
        self.approximate_seconds_before_time_out = 123

    def to_get_dict(self) -> dict[str, Any]:
        return {
            "jobId": self.job_id,
            "status": self.status,
            "forceCanceled": self.force_canceled,
            "statusDetails": {"detailsMap": self.status_details_map},
            "thingArn": self.thing_arn,
            "queuedAt": self.queued_at,
            "startedAt": self.started_at,
            "lastUpdatedAt": self.last_updated_at,
            "executionNumber": self.execution_number,
            "versionNumber": self.version_number,
            "approximateSecondsBeforeTimedOut": self.approximate_seconds_before_time_out,
        }

    def to_dict(self) -> dict[str, Any]:
        return {
            "jobId": self.job_id,
            "thingArn": self.thing_arn,
            "jobExecutionSummary": {
                "status": self.status,
                "queuedAt": self.queued_at,
                "startedAt": self.started_at,
                "lastUpdatedAt": self.last_updated_at,
                "executionNumber": self.execution_number,
            },
        }


class FakeJobTemplate(CloudFormationModel):
    JOB_TEMPLATE_ID_REGEX_PATTERN = "[a-zA-Z0-9_-]+"
    JOB_TEMPLATE_ID_REGEX = re.compile(JOB_TEMPLATE_ID_REGEX_PATTERN)

    def __init__(
        self,
        job_template_id: str,
        document_source: str,
        document: str,
        description: str,
        presigned_url_config: dict[str, Any],
        job_executions_rollout_config: dict[str, Any],
        abort_config: dict[str, list[dict[str, Any]]],
        job_execution_retry_config: dict[str, Any],
        timeout_config: dict[str, Any],
        account_id: str,
        region_name: str,
    ):
        if not self._job_template_id_matcher(job_template_id):
            raise InvalidRequestException()

        self.account_id = account_id
        self.region_name = region_name
        self.job_template_id = job_template_id
        self.job_template_arn = f"arn:{get_partition(self.region_name)}:iot:{self.region_name}:{self.account_id}:jobtemplate/{job_template_id}"
        self.document_source = document_source
        self.document = document
        self.description = description
        self.presigned_url_config = presigned_url_config
        self.job_executions_rollout_config = job_executions_rollout_config
        self.abort_config = abort_config
        self.job_execution_retry_config = job_execution_retry_config
        self.timeout_config = timeout_config
        self.created_at = utcnow()

    def to_dict(self) -> dict[str, Union[str, datetime]]:
        return {
            "jobTemplateArn": self.job_template_arn,
            "jobTemplateId": self.job_template_id,
            "description": self.description,
            "createdAt": self.created_at,
        }

    def _job_template_id_matcher(self, argument: str) -> bool:
        return (
            self.JOB_TEMPLATE_ID_REGEX.fullmatch(argument) is not None
            and len(argument) <= 64
        )

    @staticmethod
    def cloudformation_name_type() -> str:
        return "JobTemplate"

    @staticmethod
    def cloudformation_type() -> str:
        return "AWS::IoT::JobTemplate"

    @classmethod
    def has_cfn_attr(cls, attr: str) -> bool:
        return attr in [
            "Arn",
        ]

    def get_cfn_attribute(self, attribute_name: str) -> Any:
        from moto.cloudformation.exceptions import UnformattedGetAttTemplateException

        if attribute_name == "Arn":
            return self.job_template_arn
        raise UnformattedGetAttTemplateException()

    @classmethod
    def create_from_cloudformation_json(  # type: ignore[misc]
        cls,
        resource_name: str,
        cloudformation_json: Any,
        account_id: str,
        region_name: str,
        **kwargs: Any,
    ) -> "FakeJobTemplate":
        iot_backend = iot_backends[account_id][region_name]
        properties = cloudformation_json["Properties"]

        return iot_backend.create_job_template(
            job_template_id=properties.get("JobTemplateId", resource_name),
            document_source=properties.get("DocumentSource", ""),
            document=properties.get("Document"),
            description=properties.get("Description"),
            presigned_url_config=decapitalize_dict(
                properties.get("PresignedUrlConfig", {})
            ),
            job_executions_rollout_config=decapitalize_dict(
                properties.get("JobExecutionsRolloutConfig", {})
            ),
            abort_config=decapitalize_dict(properties.get("AbortConfig", {})),
            job_execution_retry_config=decapitalize_dict(
                properties.get("JobExecutionsRetryConfig", {})
            ),
            timeout_config=decapitalize_dict(properties.get("TimeoutConfig", {})),
        )

    @classmethod
    def update_from_cloudformation_json(  # type: ignore[misc]
        cls,
        original_resource: "FakeJobTemplate",
        new_resource_name: str,
        cloudformation_json: Any,
        account_id: str,
        region_name: str,
    ) -> "FakeJobTemplate":
        iot_backend = iot_backends[account_id][region_name]
        iot_backend.delete_job_template(
            job_template_id=original_resource.job_template_id
        )

        return cls.create_from_cloudformation_json(
            new_resource_name, cloudformation_json, account_id, region_name
        )

    @classmethod
    def delete_from_cloudformation_json(  # type: ignore[misc]
        cls,
        resource_name: str,
        cloudformation_json: Any,
        account_id: str,
        region_name: str,
    ) -> None:
        properties = cloudformation_json["Properties"]
        job_template_id = properties.get("JobTemplateId", resource_name)

        iot_backend = iot_backends[account_id][region_name]
        iot_backend.delete_job_template(job_template_id=job_template_id)


class FakeEndpoint(BaseModel):
    def __init__(self, endpoint_type: str, region_name: str):
        if endpoint_type not in [
            "iot:Data",
            "iot:Data-ATS",
            "iot:CredentialProvider",
            "iot:Jobs",
        ]:
            raise InvalidRequestException(
                " An error occurred (InvalidRequestException) when calling the DescribeEndpoint "
                f"operation: Endpoint type {endpoint_type} not recognized."
            )
        self.region_name = region_name
        identifier = random.get_random_string(length=14, lower_case=True)
        if endpoint_type == "iot:Data":
            self.endpoint = f"{identifier}.iot.{self.region_name}.amazonaws.com"
        elif "iot:Data-ATS" in endpoint_type:
            self.endpoint = f"{identifier}-ats.iot.{self.region_name}.amazonaws.com"
        elif "iot:CredentialProvider" in endpoint_type:
            self.endpoint = (
                f"{identifier}.credentials.iot.{self.region_name}.amazonaws.com"
            )
        elif "iot:Jobs" in endpoint_type:
            self.endpoint = f"{identifier}.jobs.iot.{self.region_name}.amazonaws.com"
        self.endpoint_type = endpoint_type

    def to_get_dict(self) -> dict[str, str]:
        return {
            "endpointAddress": self.endpoint,
        }

    def to_dict(self) -> dict[str, str]:
        return {
            "endpointAddress": self.endpoint,
        }


class FakeRule(BaseModel):
    def __init__(
        self,
        rule_name: str,
        description: str,
        created_at: datetime,
        rule_disabled: bool,
        topic_pattern: Optional[str],
        actions: list[dict[str, Any]],
        error_action: dict[str, Any],
        sql: str,
        aws_iot_sql_version: str,
        account_id: str,
        region_name: str,
    ):
        self.account_id = account_id
        self.region_name = region_name
        self.rule_name = rule_name
        self.description = description or ""
        self.created_at = created_at
        self.rule_disabled = bool(rule_disabled)
        self.topic_pattern = topic_pattern
        self.actions = actions or []
        self.error_action = error_action or {}
        self.sql = sql
        self.aws_iot_sql_version = aws_iot_sql_version or "2016-03-23"
        self.arn = f"arn:{get_partition(self.region_name)}:iot:{self.region_name}:{self.account_id}:rule/{rule_name}"

    def to_get_dict(self) -> dict[str, Any]:
        return {
            "rule": {
                "actions": self.actions,
                "awsIotSqlVersion": self.aws_iot_sql_version,
                "createdAt": self.created_at,
                "description": self.description,
                "errorAction": self.error_action,
                "ruleDisabled": self.rule_disabled,
                "ruleName": self.rule_name,
                "sql": self.sql,
            },
            "ruleArn": self.arn,
        }

    def to_dict(self) -> dict[str, Any]:
        return {
            "ruleName": self.rule_name,
            "createdAt": self.created_at,
            "ruleArn": self.arn,
            "ruleDisabled": self.rule_disabled,
            "topicPattern": self.topic_pattern,
        }


class FakeDomainConfiguration(BaseModel):
    def __init__(
        self,
        account_id: str,
        region_name: str,
        domain_configuration_name: str,
        domain_name: str,
        server_certificate_arns: list[str],
        domain_configuration_status: str,
        service_type: str,
        authorizer_config: Optional[dict[str, Any]],
        domain_type: str,
    ):
        if service_type and service_type not in ["DATA", "CREDENTIAL_PROVIDER", "JOBS"]:
            raise InvalidRequestException(
                "An error occurred (InvalidRequestException) when calling the DescribeDomainConfiguration "
                f"operation: Service type {service_type} not recognized."
            )
        self.domain_configuration_name = domain_configuration_name
        self.domain_configuration_arn = f"arn:{get_partition(region_name)}:iot:{region_name}:{account_id}:domainconfiguration/{domain_configuration_name}/{random.get_random_string(length=5)}"
        self.domain_name = domain_name
        self.server_certificates = []
        if server_certificate_arns:
            for sc in server_certificate_arns:
                self.server_certificates.append(
                    {"serverCertificateArn": sc, "serverCertificateStatus": "VALID"}
                )
        self.domain_configuration_status = domain_configuration_status
        self.service_type = service_type
        self.authorizer_config = authorizer_config
        self.domain_type = domain_type
        self.last_status_change_date = utcnow()

    def to_description_dict(self) -> dict[str, Any]:
        return {
            "domainConfigurationName": self.domain_configuration_name,
            "domainConfigurationArn": self.domain_configuration_arn,
            "domainName": self.domain_name,
            "serverCertificates": self.server_certificates,
            "authorizerConfig": self.authorizer_config,
            "domainConfigurationStatus": self.domain_configuration_status,
            "serviceType": self.service_type,
            "domainType": self.domain_type,
            "lastStatusChangeDate": self.last_status_change_date,
        }

    def to_dict(self) -> dict[str, Any]:
        return {
            "domainConfigurationName": self.domain_configuration_name,
            "domainConfigurationArn": self.domain_configuration_arn,
        }


class FakeRoleAlias(CloudFormationModel):
    def __init__(
        self,
        role_alias: str,
        role_arn: str,
        account_id: str,
        region_name: str,
        credential_duration_seconds: int = 3600,
    ):
        self.role_alias = role_alias
        self.role_arn = role_arn
        self.credential_duration_seconds = credential_duration_seconds
        self.account_id = account_id
        self.region_name = region_name
        self.creation_date = utcnow()
        self.last_modified_date = self.creation_date
        self.arn = f"arn:{get_partition(self.region_name)}:iot:{self.region_name}:{self.account_id}:rolealias/{role_alias}"

    def to_dict(self) -> dict[str, Any]:
        return {
            "roleAlias": self.role_alias,
            "roleAliasArn": self.arn,
            "roleArn": self.role_arn,
            "owner": self.account_id,
            "credentialDurationSeconds": self.credential_duration_seconds,
            "creationDate": self.creation_date,
            "lastModifiedDate": self.last_modified_date,
        }

    @staticmethod
    def cloudformation_name_type() -> str:
        return "RoleAlias"

    @staticmethod
    def cloudformation_type() -> str:
        return "AWS::IoT::RoleAlias"

    @classmethod
    def has_cfn_attr(cls, attr: str) -> bool:
        return attr in [
            "RoleAliasArn",
        ]

    def get_cfn_attribute(self, attribute_name: str) -> Any:
        from moto.cloudformation.exceptions import UnformattedGetAttTemplateException

        if attribute_name == "RoleAliasArn":
            return self.arn
        raise UnformattedGetAttTemplateException()

    @classmethod
    def create_from_cloudformation_json(  # type: ignore[misc]
        cls,
        resource_name: str,
        cloudformation_json: Any,
        account_id: str,
        region_name: str,
        **kwargs: Any,
    ) -> "FakeRoleAlias":
        iot_backend = iot_backends[account_id][region_name]
        properties = cloudformation_json["Properties"]

        role_alias_name = properties.get("RoleAlias", resource_name)
        role_arn = properties.get("RoleArn")
        credential_duration_seconds = properties.get("CredentialDurationSeconds", 3600)

        return iot_backend.create_role_alias(
            role_alias_name=role_alias_name,
            role_arn=role_arn,
            credential_duration_seconds=credential_duration_seconds,
        )

    @classmethod
    def update_from_cloudformation_json(  # type: ignore[misc]
        cls,
        original_resource: "FakeRoleAlias",
        new_resource_name: str,
        cloudformation_json: Any,
        account_id: str,
        region_name: str,
    ) -> "FakeRoleAlias":
        iot_backend = iot_backends[account_id][region_name]
        iot_backend.delete_role_alias(role_alias_name=original_resource.role_alias)
        return cls.create_from_cloudformation_json(
            new_resource_name, cloudformation_json, account_id, region_name
        )

    @classmethod
    def delete_from_cloudformation_json(  # type: ignore[misc]
        cls,
        resource_name: str,
        cloudformation_json: Any,
        account_id: str,
        region_name: str,
    ) -> None:
        properties = cloudformation_json["Properties"]
        role_alias_name = properties.get("RoleAlias", resource_name)

        iot_backend = iot_backends[account_id][region_name]
        iot_backend.delete_role_alias(role_alias_name=role_alias_name)


@dataclass(frozen=True)
class FakeConfigField:
    name: str
    type: str


@dataclass(frozen=True)
class FakeThingGroupIndexingConfiguration:
    customFields: list[FakeConfigField] = field(default_factory=list)
    managedFields: list[FakeConfigField] = field(default_factory=list)
    thingGroupIndexingMode: str = "OFF"


@dataclass(frozen=True)
class FakeThingIndexingConfigurationFilterGeoLocations:
    name: str
    order: str


@dataclass(frozen=True)
class FakeThingIndexingConfigurationFilter:
    geoLocations: list[FakeThingIndexingConfigurationFilterGeoLocations] = field(
        default_factory=list
    )
    namedShadowNames: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class FakeThingIndexingConfiguration:
    customFields: list[FakeConfigField] = field(default_factory=list)
    managedFields: list[FakeConfigField] = field(default_factory=list)
    filter: FakeThingIndexingConfigurationFilter = field(
        default_factory=FakeThingIndexingConfigurationFilter
    )
    deviceDefenderIndexingMode: str = "OFF"
    namedShadowIndexingMode: str = "OFF"
    thingConnectivityIndexingMode: str = "OFF"
    thingIndexingMode: str = "OFF"


@dataclass(frozen=True)
class FakeIndexingConfigurationData:
    thingGroupIndexingConfiguration: FakeThingGroupIndexingConfiguration = field(
        default_factory=FakeThingGroupIndexingConfiguration
    )
    thingIndexingConfiguration: FakeThingIndexingConfiguration = field(
        default_factory=FakeThingIndexingConfiguration
    )


class FakeIndexingConfiguration(BaseModel):
    def __init__(self, region_name: str, account_id: str) -> None:
        self.region_name = region_name
        self.account_id = account_id
        self.configuration = FakeIndexingConfigurationData()

    def to_dict(self) -> dict[str, Any]:
        return asdict(self.configuration)

    def update_configuration(
        self,
        thingIndexingConfiguration: dict[str, Any],
        thingGroupIndexingConfiguration: dict[str, Any],
    ) -> None:
        self.configuration = replace(
            self.configuration,
            thingIndexingConfiguration=replace(
                self.configuration.thingIndexingConfiguration,
                **thingIndexingConfiguration,
            ),
            thingGroupIndexingConfiguration=replace(
                self.configuration.thingGroupIndexingConfiguration,
                **thingGroupIndexingConfiguration,
            ),
        )


class FakeSecurityProfile(BaseModel):
    def __init__(
        self,
        account_id: str,
        region_name: str,
        security_profile_name: str,
        security_profile_description: Optional[str],
        behaviors: Optional[list[dict[str, Any]]],
        alert_targets: Optional[dict[str, Any]],
        additional_metrics_to_retain_v2: Optional[list[dict[str, Any]]],
        tags: Optional[list[dict[str, str]]],
    ):
        self.security_profile_name = security_profile_name
        self.security_profile_description = security_profile_description or ""
        self.behaviors = behaviors or []
        self.alert_targets = alert_targets or {}
        self.additional_metrics_to_retain_v2 = additional_metrics_to_retain_v2 or []
        self.tags = tags or []
        self.creation_date = utcnow()
        self.last_modified_date = self.creation_date
        self.version = 1
        self.arn = f"arn:{get_partition(region_name)}:iot:{region_name}:{account_id}:securityprofile/{security_profile_name}"
        self.targets: list[str] = []

    def to_dict(self) -> dict[str, Any]:
        """Used for create response (securityProfileName, securityProfileArn)."""
        return {
            "securityProfileName": self.security_profile_name,
            "securityProfileArn": self.arn,
        }

    def to_list_dict(self) -> dict[str, Any]:
        """Used for list response (name, arn)."""
        return {
            "name": self.security_profile_name,
            "arn": self.arn,
        }

    def to_description_dict(self) -> dict[str, Any]:
        return {
            "securityProfileName": self.security_profile_name,
            "securityProfileArn": self.arn,
            "securityProfileDescription": self.security_profile_description,
            "behaviors": self.behaviors,
            "alertTargets": self.alert_targets,
            "additionalMetricsToRetainV2": self.additional_metrics_to_retain_v2,
            "version": self.version,
            "creationDate": self.creation_date,
            "lastModifiedDate": self.last_modified_date,
        }


class FakeAuthorizer(BaseModel):
    def __init__(
        self,
        account_id: str,
        region_name: str,
        authorizer_name: str,
        authorizer_function_arn: str,
        token_key_name: Optional[str],
        token_signing_public_keys: Optional[dict[str, str]],
        status: Optional[str],
        signing_disabled: Optional[bool],
        enable_caching_for_http: Optional[bool],
    ):
        self.authorizer_name = authorizer_name
        self.authorizer_function_arn = authorizer_function_arn
        self.token_key_name = token_key_name or ""
        self.token_signing_public_keys = token_signing_public_keys or {}
        self.status = status or "ACTIVE"
        self.signing_disabled = signing_disabled or False
        self.enable_caching_for_http = enable_caching_for_http or False
        self.creation_date = utcnow()
        self.last_modified_date = self.creation_date
        self.arn = f"arn:{get_partition(region_name)}:iot:{region_name}:{account_id}:authorizer/{authorizer_name}"

    def to_dict(self) -> dict[str, Any]:
        return {
            "authorizerName": self.authorizer_name,
            "authorizerArn": self.arn,
        }

    def to_description_dict(self) -> dict[str, Any]:
        return {
            "authorizerName": self.authorizer_name,
            "authorizerArn": self.arn,
            "authorizerFunctionArn": self.authorizer_function_arn,
            "tokenKeyName": self.token_key_name,
            "tokenSigningPublicKeys": self.token_signing_public_keys,
            "status": self.status,
            "signingDisabled": self.signing_disabled,
            "enableCachingForHttp": self.enable_caching_for_http,
            "creationDate": self.creation_date,
            "lastModifiedDate": self.last_modified_date,
        }


class FakeProvisioningTemplate(BaseModel):
    def __init__(
        self,
        account_id: str,
        region_name: str,
        template_name: str,
        description: Optional[str],
        template_body: str,
        enabled: Optional[bool],
        provisioning_role_arn: str,
        pre_provisioning_hook: Optional[dict[str, str]],
        tags: Optional[list[dict[str, str]]],
        template_type: Optional[str],
    ):
        self.template_name = template_name
        self.description = description or ""
        self.template_body = template_body
        self.enabled = enabled if enabled is not None else False
        self.provisioning_role_arn = provisioning_role_arn
        self.pre_provisioning_hook = pre_provisioning_hook
        self.tags = tags or []
        self.template_type = template_type
        self.creation_date = utcnow()
        self.last_modified_date = self.creation_date
        self.default_version_id = 1
        self.arn = f"arn:{get_partition(region_name)}:iot:{region_name}:{account_id}:provisioningtemplate/{template_name}"

    def to_dict(self) -> dict[str, Any]:
        return {
            "templateName": self.template_name,
            "templateArn": self.arn,
            "enabled": self.enabled,
            "creationDate": self.creation_date,
            "lastModifiedDate": self.last_modified_date,
        }

    def to_description_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {
            "templateName": self.template_name,
            "templateArn": self.arn,
            "description": self.description,
            "templateBody": self.template_body,
            "enabled": self.enabled,
            "provisioningRoleArn": self.provisioning_role_arn,
            "defaultVersionId": self.default_version_id,
            "creationDate": self.creation_date,
            "lastModifiedDate": self.last_modified_date,
        }
        if self.pre_provisioning_hook:
            result["preProvisioningHook"] = self.pre_provisioning_hook
        if self.template_type:
            result["type"] = self.template_type
        return result


class FakeDimension(BaseModel):
    def __init__(
        self,
        account_id: str,
        region_name: str,
        name: str,
        dimension_type: str,
        string_values: list[str],
        tags: Optional[list[dict[str, str]]],
    ):
        self.name = name
        self.type = dimension_type
        self.string_values = string_values
        self.tags = tags or []
        self.creation_date = utcnow()
        self.last_modified_date = self.creation_date
        self.arn = f"arn:{get_partition(region_name)}:iot:{region_name}:{account_id}:dimension/{name}"

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "arn": self.arn,
        }

    def to_description_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "arn": self.arn,
            "type": self.type,
            "stringValues": self.string_values,
            "creationDate": self.creation_date,
            "lastModifiedDate": self.last_modified_date,
        }


class FakeCustomMetric(BaseModel):
    def __init__(
        self,
        account_id: str,
        region_name: str,
        metric_name: str,
        display_name: Optional[str],
        metric_type: str,
        tags: Optional[list[dict[str, str]]],
    ):
        self.metric_name = metric_name
        self.display_name = display_name or ""
        self.metric_type = metric_type
        self.tags = tags or []
        self.creation_date = utcnow()
        self.last_modified_date = self.creation_date
        self.arn = f"arn:{get_partition(region_name)}:iot:{region_name}:{account_id}:custommetric/{metric_name}"

    def to_dict(self) -> dict[str, Any]:
        return {
            "metricName": self.metric_name,
            "metricArn": self.arn,
        }

    def to_description_dict(self) -> dict[str, Any]:
        return {
            "metricName": self.metric_name,
            "metricArn": self.arn,
            "displayName": self.display_name,
            "metricType": self.metric_type,
            "creationDate": self.creation_date,
            "lastModifiedDate": self.last_modified_date,
        }


class FakeFleetMetric(BaseModel):
    def __init__(
        self,
        account_id: str,
        region_name: str,
        metric_name: str,
        query_string: str,
        aggregation_type: Optional[dict[str, Any]],
        period: Optional[int],
        aggregation_field: Optional[str],
        description: Optional[str],
        query_version: Optional[str],
        index_name: Optional[str],
        unit: Optional[str],
        tags: Optional[list[dict[str, str]]],
    ):
        self.metric_name = metric_name
        self.query_string = query_string
        self.aggregation_type = aggregation_type
        self.period = period or 300
        self.aggregation_field = aggregation_field or ""
        self.description = description or ""
        self.query_version = query_version or "2017-09-30"
        self.index_name = index_name or "AWS_Things"
        self.unit = unit or "None"
        self.tags = tags or []
        self.creation_date = utcnow()
        self.last_modified_date = self.creation_date
        self.version = 1
        self.arn = f"arn:{get_partition(region_name)}:iot:{region_name}:{account_id}:fleetmetric/{metric_name}"

    def to_dict(self) -> dict[str, Any]:
        return {
            "metricName": self.metric_name,
            "metricArn": self.arn,
        }

    def to_description_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {
            "metricName": self.metric_name,
            "metricArn": self.arn,
            "queryString": self.query_string,
            "period": self.period,
            "aggregationField": self.aggregation_field,
            "description": self.description,
            "queryVersion": self.query_version,
            "indexName": self.index_name,
            "unit": self.unit,
            "version": self.version,
            "creationDate": self.creation_date,
            "lastModifiedDate": self.last_modified_date,
        }
        if self.aggregation_type:
            result["aggregationType"] = self.aggregation_type
        return result


class FakeStream(BaseModel):
    def __init__(
        self,
        account_id: str,
        region_name: str,
        stream_id: str,
        description: str,
        files: list[dict[str, Any]],
        role_arn: str,
        tags: Optional[list[dict[str, str]]],
    ):
        self.stream_id = stream_id
        self.description = description or ""
        self.files = files or []
        self.role_arn = role_arn
        self.tags = tags or []
        self.stream_version = 1
        self.created_at = utcnow()
        self.last_updated_at = self.created_at
        self.arn = f"arn:{get_partition(region_name)}:iot:{region_name}:{account_id}:stream/{stream_id}"

    def to_dict(self) -> dict[str, Any]:
        return {
            "streamId": self.stream_id,
            "streamArn": self.arn,
            "streamVersion": self.stream_version,
        }

    def to_description_dict(self) -> dict[str, Any]:
        return {
            "streamInfo": {
                "streamId": self.stream_id,
                "streamArn": self.arn,
                "streamVersion": self.stream_version,
                "description": self.description,
                "files": self.files,
                "roleArn": self.role_arn,
                "createdAt": self.created_at,
                "lastUpdatedAt": self.last_updated_at,
            }
        }


class FakeMitigationAction(BaseModel):
    def __init__(
        self,
        account_id: str,
        region_name: str,
        action_name: str,
        role_arn: str,
        action_params: dict[str, Any],
        tags: Optional[list[dict[str, str]]],
    ):
        self.action_name = action_name
        self.role_arn = role_arn
        self.action_params = action_params
        self.tags = tags or []
        self.action_id = str(random.uuid4())
        self.creation_date = utcnow()
        self.last_modified_date = self.creation_date
        self.arn = f"arn:{get_partition(region_name)}:iot:{region_name}:{account_id}:mitigationaction/{action_name}"

    def to_dict(self) -> dict[str, Any]:
        return {
            "actionName": self.action_name,
            "actionArn": self.arn,
            "actionId": self.action_id,
        }

    def to_description_dict(self) -> dict[str, Any]:
        return {
            "actionName": self.action_name,
            "actionArn": self.arn,
            "actionId": self.action_id,
            "actionType": next(iter(self.action_params.keys()), "UNKNOWN"),
            "actionParams": self.action_params,
            "roleArn": self.role_arn,
            "creationDate": self.creation_date,
            "lastModifiedDate": self.last_modified_date,
        }


class FakeScheduledAudit(BaseModel):
    def __init__(
        self,
        account_id: str,
        region_name: str,
        scheduled_audit_name: str,
        frequency: str,
        day_of_month: Optional[str],
        day_of_week: Optional[str],
        target_check_names: list[str],
        tags: Optional[list[dict[str, str]]],
    ):
        self.scheduled_audit_name = scheduled_audit_name
        self.frequency = frequency
        self.day_of_month = day_of_month
        self.day_of_week = day_of_week
        self.target_check_names = target_check_names
        self.tags = tags or []
        self.arn = f"arn:{get_partition(region_name)}:iot:{region_name}:{account_id}:scheduledaudit/{scheduled_audit_name}"

    def to_dict(self) -> dict[str, Any]:
        return {
            "scheduledAuditName": self.scheduled_audit_name,
            "scheduledAuditArn": self.arn,
            "frequency": self.frequency,
        }

    def to_description_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {
            "scheduledAuditName": self.scheduled_audit_name,
            "scheduledAuditArn": self.arn,
            "frequency": self.frequency,
            "targetCheckNames": self.target_check_names,
        }
        if self.day_of_month:
            result["dayOfMonth"] = self.day_of_month
        if self.day_of_week:
            result["dayOfWeek"] = self.day_of_week
        return result


class IoTBackend(BaseBackend):
    def __init__(self, region_name: str, account_id: str):
        super().__init__(region_name, account_id)
        self.things: dict[str, FakeThing] = OrderedDict()
        self.jobs: dict[str, FakeJob] = OrderedDict()
        self.jobs_templates: dict[str, FakeJobTemplate] = OrderedDict()
        self.job_executions: dict[tuple[str, str], FakeJobExecution] = OrderedDict()
        self.thing_types: dict[str, FakeThingType] = OrderedDict()
        self.thing_groups: dict[str, FakeThingGroup] = OrderedDict()
        self.billing_groups: dict[str, FakeBillingGroup] = OrderedDict()
        self.ca_certificates: dict[str, FakeCaCertificate] = OrderedDict()
        self.certificates: dict[str, FakeCertificate] = OrderedDict()
        self.policies: dict[str, FakePolicy] = OrderedDict()
        self.principal_policies: dict[tuple[str, str], tuple[str, FakePolicy]] = (
            OrderedDict()
        )
        self.principal_things: dict[tuple[str, str], tuple[str, FakeThing]] = (
            OrderedDict()
        )
        self.rules: dict[str, FakeRule] = OrderedDict()
        self.role_aliases: dict[str, FakeRoleAlias] = OrderedDict()
        self.endpoint: Optional[FakeEndpoint] = None
        self.domain_configurations: dict[str, FakeDomainConfiguration] = OrderedDict()
        self.indexing_configuration = FakeIndexingConfiguration(region_name, account_id)
        self.security_profiles: dict[str, FakeSecurityProfile] = OrderedDict()
        self.authorizers: dict[str, FakeAuthorizer] = OrderedDict()
        self.default_authorizer_name: Optional[str] = None
        self.provisioning_templates: dict[str, FakeProvisioningTemplate] = OrderedDict()
        self.provisioning_template_versions: dict[str, list[dict[str, Any]]] = (
            OrderedDict()
        )
        self.dimensions: dict[str, FakeDimension] = OrderedDict()
        self.custom_metrics: dict[str, FakeCustomMetric] = OrderedDict()
        self.fleet_metrics: dict[str, FakeFleetMetric] = OrderedDict()
        self.streams: dict[str, FakeStream] = OrderedDict()
        self.mitigation_actions: dict[str, FakeMitigationAction] = OrderedDict()
        self.scheduled_audits: dict[str, FakeScheduledAudit] = OrderedDict()
        self.event_configurations: dict[str, dict[str, bool]] = {}
        self.account_audit_configuration: dict[str, Any] = {}

    @staticmethod
    def default_vpc_endpoint_service(
        service_region: str, zones: list[str]
    ) -> list[dict[str, str]]:
        """Default VPC endpoint service."""
        return BaseBackend.default_vpc_endpoint_service_factory(
            service_region, zones, "iot"
        ) + BaseBackend.default_vpc_endpoint_service_factory(
            service_region,
            zones,
            "data.iot",
            private_dns_names=False,
            special_service_name="iot.data",
            policy_supported=False,
        )

    def create_certificate_from_csr(
        self, csr: str, set_as_active: bool
    ) -> FakeCertificate:
        cert = x509.load_pem_x509_csr(csr.encode("utf-8"), default_backend())
        pem = self._generate_certificate_pem(
            domain_name="example.com", subject=cert.subject
        )
        return self.register_certificate(
            pem, ca_certificate_pem=None, set_as_active=set_as_active, status="INACTIVE"
        )

    def _generate_certificate_pem(
        self,
        domain_name: str,
        subject: x509.Name,
        key: Optional[rsa.RSAPrivateKey] = None,
    ) -> str:
        sans = [x509.DNSName(domain_name)]

        key = key or rsa.generate_private_key(
            public_exponent=65537, key_size=2048, backend=default_backend()
        )
        issuer = x509.Name(
            [  # C = US, O = Moto, OU = Server CA 1B, CN = Moto
                x509.NameAttribute(x509.NameOID.COUNTRY_NAME, "US"),
                x509.NameAttribute(x509.NameOID.ORGANIZATION_NAME, "Moto"),
                x509.NameAttribute(
                    x509.NameOID.ORGANIZATIONAL_UNIT_NAME, "Server CA 1B"
                ),
                x509.NameAttribute(x509.NameOID.COMMON_NAME, "Moto"),
            ]
        )
        cert = (
            x509.CertificateBuilder()
            .subject_name(subject)
            .issuer_name(issuer)
            .public_key(key.public_key())
            .serial_number(x509.random_serial_number())
            .not_valid_before(utcnow())
            .not_valid_after(utcnow() + timedelta(days=365))
            .add_extension(x509.SubjectAlternativeName(sans), critical=False)
            .sign(key, hashes.SHA512(), default_backend())
        )

        return cert.public_bytes(serialization.Encoding.PEM).decode("utf-8")

    def create_thing(
        self,
        thing_name: str,
        thing_type_name: str,
        attribute_payload: Optional[dict[str, Any]],
        billing_group_name: Optional[str] = None,
    ) -> FakeThing:
        thing_types = self.list_thing_types()
        thing_type = None
        if thing_type_name:
            filtered_thing_types = [
                _ for _ in thing_types if _.thing_type_name == thing_type_name
            ]
            if len(filtered_thing_types) == 0:
                raise ResourceNotFoundException()
            thing_type = filtered_thing_types[0]

            if thing_type.metadata["deprecated"]:
                # note - typo (depreated) exists also in the original exception.
                raise InvalidRequestException(
                    msg=f"Can not create new thing with depreated thing type:{thing_type_name}"
                )
        if attribute_payload is None:
            attributes: dict[str, Any] = {}
        elif "attributes" not in attribute_payload:
            attributes = {}
        else:
            attributes = attribute_payload["attributes"]
        thing = FakeThing(
            thing_name,
            thing_type,
            attributes,
            self.account_id,
            self.region_name,
            billing_group_name,
        )
        self.things[thing.arn] = thing
        if billing_group_name:
            self.add_thing_to_billing_group(
                billing_group_name=billing_group_name, thing_arn=thing.arn
            )
        return thing

    def create_thing_type(
        self, thing_type_name: str, thing_type_properties: dict[str, Any]
    ) -> tuple[str, str]:
        if thing_type_properties is None:
            thing_type_properties = {}
        thing_type = FakeThingType(
            thing_type_name, thing_type_properties, self.account_id, self.region_name
        )
        self.thing_types[thing_type.arn] = thing_type
        return thing_type.thing_type_name, thing_type.arn

    def list_thing_types(
        self, thing_type_name: Optional[str] = None
    ) -> Iterable[FakeThingType]:
        if thing_type_name:
            # It's weird but thing_type_name is filtered by forward match, not complete match
            return [
                _
                for _ in self.thing_types.values()
                if _.thing_type_name.startswith(thing_type_name)
            ]
        return self.thing_types.values()

    @paginate(PAGINATION_MODEL)
    def list_things(  # type: ignore[misc]
        self,
        attribute_name: str,
        attribute_value: str,
        thing_type_name: str,
    ) -> list[dict[str, Any]]:
        all_things = [_.to_dict() for _ in self.things.values()]
        if attribute_name is not None and thing_type_name is not None:
            filtered_things = list(
                filter(
                    lambda elem: attribute_name in elem["attributes"]
                    and elem["attributes"][attribute_name] == attribute_value
                    and "thingTypeName" in elem
                    and elem["thingTypeName"] == thing_type_name,
                    all_things,
                )
            )
        elif attribute_name is not None and thing_type_name is None:
            filtered_things = list(
                filter(
                    lambda elem: attribute_name in elem["attributes"]
                    and elem["attributes"][attribute_name] == attribute_value,
                    all_things,
                )
            )
        elif attribute_name is None and thing_type_name is not None:
            filtered_things = list(
                filter(
                    lambda elem: "thingTypeName" in elem
                    and elem["thingTypeName"] == thing_type_name,
                    all_things,
                )
            )
        else:
            filtered_things = all_things

        return filtered_things

    def describe_thing(self, thing_name: str) -> FakeThing:
        things = [_ for _ in self.things.values() if _.thing_name == thing_name]
        if len(things) == 0:
            raise ResourceNotFoundException()
        return things[0]

    def describe_thing_type(self, thing_type_name: str) -> FakeThingType:
        thing_types = [
            _ for _ in self.thing_types.values() if _.thing_type_name == thing_type_name
        ]
        if len(thing_types) == 0:
            raise ResourceNotFoundException()
        return thing_types[0]

    def describe_endpoint(self, endpoint_type: str) -> FakeEndpoint:
        self.endpoint = FakeEndpoint(endpoint_type, self.region_name)
        return self.endpoint

    def delete_thing(self, thing_name: str) -> None:
        """
        The ExpectedVersion-parameter is not yet implemented
        """

        # can raise ResourceNotFoundError
        thing = self.describe_thing(thing_name)

        for k in list(self.principal_things.keys()):
            if k[1] == thing_name:
                raise ThingStillAttached(thing_name)

        # Remove thing from any associated billing groups
        for billing_group in self.billing_groups.values():
            if thing.arn in billing_group.things:
                billing_group.things.remove(thing.arn)
                # Also set the billing_group_name of the thing to None
                # This is important if the thing object is still referenced elsewhere
                thing.billing_group_name = None

        del self.things[thing.arn]

    def delete_thing_type(self, thing_type_name: str) -> None:
        # can raise ResourceNotFoundError
        thing_type = self.describe_thing_type(thing_type_name)
        del self.thing_types[thing_type.arn]

    def deprecate_thing_type(
        self, thing_type_name: str, undo_deprecate: bool
    ) -> FakeThingType:
        thing_types = [
            _ for _ in self.thing_types.values() if _.thing_type_name == thing_type_name
        ]
        if len(thing_types) == 0:
            raise ResourceNotFoundException()
        thing_types[0].metadata["deprecated"] = not undo_deprecate
        return thing_types[0]

    def update_thing(
        self,
        thing_name: str,
        thing_type_name: str,
        attribute_payload: Optional[dict[str, Any]],
        remove_thing_type: bool,
    ) -> None:
        """
        The ExpectedVersion-parameter is not yet implemented
        """
        # if attributes payload = {}, nothing
        thing = self.describe_thing(thing_name)

        if remove_thing_type and thing_type_name:
            raise InvalidRequestException()

        # thing_type
        if thing_type_name:
            thing_types = self.list_thing_types()
            filtered_thing_types = [
                _ for _ in thing_types if _.thing_type_name == thing_type_name
            ]
            if len(filtered_thing_types) == 0:
                raise ResourceNotFoundException()
            thing_type = filtered_thing_types[0]

            if thing_type.metadata["deprecated"]:
                raise InvalidRequestException(
                    msg=f"Can not update a thing to use deprecated thing type: {thing_type_name}"
                )

            thing.thing_type = thing_type

        if remove_thing_type:
            thing.thing_type = None

        # attribute
        if attribute_payload is not None and "attributes" in attribute_payload:
            do_merge = attribute_payload.get("merge", False)
            attributes = attribute_payload["attributes"]
            if not do_merge:
                thing.attributes = attributes
            else:
                thing.attributes.update(attributes)
            thing.attributes = {k: v for k, v in thing.attributes.items() if v}

    def create_keys_and_certificate(
        self, set_as_active: bool
    ) -> tuple[FakeCertificate, dict[str, str]]:
        # implement here
        # caCertificate can be blank
        private_key = rsa.generate_private_key(
            public_exponent=65537, key_size=2048, backend=default_backend()
        )
        key_pair = {
            "PublicKey": private_key.public_key()
            .public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo,
            )
            .decode("utf-8"),
            "PrivateKey": private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.TraditionalOpenSSL,
                encryption_algorithm=serialization.NoEncryption(),
            ).decode("utf-8"),
        }
        subject = x509.Name(
            [x509.NameAttribute(NameOID.COMMON_NAME, "AWS IoT Certificate")]
        )
        certificate_pem = self._generate_certificate_pem(
            "getmoto.org", subject, key=private_key
        )
        status = "ACTIVE" if set_as_active else "INACTIVE"
        certificate = FakeCertificate(
            certificate_pem, status, self.account_id, self.region_name
        )
        self.certificates[certificate.certificate_id] = certificate
        return certificate, key_pair

    def delete_ca_certificate(self, certificate_id: str) -> None:
        cert = self.describe_ca_certificate(certificate_id)
        self._validation_delete(cert)
        del self.ca_certificates[certificate_id]

    def delete_certificate(self, certificate_id: str, force_delete: bool) -> None:
        cert = self.describe_certificate(certificate_id)
        self._validation_delete(cert, force_delete)
        del self.certificates[certificate_id]

    def _validation_delete(
        self, cert: FakeCertificate, force_delete: bool = False
    ) -> None:
        if cert.status == "ACTIVE":
            raise CertificateStateException(
                "Certificate must be deactivated (not ACTIVE) before deletion.",
                cert.certificate_id,
            )

        certs = [
            k[0]
            for k, v in self.principal_things.items()
            if self._get_principal(k[0]).certificate_id == cert.certificate_id
        ]
        if len(certs) > 0:
            raise DeleteConflictException(
                f"Things must be detached before deletion (arn: {certs[0]})"
            )

        certs = [
            k[0]
            for k, v in self.principal_policies.items()
            if self._get_principal(k[0]).certificate_id == cert.certificate_id
        ]
        if len(certs) > 0 and not force_delete:
            raise DeleteConflictException(
                f"Certificate policies must be detached before deletion (arn: {certs[0]})"
            )

    def describe_ca_certificate(self, certificate_id: str) -> FakeCaCertificate:
        if certificate_id not in self.ca_certificates:
            raise ResourceNotFoundException()
        return self.ca_certificates[certificate_id]

    def describe_certificate(self, certificate_id: str) -> FakeCertificate:
        certs = [
            _ for _ in self.certificates.values() if _.certificate_id == certificate_id
        ]
        if len(certs) == 0:
            raise ResourceNotFoundException()
        return certs[0]

    def get_registration_code(self) -> str:
        return str(random.uuid4())

    def list_certificates(self) -> Iterable[FakeCertificate]:
        """
        Pagination is not yet implemented
        """
        return self.certificates.values()

    def list_certificates_by_ca(self, ca_certificate_id: str) -> list[FakeCertificate]:
        """
        Pagination is not yet implemented
        """
        return [
            cert
            for cert in self.certificates.values()
            if cert.ca_certificate_id == ca_certificate_id
        ]

    def __raise_if_certificate_already_exists(
        self, certificate_id: str, certificate_arn: str
    ) -> None:
        if certificate_id in self.certificates:
            raise ResourceAlreadyExistsException(
                "The certificate is already provisioned or registered",
                certificate_id,
                certificate_arn,
            )

    def register_ca_certificate(
        self,
        ca_certificate: str,
        set_as_active: bool,
        registration_config: dict[str, str],
    ) -> FakeCaCertificate:
        """
        The VerificationCertificate-parameter is not yet implemented
        """
        certificate = FakeCaCertificate(
            ca_certificate=ca_certificate,
            status="ACTIVE" if set_as_active else "INACTIVE",
            account_id=self.account_id,
            region_name=self.region_name,
            registration_config=registration_config,
        )

        self.ca_certificates[certificate.certificate_id] = certificate
        return certificate

    def _find_ca_certificate(self, ca_certificate_pem: Optional[str]) -> Optional[str]:
        for ca_cert in self.ca_certificates.values():
            if ca_cert.certificate_pem == ca_certificate_pem:
                return ca_cert.certificate_id
        return None

    def register_certificate(
        self,
        certificate_pem: str,
        ca_certificate_pem: Optional[str],
        set_as_active: bool,
        status: str,
    ) -> FakeCertificate:
        ca_certificate_id = self._find_ca_certificate(ca_certificate_pem)
        certificate = FakeCertificate(
            certificate_pem,
            "ACTIVE" if set_as_active else status,
            self.account_id,
            self.region_name,
            ca_certificate_id,
        )
        self.__raise_if_certificate_already_exists(
            certificate.certificate_id, certificate_arn=certificate.arn
        )

        self.certificates[certificate.certificate_id] = certificate
        return certificate

    def register_certificate_without_ca(
        self, certificate_pem: str, status: str
    ) -> FakeCertificate:
        certificate = FakeCertificate(
            certificate_pem, status, self.account_id, self.region_name
        )
        self.__raise_if_certificate_already_exists(
            certificate.certificate_id, certificate_arn=certificate.arn
        )

        self.certificates[certificate.certificate_id] = certificate
        return certificate

    def update_ca_certificate(
        self,
        certificate_id: str,
        new_status: Optional[str],
        config: Optional[dict[str, str]],
    ) -> None:
        """
        The newAutoRegistrationStatus and removeAutoRegistration-parameters are not yet implemented
        """
        cert = self.describe_ca_certificate(certificate_id)
        if new_status is not None:
            cert.status = new_status
        if config is not None:
            cert.registration_config = config

    def update_certificate(self, certificate_id: str, new_status: str) -> None:
        cert = self.describe_certificate(certificate_id)
        # TODO: validate new_status
        cert.status = new_status

    def create_policy(
        self, policy_name: str, policy_document: dict[str, Any]
    ) -> FakePolicy:
        if policy_name in self.policies:
            current_policy = self.policies[policy_name]
            raise ResourceAlreadyExistsException(
                f"Policy cannot be created - name already exists (name={policy_name})",
                current_policy.name,
                current_policy.arn,
            )
        policy = FakePolicy(
            policy_name, policy_document, self.account_id, self.region_name
        )
        self.policies[policy.name] = policy
        return policy

    def attach_policy(self, policy_name: str, target: str) -> None:
        principal = self._get_principal(target)
        policy = self.get_policy(policy_name)
        k = (target, policy_name)
        if k in self.principal_policies:
            return
        self.principal_policies[k] = (principal, policy)

    def detach_policy(self, policy_name: str, target: str) -> None:
        # this may raise ResourceNotFoundException
        self._get_principal(target)
        self.get_policy(policy_name)

        k = (target, policy_name)
        if k not in self.principal_policies:
            raise ResourceNotFoundException()
        del self.principal_policies[k]

    def list_attached_policies(self, target: str) -> list[FakePolicy]:
        """
        Pagination is not yet implemented
        """
        return [v[1] for k, v in self.principal_policies.items() if k[0] == target]

    def list_policies(self) -> Iterable[FakePolicy]:
        """
        Pagination is not yet implemented
        """
        return self.policies.values()

    def get_policy(self, policy_name: str) -> FakePolicy:
        policies = [_ for _ in self.policies.values() if _.name == policy_name]
        if len(policies) == 0:
            raise ResourceNotFoundException()
        return policies[0]

    def delete_policy(self, policy_name: str) -> None:
        policies = [
            k[1] for k, v in self.principal_policies.items() if k[1] == policy_name
        ]
        if len(policies) > 0:
            raise DeleteConflictException(
                f"The policy cannot be deleted as the policy is attached to one or more principals (name={policy_name})"
            )

        policy = self.get_policy(policy_name)
        if len(policy.versions) > 1:
            raise DeleteConflictException(
                f"Cannot delete the policy because it has one or more policy versions attached to it (name={policy_name})"
            )
        del self.policies[policy.name]

    def create_policy_version(
        self, policy_name: str, policy_document: dict[str, Any], set_as_default: bool
    ) -> FakePolicyVersion:
        policy = self.get_policy(policy_name)
        if not policy:
            raise ResourceNotFoundException()
        if len(policy.versions) >= 5:
            raise VersionsLimitExceededException(policy_name)

        policy._max_version_id += 1
        version = FakePolicyVersion(
            policy_name,
            policy_document,
            set_as_default,
            self.account_id,
            self.region_name,
            version_id=policy._max_version_id,
        )
        policy.versions.append(version)
        if set_as_default:
            self.set_default_policy_version(policy_name, version.version_id)
        return version

    def set_default_policy_version(self, policy_name: str, version_id: str) -> None:
        policy = self.get_policy(policy_name)
        if not policy:
            raise ResourceNotFoundException()
        for version in policy.versions:
            if version.version_id == version_id:
                version.is_default = True
                policy.default_version_id = version.version_id
                policy.document = version.document
            else:
                version.is_default = False

    def get_policy_version(
        self, policy_name: str, version_id: str
    ) -> FakePolicyVersion:
        policy = self.get_policy(policy_name)
        if not policy:
            raise ResourceNotFoundException()
        for version in policy.versions:
            if version.version_id == version_id:
                return version
        raise ResourceNotFoundException()

    def list_policy_versions(self, policy_name: str) -> Iterable[FakePolicyVersion]:
        policy = self.get_policy(policy_name)
        if not policy:
            raise ResourceNotFoundException()
        return policy.versions

    def delete_policy_version(self, policy_name: str, version_id: str) -> None:
        policy = self.get_policy(policy_name)
        if not policy:
            raise ResourceNotFoundException()
        if version_id == policy.default_version_id:
            raise InvalidRequestException(
                "Cannot delete the default version of a policy"
            )
        for i, v in enumerate(policy.versions):
            if v.version_id == version_id:
                del policy.versions[i]
                return
        raise ResourceNotFoundException()

    def _get_principal(self, principal_arn: str) -> Any:
        """
        raise ResourceNotFoundException
        """
        if ":cert/" in principal_arn:
            certs = [_ for _ in self.certificates.values() if _.arn == principal_arn]
            if len(certs) == 0:
                raise ResourceNotFoundException()
            principal = certs[0]
            return principal
        if ":thinggroup/" in principal_arn:
            try:
                return self.thing_groups[principal_arn]
            except KeyError:
                raise ResourceNotFoundException(
                    f"No thing group with ARN {principal_arn} exists"
                )
        from moto.cognitoidentity import cognitoidentity_backends

        cognito = cognitoidentity_backends[self.account_id][self.region_name]
        identities = []
        for identity_pool in cognito.identity_pools:
            pool_identities = cognito.pools_identities.get(identity_pool, {})
            identities.extend(
                [pi["IdentityId"] for pi in pool_identities.get("Identities", [])]
            )
            if principal_arn in identities:
                return {"IdentityId": principal_arn}

        raise ResourceNotFoundException()

    def attach_principal_policy(self, policy_name: str, principal_arn: str) -> None:
        principal = self._get_principal(principal_arn)
        policy = self.get_policy(policy_name)
        k = (principal_arn, policy_name)
        if k in self.principal_policies:
            return
        self.principal_policies[k] = (principal, policy)

    def detach_principal_policy(self, policy_name: str, principal_arn: str) -> None:
        # this may raises ResourceNotFoundException
        self._get_principal(principal_arn)
        self.get_policy(policy_name)

        k = (principal_arn, policy_name)
        if k not in self.principal_policies:
            raise ResourceNotFoundException()
        del self.principal_policies[k]

    def list_principal_policies(self, principal_arn: str) -> list[FakePolicy]:
        """
        Pagination is not yet implemented
        """
        policies = [
            v[1] for k, v in self.principal_policies.items() if k[0] == principal_arn
        ]
        return policies

    def list_policy_principals(self, policy_name: str) -> list[str]:
        """
        Pagination is not yet implemented
        """
        # this action is deprecated
        # https://docs.aws.amazon.com/iot/latest/apireference/API_ListTargetsForPolicy.html
        # should use ListTargetsForPolicy instead
        principals = [
            k[0] for k, v in self.principal_policies.items() if k[1] == policy_name
        ]
        return principals

    def list_targets_for_policy(self, policy_name: str) -> list[str]:
        """
        Pagination is not yet implemented
        """
        # This behaviour is different to list_policy_principals which will just return an empty list
        if policy_name not in self.policies:
            raise ResourceNotFoundException("Policy not found")
        return self.list_policy_principals(policy_name=policy_name)

    def attach_thing_principal(self, thing_name: str, principal_arn: str) -> None:
        principal = self._get_principal(principal_arn)
        thing = self.describe_thing(thing_name)
        k = (principal_arn, thing_name)
        if k in self.principal_things:
            return
        self.principal_things[k] = (principal, thing)

    def detach_thing_principal(self, thing_name: str, principal_arn: str) -> None:
        # this may raises ResourceNotFoundException
        self._get_principal(principal_arn)
        self.describe_thing(thing_name)

        k = (principal_arn, thing_name)
        if k not in self.principal_things:
            raise ResourceNotFoundException()
        del self.principal_things[k]

    def list_principal_things(self, principal_arn: str) -> list[str]:
        thing_names = [
            k[1] for k, v in self.principal_things.items() if k[0] == principal_arn
        ]
        return thing_names

    def list_thing_principals(self, thing_name: str) -> list[str]:
        things = [_ for _ in self.things.values() if _.thing_name == thing_name]
        if len(things) == 0:
            raise ResourceNotFoundException(
                f"Failed to list principals for thing {thing_name} because the thing does not exist in your account"
            )

        principals = [
            k[0] for k, v in self.principal_things.items() if k[1] == thing_name
        ]
        return principals

    def list_thing_principals_v2(self, thing_name: str) -> list[str]:
        return self.list_thing_principals(thing_name)

    def describe_thing_group(self, thing_group_name: str) -> FakeThingGroup:
        thing_groups = [
            _
            for _ in self.thing_groups.values()
            if _.thing_group_name == thing_group_name
        ]
        if len(thing_groups) == 0:
            raise ResourceNotFoundException()
        return thing_groups[0]

    def create_thing_group(
        self,
        thing_group_name: str,
        parent_group_name: str,
        thing_group_properties: dict[str, Any],
    ) -> tuple[str, str, str]:
        thing_group = FakeThingGroup(
            thing_group_name,
            parent_group_name,
            thing_group_properties,
            self.account_id,
            self.region_name,
            self.thing_groups,
        )
        # this behavior is not documented, but AWS does it like that
        # if a thing group with the same name exists, it's properties are compared
        # if they differ, an error is returned.
        # Otherwise, the old thing group is returned
        if thing_group.arn in self.thing_groups:
            current_thing_group = self.thing_groups[thing_group.arn]
            if current_thing_group.thing_group_properties != thing_group_properties:
                raise ResourceAlreadyExistsException(
                    msg=f"Thing Group {thing_group_name} already exists in current account with different properties",
                    resource_arn=thing_group.arn,
                    resource_id=current_thing_group.thing_group_id,
                )
            thing_group = current_thing_group
        else:
            self.thing_groups[thing_group.arn] = thing_group
        return thing_group.thing_group_name, thing_group.arn, thing_group.thing_group_id

    def delete_thing_group(self, thing_group_name: str) -> None:
        """
        The ExpectedVersion-parameter is not yet implemented
        """
        child_groups = [
            thing_group
            for _, thing_group in self.thing_groups.items()
            if thing_group.parent_group_name == thing_group_name
        ]
        if len(child_groups) > 0:
            raise InvalidRequestException(
                " Cannot delete thing group : "
                + thing_group_name
                + " when there are still child groups attached to it"
            )
        try:
            thing_group = self.describe_thing_group(thing_group_name)
            del self.thing_groups[thing_group.arn]
        except ResourceNotFoundException:
            # AWS returns success even if the thing group does not exist.
            pass

    def list_thing_groups(
        self,
        parent_group: Optional[str],
        name_prefix_filter: Optional[str],
        recursive: Optional[bool],
    ) -> list[FakeThingGroup]:
        if recursive is None:
            recursive = True
        if name_prefix_filter is None:
            name_prefix_filter = ""
        if parent_group and parent_group not in [
            _.thing_group_name for _ in self.thing_groups.values()
        ]:
            raise ResourceNotFoundException()
        thing_groups = [
            _ for _ in self.thing_groups.values() if _.parent_group_name == parent_group
        ]
        if recursive:
            for g in thing_groups:
                thing_groups.extend(
                    self.list_thing_groups(
                        parent_group=g.thing_group_name,
                        name_prefix_filter=None,
                        recursive=False,
                    )
                )
        # thing_groups = groups_to_process.values()
        return [
            _ for _ in thing_groups if _.thing_group_name.startswith(name_prefix_filter)
        ]

    def update_thing_group(
        self,
        thing_group_name: str,
        thing_group_properties: dict[str, Any],
        expected_version: int,
    ) -> int:
        thing_group = self.describe_thing_group(thing_group_name)
        if expected_version and expected_version != thing_group.version:
            raise VersionConflictException(thing_group_name)
        attribute_payload = thing_group_properties.get("attributePayload", None)
        if attribute_payload is not None and "attributes" in attribute_payload:
            do_merge = attribute_payload.get("merge", False)
            attributes = attribute_payload["attributes"]
            if attributes:
                # might not exist yet, for example when the thing group was created without attributes
                current_attribute_payload = (
                    thing_group.thing_group_properties.setdefault(
                        "attributePayload",
                        {"attributes": {}},  # type: ignore
                    )
                )
                if not do_merge:
                    current_attribute_payload["attributes"] = attributes  # type: ignore
                else:
                    current_attribute_payload["attributes"].update(attributes)  # type: ignore
        elif attribute_payload is not None and "attributes" not in attribute_payload:
            thing_group.attributes = {}  # type: ignore
        if "thingGroupDescription" in thing_group_properties:
            thing_group.thing_group_properties["thingGroupDescription"] = (
                thing_group_properties["thingGroupDescription"]
            )
        thing_group.version = thing_group.version + 1
        return thing_group.version

    def _identify_thing_group(
        self, thing_group_name: Optional[str], thing_group_arn: Optional[str]
    ) -> FakeThingGroup:
        # identify thing group
        if thing_group_name is None and thing_group_arn is None:
            raise InvalidRequestException(
                " Both thingGroupArn and thingGroupName are empty. Need to specify at least one of them"
            )
        if thing_group_name is not None:
            thing_group = self.describe_thing_group(thing_group_name)
            if thing_group_arn and thing_group.arn != thing_group_arn:
                raise InvalidRequestException(
                    "ThingGroupName thingGroupArn does not match specified thingGroupName in request"
                )
        elif thing_group_arn is not None:
            if thing_group_arn not in self.thing_groups:
                raise InvalidRequestException()
            thing_group = self.thing_groups[thing_group_arn]
        return thing_group

    def _identify_thing(
        self, thing_name: Optional[str], thing_arn: Optional[str]
    ) -> FakeThing:
        # identify thing
        if thing_name is None and thing_arn is None:
            raise InvalidRequestException(
                "Both thingArn and thingName are empty. Need to specify at least one of them"
            )
        if thing_name is not None:
            thing = self.describe_thing(thing_name)
            if thing_arn and thing.arn != thing_arn:
                raise InvalidRequestException(
                    "ThingName thingArn does not match specified thingName in request"
                )
        elif thing_arn is not None:
            if thing_arn not in self.things:
                raise InvalidRequestException()
            thing = self.things[thing_arn]
        return thing

    def add_thing_to_thing_group(
        self,
        thing_group_name: str,
        thing_group_arn: Optional[str],
        thing_name: str,
        thing_arn: Optional[str],
    ) -> None:
        thing_group = self._identify_thing_group(thing_group_name, thing_group_arn)
        thing = self._identify_thing(thing_name, thing_arn)
        if thing.arn in thing_group.things:
            # aws ignores duplicate registration
            return
        thing_group.things[thing.arn] = thing

    def remove_thing_from_thing_group(
        self,
        thing_group_name: str,
        thing_group_arn: Optional[str],
        thing_name: str,
        thing_arn: Optional[str],
    ) -> None:
        thing_group = self._identify_thing_group(thing_group_name, thing_group_arn)
        thing = self._identify_thing(thing_name, thing_arn)
        if thing.arn not in thing_group.things:
            # aws ignores non-registered thing
            return
        del thing_group.things[thing.arn]

    def list_things_in_thing_group(self, thing_group_name: str) -> Iterable[FakeThing]:
        """
        Pagination and the recursive-parameter is not yet implemented
        """
        thing_group = self.describe_thing_group(thing_group_name)
        return thing_group.things.values()

    def list_thing_groups_for_thing(self, thing_name: str) -> list[dict[str, str]]:
        """
        Pagination is not yet implemented
        """
        thing = self.describe_thing(thing_name)
        all_thing_groups = self.list_thing_groups(None, None, None)
        ret = []
        for thing_group in all_thing_groups:
            if thing.arn in thing_group.things:
                ret.append(
                    {
                        "groupName": thing_group.thing_group_name,
                        "groupArn": thing_group.arn,
                    }
                )
        return ret

    def update_thing_groups_for_thing(
        self,
        thing_name: str,
        thing_groups_to_add: list[str],
        thing_groups_to_remove: list[str],
    ) -> None:
        thing = self.describe_thing(thing_name)
        for thing_group_name in thing_groups_to_add:
            thing_group = self.describe_thing_group(thing_group_name)
            self.add_thing_to_thing_group(
                thing_group.thing_group_name, None, thing.thing_name, None
            )
        for thing_group_name in thing_groups_to_remove:
            thing_group = self.describe_thing_group(thing_group_name)
            self.remove_thing_from_thing_group(
                thing_group.thing_group_name, None, thing.thing_name, None
            )

    def create_job(
        self,
        job_id: str,
        targets: list[str],
        document_source: str,
        document: str,
        description: str,
        presigned_url_config: dict[str, Any],
        target_selection: str,
        job_executions_rollout_config: dict[str, Any],
        document_parameters: dict[str, str],
        abort_config: dict[str, list[dict[str, Any]]],
        job_execution_retry_config: dict[str, Any],
        scheduling_config: dict[str, Any],
        timeout_config: dict[str, Any],
    ) -> tuple[str, str, str]:
        job = FakeJob(
            job_id=job_id,
            targets=targets,
            document_source=document_source,
            document=document,
            description=description,
            presigned_url_config=presigned_url_config,
            target_selection=target_selection,
            job_executions_rollout_config=job_executions_rollout_config,
            abort_config=abort_config,
            job_execution_retry_config=job_execution_retry_config,
            scheduling_config=scheduling_config,
            timeout_config=timeout_config,
            document_parameters=document_parameters,
            account_id=self.account_id,
            region_name=self.region_name,
        )
        self.jobs[job_id] = job

        for thing_arn in targets:
            thing_name = thing_arn.split(":")[-1].split("/")[-1]
            job_execution = FakeJobExecution(job_id, thing_arn)
            self.job_executions[(job_id, thing_name)] = job_execution
        return job.job_arn, job_id, description

    def describe_job(self, job_id: str) -> FakeJob:
        jobs = [_ for _ in self.jobs.values() if _.job_id == job_id]
        if len(jobs) == 0:
            raise ResourceNotFoundException()
        return jobs[0]

    def delete_job(self, job_id: str, force: bool) -> None:
        job = self.jobs[job_id]

        if job.status == "IN_PROGRESS" and force:
            del self.jobs[job_id]
        elif job.status != "IN_PROGRESS":
            del self.jobs[job_id]
        else:
            raise InvalidStateTransitionException()

    def cancel_job(
        self, job_id: str, reason_code: str, comment: str, force: bool
    ) -> FakeJob:
        job = self.jobs[job_id]

        job.reason_code = reason_code if reason_code is not None else job.reason_code
        job.comment = comment if comment is not None else job.comment
        job.force = force if force is not None and force != job.force else job.force
        job.status = "CANCELED"

        if job.status == "IN_PROGRESS" and force:
            self.jobs[job_id] = job
        elif job.status != "IN_PROGRESS":
            self.jobs[job_id] = job
        else:
            raise InvalidStateTransitionException()

        return job

    def get_job_document(self, job_id: str) -> FakeJob:
        return self.jobs[job_id]

    @paginate(PAGINATION_MODEL)  # type: ignore[misc]
    def list_jobs(self) -> list[FakeJob]:
        """
        The following parameter are not yet implemented: Status, TargetSelection, ThingGroupName, ThingGroupId
        """
        return list(self.jobs.values())

    def describe_job_execution(
        self, job_id: str, thing_name: str, execution_number: int
    ) -> FakeJobExecution:
        try:
            job_execution = self.job_executions[(job_id, thing_name)]
        except KeyError:
            raise ResourceNotFoundException()

        if job_execution is None or (
            execution_number is not None
            and job_execution.execution_number != execution_number
        ):
            raise ResourceNotFoundException()

        return job_execution

    def cancel_job_execution(self, job_id: str, thing_name: str, force: bool) -> None:
        """
        The parameters ExpectedVersion and StatusDetails are not yet implemented
        """
        job_execution = self.job_executions[(job_id, thing_name)]

        if job_execution is None:
            raise ResourceNotFoundException()

        job_execution.force_canceled = (
            force if force is not None else job_execution.force_canceled
        )
        # TODO: implement expected_version and status_details (at most 10 can be specified)

        if job_execution.status == "IN_PROGRESS" and force:
            job_execution.status = "CANCELED"
            self.job_executions[(job_id, thing_name)] = job_execution
        elif job_execution.status != "IN_PROGRESS":
            job_execution.status = "CANCELED"
            self.job_executions[(job_id, thing_name)] = job_execution
        else:
            raise InvalidStateTransitionException()

    def delete_job_execution(
        self, job_id: str, thing_name: str, execution_number: int, force: bool
    ) -> None:
        job_execution = self.job_executions[(job_id, thing_name)]

        if job_execution.execution_number != execution_number:
            raise ResourceNotFoundException()

        if job_execution.status == "IN_PROGRESS" and force:
            del self.job_executions[(job_id, thing_name)]
        elif job_execution.status != "IN_PROGRESS":
            del self.job_executions[(job_id, thing_name)]
        else:
            raise InvalidStateTransitionException()

    @paginate(PAGINATION_MODEL)
    def list_job_executions_for_job(
        self, job_id: str, status: str
    ) -> list[FakeJobExecution]:
        return [
            job_exec
            for (_id, _), job_exec in self.job_executions.items()
            if _id == job_id and (not status or job_exec.status == status)
        ]

    @paginate(PAGINATION_MODEL)  # type: ignore[misc]
    def list_job_executions_for_thing(
        self, thing_name: str, status: Optional[str]
    ) -> list[FakeJobExecution]:
        return [
            job_exec
            for (_, name), job_exec in self.job_executions.items()
            if name == thing_name and (not status or job_exec.status == status)
        ]

    def list_topic_rules(self) -> list[dict[str, Any]]:
        return [r.to_dict() for r in self.rules.values()]

    def get_topic_rule(self, rule_name: str) -> dict[str, Any]:
        if rule_name not in self.rules:
            raise ResourceNotFoundException()
        return self.rules[rule_name].to_get_dict()

    def create_topic_rule(self, rule_name: str, sql: str, **kwargs: Any) -> None:
        if not re.match("^[a-zA-Z0-9_]+$", rule_name):
            msg = f"1 validation error detected: Value '{rule_name}' at 'ruleName' failed to satisfy constraint: Member must satisfy regular expression pattern: ^[a-zA-Z0-9_]+$"
            raise InvalidRequestException(msg)
        if rule_name in self.rules:
            raise ResourceAlreadyExistsException(
                "Rule with given name already exists", "", self.rules[rule_name].arn
            )
        result = re.search(r"FROM\s+([^\s]*)", sql)
        topic = result.group(1).strip("'") if result else None
        self.rules[rule_name] = FakeRule(
            rule_name=rule_name,
            created_at=utcnow(),
            topic_pattern=topic,
            sql=sql,
            account_id=self.account_id,
            region_name=self.region_name,
            **kwargs,
        )

    def replace_topic_rule(self, rule_name: str, **kwargs: Any) -> None:
        self.delete_topic_rule(rule_name)
        self.create_topic_rule(rule_name, **kwargs)

    def delete_topic_rule(self, rule_name: str) -> None:
        if rule_name not in self.rules:
            raise ResourceNotFoundException()
        del self.rules[rule_name]

    def enable_topic_rule(self, rule_name: str) -> None:
        if rule_name not in self.rules:
            raise ResourceNotFoundException()
        self.rules[rule_name].rule_disabled = False

    def disable_topic_rule(self, rule_name: str) -> None:
        if rule_name not in self.rules:
            raise ResourceNotFoundException()
        self.rules[rule_name].rule_disabled = True

    def create_domain_configuration(
        self,
        domain_configuration_name: str,
        domain_name: str,
        server_certificate_arns: list[str],
        authorizer_config: dict[str, Any],
        service_type: str,
    ) -> FakeDomainConfiguration:
        """
        The ValidationCertificateArn-parameter is not yet implemented
        """
        if domain_configuration_name in self.domain_configurations:
            raise ResourceAlreadyExistsException(
                "Domain configuration with given name already exists.",
                self.domain_configurations[
                    domain_configuration_name
                ].domain_configuration_name,
                self.domain_configurations[
                    domain_configuration_name
                ].domain_configuration_arn,
            )
        self.domain_configurations[domain_configuration_name] = FakeDomainConfiguration(
            self.account_id,
            self.region_name,
            domain_configuration_name,
            domain_name,
            server_certificate_arns,
            "ENABLED",
            service_type,
            authorizer_config,
            "CUSTOMER_MANAGED",
        )
        return self.domain_configurations[domain_configuration_name]

    def delete_domain_configuration(self, domain_configuration_name: str) -> None:
        if domain_configuration_name not in self.domain_configurations:
            raise ResourceNotFoundException("The specified resource does not exist.")
        del self.domain_configurations[domain_configuration_name]

    def describe_domain_configuration(
        self, domain_configuration_name: str
    ) -> FakeDomainConfiguration:
        if domain_configuration_name not in self.domain_configurations:
            raise ResourceNotFoundException("The specified resource does not exist.")
        return self.domain_configurations[domain_configuration_name]

    def list_domain_configurations(self) -> list[dict[str, Any]]:
        return [_.to_dict() for _ in self.domain_configurations.values()]

    def update_domain_configuration(
        self,
        domain_configuration_name: str,
        authorizer_config: dict[str, Any],
        domain_configuration_status: str,
        remove_authorizer_config: Optional[bool],
    ) -> FakeDomainConfiguration:
        if domain_configuration_name not in self.domain_configurations:
            raise ResourceNotFoundException("The specified resource does not exist.")
        domain_configuration = self.domain_configurations[domain_configuration_name]
        if authorizer_config is not None:
            domain_configuration.authorizer_config = authorizer_config
        if domain_configuration_status is not None:
            domain_configuration.domain_configuration_status = (
                domain_configuration_status
            )
        if remove_authorizer_config is not None and remove_authorizer_config is True:
            domain_configuration.authorizer_config = None
        return domain_configuration

    def search_index(self, query_string: str) -> list[dict[str, Any]]:
        """
        Pagination is not yet implemented. Only basic search queries are supported for now.
        """
        things = [
            thing for thing in self.things.values() if thing.matches(query_string)
        ]
        return [
            t.to_dict(
                include_connectivity=True,
                include_thing_id=True,
                include_thing_group_names=True,
                include_shadows_as_json=True,
            )
            for t in things
        ]

    def create_role_alias(
        self,
        role_alias_name: str,
        role_arn: str,
        credential_duration_seconds: int = 3600,
    ) -> FakeRoleAlias:
        if role_alias_name in self.role_aliases:
            current_role_alias = self.role_aliases[role_alias_name]
            raise ResourceAlreadyExistsException(
                f"RoleAlias cannot be created - already exists (name={role_alias_name})",
                current_role_alias.role_alias,
                current_role_alias.arn,
            )
        new_role_alias = FakeRoleAlias(
            role_alias=role_alias_name,
            role_arn=role_arn,
            credential_duration_seconds=credential_duration_seconds,
            account_id=self.account_id,
            region_name=self.region_name,
        )
        self.role_aliases[role_alias_name] = new_role_alias
        return new_role_alias

    def list_role_aliases(self) -> Iterable[FakeRoleAlias]:
        return self.role_aliases.values()

    def describe_role_alias(self, role_alias_name: str) -> FakeRoleAlias:
        if role_alias_name not in self.role_aliases:
            raise ResourceNotFoundException(
                f"RoleAlias not found (name= {role_alias_name})"
            )
        return self.role_aliases[role_alias_name]

    def update_role_alias(
        self,
        role_alias_name: str,
        role_arn: Optional[str] = None,
        credential_duration_seconds: Optional[int] = None,
    ) -> FakeRoleAlias:
        role_alias = self.describe_role_alias(role_alias_name=role_alias_name)
        if role_arn:
            role_alias.role_arn = role_arn
        if credential_duration_seconds:
            role_alias.credential_duration_seconds = credential_duration_seconds
        return role_alias

    def delete_role_alias(self, role_alias_name: str) -> None:
        self.describe_role_alias(role_alias_name=role_alias_name)
        del self.role_aliases[role_alias_name]

    def get_indexing_configuration(self) -> dict[str, Any]:
        return self.indexing_configuration.to_dict()

    def update_indexing_configuration(
        self,
        thingIndexingConfiguration: dict[str, Any],
        thingGroupIndexingConfiguration: dict[str, Any],
    ) -> None:
        self.indexing_configuration.update_configuration(
            thingIndexingConfiguration, thingGroupIndexingConfiguration
        )

    def create_job_template(
        self,
        job_template_id: str,
        document_source: str,
        document: str,
        description: str,
        presigned_url_config: dict[str, Any],
        job_executions_rollout_config: dict[str, Any],
        abort_config: dict[str, list[dict[str, Any]]],
        job_execution_retry_config: dict[str, Any],
        timeout_config: dict[str, Any],
    ) -> "FakeJobTemplate":
        if job_template_id in self.jobs_templates:
            raise ConflictException(job_template_id)

        job_template = FakeJobTemplate(
            job_template_id=job_template_id,
            document_source=document_source,
            document=document,
            description=description,
            presigned_url_config=presigned_url_config,
            job_executions_rollout_config=job_executions_rollout_config,
            abort_config=abort_config,
            job_execution_retry_config=job_execution_retry_config,
            timeout_config=timeout_config,
            account_id=self.account_id,
            region_name=self.region_name,
        )
        self.jobs_templates[job_template_id] = job_template
        return job_template

    @paginate(PAGINATION_MODEL)  # type: ignore[misc]
    def list_job_templates(self) -> list[dict[str, Union[str, datetime]]]:
        return [_.to_dict() for _ in self.jobs_templates.values()]

    def delete_job_template(self, job_template_id: str) -> None:
        if job_template_id not in self.jobs_templates:
            raise ResourceNotFoundException(f"Job template {job_template_id} not found")
        del self.jobs_templates[job_template_id]

    def describe_job_template(self, job_template_id: str) -> FakeJobTemplate:
        if job_template_id not in self.jobs_templates:
            raise ResourceNotFoundException(f"Job template {job_template_id} not found")
        return self.jobs_templates[job_template_id]

    def create_billing_group(
        self,
        billing_group_name: str,
        billing_group_properties: Optional[dict[str, Any]],
    ) -> FakeBillingGroup:
        if billing_group_name in self.billing_groups:
            raise ResourceAlreadyExistsException(
                f"Billing group {billing_group_name} already exists.",
                resource_id=billing_group_name,
                resource_arn=self.billing_groups[billing_group_name].arn,
            )
        billing_group = FakeBillingGroup(
            billing_group_name=billing_group_name,
            billing_group_properties=billing_group_properties,
            account_id=self.account_id,
            region_name=self.region_name,
        )
        self.billing_groups[billing_group_name] = billing_group
        return billing_group

    def describe_billing_group(self, billing_group_name: str) -> FakeBillingGroup:
        if billing_group_name not in self.billing_groups:
            raise ResourceNotFoundException()
        return self.billing_groups[billing_group_name]

    def delete_billing_group(self, billing_group_name: str) -> None:
        if billing_group_name not in self.billing_groups:
            raise ResourceNotFoundException()
        del self.billing_groups[billing_group_name]

    @paginate(PAGINATION_MODEL)
    def list_billing_groups(
        self, name_prefix_filter: Optional[str] = None
    ) -> list[dict[str, str]]:
        if name_prefix_filter:
            result = [
                group.to_short_dict()
                for group in self.billing_groups.values()
                if group.billing_group_name.startswith(name_prefix_filter)
            ]
            return result
        return [group.to_short_dict() for group in self.billing_groups.values()]

    def update_billing_group(
        self,
        billing_group_name: str,
        billing_group_properties: dict[str, Any],
        expected_version: int,
    ) -> int:
        billing_group = self.describe_billing_group(billing_group_name)
        if expected_version is not None and billing_group.version != expected_version:
            raise VersionConflictException(billing_group_name)
        billing_group.billing_group_properties = billing_group_properties
        billing_group.version += 1
        return billing_group.version

    def add_thing_to_billing_group(
        self,
        billing_group_name: Optional[str] = None,
        billing_group_arn: Optional[str] = None,
        thing_name: Optional[str] = None,
        thing_arn: Optional[str] = None,
    ) -> None:
        if billing_group_name:
            billing_group = self.describe_billing_group(billing_group_name)
        elif billing_group_arn:
            billing_group = self.describe_billing_group(
                billing_group_arn.split("/")[-1]
            )
        else:
            raise InvalidRequestException(
                "Both billingGroupName and billingGroupArn cannot be null"
            )

        if thing_name:
            thing = self.describe_thing(thing_name)
        elif thing_arn:
            thing = self.describe_thing(thing_arn.split("/")[-1])
        else:
            raise InvalidRequestException("Both thingName and thingArn cannot be null")

        if thing.arn not in billing_group.things:
            billing_group.things.append(thing.arn)
            thing.billing_group_name = billing_group.billing_group_name

    def remove_thing_from_billing_group(
        self,
        billing_group_name: Optional[str] = None,
        billing_group_arn: Optional[str] = None,
        thing_name: Optional[str] = None,
        thing_arn: Optional[str] = None,
    ) -> None:
        if billing_group_name:
            billing_group = self.describe_billing_group(billing_group_name)
        elif billing_group_arn:
            billing_group = self.describe_billing_group(
                billing_group_arn.split("/")[-1]
            )
        else:
            raise InvalidRequestException(
                "Both billingGroupName and billingGroupArn cannot be null"
            )

        if thing_name:
            thing = self.describe_thing(thing_name)
        elif thing_arn:
            thing = self.describe_thing(thing_arn.split("/")[-1])
        else:
            raise InvalidRequestException("Both thingName and thingArn cannot be null")

        if thing.arn in billing_group.things:
            billing_group.things.remove(thing.arn)
            thing.billing_group_name = None

    @paginate(PAGINATION_MODEL)
    def list_things_in_billing_group(self, billing_group_name: str) -> list[FakeThing]:
        billing_group = self.describe_billing_group(billing_group_name)
        return [self.things[arn] for arn in billing_group.things]


    # --- Security Profiles ---

    def create_security_profile(
        self,
        security_profile_name: str,
        security_profile_description: Optional[str],
        behaviors: Optional[list[dict[str, Any]]],
        alert_targets: Optional[dict[str, Any]],
        additional_metrics_to_retain_v2: Optional[list[dict[str, Any]]],
        tags: Optional[list[dict[str, str]]],
    ) -> FakeSecurityProfile:
        if security_profile_name in self.security_profiles:
            raise ResourceAlreadyExistsException(
                f"Security profile {security_profile_name} already exists.",
                security_profile_name,
                self.security_profiles[security_profile_name].arn,
            )
        profile = FakeSecurityProfile(
            self.account_id,
            self.region_name,
            security_profile_name,
            security_profile_description,
            behaviors,
            alert_targets,
            additional_metrics_to_retain_v2,
            tags,
        )
        self.security_profiles[security_profile_name] = profile
        return profile

    def describe_security_profile(
        self, security_profile_name: str
    ) -> FakeSecurityProfile:
        if security_profile_name not in self.security_profiles:
            raise ResourceNotFoundException(
                f"Security profile {security_profile_name} does not exist."
            )
        return self.security_profiles[security_profile_name]

    def update_security_profile(
        self,
        security_profile_name: str,
        security_profile_description: Optional[str],
        behaviors: Optional[list[dict[str, Any]]],
        alert_targets: Optional[dict[str, Any]],
        additional_metrics_to_retain_v2: Optional[list[dict[str, Any]]],
    ) -> FakeSecurityProfile:
        if security_profile_name not in self.security_profiles:
            raise ResourceNotFoundException(
                f"Security profile {security_profile_name} does not exist."
            )
        profile = self.security_profiles[security_profile_name]
        if security_profile_description is not None:
            profile.security_profile_description = security_profile_description
        if behaviors is not None:
            profile.behaviors = behaviors
        if alert_targets is not None:
            profile.alert_targets = alert_targets
        if additional_metrics_to_retain_v2 is not None:
            profile.additional_metrics_to_retain_v2 = additional_metrics_to_retain_v2
        profile.version += 1
        profile.last_modified_date = utcnow()
        return profile

    def delete_security_profile(self, security_profile_name: str) -> None:
        if security_profile_name not in self.security_profiles:
            raise ResourceNotFoundException(
                f"Security profile {security_profile_name} does not exist."
            )
        del self.security_profiles[security_profile_name]

    def list_security_profiles(self) -> list[FakeSecurityProfile]:
        return list(self.security_profiles.values())

    def attach_security_profile(
        self, security_profile_name: str, security_profile_target_arn: str
    ) -> None:
        if security_profile_name not in self.security_profiles:
            raise ResourceNotFoundException(
                f"Security profile {security_profile_name} does not exist."
            )
        profile = self.security_profiles[security_profile_name]
        if security_profile_target_arn not in profile.targets:
            profile.targets.append(security_profile_target_arn)

    def detach_security_profile(
        self, security_profile_name: str, security_profile_target_arn: str
    ) -> None:
        if security_profile_name not in self.security_profiles:
            raise ResourceNotFoundException(
                f"Security profile {security_profile_name} does not exist."
            )
        profile = self.security_profiles[security_profile_name]
        if security_profile_target_arn in profile.targets:
            profile.targets.remove(security_profile_target_arn)

    # --- Authorizers ---

    def create_authorizer(
        self,
        authorizer_name: str,
        authorizer_function_arn: str,
        token_key_name: Optional[str],
        token_signing_public_keys: Optional[dict[str, str]],
        status: Optional[str],
        signing_disabled: Optional[bool],
        enable_caching_for_http: Optional[bool],
    ) -> FakeAuthorizer:
        if authorizer_name in self.authorizers:
            raise ResourceAlreadyExistsException(
                f"Authorizer {authorizer_name} already exists.",
                authorizer_name,
                self.authorizers[authorizer_name].arn,
            )
        authorizer = FakeAuthorizer(
            self.account_id,
            self.region_name,
            authorizer_name,
            authorizer_function_arn,
            token_key_name,
            token_signing_public_keys,
            status,
            signing_disabled,
            enable_caching_for_http,
        )
        self.authorizers[authorizer_name] = authorizer
        return authorizer

    def describe_authorizer(self, authorizer_name: str) -> FakeAuthorizer:
        if authorizer_name not in self.authorizers:
            raise ResourceNotFoundException(
                f"Authorizer {authorizer_name} does not exist."
            )
        return self.authorizers[authorizer_name]

    def update_authorizer(
        self,
        authorizer_name: str,
        authorizer_function_arn: Optional[str],
        token_key_name: Optional[str],
        token_signing_public_keys: Optional[dict[str, str]],
        status: Optional[str],
        enable_caching_for_http: Optional[bool],
    ) -> FakeAuthorizer:
        if authorizer_name not in self.authorizers:
            raise ResourceNotFoundException(
                f"Authorizer {authorizer_name} does not exist."
            )
        authorizer = self.authorizers[authorizer_name]
        if authorizer_function_arn is not None:
            authorizer.authorizer_function_arn = authorizer_function_arn
        if token_key_name is not None:
            authorizer.token_key_name = token_key_name
        if token_signing_public_keys is not None:
            authorizer.token_signing_public_keys = token_signing_public_keys
        if status is not None:
            authorizer.status = status
        if enable_caching_for_http is not None:
            authorizer.enable_caching_for_http = enable_caching_for_http
        authorizer.last_modified_date = utcnow()
        return authorizer

    def delete_authorizer(self, authorizer_name: str) -> None:
        if authorizer_name not in self.authorizers:
            raise ResourceNotFoundException(
                f"Authorizer {authorizer_name} does not exist."
            )
        del self.authorizers[authorizer_name]

    def list_authorizers(self) -> list[FakeAuthorizer]:
        return list(self.authorizers.values())

    # --- Provisioning Templates ---

    def create_provisioning_template(
        self,
        template_name: str,
        description: Optional[str],
        template_body: str,
        enabled: Optional[bool],
        provisioning_role_arn: str,
        pre_provisioning_hook: Optional[dict[str, str]],
        tags: Optional[list[dict[str, str]]],
        template_type: Optional[str],
    ) -> FakeProvisioningTemplate:
        if template_name in self.provisioning_templates:
            raise ResourceAlreadyExistsException(
                f"Provisioning template {template_name} already exists.",
                template_name,
                self.provisioning_templates[template_name].arn,
            )
        template = FakeProvisioningTemplate(
            self.account_id,
            self.region_name,
            template_name,
            description,
            template_body,
            enabled,
            provisioning_role_arn,
            pre_provisioning_hook,
            tags,
            template_type,
        )
        self.provisioning_templates[template_name] = template
        return template

    def describe_provisioning_template(
        self, template_name: str
    ) -> FakeProvisioningTemplate:
        if template_name not in self.provisioning_templates:
            raise ResourceNotFoundException(
                f"Provisioning template {template_name} does not exist."
            )
        return self.provisioning_templates[template_name]

    def update_provisioning_template(
        self,
        template_name: str,
        description: Optional[str],
        enabled: Optional[bool],
        provisioning_role_arn: Optional[str],
        pre_provisioning_hook: Optional[dict[str, str]],
        default_version_id: Optional[int],
    ) -> None:
        if template_name not in self.provisioning_templates:
            raise ResourceNotFoundException(
                f"Provisioning template {template_name} does not exist."
            )
        template = self.provisioning_templates[template_name]
        if description is not None:
            template.description = description
        if enabled is not None:
            template.enabled = enabled
        if provisioning_role_arn is not None:
            template.provisioning_role_arn = provisioning_role_arn
        if pre_provisioning_hook is not None:
            template.pre_provisioning_hook = pre_provisioning_hook
        if default_version_id is not None:
            template.default_version_id = default_version_id
        template.last_modified_date = utcnow()

    def delete_provisioning_template(self, template_name: str) -> None:
        if template_name not in self.provisioning_templates:
            raise ResourceNotFoundException(
                f"Provisioning template {template_name} does not exist."
            )
        del self.provisioning_templates[template_name]

    def list_provisioning_templates(self) -> list[FakeProvisioningTemplate]:
        return list(self.provisioning_templates.values())

    # --- Dimensions ---

    def create_dimension(
        self,
        name: str,
        dimension_type: str,
        string_values: list[str],
        tags: Optional[list[dict[str, str]]],
    ) -> FakeDimension:
        if name in self.dimensions:
            raise ResourceAlreadyExistsException(
                f"Dimension {name} already exists.",
                name,
                self.dimensions[name].arn,
            )
        dimension = FakeDimension(
            self.account_id,
            self.region_name,
            name,
            dimension_type,
            string_values,
            tags,
        )
        self.dimensions[name] = dimension
        return dimension

    def describe_dimension(self, name: str) -> FakeDimension:
        if name not in self.dimensions:
            raise ResourceNotFoundException(f"Dimension {name} does not exist.")
        return self.dimensions[name]

    def update_dimension(self, name: str, string_values: list[str]) -> FakeDimension:
        if name not in self.dimensions:
            raise ResourceNotFoundException(f"Dimension {name} does not exist.")
        dimension = self.dimensions[name]
        dimension.string_values = string_values
        dimension.last_modified_date = utcnow()
        return dimension

    def delete_dimension(self, name: str) -> None:
        if name not in self.dimensions:
            raise ResourceNotFoundException(f"Dimension {name} does not exist.")
        del self.dimensions[name]

    def list_dimensions(self) -> list[str]:
        return list(self.dimensions.keys())

    # --- Custom Metrics ---

    def create_custom_metric(
        self,
        metric_name: str,
        display_name: Optional[str],
        metric_type: str,
        tags: Optional[list[dict[str, str]]],
    ) -> FakeCustomMetric:
        if metric_name in self.custom_metrics:
            raise ResourceAlreadyExistsException(
                f"Custom metric {metric_name} already exists.",
                metric_name,
                self.custom_metrics[metric_name].arn,
            )
        metric = FakeCustomMetric(
            self.account_id,
            self.region_name,
            metric_name,
            display_name,
            metric_type,
            tags,
        )
        self.custom_metrics[metric_name] = metric
        return metric

    def describe_custom_metric(self, metric_name: str) -> FakeCustomMetric:
        if metric_name not in self.custom_metrics:
            raise ResourceNotFoundException(
                f"Custom metric {metric_name} does not exist."
            )
        return self.custom_metrics[metric_name]

    def update_custom_metric(
        self, metric_name: str, display_name: str
    ) -> FakeCustomMetric:
        if metric_name not in self.custom_metrics:
            raise ResourceNotFoundException(
                f"Custom metric {metric_name} does not exist."
            )
        metric = self.custom_metrics[metric_name]
        metric.display_name = display_name
        metric.last_modified_date = utcnow()
        return metric

    def delete_custom_metric(self, metric_name: str) -> None:
        if metric_name not in self.custom_metrics:
            raise ResourceNotFoundException(
                f"Custom metric {metric_name} does not exist."
            )
        del self.custom_metrics[metric_name]

    def list_custom_metrics(self) -> list[str]:
        return list(self.custom_metrics.keys())

    # --- Fleet Metrics ---

    def create_fleet_metric(
        self,
        metric_name: str,
        query_string: str,
        aggregation_type: Optional[dict[str, Any]],
        period: Optional[int],
        aggregation_field: Optional[str],
        description: Optional[str],
        query_version: Optional[str],
        index_name: Optional[str],
        unit: Optional[str],
        tags: Optional[list[dict[str, str]]],
    ) -> FakeFleetMetric:
        if metric_name in self.fleet_metrics:
            raise ResourceAlreadyExistsException(
                f"Fleet metric {metric_name} already exists.",
                metric_name,
                self.fleet_metrics[metric_name].arn,
            )
        fleet_metric = FakeFleetMetric(
            self.account_id,
            self.region_name,
            metric_name,
            query_string,
            aggregation_type,
            period,
            aggregation_field,
            description,
            query_version,
            index_name,
            unit,
            tags,
        )
        self.fleet_metrics[metric_name] = fleet_metric
        return fleet_metric

    def describe_fleet_metric(self, metric_name: str) -> FakeFleetMetric:
        if metric_name not in self.fleet_metrics:
            raise ResourceNotFoundException(
                f"Fleet metric {metric_name} does not exist."
            )
        return self.fleet_metrics[metric_name]

    def update_fleet_metric(
        self,
        metric_name: str,
        query_string: Optional[str],
        aggregation_type: Optional[dict[str, Any]],
        period: Optional[int],
        aggregation_field: Optional[str],
        description: Optional[str],
        query_version: Optional[str],
        index_name: Optional[str],
        unit: Optional[str],
    ) -> None:
        if metric_name not in self.fleet_metrics:
            raise ResourceNotFoundException(
                f"Fleet metric {metric_name} does not exist."
            )
        fleet_metric = self.fleet_metrics[metric_name]
        if query_string is not None:
            fleet_metric.query_string = query_string
        if aggregation_type is not None:
            fleet_metric.aggregation_type = aggregation_type
        if period is not None:
            fleet_metric.period = period
        if aggregation_field is not None:
            fleet_metric.aggregation_field = aggregation_field
        if description is not None:
            fleet_metric.description = description
        if query_version is not None:
            fleet_metric.query_version = query_version
        if index_name is not None:
            fleet_metric.index_name = index_name
        if unit is not None:
            fleet_metric.unit = unit
        fleet_metric.version += 1
        fleet_metric.last_modified_date = utcnow()

    def delete_fleet_metric(self, metric_name: str) -> None:
        if metric_name not in self.fleet_metrics:
            raise ResourceNotFoundException(
                f"Fleet metric {metric_name} does not exist."
            )
        del self.fleet_metrics[metric_name]

    def list_fleet_metrics(self) -> list[FakeFleetMetric]:
        return list(self.fleet_metrics.values())

    # --- Event Configurations ---

    def describe_event_configurations(self) -> dict[str, dict[str, bool]]:
        if not self.event_configurations:
            # Return defaults for all event types
            event_types = [
                "THING",
                "THING_GROUP",
                "THING_TYPE",
                "THING_GROUP_MEMBERSHIP",
                "THING_GROUP_HIERARCHY",
                "THING_TYPE_ASSOCIATION",
                "JOB",
                "JOB_EXECUTION",
                "POLICY",
                "CERTIFICATE",
                "CA_CERTIFICATE",
            ]
            return {et: {"Enabled": False} for et in event_types}
        return self.event_configurations

    def update_event_configurations(
        self, event_configurations: dict[str, dict[str, bool]]
    ) -> None:
        self.event_configurations.update(event_configurations)

    # --- Index ---

    def describe_index(self, index_name: str) -> dict[str, Any]:
        if index_name != "AWS_Things":
            raise ResourceNotFoundException(f"Index {index_name} does not exist.")
        return {
            "indexName": "AWS_Things",
            "indexStatus": "ACTIVE",
            "schema": "REGISTRY_AND_SHADOW_AND_CONNECTIVITY_STATUS",
        }

    # --- Default Authorizer ---

    def set_default_authorizer(self, authorizer_name: str) -> FakeAuthorizer:
        if authorizer_name not in self.authorizers:
            raise ResourceNotFoundException(
                f"Authorizer {authorizer_name} does not exist."
            )
        self.default_authorizer_name = authorizer_name
        return self.authorizers[authorizer_name]

    def describe_default_authorizer(self) -> FakeAuthorizer:
        if not self.default_authorizer_name:
            raise ResourceNotFoundException("No default authorizer has been configured.")
        if self.default_authorizer_name not in self.authorizers:
            raise ResourceNotFoundException("No default authorizer has been configured.")
        return self.authorizers[self.default_authorizer_name]

    def clear_default_authorizer(self) -> None:
        self.default_authorizer_name = None

    # --- Account Audit Configuration ---

    def describe_account_audit_configuration(self) -> dict[str, Any]:
        if not self.account_audit_configuration:
            return {
                "roleArn": "",
                "auditNotificationTargetConfigurations": {},
                "auditCheckConfigurations": {},
            }
        return self.account_audit_configuration

    def update_account_audit_configuration(
        self,
        role_arn: Optional[str],
        audit_notification_target_configurations: Optional[dict[str, Any]],
        audit_check_configurations: Optional[dict[str, Any]],
    ) -> None:
        if role_arn is not None:
            self.account_audit_configuration["roleArn"] = role_arn
        if audit_notification_target_configurations is not None:
            self.account_audit_configuration[
                "auditNotificationTargetConfigurations"
            ] = audit_notification_target_configurations
        if audit_check_configurations is not None:
            self.account_audit_configuration[
                "auditCheckConfigurations"
            ] = audit_check_configurations

    # --- Audit stubs (finding, task, suppression, mitigation actions task) ---

    def describe_audit_finding(self, finding_id: str) -> dict[str, Any]:
        raise ResourceNotFoundException(f"Audit finding {finding_id} does not exist.")

    def describe_audit_task(self, task_id: str) -> dict[str, Any]:
        raise ResourceNotFoundException(f"Audit task {task_id} does not exist.")

    def describe_audit_suppression(
        self, check_name: str, resource_identifier: dict[str, Any]
    ) -> dict[str, Any]:
        raise ResourceNotFoundException("Audit suppression does not exist.")

    def describe_audit_mitigation_actions_task(
        self, task_id: str
    ) -> dict[str, Any]:
        raise ResourceNotFoundException(
            f"Audit mitigation actions task {task_id} does not exist."
        )

    def describe_detect_mitigation_actions_task(
        self, task_id: str
    ) -> dict[str, Any]:
        raise ResourceNotFoundException(
            f"Detect mitigation actions task {task_id} does not exist."
        )

    # --- Mitigation Actions ---

    def create_mitigation_action(
        self,
        action_name: str,
        role_arn: str,
        action_params: dict[str, Any],
        tags: Optional[list[dict[str, str]]],
    ) -> FakeMitigationAction:
        if action_name in self.mitigation_actions:
            raise ResourceAlreadyExistsException(
                f"Mitigation action {action_name} already exists.",
                action_name,
                self.mitigation_actions[action_name].arn,
            )
        action = FakeMitigationAction(
            self.account_id,
            self.region_name,
            action_name,
            role_arn,
            action_params,
            tags,
        )
        self.mitigation_actions[action_name] = action
        return action

    def describe_mitigation_action(
        self, action_name: str
    ) -> FakeMitigationAction:
        if action_name not in self.mitigation_actions:
            raise ResourceNotFoundException(
                f"Mitigation action {action_name} does not exist."
            )
        return self.mitigation_actions[action_name]

    def delete_mitigation_action(self, action_name: str) -> None:
        if action_name not in self.mitigation_actions:
            raise ResourceNotFoundException(
                f"Mitigation action {action_name} does not exist."
            )
        del self.mitigation_actions[action_name]

    def list_mitigation_actions(self) -> list[FakeMitigationAction]:
        return list(self.mitigation_actions.values())

    # --- Scheduled Audits ---

    def create_scheduled_audit(
        self,
        scheduled_audit_name: str,
        frequency: str,
        day_of_month: Optional[str],
        day_of_week: Optional[str],
        target_check_names: list[str],
        tags: Optional[list[dict[str, str]]],
    ) -> FakeScheduledAudit:
        if scheduled_audit_name in self.scheduled_audits:
            raise ResourceAlreadyExistsException(
                f"Scheduled audit {scheduled_audit_name} already exists.",
                scheduled_audit_name,
                self.scheduled_audits[scheduled_audit_name].arn,
            )
        audit = FakeScheduledAudit(
            self.account_id,
            self.region_name,
            scheduled_audit_name,
            frequency,
            day_of_month,
            day_of_week,
            target_check_names,
            tags,
        )
        self.scheduled_audits[scheduled_audit_name] = audit
        return audit

    def describe_scheduled_audit(
        self, scheduled_audit_name: str
    ) -> FakeScheduledAudit:
        if scheduled_audit_name not in self.scheduled_audits:
            raise ResourceNotFoundException(
                f"Scheduled audit {scheduled_audit_name} does not exist."
            )
        return self.scheduled_audits[scheduled_audit_name]

    def delete_scheduled_audit(self, scheduled_audit_name: str) -> None:
        if scheduled_audit_name not in self.scheduled_audits:
            raise ResourceNotFoundException(
                f"Scheduled audit {scheduled_audit_name} does not exist."
            )
        del self.scheduled_audits[scheduled_audit_name]

    def list_scheduled_audits(self) -> list[FakeScheduledAudit]:
        return list(self.scheduled_audits.values())

    # --- Provisioning Template Versions ---

    def create_provisioning_template_version(
        self, template_name: str, template_body: str, set_as_default: bool
    ) -> dict[str, Any]:
        if template_name not in self.provisioning_templates:
            raise ResourceNotFoundException(
                f"Provisioning template {template_name} does not exist."
            )
        template = self.provisioning_templates[template_name]
        if template_name not in self.provisioning_template_versions:
            # Store version 1 (the original)
            self.provisioning_template_versions[template_name] = [
                {
                    "versionId": 1,
                    "templateBody": template.template_body,
                    "isDefaultVersion": True,
                    "creationDate": template.creation_date,
                }
            ]
        versions = self.provisioning_template_versions[template_name]
        new_version_id = len(versions) + 1
        version_entry = {
            "versionId": new_version_id,
            "templateBody": template_body,
            "isDefaultVersion": bool(set_as_default),
            "creationDate": utcnow(),
        }
        if set_as_default:
            for v in versions:
                v["isDefaultVersion"] = False
            template.default_version_id = new_version_id
            template.template_body = template_body
        versions.append(version_entry)
        return {
            "templateArn": template.arn,
            "templateName": template_name,
            "versionId": new_version_id,
            "isDefaultVersion": bool(set_as_default),
        }

    def describe_provisioning_template_version(
        self, template_name: str, version_id: int
    ) -> dict[str, Any]:
        if template_name not in self.provisioning_templates:
            raise ResourceNotFoundException(
                f"Provisioning template {template_name} does not exist."
            )
        if template_name not in self.provisioning_template_versions:
            # Only version 1 exists (the original)
            template = self.provisioning_templates[template_name]
            if version_id != 1:
                raise ResourceNotFoundException(
                    f"Version {version_id} of provisioning template {template_name} does not exist."
                )
            return {
                "versionId": 1,
                "templateBody": template.template_body,
                "isDefaultVersion": True,
                "creationDate": template.creation_date,
            }
        versions = self.provisioning_template_versions[template_name]
        for v in versions:
            if v["versionId"] == version_id:
                return v
        raise ResourceNotFoundException(
            f"Version {version_id} of provisioning template {template_name} does not exist."
        )

    # --- Streams ---

    def create_stream(
        self,
        stream_id: str,
        description: str,
        files: list[dict[str, Any]],
        role_arn: str,
        tags: Optional[list[dict[str, str]]],
    ) -> FakeStream:
        if stream_id in self.streams:
            raise ResourceAlreadyExistsException(
                f"Stream {stream_id} already exists.",
                stream_id,
                self.streams[stream_id].arn,
            )
        stream = FakeStream(
            self.account_id,
            self.region_name,
            stream_id,
            description,
            files,
            role_arn,
            tags,
        )
        self.streams[stream_id] = stream
        return stream

    def describe_stream(self, stream_id: str) -> FakeStream:
        if stream_id not in self.streams:
            raise ResourceNotFoundException(
                f"Stream {stream_id} does not exist."
            )
        return self.streams[stream_id]

    def delete_stream(self, stream_id: str) -> None:
        if stream_id not in self.streams:
            raise ResourceNotFoundException(
                f"Stream {stream_id} does not exist."
            )
        del self.streams[stream_id]

    def list_streams(self) -> list[FakeStream]:
        return list(self.streams.values())

    # --- Managed Job Templates (stub) ---

    def describe_managed_job_template(
        self, template_name: str, template_version: Optional[str]
    ) -> dict[str, Any]:
        raise ResourceNotFoundException(
            f"Managed job template {template_name} does not exist."
        )

    # --- Thing Registration Task (stub) ---

    def describe_thing_registration_task(self, task_id: str) -> dict[str, Any]:
        raise ResourceNotFoundException(
            f"Thing registration task {task_id} does not exist."
        )

    def get_statistics(
        self,
        index_name: Optional[str],
        query_string: str,
        aggregation_field: Optional[str],
        query_version: Optional[str],
    ) -> dict[str, Any]:
        """Return mock statistics for fleet indexing queries."""
        # Count things matching the query (simplified: return total thing count)
        count = len(self.things)
        statistics = {"count": count}
        if aggregation_field:
            statistics.update(
                {
                    "average": 0.0,
                    "sum": 0.0,
                    "minimum": 0.0,
                    "maximum": 0.0,
                    "sumOfSquares": 0.0,
                    "variance": 0.0,
                    "stdDeviation": 0.0,
                }
            )
        return statistics

    def get_topic_rule_destination(self, arn: str) -> dict[str, Any]:
        """Return a topic rule destination by ARN. Not yet stored, so always raises."""
        raise ResourceNotFoundException()

    def get_v2_logging_options(self) -> dict[str, Any]:
        """Return default V2 logging options."""
        return {
            "roleArn": "",
            "defaultLogLevel": "WARN",
            "disableAllLogs": False,
        }

    def list_audit_findings(
        self,
        task_id: Optional[str],
        check_name: Optional[str],
        max_results: Optional[int],
        next_token: Optional[str],
    ) -> dict[str, Any]:
        """Return empty audit findings list (auditing not yet implemented)."""
        return {"findings": [], "nextToken": None}

    def list_audit_mitigation_actions_executions(
        self,
        task_id: str,
        finding_id: str,
        max_results: Optional[int],
        next_token: Optional[str],
    ) -> dict[str, Any]:
        """Return empty audit mitigation actions executions list."""
        return {"actionsExecutions": [], "nextToken": None}

    def list_audit_mitigation_actions_tasks(
        self,
        start_time: str,
        end_time: str,
        max_results: Optional[int],
        next_token: Optional[str],
    ) -> dict[str, Any]:
        """Return empty audit mitigation actions tasks list."""
        return {"tasks": [], "nextToken": None}

    def list_audit_suppressions(
        self,
        max_results: Optional[int],
        next_token: Optional[str],
    ) -> dict[str, Any]:
        """Return empty audit suppressions list."""
        return {"suppressions": [], "nextToken": None}

    def list_audit_tasks(
        self,
        start_time: str,
        end_time: str,
        max_results: Optional[int],
        next_token: Optional[str],
    ) -> dict[str, Any]:
        """Return empty audit tasks list."""
        return {"tasks": [], "nextToken": None}

    def list_detect_mitigation_actions_executions(
        self,
        task_id: Optional[str],
        max_results: Optional[int],
        next_token: Optional[str],
    ) -> dict[str, Any]:
        """Return empty detect mitigation actions executions list."""
        return {"actionsExecutions": [], "nextToken": None}

    def list_detect_mitigation_actions_tasks(
        self,
        start_time: str,
        end_time: str,
        max_results: Optional[int],
        next_token: Optional[str],
    ) -> dict[str, Any]:
        """Return empty detect mitigation actions tasks list."""
        return {"tasks": [], "nextToken": None}


iot_backends = BackendDict(IoTBackend, "iot")
