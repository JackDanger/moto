import json

import boto3
import pytest
from botocore.exceptions import ClientError

from moto import mock_aws


@mock_aws
def test_put_account_policy():
    client = boto3.client("logs", region_name="us-east-1")
    policy_doc = json.dumps(
        {
            "Name": "test-policy",
            "Version": "1",
        }
    )
    resp = client.put_account_policy(
        policyName="test-policy",
        policyDocument=policy_doc,
        policyType="DATA_PROTECTION_POLICY",
    )
    policy = resp["accountPolicy"]
    assert policy["policyName"] == "test-policy"
    assert policy["policyDocument"] == policy_doc
    assert policy["policyType"] == "DATA_PROTECTION_POLICY"
    assert policy["scope"] == "ALL"
    assert "lastUpdatedTime" in policy
    assert policy["accountId"] == "123456789012"


@mock_aws
def test_put_account_policy_with_scope_and_selection_criteria():
    client = boto3.client("logs", region_name="us-east-1")
    policy_doc = json.dumps({"Name": "test"})
    resp = client.put_account_policy(
        policyName="test-policy",
        policyDocument=policy_doc,
        policyType="SUBSCRIPTION_FILTER_POLICY",
        scope="ALL",
        selectionCriteria="LogGroupName PREFIX \"/aws/\"",
    )
    policy = resp["accountPolicy"]
    assert policy["policyType"] == "SUBSCRIPTION_FILTER_POLICY"
    assert policy["scope"] == "ALL"
    assert policy["selectionCriteria"] == "LogGroupName PREFIX \"/aws/\""


@mock_aws
def test_describe_account_policies():
    client = boto3.client("logs", region_name="us-east-1")
    policy_doc = json.dumps({"Name": "test"})

    client.put_account_policy(
        policyName="policy-1",
        policyDocument=policy_doc,
        policyType="DATA_PROTECTION_POLICY",
    )
    client.put_account_policy(
        policyName="policy-2",
        policyDocument=policy_doc,
        policyType="DATA_PROTECTION_POLICY",
    )

    resp = client.describe_account_policies(
        policyType="DATA_PROTECTION_POLICY",
    )
    assert len(resp["accountPolicies"]) == 2

    # Filter by name
    resp = client.describe_account_policies(
        policyType="DATA_PROTECTION_POLICY",
        policyName="policy-1",
    )
    assert len(resp["accountPolicies"]) == 1
    assert resp["accountPolicies"][0]["policyName"] == "policy-1"


@mock_aws
def test_describe_account_policies_empty():
    client = boto3.client("logs", region_name="us-east-1")
    resp = client.describe_account_policies(
        policyType="DATA_PROTECTION_POLICY",
    )
    assert resp["accountPolicies"] == []


@mock_aws
def test_delete_account_policy():
    client = boto3.client("logs", region_name="us-east-1")
    policy_doc = json.dumps({"Name": "test"})

    client.put_account_policy(
        policyName="test-policy",
        policyDocument=policy_doc,
        policyType="DATA_PROTECTION_POLICY",
    )

    client.delete_account_policy(
        policyName="test-policy",
        policyType="DATA_PROTECTION_POLICY",
    )

    resp = client.describe_account_policies(
        policyType="DATA_PROTECTION_POLICY",
    )
    assert len(resp["accountPolicies"]) == 0


@mock_aws
def test_delete_account_policy_not_found():
    client = boto3.client("logs", region_name="us-east-1")
    with pytest.raises(ClientError) as exc:
        client.delete_account_policy(
            policyName="nonexistent",
            policyType="DATA_PROTECTION_POLICY",
        )
    assert exc.value.response["Error"]["Code"] == "ResourceNotFoundException"


@mock_aws
def test_put_account_policy_update():
    client = boto3.client("logs", region_name="us-east-1")
    policy_doc_1 = json.dumps({"Name": "v1"})
    policy_doc_2 = json.dumps({"Name": "v2"})

    client.put_account_policy(
        policyName="test-policy",
        policyDocument=policy_doc_1,
        policyType="DATA_PROTECTION_POLICY",
    )

    # Update same policy
    resp = client.put_account_policy(
        policyName="test-policy",
        policyDocument=policy_doc_2,
        policyType="DATA_PROTECTION_POLICY",
    )
    assert resp["accountPolicy"]["policyDocument"] == policy_doc_2

    # Should still be just 1 policy
    resp = client.describe_account_policies(
        policyType="DATA_PROTECTION_POLICY",
    )
    assert len(resp["accountPolicies"]) == 1
