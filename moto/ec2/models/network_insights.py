from typing import Any, Optional

from moto.core.utils import iso_8601_datetime_with_milliseconds, utcnow

from ..utils import random_network_insights_analysis_id, random_network_insights_path_id
from .core import TaggedEC2Resource


class NetworkInsightsPath(TaggedEC2Resource):
    def __init__(
        self,
        backend: Any,
        source: str,
        destination: Optional[str],
        protocol: str,
        destination_port: Optional[int] = None,
        filter_at_source: Optional[dict[str, Any]] = None,
        filter_at_destination: Optional[dict[str, Any]] = None,
        tags: Optional[dict[str, str]] = None,
    ):
        self.ec2_backend = backend
        self.id = random_network_insights_path_id()
        self.source = source
        self.destination = destination
        self.protocol = protocol
        self.destination_port = destination_port
        self.filter_at_source = filter_at_source
        self.filter_at_destination = filter_at_destination
        self.state = "available"
        self._created_at = utcnow()
        self.add_tags(tags or {})

    @property
    def creation_time(self) -> str:
        return iso_8601_datetime_with_milliseconds(self._created_at)

    @property
    def arn(self) -> str:
        return (
            f"arn:{self.ec2_backend.partition}:ec2:{self.ec2_backend.region_name}"
            f":{self.ec2_backend.account_id}:network-insights-path/{self.id}"
        )


class NetworkInsightsAnalysis(TaggedEC2Resource):
    def __init__(
        self,
        backend: Any,
        network_insights_path_id: str,
        filter_in_arns: Optional[list[str]] = None,
        tags: Optional[dict[str, str]] = None,
    ):
        self.ec2_backend = backend
        self.id = random_network_insights_analysis_id()
        self.network_insights_path_id = network_insights_path_id
        self.filter_in_arns = filter_in_arns or []
        self.status = "succeeded"
        self.status_message = ""
        self.network_path_found = True
        self._start_date = utcnow()
        self.add_tags(tags or {})

    @property
    def start_date(self) -> str:
        return iso_8601_datetime_with_milliseconds(self._start_date)

    @property
    def arn(self) -> str:
        return (
            f"arn:{self.ec2_backend.partition}:ec2:{self.ec2_backend.region_name}"
            f":{self.ec2_backend.account_id}:network-insights-analysis/{self.id}"
        )


class NetworkInsightsBackend:
    def __init__(self) -> None:
        self.network_insights_paths: dict[str, NetworkInsightsPath] = {}
        self.network_insights_analyses: dict[str, NetworkInsightsAnalysis] = {}

    def create_network_insights_path(
        self,
        source: str,
        destination: Optional[str] = None,
        protocol: str = "tcp",
        destination_port: Optional[int] = None,
        filter_at_source: Optional[dict[str, Any]] = None,
        filter_at_destination: Optional[dict[str, Any]] = None,
        tags: Optional[dict[str, str]] = None,
    ) -> NetworkInsightsPath:
        path = NetworkInsightsPath(
            self,
            source=source,
            destination=destination,
            protocol=protocol,
            destination_port=destination_port,
            filter_at_source=filter_at_source,
            filter_at_destination=filter_at_destination,
            tags=tags,
        )
        self.network_insights_paths[path.id] = path
        return path

    def delete_network_insights_path(
        self, network_insights_path_id: str
    ) -> NetworkInsightsPath:
        path = self.network_insights_paths.get(network_insights_path_id)
        if not path:
            from ..exceptions import EC2ClientError

            raise EC2ClientError(
                "InvalidNetworkInsightsPathId.NotFound",
                f"The network insights path ID '{network_insights_path_id}' does not exist",
            )
        return self.network_insights_paths.pop(network_insights_path_id)

    def describe_network_insights_paths(
        self,
        network_insights_path_ids: Optional[list[str]] = None,
        filters: Any = None,
    ) -> list[NetworkInsightsPath]:
        paths = list(self.network_insights_paths.values())
        if network_insights_path_ids:
            paths = [p for p in paths if p.id in network_insights_path_ids]
        return paths

    def start_network_insights_analysis(
        self,
        network_insights_path_id: str,
        filter_in_arns: Optional[list[str]] = None,
        tags: Optional[dict[str, str]] = None,
    ) -> NetworkInsightsAnalysis:
        analysis = NetworkInsightsAnalysis(
            self,
            network_insights_path_id=network_insights_path_id,
            filter_in_arns=filter_in_arns,
            tags=tags,
        )
        self.network_insights_analyses[analysis.id] = analysis
        return analysis

    def describe_network_insights_analyses(
        self,
        network_insights_analysis_ids: Optional[list[str]] = None,
        network_insights_path_id: Optional[str] = None,
        filters: Any = None,
    ) -> list[NetworkInsightsAnalysis]:
        analyses = list(self.network_insights_analyses.values())
        if network_insights_analysis_ids:
            analyses = [a for a in analyses if a.id in network_insights_analysis_ids]
        if network_insights_path_id:
            analyses = [
                a
                for a in analyses
                if a.network_insights_path_id == network_insights_path_id
            ]
        return analyses
