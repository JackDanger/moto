from moto.core.responses import ActionResult
from moto.ec2.utils import add_tag_specification
from moto.utilities.utils import str2bool

from ._base_response import EC2BaseResponse


class IpamResponse(EC2BaseResponse):
    def create_ipam(self) -> ActionResult:
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
        return ActionResult({"Ipam": ipam})

    def describe_ipams(self) -> ActionResult:
        ipam_ids = self._get_param("IpamIds", [])
        ipams = self.ec2_backend.describe_ipams(
            ipam_ids=ipam_ids or None,
        )
        return ActionResult({"Ipams": ipams})

    def modify_ipam(self) -> ActionResult:
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
        return ActionResult({"Ipam": ipam})

    def delete_ipam(self) -> ActionResult:
        ipam_id = self._get_param("IpamId")
        ipam = self.ec2_backend.delete_ipam(ipam_id)
        return ActionResult({"Ipam": ipam})

    def create_ipam_pool(self) -> ActionResult:
        ipam_scope_id = self._get_param("IpamScopeId")
        address_family = self._get_param("AddressFamily", "ipv4")
        locale = self._get_param("Locale")
        description = self._get_param("Description", "")
        auto_import = str2bool(self._get_param("AutoImport", "false"))
        publicly_advertisable = str2bool(
            self._get_param("PubliclyAdvertisable", "false")
        )
        allocation_min = int(self._get_param("AllocationMinNetmaskLength", "0"))
        allocation_max = int(self._get_param("AllocationMaxNetmaskLength", "32"))
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
        pool_dict = {
            "IpamPoolId": pool.id,
            "IpamPoolArn": pool.arn,
            "IpamScopeId": pool.ipam_scope_id,
            "AddressFamily": pool.address_family,
            "Locale": pool.locale,
            "Description": pool.description,
            "AutoImport": pool.auto_import,
            "PubliclyAdvertisable": pool.publicly_advertisable,
            "AllocationMinNetmaskLength": pool.allocation_min_netmask_length,
            "AllocationMaxNetmaskLength": pool.allocation_max_netmask_length,
            "AllocationDefaultNetmaskLength": pool.allocation_default_netmask_length,
            "PoolDepth": pool.pool_depth,
            "State": pool.state,
            "Tags": [{"Key": tag.key, "Value": tag.value} for tag in pool.get_tags()],
        }
        if pool.source_ipam_pool_id:
            pool_dict["SourceIpamPoolId"] = pool.source_ipam_pool_id
        result = {"IpamPool": pool_dict}
        return ActionResult(result)

    def describe_ipam_pools(self) -> ActionResult:
        ipam_pool_ids = self._get_param("IpamPoolIds", [])
        pools = self.ec2_backend.describe_ipam_pools(
            ipam_pool_ids=ipam_pool_ids or None,
        )
        result = {
            "IpamPools": [
                {
                    "IpamPoolId": pool.id,
                    "IpamPoolArn": pool.arn,
                    "IpamScopeId": pool.ipam_scope_id,
                    "AddressFamily": pool.address_family,
                    "Locale": pool.locale,
                    "Description": pool.description,
                    "AutoImport": pool.auto_import,
                    "PubliclyAdvertisable": pool.publicly_advertisable,
                    "AllocationMinNetmaskLength": pool.allocation_min_netmask_length,
                    "AllocationMaxNetmaskLength": pool.allocation_max_netmask_length,
                    "AllocationDefaultNetmaskLength": pool.allocation_default_netmask_length,
                    "PoolDepth": pool.pool_depth,
                    "State": pool.state,
                    "Tags": [
                        {"Key": tag.key, "Value": tag.value} for tag in pool.get_tags()
                    ],
                    **(
                        {"SourceIpamPoolId": pool.source_ipam_pool_id}
                        if pool.source_ipam_pool_id
                        else {}
                    ),
                }
                for pool in pools
            ]
        }
        return ActionResult(result)

    def modify_ipam_pool(self) -> ActionResult:
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
        result = {
            "IpamPool": {
                "IpamPoolId": pool.id,
                "IpamPoolArn": pool.arn,
                "State": pool.state,
                "Description": pool.description,
            }
        }
        return ActionResult(result)

    def delete_ipam_pool(self) -> ActionResult:
        ipam_pool_id = self._get_param("IpamPoolId")
        pool = self.ec2_backend.delete_ipam_pool(ipam_pool_id)
        result = {
            "IpamPool": {
                "IpamPoolId": pool.id,
                "State": pool.state,
            }
        }
        return ActionResult(result)

    def provision_ipam_pool_cidr(self) -> ActionResult:
        ipam_pool_id = self._get_param("IpamPoolId")
        cidr = self._get_param("Cidr")
        pool_cidr = self.ec2_backend.provision_ipam_pool_cidr(
            ipam_pool_id=ipam_pool_id,
            cidr=cidr,
        )
        result = {
            "IpamPoolCidr": {
                "Cidr": pool_cidr.cidr,
                "State": pool_cidr.state,
            }
        }
        return ActionResult(result)

    def deprovision_ipam_pool_cidr(self) -> ActionResult:
        ipam_pool_id = self._get_param("IpamPoolId")
        cidr = self._get_param("Cidr")
        pool_cidr = self.ec2_backend.deprovision_ipam_pool_cidr(
            ipam_pool_id=ipam_pool_id,
            cidr=cidr,
        )
        result = {
            "IpamPoolCidr": {
                "Cidr": pool_cidr.cidr,
                "State": pool_cidr.state,
            }
        }
        return ActionResult(result)

    def allocate_ipam_pool_cidr(self) -> ActionResult:
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
        result = {
            "IpamPoolAllocation": {
                "Cidr": allocation.cidr,
                "IpamPoolAllocationId": allocation.ipam_pool_allocation_id,
                "ResourceType": allocation.resource_type,
            }
        }
        return ActionResult(result)

    def release_ipam_pool_allocation(self) -> ActionResult:
        ipam_pool_id = self._get_param("IpamPoolId")
        ipam_pool_allocation_id = self._get_param("IpamPoolAllocationId")
        cidr = self._get_param("Cidr")
        self.ec2_backend.release_ipam_pool_allocation(
            ipam_pool_id=ipam_pool_id,
            ipam_pool_allocation_id=ipam_pool_allocation_id,
            cidr=cidr,
        )
        result = {"Return": True}
        return ActionResult(result)

    def create_ipam_scope(self) -> ActionResult:
        ipam_id = self._get_param("IpamId")
        description = self._get_param("Description", "")
        tags = add_tag_specification(self._get_param("TagSpecifications", []))
        scope = self.ec2_backend.create_ipam_scope(
            ipam_id=ipam_id,
            description=description,
            tags=tags,
        )
        result = {
            "IpamScope": {
                "IpamScopeId": scope.id,
                "IpamScopeArn": scope.arn,
                "IpamId": scope.ipam_id,
                "IpamArn": scope.ipam_arn,
                "IpamScopeType": scope.scope_type,
                "IsDefault": scope.is_default,
                "Description": scope.description,
                "State": scope.state,
                "PoolCount": scope.pool_count,
                "OwnerId": scope.owner_id,
                "Tags": [{"Key": tag.key, "Value": tag.value} for tag in scope.get_tags()],
            }
        }
        return ActionResult(result)

    def delete_ipam_scope(self) -> ActionResult:
        ipam_scope_id = self._get_param("IpamScopeId")
        scope = self.ec2_backend.delete_ipam_scope(ipam_scope_id)
        result = {
            "IpamScope": {
                "IpamScopeId": scope.id,
                "State": scope.state,
            }
        }
        return ActionResult(result)

    def describe_ipam_scopes(self) -> ActionResult:
        ipam_scope_ids = self._get_param("IpamScopeId", [])
        scopes = self.ec2_backend.describe_ipam_scopes(
            ipam_scope_ids=ipam_scope_ids or None,
        )
        result = {
            "IpamScopes": [
                {
                    "IpamScopeId": scope.id,
                    "IpamScopeArn": scope.arn,
                    "IpamId": scope.ipam_id,
                    "IpamScopeType": scope.scope_type,
                    "IsDefault": scope.is_default,
                    "Description": scope.description,
                    "State": scope.state,
                    "PoolCount": scope.pool_count,
                    "OwnerId": scope.owner_id,
                }
                for scope in scopes
            ]
        }
        return ActionResult(result)

    def get_ipam_pool_allocations(self) -> ActionResult:
        ipam_pool_id = self._get_param("IpamPoolId")
        ipam_pool_allocation_id = self._get_param("IpamPoolAllocationId")
        allocations = self.ec2_backend.get_ipam_pool_allocations(
            ipam_pool_id=ipam_pool_id,
            ipam_pool_allocation_id=ipam_pool_allocation_id,
        )
        result = {
            "IpamPoolAllocations": [
                {
                    "Cidr": alloc.cidr,
                    "IpamPoolAllocationId": alloc.ipam_pool_allocation_id,
                    "ResourceType": alloc.resource_type,
                    "Description": alloc.description,
                }
                for alloc in allocations
            ]
        }
        return ActionResult(result)

    def get_ipam_pool_cidrs(self) -> ActionResult:
        ipam_pool_id = self._get_param("IpamPoolId")
        cidrs = self.ec2_backend.get_ipam_pool_cidrs(
            ipam_pool_id=ipam_pool_id,
        )
        result = {
            "IpamPoolCidrs": [
                {
                    "Cidr": cidr_obj.cidr,
                    "State": cidr_obj.state,
                }
                for cidr_obj in cidrs
            ]
        }
        return ActionResult(result)

    def get_ipam_resource_cidrs(self) -> ActionResult:
        ipam_pool_id = self._get_param("IpamPoolId")
        ipam_scope_id = self._get_param("IpamScopeId")
        resources = self.ec2_backend.get_ipam_resource_cidrs(
            ipam_pool_id=ipam_pool_id,
            ipam_scope_id=ipam_scope_id,
        )
        result = {
            "IpamResourceCidrs": [
                {
                    "IpamPoolId": res.ipam_pool_id,
                    "ResourceCidr": res.resource_cidr,
                    "ResourceType": res.resource_type,
                    "ResourceRegion": res.resource_region,
                    "ComplianceStatus": res.compliance_status,
                    "OverlapStatus": res.overlap_status,
                    "ManagementState": res.management_state,
                }
                for res in resources
            ]
        }
        return ActionResult(result)

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
