from ._base_response import EC2BaseResponse


class StoreImageTaskResponse(EC2BaseResponse):
    def create_store_image_task(self) -> str:
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
        template = self.response_template(CREATE_STORE_IMAGE_TASK)
        return template.render(task=task)

    def describe_store_image_tasks(self) -> str:
        image_ids = self._get_param("ImageId", [])
        tasks = self.ec2_backend.describe_store_image_tasks(
            image_ids=image_ids or None,
        )
        template = self.response_template(DESCRIBE_STORE_IMAGE_TASKS)
        return template.render(tasks=tasks)


CREATE_STORE_IMAGE_TASK = """<CreateStoreImageTaskResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
  <requestId>7a62c49f-347e-4fc4-9331-6e8eEXAMPLE</requestId>
  <objectKey>{{ task.s3objectKey }}</objectKey>
</CreateStoreImageTaskResponse>"""

DESCRIBE_STORE_IMAGE_TASKS = """<DescribeStoreImageTasksResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
  <requestId>7a62c49f-347e-4fc4-9331-6e8eEXAMPLE</requestId>
  <storeImageTaskResultSet>
    {% for task in tasks %}
    <item>
      <amiId>{{ task.ami_id }}</amiId>
      <bucket>{{ task.bucket }}</bucket>
      <s3objectKey>{{ task.s3objectKey }}</s3objectKey>
      <taskStartTime>{{ task.task_start_time }}</taskStartTime>
      <storeTaskState>{{ task.store_task_state }}</storeTaskState>
      <progressPercentage>{{ task.progress }}</progressPercentage>
    </item>
    {% endfor %}
  </storeImageTaskResultSet>
</DescribeStoreImageTasksResponse>"""
