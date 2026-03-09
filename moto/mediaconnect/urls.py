from .responses import MediaConnectResponse

url_bases = [
    r"https?://mediaconnect\.(.+)\.amazonaws.com",
]


response = MediaConnectResponse()


url_paths = {
    # Flows
    "{0}/v1/flows$": response.dispatch,
    "{0}/v1/flows/(?P<flowarn>[^/.]+)$": response.dispatch,
    "{0}/v1/flows/(?P<flowarn>[^/.]+)/vpcInterfaces$": response.dispatch,
    "{0}/v1/flows/(?P<flowarn>[^/.]+)/vpcInterfaces/(?P<vpcinterfacename>[^/.]+)$": response.dispatch,
    "{0}/v1/flows/(?P<flowarn>[^/.]+)/source$": response.dispatch,
    "{0}/v1/flows/(?P<flowarn>[^/.]+)/source/(?P<sourcearn>[^/.]+)$": response.dispatch,
    "{0}/v1/flows/(?P<flowarn>[^/.]+)/outputs$": response.dispatch,
    "{0}/v1/flows/(?P<flowarn>[^/.]+)/outputs/(?P<outputarn>[^/.]+)$": response.dispatch,
    "{0}/v1/flows/(?P<flowarn>[^/.]+)/entitlements$": response.dispatch,
    "{0}/v1/flows/(?P<flowarn>[^/.]+)/entitlements/(?P<entitlementarn>[^/.]+)$": response.dispatch,
    "{0}/v1/flows/start/(?P<flowarn>[^/.]+)$": response.dispatch,
    "{0}/v1/flows/stop/(?P<flowarn>[^/.]+)$": response.dispatch,
    # Flow media streams
    "{0}/v1/flows/(?P<flowarn>[^/.]+)/mediaStreams$": response.dispatch,
    "{0}/v1/flows/(?P<flowarn>[^/.]+)/mediaStreams/(?P<mediastreamname>[^/.]+)$": response.dispatch,
    # Flow source metadata/thumbnail
    "{0}/v1/flows/(?P<flowarn>[^/.]+)/source-metadata$": response.dispatch,
    "{0}/v1/flows/(?P<flowarn>[^/.]+)/source-thumbnail$": response.dispatch,
    # Tags
    "{0}/tags/(?P<resourcearn>[^/.]+)$": response.dispatch,
    "{0}/tags/global/(?P<resourcearn>[^/.]+)$": response.dispatch,
    # Bridges
    "{0}/v1/bridges$": response.dispatch,
    "{0}/v1/bridges/(?P<bridgearn>[^/.]+)$": response.dispatch,
    "{0}/v1/bridges/(?P<bridgearn>[^/.]+)/state$": response.dispatch,
    "{0}/v1/bridges/(?P<bridgearn>[^/.]+)/outputs$": response.dispatch,
    "{0}/v1/bridges/(?P<bridgearn>[^/.]+)/outputs/(?P<outputname>[^/.]+)$": response.dispatch,
    "{0}/v1/bridges/(?P<bridgearn>[^/.]+)/sources$": response.dispatch,
    "{0}/v1/bridges/(?P<bridgearn>[^/.]+)/sources/(?P<sourcename>[^/.]+)$": response.dispatch,
    # Gateways
    "{0}/v1/gateways$": response.dispatch,
    "{0}/v1/gateways/(?P<gatewayarn>[^/.]+)$": response.dispatch,
    # Gateway instances
    "{0}/v1/gateway-instances$": response.dispatch,
    "{0}/v1/gateway-instances/(?P<gatewayinstancearn>[^/.]+)$": response.dispatch,
    # Entitlements
    "{0}/v1/entitlements$": response.dispatch,
    # Offerings
    "{0}/v1/offerings$": response.dispatch,
    "{0}/v1/offerings/(?P<offeringarn>[^/.]+)$": response.dispatch,
    # Reservations
    "{0}/v1/reservations$": response.dispatch,
    "{0}/v1/reservations/(?P<reservationarn>[^/.]+)$": response.dispatch,
    # Router inputs
    "{0}/v1/routerInput$": response.dispatch,
    "{0}/v1/routerInput/(?P<arn>[^/.]+)$": response.dispatch,
    "{0}/v1/routerInput/(?P<arn>[^/.]+)/source-metadata$": response.dispatch,
    "{0}/v1/routerInput/(?P<arn>[^/.]+)/thumbnail$": response.dispatch,
    "{0}/v1/routerInput/start/(?P<arn>[^/.]+)$": response.dispatch,
    "{0}/v1/routerInput/stop/(?P<arn>[^/.]+)$": response.dispatch,
    "{0}/v1/routerInput/restart/(?P<arn>[^/.]+)$": response.dispatch,
    "{0}/v1/routerInputs$": response.dispatch,
    # Router network interfaces
    "{0}/v1/routerNetworkInterface$": response.dispatch,
    "{0}/v1/routerNetworkInterface/(?P<arn>[^/.]+)$": response.dispatch,
    "{0}/v1/routerNetworkInterfaces$": response.dispatch,
    # Router outputs
    "{0}/v1/routerOutput$": response.dispatch,
    "{0}/v1/routerOutput/(?P<arn>[^/.]+)$": response.dispatch,
    "{0}/v1/routerOutput/start/(?P<arn>[^/.]+)$": response.dispatch,
    "{0}/v1/routerOutput/stop/(?P<arn>[^/.]+)$": response.dispatch,
    "{0}/v1/routerOutput/restart/(?P<arn>[^/.]+)$": response.dispatch,
    "{0}/v1/routerOutput/takeRouterInput/(?P<routeroutputarn>[^/.]+)$": response.dispatch,
    "{0}/v1/routerOutputs$": response.dispatch,
}
