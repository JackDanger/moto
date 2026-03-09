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
    "{0}/clusters/(?P<name>[^/]+)/updates$": response.dispatch,
    "{0}/clusters/(?P<name>[^/]+)/encryption-config/associate$": response.dispatch,
    "{0}/tags/(?P<resourceArn>.+)$": response.dispatch,
    # Addon routes
    "{0}/clusters/(?P<name>[^/]+)/addons$": response.dispatch,
    "{0}/clusters/(?P<name>[^/]+)/addons/(?P<addonName>[^/]+)$": response.dispatch,
    "{0}/clusters/(?P<name>[^/]+)/addons/(?P<addonName>[^/]+)/update$": response.dispatch,
    # Addon versions and configuration (global, not per-cluster)
    "{0}/addons/supported-versions$": response.dispatch,
    "{0}/addons/configuration-schemas$": response.dispatch,
    # Access entry routes
    "{0}/clusters/(?P<name>[^/]+)/access-entries$": response.dispatch,
    "{0}/clusters/(?P<name>[^/]+)/access-entries/(?P<principalArn>[^/]+)$": response.dispatch,
    # Access policy routes
    "{0}/access-policies$": response.dispatch,
    "{0}/clusters/(?P<name>[^/]+)/access-entries/(?P<principalArn>[^/]+)/access-policies$": response.dispatch,
    "{0}/clusters/(?P<name>[^/]+)/access-entries/(?P<principalArn>[^/]+)/access-policies/(?P<policyArn>.+)$": response.dispatch,
    # Pod identity association routes
    "{0}/clusters/(?P<name>[^/]+)/pod-identity-associations$": response.dispatch,
    "{0}/clusters/(?P<name>[^/]+)/pod-identity-associations/(?P<associationId>[^/]+)$": response.dispatch,
    # Identity provider config routes
    "{0}/clusters/(?P<name>[^/]+)/identity-provider-configs$": response.dispatch,
    "{0}/clusters/(?P<name>[^/]+)/identity-provider-configs/associate$": response.dispatch,
    "{0}/clusters/(?P<name>[^/]+)/identity-provider-configs/describe$": response.dispatch,
    "{0}/clusters/(?P<name>[^/]+)/identity-provider-configs/disassociate$": response.dispatch,
    # Insight routes
    "{0}/clusters/(?P<name>[^/]+)/insights$": response.dispatch,
    "{0}/clusters/(?P<name>[^/]+)/insights/(?P<id>[^/]+)$": response.dispatch,
    # Cluster versions (global)
    "{0}/cluster-versions$": response.dispatch,
    # Cluster registration/deregistration
    "{0}/cluster-registrations/(?P<name>[^/]+)$": response.dispatch,
    # EKS Anywhere subscription routes
    "{0}/eks-anywhere-subscriptions$": response.dispatch,
    "{0}/eks-anywhere-subscriptions/(?P<id>[^/]+)$": response.dispatch,
    # Capability routes
    "{0}/clusters/(?P<name>[^/]+)/capabilities$": response.dispatch,
    "{0}/clusters/(?P<name>[^/]+)/capabilities/(?P<capabilityName>[^/]+)$": response.dispatch,
}
