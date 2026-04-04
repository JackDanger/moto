"""WorkSpacesBackend class with methods for supported APIs."""

import re
from collections.abc import Mapping
from typing import Any, Optional

from moto.core.base_backend import BackendDict, BaseBackend
from moto.core.common_models import BaseModel
from moto.core.utils import unix_time
from moto.ds import ds_backends
from moto.ds.models import Directory
from moto.ec2 import ec2_backends
from moto.moto_api._internal import mock_random
from moto.utilities.utils import get_partition
from moto.workspaces.exceptions import (
    InvalidParameterValuesException,
    ResourceAlreadyExistsException,
    ResourceNotFoundException,
    ValidationException,
)


class Workspace(BaseModel):
    def __init__(
        self,
        workspace: dict[str, Any],
        running_mode: str,
        error_code: str,
        error_msg: str,
    ):
        self.workspace_properties: dict[str, Any]
        self.workspace = workspace
        self.workspace_id = f"ws-{mock_random.get_random_hex(9)}"
        # Create_workspaces operation is asynchronous and returns before the WorkSpaces are created.
        # Initially the 'state' is 'PENDING', but here the 'state' will be set as 'AVAILABLE' since
        # this operation is being mocked.
        self.directory_id = workspace["DirectoryId"]
        self.bundle_id = workspace["BundleId"]
        self.user_name = workspace["UserName"]
        self.state = "AVAILABLE"
        self.error_message = error_msg or ""
        self.error_code = error_code or ""
        self.volume_encryption_key = workspace.get("VolumeEncryptionKey", "")
        self.user_volume_encryption_enabled = workspace.get(
            "UserVolumeEncryptionEnabled", ""
        )
        self.root_volume_encryption_enabled = workspace.get(
            "RootVolumeEncryptionEnabled", ""
        )
        workspace_properties = {"RunningMode": running_mode}
        self.workspace_properties = workspace.get("WorkspaceProperties", "")

        if self.workspace_properties:
            self.workspace_properties["RunningMode"] = running_mode
        else:
            self.workspace_properties = workspace_properties

        self.computer_name = ""  # Workspace Bundle
        self.modification_states: list[
            dict[str, str]
        ] = []  # modify_workspace_properties
        # create_standy_workspace
        self.related_workspaces: list[dict[str, str]] = []
        self.data_replication_settings: dict[str, Any] = {}
        # The properties of the standby WorkSpace related to related_workspaces
        self.standby_workspaces_properties: list[dict[str, Any]] = []
        self.tags = workspace.get("Tags", [])

    def to_dict_pending(self) -> dict[str, Any]:
        dct = {
            "WorkspaceId": self.workspace_id,
            "DirectoryId": self.directory_id,
            "UserName": self.user_name,
            "IpAddress": "",  # UnKnown
            "State": self.state,
            "BundleId": self.bundle_id,
            "SubnetId": "",  # UnKnown
            "ErrorMessage": self.error_message,
            "ErrorCode": self.error_code,
            "ComputerName": self.computer_name,
            "VolumeEncryptionKey": self.volume_encryption_key,
            "UserVolumeEncryptionEnabled": self.user_volume_encryption_enabled,
            "RootVolumeEncryptionEnabled": self.root_volume_encryption_enabled,
            "WorkspaceProperties": self.workspace_properties,
            "ModificationStates": self.modification_states,
            "RelatedWorkspaces": self.related_workspaces,
            "DataReplicationSettings": self.data_replication_settings,
            "StandbyWorkspacesProperties": self.standby_workspaces_properties,
        }
        return {k: v for k, v in dct.items() if v}

    def filter_empty_values(self, d: dict[str, Any]) -> dict[str, Any]:
        if isinstance(d, Mapping):
            return {k: self.filter_empty_values(v) for k, v in d.items() if v}
        else:
            return d

    def to_dict_failed(self) -> dict[str, Any]:
        dct = {
            "WorkspaceRequest": {
                "DirectoryId": self.workspace["DirectoryId"],
                "UserName": self.workspace["UserName"],
                "BundleId": self.workspace["BundleId"],
                "SubnetId": "",  # UnKnown
                "VolumeEncryptionKey": self.volume_encryption_key,
                "UserVolumeEncryptionEnabled": self.user_volume_encryption_enabled,
                "RootVolumeEncryptionEnabled": self.root_volume_encryption_enabled,
                "WorkspaceProperties": self.workspace_properties,
                "Tags": self.tags,
            },
            "ErrorCode": self.error_code,
            "ErrorMessage": self.error_message,
        }
        return self.filter_empty_values(dct)


class WorkSpaceDirectory(BaseModel):
    def __init__(
        self,
        account_id: str,
        region: str,
        directory: Directory,
        registration_code: str,
        security_group_id: str,
        subnet_ids: list[str],
        enable_self_service: bool,
        tenancy: str,
        tags: list[dict[str, str]],
    ):
        self.account_id = account_id
        self.region = region
        self.directory_id = directory.directory_id
        self.alias = directory.alias
        self.directory_name = directory.name
        self.launch_time = directory.launch_time
        self.registration_code = registration_code
        if directory.directory_type == "ADConnector":
            dir_subnet_ids = directory.connect_settings["SubnetIds"]  # type: ignore[index]
        else:
            dir_subnet_ids = directory.vpc_settings["SubnetIds"]  # type: ignore[index]
        self.subnet_ids = subnet_ids or dir_subnet_ids
        self.dns_ip_addresses = directory.dns_ip_addrs
        self.customer_username = "Administrator"
        self.iam_rold_id = (
            f"arn:{get_partition(region)}:iam::{account_id}:role/workspaces_DefaultRole"
        )
        dir_type = directory.directory_type
        if dir_type == "ADConnector":
            self.directory_type = "AD_CONNECTOR"
        elif dir_type == "SimpleAD":
            self.directory_type = "SIMPLE_AD"
        else:
            self.directory_type = dir_type
        self.workspace_security_group_id = security_group_id
        self.state = "REGISTERED"
        # Default values for workspace_creation_properties
        workspace_creation_properties = {
            "EnableInternetAccess": False,
            "DefaultOu": "",
            "CustomSecurityGroupId": "",
            "UserEnabledAsLocalAdministrator": (
                True if self.customer_username == "Administrator" else False
            ),
            "EnableMaintenanceMode": True,
        }
        # modify creation properites
        self.workspace_creation_properties = workspace_creation_properties
        self.ip_group_ids: list[str] = []
        # Default values for workspace access properties
        workspace_access_properties = {
            "DeviceTypeWindows": (
                "DENY" if self.directory_type == "AD_CONNECTOR" else "ALLOW"
            ),
            "DeviceTypeOsx": "ALLOW",
            "DeviceTypeWeb": "DENY",
            "DeviceTypeIos": "ALLOW",
            "DeviceTypeAndroid": "ALLOW",
            "DeviceTypeChromeOs": "ALLOW",
            "DeviceTypeZeroClient": (
                "DENY" if self.directory_type == "AD_CONNECTOR" else "ALLOW"
            ),
            "DeviceTypeLinux": "DENY",
        }
        # modify_workspace_access_properties
        self.workspace_access_properties = workspace_access_properties
        self.tenancy = tenancy or "SHARED"

        # Default values for self service permissions
        mode = "DISABLED"
        if enable_self_service:
            mode = "ENABLED"
        self_service_permissions = {
            "RestartWorkspace": "ENABLED",
            "IncreaseVolumeSize": mode,
            "ChangeComputeType": mode,
            "SwitchRunningMode": mode,
            "RebuildWorkspace": mode,
        }
        self.self_service_permissions = self_service_permissions
        # Default values for saml properties
        saml_properties = {
            "Status": "DISABLED",
            "UserAccessUrl": "",
            "RelayStateParameterName": "RelayState",
        }
        self.saml_properties = saml_properties
        # Default values for certificate bases auth properties
        self.certificate_based_auth_properties: dict[str, str] = {
            "Status": "DISABLED",
        }
        # ModifyCertificateBasedAuthProperties
        self.tags = tags or []
        client_properties = {
            # Log uploading is enabled by default.
            "ReconnectEnabled": "ENABLED",
            "LogUploadEnabled": "ENABLED",  # Remember me is enabled by default
        }
        self.client_properties = client_properties
        self.streaming_properties: dict[str, Any] = {}
        self.endpoint_encryption_mode: str = ""

    def delete_security_group(self) -> None:
        """Delete the given security group."""
        ec2_backends[self.account_id][self.region].delete_security_group(
            group_id=self.workspace_security_group_id
        )

    def to_dict(self) -> dict[str, Any]:
        dct = {
            "DirectoryId": self.directory_id,
            "Alias": self.alias,
            "DirectoryName": self.directory_name,
            "RegistrationCode": self.registration_code,
            "SubnetIds": self.subnet_ids,
            "DnsIpAddresses": self.dns_ip_addresses,
            "CustomerUserName": self.customer_username,
            "IamRoleId": self.iam_rold_id,
            "DirectoryType": self.directory_type,
            "WorkspaceSecurityGroupId": self.workspace_security_group_id,
            "State": self.state,
            "WorkspaceCreationProperties": self.workspace_creation_properties,
            "ipGroupIds": self.ip_group_ids,
            "WorkspaceAccessProperties": self.workspace_access_properties,
            "Tenancy": self.tenancy,
            "SelfservicePermissions": self.self_service_permissions,
            "SamlProperties": self.saml_properties,
            "CertificateBasedAuthProperties": self.certificate_based_auth_properties,
        }
        return {k: v for k, v in dct.items() if v}


class WorkspaceImage(BaseModel):
    def __init__(
        self,
        name: str,
        description: str,
        tags: list[dict[str, str]],
        account_id: str,
    ):
        self.image_id = f"wsi-{mock_random.get_random_hex(9)}"
        self.name = name
        self.description = description
        self.operating_system: dict[str, str] = {}  # Unknown
        # Initially the 'state' is 'PENDING', but here the 'state' will be set as 'AVAILABLE' since
        # this operation is being mocked.
        self.state = "AVAILABLE"
        self.required_tenancy = "DEFAULT"
        self.created = unix_time()
        self.owner_account = account_id
        self.error_code = ""
        self.error_message = ""
        self.image_permissions: list[dict[str, str]] = []
        self.tags = tags or []

        # Default updates
        self.updates = {
            "UpdateAvailable": False,
            "Description": "This WorkSpace image does not have updates available",
        }
        self.error_details: list[dict[str, str]] = []

    def to_dict(self) -> dict[str, Any]:
        dct = {
            "ImageId": self.image_id,
            "Name": self.name,
            "Description": self.description,
            "OperatingSystem": self.operating_system,
            "State": self.state,
            "RequiredTenancy": self.required_tenancy,
            "Created": self.created,
            "OwnerAccountId": self.owner_account,
        }
        return {k: v for k, v in dct.items() if v}

    def to_desc_dict(self) -> dict[str, Any]:
        dct = self.to_dict()
        dct_options = {
            "ErrorCode": self.error_code,
            "ErrorMessage": self.error_message,
            "Updates": self.updates,
            "ErrorDetails": self.error_details,
        }
        for key, value in dct_options.items():
            if value is not None:
                dct[key] = value
        return dct


class IpGroup(BaseModel):
    def __init__(
        self,
        group_name: str,
        group_desc: str,
        user_rules: list[dict[str, str]],
        tags: list[dict[str, str]],
    ):
        self.group_id = f"wsipg-{mock_random.get_random_hex(9)}"
        self.group_name = group_name
        self.group_desc = group_desc or ""
        self.user_rules = user_rules or []
        self.tags = tags or []

    def to_dict(self) -> dict[str, Any]:
        return {
            "groupId": self.group_id,
            "groupName": self.group_name,
            "groupDesc": self.group_desc,
            "userRules": self.user_rules,
        }


class ConnectionAlias(BaseModel):
    def __init__(
        self,
        connection_string: str,
        tags: list[dict[str, str]],
        account_id: str,
        region: str,
    ):
        self.alias_id = f"wsca-{mock_random.get_random_hex(9)}"
        self.connection_string = connection_string
        self.state = "CREATED"
        self.owner_account_id = account_id
        self.associations: list[dict[str, str]] = []
        self.tags = tags or []
        self.region = region
        self.permissions: list[dict[str, Any]] = []

    def to_dict(self) -> dict[str, Any]:
        dct: dict[str, Any] = {
            "AliasId": self.alias_id,
            "ConnectionString": self.connection_string,
            "State": self.state,
            "OwnerAccountId": self.owner_account_id,
            "Associations": self.associations,
        }
        return {k: v for k, v in dct.items() if v is not None}


class WorkspaceBundle(BaseModel):
    def __init__(
        self,
        bundle_name: str,
        bundle_description: str,
        image_id: str,
        compute_type: dict[str, str],
        user_storage: dict[str, str],
        root_storage: Optional[dict[str, str]],
        tags: list[dict[str, str]],
        account_id: str,
    ):
        self.bundle_id = f"wsb-{mock_random.get_random_hex(9)}"
        self.name = bundle_name
        self.description = bundle_description or ""
        self.image_id = image_id
        self.compute_type = compute_type
        self.user_storage = user_storage
        self.root_storage = root_storage or {}
        self.tags = tags or []
        self.owner = account_id
        self.state = "AVAILABLE"
        self.creation_time = unix_time()
        self.last_updated_time = unix_time()

    def to_dict(self) -> dict[str, Any]:
        dct: dict[str, Any] = {
            "BundleId": self.bundle_id,
            "Name": self.name,
            "Owner": self.owner,
            "Description": self.description,
            "ImageId": self.image_id,
            "ComputeType": self.compute_type,
            "UserStorage": self.user_storage,
            "RootStorage": self.root_storage,
            "State": self.state,
            "CreationTime": self.creation_time,
            "LastUpdatedTime": self.last_updated_time,
        }
        return {k: v for k, v in dct.items() if v}


class ConnectClientAddIn(BaseModel):
    def __init__(
        self,
        resource_id: str,
        name: str,
        url: str,
    ):
        self.add_in_id = str(mock_random.uuid4())
        self.resource_id = resource_id
        self.name = name
        self.url = url

    def to_dict(self) -> dict[str, Any]:
        return {
            "AddInId": self.add_in_id,
            "ResourceId": self.resource_id,
            "Name": self.name,
            "URL": self.url,
        }


class AccountLink(BaseModel):
    def __init__(
        self,
        source_account_id: str,
        target_account_id: str,
    ):
        self.link_id = f"wsal-{mock_random.get_random_hex(9)}"
        self.link_status = "LINKED"
        self.source_account_id = source_account_id
        self.target_account_id = target_account_id

    def to_dict(self) -> dict[str, Any]:
        return {
            "AccountLinkId": self.link_id,
            "AccountLinkStatus": self.link_status,
            "SourceAccountId": self.source_account_id,
            "TargetAccountId": self.target_account_id,
        }


class WorkspacesPool(BaseModel):
    def __init__(
        self,
        pool_name: str,
        description: str,
        bundle_id: str,
        directory_id: str,
        capacity: dict[str, int],
        tags: list[dict[str, str]],
        application_settings: Optional[dict[str, Any]],
        timeout_settings: Optional[dict[str, Any]],
        running_mode: Optional[str],
        account_id: str,
        region: str,
    ):
        self.pool_id = f"wsp-{mock_random.get_random_hex(9)}"
        self.pool_name = pool_name
        self.description = description or ""
        self.bundle_id = bundle_id
        self.directory_id = directory_id
        self.capacity = capacity
        self.tags = tags or []
        self.application_settings = application_settings or {}
        self.timeout_settings = timeout_settings or {}
        self.running_mode = running_mode or "AUTO_STOP"
        self.state = "AVAILABLE"
        self.created_at = unix_time()
        self.account_id = account_id
        self.region = region
        self.pool_arn = (
            f"arn:{get_partition(region)}:workspaces:{region}:{account_id}:workspacespool/{self.pool_id}"
        )
        self.errors: list[dict[str, str]] = []
        # Track sessions
        self.sessions: list[dict[str, Any]] = []

    def to_dict(self) -> dict[str, Any]:
        dct: dict[str, Any] = {
            "PoolId": self.pool_id,
            "PoolArn": self.pool_arn,
            "CapacityStatus": {
                "AvailableUserSessions": self.capacity.get("DesiredUserSessions", 1),
                "DesiredUserSessions": self.capacity.get("DesiredUserSessions", 1),
                "ActualUserSessions": 0,
                "ActiveUserSessions": 0,
            },
            "PoolName": self.pool_name,
            "Description": self.description,
            "State": self.state,
            "CreatedAt": self.created_at,
            "BundleId": self.bundle_id,
            "DirectoryId": self.directory_id,
            "Errors": self.errors,
        }
        if self.application_settings:
            dct["ApplicationSettings"] = self.application_settings
        if self.timeout_settings:
            dct["TimeoutSettings"] = self.timeout_settings
        return dct


class WorkSpacesBackend(BaseBackend):
    """Implementation of WorkSpaces APIs."""

    # The assumption here is that the limits are the same for all regions.
    DIRECTORIES_LIMIT = 50

    def __init__(self, region_name: str, account_id: str):
        super().__init__(region_name, account_id)
        self.workspaces: dict[str, Workspace] = {}
        self.workspace_directories: dict[str, WorkSpaceDirectory] = {}
        self.workspace_images: dict[str, WorkspaceImage] = {}
        self.ip_groups: dict[str, IpGroup] = {}
        self.connection_aliases: dict[str, ConnectionAlias] = {}
        self.workspace_bundles: dict[str, WorkspaceBundle] = {}
        self.connect_client_add_ins: dict[str, ConnectClientAddIn] = {}
        self.account_links: dict[str, AccountLink] = {}
        self.workspaces_pools: dict[str, WorkspacesPool] = {}
        self.directories: list[Directory]
        # Account-level settings
        self.dedicated_tenancy_support: str = ""
        self.dedicated_tenancy_management_cidr_range: str = ""
        self.account_modifications: list[dict[str, Any]] = []

    def validate_directory_id(self, value: str, msg: str) -> None:
        """Raise exception if the directory id is invalid."""
        id_pattern = r"^d-[0-9a-f]{10}$"
        if not re.match(id_pattern, value):
            raise ValidationException(msg)

    def validate_image_id(self, value: str, msg: str) -> None:
        """Raise exception if the image id is invalid."""
        id_pattern = r"^wsi-[0-9a-z]{9}$"
        if not re.match(id_pattern, value):
            raise ValidationException(msg)

    def _get_resource_tags(self, resource_id: str) -> list[dict[str, str]]:
        """Get tags for any resource type by prefix."""
        if resource_id.startswith("d-"):
            if resource_id in self.workspace_directories:
                return self.workspace_directories[resource_id].tags
        elif resource_id.startswith("ws-"):
            if resource_id in self.workspaces:
                return self.workspaces[resource_id].tags
        elif resource_id.startswith("wsi-"):
            if resource_id in self.workspace_images:
                return self.workspace_images[resource_id].tags
        elif resource_id.startswith("wsipg-"):
            if resource_id in self.ip_groups:
                return self.ip_groups[resource_id].tags
        elif resource_id.startswith("wsca-"):
            if resource_id in self.connection_aliases:
                return self.connection_aliases[resource_id].tags
        elif resource_id.startswith("wsb-"):
            if resource_id in self.workspace_bundles:
                return self.workspace_bundles[resource_id].tags
        elif resource_id.startswith("wsp-"):
            if resource_id in self.workspaces_pools:
                return self.workspaces_pools[resource_id].tags
        return []

    def create_security_group(self, directory_id: str, vpc_id: str) -> str:
        """Create security group for the workspace directory."""
        security_group_info = ec2_backends[self.account_id][
            self.region_name
        ].create_security_group(
            name=f"{directory_id}_workspacesMembers",
            description=("Amazon WorkSpaces Security Group"),
            vpc_id=vpc_id,
        )
        return security_group_info.id

    def create_workspaces(
        self, workspaces: list[dict[str, Any]]
    ) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
        failed_requests = []
        pending_requests = []

        for ws in workspaces:
            error_code = ""
            error_msg = ""
            directory_id = ws["DirectoryId"]
            msg = f"The Directory ID {directory_id} in the request is invalid."
            self.validate_directory_id(directory_id, msg)

            # FailedRequests are created if the directory_id is unknown
            if directory_id not in self.workspace_directories:
                error_code = "ResourceNotFound.Directory"
                error_msg = "The specified directory could not be found in the specified region."

            running_mode = "ALWAYS_ON"
            workspace_properties = ws.get("WorkspaceProperties", "")
            if workspace_properties:
                running_mode = workspace_properties.get("RunningMode", running_mode)
                auto_stop_timeout = workspace_properties.get(
                    "RunningModeAutoStopTimeoutInMinutes", ""
                )

                # Requests fail if AutoStopTimeout is given for an AlwaysOn Running mode
                if auto_stop_timeout and running_mode == "ALWAYS_ON":
                    error_code = "AutoStopTimeoutIsNotApplicableForAnAlwaysOnWorkspace"
                    error_msg = "RunningModeAutoStopTimeoutInMinutes is not applicable for WorkSpace with running mode set to ALWAYS_ON."

                # Requests fail if AutoStopTimeout is given for an Manual Running mode
                if auto_stop_timeout and running_mode == "MANUAL":
                    error_code = "AutoStopTimeoutIsNotDefaultForManualWorkspace"

            workspace = Workspace(
                workspace=ws,
                running_mode=running_mode,
                error_code=error_code,
                error_msg=error_msg,
            )
            if error_code:
                failed_requests.append(workspace.to_dict_failed())
            else:
                pending_requests.append(workspace.to_dict_pending())
                self.workspaces[workspace.workspace_id] = workspace

        return failed_requests, pending_requests

    def describe_workspaces(
        self,
        workspace_ids: list[str],
        directory_id: str,
        user_name: str,
        bundle_id: str,
    ) -> list[Workspace]:
        # Pagination not yet implemented

        # Only one of the following are allowed to be specified: BundleId, DirectoryId, WorkSpaceIds.
        if (
            (workspace_ids and directory_id)
            or (directory_id and bundle_id)
            or (workspace_ids and bundle_id)
        ):
            msg = "An invalid number of parameters provided with DescribeWorkspaces. Only one of the following are allowed to be specified: BundleId, DirectoryId, WorkSpaceIds, Filters."
            raise InvalidParameterValuesException(msg)

        # Directory_id parameter is required when Username is given.
        if user_name and not directory_id:
            msg = "The DirectoryId parameter is required when UserName is used."
            raise InvalidParameterValuesException(msg)

        workspaces = list(self.workspaces.values())
        if workspace_ids:
            workspaces = [x for x in workspaces if x.workspace_id in workspace_ids]
        if directory_id:
            workspaces = [x for x in workspaces if x.directory_id == directory_id]
        if directory_id and user_name:
            workspaces = [
                x
                for x in workspaces
                if (x.directory_id == directory_id) and (x.user_name == user_name)
            ]
        if bundle_id:
            workspaces = [x for x in workspaces if x.bundle_id == bundle_id]
        return workspaces

    def terminate_workspaces(
        self, terminate_workspace_requests: list[dict[str, Any]]
    ) -> dict[str, list[dict[str, Any]]]:
        failed_requests = []

        for ws in terminate_workspace_requests:
            workspace_id = ws["WorkspaceId"]
            if workspace_id not in self.workspaces:
                failed_requests.append(
                    {
                        "WorkspaceId": workspace_id,
                        "ErrorCode": "400",
                        "ErrorMessage": f"WorkSpace {workspace_id} could not be found.",
                    }
                )
                continue

            self.workspaces.pop(workspace_id)

        return {
            "FailedRequests": failed_requests,
        }

    def register_workspace_directory(
        self,
        directory_id: str,
        subnet_ids: list[str],
        enable_self_service: bool,
        tenancy: str,
        tags: list[dict[str, str]],
    ) -> None:
        ran_str = mock_random.get_random_string(length=6)
        registration_code = f"SLiad+{ran_str.upper()}"

        (self.directories, _) = ds_backends[self.account_id][
            self.region_name
        ].describe_directories(directory_ids=[directory_id])
        directory = self.directories[0]

        if directory.directory_type == "ADConnector":
            vpc_id = directory.connect_settings["VpcId"]  # type: ignore[index]
        else:
            vpc_id = directory.vpc_settings["VpcId"]  # type: ignore[index]

        security_group_id = self.create_security_group(directory_id, vpc_id)

        workspace_directory = WorkSpaceDirectory(
            account_id=self.account_id,
            region=self.region_name,
            directory=directory,
            registration_code=registration_code,
            security_group_id=security_group_id,
            subnet_ids=subnet_ids,
            enable_self_service=enable_self_service,
            tenancy=tenancy,
            tags=tags,
        )
        self.workspace_directories[workspace_directory.directory_id] = (
            workspace_directory
        )

    def describe_workspace_directories(
        self, directory_ids: Optional[list[str]] = None
    ) -> list[WorkSpaceDirectory]:
        """Return info on all directories or directories with matching IDs."""
        # Pagination not yet implemented

        workspace_directories = list(self.workspace_directories.values())
        if directory_ids:
            for d in directory_ids:
                msg = "The request is invalid."
                self.validate_directory_id(d, msg)
            workspace_directories = [
                x for x in workspace_directories if x.directory_id in directory_ids
            ]

        return sorted(workspace_directories, key=lambda x: x.launch_time)

    def modify_workspace_creation_properties(
        self, resource_id: str, workspace_creation_properties: dict[str, Any]
    ) -> None:
        # Raise Exception if Directory doesnot exist.
        if resource_id not in self.workspace_directories:
            raise ValidationException("The request is invalid.")

        res = self.workspace_directories[resource_id]
        res.workspace_creation_properties = workspace_creation_properties

    def create_tags(self, resource_id: str, tags: list[dict[str, str]]) -> None:
        if resource_id.startswith("d-"):
            ds = self.workspace_directories[resource_id]
            ds.tags.extend(tags)
        elif resource_id.startswith("ws-"):
            ws = self.workspaces[resource_id]
            ws.tags.extend(tags)
        elif resource_id.startswith("wsi-"):
            wsi = self.workspace_images[resource_id]
            wsi.tags.extend(tags)
        elif resource_id.startswith("wsipg-"):
            grp = self.ip_groups[resource_id]
            grp.tags.extend(tags)
        elif resource_id.startswith("wsca-"):
            ca = self.connection_aliases[resource_id]
            ca.tags.extend(tags)
        elif resource_id.startswith("wsb-"):
            bun = self.workspace_bundles[resource_id]
            bun.tags.extend(tags)
        elif resource_id.startswith("wsp-"):
            pool = self.workspaces_pools[resource_id]
            pool.tags.extend(tags)

    def delete_tags(self, resource_id: str, tag_keys: list[str]) -> None:
        tags = self._get_resource_tags(resource_id)
        # Remove tags with matching keys in-place
        to_remove = [t for t in tags if t.get("Key") in tag_keys]
        for t in to_remove:
            tags.remove(t)

    def describe_tags(self, resource_id: str) -> list[dict[str, str]]:
        # AWS returns empty tags (not an error) for nonexistent resources
        if resource_id.startswith("d-"):
            resource = self.workspace_directories.get(resource_id)
        elif resource_id.startswith("ws-"):
            resource = self.workspaces.get(resource_id)
        elif resource_id.startswith("wsi-"):
            resource = self.workspace_images.get(resource_id)
        elif resource_id.startswith("wsipg-"):
            resource = self.ip_groups.get(resource_id)
        elif resource_id.startswith("wsca-"):
            resource = self.connection_aliases.get(resource_id)
        elif resource_id.startswith("wsb-"):
            resource = self.workspace_bundles.get(resource_id)
        elif resource_id.startswith("wsp-"):
            resource = self.workspaces_pools.get(resource_id)
        else:
            resource = None
        return resource.tags if resource is not None else []

    def describe_client_properties(self, resource_ids: str) -> list[dict[str, Any]]:
        workspace_directories = list(self.workspace_directories.values())
        workspace_directories = [
            x for x in workspace_directories if x.directory_id in resource_ids
        ]
        client_properties_list = []
        for wd in workspace_directories:
            cpl = {
                "ResourceId": wd.directory_id,
                "ClientProperties": wd.client_properties,
            }
            client_properties_list.append(cpl)
        return client_properties_list

    def modify_client_properties(
        self, resource_id: str, client_properties: dict[str, str]
    ) -> None:
        res = self.workspace_directories[resource_id]
        res.client_properties = client_properties

    def create_workspace_image(
        self, name: str, description: str, workspace_id: str, tags: list[dict[str, str]]
    ) -> dict[str, Any]:
        # Check if workspace exists.
        if workspace_id not in self.workspaces:
            raise ResourceNotFoundException(
                "The specified WorkSpace cannot be found. Confirm that the workspace exists in your AWS account, and try again."
            )
        # Check if image name already exists.
        if name in [x.name for x in self.workspace_images.values()]:
            raise ResourceAlreadyExistsException(
                "A WorkSpace image with the same name exists in the destination Region. Provide a unique destination image name, and try again."
            )

        workspace_image = WorkspaceImage(
            name=name,
            description=description,
            tags=tags,
            account_id=self.account_id,
        )
        self.workspace_images[workspace_image.image_id] = workspace_image
        return workspace_image.to_dict()

    def describe_workspace_images(
        self, image_ids: Optional[list[str]], image_type: Optional[str]
    ) -> list[dict[str, Any]]:
        # Pagination not yet implemented
        workspace_images = list(self.workspace_images.values())
        if image_type == "OWNED":
            workspace_images = [
                i for i in workspace_images if i.owner_account == self.account_id
            ]
        elif image_type == "SHARED":
            workspace_images = [
                i for i in workspace_images if i.owner_account != self.account_id
            ]
        if image_ids:
            workspace_images = [i for i in workspace_images if i.image_id in image_ids]
        return [w.to_desc_dict() for w in workspace_images]

    def update_workspace_image_permission(
        self, image_id: str, allow_copy_image: bool, shared_account_id: str
    ) -> None:
        shared_account = {"SharedAccountId": shared_account_id}
        res = self.workspace_images[image_id]
        shared_accounts = []
        shared_accounts = res.image_permissions

        if shared_account not in shared_accounts and allow_copy_image:
            shared_accounts.append(shared_account)
        if shared_account in shared_accounts and not allow_copy_image:
            shared_accounts.remove(shared_account)

        res.image_permissions = shared_accounts

    def describe_workspace_image_permissions(
        self, image_id: str
    ) -> tuple[str, list[dict[str, str]]]:
        # Pagination not yet implemented

        msg = f"The Image ID {image_id} in the request is invalid"
        self.validate_image_id(image_id, msg)

        image_permissions = []
        if image_id in self.workspace_images:
            res = self.workspace_images[image_id]
            image_permissions = res.image_permissions
        return image_id, image_permissions

    def deregister_workspace_directory(self, directory_id: str) -> None:
        """Deregister Workspace Directory with the matching ID."""
        self.workspace_directories[directory_id].delete_security_group()
        self.workspace_directories.pop(directory_id)

    def modify_selfservice_permissions(
        self, resource_id: str, selfservice_permissions: dict[str, str]
    ) -> None:
        res = self.workspace_directories[resource_id]
        res.self_service_permissions = selfservice_permissions

    # --- IP Groups ---

    def create_ip_group(
        self,
        group_name: str,
        group_desc: str,
        user_rules: list[dict[str, str]],
        tags: list[dict[str, str]],
    ) -> str:
        ip_group = IpGroup(
            group_name=group_name,
            group_desc=group_desc,
            user_rules=user_rules,
            tags=tags,
        )
        self.ip_groups[ip_group.group_id] = ip_group
        return ip_group.group_id

    def describe_ip_groups(
        self, group_ids: Optional[list[str]] = None
    ) -> list[dict[str, Any]]:
        groups = list(self.ip_groups.values())
        if group_ids:
            groups = [g for g in groups if g.group_id in group_ids]
        return [g.to_dict() for g in groups]

    def delete_ip_group(self, group_id: str) -> None:
        if group_id not in self.ip_groups:
            raise ResourceNotFoundException(f"The IP group {group_id} does not exist.")
        # Also disassociate from any directories
        for directory in self.workspace_directories.values():
            if group_id in directory.ip_group_ids:
                directory.ip_group_ids.remove(group_id)
        self.ip_groups.pop(group_id)

    def authorize_ip_rules(
        self, group_id: str, user_rules: list[dict[str, str]]
    ) -> None:
        if group_id not in self.ip_groups:
            raise ResourceNotFoundException(f"The IP group {group_id} does not exist.")
        grp = self.ip_groups[group_id]
        grp.user_rules.extend(user_rules)

    def revoke_ip_rules(self, group_id: str, user_rules: list[str]) -> None:
        if group_id not in self.ip_groups:
            raise ResourceNotFoundException(f"The IP group {group_id} does not exist.")
        grp = self.ip_groups[group_id]
        grp.user_rules = [r for r in grp.user_rules if r.get("ipRule") not in user_rules]

    def update_rules_of_ip_group(
        self, group_id: str, user_rules: list[dict[str, str]]
    ) -> None:
        if group_id not in self.ip_groups:
            raise ResourceNotFoundException(f"The IP group {group_id} does not exist.")
        grp = self.ip_groups[group_id]
        grp.user_rules = user_rules

    def associate_ip_groups(
        self, directory_id: str, group_ids: list[str]
    ) -> None:
        if directory_id not in self.workspace_directories:
            raise ResourceNotFoundException(
                f"The directory {directory_id} does not exist."
            )
        directory = self.workspace_directories[directory_id]
        for gid in group_ids:
            if gid not in self.ip_groups:
                raise ResourceNotFoundException(f"The IP group {gid} does not exist.")
            if gid not in directory.ip_group_ids:
                directory.ip_group_ids.append(gid)

    def disassociate_ip_groups(
        self, directory_id: str, group_ids: list[str]
    ) -> None:
        if directory_id not in self.workspace_directories:
            raise ResourceNotFoundException(
                f"The directory {directory_id} does not exist."
            )
        directory = self.workspace_directories[directory_id]
        for gid in group_ids:
            if gid in directory.ip_group_ids:
                directory.ip_group_ids.remove(gid)

    # --- Connection Aliases ---

    def create_connection_alias(
        self,
        connection_string: str,
        tags: list[dict[str, str]],
    ) -> str:
        alias = ConnectionAlias(
            connection_string=connection_string,
            tags=tags,
            account_id=self.account_id,
            region=self.region_name,
        )
        self.connection_aliases[alias.alias_id] = alias
        return alias.alias_id

    def describe_connection_aliases(
        self,
        alias_ids: Optional[list[str]] = None,
        resource_id: Optional[str] = None,
    ) -> list[dict[str, Any]]:
        aliases = list(self.connection_aliases.values())
        if alias_ids:
            aliases = [a for a in aliases if a.alias_id in alias_ids]
        if resource_id:
            aliases = [
                a
                for a in aliases
                if any(
                    assoc.get("ResourceId") == resource_id for assoc in a.associations
                )
            ]
        return [a.to_dict() for a in aliases]

    def delete_connection_alias(self, alias_id: str) -> None:
        if alias_id not in self.connection_aliases:
            raise ResourceNotFoundException(
                f"The connection alias {alias_id} does not exist."
            )
        self.connection_aliases.pop(alias_id)

    def associate_connection_alias(
        self, alias_id: str, resource_id: str
    ) -> str:
        if alias_id not in self.connection_aliases:
            raise ResourceNotFoundException(
                f"The connection alias {alias_id} does not exist."
            )
        alias = self.connection_aliases[alias_id]
        connection_id = f"wsci-{mock_random.get_random_hex(9)}"
        alias.associations.append(
            {
                "AssociatedAccountId": self.account_id,
                "ResourceId": resource_id,
                "ConnectionIdentifier": connection_id,
                "AssociationStatus": "ASSOCIATED",
            }
        )
        return connection_id

    def disassociate_connection_alias(self, alias_id: str) -> None:
        if alias_id not in self.connection_aliases:
            raise ResourceNotFoundException(
                f"The connection alias {alias_id} does not exist."
            )
        alias = self.connection_aliases[alias_id]
        alias.associations = []

    def describe_connection_alias_permissions(
        self, alias_id: str
    ) -> tuple[str, list[dict[str, Any]]]:
        if alias_id not in self.connection_aliases:
            raise ResourceNotFoundException(
                f"The connection alias {alias_id} does not exist."
            )
        alias = self.connection_aliases[alias_id]
        return alias_id, alias.permissions

    def update_connection_alias_permission(
        self, alias_id: str, connection_alias_permission: dict[str, Any]
    ) -> None:
        if alias_id not in self.connection_aliases:
            raise ResourceNotFoundException(
                f"The connection alias {alias_id} does not exist."
            )
        alias = self.connection_aliases[alias_id]
        shared_account_id = connection_alias_permission.get("SharedAccountId", "")
        allow_association = connection_alias_permission.get("AllowAssociation", False)
        existing = [
            p for p in alias.permissions if p.get("SharedAccountId") == shared_account_id
        ]
        if allow_association:
            if not existing:
                alias.permissions.append(connection_alias_permission)
        else:
            alias.permissions = [
                p
                for p in alias.permissions
                if p.get("SharedAccountId") != shared_account_id
            ]

    # --- Workspace Bundles ---

    def create_workspace_bundle(
        self,
        bundle_name: str,
        bundle_description: str,
        image_id: str,
        compute_type: dict[str, str],
        user_storage: dict[str, str],
        root_storage: Optional[dict[str, str]],
        tags: list[dict[str, str]],
    ) -> dict[str, Any]:
        bundle = WorkspaceBundle(
            bundle_name=bundle_name,
            bundle_description=bundle_description,
            image_id=image_id,
            compute_type=compute_type,
            user_storage=user_storage,
            root_storage=root_storage,
            tags=tags,
            account_id=self.account_id,
        )
        self.workspace_bundles[bundle.bundle_id] = bundle
        return bundle.to_dict()

    def describe_workspace_bundles(
        self,
        bundle_ids: Optional[list[str]] = None,
        owner: Optional[str] = None,
    ) -> list[dict[str, Any]]:
        bundles = list(self.workspace_bundles.values())
        if bundle_ids:
            bundles = [b for b in bundles if b.bundle_id in bundle_ids]
        if owner:
            bundles = [b for b in bundles if b.owner == owner]
        return [b.to_dict() for b in bundles]

    def delete_workspace_bundle(self, bundle_id: str) -> None:
        if bundle_id and bundle_id in self.workspace_bundles:
            self.workspace_bundles.pop(bundle_id)

    def update_workspace_bundle(
        self, bundle_id: str, image_id: str
    ) -> None:
        if bundle_id not in self.workspace_bundles:
            raise ResourceNotFoundException(
                f"The workspace bundle {bundle_id} does not exist."
            )
        bundle = self.workspace_bundles[bundle_id]
        if image_id:
            bundle.image_id = image_id
            bundle.last_updated_time = unix_time()

    # --- Workspace Image (additional ops) ---

    def copy_workspace_image(
        self,
        name: str,
        description: str,
        source_image_id: str,
        source_region: str,
        tags: list[dict[str, str]],
    ) -> str:
        # Create a copy as a new image
        workspace_image = WorkspaceImage(
            name=name,
            description=description or "",
            tags=tags or [],
            account_id=self.account_id,
        )
        self.workspace_images[workspace_image.image_id] = workspace_image
        return workspace_image.image_id

    def delete_workspace_image(self, image_id: str) -> None:
        if image_id in self.workspace_images:
            self.workspace_images.pop(image_id)

    def create_updated_workspace_image(
        self,
        name: str,
        description: str,
        source_image_id: str,
        tags: list[dict[str, str]],
    ) -> str:
        workspace_image = WorkspaceImage(
            name=name,
            description=description or "",
            tags=tags or [],
            account_id=self.account_id,
        )
        self.workspace_images[workspace_image.image_id] = workspace_image
        return workspace_image.image_id

    def import_workspace_image(
        self,
        ec2_image_id: str,
        ingestion_process: str,
        image_name: str,
        image_description: str,
        tags: list[dict[str, str]],
        applications: Optional[list[str]],
    ) -> str:
        workspace_image = WorkspaceImage(
            name=image_name,
            description=image_description or "",
            tags=tags or [],
            account_id=self.account_id,
        )
        self.workspace_images[workspace_image.image_id] = workspace_image
        return workspace_image.image_id

    def import_custom_workspace_image(
        self,
        image_name: str,
        image_description: str,
        compute_type: Optional[str],
        protocol: Optional[str],
        image_source: Optional[dict[str, str]],
        infrastructure_configuration_arn: Optional[str],
        platform: Optional[str],
        os_version: Optional[str],
        tags: list[dict[str, str]],
    ) -> tuple[str, str]:
        workspace_image = WorkspaceImage(
            name=image_name,
            description=image_description or "",
            tags=tags or [],
            account_id=self.account_id,
        )
        self.workspace_images[workspace_image.image_id] = workspace_image
        return workspace_image.image_id, workspace_image.state

    def describe_custom_workspace_image_import(
        self, image_id: str
    ) -> dict[str, Any]:
        if image_id in self.workspace_images:
            img = self.workspace_images[image_id]
            return {
                "ImageId": img.image_id,
                "State": img.state,
                "Created": img.created,
            }
        raise ResourceNotFoundException(
            f"The workspace image {image_id} does not exist."
        )

    # --- Connect Client Add-Ins ---

    def create_connect_client_add_in(
        self, resource_id: str, name: str, url: str
    ) -> str:
        add_in = ConnectClientAddIn(
            resource_id=resource_id,
            name=name,
            url=url,
        )
        self.connect_client_add_ins[add_in.add_in_id] = add_in
        return add_in.add_in_id

    def describe_connect_client_add_ins(
        self, resource_id: str
    ) -> list[dict[str, Any]]:
        add_ins = [
            a
            for a in self.connect_client_add_ins.values()
            if a.resource_id == resource_id
        ]
        return [a.to_dict() for a in add_ins]

    def delete_connect_client_add_in(
        self, add_in_id: str, resource_id: str
    ) -> None:
        if add_in_id in self.connect_client_add_ins:
            self.connect_client_add_ins.pop(add_in_id)

    def update_connect_client_add_in(
        self,
        add_in_id: str,
        resource_id: str,
        name: Optional[str],
        url: Optional[str],
    ) -> None:
        if add_in_id not in self.connect_client_add_ins:
            raise ResourceNotFoundException(
                f"The add-in {add_in_id} does not exist."
            )
        add_in = self.connect_client_add_ins[add_in_id]
        if name:
            add_in.name = name
        if url:
            add_in.url = url

    # --- Account Links ---

    def create_account_link_invitation(
        self, target_account_id: str, client_token: Optional[str]
    ) -> dict[str, Any]:
        link = AccountLink(
            source_account_id=self.account_id,
            target_account_id=target_account_id,
        )
        link.link_status = "PENDING_ACCEPTANCE"
        self.account_links[link.link_id] = link
        return link.to_dict()

    def accept_account_link_invitation(
        self, link_id: str, client_token: Optional[str]
    ) -> dict[str, Any]:
        if link_id not in self.account_links:
            raise ResourceNotFoundException(
                f"The account link {link_id} does not exist."
            )
        link = self.account_links[link_id]
        link.link_status = "LINKED"
        return link.to_dict()

    def reject_account_link_invitation(
        self, link_id: str, client_token: Optional[str]
    ) -> dict[str, Any]:
        if link_id not in self.account_links:
            raise ResourceNotFoundException(
                f"The account link {link_id} does not exist."
            )
        link = self.account_links[link_id]
        link.link_status = "REJECTED"
        return link.to_dict()

    def delete_account_link_invitation(
        self, link_id: str, client_token: Optional[str]
    ) -> dict[str, Any]:
        if link_id not in self.account_links:
            raise ResourceNotFoundException(
                f"The account link {link_id} does not exist."
            )
        link = self.account_links.pop(link_id)
        link.link_status = "DELETED"
        return link.to_dict()

    def get_account_link(
        self,
        link_id: Optional[str],
        linked_account_id: Optional[str],
    ) -> dict[str, Any]:
        if link_id:
            if link_id not in self.account_links:
                raise ResourceNotFoundException(
                    f"The account link {link_id} does not exist."
                )
            return self.account_links[link_id].to_dict()
        if linked_account_id:
            for link in self.account_links.values():
                if (
                    link.target_account_id == linked_account_id
                    or link.source_account_id == linked_account_id
                ):
                    return link.to_dict()
        raise ResourceNotFoundException("The account link does not exist.")

    def list_account_links(
        self,
        link_status_filter: Optional[list[str]] = None,
    ) -> list[dict[str, Any]]:
        links = list(self.account_links.values())
        if link_status_filter:
            links = [lk for lk in links if lk.link_status in link_status_filter]
        return [lk.to_dict() for lk in links]

    # --- Workspace Pools ---

    def create_workspaces_pool(
        self,
        pool_name: str,
        description: str,
        bundle_id: str,
        directory_id: str,
        capacity: dict[str, int],
        tags: list[dict[str, str]],
        application_settings: Optional[dict[str, Any]],
        timeout_settings: Optional[dict[str, Any]],
        running_mode: Optional[str],
    ) -> dict[str, Any]:
        pool = WorkspacesPool(
            pool_name=pool_name,
            description=description,
            bundle_id=bundle_id,
            directory_id=directory_id,
            capacity=capacity,
            tags=tags,
            application_settings=application_settings,
            timeout_settings=timeout_settings,
            running_mode=running_mode,
            account_id=self.account_id,
            region=self.region_name,
        )
        self.workspaces_pools[pool.pool_id] = pool
        return pool.to_dict()

    def describe_workspaces_pools(
        self,
        pool_ids: Optional[list[str]] = None,
        filters: Optional[list[dict[str, Any]]] = None,
    ) -> list[dict[str, Any]]:
        pools = list(self.workspaces_pools.values())
        if pool_ids:
            pools = [p for p in pools if p.pool_id in pool_ids]
        return [p.to_dict() for p in pools]

    def update_workspaces_pool(
        self,
        pool_id: str,
        description: Optional[str],
        bundle_id: Optional[str],
        directory_id: Optional[str],
        capacity: Optional[dict[str, int]],
        application_settings: Optional[dict[str, Any]],
        timeout_settings: Optional[dict[str, Any]],
        running_mode: Optional[str],
    ) -> dict[str, Any]:
        if pool_id not in self.workspaces_pools:
            raise ResourceNotFoundException(
                f"The workspaces pool {pool_id} does not exist."
            )
        pool = self.workspaces_pools[pool_id]
        if description is not None:
            pool.description = description
        if bundle_id is not None:
            pool.bundle_id = bundle_id
        if directory_id is not None:
            pool.directory_id = directory_id
        if capacity is not None:
            pool.capacity = capacity
        if application_settings is not None:
            pool.application_settings = application_settings
        if timeout_settings is not None:
            pool.timeout_settings = timeout_settings
        if running_mode is not None:
            pool.running_mode = running_mode
        return pool.to_dict()

    def terminate_workspaces_pool(self, pool_id: str) -> None:
        if pool_id not in self.workspaces_pools:
            raise ResourceNotFoundException(
                f"The workspaces pool {pool_id} does not exist."
            )
        self.workspaces_pools.pop(pool_id)

    def start_workspaces_pool(self, pool_id: str) -> None:
        if pool_id not in self.workspaces_pools:
            raise ResourceNotFoundException(
                f"The workspaces pool {pool_id} does not exist."
            )
        pool = self.workspaces_pools[pool_id]
        pool.state = "AVAILABLE"

    def stop_workspaces_pool(self, pool_id: str) -> None:
        if pool_id not in self.workspaces_pools:
            raise ResourceNotFoundException(
                f"The workspaces pool {pool_id} does not exist."
            )
        pool = self.workspaces_pools[pool_id]
        pool.state = "STOPPED"

    def describe_workspaces_pool_sessions(
        self,
        pool_id: str,
        user_id: Optional[str] = None,
    ) -> list[dict[str, Any]]:
        if pool_id not in self.workspaces_pools:
            raise ResourceNotFoundException(
                f"The workspaces pool {pool_id} does not exist."
            )
        pool = self.workspaces_pools[pool_id]
        sessions = pool.sessions
        if user_id:
            sessions = [s for s in sessions if s.get("UserId") == user_id]
        return sessions

    def terminate_workspaces_pool_session(self, session_id: str) -> None:
        for pool in self.workspaces_pools.values():
            pool.sessions = [s for s in pool.sessions if s.get("SessionId") != session_id]

    # --- Workspace State Operations ---

    def start_workspaces(
        self, start_workspace_requests: list[dict[str, str]]
    ) -> list[dict[str, Any]]:
        failed_requests = []
        for req in start_workspace_requests:
            workspace_id = req["WorkspaceId"]
            if workspace_id not in self.workspaces:
                failed_requests.append(
                    {
                        "WorkspaceId": workspace_id,
                        "ErrorCode": "ResourceNotFound.Workspace",
                        "ErrorMessage": f"WorkSpace {workspace_id} could not be found.",
                    }
                )
                continue
            ws = self.workspaces[workspace_id]
            ws.state = "AVAILABLE"
        return failed_requests

    def stop_workspaces(
        self, stop_workspace_requests: list[dict[str, str]]
    ) -> list[dict[str, Any]]:
        failed_requests = []
        for req in stop_workspace_requests:
            workspace_id = req["WorkspaceId"]
            if workspace_id not in self.workspaces:
                failed_requests.append(
                    {
                        "WorkspaceId": workspace_id,
                        "ErrorCode": "ResourceNotFound.Workspace",
                        "ErrorMessage": f"WorkSpace {workspace_id} could not be found.",
                    }
                )
                continue
            ws = self.workspaces[workspace_id]
            ws.state = "STOPPED"
        return failed_requests

    def reboot_workspaces(
        self, reboot_workspace_requests: list[dict[str, str]]
    ) -> list[dict[str, Any]]:
        failed_requests = []
        for req in reboot_workspace_requests:
            workspace_id = req["WorkspaceId"]
            if workspace_id not in self.workspaces:
                failed_requests.append(
                    {
                        "WorkspaceId": workspace_id,
                        "ErrorCode": "ResourceNotFound.Workspace",
                        "ErrorMessage": f"WorkSpace {workspace_id} could not be found.",
                    }
                )
                continue
            # Workspace stays AVAILABLE after reboot
        return failed_requests

    def rebuild_workspaces(
        self, rebuild_workspace_requests: list[dict[str, str]]
    ) -> list[dict[str, Any]]:
        failed_requests = []
        for req in rebuild_workspace_requests:
            workspace_id = req["WorkspaceId"]
            if workspace_id not in self.workspaces:
                failed_requests.append(
                    {
                        "WorkspaceId": workspace_id,
                        "ErrorCode": "ResourceNotFound.Workspace",
                        "ErrorMessage": f"WorkSpace {workspace_id} could not be found.",
                    }
                )
                continue
            # In mock, workspace stays AVAILABLE
        return failed_requests

    def modify_workspace_properties(
        self,
        workspace_id: str,
        workspace_properties: Optional[dict[str, Any]],
        data_replication: Optional[str],
    ) -> None:
        if workspace_id not in self.workspaces:
            raise ResourceNotFoundException(
                f"The workspace {workspace_id} does not exist."
            )
        ws = self.workspaces[workspace_id]
        if workspace_properties:
            ws.workspace_properties.update(workspace_properties)
        if data_replication:
            ws.data_replication_settings["DataReplication"] = data_replication

    def modify_workspace_state(
        self, workspace_id: str, workspace_state: str
    ) -> None:
        if workspace_id not in self.workspaces:
            raise ResourceNotFoundException(
                f"The workspace {workspace_id} does not exist."
            )
        ws = self.workspaces[workspace_id]
        ws.state = workspace_state

    def restore_workspace(self, workspace_id: str) -> None:
        if workspace_id not in self.workspaces:
            raise ResourceNotFoundException(
                f"The workspace {workspace_id} does not exist."
            )
        # In mock, workspace stays AVAILABLE

    def migrate_workspace(
        self, source_workspace_id: str, bundle_id: str
    ) -> tuple[str, str]:
        if source_workspace_id not in self.workspaces:
            raise ResourceNotFoundException(
                f"The workspace {source_workspace_id} does not exist."
            )
        # Create a new workspace as the target
        target_id = f"ws-{mock_random.get_random_hex(9)}"
        return source_workspace_id, target_id

    def describe_workspaces_connection_status(
        self, workspace_ids: Optional[list[str]] = None
    ) -> list[dict[str, Any]]:
        workspaces = list(self.workspaces.values())
        if workspace_ids:
            workspaces = [w for w in workspaces if w.workspace_id in workspace_ids]
        result = []
        for ws in workspaces:
            result.append(
                {
                    "WorkspaceId": ws.workspace_id,
                    "ConnectionState": "UNKNOWN",
                    "ConnectionStateCheckTimestamp": unix_time(),
                    "LastKnownUserConnectionTimestamp": unix_time(),
                }
            )
        return result

    def describe_workspace_snapshots(
        self, workspace_id: str
    ) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
        if workspace_id not in self.workspaces:
            raise ResourceNotFoundException(
                f"The workspace {workspace_id} does not exist."
            )
        rebuild_snapshots: list[dict[str, Any]] = []
        restore_snapshots: list[dict[str, Any]] = []
        return rebuild_snapshots, restore_snapshots

    def create_standby_workspaces(
        self,
        primary_region: str,
        standby_workspaces: list[dict[str, Any]],
    ) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
        failed_requests: list[dict[str, Any]] = []
        pending_requests: list[dict[str, Any]] = []
        for sw in standby_workspaces:
            primary_workspace_id = sw.get("PrimaryWorkspaceId", "")
            directory_id = sw.get("DirectoryId", "")
            workspace_id = f"ws-{mock_random.get_random_hex(9)}"
            pending_requests.append(
                {
                    "StandbyWorkspace": {
                        "PrimaryWorkspaceId": primary_workspace_id,
                        "DirectoryId": directory_id,
                    },
                    "WorkspaceId": workspace_id,
                }
            )
        return failed_requests, pending_requests

    # --- Directory Modification Ops ---

    def modify_workspace_access_properties(
        self, resource_id: str, workspace_access_properties: dict[str, str]
    ) -> None:
        if resource_id not in self.workspace_directories:
            raise ResourceNotFoundException(
                f"The directory {resource_id} does not exist."
            )
        directory = self.workspace_directories[resource_id]
        directory.workspace_access_properties.update(workspace_access_properties)

    def modify_saml_properties(
        self,
        resource_id: str,
        saml_properties: Optional[dict[str, str]],
        properties_to_delete: Optional[list[str]],
    ) -> None:
        if resource_id not in self.workspace_directories:
            raise ResourceNotFoundException(
                f"The directory {resource_id} does not exist."
            )
        directory = self.workspace_directories[resource_id]
        if saml_properties:
            directory.saml_properties.update(saml_properties)
        if properties_to_delete:
            for prop in properties_to_delete:
                if prop == "SAML_PROPERTIES_USER_ACCESS_URL":
                    directory.saml_properties["UserAccessUrl"] = ""
                elif prop == "SAML_PROPERTIES_RELAY_STATE_PARAMETER_NAME":
                    directory.saml_properties["RelayStateParameterName"] = ""

    def modify_certificate_based_auth_properties(
        self,
        resource_id: str,
        certificate_based_auth_properties: Optional[dict[str, str]],
        properties_to_delete: Optional[list[str]],
    ) -> None:
        if resource_id not in self.workspace_directories:
            raise ResourceNotFoundException(
                f"The directory {resource_id} does not exist."
            )
        directory = self.workspace_directories[resource_id]
        if certificate_based_auth_properties:
            directory.certificate_based_auth_properties.update(
                certificate_based_auth_properties
            )
        if properties_to_delete:
            for prop in properties_to_delete:
                if prop == "CERTIFICATE_BASED_AUTH_PROPERTIES_CERTIFICATE_AUTHORITY_ARN":
                    directory.certificate_based_auth_properties.pop(
                        "CertificateAuthorityArn", None
                    )

    def modify_streaming_properties(
        self,
        resource_id: str,
        streaming_properties: Optional[dict[str, Any]],
    ) -> None:
        if resource_id not in self.workspace_directories:
            raise ResourceNotFoundException(
                f"The directory {resource_id} does not exist."
            )
        directory = self.workspace_directories[resource_id]
        if streaming_properties is not None:
            directory.streaming_properties = streaming_properties

    def modify_endpoint_encryption_mode(
        self,
        directory_id: str,
        endpoint_encryption_mode: str,
    ) -> None:
        if directory_id not in self.workspace_directories:
            raise ResourceNotFoundException(
                f"The directory {directory_id} does not exist."
            )
        directory = self.workspace_directories[directory_id]
        directory.endpoint_encryption_mode = endpoint_encryption_mode

    # --- Account Operations ---

    def describe_account(self) -> dict[str, Any]:
        return {
            "DedicatedTenancySupport": self.dedicated_tenancy_support or "DISABLED",
            "DedicatedTenancyManagementCidrRange": self.dedicated_tenancy_management_cidr_range,
        }

    def modify_account(
        self,
        dedicated_tenancy_support: Optional[str],
        dedicated_tenancy_management_cidr_range: Optional[str],
    ) -> None:
        if dedicated_tenancy_support:
            self.dedicated_tenancy_support = dedicated_tenancy_support
        if dedicated_tenancy_management_cidr_range:
            self.dedicated_tenancy_management_cidr_range = (
                dedicated_tenancy_management_cidr_range
            )
        self.account_modifications.append(
            {
                "ModificationState": "COMPLETED",
                "DedicatedTenancySupport": self.dedicated_tenancy_support,
                "DedicatedTenancyManagementCidrRange": self.dedicated_tenancy_management_cidr_range,
                "StartTime": unix_time(),
            }
        )

    def describe_account_modifications(self) -> list[dict[str, Any]]:
        return self.account_modifications

    # --- Client Branding ---

    def import_client_branding(
        self, resource_id: str, branding_info: dict[str, Any]
    ) -> dict[str, Any]:
        # Store branding on the directory
        if resource_id not in self.workspace_directories:
            raise ResourceNotFoundException(
                f"The directory {resource_id} does not exist."
            )
        directory = self.workspace_directories[resource_id]
        if not hasattr(directory, "client_branding"):
            directory.client_branding = {}  # type: ignore[attr-defined]
        directory.client_branding.update(branding_info)  # type: ignore[attr-defined]
        return branding_info

    def describe_client_branding(self, resource_id: str) -> dict[str, Any]:
        if resource_id not in self.workspace_directories:
            raise ResourceNotFoundException(
                f"The directory {resource_id} does not exist."
            )
        directory = self.workspace_directories[resource_id]
        if hasattr(directory, "client_branding"):
            return directory.client_branding  # type: ignore[attr-defined]
        return {}

    def delete_client_branding(
        self, resource_id: str, platforms: list[str]
    ) -> None:
        if resource_id not in self.workspace_directories:
            raise ResourceNotFoundException(
                f"The directory {resource_id} does not exist."
            )
        directory = self.workspace_directories[resource_id]
        if hasattr(directory, "client_branding"):
            for platform in platforms:
                key = f"DeviceType{platform.replace('DeviceType', '')}"
                directory.client_branding.pop(key, None)  # type: ignore[attr-defined]

    # --- Application Associations (stubs) ---

    def associate_workspace_application(
        self, workspace_id: str, application_id: str
    ) -> dict[str, Any]:
        return {
            "WorkspaceId": workspace_id,
            "ApplicationId": application_id,
            "State": "COMPLETED",
            "AssociatedResourceType": "APPLICATION",
        }

    def disassociate_workspace_application(
        self, workspace_id: str, application_id: str
    ) -> dict[str, Any]:
        return {
            "WorkspaceId": workspace_id,
            "ApplicationId": application_id,
            "State": "REMOVED",
            "AssociatedResourceType": "APPLICATION",
        }

    def deploy_workspace_applications(
        self, workspace_id: str, force: Optional[bool]
    ) -> dict[str, Any]:
        return {
            "Deployment": {
                "Associations": [],
            }
        }

    def describe_application_associations(
        self,
        application_id: str,
        associated_resource_types: list[str],
    ) -> list[dict[str, Any]]:
        return []

    def describe_applications(
        self,
        application_ids: Optional[list[str]] = None,
        compute_type_names: Optional[list[str]] = None,
        license_type: Optional[str] = None,
        operating_system_names: Optional[list[str]] = None,
        owner: Optional[str] = None,
    ) -> list[dict[str, Any]]:
        return []

    def describe_bundle_associations(
        self,
        bundle_id: str,
        associated_resource_types: list[str],
    ) -> list[dict[str, Any]]:
        return []

    def describe_image_associations(
        self,
        image_id: str,
        associated_resource_types: list[str],
    ) -> list[dict[str, Any]]:
        return []

    def describe_workspace_associations(
        self,
        workspace_id: str,
        associated_resource_types: list[str],
    ) -> list[dict[str, Any]]:
        return []

    # --- Management CIDR Ranges ---

    def list_available_management_cidr_ranges(
        self, management_cidr_range_constraint: str
    ) -> list[str]:
        # Return some plausible CIDR ranges based on the constraint
        return [management_cidr_range_constraint]


workspaces_backends = BackendDict(WorkSpacesBackend, "workspaces")
