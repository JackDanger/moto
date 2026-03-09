"""NetworkManagerBackend class with methods for supported APIs."""

from datetime import datetime, timezone
from typing import Any, Optional

from moto.core.base_backend import BackendDict, BaseBackend
from moto.core.common_models import BaseModel
from moto.moto_api._internal import mock_random
from moto.utilities.paginator import paginate
from moto.utilities.utils import PARTITION_NAMES

from .exceptions import ResourceNotFound, ValidationError

PAGINATION_MODEL = {
    "describe_global_networks": {
        "input_token": "next_token",
        "limit_key": "max_results",
        "limit_default": 100,
        "unique_attribute": "global_network_arn",
    },
    "list_core_networks": {
        "input_token": "next_token",
        "limit_key": "max_results",
        "limit_default": 100,
        "unique_attribute": "core_network_arn",
    },
    "get_sites": {
        "input_token": "next_token",
        "limit_key": "max_results",
        "limit_default": 100,
        "unique_attribute": "site_arn",
    },
    "get_links": {
        "input_token": "next_token",
        "limit_key": "max_results",
        "limit_default": 100,
        "unique_attribute": "link_arn",
    },
    "get_devices": {
        "input_token": "next_token",
        "limit_key": "max_results",
        "limit_default": 100,
        "unique_attribute": "device_arn",
    },
    "get_connections": {
        "input_token": "next_token",
        "limit_key": "max_results",
        "limit_default": 100,
        "unique_attribute": "connection_arn",
    },
    "list_attachments": {
        "input_token": "next_token",
        "limit_key": "max_results",
        "limit_default": 100,
        "unique_attribute": "attachment_id",
    },
    "list_connect_peers": {
        "input_token": "next_token",
        "limit_key": "max_results",
        "limit_default": 100,
        "unique_attribute": "connect_peer_id",
    },
    "list_peerings": {
        "input_token": "next_token",
        "limit_key": "max_results",
        "limit_default": 100,
        "unique_attribute": "peering_id",
    },
    "list_core_network_policy_versions": {
        "input_token": "next_token",
        "limit_key": "max_results",
        "limit_default": 100,
        "unique_attribute": "policy_version_id",
    },
    "get_connect_peer_associations": {
        "input_token": "next_token",
        "limit_key": "max_results",
        "limit_default": 100,
        "unique_attribute": "connect_peer_id",
    },
    "get_customer_gateway_associations": {
        "input_token": "next_token",
        "limit_key": "max_results",
        "limit_default": 100,
        "unique_attribute": "customer_gateway_arn",
    },
    "get_link_associations": {
        "input_token": "next_token",
        "limit_key": "max_results",
        "limit_default": 100,
        "unique_attribute": "link_id",
    },
    "get_transit_gateway_connect_peer_associations": {
        "input_token": "next_token",
        "limit_key": "max_results",
        "limit_default": 100,
        "unique_attribute": "transit_gateway_connect_peer_arn",
    },
    "get_transit_gateway_registrations": {
        "input_token": "next_token",
        "limit_key": "max_results",
        "limit_default": 100,
        "unique_attribute": "transit_gateway_arn",
    },
}


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")


class GlobalNetwork(BaseModel):
    def __init__(
        self,
        account_id: str,
        partition: str,
        description: Optional[str],
        tags: Optional[list[dict[str, str]]],
    ):
        self.description = description
        self.tags = tags or []
        self.global_network_id = "global-network-" + "".join(
            mock_random.get_random_hex(18)
        )
        self.global_network_arn = f"arn:{partition}:networkmanager:{account_id}:global-network/{self.global_network_id}"
        self.created_at = _now()
        self.state = "PENDING"

    def to_dict(self) -> dict[str, Any]:
        return {
            "GlobalNetworkId": self.global_network_id,
            "GlobalNetworkArn": self.global_network_arn,
            "Description": self.description,
            "Tags": self.tags,
            "State": self.state,
            "CreatedAt": self.created_at,
        }


class CoreNetwork(BaseModel):
    def __init__(
        self,
        account_id: str,
        partition: str,
        global_network_id: str,
        description: Optional[str],
        tags: Optional[list[dict[str, str]]],
        policy_document: str,
        client_token: str,
    ):
        self.owner_account_id = account_id
        self.global_network_id = global_network_id
        self.description = description
        self.tags = tags or []
        self.policy_document = policy_document
        self.client_token = client_token
        self.core_network_id = "core-network-" + "".join(mock_random.get_random_hex(18))
        self.core_network_arn = f"arn:{partition}:networkmanager:{account_id}:core-network/{self.core_network_id}"
        self.created_at = _now()
        self.state = "PENDING"

    def to_dict(self) -> dict[str, Any]:
        return {
            "CoreNetworkId": self.core_network_id,
            "CoreNetworkArn": self.core_network_arn,
            "GlobalNetworkId": self.global_network_id,
            "OwnerAccountId": self.owner_account_id,
            "Description": self.description,
            "Tags": self.tags,
            "PolicyDocument": self.policy_document,
            "State": self.state,
            "CreatedAt": self.created_at,
        }


class Site(BaseModel):
    def __init__(
        self,
        account_id: str,
        partition: str,
        global_network_id: str,
        description: Optional[str],
        location: Optional[dict[str, Any]],
        tags: Optional[list[dict[str, str]]],
    ):
        self.global_network_id = global_network_id
        self.description = description
        self.location = location
        self.tags = tags or []
        self.site_id = "site-" + "".join(mock_random.get_random_hex(18))
        self.site_arn = (
            f"arn:{partition}:networkmanager:{account_id}:site/{self.site_id}"
        )
        self.created_at = _now()
        self.state = "PENDING"

    def to_dict(self) -> dict[str, Any]:
        return {
            "SiteId": self.site_id,
            "SiteArn": self.site_arn,
            "GlobalNetworkId": self.global_network_id,
            "Description": self.description,
            "Location": self.location,
            "Tags": self.tags,
            "State": self.state,
            "CreatedAt": self.created_at,
        }


class Link(BaseModel):
    def __init__(
        self,
        account_id: str,
        partition: str,
        global_network_id: str,
        description: Optional[str],
        type: Optional[str],
        bandwidth: dict[str, int],
        provider: Optional[str],
        site_id: str,
        tags: Optional[list[dict[str, str]]],
    ):
        self.global_network_id = global_network_id
        self.description = description
        self.type = type
        self.bandwidth = bandwidth
        self.provider = provider
        self.site_id = site_id
        self.tags = tags or []
        self.link_id = "link-" + "".join(mock_random.get_random_hex(18))
        self.link_arn = (
            f"arn:{partition}:networkmanager:{account_id}:link/{self.link_id}"
        )
        self.created_at = _now()
        self.state = "PENDING"

    def to_dict(self) -> dict[str, Any]:
        return {
            "LinkId": self.link_id,
            "LinkArn": self.link_arn,
            "GlobalNetworkId": self.global_network_id,
            "Description": self.description,
            "Type": self.type,
            "Bandwidth": self.bandwidth,
            "Provider": self.provider,
            "SiteId": self.site_id,
            "Tags": self.tags,
            "State": self.state,
            "CreatedAt": self.created_at,
        }


class Device(BaseModel):
    def __init__(
        self,
        account_id: str,
        partition: str,
        global_network_id: str,
        aws_location: Optional[dict[str, str]],
        description: Optional[str],
        type: Optional[str],
        vendor: Optional[str],
        model: Optional[str],
        serial_number: Optional[str],
        location: Optional[dict[str, str]],
        site_id: Optional[str],
        tags: Optional[list[dict[str, str]]],
    ):
        self.global_network_id = global_network_id
        self.aws_location = aws_location
        self.description = description
        self.type = type
        self.vendor = vendor
        self.model = model
        self.serial_number = serial_number
        self.location = location
        self.site_id = site_id
        self.tags = tags or []
        self.device_id = "device-" + "".join(mock_random.get_random_hex(18))
        self.device_arn = (
            f"arn:{partition}:networkmanager:{account_id}:device/{self.device_id}"
        )
        self.created_at = _now()
        self.state = "PENDING"

    def to_dict(self) -> dict[str, Any]:
        return {
            "DeviceId": self.device_id,
            "DeviceArn": self.device_arn,
            "GlobalNetworkId": self.global_network_id,
            "AWSLocation": self.aws_location,
            "Description": self.description,
            "Type": self.type,
            "Vendor": self.vendor,
            "Model": self.model,
            "SerialNumber": self.serial_number,
            "Location": self.location,
            "SiteId": self.site_id,
            "Tags": self.tags,
            "State": self.state,
            "CreatedAt": self.created_at,
        }


class Connection(BaseModel):
    def __init__(
        self,
        account_id: str,
        partition: str,
        global_network_id: str,
        device_id: str,
        connected_device_id: str,
        link_id: Optional[str],
        connected_link_id: Optional[str],
        description: Optional[str],
        tags: Optional[list[dict[str, str]]],
    ):
        self.global_network_id = global_network_id
        self.device_id = device_id
        self.connected_device_id = connected_device_id
        self.link_id = link_id
        self.connected_link_id = connected_link_id
        self.description = description
        self.tags = tags or []
        self.connection_id = "connection-" + "".join(mock_random.get_random_hex(18))
        self.connection_arn = (
            f"arn:{partition}:networkmanager:{account_id}:connection/{self.connection_id}"
        )
        self.created_at = _now()
        self.state = "PENDING"

    def to_dict(self) -> dict[str, Any]:
        return {
            "ConnectionId": self.connection_id,
            "ConnectionArn": self.connection_arn,
            "GlobalNetworkId": self.global_network_id,
            "DeviceId": self.device_id,
            "ConnectedDeviceId": self.connected_device_id,
            "LinkId": self.link_id,
            "ConnectedLinkId": self.connected_link_id,
            "Description": self.description,
            "Tags": self.tags,
            "State": self.state,
            "CreatedAt": self.created_at,
        }


class Attachment(BaseModel):
    def __init__(
        self,
        account_id: str,
        partition: str,
        attachment_type: str,
        core_network_id: Optional[str],
        core_network_arn: Optional[str],
        edge_location: Optional[str],
        tags: Optional[list[dict[str, str]]],
    ):
        self.owner_account_id = account_id
        self.attachment_type = attachment_type
        self.core_network_id = core_network_id
        self.core_network_arn = core_network_arn
        self.edge_location = edge_location or "us-east-1"
        self.tags = tags or []
        self.attachment_id = "attachment-" + "".join(mock_random.get_random_hex(18))
        self.attachment_arn = (
            f"arn:{partition}:networkmanager:{account_id}:attachment/{self.attachment_id}"
        )
        self.created_at = _now()
        self.updated_at = self.created_at
        self.state = "CREATING"
        self.segment_name: Optional[str] = None
        self.resource_arn: Optional[str] = None
        self.attachment_policy_rule_number: Optional[int] = None
        self.routing_policy_label: Optional[str] = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "AttachmentId": self.attachment_id,
            "CoreNetworkId": self.core_network_id,
            "CoreNetworkArn": self.core_network_arn,
            "OwnerAccountId": self.owner_account_id,
            "AttachmentType": self.attachment_type,
            "EdgeLocation": self.edge_location,
            "ResourceArn": self.resource_arn,
            "Tags": self.tags,
            "State": self.state,
            "SegmentName": self.segment_name,
            "CreatedAt": self.created_at,
            "UpdatedAt": self.updated_at,
            "AttachmentPolicyRuleNumber": self.attachment_policy_rule_number,
        }


class VpcAttachment(BaseModel):
    def __init__(
        self,
        account_id: str,
        partition: str,
        core_network_id: str,
        core_network_arn: Optional[str],
        vpc_arn: str,
        subnet_arns: list[str],
        options: Optional[dict[str, Any]],
        tags: Optional[list[dict[str, str]]],
    ):
        self.attachment = Attachment(
            account_id=account_id,
            partition=partition,
            attachment_type="VPC",
            core_network_id=core_network_id,
            core_network_arn=core_network_arn,
            edge_location=None,
            tags=tags,
        )
        self.attachment.resource_arn = vpc_arn
        self.vpc_arn = vpc_arn
        self.subnet_arns = subnet_arns
        self.options = options or {"Ipv6Support": False, "ApplianceModeSupport": False}

    def to_dict(self) -> dict[str, Any]:
        return {
            "Attachment": self.attachment.to_dict(),
            "SubnetArns": self.subnet_arns,
            "Options": self.options,
        }


class ConnectAttachment(BaseModel):
    def __init__(
        self,
        account_id: str,
        partition: str,
        core_network_id: str,
        core_network_arn: Optional[str],
        edge_location: Optional[str],
        transport_attachment_id: str,
        options: Optional[dict[str, Any]],
        tags: Optional[list[dict[str, str]]],
    ):
        self.attachment = Attachment(
            account_id=account_id,
            partition=partition,
            attachment_type="CONNECT",
            core_network_id=core_network_id,
            core_network_arn=core_network_arn,
            edge_location=edge_location,
            tags=tags,
        )
        self.transport_attachment_id = transport_attachment_id
        self.options = options or {"Protocol": "GRE"}

    def to_dict(self) -> dict[str, Any]:
        return {
            "Attachment": self.attachment.to_dict(),
            "TransportAttachmentId": self.transport_attachment_id,
            "Options": self.options,
        }


class SiteToSiteVpnAttachment(BaseModel):
    def __init__(
        self,
        account_id: str,
        partition: str,
        core_network_id: str,
        core_network_arn: Optional[str],
        vpn_connection_arn: str,
        tags: Optional[list[dict[str, str]]],
    ):
        self.attachment = Attachment(
            account_id=account_id,
            partition=partition,
            attachment_type="SITE_TO_SITE_VPN",
            core_network_id=core_network_id,
            core_network_arn=core_network_arn,
            edge_location=None,
            tags=tags,
        )
        self.attachment.resource_arn = vpn_connection_arn
        self.vpn_connection_arn = vpn_connection_arn

    def to_dict(self) -> dict[str, Any]:
        return {
            "Attachment": self.attachment.to_dict(),
            "VpnConnectionArn": self.vpn_connection_arn,
        }


class TransitGatewayRouteTableAttachment(BaseModel):
    def __init__(
        self,
        account_id: str,
        partition: str,
        peering_id: str,
        transit_gateway_route_table_arn: str,
        tags: Optional[list[dict[str, str]]],
        core_network_id: Optional[str] = None,
        core_network_arn: Optional[str] = None,
    ):
        self.attachment = Attachment(
            account_id=account_id,
            partition=partition,
            attachment_type="TRANSIT_GATEWAY_ROUTE_TABLE",
            core_network_id=core_network_id,
            core_network_arn=core_network_arn,
            edge_location=None,
            tags=tags,
        )
        self.attachment.resource_arn = transit_gateway_route_table_arn
        self.peering_id = peering_id
        self.transit_gateway_route_table_arn = transit_gateway_route_table_arn

    def to_dict(self) -> dict[str, Any]:
        return {
            "Attachment": self.attachment.to_dict(),
            "PeeringId": self.peering_id,
            "TransitGatewayRouteTableArn": self.transit_gateway_route_table_arn,
        }


class DirectConnectGatewayAttachment(BaseModel):
    def __init__(
        self,
        account_id: str,
        partition: str,
        core_network_id: str,
        core_network_arn: Optional[str],
        direct_connect_gateway_arn: str,
        edge_locations: Optional[list[str]],
        tags: Optional[list[dict[str, str]]],
    ):
        self.attachment = Attachment(
            account_id=account_id,
            partition=partition,
            attachment_type="DIRECT_CONNECT_GATEWAY",
            core_network_id=core_network_id,
            core_network_arn=core_network_arn,
            edge_location=edge_locations[0] if edge_locations else None,
            tags=tags,
        )
        self.attachment.resource_arn = direct_connect_gateway_arn
        self.direct_connect_gateway_arn = direct_connect_gateway_arn
        self.edge_locations = edge_locations or []

    def to_dict(self) -> dict[str, Any]:
        return {
            "Attachment": self.attachment.to_dict(),
            "DirectConnectGatewayArn": self.direct_connect_gateway_arn,
            "EdgeLocations": self.edge_locations,
        }


class ConnectPeer(BaseModel):
    def __init__(
        self,
        account_id: str,
        partition: str,
        connect_attachment_id: str,
        core_network_address: Optional[str],
        peer_address: str,
        bgp_options: Optional[dict[str, Any]],
        inside_cidr_blocks: Optional[list[str]],
        tags: Optional[list[dict[str, str]]],
        client_token: Optional[str],
        subnet_arn: Optional[str],
    ):
        self.connect_attachment_id = connect_attachment_id
        self.core_network_address = core_network_address
        self.peer_address = peer_address
        self.bgp_options = bgp_options
        self.inside_cidr_blocks = inside_cidr_blocks or []
        self.tags = tags or []
        self.client_token = client_token
        self.subnet_arn = subnet_arn
        self.connect_peer_id = "connect-peer-" + "".join(mock_random.get_random_hex(18))
        self.connect_peer_arn = (
            f"arn:{partition}:networkmanager:{account_id}:connect-peer/{self.connect_peer_id}"
        )
        self.edge_location = "us-east-1"
        self.created_at = _now()
        self.state = "CREATING"
        self.configuration: dict[str, Any] = {
            "CoreNetworkAddress": core_network_address,
            "PeerAddress": peer_address,
            "InsideCidrBlocks": self.inside_cidr_blocks,
            "Protocol": "GRE",
            "BgpConfigurations": [],
        }

    def to_dict(self) -> dict[str, Any]:
        return {
            "ConnectPeerId": self.connect_peer_id,
            "ConnectPeerArn": self.connect_peer_arn,
            "ConnectAttachmentId": self.connect_attachment_id,
            "CoreNetworkId": None,
            "EdgeLocation": self.edge_location,
            "CoreNetworkAddress": self.core_network_address,
            "PeerAddress": self.peer_address,
            "BgpOptions": self.bgp_options,
            "InsideCidrBlocks": self.inside_cidr_blocks,
            "Configuration": self.configuration,
            "Tags": self.tags,
            "State": self.state,
            "CreatedAt": self.created_at,
            "SubnetArn": self.subnet_arn,
        }


class Peering(BaseModel):
    def __init__(
        self,
        account_id: str,
        partition: str,
        core_network_id: str,
        core_network_arn: Optional[str],
        peering_type: str,
        edge_location: Optional[str],
        tags: Optional[list[dict[str, str]]],
    ):
        self.owner_account_id = account_id
        self.core_network_id = core_network_id
        self.core_network_arn = core_network_arn
        self.peering_type = peering_type
        self.edge_location = edge_location or "us-east-1"
        self.tags = tags or []
        self.peering_id = "peering-" + "".join(mock_random.get_random_hex(18))
        self.peering_arn = (
            f"arn:{partition}:networkmanager:{account_id}:peering/{self.peering_id}"
        )
        self.created_at = _now()
        self.state = "CREATING"
        self.resource_arn: Optional[str] = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "PeeringId": self.peering_id,
            "CoreNetworkId": self.core_network_id,
            "CoreNetworkArn": self.core_network_arn,
            "OwnerAccountId": self.owner_account_id,
            "PeeringType": self.peering_type,
            "EdgeLocation": self.edge_location,
            "ResourceArn": self.resource_arn,
            "Tags": self.tags,
            "State": self.state,
            "CreatedAt": self.created_at,
        }


class TransitGatewayPeering(BaseModel):
    def __init__(
        self,
        account_id: str,
        partition: str,
        core_network_id: str,
        core_network_arn: Optional[str],
        transit_gateway_arn: str,
        tags: Optional[list[dict[str, str]]],
    ):
        self.peering = Peering(
            account_id=account_id,
            partition=partition,
            core_network_id=core_network_id,
            core_network_arn=core_network_arn,
            peering_type="TRANSIT_GATEWAY",
            edge_location=None,
            tags=tags,
        )
        self.peering.resource_arn = transit_gateway_arn
        self.transit_gateway_arn = transit_gateway_arn
        self.transit_gateway_peering_attachment_id = "tgw-peering-" + "".join(
            mock_random.get_random_hex(18)
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "Peering": self.peering.to_dict(),
            "TransitGatewayArn": self.transit_gateway_arn,
            "TransitGatewayPeeringAttachmentId": self.transit_gateway_peering_attachment_id,
        }


class CoreNetworkPolicy(BaseModel):
    def __init__(
        self,
        core_network_id: str,
        policy_document: str,
        description: Optional[str],
        client_token: Optional[str],
    ):
        self.core_network_id = core_network_id
        self.policy_document = policy_document
        self.description = description
        self.client_token = client_token
        self.policy_version_id = 1
        self.alias = "LATEST"
        self.created_at = _now()
        self.change_set_state = "READY_TO_EXECUTE"
        self.policy_errors: list[dict[str, Any]] = []

    def to_dict(self) -> dict[str, Any]:
        return {
            "CoreNetworkId": self.core_network_id,
            "PolicyVersionId": self.policy_version_id,
            "Alias": self.alias,
            "Description": self.description,
            "PolicyDocument": self.policy_document,
            "CreatedAt": self.created_at,
            "ChangeSetState": self.change_set_state,
            "PolicyErrors": self.policy_errors,
        }

    def to_version_dict(self) -> dict[str, Any]:
        return {
            "CoreNetworkId": self.core_network_id,
            "PolicyVersionId": self.policy_version_id,
            "Alias": self.alias,
            "Description": self.description,
            "CreatedAt": self.created_at,
            "ChangeSetState": self.change_set_state,
        }


class ConnectPeerAssociation(BaseModel):
    def __init__(
        self,
        global_network_id: str,
        connect_peer_id: str,
        device_id: str,
        link_id: Optional[str],
    ):
        self.global_network_id = global_network_id
        self.connect_peer_id = connect_peer_id
        self.device_id = device_id
        self.link_id = link_id
        self.state = "AVAILABLE"

    def to_dict(self) -> dict[str, Any]:
        return {
            "GlobalNetworkId": self.global_network_id,
            "ConnectPeerId": self.connect_peer_id,
            "DeviceId": self.device_id,
            "LinkId": self.link_id,
            "State": self.state,
        }


class CustomerGatewayAssociation(BaseModel):
    def __init__(
        self,
        global_network_id: str,
        customer_gateway_arn: str,
        device_id: str,
        link_id: Optional[str],
    ):
        self.global_network_id = global_network_id
        self.customer_gateway_arn = customer_gateway_arn
        self.device_id = device_id
        self.link_id = link_id
        self.state = "AVAILABLE"

    def to_dict(self) -> dict[str, Any]:
        return {
            "GlobalNetworkId": self.global_network_id,
            "CustomerGatewayArn": self.customer_gateway_arn,
            "DeviceId": self.device_id,
            "LinkId": self.link_id,
            "State": self.state,
        }


class LinkAssociation(BaseModel):
    def __init__(
        self,
        global_network_id: str,
        device_id: str,
        link_id: str,
    ):
        self.global_network_id = global_network_id
        self.device_id = device_id
        self.link_id = link_id
        self.state = "AVAILABLE"

    def to_dict(self) -> dict[str, Any]:
        return {
            "GlobalNetworkId": self.global_network_id,
            "DeviceId": self.device_id,
            "LinkId": self.link_id,
            "LinkAssociationState": self.state,
        }


class TransitGatewayConnectPeerAssociation(BaseModel):
    def __init__(
        self,
        global_network_id: str,
        transit_gateway_connect_peer_arn: str,
        device_id: str,
        link_id: Optional[str],
    ):
        self.global_network_id = global_network_id
        self.transit_gateway_connect_peer_arn = transit_gateway_connect_peer_arn
        self.device_id = device_id
        self.link_id = link_id
        self.state = "AVAILABLE"

    def to_dict(self) -> dict[str, Any]:
        return {
            "GlobalNetworkId": self.global_network_id,
            "TransitGatewayConnectPeerArn": self.transit_gateway_connect_peer_arn,
            "DeviceId": self.device_id,
            "LinkId": self.link_id,
            "State": self.state,
        }


class TransitGatewayRegistration(BaseModel):
    def __init__(
        self,
        global_network_id: str,
        transit_gateway_arn: str,
    ):
        self.global_network_id = global_network_id
        self.transit_gateway_arn = transit_gateway_arn
        self.state = {"Code": "AVAILABLE", "Message": ""}

    def to_dict(self) -> dict[str, Any]:
        return {
            "GlobalNetworkId": self.global_network_id,
            "TransitGatewayArn": self.transit_gateway_arn,
            "State": self.state,
        }


class RouteAnalysis(BaseModel):
    def __init__(
        self,
        account_id: str,
        global_network_id: str,
        source: Optional[dict[str, Any]],
        destination: Optional[dict[str, Any]],
        include_return_path: bool,
        use_middleboxes: bool,
    ):
        self.owner_account_id = account_id
        self.global_network_id = global_network_id
        self.route_analysis_id = "route-analysis-" + "".join(mock_random.get_random_hex(18))
        self.source = source or {}
        self.destination = destination or {}
        self.include_return_path = include_return_path
        self.use_middleboxes = use_middleboxes
        self.start_timestamp = _now()
        self.status = "COMPLETED"
        self.forward_path: dict[str, Any] = {"CompletionStatus": {"ResultCode": "CONNECTED"}}
        self.return_path: dict[str, Any] = (
            {"CompletionStatus": {"ResultCode": "CONNECTED"}} if include_return_path else {}
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "GlobalNetworkId": self.global_network_id,
            "OwnerAccountId": self.owner_account_id,
            "RouteAnalysisId": self.route_analysis_id,
            "Source": self.source,
            "Destination": self.destination,
            "IncludeReturnPath": self.include_return_path,
            "UseMiddleboxes": self.use_middleboxes,
            "StartTimestamp": self.start_timestamp,
            "Status": self.status,
            "ForwardPath": self.forward_path,
            "ReturnPath": self.return_path,
        }


class CoreNetworkPrefixListAssociation(BaseModel):
    def __init__(
        self,
        core_network_id: str,
        prefix_list: str,
        segment_name: Optional[str],
    ):
        self.core_network_id = core_network_id
        self.prefix_list = prefix_list
        self.segment_name = segment_name

    def to_dict(self) -> dict[str, Any]:
        return {
            "CoreNetworkId": self.core_network_id,
            "PrefixList": self.prefix_list,
            "SegmentName": self.segment_name,
        }


class NetworkManagerBackend(BaseBackend):
    """Implementation of NetworkManager APIs."""

    def __init__(self, region_name: str, account_id: str) -> None:
        super().__init__(region_name, account_id)
        self.global_networks: dict[str, GlobalNetwork] = {}
        self.core_networks: dict[str, CoreNetwork] = {}
        self.sites: dict[str, dict[str, Site]] = {}
        self.links: dict[str, dict[str, Link]] = {}
        self.devices: dict[str, dict[str, Device]] = {}
        self.connections: dict[str, dict[str, Connection]] = {}
        self.attachments: dict[str, Attachment] = {}
        self.vpc_attachments: dict[str, VpcAttachment] = {}
        self.connect_attachments: dict[str, ConnectAttachment] = {}
        self.site_to_site_vpn_attachments: dict[str, SiteToSiteVpnAttachment] = {}
        self.transit_gateway_route_table_attachments: dict[
            str, TransitGatewayRouteTableAttachment
        ] = {}
        self.direct_connect_gateway_attachments: dict[
            str, DirectConnectGatewayAttachment
        ] = {}
        self.connect_peers: dict[str, ConnectPeer] = {}
        self.peerings: dict[str, Peering] = {}
        self.transit_gateway_peerings: dict[str, TransitGatewayPeering] = {}
        self.core_network_policies: dict[str, list[CoreNetworkPolicy]] = {}
        self.resource_policies: dict[str, str] = {}
        self.connect_peer_associations: dict[str, dict[str, ConnectPeerAssociation]] = {}
        self.customer_gateway_associations: dict[str, dict[str, CustomerGatewayAssociation]] = {}
        self.link_associations: dict[str, list[LinkAssociation]] = {}
        self.transit_gateway_connect_peer_associations: dict[
            str, dict[str, TransitGatewayConnectPeerAssociation]
        ] = {}
        self.transit_gateway_registrations: dict[
            str, dict[str, TransitGatewayRegistration]
        ] = {}
        self.route_analyses: dict[str, dict[str, RouteAnalysis]] = {}
        self.core_network_prefix_list_associations: dict[
            str, list[CoreNetworkPrefixListAssociation]
        ] = {}
        self.routing_policy_labels: dict[str, dict[str, str]] = {}
        self.organization_service_access: Optional[str] = None

    def _get_resource_from_arn(self, arn: str) -> Any:
        resources_types: dict[str, dict[str, Any]] = {
            "core-network": self.core_networks,
            "global-network": self.global_networks,
            "site": self.sites,
            "link": self.links,
            "device": self.devices,
            "connection": self.connections,
            "attachment": self.attachments,
            "connect-peer": self.connect_peers,
            "peering": self.peerings,
        }
        try:
            target_resource, target_name = arn.split(":")[-1].split("/")
            resources = resources_types.get(target_resource, {})
            if target_resource not in [
                "core-network", "global-network", "attachment", "connect-peer", "peering",
            ]:
                resources = {
                    k: v
                    for inner_dict in resources.values()
                    for k, v in inner_dict.items()
                }
            return resources[target_name]
        except (KeyError, ValueError, AttributeError):
            raise ResourceNotFound(arn)

    def update_resource_state(self, resource_arn: str, state: str) -> None:
        resource = self._get_resource_from_arn(resource_arn)
        resource.state = state

    def create_global_network(
        self, description: Optional[str], tags: Optional[list[dict[str, str]]],
    ) -> GlobalNetwork:
        global_network = GlobalNetwork(
            description=description, tags=tags,
            account_id=self.account_id, partition=self.partition,
        )
        gnw_id = global_network.global_network_id
        self.global_networks[gnw_id] = global_network
        self.sites[gnw_id] = {}
        self.links[gnw_id] = {}
        self.devices[gnw_id] = {}
        self.connections[gnw_id] = {}
        self.connect_peer_associations[gnw_id] = {}
        self.customer_gateway_associations[gnw_id] = {}
        self.link_associations[gnw_id] = []
        self.transit_gateway_connect_peer_associations[gnw_id] = {}
        self.transit_gateway_registrations[gnw_id] = {}
        self.route_analyses[gnw_id] = {}
        return global_network

    def delete_global_network(self, global_network_id: str) -> GlobalNetwork:
        if global_network_id not in self.global_networks:
            raise ResourceNotFound(global_network_id)
        gn = self.global_networks.pop(global_network_id)
        gn.state = "DELETING"
        for store in [
            self.sites, self.links, self.devices, self.connections,
            self.connect_peer_associations, self.customer_gateway_associations,
            self.link_associations, self.transit_gateway_connect_peer_associations,
            self.transit_gateway_registrations, self.route_analyses,
        ]:
            store.pop(global_network_id, None)
        return gn

    def update_global_network(
        self, global_network_id: str, description: Optional[str],
    ) -> GlobalNetwork:
        if global_network_id not in self.global_networks:
            raise ResourceNotFound(global_network_id)
        gn = self.global_networks[global_network_id]
        if description is not None:
            gn.description = description
        return gn

    def create_core_network(
        self, global_network_id: str, description: Optional[str],
        tags: Optional[list[dict[str, str]]], policy_document: str, client_token: str,
    ) -> CoreNetwork:
        if global_network_id not in self.global_networks:
            raise ResourceNotFound(global_network_id)
        core_network = CoreNetwork(
            global_network_id=global_network_id, description=description, tags=tags,
            policy_document=policy_document, client_token=client_token,
            account_id=self.account_id, partition=self.partition,
        )
        cnw_id = core_network.core_network_id
        self.core_networks[cnw_id] = core_network
        self.core_network_policies[cnw_id] = []
        self.core_network_prefix_list_associations[cnw_id] = []
        self.routing_policy_labels[cnw_id] = {}
        return core_network

    def delete_core_network(self, core_network_id: str) -> CoreNetwork:
        if core_network_id not in self.core_networks:
            raise ResourceNotFound(core_network_id)
        core_network = self.core_networks.pop(core_network_id)
        core_network.state = "DELETING"
        self.core_network_policies.pop(core_network_id, None)
        self.core_network_prefix_list_associations.pop(core_network_id, None)
        self.routing_policy_labels.pop(core_network_id, None)
        return core_network

    def update_core_network(
        self, core_network_id: str, description: Optional[str],
    ) -> CoreNetwork:
        if core_network_id not in self.core_networks:
            raise ResourceNotFound(core_network_id)
        cn = self.core_networks[core_network_id]
        if description is not None:
            cn.description = description
        return cn

    def tag_resource(self, resource_arn: str, tags: list[dict[str, Any]]) -> None:
        resource = self._get_resource_from_arn(resource_arn)
        resource.tags.extend(tags)

    def untag_resource(self, resource_arn: str, tag_keys: Optional[list[str]]) -> None:
        resource = self._get_resource_from_arn(resource_arn)
        if tag_keys:
            resource.tags = [tag for tag in resource.tags if tag["Key"] not in tag_keys]

    @paginate(pagination_model=PAGINATION_MODEL)
    def list_core_networks(self) -> list[CoreNetwork]:
        return list(self.core_networks.values())

    def get_core_network(self, core_network_id: str) -> CoreNetwork:
        if core_network_id not in self.core_networks:
            raise ResourceNotFound(core_network_id)
        return self.core_networks[core_network_id]

    @paginate(pagination_model=PAGINATION_MODEL)
    def describe_global_networks(self, global_network_ids: list[str]) -> list[GlobalNetwork]:
        if not global_network_ids:
            return list(self.global_networks.values())
        elif isinstance(global_network_ids, str):
            if global_network_ids not in self.global_networks:
                raise ResourceNotFound(global_network_ids)
            return [self.global_networks[global_network_ids]]
        else:
            return [self.global_networks[gid] for gid in global_network_ids if gid in self.global_networks]

    def create_site(
        self, global_network_id: str, description: Optional[str],
        location: Optional[dict[str, str]], tags: Optional[list[dict[str, str]]],
    ) -> Site:
        if global_network_id not in self.global_networks:
            raise ResourceNotFound(global_network_id)
        site = Site(
            global_network_id=global_network_id, description=description,
            location=location, tags=tags, account_id=self.account_id, partition=self.partition,
        )
        self.sites[global_network_id][site.site_id] = site
        return site

    def delete_site(self, global_network_id: str, site_id: str) -> Site:
        if global_network_id not in self.global_networks:
            raise ResourceNotFound(global_network_id)
        if global_network_id not in self.sites:
            raise ResourceNotFound(site_id)
        site = self.sites[global_network_id].pop(site_id)
        site.state = "DELETING"
        return site

    def update_site(
        self, global_network_id: str, site_id: str,
        description: Optional[str], location: Optional[dict[str, str]],
    ) -> Site:
        if global_network_id not in self.global_networks:
            raise ResourceNotFound(global_network_id)
        gn_sites = self.sites.get(global_network_id, {})
        if site_id not in gn_sites:
            raise ResourceNotFound(site_id)
        site = gn_sites[site_id]
        if description is not None:
            site.description = description
        if location is not None:
            site.location = location
        return site

    @paginate(pagination_model=PAGINATION_MODEL)
    def get_sites(self, global_network_id: str, site_ids: list[str]) -> list[Site]:
        if global_network_id not in self.global_networks:
            raise ValidationError("Incorrect input.")
        gn_sites = self.sites.get(global_network_id) or {}
        if not site_ids:
            return list(gn_sites.values())
        return [gn_sites[sid] for sid in site_ids if sid in gn_sites]

    def create_link(
        self, global_network_id: str, description: Optional[str], type: Optional[str],
        bandwidth: dict[str, Any], provider: Optional[str], site_id: str,
        tags: Optional[list[dict[str, str]]],
    ) -> Link:
        if global_network_id not in self.global_networks:
            raise ResourceNotFound(global_network_id)
        link = Link(
            global_network_id=global_network_id, description=description, type=type,
            bandwidth=bandwidth, provider=provider, site_id=site_id, tags=tags,
            account_id=self.account_id, partition=self.partition,
        )
        self.links[global_network_id][link.link_id] = link
        return link

    @paginate(pagination_model=PAGINATION_MODEL)
    def get_links(
        self, global_network_id: str, link_ids: list[str], site_id: str, type: str, provider: str,
    ) -> list[Link]:
        if global_network_id not in self.global_networks:
            raise ValidationError("Incorrect input.")
        gn_links = self.links.get(global_network_id) or {}
        if not link_ids:
            return list(gn_links.values())
        return [gn_links[lid] for lid in link_ids if lid in gn_links]

    def delete_link(self, global_network_id: str, link_id: str) -> Link:
        try:
            link = self.links[global_network_id].pop(link_id)
        except KeyError:
            raise ResourceNotFound(link_id)
        link.state = "DELETING"
        return link

    def update_link(
        self, global_network_id: str, link_id: str, description: Optional[str],
        type: Optional[str], bandwidth: Optional[dict[str, Any]], provider: Optional[str],
    ) -> Link:
        if global_network_id not in self.global_networks:
            raise ResourceNotFound(global_network_id)
        gn_links = self.links.get(global_network_id, {})
        if link_id not in gn_links:
            raise ResourceNotFound(link_id)
        link = gn_links[link_id]
        if description is not None:
            link.description = description
        if type is not None:
            link.type = type
        if bandwidth is not None:
            link.bandwidth = bandwidth
        if provider is not None:
            link.provider = provider
        return link

    def create_device(
        self, global_network_id: str, aws_location: Optional[dict[str, str]],
        description: Optional[str], type: Optional[str], vendor: Optional[str],
        model: Optional[str], serial_number: Optional[str],
        location: Optional[dict[str, str]], site_id: Optional[str],
        tags: Optional[list[dict[str, str]]],
    ) -> Device:
        if global_network_id not in self.global_networks:
            raise ResourceNotFound(global_network_id)
        device = Device(
            global_network_id=global_network_id, aws_location=aws_location,
            description=description, type=type, vendor=vendor, model=model,
            serial_number=serial_number, location=location, site_id=site_id,
            tags=tags, account_id=self.account_id, partition=self.partition,
        )
        self.devices[global_network_id][device.device_id] = device
        return device

    @paginate(pagination_model=PAGINATION_MODEL)
    def get_devices(
        self, global_network_id: str, device_ids: list[str], site_id: Optional[str],
    ) -> list[Device]:
        if global_network_id not in self.global_networks:
            raise ValidationError("Incorrect input.")
        gn_devices = self.devices.get(global_network_id) or {}
        if not device_ids:
            return list(gn_devices.values())
        return [gn_devices[did] for did in device_ids if did in gn_devices]

    def delete_device(self, global_network_id: str, device_id: str) -> Device:
        try:
            device = self.devices[global_network_id].pop(device_id)
        except KeyError:
            raise ResourceNotFound(device_id)
        device.state = "DELETING"
        return device

    def update_device(
        self, global_network_id: str, device_id: str,
        aws_location: Optional[dict[str, str]], description: Optional[str],
        type: Optional[str], vendor: Optional[str], model: Optional[str],
        serial_number: Optional[str], location: Optional[dict[str, str]],
        site_id: Optional[str],
    ) -> Device:
        if global_network_id not in self.global_networks:
            raise ResourceNotFound(global_network_id)
        gn_devices = self.devices.get(global_network_id, {})
        if device_id not in gn_devices:
            raise ResourceNotFound(device_id)
        device = gn_devices[device_id]
        if aws_location is not None:
            device.aws_location = aws_location
        if description is not None:
            device.description = description
        if type is not None:
            device.type = type
        if vendor is not None:
            device.vendor = vendor
        if model is not None:
            device.model = model
        if serial_number is not None:
            device.serial_number = serial_number
        if location is not None:
            device.location = location
        if site_id is not None:
            device.site_id = site_id
        return device

    def list_tags_for_resource(self, resource_arn: str) -> list[dict[str, str]]:
        return self._get_resource_from_arn(resource_arn).tags

    # --- Connection ---

    def create_connection(
        self, global_network_id: str, device_id: str, connected_device_id: str,
        link_id: Optional[str], connected_link_id: Optional[str],
        description: Optional[str], tags: Optional[list[dict[str, str]]],
    ) -> Connection:
        if global_network_id not in self.global_networks:
            raise ResourceNotFound(global_network_id)
        conn = Connection(
            account_id=self.account_id, partition=self.partition,
            global_network_id=global_network_id, device_id=device_id,
            connected_device_id=connected_device_id, link_id=link_id,
            connected_link_id=connected_link_id, description=description, tags=tags,
        )
        self.connections[global_network_id][conn.connection_id] = conn
        conn.state = "AVAILABLE"
        return conn

    def delete_connection(self, global_network_id: str, connection_id: str) -> Connection:
        if global_network_id not in self.global_networks:
            raise ResourceNotFound(global_network_id)
        gn_conns = self.connections.get(global_network_id, {})
        if connection_id not in gn_conns:
            raise ResourceNotFound(connection_id)
        conn = gn_conns.pop(connection_id)
        conn.state = "DELETING"
        return conn

    def update_connection(
        self, global_network_id: str, connection_id: str,
        link_id: Optional[str], connected_link_id: Optional[str], description: Optional[str],
    ) -> Connection:
        if global_network_id not in self.global_networks:
            raise ResourceNotFound(global_network_id)
        gn_conns = self.connections.get(global_network_id, {})
        if connection_id not in gn_conns:
            raise ResourceNotFound(connection_id)
        conn = gn_conns[connection_id]
        if link_id is not None:
            conn.link_id = link_id
        if connected_link_id is not None:
            conn.connected_link_id = connected_link_id
        if description is not None:
            conn.description = description
        return conn

    @paginate(pagination_model=PAGINATION_MODEL)
    def get_connections(
        self, global_network_id: str, connection_ids: Optional[list[str]],
        device_id: Optional[str],
    ) -> list[Connection]:
        if global_network_id not in self.global_networks:
            raise ValidationError("Incorrect input.")
        gn_conns = self.connections.get(global_network_id, {})
        if connection_ids:
            return [gn_conns[c] for c in connection_ids if c in gn_conns]
        result = list(gn_conns.values())
        if device_id:
            result = [c for c in result if c.device_id == device_id]
        return result

    # --- Attachments ---

    def create_vpc_attachment(
        self, core_network_id: str, vpc_arn: str, subnet_arns: list[str],
        options: Optional[dict[str, Any]], tags: Optional[list[dict[str, str]]],
        client_token: Optional[str],
    ) -> VpcAttachment:
        cn = self.core_networks.get(core_network_id)
        if not cn:
            raise ResourceNotFound(core_network_id)
        att = VpcAttachment(
            account_id=self.account_id, partition=self.partition,
            core_network_id=core_network_id, core_network_arn=cn.core_network_arn,
            vpc_arn=vpc_arn, subnet_arns=subnet_arns, options=options, tags=tags,
        )
        aid = att.attachment.attachment_id
        self.attachments[aid] = att.attachment
        self.vpc_attachments[aid] = att
        att.attachment.state = "AVAILABLE"
        return att

    def get_vpc_attachment(self, attachment_id: str) -> VpcAttachment:
        if attachment_id not in self.vpc_attachments:
            raise ResourceNotFound(attachment_id)
        return self.vpc_attachments[attachment_id]

    def update_vpc_attachment(
        self, attachment_id: str, add_subnet_arns: Optional[list[str]],
        remove_subnet_arns: Optional[list[str]], options: Optional[dict[str, Any]],
    ) -> VpcAttachment:
        if attachment_id not in self.vpc_attachments:
            raise ResourceNotFound(attachment_id)
        att = self.vpc_attachments[attachment_id]
        if add_subnet_arns:
            att.subnet_arns.extend(add_subnet_arns)
        if remove_subnet_arns:
            att.subnet_arns = [s for s in att.subnet_arns if s not in remove_subnet_arns]
        if options is not None:
            att.options = options
        att.attachment.updated_at = _now()
        return att

    def create_connect_attachment(
        self, core_network_id: str, edge_location: Optional[str],
        transport_attachment_id: str, options: Optional[dict[str, Any]],
        tags: Optional[list[dict[str, str]]], client_token: Optional[str],
    ) -> ConnectAttachment:
        cn = self.core_networks.get(core_network_id)
        if not cn:
            raise ResourceNotFound(core_network_id)
        att = ConnectAttachment(
            account_id=self.account_id, partition=self.partition,
            core_network_id=core_network_id, core_network_arn=cn.core_network_arn,
            edge_location=edge_location, transport_attachment_id=transport_attachment_id,
            options=options, tags=tags,
        )
        aid = att.attachment.attachment_id
        self.attachments[aid] = att.attachment
        self.connect_attachments[aid] = att
        att.attachment.state = "AVAILABLE"
        return att

    def get_connect_attachment(self, attachment_id: str) -> ConnectAttachment:
        if attachment_id not in self.connect_attachments:
            raise ResourceNotFound(attachment_id)
        return self.connect_attachments[attachment_id]

    def create_site_to_site_vpn_attachment(
        self, core_network_id: str, vpn_connection_arn: str,
        tags: Optional[list[dict[str, str]]], client_token: Optional[str],
    ) -> SiteToSiteVpnAttachment:
        cn = self.core_networks.get(core_network_id)
        if not cn:
            raise ResourceNotFound(core_network_id)
        att = SiteToSiteVpnAttachment(
            account_id=self.account_id, partition=self.partition,
            core_network_id=core_network_id, core_network_arn=cn.core_network_arn,
            vpn_connection_arn=vpn_connection_arn, tags=tags,
        )
        aid = att.attachment.attachment_id
        self.attachments[aid] = att.attachment
        self.site_to_site_vpn_attachments[aid] = att
        att.attachment.state = "AVAILABLE"
        return att

    def get_site_to_site_vpn_attachment(self, attachment_id: str) -> SiteToSiteVpnAttachment:
        if attachment_id not in self.site_to_site_vpn_attachments:
            raise ResourceNotFound(attachment_id)
        return self.site_to_site_vpn_attachments[attachment_id]

    def create_transit_gateway_route_table_attachment(
        self, peering_id: str, transit_gateway_route_table_arn: str,
        tags: Optional[list[dict[str, str]]], client_token: Optional[str],
    ) -> TransitGatewayRouteTableAttachment:
        peering_obj = None
        for tgp in self.transit_gateway_peerings.values():
            if tgp.peering.peering_id == peering_id:
                peering_obj = tgp.peering
                break
        if not peering_obj:
            raise ResourceNotFound(peering_id)
        att = TransitGatewayRouteTableAttachment(
            account_id=self.account_id, partition=self.partition,
            peering_id=peering_id, transit_gateway_route_table_arn=transit_gateway_route_table_arn,
            tags=tags, core_network_id=peering_obj.core_network_id,
            core_network_arn=peering_obj.core_network_arn,
        )
        aid = att.attachment.attachment_id
        self.attachments[aid] = att.attachment
        self.transit_gateway_route_table_attachments[aid] = att
        att.attachment.state = "AVAILABLE"
        return att

    def get_transit_gateway_route_table_attachment(
        self, attachment_id: str,
    ) -> TransitGatewayRouteTableAttachment:
        if attachment_id not in self.transit_gateway_route_table_attachments:
            raise ResourceNotFound(attachment_id)
        return self.transit_gateway_route_table_attachments[attachment_id]

    def create_direct_connect_gateway_attachment(
        self, core_network_id: str, direct_connect_gateway_arn: str,
        edge_locations: Optional[list[str]], tags: Optional[list[dict[str, str]]],
        client_token: Optional[str],
    ) -> DirectConnectGatewayAttachment:
        cn = self.core_networks.get(core_network_id)
        if not cn:
            raise ResourceNotFound(core_network_id)
        att = DirectConnectGatewayAttachment(
            account_id=self.account_id, partition=self.partition,
            core_network_id=core_network_id, core_network_arn=cn.core_network_arn,
            direct_connect_gateway_arn=direct_connect_gateway_arn,
            edge_locations=edge_locations, tags=tags,
        )
        aid = att.attachment.attachment_id
        self.attachments[aid] = att.attachment
        self.direct_connect_gateway_attachments[aid] = att
        att.attachment.state = "AVAILABLE"
        return att

    def get_direct_connect_gateway_attachment(
        self, attachment_id: str,
    ) -> DirectConnectGatewayAttachment:
        if attachment_id not in self.direct_connect_gateway_attachments:
            raise ResourceNotFound(attachment_id)
        return self.direct_connect_gateway_attachments[attachment_id]

    def update_direct_connect_gateway_attachment(
        self, attachment_id: str, edge_locations: Optional[list[str]],
    ) -> DirectConnectGatewayAttachment:
        if attachment_id not in self.direct_connect_gateway_attachments:
            raise ResourceNotFound(attachment_id)
        att = self.direct_connect_gateway_attachments[attachment_id]
        if edge_locations is not None:
            att.edge_locations = edge_locations
        att.attachment.updated_at = _now()
        return att

    def delete_attachment(self, attachment_id: str) -> Attachment:
        if attachment_id not in self.attachments:
            raise ResourceNotFound(attachment_id)
        att = self.attachments.pop(attachment_id)
        att.state = "DELETING"
        self.vpc_attachments.pop(attachment_id, None)
        self.connect_attachments.pop(attachment_id, None)
        self.site_to_site_vpn_attachments.pop(attachment_id, None)
        self.transit_gateway_route_table_attachments.pop(attachment_id, None)
        self.direct_connect_gateway_attachments.pop(attachment_id, None)
        return att

    def accept_attachment(self, attachment_id: str) -> Attachment:
        if attachment_id not in self.attachments:
            raise ResourceNotFound(attachment_id)
        att = self.attachments[attachment_id]
        att.state = "AVAILABLE"
        att.updated_at = _now()
        return att

    def reject_attachment(self, attachment_id: str) -> Attachment:
        if attachment_id not in self.attachments:
            raise ResourceNotFound(attachment_id)
        att = self.attachments[attachment_id]
        att.state = "REJECTED"
        att.updated_at = _now()
        return att

    @paginate(pagination_model=PAGINATION_MODEL)
    def list_attachments(
        self, core_network_id: Optional[str], attachment_type: Optional[str],
        edge_location: Optional[str], state: Optional[str],
    ) -> list[Attachment]:
        result = list(self.attachments.values())
        if core_network_id:
            result = [a for a in result if a.core_network_id == core_network_id]
        if attachment_type:
            result = [a for a in result if a.attachment_type == attachment_type]
        if edge_location:
            result = [a for a in result if a.edge_location == edge_location]
        if state:
            result = [a for a in result if a.state == state]
        return result

    # --- Connect Peer ---

    def create_connect_peer(
        self, connect_attachment_id: str, core_network_address: Optional[str],
        peer_address: str, bgp_options: Optional[dict[str, Any]],
        inside_cidr_blocks: Optional[list[str]], tags: Optional[list[dict[str, str]]],
        client_token: Optional[str], subnet_arn: Optional[str],
    ) -> ConnectPeer:
        if connect_attachment_id not in self.connect_attachments:
            raise ResourceNotFound(connect_attachment_id)
        cp = ConnectPeer(
            account_id=self.account_id, partition=self.partition,
            connect_attachment_id=connect_attachment_id,
            core_network_address=core_network_address, peer_address=peer_address,
            bgp_options=bgp_options, inside_cidr_blocks=inside_cidr_blocks,
            tags=tags, client_token=client_token, subnet_arn=subnet_arn,
        )
        self.connect_peers[cp.connect_peer_id] = cp
        cp.state = "AVAILABLE"
        return cp

    def get_connect_peer(self, connect_peer_id: str) -> ConnectPeer:
        if connect_peer_id not in self.connect_peers:
            raise ResourceNotFound(connect_peer_id)
        return self.connect_peers[connect_peer_id]

    def delete_connect_peer(self, connect_peer_id: str) -> ConnectPeer:
        if connect_peer_id not in self.connect_peers:
            raise ResourceNotFound(connect_peer_id)
        cp = self.connect_peers.pop(connect_peer_id)
        cp.state = "DELETING"
        return cp

    @paginate(pagination_model=PAGINATION_MODEL)
    def list_connect_peers(
        self, core_network_id: Optional[str], connect_attachment_id: Optional[str],
    ) -> list[ConnectPeer]:
        result = list(self.connect_peers.values())
        if connect_attachment_id:
            result = [cp for cp in result if cp.connect_attachment_id == connect_attachment_id]
        return result

    # --- Peering ---

    def create_transit_gateway_peering(
        self, core_network_id: str, transit_gateway_arn: str,
        tags: Optional[list[dict[str, str]]], client_token: Optional[str],
    ) -> TransitGatewayPeering:
        cn = self.core_networks.get(core_network_id)
        if not cn:
            raise ResourceNotFound(core_network_id)
        tgp = TransitGatewayPeering(
            account_id=self.account_id, partition=self.partition,
            core_network_id=core_network_id, core_network_arn=cn.core_network_arn,
            transit_gateway_arn=transit_gateway_arn, tags=tags,
        )
        pid = tgp.peering.peering_id
        self.peerings[pid] = tgp.peering
        self.transit_gateway_peerings[pid] = tgp
        tgp.peering.state = "AVAILABLE"
        return tgp

    def get_transit_gateway_peering(self, peering_id: str) -> TransitGatewayPeering:
        if peering_id not in self.transit_gateway_peerings:
            raise ResourceNotFound(peering_id)
        return self.transit_gateway_peerings[peering_id]

    def delete_peering(self, peering_id: str) -> Peering:
        if peering_id not in self.peerings:
            raise ResourceNotFound(peering_id)
        peering = self.peerings.pop(peering_id)
        peering.state = "DELETING"
        self.transit_gateway_peerings.pop(peering_id, None)
        return peering

    @paginate(pagination_model=PAGINATION_MODEL)
    def list_peerings(
        self, core_network_id: Optional[str], peering_type: Optional[str],
        edge_location: Optional[str], state: Optional[str],
    ) -> list[Peering]:
        result = list(self.peerings.values())
        if core_network_id:
            result = [p for p in result if p.core_network_id == core_network_id]
        if peering_type:
            result = [p for p in result if p.peering_type == peering_type]
        if edge_location:
            result = [p for p in result if p.edge_location == edge_location]
        if state:
            result = [p for p in result if p.state == state]
        return result

    # --- Core Network Policy ---

    def put_core_network_policy(
        self, core_network_id: str, policy_document: str,
        description: Optional[str], latest_version_id: Optional[int],
        client_token: Optional[str],
    ) -> CoreNetworkPolicy:
        if core_network_id not in self.core_networks:
            raise ResourceNotFound(core_network_id)
        policy = CoreNetworkPolicy(
            core_network_id=core_network_id, policy_document=policy_document,
            description=description, client_token=client_token,
        )
        policies = self.core_network_policies.get(core_network_id, [])
        policy.policy_version_id = len(policies) + 1
        policies.append(policy)
        self.core_network_policies[core_network_id] = policies
        return policy

    def get_core_network_policy(
        self, core_network_id: str, policy_version_id: Optional[int], alias: Optional[str],
    ) -> CoreNetworkPolicy:
        if core_network_id not in self.core_networks:
            raise ResourceNotFound(core_network_id)
        policies = self.core_network_policies.get(core_network_id, [])
        if not policies:
            raise ResourceNotFound(core_network_id)
        if policy_version_id:
            for p in policies:
                if p.policy_version_id == policy_version_id:
                    return p
            raise ResourceNotFound(str(policy_version_id))
        if alias:
            for p in policies:
                if p.alias == alias:
                    return p
        return policies[-1]

    def delete_core_network_policy_version(
        self, core_network_id: str, policy_version_id: int,
    ) -> CoreNetworkPolicy:
        if core_network_id not in self.core_networks:
            raise ResourceNotFound(core_network_id)
        policies = self.core_network_policies.get(core_network_id, [])
        for i, p in enumerate(policies):
            if p.policy_version_id == policy_version_id:
                return policies.pop(i)
        raise ResourceNotFound(str(policy_version_id))

    def restore_core_network_policy_version(
        self, core_network_id: str, policy_version_id: int,
    ) -> CoreNetworkPolicy:
        if core_network_id not in self.core_networks:
            raise ResourceNotFound(core_network_id)
        policies = self.core_network_policies.get(core_network_id, [])
        for p in policies:
            if p.policy_version_id == policy_version_id:
                new_policy = CoreNetworkPolicy(
                    core_network_id=core_network_id, policy_document=p.policy_document,
                    description=p.description, client_token=p.client_token,
                )
                new_policy.policy_version_id = len(policies) + 1
                policies.append(new_policy)
                return new_policy
        raise ResourceNotFound(str(policy_version_id))

    @paginate(pagination_model=PAGINATION_MODEL)
    def list_core_network_policy_versions(self, core_network_id: str) -> list[CoreNetworkPolicy]:
        if core_network_id not in self.core_networks:
            raise ResourceNotFound(core_network_id)
        return self.core_network_policies.get(core_network_id, [])

    def execute_core_network_change_set(
        self, core_network_id: str, policy_version_id: int,
    ) -> None:
        if core_network_id not in self.core_networks:
            raise ResourceNotFound(core_network_id)
        policies = self.core_network_policies.get(core_network_id, [])
        for p in policies:
            if p.policy_version_id == policy_version_id:
                for other in policies:
                    if other.alias == "LIVE":
                        other.alias = "LATEST"
                p.alias = "LIVE"
                p.change_set_state = "EXECUTION_SUCCEEDED"
                return
        raise ResourceNotFound(str(policy_version_id))

    def get_core_network_change_set(
        self, core_network_id: str, policy_version_id: int,
    ) -> list[dict[str, Any]]:
        if core_network_id not in self.core_networks:
            raise ResourceNotFound(core_network_id)
        return []

    def get_core_network_change_events(
        self, core_network_id: str, policy_version_id: int,
    ) -> list[dict[str, Any]]:
        if core_network_id not in self.core_networks:
            raise ResourceNotFound(core_network_id)
        return []

    # --- Resource Policy ---

    def put_resource_policy(self, resource_arn: str, policy_document: str) -> None:
        self.resource_policies[resource_arn] = policy_document

    def get_resource_policy(self, resource_arn: str) -> Optional[str]:
        return self.resource_policies.get(resource_arn)

    def delete_resource_policy(self, resource_arn: str) -> None:
        self.resource_policies.pop(resource_arn, None)

    # --- Associations ---

    def associate_connect_peer(
        self, global_network_id: str, connect_peer_id: str,
        device_id: str, link_id: Optional[str],
    ) -> ConnectPeerAssociation:
        if global_network_id not in self.global_networks:
            raise ResourceNotFound(global_network_id)
        assoc = ConnectPeerAssociation(
            global_network_id=global_network_id, connect_peer_id=connect_peer_id,
            device_id=device_id, link_id=link_id,
        )
        self.connect_peer_associations[global_network_id][connect_peer_id] = assoc
        return assoc

    def disassociate_connect_peer(
        self, global_network_id: str, connect_peer_id: str,
    ) -> ConnectPeerAssociation:
        if global_network_id not in self.global_networks:
            raise ResourceNotFound(global_network_id)
        assocs = self.connect_peer_associations.get(global_network_id, {})
        if connect_peer_id not in assocs:
            raise ResourceNotFound(connect_peer_id)
        assoc = assocs.pop(connect_peer_id)
        assoc.state = "DELETED"
        return assoc

    @paginate(pagination_model=PAGINATION_MODEL)
    def get_connect_peer_associations(
        self, global_network_id: str, connect_peer_ids: Optional[list[str]],
    ) -> list[ConnectPeerAssociation]:
        if global_network_id not in self.global_networks:
            raise ValidationError("Incorrect input.")
        assocs = self.connect_peer_associations.get(global_network_id, {})
        if connect_peer_ids:
            return [assocs[c] for c in connect_peer_ids if c in assocs]
        return list(assocs.values())

    def associate_customer_gateway(
        self, global_network_id: str, customer_gateway_arn: str,
        device_id: str, link_id: Optional[str],
    ) -> CustomerGatewayAssociation:
        if global_network_id not in self.global_networks:
            raise ResourceNotFound(global_network_id)
        assoc = CustomerGatewayAssociation(
            global_network_id=global_network_id, customer_gateway_arn=customer_gateway_arn,
            device_id=device_id, link_id=link_id,
        )
        self.customer_gateway_associations[global_network_id][customer_gateway_arn] = assoc
        return assoc

    def disassociate_customer_gateway(
        self, global_network_id: str, customer_gateway_arn: str,
    ) -> CustomerGatewayAssociation:
        if global_network_id not in self.global_networks:
            raise ResourceNotFound(global_network_id)
        assocs = self.customer_gateway_associations.get(global_network_id, {})
        if customer_gateway_arn not in assocs:
            raise ResourceNotFound(customer_gateway_arn)
        assoc = assocs.pop(customer_gateway_arn)
        assoc.state = "DELETED"
        return assoc

    @paginate(pagination_model=PAGINATION_MODEL)
    def get_customer_gateway_associations(
        self, global_network_id: str, customer_gateway_arns: Optional[list[str]],
    ) -> list[CustomerGatewayAssociation]:
        if global_network_id not in self.global_networks:
            raise ValidationError("Incorrect input.")
        assocs = self.customer_gateway_associations.get(global_network_id, {})
        if customer_gateway_arns:
            return [assocs[a] for a in customer_gateway_arns if a in assocs]
        return list(assocs.values())

    def associate_link(
        self, global_network_id: str, device_id: str, link_id: str,
    ) -> LinkAssociation:
        if global_network_id not in self.global_networks:
            raise ResourceNotFound(global_network_id)
        assoc = LinkAssociation(
            global_network_id=global_network_id, device_id=device_id, link_id=link_id,
        )
        self.link_associations.setdefault(global_network_id, []).append(assoc)
        return assoc

    def disassociate_link(
        self, global_network_id: str, device_id: str, link_id: str,
    ) -> LinkAssociation:
        if global_network_id not in self.global_networks:
            raise ResourceNotFound(global_network_id)
        assocs = self.link_associations.get(global_network_id, [])
        for i, a in enumerate(assocs):
            if a.device_id == device_id and a.link_id == link_id:
                removed = assocs.pop(i)
                removed.state = "DELETED"
                return removed
        raise ResourceNotFound(f"{device_id}/{link_id}")

    @paginate(pagination_model=PAGINATION_MODEL)
    def get_link_associations(
        self, global_network_id: str, device_id: Optional[str], link_id: Optional[str],
    ) -> list[LinkAssociation]:
        if global_network_id not in self.global_networks:
            raise ValidationError("Incorrect input.")
        result = self.link_associations.get(global_network_id, [])
        if device_id:
            result = [a for a in result if a.device_id == device_id]
        if link_id:
            result = [a for a in result if a.link_id == link_id]
        return result

    def associate_transit_gateway_connect_peer(
        self, global_network_id: str, transit_gateway_connect_peer_arn: str,
        device_id: str, link_id: Optional[str],
    ) -> TransitGatewayConnectPeerAssociation:
        if global_network_id not in self.global_networks:
            raise ResourceNotFound(global_network_id)
        assoc = TransitGatewayConnectPeerAssociation(
            global_network_id=global_network_id,
            transit_gateway_connect_peer_arn=transit_gateway_connect_peer_arn,
            device_id=device_id, link_id=link_id,
        )
        self.transit_gateway_connect_peer_associations[global_network_id][
            transit_gateway_connect_peer_arn
        ] = assoc
        return assoc

    def disassociate_transit_gateway_connect_peer(
        self, global_network_id: str, transit_gateway_connect_peer_arn: str,
    ) -> TransitGatewayConnectPeerAssociation:
        if global_network_id not in self.global_networks:
            raise ResourceNotFound(global_network_id)
        assocs = self.transit_gateway_connect_peer_associations.get(global_network_id, {})
        if transit_gateway_connect_peer_arn not in assocs:
            raise ResourceNotFound(transit_gateway_connect_peer_arn)
        assoc = assocs.pop(transit_gateway_connect_peer_arn)
        assoc.state = "DELETED"
        return assoc

    @paginate(pagination_model=PAGINATION_MODEL)
    def get_transit_gateway_connect_peer_associations(
        self, global_network_id: str, transit_gateway_connect_peer_arns: Optional[list[str]],
    ) -> list[TransitGatewayConnectPeerAssociation]:
        if global_network_id not in self.global_networks:
            raise ValidationError("Incorrect input.")
        assocs = self.transit_gateway_connect_peer_associations.get(global_network_id, {})
        if transit_gateway_connect_peer_arns:
            return [assocs[a] for a in transit_gateway_connect_peer_arns if a in assocs]
        return list(assocs.values())

    # --- Transit Gateway Registration ---

    def register_transit_gateway(
        self, global_network_id: str, transit_gateway_arn: str,
    ) -> TransitGatewayRegistration:
        if global_network_id not in self.global_networks:
            raise ResourceNotFound(global_network_id)
        reg = TransitGatewayRegistration(
            global_network_id=global_network_id, transit_gateway_arn=transit_gateway_arn,
        )
        self.transit_gateway_registrations.setdefault(global_network_id, {})[
            transit_gateway_arn
        ] = reg
        return reg

    def deregister_transit_gateway(
        self, global_network_id: str, transit_gateway_arn: str,
    ) -> TransitGatewayRegistration:
        if global_network_id not in self.global_networks:
            raise ResourceNotFound(global_network_id)
        regs = self.transit_gateway_registrations.get(global_network_id, {})
        if transit_gateway_arn not in regs:
            raise ResourceNotFound(transit_gateway_arn)
        reg = regs.pop(transit_gateway_arn)
        reg.state = {"Code": "DELETING", "Message": ""}
        return reg

    @paginate(pagination_model=PAGINATION_MODEL)
    def get_transit_gateway_registrations(
        self, global_network_id: str, transit_gateway_arns: Optional[list[str]],
    ) -> list[TransitGatewayRegistration]:
        if global_network_id not in self.global_networks:
            raise ValidationError("Incorrect input.")
        regs = self.transit_gateway_registrations.get(global_network_id, {})
        if transit_gateway_arns:
            return [regs[a] for a in transit_gateway_arns if a in regs]
        return list(regs.values())

    # --- Route Analysis ---

    def start_route_analysis(
        self, global_network_id: str, source: Optional[dict[str, Any]],
        destination: Optional[dict[str, Any]], include_return_path: bool, use_middleboxes: bool,
    ) -> RouteAnalysis:
        if global_network_id not in self.global_networks:
            raise ResourceNotFound(global_network_id)
        ra = RouteAnalysis(
            account_id=self.account_id, global_network_id=global_network_id,
            source=source, destination=destination,
            include_return_path=include_return_path, use_middleboxes=use_middleboxes,
        )
        self.route_analyses.setdefault(global_network_id, {})[ra.route_analysis_id] = ra
        return ra

    def get_route_analysis(
        self, global_network_id: str, route_analysis_id: str,
    ) -> RouteAnalysis:
        if global_network_id not in self.global_networks:
            raise ResourceNotFound(global_network_id)
        ras = self.route_analyses.get(global_network_id, {})
        if route_analysis_id not in ras:
            raise ResourceNotFound(route_analysis_id)
        return ras[route_analysis_id]

    # --- Network Resource stubs ---

    def get_network_resources(self, global_network_id: str) -> list[dict[str, Any]]:
        if global_network_id not in self.global_networks:
            raise ResourceNotFound(global_network_id)
        return []

    def get_network_resource_relationships(self, global_network_id: str) -> list[dict[str, Any]]:
        if global_network_id not in self.global_networks:
            raise ResourceNotFound(global_network_id)
        return []

    def get_network_resource_counts(self, global_network_id: str) -> list[dict[str, Any]]:
        if global_network_id not in self.global_networks:
            raise ResourceNotFound(global_network_id)
        return []

    def get_network_routes(
        self, global_network_id: str, route_table_identifier: Optional[dict[str, Any]],
    ) -> dict[str, Any]:
        if global_network_id not in self.global_networks:
            raise ResourceNotFound(global_network_id)
        return {
            "RouteTableArn": (route_table_identifier or {}).get("TransitGatewayRouteTableArn", ""),
            "CoreNetworkSegmentEdge": (route_table_identifier or {}).get("CoreNetworkSegmentEdge"),
            "RouteTableType": "TRANSIT_GATEWAY_ROUTE_TABLE",
            "RouteTableTimestamp": _now(),
            "NetworkRoutes": [],
        }

    def get_network_telemetry(self, global_network_id: str) -> list[dict[str, Any]]:
        if global_network_id not in self.global_networks:
            raise ResourceNotFound(global_network_id)
        return []

    def update_network_resource_metadata(
        self, global_network_id: str, resource_arn: str, metadata: dict[str, str],
    ) -> dict[str, Any]:
        if global_network_id not in self.global_networks:
            raise ResourceNotFound(global_network_id)
        return {"ResourceArn": resource_arn, "Metadata": metadata}

    # --- Core Network Prefix List Association ---

    def create_core_network_prefix_list_association(
        self, core_network_id: Optional[str], prefix_list: Optional[str],
        segment_name: Optional[str],
    ) -> CoreNetworkPrefixListAssociation:
        if core_network_id and core_network_id not in self.core_networks:
            raise ResourceNotFound(core_network_id)
        assoc = CoreNetworkPrefixListAssociation(
            core_network_id=core_network_id or "", prefix_list=prefix_list or "",
            segment_name=segment_name,
        )
        self.core_network_prefix_list_associations.setdefault(core_network_id or "", []).append(assoc)
        return assoc

    def delete_core_network_prefix_list_association(
        self, core_network_id: str, prefix_list_arn: str,
    ) -> CoreNetworkPrefixListAssociation:
        assocs = self.core_network_prefix_list_associations.get(core_network_id, [])
        for i, a in enumerate(assocs):
            if a.prefix_list == prefix_list_arn:
                return assocs.pop(i)
        raise ResourceNotFound(prefix_list_arn)

    def list_core_network_prefix_list_associations(
        self, core_network_id: str,
    ) -> list[CoreNetworkPrefixListAssociation]:
        if core_network_id not in self.core_networks:
            raise ResourceNotFound(core_network_id)
        return self.core_network_prefix_list_associations.get(core_network_id, [])

    # --- Routing Policy Label ---

    def put_attachment_routing_policy_label(
        self, attachment_id: str, label: str,
    ) -> dict[str, Any]:
        if attachment_id not in self.attachments:
            raise ResourceNotFound(attachment_id)
        att = self.attachments[attachment_id]
        cn_id = att.core_network_id or ""
        self.routing_policy_labels.setdefault(cn_id, {})[attachment_id] = label
        att.routing_policy_label = label
        return {"AttachmentId": attachment_id, "Label": label}

    def remove_attachment_routing_policy_label(
        self, core_network_id: str, attachment_id: str,
    ) -> dict[str, Any]:
        labels = self.routing_policy_labels.get(core_network_id, {})
        labels.pop(attachment_id, None)
        if attachment_id in self.attachments:
            self.attachments[attachment_id].routing_policy_label = None
        return {"AttachmentId": attachment_id}

    def list_attachment_routing_policy_associations(
        self, core_network_id: str,
    ) -> list[dict[str, Any]]:
        if core_network_id not in self.core_networks:
            raise ResourceNotFound(core_network_id)
        labels = self.routing_policy_labels.get(core_network_id, {})
        return [{"AttachmentId": aid, "Label": label} for aid, label in labels.items()]

    # --- Core Network Routing Information ---

    def list_core_network_routing_information(
        self, core_network_id: str,
    ) -> list[dict[str, Any]]:
        if core_network_id not in self.core_networks:
            raise ResourceNotFound(core_network_id)
        return []

    # --- Organization Service Access ---

    def start_organization_service_access_update(self, action: str) -> dict[str, Any]:
        self.organization_service_access = action
        return {
            "OrganizationStatus": {
                "OrganizationId": "o-" + "".join(mock_random.get_random_hex(10)),
                "OrganizationAwsServiceAccessStatus": "ENABLED" if action == "ENABLE" else "DISABLED",
                "SLRDeploymentStatus": "SUCCEEDED",
                "AccountStatusList": [],
            }
        }

    def list_organization_service_access_status(self) -> dict[str, Any]:
        return {
            "OrganizationStatus": {
                "OrganizationId": "o-" + "".join(mock_random.get_random_hex(10)),
                "OrganizationAwsServiceAccessStatus": "ENABLED"
                if self.organization_service_access == "ENABLE" else "DISABLED",
                "SLRDeploymentStatus": "SUCCEEDED",
                "AccountStatusList": [],
            }
        }


networkmanager_backends = BackendDict(
    NetworkManagerBackend,
    "networkmanager",
    use_boto3_regions=False,
    additional_regions=PARTITION_NAMES,
)
