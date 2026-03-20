import boto3
import pytest

from moto import mock_aws


@pytest.fixture(scope="function", name="efs")
def fixture_efs():
    with mock_aws():
        yield boto3.client("efs", region_name="us-east-1")


def test_create_tags(efs):
    fs = efs.create_file_system(CreationToken="token1")
    fs_id = fs["FileSystemId"]

    efs.create_tags(
        FileSystemId=fs_id,
        Tags=[{"Key": "env", "Value": "prod"}, {"Key": "team", "Value": "infra"}],
    )

    resp = efs.list_tags_for_resource(ResourceId=fs_id)
    tags = {t["Key"]: t["Value"] for t in resp["Tags"]}
    assert tags["env"] == "prod"
    assert tags["team"] == "infra"


def test_create_tags_fs_not_found(efs):
    with pytest.raises(efs.exceptions.ClientError) as exc:
        efs.create_tags(
            FileSystemId="fs-00000000",
            Tags=[{"Key": "k", "Value": "v"}],
        )
    assert "FileSystemNotFound" in str(exc.value)


def test_delete_tags(efs):
    fs = efs.create_file_system(
        CreationToken="token1",
        Tags=[
            {"Key": "key1", "Value": "val1"},
            {"Key": "key2", "Value": "val2"},
            {"Key": "key3", "Value": "val3"},
        ],
    )
    fs_id = fs["FileSystemId"]

    efs.delete_tags(FileSystemId=fs_id, TagKeys=["key1", "key3"])

    resp = efs.list_tags_for_resource(ResourceId=fs_id)
    tags = {t["Key"]: t["Value"] for t in resp["Tags"]}
    assert "key1" not in tags
    assert "key3" not in tags
    assert tags["key2"] == "val2"


def test_delete_tags_fs_not_found(efs):
    with pytest.raises(efs.exceptions.ClientError) as exc:
        efs.delete_tags(FileSystemId="fs-00000000", TagKeys=["key1"])
    assert "FileSystemNotFound" in str(exc.value)


def test_create_and_delete_tags_roundtrip(efs):
    fs = efs.create_file_system(CreationToken="token1")
    fs_id = fs["FileSystemId"]

    # Add tags via legacy API
    efs.create_tags(
        FileSystemId=fs_id,
        Tags=[{"Key": "a", "Value": "1"}, {"Key": "b", "Value": "2"}],
    )

    # Verify via describe_tags (legacy)
    resp = efs.describe_tags(FileSystemId=fs_id)
    tags = {t["Key"]: t["Value"] for t in resp["Tags"]}
    assert tags == {"a": "1", "b": "2"}

    # Delete one tag
    efs.delete_tags(FileSystemId=fs_id, TagKeys=["a"])

    resp = efs.describe_tags(FileSystemId=fs_id)
    tags = {t["Key"]: t["Value"] for t in resp["Tags"]}
    assert tags == {"b": "2"}
