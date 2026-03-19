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
    "{0}/2020-05-31/distribution/(?P<distribution_id>[^/]+)/invalidation$": CloudFrontResponse.dispatch,
    "{0}/2020-05-31/distribution/(?P<distribution_id>[^/]+)/invalidation/(?P<invalidation_id>[^/]+)$": CloudFrontResponse.dispatch,
    "{0}/2020-05-31/distribution/(?P<distribution_id>[^/]+)/associate-alias$": CloudFrontResponse.dispatch,
    "{0}/2020-05-31/distribution/(?P<distribution_id>[^/]+)/associate-web-acl$": CloudFrontResponse.dispatch,
    "{0}/2020-05-31/distribution/(?P<distribution_id>[^/]+)/disassociate-web-acl$": CloudFrontResponse.dispatch,
    "{0}/2020-05-31/distribution/(?P<distribution_id>[^/]+)/copy$": CloudFrontResponse.dispatch,
    "{0}/2020-05-31/distribution/(?P<distribution_id>[^/]+)/promote-staging-config$": CloudFrontResponse.dispatch,
    # Distributions by WebACL
    "{0}/2020-05-31/distributionsByWebACLId/(?P<web_acl_id>[^/]+)$": CloudFrontResponse.dispatch,
    # Distributions by cache policy
    "{0}/2020-05-31/distributionsByCachePolicyId/(?P<cache_policy_id>[^/]+)$": CloudFrontResponse.dispatch,
    # Distributions by origin request policy
    "{0}/2020-05-31/distributionsByOriginRequestPolicyId/(?P<policy_id>[^/]+)$": CloudFrontResponse.dispatch,
    # Distributions by response headers policy
    "{0}/2020-05-31/distributionsByResponseHeadersPolicyId/(?P<policy_id>[^/]+)$": CloudFrontResponse.dispatch,
    # Distributions by key group
    "{0}/2020-05-31/distributionsByKeyGroupId/(?P<key_group_id>[^/]+)$": CloudFrontResponse.dispatch,
    # Distributions by realtime log config
    "{0}/2020-05-31/distributionsByRealtimeLogConfig$": CloudFrontResponse.dispatch,
    # Distributions by anycast IP list
    "{0}/2020-05-31/distributionsByAnycastIpListId/(?P<list_id>[^/]+)$": CloudFrontResponse.dispatch,
    # Distributions by VPC origin
    "{0}/2020-05-31/distributionsByVpcOriginId/(?P<vpc_origin_id>[^/]+)$": CloudFrontResponse.dispatch,
    # Distributions by connection mode
    "{0}/2020-05-31/distributionsByConnectionMode/(?P<mode>[^/]+)$": CloudFrontResponse.dispatch,
    # Distributions by connection function
    "{0}/2020-05-31/distributionsByConnectionFunction$": CloudFrontResponse.dispatch,
    # Distributions by owned resource
    "{0}/2020-05-31/distributionsByOwnedResource/(?P<resource_id>[^/]+)$": CloudFrontResponse.dispatch,
    # Distributions by trust store
    "{0}/2020-05-31/distributionsByTrustStore$": CloudFrontResponse.dispatch,
    # Key groups
    "{0}/2020-05-31/key-group$": CloudFrontResponse.dispatch,
    "{0}/2020-05-31/key-group/(?P<key_name>[^/]+)$": CloudFrontResponse.dispatch,
    "{0}/2020-05-31/key-group/(?P<key_name>[^/]+)/config$": CloudFrontResponse.dispatch,
    # Tags
    "{0}/2020-05-31/tagging$": CloudFrontResponse.dispatch,
    # Origin Access Controls

    "{0}/2020-05-31/origin-access-control$": CloudFrontResponse.dispatch,
    "{0}/2020-05-31/origin-access-control/(?P<oac_id>[^/]+)$": CloudFrontResponse.dispatch,
    "{0}/2020-05-31/origin-access-control/(?P<oac_id>[^/]+)/config$": CloudFrontResponse.dispatch,
    # Origin Access Identities (legacy)
    "{0}/2020-05-31/origin-access-identity/cloudfront$": CloudFrontResponse.dispatch,
    "{0}/2020-05-31/origin-access-identity/cloudfront/(?P<identity_id>[^/]+)$": CloudFrontResponse.dispatch,
    "{0}/2020-05-31/origin-access-identity/cloudfront/(?P<identity_id>[^/]+)/config$": CloudFrontResponse.dispatch,
    # Public keys
    "{0}/2020-05-31/public-key$": CloudFrontResponse.dispatch,
    "{0}/2020-05-31/public-key/(?P<key_name>[^/]+)$": CloudFrontResponse.dispatch,
    "{0}/2020-05-31/public-key/(?P<key_name>[^/]+)/config$": CloudFrontResponse.dispatch,
    # Functions
    "{0}/2020-05-31/function$": CloudFrontResponse.dispatch,
    "{0}/2020-05-31/function/(?P<function_name>[^/]+)$": CloudFrontResponse.dispatch,
    "{0}/2020-05-31/function/(?P<function_name>[^/]+)/describe$": CloudFrontResponse.dispatch,
    "{0}/2020-05-31/function/(?P<function_name>[^/]+)/publish$": CloudFrontResponse.dispatch,
    "{0}/2020-05-31/function/(?P<function_name>[^/]+)/test$": CloudFrontResponse.dispatch,
    # Cache policies
    "{0}/2020-05-31/cache-policy$": CloudFrontResponse.dispatch,
    "{0}/2020-05-31/cache-policy/(?P<policy_id>[^/]+)$": CloudFrontResponse.dispatch,
    "{0}/2020-05-31/cache-policy/(?P<policy_id>[^/]+)/config$": CloudFrontResponse.dispatch,
    # Response headers policies
    "{0}/2020-05-31/response-headers-policy$": CloudFrontResponse.dispatch,
    "{0}/2020-05-31/response-headers-policy/(?P<policy_id>[^/]+)$": CloudFrontResponse.dispatch,
    "{0}/2020-05-31/response-headers-policy/(?P<policy_id>[^/]+)/config$": CloudFrontResponse.dispatch,
    # Origin request policies
    "{0}/2020-05-31/origin-request-policy$": CloudFrontResponse.dispatch,
    "{0}/2020-05-31/origin-request-policy/(?P<policy_id>[^/]+)$": CloudFrontResponse.dispatch,
    "{0}/2020-05-31/origin-request-policy/(?P<policy_id>[^/]+)/config$": CloudFrontResponse.dispatch,
    # Field Level Encryption
    "{0}/2020-05-31/field-level-encryption$": CloudFrontResponse.dispatch,
    "{0}/2020-05-31/field-level-encryption/(?P<config_id>[^/]+)$": CloudFrontResponse.dispatch,
    "{0}/2020-05-31/field-level-encryption/(?P<config_id>[^/]+)/config$": CloudFrontResponse.dispatch,
    # Field Level Encryption Profiles
    "{0}/2020-05-31/field-level-encryption-profile$": CloudFrontResponse.dispatch,
    "{0}/2020-05-31/field-level-encryption-profile/(?P<profile_id>[^/]+)$": CloudFrontResponse.dispatch,
    "{0}/2020-05-31/field-level-encryption-profile/(?P<profile_id>[^/]+)/config$": CloudFrontResponse.dispatch,
    # Streaming Distributions
    "{0}/2020-05-31/streaming-distribution$": CloudFrontResponse.dispatch,
    "{0}/2020-05-31/streaming-distribution/(?P<dist_id>[^/]+)$": CloudFrontResponse.dispatch,
    "{0}/2020-05-31/streaming-distribution/(?P<dist_id>[^/]+)/config$": CloudFrontResponse.dispatch,
    # Continuous Deployment Policies
    "{0}/2020-05-31/continuous-deployment-policy$": CloudFrontResponse.dispatch,
    "{0}/2020-05-31/continuous-deployment-policy/(?P<policy_id>[^/]+)$": CloudFrontResponse.dispatch,
    "{0}/2020-05-31/continuous-deployment-policy/(?P<policy_id>[^/]+)/config$": CloudFrontResponse.dispatch,
    # Monitoring Subscriptions
    "{0}/2020-05-31/distributions/(?P<dist_id>[^/]+)/monitoring-subscription$": CloudFrontResponse.dispatch,
    # Realtime Log Configs (POST body-based operations use dedicated paths)
    "{0}/2020-05-31/realtime-log-config$": CloudFrontResponse.dispatch,
    "{0}/2020-05-31/get-realtime-log-config$": CloudFrontResponse.dispatch,
    "{0}/2020-05-31/delete-realtime-log-config$": CloudFrontResponse.dispatch,
    # Key Value Stores
    "{0}/2020-05-31/key-value-store$": CloudFrontResponse.dispatch,
    "{0}/2020-05-31/key-value-store/(?P<store_name>[^/]+)$": CloudFrontResponse.dispatch,
    # Conflicting aliases
    "{0}/2020-05-31/conflicting-alias$": CloudFrontResponse.dispatch,
    # VPC Origins
    "{0}/2020-05-31/vpc-origin$": CloudFrontResponse.dispatch,
    "{0}/2020-05-31/vpc-origin/(?P<vpc_origin_id>[^/]+)$": CloudFrontResponse.dispatch,
    # Trust Stores
    "{0}/2020-05-31/trust-store$": CloudFrontResponse.dispatch,
    "{0}/2020-05-31/trust-store/(?P<store_id>[^/]+)$": CloudFrontResponse.dispatch,
    "{0}/2020-05-31/trust-stores$": CloudFrontResponse.dispatch,
    # Resource Policies (POST-based)
    "{0}/2020-05-31/get-resource-policy$": CloudFrontResponse.dispatch,
    "{0}/2020-05-31/put-resource-policy$": CloudFrontResponse.dispatch,
    "{0}/2020-05-31/delete-resource-policy$": CloudFrontResponse.dispatch,
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
    "{0}/2020-05-31/distribution-tenant/(?P<tenant_id>[^/]+)/associate-web-acl$": CloudFrontResponse.dispatch,
    "{0}/2020-05-31/distribution-tenant/(?P<tenant_id>[^/]+)/disassociate-web-acl$": CloudFrontResponse.dispatch,
    "{0}/2020-05-31/distribution-tenant/(?P<tenant_id>[^/]+)/invalidation$": CloudFrontResponse.dispatch,
    "{0}/2020-05-31/distribution-tenant/(?P<tenant_id>[^/]+)/invalidation/(?P<inv_id>[^/]+)$": CloudFrontResponse.dispatch,
    "{0}/2020-05-31/distribution-tenants$": CloudFrontResponse.dispatch,
    "{0}/2020-05-31/distribution-tenants-by-customization$": CloudFrontResponse.dispatch,
    # Domain operations
    "{0}/2020-05-31/domain-association$": CloudFrontResponse.dispatch,
    "{0}/2020-05-31/domain-conflicts$": CloudFrontResponse.dispatch,
    # Managed certificate
    "{0}/2020-05-31/managed-certificate/(?P<cert_id>[^/]+)$": CloudFrontResponse.dispatch,
    # DNS verification
    "{0}/2020-05-31/verify-dns-configuration$": CloudFrontResponse.dispatch,
}
