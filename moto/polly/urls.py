from .responses import PollyResponse

url_bases = [r"https?://polly\.(.+)\.amazonaws.com"]

url_paths = {
    "{0}/v1/voices": PollyResponse.dispatch,
    "{0}/v1/lexicons/(?P<lexicon>[^/]+)": PollyResponse.dispatch,
    "{0}/v1/lexicons": PollyResponse.dispatch,
    "{0}/v1/speech": PollyResponse.dispatch,
    "{0}/v1/synthesisTasks/(?P<task_id>[^/]+)": PollyResponse.dispatch,
    "{0}/v1/synthesisTasks": PollyResponse.dispatch,
}
