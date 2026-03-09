"""Tests for newly implemented FSx operations."""

import boto3
import pytest
from botocore.exceptions import ClientError

from moto import mock_aws

TEST_REGION = "us-east-1"
FAKE_SUBNET = "subnet-012345678"
FAKE_SG = ["sg-0123456789abcdef0"]


@pytest.fixture(name="client")
def fixture_client():
    with mock_aws():
        yield boto3.client("fsx", region_name=TEST_REGION)


def _create_ontap_fs(client):
    resp = client.create_file_system(
        FileSystemType="ONTAP",
        StorageCapacity=1024,
        StorageType="SSD",
        SubnetIds=[FAKE_SUBNET],
        SecurityGroupIds=FAKE_SG,
        OntapConfiguration={
            "DeploymentType": "SINGLE_AZ_1",
            "ThroughputCapacity": 128,
        },
    )
    return resp["FileSystem"]["FileSystemId"]


def _create_lustre_fs(client):
    resp = client.create_file_system(
        FileSystemType="LUSTRE",
        StorageCapacity=1200,
        StorageType="SSD",
        SubnetIds=[FAKE_SUBNET],
        SecurityGroupIds=FAKE_SG,
    )
    return resp["FileSystem"]["FileSystemId"]


def _create_windows_fs(client):
    resp = client.create_file_system(
        FileSystemType="WINDOWS",
        StorageCapacity=32,
        StorageType="SSD",
        SubnetIds=[FAKE_SUBNET],
        SecurityGroupIds=FAKE_SG,
        WindowsConfiguration={
            "ThroughputCapacity": 8,
            "ActiveDirectoryId": "d-1234567890",
        },
    )
    return resp["FileSystem"]["FileSystemId"]


# --- UpdateFileSystem ---


class TestUpdateFileSystem:
    def test_update_storage_capacity(self, client):
        fs_id = _create_lustre_fs(client)
        resp = client.update_file_system(
            FileSystemId=fs_id,
            StorageCapacity=2400,
        )
        assert resp["FileSystem"]["StorageCapacity"] == 2400

    def test_update_lustre_configuration(self, client):
        fs_id = _create_lustre_fs(client)
        resp = client.update_file_system(
            FileSystemId=fs_id,
            LustreConfiguration={"WeeklyMaintenanceStartTime": "1:00:00"},
        )
        assert (
            resp["FileSystem"]["LustreConfiguration"]["WeeklyMaintenanceStartTime"]
            == "1:00:00"
        )

    def test_update_nonexistent_fs(self, client):
        with pytest.raises(ClientError) as exc:
            client.update_file_system(
                FileSystemId="fs-nonexistent",
                StorageCapacity=100,
            )
        assert exc.value.response["Error"]["Code"] == "FileSystemNotFound"


# --- CreateFileSystemFromBackup ---


class TestCreateFileSystemFromBackup:
    def test_create_from_backup(self, client):
        fs_id = _create_lustre_fs(client)
        backup = client.create_backup(FileSystemId=fs_id)
        backup_id = backup["Backup"]["BackupId"]

        resp = client.create_file_system_from_backup(
            BackupId=backup_id,
            SubnetIds=[FAKE_SUBNET],
            SecurityGroupIds=FAKE_SG,
        )
        new_fs = resp["FileSystem"]
        assert new_fs["FileSystemId"] != fs_id
        assert new_fs["FileSystemType"] == "LUSTRE"
        assert new_fs["StorageCapacity"] == 1200

    def test_from_nonexistent_backup(self, client):
        with pytest.raises(ClientError) as exc:
            client.create_file_system_from_backup(
                BackupId="backup-nonexist",
                SubnetIds=[FAKE_SUBNET],
            )
        assert exc.value.response["Error"]["Code"] == "BackupNotFound"


# --- StorageVirtualMachine ---


class TestStorageVirtualMachine:
    def test_create_svm(self, client):
        fs_id = _create_ontap_fs(client)
        resp = client.create_storage_virtual_machine(
            FileSystemId=fs_id,
            Name="test-svm",
        )
        svm = resp["StorageVirtualMachine"]
        assert svm["Name"] == "test-svm"
        assert svm["FileSystemId"] == fs_id
        assert svm["Lifecycle"] == "CREATED"
        assert svm["StorageVirtualMachineId"].startswith("svm-")
        assert svm["RootVolumeSecurityStyle"] == "UNIX"

    def test_describe_svms(self, client):
        fs_id = _create_ontap_fs(client)
        client.create_storage_virtual_machine(FileSystemId=fs_id, Name="svm-1")
        client.create_storage_virtual_machine(FileSystemId=fs_id, Name="svm-2")

        resp = client.describe_storage_virtual_machines()
        assert len(resp["StorageVirtualMachines"]) == 2

    def test_describe_svm_by_id(self, client):
        fs_id = _create_ontap_fs(client)
        create_resp = client.create_storage_virtual_machine(
            FileSystemId=fs_id, Name="svm-1"
        )
        svm_id = create_resp["StorageVirtualMachine"]["StorageVirtualMachineId"]

        resp = client.describe_storage_virtual_machines(
            StorageVirtualMachineIds=[svm_id]
        )
        assert len(resp["StorageVirtualMachines"]) == 1
        assert resp["StorageVirtualMachines"][0]["Name"] == "svm-1"

    def test_delete_svm(self, client):
        fs_id = _create_ontap_fs(client)
        create_resp = client.create_storage_virtual_machine(
            FileSystemId=fs_id, Name="svm-del"
        )
        svm_id = create_resp["StorageVirtualMachine"]["StorageVirtualMachineId"]

        resp = client.delete_storage_virtual_machine(
            StorageVirtualMachineId=svm_id
        )
        assert resp["Lifecycle"] == "DELETING"

        desc = client.describe_storage_virtual_machines()
        assert len(desc["StorageVirtualMachines"]) == 0

    def test_create_svm_nonexistent_fs(self, client):
        with pytest.raises(ClientError) as exc:
            client.create_storage_virtual_machine(
                FileSystemId="fs-nonexist", Name="bad"
            )
        assert exc.value.response["Error"]["Code"] == "FileSystemNotFound"


# --- Volume ---


class TestVolume:
    def test_create_volume(self, client):
        fs_id = _create_ontap_fs(client)
        svm = client.create_storage_virtual_machine(
            FileSystemId=fs_id, Name="svm-vol"
        )
        svm_id = svm["StorageVirtualMachine"]["StorageVirtualMachineId"]

        resp = client.create_volume(
            VolumeType="ONTAP",
            Name="test-vol",
            OntapConfiguration={
                "StorageVirtualMachineId": svm_id,
                "SizeInMegabytes": 1024,
                "JunctionPath": "/vol1",
                "StorageEfficiencyEnabled": True,
            },
        )
        vol = resp["Volume"]
        assert vol["Name"] == "test-vol"
        assert vol["VolumeType"] == "ONTAP"
        assert vol["VolumeId"].startswith("fsvol-")
        assert vol["Lifecycle"] == "CREATED"

    def test_describe_volumes(self, client):
        fs_id = _create_ontap_fs(client)
        svm = client.create_storage_virtual_machine(
            FileSystemId=fs_id, Name="svm-desc"
        )
        svm_id = svm["StorageVirtualMachine"]["StorageVirtualMachineId"]

        client.create_volume(
            VolumeType="ONTAP",
            Name="vol-1",
            OntapConfiguration={
                "StorageVirtualMachineId": svm_id,
                "SizeInMegabytes": 512,
                "JunctionPath": "/v1",
                "StorageEfficiencyEnabled": True,
            },
        )
        client.create_volume(
            VolumeType="ONTAP",
            Name="vol-2",
            OntapConfiguration={
                "StorageVirtualMachineId": svm_id,
                "SizeInMegabytes": 512,
                "JunctionPath": "/v2",
                "StorageEfficiencyEnabled": True,
            },
        )
        resp = client.describe_volumes()
        assert len(resp["Volumes"]) == 2

    def test_delete_volume(self, client):
        fs_id = _create_ontap_fs(client)
        svm = client.create_storage_virtual_machine(
            FileSystemId=fs_id, Name="svm-dv"
        )
        svm_id = svm["StorageVirtualMachine"]["StorageVirtualMachineId"]

        vol = client.create_volume(
            VolumeType="ONTAP",
            Name="del-vol",
            OntapConfiguration={
                "StorageVirtualMachineId": svm_id,
                "SizeInMegabytes": 256,
                "JunctionPath": "/dv",
                "StorageEfficiencyEnabled": True,
            },
        )
        vol_id = vol["Volume"]["VolumeId"]
        resp = client.delete_volume(VolumeId=vol_id)
        assert resp["Lifecycle"] == "DELETING"

        desc = client.describe_volumes()
        assert len(desc["Volumes"]) == 0

    def test_create_volume_from_backup(self, client):
        fs_id = _create_ontap_fs(client)
        svm = client.create_storage_virtual_machine(
            FileSystemId=fs_id, Name="svm-bk"
        )
        svm_id = svm["StorageVirtualMachine"]["StorageVirtualMachineId"]

        backup = client.create_backup(FileSystemId=fs_id)
        backup_id = backup["Backup"]["BackupId"]

        resp = client.create_volume_from_backup(
            BackupId=backup_id,
            Name="vol-from-backup",
            OntapConfiguration={
                "StorageVirtualMachineId": svm_id,
                "SizeInMegabytes": 512,
                "JunctionPath": "/vfb",
                "StorageEfficiencyEnabled": True,
            },
        )
        vol = resp["Volume"]
        assert vol["Name"] == "vol-from-backup"
        assert vol["VolumeType"] == "ONTAP"


# --- Snapshot ---


class TestSnapshot:
    def _make_volume(self, client):
        fs_id = _create_ontap_fs(client)
        svm = client.create_storage_virtual_machine(
            FileSystemId=fs_id, Name="svm-snap"
        )
        svm_id = svm["StorageVirtualMachine"]["StorageVirtualMachineId"]
        vol = client.create_volume(
            VolumeType="ONTAP",
            Name="snap-vol",
            OntapConfiguration={
                "StorageVirtualMachineId": svm_id,
                "SizeInMegabytes": 256,
                "JunctionPath": "/sv",
                "StorageEfficiencyEnabled": True,
            },
        )
        return vol["Volume"]["VolumeId"]

    def test_create_snapshot(self, client):
        vol_id = self._make_volume(client)
        resp = client.create_snapshot(Name="my-snap", VolumeId=vol_id)
        snap = resp["Snapshot"]
        assert snap["Name"] == "my-snap"
        assert snap["VolumeId"] == vol_id
        assert snap["Lifecycle"] == "AVAILABLE"
        assert snap["SnapshotId"].startswith("fsvolsnap-")

    def test_describe_snapshots(self, client):
        vol_id = self._make_volume(client)
        client.create_snapshot(Name="s1", VolumeId=vol_id)
        client.create_snapshot(Name="s2", VolumeId=vol_id)
        resp = client.describe_snapshots()
        assert len(resp["Snapshots"]) == 2

    def test_delete_snapshot(self, client):
        vol_id = self._make_volume(client)
        snap = client.create_snapshot(Name="del-snap", VolumeId=vol_id)
        snap_id = snap["Snapshot"]["SnapshotId"]
        resp = client.delete_snapshot(SnapshotId=snap_id)
        assert resp["Lifecycle"] == "DELETING"

        desc = client.describe_snapshots()
        assert len(desc["Snapshots"]) == 0

    def test_update_snapshot(self, client):
        vol_id = self._make_volume(client)
        snap = client.create_snapshot(Name="old-name", VolumeId=vol_id)
        snap_id = snap["Snapshot"]["SnapshotId"]

        resp = client.update_snapshot(SnapshotId=snap_id, Name="new-name")
        assert resp["Snapshot"]["Name"] == "new-name"

    def test_delete_nonexistent_snapshot(self, client):
        with pytest.raises(ClientError) as exc:
            client.delete_snapshot(SnapshotId="fsvolsnap-nonexist")
        assert exc.value.response["Error"]["Code"] == "SnapshotNotFound"


# --- File System Aliases ---


class TestFileSystemAliases:
    def test_associate_aliases(self, client):
        fs_id = _create_windows_fs(client)
        resp = client.associate_file_system_aliases(
            FileSystemId=fs_id,
            Aliases=["accounting.example.com", "finance.example.com"],
        )
        assert len(resp["Aliases"]) == 2
        assert resp["Aliases"][0]["Lifecycle"] == "AVAILABLE"

    def test_describe_aliases(self, client):
        fs_id = _create_windows_fs(client)
        client.associate_file_system_aliases(
            FileSystemId=fs_id, Aliases=["test.example.com"]
        )
        resp = client.describe_file_system_aliases(FileSystemId=fs_id)
        assert len(resp["Aliases"]) == 1
        assert resp["Aliases"][0]["Name"] == "test.example.com"

    def test_disassociate_aliases(self, client):
        fs_id = _create_windows_fs(client)
        client.associate_file_system_aliases(
            FileSystemId=fs_id, Aliases=["a.example.com", "b.example.com"]
        )
        resp = client.disassociate_file_system_aliases(
            FileSystemId=fs_id, Aliases=["a.example.com"]
        )
        assert len(resp["Aliases"]) == 1
        assert resp["Aliases"][0]["Lifecycle"] == "DELETING"

        desc = client.describe_file_system_aliases(FileSystemId=fs_id)
        assert len(desc["Aliases"]) == 1
        assert desc["Aliases"][0]["Name"] == "b.example.com"

    def test_no_duplicate_aliases(self, client):
        fs_id = _create_windows_fs(client)
        client.associate_file_system_aliases(
            FileSystemId=fs_id, Aliases=["dup.example.com"]
        )
        client.associate_file_system_aliases(
            FileSystemId=fs_id, Aliases=["dup.example.com"]
        )
        desc = client.describe_file_system_aliases(FileSystemId=fs_id)
        assert len(desc["Aliases"]) == 1

    def test_alias_nonexistent_fs(self, client):
        with pytest.raises(ClientError) as exc:
            client.associate_file_system_aliases(
                FileSystemId="fs-nonexist", Aliases=["x.example.com"]
            )
        assert exc.value.response["Error"]["Code"] == "FileSystemNotFound"


# --- Data Repository Association ---


class TestDataRepositoryAssociation:
    def test_create_dra(self, client):
        fs_id = _create_lustre_fs(client)
        resp = client.create_data_repository_association(
            FileSystemId=fs_id,
            FileSystemPath="/ns1",
            DataRepositoryPath="s3://my-bucket/prefix",
        )
        assoc = resp["Association"]
        assert assoc["FileSystemId"] == fs_id
        assert assoc["DataRepositoryPath"] == "s3://my-bucket/prefix"
        assert assoc["Lifecycle"] == "AVAILABLE"
        assert assoc["AssociationId"].startswith("dra-")

    def test_describe_dras(self, client):
        fs_id = _create_lustre_fs(client)
        client.create_data_repository_association(
            FileSystemId=fs_id,
            FileSystemPath="/ns1",
            DataRepositoryPath="s3://bucket1",
        )
        client.create_data_repository_association(
            FileSystemId=fs_id,
            FileSystemPath="/ns2",
            DataRepositoryPath="s3://bucket2",
        )
        resp = client.describe_data_repository_associations()
        assert len(resp["Associations"]) == 2

    def test_update_dra(self, client):
        fs_id = _create_lustre_fs(client)
        create = client.create_data_repository_association(
            FileSystemId=fs_id,
            FileSystemPath="/ns1",
            DataRepositoryPath="s3://bucket",
            ImportedFileChunkSize=1024,
        )
        assoc_id = create["Association"]["AssociationId"]

        resp = client.update_data_repository_association(
            AssociationId=assoc_id,
            ImportedFileChunkSize=2048,
        )
        assert resp["Association"]["ImportedFileChunkSize"] == 2048

    def test_delete_dra(self, client):
        fs_id = _create_lustre_fs(client)
        create = client.create_data_repository_association(
            FileSystemId=fs_id,
            FileSystemPath="/ns1",
            DataRepositoryPath="s3://bucket",
        )
        assoc_id = create["Association"]["AssociationId"]

        resp = client.delete_data_repository_association(
            AssociationId=assoc_id,
            DeleteDataInFileSystem=False,
        )
        assert resp["Lifecycle"] == "DELETING"

        desc = client.describe_data_repository_associations()
        assert len(desc["Associations"]) == 0

    def test_create_dra_nonexistent_fs(self, client):
        with pytest.raises(ClientError) as exc:
            client.create_data_repository_association(
                FileSystemId="fs-nonexist",
                FileSystemPath="/bad",
                DataRepositoryPath="s3://bucket",
            )
        assert exc.value.response["Error"]["Code"] == "FileSystemNotFound"
