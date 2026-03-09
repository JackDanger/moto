from typing import Any, Optional

from moto.core.utils import iso_8601_datetime_with_milliseconds, utcnow

from ..utils import random_id
from .core import TaggedEC2Resource


class ReplaceRootVolumeTask(TaggedEC2Resource):
    def __init__(
        self,
        ec2_backend: Any,
        instance_id: str,
        snapshot_id: Optional[str] = None,
        image_id: Optional[str] = None,
        delete_replaced_root_volume: bool = False,
        tags: Optional[dict[str, str]] = None,
    ):
        self.ec2_backend = ec2_backend
        self.id = random_id(prefix="replacevol-")
        self.instance_id = instance_id
        self.snapshot_id = snapshot_id or ""
        self.image_id = image_id or ""
        self.delete_replaced_root_volume = delete_replaced_root_volume
        self.task_state = "succeeded"
        self.complete_time = iso_8601_datetime_with_milliseconds(utcnow())
        self.start_time = iso_8601_datetime_with_milliseconds(utcnow())
        self.add_tags(tags or {})


class ReplaceRootVolumeTaskBackend:
    def __init__(self) -> None:
        self.replace_root_volume_tasks: dict[str, ReplaceRootVolumeTask] = {}

    def create_replace_root_volume_task(
        self,
        instance_id: str,
        snapshot_id: Optional[str] = None,
        image_id: Optional[str] = None,
        delete_replaced_root_volume: bool = False,
        tags: Optional[dict[str, str]] = None,
    ) -> ReplaceRootVolumeTask:
        task = ReplaceRootVolumeTask(
            self,
            instance_id=instance_id,
            snapshot_id=snapshot_id,
            image_id=image_id,
            delete_replaced_root_volume=delete_replaced_root_volume,
            tags=tags,
        )
        self.replace_root_volume_tasks[task.id] = task
        return task

    def describe_replace_root_volume_tasks(
        self,
        task_ids: Optional[list[str]] = None,
    ) -> list[ReplaceRootVolumeTask]:
        tasks = list(self.replace_root_volume_tasks.values())
        if task_ids:
            tasks = [t for t in tasks if t.id in task_ids]
        return tasks
