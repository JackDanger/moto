"""synthetics base URL and path."""

from .responses import SyntheticsResponse

dispatch = SyntheticsResponse.dispatch

url_bases = [
    r"https?://synthetics\.(.+)\.amazonaws\.com",
]

response = SyntheticsResponse()

url_paths = {
    "{0}/$": dispatch,
    "{0}/canary$": response.canary,
    "{0}/canary/(?P<name>[^/]+)$": response.canary,
    "{0}/canary/(?P<name>[^/]+)/start$": response.canary_start,
    "{0}/canary/(?P<name>[^/]+)/stop$": response.canary_stop,
    "{0}/canary/(?P<name>[^/]+)/runs$": response.canary_runs,
    "{0}/canary/(?P<name>[^/]+)/dry-run/start$": response.canary_dry_run_start,
    "{0}/canaries$": response.canaries,
    "{0}/canaries/last-run$": response.canaries_last_run,
    "{0}/runtime-versions$": response.runtime_versions,
    "{0}/group$": response.group_dispatch,
    "{0}/group/(?P<groupIdentifier>[^/]+)$": response.group_dispatch,
    "{0}/group/(?P<groupIdentifier>[^/]+)/associate$": response.group_associate,
    "{0}/group/(?P<groupIdentifier>[^/]+)/disassociate$": response.group_disassociate,
    "{0}/group/(?P<groupIdentifier>[^/]+)/resources$": response.group_resources,
    "{0}/groups$": response.groups_list,
    "{0}/resource/(?P<resourceArn>[^/]+)/groups$": response.resource_groups,
    "{0}/tags/(?P<resourceArn>.+)$": response.tags,
}
