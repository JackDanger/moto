"""networkmanager base URL and path."""

from .responses import NetworkManagerResponse

url_bases = [
    r"https?://networkmanager\.(.+)\.amazonaws\.com",
]

url_paths = {
    "{0}/$": NetworkManagerResponse.dispatch,
    # Global networks
    "{0}/global-networks$": NetworkManagerResponse.dispatch,
    "{0}/global-networks/(?P<networkid>[^/.]+)$": NetworkManagerResponse.dispatch,
    # Sites
    "{0}/global-networks/(?P<networkid>[^/.]+)/sites$": NetworkManagerResponse.dispatch,
    "{0}/global-networks/(?P<networkid>[^/.]+)/sites/(?P<siteid>[^/.]+)$": NetworkManagerResponse.dispatch,
    # Links
    "{0}/global-networks/(?P<networkid>[^/.]+)/links$": NetworkManagerResponse.dispatch,
    "{0}/global-networks/(?P<networkid>[^/.]+)/links/(?P<linkid>[^/.]+)$": NetworkManagerResponse.dispatch,
    # Devices
    "{0}/global-networks/(?P<networkid>[^/.]+)/devices$": NetworkManagerResponse.dispatch,
    "{0}/global-networks/(?P<networkid>[^/.]+)/devices/(?P<deviceid>[^/.]+)$": NetworkManagerResponse.dispatch,
    # Connections
    "{0}/global-networks/(?P<networkid>[^/.]+)/connections$": NetworkManagerResponse.dispatch,
    "{0}/global-networks/(?P<networkid>[^/.]+)/connections/(?P<connid>[^/.]+)$": NetworkManagerResponse.dispatch,
    # Core networks
    "{0}/core-networks$": NetworkManagerResponse.dispatch,
    "{0}/core-networks/(?P<networkid>[^/.]+)$": NetworkManagerResponse.dispatch,
    # Core network policy
    "{0}/core-networks/(?P<networkid>[^/.]+)/core-network-policy$": NetworkManagerResponse.dispatch,
    "{0}/core-networks/(?P<networkid>[^/.]+)/core-network-policy-versions$": NetworkManagerResponse.dispatch,
    "{0}/core-networks/(?P<networkid>[^/.]+)/core-network-policy-versions/(?P<versionid>[^/.]+)$": NetworkManagerResponse.dispatch,
    "{0}/core-networks/(?P<networkid>[^/.]+)/core-network-policy-versions/(?P<versionid>[^/.]+)/restore$": NetworkManagerResponse.dispatch,
    # Core network change sets
    "{0}/core-networks/(?P<networkid>[^/.]+)/core-network-change-sets/(?P<versionid>[^/.]+)$": NetworkManagerResponse.dispatch,
    "{0}/core-networks/(?P<networkid>[^/.]+)/core-network-change-sets/(?P<versionid>[^/.]+)/execute$": NetworkManagerResponse.dispatch,
    # Core network change events
    "{0}/core-networks/(?P<networkid>[^/.]+)/core-network-change-events/(?P<versionid>[^/.]+)$": NetworkManagerResponse.dispatch,
    # Core network routing information
    "{0}/core-networks/(?P<networkid>[^/.]+)/core-network-routing-information$": NetworkManagerResponse.dispatch,
    # Tags
    "{0}/tags$": NetworkManagerResponse.dispatch,
    "{0}/tags/(?P<resourcearn>[^/.]+)$": NetworkManagerResponse.dispatch,
    "{0}/tags/(?P<arn_prefix>[^/]+)/(?P<resource_id>[^/]+)$": NetworkManagerResponse.dispatch,
    # Attachments
    "{0}/attachments$": NetworkManagerResponse.dispatch,
    "{0}/attachments/(?P<attachmentid>[^/.]+)$": NetworkManagerResponse.dispatch,
    "{0}/attachments/(?P<attachmentid>[^/.]+)/accept$": NetworkManagerResponse.dispatch,
    "{0}/attachments/(?P<attachmentid>[^/.]+)/reject$": NetworkManagerResponse.dispatch,
    # VPC attachments
    "{0}/vpc-attachments$": NetworkManagerResponse.dispatch,
    "{0}/vpc-attachments/(?P<attachmentid>[^/.]+)$": NetworkManagerResponse.dispatch,
    # Connect attachments
    "{0}/connect-attachments$": NetworkManagerResponse.dispatch,
    "{0}/connect-attachments/(?P<attachmentid>[^/.]+)$": NetworkManagerResponse.dispatch,
    # Site-to-site VPN attachments
    "{0}/site-to-site-vpn-attachments$": NetworkManagerResponse.dispatch,
    "{0}/site-to-site-vpn-attachments/(?P<attachmentid>[^/.]+)$": NetworkManagerResponse.dispatch,
    # Transit gateway route table attachments
    "{0}/transit-gateway-route-table-attachments$": NetworkManagerResponse.dispatch,
    "{0}/transit-gateway-route-table-attachments/(?P<attachmentid>[^/.]+)$": NetworkManagerResponse.dispatch,
    # Direct connect gateway attachments
    "{0}/direct-connect-gateway-attachments$": NetworkManagerResponse.dispatch,
    "{0}/direct-connect-gateway-attachments/(?P<attachmentid>[^/.]+)$": NetworkManagerResponse.dispatch,
    # Connect peers
    "{0}/connect-peers$": NetworkManagerResponse.dispatch,
    "{0}/connect-peers/(?P<connectpeerid>[^/.]+)$": NetworkManagerResponse.dispatch,
    # Peerings
    "{0}/peerings$": NetworkManagerResponse.dispatch,
    "{0}/peerings/(?P<peeringid>[^/.]+)$": NetworkManagerResponse.dispatch,
    # Transit gateway peerings
    "{0}/transit-gateway-peerings$": NetworkManagerResponse.dispatch,
    "{0}/transit-gateway-peerings/(?P<peeringid>[^/.]+)$": NetworkManagerResponse.dispatch,
    # Resource policy
    "{0}/resource-policy/(?P<resourcearn>.+)$": NetworkManagerResponse.dispatch,
    # Connect peer associations
    "{0}/global-networks/(?P<networkid>[^/.]+)/connect-peer-associations$": NetworkManagerResponse.dispatch,
    "{0}/global-networks/(?P<networkid>[^/.]+)/connect-peer-associations/(?P<connectpeerid>[^/.]+)$": NetworkManagerResponse.dispatch,
    # Customer gateway associations
    "{0}/global-networks/(?P<networkid>[^/.]+)/customer-gateway-associations$": NetworkManagerResponse.dispatch,
    "{0}/global-networks/(?P<networkid>[^/.]+)/customer-gateway-associations/(?P<cgwarn>.+)$": NetworkManagerResponse.dispatch,
    # Link associations
    "{0}/global-networks/(?P<networkid>[^/.]+)/link-associations$": NetworkManagerResponse.dispatch,
    # Transit gateway connect peer associations
    "{0}/global-networks/(?P<networkid>[^/.]+)/transit-gateway-connect-peer-associations$": NetworkManagerResponse.dispatch,
    "{0}/global-networks/(?P<networkid>[^/.]+)/transit-gateway-connect-peer-associations/(?P<tgwcparn>.+)$": NetworkManagerResponse.dispatch,
    # Transit gateway registrations
    "{0}/global-networks/(?P<networkid>[^/.]+)/transit-gateway-registrations$": NetworkManagerResponse.dispatch,
    "{0}/global-networks/(?P<networkid>[^/.]+)/transit-gateway-registrations/(?P<tgwarn>.+)$": NetworkManagerResponse.dispatch,
    # Route analyses
    "{0}/global-networks/(?P<networkid>[^/.]+)/route-analyses$": NetworkManagerResponse.dispatch,
    "{0}/global-networks/(?P<networkid>[^/.]+)/route-analyses/(?P<raid>[^/.]+)$": NetworkManagerResponse.dispatch,
    # Network resources
    "{0}/global-networks/(?P<networkid>[^/.]+)/network-resources$": NetworkManagerResponse.dispatch,
    "{0}/global-networks/(?P<networkid>[^/.]+)/network-resources/(?P<resourcearn>.+)/metadata$": NetworkManagerResponse.dispatch,
    # Network resource relationships
    "{0}/global-networks/(?P<networkid>[^/.]+)/network-resource-relationships$": NetworkManagerResponse.dispatch,
    # Network resource counts
    "{0}/global-networks/(?P<networkid>[^/.]+)/network-resource-count$": NetworkManagerResponse.dispatch,
    # Network routes
    "{0}/global-networks/(?P<networkid>[^/.]+)/network-routes$": NetworkManagerResponse.dispatch,
    # Network telemetry
    "{0}/global-networks/(?P<networkid>[^/.]+)/network-telemetry$": NetworkManagerResponse.dispatch,
    # Prefix list
    "{0}/prefix-list$": NetworkManagerResponse.dispatch,
    "{0}/prefix-list/core-network/(?P<cnid>[^/.]+)$": NetworkManagerResponse.dispatch,
    "{0}/prefix-list/(?P<prefixlistarn>[^/]+)/core-network/(?P<cnid>[^/.]+)$": NetworkManagerResponse.dispatch,
    # Routing policy label
    "{0}/routing-policy-label$": NetworkManagerResponse.dispatch,
    "{0}/routing-policy-label/core-network/(?P<cnid>[^/.]+)$": NetworkManagerResponse.dispatch,
    "{0}/routing-policy-label/core-network/(?P<cnid>[^/.]+)/attachment/(?P<attachmentid>[^/.]+)$": NetworkManagerResponse.dispatch,
    # Organization service access
    "{0}/organizations/service-access$": NetworkManagerResponse.dispatch,
}
