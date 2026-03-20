from moto.ec2.utils import add_tag_specification

from ._base_response import EC2BaseResponse


class CoipResponse(EC2BaseResponse):
    def create_coip_pool(self) -> str:
        local_gw_rt_id = self._get_param("LocalGatewayRouteTableId")
        tags = add_tag_specification(self._get_param("TagSpecifications", []))
        pool = self.ec2_backend.create_coip_pool(
            local_gateway_route_table_id=local_gw_rt_id,
            tags=tags,
        )
        template = self.response_template(CREATE_COIP_POOL)
        return template.render(pool=pool)

    def delete_coip_pool(self) -> str:
        pool_id = self._get_param("CoipPoolId")
        pool = self.ec2_backend.delete_coip_pool(coip_pool_id=pool_id)
        template = self.response_template(DELETE_COIP_POOL)
        return template.render(pool=pool)

    def describe_coip_pools(self) -> str:
        pool_ids = self._get_param("CoipPoolId", [])
        pools = self.ec2_backend.describe_coip_pools(pool_ids=pool_ids or None)
        template = self.response_template(DESCRIBE_COIP_POOLS)
        return template.render(pools=pools)

    def get_coip_pool_usage(self) -> str:
        pool_id = self._get_param("PoolId")
        pool, cidrs = self.ec2_backend.get_coip_pool_usage(pool_id=pool_id)
        template = self.response_template(GET_COIP_POOL_USAGE)
        return template.render(pool=pool, cidrs=cidrs, pool_id=pool_id)

    def create_coip_cidr(self) -> str:
        pool_id = self._get_param("CoipPoolId")
        cidr = self._get_param("Cidr")
        coip_cidr = self.ec2_backend.create_coip_cidr(coip_pool_id=pool_id, cidr=cidr)
        template = self.response_template(CREATE_COIP_CIDR)
        return template.render(coip_cidr=coip_cidr)

    def delete_coip_cidr(self) -> str:
        pool_id = self._get_param("CoipPoolId")
        cidr = self._get_param("Cidr")
        coip_cidr = self.ec2_backend.delete_coip_cidr(coip_pool_id=pool_id, cidr=cidr)
        template = self.response_template(DELETE_COIP_CIDR)
        return template.render(coip_cidr=coip_cidr)


CREATE_COIP_POOL = """<CreateCoipPoolResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
  <requestId>7a62c49f-347e-4fc4-9331-6e8eEXAMPLE</requestId>
  <coipPool>
    <poolId>{{ pool.id }}</poolId>
    <localGatewayRouteTableId>{{ pool.local_gateway_route_table_id }}</localGatewayRouteTableId>
    <poolArn>{{ pool.pool_arn }}</poolArn>
    <poolCidrs>
      {% for cidr in pool.pool_cidrs %}
      <item>{{ cidr }}</item>
      {% endfor %}
    </poolCidrs>
    <tagSet>
      {% for tag in pool.get_tags() %}
      <item>
        <key>{{ tag.key }}</key>
        <value>{{ tag.value }}</value>
      </item>
      {% endfor %}
    </tagSet>
  </coipPool>
</CreateCoipPoolResponse>"""

DELETE_COIP_POOL = """<DeleteCoipPoolResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
  <requestId>7a62c49f-347e-4fc4-9331-6e8eEXAMPLE</requestId>
  <coipPool>
    <poolId>{{ pool.id }}</poolId>
  </coipPool>
</DeleteCoipPoolResponse>"""

DESCRIBE_COIP_POOLS = """<DescribeCoipPoolsResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
  <requestId>7a62c49f-347e-4fc4-9331-6e8eEXAMPLE</requestId>
  <coipPoolSet>
    {% for pool in pools %}
    <item>
      <poolId>{{ pool.id }}</poolId>
      <localGatewayRouteTableId>{{ pool.local_gateway_route_table_id }}</localGatewayRouteTableId>
      <poolArn>{{ pool.pool_arn }}</poolArn>
      <poolCidrs>
        {% for cidr in pool.pool_cidrs %}
        <item>{{ cidr }}</item>
        {% endfor %}
      </poolCidrs>
      <tagSet>
        {% for tag in pool.get_tags() %}
        <item>
          <key>{{ tag.key }}</key>
          <value>{{ tag.value }}</value>
        </item>
        {% endfor %}
      </tagSet>
    </item>
    {% endfor %}
  </coipPoolSet>
</DescribeCoipPoolsResponse>"""

GET_COIP_POOL_USAGE = """<GetCoipPoolUsageResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
  <requestId>7a62c49f-347e-4fc4-9331-6e8eEXAMPLE</requestId>
  <coipPoolId>{{ pool_id }}</coipPoolId>
  {% if pool %}
  <localGatewayRouteTableId>{{ pool.local_gateway_route_table_id }}</localGatewayRouteTableId>
  {% endif %}
  <coipAddressUsageSet/>
</GetCoipPoolUsageResponse>"""

CREATE_COIP_CIDR = """<CreateCoipCidrResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
  <requestId>7a62c49f-347e-4fc4-9331-6e8eEXAMPLE</requestId>
  <coipCidr>
    <cidr>{{ coip_cidr.cidr }}</cidr>
    <coipPoolId>{{ coip_cidr.coip_pool_id }}</coipPoolId>
    <localGatewayRouteTableId>{{ coip_cidr.local_gateway_route_table_id }}</localGatewayRouteTableId>
  </coipCidr>
</CreateCoipCidrResponse>"""

DELETE_COIP_CIDR = """<DeleteCoipCidrResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
  <requestId>7a62c49f-347e-4fc4-9331-6e8eEXAMPLE</requestId>
  <coipCidr>
    <cidr>{{ coip_cidr.cidr }}</cidr>
    <coipPoolId>{{ coip_cidr.coip_pool_id }}</coipPoolId>
    <localGatewayRouteTableId>{{ coip_cidr.local_gateway_route_table_id }}</localGatewayRouteTableId>
  </coipCidr>
</DeleteCoipCidrResponse>"""
