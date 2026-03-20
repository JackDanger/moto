from moto.core.exceptions import JsonRESTError


class ValidationError(JsonRESTError):
    def __init__(self, message: str):
        super().__init__("ValidationException", message)


class ResourceNotFoundException(JsonRESTError):
    code = 404

    def __init__(self, message: str):
        super().__init__("ResourceNotFoundException", message)


class ConflictException(JsonRESTError):
    code = 409

    def __init__(self, message: str):
        super().__init__("ConflictException", message)
