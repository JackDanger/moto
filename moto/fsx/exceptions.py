"""Exceptions raised by the fsx service."""

from moto.core.exceptions import JsonRESTError


class ResourceNotFoundException(JsonRESTError):
    def __init__(self, msg: str):
        super().__init__("ResourceNotFoundException", f"{msg}")


class FileSystemNotFoundException(JsonRESTError):
    def __init__(self, file_system_id: str):
        super().__init__(
            "FileSystemNotFound",
            f"File system '{file_system_id}' does not exist.",
        )


class BackupNotFoundException(JsonRESTError):
    def __init__(self, backup_id: str):
        super().__init__(
            "BackupNotFound",
            f"Backup '{backup_id}' does not exist.",
        )


class VolumeNotFoundException(JsonRESTError):
    def __init__(self, volume_id: str):
        super().__init__(
            "VolumeNotFound",
            f"Volume '{volume_id}' does not exist.",
        )


class SnapshotNotFoundException(JsonRESTError):
    def __init__(self, snapshot_id: str):
        super().__init__(
            "SnapshotNotFound",
            f"Snapshot '{snapshot_id}' does not exist.",
        )


class StorageVirtualMachineNotFoundException(JsonRESTError):
    def __init__(self, svm_id: str):
        super().__init__(
            "StorageVirtualMachineNotFound",
            f"Storage virtual machine '{svm_id}' does not exist.",
        )
