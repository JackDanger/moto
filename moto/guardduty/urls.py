from .responses import GuardDutyResponse

url_bases = [
    "https?://guardduty\\.(.+)\\.amazonaws\\.com",
]


url_paths = {
    "{0}/detector$": GuardDutyResponse.dispatch,
    "{0}/detector/(?P<detector_id>[^/]+)$": GuardDutyResponse.dispatch,
    "{0}/detector/(?P<detector_id>[^/]+)/administrator$": GuardDutyResponse.dispatch,
    "{0}/detector/(?P<detector_id>[^/]+)/admin$": GuardDutyResponse.dispatch,
    "{0}/detector/(?P<detector_id>[^/]+)/filter$": GuardDutyResponse.dispatch,
    "{0}/detector/(?P<detector_id>[^/]+)/filter/(?P<filter_name>[^/]+)$": GuardDutyResponse.dispatch,
    "{0}/detector/(?P<detector_id>[^/]+)/ipset$": GuardDutyResponse.dispatch,
    "{0}/detector/(?P<detector_id>[^/]+)/ipset/(?P<ip_set_id>[^/]+)$": GuardDutyResponse.dispatch,
    "{0}/detector/(?P<detector_id>[^/]+)/threatintelset$": GuardDutyResponse.dispatch,
    "{0}/detector/(?P<detector_id>[^/]+)/threatintelset/(?P<threat_intel_set_id>[^/]+)$": GuardDutyResponse.dispatch,
    "{0}/detector/(?P<detector_id>[^/]+)/findings$": GuardDutyResponse.dispatch,
    "{0}/detector/(?P<detector_id>[^/]+)/findings/get$": GuardDutyResponse.dispatch,
    "{0}/detector/(?P<detector_id>[^/]+)/findings/statistics$": GuardDutyResponse.dispatch,
    "{0}/detector/(?P<detector_id>[^/]+)/findings/create$": GuardDutyResponse.dispatch,
    "{0}/detector/(?P<detector_id>[^/]+)/master$": GuardDutyResponse.dispatch,
    "{0}/detector/(?P<detector_id>[^/]+)/member/detector/get$": GuardDutyResponse.dispatch,
    "{0}/detector/(?P<detector_id>[^/]+)/freeTrial/daysRemaining$": GuardDutyResponse.dispatch,
    "{0}/detector/(?P<detector_id>[^/]+)/usage/statistics$": GuardDutyResponse.dispatch,
    "{0}/detector/(?P<detector_id>[^/]+)/malware-scans$": GuardDutyResponse.dispatch,
    "{0}/detector/(?P<detector_id>[^/]+)/malware-scan-settings$": GuardDutyResponse.dispatch,
    "{0}/detector/(?P<detector_id>[^/]+)/publishingDestination$": GuardDutyResponse.dispatch,
    "{0}/detector/(?P<detector_id>[^/]+)/publishingDestination/(?P<destination_id>[^/]+)$": GuardDutyResponse.dispatch,
    "{0}/detector/(?P<detector_id>[^/]+)/coverage/statistics$": GuardDutyResponse.dispatch,
    "{0}/invitation$": GuardDutyResponse.dispatch,
    "{0}/admin/enable$": GuardDutyResponse.dispatch,
    "{0}/admin$": GuardDutyResponse.dispatch,
    "{0}/tags/(?P<resource_arn>.+)$": GuardDutyResponse.dispatch,
}
