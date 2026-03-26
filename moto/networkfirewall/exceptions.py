"""Exceptions raised by the networkfirewall service."""

import json

from moto.core.exceptions import JsonRESTError


class ResourceNotFound(JsonRESTError):
    def __init__(self, resource_id: str):
        super().__init__("ResourceNotFoundException", "Resource not found.")
        body = {
            "ResourceId": resource_id,
            "Message": "Resource not found.",
        }
        self.description = json.dumps(body)


class ResourceInUse(JsonRESTError):
    def __init__(self, message: str):
        super().__init__("ResourceOwnerCheckException", message)
        body = {
            "Message": message,
        }
        self.description = json.dumps(body)


class InvalidRequest(JsonRESTError):
    def __init__(self, message: str):
        super().__init__("InvalidRequestException", message)
        body = {
            "Message": message,
        }
        self.description = json.dumps(body)
