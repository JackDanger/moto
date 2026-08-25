"""pinpoint base URL and path."""

from .responses import PinpointResponse

url_bases = [
    r"https?://pinpoint\.(.+)\.amazonaws\.com",
]

dispatch = PinpointResponse.dispatch

url_paths = {
    # Apps
    "{0}/v1/apps$": dispatch,
    "{0}/v1/apps/(?P<app_id>[^/]+)$": dispatch,
    "{0}/v1/apps/(?P<app_id>[^/]+)/settings$": dispatch,
    # Event Stream
    "{0}/v1/apps/(?P<app_id>[^/]+)/eventstream$": dispatch,
    # Campaigns
    "{0}/v1/apps/(?P<app_id>[^/]+)/campaigns$": dispatch,
    "{0}/v1/apps/(?P<app_id>[^/]+)/campaigns/(?P<campaign_id>[^/]+)$": dispatch,
    "{0}/v1/apps/(?P<app_id>[^/]+)/campaigns/(?P<campaign_id>[^/]+)/versions$": dispatch,
    "{0}/v1/apps/(?P<app_id>[^/]+)/campaigns/(?P<campaign_id>[^/]+)/versions/(?P<version>[^/]+)$": dispatch,
    "{0}/v1/apps/(?P<app_id>[^/]+)/campaigns/(?P<campaign_id>[^/]+)/activities$": dispatch,
    "{0}/v1/apps/(?P<app_id>[^/]+)/campaigns/(?P<campaign_id>[^/]+)/kpis/daterange/(?P<kpi_name>[^/]+)$": dispatch,
    # Segments
    "{0}/v1/apps/(?P<app_id>[^/]+)/segments$": dispatch,
    "{0}/v1/apps/(?P<app_id>[^/]+)/segments/(?P<segment_id>[^/]+)$": dispatch,
    "{0}/v1/apps/(?P<app_id>[^/]+)/segments/(?P<segment_id>[^/]+)/versions$": dispatch,
    "{0}/v1/apps/(?P<app_id>[^/]+)/segments/(?P<segment_id>[^/]+)/versions/(?P<version>[^/]+)$": dispatch,
    "{0}/v1/apps/(?P<app_id>[^/]+)/segments/(?P<segment_id>[^/]+)/jobs/export$": dispatch,
    "{0}/v1/apps/(?P<app_id>[^/]+)/segments/(?P<segment_id>[^/]+)/jobs/import$": dispatch,
    # Journeys
    "{0}/v1/apps/(?P<app_id>[^/]+)/journeys$": dispatch,
    "{0}/v1/apps/(?P<app_id>[^/]+)/journeys/(?P<journey_id>[^/]+)$": dispatch,
    "{0}/v1/apps/(?P<app_id>[^/]+)/journeys/(?P<journey_id>[^/]+)/state$": dispatch,
    "{0}/v1/apps/(?P<app_id>[^/]+)/journeys/(?P<journey_id>[^/]+)/kpis/daterange/(?P<kpi_name>[^/]+)$": dispatch,
    "{0}/v1/apps/(?P<app_id>[^/]+)/journeys/(?P<journey_id>[^/]+)/execution-metrics$": dispatch,
    "{0}/v1/apps/(?P<app_id>[^/]+)/journeys/(?P<journey_id>[^/]+)/activities/(?P<activity_id>[^/]+)/execution-metrics$": dispatch,
    "{0}/v1/apps/(?P<app_id>[^/]+)/journeys/(?P<journey_id>[^/]+)/runs$": dispatch,
    "{0}/v1/apps/(?P<app_id>[^/]+)/journeys/(?P<journey_id>[^/]+)/runs/(?P<run_id>[^/]+)/execution-metrics$": dispatch,
    "{0}/v1/apps/(?P<app_id>[^/]+)/journeys/(?P<journey_id>[^/]+)/runs/(?P<run_id>[^/]+)/activities/(?P<activity_id>[^/]+)/execution-metrics$": dispatch,
    # Channels (specific types)
    "{0}/v1/apps/(?P<app_id>[^/]+)/channels$": dispatch,
    "{0}/v1/apps/(?P<app_id>[^/]+)/channels/adm$": dispatch,
    "{0}/v1/apps/(?P<app_id>[^/]+)/channels/apns$": dispatch,
    "{0}/v1/apps/(?P<app_id>[^/]+)/channels/apns_sandbox$": dispatch,
    "{0}/v1/apps/(?P<app_id>[^/]+)/channels/apns_voip$": dispatch,
    "{0}/v1/apps/(?P<app_id>[^/]+)/channels/apns_voip_sandbox$": dispatch,
    "{0}/v1/apps/(?P<app_id>[^/]+)/channels/baidu$": dispatch,
    "{0}/v1/apps/(?P<app_id>[^/]+)/channels/email$": dispatch,
    "{0}/v1/apps/(?P<app_id>[^/]+)/channels/gcm$": dispatch,
    "{0}/v1/apps/(?P<app_id>[^/]+)/channels/sms$": dispatch,
    "{0}/v1/apps/(?P<app_id>[^/]+)/channels/voice$": dispatch,
    # Endpoints
    "{0}/v1/apps/(?P<app_id>[^/]+)/endpoints$": dispatch,
    "{0}/v1/apps/(?P<app_id>[^/]+)/endpoints/(?P<endpoint_id>[^/]+)$": dispatch,
    "{0}/v1/apps/(?P<app_id>[^/]+)/endpoints/(?P<endpoint_id>[^/]+)/inappmessages$": dispatch,
    # Users
    "{0}/v1/apps/(?P<app_id>[^/]+)/users/(?P<user_id>[^/]+)$": dispatch,
    # Export/Import Jobs
    "{0}/v1/apps/(?P<app_id>[^/]+)/jobs/export$": dispatch,
    "{0}/v1/apps/(?P<app_id>[^/]+)/jobs/export/(?P<job_id>[^/]+)$": dispatch,
    "{0}/v1/apps/(?P<app_id>[^/]+)/jobs/import$": dispatch,
    "{0}/v1/apps/(?P<app_id>[^/]+)/jobs/import/(?P<job_id>[^/]+)$": dispatch,
    # Events
    "{0}/v1/apps/(?P<app_id>[^/]+)/events$": dispatch,
    # Messages
    "{0}/v1/apps/(?P<app_id>[^/]+)/messages$": dispatch,
    "{0}/v1/apps/(?P<app_id>[^/]+)/users-messages$": dispatch,
    "{0}/v1/apps/(?P<app_id>[^/]+)/otp$": dispatch,
    "{0}/v1/apps/(?P<app_id>[^/]+)/verify-otp$": dispatch,
    # KPI
    "{0}/v1/apps/(?P<app_id>[^/]+)/kpis/daterange/(?P<kpi_name>[^/]+)$": dispatch,
    # Attributes
    "{0}/v1/apps/(?P<app_id>[^/]+)/attributes/(?P<attribute_type>[^/]+)$": dispatch,
    # Templates
    "{0}/v1/templates$": dispatch,
    "{0}/v1/templates/(?P<template_name>[^/]+)/email$": dispatch,
    "{0}/v1/templates/(?P<template_name>[^/]+)/sms$": dispatch,
    "{0}/v1/templates/(?P<template_name>[^/]+)/push$": dispatch,
    "{0}/v1/templates/(?P<template_name>[^/]+)/voice$": dispatch,
    "{0}/v1/templates/(?P<template_name>[^/]+)/inapp$": dispatch,
    "{0}/v1/templates/(?P<template_name>[^/]+)/(?P<template_type>[^/]+)/versions$": dispatch,
    "{0}/v1/templates/(?P<template_name>[^/]+)/(?P<template_type>[^/]+)/active-version$": dispatch,
    # Recommenders
    "{0}/v1/recommenders$": dispatch,
    "{0}/v1/recommenders/(?P<recommender_id>[^/]+)$": dispatch,
    # Phone
    "{0}/v1/phone/number/validate$": dispatch,
    # Tags
    "{0}/v1/tags/(?P<app_arn>[^/]+)$": dispatch,
    "{0}/v1/tags/(?P<app_arn_pt_1>[^/]+)/(?P<app_arn_pt_2>[^/]+)$": dispatch,
}
