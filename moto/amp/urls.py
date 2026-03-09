"""amp base URL and path."""

from .responses import PrometheusServiceResponse

url_bases = [
    r"https?://aps\.(.+)\.amazonaws\.com",
]

response = PrometheusServiceResponse()

url_paths = {
    "{0}/workspaces$": PrometheusServiceResponse.dispatch,
    "{0}/workspaces/(?P<workspace_id>[^/]+)$": PrometheusServiceResponse.dispatch,
    "{0}/workspaces/(?P<workspace_id>[^/]+)/alias$": PrometheusServiceResponse.dispatch,
    "{0}/workspaces/(?P<workspace_id>[^/]+)/logging$": PrometheusServiceResponse.dispatch,
    "{0}/workspaces/(?P<workspace_id>[^/]+)/rulegroupsnamespaces$": PrometheusServiceResponse.dispatch,
    "{0}/workspaces/(?P<workspace_id>[^/]+)/rulegroupsnamespaces/(?P<name>[^/]+)$": PrometheusServiceResponse.dispatch,
    # Alert Manager Definition
    "{0}/workspaces/(?P<workspace_id>[^/]+)/alertmanager/definition$": response.alert_manager_definition,
    # Anomaly Detectors
    "{0}/workspaces/(?P<workspace_id>[^/]+)/anomalydetectors$": response.anomaly_detectors_dispatch,
    "{0}/workspaces/(?P<workspace_id>[^/]+)/anomalydetectors/(?P<anomaly_detector_id>[^/]+)$": response.anomaly_detector_dispatch,
    # Query Logging
    "{0}/workspaces/(?P<workspace_id>[^/]+)/logging/query$": response.query_logging,
    # Resource Policy
    "{0}/workspaces/(?P<workspace_id>[^/]+)/policy$": response.resource_policy,
    # Workspace Configuration
    "{0}/workspaces/(?P<workspace_id>[^/]+)/configuration$": response.workspace_configuration,
    # Scrapers
    "{0}/scrapers$": response.scrapers_dispatch,
    "{0}/scrapers/(?P<scraper_id>[^/]+)$": response.scraper_dispatch,
    "{0}/scrapers/(?P<scraper_id>[^/]+)/logging-configuration$": response.scraper_logging,
    # Default scraper configuration
    "{0}/scraperconfiguration$": response.scraper_configuration,
    # Tags
    "{0}/tags/(?P<resource_arn>[^/]+)$": PrometheusServiceResponse.dispatch,
    "{0}/tags/(?P<arn_prefix>[^/]+)/(?P<workspace_id>[^/]+)$": PrometheusServiceResponse.dispatch,
    "{0}/tags/(?P<arn_prefix>[^/]+)/(?P<workspace_id>[^/]+)/(?P<ns_name>[^/]+)$": PrometheusServiceResponse.dispatch,
}
