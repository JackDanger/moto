"""route53resolver base URL and path."""

from .responses import Route53ResolverResponse

url_bases = [
    r"https?://route53resolver\.(.+)\.amazonaws\.com",
]


url_paths = {
    "{0}/$": Route53ResolverResponse.dispatch,
    "{0}/outpost-resolvers$": Route53ResolverResponse.dispatch,
    "{0}/outpost-resolvers/(?P<resolver_id>[^/]+)$": Route53ResolverResponse.dispatch,
}
