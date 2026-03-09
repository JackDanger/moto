from typing import Optional


class SecurityGroupVpcAssociation:
    def __init__(
        self,
        group_id: str,
        vpc_id: str,
        state: str = "associated",
    ):
        self.group_id = group_id
        self.vpc_id = vpc_id
        self.state = state


class SecurityGroupVpcAssociationBackend:
    def __init__(self) -> None:
        self.security_group_vpc_associations: list[SecurityGroupVpcAssociation] = []

    def associate_security_group_vpc(
        self, group_id: str, vpc_id: str
    ) -> SecurityGroupVpcAssociation:
        assoc = SecurityGroupVpcAssociation(
            group_id=group_id,
            vpc_id=vpc_id,
            state="associated",
        )
        self.security_group_vpc_associations.append(assoc)
        return assoc

    def describe_security_group_vpc_associations(
        self,
        group_ids: Optional[list[str]] = None,
        vpc_ids: Optional[list[str]] = None,
    ) -> list[SecurityGroupVpcAssociation]:
        assocs = [
            a
            for a in self.security_group_vpc_associations
            if a.state != "disassociated"
        ]
        if group_ids:
            assocs = [a for a in assocs if a.group_id in group_ids]
        if vpc_ids:
            assocs = [a for a in assocs if a.vpc_id in vpc_ids]
        return assocs

    def disassociate_security_group_vpc(
        self, group_id: str, vpc_id: str
    ) -> SecurityGroupVpcAssociation:
        for assoc in self.security_group_vpc_associations:
            if assoc.group_id == group_id and assoc.vpc_id == vpc_id:
                assoc.state = "disassociated"
                return assoc
        from ..exceptions import EC2ClientError

        raise EC2ClientError(
            "InvalidSecurityGroupVpcAssociation.NotFound",
            f"The security group VPC association for group '{group_id}' and VPC '{vpc_id}' does not exist",
        )
