"""Exceptions raised by the kafka service."""

import json

from moto.core.exceptions import JsonRESTError


class KafkaError(JsonRESTError):
    code = 400


class NotFoundException(KafkaError):
    def __init__(self, message: str) -> None:
        super().__init__("NotFoundException", message)
        self.description = json.dumps(
            {"message": message, "invalidParameter": None, "Message": message}
        )


class BadRequestException(KafkaError):
    def __init__(self, message: str) -> None:
        super().__init__("BadRequestException", message)
        self.description = json.dumps(
            {"message": message, "invalidParameter": None, "Message": message}
        )


class ConflictException(KafkaError):
    def __init__(self, message: str) -> None:
        super().__init__("ConflictException", message)
        self.description = json.dumps(
            {"message": message, "invalidParameter": None, "Message": message}
        )
