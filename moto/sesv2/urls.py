"""sesv2 base URL and path."""

from .responses import SESV2Response

url_bases = [
    r"https?://email\.(.+)\.amazonaws\.com",
]


response = SESV2Response()


url_paths = {
    "{0}/v2/email/outbound-emails$": response.dispatch,
    "{0}/v2/email/contact-lists/(?P<name>[^/]+)$": response.dispatch,
    "{0}/v2/email/contact-lists/(?P<name>[^/]+)/contacts$": response.dispatch,
    "{0}/v2/email/contact-lists/(?P<name>[^/]+)/contacts/(?P<email>[^/]+)$": response.dispatch,
    "{0}/v2/email/contact-lists$": response.dispatch,
    "{0}/v2/email/templates$": response.dispatch,
    "{0}/v2/email/templates/(?P<TemplateName>[^/]+)$": response.dispatch,
    "{0}/v2/email/custom-verification-email-templates$": response.dispatch,
    "{0}/v2/email/custom-verification-email-templates/(?P<TemplateName>[^/]+)$": response.dispatch,
    "{0}/v2/email/account$": response.dispatch,
    "{0}/v2/email/account/details$": response.dispatch,
    "{0}/v2/email/account/sending$": response.dispatch,
    "{0}/v2/email/account/suppression$": response.dispatch,
    "{0}/v2/email/configuration-sets$": SESV2Response.dispatch,
    "{0}/v2/email/configuration-sets/(?P<ConfigurationSetName>[^/]+)$": SESV2Response.dispatch,
    "{0}/v2/email/configuration-sets/(?P<ConfigurationSetName>[^/]+)/event-destinations$": response.dispatch,
    "{0}/v2/email/configuration-sets/(?P<ConfigurationSetName>[^/]+)/event-destinations/(?P<EventDestinationName>[^/]+)$": response.dispatch,
    "{0}/v2/email/configuration-sets/(?P<ConfigurationSetName>[^/]+)/sending$": response.dispatch,
    "{0}/v2/email/configuration-sets/(?P<ConfigurationSetName>[^/]+)/reputation-options$": response.dispatch,
    "{0}/v2/email/dedicated-ip-pools$": SESV2Response.dispatch,
    "{0}/v2/email/dedicated-ip-pools/(?P<PoolName>[^/]+)$": SESV2Response.dispatch,
    "{0}/v2/email/identities$": SESV2Response.dispatch,
    "{0}/v2/email/identities/(?P<EmailIdentity>[^/]+)$": SESV2Response.dispatch,
    "{0}/v2/email/identities/(?P<EmailIdentity>[^/]+)/policies/(?P<PolicyName>[^/]+)$": SESV2Response.dispatch,
    "{0}/v2/email/identities/(?P<EmailIdentity>[^/]+)/policies$": SESV2Response.dispatch,
    "{0}/v2/email/suppression/addresses/(?P<EmailAddress>[^/]+)$": response.dispatch,
    "{0}/v2/email/suppression/addresses$": response.dispatch,
    "{0}/v2/email/dedicated-ips/(?P<IP>[^/]+)/warmup$": response.dispatch,
    "{0}/v2/email/dedicated-ips/(?P<IP>[^/]+)$": response.dispatch,
    "{0}/v2/email/dedicated-ips$": response.dispatch,
    "{0}/v2/email/deliverability-dashboard/blacklist-report$": response.dispatch,
    "{0}/v2/email/deliverability-dashboard$": response.dispatch,
    "{0}/v2/email/multi-region-endpoints$": response.dispatch,
    "{0}/v2/email/configuration-sets/(?P<ConfigurationSetName>[^/]+)/vdm-options$": response.dispatch,
    "{0}/v2/email/identities/(?P<EmailIdentity>[^/]+)/dkim/signing$": SESV2Response.dispatch,
    "{0}/v2/email/identities/(?P<EmailIdentity>[^/]+)/configuration-set$": SESV2Response.dispatch,
    "{0}/v2/email/tags$": SESV2Response.dispatch,
    "{0}/v2/.*$": response.dispatch,
}
