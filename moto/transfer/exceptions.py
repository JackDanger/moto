"""Exceptions raised by the transfer service."""

from moto.core.exceptions import JsonRESTError


class TransferError(JsonRESTError):
    code = 400


class ServerNotFound(TransferError):
    def __init__(self, server_id: str) -> None:
        super().__init__(
            "ServerNotFound",
            f"There are no transfer protocol-enabled servers with ID {server_id}.",
        )


class UserNotFound(TransferError):
    def __init__(self, user_name: str, server_id: str) -> None:
        super().__init__(
            "UserNotFound",
            f"{user_name} does not match any user associated with server {server_id}.",
        )


class PublicKeyNotFound(TransferError):
    def __init__(self, user_name: str, server_id: str, ssh_public_key_id: str) -> None:
        super().__init__(
            "PublicKeyNotFound",
            f"{ssh_public_key_id} does not match any keys associated with user {user_name} for server {server_id}.",
        )


class ResourceNotFound(TransferError):
    code = 404

    def __init__(self, resource_type: str, resource_id: str) -> None:
        super().__init__(
            "ResourceNotFoundException",
            f"{resource_type} not found: {resource_id}",
        )


class AccessNotFound(TransferError):
    def __init__(self, server_id: str, external_id: str) -> None:
        super().__init__(
            "ResourceNotFoundException",
            f"Access for ExternalId {external_id} and ServerId {server_id} does not exist.",
        )


class InvalidRequestError(TransferError):
    def __init__(self, message: str) -> None:
        super().__init__(
            "InvalidRequestException",
            message,

class ConnectorNotFound(TransferError):
    def __init__(self, connector_id: str) -> None:
        super().__init__(
            "ResourceNotFoundException",
            f"Connector {connector_id} does not exist.",

        )
