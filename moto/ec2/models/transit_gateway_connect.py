from typing import Any, Optional

from moto.core.utils import iso_8601_datetime_with_milliseconds, utcnow

from ..utils import (
    random_transit_gateway_attachment_id,
    random_transit_gateway_connect_peer_id,
)
from .core import TaggedEC2Resource


class TransitGatewayConnect(TaggedEC2Resource):
    def __init__(
        self,
        backend: Any,
        transport_transit_gateway_attachment_id: str,
        transit_gateway_id: str,
        options: Optional[dict[str, str]] = None,
        tags: Optional[dict[str, str]] = None,
    ):
        self.ec2_backend = backend
        self.id = random_transit_gateway_attachment_id()
        self.transport_transit_gateway_attachment_id = (
            transport_transit_gateway_attachment_id
        )
        self.transit_gateway_id = transit_gateway_id
        self.options = options or {"Protocol": "gre"}
        self.state = "available"
        self._created_at = utcnow()
        self.add_tags(tags or {})

    @property
    def creation_time(self) -> str:
        return iso_8601_datetime_with_milliseconds(self._created_at)

    @property
    def owner_id(self) -> str:
        return self.ec2_backend.account_id


class TransitGatewayConnectPeer(TaggedEC2Resource):
    def __init__(
        self,
        backend: Any,
        transit_gateway_attachment_id: str,
        transit_gateway_address: Optional[str],
        peer_address: str,
        bgp_options: Optional[dict[str, str]] = None,
        inside_cidr_blocks: Optional[list[str]] = None,
        tags: Optional[dict[str, str]] = None,
    ):
        self.ec2_backend = backend
        self.id = random_transit_gateway_connect_peer_id()
        self.transit_gateway_attachment_id = transit_gateway_attachment_id
        self.transit_gateway_address = transit_gateway_address or "10.0.0.1"
        self.peer_address = peer_address
        self.bgp_options = bgp_options or {"PeerAsn": "65000"}
        self.inside_cidr_blocks = inside_cidr_blocks or []
        self.state = "available"
        self._created_at = utcnow()
        self.add_tags(tags or {})

    @property
    def creation_time(self) -> str:
        return iso_8601_datetime_with_milliseconds(self._created_at)


class TransitGatewayConnectBackend:
    def __init__(self) -> None:
        self.transit_gateway_connects: dict[str, TransitGatewayConnect] = {}
        self.transit_gateway_connect_peers: dict[str, TransitGatewayConnectPeer] = {}

    def create_transit_gateway_connect(
        self,
        transport_transit_gateway_attachment_id: str,
        options: Optional[dict[str, str]] = None,
        tags: Optional[dict[str, str]] = None,
    ) -> TransitGatewayConnect:
        # Look up the transport attachment to get the transit gateway ID
        attachment = self.transit_gateway_attachments.get(  # type: ignore[attr-defined]
            transport_transit_gateway_attachment_id
        )
        transit_gateway_id = attachment.transit_gateway_id if attachment else "tgw-unknown"

        connect = TransitGatewayConnect(
            self,
            transport_transit_gateway_attachment_id=transport_transit_gateway_attachment_id,
            transit_gateway_id=transit_gateway_id,
            options=options,
            tags=tags,
        )
        self.transit_gateway_connects[connect.id] = connect
        return connect

    def delete_transit_gateway_connect(
        self, transit_gateway_attachment_id: str
    ) -> TransitGatewayConnect:
        connect = self.transit_gateway_connects.get(transit_gateway_attachment_id)
        if not connect:
            from ..exceptions import InvalidTransitGatewayAttachmentIdError

            raise InvalidTransitGatewayAttachmentIdError(transit_gateway_attachment_id)
        connect.state = "deleted"
        return self.transit_gateway_connects.pop(transit_gateway_attachment_id)

    def describe_transit_gateway_connects(
        self,
        transit_gateway_attachment_ids: Optional[list[str]] = None,
        filters: Any = None,
    ) -> list[TransitGatewayConnect]:
        connects = list(self.transit_gateway_connects.values())
        if transit_gateway_attachment_ids:
            connects = [c for c in connects if c.id in transit_gateway_attachment_ids]
        return connects

    def create_transit_gateway_connect_peer(
        self,
        transit_gateway_attachment_id: str,
        transit_gateway_address: Optional[str] = None,
        peer_address: str = "",
        bgp_options: Optional[dict[str, str]] = None,
        inside_cidr_blocks: Optional[list[str]] = None,
        tags: Optional[dict[str, str]] = None,
    ) -> TransitGatewayConnectPeer:
        peer = TransitGatewayConnectPeer(
            self,
            transit_gateway_attachment_id=transit_gateway_attachment_id,
            transit_gateway_address=transit_gateway_address,
            peer_address=peer_address,
            bgp_options=bgp_options,
            inside_cidr_blocks=inside_cidr_blocks,
            tags=tags,
        )
        self.transit_gateway_connect_peers[peer.id] = peer
        return peer

    def delete_transit_gateway_connect_peer(
        self, transit_gateway_connect_peer_id: str
    ) -> TransitGatewayConnectPeer:
        peer = self.transit_gateway_connect_peers.get(transit_gateway_connect_peer_id)
        if not peer:
            from ..exceptions import EC2ClientError

            raise EC2ClientError(
                "InvalidTransitGatewayConnectPeerId.NotFound",
                f"The transitGatewayConnectPeer ID '{transit_gateway_connect_peer_id}' does not exist",
            )
        peer.state = "deleted"
        return self.transit_gateway_connect_peers.pop(transit_gateway_connect_peer_id)

    def describe_transit_gateway_connect_peers(
        self,
        transit_gateway_connect_peer_ids: Optional[list[str]] = None,
        filters: Any = None,
    ) -> list[TransitGatewayConnectPeer]:
        peers = list(self.transit_gateway_connect_peers.values())
        if transit_gateway_connect_peer_ids:
            peers = [p for p in peers if p.id in transit_gateway_connect_peer_ids]
        return peers

    def create_transit_gateway_prefix_list_reference(
        self,
        transit_gateway_route_table_id: str,
        prefix_list_id: str,
        transit_gateway_attachment_id: Optional[str] = None,
        blackhole: bool = False,
    ) -> dict[str, Any]:
        route_table = self.transit_gateways_route_tables.get(  # type: ignore[attr-defined]
            transit_gateway_route_table_id
        )
        ref: dict[str, Any] = {
            "prefixListId": prefix_list_id,
            "transitGatewayRouteTableId": transit_gateway_route_table_id,
            "state": "available",
            "blackhole": blackhole,
        }
        if transit_gateway_attachment_id and not blackhole:
            attachment = self.transit_gateway_attachments.get(  # type: ignore[attr-defined]
                transit_gateway_attachment_id
            )
            if attachment:
                ref["transitGatewayAttachment"] = {
                    "transitGatewayAttachmentId": transit_gateway_attachment_id,
                    "resourceType": attachment.resource_type,
                    "resourceId": attachment.resource_id,
                }
        if route_table:
            if not hasattr(route_table, "prefix_list_references"):
                route_table.prefix_list_references = {}
            route_table.prefix_list_references[prefix_list_id] = ref
        return ref

    def delete_transit_gateway_prefix_list_reference(
        self,
        transit_gateway_route_table_id: str,
        prefix_list_id: str,
    ) -> dict[str, Any]:
        route_table = self.transit_gateways_route_tables.get(  # type: ignore[attr-defined]
            transit_gateway_route_table_id
        )
        ref = {"prefixListId": prefix_list_id, "state": "deleted"}
        if route_table and hasattr(route_table, "prefix_list_references"):
            ref = route_table.prefix_list_references.pop(prefix_list_id, ref)
            ref["state"] = "deleted"
        return ref

    def get_transit_gateway_prefix_list_references(
        self,
        transit_gateway_route_table_id: str,
        filters: Any = None,
    ) -> list[dict[str, Any]]:
        route_table = self.transit_gateways_route_tables.get(  # type: ignore[attr-defined]
            transit_gateway_route_table_id
        )
        if not route_table or not hasattr(route_table, "prefix_list_references"):
            return []
        return list(route_table.prefix_list_references.values())
