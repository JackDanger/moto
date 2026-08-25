"""inspector2 base URL and path."""

from .responses import Inspector2Response

url_bases = [
    r"https?://inspector2\.(.+)\.amazonaws\.com",
]


url_paths = {
    # Account and enable/disable
    "{0}/disable$": Inspector2Response.dispatch,
    "{0}/enable$": Inspector2Response.dispatch,
    "{0}/status/batch/get$": Inspector2Response.dispatch,
    # Delegated admin
    "{0}/delegatedadminaccounts/disable$": Inspector2Response.dispatch,
    "{0}/delegatedadminaccounts/enable$": Inspector2Response.dispatch,
    "{0}/delegatedadminaccounts/get$": Inspector2Response.dispatch,
    "{0}/delegatedadminaccounts/list$": Inspector2Response.dispatch,
    # Organization configuration
    "{0}/organizationconfiguration/describe$": Inspector2Response.dispatch,
    "{0}/organizationconfiguration/update$": Inspector2Response.dispatch,
    # Filters
    "{0}/filters/create$": Inspector2Response.dispatch,
    "{0}/filters/delete$": Inspector2Response.dispatch,
    "{0}/filters/list$": Inspector2Response.dispatch,
    "{0}/filters/update$": Inspector2Response.dispatch,
    # Findings
    "{0}/findings/list$": Inspector2Response.dispatch,
    "{0}/findings/details/batch/get$": Inspector2Response.dispatch,
    "{0}/findings/aggregation/list$": Inspector2Response.dispatch,
    # Members
    "{0}/members/associate$": Inspector2Response.dispatch,
    "{0}/members/disassociate$": Inspector2Response.dispatch,
    "{0}/members/get": Inspector2Response.dispatch,
    "{0}/members/list": Inspector2Response.dispatch,
    # Free trial
    "{0}/freetrialinfo/batchget$": Inspector2Response.dispatch,
    # Code snippet
    "{0}/codesnippet/batchget$": Inspector2Response.dispatch,
    # EC2 deep inspection
    "{0}/ec2deepinspectionconfiguration/get$": Inspector2Response.dispatch,
    "{0}/ec2deepinspectionconfiguration/update$": Inspector2Response.dispatch,
    "{0}/ec2deepinspectionconfiguration/org/update$": Inspector2Response.dispatch,
    "{0}/ec2deepinspectionstatus/member/batch/get$": Inspector2Response.dispatch,
    "{0}/ec2deepinspectionstatus/member/batch/update$": Inspector2Response.dispatch,
    # CIS scan configurations
    "{0}/cis/scan-configuration/create$": Inspector2Response.dispatch,
    "{0}/cis/scan-configuration/delete$": Inspector2Response.dispatch,
    "{0}/cis/scan-configuration/list$": Inspector2Response.dispatch,
    "{0}/cis/scan-configuration/update$": Inspector2Response.dispatch,
    # CIS scans
    "{0}/cis/scan/list$": Inspector2Response.dispatch,
    "{0}/cis/scan/report/get$": Inspector2Response.dispatch,
    "{0}/cis/scan-result/details/get$": Inspector2Response.dispatch,
    "{0}/cis/scan-result/check/list$": Inspector2Response.dispatch,
    "{0}/cis/scan-result/resource/list$": Inspector2Response.dispatch,
    # CIS sessions
    "{0}/cissession/start$": Inspector2Response.dispatch,
    "{0}/cissession/stop$": Inspector2Response.dispatch,
    "{0}/cissession/health/send$": Inspector2Response.dispatch,
    "{0}/cissession/telemetry/send$": Inspector2Response.dispatch,
    # Findings reports
    "{0}/reporting/create$": Inspector2Response.dispatch,
    "{0}/reporting/cancel$": Inspector2Response.dispatch,
    "{0}/reporting/status/get$": Inspector2Response.dispatch,
    # SBOM export
    "{0}/sbomexport/create$": Inspector2Response.dispatch,
    "{0}/sbomexport/cancel$": Inspector2Response.dispatch,
    "{0}/sbomexport/get$": Inspector2Response.dispatch,
    # Configuration
    "{0}/configuration/get$": Inspector2Response.dispatch,
    "{0}/configuration/update$": Inspector2Response.dispatch,
    # Encryption key
    "{0}/encryptionkey/get$": Inspector2Response.dispatch,
    "{0}/encryptionkey/update$": Inspector2Response.dispatch,
    "{0}/encryptionkey/reset$": Inspector2Response.dispatch,
    # Coverage
    "{0}/coverage/list$": Inspector2Response.dispatch,
    "{0}/coverage/statistics/list$": Inspector2Response.dispatch,
    # Account permissions
    "{0}/accountpermissions/list$": Inspector2Response.dispatch,
    # Usage
    "{0}/usage/list$": Inspector2Response.dispatch,
    # Vulnerabilities
    "{0}/vulnerabilities/search$": Inspector2Response.dispatch,
    # Clusters for image
    "{0}/cluster/get$": Inspector2Response.dispatch,
    # Code security integrations
    "{0}/codesecurity/integration/create$": Inspector2Response.dispatch,
    "{0}/codesecurity/integration/delete$": Inspector2Response.dispatch,
    "{0}/codesecurity/integration/get$": Inspector2Response.dispatch,
    "{0}/codesecurity/integration/list$": Inspector2Response.dispatch,
    "{0}/codesecurity/integration/update$": Inspector2Response.dispatch,
    # Code security scan configurations
    "{0}/codesecurity/scan-configuration/create$": Inspector2Response.dispatch,
    "{0}/codesecurity/scan-configuration/delete$": Inspector2Response.dispatch,
    "{0}/codesecurity/scan-configuration/get$": Inspector2Response.dispatch,
    "{0}/codesecurity/scan-configuration/list$": Inspector2Response.dispatch,
    "{0}/codesecurity/scan-configuration/update$": Inspector2Response.dispatch,
    "{0}/codesecurity/scan-configuration/batch/associate$": Inspector2Response.dispatch,
    "{0}/codesecurity/scan-configuration/batch/disassociate$": Inspector2Response.dispatch,
    "{0}/codesecurity/scan-configuration/associations/list$": Inspector2Response.dispatch,
    # Code security scans
    "{0}/codesecurity/scan/start$": Inspector2Response.dispatch,
    "{0}/codesecurity/scan/get$": Inspector2Response.dispatch,
    # Tags
    "{0}/tags/(?P<resource_arn>.+)$": Inspector2Response.dispatch,
}
