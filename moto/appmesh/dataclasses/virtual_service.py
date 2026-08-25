from dataclasses import dataclass, field
from typing import Any, Optional

from moto.appmesh.dataclasses.shared import Metadata, Status
from moto.appmesh.utils.common import clean_dict


@dataclass
class VirtualServiceSpec:
    """Spec for a top-level VirtualService resource."""

    spec: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:  # type: ignore[misc]
        return self.spec


@dataclass
class VirtualServiceMetadata(Metadata):
    mesh_name: str = field(default="")
    virtual_service_name: str = field(default="")

    def __post_init__(self) -> None:
        if self.mesh_name == "":
            raise TypeError("__init__ missing 1 required argument: 'mesh_name'")
        if self.virtual_service_name == "":
            raise TypeError(
                "__init__ missing 1 required argument: 'virtual_service_name'"
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
            "virtualServiceName": self.virtual_service_name,
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
class VirtualServiceResource:
    """Top-level VirtualService resource (not to be confused with the backend
    VirtualService type used inside VirtualNode specs)."""

    mesh_name: str
    mesh_owner: str
    metadata: VirtualServiceMetadata
    spec: VirtualServiceSpec
    virtual_service_name: str
    status: Status = field(default_factory=lambda: {"status": "ACTIVE"})
    tags: list[dict[str, str]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:  # type: ignore[misc]
        return clean_dict(
            {
                "meshName": self.mesh_name,
                "metadata": self.metadata.formatted_for_crud_apis(),
                "spec": self.spec.to_dict(),
                "status": self.status,
                "virtualServiceName": self.virtual_service_name,
            }
        )
