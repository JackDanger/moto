from typing import Any, Optional

from moto.core.utils import iso_8601_datetime_with_milliseconds, utcnow

from ..utils import random_ipam_id, random_ipam_pool_id, random_ipam_scope_id
from .core import TaggedEC2Resource


class IpamScope:
    def __init__(
        self,
        ec2_backend: Any,
        ipam_id: str,
        scope_type: str = "private",
        is_default: bool = False,
    ):
        self.ec2_backend = ec2_backend
        self.id = random_ipam_scope_id()
        self.ipam_id = ipam_id
        self.scope_type = scope_type
        self.is_default = is_default
        self.state = "create-complete"
        self.pool_count = 0

    @property
    def arn(self) -> str:
        return (
            f"arn:{self.ec2_backend.partition}:ec2:{self.ec2_backend.region_name}"
            f":{self.ec2_backend.account_id}:ipam-scope/{self.id}"
        )


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
        return ipam

    def describe_ipams(
        self, ipam_ids: Optional[list[str]] = None
    ) -> list[Ipam]:
        ipams = list(self.ipams.values())
        if ipam_ids:
            ipams = [i for i in ipams if i.id in ipam_ids]
        return ipams

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
