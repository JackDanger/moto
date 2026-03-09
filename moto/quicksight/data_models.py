import datetime
from typing import Any, Optional, Union

from moto.core.common_models import BaseModel
from moto.moto_api._internal import mock_random as random
from moto.utilities.utils import get_partition


class QuicksightDataSet(BaseModel):
    def __init__(self, account_id: str, region: str, _id: str, name: str):
        self.arn = f"arn:{get_partition(region)}:quicksight:{region}:{account_id}:data-set/{_id}"
        self._id = _id
        self.name = name
        self.region = region
        self.account_id = account_id

    def to_json(self) -> dict[str, Any]:
        return {
            "Arn": self.arn,
            "DataSetId": self._id,
            "IngestionArn": f"arn:{get_partition(self.region)}:quicksight:{self.region}:{self.account_id}:ingestion/tbd",
        }


class QuicksightIngestion(BaseModel):
    def __init__(
        self, account_id: str, region: str, data_set_id: str, ingestion_id: str
    ):
        self.arn = f"arn:{get_partition(region)}:quicksight:{region}:{account_id}:data-set/{data_set_id}/ingestions/{ingestion_id}"
        self.ingestion_id = ingestion_id
        self.data_set_id = data_set_id
        self.ingestion_status = "INITIALIZED"
        self.created_time = datetime.datetime.now()

    def to_json(self) -> dict[str, Any]:
        return {
            "Arn": self.arn,
            "IngestionId": self.ingestion_id,
            "IngestionStatus": self.ingestion_status,
        }


class QuicksightMembership(BaseModel):
    def __init__(self, account_id: str, region: str, group: str, user: str):
        self.group = group
        self.user = user
        self.arn = f"arn:{get_partition(region)}:quicksight:{region}:{account_id}:group/default/{group}/{user}"

    def to_json(self) -> dict[str, str]:
        return {"Arn": self.arn, "MemberName": self.user}


class QuicksightGroup(BaseModel):
    def __init__(
        self,
        region: str,
        group_name: str,
        description: str,
        aws_account_id: str,
        namespace: str,
    ):
        self.arn = f"arn:{get_partition(region)}:quicksight:{region}:{aws_account_id}:group/default/{group_name}"
        self.group_name = group_name
        self.description = description
        self.aws_account_id = aws_account_id
        self.namespace = namespace
        self.region = region

        self.members: dict[str, QuicksightMembership] = {}

    def add_member(self, member_name: str) -> QuicksightMembership:
        membership = QuicksightMembership(
            self.aws_account_id, self.region, self.group_name, member_name
        )
        self.members[member_name] = membership
        return membership

    def delete_member(self, user_name: str) -> None:
        self.members.pop(user_name, None)

    def get_member(self, user_name: str) -> Union[QuicksightMembership, None]:
        return self.members.get(user_name, None)

    def list_members(self) -> list[QuicksightMembership]:
        return list(self.members.values())

    def to_json(self) -> dict[str, Any]:
        return {
            "Arn": self.arn,
            "GroupName": self.group_name,
            "Description": self.description,
            "PrincipalId": self.aws_account_id,
            "Namespace": self.namespace,
        }


class QuicksightUser(BaseModel):
    def __init__(
        self,
        account_id: str,
        region: str,
        email: str,
        identity_type: str,
        username: str,
        user_role: str,
    ):
        self.arn = f"arn:{get_partition(region)}:quicksight:{region}:{account_id}:user/default/{username}"
        self.email = email
        self.identity_type = identity_type
        self.username = username
        self.user_role = user_role
        self.active = False
        self.principal_id = random.get_random_hex(10)
        self.account_id = account_id
        self.region = region
        self.custom_permissions_name: Optional[str] = None

    def to_json(self) -> dict[str, Any]:
        return {
            "Arn": self.arn,
            "Email": self.email,
            "IdentityType": self.identity_type,
            "Role": self.user_role,
            "UserName": self.username,
            "Active": self.active,
            "PrincipalId": self.principal_id,
        }


class QuicksightDashboard(BaseModel):
    def __init__(
        self,
        account_id: str,
        region: str,
        dashboard_id: str,
        dashboard_publish_options: dict[str, Any],
        name: str,
        definition: dict[str, Any],
        folder_arns: list[str],
        link_entities: list[str],
        link_sharing_configuration: dict[str, Any],
        parameters: dict[str, Any],
        permissions: list[dict[str, Any]],
        source_entity: dict[str, Any],
        tags: list[dict[str, Any]],
        theme_arn: str,
        version_description: str,
        validation_strategy: dict[str, str],
    ) -> None:
        self.arn = f"arn:{get_partition(region)}:quicksight:{region}:{account_id}:dashboard/{dashboard_id}"
        self.dashboard_id = dashboard_id
        self.name = name
        self.region = region
        self.account_id = account_id
        self.dashboard_publish_options = dashboard_publish_options
        self.definition = definition
        self.folder_arns = folder_arns
        self.link_entities = link_entities
        self.link_sharing_configuration = link_sharing_configuration
        self.parameters = parameters
        self.permissions = permissions or []
        self.source_entity = source_entity
        self.tags = tags
        self.theme_arn = theme_arn
        self.version_description = version_description
        self.validation_strategy = validation_strategy
        # Not user provided
        self.created_time = datetime.datetime.now()
        self.version_number = 1
        self.status = "CREATION_SUCCESSFUL"
        self.last_updated_time = datetime.datetime.now()
        self.last_published_time = datetime.datetime.now()

    def to_dict(self) -> dict[str, Any]:
        return {
            "Arn": self.arn,
            "DashboardId": self.dashboard_id,
            "Name": self.name,
            "Version": {
                "CreatedTime": str(self.created_time),
                "Errors": [],
                "Status": self.status,
                "VersionNumber": self.version_number,
                "Arn": self.arn,
                "SourceEntityArn": self.source_entity,
                "ThemeArn": self.theme_arn,
                "Description": self.version_description,
                "SourceEntity": self.source_entity,
            },
            "CreatedTime": str(self.created_time),
            "LastPublishedTime": str(self.last_published_time),
            "LastUpdatedTime": str(self.last_updated_time),
        }


class QuicksightAccountSettings(BaseModel):
    def __init__(
        self, account_id: str, account_name: Optional[str] = "default"
    ) -> None:
        self.account_name = account_name
        self.account_id = account_id
        self.default_namespace = "default"
        self.notification_email = ""
        self.termination_protection_enabled = False
        self.public_sharing_enabled = False
        self.edition = "STANDARD"


class QuickSightDataSource(BaseModel):
    def __init__(
        self,
        account_id: str,
        region: str,
        data_source_id: str,
        name: str,
        data_source_parameters: Optional[dict[str, dict[str, Any]]] = None,
        alternate_data_source_parameters: Optional[list[dict[str, Any]]] = None,
        ssl_properties: Optional[dict[str, Any]] = None,
        status: Optional[str] = None,
        tags: Optional[list[dict[str, str]]] = None,
        data_source_type: Optional[str] = None,
        vpc_connection_properties: Optional[dict[str, Any]] = None,
    ) -> None:
        self.account_id = account_id
        self.region = region
        self.created_time = datetime.datetime.now()
        self.data_source_id = data_source_id
        self.data_source_parameters = data_source_parameters
        self.alternate_data_source_parameters = alternate_data_source_parameters
        self.last_updated_time = datetime.datetime.now()
        self.name = name
        self.data_source_type = data_source_type
        self.arn = f"arn:{get_partition(region)}:quicksight:{region}:{account_id}:datasource/{data_source_id}"
        self.status = status
        self.tags = tags or []
        self.ssl_properties = ssl_properties
        self.vpc_connection_properties = vpc_connection_properties
        self.permissions: list[dict[str, Any]] = []

    def to_json(self) -> dict[str, Any]:
        return {
            "AlternateDataSourceParameters": self.alternate_data_source_parameters,
            "Arn": self.arn,
            "CreatedTime": self.created_time.isoformat(),
            "DataSourceId": self.data_source_id,
            "DataSourceParameters": self.data_source_parameters,
            "LastUpdatedTime": self.last_updated_time.isoformat(),
            "Name": self.name,
            "SslProperties": self.ssl_properties,
            "Status": self.status,
            "Type": self.data_source_type,
            "VpcConnectionProperties": self.vpc_connection_properties,
        }


# --- New resource types ---


class QuicksightAnalysis(BaseModel):
    def __init__(
        self,
        account_id: str,
        region: str,
        analysis_id: str,
        name: str,
        source_entity: Optional[dict[str, Any]] = None,
        definition: Optional[dict[str, Any]] = None,
        parameters: Optional[dict[str, Any]] = None,
        permissions: Optional[list[dict[str, Any]]] = None,
        tags: Optional[list[dict[str, str]]] = None,
        theme_arn: Optional[str] = None,
        validation_strategy: Optional[dict[str, str]] = None,
        folder_arns: Optional[list[str]] = None,
    ) -> None:
        self.arn = f"arn:{get_partition(region)}:quicksight:{region}:{account_id}:analysis/{analysis_id}"
        self.analysis_id = analysis_id
        self.name = name
        self.account_id = account_id
        self.region = region
        self.source_entity = source_entity
        self.definition = definition
        self.parameters = parameters
        self.permissions = permissions or []
        self.tags = tags
        self.theme_arn = theme_arn
        self.validation_strategy = validation_strategy
        self.folder_arns = folder_arns
        self.created_time = datetime.datetime.now()
        self.last_updated_time = datetime.datetime.now()
        self.status = "CREATION_SUCCESSFUL"
        self.deleted = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "Arn": self.arn,
            "AnalysisId": self.analysis_id,
            "Name": self.name,
            "Status": self.status,
            "CreatedTime": str(self.created_time),
            "LastUpdatedTime": str(self.last_updated_time),
            "ThemeArn": self.theme_arn,
        }

    def to_summary(self) -> dict[str, Any]:
        return {
            "Arn": self.arn,
            "AnalysisId": self.analysis_id,
            "Name": self.name,
            "Status": self.status,
            "CreatedTime": str(self.created_time),
            "LastUpdatedTime": str(self.last_updated_time),
        }


class QuicksightTemplate(BaseModel):
    def __init__(
        self,
        account_id: str,
        region: str,
        template_id: str,
        name: str,
        source_entity: Optional[dict[str, Any]] = None,
        definition: Optional[dict[str, Any]] = None,
        permissions: Optional[list[dict[str, Any]]] = None,
        tags: Optional[list[dict[str, str]]] = None,
        version_description: Optional[str] = None,
        validation_strategy: Optional[dict[str, str]] = None,
    ) -> None:
        self.arn = f"arn:{get_partition(region)}:quicksight:{region}:{account_id}:template/{template_id}"
        self.template_id = template_id
        self.name = name
        self.account_id = account_id
        self.region = region
        self.source_entity = source_entity
        self.definition = definition
        self.permissions = permissions or []
        self.tags = tags
        self.version_description = version_description
        self.validation_strategy = validation_strategy
        self.created_time = datetime.datetime.now()
        self.last_updated_time = datetime.datetime.now()
        self.version_number = 1
        self.status = "CREATION_SUCCESSFUL"
        self.aliases: dict[str, QuicksightTemplateAlias] = {}

    def to_dict(self) -> dict[str, Any]:
        return {
            "Arn": self.arn,
            "TemplateId": self.template_id,
            "Name": self.name,
            "Version": {
                "CreatedTime": str(self.created_time),
                "Errors": [],
                "VersionNumber": self.version_number,
                "Status": self.status,
                "Description": self.version_description,
                "SourceEntityArn": self.source_entity,
            },
            "CreatedTime": str(self.created_time),
            "LastUpdatedTime": str(self.last_updated_time),
        }

    def to_summary(self) -> dict[str, Any]:
        return {
            "Arn": self.arn,
            "TemplateId": self.template_id,
            "Name": self.name,
            "LatestVersionNumber": self.version_number,
            "CreatedTime": str(self.created_time),
            "LastUpdatedTime": str(self.last_updated_time),
        }


class QuicksightTemplateAlias(BaseModel):
    def __init__(
        self,
        alias_name: str,
        template_version_number: int,
        arn: str,
    ) -> None:
        self.alias_name = alias_name
        self.template_version_number = template_version_number
        self.arn = arn

    def to_dict(self) -> dict[str, Any]:
        return {
            "AliasName": self.alias_name,
            "Arn": self.arn,
            "TemplateVersionNumber": self.template_version_number,
        }


class QuicksightTheme(BaseModel):
    def __init__(
        self,
        account_id: str,
        region: str,
        theme_id: str,
        name: str,
        base_theme_id: Optional[str] = None,
        configuration: Optional[dict[str, Any]] = None,
        permissions: Optional[list[dict[str, Any]]] = None,
        tags: Optional[list[dict[str, str]]] = None,
        version_description: Optional[str] = None,
    ) -> None:
        self.arn = f"arn:{get_partition(region)}:quicksight:{region}:{account_id}:theme/{theme_id}"
        self.theme_id = theme_id
        self.name = name
        self.account_id = account_id
        self.region = region
        self.base_theme_id = base_theme_id
        self.configuration = configuration
        self.permissions = permissions or []
        self.tags = tags
        self.version_description = version_description
        self.created_time = datetime.datetime.now()
        self.last_updated_time = datetime.datetime.now()
        self.version_number = 1
        self.status = "CREATION_SUCCESSFUL"
        self.aliases: dict[str, QuicksightThemeAlias] = {}

    def to_dict(self) -> dict[str, Any]:
        return {
            "Arn": self.arn,
            "ThemeId": self.theme_id,
            "Name": self.name,
            "Version": {
                "VersionNumber": self.version_number,
                "Status": self.status,
                "CreatedTime": str(self.created_time),
                "Description": self.version_description,
                "BaseThemeId": self.base_theme_id,
                "Configuration": self.configuration,
            },
            "CreatedTime": str(self.created_time),
            "LastUpdatedTime": str(self.last_updated_time),
            "Type": "CUSTOM",
        }

    def to_summary(self) -> dict[str, Any]:
        return {
            "Arn": self.arn,
            "ThemeId": self.theme_id,
            "Name": self.name,
            "LatestVersionNumber": self.version_number,
            "CreatedTime": str(self.created_time),
            "LastUpdatedTime": str(self.last_updated_time),
        }


class QuicksightThemeAlias(BaseModel):
    def __init__(
        self,
        alias_name: str,
        theme_version_number: int,
        arn: str,
    ) -> None:
        self.alias_name = alias_name
        self.theme_version_number = theme_version_number
        self.arn = arn

    def to_dict(self) -> dict[str, Any]:
        return {
            "AliasName": self.alias_name,
            "Arn": self.arn,
            "ThemeVersionNumber": self.theme_version_number,
        }


class QuicksightFolder(BaseModel):
    def __init__(
        self,
        account_id: str,
        region: str,
        folder_id: str,
        name: str,
        folder_type: Optional[str] = None,
        parent_folder_arn: Optional[str] = None,
        permissions: Optional[list[dict[str, Any]]] = None,
        tags: Optional[list[dict[str, str]]] = None,
        sharing_model: Optional[str] = None,
    ) -> None:
        self.arn = f"arn:{get_partition(region)}:quicksight:{region}:{account_id}:folder/{folder_id}"
        self.folder_id = folder_id
        self.name = name
        self.account_id = account_id
        self.region = region
        self.folder_type = folder_type or "SHARED"
        self.parent_folder_arn = parent_folder_arn
        self.permissions = permissions or []
        self.tags = tags
        self.sharing_model = sharing_model
        self.created_time = datetime.datetime.now()
        self.last_updated_time = datetime.datetime.now()
        # members: dict of (member_type, member_id) -> member_arn
        self.members: dict[tuple[str, str], str] = {}

    def to_dict(self) -> dict[str, Any]:
        return {
            "Arn": self.arn,
            "FolderId": self.folder_id,
            "Name": self.name,
            "FolderType": self.folder_type,
            "FolderPath": [self.arn],
            "CreatedTime": str(self.created_time),
            "LastUpdatedTime": str(self.last_updated_time),
            "SharingModel": self.sharing_model,
        }

    def to_summary(self) -> dict[str, Any]:
        return {
            "Arn": self.arn,
            "FolderId": self.folder_id,
            "Name": self.name,
            "FolderType": self.folder_type,
            "CreatedTime": str(self.created_time),
            "LastUpdatedTime": str(self.last_updated_time),
            "SharingModel": self.sharing_model,
        }


class QuicksightNamespace(BaseModel):
    def __init__(
        self,
        account_id: str,
        region: str,
        namespace: str,
        identity_store: Optional[str] = None,
        tags: Optional[list[dict[str, str]]] = None,
    ) -> None:
        self.arn = f"arn:{get_partition(region)}:quicksight:{region}:{account_id}:namespace/{namespace}"
        self.namespace = namespace
        self.account_id = account_id
        self.region = region
        self.identity_store = identity_store or "QUICKSIGHT"
        self.tags = tags
        self.creation_status = "CREATED"
        self.capacity_region = region

    def to_dict(self) -> dict[str, Any]:
        return {
            "Arn": self.arn,
            "Name": self.namespace,
            "CapacityRegion": self.capacity_region,
            "CreationStatus": self.creation_status,
            "IdentityStore": self.identity_store,
        }


class QuicksightTopic(BaseModel):
    def __init__(
        self,
        account_id: str,
        region: str,
        topic_id: str,
        name: str,
        description: Optional[str] = None,
        data_sets: Optional[list[dict[str, Any]]] = None,
        tags: Optional[list[dict[str, str]]] = None,
    ) -> None:
        self.arn = f"arn:{get_partition(region)}:quicksight:{region}:{account_id}:topic/{topic_id}"
        self.topic_id = topic_id
        self.name = name
        self.account_id = account_id
        self.region = region
        self.description = description
        self.data_sets = data_sets or []
        self.tags = tags
        self.permissions: list[dict[str, Any]] = []
        self.refresh_schedules: dict[str, dict[str, Any]] = {}
        self.reviewed_answers: list[dict[str, Any]] = []

    def to_dict(self) -> dict[str, Any]:
        return {
            "Arn": self.arn,
            "TopicId": self.topic_id,
            "Name": self.name,
            "Description": self.description,
            "DataSets": self.data_sets,
        }

    def to_summary(self) -> dict[str, Any]:
        return {
            "Arn": self.arn,
            "TopicId": self.topic_id,
            "Name": self.name,
        }


class QuicksightVPCConnection(BaseModel):
    def __init__(
        self,
        account_id: str,
        region: str,
        vpc_connection_id: str,
        name: str,
        subnet_ids: Optional[list[str]] = None,
        security_group_ids: Optional[list[str]] = None,
        dns_resolvers: Optional[list[str]] = None,
        role_arn: Optional[str] = None,
        tags: Optional[list[dict[str, str]]] = None,
    ) -> None:
        self.arn = f"arn:{get_partition(region)}:quicksight:{region}:{account_id}:vpcConnection/{vpc_connection_id}"
        self.vpc_connection_id = vpc_connection_id
        self.name = name
        self.account_id = account_id
        self.region = region
        self.subnet_ids = subnet_ids or []
        self.security_group_ids = security_group_ids or []
        self.dns_resolvers = dns_resolvers or []
        self.role_arn = role_arn
        self.tags = tags
        self.status = "CREATION_SUCCESSFUL"
        self.availability_status = "AVAILABLE"
        self.created_time = datetime.datetime.now()
        self.last_updated_time = datetime.datetime.now()

    def to_dict(self) -> dict[str, Any]:
        return {
            "Arn": self.arn,
            "VPCConnectionId": self.vpc_connection_id,
            "Name": self.name,
            "VPCId": "vpc-mock",
            "SecurityGroupIds": self.security_group_ids,
            "DnsResolvers": self.dns_resolvers,
            "Status": self.status,
            "AvailabilityStatus": self.availability_status,
            "RoleArn": self.role_arn,
            "CreatedTime": str(self.created_time),
            "LastUpdatedTime": str(self.last_updated_time),
        }

    def to_summary(self) -> dict[str, Any]:
        return {
            "Arn": self.arn,
            "VPCConnectionId": self.vpc_connection_id,
            "Name": self.name,
            "VPCId": "vpc-mock",
            "Status": self.status,
            "AvailabilityStatus": self.availability_status,
            "CreatedTime": str(self.created_time),
            "LastUpdatedTime": str(self.last_updated_time),
        }


class QuicksightRefreshSchedule(BaseModel):
    def __init__(
        self,
        account_id: str,
        region: str,
        data_set_id: str,
        schedule: dict[str, Any],
    ) -> None:
        self.schedule_id = schedule.get("ScheduleId", "")
        self.arn = f"arn:{get_partition(region)}:quicksight:{region}:{account_id}:data-set/{data_set_id}/refresh-schedule/{self.schedule_id}"
        self.data_set_id = data_set_id
        self.schedule = schedule

    def to_dict(self) -> dict[str, Any]:
        return self.schedule


class QuicksightIAMPolicyAssignment(BaseModel):
    def __init__(
        self,
        account_id: str,
        region: str,
        namespace: str,
        assignment_name: str,
        assignment_status: Optional[str] = None,
        policy_arn: Optional[str] = None,
        identities: Optional[dict[str, list[str]]] = None,
    ) -> None:
        self.arn = f"arn:{get_partition(region)}:quicksight:{region}:{account_id}:assignment/{namespace}/{assignment_name}"
        self.assignment_name = assignment_name
        self.assignment_id = random.get_random_hex(16)
        self.assignment_status = assignment_status or "ENABLED"
        self.policy_arn = policy_arn
        self.identities = identities or {}
        self.namespace = namespace
        self.account_id = account_id
        self.region = region

    def to_dict(self) -> dict[str, Any]:
        return {
            "AssignmentName": self.assignment_name,
            "AssignmentId": self.assignment_id,
            "AssignmentStatus": self.assignment_status,
            "PolicyArn": self.policy_arn,
            "Identities": self.identities,
        }


class QuicksightAccountCustomization(BaseModel):
    def __init__(
        self,
        account_id: str,
        region: str,
        default_theme: Optional[str] = None,
        default_email_customization_template: Optional[str] = None,
        namespace: Optional[str] = None,
    ) -> None:
        self.account_id = account_id
        self.region = region
        self.default_theme = default_theme
        self.default_email_customization_template = default_email_customization_template
        self.namespace = namespace

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        if self.default_theme:
            result["DefaultTheme"] = self.default_theme
        if self.default_email_customization_template:
            result["DefaultEmailCustomizationTemplate"] = self.default_email_customization_template
        return result
