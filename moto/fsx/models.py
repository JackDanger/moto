"""FSxBackend class with methods for supported APIs."""

import time
from typing import Any, Optional
from uuid import uuid4

from moto.core.base_backend import BackendDict, BaseBackend
from moto.core.common_models import BaseModel
from moto.utilities.paginator import paginate
from moto.utilities.tagging_service import TaggingService
from moto.utilities.utils import filter_resources

from .exceptions import (
    BackupNotFoundException,
    FileSystemNotFoundException,
    ResourceNotFoundException,
    SnapshotNotFoundException,
    StorageVirtualMachineNotFoundException,
    VolumeNotFoundException,
)
from .utils import FileSystemType

PAGINATION_MODEL = {
    "describe_file_systems": {
        "input_token": "next_token",
        "limit_key": "max_results",
        "limit_default": 2147483647,
        "unique_attribute": "resource_arn",
    },
    "describe_backups": {
        "input_token": "next_token",
        "limit_key": "max_results",
        "limit_default": 2147483647,
        "unique_attribute": "resource_arn",
    },
}


class FileSystem(BaseModel):
    def __init__(
        self,
        account_id: str,
        region_name: str,
        file_system_type: str,
        storage_capacity: int,
        storage_type: str,
        subnet_ids: list[str],
        security_group_ids: list[str],
        tags: Optional[list[dict[str, str]]],
        kms_key_id: Optional[str],
        windows_configuration: Optional[dict[str, Any]],
        lustre_configuration: Optional[dict[str, Any]],
        ontap_configuration: Optional[dict[str, Any]],
        open_zfs_configuration: Optional[dict[str, Any]],
        backend: "FSxBackend",
    ) -> None:
        self.file_system_id = f"fs-{uuid4().hex[:8]}"
        self.file_system_type = file_system_type
        if self.file_system_type not in FileSystemType.list_values():
            raise ValueError(f"Invalid FileSystemType: {self.file_system_type}")
        self.storage_capacity = storage_capacity
        self.storage_type = storage_type
        self.subnet_ids = subnet_ids
        self.security_group_ids = security_group_ids
        self.dns_name = f"{self.file_system_id}.fsx.{region_name}.amazonaws.com"
        self.kms_key_id = kms_key_id
        self.resource_arn = (
            f"arn:aws:fsx:{region_name}:{account_id}:file-system/{self.file_system_id}"
        )
        self.windows_configuration = windows_configuration
        self.lustre_configuration = lustre_configuration
        self.ontap_configuration = ontap_configuration
        self.open_zfs_configuration = open_zfs_configuration
        self.aliases: list[dict[str, str]] = []
        self.backend = backend
        if tags:
            self.backend.tag_resource(self.resource_arn, tags)

    def to_dict(self) -> dict[str, Any]:
        dct = {
            "FileSystemId": self.file_system_id,
            "FileSystemType": self.file_system_type,
            "StorageCapacity": self.storage_capacity,
            "StorageType": self.storage_type,
            "SubnetIds": self.subnet_ids,
            "SecurityGroupIds": self.security_group_ids,
            "Tags": self.backend.list_tags_for_resource(self.resource_arn),
            "DNSName": self.dns_name,
            "KmsKeyId": self.kms_key_id,
            "ResourceARN": self.resource_arn,
            "WindowsConfiguration": self.windows_configuration,
            "LustreConfiguration": self.lustre_configuration,
            "OntapConfiguration": self.ontap_configuration,
            "OpenZFSConfiguration": self.open_zfs_configuration,
        }
        return {k: v for k, v in dct.items() if v}


class Backup(BaseModel):
    def __init__(
        self,
        account_id: str,
        region_name: str,
        file_system_id: str,
        client_request_token: Optional[str],
        volume_id: Optional[str],
        tags: Optional[list[dict[str, str]]],
        backend: "FSxBackend",
    ) -> None:
        self.backup_id = f"backup-{uuid4().hex[:8]}"
        self.file_system_id = file_system_id
        self.client_request_token = client_request_token or str(uuid4())
        self.volume_id = volume_id
        self.resource_arn = (
            f"arn:aws:fsx:{region_name}:{account_id}:backup/{self.backup_id}"
        )
        self.lifecycle = "CREATING"
        self.creation_time = time.time()
        self.backend = backend
        if tags:
            self.backend.tag_resource(self.resource_arn, tags)

    def to_dict(self) -> dict[str, Any]:
        dct = {
            "BackupId": self.backup_id,
            "FileSystemId": self.file_system_id,
            "VolumeId": self.volume_id,
            "Lifecycle": self.lifecycle,
            "CreationTime": self.creation_time,
            "Tags": self.backend.list_tags_for_resource(self.resource_arn),
            "ResourceARN": self.resource_arn,
            "ClientRequestToken": self.client_request_token,
        }
        return {k: v for k, v in dct.items() if v is not None}


class StorageVirtualMachine(BaseModel):
    def __init__(
        self,
        account_id: str,
        region_name: str,
        file_system_id: str,
        name: str,
        active_directory_configuration: Optional[dict[str, Any]],
        root_volume_security_style: Optional[str],
        tags: Optional[list[dict[str, str]]],
        backend: "FSxBackend",
    ) -> None:
        self.storage_virtual_machine_id = f"svm-{uuid4().hex[:17]}"
        self.file_system_id = file_system_id
        self.name = name
        self.active_directory_configuration = active_directory_configuration
        self.root_volume_security_style = root_volume_security_style or "UNIX"
        self.lifecycle = "CREATED"
        self.creation_time = time.time()
        self.resource_arn = (
            f"arn:aws:fsx:{region_name}:{account_id}"
            f":storage-virtual-machine/{file_system_id}/{self.storage_virtual_machine_id}"
        )
        self.backend = backend
        if tags:
            self.backend.tag_resource(self.resource_arn, tags)

    def to_dict(self) -> dict[str, Any]:
        dct: dict[str, Any] = {
            "StorageVirtualMachineId": self.storage_virtual_machine_id,
            "FileSystemId": self.file_system_id,
            "Name": self.name,
            "Lifecycle": self.lifecycle,
            "CreationTime": self.creation_time,
            "ResourceARN": self.resource_arn,
            "RootVolumeSecurityStyle": self.root_volume_security_style,
            "Tags": self.backend.list_tags_for_resource(self.resource_arn),
            "ActiveDirectoryConfiguration": self.active_directory_configuration,
        }
        return {k: v for k, v in dct.items() if v is not None}


class Volume(BaseModel):
    def __init__(
        self,
        account_id: str,
        region_name: str,
        volume_type: str,
        name: str,
        file_system_id: Optional[str],
        ontap_configuration: Optional[dict[str, Any]],
        open_zfs_configuration: Optional[dict[str, Any]],
        tags: Optional[list[dict[str, str]]],
        backend: "FSxBackend",
    ) -> None:
        self.volume_id = f"fsvol-{uuid4().hex[:17]}"
        self.volume_type = volume_type
        self.name = name
        self.file_system_id = file_system_id
        self.ontap_configuration = ontap_configuration
        self.open_zfs_configuration = open_zfs_configuration
        self.lifecycle = "CREATED"
        self.creation_time = time.time()
        self.resource_arn = (
            f"arn:aws:fsx:{region_name}:{account_id}:volume/{self.volume_id}"
        )
        self.backend = backend
        if tags:
            self.backend.tag_resource(self.resource_arn, tags)

    def to_dict(self) -> dict[str, Any]:
        dct: dict[str, Any] = {
            "VolumeId": self.volume_id,
            "VolumeType": self.volume_type,
            "Name": self.name,
            "FileSystemId": self.file_system_id,
            "Lifecycle": self.lifecycle,
            "CreationTime": self.creation_time,
            "ResourceARN": self.resource_arn,
            "Tags": self.backend.list_tags_for_resource(self.resource_arn),
            "OntapConfiguration": self.ontap_configuration,
            "OpenZFSConfiguration": self.open_zfs_configuration,
        }
        return {k: v for k, v in dct.items() if v is not None}


class Snapshot(BaseModel):
    def __init__(
        self,
        account_id: str,
        region_name: str,
        name: str,
        volume_id: str,
        tags: Optional[list[dict[str, str]]],
        backend: "FSxBackend",
    ) -> None:
        self.snapshot_id = f"fsvolsnap-{uuid4().hex[:17]}"
        self.name = name
        self.volume_id = volume_id
        self.lifecycle = "AVAILABLE"
        self.creation_time = time.time()
        self.resource_arn = (
            f"arn:aws:fsx:{region_name}:{account_id}:snapshot/{self.snapshot_id}"
        )
        self.backend = backend
        if tags:
            self.backend.tag_resource(self.resource_arn, tags)

    def to_dict(self) -> dict[str, Any]:
        dct: dict[str, Any] = {
            "SnapshotId": self.snapshot_id,
            "Name": self.name,
            "VolumeId": self.volume_id,
            "Lifecycle": self.lifecycle,
            "CreationTime": self.creation_time,
            "ResourceARN": self.resource_arn,
            "Tags": self.backend.list_tags_for_resource(self.resource_arn),
        }
        return {k: v for k, v in dct.items() if v is not None}


class DataRepositoryAssociation(BaseModel):
    def __init__(
        self,
        account_id: str,
        region_name: str,
        file_system_id: str,
        file_system_path: Optional[str],
        data_repository_path: str,
        batch_import_meta_data_on_create: Optional[bool],
        imported_file_chunk_size: Optional[int],
        s3: Optional[dict[str, Any]],
        tags: Optional[list[dict[str, str]]],
        backend: "FSxBackend",
    ) -> None:
        self.association_id = f"dra-{uuid4().hex[:9]}"
        self.file_system_id = file_system_id
        self.file_system_path = file_system_path
        self.data_repository_path = data_repository_path
        self.batch_import_meta_data_on_create = batch_import_meta_data_on_create
        self.imported_file_chunk_size = imported_file_chunk_size
        self.s3 = s3
        self.lifecycle = "AVAILABLE"
        self.creation_time = time.time()
        self.resource_arn = (
            f"arn:aws:fsx:{region_name}:{account_id}"
            f":association/{file_system_id}/{self.association_id}"
        )
        self.backend = backend
        if tags:
            self.backend.tag_resource(self.resource_arn, tags)

    def to_dict(self) -> dict[str, Any]:
        dct: dict[str, Any] = {
            "AssociationId": self.association_id,
            "FileSystemId": self.file_system_id,
            "FileSystemPath": self.file_system_path,
            "DataRepositoryPath": self.data_repository_path,
            "BatchImportMetaDataOnCreate": self.batch_import_meta_data_on_create,
            "ImportedFileChunkSize": self.imported_file_chunk_size,
            "S3": self.s3,
            "Lifecycle": self.lifecycle,
            "CreationTime": self.creation_time,
            "ResourceARN": self.resource_arn,
            "Tags": self.backend.list_tags_for_resource(self.resource_arn),
        }
        return {k: v for k, v in dct.items() if v is not None}


class FSxBackend(BaseBackend):
    """Implementation of FSx APIs."""

    def __init__(self, region_name: str, account_id: str) -> None:
        super().__init__(region_name, account_id)
        self.file_systems: dict[str, FileSystem] = {}
        self.backups: dict[str, Backup] = {}
        self.storage_virtual_machines: dict[str, StorageVirtualMachine] = {}
        self.volumes: dict[str, Volume] = {}
        self.snapshots: dict[str, Snapshot] = {}
        self.data_repository_associations: dict[str, DataRepositoryAssociation] = {}
        self.tagger = TaggingService()

    def create_file_system(
        self,
        client_request_token: str,
        file_system_type: str,
        storage_capacity: int,
        storage_type: str,
        subnet_ids: list[str],
        security_group_ids: list[str],
        tags: Optional[list[dict[str, str]]],
        kms_key_id: Optional[str],
        windows_configuration: Optional[dict[str, Any]],
        lustre_configuration: Optional[dict[str, Any]],
        ontap_configuration: Optional[dict[str, Any]],
        file_system_type_version: Optional[str],
        open_zfs_configuration: Optional[dict[str, Any]],
    ) -> FileSystem:
        file_system = FileSystem(
            account_id=self.account_id,
            region_name=self.region_name,
            file_system_type=file_system_type,
            storage_capacity=storage_capacity,
            storage_type=storage_type,
            subnet_ids=subnet_ids,
            security_group_ids=security_group_ids,
            tags=tags,
            kms_key_id=kms_key_id,
            windows_configuration=windows_configuration,
            ontap_configuration=ontap_configuration,
            open_zfs_configuration=open_zfs_configuration,
            lustre_configuration=lustre_configuration,
            backend=self,
        )

        file_system_id = file_system.file_system_id

        self.file_systems[file_system_id] = file_system
        if tags:
            self.tag_resource(resource_arn=file_system.resource_arn, tags=tags)
        return file_system

    @paginate(pagination_model=PAGINATION_MODEL)
    def describe_file_systems(self, file_system_ids: list[str]) -> list[FileSystem]:
        file_systems = []
        if not file_system_ids:
            file_systems = list(self.file_systems.values())
        else:
            for id in file_system_ids:
                if id in self.file_systems:
                    file_systems.append(self.file_systems[id])
        return file_systems

    def delete_file_system(
        self,
        file_system_id: str,
        client_request_token: str,
        windows_configuration: Optional[dict[str, Any]],
        lustre_configuration: Optional[dict[str, Any]],
        open_zfs_configuration: Optional[dict[str, Any]],
    ) -> tuple[
        str,
        str,
        Optional[dict[str, Any]],
        Optional[dict[str, Any]],
        Optional[dict[str, Any]],
    ]:
        response_template = {"FinalBackUpId": "", "FinalBackUpTags": []}

        file_system_type = self.file_systems[file_system_id].file_system_type

        lifecycle = "DELETING"
        self.file_systems.pop(file_system_id)

        windows_response = None
        lustre_response = None
        open_zfs_response = None

        if file_system_type == "WINDOWS":
            windows_response = response_template
        elif file_system_type == "LUSTRE":
            lustre_response = response_template
        elif file_system_type == "OPEN_ZFS":
            open_zfs_response = response_template

        return (
            file_system_id,
            lifecycle,
            windows_response,
            lustre_response,
            open_zfs_response,
        )

    def create_backup(
        self,
        file_system_id: str,
        client_request_token: Optional[str],
        volume_id: Optional[str],
        tags: Optional[list[dict[str, str]]],
    ) -> Backup:
        backup = Backup(
            account_id=self.account_id,
            region_name=self.region_name,
            file_system_id=file_system_id,
            client_request_token=client_request_token,
            volume_id=volume_id,
            tags=tags,
            backend=self,
        )
        if file_system_id not in self.file_systems:
            raise ResourceNotFoundException(
                msg=f"FSx resource, {file_system_id} does not exist"
            )
        self.backups[backup.backup_id] = backup
        if tags:
            self.tag_resource(resource_arn=backup.resource_arn, tags=tags)
        return backup

    def delete_backup(
        self, backup_id: str, client_request_token: Optional[str]
    ) -> dict[str, Any]:
        if backup_id not in self.backups:
            raise ResourceNotFoundException(
                msg=f"FSx resource, {backup_id} does not exist"
            )
        self.backups.pop(backup_id)

        return {"BackupId": backup_id, "Lifecycle": "DELETED"}

    @paginate(pagination_model=PAGINATION_MODEL)
    def describe_backups(
        self,
        backup_ids: list[str],
        filters: Optional[list[dict[str, Any]]] = None,
    ) -> list[Backup]:
        backups = []
        if not backup_ids:
            backups = list(self.backups.values())
        else:
            for id in backup_ids:
                if id in self.backups:
                    backups.append(self.backups[id])

        attr_pairs = (
            ("file-system-id", "file_system_id"),
            ("backup-type", "backup_type"),
            ("file-system-type", "file_system_type"),
            ("volume-id", "volume_id"),
            ("data-repository-type", "data_repository_type"),
            ("file-cache-id", "file_cache_id"),
            ("file-cache-type", "file_cache_type"),
        )

        if filters:
            filter_dict = {f["Name"]: f["Values"] for f in filters}
            backups = filter_resources(backups, filter_dict, attr_pairs)
        return backups

    def update_file_system(
        self,
        file_system_id: str,
        client_request_token: Optional[str],
        storage_capacity: Optional[int],
        windows_configuration: Optional[dict[str, Any]],
        lustre_configuration: Optional[dict[str, Any]],
        ontap_configuration: Optional[dict[str, Any]],
        open_zfs_configuration: Optional[dict[str, Any]],
        storage_type: Optional[str],
    ) -> FileSystem:
        if file_system_id not in self.file_systems:
            raise FileSystemNotFoundException(file_system_id)
        fs = self.file_systems[file_system_id]
        if storage_capacity is not None:
            fs.storage_capacity = storage_capacity
        if storage_type is not None:
            fs.storage_type = storage_type
        if windows_configuration is not None:
            fs.windows_configuration = {
                **(fs.windows_configuration or {}),
                **windows_configuration,
            }
        if lustre_configuration is not None:
            fs.lustre_configuration = {
                **(fs.lustre_configuration or {}),
                **lustre_configuration,
            }
        if ontap_configuration is not None:
            fs.ontap_configuration = {
                **(fs.ontap_configuration or {}),
                **ontap_configuration,
            }
        if open_zfs_configuration is not None:
            fs.open_zfs_configuration = {
                **(fs.open_zfs_configuration or {}),
                **open_zfs_configuration,
            }
        return fs

    def create_file_system_from_backup(
        self,
        backup_id: str,
        client_request_token: Optional[str],
        subnet_ids: list[str],
        security_group_ids: Optional[list[str]],
        tags: Optional[list[dict[str, str]]],
        windows_configuration: Optional[dict[str, Any]],
        lustre_configuration: Optional[dict[str, Any]],
        storage_type: Optional[str],
        kms_key_id: Optional[str],
        file_system_type_version: Optional[str],
        open_zfs_configuration: Optional[dict[str, Any]],
        storage_capacity: Optional[int],
    ) -> FileSystem:
        if backup_id not in self.backups:
            raise BackupNotFoundException(backup_id)
        backup = self.backups[backup_id]
        # Get the original filesystem for defaults
        orig_fs = self.file_systems.get(backup.file_system_id)
        fs_type = orig_fs.file_system_type if orig_fs else "LUSTRE"
        cap = storage_capacity or (orig_fs.storage_capacity if orig_fs else 1200)
        s_type = storage_type or (orig_fs.storage_type if orig_fs else "SSD")

        return self.create_file_system(
            client_request_token=client_request_token or str(uuid4()),
            file_system_type=fs_type,
            storage_capacity=cap,
            storage_type=s_type,
            subnet_ids=subnet_ids,
            security_group_ids=security_group_ids or [],
            tags=tags,
            kms_key_id=kms_key_id,
            windows_configuration=windows_configuration,
            lustre_configuration=lustre_configuration,
            ontap_configuration=None,
            file_system_type_version=file_system_type_version,
            open_zfs_configuration=open_zfs_configuration,
        )

    # --- Storage Virtual Machine ---

    def create_storage_virtual_machine(
        self,
        file_system_id: str,
        name: str,
        active_directory_configuration: Optional[dict[str, Any]],
        root_volume_security_style: Optional[str],
        tags: Optional[list[dict[str, str]]],
    ) -> StorageVirtualMachine:
        if file_system_id not in self.file_systems:
            raise FileSystemNotFoundException(file_system_id)
        svm = StorageVirtualMachine(
            account_id=self.account_id,
            region_name=self.region_name,
            file_system_id=file_system_id,
            name=name,
            active_directory_configuration=active_directory_configuration,
            root_volume_security_style=root_volume_security_style,
            tags=tags,
            backend=self,
        )
        self.storage_virtual_machines[svm.storage_virtual_machine_id] = svm
        return svm

    def describe_storage_virtual_machines(
        self,
        storage_virtual_machine_ids: Optional[list[str]] = None,
        filters: Optional[list[dict[str, Any]]] = None,
    ) -> list[StorageVirtualMachine]:
        if not storage_virtual_machine_ids:
            svms = list(self.storage_virtual_machines.values())
        else:
            svms = []
            for svm_id in storage_virtual_machine_ids:
                if svm_id in self.storage_virtual_machines:
                    svms.append(self.storage_virtual_machines[svm_id])
                else:
                    raise StorageVirtualMachineNotFoundException(svm_id)
        if filters:
            attr_pairs = (("file-system-id", "file_system_id"),)
            filter_dict = {f["Name"]: f["Values"] for f in filters}
            svms = filter_resources(svms, filter_dict, attr_pairs)
        return svms

    def delete_storage_virtual_machine(
        self,
        storage_virtual_machine_id: str,
    ) -> dict[str, Any]:
        if storage_virtual_machine_id not in self.storage_virtual_machines:
            raise StorageVirtualMachineNotFoundException(storage_virtual_machine_id)
        self.storage_virtual_machines.pop(storage_virtual_machine_id)
        return {
            "StorageVirtualMachineId": storage_virtual_machine_id,
            "Lifecycle": "DELETING",
        }

    # --- Volume ---

    def create_volume(
        self,
        volume_type: str,
        name: str,
        ontap_configuration: Optional[dict[str, Any]],
        open_zfs_configuration: Optional[dict[str, Any]],
        tags: Optional[list[dict[str, str]]],
    ) -> Volume:
        # Derive file_system_id from config
        file_system_id = None
        if ontap_configuration:
            svm_id = ontap_configuration.get("StorageVirtualMachineId")
            if svm_id and svm_id in self.storage_virtual_machines:
                file_system_id = self.storage_virtual_machines[svm_id].file_system_id
        if open_zfs_configuration:
            file_system_id = open_zfs_configuration.get("ParentVolumeId")

        vol = Volume(
            account_id=self.account_id,
            region_name=self.region_name,
            volume_type=volume_type,
            name=name,
            file_system_id=file_system_id,
            ontap_configuration=ontap_configuration,
            open_zfs_configuration=open_zfs_configuration,
            tags=tags,
            backend=self,
        )
        self.volumes[vol.volume_id] = vol
        return vol

    def create_volume_from_backup(
        self,
        backup_id: str,
        name: str,
        ontap_configuration: Optional[dict[str, Any]],
        tags: Optional[list[dict[str, str]]],
    ) -> Volume:
        if backup_id not in self.backups:
            raise BackupNotFoundException(backup_id)
        return self.create_volume(
            volume_type="ONTAP",
            name=name,
            ontap_configuration=ontap_configuration,
            open_zfs_configuration=None,
            tags=tags,
        )

    def describe_volumes(
        self,
        volume_ids: Optional[list[str]] = None,
        filters: Optional[list[dict[str, Any]]] = None,
    ) -> list[Volume]:
        if not volume_ids:
            vols = list(self.volumes.values())
        else:
            vols = []
            for vid in volume_ids:
                if vid in self.volumes:
                    vols.append(self.volumes[vid])
                else:
                    raise VolumeNotFoundException(vid)
        if filters:
            attr_pairs = (
                ("file-system-id", "file_system_id"),
                ("volume-type", "volume_type"),
            )
            filter_dict = {f["Name"]: f["Values"] for f in filters}
            vols = filter_resources(vols, filter_dict, attr_pairs)
        return vols

    def delete_volume(
        self,
        volume_id: str,
    ) -> dict[str, Any]:
        if volume_id not in self.volumes:
            raise VolumeNotFoundException(volume_id)
        vol = self.volumes.pop(volume_id)
        return {
            "VolumeId": volume_id,
            "Lifecycle": "DELETING",
            "OntapResponse": (
                {"FinalBackupId": None}
                if vol.volume_type == "ONTAP"
                else None
            ),
        }

    # --- Snapshot ---

    def create_snapshot(
        self,
        name: str,
        volume_id: str,
        tags: Optional[list[dict[str, str]]],
    ) -> Snapshot:
        if volume_id not in self.volumes:
            raise VolumeNotFoundException(volume_id)
        snap = Snapshot(
            account_id=self.account_id,
            region_name=self.region_name,
            name=name,
            volume_id=volume_id,
            tags=tags,
            backend=self,
        )
        self.snapshots[snap.snapshot_id] = snap
        return snap

    def describe_snapshots(
        self,
        snapshot_ids: Optional[list[str]] = None,
        filters: Optional[list[dict[str, Any]]] = None,
    ) -> list[Snapshot]:
        if not snapshot_ids:
            snaps = list(self.snapshots.values())
        else:
            snaps = []
            for sid in snapshot_ids:
                if sid in self.snapshots:
                    snaps.append(self.snapshots[sid])
                else:
                    raise SnapshotNotFoundException(sid)
        if filters:
            attr_pairs = (
                ("volume-id", "volume_id"),
            )
            filter_dict = {f["Name"]: f["Values"] for f in filters}
            snaps = filter_resources(snaps, filter_dict, attr_pairs)
        return snaps

    def delete_snapshot(
        self,
        snapshot_id: str,
    ) -> dict[str, Any]:
        if snapshot_id not in self.snapshots:
            raise SnapshotNotFoundException(snapshot_id)
        self.snapshots.pop(snapshot_id)
        return {"SnapshotId": snapshot_id, "Lifecycle": "DELETING"}

    def update_snapshot(
        self,
        snapshot_id: str,
        name: str,
    ) -> Snapshot:
        if snapshot_id not in self.snapshots:
            raise SnapshotNotFoundException(snapshot_id)
        snap = self.snapshots[snapshot_id]
        snap.name = name
        return snap

    # --- File System Aliases ---

    def associate_file_system_aliases(
        self,
        file_system_id: str,
        aliases: list[str],
    ) -> list[dict[str, str]]:
        if file_system_id not in self.file_systems:
            raise FileSystemNotFoundException(file_system_id)
        fs = self.file_systems[file_system_id]
        result = []
        for alias in aliases:
            entry = {"Name": alias, "Lifecycle": "AVAILABLE"}
            # Don't add duplicates
            existing_names = [a["Name"] for a in fs.aliases]
            if alias not in existing_names:
                fs.aliases.append(entry)
            result.append(entry)
        return result

    def disassociate_file_system_aliases(
        self,
        file_system_id: str,
        aliases: list[str],
    ) -> list[dict[str, str]]:
        if file_system_id not in self.file_systems:
            raise FileSystemNotFoundException(file_system_id)
        fs = self.file_systems[file_system_id]
        result = []
        for alias in aliases:
            fs.aliases = [a for a in fs.aliases if a["Name"] != alias]
            result.append({"Name": alias, "Lifecycle": "DELETING"})
        return result

    def describe_file_system_aliases(
        self,
        file_system_id: str,
    ) -> list[dict[str, Any]]:
        if file_system_id not in self.file_systems:
            raise FileSystemNotFoundException(file_system_id)
        return self.file_systems[file_system_id].aliases

    # --- Data Repository Association ---

    def create_data_repository_association(
        self,
        file_system_id: str,
        file_system_path: Optional[str],
        data_repository_path: str,
        batch_import_meta_data_on_create: Optional[bool],
        imported_file_chunk_size: Optional[int],
        s3: Optional[dict[str, Any]],
        tags: Optional[list[dict[str, str]]],
    ) -> DataRepositoryAssociation:
        if file_system_id not in self.file_systems:
            raise FileSystemNotFoundException(file_system_id)
        assoc = DataRepositoryAssociation(
            account_id=self.account_id,
            region_name=self.region_name,
            file_system_id=file_system_id,
            file_system_path=file_system_path,
            data_repository_path=data_repository_path,
            batch_import_meta_data_on_create=batch_import_meta_data_on_create,
            imported_file_chunk_size=imported_file_chunk_size,
            s3=s3,
            tags=tags,
            backend=self,
        )
        self.data_repository_associations[assoc.association_id] = assoc
        return assoc

    def describe_data_repository_associations(
        self,
        association_ids: Optional[list[str]] = None,
        filters: Optional[list[dict[str, Any]]] = None,
    ) -> list[DataRepositoryAssociation]:
        if not association_ids:
            assocs = list(self.data_repository_associations.values())
        else:
            assocs = []
            for aid in association_ids:
                if aid in self.data_repository_associations:
                    assocs.append(self.data_repository_associations[aid])
        if filters:
            attr_pairs = (
                ("file-system-id", "file_system_id"),
                ("data-repository-type", "data_repository_type"),
            )
            filter_dict = {f["Name"]: f["Values"] for f in filters}
            assocs = filter_resources(assocs, filter_dict, attr_pairs)
        return assocs

    def update_data_repository_association(
        self,
        association_id: str,
        imported_file_chunk_size: Optional[int],
        s3: Optional[dict[str, Any]],
    ) -> DataRepositoryAssociation:
        if association_id not in self.data_repository_associations:
            raise ResourceNotFoundException(
                msg=f"FSx resource, {association_id} does not exist"
            )
        assoc = self.data_repository_associations[association_id]
        if imported_file_chunk_size is not None:
            assoc.imported_file_chunk_size = imported_file_chunk_size
        if s3 is not None:
            assoc.s3 = s3
        return assoc

    def delete_data_repository_association(
        self,
        association_id: str,
        delete_data_in_file_system: Optional[bool],
    ) -> dict[str, Any]:
        if association_id not in self.data_repository_associations:
            raise ResourceNotFoundException(
                msg=f"FSx resource, {association_id} does not exist"
            )
        self.data_repository_associations.pop(association_id)
        return {
            "AssociationId": association_id,
            "Lifecycle": "DELETING",
            "DeleteDataInFileSystem": delete_data_in_file_system or False,
        }

    def describe_data_repository_tasks(
        self,
        task_ids: Optional[list[str]] = None,
        filters: Optional[list[dict[str, Any]]] = None,
    ) -> list[dict[str, Any]]:
        """Describe data repository tasks — returns empty list."""
        return []

    def describe_file_caches(
        self,
        file_cache_ids: Optional[list[str]] = None,
    ) -> list[dict[str, Any]]:
        """Describe file caches — returns empty list."""
        return []

    def describe_shared_vpc_configuration(self) -> dict[str, str]:
        """Describe shared VPC configuration."""
        return {"EnableFsxRouteTableUpdatesFromParticipantAccounts": "false"}

    def describe_s3_access_point_attachments(
        self,
        file_system_id: Optional[str] = None,
        filters: Optional[list[dict[str, Any]]] = None,
    ) -> list[dict[str, Any]]:
        """Describe S3 access point attachments — returns empty list."""
        return []

    def tag_resource(self, resource_arn: str, tags: list[dict[str, str]]) -> None:
        self.tagger.tag_resource(resource_arn, tags)

    def untag_resource(self, resource_arn: str, tag_keys: list[str]) -> None:
        self.tagger.untag_resource_using_names(resource_arn, tag_keys)

    def list_tags_for_resource(self, resource_arn: str) -> list[dict[str, str]]:
        """
        Pagination is not yet implemented
        """
        if self.tagger.has_tags(resource_arn):
            return self.tagger.list_tags_for_resource(resource_arn)["Tags"]
        return []


fsx_backends = BackendDict(FSxBackend, "fsx")
