"""securityhub base URL and path."""

from .responses import SecurityHubResponse

url_bases = [
    r"https?://securityhub\.(.+)\.amazonaws\.com",
]

url_paths = {
    # Hub
    "{0}/accounts$": SecurityHubResponse.dispatch,
    "{0}/accounts/describe$": SecurityHubResponse.dispatch,
    # Findings
    "{0}/findings$": SecurityHubResponse.dispatch,
    "{0}/findings/import$": SecurityHubResponse.dispatch,
    "{0}/findings/batchupdate$": SecurityHubResponse.dispatch,
    "{0}/findingHistory/get$": SecurityHubResponse.dispatch,
    # Findings V2
    "{0}/findingsv2$": SecurityHubResponse.dispatch,
    "{0}/findingsv2/batchupdatev2$": SecurityHubResponse.dispatch,
    "{0}/findingsv2/statistics$": SecurityHubResponse.dispatch,
    "{0}/findingsTrendsv2$": SecurityHubResponse.dispatch,
    # Resources V2
    "{0}/resourcesv2$": SecurityHubResponse.dispatch,
    "{0}/resourcesv2/statistics$": SecurityHubResponse.dispatch,
    "{0}/resourcesTrendsv2$": SecurityHubResponse.dispatch,
    # Action Targets
    "{0}/actionTargets$": SecurityHubResponse.dispatch,
    "{0}/actionTargets/get$": SecurityHubResponse.dispatch,
    "{0}/actionTargets/(?P<ActionTargetArn>.+)$": SecurityHubResponse.dispatch,
    # Insights
    "{0}/insights$": SecurityHubResponse.dispatch,
    "{0}/insights/get$": SecurityHubResponse.dispatch,
    "{0}/insights/results/(?P<InsightArn>.+)$": SecurityHubResponse.dispatch,
    "{0}/insights/(?P<InsightArn>.+)$": SecurityHubResponse.dispatch,
    # Standards
    "{0}/standards$": SecurityHubResponse.dispatch,
    "{0}/standards/register$": SecurityHubResponse.dispatch,
    "{0}/standards/deregister$": SecurityHubResponse.dispatch,
    "{0}/standards/get$": SecurityHubResponse.dispatch,
    "{0}/standards/controls/(?P<StandardsSubscriptionArn>.+)$": SecurityHubResponse.dispatch,
    "{0}/standards/control/(?P<StandardsControlArn>.+)$": SecurityHubResponse.dispatch,
    # Standards Control Associations
    "{0}/associations$": SecurityHubResponse.dispatch,
    "{0}/associations/batchGet$": SecurityHubResponse.dispatch,
    # Automation Rules
    "{0}/automationrules/create$": SecurityHubResponse.dispatch,
    "{0}/automationrules/get$": SecurityHubResponse.dispatch,
    "{0}/automationrules/update$": SecurityHubResponse.dispatch,
    "{0}/automationrules/delete$": SecurityHubResponse.dispatch,
    "{0}/automationrules/list$": SecurityHubResponse.dispatch,
    # Automation Rules V2
    "{0}/automationrulesv2/create$": SecurityHubResponse.dispatch,
    "{0}/automationrulesv2/list$": SecurityHubResponse.dispatch,
    "{0}/automationrulesv2/(?P<Identifier>[^/]+)$": SecurityHubResponse.dispatch,
    # Finding Aggregator
    "{0}/findingAggregator/create$": SecurityHubResponse.dispatch,
    "{0}/findingAggregator/update$": SecurityHubResponse.dispatch,
    "{0}/findingAggregator/list$": SecurityHubResponse.dispatch,
    "{0}/findingAggregator/get/(?P<FindingAggregatorArn>.+)$": SecurityHubResponse.dispatch,
    "{0}/findingAggregator/delete/(?P<FindingAggregatorArn>.+)$": SecurityHubResponse.dispatch,
    # Aggregator V2
    "{0}/aggregatorv2/create$": SecurityHubResponse.dispatch,
    "{0}/aggregatorv2/list$": SecurityHubResponse.dispatch,
    "{0}/aggregatorv2/get/(?P<AggregatorV2Arn>.+)$": SecurityHubResponse.dispatch,
    "{0}/aggregatorv2/update/(?P<AggregatorV2Arn>.+)$": SecurityHubResponse.dispatch,
    "{0}/aggregatorv2/delete/(?P<AggregatorV2Arn>.+)$": SecurityHubResponse.dispatch,
    # Configuration Policies
    "{0}/configurationPolicy/create$": SecurityHubResponse.dispatch,
    "{0}/configurationPolicy/list$": SecurityHubResponse.dispatch,
    "{0}/configurationPolicy/get/(?P<Identifier>[^/]+)$": SecurityHubResponse.dispatch,
    "{0}/configurationPolicy/(?P<Identifier>[^/]+)$": SecurityHubResponse.dispatch,
    # Configuration Policy Associations
    "{0}/configurationPolicyAssociation/associate$": SecurityHubResponse.dispatch,
    "{0}/configurationPolicyAssociation/disassociate$": SecurityHubResponse.dispatch,
    "{0}/configurationPolicyAssociation/get$": SecurityHubResponse.dispatch,
    "{0}/configurationPolicyAssociation/batchget$": SecurityHubResponse.dispatch,
    "{0}/configurationPolicyAssociation/list$": SecurityHubResponse.dispatch,
    # Security Controls
    "{0}/securityControls/batchGet$": SecurityHubResponse.dispatch,
    "{0}/securityControl/update$": SecurityHubResponse.dispatch,
    "{0}/securityControl/definition$": SecurityHubResponse.dispatch,
    "{0}/securityControls/definitions$": SecurityHubResponse.dispatch,
    # Products
    "{0}/products$": SecurityHubResponse.dispatch,
    "{0}/productsV2$": SecurityHubResponse.dispatch,
    "{0}/productSubscriptions$": SecurityHubResponse.dispatch,
    "{0}/productSubscriptions/(?P<ProductSubscriptionArn>.+)$": SecurityHubResponse.dispatch,
    # Organization
    "{0}/organization/admin$": SecurityHubResponse.dispatch,
    "{0}/organization/admin/enable$": SecurityHubResponse.dispatch,
    "{0}/organization/admin/disable$": SecurityHubResponse.dispatch,
    "{0}/organization/configuration$": SecurityHubResponse.dispatch,
    # Administrator / Master
    "{0}/administrator$": SecurityHubResponse.dispatch,
    "{0}/administrator/disassociate$": SecurityHubResponse.dispatch,
    "{0}/master$": SecurityHubResponse.dispatch,
    "{0}/master/disassociate$": SecurityHubResponse.dispatch,
    # Members
    "{0}/members$": SecurityHubResponse.dispatch,
    "{0}/members/get$": SecurityHubResponse.dispatch,
    "{0}/members/delete$": SecurityHubResponse.dispatch,
    "{0}/members/disassociate$": SecurityHubResponse.dispatch,
    "{0}/members/invite$": SecurityHubResponse.dispatch,
    # Invitations
    "{0}/invitations$": SecurityHubResponse.dispatch,
    "{0}/invitations/count$": SecurityHubResponse.dispatch,
    "{0}/invitations/decline$": SecurityHubResponse.dispatch,
    "{0}/invitations/delete$": SecurityHubResponse.dispatch,
    # Hub V2
    "{0}/hubv2$": SecurityHubResponse.dispatch,
    # Connector V2
    "{0}/connectorsv2$": SecurityHubResponse.dispatch,
    "{0}/connectorsv2/register$": SecurityHubResponse.dispatch,
    "{0}/connectorsv2/(?P<ConnectorId>.+)$": SecurityHubResponse.dispatch,
    # Tickets V2
    "{0}/ticketsv2$": SecurityHubResponse.dispatch,
    # Tags
    "{0}/tags/(?P<ResourceArn>.+)$": SecurityHubResponse.dispatch,
}
