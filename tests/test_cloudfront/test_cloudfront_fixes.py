"""Tests for CloudFront 500-error fixes."""

import json

import boto3
import pytest
from botocore.exceptions import ClientError

from moto import mock_aws


@mock_aws
def test_create_key_group():
    client = boto3.client("cloudfront", region_name="us-east-1")
    # First create a public key
    resp = client.create_public_key(
        PublicKeyConfig={
            "CallerReference": "ref1",
            "Name": "test-key",
            "EncodedKey": (
                "-----BEGIN PUBLIC KEY-----\n"
                "MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA2a3anb4GOMXQ79cM+TkQ\n"
                "oUBJn4I5kAEi4JY9OoYU3MrvkBPOjNMPcFjhFKBOTvPY4v+8fC/bFGcuMG1E3MR\n"
                "QKCRgKOPOOvI9XJqYEgpRQKEuLzMEMy2aIRMz+g0VBEVBOkC/Iq8uFJkHkMOSBg\n"
                "YH5Q8RITFJLSBDXwrhO/SYhIOIFJnBCUHMfJJqYCwJYoG/7MCn4+D40YNsBaZdQF\n"
                "2FNMjEdKRUjFRHOVF5r2fOKGH8soGRHJlkqUZOCUKUDf0oTO/o9FZXO5LCe4Bk+\n"
                "IGPJRB7AhKYi2G4XO4G5basBwR0rV4KT4UmDQ7DERPJPhYE/hm6mS4WREKP7LkG\n"
                "bQIDAQAB\n"
                "-----END PUBLIC KEY-----\n"
            ),
        }
    )
    key_id = resp["PublicKey"]["Id"]

    # Now create a key group
    resp = client.create_key_group(
        KeyGroupConfig={
            "Name": "test-group",
            "Items": [key_id],
        }
    )
    assert resp["ResponseMetadata"]["HTTPStatusCode"] == 201
    assert "KeyGroup" in resp
    assert resp["KeyGroup"]["KeyGroupConfig"]["Name"] == "test-group"


@mock_aws
def test_get_key_group_not_found():
    client = boto3.client("cloudfront", region_name="us-east-1")
    with pytest.raises(ClientError) as exc:
        client.get_key_group(Id="nonexistent-id")
    assert exc.value.response["Error"]["Code"] == "NoSuchResource"


@mock_aws
def test_update_key_group_not_found():
    client = boto3.client("cloudfront", region_name="us-east-1")
    with pytest.raises(ClientError) as exc:
        client.update_key_group(
            Id="nonexistent-id",
            KeyGroupConfig={"Name": "test", "Items": ["key1"]},
            IfMatch="etag",
        )
    assert exc.value.response["Error"]["Code"] == "NoSuchResource"


@mock_aws
def test_get_public_key_not_found():
    client = boto3.client("cloudfront", region_name="us-east-1")
    with pytest.raises(ClientError) as exc:
        client.get_public_key(Id="nonexistent-id")
    assert exc.value.response["Error"]["Code"] == "NoSuchPublicKey"


@mock_aws
def test_delete_origin_access_control_not_found():
    client = boto3.client("cloudfront", region_name="us-east-1")
    with pytest.raises(ClientError) as exc:
        client.delete_origin_access_control(Id="nonexistent-id")
    assert exc.value.response["Error"]["Code"] == "NoSuchOriginAccessControl"


@mock_aws
def test_create_realtime_log_config():
    client = boto3.client("cloudfront", region_name="us-east-1")
    resp = client.create_realtime_log_config(
        EndPoints=[
            {
                "StreamType": "Kinesis",
                "KinesisStreamConfig": {
                    "RoleARN": "arn:aws:iam::123456789012:role/test",
                    "StreamARN": "arn:aws:kinesis:us-east-1:123456789012:stream/test",
                },
            }
        ],
        Fields=["timestamp", "c-ip"],
        Name="test-config",
        SamplingRate=100,
    )
    assert resp["ResponseMetadata"]["HTTPStatusCode"] == 201
    assert "RealtimeLogConfig" in resp
    assert resp["RealtimeLogConfig"]["Name"] == "test-config"


@mock_aws
def test_update_realtime_log_config():
    client = boto3.client("cloudfront", region_name="us-east-1")
    # Create first
    client.create_realtime_log_config(
        EndPoints=[
            {
                "StreamType": "Kinesis",
                "KinesisStreamConfig": {
                    "RoleARN": "arn:aws:iam::123456789012:role/test",
                    "StreamARN": "arn:aws:kinesis:us-east-1:123456789012:stream/test",
                },
            }
        ],
        Fields=["timestamp", "c-ip"],
        Name="test-config",
        SamplingRate=100,
    )
    # Update
    resp = client.update_realtime_log_config(
        Name="test-config",
        SamplingRate=50,
    )
    assert resp["ResponseMetadata"]["HTTPStatusCode"] == 200
    assert resp["RealtimeLogConfig"]["SamplingRate"] == 50


@mock_aws
def test_create_streaming_distribution_with_tags():
    client = boto3.client("cloudfront", region_name="us-east-1")
    resp = client.create_streaming_distribution_with_tags(
        StreamingDistributionConfigWithTags={
            "StreamingDistributionConfig": {
                "CallerReference": "ref1",
                "S3Origin": {
                    "DomainName": "mybucket.s3.amazonaws.com",
                    "OriginAccessIdentity": "",
                },
                "Comment": "test",
                "TrustedSigners": {"Enabled": False, "Quantity": 0},
                "Enabled": True,
            },
            "Tags": {"Items": [{"Key": "env", "Value": "test"}]},
        }
    )
    assert resp["ResponseMetadata"]["HTTPStatusCode"] == 201
    assert "StreamingDistribution" in resp


@mock_aws
def test_create_key_value_store():
    client = boto3.client("cloudfront", region_name="us-east-1")
    resp = client.create_key_value_store(Name="test-store")
    assert resp["ResponseMetadata"]["HTTPStatusCode"] == 201
    assert "KeyValueStore" in resp
    assert resp["KeyValueStore"]["Name"] == "test-store"


@mock_aws
def test_describe_key_value_store():
    client = boto3.client("cloudfront", region_name="us-east-1")
    client.create_key_value_store(Name="test-store")
    resp = client.describe_key_value_store(Name="test-store")
    assert resp["ResponseMetadata"]["HTTPStatusCode"] == 200
    assert "KeyValueStore" in resp


@mock_aws
def test_list_key_value_stores():
    client = boto3.client("cloudfront", region_name="us-east-1")
    resp = client.list_key_value_stores()
    assert resp["ResponseMetadata"]["HTTPStatusCode"] == 200
    assert "KeyValueStoreList" in resp
