from moto.core.responses import ActionResult, EmptyResult

from ._base_response import EC2BaseResponse


class SecurityGroupVpcAssociationResponse(EC2BaseResponse):
    def associate_security_group_vpc(self) -> ActionResult:
        group_id = self._get_param("GroupId")
        vpc_id = self._get_param("VpcId")
        assoc = self.ec2_backend.associate_security_group_vpc(
            group_id=group_id,
            vpc_id=vpc_id,
        )
        result = {"State": assoc.state}
        return ActionResult(result)

    def describe_security_group_vpc_associations(self) -> ActionResult:
        filters = self._filters_from_querystring()
        group_ids = filters.get("group-id", None)
        vpc_ids = filters.get("vpc-id", None)
        assocs = self.ec2_backend.describe_security_group_vpc_associations(
            group_ids=group_ids,
            vpc_ids=vpc_ids,
        )
        result = {
            "SecurityGroupVpcAssociationSet": [
                {
                    "GroupId": assoc.group_id,
                    "VpcId": assoc.vpc_id,
                    "State": assoc.state,
                }
                for assoc in assocs
            ]
        }
        return ActionResult(result)

    def disassociate_security_group_vpc(self) -> ActionResult:
        group_id = self._get_param("GroupId")
        vpc_id = self._get_param("VpcId")
        assoc = self.ec2_backend.disassociate_security_group_vpc(
            group_id=group_id,
            vpc_id=vpc_id,
        )
        result = {"State": assoc.state}
        return ActionResult(result)
