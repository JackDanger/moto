"""Handles incoming amp requests, invokes methods, returns responses."""

import json
from typing import Any
from urllib.parse import unquote

from moto.core.responses import BaseResponse

from .models import PrometheusServiceBackend, amp_backends


class PrometheusServiceResponse(BaseResponse):
    """Handler for PrometheusService requests and responses."""

    def tags(self, request: Any, full_url: str, headers: Any) -> str:  # type: ignore[return]
        self.setup_class(request, full_url, headers)
        if request.method == "GET":
            return self.list_tags_for_resource()
        if request.method == "POST":
            return self.tag_resource()
        if request.method == "DELETE":
            return self.untag_resource()

    def __init__(self) -> None:
        super().__init__(service_name="amp")

    @property
    def amp_backend(self) -> PrometheusServiceBackend:
        """Return backend instance specific for this region."""
        return amp_backends[self.current_account][self.region]

    def create_workspace(self) -> str:
        params = json.loads(self.body)
        alias = params.get("alias")
        tags = params.get("tags")
        workspace = self.amp_backend.create_workspace(alias=alias, tags=tags)
        return json.dumps(dict(workspace.to_dict()))

    def describe_workspace(self) -> str:
        workspace_id = self.path.split("/")[-1]
        workspace = self.amp_backend.describe_workspace(workspace_id=workspace_id)
        return json.dumps({"workspace": workspace.to_dict()})

    def list_tags_for_resource(self) -> str:
        resource_arn = unquote(self.path).split("tags/")[-1]
        tags = self.amp_backend.list_tags_for_resource(resource_arn=resource_arn)
        return json.dumps({"tags": tags})

    def update_workspace_alias(self) -> str:
        params = json.loads(self.body)
        alias = params.get("alias")
        workspace_id = self.path.split("/")[-2]
        self.amp_backend.update_workspace_alias(alias=alias, workspace_id=workspace_id)
        return json.dumps({})

    def delete_workspace(self) -> str:
        workspace_id = self.path.split("/")[-1]
        self.amp_backend.delete_workspace(workspace_id=workspace_id)
        return json.dumps({})

    def list_workspaces(self) -> str:
        alias = self._get_param("alias")
        max_results = self._get_int_param("maxResults")
        next_token = self._get_param("nextToken")
        workspaces, next_token = self.amp_backend.list_workspaces(
            alias, max_results=max_results, next_token=next_token
        )
        return json.dumps(
            {"nextToken": next_token, "workspaces": [w.to_dict() for w in workspaces]}
        )

    def tag_resource(self) -> str:
        params = json.loads(self.body)
        resource_arn = unquote(self.path).split("tags/")[-1]
        tags = params.get("tags")
        self.amp_backend.tag_resource(resource_arn=resource_arn, tags=tags)
        return json.dumps({})

    def untag_resource(self) -> str:
        resource_arn = unquote(self.path).split("tags/")[-1]
        tag_keys = self.querystring.get("tagKeys", [])
        self.amp_backend.untag_resource(resource_arn=resource_arn, tag_keys=tag_keys)
        return json.dumps({})

    def create_rule_groups_namespace(self) -> str:
        params = json.loads(self.body)
        data = params.get("data")
        name = params.get("name")
        tags = params.get("tags")
        workspace_id = unquote(self.path).split("/")[-2]
        rule_group_namespace = self.amp_backend.create_rule_groups_namespace(
            data=data,
            name=name,
            tags=tags,
            workspace_id=workspace_id,
        )
        return json.dumps(rule_group_namespace.to_dict())

    def delete_rule_groups_namespace(self) -> str:
        name = unquote(self.path).split("/")[-1]
        workspace_id = unquote(self.path).split("/")[-3]
        self.amp_backend.delete_rule_groups_namespace(
            name=name,
            workspace_id=workspace_id,
        )
        return json.dumps({})

    def describe_rule_groups_namespace(self) -> str:
        name = unquote(self.path).split("/")[-1]
        workspace_id = unquote(self.path).split("/")[-3]
        ns = self.amp_backend.describe_rule_groups_namespace(
            name=name, workspace_id=workspace_id
        )
        return json.dumps({"ruleGroupsNamespace": ns.to_dict()})

    def put_rule_groups_namespace(self) -> str:
        params = json.loads(self.body)
        data = params.get("data")
        name = unquote(self.path).split("/")[-1]
        workspace_id = unquote(self.path).split("/")[-3]
        ns = self.amp_backend.put_rule_groups_namespace(
            data=data,
            name=name,
            workspace_id=workspace_id,
        )
        return json.dumps(ns.to_dict())

    def list_rule_groups_namespaces(self) -> str:
        max_results = self._get_int_param("maxResults")
        next_token = self._get_param("nextToken")
        name = self._get_param("name")
        workspace_id = unquote(self.path).split("/")[-2]
        namespaces, next_token = self.amp_backend.list_rule_groups_namespaces(
            max_results=max_results,
            name=name,
            next_token=next_token,
            workspace_id=workspace_id,
        )
        return json.dumps(
            {
                "nextToken": next_token,
                "ruleGroupsNamespaces": [ns.to_dict() for ns in namespaces],
            }
        )

    def create_logging_configuration(self) -> str:
        workspace_id = unquote(self.path).split("/")[-2]
        log_group_arn = self._get_param("logGroupArn")
        status = self.amp_backend.create_logging_configuration(
            workspace_id=workspace_id,
            log_group_arn=log_group_arn,
        )
        return json.dumps({"status": status})

    def describe_logging_configuration(self) -> str:
        workspace_id = unquote(self.path).split("/")[-2]
        config = self.amp_backend.describe_logging_configuration(
            workspace_id=workspace_id
        )
        return json.dumps({"loggingConfiguration": config})

    def update_logging_configuration(self) -> str:
        workspace_id = unquote(self.path).split("/")[-2]
        log_group_arn = self._get_param("logGroupArn")
        status = self.amp_backend.update_logging_configuration(
            workspace_id=workspace_id, log_group_arn=log_group_arn
        )
        return json.dumps({"status": status})

    def delete_logging_configuration(self) -> str:
        workspace_id = unquote(self.path).split("/")[-2]
        self.amp_backend.delete_logging_configuration(workspace_id=workspace_id)
        return "{}"

    # --- Alert Manager Definition ---

    def alert_manager_definition(self, request: Any, full_url: str, headers: Any) -> str:  # type: ignore[return]
        self.setup_class(request, full_url, headers)
        if request.method == "POST":
            return self.create_alert_manager_definition()
        if request.method == "GET":
            return self.describe_alert_manager_definition()
        if request.method == "PUT":
            return self.put_alert_manager_definition()
        if request.method == "DELETE":
            return self.delete_alert_manager_definition()

    def create_alert_manager_definition(self) -> str:
        workspace_id = unquote(self.path).split("/workspaces/")[-1].split("/")[0]
        params = json.loads(self.body)
        data = params.get("data", "")
        status = self.amp_backend.create_alert_manager_definition(
            workspace_id=workspace_id, data=data
        )
        return json.dumps({"status": status})

    def describe_alert_manager_definition(self) -> str:
        workspace_id = unquote(self.path).split("/workspaces/")[-1].split("/")[0]
        definition = self.amp_backend.describe_alert_manager_definition(
            workspace_id=workspace_id
        )
        return json.dumps({"alertManagerDefinition": definition})

    def put_alert_manager_definition(self) -> str:
        workspace_id = unquote(self.path).split("/workspaces/")[-1].split("/")[0]
        params = json.loads(self.body)
        data = params.get("data", "")
        status = self.amp_backend.put_alert_manager_definition(
            workspace_id=workspace_id, data=data
        )
        return json.dumps({"status": status})

    def delete_alert_manager_definition(self) -> str:
        workspace_id = unquote(self.path).split("/workspaces/")[-1].split("/")[0]
        self.amp_backend.delete_alert_manager_definition(workspace_id=workspace_id)
        return "{}"

    # --- Scraper ---

    def scrapers_dispatch(self, request: Any, full_url: str, headers: Any) -> str:  # type: ignore[return]
        self.setup_class(request, full_url, headers)
        if request.method == "POST":
            return self.create_scraper()
        if request.method == "GET":
            return self.list_scrapers()

    def scraper_dispatch(self, request: Any, full_url: str, headers: Any) -> str:  # type: ignore[return]
        self.setup_class(request, full_url, headers)
        if request.method == "GET":
            return self.describe_scraper()
        if request.method == "PUT":
            return self.update_scraper()
        if request.method == "DELETE":
            return self.delete_scraper()

    def create_scraper(self) -> str:
        params = json.loads(self.body)
        scraper = self.amp_backend.create_scraper(
            alias=params.get("alias"),
            scrape_configuration=params.get("scrapeConfiguration"),
            source=params.get("source"),
            destination=params.get("destination"),
            role_configuration=params.get("roleConfiguration"),
            tags=params.get("tags"),
        )
        return json.dumps({
            "scraperId": scraper.scraper_id,
            "arn": scraper.arn,
            "status": scraper.status,
            "tags": scraper.tags,
        })

    def describe_scraper(self) -> str:
        scraper_id = unquote(self.path).split("/scrapers/")[-1].split("/")[0]
        scraper = self.amp_backend.describe_scraper(scraper_id=scraper_id)
        return json.dumps({"scraper": scraper.to_dict()})

    def update_scraper(self) -> str:
        scraper_id = unquote(self.path).split("/scrapers/")[-1].split("/")[0]
        params = json.loads(self.body)
        scraper = self.amp_backend.update_scraper(
            scraper_id=scraper_id,
            alias=params.get("alias"),
            scrape_configuration=params.get("scrapeConfiguration"),
            destination=params.get("destination"),
            role_configuration=params.get("roleConfiguration"),
        )
        return json.dumps({
            "scraperId": scraper.scraper_id,
            "arn": scraper.arn,
            "status": scraper.status,
            "tags": scraper.tags,
        })

    def delete_scraper(self) -> str:
        scraper_id = unquote(self.path).split("/scrapers/")[-1].split("/")[0]
        result = self.amp_backend.delete_scraper(scraper_id=scraper_id)
        return json.dumps(result)

    def list_scrapers(self) -> str:
        # filters come as query params like filters.key=value
        scrapers = self.amp_backend.list_scrapers(filters=None)
        return json.dumps({
            "nextToken": None,
            "scrapers": [s.summary_dict() for s in scrapers],
        })

    def scraper_configuration(self, request: Any, full_url: str, headers: Any) -> str:
        self.setup_class(request, full_url, headers)
        return self.get_default_scraper_configuration()

    def get_default_scraper_configuration(self) -> str:
        config = self.amp_backend.get_default_scraper_configuration()
        return json.dumps({"configuration": config})

    # --- Scraper Logging Configuration ---

    def scraper_logging(self, request: Any, full_url: str, headers: Any) -> str:  # type: ignore[return]
        self.setup_class(request, full_url, headers)
        if request.method == "GET":
            return self.describe_scraper_logging_configuration()
        if request.method == "PUT":
            return self.update_scraper_logging_configuration()
        if request.method == "DELETE":
            return self.delete_scraper_logging_configuration()

    def describe_scraper_logging_configuration(self) -> str:
        scraper_id = unquote(self.path).split("/scrapers/")[-1].split("/")[0]
        result = self.amp_backend.describe_scraper_logging_configuration(
            scraper_id=scraper_id
        )
        return json.dumps(result)

    def update_scraper_logging_configuration(self) -> str:
        scraper_id = unquote(self.path).split("/scrapers/")[-1].split("/")[0]
        params = json.loads(self.body)
        status = self.amp_backend.update_scraper_logging_configuration(
            scraper_id=scraper_id,
            logging_destination=params.get("loggingDestination"),
            scraper_components=params.get("scraperComponents"),
        )
        return json.dumps({"status": status})

    def delete_scraper_logging_configuration(self) -> str:
        scraper_id = unquote(self.path).split("/scrapers/")[-1].split("/")[0]
        self.amp_backend.delete_scraper_logging_configuration(scraper_id=scraper_id)
        return "{}"

    # --- Anomaly Detector ---

    def anomaly_detectors_dispatch(self, request: Any, full_url: str, headers: Any) -> str:  # type: ignore[return]
        self.setup_class(request, full_url, headers)
        if request.method == "POST":
            return self.create_anomaly_detector()
        if request.method == "GET":
            return self.list_anomaly_detectors()

    def anomaly_detector_dispatch(self, request: Any, full_url: str, headers: Any) -> str:  # type: ignore[return]
        self.setup_class(request, full_url, headers)
        if request.method == "GET":
            return self.describe_anomaly_detector()
        if request.method == "PUT":
            return self.put_anomaly_detector()
        if request.method == "DELETE":
            return self.delete_anomaly_detector()

    def create_anomaly_detector(self) -> str:
        workspace_id = unquote(self.path).split("/workspaces/")[-1].split("/")[0]
        params = json.loads(self.body)
        ad = self.amp_backend.create_anomaly_detector(
            workspace_id=workspace_id,
            alias=params.get("alias"),
            evaluation_interval_in_seconds=params.get("evaluationIntervalInSeconds"),
            missing_data_action=params.get("missingDataAction"),
            configuration=params.get("configuration"),
            labels=params.get("labels"),
            tags=params.get("tags"),
        )
        return json.dumps({
            "anomalyDetectorId": ad.anomaly_detector_id,
            "arn": ad.arn,
            "status": ad.status,
            "tags": ad.tags,
        })

    def describe_anomaly_detector(self) -> str:
        parts = unquote(self.path).split("/")
        workspace_id = parts[parts.index("workspaces") + 1]
        anomaly_detector_id = parts[-1]
        ad = self.amp_backend.describe_anomaly_detector(
            workspace_id=workspace_id,
            anomaly_detector_id=anomaly_detector_id,
        )
        return json.dumps({"anomalyDetector": ad.to_dict()})

    def put_anomaly_detector(self) -> str:
        parts = unquote(self.path).split("/")
        workspace_id = parts[parts.index("workspaces") + 1]
        anomaly_detector_id = parts[-1]
        params = json.loads(self.body)
        ad = self.amp_backend.put_anomaly_detector(
            workspace_id=workspace_id,
            anomaly_detector_id=anomaly_detector_id,
            evaluation_interval_in_seconds=params.get("evaluationIntervalInSeconds"),
            missing_data_action=params.get("missingDataAction"),
            configuration=params.get("configuration"),
            labels=params.get("labels"),
        )
        return json.dumps({
            "anomalyDetectorId": ad.anomaly_detector_id,
            "arn": ad.arn,
            "status": ad.status,
            "tags": ad.tags,
        })

    def delete_anomaly_detector(self) -> str:
        parts = unquote(self.path).split("/")
        workspace_id = parts[parts.index("workspaces") + 1]
        anomaly_detector_id = parts[-1]
        self.amp_backend.delete_anomaly_detector(
            workspace_id=workspace_id,
            anomaly_detector_id=anomaly_detector_id,
        )
        return "{}"

    def list_anomaly_detectors(self) -> str:
        workspace_id = unquote(self.path).split("/workspaces/")[-1].split("/")[0]
        alias = self._get_param("alias")
        detectors = self.amp_backend.list_anomaly_detectors(
            workspace_id=workspace_id, alias=alias
        )
        return json.dumps({
            "nextToken": None,
            "anomalyDetectors": [d.to_dict() for d in detectors],
        })

    # --- Query Logging Configuration ---

    def query_logging(self, request: Any, full_url: str, headers: Any) -> str:  # type: ignore[return]
        self.setup_class(request, full_url, headers)
        if request.method == "POST":
            return self.create_query_logging_configuration()
        if request.method == "GET":
            return self.describe_query_logging_configuration()
        if request.method == "PUT":
            return self.update_query_logging_configuration()
        if request.method == "DELETE":
            return self.delete_query_logging_configuration()

    def create_query_logging_configuration(self) -> str:
        workspace_id = unquote(self.path).split("/workspaces/")[-1].split("/")[0]
        params = json.loads(self.body)
        destinations = params.get("destinations", [])
        status = self.amp_backend.create_query_logging_configuration(
            workspace_id=workspace_id, destinations=destinations
        )
        return json.dumps({"status": status})

    def describe_query_logging_configuration(self) -> str:
        workspace_id = unquote(self.path).split("/workspaces/")[-1].split("/")[0]
        config = self.amp_backend.describe_query_logging_configuration(
            workspace_id=workspace_id
        )
        return json.dumps({"queryLoggingConfiguration": config})

    def update_query_logging_configuration(self) -> str:
        workspace_id = unquote(self.path).split("/workspaces/")[-1].split("/")[0]
        params = json.loads(self.body)
        destinations = params.get("destinations", [])
        status = self.amp_backend.update_query_logging_configuration(
            workspace_id=workspace_id, destinations=destinations
        )
        return json.dumps({"status": status})

    def delete_query_logging_configuration(self) -> str:
        workspace_id = unquote(self.path).split("/workspaces/")[-1].split("/")[0]
        self.amp_backend.delete_query_logging_configuration(
            workspace_id=workspace_id
        )
        return "{}"

    # --- Resource Policy ---

    def resource_policy(self, request: Any, full_url: str, headers: Any) -> str:  # type: ignore[return]
        self.setup_class(request, full_url, headers)
        if request.method == "GET":
            return self.describe_resource_policy()
        if request.method == "PUT":
            return self.put_resource_policy()
        if request.method == "DELETE":
            return self.delete_resource_policy()

    def describe_resource_policy(self) -> str:
        workspace_id = unquote(self.path).split("/workspaces/")[-1].split("/")[0]
        policy = self.amp_backend.describe_resource_policy(workspace_id=workspace_id)
        return json.dumps(policy)

    def put_resource_policy(self) -> str:
        workspace_id = unquote(self.path).split("/workspaces/")[-1].split("/")[0]
        params = json.loads(self.body)
        result = self.amp_backend.put_resource_policy(
            workspace_id=workspace_id,
            policy_document=params.get("policyDocument", ""),
            revision_id=params.get("revisionId"),
        )
        return json.dumps(result)

    def delete_resource_policy(self) -> str:
        workspace_id = unquote(self.path).split("/workspaces/")[-1].split("/")[0]
        self.amp_backend.delete_resource_policy(workspace_id=workspace_id)
        return "{}"

    # --- Workspace Configuration ---

    def workspace_configuration(self, request: Any, full_url: str, headers: Any) -> str:  # type: ignore[return]
        self.setup_class(request, full_url, headers)
        if request.method == "GET":
            return self.describe_workspace_configuration()
        if request.method == "PATCH":
            return self.update_workspace_configuration()

    def describe_workspace_configuration(self) -> str:
        workspace_id = unquote(self.path).split("/workspaces/")[-1].split("/")[0]
        result = self.amp_backend.describe_workspace_configuration(
            workspace_id=workspace_id
        )
        return json.dumps(result)

    def update_workspace_configuration(self) -> str:
        workspace_id = unquote(self.path).split("/workspaces/")[-1].split("/")[0]
        params = json.loads(self.body)
        status = self.amp_backend.update_workspace_configuration(
            workspace_id=workspace_id,
            limits_per_label_set=params.get("limitsPerLabelSet"),
            retention_period_in_days=params.get("retentionPeriodInDays"),
        )
        return json.dumps({"status": status})
