import json
import uuid
from collections import defaultdict
from datetime import datetime, timezone
from typing import Any, Optional

from moto.core.base_backend import BackendDict, BaseBackend
from moto.core.common_models import BaseModel
from moto.moto_api._internal import mock_random
from moto.s3 import s3_backends
from moto.s3.exceptions import (
    InvalidPublicAccessBlockConfiguration,
    WrongPublicAccessBlockAccountIdError,
)
from moto.s3.models import PublicAccessBlock, S3Backend
from moto.utilities.paginator import paginate
from moto.utilities.tagging_service import TaggingService
from moto.utilities.utils import PARTITION_NAMES, get_partition

from .exceptions import (
    AccessGrantNotFound,
    AccessGrantsInstanceNotFound,
    AccessGrantsLocationNotFound,
    AccessPointNotFound,
    AccessPointPolicyNotFound,
    InvalidRequestException,
    JobNotFound,
    MultiRegionAccessPointNotFound,
    MultiRegionAccessPointOperationNotFound,
    MultiRegionAccessPointPolicyNotFound,
    NoSuchPublicAccessBlockConfiguration,
    StorageLensConfigurationNotFound,
    StorageLensGroupNotFound,
)

class AccessGrantsInstance(BaseModel):
    def __init__(
        self,
        account_id: str,
        region_name: str,
        identity_center_arn: Optional[str] = None,
    ):
        self.instance_id = mock_random.get_random_hex(16)
        self.instance_arn = f"arn:{get_partition(region_name)}:s3:{region_name}:{account_id}:access-grants/default"
        self.created_at = datetime.now(timezone.utc)
        self.identity_center_arn = identity_center_arn or ""


class AccessGrantsLocation(BaseModel):
    def __init__(
        self,
        account_id: str,
        region_name: str,
        location_scope: str,
        iam_role_arn: str,
    ):
        self.location_id = f"default-{mock_random.get_random_hex(16)}"
        self.location_scope = location_scope
        self.iam_role_arn = iam_role_arn
        self.location_arn = f"arn:{get_partition(region_name)}:s3:{region_name}:{account_id}:access-grants/default/location/{self.location_id}"
        self.created_at = datetime.now(timezone.utc)


class AccessGrant(BaseModel):
    def __init__(
        self,
        account_id: str,
        region_name: str,
        location_id: str,
        grantee: dict[str, Any],
        permission: str,
        location_scope: str,
        application_arn: Optional[str] = None,
    ):
        self.grant_id = mock_random.get_random_hex(16)
        self.grant_arn = f"arn:{get_partition(region_name)}:s3:{region_name}:{account_id}:access-grants/default/grant/{self.grant_id}"
        self.created_at = datetime.now(timezone.utc)
        self.location_id = location_id
        self.grantee = grantee
        self.permission = permission
        self.location_scope = location_scope
        self.application_arn = application_arn or ""


class StorageLensGroup(BaseModel):
    def __init__(
        self,
        account_id: str,
        region_name: str,
        name: str,
        storage_lens_group: dict[str, Any],
        tags: Optional[list[dict[str, str]]] = None,
    ):
        self.name = name
        self.account_id = account_id
        self.region_name = region_name
        self.storage_lens_group = storage_lens_group
        self.tags = tags or []
        self.arn = f"arn:{get_partition(region_name)}:s3:{region_name}:{account_id}:storage-lens-group/{name}"
        self.created_at = datetime.now(timezone.utc)


class OutpostsBucket(BaseModel):
    def __init__(
        self,
        account_id: str,
        region_name: str,
        bucket: str,
        outpost_id: Optional[str] = None,
    ):
        self.bucket = bucket
        self.account_id = account_id
        self.region_name = region_name
        self.outpost_id = outpost_id or "op-default"
        self.creation_date = datetime.now(timezone.utc)

    @property
    def arn(self) -> str:
        # region_name on s3control backend is a partition name ("aws", "aws-cn", etc.)
        # so use us-east-1 as the default region for ARN construction
        region = self.region_name if "-" in self.region_name else "us-east-1"
        partition = get_partition(region)
        account = self.account_id or "123456789012"
        return (
            f"arn:{partition}:s3-outposts:{region}:{account}"
            f":outpost/{self.outpost_id}/bucket/{self.bucket}"
        )


class S3Job(BaseModel):
    def __init__(
        self,
        account_id: str,
        region_name: str,
    ):
        self.job_id = str(uuid.uuid4())
        self.status = "Complete"
        self.created_at = datetime.now(timezone.utc)
        self.account_id = account_id
        self.region_name = region_name
        self.description = ""
        self.operation = {}
        self.priority = 0
        self.progress = {"NumberOfTasksSucceeded": 0, "NumberOfTasksFailed": 0, "TotalNumberOfTasks": 0}
        self.termination_date = None
        self.role_arn = ""
        self.manifest = {}


PAGINATION_MODEL = {
    "list_storage_lens_configurations": {
        "input_token": "next_token",
        "limit_default": 100,
        "unique_attribute": "id",
    },
    "list_access_points": {
        "input_token": "next_token",
        "limit_key": "max_results",
        "limit_default": 1000,
        "unique_attribute": "name",
    },
    "list_multi_region_access_points": {
        "input_token": "next_token",
        "limit_key": "max_results",
        "limit_default": 100,
        "unique_attribute": "name",
    },
    "list_access_grants": {
        "input_token": "next_token",
        "limit_key": "max_results",
        "limit_default": 100,
        "unique_attribute": "grant_id",
    },
    "list_access_grants_instances": {
        "input_token": "next_token",
        "limit_key": "max_results",
        "limit_default": 100,
        "unique_attribute": "instance_id",
    },
    "list_access_grants_locations": {
        "input_token": "next_token",
        "limit_key": "max_results",
        "limit_default": 100,
        "unique_attribute": "location_id",
    },
    "list_jobs": {
        "input_token": "next_token",
        "limit_key": "max_results",
        "limit_default": 1000,
        "unique_attribute": "job_id",
    },
    "list_storage_lens_groups": {
        "input_token": "next_token",
        "limit_default": 100,
        "unique_attribute": "name",
    },
}


class AccessPoint(BaseModel):
    def __init__(
        self,
        account_id: str,
        region_name: str,
        name: str,
        bucket: str,
        vpc_configuration: dict[str, Any],
        public_access_block_configuration: dict[str, Any],
    ):
        self.name = name
        self.alias = f"{name}-{mock_random.get_random_hex(34)}-s3alias"
        self.bucket = bucket
        self.created = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")
        self.arn = f"arn:{get_partition(region_name)}:s3:us-east-1:{account_id}:accesspoint/{name}"
        self.policy: Optional[str] = None
        self.network_origin = "VPC" if vpc_configuration else "Internet"
        self.vpc_id = (vpc_configuration or {}).get("VpcId")
        pubc = public_access_block_configuration or {}
        self.pubc = {
            "BlockPublicAcls": pubc.get("BlockPublicAcls", "true"),
            "IgnorePublicAcls": pubc.get("IgnorePublicAcls", "true"),
            "BlockPublicPolicy": pubc.get("BlockPublicPolicy", "true"),
            "RestrictPublicBuckets": pubc.get("RestrictPublicBuckets", "true"),
        }

    def delete_policy(self) -> None:
        self.policy = None

    def set_policy(self, policy: str) -> None:
        self.policy = policy

    def has_policy(self) -> bool:
        return self.policy is not None


class MultiRegionAccessPoint(BaseModel):
    def __init__(
        self,
        name: str,
        public_access_block: dict[str, Any],
        regions: list[dict[str, str]],
    ):
        self.name = name
        self.alias = f"{name}-{mock_random.get_random_hex(10)}.mrap"
        self.created_at = datetime.now(timezone.utc)
        self.public_access_block = public_access_block or {
            "BlockPublicAcls": True,
            "IgnorePublicAcls": True,
            "BlockPublicPolicy": True,
            "RestrictPublicBuckets": True,
        }
        self.regions = regions
        self.status = "READY"
        self.policy: Optional[str] = None

    def set_policy(self, policy: str) -> None:
        self.policy = policy

    def has_policy(self) -> bool:
        return self.policy is not None

    def to_dict(self) -> dict[str, Any]:
        return {
            "Name": self.name or "",
            "Alias": self.alias,
            "CreatedAt": self.created_at.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
            "PublicAccessBlock": self.public_access_block,
            "Status": self.status,
            "Regions": self.regions,
        }


class MultiRegionAccessPointOperation(BaseModel):
    def __init__(
        self,
        account_id: str,
        operation: str,
        region_name: str,
        name: Optional[str] = None,
        details: Optional[dict[str, Any]] = None,
    ):
        self.request_token_arn = f"arn:aws:s3:{region_name}:{account_id}:async-request/mrap/{operation.lower()}/{uuid.uuid4().hex[:24]}"
        self.request_status = "SUCCEEDED"
        self.name = name
        self.operation = operation
        self.created_at = datetime.now(timezone.utc)
        self.details = details or {}

    def to_dict(self) -> dict[str, Any]:
        response: dict[str, Any] = {
            "RequestTokenARN": self.request_token_arn,
            "RequestStatus": self.request_status,
            "CreationTime": self.created_at.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
            "Operation": self.operation,
        }

        if self.operation == "CreateMultiRegionAccessPoint" and self.details:
            response["RequestParameters"] = {
                "CreateMultiRegionAccessPointRequest": {
                    "Name": self.name or "",
                    "Regions": self.details.get("Regions", []),
                    "PublicAccessBlock": self.details.get("PublicAccessBlock", {}),
                }
            }
            regions_response = [
                {"Name": r.get("Region", ""), "RequestStatus": self.request_status}
                for r in self.details.get("Regions", [])
            ]
            response["ResponseDetails"] = {
                "MultiRegionAccessPointDetails": {
                    "Regions": regions_response,
                }
            }
        elif self.operation == "DeleteMultiRegionAccessPoint":
            response["RequestParameters"] = {
                "DeleteMultiRegionAccessPointRequest": {
                    "Name": self.name or "",
                }
            }
            response["ResponseDetails"] = {
                "MultiRegionAccessPointDetails": {
                    "Regions": [],
                }
            }
        elif self.operation == "PutMultiRegionAccessPointPolicy":
            response["RequestParameters"] = {
                "PutMultiRegionAccessPointPolicyRequest": {
                    "Name": self.name or "",
                    "Policy": self.details.get("Policy", ""),
                }
            }
            response["ResponseDetails"] = {}

        return response


class StorageLensConfiguration(BaseModel):
    def __init__(
        self,
        account_id: str,
        config_id: str,
        storage_lens_configuration: dict[str, Any],
        tags: Optional[dict[str, str]] = None,
    ):
        self.account_id = account_id
        self.config_id = config_id
        self.config = storage_lens_configuration
        self.tags = tags or {}
        self.arn = f"arn:{get_partition('us-east-1')}:s3:us-east-1:{account_id}:storage-lens/{config_id}"


class S3ControlBackend(BaseBackend):
    def __init__(self, region_name: str, account_id: str):
        super().__init__(region_name, account_id)
        self.public_access_block: Optional[PublicAccessBlock] = None
        self.access_points: dict[str, dict[str, AccessPoint]] = defaultdict(dict)
        self.multi_region_access_points: dict[
            str, dict[str, MultiRegionAccessPoint]
        ] = defaultdict(dict)
        self.mrap_operations: dict[str, dict[str, MultiRegionAccessPointOperation]] = (
            defaultdict(dict)
        )
        self.storage_lens_configs: dict[str, StorageLensConfiguration] = {}
        self.tagger = TaggingService()
        self.access_grants_instances: dict[str, AccessGrantsInstance] = {}
        self.access_grants_locations: dict[str, AccessGrantsLocation] = {}
        self.access_grants: dict[str, AccessGrant] = {}
        self.jobs: dict[str, S3Job] = {}
        self.resource_policy: Optional[str] = None
        self.storage_lens_groups: dict[str, StorageLensGroup] = {}
        self.object_lambda_access_points: dict[str, dict[str, AccessPoint]] = defaultdict(dict)
        self.object_lambda_access_point_policies: dict[str, dict[str, str]] = defaultdict(dict)
        self.access_point_scopes: dict[str, dict[str, dict[str, Any]]] = defaultdict(dict)
        self.job_tags: dict[str, list[dict[str, str]]] = {}
        self.outposts_buckets: dict[str, OutpostsBucket] = {}

    def get_public_access_block(self, account_id: str) -> PublicAccessBlock:
        if account_id != self.account_id:
            raise WrongPublicAccessBlockAccountIdError()

        if not self.public_access_block:
            raise NoSuchPublicAccessBlockConfiguration()

        return self.public_access_block

    def delete_public_access_block(self, account_id: str) -> None:
        if account_id != self.account_id:
            raise WrongPublicAccessBlockAccountIdError()

        self.public_access_block = None

    def put_public_access_block(
        self, account_id: str, pub_block_config: dict[str, Any]
    ) -> None:
        if account_id != self.account_id:
            raise WrongPublicAccessBlockAccountIdError()

        if not pub_block_config:
            raise InvalidPublicAccessBlockConfiguration()

        self.public_access_block = PublicAccessBlock(
            pub_block_config.get("BlockPublicAcls"),
            pub_block_config.get("IgnorePublicAcls"),
            pub_block_config.get("BlockPublicPolicy"),
            pub_block_config.get("RestrictPublicBuckets"),
        )

    def create_access_point(
        self,
        account_id: str,
        name: str,
        bucket: str,
        vpc_configuration: dict[str, Any],
        public_access_block_configuration: dict[str, Any],
    ) -> AccessPoint:
        access_point = AccessPoint(
            account_id,
            region_name=self.region_name,
            name=name,
            bucket=bucket,
            vpc_configuration=vpc_configuration,
            public_access_block_configuration=public_access_block_configuration,
        )
        self.access_points[account_id][name] = access_point
        return access_point

    def delete_access_point(self, account_id: str, name: str) -> None:
        self.access_points[account_id].pop(name, None)

    def get_access_point(self, account_id: str, name: str) -> AccessPoint:
        if name not in self.access_points[account_id]:
            raise AccessPointNotFound(name)
        return self.access_points[account_id][name]

    def put_access_point_policy(self, account_id: str, name: str, policy: str) -> None:
        access_point = self.get_access_point(account_id, name)
        access_point.set_policy(policy)

    def get_access_point_policy(self, account_id: str, name: str) -> str:
        access_point = self.get_access_point(account_id, name)
        if access_point.has_policy():
            return access_point.policy  # type: ignore[return-value]
        raise AccessPointPolicyNotFound(name)

    def delete_access_point_policy(self, account_id: str, name: str) -> None:
        access_point = self.get_access_point(account_id, name)
        access_point.delete_policy()

    def get_access_point_policy_status(self, account_id: str, name: str) -> bool:
        self.get_access_point_policy(account_id, name)
        return True

    def create_multi_region_access_point(
        self,
        account_id: str,
        name: str,
        public_access_block: dict[str, Any],
        regions: list[dict[str, str]],
        region_name: str,
    ) -> MultiRegionAccessPointOperation:
        if name in self.multi_region_access_points[account_id]:
            raise InvalidRequestException(
                f"Multi-Region Access Point {name} already exists"
            )

        processed_regions: list[dict[str, str]] = []
        for region_item in regions:
            bucket_name = region_item.get("Bucket", "")
            found_region = "us-east-1"

            found = False
            for account_id_key in s3_backends:
                if found:
                    break
                for region_key, backend in s3_backends[account_id_key].items():
                    if region_key == "aws":
                        continue

                    if bucket_name in backend.buckets:
                        found_region = region_key
                        found = True
                        break

            processed_regions.append({"Bucket": bucket_name, "Region": found_region})

        mrap = MultiRegionAccessPoint(
            name=name,
            public_access_block=public_access_block,
            regions=processed_regions,
        )
        self.multi_region_access_points[account_id][name] = mrap

        operation = MultiRegionAccessPointOperation(
            account_id=account_id,
            operation="CreateMultiRegionAccessPoint",
            region_name=region_name,
            name=name,
            details={
                "Regions": processed_regions,
                "PublicAccessBlock": public_access_block,
            },
        )
        self.mrap_operations[account_id][operation.request_token_arn] = operation

        return operation

    def delete_multi_region_access_point(
        self,
        account_id: str,
        name: str,
        region_name: str,
    ) -> MultiRegionAccessPointOperation:
        if name not in self.multi_region_access_points[account_id]:
            raise MultiRegionAccessPointNotFound(name)

        del self.multi_region_access_points[account_id][name]

        operation = MultiRegionAccessPointOperation(
            account_id=account_id,
            operation="DeleteMultiRegionAccessPoint",
            region_name=region_name,
            name=name,
        )
        self.mrap_operations[account_id][operation.request_token_arn] = operation

        return operation

    def describe_multi_region_access_point_operation(
        self,
        account_id: str,
        request_token_arn: str,
    ) -> MultiRegionAccessPointOperation:
        if request_token_arn not in self.mrap_operations[account_id]:
            raise MultiRegionAccessPointOperationNotFound(request_token_arn)

        return self.mrap_operations[account_id][request_token_arn]

    def get_multi_region_access_point(
        self,
        account_id: str,
        name: str,
    ) -> MultiRegionAccessPoint:
        if name not in self.multi_region_access_points[account_id]:
            raise MultiRegionAccessPointNotFound(name)

        return self.multi_region_access_points[account_id][name]

    def get_multi_region_access_point_policy(
        self,
        account_id: str,
        name: str,
    ) -> str:
        mrap = self.get_multi_region_access_point(account_id, name)
        if not mrap.has_policy():
            raise MultiRegionAccessPointPolicyNotFound(name)
        return mrap.policy  # type: ignore[return-value]

    def _is_policy_public(
        self, policy: str, public_access_block: dict[str, Any]
    ) -> bool:
        block_public = public_access_block.get("BlockPublicPolicy")
        if block_public is True or block_public == "true":
            return False

        policy_no_spaces = policy.replace(" ", "")
        if '"Principal":"*"' in policy_no_spaces:
            return True
        if '"Principal":{"AWS":"*"}' in policy_no_spaces:
            return True

        return False

    def get_multi_region_access_point_policy_status(
        self,
        account_id: str,
        name: str,
    ) -> dict[str, Any]:
        mrap = self.get_multi_region_access_point(account_id, name)
        if not mrap.has_policy():
            raise MultiRegionAccessPointPolicyNotFound(name)
        is_public = self._is_policy_public(mrap.policy, mrap.public_access_block)  # type: ignore[arg-type]
        return {"IsPublic": is_public}

    @paginate(pagination_model=PAGINATION_MODEL)
    def list_multi_region_access_points(
        self,
        account_id: str,
        max_results: Optional[int] = None,
        next_token: Optional[str] = None,
    ) -> list[MultiRegionAccessPoint]:
        return list(self.multi_region_access_points[account_id].values())

    def put_multi_region_access_point_policy(
        self,
        account_id: str,
        name: str,
        policy: str,
        region_name: str,
    ) -> MultiRegionAccessPointOperation:
        mrap = self.get_multi_region_access_point(account_id, name)
        mrap.set_policy(policy)

        operation = MultiRegionAccessPointOperation(
            account_id=account_id,
            operation="PutMultiRegionAccessPointPolicy",
            region_name=region_name,
            name=name,
            details={"Policy": policy},
        )
        self.mrap_operations[account_id][operation.request_token_arn] = operation

        return operation

    def put_storage_lens_configuration(
        self,
        config_id: str,
        account_id: str,
        storage_lens_configuration: dict[str, Any],
        tags: Optional[dict[str, str]] = None,
    ) -> None:
        if account_id != self.account_id:
            raise WrongPublicAccessBlockAccountIdError()

        storage_lens = StorageLensConfiguration(
            account_id=account_id,
            config_id=config_id,
            storage_lens_configuration=storage_lens_configuration,
            tags=tags,
        )
        self.storage_lens_configs[config_id] = storage_lens

    def get_storage_lens_configuration(
        self, config_id: str, account_id: str
    ) -> StorageLensConfiguration:
        if config_id not in self.storage_lens_configs:
            raise StorageLensConfigurationNotFound(config_id)
        storage_lens_configuration = self.storage_lens_configs[config_id]
        return storage_lens_configuration

    def delete_storage_lens_configuration(
        self, config_id: str, account_id: str
    ) -> None:
        if account_id != self.account_id:
            raise WrongPublicAccessBlockAccountIdError()
        if config_id not in self.storage_lens_configs:
            raise StorageLensConfigurationNotFound(config_id)
        del self.storage_lens_configs[config_id]

    @paginate(pagination_model=PAGINATION_MODEL)
    def list_storage_lens_configurations(
        self, account_id: str
    ) -> list[StorageLensConfiguration]:
        storage_lens_configuration_list = list(self.storage_lens_configs.values())
        return storage_lens_configuration_list

    @paginate(pagination_model=PAGINATION_MODEL)
    def list_access_points(
        self,
        account_id: str,
        bucket: Optional[str] = None,
        max_results: Optional[int] = None,
        next_token: Optional[str] = None,
    ) -> list[AccessPoint]:
        account_access_points = self.access_points.get(account_id, {})
        all_access_points = list(account_access_points.values())

        if bucket:
            return [ap for ap in all_access_points if ap.bucket == bucket]
        return all_access_points

    def put_storage_lens_configuration_tagging(
        self, config_id: str, account_id: str, tags: dict[str, str]
    ) -> None:
        if account_id != self.account_id:
            raise WrongPublicAccessBlockAccountIdError()

        if config_id not in self.storage_lens_configs:
            raise AccessPointNotFound(config_id)

        self.storage_lens_configs[config_id].tags = tags

    def get_storage_lens_configuration_tagging(
        self, config_id: str, account_id: str
    ) -> dict[str, str]:
        if account_id != self.account_id:
            raise WrongPublicAccessBlockAccountIdError()
        if config_id not in self.storage_lens_configs:
            raise AccessPointNotFound(config_id)

        return self.storage_lens_configs[config_id].tags

    def list_tags_for_resource(self, resource_arn: str) -> list[dict[str, str]]:
        backend: S3Backend = s3_backends[self.account_id][self.partition]
        return backend.tagger.list_tags_for_resource(resource_arn)["Tags"]

    def tag_resource(self, resource_arn: str, tags: list[dict[str, str]]) -> None:
        backend: S3Backend = s3_backends[self.account_id][self.partition]
        backend.tagger.tag_resource(resource_arn, tags=tags)

    def untag_resource(self, resource_arn: str, tag_keys: list[str]) -> None:
        backend: S3Backend = s3_backends[self.account_id][self.partition]
        backend.tagger.untag_resource_using_names(resource_arn, tag_names=tag_keys)

    # Access Grants Instance operations

    def create_access_grants_instance(
        self,
        account_id: str,
        identity_center_arn: Optional[str] = None,
    ) -> AccessGrantsInstance:
        instance = AccessGrantsInstance(
            account_id=account_id,
            region_name=self.region_name,
            identity_center_arn=identity_center_arn,
        )
        self.access_grants_instances[account_id] = instance
        return instance

    def get_access_grants_instance(
        self,
        account_id: str,
    ) -> AccessGrantsInstance:
        if account_id not in self.access_grants_instances:
            raise AccessGrantsInstanceNotFound()
        return self.access_grants_instances[account_id]

    def get_access_grants_instance_for_prefix(
        self,
        account_id: str,
        s3_prefix: str,
    ) -> AccessGrantsInstance:
        if account_id not in self.access_grants_instances:
            raise AccessGrantsInstanceNotFound()
        return self.access_grants_instances[account_id]

    def get_access_grants_instance_resource_policy(
        self,
        account_id: str,
    ) -> str:
        if account_id not in self.access_grants_instances:
            raise AccessGrantsInstanceNotFound()
        return self.resource_policy or ""

    def put_access_grants_instance_resource_policy(
        self,
        account_id: str,
        policy: str,
    ) -> str:
        if account_id not in self.access_grants_instances:
            raise AccessGrantsInstanceNotFound()
        self.resource_policy = policy
        return policy

    @paginate(pagination_model=PAGINATION_MODEL)
    def list_access_grants_instances(
        self,
        account_id: str,
        max_results: Optional[int] = None,
        next_token: Optional[str] = None,
    ) -> list[AccessGrantsInstance]:
        return list(self.access_grants_instances.values())

    # Access Grants Location operations

    def create_access_grants_location(
        self,
        account_id: str,
        location_scope: str,
        iam_role_arn: str,
    ) -> AccessGrantsLocation:
        location = AccessGrantsLocation(
            account_id=account_id,
            region_name=self.region_name,
            location_scope=location_scope,
            iam_role_arn=iam_role_arn,
        )
        self.access_grants_locations[location.location_id] = location
        return location

    def get_access_grants_location(
        self,
        location_id: str,
    ) -> AccessGrantsLocation:
        if location_id not in self.access_grants_locations:
            raise AccessGrantsLocationNotFound(location_id)
        return self.access_grants_locations[location_id]

    @paginate(pagination_model=PAGINATION_MODEL)
    def list_access_grants_locations(
        self,
        account_id: str,
        max_results: Optional[int] = None,
        next_token: Optional[str] = None,
    ) -> list[AccessGrantsLocation]:
        return list(self.access_grants_locations.values())

    # Access Grant operations

    def create_access_grant(
        self,
        account_id: str,
        location_id: str,
        grantee: dict[str, Any],
        permission: str,
        location_scope: str,
        application_arn: Optional[str] = None,
    ) -> AccessGrant:
        grant = AccessGrant(
            account_id=account_id,
            region_name=self.region_name,
            location_id=location_id,
            grantee=grantee,
            permission=permission,
            location_scope=location_scope,
            application_arn=application_arn,
        )
        self.access_grants[grant.grant_id] = grant
        return grant

    def get_access_grant(
        self,
        grant_id: str,
    ) -> AccessGrant:
        if grant_id not in self.access_grants:
            raise AccessGrantNotFound(grant_id)
        return self.access_grants[grant_id]

    @paginate(pagination_model=PAGINATION_MODEL)
    def list_access_grants(
        self,
        account_id: str,
        max_results: Optional[int] = None,
        next_token: Optional[str] = None,
    ) -> list[AccessGrant]:
        return list(self.access_grants.values())

    # S3 Batch Operations (Jobs)

    def describe_job(
        self,
        account_id: str,
        job_id: str,
    ) -> S3Job:
        if job_id not in self.jobs:
            raise JobNotFound(job_id)
        return self.jobs[job_id]

    @paginate(pagination_model=PAGINATION_MODEL)
    def list_jobs(
        self,
        account_id: str,
        max_results: Optional[int] = None,
        next_token: Optional[str] = None,
    ) -> list[S3Job]:
        return list(self.jobs.values())

    def create_job(
        self,
        account_id: str,
        operation: dict[str, Any],
        manifest: dict[str, Any],
        priority: int,
        role_arn: str,
        description: str = "",
        confirmation_required: bool = False,
    ) -> S3Job:
        job = S3Job(account_id=account_id, region_name=self.region_name)
        job.operation = operation
        job.manifest = manifest
        job.priority = priority
        job.role_arn = role_arn
        job.description = description
        job.status = "Ready" if not confirmation_required else "Suspended"
        self.jobs[job.job_id] = job
        return job

    def update_job_priority(
        self, account_id: str, job_id: str, priority: int
    ) -> S3Job:
        if job_id not in self.jobs:
            raise JobNotFound(job_id)
        self.jobs[job_id].priority = priority
        return self.jobs[job_id]

    def update_job_status(
        self,
        account_id: str,
        job_id: str,
        requested_job_status: str,
        status_update_reason: str = "",
    ) -> S3Job:
        if job_id not in self.jobs:
            raise JobNotFound(job_id)
        self.jobs[job_id].status = requested_job_status
        return self.jobs[job_id]

    def delete_storage_lens_configuration_tagging(
        self, config_id: str, account_id: str
    ) -> None:
        if account_id != self.account_id:
            raise WrongPublicAccessBlockAccountIdError()
        if config_id not in self.storage_lens_configs:
            raise StorageLensConfigurationNotFound(config_id)
        self.storage_lens_configs[config_id].tags = {}

    def get_multi_region_access_point_routes(
        self, account_id: str, mrap: str
    ) -> list[dict[str, Any]]:
        name = mrap.split("/")[-1] if "/" in mrap else mrap
        mrap_obj = self.get_multi_region_access_point(account_id, name)
        routes = []
        for region in mrap_obj.regions:
            routes.append(
                {
                    "Bucket": region.get("Bucket", ""),
                    "Region": region.get("Region", ""),
                    "TrafficDialPercentage": 100,
                }
            )
        return routes

    def submit_multi_region_access_point_routes(
        self,
        account_id: str,
        mrap: str,
        route_updates: list[dict[str, Any]],
    ) -> None:
        name = mrap.split("/")[-1] if "/" in mrap else mrap
        self.get_multi_region_access_point(account_id, name)

    def delete_access_grants_instance(self, account_id: str) -> None:
        if account_id not in self.access_grants_instances:
            raise AccessGrantsInstanceNotFound()
        del self.access_grants_instances[account_id]
        self.access_grants.clear()
        self.access_grants_locations.clear()
        self.resource_policy = None

    def delete_access_grants_instance_resource_policy(
        self, account_id: str
    ) -> None:
        if account_id not in self.access_grants_instances:
            raise AccessGrantsInstanceNotFound()
        self.resource_policy = None

    def delete_access_grants_location(self, location_id: str) -> None:
        if location_id not in self.access_grants_locations:
            raise AccessGrantsLocationNotFound(location_id)
        del self.access_grants_locations[location_id]

    def update_access_grants_location(
        self,
        location_id: str,
        iam_role_arn: str,
        location_scope: Optional[str] = None,
    ) -> AccessGrantsLocation:
        if location_id not in self.access_grants_locations:
            raise AccessGrantsLocationNotFound(location_id)
        loc = self.access_grants_locations[location_id]
        loc.iam_role_arn = iam_role_arn
        if location_scope is not None:
            loc.location_scope = location_scope
        return loc

    def delete_access_grant(self, grant_id: str) -> None:
        if grant_id not in self.access_grants:
            raise AccessGrantNotFound(grant_id)
        del self.access_grants[grant_id]

    # Bucket-level operations (delegating to S3 backend)

    def get_bucket_lifecycle_configuration(
        self,
        account_id: str,
        bucket: str,
    ) -> list[Any]:
        backend: S3Backend = s3_backends[self.account_id][self.partition]
        bucket_obj = backend.get_bucket(bucket)
        if hasattr(bucket_obj, "rules") and bucket_obj.rules:
            return list(bucket_obj.rules)
        return []

    def get_bucket_policy(
        self,
        account_id: str,
        bucket: str,
    ) -> Optional[str]:
        backend: S3Backend = s3_backends[self.account_id][self.partition]
        return backend.get_bucket_policy(bucket)

    def get_bucket_replication(
        self,
        account_id: str,
        bucket: str,
    ) -> Optional[dict[str, Any]]:
        backend: S3Backend = s3_backends[self.account_id][self.partition]
        bucket_obj = backend.get_bucket(bucket)
        if hasattr(bucket_obj, "replication") and bucket_obj.replication:
            return bucket_obj.replication
        return None

    def get_bucket_tagging(
        self,
        account_id: str,
        bucket: str,
    ) -> list[dict[str, str]]:
        backend: S3Backend = s3_backends[self.account_id][self.partition]
        try:
            return backend.get_bucket_tagging(bucket)
        except Exception:
            return []

    def get_bucket_versioning(
        self,
        account_id: str,
        bucket: str,
    ) -> Optional[str]:
        backend: S3Backend = s3_backends[self.account_id][self.partition]
        bucket_obj = backend.get_bucket(bucket)
        if hasattr(bucket_obj, "versioning_status"):
            return bucket_obj.versioning_status
        return None

    def put_bucket_versioning(
        self,
        account_id: str,
        bucket: str,
        status: str,
    ) -> None:
        backend: S3Backend = s3_backends[self.account_id][self.partition]
        backend.put_bucket_versioning(bucket, status)

    def put_bucket_policy(
        self,
        account_id: str,
        bucket: str,
        policy: str,
    ) -> None:
        backend: S3Backend = s3_backends[self.account_id][self.partition]
        backend.put_bucket_policy(bucket, policy)

    def delete_bucket_policy(
        self,
        account_id: str,
        bucket: str,
    ) -> None:
        backend: S3Backend = s3_backends[self.account_id][self.partition]
        backend.delete_bucket_policy(bucket)

    def put_bucket_tagging(
        self,
        account_id: str,
        bucket: str,
        tagging: dict[str, Any],
    ) -> None:
        backend: S3Backend = s3_backends[self.account_id][self.partition]
        backend.put_bucket_tagging(bucket, tagging)

    def delete_bucket_tagging(
        self,
        account_id: str,
        bucket: str,
    ) -> None:
        backend: S3Backend = s3_backends[self.account_id][self.partition]
        backend.delete_bucket_tagging(bucket)

    def put_bucket_lifecycle(
        self,
        account_id: str,
        bucket: str,
        rules: list[dict[str, Any]],
    ) -> None:
        backend: S3Backend = s3_backends[self.account_id][self.partition]
        backend.put_bucket_lifecycle(bucket, rules)

    def delete_bucket_lifecycle(
        self,
        account_id: str,
        bucket: str,
    ) -> None:
        backend: S3Backend = s3_backends[self.account_id][self.partition]
        backend.delete_bucket_lifecycle(bucket)

    def put_bucket_replication(
        self,
        account_id: str,
        bucket: str,
        replication: dict[str, Any],
    ) -> None:
        backend: S3Backend = s3_backends[self.account_id][self.partition]
        bucket_obj = backend.get_bucket(bucket)
        bucket_obj.replication = replication

    def delete_bucket_replication(
        self,
        account_id: str,
        bucket: str,
    ) -> None:
        backend: S3Backend = s3_backends[self.account_id][self.partition]
        bucket_obj = backend.get_bucket(bucket)
        bucket_obj.replication = None

    # Storage Lens Group operations

    def create_storage_lens_group(
        self,
        account_id: str,
        name: str,
        storage_lens_group: dict[str, Any],
        tags: Optional[list[dict[str, str]]] = None,
    ) -> StorageLensGroup:
        group = StorageLensGroup(
            account_id=account_id,
            region_name=self.region_name,
            name=name,
            storage_lens_group=storage_lens_group,
            tags=tags,
        )
        self.storage_lens_groups[name] = group
        return group

    def get_storage_lens_group(
        self,
        name: str,
    ) -> StorageLensGroup:
        if name not in self.storage_lens_groups:
            raise StorageLensGroupNotFound(name)
        return self.storage_lens_groups[name]

    def delete_storage_lens_group(
        self,
        name: str,
    ) -> None:
        if name not in self.storage_lens_groups:
            raise StorageLensGroupNotFound(name)
        del self.storage_lens_groups[name]

    def update_storage_lens_group(
        self,
        name: str,
        storage_lens_group: dict[str, Any],
    ) -> StorageLensGroup:
        if name not in self.storage_lens_groups:
            raise StorageLensGroupNotFound(name)
        group = self.storage_lens_groups[name]
        group.storage_lens_group = storage_lens_group
        return group

    @paginate(pagination_model=PAGINATION_MODEL)
    def list_storage_lens_groups(
        self,
        account_id: str,
        next_token: Optional[str] = None,
    ) -> list[StorageLensGroup]:
        return list(self.storage_lens_groups.values())

    # Object Lambda Access Point operations

    def create_access_point_for_object_lambda(
        self,
        account_id: str,
        name: str,
        configuration: dict[str, Any],
    ) -> AccessPoint:
        access_point = AccessPoint(
            account_id=account_id,
            region_name=self.region_name,
            name=name,
            bucket=configuration.get("SupportingAccessPoint", ""),
            vpc_configuration={},
            public_access_block_configuration={},
        )
        self.object_lambda_access_points[account_id][name] = access_point
        return access_point

    def get_access_point_for_object_lambda(
        self,
        account_id: str,
        name: str,
    ) -> AccessPoint:
        if name not in self.object_lambda_access_points.get(account_id, {}):
            raise AccessPointNotFound(name)
        return self.object_lambda_access_points[account_id][name]

    def delete_access_point_for_object_lambda(
        self,
        account_id: str,
        name: str,
    ) -> None:
        if account_id in self.object_lambda_access_points:
            self.object_lambda_access_points[account_id].pop(name, None)
        self.object_lambda_access_point_policies.get(account_id, {}).pop(name, None)

    def put_access_point_policy_for_object_lambda(
        self,
        account_id: str,
        name: str,
        policy: str,
    ) -> None:
        if name not in self.object_lambda_access_points.get(account_id, {}):
            raise AccessPointNotFound(name)
        self.object_lambda_access_point_policies[account_id][name] = policy

    def delete_access_point_policy_for_object_lambda(
        self,
        account_id: str,
        name: str,
    ) -> None:
        self.object_lambda_access_point_policies.get(account_id, {}).pop(name, None)

    # Access Point Scope operations

    def get_access_point_scope(
        self,
        account_id: str,
        name: str,
    ) -> dict[str, Any]:
        return self.access_point_scopes.get(account_id, {}).get(name, {})

    def put_access_point_scope(
        self,
        account_id: str,
        name: str,
        scope: dict[str, Any],
    ) -> None:
        self.access_point_scopes[account_id][name] = scope

    def delete_access_point_scope(
        self,
        account_id: str,
        name: str,
    ) -> None:
        self.access_point_scopes.get(account_id, {}).pop(name, None)

    # Job Tagging operations

    def get_job_tagging(
        self,
        account_id: str,
        job_id: str,
    ) -> list[dict[str, str]]:
        if job_id not in self.jobs:
            raise JobNotFound(job_id)
        return self.job_tags.get(job_id, [])

    def put_job_tagging(
        self,
        account_id: str,
        job_id: str,
        tags: list[dict[str, str]],
    ) -> None:
        if job_id not in self.jobs:
            raise JobNotFound(job_id)
        self.job_tags[job_id] = tags

    def delete_job_tagging(
        self,
        account_id: str,
        job_id: str,
    ) -> None:
        if job_id not in self.jobs:
            raise JobNotFound(job_id)
        self.job_tags.pop(job_id, None)

    def list_access_points_for_object_lambda(
        self,
        account_id: str,
        max_results: Optional[int] = None,
        next_token: Optional[str] = None,
    ) -> tuple[list[dict[str, Any]], Optional[str]]:
        # Returns list of object lambda access points for this account
        access_points = [
            {
                "Name": ap.name,
                "ObjectLambdaAccessPointArn": ap.arn,
                "Alias": {"Value": ap.alias, "Status": "READY"},
            }
            for ap in self.object_lambda_access_points.get(account_id, {}).values()
        ]
        return access_points, None

    def create_bucket(
        self,
        account_id: str,
        bucket: str,
        outpost_id: Optional[str] = None,
    ) -> OutpostsBucket:
        ob = OutpostsBucket(
            account_id=account_id,
            region_name=self.region_name,
            bucket=bucket,
            outpost_id=outpost_id,
        )
        self.outposts_buckets[bucket] = ob
        return ob

    def get_bucket(
        self,
        account_id: str,
        bucket: str,
    ) -> OutpostsBucket:
        from .exceptions import InvalidRequestException

        if bucket not in self.outposts_buckets:
            raise InvalidRequestException(f"The specified bucket does not exist: {bucket}")
        return self.outposts_buckets[bucket]

    def delete_bucket(
        self,
        account_id: str,
        bucket: str,
    ) -> None:
        self.outposts_buckets.pop(bucket, None)

    def list_regional_buckets(
        self,
        account_id: str,
        outpost_id: Optional[str] = None,
        max_results: Optional[int] = None,
        next_token: Optional[str] = None,
    ) -> tuple[list[dict[str, Any]], Optional[str]]:
        # Stub: regional (Outposts) buckets not yet modeled
        return [], None

    def list_caller_access_grants(
        self,
        account_id: str,
        grant_scope: Optional[str] = None,
        max_results: Optional[int] = None,
        next_token: Optional[str] = None,
        allowed_by_application: Optional[bool] = None,
    ) -> tuple[list[dict[str, Any]], Optional[str]]:
        # Stub: caller access grants not yet modeled
        return [], None


s3control_backends = BackendDict(
    S3ControlBackend,
    "s3control",
    use_boto3_regions=False,
    additional_regions=PARTITION_NAMES,
)
