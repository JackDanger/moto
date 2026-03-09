"""Handles incoming fsx requests, invokes methods, returns responses."""

import json

from moto.core.common_types import TYPE_RESPONSE
from moto.core.responses import BaseResponse

from .models import FSxBackend, fsx_backends


class FSxResponse(BaseResponse):
    """Handler for FSx requests and responses."""

    def __init__(self) -> None:
        super().__init__(service_name="fsx")

    @property
    def fsx_backend(self) -> FSxBackend:
        """Return backend instance specific for this region."""
        return fsx_backends[self.current_account][self.region]

    def create_file_system(self) -> str:
        params = json.loads(self.body)
        client_request_token = params.get("ClientRequestToken")
        file_system_type = params.get("FileSystemType")
        storage_capacity = params.get("StorageCapacity")
        storage_type = params.get("StorageType")
        subnet_ids = params.get("SubnetIds")
        security_group_ids = params.get("SecurityGroupIds")
        tags = params.get("Tags")
        kms_key_id = params.get("KmsKeyId")
        windows_configuration = params.get("WindowsConfiguration")
        lustre_configuration = params.get("LustreConfiguration")
        ontap_configuration = params.get("OntapConfiguration")
        file_system_type_version = params.get("FileSystemTypeVersion")
        open_zfs_configuration = params.get("OpenZFSConfiguration")
        file_system = self.fsx_backend.create_file_system(
            client_request_token=client_request_token,
            file_system_type=file_system_type,
            storage_capacity=storage_capacity,
            storage_type=storage_type,
            subnet_ids=subnet_ids,
            security_group_ids=security_group_ids,
            tags=tags,
            kms_key_id=kms_key_id,
            windows_configuration=windows_configuration,
            lustre_configuration=lustre_configuration,
            ontap_configuration=ontap_configuration,
            file_system_type_version=file_system_type_version,
            open_zfs_configuration=open_zfs_configuration,
        )

        return json.dumps({"FileSystem": file_system.to_dict()})

    def describe_file_systems(self) -> str:
        params = json.loads(self.body)
        file_system_ids = params.get("FileSystemIds")
        max_results = params.get("MaxResults")
        next_token = params.get("NextToken")
        file_systems, next_token = self.fsx_backend.describe_file_systems(
            file_system_ids=file_system_ids,
            max_results=max_results,
            next_token=next_token,
        )
        list_file_systems = [file_system.to_dict() for file_system in file_systems]
        return json.dumps({"FileSystems": list_file_systems, "NextToken": next_token})

    def delete_file_system(self) -> str:
        params = json.loads(self.body)
        file_system_id = params.get("FileSystemId")
        client_request_token = params.get("ClientRequestToken")
        windows_configuration = params.get("WindowsConfiguration")
        lustre_configuration = params.get("LustreConfiguration")
        open_zfs_configuration = params.get("OpenZFSConfiguration")
        (
            file_system_id,
            lifecycle,
            windows_response,
            lustre_response,
            open_zfs_response,
        ) = self.fsx_backend.delete_file_system(
            file_system_id=file_system_id,
            client_request_token=client_request_token,
            windows_configuration=windows_configuration,
            lustre_configuration=lustre_configuration,
            open_zfs_configuration=open_zfs_configuration,
        )

        return json.dumps(
            {
                "FileSystemId": file_system_id,
                "Lifecycle": lifecycle,
                "WindowsResponse": windows_response,
                "LustreResponse": lustre_response,
                "OpenZfsResponse": open_zfs_response,
            }
        )

    def create_backup(self) -> str:
        params = json.loads(self.body)
        file_system_id = params.get("FileSystemId")
        client_request_token = params.get("ClientRequestToken")
        tags = params.get("Tags")
        volume_id = params.get("VolumeId")

        backup = self.fsx_backend.create_backup(
            file_system_id=file_system_id,
            client_request_token=client_request_token,
            tags=tags,
            volume_id=volume_id,
        )
        return json.dumps({"Backup": backup.to_dict()})

    def delete_backup(self) -> str:
        params = json.loads(self.body)
        backup_id = params.get("BackupId")
        client_request_token = params.get("ClientRequestToken")
        resp = self.fsx_backend.delete_backup(
            backup_id=backup_id, client_request_token=client_request_token
        )
        return json.dumps(resp)

    def describe_backups(self) -> str:
        params = json.loads(self.body)
        backup_ids = params.get("BackupIds")
        filters = params.get("Filters")
        max_results = params.get("MaxResults")
        next_token = params.get("NextToken")
        backups, next_token = self.fsx_backend.describe_backups(
            backup_ids=backup_ids,
            filters=filters,
            max_results=max_results,
            next_token=next_token,
        )
        list_backups = [backup.to_dict() for backup in backups]
        return json.dumps({"Backups": list_backups, "NextToken": next_token})

    def update_file_system(self) -> str:
        params = json.loads(self.body)
        fs = self.fsx_backend.update_file_system(
            file_system_id=params.get("FileSystemId"),
            client_request_token=params.get("ClientRequestToken"),
            storage_capacity=params.get("StorageCapacity"),
            windows_configuration=params.get("WindowsConfiguration"),
            lustre_configuration=params.get("LustreConfiguration"),
            ontap_configuration=params.get("OntapConfiguration"),
            open_zfs_configuration=params.get("OpenZFSConfiguration"),
            storage_type=params.get("StorageType"),
        )
        return json.dumps({"FileSystem": fs.to_dict()})

    def create_file_system_from_backup(self) -> str:
        params = json.loads(self.body)
        fs = self.fsx_backend.create_file_system_from_backup(
            backup_id=params.get("BackupId"),
            client_request_token=params.get("ClientRequestToken"),
            subnet_ids=params.get("SubnetIds", []),
            security_group_ids=params.get("SecurityGroupIds"),
            tags=params.get("Tags"),
            windows_configuration=params.get("WindowsConfiguration"),
            lustre_configuration=params.get("LustreConfiguration"),
            storage_type=params.get("StorageType"),
            kms_key_id=params.get("KmsKeyId"),
            file_system_type_version=params.get("FileSystemTypeVersion"),
            open_zfs_configuration=params.get("OpenZFSConfiguration"),
            storage_capacity=params.get("StorageCapacity"),
        )
        return json.dumps({"FileSystem": fs.to_dict()})

    # --- Storage Virtual Machine ---

    def create_storage_virtual_machine(self) -> str:
        params = json.loads(self.body)
        svm = self.fsx_backend.create_storage_virtual_machine(
            file_system_id=params.get("FileSystemId"),
            name=params.get("Name"),
            active_directory_configuration=params.get("ActiveDirectoryConfiguration"),
            root_volume_security_style=params.get("RootVolumeSecurityStyle"),
            tags=params.get("Tags"),
        )
        return json.dumps({"StorageVirtualMachine": svm.to_dict()})

    def delete_storage_virtual_machine(self) -> str:
        params = json.loads(self.body)
        resp = self.fsx_backend.delete_storage_virtual_machine(
            storage_virtual_machine_id=params.get("StorageVirtualMachineId"),
        )
        return json.dumps(resp)

    def describe_storage_virtual_machines(self) -> str:
        params = json.loads(self.body)
        svm_ids = params.get("StorageVirtualMachineIds")
        filters = params.get("Filters")
        svms = self.fsx_backend.describe_storage_virtual_machines(
            storage_virtual_machine_ids=svm_ids, filters=filters
        )
        return json.dumps(
            {"StorageVirtualMachines": [s.to_dict() for s in svms], "NextToken": None}
        )

    # --- Volume ---

    def create_volume(self) -> str:
        params = json.loads(self.body)
        vol = self.fsx_backend.create_volume(
            volume_type=params.get("VolumeType"),
            name=params.get("Name"),
            ontap_configuration=params.get("OntapConfiguration"),
            open_zfs_configuration=params.get("OpenZFSConfiguration"),
            tags=params.get("Tags"),
        )
        return json.dumps({"Volume": vol.to_dict()})

    def create_volume_from_backup(self) -> str:
        params = json.loads(self.body)
        vol = self.fsx_backend.create_volume_from_backup(
            backup_id=params.get("BackupId"),
            name=params.get("Name"),
            ontap_configuration=params.get("OntapConfiguration"),
            tags=params.get("Tags"),
        )
        return json.dumps({"Volume": vol.to_dict()})

    def delete_volume(self) -> str:
        params = json.loads(self.body)
        resp = self.fsx_backend.delete_volume(volume_id=params.get("VolumeId"))
        return json.dumps(resp)

    def describe_volumes(self) -> str:
        params = json.loads(self.body)
        volume_ids = params.get("VolumeIds")
        filters = params.get("Filters")
        volumes = self.fsx_backend.describe_volumes(
            volume_ids=volume_ids, filters=filters
        )
        return json.dumps(
            {"Volumes": [v.to_dict() for v in volumes], "NextToken": None}
        )

    # --- Snapshot ---

    def create_snapshot(self) -> str:
        params = json.loads(self.body)
        snap = self.fsx_backend.create_snapshot(
            name=params.get("Name"),
            volume_id=params.get("VolumeId"),
            tags=params.get("Tags"),
        )
        return json.dumps({"Snapshot": snap.to_dict()})

    def delete_snapshot(self) -> str:
        params = json.loads(self.body)
        resp = self.fsx_backend.delete_snapshot(snapshot_id=params.get("SnapshotId"))
        return json.dumps(resp)

    def update_snapshot(self) -> str:
        params = json.loads(self.body)
        snap = self.fsx_backend.update_snapshot(
            snapshot_id=params.get("SnapshotId"),
            name=params.get("Name"),
        )
        return json.dumps({"Snapshot": snap.to_dict()})

    def describe_snapshots(self) -> str:
        params = json.loads(self.body)
        snapshot_ids = params.get("SnapshotIds")
        filters = params.get("Filters")
        snapshots = self.fsx_backend.describe_snapshots(
            snapshot_ids=snapshot_ids, filters=filters
        )
        return json.dumps(
            {"Snapshots": [s.to_dict() for s in snapshots], "NextToken": None}
        )

    # --- File System Aliases ---

    def associate_file_system_aliases(self) -> str:
        params = json.loads(self.body)
        aliases = self.fsx_backend.associate_file_system_aliases(
            file_system_id=params.get("FileSystemId"),
            aliases=params.get("Aliases", []),
        )
        return json.dumps({"Aliases": aliases})

    def disassociate_file_system_aliases(self) -> str:
        params = json.loads(self.body)
        aliases = self.fsx_backend.disassociate_file_system_aliases(
            file_system_id=params.get("FileSystemId"),
            aliases=params.get("Aliases", []),
        )
        return json.dumps({"Aliases": aliases})

    # --- Data Repository Association ---

    def create_data_repository_association(self) -> str:
        params = json.loads(self.body)
        assoc = self.fsx_backend.create_data_repository_association(
            file_system_id=params.get("FileSystemId"),
            file_system_path=params.get("FileSystemPath"),
            data_repository_path=params.get("DataRepositoryPath"),
            batch_import_meta_data_on_create=params.get("BatchImportMetaDataOnCreate"),
            imported_file_chunk_size=params.get("ImportedFileChunkSize"),
            s3=params.get("S3"),
            tags=params.get("Tags"),
        )
        return json.dumps({"Association": assoc.to_dict()})

    def update_data_repository_association(self) -> str:
        params = json.loads(self.body)
        assoc = self.fsx_backend.update_data_repository_association(
            association_id=params.get("AssociationId"),
            imported_file_chunk_size=params.get("ImportedFileChunkSize"),
            s3=params.get("S3"),
        )
        return json.dumps({"Association": assoc.to_dict()})

    def delete_data_repository_association(self) -> str:
        params = json.loads(self.body)
        resp = self.fsx_backend.delete_data_repository_association(
            association_id=params.get("AssociationId"),
            delete_data_in_file_system=params.get("DeleteDataInFileSystem"),
        )
        return json.dumps(resp)

    def describe_data_repository_associations(self) -> str:
        params = json.loads(self.body)
        association_ids = params.get("AssociationIds")
        filters = params.get("Filters")
        associations = self.fsx_backend.describe_data_repository_associations(
            association_ids=association_ids, filters=filters
        )
        return json.dumps(
            {"Associations": [a.to_dict() for a in associations], "NextToken": None}
        )

    def describe_data_repository_tasks(self) -> str:
        params = json.loads(self.body)
        task_ids = params.get("TaskIds")
        filters = params.get("Filters")
        tasks = self.fsx_backend.describe_data_repository_tasks(
            task_ids=task_ids, filters=filters
        )
        return json.dumps({"DataRepositoryTasks": tasks, "NextToken": None})

    def describe_file_caches(self) -> str:
        params = json.loads(self.body)
        file_cache_ids = params.get("FileCacheIds")
        caches = self.fsx_backend.describe_file_caches(
            file_cache_ids=file_cache_ids
        )
        return json.dumps({"FileCaches": caches, "NextToken": None})

    def describe_file_system_aliases(self) -> str:
        params = json.loads(self.body)
        file_system_id = params.get("FileSystemId")
        aliases = self.fsx_backend.describe_file_system_aliases(
            file_system_id=file_system_id
        )
        return json.dumps({"Aliases": aliases, "NextToken": None})

    def describe_shared_vpc_configuration(self) -> str:
        config = self.fsx_backend.describe_shared_vpc_configuration()
        return json.dumps(config)

    def describe_s3_access_point_attachments(self) -> str:
        params = json.loads(self.body)
        file_system_id = params.get("FileSystemId")
        filters = params.get("Filters")
        attachments = self.fsx_backend.describe_s3_access_point_attachments(
            file_system_id=file_system_id, filters=filters
        )
        return json.dumps(
            {"S3AccessPointAttachments": attachments, "NextToken": None}
        )

    def tag_resource(self) -> TYPE_RESPONSE:
        params = json.loads(self.body)
        resource_arn = params.get("ResourceARN")
        tags = params.get("Tags")
        self.fsx_backend.tag_resource(
            resource_arn=resource_arn,
            tags=tags,
        )
        return 200, {}, json.dumps({})

    def untag_resource(self) -> TYPE_RESPONSE:
        params = json.loads(self.body)
        resource_arn = params.get("ResourceARN")
        tag_keys = params.get("TagKeys")
        self.fsx_backend.untag_resource(
            resource_arn=resource_arn,
            tag_keys=tag_keys,
        )
        return 200, {}, json.dumps({})

    def list_tags_for_resource(self) -> str:
        params = json.loads(self.body)
        resource_arn = params.get("ResourceARN")
        tags = self.fsx_backend.list_tags_for_resource(resource_arn=resource_arn)
        return json.dumps({"Tags": tags})
