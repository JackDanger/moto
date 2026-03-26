from moto.core.responses import ActionResult
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

    def modify_ipam(self) -> str:
        ipam_id = self._get_param("IpamId")
        description = self._get_param("Description")
        add_regions = self._get_param("AddOperatingRegion", [])
        if add_regions:
            add_regions = [r.get("RegionName", r) for r in add_regions]
        remove_regions = self._get_param("RemoveOperatingRegion", [])
        if remove_regions:
            remove_regions = [r.get("RegionName", r) for r in remove_regions]
        ipam = self.ec2_backend.modify_ipam(
            ipam_id=ipam_id,
            description=description,
            add_operating_regions=add_regions or None,
            remove_operating_regions=remove_regions or None,
        )
        template = self.response_template(MODIFY_IPAM)
        return template.render(ipam=ipam)

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

    def modify_ipam_pool(self) -> str:
        ipam_pool_id = self._get_param("IpamPoolId")
        description = self._get_param("Description")
        auto_import_str = self._get_param("AutoImport")
        auto_import = str2bool(auto_import_str) if auto_import_str else None
        alloc_min = self._get_param("AllocationMinNetmaskLength")
        alloc_max = self._get_param("AllocationMaxNetmaskLength")
        alloc_default = self._get_param("AllocationDefaultNetmaskLength")
        pool = self.ec2_backend.modify_ipam_pool(
            ipam_pool_id=ipam_pool_id,
            description=description,
            auto_import=auto_import,
            allocation_min_netmask_length=int(alloc_min) if alloc_min else None,
            allocation_max_netmask_length=int(alloc_max) if alloc_max else None,
            allocation_default_netmask_length=int(alloc_default) if alloc_default else None,
        )
        template = self.response_template(MODIFY_IPAM_POOL)
        return template.render(pool=pool)

    def delete_ipam_pool(self) -> str:
        ipam_pool_id = self._get_param("IpamPoolId")
        pool = self.ec2_backend.delete_ipam_pool(ipam_pool_id)
        template = self.response_template(DELETE_IPAM_POOL)
        return template.render(pool=pool)

    def provision_ipam_pool_cidr(self) -> str:
        ipam_pool_id = self._get_param("IpamPoolId")
        cidr = self._get_param("Cidr")
        pool_cidr = self.ec2_backend.provision_ipam_pool_cidr(
            ipam_pool_id=ipam_pool_id,
            cidr=cidr,
        )
        template = self.response_template(PROVISION_IPAM_POOL_CIDR)
        return template.render(pool_cidr=pool_cidr)

    def deprovision_ipam_pool_cidr(self) -> str:
        ipam_pool_id = self._get_param("IpamPoolId")
        cidr = self._get_param("Cidr")
        pool_cidr = self.ec2_backend.deprovision_ipam_pool_cidr(
            ipam_pool_id=ipam_pool_id,
            cidr=cidr,
        )
        template = self.response_template(DEPROVISION_IPAM_POOL_CIDR)
        return template.render(pool_cidr=pool_cidr)

    def allocate_ipam_pool_cidr(self) -> str:
        ipam_pool_id = self._get_param("IpamPoolId")
        cidr = self._get_param("Cidr")
        netmask_length = self._get_param("NetmaskLength")
        description = self._get_param("Description", "")
        allocation = self.ec2_backend.allocate_ipam_pool_cidr(
            ipam_pool_id=ipam_pool_id,
            cidr=cidr,
            netmask_length=int(netmask_length) if netmask_length else None,
            description=description,
        )
        template = self.response_template(ALLOCATE_IPAM_POOL_CIDR)
        return template.render(allocation=allocation)

    def release_ipam_pool_allocation(self) -> str:
        ipam_pool_id = self._get_param("IpamPoolId")
        ipam_pool_allocation_id = self._get_param("IpamPoolAllocationId")
        cidr = self._get_param("Cidr")
        self.ec2_backend.release_ipam_pool_allocation(
            ipam_pool_id=ipam_pool_id,
            ipam_pool_allocation_id=ipam_pool_allocation_id,
            cidr=cidr,
        )
        template = self.response_template(RELEASE_IPAM_POOL_ALLOCATION)
        return template.render()

    def create_ipam_scope(self) -> str:
        ipam_id = self._get_param("IpamId")
        description = self._get_param("Description", "")
        tags = add_tag_specification(self._get_param("TagSpecifications", []))
        scope = self.ec2_backend.create_ipam_scope(
            ipam_id=ipam_id,
            description=description,
            tags=tags,
        )
        template = self.response_template(CREATE_IPAM_SCOPE)
        return template.render(scope=scope)

    def delete_ipam_scope(self) -> str:
        ipam_scope_id = self._get_param("IpamScopeId")
        scope = self.ec2_backend.delete_ipam_scope(ipam_scope_id)
        template = self.response_template(DELETE_IPAM_SCOPE)
        return template.render(scope=scope)

    def describe_ipam_scopes(self) -> str:
        ipam_scope_ids = self._get_param("IpamScopeId", [])
        scopes = self.ec2_backend.describe_ipam_scopes(
            ipam_scope_ids=ipam_scope_ids or None,
        )
        template = self.response_template(DESCRIBE_IPAM_SCOPES)
        return template.render(scopes=scopes)

    def get_ipam_pool_allocations(self) -> str:
        ipam_pool_id = self._get_param("IpamPoolId")
        ipam_pool_allocation_id = self._get_param("IpamPoolAllocationId")
        allocations = self.ec2_backend.get_ipam_pool_allocations(
            ipam_pool_id=ipam_pool_id,
            ipam_pool_allocation_id=ipam_pool_allocation_id,
        )
        template = self.response_template(GET_IPAM_POOL_ALLOCATIONS)
        return template.render(allocations=allocations)

    def get_ipam_pool_cidrs(self) -> str:
        ipam_pool_id = self._get_param("IpamPoolId")
        cidrs = self.ec2_backend.get_ipam_pool_cidrs(
            ipam_pool_id=ipam_pool_id,
        )
        template = self.response_template(GET_IPAM_POOL_CIDRS)
        return template.render(cidrs=cidrs)

    def get_ipam_resource_cidrs(self) -> str:
        ipam_pool_id = self._get_param("IpamPoolId")
        ipam_scope_id = self._get_param("IpamScopeId")
        resources = self.ec2_backend.get_ipam_resource_cidrs(
            ipam_pool_id=ipam_pool_id,
            ipam_scope_id=ipam_scope_id,
        )
        template = self.response_template(GET_IPAM_RESOURCE_CIDRS)
        return template.render(resources=resources)

    def disable_ipam_organization_admin_account(self) -> ActionResult:
        delegated_admin_account_id = self._get_param("DelegatedAdminAccountId")
        success = self.ec2_backend.disable_ipam_organization_admin_account(
            delegated_admin_account_id
        )
        return ActionResult({"Success": success})

    def enable_ipam_organization_admin_account(self) -> ActionResult:
        delegated_admin_account_id = self._get_param("DelegatedAdminAccountId")
        success = self.ec2_backend.enable_ipam_organization_admin_account(
            delegated_admin_account_id
        )
        return ActionResult({"Success": success})

    def disassociate_ipam_byoasn(self) -> ActionResult:
        asn = self._get_param("Asn")
        cidr = self._get_param("Cidr")
        result = self.ec2_backend.disassociate_ipam_byoasn(asn=asn, cidr=cidr)
        return ActionResult({"Ipv4IpamByoasn": result})

    def disassociate_ipam_resource_discovery(self) -> ActionResult:
        assoc_id = self._get_param("IpamResourceDiscoveryAssociationId")
        result = self.ec2_backend.disassociate_ipam_resource_discovery(assoc_id)
        return ActionResult({"IpamResourceDiscoveryAssociation": result})


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

MODIFY_IPAM = """<ModifyIpamResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
  <requestId>7a62c49f-347e-4fc4-9331-6e8eEXAMPLE</requestId>
  <ipam>
    <ipamId>{{ ipam.id }}</ipamId>
    <ipamArn>{{ ipam.arn }}</ipamArn>
    <description>{{ ipam.description }}</description>
    <state>{{ ipam.state }}</state>
  </ipam>
</ModifyIpamResponse>"""

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

MODIFY_IPAM_POOL = """<ModifyIpamPoolResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
  <requestId>7a62c49f-347e-4fc4-9331-6e8eEXAMPLE</requestId>
  <ipamPool>
    <ipamPoolId>{{ pool.id }}</ipamPoolId>
    <ipamPoolArn>{{ pool.arn }}</ipamPoolArn>
    <state>{{ pool.state }}</state>
    <description>{{ pool.description }}</description>
  </ipamPool>
</ModifyIpamPoolResponse>"""

DELETE_IPAM_POOL = """<DeleteIpamPoolResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
  <requestId>7a62c49f-347e-4fc4-9331-6e8eEXAMPLE</requestId>
  <ipamPool>
    <ipamPoolId>{{ pool.id }}</ipamPoolId>
    <state>{{ pool.state }}</state>
  </ipamPool>
</DeleteIpamPoolResponse>"""

PROVISION_IPAM_POOL_CIDR = """<ProvisionIpamPoolCidrResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
  <requestId>7a62c49f-347e-4fc4-9331-6e8eEXAMPLE</requestId>
  <ipamPoolCidr>
    <cidr>{{ pool_cidr.cidr }}</cidr>
    <state>{{ pool_cidr.state }}</state>
  </ipamPoolCidr>
</ProvisionIpamPoolCidrResponse>"""

DEPROVISION_IPAM_POOL_CIDR = """<DeprovisionIpamPoolCidrResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
  <requestId>7a62c49f-347e-4fc4-9331-6e8eEXAMPLE</requestId>
  <ipamPoolCidr>
    <cidr>{{ pool_cidr.cidr }}</cidr>
    <state>{{ pool_cidr.state }}</state>
  </ipamPoolCidr>
</DeprovisionIpamPoolCidrResponse>"""

ALLOCATE_IPAM_POOL_CIDR = """<AllocateIpamPoolCidrResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
  <requestId>7a62c49f-347e-4fc4-9331-6e8eEXAMPLE</requestId>
  <ipamPoolAllocation>
    <cidr>{{ allocation.cidr }}</cidr>
    <ipamPoolAllocationId>{{ allocation.ipam_pool_allocation_id }}</ipamPoolAllocationId>
    <resourceType>{{ allocation.resource_type }}</resourceType>
  </ipamPoolAllocation>
</AllocateIpamPoolCidrResponse>"""

RELEASE_IPAM_POOL_ALLOCATION = """<ReleaseIpamPoolAllocationResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
  <requestId>7a62c49f-347e-4fc4-9331-6e8eEXAMPLE</requestId>
  <return>true</return>
</ReleaseIpamPoolAllocationResponse>"""

CREATE_IPAM_SCOPE = """<CreateIpamScopeResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
  <requestId>7a62c49f-347e-4fc4-9331-6e8eEXAMPLE</requestId>
  <ipamScope>
    <ipamScopeId>{{ scope.id }}</ipamScopeId>
    <ipamScopeArn>{{ scope.arn }}</ipamScopeArn>
    <ipamId>{{ scope.ipam_id }}</ipamId>
    <ipamArn>{{ scope.ipam_arn }}</ipamArn>
    <ipamScopeType>{{ scope.scope_type }}</ipamScopeType>
    <isDefault>{{ 'true' if scope.is_default else 'false' }}</isDefault>
    <description>{{ scope.description }}</description>
    <state>{{ scope.state }}</state>
    <poolCount>{{ scope.pool_count }}</poolCount>
    <ownerId>{{ scope.owner_id }}</ownerId>
    <tagSet>
      {% for tag in scope.get_tags() %}
      <item>
        <key>{{ tag.key }}</key>
        <value>{{ tag.value }}</value>
      </item>
      {% endfor %}
    </tagSet>
  </ipamScope>
</CreateIpamScopeResponse>"""

DELETE_IPAM_SCOPE = """<DeleteIpamScopeResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
  <requestId>7a62c49f-347e-4fc4-9331-6e8eEXAMPLE</requestId>
  <ipamScope>
    <ipamScopeId>{{ scope.id }}</ipamScopeId>
    <state>{{ scope.state }}</state>
  </ipamScope>
</DeleteIpamScopeResponse>"""

DESCRIBE_IPAM_SCOPES = """<DescribeIpamScopesResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
  <requestId>7a62c49f-347e-4fc4-9331-6e8eEXAMPLE</requestId>
  <ipamScopeSet>
    {% for scope in scopes %}
    <item>
      <ipamScopeId>{{ scope.id }}</ipamScopeId>
      <ipamScopeArn>{{ scope.arn }}</ipamScopeArn>
      <ipamId>{{ scope.ipam_id }}</ipamId>
      <ipamScopeType>{{ scope.scope_type }}</ipamScopeType>
      <isDefault>{{ 'true' if scope.is_default else 'false' }}</isDefault>
      <description>{{ scope.description }}</description>
      <state>{{ scope.state }}</state>
      <poolCount>{{ scope.pool_count }}</poolCount>
      <ownerId>{{ scope.owner_id }}</ownerId>
    </item>
    {% endfor %}
  </ipamScopeSet>
</DescribeIpamScopesResponse>"""

GET_IPAM_POOL_ALLOCATIONS = """<GetIpamPoolAllocationsResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
  <requestId>7a62c49f-347e-4fc4-9331-6e8eEXAMPLE</requestId>
  <ipamPoolAllocationSet>
    {% for alloc in allocations %}
    <item>
      <cidr>{{ alloc.cidr }}</cidr>
      <ipamPoolAllocationId>{{ alloc.ipam_pool_allocation_id }}</ipamPoolAllocationId>
      <resourceType>{{ alloc.resource_type }}</resourceType>
      <description>{{ alloc.description }}</description>
    </item>
    {% endfor %}
  </ipamPoolAllocationSet>
</GetIpamPoolAllocationsResponse>"""

GET_IPAM_POOL_CIDRS = """<GetIpamPoolCidrsResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
  <requestId>7a62c49f-347e-4fc4-9331-6e8eEXAMPLE</requestId>
  <ipamPoolCidrSet>
    {% for cidr_obj in cidrs %}
    <item>
      <cidr>{{ cidr_obj.cidr }}</cidr>
      <state>{{ cidr_obj.state }}</state>
    </item>
    {% endfor %}
  </ipamPoolCidrSet>
</GetIpamPoolCidrsResponse>"""

GET_IPAM_RESOURCE_CIDRS = """<GetIpamResourceCidrsResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
  <requestId>7a62c49f-347e-4fc4-9331-6e8eEXAMPLE</requestId>
  <ipamResourceCidrSet>
    {% for res in resources %}
    <item>
      <ipamPoolId>{{ res.ipam_pool_id }}</ipamPoolId>
      <resourceCidr>{{ res.resource_cidr }}</resourceCidr>
      <resourceType>{{ res.resource_type }}</resourceType>
      <resourceRegion>{{ res.resource_region }}</resourceRegion>
      <complianceStatus>{{ res.compliance_status }}</complianceStatus>
      <overlapStatus>{{ res.overlap_status }}</overlapStatus>
      <managementState>{{ res.management_state }}</managementState>
    </item>
    {% endfor %}
  </ipamResourceCidrSet>
</GetIpamResourceCidrsResponse>"""
