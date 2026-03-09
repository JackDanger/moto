"""s3control base URL and path."""

from .responses import S3ControlResponse

url_bases = [
    r"https?://([0-9]+)\.s3-control\.(.+)\.amazonaws\.com",
]


url_paths = {
    r"{0}/v20180820/accesspoint$": S3ControlResponse.dispatch,
    r"{0}/v20180820/configuration/publicAccessBlock$": S3ControlResponse.dispatch,
    r"{0}/v20180820/accesspoint/(?P<name>[\w_:%-]+)$": S3ControlResponse.dispatch,
    r"{0}/v20180820/accesspoint/(?P<name>[\w_:%-]+)/policy$": S3ControlResponse.dispatch,
    r"{0}/v20180820/accesspoint/(?P<name>[\w_:%-]+)/policyStatus$": S3ControlResponse.dispatch,
    r"{0}/v20180820/async-requests/mrap.*$": S3ControlResponse.dispatch,
    r"{0}/v20180820/mrap/instances.*$": S3ControlResponse.dispatch,
    "{0}/v20180820/storagelens/(?P<storagelensid>[^/]+)$": S3ControlResponse.dispatch,
    "{0}/v20180820/storagelens/(?P<storagelensid>[^/]+)/tagging$": S3ControlResponse.dispatch,
    "{0}/v20180820/storagelens$": S3ControlResponse.dispatch,
    r"{0}/v20180820/tags/(?P<arn>[\w_:%-]+)$": S3ControlResponse.dispatch,
    "/v20180820/accesspoint": S3ControlResponse.dispatch,
    "/v20180820/configuration/publicAccessBlock": S3ControlResponse.dispatch,
    "/v20180820/accesspoint/<name>": S3ControlResponse.dispatch,
    "/v20180820/accesspoint/<name>/policy": S3ControlResponse.dispatch,
    "/v20180820/accesspoint/<name>/policyStatus": S3ControlResponse.dispatch,
    "/v20180820/async-requests/mrap/create": S3ControlResponse.dispatch,
    "/v20180820/async-requests/mrap/delete": S3ControlResponse.dispatch,
    "/v20180820/async-requests/mrap/put-policy": S3ControlResponse.dispatch,
    "/v20180820/async-requests/mrap/<path:request_token_arn>": S3ControlResponse.dispatch,
    "/v20180820/mrap/instances": S3ControlResponse.dispatch,
    "/v20180820/mrap/instances/<mrap_name>": S3ControlResponse.dispatch,
    "/v20180820/mrap/instances/<mrap_name>/policy": S3ControlResponse.dispatch,
    "/v20180820/mrap/instances/<mrap_name>/policystatus": S3ControlResponse.dispatch,
    "/v20180820/storagelens/<storagelensid>": S3ControlResponse.dispatch,
    "/v20180820/storagelens/<storagelensid>/tagging": S3ControlResponse.dispatch,
    "/v20180820/storagelens": S3ControlResponse.dispatch,
    "/v20180820/tags/<arn>": S3ControlResponse.dispatch,
    # Access Grants Instance
    r"{0}/v20180820/accessgrantsinstance$": S3ControlResponse.dispatch,
    r"{0}/v20180820/accessgrantsinstance/resourcepolicy$": S3ControlResponse.dispatch,
    r"{0}/v20180820/accessgrantsinstance/prefix$": S3ControlResponse.dispatch,
    r"{0}/v20180820/accessgrantsinstances$": S3ControlResponse.dispatch,
    # Access Grants Locations
    r"{0}/v20180820/accessgrantsinstance/location$": S3ControlResponse.dispatch,
    r"{0}/v20180820/accessgrantsinstance/locations$": S3ControlResponse.dispatch,
    r"{0}/v20180820/accessgrantsinstance/location/(?P<location_id>[^/]+)$": S3ControlResponse.dispatch,
    # Access Grants
    r"{0}/v20180820/accessgrantsinstance/grant$": S3ControlResponse.dispatch,
    r"{0}/v20180820/accessgrantsinstance/grants$": S3ControlResponse.dispatch,
    r"{0}/v20180820/accessgrantsinstance/grant/(?P<grant_id>[^/]+)$": S3ControlResponse.dispatch,
    # Flask-style routes
    "/v20180820/accessgrantsinstance": S3ControlResponse.dispatch,
    "/v20180820/accessgrantsinstance/resourcepolicy": S3ControlResponse.dispatch,
    "/v20180820/accessgrantsinstance/prefix": S3ControlResponse.dispatch,
    "/v20180820/accessgrantsinstances": S3ControlResponse.dispatch,
    "/v20180820/accessgrantsinstance/location": S3ControlResponse.dispatch,
    "/v20180820/accessgrantsinstance/locations": S3ControlResponse.dispatch,
    "/v20180820/accessgrantsinstance/location/<location_id>": S3ControlResponse.dispatch,
    "/v20180820/accessgrantsinstance/grant": S3ControlResponse.dispatch,
    "/v20180820/accessgrantsinstance/grants": S3ControlResponse.dispatch,
    "/v20180820/accessgrantsinstance/grant/<grant_id>": S3ControlResponse.dispatch,
    # Jobs
    r"{0}/v20180820/jobs$": S3ControlResponse.dispatch,
    r"{0}/v20180820/jobs/(?P<job_id>[^/]+)$": S3ControlResponse.dispatch,
    "/v20180820/jobs": S3ControlResponse.dispatch,
    "/v20180820/jobs/<job_id>": S3ControlResponse.dispatch,
    # Job priority/status
    r"{0}/v20180820/jobs/(?P<job_id>[^/]+)/priority$": S3ControlResponse.dispatch,
    r"{0}/v20180820/jobs/(?P<job_id>[^/]+)/status$": S3ControlResponse.dispatch,
    "/v20180820/jobs/<job_id>/priority": S3ControlResponse.dispatch,
    "/v20180820/jobs/<job_id>/status": S3ControlResponse.dispatch,
    # MRAP routes
    r"{0}/v20180820/mrap/instances/(?P<mrap_name>[^/]+)/routes$": S3ControlResponse.dispatch,
    "/v20180820/mrap/instances/<mrap_name>/routes": S3ControlResponse.dispatch,
    # Bucket-level operations
    r"{0}/v20180820/bucket/(?P<bucket>[^/]+)/lifecycleconfiguration$": S3ControlResponse.dispatch,
    r"{0}/v20180820/bucket/(?P<bucket>[^/]+)/policy$": S3ControlResponse.dispatch,
    r"{0}/v20180820/bucket/(?P<bucket>[^/]+)/replication$": S3ControlResponse.dispatch,
    r"{0}/v20180820/bucket/(?P<bucket>[^/]+)/tagging$": S3ControlResponse.dispatch,
    r"{0}/v20180820/bucket/(?P<bucket>[^/]+)/versioning$": S3ControlResponse.dispatch,
    "/v20180820/bucket/<bucket>/lifecycleconfiguration": S3ControlResponse.dispatch,
    "/v20180820/bucket/<bucket>/policy": S3ControlResponse.dispatch,
    "/v20180820/bucket/<bucket>/replication": S3ControlResponse.dispatch,
    "/v20180820/bucket/<bucket>/tagging": S3ControlResponse.dispatch,
    "/v20180820/bucket/<bucket>/versioning": S3ControlResponse.dispatch,
}
