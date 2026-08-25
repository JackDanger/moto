"""Handles incoming workspaces requests, invokes methods, returns responses."""

import json

from moto.core.responses import BaseResponse

from .models import WorkSpacesBackend, workspaces_backends


class WorkSpacesResponse(BaseResponse):
    """Handler for WorkSpaces requests and responses."""

    def __init__(self) -> None:
        super().__init__(service_name="workspaces")

    @property
    def workspaces_backend(self) -> WorkSpacesBackend:
        """Return backend instance specific for this region."""
        return workspaces_backends[self.current_account][self.region]

    def create_workspaces(self) -> str:
        params = json.loads(self.body)
        workspaces = params.get("Workspaces")
        failed_requests, pending_requests = self.workspaces_backend.create_workspaces(
            workspaces=workspaces,
        )
        return json.dumps(
            {"FailedRequests": failed_requests, "PendingRequests": pending_requests}
        )

    def describe_workspaces(self) -> str:
        params = json.loads(self.body)
        workspace_ids = params.get("WorkspaceIds")
        directory_id = params.get("DirectoryId")
        user_name = params.get("UserName")
        bundle_id = params.get("BundleId")
        workspaces = self.workspaces_backend.describe_workspaces(
            workspace_ids=workspace_ids,
            directory_id=directory_id,
            user_name=user_name,
            bundle_id=bundle_id,
        )
        return json.dumps({"Workspaces": [x.to_dict_pending() for x in workspaces]})

    def describe_workspace_directories(self) -> str:
        params = json.loads(self.body)
        directory_ids = params.get("DirectoryIds")
        directories = self.workspaces_backend.describe_workspace_directories(
            directory_ids=directory_ids,
        )
        return json.dumps({"Directories": [d.to_dict() for d in directories]})

    def terminate_workspaces(self) -> str:
        params = json.loads(self.body)
        terminate_requests = params.get("TerminateWorkspaceRequests")

        failed_requests = self.workspaces_backend.terminate_workspaces(
            terminate_workspace_requests=terminate_requests,
        )

        return json.dumps(failed_requests)

    def register_workspace_directory(self) -> str:
        params = json.loads(self.body)
        directory_id = params.get("DirectoryId")
        subnet_ids = params.get("SubnetIds")
        enable_self_service = params.get("EnableSelfService")
        tenancy = params.get("Tenancy")
        tags = params.get("Tags")
        self.workspaces_backend.register_workspace_directory(
            directory_id=directory_id,
            subnet_ids=subnet_ids,
            enable_self_service=enable_self_service,
            tenancy=tenancy,
            tags=tags,
        )
        return json.dumps({})

    def modify_workspace_creation_properties(self) -> str:
        params = json.loads(self.body)
        resource_id = params.get("ResourceId")
        workspace_creation_properties = params.get("WorkspaceCreationProperties")
        self.workspaces_backend.modify_workspace_creation_properties(
            resource_id=resource_id,
            workspace_creation_properties=workspace_creation_properties,
        )
        return "{}"

    def create_tags(self) -> str:
        params = json.loads(self.body)
        resource_id = params.get("ResourceId")
        tags = params.get("Tags")
        self.workspaces_backend.create_tags(
            resource_id=resource_id,
            tags=tags,
        )
        return "{}"

    def delete_tags(self) -> str:
        params = json.loads(self.body)
        resource_id = params.get("ResourceId")
        tag_keys = params.get("TagKeys", [])
        self.workspaces_backend.delete_tags(
            resource_id=resource_id,
            tag_keys=tag_keys,
        )
        return "{}"

    def describe_tags(self) -> str:
        params = json.loads(self.body)
        resource_id = params.get("ResourceId")
        tag_list = self.workspaces_backend.describe_tags(
            resource_id=resource_id,
        )
        return json.dumps({"TagList": tag_list})

    def describe_client_properties(self) -> str:
        params = json.loads(self.body)
        resource_ids = params.get("ResourceIds")
        client_properties_list = self.workspaces_backend.describe_client_properties(
            resource_ids=resource_ids,
        )
        return json.dumps({"ClientPropertiesList": client_properties_list})

    def modify_client_properties(self) -> str:
        params = json.loads(self.body)
        resource_id = params.get("ResourceId")
        client_properties = params.get("ClientProperties")
        self.workspaces_backend.modify_client_properties(
            resource_id=resource_id,
            client_properties=client_properties,
        )
        return "{}"

    def create_workspace_image(self) -> str:
        params = json.loads(self.body)
        name = params.get("Name")
        description = params.get("Description")
        workspace_id = params.get("WorkspaceId")
        tags = params.get("Tags")
        workspace_image = self.workspaces_backend.create_workspace_image(
            name=name,
            description=description,
            workspace_id=workspace_id,
            tags=tags,
        )
        return json.dumps(workspace_image)

    def describe_workspace_images(self) -> str:
        params = json.loads(self.body)
        image_ids = params.get("ImageIds")
        image_type = params.get("ImageType")
        images = self.workspaces_backend.describe_workspace_images(
            image_ids=image_ids,
            image_type=image_type,
        )
        return json.dumps({"Images": images})

    def update_workspace_image_permission(self) -> str:
        params = json.loads(self.body)
        image_id = params.get("ImageId")
        allow_copy_image = params.get("AllowCopyImage")
        shared_account_id = params.get("SharedAccountId")
        self.workspaces_backend.update_workspace_image_permission(
            image_id=image_id,
            allow_copy_image=allow_copy_image,
            shared_account_id=shared_account_id,
        )
        return "{}"

    def describe_workspace_image_permissions(self) -> str:
        params = json.loads(self.body)
        image_id = params.get("ImageId")
        (
            image_id,
            image_permissions,
        ) = self.workspaces_backend.describe_workspace_image_permissions(
            image_id=image_id,
        )
        return json.dumps({"ImageId": image_id, "ImagePermissions": image_permissions})

    def deregister_workspace_directory(self) -> str:
        params = json.loads(self.body)
        directory_id = params.get("DirectoryId")
        self.workspaces_backend.deregister_workspace_directory(
            directory_id=directory_id,
        )
        return "{}"

    def modify_selfservice_permissions(self) -> str:
        params = json.loads(self.body)
        resource_id = params.get("ResourceId")
        selfservice_permissions = params.get("SelfservicePermissions")
        self.workspaces_backend.modify_selfservice_permissions(
            resource_id=resource_id,
            selfservice_permissions=selfservice_permissions,
        )
        return "{}"

    # --- IP Groups ---

    def create_ip_group(self) -> str:
        params = json.loads(self.body)
        group_id = self.workspaces_backend.create_ip_group(
            group_name=params.get("GroupName", ""),
            group_desc=params.get("GroupDesc", ""),
            user_rules=params.get("UserRules", []),
            tags=params.get("Tags", []),
        )
        return json.dumps({"GroupId": group_id})

    def describe_ip_groups(self) -> str:
        params = json.loads(self.body)
        group_ids = params.get("GroupIds")
        result = self.workspaces_backend.describe_ip_groups(group_ids=group_ids)
        return json.dumps({"Result": result})

    def delete_ip_group(self) -> str:
        params = json.loads(self.body)
        self.workspaces_backend.delete_ip_group(group_id=params["GroupId"])
        return "{}"

    def authorize_ip_rules(self) -> str:
        params = json.loads(self.body)
        self.workspaces_backend.authorize_ip_rules(
            group_id=params["GroupId"],
            user_rules=params.get("UserRules", []),
        )
        return "{}"

    def revoke_ip_rules(self) -> str:
        params = json.loads(self.body)
        self.workspaces_backend.revoke_ip_rules(
            group_id=params["GroupId"],
            user_rules=params.get("UserRules", []),
        )
        return "{}"

    def update_rules_of_ip_group(self) -> str:
        params = json.loads(self.body)
        self.workspaces_backend.update_rules_of_ip_group(
            group_id=params["GroupId"],
            user_rules=params.get("UserRules", []),
        )
        return "{}"

    def associate_ip_groups(self) -> str:
        params = json.loads(self.body)
        self.workspaces_backend.associate_ip_groups(
            directory_id=params["DirectoryId"],
            group_ids=params.get("GroupIds", []),
        )
        return "{}"

    def disassociate_ip_groups(self) -> str:
        params = json.loads(self.body)
        self.workspaces_backend.disassociate_ip_groups(
            directory_id=params["DirectoryId"],
            group_ids=params.get("GroupIds", []),
        )
        return "{}"

    # --- Connection Aliases ---

    def create_connection_alias(self) -> str:
        params = json.loads(self.body)
        alias_id = self.workspaces_backend.create_connection_alias(
            connection_string=params["ConnectionString"],
            tags=params.get("Tags", []),
        )
        return json.dumps({"AliasId": alias_id})

    def describe_connection_aliases(self) -> str:
        params = json.loads(self.body)
        aliases = self.workspaces_backend.describe_connection_aliases(
            alias_ids=params.get("AliasIds"),
            resource_id=params.get("ResourceId"),
        )
        return json.dumps({"ConnectionAliases": aliases})

    def delete_connection_alias(self) -> str:
        params = json.loads(self.body)
        self.workspaces_backend.delete_connection_alias(alias_id=params["AliasId"])
        return "{}"

    def associate_connection_alias(self) -> str:
        params = json.loads(self.body)
        connection_id = self.workspaces_backend.associate_connection_alias(
            alias_id=params["AliasId"],
            resource_id=params["ResourceId"],
        )
        return json.dumps({"ConnectionIdentifier": connection_id})

    def disassociate_connection_alias(self) -> str:
        params = json.loads(self.body)
        self.workspaces_backend.disassociate_connection_alias(
            alias_id=params["AliasId"],
        )
        return "{}"

    def describe_connection_alias_permissions(self) -> str:
        params = json.loads(self.body)
        alias_id, permissions = (
            self.workspaces_backend.describe_connection_alias_permissions(
                alias_id=params["AliasId"],
            )
        )
        return json.dumps(
            {"AliasId": alias_id, "ConnectionAliasPermissions": permissions}
        )

    def update_connection_alias_permission(self) -> str:
        params = json.loads(self.body)
        self.workspaces_backend.update_connection_alias_permission(
            alias_id=params["AliasId"],
            connection_alias_permission=params["ConnectionAliasPermission"],
        )
        return "{}"

    # --- Workspace Bundles ---

    def create_workspace_bundle(self) -> str:
        params = json.loads(self.body)
        bundle = self.workspaces_backend.create_workspace_bundle(
            bundle_name=params["BundleName"],
            bundle_description=params.get("BundleDescription", ""),
            image_id=params["ImageId"],
            compute_type=params["ComputeType"],
            user_storage=params["UserStorage"],
            root_storage=params.get("RootStorage"),
            tags=params.get("Tags", []),
        )
        return json.dumps({"WorkspaceBundle": bundle})

    def describe_workspace_bundles(self) -> str:
        params = json.loads(self.body)
        bundles = self.workspaces_backend.describe_workspace_bundles(
            bundle_ids=params.get("BundleIds"),
            owner=params.get("Owner"),
        )
        return json.dumps({"Bundles": bundles})

    def delete_workspace_bundle(self) -> str:
        params = json.loads(self.body)
        self.workspaces_backend.delete_workspace_bundle(
            bundle_id=params.get("BundleId", ""),
        )
        return "{}"

    def update_workspace_bundle(self) -> str:
        params = json.loads(self.body)
        self.workspaces_backend.update_workspace_bundle(
            bundle_id=params.get("BundleId", ""),
            image_id=params.get("ImageId", ""),
        )
        return "{}"

    # --- Workspace Image (additional ops) ---

    def copy_workspace_image(self) -> str:
        params = json.loads(self.body)
        image_id = self.workspaces_backend.copy_workspace_image(
            name=params["Name"],
            description=params.get("Description", ""),
            source_image_id=params["SourceImageId"],
            source_region=params["SourceRegion"],
            tags=params.get("Tags", []),
        )
        return json.dumps({"ImageId": image_id})

    def delete_workspace_image(self) -> str:
        params = json.loads(self.body)
        self.workspaces_backend.delete_workspace_image(image_id=params["ImageId"])
        return "{}"

    def create_updated_workspace_image(self) -> str:
        params = json.loads(self.body)
        image_id = self.workspaces_backend.create_updated_workspace_image(
            name=params["Name"],
            description=params.get("Description", ""),
            source_image_id=params["SourceImageId"],
            tags=params.get("Tags", []),
        )
        return json.dumps({"ImageId": image_id})

    def import_workspace_image(self) -> str:
        params = json.loads(self.body)
        image_id = self.workspaces_backend.import_workspace_image(
            ec2_image_id=params["Ec2ImageId"],
            ingestion_process=params["IngestionProcess"],
            image_name=params["ImageName"],
            image_description=params.get("ImageDescription", ""),
            tags=params.get("Tags", []),
            applications=params.get("Applications"),
        )
        return json.dumps({"ImageId": image_id})

    def import_custom_workspace_image(self) -> str:
        params = json.loads(self.body)
        image_id, state = self.workspaces_backend.import_custom_workspace_image(
            image_name=params["ImageName"],
            image_description=params.get("ImageDescription", ""),
            compute_type=params.get("ComputeType"),
            protocol=params.get("Protocol"),
            image_source=params.get("ImageSource"),
            infrastructure_configuration_arn=params.get(
                "InfrastructureConfigurationArn"
            ),
            platform=params.get("Platform"),
            os_version=params.get("OsVersion"),
            tags=params.get("Tags", []),
        )
        return json.dumps({"ImageId": image_id, "State": state})

    def describe_custom_workspace_image_import(self) -> str:
        params = json.loads(self.body)
        result = self.workspaces_backend.describe_custom_workspace_image_import(
            image_id=params["ImageId"],
        )
        return json.dumps(result)

    # --- Connect Client Add-Ins ---

    def create_connect_client_add_in(self) -> str:
        params = json.loads(self.body)
        add_in_id = self.workspaces_backend.create_connect_client_add_in(
            resource_id=params["ResourceId"],
            name=params["Name"],
            url=params["URL"],
        )
        return json.dumps({"AddInId": add_in_id})

    def describe_connect_client_add_ins(self) -> str:
        params = json.loads(self.body)
        add_ins = self.workspaces_backend.describe_connect_client_add_ins(
            resource_id=params["ResourceId"],
        )
        return json.dumps({"AddIns": add_ins})

    def delete_connect_client_add_in(self) -> str:
        params = json.loads(self.body)
        self.workspaces_backend.delete_connect_client_add_in(
            add_in_id=params["AddInId"],
            resource_id=params["ResourceId"],
        )
        return "{}"

    def update_connect_client_add_in(self) -> str:
        params = json.loads(self.body)
        self.workspaces_backend.update_connect_client_add_in(
            add_in_id=params["AddInId"],
            resource_id=params["ResourceId"],
            name=params.get("Name"),
            url=params.get("URL"),
        )
        return "{}"

    # --- Account Links ---

    def create_account_link_invitation(self) -> str:
        params = json.loads(self.body)
        account_link = self.workspaces_backend.create_account_link_invitation(
            target_account_id=params["TargetAccountId"],
            client_token=params.get("ClientToken"),
        )
        return json.dumps({"AccountLink": account_link})

    def accept_account_link_invitation(self) -> str:
        params = json.loads(self.body)
        account_link = self.workspaces_backend.accept_account_link_invitation(
            link_id=params["LinkId"],
            client_token=params.get("ClientToken"),
        )
        return json.dumps({"AccountLink": account_link})

    def reject_account_link_invitation(self) -> str:
        params = json.loads(self.body)
        account_link = self.workspaces_backend.reject_account_link_invitation(
            link_id=params["LinkId"],
            client_token=params.get("ClientToken"),
        )
        return json.dumps({"AccountLink": account_link})

    def delete_account_link_invitation(self) -> str:
        params = json.loads(self.body)
        account_link = self.workspaces_backend.delete_account_link_invitation(
            link_id=params["LinkId"],
            client_token=params.get("ClientToken"),
        )
        return json.dumps({"AccountLink": account_link})

    def get_account_link(self) -> str:
        params = json.loads(self.body)
        account_link = self.workspaces_backend.get_account_link(
            link_id=params.get("LinkId"),
            linked_account_id=params.get("LinkedAccountId"),
        )
        return json.dumps({"AccountLink": account_link})

    def list_account_links(self) -> str:
        params = json.loads(self.body)
        links = self.workspaces_backend.list_account_links(
            link_status_filter=params.get("LinkStatusFilter"),
        )
        return json.dumps({"AccountLinks": links})

    # --- Workspace Pools ---

    def create_workspaces_pool(self) -> str:
        params = json.loads(self.body)
        pool = self.workspaces_backend.create_workspaces_pool(
            pool_name=params["PoolName"],
            description=params.get("Description", ""),
            bundle_id=params["BundleId"],
            directory_id=params["DirectoryId"],
            capacity=params["Capacity"],
            tags=params.get("Tags", []),
            application_settings=params.get("ApplicationSettings"),
            timeout_settings=params.get("TimeoutSettings"),
            running_mode=params.get("RunningMode"),
        )
        return json.dumps({"WorkspacesPool": pool})

    def describe_workspaces_pools(self) -> str:
        params = json.loads(self.body)
        pools = self.workspaces_backend.describe_workspaces_pools(
            pool_ids=params.get("PoolIds"),
            filters=params.get("Filters"),
        )
        return json.dumps({"WorkspacesPools": pools})

    def update_workspaces_pool(self) -> str:
        params = json.loads(self.body)
        pool = self.workspaces_backend.update_workspaces_pool(
            pool_id=params["PoolId"],
            description=params.get("Description"),
            bundle_id=params.get("BundleId"),
            directory_id=params.get("DirectoryId"),
            capacity=params.get("Capacity"),
            application_settings=params.get("ApplicationSettings"),
            timeout_settings=params.get("TimeoutSettings"),
            running_mode=params.get("RunningMode"),
        )
        return json.dumps({"WorkspacesPool": pool})

    def terminate_workspaces_pool(self) -> str:
        params = json.loads(self.body)
        self.workspaces_backend.terminate_workspaces_pool(pool_id=params["PoolId"])
        return "{}"

    def start_workspaces_pool(self) -> str:
        params = json.loads(self.body)
        self.workspaces_backend.start_workspaces_pool(pool_id=params["PoolId"])
        return "{}"

    def stop_workspaces_pool(self) -> str:
        params = json.loads(self.body)
        self.workspaces_backend.stop_workspaces_pool(pool_id=params["PoolId"])
        return "{}"

    def describe_workspaces_pool_sessions(self) -> str:
        params = json.loads(self.body)
        sessions = self.workspaces_backend.describe_workspaces_pool_sessions(
            pool_id=params["PoolId"],
            user_id=params.get("UserId"),
        )
        return json.dumps({"Sessions": sessions})

    def terminate_workspaces_pool_session(self) -> str:
        params = json.loads(self.body)
        self.workspaces_backend.terminate_workspaces_pool_session(
            session_id=params["SessionId"],
        )
        return "{}"

    # --- Workspace State Operations ---

    def start_workspaces(self) -> str:
        params = json.loads(self.body)
        failed = self.workspaces_backend.start_workspaces(
            start_workspace_requests=params["StartWorkspaceRequests"],
        )
        return json.dumps({"FailedRequests": failed})

    def stop_workspaces(self) -> str:
        params = json.loads(self.body)
        failed = self.workspaces_backend.stop_workspaces(
            stop_workspace_requests=params["StopWorkspaceRequests"],
        )
        return json.dumps({"FailedRequests": failed})

    def reboot_workspaces(self) -> str:
        params = json.loads(self.body)
        failed = self.workspaces_backend.reboot_workspaces(
            reboot_workspace_requests=params["RebootWorkspaceRequests"],
        )
        return json.dumps({"FailedRequests": failed})

    def rebuild_workspaces(self) -> str:
        params = json.loads(self.body)
        failed = self.workspaces_backend.rebuild_workspaces(
            rebuild_workspace_requests=params["RebuildWorkspaceRequests"],
        )
        return json.dumps({"FailedRequests": failed})

    def modify_workspace_properties(self) -> str:
        params = json.loads(self.body)
        self.workspaces_backend.modify_workspace_properties(
            workspace_id=params["WorkspaceId"],
            workspace_properties=params.get("WorkspaceProperties"),
            data_replication=params.get("DataReplication"),
        )
        return "{}"

    def modify_workspace_state(self) -> str:
        params = json.loads(self.body)
        self.workspaces_backend.modify_workspace_state(
            workspace_id=params["WorkspaceId"],
            workspace_state=params["WorkspaceState"],
        )
        return "{}"

    def restore_workspace(self) -> str:
        params = json.loads(self.body)
        self.workspaces_backend.restore_workspace(
            workspace_id=params["WorkspaceId"],
        )
        return "{}"

    def migrate_workspace(self) -> str:
        params = json.loads(self.body)
        source_id, target_id = self.workspaces_backend.migrate_workspace(
            source_workspace_id=params["SourceWorkspaceId"],
            bundle_id=params["BundleId"],
        )
        return json.dumps(
            {"SourceWorkspaceId": source_id, "TargetWorkspaceId": target_id}
        )

    def describe_workspaces_connection_status(self) -> str:
        params = json.loads(self.body)
        statuses = self.workspaces_backend.describe_workspaces_connection_status(
            workspace_ids=params.get("WorkspaceIds"),
        )
        return json.dumps({"WorkspacesConnectionStatus": statuses})

    def describe_workspace_snapshots(self) -> str:
        params = json.loads(self.body)
        rebuild, restore = self.workspaces_backend.describe_workspace_snapshots(
            workspace_id=params["WorkspaceId"],
        )
        return json.dumps(
            {"RebuildSnapshots": rebuild, "RestoreSnapshots": restore}
        )

    def create_standby_workspaces(self) -> str:
        params = json.loads(self.body)
        failed, pending = self.workspaces_backend.create_standby_workspaces(
            primary_region=params["PrimaryRegion"],
            standby_workspaces=params["StandbyWorkspaces"],
        )
        return json.dumps(
            {
                "FailedStandbyRequests": failed,
                "PendingStandbyRequests": pending,
            }
        )

    # --- Directory Modification Ops ---

    def modify_workspace_access_properties(self) -> str:
        params = json.loads(self.body)
        self.workspaces_backend.modify_workspace_access_properties(
            resource_id=params["ResourceId"],
            workspace_access_properties=params["WorkspaceAccessProperties"],
        )
        return "{}"

    def modify_saml_properties(self) -> str:
        params = json.loads(self.body)
        self.workspaces_backend.modify_saml_properties(
            resource_id=params["ResourceId"],
            saml_properties=params.get("SamlProperties"),
            properties_to_delete=params.get("PropertiesToDelete"),
        )
        return "{}"

    def modify_certificate_based_auth_properties(self) -> str:
        params = json.loads(self.body)
        self.workspaces_backend.modify_certificate_based_auth_properties(
            resource_id=params["ResourceId"],
            certificate_based_auth_properties=params.get(
                "CertificateBasedAuthProperties"
            ),
            properties_to_delete=params.get("PropertiesToDelete"),
        )
        return "{}"

    def modify_streaming_properties(self) -> str:
        params = json.loads(self.body)
        self.workspaces_backend.modify_streaming_properties(
            resource_id=params["ResourceId"],
            streaming_properties=params.get("StreamingProperties"),
        )
        return "{}"

    def modify_endpoint_encryption_mode(self) -> str:
        params = json.loads(self.body)
        self.workspaces_backend.modify_endpoint_encryption_mode(
            directory_id=params["DirectoryId"],
            endpoint_encryption_mode=params["EndpointEncryptionMode"],
        )
        return "{}"

    # --- Account Operations ---

    def describe_account(self) -> str:
        result = self.workspaces_backend.describe_account()
        return json.dumps(result)

    def modify_account(self) -> str:
        params = json.loads(self.body)
        self.workspaces_backend.modify_account(
            dedicated_tenancy_support=params.get("DedicatedTenancySupport"),
            dedicated_tenancy_management_cidr_range=params.get(
                "DedicatedTenancyManagementCidrRange"
            ),
        )
        return "{}"

    def describe_account_modifications(self) -> str:
        modifications = self.workspaces_backend.describe_account_modifications()
        return json.dumps({"AccountModifications": modifications})

    # --- Client Branding ---

    def import_client_branding(self) -> str:
        params = json.loads(self.body)
        resource_id = params.get("ResourceId")
        branding_info = {}
        for key in [
            "DeviceTypeWindows",
            "DeviceTypeOsx",
            "DeviceTypeAndroid",
            "DeviceTypeIos",
            "DeviceTypeLinux",
            "DeviceTypeWeb",
        ]:
            if key in params:
                branding_info[key] = params[key]
        result = self.workspaces_backend.import_client_branding(
            resource_id=resource_id,
            branding_info=branding_info,
        )
        return json.dumps(result)

    def describe_client_branding(self) -> str:
        params = json.loads(self.body)
        result = self.workspaces_backend.describe_client_branding(
            resource_id=params["ResourceId"],
        )
        return json.dumps(result)

    def delete_client_branding(self) -> str:
        params = json.loads(self.body)
        self.workspaces_backend.delete_client_branding(
            resource_id=params["ResourceId"],
            platforms=params.get("Platforms", []),
        )
        return "{}"

    # --- Application Associations ---

    def associate_workspace_application(self) -> str:
        params = json.loads(self.body)
        result = self.workspaces_backend.associate_workspace_application(
            workspace_id=params["WorkspaceId"],
            application_id=params["ApplicationId"],
        )
        return json.dumps({"Association": result})

    def disassociate_workspace_application(self) -> str:
        params = json.loads(self.body)
        result = self.workspaces_backend.disassociate_workspace_application(
            workspace_id=params["WorkspaceId"],
            application_id=params["ApplicationId"],
        )
        return json.dumps({"Association": result})

    def deploy_workspace_applications(self) -> str:
        params = json.loads(self.body)
        result = self.workspaces_backend.deploy_workspace_applications(
            workspace_id=params["WorkspaceId"],
            force=params.get("Force"),
        )
        return json.dumps(result)

    def describe_application_associations(self) -> str:
        params = json.loads(self.body)
        result = self.workspaces_backend.describe_application_associations(
            application_id=params["ApplicationId"],
            associated_resource_types=params["AssociatedResourceTypes"],
        )
        return json.dumps({"Associations": result})

    def describe_applications(self) -> str:
        params = json.loads(self.body)
        result = self.workspaces_backend.describe_applications(
            application_ids=params.get("ApplicationIds"),
            compute_type_names=params.get("ComputeTypeNames"),
            license_type=params.get("LicenseType"),
            operating_system_names=params.get("OperatingSystemNames"),
            owner=params.get("Owner"),
        )
        return json.dumps({"Applications": result})

    def describe_bundle_associations(self) -> str:
        params = json.loads(self.body)
        result = self.workspaces_backend.describe_bundle_associations(
            bundle_id=params["BundleId"],
            associated_resource_types=params["AssociatedResourceTypes"],
        )
        return json.dumps({"Associations": result})

    def describe_image_associations(self) -> str:
        params = json.loads(self.body)
        result = self.workspaces_backend.describe_image_associations(
            image_id=params["ImageId"],
            associated_resource_types=params["AssociatedResourceTypes"],
        )
        return json.dumps({"Associations": result})

    def describe_workspace_associations(self) -> str:
        params = json.loads(self.body)
        result = self.workspaces_backend.describe_workspace_associations(
            workspace_id=params["WorkspaceId"],
            associated_resource_types=params["AssociatedResourceTypes"],
        )
        return json.dumps({"Associations": result})

    # --- Management CIDR Ranges ---

    def list_available_management_cidr_ranges(self) -> str:
        params = json.loads(self.body)
        ranges = self.workspaces_backend.list_available_management_cidr_ranges(
            management_cidr_range_constraint=params["ManagementCidrRangeConstraint"],
        )
        return json.dumps({"ManagementCidrRanges": ranges})
