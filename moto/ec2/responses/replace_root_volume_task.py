from moto.core.responses import ActionResult
from moto.ec2.utils import add_tag_specification
from moto.utilities.utils import str2bool

from ._base_response import EC2BaseResponse


class ReplaceRootVolumeTaskResponse(EC2BaseResponse):
    def create_replace_root_volume_task(self) -> ActionResult:
        instance_id = self._get_param("InstanceId")
        snapshot_id = self._get_param("SnapshotId")
        image_id = self._get_param("ImageId")
        delete_replaced = str2bool(self._get_param("DeleteReplacedRootVolume", "false"))
        tags = add_tag_specification(self._get_param("TagSpecifications", []))
        task = self.ec2_backend.create_replace_root_volume_task(
            instance_id=instance_id,
            snapshot_id=snapshot_id,
            image_id=image_id,
            delete_replaced_root_volume=delete_replaced,
            tags=tags,
        )
        tag_set = [{"Key": tag.key, "Value": tag.value} for tag in task.get_tags()]
        result = {
            "ReplaceRootVolumeTaskId": task.id,
            "InstanceId": task.instance_id,
            "TaskState": task.task_state,
            "StartTime": task.start_time,
            "CompleteTime": task.complete_time,
            "DeleteReplacedRootVolume": task.delete_replaced_root_volume,
            "Tags": tag_set,
        }
        if task.snapshot_id:
            result["SnapshotId"] = task.snapshot_id
        if task.image_id:
            result["ImageId"] = task.image_id
        return ActionResult({"ReplaceRootVolumeTask": result})

    def describe_replace_root_volume_tasks(self) -> ActionResult:
        task_ids = self._get_param("ReplaceRootVolumeTaskId", [])
        tasks = self.ec2_backend.describe_replace_root_volume_tasks(
            task_ids=task_ids or None,
        )
        task_list = []
        for task in tasks:
            tag_set = [{"Key": tag.key, "Value": tag.value} for tag in task.get_tags()]
            task_dict = {
                "ReplaceRootVolumeTaskId": task.id,
                "InstanceId": task.instance_id,
                "TaskState": task.task_state,
                "StartTime": task.start_time,
                "CompleteTime": task.complete_time,
                "DeleteReplacedRootVolume": task.delete_replaced_root_volume,
                "Tags": tag_set,
            }
            if task.snapshot_id:
                task_dict["SnapshotId"] = task.snapshot_id
            if task.image_id:
                task_dict["ImageId"] = task.image_id
            task_list.append(task_dict)
        return ActionResult({"ReplaceRootVolumeTasks": task_list})
