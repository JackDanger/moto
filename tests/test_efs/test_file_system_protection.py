import boto3
import pytest

from moto import mock_aws


@pytest.fixture(scope="function", name="efs")
def fixture_efs():
    with mock_aws():
        yield boto3.client("efs", region_name="us-east-1")


def test_update_file_system_protection(efs):
    fs = efs.create_file_system(CreationToken="token1")
    fs_id = fs["FileSystemId"]

    resp = efs.update_file_system_protection(
        FileSystemId=fs_id,
        ReplicationOverwriteProtection="DISABLED",
    )
    assert resp["ReplicationOverwriteProtection"] == "DISABLED"


def test_update_file_system_protection_enable(efs):
    fs = efs.create_file_system(CreationToken="token1")
    fs_id = fs["FileSystemId"]

    # Disable first
    efs.update_file_system_protection(
        FileSystemId=fs_id,
        ReplicationOverwriteProtection="DISABLED",
    )

    # Re-enable
    resp = efs.update_file_system_protection(
        FileSystemId=fs_id,
        ReplicationOverwriteProtection="ENABLED",
    )
    assert resp["ReplicationOverwriteProtection"] == "ENABLED"


def test_update_file_system_protection_fs_not_found(efs):
    with pytest.raises(efs.exceptions.ClientError) as exc:
        efs.update_file_system_protection(
            FileSystemId="fs-00000000",
            ReplicationOverwriteProtection="DISABLED",
        )
    assert "FileSystemNotFound" in str(exc.value)
