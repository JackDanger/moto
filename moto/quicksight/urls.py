"""quicksight base URL and path."""

from .responses import QuickSightResponse

url_bases = [
    r"https?://quicksight\.(.+)\.amazonaws\.com",
]

dispatch = QuickSightResponse.dispatch

url_paths = {
    # --- Tagging ---
    r"{0}/resources/(?P<resource_arn>[^/].+)/tags$": dispatch,

    # --- Account (note: /account/ not /accounts/) ---
    r"{0}/account/(?P<account_id>[^/]+)$": dispatch,

    # --- Account Settings / Customization / Misc ---
    r"{0}/accounts/(?P<account_id>[^/]+)/settings$": dispatch,
    r"{0}/accounts/(?P<account_id>[^/]+)/public-sharing-settings$": dispatch,
    r"{0}/accounts/(?P<account_id>[^/]+)/customizations$": dispatch,
    r"{0}/accounts/(?P<account_id>[^/]+)/custom-permission$": dispatch,
    r"{0}/accounts/(?P<account_id>[^/]+)/custom-permissions$": dispatch,
    r"{0}/accounts/(?P<account_id>[^/]+)/custom-permissions/(?P<custom_permissions_name>[^/]+)$": dispatch,
    r"{0}/accounts/(?P<account_id>[^/]+)/ip-restriction$": dispatch,
    r"{0}/accounts/(?P<account_id>[^/]+)/key-registration$": dispatch,
    r"{0}/accounts/(?P<account_id>[^/]+)/spice-capacity-configuration$": dispatch,
    r"{0}/accounts/(?P<account_id>[^/]+)/q-personalization-configuration$": dispatch,
    r"{0}/accounts/(?P<account_id>[^/]+)/quicksight-q-search-configuration$": dispatch,
    r"{0}/accounts/(?P<account_id>[^/]+)/application-with-token-exchange-grant$": dispatch,
    r"{0}/accounts/(?P<account_id>[^/]+)/default-qbusiness-application$": dispatch,
    r"{0}/accounts/(?P<account_id>[^/]+)/dashboards-qa-configuration$": dispatch,
    r"{0}/accounts/(?P<account_id>[^/]+)/qa/predict$": dispatch,
    r"{0}/accounts/(?P<account_id>[^/]+)/identity-context$": dispatch,

    # --- Identity Propagation ---
    r"{0}/accounts/(?P<account_id>[^/]+)/identity-propagation-config$": dispatch,
    r"{0}/accounts/(?P<account_id>[^/]+)/identity-propagation-config/(?P<service>[^/]+)$": dispatch,

    # --- Session Embed URL ---
    r"{0}/accounts/(?P<account_id>[^/]+)/session-embed-url$": dispatch,

    # --- Embed URLs ---
    r"{0}/accounts/(?P<account_id>[^/]+)/embed-url/anonymous-user$": dispatch,
    r"{0}/accounts/(?P<account_id>[^/]+)/embed-url/registered-user$": dispatch,
    r"{0}/accounts/(?P<account_id>[^/]+)/embed-url/registered-user-with-identity$": dispatch,

    # --- DataSet ---
    r"{0}/accounts/(?P<account_id>[^/]+)/data-sets$": dispatch,
    r"{0}/accounts/(?P<account_id>[^/]+)/data-sets/(?P<datasetid>[^/]+)$": dispatch,
    r"{0}/accounts/(?P<account_id>[^/]+)/data-sets/(?P<datasetid>[^/]+)/permissions$": dispatch,
    r"{0}/accounts/(?P<account_id>[^/]+)/data-sets/(?P<datasetid>[^/]+)/refresh-properties$": dispatch,

    # --- DataSet Ingestion ---
    r"{0}/accounts/(?P<account_id>[^/]+)/data-sets/(?P<datasetid>[^/]+)/ingestions$": dispatch,
    r"{0}/accounts/(?P<account_id>[^/]+)/data-sets/(?P<datasetid>[^/]+)/ingestions/(?P<ingestionid>[^/]+)$": dispatch,

    # --- DataSet Refresh Schedule ---
    r"{0}/accounts/(?P<account_id>[^/]+)/data-sets/(?P<datasetid>[^/]+)/refresh-schedules$": dispatch,
    r"{0}/accounts/(?P<account_id>[^/]+)/data-sets/(?P<datasetid>[^/]+)/refresh-schedules/(?P<scheduleid>[^/]+)$": dispatch,

    # --- DataSource ---
    r"{0}/accounts/(?P<account_id>[^/]+)/data-sources$": dispatch,
    r"{0}/accounts/(?P<account_id>[^/]+)/data-sources/(?P<datasourceid>[^/]+)$": dispatch,
    r"{0}/accounts/(?P<account_id>[^/]+)/data-sources/(?P<datasourceid>[^/]+)/permissions$": dispatch,

    # --- Dashboard ---
    r"{0}/accounts/(?P<account_id>[^/]+)/dashboards$": dispatch,
    r"{0}/accounts/(?P<account_id>[^/]+)/dashboards/(?P<dashboard_id>[^/]+)$": dispatch,
    r"{0}/accounts/(?P<account_id>[^/]+)/dashboards/(?P<dashboard_id>[^/]+)/definition$": dispatch,
    r"{0}/accounts/(?P<account_id>[^/]+)/dashboards/(?P<dashboard_id>[^/]+)/permissions$": dispatch,
    r"{0}/accounts/(?P<account_id>[^/]+)/dashboards/(?P<dashboard_id>[^/]+)/versions$": dispatch,
    r"{0}/accounts/(?P<account_id>[^/]+)/dashboards/(?P<dashboard_id>[^/]+)/versions/(?P<version_number>[^/]+)$": dispatch,
    r"{0}/accounts/(?P<account_id>[^/]+)/dashboards/(?P<dashboard_id>[^/]+)/linked-entities$": dispatch,
    r"{0}/accounts/(?P<account_id>[^/]+)/dashboards/(?P<dashboard_id>[^/]+)/embed-url$": dispatch,
    r"{0}/accounts/(?P<account_id>[^/]+)/dashboards/(?P<dashboard_id>[^/]+)/snapshot-jobs$": dispatch,
    r"{0}/accounts/(?P<account_id>[^/]+)/dashboards/(?P<dashboard_id>[^/]+)/snapshot-jobs/(?P<snapshot_job_id>[^/]+)$": dispatch,
    r"{0}/accounts/(?P<account_id>[^/]+)/dashboards/(?P<dashboard_id>[^/]+)/snapshot-jobs/(?P<snapshot_job_id>[^/]+)/result$": dispatch,
    r"{0}/accounts/(?P<account_id>[^/]+)/dashboards/(?P<dashboard_id>[^/]+)/schedules/(?P<schedule_id>[^/]+)$": dispatch,

    # --- Analysis ---
    r"{0}/accounts/(?P<account_id>[^/]+)/analyses$": dispatch,
    r"{0}/accounts/(?P<account_id>[^/]+)/analyses/(?P<analysis_id>[^/]+)$": dispatch,
    r"{0}/accounts/(?P<account_id>[^/]+)/analyses/(?P<analysis_id>[^/]+)/definition$": dispatch,
    r"{0}/accounts/(?P<account_id>[^/]+)/analyses/(?P<analysis_id>[^/]+)/permissions$": dispatch,
    r"{0}/accounts/(?P<account_id>[^/]+)/restore/analyses/(?P<analysis_id>[^/]+)$": dispatch,

    # --- Template ---
    r"{0}/accounts/(?P<account_id>[^/]+)/templates$": dispatch,
    r"{0}/accounts/(?P<account_id>[^/]+)/templates/(?P<template_id>[^/]+)$": dispatch,
    r"{0}/accounts/(?P<account_id>[^/]+)/templates/(?P<template_id>[^/]+)/definition$": dispatch,
    r"{0}/accounts/(?P<account_id>[^/]+)/templates/(?P<template_id>[^/]+)/permissions$": dispatch,
    r"{0}/accounts/(?P<account_id>[^/]+)/templates/(?P<template_id>[^/]+)/versions$": dispatch,
    r"{0}/accounts/(?P<account_id>[^/]+)/templates/(?P<template_id>[^/]+)/aliases$": dispatch,
    r"{0}/accounts/(?P<account_id>[^/]+)/templates/(?P<template_id>[^/]+)/aliases/(?P<alias_name>[^/]+)$": dispatch,

    # --- Theme ---
    r"{0}/accounts/(?P<account_id>[^/]+)/themes$": dispatch,
    r"{0}/accounts/(?P<account_id>[^/]+)/themes/(?P<theme_id>[^/]+)$": dispatch,
    r"{0}/accounts/(?P<account_id>[^/]+)/themes/(?P<theme_id>[^/]+)/permissions$": dispatch,
    r"{0}/accounts/(?P<account_id>[^/]+)/themes/(?P<theme_id>[^/]+)/versions$": dispatch,
    r"{0}/accounts/(?P<account_id>[^/]+)/themes/(?P<theme_id>[^/]+)/aliases$": dispatch,
    r"{0}/accounts/(?P<account_id>[^/]+)/themes/(?P<theme_id>[^/]+)/aliases/(?P<alias_name>[^/]+)$": dispatch,

    # --- Folder ---
    r"{0}/accounts/(?P<account_id>[^/]+)/folders$": dispatch,
    r"{0}/accounts/(?P<account_id>[^/]+)/folders/(?P<folder_id>[^/]+)$": dispatch,
    r"{0}/accounts/(?P<account_id>[^/]+)/folders/(?P<folder_id>[^/]+)/permissions$": dispatch,
    r"{0}/accounts/(?P<account_id>[^/]+)/folders/(?P<folder_id>[^/]+)/resolved-permissions$": dispatch,
    r"{0}/accounts/(?P<account_id>[^/]+)/folders/(?P<folder_id>[^/]+)/members$": dispatch,
    r"{0}/accounts/(?P<account_id>[^/]+)/folders/(?P<folder_id>[^/]+)/members/(?P<member_type>[^/]+)/(?P<member_id>[^/]+)$": dispatch,
    r"{0}/accounts/(?P<account_id>[^/]+)/resource/(?P<resource_arn>[^/]+)/folders$": dispatch,

    # --- Topic ---
    r"{0}/accounts/(?P<account_id>[^/]+)/topics$": dispatch,
    r"{0}/accounts/(?P<account_id>[^/]+)/topics/(?P<topic_id>[^/]+)$": dispatch,
    r"{0}/accounts/(?P<account_id>[^/]+)/topics/(?P<topic_id>[^/]+)/permissions$": dispatch,
    r"{0}/accounts/(?P<account_id>[^/]+)/topics/(?P<topic_id>[^/]+)/refresh/(?P<refresh_id>[^/]+)$": dispatch,
    r"{0}/accounts/(?P<account_id>[^/]+)/topics/(?P<topic_id>[^/]+)/schedules$": dispatch,
    r"{0}/accounts/(?P<account_id>[^/]+)/topics/(?P<topic_id>[^/]+)/schedules/(?P<dataset_id>[^/]+)$": dispatch,
    r"{0}/accounts/(?P<account_id>[^/]+)/topics/(?P<topic_id>[^/]+)/batch-create-reviewed-answers$": dispatch,
    r"{0}/accounts/(?P<account_id>[^/]+)/topics/(?P<topic_id>[^/]+)/batch-delete-reviewed-answers$": dispatch,
    r"{0}/accounts/(?P<account_id>[^/]+)/topics/(?P<topic_id>[^/]+)/reviewed-answers$": dispatch,

    # --- VPCConnection ---
    r"{0}/accounts/(?P<account_id>[^/]+)/vpc-connections$": dispatch,
    r"{0}/accounts/(?P<account_id>[^/]+)/vpc-connections/(?P<vpc_connection_id>[^/]+)$": dispatch,

    # --- Namespace ---
    r"{0}/accounts/(?P<account_id>[^/]+)/namespaces$": dispatch,
    r"{0}/accounts/(?P<account_id>[^/]+)/namespaces/(?P<namespace>[^/]+)$": dispatch,

    # --- Namespace: Groups ---
    r"{0}/accounts/(?P<account_id>[^/]+)/namespaces/(?P<namespace>[a-zA-Z0-9._-]+)/groups$": dispatch,
    r"{0}/accounts/(?P<account_id>[^/]+)/namespaces/(?P<namespace>[a-zA-Z0-9._-]+)/groups/(?P<groupname>[^/]+)$": dispatch,
    r"{0}/accounts/(?P<account_id>[^/]+)/namespaces/(?P<namespace>[a-zA-Z0-9._-]+)/groups/(?P<groupname>[^/]+)/members$": dispatch,
    r"{0}/accounts/(?P<account_id>[^/]+)/namespaces/(?P<namespace>[a-zA-Z0-9._-]+)/groups/(?P<groupname>[^/]+)/members/(?P<username>[^/]+)$": dispatch,
    r"{0}/accounts/(?P<account_id>[^/]+)/namespaces/(?P<namespace>[a-zA-Z0-9._-]+)/groups-search$": dispatch,

    # --- Namespace: Users ---
    r"{0}/accounts/(?P<account_id>[^/]+)/namespaces/(?P<namespace>[a-zA-Z0-9._-]+)/users$": dispatch,
    r"{0}/accounts/(?P<account_id>[^/]+)/namespaces/(?P<namespace>[a-zA-Z0-9._-]+)/users/(?P<username>[^/]+)$": dispatch,
    r"{0}/accounts/(?P<account_id>[^/]+)/namespaces/(?P<namespace>[a-zA-Z0-9._-]+)/users/(?P<username>[^/]+)/groups$": dispatch,
    r"{0}/accounts/(?P<account_id>[^/]+)/namespaces/(?P<namespace>[a-zA-Z0-9._-]+)/users/(?P<username>[^/]+)/iam-policy-assignments$": dispatch,
    r"{0}/accounts/(?P<account_id>[^/]+)/namespaces/(?P<namespace>[a-zA-Z0-9._-]+)/users/(?P<username>[^/]+)/custom-permission$": dispatch,
    r"{0}/accounts/(?P<account_id>[^/]+)/namespaces/(?P<namespace>[a-zA-Z0-9._-]+)/user-principals/(?P<principal_id>[^/]+)$": dispatch,

    # --- Namespace: IAM Policy Assignments ---
    r"{0}/accounts/(?P<account_id>[^/]+)/namespaces/(?P<namespace>[a-zA-Z0-9._-]+)/iam-policy-assignments/$": dispatch,
    r"{0}/accounts/(?P<account_id>[^/]+)/namespaces/(?P<namespace>[a-zA-Z0-9._-]+)/v2/iam-policy-assignments$": dispatch,
    r"{0}/accounts/(?P<account_id>[^/]+)/namespace/(?P<namespace>[a-zA-Z0-9._-]+)/iam-policy-assignments/(?P<assignment_name>[^/]+)$": dispatch,
    r"{0}/accounts/(?P<account_id>[^/]+)/namespaces/(?P<namespace>[a-zA-Z0-9._-]+)/iam-policy-assignments/(?P<assignment_name>[^/]+)$": dispatch,

    # --- Namespace: Roles ---
    r"{0}/accounts/(?P<account_id>[^/]+)/namespaces/(?P<namespace>[a-zA-Z0-9._-]+)/roles/(?P<role>[^/]+)/members$": dispatch,
    r"{0}/accounts/(?P<account_id>[^/]+)/namespaces/(?P<namespace>[a-zA-Z0-9._-]+)/roles/(?P<role>[^/]+)/members/(?P<member_name>[^/]+)$": dispatch,
    r"{0}/accounts/(?P<account_id>[^/]+)/namespaces/(?P<namespace>[a-zA-Z0-9._-]+)/roles/(?P<role>[^/]+)/custom-permission$": dispatch,

    # --- Namespace: Self-upgrade ---
    r"{0}/accounts/(?P<account_id>[^/]+)/namespaces/(?P<namespace>[a-zA-Z0-9._-]+)/self-upgrade-configuration$": dispatch,
    r"{0}/accounts/(?P<account_id>[^/]+)/namespaces/(?P<namespace>[a-zA-Z0-9._-]+)/update-self-upgrade-request$": dispatch,
    r"{0}/accounts/(?P<account_id>[^/]+)/namespaces/(?P<namespace>[a-zA-Z0-9._-]+)/self-upgrade-requests$": dispatch,

    # --- Search ---
    r"{0}/accounts/(?P<account_id>[^/]+)/search/analyses$": dispatch,
    r"{0}/accounts/(?P<account_id>[^/]+)/search/dashboards$": dispatch,
    r"{0}/accounts/(?P<account_id>[^/]+)/search/data-sets$": dispatch,
    r"{0}/accounts/(?P<account_id>[^/]+)/search/data-sources$": dispatch,
    r"{0}/accounts/(?P<account_id>[^/]+)/search/folders$": dispatch,
    r"{0}/accounts/(?P<account_id>[^/]+)/search/topics$": dispatch,
    r"{0}/accounts/(?P<account_id>[^/]+)/search/action-connectors$": dispatch,

    # --- Asset Bundle ---
    r"{0}/accounts/(?P<account_id>[^/]+)/asset-bundle-export-jobs$": dispatch,
    r"{0}/accounts/(?P<account_id>[^/]+)/asset-bundle-export-jobs/export$": dispatch,
    r"{0}/accounts/(?P<account_id>[^/]+)/asset-bundle-export-jobs/(?P<job_id>[^/]+)$": dispatch,
    r"{0}/accounts/(?P<account_id>[^/]+)/asset-bundle-import-jobs$": dispatch,
    r"{0}/accounts/(?P<account_id>[^/]+)/asset-bundle-import-jobs/import$": dispatch,
    r"{0}/accounts/(?P<account_id>[^/]+)/asset-bundle-import-jobs/(?P<job_id>[^/]+)$": dispatch,

    # --- Brand ---
    r"{0}/accounts/(?P<account_id>[^/]+)/brands$": dispatch,
    r"{0}/accounts/(?P<account_id>[^/]+)/brands/(?P<brand_id>[^/]+)$": dispatch,
    r"{0}/accounts/(?P<account_id>[^/]+)/brands/(?P<brand_id>[^/]+)/publishedversion$": dispatch,
    r"{0}/accounts/(?P<account_id>[^/]+)/brandassignments$": dispatch,

    # --- ActionConnector ---
    r"{0}/accounts/(?P<account_id>[^/]+)/action-connectors$": dispatch,
    r"{0}/accounts/(?P<account_id>[^/]+)/action-connectors/(?P<action_connector_id>[^/]+)$": dispatch,
    r"{0}/accounts/(?P<account_id>[^/]+)/action-connectors/(?P<action_connector_id>[^/]+)/permissions$": dispatch,

    # --- Flow ---
    r"{0}/accounts/(?P<account_id>[^/]+)/flows$": dispatch,
    r"{0}/accounts/(?P<account_id>[^/]+)/flows/searchFlows$": dispatch,
    r"{0}/accounts/(?P<account_id>[^/]+)/flows/(?P<flow_id>[^/]+)/metadata$": dispatch,
    r"{0}/accounts/(?P<account_id>[^/]+)/flows/(?P<flow_id>[^/]+)/permissions$": dispatch,
}
