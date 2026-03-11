import boto3

from moto import mock_aws


@mock_aws
def test_describe_account_limits():
    client = boto3.client("elb", region_name="us-east-1")
    resp = client.describe_account_limits()

    limits = resp["Limits"]
    assert len(limits) == 3

    limit_map = {l["Name"]: l["Max"] for l in limits}
    assert "classic-load-balancers" in limit_map
    assert "classic-listeners" in limit_map
    assert "classic-registered-instances" in limit_map
    assert limit_map["classic-load-balancers"] == "20"
    assert limit_map["classic-listeners"] == "100"
    assert limit_map["classic-registered-instances"] == "1000"


@mock_aws
def test_describe_load_balancer_policy_types():
    client = boto3.client("elb", region_name="us-east-1")
    resp = client.describe_load_balancer_policy_types()

    policy_types = resp["PolicyTypeDescriptions"]
    assert len(policy_types) >= 6

    type_names = [pt["PolicyTypeName"] for pt in policy_types]
    assert "SSLNegotiationPolicyType" in type_names
    assert "AppCookieStickinessPolicyType" in type_names
    assert "LBCookieStickinessPolicyType" in type_names
    assert "ProxyProtocolPolicyType" in type_names
    assert "BackendServerAuthenticationPolicyType" in type_names
    assert "PublicKeyPolicyType" in type_names

    # Each policy type should have a description and attribute type descriptions
    for pt in policy_types:
        assert "Description" in pt
        assert "PolicyAttributeTypeDescriptions" in pt
        assert len(pt["PolicyAttributeTypeDescriptions"]) >= 1


@mock_aws
def test_describe_load_balancer_policy_types_filtered():
    client = boto3.client("elb", region_name="us-east-1")
    resp = client.describe_load_balancer_policy_types(
        PolicyTypeNames=["SSLNegotiationPolicyType"]
    )

    policy_types = resp["PolicyTypeDescriptions"]
    assert len(policy_types) == 1
    assert policy_types[0]["PolicyTypeName"] == "SSLNegotiationPolicyType"

    # Verify attributes are present
    attrs = policy_types[0]["PolicyAttributeTypeDescriptions"]
    attr_names = [a["AttributeName"] for a in attrs]
    assert "Protocol-TLSv1.2" in attr_names
