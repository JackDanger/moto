from moto.opensearch.responses import OpenSearchServiceResponse

url_bases = [
    r"https?://es\.(.+)\.amazonaws\.com",
]


url_paths = {
    # ---- ES 2015-01-01 explicit routes ----
    # Domain CRUD
    "{0}/2015-01-01/domain$": OpenSearchServiceResponse.list_domains,
    "{0}/2015-01-01/es/domain$": OpenSearchServiceResponse.domains,
    "{0}/2015-01-01/es/domain/(?P<domainname>[^/]+)/config$": OpenSearchServiceResponse.domain_config,
    "{0}/2015-01-01/es/domain/(?P<domainname>[^/]+)/autoTunes$": OpenSearchServiceResponse.domain_auto_tunes,
    "{0}/2015-01-01/es/domain/(?P<domainname>[^/]+)/progress$": OpenSearchServiceResponse.domain_change_progress,
    "{0}/2015-01-01/es/domain/(?P<domainname>[^/]+)/dryRun$": OpenSearchServiceResponse.dry_run_progress,
    "{0}/2015-01-01/es/domain/(?P<domainname>[^/]+)/packages$": OpenSearchServiceResponse.list_packages_for_domain_route,
    "{0}/2015-01-01/domain/(?P<domainname>[^/]+)/packages$": OpenSearchServiceResponse.list_packages_for_domain_route,
    "{0}/2015-01-01/es/domain/(?P<domainname>[^/]+)/vpcEndpoints$": OpenSearchServiceResponse.vpc_endpoints_for_domain,
    "{0}/2015-01-01/es/domain/(?P<domainname>[^/]+)$": OpenSearchServiceResponse.domain,
    "{0}/2015-01-01/es/domain-info$": OpenSearchServiceResponse.list_domains,
    # Tags
    "{0}/2015-01-01/tags/?$": OpenSearchServiceResponse.tags,
    "{0}/2015-01-01/tags-removal/?$": OpenSearchServiceResponse.tag_removal,
    # Compatible versions
    "{0}/2015-01-01/es/compatibleVersions$": OpenSearchServiceResponse.compatible_versions,
    # Packages
    "{0}/2015-01-01/packages$": OpenSearchServiceResponse.packages_route,
    "{0}/2015-01-01/packages/describe$": OpenSearchServiceResponse.packages_describe,
    "{0}/2015-01-01/packages/update$": OpenSearchServiceResponse.package_by_id,
    "{0}/2015-01-01/packages/(?P<pkgid>[^/]+)$": OpenSearchServiceResponse.package_by_id,
    "{0}/2015-01-01/packages/(?P<pkgid>[^/]+)/history$": OpenSearchServiceResponse.package_history,
    "{0}/2015-01-01/packages/associate/(?P<pkgid>[^/]+)/(?P<domainname>[^/]+)$": OpenSearchServiceResponse.associate_package_route,
    "{0}/2015-01-01/packages/dissociate/(?P<pkgid>[^/]+)/(?P<domainname>[^/]+)$": OpenSearchServiceResponse.dissociate_package_route,
    "{0}/2015-01-01/packages/(?P<pkgid>[^/]+)/domains$": OpenSearchServiceResponse.list_domains_for_package_route,
    # VPC Endpoints
    "{0}/2015-01-01/es/vpcEndpoints$": OpenSearchServiceResponse.vpc_endpoints_route,
    "{0}/2015-01-01/es/vpcEndpoints/describe$": OpenSearchServiceResponse.vpc_endpoints_describe,
    "{0}/2015-01-01/es/vpcEndpoints/update$": OpenSearchServiceResponse.vpc_endpoints_update,
    "{0}/2015-01-01/es/vpcEndpoints/(?P<vpce_id>[^/]+)$": OpenSearchServiceResponse.vpc_endpoint_by_id,
    # Connections
    "{0}/2015-01-01/es/ccs/outboundConnection$": OpenSearchServiceResponse.outbound_connection_route,
    "{0}/2015-01-01/es/ccs/outboundConnection/search$": OpenSearchServiceResponse.outbound_connection_search,
    "{0}/2015-01-01/es/ccs/outboundConnection/(?P<conn_id>[^/]+)$": OpenSearchServiceResponse.outbound_connection_by_id,
    "{0}/2015-01-01/es/ccs/inboundConnection/search$": OpenSearchServiceResponse.inbound_connection_search,
    "{0}/2015-01-01/es/ccs/inboundConnection/(?P<conn_id>[^/]+)/accept$": OpenSearchServiceResponse.inbound_connection_accept,
    "{0}/2015-01-01/es/ccs/inboundConnection/(?P<conn_id>[^/]+)$": OpenSearchServiceResponse.inbound_connection_by_id,
    # Reserved Instances
    "{0}/2015-01-01/es/reservedInstanceOfferings$": OpenSearchServiceResponse.reserved_instance_offerings_route,
    "{0}/2015-01-01/es/reservedInstances$": OpenSearchServiceResponse.reserved_instances_route,
    "{0}/2015-01-01/es/purchaseReservedInstanceOffering$": OpenSearchServiceResponse.purchase_reserved_instance_route,
    # Upgrade and service software update
    "{0}/2015-01-01/es/upgradeDomain$": OpenSearchServiceResponse.es_upgrade_domain_route,
    "{0}/2015-01-01/es/upgradeDomain/(?P<domainname>[^/]+)/history$": OpenSearchServiceResponse.es_upgrade_history_route,
    "{0}/2015-01-01/es/upgradeDomain/(?P<domainname>[^/]+)/status$": OpenSearchServiceResponse.es_upgrade_status_route,
    "{0}/2015-01-01/es/serviceSoftwareUpdate/cancel$": OpenSearchServiceResponse.es_service_software_cancel_route,
    "{0}/2015-01-01/es/serviceSoftwareUpdate/start$": OpenSearchServiceResponse.es_service_software_start_route,
    # VPC endpoint access
    "{0}/2015-01-01/es/domain/(?P<domainname>[^/]+)/listVpcEndpointAccess$": OpenSearchServiceResponse.es_list_vpc_endpoint_access_route,
    "{0}/2015-01-01/es/domain/(?P<domainname>[^/]+)/authorizeVpcEndpointAccess$": OpenSearchServiceResponse.es_authorize_vpc_endpoint_access_route,
    "{0}/2015-01-01/es/domain/(?P<domainname>[^/]+)/revokeVpcEndpointAccess$": OpenSearchServiceResponse.es_revoke_vpc_endpoint_access_route,
    # Domain config cancel
    "{0}/2015-01-01/es/domain/(?P<domainname>[^/]+)/config/cancel$": OpenSearchServiceResponse.es_cancel_domain_config_change_route,
    # Inbound connection reject
    "{0}/2015-01-01/es/ccs/inboundConnection/(?P<conn_id>[^/]+)/reject$": OpenSearchServiceResponse.es_reject_inbound_connection_route,
    # Versions & Instance Types
    "{0}/2015-01-01/es/versions$": OpenSearchServiceResponse.es_versions_route,
    "{0}/2015-01-01/es/instanceTypes/(?P<version>[^/]+)$": OpenSearchServiceResponse.es_instance_types_route,
    "{0}/2015-01-01/es/instanceTypeLimits/(?P<version>[^/]+)/(?P<itype>[^/]+)$": OpenSearchServiceResponse.instance_type_limits_route,
    # ---- OpenSearch 2021-01-01 catch-all (dispatch uses botocore model) ----
    "{0}/2021-01-01/.*$": OpenSearchServiceResponse.dispatch,
}
