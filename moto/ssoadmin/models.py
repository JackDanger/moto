import json
from typing import Any, Optional

from moto.core.base_backend import BackendDict, BaseBackend
from moto.core.common_models import BaseModel
from moto.core.utils import unix_time
from moto.iam.aws_managed_policies import aws_managed_policies_data
from moto.moto_api._internal import mock_random as random
from moto.utilities.paginator import paginate
from moto.utilities.utils import get_partition

from .exceptions import (
    ConflictException,
    ResourceNotFoundException,
    ServiceQuotaExceededException,
    ValidationException,
)
from .utils import PAGINATION_MODEL

# https://docs.aws.amazon.com/singlesignon/latest/userguide/limits.html
MAX_MANAGED_POLICIES_PER_PERMISSION_SET = 20


class AccountAssignment(BaseModel):
    def __init__(
        self,
        instance_arn: str,
        target_id: str,
        target_type: str,
        permission_set_arn: str,
        principal_type: str,
        principal_id: str,
    ):
        self.request_id = str(random.uuid4())
        self.instance_arn = instance_arn
        self.target_id = target_id
        self.target_type = target_type
        self.permission_set_arn = permission_set_arn
        self.principal_type = principal_type
        self.principal_id = principal_id
        self.created_date = unix_time()

    def to_json(
        self, include_creation_date: bool = False, include_request_id: bool = False
    ) -> dict[str, Any]:
        summary: dict[str, Any] = {
            "TargetId": self.target_id,
            "TargetType": self.target_type,
            "PermissionSetArn": self.permission_set_arn,
            "PrincipalType": self.principal_type,
            "PrincipalId": self.principal_id,
        }
        if include_creation_date:
            summary["CreatedDate"] = self.created_date
        if include_request_id:
            summary["RequestId"] = self.request_id
        return summary


class PermissionSet(BaseModel):
    def __init__(
        self,
        name: str,
        description: str,
        instance_arn: str,
        session_duration: str,
        relay_state: str,
        tags: list[dict[str, str]],
    ):
        self.name = name
        self.description = description
        self.instance_arn = instance_arn
        self.permission_set_arn = PermissionSet.generate_id(instance_arn)
        self.session_duration = session_duration
        self.relay_state = relay_state
        self.tags = tags
        self.created_date = unix_time()
        self.inline_policy = ""
        self.managed_policies: list[ManagedPolicy] = []
        self.customer_managed_policies: list[CustomerManagedPolicy] = []
        self.total_managed_policies_attached = (
            0  # this will also include customer managed policies
        )

    def to_json(self, include_creation_date: bool = False) -> dict[str, Any]:
        summary: dict[str, Any] = {
            "Name": self.name,
            "Description": self.description,
            "PermissionSetArn": self.permission_set_arn,
            "SessionDuration": self.session_duration,
            "RelayState": self.relay_state,
        }
        if include_creation_date:
            summary["CreatedDate"] = self.created_date
        return summary

    @staticmethod
    def generate_id(instance_arn: str) -> str:
        return instance_arn + "/ps-" + random.get_random_string(length=16).lower()


class ManagedPolicy(BaseModel):
    def __init__(self, arn: str, name: str):
        self.arn = arn
        self.name = name

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, ManagedPolicy):
            return False
        return self.arn == other.arn


class CustomerManagedPolicy(BaseModel):
    def __init__(self, name: str, path: str = "/"):
        self.name = name
        self.path = path

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, CustomerManagedPolicy):
            return False
        return f"{self.path}{self.name}" == f"{other.path}{other.name}"


class InstanceAccessControlAttributeConfiguration:
    def __init__(self, access_control_attributes: list[dict[str, Any]]):
        self.access_control_attributes = access_control_attributes
        self.status = "ENABLED"
        self.status_reason: Optional[str] = None

    def to_json(self) -> dict[str, Any]:
        return {
            "AccessControlAttributes": self.access_control_attributes,
            "Status": self.status,
            "StatusReason": self.status_reason,
        }


class Application:
    def __init__(
        self,
        application_provider_arn: str,
        instance_arn: str,
        name: str,
        description: Optional[str],
        portal_options: Optional[dict[str, Any]],
        status: str,
        tags: list[dict[str, str]],
        client_token: Optional[str],
        region: str,
        account_id: str,
    ):
        self.application_provider_arn = application_provider_arn
        self.instance_arn = instance_arn
        self.name = name
        self.description = description
        self.portal_options = portal_options or {}
        self.status = status
        self.tags = tags or []
        self.created_date = unix_time()
        self.application_arn = (
            f"arn:{get_partition(region)}:sso::{account_id}:application/"
            f"ssoins-{random.get_random_string(length=16, lower_case=True)}/"
            f"apl-{random.get_random_string(length=16, lower_case=True)}"
        )
        self.assignments: list[ApplicationAssignment] = []
        self.access_scopes: dict[str, dict[str, Any]] = {}
        self.authentication_methods: dict[str, dict[str, Any]] = {}
        self.grants: dict[str, dict[str, Any]] = {}
        self.assignment_required: bool = False
        self.session_configuration: Optional[dict[str, Any]] = None

    def to_json(self, include_all: bool = False) -> dict[str, Any]:
        result: dict[str, Any] = {
            "ApplicationArn": self.application_arn,
            "ApplicationProviderArn": self.application_provider_arn,
            "InstanceArn": self.instance_arn,
            "Name": self.name,
            "Status": self.status,
            "CreatedDate": self.created_date,
        }
        if self.description is not None:
            result["Description"] = self.description
        if self.portal_options:
            result["PortalOptions"] = self.portal_options
        return result


class ApplicationAssignment:
    def __init__(
        self,
        application_arn: str,
        principal_type: str,
        principal_id: str,
    ):
        self.application_arn = application_arn
        self.principal_type = principal_type
        self.principal_id = principal_id

    def to_json(self) -> dict[str, Any]:
        return {
            "ApplicationArn": self.application_arn,
            "PrincipalType": self.principal_type,
            "PrincipalId": self.principal_id,
        }


class TrustedTokenIssuer:
    def __init__(
        self,
        name: str,
        trusted_token_issuer_type: str,
        trusted_token_issuer_configuration: dict[str, Any],
        instance_arn: str,
        tags: list[dict[str, str]],
        region: str,
        account_id: str,
        client_token: Optional[str] = None,
    ):
        self.name = name
        self.trusted_token_issuer_type = trusted_token_issuer_type
        self.trusted_token_issuer_configuration = trusted_token_issuer_configuration
        self.instance_arn = instance_arn
        self.tags = tags or []
        self.trusted_token_issuer_arn = (
            f"arn:{get_partition(region)}:sso::{account_id}:trustedTokenIssuer/"
            f"ssoins-{random.get_random_string(length=16, lower_case=True)}/"
            f"tti-{random.get_random_string(length=16, lower_case=True)}"
        )

    def to_json(self) -> dict[str, Any]:
        return {
            "TrustedTokenIssuerArn": self.trusted_token_issuer_arn,
            "Name": self.name,
            "TrustedTokenIssuerType": self.trusted_token_issuer_type,
            "TrustedTokenIssuerConfiguration": self.trusted_token_issuer_configuration,
        }


class Instance:
    def __init__(self, account_id: str, region: str):
        self.created_date = unix_time()
        self.identity_store_id = (
            f"d-{random.get_random_string(length=10, lower_case=True)}"
        )
        self.instance_arn = f"arn:{get_partition(region)}:sso:::instance/ssoins-{random.get_random_string(length=16, lower_case=True)}"
        self.account_id = account_id
        self.status = "ACTIVE"
        self.name: Optional[str] = None

        self.provisioned_permission_sets: list[PermissionSet] = []
        self.tags: list[dict[str, str]] = []
        self.access_control_attribute_config: Optional[
            InstanceAccessControlAttributeConfiguration
        ] = None

    def to_json(self) -> dict[str, Any]:
        return {
            "CreatedDate": self.created_date,
            "IdentityStoreId": self.identity_store_id,
            "InstanceArn": self.instance_arn,
            "Name": self.name,
            "OwnerAccountId": self.account_id,
            "Status": self.status,
        }


class SSOAdminBackend(BaseBackend):
    """Implementation of SSOAdmin APIs."""

    def __init__(self, region_name: str, account_id: str):
        super().__init__(region_name, account_id)
        self.account_assignments: list[AccountAssignment] = []
        self.deleted_account_assignments: list[AccountAssignment] = []
        self.permission_sets: list[PermissionSet] = []
        self.aws_managed_policies: Optional[dict[str, Any]] = None
        self.instances: list[Instance] = []
        self.applications: list[Application] = []
        self.trusted_token_issuers: list[TrustedTokenIssuer] = []
        # tag store: resource_arn -> list of tags
        self._tags: dict[str, list[dict[str, str]]] = {}

        self.instances.append(Instance(self.account_id, self.region_name))

    def create_account_assignment(
        self,
        instance_arn: str,
        target_id: str,
        target_type: str,
        permission_set_arn: str,
        principal_type: str,
        principal_id: str,
    ) -> dict[str, Any]:
        assignment = AccountAssignment(
            instance_arn,
            target_id,
            target_type,
            permission_set_arn,
            principal_type,
            principal_id,
        )
        self.account_assignments.append(assignment)
        return assignment.to_json(include_creation_date=True, include_request_id=True)

    def delete_account_assignment(
        self,
        instance_arn: str,
        target_id: str,
        target_type: str,
        permission_set_arn: str,
        principal_type: str,
        principal_id: str,
    ) -> dict[str, Any]:
        account = self._find_account(
            instance_arn,
            target_id,
            target_type,
            permission_set_arn,
            principal_type,
            principal_id,
        )
        self.deleted_account_assignments.append(account)
        self.account_assignments.remove(account)
        return account.to_json(include_creation_date=True, include_request_id=True)

    def _find_account(
        self,
        instance_arn: str,
        target_id: str,
        target_type: str,
        permission_set_arn: str,
        principal_type: str,
        principal_id: str,
    ) -> AccountAssignment:
        for account in self.account_assignments:
            instance_arn_match = account.instance_arn == instance_arn
            target_id_match = account.target_id == target_id
            target_type_match = account.target_type == target_type
            permission_set_match = account.permission_set_arn == permission_set_arn
            principal_type_match = account.principal_type == principal_type
            principal_id_match = account.principal_id == principal_id
            if (
                instance_arn_match
                and target_id_match
                and target_type_match
                and permission_set_match
                and principal_type_match
                and principal_id_match
            ):
                return account
        raise ResourceNotFoundException

    def _find_managed_policy(self, managed_policy_arn: str) -> ManagedPolicy:
        """
        Checks to make sure the managed policy exists.
        This pulls from moto/iam/aws_managed_policies.py
        """
        # Lazy loading of aws managed policies file
        if self.aws_managed_policies is None:
            self.aws_managed_policies = json.loads(aws_managed_policies_data)

        policy_name = managed_policy_arn.split("/")[-1]
        managed_policy = self.aws_managed_policies.get(policy_name, None)
        if managed_policy is not None:
            path = managed_policy.get("path", "/")
            expected_arn = f"arn:{self.partition}:iam::aws:policy{path}{policy_name}"

            if managed_policy_arn == expected_arn:
                return ManagedPolicy(managed_policy_arn, policy_name)
        raise ResourceNotFoundException(
            f"Policy does not exist with ARN: {managed_policy_arn}"
        )

    @paginate(PAGINATION_MODEL)
    def list_account_assignments(
        self, instance_arn: str, account_id: str, permission_set_arn: str
    ) -> list[dict[str, str]]:
        account_assignments = []
        for assignment in self.account_assignments:
            if (
                assignment.instance_arn == instance_arn
                and assignment.target_id == account_id
                and assignment.permission_set_arn == permission_set_arn
            ):
                account_assignments.append(
                    {
                        "AccountId": assignment.target_id,
                        "PermissionSetArn": assignment.permission_set_arn,
                        "PrincipalType": assignment.principal_type,
                        "PrincipalId": assignment.principal_id,
                    }
                )
        return account_assignments

    @paginate(PAGINATION_MODEL)
    def list_account_assignments_for_principal(
        self,
        filter_: dict[str, Any],
        instance_arn: str,
        principal_id: str,
        principal_type: str,
    ) -> list[dict[str, str]]:
        return [
            {
                "AccountId": account_assignment.target_id,
                "PermissionSetArn": account_assignment.permission_set_arn,
                "PrincipalId": account_assignment.principal_id,
                "PrincipalType": account_assignment.principal_type,
            }
            for account_assignment in self.account_assignments
            if all(
                [
                    filter_.get("AccountId", account_assignment.target_id)
                    == account_assignment.target_id,
                    principal_id == account_assignment.principal_id,
                    principal_type == account_assignment.principal_type,
                    instance_arn == account_assignment.instance_arn,
                ]
            )
        ]

    def create_permission_set(
        self,
        name: str,
        description: str,
        instance_arn: str,
        session_duration: str,
        relay_state: str,
        tags: list[dict[str, str]],
    ) -> dict[str, Any]:
        permission_set = PermissionSet(
            name,
            description,
            instance_arn,
            session_duration,
            relay_state,
            tags,
        )
        self.permission_sets.append(permission_set)
        return permission_set.to_json(True)

    def update_permission_set(
        self,
        instance_arn: str,
        permission_set_arn: str,
        description: str,
        session_duration: str,
        relay_state: str,
    ) -> dict[str, Any]:
        permission_set = self._find_permission_set(
            instance_arn,
            permission_set_arn,
        )
        self.permission_sets.remove(permission_set)
        permission_set.description = description
        permission_set.session_duration = session_duration
        permission_set.relay_state = relay_state
        self.permission_sets.append(permission_set)
        return permission_set.to_json(True)

    def describe_permission_set(
        self, instance_arn: str, permission_set_arn: str
    ) -> dict[str, Any]:
        permission_set = self._find_permission_set(
            instance_arn,
            permission_set_arn,
        )
        return permission_set.to_json(True)

    def delete_permission_set(
        self, instance_arn: str, permission_set_arn: str
    ) -> dict[str, Any]:
        permission_set = self._find_permission_set(
            instance_arn,
            permission_set_arn,
        )
        self.permission_sets.remove(permission_set)

        for instance in self.instances:
            try:
                instance.provisioned_permission_sets.remove(permission_set)
            except ValueError:
                pass

        return permission_set.to_json(include_creation_date=True)

    def _find_permission_set(
        self, instance_arn: str, permission_set_arn: str
    ) -> PermissionSet:
        for permission_set in self.permission_sets:
            instance_arn_match = permission_set.instance_arn == instance_arn
            permission_set_match = (
                permission_set.permission_set_arn == permission_set_arn
            )
            if instance_arn_match and permission_set_match:
                return permission_set
        ps_id = permission_set_arn.split("/")[-1]
        raise ResourceNotFoundException(
            message=f"Could not find PermissionSet with id {ps_id}"
        )

    @paginate(pagination_model=PAGINATION_MODEL)
    def list_permission_sets(self, instance_arn: str) -> list[PermissionSet]:
        permission_sets = []
        for permission_set in self.permission_sets:
            if permission_set.instance_arn == instance_arn:
                permission_sets.append(permission_set)
        return permission_sets

    def put_inline_policy_to_permission_set(
        self, instance_arn: str, permission_set_arn: str, inline_policy: str
    ) -> None:
        permission_set = self._find_permission_set(
            instance_arn,
            permission_set_arn,
        )
        permission_set.inline_policy = inline_policy

    def get_inline_policy_for_permission_set(
        self, instance_arn: str, permission_set_arn: str
    ) -> str:
        permission_set = self._find_permission_set(
            instance_arn,
            permission_set_arn,
        )
        return permission_set.inline_policy

    def delete_inline_policy_from_permission_set(
        self, instance_arn: str, permission_set_arn: str
    ) -> None:
        permission_set = self._find_permission_set(
            instance_arn,
            permission_set_arn,
        )
        permission_set.inline_policy = ""

    def attach_managed_policy_to_permission_set(
        self, instance_arn: str, permission_set_arn: str, managed_policy_arn: str
    ) -> None:
        permissionset = self._find_permission_set(
            instance_arn,
            permission_set_arn,
        )
        managed_policy = self._find_managed_policy(managed_policy_arn)

        permissionset_id = permission_set_arn.split("/")[-1]
        if managed_policy in permissionset.managed_policies:
            raise ConflictException(
                f"Permission set with id {permissionset_id} already has a typed link attachment to a manged policy with {managed_policy_arn}"
            )

        if (
            permissionset.total_managed_policies_attached
            >= MAX_MANAGED_POLICIES_PER_PERMISSION_SET
        ):
            permissionset_id = permission_set_arn.split("/")[-1]
            raise ServiceQuotaExceededException(
                f"You have exceeded AWS SSO limits. Cannot create ManagedPolicy more than {MAX_MANAGED_POLICIES_PER_PERMISSION_SET} for id {permissionset_id}. Please refer to https://docs.aws.amazon.com/singlesignon/latest/userguide/limits.html"
            )

        permissionset.managed_policies.append(managed_policy)
        permissionset.total_managed_policies_attached += 1

    @paginate(pagination_model=PAGINATION_MODEL)
    def list_managed_policies_in_permission_set(
        self,
        instance_arn: str,
        permission_set_arn: str,
    ) -> list[ManagedPolicy]:
        permissionset = self._find_permission_set(
            instance_arn,
            permission_set_arn,
        )
        return permissionset.managed_policies

    def _detach_managed_policy(
        self, instance_arn: str, permission_set_arn: str, managed_policy_arn: str
    ) -> None:
        # ensure permission_set exists
        permissionset = self._find_permission_set(
            instance_arn,
            permission_set_arn,
        )

        for managed_policy in permissionset.managed_policies:
            if managed_policy.arn == managed_policy_arn:
                permissionset.managed_policies.remove(managed_policy)
                permissionset.total_managed_policies_attached -= 1
                return

        raise ResourceNotFoundException(
            f"Could not find ManagedPolicy with arn {managed_policy_arn}"
        )

    def detach_managed_policy_from_permission_set(
        self, instance_arn: str, permission_set_arn: str, managed_policy_arn: str
    ) -> None:
        self._detach_managed_policy(
            instance_arn, permission_set_arn, managed_policy_arn
        )

    def attach_customer_managed_policy_reference_to_permission_set(
        self,
        instance_arn: str,
        permission_set_arn: str,
        customer_managed_policy_reference: dict[str, str],
    ) -> None:
        permissionset = self._find_permission_set(
            permission_set_arn=permission_set_arn, instance_arn=instance_arn
        )

        name = customer_managed_policy_reference["Name"]
        path = customer_managed_policy_reference.get("Path", "/")  # default path is "/"
        customer_managed_policy = CustomerManagedPolicy(name=name, path=path)

        if customer_managed_policy in permissionset.customer_managed_policies:
            raise ConflictException(
                f"Given customer managed policy with name: {name}  and path {path} already attached"
            )

        if (
            permissionset.total_managed_policies_attached
            >= MAX_MANAGED_POLICIES_PER_PERMISSION_SET
        ):
            raise ServiceQuotaExceededException(
                f"Cannot attach managed policy: number of attached managed policies is already at maximum {MAX_MANAGED_POLICIES_PER_PERMISSION_SET}"
            )

        permissionset.customer_managed_policies.append(customer_managed_policy)
        permissionset.total_managed_policies_attached += 1

    @paginate(pagination_model=PAGINATION_MODEL)
    def list_customer_managed_policy_references_in_permission_set(
        self, instance_arn: str, permission_set_arn: str
    ) -> list[CustomerManagedPolicy]:
        permissionset = self._find_permission_set(
            permission_set_arn=permission_set_arn, instance_arn=instance_arn
        )
        return permissionset.customer_managed_policies

    def _detach_customer_managed_policy_from_permissionset(
        self,
        instance_arn: str,
        permission_set_arn: str,
        customer_managed_policy_reference: dict[str, str],
    ) -> None:
        permissionset = self._find_permission_set(
            permission_set_arn=permission_set_arn, instance_arn=instance_arn
        )
        path: str = customer_managed_policy_reference.get("Path", "/")
        name: str = customer_managed_policy_reference["Name"]

        for customer_managed_policy in permissionset.customer_managed_policies:
            if (
                customer_managed_policy.name == name
                and customer_managed_policy.path == path
            ):
                permissionset.customer_managed_policies.remove(customer_managed_policy)
                permissionset.total_managed_policies_attached -= 1
                return

        raise ResourceNotFoundException(
            f"Given managed policy with name: {name}  and path {path} does not exist on PermissionSet"
        )

    def detach_customer_managed_policy_reference_from_permission_set(
        self,
        instance_arn: str,
        permission_set_arn: str,
        customer_managed_policy_reference: dict[str, str],
    ) -> None:
        self._detach_customer_managed_policy_from_permissionset(
            instance_arn=instance_arn,
            permission_set_arn=permission_set_arn,
            customer_managed_policy_reference=customer_managed_policy_reference,
        )

    def describe_account_assignment_creation_status(
        self, account_assignment_creation_request_id: str, instance_arn: str
    ) -> dict[str, Any]:
        for account in self.account_assignments:
            if account.request_id == account_assignment_creation_request_id:
                return account.to_json(
                    include_creation_date=True, include_request_id=True
                )

        raise ResourceNotFoundException

    def describe_account_assignment_deletion_status(
        self, account_assignment_deletion_request_id: str, instance_arn: str
    ) -> dict[str, Any]:
        for account in self.deleted_account_assignments:
            if account.request_id == account_assignment_deletion_request_id:
                return account.to_json(
                    include_creation_date=True, include_request_id=True
                )

        raise ResourceNotFoundException

    def list_instances(self) -> list[Instance]:
        return self.instances

    def update_instance(self, instance_arn: str, name: str) -> None:
        for instance in self.instances:
            if instance.instance_arn == instance_arn:
                instance.name = name

    def provision_permission_set(
        self, instance_arn: str, permission_set_arn: str
    ) -> None:
        """
        The TargetType/TargetId parameters are currently ignored - PermissionSets are simply provisioned to the caller's account
        """
        permission_set = self._find_permission_set(instance_arn, permission_set_arn)
        instance = [i for i in self.instances if i.instance_arn == instance_arn][0]
        instance.provisioned_permission_sets.append(permission_set)

    def list_permission_sets_provisioned_to_account(
        self, instance_arn: str
    ) -> list[PermissionSet]:
        """
        The following parameters are not yet implemented: AccountId, ProvisioningStatus, MaxResults, NextToken
        """
        for instance in self.instances:
            if instance.instance_arn == instance_arn:
                return instance.provisioned_permission_sets
        return []

    def list_accounts_for_provisioned_permission_set(
        self, instance_arn: str, permission_set_arn: str
    ) -> list[str]:
        """
        The following parameters are not yet implemented: MaxResults, NextToken, ProvisioningStatus
        """
        for instance in self.instances:
            if instance.instance_arn == instance_arn:
                for ps in instance.provisioned_permission_sets:
                    if ps.permission_set_arn == permission_set_arn:
                        return [self.account_id]
        return []

    # --- Tagging ---

    def tag_resource(
        self, instance_arn: str, resource_arn: str, tags: list[dict[str, str]]
    ) -> None:
        existing = self._tags.get(resource_arn, [])
        # merge: overwrite existing keys, add new
        existing_map = {t["Key"]: t for t in existing}
        for tag in tags:
            existing_map[tag["Key"]] = tag
        self._tags[resource_arn] = list(existing_map.values())

    def untag_resource(
        self, instance_arn: str, resource_arn: str, tag_keys: list[str]
    ) -> None:
        existing = self._tags.get(resource_arn, [])
        self._tags[resource_arn] = [t for t in existing if t["Key"] not in tag_keys]

    @paginate(pagination_model=PAGINATION_MODEL)
    def list_tags_for_resource(
        self, instance_arn: str, resource_arn: str
    ) -> list[dict[str, str]]:
        return self._tags.get(resource_arn, [])

    # --- Permissions Boundary ---

    def put_permissions_boundary_to_permission_set(
        self,
        instance_arn: str,
        permission_set_arn: str,
        permissions_boundary: dict[str, Any],
    ) -> None:
        permission_set = self._find_permission_set(instance_arn, permission_set_arn)
        permission_set.permissions_boundary = permissions_boundary  # type: ignore[attr-defined]

    def get_permissions_boundary_for_permission_set(
        self, instance_arn: str, permission_set_arn: str
    ) -> dict[str, Any]:
        permission_set = self._find_permission_set(instance_arn, permission_set_arn)
        boundary = getattr(permission_set, "permissions_boundary", None)
        if boundary is None:
            raise ResourceNotFoundException(
                f"PermissionSet {permission_set_arn} has no permissions boundary"
            )
        return boundary

    def delete_permissions_boundary_from_permission_set(
        self, instance_arn: str, permission_set_arn: str
    ) -> None:
        permission_set = self._find_permission_set(instance_arn, permission_set_arn)
        permission_set.permissions_boundary = None  # type: ignore[attr-defined]

    # --- Instance CRUD ---

    def create_instance(
        self,
        client_token: Optional[str],
        name: Optional[str],
        tags: list[dict[str, str]],
    ) -> Instance:
        instance = Instance(self.account_id, self.region_name)
        instance.name = name
        instance.tags = tags or []
        instance.status = "ACTIVE"
        self.instances.append(instance)
        return instance

    def delete_instance(self, instance_arn: str) -> None:
        instance = self._find_instance(instance_arn)
        self.instances.remove(instance)

    def describe_instance(self, instance_arn: str) -> Instance:
        return self._find_instance(instance_arn)

    def _find_instance(self, instance_arn: str) -> Instance:
        for instance in self.instances:
            if instance.instance_arn == instance_arn:
                return instance
        raise ResourceNotFoundException(f"Instance {instance_arn} not found")

    # --- Instance Access Control Attribute Configuration ---

    def create_instance_access_control_attribute_configuration(
        self,
        instance_arn: str,
        instance_access_control_attribute_configuration: dict[str, Any],
    ) -> None:
        instance = self._find_instance(instance_arn)
        if instance.access_control_attribute_config is not None:
            raise ConflictException(
                f"Instance {instance_arn} already has access control attribute configuration"
            )
        access_control_attributes = instance_access_control_attribute_configuration.get(
            "AccessControlAttributes", []
        )
        instance.access_control_attribute_config = (
            InstanceAccessControlAttributeConfiguration(access_control_attributes)
        )

    def describe_instance_access_control_attribute_configuration(
        self, instance_arn: str
    ) -> dict[str, Any]:
        instance = self._find_instance(instance_arn)
        if instance.access_control_attribute_config is None:
            raise ResourceNotFoundException(
                f"Instance {instance_arn} has no access control attribute configuration"
            )
        return instance.access_control_attribute_config.to_json()

    def update_instance_access_control_attribute_configuration(
        self,
        instance_arn: str,
        instance_access_control_attribute_configuration: dict[str, Any],
    ) -> None:
        instance = self._find_instance(instance_arn)
        if instance.access_control_attribute_config is None:
            raise ResourceNotFoundException(
                f"Instance {instance_arn} has no access control attribute configuration"
            )
        access_control_attributes = instance_access_control_attribute_configuration.get(
            "AccessControlAttributes", []
        )
        instance.access_control_attribute_config.access_control_attributes = (
            access_control_attributes
        )

    def delete_instance_access_control_attribute_configuration(
        self, instance_arn: str
    ) -> None:
        instance = self._find_instance(instance_arn)
        if instance.access_control_attribute_config is None:
            raise ResourceNotFoundException(
                f"Instance {instance_arn} has no access control attribute configuration"
            )
        instance.access_control_attribute_config = None

    # --- Account assignment status lists ---

    @paginate(pagination_model=PAGINATION_MODEL)
    def list_account_assignment_creation_status(
        self,
        instance_arn: str,
        filter_: Optional[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        results = []
        for assignment in self.account_assignments:
            if assignment.instance_arn == instance_arn:
                results.append(
                    {
                        "RequestId": assignment.request_id,
                        "Status": "SUCCEEDED",
                        "CreatedDate": assignment.created_date,
                    }
                )
        return results

    @paginate(pagination_model=PAGINATION_MODEL)
    def list_account_assignment_deletion_status(
        self,
        instance_arn: str,
        filter_: Optional[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        results = []
        for assignment in self.deleted_account_assignments:
            if assignment.instance_arn == instance_arn:
                results.append(
                    {
                        "RequestId": assignment.request_id,
                        "Status": "SUCCEEDED",
                        "CreatedDate": assignment.created_date,
                    }
                )
        return results

    @paginate(pagination_model=PAGINATION_MODEL)
    def list_permission_set_provisioning_status(
        self,
        instance_arn: str,
        filter_: Optional[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        instance = self._find_instance(instance_arn)
        results = []
        for ps in instance.provisioned_permission_sets:
            results.append(
                {
                    "RequestId": str(random.uuid4()),
                    "Status": "SUCCEEDED",
                    "PermissionSetArn": ps.permission_set_arn,
                    "CreatedDate": ps.created_date,
                }
            )
        return results

    # --- Applications ---

    def create_application(
        self,
        application_provider_arn: str,
        instance_arn: str,
        name: str,
        description: Optional[str],
        portal_options: Optional[dict[str, Any]],
        status: str,
        tags: list[dict[str, str]],
        client_token: Optional[str],
    ) -> Application:
        application = Application(
            application_provider_arn=application_provider_arn,
            instance_arn=instance_arn,
            name=name,
            description=description,
            portal_options=portal_options,
            status=status or "ENABLED",
            tags=tags or [],
            client_token=client_token,
            region=self.region_name,
            account_id=self.account_id,
        )
        self.applications.append(application)
        return application

    def delete_application(self, application_arn: str) -> None:
        application = self._find_application(application_arn)
        self.applications.remove(application)

    def describe_application(self, application_arn: str) -> Application:
        return self._find_application(application_arn)

    def update_application(
        self,
        application_arn: str,
        description: Optional[str],
        name: Optional[str],
        portal_options: Optional[dict[str, Any]],
        status: Optional[str],
    ) -> None:
        application = self._find_application(application_arn)
        if description is not None:
            application.description = description
        if name is not None:
            application.name = name
        if portal_options is not None:
            application.portal_options = portal_options
        if status is not None:
            application.status = status

    @paginate(pagination_model=PAGINATION_MODEL)
    def list_applications(
        self,
        instance_arn: str,
        filter_: Optional[dict[str, Any]],
    ) -> list[Application]:
        apps = [a for a in self.applications if a.instance_arn == instance_arn]
        if filter_:
            app_provider_arn = filter_.get("ApplicationProviderArn")
            if app_provider_arn:
                apps = [
                    a for a in apps if a.application_provider_arn == app_provider_arn
                ]
        return apps

    def _find_application(self, application_arn: str) -> Application:
        for app in self.applications:
            if app.application_arn == application_arn:
                return app
        raise ResourceNotFoundException(f"Application {application_arn} not found")

    # --- Application Access Scopes ---

    def put_application_access_scope(
        self,
        application_arn: str,
        scope: str,
        authorized_targets: Optional[list[str]],
    ) -> None:
        application = self._find_application(application_arn)
        application.access_scopes[scope] = {
            "Scope": scope,
            "AuthorizedTargets": authorized_targets or [],
        }

    def get_application_access_scope(
        self, application_arn: str, scope: str
    ) -> dict[str, Any]:
        application = self._find_application(application_arn)
        if scope not in application.access_scopes:
            raise ResourceNotFoundException(
                f"Application {application_arn} has no access scope {scope}"
            )
        return application.access_scopes[scope]

    def delete_application_access_scope(
        self, application_arn: str, scope: str
    ) -> None:
        application = self._find_application(application_arn)
        if scope not in application.access_scopes:
            raise ResourceNotFoundException(
                f"Application {application_arn} has no access scope {scope}"
            )
        del application.access_scopes[scope]

    @paginate(pagination_model=PAGINATION_MODEL)
    def list_application_access_scopes(
        self, application_arn: str
    ) -> list[dict[str, Any]]:
        application = self._find_application(application_arn)
        return list(application.access_scopes.values())

    # --- Application Assignments ---

    def create_application_assignment(
        self,
        application_arn: str,
        principal_type: str,
        principal_id: str,
    ) -> None:
        application = self._find_application(application_arn)
        # Check for duplicate
        for assignment in application.assignments:
            if (
                assignment.principal_type == principal_type
                and assignment.principal_id == principal_id
            ):
                raise ConflictException(
                    f"Application {application_arn} already has assignment for {principal_type}/{principal_id}"
                )
        application.assignments.append(
            ApplicationAssignment(application_arn, principal_type, principal_id)
        )

    def delete_application_assignment(
        self,
        application_arn: str,
        principal_type: str,
        principal_id: str,
    ) -> None:
        application = self._find_application(application_arn)
        for assignment in application.assignments:
            if (
                assignment.principal_type == principal_type
                and assignment.principal_id == principal_id
            ):
                application.assignments.remove(assignment)
                return
        raise ResourceNotFoundException(
            f"Application {application_arn} has no assignment for {principal_type}/{principal_id}"
        )

    def describe_application_assignment(
        self,
        application_arn: str,
        principal_type: str,
        principal_id: str,
    ) -> ApplicationAssignment:
        application = self._find_application(application_arn)
        for assignment in application.assignments:
            if (
                assignment.principal_type == principal_type
                and assignment.principal_id == principal_id
            ):
                return assignment
        raise ResourceNotFoundException(
            f"Application {application_arn} has no assignment for {principal_type}/{principal_id}"
        )

    @paginate(pagination_model=PAGINATION_MODEL)
    def list_application_assignments(
        self, application_arn: str
    ) -> list[ApplicationAssignment]:
        application = self._find_application(application_arn)
        return application.assignments

    @paginate(pagination_model=PAGINATION_MODEL)
    def list_application_assignments_for_principal(
        self,
        instance_arn: str,
        principal_type: str,
        principal_id: str,
        filter_: Optional[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        results = []
        for application in self.applications:
            if application.instance_arn != instance_arn:
                continue
            for assignment in application.assignments:
                if (
                    assignment.principal_type == principal_type
                    and assignment.principal_id == principal_id
                ):
                    results.append(
                        {
                            "ApplicationArn": application.application_arn,
                            "PrincipalType": assignment.principal_type,
                            "PrincipalId": assignment.principal_id,
                        }
                    )
        return results

    # --- Application Assignment Configuration ---

    def put_application_assignment_configuration(
        self,
        application_arn: str,
        assignment_required: bool,
    ) -> None:
        application = self._find_application(application_arn)
        application.assignment_required = assignment_required

    def get_application_assignment_configuration(
        self, application_arn: str
    ) -> dict[str, Any]:
        application = self._find_application(application_arn)
        return {"AssignmentRequired": application.assignment_required}

    # --- Application Authentication Methods ---

    def put_application_authentication_method(
        self,
        application_arn: str,
        authentication_method_type: str,
        authentication_method: dict[str, Any],
    ) -> None:
        application = self._find_application(application_arn)
        application.authentication_methods[authentication_method_type] = {
            "AuthenticationMethodType": authentication_method_type,
            "AuthenticationMethod": authentication_method,
        }

    def get_application_authentication_method(
        self,
        application_arn: str,
        authentication_method_type: str,
    ) -> dict[str, Any]:
        application = self._find_application(application_arn)
        if authentication_method_type not in application.authentication_methods:
            raise ResourceNotFoundException(
                f"Application {application_arn} has no authentication method {authentication_method_type}"
            )
        return application.authentication_methods[authentication_method_type]

    def delete_application_authentication_method(
        self,
        application_arn: str,
        authentication_method_type: str,
    ) -> None:
        application = self._find_application(application_arn)
        if authentication_method_type not in application.authentication_methods:
            raise ResourceNotFoundException(
                f"Application {application_arn} has no authentication method {authentication_method_type}"
            )
        del application.authentication_methods[authentication_method_type]

    @paginate(pagination_model=PAGINATION_MODEL)
    def list_application_authentication_methods(
        self, application_arn: str
    ) -> list[dict[str, Any]]:
        application = self._find_application(application_arn)
        return list(application.authentication_methods.values())

    # --- Application Grants ---

    def put_application_grant(
        self,
        application_arn: str,
        grant_type: str,
        grant: dict[str, Any],
    ) -> None:
        application = self._find_application(application_arn)
        application.grants[grant_type] = {
            "GrantType": grant_type,
            "Grant": grant,
        }

    def get_application_grant(
        self,
        application_arn: str,
        grant_type: str,
    ) -> dict[str, Any]:
        application = self._find_application(application_arn)
        if grant_type not in application.grants:
            raise ResourceNotFoundException(
                f"Application {application_arn} has no grant {grant_type}"
            )
        return application.grants[grant_type]

    def delete_application_grant(
        self,
        application_arn: str,
        grant_type: str,
    ) -> None:
        application = self._find_application(application_arn)
        if grant_type not in application.grants:
            raise ResourceNotFoundException(
                f"Application {application_arn} has no grant {grant_type}"
            )
        del application.grants[grant_type]

    @paginate(pagination_model=PAGINATION_MODEL)
    def list_application_grants(self, application_arn: str) -> list[dict[str, Any]]:
        application = self._find_application(application_arn)
        return list(application.grants.values())

    # --- Application Session Configuration ---

    def put_application_session_configuration(
        self,
        application_arn: str,
        session_configuration: dict[str, Any],
    ) -> None:
        application = self._find_application(application_arn)
        application.session_configuration = session_configuration

    def get_application_session_configuration(
        self, application_arn: str
    ) -> dict[str, Any]:
        application = self._find_application(application_arn)
        if application.session_configuration is None:
            raise ResourceNotFoundException(
                f"Application {application_arn} has no session configuration"
            )
        return application.session_configuration

    # --- Trusted Token Issuers ---

    def create_trusted_token_issuer(
        self,
        instance_arn: str,
        name: str,
        trusted_token_issuer_type: str,
        trusted_token_issuer_configuration: dict[str, Any],
        tags: list[dict[str, str]],
        client_token: Optional[str],
    ) -> TrustedTokenIssuer:
        tti = TrustedTokenIssuer(
            name=name,
            trusted_token_issuer_type=trusted_token_issuer_type,
            trusted_token_issuer_configuration=trusted_token_issuer_configuration,
            instance_arn=instance_arn,
            tags=tags or [],
            region=self.region_name,
            account_id=self.account_id,
            client_token=client_token,
        )
        self.trusted_token_issuers.append(tti)
        return tti

    def delete_trusted_token_issuer(self, trusted_token_issuer_arn: str) -> None:
        tti = self._find_trusted_token_issuer(trusted_token_issuer_arn)
        self.trusted_token_issuers.remove(tti)

    def describe_trusted_token_issuer(
        self, trusted_token_issuer_arn: str
    ) -> TrustedTokenIssuer:
        return self._find_trusted_token_issuer(trusted_token_issuer_arn)

    def update_trusted_token_issuer(
        self,
        trusted_token_issuer_arn: str,
        name: Optional[str],
        trusted_token_issuer_configuration: Optional[dict[str, Any]],
    ) -> None:
        tti = self._find_trusted_token_issuer(trusted_token_issuer_arn)
        if name is not None:
            tti.name = name
        if trusted_token_issuer_configuration is not None:
            tti.trusted_token_issuer_configuration = trusted_token_issuer_configuration

    @paginate(pagination_model=PAGINATION_MODEL)
    def list_trusted_token_issuers(
        self, instance_arn: str
    ) -> list[TrustedTokenIssuer]:
        return [
            tti
            for tti in self.trusted_token_issuers
            if tti.instance_arn == instance_arn
        ]

    def _find_trusted_token_issuer(
        self, trusted_token_issuer_arn: str
    ) -> TrustedTokenIssuer:
        for tti in self.trusted_token_issuers:
            if tti.trusted_token_issuer_arn == trusted_token_issuer_arn:
                return tti
        raise ResourceNotFoundException(
            f"TrustedTokenIssuer {trusted_token_issuer_arn} not found"
        )

    # --- Application Providers (static/read-only) ---

    @paginate(pagination_model=PAGINATION_MODEL)
    def list_application_providers(self) -> list[dict[str, Any]]:
        # Return a minimal set of well-known application providers
        return [
            {
                "ApplicationProviderArn": "arn:aws:sso::aws:applicationProvider/custom",
                "DisplayData": {
                    "Description": "Custom SAML 2.0 Application",
                    "DisplayName": "Custom SAML 2.0 Application",
                },
                "FederationProtocol": "SAML",
                "ResourceServerConfig": {},
            }
        ]

    def describe_application_provider(
        self, application_provider_arn: str
    ) -> dict[str, Any]:
        providers = self.list_application_providers()
        for provider in providers[0]:  # list_application_providers returns (items, token)
            if provider.get("ApplicationProviderArn") == application_provider_arn:
                return provider
        raise ResourceNotFoundException(
            f"ApplicationProvider {application_provider_arn} not found"
        )


ssoadmin_backends = BackendDict(SSOAdminBackend, "sso-admin")
