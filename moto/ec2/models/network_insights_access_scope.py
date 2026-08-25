from typing import Any, Optional

from moto.core.utils import iso_8601_datetime_with_milliseconds, utcnow

from ..utils import random_id
from .core import TaggedEC2Resource


class NetworkInsightsAccessScope(TaggedEC2Resource):
    def __init__(
        self,
        ec2_backend: Any,
        match_paths: Optional[list[dict[str, Any]]] = None,
        exclude_paths: Optional[list[dict[str, Any]]] = None,
        client_token: Optional[str] = None,
        tags: Optional[dict[str, str]] = None,
    ):
        self.ec2_backend = ec2_backend
        self.id = random_id(prefix="nis-")
        self.match_paths = match_paths or []
        self.exclude_paths = exclude_paths or []
        self.client_token = client_token or ""
        self._created_at = utcnow()
        self.add_tags(tags or {})

    @property
    def arn(self) -> str:
        return (
            f"arn:{self.ec2_backend.partition}:ec2:{self.ec2_backend.region_name}"
            f":{self.ec2_backend.account_id}:network-insights-access-scope/{self.id}"
        )

    @property
    def created_date(self) -> str:
        return iso_8601_datetime_with_milliseconds(self._created_at)


class NetworkInsightsAccessScopeAnalysis(TaggedEC2Resource):
    def __init__(
        self,
        ec2_backend: Any,
        network_insights_access_scope_id: str,
        tags: Optional[dict[str, str]] = None,
    ):
        self.ec2_backend = ec2_backend
        self.id = random_id(prefix="nisa-")
        self.network_insights_access_scope_id = network_insights_access_scope_id
        self.status = "succeeded"
        self.status_message = ""
        self.findings_found = "true"
        self.analyzed_eni_count = 0
        self._created_at = utcnow()
        self.add_tags(tags or {})

    @property
    def arn(self) -> str:
        return (
            f"arn:{self.ec2_backend.partition}:ec2:{self.ec2_backend.region_name}"
            f":{self.ec2_backend.account_id}:network-insights-access-scope-analysis/{self.id}"
        )

    @property
    def start_date(self) -> str:
        return iso_8601_datetime_with_milliseconds(self._created_at)

    @property
    def end_date(self) -> str:
        return iso_8601_datetime_with_milliseconds(self._created_at)


class NetworkInsightsAccessScopeBackend:
    def __init__(self) -> None:
        self.network_insights_access_scopes: dict[str, NetworkInsightsAccessScope] = {}
        self.network_insights_access_scope_analyses: dict[
            str, NetworkInsightsAccessScopeAnalysis
        ] = {}

    def create_network_insights_access_scope(
        self,
        match_paths: Optional[list[dict[str, Any]]] = None,
        exclude_paths: Optional[list[dict[str, Any]]] = None,
        client_token: Optional[str] = None,
        tags: Optional[dict[str, str]] = None,
    ) -> NetworkInsightsAccessScope:
        scope = NetworkInsightsAccessScope(
            self,
            match_paths=match_paths,
            exclude_paths=exclude_paths,
            client_token=client_token,
            tags=tags,
        )
        self.network_insights_access_scopes[scope.id] = scope
        return scope

    def delete_network_insights_access_scope(
        self, network_insights_access_scope_id: str
    ) -> NetworkInsightsAccessScope:
        scope = self.network_insights_access_scopes.pop(
            network_insights_access_scope_id, None
        )
        if not scope:
            from ..exceptions import EC2ClientError

            raise EC2ClientError(
                "InvalidNetworkInsightsAccessScopeId.NotFound",
                f"The network insights access scope ID '{network_insights_access_scope_id}' does not exist",
            )
        return scope

    def describe_network_insights_access_scopes(
        self,
        scope_ids: Optional[list[str]] = None,
    ) -> list[NetworkInsightsAccessScope]:
        scopes = list(self.network_insights_access_scopes.values())
        if scope_ids:
            scopes = [s for s in scopes if s.id in scope_ids]
        return scopes

    def start_network_insights_access_scope_analysis(
        self,
        network_insights_access_scope_id: str,
        tags: Optional[dict[str, str]] = None,
    ) -> NetworkInsightsAccessScopeAnalysis:
        if network_insights_access_scope_id not in self.network_insights_access_scopes:
            from ..exceptions import EC2ClientError

            raise EC2ClientError(
                "InvalidNetworkInsightsAccessScopeId.NotFound",
                f"The network insights access scope ID '{network_insights_access_scope_id}' does not exist",
            )
        analysis = NetworkInsightsAccessScopeAnalysis(
            self,
            network_insights_access_scope_id=network_insights_access_scope_id,
            tags=tags,
        )
        self.network_insights_access_scope_analyses[analysis.id] = analysis
        return analysis

    def describe_network_insights_access_scope_analyses(
        self,
        analysis_ids: Optional[list[str]] = None,
        scope_id: Optional[str] = None,
    ) -> list[NetworkInsightsAccessScopeAnalysis]:
        analyses = list(self.network_insights_access_scope_analyses.values())
        if analysis_ids:
            analyses = [a for a in analyses if a.id in analysis_ids]
        if scope_id:
            analyses = [
                a for a in analyses if a.network_insights_access_scope_id == scope_id
            ]
        return analyses

    def get_network_insights_access_scope_analysis_findings(
        self,
        analysis_id: str,
    ) -> tuple[Optional[NetworkInsightsAccessScopeAnalysis], list[Any]]:
        analysis = self.network_insights_access_scope_analyses.get(analysis_id)
        return analysis, []

    def get_network_insights_access_scope_content(
        self,
        network_insights_access_scope_id: str,
    ) -> Optional[NetworkInsightsAccessScope]:
        return self.network_insights_access_scopes.get(network_insights_access_scope_id)
