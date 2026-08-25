import json

import boto3
import pytest
from botocore.exceptions import ClientError

from moto import mock_aws


@mock_aws
def test_put_index_policy():
    client = boto3.client("logs", region_name="us-east-1")
    client.create_log_group(logGroupName="/test/log-group")

    policy_doc = json.dumps({"Fields": ["@timestamp", "@message"]})
    resp = client.put_index_policy(
        logGroupIdentifier="/test/log-group",
        policyDocument=policy_doc,
    )
    policy = resp["indexPolicy"]
    assert policy["policyName"] == "default"
    assert policy["policyDocument"] == policy_doc
    assert "logGroupIdentifier" in policy
    assert "lastUpdateTime" in policy


@mock_aws
def test_put_index_policy_by_arn():
    client = boto3.client("logs", region_name="us-east-1")
    client.create_log_group(logGroupName="/test/log-group")

    policy_doc = json.dumps({"Fields": ["@timestamp"]})
    resp = client.put_index_policy(
        logGroupIdentifier="arn:aws:logs:us-east-1:123456789012:log-group:/test/log-group",
        policyDocument=policy_doc,
    )
    assert resp["indexPolicy"]["policyDocument"] == policy_doc


@mock_aws
def test_put_index_policy_nonexistent_group():
    client = boto3.client("logs", region_name="us-east-1")
    with pytest.raises(ClientError) as exc:
        client.put_index_policy(
            logGroupIdentifier="/nonexistent",
            policyDocument=json.dumps({"Fields": []}),
        )
    assert exc.value.response["Error"]["Code"] == "ResourceNotFoundException"


@mock_aws
def test_describe_index_policies():
    client = boto3.client("logs", region_name="us-east-1")
    client.create_log_group(logGroupName="/test/group-1")
    client.create_log_group(logGroupName="/test/group-2")

    policy_doc = json.dumps({"Fields": ["@timestamp"]})
    client.put_index_policy(
        logGroupIdentifier="/test/group-1",
        policyDocument=policy_doc,
    )
    client.put_index_policy(
        logGroupIdentifier="/test/group-2",
        policyDocument=policy_doc,
    )

    resp = client.describe_index_policies(
        logGroupIdentifiers=["/test/group-1"],
    )
    assert len(resp["indexPolicies"]) == 1

    resp = client.describe_index_policies(
        logGroupIdentifiers=["/test/group-1", "/test/group-2"],
    )
    assert len(resp["indexPolicies"]) == 2


@mock_aws
def test_describe_index_policies_empty():
    client = boto3.client("logs", region_name="us-east-1")
    resp = client.describe_index_policies(
        logGroupIdentifiers=["/nonexistent"],
    )
    assert resp["indexPolicies"] == []


@mock_aws
def test_delete_index_policy():
    client = boto3.client("logs", region_name="us-east-1")
    client.create_log_group(logGroupName="/test/log-group")

    policy_doc = json.dumps({"Fields": ["@timestamp"]})
    client.put_index_policy(
        logGroupIdentifier="/test/log-group",
        policyDocument=policy_doc,
    )

    client.delete_index_policy(
        logGroupIdentifier="/test/log-group",
    )

    resp = client.describe_index_policies(
        logGroupIdentifiers=["/test/log-group"],
    )
    assert len(resp["indexPolicies"]) == 0


@mock_aws
def test_delete_index_policy_not_found():
    client = boto3.client("logs", region_name="us-east-1")
    client.create_log_group(logGroupName="/test/log-group")

    with pytest.raises(ClientError) as exc:
        client.delete_index_policy(
            logGroupIdentifier="/test/log-group",
        )
    assert exc.value.response["Error"]["Code"] == "ResourceNotFoundException"


@mock_aws
def test_put_index_policy_update():
    client = boto3.client("logs", region_name="us-east-1")
    client.create_log_group(logGroupName="/test/log-group")

    policy_doc_1 = json.dumps({"Fields": ["@timestamp"]})
    policy_doc_2 = json.dumps({"Fields": ["@timestamp", "@message"]})

    client.put_index_policy(
        logGroupIdentifier="/test/log-group",
        policyDocument=policy_doc_1,
    )
    client.put_index_policy(
        logGroupIdentifier="/test/log-group",
        policyDocument=policy_doc_2,
    )

    resp = client.describe_index_policies(
        logGroupIdentifiers=["/test/log-group"],
    )
    assert len(resp["indexPolicies"]) == 1
    assert resp["indexPolicies"][0]["policyDocument"] == policy_doc_2
