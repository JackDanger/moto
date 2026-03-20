from ._base_response import EC2BaseResponse


class SecurityGroupVpcAssociationResponse(EC2BaseResponse):
    def associate_security_group_vpc(self) -> str:
        group_id = self._get_param("GroupId")
        vpc_id = self._get_param("VpcId")
        assoc = self.ec2_backend.associate_security_group_vpc(
            group_id=group_id,
            vpc_id=vpc_id,
        )
        template = self.response_template(ASSOCIATE_SECURITY_GROUP_VPC)
        return template.render(assoc=assoc)

    def describe_security_group_vpc_associations(self) -> str:
        filters = self._filters_from_querystring()
        group_ids = filters.get("group-id", None)
        vpc_ids = filters.get("vpc-id", None)
        assocs = self.ec2_backend.describe_security_group_vpc_associations(
            group_ids=group_ids,
            vpc_ids=vpc_ids,
        )
        template = self.response_template(DESCRIBE_SECURITY_GROUP_VPC_ASSOCIATIONS)
        return template.render(assocs=assocs)

    def disassociate_security_group_vpc(self) -> str:
        group_id = self._get_param("GroupId")
        vpc_id = self._get_param("VpcId")
        assoc = self.ec2_backend.disassociate_security_group_vpc(
            group_id=group_id,
            vpc_id=vpc_id,
        )
        template = self.response_template(DISASSOCIATE_SECURITY_GROUP_VPC)
        return template.render(assoc=assoc)


ASSOCIATE_SECURITY_GROUP_VPC = """<AssociateSecurityGroupVpcResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
  <requestId>7a62c49f-347e-4fc4-9331-6e8eEXAMPLE</requestId>
  <state>{{ assoc.state }}</state>
</AssociateSecurityGroupVpcResponse>"""

DESCRIBE_SECURITY_GROUP_VPC_ASSOCIATIONS = """<DescribeSecurityGroupVpcAssociationsResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
  <requestId>7a62c49f-347e-4fc4-9331-6e8eEXAMPLE</requestId>
  <securityGroupVpcAssociationSet>
    {% for assoc in assocs %}
    <item>
      <groupId>{{ assoc.group_id }}</groupId>
      <vpcId>{{ assoc.vpc_id }}</vpcId>
      <state>{{ assoc.state }}</state>
    </item>
    {% endfor %}
  </securityGroupVpcAssociationSet>
</DescribeSecurityGroupVpcAssociationsResponse>"""

DISASSOCIATE_SECURITY_GROUP_VPC = """<DisassociateSecurityGroupVpcResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
  <requestId>7a62c49f-347e-4fc4-9331-6e8eEXAMPLE</requestId>
  <state>{{ assoc.state }}</state>
</DisassociateSecurityGroupVpcResponse>"""
