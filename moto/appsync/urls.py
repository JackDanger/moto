"""appsync base URL and path."""

from .responses import AppSyncResponse

url_bases = [
    r"https?://appsync\.(.+)\.amazonaws\.com",
    r"https?://([a-zA-Z0-9\-_]+)\.appsync-api\.(.+)\.amazonaws\.com",
]


url_paths = {
    "{0}/v1/apis$": AppSyncResponse.dispatch,
    "{0}/v1/apis/(?P<api_id>[^/]+)$": AppSyncResponse.dispatch,
    "{0}/v1/apis/(?P<api_id>[^/]+)/apikeys$": AppSyncResponse.dispatch,
    "{0}/v1/apis/(?P<api_id>[^/]+)/apikeys/(?P<api_key_id>[^/]+)$": AppSyncResponse.dispatch,
    "{0}/v1/apis/(?P<api_id>[^/]+)/schemacreation$": AppSyncResponse.dispatch,
    "{0}/v1/apis/(?P<api_id>[^/]+)/schema$": AppSyncResponse.dispatch,
    "{0}/v1/tags/(?P<resource_arn>.+)$": AppSyncResponse.dispatch,
    "{0}/v1/tags/(?P<resource_arn_pt1>.+)/(?P<resource_arn_pt2>.+)$": AppSyncResponse.dispatch,
    # DataSources
    "{0}/v1/apis/(?P<api_id>[^/]+)/datasources$": AppSyncResponse.dispatch,
    "{0}/v1/apis/(?P<api_id>[^/]+)/datasources/(?P<name>[^/]+)$": AppSyncResponse.dispatch,
    # Types (must come before the old types pattern)
    "{0}/v1/apis/(?P<api_id>[^/]+)/types$": AppSyncResponse.dispatch,
    # Resolvers
    "{0}/v1/apis/(?P<api_id>[^/]+)/types/(?P<type_name>[^/]+)/resolvers$": AppSyncResponse.dispatch,
    "{0}/v1/apis/(?P<api_id>[^/]+)/types/(?P<type_name>[^/]+)/resolvers/(?P<field_name>[^/]+)$": AppSyncResponse.dispatch,
    # Types with name (after resolvers so resolvers match first)
    "{0}/v1/apis/(?P<api_id>[^/]+)/types/(?P<type_name>.+)$": AppSyncResponse.dispatch,
    # Functions
    "{0}/v1/apis/(?P<api_id>[^/]+)/functions$": AppSyncResponse.dispatch,
    "{0}/v1/apis/(?P<api_id>[^/]+)/functions/(?P<function_id>[^/]+)$": AppSyncResponse.dispatch,
    # API Caches
    "{0}/v1/apis/(?P<apiId>.*)/ApiCaches$": AppSyncResponse.dispatch,
    "{0}/v1/apis/(?P<apiId>.*)/ApiCaches/update$": AppSyncResponse.dispatch,
    "{0}/v1/apis/(?P<apiId>.*)/FlushCache$": AppSyncResponse.dispatch,
    # Domain Names
    "{0}/v1/domainnames$": AppSyncResponse.dispatch,
    "{0}/v1/domainnames/(?P<domain_name>[^/]+)/apiassociation$": AppSyncResponse.dispatch,
    "{0}/v1/domainnames/(?P<domain_name>[^/]+)$": AppSyncResponse.dispatch,
    # Events API (v2)
    "{0}/v2/apis$": AppSyncResponse.dispatch,
    "{0}/v2/apis/(?P<apiId>[^/]+)$": AppSyncResponse.dispatch,
    "{0}/v2/apis/(?P<apiId>[^/]+)/channelNamespaces$": AppSyncResponse.dispatch,
    "{0}/v2/apis/(?P<apiId>[^/]+)/channelNamespaces/(?P<name>[^/]+)$": AppSyncResponse.dispatch,
    "{0}/event$": AppSyncResponse.dns_event_response,
    # Merged/Source API associations
    "{0}/v1/sourceApis/(?P<sourceApiId>[^/]+)/mergedApiAssociations$": AppSyncResponse.dispatch,
    "{0}/v1/sourceApis/(?P<sourceApiId>[^/]+)/mergedApiAssociations/(?P<assocId>[^/]+)$": AppSyncResponse.dispatch,
    "{0}/v1/mergedApis/(?P<mergedApiId>[^/]+)/sourceApiAssociations$": AppSyncResponse.dispatch,
    "{0}/v1/mergedApis/(?P<mergedApiId>[^/]+)/sourceApiAssociations/(?P<assocId>[^/]+)/merge$": AppSyncResponse.dispatch,
    "{0}/v1/mergedApis/(?P<mergedApiId>[^/]+)/sourceApiAssociations/(?P<assocId>[^/]+)/types$": AppSyncResponse.dispatch,
    "{0}/v1/mergedApis/(?P<mergedApiId>[^/]+)/sourceApiAssociations/(?P<assocId>[^/]+)$": AppSyncResponse.dispatch,
    # Resolvers by function
    "{0}/v1/apis/(?P<api_id>[^/]+)/functions/(?P<function_id>[^/]+)/resolvers$": AppSyncResponse.dispatch,
    # Environment variables
    "{0}/v1/apis/(?P<api_id>[^/]+)/environmentVariables$": AppSyncResponse.dispatch,
    # Evaluate code / mapping template
    "{0}/v1/dataplane-evaluatecode$": AppSyncResponse.dispatch,
    "{0}/v1/dataplane-evaluatetemplate$": AppSyncResponse.dispatch,
    # DataSource introspection
    "{0}/v1/datasources/introspections$": AppSyncResponse.dispatch,
    "{0}/v1/datasources/introspections/(?P<introspectionId>[^/]+)$": AppSyncResponse.dispatch,
    # Source API associations for listing
    "{0}/v1/apis/(?P<api_id>[^/]+)/sourceApiAssociations$": AppSyncResponse.dispatch,
}
