from moto.core.exceptions import JsonRESTError


class AlreadyExistsException(JsonRESTError):
    code = 400

    def __init__(self, message):
        super().__init__("AlreadyExistsException", message)


class SESV2NotFoundException(JsonRESTError):
    code = 404

    def __init__(self, message):
        super().__init__("NotFoundException", message)
