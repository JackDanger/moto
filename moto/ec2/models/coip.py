from typing import Any, Optional

from moto.core.utils import utcnow

from ..utils import random_id
from .core import TaggedEC2Resource


class CoipPool(TaggedEC2Resource):
    def __init__(
        self,
        ec2_backend: Any,
        local_gateway_route_table_id: str,
        tags: Optional[dict[str, str]] = None,
    ):
        self.ec2_backend = ec2_backend
        self.id = random_id(prefix="ipv4pool-coip-")
        self.local_gateway_route_table_id = local_gateway_route_table_id
        self.pool_cidrs: list[str] = []
        self._created_at = utcnow()
        self.add_tags(tags or {})

    @property
    def pool_arn(self) -> str:
        return (
            f"arn:{self.ec2_backend.partition}:ec2:{self.ec2_backend.region_name}"
            f":{self.ec2_backend.account_id}:coip-pool/{self.id}"
        )


class CoipCidr:
    def __init__(self, coip_pool_id: str, cidr: str, local_gateway_route_table_id: str):
        self.coip_pool_id = coip_pool_id
        self.cidr = cidr
        self.local_gateway_route_table_id = local_gateway_route_table_id


class CoipBackend:
    def __init__(self) -> None:
        self.coip_pools: dict[str, CoipPool] = {}

    def create_coip_pool(
        self,
        local_gateway_route_table_id: str,
        tags: Optional[dict[str, str]] = None,
    ) -> CoipPool:
        pool = CoipPool(self, local_gateway_route_table_id, tags=tags)
        self.coip_pools[pool.id] = pool
        return pool

    def delete_coip_pool(self, coip_pool_id: str) -> CoipPool:
        pool = self.coip_pools.pop(coip_pool_id, None)
        if not pool:
            from ..exceptions import EC2ClientError

            raise EC2ClientError(
                "InvalidCoipPoolId.NotFound",
                f"The coip pool ID '{coip_pool_id}' does not exist",
            )
        return pool

    def describe_coip_pools(
        self, pool_ids: Optional[list[str]] = None
    ) -> list[CoipPool]:
        pools = list(self.coip_pools.values())
        if pool_ids:
            pools = [p for p in pools if p.id in pool_ids]
        return pools

    def get_coip_pool_usage(self, pool_id: str) -> tuple[Optional[CoipPool], list[str]]:
        pool = self.coip_pools.get(pool_id)
        return pool, pool.pool_cidrs if pool else []

    def create_coip_cidr(self, coip_pool_id: str, cidr: str) -> Optional[CoipCidr]:
        pool = self.coip_pools.get(coip_pool_id)
        if not pool:
            from ..exceptions import EC2ClientError

            raise EC2ClientError(
                "InvalidCoipPoolId.NotFound",
                f"The coip pool ID '{coip_pool_id}' does not exist",
            )
        pool.pool_cidrs.append(cidr)
        return CoipCidr(
            coip_pool_id=coip_pool_id,
            cidr=cidr,
            local_gateway_route_table_id=pool.local_gateway_route_table_id,
        )

    def delete_coip_cidr(self, coip_pool_id: str, cidr: str) -> Optional[CoipCidr]:
        pool = self.coip_pools.get(coip_pool_id)
        if not pool:
            from ..exceptions import EC2ClientError

            raise EC2ClientError(
                "InvalidCoipPoolId.NotFound",
                f"The coip pool ID '{coip_pool_id}' does not exist",
            )
        if cidr in pool.pool_cidrs:
            pool.pool_cidrs.remove(cidr)
        return CoipCidr(
            coip_pool_id=coip_pool_id,
            cidr=cidr,
            local_gateway_route_table_id=pool.local_gateway_route_table_id,
        )
