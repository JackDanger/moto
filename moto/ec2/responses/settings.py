from moto.core.responses import ActionResult

from ._base_response import EC2BaseResponse


class Settings(EC2BaseResponse):
    def enable_fast_snapshot_restores(self) -> ActionResult:
        availability_zones = self._get_param("AvailabilityZones", [])
        source_snapshot_ids = self._get_param("SourceSnapshotIds", [])
        successful = [
            {
                "SnapshotId": snap_id,
                "AvailabilityZone": az,
                "State": "enabled",
            }
            for snap_id in source_snapshot_ids
            for az in availability_zones
        ]
        return ActionResult({"Successful": successful, "Unsuccessful": []})

    def disable_fast_snapshot_restores(self) -> ActionResult:
        availability_zones = self._get_param("AvailabilityZones", [])
        source_snapshot_ids = self._get_param("SourceSnapshotIds", [])
        successful = [
            {
                "SnapshotId": snap_id,
                "AvailabilityZone": az,
                "State": "disabled",
            }
            for snap_id in source_snapshot_ids
            for az in availability_zones
        ]
        return ActionResult({"Successful": successful, "Unsuccessful": []})

    def disable_ebs_encryption_by_default(self) -> ActionResult:
        self.error_on_dryrun()
        self.ec2_backend.disable_ebs_encryption_by_default()
        return ActionResult({"EbsEncryptionByDefault": False})

    def enable_ebs_encryption_by_default(self) -> ActionResult:
        self.error_on_dryrun()
        self.ec2_backend.enable_ebs_encryption_by_default()
        return ActionResult({"EbsEncryptionByDefault": True})

    def get_ebs_encryption_by_default(self) -> ActionResult:
        self.error_on_dryrun()
        value = self.ec2_backend.get_ebs_encryption_by_default()
        return ActionResult({"EbsEncryptionByDefault": value})
