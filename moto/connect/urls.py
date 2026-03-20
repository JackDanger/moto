from .responses import ConnectResponse

url_bases = [
    r"https?://connect\.(.+)\.amazonaws\.com",
]

url_paths = {
    # Instance
    "{0}/instance$": ConnectResponse.dispatch,
    "{0}/instance/(?P<InstanceId>[^/]+)$": ConnectResponse.dispatch,
    "{0}/instance/(?P<InstanceId>[^/]+)/attribute/(?P<AttributeType>[^/]+)$": ConnectResponse.dispatch,
    "{0}/instance/(?P<InstanceId>[^/]+)/attributes$": ConnectResponse.dispatch,
    "{0}/instance/(?P<InstanceId>[^/]+)/storage-config/(?P<AssociationId>[^/]+)$": ConnectResponse.dispatch,
    "{0}/instance/(?P<InstanceId>[^/]+)/storage-configs$": ConnectResponse.dispatch,
    "{0}/instance/(?P<InstanceId>[^/]+)/approved-origins$": ConnectResponse.dispatch,
    "{0}/instance/(?P<InstanceId>[^/]+)/approved-origin$": ConnectResponse.dispatch,
    "{0}/instance/(?P<InstanceId>[^/]+)/bots$": ConnectResponse.dispatch,
    "{0}/instance/(?P<InstanceId>[^/]+)/bot$": ConnectResponse.dispatch,
    "{0}/instance/(?P<InstanceId>[^/]+)/lambda-functions$": ConnectResponse.dispatch,
    "{0}/instance/(?P<InstanceId>[^/]+)/lambda-function$": ConnectResponse.dispatch,
    "{0}/instance/(?P<InstanceId>[^/]+)/security-keys$": ConnectResponse.dispatch,
    "{0}/instance/(?P<InstanceId>[^/]+)/security-key$": ConnectResponse.dispatch,
    "{0}/instance/(?P<InstanceId>[^/]+)/security-key/(?P<AssociationId>[^/]+)$": ConnectResponse.dispatch,
    "{0}/instance/(?P<InstanceId>[^/]+)/storage-config$": ConnectResponse.dispatch,
    "{0}/instance/(?P<InstanceId>[^/]+)/integration-associations$": ConnectResponse.dispatch,
    "{0}/instance/(?P<InstanceId>[^/]+)/integration-associations/(?P<IntegrationAssociationId>[^/]+)/use-cases$": ConnectResponse.dispatch,
    "{0}/analytics-data/instance/(?P<InstanceId>[^/]+)/association$": ConnectResponse.dispatch,
    # Agent status
    "{0}/agent-status/(?P<InstanceId>[^/]+)$": ConnectResponse.dispatch,
    "{0}/agent-status/(?P<InstanceId>[^/]+)/(?P<AgentStatusId>[^/]+)$": ConnectResponse.dispatch,
    # Contact flows
    "{0}/contact-flows/(?P<InstanceId>[^/]+)$": ConnectResponse.dispatch,
    "{0}/contact-flows/(?P<InstanceId>[^/]+)/(?P<ContactFlowId>[^/]+)$": ConnectResponse.dispatch,
    "{0}/contact-flows/(?P<InstanceId>[^/]+)/(?P<ContactFlowId>[^/]+)/versions$": ConnectResponse.dispatch,
    "{0}/contact-flows/(?P<InstanceId>[^/]+)/(?P<ContactFlowId>[^/]+)/content$": ConnectResponse.dispatch,
    "{0}/contact-flows/(?P<InstanceId>[^/]+)/(?P<ContactFlowId>[^/]+)/name$": ConnectResponse.dispatch,
    "{0}/contact-flows-summary/(?P<InstanceId>[^/]+)$": ConnectResponse.dispatch,
    # Contact flow metadata
    "{0}/contact-flows/(?P<InstanceId>[^/]+)/(?P<ContactFlowId>[^/]+)/metadata$": ConnectResponse.dispatch,
    # Contact flow modules
    "{0}/contact-flow-modules/(?P<InstanceId>[^/]+)/(?P<ContactFlowModuleId>[^/]+)/alias/(?P<AliasId>[^/]+)$": ConnectResponse.dispatch,
    "{0}/contact-flow-modules/(?P<InstanceId>[^/]+)/(?P<ContactFlowModuleId>[^/]+)/aliases$": ConnectResponse.dispatch,
    "{0}/contact-flow-modules/(?P<InstanceId>[^/]+)/(?P<ContactFlowModuleId>[^/]+)/alias$": ConnectResponse.dispatch,
    "{0}/contact-flow-modules/(?P<InstanceId>[^/]+)$": ConnectResponse.dispatch,
    "{0}/contact-flow-modules/(?P<InstanceId>[^/]+)/(?P<ContactFlowModuleId>[^/]+)$": ConnectResponse.dispatch,
    "{0}/contact-flow-modules/(?P<InstanceId>[^/]+)/(?P<ContactFlowModuleId>[^/]+)/content$": ConnectResponse.dispatch,
    "{0}/contact-flow-modules/(?P<InstanceId>[^/]+)/(?P<ContactFlowModuleId>[^/]+)/metadata$": ConnectResponse.dispatch,
    "{0}/contact-flow-modules-summary/(?P<InstanceId>[^/]+)$": ConnectResponse.dispatch,
    # Contact evaluations and references
    "{0}/contact-evaluations/(?P<InstanceId>[^/]+)/(?P<EvaluationId>[^/]+)$": ConnectResponse.dispatch,
    "{0}/contact-evaluations/(?P<InstanceId>[^/]+)$": ConnectResponse.dispatch,
    "{0}/contact/references/(?P<InstanceId>[^/]+)/(?P<ContactId>[^/]+)$": ConnectResponse.dispatch,
    # Default vocabulary summary
    "{0}/default-vocabulary-summary/(?P<InstanceId>[^/]+)$": ConnectResponse.dispatch,
    # Evaluation forms
    "{0}/evaluation-forms/(?P<InstanceId>[^/]+)$": ConnectResponse.dispatch,
    "{0}/evaluation-forms/(?P<InstanceId>[^/]+)/(?P<EvaluationFormId>[^/]+)$": ConnectResponse.dispatch,
    "{0}/evaluation-forms/(?P<InstanceId>[^/]+)/(?P<EvaluationFormId>[^/]+)/versions$": ConnectResponse.dispatch,
    # Flow associations
    "{0}/flow-associations-summary/(?P<InstanceId>[^/]+)$": ConnectResponse.dispatch,
    # Hours of operation
    "{0}/hours-of-operations/(?P<InstanceId>[^/]+)$": ConnectResponse.dispatch,
    "{0}/hours-of-operations/(?P<InstanceId>[^/]+)/(?P<HoursOfOperationId>[^/]+)$": ConnectResponse.dispatch,
    "{0}/hours-of-operations/(?P<InstanceId>[^/]+)/(?P<HoursOfOperationId>[^/]+)/overrides$": ConnectResponse.dispatch,
    "{0}/hours-of-operations/(?P<InstanceId>[^/]+)/(?P<HoursOfOperationId>[^/]+)/overrides/(?P<HoursOfOperationOverrideId>[^/]+)$": ConnectResponse.dispatch,
    "{0}/hours-of-operations-summary/(?P<InstanceId>[^/]+)$": ConnectResponse.dispatch,
    # Predefined attributes
    "{0}/predefined-attributes/(?P<InstanceId>[^/]+)$": ConnectResponse.dispatch,
    "{0}/predefined-attributes/(?P<InstanceId>[^/]+)/(?P<Name>[^/]+)$": ConnectResponse.dispatch,
    "{0}/predefined-attributes-summary/(?P<InstanceId>[^/]+)$": ConnectResponse.dispatch,
    # Task templates
    "{0}/instance/(?P<InstanceId>[^/]+)/task/template$": ConnectResponse.dispatch,
    "{0}/instance/(?P<InstanceId>[^/]+)/task/template/(?P<TaskTemplateId>[^/]+)$": ConnectResponse.dispatch,
    # Contacts
    "{0}/contact/create-contact$": ConnectResponse.dispatch,
    "{0}/contacts/(?P<InstanceId>[^/]+)/(?P<ContactId>[^/]+)$": ConnectResponse.dispatch,
    "{0}/contact/stop$": ConnectResponse.dispatch,
    # Phone number
    "{0}/phone-number/claim$": ConnectResponse.dispatch,
    "{0}/phone-number/search-available$": ConnectResponse.dispatch,
    "{0}/phone-number/list$": ConnectResponse.dispatch,
    "{0}/phone-number/(?P<PhoneNumberId>[^/]+)$": ConnectResponse.dispatch,
    "{0}/phone-numbers-summary/(?P<InstanceId>[^/]+)$": ConnectResponse.dispatch,
    # Prompts
    "{0}/prompts/(?P<InstanceId>[^/]+)$": ConnectResponse.dispatch,
    "{0}/prompts/(?P<InstanceId>[^/]+)/(?P<PromptId>[^/]+)$": ConnectResponse.dispatch,
    "{0}/prompts-summary/(?P<InstanceId>[^/]+)$": ConnectResponse.dispatch,
    # Queues
    "{0}/queues/(?P<InstanceId>[^/]+)$": ConnectResponse.dispatch,
    "{0}/queues/(?P<InstanceId>[^/]+)/(?P<QueueId>[^/]+)$": ConnectResponse.dispatch,
    "{0}/queues/(?P<InstanceId>[^/]+)/(?P<QueueId>[^/]+)/name$": ConnectResponse.dispatch,
    "{0}/queues/(?P<InstanceId>[^/]+)/(?P<QueueId>[^/]+)/max-contacts$": ConnectResponse.dispatch,
    "{0}/queues/(?P<InstanceId>[^/]+)/(?P<QueueId>[^/]+)/status$": ConnectResponse.dispatch,
    "{0}/queues/(?P<InstanceId>[^/]+)/(?P<QueueId>[^/]+)/hours-of-operation$": ConnectResponse.dispatch,
    "{0}/queues/(?P<InstanceId>[^/]+)/(?P<QueueId>[^/]+)/outbound-caller-config$": ConnectResponse.dispatch,
    "{0}/queues/(?P<InstanceId>[^/]+)/(?P<QueueId>[^/]+)/quick-connects$": ConnectResponse.dispatch,
    "{0}/queues/(?P<InstanceId>[^/]+)/(?P<QueueId>[^/]+)/associate-quick-connects$": ConnectResponse.dispatch,
    "{0}/queues/(?P<InstanceId>[^/]+)/(?P<QueueId>[^/]+)/disassociate-quick-connects$": ConnectResponse.dispatch,
    "{0}/queues-summary/(?P<InstanceId>[^/]+)$": ConnectResponse.dispatch,
    # Quick connects
    "{0}/quick-connects/(?P<InstanceId>[^/]+)$": ConnectResponse.dispatch,
    "{0}/quick-connects/(?P<InstanceId>[^/]+)/(?P<QuickConnectId>[^/]+)$": ConnectResponse.dispatch,
    "{0}/quick-connects/(?P<InstanceId>[^/]+)/(?P<QuickConnectId>[^/]+)/name$": ConnectResponse.dispatch,
    "{0}/quick-connects/(?P<InstanceId>[^/]+)/(?P<QuickConnectId>[^/]+)/config$": ConnectResponse.dispatch,
    # Routing profiles
    "{0}/routing-profiles/(?P<InstanceId>[^/]+)$": ConnectResponse.dispatch,
    "{0}/routing-profiles/(?P<InstanceId>[^/]+)/(?P<RoutingProfileId>[^/]+)$": ConnectResponse.dispatch,
    "{0}/routing-profiles/(?P<InstanceId>[^/]+)/(?P<RoutingProfileId>[^/]+)/concurrency$": ConnectResponse.dispatch,
    "{0}/routing-profiles/(?P<InstanceId>[^/]+)/(?P<RoutingProfileId>[^/]+)/default-outbound-queue$": ConnectResponse.dispatch,
    "{0}/routing-profiles/(?P<InstanceId>[^/]+)/(?P<RoutingProfileId>[^/]+)/name$": ConnectResponse.dispatch,
    "{0}/routing-profiles/(?P<InstanceId>[^/]+)/(?P<RoutingProfileId>[^/]+)/queues$": ConnectResponse.dispatch,
    "{0}/routing-profiles/(?P<InstanceId>[^/]+)/(?P<RoutingProfileId>[^/]+)/associate-queues$": ConnectResponse.dispatch,
    "{0}/routing-profiles/(?P<InstanceId>[^/]+)/(?P<RoutingProfileId>[^/]+)/disassociate-queues$": ConnectResponse.dispatch,
    "{0}/routing-profiles-summary/(?P<InstanceId>[^/]+)$": ConnectResponse.dispatch,
    # Rules
    "{0}/rules/(?P<InstanceId>[^/]+)$": ConnectResponse.dispatch,
    "{0}/rules/(?P<InstanceId>[^/]+)/(?P<RuleId>[^/]+)$": ConnectResponse.dispatch,
    # Security profiles
    "{0}/security-profiles/(?P<InstanceId>[^/]+)$": ConnectResponse.dispatch,
    "{0}/security-profiles/(?P<InstanceId>[^/]+)/(?P<SecurityProfileId>[^/]+)$": ConnectResponse.dispatch,
    "{0}/security-profiles-summary/(?P<InstanceId>[^/]+)$": ConnectResponse.dispatch,
    "{0}/security-profiles-permissions/(?P<InstanceId>[^/]+)/(?P<SecurityProfileId>[^/]+)$": ConnectResponse.dispatch,
    "{0}/security-profiles-applications/(?P<InstanceId>[^/]+)/(?P<SecurityProfileId>[^/]+)$": ConnectResponse.dispatch,
    # Traffic distribution group
    "{0}/traffic-distribution-group$": ConnectResponse.dispatch,
    "{0}/traffic-distribution-group/(?P<TrafficDistributionGroupId>[^/]+)$": ConnectResponse.dispatch,
    "{0}/traffic-distribution-groups$": ConnectResponse.dispatch,
    # Users
    "{0}/users/(?P<InstanceId>[^/]+)$": ConnectResponse.dispatch,
    "{0}/users/(?P<InstanceId>[^/]+)/(?P<UserId>[^/]+)$": ConnectResponse.dispatch,
    "{0}/users/(?P<InstanceId>[^/]+)/(?P<UserId>[^/]+)/identity-info$": ConnectResponse.dispatch,
    "{0}/users/(?P<InstanceId>[^/]+)/(?P<UserId>[^/]+)/phone-config$": ConnectResponse.dispatch,
    "{0}/users/(?P<InstanceId>[^/]+)/(?P<UserId>[^/]+)/routing-profile$": ConnectResponse.dispatch,
    "{0}/users/(?P<InstanceId>[^/]+)/(?P<UserId>[^/]+)/security-profiles$": ConnectResponse.dispatch,
    "{0}/users/(?P<InstanceId>[^/]+)/(?P<UserId>[^/]+)/hierarchy$": ConnectResponse.dispatch,
    "{0}/users-summary/(?P<InstanceId>[^/]+)$": ConnectResponse.dispatch,
    "{0}/search-users$": ConnectResponse.dispatch,
    # User hierarchy
    "{0}/user-hierarchy-groups/(?P<InstanceId>[^/]+)$": ConnectResponse.dispatch,
    "{0}/user-hierarchy-groups/(?P<InstanceId>[^/]+)/(?P<HierarchyGroupId>[^/]+)$": ConnectResponse.dispatch,
    "{0}/user-hierarchy-groups/(?P<InstanceId>[^/]+)/(?P<HierarchyGroupId>[^/]+)/name$": ConnectResponse.dispatch,
    "{0}/user-hierarchy-groups-summary/(?P<InstanceId>[^/]+)$": ConnectResponse.dispatch,
    "{0}/user-hierarchy-structure/(?P<InstanceId>[^/]+)$": ConnectResponse.dispatch,
    # Use case
    "{0}/instance/(?P<InstanceId>[^/]+)/integration-associations/(?P<IntegrationAssociationId>[^/]+)/use-cases/(?P<UseCaseId>[^/]+)$": ConnectResponse.dispatch,
    # Views
    "{0}/views/(?P<InstanceId>[^/]+)$": ConnectResponse.dispatch,
    "{0}/views/(?P<InstanceId>[^/]+)/(?P<ViewId>[^/]+)$": ConnectResponse.dispatch,
    "{0}/views/(?P<InstanceId>[^/]+)/(?P<ViewId>[^/]+)/content$": ConnectResponse.dispatch,
    "{0}/views/(?P<InstanceId>[^/]+)/(?P<ViewId>[^/]+)/metadata$": ConnectResponse.dispatch,
    # Vocabulary
    "{0}/vocabulary/(?P<InstanceId>[^/]+)$": ConnectResponse.dispatch,
    "{0}/vocabulary/(?P<InstanceId>[^/]+)/(?P<VocabularyId>[^/]+)$": ConnectResponse.dispatch,
    "{0}/vocabulary/(?P<InstanceId>[^/]+)/search$": ConnectResponse.dispatch,
    "{0}/vocabulary-remove/(?P<InstanceId>[^/]+)/(?P<VocabularyId>[^/]+)$": ConnectResponse.dispatch,
    "{0}/vocabulary-summary/(?P<InstanceId>[^/]+)$": ConnectResponse.dispatch,
    # Contact attributes
    "{0}/contact/attributes/(?P<InstanceId>[^/]+)/(?P<InitialContactId>[^/]+)$": ConnectResponse.dispatch,
    "{0}/contact/attributes$": ConnectResponse.dispatch,
    # Evaluation form activate/deactivate
    "{0}/evaluation-forms/(?P<InstanceId>[^/]+)/(?P<EvaluationFormId>[^/]+)/activate$": ConnectResponse.dispatch,
    "{0}/evaluation-forms/(?P<InstanceId>[^/]+)/(?P<EvaluationFormId>[^/]+)/deactivate$": ConnectResponse.dispatch,
    # Search endpoints
    "{0}/search-queues$": ConnectResponse.dispatch,
    "{0}/search-quick-connects$": ConnectResponse.dispatch,
    "{0}/search-prompts$": ConnectResponse.dispatch,
    "{0}/search-routing-profiles$": ConnectResponse.dispatch,
    "{0}/search-security-profiles$": ConnectResponse.dispatch,
    "{0}/search-hours-of-operations$": ConnectResponse.dispatch,
    "{0}/search-agent-statuses$": ConnectResponse.dispatch,
    "{0}/search-contact-flows$": ConnectResponse.dispatch,
    "{0}/search-contact-flow-modules$": ConnectResponse.dispatch,
    "{0}/search-user-hierarchy-groups$": ConnectResponse.dispatch,
    "{0}/search-predefined-attributes$": ConnectResponse.dispatch,
    # Workspaces
    "{0}/workspaces/(?P<InstanceId>[^/]+)/(?P<WorkspaceId>[^/]+)$": ConnectResponse.dispatch,
    "{0}/workspaces/(?P<InstanceId>[^/]+)$": ConnectResponse.dispatch,
    # Email addresses
    "{0}/email-addresses/(?P<InstanceId>[^/]+)/(?P<EmailAddressId>[^/]+)$": ConnectResponse.dispatch,
    "{0}/email-addresses/(?P<InstanceId>[^/]+)$": ConnectResponse.dispatch,
    # Notifications
    "{0}/notifications/(?P<InstanceId>[^/]+)/(?P<NotificationId>[^/]+)$": ConnectResponse.dispatch,
    "{0}/notifications/(?P<InstanceId>[^/]+)$": ConnectResponse.dispatch,
    # Data tables
    "{0}/data-tables/(?P<InstanceId>[^/]+)/(?P<DataTableId>[^/]+)/attributes/(?P<AttributeName>[^/]+)$": ConnectResponse.dispatch,
    "{0}/data-tables/(?P<InstanceId>[^/]+)/(?P<DataTableId>[^/]+)/attributes$": ConnectResponse.dispatch,
    "{0}/data-tables/(?P<InstanceId>[^/]+)/(?P<DataTableId>[^/]+)$": ConnectResponse.dispatch,
    "{0}/data-tables/(?P<InstanceId>[^/]+)$": ConnectResponse.dispatch,
    # Test cases
    "{0}/test-cases/(?P<InstanceId>[^/]+)/(?P<TestCaseId>[^/]+)$": ConnectResponse.dispatch,
    "{0}/test-cases-summary/(?P<InstanceId>[^/]+)$": ConnectResponse.dispatch,
    "{0}/test-cases/(?P<InstanceId>[^/]+)$": ConnectResponse.dispatch,
    # Tags
    "{0}/tags/(?P<resourceArn>.+)$": ConnectResponse.dispatch,
}
