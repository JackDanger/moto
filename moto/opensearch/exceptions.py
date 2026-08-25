"""Exceptions raised by the opensearch service."""

from moto.core.exceptions import JsonRESTError


class ResourceNotFoundException(JsonRESTError):
    code = 404

    def __init__(self, name: str):
        super().__init__("ResourceNotFoundException", f"Domain not found: {name}")


class EngineTypeNotFoundException(JsonRESTError):
    def __init__(self, domain_name: str):
        super().__init__(
            "EngineTypeNotFoundException", f"Engine Type not found: {domain_name}"
        )


class ResourceAlreadyExistsException(JsonRESTError):
    code = 409

    def __init__(self, name: str):
        super().__init__(
            "ResourceAlreadyExistsException",
            f"Domain already exists: {name}",
        )


class ConflictException(JsonRESTError):
    code = 409

    def __init__(self, message: str):
        super().__init__("ConflictException", message)
