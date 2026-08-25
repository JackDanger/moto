from moto.core.responses import ActionResult
from moto.ec2.utils import add_tag_specification

from ._base_response import EC2BaseResponse


class NatGateways(EC2BaseResponse):
    def create_nat_gateway(self) -> ActionResult:
        subnet_id = self._get_param("SubnetId")
        allocation_id = self._get_param("AllocationId")
        connectivity_type = self._get_param("ConnectivityType")
        tags = add_tag_specification(self._get_param("TagSpecifications", []))

        nat_gateway = self.ec2_backend.create_nat_gateway(
            subnet_id=subnet_id,
            allocation_id=allocation_id,
            tags=tags,
            connectivity_type=connectivity_type,
        )
        return ActionResult({"NatGateway": nat_gateway})

    def delete_nat_gateway(self) -> ActionResult:
        nat_gateway_id = self._get_param("NatGatewayId")
        nat_gateway = self.ec2_backend.delete_nat_gateway(nat_gateway_id)
        return ActionResult({"NatGatewayId": nat_gateway.id})

    def describe_nat_gateways(self) -> ActionResult:
        filters = self._filters_from_querystring()
        nat_gateway_ids = self._get_param("NatGatewayIds", [])
        nat_gateways = self.ec2_backend.describe_nat_gateways(filters, nat_gateway_ids)
        return ActionResult({"NatGateways": nat_gateways})
        gateway_list = []
        for nat_gateway in nat_gateways:
            address_items = []
            for address_set in nat_gateway.address_set:
                address_dict = {}
                if address_set.allocationId:
                    address_dict["AllocationId"] = address_set.allocationId
                if address_set.privateIp:
                    address_dict["PrivateIp"] = address_set.privateIp
                if address_set.publicIp:
                    address_dict["PublicIp"] = address_set.publicIp
                if address_set.networkInterfaceId:
                    address_dict["NetworkInterfaceId"] = address_set.networkInterfaceId
                if address_set.associationId:
                    address_dict["AssociationId"] = address_set.associationId
                address_items.append(address_dict)
            tags = [{"Key": tag.key, "Value": tag.value} for tag in nat_gateway.get_tags()]
            gateway_dict = {
                "SubnetId": nat_gateway.subnet_id,
                "NatGatewayAddresses": address_items,
                "CreateTime": nat_gateway.create_time,
                "VpcId": nat_gateway.vpc_id,
                "NatGatewayId": nat_gateway.id,
                "ConnectivityType": nat_gateway.connectivity_type,
                "State": nat_gateway.state,
                "Tags": tags,
            }
            gateway_list.append(gateway_dict)
        return ActionResult({"NatGateways": gateway_list})
    def disassociate_nat_gateway_address(self) -> ActionResult:
        nat_gateway_id = self._get_param("NatGatewayId")
        association_ids = self._get_param("AssociationIds", [])
        result = self.ec2_backend.disassociate_nat_gateway_address(
            nat_gateway_id=nat_gateway_id,
            association_ids=association_ids,
        )
        return ActionResult(result)
