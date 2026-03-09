from .responses import MacieResponse

url_bases = [
    r"https?://macie2\.(.+)\.amazonaws\.com",
]

url_paths = {
    # Admin
    "{0}/admin$": MacieResponse.dispatch,
    "{0}/admin/configuration$": MacieResponse.dispatch,
    # Administrator
    "{0}/administrator$": MacieResponse.dispatch,
    "{0}/administrator/disassociate$": MacieResponse.dispatch,
    # Allow Lists
    "{0}/allow-lists$": MacieResponse.dispatch,
    "{0}/allow-lists/(?P<id>[^/]+)$": MacieResponse.dispatch,
    # Automated Discovery
    "{0}/automated-discovery/accounts$": MacieResponse.dispatch,
    "{0}/automated-discovery/configuration$": MacieResponse.dispatch,
    # Classification Export Configuration
    "{0}/classification-export-configuration$": MacieResponse.dispatch,
    # Classification Scopes
    "{0}/classification-scopes$": MacieResponse.dispatch,
    "{0}/classification-scopes/(?P<id>[^/]+)$": MacieResponse.dispatch,
    # Custom Data Identifiers
    "{0}/custom-data-identifiers$": MacieResponse.dispatch,
    "{0}/custom-data-identifiers/get$": MacieResponse.dispatch,
    "{0}/custom-data-identifiers/list$": MacieResponse.dispatch,
    "{0}/custom-data-identifiers/test$": MacieResponse.dispatch,
    "{0}/custom-data-identifiers/(?P<id>[^/]+)$": MacieResponse.dispatch,
    # Datasources / Buckets
    "{0}/datasources/s3$": MacieResponse.dispatch,
    "{0}/datasources/s3/statistics$": MacieResponse.dispatch,
    "{0}/datasources/search-resources$": MacieResponse.dispatch,
    # Findings
    "{0}/findings$": MacieResponse.dispatch,
    "{0}/findings/describe$": MacieResponse.dispatch,
    "{0}/findings/sample$": MacieResponse.dispatch,
    "{0}/findings/statistics$": MacieResponse.dispatch,
    "{0}/findings/(?P<findingId>[^/]+)/reveal$": MacieResponse.dispatch,
    "{0}/findings/(?P<findingId>[^/]+)/reveal/availability$": MacieResponse.dispatch,
    # Findings Filters
    "{0}/findingsfilters$": MacieResponse.dispatch,
    "{0}/findingsfilters/(?P<id>[^/]+)$": MacieResponse.dispatch,
    # Findings Publication Configuration
    "{0}/findings-publication-configuration$": MacieResponse.dispatch,
    # Invitations
    "{0}/invitations$": MacieResponse.dispatch,
    "{0}/invitations/accept$": MacieResponse.dispatch,
    "{0}/invitations/count$": MacieResponse.dispatch,
    "{0}/invitations/decline$": MacieResponse.dispatch,
    "{0}/invitations/delete$": MacieResponse.dispatch,
    # Jobs
    "{0}/jobs$": MacieResponse.dispatch,
    "{0}/jobs/list$": MacieResponse.dispatch,
    "{0}/jobs/(?P<jobId>[^/]+)$": MacieResponse.dispatch,
    # Macie Session
    "{0}/macie$": MacieResponse.dispatch,
    "{0}/macie/members/(?P<id>[^/]+)$": MacieResponse.dispatch,
    # Managed Data Identifiers
    "{0}/managed-data-identifiers/list$": MacieResponse.dispatch,
    # Master (deprecated)
    "{0}/master$": MacieResponse.dispatch,
    "{0}/master/disassociate$": MacieResponse.dispatch,
    # Members
    "{0}/members$": MacieResponse.dispatch,
    "{0}/members/disassociate/(?P<id>[^/]+)$": MacieResponse.dispatch,
    "{0}/members/(?P<id>[^/]+)$": MacieResponse.dispatch,
    # Resource Profiles
    "{0}/resource-profiles$": MacieResponse.dispatch,
    "{0}/resource-profiles/artifacts$": MacieResponse.dispatch,
    "{0}/resource-profiles/detections$": MacieResponse.dispatch,
    # Reveal Configuration
    "{0}/reveal-configuration$": MacieResponse.dispatch,
    # Session (kept for backward compat, alias for /macie GET)
    "{0}/session$": MacieResponse.dispatch,
    # Sensitivity Inspection Templates
    "{0}/templates/sensitivity-inspections$": MacieResponse.dispatch,
    "{0}/templates/sensitivity-inspections/(?P<id>[^/]+)$": MacieResponse.dispatch,
    # Tags
    "{0}/tags/(?P<resourceArn>.+)$": MacieResponse.dispatch,
    # Usage
    "{0}/usage$": MacieResponse.dispatch,
    "{0}/usage/statistics$": MacieResponse.dispatch,
}
