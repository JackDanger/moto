"""PrometheusServiceBackend class with methods for supported APIs."""

import base64
from collections.abc import Callable
from typing import Any, Optional

from moto.core.base_backend import BackendDict, BaseBackend
from moto.core.common_models import BaseModel
from moto.core.utils import unix_time
from moto.moto_api._internal import mock_random
from moto.utilities.paginator import paginate
from moto.utilities.tagging_service import TaggingService
from moto.utilities.utils import get_partition

from .exceptions import (
    ResourceNotFoundException,
    RuleGroupNamespaceNotFound,
    WorkspaceNotFound,
)
from .utils import PAGINATION_MODEL


class RuleGroupNamespace(BaseModel):
    def __init__(
        self,
        account_id: str,
        region: str,
        workspace_id: str,
        name: str,
        data: str,
        tag_fn: Callable[[str], dict[str, str]],
    ):
        self.name = name
        self.data = data
        self.tag_fn = tag_fn
        self.arn = f"arn:{get_partition(region)}:aps:{region}:{account_id}:rulegroupsnamespace/{workspace_id}/{self.name}"
        self.created_at = unix_time()
        self.modified_at = self.created_at

    def update(self, new_data: str) -> None:
        self.data = new_data
        self.modified_at = unix_time()

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "arn": self.arn,
            "status": {"statusCode": "ACTIVE"},
            "createdAt": self.created_at,
            "modifiedAt": self.modified_at,
            "data": self.data,
            "tags": self.tag_fn(self.arn),
        }


class AlertManagerDefinition(BaseModel):
    def __init__(self, workspace_id: str, data: str):
        self.workspace_id = workspace_id
        self.data = data
        self.created_at = unix_time()
        self.modified_at = self.created_at
        self.status = {"statusCode": "ACTIVE"}

    def to_dict(self) -> dict[str, Any]:
        return {
            "data": self.data,
            "createdAt": self.created_at,
            "modifiedAt": self.modified_at,
            "status": self.status,
        }


class Scraper(BaseModel):
    def __init__(
        self,
        account_id: str,
        region: str,
        alias: Optional[str],
        scrape_configuration: Optional[dict[str, Any]],
        source: Optional[dict[str, Any]],
        destination: Optional[dict[str, Any]],
        role_configuration: Optional[dict[str, Any]],
        tags: Optional[dict[str, str]],
    ):
        self.scraper_id = f"s-{mock_random.uuid4()}"
        self.alias = alias or ""
        self.arn = f"arn:{get_partition(region)}:aps:{region}:{account_id}:scraper/{self.scraper_id}"
        self.scrape_configuration = scrape_configuration or {}
        self.source = source or {}
        self.destination = destination or {}
        self.role_configuration = role_configuration
        self.tags = tags or {}
        self.status = {"statusCode": "ACTIVE"}
        self.created_at = unix_time()
        self.last_modified_at = self.created_at
        self.logging_destination: Optional[dict[str, Any]] = None
        self.scraper_components: Optional[list[dict[str, Any]]] = None
        self.logging_status: Optional[dict[str, str]] = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "scraperId": self.scraper_id,
            "alias": self.alias,
            "arn": self.arn,
            "scrapeConfiguration": self.scrape_configuration,
            "source": self.source,
            "destination": self.destination,
            "roleConfiguration": self.role_configuration,
            "status": self.status,
            "createdAt": self.created_at,
            "lastModifiedAt": self.last_modified_at,
            "tags": self.tags,
        }

    def summary_dict(self) -> dict[str, Any]:
        return {
            "scraperId": self.scraper_id,
            "alias": self.alias,
            "arn": self.arn,
            "source": self.source,
            "destination": self.destination,
            "roleConfiguration": self.role_configuration,
            "status": self.status,
            "createdAt": self.created_at,
            "lastModifiedAt": self.last_modified_at,
            "tags": self.tags,
        }


class AnomalyDetector(BaseModel):
    def __init__(
        self,
        account_id: str,
        region: str,
        workspace_id: str,
        alias: Optional[str],
        evaluation_interval_in_seconds: Optional[int],
        missing_data_action: Optional[str],
        configuration: Optional[dict[str, Any]],
        labels: Optional[dict[str, str]],
        tags: Optional[dict[str, str]],
    ):
        self.anomaly_detector_id = f"ad-{mock_random.uuid4()}"
        self.workspace_id = workspace_id
        self.alias = alias or ""
        self.arn = f"arn:{get_partition(region)}:aps:{region}:{account_id}:workspace/{workspace_id}/anomalydetector/{self.anomaly_detector_id}"
        self.evaluation_interval_in_seconds = evaluation_interval_in_seconds or 300
        self.missing_data_action = missing_data_action or "IGNORE"
        self.configuration = configuration or {}
        self.labels = labels or {}
        self.tags = tags or {}
        self.status = {"statusCode": "ACTIVE"}
        self.created_at = unix_time()
        self.modified_at = self.created_at

    def to_dict(self) -> dict[str, Any]:
        return {
            "anomalyDetectorId": self.anomaly_detector_id,
            "alias": self.alias,
            "arn": self.arn,
            "evaluationIntervalInSeconds": self.evaluation_interval_in_seconds,
            "missingDataAction": self.missing_data_action,
            "configuration": self.configuration,
            "labels": self.labels,
            "status": self.status,
            "createdAt": self.created_at,
            "modifiedAt": self.modified_at,
            "tags": self.tags,
        }


class Workspace(BaseModel):
    def __init__(
        self,
        account_id: str,
        region: str,
        alias: str,
        tag_fn: Callable[[str], dict[str, str]],
    ):
        self.alias = alias
        self.workspace_id = f"ws-{mock_random.uuid4()}"
        self.arn = f"arn:{get_partition(region)}:aps:{region}:{account_id}:workspace/{self.workspace_id}"
        self.endpoint = f"https://aps-workspaces.{region}.amazonaws.com/workspaces/{self.workspace_id}/"
        self.status = {"statusCode": "ACTIVE"}
        self.created_at = unix_time()
        self.tag_fn = tag_fn
        self.rule_group_namespaces: dict[str, RuleGroupNamespace] = {}
        self.logging_config: Optional[dict[str, Any]] = None
        self.alert_manager_definition: Optional[AlertManagerDefinition] = None
        self.anomaly_detectors: dict[str, AnomalyDetector] = {}
        self.query_logging_config: Optional[dict[str, Any]] = None
        self.resource_policy: Optional[dict[str, Any]] = None
        self.workspace_configuration: Optional[dict[str, Any]] = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "alias": self.alias,
            "arn": self.arn,
            "workspaceId": self.workspace_id,
            "status": self.status,
            "createdAt": self.created_at,
            "prometheusEndpoint": self.endpoint,
            "tags": self.tag_fn(self.arn),
        }


class PrometheusServiceBackend(BaseBackend):
    """Implementation of PrometheusService APIs."""

    def __init__(self, region_name: str, account_id: str):
        super().__init__(region_name, account_id)
        self.workspaces: dict[str, Workspace] = {}
        self.scrapers: dict[str, Scraper] = {}
        self.tagger = TaggingService()

    def create_workspace(self, alias: str, tags: dict[str, str]) -> Workspace:
        """
        The ClientToken-parameter is not yet implemented
        """
        workspace = Workspace(
            self.account_id,
            self.region_name,
            alias=alias,
            tag_fn=self.list_tags_for_resource,
        )
        self.workspaces[workspace.workspace_id] = workspace
        self.tag_resource(workspace.arn, tags)
        return workspace

    def describe_workspace(self, workspace_id: str) -> Workspace:
        if workspace_id not in self.workspaces:
            raise WorkspaceNotFound(workspace_id)
        return self.workspaces[workspace_id]

    def list_tags_for_resource(self, resource_arn: str) -> dict[str, str]:
        return self.tagger.get_tag_dict_for_resource(resource_arn)

    def update_workspace_alias(self, alias: str, workspace_id: str) -> None:
        """
        The ClientToken-parameter is not yet implemented
        """
        self.workspaces[workspace_id].alias = alias

    def delete_workspace(self, workspace_id: str) -> None:
        """
        The ClientToken-parameter is not yet implemented
        """
        self.workspaces.pop(workspace_id, None)

    @paginate(pagination_model=PAGINATION_MODEL)
    def list_workspaces(self, alias: str) -> list[Workspace]:
        if alias:
            return [w for w in self.workspaces.values() if w.alias == alias]
        return list(self.workspaces.values())

    def tag_resource(self, resource_arn: str, tags: dict[str, str]) -> None:
        tag_list = self.tagger.convert_dict_to_tags_input(tags)
        self.tagger.tag_resource(resource_arn, tag_list)

    def untag_resource(self, resource_arn: str, tag_keys: list[str]) -> None:
        self.tagger.untag_resource_using_names(resource_arn, tag_keys)

    def create_rule_groups_namespace(
        self, data: str, name: str, tags: dict[str, str], workspace_id: str
    ) -> RuleGroupNamespace:
        """
        The ClientToken-parameter is not yet implemented
        """
        workspace = self.describe_workspace(workspace_id)
        group = RuleGroupNamespace(
            account_id=self.account_id,
            region=self.region_name,
            workspace_id=workspace_id,
            name=name,
            data=data,
            tag_fn=self.list_tags_for_resource,
        )
        workspace.rule_group_namespaces[name] = group
        self.tag_resource(group.arn, tags)
        return group

    def delete_rule_groups_namespace(self, name: str, workspace_id: str) -> None:
        """
        The ClientToken-parameter is not yet implemented
        """
        ws = self.describe_workspace(workspace_id)
        ws.rule_group_namespaces.pop(name, None)

    def describe_rule_groups_namespace(
        self, name: str, workspace_id: str
    ) -> RuleGroupNamespace:
        ws = self.describe_workspace(workspace_id)
        if name not in ws.rule_group_namespaces:
            raise RuleGroupNamespaceNotFound(name=name)
        return ws.rule_group_namespaces[name]

    def put_rule_groups_namespace(
        self, data: str, name: str, workspace_id: str
    ) -> RuleGroupNamespace:
        """
        The ClientToken-parameter is not yet implemented
        """
        ns = self.describe_rule_groups_namespace(name=name, workspace_id=workspace_id)
        ns.update(data)
        return ns

    @paginate(pagination_model=PAGINATION_MODEL)
    def list_rule_groups_namespaces(
        self, name: str, workspace_id: str
    ) -> list[RuleGroupNamespace]:
        ws = self.describe_workspace(workspace_id)
        if name:
            return [
                ns
                for ns_name, ns in ws.rule_group_namespaces.items()
                if ns_name.startswith(name)
            ]
        return list(ws.rule_group_namespaces.values())

    def create_logging_configuration(
        self, workspace_id: str, log_group_arn: str
    ) -> dict[str, str]:
        ws = self.describe_workspace(workspace_id)
        ws.logging_config = {
            "logGroupArn": log_group_arn,
            "createdAt": unix_time(),
            "status": {"statusCode": "ACTIVE"},
            "workspace": workspace_id,
        }
        return ws.logging_config["status"]

    def describe_logging_configuration(self, workspace_id: str) -> dict[str, Any]:
        ws = self.describe_workspace(workspace_id)
        if ws.logging_config is None:
            return {}
        return ws.logging_config

    def delete_logging_configuration(self, workspace_id: str) -> None:
        ws = self.describe_workspace(workspace_id)
        ws.logging_config = None

    def update_logging_configuration(
        self, workspace_id: str, log_group_arn: str
    ) -> dict[str, str]:
        ws = self.describe_workspace(workspace_id)
        ws.logging_config["logGroupArn"] = log_group_arn  # type: ignore[index]
        ws.logging_config["modifiedAt"] = unix_time()  # type: ignore[index]
        return ws.logging_config["status"]  # type: ignore[index]

    # --- Alert Manager Definition ---

    def create_alert_manager_definition(
        self, workspace_id: str, data: str
    ) -> dict[str, str]:
        ws = self.describe_workspace(workspace_id)
        ws.alert_manager_definition = AlertManagerDefinition(
            workspace_id=workspace_id, data=data
        )
        return ws.alert_manager_definition.status

    def describe_alert_manager_definition(self, workspace_id: str) -> dict[str, Any]:
        ws = self.describe_workspace(workspace_id)
        if ws.alert_manager_definition is None:
            raise ResourceNotFoundException(
                "AlertManagerDefinition not found",
                resource_id=workspace_id,
                resource_type="AWS::APS::AlertManagerDefinition",
            )
        return ws.alert_manager_definition.to_dict()

    def put_alert_manager_definition(
        self, workspace_id: str, data: str
    ) -> dict[str, str]:
        ws = self.describe_workspace(workspace_id)
        if ws.alert_manager_definition is None:
            ws.alert_manager_definition = AlertManagerDefinition(
                workspace_id=workspace_id, data=data
            )
        else:
            ws.alert_manager_definition.data = data
            ws.alert_manager_definition.modified_at = unix_time()
        return ws.alert_manager_definition.status

    def delete_alert_manager_definition(self, workspace_id: str) -> None:
        ws = self.describe_workspace(workspace_id)
        ws.alert_manager_definition = None

    # --- Scraper ---

    def create_scraper(
        self,
        alias: Optional[str],
        scrape_configuration: Optional[dict[str, Any]],
        source: Optional[dict[str, Any]],
        destination: Optional[dict[str, Any]],
        role_configuration: Optional[dict[str, Any]],
        tags: Optional[dict[str, str]],
    ) -> Scraper:
        scraper = Scraper(
            account_id=self.account_id,
            region=self.region_name,
            alias=alias,
            scrape_configuration=scrape_configuration,
            source=source,
            destination=destination,
            role_configuration=role_configuration,
            tags=tags,
        )
        self.scrapers[scraper.scraper_id] = scraper
        if tags:
            self.tag_resource(scraper.arn, tags)
        return scraper

    def describe_scraper(self, scraper_id: str) -> Scraper:
        if scraper_id not in self.scrapers:
            raise ResourceNotFoundException(
                "Scraper not found",
                resource_id=scraper_id,
                resource_type="AWS::APS::Scraper",
            )
        return self.scrapers[scraper_id]

    def update_scraper(
        self,
        scraper_id: str,
        alias: Optional[str],
        scrape_configuration: Optional[dict[str, Any]],
        destination: Optional[dict[str, Any]],
        role_configuration: Optional[dict[str, Any]],
    ) -> Scraper:
        scraper = self.describe_scraper(scraper_id)
        if alias is not None:
            scraper.alias = alias
        if scrape_configuration is not None:
            scraper.scrape_configuration = scrape_configuration
        if destination is not None:
            scraper.destination = destination
        if role_configuration is not None:
            scraper.role_configuration = role_configuration
        scraper.last_modified_at = unix_time()
        return scraper

    def delete_scraper(self, scraper_id: str) -> dict[str, Any]:
        scraper = self.describe_scraper(scraper_id)
        del self.scrapers[scraper_id]
        return {
            "scraperId": scraper_id,
            "status": {"statusCode": "DELETING"},
        }

    def list_scrapers(self, filters: Optional[dict[str, list[str]]]) -> list[Scraper]:
        scrapers = list(self.scrapers.values())
        if filters:
            for key, values in filters.items():
                if key == "alias":
                    scrapers = [s for s in scrapers if s.alias in values]
        return scrapers

    def get_default_scraper_configuration(self) -> str:
        # Return a base64-encoded default Prometheus scraping config
        default_config = """global:
  scrape_interval: 30s
scrape_configs:
  - job_name: default
    static_configs:
      - targets: ['localhost:9090']
"""
        return base64.b64encode(default_config.encode()).decode()

    # --- Scraper Logging Configuration ---

    def describe_scraper_logging_configuration(
        self, scraper_id: str
    ) -> dict[str, Any]:
        scraper = self.describe_scraper(scraper_id)
        result: dict[str, Any] = {
            "scraperId": scraper_id,
            "status": {"statusCode": "ACTIVE"},
            "modifiedAt": scraper.last_modified_at,
        }
        if scraper.logging_destination:
            result["loggingDestination"] = scraper.logging_destination
        if scraper.scraper_components:
            result["scraperComponents"] = scraper.scraper_components
        return result

    def update_scraper_logging_configuration(
        self,
        scraper_id: str,
        logging_destination: Optional[dict[str, Any]],
        scraper_components: Optional[list[dict[str, Any]]],
    ) -> dict[str, str]:
        scraper = self.describe_scraper(scraper_id)
        if logging_destination is not None:
            scraper.logging_destination = logging_destination
        if scraper_components is not None:
            scraper.scraper_components = scraper_components
        scraper.last_modified_at = unix_time()
        return {"statusCode": "ACTIVE"}

    def delete_scraper_logging_configuration(self, scraper_id: str) -> None:
        scraper = self.describe_scraper(scraper_id)
        scraper.logging_destination = None
        scraper.scraper_components = None
        scraper.last_modified_at = unix_time()

    # --- Anomaly Detector ---

    def create_anomaly_detector(
        self,
        workspace_id: str,
        alias: Optional[str],
        evaluation_interval_in_seconds: Optional[int],
        missing_data_action: Optional[str],
        configuration: Optional[dict[str, Any]],
        labels: Optional[dict[str, str]],
        tags: Optional[dict[str, str]],
    ) -> AnomalyDetector:
        ws = self.describe_workspace(workspace_id)
        ad = AnomalyDetector(
            account_id=self.account_id,
            region=self.region_name,
            workspace_id=workspace_id,
            alias=alias,
            evaluation_interval_in_seconds=evaluation_interval_in_seconds,
            missing_data_action=missing_data_action,
            configuration=configuration,
            labels=labels,
            tags=tags,
        )
        ws.anomaly_detectors[ad.anomaly_detector_id] = ad
        if tags:
            self.tag_resource(ad.arn, tags)
        return ad

    def describe_anomaly_detector(
        self, workspace_id: str, anomaly_detector_id: str
    ) -> AnomalyDetector:
        ws = self.describe_workspace(workspace_id)
        if anomaly_detector_id not in ws.anomaly_detectors:
            raise ResourceNotFoundException(
                "AnomalyDetector not found",
                resource_id=anomaly_detector_id,
                resource_type="AWS::APS::AnomalyDetector",
            )
        return ws.anomaly_detectors[anomaly_detector_id]

    def put_anomaly_detector(
        self,
        workspace_id: str,
        anomaly_detector_id: str,
        evaluation_interval_in_seconds: Optional[int],
        missing_data_action: Optional[str],
        configuration: Optional[dict[str, Any]],
        labels: Optional[dict[str, str]],
    ) -> AnomalyDetector:
        ad = self.describe_anomaly_detector(workspace_id, anomaly_detector_id)
        if evaluation_interval_in_seconds is not None:
            ad.evaluation_interval_in_seconds = evaluation_interval_in_seconds
        if missing_data_action is not None:
            ad.missing_data_action = missing_data_action
        if configuration is not None:
            ad.configuration = configuration
        if labels is not None:
            ad.labels = labels
        ad.modified_at = unix_time()
        return ad

    def delete_anomaly_detector(
        self, workspace_id: str, anomaly_detector_id: str
    ) -> None:
        ws = self.describe_workspace(workspace_id)
        ws.anomaly_detectors.pop(anomaly_detector_id, None)

    def list_anomaly_detectors(
        self, workspace_id: str, alias: Optional[str]
    ) -> list[AnomalyDetector]:
        ws = self.describe_workspace(workspace_id)
        detectors = list(ws.anomaly_detectors.values())
        if alias:
            detectors = [d for d in detectors if d.alias == alias]
        return detectors

    # --- Query Logging Configuration ---

    def create_query_logging_configuration(
        self, workspace_id: str, destinations: list[dict[str, Any]]
    ) -> dict[str, str]:
        ws = self.describe_workspace(workspace_id)
        ws.query_logging_config = {
            "destinations": destinations,
            "createdAt": unix_time(),
            "modifiedAt": unix_time(),
            "status": {"statusCode": "ACTIVE"},
            "workspace": workspace_id,
        }
        return ws.query_logging_config["status"]

    def describe_query_logging_configuration(
        self, workspace_id: str
    ) -> dict[str, Any]:
        ws = self.describe_workspace(workspace_id)
        if ws.query_logging_config is None:
            raise ResourceNotFoundException(
                "QueryLoggingConfiguration not found",
                resource_id=workspace_id,
                resource_type="AWS::APS::QueryLoggingConfiguration",
            )
        return ws.query_logging_config

    def update_query_logging_configuration(
        self, workspace_id: str, destinations: list[dict[str, Any]]
    ) -> dict[str, str]:
        ws = self.describe_workspace(workspace_id)
        if ws.query_logging_config is None:
            raise ResourceNotFoundException(
                "QueryLoggingConfiguration not found",
                resource_id=workspace_id,
                resource_type="AWS::APS::QueryLoggingConfiguration",
            )
        ws.query_logging_config["destinations"] = destinations
        ws.query_logging_config["modifiedAt"] = unix_time()
        return ws.query_logging_config["status"]

    def delete_query_logging_configuration(self, workspace_id: str) -> None:
        ws = self.describe_workspace(workspace_id)
        ws.query_logging_config = None

    # --- Resource Policy ---

    def put_resource_policy(
        self,
        workspace_id: str,
        policy_document: str,
        revision_id: Optional[str],
    ) -> dict[str, Any]:
        ws = self.describe_workspace(workspace_id)
        new_revision_id = str(mock_random.uuid4())
        ws.resource_policy = {
            "policyDocument": policy_document,
            "revisionId": new_revision_id,
            "policyStatus": {"statusCode": "ACTIVE"},
        }
        return {
            "policyStatus": ws.resource_policy["policyStatus"],
            "revisionId": new_revision_id,
        }

    def describe_resource_policy(self, workspace_id: str) -> dict[str, Any]:
        ws = self.describe_workspace(workspace_id)
        if ws.resource_policy is None:
            raise ResourceNotFoundException(
                "ResourcePolicy not found",
                resource_id=workspace_id,
                resource_type="AWS::APS::ResourcePolicy",
            )
        return ws.resource_policy

    def delete_resource_policy(self, workspace_id: str) -> None:
        ws = self.describe_workspace(workspace_id)
        ws.resource_policy = None

    # --- Workspace Configuration ---

    def describe_workspace_configuration(self, workspace_id: str) -> dict[str, Any]:
        ws = self.describe_workspace(workspace_id)
        if ws.workspace_configuration is None:
            return {
                "workspaceConfiguration": {
                    "status": {"statusCode": "ACTIVE"},
                    "retentionPeriodInDays": 150,
                    "limitsPerLabelSet": [],
                }
            }
        return {"workspaceConfiguration": ws.workspace_configuration}

    def update_workspace_configuration(
        self,
        workspace_id: str,
        limits_per_label_set: Optional[list[dict[str, Any]]],
        retention_period_in_days: Optional[int],
    ) -> dict[str, str]:
        ws = self.describe_workspace(workspace_id)
        config: dict[str, Any] = {
            "status": {"statusCode": "ACTIVE"},
        }
        if retention_period_in_days is not None:
            config["retentionPeriodInDays"] = retention_period_in_days
        if limits_per_label_set is not None:
            config["limitsPerLabelSet"] = limits_per_label_set
        ws.workspace_configuration = config
        return {"statusCode": "ACTIVE"}


amp_backends = BackendDict(PrometheusServiceBackend, "amp")
