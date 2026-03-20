"""ivs base URL and path."""

from .responses import IVSResponse

url_bases = [
    r"https?://ivs\.(.+)\.amazonaws\.com",
]

url_paths = {
    "{0}/CreateChannel": IVSResponse.dispatch,
    "{0}/ListChannels": IVSResponse.dispatch,
    "{0}/GetChannel": IVSResponse.dispatch,
    "{0}/BatchGetChannel": IVSResponse.dispatch,
    "{0}/UpdateChannel": IVSResponse.dispatch,
    "{0}/DeleteChannel": IVSResponse.dispatch,
    "{0}/CreateStreamKey": IVSResponse.dispatch,
    "{0}/GetStreamKey": IVSResponse.dispatch,
    "{0}/DeleteStreamKey": IVSResponse.dispatch,
    "{0}/BatchGetStreamKey": IVSResponse.dispatch,
    "{0}/ListStreamKeys": IVSResponse.dispatch,
    "{0}/ImportPlaybackKeyPair": IVSResponse.dispatch,
    "{0}/GetPlaybackKeyPair": IVSResponse.dispatch,
    "{0}/DeletePlaybackKeyPair": IVSResponse.dispatch,
    "{0}/ListPlaybackKeyPairs": IVSResponse.dispatch,
    "{0}/CreatePlaybackRestrictionPolicy": IVSResponse.dispatch,
    "{0}/GetPlaybackRestrictionPolicy": IVSResponse.dispatch,
    "{0}/UpdatePlaybackRestrictionPolicy": IVSResponse.dispatch,
    "{0}/DeletePlaybackRestrictionPolicy": IVSResponse.dispatch,
    "{0}/ListPlaybackRestrictionPolicies": IVSResponse.dispatch,
    "{0}/ListStreams": IVSResponse.dispatch,
    "{0}/StopStream": IVSResponse.dispatch,
    "{0}/PutMetadata": IVSResponse.dispatch,
    "{0}/ListStreamSessions": IVSResponse.dispatch,
    "{0}/GetStreamSession": IVSResponse.dispatch,
    "{0}/StartViewerSessionRevocation": IVSResponse.dispatch,
    "{0}/BatchStartViewerSessionRevocation": IVSResponse.dispatch,
    "{0}/CreateRecordingConfiguration": IVSResponse.dispatch,
    "{0}/GetRecordingConfiguration": IVSResponse.dispatch,
    "{0}/DeleteRecordingConfiguration": IVSResponse.dispatch,
    "{0}/ListRecordingConfigurations": IVSResponse.dispatch,
    "{0}/TagResource": IVSResponse.dispatch,
    "{0}/UntagResource": IVSResponse.dispatch,
    "{0}/ListTagsForResource": IVSResponse.dispatch,
    "{0}/tags/(?P<resourceArn>.+)$": IVSResponse.dispatch,
}
