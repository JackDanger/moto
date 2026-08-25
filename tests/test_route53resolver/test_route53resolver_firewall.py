"""Tests for Route53Resolver DNS Firewall operations."""

import boto3
import pytest
from botocore.exceptions import ClientError
from moto import mock_aws


@mock_aws
def test_create_firewall_domain_list():
    client = boto3.client("route53resolver", region_name="us-east-1")
    resp = client.create_firewall_domain_list(Name="test-domain-list")
    domain_list = resp["FirewallDomainList"]
    assert domain_list["Name"] == "test-domain-list"
    assert domain_list["Id"].startswith("rslvr-fdl-")
    assert domain_list["Status"] == "COMPLETE"
    assert domain_list["DomainCount"] == 0
    assert "Arn" in domain_list


@mock_aws
def test_get_firewall_domain_list():
    client = boto3.client("route53resolver", region_name="us-east-1")
    create_resp = client.create_firewall_domain_list(Name="test-domain-list")
    domain_list_id = create_resp["FirewallDomainList"]["Id"]

    get_resp = client.get_firewall_domain_list(FirewallDomainListId=domain_list_id)
    assert get_resp["FirewallDomainList"]["Id"] == domain_list_id
    assert get_resp["FirewallDomainList"]["Name"] == "test-domain-list"


@mock_aws
def test_get_firewall_domain_list_not_found():
    client = boto3.client("route53resolver", region_name="us-east-1")
    with pytest.raises(ClientError) as exc:
        client.get_firewall_domain_list(FirewallDomainListId="rslvr-fdl-fake")
    assert exc.value.response["Error"]["Code"] == "ResourceNotFoundException"


@mock_aws
def test_delete_firewall_domain_list():
    client = boto3.client("route53resolver", region_name="us-east-1")
    create_resp = client.create_firewall_domain_list(Name="test-domain-list")
    domain_list_id = create_resp["FirewallDomainList"]["Id"]

    delete_resp = client.delete_firewall_domain_list(FirewallDomainListId=domain_list_id)
    assert delete_resp["FirewallDomainList"]["Status"] == "DELETING"

    # Should be gone now
    with pytest.raises(ClientError) as exc:
        client.get_firewall_domain_list(FirewallDomainListId=domain_list_id)
    assert exc.value.response["Error"]["Code"] == "ResourceNotFoundException"


@mock_aws
def test_list_firewall_domain_lists():
    client = boto3.client("route53resolver", region_name="us-east-1")
    client.create_firewall_domain_list(Name="alpha-list")
    client.create_firewall_domain_list(Name="beta-list")

    resp = client.list_firewall_domain_lists()
    assert len(resp["FirewallDomainLists"]) == 2
    names = [x["Name"] for x in resp["FirewallDomainLists"]]
    assert "alpha-list" in names
    assert "beta-list" in names


@mock_aws
def test_update_firewall_domains_add():
    client = boto3.client("route53resolver", region_name="us-east-1")
    create_resp = client.create_firewall_domain_list(Name="test-domain-list")
    domain_list_id = create_resp["FirewallDomainList"]["Id"]

    resp = client.update_firewall_domains(
        FirewallDomainListId=domain_list_id,
        Operation="ADD",
        Domains=["example.com", "test.org"],
    )
    assert resp["Status"] == "COMPLETE"

    # Verify domains were added
    get_resp = client.get_firewall_domain_list(FirewallDomainListId=domain_list_id)
    assert get_resp["FirewallDomainList"]["DomainCount"] == 2


@mock_aws
def test_update_firewall_domains_remove():
    client = boto3.client("route53resolver", region_name="us-east-1")
    create_resp = client.create_firewall_domain_list(Name="test-domain-list")
    domain_list_id = create_resp["FirewallDomainList"]["Id"]

    client.update_firewall_domains(
        FirewallDomainListId=domain_list_id,
        Operation="ADD",
        Domains=["example.com", "test.org", "keep.me"],
    )
    client.update_firewall_domains(
        FirewallDomainListId=domain_list_id,
        Operation="REMOVE",
        Domains=["test.org"],
    )

    get_resp = client.get_firewall_domain_list(FirewallDomainListId=domain_list_id)
    assert get_resp["FirewallDomainList"]["DomainCount"] == 2


@mock_aws
def test_update_firewall_domains_replace():
    client = boto3.client("route53resolver", region_name="us-east-1")
    create_resp = client.create_firewall_domain_list(Name="test-domain-list")
    domain_list_id = create_resp["FirewallDomainList"]["Id"]

    client.update_firewall_domains(
        FirewallDomainListId=domain_list_id,
        Operation="ADD",
        Domains=["example.com", "test.org"],
    )
    client.update_firewall_domains(
        FirewallDomainListId=domain_list_id,
        Operation="REPLACE",
        Domains=["new.com"],
    )

    get_resp = client.get_firewall_domain_list(FirewallDomainListId=domain_list_id)
    assert get_resp["FirewallDomainList"]["DomainCount"] == 1


@mock_aws
def test_list_firewall_domains():
    client = boto3.client("route53resolver", region_name="us-east-1")
    create_resp = client.create_firewall_domain_list(Name="test-domain-list")
    domain_list_id = create_resp["FirewallDomainList"]["Id"]

    client.update_firewall_domains(
        FirewallDomainListId=domain_list_id,
        Operation="ADD",
        Domains=["example.com", "test.org"],
    )

    resp = client.list_firewall_domains(FirewallDomainListId=domain_list_id)
    assert len(resp["Domains"]) == 2
    assert "example.com" in resp["Domains"]
    assert "test.org" in resp["Domains"]


# --- Firewall Rule Groups ---


@mock_aws
def test_create_firewall_rule_group():
    client = boto3.client("route53resolver", region_name="us-east-1")
    resp = client.create_firewall_rule_group(Name="test-rule-group")
    rule_group = resp["FirewallRuleGroup"]
    assert rule_group["Name"] == "test-rule-group"
    assert rule_group["Id"].startswith("rslvr-frg-")
    assert rule_group["Status"] == "COMPLETE"
    assert rule_group["RuleCount"] == 0


@mock_aws
def test_get_firewall_rule_group():
    client = boto3.client("route53resolver", region_name="us-east-1")
    create_resp = client.create_firewall_rule_group(Name="test-rule-group")
    rule_group_id = create_resp["FirewallRuleGroup"]["Id"]

    get_resp = client.get_firewall_rule_group(FirewallRuleGroupId=rule_group_id)
    assert get_resp["FirewallRuleGroup"]["Id"] == rule_group_id
    assert get_resp["FirewallRuleGroup"]["Name"] == "test-rule-group"


@mock_aws
def test_get_firewall_rule_group_not_found():
    client = boto3.client("route53resolver", region_name="us-east-1")
    with pytest.raises(ClientError) as exc:
        client.get_firewall_rule_group(FirewallRuleGroupId="rslvr-frg-fake")
    assert exc.value.response["Error"]["Code"] == "ResourceNotFoundException"


@mock_aws
def test_delete_firewall_rule_group():
    client = boto3.client("route53resolver", region_name="us-east-1")
    create_resp = client.create_firewall_rule_group(Name="test-rule-group")
    rule_group_id = create_resp["FirewallRuleGroup"]["Id"]

    delete_resp = client.delete_firewall_rule_group(FirewallRuleGroupId=rule_group_id)
    assert delete_resp["FirewallRuleGroup"]["Status"] == "DELETING"

    with pytest.raises(ClientError) as exc:
        client.get_firewall_rule_group(FirewallRuleGroupId=rule_group_id)
    assert exc.value.response["Error"]["Code"] == "ResourceNotFoundException"


@mock_aws
def test_list_firewall_rule_groups():
    client = boto3.client("route53resolver", region_name="us-east-1")
    client.create_firewall_rule_group(Name="alpha-group")
    client.create_firewall_rule_group(Name="beta-group")

    resp = client.list_firewall_rule_groups()
    assert len(resp["FirewallRuleGroups"]) == 2


# --- Firewall Rules ---


@mock_aws
def test_create_firewall_rule():
    client = boto3.client("route53resolver", region_name="us-east-1")
    domain_list = client.create_firewall_domain_list(Name="test-dl")
    domain_list_id = domain_list["FirewallDomainList"]["Id"]
    rule_group = client.create_firewall_rule_group(Name="test-rg")
    rule_group_id = rule_group["FirewallRuleGroup"]["Id"]

    resp = client.create_firewall_rule(
        FirewallRuleGroupId=rule_group_id,
        FirewallDomainListId=domain_list_id,
        Name="test-rule",
        Priority=100,
        Action="BLOCK",
        BlockResponse="NODATA",
    )
    rule = resp["FirewallRule"]
    assert rule["Name"] == "test-rule"
    assert rule["Priority"] == 100
    assert rule["Action"] == "BLOCK"
    assert rule["BlockResponse"] == "NODATA"
    assert rule["FirewallRuleGroupId"] == rule_group_id
    assert rule["FirewallDomainListId"] == domain_list_id

    # Rule count should be incremented
    rg = client.get_firewall_rule_group(FirewallRuleGroupId=rule_group_id)
    assert rg["FirewallRuleGroup"]["RuleCount"] == 1


@mock_aws
def test_create_firewall_rule_nonexistent_group():
    client = boto3.client("route53resolver", region_name="us-east-1")
    domain_list = client.create_firewall_domain_list(Name="test-dl")
    domain_list_id = domain_list["FirewallDomainList"]["Id"]

    with pytest.raises(ClientError) as exc:
        client.create_firewall_rule(
            FirewallRuleGroupId="rslvr-frg-fake",
            FirewallDomainListId=domain_list_id,
            Name="test-rule",
            Priority=100,
            Action="ALLOW",
        )
    assert exc.value.response["Error"]["Code"] == "ResourceNotFoundException"


@mock_aws
def test_delete_firewall_rule():
    client = boto3.client("route53resolver", region_name="us-east-1")
    domain_list = client.create_firewall_domain_list(Name="test-dl")
    domain_list_id = domain_list["FirewallDomainList"]["Id"]
    rule_group = client.create_firewall_rule_group(Name="test-rg")
    rule_group_id = rule_group["FirewallRuleGroup"]["Id"]

    client.create_firewall_rule(
        FirewallRuleGroupId=rule_group_id,
        FirewallDomainListId=domain_list_id,
        Name="test-rule",
        Priority=100,
        Action="ALLOW",
    )

    resp = client.delete_firewall_rule(
        FirewallRuleGroupId=rule_group_id,
        FirewallDomainListId=domain_list_id,
    )
    assert resp["FirewallRule"]["Name"] == "test-rule"

    # Rule count should be decremented
    rg = client.get_firewall_rule_group(FirewallRuleGroupId=rule_group_id)
    assert rg["FirewallRuleGroup"]["RuleCount"] == 0


@mock_aws
def test_update_firewall_rule():
    client = boto3.client("route53resolver", region_name="us-east-1")
    domain_list = client.create_firewall_domain_list(Name="test-dl")
    domain_list_id = domain_list["FirewallDomainList"]["Id"]
    rule_group = client.create_firewall_rule_group(Name="test-rg")
    rule_group_id = rule_group["FirewallRuleGroup"]["Id"]

    client.create_firewall_rule(
        FirewallRuleGroupId=rule_group_id,
        FirewallDomainListId=domain_list_id,
        Name="test-rule",
        Priority=100,
        Action="ALLOW",
    )

    resp = client.update_firewall_rule(
        FirewallRuleGroupId=rule_group_id,
        FirewallDomainListId=domain_list_id,
        Name="updated-rule",
        Priority=200,
        Action="BLOCK",
        BlockResponse="NXDOMAIN",
    )
    rule = resp["FirewallRule"]
    assert rule["Name"] == "updated-rule"
    assert rule["Priority"] == 200
    assert rule["Action"] == "BLOCK"
    assert rule["BlockResponse"] == "NXDOMAIN"


@mock_aws
def test_list_firewall_rules():
    client = boto3.client("route53resolver", region_name="us-east-1")
    domain_list1 = client.create_firewall_domain_list(Name="dl1")
    dl1_id = domain_list1["FirewallDomainList"]["Id"]
    domain_list2 = client.create_firewall_domain_list(Name="dl2")
    dl2_id = domain_list2["FirewallDomainList"]["Id"]
    rule_group = client.create_firewall_rule_group(Name="test-rg")
    rg_id = rule_group["FirewallRuleGroup"]["Id"]

    client.create_firewall_rule(
        FirewallRuleGroupId=rg_id,
        FirewallDomainListId=dl1_id,
        Name="rule-1",
        Priority=100,
        Action="ALLOW",
    )
    client.create_firewall_rule(
        FirewallRuleGroupId=rg_id,
        FirewallDomainListId=dl2_id,
        Name="rule-2",
        Priority=200,
        Action="BLOCK",
        BlockResponse="NODATA",
    )

    resp = client.list_firewall_rules(FirewallRuleGroupId=rg_id)
    assert len(resp["FirewallRules"]) == 2
    # Should be sorted by priority
    assert resp["FirewallRules"][0]["Priority"] == 100
    assert resp["FirewallRules"][1]["Priority"] == 200


# --- Firewall Rule Group Associations ---


@mock_aws
def test_associate_firewall_rule_group():
    client = boto3.client("route53resolver", region_name="us-east-1")
    rule_group = client.create_firewall_rule_group(Name="test-rg")
    rule_group_id = rule_group["FirewallRuleGroup"]["Id"]

    resp = client.associate_firewall_rule_group(
        FirewallRuleGroupId=rule_group_id,
        VpcId="vpc-12345",
        Name="test-assoc",
        Priority=101,
        MutationProtection="DISABLED",
    )
    assoc = resp["FirewallRuleGroupAssociation"]
    assert assoc["FirewallRuleGroupId"] == rule_group_id
    assert assoc["VpcId"] == "vpc-12345"
    assert assoc["Name"] == "test-assoc"
    assert assoc["Priority"] == 101
    assert assoc["Status"] == "COMPLETE"
    assert assoc["Id"].startswith("rslvr-frgassoc-")


@mock_aws
def test_get_firewall_rule_group_association():
    client = boto3.client("route53resolver", region_name="us-east-1")
    rule_group = client.create_firewall_rule_group(Name="test-rg")
    rule_group_id = rule_group["FirewallRuleGroup"]["Id"]

    assoc_resp = client.associate_firewall_rule_group(
        FirewallRuleGroupId=rule_group_id,
        VpcId="vpc-12345",
        Name="test-assoc",
        Priority=101,
    )
    assoc_id = assoc_resp["FirewallRuleGroupAssociation"]["Id"]

    get_resp = client.get_firewall_rule_group_association(
        FirewallRuleGroupAssociationId=assoc_id
    )
    assert get_resp["FirewallRuleGroupAssociation"]["Id"] == assoc_id
    assert get_resp["FirewallRuleGroupAssociation"]["VpcId"] == "vpc-12345"


@mock_aws
def test_disassociate_firewall_rule_group():
    client = boto3.client("route53resolver", region_name="us-east-1")
    rule_group = client.create_firewall_rule_group(Name="test-rg")
    rule_group_id = rule_group["FirewallRuleGroup"]["Id"]

    assoc_resp = client.associate_firewall_rule_group(
        FirewallRuleGroupId=rule_group_id,
        VpcId="vpc-12345",
        Name="test-assoc",
        Priority=101,
    )
    assoc_id = assoc_resp["FirewallRuleGroupAssociation"]["Id"]

    dis_resp = client.disassociate_firewall_rule_group(
        FirewallRuleGroupAssociationId=assoc_id
    )
    assert dis_resp["FirewallRuleGroupAssociation"]["Status"] == "DELETING"

    with pytest.raises(ClientError) as exc:
        client.get_firewall_rule_group_association(
            FirewallRuleGroupAssociationId=assoc_id
        )
    assert exc.value.response["Error"]["Code"] == "ResourceNotFoundException"


@mock_aws
def test_list_firewall_rule_group_associations():
    client = boto3.client("route53resolver", region_name="us-east-1")
    rg1 = client.create_firewall_rule_group(Name="rg1")
    rg1_id = rg1["FirewallRuleGroup"]["Id"]
    rg2 = client.create_firewall_rule_group(Name="rg2")
    rg2_id = rg2["FirewallRuleGroup"]["Id"]

    client.associate_firewall_rule_group(
        FirewallRuleGroupId=rg1_id,
        VpcId="vpc-111",
        Name="assoc-1",
        Priority=100,
    )
    client.associate_firewall_rule_group(
        FirewallRuleGroupId=rg2_id,
        VpcId="vpc-222",
        Name="assoc-2",
        Priority=200,
    )

    # List all
    resp = client.list_firewall_rule_group_associations()
    assert len(resp["FirewallRuleGroupAssociations"]) == 2

    # Filter by rule group id
    resp = client.list_firewall_rule_group_associations(
        FirewallRuleGroupId=rg1_id
    )
    assert len(resp["FirewallRuleGroupAssociations"]) == 1
    assert resp["FirewallRuleGroupAssociations"][0]["FirewallRuleGroupId"] == rg1_id

    # Filter by VPC id
    resp = client.list_firewall_rule_group_associations(VpcId="vpc-222")
    assert len(resp["FirewallRuleGroupAssociations"]) == 1
    assert resp["FirewallRuleGroupAssociations"][0]["VpcId"] == "vpc-222"


@mock_aws
def test_delete_rule_group_with_association_fails():
    """Cannot delete a rule group that still has VPC associations."""
    client = boto3.client("route53resolver", region_name="us-east-1")
    rg = client.create_firewall_rule_group(Name="rg")
    rg_id = rg["FirewallRuleGroup"]["Id"]

    client.associate_firewall_rule_group(
        FirewallRuleGroupId=rg_id,
        VpcId="vpc-111",
        Name="assoc",
        Priority=100,
    )

    with pytest.raises(ClientError) as exc:
        client.delete_firewall_rule_group(FirewallRuleGroupId=rg_id)
    assert exc.value.response["Error"]["Code"] == "ResourceInUseException"


@mock_aws
def test_delete_domain_list_with_rule_fails():
    """Cannot delete a domain list referenced by a rule."""
    client = boto3.client("route53resolver", region_name="us-east-1")
    dl = client.create_firewall_domain_list(Name="dl")
    dl_id = dl["FirewallDomainList"]["Id"]
    rg = client.create_firewall_rule_group(Name="rg")
    rg_id = rg["FirewallRuleGroup"]["Id"]

    client.create_firewall_rule(
        FirewallRuleGroupId=rg_id,
        FirewallDomainListId=dl_id,
        Name="rule",
        Priority=100,
        Action="ALLOW",
    )

    with pytest.raises(ClientError) as exc:
        client.delete_firewall_domain_list(FirewallDomainListId=dl_id)
    assert exc.value.response["Error"]["Code"] == "ResourceInUseException"


# --- Query Log Config Delete/Disassociate ---


@mock_aws
def test_delete_resolver_query_log_config():
    client = boto3.client("route53resolver", region_name="us-east-1")
    resp = client.create_resolver_query_log_config(
        Name="test-qlc",
        DestinationArn="arn:aws:s3:::my-bucket",
        CreatorRequestId="creator-1",
    )
    config_id = resp["ResolverQueryLogConfig"]["Id"]

    delete_resp = client.delete_resolver_query_log_config(
        ResolverQueryLogConfigId=config_id
    )
    assert delete_resp["ResolverQueryLogConfig"]["Status"] == "DELETING"

    with pytest.raises(ClientError) as exc:
        client.get_resolver_query_log_config(ResolverQueryLogConfigId=config_id)
    assert exc.value.response["Error"]["Code"] == "ResourceNotFoundException"


@mock_aws
def test_delete_resolver_query_log_config_not_found():
    client = boto3.client("route53resolver", region_name="us-east-1")
    with pytest.raises(ClientError) as exc:
        client.delete_resolver_query_log_config(
            ResolverQueryLogConfigId="rslvr-qlc-fake"
        )
    assert exc.value.response["Error"]["Code"] == "ResourceNotFoundException"


@mock_aws
def test_disassociate_resolver_query_log_config():
    ec2_client = boto3.client("ec2", region_name="us-east-1")
    vpc = ec2_client.create_vpc(CidrBlock="10.0.0.0/16")
    vpc_id = vpc["Vpc"]["VpcId"]

    client = boto3.client("route53resolver", region_name="us-east-1")
    config_resp = client.create_resolver_query_log_config(
        Name="test-qlc",
        DestinationArn="arn:aws:s3:::my-bucket",
        CreatorRequestId="creator-1",
    )
    config_id = config_resp["ResolverQueryLogConfig"]["Id"]

    client.associate_resolver_query_log_config(
        ResolverQueryLogConfigId=config_id,
        ResourceId=vpc_id,
    )

    dis_resp = client.disassociate_resolver_query_log_config(
        ResolverQueryLogConfigId=config_id,
        ResourceId=vpc_id,
    )
    assert dis_resp["ResolverQueryLogConfigAssociation"]["Status"] == "DELETING"

    # Association count should be decremented
    config = client.get_resolver_query_log_config(ResolverQueryLogConfigId=config_id)
    assert config["ResolverQueryLogConfig"]["AssociationCount"] == 0
