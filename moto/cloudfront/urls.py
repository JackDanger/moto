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
    "{0}/2020-05-31/distribution/(?P<distribution_id>[^/]+)/associate-alias$": CloudFrontResponse.dispatch,
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
    # Key groups
    "{0}/2020-05-31/key-group$": CloudFrontResponse.dispatch,
    "{0}/2020-05-31/key-group/(?P<key_name>[^/]+)$": CloudFrontResponse.dispatch,
    "{0}/2020-05-31/key-group/(?P<key_name>[^/]+)/config$": CloudFrontResponse.dispatch,
    # Tags
    "{0}/2020-05-31/tagging$": CloudFrontResponse.tagging,
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
    # Realtime Log Configs
    "{0}/2020-05-31/realtime-log-config$": CloudFrontResponse.dispatch,
    # Key Value Stores
    "{0}/2020-05-31/key-value-store$": CloudFrontResponse.dispatch,
    "{0}/2020-05-31/key-value-store/(?P<store_name>[^/]+)$": CloudFrontResponse.dispatch,
    # Conflicting aliases
    "{0}/2020-05-31/conflicting-alias$": CloudFrontResponse.dispatch,
}
