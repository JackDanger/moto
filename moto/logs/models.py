import re
from collections.abc import Iterable
from datetime import datetime, timedelta
from gzip import compress as gzip_compress
from typing import Any, Optional

from moto.core.base_backend import BackendDict, BaseBackend
from moto.core.common_models import BaseModel, CloudFormationModel
from moto.core.utils import unix_time_millis, utcnow
from moto.logs.exceptions import (
    ConflictException,
    InvalidParameterException,
    LimitExceededException,
    ResourceAlreadyExistsException,
    ResourceNotFoundException,
    ValidationException,
)
from moto.logs.logs_query import execute_query
from moto.logs.metric_filters import MetricFilters
from moto.moto_api._internal import mock_random
from moto.s3.models import MissingBucket, s3_backends
from moto.utilities.arns import parse_arn
from moto.utilities.paginator import paginate
from moto.utilities.tagging_service import TaggingService
from moto.utilities.utils import get_partition

from .utils import PAGINATION_MODEL, EventMessageFilter

MAX_RESOURCE_POLICIES_PER_REGION = 10


class Destination(BaseModel):
    def __init__(
        self,
        account_id: str,
        region: str,
        destination_name: str,
        role_arn: str,
        target_arn: str,
        access_policy: Optional[str] = None,
    ):
        self.access_policy = access_policy
        self.arn = f"arn:{get_partition(region)}:logs:{region}:{account_id}:destination:{destination_name}"
        self.creation_time = int(unix_time_millis())
        self.destination_name = destination_name
        self.role_arn = role_arn
        self.target_arn = target_arn

    def to_dict(self) -> dict[str, Any]:
        return {
            "accessPolicy": self.access_policy,
            "arn": self.arn,
            "creationTime": self.creation_time,
            "destinationName": self.destination_name,
            "roleArn": self.role_arn,
            "targetArn": self.target_arn,
        }


class LogQuery(BaseModel):
    def __init__(
        self,
        query_id: str,
        start_time: int,
        end_time: int,
        query: str,
        log_groups: list["LogGroup"],
    ):
        self.query_id = query_id
        self.start_time = start_time
        self.end_time = end_time
        self.query = query
        self.log_group_names = [lg.name for lg in log_groups]
        self.create_time = unix_time_millis()
        self.status = "Running"
        self.results = execute_query(
            log_groups=log_groups, query=query, start_time=start_time, end_time=end_time
        )
        self.status = "Complete"

    def to_json(self, log_group_name: str) -> dict[str, Any]:
        return {
            "queryId": self.query_id,
            "queryString": self.query,
            "status": self.status,
            "createTime": self.create_time,
            "logGroupName": log_group_name,
        }

    def to_result_json(self) -> dict[str, Any]:
        return {
            "results": [
                [{"field": key, "value": str(val)} for key, val in result.items()]
                for result in self.results
            ],
            "status": self.status,
        }


class LogEvent(BaseModel):
    _event_id = 0

    def __init__(self, ingestion_time: int, log_event: dict[str, Any]):
        self.ingestion_time = ingestion_time
        self.timestamp = log_event["timestamp"]
        self.message = log_event["message"]
        self.event_id = self.__class__._event_id
        self.__class__._event_id += 1
        ""

    def to_filter_dict(self) -> dict[str, Any]:
        return {
            "eventId": str(self.event_id),
            "ingestionTime": self.ingestion_time,
            # "logStreamName":
            "message": self.message,
            "timestamp": self.timestamp,
        }

    def to_response_dict(self) -> dict[str, Any]:
        return {
            "ingestionTime": self.ingestion_time,
            "message": self.message,
            "timestamp": self.timestamp,
        }


class LogStream(BaseModel):
    _log_ids = 0

    def __init__(self, log_group: "LogGroup", name: str):
        self.account_id = log_group.account_id
        self.region = log_group.region
        self.log_group = log_group
        self.arn = f"arn:{get_partition(self.region)}:logs:{self.region}:{self.account_id}:log-group:{log_group.name}:log-stream:{name}"
        self.creation_time = int(unix_time_millis())
        self.first_event_timestamp = None
        self.last_event_timestamp = None
        self.last_ingestion_time: Optional[int] = None
        self.log_stream_name = name
        self.stored_bytes = 0
        # I'm  guessing this is token needed for sequenceToken by put_events
        self.upload_sequence_token = 0
        self.events: list[LogEvent] = []

        self.__class__._log_ids += 1

    def _update(self) -> None:
        # events can be empty when stream is described soon after creation
        self.first_event_timestamp = (
            min([x.timestamp for x in self.events]) if self.events else None
        )
        self.last_event_timestamp = (
            max([x.timestamp for x in self.events]) if self.events else None
        )

    def to_describe_dict(self) -> dict[str, Any]:
        # Compute start and end times
        self._update()

        res = {
            "arn": self.arn,
            "creationTime": self.creation_time,
            "logStreamName": self.log_stream_name,
            "storedBytes": self.stored_bytes,
        }
        if self.events:
            rest = {
                "firstEventTimestamp": self.first_event_timestamp,
                "lastEventTimestamp": self.last_event_timestamp,
                "lastIngestionTime": self.last_ingestion_time,
                "uploadSequenceToken": str(self.upload_sequence_token),
            }
            res.update(rest)
        return res

    def put_log_events(self, log_events: list[dict[str, Any]]) -> str:
        # TODO: ensure sequence_token
        # TODO: to be thread safe this would need a lock
        self.last_ingestion_time = int(unix_time_millis())
        # TODO: make this match AWS if possible
        self.stored_bytes += sum(
            [len(log_event["message"]) for log_event in log_events]
        )
        events = [
            LogEvent(self.last_ingestion_time, log_event) for log_event in log_events
        ]
        self.events += events
        self.upload_sequence_token += 1

        for subscription_filter in self.log_group.subscription_filters.values():
            service = subscription_filter.destination_arn.split(":")[2]
            formatted_log_events = [
                {
                    "id": event.event_id,
                    "timestamp": event.timestamp,
                    "message": event.message,
                }
                for event in events
            ]
            self._send_log_events(
                service=service,
                destination_arn=subscription_filter.destination_arn,
                filter_name=subscription_filter.name,
                log_events=formatted_log_events,
            )
        return f"{self.upload_sequence_token:056d}"

    def _send_log_events(
        self,
        service: str,
        destination_arn: str,
        filter_name: str,
        log_events: list[dict[str, Any]],
    ) -> None:
        if service == "lambda":
            from moto.awslambda.utils import get_backend

            get_backend(self.account_id, self.region).send_log_event(
                destination_arn,
                filter_name,
                self.log_group.name,
                self.log_stream_name,
                log_events,
            )
        elif service == "firehose":
            from moto.firehose import firehose_backends

            firehose_backends[self.account_id][self.region].send_log_event(
                destination_arn,
                filter_name,
                self.log_group.name,
                self.log_stream_name,
                log_events,
            )
        elif service == "kinesis":
            from moto.kinesis import kinesis_backends

            kinesis = kinesis_backends[self.account_id][self.region]
            kinesis.send_log_event(
                destination_arn,
                filter_name,
                self.log_group.name,
                self.log_stream_name,
                log_events,
            )
        elif service == "logs":
            target_arn = parse_arn(destination_arn)
            backend: LogsBackend = logs_backends[target_arn.account][target_arn.region]
            # {name}:* --> We only need the name
            target_group_name = target_arn.resource_id.split(":")[0]
            log_group = backend._find_log_group(log_group_name=target_group_name)
            log_group.put_log_events(self.log_stream_name, log_events=log_events)

    def get_log_events(
        self,
        start_time: str,
        end_time: str,
        limit: int,
        next_token: Optional[str],
        start_from_head: str,
    ) -> tuple[list[dict[str, Any]], Optional[str], Optional[str]]:
        if limit is None:
            limit = 10000

        def filter_func(event: LogEvent) -> bool:
            if start_time and event.timestamp < start_time:
                return False

            if end_time and event.timestamp > end_time:
                return False

            return True

        def get_index_and_direction_from_token(
            token: Optional[str],
        ) -> tuple[Optional[str], int]:
            if token is not None:
                try:
                    return token[0], int(token[2:])
                except Exception:
                    raise InvalidParameterException(
                        "The specified nextToken is invalid."
                    )
            return None, 0

        events = sorted(
            filter(filter_func, self.events), key=lambda event: event.timestamp
        )

        direction, index = get_index_and_direction_from_token(next_token)
        limit_index = limit - 1
        final_index = len(events) - 1

        if direction is None:
            if start_from_head:
                start_index = 0
                end_index = start_index + limit_index
            else:
                end_index = final_index
                start_index = end_index - limit_index
        elif direction == "f":
            start_index = index + 1
            end_index = start_index + limit_index
        elif direction == "b":
            end_index = index - 1
            start_index = end_index - limit_index
        else:
            raise InvalidParameterException("The specified nextToken is invalid.")

        if start_index < 0:
            start_index = 0
        elif start_index > final_index:
            return ([], f"b/{final_index:056d}", f"f/{final_index:056d}")

        if end_index > final_index:
            end_index = final_index
        elif end_index < 0:
            return ([], f"b/{0:056d}", f"f/{0:056d}")

        events_page = [
            event.to_response_dict() for event in events[start_index : end_index + 1]
        ]

        return (events_page, f"b/{start_index:056d}", f"f/{end_index:056d}")

    def filter_log_events(
        self, start_time: int, end_time: int, filter_pattern: str
    ) -> list[dict[str, Any]]:
        def filter_func(event: LogEvent) -> bool:
            if start_time and event.timestamp < start_time:
                return False

            if end_time and event.timestamp > end_time:
                return False

            if not EventMessageFilter(filter_pattern).matches(event.message):
                return False

            return True

        events: list[dict[str, Any]] = []
        for event in sorted(
            filter(filter_func, self.events), key=lambda x: x.timestamp
        ):
            event_obj = event.to_filter_dict()
            event_obj["logStreamName"] = self.log_stream_name
            events.append(event_obj)
        return events


class SubscriptionFilter(BaseModel):
    def __init__(
        self,
        name: str,
        log_group_name: str,
        filter_pattern: str,
        destination_arn: str,
        role_arn: str,
    ):
        self.name = name
        self.log_group_name = log_group_name
        self.filter_pattern = filter_pattern
        self.destination_arn = destination_arn
        self.role_arn = role_arn
        self.creation_time = int(unix_time_millis())

    def update(self, filter_pattern: str, destination_arn: str, role_arn: str) -> None:
        self.filter_pattern = filter_pattern
        self.destination_arn = destination_arn
        self.role_arn = role_arn

    def to_json(self) -> dict[str, Any]:
        return {
            "filterName": self.name,
            "logGroupName": self.log_group_name,
            "filterPattern": self.filter_pattern,
            "destinationArn": self.destination_arn,
            "roleArn": self.role_arn,
            "distribution": "ByLogStream",
            "creationTime": self.creation_time,
        }


class LogGroup(CloudFormationModel):
    def __init__(
        self,
        account_id: str,
        region: str,
        name: str,
        **kwargs: Any,
    ):
        self.name = name
        self.account_id = account_id
        self.region = region
        self.arn = (
            f"arn:{get_partition(region)}:logs:{region}:{account_id}:log-group:{name}"
        )
        self.creation_time = int(unix_time_millis())
        self.streams: dict[str, LogStream] = {}  # {name: LogStream}
        # AWS defaults to Never Expire for log group retention
        self.retention_in_days = kwargs.get("RetentionInDays")
        self.subscription_filters: dict[str, SubscriptionFilter] = {}
        self.data_protection_policy: Optional[dict[str, Any]] = None
        self.transformer: Optional[dict[str, Any]] = None
        self.deletion_protection: bool = False

        # The Amazon Resource Name (ARN) of the CMK to use when encrypting log data. It is optional.
        # Docs:
        # https://docs.aws.amazon.com/AmazonCloudWatchLogs/latest/APIReference/API_CreateLogGroup.html
        self.kms_key_id = kwargs.get("kmsKeyId")

    @staticmethod
    def cloudformation_name_type() -> str:
        return "LogGroupName"

    @staticmethod
    def cloudformation_type() -> str:
        # https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-logs-loggroup.html
        return "AWS::Logs::LogGroup"

    @classmethod
    def create_from_cloudformation_json(  # type: ignore[misc]
        cls,
        resource_name: str,
        cloudformation_json: Any,
        account_id: str,
        region_name: str,
        **kwargs: Any,
    ) -> "LogGroup":
        properties = cloudformation_json["Properties"]
        tags = properties.get("Tags", [])
        tags = dict([tag.values() for tag in tags])

        return logs_backends[account_id][region_name].create_log_group(
            resource_name, tags, **properties
        )

    def delete(self, account_id: str, region_name: str) -> None:
        backend = logs_backends[account_id][region_name]
        backend.delete_log_group(self.name)

    @classmethod
    def has_cfn_attr(cls, attr: str) -> bool:
        return attr in ["Arn"]

    def get_cfn_attribute(self, attribute_name: str) -> str:
        from moto.cloudformation.exceptions import UnformattedGetAttTemplateException

        if attribute_name == "Arn":
            return self.arn
        raise UnformattedGetAttTemplateException()

    @property
    def physical_resource_id(self) -> str:
        return self.name

    def create_log_stream(self, log_stream_name: str) -> None:
        if log_stream_name in self.streams:
            raise ResourceAlreadyExistsException()
        stream = LogStream(log_group=self, name=log_stream_name)

        self.streams[log_stream_name] = stream

    def delete_log_stream(self, log_stream_name: str) -> None:
        if log_stream_name not in self.streams:
            raise ResourceNotFoundException()
        del self.streams[log_stream_name]

    def describe_log_streams(
        self,
        descending: bool,
        log_group_name: str,
        log_stream_name_prefix: str,
        order_by: str,
        limit: int,
        next_token: Optional[str] = None,
    ) -> tuple[list[dict[str, Any]], Optional[str]]:
        # responses only log_stream_name, creation_time, arn, stored_bytes when no events are stored.

        log_streams = [
            (name, stream.to_describe_dict())
            for name, stream in self.streams.items()
            if name.startswith(log_stream_name_prefix)
        ]

        def sorter(item: Any) -> Any:
            return (
                item[0]
                if order_by == "LogStreamName"
                else item[1].get("lastEventTimestamp", 0)
            )

        log_streams = sorted(log_streams, key=sorter, reverse=descending)
        first_index = 0
        if next_token:
            try:
                group, stream = next_token.split("@")
                if group != log_group_name:
                    raise ValueError()
                first_index = (
                    next(
                        index
                        for (index, e) in enumerate(log_streams)
                        if e[1]["logStreamName"] == stream
                    )
                    + 1
                )
            except (ValueError, StopIteration):
                first_index = 0
                log_streams = []

        last_index = first_index + limit
        if last_index > len(log_streams):
            last_index = len(log_streams)
        log_streams_page = [x[1] for x in log_streams[first_index:last_index]]
        new_token = None
        if log_streams_page and last_index < len(log_streams):
            new_token = f"{log_group_name}@{log_streams_page[-1]['logStreamName']}"

        return log_streams_page, new_token

    def put_log_events(
        self,
        log_stream_name: str,
        log_events: list[dict[str, Any]],
    ) -> str:
        if log_stream_name not in self.streams:
            raise ResourceNotFoundException("The specified log stream does not exist.")
        stream = self.streams[log_stream_name]
        return stream.put_log_events(log_events)

    def get_log_events(
        self,
        log_stream_name: str,
        start_time: str,
        end_time: str,
        limit: int,
        next_token: Optional[str],
        start_from_head: str,
    ) -> tuple[list[dict[str, Any]], Optional[str], Optional[str]]:
        if log_stream_name not in self.streams:
            raise ResourceNotFoundException()
        stream = self.streams[log_stream_name]
        return stream.get_log_events(
            start_time,
            end_time,
            limit,
            next_token,
            start_from_head,
        )

    def filter_log_events(
        self,
        log_group_name: str,
        log_stream_names: list[str],
        start_time: int,
        end_time: int,
        limit: Optional[int],
        next_token: Optional[str],
        filter_pattern: str,
        interleaved: bool,
    ) -> tuple[list[dict[str, Any]], Optional[str], list[dict[str, Any]]]:
        if not limit:
            limit = 10000
        streams = [
            stream
            for name, stream in self.streams.items()
            if not log_stream_names or name in log_stream_names
        ]

        events = []
        for stream in streams:
            events += stream.filter_log_events(start_time, end_time, filter_pattern)

        if interleaved:
            events = sorted(events, key=lambda event: event["timestamp"])

        first_index = 0
        if next_token:
            try:
                group, stream_name, event_id = next_token.split("@")
                if group != log_group_name:
                    raise ValueError()
                first_index = (
                    next(
                        index
                        for (index, e) in enumerate(events)
                        if e["logStreamName"] == stream_name
                        and e["eventId"] == event_id
                    )
                    + 1
                )
            except (ValueError, StopIteration):
                first_index = 0
                # AWS returns an empty list if it receives an invalid token.
                events = []

        last_index = first_index + limit
        if last_index > len(events):
            last_index = len(events)
        events_page = events[first_index:last_index]
        next_token = None
        if events_page and last_index < len(events):
            last_event = events_page[-1]
            next_token = f"{log_group_name}@{last_event['logStreamName']}@{last_event['eventId']}"

        searched_streams = [
            {"logStreamName": stream.log_stream_name, "searchedCompletely": True}
            for stream in streams
        ]
        return events_page, next_token, searched_streams

    def to_describe_dict(self) -> dict[str, Any]:
        log_group = {
            "arn": f"{self.arn}:*",
            "logGroupArn": self.arn,
            "creationTime": self.creation_time,
            "logGroupName": self.name,
            "metricFilterCount": 0,
            "storedBytes": sum(s.stored_bytes for s in self.streams.values()),
        }
        # AWS only returns retentionInDays if a value is set for the log group (ie. not Never Expire)
        if self.retention_in_days:
            log_group["retentionInDays"] = self.retention_in_days
        if self.kms_key_id:
            log_group["kmsKeyId"] = self.kms_key_id
        return log_group

    def set_retention_policy(self, retention_in_days: Optional[str]) -> None:
        self.retention_in_days = retention_in_days

    def describe_subscription_filters(self) -> Iterable[SubscriptionFilter]:
        return self.subscription_filters.values()

    def put_subscription_filter(
        self, filter_name: str, filter_pattern: str, destination_arn: str, role_arn: str
    ) -> None:
        # only two subscription filters can be associated with a log group
        if len(self.subscription_filters) == 2:
            raise LimitExceededException()

        # Update existing filter
        if filter_name in self.subscription_filters:
            self.subscription_filters[filter_name].update(
                filter_pattern, destination_arn, role_arn
            )
            return

        self.subscription_filters[filter_name] = SubscriptionFilter(
            name=filter_name,
            log_group_name=self.name,
            filter_pattern=filter_pattern,
            destination_arn=destination_arn,
            role_arn=role_arn,
        )

    def delete_subscription_filter(self, filter_name: str) -> None:
        if filter_name not in self.subscription_filters:
            raise ResourceNotFoundException(
                "The specified subscription filter does not exist."
            )

        self.subscription_filters.pop(filter_name)


class LogResourcePolicy(CloudFormationModel):
    def __init__(self, policy_name: str, policy_document: str):
        self.policy_name = policy_name
        self.policy_document = policy_document
        self.last_updated_time = int(unix_time_millis())

    def update(self, policy_document: str) -> None:
        self.policy_document = policy_document
        self.last_updated_time = int(unix_time_millis())

    def describe(self) -> dict[str, Any]:
        return {
            "policyName": self.policy_name,
            "policyDocument": self.policy_document,
            "lastUpdatedTime": self.last_updated_time,
        }

    @property
    def physical_resource_id(self) -> str:
        return self.policy_name

    @staticmethod
    def cloudformation_name_type() -> str:
        return "PolicyName"

    @staticmethod
    def cloudformation_type() -> str:
        # https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-logs-resourcepolicy.html
        return "AWS::Logs::ResourcePolicy"

    @classmethod
    def create_from_cloudformation_json(  # type: ignore[misc]
        cls,
        resource_name: str,
        cloudformation_json: Any,
        account_id: str,
        region_name: str,
        **kwargs: Any,
    ) -> "LogResourcePolicy":
        properties = cloudformation_json["Properties"]
        policy_name = properties["PolicyName"]
        policy_document = properties["PolicyDocument"]
        return logs_backends[account_id][region_name].put_resource_policy(
            policy_name, policy_document
        )

    @classmethod
    def update_from_cloudformation_json(  # type: ignore[misc]
        cls,
        original_resource: Any,
        new_resource_name: str,
        cloudformation_json: Any,
        account_id: str,
        region_name: str,
    ) -> "LogResourcePolicy":
        properties = cloudformation_json["Properties"]
        policy_name = properties["PolicyName"]
        policy_document = properties["PolicyDocument"]

        backend = logs_backends[account_id][region_name]
        updated = backend.put_resource_policy(policy_name, policy_document)
        # TODO: move `update by replacement logic` to cloudformation. this is required for implementing rollbacks
        if original_resource.policy_name != policy_name:
            backend.delete_resource_policy(original_resource.policy_name)
        return updated

    @classmethod
    def delete_from_cloudformation_json(  # type: ignore[misc]
        cls,
        resource_name: str,
        cloudformation_json: Any,
        account_id: str,
        region_name: str,
    ) -> None:
        logs_backends[account_id][region_name].delete_resource_policy(resource_name)


class ExportTask(BaseModel):
    def __init__(
        self,
        task_id: str,
        task_name: str,
        log_group_name: str,
        destination: str,
        destination_prefix: str,
        from_time: int,
        to: int,
    ):
        self.task_id = task_id
        self.task_name = task_name
        self.log_group_name = log_group_name
        self.destination = destination
        self.destination_prefix = destination_prefix
        self.from_time = from_time
        self.to = to
        self.status = {"code": "active", "message": "Task is active"}

    def to_json(self) -> dict[str, Any]:
        return {
            "taskId": self.task_id,
            "taskName": self.task_name,
            "logGroupName": self.log_group_name,
            "destination": self.destination,
            "destinationPrefix": self.destination_prefix,
            "from": self.from_time,
            "to": self.to,
            "status": self.status,
        }


class DeliveryDestination(BaseModel):
    def __init__(
        self,
        account_id: str,
        region: str,
        name: str,
        output_format: Optional[str],
        delivery_destination_configuration: dict[str, str],
        tags: Optional[dict[str, str]],
        policy: Optional[str] = None,
    ):
        self.name = name
        self.output_format = output_format
        self.arn = f"arn:aws:logs:{region}:{account_id}:delivery-destination:{name}"
        destination_type = delivery_destination_configuration[
            "destinationResourceArn"
        ].split(":")[2]
        if destination_type == "s3":
            self.delivery_destination_type = "S3"
        elif destination_type == "logs":
            self.delivery_destination_type = "CWL"
        elif destination_type == "firehose":
            self.delivery_destination_type = "FH"
        self.delivery_destination_configuration = delivery_destination_configuration
        self.tags = tags
        self.policy = policy

    def to_dict(self) -> dict[str, Any]:
        dct = {
            "name": self.name,
            "arn": self.arn,
            "deliveryDestinationType": self.delivery_destination_type,
            "outputFormat": self.output_format,
            "deliveryDestinationConfiguration": self.delivery_destination_configuration,
            "tags": self.tags,
        }
        dct_items = {k: v for k, v in dct.items() if v}
        return dct_items


class DeliverySource(BaseModel):
    def __init__(
        self,
        account_id: str,
        region: str,
        name: str,
        resource_arn: str,
        log_type: str,
        tags: Optional[dict[str, str]],
    ):
        res_arns = []
        res_arns.append(resource_arn)
        self.name = name
        self.arn = f"arn:aws:logs:{region}:{account_id}:delivery-source:{name}"
        self.resource_arns = res_arns
        self.service = resource_arn.split(":")[2]
        self.log_type = log_type
        self.tags = tags

    def to_dict(self) -> dict[str, Any]:
        dct = {
            "name": self.name,
            "arn": self.arn,
            "resourceArns": self.resource_arns,
            "service": self.service,
            "logType": self.log_type,
            "tags": self.tags,
        }
        dct_items = {k: v for k, v in dct.items() if v}
        return dct_items


class Delivery(BaseModel):
    def __init__(
        self,
        account_id: str,
        region: str,
        delivery_source_name: str,
        delivery_destination_arn: str,
        destination_type: str,
        record_fields: Optional[list[str]],
        field_delimiter: Optional[str],
        s3_delivery_configuration: Optional[dict[str, Any]],
        tags: Optional[dict[str, str]],
    ):
        self.id = mock_random.get_random_string(length=16)
        self.arn = f"arn:aws:logs:{region}:{account_id}:delivery:{self.id}"
        self.delivery_source_name = delivery_source_name
        self.delivery_destination_arn = delivery_destination_arn
        self.destination_type = destination_type
        # Default record fields
        default_record_fields = [
            "date",
            "time",
            "x-edge-location",
            "sc-bytes",
            "c-ip",
            "cs-method",
            "cs(Host)",
            "cs-uri-stem",
            "sc-status",
            "cs(Referer)",
            "cs(User-Agent)",
            "cs-uri-query",
            "cs(Cookie)",
            "x-edge-result-type",
            "x-edge-request-id",
            "x-host-header",
            "cs-protocol",
            "cs-bytes",
            "time-taken",
            "x-forwarded-for",
            "ssl-protocol",
            "ssl-cipher",
            "x-edge-response-result-type",
            "cs-protocol-version",
            "fle-status",
            "fle-encrypted-fields",
            "c-port",
            "time-to-first-byte",
            "x-edge-detailed-result-type",
            "sc-content-type",
            "sc-content-len",
            "sc-range-start",
            "sc-range-end",
        ]
        self.record_fields = record_fields or default_record_fields
        self.field_delimiter = field_delimiter
        default_s3_configuration = {}
        if destination_type == "S3":
            # Default s3 configuration
            default_s3_configuration = {
                "suffixPath": "AWSLogs/{account-id}/CloudFront/",
                "enableHiveCompatiblePath": False,
            }
        self.s3_delivery_configuration = (
            s3_delivery_configuration or default_s3_configuration
        )
        self.tags = tags

    def to_dict(self) -> dict[str, Any]:
        dct = {
            "id": self.id,
            "arn": self.arn,
            "deliverySourceName": self.delivery_source_name,
            "deliveryDestinationArn": self.delivery_destination_arn,
            "deliveryDestinationType": self.destination_type,
            "recordFields": self.record_fields,
            "fieldDelimiter": self.field_delimiter,
            "s3DeliveryConfiguration": self.s3_delivery_configuration,
            "tags": self.tags,
        }
        dct_items = {k: v for k, v in dct.items() if v}
        return dct_items


class AccountPolicy(BaseModel):
    def __init__(
        self,
        account_id: str,
        policy_name: str,
        policy_document: str,
        policy_type: str,
        scope: Optional[str],
        selection_criteria: Optional[str],
    ):
        self.account_id = account_id
        self.policy_name = policy_name
        self.policy_document = policy_document
        self.policy_type = policy_type
        self.scope = scope or "ALL"
        self.selection_criteria = selection_criteria
        self.last_updated_time = int(unix_time_millis())

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {
            "accountId": self.account_id,
            "policyName": self.policy_name,
            "policyDocument": self.policy_document,
            "policyType": self.policy_type,
            "scope": self.scope,
            "lastUpdatedTime": self.last_updated_time,
        }
        if self.selection_criteria:
            result["selectionCriteria"] = self.selection_criteria
        return result


class LogAnomalyDetector(BaseModel):
    def __init__(
        self,
        account_id: str,
        region: str,
        detector_name: str,
        log_group_arn_list: list[str],
        evaluation_frequency: Optional[str],
        filter_pattern: Optional[str],
        kms_key_id: Optional[str],
        anomaly_visibility_time: Optional[int],
        tags: Optional[dict[str, str]],
    ):
        self.detector_name = detector_name
        self.anomaly_detector_arn = f"arn:{get_partition(region)}:logs:{region}:{account_id}:anomaly-detector:{mock_random.get_random_hex(8)}"
        self.log_group_arn_list = log_group_arn_list
        self.evaluation_frequency = evaluation_frequency or "FIVE_MIN"
        self.filter_pattern = filter_pattern or ""
        self.kms_key_id = kms_key_id
        self.anomaly_visibility_time = anomaly_visibility_time or 7
        self.tags = tags or {}
        self.anomaly_detector_status = "TRAINING"
        self.creation_time_stamp = int(unix_time_millis())
        self.last_modified_time_stamp = int(unix_time_millis())

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {
            "detectorName": self.detector_name,
            "anomalyDetectorArn": self.anomaly_detector_arn,
            "logGroupArnList": self.log_group_arn_list,
            "evaluationFrequency": self.evaluation_frequency,
            "filterPattern": self.filter_pattern,
            "anomalyDetectorStatus": self.anomaly_detector_status,
            "anomalyVisibilityTime": self.anomaly_visibility_time,
            "creationTimeStamp": self.creation_time_stamp,
            "lastModifiedTimeStamp": self.last_modified_time_stamp,
        }
        if self.kms_key_id:
            result["kmsKeyId"] = self.kms_key_id
        return result


class IndexPolicy(BaseModel):
    def __init__(
        self,
        account_id: str,
        log_group_identifier: str,
        policy_document: str,
        log_group_name: str,
    ):
        self.policy_name = "default"
        self.policy_document = policy_document
        self.log_group_identifier = log_group_identifier
        self.source = account_id
        self.last_update_time = int(unix_time_millis())
        # Store the log group name for lookup
        self.log_group_name = log_group_name

    def to_dict(self) -> dict[str, Any]:
        return {
            "policyName": self.policy_name,
            "policyDocument": self.policy_document,
            "logGroupIdentifier": self.log_group_identifier,
            "source": self.source,
            "lastUpdateTime": self.last_update_time,
        }


class ScheduledQuery(BaseModel):
    def __init__(
        self,
        account_id: str,
        region: str,
        name: str,
        query_string: str,
        log_group_names: list[str],
        schedule_expression: str,
        target_configuration: Optional[dict[str, Any]] = None,
        query_language: str = "CWLI",
    ):
        self.name = name
        self.scheduled_query_id = mock_random.get_random_hex(16)
        self.arn = (
            f"arn:{get_partition(region)}:logs:{region}:{account_id}"
            f":scheduled-query:{self.scheduled_query_id}"
        )
        self.query_string = query_string
        self.query_language = query_language
        self.log_group_names = log_group_names
        self.schedule_expression = schedule_expression
        self.target_configuration = target_configuration or {}
        self.status = "ACTIVE"
        self.creation_time = int(unix_time_millis())
        self.last_modified_time = int(unix_time_millis())
        self.run_status: Optional[dict[str, Any]] = None

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {
            "name": self.name,
            "scheduledQueryId": self.scheduled_query_id,
            "arn": self.arn,
            "queryLanguage": self.query_language,
            "queryString": self.query_string,
            "logGroupIdentifiers": self.log_group_names,
            "scheduleExpression": self.schedule_expression,
            "status": self.status,
            "creationTime": self.creation_time,
            "lastModifiedTime": self.last_modified_time,
        }
        if self.target_configuration:
            result["targetConfiguration"] = self.target_configuration
        if self.run_status:
            result["runStatus"] = self.run_status
        return result


class LogsBackend(BaseBackend):
    def __init__(self, region_name: str, account_id: str):
        super().__init__(region_name, account_id)
        self.groups: dict[str, LogGroup] = {}
        self.filters = MetricFilters()
        self.queries: dict[str, LogQuery] = {}
        self.resource_policies: dict[str, LogResourcePolicy] = {}
        self.destinations: dict[str, Destination] = {}
        self.tagger = TaggingService()
        self.export_tasks: dict[str, ExportTask] = {}
        self.delivery_destinations: dict[str, DeliveryDestination] = {}
        self.delivery_sources: dict[str, DeliverySource] = {}
        self.deliveries: dict[str, Delivery] = {}
        self.query_definitions: dict[str, dict[str, Any]] = {}
        self.account_policies: dict[str, dict[str, AccountPolicy]] = {}
        self.anomaly_detectors: dict[str, LogAnomalyDetector] = {}
        self.index_policies: dict[str, IndexPolicy] = {}
        self.scheduled_queries: dict[str, ScheduledQuery] = {}

    def create_log_group(
        self, log_group_name: str, tags: dict[str, str], **kwargs: Any
    ) -> LogGroup:
        if log_group_name in self.groups:
            raise ResourceAlreadyExistsException()
        if len(log_group_name) > 512:
            raise InvalidParameterException(
                constraint="Member must have length less than or equal to 512",
                parameter="logGroupName",
                value=log_group_name,
            )
        self.groups[log_group_name] = LogGroup(
            self.account_id, self.region_name, log_group_name, **kwargs
        )
        self.tag_resource(self.groups[log_group_name].arn, tags)
        return self.groups[log_group_name]

    def ensure_log_group(self, log_group_name: str) -> None:
        if log_group_name in self.groups:
            return
        self.groups[log_group_name] = LogGroup(
            self.account_id,
            self.region_name,
            log_group_name,
        )

    def delete_log_group(self, log_group_name: str) -> None:
        if log_group_name not in self.groups:
            raise ResourceNotFoundException()
        del self.groups[log_group_name]

    @paginate(pagination_model=PAGINATION_MODEL)
    def describe_log_groups(
        self, log_group_name_prefix: Optional[str] = None
    ) -> list[LogGroup]:
        groups = [
            group
            for name, group in self.groups.items()
            if name.startswith(log_group_name_prefix or "")
        ]
        return sorted(groups, key=lambda x: x.name)

    def get_destination(self, destination_name: str) -> Destination:
        for destination in self.destinations:
            if self.destinations[destination].destination_name == destination_name:
                return self.destinations[destination]
        raise ResourceNotFoundException()

    def put_destination(
        self,
        destination_name: str,
        role_arn: str,
        target_arn: str,
        tags: dict[str, str],
    ) -> Destination:
        for _, destination in self.destinations.items():
            if destination.destination_name == destination_name:
                if role_arn:
                    destination.role_arn = role_arn
                if target_arn:
                    destination.target_arn = target_arn
                return destination
        destination = Destination(
            self.account_id, self.region_name, destination_name, role_arn, target_arn
        )
        self.destinations[destination.arn] = destination
        self.tag_resource(destination.arn, tags)
        return destination

    def delete_destination(self, destination_name: str) -> None:
        destination = self.get_destination(destination_name)
        self.destinations.pop(destination.arn)
        return

    def describe_destinations(
        self, destination_name_prefix: str, limit: int, next_token: Optional[int] = None
    ) -> tuple[list[dict[str, Any]], Optional[int]]:
        if limit > 50:
            raise InvalidParameterException(
                constraint="Member must have value less than or equal to 50",
                parameter="limit",
                value=limit,
            )

        result = []
        for destination in self.destinations:
            result.append(self.destinations[destination].to_dict())
        if next_token:
            result = result[: int(next_token)]

        if destination_name_prefix:
            result = [
                destination
                for destination in result
                if destination["destinationName"].startswith(destination_name_prefix)
            ]

        return result, next_token

    def put_destination_policy(self, destination_name: str, access_policy: str) -> None:
        destination = self.get_destination(destination_name)
        destination.access_policy = access_policy
        return

    def create_log_stream(self, log_group_name: str, log_stream_name: str) -> None:
        if log_group_name not in self.groups:
            raise ResourceNotFoundException()
        log_group = self.groups[log_group_name]
        log_group.create_log_stream(log_stream_name)

    def ensure_log_stream(self, log_group_name: str, log_stream_name: str) -> None:
        if log_group_name not in self.groups:
            raise ResourceNotFoundException()

        if log_stream_name in self.groups[log_group_name].streams:
            return

        self.create_log_stream(log_group_name, log_stream_name)

    def delete_log_stream(self, log_group_name: str, log_stream_name: str) -> None:
        if log_group_name not in self.groups:
            raise ResourceNotFoundException()
        log_group = self.groups[log_group_name]
        log_group.delete_log_stream(log_stream_name)

    def describe_log_streams(
        self,
        descending: bool,
        limit: int,
        log_group_name: str,
        log_group_id: str,
        log_stream_name_prefix: str,
        next_token: Optional[str],
        order_by: str,
    ) -> tuple[list[dict[str, Any]], Optional[str]]:
        log_group = self._find_log_group(log_group_id, log_group_name=log_group_name)
        if limit > 50:
            raise InvalidParameterException(
                constraint="Member must have value less than or equal to 50",
                parameter="limit",
                value=limit,
            )
        if order_by not in ["LogStreamName", "LastEventTime"]:
            raise InvalidParameterException(
                constraint="Member must satisfy enum value set: [LogStreamName, LastEventTime]",
                parameter="orderBy",
                value=order_by,
            )
        if order_by == "LastEventTime" and log_stream_name_prefix:
            raise InvalidParameterException(
                msg="Cannot order by LastEventTime with a logStreamNamePrefix."
            )
        return log_group.describe_log_streams(
            descending=descending,
            limit=limit,
            log_group_name=log_group_name,
            log_stream_name_prefix=log_stream_name_prefix,
            next_token=next_token,
            order_by=order_by,
        )

    def put_log_events(
        self,
        log_group_name: str,
        log_stream_name: str,
        log_events: list[dict[str, Any]],
    ) -> tuple[str, dict[str, Any]]:
        """
        The SequenceToken-parameter is not yet implemented
        """
        if log_group_name not in self.groups:
            raise ResourceNotFoundException()
        log_group = self.groups[log_group_name]

        # Only events from the last 14 days or 2 hours in the future are accepted
        rejected_info = {}
        allowed_events = []
        last_timestamp = None
        oldest = int(unix_time_millis(utcnow() - timedelta(days=14)))
        newest = int(unix_time_millis(utcnow() + timedelta(hours=2)))
        for idx, event in enumerate(log_events):
            if last_timestamp and last_timestamp > event["timestamp"]:
                raise InvalidParameterException(
                    "Log events in a single PutLogEvents request must be in chronological order."
                )
            if event["timestamp"] < oldest:
                rejected_info["tooOldLogEventEndIndex"] = idx
            elif event["timestamp"] > newest:
                rejected_info["tooNewLogEventStartIndex"] = idx
            else:
                allowed_events.append(event)
            last_timestamp = event["timestamp"]

        token = log_group.put_log_events(log_stream_name, allowed_events)
        return token, rejected_info

    def get_log_events(
        self,
        log_group_name: str,
        log_group_id: str,
        log_stream_name: str,
        start_time: str,
        end_time: str,
        limit: int,
        next_token: Optional[str],
        start_from_head: str,
    ) -> tuple[list[dict[str, Any]], Optional[str], Optional[str]]:
        log_group = self._find_log_group(
            log_group_id=log_group_id, log_group_name=log_group_name
        )
        if limit and limit > 10000:
            raise InvalidParameterException(
                constraint="Member must have value less than or equal to 10000",
                parameter="limit",
                value=limit,
            )
        return log_group.get_log_events(
            log_stream_name, start_time, end_time, limit, next_token, start_from_head
        )

    def filter_log_events(
        self,
        log_group_name: str,
        log_stream_names: list[str],
        start_time: int,
        end_time: int,
        limit: Optional[int],
        next_token: Optional[str],
        filter_pattern: str,
        interleaved: bool,
    ) -> tuple[list[dict[str, Any]], Optional[str], list[dict[str, Any]]]:
        """
        The following filter patterns are currently supported: Single Terms, Multiple Terms, Exact Phrases.
        If the pattern is not supported, all events are returned.
        """
        if log_group_name not in self.groups:
            raise ResourceNotFoundException()
        if limit and limit > 10000:
            raise InvalidParameterException(
                constraint="Member must have value less than or equal to 10000",
                parameter="limit",
                value=limit,
            )
        log_group = self.groups[log_group_name]
        return log_group.filter_log_events(
            log_group_name,
            log_stream_names,
            start_time,
            end_time,
            limit,
            next_token,
            filter_pattern,
            interleaved,
        )

    def put_retention_policy(self, log_group_name: str, retention_in_days: str) -> None:
        if log_group_name not in self.groups:
            raise ResourceNotFoundException()
        self.groups[log_group_name].set_retention_policy(retention_in_days)

    def delete_retention_policy(self, log_group_name: str) -> None:
        if log_group_name not in self.groups:
            raise ResourceNotFoundException()
        self.groups[log_group_name].set_retention_policy(None)

    def describe_resource_policies(self) -> list[LogResourcePolicy]:
        """
        Return list of resource policies.

        The next_token and limit arguments are ignored.  The maximum
        number of resource policies per region is a small number (less
        than 50), so pagination isn't needed.
        """

        return list(self.resource_policies.values())

    def put_resource_policy(
        self, policy_name: str, policy_doc: str
    ) -> LogResourcePolicy:
        """
        Creates/updates resource policy and return policy object
        """
        if policy_name in self.resource_policies:
            policy = self.resource_policies[policy_name]
            policy.update(policy_doc)
            return policy
        if len(self.resource_policies) == MAX_RESOURCE_POLICIES_PER_REGION:
            raise LimitExceededException()
        policy = LogResourcePolicy(policy_name, policy_doc)
        self.resource_policies[policy_name] = policy
        return policy

    def delete_resource_policy(self, policy_name: str) -> None:
        """
        Remove resource policy with a policy name matching given name.
        """
        if policy_name not in self.resource_policies:
            raise ResourceNotFoundException(
                msg=f"Policy with name [{policy_name}] does not exist"
            )
        del self.resource_policies[policy_name]

    def list_tags_log_group(self, log_group_name: str) -> dict[str, str]:
        if log_group_name not in self.groups:
            raise ResourceNotFoundException()
        log_group = self.groups[log_group_name]
        return self.list_tags_for_resource(log_group.arn)

    def tag_log_group(self, log_group_name: str, tags: dict[str, str]) -> None:
        if log_group_name not in self.groups:
            raise ResourceNotFoundException()
        log_group = self.groups[log_group_name]
        self.tag_resource(log_group.arn, tags)

    def untag_log_group(self, log_group_name: str, tags: list[str]) -> None:
        if log_group_name not in self.groups:
            raise ResourceNotFoundException()
        log_group = self.groups[log_group_name]
        self.untag_resource(log_group.arn, tags)

    def put_metric_filter(
        self,
        filter_name: str,
        filter_pattern: str,
        log_group_name: str,
        metric_transformations: str,
    ) -> None:
        self.filters.add_filter(
            filter_name, filter_pattern, log_group_name, metric_transformations
        )

    def describe_metric_filters(
        self,
        prefix: Optional[str] = None,
        log_group_name: Optional[str] = None,
        metric_name: Optional[str] = None,
        metric_namespace: Optional[str] = None,
    ) -> list[dict[str, Any]]:
        filters = self.filters.get_matching_filters(
            prefix, log_group_name, metric_name, metric_namespace
        )
        return filters

    def delete_metric_filter(
        self, filter_name: Optional[str] = None, log_group_name: Optional[str] = None
    ) -> None:
        self.filters.delete_filter(filter_name, log_group_name)

    def describe_subscription_filters(
        self, log_group_name: str
    ) -> Iterable[SubscriptionFilter]:
        log_group = self.groups.get(log_group_name)

        if not log_group:
            raise ResourceNotFoundException()

        return log_group.describe_subscription_filters()

    def put_subscription_filter(
        self,
        log_group_name: str,
        filter_name: str,
        filter_pattern: str,
        destination_arn: str,
        role_arn: str,
    ) -> None:
        log_group = self.groups.get(log_group_name)

        if not log_group:
            raise ResourceNotFoundException()

        parsed_arn = parse_arn(destination_arn)
        service = parsed_arn.service

        if service == "lambda":
            from moto.awslambda.utils import get_backend

            try:
                get_backend(self.account_id, self.region_name).get_function(
                    destination_arn
                )
            # no specific permission check implemented
            except Exception:
                raise InvalidParameterException(
                    "Could not execute the lambda function. Make sure you "
                    "have given CloudWatch Logs permission to execute your "
                    "function."
                )
        elif service == "firehose":
            from moto.firehose import firehose_backends

            firehose = firehose_backends[self.account_id][
                self.region_name
            ].lookup_name_from_arn(destination_arn)
            if not firehose:
                raise InvalidParameterException(
                    "Could not deliver test message to specified Firehose "
                    "stream. Check if the given Firehose stream is in ACTIVE "
                    "state."
                )
        elif service == "kinesis":
            from moto.kinesis import kinesis_backends

            kinesis = kinesis_backends[self.account_id][self.region_name]
            try:
                kinesis.describe_stream(stream_arn=destination_arn, stream_name=None)
            except Exception:
                raise InvalidParameterException(
                    "Could not deliver test message to specified Kinesis stream. Verify the stream exists "
                )
        elif service == "logs":
            backend: LogsBackend = logs_backends[parsed_arn.account][parsed_arn.region]
            # {name}:* --> We only need the name
            target_group_name = parsed_arn.resource_id.split(":")[0]
            backend._find_log_group(log_group_name=target_group_name)
        else:
            # TODO: support Kinesis stream destinations
            raise InvalidParameterException(
                f"Service '{service}' has not implemented for put_subscription_filter()"
            )

        log_group.put_subscription_filter(
            filter_name, filter_pattern, destination_arn, role_arn
        )

    def delete_subscription_filter(self, log_group_name: str, filter_name: str) -> None:
        log_group = self.groups.get(log_group_name)

        if not log_group:
            raise ResourceNotFoundException()

        log_group.delete_subscription_filter(filter_name)

    def start_query(
        self,
        log_group_names: list[str],
        start_time: int,
        end_time: int,
        query_string: str,
    ) -> str:
        for log_group_name in log_group_names:
            if log_group_name not in self.groups:
                raise ResourceNotFoundException()
        log_groups = [self.groups[name] for name in log_group_names]

        query_id = str(mock_random.uuid1())
        self.queries[query_id] = LogQuery(
            query_id, start_time, end_time, query_string, log_groups
        )
        return query_id

    def describe_queries(
        self, log_stream_name: str, status: Optional[str]
    ) -> list[LogQuery]:
        """
        Pagination is not yet implemented
        """
        queries: list[LogQuery] = []
        for query in self.queries.values():
            if log_stream_name in query.log_group_names and (
                not status or status == query.status
            ):
                queries.append(query)
        return queries

    def get_query_results(self, query_id: str) -> LogQuery:
        """
        Not all query commands are implemented yet. Please raise an issue if you encounter unexpected results.
        """
        return self.queries[query_id]

    def cancel_export_task(self, task_id: str) -> None:
        task = self.export_tasks.get(task_id)
        if not task:
            raise ResourceNotFoundException("The specified export task does not exist.")
        # If the task has already finished, AWS throws an InvalidOperationException
        #     'The specified export task has already finished'
        # However, the export task is currently syncronous, meaning it finishes immediately
        # When we make the Task async, we can also implement the error behaviour
        task.status = {"code": "CANCELLED", "message": "Cancelled by user"}

    def create_export_task(
        self,
        taskName: str,
        logGroupName: str,
        destination: str,
        destinationPrefix: str,
        fromTime: int,
        to: int,
    ) -> str:
        try:
            s3_backends[self.account_id][self.partition].get_bucket(destination)
        except MissingBucket:
            raise InvalidParameterException(
                "The given bucket does not exist. Please make sure the bucket is valid."
            )
        if logGroupName not in self.groups:
            raise ResourceNotFoundException()
        task_id = str(mock_random.uuid4())
        self.export_tasks[task_id] = ExportTask(
            task_id,
            taskName,
            logGroupName,
            destination,
            destinationPrefix,
            fromTime,
            to,
        )

        s3_backends[self.account_id][self.partition].put_object(
            bucket_name=destination,
            key_name="aws-logs-write-test",
            value=b"Permission Check Successful",
        )

        if fromTime <= to:
            for stream_name in self.groups[logGroupName].streams.keys():
                logs, _, _ = self.filter_log_events(
                    log_group_name=logGroupName,
                    log_stream_names=[stream_name],
                    start_time=fromTime,
                    end_time=to,
                    limit=None,
                    next_token=None,
                    filter_pattern="",
                    interleaved=False,
                )
                raw_logs = "\n".join(
                    [
                        f"{datetime.fromtimestamp(log['timestamp'] / 1000).strftime('%Y-%m-%dT%H:%M:%S.000Z')} {log['message']}"
                        for log in logs
                    ]
                )
                folder = str(mock_random.uuid4()) + "/" + stream_name.replace("/", "-")
                key_name = f"{destinationPrefix}/{folder}/000000.gz"
                s3_backends[self.account_id][self.partition].put_object(
                    bucket_name=destination,
                    key_name=key_name,
                    value=gzip_compress(raw_logs.encode("utf-8")),
                )
            self.export_tasks[task_id].status["code"] = "COMPLETED"
            self.export_tasks[task_id].status["message"] = "Completed successfully"

        return task_id

    def describe_export_tasks(self, task_id: str) -> list[ExportTask]:
        """
        Pagination is not yet implemented
        """
        if task_id:
            if task_id not in self.export_tasks:
                raise ResourceNotFoundException()
            return [self.export_tasks[task_id]]
        else:
            return list(self.export_tasks.values())

    def list_tags_for_resource(self, resource_arn: str) -> dict[str, str]:
        return self.tagger.get_tag_dict_for_resource(resource_arn)

    def tag_resource(self, arn: str, tags: dict[str, str]) -> None:
        self.tagger.tag_resource(arn, TaggingService.convert_dict_to_tags_input(tags))

    def untag_resource(self, arn: str, tag_keys: list[str]) -> None:
        self.tagger.untag_resource_using_names(arn, tag_keys)

    def _find_log_group(
        self, log_group_id: Optional[str] = None, log_group_name: Optional[str] = None
    ) -> LogGroup:
        log_group: Optional[LogGroup] = None
        if log_group_name:
            log_group = self.groups.get(log_group_name)
        elif log_group_id:
            if not re.fullmatch(r"[\w#+=/:,.@-]*", log_group_id):
                raise InvalidParameterException(
                    msg=f"1 validation error detected: Value '{log_group_id}' at 'logGroupIdentifier' failed to satisfy constraint: Member must satisfy regular expression pattern: [\\w#+=/:,.@-]*"
                )
            for log_group in self.groups.values():
                if log_group.arn == log_group_id:
                    log_group = log_group
        else:
            raise InvalidParameterException(
                "Should provider either name or id, but not both"
            )
        if not log_group:
            raise ResourceNotFoundException()
        return log_group

    def put_delivery_destination(
        self,
        name: str,
        output_format: Optional[str],
        delivery_destination_configuration: dict[str, str],
        tags: Optional[dict[str, str]],
    ) -> DeliveryDestination:
        if output_format and output_format not in [
            "w3c",
            "raw",
            "json",
            "plain",
            "parquet",
        ]:
            msg = f"1 validation error detected: Value '{output_format}' at 'outputFormat' failed to satisfy constraint: Member must satisfy enum value set: [w3c, raw, json, plain, parquet]"
            raise ValidationException(msg)
        if name in self.delivery_destinations:
            if tags:
                raise ConflictException(
                    msg="Tags can only be provided when a resource is being created, not updated."
                )
            if (
                output_format
                and self.delivery_destinations[name].output_format != output_format
            ):
                msg = "Update to existing Delivery Destination with new Output Format is not allowed. Please create a new Delivery Destination instead."
                raise ValidationException(msg)
        delivery_destination = DeliveryDestination(
            account_id=self.account_id,
            region=self.region_name,
            name=name,
            output_format=output_format,
            delivery_destination_configuration=delivery_destination_configuration,
            tags=tags,
            policy=None,
        )
        self.delivery_destinations[name] = delivery_destination
        if tags:
            self.tag_resource(delivery_destination.arn, tags)
        return delivery_destination

    def get_delivery_destination(self, name: str) -> DeliveryDestination:
        if name not in self.delivery_destinations:
            raise ResourceNotFoundException(
                msg="Requested Delivery Destination does not exist in this account."
            )
        delivery_destination = self.delivery_destinations[name]
        return delivery_destination

    def describe_delivery_destinations(self) -> list[DeliveryDestination]:
        # Pagination not yet implemented
        delivery_destinations = list(self.delivery_destinations.values())
        return delivery_destinations

    def put_delivery_destination_policy(
        self, delivery_destination_name: str, delivery_destination_policy: str
    ) -> dict[str, str]:
        if delivery_destination_name not in self.delivery_destinations:
            raise ResourceNotFoundException(
                msg="Requested Delivery Destination does not exist in this account."
            )
        dd = self.delivery_destinations[delivery_destination_name]
        dd.policy = delivery_destination_policy
        return {"deliveryDestinationPolicy": delivery_destination_policy}

    def get_delivery_destination_policy(
        self, delivery_destination_name: str
    ) -> dict[str, Any]:
        if delivery_destination_name not in self.delivery_destinations:
            raise ResourceNotFoundException(
                msg="Requested Delivery Destination does not exist in this account."
            )
        policy = self.delivery_destinations[delivery_destination_name].policy
        return {"deliveryDestinationPolicy": policy}

    def put_delivery_source(
        self, name: str, resource_arn: str, log_type: str, tags: dict[str, str]
    ) -> DeliverySource:
        log_types = {
            "cloudfront": "ACCESS_LOGS",
            "bedrock": "APPLICATION_LOGS",
            "codewhisperer": "EVENT_LOGS",
            "mediapackage": ["EGRESS_ACCESS_LOGS", "INGRESS_ACCESS_LOGS"],
            "mediatailor": [
                "AD_DECISION_SERVER_LOGS",
                "MANIFEST_SERVICE_LOGS",
                "TRANSCODE_LOGS",
            ],
            "sso": "ERROR_LOGS",
            "qdeveloper": "EVENT_LOGS",
            "ses": "APPLICATION_LOG",
            "workmail": [
                "ACCESS_CONTROL_LOGS",
                "AUTHENTICATION_LOGS",
                "WORKMAIL_AVAILABILITY_PROVIDER_LOGS",
                "WORKMAIL_MAILBOX_ACCESS_LOGS",
                "WORKMAIL_PERSONAL_ACCESS_TOKEN_LOGS",
            ],
        }
        resource_type = resource_arn.split(":")[2]

        if resource_type not in log_types:
            raise ResourceNotFoundException(msg="Cannot access provided service.")

        if log_type not in log_types[resource_type]:
            raise ValidationException(
                msg=" This service is not allowed for this LogSource."
            )

        if name in self.delivery_sources:
            if tags:
                raise ConflictException(
                    msg="Tags can only be provided when a resource is being created, not updated."
                )
            if resource_arn not in self.delivery_sources[name].resource_arns:
                raise ConflictException(
                    msg="Update to existing Delivery Source with new ResourceId is not allowed. Please create a new Delivery Source instead."
                )
        delivery_source = DeliverySource(
            account_id=self.account_id,
            region=self.region_name,
            name=name,
            resource_arn=resource_arn,
            log_type=log_type,
            tags=tags,
        )
        self.delivery_sources[name] = delivery_source
        if tags:
            self.tag_resource(delivery_source.arn, tags)
        return delivery_source

    def describe_delivery_sources(self) -> list[DeliverySource]:
        # Pagination not yet implemented
        delivery_sources = list(self.delivery_sources.values())
        return delivery_sources

    def get_delivery_source(self, name: str) -> DeliverySource:
        if name not in self.delivery_sources:
            raise ResourceNotFoundException(
                msg="Requested Delivery Source does not exist in this account.."
            )
        delivery_source = self.delivery_sources[name]
        return delivery_source

    def create_delivery(
        self,
        delivery_source_name: str,
        delivery_destination_arn: str,
        record_fields: Optional[list[str]],
        field_delimiter: Optional[str],
        s3_delivery_configuration: Optional[dict[str, Any]],
        tags: Optional[dict[str, str]],
    ) -> Delivery:
        if delivery_source_name not in self.delivery_sources:
            raise ResourceNotFoundException(
                msg="Requested Delivery Source does not exist in this account."
            )
        if delivery_destination_arn not in [
            dd.arn for dd in self.delivery_destinations.values()
        ]:
            raise ResourceNotFoundException(
                msg="Requested Delivery Destination does not exist in this account."
            )

        for delivery in self.deliveries.values():
            if (
                delivery.delivery_source_name == delivery_source_name
                and delivery.delivery_destination_arn == delivery_destination_arn
            ):
                raise ConflictException(msg="The specified Delivery already exists")
            if delivery.delivery_source_name == delivery_source_name:
                for dd in self.delivery_destinations.values():
                    if (
                        dd.arn == delivery_destination_arn
                        and delivery.destination_type == dd.delivery_destination_type
                    ):
                        raise ConflictException(
                            msg="Delivery already exists for this Delivery Source with the same Delivery Destination Type."
                        )

        for dd in list(self.delivery_destinations.values()):
            if dd.arn == delivery_destination_arn:
                destination_type = dd.delivery_destination_type

        delivery = Delivery(
            account_id=self.account_id,
            region=self.region_name,
            delivery_source_name=delivery_source_name,
            delivery_destination_arn=delivery_destination_arn,
            destination_type=destination_type,
            record_fields=record_fields,
            field_delimiter=field_delimiter,
            s3_delivery_configuration=s3_delivery_configuration,
            tags=tags,
        )
        self.deliveries[delivery.id] = delivery
        if tags:
            self.tag_resource(delivery.arn, tags)
        return delivery

    def describe_deliveries(self) -> list[Delivery]:
        # Pagination not yet implemented
        deliveries = list(self.deliveries.values())
        return deliveries

    def get_delivery(self, id: str) -> Delivery:
        if id not in self.deliveries:
            raise ResourceNotFoundException(
                msg="Requested Delivery does not exist in this account."
            )
        delivery = self.deliveries[id]
        return delivery

    def delete_delivery(self, id: str) -> None:
        if id not in self.deliveries:
            raise ResourceNotFoundException(
                msg="Requested Delivery does not exist in this account."
            )
        self.deliveries.pop(id)
        return

    def delete_delivery_destination(self, name: str) -> None:
        if name not in self.delivery_destinations:
            raise ResourceNotFoundException(
                msg="Requested Delivery Destination does not exist in this account."
            )
        self.delivery_destinations.pop(name)
        return

    def delete_delivery_destination_policy(
        self, delivery_destination_name: str
    ) -> None:
        delivery_destination = self.delivery_destinations.get(delivery_destination_name)
        if not delivery_destination:
            raise ResourceNotFoundException(
                msg="Requested Delivery Destination does not exist in this account."
            )
        delivery_destination.policy = None
        return

    def delete_delivery_source(self, name: str) -> None:
        if name not in self.delivery_sources:
            raise ResourceNotFoundException(
                msg="Requested Delivery Source does not exist in this account."
            )
        self.delivery_sources.pop(name)
        return

    def put_query_definition(
        self,
        name: str,
        query_string: str,
        log_group_names: list[str],
        query_definition_id: Optional[str] = None,
    ) -> str:
        if query_definition_id is None:
            query_definition_id = str(mock_random.uuid4())
        self.query_definitions[query_definition_id] = {
            "queryDefinitionId": query_definition_id,
            "name": name,
            "queryString": query_string,
            "logGroupNames": log_group_names,
            "lastModified": int(unix_time_millis()),
        }
        return query_definition_id

    def delete_query_definition(
        self,
        query_definition_id: str,
    ) -> bool:
        if query_definition_id not in self.query_definitions:
            raise ResourceNotFoundException(
                msg=f"Query definition with id [{query_definition_id}] does not exist."
            )
        del self.query_definitions[query_definition_id]
        return True

    def describe_query_definitions(
        self,
        query_definition_name_prefix: Optional[str] = None,
    ) -> list[dict[str, Any]]:
        definitions = list(self.query_definitions.values())
        if query_definition_name_prefix:
            definitions = [
                d
                for d in definitions
                if d["name"].startswith(query_definition_name_prefix)
            ]
        return definitions

    def get_log_group_fields(
        self,
        log_group_name: Optional[str] = None,
    ) -> list[dict[str, Any]]:
        # Return common default fields that CloudWatch Logs always includes
        return [
            {"name": "@timestamp", "percent": 100},
            {"name": "@message", "percent": 100},
            {"name": "@logStream", "percent": 100},
        ]

    def list_log_groups(
        self,
        log_group_name_prefix: Optional[str] = None,
        log_group_name_pattern: Optional[str] = None,
        limit: int = 50,
        next_token: Optional[str] = None,
    ) -> tuple[list[dict[str, Any]], Optional[str]]:
        # Re-use existing describe_log_groups logic
        groups, new_next_token = self.describe_log_groups(
            limit=limit,
            log_group_name_prefix=log_group_name_prefix,
            next_token=next_token,
        )
        result = [g.to_describe_dict() for g in groups]
        if log_group_name_pattern:
            import re as _re

            result = [
                g for g in result if _re.search(log_group_name_pattern, g["logGroupName"])
            ]
        return result, new_next_token

    def describe_configuration_templates(self) -> list[dict[str, Any]]:
        # Configuration templates are not yet modeled; return empty list
        return []

    def describe_import_tasks(self) -> list[dict[str, Any]]:
        # Import tasks are not yet modeled; return empty list
        return []

    def put_account_policy(
        self,
        policy_name: str,
        policy_document: str,
        policy_type: str,
        scope: Optional[str],
        selection_criteria: Optional[str],
    ) -> AccountPolicy:
        valid_types = [
            "DATA_PROTECTION_POLICY",
            "SUBSCRIPTION_FILTER_POLICY",
        ]
        if policy_type not in valid_types:
            raise InvalidParameterException(
                constraint=f"Member must satisfy enum value set: {valid_types}",
                parameter="policyType",
                value=policy_type,
            )
        if policy_type not in self.account_policies:
            self.account_policies[policy_type] = {}
        policy = AccountPolicy(
            account_id=self.account_id,
            policy_name=policy_name,
            policy_document=policy_document,
            policy_type=policy_type,
            scope=scope,
            selection_criteria=selection_criteria,
        )
        self.account_policies[policy_type][policy_name] = policy
        return policy

    def describe_account_policies(
        self,
        policy_type: str,
        policy_name: Optional[str] = None,
    ) -> list[AccountPolicy]:
        valid_types = [
            "DATA_PROTECTION_POLICY",
            "SUBSCRIPTION_FILTER_POLICY",
        ]
        if policy_type not in valid_types:
            raise InvalidParameterException(
                constraint=f"Member must satisfy enum value set: {valid_types}",
                parameter="policyType",
                value=policy_type,
            )
        policies = list(self.account_policies.get(policy_type, {}).values())
        if policy_name:
            policies = [p for p in policies if p.policy_name == policy_name]
        return policies

    def delete_account_policy(
        self,
        policy_name: str,
        policy_type: str,
    ) -> None:
        valid_types = [
            "DATA_PROTECTION_POLICY",
            "SUBSCRIPTION_FILTER_POLICY",
        ]
        if policy_type not in valid_types:
            raise InvalidParameterException(
                constraint=f"Member must satisfy enum value set: {valid_types}",
                parameter="policyType",
                value=policy_type,
            )
        policies = self.account_policies.get(policy_type, {})
        if policy_name not in policies:
            raise ResourceNotFoundException(
                msg=f"Policy with name [{policy_name}] does not exist"
            )
        del policies[policy_name]

    def create_log_anomaly_detector(
        self,
        log_group_arn_list: list[str],
        detector_name: Optional[str],
        evaluation_frequency: Optional[str],
        filter_pattern: Optional[str],
        kms_key_id: Optional[str],
        anomaly_visibility_time: Optional[int],
        tags: Optional[dict[str, str]],
    ) -> str:
        if evaluation_frequency and evaluation_frequency not in [
            "ONE_MIN",
            "FIVE_MIN",
            "TEN_MIN",
            "FIFTEEN_MIN",
            "THIRTY_MIN",
            "ONE_HOUR",
        ]:
            raise InvalidParameterException(
                constraint="Member must satisfy enum value set: [ONE_MIN, FIVE_MIN, TEN_MIN, FIFTEEN_MIN, THIRTY_MIN, ONE_HOUR]",
                parameter="evaluationFrequency",
                value=evaluation_frequency,
            )
        detector = LogAnomalyDetector(
            account_id=self.account_id,
            region=self.region_name,
            detector_name=detector_name or "",
            log_group_arn_list=log_group_arn_list,
            evaluation_frequency=evaluation_frequency,
            filter_pattern=filter_pattern,
            kms_key_id=kms_key_id,
            anomaly_visibility_time=anomaly_visibility_time,
            tags=tags,
        )
        self.anomaly_detectors[detector.anomaly_detector_arn] = detector
        if tags:
            self.tag_resource(detector.anomaly_detector_arn, tags)
        return detector.anomaly_detector_arn

    def get_log_anomaly_detector(self, anomaly_detector_arn: str) -> LogAnomalyDetector:
        if anomaly_detector_arn not in self.anomaly_detectors:
            raise ResourceNotFoundException(
                msg="The specified anomaly detector does not exist."
            )
        return self.anomaly_detectors[anomaly_detector_arn]

    def update_log_anomaly_detector(
        self,
        anomaly_detector_arn: str,
        evaluation_frequency: Optional[str],
        filter_pattern: Optional[str],
        anomaly_visibility_time: Optional[int],
        enabled: bool,
    ) -> None:
        if anomaly_detector_arn not in self.anomaly_detectors:
            raise ResourceNotFoundException(
                msg="The specified anomaly detector does not exist."
            )
        detector = self.anomaly_detectors[anomaly_detector_arn]
        if evaluation_frequency is not None:
            detector.evaluation_frequency = evaluation_frequency
        if filter_pattern is not None:
            detector.filter_pattern = filter_pattern
        if anomaly_visibility_time is not None:
            detector.anomaly_visibility_time = anomaly_visibility_time
        if enabled:
            detector.anomaly_detector_status = "TRAINING"
        else:
            detector.anomaly_detector_status = "PAUSED"
        detector.last_modified_time_stamp = int(unix_time_millis())

    def delete_log_anomaly_detector(self, anomaly_detector_arn: str) -> None:
        if anomaly_detector_arn not in self.anomaly_detectors:
            raise ResourceNotFoundException(
                msg="The specified anomaly detector does not exist."
            )
        del self.anomaly_detectors[anomaly_detector_arn]

    def list_anomalies(
        self,
        anomaly_detector_arn: Optional[str] = None,
    ) -> list[dict[str, Any]]:
        # Anomalies are not yet modeled; return empty list
        return []

    def list_log_anomaly_detectors(
        self,
        filter_log_group_arn: Optional[str] = None,
    ) -> list[dict[str, Any]]:
        detectors = list(self.anomaly_detectors.values())
        if filter_log_group_arn:
            detectors = [
                d
                for d in detectors
                if filter_log_group_arn in d.log_group_arn_list
            ]
        return [d.to_dict() for d in detectors]

    def put_index_policy(
        self,
        log_group_identifier: str,
        policy_document: str,
    ) -> IndexPolicy:
        # log_group_identifier can be a name or ARN
        log_group = None
        for group in self.groups.values():
            if group.name == log_group_identifier or group.arn == log_group_identifier:
                log_group = group
                break
        if not log_group:
            raise ResourceNotFoundException()
        policy = IndexPolicy(
            account_id=self.account_id,
            log_group_identifier=log_group.arn,
            policy_document=policy_document,
            log_group_name=log_group.name,
        )
        self.index_policies[log_group.name] = policy
        return policy

    def describe_index_policies(
        self,
        log_group_identifiers: list[str],
    ) -> list[IndexPolicy]:
        results = []
        for identifier in log_group_identifiers:
            # Identifier can be name or ARN
            for name, policy in self.index_policies.items():
                if (
                    name == identifier
                    or policy.log_group_identifier == identifier
                ):
                    results.append(policy)
        return results

    def delete_index_policy(
        self,
        log_group_identifier: str,
    ) -> None:
        # Find the log group by name or ARN
        log_group = None
        for group in self.groups.values():
            if group.name == log_group_identifier or group.arn == log_group_identifier:
                log_group = group
                break
        if not log_group:
            raise ResourceNotFoundException()
        if log_group.name not in self.index_policies:
            raise ResourceNotFoundException(
                msg="No index policy found for the specified log group."
            )
        del self.index_policies[log_group.name]

    def list_integrations(
        self,
        integration_name_prefix: Optional[str] = None,
        integration_type: Optional[str] = None,
    ) -> list[dict[str, Any]]:
        # Integrations are not yet modeled; return empty list
        return []

    def delete_integration(
        self,
        integration_name: str,
    ) -> None:
        # Integrations are not yet fully modeled, but we validate the name
        raise ResourceNotFoundException(
            msg=f"Integration with name [{integration_name}] does not exist."
        )

    def list_scheduled_queries(self) -> list[dict[str, Any]]:
        return [sq.to_dict() for sq in self.scheduled_queries.values()]

    def create_scheduled_query(
        self,
        name: str,
        query_string: str,
        log_group_names: list[str],
        schedule_expression: str,
        target_configuration: Optional[dict[str, Any]] = None,
        query_language: str = "CWLI",
    ) -> ScheduledQuery:
        # Check for duplicate name
        for sq in self.scheduled_queries.values():
            if sq.name == name:
                raise ConflictException(
                    f"A scheduled query with name [{name}] already exists."
                )
        sq = ScheduledQuery(
            account_id=self.account_id,
            region=self.region_name,
            name=name,
            query_string=query_string,
            log_group_names=log_group_names,
            schedule_expression=schedule_expression,
            target_configuration=target_configuration,
            query_language=query_language,
        )
        self.scheduled_queries[sq.arn] = sq
        return sq

    def get_scheduled_query(self, arn: str) -> ScheduledQuery:
        sq = self.scheduled_queries.get(arn)
        if not sq:
            raise ResourceNotFoundException(
                msg=f"Scheduled query [{arn}] does not exist."
            )
        return sq

    def update_scheduled_query(
        self,
        arn: str,
        query_string: Optional[str] = None,
        schedule_expression: Optional[str] = None,
        log_group_names: Optional[list[str]] = None,
        target_configuration: Optional[dict[str, Any]] = None,
        enabled: Optional[bool] = None,
    ) -> ScheduledQuery:
        sq = self.get_scheduled_query(arn)
        if query_string is not None:
            sq.query_string = query_string
        if schedule_expression is not None:
            sq.schedule_expression = schedule_expression
        if log_group_names is not None:
            sq.log_group_names = log_group_names
        if target_configuration is not None:
            sq.target_configuration = target_configuration
        if enabled is not None:
            sq.status = "ACTIVE" if enabled else "DISABLED"
        sq.last_modified_time = int(unix_time_millis())
        return sq

    def delete_scheduled_query(self, arn: str) -> None:
        if arn not in self.scheduled_queries:
            raise ResourceNotFoundException(
                msg=f"Scheduled query [{arn}] does not exist."
            )
        del self.scheduled_queries[arn]

    def get_scheduled_query_history(
        self,
        arn: str,
    ) -> list[dict[str, Any]]:
        # Validate the scheduled query exists
        self.get_scheduled_query(arn)
        # No actual runs in the emulator, return empty history
        return []

    def put_log_group_deletion_protection(
        self,
        log_group_name: str,
        deletion_protection_enabled: bool,
    ) -> None:
        log_group = self._find_log_group(log_group_name=log_group_name)
        log_group.deletion_protection = deletion_protection_enabled

    def update_anomaly(
        self,
        anomaly_id: Optional[str] = None,
        pattern_id: Optional[str] = None,
        anomaly_detector_arn: Optional[str] = None,
        suppression: Optional[dict[str, Any]] = None,
        baseline: Optional[bool] = None,
    ) -> None:
        # Validate anomaly detector exists if provided
        if anomaly_detector_arn:
            if anomaly_detector_arn not in self.anomaly_detectors:
                raise ResourceNotFoundException(
                    msg=f"Anomaly detector [{anomaly_detector_arn}] does not exist."
                )
        # Stub: accept params and return success (anomalies are not modeled)

    def update_delivery_configuration(
        self,
        delivery_id: str,
        record_fields: Optional[list[str]] = None,
        field_delimiter: Optional[str] = None,
        s3_delivery_configuration: Optional[dict[str, Any]] = None,
    ) -> None:
        delivery = self.get_delivery(id=delivery_id)
        if record_fields is not None:
            delivery.record_fields = record_fields
        if field_delimiter is not None:
            delivery.field_delimiter = field_delimiter
        if s3_delivery_configuration is not None:
            delivery.s3_delivery_configuration = s3_delivery_configuration

    def list_aggregate_log_group_summaries(
        self,
        log_group_name_pattern: Optional[str] = None,
        group_by: Optional[str] = None,
        limit: int = 50,
        next_token: Optional[str] = None,
    ) -> tuple[list[dict[str, Any]], Optional[str]]:
        groups, new_next_token = self.describe_log_groups(
            limit=limit,
            next_token=next_token,
        )
        summaries = []
        for group in groups:
            if log_group_name_pattern:
                import re as _re

                if not _re.search(log_group_name_pattern, group.name):
                    continue
            summary: dict[str, Any] = {
                "logGroupName": group.name,
                "logGroupArn": group.arn,
                "creationTime": group.creation_time,
                "storedBytes": 0,
                "logStreamCount": len(group.streams),
            }
            if group.retention_in_days:
                summary["retentionInDays"] = group.retention_in_days
            summaries.append(summary)
        return summaries, new_next_token

    def put_bearer_token_authentication(
        self,
        log_group_identifier: str,
        enabled: bool,
    ) -> None:
        # Verify log group exists
        self._find_log_group(log_group_name=log_group_identifier)

    def _find_log_group(
        self,
        log_group_id: Optional[str] = None,
        log_group_name: Optional[str] = None,
    ) -> "LogGroup":
        """Find a log group by name or ARN."""
        identifier = log_group_name or log_group_id
        if identifier:
            for group in self.groups.values():
                if group.name == identifier or group.arn == identifier:
                    return group
        raise ResourceNotFoundException()

    def put_data_protection_policy(
        self,
        log_group_identifier: str,
        policy_document: str,
    ) -> dict[str, Any]:
        log_group = self._find_log_group(log_group_name=log_group_identifier)
        log_group.data_protection_policy = {
            "logGroupIdentifier": log_group.name,
            "policyDocument": policy_document,
            "lastUpdatedTime": int(unix_time_millis()),
        }
        return log_group.data_protection_policy

    def delete_data_protection_policy(
        self,
        log_group_identifier: str,
    ) -> None:
        log_group = self._find_log_group(log_group_name=log_group_identifier)
        if log_group.data_protection_policy is None:
            raise ResourceNotFoundException(
                msg="The specified data protection policy does not exist."
            )
        log_group.data_protection_policy = None

    def get_data_protection_policy(
        self,
        log_group_identifier: Optional[str] = None,
    ) -> dict[str, Any]:
        if not log_group_identifier:
            return {}
        log_group = self._find_log_group(log_group_name=log_group_identifier)
        if log_group.data_protection_policy is None:
            return {}
        return log_group.data_protection_policy

    def get_log_record(
        self,
        log_record_pointer: str,
    ) -> dict[str, str]:
        # logRecordPointer is an opaque string. In AWS it encodes the log group,
        # stream and event offset. We scan all events looking for a match.
        # The pointer format used by get_log_events/filter_log_events isn't
        # formally specified; we use eventId as a rough equivalent.
        for group in self.groups.values():
            for stream in group.streams.values():
                for event in stream.events:
                    if str(event.event_id) == log_record_pointer:
                        return {
                            "@message": event.message,
                            "@timestamp": str(event.timestamp),
                            "@logStream": stream.log_stream_name,
                            "@logGroup": group.name,
                            "@ingestionTime": str(event.ingestion_time),
                        }
        raise ResourceNotFoundException(
            msg="The specified log record does not exist."
        )

    def put_transformer(
        self,
        log_group_identifier: str,
        transformer_config: list[dict[str, Any]],
    ) -> None:
        log_group = self._find_log_group(log_group_name=log_group_identifier)
        now = int(unix_time_millis())
        creation_time = now
        if log_group.transformer is not None:
            creation_time = log_group.transformer.get("creationTime", now)
        log_group.transformer = {
            "logGroupIdentifier": log_group.name,
            "transformerConfig": transformer_config,
            "creationTime": creation_time,
            "lastModifiedTime": now,
        }

    def delete_transformer(
        self,
        log_group_identifier: str,
    ) -> None:
        log_group = self._find_log_group(log_group_name=log_group_identifier)
        if log_group.transformer is None:
            raise ResourceNotFoundException(
                msg="No transformer found for the specified log group."
            )
        log_group.transformer = None

    def get_transformer(
        self,
        log_group_identifier: Optional[str] = None,
    ) -> dict[str, Any]:
        if not log_group_identifier:
            raise ResourceNotFoundException(
                msg="No transformer found for the specified log group."
            )
        log_group = self._find_log_group(log_group_name=log_group_identifier)
        if log_group.transformer is None:
            raise ResourceNotFoundException(
                msg="No transformer found for the specified log group."
            )
        return log_group.transformer

    def list_transformers(
        self,
        log_group_name_prefix: Optional[str] = None,
    ) -> list[dict[str, Any]]:
        results = []
        for group in self.groups.values():
            if log_group_name_prefix and not group.name.startswith(log_group_name_prefix):
                continue
            if group.transformer is not None:
                results.append(group.transformer)
        return results

    def get_integration(
        self,
        integration_name: Optional[str] = None,
    ) -> dict[str, Any]:
        # Integrations are not yet modeled
        raise ResourceNotFoundException(
            msg=f"Integration with name [{integration_name}] does not exist."
        )

    def get_log_fields(
        self,
        log_group_name: Optional[str] = None,
        log_group_identifier: Optional[str] = None,
    ) -> list[dict[str, Any]]:
        identifier = log_group_name or log_group_identifier
        if identifier:
            found = False
            for group in self.groups.values():
                if group.name == identifier or group.arn == identifier:
                    found = True
                    break
            if not found:
                raise ResourceNotFoundException()
        # Return common fields that CloudWatch Logs always includes
        return [
            {"name": "@timestamp", "percent": 100},
            {"name": "@message", "percent": 100},
            {"name": "@logStream", "percent": 100},
        ]

    def describe_field_indexes(
        self,
        log_group_identifiers: Optional[list[str]] = None,
    ) -> list[dict[str, Any]]:
        # Field indexes are not yet modeled; return empty list
        return []

    def describe_import_task_batches(
        self,
        import_task_identifier: Optional[str] = None,
    ) -> list[dict[str, Any]]:
        # Import task batches are not yet modeled; return empty list
        return []

    def test_metric_filter(
        self,
        filter_pattern: str,
        log_event_messages: list[str],
    ) -> list[dict[str, Any]]:
        """Test a metric filter pattern against sample log event messages.

        Supports simple term matching: a bare term like "ERROR" matches any
        message containing that term (case-sensitive substring match).
        JSON-structured patterns ({$.key = "value"}) are not yet implemented
        and return no matches.
        """
        import re

        matches = []
        # Skip JSON/structured patterns (start with '{')
        if filter_pattern.strip().startswith("{"):
            return []

        # Simple space-delimited terms: each term must appear in the message
        terms = filter_pattern.split()
        for i, message in enumerate(log_event_messages):
            if all(term in message for term in terms):
                matches.append(
                    {
                        "eventNumber": i + 1,
                        "eventMessage": message,
                        "extractedValues": {},
                    }
                )
        return matches

    def cancel_import_task(
        self,
        import_id: str,
    ) -> dict[str, Any]:
        # Stub: import tasks not yet modeled; return minimal response
        return {"importId": import_id, "importStatus": "CANCELLED"}

    def create_import_task(
        self,
        import_source_arn: str,
        import_role_arn: str,
        import_filter: Optional[dict[str, Any]] = None,
        import_destination_arn: Optional[str] = None,
    ) -> dict[str, Any]:
        # Stub: import tasks not yet modeled; return minimal response
        import uuid

        return {
            "importId": str(uuid.uuid4()),
            "importDestinationArn": import_destination_arn or "",
            "creationTime": 0,
        }

    def list_log_groups_for_query(
        self,
        query_id: Optional[str] = None,
    ) -> list[str]:
        if query_id and query_id in self.queries:
            return self.queries[query_id].log_group_names
        if query_id:
            raise ResourceNotFoundException(
                msg=f"Query with id [{query_id}] does not exist."
            )
        return []


logs_backends = BackendDict(LogsBackend, "logs")
