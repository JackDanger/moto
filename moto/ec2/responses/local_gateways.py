from moto.ec2.utils import add_tag_specification

from ._base_response import EC2BaseResponse


class LocalGatewayResponse(EC2BaseResponse):
    def create_local_gateway_route_table(self) -> str:
        lgw_id = self._get_param("LocalGatewayId")
        mode = self._get_param("Mode", "direct-vpc-routing")
        tags = add_tag_specification(
            self._get_param("TagSpecifications", [])
        )
        table = self.ec2_backend.create_local_gateway_route_table(
            local_gateway_id=lgw_id,
            mode=mode,
            tags=tags,
        )
        template = self.response_template(
            CREATE_LOCAL_GATEWAY_ROUTE_TABLE
        )
        return template.render(table=table)

    def describe_local_gateway_route_tables(self) -> str:
        table_ids = self._get_param(
            "LocalGatewayRouteTableId", []
        )
        tables = self.ec2_backend.describe_local_gateway_route_tables(
            local_gateway_route_table_ids=table_ids or None,
        )
        template = self.response_template(
            DESCRIBE_LOCAL_GATEWAY_ROUTE_TABLES
        )
        return template.render(tables=tables)

    def delete_local_gateway_route_table(self) -> str:
        table_id = self._get_param("LocalGatewayRouteTableId")
        table = self.ec2_backend.delete_local_gateway_route_table(
            local_gateway_route_table_id=table_id,
        )
        template = self.response_template(
            DELETE_LOCAL_GATEWAY_ROUTE_TABLE
        )
        return template.render(table=table)

    def create_local_gateway_route(self) -> str:
        dst_cidr = self._get_param("DestinationCidrBlock")
        table_id = self._get_param("LocalGatewayRouteTableId")
        vif_group_id = self._get_param(
            "LocalGatewayVirtualInterfaceGroupId"
        )
        eni_id = self._get_param("NetworkInterfaceId")
        route = self.ec2_backend.create_local_gateway_route(
            destination_cidr_block=dst_cidr,
            local_gateway_route_table_id=table_id,
            local_gateway_virtual_interface_group_id=vif_group_id,
            network_interface_id=eni_id,
        )
        template = self.response_template(
            CREATE_LOCAL_GATEWAY_ROUTE
        )
        return template.render(route=route)

    def search_local_gateway_routes(self) -> str:
        table_id = self._get_param("LocalGatewayRouteTableId")
        routes = self.ec2_backend.search_local_gateway_routes(
            local_gateway_route_table_id=table_id,
        )
        template = self.response_template(
            DESCRIBE_LOCAL_GATEWAY_ROUTES
        )
        return template.render(routes=routes)


CREATE_LOCAL_GATEWAY_ROUTE_TABLE = """<CreateLocalGatewayRouteTableResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
  <requestId>7a62c49f-347e-4fc4-9331-6e8eEXAMPLE</requestId>
  <localGatewayRouteTable>
    <localGatewayRouteTableId>{{ table.id }}</localGatewayRouteTableId>
    <localGatewayRouteTableArn>{{ table.arn }}</localGatewayRouteTableArn>
    <localGatewayId>{{ table.local_gateway_id }}</localGatewayId>
    <state>{{ table.state }}</state>
    <mode>{{ table.mode }}</mode>
    <ownerId>{{ table.owner_id }}</ownerId>
    <tagSet>
      {% for tag in table.get_tags() %}
      <item>
        <key>{{ tag.key }}</key>
        <value>{{ tag.value }}</value>
      </item>
      {% endfor %}
    </tagSet>
  </localGatewayRouteTable>
</CreateLocalGatewayRouteTableResponse>"""

DESCRIBE_LOCAL_GATEWAY_ROUTE_TABLES = """<DescribeLocalGatewayRouteTablesResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
  <requestId>7a62c49f-347e-4fc4-9331-6e8eEXAMPLE</requestId>
  <localGatewayRouteTableSet>
    {% for table in tables %}
    <item>
      <localGatewayRouteTableId>{{ table.id }}</localGatewayRouteTableId>
      <localGatewayRouteTableArn>{{ table.arn }}</localGatewayRouteTableArn>
      <localGatewayId>{{ table.local_gateway_id }}</localGatewayId>
      <state>{{ table.state }}</state>
      <mode>{{ table.mode }}</mode>
      <ownerId>{{ table.owner_id }}</ownerId>
      <tagSet>
        {% for tag in table.get_tags() %}
        <item>
          <key>{{ tag.key }}</key>
          <value>{{ tag.value }}</value>
        </item>
        {% endfor %}
      </tagSet>
    </item>
    {% endfor %}
  </localGatewayRouteTableSet>
</DescribeLocalGatewayRouteTablesResponse>"""

DELETE_LOCAL_GATEWAY_ROUTE_TABLE = """<DeleteLocalGatewayRouteTableResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
  <requestId>7a62c49f-347e-4fc4-9331-6e8eEXAMPLE</requestId>
  <localGatewayRouteTable>
    <localGatewayRouteTableId>{{ table.id }}</localGatewayRouteTableId>
    <state>{{ table.state }}</state>
  </localGatewayRouteTable>
</DeleteLocalGatewayRouteTableResponse>"""

CREATE_LOCAL_GATEWAY_ROUTE = """<CreateLocalGatewayRouteResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
  <requestId>7a62c49f-347e-4fc4-9331-6e8eEXAMPLE</requestId>
  <route>
    <destinationCidrBlock>{{ route.destination_cidr_block }}</destinationCidrBlock>
    <localGatewayRouteTableId>{{ route.local_gateway_route_table_id }}</localGatewayRouteTableId>
    <type>{{ route.route_type }}</type>
    <state>{{ route.state }}</state>
    {% if route.local_gateway_virtual_interface_group_id %}
    <localGatewayVirtualInterfaceGroupId>{{ route.local_gateway_virtual_interface_group_id }}</localGatewayVirtualInterfaceGroupId>
    {% endif %}
    {% if route.network_interface_id %}
    <networkInterfaceId>{{ route.network_interface_id }}</networkInterfaceId>
    {% endif %}
  </route>
</CreateLocalGatewayRouteResponse>"""

DESCRIBE_LOCAL_GATEWAY_ROUTES = """<DescribeLocalGatewayRoutesResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
  <requestId>7a62c49f-347e-4fc4-9331-6e8eEXAMPLE</requestId>
  <routeSet>
    {% for route in routes %}
    <item>
      <destinationCidrBlock>{{ route.destination_cidr_block }}</destinationCidrBlock>
      <localGatewayRouteTableId>{{ route.local_gateway_route_table_id }}</localGatewayRouteTableId>
      <type>{{ route.route_type }}</type>
      <state>{{ route.state }}</state>
      {% if route.local_gateway_virtual_interface_group_id %}
      <localGatewayVirtualInterfaceGroupId>{{ route.local_gateway_virtual_interface_group_id }}</localGatewayVirtualInterfaceGroupId>
      {% endif %}
      {% if route.network_interface_id %}
      <networkInterfaceId>{{ route.network_interface_id }}</networkInterfaceId>
      {% endif %}
    </item>
    {% endfor %}
  </routeSet>
</DescribeLocalGatewayRoutesResponse>"""
