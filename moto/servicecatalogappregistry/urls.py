"""servicecatalogappregistry base URL and path."""

from .responses import AppRegistryResponse

url_bases = [
    r"https?://servicecatalog-appregistry\.(.+)\.amazonaws\.com",
]

url_paths = {
    "{0}/applications$": AppRegistryResponse.dispatch,
    "{0}/applications/(?P<application>[^/]+)/attribute-groups/(?P<attributeGroup>[^/]+)$": AppRegistryResponse.dispatch,
    "{0}/applications/(?P<application>[^/]+)/attribute-groups$": AppRegistryResponse.dispatch,
    "{0}/applications/(?P<application>[^/]+)/attribute-group-details$": AppRegistryResponse.dispatch,
    "{0}/applications/(?P<application>[^/]+)/resources/(?P<resourceType>[^/]+)/(?P<resource>.+)$": AppRegistryResponse.dispatch,
    "{0}/applications/(?P<application>.+)/resources$": AppRegistryResponse.dispatch,
    "{0}/applications/(?P<application>[^/]+)$": AppRegistryResponse.dispatch,
    "{0}/attribute-groups/(?P<attributeGroup>[^/]+)$": AppRegistryResponse.dispatch,
    "{0}/attribute-groups$": AppRegistryResponse.dispatch,
    "{0}/sync/(?P<resourceType>[^/]+)/(?P<resource>.+)$": AppRegistryResponse.dispatch,
    "{0}/tags/(?P<resourceArn>.+)$": AppRegistryResponse.dispatch,
    "{0}/configuration$": AppRegistryResponse.dispatch,
}
