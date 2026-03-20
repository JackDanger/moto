import boto3
import pytest
from moto import mock_aws


@mock_aws
def test_create_ipam():
    client = boto3.client("ec2", region_name="us-east-1")
    resp = client.create_ipam(
        Description="test ipam",
        OperatingRegions=[{"RegionName": "us-east-1"}],
    )
    ipam = resp["Ipam"]
    assert ipam["IpamId"].startswith("ipam-")
    assert "IpamArn" in ipam
    assert ipam["Description"] == "test ipam"
    assert ipam["State"] == "create-complete"
    assert ipam["ScopeCount"] == 2
    assert ipam["PublicDefaultScopeId"].startswith("ipam-scope-")
    assert ipam["PrivateDefaultScopeId"].startswith("ipam-scope-")
    assert len(ipam["OperatingRegions"]) == 1
    assert ipam["OperatingRegions"][0]["RegionName"] == "us-east-1"


@mock_aws
def test_describe_ipams():
    client = boto3.client("ec2", region_name="us-east-1")
    resp1 = client.create_ipam(Description="ipam1")
    resp2 = client.create_ipam(Description="ipam2")

    resp = client.describe_ipams()
    assert len(resp["Ipams"]) == 2

    # Filter by ID
    ipam_id = resp1["Ipam"]["IpamId"]
    resp = client.describe_ipams(IpamIds=[ipam_id])
    assert len(resp["Ipams"]) == 1
    assert resp["Ipams"][0]["IpamId"] == ipam_id


@mock_aws
def test_delete_ipam():
    client = boto3.client("ec2", region_name="us-east-1")
    resp1 = client.create_ipam(Description="to delete")
    ipam_id = resp1["Ipam"]["IpamId"]

    resp = client.delete_ipam(IpamId=ipam_id)
    assert resp["Ipam"]["IpamId"] == ipam_id
    assert resp["Ipam"]["State"] == "delete-complete"

    resp = client.describe_ipams()
    assert len(resp["Ipams"]) == 0


@mock_aws
def test_create_ipam_pool():
    client = boto3.client("ec2", region_name="us-east-1")
    ipam = client.create_ipam(Description="test")["Ipam"]
    scope_id = ipam["PrivateDefaultScopeId"]

    resp = client.create_ipam_pool(
        IpamScopeId=scope_id,
        AddressFamily="ipv4",
        Description="test pool",
    )
    pool = resp["IpamPool"]
    assert pool["IpamPoolId"].startswith("ipam-pool-")
    assert "IpamPoolArn" in pool
    assert pool["AddressFamily"] == "ipv4"
    assert pool["Description"] == "test pool"
    assert pool["State"] == "create-complete"


@mock_aws
def test_describe_ipam_pools():
    client = boto3.client("ec2", region_name="us-east-1")
    ipam = client.create_ipam(Description="test")["Ipam"]
    scope_id = ipam["PrivateDefaultScopeId"]

    client.create_ipam_pool(IpamScopeId=scope_id, AddressFamily="ipv4", Description="pool1")
    client.create_ipam_pool(IpamScopeId=scope_id, AddressFamily="ipv4", Description="pool2")

    resp = client.describe_ipam_pools()
    assert len(resp["IpamPools"]) == 2
