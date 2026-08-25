from typing import Any, Optional

from ..utils import random_id
from .core import TaggedEC2Resource


class InstanceEventWindow(TaggedEC2Resource):
    def __init__(
        self,
        ec2_backend: Any,
        name: Optional[str] = None,
        time_ranges: Optional[list[dict[str, Any]]] = None,
        cron_expression: Optional[str] = None,
        tags: Optional[dict[str, str]] = None,
    ):
        self.ec2_backend = ec2_backend
        self.id = random_id(prefix="iew-")
        self.name = name or ""
        self.time_ranges = time_ranges or []
        self.cron_expression = cron_expression or ""
        self.state = "active"
        self.association_target: dict[str, list[str]] = {
            "instance_ids": [],
            "dedicated_host_ids": [],
            "tags": [],
        }
        self.add_tags(tags or {})


class InstanceEventWindowBackend:
    def __init__(self) -> None:
        self.instance_event_windows: dict[str, InstanceEventWindow] = {}

    def create_instance_event_window(
        self,
        name: Optional[str] = None,
        time_ranges: Optional[list[dict[str, Any]]] = None,
        cron_expression: Optional[str] = None,
        tags: Optional[dict[str, str]] = None,
    ) -> InstanceEventWindow:
        window = InstanceEventWindow(
            self,
            name=name,
            time_ranges=time_ranges,
            cron_expression=cron_expression,
            tags=tags,
        )
        self.instance_event_windows[window.id] = window
        return window

    def delete_instance_event_window(
        self, instance_event_window_id: str, force_delete: bool = False
    ) -> InstanceEventWindow:
        window = self.instance_event_windows.pop(instance_event_window_id, None)
        if not window:
            from ..exceptions import EC2ClientError

            raise EC2ClientError(
                "InvalidInstanceEventWindowId.NotFound",
                f"The instance event window ID '{instance_event_window_id}' does not exist",
            )
        window.state = "deleted"
        return window

    def describe_instance_event_windows(
        self,
        instance_event_window_ids: Optional[list[str]] = None,
    ) -> list[InstanceEventWindow]:
        windows = [
            w for w in self.instance_event_windows.values() if w.state != "deleted"
        ]
        if instance_event_window_ids:
            windows = [w for w in windows if w.id in instance_event_window_ids]
        return windows

    def modify_instance_event_window(
        self,
        instance_event_window_id: str,
        name: Optional[str] = None,
        time_ranges: Optional[list[dict[str, Any]]] = None,
        cron_expression: Optional[str] = None,
    ) -> InstanceEventWindow:
        window = self.instance_event_windows.get(instance_event_window_id)
        if not window:
            from ..exceptions import EC2ClientError

            raise EC2ClientError(
                "InvalidInstanceEventWindowId.NotFound",
                f"The instance event window ID '{instance_event_window_id}' does not exist",
            )
        if name is not None:
            window.name = name
        if time_ranges is not None:
            window.time_ranges = time_ranges
        if cron_expression is not None:
            window.cron_expression = cron_expression
        return window

    def associate_instance_event_window(
        self,
        instance_event_window_id: str,
        instance_ids: Optional[list[str]] = None,
        dedicated_host_ids: Optional[list[str]] = None,
        instance_tags: Optional[list[dict[str, str]]] = None,
    ) -> InstanceEventWindow:
        window = self.instance_event_windows.get(instance_event_window_id)
        if not window:
            from ..exceptions import EC2ClientError

            raise EC2ClientError(
                "InvalidInstanceEventWindowId.NotFound",
                f"The instance event window ID '{instance_event_window_id}' does not exist",
            )
        if instance_ids:
            window.association_target["instance_ids"].extend(instance_ids)
        if dedicated_host_ids:
            window.association_target["dedicated_host_ids"].extend(dedicated_host_ids)
        if instance_tags:
            window.association_target["tags"].extend(instance_tags)
        return window

    def disassociate_instance_event_window(
        self,
        instance_event_window_id: str,
        instance_ids: Optional[list[str]] = None,
        dedicated_host_ids: Optional[list[str]] = None,
        instance_tags: Optional[list[dict[str, str]]] = None,
    ) -> InstanceEventWindow:
        window = self.instance_event_windows.get(instance_event_window_id)
        if not window:
            from ..exceptions import EC2ClientError

            raise EC2ClientError(
                "InvalidInstanceEventWindowId.NotFound",
                f"The instance event window ID '{instance_event_window_id}' does not exist",
            )
        if instance_ids:
            for iid in instance_ids:
                if iid in window.association_target["instance_ids"]:
                    window.association_target["instance_ids"].remove(iid)
        if dedicated_host_ids:
            for hid in dedicated_host_ids:
                if hid in window.association_target["dedicated_host_ids"]:
                    window.association_target["dedicated_host_ids"].remove(hid)
        return window
