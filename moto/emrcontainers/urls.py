"""emrcontainers base URL and path."""

from .responses import EMRContainersResponse

url_bases = [
    r"https?://emr-containers\.(.+)\.amazonaws\.com",
]


url_paths = {
    "{0}/virtualclusters$": EMRContainersResponse.dispatch,
    "{0}/virtualclusters/(?P<virtualClusterId>[^/]+)$": EMRContainersResponse.dispatch,
    "{0}/virtualclusters/(?P<virtualClusterId>[^/]+)/jobruns$": EMRContainersResponse.dispatch,
    "{0}/virtualclusters/(?P<virtualClusterId>[^/]+)/jobruns/(?P<jobRunId>[^/]+)$": EMRContainersResponse.dispatch,
    "{0}/jobtemplates$": EMRContainersResponse.dispatch,
    "{0}/jobtemplates/(?P<templateId>[^/]+)$": EMRContainersResponse.dispatch,
    "{0}/virtualclusters/(?P<virtualClusterId>[^/]+)/endpoints$": EMRContainersResponse.dispatch,
    "{0}/virtualclusters/(?P<virtualClusterId>[^/]+)/endpoints/(?P<endpointId>[^/]+)$": EMRContainersResponse.dispatch,
    "{0}/securityconfigurations$": EMRContainersResponse.dispatch,
    "{0}/securityconfigurations/(?P<securityConfigurationId>[^/]+)$": EMRContainersResponse.dispatch,
}
