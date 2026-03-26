import random as _random
from typing import Any, Optional

from moto.core.utils import iso_8601_datetime_with_milliseconds, utcnow

from ..utils import (
    random_ipam_id,
    random_ipam_pool_allocation_id,
    random_ipam_pool_cidr_id,
    random_ipam_pool_id,
    random_ipam_scope_id,
)
from .core import TaggedEC2Resource


class IpamScope(TaggedEC2Resource):
    def __init__(
        self,
        ec2_backend: Any,
        ipam_id: str,
        scope_type: str = "private",
        is_default: bool = False,
        description: str = "",
        tags: Optional[dict[str, str]] = None,
    ):
        self.ec2_backend = ec2_backend
        self.id = random_ipam_scope_id()
        self.ipam_id = ipam_id
        self.scope_type = scope_type
        self.is_default = is_default
        self.description = description
        self.state = "create-complete"
        self.pool_count = 0
        self.add_tags(tags or {})

    @property
    def owner_id(self) -> str:
        return self.ec2_backend.account_id

    @property
    def ipam_arn(self) -> str:
        return (
            f"arn:{self.ec2_backend.partition}:ec2:{self.ec2_backend.region_name}"
            f":{self.ec2_backend.account_id}:ipam/{self.ipam_id}"
        )

    @property
    def arn(self) -> str:
        return (
            f"arn:{self.ec2_backend.partition}:ec2:{self.ec2_backend.region_name}"
            f":{self.ec2_backend.account_id}:ipam-scope/{self.id}"
        )


class IpamPoolCidr:
    def __init__(
        self,
        cidr: str,
        ipam_pool_id: str,
    ):
        self.id = random_ipam_pool_cidr_id()
        self.cidr = cidr
        self.ipam_pool_id = ipam_pool_id
        self.state = "provisioned"


class IpamPoolAllocation:
    def __init__(
        self,
        cidr: str,
        ipam_pool_allocation_id: str,
        description: str = "",
    ):
        self.cidr = cidr
        self.ipam_pool_allocation_id = ipam_pool_allocation_id
        self.description = description
        self.resource_type = "custom"
        self.resource_id = ""
        self.resource_region = ""
        self.resource_owner = ""


class Ipam(TaggedEC2Resource):
    def __init__(
        self,
        ec2_backend: Any,
        ipam_id: str,
        description: str = "",
        operating_regions: Optional[list[str]] = None,
        tier: str = "advanced",
        tags: Optional[dict[str, str]] = None,
    ):
        self.ec2_backend = ec2_backend
        self.id = ipam_id
        self.description = description
        self.operating_regions = operating_regions or [ec2_backend.region_name]
        self.tier = tier
        self.state = "create-complete"
        self._created_at = utcnow()

        # Create default scopes
        self.private_default_scope = IpamScope(
            ec2_backend, self.id, scope_type="private", is_default=True
        )
        self.public_default_scope = IpamScope(
            ec2_backend, self.id, scope_type="public", is_default=True
        )
        self.scope_count = 2

        self.add_tags(tags or {})

    @property
    def creation_time(self) -> str:
        return iso_8601_datetime_with_milliseconds(self._created_at)

    @property
    def owner_id(self) -> str:
        return self.ec2_backend.account_id

    @property
    def arn(self) -> str:
        return (
            f"arn:{self.ec2_backend.partition}:ec2:{self.ec2_backend.region_name}"
            f":{self.ec2_backend.account_id}:ipam/{self.id}"
        )

    @property
    def private_default_scope_id(self) -> str:
        return self.private_default_scope.id

    @property
    def public_default_scope_id(self) -> str:
        return self.public_default_scope.id


class IpamPool(TaggedEC2Resource):
    def __init__(
        self,
        ec2_backend: Any,
        ipam_pool_id: str,
        ipam_scope_id: str,
        address_family: str = "ipv4",
        locale: Optional[str] = None,
        description: str = "",
        auto_import: bool = False,
        publicly_advertisable: bool = False,
        allocation_min_netmask_length: int = 0,
        allocation_max_netmask_length: int = 32,
        allocation_default_netmask_length: int = 0,
        source_ipam_pool_id: Optional[str] = None,
        tags: Optional[dict[str, str]] = None,
    ):
        self.ec2_backend = ec2_backend
        self.id = ipam_pool_id
        self.ipam_scope_id = ipam_scope_id
        self.address_family = address_family
        self.locale = locale or ec2_backend.region_name
        self.description = description
        self.auto_import = auto_import
        self.publicly_advertisable = publicly_advertisable
        self.allocation_min_netmask_length = allocation_min_netmask_length
        self.allocation_max_netmask_length = allocation_max_netmask_length
        self.allocation_default_netmask_length = allocation_default_netmask_length
        self.source_ipam_pool_id = source_ipam_pool_id
        self.state = "create-complete"
        self.pool_depth = 1
        self._created_at = utcnow()
        self.cidrs: list[IpamPoolCidr] = []
        self.allocations: dict[str, IpamPoolAllocation] = {}
        self.add_tags(tags or {})

    @property
    def creation_time(self) -> str:
        return iso_8601_datetime_with_milliseconds(self._created_at)

    @property
    def arn(self) -> str:
        return (
            f"arn:{self.ec2_backend.partition}:ec2:{self.ec2_backend.region_name}"
            f":{self.ec2_backend.account_id}:ipam-pool/{self.id}"
        )


class IpamBackend:
    def __init__(self) -> None:
        self.ipams: dict[str, Ipam] = {}
        self.ipam_pools: dict[str, IpamPool] = {}
        self.ipam_scopes: dict[str, IpamScope] = {}

    def create_ipam(
        self,
        description: str = "",
        operating_regions: Optional[list[str]] = None,
        tier: str = "advanced",
        tags: Optional[dict[str, str]] = None,
    ) -> Ipam:
        ipam_id = random_ipam_id()
        ipam = Ipam(
            self,
            ipam_id=ipam_id,
            description=description,
            operating_regions=operating_regions,
            tier=tier,
            tags=tags,
        )
        self.ipams[ipam.id] = ipam
        # Register default scopes
        self.ipam_scopes[ipam.private_default_scope.id] = ipam.private_default_scope
        self.ipam_scopes[ipam.public_default_scope.id] = ipam.public_default_scope
        return ipam

    def describe_ipams(
        self, ipam_ids: Optional[list[str]] = None
    ) -> list[Ipam]:
        ipams = list(self.ipams.values())
        if ipam_ids:
            ipams = [i for i in ipams if i.id in ipam_ids]
        return ipams

    def modify_ipam(
        self,
        ipam_id: str,
        description: Optional[str] = None,
        add_operating_regions: Optional[list[str]] = None,
        remove_operating_regions: Optional[list[str]] = None,
    ) -> Ipam:
        ipam = self.ipams.get(ipam_id)
        if not ipam:
            from ..exceptions import InvalidIpamIdError

            raise InvalidIpamIdError(ipam_id)
        if description is not None:
            ipam.description = description
        if add_operating_regions:
            for region in add_operating_regions:
                if region not in ipam.operating_regions:
                    ipam.operating_regions.append(region)
        if remove_operating_regions:
            ipam.operating_regions = [
                r for r in ipam.operating_regions if r not in remove_operating_regions
            ]
        return ipam

    def delete_ipam(self, ipam_id: str) -> Ipam:
        ipam = self.ipams.get(ipam_id)
        if not ipam:
            from ..exceptions import InvalidIpamIdError

            raise InvalidIpamIdError(ipam_id)
        ipam.state = "delete-complete"
        return self.ipams.pop(ipam_id)

    def create_ipam_pool(
        self,
        ipam_scope_id: str,
        address_family: str = "ipv4",
        locale: Optional[str] = None,
        description: str = "",
        auto_import: bool = False,
        publicly_advertisable: bool = False,
        allocation_min_netmask_length: int = 0,
        allocation_max_netmask_length: int = 32,
        allocation_default_netmask_length: int = 0,
        source_ipam_pool_id: Optional[str] = None,
        tags: Optional[dict[str, str]] = None,
    ) -> IpamPool:
        ipam_pool_id = random_ipam_pool_id()
        ipam_pool = IpamPool(
            self,
            ipam_pool_id=ipam_pool_id,
            ipam_scope_id=ipam_scope_id,
            address_family=address_family,
            locale=locale,
            description=description,
            auto_import=auto_import,
            publicly_advertisable=publicly_advertisable,
            allocation_min_netmask_length=allocation_min_netmask_length,
            allocation_max_netmask_length=allocation_max_netmask_length,
            allocation_default_netmask_length=allocation_default_netmask_length,
            source_ipam_pool_id=source_ipam_pool_id,
            tags=tags,
        )
        self.ipam_pools[ipam_pool.id] = ipam_pool
        return ipam_pool

    def describe_ipam_pools(
        self, ipam_pool_ids: Optional[list[str]] = None
    ) -> list[IpamPool]:
        pools = list(self.ipam_pools.values())
        if ipam_pool_ids:
            pools = [p for p in pools if p.id in ipam_pool_ids]
        return pools

    def modify_ipam_pool(
        self,
        ipam_pool_id: str,
        description: Optional[str] = None,
        auto_import: Optional[bool] = None,
        allocation_min_netmask_length: Optional[int] = None,
        allocation_max_netmask_length: Optional[int] = None,
        allocation_default_netmask_length: Optional[int] = None,
    ) -> IpamPool:
        pool = self.ipam_pools.get(ipam_pool_id)
        if not pool:
            from ..exceptions import InvalidIpamPoolIdError

            raise InvalidIpamPoolIdError(ipam_pool_id)
        if description is not None:
            pool.description = description
        if auto_import is not None:
            pool.auto_import = auto_import
        if allocation_min_netmask_length is not None:
            pool.allocation_min_netmask_length = allocation_min_netmask_length
        if allocation_max_netmask_length is not None:
            pool.allocation_max_netmask_length = allocation_max_netmask_length
        if allocation_default_netmask_length is not None:
            pool.allocation_default_netmask_length = allocation_default_netmask_length
        return pool

    def delete_ipam_pool(self, ipam_pool_id: str) -> IpamPool:
        pool = self.ipam_pools.get(ipam_pool_id)
        if not pool:
            from ..exceptions import InvalidIpamPoolIdError

            raise InvalidIpamPoolIdError(ipam_pool_id)
        pool.state = "delete-complete"
        return self.ipam_pools.pop(ipam_pool_id)

    def provision_ipam_pool_cidr(
        self,
        ipam_pool_id: str,
        cidr: str,
    ) -> IpamPoolCidr:
        pool = self.ipam_pools.get(ipam_pool_id)
        if not pool:
            from ..exceptions import InvalidIpamPoolIdError

            raise InvalidIpamPoolIdError(ipam_pool_id)
        pool_cidr = IpamPoolCidr(cidr=cidr, ipam_pool_id=ipam_pool_id)
        pool.cidrs.append(pool_cidr)
        return pool_cidr

    def deprovision_ipam_pool_cidr(
        self,
        ipam_pool_id: str,
        cidr: str,
    ) -> IpamPoolCidr:
        pool = self.ipam_pools.get(ipam_pool_id)
        if not pool:
            from ..exceptions import InvalidIpamPoolIdError

            raise InvalidIpamPoolIdError(ipam_pool_id)
        for pc in pool.cidrs:
            if pc.cidr == cidr:
                pc.state = "deprovisioned"
                pool.cidrs.remove(pc)
                return pc
        # Return synthetic result
        pc = IpamPoolCidr(cidr=cidr, ipam_pool_id=ipam_pool_id)
        pc.state = "deprovisioned"
        return pc

    def allocate_ipam_pool_cidr(
        self,
        ipam_pool_id: str,
        cidr: Optional[str] = None,
        netmask_length: Optional[int] = None,
        description: str = "",
    ) -> IpamPoolAllocation:
        pool = self.ipam_pools.get(ipam_pool_id)
        if not pool:
            from ..exceptions import InvalidIpamPoolIdError

            raise InvalidIpamPoolIdError(ipam_pool_id)
        if not cidr and netmask_length:
            # Generate a CIDR from the pool
            base = _random.randint(1, 254)
            cidr = f"10.{base}.0.0/{netmask_length}"
        elif not cidr:
            cidr = "10.0.0.0/24"
        alloc_id = random_ipam_pool_allocation_id()
        allocation = IpamPoolAllocation(
            cidr=cidr,
            ipam_pool_allocation_id=alloc_id,
            description=description,
        )
        pool.allocations[alloc_id] = allocation
        return allocation

    def release_ipam_pool_allocation(
        self,
        ipam_pool_id: str,
        ipam_pool_allocation_id: str,
        cidr: str,
    ) -> None:
        pool = self.ipam_pools.get(ipam_pool_id)
        if not pool:
            from ..exceptions import InvalidIpamPoolIdError

            raise InvalidIpamPoolIdError(ipam_pool_id)
        pool.allocations.pop(ipam_pool_allocation_id, None)

    def create_ipam_scope(
        self,
        ipam_id: str,
        description: str = "",
        tags: Optional[dict[str, str]] = None,
    ) -> IpamScope:
        ipam = self.ipams.get(ipam_id)
        if not ipam:
            from ..exceptions import InvalidIpamIdError

            raise InvalidIpamIdError(ipam_id)
        scope = IpamScope(
            self,
            ipam_id=ipam_id,
            scope_type="private",
            is_default=False,
            description=description,
            tags=tags,
        )
        self.ipam_scopes[scope.id] = scope
        ipam.scope_count += 1
        return scope

    def delete_ipam_scope(self, ipam_scope_id: str) -> IpamScope:
        scope = self.ipam_scopes.get(ipam_scope_id)
        if not scope:
            from ..exceptions import InvalidIpamScopeIdError

            raise InvalidIpamScopeIdError(ipam_scope_id)
        if scope.is_default:
            from ..exceptions import InvalidInputError

            raise InvalidInputError("Cannot delete a default IPAM scope")
        scope.state = "delete-complete"
        # Decrement scope count on parent IPAM
        ipam = self.ipams.get(scope.ipam_id)
        if ipam:
            ipam.scope_count -= 1
        return self.ipam_scopes.pop(ipam_scope_id)

    def describe_ipam_scopes(
        self,
        ipam_scope_ids: Optional[list[str]] = None,
    ) -> list[IpamScope]:
        scopes = list(self.ipam_scopes.values())
        if ipam_scope_ids:
            scopes = [s for s in scopes if s.id in ipam_scope_ids]
        return scopes

    def get_ipam_pool_allocations(
        self,
        ipam_pool_id: str,
        ipam_pool_allocation_id: Optional[str] = None,
    ) -> list[IpamPoolAllocation]:
        pool = self.ipam_pools.get(ipam_pool_id)
        if not pool:
            from ..exceptions import InvalidIpamPoolIdError

            raise InvalidIpamPoolIdError(ipam_pool_id)
        allocs = list(pool.allocations.values())
        if ipam_pool_allocation_id:
            allocs = [
                a for a in allocs if a.ipam_pool_allocation_id == ipam_pool_allocation_id
            ]
        return allocs

    def get_ipam_pool_cidrs(
        self,
        ipam_pool_id: str,
    ) -> list[IpamPoolCidr]:
        pool = self.ipam_pools.get(ipam_pool_id)
        if not pool:
            from ..exceptions import InvalidIpamPoolIdError

            raise InvalidIpamPoolIdError(ipam_pool_id)
        return pool.cidrs

    def get_ipam_resource_cidrs(
        self,
        ipam_pool_id: Optional[str] = None,
        ipam_scope_id: Optional[str] = None,
    ) -> list[dict[str, Any]]:
        results: list[dict[str, Any]] = []
        pools = list(self.ipam_pools.values())
        if ipam_pool_id:
            pools = [p for p in pools if p.id == ipam_pool_id]
        if ipam_scope_id:
            pools = [p for p in pools if p.ipam_scope_id == ipam_scope_id]
        for pool in pools:
            for cidr_obj in pool.cidrs:
                results.append(
                    {
                        "ipam_pool_id": pool.id,
                        "resource_cidr": cidr_obj.cidr,
                        "resource_type": "subnet",
                        "resource_id": "",
                        "resource_name": "",
                        "resource_region": self.region_name,
                        "compliance_status": "compliant",
                        "overlap_status": "nonoverlapping",
                        "management_state": "managed",
                    }
                )
        return results

    def disable_ipam_organization_admin_account(
        self, delegated_admin_account_id: str
    ) -> bool:
        """Remove delegated IPAM admin account. Returns True for success."""
        return True

    def enable_ipam_organization_admin_account(
        self, delegated_admin_account_id: str
    ) -> bool:
        """Delegate an account as IPAM admin. Returns True for success."""
        return True

    def disassociate_ipam_byoasn(self, asn: str, cidr: str) -> dict[str, Any]:  # type: ignore[name-defined]
        """Disassociate a BYOASN from a CIDR. Returns association info."""
        return {"Asn": asn, "Cidr": cidr, "State": "disassociated"}

    def disassociate_ipam_resource_discovery(
        self, ipam_resource_discovery_association_id: str
    ) -> dict[str, Any]:  # type: ignore[name-defined]
        """Disassociate a resource discovery from an IPAM."""
        return {
            "IpamResourceDiscoveryAssociationId": ipam_resource_discovery_association_id,
            "IpamResourceDiscoveryAssociationArn": f"arn:aws:ec2:{self.region_name}:{self.account_id}:ipam-resource-discovery-association/{ipam_resource_discovery_association_id}",  # type: ignore[attr-defined]
            "State": "disassociated",
        }
