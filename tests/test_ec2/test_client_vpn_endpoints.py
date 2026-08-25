import boto3
import pytest
from moto import mock_aws


@mock_aws
def test_create_client_vpn_endpoint():
    client = boto3.client("ec2", region_name="us-east-1")
    resp = client.create_client_vpn_endpoint(
        ClientCidrBlock="10.0.0.0/16",
        ServerCertificateArn="arn:aws:acm:us-east-1:123456789012:certificate/abc123",
        AuthenticationOptions=[
            {"Type": "certificate-authentication", "MutualAuthentication": {"ClientRootCertificateChainArn": "arn:aws:acm:us-east-1:123456789012:certificate/abc123"}}
        ],
        ConnectionLogOptions={"Enabled": False},
    )
    assert "ClientVpnEndpointId" in resp
    assert resp["ClientVpnEndpointId"].startswith("cvpn-endpoint-")
    assert resp["Status"]["Code"] == "pending-associate"
    assert "DnsName" in resp


@mock_aws
def test_describe_client_vpn_endpoints():
    client = boto3.client("ec2", region_name="us-east-1")
    resp1 = client.create_client_vpn_endpoint(
        ClientCidrBlock="10.0.0.0/16",
        ServerCertificateArn="arn:aws:acm:us-east-1:123456789012:certificate/abc123",
        AuthenticationOptions=[
            {"Type": "certificate-authentication", "MutualAuthentication": {"ClientRootCertificateChainArn": "arn:aws:acm:us-east-1:123456789012:certificate/abc123"}}
        ],
        ConnectionLogOptions={"Enabled": False},
    )
    endpoint_id = resp1["ClientVpnEndpointId"]

    resp = client.describe_client_vpn_endpoints()
    assert len(resp["ClientVpnEndpoints"]) == 1
    ep = resp["ClientVpnEndpoints"][0]
    assert ep["ClientVpnEndpointId"] == endpoint_id
    assert ep["ClientCidrBlock"] == "10.0.0.0/16"
    assert ep["ServerCertificateArn"] == "arn:aws:acm:us-east-1:123456789012:certificate/abc123"

    # Describe with filter
    resp = client.describe_client_vpn_endpoints(ClientVpnEndpointIds=[endpoint_id])
    assert len(resp["ClientVpnEndpoints"]) == 1


@mock_aws
def test_delete_client_vpn_endpoint():
    client = boto3.client("ec2", region_name="us-east-1")
    resp1 = client.create_client_vpn_endpoint(
        ClientCidrBlock="10.0.0.0/16",
        ServerCertificateArn="arn:aws:acm:us-east-1:123456789012:certificate/abc123",
        AuthenticationOptions=[
            {"Type": "certificate-authentication", "MutualAuthentication": {"ClientRootCertificateChainArn": "arn:aws:acm:us-east-1:123456789012:certificate/abc123"}}
        ],
        ConnectionLogOptions={"Enabled": False},
    )
    endpoint_id = resp1["ClientVpnEndpointId"]

    resp = client.delete_client_vpn_endpoint(ClientVpnEndpointId=endpoint_id)
    assert resp["Status"]["Code"] == "deleting"

    resp = client.describe_client_vpn_endpoints()
    assert len(resp["ClientVpnEndpoints"]) == 0


@mock_aws
def test_modify_client_vpn_endpoint():
    client = boto3.client("ec2", region_name="us-east-1")
    resp1 = client.create_client_vpn_endpoint(
        ClientCidrBlock="10.0.0.0/16",
        ServerCertificateArn="arn:aws:acm:us-east-1:123456789012:certificate/abc123",
        AuthenticationOptions=[
            {"Type": "certificate-authentication", "MutualAuthentication": {"ClientRootCertificateChainArn": "arn:aws:acm:us-east-1:123456789012:certificate/abc123"}}
        ],
        ConnectionLogOptions={"Enabled": False},
        Description="original",
    )
    endpoint_id = resp1["ClientVpnEndpointId"]

    resp = client.modify_client_vpn_endpoint(
        ClientVpnEndpointId=endpoint_id,
        Description="modified",
        VpnPort=1194,
    )
    assert resp["Return"] is True

    resp = client.describe_client_vpn_endpoints(ClientVpnEndpointIds=[endpoint_id])
    ep = resp["ClientVpnEndpoints"][0]
    assert ep["Description"] == "modified"
    assert ep["VpnPort"] == 1194
