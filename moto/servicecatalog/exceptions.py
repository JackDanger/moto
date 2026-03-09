from moto.core.exceptions import JsonRESTError


class ResourceNotFoundException(JsonRESTError):
    code = 400

    def __init__(self, message: str):
        super().__init__("ResourceNotFoundException", message)


class InvalidParametersException(JsonRESTError):
    code = 400

    def __init__(self, message: str):
        super().__init__("InvalidParametersException", message)


class DuplicateResourceException(JsonRESTError):
    code = 400

    def __init__(self, message: str):
        super().__init__("DuplicateResourceException", message)


class ResourceInUseException(JsonRESTError):
    code = 400

    def __init__(self, message: str):
        super().__init__("ResourceInUseException", message)
