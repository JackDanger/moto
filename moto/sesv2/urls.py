"""sesv2 base URL and path."""

from .responses import SESV2Response

url_bases = [
    r"https?://email\.(.+)\.amazonaws\.com",
]


response = SESV2Response()


url_paths = {
    # Outbound emails
    "{0}/v2/email/outbound-emails$": response.dispatch,
    "{0}/v2/email/outbound-bulk-emails$": response.dispatch,
    "{0}/v2/email/outbound-custom-verification-emails$": response.dispatch,
    # Contact lists
    "{0}/v2/email/contact-lists$": response.dispatch,
    "{0}/v2/email/contact-lists/(?P<ContactListName>[^/]+)$": response.dispatch,
    "{0}/v2/email/contact-lists/(?P<ContactListName>[^/]+)/contacts/list$": response.dispatch,
    "{0}/v2/email/contact-lists/(?P<ContactListName>[^/]+)/contacts$": response.dispatch,
    "{0}/v2/email/contact-lists/(?P<ContactListName>[^/]+)/contacts/(?P<EmailAddress>[^/]+)$": response.dispatch,
    # Templates
    "{0}/v2/email/templates$": response.dispatch,
    "{0}/v2/email/templates/(?P<TemplateName>[^/]+)$": response.dispatch,
    "{0}/v2/email/templates/(?P<TemplateName>[^/]+)/render$": response.dispatch,
    # Custom verification email templates
    "{0}/v2/email/custom-verification-email-templates$": response.dispatch,
    "{0}/v2/email/custom-verification-email-templates/(?P<TemplateName>[^/]+)$": response.dispatch,
    # Account
    "{0}/v2/email/account$": response.dispatch,
    "{0}/v2/email/account/details$": response.dispatch,
    "{0}/v2/email/account/sending$": response.dispatch,
    "{0}/v2/email/account/suppression$": response.dispatch,
    "{0}/v2/email/account/dedicated-ips/warmup$": response.dispatch,
    "{0}/v2/email/account/vdm$": response.dispatch,
    # Suppression
    "{0}/v2/email/suppression/addresses$": response.dispatch,
    "{0}/v2/email/suppression/addresses/(?P<EmailAddress>[^/]+)$": response.dispatch,
    # Dedicated IPs
    "{0}/v2/email/dedicated-ips$": response.dispatch,
    "{0}/v2/email/dedicated-ips/(?P<IP>[^/]+)/warmup$": response.dispatch,
    "{0}/v2/email/dedicated-ips/(?P<IP>[^/]+)/pool$": response.dispatch,
    "{0}/v2/email/dedicated-ips/(?P<IP>[^/]+)$": response.dispatch,
    # Dedicated IP Pools
    "{0}/v2/email/dedicated-ip-pools$": response.dispatch,
    "{0}/v2/email/dedicated-ip-pools/(?P<PoolName>[^/]+)/scaling$": response.dispatch,
    "{0}/v2/email/dedicated-ip-pools/(?P<PoolName>[^/]+)$": response.dispatch,
    # Deliverability Dashboard
    "{0}/v2/email/deliverability-dashboard$": response.dispatch,
    "{0}/v2/email/deliverability-dashboard/blacklist-report$": response.dispatch,
    "{0}/v2/email/deliverability-dashboard/test$": response.dispatch,
    "{0}/v2/email/deliverability-dashboard/test-reports$": response.dispatch,
    "{0}/v2/email/deliverability-dashboard/test-reports/(?P<ReportId>[^/]+)$": response.dispatch,
    "{0}/v2/email/deliverability-dashboard/campaigns/(?P<CampaignId>[^/]+)$": response.dispatch,
    "{0}/v2/email/deliverability-dashboard/domains/(?P<SubscribedDomain>[^/]+)/campaigns$": response.dispatch,
    "{0}/v2/email/deliverability-dashboard/statistics-report/(?P<Domain>[^/]+)$": response.dispatch,
    # Multi-region endpoints
    "{0}/v2/email/multi-region-endpoints$": response.dispatch,
    "{0}/v2/email/multi-region-endpoints/(?P<EndpointName>[^/]+)$": response.dispatch,
    # Configuration sets
    "{0}/v2/email/configuration-sets$": response.dispatch,
    "{0}/v2/email/configuration-sets/(?P<ConfigurationSetName>[^/]+)$": response.dispatch,
    "{0}/v2/email/configuration-sets/(?P<ConfigurationSetName>[^/]+)/event-destinations$": response.dispatch,
    "{0}/v2/email/configuration-sets/(?P<ConfigurationSetName>[^/]+)/event-destinations/(?P<EventDestinationName>[^/]+)$": response.dispatch,
    "{0}/v2/email/configuration-sets/(?P<ConfigurationSetName>[^/]+)/sending$": response.dispatch,
    "{0}/v2/email/configuration-sets/(?P<ConfigurationSetName>[^/]+)/reputation-options$": response.dispatch,
    "{0}/v2/email/configuration-sets/(?P<ConfigurationSetName>[^/]+)/vdm-options$": response.dispatch,
    "{0}/v2/email/configuration-sets/(?P<ConfigurationSetName>[^/]+)/delivery-options$": response.dispatch,
    "{0}/v2/email/configuration-sets/(?P<ConfigurationSetName>[^/]+)/suppression-options$": response.dispatch,
    "{0}/v2/email/configuration-sets/(?P<ConfigurationSetName>[^/]+)/tracking-options$": response.dispatch,
    "{0}/v2/email/configuration-sets/(?P<ConfigurationSetName>[^/]+)/archiving-options$": response.dispatch,
    # Email identities
    "{0}/v2/email/identities$": response.dispatch,
    "{0}/v2/email/identities/(?P<EmailIdentity>[^/]+)$": response.dispatch,
    "{0}/v2/email/identities/(?P<EmailIdentity>[^/]+)/dkim/signing$": response.dispatch,
    "{0}/v2/email/identities/(?P<EmailIdentity>[^/]+)/dkim$": response.dispatch,
    "{0}/v2/email/identities/(?P<EmailIdentity>[^/]+)/feedback$": response.dispatch,
    "{0}/v2/email/identities/(?P<EmailIdentity>[^/]+)/mail-from$": response.dispatch,
    "{0}/v2/email/identities/(?P<EmailIdentity>[^/]+)/configuration-set$": response.dispatch,
    "{0}/v2/email/identities/(?P<EmailIdentity>[^/]+)/policies$": response.dispatch,
    "{0}/v2/email/identities/(?P<EmailIdentity>[^/]+)/policies/(?P<PolicyName>[^/]+)$": response.dispatch,
    # Tags
    "{0}/v2/email/tags$": response.dispatch,
    # Import jobs
    "{0}/v2/email/import-jobs$": response.dispatch,
    "{0}/v2/email/import-jobs/list$": response.dispatch,
    "{0}/v2/email/import-jobs/(?P<JobId>[^/]+)$": response.dispatch,
    # Export jobs
    "{0}/v2/email/export-jobs$": response.dispatch,
    "{0}/v2/email/export-jobs/(?P<JobId>[^/]+)/cancel$": response.dispatch,
    "{0}/v2/email/export-jobs/(?P<JobId>[^/]+)$": response.dispatch,
    # List export jobs (different path from create)
    "{0}/v2/email/list-export-jobs$": response.dispatch,
    # Insights
    "{0}/v2/email/insights/(?P<MessageId>[^/]+)/?$": response.dispatch,
    "{0}/v2/email/email-address-insights/?$": response.dispatch,
    # Recommendations
    "{0}/v2/email/vdm/recommendations$": response.dispatch,
    # Metrics
    "{0}/v2/email/metrics/batch$": response.dispatch,
    # Tenants
    "{0}/v2/email/tenants$": response.dispatch,
    "{0}/v2/email/tenants/delete$": response.dispatch,
    "{0}/v2/email/tenants/get$": response.dispatch,
    "{0}/v2/email/tenants/list$": response.dispatch,
    "{0}/v2/email/tenants/resources$": response.dispatch,
    "{0}/v2/email/tenants/resources/delete$": response.dispatch,
    "{0}/v2/email/tenants/resources/list$": response.dispatch,
    "{0}/v2/email/resources/tenants/list$": response.dispatch,
    # Reputation entities
    "{0}/v2/email/reputation/entities$": response.dispatch,
    "{0}/v2/email/reputation/entities/(?P<ReputationEntityType>[^/]+)/(?P<ReputationEntityReference>[^/]+)/customer-managed-status$": response.dispatch,
    "{0}/v2/email/reputation/entities/(?P<ReputationEntityType>[^/]+)/(?P<ReputationEntityReference>[^/]+)/policy$": response.dispatch,
    "{0}/v2/email/reputation/entities/(?P<ReputationEntityType>[^/]+)/(?P<ReputationEntityReference>[^/]+)$": response.dispatch,
    # Catch-all for any unmatched v2/email paths
    "{0}/v2/.*$": response.dispatch,
}
