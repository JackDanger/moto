"""cloudfront base URL and path."""

from .responses import CloudFrontResponse

url_bases = [
    r"https?://cloudfront\.amazonaws\.com",
    r"https?://cloudfront\.(.+)\.amazonaws\.com",
]
url_paths = {
    # Distributions
    "{0}/2020-05-31/distribution$": CloudFrontResponse.dispatch,
    "{0}/2020-05-31/distribution/(?P<distribution_id>[^/]+)$": CloudFrontResponse.dispatch,
    "{0}/2020-05-31/distribution/(?P<distribution_id>[^/]+)/config$": CloudFrontResponse.dispatch,
    "{0}/2020-05-31/distribution/(?P<distribution_id>[^/]+)/invalidation": CloudFrontResponse.dispatch,
    "{0}/2020-05-31/distribution/(?P<distribution_id>[^/]+)/invalidation/(?P<invalidation_id>[^/]+)": CloudFrontResponse.dispatch,
    # Key groups
    "{0}/2020-05-31/key-group$": CloudFrontResponse.dispatch,
    "{0}/2020-05-31/key-group/(?P<key_name>[^/]+)$": CloudFrontResponse.dispatch,
    # Tags
    "{0}/2020-05-31/tagging$": CloudFrontResponse.dispatch,
    # Origin Access Controls
    "{0}/2020-05-31/origin-access-control$": CloudFrontResponse.dispatch,
    "{0}/2020-05-31/origin-access-control/(?P<oac_id>[^/]+)$": CloudFrontResponse.dispatch,
    "{0}/2020-05-31/origin-access-control/(?P<oac_id>[^/]+)/config$": CloudFrontResponse.dispatch,
    # Public keys
    "{0}/2020-05-31/public-key$": CloudFrontResponse.dispatch,
    "{0}/2020-05-31/public-key/(?P<key_name>[^/]+)$": CloudFrontResponse.dispatch,
    # VPC Origins
    "{0}/2020-05-31/vpc-origin$": CloudFrontResponse.dispatch,
    "{0}/2020-05-31/vpc-origin/(?P<vpc_origin_id>[^/]+)$": CloudFrontResponse.dispatch,
    # Trust Stores
    "{0}/2020-05-31/trust-store$": CloudFrontResponse.dispatch,
    "{0}/2020-05-31/trust-store/(?P<store_id>[^/]+)$": CloudFrontResponse.dispatch,
    "{0}/2020-05-31/trust-stores$": CloudFrontResponse.dispatch,
    # Anycast IP Lists
    "{0}/2020-05-31/anycast-ip-list$": CloudFrontResponse.dispatch,
    "{0}/2020-05-31/anycast-ip-list/(?P<list_id>[^/]+)$": CloudFrontResponse.dispatch,
    # Connection Groups
    "{0}/2020-05-31/connection-group$": CloudFrontResponse.dispatch,
    "{0}/2020-05-31/connection-group/(?P<group_id>[^/]+)$": CloudFrontResponse.dispatch,
    "{0}/2020-05-31/connection-groups$": CloudFrontResponse.dispatch,
    # Connection Functions
    "{0}/2020-05-31/connection-function$": CloudFrontResponse.dispatch,
    "{0}/2020-05-31/connection-function/(?P<func_name>[^/]+)$": CloudFrontResponse.dispatch,
    "{0}/2020-05-31/connection-function/(?P<func_name>[^/]+)/describe$": CloudFrontResponse.dispatch,
    "{0}/2020-05-31/connection-function/(?P<func_name>[^/]+)/publish$": CloudFrontResponse.dispatch,
    "{0}/2020-05-31/connection-function/(?P<func_name>[^/]+)/test$": CloudFrontResponse.dispatch,
    "{0}/2020-05-31/connection-functions$": CloudFrontResponse.dispatch,
    # Distribution Tenants
    "{0}/2020-05-31/distribution-tenant$": CloudFrontResponse.dispatch,
    "{0}/2020-05-31/distribution-tenant/(?P<tenant_id>[^/]+)$": CloudFrontResponse.dispatch,
    "{0}/2020-05-31/distribution-tenant/(?P<tenant_id>[^/]+)/invalidation$": CloudFrontResponse.dispatch,
    "{0}/2020-05-31/distribution-tenant/(?P<tenant_id>[^/]+)/invalidation/(?P<inv_id>[^/]+)$": CloudFrontResponse.dispatch,
    "{0}/2020-05-31/distribution-tenants$": CloudFrontResponse.dispatch,
    "{0}/2020-05-31/distribution-tenants-by-customization$": CloudFrontResponse.dispatch,
    # Resource Policies
    "{0}/2020-05-31/get-resource-policy$": CloudFrontResponse.dispatch,
    "{0}/2020-05-31/put-resource-policy$": CloudFrontResponse.dispatch,
    "{0}/2020-05-31/delete-resource-policy$": CloudFrontResponse.dispatch,
    # Distributions by various criteria
    "{0}/2020-05-31/distributionsByVpcOriginId/(?P<vpc_origin_id>[^/]+)$": CloudFrontResponse.dispatch,
    "{0}/2020-05-31/distributionsByAnycastIpListId/(?P<list_id>[^/]+)$": CloudFrontResponse.dispatch,
    "{0}/2020-05-31/distributionsByTrustStore$": CloudFrontResponse.dispatch,
    "{0}/2020-05-31/distributionsByConnectionFunction$": CloudFrontResponse.dispatch,
    "{0}/2020-05-31/distributionsByOwnedResource/(?P<resource_id>[^/]+)$": CloudFrontResponse.dispatch,
    # Domain operations
    "{0}/2020-05-31/domain-association$": CloudFrontResponse.dispatch,
    "{0}/2020-05-31/domain-conflicts$": CloudFrontResponse.dispatch,
    # DNS verification
    "{0}/2020-05-31/verify-dns-configuration$": CloudFrontResponse.dispatch,
    # Managed certificate
    "{0}/2020-05-31/managed-certificate/(?P<cert_id>[^/]+)$": CloudFrontResponse.dispatch,
}
