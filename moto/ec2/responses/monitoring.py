from moto.core.responses import ActionResult

from ._base_response import EC2BaseResponse


class Monitoring(EC2BaseResponse):
    def monitor_instances(self) -> ActionResult:
        self.error_on_dryrun()
        instance_ids = self._get_param("InstanceIds", [])
        instances = self.ec2_backend.monitor_instances(instance_ids)
        result = {
            "InstanceMonitorings": [
                {
                    "InstanceId": instance.id,
                    "Monitoring": {"State": instance.monitoring_state},
                }
                for instance in instances
            ]
        }
        return ActionResult(result)

    def unmonitor_instances(self) -> ActionResult:
        self.error_on_dryrun()
        instance_ids = self._get_param("InstanceIds", [])
        instances = self.ec2_backend.unmonitor_instances(instance_ids)
        result = {
            "InstanceMonitorings": [
                {
                    "InstanceId": instance.id,
                    "Monitoring": {"State": instance.monitoring_state},
                }
                for instance in instances
            ]
        }
        return ActionResult(result)
