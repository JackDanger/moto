"""Exceptions raised by the networkfirewall service."""

import json

from moto.core.exceptions import JsonRESTError


class ResourceNotFound(JsonRESTError):
    code = 400

    def __init__(self, resource_id: str):
        super().__init__("ResourceNotFoundException", "Resource not found.")
        self.description = json.dumps(
            {
                "__type": "ResourceNotFoundException",
                "Message": "Resource not found.",
                "ResourceId": resource_id,
            }
        )


class ResourceInUse(JsonRESTError):
    code = 400

    def __init__(self, message: str):
        super().__init__("ResourceOwnerCheckException", message)
        self.description = json.dumps(
            {
                "__type": "ResourceOwnerCheckException",
                "Message": message,
            }
        )


class InvalidRequest(JsonRESTError):
    code = 400

    def __init__(self, message: str):
        super().__init__("InvalidRequestException", message)
        self.description = json.dumps(
            {
                "__type": "InvalidRequestException",
                "Message": message,
            }
        )
