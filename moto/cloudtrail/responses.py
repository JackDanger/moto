"""Handles incoming cloudtrail requests, invokes methods, returns responses."""

import json
from typing import Any

from moto.core.responses import BaseResponse

from .exceptions import InvalidParameterCombinationException
from .models import CloudTrailBackend, cloudtrail_backends


class CloudTrailResponse(BaseResponse):
    """Handler for CloudTrail requests and responses."""

    def __init__(self) -> None:
        super().__init__(service_name="cloudtrail")

    @property
    def cloudtrail_backend(self) -> CloudTrailBackend:
        """Return backend instance specific for this region."""
        return cloudtrail_backends[self.current_account][self.region]

    def create_trail(self) -> str:
        name = self._get_param("Name")
        bucket_name = self._get_param("S3BucketName")
        is_global = self._get_bool_param("IncludeGlobalServiceEvents", True)
        is_multi_region = self._get_bool_param("IsMultiRegionTrail", False)
        if not is_global and is_multi_region:
            raise InvalidParameterCombinationException(
                "Multi-Region trail must include global service events."
            )
        s3_key_prefix = self._get_param("S3KeyPrefix")
        sns_topic_name = self._get_param("SnsTopicName")
        log_validation = self._get_bool_param("EnableLogFileValidation", False)
        is_org_trail = self._get_bool_param("IsOrganizationTrail", False)
        cw_log_group_arn = self._get_param("CloudWatchLogsLogGroupArn")
        cw_role_arn = self._get_param("CloudWatchLogsRoleArn")
        kms_key_id = self._get_param("KmsKeyId")
        tags_list = self._get_param("TagsList", [])
        trail = self.cloudtrail_backend.create_trail(
            name,
            bucket_name,
            s3_key_prefix,
            sns_topic_name,
            is_global,
            is_multi_region,
            log_validation,
            is_org_trail,
            cw_log_group_arn,
            cw_role_arn,
            kms_key_id,
            tags_list,
        )
        return json.dumps(trail.description())

    def get_trail(self) -> str:
        name = self._get_param("Name")
        trail = self.cloudtrail_backend.get_trail(name)
        return json.dumps({"Trail": trail.description()})

    def get_trail_status(self) -> str:
        name = self._get_param("Name")
        status = self.cloudtrail_backend.get_trail_status(name)
        return json.dumps(status.description())

    def describe_trails(self) -> str:
        include_shadow_trails = self._get_bool_param("includeShadowTrails", True)
        trails = self.cloudtrail_backend.describe_trails(include_shadow_trails)
        return json.dumps(
            {"trailList": [t.description(include_region=True) for t in trails]}
        )

    def list_trails(self) -> str:
        all_trails = self.cloudtrail_backend.list_trails()
        return json.dumps({"Trails": [t.short() for t in all_trails]})

    def start_logging(self) -> str:
        name = self._get_param("Name")
        self.cloudtrail_backend.start_logging(name)
        return json.dumps({})

    def stop_logging(self) -> str:
        name = self._get_param("Name")
        self.cloudtrail_backend.stop_logging(name)
        return json.dumps({})

    def delete_trail(self) -> str:
        name = self._get_param("Name")
        self.cloudtrail_backend.delete_trail(name)
        return json.dumps({})

    def update_trail(self) -> str:
        name = self._get_param("Name")
        s3_bucket_name = self._get_param("S3BucketName")
        s3_key_prefix = self._get_param("S3KeyPrefix")
        sns_topic_name = self._get_param("SnsTopicName")
        include_global_service_events = self._get_param("IncludeGlobalServiceEvents")
        is_multi_region_trail = self._get_param("IsMultiRegionTrail")
        enable_log_file_validation = self._get_param("EnableLogFileValidation")
        is_organization_trail = self._get_param("IsOrganizationTrail")
        cw_log_group_arn = self._get_param("CloudWatchLogsLogGroupArn")
        cw_role_arn = self._get_param("CloudWatchLogsRoleArn")
        kms_key_id = self._get_param("KmsKeyId")
        trail = self.cloudtrail_backend.update_trail(
            name=name,
            s3_bucket_name=s3_bucket_name,
            s3_key_prefix=s3_key_prefix,
            sns_topic_name=sns_topic_name,
            include_global_service_events=include_global_service_events,
            is_multi_region_trail=is_multi_region_trail,
            enable_log_file_validation=enable_log_file_validation,
            is_organization_trail=is_organization_trail,
            cw_log_group_arn=cw_log_group_arn,
            cw_role_arn=cw_role_arn,
            kms_key_id=kms_key_id,
        )
        return json.dumps(trail.description())

    def put_event_selectors(self) -> str:
        params = json.loads(self.body)
        trail_name = params.get("TrailName")
        event_selectors = params.get("EventSelectors")
        advanced_event_selectors = params.get("AdvancedEventSelectors")
        (
            trail_arn,
            event_selectors,
            advanced_event_selectors,
        ) = self.cloudtrail_backend.put_event_selectors(
            trail_name=trail_name,
            event_selectors=event_selectors,
            advanced_event_selectors=advanced_event_selectors,
        )
        return json.dumps(
            {
                "TrailARN": trail_arn,
                "EventSelectors": event_selectors,
                "AdvancedEventSelectors": advanced_event_selectors,
            }
        )

    def get_event_selectors(self) -> str:
        params = json.loads(self.body)
        trail_name = params.get("TrailName")
        (
            trail_arn,
            event_selectors,
            advanced_event_selectors,
        ) = self.cloudtrail_backend.get_event_selectors(trail_name=trail_name)
        return json.dumps(
            {
                "TrailARN": trail_arn,
                "EventSelectors": event_selectors,
                "AdvancedEventSelectors": advanced_event_selectors,
            }
        )

    def add_tags(self) -> str:
        params = json.loads(self.body)
        resource_id = params.get("ResourceId")
        tags_list = params.get("TagsList")
        self.cloudtrail_backend.add_tags(resource_id=resource_id, tags_list=tags_list)
        return json.dumps({})

    def remove_tags(self) -> str:
        resource_id = self._get_param("ResourceId")
        tags_list = self._get_param("TagsList")
        self.cloudtrail_backend.remove_tags(
            resource_id=resource_id, tags_list=tags_list
        )
        return json.dumps({})

    def list_tags(self) -> str:
        params = json.loads(self.body)
        resource_id_list = params.get("ResourceIdList")
        resource_tag_list = self.cloudtrail_backend.list_tags(
            resource_id_list=resource_id_list
        )
        return json.dumps({"ResourceTagList": resource_tag_list})

    def put_insight_selectors(self) -> str:
        trail_name = self._get_param("TrailName")
        insight_selectors = self._get_param("InsightSelectors")
        event_data_store = self._get_param("EventDataStore")
        if event_data_store:
            eds_arn, selectors = (
                self.cloudtrail_backend.put_insight_selectors_for_event_data_store(
                    event_data_store=event_data_store,
                    insight_selectors=insight_selectors,
                )
            )
            return json.dumps(
                {"EventDataStoreArn": eds_arn, "InsightSelectors": selectors}
            )
        trail_arn, insight_selectors = self.cloudtrail_backend.put_insight_selectors(
            trail_name=trail_name, insight_selectors=insight_selectors
        )
        return json.dumps(
            {"TrailARN": trail_arn, "InsightSelectors": insight_selectors}
        )

    def get_insight_selectors(self) -> str:
        trail_name = self._get_param("TrailName")
        # Support both trail-based and event-data-store-based insight selectors
        event_data_store = self._get_param("EventDataStore")
        if event_data_store:
            eds_arn, insight_selectors = (
                self.cloudtrail_backend.get_insight_selectors_for_event_data_store(
                    event_data_store=event_data_store
                )
            )
            resp: dict[str, Any] = {"EventDataStoreArn": eds_arn}
            if insight_selectors:
                resp["InsightSelectors"] = insight_selectors
            return json.dumps(resp)

        trail_arn, insight_selectors = self.cloudtrail_backend.get_insight_selectors(
            trail_name=trail_name
        )
        resp = {"TrailARN": trail_arn}
        if insight_selectors:
            resp["InsightSelectors"] = insight_selectors
        return json.dumps(resp)

    # Event Data Store operations

    def create_event_data_store(self) -> str:
        name = self._get_param("Name")
        advanced_event_selectors = self._get_param("AdvancedEventSelectors")
        multi_region_enabled = self._get_bool_param("MultiRegionEnabled", True)
        organization_enabled = self._get_bool_param("OrganizationEnabled", False)
        retention_period = self._get_int_param("RetentionPeriod", 2557)
        termination_protection_enabled = self._get_bool_param(
            "TerminationProtectionEnabled", True
        )
        kms_key_id = self._get_param("KmsKeyId")
        billing_mode = self._get_param("BillingMode") or "EXTENDABLE_RETENTION_PRICING"
        tags_list = self._get_param("TagsList", [])
        eds = self.cloudtrail_backend.create_event_data_store(
            name=name,
            advanced_event_selectors=advanced_event_selectors,
            multi_region_enabled=multi_region_enabled,
            organization_enabled=organization_enabled,
            retention_period=retention_period,
            termination_protection_enabled=termination_protection_enabled,
            kms_key_id=kms_key_id,
            billing_mode=billing_mode,
            tags_list=tags_list,
        )
        return json.dumps(eds.description())

    def get_event_data_store(self) -> str:
        event_data_store = self._get_param("EventDataStore")
        eds = self.cloudtrail_backend.get_event_data_store(event_data_store)
        return json.dumps(eds.description())

    def list_event_data_stores(self) -> str:
        stores = self.cloudtrail_backend.list_event_data_stores()
        return json.dumps({"EventDataStores": [eds.description() for eds in stores]})

    # Channel operations

    def create_channel(self) -> str:
        name = self._get_param("Name")
        source = self._get_param("Source")
        destinations = self._get_param("Destinations")
        tags_list = self._get_param("Tags", [])
        channel = self.cloudtrail_backend.create_channel(
            name=name,
            source=source,
            destinations=destinations,
            tags_list=tags_list,
        )
        return json.dumps(channel.description())

    def get_channel(self) -> str:
        channel_arn = self._get_param("Channel")
        channel = self.cloudtrail_backend.get_channel(channel_arn)
        return json.dumps(channel.description())

    def list_channels(self) -> str:
        channels = self.cloudtrail_backend.list_channels()
        return json.dumps(
            {"Channels": [{"ChannelArn": ch.arn, "Name": ch.name} for ch in channels]}
        )

    # Query operations

    def start_query(self) -> str:
        query_statement = self._get_param("QueryStatement")
        event_data_store_arn = self._get_param("EventDataStoreArn")
        query = self.cloudtrail_backend.start_query(
            query_statement=query_statement,
            event_data_store_arn=event_data_store_arn,
        )
        return json.dumps({"QueryId": query.query_id})

    def describe_query(self) -> str:
        query_id = self._get_param("QueryId")
        query = self.cloudtrail_backend.describe_query(query_id)
        return json.dumps(query.description())

    def get_query_results(self) -> str:
        query_id = self._get_param("QueryId")
        query_status, query_results, query_statistics = (
            self.cloudtrail_backend.get_query_results(query_id)
        )
        resp: dict[str, Any] = {
            "QueryStatus": query_status,
            "QueryStatistics": {
                "ResultsCount": len(query_results),
                "TotalResultsCount": len(query_results),
                "BytesScanned": query_statistics.get("BytesScanned", 0),
            },
            "QueryResultRows": query_results,
        }
        return json.dumps(resp)

    def delete_event_data_store(self) -> str:
        event_data_store = self._get_param("EventDataStore")
        self.cloudtrail_backend.delete_event_data_store(event_data_store)
        return json.dumps({})

    def update_event_data_store(self) -> str:
        event_data_store = self._get_param("EventDataStore")
        name = self._get_param("Name")
        advanced_event_selectors = self._get_param("AdvancedEventSelectors")
        multi_region_enabled = self._get_param("MultiRegionEnabled")
        organization_enabled = self._get_param("OrganizationEnabled")
        retention_period = self._get_param("RetentionPeriod")
        termination_protection_enabled = self._get_param("TerminationProtectionEnabled")
        kms_key_id = self._get_param("KmsKeyId")
        billing_mode = self._get_param("BillingMode")
        eds = self.cloudtrail_backend.update_event_data_store(
            event_data_store=event_data_store,
            name=name,
            advanced_event_selectors=advanced_event_selectors,
            multi_region_enabled=multi_region_enabled,
            organization_enabled=organization_enabled,
            retention_period=retention_period,
            termination_protection_enabled=termination_protection_enabled,
            kms_key_id=kms_key_id,
            billing_mode=billing_mode,
        )
        return json.dumps(eds.description())

    def restore_event_data_store(self) -> str:
        event_data_store = self._get_param("EventDataStore")
        eds = self.cloudtrail_backend.restore_event_data_store(event_data_store)
        return json.dumps(eds.description())

    def list_queries(self) -> str:
        event_data_store = self._get_param("EventDataStore")
        queries = self.cloudtrail_backend.list_queries(event_data_store)
        return json.dumps(
            {
                "Queries": [
                    {
                        "QueryId": q.query_id,
                        "QueryStatus": q.query_status,
                        "CreationTime": q.query_statistics.get("CreationTime", 0),
                    }
                    for q in queries
                ]
            }
        )

    def cancel_query(self) -> str:
        query_id = self._get_param("QueryId")
        qid, status = self.cloudtrail_backend.cancel_query(query_id)
        return json.dumps({"QueryId": qid, "QueryStatus": status})

    def delete_channel(self) -> str:
        channel_arn = self._get_param("Channel")
        self.cloudtrail_backend.delete_channel(channel_arn)
        return json.dumps({})

    def update_channel(self) -> str:
        channel_arn = self._get_param("Channel")
        name = self._get_param("Name")
        source = self._get_param("Source")
        destinations = self._get_param("Destinations")
        channel = self.cloudtrail_backend.update_channel(
            channel_arn=channel_arn,
            name=name,
            source=source,
            destinations=destinations,
        )
        return json.dumps(channel.description())

    def enable_federation(self) -> str:
        event_data_store = self._get_param("EventDataStore")
        federation_role_arn = self._get_param("FederationRoleArn")
        eds_arn, status, role_arn = self.cloudtrail_backend.enable_federation(
            event_data_store=event_data_store,
            federation_role_arn=federation_role_arn,
        )
        return json.dumps(
            {
                "EventDataStoreArn": eds_arn,
                "FederationStatus": status,
                "FederationRoleArn": role_arn,
            }
        )

    def disable_federation(self) -> str:
        event_data_store = self._get_param("EventDataStore")
        eds_arn, status = self.cloudtrail_backend.disable_federation(
            event_data_store=event_data_store,
        )
        return json.dumps(
            {
                "EventDataStoreArn": eds_arn,
                "FederationStatus": status,
            }
        )

    def start_import(self) -> str:
        params = json.loads(self.body)
        source = None
        import_source = params.get("ImportSource")
        if import_source and "S3" in import_source:
            source = import_source["S3"].get("S3LocationUri")
        destinations = params.get("Destinations")
        import_id = params.get("ImportId")
        imp = self.cloudtrail_backend.start_import(
            source=source,
            destinations=destinations,
            import_id=import_id,
        )
        return json.dumps(imp.description())

    def get_import(self) -> str:
        import_id = self._get_param("ImportId")
        imp = self.cloudtrail_backend.get_import(import_id)
        return json.dumps(imp.description())

    def list_imports(self) -> str:
        destination = self._get_param("Destination")
        imports = self.cloudtrail_backend.list_imports(destination=destination)
        return json.dumps({"Imports": [imp.description() for imp in imports]})

    def stop_import(self) -> str:
        import_id = self._get_param("ImportId")
        imp = self.cloudtrail_backend.stop_import(import_id)
        return json.dumps(imp.description())

    def register_organization_delegated_admin(self) -> str:
        member_account_id = self._get_param("MemberAccountId")
        self.cloudtrail_backend.register_organization_delegated_admin(
            member_account_id=member_account_id,
        )
        return json.dumps({})

    def deregister_organization_delegated_admin(self) -> str:
        delegated_admin_account_id = self._get_param("DelegatedAdminAccountId")
        self.cloudtrail_backend.deregister_organization_delegated_admin(
            delegated_admin_account_id=delegated_admin_account_id,
        )
        return json.dumps({})

    # Resource Policy operations

    def put_resource_policy(self) -> str:
        resource_arn = self._get_param("ResourceArn")
        resource_policy = self._get_param("ResourcePolicy")
        arn, policy = self.cloudtrail_backend.put_resource_policy(
            resource_arn=resource_arn,
            resource_policy=resource_policy,
        )
        return json.dumps({"ResourceArn": arn, "ResourcePolicy": policy})

    def get_resource_policy(self) -> str:
        resource_arn = self._get_param("ResourceArn")
        arn, policy = self.cloudtrail_backend.get_resource_policy(
            resource_arn=resource_arn
        )
        return json.dumps({"ResourceArn": arn, "ResourcePolicy": policy})

    # Dashboard operations

    def create_dashboard(self) -> str:
        name = self._get_param("Name")
        widgets = self._get_param("Widgets", [])
        refresh_schedule = self._get_param("RefreshSchedule")
        termination_protection_enabled = self._get_bool_param(
            "TerminationProtectionEnabled", False
        )
        tags_list = self._get_param("TagsList", [])
        dashboard = self.cloudtrail_backend.create_dashboard(
            name=name,
            widgets=widgets,
            refresh_schedule=refresh_schedule,
            termination_protection_enabled=termination_protection_enabled,
            tags_list=tags_list,
        )
        return json.dumps(dashboard.to_dict())

    def get_dashboard(self) -> str:
        dashboard_id = self._get_param("DashboardId")
        dashboard = self.cloudtrail_backend.get_dashboard(dashboard_id)
        return json.dumps(dashboard.to_dict())

    def list_dashboards(self) -> str:
        dashboards = self.cloudtrail_backend.list_dashboards()
        items = [
            {
                "DashboardArn": d.arn,
                "Type": d.type_,
            }
            for d in dashboards
        ]
        return json.dumps({"Dashboards": items})

    def update_dashboard(self) -> str:
        dashboard_id = self._get_param("DashboardId")
        widgets = self._get_param("Widgets")
        refresh_schedule = self._get_param("RefreshSchedule")
        termination_protection_enabled = self._get_param("TerminationProtectionEnabled")
        dashboard = self.cloudtrail_backend.update_dashboard(
            dashboard_id=dashboard_id,
            widgets=widgets,
            refresh_schedule=refresh_schedule,
            termination_protection_enabled=termination_protection_enabled,
        )
        return json.dumps(dashboard.to_dict())

    def delete_dashboard(self) -> str:
        dashboard_id = self._get_param("DashboardId")
        self.cloudtrail_backend.delete_dashboard(dashboard_id)
        return json.dumps({})

    # Event Configuration operations

    def put_event_configuration(self) -> str:
        event_data_store = self._get_param("EventDataStore")
        trail_name = self._get_param("TrailName")
        aggregation_configurations = self._get_param("AggregationConfigurations")
        context_key_selectors = self._get_param("ContextKeySelectors")
        max_event_size = self._get_param("MaxEventSize")
        config = self.cloudtrail_backend.put_event_configuration(
            event_data_store=event_data_store,
            trail_name=trail_name,
            aggregation_configurations=aggregation_configurations,
            context_key_selectors=context_key_selectors,
            max_event_size=max_event_size,
        )
        return json.dumps(config)

    def get_event_configuration(self) -> str:
        event_data_store = self._get_param("EventDataStore")
        trail_name = self._get_param("TrailName")
        config = self.cloudtrail_backend.get_event_configuration(
            event_data_store=event_data_store,
            trail_name=trail_name,
        )
        return json.dumps(config)

    # Resource Policy delete

    def delete_resource_policy(self) -> str:
        resource_arn = self._get_param("ResourceArn")
        self.cloudtrail_backend.delete_resource_policy(resource_arn=resource_arn)
        return json.dumps({})
