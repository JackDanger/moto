import json

import boto3
import pytest
from botocore.exceptions import ClientError

from moto import mock_aws


@mock_aws
def test_put_and_get_data_protection_policy():
    client = boto3.client("sns", region_name="us-east-1")
    topic_arn = client.create_topic(Name="test-topic")["TopicArn"]

    policy = json.dumps(
        {
            "Name": "__default_data_protection_policy",
            "Description": "Default data protection policy",
            "Version": "2021-06-01",
            "Statement": [
                {
                    "DataDirection": "Inbound",
                    "Principal": ["*"],
                    "DataIdentifier": [
                        "arn:aws:dataprotection::aws:data-identifier/CreditCardNumber",
                    ],
                    "Operation": {"Deny": {}},
                }
            ],
        }
    )

    client.put_data_protection_policy(
        ResourceArn=topic_arn, DataProtectionPolicy=policy
    )

    resp = client.get_data_protection_policy(ResourceArn=topic_arn)
    assert resp["DataProtectionPolicy"] == policy


@mock_aws
def test_get_data_protection_policy_default_empty():
    client = boto3.client("sns", region_name="us-east-1")
    topic_arn = client.create_topic(Name="test-topic")["TopicArn"]

    resp = client.get_data_protection_policy(ResourceArn=topic_arn)
    assert resp["DataProtectionPolicy"] == ""


@mock_aws
def test_get_data_protection_policy_topic_not_found():
    client = boto3.client("sns", region_name="us-east-1")

    with pytest.raises(ClientError) as exc:
        client.get_data_protection_policy(
            ResourceArn="arn:aws:sns:us-east-1:123456789012:nonexistent"
        )
    assert exc.value.response["Error"]["Code"] == "NotFound"


@mock_aws
def test_put_data_protection_policy_topic_not_found():
    client = boto3.client("sns", region_name="us-east-1")

    with pytest.raises(ClientError) as exc:
        client.put_data_protection_policy(
            ResourceArn="arn:aws:sns:us-east-1:123456789012:nonexistent",
            DataProtectionPolicy="{}",
        )
    assert exc.value.response["Error"]["Code"] == "NotFound"


@mock_aws
def test_put_data_protection_policy_overwrite():
    client = boto3.client("sns", region_name="us-east-1")
    topic_arn = client.create_topic(Name="test-topic")["TopicArn"]

    policy1 = json.dumps({"Name": "policy1", "Version": "2021-06-01", "Statement": []})
    policy2 = json.dumps({"Name": "policy2", "Version": "2021-06-01", "Statement": []})

    client.put_data_protection_policy(
        ResourceArn=topic_arn, DataProtectionPolicy=policy1
    )
    client.put_data_protection_policy(
        ResourceArn=topic_arn, DataProtectionPolicy=policy2
    )

    resp = client.get_data_protection_policy(ResourceArn=topic_arn)
    assert resp["DataProtectionPolicy"] == policy2
