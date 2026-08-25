from typing import Any, Optional

from ..utils import random_id
from .core import TaggedEC2Resource


class PublicIpv4PoolCidr:
    def __init__(self, cidr: str):
        self.cidr = cidr
        self.address_count = 0
        self.available_address_count = 0


class PublicIpv4Pool(TaggedEC2Resource):
    def __init__(
        self,
        ec2_backend: Any,
        tags: Optional[dict[str, str]] = None,
    ):
        self.ec2_backend = ec2_backend
        self.id = random_id(prefix="ipv4pool-ec2-")
        self.description = ""
        self.pool_address_ranges: list[PublicIpv4PoolCidr] = []
        self.total_address_count = 0
        self.total_available_address_count = 0
        self.network_border_group = ec2_backend.region_name
        self.add_tags(tags or {})


class PublicIpv4PoolBackend:
    def __init__(self) -> None:
        self.public_ipv4_pools: dict[str, PublicIpv4Pool] = {}

    def create_public_ipv4_pool(
        self,
        tags: Optional[dict[str, str]] = None,
    ) -> PublicIpv4Pool:
        pool = PublicIpv4Pool(self, tags=tags)
        self.public_ipv4_pools[pool.id] = pool
        return pool

    def delete_public_ipv4_pool(self, pool_id: str) -> PublicIpv4Pool:
        pool = self.public_ipv4_pools.pop(pool_id, None)
        if not pool:
            from ..exceptions import EC2ClientError

            raise EC2ClientError(
                "InvalidPublicIpv4PoolID.NotFound",
                f"The public IPv4 pool ID '{pool_id}' does not exist",
            )
        return pool

    def describe_public_ipv4_pools(
        self, pool_ids: Optional[list[str]] = None
    ) -> list[PublicIpv4Pool]:
        pools = list(self.public_ipv4_pools.values())
        if pool_ids:
            pools = [p for p in pools if p.id in pool_ids]
        return pools

    def provision_public_ipv4_pool_cidr(
        self,
        pool_id: str,
        ipam_pool_id: str,
        netmask_length: int,
    ) -> tuple[str, str]:
        pool = self.public_ipv4_pools.get(pool_id)
        if not pool:
            from ..exceptions import EC2ClientError

            raise EC2ClientError(
                "InvalidPublicIpv4PoolID.NotFound",
                f"The public IPv4 pool ID '{pool_id}' does not exist",
            )
        # Generate a fake CIDR
        cidr = f"10.0.0.0/{netmask_length}"
        pool_cidr = PublicIpv4PoolCidr(cidr)
        pool.pool_address_ranges.append(pool_cidr)
        return pool_id, cidr

    def deprovision_public_ipv4_pool_cidr(
        self,
        pool_id: str,
        cidr: str,
    ) -> tuple[str, str]:
        pool = self.public_ipv4_pools.get(pool_id)
        if not pool:
            from ..exceptions import EC2ClientError

            raise EC2ClientError(
                "InvalidPublicIpv4PoolID.NotFound",
                f"The public IPv4 pool ID '{pool_id}' does not exist",
            )
        pool.pool_address_ranges = [
            r for r in pool.pool_address_ranges if r.cidr != cidr
        ]
        return pool_id, cidr
