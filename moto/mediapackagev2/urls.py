"""mediapackagev2 base URL and path."""

from .responses import mediapackagev2Response

url_bases = [
    r"https?://mediapackagev2\.(.+)\.amazonaws\.com",
]

url_paths = {
    # Channel Groups
    "{0}/channelGroup$": mediapackagev2Response.dispatch,
    "{0}/channelGroup/(?P<ChannelGroupName>[^/]+)$": mediapackagev2Response.dispatch,
    # Channels
    "{0}/channelGroup/(?P<ChannelGroupName>[^/]+)/channel$": mediapackagev2Response.dispatch,
    "{0}/channelGroup/(?P<ChannelGroupName>[^/]+)/channel/(?P<ChannelName>[^/]+)/$": mediapackagev2Response.dispatch,
    # Channel Policy
    "{0}/channelGroup/(?P<ChannelGroupName>[^/]+)/channel/(?P<ChannelName>[^/]+)/policy$": mediapackagev2Response.dispatch,
    # Channel Reset
    "{0}/channelGroup/(?P<ChannelGroupName>[^/]+)/channel/(?P<ChannelName>[^/]+)/reset$": mediapackagev2Response.dispatch,
    # Origin Endpoints
    "{0}/channelGroup/(?P<ChannelGroupName>[^/]+)/channel/(?P<ChannelName>[^/]+)/originEndpoint$": mediapackagev2Response.dispatch,
    "{0}/channelGroup/(?P<ChannelGroupName>[^/]+)/channel/(?P<ChannelName>[^/]+)/originEndpoint/(?P<OriginEndpointName>[^/]+)$": mediapackagev2Response.dispatch,
    # Origin Endpoint Policy
    "{0}/channelGroup/(?P<ChannelGroupName>[^/]+)/channel/(?P<ChannelName>[^/]+)/originEndpoint/(?P<OriginEndpointName>[^/]+)/policy$": mediapackagev2Response.dispatch,
    # Origin Endpoint Reset
    "{0}/channelGroup/(?P<ChannelGroupName>[^/]+)/channel/(?P<ChannelName>[^/]+)/originEndpoint/(?P<OriginEndpointName>[^/]+)/reset$": mediapackagev2Response.dispatch,
    # Harvest Jobs
    "{0}/channelGroup/(?P<ChannelGroupName>[^/]+)/harvestJob$": mediapackagev2Response.dispatch,
    "{0}/channelGroup/(?P<ChannelGroupName>[^/]+)/channel/(?P<ChannelName>[^/]+)/originEndpoint/(?P<OriginEndpointName>[^/]+)/harvestJob$": mediapackagev2Response.dispatch,
    "{0}/channelGroup/(?P<ChannelGroupName>[^/]+)/channel/(?P<ChannelName>[^/]+)/originEndpoint/(?P<OriginEndpointName>[^/]+)/harvestJob/(?P<HarvestJobName>[^/]+)$": mediapackagev2Response.dispatch,
    # Tags
    "{0}/tags/(?P<ResourceArn>.+)$": mediapackagev2Response.dispatch,
}
