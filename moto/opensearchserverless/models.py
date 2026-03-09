"""OpenSearchServiceServerlessBackend class with methods for supported APIs."""

import json
from typing import Any

from moto.core.base_backend import BackendDict, BaseBackend
from moto.core.common_models import BaseModel
from moto.core.utils import unix_time
from moto.moto_api._internal import mock_random
from moto.utilities.tagging_service import TaggingService

from .exceptions import (
    ConflictException,
    ResourceNotFoundException,
    ValidationException,
)


class SecurityPolicy(BaseModel):
    def __init__(
        self,
        client_token: str,
        description: str,
        name: str,
        policy: str,
        type: str,
    ):
        self.client_token = client_token
        self.description = description
        self.name = name
        self.type = type
        self.created_date = int(unix_time() * 1000)
        # update policy # current date default
        self.last_modified_date = int(unix_time() * 1000)
        self.policy = json.loads(policy)
        self.policy_version = mock_random.get_random_string(20)
        if type == "encryption":
            self.resources = [
                res for rule in self.policy["Rules"] for res in rule["Resource"]
            ]
        else:
            self.resources = [
                res
                for p in self.policy
                for rule in p["Rules"]
                for res in rule["Resource"]
            ]

    def to_dict(self) -> dict[str, Any]:
        dct = {
            "createdDate": self.created_date,
            "description": self.description,
            "lastModifiedDate": self.last_modified_date,
            "name": self.name,
            "policy": self.policy,
            "policyVersion": self.policy_version,
            "type": self.type,
        }
        return {k: v for k, v in dct.items() if v}

    def to_dict_list(self) -> dict[str, Any]:
        dct = self.to_dict()
        dct.pop("policy")
        return {k: v for k, v in dct.items() if v}


class Collection(BaseModel):
    def __init__(
        self,
        client_token: str,
        description: str,
        name: str,
        standby_replicas: str,
        tags: list[dict[str, str]],
        type: str,
        policy: Any,
        region: str,
        account_id: str,
    ):
        self.client_token = client_token
        self.description = description
        self.name = name
        self.standby_replicas = standby_replicas
        self.tags = tags
        self.type = type
        self.id = mock_random.get_random_string(length=20, lower_case=True)
        self.arn = f"arn:aws:aoss:{region}:{account_id}:collection/{self.id}"
        self.created_date = int(unix_time() * 1000)
        self.kms_key_arn = policy.get("KmsARN", "")
        self.last_modified_date = int(unix_time() * 1000)
        self.status = "ACTIVE"
        self.collection_endpoint = f"https://{self.id}.{region}.aoss.amazonaws.com"
        self.dashboard_endpoint = (
            f"https://{self.id}.{region}.aoss.amazonaws.com/_dashboards"
        )

    def to_dict(self) -> dict[str, Any]:
        dct = {
            "arn": self.arn,
            "createdDate": self.created_date,
            "description": self.description,
            "id": self.id,
            "kmsKeyArn": self.kms_key_arn,
            "lastModifiedDate": self.last_modified_date,
            "name": self.name,
            "standbyReplicas": self.standby_replicas,
            "status": self.status,
            "type": self.type,
        }
        return {k: v for k, v in dct.items() if v}

    def to_dict_list(self) -> dict[str, Any]:
        dct = {"arn": self.arn, "id": self.id, "name": self.name, "status": self.status}
        return {k: v for k, v in dct.items() if v}

    def to_dict_batch(self) -> dict[str, Any]:
        dct = self.to_dict()
        dct_options = {
            "collectionEndpoint": self.collection_endpoint,
            "dashboardEndpoint": self.dashboard_endpoint,
        }
        for key, value in dct_options.items():
            if value is not None:
                dct[key] = value
        return dct


class AccessPolicy(BaseModel):
    def __init__(self, description: str, name: str, policy: str, type: str):
        self.description = description
        self.name = name
        self.type = type
        self.created_date = int(unix_time() * 1000)
        self.last_modified_date = int(unix_time() * 1000)
        self.policy = json.loads(policy)
        self.policy_version = mock_random.get_random_string(20)

    def to_dict(self) -> dict[str, Any]:
        return {
            "createdDate": self.created_date,
            "description": self.description,
            "lastModifiedDate": self.last_modified_date,
            "name": self.name,
            "policy": self.policy,
            "policyVersion": self.policy_version,
            "type": self.type,
        }

    def to_dict_list(self) -> dict[str, Any]:
        d = self.to_dict()
        d.pop("policy", None)
        return d


class LifecyclePolicy(BaseModel):
    def __init__(self, description: str, name: str, policy: str, type: str):
        self.description = description
        self.name = name
        self.type = type
        self.created_date = int(unix_time() * 1000)
        self.last_modified_date = int(unix_time() * 1000)
        self.policy = json.loads(policy)
        self.policy_version = mock_random.get_random_string(20)

    def to_dict(self) -> dict[str, Any]:
        return {
            "createdDate": self.created_date,
            "description": self.description,
            "lastModifiedDate": self.last_modified_date,
            "name": self.name,
            "policy": self.policy,
            "policyVersion": self.policy_version,
            "type": self.type,
        }

    def to_dict_list(self) -> dict[str, Any]:
        d = self.to_dict()
        d.pop("policy", None)
        return d


class SecurityConfig(BaseModel):
    def __init__(
        self,
        description: str,
        name: str,
        saml_options: dict[str, Any] | None,
        type: str,
        region: str,
        account_id: str,
    ):
        self.description = description
        self.name = name
        self.type = type
        self.saml_options = saml_options or {}
        self.id = mock_random.get_random_string(20, lower_case=True)
        self.config_version = mock_random.get_random_string(20)
        self.created_date = int(unix_time() * 1000)
        self.last_modified_date = int(unix_time() * 1000)

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {
            "configVersion": self.config_version,
            "createdDate": self.created_date,
            "description": self.description,
            "id": self.id,
            "lastModifiedDate": self.last_modified_date,
            "type": self.type,
        }
        if self.saml_options:
            d["samlOptions"] = self.saml_options
        return d

    def to_dict_list(self) -> dict[str, Any]:
        return {
            "configVersion": self.config_version,
            "createdDate": self.created_date,
            "description": self.description,
            "id": self.id,
            "lastModifiedDate": self.last_modified_date,
            "type": self.type,
        }


class OSEndpoint(BaseModel):
    def __init__(
        self,
        client_token: str,
        name: str,
        security_group_ids: list[str],
        subnet_ids: list[str],
        vpc_id: str,
    ):
        self.client_token = client_token
        self.name = name
        self.security_group_ids = security_group_ids
        self.subnet_ids = subnet_ids
        self.vpc_id = vpc_id
        self.id = f"vpce-0{mock_random.get_random_string(length=16, lower_case=True)}"
        self.status = "ACTIVE"

    def to_dict(self) -> dict[str, Any]:
        dct = {"id": self.id, "name": self.name, "status": self.status}
        return {k: v for k, v in dct.items() if v}


class OpenSearchServiceServerlessBackend(BaseBackend):
    """Implementation of OpenSearchServiceServerless APIs."""

    def __init__(self, region_name: str, account_id: str):
        super().__init__(region_name, account_id)

        self.collections: dict[str, Collection] = {}
        self.security_policies: dict[str, SecurityPolicy] = {}
        self.access_policies: dict[str, AccessPolicy] = {}
        self.lifecycle_policies: dict[str, LifecyclePolicy] = {}
        self.security_configs: dict[str, SecurityConfig] = {}
        self.os_endpoints: dict[str, OSEndpoint] = {}
        self.account_settings: dict[str, Any] = {}
        self.tagger = TaggingService(
            tag_name="tags", key_name="key", value_name="value"
        )

    def create_security_policy(
        self, client_token: str, description: str, name: str, policy: str, type: str
    ) -> SecurityPolicy:
        if not client_token:
            client_token = mock_random.get_random_string(10)

        if (name, type) in [
            (sp.name, sp.type) for sp in list(self.security_policies.values())
        ]:
            raise ConflictException(
                msg=f"Policy with name {name} and type {type} already exists"
            )
        if type not in ["encryption", "network"]:
            raise ValidationException(
                msg=f"1 validation error detected: Value '{type}' at 'type' failed to satisfy constraint: Member must satisfy enum value set: [encryption, network]"
            )

        security_policy = SecurityPolicy(
            client_token=client_token,
            description=description,
            name=name,
            policy=policy,
            type=type,
        )
        self.security_policies[security_policy.client_token] = security_policy
        return security_policy

    def get_security_policy(self, name: str, type: str) -> SecurityPolicy:
        for sp in list(self.security_policies.values()):
            if sp.name == name and sp.type == type:
                return sp
        raise ResourceNotFoundException(
            msg=f"Policy with name {name} and type {type} is not found"
        )

    def list_security_policies(
        self, resource: list[str], type: str
    ) -> list[SecurityPolicy]:
        """
        Pagination is not yet implemented
        """
        security_policy_summaries = []
        if resource:
            for res in resource:
                security_policy_summaries.extend(
                    [
                        sp
                        for sp in list(self.security_policies.values())
                        if res in sp.resources and type == sp.type
                    ]
                )
        else:
            security_policy_summaries = [
                sp for sp in list(self.security_policies.values()) if sp.type == type
            ]
        return security_policy_summaries

    def update_security_policy(
        self,
        client_token: str,
        description: str,
        name: str,
        policy: str,
        policy_version: str,
        type: str,
    ) -> SecurityPolicy:
        if not client_token:
            client_token = mock_random.get_random_string(10)

        for sp in list(self.security_policies.values()):
            if sp.name == name and sp.type == type:
                if sp.policy_version == policy_version:
                    last_modified_date = sp.last_modified_date
                    if sp.policy != json.loads(policy):
                        last_modified_date = int(unix_time() * 1000)
                        # Updating policy version
                        policy_version = mock_random.get_random_string(20)

                    sp.client_token = client_token
                    sp.description = description
                    sp.name = name
                    sp.policy = json.loads(policy)
                    sp.last_modified_date = last_modified_date
                    sp.policy_version = policy_version
                    return sp
                else:
                    raise ValidationException(
                        msg="Policy version specified in the request refers to an older version and policy has since changed"
                    )

        raise ResourceNotFoundException(
            msg=f"Policy with name {name} and type {type} is not found"
        )

    def create_collection(
        self,
        client_token: str,
        description: str,
        name: str,
        standby_replicas: str,
        tags: list[dict[str, str]],
        type: str,
    ) -> Collection:
        policy = ""
        if not client_token:
            client_token = mock_random.get_random_string(10)

        import fnmatch

        for sp in list(self.security_policies.values()):
            if sp.type != "encryption":
                continue
            for res in sp.resources:
                if fnmatch.fnmatch(f"collection/{name}", res):
                    policy = sp.policy
                    break
        if not policy:
            raise ValidationException(
                msg=f"No matching security policy of encryption type found for collection name: {name}. Please create security policy of encryption type for this collection."
            )

        collection = Collection(
            client_token=client_token,
            description=description,
            name=name,
            standby_replicas=standby_replicas,
            tags=tags,
            type=type,
            policy=policy,
            region=self.region_name,
            account_id=self.account_id,
        )
        self.collections[collection.id] = collection
        self.tag_resource(collection.arn, tags)
        return collection

    def list_collections(self, collection_filters: dict[str, str]) -> list[Collection]:
        """
        Pagination is not yet implemented
        """
        collection_summaries = []
        if (collection_filters) and ("name" in collection_filters):
            collection_summaries = [
                collection
                for collection in list(self.collections.values())
                if collection.name == collection_filters["name"]
            ]
        else:
            collection_summaries = list(self.collections.values())
        return collection_summaries

    def create_vpc_endpoint(
        self,
        client_token: str,
        name: str,
        security_group_ids: list[str],
        subnet_ids: list[str],
        vpc_id: str,
    ) -> OSEndpoint:
        if not client_token:
            client_token = mock_random.get_random_string(10)

        # Only 1 endpoint should exists under each VPC
        if vpc_id in [ose.vpc_id for ose in list(self.os_endpoints.values())]:
            raise ConflictException(
                msg=f"Failed to create a VpcEndpoint {name} for AccountId {self.account_id} :: There is already a VpcEndpoint exist under VpcId {vpc_id}"
            )

        os_endpoint = OSEndpoint(
            client_token=client_token,
            name=name,
            security_group_ids=security_group_ids,
            subnet_ids=subnet_ids,
            vpc_id=vpc_id,
        )
        self.os_endpoints[os_endpoint.client_token] = os_endpoint

        return os_endpoint

    def delete_collection(self, client_token: str, id: str) -> Collection:
        if not client_token:
            client_token = mock_random.get_random_string(10)

        if id in self.collections:
            self.collections[id].status = "DELETING"
            return self.collections.pop(id)
        raise ResourceNotFoundException(f"Collection with ID {id} cannot be found.")

    def tag_resource(self, resource_arn: str, tags: list[dict[str, str]]) -> None:
        self.tagger.tag_resource(resource_arn, tags)

    def untag_resource(self, resource_arn: str, tag_keys: list[str]) -> None:
        self.tagger.untag_resource_using_names(resource_arn, tag_keys)

    def list_tags_for_resource(self, resource_arn: str) -> list[dict[str, str]]:
        return self.tagger.list_tags_for_resource(resource_arn)["tags"]

    def batch_get_collection(
        self, ids: list[str], names: list[str]
    ) -> tuple[list[Any], list[dict[str, str]]]:
        collection_details = []
        collection_error_details = []
        collection_error_detail = {
            "errorCode": "NOT_FOUND",
            "errorMessage": "The specified Collection is not found.",
        }
        if ids and names:
            raise ValidationException(
                msg="You need to provide IDs or names. You can't provide both IDs and names in the same request"
            )
        if ids:
            for i in ids:
                if i in self.collections:
                    collection_details.append(self.collections[i].to_dict_batch())
                else:
                    collection_error_detail["id"] = i
                    collection_error_details.append(collection_error_detail)

        if names:
            for n in names:
                for collection in self.collections.values():
                    if collection.name == n:
                        collection_details.append(collection.to_dict_batch())
                    else:
                        collection_error_detail["name"] = n
                        collection_error_details.append(collection_error_detail)
        return collection_details, collection_error_details

    def update_collection(
        self, id: str, description: str | None
    ) -> Collection:
        if id not in self.collections:
            raise ResourceNotFoundException(f"Collection with ID {id} cannot be found.")
        collection = self.collections[id]
        if description is not None:
            collection.description = description
        collection.last_modified_date = int(unix_time() * 1000)
        return collection

    def delete_security_policy(self, name: str, type: str) -> None:
        for key, sp in list(self.security_policies.items()):
            if sp.name == name and sp.type == type:
                del self.security_policies[key]
                return
        raise ResourceNotFoundException(
            msg=f"Policy with name {name} and type {type} is not found"
        )

    # Access Policy operations
    def create_access_policy(
        self, description: str, name: str, policy: str, type: str
    ) -> AccessPolicy:
        key = (name, type)
        for ap in self.access_policies.values():
            if (ap.name, ap.type) == key:
                raise ConflictException(
                    msg=f"Policy with name {name} and type {type} already exists"
                )
        ap = AccessPolicy(description=description, name=name, policy=policy, type=type)
        self.access_policies[f"{name}:{type}"] = ap
        return ap

    def get_access_policy(self, name: str, type: str) -> AccessPolicy:
        key = f"{name}:{type}"
        if key in self.access_policies:
            return self.access_policies[key]
        raise ResourceNotFoundException(
            msg=f"Policy with name {name} and type {type} is not found"
        )

    def list_access_policies(self, type: str) -> list[AccessPolicy]:
        return [ap for ap in self.access_policies.values() if ap.type == type]

    def update_access_policy(
        self, name: str, type: str, description: str | None, policy: str | None, policy_version: str | None
    ) -> AccessPolicy:
        key = f"{name}:{type}"
        if key not in self.access_policies:
            raise ResourceNotFoundException(
                msg=f"Policy with name {name} and type {type} is not found"
            )
        ap = self.access_policies[key]
        if description is not None:
            ap.description = description
        if policy is not None:
            ap.policy = json.loads(policy)
            ap.policy_version = mock_random.get_random_string(20)
        ap.last_modified_date = int(unix_time() * 1000)
        return ap

    def delete_access_policy(self, name: str, type: str) -> None:
        key = f"{name}:{type}"
        if key not in self.access_policies:
            raise ResourceNotFoundException(
                msg=f"Policy with name {name} and type {type} is not found"
            )
        del self.access_policies[key]

    # Lifecycle Policy operations
    def create_lifecycle_policy(
        self, description: str, name: str, policy: str, type: str
    ) -> LifecyclePolicy:
        key = f"{name}:{type}"
        if key in self.lifecycle_policies:
            raise ConflictException(
                msg=f"Policy with name {name} and type {type} already exists"
            )
        lp = LifecyclePolicy(description=description, name=name, policy=policy, type=type)
        self.lifecycle_policies[key] = lp
        return lp

    def get_lifecycle_policy(self, name: str, type: str) -> LifecyclePolicy:
        key = f"{name}:{type}"
        if key in self.lifecycle_policies:
            return self.lifecycle_policies[key]
        raise ResourceNotFoundException(
            msg=f"Policy with name {name} and type {type} is not found"
        )

    def list_lifecycle_policies(self, type: str) -> list[LifecyclePolicy]:
        return [lp for lp in self.lifecycle_policies.values() if lp.type == type]

    def update_lifecycle_policy(
        self, name: str, type: str, description: str | None, policy: str | None, policy_version: str | None
    ) -> LifecyclePolicy:
        key = f"{name}:{type}"
        if key not in self.lifecycle_policies:
            raise ResourceNotFoundException(
                msg=f"Policy with name {name} and type {type} is not found"
            )
        lp = self.lifecycle_policies[key]
        if description is not None:
            lp.description = description
        if policy is not None:
            lp.policy = json.loads(policy)
            lp.policy_version = mock_random.get_random_string(20)
        lp.last_modified_date = int(unix_time() * 1000)
        return lp

    def delete_lifecycle_policy(self, name: str, type: str) -> None:
        key = f"{name}:{type}"
        if key not in self.lifecycle_policies:
            raise ResourceNotFoundException(
                msg=f"Policy with name {name} and type {type} is not found"
            )
        del self.lifecycle_policies[key]

    def batch_get_lifecycle_policy(
        self, identifiers: list[dict[str, str]]
    ) -> tuple[list[dict[str, Any]], list[dict[str, str]]]:
        details = []
        errors = []
        for ident in identifiers:
            name = ident.get("name", "")
            type_ = ident.get("type", "")
            key = f"{name}:{type_}"
            if key in self.lifecycle_policies:
                details.append(self.lifecycle_policies[key].to_dict())
            else:
                errors.append(
                    {"errorCode": "NOT_FOUND", "errorMessage": f"Policy {name} not found", "name": name, "type": type_}
                )
        return details, errors

    def batch_get_effective_lifecycle_policy(
        self, resource_identifiers: list[dict[str, str]]
    ) -> tuple[list[dict[str, Any]], list[dict[str, str]]]:
        details = []
        errors = []
        for ri in resource_identifiers:
            resource = ri.get("resource", "")
            type_ = ri.get("type", "")
            found = False
            for lp in self.lifecycle_policies.values():
                if lp.type == type_:
                    details.append({
                        "policyName": lp.name,
                        "resource": resource,
                        "resourceType": "collection",
                        "type": type_,
                    })
                    found = True
                    break
            if not found:
                errors.append({"errorCode": "NOT_FOUND", "errorMessage": "No matching policy", "resource": resource, "type": type_})
        return details, errors

    # Security Config operations
    def create_security_config(
        self, description: str, name: str, saml_options: dict[str, Any] | None, type: str
    ) -> SecurityConfig:
        for sc in self.security_configs.values():
            if sc.name == name:
                raise ConflictException(msg=f"Security config with name {name} already exists")
        sc = SecurityConfig(
            description=description, name=name, saml_options=saml_options,
            type=type, region=self.region_name, account_id=self.account_id,
        )
        self.security_configs[sc.id] = sc
        return sc

    def get_security_config(self, id: str) -> SecurityConfig:
        if id in self.security_configs:
            return self.security_configs[id]
        raise ResourceNotFoundException(msg=f"Security config with ID {id} is not found")

    def list_security_configs(self, type: str) -> list[SecurityConfig]:
        return [sc for sc in self.security_configs.values() if sc.type == type]

    def update_security_config(
        self, config_version: str, id: str, description: str | None, saml_options: dict[str, Any] | None
    ) -> SecurityConfig:
        if id not in self.security_configs:
            raise ResourceNotFoundException(msg=f"Security config with ID {id} is not found")
        sc = self.security_configs[id]
        if description is not None:
            sc.description = description
        if saml_options is not None:
            sc.saml_options = saml_options
        sc.config_version = mock_random.get_random_string(20)
        sc.last_modified_date = int(unix_time() * 1000)
        return sc

    def delete_security_config(self, id: str) -> None:
        if id not in self.security_configs:
            raise ResourceNotFoundException(msg=f"Security config with ID {id} is not found")
        del self.security_configs[id]

    # VPC Endpoint operations
    def delete_vpc_endpoint(self, id: str) -> dict[str, Any]:
        for key, ep in list(self.os_endpoints.items()):
            if ep.id == id:
                ep.status = "DELETING"
                del self.os_endpoints[key]
                return ep.to_dict()
        raise ResourceNotFoundException(msg=f"VPC endpoint with ID {id} is not found")

    def list_vpc_endpoints(self) -> list[OSEndpoint]:
        return list(self.os_endpoints.values())

    def update_vpc_endpoint(
        self, id: str, add_security_group_ids: list[str] | None, add_subnet_ids: list[str] | None,
        remove_security_group_ids: list[str] | None, remove_subnet_ids: list[str] | None
    ) -> dict[str, Any]:
        for ep in self.os_endpoints.values():
            if ep.id == id:
                if add_security_group_ids:
                    ep.security_group_ids.extend(add_security_group_ids)
                if remove_security_group_ids:
                    ep.security_group_ids = [sg for sg in ep.security_group_ids if sg not in remove_security_group_ids]
                if add_subnet_ids:
                    ep.subnet_ids.extend(add_subnet_ids)
                if remove_subnet_ids:
                    ep.subnet_ids = [s for s in ep.subnet_ids if s not in remove_subnet_ids]
                return ep.to_dict()
        raise ResourceNotFoundException(msg=f"VPC endpoint with ID {id} is not found")

    def batch_get_vpc_endpoint(self, ids: list[str]) -> tuple[list[dict[str, Any]], list[dict[str, str]]]:
        details = []
        errors = []
        for id in ids:
            found = False
            for ep in self.os_endpoints.values():
                if ep.id == id:
                    details.append({
                        "id": ep.id, "name": ep.name, "status": ep.status,
                        "vpcId": ep.vpc_id, "subnetIds": ep.subnet_ids,
                        "securityGroupIds": ep.security_group_ids,
                    })
                    found = True
                    break
            if not found:
                errors.append({"errorCode": "NOT_FOUND", "errorMessage": f"VPC endpoint {id} not found", "id": id})
        return details, errors

    # Account Settings
    def get_account_settings(self) -> dict[str, Any]:
        return self.account_settings or {"capacityLimits": {"maxIndexingCapacityInOCU": 20, "maxSearchCapacityInOCU": 20}}

    def update_account_settings(self, capacity_limits: dict[str, Any] | None) -> dict[str, Any]:
        if capacity_limits:
            self.account_settings["capacityLimits"] = capacity_limits
        return self.get_account_settings()

    # Policies Stats
    def get_policies_stats(self) -> dict[str, Any]:
        return {
            "AccessPolicyStats": {"DataPolicyCount": len([ap for ap in self.access_policies.values() if ap.type == "data"])},
            "LifecyclePolicyStats": {"RetentionPolicyCount": len(self.lifecycle_policies)},
            "SecurityConfigStats": {"SamlConfigCount": len([sc for sc in self.security_configs.values() if sc.type == "saml"])},
            "SecurityPolicyStats": {
                "EncryptionPolicyCount": len([sp for sp in self.security_policies.values() if sp.type == "encryption"]),
                "NetworkPolicyCount": len([sp for sp in self.security_policies.values() if sp.type == "network"]),
            },
            "TotalPolicyCount": len(self.security_policies) + len(self.access_policies) + len(self.lifecycle_policies),
        }


opensearchserverless_backends = BackendDict(
    OpenSearchServiceServerlessBackend, "opensearchserverless"
)
