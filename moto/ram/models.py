import re
import string
from datetime import datetime, timezone
from typing import Any, Optional

from moto.core.base_backend import BackendDict, BaseBackend
from moto.core.common_models import BaseModel
from moto.core.utils import unix_time, utcnow
from moto.moto_api._internal import mock_random as random
from moto.organizations.models import (
    OrganizationsBackend,
    organizations_backends,
)
from moto.ram.exceptions import (
    InvalidParameterException,
    MalformedArnException,
    OperationNotPermittedException,
    UnknownResourceException,
)
from moto.ram.utils import AWS_MANAGED_PERMISSIONS, RAM_RESOURCE_TYPES
from moto.utilities.utils import get_partition


def random_resource_id(size: int) -> str:
    return "".join(random.choice(string.digits + "abcdef") for _ in range(size))


class ResourceShareInvitation(BaseModel):
    def __init__(
        self,
        account_id: str,
        region: str,
        resource_share_arn: str,
        resource_share_name: str,
        sender_account_id: str,
        receiver_account_id: str,
    ):
        self.partition = get_partition(region)
        self.arn = (
            f"arn:{self.partition}:ram:{region}:{account_id}"
            f":resource-share-invitation/{random.uuid4()}"
        )
        self.resource_share_arn = resource_share_arn
        self.resource_share_name = resource_share_name
        self.sender_account_id = sender_account_id
        self.receiver_account_id = receiver_account_id
        self.invitation_timestamp = utcnow()
        self.status = "PENDING"
        self.resource_share_associations: list[dict[str, Any]] = []

    def accept(self) -> None:
        self.status = "ACCEPTED"

    def reject(self) -> None:
        self.status = "REJECTED"

    def describe(self) -> dict[str, Any]:
        return {
            "resourceShareInvitationArn": self.arn,
            "resourceShareName": self.resource_share_name,
            "resourceShareArn": self.resource_share_arn,
            "senderAccountId": self.sender_account_id,
            "receiverAccountId": self.receiver_account_id,
            "invitationTimestamp": unix_time(self.invitation_timestamp),
            "status": self.status,
            "resourceShareAssociations": self.resource_share_associations,
        }


class ResourceShare(BaseModel):
    # List of shareable resources can be found here
    # https://docs.aws.amazon.com/ram/latest/userguide/shareable.html
    SHAREABLE_RESOURCES = [
        "cluster",  # Amazon Aurora cluster
        "component",  # Amazon EC2 Image Builder component
        "core-network",  # Amazon Network Manager core network
        "group",  # AWS Resource Groups
        "image",  # Amazon EC2 Image Builder image
        "image-recipe",  # Amazon EC2 Image Builder image recipe
        "license-configuration",  # AWS License Manager configuration
        "mesh",  # AWS App Mesh
        "prefix-list",  # Amazon EC2 prefix list
        "project",  # AWS CodeBuild project
        "report-group",  # AWS CodeBuild report group
        "resolver-rule",  # Amazon Route 53 forwarding rule
        "subnet",  # Amazon EC2 subnet
        "transit-gateway",  # Amazon EC2 transit gateway,
        "database",  # Amazon Glue database
        "table",  # Amazon Glue table
        "catalog",  # Amazon Glue catalog
    ]

    def __init__(self, account_id: str, region: str, **kwargs: Any):
        self.account_id = account_id
        self.region = region
        self.partition = get_partition(region)

        self.allow_external_principals = kwargs.get("allowExternalPrincipals", True)
        self.arn = f"arn:{self.partition}:ram:{self.region}:{account_id}:resource-share/{random.uuid4()}"
        self.creation_time = utcnow()
        self.feature_set = "STANDARD"
        self.last_updated_time = utcnow()
        self.name = kwargs["name"]
        self.owning_account_id = account_id
        self.principals: list[str] = []
        self.resource_arns: list[str] = []
        self.status = "ACTIVE"
        self.tags: list[dict[str, str]] = kwargs.get("tags", [])
        self.permission_arns: list[str] = []

    @property
    def organizations_backend(self) -> OrganizationsBackend:
        return organizations_backends[self.account_id][self.partition]

    def add_principals(self, principals: list[str]) -> None:
        for principal in principals:
            match = re.search(
                r"^arn:aws:organizations::\d{12}:organization/(o-\w+)$", principal
            )
            if match:
                organization = self.organizations_backend.describe_organization()
                if principal == organization["Organization"]["Arn"]:
                    continue
                else:
                    raise UnknownResourceException(
                        f"Organization {match.group(1)} could not be found."
                    )

            match = re.search(
                r"^arn:aws:organizations::\d{12}:ou/(o-\w+)/(ou-[\w-]+)$", principal
            )
            if match:
                roots = self.organizations_backend.list_roots()
                root_id = next(
                    (
                        root["Id"]
                        for root in roots["Roots"]
                        if root["Name"] == "Root" and match.group(1) in root["Arn"]
                    ),
                    None,
                )

                if root_id:
                    (
                        ous,
                        _,
                    ) = self.organizations_backend.list_organizational_units_for_parent(
                        parent_id=root_id
                    )
                    if any(principal == ou.arn for ou in ous):
                        continue

                raise UnknownResourceException(
                    f"OrganizationalUnit {match.group(2)} in unknown organization could not be found."
                )

            if not re.match(r"^\d{12}$", principal):
                raise InvalidParameterException(
                    f"Principal ID {principal} is malformed. Verify the ID and try again."
                )

        for principal in principals:
            self.principals.append(principal)

    def add_resources(self, resource_arns: list[str]) -> None:
        for resource in resource_arns:
            match = re.search(
                r"^arn:aws:[a-z0-9-]+:[a-z0-9-]*:[0-9]{12}:([a-z-]+)[/:].*$", resource
            )
            if not match:
                raise MalformedArnException(
                    f"The specified resource ARN {resource} is not valid. Verify the ARN and try again."
                )

            if match.group(1) not in self.SHAREABLE_RESOURCES:
                raise MalformedArnException(
                    "You cannot share the selected resource type."
                )

        for resource in resource_arns:
            self.resource_arns.append(resource)

    def remove_principals(self, principals: list[str]) -> None:
        self.principals = [p for p in self.principals if p not in principals]

    def remove_resources(self, resource_arns: list[str]) -> None:
        self.resource_arns = [r for r in self.resource_arns if r not in resource_arns]

    def add_tags(self, tags: list[dict[str, str]]) -> None:
        existing_keys = {t["key"]: i for i, t in enumerate(self.tags)}
        for tag in tags:
            if tag["key"] in existing_keys:
                self.tags[existing_keys[tag["key"]]] = tag
            else:
                self.tags.append(tag)

    def remove_tags(self, tag_keys: list[str]) -> None:
        self.tags = [t for t in self.tags if t["key"] not in tag_keys]

    def delete(self) -> None:
        self.last_updated_time = utcnow()
        self.status = "DELETED"

    def describe(self) -> dict[str, Any]:
        return {
            "allowExternalPrincipals": self.allow_external_principals,
            "creationTime": unix_time(self.creation_time),
            "featureSet": self.feature_set,
            "lastUpdatedTime": unix_time(self.last_updated_time),
            "name": self.name,
            "owningAccountId": self.owning_account_id,
            "resourceShareArn": self.arn,
            "status": self.status,
        }

    def update(self, allow_external_principals: bool, name: Optional[str]) -> None:
        self.allow_external_principals = allow_external_principals
        self.last_updated_time = utcnow()
        self.name = name


class ResourceType(BaseModel):
    def __init__(
        self, resource_type: str, service_name: str, resource_region_scope: str
    ):
        self.resource_type = resource_type
        self.service_name = service_name
        self.resource_region_scope = resource_region_scope

    def describe(self) -> dict[str, Any]:
        return {
            "resourceType": self.resource_type,
            "serviceName": self.service_name,
            "resourceRegionScope": self.resource_region_scope,
        }


class ManagedPermission(BaseModel):
    def __init__(
        self,
        account_id: str,
        region: str,
        name: str,
        resource_type: str,
        version: str = "1",
        default_version: bool = True,
        status: str = "ATTACHABLE",
        creation_time: Optional[str] = None,
        last_updated_time: Optional[str] = None,
        is_resource_type_default: bool = False,
        permission_type: str = "AWS_MANAGED",  # or "CUSTOMER_MANAGED",
    ):
        self.account_id = account_id
        self.region = region
        self.partition = get_partition(region)

        now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        arn_prefix = (
            f"arn:{self.partition}:ram::{self.partition}:permission/"
            if permission_type == "AWS_MANAGED"
            else f"arn:{self.partition}:ram:{self.region}:{account_id}:permission/"
        )

        self.name = name
        self.arn = f"{arn_prefix}{name}"
        self.resource_type = resource_type
        self.version = version
        self.default_version = default_version
        self.status = status
        self.creation_time = creation_time or now
        self.last_updated_time = last_updated_time or creation_time
        self.is_resource_type_default = is_resource_type_default
        self.permission_type = permission_type
        self.policy_template: Optional[str] = None
        self.versions: list[dict[str, Any]] = [
            {
                "version": self.version,
                "default_version": self.default_version,
                "creation_time": self.creation_time,
                "status": self.status,
            }
        ]
        self.tags: list[dict[str, str]] = []

    def describe(self) -> dict[str, Any]:
        return {
            "arn": self.arn,
            "name": self.name,
            "resourceType": self.resource_type,
            "version": self.version,
            "defaultVersion": self.default_version,
            "status": self.status,
            "creationTime": self.creation_time,
            "lastUpdatedTime": self.last_updated_time,
            "isResourceTypeDefault": self.is_resource_type_default,
            "permissionType": self.permission_type,
        }


    def describe_detail(self, version: Optional[int] = None) -> dict[str, Any]:
        result = self.describe()
        result["permission"] = self.policy_template or "{}"
        if version:
            result["version"] = str(version)
        return result

    def create_version(self, policy_template: str) -> dict[str, Any]:
        new_version = str(len(self.versions) + 1)
        now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        self.versions.append(
            {
                "version": new_version,
                "default_version": False,
                "creation_time": now,
                "status": "CREATED",
            }
        )
        return {
            "arn": self.arn,
            "name": self.name,
            "resourceType": self.resource_type,
            "version": new_version,
            "defaultVersion": False,
            "status": "CREATED",
            "creationTime": now,
            "lastUpdatedTime": now,
            "isResourceTypeDefault": self.is_resource_type_default,
            "permissionType": self.permission_type,
            "permission": policy_template,
        }

    def delete_version(self, version: int) -> None:
        self.versions = [
            v for v in self.versions if v["version"] != str(version)
        ]

    def set_default_version(self, version: int) -> None:
        for v in self.versions:
            v["default_version"] = v["version"] == str(version)
        self.version = str(version)
        self.default_version = True

    def list_versions(self) -> list[dict[str, Any]]:
        return [
            {
                "arn": self.arn,
                "name": self.name,
                "resourceType": self.resource_type,
                "version": v["version"],
                "defaultVersion": v["default_version"],
                "status": v.get("status", self.status),
                "creationTime": v["creation_time"],
                "lastUpdatedTime": v["creation_time"],
                "isResourceTypeDefault": self.is_resource_type_default,
                "permissionType": self.permission_type,
            }
            for v in self.versions
        ]


class ResourceAccessManagerBackend(BaseBackend):
    PERMISSION_TYPES = ["ALL", "AWS", "LOCAL"]

    def __init__(self, region_name: str, account_id: str):
        super().__init__(region_name, account_id)
        self.resource_shares: list[ResourceShare] = []
        self.invitations: list[ResourceShareInvitation] = []
        self.replace_permission_work_items: list[dict[str, Any]] = []
        self.managed_permissions: list[ManagedPermission] = [
            ManagedPermission(
                account_id=account_id,
                region=region_name,
                name=permission["name"],
                resource_type=permission["resourceType"],
                version=permission["version"],
                default_version=permission["defaultVersion"],
                status=permission["status"],
                creation_time=permission["creationTime"],
                last_updated_time=permission["lastUpdatedTime"],
                is_resource_type_default=permission["isResourceTypeDefault"],
                permission_type=permission["permissionType"],
            )
            for permission in AWS_MANAGED_PERMISSIONS
        ]
        self.resource_types: list[ResourceType] = [
            ResourceType(
                resource_type=resource_type["resourceType"],
                service_name=resource_type["serviceName"],
                resource_region_scope=resource_type["resourceRegionScope"],
            )
            for resource_type in RAM_RESOURCE_TYPES
        ]

    @property
    def organizations_backend(self) -> OrganizationsBackend:
        return organizations_backends[self.account_id][self.partition]

    def create_resource_share(self, **kwargs: Any) -> dict[str, Any]:
        resource = ResourceShare(self.account_id, self.region_name, **kwargs)
        resource.add_principals(kwargs.get("principals", []))
        resource.add_resources(kwargs.get("resourceArns", []))

        self.resource_shares.append(resource)

        response = resource.describe()
        response.pop("featureSet")

        return {"resourceShare": response}

    def get_resource_shares(self, resource_owner: Optional[str]) -> dict[str, Any]:
        if resource_owner not in ["SELF", "OTHER-ACCOUNTS"]:
            raise InvalidParameterException(
                f"{resource_owner} is not a valid resource owner. "
                "Specify either SELF or OTHER-ACCOUNTS and try again."
            )

        if resource_owner == "OTHER-ACCOUNTS":
            raise NotImplementedError(
                "Value 'OTHER-ACCOUNTS' for parameter 'resourceOwner' not implemented."
            )

        resources = [resource.describe() for resource in self.resource_shares]

        return {"resourceShares": resources}

    def update_resource_share(
        self,
        resource_share_arn: Optional[str],
        allow_external_principals: bool,
        name: Optional[str],
    ) -> dict[str, Any]:
        resource = next(
            (
                resource
                for resource in self.resource_shares
                if resource_share_arn == resource.arn
            ),
            None,
        )

        if not resource:
            raise UnknownResourceException(
                f"ResourceShare {resource_share_arn} could not be found."
            )

        resource.update(allow_external_principals, name)
        response = resource.describe()
        response.pop("featureSet")

        return {"resourceShare": response}

    def delete_resource_share(
        self, resource_share_arn: Optional[str]
    ) -> dict[str, Any]:
        resource = next(
            (
                resource
                for resource in self.resource_shares
                if resource_share_arn == resource.arn
            ),
            None,
        )

        if not resource:
            raise UnknownResourceException(
                f"ResourceShare {resource_share_arn} could not be found."
            )

        resource.delete()

        return {"returnValue": True}

    def enable_sharing_with_aws_organization(self) -> dict[str, Any]:
        if not self.organizations_backend.org:
            raise OperationNotPermittedException

        return {"returnValue": True}

    def get_resource_share_associations(
        self,
        association_type: Optional[str],
        association_status: Optional[str],
        resource_share_arns: list[str],
        resource_arn: Optional[str],
        principal: Optional[str],
    ) -> dict[str, Any]:
        if association_type not in ["PRINCIPAL", "RESOURCE"]:
            raise InvalidParameterException(
                f"{association_type} is not a valid association type. "
                "Specify either PRINCIPAL or RESOURCE and try again."
            )

        if association_status and association_status not in [
            "ASSOCIATING",
            "ASSOCIATED",
            "FAILED",
            "DISASSOCIATING",
            "DISASSOCIATED",
        ]:
            raise InvalidParameterException(
                f"{association_status} is not a valid association status."
            )

        if association_type == "PRINCIPAL" and resource_arn:
            raise InvalidParameterException(
                "You cannot specify a resource ARN when the association type is PRINCIPAL."
            )
        if association_type == "RESOURCE" and principal:
            raise InvalidParameterException(
                "You cannot specify a principal when the association type is RESOURCE."
            )

        associations = []
        for resource_share in self.resource_shares:
            if resource_share_arns and resource_share.arn not in resource_share_arns:
                continue

            if association_type == "PRINCIPAL":
                for principal_id in resource_share.principals:
                    if principal and principal != principal_id:
                        continue
                    associations.append(
                        {
                            "resourceShareArn": resource_share.arn,
                            "resourceShareName": resource_share.name,
                            "associatedEntity": principal_id,
                            "associationType": "PRINCIPAL",
                            "status": association_status or "ASSOCIATED",
                            "creationTime": unix_time(resource_share.creation_time),
                            "lastUpdatedTime": unix_time(
                                resource_share.last_updated_time
                            ),
                            "external": False,
                        }
                    )
            else:  # RESOURCE
                for resource_id in resource_share.resource_arns:
                    if resource_arn and resource_arn != resource_id:
                        continue
                    associations.append(
                        {
                            "resourceShareArn": resource_share.arn,
                            "resourceShareName": resource_share.name,
                            "associatedEntity": resource_id,
                            "associationType": "RESOURCE",
                            "status": association_status or "ASSOCIATED",
                            "creationTime": unix_time(resource_share.creation_time),
                            "lastUpdatedTime": unix_time(
                                resource_share.last_updated_time
                            ),
                            "external": False,
                        }
                    )

        return {"resourceShareAssociations": associations}

    def list_resource_types(self, resource_region_scope: str) -> dict[str, Any]:
        if resource_region_scope not in ["ALL", "REGIONAL", "GLOBAL"]:
            raise InvalidParameterException(
                f"{resource_region_scope} is not a valid resource region "
                "scope value. Specify a valid value and try again."
            )

        if resource_region_scope == "ALL":
            resource_types = [
                resource_type.describe() for resource_type in self.resource_types
            ]
        else:
            resource_types = [
                resource_type_dict
                for resource_type in self.resource_types
                if (resource_type_dict := resource_type.describe())
                and resource_type_dict["resourceRegionScope"] == resource_region_scope
            ]

        return {"resourceTypes": resource_types}

    def list_permissions(
        self, resource_type: str, permission_type: str
    ) -> dict[str, Any]:
        permission_types_relation = {
            "AWS": "AWS_MANAGED",
            "LOCAL": "CUSTOMER_MANAGED",
        }

        # Here, resourceType first partition (service) is case sensitive and
        # last partition (type) is case insensitive
        if resource_type and not any(
            (permission_dict := permission.describe())
            and permission_dict["resourceType"].split(":")[0]
            == resource_type.split(":")[0]
            and permission_dict["resourceType"].lower() == resource_type.lower()
            for permission in self.managed_permissions
        ):
            raise InvalidParameterException(f"Invalid resource type: {resource_type}")

        if resource_type:
            permissions = [
                permission_dict
                for permission in self.managed_permissions
                if (permission_dict := permission.describe())
                and permission_dict["resourceType"].lower() == resource_type.lower()
            ]
        else:
            permissions = [
                permission.describe() for permission in self.managed_permissions
            ]

        if permission_type not in self.PERMISSION_TYPES:
            raise InvalidParameterException(
                f"{permission_type} is not a valid scope. Must be one of: "
                f"{', '.join(self.PERMISSION_TYPES)}."
            )

        if permission_type != "ALL":
            permissions = [
                permission
                for permission in permissions
                if permission_types_relation.get(permission_type)
                == permission["permissionType"]
            ]

        return {"permissions": permissions}

    def _find_resource_share(self, arn: str) -> ResourceShare:
        resource = next(
            (rs for rs in self.resource_shares if rs.arn == arn), None
        )
        if not resource:
            raise UnknownResourceException(
                f"ResourceShare {arn} could not be found."
            )
        return resource

    def _find_permission(self, arn: str) -> ManagedPermission:
        permission = next(
            (p for p in self.managed_permissions if p.arn == arn), None
        )
        if not permission:
            raise UnknownResourceException(
                f"Permission {arn} could not be found."
            )
        return permission

    def _find_invitation(self, arn: str) -> "ResourceShareInvitation":
        invitation = next(
            (inv for inv in self.invitations if inv.arn == arn), None
        )
        if not invitation:
            raise UnknownResourceException(
                f"ResourceShareInvitation {arn} could not be found."
            )
        return invitation

    def associate_resource_share(
        self,
        resource_share_arn: str,
        resource_arns: list[str],
        principals: list[str],
    ) -> dict[str, Any]:
        resource_share = self._find_resource_share(resource_share_arn)
        associations: list[dict[str, Any]] = []

        if resource_arns:
            resource_share.add_resources(resource_arns)
            for resource_arn in resource_arns:
                associations.append(
                    {
                        "resourceShareArn": resource_share.arn,
                        "resourceShareName": resource_share.name,
                        "associatedEntity": resource_arn,
                        "associationType": "RESOURCE",
                        "status": "ASSOCIATED",
                        "creationTime": unix_time(resource_share.creation_time),
                        "lastUpdatedTime": unix_time(utcnow()),
                        "external": False,
                    }
                )

        if principals:
            resource_share.add_principals(principals)
            for principal in principals:
                associations.append(
                    {
                        "resourceShareArn": resource_share.arn,
                        "resourceShareName": resource_share.name,
                        "associatedEntity": principal,
                        "associationType": "PRINCIPAL",
                        "status": "ASSOCIATED",
                        "creationTime": unix_time(resource_share.creation_time),
                        "lastUpdatedTime": unix_time(utcnow()),
                        "external": False,
                    }
                )

        return {"resourceShareAssociations": associations}

    def disassociate_resource_share(
        self,
        resource_share_arn: str,
        resource_arns: list[str],
        principals: list[str],
    ) -> dict[str, Any]:
        resource_share = self._find_resource_share(resource_share_arn)
        associations: list[dict[str, Any]] = []

        if resource_arns:
            resource_share.remove_resources(resource_arns)
            for resource_arn in resource_arns:
                associations.append(
                    {
                        "resourceShareArn": resource_share.arn,
                        "resourceShareName": resource_share.name,
                        "associatedEntity": resource_arn,
                        "associationType": "RESOURCE",
                        "status": "DISASSOCIATED",
                        "creationTime": unix_time(resource_share.creation_time),
                        "lastUpdatedTime": unix_time(utcnow()),
                        "external": False,
                    }
                )

        if principals:
            resource_share.remove_principals(principals)
            for principal in principals:
                associations.append(
                    {
                        "resourceShareArn": resource_share.arn,
                        "resourceShareName": resource_share.name,
                        "associatedEntity": principal,
                        "associationType": "PRINCIPAL",
                        "status": "DISASSOCIATED",
                        "creationTime": unix_time(resource_share.creation_time),
                        "lastUpdatedTime": unix_time(utcnow()),
                        "external": False,
                    }
                )

        return {"resourceShareAssociations": associations}

    def associate_resource_share_permission(
        self,
        resource_share_arn: str,
        permission_arn: str,
    ) -> dict[str, Any]:
        resource_share = self._find_resource_share(resource_share_arn)
        self._find_permission(permission_arn)
        if permission_arn not in resource_share.permission_arns:
            resource_share.permission_arns.append(permission_arn)
        return {"returnValue": True}

    def disassociate_resource_share_permission(
        self,
        resource_share_arn: str,
        permission_arn: str,
    ) -> dict[str, Any]:
        resource_share = self._find_resource_share(resource_share_arn)
        resource_share.permission_arns = [
            a for a in resource_share.permission_arns if a != permission_arn
        ]
        return {"returnValue": True}

    def create_permission(
        self,
        name: str,
        resource_type: str,
        policy_template: str,
        tags: Optional[list[dict[str, str]]] = None,
    ) -> dict[str, Any]:
        permission = ManagedPermission(
            account_id=self.account_id,
            region=self.region_name,
            name=name,
            resource_type=resource_type,
            permission_type="CUSTOMER_MANAGED",
        )
        permission.policy_template = policy_template
        if tags:
            permission.tags = tags
        self.managed_permissions.append(permission)
        return {"permission": permission.describe()}

    def create_permission_version(
        self,
        permission_arn: str,
        policy_template: str,
    ) -> dict[str, Any]:
        permission = self._find_permission(permission_arn)
        version_detail = permission.create_version(policy_template)
        return {"permission": version_detail}

    def delete_permission(self, permission_arn: str) -> dict[str, Any]:
        permission = self._find_permission(permission_arn)
        if permission.permission_type == "AWS_MANAGED":
            raise InvalidParameterException(
                "You cannot delete an AWS managed permission."
            )
        self.managed_permissions = [
            p for p in self.managed_permissions if p.arn != permission_arn
        ]
        return {"returnValue": True, "permissionStatus": "DELETED"}

    def delete_permission_version(
        self, permission_arn: str, permission_version: int
    ) -> dict[str, Any]:
        permission = self._find_permission(permission_arn)
        permission.delete_version(permission_version)
        return {"returnValue": True, "permissionStatus": "DELETED"}

    def get_permission(
        self, permission_arn: str, permission_version: Optional[int] = None
    ) -> dict[str, Any]:
        permission = self._find_permission(permission_arn)
        return {"permission": permission.describe_detail(permission_version)}

    def set_default_permission_version(
        self, permission_arn: str, permission_version: int
    ) -> dict[str, Any]:
        permission = self._find_permission(permission_arn)
        permission.set_default_version(permission_version)
        return {"returnValue": True}

    def list_permission_versions(
        self, permission_arn: str
    ) -> dict[str, Any]:
        permission = self._find_permission(permission_arn)
        return {"permissions": permission.list_versions()}

    def list_resource_share_permissions(
        self, resource_share_arn: str
    ) -> dict[str, Any]:
        resource_share = self._find_resource_share(resource_share_arn)
        permissions = []
        for perm_arn in resource_share.permission_arns:
            try:
                perm = self._find_permission(perm_arn)
                permissions.append(perm.describe())
            except UnknownResourceException:
                pass
        return {"permissions": permissions}

    def get_resource_share_invitations(
        self,
        resource_share_invitation_arns: Optional[list[str]] = None,
        resource_share_arns: Optional[list[str]] = None,
    ) -> dict[str, Any]:
        invitations = self.invitations
        if resource_share_invitation_arns:
            invitations = [
                inv
                for inv in invitations
                if inv.arn in resource_share_invitation_arns
            ]
        if resource_share_arns:
            invitations = [
                inv
                for inv in invitations
                if inv.resource_share_arn in resource_share_arns
            ]
        return {
            "resourceShareInvitations": [
                inv.describe() for inv in invitations
            ]
        }

    def accept_resource_share_invitation(
        self, resource_share_invitation_arn: str
    ) -> dict[str, Any]:
        invitation = self._find_invitation(resource_share_invitation_arn)
        invitation.accept()
        return {"resourceShareInvitation": invitation.describe()}

    def reject_resource_share_invitation(
        self, resource_share_invitation_arn: str
    ) -> dict[str, Any]:
        invitation = self._find_invitation(resource_share_invitation_arn)
        invitation.reject()
        return {"resourceShareInvitation": invitation.describe()}

    def get_resource_policies(
        self, resource_arns: list[str]
    ) -> dict[str, Any]:
        # Return empty policies - resource policies are not tracked in RAM mock
        return {"policies": []}

    def list_principals(
        self,
        resource_owner: str,
        resource_arn: Optional[str] = None,
        principals_filter: Optional[list[str]] = None,
        resource_type: Optional[str] = None,
        resource_share_arns: Optional[list[str]] = None,
    ) -> dict[str, Any]:
        if resource_owner not in ["SELF", "OTHER-ACCOUNTS"]:
            raise InvalidParameterException(
                f"{resource_owner} is not a valid resource owner. "
                "Specify either SELF or OTHER-ACCOUNTS and try again."
            )

        result: list[dict[str, Any]] = []
        for resource_share in self.resource_shares:
            if resource_share_arns and resource_share.arn not in resource_share_arns:
                continue
            if resource_arn and resource_arn not in resource_share.resource_arns:
                continue
            for principal in resource_share.principals:
                if principals_filter and principal not in principals_filter:
                    continue
                result.append(
                    {
                        "id": principal,
                        "resourceShareArn": resource_share.arn,
                        "creationTime": unix_time(resource_share.creation_time),
                        "lastUpdatedTime": unix_time(
                            resource_share.last_updated_time
                        ),
                        "external": not re.match(r"^\d{12}$", principal),
                    }
                )

        return {"principals": result}

    def list_resources(
        self,
        resource_owner: str,
        principal: Optional[str] = None,
        resource_type: Optional[str] = None,
        resource_arns_filter: Optional[list[str]] = None,
        resource_share_arns: Optional[list[str]] = None,
    ) -> dict[str, Any]:
        if resource_owner not in ["SELF", "OTHER-ACCOUNTS"]:
            raise InvalidParameterException(
                f"{resource_owner} is not a valid resource owner. "
                "Specify either SELF or OTHER-ACCOUNTS and try again."
            )

        result: list[dict[str, Any]] = []
        for resource_share in self.resource_shares:
            if resource_share_arns and resource_share.arn not in resource_share_arns:
                continue
            if principal and principal not in resource_share.principals:
                continue
            for res_arn in resource_share.resource_arns:
                if resource_arns_filter and res_arn not in resource_arns_filter:
                    continue
                # Extract resource type from ARN
                match = re.search(
                    r"^arn:aws:[a-z0-9-]+:[a-z0-9-]*:[0-9]{12}:([a-z-]+)[/:]",
                    res_arn,
                )
                res_type = match.group(1) if match else ""
                if resource_type and res_type != resource_type:
                    continue
                result.append(
                    {
                        "arn": res_arn,
                        "type": res_type,
                        "resourceShareArn": resource_share.arn,
                        "resourceGroupArn": None,
                        "status": "AVAILABLE",
                        "creationTime": unix_time(resource_share.creation_time),
                        "lastUpdatedTime": unix_time(
                            resource_share.last_updated_time
                        ),
                    }
                )

        return {"resources": result}

    def list_pending_invitation_resources(
        self, resource_share_invitation_arn: str
    ) -> dict[str, Any]:
        invitation = self._find_invitation(resource_share_invitation_arn)
        resource_share = next(
            (
                rs
                for rs in self.resource_shares
                if rs.arn == invitation.resource_share_arn
            ),
            None,
        )
        resources: list[dict[str, Any]] = []
        if resource_share:
            for res_arn in resource_share.resource_arns:
                match = re.search(
                    r"^arn:aws:[a-z0-9-]+:[a-z0-9-]*:[0-9]{12}:([a-z-]+)[/:]",
                    res_arn,
                )
                res_type = match.group(1) if match else ""
                resources.append(
                    {
                        "arn": res_arn,
                        "type": res_type,
                        "resourceShareArn": resource_share.arn,
                        "status": "AVAILABLE",
                        "creationTime": unix_time(resource_share.creation_time),
                        "lastUpdatedTime": unix_time(
                            resource_share.last_updated_time
                        ),
                    }
                )
        return {"resources": resources}

    def list_permission_associations(
        self,
        permission_arn: Optional[str] = None,
    ) -> dict[str, Any]:
        result: list[dict[str, Any]] = []
        for resource_share in self.resource_shares:
            for perm_arn in resource_share.permission_arns:
                if permission_arn and perm_arn != permission_arn:
                    continue
                result.append(
                    {
                        "arn": perm_arn,
                        "permissionVersion": "1",
                        "defaultVersion": True,
                        "resourceShareArn": resource_share.arn,
                        "status": "ASSOCIATED",
                        "featureSet": resource_share.feature_set,
                        "lastUpdatedTime": unix_time(
                            resource_share.last_updated_time
                        ),
                        "resourceType": "",
                    }
                )
        return {"permissions": result}

    def list_replace_permission_associations_work(
        self,
        work_ids: Optional[list[str]] = None,
        status: Optional[str] = None,
    ) -> dict[str, Any]:
        items = self.replace_permission_work_items
        if work_ids:
            items = [w for w in items if w["id"] in work_ids]
        if status:
            items = [w for w in items if w["status"] == status]
        return {"replacePermissionAssociationsWorks": items}

    def list_source_associations(
        self,
        resource_share_arns: Optional[list[str]] = None,
    ) -> dict[str, Any]:
        # Source associations are not tracked in the mock
        return {"sourceAssociations": []}

    def promote_permission_created_from_policy(
        self, permission_arn: str, name: str
    ) -> dict[str, Any]:
        permission = self._find_permission(permission_arn)
        permission.name = name
        permission.permission_type = "CUSTOMER_MANAGED"
        return {"permission": permission.describe()}

    def promote_resource_share_created_from_policy(
        self, resource_share_arn: str
    ) -> dict[str, Any]:
        self._find_resource_share(resource_share_arn)
        return {"returnValue": True}

    def replace_permission_associations(
        self,
        from_permission_arn: str,
        to_permission_arn: str,
    ) -> dict[str, Any]:
        self._find_permission(from_permission_arn)
        self._find_permission(to_permission_arn)
        now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        work_id = str(random.uuid4())
        work_item = {
            "id": work_id,
            "fromPermissionArn": from_permission_arn,
            "toPermissionArn": to_permission_arn,
            "status": "COMPLETED",
            "creationTime": now,
            "lastUpdatedTime": now,
        }
        self.replace_permission_work_items.append(work_item)

        # Actually replace in resource shares
        for resource_share in self.resource_shares:
            resource_share.permission_arns = [
                to_permission_arn if a == from_permission_arn else a
                for a in resource_share.permission_arns
            ]

        return {"replacePermissionAssociationsWork": work_item}

    def tag_resource(
        self,
        resource_share_arn: Optional[str],
        resource_arn: Optional[str],
        tags: list[dict[str, str]],
    ) -> dict[str, Any]:
        arn = resource_share_arn or resource_arn
        if not arn:
            raise InvalidParameterException(
                "You must specify either resourceShareArn or resourceArn."
            )
        # Try resource share first
        resource_share = next(
            (rs for rs in self.resource_shares if rs.arn == arn), None
        )
        if resource_share:
            resource_share.add_tags(tags)
            return {}
        # Try permission
        permission = next(
            (p for p in self.managed_permissions if p.arn == arn), None
        )
        if permission:
            existing_keys = {t["key"]: i for i, t in enumerate(permission.tags)}
            for tag in tags:
                if tag["key"] in existing_keys:
                    permission.tags[existing_keys[tag["key"]]] = tag
                else:
                    permission.tags.append(tag)
            return {}
        raise UnknownResourceException(f"Resource {arn} could not be found.")

    def untag_resource(
        self,
        resource_share_arn: Optional[str],
        resource_arn: Optional[str],
        tag_keys: list[str],
    ) -> dict[str, Any]:
        arn = resource_share_arn or resource_arn
        if not arn:
            raise InvalidParameterException(
                "You must specify either resourceShareArn or resourceArn."
            )
        resource_share = next(
            (rs for rs in self.resource_shares if rs.arn == arn), None
        )
        if resource_share:
            resource_share.remove_tags(tag_keys)
            return {}
        permission = next(
            (p for p in self.managed_permissions if p.arn == arn), None
        )
        if permission:
            permission.tags = [
                t for t in permission.tags if t["key"] not in tag_keys
            ]
            return {}
        raise UnknownResourceException(f"Resource {arn} could not be found.")


ram_backends = BackendDict(ResourceAccessManagerBackend, "ram")
