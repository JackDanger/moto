"""signer base URL and path."""

from .responses import SignerResponse

url_bases = [
    r"https?://signer\.(.+)\.amazonaws\.com",
]

response = SignerResponse()

url_paths = {
    "{0}/tags/(?P<profile_arn>[^/]+)$": response.tags,
    "{0}/tags/(?P<arn_prefix>[^/]+)/signing-profiles/(?P<profile_name>[^/]+)$": response.tags,
    "{0}/signing-profiles$": response.signing_profiles,
    "{0}/signing-profiles/(?P<profile_name>[^/]+)$": response.signing_profile,
    "{0}/signing-profiles/(?P<profile_name>[^/]+)/revoke$": response.signing_profile_revoke,
    "{0}/signing-profiles/(?P<profile_name>[^/]+)/permissions$": response.profile_permissions,
    "{0}/signing-profiles/(?P<profile_name>[^/]+)/permissions/(?P<statement_id>[^/]+)$": response.profile_permission,
    "{0}/signing-platforms$": SignerResponse.dispatch,
    "{0}/signing-platforms/(?P<platform_id>[^/]+)$": response.signing_platform,
    "{0}/signing-jobs$": response.signing_jobs,
    "{0}/signing-jobs/with-payload$": response.sign_payload,
    "{0}/signing-jobs/(?P<job_id>[^/]+)$": response.signing_job,
    "{0}/signing-jobs/(?P<job_id>[^/]+)/revoke$": response.signing_job_revoke,
    "{0}/revocations$": response.revocations,
}
