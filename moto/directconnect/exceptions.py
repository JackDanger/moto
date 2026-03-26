"""Exceptions raised by the directconnect service."""

from moto.core.exceptions import JsonRESTError


class DXConnectionError(JsonRESTError):
    code = 400


class DirectConnectClientError(DXConnectionError):
    def __init__(self, error_type: str, message: str) -> None:
        super().__init__(error_type, message)


class ConnectionIdMissing(DXConnectionError):
    def __init__(self) -> None:
        super().__init__("ConnectionIdMissing", "The connection ID is missing.")


class ConnectionNotFound(DXConnectionError):
    def __init__(self, connection_id: str, region: str) -> None:
        super().__init__(
            "ConnectionNotFound",
            f"{connection_id} does not match any connections in region {region}.",
        )


class LAGNotFound(DXConnectionError):
    def __init__(self, lag_id: str, region: str) -> None:
        super().__init__(
            "LagNotFound",
            f"{lag_id} does not match any LAGs in region {region}.",
        )


class MacSecKeyNotFound(DXConnectionError):
    def __init__(self, secret_arn: str, connection_id: str) -> None:
        super().__init__(
            "MacSecKeyNotFound",
            f"Secret ARN '{secret_arn}' not found for connection {connection_id}.",
        )


class VirtualInterfaceNotFound(DXConnectionError):
    def __init__(self, virtual_interface_id: str, region: str) -> None:
        super().__init__(
            "VirtualInterfaceNotFound",
            f"{virtual_interface_id} does not match any virtual interfaces in region {region}.",
        )


class InterconnectNotFound(DXConnectionError):
    def __init__(self, interconnect_id: str, region: str) -> None:
        super().__init__(
            "InterconnectNotFound",
            f"{interconnect_id} does not match any interconnects in region {region}.",
        )


class VirtualGatewayNotFound(DXConnectionError):
    def __init__(self, virtual_gateway_id: str, region: str) -> None:
        super().__init__(
            "VirtualGatewayNotFound",
            f"{virtual_gateway_id} does not match any virtual gateways in region {region}.",
        )
