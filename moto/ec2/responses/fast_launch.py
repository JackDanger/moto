from moto.core.responses import ActionResult

from ._base_response import EC2BaseResponse


class FastLaunchResponse(EC2BaseResponse):
    def enable_fast_launch(self) -> ActionResult:
        image_id = self._get_param("ImageId")
        resource_type = self._get_param("ResourceType", "snapshot")
        max_parallel = int(self._get_param("MaxParallelLaunches", "6"))
        snapshot_config = self._get_param("SnapshotConfiguration")
        launch_template = self._get_param("LaunchTemplate")
        fli = self.ec2_backend.enable_fast_launch(
            image_id=image_id,
            resource_type=resource_type,
            max_parallel_launches=max_parallel,
            snapshot_configuration=snapshot_config,
            launch_template=launch_template,
        )
        result = {
            "ImageId": fli.image_id,
            "ResourceType": fli.resource_type,
            "SnapshotConfiguration": {
                "TargetResourceCount": fli.snapshot_configuration.get(
                    "TargetResourceCount", 5
                ),
            },
            "MaxParallelLaunches": fli.max_parallel_launches,
            "OwnerId": fli.owner_id,
            "State": fli.state,
            "StateTransitionReason": fli.state_transition_reason,
            "StateTransitionTime": fli.state_transition_time,
        }
        return ActionResult(result)

    def describe_fast_launch_images(self) -> ActionResult:
        image_ids = self._get_param("ImageId", [])
        images = self.ec2_backend.describe_fast_launch_images(
            image_ids=image_ids or None,
        )
        result = {
            "FastLaunchImages": [
                {
                    "ImageId": fli.image_id,
                    "ResourceType": fli.resource_type,
                    "SnapshotConfiguration": {
                        "TargetResourceCount": fli.snapshot_configuration.get(
                            "TargetResourceCount", 5
                        ),
                    },
                    "MaxParallelLaunches": fli.max_parallel_launches,
                    "OwnerId": fli.owner_id,
                    "State": fli.state,
                    "StateTransitionReason": fli.state_transition_reason,
                    "StateTransitionTime": fli.state_transition_time,
                }
                for fli in images
            ]
        }
        return ActionResult(result)

    def disable_fast_launch(self) -> ActionResult:
        image_id = self._get_param("ImageId")
        fli = self.ec2_backend.disable_fast_launch(image_id=image_id)
        result = {
            "ImageId": fli.image_id,
            "ResourceType": fli.resource_type,
            "MaxParallelLaunches": fli.max_parallel_launches,
            "OwnerId": fli.owner_id,
            "State": fli.state,
            "StateTransitionReason": fli.state_transition_reason,
            "StateTransitionTime": fli.state_transition_time,
        }
        return ActionResult(result)
