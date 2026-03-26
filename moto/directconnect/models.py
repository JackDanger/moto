"""DirectConnectBackend class with methods for supported APIs."""

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional

from moto.core.base_backend import BackendDict, BaseBackend
from moto.core.common_models import BaseModel
from moto.utilities.tagging_service import TaggingService

from .enums import (
    ConnectionStateType,
    EncryptionModeType,
    LagStateType,
    MacSecKeyStateType,
    PortEncryptionStatusType,
)
from .exceptions import (
    ConnectionIdMissing,
    ConnectionNotFound,
    DirectConnectClientError,
    InterconnectNotFound,
    LAGNotFound,
    MacSecKeyNotFound,
    VirtualGatewayNotFound,
    VirtualInterfaceNotFound,
)


@dataclass
class MacSecKey(BaseModel):
    secret_arn: Optional[str]
    ckn: Optional[str]
    state: MacSecKeyStateType
    start_on: str
    cak: Optional[str] = None

    def to_dict(self) -> dict[str, str]:
        return {
            "secretARN": self.secret_arn or "",
            "ckn": self.ckn or "",
            "state": self.state,
            "startOn": self.start_on,
        }


@dataclass
class BGPPeer(BaseModel):
    asn: int
    auth_key: Optional[str]
    address_family: str
    amazon_address: Optional[str]
    customer_address: Optional[str]
    bgp_peer_state: str = "available"
    bgp_status: str = "up"
    aws_device_v2: str = "mock_device_v2"
    bgp_peer_id: str = field(default="", init=False)

    def __post_init__(self) -> None:
        if not self.bgp_peer_id:
            self.bgp_peer_id = f"dxpeer-{uuid.uuid4().hex[:8]}"

    def to_dict(self) -> dict[str, Any]:
        return {
            "asn": self.asn,
            "authKey": self.auth_key,
            "addressFamily": self.address_family,
            "amazonAddress": self.amazon_address,
            "customerAddress": self.customer_address,
            "bgpPeerState": self.bgp_peer_state,
            "bgpStatus": self.bgp_status,
            "awsDeviceV2": self.aws_device_v2,
            "bgpPeerId": self.bgp_peer_id,
        }


@dataclass
class VirtualInterface(BaseModel):
    connection_id: str
    virtual_interface_type: str
    virtual_interface_name: str
    vlan: int
    asn: int
    auth_key: Optional[str]
    amazon_address: Optional[str]
    customer_address: Optional[str]
    address_family: Optional[str]
    virtual_gateway_id: Optional[str]
    direct_connect_gateway_id: Optional[str]
    route_filter_prefixes: list[dict[str, str]]
    bgp_peers: list[BGPPeer]
    tags: Optional[list[dict[str, str]]]
    owner_account: str
    region: str
    backend: "DirectConnectBackend"
    virtual_interface_id: str = field(default="", init=False)
    virtual_interface_state: str = "available"
    mtu: int = 1500
    jumbo_frame_capable: bool = False

    def __post_init__(self) -> None:
        if not self.virtual_interface_id:
            self.virtual_interface_id = f"dxvif-{uuid.uuid4().hex[:8]}"

    def to_dict(self) -> dict[str, Any]:
        return {
            "ownerAccount": self.owner_account,
            "virtualInterfaceId": self.virtual_interface_id,
            "location": "mock_location",
            "connectionId": self.connection_id,
            "virtualInterfaceType": self.virtual_interface_type,
            "virtualInterfaceName": self.virtual_interface_name,
            "vlan": self.vlan,
            "asn": self.asn,
            "authKey": self.auth_key,
            "amazonAddress": self.amazon_address,
            "customerAddress": self.customer_address,
            "addressFamily": self.address_family,
            "virtualInterfaceState": self.virtual_interface_state,
            "customerRouterConfig": "",
            "mtu": self.mtu,
            "jumboFrameCapable": self.jumbo_frame_capable,
            "virtualGatewayId": self.virtual_gateway_id,
            "directConnectGatewayId": self.direct_connect_gateway_id,
            "routeFilterPrefixes": self.route_filter_prefixes,
            "bgpPeers": [p.to_dict() for p in self.bgp_peers],
            "region": self.region,
            "awsDeviceV2": "mock_device_v2",
            "awsLogicalDeviceId": "mock_logical_device_id",
            "tags": self.backend.list_tags_for_resource(self.virtual_interface_id),
        }


@dataclass
class DirectConnectGateway(BaseModel):
    direct_connect_gateway_name: str
    amazon_side_asn: int
    owner_account: str
    direct_connect_gateway_id: str = field(default="", init=False)
    direct_connect_gateway_state: str = "available"

    def __post_init__(self) -> None:
        if not self.direct_connect_gateway_id:
            self.direct_connect_gateway_id = str(uuid.uuid4())

    def to_dict(self) -> dict[str, Any]:
        return {
            "directConnectGatewayId": self.direct_connect_gateway_id,
            "directConnectGatewayName": self.direct_connect_gateway_name,
            "amazonSideAsn": self.amazon_side_asn,
            "ownerAccount": self.owner_account,
            "directConnectGatewayState": self.direct_connect_gateway_state,
            "stateChangeError": "",
        }


@dataclass
class DirectConnectGatewayAssociation(BaseModel):
    direct_connect_gateway_id: str
    direct_connect_gateway_owner_account: str
    associated_gateway_id: str
    associated_gateway_type: str
    associated_gateway_owner_account: str
    allowed_prefixes_to_direct_connect_gateway: list[dict[str, str]]
    association_id: str = field(default="", init=False)
    association_state: str = "associated"

    def __post_init__(self) -> None:
        if not self.association_id:
            self.association_id = str(uuid.uuid4())

    def to_dict(self) -> dict[str, Any]:
        return {
            "directConnectGatewayId": self.direct_connect_gateway_id,
            "directConnectGatewayOwnerAccount": self.direct_connect_gateway_owner_account,
            "associationState": self.association_state,
            "stateChangeError": "",
            "associatedGateway": {
                "id": self.associated_gateway_id,
                "type": self.associated_gateway_type,
                "ownerAccount": self.associated_gateway_owner_account,
                "region": "us-east-1",
            },
            "associationId": self.association_id,
            "allowedPrefixesToDirectConnectGateway": self.allowed_prefixes_to_direct_connect_gateway,
        }


@dataclass
class DirectConnectGatewayAssociationProposal(BaseModel):
    direct_connect_gateway_id: str
    direct_connect_gateway_owner_account: str
    gateway_id: str
    add_allowed_prefixes: list[dict[str, str]]
    remove_allowed_prefixes: list[dict[str, str]]
    proposal_id: str = field(default="", init=False)
    proposal_state: str = "requested"

    def __post_init__(self) -> None:
        if not self.proposal_id:
            self.proposal_id = str(uuid.uuid4())

    def to_dict(self) -> dict[str, Any]:
        return {
            "proposalId": self.proposal_id,
            "directConnectGatewayId": self.direct_connect_gateway_id,
            "directConnectGatewayOwnerAccount": self.direct_connect_gateway_owner_account,
            "proposalState": self.proposal_state,
            "associatedGateway": {
                "id": self.gateway_id,
                "type": "virtualPrivateGateway",
                "ownerAccount": self.direct_connect_gateway_owner_account,
                "region": "us-east-1",
            },
            "existingAllowedPrefixesToDirectConnectGateway": [],
            "requestedAllowedPrefixesToDirectConnectGateway": self.add_allowed_prefixes,
        }


@dataclass
class Interconnect(BaseModel):
    interconnect_name: str
    bandwidth: str
    location: str
    lag_id: Optional[str]
    provider_name: Optional[str]
    tags: Optional[list[dict[str, str]]]
    owner_account: str
    region: str
    backend: "DirectConnectBackend"
    interconnect_id: str = field(default="", init=False)
    interconnect_state: str = "available"

    def __post_init__(self) -> None:
        if not self.interconnect_id:
            self.interconnect_id = f"dxcon-{uuid.uuid4().hex[:8]}"

    def to_dict(self) -> dict[str, Any]:
        return {
            "interconnectId": self.interconnect_id,
            "interconnectName": self.interconnect_name,
            "interconnectState": self.interconnect_state,
            "region": self.region,
            "location": self.location,
            "bandwidth": self.bandwidth,
            "loaIssueTime": datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
            "lagId": self.lag_id,
            "awsDevice": "mock_device",
            "jumboFrameCapable": False,
            "awsDeviceV2": "mock_device_v2",
            "awsLogicalDeviceId": "mock_logical_device_id",
            "hasLogicalRedundancy": False,
            "tags": self.backend.list_tags_for_resource(self.interconnect_id),
            "providerName": self.provider_name,
        }


@dataclass
class VirtualGateway(BaseModel):
    virtual_gateway_id: str
    virtual_gateway_state: str = "available"

    def to_dict(self) -> dict[str, Any]:
        return {
            "virtualGatewayId": self.virtual_gateway_id,
            "virtualGatewayState": self.virtual_gateway_state,
        }


@dataclass
class Connection(BaseModel):
    aws_device_v2: str
    aws_device: str
    aws_logical_device_id: str
    bandwidth: str
    connection_name: str
    connection_state: ConnectionStateType
    encryption_mode: EncryptionModeType
    has_logical_redundancy: bool
    jumbo_frame_capable: bool
    lag_id: Optional[str]
    loa_issue_time: str
    location: str
    mac_sec_capable: Optional[bool]
    mac_sec_keys: list[MacSecKey]
    owner_account: str
    partner_name: str
    port_encryption_status: PortEncryptionStatusType
    provider_name: Optional[str]
    region: str
    tags: Optional[list[dict[str, str]]]
    vlan: int
    connection_id: str = field(default="", init=False)
    backend: "DirectConnectBackend"

    def __post_init__(self) -> None:
        if self.connection_id == "":
            self.connection_id = f"arn:aws:directconnect:{self.region}:{self.owner_account}:dx-con/dx-moto-{self.connection_name}-{datetime.now().strftime('%Y%m%d%H%M%S')}"

    def to_dict(self) -> dict[str, Any]:
        return {
            "awsDevice": self.aws_device,
            "awsDeviceV2": self.aws_device_v2,
            "awsLogicalDeviceId": self.aws_logical_device_id,
            "bandwidth": self.bandwidth,
            "connectionId": self.connection_id,
            "connectionName": self.connection_name,
            "connectionState": self.connection_state,
            "encryptionMode": self.encryption_mode,
            "hasLogicalRedundancy": self.has_logical_redundancy,
            "jumboFrameCapable": self.jumbo_frame_capable,
            "lagId": self.lag_id,
            "loaIssueTime": self.loa_issue_time,
            "location": self.location,
            "macSecCapable": self.mac_sec_capable,
            "macSecKeys": [key.to_dict() for key in self.mac_sec_keys],
            "partnerName": self.partner_name,
            "portEncryptionStatus": self.port_encryption_status,
            "providerName": self.provider_name,
            "region": self.region,
            "tags": self.backend.list_tags_for_resource(self.connection_id),
            "vlan": self.vlan,
        }


@dataclass
class LAG(BaseModel):
    aws_device_v2: str
    aws_device: str
    aws_logical_device_id: str
    connections_bandwidth: str
    number_of_connections: int
    minimum_links: int
    connections: list[Connection]
    lag_name: str
    lag_state: LagStateType
    encryption_mode: EncryptionModeType
    has_logical_redundancy: bool
    jumbo_frame_capable: bool
    location: str
    mac_sec_capable: Optional[bool]
    mac_sec_keys: list[MacSecKey]
    owner_account: str
    provider_name: Optional[str]
    region: str
    tags: Optional[list[dict[str, str]]]
    lag_id: str = field(default="", init=False)
    backend: "DirectConnectBackend"

    def __post_init__(self) -> None:
        if self.lag_id == "":
            self.lag_id = f"arn:aws:directconnect:{self.region}:{self.owner_account}:dxlag/dxlag-moto-{self.lag_name}-{datetime.now().strftime('%Y%m%d%H%M%S')}"

    def to_dict(self) -> dict[str, Any]:
        return {
            "awsDevice": self.aws_device,
            "awsDeviceV2": self.aws_device_v2,
            "awsLogicalDeviceId": self.aws_logical_device_id,
            "connectionsBandwidth": self.connections_bandwidth,
            "numberOfConnections": self.number_of_connections,
            "minimumLinks": self.minimum_links,
            "connections": [conn.to_dict() for conn in self.connections],
            "lagId": self.lag_id,
            "lagName": self.lag_name,
            "lagState": self.lag_state,
            "encryptionMode": self.encryption_mode,
            "hasLogicalRedundancy": self.has_logical_redundancy,
            "jumboFrameCapable": self.jumbo_frame_capable,
            "location": self.location,
            "macSecCapable": self.mac_sec_capable,
            "macSecKeys": [key.to_dict() for key in self.mac_sec_keys],
            "providerName": self.provider_name,
            "region": self.region,
            "tags": self.backend.list_tags_for_resource(self.lag_id),
        }


class DirectConnectBackend(BaseBackend):
    """Implementation of DirectConnect APIs."""

    def __init__(self, region_name: str, account_id: str) -> None:
        super().__init__(region_name, account_id)
        self.connections: dict[str, Connection] = {}
        self.lags: dict[str, LAG] = {}
        self.virtual_interfaces: dict[str, VirtualInterface] = {}
        self.direct_connect_gateways: dict[str, DirectConnectGateway] = {}
        self.gateway_associations: dict[str, DirectConnectGatewayAssociation] = {}
        self.gateway_association_proposals: dict[str, DirectConnectGatewayAssociationProposal] = {}
        self.interconnects: dict[str, Interconnect] = {}
        self.virtual_gateways: dict[str, VirtualGateway] = {}
        self.tagger = TaggingService(key_name="key", value_name="value")

    def describe_connections(self, connection_id: Optional[str]) -> list[Connection]:
        if connection_id and connection_id not in self.connections:
            raise ConnectionNotFound(connection_id, self.region_name)
        if connection_id:
            connection = self.connections.get(connection_id)
            return [] if not connection else [connection]
        return list(self.connections.values())

    def create_connection(
        self,
        location: str,
        bandwidth: str,
        connection_name: str,
        lag_id: Optional[str],
        tags: Optional[list[dict[str, str]]],
        provider_name: Optional[str],
        request_mac_sec: Optional[bool],
    ) -> Connection:
        encryption_mode = EncryptionModeType.NO
        mac_sec_keys = []
        if request_mac_sec:
            encryption_mode = EncryptionModeType.MUST
            mac_sec_keys = [
                MacSecKey(
                    secret_arn="mock_secret_arn",
                    ckn="mock_ckn",
                    state=MacSecKeyStateType.ASSOCIATED,
                    start_on=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                )
            ]
        connection = Connection(
            aws_device_v2="mock_device_v2",
            aws_device="mock_device",
            aws_logical_device_id="mock_logical_device_id",
            bandwidth=bandwidth,
            connection_name=connection_name,
            connection_state=ConnectionStateType.AVAILABLE,
            encryption_mode=encryption_mode,
            has_logical_redundancy=False,
            jumbo_frame_capable=False,
            lag_id=lag_id,
            loa_issue_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            location=location,
            mac_sec_capable=request_mac_sec,
            mac_sec_keys=mac_sec_keys,
            owner_account=self.account_id,
            partner_name="mock_partner",
            port_encryption_status=PortEncryptionStatusType.DOWN,
            provider_name=provider_name,
            region=self.region_name,
            tags=tags,
            vlan=0,
            backend=self,
        )
        if tags:
            self.tag_resource(connection.connection_id, tags)
        self.connections[connection.connection_id] = connection
        return connection

    def confirm_connection(self, connection_id: str) -> Connection:
        if not connection_id:
            raise ConnectionIdMissing()
        connection = self.connections.get(connection_id)
        if not connection:
            raise ConnectionNotFound(connection_id, self.region_name)
        connection.connection_state = ConnectionStateType.AVAILABLE
        return connection

    def describe_hosted_connections(self, connection_id: str) -> list[Connection]:
        return [c for c in self.connections.values() if c.lag_id == connection_id]

    def describe_connection_loa(
        self,
        connection_id: str,
        provider_name: Optional[str],
        loa_content_type: Optional[str],
    ) -> dict[str, Any]:
        if connection_id not in self.connections:
            raise ConnectionNotFound(connection_id, self.region_name)
        return {
            "loa": {
                "loaContent": "bW9ja19sb2FfY29udGVudA==",
                "loaContentType": loa_content_type or "application/pdf",
            }
        }

    def tag_resource(self, resource_arn: str, tags: list[dict[str, str]]) -> None:
        self.tagger.tag_resource(
            resource_arn,
            tags=tags if tags else [],
        )

    def list_tags_for_resource(self, resource_arn: str) -> list[dict[str, str]]:
        tags = self.tagger.get_tag_dict_for_resource(resource_arn)
        if not tags:
            return []
        return [{"key": k, "value": v} for (k, v) in tags.items()]

    def list_tags_for_resources(self, resource_arns: list[str]) -> dict[str, list[Any]]:
        response: dict[str, list[Any]] = {"resourceTags": []}
        for resource_arn in resource_arns:
            response["resourceTags"].append(
                {
                    "resourceArn": resource_arn,
                    "tags": self.list_tags_for_resource(resource_arn),
                }
            )
        return response

    def untag_resource(self, resource_arn: str, tag_keys: list[str]) -> None:
        self.tagger.untag_resource_using_names(resource_arn, tag_keys)

    def delete_connection(self, connection_id: str) -> Connection:
        if not connection_id:
            raise ConnectionIdMissing()
        connection = self.connections.get(connection_id)
        if connection:
            self.connections[connection_id].connection_state = ConnectionStateType.DELETED
            return connection
        raise ConnectionNotFound(connection_id, self.region_name)

    def update_connection(
        self,
        connection_id: str,
        new_connection_name: Optional[str],
        new_encryption_mode: Optional[EncryptionModeType],
    ) -> Connection:
        if not connection_id:
            raise ConnectionIdMissing()
        connection = self.connections.get(connection_id)
        if connection:
            if new_connection_name:
                self.connections[connection_id].connection_name = new_connection_name
            if new_encryption_mode:
                self.connections[connection_id].encryption_mode = new_encryption_mode
            return connection
        raise ConnectionNotFound(connection_id, self.region_name)

    def associate_mac_sec_key(
        self,
        connection_id: str,
        secret_arn: Optional[str],
        ckn: Optional[str],
        cak: Optional[str],
    ) -> tuple[str, list[MacSecKey]]:
        mac_sec_key = MacSecKey(
            secret_arn=secret_arn or "mock_secret_arn",
            ckn=ckn,
            cak=cak,
            state=MacSecKeyStateType.ASSOCIATED,
            start_on=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        )
        if "dxlag-" in connection_id:
            return self._associate_mac_sec_key_with_lag(
                lag_id=connection_id, mac_sec_key=mac_sec_key
            )
        return self._associate_mac_sec_key_with_connection(
            connection_id=connection_id, mac_sec_key=mac_sec_key
        )

    def _associate_mac_sec_key_with_lag(
        self, lag_id: str, mac_sec_key: MacSecKey
    ) -> tuple[str, list[MacSecKey]]:
        lag = self.lags.get(lag_id) or None
        if not lag:
            raise LAGNotFound(lag_id, self.region_name)
        lag.mac_sec_keys.append(mac_sec_key)
        for connection in lag.connections:
            connection.mac_sec_keys = lag.mac_sec_keys
        return lag_id, lag.mac_sec_keys

    def _associate_mac_sec_key_with_connection(
        self, connection_id: str, mac_sec_key: MacSecKey
    ) -> tuple[str, list[MacSecKey]]:
        connection = self.connections.get(connection_id) or None
        if not connection:
            raise ConnectionNotFound(connection_id, self.region_name)
        self.connections[connection_id].mac_sec_keys.append(mac_sec_key)
        return connection_id, self.connections[connection_id].mac_sec_keys

    def create_lag(
        self,
        number_of_connections: int,
        location: str,
        connections_bandwidth: str,
        lag_name: str,
        connection_id: Optional[str],
        tags: Optional[list[dict[str, str]]],
        child_connection_tags: Optional[list[dict[str, str]]],
        provider_name: Optional[str],
        request_mac_sec: Optional[bool],
    ) -> LAG:
        if connection_id:
            raise NotImplementedError(
                "creating a lag with a connection_id is not currently supported by moto"
            )
        encryption_mode = EncryptionModeType.NO
        mac_sec_keys = []
        if request_mac_sec:
            encryption_mode = EncryptionModeType.MUST
            mac_sec_keys = [
                MacSecKey(
                    secret_arn="mock_secret_arn",
                    ckn="mock_ckn",
                    state=MacSecKeyStateType.ASSOCIATED,
                    start_on=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                )
            ]
        lag = LAG(
            aws_device_v2="mock_device_v2",
            aws_device="mock_device",
            aws_logical_device_id="mock_logical_device_id",
            connections_bandwidth=connections_bandwidth,
            lag_name=lag_name,
            lag_state=LagStateType.AVAILABLE,
            minimum_links=0,
            encryption_mode=encryption_mode,
            has_logical_redundancy=False,
            jumbo_frame_capable=False,
            number_of_connections=number_of_connections,
            connections=[],
            location=location,
            mac_sec_capable=request_mac_sec,
            mac_sec_keys=mac_sec_keys,
            owner_account=self.account_id,
            provider_name=provider_name,
            region=self.region_name,
            tags=tags,
            backend=self,
        )
        for i in range(number_of_connections):
            connection = self.create_connection(
                location=location,
                bandwidth=connections_bandwidth,
                connection_name=f"Requested Connection {i + 1} for Lag {lag.lag_id}",
                lag_id=lag.lag_id,
                tags=child_connection_tags,
                request_mac_sec=False,
                provider_name=provider_name,
            )
            if request_mac_sec:
                connection.mac_sec_capable = True
                connection.mac_sec_keys = mac_sec_keys
                connection.encryption_mode = encryption_mode
            lag.connections.append(connection)
        if tags:
            self.tag_resource(lag.lag_id, tags)
        self.lags[lag.lag_id] = lag
        return lag

    def describe_lags(self, lag_id: Optional[str]) -> list[LAG]:
        if lag_id and lag_id not in self.lags:
            raise LAGNotFound(lag_id, self.region_name)
        if lag_id:
            lag = self.lags.get(lag_id)
            return [] if not lag else [lag]
        return list(self.lags.values())

    def delete_lag(self, lag_id: str) -> LAG:
        lag = self.lags.get(lag_id)
        if not lag:
            raise LAGNotFound(lag_id, self.region_name)
        lag.lag_state = LagStateType.DELETED
        return lag

    def update_lag(
        self,
        lag_id: str,
        lag_name: Optional[str],
        minimum_links: Optional[int],
        encryption_mode: Optional[str],
    ) -> LAG:
        lag = self.lags.get(lag_id)
        if not lag:
            raise LAGNotFound(lag_id, self.region_name)
        if lag_name:
            lag.lag_name = lag_name
        if minimum_links is not None:
            lag.minimum_links = minimum_links
        if encryption_mode:
            lag.encryption_mode = EncryptionModeType(encryption_mode)
        return lag

    def associate_connection_with_lag(self, connection_id: str, lag_id: str) -> Connection:
        connection = self.connections.get(connection_id)
        if not connection:
            raise ConnectionNotFound(connection_id, self.region_name)
        lag = self.lags.get(lag_id)
        if not lag:
            raise LAGNotFound(lag_id, self.region_name)
        connection.lag_id = lag_id
        if connection not in lag.connections:
            lag.connections.append(connection)
            lag.number_of_connections = len(lag.connections)
        return connection

    def disassociate_connection_from_lag(self, connection_id: str, lag_id: str) -> Connection:
        connection = self.connections.get(connection_id)
        if not connection:
            raise ConnectionNotFound(connection_id, self.region_name)
        lag = self.lags.get(lag_id)
        if not lag:
            raise LAGNotFound(lag_id, self.region_name)
        connection.lag_id = None
        lag.connections = [c for c in lag.connections if c.connection_id != connection_id]
        lag.number_of_connections = len(lag.connections)
        return connection

    def disassociate_mac_sec_key(self, connection_id: str, secret_arn: str) -> tuple[str, MacSecKey]:
        mac_sec_keys: list[MacSecKey] = []
        if "dxlag-" in connection_id:
            if connection_id in self.lags:
                mac_sec_keys = self.lags[connection_id].mac_sec_keys
        elif connection_id in self.connections:
            mac_sec_keys = self.connections[connection_id].mac_sec_keys
        if not mac_sec_keys:
            raise ConnectionNotFound(connection_id, self.region_name)
        arn_casefold = secret_arn.casefold()
        for i, mac_sec_key in enumerate(mac_sec_keys):
            if str(mac_sec_key.secret_arn).casefold() == arn_casefold:
                mac_sec_key.state = MacSecKeyStateType.DISASSOCIATED
                return connection_id, mac_sec_keys.pop(i)
        raise MacSecKeyNotFound(secret_arn=secret_arn, connection_id=connection_id)

    # Virtual Interfaces

    def _create_virtual_interface(
        self,
        connection_id: str,
        virtual_interface_type: str,
        new_vif: dict[str, Any],
        tags: Optional[list[dict[str, str]]],
        owner_account: Optional[str] = None,
    ) -> VirtualInterface:
        bgp_peers = []
        if new_vif.get("asn"):
            bgp_peer = BGPPeer(
                asn=new_vif.get("asn", 65000),
                auth_key=new_vif.get("authKey"),
                address_family=new_vif.get("addressFamily", "ipv4"),
                amazon_address=new_vif.get("amazonAddress"),
                customer_address=new_vif.get("customerAddress"),
            )
            bgp_peers = [bgp_peer]
        vif = VirtualInterface(
            connection_id=connection_id,
            virtual_interface_type=virtual_interface_type,
            virtual_interface_name=new_vif.get("virtualInterfaceName", ""),
            vlan=new_vif.get("vlan", 0),
            asn=new_vif.get("asn", 65000),
            auth_key=new_vif.get("authKey"),
            amazon_address=new_vif.get("amazonAddress"),
            customer_address=new_vif.get("customerAddress"),
            address_family=new_vif.get("addressFamily"),
            virtual_gateway_id=new_vif.get("virtualGatewayId"),
            direct_connect_gateway_id=new_vif.get("directConnectGatewayId"),
            route_filter_prefixes=new_vif.get("routeFilterPrefixes", []),
            bgp_peers=bgp_peers,
            tags=tags,
            owner_account=owner_account or self.account_id,
            region=self.region_name,
            backend=self,
        )
        if tags:
            self.tag_resource(vif.virtual_interface_id, tags)
        self.virtual_interfaces[vif.virtual_interface_id] = vif
        return vif

    def create_private_virtual_interface(
        self,
        connection_id: str,
        new_private_virtual_interface: dict[str, Any],
        tags: Optional[list[dict[str, str]]],
    ) -> VirtualInterface:
        return self._create_virtual_interface(
            connection_id, "private", new_private_virtual_interface, tags
        )

    def create_public_virtual_interface(
        self,
        connection_id: str,
        new_public_virtual_interface: dict[str, Any],
        tags: Optional[list[dict[str, str]]],
    ) -> VirtualInterface:
        return self._create_virtual_interface(
            connection_id, "public", new_public_virtual_interface, tags
        )

    def create_transit_virtual_interface(
        self,
        connection_id: str,
        new_transit_virtual_interface: dict[str, Any],
        tags: Optional[list[dict[str, str]]],
    ) -> VirtualInterface:
        return self._create_virtual_interface(
            connection_id, "transit", new_transit_virtual_interface, tags
        )

    def allocate_private_virtual_interface(
        self,
        connection_id: str,
        owner_account: str,
        new_private_virtual_interface_allocation: dict[str, Any],
        tags: Optional[list[dict[str, str]]],
    ) -> VirtualInterface:
        return self._create_virtual_interface(
            connection_id, "private", new_private_virtual_interface_allocation, tags,
            owner_account=owner_account,
        )

    def allocate_public_virtual_interface(
        self,
        connection_id: str,
        owner_account: str,
        new_public_virtual_interface_allocation: dict[str, Any],
        tags: Optional[list[dict[str, str]]],
    ) -> VirtualInterface:
        return self._create_virtual_interface(
            connection_id, "public", new_public_virtual_interface_allocation, tags,
            owner_account=owner_account,
        )

    def allocate_transit_virtual_interface(
        self,
        connection_id: str,
        owner_account: str,
        new_transit_virtual_interface_allocation: dict[str, Any],
        tags: Optional[list[dict[str, str]]],
    ) -> VirtualInterface:
        return self._create_virtual_interface(
            connection_id, "transit", new_transit_virtual_interface_allocation, tags,
            owner_account=owner_account,
        )

    def allocate_hosted_connection(
        self,
        connection_id: str,
        owner_account: str,
        bandwidth: str,
        connection_name: str,
        vlan: int,
        tags: Optional[list[dict[str, str]]],
    ) -> Connection:
        connection = Connection(
            aws_device_v2="mock_device_v2",
            aws_device="mock_device",
            aws_logical_device_id="mock_logical_device_id",
            bandwidth=bandwidth,
            connection_name=connection_name,
            connection_state=ConnectionStateType.AVAILABLE,
            encryption_mode=EncryptionModeType.NO,
            has_logical_redundancy=False,
            jumbo_frame_capable=False,
            lag_id=None,
            loa_issue_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            location="mock_location",
            mac_sec_capable=False,
            mac_sec_keys=[],
            owner_account=owner_account,
            partner_name="mock_partner",
            port_encryption_status=PortEncryptionStatusType.DOWN,
            provider_name=None,
            region=self.region_name,
            tags=tags,
            vlan=vlan,
            backend=self,
        )
        if tags:
            self.tag_resource(connection.connection_id, tags)
        self.connections[connection.connection_id] = connection
        return connection

    def describe_virtual_interfaces(
        self, connection_id: Optional[str], virtual_interface_id: Optional[str]
    ) -> list[VirtualInterface]:
        if virtual_interface_id:
            vif = self.virtual_interfaces.get(virtual_interface_id)
            if not vif:
                raise VirtualInterfaceNotFound(virtual_interface_id, self.region_name)
            return [vif]
        if connection_id:
            return [v for v in self.virtual_interfaces.values() if v.connection_id == connection_id]
        return list(self.virtual_interfaces.values())

    def delete_virtual_interface(self, virtual_interface_id: str) -> VirtualInterface:
        vif = self.virtual_interfaces.get(virtual_interface_id)
        if not vif:
            raise VirtualInterfaceNotFound(virtual_interface_id, self.region_name)
        vif.virtual_interface_state = "deleted"
        return vif

    def confirm_private_virtual_interface(
        self,
        virtual_interface_id: str,
        virtual_gateway_id: Optional[str],
        direct_connect_gateway_id: Optional[str],
    ) -> str:
        vif = self.virtual_interfaces.get(virtual_interface_id)
        if not vif:
            raise VirtualInterfaceNotFound(virtual_interface_id, self.region_name)
        vif.virtual_interface_state = "available"
        if virtual_gateway_id:
            vif.virtual_gateway_id = virtual_gateway_id
        if direct_connect_gateway_id:
            vif.direct_connect_gateway_id = direct_connect_gateway_id
        return vif.virtual_interface_state

    def confirm_public_virtual_interface(self, virtual_interface_id: str) -> str:
        vif = self.virtual_interfaces.get(virtual_interface_id)
        if not vif:
            raise VirtualInterfaceNotFound(virtual_interface_id, self.region_name)
        vif.virtual_interface_state = "available"
        return vif.virtual_interface_state

    def confirm_transit_virtual_interface(
        self, virtual_interface_id: str, direct_connect_gateway_id: str
    ) -> str:
        vif = self.virtual_interfaces.get(virtual_interface_id)
        if not vif:
            raise VirtualInterfaceNotFound(virtual_interface_id, self.region_name)
        vif.virtual_interface_state = "available"
        vif.direct_connect_gateway_id = direct_connect_gateway_id
        return vif.virtual_interface_state

    def update_virtual_interface_attributes(
        self,
        virtual_interface_id: str,
        mtu: Optional[int],
        enable_site_link: Optional[bool],
        virtual_interface_name: Optional[str],
    ) -> VirtualInterface:
        vif = self.virtual_interfaces.get(virtual_interface_id)
        if not vif:
            raise VirtualInterfaceNotFound(virtual_interface_id, self.region_name)
        if mtu:
            vif.mtu = mtu
        if virtual_interface_name:
            vif.virtual_interface_name = virtual_interface_name
        return vif

    def create_bgp_peer(
        self,
        virtual_interface_id: str,
        new_bgp_peer: dict[str, Any],
    ) -> VirtualInterface:
        vif = self.virtual_interfaces.get(virtual_interface_id)
        if not vif:
            raise VirtualInterfaceNotFound(virtual_interface_id, self.region_name)
        bgp_peer = BGPPeer(
            asn=new_bgp_peer.get("asn", 65000),
            auth_key=new_bgp_peer.get("authKey"),
            address_family=new_bgp_peer.get("addressFamily", "ipv4"),
            amazon_address=new_bgp_peer.get("amazonAddress"),
            customer_address=new_bgp_peer.get("customerAddress"),
        )
        vif.bgp_peers.append(bgp_peer)
        return vif

    def delete_bgp_peer(
        self,
        virtual_interface_id: str,
        asn: Optional[int],
        customer_address: Optional[str],
        bgp_peer_id: Optional[str],
    ) -> VirtualInterface:
        vif = self.virtual_interfaces.get(virtual_interface_id)
        if not vif:
            raise VirtualInterfaceNotFound(virtual_interface_id, self.region_name)
        for peer in vif.bgp_peers:
            if bgp_peer_id and peer.bgp_peer_id == bgp_peer_id:
                peer.bgp_peer_state = "deleted"
                break
            elif asn and peer.asn == asn:
                peer.bgp_peer_state = "deleted"
                break
        return vif

    # Direct Connect Gateways

    def create_direct_connect_gateway(
        self,
        direct_connect_gateway_name: str,
        amazon_side_asn: Optional[int],
    ) -> DirectConnectGateway:
        gateway = DirectConnectGateway(
            direct_connect_gateway_name=direct_connect_gateway_name,
            amazon_side_asn=amazon_side_asn or 64512,
            owner_account=self.account_id,
        )
        self.direct_connect_gateways[gateway.direct_connect_gateway_id] = gateway
        return gateway

    def describe_direct_connect_gateways(
        self,
        direct_connect_gateway_id: Optional[str],
    ) -> list[DirectConnectGateway]:
        if direct_connect_gateway_id:
            gw = self.direct_connect_gateways.get(direct_connect_gateway_id)
            return [gw] if gw else []
        return list(self.direct_connect_gateways.values())

    def delete_direct_connect_gateway(self, direct_connect_gateway_id: str) -> DirectConnectGateway:
        gateway = self.direct_connect_gateways.get(direct_connect_gateway_id)
        if not gateway:
            raise DirectConnectClientError(
                "DirectConnectGatewayNotFound",
                f"Gateway {direct_connect_gateway_id} not found",
            )
        gateway.direct_connect_gateway_state = "deleted"
        return gateway

    def update_direct_connect_gateway(
        self,
        direct_connect_gateway_id: str,
        new_direct_connect_gateway_name: str,
    ) -> DirectConnectGateway:
        gateway = self.direct_connect_gateways.get(direct_connect_gateway_id)
        if not gateway:
            raise DirectConnectClientError(
                "DirectConnectGatewayNotFound",
                f"Gateway {direct_connect_gateway_id} not found",
            )
        gateway.direct_connect_gateway_name = new_direct_connect_gateway_name
        return gateway

    def create_direct_connect_gateway_association(
        self,
        direct_connect_gateway_id: str,
        gateway_id: Optional[str],
        add_allowed_prefixes: Optional[list[dict[str, str]]],
        virtual_gateway_id: Optional[str],
    ) -> DirectConnectGatewayAssociation:
        target_gateway_id = gateway_id or virtual_gateway_id or ""
        assoc = DirectConnectGatewayAssociation(
            direct_connect_gateway_id=direct_connect_gateway_id,
            direct_connect_gateway_owner_account=self.account_id,
            associated_gateway_id=target_gateway_id,
            associated_gateway_type="virtualPrivateGateway",
            associated_gateway_owner_account=self.account_id,
            allowed_prefixes_to_direct_connect_gateway=add_allowed_prefixes or [],
        )
        self.gateway_associations[assoc.association_id] = assoc
        return assoc

    def describe_direct_connect_gateway_associations(
        self,
        association_id: Optional[str],
        associated_gateway_id: Optional[str],
        direct_connect_gateway_id: Optional[str],
    ) -> list[DirectConnectGatewayAssociation]:
        if association_id:
            assoc = self.gateway_associations.get(association_id)
            return [assoc] if assoc else []
        result = list(self.gateway_associations.values())
        if associated_gateway_id:
            result = [a for a in result if a.associated_gateway_id == associated_gateway_id]
        if direct_connect_gateway_id:
            result = [a for a in result if a.direct_connect_gateway_id == direct_connect_gateway_id]
        return result

    def delete_direct_connect_gateway_association(
        self,
        association_id: Optional[str],
        direct_connect_gateway_id: Optional[str],
        virtual_gateway_id: Optional[str],
    ) -> DirectConnectGatewayAssociation:
        if association_id:
            assoc = self.gateway_associations.get(association_id)
        elif direct_connect_gateway_id and virtual_gateway_id:
            assoc = next(
                (
                    a for a in self.gateway_associations.values()
                    if a.direct_connect_gateway_id == direct_connect_gateway_id
                    and a.associated_gateway_id == virtual_gateway_id
                ),
                None,
            )
        else:
            assoc = None
        if not assoc:
            raise DirectConnectClientError(
                "DirectConnectGatewayAssociationNotFound",
                "Association not found",
            )
        assoc.association_state = "disassociated"
        return assoc

    def update_direct_connect_gateway_association(
        self,
        association_id: str,
        add_allowed_prefixes: Optional[list[dict[str, str]]],
        remove_allowed_prefixes: Optional[list[dict[str, str]]],
    ) -> DirectConnectGatewayAssociation:
        assoc = self.gateway_associations.get(association_id)
        if not assoc:
            raise DirectConnectClientError(
                "DirectConnectGatewayAssociationNotFound",
                f"Association {association_id} not found",
            )
        if add_allowed_prefixes:
            existing = {p["cidr"] for p in assoc.allowed_prefixes_to_direct_connect_gateway}
            for p in add_allowed_prefixes:
                if p["cidr"] not in existing:
                    assoc.allowed_prefixes_to_direct_connect_gateway.append(p)
        if remove_allowed_prefixes:
            remove_cidrs = {p["cidr"] for p in remove_allowed_prefixes}
            assoc.allowed_prefixes_to_direct_connect_gateway = [
                p for p in assoc.allowed_prefixes_to_direct_connect_gateway
                if p["cidr"] not in remove_cidrs
            ]
        return assoc

    def create_direct_connect_gateway_association_proposal(
        self,
        direct_connect_gateway_id: str,
        direct_connect_gateway_owner_account: str,
        gateway_id: str,
        add_allowed_prefixes: Optional[list[dict[str, str]]],
        remove_allowed_prefixes: Optional[list[dict[str, str]]],
    ) -> DirectConnectGatewayAssociationProposal:
        proposal = DirectConnectGatewayAssociationProposal(
            direct_connect_gateway_id=direct_connect_gateway_id,
            direct_connect_gateway_owner_account=direct_connect_gateway_owner_account,
            gateway_id=gateway_id,
            add_allowed_prefixes=add_allowed_prefixes or [],
            remove_allowed_prefixes=remove_allowed_prefixes or [],
        )
        self.gateway_association_proposals[proposal.proposal_id] = proposal
        return proposal

    def describe_direct_connect_gateway_association_proposals(
        self,
        direct_connect_gateway_id: Optional[str],
        proposal_id: Optional[str],
        associated_gateway_id: Optional[str],
    ) -> list[DirectConnectGatewayAssociationProposal]:
        if proposal_id:
            p = self.gateway_association_proposals.get(proposal_id)
            return [p] if p else []
        result = list(self.gateway_association_proposals.values())
        if direct_connect_gateway_id:
            result = [p for p in result if p.direct_connect_gateway_id == direct_connect_gateway_id]
        if associated_gateway_id:
            result = [p for p in result if p.gateway_id == associated_gateway_id]
        return result

    def delete_direct_connect_gateway_association_proposal(
        self, proposal_id: str
    ) -> DirectConnectGatewayAssociationProposal:
        proposal = self.gateway_association_proposals.get(proposal_id)
        if not proposal:
            raise DirectConnectClientError(
                "DirectConnectGatewayAssociationProposalNotFound",
                f"Proposal {proposal_id} not found",
            )
        proposal.proposal_state = "deleted"
        return proposal

    def accept_direct_connect_gateway_association_proposal(
        self,
        proposal_id: str,
        associated_gateway_owner_account: str,
        override_allowed_prefixes: Optional[list[dict[str, str]]],
    ) -> DirectConnectGatewayAssociation:
        proposal = self.gateway_association_proposals.get(proposal_id)
        if not proposal:
            raise DirectConnectClientError(
                "DirectConnectGatewayAssociationProposalNotFound",
                f"Proposal {proposal_id} not found",
            )
        proposal.proposal_state = "accepted"
        assoc = DirectConnectGatewayAssociation(
            direct_connect_gateway_id=proposal.direct_connect_gateway_id,
            direct_connect_gateway_owner_account=proposal.direct_connect_gateway_owner_account,
            associated_gateway_id=proposal.gateway_id,
            associated_gateway_type="virtualPrivateGateway",
            associated_gateway_owner_account=associated_gateway_owner_account,
            allowed_prefixes_to_direct_connect_gateway=(
                override_allowed_prefixes or proposal.add_allowed_prefixes
            ),
        )
        self.gateway_associations[assoc.association_id] = assoc
        return assoc

    def describe_direct_connect_gateway_attachments(
        self,
        direct_connect_gateway_id: Optional[str],
        virtual_interface_id: Optional[str],
    ) -> list[dict[str, Any]]:
        attachments = []
        for vif in self.virtual_interfaces.values():
            if vif.direct_connect_gateway_id:
                if direct_connect_gateway_id and vif.direct_connect_gateway_id != direct_connect_gateway_id:
                    continue
                if virtual_interface_id and vif.virtual_interface_id != virtual_interface_id:
                    continue
                attachments.append({
                    "directConnectGatewayId": vif.direct_connect_gateway_id,
                    "virtualInterfaceId": vif.virtual_interface_id,
                    "virtualInterfaceRegion": self.region_name,
                    "virtualInterfaceOwnerAccount": vif.owner_account,
                    "attachmentState": "attached",
                    "attachmentType": "TransitVirtualInterface",
                    "stateChangeError": "",
                })
        return attachments

    # Interconnects

    def create_interconnect(
        self,
        interconnect_name: str,
        bandwidth: str,
        location: str,
        lag_id: Optional[str],
        tags: Optional[list[dict[str, str]]],
        provider_name: Optional[str],
    ) -> Interconnect:
        interconnect = Interconnect(
            interconnect_name=interconnect_name,
            bandwidth=bandwidth,
            location=location,
            lag_id=lag_id,
            provider_name=provider_name,
            tags=tags,
            owner_account=self.account_id,
            region=self.region_name,
            backend=self,
        )
        if tags:
            self.tag_resource(interconnect.interconnect_id, tags)
        self.interconnects[interconnect.interconnect_id] = interconnect
        return interconnect

    def describe_interconnects(self, interconnect_id: Optional[str]) -> list[Interconnect]:
        if interconnect_id:
            ic = self.interconnects.get(interconnect_id)
            if not ic:
                raise InterconnectNotFound(interconnect_id, self.region_name)
            return [ic]
        return list(self.interconnects.values())

    def delete_interconnect(self, interconnect_id: str) -> str:
        ic = self.interconnects.get(interconnect_id)
        if not ic:
            raise InterconnectNotFound(interconnect_id, self.region_name)
        ic.interconnect_state = "deleted"
        return ic.interconnect_state

    def describe_connections_on_interconnect(self, interconnect_id: str) -> list[Connection]:
        if interconnect_id not in self.interconnects:
            raise InterconnectNotFound(interconnect_id, self.region_name)
        return [c for c in self.connections.values() if c.lag_id == interconnect_id]

    def describe_interconnect_loa(
        self,
        interconnect_id: str,
        provider_name: Optional[str],
        loa_content_type: Optional[str],
    ) -> dict[str, Any]:
        if interconnect_id not in self.interconnects:
            raise InterconnectNotFound(interconnect_id, self.region_name)
        return {
            "loa": {
                "loaContent": "bW9ja19sb2FfY29udGVudA==",
                "loaContentType": loa_content_type or "application/pdf",
            }
        }

    def describe_loa(
        self,
        connection_id: str,
        provider_name: Optional[str],
        loa_content_type: Optional[str],
    ) -> dict[str, Any]:
        return {
            "loaContent": "bW9ja19sb2FfY29udGVudA==",
            "loaContentType": loa_content_type or "application/pdf",
        }

    # Virtual Gateways

    def describe_virtual_gateways(self) -> list[VirtualGateway]:
        return list(self.virtual_gateways.values())

    def associate_hosted_connection(self, connection_id: str, parent_connection_id: str) -> Connection:
        connection = self.connections.get(connection_id)
        if not connection:
            raise ConnectionNotFound(connection_id, self.region_name)
        connection.lag_id = parent_connection_id
        return connection

    def associate_virtual_interface(self, virtual_interface_id: str, connection_id: str) -> VirtualInterface:
        vif = self.virtual_interfaces.get(virtual_interface_id)
        if not vif:
            raise VirtualInterfaceNotFound(virtual_interface_id, self.region_name)
        vif.connection_id = connection_id
        return vif

    def confirm_customer_agreement(self, agreement_name: Optional[str]) -> str:
        return "signed"

    def describe_customer_metadata(self) -> dict[str, Any]:
        return {
            "agreements": [
                {
                    "agreementName": "SpectrumFrameworkAgreement",
                    "agreementType": "ManagedAgreement",
                    "ownerAccount": self.account_id,
                    "status": "signed",
                }
            ],
            "nniPartnerType": "nonPartner",
        }

    def describe_locations(self) -> list[dict[str, Any]]:
        return [
            {
                "locationCode": "EqDC2",
                "locationName": "Equinix DC2, Ashburn, VA",
                "region": "us-east-1",
                "availablePortSpeeds": ["1Gbps", "10Gbps"],
                "availableProviders": ["CenturyLink Communications LLC", "CoreSite"],
                "availableMacSecPortSpeeds": ["10Gbps"],
            },
            {
                "locationCode": "EqSV5",
                "locationName": "Equinix SV5, San Jose, CA",
                "region": "us-west-1",
                "availablePortSpeeds": ["1Gbps", "10Gbps"],
                "availableProviders": ["AT&T", "Tata Communications"],
                "availableMacSecPortSpeeds": [],
            },
        ]

    def describe_router_configuration(
        self, virtual_interface_id: str, router_type_identifier: Optional[str]
    ) -> dict[str, Any]:
        vif = self.virtual_interfaces.get(virtual_interface_id)
        if not vif:
            raise VirtualInterfaceNotFound(virtual_interface_id, self.region_name)
        return {
            "customerRouterConfig": "! example config",
            "router": {
                "platform": "mock_platform",
                "softwareVersion": "mock_version",
                "xsltTemplateName": "mock_template",
                "xsltTemplateNameForMacSec": "",
                "routerTypeIdentifier": router_type_identifier or "CiscoSystemsInc-2900SeriesRouters-IOS124",
            },
            "virtualInterfaceId": virtual_interface_id,
            "virtualInterfaceName": vif.virtual_interface_name,
        }

    def list_virtual_interface_test_history(
        self,
        test_id: Optional[str],
        virtual_interface_id: Optional[str],
        bgp_peers: Optional[list[str]],
        status: Optional[str],
    ) -> list[dict[str, Any]]:
        return []

    def start_bgp_failover_test(
        self,
        virtual_interface_id: str,
        bgp_peers: Optional[list[str]],
        test_duration_in_minutes: Optional[int],
    ) -> dict[str, Any]:
        return {
            "virtualInterfaceTest": {
                "testId": f"dxtest-{uuid.uuid4().hex[:8]}",
                "virtualInterfaceId": virtual_interface_id,
                "bgpPeers": bgp_peers or [],
                "status": "IN_PROGRESS",
                "ownerAccount": self.account_id,
                "testDurationInMinutes": test_duration_in_minutes or 180,
                "startTime": datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
                "endTime": None,
            }
        }

    def stop_bgp_failover_test(self, virtual_interface_id: str) -> dict[str, Any]:
        return {
            "virtualInterfaceTest": {
                "testId": f"dxtest-{uuid.uuid4().hex[:8]}",
                "virtualInterfaceId": virtual_interface_id,
                "bgpPeers": [],
                "status": "COMPLETED",
                "ownerAccount": self.account_id,
                "testDurationInMinutes": 180,
                "startTime": datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
                "endTime": datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
            }
        }

    def allocate_connection_on_interconnect(
        self,
        bandwidth: str,
        connection_name: str,
        owner_account: str,
        interconnect_id: str,
        vlan: int,
    ) -> Connection:
        connection = Connection(
            aws_device_v2="mock_device_v2",
            aws_device="mock_device",
            aws_logical_device_id="mock_logical_device_id",
            bandwidth=bandwidth,
            connection_name=connection_name,
            connection_state=ConnectionStateType.AVAILABLE,
            encryption_mode=EncryptionModeType.NO,
            has_logical_redundancy=False,
            jumbo_frame_capable=False,
            lag_id=interconnect_id,
            loa_issue_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            location="mock_location",
            mac_sec_capable=False,
            mac_sec_keys=[],
            owner_account=owner_account,
            partner_name="mock_partner",
            port_encryption_status=PortEncryptionStatusType.DOWN,
            provider_name=None,
            region=self.region_name,
            tags=None,
            vlan=vlan,
            backend=self,
        )
        self.connections[connection.connection_id] = connection
        return connection


directconnect_backends = BackendDict(DirectConnectBackend, "directconnect")
