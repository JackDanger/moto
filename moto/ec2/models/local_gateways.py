from typing import Any, Optional

from ..utils import (
    random_local_gateway_id,
    random_local_gateway_route_table_id,
)
from .core import TaggedEC2Resource


class LocalGatewayRouteTable(TaggedEC2Resource):
    def __init__(
        self,
        ec2_backend: Any,
        local_gateway_id: str,
        mode: str = "direct-vpc-routing",
        tags: Optional[dict[str, str]] = None,
    ):
        self.ec2_backend = ec2_backend
        self.id = random_local_gateway_route_table_id()
        self.local_gateway_id = local_gateway_id
        self.mode = mode
        self.state = "available"
        self.routes: dict[str, "LocalGatewayRoute"] = {}
        self.add_tags(tags or {})

    @property
    def owner_id(self) -> str:
        return self.ec2_backend.account_id

    @property
    def arn(self) -> str:
        return (
            f"arn:{self.ec2_backend.partition}:ec2"
            f":{self.ec2_backend.region_name}"
            f":{self.ec2_backend.account_id}"
            f":local-gateway-route-table/{self.id}"
        )


class LocalGatewayRoute:
    def __init__(
        self,
        destination_cidr_block: str,
        local_gateway_route_table_id: str,
        local_gateway_virtual_interface_group_id: Optional[str] = None,
        network_interface_id: Optional[str] = None,
        route_type: str = "static",
    ):
        self.destination_cidr_block = destination_cidr_block
        self.local_gateway_route_table_id = local_gateway_route_table_id
        self.local_gateway_virtual_interface_group_id = (
            local_gateway_virtual_interface_group_id
        )
        self.network_interface_id = network_interface_id
        self.route_type = route_type
        self.state = "active"
        if network_interface_id:
            self.target_type = "network-interface"
        else:
            self.target_type = "local-gateway-virtual-interface-group"


class LocalGateway(TaggedEC2Resource):
    def __init__(
        self,
        ec2_backend: Any,
        tags: Optional[dict[str, str]] = None,
    ):
        self.ec2_backend = ec2_backend
        self.id = random_local_gateway_id()
        self.state = "available"
        self.add_tags(tags or {})

    @property
    def owner_id(self) -> str:
        return self.ec2_backend.account_id


class LocalGatewayBackend:
    def __init__(self) -> None:
        self.local_gateways: dict[str, LocalGateway] = {}
        self.local_gateway_route_tables: dict[
            str, LocalGatewayRouteTable
        ] = {}

    def create_local_gateway_route_table(
        self,
        local_gateway_id: str,
        mode: str = "direct-vpc-routing",
        tags: Optional[dict[str, str]] = None,
    ) -> LocalGatewayRouteTable:
        route_table = LocalGatewayRouteTable(
            self,
            local_gateway_id=local_gateway_id,
            mode=mode,
            tags=tags,
        )
        self.local_gateway_route_tables[route_table.id] = route_table
        return route_table

    def describe_local_gateway_route_tables(
        self,
        local_gateway_route_table_ids: Optional[list[str]] = None,
    ) -> list[LocalGatewayRouteTable]:
        tables = list(self.local_gateway_route_tables.values())
        if local_gateway_route_table_ids:
            tables = [
                t
                for t in tables
                if t.id in local_gateway_route_table_ids
            ]
        return tables

    def delete_local_gateway_route_table(
        self,
        local_gateway_route_table_id: str,
    ) -> LocalGatewayRouteTable:
        table = self.local_gateway_route_tables.get(
            local_gateway_route_table_id
        )
        if not table:
            from ..exceptions import InvalidLocalGatewayRouteTableIdError

            raise InvalidLocalGatewayRouteTableIdError(
                local_gateway_route_table_id
            )
        table.state = "deleted"
        return self.local_gateway_route_tables.pop(
            local_gateway_route_table_id
        )

    def create_local_gateway_route(
        self,
        destination_cidr_block: str,
        local_gateway_route_table_id: str,
        local_gateway_virtual_interface_group_id: Optional[str] = None,
        network_interface_id: Optional[str] = None,
    ) -> LocalGatewayRoute:
        table = self.local_gateway_route_tables.get(
            local_gateway_route_table_id
        )
        if not table:
            from ..exceptions import InvalidLocalGatewayRouteTableIdError

            raise InvalidLocalGatewayRouteTableIdError(
                local_gateway_route_table_id
            )
        route = LocalGatewayRoute(
            destination_cidr_block=destination_cidr_block,
            local_gateway_route_table_id=local_gateway_route_table_id,
            local_gateway_virtual_interface_group_id=(
                local_gateway_virtual_interface_group_id
            ),
            network_interface_id=network_interface_id,
        )
        table.routes[destination_cidr_block] = route
        return route

    def search_local_gateway_routes(
        self,
        local_gateway_route_table_id: str,
    ) -> list[LocalGatewayRoute]:
        table = self.local_gateway_route_tables.get(
            local_gateway_route_table_id
        )
        if not table:
            return []
        return list(table.routes.values())
