from collections import OrderedDict
from typing import Any, Optional

from moto.core.base_backend import BackendDict, BaseBackend
from moto.core.common_models import BaseModel
from moto.mediaconnect.exceptions import NotFoundException
from moto.moto_api._internal import mock_random as random
from moto.utilities.tagging_service import TaggingService
from moto.utilities.utils import get_partition


class Flow(BaseModel):
    def __init__(self, account_id: str, region_name: str, **kwargs: Any):
        self.id = random.uuid4().hex
        self.availability_zone = kwargs.get("availability_zone")
        self.entitlements = kwargs.get("entitlements", [])
        self.name = kwargs.get("name")
        self.outputs = kwargs.get("outputs", [])
        self.source = kwargs.get("source", {})
        self.source_failover_config = kwargs.get("source_failover_config", {})
        self.sources = kwargs.get("sources", [])
        self.vpc_interfaces = kwargs.get("vpc_interfaces", [])
        self.media_streams: list[dict[str, Any]] = kwargs.get("media_streams", [])
        self.status: Optional[str] = (
            "STANDBY"  # one of 'STANDBY'|'ACTIVE'|'UPDATING'|'DELETING'|'STARTING'|'STOPPING'|'ERROR'
        )
        self._previous_status: Optional[str] = None
        self.description = kwargs.get("description", "A Moto test flow")
        self.flow_arn = f"arn:{get_partition(region_name)}:mediaconnect:{region_name}:{account_id}:flow:{self.id}:{self.name}"
        self.egress_ip = "127.0.0.1"
        self.maintenance = kwargs.get("maintenance", {})
        if self.source and not self.sources:
            self.sources = [
                self.source,
            ]

    def to_dict(self, include: Optional[list[str]] = None) -> dict[str, Any]:
        data = {
            "availabilityZone": self.availability_zone,
            "description": self.description,
            "egressIp": self.egress_ip,
            "entitlements": self.entitlements,
            "flowArn": self.flow_arn,
            "name": self.name,
            "outputs": self.outputs,
            "source": self.source,
            "sourceFailoverConfig": self.source_failover_config,
            "sources": self.sources,
            "status": self.status,
            "vpcInterfaces": self.vpc_interfaces,
            "mediaStreams": self.media_streams,
        }

        if self.maintenance:
            data["maintenance"] = self.maintenance

        if include:
            new_data = {k: v for k, v in data.items() if k in include}
            if "sourceType" in include:
                new_data["sourceType"] = "OWNED"
            return new_data
        return data

    def resolve_transient_states(self) -> None:
        if self.status in ["STARTING"]:
            self.status = "ACTIVE"
        if self.status in ["STOPPING"]:
            self.status = "STANDBY"
        if self.status in ["UPDATING"]:
            self.status = self._previous_status
            self._previous_status = None


class Bridge(BaseModel):
    def __init__(self, account_id: str, region_name: str, **kwargs: Any):
        self.id = random.uuid4().hex
        self.name = kwargs.get("name", "")
        self.placement_arn = kwargs.get("placement_arn", "")
        self.sources: list[dict[str, Any]] = kwargs.get("sources", [])
        self.outputs: list[dict[str, Any]] = kwargs.get("outputs", [])
        self.source_failover_config = kwargs.get("source_failover_config", {})
        self.egress_gateway_bridge = kwargs.get("egress_gateway_bridge", {})
        self.ingress_gateway_bridge = kwargs.get("ingress_gateway_bridge", {})
        self.bridge_state = "ACTIVE"
        self.bridge_arn = (
            f"arn:{get_partition(region_name)}:mediaconnect:{region_name}"
            f":{account_id}:bridge:{self.id}:{self.name}"
        )
        # Add ARNs to sources/outputs
        for source in self.sources:
            if "flowSource" in source:
                source["flowSource"]["sourceArn"] = (
                    f"arn:{get_partition(region_name)}:mediaconnect:{region_name}"
                    f":{account_id}:bridge-source:{random.uuid4().hex}"
                    f":{source['flowSource'].get('name', '')}"
                )
            if "networkSource" in source:
                source["networkSource"]["sourceArn"] = (
                    f"arn:{get_partition(region_name)}:mediaconnect:{region_name}"
                    f":{account_id}:bridge-source:{random.uuid4().hex}"
                    f":{source['networkSource'].get('name', '')}"
                )
        for output in self.outputs:
            if "networkOutput" in output:
                output["networkOutput"]["outputArn"] = (
                    f"arn:{get_partition(region_name)}:mediaconnect:{region_name}"
                    f":{account_id}:bridge-output:{random.uuid4().hex}"
                    f":{output['networkOutput'].get('name', '')}"
                )

    def to_dict(self) -> dict[str, Any]:
        data: dict[str, Any] = {
            "bridgeArn": self.bridge_arn,
            "bridgeState": self.bridge_state,
            "name": self.name,
            "placementArn": self.placement_arn,
            "sources": self.sources,
            "outputs": self.outputs,
        }
        if self.source_failover_config:
            data["sourceFailoverConfig"] = self.source_failover_config
        if self.egress_gateway_bridge:
            data["egressGatewayBridge"] = self.egress_gateway_bridge
        if self.ingress_gateway_bridge:
            data["ingressGatewayBridge"] = self.ingress_gateway_bridge
        return data

    def to_list_dict(self) -> dict[str, Any]:
        return {
            "bridgeArn": self.bridge_arn,
            "bridgeState": self.bridge_state,
            "bridgeType": "TRANSPARENT_PIPELINE",
            "name": self.name,
            "placementArn": self.placement_arn,
        }


class Gateway(BaseModel):
    def __init__(self, account_id: str, region_name: str, **kwargs: Any):
        self.id = random.uuid4().hex
        self.name = kwargs.get("name", "")
        self.egress_cidr_blocks: list[str] = kwargs.get("egress_cidr_blocks", [])
        self.networks: list[dict[str, Any]] = kwargs.get("networks", [])
        self.gateway_state = "ACTIVE"
        self.gateway_arn = (
            f"arn:{get_partition(region_name)}:mediaconnect:{region_name}"
            f":{account_id}:gateway:{self.id}:{self.name}"
        )
        self._instances: list[dict[str, Any]] = []

    def to_dict(self) -> dict[str, Any]:
        return {
            "egressCidrBlocks": self.egress_cidr_blocks,
            "gatewayArn": self.gateway_arn,
            "gatewayMessages": [],
            "gatewayState": self.gateway_state,
            "name": self.name,
            "networks": self.networks,
        }

    def to_list_dict(self) -> dict[str, Any]:
        return {
            "gatewayArn": self.gateway_arn,
            "gatewayState": self.gateway_state,
            "name": self.name,
        }


class GatewayInstance(BaseModel):
    def __init__(self, account_id: str, region_name: str, **kwargs: Any):
        self.id = random.uuid4().hex
        self.gateway_arn = kwargs.get("gateway_arn", "")
        self.gateway_instance_arn = (
            f"arn:{get_partition(region_name)}:mediaconnect:{region_name}"
            f":{account_id}:gateway-instance:{self.id}"
        )
        self.instance_id = kwargs.get("instance_id", f"i-{random.uuid4().hex[:17]}")
        self.instance_state = "ACTIVE"
        self.bridge_placement = kwargs.get("bridge_placement", "AVAILABLE")
        self.instance_messages: list[dict[str, Any]] = []
        self.running_bridge_count = 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "bridgePlacement": self.bridge_placement,
            "connectionStatus": "CONNECTED",
            "gatewayArn": self.gateway_arn,
            "gatewayInstanceArn": self.gateway_instance_arn,
            "instanceId": self.instance_id,
            "instanceMessages": self.instance_messages,
            "instanceState": self.instance_state,
            "runningBridgeCount": self.running_bridge_count,
        }

    def to_list_dict(self) -> dict[str, Any]:
        return {
            "gatewayArn": self.gateway_arn,
            "gatewayInstanceArn": self.gateway_instance_arn,
            "instanceId": self.instance_id,
            "instanceState": self.instance_state,
        }


class Offering(BaseModel):
    def __init__(self, account_id: str, region_name: str, **kwargs: Any):
        self.id = random.uuid4().hex
        self.offering_arn = (
            f"arn:{get_partition(region_name)}:mediaconnect:{region_name}"
            f":{account_id}:offering:{self.id}"
        )
        self.currency_code = "USD"
        self.duration = kwargs.get("duration", 12)
        self.duration_units = kwargs.get("duration_units", "MONTHS")
        self.offering_description = kwargs.get(
            "offering_description", "Test offering"
        )
        self.price_per_unit = kwargs.get("price_per_unit", "0.10")
        self.price_units = kwargs.get("price_units", "HOURLY")
        self.resource_specification = kwargs.get("resource_specification", {
            "resourceType": "Mbps_Outbound_Bandwidth",
            "reservedBitrate": 100,
        })

    def to_dict(self) -> dict[str, Any]:
        return {
            "currencyCode": self.currency_code,
            "duration": self.duration,
            "durationUnits": self.duration_units,
            "offeringArn": self.offering_arn,
            "offeringDescription": self.offering_description,
            "pricePerUnit": self.price_per_unit,
            "priceUnits": self.price_units,
            "resourceSpecification": self.resource_specification,
        }


class Reservation(BaseModel):
    def __init__(self, account_id: str, region_name: str, offering: Offering, **kwargs: Any):
        self.id = random.uuid4().hex
        self.reservation_arn = (
            f"arn:{get_partition(region_name)}:mediaconnect:{region_name}"
            f":{account_id}:reservation:{self.id}"
        )
        self.reservation_name = kwargs.get("reservation_name", "")
        self.start = kwargs.get("start", "2024-01-01T00:00:00Z")
        self.end = kwargs.get("end", "2025-01-01T00:00:00Z")
        self.reservation_state = "ACTIVE"
        self.offering = offering
        self.currency_code = offering.currency_code
        self.duration = offering.duration
        self.duration_units = offering.duration_units
        self.offering_arn = offering.offering_arn
        self.offering_description = offering.offering_description
        self.price_per_unit = offering.price_per_unit
        self.price_units = offering.price_units
        self.resource_specification = offering.resource_specification

    def to_dict(self) -> dict[str, Any]:
        return {
            "currencyCode": self.currency_code,
            "duration": self.duration,
            "durationUnits": self.duration_units,
            "end": self.end,
            "offeringArn": self.offering_arn,
            "offeringDescription": self.offering_description,
            "pricePerUnit": self.price_per_unit,
            "priceUnits": self.price_units,
            "reservationArn": self.reservation_arn,
            "reservationName": self.reservation_name,
            "reservationState": self.reservation_state,
            "resourceSpecification": self.resource_specification,
            "start": self.start,
        }


class RouterInput(BaseModel):
    def __init__(self, account_id: str, region_name: str, **kwargs: Any):
        self.id = random.uuid4().hex
        self.name = kwargs.get("name", "")
        self.router_arn = kwargs.get("router_arn", "")
        self.gateway_arn = kwargs.get("gateway_arn", "")
        self.data_type = kwargs.get("data_type", "sdi")
        self.ip = kwargs.get("ip", "")
        self.port = kwargs.get("port", 0)
        self.network_interface_arn = kwargs.get("network_interface_arn", "")
        self.state = "ACTIVE"
        self.arn = (
            f"arn:{get_partition(region_name)}:mediaconnect:{region_name}"
            f":{account_id}:router-input:{self.id}:{self.name}"
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "arn": self.arn,
            "dataType": self.data_type,
            "gatewayArn": self.gateway_arn,
            "ip": self.ip,
            "name": self.name,
            "networkInterfaceArn": self.network_interface_arn,
            "port": self.port,
            "routerArn": self.router_arn,
            "state": self.state,
        }


class RouterNetworkInterface(BaseModel):
    def __init__(self, account_id: str, region_name: str, **kwargs: Any):
        self.id = random.uuid4().hex
        self.name = kwargs.get("name", "")
        self.router_arn = kwargs.get("router_arn", "")
        self.gateway_arn = kwargs.get("gateway_arn", "")
        self.network_name = kwargs.get("network_name", "")
        self.ip_address = kwargs.get("ip_address", "10.0.0.1")
        self.subnet_mask = kwargs.get("subnet_mask", "255.255.255.0")
        self.default_gateway = kwargs.get("default_gateway", "10.0.0.1")
        self.state = "ACTIVE"
        self.arn = (
            f"arn:{get_partition(region_name)}:mediaconnect:{region_name}"
            f":{account_id}:router-network-interface:{self.id}:{self.name}"
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "arn": self.arn,
            "defaultGateway": self.default_gateway,
            "gatewayArn": self.gateway_arn,
            "ipAddress": self.ip_address,
            "name": self.name,
            "networkName": self.network_name,
            "routerArn": self.router_arn,
            "state": self.state,
            "subnetMask": self.subnet_mask,
        }


class RouterOutput(BaseModel):
    def __init__(self, account_id: str, region_name: str, **kwargs: Any):
        self.id = random.uuid4().hex
        self.name = kwargs.get("name", "")
        self.router_arn = kwargs.get("router_arn", "")
        self.gateway_arn = kwargs.get("gateway_arn", "")
        self.data_type = kwargs.get("data_type", "sdi")
        self.ip = kwargs.get("ip", "")
        self.port = kwargs.get("port", 0)
        self.network_interface_arn = kwargs.get("network_interface_arn", "")
        self.state = "ACTIVE"
        self.router_input_arn = kwargs.get("router_input_arn", "")
        self.arn = (
            f"arn:{get_partition(region_name)}:mediaconnect:{region_name}"
            f":{account_id}:router-output:{self.id}:{self.name}"
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "arn": self.arn,
            "dataType": self.data_type,
            "gatewayArn": self.gateway_arn,
            "ip": self.ip,
            "name": self.name,
            "networkInterfaceArn": self.network_interface_arn,
            "port": self.port,
            "routerArn": self.router_arn,
            "routerInputArn": self.router_input_arn,
            "state": self.state,
        }


class MediaConnectBackend(BaseBackend):
    def __init__(self, region_name: str, account_id: str):
        super().__init__(region_name, account_id)
        self._flows: dict[str, Flow] = OrderedDict()
        self._bridges: dict[str, Bridge] = OrderedDict()
        self._gateways: dict[str, Gateway] = OrderedDict()
        self._gateway_instances: dict[str, GatewayInstance] = OrderedDict()
        self._offerings: dict[str, Offering] = OrderedDict()
        self._reservations: dict[str, Reservation] = OrderedDict()
        self._router_inputs: dict[str, RouterInput] = OrderedDict()
        self._router_network_interfaces: dict[str, RouterNetworkInterface] = OrderedDict()
        self._router_outputs: dict[str, RouterOutput] = OrderedDict()
        self.tagger = TaggingService()
        # Seed a few offerings
        for i in range(3):
            offering = Offering(
                account_id=self.account_id,
                region_name=self.region_name,
                duration=12,
                offering_description=f"Test offering {i + 1}",
                price_per_unit=f"0.{i + 1}0",
            )
            self._offerings[offering.offering_arn] = offering

    def _add_source_details(
        self,
        source: Optional[dict[str, Any]],
        flow_id: str,
        ingest_ip: str = "127.0.0.1",
    ) -> None:
        if source:
            source["sourceArn"] = (
                f"arn:{get_partition(self.region_name)}:mediaconnect:{self.region_name}:{self.account_id}:source"
                f":{flow_id}:{source['name']}"
            )
            if not source.get("entitlementArn"):
                source["ingestIp"] = ingest_ip

    def _add_entitlement_details(
        self, entitlement: Optional[dict[str, Any]], entitlement_id: str
    ) -> None:
        if entitlement:
            entitlement["entitlementArn"] = (
                f"arn:{get_partition(self.region_name)}:mediaconnect:{self.region_name}"
                f":{self.account_id}:entitlement:{entitlement_id}"
                f":{entitlement['name']}"
            )

    def _create_flow_add_details(self, flow: Flow) -> None:
        for index, _source in enumerate(flow.sources):
            self._add_source_details(_source, flow.id, f"127.0.0.{index}")

        for index, output in enumerate(flow.outputs or []):
            if output.get("protocol") in ["srt-listener", "zixi-pull"]:
                output["listenerAddress"] = f"{index}.0.0.0"
            output_id = random.uuid4().hex
            arn = (
                f"arn:{get_partition(self.region_name)}:mediaconnect:{self.region_name}"
                f":{self.account_id}:output:{output_id}:{output['name']}"
            )
            output["outputArn"] = arn

        for _, entitlement in enumerate(flow.entitlements):
            entitlement_id = random.uuid4().hex
            self._add_entitlement_details(entitlement, entitlement_id)

    def create_flow(
        self,
        availability_zone: str,
        entitlements: list[dict[str, Any]],
        name: str,
        outputs: list[dict[str, Any]],
        source: dict[str, Any],
        source_failover_config: dict[str, Any],
        sources: list[dict[str, Any]],
        vpc_interfaces: list[dict[str, Any]],
        maintenance: Optional[list[dict[str, Any]]] = None,
        media_streams: Optional[list[dict[str, Any]]] = None,
    ) -> Flow:
        flow = Flow(
            account_id=self.account_id,
            region_name=self.region_name,
            availability_zone=availability_zone,
            entitlements=entitlements,
            name=name,
            outputs=outputs,
            source=source,
            source_failover_config=source_failover_config,
            sources=sources,
            vpc_interfaces=vpc_interfaces,
            maintenance=maintenance,
            media_streams=media_streams or [],
        )
        self._create_flow_add_details(flow)
        self._flows[flow.flow_arn] = flow
        return flow

    def list_flows(self, max_results: Optional[int]) -> list[dict[str, Any]]:
        """
        Pagination is not yet implemented
        """
        flows = list(self._flows.values())
        if max_results is not None:
            flows = flows[:max_results]
        return [
            fl.to_dict(
                include=[
                    "availabilityZone",
                    "description",
                    "flowArn",
                    "name",
                    "sourceType",
                    "status",
                ]
            )
            for fl in flows
        ]

    def describe_flow(self, flow_arn: str) -> Flow:
        if flow_arn in self._flows:
            flow = self._flows[flow_arn]
            flow.resolve_transient_states()
            return flow
        raise NotFoundException(message="Flow not found.")

    def delete_flow(self, flow_arn: str) -> Flow:
        if flow_arn in self._flows:
            return self._flows.pop(flow_arn)
        raise NotFoundException(message="Flow not found.")

    def start_flow(self, flow_arn: str) -> Flow:
        if flow_arn in self._flows:
            flow = self._flows[flow_arn]
            flow.status = "STARTING"
            return flow
        raise NotFoundException(message="Flow not found.")

    def stop_flow(self, flow_arn: str) -> Flow:
        if flow_arn in self._flows:
            flow = self._flows[flow_arn]
            flow.status = "STOPPING"
            return flow
        raise NotFoundException(message="Flow not found.")

    def update_flow(
        self,
        flow_arn: str,
        source_failover_config: Optional[dict[str, Any]],
        maintenance: Optional[dict[str, Any]],
    ) -> Flow:
        if flow_arn not in self._flows:
            raise NotFoundException(message="Flow not found.")
        flow = self._flows[flow_arn]
        if source_failover_config is not None:
            flow.source_failover_config = source_failover_config
        if maintenance is not None:
            flow.maintenance = maintenance
        flow._previous_status = flow.status
        flow.status = "UPDATING"
        return flow

    def tag_resource(self, resource_arn: str, tags: dict[str, Any]) -> None:
        tag_list = TaggingService.convert_dict_to_tags_input(tags)
        self.tagger.tag_resource(resource_arn, tag_list)

    def untag_resource(self, resource_arn: str, tag_keys: list[str]) -> None:
        self.tagger.untag_resource_using_names(resource_arn, tag_keys)

    def list_tags_for_resource(self, resource_arn: str) -> dict[str, str]:
        if self.tagger.has_tags(resource_arn):
            return self.tagger.get_tag_dict_for_resource(resource_arn)
        raise NotFoundException(message="Resource not found.")

    def tag_global_resource(self, resource_arn: str, tags: dict[str, Any]) -> None:
        tag_list = TaggingService.convert_dict_to_tags_input(tags)
        self.tagger.tag_resource(resource_arn, tag_list)

    def untag_global_resource(self, resource_arn: str, tag_keys: list[str]) -> None:
        self.tagger.untag_resource_using_names(resource_arn, tag_keys)

    def list_tags_for_global_resource(self, resource_arn: str) -> dict[str, str]:
        if self.tagger.has_tags(resource_arn):
            return self.tagger.get_tag_dict_for_resource(resource_arn)
        raise NotFoundException(message="Resource not found.")

    def add_flow_vpc_interfaces(
        self, flow_arn: str, vpc_interfaces: list[dict[str, Any]]
    ) -> Flow:
        if flow_arn in self._flows:
            flow = self._flows[flow_arn]
            flow.vpc_interfaces = vpc_interfaces
            return flow
        raise NotFoundException(message=f"flow with arn={flow_arn} not found")

    def add_flow_outputs(self, flow_arn: str, outputs: list[dict[str, Any]]) -> Flow:
        if flow_arn in self._flows:
            flow = self._flows[flow_arn]
            flow.outputs = outputs
            return flow
        raise NotFoundException(message=f"flow with arn={flow_arn} not found")

    def remove_flow_vpc_interface(self, flow_arn: str, vpc_interface_name: str) -> None:
        if flow_arn in self._flows:
            flow = self._flows[flow_arn]
            flow.vpc_interfaces = [
                vpc_interface
                for vpc_interface in self._flows[flow_arn].vpc_interfaces
                if vpc_interface["name"] != vpc_interface_name
            ]
        else:
            raise NotFoundException(message=f"flow with arn={flow_arn} not found")

    def remove_flow_output(self, flow_arn: str, output_name: str) -> None:
        if flow_arn in self._flows:
            flow = self._flows[flow_arn]
            flow.outputs = [
                output
                for output in self._flows[flow_arn].outputs
                if output["name"] != output_name
            ]
        else:
            raise NotFoundException(message=f"flow with arn={flow_arn} not found")

    def update_flow_output(
        self,
        flow_arn: str,
        output_arn: str,
        cidr_allow_list: list[str],
        description: str,
        destination: str,
        encryption: dict[str, str],
        max_latency: int,
        media_stream_output_configuration: list[dict[str, Any]],
        min_latency: int,
        port: int,
        protocol: str,
        remote_id: str,
        sender_control_port: int,
        sender_ip_address: str,
        smoothing_latency: int,
        stream_id: str,
        vpc_interface_attachment: dict[str, str],
    ) -> dict[str, Any]:
        if flow_arn not in self._flows:
            raise NotFoundException(message=f"flow with arn={flow_arn} not found")
        flow = self._flows[flow_arn]
        for output in flow.outputs:
            if output["outputArn"] == output_arn:
                output["cidrAllowList"] = cidr_allow_list
                output["description"] = description
                output["destination"] = destination
                output["encryption"] = encryption
                output["maxLatency"] = max_latency
                output["mediaStreamOutputConfiguration"] = (
                    media_stream_output_configuration
                )
                output["minLatency"] = min_latency
                output["port"] = port
                output["protocol"] = protocol
                output["remoteId"] = remote_id
                output["senderControlPort"] = sender_control_port
                output["senderIpAddress"] = sender_ip_address
                output["smoothingLatency"] = smoothing_latency
                output["streamId"] = stream_id
                output["vpcInterfaceAttachment"] = vpc_interface_attachment
                return output
        raise NotFoundException(message=f"output with arn={output_arn} not found")

    def add_flow_sources(
        self, flow_arn: str, sources: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        if flow_arn not in self._flows:
            raise NotFoundException(message=f"flow with arn={flow_arn} not found")
        flow = self._flows[flow_arn]
        for source in sources:
            source_id = random.uuid4().hex
            name = source["name"]
            arn = f"arn:{get_partition(self.region_name)}:mediaconnect:{self.region_name}:{self.account_id}:source:{source_id}:{name}"
            source["sourceArn"] = arn
        flow.sources = sources
        return sources

    def update_flow_source(
        self,
        flow_arn: str,
        source_arn: str,
        decryption: str,
        description: str,
        entitlement_arn: str,
        ingest_port: int,
        max_bitrate: int,
        max_latency: int,
        max_sync_buffer: int,
        media_stream_source_configurations: list[dict[str, Any]],
        min_latency: int,
        protocol: str,
        sender_control_port: int,
        sender_ip_address: str,
        stream_id: str,
        vpc_interface_name: str,
        whitelist_cidr: str,
    ) -> Optional[dict[str, Any]]:
        if flow_arn not in self._flows:
            raise NotFoundException(message=f"flow with arn={flow_arn} not found")
        flow = self._flows[flow_arn]
        source: Optional[dict[str, Any]] = next(
            iter(
                [source for source in flow.sources if source["sourceArn"] == source_arn]
            ),
            {},
        )
        if source:
            source["decryption"] = decryption
            source["description"] = description
            source["entitlementArn"] = entitlement_arn
            source["ingestPort"] = ingest_port
            source["maxBitrate"] = max_bitrate
            source["maxLatency"] = max_latency
            source["maxSyncBuffer"] = max_sync_buffer
            source["mediaStreamSourceConfigurations"] = (
                media_stream_source_configurations
            )
            source["minLatency"] = min_latency
            source["protocol"] = protocol
            source["senderControlPort"] = sender_control_port
            source["senderIpAddress"] = sender_ip_address
            source["streamId"] = stream_id
            source["vpcInterfaceName"] = vpc_interface_name
            source["whitelistCidr"] = whitelist_cidr
        return source

    def remove_flow_source(self, flow_arn: str, source_arn: str) -> None:
        if flow_arn not in self._flows:
            raise NotFoundException(message=f"flow with arn={flow_arn} not found")
        flow = self._flows[flow_arn]
        original_len = len(flow.sources)
        flow.sources = [s for s in flow.sources if s.get("sourceArn") != source_arn]
        if len(flow.sources) == original_len:
            raise NotFoundException(message=f"source with arn={source_arn} not found")

    def grant_flow_entitlements(
        self,
        flow_arn: str,
        entitlements: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        if flow_arn not in self._flows:
            raise NotFoundException(message=f"flow with arn={flow_arn} not found")
        flow = self._flows[flow_arn]
        for entitlement in entitlements:
            entitlement_id = random.uuid4().hex
            name = entitlement["name"]
            arn = f"arn:{get_partition(self.region_name)}:mediaconnect:{self.region_name}:{self.account_id}:entitlement:{entitlement_id}:{name}"
            entitlement["entitlementArn"] = arn

        flow.entitlements += entitlements
        return entitlements

    def revoke_flow_entitlement(self, flow_arn: str, entitlement_arn: str) -> None:
        if flow_arn not in self._flows:
            raise NotFoundException(message=f"flow with arn={flow_arn} not found")
        flow = self._flows[flow_arn]
        for entitlement in flow.entitlements:
            if entitlement_arn == entitlement["entitlementArn"]:
                flow.entitlements.remove(entitlement)
                return
        raise NotFoundException(
            message=f"entitlement with arn={entitlement_arn} not found"
        )

    def update_flow_entitlement(
        self,
        flow_arn: str,
        entitlement_arn: str,
        description: str,
        encryption: dict[str, str],
        entitlement_status: str,
        name: str,
        subscribers: list[str],
    ) -> dict[str, Any]:
        if flow_arn not in self._flows:
            raise NotFoundException(message=f"flow with arn={flow_arn} not found")
        flow = self._flows[flow_arn]
        for entitlement in flow.entitlements:
            if entitlement_arn == entitlement["entitlementArn"]:
                entitlement["description"] = description
                entitlement["encryption"] = encryption
                entitlement["entitlementStatus"] = entitlement_status
                entitlement["name"] = name
                entitlement["subscribers"] = subscribers
                return entitlement
        raise NotFoundException(
            message=f"entitlement with arn={entitlement_arn} not found"
        )

    def list_entitlements(self, max_results: Optional[int]) -> list[dict[str, Any]]:
        """
        Pagination is not yet implemented
        """
        entitlements: list[dict[str, Any]] = []
        for flow in self._flows.values():
            for ent in flow.entitlements:
                entitlements.append({
                    "dataTransferSubscriberFeePercent": ent.get("dataTransferSubscriberFeePercent", 0),
                    "entitlementArn": ent["entitlementArn"],
                    "entitlementName": ent.get("name", ""),
                })
        if max_results is not None:
            entitlements = entitlements[:max_results]
        return entitlements

    # --- Media Streams ---

    def add_flow_media_streams(
        self, flow_arn: str, media_streams: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        if flow_arn not in self._flows:
            raise NotFoundException(message=f"flow with arn={flow_arn} not found")
        flow = self._flows[flow_arn]
        for ms in media_streams:
            ms.setdefault("mediaStreamId", random.randint(1, 999999))
            ms.setdefault("mediaStreamType", "video")
            ms.setdefault("fmt", {})
        flow.media_streams.extend(media_streams)
        return media_streams

    def remove_flow_media_stream(self, flow_arn: str, media_stream_name: str) -> None:
        if flow_arn not in self._flows:
            raise NotFoundException(message=f"flow with arn={flow_arn} not found")
        flow = self._flows[flow_arn]
        original_len = len(flow.media_streams)
        flow.media_streams = [
            ms for ms in flow.media_streams if ms.get("mediaStreamName") != media_stream_name
        ]
        if len(flow.media_streams) == original_len:
            raise NotFoundException(
                message=f"media stream {media_stream_name} not found"
            )

    def update_flow_media_stream(
        self,
        flow_arn: str,
        media_stream_name: str,
        attributes: Optional[dict[str, Any]],
        clock_rate: Optional[int],
        description: Optional[str],
        media_stream_type: Optional[str],
        video_format: Optional[str],
    ) -> dict[str, Any]:
        if flow_arn not in self._flows:
            raise NotFoundException(message=f"flow with arn={flow_arn} not found")
        flow = self._flows[flow_arn]
        for ms in flow.media_streams:
            if ms.get("mediaStreamName") == media_stream_name:
                if attributes is not None:
                    ms["attributes"] = attributes
                if clock_rate is not None:
                    ms["clockRate"] = clock_rate
                if description is not None:
                    ms["description"] = description
                if media_stream_type is not None:
                    ms["mediaStreamType"] = media_stream_type
                if video_format is not None:
                    ms["videoFormat"] = video_format
                return ms
        raise NotFoundException(
            message=f"media stream {media_stream_name} not found"
        )

    def describe_flow_source_metadata(self, flow_arn: str) -> dict[str, Any]:
        if flow_arn not in self._flows:
            raise NotFoundException(message="Flow not found.")
        flow = self._flows[flow_arn]
        return {
            "flowArn": flow.flow_arn,
            "messages": [],
            "timestamp": "2024-01-01T00:00:00Z",
            "transportMediaInfo": {},
        }

    def describe_flow_source_thumbnail(self, flow_arn: str) -> dict[str, Any]:
        if flow_arn not in self._flows:
            raise NotFoundException(message="Flow not found.")
        return {
            "thumbnail": {
                "flowArn": flow_arn,
                "thumbnail": "",
                "timestamp": "2024-01-01T00:00:00Z",
            }
        }

    # --- Bridge operations ---

    def create_bridge(
        self,
        name: str,
        placement_arn: str,
        sources: list[dict[str, Any]],
        outputs: list[dict[str, Any]],
        source_failover_config: Optional[dict[str, Any]],
        egress_gateway_bridge: Optional[dict[str, Any]],
        ingress_gateway_bridge: Optional[dict[str, Any]],
    ) -> Bridge:
        bridge = Bridge(
            account_id=self.account_id,
            region_name=self.region_name,
            name=name,
            placement_arn=placement_arn,
            sources=sources or [],
            outputs=outputs or [],
            source_failover_config=source_failover_config or {},
            egress_gateway_bridge=egress_gateway_bridge or {},
            ingress_gateway_bridge=ingress_gateway_bridge or {},
        )
        self._bridges[bridge.bridge_arn] = bridge
        return bridge

    def list_bridges(self, max_results: Optional[int]) -> list[dict[str, Any]]:
        bridges = list(self._bridges.values())
        if max_results is not None:
            bridges = bridges[:max_results]
        return [b.to_list_dict() for b in bridges]

    def describe_bridge(self, bridge_arn: str) -> Bridge:
        if bridge_arn in self._bridges:
            return self._bridges[bridge_arn]
        raise NotFoundException(message="Bridge not found.")

    def delete_bridge(self, bridge_arn: str) -> str:
        if bridge_arn in self._bridges:
            self._bridges.pop(bridge_arn)
            return bridge_arn
        raise NotFoundException(message="Bridge not found.")

    def update_bridge(
        self,
        bridge_arn: str,
        source_failover_config: Optional[dict[str, Any]],
        egress_gateway_bridge: Optional[dict[str, Any]],
        ingress_gateway_bridge: Optional[dict[str, Any]],
    ) -> Bridge:
        if bridge_arn not in self._bridges:
            raise NotFoundException(message="Bridge not found.")
        bridge = self._bridges[bridge_arn]
        if source_failover_config is not None:
            bridge.source_failover_config = source_failover_config
        if egress_gateway_bridge is not None:
            bridge.egress_gateway_bridge = egress_gateway_bridge
        if ingress_gateway_bridge is not None:
            bridge.ingress_gateway_bridge = ingress_gateway_bridge
        return bridge

    def update_bridge_state(self, bridge_arn: str, desired_state: str) -> Bridge:
        if bridge_arn not in self._bridges:
            raise NotFoundException(message="Bridge not found.")
        bridge = self._bridges[bridge_arn]
        bridge.bridge_state = desired_state
        return bridge

    def add_bridge_outputs(
        self, bridge_arn: str, outputs: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        if bridge_arn not in self._bridges:
            raise NotFoundException(message="Bridge not found.")
        bridge = self._bridges[bridge_arn]
        for output in outputs:
            if "networkOutput" in output:
                output["networkOutput"]["outputArn"] = (
                    f"arn:{get_partition(self.region_name)}:mediaconnect:{self.region_name}"
                    f":{self.account_id}:bridge-output:{random.uuid4().hex}"
                    f":{output['networkOutput'].get('name', '')}"
                )
        bridge.outputs.extend(outputs)
        return outputs

    def remove_bridge_output(self, bridge_arn: str, output_name: str) -> None:
        if bridge_arn not in self._bridges:
            raise NotFoundException(message="Bridge not found.")
        bridge = self._bridges[bridge_arn]
        original_len = len(bridge.outputs)
        bridge.outputs = [
            o for o in bridge.outputs
            if o.get("networkOutput", {}).get("name") != output_name
        ]
        if len(bridge.outputs) == original_len:
            raise NotFoundException(message=f"output {output_name} not found")

    def update_bridge_output(
        self, bridge_arn: str, output_name: str, network_output: Optional[dict[str, Any]]
    ) -> dict[str, Any]:
        if bridge_arn not in self._bridges:
            raise NotFoundException(message="Bridge not found.")
        bridge = self._bridges[bridge_arn]
        for output in bridge.outputs:
            if output.get("networkOutput", {}).get("name") == output_name:
                if network_output is not None:
                    output["networkOutput"].update(network_output)
                return output
        raise NotFoundException(message=f"output {output_name} not found")

    def add_bridge_sources(
        self, bridge_arn: str, sources: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        if bridge_arn not in self._bridges:
            raise NotFoundException(message="Bridge not found.")
        bridge = self._bridges[bridge_arn]
        for source in sources:
            if "flowSource" in source:
                source["flowSource"]["sourceArn"] = (
                    f"arn:{get_partition(self.region_name)}:mediaconnect:{self.region_name}"
                    f":{self.account_id}:bridge-source:{random.uuid4().hex}"
                    f":{source['flowSource'].get('name', '')}"
                )
            if "networkSource" in source:
                source["networkSource"]["sourceArn"] = (
                    f"arn:{get_partition(self.region_name)}:mediaconnect:{self.region_name}"
                    f":{self.account_id}:bridge-source:{random.uuid4().hex}"
                    f":{source['networkSource'].get('name', '')}"
                )
        bridge.sources.extend(sources)
        return sources

    def remove_bridge_source(self, bridge_arn: str, source_name: str) -> None:
        if bridge_arn not in self._bridges:
            raise NotFoundException(message="Bridge not found.")
        bridge = self._bridges[bridge_arn]
        original_len = len(bridge.sources)
        bridge.sources = [
            s for s in bridge.sources
            if (s.get("flowSource", {}).get("name") != source_name
                and s.get("networkSource", {}).get("name") != source_name)
        ]
        if len(bridge.sources) == original_len:
            raise NotFoundException(message=f"source {source_name} not found")

    def update_bridge_source(
        self,
        bridge_arn: str,
        source_name: str,
        flow_source: Optional[dict[str, Any]],
        network_source: Optional[dict[str, Any]],
    ) -> dict[str, Any]:
        if bridge_arn not in self._bridges:
            raise NotFoundException(message="Bridge not found.")
        bridge = self._bridges[bridge_arn]
        for source in bridge.sources:
            if source.get("flowSource", {}).get("name") == source_name:
                if flow_source is not None:
                    source["flowSource"].update(flow_source)
                return source
            if source.get("networkSource", {}).get("name") == source_name:
                if network_source is not None:
                    source["networkSource"].update(network_source)
                return source
        raise NotFoundException(message=f"source {source_name} not found")

    # --- Gateway operations ---

    def create_gateway(
        self,
        name: str,
        egress_cidr_blocks: list[str],
        networks: list[dict[str, Any]],
    ) -> Gateway:
        gw = Gateway(
            account_id=self.account_id,
            region_name=self.region_name,
            name=name,
            egress_cidr_blocks=egress_cidr_blocks,
            networks=networks or [],
        )
        self._gateways[gw.gateway_arn] = gw
        return gw

    def list_gateways(self, max_results: Optional[int]) -> list[dict[str, Any]]:
        gateways = list(self._gateways.values())
        if max_results is not None:
            gateways = gateways[:max_results]
        return [g.to_list_dict() for g in gateways]

    def describe_gateway(self, gateway_arn: str) -> Gateway:
        if gateway_arn in self._gateways:
            return self._gateways[gateway_arn]
        raise NotFoundException(message="Gateway not found.")

    def delete_gateway(self, gateway_arn: str) -> str:
        if gateway_arn in self._gateways:
            self._gateways.pop(gateway_arn)
            return gateway_arn
        raise NotFoundException(message="Gateway not found.")

    # --- Gateway Instance operations ---

    def describe_gateway_instance(self, gateway_instance_arn: str) -> GatewayInstance:
        if gateway_instance_arn in self._gateway_instances:
            return self._gateway_instances[gateway_instance_arn]
        raise NotFoundException(message="Gateway instance not found.")

    def deregister_gateway_instance(
        self, gateway_instance_arn: str, force: bool = False
    ) -> str:
        if gateway_instance_arn in self._gateway_instances:
            self._gateway_instances.pop(gateway_instance_arn)
            return gateway_instance_arn
        raise NotFoundException(message="Gateway instance not found.")

    def list_gateway_instances(
        self, max_results: Optional[int], filter_arn: Optional[str] = None
    ) -> list[dict[str, Any]]:
        instances = list(self._gateway_instances.values())
        if filter_arn:
            instances = [i for i in instances if i.gateway_arn == filter_arn]
        if max_results is not None:
            instances = instances[:max_results]
        return [i.to_list_dict() for i in instances]

    def update_gateway_instance(
        self,
        gateway_instance_arn: str,
        bridge_placement: Optional[str],
    ) -> GatewayInstance:
        if gateway_instance_arn not in self._gateway_instances:
            raise NotFoundException(message="Gateway instance not found.")
        instance = self._gateway_instances[gateway_instance_arn]
        if bridge_placement is not None:
            instance.bridge_placement = bridge_placement
        return instance

    # --- Offering operations ---

    def list_offerings(self, max_results: Optional[int]) -> list[dict[str, Any]]:
        offerings = list(self._offerings.values())
        if max_results is not None:
            offerings = offerings[:max_results]
        return [o.to_dict() for o in offerings]

    def describe_offering(self, offering_arn: str) -> Offering:
        if offering_arn in self._offerings:
            return self._offerings[offering_arn]
        raise NotFoundException(message="Offering not found.")

    def purchase_offering(
        self, offering_arn: str, reservation_name: str, start: str
    ) -> Reservation:
        if offering_arn not in self._offerings:
            raise NotFoundException(message="Offering not found.")
        offering = self._offerings[offering_arn]
        reservation = Reservation(
            account_id=self.account_id,
            region_name=self.region_name,
            offering=offering,
            reservation_name=reservation_name,
            start=start,
        )
        self._reservations[reservation.reservation_arn] = reservation
        return reservation

    # --- Reservation operations ---

    def list_reservations(self, max_results: Optional[int]) -> list[dict[str, Any]]:
        reservations = list(self._reservations.values())
        if max_results is not None:
            reservations = reservations[:max_results]
        return [r.to_dict() for r in reservations]

    def describe_reservation(self, reservation_arn: str) -> Reservation:
        if reservation_arn in self._reservations:
            return self._reservations[reservation_arn]
        raise NotFoundException(message="Reservation not found.")

    # --- Router Input operations ---

    def create_router_input(self, **kwargs: Any) -> RouterInput:
        ri = RouterInput(
            account_id=self.account_id,
            region_name=self.region_name,
            **kwargs,
        )
        self._router_inputs[ri.arn] = ri
        return ri

    def get_router_input(self, arn: str) -> RouterInput:
        if arn in self._router_inputs:
            return self._router_inputs[arn]
        raise NotFoundException(message="Router input not found.")

    def delete_router_input(self, arn: str) -> str:
        if arn in self._router_inputs:
            self._router_inputs.pop(arn)
            return arn
        raise NotFoundException(message="Router input not found.")

    def update_router_input(self, arn: str, **kwargs: Any) -> RouterInput:
        if arn not in self._router_inputs:
            raise NotFoundException(message="Router input not found.")
        ri = self._router_inputs[arn]
        for key, value in kwargs.items():
            if value is not None and hasattr(ri, key):
                setattr(ri, key, value)
        return ri

    def list_router_inputs(
        self,
        max_results: Optional[int],
        filter_arn: Optional[str] = None,
    ) -> list[dict[str, Any]]:
        inputs = list(self._router_inputs.values())
        if filter_arn:
            inputs = [i for i in inputs if i.router_arn == filter_arn or i.gateway_arn == filter_arn]
        if max_results is not None:
            inputs = inputs[:max_results]
        return [i.to_dict() for i in inputs]

    def batch_get_router_input(self, arns: list[str]) -> list[dict[str, Any]]:
        results = []
        for arn in arns:
            if arn in self._router_inputs:
                results.append(self._router_inputs[arn].to_dict())
        return results

    def start_router_input(self, arn: str) -> RouterInput:
        if arn not in self._router_inputs:
            raise NotFoundException(message="Router input not found.")
        ri = self._router_inputs[arn]
        ri.state = "ACTIVE"
        return ri

    def stop_router_input(self, arn: str) -> RouterInput:
        if arn not in self._router_inputs:
            raise NotFoundException(message="Router input not found.")
        ri = self._router_inputs[arn]
        ri.state = "STOPPED"
        return ri

    def restart_router_input(self, arn: str) -> RouterInput:
        if arn not in self._router_inputs:
            raise NotFoundException(message="Router input not found.")
        ri = self._router_inputs[arn]
        ri.state = "ACTIVE"
        return ri

    def get_router_input_source_metadata(self, arn: str) -> dict[str, Any]:
        if arn not in self._router_inputs:
            raise NotFoundException(message="Router input not found.")
        return {
            "routerInputArn": arn,
            "messages": [],
            "timestamp": "2024-01-01T00:00:00Z",
            "transportMediaInfo": {},
        }

    def get_router_input_thumbnail(self, arn: str) -> dict[str, Any]:
        if arn not in self._router_inputs:
            raise NotFoundException(message="Router input not found.")
        return {
            "thumbnail": {
                "routerInputArn": arn,
                "thumbnail": "",
                "timestamp": "2024-01-01T00:00:00Z",
            }
        }

    # --- Router Network Interface operations ---

    def create_router_network_interface(self, **kwargs: Any) -> RouterNetworkInterface:
        rni = RouterNetworkInterface(
            account_id=self.account_id,
            region_name=self.region_name,
            **kwargs,
        )
        self._router_network_interfaces[rni.arn] = rni
        return rni

    def get_router_network_interface(self, arn: str) -> RouterNetworkInterface:
        if arn in self._router_network_interfaces:
            return self._router_network_interfaces[arn]
        raise NotFoundException(message="Router network interface not found.")

    def delete_router_network_interface(self, arn: str) -> str:
        if arn in self._router_network_interfaces:
            self._router_network_interfaces.pop(arn)
            return arn
        raise NotFoundException(message="Router network interface not found.")

    def update_router_network_interface(self, arn: str, **kwargs: Any) -> RouterNetworkInterface:
        if arn not in self._router_network_interfaces:
            raise NotFoundException(message="Router network interface not found.")
        rni = self._router_network_interfaces[arn]
        for key, value in kwargs.items():
            if value is not None and hasattr(rni, key):
                setattr(rni, key, value)
        return rni

    def list_router_network_interfaces(
        self,
        max_results: Optional[int],
        filter_arn: Optional[str] = None,
    ) -> list[dict[str, Any]]:
        interfaces = list(self._router_network_interfaces.values())
        if filter_arn:
            interfaces = [i for i in interfaces if i.router_arn == filter_arn or i.gateway_arn == filter_arn]
        if max_results is not None:
            interfaces = interfaces[:max_results]
        return [i.to_dict() for i in interfaces]

    def batch_get_router_network_interface(self, arns: list[str]) -> list[dict[str, Any]]:
        results = []
        for arn in arns:
            if arn in self._router_network_interfaces:
                results.append(self._router_network_interfaces[arn].to_dict())
        return results

    # --- Router Output operations ---

    def create_router_output(self, **kwargs: Any) -> RouterOutput:
        ro = RouterOutput(
            account_id=self.account_id,
            region_name=self.region_name,
            **kwargs,
        )
        self._router_outputs[ro.arn] = ro
        return ro

    def get_router_output(self, arn: str) -> RouterOutput:
        if arn in self._router_outputs:
            return self._router_outputs[arn]
        raise NotFoundException(message="Router output not found.")

    def delete_router_output(self, arn: str) -> str:
        if arn in self._router_outputs:
            self._router_outputs.pop(arn)
            return arn
        raise NotFoundException(message="Router output not found.")

    def update_router_output(self, arn: str, **kwargs: Any) -> RouterOutput:
        if arn not in self._router_outputs:
            raise NotFoundException(message="Router output not found.")
        ro = self._router_outputs[arn]
        for key, value in kwargs.items():
            if value is not None and hasattr(ro, key):
                setattr(ro, key, value)
        return ro

    def list_router_outputs(
        self,
        max_results: Optional[int],
        filter_arn: Optional[str] = None,
    ) -> list[dict[str, Any]]:
        outputs = list(self._router_outputs.values())
        if filter_arn:
            outputs = [o for o in outputs if o.router_arn == filter_arn or o.gateway_arn == filter_arn]
        if max_results is not None:
            outputs = outputs[:max_results]
        return [o.to_dict() for o in outputs]

    def batch_get_router_output(self, arns: list[str]) -> list[dict[str, Any]]:
        results = []
        for arn in arns:
            if arn in self._router_outputs:
                results.append(self._router_outputs[arn].to_dict())
        return results

    def start_router_output(self, arn: str) -> RouterOutput:
        if arn not in self._router_outputs:
            raise NotFoundException(message="Router output not found.")
        ro = self._router_outputs[arn]
        ro.state = "ACTIVE"
        return ro

    def stop_router_output(self, arn: str) -> RouterOutput:
        if arn not in self._router_outputs:
            raise NotFoundException(message="Router output not found.")
        ro = self._router_outputs[arn]
        ro.state = "STOPPED"
        return ro

    def restart_router_output(self, arn: str) -> RouterOutput:
        if arn not in self._router_outputs:
            raise NotFoundException(message="Router output not found.")
        ro = self._router_outputs[arn]
        ro.state = "ACTIVE"
        return ro

    def take_router_input(
        self, router_output_arn: str, router_input_arn: Optional[str]
    ) -> RouterOutput:
        if router_output_arn not in self._router_outputs:
            raise NotFoundException(message="Router output not found.")
        ro = self._router_outputs[router_output_arn]
        ro.router_input_arn = router_input_arn or ""
        return ro


mediaconnect_backends = BackendDict(MediaConnectBackend, "mediaconnect")
