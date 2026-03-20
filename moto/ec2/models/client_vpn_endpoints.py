from typing import Any, Optional

from moto.core.utils import iso_8601_datetime_with_milliseconds, utcnow

from ..utils import random_client_vpn_endpoint_id
from .core import TaggedEC2Resource


class ClientVpnEndpoint(TaggedEC2Resource):
    def __init__(
        self,
        ec2_backend: Any,
        client_vpn_endpoint_id: str,
        client_cidr_block: str,
        server_certificate_arn: str,
        authentication_options: Optional[list[dict[str, Any]]] = None,
        connection_log_options: Optional[dict[str, Any]] = None,
        dns_servers: Optional[list[str]] = None,
        transport_protocol: str = "udp",
        vpn_port: int = 443,
        description: str = "",
        split_tunnel: bool = False,
        vpc_id: Optional[str] = None,
        security_group_ids: Optional[list[str]] = None,
        tags: Optional[dict[str, str]] = None,
    ):
        self.ec2_backend = ec2_backend
        self.id = client_vpn_endpoint_id
        self.client_cidr_block = client_cidr_block
        self.server_certificate_arn = server_certificate_arn
        self.authentication_options = authentication_options or []
        self.connection_log_options = connection_log_options or {}
        self.dns_servers = dns_servers or []
        self.transport_protocol = transport_protocol
        self.vpn_port = vpn_port
        self.description = description
        self.split_tunnel = split_tunnel
        self.vpc_id = vpc_id
        self.security_group_ids = security_group_ids or []
        self.state = "available"
        self._created_at = utcnow()
        self.add_tags(tags or {})

    @property
    def creation_time(self) -> str:
        return iso_8601_datetime_with_milliseconds(self._created_at)

    @property
    def dns_name(self) -> str:
        return f"*.{self.id}.prod.clientvpn.{self.ec2_backend.region_name}.amazonaws.com"


class ClientVpnEndpointBackend:
    def __init__(self) -> None:
        self.client_vpn_endpoints: dict[str, ClientVpnEndpoint] = {}

    def create_client_vpn_endpoint(
        self,
        client_cidr_block: str,
        server_certificate_arn: str,
        authentication_options: Optional[list[dict[str, Any]]] = None,
        connection_log_options: Optional[dict[str, Any]] = None,
        dns_servers: Optional[list[str]] = None,
        transport_protocol: str = "udp",
        vpn_port: int = 443,
        description: str = "",
        split_tunnel: bool = False,
        vpc_id: Optional[str] = None,
        security_group_ids: Optional[list[str]] = None,
        tags: Optional[dict[str, str]] = None,
    ) -> ClientVpnEndpoint:
        client_vpn_endpoint_id = random_client_vpn_endpoint_id()
        client_vpn_endpoint = ClientVpnEndpoint(
            self,
            client_vpn_endpoint_id=client_vpn_endpoint_id,
            client_cidr_block=client_cidr_block,
            server_certificate_arn=server_certificate_arn,
            authentication_options=authentication_options,
            connection_log_options=connection_log_options,
            dns_servers=dns_servers,
            transport_protocol=transport_protocol,
            vpn_port=vpn_port,
            description=description,
            split_tunnel=split_tunnel,
            vpc_id=vpc_id,
            security_group_ids=security_group_ids,
            tags=tags,
        )
        self.client_vpn_endpoints[client_vpn_endpoint.id] = client_vpn_endpoint
        return client_vpn_endpoint

    def describe_client_vpn_endpoints(
        self, client_vpn_endpoint_ids: Optional[list[str]] = None
    ) -> list[ClientVpnEndpoint]:
        endpoints = list(self.client_vpn_endpoints.values())
        if client_vpn_endpoint_ids:
            endpoints = [e for e in endpoints if e.id in client_vpn_endpoint_ids]
        return endpoints

    def delete_client_vpn_endpoint(
        self, client_vpn_endpoint_id: str
    ) -> ClientVpnEndpoint:
        endpoint = self.client_vpn_endpoints.get(client_vpn_endpoint_id)
        if endpoint:
            endpoint.state = "deleting"
            self.client_vpn_endpoints.pop(client_vpn_endpoint_id, None)
        else:
            from ..exceptions import InvalidClientVpnEndpointIdError

            raise InvalidClientVpnEndpointIdError(client_vpn_endpoint_id)
        return endpoint

    def modify_client_vpn_endpoint(
        self,
        client_vpn_endpoint_id: str,
        server_certificate_arn: Optional[str] = None,
        connection_log_options: Optional[dict[str, Any]] = None,
        dns_servers: Optional[list[str]] = None,
        vpn_port: Optional[int] = None,
        description: Optional[str] = None,
        split_tunnel: Optional[bool] = None,
        vpc_id: Optional[str] = None,
        security_group_ids: Optional[list[str]] = None,
    ) -> bool:
        endpoint = self.client_vpn_endpoints.get(client_vpn_endpoint_id)
        if not endpoint:
            from ..exceptions import InvalidClientVpnEndpointIdError

            raise InvalidClientVpnEndpointIdError(client_vpn_endpoint_id)
        if server_certificate_arn is not None:
            endpoint.server_certificate_arn = server_certificate_arn
        if connection_log_options is not None:
            endpoint.connection_log_options = connection_log_options
        if dns_servers is not None:
            endpoint.dns_servers = dns_servers
        if vpn_port is not None:
            endpoint.vpn_port = vpn_port
        if description is not None:
            endpoint.description = description
        if split_tunnel is not None:
            endpoint.split_tunnel = split_tunnel
        if vpc_id is not None:
            endpoint.vpc_id = vpc_id
        if security_group_ids is not None:
            endpoint.security_group_ids = security_group_ids
        return True
