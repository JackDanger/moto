from moto.ec2.utils import add_tag_specification
from moto.utilities.utils import str2bool

from ._base_response import EC2BaseResponse


class InstanceConnectEndpointResponse(EC2BaseResponse):
    def create_instance_connect_endpoint(self) -> str:
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
        template = self.response_template(CREATE_INSTANCE_CONNECT_ENDPOINT)
        return template.render(endpoint=endpoint)

    def delete_instance_connect_endpoint(self) -> str:
        endpoint_id = self._get_param("InstanceConnectEndpointId")
        endpoint = self.ec2_backend.delete_instance_connect_endpoint(endpoint_id)
        template = self.response_template(DELETE_INSTANCE_CONNECT_ENDPOINT)
        return template.render(endpoint=endpoint)

    def describe_instance_connect_endpoints(self) -> str:
        endpoint_ids = self._get_param("InstanceConnectEndpointIds", [])
        filters = self._filters_from_querystring()
        endpoints = self.ec2_backend.describe_instance_connect_endpoints(
            instance_connect_endpoint_ids=endpoint_ids or None,
            filters=filters,
        )
        template = self.response_template(DESCRIBE_INSTANCE_CONNECT_ENDPOINTS)
        return template.render(endpoints=endpoints)


CREATE_INSTANCE_CONNECT_ENDPOINT = """<CreateInstanceConnectEndpointResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
  <requestId>7a62c49f-347e-4fc4-9331-6e8eEXAMPLE</requestId>
  <instanceConnectEndpoint>
    <instanceConnectEndpointId>{{ endpoint.id }}</instanceConnectEndpointId>
    <instanceConnectEndpointArn>{{ endpoint.arn }}</instanceConnectEndpointArn>
    <subnetId>{{ endpoint.subnet_id }}</subnetId>
    <vpcId>{{ endpoint.vpc_id }}</vpcId>
    <availabilityZone>{{ endpoint.availability_zone }}</availabilityZone>
    <dnsName>{{ endpoint.dns_name }}</dnsName>
    <fipsDnsName>{{ endpoint.fips_dns_name }}</fipsDnsName>
    <stateMessage></stateMessage>
    <state>{{ endpoint.state }}</state>
    <preserveClientIp>{{ 'true' if endpoint.preserve_client_ip else 'false' }}</preserveClientIp>
    <securityGroupIdSet>
      {% for sg_id in endpoint.security_group_ids %}
      <item>{{ sg_id }}</item>
      {% endfor %}
    </securityGroupIdSet>
    <networkInterfaceIdSet>
      {% for eni_id in endpoint.network_interface_ids %}
      <item>{{ eni_id }}</item>
      {% endfor %}
    </networkInterfaceIdSet>
    <ownerId>{{ endpoint.owner_id }}</ownerId>
    <createdAt>{{ endpoint.created_at }}</createdAt>
    <tagSet>
      {% for tag in endpoint.get_tags() %}
      <item>
        <key>{{ tag.key }}</key>
        <value>{{ tag.value }}</value>
      </item>
      {% endfor %}
    </tagSet>
  </instanceConnectEndpoint>
</CreateInstanceConnectEndpointResponse>"""


DELETE_INSTANCE_CONNECT_ENDPOINT = """<DeleteInstanceConnectEndpointResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
  <requestId>7a62c49f-347e-4fc4-9331-6e8eEXAMPLE</requestId>
  <instanceConnectEndpoint>
    <instanceConnectEndpointId>{{ endpoint.id }}</instanceConnectEndpointId>
    <state>{{ endpoint.state }}</state>
  </instanceConnectEndpoint>
</DeleteInstanceConnectEndpointResponse>"""


DESCRIBE_INSTANCE_CONNECT_ENDPOINTS = """<DescribeInstanceConnectEndpointsResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
  <requestId>7a62c49f-347e-4fc4-9331-6e8eEXAMPLE</requestId>
  <instanceConnectEndpointSet>
    {% for endpoint in endpoints %}
    <item>
      <instanceConnectEndpointId>{{ endpoint.id }}</instanceConnectEndpointId>
      <instanceConnectEndpointArn>{{ endpoint.arn }}</instanceConnectEndpointArn>
      <subnetId>{{ endpoint.subnet_id }}</subnetId>
      <vpcId>{{ endpoint.vpc_id }}</vpcId>
      <availabilityZone>{{ endpoint.availability_zone }}</availabilityZone>
      <dnsName>{{ endpoint.dns_name }}</dnsName>
      <fipsDnsName>{{ endpoint.fips_dns_name }}</fipsDnsName>
      <stateMessage></stateMessage>
      <state>{{ endpoint.state }}</state>
      <preserveClientIp>{{ 'true' if endpoint.preserve_client_ip else 'false' }}</preserveClientIp>
      <securityGroupIdSet>
        {% for sg_id in endpoint.security_group_ids %}
        <item>{{ sg_id }}</item>
        {% endfor %}
      </securityGroupIdSet>
      <networkInterfaceIdSet>
        {% for eni_id in endpoint.network_interface_ids %}
        <item>{{ eni_id }}</item>
        {% endfor %}
      </networkInterfaceIdSet>
      <ownerId>{{ endpoint.owner_id }}</ownerId>
      <createdAt>{{ endpoint.created_at }}</createdAt>
      <tagSet>
        {% for tag in endpoint.get_tags() %}
        <item>
          <key>{{ tag.key }}</key>
          <value>{{ tag.value }}</value>
        </item>
        {% endfor %}
      </tagSet>
    </item>
    {% endfor %}
  </instanceConnectEndpointSet>
</DescribeInstanceConnectEndpointsResponse>"""
