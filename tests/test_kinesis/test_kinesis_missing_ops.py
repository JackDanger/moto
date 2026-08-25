import boto3
import pytest
from botocore.exceptions import ClientError

from moto import mock_aws


@mock_aws
def test_list_tags_for_resource():
    client = boto3.client("kinesis", region_name="us-east-1")
    client.create_stream(StreamName="my-stream", ShardCount=1)
    stream_arn = client.describe_stream(StreamName="my-stream")["StreamDescription"][
        "StreamARN"
    ]

    # Add tags via the older API
    client.add_tags_to_stream(StreamName="my-stream", Tags={"env": "test", "team": "dev"})

    # List via the newer ARN-based API
    resp = client.list_tags_for_resource(ResourceARN=stream_arn)
    tags = resp["Tags"]
    assert len(tags) == 2
    tag_dict = {t["Key"]: t["Value"] for t in tags}
    assert tag_dict == {"env": "test", "team": "dev"}


@mock_aws
def test_list_tags_for_resource_empty():
    client = boto3.client("kinesis", region_name="us-east-1")
    client.create_stream(StreamName="my-stream", ShardCount=1)
    stream_arn = client.describe_stream(StreamName="my-stream")["StreamDescription"][
        "StreamARN"
    ]
    resp = client.list_tags_for_resource(ResourceARN=stream_arn)
    assert resp["Tags"] == []


@mock_aws
def test_list_tags_for_resource_not_found():
    client = boto3.client("kinesis", region_name="us-east-1")
    with pytest.raises(ClientError) as exc:
        client.list_tags_for_resource(
            ResourceARN="arn:aws:kinesis:us-east-1:123456789012:stream/nonexistent"
        )
    assert exc.value.response["Error"]["Code"] == "ResourceNotFoundException"


@mock_aws
def test_tag_resource():
    client = boto3.client("kinesis", region_name="us-east-1")
    client.create_stream(StreamName="my-stream", ShardCount=1)
    stream_arn = client.describe_stream(StreamName="my-stream")["StreamDescription"][
        "StreamARN"
    ]

    # Tag via ARN-based API
    client.tag_resource(ResourceARN=stream_arn, Tags={"env": "prod", "version": "1"})

    # Verify via list_tags_for_resource
    resp = client.list_tags_for_resource(ResourceARN=stream_arn)
    tag_dict = {t["Key"]: t["Value"] for t in resp["Tags"]}
    assert tag_dict == {"env": "prod", "version": "1"}


@mock_aws
def test_tag_resource_overwrite():
    client = boto3.client("kinesis", region_name="us-east-1")
    client.create_stream(StreamName="my-stream", ShardCount=1)
    stream_arn = client.describe_stream(StreamName="my-stream")["StreamDescription"][
        "StreamARN"
    ]

    client.tag_resource(ResourceARN=stream_arn, Tags={"env": "dev"})
    client.tag_resource(ResourceARN=stream_arn, Tags={"env": "prod"})

    resp = client.list_tags_for_resource(ResourceARN=stream_arn)
    tag_dict = {t["Key"]: t["Value"] for t in resp["Tags"]}
    assert tag_dict["env"] == "prod"


@mock_aws
def test_tag_resource_not_found():
    client = boto3.client("kinesis", region_name="us-east-1")
    with pytest.raises(ClientError) as exc:
        client.tag_resource(
            ResourceARN="arn:aws:kinesis:us-east-1:123456789012:stream/nonexistent",
            Tags={"env": "test"},
        )
    assert exc.value.response["Error"]["Code"] == "ResourceNotFoundException"


@mock_aws
def test_untag_resource():
    client = boto3.client("kinesis", region_name="us-east-1")
    client.create_stream(StreamName="my-stream", ShardCount=1)
    stream_arn = client.describe_stream(StreamName="my-stream")["StreamDescription"][
        "StreamARN"
    ]

    client.tag_resource(ResourceARN=stream_arn, Tags={"env": "prod", "version": "1"})
    client.untag_resource(ResourceARN=stream_arn, TagKeys=["version"])

    resp = client.list_tags_for_resource(ResourceARN=stream_arn)
    tag_dict = {t["Key"]: t["Value"] for t in resp["Tags"]}
    assert tag_dict == {"env": "prod"}


@mock_aws
def test_untag_resource_nonexistent_key():
    """Untagging a key that doesn't exist should be a no-op."""
    client = boto3.client("kinesis", region_name="us-east-1")
    client.create_stream(StreamName="my-stream", ShardCount=1)
    stream_arn = client.describe_stream(StreamName="my-stream")["StreamDescription"][
        "StreamARN"
    ]

    client.tag_resource(ResourceARN=stream_arn, Tags={"env": "prod"})
    client.untag_resource(ResourceARN=stream_arn, TagKeys=["nonexistent"])

    resp = client.list_tags_for_resource(ResourceARN=stream_arn)
    assert len(resp["Tags"]) == 1


@mock_aws
def test_untag_resource_not_found():
    client = boto3.client("kinesis", region_name="us-east-1")
    with pytest.raises(ClientError) as exc:
        client.untag_resource(
            ResourceARN="arn:aws:kinesis:us-east-1:123456789012:stream/nonexistent",
            TagKeys=["env"],
        )
    assert exc.value.response["Error"]["Code"] == "ResourceNotFoundException"


@mock_aws
def test_subscribe_to_shard():
    """SubscribeToShard uses HTTP/2 event streaming which botocore can't parse
    from a standard JSON mock response. We verify the backend logic directly."""
    from moto.kinesis.models import kinesis_backends

    client = boto3.client("kinesis", region_name="us-east-1")
    client.create_stream(StreamName="my-stream", ShardCount=1)
    stream_arn = client.describe_stream(StreamName="my-stream")["StreamDescription"][
        "StreamARN"
    ]

    consumer = client.register_stream_consumer(
        StreamARN=stream_arn, ConsumerName="my-consumer"
    )["Consumer"]

    shards = client.list_shards(StreamName="my-stream")["Shards"]
    shard_id = shards[0]["ShardId"]

    # Test the backend directly since event streaming can't be parsed from JSON mock
    backend = kinesis_backends["123456789012"]["us-east-1"]
    result = backend.subscribe_to_shard(
        consumer_arn=consumer["ConsumerARN"],
        shard_id=shard_id,
        starting_position={"Type": "TRIM_HORIZON"},
    )
    assert "EventStream" in result
    event = result["EventStream"]["SubscribeToShardEvent"]
    assert "Records" in event
    assert "ContinuationSequenceNumber" in event
    assert "MillisBehindLatest" in event
    assert event["MillisBehindLatest"] == 0


@mock_aws
def test_subscribe_to_shard_consumer_not_found():
    """SubscribeToShard with unknown consumer raises ResourceNotFoundException."""
    from moto.kinesis.models import kinesis_backends

    client = boto3.client("kinesis", region_name="us-east-1")
    client.create_stream(StreamName="my-stream", ShardCount=1)

    backend = kinesis_backends["123456789012"]["us-east-1"]
    with pytest.raises(Exception) as exc:
        backend.subscribe_to_shard(
            consumer_arn="arn:aws:kinesis:us-east-1:123456789012:stream/my-stream/consumer/nonexistent",
            shard_id="shardId-000000000000",
            starting_position={"Type": "TRIM_HORIZON"},
        )
    assert "ResourceNotFoundException" in str(type(exc.value).__mro__) or "not found" in str(exc.value).lower()


@mock_aws
def test_update_account_settings():
    client = boto3.client("kinesis", region_name="us-east-1")
    resp = client.update_account_settings(
        MinimumThroughputBillingCommitment={"Status": "ENABLED"}
    )
    assert resp["MinimumThroughputBillingCommitment"]["Status"] == "ENABLED"


@mock_aws
def test_update_account_settings_disable():
    client = boto3.client("kinesis", region_name="us-east-1")
    client.update_account_settings(
        MinimumThroughputBillingCommitment={"Status": "ENABLED"}
    )
    resp = client.update_account_settings(
        MinimumThroughputBillingCommitment={"Status": "DISABLED"}
    )
    assert resp["MinimumThroughputBillingCommitment"]["Status"] == "DISABLED"


@mock_aws
def test_update_max_record_size():
    client = boto3.client("kinesis", region_name="us-east-1")
    client.create_stream(StreamName="my-stream", ShardCount=1)
    stream_arn = client.describe_stream(StreamName="my-stream")["StreamDescription"][
        "StreamARN"
    ]

    # Update max record size - no output, just verifying it doesn't error
    client.update_max_record_size(StreamARN=stream_arn, MaxRecordSizeInKiB=10240)


@mock_aws
def test_update_max_record_size_not_found():
    client = boto3.client("kinesis", region_name="us-east-1")
    with pytest.raises(ClientError) as exc:
        client.update_max_record_size(
            StreamARN="arn:aws:kinesis:us-east-1:123456789012:stream/nonexistent",
            MaxRecordSizeInKiB=10240,
        )
    assert exc.value.response["Error"]["Code"] == "ResourceNotFoundException"


@mock_aws
def test_update_stream_warm_throughput():
    client = boto3.client("kinesis", region_name="us-east-1")
    client.create_stream(StreamName="my-stream", ShardCount=1)
    stream_arn = client.describe_stream(StreamName="my-stream")["StreamDescription"][
        "StreamARN"
    ]

    resp = client.update_stream_warm_throughput(
        StreamARN=stream_arn, WarmThroughputMiBps=5
    )
    assert resp["StreamARN"] == stream_arn
    assert resp["StreamName"] == "my-stream"
    assert resp["WarmThroughput"]["TargetMiBps"] == 5
    assert resp["WarmThroughput"]["CurrentMiBps"] == 5


@mock_aws
def test_update_stream_warm_throughput_not_found():
    client = boto3.client("kinesis", region_name="us-east-1")
    with pytest.raises(ClientError) as exc:
        client.update_stream_warm_throughput(
            StreamARN="arn:aws:kinesis:us-east-1:123456789012:stream/nonexistent",
            WarmThroughputMiBps=5,
        )
    assert exc.value.response["Error"]["Code"] == "ResourceNotFoundException"


@mock_aws
def test_tags_interop_old_and_new_api():
    """Verify tags set via TagResource are visible via ListTagsForStream and vice versa."""
    client = boto3.client("kinesis", region_name="us-east-1")
    client.create_stream(StreamName="my-stream", ShardCount=1)
    stream_arn = client.describe_stream(StreamName="my-stream")["StreamDescription"][
        "StreamARN"
    ]

    # Set via new API
    client.tag_resource(ResourceARN=stream_arn, Tags={"new_api": "yes"})

    # Read via old API
    resp = client.list_tags_for_stream(StreamName="my-stream")
    tag_dict = {t["Key"]: t["Value"] for t in resp["Tags"]}
    assert tag_dict["new_api"] == "yes"

    # Set via old API
    client.add_tags_to_stream(StreamName="my-stream", Tags={"old_api": "yes"})

    # Read via new API
    resp = client.list_tags_for_resource(ResourceARN=stream_arn)
    tag_dict = {t["Key"]: t["Value"] for t in resp["Tags"]}
    assert tag_dict["old_api"] == "yes"
    assert tag_dict["new_api"] == "yes"
