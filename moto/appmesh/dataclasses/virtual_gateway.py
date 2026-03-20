from dataclasses import dataclass, field
from typing import Any

from moto.appmesh.dataclasses.shared import Metadata, Status
from moto.appmesh.utils.common import clean_dict


@dataclass
class VirtualGatewaySpec:
    """Opaque spec stored as raw dict for maximum flexibility."""

    spec: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:  # type: ignore[misc]
        return self.spec


@dataclass
class GatewayRouteSpec:
    """Opaque spec stored as raw dict."""

    spec: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:  # type: ignore[misc]
        return self.spec


@dataclass
class VirtualGatewayMetadata(Metadata):
    mesh_name: str = field(default="")
    virtual_gateway_name: str = field(default="")

    def __post_init__(self) -> None:
        if self.mesh_name == "":
            raise TypeError("__init__ missing 1 required argument: 'mesh_name'")
        if self.virtual_gateway_name == "":
            raise TypeError(
                "__init__ missing 1 required argument: 'virtual_gateway_name'"
            )

    def formatted_for_list_api(self) -> dict[str, Any]:  # type: ignore
        return {
            "arn": self.arn,
            "createdAt": self.created_at.strftime("%d/%m/%Y, %H:%M:%S"),
            "lastUpdatedAt": self.last_updated_at.strftime("%d/%m/%Y, %H:%M:%S"),
            "meshName": self.mesh_name,
            "meshOwner": self.mesh_owner,
            "resourceOwner": self.resource_owner,
            "version": self.version,
            "virtualGatewayName": self.virtual_gateway_name,
        }

    def formatted_for_crud_apis(self) -> dict[str, Any]:  # type: ignore
        return {
            "arn": self.arn,
            "createdAt": self.created_at.strftime("%d/%m/%Y, %H:%M:%S"),
            "lastUpdatedAt": self.last_updated_at.strftime("%d/%m/%Y, %H:%M:%S"),
            "meshOwner": self.mesh_owner,
            "resourceOwner": self.resource_owner,
            "uid": self.uid,
            "version": self.version,
        }


@dataclass
class GatewayRouteMetadata(Metadata):
    mesh_name: str = field(default="")
    virtual_gateway_name: str = field(default="")
    gateway_route_name: str = field(default="")

    def __post_init__(self) -> None:
        if self.mesh_name == "":
            raise TypeError("__init__ missing 1 required argument: 'mesh_name'")
        if self.virtual_gateway_name == "":
            raise TypeError(
                "__init__ missing 1 required argument: 'virtual_gateway_name'"
            )
        if self.gateway_route_name == "":
            raise TypeError(
                "__init__ missing 1 required argument: 'gateway_route_name'"
            )

    def formatted_for_list_api(self) -> dict[str, Any]:  # type: ignore
        return {
            "arn": self.arn,
            "createdAt": self.created_at.strftime("%d/%m/%Y, %H:%M:%S"),
            "gatewayRouteName": self.gateway_route_name,
            "lastUpdatedAt": self.last_updated_at.strftime("%d/%m/%Y, %H:%M:%S"),
            "meshName": self.mesh_name,
            "meshOwner": self.mesh_owner,
            "resourceOwner": self.resource_owner,
            "version": self.version,
            "virtualGatewayName": self.virtual_gateway_name,
        }

    def formatted_for_crud_apis(self) -> dict[str, Any]:  # type: ignore
        return {
            "arn": self.arn,
            "createdAt": self.created_at.strftime("%d/%m/%Y, %H:%M:%S"),
            "lastUpdatedAt": self.last_updated_at.strftime("%d/%m/%Y, %H:%M:%S"),
            "meshOwner": self.mesh_owner,
            "resourceOwner": self.resource_owner,
            "uid": self.uid,
            "version": self.version,
        }


@dataclass
class GatewayRoute:
    mesh_name: str
    mesh_owner: str
    metadata: GatewayRouteMetadata
    gateway_route_name: str
    spec: GatewayRouteSpec
    virtual_gateway_name: str
    status: Status = field(default_factory=lambda: {"status": "ACTIVE"})
    tags: list[dict[str, str]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:  # type: ignore[misc]
        return clean_dict(
            {
                "gatewayRouteName": self.gateway_route_name,
                "meshName": self.mesh_name,
                "metadata": self.metadata.formatted_for_crud_apis(),
                "spec": self.spec.to_dict(),
                "status": self.status,
                "virtualGatewayName": self.virtual_gateway_name,
            }
        )


@dataclass
class VirtualGateway:
    mesh_name: str
    mesh_owner: str
    metadata: VirtualGatewayMetadata
    spec: VirtualGatewaySpec
    virtual_gateway_name: str
    gateway_routes: dict[str, GatewayRoute] = field(default_factory=dict)
    status: Status = field(default_factory=lambda: {"status": "ACTIVE"})
    tags: list[dict[str, str]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:  # type: ignore[misc]
        return clean_dict(
            {
                "meshName": self.mesh_name,
                "metadata": self.metadata.formatted_for_crud_apis(),
                "spec": self.spec.to_dict(),
                "status": self.status,
                "virtualGatewayName": self.virtual_gateway_name,
            }
        )
