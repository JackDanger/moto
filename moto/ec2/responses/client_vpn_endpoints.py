from moto.core.responses import ActionResult, EmptyResult
from moto.ec2.utils import add_tag_specification
from moto.utilities.utils import str2bool

from ._base_response import EC2BaseResponse


class ClientVpnEndpoints(EC2BaseResponse):
    def create_client_vpn_endpoint(self) -> ActionResult:
        client_cidr_block = self._get_param("ClientCidrBlock")
        server_certificate_arn = self._get_param("ServerCertificateArn")
        authentication_options = self._get_param("Authentication", [])
        connection_log_options = self._get_param("ConnectionLogOptions", {})
        dns_servers = self._get_param("DnsServers", [])
        transport_protocol = self._get_param("TransportProtocol", "udp")
        vpn_port = int(self._get_param("VpnPort", "443"))
        description = self._get_param("Description", "")
        split_tunnel = str2bool(self._get_param("SplitTunnel", "false"))
        vpc_id = self._get_param("VpcId")
        security_group_ids = self._get_param("SecurityGroupIds", [])
        tags = add_tag_specification(self._get_param("TagSpecifications", []))

        endpoint = self.ec2_backend.create_client_vpn_endpoint(
            client_cidr_block=client_cidr_block,
            server_certificate_arn=server_certificate_arn,
            authentication_options=authentication_options,
            connection_log_options=connection_log_options,
            dns_servers=dns_servers,
            transport_protocol=transport_protocol,
            vpn_port=vpn_port,
            description=description,
            split_tunnel=split_tunnel,
            vpc_id=vpc_id,
            security_group_ids=security_group_ids,
            tags=tags,
        )
        return ActionResult(
            {
                "ClientVpnEndpointId": endpoint.id,
                "Status": {"Code": "pending-associate"},
                "DnsName": endpoint.dns_name,
            }
        )

    def describe_client_vpn_endpoints(self) -> ActionResult:
        client_vpn_endpoint_ids = self._get_param("ClientVpnEndpointIds", [])
        endpoints = self.ec2_backend.describe_client_vpn_endpoints(
            client_vpn_endpoint_ids=client_vpn_endpoint_ids
        )
        return ActionResult({"ClientVpnEndpoints": endpoints})

    def delete_client_vpn_endpoint(self) -> ActionResult:
        client_vpn_endpoint_id = self._get_param("ClientVpnEndpointId")
        endpoint = self.ec2_backend.delete_client_vpn_endpoint(client_vpn_endpoint_id)
        return ActionResult({"Status": {"Code": "deleting"}})

    def modify_client_vpn_endpoint(self) -> ActionResult:
        client_vpn_endpoint_id = self._get_param("ClientVpnEndpointId")
        server_certificate_arn = self._get_param("ServerCertificateArn")
        connection_log_options = self._get_param("ConnectionLogOptions")
        dns_servers = self._get_param("DnsServers")
        vpn_port = self._get_param("VpnPort")
        if vpn_port is not None:
            vpn_port = int(vpn_port)
        description = self._get_param("Description")
        split_tunnel = self._get_param("SplitTunnel")
        if split_tunnel is not None:
            split_tunnel = str2bool(split_tunnel)
        vpc_id = self._get_param("VpcId")
        security_group_ids = self._get_param("SecurityGroupIds")

        self.ec2_backend.modify_client_vpn_endpoint(
            client_vpn_endpoint_id=client_vpn_endpoint_id,
            server_certificate_arn=server_certificate_arn,
            connection_log_options=connection_log_options,
            dns_servers=dns_servers,
            vpn_port=vpn_port,
            description=description,
            split_tunnel=split_tunnel,
            vpc_id=vpc_id,
            security_group_ids=security_group_ids,
        )
        return ActionResult({"Return": True})

    def disassociate_client_vpn_target_network(self) -> ActionResult:
        client_vpn_endpoint_id = self._get_param("ClientVpnEndpointId")
        association_id = self._get_param("AssociationId")
        result = self.ec2_backend.disassociate_client_vpn_target_network(
            client_vpn_endpoint_id=client_vpn_endpoint_id,
            association_id=association_id,
        )
        return ActionResult(result)
