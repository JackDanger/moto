import json
from urllib.parse import unquote

from moto.core.responses import BaseResponse

from .models import MediaConnectBackend, mediaconnect_backends


class MediaConnectResponse(BaseResponse):
    def __init__(self) -> None:
        super().__init__(service_name="mediaconnect")

    @property
    def mediaconnect_backend(self) -> MediaConnectBackend:
        return mediaconnect_backends[self.current_account][self.region]

    def create_flow(self) -> str:
        availability_zone = self._get_param("availabilityZone")
        entitlements = self._get_param("entitlements", [])
        name = self._get_param("name")
        outputs = self._get_param("outputs")
        source = self._get_param("source")
        source_failover_config = self._get_param("sourceFailoverConfig")
        sources = self._get_param("sources")
        vpc_interfaces = self._get_param("vpcInterfaces")
        maintenance = self._get_param("maintenance")
        media_streams = self._get_param("mediaStreams")
        flow = self.mediaconnect_backend.create_flow(
            availability_zone=availability_zone,
            entitlements=entitlements,
            name=name,
            outputs=outputs,
            source=source,
            source_failover_config=source_failover_config,
            sources=sources,
            vpc_interfaces=vpc_interfaces,
            maintenance=maintenance,
            media_streams=media_streams,
        )
        return json.dumps({"flow": flow.to_dict()})

    def list_flows(self) -> str:
        max_results = self._get_int_param("maxResults")
        flows = self.mediaconnect_backend.list_flows(max_results=max_results)
        return json.dumps({"flows": flows})

    def describe_flow(self) -> str:
        flow_arn = self.get_flow_arn()
        flow = self.mediaconnect_backend.describe_flow(flow_arn=flow_arn)
        return json.dumps({"flow": flow.to_dict()})

    def delete_flow(self) -> str:
        flow_arn = self.get_flow_arn()
        flow = self.mediaconnect_backend.delete_flow(flow_arn=flow_arn)
        return json.dumps({"flowArn": flow.flow_arn, "status": flow.status})

    def start_flow(self) -> str:
        flow_arn = self.get_flow_arn()
        flow = self.mediaconnect_backend.start_flow(flow_arn=flow_arn)
        return json.dumps({"flowArn": flow.flow_arn, "status": flow.status})

    def stop_flow(self) -> str:
        flow_arn = self.get_flow_arn()
        flow = self.mediaconnect_backend.stop_flow(flow_arn=flow_arn)
        return json.dumps({"flowArn": flow.flow_arn, "status": flow.status})

    def update_flow(self) -> str:
        flow_arn = self.get_flow_arn()
        source_failover_config = self._get_param("sourceFailoverConfig")
        maintenance = self._get_param("maintenance")
        flow = self.mediaconnect_backend.update_flow(
            flow_arn=flow_arn,
            source_failover_config=source_failover_config,
            maintenance=maintenance,
        )
        return json.dumps({"flow": flow.to_dict()})

    def tag_resource(self) -> str:
        resource_arn = unquote(self.path.split("/tags/")[-1])
        tags = self._get_param("tags")
        self.mediaconnect_backend.tag_resource(resource_arn=resource_arn, tags=tags)
        return json.dumps({})

    def untag_resource(self) -> str:
        resource_arn = unquote(self.path.split("/tags/")[-1])
        tag_keys = self.querystring.get("tagKeys", [])
        self.mediaconnect_backend.untag_resource(
            resource_arn=resource_arn, tag_keys=tag_keys
        )
        return json.dumps({})

    def list_tags_for_resource(self) -> str:
        resource_arn = unquote(self.path.split("/tags/")[-1])
        tags = self.mediaconnect_backend.list_tags_for_resource(resource_arn)
        return json.dumps({"tags": tags})

    def tag_global_resource(self) -> str:
        resource_arn = unquote(self.path.split("/tags/global/")[-1])
        tags = self._get_param("tags")
        self.mediaconnect_backend.tag_global_resource(
            resource_arn=resource_arn, tags=tags
        )
        return json.dumps({})

    def untag_global_resource(self) -> str:
        resource_arn = unquote(self.path.split("/tags/global/")[-1])
        tag_keys = self.querystring.get("tagKeys", [])
        self.mediaconnect_backend.untag_global_resource(
            resource_arn=resource_arn, tag_keys=tag_keys
        )
        return json.dumps({})

    def list_tags_for_global_resource(self) -> str:
        resource_arn = unquote(self.path.split("/tags/global/")[-1])
        tags = self.mediaconnect_backend.list_tags_for_global_resource(resource_arn)
        return json.dumps({"tags": tags})

    def add_flow_vpc_interfaces(self) -> str:
        flow_arn = self.get_flow_arn()
        vpc_interfaces = self._get_param("vpcInterfaces")
        flow = self.mediaconnect_backend.add_flow_vpc_interfaces(
            flow_arn=flow_arn, vpc_interfaces=vpc_interfaces
        )
        return json.dumps(
            {"flow_arn": flow.flow_arn, "vpc_interfaces": flow.vpc_interfaces}
        )

    def remove_flow_vpc_interface(self) -> str:
        flow_arn = self.get_flow_arn()
        vpc_interface_name = self.get_vpc_interface_name()
        self.mediaconnect_backend.remove_flow_vpc_interface(
            flow_arn=flow_arn, vpc_interface_name=vpc_interface_name
        )
        return json.dumps(
            {"flow_arn": flow_arn, "vpc_interface_name": vpc_interface_name}
        )

    def add_flow_outputs(self) -> str:
        flow_arn = self.get_flow_arn()
        outputs = self._get_param("outputs")
        flow = self.mediaconnect_backend.add_flow_outputs(
            flow_arn=flow_arn, outputs=outputs
        )
        return json.dumps({"flow_arn": flow.flow_arn, "outputs": flow.outputs})

    def remove_flow_output(self) -> str:
        flow_arn = self.get_flow_arn()
        output_name = self.get_output_arn()
        self.mediaconnect_backend.remove_flow_output(
            flow_arn=flow_arn, output_name=output_name
        )
        return json.dumps({"flow_arn": flow_arn, "output_name": output_name})

    def update_flow_output(self) -> str:
        flow_arn = self.get_flow_arn()
        output_arn = self.get_output_arn()
        cidr_allow_list = self._get_param("cidrAllowList")
        description = self._get_param("description")
        destination = self._get_param("destination")
        encryption = self._get_param("encryption")
        max_latency = self._get_param("maxLatency")
        media_stream_output_configuration = self._get_param(
            "mediaStreamOutputConfiguration"
        )
        min_latency = self._get_param("minLatency")
        port = self._get_param("port")
        protocol = self._get_param("protocol")
        remote_id = self._get_param("remoteId")
        sender_control_port = self._get_param("senderControlPort")
        sender_ip_address = self._get_param("senderIpAddress")
        smoothing_latency = self._get_param("smoothingLatency")
        stream_id = self._get_param("streamId")
        vpc_interface_attachment = self._get_param("vpcInterfaceAttachment")
        output = self.mediaconnect_backend.update_flow_output(
            flow_arn=flow_arn,
            output_arn=output_arn,
            cidr_allow_list=cidr_allow_list,
            description=description,
            destination=destination,
            encryption=encryption,
            max_latency=max_latency,
            media_stream_output_configuration=media_stream_output_configuration,
            min_latency=min_latency,
            port=port,
            protocol=protocol,
            remote_id=remote_id,
            sender_control_port=sender_control_port,
            sender_ip_address=sender_ip_address,
            smoothing_latency=smoothing_latency,
            stream_id=stream_id,
            vpc_interface_attachment=vpc_interface_attachment,
        )
        return json.dumps({"flowArn": flow_arn, "output": output})

    def add_flow_sources(self) -> str:
        flow_arn = self.get_flow_arn()
        sources = self._get_param("sources")
        sources = self.mediaconnect_backend.add_flow_sources(
            flow_arn=flow_arn, sources=sources
        )
        return json.dumps({"flow_arn": flow_arn, "sources": sources})

    def update_flow_source(self) -> str:
        flow_arn = self.get_flow_arn()
        source_arn = self.get_source_arn()
        description = self._get_param("description")
        decryption = self._get_param("decryption")
        entitlement_arn = self.get_entitlement_arn()
        ingest_port = self._get_param("ingestPort")
        max_bitrate = self._get_param("maxBitrate")
        max_latency = self._get_param("maxLatency")
        max_sync_buffer = self._get_param("maxSyncbuffer")
        media_stream_source_configurations = self._get_param(
            "mediaStreamSourceConfigurations"
        )
        min_latency = self._get_param("minLatency")
        protocol = self._get_param("protocol")
        sender_control_port = self._get_param("senderControlPort")
        sender_ip_address = self._get_param("senderIpAddress")
        stream_id = self._get_param("streamId")
        vpc_interface_name = self.get_vpc_interface_name()
        whitelist_cidr = self._get_param("whitelistCidr")
        source = self.mediaconnect_backend.update_flow_source(
            flow_arn=flow_arn,
            source_arn=source_arn,
            decryption=decryption,
            description=description,
            entitlement_arn=entitlement_arn,
            ingest_port=ingest_port,
            max_bitrate=max_bitrate,
            max_latency=max_latency,
            max_sync_buffer=max_sync_buffer,
            media_stream_source_configurations=media_stream_source_configurations,
            min_latency=min_latency,
            protocol=protocol,
            sender_control_port=sender_control_port,
            sender_ip_address=sender_ip_address,
            stream_id=stream_id,
            vpc_interface_name=vpc_interface_name,
            whitelist_cidr=whitelist_cidr,
        )
        return json.dumps({"flow_arn": flow_arn, "source": source})

    def remove_flow_source(self) -> str:
        flow_arn = self.get_flow_arn()
        source_arn = self.get_source_arn()
        self.mediaconnect_backend.remove_flow_source(
            flow_arn=flow_arn, source_arn=source_arn
        )
        return json.dumps({"flowArn": flow_arn, "sourceArn": source_arn})

    def grant_flow_entitlements(self) -> str:
        flow_arn = self.get_flow_arn()
        entitlements = self._get_param("entitlements")
        entitlements = self.mediaconnect_backend.grant_flow_entitlements(
            flow_arn=flow_arn, entitlements=entitlements
        )
        return json.dumps({"flow_arn": flow_arn, "entitlements": entitlements})

    def revoke_flow_entitlement(self) -> str:
        flow_arn = self.get_flow_arn()
        entitlement_arn = self.get_entitlement_arn()
        self.mediaconnect_backend.revoke_flow_entitlement(
            flow_arn=flow_arn, entitlement_arn=entitlement_arn
        )
        return json.dumps({"flowArn": flow_arn, "entitlementArn": entitlement_arn})

    def update_flow_entitlement(self) -> str:
        flow_arn = self.get_flow_arn()
        entitlement_arn = self.get_entitlement_arn()
        description = self._get_param("description")
        encryption = self._get_param("encryption")
        entitlement_status = self._get_param("entitlementStatus")
        name = self._get_param("name")
        subscribers = self._get_param("subscribers")
        entitlement = self.mediaconnect_backend.update_flow_entitlement(
            flow_arn=flow_arn,
            entitlement_arn=entitlement_arn,
            description=description,
            encryption=encryption,
            entitlement_status=entitlement_status,
            name=name,
            subscribers=subscribers,
        )
        return json.dumps({"flowArn": flow_arn, "entitlement": entitlement})

    def list_entitlements(self) -> str:
        max_results = self._get_int_param("maxResults")
        entitlements = self.mediaconnect_backend.list_entitlements(
            max_results=max_results
        )
        return json.dumps({"entitlements": entitlements})

    # --- Media Streams ---

    def add_flow_media_streams(self) -> str:
        flow_arn = self.get_flow_arn()
        media_streams = self._get_param("mediaStreams", [])
        result = self.mediaconnect_backend.add_flow_media_streams(
            flow_arn=flow_arn, media_streams=media_streams
        )
        return json.dumps({"flowArn": flow_arn, "mediaStreams": result})

    def remove_flow_media_stream(self) -> str:
        flow_arn = self.get_flow_arn()
        media_stream_name = self.get_media_stream_name()
        self.mediaconnect_backend.remove_flow_media_stream(
            flow_arn=flow_arn, media_stream_name=media_stream_name
        )
        return json.dumps(
            {"flowArn": flow_arn, "mediaStreamName": media_stream_name}
        )

    def update_flow_media_stream(self) -> str:
        flow_arn = self.get_flow_arn()
        media_stream_name = self.get_media_stream_name()
        attributes = self._get_param("attributes")
        clock_rate = self._get_param("clockRate")
        description = self._get_param("description")
        media_stream_type = self._get_param("mediaStreamType")
        video_format = self._get_param("videoFormat")
        result = self.mediaconnect_backend.update_flow_media_stream(
            flow_arn=flow_arn,
            media_stream_name=media_stream_name,
            attributes=attributes,
            clock_rate=clock_rate,
            description=description,
            media_stream_type=media_stream_type,
            video_format=video_format,
        )
        return json.dumps({"flowArn": flow_arn, "mediaStream": result})

    def describe_flow_source_metadata(self) -> str:
        flow_arn = self.get_flow_arn()
        result = self.mediaconnect_backend.describe_flow_source_metadata(
            flow_arn=flow_arn
        )
        return json.dumps(result)

    def describe_flow_source_thumbnail(self) -> str:
        flow_arn = self.get_flow_arn()
        result = self.mediaconnect_backend.describe_flow_source_thumbnail(
            flow_arn=flow_arn
        )
        return json.dumps(result)

    # --- Bridge operations ---

    def create_bridge(self) -> str:
        name = self._get_param("name")
        placement_arn = self._get_param("placementArn", "")
        sources = self._get_param("sources", [])
        outputs = self._get_param("outputs", [])
        source_failover_config = self._get_param("sourceFailoverConfig")
        egress_gateway_bridge = self._get_param("egressGatewayBridge")
        ingress_gateway_bridge = self._get_param("ingressGatewayBridge")
        bridge = self.mediaconnect_backend.create_bridge(
            name=name,
            placement_arn=placement_arn,
            sources=sources,
            outputs=outputs,
            source_failover_config=source_failover_config,
            egress_gateway_bridge=egress_gateway_bridge,
            ingress_gateway_bridge=ingress_gateway_bridge,
        )
        return json.dumps({"bridge": bridge.to_dict()})

    def list_bridges(self) -> str:
        max_results = self._get_int_param("maxResults")
        bridges = self.mediaconnect_backend.list_bridges(max_results=max_results)
        return json.dumps({"bridges": bridges})

    def describe_bridge(self) -> str:
        bridge_arn = self.get_bridge_arn()
        bridge = self.mediaconnect_backend.describe_bridge(bridge_arn=bridge_arn)
        return json.dumps({"bridge": bridge.to_dict()})

    def delete_bridge(self) -> str:
        bridge_arn = self.get_bridge_arn()
        result_arn = self.mediaconnect_backend.delete_bridge(bridge_arn=bridge_arn)
        return json.dumps({"bridgeArn": result_arn})

    def update_bridge(self) -> str:
        bridge_arn = self.get_bridge_arn()
        source_failover_config = self._get_param("sourceFailoverConfig")
        egress_gateway_bridge = self._get_param("egressGatewayBridge")
        ingress_gateway_bridge = self._get_param("ingressGatewayBridge")
        bridge = self.mediaconnect_backend.update_bridge(
            bridge_arn=bridge_arn,
            source_failover_config=source_failover_config,
            egress_gateway_bridge=egress_gateway_bridge,
            ingress_gateway_bridge=ingress_gateway_bridge,
        )
        return json.dumps({"bridge": bridge.to_dict()})

    def update_bridge_state(self) -> str:
        bridge_arn = self.get_bridge_arn()
        desired_state = self._get_param("desiredState", "ACTIVE")
        bridge = self.mediaconnect_backend.update_bridge_state(
            bridge_arn=bridge_arn, desired_state=desired_state
        )
        return json.dumps(
            {"bridgeArn": bridge.bridge_arn, "desiredState": bridge.bridge_state}
        )

    def add_bridge_outputs(self) -> str:
        bridge_arn = self.get_bridge_arn()
        outputs = self._get_param("outputs", [])
        result = self.mediaconnect_backend.add_bridge_outputs(
            bridge_arn=bridge_arn, outputs=outputs
        )
        return json.dumps({"bridgeArn": bridge_arn, "outputs": result})

    def remove_bridge_output(self) -> str:
        bridge_arn = self.get_bridge_arn()
        output_name = self.get_bridge_output_name()
        self.mediaconnect_backend.remove_bridge_output(
            bridge_arn=bridge_arn, output_name=output_name
        )
        return json.dumps({"bridgeArn": bridge_arn, "outputName": output_name})

    def update_bridge_output(self) -> str:
        bridge_arn = self.get_bridge_arn()
        output_name = self.get_bridge_output_name()
        network_output = self._get_param("networkOutput")
        result = self.mediaconnect_backend.update_bridge_output(
            bridge_arn=bridge_arn,
            output_name=output_name,
            network_output=network_output,
        )
        return json.dumps({"bridgeArn": bridge_arn, "output": result})

    def add_bridge_sources(self) -> str:
        bridge_arn = self.get_bridge_arn()
        sources = self._get_param("sources", [])
        result = self.mediaconnect_backend.add_bridge_sources(
            bridge_arn=bridge_arn, sources=sources
        )
        return json.dumps({"bridgeArn": bridge_arn, "sources": result})

    def remove_bridge_source(self) -> str:
        bridge_arn = self.get_bridge_arn()
        source_name = self.get_bridge_source_name()
        self.mediaconnect_backend.remove_bridge_source(
            bridge_arn=bridge_arn, source_name=source_name
        )
        return json.dumps({"bridgeArn": bridge_arn, "sourceName": source_name})

    def update_bridge_source(self) -> str:
        bridge_arn = self.get_bridge_arn()
        source_name = self.get_bridge_source_name()
        flow_source = self._get_param("flowSource")
        network_source = self._get_param("networkSource")
        result = self.mediaconnect_backend.update_bridge_source(
            bridge_arn=bridge_arn,
            source_name=source_name,
            flow_source=flow_source,
            network_source=network_source,
        )
        return json.dumps({"bridgeArn": bridge_arn, "source": result})

    # --- Gateway operations ---

    def create_gateway(self) -> str:
        name = self._get_param("name")
        egress_cidr_blocks = self._get_param("egressCidrBlocks", [])
        networks = self._get_param("networks", [])
        gw = self.mediaconnect_backend.create_gateway(
            name=name,
            egress_cidr_blocks=egress_cidr_blocks,
            networks=networks,
        )
        return json.dumps({"gateway": gw.to_dict()})

    def list_gateways(self) -> str:
        max_results = self._get_int_param("maxResults")
        gateways = self.mediaconnect_backend.list_gateways(max_results=max_results)
        return json.dumps({"gateways": gateways})

    def describe_gateway(self) -> str:
        gateway_arn = self.get_gateway_arn()
        gw = self.mediaconnect_backend.describe_gateway(gateway_arn=gateway_arn)
        return json.dumps({"gateway": gw.to_dict()})

    def delete_gateway(self) -> str:
        gateway_arn = self.get_gateway_arn()
        result_arn = self.mediaconnect_backend.delete_gateway(
            gateway_arn=gateway_arn
        )
        return json.dumps({"gatewayArn": result_arn})

    # --- Gateway Instance operations ---

    def describe_gateway_instance(self) -> str:
        gateway_instance_arn = self.get_gateway_instance_arn()
        instance = self.mediaconnect_backend.describe_gateway_instance(
            gateway_instance_arn=gateway_instance_arn
        )
        return json.dumps({"gatewayInstance": instance.to_dict()})

    def deregister_gateway_instance(self) -> str:
        gateway_instance_arn = self.get_gateway_instance_arn()
        result_arn = self.mediaconnect_backend.deregister_gateway_instance(
            gateway_instance_arn=gateway_instance_arn
        )
        return json.dumps({"gatewayInstanceArn": result_arn})

    def list_gateway_instances(self) -> str:
        max_results = self._get_int_param("maxResults")
        filter_arn = self._get_param("filterArn")
        instances = self.mediaconnect_backend.list_gateway_instances(
            max_results=max_results, filter_arn=filter_arn
        )
        return json.dumps({"instances": instances})

    def update_gateway_instance(self) -> str:
        gateway_instance_arn = self.get_gateway_instance_arn()
        bridge_placement = self._get_param("bridgePlacement")
        instance = self.mediaconnect_backend.update_gateway_instance(
            gateway_instance_arn=gateway_instance_arn,
            bridge_placement=bridge_placement,
        )
        return json.dumps({
            "bridgePlacement": instance.bridge_placement,
            "gatewayInstanceArn": instance.gateway_instance_arn,
        })

    # --- Offering operations ---

    def list_offerings(self) -> str:
        max_results = self._get_int_param("maxResults")
        offerings = self.mediaconnect_backend.list_offerings(
            max_results=max_results
        )
        return json.dumps({"offerings": offerings})

    def describe_offering(self) -> str:
        offering_arn = self.get_offering_arn()
        offering = self.mediaconnect_backend.describe_offering(
            offering_arn=offering_arn
        )
        return json.dumps({"offering": offering.to_dict()})

    def purchase_offering(self) -> str:
        offering_arn = self.get_offering_arn()
        reservation_name = self._get_param("reservationName", "")
        start = self._get_param("start", "")
        reservation = self.mediaconnect_backend.purchase_offering(
            offering_arn=offering_arn,
            reservation_name=reservation_name,
            start=start,
        )
        return json.dumps({"reservation": reservation.to_dict()})

    # --- Reservation operations ---

    def list_reservations(self) -> str:
        max_results = self._get_int_param("maxResults")
        reservations = self.mediaconnect_backend.list_reservations(
            max_results=max_results
        )
        return json.dumps({"reservations": reservations})

    def describe_reservation(self) -> str:
        reservation_arn = self.get_reservation_arn()
        reservation = self.mediaconnect_backend.describe_reservation(
            reservation_arn=reservation_arn
        )
        return json.dumps({"reservation": reservation.to_dict()})

    # --- Router Input operations ---

    def create_router_input(self) -> str:
        name = self._get_param("name", "")
        router_arn = self._get_param("routerArn", "")
        gateway_arn = self._get_param("gatewayArn", "")
        data_type = self._get_param("dataType", "sdi")
        ip = self._get_param("ip", "")
        port = self._get_param("port", 0)
        network_interface_arn = self._get_param("networkInterfaceArn", "")
        ri = self.mediaconnect_backend.create_router_input(
            name=name,
            router_arn=router_arn,
            gateway_arn=gateway_arn,
            data_type=data_type,
            ip=ip,
            port=port,
            network_interface_arn=network_interface_arn,
        )
        return json.dumps({"routerInput": ri.to_dict()})

    def get_router_input(self) -> str:
        arn = self.get_router_resource_arn()
        ri = self.mediaconnect_backend.get_router_input(arn=arn)
        return json.dumps({"routerInput": ri.to_dict()})

    def delete_router_input(self) -> str:
        arn = self.get_router_resource_arn()
        result_arn = self.mediaconnect_backend.delete_router_input(arn=arn)
        return json.dumps({"arn": result_arn})

    def update_router_input(self) -> str:
        arn = self.get_router_resource_arn()
        name = self._get_param("name")
        data_type = self._get_param("dataType")
        ip = self._get_param("ip")
        port = self._get_param("port")
        network_interface_arn = self._get_param("networkInterfaceArn")
        ri = self.mediaconnect_backend.update_router_input(
            arn=arn,
            name=name,
            data_type=data_type,
            ip=ip,
            port=port,
            network_interface_arn=network_interface_arn,
        )
        return json.dumps({"routerInput": ri.to_dict()})

    def list_router_inputs(self) -> str:
        max_results = self._get_int_param("maxResults")
        filter_arn = self._get_param("filterArn")
        inputs = self.mediaconnect_backend.list_router_inputs(
            max_results=max_results, filter_arn=filter_arn
        )
        return json.dumps({"routerInputs": inputs})

    def batch_get_router_input(self) -> str:
        arns = self.querystring.get("arns", [])
        results = self.mediaconnect_backend.batch_get_router_input(arns=arns)
        return json.dumps({"routerInputs": results})

    def start_router_input(self) -> str:
        arn = self.get_router_resource_arn()
        ri = self.mediaconnect_backend.start_router_input(arn=arn)
        return json.dumps({"arn": ri.arn, "state": ri.state})

    def stop_router_input(self) -> str:
        arn = self.get_router_resource_arn()
        ri = self.mediaconnect_backend.stop_router_input(arn=arn)
        return json.dumps({"arn": ri.arn, "state": ri.state})

    def restart_router_input(self) -> str:
        arn = self.get_router_resource_arn()
        ri = self.mediaconnect_backend.restart_router_input(arn=arn)
        return json.dumps({"arn": ri.arn, "state": ri.state})

    def get_router_input_source_metadata(self) -> str:
        arn = self.get_router_resource_arn()
        result = self.mediaconnect_backend.get_router_input_source_metadata(arn=arn)
        return json.dumps(result)

    def get_router_input_thumbnail(self) -> str:
        arn = self.get_router_resource_arn()
        result = self.mediaconnect_backend.get_router_input_thumbnail(arn=arn)
        return json.dumps(result)

    # --- Router Network Interface operations ---

    def create_router_network_interface(self) -> str:
        name = self._get_param("name", "")
        router_arn = self._get_param("routerArn", "")
        gateway_arn = self._get_param("gatewayArn", "")
        network_name = self._get_param("networkName", "")
        ip_address = self._get_param("ipAddress", "10.0.0.1")
        subnet_mask = self._get_param("subnetMask", "255.255.255.0")
        default_gateway = self._get_param("defaultGateway", "10.0.0.1")
        rni = self.mediaconnect_backend.create_router_network_interface(
            name=name,
            router_arn=router_arn,
            gateway_arn=gateway_arn,
            network_name=network_name,
            ip_address=ip_address,
            subnet_mask=subnet_mask,
            default_gateway=default_gateway,
        )
        return json.dumps({"routerNetworkInterface": rni.to_dict()})

    def get_router_network_interface(self) -> str:
        arn = self.get_router_resource_arn()
        rni = self.mediaconnect_backend.get_router_network_interface(arn=arn)
        return json.dumps({"routerNetworkInterface": rni.to_dict()})

    def delete_router_network_interface(self) -> str:
        arn = self.get_router_resource_arn()
        result_arn = self.mediaconnect_backend.delete_router_network_interface(arn=arn)
        return json.dumps({"arn": result_arn})

    def update_router_network_interface(self) -> str:
        arn = self.get_router_resource_arn()
        name = self._get_param("name")
        network_name = self._get_param("networkName")
        ip_address = self._get_param("ipAddress")
        subnet_mask = self._get_param("subnetMask")
        default_gateway = self._get_param("defaultGateway")
        rni = self.mediaconnect_backend.update_router_network_interface(
            arn=arn,
            name=name,
            network_name=network_name,
            ip_address=ip_address,
            subnet_mask=subnet_mask,
            default_gateway=default_gateway,
        )
        return json.dumps({"routerNetworkInterface": rni.to_dict()})

    def list_router_network_interfaces(self) -> str:
        max_results = self._get_int_param("maxResults")
        filter_arn = self._get_param("filterArn")
        interfaces = self.mediaconnect_backend.list_router_network_interfaces(
            max_results=max_results, filter_arn=filter_arn
        )
        return json.dumps({"routerNetworkInterfaces": interfaces})

    def batch_get_router_network_interface(self) -> str:
        arns = self.querystring.get("arns", [])
        results = self.mediaconnect_backend.batch_get_router_network_interface(
            arns=arns
        )
        return json.dumps({"routerNetworkInterfaces": results})

    # --- Router Output operations ---

    def create_router_output(self) -> str:
        name = self._get_param("name", "")
        router_arn = self._get_param("routerArn", "")
        gateway_arn = self._get_param("gatewayArn", "")
        data_type = self._get_param("dataType", "sdi")
        ip = self._get_param("ip", "")
        port = self._get_param("port", 0)
        network_interface_arn = self._get_param("networkInterfaceArn", "")
        ro = self.mediaconnect_backend.create_router_output(
            name=name,
            router_arn=router_arn,
            gateway_arn=gateway_arn,
            data_type=data_type,
            ip=ip,
            port=port,
            network_interface_arn=network_interface_arn,
        )
        return json.dumps({"routerOutput": ro.to_dict()})

    def get_router_output(self) -> str:
        arn = self.get_router_resource_arn()
        ro = self.mediaconnect_backend.get_router_output(arn=arn)
        return json.dumps({"routerOutput": ro.to_dict()})

    def delete_router_output(self) -> str:
        arn = self.get_router_resource_arn()
        result_arn = self.mediaconnect_backend.delete_router_output(arn=arn)
        return json.dumps({"arn": result_arn})

    def update_router_output(self) -> str:
        arn = self.get_router_resource_arn()
        name = self._get_param("name")
        data_type = self._get_param("dataType")
        ip = self._get_param("ip")
        port = self._get_param("port")
        network_interface_arn = self._get_param("networkInterfaceArn")
        ro = self.mediaconnect_backend.update_router_output(
            arn=arn,
            name=name,
            data_type=data_type,
            ip=ip,
            port=port,
            network_interface_arn=network_interface_arn,
        )
        return json.dumps({"routerOutput": ro.to_dict()})

    def list_router_outputs(self) -> str:
        max_results = self._get_int_param("maxResults")
        filter_arn = self._get_param("filterArn")
        outputs = self.mediaconnect_backend.list_router_outputs(
            max_results=max_results, filter_arn=filter_arn
        )
        return json.dumps({"routerOutputs": outputs})

    def batch_get_router_output(self) -> str:
        arns = self.querystring.get("arns", [])
        results = self.mediaconnect_backend.batch_get_router_output(arns=arns)
        return json.dumps({"routerOutputs": results})

    def start_router_output(self) -> str:
        arn = self.get_router_resource_arn()
        ro = self.mediaconnect_backend.start_router_output(arn=arn)
        return json.dumps({"arn": ro.arn, "state": ro.state})

    def stop_router_output(self) -> str:
        arn = self.get_router_resource_arn()
        ro = self.mediaconnect_backend.stop_router_output(arn=arn)
        return json.dumps({"arn": ro.arn, "state": ro.state})

    def restart_router_output(self) -> str:
        arn = self.get_router_resource_arn()
        ro = self.mediaconnect_backend.restart_router_output(arn=arn)
        return json.dumps({"arn": ro.arn, "state": ro.state})

    def take_router_input(self) -> str:
        router_output_arn = self._get_param("routerOutputArn") or self._get_param(
            "RouterOutputArn", ""
        )
        if not router_output_arn:
            # Extract from URL path
            parts = self.path.split("/")
            for i, part in enumerate(parts):
                if part == "takeRouterInput" and i + 1 < len(parts):
                    router_output_arn = unquote(parts[i + 1])
                    break
        router_input_arn = self._get_param("routerInputArn", "")
        ro = self.mediaconnect_backend.take_router_input(
            router_output_arn=unquote(router_output_arn),
            router_input_arn=router_input_arn,
        )
        return json.dumps({"routerOutput": ro.to_dict()})

    # --- Helper methods to extract ARNs from URL ---

    def get_flow_arn(self) -> str:
        # Parameter name changed to UpperCase in botocore==1.37.16
        # https://github.com/boto/botocore/commit/e26766703cd11937c144ad74edf16c657d13c3f9#diff-519c5d5eac7160096946a495de3480423e1a0e56b14c4fbf1b38d1b6bc57303f
        flow_arn = self._get_param("flowArn") or self._get_param("FlowArn")
        return unquote(flow_arn)

    def get_entitlement_arn(self) -> str:
        entitlement_arn = self._get_param("entitlementArn") or self._get_param(
            "EntitlementArn", ""
        )
        return unquote(entitlement_arn)

    def get_source_arn(self) -> str:
        source_arn = self._get_param("sourceArn") or self._get_param("SourceArn", "")
        return unquote(source_arn)

    def get_output_arn(self) -> str:
        output_name = self._get_param("outputArn") or self._get_param("OutputArn", "")
        return unquote(output_name)

    def get_vpc_interface_name(self) -> str:
        vpc_interface_name = self._get_param("vpcInterfaceName") or self._get_param(
            "VpcInterfaceName", ""
        )
        return unquote(vpc_interface_name)

    def get_media_stream_name(self) -> str:
        name = self._get_param("mediaStreamName") or self._get_param(
            "MediaStreamName", ""
        )
        return unquote(name)

    def get_bridge_arn(self) -> str:
        arn = self._get_param("bridgeArn") or self._get_param("BridgeArn", "")
        return unquote(arn)

    def get_gateway_arn(self) -> str:
        arn = self._get_param("gatewayArn") or self._get_param("GatewayArn", "")
        return unquote(arn)

    def get_gateway_instance_arn(self) -> str:
        arn = self._get_param("gatewayInstanceArn") or self._get_param(
            "GatewayInstanceArn", ""
        )
        return unquote(arn)

    def get_offering_arn(self) -> str:
        arn = self._get_param("offeringArn") or self._get_param("OfferingArn", "")
        return unquote(arn)

    def get_reservation_arn(self) -> str:
        arn = self._get_param("reservationArn") or self._get_param(
            "ReservationArn", ""
        )
        return unquote(arn)

    def get_bridge_output_name(self) -> str:
        name = self._get_param("outputName") or self._get_param("OutputName", "")
        return unquote(name)

    def get_bridge_source_name(self) -> str:
        name = self._get_param("sourceName") or self._get_param("SourceName", "")
        return unquote(name)

    def get_router_resource_arn(self) -> str:
        arn = self._get_param("arn") or self._get_param("Arn", "")
        return unquote(arn)
