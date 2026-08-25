from typing import Any, Optional

from moto.core.utils import iso_8601_datetime_with_milliseconds, utcnow

from ..utils import random_instance_connect_endpoint_id
from .core import TaggedEC2Resource


class InstanceConnectEndpoint(TaggedEC2Resource):
    def __init__(
        self,
        backend: Any,
        subnet_id: str,
        security_group_ids: Optional[list[str]] = None,
        preserve_client_ip: bool = True,
        client_token: str = "",
        tags: Optional[dict[str, str]] = None,
    ):
        self.ec2_backend = backend
        self.id = random_instance_connect_endpoint_id()
        self.subnet_id = subnet_id
        self.security_group_ids = security_group_ids or []
        self.preserve_client_ip = preserve_client_ip
        self.client_token = client_token
        self.state = "create-complete"
        self._created_at = utcnow()
        self.add_tags(tags or {})

        # Derive VPC from subnet
        subnet = backend.get_subnet(subnet_id) if hasattr(backend, "get_subnet") else None
        self.vpc_id = subnet.vpc_id if subnet else "vpc-unknown"
        self.availability_zone = subnet.availability_zone if subnet else "us-east-1a"
        self.dns_name = f"{self.id}.{backend.region_name}.ec2-instance-connect-endpoint.amazonaws.com"
        self.fips_dns_name = (
            f"{self.id}.fips.{backend.region_name}.ec2-instance-connect-endpoint.amazonaws.com"
        )
        self.network_interface_ids: list[str] = []

    @property
    def created_at(self) -> str:
        return iso_8601_datetime_with_milliseconds(self._created_at)

    @property
    def owner_id(self) -> str:
        return self.ec2_backend.account_id

    @property
    def arn(self) -> str:
        return (
            f"arn:{self.ec2_backend.partition}:ec2:{self.ec2_backend.region_name}"
            f":{self.ec2_backend.account_id}:instance-connect-endpoint/{self.id}"
        )


class InstanceConnectEndpointBackend:
    def __init__(self) -> None:
        self.instance_connect_endpoints: dict[str, InstanceConnectEndpoint] = {}

    def create_instance_connect_endpoint(
        self,
        subnet_id: str,
        security_group_ids: Optional[list[str]] = None,
        preserve_client_ip: bool = True,
        client_token: str = "",
        tags: Optional[dict[str, str]] = None,
    ) -> InstanceConnectEndpoint:
        endpoint = InstanceConnectEndpoint(
            self,
            subnet_id=subnet_id,
            security_group_ids=security_group_ids,
            preserve_client_ip=preserve_client_ip,
            client_token=client_token,
            tags=tags,
        )
        self.instance_connect_endpoints[endpoint.id] = endpoint
        return endpoint

    def delete_instance_connect_endpoint(
        self, instance_connect_endpoint_id: str
    ) -> InstanceConnectEndpoint:
        endpoint = self.instance_connect_endpoints.get(instance_connect_endpoint_id)
        if not endpoint:
            from ..exceptions import EC2ClientError

            raise EC2ClientError(
                "InvalidInstanceConnectEndpointId.NotFound",
                f"The instance connect endpoint ID '{instance_connect_endpoint_id}' does not exist",
            )
        endpoint.state = "delete-complete"
        return self.instance_connect_endpoints.pop(instance_connect_endpoint_id)

    def describe_instance_connect_endpoints(
        self,
        instance_connect_endpoint_ids: Optional[list[str]] = None,
        filters: Any = None,
    ) -> list[InstanceConnectEndpoint]:
        endpoints = list(self.instance_connect_endpoints.values())
        if instance_connect_endpoint_ids:
            endpoints = [
                e for e in endpoints if e.id in instance_connect_endpoint_ids
            ]
        return endpoints
