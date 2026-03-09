from .responses import EKSResponse

url_bases = [
    r"https?://eks\.(.+)\.amazonaws.com",
]


response = EKSResponse()


url_paths = {
    "{0}/clusters$": response.dispatch,
    "{0}/clusters/(?P<name>[^/]+)$": response.dispatch,
    "{0}/clusters/(?P<name>[^/]+)/node-groups$": response.dispatch,
    "{0}/clusters/(?P<name>[^/]+)/node-groups/(?P<nodegroupName>[^/]+)$": response.dispatch,
    "{0}/clusters/(?P<name>[^/]+)/node-groups/(?P<nodegroupName>[^/]+)/update-config$": response.dispatch,
    "{0}/clusters/(?P<name>[^/]+)/fargate-profiles$": response.dispatch,
    "{0}/clusters/(?P<name>[^/]+)/fargate-profiles/(?P<fargateProfileName>[^/]+)$": response.dispatch,
    "{0}/clusters/(?P<name>[^/]+)/update-config$": response.dispatch,
    "{0}/tags/(?P<resourceArn>.+)$": response.dispatch,
    # Addon routes
    "{0}/clusters/(?P<name>[^/]+)/addons$": response.dispatch,
    "{0}/clusters/(?P<name>[^/]+)/addons/(?P<addonName>[^/]+)$": response.dispatch,
    # Addon versions (global, not per-cluster)
    "{0}/addons/supported-versions$": response.dispatch,
    # Access entry routes
    "{0}/clusters/(?P<name>[^/]+)/access-entries$": response.dispatch,
    "{0}/clusters/(?P<name>[^/]+)/access-entries/(?P<principalArn>[^/]+)$": response.dispatch,
    # Access policy routes
    "{0}/clusters/(?P<name>[^/]+)/access-entries/(?P<principalArn>[^/]+)/access-policies$": response.dispatch,
    "{0}/clusters/(?P<name>[^/]+)/access-entries/(?P<principalArn>[^/]+)/access-policies/(?P<policyArn>.+)$": response.dispatch,
    # Pod identity association routes
    "{0}/clusters/(?P<name>[^/]+)/pod-identity-associations$": response.dispatch,
    "{0}/clusters/(?P<name>[^/]+)/pod-identity-associations/(?P<associationId>[^/]+)$": response.dispatch,
}
