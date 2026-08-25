from moto.core.responses import ActionResult
from moto.ec2.utils import add_tag_specification

from ._base_response import EC2BaseResponse


class PublicIpv4PoolResponse(EC2BaseResponse):
    def create_public_ipv4_pool(self) -> ActionResult:
        tags = add_tag_specification(self._get_param("TagSpecifications", []))
        pool = self.ec2_backend.create_public_ipv4_pool(tags=tags)
        result = {"PoolId": pool.id}
        return ActionResult(result)

    def delete_public_ipv4_pool(self) -> ActionResult:
        pool_id = self._get_param("PoolId")
        self.ec2_backend.delete_public_ipv4_pool(pool_id=pool_id)
        result = {"Return": True}
        return ActionResult(result)

    def describe_public_ipv4_pools(self) -> ActionResult:
        pool_ids = self._get_param("PoolId", [])
        pools = self.ec2_backend.describe_public_ipv4_pools(
            pool_ids=pool_ids or None,
        )
        result = {"PublicIpv4Pools": pools}
        return ActionResult(result)

    def provision_public_ipv4_pool_cidr(self) -> ActionResult:
        pool_id = self._get_param("PoolId")
        ipam_pool_id = self._get_param("IpamPoolId")
        netmask_length = int(self._get_param("NetmaskLength", "24"))
        pool_id, cidr = self.ec2_backend.provision_public_ipv4_pool_cidr(
            pool_id=pool_id,
            ipam_pool_id=ipam_pool_id,
            netmask_length=netmask_length,
        )
        result = {
            "PoolId": pool_id,
            "PoolAddressRange": {"Cidr": cidr},
        }
        return ActionResult(result)

    def deprovision_public_ipv4_pool_cidr(self) -> ActionResult:
        pool_id = self._get_param("PoolId")
        cidr = self._get_param("Cidr")
        pool_id, cidr = self.ec2_backend.deprovision_public_ipv4_pool_cidr(
            pool_id=pool_id,
            cidr=cidr,
        )
        result = {
            "PoolId": pool_id,
            "DeprovisionedAddressRanges": [cidr],
        }
        return ActionResult(result)


CREATE_PUBLIC_IPV4_POOL = """<CreatePublicIpv4PoolResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
  <requestId>7a62c49f-347e-4fc4-9331-6e8eEXAMPLE</requestId>
  <poolId>{{ pool.id }}</poolId>
</CreatePublicIpv4PoolResponse>"""

DELETE_PUBLIC_IPV4_POOL = """<DeletePublicIpv4PoolResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
  <requestId>7a62c49f-347e-4fc4-9331-6e8eEXAMPLE</requestId>
  <return>true</return>
</DeletePublicIpv4PoolResponse>"""

DESCRIBE_PUBLIC_IPV4_POOLS = """<DescribePublicIpv4PoolsResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
  <requestId>7a62c49f-347e-4fc4-9331-6e8eEXAMPLE</requestId>
  <publicIpv4PoolSet>
    {% for pool in pools %}
    <item>
      <poolId>{{ pool.id }}</poolId>
      <description>{{ pool.description }}</description>
      <totalAddressCount>{{ pool.total_address_count }}</totalAddressCount>
      <totalAvailableAddressCount>{{ pool.total_available_address_count }}</totalAvailableAddressCount>
      <networkBorderGroup>{{ pool.network_border_group }}</networkBorderGroup>
      <poolAddressRangeSet>
        {% for r in pool.pool_address_ranges %}
        <item>
          <cidr>{{ r.cidr }}</cidr>
          <addressCount>{{ r.address_count }}</addressCount>
          <availableAddressCount>{{ r.available_address_count }}</availableAddressCount>
        </item>
        {% endfor %}
      </poolAddressRangeSet>
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
  </publicIpv4PoolSet>
</DescribePublicIpv4PoolsResponse>"""

PROVISION_PUBLIC_IPV4_POOL_CIDR = """<ProvisionPublicIpv4PoolCidrResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
  <requestId>7a62c49f-347e-4fc4-9331-6e8eEXAMPLE</requestId>
  <poolId>{{ pool_id }}</poolId>
  <poolAddressRange>
    <cidr>{{ cidr }}</cidr>
  </poolAddressRange>
</ProvisionPublicIpv4PoolCidrResponse>"""

DEPROVISION_PUBLIC_IPV4_POOL_CIDR = """<DeprovisionPublicIpv4PoolCidrResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
  <requestId>7a62c49f-347e-4fc4-9331-6e8eEXAMPLE</requestId>
  <poolId>{{ pool_id }}</poolId>
  <deprovisionedAddressRanges>
    <item>{{ cidr }}</item>
  </deprovisionedAddressRanges>
</DeprovisionPublicIpv4PoolCidrResponse>"""
