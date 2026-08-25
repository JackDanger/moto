"""Exceptions raised by the signer service."""

from moto.core.exceptions import JsonRESTError


class SignerClientError(JsonRESTError):
    """Base class for Signer errors."""

    code = 400


class ResourceNotFoundException(SignerClientError):
    code = 404

    def __init__(self, message: str):
        super().__init__("ResourceNotFoundException", message)
