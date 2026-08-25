"""account base URL and path."""

from .responses import AccountResponse

url_bases = [
    r"https?://account\.(.+)\.amazonaws\.com",
]

url_paths = {
    "{0}/putAlternateContact$": AccountResponse.dispatch,
    "{0}/getAlternateContact$": AccountResponse.dispatch,
    "{0}/deleteAlternateContact$": AccountResponse.dispatch,
    "{0}/getAccountInformation$": AccountResponse.dispatch,
    "{0}/getContactInformation$": AccountResponse.dispatch,
    "{0}/putContactInformation$": AccountResponse.dispatch,
    "{0}/getGovCloudAccountInformation$": AccountResponse.dispatch,
    "{0}/getPrimaryEmail$": AccountResponse.dispatch,
    "{0}/getRegionOptStatus$": AccountResponse.dispatch,
    "{0}/enableRegion$": AccountResponse.dispatch,
    "{0}/disableRegion$": AccountResponse.dispatch,
    "{0}/listRegions$": AccountResponse.dispatch,
    "{0}/putAccountName$": AccountResponse.dispatch,
    "{0}/startPrimaryEmailUpdate$": AccountResponse.dispatch,
    "{0}/acceptPrimaryEmailUpdate$": AccountResponse.dispatch,
}
