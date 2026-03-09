from .responses import XRayResponse

url_bases = [r"https?://xray\.(.+)\.amazonaws.com"]

url_paths = {
    "{0}/TelemetryRecords$": XRayResponse.dispatch,
    "{0}/TraceSegments$": XRayResponse.dispatch,
    "{0}/Traces$": XRayResponse.dispatch,
    "{0}/ServiceGraph$": XRayResponse.dispatch,
    "{0}/TraceGraph$": XRayResponse.dispatch,
    "{0}/TraceSummaries$": XRayResponse.dispatch,
    "{0}/PutResourcePolicy$": XRayResponse.dispatch,
    "{0}/ListResourcePolicies$": XRayResponse.dispatch,
    "{0}/DeleteResourcePolicy$": XRayResponse.dispatch,
    "{0}/TagResource$": XRayResponse.dispatch,
    "{0}/UntagResource$": XRayResponse.dispatch,
    "{0}/ListTagsForResource$": XRayResponse.dispatch,
    "{0}/SamplingTargets$": XRayResponse.dispatch,
    "{0}/InsightSummaries$": XRayResponse.dispatch,
    "{0}/Insight$": XRayResponse.dispatch,
    "{0}/InsightEvents$": XRayResponse.dispatch,
    "{0}/InsightImpactGraph$": XRayResponse.dispatch,
    "{0}/TimeSeriesServiceStatistics$": XRayResponse.dispatch,
    "{0}/GetIndexingRules$": XRayResponse.dispatch,
    "{0}/StartTraceRetrieval$": XRayResponse.dispatch,
    "{0}/CancelTraceRetrieval$": XRayResponse.dispatch,
    "{0}/GetRetrievedTracesGraph$": XRayResponse.dispatch,
    "{0}/ListRetrievedTraces$": XRayResponse.dispatch,
}
