from typing import Any, Optional

from moto.core.utils import iso_8601_datetime_with_milliseconds, utcnow


class FastLaunchImage:
    def __init__(
        self,
        ec2_backend: Any,
        image_id: str,
        resource_type: str = "snapshot",
        max_parallel_launches: int = 6,
        snapshot_configuration: Optional[dict[str, int]] = None,
        launch_template: Optional[dict[str, str]] = None,
    ):
        self.ec2_backend = ec2_backend
        self.image_id = image_id
        self.resource_type = resource_type
        self.max_parallel_launches = max_parallel_launches
        self.snapshot_configuration = snapshot_configuration or {
            "TargetResourceCount": 5
        }
        self.launch_template = launch_template
        self.state = "enabled"
        self._state_transition_time = utcnow()

    @property
    def state_transition_time(self) -> str:
        return iso_8601_datetime_with_milliseconds(
            self._state_transition_time
        )

    @property
    def owner_id(self) -> str:
        return self.ec2_backend.account_id

    @property
    def state_transition_reason(self) -> str:
        if self.state == "enabled":
            return "Client.UserInitiated"
        return "Client.UserInitiated - Disabling"


class FastLaunchBackend:
    def __init__(self) -> None:
        self.fast_launch_images: dict[str, FastLaunchImage] = {}

    def enable_fast_launch(
        self,
        image_id: str,
        resource_type: str = "snapshot",
        max_parallel_launches: int = 6,
        snapshot_configuration: Optional[dict[str, int]] = None,
        launch_template: Optional[dict[str, str]] = None,
    ) -> FastLaunchImage:
        fli = FastLaunchImage(
            self,
            image_id=image_id,
            resource_type=resource_type,
            max_parallel_launches=max_parallel_launches,
            snapshot_configuration=snapshot_configuration,
            launch_template=launch_template,
        )
        self.fast_launch_images[image_id] = fli
        return fli

    def describe_fast_launch_images(
        self,
        image_ids: Optional[list[str]] = None,
    ) -> list[FastLaunchImage]:
        images = list(self.fast_launch_images.values())
        if image_ids:
            images = [i for i in images if i.image_id in image_ids]
        return images

    def disable_fast_launch(self, image_id: str) -> FastLaunchImage:
        fli = self.fast_launch_images.get(image_id)
        if fli:
            fli.state = "disabling"
            fli._state_transition_time = utcnow()
            return self.fast_launch_images.pop(image_id)
        # If not found, return a synthetic disabled result
        fli = FastLaunchImage(self, image_id=image_id)
        fli.state = "disabling"
        return fli
