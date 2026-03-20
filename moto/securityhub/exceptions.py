"""Exceptions raised by the securityhub service."""

from moto.core.exceptions import JsonRESTError


class SecurityHubClientError(JsonRESTError):
    code = 400


class _InvalidOperationException(SecurityHubClientError):
    def __init__(self, error_type: str, op: str, msg: str):
        super().__init__(
            error_type,
            f"An error occurred ({error_type}) when calling the {op} operation: {msg}",
        )


class InvalidInputException(_InvalidOperationException):
    def __init__(self, op: str, msg: str):
        super().__init__("InvalidInputException", op, msg)


class InvalidAccessException(SecurityHubClientError):
    code = 402

    def __init__(self, msg: str):
        super().__init__("InvalidAccessException", msg)


class ResourceNotFoundException(SecurityHubClientError):
    code = 404

    def __init__(self, msg: str):
        super().__init__("ResourceNotFoundException", msg)
