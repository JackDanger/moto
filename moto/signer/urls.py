"""signer base URL and path."""

from .responses import SignerResponse

url_bases = [
    r"https?://signer\.(.+)\.amazonaws\.com",
]

url_paths = {
    "{0}/tags/(?P<profile_arn>[^/]+)$": SignerResponse.dispatch,
    "{0}/tags/(?P<arn_prefix>[^/]+)/signing-profiles/(?P<profile_name>[^/]+)$": SignerResponse.dispatch,
    "{0}/signing-profiles$": SignerResponse.dispatch,
    "{0}/signing-profiles/(?P<profile_name>[^/]+)$": SignerResponse.dispatch,
    "{0}/signing-profiles/(?P<profile_name>[^/]+)/revoke$": SignerResponse.dispatch,
    "{0}/signing-profiles/(?P<profile_name>[^/]+)/permissions$": SignerResponse.dispatch,
    "{0}/signing-profiles/(?P<profile_name>[^/]+)/permissions/(?P<statement_id>[^/]+)$": SignerResponse.dispatch,
    "{0}/signing-platforms$": SignerResponse.dispatch,
    "{0}/signing-platforms/(?P<platform_id>[^/]+)$": SignerResponse.dispatch,
    "{0}/signing-jobs$": SignerResponse.dispatch,
    "{0}/signing-jobs/with-payload$": SignerResponse.dispatch,
    "{0}/signing-jobs/(?P<job_id>[^/]+)$": SignerResponse.dispatch,
    "{0}/signing-jobs/(?P<job_id>[^/]+)/revoke$": SignerResponse.dispatch,
    "{0}/revocations$": SignerResponse.dispatch,
}
