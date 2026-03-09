from moto.ec2.utils import add_tag_specification
from moto.utilities.utils import str2bool

from ._base_response import EC2BaseResponse


class IpamResponse(EC2BaseResponse):
    def create_ipam(self) -> str:
        description = self._get_param("Description", "")
        operating_regions = self._get_param("OperatingRegions", [])
        if operating_regions:
            operating_regions = [r.get("RegionName", r) for r in operating_regions]
        tier = self._get_param("Tier", "advanced")
        tags = add_tag_specification(self._get_param("TagSpecifications", []))

        ipam = self.ec2_backend.create_ipam(
            description=description,
            operating_regions=operating_regions or None,
            tier=tier,
            tags=tags,
        )
        template = self.response_template(CREATE_IPAM)
        return template.render(ipam=ipam)

    def describe_ipams(self) -> str:
        ipam_ids = self._get_param("IpamIds", [])
        ipams = self.ec2_backend.describe_ipams(
            ipam_ids=ipam_ids or None,
        )
        template = self.response_template(DESCRIBE_IPAMS)
        return template.render(ipams=ipams)

    def delete_ipam(self) -> str:
        ipam_id = self._get_param("IpamId")
        ipam = self.ec2_backend.delete_ipam(ipam_id)
        template = self.response_template(DELETE_IPAM)
        return template.render(ipam=ipam)

    def create_ipam_pool(self) -> str:
        ipam_scope_id = self._get_param("IpamScopeId")
        address_family = self._get_param("AddressFamily", "ipv4")
        locale = self._get_param("Locale")
        description = self._get_param("Description", "")
        auto_import = str2bool(self._get_param("AutoImport", "false"))
        publicly_advertisable = str2bool(
            self._get_param("PubliclyAdvertisable", "false")
        )
        allocation_min = int(
            self._get_param("AllocationMinNetmaskLength", "0")
        )
        allocation_max = int(
            self._get_param("AllocationMaxNetmaskLength", "32")
        )
        allocation_default = int(
            self._get_param("AllocationDefaultNetmaskLength", "0")
        )
        source_ipam_pool_id = self._get_param("SourceIpamPoolId")
        tags = add_tag_specification(self._get_param("TagSpecifications", []))

        pool = self.ec2_backend.create_ipam_pool(
            ipam_scope_id=ipam_scope_id,
            address_family=address_family,
            locale=locale,
            description=description,
            auto_import=auto_import,
            publicly_advertisable=publicly_advertisable,
            allocation_min_netmask_length=allocation_min,
            allocation_max_netmask_length=allocation_max,
            allocation_default_netmask_length=allocation_default,
            source_ipam_pool_id=source_ipam_pool_id,
            tags=tags,
        )
        template = self.response_template(CREATE_IPAM_POOL)
        return template.render(pool=pool)

    def describe_ipam_pools(self) -> str:
        ipam_pool_ids = self._get_param("IpamPoolIds", [])
        pools = self.ec2_backend.describe_ipam_pools(
            ipam_pool_ids=ipam_pool_ids or None,
        )
        template = self.response_template(DESCRIBE_IPAM_POOLS)
        return template.render(pools=pools)


CREATE_IPAM = """<CreateIpamResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
  <requestId>7a62c49f-347e-4fc4-9331-6e8eEXAMPLE</requestId>
  <ipam>
    <ipamId>{{ ipam.id }}</ipamId>
    <ipamArn>{{ ipam.arn }}</ipamArn>
    <ipamRegion>{{ ipam.ec2_backend.region_name }}</ipamRegion>
    <description>{{ ipam.description }}</description>
    <publicDefaultScopeId>{{ ipam.public_default_scope_id }}</publicDefaultScopeId>
    <privateDefaultScopeId>{{ ipam.private_default_scope_id }}</privateDefaultScopeId>
    <scopeCount>{{ ipam.scope_count }}</scopeCount>
    <operatingRegionSet>
      {% for region in ipam.operating_regions %}
      <item>
        <regionName>{{ region }}</regionName>
      </item>
      {% endfor %}
    </operatingRegionSet>
    <state>{{ ipam.state }}</state>
    <ownerId>{{ ipam.owner_id }}</ownerId>
    <tier>{{ ipam.tier }}</tier>
    <tagSet>
      {% for tag in ipam.get_tags() %}
      <item>
        <key>{{ tag.key }}</key>
        <value>{{ tag.value }}</value>
      </item>
      {% endfor %}
    </tagSet>
  </ipam>
</CreateIpamResponse>"""


DESCRIBE_IPAMS = """<DescribeIpamsResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
  <requestId>7a62c49f-347e-4fc4-9331-6e8eEXAMPLE</requestId>
  <ipamSet>
    {% for ipam in ipams %}
    <item>
      <ipamId>{{ ipam.id }}</ipamId>
      <ipamArn>{{ ipam.arn }}</ipamArn>
      <ipamRegion>{{ ipam.ec2_backend.region_name }}</ipamRegion>
      <description>{{ ipam.description }}</description>
      <publicDefaultScopeId>{{ ipam.public_default_scope_id }}</publicDefaultScopeId>
      <privateDefaultScopeId>{{ ipam.private_default_scope_id }}</privateDefaultScopeId>
      <scopeCount>{{ ipam.scope_count }}</scopeCount>
      <operatingRegionSet>
        {% for region in ipam.operating_regions %}
        <item>
          <regionName>{{ region }}</regionName>
        </item>
        {% endfor %}
      </operatingRegionSet>
      <state>{{ ipam.state }}</state>
      <ownerId>{{ ipam.owner_id }}</ownerId>
      <tier>{{ ipam.tier }}</tier>
      <tagSet>
        {% for tag in ipam.get_tags() %}
        <item>
          <key>{{ tag.key }}</key>
          <value>{{ tag.value }}</value>
        </item>
        {% endfor %}
      </tagSet>
    </item>
    {% endfor %}
  </ipamSet>
</DescribeIpamsResponse>"""


DELETE_IPAM = """<DeleteIpamResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
  <requestId>7a62c49f-347e-4fc4-9331-6e8eEXAMPLE</requestId>
  <ipam>
    <ipamId>{{ ipam.id }}</ipamId>
    <ipamArn>{{ ipam.arn }}</ipamArn>
    <state>{{ ipam.state }}</state>
  </ipam>
</DeleteIpamResponse>"""


CREATE_IPAM_POOL = """<CreateIpamPoolResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
  <requestId>7a62c49f-347e-4fc4-9331-6e8eEXAMPLE</requestId>
  <ipamPool>
    <ipamPoolId>{{ pool.id }}</ipamPoolId>
    <ipamPoolArn>{{ pool.arn }}</ipamPoolArn>
    <ipamScopeId>{{ pool.ipam_scope_id }}</ipamScopeId>
    <addressFamily>{{ pool.address_family }}</addressFamily>
    <locale>{{ pool.locale }}</locale>
    <description>{{ pool.description }}</description>
    <autoImport>{{ 'true' if pool.auto_import else 'false' }}</autoImport>
    <publiclyAdvertisable>{{ 'true' if pool.publicly_advertisable else 'false' }}</publiclyAdvertisable>
    <allocationMinNetmaskLength>{{ pool.allocation_min_netmask_length }}</allocationMinNetmaskLength>
    <allocationMaxNetmaskLength>{{ pool.allocation_max_netmask_length }}</allocationMaxNetmaskLength>
    <allocationDefaultNetmaskLength>{{ pool.allocation_default_netmask_length }}</allocationDefaultNetmaskLength>
    <poolDepth>{{ pool.pool_depth }}</poolDepth>
    <state>{{ pool.state }}</state>
    {% if pool.source_ipam_pool_id %}
    <sourceIpamPoolId>{{ pool.source_ipam_pool_id }}</sourceIpamPoolId>
    {% endif %}
    <tagSet>
      {% for tag in pool.get_tags() %}
      <item>
        <key>{{ tag.key }}</key>
        <value>{{ tag.value }}</value>
      </item>
      {% endfor %}
    </tagSet>
  </ipamPool>
</CreateIpamPoolResponse>"""


DESCRIBE_IPAM_POOLS = """<DescribeIpamPoolsResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
  <requestId>7a62c49f-347e-4fc4-9331-6e8eEXAMPLE</requestId>
  <ipamPoolSet>
    {% for pool in pools %}
    <item>
      <ipamPoolId>{{ pool.id }}</ipamPoolId>
      <ipamPoolArn>{{ pool.arn }}</ipamPoolArn>
      <ipamScopeId>{{ pool.ipam_scope_id }}</ipamScopeId>
      <addressFamily>{{ pool.address_family }}</addressFamily>
      <locale>{{ pool.locale }}</locale>
      <description>{{ pool.description }}</description>
      <autoImport>{{ 'true' if pool.auto_import else 'false' }}</autoImport>
      <publiclyAdvertisable>{{ 'true' if pool.publicly_advertisable else 'false' }}</publiclyAdvertisable>
      <allocationMinNetmaskLength>{{ pool.allocation_min_netmask_length }}</allocationMinNetmaskLength>
      <allocationMaxNetmaskLength>{{ pool.allocation_max_netmask_length }}</allocationMaxNetmaskLength>
      <allocationDefaultNetmaskLength>{{ pool.allocation_default_netmask_length }}</allocationDefaultNetmaskLength>
      <poolDepth>{{ pool.pool_depth }}</poolDepth>
      <state>{{ pool.state }}</state>
      {% if pool.source_ipam_pool_id %}
      <sourceIpamPoolId>{{ pool.source_ipam_pool_id }}</sourceIpamPoolId>
      {% endif %}
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
  </ipamPoolSet>
</DescribeIpamPoolsResponse>"""
