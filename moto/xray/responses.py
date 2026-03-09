import datetime
import json
from typing import Any, Union
from urllib.parse import urlsplit

from moto.core.exceptions import AWSError
from moto.core.responses import BaseResponse

from .exceptions import BadSegmentException
from .models import XRayBackend, xray_backends


class XRayResponse(BaseResponse):
    def __init__(self) -> None:
        super().__init__(service_name="xray")

    def _error(self, code: str, message: str) -> tuple[str, dict[str, int]]:
        return json.dumps({"__type": code, "message": message}), {"status": 400}

    @property
    def xray_backend(self) -> XRayBackend:
        return xray_backends[self.current_account][self.region]

    @property
    def request_params(self) -> Any:  # type: ignore[misc]
        try:
            return json.loads(self.body)
        except ValueError:
            return {}

    def _get_param(self, param_name: str, if_none: Any = None) -> Any:
        return self.request_params.get(param_name, if_none)

    def _get_action(self) -> str:
        # Amazon is just calling urls like /TelemetryRecords etc...
        # This uses the value after / as the camalcase action, which then
        # gets converted in call_action to find the following methods
        return urlsplit(self.uri).path.lstrip("/")

    # PutTelemetryRecords
    def telemetry_records(self) -> str:
        self.xray_backend.add_telemetry_records(self.request_params)

        return ""

    # PutTraceSegments
    def trace_segments(self) -> Union[str, tuple[str, dict[str, int]]]:
        docs = self._get_param("TraceSegmentDocuments")

        if docs is None:
            msg = "Parameter TraceSegmentDocuments is missing"
            return (
                json.dumps({"__type": "MissingParameter", "message": msg}),
                {"status": 400},
            )

        # Raises an exception that contains info about a bad segment,
        # the object also has a to_dict() method
        bad_segments = []
        for doc in docs:
            try:
                self.xray_backend.process_segment(doc)
            except BadSegmentException as bad_seg:
                bad_segments.append(bad_seg)
            except Exception as err:
                return (
                    json.dumps({"__type": "InternalFailure", "message": str(err)}),
                    {"status": 500},
                )

        result = {"UnprocessedTraceSegments": [x.to_dict() for x in bad_segments]}
        return json.dumps(result)

    # GetTraceSummaries
    def trace_summaries(self) -> Union[str, tuple[str, dict[str, int]]]:
        start_time = self._get_param("StartTime")
        end_time = self._get_param("EndTime")
        if start_time is None:
            msg = "Parameter StartTime is missing"
            return (
                json.dumps({"__type": "MissingParameter", "message": msg}),
                {"status": 400},
            )
        if end_time is None:
            msg = "Parameter EndTime is missing"
            return (
                json.dumps({"__type": "MissingParameter", "message": msg}),
                {"status": 400},
            )

        filter_expression = self._get_param("FilterExpression")

        try:
            start_time = datetime.datetime.fromtimestamp(int(start_time))
            end_time = datetime.datetime.fromtimestamp(int(end_time))
        except ValueError:
            msg = "start_time and end_time are not integers"
            return (
                json.dumps({"__type": "InvalidParameterValue", "message": msg}),
                {"status": 400},
            )
        except Exception as err:
            return (
                json.dumps({"__type": "InternalFailure", "message": str(err)}),
                {"status": 500},
            )

        try:
            result = self.xray_backend.get_trace_summary(
                start_time,  # type: ignore[arg-type]
                end_time,  # type: ignore[arg-type]
                filter_expression,
            )
        except AWSError as err:
            raise err
        except Exception as err:
            return (
                json.dumps({"__type": "InternalFailure", "message": str(err)}),
                {"status": 500},
            )

        return json.dumps(result)

    # BatchGetTraces
    def traces(self) -> Union[str, tuple[str, dict[str, int]]]:
        trace_ids = self._get_param("TraceIds")

        if trace_ids is None:
            msg = "Parameter TraceIds is missing"
            return (
                json.dumps({"__type": "MissingParameter", "message": msg}),
                {"status": 400},
            )

        try:
            result = self.xray_backend.get_trace_ids(trace_ids)
        except AWSError as err:
            raise err
        except Exception as err:
            return (
                json.dumps({"__type": "InternalFailure", "message": str(err)}),
                {"status": 500},
            )

        return json.dumps(result)

    # GetServiceGraph - just a dummy response for now
    def service_graph(self) -> Union[str, tuple[str, dict[str, int]]]:
        start_time = self._get_param("StartTime")
        end_time = self._get_param("EndTime")
        # next_token = self._get_param('NextToken')  # not implemented yet

        if start_time is None:
            msg = "Parameter StartTime is missing"
            return (
                json.dumps({"__type": "MissingParameter", "message": msg}),
                {"status": 400},
            )
        if end_time is None:
            msg = "Parameter EndTime is missing"
            return (
                json.dumps({"__type": "MissingParameter", "message": msg}),
                {"status": 400},
            )

        result = {"StartTime": start_time, "EndTime": end_time, "Services": []}
        return json.dumps(result)

    # GetTraceGraph - just a dummy response for now
    def trace_graph(self) -> Union[str, tuple[str, dict[str, int]]]:
        trace_ids = self._get_param("TraceIds")
        # next_token = self._get_param('NextToken')  # not implemented yet

        if trace_ids is None:
            msg = "Parameter TraceIds is missing"
            return (
                json.dumps({"__type": "MissingParameter", "message": msg}),
                {"status": 400},
            )

        result: dict[str, Any] = {"Services": []}
        return json.dumps(result)

    # PutResourcePolicy
    def put_resource_policy(self) -> Union[str, tuple[str, dict[str, int]]]:
        policy_name = self._get_param("PolicyName")
        policy_document = self._get_param("PolicyDocument")
        policy_revision_id = self._get_param("PolicyRevisionId")

        if policy_name is None:
            return self._error("MissingParameter", "Parameter PolicyName is missing")
        if policy_document is None:
            return self._error(
                "MissingParameter", "Parameter PolicyDocument is missing"
            )

        try:
            resource_policy = self.xray_backend.put_resource_policy(
                policy_name, policy_document, policy_revision_id
            )
        except Exception as err:
            raise err

        return json.dumps({"ResourcePolicy": resource_policy})

    # ListResourcePolicies
    def list_resource_policies(self) -> str:
        policies = self.xray_backend.list_resource_policies()
        return json.dumps({"ResourcePolicies": policies})

    # DeleteResourcePolicy
    def delete_resource_policy(self) -> Union[str, tuple[str, dict[str, int]]]:
        policy_name = self._get_param("PolicyName")
        policy_revision_id = self._get_param("PolicyRevisionId")

        if policy_name is None:
            return self._error("MissingParameter", "Parameter PolicyName is missing")

        try:
            self.xray_backend.delete_resource_policy(policy_name, policy_revision_id)
        except Exception as err:
            raise err

        return json.dumps({})

    # TagResource
    def tag_resource(self) -> Union[str, tuple[str, dict[str, int]]]:
        resource_arn = self._get_param("ResourceARN")
        tags = self._get_param("Tags")

        if resource_arn is None:
            return self._error("MissingParameter", "Parameter ResourceARN is missing")
        if tags is None:
            return self._error("MissingParameter", "Parameter Tags is missing")

        self.xray_backend.tag_resource(resource_arn, tags)
        return json.dumps({})

    # UntagResource
    def untag_resource(self) -> Union[str, tuple[str, dict[str, int]]]:
        resource_arn = self._get_param("ResourceARN")
        tag_keys = self._get_param("TagKeys")

        if resource_arn is None:
            return self._error("MissingParameter", "Parameter ResourceARN is missing")
        if tag_keys is None:
            return self._error("MissingParameter", "Parameter TagKeys is missing")

        self.xray_backend.untag_resource(resource_arn, tag_keys)
        return json.dumps({})

    # ListTagsForResource
    def list_tags_for_resource(self) -> Union[str, tuple[str, dict[str, int]]]:
        resource_arn = self._get_param("ResourceARN")

        if resource_arn is None:
            return self._error("MissingParameter", "Parameter ResourceARN is missing")

        tags = self.xray_backend.list_tags_for_resource(resource_arn)
        return json.dumps({"Tags": tags})

    # GetSamplingTargets
    def sampling_targets(self) -> str:
        docs = self._get_param("SamplingStatisticsDocuments", [])
        result = self.xray_backend.get_sampling_targets(docs)
        return json.dumps(result)

    # GetInsightSummaries
    def insight_summaries(self) -> str:
        result = self.xray_backend.get_insight_summaries()
        return json.dumps(result)

    # GetInsight
    def insight(self) -> str:
        insight_id = self._get_param("InsightId")
        result = self.xray_backend.get_insight(insight_id)
        return json.dumps(result)

    # GetInsightEvents
    def insight_events(self) -> str:
        insight_id = self._get_param("InsightId")
        result = self.xray_backend.get_insight_events(insight_id)
        return json.dumps(result)

    # GetInsightImpactGraph
    def insight_impact_graph(self) -> str:
        insight_id = self._get_param("InsightId")
        start_time = self._get_param("StartTime")
        end_time = self._get_param("EndTime")
        result = self.xray_backend.get_insight_impact_graph(
            insight_id, start_time, end_time
        )
        return json.dumps(result)

    # GetTimeSeriesServiceStatistics
    def time_series_service_statistics(self) -> str:
        result = self.xray_backend.get_time_series_service_statistics()
        return json.dumps(result)

    # GetIndexingRules
    def get_indexing_rules(self) -> str:
        result = self.xray_backend.get_indexing_rules()
        return json.dumps(result)

    # StartTraceRetrieval
    def start_trace_retrieval(self) -> Union[str, tuple[str, dict[str, int]]]:
        trace_ids = self._get_param("TraceIds")
        start_time = self._get_param("StartTime")
        end_time = self._get_param("EndTime")

        if trace_ids is None:
            return self._error("MissingParameter", "Parameter TraceIds is missing")
        if start_time is None:
            return self._error("MissingParameter", "Parameter StartTime is missing")
        if end_time is None:
            return self._error("MissingParameter", "Parameter EndTime is missing")

        token = self.xray_backend.start_trace_retrieval(
            trace_ids, start_time, end_time
        )
        return json.dumps({"RetrievalToken": token})

    # CancelTraceRetrieval
    def cancel_trace_retrieval(self) -> Union[str, tuple[str, dict[str, int]]]:
        retrieval_token = self._get_param("RetrievalToken")

        if retrieval_token is None:
            return self._error(
                "MissingParameter", "Parameter RetrievalToken is missing"
            )

        self.xray_backend.cancel_trace_retrieval(retrieval_token)
        return json.dumps({})

    # GetRetrievedTracesGraph
    def get_retrieved_traces_graph(self) -> Union[str, tuple[str, dict[str, int]]]:
        retrieval_token = self._get_param("RetrievalToken")

        if retrieval_token is None:
            return self._error(
                "MissingParameter", "Parameter RetrievalToken is missing"
            )

        result = self.xray_backend.get_retrieved_traces_graph(retrieval_token)
        return json.dumps(result)

    # ListRetrievedTraces
    def list_retrieved_traces(self) -> Union[str, tuple[str, dict[str, int]]]:
        retrieval_token = self._get_param("RetrievalToken")
        trace_format = self._get_param("TraceFormat")

        if retrieval_token is None:
            return self._error(
                "MissingParameter", "Parameter RetrievalToken is missing"
            )

        result = self.xray_backend.list_retrieved_traces(
            retrieval_token, trace_format
        )
        return json.dumps(result)
