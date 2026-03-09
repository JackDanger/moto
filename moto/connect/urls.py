from .responses import ConnectResponse

url_bases = [
    r"https?://connect\.(.+)\.amazonaws\.com",
]

url_paths = {
    # Existing patterns
    "{0}/analytics-data/instance/(?P<InstanceId>[^/]+)/association$": ConnectResponse.dispatch,
    "{0}/instance/(?P<InstanceId>[^/]+)$": ConnectResponse.dispatch,
    "{0}/instance$": ConnectResponse.dispatch,
    "{0}/tags/(?P<resourceArn>.+)$": ConnectResponse.dispatch,
    # List operations - simple summaries
    "{0}/agent-status/(?P<InstanceId>[^/]+)$": ConnectResponse.dispatch,
    "{0}/instance/(?P<InstanceId>[^/]+)/approved-origins$": ConnectResponse.dispatch,
    "{0}/instance/(?P<InstanceId>[^/]+)/bots$": ConnectResponse.dispatch,
    "{0}/contact-evaluations/(?P<InstanceId>[^/]+)$": ConnectResponse.dispatch,
    "{0}/contact-flow-modules-summary/(?P<InstanceId>[^/]+)$": ConnectResponse.dispatch,
    "{0}/contact-flows/(?P<InstanceId>[^/]+)/(?P<ContactFlowId>[^/]+)/versions$": ConnectResponse.dispatch,
    "{0}/contact-flows-summary/(?P<InstanceId>[^/]+)$": ConnectResponse.dispatch,
    "{0}/contact/references/(?P<InstanceId>[^/]+)/(?P<ContactId>[^/]+)$": ConnectResponse.dispatch,
    "{0}/default-vocabulary-summary/(?P<InstanceId>[^/]+)$": ConnectResponse.dispatch,
    "{0}/evaluation-forms/(?P<InstanceId>[^/]+)/(?P<EvaluationFormId>[^/]+)/versions$": ConnectResponse.dispatch,
    "{0}/evaluation-forms/(?P<InstanceId>[^/]+)$": ConnectResponse.dispatch,
    "{0}/flow-associations-summary/(?P<InstanceId>[^/]+)$": ConnectResponse.dispatch,
    "{0}/hours-of-operations/(?P<InstanceId>[^/]+)/(?P<HoursOfOperationId>[^/]+)/overrides$": ConnectResponse.dispatch,
    "{0}/hours-of-operations-summary/(?P<InstanceId>[^/]+)$": ConnectResponse.dispatch,
    "{0}/instance/(?P<InstanceId>[^/]+)/attributes$": ConnectResponse.dispatch,
    "{0}/instance/(?P<InstanceId>[^/]+)/storage-configs$": ConnectResponse.dispatch,
    "{0}/instance/(?P<InstanceId>[^/]+)/lambda-functions$": ConnectResponse.dispatch,
    "{0}/phone-numbers-summary/(?P<InstanceId>[^/]+)$": ConnectResponse.dispatch,
    "{0}/phone-number/list$": ConnectResponse.dispatch,
    "{0}/prompts-summary/(?P<InstanceId>[^/]+)$": ConnectResponse.dispatch,
    "{0}/queues/(?P<InstanceId>[^/]+)/(?P<QueueId>[^/]+)/quick-connects$": ConnectResponse.dispatch,
    "{0}/queues-summary/(?P<InstanceId>[^/]+)$": ConnectResponse.dispatch,
    "{0}/quick-connects/(?P<InstanceId>[^/]+)$": ConnectResponse.dispatch,
    "{0}/routing-profiles-summary/(?P<InstanceId>[^/]+)$": ConnectResponse.dispatch,
    "{0}/instance/(?P<InstanceId>[^/]+)/security-keys$": ConnectResponse.dispatch,
    "{0}/security-profiles-applications/(?P<InstanceId>[^/]+)/(?P<SecurityProfileId>[^/]+)$": ConnectResponse.dispatch,
    "{0}/security-profiles-permissions/(?P<InstanceId>[^/]+)/(?P<SecurityProfileId>[^/]+)$": ConnectResponse.dispatch,
    "{0}/security-profiles-summary/(?P<InstanceId>[^/]+)$": ConnectResponse.dispatch,
    "{0}/instance/(?P<InstanceId>[^/]+)/integration-associations/(?P<IntegrationAssociationId>[^/]+)/use-cases$": ConnectResponse.dispatch,
}
