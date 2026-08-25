from moto.core.responses import ActionResult
from moto.ec2.utils import add_tag_specification
from moto.utilities.utils import str2bool

from ._base_response import EC2BaseResponse


class InstanceConnectEndpointResponse(EC2BaseResponse):
    def create_instance_connect_endpoint(self) -> ActionResult:
        subnet_id = self._get_param("SubnetId")
        security_group_ids = self._get_param("SecurityGroupIds", [])
        preserve_client_ip = str2bool(
            self._get_param("PreserveClientIp", "true")
        )
        client_token = self._get_param("ClientToken", "")
        tags = add_tag_specification(self._get_param("TagSpecifications", []))

        endpoint = self.ec2_backend.create_instance_connect_endpoint(
            subnet_id=subnet_id,
            security_group_ids=security_group_ids,
            preserve_client_ip=preserve_client_ip,
            client_token=client_token,
            tags=tags,
        )
        result = {
            "InstanceConnectEndpoint": {
                "InstanceConnectEndpointId": endpoint.id,
                "InstanceConnectEndpointArn": endpoint.arn,
                "SubnetId": endpoint.subnet_id,
                "VpcId": endpoint.vpc_id,
                "AvailabilityZone": endpoint.availability_zone,
                "DnsName": endpoint.dns_name,
                "FipsDnsName": endpoint.fips_dns_name,
                "StateMessage": "",
                "State": endpoint.state,
                "PreserveClientIp": endpoint.preserve_client_ip,
                "SecurityGroupIds": endpoint.security_group_ids,
                "NetworkInterfaceIds": endpoint.network_interface_ids,
                "OwnerId": endpoint.owner_id,
                "CreatedAt": endpoint.created_at,
                "Tags": [{"Key": tag.key, "Value": tag.value} for tag in endpoint.get_tags()],
            }
        }
        return ActionResult(result)

    def delete_instance_connect_endpoint(self) -> ActionResult:
        endpoint_id = self._get_param("InstanceConnectEndpointId")
        endpoint = self.ec2_backend.delete_instance_connect_endpoint(endpoint_id)
        result = {
            "InstanceConnectEndpoint": {
                "InstanceConnectEndpointId": endpoint.id,
                "State": endpoint.state,
            }
        }
        return ActionResult(result)

    def describe_instance_connect_endpoints(self) -> ActionResult:
        endpoint_ids = self._get_param("InstanceConnectEndpointIds", [])
        filters = self._filters_from_querystring()
        endpoints = self.ec2_backend.describe_instance_connect_endpoints(
            instance_connect_endpoint_ids=endpoint_ids or None,
            filters=filters,
        )
        result = {
            "InstanceConnectEndpoints": [
                {
                    "InstanceConnectEndpointId": endpoint.id,
                    "InstanceConnectEndpointArn": endpoint.arn,
                    "SubnetId": endpoint.subnet_id,
                    "VpcId": endpoint.vpc_id,
                    "AvailabilityZone": endpoint.availability_zone,
                    "DnsName": endpoint.dns_name,
                    "FipsDnsName": endpoint.fips_dns_name,
                    "StateMessage": "",
                    "State": endpoint.state,
                    "PreserveClientIp": endpoint.preserve_client_ip,
                    "SecurityGroupIds": endpoint.security_group_ids,
                    "NetworkInterfaceIds": endpoint.network_interface_ids,
                    "OwnerId": endpoint.owner_id,
                    "CreatedAt": endpoint.created_at,
                    "Tags": [{"Key": tag.key, "Value": tag.value} for tag in endpoint.get_tags()],
                }
                for endpoint in endpoints
            ]
        }
        return ActionResult(result)
