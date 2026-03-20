"""Handles incoming quicksight requests, invokes methods, returns responses."""

import json
from urllib.parse import unquote

from moto.core.common_types import TYPE_RESPONSE
from moto.core.responses import BaseResponse

from .models import QuickSightBackend, quicksight_backends


class QuickSightResponse(BaseResponse):
    def __init__(self) -> None:
        super().__init__(service_name="quicksight")

    @property
    def quicksight_backend(self) -> QuickSightBackend:
        """Return backend instance specific for this region."""
        return quicksight_backends[self.current_account][self.region]

    # --- DataSet ---

    def create_data_set(self) -> str:
        params = json.loads(self.body)
        data_set_id = params.get("DataSetId")
        name = params.get("Name")
        tags = self._get_param("Tags")
        data_set = self.quicksight_backend.create_data_set(data_set_id, name, tags)
        return json.dumps(data_set.to_json())

    def describe_data_set(self) -> str:
        data_set_id = self._get_param("DataSetId")
        data_set = self.quicksight_backend.describe_data_set(data_set_id)
        return json.dumps({"DataSet": data_set.to_json(), "Status": 200, "RequestId": "request_id"})

    def delete_data_set(self) -> str:
        data_set_id = self._get_param("DataSetId")
        data_set = self.quicksight_backend.delete_data_set(data_set_id)
        return json.dumps({"Arn": data_set.arn, "DataSetId": data_set._id, "Status": 200, "RequestId": "request_id"})

    def list_data_sets(self) -> str:
        data_sets = self.quicksight_backend.list_data_sets()
        return json.dumps({"DataSetSummaries": data_sets, "Status": 200, "RequestId": "request_id"})

    def update_data_set(self) -> str:
        data_set_id = self._get_param("DataSetId")
        params = json.loads(self.body)
        name = params.get("Name")
        data_set = self.quicksight_backend.update_data_set(data_set_id, name)
        return json.dumps({"Arn": data_set.arn, "DataSetId": data_set._id, "Status": 200, "RequestId": "request_id"})

    def describe_data_set_permissions(self) -> str:
        data_set_id = self._get_param("DataSetId")
        arn, dsid, permissions = self.quicksight_backend.describe_data_set_permissions(data_set_id)
        return json.dumps({"DataSetArn": arn, "DataSetId": dsid, "Permissions": permissions, "Status": 200, "RequestId": "request_id"})

    def update_data_set_permissions(self) -> str:
        data_set_id = self._get_param("DataSetId")
        params = json.loads(self.body)
        arn, dsid = self.quicksight_backend.update_data_set_permissions(
            data_set_id,
            grant_permissions=params.get("GrantPermissions"),
            revoke_permissions=params.get("RevokePermissions"),
        )
        return json.dumps({"DataSetArn": arn, "DataSetId": dsid, "Status": 200, "RequestId": "request_id"})

    def delete_data_set_refresh_properties(self) -> str:
        return json.dumps({"Status": 200, "RequestId": "request_id"})

    def put_data_set_refresh_properties(self) -> str:
        return json.dumps({"Status": 200, "RequestId": "request_id"})

    def describe_data_set_refresh_properties(self) -> str:
        return json.dumps({"Status": 200, "RequestId": "request_id"})

    # --- Group ---

    def create_group(self) -> str:
        params = json.loads(self.body)
        group_name = params.get("GroupName")
        description = params.get("Description")
        aws_account_id = self._get_param("AwsAccountId")
        namespace = self._get_param("Namespace")
        group = self.quicksight_backend.create_group(
            group_name=group_name,
            description=description,
            aws_account_id=aws_account_id,
            namespace=namespace,
        )
        return json.dumps({"Group": group.to_json()})

    def create_group_membership(self) -> str:
        aws_account_id = self._get_param("AwsAccountId")
        namespace = self._get_param("Namespace")
        group_name = unquote(self._get_param("GroupName"))
        member_name = unquote(self._get_param("MemberName"))
        member = self.quicksight_backend.create_group_membership(
            aws_account_id, namespace, group_name, member_name
        )
        return json.dumps({"GroupMember": member.to_json()})

    def delete_group_membership(self) -> TYPE_RESPONSE:
        aws_account_id = self._get_param("AwsAccountId")
        namespace = self._get_param("Namespace")
        group_name = unquote(self._get_param("GroupName"))
        member_name = unquote(self._get_param("MemberName"))
        self.quicksight_backend.delete_group_membership(
            aws_account_id, namespace, group_name, member_name
        )
        return 200, {"status": 200}, json.dumps({"RequestId": "request_id", "Status": 200})

    def describe_group_membership(self) -> str:
        aws_account_id = self._get_param("AwsAccountId")
        namespace = self._get_param("Namespace")
        group_name = unquote(self._get_param("GroupName"))
        member_name = unquote(self._get_param("MemberName"))
        member = self.quicksight_backend.describe_group_membership(
            aws_account_id, namespace, group_name, member_name
        )
        return json.dumps({"GroupMember": member.to_json()})

    def list_groups(self) -> str:
        max_results = self._get_int_param("max-results")
        next_token = self._get_param("next-token")
        aws_account_id = self._get_param("AwsAccountId")
        namespace = self._get_param("Namespace")
        groups, next_token = self.quicksight_backend.list_groups(
            aws_account_id, namespace, max_results=max_results, next_token=next_token
        )
        return json.dumps(
            {"NextToken": next_token, "GroupList": [g.to_json() for g in groups]}
        )

    def list_group_memberships(self) -> str:
        max_results = self._get_int_param("max-results")
        next_token = self._get_param("next-token")
        aws_account_id = self._get_param("AwsAccountId")
        namespace = self._get_param("Namespace")
        group_name = unquote(self._get_param("GroupName"))
        members, next_token = self.quicksight_backend.list_group_memberships(
            aws_account_id,
            namespace,
            group_name,
            max_results=max_results,
            next_token=next_token,
        )
        return json.dumps(
            {"NextToken": next_token, "GroupMemberList": [m.to_json() for m in members]}
        )

    def describe_group(self) -> str:
        aws_account_id = self._get_param("AwsAccountId")
        namespace = self._get_param("Namespace")
        group_name = unquote(self._get_param("GroupName"))
        group = self.quicksight_backend.describe_group(
            aws_account_id, namespace, group_name
        )
        return json.dumps({"Group": group.to_json()})

    def delete_group(self) -> TYPE_RESPONSE:
        aws_account_id = self._get_param("AwsAccountId")
        namespace = self._get_param("Namespace")
        group_name = unquote(self._get_param("GroupName"))
        self.quicksight_backend.delete_group(aws_account_id, namespace, group_name)
        return 204, {"status": 204}, json.dumps({"Status": 204})

    def update_group(self) -> str:
        aws_account_id = self._get_param("AwsAccountId")
        namespace = self._get_param("Namespace")
        group_name = unquote(self._get_param("GroupName"))
        description = json.loads(self.body).get("Description")
        group = self.quicksight_backend.update_group(
            aws_account_id, namespace, group_name, description
        )
        return json.dumps({"Group": group.to_json()})

    def search_groups(self) -> str:
        max_results = self._get_int_param("max-results")
        next_token = self._get_param("next-token")
        aws_account_id = self._get_param("AwsAccountId")
        namespace = self._get_param("Namespace")
        body = json.loads(self.body)
        groups, next_token = self.quicksight_backend.search_groups(
            aws_account_id,
            namespace,
            body.get("Filters", None),
            max_results=max_results,
            next_token=next_token,
        )
        return json.dumps(
            {"NextToken": next_token, "GroupList": [g.to_json() for g in groups]}
        )

    # --- User ---

    def register_user(self) -> str:
        params = json.loads(self.body)
        identity_type = params.get("IdentityType")
        email = params.get("Email")
        user_role = params.get("UserRole")
        aws_account_id = self._get_param("AwsAccountId")
        namespace = self._get_param("Namespace")
        user_name = params.get("UserName")
        tags = params.get("Tags")
        user = self.quicksight_backend.register_user(
            identity_type=identity_type,
            email=email,
            user_role=user_role,
            aws_account_id=aws_account_id,
            namespace=namespace,
            user_name=user_name,
            tags=tags,
        )
        return json.dumps({"User": user.to_json(), "UserInvitationUrl": "TBD"})

    def update_user(self) -> str:
        aws_account_id = self._get_param("AwsAccountId")
        namespace = self._get_param("Namespace")
        user_name = unquote(self._get_param("UserName"))
        body = json.loads(self.body)
        email = body.get("Email", None)
        user_role = body.get("Role", None)
        user = self.quicksight_backend.update_user(
            aws_account_id, namespace, user_name, email, user_role
        )
        return json.dumps({"User": user.to_json()})

    def describe_user(self) -> str:
        aws_account_id = self._get_param("AwsAccountId")
        namespace = self._get_param("Namespace")
        user_name = unquote(self._get_param("UserName"))
        user = self.quicksight_backend.describe_user(
            aws_account_id, namespace, user_name
        )
        return json.dumps({"User": user.to_json()})

    def delete_user(self) -> TYPE_RESPONSE:
        aws_account_id = self._get_param("AwsAccountId")
        namespace = self._get_param("Namespace")
        user_name = unquote(self._get_param("UserName"))
        self.quicksight_backend.delete_user(aws_account_id, namespace, user_name)
        return 204, {"status": 204}, json.dumps({"Status": 204})

    def delete_user_by_principal_id(self) -> TYPE_RESPONSE:
        aws_account_id = self._get_param("AwsAccountId")
        namespace = self._get_param("Namespace")
        principal_id = self._get_param("PrincipalId")
        self.quicksight_backend.delete_user_by_principal_id(
            aws_account_id, namespace, principal_id
        )
        return 200, {"status": 200}, json.dumps({"RequestId": "request_id", "Status": 200})

    def list_users(self) -> str:
        max_results = self._get_int_param("max-results")
        next_token = self._get_param("next-token")
        aws_account_id = self._get_param("AwsAccountId")
        namespace = self._get_param("Namespace")
        users, next_token = self.quicksight_backend.list_users(
            aws_account_id, namespace, max_results=max_results, next_token=next_token
        )
        return json.dumps(
            {"NextToken": next_token, "UserList": [u.to_json() for u in users]}
        )

    def list_user_groups(self) -> str:
        max_results = self._get_int_param("max-results")
        next_token = self._get_param("next-token")
        aws_account_id = self._get_param("AwsAccountId")
        namespace = self._get_param("Namespace")
        user_name = unquote(self._get_param("UserName"))
        groups, next_token = self.quicksight_backend.list_user_groups(
            aws_account_id,
            namespace,
            user_name,
            max_results=max_results,
            next_token=next_token,
        )
        return json.dumps(
            {"NextToken": next_token, "GroupList": [g.to_json() for g in groups]}
        )

    def update_user_custom_permission(self) -> str:
        aws_account_id = self._get_param("AwsAccountId")
        namespace = self._get_param("Namespace")
        user_name = unquote(self._get_param("UserName"))
        body = json.loads(self.body)
        custom_permissions_name = body.get("CustomPermissionsName", "")
        self.quicksight_backend.update_user_custom_permission(
            aws_account_id, namespace, user_name, custom_permissions_name
        )
        return json.dumps({"RequestId": "request_id", "Status": 200})

    def delete_user_custom_permission(self) -> str:
        aws_account_id = self._get_param("AwsAccountId")
        namespace = self._get_param("Namespace")
        user_name = unquote(self._get_param("UserName"))
        self.quicksight_backend.delete_user_custom_permission(
            aws_account_id, namespace, user_name
        )
        return json.dumps({"RequestId": "request_id", "Status": 200})

    # --- Ingestion ---

    def create_ingestion(self) -> str:
        data_set_id = self._get_param("DataSetId")
        ingestion_id = self._get_param("IngestionId")
        ingestion = self.quicksight_backend.create_ingestion(data_set_id, ingestion_id)
        return json.dumps(ingestion.to_json())

    def cancel_ingestion(self) -> str:
        data_set_id = self._get_param("DataSetId")
        ingestion_id = self._get_param("IngestionId")
        ingestion = self.quicksight_backend.cancel_ingestion(data_set_id, ingestion_id)
        return json.dumps({"Arn": ingestion.arn, "IngestionId": ingestion.ingestion_id, "RequestId": "request_id", "Status": 200})

    def describe_ingestion(self) -> str:
        data_set_id = self._get_param("DataSetId")
        ingestion_id = self._get_param("IngestionId")
        ingestion = self.quicksight_backend.describe_ingestion(data_set_id, ingestion_id)
        return json.dumps({"Ingestion": ingestion.to_json(), "RequestId": "request_id", "Status": 200})

    def list_ingestions(self) -> str:
        data_set_id = self._get_param("DataSetId")
        ingestions = self.quicksight_backend.list_ingestions(data_set_id)
        return json.dumps({"Ingestions": [i.to_json() for i in ingestions], "RequestId": "request_id", "Status": 200})

    # --- Dashboard ---

    def create_dashboard(self) -> str:
        aws_account_id = self._get_param("AwsAccountId")
        dashboard_id = self._get_param("DashboardId")
        dashboard_publish_options = self._get_param("DashboardPublishOptions")
        definition = self._get_param("Definition")
        folder_arns = self._get_param("FolderArns")
        link_entities = self._get_param("LinkEntities")
        link_sharing_configuration = self._get_param("LinkSharingConfiguration")
        name = self._get_param("Name")
        parameters = self._get_param("Parameters")
        permissions = self._get_param("Permissions")
        source_entity = self._get_param("SourceEntity")
        tags = self._get_param("Tags")
        theme_arn = self._get_param("ThemeArn")
        validation_strategy = self._get_param("ValidationStrategy")
        version_description = self._get_param("VersionDescription")

        dashboard = self.quicksight_backend.create_dashboard(
            aws_account_id=aws_account_id,
            dashboard_id=dashboard_id,
            name=name,
            parameters=parameters,
            permissions=permissions,
            source_entity=source_entity,
            tags=tags,
            version_description=version_description,
            dashboard_publish_options=dashboard_publish_options,
            theme_arn=theme_arn,
            definition=definition,
            validation_strategy=validation_strategy,
            folder_arns=folder_arns,
            link_sharing_configuration=link_sharing_configuration,
            link_entities=link_entities,
        )
        return json.dumps(
            {
                "Arn": dashboard.arn,
                "VersionArn": dashboard.version_number,
                "DashboardId": dashboard.dashboard_id,
                "CreationStatus": dashboard.status,
            }
        )

    def describe_dashboard(self) -> str:
        aws_account_id = self._get_param("AwsAccountId")
        dashboard_id = self._get_param("DashboardId")
        version_number = self._get_param("VersionNumber")
        alias_name = self._get_param("AliasName")
        dashboard = self.quicksight_backend.describe_dashboard(
            aws_account_id=aws_account_id,
            dashboard_id=dashboard_id,
            version_number=version_number,
            alias_name=alias_name,
        )
        return json.dumps(
            {"Dashboard": dashboard.to_dict(), "Status": 200, "RequestId": "request_id"}
        )

    def describe_dashboard_definition(self) -> str:
        dashboard_id = self._get_param("DashboardId")
        dashboard = self.quicksight_backend.dashboards.get(dashboard_id)
        if not dashboard:
            from .exceptions import ResourceNotFoundException
            raise ResourceNotFoundException(f"Dashboard {dashboard_id} not found")
        return json.dumps({
            "DashboardId": dashboard.dashboard_id,
            "Name": dashboard.name,
            "Definition": dashboard.definition,
            "Status": 200,
            "RequestId": "request_id",
        })

    def update_dashboard(self) -> str:
        aws_account_id = self._get_param("AwsAccountId")
        dashboard_id = self._get_param("DashboardId")
        body = json.loads(self.body)
        dashboard = self.quicksight_backend.update_dashboard(
            aws_account_id=aws_account_id,
            dashboard_id=dashboard_id,
            name=body.get("Name"),
            source_entity=body.get("SourceEntity"),
            definition=body.get("Definition"),
            parameters=body.get("Parameters"),
            version_description=body.get("VersionDescription"),
            dashboard_publish_options=body.get("DashboardPublishOptions"),
            theme_arn=body.get("ThemeArn"),
            validation_strategy=body.get("ValidationStrategy"),
        )
        return json.dumps({
            "Arn": dashboard.arn,
            "DashboardId": dashboard.dashboard_id,
            "CreationStatus": dashboard.status,
            "Status": 200,
            "VersionArn": dashboard.version_number,
        })

    def delete_dashboard(self) -> str:
        dashboard_id = self._get_param("DashboardId")
        dashboard = self.quicksight_backend.delete_dashboard(dashboard_id)
        return json.dumps({"Arn": dashboard.arn, "DashboardId": dashboard.dashboard_id, "Status": 200, "RequestId": "request_id"})

    def list_dashboards(self) -> str:
        aws_account_id = self._get_param("AwsAccountId")
        next_token = self._get_param("NextToken")
        dashboard_summary_list = self.quicksight_backend.list_dashboards(
            aws_account_id=aws_account_id,
        )
        return json.dumps(
            {
                "DashboardSummaryList": dashboard_summary_list,
                "Next_token": next_token,
                "Status": 200,
            }
        )

    def list_dashboard_versions(self) -> str:
        dashboard_id = self._get_param("DashboardId")
        versions = self.quicksight_backend.list_dashboard_versions(dashboard_id)
        return json.dumps({"DashboardVersionSummaryList": versions, "Status": 200, "RequestId": "request_id"})

    def describe_dashboard_permissions(self) -> str:
        dashboard_id = self._get_param("DashboardId")
        dashboard = self.quicksight_backend.describe_dashboard_permissions(dashboard_id)
        return json.dumps({
            "DashboardArn": dashboard.arn,
            "DashboardId": dashboard.dashboard_id,
            "Permissions": dashboard.permissions,
            "Status": 200,
            "RequestId": "request_id",
        })

    def update_dashboard_permissions(self) -> str:
        dashboard_id = self._get_param("DashboardId")
        body = json.loads(self.body)
        dashboard = self.quicksight_backend.update_dashboard_permissions(
            dashboard_id,
            grant_permissions=body.get("GrantPermissions"),
            revoke_permissions=body.get("RevokePermissions"),
        )
        return json.dumps({
            "DashboardArn": dashboard.arn,
            "DashboardId": dashboard.dashboard_id,
            "Permissions": dashboard.permissions,
            "Status": 200,
            "RequestId": "request_id",
        })

    def update_dashboard_published_version(self) -> str:
        dashboard_id = self._get_param("DashboardId")
        version_number = self._get_param("VersionNumber")
        dashboard = self.quicksight_backend.update_dashboard_published_version(
            dashboard_id, version_number
        )
        return json.dumps({
            "DashboardArn": dashboard.arn,
            "DashboardId": dashboard.dashboard_id,
            "Status": 200,
            "RequestId": "request_id",
        })

    def update_dashboard_links(self) -> str:
        dashboard_id = self._get_param("DashboardId")
        body = json.loads(self.body)
        dashboard = self.quicksight_backend.update_dashboard_links(
            dashboard_id, body.get("LinkEntities", [])
        )
        return json.dumps({
            "DashboardArn": dashboard.arn,
            "Status": 200,
            "RequestId": "request_id",
        })

    def describe_dashboards_qa_configuration(self) -> str:
        return json.dumps({"DashboardsQAConfiguration": {"Status": "ENABLED"}, "Status": 200, "RequestId": "request_id"})

    def update_dashboards_qa_configuration(self) -> str:
        return json.dumps({"Status": 200, "RequestId": "request_id"})

    def start_dashboard_snapshot_job(self) -> str:
        return json.dumps({"Status": 200, "RequestId": "request_id", "Arn": "mock-arn", "SnapshotJobId": "mock-job-id"})

    def describe_dashboard_snapshot_job(self) -> str:
        return json.dumps({"Status": 200, "RequestId": "request_id", "JobStatus": "COMPLETED"})

    def describe_dashboard_snapshot_job_result(self) -> str:
        return json.dumps({"Status": 200, "RequestId": "request_id"})

    def start_dashboard_snapshot_job_schedule(self) -> str:
        return json.dumps({"Status": 200, "RequestId": "request_id"})

    # --- Account Settings ---

    def describe_account_settings(self) -> str:
        aws_account_id = self._get_param("AwsAccountId")
        settings = self.quicksight_backend.describe_account_settings(
            aws_account_id=aws_account_id,
        )
        resp = {
            "AccountName": settings.account_name,
            "Edition": settings.edition,
            "DefaultNamespace": settings.default_namespace,
            "NotificationEmail": settings.notification_email,
            "PublicSharingEnabled": settings.public_sharing_enabled,
            "TerminationProtectionEnabled": settings.termination_protection_enabled,
        }
        return json.dumps({"AccountSettings": resp, "Status": 200})

    def update_account_settings(self) -> str:
        aws_account_id = self._get_param("AwsAccountId")
        default_namespace = self._get_param("DefaultNamespace")
        notification_email = self._get_param("NotificationEmail")
        termination_protection_enabled = self._get_param("TerminationProtectionEnabled")
        self.quicksight_backend.update_account_settings(
            aws_account_id=aws_account_id,
            default_namespace=default_namespace,
            notification_email=notification_email,
            termination_protection_enabled=termination_protection_enabled,
        )
        return json.dumps({"Status": 200})

    def update_public_sharing_settings(self) -> str:
        aws_account_id = self._get_param("AwsAccountId")
        public_sharing_enabled = self._get_param("PublicSharingEnabled")
        self.quicksight_backend.update_public_sharing_settings(
            aws_account_id=aws_account_id,
            public_sharing_enabled=public_sharing_enabled,
        )
        return json.dumps({"Status": 200})

    def describe_account_subscription(self) -> str:
        aws_account_id = self._get_param("AwsAccountId")
        info = self.quicksight_backend.describe_account_subscription(aws_account_id)
        return json.dumps({"AccountInfo": info, "Status": 200, "RequestId": "request_id"})

    def create_account_subscription(self) -> str:
        return json.dumps({
            "SignupResponse": {"accountName": "default", "directoryType": "QUICKSIGHT"},
            "Status": 200,
            "RequestId": "request_id",
        })

    def delete_account_subscription(self) -> str:
        return json.dumps({"Status": 200, "RequestId": "request_id"})

    # --- Account Customization ---

    def create_account_customization(self) -> str:
        body = json.loads(self.body)
        customization = self.quicksight_backend.create_account_customization(
            account_customization=body.get("AccountCustomization", {}),
            namespace=self._get_param("Namespace"),
            tags=body.get("Tags"),
        )
        return json.dumps({
            "AccountCustomization": customization.to_dict(),
            "AwsAccountId": self.quicksight_backend.account_id,
            "Status": 200,
            "RequestId": "request_id",
        })

    def describe_account_customization(self) -> str:
        customization = self.quicksight_backend.describe_account_customization(
            namespace=self._get_param("Namespace"),
        )
        return json.dumps({
            "AccountCustomization": customization.to_dict(),
            "AwsAccountId": self.quicksight_backend.account_id,
            "Status": 200,
            "RequestId": "request_id",
        })

    def update_account_customization(self) -> str:
        body = json.loads(self.body)
        customization = self.quicksight_backend.update_account_customization(
            account_customization=body.get("AccountCustomization", {}),
            namespace=self._get_param("Namespace"),
        )
        return json.dumps({
            "AccountCustomization": customization.to_dict(),
            "AwsAccountId": self.quicksight_backend.account_id,
            "Status": 200,
            "RequestId": "request_id",
        })

    def delete_account_customization(self) -> str:
        self.quicksight_backend.delete_account_customization(
            namespace=self._get_param("Namespace"),
        )
        return json.dumps({"Status": 200, "RequestId": "request_id"})

    # --- DataSource ---

    def create_data_source(self) -> str:
        aws_account_id = self._get_param("AwsAccountId")
        data_source_id = self._get_param("DataSourceId")
        name = self._get_param("Name")
        data_source_type = self._get_param("Type")
        data_source_parameters = self._get_param("DataSourceParameters")
        ssl_properties = self._get_param("SslProperties")
        vpc_connection_properties = self._get_param("VpcConnectionProperties")
        tags = self._get_param("Tags")
        data_source = self.quicksight_backend.create_data_source(
            aws_account_id=aws_account_id,
            data_source_id=data_source_id,
            name=name,
            data_source_type=data_source_type,
            data_source_parameters=data_source_parameters,
            ssl_properties=ssl_properties,
            vpc_connection_properties=vpc_connection_properties,
            tags=tags,
        )
        return json.dumps({
            "Arn": data_source.arn,
            "DataSourceId": data_source.data_source_id,
            "CreationStatus": data_source.status,
            "RequestId": "request_id",
            "Status": 200,
        })

    def delete_data_source(self) -> str:
        aws_account_id = self._get_param("AwsAccountId")
        data_source_id = self._get_param("DataSourceId")
        resp = self.quicksight_backend.delete_data_source(
            aws_account_id=aws_account_id, data_source_id=data_source_id
        )
        return json.dumps({
            "Arn": resp.arn,
            "DataSourceId": resp.data_source_id,
            "RequestId": "request_id",
            "Status": 200,
        })

    def describe_data_source(self) -> str:
        aws_account_id = self._get_param("AwsAccountId")
        data_source_id = self._get_param("DataSourceId")
        data_source = self.quicksight_backend.describe_data_source(
            aws_account_id=aws_account_id, data_source_id=data_source_id
        )
        return json.dumps({
            "DataSource": data_source.to_json(),
            "RequestId": "request_id",
            "Status": 200,
        })

    def list_data_sources(self) -> str:
        aws_account_id = self._get_param("AwsAccountId")
        next_token = self._get_param("NextToken")
        data_sources = self.quicksight_backend.list_data_sources(
            aws_account_id=aws_account_id,
        )
        return json.dumps({
            "DataSources": data_sources,
            "NextToken": next_token,
            "RequestId": "request_id",
            "Status": 200,
        })

    def update_data_source(self) -> str:
        aws_account_id = self._get_param("AwsAccountId")
        data_source_id = self._get_param("DataSourceId")
        name = self._get_param("Name")
        data_source_parameters = self._get_param("DataSourceParameters")
        data_source = self.quicksight_backend.update_data_source(
            aws_account_id=aws_account_id,
            data_source_id=data_source_id,
            name=name,
            data_source_parameters=data_source_parameters,
        )
        return json.dumps({
            "Arn": data_source.arn,
            "DataSourceId": data_source.data_source_id,
            "UpdateStatus": data_source.status,
            "RequestId": "request_id",
            "Status": 200,
        })

    def describe_data_source_permissions(self) -> str:
        aws_account_id = self._get_param("AwsAccountId")
        data_source_id = self._get_param("DataSourceId")
        data_source = self.quicksight_backend.describe_data_source_permissions(
            aws_account_id=aws_account_id, data_source_id=data_source_id
        )
        return json.dumps({
            "DataSourceArn": data_source.arn,
            "DataSourceId": data_source.data_source_id,
            "Permissions": data_source.permissions,
            "Status": 200,
            "RequestId": "request_id",
        })

    def update_data_source_permissions(self) -> str:
        aws_account_id = self._get_param("AwsAccountId")
        data_source_id = self._get_param("DataSourceId")
        body = json.loads(self.body)
        data_source = self.quicksight_backend.update_data_source_permissions(
            aws_account_id=aws_account_id,
            data_source_id=data_source_id,
            grant_permissions=body.get("GrantPermissions"),
            revoke_permissions=body.get("RevokePermissions"),
        )
        return json.dumps({
            "DataSourceArn": data_source.arn,
            "DataSourceId": data_source.data_source_id,
            "Status": 200,
            "RequestId": "request_id",
        })

    # --- Analysis ---

    def create_analysis(self) -> str:
        analysis_id = self._get_param("AnalysisId")
        body = json.loads(self.body)
        analysis = self.quicksight_backend.create_analysis(
            analysis_id=analysis_id,
            name=body.get("Name", ""),
            source_entity=body.get("SourceEntity"),
            definition=body.get("Definition"),
            parameters=body.get("Parameters"),
            permissions=body.get("Permissions"),
            tags=body.get("Tags"),
            theme_arn=body.get("ThemeArn"),
            validation_strategy=body.get("ValidationStrategy"),
            folder_arns=body.get("FolderArns"),
        )
        return json.dumps({
            "Arn": analysis.arn,
            "AnalysisId": analysis.analysis_id,
            "CreationStatus": analysis.status,
            "Status": 200,
            "RequestId": "request_id",
        })

    def describe_analysis(self) -> str:
        analysis_id = self._get_param("AnalysisId")
        analysis = self.quicksight_backend.describe_analysis(analysis_id)
        return json.dumps({
            "Analysis": analysis.to_dict(),
            "Status": 200,
            "RequestId": "request_id",
        })

    def describe_analysis_definition(self) -> str:
        analysis_id = self._get_param("AnalysisId")
        analysis = self.quicksight_backend.describe_analysis_definition(analysis_id)
        return json.dumps({
            "AnalysisId": analysis.analysis_id,
            "Name": analysis.name,
            "Definition": analysis.definition,
            "Status": 200,
            "RequestId": "request_id",
        })

    def describe_analysis_permissions(self) -> str:
        analysis_id = self._get_param("AnalysisId")
        analysis = self.quicksight_backend.describe_analysis_permissions(analysis_id)
        return json.dumps({
            "AnalysisArn": analysis.arn,
            "AnalysisId": analysis.analysis_id,
            "Permissions": analysis.permissions,
            "Status": 200,
            "RequestId": "request_id",
        })

    def update_analysis(self) -> str:
        analysis_id = self._get_param("AnalysisId")
        body = json.loads(self.body)
        analysis = self.quicksight_backend.update_analysis(
            analysis_id=analysis_id,
            name=body.get("Name", ""),
            source_entity=body.get("SourceEntity"),
            definition=body.get("Definition"),
            parameters=body.get("Parameters"),
            theme_arn=body.get("ThemeArn"),
            validation_strategy=body.get("ValidationStrategy"),
        )
        return json.dumps({
            "Arn": analysis.arn,
            "AnalysisId": analysis.analysis_id,
            "UpdateStatus": analysis.status,
            "Status": 200,
            "RequestId": "request_id",
        })

    def update_analysis_permissions(self) -> str:
        analysis_id = self._get_param("AnalysisId")
        body = json.loads(self.body)
        analysis = self.quicksight_backend.update_analysis_permissions(
            analysis_id=analysis_id,
            grant_permissions=body.get("GrantPermissions"),
            revoke_permissions=body.get("RevokePermissions"),
        )
        return json.dumps({
            "AnalysisArn": analysis.arn,
            "AnalysisId": analysis.analysis_id,
            "Permissions": analysis.permissions,
            "Status": 200,
            "RequestId": "request_id",
        })

    def delete_analysis(self) -> str:
        analysis_id = self._get_param("AnalysisId")
        analysis = self.quicksight_backend.delete_analysis(analysis_id)
        return json.dumps({
            "Arn": analysis.arn,
            "AnalysisId": analysis.analysis_id,
            "DeletionTime": str(analysis.last_updated_time),
            "Status": 200,
            "RequestId": "request_id",
        })

    def restore_analysis(self) -> str:
        analysis_id = self._get_param("AnalysisId")
        analysis = self.quicksight_backend.restore_analysis(analysis_id)
        return json.dumps({
            "Arn": analysis.arn,
            "AnalysisId": analysis.analysis_id,
            "Status": 200,
            "RequestId": "request_id",
        })

    def list_analyses(self) -> str:
        analyses = self.quicksight_backend.list_analyses()
        return json.dumps({
            "AnalysisSummaryList": analyses,
            "Status": 200,
            "RequestId": "request_id",
        })

    # --- Template ---

    def create_template(self) -> str:
        template_id = self._get_param("TemplateId")
        body = json.loads(self.body)
        template = self.quicksight_backend.create_template(
            template_id=template_id,
            name=body.get("Name", ""),
            source_entity=body.get("SourceEntity"),
            definition=body.get("Definition"),
            permissions=body.get("Permissions"),
            tags=body.get("Tags"),
            version_description=body.get("VersionDescription"),
            validation_strategy=body.get("ValidationStrategy"),
        )
        return json.dumps({
            "Arn": template.arn,
            "TemplateId": template.template_id,
            "CreationStatus": template.status,
            "VersionArn": template.arn,
            "Status": 200,
            "RequestId": "request_id",
        })

    def describe_template(self) -> str:
        template_id = self._get_param("TemplateId")
        template = self.quicksight_backend.describe_template(template_id)
        return json.dumps({
            "Template": template.to_dict(),
            "Status": 200,
            "RequestId": "request_id",
        })

    def describe_template_definition(self) -> str:
        template_id = self._get_param("TemplateId")
        template = self.quicksight_backend.describe_template_definition(template_id)
        return json.dumps({
            "TemplateId": template.template_id,
            "Name": template.name,
            "Definition": template.definition,
            "Status": 200,
            "RequestId": "request_id",
        })

    def describe_template_permissions(self) -> str:
        template_id = self._get_param("TemplateId")
        template = self.quicksight_backend.describe_template_permissions(template_id)
        return json.dumps({
            "TemplateArn": template.arn,
            "TemplateId": template.template_id,
            "Permissions": template.permissions,
            "Status": 200,
            "RequestId": "request_id",
        })

    def update_template(self) -> str:
        template_id = self._get_param("TemplateId")
        body = json.loads(self.body)
        template = self.quicksight_backend.update_template(
            template_id=template_id,
            name=body.get("Name"),
            source_entity=body.get("SourceEntity"),
            definition=body.get("Definition"),
            version_description=body.get("VersionDescription"),
            validation_strategy=body.get("ValidationStrategy"),
        )
        return json.dumps({
            "Arn": template.arn,
            "TemplateId": template.template_id,
            "CreationStatus": template.status,
            "VersionArn": template.arn,
            "Status": 200,
            "RequestId": "request_id",
        })

    def update_template_permissions(self) -> str:
        template_id = self._get_param("TemplateId")
        body = json.loads(self.body)
        template = self.quicksight_backend.update_template_permissions(
            template_id=template_id,
            grant_permissions=body.get("GrantPermissions"),
            revoke_permissions=body.get("RevokePermissions"),
        )
        return json.dumps({
            "TemplateArn": template.arn,
            "TemplateId": template.template_id,
            "Permissions": template.permissions,
            "Status": 200,
            "RequestId": "request_id",
        })

    def delete_template(self) -> str:
        template_id = self._get_param("TemplateId")
        template = self.quicksight_backend.delete_template(template_id)
        return json.dumps({
            "Arn": template.arn,
            "TemplateId": template.template_id,
            "Status": 200,
            "RequestId": "request_id",
        })

    def list_templates(self) -> str:
        templates = self.quicksight_backend.list_templates()
        return json.dumps({
            "TemplateSummaryList": templates,
            "Status": 200,
            "RequestId": "request_id",
        })

    def list_template_versions(self) -> str:
        template_id = self._get_param("TemplateId")
        versions = self.quicksight_backend.list_template_versions(template_id)
        return json.dumps({
            "TemplateVersionSummaryList": versions,
            "Status": 200,
            "RequestId": "request_id",
        })

    # --- Template Alias ---

    def create_template_alias(self) -> str:
        template_id = self._get_param("TemplateId")
        alias_name = self._get_param("AliasName")
        body = json.loads(self.body)
        template_version_number = body.get("TemplateVersionNumber", 1)
        alias = self.quicksight_backend.create_template_alias(
            template_id, alias_name, template_version_number
        )
        return json.dumps({"TemplateAlias": alias.to_dict(), "Status": 200, "RequestId": "request_id"})

    def describe_template_alias(self) -> str:
        template_id = self._get_param("TemplateId")
        alias_name = self._get_param("AliasName")
        alias = self.quicksight_backend.describe_template_alias(template_id, alias_name)
        return json.dumps({"TemplateAlias": alias.to_dict(), "Status": 200, "RequestId": "request_id"})

    def update_template_alias(self) -> str:
        template_id = self._get_param("TemplateId")
        alias_name = self._get_param("AliasName")
        body = json.loads(self.body)
        template_version_number = body.get("TemplateVersionNumber", 1)
        alias = self.quicksight_backend.update_template_alias(
            template_id, alias_name, template_version_number
        )
        return json.dumps({"TemplateAlias": alias.to_dict(), "Status": 200, "RequestId": "request_id"})

    def delete_template_alias(self) -> str:
        template_id = self._get_param("TemplateId")
        alias_name = self._get_param("AliasName")
        alias = self.quicksight_backend.delete_template_alias(template_id, alias_name)
        return json.dumps({"AliasName": alias.alias_name, "Arn": alias.arn, "TemplateId": template_id, "Status": 200, "RequestId": "request_id"})

    def list_template_aliases(self) -> str:
        template_id = self._get_param("TemplateId")
        aliases = self.quicksight_backend.list_template_aliases(template_id)
        return json.dumps({"TemplateAliasList": aliases, "Status": 200, "RequestId": "request_id"})

    # --- Theme ---

    def create_theme(self) -> str:
        theme_id = self._get_param("ThemeId")
        body = json.loads(self.body)
        theme = self.quicksight_backend.create_theme(
            theme_id=theme_id,
            name=body.get("Name", ""),
            base_theme_id=body.get("BaseThemeId"),
            configuration=body.get("Configuration"),
            permissions=body.get("Permissions"),
            tags=body.get("Tags"),
            version_description=body.get("VersionDescription"),
        )
        return json.dumps({
            "Arn": theme.arn,
            "ThemeId": theme.theme_id,
            "CreationStatus": theme.status,
            "VersionArn": theme.arn,
            "Status": 200,
            "RequestId": "request_id",
        })

    def describe_theme(self) -> str:
        theme_id = self._get_param("ThemeId")
        theme = self.quicksight_backend.describe_theme(theme_id)
        return json.dumps({
            "Theme": theme.to_dict(),
            "Status": 200,
            "RequestId": "request_id",
        })

    def describe_theme_permissions(self) -> str:
        theme_id = self._get_param("ThemeId")
        theme = self.quicksight_backend.describe_theme_permissions(theme_id)
        return json.dumps({
            "ThemeArn": theme.arn,
            "ThemeId": theme.theme_id,
            "Permissions": theme.permissions,
            "Status": 200,
            "RequestId": "request_id",
        })

    def update_theme(self) -> str:
        theme_id = self._get_param("ThemeId")
        body = json.loads(self.body)
        theme = self.quicksight_backend.update_theme(
            theme_id=theme_id,
            name=body.get("Name"),
            base_theme_id=body.get("BaseThemeId"),
            configuration=body.get("Configuration"),
            version_description=body.get("VersionDescription"),
        )
        return json.dumps({
            "Arn": theme.arn,
            "ThemeId": theme.theme_id,
            "CreationStatus": theme.status,
            "VersionArn": theme.arn,
            "Status": 200,
            "RequestId": "request_id",
        })

    def update_theme_permissions(self) -> str:
        theme_id = self._get_param("ThemeId")
        body = json.loads(self.body)
        theme = self.quicksight_backend.update_theme_permissions(
            theme_id=theme_id,
            grant_permissions=body.get("GrantPermissions"),
            revoke_permissions=body.get("RevokePermissions"),
        )
        return json.dumps({
            "ThemeArn": theme.arn,
            "ThemeId": theme.theme_id,
            "Permissions": theme.permissions,
            "Status": 200,
            "RequestId": "request_id",
        })

    def delete_theme(self) -> str:
        theme_id = self._get_param("ThemeId")
        theme = self.quicksight_backend.delete_theme(theme_id)
        return json.dumps({
            "Arn": theme.arn,
            "ThemeId": theme.theme_id,
            "Status": 200,
            "RequestId": "request_id",
        })

    def list_themes(self) -> str:
        themes = self.quicksight_backend.list_themes()
        return json.dumps({
            "ThemeSummaryList": themes,
            "Status": 200,
            "RequestId": "request_id",
        })

    def list_theme_versions(self) -> str:
        theme_id = self._get_param("ThemeId")
        versions = self.quicksight_backend.list_theme_versions(theme_id)
        return json.dumps({
            "ThemeVersionSummaryList": versions,
            "Status": 200,
            "RequestId": "request_id",
        })

    # --- Theme Alias ---

    def create_theme_alias(self) -> str:
        theme_id = self._get_param("ThemeId")
        alias_name = self._get_param("AliasName")
        body = json.loads(self.body)
        theme_version_number = body.get("ThemeVersionNumber", 1)
        alias = self.quicksight_backend.create_theme_alias(
            theme_id, alias_name, theme_version_number
        )
        return json.dumps({"ThemeAlias": alias.to_dict(), "Status": 200, "RequestId": "request_id"})

    def describe_theme_alias(self) -> str:
        theme_id = self._get_param("ThemeId")
        alias_name = self._get_param("AliasName")
        alias = self.quicksight_backend.describe_theme_alias(theme_id, alias_name)
        return json.dumps({"ThemeAlias": alias.to_dict(), "Status": 200, "RequestId": "request_id"})

    def update_theme_alias(self) -> str:
        theme_id = self._get_param("ThemeId")
        alias_name = self._get_param("AliasName")
        body = json.loads(self.body)
        theme_version_number = body.get("ThemeVersionNumber", 1)
        alias = self.quicksight_backend.update_theme_alias(
            theme_id, alias_name, theme_version_number
        )
        return json.dumps({"ThemeAlias": alias.to_dict(), "Status": 200, "RequestId": "request_id"})

    def delete_theme_alias(self) -> str:
        theme_id = self._get_param("ThemeId")
        alias_name = self._get_param("AliasName")
        alias = self.quicksight_backend.delete_theme_alias(theme_id, alias_name)
        return json.dumps({"AliasName": alias.alias_name, "Arn": alias.arn, "ThemeId": theme_id, "Status": 200, "RequestId": "request_id"})

    def list_theme_aliases(self) -> str:
        theme_id = self._get_param("ThemeId")
        aliases = self.quicksight_backend.list_theme_aliases(theme_id)
        return json.dumps({"ThemeAliasList": aliases, "Status": 200, "RequestId": "request_id"})

    # --- Folder ---

    def create_folder(self) -> str:
        folder_id = self._get_param("FolderId")
        body = json.loads(self.body)
        folder = self.quicksight_backend.create_folder(
            folder_id=folder_id,
            name=body.get("Name", ""),
            folder_type=body.get("FolderType"),
            parent_folder_arn=body.get("ParentFolderArn"),
            permissions=body.get("Permissions"),
            tags=body.get("Tags"),
            sharing_model=body.get("SharingModel"),
        )
        return json.dumps({
            "Arn": folder.arn,
            "FolderId": folder.folder_id,
            "Status": 200,
            "RequestId": "request_id",
        })

    def describe_folder(self) -> str:
        folder_id = self._get_param("FolderId")
        folder = self.quicksight_backend.describe_folder(folder_id)
        return json.dumps({
            "Folder": folder.to_dict(),
            "Status": 200,
            "RequestId": "request_id",
        })

    def describe_folder_permissions(self) -> str:
        folder_id = self._get_param("FolderId")
        folder = self.quicksight_backend.describe_folder_permissions(folder_id)
        return json.dumps({
            "FolderArn": folder.arn,
            "FolderId": folder.folder_id,
            "Permissions": folder.permissions,
            "Status": 200,
            "RequestId": "request_id",
        })

    def describe_folder_resolved_permissions(self) -> str:
        folder_id = self._get_param("FolderId")
        folder = self.quicksight_backend.describe_folder_resolved_permissions(folder_id)
        return json.dumps({
            "FolderArn": folder.arn,
            "FolderId": folder.folder_id,
            "Permissions": folder.permissions,
            "Status": 200,
            "RequestId": "request_id",
        })

    def update_folder(self) -> str:
        folder_id = self._get_param("FolderId")
        body = json.loads(self.body)
        folder = self.quicksight_backend.update_folder(
            folder_id=folder_id, name=body.get("Name", "")
        )
        return json.dumps({
            "Arn": folder.arn,
            "FolderId": folder.folder_id,
            "Status": 200,
            "RequestId": "request_id",
        })

    def update_folder_permissions(self) -> str:
        folder_id = self._get_param("FolderId")
        body = json.loads(self.body)
        folder = self.quicksight_backend.update_folder_permissions(
            folder_id=folder_id,
            grant_permissions=body.get("GrantPermissions"),
            revoke_permissions=body.get("RevokePermissions"),
        )
        return json.dumps({
            "FolderArn": folder.arn,
            "FolderId": folder.folder_id,
            "Permissions": folder.permissions,
            "Status": 200,
            "RequestId": "request_id",
        })

    def delete_folder(self) -> str:
        folder_id = self._get_param("FolderId")
        folder = self.quicksight_backend.delete_folder(folder_id)
        return json.dumps({
            "Arn": folder.arn,
            "FolderId": folder.folder_id,
            "Status": 200,
            "RequestId": "request_id",
        })

    def list_folders(self) -> str:
        folders = self.quicksight_backend.list_folders()
        return json.dumps({
            "FolderSummaryList": folders,
            "Status": 200,
            "RequestId": "request_id",
        })

    def create_folder_membership(self) -> str:
        folder_id = self._get_param("FolderId")
        member_type = self._get_param("MemberType")
        member_id = self._get_param("MemberId")
        result = self.quicksight_backend.create_folder_membership(
            folder_id, member_type, member_id
        )
        return json.dumps(result)

    def delete_folder_membership(self) -> str:
        folder_id = self._get_param("FolderId")
        member_type = self._get_param("MemberType")
        member_id = self._get_param("MemberId")
        self.quicksight_backend.delete_folder_membership(
            folder_id, member_type, member_id
        )
        return json.dumps({"Status": 200, "RequestId": "request_id"})

    def list_folder_members(self) -> str:
        folder_id = self._get_param("FolderId")
        members = self.quicksight_backend.list_folder_members(folder_id)
        return json.dumps({
            "FolderMemberList": members,
            "Status": 200,
            "RequestId": "request_id",
        })

    def list_folders_for_resource(self) -> str:
        return json.dumps({"Folders": [], "Status": 200, "RequestId": "request_id"})

    # --- Namespace ---

    def create_namespace(self) -> str:
        body = json.loads(self.body)
        namespace = body.get("Namespace", "")
        identity_store = body.get("IdentityStore")
        tags = body.get("Tags")
        ns = self.quicksight_backend.create_namespace(
            namespace=namespace,
            identity_store=identity_store,
            tags=tags,
        )
        return json.dumps({
            "Arn": ns.arn,
            "Name": ns.namespace,
            "CapacityRegion": ns.capacity_region,
            "CreationStatus": ns.creation_status,
            "IdentityStore": ns.identity_store,
            "Status": 200,
            "RequestId": "request_id",
        })

    def describe_namespace(self) -> str:
        namespace = self._get_param("Namespace")
        ns = self.quicksight_backend.describe_namespace(namespace)
        return json.dumps({
            "Namespace": ns.to_dict(),
            "Status": 200,
            "RequestId": "request_id",
        })

    def delete_namespace(self) -> str:
        namespace = self._get_param("Namespace")
        self.quicksight_backend.delete_namespace(namespace)
        return json.dumps({"Status": 200, "RequestId": "request_id"})

    def list_namespaces(self) -> str:
        namespaces = self.quicksight_backend.list_namespaces()
        return json.dumps({
            "Namespaces": namespaces,
            "Status": 200,
            "RequestId": "request_id",
        })

    # --- Topic ---

    def create_topic(self) -> str:
        body = json.loads(self.body)
        topic_id = body.get("TopicId", "")
        topic = body.get("Topic", {})
        topic_obj = self.quicksight_backend.create_topic(
            topic_id=topic_id,
            name=topic.get("Name", ""),
            description=topic.get("Description"),
            data_sets=topic.get("DataSets"),
            tags=body.get("Tags"),
        )
        return json.dumps({
            "Arn": topic_obj.arn,
            "TopicId": topic_obj.topic_id,
            "Status": 200,
            "RequestId": "request_id",
        })

    def describe_topic(self) -> str:
        topic_id = self._get_param("TopicId")
        topic = self.quicksight_backend.describe_topic(topic_id)
        return json.dumps({
            "Arn": topic.arn,
            "TopicId": topic.topic_id,
            "Topic": topic.to_dict(),
            "Status": 200,
            "RequestId": "request_id",
        })

    def describe_topic_permissions(self) -> str:
        topic_id = self._get_param("TopicId")
        topic = self.quicksight_backend.describe_topic_permissions(topic_id)
        return json.dumps({
            "TopicArn": topic.arn,
            "TopicId": topic.topic_id,
            "Permissions": topic.permissions,
            "Status": 200,
            "RequestId": "request_id",
        })

    def update_topic(self) -> str:
        topic_id = self._get_param("TopicId")
        body = json.loads(self.body)
        topic_def = body.get("Topic", {})
        topic = self.quicksight_backend.update_topic(
            topic_id=topic_id,
            name=topic_def.get("Name"),
            description=topic_def.get("Description"),
            data_sets=topic_def.get("DataSets"),
        )
        return json.dumps({
            "Arn": topic.arn,
            "TopicId": topic.topic_id,
            "Status": 200,
            "RequestId": "request_id",
        })

    def update_topic_permissions(self) -> str:
        topic_id = self._get_param("TopicId")
        body = json.loads(self.body)
        topic = self.quicksight_backend.update_topic_permissions(
            topic_id=topic_id,
            grant_permissions=body.get("GrantPermissions"),
            revoke_permissions=body.get("RevokePermissions"),
        )
        return json.dumps({
            "TopicArn": topic.arn,
            "TopicId": topic.topic_id,
            "Permissions": topic.permissions,
            "Status": 200,
            "RequestId": "request_id",
        })

    def delete_topic(self) -> str:
        topic_id = self._get_param("TopicId")
        self.quicksight_backend.delete_topic(topic_id)
        return json.dumps({"TopicId": topic_id, "Status": 200, "RequestId": "request_id"})

    def list_topics(self) -> str:
        topics = self.quicksight_backend.list_topics()
        return json.dumps({
            "TopicsSummaries": topics,
            "Status": 200,
            "RequestId": "request_id",
        })

    # --- Topic Refresh Schedule ---

    def create_topic_refresh_schedule(self) -> str:
        topic_id = self._get_param("TopicId")
        body = json.loads(self.body)
        result = self.quicksight_backend.create_topic_refresh_schedule(
            topic_id=topic_id,
            dataset_arn=body.get("DatasetArn", ""),
            refresh_schedule=body.get("RefreshSchedule", {}),
        )
        return json.dumps({**result, "Status": 200, "RequestId": "request_id"})

    def describe_topic_refresh_schedule(self) -> str:
        topic_id = self._get_param("TopicId")
        dataset_id = self._get_param("DatasetId")
        result = self.quicksight_backend.describe_topic_refresh_schedule(topic_id, dataset_id)
        return json.dumps({**result, "Status": 200, "RequestId": "request_id"})

    def delete_topic_refresh_schedule(self) -> str:
        topic_id = self._get_param("TopicId")
        dataset_id = self._get_param("DatasetId")
        self.quicksight_backend.delete_topic_refresh_schedule(topic_id, dataset_id)
        return json.dumps({"TopicId": topic_id, "Status": 200, "RequestId": "request_id"})

    def update_topic_refresh_schedule(self) -> str:
        topic_id = self._get_param("TopicId")
        dataset_id = self._get_param("DatasetId")
        body = json.loads(self.body)
        # Use same pattern as create - update the schedule for the dataset
        topic = self.quicksight_backend.describe_topic(topic_id)
        refresh_schedule = body.get("RefreshSchedule", {})
        topic.refresh_schedules[dataset_id] = refresh_schedule
        return json.dumps({"TopicId": topic_id, "TopicArn": topic.arn, "DatasetArn": dataset_id, "Status": 200, "RequestId": "request_id"})

    def list_topic_refresh_schedules(self) -> str:
        topic_id = self._get_param("TopicId")
        result = self.quicksight_backend.list_topic_refresh_schedules(topic_id)
        return json.dumps({**result, "Status": 200, "RequestId": "request_id"})

    # --- Topic Reviewed Answers ---

    def batch_create_topic_reviewed_answer(self) -> str:
        topic_id = self._get_param("TopicId")
        body = json.loads(self.body)
        result = self.quicksight_backend.batch_create_topic_reviewed_answer(
            topic_id=topic_id, answers=body.get("Answers", [])
        )
        return json.dumps({**result, "Status": 200, "RequestId": "request_id"})

    def batch_delete_topic_reviewed_answer(self) -> str:
        topic_id = self._get_param("TopicId")
        body = json.loads(self.body)
        result = self.quicksight_backend.batch_delete_topic_reviewed_answer(
            topic_id=topic_id, answer_ids=body.get("AnswerIds", [])
        )
        return json.dumps({**result, "Status": 200, "RequestId": "request_id"})

    def list_topic_reviewed_answers(self) -> str:
        topic_id = self._get_param("TopicId")
        result = self.quicksight_backend.list_topic_reviewed_answers(topic_id)
        return json.dumps({**result, "Status": 200, "RequestId": "request_id"})

    def describe_topic_refresh(self) -> str:
        return json.dumps({"Status": 200, "RequestId": "request_id"})

    # --- VPCConnection ---

    def create_vpc_connection(self) -> str:
        body = json.loads(self.body)
        vpc = self.quicksight_backend.create_vpc_connection(
            vpc_connection_id=body.get("VPCConnectionId", ""),
            name=body.get("Name", ""),
            subnet_ids=body.get("SubnetIds"),
            security_group_ids=body.get("SecurityGroupIds"),
            dns_resolvers=body.get("DnsResolvers"),
            role_arn=body.get("RoleArn"),
            tags=body.get("Tags"),
        )
        return json.dumps({
            "Arn": vpc.arn,
            "VPCConnectionId": vpc.vpc_connection_id,
            "CreationStatus": vpc.status,
            "AvailabilityStatus": vpc.availability_status,
            "Status": 200,
            "RequestId": "request_id",
        })

    def describe_vpc_connection(self) -> str:
        vpc_connection_id = self._get_param("VPCConnectionId")
        vpc = self.quicksight_backend.describe_vpc_connection(vpc_connection_id)
        return json.dumps({
            "VPCConnection": vpc.to_dict(),
            "Status": 200,
            "RequestId": "request_id",
        })

    def update_vpc_connection(self) -> str:
        vpc_connection_id = self._get_param("VPCConnectionId")
        body = json.loads(self.body)
        vpc = self.quicksight_backend.update_vpc_connection(
            vpc_connection_id=vpc_connection_id,
            name=body.get("Name"),
            subnet_ids=body.get("SubnetIds"),
            security_group_ids=body.get("SecurityGroupIds"),
            dns_resolvers=body.get("DnsResolvers"),
            role_arn=body.get("RoleArn"),
        )
        return json.dumps({
            "Arn": vpc.arn,
            "VPCConnectionId": vpc.vpc_connection_id,
            "UpdateStatus": vpc.status,
            "AvailabilityStatus": vpc.availability_status,
            "Status": 200,
            "RequestId": "request_id",
        })

    def delete_vpc_connection(self) -> str:
        vpc_connection_id = self._get_param("VPCConnectionId")
        vpc = self.quicksight_backend.delete_vpc_connection(vpc_connection_id)
        return json.dumps({
            "Arn": vpc.arn,
            "VPCConnectionId": vpc.vpc_connection_id,
            "DeletionStatus": vpc.status,
            "AvailabilityStatus": vpc.availability_status,
            "Status": 200,
            "RequestId": "request_id",
        })

    def list_vpc_connections(self) -> str:
        vpcs = self.quicksight_backend.list_vpc_connections()
        return json.dumps({
            "VPCConnectionSummaries": vpcs,
            "Status": 200,
            "RequestId": "request_id",
        })

    # --- Refresh Schedule ---

    def create_refresh_schedule(self) -> str:
        data_set_id = self._get_param("DataSetId")
        body = json.loads(self.body)
        schedule = body.get("Schedule", {})
        rs = self.quicksight_backend.create_refresh_schedule(data_set_id, schedule)
        return json.dumps({
            "Arn": rs.arn,
            "ScheduleId": rs.schedule_id,
            "Status": 200,
            "RequestId": "request_id",
        })

    def describe_refresh_schedule(self) -> str:
        data_set_id = self._get_param("DataSetId")
        schedule_id = self._get_param("ScheduleId")
        rs = self.quicksight_backend.describe_refresh_schedule(data_set_id, schedule_id)
        return json.dumps({
            "RefreshSchedule": rs.to_dict(),
            "Arn": rs.arn,
            "Status": 200,
            "RequestId": "request_id",
        })

    def update_refresh_schedule(self) -> str:
        data_set_id = self._get_param("DataSetId")
        body = json.loads(self.body)
        schedule = body.get("Schedule", {})
        rs = self.quicksight_backend.update_refresh_schedule(data_set_id, schedule)
        return json.dumps({
            "Arn": rs.arn,
            "ScheduleId": rs.schedule_id,
            "Status": 200,
            "RequestId": "request_id",
        })

    def delete_refresh_schedule(self) -> str:
        data_set_id = self._get_param("DataSetId")
        schedule_id = self._get_param("ScheduleId")
        self.quicksight_backend.delete_refresh_schedule(data_set_id, schedule_id)
        return json.dumps({"Status": 200, "RequestId": "request_id"})

    def list_refresh_schedules(self) -> str:
        data_set_id = self._get_param("DataSetId")
        schedules = self.quicksight_backend.list_refresh_schedules(data_set_id)
        return json.dumps({
            "RefreshSchedules": schedules,
            "Status": 200,
            "RequestId": "request_id",
        })

    # --- IAM Policy Assignment ---

    def create_iam_policy_assignment(self) -> str:
        namespace = self._get_param("Namespace")
        body = json.loads(self.body)
        assignment = self.quicksight_backend.create_iam_policy_assignment(
            namespace=namespace,
            assignment_name=body.get("AssignmentName", ""),
            assignment_status=body.get("AssignmentStatus"),
            policy_arn=body.get("PolicyArn"),
            identities=body.get("Identities"),
        )
        return json.dumps({
            "AssignmentName": assignment.assignment_name,
            "AssignmentId": assignment.assignment_id,
            "AssignmentStatus": assignment.assignment_status,
            "PolicyArn": assignment.policy_arn,
            "Identities": assignment.identities,
            "Status": 200,
            "RequestId": "request_id",
        })

    def describe_iam_policy_assignment(self) -> str:
        namespace = self._get_param("Namespace")
        assignment_name = self._get_param("AssignmentName")
        assignment = self.quicksight_backend.describe_iam_policy_assignment(
            namespace, assignment_name
        )
        return json.dumps({
            "IAMPolicyAssignment": assignment.to_dict(),
            "Status": 200,
            "RequestId": "request_id",
        })

    def update_iam_policy_assignment(self) -> str:
        namespace = self._get_param("Namespace")
        assignment_name = self._get_param("AssignmentName")
        body = json.loads(self.body)
        assignment = self.quicksight_backend.update_iam_policy_assignment(
            namespace=namespace,
            assignment_name=assignment_name,
            assignment_status=body.get("AssignmentStatus"),
            policy_arn=body.get("PolicyArn"),
            identities=body.get("Identities"),
        )
        return json.dumps({
            "AssignmentName": assignment.assignment_name,
            "AssignmentId": assignment.assignment_id,
            "AssignmentStatus": assignment.assignment_status,
            "PolicyArn": assignment.policy_arn,
            "Identities": assignment.identities,
            "Status": 200,
            "RequestId": "request_id",
        })

    def delete_iam_policy_assignment(self) -> str:
        namespace = self._get_param("Namespace")
        assignment_name = self._get_param("AssignmentName")
        self.quicksight_backend.delete_iam_policy_assignment(namespace, assignment_name)
        return json.dumps({"AssignmentName": assignment_name, "Status": 200, "RequestId": "request_id"})

    def list_iam_policy_assignments(self) -> str:
        namespace = self._get_param("Namespace")
        assignments = self.quicksight_backend.list_iam_policy_assignments(namespace)
        return json.dumps({
            "IAMPolicyAssignments": assignments,
            "Status": 200,
            "RequestId": "request_id",
        })

    def list_iam_policy_assignments_for_user(self) -> str:
        namespace = self._get_param("Namespace")
        user_name = unquote(self._get_param("UserName"))
        assignments = self.quicksight_backend.list_iam_policy_assignments_for_user(
            namespace, user_name
        )
        return json.dumps({
            "ActiveAssignments": assignments,
            "Status": 200,
            "RequestId": "request_id",
        })

    # --- IP Restriction ---

    def describe_ip_restriction(self) -> str:
        result = self.quicksight_backend.describe_ip_restriction()
        return json.dumps({**result, "Status": 200, "RequestId": "request_id"})

    def update_ip_restriction(self) -> str:
        body = json.loads(self.body)
        self.quicksight_backend.update_ip_restriction(
            ip_restriction_rule_map=body.get("IpRestrictionRuleMap"),
            vpc_id_restriction_rule_map=body.get("VpcIdRestrictionRuleMap"),
            vpc_endpoint_id_restriction_rule_map=body.get("VpcEndpointIdRestrictionRuleMap"),
            enabled=body.get("Enabled"),
        )
        return json.dumps({"Status": 200, "RequestId": "request_id"})

    # --- Embed URLs ---

    def generate_embed_url_for_anonymous_user(self) -> str:
        url = self.quicksight_backend.generate_embed_url_for_anonymous_user()
        return json.dumps({"EmbedUrl": url, "Status": 200, "RequestId": "request_id"})

    def generate_embed_url_for_registered_user(self) -> str:
        url = self.quicksight_backend.generate_embed_url_for_registered_user()
        return json.dumps({"EmbedUrl": url, "Status": 200, "RequestId": "request_id"})

    def generate_embed_url_for_registered_user_with_identity(self) -> str:
        url = self.quicksight_backend.generate_embed_url_for_registered_user()
        return json.dumps({"EmbedUrl": url, "Status": 200, "RequestId": "request_id"})

    def get_dashboard_embed_url(self) -> str:
        dashboard_id = self._get_param("DashboardId")
        url = self.quicksight_backend.get_dashboard_embed_url(dashboard_id)
        return json.dumps({"EmbedUrl": url, "Status": 200, "RequestId": "request_id"})

    def get_session_embed_url(self) -> str:
        url = self.quicksight_backend.get_session_embed_url()
        return json.dumps({"EmbedUrl": url, "Status": 200, "RequestId": "request_id"})

    # --- Search operations ---

    def search_analyses(self) -> str:
        body = json.loads(self.body)
        results = self.quicksight_backend.search_analyses(body.get("Filters", []))
        return json.dumps({"AnalysisSummaryList": results, "Status": 200, "RequestId": "request_id"})

    def search_dashboards(self) -> str:
        body = json.loads(self.body)
        results = self.quicksight_backend.search_dashboards(body.get("Filters", []))
        return json.dumps({"DashboardSummaryList": results, "Status": 200, "RequestId": "request_id"})

    def search_data_sets(self) -> str:
        body = json.loads(self.body)
        results = self.quicksight_backend.search_data_sets(body.get("Filters", []))
        return json.dumps({"DataSetSummaries": results, "Status": 200, "RequestId": "request_id"})

    def search_data_sources(self) -> str:
        body = json.loads(self.body)
        results = self.quicksight_backend.search_data_sources(body.get("Filters", []))
        return json.dumps({"DataSourceSummaries": results, "Status": 200, "RequestId": "request_id"})

    def search_folders(self) -> str:
        body = json.loads(self.body)
        results = self.quicksight_backend.search_folders(body.get("Filters", []))
        return json.dumps({"FolderSummaryList": results, "Status": 200, "RequestId": "request_id"})

    def search_topics(self) -> str:
        body = json.loads(self.body)
        results = self.quicksight_backend.search_topics(body.get("Filters", []))
        return json.dumps({"TopicSummaries": results, "Status": 200, "RequestId": "request_id"})

    # --- Role operations ---

    def create_role_membership(self) -> str:
        namespace = self._get_param("Namespace")
        role = self._get_param("Role")
        member_name = self._get_param("MemberName")
        self.quicksight_backend.create_role_membership(namespace, role, member_name)
        return json.dumps({"Status": 200, "RequestId": "request_id"})

    def delete_role_membership(self) -> str:
        namespace = self._get_param("Namespace")
        role = self._get_param("Role")
        member_name = self._get_param("MemberName")
        self.quicksight_backend.delete_role_membership(namespace, role, member_name)
        return json.dumps({"Status": 200, "RequestId": "request_id"})

    def list_role_memberships(self) -> str:
        namespace = self._get_param("Namespace")
        role = self._get_param("Role")
        members = self.quicksight_backend.list_role_memberships(namespace, role)
        return json.dumps({"MembersList": members, "Status": 200, "RequestId": "request_id"})

    def describe_role_custom_permission(self) -> str:
        namespace = self._get_param("Namespace")
        role = self._get_param("Role")
        result = self.quicksight_backend.describe_role_custom_permission(namespace, role)
        return json.dumps({"CustomPermissionsName": result, "Status": 200, "RequestId": "request_id"})

    def update_role_custom_permission(self) -> str:
        namespace = self._get_param("Namespace")
        role = self._get_param("Role")
        body = json.loads(self.body)
        self.quicksight_backend.update_role_custom_permission(
            namespace, role, body.get("CustomPermissionsName", "")
        )
        return json.dumps({"Status": 200, "RequestId": "request_id"})

    def delete_role_custom_permission(self) -> str:
        namespace = self._get_param("Namespace")
        role = self._get_param("Role")
        self.quicksight_backend.delete_role_custom_permission(namespace, role)
        return json.dumps({"Status": 200, "RequestId": "request_id"})

    # --- Tagging ---

    def tag_resource(self) -> str:
        resource_arn = unquote(self._get_param("ResourceArn"))
        tags = self._get_param("Tags")
        self.quicksight_backend.tag_resource(resource_arn, tags)
        return json.dumps({"RequestId": "request_id", "Status": 200})

    def untag_resource(self) -> str:
        resource_arn = unquote(self._get_param("ResourceArn"))
        tag_keys = self.__dict__["data"]["keys"]
        self.quicksight_backend.untag_resource(resource_arn, tag_keys)
        return json.dumps({"RequestId": "request_id", "Status": 200})

    def list_tags_for_resource(self) -> str:
        resource_arn = unquote(self._get_param("ResourceArn"))
        tags = self.quicksight_backend.list_tags_for_resource(arn=resource_arn)
        return json.dumps({"Tags": tags, "RequestId": "request_id", "Status": 200})

    # --- Stub operations (return mock responses) ---

    def describe_account_custom_permission(self) -> str:
        return json.dumps({"Status": 200, "RequestId": "request_id"})

    def delete_account_custom_permission(self) -> str:
        return json.dumps({"Status": 200, "RequestId": "request_id"})

    def update_account_custom_permission(self) -> str:
        return json.dumps({"Status": 200, "RequestId": "request_id"})

    def create_custom_permissions(self) -> str:
        return json.dumps({"Status": 200, "RequestId": "request_id"})

    def describe_custom_permissions(self) -> str:
        return json.dumps({"Status": 200, "RequestId": "request_id"})

    def update_custom_permissions(self) -> str:
        return json.dumps({"Status": 200, "RequestId": "request_id"})

    def delete_custom_permissions(self) -> str:
        return json.dumps({"Status": 200, "RequestId": "request_id"})

    def list_custom_permissions(self) -> str:
        return json.dumps({"CustomPermissionsList": [], "Status": 200, "RequestId": "request_id"})

    def describe_key_registration(self) -> str:
        return json.dumps({"KeyRegistration": [], "Status": 200, "RequestId": "request_id"})

    def update_key_registration(self) -> str:
        return json.dumps({"Status": 200, "RequestId": "request_id"})

    def update_spice_capacity_configuration(self) -> str:
        return json.dumps({"Status": 200, "RequestId": "request_id"})

    def describe_q_personalization_configuration(self) -> str:
        return json.dumps({"PersonalizationMode": "ENABLED", "Status": 200, "RequestId": "request_id"})

    def update_q_personalization_configuration(self) -> str:
        return json.dumps({"Status": 200, "RequestId": "request_id"})

    def describe_quick_sight_q_search_configuration(self) -> str:
        return json.dumps({"QSearchStatus": "ENABLED", "Status": 200, "RequestId": "request_id"})

    def update_quick_sight_q_search_configuration(self) -> str:
        return json.dumps({"Status": 200, "RequestId": "request_id"})

    def update_application_with_token_exchange_grant(self) -> str:
        return json.dumps({"Status": 200, "RequestId": "request_id"})

    def delete_identity_propagation_config(self) -> str:
        return json.dumps({"Status": 200, "RequestId": "request_id"})

    def update_identity_propagation_config(self) -> str:
        return json.dumps({"Status": 200, "RequestId": "request_id"})

    def list_identity_propagation_configs(self) -> str:
        return json.dumps({"Services": [], "Status": 200, "RequestId": "request_id"})

    def start_asset_bundle_export_job(self) -> str:
        return json.dumps({"Arn": "mock-arn", "AssetBundleExportJobId": "mock-job", "Status": 200, "RequestId": "request_id"})

    def start_asset_bundle_import_job(self) -> str:
        return json.dumps({"Arn": "mock-arn", "AssetBundleImportJobId": "mock-job", "Status": 200, "RequestId": "request_id"})

    def describe_asset_bundle_export_job(self) -> str:
        return json.dumps({"JobStatus": "SUCCESSFUL", "Status": 200, "RequestId": "request_id"})

    def describe_asset_bundle_import_job(self) -> str:
        return json.dumps({"JobStatus": "SUCCESSFUL", "Status": 200, "RequestId": "request_id"})

    def list_asset_bundle_export_jobs(self) -> str:
        return json.dumps({"AssetBundleExportJobSummaryList": [], "Status": 200, "RequestId": "request_id"})

    def list_asset_bundle_import_jobs(self) -> str:
        return json.dumps({"AssetBundleImportJobSummaryList": [], "Status": 200, "RequestId": "request_id"})

    def predict_qa_results(self) -> str:
        return json.dumps({"Status": 200, "RequestId": "request_id"})

    def get_identity_context(self) -> str:
        return json.dumps({"Status": 200, "RequestId": "request_id"})

    def describe_default_q_business_application(self) -> str:
        return json.dumps({"Status": 200, "RequestId": "request_id"})

    def update_default_q_business_application(self) -> str:
        return json.dumps({"Status": 200, "RequestId": "request_id"})

    def delete_default_q_business_application(self) -> str:
        return json.dumps({"Status": 200, "RequestId": "request_id"})

    def describe_self_upgrade_configuration(self) -> str:
        return json.dumps({"Status": 200, "RequestId": "request_id"})

    def update_self_upgrade_configuration(self) -> str:
        return json.dumps({"Status": 200, "RequestId": "request_id"})

    def update_self_upgrade(self) -> str:
        return json.dumps({"Status": 200, "RequestId": "request_id"})

    def list_self_upgrades(self) -> str:
        return json.dumps({"SelfUpgradesList": [], "Status": 200, "RequestId": "request_id"})

    # --- Brand operations (stubs) ---

    def create_brand(self) -> str:
        return json.dumps({"Status": 200, "RequestId": "request_id"})

    def describe_brand(self) -> str:
        return json.dumps({"Status": 200, "RequestId": "request_id"})

    def update_brand(self) -> str:
        return json.dumps({"Status": 200, "RequestId": "request_id"})

    def delete_brand(self) -> str:
        return json.dumps({"Status": 200, "RequestId": "request_id"})

    def list_brands(self) -> str:
        return json.dumps({"Brands": [], "Status": 200, "RequestId": "request_id"})

    def describe_brand_assignment(self) -> str:
        return json.dumps({"Status": 200, "RequestId": "request_id"})

    def update_brand_assignment(self) -> str:
        return json.dumps({"Status": 200, "RequestId": "request_id"})

    def delete_brand_assignment(self) -> str:
        return json.dumps({"Status": 200, "RequestId": "request_id"})

    def describe_brand_published_version(self) -> str:
        return json.dumps({"Status": 200, "RequestId": "request_id"})

    def update_brand_published_version(self) -> str:
        return json.dumps({"Status": 200, "RequestId": "request_id"})

    # --- ActionConnector operations (stubs) ---

    def create_action_connector(self) -> str:
        return json.dumps({"Status": 200, "RequestId": "request_id"})

    def describe_action_connector(self) -> str:
        return json.dumps({"Status": 200, "RequestId": "request_id"})

    def describe_action_connector_permissions(self) -> str:
        return json.dumps({"Status": 200, "RequestId": "request_id"})

    def update_action_connector(self) -> str:
        return json.dumps({"Status": 200, "RequestId": "request_id"})

    def update_action_connector_permissions(self) -> str:
        return json.dumps({"Status": 200, "RequestId": "request_id"})

    def delete_action_connector(self) -> str:
        return json.dumps({"Status": 200, "RequestId": "request_id"})

    def list_action_connectors(self) -> str:
        return json.dumps({"ActionConnectors": [], "Status": 200, "RequestId": "request_id"})

    def search_action_connectors(self) -> str:
        return json.dumps({"ActionConnectors": [], "Status": 200, "RequestId": "request_id"})

    # --- Flow operations (stubs) ---

    def list_flows(self) -> str:
        return json.dumps({"Flows": [], "Status": 200, "RequestId": "request_id"})

    def get_flow_metadata(self) -> str:
        return json.dumps({"Status": 200, "RequestId": "request_id"})

    def get_flow_permissions(self) -> str:
        return json.dumps({"Permissions": [], "Status": 200, "RequestId": "request_id"})

    def update_flow_permissions(self) -> str:
        return json.dumps({"Status": 200, "RequestId": "request_id"})

    def search_flows(self) -> str:
        return json.dumps({"Flows": [], "Status": 200, "RequestId": "request_id"})
