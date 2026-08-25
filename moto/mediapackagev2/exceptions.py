"""Exceptions raised by the mediapackagev2 service."""

from moto.core.exceptions import JsonRESTError


class ChannelGroupNotEmpty(JsonRESTError):
    def __init__(self) -> None:
        msg = "The channel group you tried to delete has channels attached to it. If you want to delete this channel group, you must first delete the channels attached to it"
        super().__init__(error_type="ConflictException", message=msg)


class ChannelNotFound(JsonRESTError):
    def __init__(self) -> None:
        msg = "MediaPackage can't process your request because we can't find your channel. Verify your channel name or add a channel and then try again"
        super().__init__(error_type="ResourceNotFoundException", message=msg)


class ChannelGroupNotFound(JsonRESTError):
    def __init__(self) -> None:
        msg = "MediaPackage can't process your request because we can't find your channel group. Verify your channel group name or add a channel group and then try again"
        super().__init__(error_type="ResourceNotFoundException", message=msg)


class OriginEndpointNotFound(JsonRESTError):
    def __init__(self) -> None:
        msg = "MediaPackage can't process your request because we can't find your origin endpoint. Verify your origin endpoint name or add an origin endpoint and then try again"
        super().__init__(error_type="ResourceNotFoundException", message=msg)


class HarvestJobNotFound(JsonRESTError):
    def __init__(self) -> None:
        msg = "MediaPackage can't process your request because we can't find your harvest job. Verify your harvest job name and try again"
        super().__init__(error_type="ResourceNotFoundException", message=msg)


class OriginEndpointPolicyNotFound(JsonRESTError):
    def __init__(self) -> None:
        msg = "MediaPackage can't process your request because we can't find the policy for this origin endpoint"
        super().__init__(error_type="ResourceNotFoundException", message=msg)


class ChannelPolicyNotFound(JsonRESTError):
    def __init__(self) -> None:
        msg = "MediaPackage can't process your request because we can't find the policy for this channel"
        super().__init__(error_type="ResourceNotFoundException", message=msg)
