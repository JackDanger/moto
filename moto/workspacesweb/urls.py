"""workspacesweb base URL and path."""

from .responses import WorkSpacesWebResponse

url_bases = [
    r"https?://workspaces-web\.(.+)\.amazonaws\.com",
]

url_paths = {
    # Collection endpoints (dispatch handles GET list + POST create)
    "{0}/browserSettings$": WorkSpacesWebResponse.dispatch,
    "{0}/networkSettings$": WorkSpacesWebResponse.dispatch,
    "{0}/userSettings$": WorkSpacesWebResponse.dispatch,
    "{0}/userAccessLoggingSettings$": WorkSpacesWebResponse.dispatch,
    "{0}/portals$": WorkSpacesWebResponse.dispatch,
    "{0}/ipAccessSettings$": WorkSpacesWebResponse.dispatch,
    "{0}/trustStores$": WorkSpacesWebResponse.dispatch,
    "{0}/dataProtectionSettings$": WorkSpacesWebResponse.dispatch,
    "{0}/sessionLoggers$": WorkSpacesWebResponse.dispatch,
    "{0}/identityProviders$": WorkSpacesWebResponse.dispatch,
    "{0}/tags/(?P<resourceArn>.+)$": WorkSpacesWebResponse.dispatch,
    # Portal sub-resource associations (dispatch)
    "{0}/portals/(?P<portalArn>.*)/browserSettings$": WorkSpacesWebResponse.dispatch,
    "{0}/portals/(?P<portalArn>.*)/networkSettings$": WorkSpacesWebResponse.dispatch,
    "{0}/portals/(?P<portalArn>.*)/userSettings$": WorkSpacesWebResponse.dispatch,
    "{0}/portals/(?P<portalArn>.*)/userAccessLoggingSettings$": WorkSpacesWebResponse.dispatch,
    "{0}/portals/(?P<portalArn>.*)/ipAccessSettings$": WorkSpacesWebResponse.dispatch,
    "{0}/portals/(?P<portalArn>.*)/trustStores$": WorkSpacesWebResponse.dispatch,
    "{0}/portals/(?P<portalArn>.*)/dataProtectionSettings$": WorkSpacesWebResponse.dispatch,
    "{0}/portals/(?P<portalArn>.*)/sessionLogger$": WorkSpacesWebResponse.dispatch,
    "{0}/portals/(?P<portalArn>.*)/identityProviders$": WorkSpacesWebResponse.dispatch,
    # Sessions
    "{0}/portals/(?P<portalId>[^/]+)/sessions$": WorkSpacesWebResponse.dispatch,
    "{0}/portals/(?P<portalId>[^/]+)/sessions/(?P<sessionId>[^/]+)$": WorkSpacesWebResponse.dispatch,
    # Individual resource endpoints (static handlers for GET/PATCH/PUT/DELETE)
    "{0}/portals/(?P<portalArn>.+)$": WorkSpacesWebResponse.portal,
    "{0}/portalIdp/(?P<portalArn>.+)$": WorkSpacesWebResponse.dispatch,
    "{0}/browserSettings/(?P<browserSettingsArn>.+)$": WorkSpacesWebResponse.browser_settings,
    "{0}/networkSettings/(?P<networkSettingsArn>.+)$": WorkSpacesWebResponse.network_settings,
    "{0}/userSettings/(?P<userSettingsArn>.+)$": WorkSpacesWebResponse.user_settings,
    "{0}/userAccessLoggingSettings/(?P<userAccessLoggingSettingsArn>.+)$": WorkSpacesWebResponse.user_access_logging_settings,
    "{0}/ipAccessSettings/(?P<ipAccessSettingsArn>.+)$": WorkSpacesWebResponse.ip_access_settings_resource,
    "{0}/trustStores/(?P<trustStoreArn>.+)/certificate$": WorkSpacesWebResponse.dispatch,
    "{0}/trustStores/(?P<trustStoreArn>.+)/certificates$": WorkSpacesWebResponse.dispatch,
    "{0}/trustStores/(?P<trustStoreArn>.+)$": WorkSpacesWebResponse.trust_store_resource,
    "{0}/identityProviders/(?P<identityProviderArn>.+)$": WorkSpacesWebResponse.identity_provider_resource,
    "{0}/dataProtectionSettings/(?P<dataProtectionSettingsArn>.+)$": WorkSpacesWebResponse.data_protection_settings_resource,
    "{0}/sessionLoggers/(?P<sessionLoggerArn>.+)$": WorkSpacesWebResponse.session_logger_resource,
}
