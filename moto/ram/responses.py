import json
from typing import Any

from moto.core.responses import BaseResponse

from .models import ResourceAccessManagerBackend, ram_backends


class ResourceAccessManagerResponse(BaseResponse):
    def __init__(self) -> None:
        super().__init__(service_name="ram")

    @property
    def ram_backend(self) -> ResourceAccessManagerBackend:
        return ram_backends[self.current_account][self.region]

    @property
    def request_params(self) -> dict[str, Any]:  # type: ignore[misc]
        try:
            return json.loads(self.body)
        except ValueError:
            return {}

    def create_resource_share(self) -> str:
        return json.dumps(self.ram_backend.create_resource_share(**self.request_params))

    def get_resource_shares(self) -> str:
        resource_owner = self._get_param("resourceOwner")
        return json.dumps(self.ram_backend.get_resource_shares(resource_owner))

    def update_resource_share(self) -> str:
        resource_share_arn = self._get_param("resourceShareArn")
        allow_external_principals = self._get_param("allowExternalPrincipals", True)
        name = self._get_param("name")
        return json.dumps(
            self.ram_backend.update_resource_share(
                resource_share_arn, allow_external_principals, name
            )
        )

    def delete_resource_share(self) -> str:
        resource_share_arn = self._get_param("resourceShareArn")
        return json.dumps(self.ram_backend.delete_resource_share(resource_share_arn))

    def enable_sharing_with_aws_organization(self) -> str:
        return json.dumps(self.ram_backend.enable_sharing_with_aws_organization())

    def get_resource_share_associations(self) -> str:
        association_type = self._get_param("associationType")
        association_status = self._get_param("associationStatus")
        resource_share_arns = self._get_param("resourceShareArns", [])
        resource_arn = self._get_param("resourceArn")
        principal = self._get_param("principal")
        return json.dumps(
            self.ram_backend.get_resource_share_associations(
                association_type,
                association_status,
                resource_share_arns,
                resource_arn,
                principal,
            )
        )

    def list_resource_types(self) -> str:
        resource_region_scope = self._get_param("resourceRegionScope", "ALL")
        return json.dumps(self.ram_backend.list_resource_types(resource_region_scope))

    def list_permissions(self) -> str:
        resource_type = self._get_param("resourceType")
        permission_type = self._get_param("permissionType", "ALL")
        return json.dumps(
            self.ram_backend.list_permissions(resource_type, permission_type)
        )

    def associate_resource_share(self) -> str:
        resource_share_arn = self._get_param("resourceShareArn")
        resource_arns = self._get_param("resourceArns", [])
        principals = self._get_param("principals", [])
        return json.dumps(
            self.ram_backend.associate_resource_share(
                resource_share_arn, resource_arns, principals
            )
        )

    def disassociate_resource_share(self) -> str:
        resource_share_arn = self._get_param("resourceShareArn")
        resource_arns = self._get_param("resourceArns", [])
        principals = self._get_param("principals", [])
        return json.dumps(
            self.ram_backend.disassociate_resource_share(
                resource_share_arn, resource_arns, principals
            )
        )

    def associate_resource_share_permission(self) -> str:
        resource_share_arn = self._get_param("resourceShareArn")
        permission_arn = self._get_param("permissionArn")
        return json.dumps(
            self.ram_backend.associate_resource_share_permission(
                resource_share_arn, permission_arn
            )
        )

    def disassociate_resource_share_permission(self) -> str:
        resource_share_arn = self._get_param("resourceShareArn")
        permission_arn = self._get_param("permissionArn")
        return json.dumps(
            self.ram_backend.disassociate_resource_share_permission(
                resource_share_arn, permission_arn
            )
        )

    def create_permission(self) -> str:
        name = self._get_param("name")
        resource_type = self._get_param("resourceType")
        policy_template = self._get_param("policyTemplate")
        tags = self._get_param("tags", [])
        return json.dumps(
            self.ram_backend.create_permission(
                name, resource_type, policy_template, tags
            )
        )

    def create_permission_version(self) -> str:
        permission_arn = self._get_param("permissionArn")
        policy_template = self._get_param("policyTemplate")
        return json.dumps(
            self.ram_backend.create_permission_version(
                permission_arn, policy_template
            )
        )

    def delete_permission(self) -> str:
        permission_arn = self._get_param("permissionArn")
        return json.dumps(
            self.ram_backend.delete_permission(permission_arn)
        )

    def delete_permission_version(self) -> str:
        permission_arn = self._get_param("permissionArn")
        permission_version = int(self._get_param("permissionVersion"))
        return json.dumps(
            self.ram_backend.delete_permission_version(
                permission_arn, permission_version
            )
        )

    def get_permission(self) -> str:
        permission_arn = self._get_param("permissionArn")
        permission_version = self._get_param("permissionVersion")
        if permission_version is not None:
            permission_version = int(permission_version)
        return json.dumps(
            self.ram_backend.get_permission(permission_arn, permission_version)
        )

    def set_default_permission_version(self) -> str:
        permission_arn = self._get_param("permissionArn")
        permission_version = int(self._get_param("permissionVersion"))
        return json.dumps(
            self.ram_backend.set_default_permission_version(
                permission_arn, permission_version
            )
        )

    def list_permission_versions(self) -> str:
        permission_arn = self._get_param("permissionArn")
        return json.dumps(
            self.ram_backend.list_permission_versions(permission_arn)
        )

    def list_resource_share_permissions(self) -> str:
        resource_share_arn = self._get_param("resourceShareArn")
        return json.dumps(
            self.ram_backend.list_resource_share_permissions(resource_share_arn)
        )

    def get_resource_share_invitations(self) -> str:
        resource_share_invitation_arns = self._get_param(
            "resourceShareInvitationArns", []
        )
        resource_share_arns = self._get_param("resourceShareArns", [])
        return json.dumps(
            self.ram_backend.get_resource_share_invitations(
                resource_share_invitation_arns, resource_share_arns
            )
        )

    def accept_resource_share_invitation(self) -> str:
        resource_share_invitation_arn = self._get_param(
            "resourceShareInvitationArn"
        )
        return json.dumps(
            self.ram_backend.accept_resource_share_invitation(
                resource_share_invitation_arn
            )
        )

    def reject_resource_share_invitation(self) -> str:
        resource_share_invitation_arn = self._get_param(
            "resourceShareInvitationArn"
        )
        return json.dumps(
            self.ram_backend.reject_resource_share_invitation(
                resource_share_invitation_arn
            )
        )

    def get_resource_policies(self) -> str:
        resource_arns = self._get_param("resourceArns", [])
        return json.dumps(
            self.ram_backend.get_resource_policies(resource_arns)
        )

    def list_principals(self) -> str:
        resource_owner = self._get_param("resourceOwner")
        resource_arn = self._get_param("resourceArn")
        principals = self._get_param("principals", [])
        resource_type = self._get_param("resourceType")
        resource_share_arns = self._get_param("resourceShareArns", [])
        return json.dumps(
            self.ram_backend.list_principals(
                resource_owner,
                resource_arn,
                principals,
                resource_type,
                resource_share_arns,
            )
        )

    def list_resources(self) -> str:
        resource_owner = self._get_param("resourceOwner")
        principal = self._get_param("principal")
        resource_type = self._get_param("resourceType")
        resource_arns = self._get_param("resourceArns", [])
        resource_share_arns = self._get_param("resourceShareArns", [])
        return json.dumps(
            self.ram_backend.list_resources(
                resource_owner,
                principal,
                resource_type,
                resource_arns,
                resource_share_arns,
            )
        )

    def list_pending_invitation_resources(self) -> str:
        resource_share_invitation_arn = self._get_param(
            "resourceShareInvitationArn"
        )
        return json.dumps(
            self.ram_backend.list_pending_invitation_resources(
                resource_share_invitation_arn
            )
        )

    def list_permission_associations(self) -> str:
        permission_arn = self._get_param("permissionArn")
        return json.dumps(
            self.ram_backend.list_permission_associations(permission_arn)
        )

    def list_replace_permission_associations_work(self) -> str:
        work_ids = self._get_param("workIds", [])
        status = self._get_param("status")
        return json.dumps(
            self.ram_backend.list_replace_permission_associations_work(
                work_ids, status
            )
        )

    def list_source_associations(self) -> str:
        resource_share_arns = self._get_param("resourceShareArns", [])
        return json.dumps(
            self.ram_backend.list_source_associations(resource_share_arns)
        )

    def promote_permission_created_from_policy(self) -> str:
        permission_arn = self._get_param("permissionArn")
        name = self._get_param("name")
        return json.dumps(
            self.ram_backend.promote_permission_created_from_policy(
                permission_arn, name
            )
        )

    def promote_resource_share_created_from_policy(self) -> str:
        resource_share_arn = self._get_param("resourceShareArn")
        return json.dumps(
            self.ram_backend.promote_resource_share_created_from_policy(
                resource_share_arn
            )
        )

    def replace_permission_associations(self) -> str:
        from_permission_arn = self._get_param("fromPermissionArn")
        to_permission_arn = self._get_param("toPermissionArn")
        return json.dumps(
            self.ram_backend.replace_permission_associations(
                from_permission_arn, to_permission_arn
            )
        )

    def tag_resource(self) -> str:
        resource_share_arn = self._get_param("resourceShareArn")
        resource_arn = self._get_param("resourceArn")
        tags = self._get_param("tags", [])
        return json.dumps(
            self.ram_backend.tag_resource(
                resource_share_arn, resource_arn, tags
            )
        )

    def untag_resource(self) -> str:
        resource_share_arn = self._get_param("resourceShareArn")
        resource_arn = self._get_param("resourceArn")
        tag_keys = self._get_param("tagKeys", [])
        return json.dumps(
            self.ram_backend.untag_resource(
                resource_share_arn, resource_arn, tag_keys
            )
        )
