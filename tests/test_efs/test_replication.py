import boto3
import pytest

from moto import mock_aws


@pytest.fixture(scope="function", name="efs")
def fixture_efs():
    with mock_aws():
        yield boto3.client("efs", region_name="us-east-1")


def test_create_replication_configuration(efs):
    fs = efs.create_file_system(CreationToken="token1")
    fs_id = fs["FileSystemId"]

    resp = efs.create_replication_configuration(
        SourceFileSystemId=fs_id,
        Destinations=[{"Region": "us-west-2"}],
    )
    assert resp["SourceFileSystemId"] == fs_id
    assert resp["SourceFileSystemRegion"] == "us-east-1"
    assert "SourceFileSystemArn" in resp
    assert "OriginalSourceFileSystemArn" in resp
    assert "CreationTime" in resp
    assert "SourceFileSystemOwnerId" in resp
    assert len(resp["Destinations"]) == 1
    dest = resp["Destinations"][0]
    assert dest["Region"] == "us-west-2"
    assert dest["Status"] == "ENABLED"
    assert "FileSystemId" in dest


def test_create_replication_configuration_already_exists(efs):
    fs = efs.create_file_system(CreationToken="token1")
    fs_id = fs["FileSystemId"]

    efs.create_replication_configuration(
        SourceFileSystemId=fs_id,
        Destinations=[{"Region": "us-west-2"}],
    )

    with pytest.raises(efs.exceptions.ClientError) as exc:
        efs.create_replication_configuration(
            SourceFileSystemId=fs_id,
            Destinations=[{"Region": "eu-west-1"}],
        )
    assert "ReplicationAlreadyExists" in str(exc.value)


def test_create_replication_configuration_fs_not_found(efs):
    with pytest.raises(efs.exceptions.ClientError) as exc:
        efs.create_replication_configuration(
            SourceFileSystemId="fs-00000000",
            Destinations=[{"Region": "us-west-2"}],
        )
    assert "FileSystemNotFound" in str(exc.value)


def test_delete_replication_configuration(efs):
    fs = efs.create_file_system(CreationToken="token1")
    fs_id = fs["FileSystemId"]

    efs.create_replication_configuration(
        SourceFileSystemId=fs_id,
        Destinations=[{"Region": "us-west-2"}],
    )

    efs.delete_replication_configuration(SourceFileSystemId=fs_id)

    # After deletion, describe should return empty
    resp = efs.describe_replication_configurations(FileSystemId=fs_id)
    assert resp["Replications"] == []


def test_delete_replication_configuration_not_found(efs):
    fs = efs.create_file_system(CreationToken="token1")
    fs_id = fs["FileSystemId"]

    with pytest.raises(efs.exceptions.ClientError) as exc:
        efs.delete_replication_configuration(SourceFileSystemId=fs_id)
    assert "ReplicationNotFound" in str(exc.value)


def test_describe_replication_configurations(efs):
    fs1 = efs.create_file_system(CreationToken="token1")
    fs2 = efs.create_file_system(CreationToken="token2")

    efs.create_replication_configuration(
        SourceFileSystemId=fs1["FileSystemId"],
        Destinations=[{"Region": "us-west-2"}],
    )

    # Describe for specific filesystem
    resp = efs.describe_replication_configurations(
        FileSystemId=fs1["FileSystemId"]
    )
    assert len(resp["Replications"]) == 1

    # Describe for filesystem without replication
    resp = efs.describe_replication_configurations(
        FileSystemId=fs2["FileSystemId"]
    )
    assert len(resp["Replications"]) == 0
