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
    # Instance attributes (list)
    "{0}/instance/(?P<InstanceId>[^/]+)/attributes$": ConnectResponse.dispatch,
    # Instance storage config (placeholder for DescribeInstanceStorageConfig)
    "{0}/instance/(?P<InstanceId>[^/]+)/storage-config/(?P<AssociationId>[^/]+)$": ConnectResponse.dispatch,
    # Instance storage configs (list)
    "{0}/instance/(?P<InstanceId>[^/]+)/storage-configs$": ConnectResponse.dispatch,
    # Instance-level sub-resources
    "{0}/instance/(?P<InstanceId>[^/]+)/approved-origins$": ConnectResponse.dispatch,
    "{0}/instance/(?P<InstanceId>[^/]+)/bots$": ConnectResponse.dispatch,
    "{0}/instance/(?P<InstanceId>[^/]+)/lambda-functions$": ConnectResponse.dispatch,
    "{0}/instance/(?P<InstanceId>[^/]+)/security-keys$": ConnectResponse.dispatch,
    "{0}/instance/(?P<InstanceId>[^/]+)/integration-associations$": ConnectResponse.dispatch,
    "{0}/instance/(?P<InstanceId>[^/]+)/integration-associations/(?P<IntegrationAssociationId>[^/]+)/use-cases$": ConnectResponse.dispatch,
    # Task templates
    "{0}/instance/(?P<InstanceId>[^/]+)/task/template$": ConnectResponse.dispatch,
    # Analytics data associations
    "{0}/analytics-data/instance/(?P<InstanceId>[^/]+)/association$": ConnectResponse.dispatch,
    # Agent status
    "{0}/agent-status/(?P<InstanceId>[^/]+)$": ConnectResponse.dispatch,
    "{0}/agent-status/(?P<InstanceId>[^/]+)/(?P<AgentStatusId>[^/]+)$": ConnectResponse.dispatch,
    # Contact flows (CRUD)
    "{0}/contact-flows/(?P<InstanceId>[^/]+)$": ConnectResponse.dispatch,
    "{0}/contact-flows/(?P<InstanceId>[^/]+)/(?P<ContactFlowId>[^/]+)$": ConnectResponse.dispatch,
    "{0}/contact-flows/(?P<InstanceId>[^/]+)/(?P<ContactFlowId>[^/]+)/versions$": ConnectResponse.dispatch,
    # Contact flows (list summary)
    "{0}/contact-flows-summary/(?P<InstanceId>[^/]+)$": ConnectResponse.dispatch,
    # Contact flow modules (CRUD)
    "{0}/contact-flow-modules/(?P<InstanceId>[^/]+)$": ConnectResponse.dispatch,
    "{0}/contact-flow-modules/(?P<InstanceId>[^/]+)/(?P<ContactFlowModuleId>[^/]+)$": ConnectResponse.dispatch,
    # Contact flow modules (list summary)
    "{0}/contact-flow-modules-summary/(?P<InstanceId>[^/]+)$": ConnectResponse.dispatch,
    # Contact evaluations
    "{0}/contact-evaluations/(?P<InstanceId>[^/]+)$": ConnectResponse.dispatch,
    # Contact references
    "{0}/contact/references/(?P<InstanceId>[^/]+)/(?P<ContactId>[^/]+)$": ConnectResponse.dispatch,
    # Default vocabulary summary (POST)
    "{0}/default-vocabulary-summary/(?P<InstanceId>[^/]+)$": ConnectResponse.dispatch,
    # Evaluation forms (CRUD)
    "{0}/evaluation-forms/(?P<InstanceId>[^/]+)$": ConnectResponse.dispatch,
    "{0}/evaluation-forms/(?P<InstanceId>[^/]+)/(?P<EvaluationFormId>[^/]+)$": ConnectResponse.dispatch,
    "{0}/evaluation-forms/(?P<InstanceId>[^/]+)/(?P<EvaluationFormId>[^/]+)/versions$": ConnectResponse.dispatch,
    # Flow associations (list summary)
    "{0}/flow-associations-summary/(?P<InstanceId>[^/]+)$": ConnectResponse.dispatch,
    # Hours of operation (CRUD)
    "{0}/hours-of-operations/(?P<InstanceId>[^/]+)$": ConnectResponse.dispatch,
    "{0}/hours-of-operations/(?P<InstanceId>[^/]+)/(?P<HoursOfOperationId>[^/]+)$": ConnectResponse.dispatch,
    "{0}/hours-of-operations/(?P<InstanceId>[^/]+)/(?P<HoursOfOperationId>[^/]+)/overrides$": ConnectResponse.dispatch,
    # Hours of operation (list summary)
    "{0}/hours-of-operations-summary/(?P<InstanceId>[^/]+)$": ConnectResponse.dispatch,
    # Phone number
    "{0}/phone-number/(?P<PhoneNumberId>[^/]+)$": ConnectResponse.dispatch,
    "{0}/phone-number/list$": ConnectResponse.dispatch,
    # Phone numbers summary (list)
    "{0}/phone-numbers-summary/(?P<InstanceId>[^/]+)$": ConnectResponse.dispatch,
    # Prompts (CRUD)
    "{0}/prompts/(?P<InstanceId>[^/]+)$": ConnectResponse.dispatch,
    "{0}/prompts/(?P<InstanceId>[^/]+)/(?P<PromptId>[^/]+)$": ConnectResponse.dispatch,
    # Prompts (list summary)
    "{0}/prompts-summary/(?P<InstanceId>[^/]+)$": ConnectResponse.dispatch,
    # Queues (CRUD)
    "{0}/queues/(?P<InstanceId>[^/]+)$": ConnectResponse.dispatch,
    "{0}/queues/(?P<InstanceId>[^/]+)/(?P<QueueId>[^/]+)$": ConnectResponse.dispatch,
    "{0}/queues/(?P<InstanceId>[^/]+)/(?P<QueueId>[^/]+)/quick-connects$": ConnectResponse.dispatch,
    # Queues (list summary)
    "{0}/queues-summary/(?P<InstanceId>[^/]+)$": ConnectResponse.dispatch,
    # Quick connects
    "{0}/quick-connects/(?P<InstanceId>[^/]+)$": ConnectResponse.dispatch,
    "{0}/quick-connects/(?P<InstanceId>[^/]+)/(?P<QuickConnectId>[^/]+)$": ConnectResponse.dispatch,
    # Routing profiles (CRUD)
    "{0}/routing-profiles/(?P<InstanceId>[^/]+)$": ConnectResponse.dispatch,
    "{0}/routing-profiles/(?P<InstanceId>[^/]+)/(?P<RoutingProfileId>[^/]+)$": ConnectResponse.dispatch,
    "{0}/routing-profiles/(?P<InstanceId>[^/]+)/(?P<RoutingProfileId>[^/]+)/queues$": ConnectResponse.dispatch,
    # Routing profiles (list summary)
    "{0}/routing-profiles-summary/(?P<InstanceId>[^/]+)$": ConnectResponse.dispatch,
    # Rules (CRUD)
    "{0}/rules/(?P<InstanceId>[^/]+)$": ConnectResponse.dispatch,
    "{0}/rules/(?P<InstanceId>[^/]+)/(?P<RuleId>[^/]+)$": ConnectResponse.dispatch,
    # Security profiles (CRUD)
    "{0}/security-profiles/(?P<InstanceId>[^/]+)$": ConnectResponse.dispatch,
    "{0}/security-profiles/(?P<InstanceId>[^/]+)/(?P<SecurityProfileId>[^/]+)$": ConnectResponse.dispatch,
    # Security profiles (list summary)
    "{0}/security-profiles-summary/(?P<InstanceId>[^/]+)$": ConnectResponse.dispatch,
    # Security profile permissions
    "{0}/security-profiles-permissions/(?P<InstanceId>[^/]+)/(?P<SecurityProfileId>[^/]+)$": ConnectResponse.dispatch,
    # Security profile applications
    "{0}/security-profiles-applications/(?P<InstanceId>[^/]+)/(?P<SecurityProfileId>[^/]+)$": ConnectResponse.dispatch,
    # Traffic distribution group
    "{0}/traffic-distribution-group$": ConnectResponse.dispatch,
    "{0}/traffic-distribution-group/(?P<TrafficDistributionGroupId>[^/]+)$": ConnectResponse.dispatch,
    "{0}/traffic-distribution-groups$": ConnectResponse.dispatch,
    # Users (CRUD)
    "{0}/users/(?P<InstanceId>[^/]+)$": ConnectResponse.dispatch,
    "{0}/users/(?P<InstanceId>[^/]+)/(?P<UserId>[^/]+)$": ConnectResponse.dispatch,
    # Users (list summary)
    "{0}/users-summary/(?P<InstanceId>[^/]+)$": ConnectResponse.dispatch,
    # User hierarchy groups (CRUD)
    "{0}/user-hierarchy-groups/(?P<InstanceId>[^/]+)$": ConnectResponse.dispatch,
    "{0}/user-hierarchy-groups/(?P<InstanceId>[^/]+)/(?P<HierarchyGroupId>[^/]+)$": ConnectResponse.dispatch,
    # User hierarchy groups (list summary)
    "{0}/user-hierarchy-groups-summary/(?P<InstanceId>[^/]+)$": ConnectResponse.dispatch,
    # User hierarchy structure
    "{0}/user-hierarchy-structure/(?P<InstanceId>[^/]+)$": ConnectResponse.dispatch,
    # Views (CRUD)
    "{0}/views/(?P<InstanceId>[^/]+)$": ConnectResponse.dispatch,
    "{0}/views/(?P<InstanceId>[^/]+)/(?P<ViewId>[^/]+)$": ConnectResponse.dispatch,
    # Vocabulary (CRUD)
    "{0}/vocabulary/(?P<InstanceId>[^/]+)$": ConnectResponse.dispatch,
    "{0}/vocabulary/(?P<InstanceId>[^/]+)/(?P<VocabularyId>[^/]+)$": ConnectResponse.dispatch,
    # Contact attributes
    "{0}/contact/attributes/(?P<InstanceId>[^/]+)/(?P<InitialContactId>[^/]+)$": ConnectResponse.dispatch,
    # Update contact attributes (POST body, different URL)
    "{0}/contact/attributes$": ConnectResponse.dispatch,
    # Tags
    "{0}/tags/(?P<resourceArn>.+)$": ConnectResponse.dispatch,
}
