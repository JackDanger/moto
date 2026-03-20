from moto.core.responses import ActionResult
from moto.core.utils import utcnow

from ._base_response import EC2BaseResponse


class Windows(EC2BaseResponse):
    def bundle_instance(self) -> str:
        raise NotImplementedError("Windows.bundle_instance is not yet implemented")

    def cancel_bundle_task(self) -> str:
        raise NotImplementedError("Windows.cancel_bundle_task is not yet implemented")

    def describe_bundle_tasks(self) -> str:
        template = self.response_template(DESCRIBE_BUNDLE_TASKS_TEMPLATE)
        return template.render()

    def get_password_data(self) -> ActionResult:
        instance_id = self._get_param("InstanceId")
        password_data = self.ec2_backend.get_password_data(instance_id)
        result = {
            "InstanceId": instance_id,
            "Timestamp": utcnow(),
            "PasswordData": password_data,
        }
        return ActionResult(result)


DESCRIBE_BUNDLE_TASKS_TEMPLATE = """<DescribeBundleTasksResponse xmlns="http://ec2.amazonaws.com/doc/2013-10-15/">
  <requestId>59dbff89-35bd-4eac-99ed-be587EXAMPLE</requestId>
  <bundleInstanceTasksSet/>
</DescribeBundleTasksResponse>"""
