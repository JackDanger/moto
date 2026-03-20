"""Exceptions raised by the kinesisanalyticsv2 service."""

import json

from moto.core.exceptions import JsonRESTError


class ResourceNotFoundException(JsonRESTError):
    def __init__(self, message: str) -> None:
        super().__init__(error_type="ResourceNotFoundException", message=message)


class ResourceInUseException(JsonRESTError):
    def __init__(self, message: str) -> None:
        super().__init__(error_type="ResourceInUseException", message=message)


class InvalidArgumentException(JsonRESTError):
    def __init__(self, message: str) -> None:
        super().__init__(error_type="InvalidArgumentException", message=message)


class ConcurrentModificationException(JsonRESTError):
    def __init__(self, message: str = "") -> None:
        super().__init__(
            error_type="ConcurrentModificationException",
            message=message or "There is a concurrent modification to the application.",
        )
