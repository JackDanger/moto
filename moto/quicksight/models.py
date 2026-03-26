from datetime import datetime
from typing import Any, Optional

from moto.core.base_backend import BackendDict, BaseBackend
from moto.utilities.paginator import paginate
from moto.utilities.tagging_service import TaggingService

from .data_models import (
    QuicksightAccountCustomization,
    QuicksightAccountSettings,
    QuicksightAnalysis,
    QuicksightDashboard,
    QuicksightDataSet,
    QuickSightDataSource,
    QuicksightFolder,
    QuicksightGroup,
    QuicksightIAMPolicyAssignment,
    QuicksightIngestion,
    QuicksightMembership,
    QuicksightNamespace,
    QuicksightRefreshSchedule,
    QuicksightTemplate,
    QuicksightTemplateAlias,
    QuicksightTheme,
    QuicksightThemeAlias,
    QuicksightTopic,
    QuicksightUser,
    QuicksightVPCConnection,
)
from .exceptions import ResourceNotFoundException
from .utils import PAGINATION_MODEL, QuicksightSearchFilterFactory


def _create_id(aws_account_id: str, namespace: str, _id: str) -> str:
    return f"{aws_account_id}:{namespace}:{_id}"


class QuickSightBackend(BaseBackend):
    """Implementation of QuickSight APIs."""

    def __init__(self, region_name: str, account_id: str):
        super().__init__(region_name, account_id)
        self.dashboards: dict[str, QuicksightDashboard] = {}
        self.groups: dict[str, QuicksightGroup] = {}
        self.users: dict[str, QuicksightUser] = {}
        self.account_settings: QuicksightAccountSettings = QuicksightAccountSettings(
            account_id=account_id
        )
        self.data_sources: dict[str, QuickSightDataSource] = {}
        self.data_sets: dict[str, QuicksightDataSet] = {}
        self.analyses: dict[str, QuicksightAnalysis] = {}
        self.templates: dict[str, QuicksightTemplate] = {}
        self.themes: dict[str, QuicksightTheme] = {}
        self.folders: dict[str, QuicksightFolder] = {}
        self.namespaces: dict[str, QuicksightNamespace] = {}
        self.topics: dict[str, QuicksightTopic] = {}
        self.vpc_connections: dict[str, QuicksightVPCConnection] = {}
        self.ingestions: dict[str, QuicksightIngestion] = {}
        self.refresh_schedules: dict[str, dict[str, QuicksightRefreshSchedule]] = {}
        self.iam_policy_assignments: dict[str, dict[str, QuicksightIAMPolicyAssignment]] = {}
        self.account_customization: Optional[QuicksightAccountCustomization] = None
        self.ip_restriction: dict[str, Any] = {}
        self.tagger = TaggingService()
        # role -> namespace -> set of member names
        self.role_memberships: dict[str, dict[str, set[str]]] = {}
        # role -> namespace -> custom_permissions_name
        self.role_custom_permissions: dict[str, dict[str, str]] = {}

    # --- DataSet ---

    def create_data_set(
        self,
        data_set_id: str,
        name: str,
        tags: Optional[list[dict[str, str]]] = None,
    ) -> QuicksightDataSet:
        dataset = QuicksightDataSet(
            self.account_id, self.region_name, data_set_id, name=name
        )
        if tags:
            self.tagger.tag_resource(arn=dataset.arn, tags=tags)
        self.data_sets[data_set_id] = dataset
        return dataset

    def describe_data_set(self, data_set_id: str) -> QuicksightDataSet:
        ds = self.data_sets.get(data_set_id)
        if not ds:
            raise ResourceNotFoundException(f"DataSet {data_set_id} not found")
        return ds

    def delete_data_set(self, data_set_id: str) -> QuicksightDataSet:
        ds = self.data_sets.pop(data_set_id, None)
        if not ds:
            raise ResourceNotFoundException(f"DataSet {data_set_id} not found")
        return ds

    def list_data_sets(self) -> list[dict[str, Any]]:
        return [ds.to_json() for ds in self.data_sets.values()]

    def update_data_set(
        self, data_set_id: str, name: str
    ) -> QuicksightDataSet:
        ds = self.data_sets.get(data_set_id)
        if not ds:
            raise ResourceNotFoundException(f"DataSet {data_set_id} not found")
        if name:
            ds.name = name
        return ds

    def describe_data_set_permissions(self, data_set_id: str) -> tuple[str, str, list[dict[str, Any]]]:
        ds = self.describe_data_set(data_set_id)
        return ds.arn, data_set_id, []

    def update_data_set_permissions(
        self, data_set_id: str,
        grant_permissions: Optional[list[dict[str, Any]]] = None,
        revoke_permissions: Optional[list[dict[str, Any]]] = None,
    ) -> tuple[str, str]:
        ds = self.describe_data_set(data_set_id)
        return ds.arn, data_set_id

    # --- Group ---

    def create_group(
        self, group_name: str, description: str, aws_account_id: str, namespace: str
    ) -> QuicksightGroup:
        group = QuicksightGroup(
            region=self.region_name,
            group_name=group_name,
            description=description,
            aws_account_id=aws_account_id,
            namespace=namespace,
        )
        _id = _create_id(aws_account_id, namespace, group_name)
        self.groups[_id] = group
        return group

    def create_group_membership(
        self, aws_account_id: str, namespace: str, group_name: str, member_name: str
    ) -> QuicksightMembership:
        group = self.describe_group(aws_account_id, namespace, group_name)
        return group.add_member(member_name)

    def delete_group(
        self, aws_account_id: str, namespace: str, group_name: str
    ) -> None:
        _id = _create_id(aws_account_id, namespace, group_name)
        self.groups.pop(_id, None)

    def delete_group_membership(
        self, aws_account_id: str, namespace: str, group_name: str, member_name: str
    ) -> None:
        group = self.describe_group(aws_account_id, namespace, group_name)
        group.delete_member(member_name)

    def describe_group(
        self, aws_account_id: str, namespace: str, group_name: str
    ) -> QuicksightGroup:
        _id = _create_id(aws_account_id, namespace, group_name)
        if _id not in self.groups:
            raise ResourceNotFoundException(f"Group {group_name} not found")
        return self.groups[_id]

    def describe_group_membership(
        self, aws_account_id: str, namespace: str, group_name: str, member_name: str
    ) -> QuicksightMembership:
        group = self.describe_group(aws_account_id, namespace, group_name)
        member = group.get_member(member_name)
        if member is None:
            raise ResourceNotFoundException(f"Member {member_name} not found")
        return member

    def update_group(
        self, aws_account_id: str, namespace: str, group_name: str, description: str
    ) -> QuicksightGroup:
        group = self.describe_group(aws_account_id, namespace, group_name)
        group.description = description
        return group

    @paginate(pagination_model=PAGINATION_MODEL)
    def list_groups(self, aws_account_id: str, namespace: str) -> list[QuicksightGroup]:
        id_for_ns = _create_id(aws_account_id, namespace, _id="")
        return [
            group for _id, group in self.groups.items() if _id.startswith(id_for_ns)
        ]

    @paginate(pagination_model=PAGINATION_MODEL)
    def search_groups(
        self, aws_account_id: str, namespace: str, filters: list[dict[str, str]]
    ) -> list[QuicksightGroup]:
        id_for_ns = _create_id(aws_account_id, namespace, _id="")
        filter_list = QuicksightSearchFilterFactory.validate_and_create_filter(
            model_type=QuicksightGroup, input=filters
        )
        return [
            group
            for _id, group in self.groups.items()
            if _id.startswith(id_for_ns) and filter_list.match(group)
        ]

    @paginate(pagination_model=PAGINATION_MODEL)
    def list_group_memberships(
        self, aws_account_id: str, namespace: str, group_name: str
    ) -> list[QuicksightMembership]:
        group = self.describe_group(aws_account_id, namespace, group_name)
        return group.list_members()

    # --- User ---

    def register_user(
        self,
        identity_type: str,
        email: str,
        user_role: str,
        aws_account_id: str,
        namespace: str,
        user_name: str,
        tags: Optional[list[dict[str, str]]] = None,
    ) -> QuicksightUser:
        user = QuicksightUser(
            account_id=aws_account_id,
            region=self.region_name,
            email=email,
            identity_type=identity_type,
            user_role=user_role,
            username=user_name,
        )
        _id = _create_id(aws_account_id, namespace, user_name)
        if tags:
            self.tagger.tag_resource(arn=user.arn, tags=tags)
        self.users[_id] = user
        return user

    def describe_user(
        self, aws_account_id: str, namespace: str, user_name: str
    ) -> QuicksightUser:
        _id = _create_id(aws_account_id, namespace, user_name)
        if _id not in self.users:
            raise ResourceNotFoundException(f"User {user_name} not found")
        return self.users[_id]

    def update_user(
        self,
        aws_account_id: str,
        namespace: str,
        user_name: str,
        email: str,
        user_role: str,
    ) -> QuicksightUser:
        user = self.describe_user(aws_account_id, namespace, user_name)
        user.email = email
        user.user_role = user_role
        return user

    def delete_user(self, aws_account_id: str, namespace: str, user_name: str) -> None:
        for group in self.groups.values():
            group.delete_member(user_name)
        _id = _create_id(aws_account_id, namespace, user_name)
        self.users.pop(_id, None)

    def delete_user_by_principal_id(
        self, aws_account_id: str, namespace: str, principal_id: str
    ) -> None:
        id_for_ns = _create_id(aws_account_id, namespace, _id="")
        to_delete = None
        for uid, user in self.users.items():
            if uid.startswith(id_for_ns) and user.principal_id == principal_id:
                to_delete = uid
                break
        if to_delete:
            self.users.pop(to_delete, None)

    @paginate(pagination_model=PAGINATION_MODEL)
    def list_users(self, aws_account_id: str, namespace: str) -> list[QuicksightUser]:
        id_for_ns = _create_id(aws_account_id, namespace, _id="")
        return [user for _id, user in self.users.items() if _id.startswith(id_for_ns)]

    @paginate(pagination_model=PAGINATION_MODEL)
    def list_user_groups(
        self, aws_account_id: str, namespace: str, user_name: str
    ) -> list[QuicksightGroup]:
        id_for_ns = _create_id(aws_account_id, namespace, _id="")
        group_list: dict[str, QuicksightGroup] = {}
        for gid, group in self.groups.items():
            if group.get_member(user_name):
                group_list[gid] = group
        return [group for _id, group in group_list.items() if _id.startswith(id_for_ns)]

    def update_user_custom_permission(
        self, aws_account_id: str, namespace: str, user_name: str,
        custom_permissions_name: str,
    ) -> QuicksightUser:
        user = self.describe_user(aws_account_id, namespace, user_name)
        user.custom_permissions_name = custom_permissions_name
        return user

    def delete_user_custom_permission(
        self, aws_account_id: str, namespace: str, user_name: str
    ) -> QuicksightUser:
        user = self.describe_user(aws_account_id, namespace, user_name)
        user.custom_permissions_name = None
        return user

    # --- Ingestion ---

    def create_ingestion(
        self, data_set_id: str, ingestion_id: str
    ) -> QuicksightIngestion:
        ingestion = QuicksightIngestion(
            self.account_id, self.region_name, data_set_id, ingestion_id
        )
        key = f"{data_set_id}:{ingestion_id}"
        self.ingestions[key] = ingestion
        return ingestion

    def cancel_ingestion(
        self, data_set_id: str, ingestion_id: str
    ) -> QuicksightIngestion:
        key = f"{data_set_id}:{ingestion_id}"
        ingestion = self.ingestions.get(key)
        if not ingestion:
            raise ResourceNotFoundException(f"Ingestion {ingestion_id} not found")
        ingestion.ingestion_status = "CANCELLED"
        return ingestion

    def describe_ingestion(
        self, data_set_id: str, ingestion_id: str
    ) -> QuicksightIngestion:
        key = f"{data_set_id}:{ingestion_id}"
        ingestion = self.ingestions.get(key)
        if not ingestion:
            raise ResourceNotFoundException(f"Ingestion {ingestion_id} not found")
        return ingestion

    def list_ingestions(self, data_set_id: str) -> list[QuicksightIngestion]:
        return [
            ing for ing in self.ingestions.values()
            if ing.data_set_id == data_set_id
        ]

    # --- Dashboard ---

    def create_dashboard(
        self,
        aws_account_id: str,
        dashboard_id: str,
        name: str,
        parameters: dict[str, Any],
        permissions: list[dict[str, Any]],
        source_entity: dict[str, Any],
        tags: list[dict[str, str]],
        version_description: str,
        dashboard_publish_options: dict[str, Any],
        theme_arn: str,
        definition: dict[str, Any],
        validation_strategy: dict[str, str],
        folder_arns: list[str],
        link_sharing_configuration: dict[str, Any],
        link_entities: list[str],
    ) -> QuicksightDashboard:
        dashboard = QuicksightDashboard(
            account_id=aws_account_id,
            region=self.region_name,
            dashboard_id=dashboard_id,
            dashboard_publish_options=dashboard_publish_options,
            name=name,
            definition=definition,
            folder_arns=folder_arns,
            link_entities=link_entities,
            link_sharing_configuration=link_sharing_configuration,
            parameters=parameters,
            permissions=permissions,
            source_entity=source_entity,
            tags=tags,
            theme_arn=theme_arn,
            version_description=version_description,
            validation_strategy=validation_strategy,
        )
        if tags:
            self.tagger.tag_resource(arn=dashboard.arn, tags=tags)
        self.dashboards[dashboard_id] = dashboard
        return dashboard

    def describe_dashboard(
        self,
        aws_account_id: str,
        dashboard_id: str,
        version_number: int,
        alias_name: str,
    ) -> QuicksightDashboard:
        dashboard = self.dashboards.get(dashboard_id)
        if not dashboard:
            raise ResourceNotFoundException(f"Dashboard {dashboard_id} not found")
        return dashboard

    def update_dashboard(
        self,
        aws_account_id: str,
        dashboard_id: str,
        name: str,
        source_entity: Optional[dict[str, Any]] = None,
        definition: Optional[dict[str, Any]] = None,
        parameters: Optional[dict[str, Any]] = None,
        version_description: Optional[str] = None,
        dashboard_publish_options: Optional[dict[str, Any]] = None,
        theme_arn: Optional[str] = None,
        validation_strategy: Optional[dict[str, str]] = None,
    ) -> QuicksightDashboard:
        dashboard = self.dashboards.get(dashboard_id)
        if not dashboard:
            raise ResourceNotFoundException(f"Dashboard {dashboard_id} not found")
        if name:
            dashboard.name = name
        if source_entity is not None:
            dashboard.source_entity = source_entity
        if definition is not None:
            dashboard.definition = definition
        if parameters is not None:
            dashboard.parameters = parameters
        if version_description is not None:
            dashboard.version_description = version_description
        if dashboard_publish_options is not None:
            dashboard.dashboard_publish_options = dashboard_publish_options
        if theme_arn is not None:
            dashboard.theme_arn = theme_arn
        if validation_strategy is not None:
            dashboard.validation_strategy = validation_strategy
        dashboard.version_number += 1
        dashboard.last_updated_time = datetime.now()
        return dashboard

    def delete_dashboard(self, dashboard_id: str) -> QuicksightDashboard:
        dashboard = self.dashboards.pop(dashboard_id, None)
        if not dashboard:
            raise ResourceNotFoundException(f"Dashboard {dashboard_id} not found")
        return dashboard

    def list_dashboards(self, aws_account_id: str) -> list[dict[str, Any]]:
        dashboard_list: list[dict[str, Any]] = []
        for dashboard in self.dashboards.values():
            dashboard_list.append({
                "Arn": dashboard.arn,
                "DashboardId": dashboard.dashboard_id,
                "Name": dashboard.name,
                "CreatedTime": str(dashboard.created_time),
                "LastUpdatedTime": str(dashboard.last_updated_time),
                "PublishedVersionNumber": dashboard.version_number,
                "LastPublishedTime": str(dashboard.last_published_time),
            })
        return dashboard_list

    def list_dashboard_versions(self, dashboard_id: str) -> list[dict[str, Any]]:
        dashboard = self.dashboards.get(dashboard_id)
        if not dashboard:
            raise ResourceNotFoundException(f"Dashboard {dashboard_id} not found")
        return [{
            "Arn": dashboard.arn,
            "VersionNumber": dashboard.version_number,
            "Status": dashboard.status,
            "CreatedTime": str(dashboard.created_time),
            "Description": dashboard.version_description,
            "SourceEntityArn": dashboard.source_entity,
        }]

    def describe_dashboard_permissions(self, dashboard_id: str) -> QuicksightDashboard:
        dashboard = self.dashboards.get(dashboard_id)
        if not dashboard:
            raise ResourceNotFoundException(f"Dashboard {dashboard_id} not found")
        return dashboard

    def update_dashboard_permissions(
        self,
        dashboard_id: str,
        grant_permissions: Optional[list[dict[str, Any]]] = None,
        revoke_permissions: Optional[list[dict[str, Any]]] = None,
    ) -> QuicksightDashboard:
        dashboard = self.dashboards.get(dashboard_id)
        if not dashboard:
            raise ResourceNotFoundException(f"Dashboard {dashboard_id} not found")
        if grant_permissions:
            dashboard.permissions.extend(grant_permissions)
        if revoke_permissions:
            principals_to_revoke = {p.get("Principal") for p in revoke_permissions}
            dashboard.permissions = [
                p for p in dashboard.permissions
                if p.get("Principal") not in principals_to_revoke
            ]
        return dashboard

    def update_dashboard_published_version(
        self, dashboard_id: str, version_number: int
    ) -> QuicksightDashboard:
        dashboard = self.dashboards.get(dashboard_id)
        if not dashboard:
            raise ResourceNotFoundException(f"Dashboard {dashboard_id} not found")
        return dashboard

    def update_dashboard_links(
        self, dashboard_id: str, link_entities: list[str]
    ) -> QuicksightDashboard:
        dashboard = self.dashboards.get(dashboard_id)
        if not dashboard:
            raise ResourceNotFoundException(f"Dashboard {dashboard_id} not found")
        dashboard.link_entities = link_entities
        return dashboard

    # --- Account Settings ---

    def describe_account_settings(
        self, aws_account_id: str
    ) -> QuicksightAccountSettings:
        return self.account_settings

    def update_account_settings(
        self,
        aws_account_id: str,
        default_namespace: str,
        notification_email: str,
        termination_protection_enabled: bool,
    ) -> None:
        if notification_email:
            self.account_settings.notification_email = notification_email
        if termination_protection_enabled:
            self.account_settings.termination_protection_enabled = (
                termination_protection_enabled
            )

    def update_public_sharing_settings(
        self, aws_account_id: str, public_sharing_enabled: bool
    ) -> None:
        self.account_settings.public_sharing_enabled = public_sharing_enabled

    def describe_account_subscription(self, aws_account_id: str) -> dict[str, Any]:
        return {
            "AccountName": self.account_settings.account_name,
            "Edition": self.account_settings.edition,
            "NotificationEmail": self.account_settings.notification_email,
            "AccountSubscriptionStatus": "ACCOUNT_CREATED",
        }

    # --- Account Customization ---

    def create_account_customization(
        self, account_customization: dict[str, Any], namespace: Optional[str] = None,
        tags: Optional[list[dict[str, str]]] = None,
    ) -> QuicksightAccountCustomization:
        self.account_customization = QuicksightAccountCustomization(
            account_id=self.account_id,
            region=self.region_name,
            default_theme=account_customization.get("DefaultTheme"),
            default_email_customization_template=account_customization.get(
                "DefaultEmailCustomizationTemplate"
            ),
            namespace=namespace,
        )
        return self.account_customization

    def describe_account_customization(
        self, namespace: Optional[str] = None,
    ) -> QuicksightAccountCustomization:
        if not self.account_customization:
            raise ResourceNotFoundException("Account customization not found")
        return self.account_customization

    def update_account_customization(
        self, account_customization: dict[str, Any], namespace: Optional[str] = None,
    ) -> QuicksightAccountCustomization:
        if not self.account_customization:
            raise ResourceNotFoundException("Account customization not found")
        if "DefaultTheme" in account_customization:
            self.account_customization.default_theme = account_customization["DefaultTheme"]
        if "DefaultEmailCustomizationTemplate" in account_customization:
            self.account_customization.default_email_customization_template = (
                account_customization["DefaultEmailCustomizationTemplate"]
            )
        return self.account_customization

    def delete_account_customization(self, namespace: Optional[str] = None) -> None:
        self.account_customization = None

    # --- DataSource ---

    def create_data_source(
        self,
        aws_account_id: str,
        data_source_id: str,
        name: str,
        data_source_type: str,
        data_source_parameters: Optional[dict[str, dict[str, Any]]] = None,
        vpc_connection_properties: Optional[dict[str, Any]] = None,
        ssl_properties: Optional[dict[str, Any]] = None,
        tags: Optional[list[dict[str, str]]] = None,
    ) -> QuickSightDataSource:
        data_source = QuickSightDataSource(
            account_id=aws_account_id,
            region=self.region_name,
            data_source_id=data_source_id,
            name=name,
            status="CREATION_SUCCESSFUL",
            data_source_type=data_source_type,
            data_source_parameters=data_source_parameters,
            ssl_properties=ssl_properties,
            vpc_connection_properties=vpc_connection_properties,
            tags=tags,
        )
        if tags:
            self.tagger.tag_resource(arn=data_source.arn, tags=tags)
        self.data_sources[data_source_id] = data_source
        return data_source

    def update_data_source(
        self,
        aws_account_id: str,
        data_source_id: str,
        name: str,
        data_source_parameters: Optional[dict[str, Any]] = None,
        vpc_connection_properties: Optional[dict[str, Any]] = None,
        ssl_properties: Optional[dict[str, Any]] = None,
    ) -> QuickSightDataSource:
        data_source = self.data_sources.get(data_source_id)
        if not data_source:
            raise ResourceNotFoundException(f"DataSource {data_source_id} Not Found")
        data_source.name = name
        data_source.data_source_parameters = data_source_parameters
        data_source.last_updated_time = datetime.now()
        data_source.status = "UPDATE_SUCCESSFUL"
        return data_source

    def delete_data_source(
        self, aws_account_id: str, data_source_id: str
    ) -> QuickSightDataSource:
        data_source = self.data_sources.pop(data_source_id, None)
        if data_source is None:
            raise ResourceNotFoundException(f"DataSource {data_source_id} Not Found")
        return data_source

    def describe_data_source(
        self, aws_account_id: str, data_source_id: str
    ) -> QuickSightDataSource:
        data_source = self.data_sources.get(data_source_id)
        if not data_source:
            raise ResourceNotFoundException(f"DataSource {data_source_id} Not Found")
        return data_source

    def list_data_sources(self, aws_account_id: str) -> list[dict[str, Any]]:
        return [ds.to_json() for ds in self.data_sources.values()]

    def describe_data_source_permissions(
        self, aws_account_id: str, data_source_id: str
    ) -> QuickSightDataSource:
        data_source = self.data_sources.get(data_source_id)
        if not data_source:
            raise ResourceNotFoundException(f"DataSource {data_source_id} Not Found")
        return data_source

    def update_data_source_permissions(
        self, aws_account_id: str, data_source_id: str,
        grant_permissions: Optional[list[dict[str, Any]]] = None,
        revoke_permissions: Optional[list[dict[str, Any]]] = None,
    ) -> QuickSightDataSource:
        data_source = self.data_sources.get(data_source_id)
        if not data_source:
            raise ResourceNotFoundException(f"DataSource {data_source_id} Not Found")
        if grant_permissions:
            data_source.permissions.extend(grant_permissions)
        if revoke_permissions:
            principals_to_revoke = {p.get("Principal") for p in revoke_permissions}
            data_source.permissions = [
                p for p in data_source.permissions
                if p.get("Principal") not in principals_to_revoke
            ]
        return data_source

    # --- Analysis ---

    def create_analysis(
        self,
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
    ) -> QuicksightAnalysis:
        analysis = QuicksightAnalysis(
            account_id=self.account_id,
            region=self.region_name,
            analysis_id=analysis_id,
            name=name,
            source_entity=source_entity,
            definition=definition,
            parameters=parameters,
            permissions=permissions,
            tags=tags,
            theme_arn=theme_arn,
            validation_strategy=validation_strategy,
            folder_arns=folder_arns,
        )
        if tags:
            self.tagger.tag_resource(arn=analysis.arn, tags=tags)
        self.analyses[analysis_id] = analysis
        return analysis

    def describe_analysis(self, analysis_id: str) -> QuicksightAnalysis:
        analysis = self.analyses.get(analysis_id)
        if not analysis or analysis.deleted:
            raise ResourceNotFoundException(f"Analysis {analysis_id} not found")
        return analysis

    def describe_analysis_definition(self, analysis_id: str) -> QuicksightAnalysis:
        return self.describe_analysis(analysis_id)

    def describe_analysis_permissions(self, analysis_id: str) -> QuicksightAnalysis:
        return self.describe_analysis(analysis_id)

    def update_analysis(
        self,
        analysis_id: str,
        name: str,
        source_entity: Optional[dict[str, Any]] = None,
        definition: Optional[dict[str, Any]] = None,
        parameters: Optional[dict[str, Any]] = None,
        theme_arn: Optional[str] = None,
        validation_strategy: Optional[dict[str, str]] = None,
    ) -> QuicksightAnalysis:
        analysis = self.describe_analysis(analysis_id)
        if name:
            analysis.name = name
        if source_entity is not None:
            analysis.source_entity = source_entity
        if definition is not None:
            analysis.definition = definition
        if parameters is not None:
            analysis.parameters = parameters
        if theme_arn is not None:
            analysis.theme_arn = theme_arn
        analysis.last_updated_time = datetime.now()
        return analysis

    def update_analysis_permissions(
        self,
        analysis_id: str,
        grant_permissions: Optional[list[dict[str, Any]]] = None,
        revoke_permissions: Optional[list[dict[str, Any]]] = None,
    ) -> QuicksightAnalysis:
        analysis = self.describe_analysis(analysis_id)
        if grant_permissions:
            analysis.permissions.extend(grant_permissions)
        if revoke_permissions:
            principals_to_revoke = {p.get("Principal") for p in revoke_permissions}
            analysis.permissions = [
                p for p in analysis.permissions
                if p.get("Principal") not in principals_to_revoke
            ]
        return analysis

    def delete_analysis(self, analysis_id: str) -> QuicksightAnalysis:
        analysis = self.analyses.get(analysis_id)
        if not analysis:
            raise ResourceNotFoundException(f"Analysis {analysis_id} not found")
        analysis.deleted = True
        analysis.status = "DELETED"
        return analysis

    def restore_analysis(self, analysis_id: str) -> QuicksightAnalysis:
        analysis = self.analyses.get(analysis_id)
        if not analysis:
            raise ResourceNotFoundException(f"Analysis {analysis_id} not found")
        analysis.deleted = False
        analysis.status = "CREATION_SUCCESSFUL"
        return analysis

    def list_analyses(self) -> list[dict[str, Any]]:
        return [
            a.to_summary() for a in self.analyses.values() if not a.deleted
        ]

    # --- Template ---

    def create_template(
        self,
        template_id: str,
        name: str,
        source_entity: Optional[dict[str, Any]] = None,
        definition: Optional[dict[str, Any]] = None,
        permissions: Optional[list[dict[str, Any]]] = None,
        tags: Optional[list[dict[str, str]]] = None,
        version_description: Optional[str] = None,
        validation_strategy: Optional[dict[str, str]] = None,
    ) -> QuicksightTemplate:
        template = QuicksightTemplate(
            account_id=self.account_id,
            region=self.region_name,
            template_id=template_id,
            name=name,
            source_entity=source_entity,
            definition=definition,
            permissions=permissions,
            tags=tags,
            version_description=version_description,
            validation_strategy=validation_strategy,
        )
        if tags:
            self.tagger.tag_resource(arn=template.arn, tags=tags)
        self.templates[template_id] = template
        return template

    def describe_template(self, template_id: str) -> QuicksightTemplate:
        template = self.templates.get(template_id)
        if not template:
            raise ResourceNotFoundException(f"Template {template_id} not found")
        return template

    def describe_template_definition(self, template_id: str) -> QuicksightTemplate:
        return self.describe_template(template_id)

    def describe_template_permissions(self, template_id: str) -> QuicksightTemplate:
        return self.describe_template(template_id)

    def update_template(
        self,
        template_id: str,
        name: Optional[str] = None,
        source_entity: Optional[dict[str, Any]] = None,
        definition: Optional[dict[str, Any]] = None,
        version_description: Optional[str] = None,
        validation_strategy: Optional[dict[str, str]] = None,
    ) -> QuicksightTemplate:
        template = self.describe_template(template_id)
        if name:
            template.name = name
        if source_entity is not None:
            template.source_entity = source_entity
        if definition is not None:
            template.definition = definition
        if version_description is not None:
            template.version_description = version_description
        template.version_number += 1
        template.last_updated_time = datetime.now()
        return template

    def update_template_permissions(
        self,
        template_id: str,
        grant_permissions: Optional[list[dict[str, Any]]] = None,
        revoke_permissions: Optional[list[dict[str, Any]]] = None,
    ) -> QuicksightTemplate:
        template = self.describe_template(template_id)
        if grant_permissions:
            template.permissions.extend(grant_permissions)
        if revoke_permissions:
            principals_to_revoke = {p.get("Principal") for p in revoke_permissions}
            template.permissions = [
                p for p in template.permissions
                if p.get("Principal") not in principals_to_revoke
            ]
        return template

    def delete_template(self, template_id: str) -> QuicksightTemplate:
        template = self.templates.pop(template_id, None)
        if not template:
            raise ResourceNotFoundException(f"Template {template_id} not found")
        return template

    def list_templates(self) -> list[dict[str, Any]]:
        return [t.to_summary() for t in self.templates.values()]

    def list_template_versions(self, template_id: str) -> list[dict[str, Any]]:
        template = self.describe_template(template_id)
        return [{
            "Arn": template.arn,
            "VersionNumber": template.version_number,
            "Status": template.status,
            "CreatedTime": str(template.created_time),
            "Description": template.version_description,
        }]

    # --- Template Alias ---

    def create_template_alias(
        self, template_id: str, alias_name: str, template_version_number: int
    ) -> QuicksightTemplateAlias:
        template = self.describe_template(template_id)
        alias = QuicksightTemplateAlias(
            alias_name=alias_name,
            template_version_number=template_version_number,
            arn=f"{template.arn}/alias/{alias_name}",
        )
        template.aliases[alias_name] = alias
        return alias

    def describe_template_alias(
        self, template_id: str, alias_name: str
    ) -> QuicksightTemplateAlias:
        template = self.describe_template(template_id)
        alias = template.aliases.get(alias_name)
        if not alias:
            raise ResourceNotFoundException(f"Template alias {alias_name} not found")
        return alias

    def update_template_alias(
        self, template_id: str, alias_name: str, template_version_number: int
    ) -> QuicksightTemplateAlias:
        template = self.describe_template(template_id)
        alias = template.aliases.get(alias_name)
        if not alias:
            raise ResourceNotFoundException(f"Template alias {alias_name} not found")
        alias.template_version_number = template_version_number
        return alias

    def delete_template_alias(
        self, template_id: str, alias_name: str
    ) -> QuicksightTemplateAlias:
        template = self.describe_template(template_id)
        alias = template.aliases.pop(alias_name, None)
        if not alias:
            raise ResourceNotFoundException(f"Template alias {alias_name} not found")
        return alias

    def list_template_aliases(self, template_id: str) -> list[dict[str, Any]]:
        template = self.describe_template(template_id)
        return [a.to_dict() for a in template.aliases.values()]

    # --- Theme ---

    def create_theme(
        self,
        theme_id: str,
        name: str,
        base_theme_id: Optional[str] = None,
        configuration: Optional[dict[str, Any]] = None,
        permissions: Optional[list[dict[str, Any]]] = None,
        tags: Optional[list[dict[str, str]]] = None,
        version_description: Optional[str] = None,
    ) -> QuicksightTheme:
        theme = QuicksightTheme(
            account_id=self.account_id,
            region=self.region_name,
            theme_id=theme_id,
            name=name,
            base_theme_id=base_theme_id,
            configuration=configuration,
            permissions=permissions,
            tags=tags,
            version_description=version_description,
        )
        if tags:
            self.tagger.tag_resource(arn=theme.arn, tags=tags)
        self.themes[theme_id] = theme
        return theme

    def describe_theme(self, theme_id: str) -> QuicksightTheme:
        theme = self.themes.get(theme_id)
        if not theme:
            raise ResourceNotFoundException(f"Theme {theme_id} not found")
        return theme

    def describe_theme_permissions(self, theme_id: str) -> QuicksightTheme:
        return self.describe_theme(theme_id)

    def update_theme(
        self,
        theme_id: str,
        name: Optional[str] = None,
        base_theme_id: Optional[str] = None,
        configuration: Optional[dict[str, Any]] = None,
        version_description: Optional[str] = None,
    ) -> QuicksightTheme:
        theme = self.describe_theme(theme_id)
        if name:
            theme.name = name
        if base_theme_id is not None:
            theme.base_theme_id = base_theme_id
        if configuration is not None:
            theme.configuration = configuration
        if version_description is not None:
            theme.version_description = version_description
        theme.version_number += 1
        theme.last_updated_time = datetime.now()
        return theme

    def update_theme_permissions(
        self,
        theme_id: str,
        grant_permissions: Optional[list[dict[str, Any]]] = None,
        revoke_permissions: Optional[list[dict[str, Any]]] = None,
    ) -> QuicksightTheme:
        theme = self.describe_theme(theme_id)
        if grant_permissions:
            theme.permissions.extend(grant_permissions)
        if revoke_permissions:
            principals_to_revoke = {p.get("Principal") for p in revoke_permissions}
            theme.permissions = [
                p for p in theme.permissions
                if p.get("Principal") not in principals_to_revoke
            ]
        return theme

    def delete_theme(self, theme_id: str) -> QuicksightTheme:
        theme = self.themes.pop(theme_id, None)
        if not theme:
            raise ResourceNotFoundException(f"Theme {theme_id} not found")
        return theme

    def list_themes(self) -> list[dict[str, Any]]:
        return [t.to_summary() for t in self.themes.values()]

    def list_theme_versions(self, theme_id: str) -> list[dict[str, Any]]:
        theme = self.describe_theme(theme_id)
        return [{
            "Arn": theme.arn,
            "VersionNumber": theme.version_number,
            "Status": theme.status,
            "CreatedTime": str(theme.created_time),
            "Description": theme.version_description,
        }]

    # --- Theme Alias ---

    def create_theme_alias(
        self, theme_id: str, alias_name: str, theme_version_number: int
    ) -> QuicksightThemeAlias:
        theme = self.describe_theme(theme_id)
        alias = QuicksightThemeAlias(
            alias_name=alias_name,
            theme_version_number=theme_version_number,
            arn=f"{theme.arn}/alias/{alias_name}",
        )
        theme.aliases[alias_name] = alias
        return alias

    def describe_theme_alias(
        self, theme_id: str, alias_name: str
    ) -> QuicksightThemeAlias:
        theme = self.describe_theme(theme_id)
        alias = theme.aliases.get(alias_name)
        if not alias:
            raise ResourceNotFoundException(f"Theme alias {alias_name} not found")
        return alias

    def update_theme_alias(
        self, theme_id: str, alias_name: str, theme_version_number: int
    ) -> QuicksightThemeAlias:
        theme = self.describe_theme(theme_id)
        alias = theme.aliases.get(alias_name)
        if not alias:
            raise ResourceNotFoundException(f"Theme alias {alias_name} not found")
        alias.theme_version_number = theme_version_number
        return alias

    def delete_theme_alias(
        self, theme_id: str, alias_name: str
    ) -> QuicksightThemeAlias:
        theme = self.describe_theme(theme_id)
        alias = theme.aliases.pop(alias_name, None)
        if not alias:
            raise ResourceNotFoundException(f"Theme alias {alias_name} not found")
        return alias

    def list_theme_aliases(self, theme_id: str) -> list[dict[str, Any]]:
        theme = self.describe_theme(theme_id)
        return [a.to_dict() for a in theme.aliases.values()]

    # --- Folder ---

    def create_folder(
        self,
        folder_id: str,
        name: str,
        folder_type: Optional[str] = None,
        parent_folder_arn: Optional[str] = None,
        permissions: Optional[list[dict[str, Any]]] = None,
        tags: Optional[list[dict[str, str]]] = None,
        sharing_model: Optional[str] = None,
    ) -> QuicksightFolder:
        folder = QuicksightFolder(
            account_id=self.account_id,
            region=self.region_name,
            folder_id=folder_id,
            name=name,
            folder_type=folder_type,
            parent_folder_arn=parent_folder_arn,
            permissions=permissions,
            tags=tags,
            sharing_model=sharing_model,
        )
        if tags:
            self.tagger.tag_resource(arn=folder.arn, tags=tags)
        self.folders[folder_id] = folder
        return folder

    def describe_folder(self, folder_id: str) -> QuicksightFolder:
        folder = self.folders.get(folder_id)
        if not folder:
            raise ResourceNotFoundException(f"Folder {folder_id} not found")
        return folder

    def describe_folder_permissions(self, folder_id: str) -> QuicksightFolder:
        return self.describe_folder(folder_id)

    def describe_folder_resolved_permissions(self, folder_id: str) -> QuicksightFolder:
        return self.describe_folder(folder_id)

    def update_folder(self, folder_id: str, name: str) -> QuicksightFolder:
        folder = self.describe_folder(folder_id)
        if name:
            folder.name = name
        folder.last_updated_time = datetime.now()
        return folder

    def update_folder_permissions(
        self,
        folder_id: str,
        grant_permissions: Optional[list[dict[str, Any]]] = None,
        revoke_permissions: Optional[list[dict[str, Any]]] = None,
    ) -> QuicksightFolder:
        folder = self.describe_folder(folder_id)
        if grant_permissions:
            folder.permissions.extend(grant_permissions)
        if revoke_permissions:
            principals_to_revoke = {p.get("Principal") for p in revoke_permissions}
            folder.permissions = [
                p for p in folder.permissions
                if p.get("Principal") not in principals_to_revoke
            ]
        return folder

    def delete_folder(self, folder_id: str) -> QuicksightFolder:
        folder = self.folders.pop(folder_id, None)
        if not folder:
            raise ResourceNotFoundException(f"Folder {folder_id} not found")
        return folder

    def list_folders(self) -> list[dict[str, Any]]:
        return [f.to_summary() for f in self.folders.values()]

    def create_folder_membership(
        self, folder_id: str, member_type: str, member_id: str
    ) -> dict[str, Any]:
        folder = self.describe_folder(folder_id)
        # Build the member ARN based on member type
        member_arn = f"arn:aws:quicksight:{self.region_name}:{self.account_id}:{member_type.lower()}/{member_id}"
        folder.members[(member_type, member_id)] = member_arn
        return {
            "Status": 200,
            "FolderMember": {
                "MemberId": member_id,
                "MemberArn": member_arn,
            },
        }

    def delete_folder_membership(
        self, folder_id: str, member_type: str, member_id: str
    ) -> None:
        folder = self.describe_folder(folder_id)
        folder.members.pop((member_type, member_id), None)

    def list_folder_members(self, folder_id: str) -> list[dict[str, Any]]:
        folder = self.describe_folder(folder_id)
        return [
            {"MemberId": mid, "MemberArn": marn}
            for (mtype, mid), marn in folder.members.items()
        ]

    # --- Namespace ---

    def create_namespace(
        self,
        namespace: str,
        identity_store: Optional[str] = None,
        tags: Optional[list[dict[str, str]]] = None,
    ) -> QuicksightNamespace:
        ns = QuicksightNamespace(
            account_id=self.account_id,
            region=self.region_name,
            namespace=namespace,
            identity_store=identity_store,
            tags=tags,
        )
        if tags:
            self.tagger.tag_resource(arn=ns.arn, tags=tags)
        self.namespaces[namespace] = ns
        return ns

    def describe_namespace(self, namespace: str) -> QuicksightNamespace:
        ns = self.namespaces.get(namespace)
        if not ns:
            raise ResourceNotFoundException(f"Namespace {namespace} not found")
        return ns

    def delete_namespace(self, namespace: str) -> None:
        if namespace not in self.namespaces:
            raise ResourceNotFoundException(f"Namespace {namespace} not found")
        self.namespaces.pop(namespace)

    def list_namespaces(self) -> list[dict[str, Any]]:
        return [ns.to_dict() for ns in self.namespaces.values()]

    # --- Topic ---

    def create_topic(
        self,
        topic_id: str,
        name: str,
        description: Optional[str] = None,
        data_sets: Optional[list[dict[str, Any]]] = None,
        tags: Optional[list[dict[str, str]]] = None,
    ) -> QuicksightTopic:
        topic = QuicksightTopic(
            account_id=self.account_id,
            region=self.region_name,
            topic_id=topic_id,
            name=name,
            description=description,
            data_sets=data_sets,
            tags=tags,
        )
        if tags:
            self.tagger.tag_resource(arn=topic.arn, tags=tags)
        self.topics[topic_id] = topic
        return topic

    def describe_topic(self, topic_id: str) -> QuicksightTopic:
        topic = self.topics.get(topic_id)
        if not topic:
            raise ResourceNotFoundException(f"Topic {topic_id} not found")
        return topic

    def describe_topic_permissions(self, topic_id: str) -> QuicksightTopic:
        return self.describe_topic(topic_id)

    def update_topic(
        self,
        topic_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        data_sets: Optional[list[dict[str, Any]]] = None,
    ) -> QuicksightTopic:
        topic = self.describe_topic(topic_id)
        if name:
            topic.name = name
        if description is not None:
            topic.description = description
        if data_sets is not None:
            topic.data_sets = data_sets
        return topic

    def update_topic_permissions(
        self,
        topic_id: str,
        grant_permissions: Optional[list[dict[str, Any]]] = None,
        revoke_permissions: Optional[list[dict[str, Any]]] = None,
    ) -> QuicksightTopic:
        topic = self.describe_topic(topic_id)
        if grant_permissions:
            topic.permissions.extend(grant_permissions)
        if revoke_permissions:
            principals_to_revoke = {p.get("Principal") for p in revoke_permissions}
            topic.permissions = [
                p for p in topic.permissions
                if p.get("Principal") not in principals_to_revoke
            ]
        return topic

    def delete_topic(self, topic_id: str) -> None:
        if topic_id not in self.topics:
            raise ResourceNotFoundException(f"Topic {topic_id} not found")
        self.topics.pop(topic_id)

    def list_topics(self) -> list[dict[str, Any]]:
        return [t.to_summary() for t in self.topics.values()]

    # --- Topic Refresh Schedule ---

    def create_topic_refresh_schedule(
        self, topic_id: str, dataset_arn: str, refresh_schedule: dict[str, Any]
    ) -> dict[str, Any]:
        topic = self.describe_topic(topic_id)
        dataset_id = dataset_arn.split("/")[-1] if dataset_arn else ""
        topic.refresh_schedules[dataset_id] = refresh_schedule
        return {"TopicId": topic_id, "TopicArn": topic.arn, "DatasetArn": dataset_arn}

    def describe_topic_refresh_schedule(
        self, topic_id: str, dataset_id: str
    ) -> dict[str, Any]:
        topic = self.describe_topic(topic_id)
        schedule = topic.refresh_schedules.get(dataset_id)
        if not schedule:
            raise ResourceNotFoundException(f"TopicRefreshSchedule for {dataset_id} not found")
        return {"TopicId": topic_id, "TopicArn": topic.arn, "DatasetArn": dataset_id, "RefreshSchedule": schedule}

    def delete_topic_refresh_schedule(
        self, topic_id: str, dataset_id: str
    ) -> None:
        topic = self.describe_topic(topic_id)
        topic.refresh_schedules.pop(dataset_id, None)

    def list_topic_refresh_schedules(self, topic_id: str) -> dict[str, Any]:
        topic = self.describe_topic(topic_id)
        schedules = [
            {"DatasetId": did, "DatasetArn": did, "RefreshSchedule": sched}
            for did, sched in topic.refresh_schedules.items()
        ]
        return {"TopicId": topic_id, "TopicArn": topic.arn, "RefreshSchedules": schedules}

    # --- Topic Reviewed Answers ---

    def batch_create_topic_reviewed_answer(
        self, topic_id: str, answers: list[dict[str, Any]]
    ) -> dict[str, Any]:
        topic = self.describe_topic(topic_id)
        topic.reviewed_answers.extend(answers)
        return {"TopicId": topic_id, "TopicArn": topic.arn, "SucceededAnswers": answers, "InvalidAnswers": []}

    def batch_delete_topic_reviewed_answer(
        self, topic_id: str, answer_ids: list[str]
    ) -> dict[str, Any]:
        topic = self.describe_topic(topic_id)
        answer_id_set = set(answer_ids)
        topic.reviewed_answers = [
            a for a in topic.reviewed_answers
            if a.get("AnswerId") not in answer_id_set
        ]
        return {"TopicId": topic_id, "TopicArn": topic.arn, "SucceededAnswers": [{"AnswerId": aid} for aid in answer_ids], "InvalidAnswers": []}

    def list_topic_reviewed_answers(self, topic_id: str) -> dict[str, Any]:
        topic = self.describe_topic(topic_id)
        return {"TopicId": topic_id, "TopicArn": topic.arn, "Answers": topic.reviewed_answers}

    # --- VPCConnection ---

    def create_vpc_connection(
        self,
        vpc_connection_id: str,
        name: str,
        subnet_ids: Optional[list[str]] = None,
        security_group_ids: Optional[list[str]] = None,
        dns_resolvers: Optional[list[str]] = None,
        role_arn: Optional[str] = None,
        tags: Optional[list[dict[str, str]]] = None,
    ) -> QuicksightVPCConnection:
        vpc = QuicksightVPCConnection(
            account_id=self.account_id,
            region=self.region_name,
            vpc_connection_id=vpc_connection_id,
            name=name,
            subnet_ids=subnet_ids,
            security_group_ids=security_group_ids,
            dns_resolvers=dns_resolvers,
            role_arn=role_arn,
            tags=tags,
        )
        if tags:
            self.tagger.tag_resource(arn=vpc.arn, tags=tags)
        self.vpc_connections[vpc_connection_id] = vpc
        return vpc

    def describe_vpc_connection(self, vpc_connection_id: str) -> QuicksightVPCConnection:
        vpc = self.vpc_connections.get(vpc_connection_id)
        if not vpc:
            raise ResourceNotFoundException(f"VPCConnection {vpc_connection_id} not found")
        return vpc

    def update_vpc_connection(
        self,
        vpc_connection_id: str,
        name: Optional[str] = None,
        subnet_ids: Optional[list[str]] = None,
        security_group_ids: Optional[list[str]] = None,
        dns_resolvers: Optional[list[str]] = None,
        role_arn: Optional[str] = None,
    ) -> QuicksightVPCConnection:
        vpc = self.describe_vpc_connection(vpc_connection_id)
        if name:
            vpc.name = name
        if subnet_ids is not None:
            vpc.subnet_ids = subnet_ids
        if security_group_ids is not None:
            vpc.security_group_ids = security_group_ids
        if dns_resolvers is not None:
            vpc.dns_resolvers = dns_resolvers
        if role_arn is not None:
            vpc.role_arn = role_arn
        vpc.last_updated_time = datetime.now()
        vpc.status = "UPDATE_SUCCESSFUL"
        return vpc

    def delete_vpc_connection(self, vpc_connection_id: str) -> QuicksightVPCConnection:
        vpc = self.vpc_connections.pop(vpc_connection_id, None)
        if not vpc:
            raise ResourceNotFoundException(f"VPCConnection {vpc_connection_id} not found")
        vpc.status = "DELETED"
        vpc.availability_status = "PARTIALLY_AVAILABLE"
        return vpc

    def list_vpc_connections(self) -> list[dict[str, Any]]:
        return [v.to_summary() for v in self.vpc_connections.values()]

    # --- RefreshSchedule ---

    def create_refresh_schedule(
        self, data_set_id: str, schedule: dict[str, Any]
    ) -> QuicksightRefreshSchedule:
        rs = QuicksightRefreshSchedule(
            account_id=self.account_id,
            region=self.region_name,
            data_set_id=data_set_id,
            schedule=schedule,
        )
        if data_set_id not in self.refresh_schedules:
            self.refresh_schedules[data_set_id] = {}
        self.refresh_schedules[data_set_id][rs.schedule_id] = rs
        return rs

    def describe_refresh_schedule(
        self, data_set_id: str, schedule_id: str
    ) -> QuicksightRefreshSchedule:
        schedules = self.refresh_schedules.get(data_set_id, {})
        rs = schedules.get(schedule_id)
        if not rs:
            raise ResourceNotFoundException(f"RefreshSchedule {schedule_id} not found")
        return rs

    def update_refresh_schedule(
        self, data_set_id: str, schedule: dict[str, Any]
    ) -> QuicksightRefreshSchedule:
        schedule_id = schedule.get("ScheduleId", "")
        schedules = self.refresh_schedules.get(data_set_id, {})
        rs = schedules.get(schedule_id)
        if not rs:
            raise ResourceNotFoundException(f"RefreshSchedule {schedule_id} not found")
        rs.schedule = schedule
        return rs

    def delete_refresh_schedule(
        self, data_set_id: str, schedule_id: str
    ) -> None:
        schedules = self.refresh_schedules.get(data_set_id, {})
        schedules.pop(schedule_id, None)

    def list_refresh_schedules(self, data_set_id: str) -> list[dict[str, Any]]:
        schedules = self.refresh_schedules.get(data_set_id, {})
        return [rs.to_dict() for rs in schedules.values()]

    # --- IAM Policy Assignment ---

    def create_iam_policy_assignment(
        self,
        namespace: str,
        assignment_name: str,
        assignment_status: Optional[str] = None,
        policy_arn: Optional[str] = None,
        identities: Optional[dict[str, list[str]]] = None,
    ) -> QuicksightIAMPolicyAssignment:
        assignment = QuicksightIAMPolicyAssignment(
            account_id=self.account_id,
            region=self.region_name,
            namespace=namespace,
            assignment_name=assignment_name,
            assignment_status=assignment_status,
            policy_arn=policy_arn,
            identities=identities,
        )
        if namespace not in self.iam_policy_assignments:
            self.iam_policy_assignments[namespace] = {}
        self.iam_policy_assignments[namespace][assignment_name] = assignment
        return assignment

    def describe_iam_policy_assignment(
        self, namespace: str, assignment_name: str
    ) -> QuicksightIAMPolicyAssignment:
        assignments = self.iam_policy_assignments.get(namespace, {})
        assignment = assignments.get(assignment_name)
        if not assignment:
            raise ResourceNotFoundException(f"IAMPolicyAssignment {assignment_name} not found")
        return assignment

    def update_iam_policy_assignment(
        self,
        namespace: str,
        assignment_name: str,
        assignment_status: Optional[str] = None,
        policy_arn: Optional[str] = None,
        identities: Optional[dict[str, list[str]]] = None,
    ) -> QuicksightIAMPolicyAssignment:
        assignment = self.describe_iam_policy_assignment(namespace, assignment_name)
        if assignment_status:
            assignment.assignment_status = assignment_status
        if policy_arn is not None:
            assignment.policy_arn = policy_arn
        if identities is not None:
            assignment.identities = identities
        return assignment

    def delete_iam_policy_assignment(
        self, namespace: str, assignment_name: str
    ) -> None:
        assignments = self.iam_policy_assignments.get(namespace, {})
        if assignment_name not in assignments:
            raise ResourceNotFoundException(f"IAMPolicyAssignment {assignment_name} not found")
        assignments.pop(assignment_name)

    def list_iam_policy_assignments(
        self, namespace: str
    ) -> list[dict[str, Any]]:
        assignments = self.iam_policy_assignments.get(namespace, {})
        return [
            {
                "AssignmentName": a.assignment_name,
                "AssignmentStatus": a.assignment_status,
            }
            for a in assignments.values()
        ]

    def list_iam_policy_assignments_for_user(
        self, namespace: str, user_name: str
    ) -> list[dict[str, Any]]:
        assignments = self.iam_policy_assignments.get(namespace, {})
        result = []
        for a in assignments.values():
            users = a.identities.get("User", []) + a.identities.get("user", [])
            if user_name in users:
                result.append({
                    "AssignmentName": a.assignment_name,
                    "AssignmentStatus": a.assignment_status,
                })
        return result

    # --- IP Restriction ---

    def describe_ip_restriction(self) -> dict[str, Any]:
        return self.ip_restriction

    def update_ip_restriction(
        self, ip_restriction_rule_map: Optional[dict[str, str]] = None,
        vpc_id_restriction_rule_map: Optional[dict[str, str]] = None,
        vpc_endpoint_id_restriction_rule_map: Optional[dict[str, str]] = None,
        enabled: Optional[bool] = None,
    ) -> None:
        if ip_restriction_rule_map is not None:
            self.ip_restriction["IpRestrictionRuleMap"] = ip_restriction_rule_map
        if vpc_id_restriction_rule_map is not None:
            self.ip_restriction["VpcIdRestrictionRuleMap"] = vpc_id_restriction_rule_map
        if vpc_endpoint_id_restriction_rule_map is not None:
            self.ip_restriction["VpcEndpointIdRestrictionRuleMap"] = vpc_endpoint_id_restriction_rule_map
        if enabled is not None:
            self.ip_restriction["Enabled"] = enabled

    # --- Embed URLs ---

    def generate_embed_url_for_anonymous_user(self) -> str:
        return f"https://quicksight.{self.region_name}.amazonaws.com/embed/mock-anonymous-url"

    def generate_embed_url_for_registered_user(self) -> str:
        return f"https://quicksight.{self.region_name}.amazonaws.com/embed/mock-registered-url"

    def get_dashboard_embed_url(self, dashboard_id: str) -> str:
        self.dashboards.get(dashboard_id)  # Validate dashboard exists
        return f"https://quicksight.{self.region_name}.amazonaws.com/embed/dashboard/{dashboard_id}"

    def get_session_embed_url(self) -> str:
        return f"https://quicksight.{self.region_name}.amazonaws.com/embed/mock-session-url"

    # --- Search operations ---

    def search_analyses(self, filters: list[dict[str, Any]]) -> list[dict[str, Any]]:
        return [a.to_summary() for a in self.analyses.values() if not a.deleted]

    def search_dashboards(self, filters: list[dict[str, Any]]) -> list[dict[str, Any]]:
        return self.list_dashboards(self.account_id)

    def search_data_sets(self, filters: list[dict[str, Any]]) -> list[dict[str, Any]]:
        return self.list_data_sets()

    def search_data_sources(self, filters: list[dict[str, Any]]) -> list[dict[str, Any]]:
        return self.list_data_sources(self.account_id)

    def search_folders(self, filters: list[dict[str, Any]]) -> list[dict[str, Any]]:
        return self.list_folders()

    def search_topics(self, filters: list[dict[str, Any]]) -> list[dict[str, Any]]:
        return self.list_topics()

    # --- Role Membership ---

    def create_role_membership(
        self, namespace: str, role: str, member_name: str
    ) -> None:
        if role not in self.role_memberships:
            self.role_memberships[role] = {}
        if namespace not in self.role_memberships[role]:
            self.role_memberships[role][namespace] = set()
        self.role_memberships[role][namespace].add(member_name)

    def delete_role_membership(
        self, namespace: str, role: str, member_name: str
    ) -> None:
        members = self.role_memberships.get(role, {}).get(namespace, set())
        members.discard(member_name)

    def list_role_memberships(
        self, namespace: str, role: str
    ) -> list[str]:
        return sorted(self.role_memberships.get(role, {}).get(namespace, set()))

    def describe_role_custom_permission(
        self, namespace: str, role: str
    ) -> Optional[str]:
        return self.role_custom_permissions.get(role, {}).get(namespace)

    def update_role_custom_permission(
        self, namespace: str, role: str, custom_permissions_name: str
    ) -> None:
        if role not in self.role_custom_permissions:
            self.role_custom_permissions[role] = {}
        self.role_custom_permissions[role][namespace] = custom_permissions_name

    def delete_role_custom_permission(
        self, namespace: str, role: str
    ) -> None:
        if role in self.role_custom_permissions:
            self.role_custom_permissions[role].pop(namespace, None)

    # --- Tagging ---

    def tag_resource(self, resource_arn: str, tags: list[dict[str, str]]) -> None:
        self.tagger.tag_resource(arn=resource_arn, tags=tags)

    def untag_resource(self, resource_arn: str, tag_keys: list[str]) -> None:
        self.tagger.untag_resource_using_names(resource_arn, tag_keys)

    def list_tags_for_resource(self, arn: str) -> list[dict[str, str]]:
        tags = self.tagger.list_tags_for_resource(arn)
        return tags.get("Tags", [])


quicksight_backends = BackendDict(QuickSightBackend, "quicksight")
