from .responses import ConnectResponse

url_bases = [
    r"https?://connect\.(.+)\.amazonaws\.com",
]

url_paths = {
    # Instance
    "{0}/instance$": ConnectResponse.dispatch,
    "{0}/instance/(?P<InstanceId>[^/]+)$": ConnectResponse.dispatch,
    # Instance attribute
    "{0}/instance/(?P<InstanceId>[^/]+)/attribute/(?P<AttributeType>[^/]+)$": ConnectResponse.dispatch,
    # Instance storage config (placeholder for DescribeInstanceStorageConfig)
    "{0}/instance/(?P<InstanceId>[^/]+)/storage-config/(?P<AssociationId>[^/]+)$": ConnectResponse.dispatch,
    # Analytics data associations
    "{0}/analytics-data/instance/(?P<InstanceId>[^/]+)/association$": ConnectResponse.dispatch,
    # Agent status
    "{0}/agent-status/(?P<InstanceId>[^/]+)$": ConnectResponse.dispatch,
    "{0}/agent-status/(?P<InstanceId>[^/]+)/(?P<AgentStatusId>[^/]+)$": ConnectResponse.dispatch,
    # Contact flows
    "{0}/contact-flows/(?P<InstanceId>[^/]+)$": ConnectResponse.dispatch,
    "{0}/contact-flows/(?P<InstanceId>[^/]+)/(?P<ContactFlowId>[^/]+)$": ConnectResponse.dispatch,
    # Contact flow modules
    "{0}/contact-flow-modules/(?P<InstanceId>[^/]+)$": ConnectResponse.dispatch,
    "{0}/contact-flow-modules/(?P<InstanceId>[^/]+)/(?P<ContactFlowModuleId>[^/]+)$": ConnectResponse.dispatch,
    # Evaluation forms
    "{0}/evaluation-forms/(?P<InstanceId>[^/]+)$": ConnectResponse.dispatch,
    "{0}/evaluation-forms/(?P<InstanceId>[^/]+)/(?P<EvaluationFormId>[^/]+)$": ConnectResponse.dispatch,
    # Hours of operation
    "{0}/hours-of-operations/(?P<InstanceId>[^/]+)$": ConnectResponse.dispatch,
    "{0}/hours-of-operations/(?P<InstanceId>[^/]+)/(?P<HoursOfOperationId>[^/]+)$": ConnectResponse.dispatch,
    # Phone number
    "{0}/phone-number/(?P<PhoneNumberId>[^/]+)$": ConnectResponse.dispatch,
    # Prompts
    "{0}/prompts/(?P<InstanceId>[^/]+)$": ConnectResponse.dispatch,
    "{0}/prompts/(?P<InstanceId>[^/]+)/(?P<PromptId>[^/]+)$": ConnectResponse.dispatch,
    # Queues
    "{0}/queues/(?P<InstanceId>[^/]+)$": ConnectResponse.dispatch,
    "{0}/queues/(?P<InstanceId>[^/]+)/(?P<QueueId>[^/]+)$": ConnectResponse.dispatch,
    # Quick connects
    "{0}/quick-connects/(?P<InstanceId>[^/]+)$": ConnectResponse.dispatch,
    "{0}/quick-connects/(?P<InstanceId>[^/]+)/(?P<QuickConnectId>[^/]+)$": ConnectResponse.dispatch,
    # Routing profiles
    "{0}/routing-profiles/(?P<InstanceId>[^/]+)$": ConnectResponse.dispatch,
    "{0}/routing-profiles/(?P<InstanceId>[^/]+)/(?P<RoutingProfileId>[^/]+)$": ConnectResponse.dispatch,
    # Rules
    "{0}/rules/(?P<InstanceId>[^/]+)$": ConnectResponse.dispatch,
    "{0}/rules/(?P<InstanceId>[^/]+)/(?P<RuleId>[^/]+)$": ConnectResponse.dispatch,
    # Security profiles
    "{0}/security-profiles/(?P<InstanceId>[^/]+)$": ConnectResponse.dispatch,
    "{0}/security-profiles/(?P<InstanceId>[^/]+)/(?P<SecurityProfileId>[^/]+)$": ConnectResponse.dispatch,
    # Traffic distribution group
    "{0}/traffic-distribution-group$": ConnectResponse.dispatch,
    "{0}/traffic-distribution-group/(?P<TrafficDistributionGroupId>[^/]+)$": ConnectResponse.dispatch,
    # Users
    "{0}/users/(?P<InstanceId>[^/]+)$": ConnectResponse.dispatch,
    "{0}/users/(?P<InstanceId>[^/]+)/(?P<UserId>[^/]+)$": ConnectResponse.dispatch,
    # User hierarchy groups
    "{0}/user-hierarchy-groups/(?P<InstanceId>[^/]+)$": ConnectResponse.dispatch,
    "{0}/user-hierarchy-groups/(?P<InstanceId>[^/]+)/(?P<HierarchyGroupId>[^/]+)$": ConnectResponse.dispatch,
    # User hierarchy structure
    "{0}/user-hierarchy-structure/(?P<InstanceId>[^/]+)$": ConnectResponse.dispatch,
    # Views
    "{0}/views/(?P<InstanceId>[^/]+)$": ConnectResponse.dispatch,
    "{0}/views/(?P<InstanceId>[^/]+)/(?P<ViewId>[^/]+)$": ConnectResponse.dispatch,
    # Vocabulary
    "{0}/vocabulary/(?P<InstanceId>[^/]+)$": ConnectResponse.dispatch,
    "{0}/vocabulary/(?P<InstanceId>[^/]+)/(?P<VocabularyId>[^/]+)$": ConnectResponse.dispatch,
    # Contact attributes
    "{0}/contact/attributes/(?P<InstanceId>[^/]+)/(?P<InitialContactId>[^/]+)$": ConnectResponse.dispatch,
    # Update contact attributes (POST body, different URL)
    "{0}/contact/attributes$": ConnectResponse.dispatch,
    # Tags
    "{0}/tags/(?P<resourceArn>.+)$": ConnectResponse.dispatch,
}
