from moto.ec2.utils import add_tag_specification
from moto.utilities.utils import str2bool

from ._base_response import EC2BaseResponse


class ReplaceRootVolumeTaskResponse(EC2BaseResponse):
    def create_replace_root_volume_task(self) -> str:
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
        template = self.response_template(CREATE_REPLACE_ROOT_VOLUME_TASK)
        return template.render(task=task)

    def describe_replace_root_volume_tasks(self) -> str:
        task_ids = self._get_param("ReplaceRootVolumeTaskId", [])
        tasks = self.ec2_backend.describe_replace_root_volume_tasks(
            task_ids=task_ids or None,
        )
        template = self.response_template(DESCRIBE_REPLACE_ROOT_VOLUME_TASKS)
        return template.render(tasks=tasks)


CREATE_REPLACE_ROOT_VOLUME_TASK = """<CreateReplaceRootVolumeTaskResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
  <requestId>7a62c49f-347e-4fc4-9331-6e8eEXAMPLE</requestId>
  <replaceRootVolumeTask>
    <replaceRootVolumeTaskId>{{ task.id }}</replaceRootVolumeTaskId>
    <instanceId>{{ task.instance_id }}</instanceId>
    <taskState>{{ task.task_state }}</taskState>
    <startTime>{{ task.start_time }}</startTime>
    <completeTime>{{ task.complete_time }}</completeTime>
    <deleteReplacedRootVolume>{{ 'true' if task.delete_replaced_root_volume else 'false' }}</deleteReplacedRootVolume>
    {% if task.snapshot_id %}
    <snapshotId>{{ task.snapshot_id }}</snapshotId>
    {% endif %}
    {% if task.image_id %}
    <imageId>{{ task.image_id }}</imageId>
    {% endif %}
    <tagSet>
      {% for tag in task.get_tags() %}
      <item>
        <key>{{ tag.key }}</key>
        <value>{{ tag.value }}</value>
      </item>
      {% endfor %}
    </tagSet>
  </replaceRootVolumeTask>
</CreateReplaceRootVolumeTaskResponse>"""

DESCRIBE_REPLACE_ROOT_VOLUME_TASKS = """<DescribeReplaceRootVolumeTasksResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
  <requestId>7a62c49f-347e-4fc4-9331-6e8eEXAMPLE</requestId>
  <replaceRootVolumeTaskSet>
    {% for task in tasks %}
    <item>
      <replaceRootVolumeTaskId>{{ task.id }}</replaceRootVolumeTaskId>
      <instanceId>{{ task.instance_id }}</instanceId>
      <taskState>{{ task.task_state }}</taskState>
      <startTime>{{ task.start_time }}</startTime>
      <completeTime>{{ task.complete_time }}</completeTime>
      <deleteReplacedRootVolume>{{ 'true' if task.delete_replaced_root_volume else 'false' }}</deleteReplacedRootVolume>
      {% if task.snapshot_id %}
      <snapshotId>{{ task.snapshot_id }}</snapshotId>
      {% endif %}
      {% if task.image_id %}
      <imageId>{{ task.image_id }}</imageId>
      {% endif %}
      <tagSet>
        {% for tag in task.get_tags() %}
        <item>
          <key>{{ tag.key }}</key>
          <value>{{ tag.value }}</value>
        </item>
        {% endfor %}
      </tagSet>
    </item>
    {% endfor %}
  </replaceRootVolumeTaskSet>
</DescribeReplaceRootVolumeTasksResponse>"""
