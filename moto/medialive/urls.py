from .responses import MediaLiveResponse

url_bases = [
    r"https?://medialive\.(.+)\.amazonaws.com",
]


response = MediaLiveResponse()


url_paths = {
    # Channels
    "{0}/prod/channels$": response.dispatch,
    "{0}/prod/channels/(?P<channelid>[^/.]+)$": response.dispatch,
    "{0}/prod/channels/(?P<channelid>[^/.]+)/start$": response.dispatch,
    "{0}/prod/channels/(?P<channelid>[^/.]+)/stop$": response.dispatch,
    "{0}/prod/channels/(?P<channelid>[^/.]+)/channelClass$": response.dispatch,
    "{0}/prod/channels/(?P<channelid>[^/.]+)/restartChannelPipelines$": response.dispatch,
    "{0}/prod/channels/(?P<channelid>[^/.]+)/thumbnails$": response.dispatch,
    "{0}/prod/channels/(?P<channelid>[^/.]+)/alerts$": response.dispatch,
    # Schedule
    "{0}/prod/channels/(?P<channelid>[^/.]+)/schedule$": response.dispatch,
    # Inputs
    "{0}/prod/inputs$": response.dispatch,
    "{0}/prod/inputs/(?P<inputid>[^/.]+)$": response.dispatch,
    "{0}/prod/inputs/(?P<inputid>[^/.]+)/partners$": response.dispatch,
    # InputSecurityGroups
    "{0}/prod/inputSecurityGroups$": response.dispatch,
    "{0}/prod/inputSecurityGroups/(?P<inputsecuritygroupid>[^/.]+)$": response.dispatch,
    # InputDevices
    "{0}/prod/inputDevices$": response.dispatch,
    "{0}/prod/inputDevices/(?P<inputdeviceid>[^/.]+)$": response.dispatch,
    "{0}/prod/inputDevices/(?P<inputdeviceid>[^/.]+)/accept$": response.dispatch,
    "{0}/prod/inputDevices/(?P<inputdeviceid>[^/.]+)/cancel$": response.dispatch,
    "{0}/prod/inputDevices/(?P<inputdeviceid>[^/.]+)/reject$": response.dispatch,
    "{0}/prod/inputDevices/(?P<inputdeviceid>[^/.]+)/reboot$": response.dispatch,
    "{0}/prod/inputDevices/(?P<inputdeviceid>[^/.]+)/start$": response.dispatch,
    "{0}/prod/inputDevices/(?P<inputdeviceid>[^/.]+)/stop$": response.dispatch,
    "{0}/prod/inputDevices/(?P<inputdeviceid>[^/.]+)/startInputDeviceMaintenanceWindow$": response.dispatch,
    "{0}/prod/inputDevices/(?P<inputdeviceid>[^/.]+)/transfer$": response.dispatch,
    "{0}/prod/inputDevices/(?P<inputdeviceid>[^/.]+)/thumbnailData$": response.dispatch,
    "{0}/prod/inputDeviceTransfers$": response.dispatch,
    # Multiplexes
    "{0}/prod/multiplexes$": response.dispatch,
    "{0}/prod/multiplexes/(?P<multiplexid>[^/.]+)$": response.dispatch,
    "{0}/prod/multiplexes/(?P<multiplexid>[^/.]+)/start$": response.dispatch,
    "{0}/prod/multiplexes/(?P<multiplexid>[^/.]+)/stop$": response.dispatch,
    "{0}/prod/multiplexes/(?P<multiplexid>[^/.]+)/alerts$": response.dispatch,
    # MultiplexPrograms
    "{0}/prod/multiplexes/(?P<multiplexid>[^/.]+)/programs$": response.dispatch,
    "{0}/prod/multiplexes/(?P<multiplexid>[^/.]+)/programs/(?P<programname>[^/.]+)$": response.dispatch,
    # Clusters
    "{0}/prod/clusters$": response.dispatch,
    "{0}/prod/clusters/(?P<clusterid>[^/.]+)$": response.dispatch,
    "{0}/prod/clusters/(?P<clusterid>[^/.]+)/alerts$": response.dispatch,
    # Nodes
    "{0}/prod/clusters/(?P<clusterid>[^/.]+)/nodes$": response.dispatch,
    "{0}/prod/clusters/(?P<clusterid>[^/.]+)/nodes/(?P<nodeid>[^/.]+)$": response.dispatch,
    "{0}/prod/clusters/(?P<clusterid>[^/.]+)/nodes/(?P<nodeid>[^/.]+)/state$": response.dispatch,
    "{0}/prod/clusters/(?P<clusterid>[^/.]+)/nodeRegistrationScript$": response.dispatch,
    # ChannelPlacementGroups
    "{0}/prod/clusters/(?P<clusterid>[^/.]+)/channelplacementgroups$": response.dispatch,
    "{0}/prod/clusters/(?P<clusterid>[^/.]+)/channelplacementgroups/(?P<channelplacementgroupid>[^/.]+)$": response.dispatch,
    # Networks
    "{0}/prod/networks$": response.dispatch,
    "{0}/prod/networks/(?P<networkid>[^/.]+)$": response.dispatch,
    # SdiSources
    "{0}/prod/sdiSources$": response.dispatch,
    "{0}/prod/sdiSources/(?P<sdisourceid>[^/.]+)$": response.dispatch,
    # CloudWatch Alarm Templates
    "{0}/prod/cloudwatch-alarm-templates$": response.dispatch,
    "{0}/prod/cloudwatch-alarm-templates/(?P<identifier>[^/.]+)$": response.dispatch,
    # CloudWatch Alarm Template Groups
    "{0}/prod/cloudwatch-alarm-template-groups$": response.dispatch,
    "{0}/prod/cloudwatch-alarm-template-groups/(?P<identifier>[^/.]+)$": response.dispatch,
    # EventBridge Rule Templates
    "{0}/prod/eventbridge-rule-templates$": response.dispatch,
    "{0}/prod/eventbridge-rule-templates/(?P<identifier>[^/.]+)$": response.dispatch,
    # EventBridge Rule Template Groups
    "{0}/prod/eventbridge-rule-template-groups$": response.dispatch,
    "{0}/prod/eventbridge-rule-template-groups/(?P<identifier>[^/.]+)$": response.dispatch,
    # Signal Maps
    "{0}/prod/signal-maps$": response.dispatch,
    "{0}/prod/signal-maps/(?P<identifier>[^/.]+)$": response.dispatch,
    "{0}/prod/signal-maps/(?P<identifier>[^/.]+)/monitor-deployment$": response.dispatch,
    # Tags
    "{0}/prod/tags/(?P<resourcearn>.+)$": response.dispatch,
    # Batch operations
    "{0}/prod/batch/delete$": response.dispatch,
    "{0}/prod/batch/start$": response.dispatch,
    "{0}/prod/batch/stop$": response.dispatch,
    # Account
    "{0}/prod/accountConfiguration$": response.dispatch,
    # Offerings & Reservations
    "{0}/prod/offerings$": response.dispatch,
    "{0}/prod/offerings/(?P<offeringid>[^/.]+)$": response.dispatch,
    "{0}/prod/offerings/(?P<offeringid>[^/.]+)/purchase$": response.dispatch,
    "{0}/prod/reservations$": response.dispatch,
    "{0}/prod/reservations/(?P<reservationid>[^/.]+)$": response.dispatch,
    # Misc
    "{0}/prod/claimDevice$": response.dispatch,
    "{0}/prod/versions$": response.dispatch,
}
