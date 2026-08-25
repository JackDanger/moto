"""appconfig base URL and path."""

from .responses import AppConfigResponse

url_bases = [
    r"https?://appconfig\.(.+)\.amazonaws\.com",
]


url_paths = {
    # Applications
    "{0}/applications$": AppConfigResponse.dispatch,
    "{0}/applications/(?P<app_id>[^/]+)$": AppConfigResponse.dispatch,
    # Configuration Profiles
    "{0}/applications/(?P<app_id>[^/]+)/configurationprofiles$": AppConfigResponse.dispatch,
    "{0}/applications/(?P<app_id>[^/]+)/configurationprofiles/(?P<config_profile_id>[^/]+)$": AppConfigResponse.dispatch,
    # Hosted Configuration Versions
    "{0}/applications/(?P<app_id>[^/]+)/configurationprofiles/(?P<config_profile_id>[^/]+)/hostedconfigurationversions$": AppConfigResponse.dispatch,
    "{0}/applications/(?P<app_id>[^/]+)/configurationprofiles/(?P<config_profile_id>[^/]+)/hostedconfigurationversions/(?P<version>[^/]+)$": AppConfigResponse.dispatch,
    # Validate Configuration
    "{0}/applications/(?P<app_id>[^/]+)/configurationprofiles/(?P<config_profile_id>[^/]+)/validators$": AppConfigResponse.dispatch,
    # Environments
    "{0}/applications/(?P<app_id>[^/]+)/environments$": AppConfigResponse.dispatch,
    "{0}/applications/(?P<app_id>[^/]+)/environments/(?P<env_id>[^/]+)$": AppConfigResponse.dispatch,
    # Deployments
    "{0}/applications/(?P<app_id>[^/]+)/environments/(?P<env_id>[^/]+)/deployments$": AppConfigResponse.dispatch,
    "{0}/applications/(?P<app_id>[^/]+)/environments/(?P<env_id>[^/]+)/deployments/(?P<deployment_number>[^/]+)$": AppConfigResponse.dispatch,
    # Configuration (deprecated GetConfiguration)
    "{0}/applications/(?P<app_id>[^/]+)/environments/(?P<env_id>[^/]+)/configurations/(?P<config_id>[^/]+)$": AppConfigResponse.dispatch,
    # Deployment Strategies
    "{0}/deploymentstrategies$": AppConfigResponse.dispatch,
    "{0}/deploymentstrategies/(?P<strategy_id>[^/]+)$": AppConfigResponse.dispatch,
    # Note: AWS has a typo in their API spec for delete: "deployementstrategies"
    "{0}/deployementstrategies/(?P<strategy_id>[^/]+)$": AppConfigResponse.dispatch,
    # Extensions
    "{0}/extensions$": AppConfigResponse.dispatch,
    "{0}/extensions/(?P<ext_id>[^/]+)$": AppConfigResponse.dispatch,
    # Extension Associations
    "{0}/extensionassociations$": AppConfigResponse.dispatch,
    "{0}/extensionassociations/(?P<assoc_id>[^/]+)$": AppConfigResponse.dispatch,
    # Account Settings
    "{0}/settings$": AppConfigResponse.dispatch,
    # Tags
    "{0}/tags/(?P<app_id>.+)$": AppConfigResponse.dispatch,
    "{0}/tags/(?P<arn_part_1>[^/]+)/(?P<app_id>[^/]+)$": AppConfigResponse.dispatch,
    "{0}/tags/(?P<arn_part_1>[^/]+)/(?P<app_id>[^/]+)/configurationprofile/(?P<cp_id>[^/]+)$": AppConfigResponse.dispatch,
}
