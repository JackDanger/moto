from .responses import MediaPackageResponse

url_bases = [
    r"https?://mediapackage\.(.+)\.amazonaws.com",
]


response = MediaPackageResponse()


url_paths = {
    "{0}/channels$": response.dispatch,
    "{0}/channels/(?P<channelid>[^/.]+)$": response.dispatch,
    "{0}/origin_endpoints$": response.dispatch,
    "{0}/origin_endpoints/(?P<id>[^/.]+)$": response.dispatch,
    "{0}/harvest_jobs$": response.dispatch,
    "{0}/harvest_jobs/(?P<id>[^/.]+)$": response.dispatch,
    "{0}/tags/(?P<resource_arn>.+)$": response.dispatch,
}
