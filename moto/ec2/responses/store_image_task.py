from moto.core.responses import ActionResult

from ._base_response import EC2BaseResponse


class StoreImageTaskResponse(EC2BaseResponse):
    def create_store_image_task(self) -> ActionResult:
        image_id = self._get_param("ImageId")
        bucket = self._get_param("Bucket")
        s3_object_tags = self._get_param("S3ObjectTag", [])
        task = self.ec2_backend.create_store_image_task(
            image_id=image_id,
            bucket=bucket,
            s3_object_tags=s3_object_tags
            if isinstance(s3_object_tags, list)
            else [s3_object_tags],
        )
        return ActionResult({"ObjectKey": task.s3objectKey})

    def describe_store_image_tasks(self) -> ActionResult:
        image_ids = self._get_param("ImageId", [])
        tasks = self.ec2_backend.describe_store_image_tasks(
            image_ids=image_ids or None,
        )
        task_results = [
            {
                "AmiId": task.ami_id,
                "Bucket": task.bucket,
                "S3ObjectKey": task.s3objectKey,
                "TaskStartTime": task.task_start_time,
                "StoreTaskState": task.store_task_state,
                "ProgressPercentage": task.progress,
            }
            for task in tasks
        ]
        return ActionResult({"StoreImageTaskResultSet": task_results})
