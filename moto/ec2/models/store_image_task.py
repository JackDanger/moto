from typing import Any, Optional

from moto.core.utils import iso_8601_datetime_with_milliseconds, utcnow


class StoreImageTask:
    def __init__(
        self,
        ec2_backend: Any,
        image_id: str,
        bucket: str,
        s3_object_tags: Optional[list[dict[str, str]]] = None,
    ):
        self.ec2_backend = ec2_backend
        self.image_id = image_id
        self.bucket = bucket
        self.s3_object_tags = s3_object_tags or []
        self.task_state = "Completed"
        self.progress = 100
        self.store_task_state = "Completed"
        self.store_task_failure_reason = ""
        self.ami_id = image_id
        self.s3objectKey = f"{image_id}.bin"
        self._created_at = utcnow()

    @property
    def task_start_time(self) -> str:
        return iso_8601_datetime_with_milliseconds(self._created_at)


class StoreImageTaskBackend:
    def __init__(self) -> None:
        self.store_image_tasks: list[StoreImageTask] = []

    def create_store_image_task(
        self,
        image_id: str,
        bucket: str,
        s3_object_tags: Optional[list[dict[str, str]]] = None,
    ) -> StoreImageTask:
        task = StoreImageTask(
            self,
            image_id=image_id,
            bucket=bucket,
            s3_object_tags=s3_object_tags,
        )
        self.store_image_tasks.append(task)
        return task

    def describe_store_image_tasks(
        self,
        image_ids: Optional[list[str]] = None,
    ) -> list[StoreImageTask]:
        tasks = self.store_image_tasks
        if image_ids:
            tasks = [t for t in tasks if t.image_id in image_ids]
        return tasks
