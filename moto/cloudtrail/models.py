import re
import time
from collections.abc import Iterable
from datetime import datetime
from typing import Any, Optional

from moto.core.base_backend import BackendDict, BaseBackend
from moto.core.common_models import BaseModel
from moto.core.utils import iso_8601_datetime_without_milliseconds, utcnow
from moto.utilities.tagging_service import TaggingService
from moto.utilities.utils import get_partition

from .exceptions import (
    ChannelNotFoundException,
    EventDataStoreNotFoundException,
    InsufficientSnsTopicPolicyException,
    QueryIdNotFoundException,
    ResourceNotFoundException,
    S3BucketDoesNotExistException,
    TrailNameInvalidChars,
    TrailNameNotEndingCorrectly,
    TrailNameNotStartingCorrectly,
    TrailNameTooLong,
    TrailNameTooShort,
    TrailNotFoundException,
)


def datetime2int(date: datetime) -> int:
    return int(time.mktime(date.timetuple()))


class TrailStatus:
    def __init__(self) -> None:
        self.is_logging = False
        self.latest_delivery_time: Optional[int] = None
        self.latest_delivery_attempt: Optional[str] = ""
        self.started: Optional[datetime] = None
        self.stopped: Optional[datetime] = None

    def start_logging(self) -> None:
        self.is_logging = True
        self.started = utcnow()
        self.latest_delivery_time = datetime2int(utcnow())
        self.latest_delivery_attempt = iso_8601_datetime_without_milliseconds(utcnow())

    def stop_logging(self) -> None:
        self.is_logging = False
        self.stopped = utcnow()

    def description(self) -> dict[str, Any]:
        if self.is_logging:
            self.latest_delivery_time = datetime2int(utcnow())
            self.latest_delivery_attempt = iso_8601_datetime_without_milliseconds(
                utcnow()
            )
        desc: dict[str, Any] = {
            "IsLogging": self.is_logging,
            "LatestDeliveryAttemptTime": self.latest_delivery_attempt,
            "LatestNotificationAttemptTime": "",
            "LatestNotificationAttemptSucceeded": "",
            "LatestDeliveryAttemptSucceeded": "",
            "TimeLoggingStarted": "",
            "TimeLoggingStopped": "",
        }
        if self.started:
            desc["StartLoggingTime"] = datetime2int(self.started)
            desc["TimeLoggingStarted"] = iso_8601_datetime_without_milliseconds(
                self.started
            )
            desc["LatestDeliveryTime"] = self.latest_delivery_time
        if self.stopped:
            desc["StopLoggingTime"] = datetime2int(self.stopped)
            desc["TimeLoggingStopped"] = iso_8601_datetime_without_milliseconds(
                self.stopped
            )
        return desc


class Trail(BaseModel):
    def __init__(
        self,
        account_id: str,
        region_name: str,
        trail_name: str,
        bucket_name: str,
        s3_key_prefix: str,
        sns_topic_name: str,
        is_global: bool,
        is_multi_region: bool,
        log_validation: bool,
        is_org_trail: bool,
        cw_log_group_arn: str,
        cw_role_arn: str,
        kms_key_id: str,
    ):
        self.account_id = account_id
        self.region_name = region_name
        self.partition = get_partition(region_name)
        self.trail_name = trail_name
        self.bucket_name = bucket_name
        self.s3_key_prefix = s3_key_prefix
        self.sns_topic_name = sns_topic_name
        self.is_multi_region = is_multi_region
        self.log_validation = log_validation
        self.is_org_trail = is_org_trail
        self.include_global_service_events = is_global
        self.cw_log_group_arn = cw_log_group_arn
        self.cw_role_arn = cw_role_arn
        self.kms_key_id = kms_key_id
        self.check_name()
        self.check_bucket_exists()
        self.check_topic_exists()
        self.status = TrailStatus()
        self.event_selectors: list[dict[str, Any]] = []
        self.advanced_event_selectors: list[dict[str, Any]] = []
        self.insight_selectors: list[dict[str, str]] = []

    @property
    def arn(self) -> str:
        return f"arn:{get_partition(self.region_name)}:cloudtrail:{self.region_name}:{self.account_id}:trail/{self.trail_name}"

    @property
    def topic_arn(self) -> Optional[str]:
        if self.sns_topic_name:
            return f"arn:{get_partition(self.region_name)}:sns:{self.region_name}:{self.account_id}:{self.sns_topic_name}"
        return None

    def check_name(self) -> None:
        if len(self.trail_name) < 3:
            raise TrailNameTooShort(actual_length=len(self.trail_name))
        if len(self.trail_name) > 128:
            raise TrailNameTooLong(actual_length=len(self.trail_name))
        if not re.match("^[0-9a-zA-Z]{1}.+$", self.trail_name):
            raise TrailNameNotStartingCorrectly()
        if not re.match(r".+[0-9a-zA-Z]{1}$", self.trail_name):
            raise TrailNameNotEndingCorrectly()
        if not re.match(r"^[.\-_0-9a-zA-Z]+$", self.trail_name):
            raise TrailNameInvalidChars()

    def check_bucket_exists(self) -> None:
        from moto.s3.models import s3_backends

        try:
            s3_backends[self.account_id][self.partition].get_bucket(self.bucket_name)
        except Exception:
            raise S3BucketDoesNotExistException(
                f"S3 bucket {self.bucket_name} does not exist!"
            )

    def check_topic_exists(self) -> None:
        if self.topic_arn:
            from moto.sns import sns_backends

            sns_backend = sns_backends[self.account_id][self.region_name]
            try:
                sns_backend.get_topic(self.topic_arn)
            except Exception:
                raise InsufficientSnsTopicPolicyException(
                    "SNS Topic does not exist or the topic policy is incorrect!"
                )

    def start_logging(self) -> None:
        self.status.start_logging()

    def stop_logging(self) -> None:
        self.status.stop_logging()

    def put_event_selectors(
        self,
        event_selectors: list[dict[str, Any]],
        advanced_event_selectors: list[dict[str, Any]],
    ) -> None:
        if event_selectors:
            self.event_selectors = event_selectors
        elif advanced_event_selectors:
            self.event_selectors = []
            self.advanced_event_selectors = advanced_event_selectors

    def get_event_selectors(self) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
        return self.event_selectors, self.advanced_event_selectors

    def put_insight_selectors(self, insight_selectors: list[dict[str, str]]) -> None:
        self.insight_selectors.extend(insight_selectors)

    def get_insight_selectors(self) -> list[dict[str, str]]:
        return self.insight_selectors

    def update(
        self,
        s3_bucket_name: Optional[str],
        s3_key_prefix: Optional[str],
        sns_topic_name: Optional[str],
        include_global_service_events: Optional[bool],
        is_multi_region_trail: Optional[bool],
        enable_log_file_validation: Optional[bool],
        is_organization_trail: Optional[bool],
        cw_log_group_arn: Optional[str],
        cw_role_arn: Optional[str],
        kms_key_id: Optional[str],
    ) -> None:
        if s3_bucket_name is not None:
            self.bucket_name = s3_bucket_name
        if s3_key_prefix is not None:
            self.s3_key_prefix = s3_key_prefix
        if sns_topic_name is not None:
            self.sns_topic_name = sns_topic_name
        if include_global_service_events is not None:
            self.include_global_service_events = include_global_service_events
        if is_multi_region_trail is not None:
            self.is_multi_region = is_multi_region_trail
        if enable_log_file_validation is not None:
            self.log_validation = enable_log_file_validation
        if is_organization_trail is not None:
            self.is_org_trail = is_organization_trail
        if cw_log_group_arn is not None:
            self.cw_log_group_arn = cw_log_group_arn
        if cw_role_arn is not None:
            self.cw_role_arn = cw_role_arn
        if kms_key_id is not None:
            self.kms_key_id = kms_key_id

    def short(self) -> dict[str, str]:
        return {
            "Name": self.trail_name,
            "TrailARN": self.arn,
            "HomeRegion": self.region_name,
        }

    def description(self, include_region: bool = False) -> dict[str, Any]:
        desc = {
            "Name": self.trail_name,
            "S3BucketName": self.bucket_name,
            "IncludeGlobalServiceEvents": self.include_global_service_events,
            "IsMultiRegionTrail": self.is_multi_region,
            "TrailARN": self.arn,
            "LogFileValidationEnabled": self.log_validation,
            "IsOrganizationTrail": self.is_org_trail,
            "HasCustomEventSelectors": False,
            "HasInsightSelectors": False,
            "CloudWatchLogsLogGroupArn": self.cw_log_group_arn,
            "CloudWatchLogsRoleArn": self.cw_role_arn,
            "KmsKeyId": self.kms_key_id,
        }
        if self.s3_key_prefix is not None:
            desc["S3KeyPrefix"] = self.s3_key_prefix
        if self.sns_topic_name is not None:
            desc["SnsTopicName"] = self.sns_topic_name
            desc["SnsTopicARN"] = self.topic_arn
        if include_region:
            desc["HomeRegion"] = self.region_name
        return desc


class EventDataStore(BaseModel):
    def __init__(
        self,
        account_id: str,
        region_name: str,
        name: str,
        advanced_event_selectors: Optional[list[dict[str, Any]]] = None,
        multi_region_enabled: bool = True,
        organization_enabled: bool = False,
        retention_period: int = 2557,
        termination_protection_enabled: bool = True,
        kms_key_id: Optional[str] = None,
        billing_mode: str = "EXTENDABLE_RETENTION_PRICING",
    ):
        import uuid as _uuid

        self.event_data_store_id = str(_uuid.uuid4())
        self.name = name
        self.status = "ENABLED"
        self.advanced_event_selectors = advanced_event_selectors or []
        self.multi_region_enabled = multi_region_enabled
        self.organization_enabled = organization_enabled
        self.retention_period = retention_period
        self.termination_protection_enabled = termination_protection_enabled
        self.kms_key_id = kms_key_id or ""
        self.billing_mode = billing_mode
        self.created_timestamp = utcnow()
        self.updated_timestamp = utcnow()
        self.arn = f"arn:{get_partition(region_name)}:cloudtrail:{region_name}:{account_id}:eventdatastore/{self.event_data_store_id}"
        self.insight_selectors: list[dict[str, str]] = []

    def description(self) -> dict[str, Any]:
        desc: dict[str, Any] = {
            "EventDataStoreArn": self.arn,
            "Name": self.name,
            "Status": self.status,
            "AdvancedEventSelectors": self.advanced_event_selectors,
            "MultiRegionEnabled": self.multi_region_enabled,
            "OrganizationEnabled": self.organization_enabled,
            "RetentionPeriod": self.retention_period,
            "TerminationProtectionEnabled": self.termination_protection_enabled,
            "CreatedTimestamp": datetime2int(self.created_timestamp),
            "UpdatedTimestamp": datetime2int(self.updated_timestamp),
            "BillingMode": self.billing_mode,
        }
        if self.kms_key_id:
            desc["KmsKeyId"] = self.kms_key_id
        return desc


class Channel(BaseModel):
    def __init__(
        self,
        account_id: str,
        region_name: str,
        name: str,
        source: str,
        destinations: Optional[list[dict[str, Any]]] = None,
    ):
        import uuid as _uuid

        self.channel_id = str(_uuid.uuid4())
        self.name = name
        self.source = source
        self.destinations = destinations or []
        self.arn = f"arn:{get_partition(region_name)}:cloudtrail:{region_name}:{account_id}:channel/{self.channel_id}"

    def description(self) -> dict[str, Any]:
        return {
            "ChannelArn": self.arn,
            "Name": self.name,
            "Source": self.source,
            "Destinations": self.destinations,
        }


class Query(BaseModel):
    def __init__(
        self,
        event_data_store_arn: str,
        query_statement: str,
    ):
        import uuid as _uuid

        self.query_id = str(_uuid.uuid4())
        self.event_data_store_arn = event_data_store_arn
        self.query_statement = query_statement
        self.query_status = "COMPLETED"
        self.query_statistics = {
            "EventsMatched": 0,
            "EventsScanned": 0,
            "BytesScanned": 0,
            "ExecutionTimeInMillis": 100,
            "CreationTime": datetime2int(utcnow()),
        }
        self.query_results: list[list[dict[str, str]]] = []
        self.query_result_count = 0

    def description(self) -> dict[str, Any]:
        return {
            "QueryId": self.query_id,
            "QueryString": self.query_statement,
            "QueryStatus": self.query_status,
            "QueryStatistics": {
                "EventsMatched": self.query_statistics["EventsMatched"],
                "EventsScanned": self.query_statistics["EventsScanned"],
                "BytesScanned": self.query_statistics["BytesScanned"],
                "ExecutionTimeInMillis": self.query_statistics["ExecutionTimeInMillis"],
                "CreationTime": self.query_statistics["CreationTime"],
            },
        }


class CloudTrailBackend(BaseBackend):
    """Implementation of CloudTrail APIs."""

    def __init__(self, region_name: str, account_id: str):
        super().__init__(region_name, account_id)
        self.trails: dict[str, Trail] = {}
        self.tagging_service = TaggingService(tag_name="TagsList")
        self.event_data_stores: dict[str, EventDataStore] = {}
        self.channels: dict[str, Channel] = {}
        self.queries: dict[str, Query] = {}
        self.resource_policies: dict[str, str] = {}
        self.dashboards: dict[str, dict[str, Any]] = {}
        self.event_configuration: Optional[dict[str, Any]] = None

    def create_trail(
        self,
        name: str,
        bucket_name: str,
        s3_key_prefix: str,
        sns_topic_name: str,
        is_global: bool,
        is_multi_region: bool,
        log_validation: bool,
        is_org_trail: bool,
        cw_log_group_arn: str,
        cw_role_arn: str,
        kms_key_id: str,
        tags_list: list[dict[str, str]],
    ) -> Trail:
        trail = Trail(
            self.account_id,
            self.region_name,
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
        )
        self.trails[name] = trail
        self.tagging_service.tag_resource(trail.arn, tags_list)
        return trail

    def get_trail(self, name_or_arn: str) -> Trail:
        if len(name_or_arn) < 3:
            raise TrailNameTooShort(actual_length=len(name_or_arn))
        if name_or_arn in self.trails:
            return self.trails[name_or_arn]
        for trail in self.trails.values():
            if trail.arn == name_or_arn:
                return trail
        raise TrailNotFoundException(account_id=self.account_id, name=name_or_arn)

    def get_trail_status(self, name: str) -> TrailStatus:
        if len(name) < 3:
            raise TrailNameTooShort(actual_length=len(name))

        all_trails = self.describe_trails(include_shadow_trails=True)
        trail = next(
            (
                trail
                for trail in all_trails
                if trail.trail_name == name or trail.arn == name
            ),
            None,
        )
        if not trail:
            # This particular method returns the ARN as part of the error message
            arn = f"arn:{get_partition(self.region_name)}:cloudtrail:{self.region_name}:{self.account_id}:trail/{name}"
            raise TrailNotFoundException(account_id=self.account_id, name=arn)
        return trail.status

    def describe_trails(self, include_shadow_trails: bool) -> Iterable[Trail]:
        all_trails = []
        if include_shadow_trails:
            current_account = cloudtrail_backends[self.account_id]
            for backend in current_account.values():
                for trail in backend.trails.values():
                    if trail.is_multi_region or trail.region_name == self.region_name:
                        all_trails.append(trail)
        else:
            all_trails.extend(self.trails.values())
        return all_trails

    def list_trails(self) -> Iterable[Trail]:
        return self.describe_trails(include_shadow_trails=True)

    def start_logging(self, name: str) -> None:
        trail = self.trails[name]
        trail.start_logging()

    def stop_logging(self, name: str) -> None:
        trail = self.trails[name]
        trail.stop_logging()

    def delete_trail(self, name: str) -> None:
        if name in self.trails:
            del self.trails[name]

    def update_trail(
        self,
        name: str,
        s3_bucket_name: str,
        s3_key_prefix: str,
        sns_topic_name: str,
        include_global_service_events: bool,
        is_multi_region_trail: bool,
        enable_log_file_validation: bool,
        is_organization_trail: bool,
        cw_log_group_arn: str,
        cw_role_arn: str,
        kms_key_id: str,
    ) -> Trail:
        trail = self.get_trail(name_or_arn=name)
        trail.update(
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
        return trail

    def put_event_selectors(
        self,
        trail_name: str,
        event_selectors: list[dict[str, Any]],
        advanced_event_selectors: list[dict[str, Any]],
    ) -> tuple[str, list[dict[str, Any]], list[dict[str, Any]]]:
        trail = self.get_trail(trail_name)
        trail.put_event_selectors(event_selectors, advanced_event_selectors)
        trail_arn = trail.arn
        return trail_arn, event_selectors, advanced_event_selectors

    def get_event_selectors(
        self, trail_name: str
    ) -> tuple[str, list[dict[str, Any]], list[dict[str, Any]]]:
        trail = self.get_trail(trail_name)
        event_selectors, advanced_event_selectors = trail.get_event_selectors()
        return trail.arn, event_selectors, advanced_event_selectors

    def add_tags(self, resource_id: str, tags_list: list[dict[str, str]]) -> None:
        self.tagging_service.tag_resource(resource_id, tags_list)

    def remove_tags(self, resource_id: str, tags_list: list[dict[str, str]]) -> None:
        self.tagging_service.untag_resource_using_tags(resource_id, tags_list)

    def list_tags(self, resource_id_list: list[str]) -> list[dict[str, Any]]:
        """
        Pagination is not yet implemented
        """
        resp: list[dict[str, Any]] = [{"ResourceId": r_id} for r_id in resource_id_list]
        for item in resp:
            item["TagsList"] = self.tagging_service.list_tags_for_resource(
                item["ResourceId"]
            )["TagsList"]
        return resp

    def put_insight_selectors(
        self, trail_name: str, insight_selectors: list[dict[str, str]]
    ) -> tuple[str, list[dict[str, str]]]:
        trail = self.get_trail(trail_name)
        trail.put_insight_selectors(insight_selectors)
        return trail.arn, insight_selectors

    def get_insight_selectors(
        self, trail_name: str
    ) -> tuple[str, list[dict[str, str]]]:
        trail = self.get_trail(trail_name)
        return trail.arn, trail.get_insight_selectors()

    # Event Data Store operations

    def create_event_data_store(
        self,
        name: str,
        advanced_event_selectors: Optional[list[dict[str, Any]]] = None,
        multi_region_enabled: bool = True,
        organization_enabled: bool = False,
        retention_period: int = 2557,
        termination_protection_enabled: bool = True,
        kms_key_id: Optional[str] = None,
        billing_mode: str = "EXTENDABLE_RETENTION_PRICING",
        tags_list: Optional[list[dict[str, str]]] = None,
    ) -> EventDataStore:
        eds = EventDataStore(
            account_id=self.account_id,
            region_name=self.region_name,
            name=name,
            advanced_event_selectors=advanced_event_selectors,
            multi_region_enabled=multi_region_enabled,
            organization_enabled=organization_enabled,
            retention_period=retention_period,
            termination_protection_enabled=termination_protection_enabled,
            kms_key_id=kms_key_id,
            billing_mode=billing_mode,
        )
        self.event_data_stores[eds.arn] = eds
        if tags_list:
            self.tagging_service.tag_resource(eds.arn, tags_list)
        return eds

    def get_event_data_store(self, event_data_store: str) -> EventDataStore:
        # Accept either ARN or name
        if event_data_store in self.event_data_stores:
            return self.event_data_stores[event_data_store]
        # Try to find by name or partial ARN
        for arn, eds in self.event_data_stores.items():
            if eds.name == event_data_store or arn.endswith(event_data_store):
                return eds
        raise EventDataStoreNotFoundException(event_data_store)

    def list_event_data_stores(self) -> list[EventDataStore]:
        return list(self.event_data_stores.values())

    # Channel operations

    def create_channel(
        self,
        name: str,
        source: str,
        destinations: Optional[list[dict[str, Any]]] = None,
        tags_list: Optional[list[dict[str, str]]] = None,
    ) -> Channel:
        channel = Channel(
            account_id=self.account_id,
            region_name=self.region_name,
            name=name,
            source=source,
            destinations=destinations,
        )
        self.channels[channel.arn] = channel
        if tags_list:
            self.tagging_service.tag_resource(channel.arn, tags_list)
        return channel

    def get_channel(self, channel_arn: str) -> Channel:
        if channel_arn in self.channels:
            return self.channels[channel_arn]
        raise ChannelNotFoundException(channel_arn)

    def list_channels(self) -> list[Channel]:
        return list(self.channels.values())

    # Query operations

    def start_query(
        self,
        query_statement: str,
        event_data_store_arn: Optional[str] = None,
    ) -> Query:
        query = Query(
            event_data_store_arn=event_data_store_arn or "",
            query_statement=query_statement,
        )
        self.queries[query.query_id] = query
        return query

    def describe_query(self, query_id: str) -> Query:
        if query_id not in self.queries:
            raise QueryIdNotFoundException(query_id)
        return self.queries[query_id]

    def get_query_results(
        self, query_id: str
    ) -> tuple[str, list[list[dict[str, str]]], dict[str, Any]]:
        if query_id not in self.queries:
            raise QueryIdNotFoundException(query_id)
        query = self.queries[query_id]
        return query.query_status, query.query_results, query.query_statistics

    # Resource Policy operations

    def put_resource_policy(
        self,
        resource_arn: str,
        resource_policy: str,
    ) -> tuple[str, str]:
        self.resource_policies[resource_arn] = resource_policy
        return resource_arn, resource_policy

    def get_resource_policy(self, resource_arn: str) -> tuple[str, str]:
        if resource_arn not in self.resource_policies:
            raise ResourceNotFoundException(resource_arn)
        return resource_arn, self.resource_policies[resource_arn]

    # Dashboard operations

    def get_dashboard(self, dashboard_id: str) -> dict[str, Any]:
        # Dashboards are a relatively new CloudTrail feature. Return minimal stub.
        if dashboard_id in self.dashboards:
            return self.dashboards[dashboard_id]
        # Return a not-found error
        raise ResourceNotFoundException(dashboard_id)

    # Event Configuration operations

    def get_event_configuration(self) -> dict[str, Any]:
        return self.event_configuration or {}

    # Insight selectors for event data stores

    def get_insight_selectors_for_event_data_store(
        self, event_data_store: str
    ) -> tuple[str, list[dict[str, str]]]:
        eds = self.get_event_data_store(event_data_store)
        return eds.arn, eds.insight_selectors

    def put_insight_selectors_for_event_data_store(
        self,
        event_data_store: str,
        insight_selectors: list[dict[str, str]],
    ) -> tuple[str, list[dict[str, str]]]:
        eds = self.get_event_data_store(event_data_store)
        eds.insight_selectors = insight_selectors
        return eds.arn, insight_selectors


cloudtrail_backends = BackendDict(CloudTrailBackend, "cloudtrail")
