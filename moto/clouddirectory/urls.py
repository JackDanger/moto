"""clouddirectory base URL and path."""

from .responses import CloudDirectoryResponse

url_bases = [
    r"https?://clouddirectory\.(.+)\.amazonaws\.com",
]

url_paths = {
    # Directory operations
    "{0}/amazonclouddirectory/2017-01-11/directory/create$": CloudDirectoryResponse.dispatch,
    "{0}/amazonclouddirectory/2017-01-11/directory/list$": CloudDirectoryResponse.dispatch,
    "{0}/amazonclouddirectory/2017-01-11/directory/get$": CloudDirectoryResponse.dispatch,
    "{0}/amazonclouddirectory/2017-01-11/directory/disable$": CloudDirectoryResponse.dispatch,
    "{0}/amazonclouddirectory/2017-01-11/directory/enable$": CloudDirectoryResponse.dispatch,
    "{0}/amazonclouddirectory/2017-01-11/directory$": CloudDirectoryResponse.dispatch,
    # Schema operations
    "{0}/amazonclouddirectory/2017-01-11/schema/create$": CloudDirectoryResponse.dispatch,
    "{0}/amazonclouddirectory/2017-01-11/schema/apply$": CloudDirectoryResponse.dispatch,
    "{0}/amazonclouddirectory/2017-01-11/schema/publish$": CloudDirectoryResponse.dispatch,
    "{0}/amazonclouddirectory/2017-01-11/schema/development$": CloudDirectoryResponse.dispatch,
    "{0}/amazonclouddirectory/2017-01-11/schema/published$": CloudDirectoryResponse.dispatch,
    "{0}/amazonclouddirectory/2017-01-11/schema/applied$": CloudDirectoryResponse.dispatch,
    "{0}/amazonclouddirectory/2017-01-11/schema/managed$": CloudDirectoryResponse.dispatch,
    "{0}/amazonclouddirectory/2017-01-11/schema/json$": CloudDirectoryResponse.dispatch,
    "{0}/amazonclouddirectory/2017-01-11/schema/update$": CloudDirectoryResponse.dispatch,
    "{0}/amazonclouddirectory/2017-01-11/schema/getappliedschema$": CloudDirectoryResponse.dispatch,
    "{0}/amazonclouddirectory/2017-01-11/schema/upgradeapplied$": CloudDirectoryResponse.dispatch,
    "{0}/amazonclouddirectory/2017-01-11/schema/upgradepublished$": CloudDirectoryResponse.dispatch,
    "{0}/amazonclouddirectory/2017-01-11/schema$": CloudDirectoryResponse.dispatch,
    # Facet operations
    "{0}/amazonclouddirectory/2017-01-11/facet/create$": CloudDirectoryResponse.dispatch,
    "{0}/amazonclouddirectory/2017-01-11/facet/delete$": CloudDirectoryResponse.dispatch,
    "{0}/amazonclouddirectory/2017-01-11/facet/list$": CloudDirectoryResponse.dispatch,
    "{0}/amazonclouddirectory/2017-01-11/facet/attributes$": CloudDirectoryResponse.dispatch,
    "{0}/amazonclouddirectory/2017-01-11/facet$": CloudDirectoryResponse.dispatch,
    # Object operations
    "{0}/amazonclouddirectory/2017-01-11/object$": CloudDirectoryResponse.dispatch,
    "{0}/amazonclouddirectory/2017-01-11/object/delete$": CloudDirectoryResponse.dispatch,
    "{0}/amazonclouddirectory/2017-01-11/object/attach$": CloudDirectoryResponse.dispatch,
    "{0}/amazonclouddirectory/2017-01-11/object/detach$": CloudDirectoryResponse.dispatch,
    "{0}/amazonclouddirectory/2017-01-11/object/update$": CloudDirectoryResponse.dispatch,
    "{0}/amazonclouddirectory/2017-01-11/object/information$": CloudDirectoryResponse.dispatch,
    "{0}/amazonclouddirectory/2017-01-11/object/attributes$": CloudDirectoryResponse.dispatch,
    "{0}/amazonclouddirectory/2017-01-11/object/attributes/get$": CloudDirectoryResponse.dispatch,
    "{0}/amazonclouddirectory/2017-01-11/object/children$": CloudDirectoryResponse.dispatch,
    "{0}/amazonclouddirectory/2017-01-11/object/parent$": CloudDirectoryResponse.dispatch,
    "{0}/amazonclouddirectory/2017-01-11/object/parentpaths$": CloudDirectoryResponse.dispatch,
    "{0}/amazonclouddirectory/2017-01-11/object/policy$": CloudDirectoryResponse.dispatch,
    "{0}/amazonclouddirectory/2017-01-11/object/facets$": CloudDirectoryResponse.dispatch,
    "{0}/amazonclouddirectory/2017-01-11/object/facets/delete$": CloudDirectoryResponse.dispatch,
    "{0}/amazonclouddirectory/2017-01-11/object/indices$": CloudDirectoryResponse.dispatch,
    # Policy operations
    "{0}/amazonclouddirectory/2017-01-11/policy/attach$": CloudDirectoryResponse.dispatch,
    "{0}/amazonclouddirectory/2017-01-11/policy/detach$": CloudDirectoryResponse.dispatch,
    "{0}/amazonclouddirectory/2017-01-11/policy/attachment$": CloudDirectoryResponse.dispatch,
    "{0}/amazonclouddirectory/2017-01-11/policy/lookup$": CloudDirectoryResponse.dispatch,
    # Index operations
    "{0}/amazonclouddirectory/2017-01-11/index$": CloudDirectoryResponse.dispatch,
    "{0}/amazonclouddirectory/2017-01-11/index/attach$": CloudDirectoryResponse.dispatch,
    "{0}/amazonclouddirectory/2017-01-11/index/detach$": CloudDirectoryResponse.dispatch,
    "{0}/amazonclouddirectory/2017-01-11/index/targets$": CloudDirectoryResponse.dispatch,
    # TypedLink operations
    "{0}/amazonclouddirectory/2017-01-11/typedlink/attach$": CloudDirectoryResponse.dispatch,
    "{0}/amazonclouddirectory/2017-01-11/typedlink/detach$": CloudDirectoryResponse.dispatch,
    "{0}/amazonclouddirectory/2017-01-11/typedlink/incoming$": CloudDirectoryResponse.dispatch,
    "{0}/amazonclouddirectory/2017-01-11/typedlink/outgoing$": CloudDirectoryResponse.dispatch,
    "{0}/amazonclouddirectory/2017-01-11/typedlink/attributes/get$": CloudDirectoryResponse.dispatch,
    "{0}/amazonclouddirectory/2017-01-11/typedlink/attributes/update$": CloudDirectoryResponse.dispatch,
    "{0}/amazonclouddirectory/2017-01-11/typedlink/facet/create$": CloudDirectoryResponse.dispatch,
    "{0}/amazonclouddirectory/2017-01-11/typedlink/facet/delete$": CloudDirectoryResponse.dispatch,
    "{0}/amazonclouddirectory/2017-01-11/typedlink/facet/get$": CloudDirectoryResponse.dispatch,
    "{0}/amazonclouddirectory/2017-01-11/typedlink/facet/list$": CloudDirectoryResponse.dispatch,
    "{0}/amazonclouddirectory/2017-01-11/typedlink/facet/attributes$": CloudDirectoryResponse.dispatch,
    "{0}/amazonclouddirectory/2017-01-11/typedlink/facet$": CloudDirectoryResponse.dispatch,
    # Tag operations
    "{0}/amazonclouddirectory/2017-01-11/tags/add$": CloudDirectoryResponse.dispatch,
    "{0}/amazonclouddirectory/2017-01-11/tags/remove$": CloudDirectoryResponse.dispatch,
    "{0}/amazonclouddirectory/2017-01-11/tags$": CloudDirectoryResponse.dispatch,
    # Batch operations
    "{0}/amazonclouddirectory/2017-01-11/batchread$": CloudDirectoryResponse.dispatch,
    "{0}/amazonclouddirectory/2017-01-11/batchwrite$": CloudDirectoryResponse.dispatch,
}
