import bisect
import datetime
import json
import time
import uuid
from collections import defaultdict
from typing import Any, Optional

from moto.core.base_backend import BackendDict, BaseBackend
from moto.core.common_models import BaseModel
from moto.core.exceptions import AWSError

from .exceptions import BadSegmentException


class TelemetryRecords(BaseModel):
    def __init__(
        self,
        instance_id: str,
        hostname: str,
        resource_arn: str,
        records: list[dict[str, Any]],
    ):
        self.instance_id = instance_id
        self.hostname = hostname
        self.resource_arn = resource_arn
        self.records = records

    @classmethod
    def from_json(cls, src: dict[str, Any]) -> "TelemetryRecords":  # type: ignore[misc]
        instance_id = src.get("EC2InstanceId", None)
        hostname = src.get("Hostname")
        resource_arn = src.get("ResourceARN")
        telemetry_records = src["TelemetryRecords"]

        return cls(instance_id, hostname, resource_arn, telemetry_records)  # type: ignore


# https://docs.aws.amazon.com/xray/latest/devguide/xray-api-segmentdocuments.html
class TraceSegment(BaseModel):
    def __init__(
        self,
        name: str,
        segment_id: str,
        trace_id: str,
        start_time: float,
        raw: Any,
        end_time: Optional[float] = None,
        in_progress: bool = False,
        service: Any = None,
        user: Any = None,
        origin: Any = None,
        parent_id: Any = None,
        http: Any = None,
        aws: Any = None,
        metadata: Any = None,
        annotations: Any = None,
        subsegments: Any = None,
        **kwargs: Any,
    ):
        self.name = name
        self.id = segment_id
        self.trace_id = trace_id
        self._trace_version: Optional[int] = None
        self._original_request_start_time: Optional[datetime.datetime] = None
        self._trace_identifier = None
        self.start_time = start_time
        self._start_date: Optional[datetime.datetime] = None
        self.end_time = end_time
        self._end_date: Optional[datetime.datetime] = None
        self.in_progress = in_progress
        self.service = service
        self.user = user
        self.origin = origin
        self.parent_id = parent_id
        self.http = http
        self.aws = aws
        self.metadata = metadata
        self.annotations = annotations
        self.subsegments = subsegments
        self.misc = kwargs

        # Raw json string
        self.raw = raw

    def __lt__(self, other: Any) -> bool:
        return self.start_date < other.start_date

    @property
    def trace_version(self) -> int:
        if self._trace_version is None:
            self._trace_version = int(self.trace_id.split("-", 1)[0])
        return self._trace_version

    @property
    def request_start_date(self) -> datetime.datetime:
        if self._original_request_start_time is None:
            start_time = int(self.trace_id.split("-")[1], 16)
            self._original_request_start_time = datetime.datetime.fromtimestamp(
                start_time
            )
        return self._original_request_start_time

    @property
    def start_date(self) -> datetime.datetime:
        if self._start_date is None:
            self._start_date = datetime.datetime.fromtimestamp(self.start_time)
        return self._start_date

    @property
    def end_date(self) -> datetime.datetime:
        if self._end_date is None:
            self._end_date = datetime.datetime.fromtimestamp(self.end_time)  # type: ignore
        return self._end_date

    @classmethod
    def from_dict(cls, data: dict[str, Any], raw: Any) -> "TraceSegment":  # type: ignore[misc]
        # Check manditory args
        if "id" not in data:
            raise BadSegmentException(code="MissingParam", message="Missing segment ID")
        seg_id = data["id"]
        data["segment_id"] = seg_id  # Just adding this key for future convenience

        for arg in ("name", "trace_id", "start_time"):
            if arg not in data:
                raise BadSegmentException(
                    seg_id=seg_id, code="MissingParam", message="Missing segment ID"
                )

        if "end_time" not in data and "in_progress" not in data:
            raise BadSegmentException(
                seg_id=seg_id,
                code="MissingParam",
                message="Missing end_time or in_progress",
            )
        if "end_time" not in data and data["in_progress"] == "false":
            raise BadSegmentException(
                seg_id=seg_id, code="MissingParam", message="Missing end_time"
            )

        return cls(raw=raw, **data)


class SegmentCollection:
    def __init__(self) -> None:
        self._traces: dict[str, dict[str, Any]] = defaultdict(self._new_trace_item)

    @staticmethod
    def _new_trace_item() -> dict[str, Any]:  # type: ignore[misc]
        return {
            "start_date": datetime.datetime(1970, 1, 1),
            "end_date": datetime.datetime(1970, 1, 1),
            "finished": False,
            "trace_id": None,
            "segments": [],
        }

    def put_segment(self, segment: Any) -> None:
        # insert into a sorted list
        bisect.insort_left(self._traces[segment.trace_id]["segments"], segment)

        # Get the last segment (takes into account incorrect ordering)
        # and if its the last one, mark trace as complete
        if self._traces[segment.trace_id]["segments"][-1].end_time is not None:
            self._traces[segment.trace_id]["finished"] = True

            start_time = self._traces[segment.trace_id]["segments"][0].start_date
            end_time = self._traces[segment.trace_id]["segments"][-1].end_date
            self._traces[segment.trace_id]["start_date"] = start_time
            self._traces[segment.trace_id]["end_date"] = end_time
            self._traces[segment.trace_id]["trace_id"] = segment.trace_id
            # Todo consolidate trace segments into a trace.
            # not enough working knowledge of xray to do this

    def summary(
        self, start_time: str, end_time: str, filter_expression: Any = None
    ) -> dict[str, Any]:
        # This beast https://docs.aws.amazon.com/xray/latest/api/API_GetTraceSummaries.html#API_GetTraceSummaries_ResponseSyntax
        if filter_expression is not None:
            raise AWSError(
                "Not implemented yet - moto",
                exception_type="InternalFailure",
                status=500,
            )

        summaries = []

        for tid, trace in self._traces.items():
            if (
                trace["finished"]
                and start_time < trace["start_date"]
                and trace["end_date"] < end_time
            ):
                duration = int(
                    (trace["end_date"] - trace["start_date"]).total_seconds()
                )
                # this stuff is mostly guesses, refer to TODO above
                has_error = any("error" in seg.misc for seg in trace["segments"])
                has_fault = any("fault" in seg.misc for seg in trace["segments"])
                has_throttle = any("throttle" in seg.misc for seg in trace["segments"])

                # Apparently all of these options are optional
                summary_part = {
                    "Annotations": {},  # Not implemented yet
                    "Duration": duration,
                    "HasError": has_error,
                    "HasFault": has_fault,
                    "HasThrottle": has_throttle,
                    "Http": {},  # Not implemented yet
                    "Id": tid,
                    "IsParital": False,  # needs lots more work to work on partials
                    "ResponseTime": 1,  # definitely 1ms resposnetime
                    "ServiceIds": [],  # Not implemented yet
                    "Users": {},  # Not implemented yet
                }
                summaries.append(summary_part)

        result = {
            "ApproximateTime": int(
                (
                    datetime.datetime.now() - datetime.datetime(1970, 1, 1)
                ).total_seconds()
            ),
            "TracesProcessedCount": len(summaries),
            "TraceSummaries": summaries,
        }

        return result

    def get_trace_ids(
        self, trace_ids: list[str]
    ) -> tuple[list[dict[str, Any]], list[str]]:
        traces = []
        unprocessed = []

        # Its a default dict
        existing_trace_ids = list(self._traces.keys())
        for trace_id in trace_ids:
            if trace_id in existing_trace_ids:
                traces.append(self._traces[trace_id])
            else:
                unprocessed.append(trace_id)

        return traces, unprocessed


class ResourcePolicy(BaseModel):
    def __init__(self, policy_name: str, policy_document: str):
        self.policy_name = policy_name
        self.policy_document = policy_document
        self.policy_revision_id = str(uuid.uuid4())
        self.last_updated_time = time.time()

    def update(self, policy_document: str) -> None:
        self.policy_document = policy_document
        self.policy_revision_id = str(uuid.uuid4())
        self.last_updated_time = time.time()

    def to_dict(self) -> dict[str, Any]:
        return {
            "PolicyName": self.policy_name,
            "PolicyDocument": self.policy_document,
            "PolicyRevisionId": self.policy_revision_id,
            "LastUpdatedTime": self.last_updated_time,
        }


class XRayBackend(BaseBackend):
    def __init__(self, region_name: str, account_id: str):
        super().__init__(region_name, account_id)
        self._telemetry_records: list[TelemetryRecords] = []
        self._segment_collection = SegmentCollection()
        self._resource_policies: dict[str, ResourcePolicy] = {}
        self._tags: dict[str, dict[str, str]] = {}  # ARN -> {key: value}
        self._trace_retrievals: dict[str, dict[str, Any]] = {}  # token -> retrieval info

    def add_telemetry_records(self, src: Any) -> None:
        self._telemetry_records.append(TelemetryRecords.from_json(src))

    def process_segment(self, doc: Any) -> None:
        try:
            data = json.loads(doc)
        except ValueError:
            raise BadSegmentException(code="JSONFormatError", message="Bad JSON data")

        try:
            # Get Segment Object
            segment = TraceSegment.from_dict(data, raw=doc)
        except ValueError:
            raise BadSegmentException(code="JSONFormatError", message="Bad JSON data")

        try:
            # Store Segment Object
            self._segment_collection.put_segment(segment)
        except Exception as err:
            raise BadSegmentException(
                seg_id=segment.id, code="InternalFailure", message=str(err)
            )

    def get_trace_summary(
        self, start_time: str, end_time: str, filter_expression: Any
    ) -> dict[str, Any]:
        return self._segment_collection.summary(start_time, end_time, filter_expression)

    def get_trace_ids(self, trace_ids: list[str]) -> dict[str, Any]:
        traces, unprocessed_ids = self._segment_collection.get_trace_ids(trace_ids)

        result: dict[str, Any] = {"Traces": [], "UnprocessedTraceIds": unprocessed_ids}

        for trace in traces:
            segments = []
            for segment in trace["segments"]:
                segments.append({"Id": segment.id, "Document": segment.raw})

            result["Traces"].append(
                {
                    "Duration": int(
                        (trace["end_date"] - trace["start_date"]).total_seconds()
                    ),
                    "Id": trace["trace_id"],
                    "Segments": segments,
                }
            )

        return result

    # Resource Policy operations

    def put_resource_policy(
        self,
        policy_name: str,
        policy_document: str,
        policy_revision_id: Optional[str] = None,
    ) -> dict[str, Any]:
        existing = self._resource_policies.get(policy_name)
        if policy_revision_id == "0" and existing is not None:
            raise AWSError(
                "The provided policy revision id does not match.",
                exception_type="InvalidPolicyRevisionIdException",
                status=400,
            )
        if (
            policy_revision_id
            and policy_revision_id != "0"
            and existing is not None
            and existing.policy_revision_id != policy_revision_id
        ):
            raise AWSError(
                "The provided policy revision id does not match.",
                exception_type="InvalidPolicyRevisionIdException",
                status=400,
            )
        if existing is not None:
            existing.update(policy_document)
        else:
            existing = ResourcePolicy(policy_name, policy_document)
            self._resource_policies[policy_name] = existing
        return existing.to_dict()

    def list_resource_policies(self) -> list[dict[str, Any]]:
        return [p.to_dict() for p in self._resource_policies.values()]

    def delete_resource_policy(
        self, policy_name: str, policy_revision_id: Optional[str] = None
    ) -> None:
        existing = self._resource_policies.get(policy_name)
        if existing is None:
            return  # AWS is idempotent on delete
        if (
            policy_revision_id
            and existing.policy_revision_id != policy_revision_id
        ):
            raise AWSError(
                "The provided policy revision id does not match.",
                exception_type="InvalidPolicyRevisionIdException",
                status=400,
            )
        del self._resource_policies[policy_name]

    # Tag operations

    def tag_resource(self, resource_arn: str, tags: list[dict[str, str]]) -> None:
        if resource_arn not in self._tags:
            self._tags[resource_arn] = {}
        for tag in tags:
            self._tags[resource_arn][tag["Key"]] = tag.get("Value", "")

    def untag_resource(self, resource_arn: str, tag_keys: list[str]) -> None:
        if resource_arn not in self._tags:
            return
        for key in tag_keys:
            self._tags[resource_arn].pop(key, None)

    def list_tags_for_resource(self, resource_arn: str) -> list[dict[str, str]]:
        tags = self._tags.get(resource_arn, {})
        return [{"Key": k, "Value": v} for k, v in tags.items()]

    # Sampling targets

    def get_sampling_targets(
        self, sampling_statistics_documents: list[dict[str, Any]]
    ) -> dict[str, Any]:
        return {
            "SamplingTargetDocuments": [],
            "LastRuleModification": time.time(),
            "UnprocessedStatistics": [],
        }

    # Insight operations (stub - return empty results)

    def get_insight_summaries(self) -> dict[str, Any]:
        return {"InsightSummaries": []}

    def get_insight(self, insight_id: str) -> dict[str, Any]:
        raise AWSError(
            f"Insight {insight_id} not found.",
            exception_type="InvalidRequestException",
            status=400,
        )

    def get_insight_events(self, insight_id: str) -> dict[str, Any]:
        raise AWSError(
            f"Insight {insight_id} not found.",
            exception_type="InvalidRequestException",
            status=400,
        )

    def get_insight_impact_graph(
        self, insight_id: str, start_time: Any, end_time: Any
    ) -> dict[str, Any]:
        raise AWSError(
            f"Insight {insight_id} not found.",
            exception_type="InvalidRequestException",
            status=400,
        )

    # Time series statistics (stub)

    def get_time_series_service_statistics(self) -> dict[str, Any]:
        return {
            "TimeSeriesServiceStatistics": [],
            "ContainsOldGroupVersions": False,
        }

    # Indexing rules (stub)

    def get_indexing_rules(self) -> dict[str, Any]:
        return {"IndexingRules": []}

    # Trace retrieval operations

    def start_trace_retrieval(
        self, trace_ids: list[str], start_time: Any, end_time: Any
    ) -> str:
        token = str(uuid.uuid4())
        self._trace_retrievals[token] = {
            "trace_ids": trace_ids,
            "start_time": start_time,
            "end_time": end_time,
            "status": "COMPLETE",
        }
        return token

    def cancel_trace_retrieval(self, retrieval_token: str) -> None:
        if retrieval_token in self._trace_retrievals:
            self._trace_retrievals[retrieval_token]["status"] = "CANCELLED"

    def get_retrieved_traces_graph(self, retrieval_token: str) -> dict[str, Any]:
        status = "COMPLETE"
        if retrieval_token in self._trace_retrievals:
            status = self._trace_retrievals[retrieval_token]["status"]
        return {
            "RetrievalStatus": status,
            "Services": [],
        }

    def list_retrieved_traces(
        self, retrieval_token: str, trace_format: Optional[str] = None
    ) -> dict[str, Any]:
        status = "COMPLETE"
        if retrieval_token in self._trace_retrievals:
            status = self._trace_retrievals[retrieval_token]["status"]
        return {
            "RetrievalStatus": status,
            "TraceFormat": trace_format or "XRAY",
            "Traces": [],
        }


xray_backends = BackendDict(XRayBackend, "xray")
