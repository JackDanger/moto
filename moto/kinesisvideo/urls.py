from .responses import KinesisVideoResponse

url_bases = [
    r"https?://kinesisvideo\.(.+)\.amazonaws.com",
]


response = KinesisVideoResponse()


url_paths = {
    "{0}/createStream$": response.dispatch,
    "{0}/describeStream$": response.dispatch,
    "{0}/updateStream$": response.dispatch,
    "{0}/deleteStream$": response.dispatch,
    "{0}/listStreams$": response.dispatch,
    "{0}/getDataEndpoint$": response.dispatch,
    "{0}/createSignalingChannel$": response.dispatch,
    "{0}/describeSignalingChannel$": response.dispatch,
    "{0}/updateSignalingChannel$": response.dispatch,
    "{0}/deleteSignalingChannel$": response.dispatch,
    "{0}/listSignalingChannels$": response.dispatch,
    "{0}/tagStream$": response.dispatch,
    "{0}/untagStream$": response.dispatch,
    "{0}/ListTagsForStream$": response.dispatch,
    "{0}/TagResource$": response.dispatch,
    "{0}/UntagResource$": response.dispatch,
    "{0}/ListTagsForResource$": response.dispatch,
}
