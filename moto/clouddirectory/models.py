"""CloudDirectoryBackend class with methods for supported APIs."""

import copy
import datetime
import json
import uuid

from moto.core.base_backend import BackendDict, BaseBackend
from moto.core.common_models import BaseModel
from moto.utilities.paginator import paginate
from moto.utilities.tagging_service import TaggingService

from .exceptions import (
    InvalidArnException,
    ResourceNotFoundException,
    SchemaAlreadyPublishedException,
)

PAGINATION_MODEL = {
    "list_directories": {
        "input_token": "next_token",
        "limit_key": "max_results",
        "limit_default": 100,
        "unique_attribute": "directory_arn",
    },
    "list_development_schema_arns": {
        "input_token": "next_token",
        "limit_key": "max_results",
        "limit_default": 100,
        "unique_attribute": "schema_arn",
    },
    "list_published_schema_arns": {
        "input_token": "next_token",
        "limit_key": "max_results",
        "limit_default": 100,
        "unique_attribute": "schema_arn",
    },
    "list_applied_schema_arns": {
        "input_token": "next_token",
        "limit_key": "max_results",
        "limit_default": 100,
        "unique_attribute": "schema_arn",
    },
    "list_facet_names": {
        "input_token": "next_token",
        "limit_key": "max_results",
        "limit_default": 100,
        "unique_attribute": "name",
    },
    "list_facet_attributes": {
        "input_token": "next_token",
        "limit_key": "max_results",
        "limit_default": 100,
        "unique_attribute": "name",
    },
    "list_typed_link_facet_names": {
        "input_token": "next_token",
        "limit_key": "max_results",
        "limit_default": 100,
        "unique_attribute": "name",
    },
    "list_typed_link_facet_attributes": {
        "input_token": "next_token",
        "limit_key": "max_results",
        "limit_default": 100,
        "unique_attribute": "name",
    },
    "list_managed_schema_arns": {
        "input_token": "next_token",
        "limit_key": "max_results",
        "limit_default": 100,
        "unique_attribute": "schema_arn",
    },
    "list_object_attributes": {
        "input_token": "next_token",
        "limit_key": "max_results",
        "limit_default": 100,
        "unique_attribute": "key",
    },
    "list_object_children": {
        "input_token": "next_token",
        "limit_key": "max_results",
        "limit_default": 100,
        "unique_attribute": "link_name",
    },
    "list_object_parent_paths": {
        "input_token": "next_token",
        "limit_key": "max_results",
        "limit_default": 100,
        "unique_attribute": "path",
    },
    "list_object_parents": {
        "input_token": "next_token",
        "limit_key": "max_results",
        "limit_default": 100,
        "unique_attribute": "object_identifier",
    },
    "list_object_policies": {
        "input_token": "next_token",
        "limit_key": "max_results",
        "limit_default": 100,
        "unique_attribute": "policy_id",
    },
    "list_policy_attachments": {
        "input_token": "next_token",
        "limit_key": "max_results",
        "limit_default": 100,
        "unique_attribute": "object_identifier",
    },
    "list_index": {
        "input_token": "next_token",
        "limit_key": "max_results",
        "limit_default": 100,
        "unique_attribute": "object_identifier",
    },
    "list_incoming_typed_links": {
        "input_token": "next_token",
        "limit_key": "max_results",
        "limit_default": 100,
        "unique_attribute": "source_object_reference",
    },
    "list_outgoing_typed_links": {
        "input_token": "next_token",
        "limit_key": "max_results",
        "limit_default": 100,
        "unique_attribute": "target_object_reference",
    },
    "list_attached_indices": {
        "input_token": "next_token",
        "limit_key": "max_results",
        "limit_default": 100,
        "unique_attribute": "index_object_identifier",
    },
}


class Directory(BaseModel):
    def __init__(
        self, account_id: str, region: str, name: str, schema_arn: str
    ) -> None:
        self.name = name
        self.schema_arn = schema_arn
        self.directory_arn = (
            f"arn:aws:clouddirectory:{region}:{account_id}:directory/{name}"
        )
        self.state = "ENABLED"
        self.creation_date_time = datetime.datetime.now()
        self.object_identifier = f"directory-{name}"
        # Applied schemas for this directory
        self.applied_schemas: list[str] = []
        # Objects in this directory: object_identifier -> DirectoryObject
        self.objects: dict[str, "DirectoryObject"] = {}
        # Root object
        root_id = str(uuid.uuid4()).replace("-", "")
        self.root_object_id = root_id
        root_obj = DirectoryObject(object_identifier=root_id, schema_facets=[])
        self.objects[root_id] = root_obj
        # Parent->child relationships: parent_id -> {link_name: child_id}
        self.children: dict[str, dict[str, str]] = {}
        # Child->parent relationships: child_id -> {parent_id: link_name}
        self.parents: dict[str, dict[str, str]] = {}
        # Policy attachments: policy_object_id -> [target_object_id, ...]
        self.policy_attachments: dict[str, list[str]] = {}
        # Object->policy: object_id -> [policy_id, ...]
        self.object_policies: dict[str, list[str]] = {}
        # Index objects: index_object_id -> IndexInfo
        self.indices: dict[str, "IndexInfo"] = {}
        # Object->attached indices: object_id -> [index_object_id, ...]
        self.object_indices: dict[str, list[str]] = {}
        # Typed link instances
        self.typed_links: list["TypedLinkInstance"] = []

    def to_dict(self) -> dict[str, str]:
        return {
            "Name": self.name,
            "SchemaArn": self.schema_arn,
            "DirectoryArn": self.directory_arn,
            "State": self.state,
            "CreationDateTime": str(self.creation_date_time),
            "ObjectIdentifier": self.object_identifier,
        }

    def resolve_object_reference(self, object_reference: dict) -> str:
        """Resolve an ObjectReference to an object_identifier."""
        selector = object_reference.get("Selector")
        if not selector:
            raise ResourceNotFoundException("ObjectReference must have a Selector")
        if selector.startswith("$"):
            obj_id = selector[1:]
            if obj_id not in self.objects:
                raise ResourceNotFoundException(obj_id)
            return obj_id
        if selector == "/":
            return self.root_object_id
        parts = selector.strip("/").split("/")
        current = self.root_object_id
        for part in parts:
            children = self.children.get(current, {})
            if part not in children:
                raise ResourceNotFoundException(selector)
            current = children[part]
        return current


class DirectoryObject(BaseModel):
    def __init__(
        self,
        object_identifier: str,
        schema_facets: list[dict],
        attributes: list[dict] | None = None,
    ) -> None:
        self.object_identifier = object_identifier
        self.schema_facets = schema_facets
        self.attributes: list[dict] = attributes or []


class Facet(BaseModel):
    def __init__(
        self,
        name: str,
        attributes: list[dict] | None = None,
        object_type: str = "NODE",
        facet_style: str | None = None,
    ) -> None:
        self.name = name
        self.attributes: list[dict] = attributes or []
        self.object_type = object_type
        self.facet_style = facet_style or "STATIC"

    def to_dict(self) -> dict:
        return {
            "Name": self.name,
            "ObjectType": self.object_type,
            "FacetStyle": self.facet_style,
        }


class TypedLinkFacet(BaseModel):
    def __init__(
        self,
        name: str,
        attributes: list[dict],
        identity_attribute_order: list[str],
    ) -> None:
        self.name = name
        self.attributes: list[dict] = attributes
        self.identity_attribute_order = identity_attribute_order


class TypedLinkInstance(BaseModel):
    def __init__(
        self,
        source_object_id: str,
        target_object_id: str,
        typed_link_facet: dict,
        attributes: list[dict],
    ) -> None:
        self.source_object_id = source_object_id
        self.target_object_id = target_object_id
        self.typed_link_facet = typed_link_facet
        self.attributes = attributes

    def to_specifier(self, directory: Directory) -> dict:
        return {
            "TypedLinkFacet": self.typed_link_facet,
            "SourceObjectReference": {"Selector": f"${self.source_object_id}"},
            "TargetObjectReference": {"Selector": f"${self.target_object_id}"},
            "IdentityAttributeValues": self.attributes,
        }


class IndexInfo(BaseModel):
    def __init__(
        self,
        object_identifier: str,
        ordered_indexed_attribute_list: list[dict],
        is_unique: bool,
    ) -> None:
        self.object_identifier = object_identifier
        self.ordered_indexed_attribute_list = ordered_indexed_attribute_list
        self.is_unique = is_unique
        self.attached_objects: list[str] = []


class SchemaInfo(BaseModel):
    """Stores schema data including facets and typed link facets."""

    def __init__(self, schema_arn: str) -> None:
        self.schema_arn = schema_arn
        self.facets: dict[str, Facet] = {}
        self.typed_link_facets: dict[str, TypedLinkFacet] = {}
        self.document: str = "{}"
        self.name: str = schema_arn.split("/")[-1] if "/" in schema_arn else ""


class CloudDirectoryBackend(BaseBackend):
    """Implementation of CloudDirectory APIs."""

    def __init__(self, region_name: str, account_id: str) -> None:
        super().__init__(region_name, account_id)
        self.directories: dict[str, Directory] = {}
        self.schemas_states: dict[str, list[str]] = {
            "development": [],
            "published": [],
            "applied": [],
        }
        self.schema_data: dict[str, SchemaInfo] = {}
        self.tagger = TaggingService()

    def _get_schema_info(self, schema_arn: str) -> SchemaInfo:
        if schema_arn not in self.schema_data:
            self.schema_data[schema_arn] = SchemaInfo(schema_arn)
        return self.schema_data[schema_arn]

    def _get_directory(self, directory_arn: str) -> Directory:
        directory = self.directories.get(directory_arn)
        if not directory:
            raise ResourceNotFoundException(directory_arn)
        return directory

    def _find_schema_arn(self, schema_arn: str) -> str:
        for state in ("development", "published", "applied"):
            if schema_arn in self.schemas_states[state]:
                return schema_arn
        raise ResourceNotFoundException(schema_arn)

    def apply_schema(self, directory_arn: str, published_schema_arn: str) -> None:
        directory = self.directories.get(directory_arn)
        if not directory:
            raise ResourceNotFoundException(directory_arn)
        if published_schema_arn not in self.schemas_states["published"]:
            raise ResourceNotFoundException(published_schema_arn)
        directory.schema_arn = published_schema_arn
        applied_arn = published_schema_arn.replace("/published/", "/applied/")
        if applied_arn not in self.schemas_states["applied"]:
            self.schemas_states["applied"].append(applied_arn)
        if applied_arn not in directory.applied_schemas:
            directory.applied_schemas.append(applied_arn)
        if published_schema_arn in self.schema_data:
            self.schema_data[applied_arn] = copy.deepcopy(
                self.schema_data[published_schema_arn]
            )
            self.schema_data[applied_arn].schema_arn = applied_arn
        return

    def publish_schema(
        self, name: str, version: str, development_schema_arn: str, minor_version: str
    ) -> str:
        schema_arn = f"arn:aws:clouddirectory:{self.region_name}:{self.account_id}:schema/published/{name}/{version}/{minor_version}"
        if development_schema_arn in self.schemas_states["published"]:
            raise SchemaAlreadyPublishedException(development_schema_arn)
        if development_schema_arn in self.schemas_states["development"]:
            self.schemas_states["development"].remove(development_schema_arn)
            self.schemas_states["published"].append(schema_arn)
        else:
            raise ResourceNotFoundException(development_schema_arn)
        if development_schema_arn in self.schema_data:
            self.schema_data[schema_arn] = copy.deepcopy(
                self.schema_data[development_schema_arn]
            )
            self.schema_data[schema_arn].schema_arn = schema_arn
        return schema_arn

    def create_directory(self, name: str, schema_arn: str) -> Directory:
        directory = Directory(self.account_id, self.region_name, name, schema_arn)
        self.directories[directory.directory_arn] = directory
        return directory

    def create_schema(self, name: str) -> str:
        self.schema_arn = f"arn:aws:clouddirectory:{self.region_name}:{self.account_id}:schema/development/{name}"
        self.schemas_states["development"].append(self.schema_arn)
        self._get_schema_info(self.schema_arn).name = name
        return self.schema_arn

    def delete_schema(self, schema_arn: str) -> None:
        if schema_arn in self.schemas_states["development"]:
            self.schemas_states["development"].remove(schema_arn)
        elif schema_arn in self.schemas_states["published"]:
            self.schemas_states["published"].remove(schema_arn)
        else:
            raise ResourceNotFoundException(schema_arn)
        self.schema_data.pop(schema_arn, None)
        return

    @paginate(pagination_model=PAGINATION_MODEL)
    def list_development_schema_arns(self) -> list[str]:
        return self.schemas_states["development"]

    @paginate(pagination_model=PAGINATION_MODEL)
    def list_published_schema_arns(self) -> list[str]:
        return self.schemas_states["published"]

    @paginate(pagination_model=PAGINATION_MODEL)
    def list_directories(self, state: str) -> list[Directory]:
        directories = list(self.directories.values())
        if state:
            directories = [
                directory for directory in directories if directory.state == state
            ]
        return directories

    def tag_resource(self, resource_arn: str, tags: list[dict[str, str]]) -> None:
        self.tagger.tag_resource(resource_arn, tags)
        return

    def untag_resource(self, resource_arn: str, tag_keys: list[str]) -> None:
        if not isinstance(tag_keys, list):
            tag_keys = [tag_keys]
        self.tagger.untag_resource_using_names(resource_arn, tag_keys)
        return

    def delete_directory(self, directory_arn: str) -> str:
        directory = self.directories.pop(directory_arn)
        return directory.directory_arn

    def get_directory(self, directory_arn: str) -> Directory:
        directory = self.directories.get(directory_arn)
        if not directory:
            raise InvalidArnException(directory_arn)
        return directory

    def list_tags_for_resource(
        self, resource_arn: str, next_token: str, max_results: int
    ) -> list[dict[str, str]]:
        tags = self.tagger.list_tags_for_resource(resource_arn)["Tags"]
        return tags

    # --- Facet operations ---

    def create_facet(
        self,
        schema_arn: str,
        name: str,
        attributes: list[dict] | None,
        object_type: str,
        facet_style: str | None,
    ) -> None:
        self._find_schema_arn(schema_arn)
        schema_info = self._get_schema_info(schema_arn)
        facet = Facet(
            name=name,
            attributes=attributes,
            object_type=object_type or "NODE",
            facet_style=facet_style,
        )
        schema_info.facets[name] = facet

    def delete_facet(self, schema_arn: str, name: str) -> None:
        self._find_schema_arn(schema_arn)
        schema_info = self._get_schema_info(schema_arn)
        if name not in schema_info.facets:
            raise ResourceNotFoundException(name)
        del schema_info.facets[name]

    def get_facet(self, schema_arn: str, name: str) -> Facet:
        self._find_schema_arn(schema_arn)
        schema_info = self._get_schema_info(schema_arn)
        if name not in schema_info.facets:
            raise ResourceNotFoundException(name)
        return schema_info.facets[name]

    def update_facet(
        self,
        schema_arn: str,
        name: str,
        attribute_updates: list[dict] | None,
        object_type: str | None,
    ) -> None:
        self._find_schema_arn(schema_arn)
        schema_info = self._get_schema_info(schema_arn)
        if name not in schema_info.facets:
            raise ResourceNotFoundException(name)
        facet = schema_info.facets[name]
        if object_type:
            facet.object_type = object_type
        if attribute_updates:
            for update in attribute_updates:
                action = update.get("Action", "CREATE_OR_UPDATE")
                attr = update.get("Attribute", {})
                attr_name = attr.get("Name")
                if action == "DELETE" and attr_name:
                    facet.attributes = [
                        a for a in facet.attributes if a.get("Name") != attr_name
                    ]
                else:
                    facet.attributes = [
                        a for a in facet.attributes if a.get("Name") != attr_name
                    ]
                    facet.attributes.append(attr)

    @paginate(pagination_model=PAGINATION_MODEL)
    def list_facet_names(self, schema_arn: str) -> list[str]:
        self._find_schema_arn(schema_arn)
        schema_info = self._get_schema_info(schema_arn)
        return list(schema_info.facets.keys())

    @paginate(pagination_model=PAGINATION_MODEL)
    def list_facet_attributes(self, schema_arn: str, name: str) -> list[dict]:
        self._find_schema_arn(schema_arn)
        schema_info = self._get_schema_info(schema_arn)
        if name not in schema_info.facets:
            raise ResourceNotFoundException(name)
        return schema_info.facets[name].attributes

    # --- TypedLink Facet operations ---

    def create_typed_link_facet(self, schema_arn: str, facet: dict) -> None:
        self._find_schema_arn(schema_arn)
        schema_info = self._get_schema_info(schema_arn)
        name = facet.get("Name", "")
        attributes = facet.get("Attributes", [])
        identity_attribute_order = facet.get("IdentityAttributeOrder", [])
        tl_facet = TypedLinkFacet(
            name=name,
            attributes=attributes,
            identity_attribute_order=identity_attribute_order,
        )
        schema_info.typed_link_facets[name] = tl_facet

    def delete_typed_link_facet(self, schema_arn: str, name: str) -> None:
        self._find_schema_arn(schema_arn)
        schema_info = self._get_schema_info(schema_arn)
        if name not in schema_info.typed_link_facets:
            raise ResourceNotFoundException(name)
        del schema_info.typed_link_facets[name]

    def get_typed_link_facet_information(
        self, schema_arn: str, name: str
    ) -> list[str]:
        self._find_schema_arn(schema_arn)
        schema_info = self._get_schema_info(schema_arn)
        if name not in schema_info.typed_link_facets:
            raise ResourceNotFoundException(name)
        return schema_info.typed_link_facets[name].identity_attribute_order

    def update_typed_link_facet(
        self,
        schema_arn: str,
        name: str,
        attribute_updates: list[dict],
        identity_attribute_order: list[str],
    ) -> None:
        self._find_schema_arn(schema_arn)
        schema_info = self._get_schema_info(schema_arn)
        if name not in schema_info.typed_link_facets:
            raise ResourceNotFoundException(name)
        tl_facet = schema_info.typed_link_facets[name]
        tl_facet.identity_attribute_order = identity_attribute_order
        if attribute_updates:
            for update in attribute_updates:
                action = update.get("Action", "CREATE_OR_UPDATE")
                attr = update.get("Attribute", {})
                attr_name = attr.get("Name")
                if action == "DELETE" and attr_name:
                    tl_facet.attributes = [
                        a for a in tl_facet.attributes if a.get("Name") != attr_name
                    ]
                else:
                    tl_facet.attributes = [
                        a for a in tl_facet.attributes if a.get("Name") != attr_name
                    ]
                    tl_facet.attributes.append(attr)

    @paginate(pagination_model=PAGINATION_MODEL)
    def list_typed_link_facet_names(self, schema_arn: str) -> list[str]:
        self._find_schema_arn(schema_arn)
        schema_info = self._get_schema_info(schema_arn)
        return list(schema_info.typed_link_facets.keys())

    @paginate(pagination_model=PAGINATION_MODEL)
    def list_typed_link_facet_attributes(
        self, schema_arn: str, name: str
    ) -> list[dict]:
        self._find_schema_arn(schema_arn)
        schema_info = self._get_schema_info(schema_arn)
        if name not in schema_info.typed_link_facets:
            raise ResourceNotFoundException(name)
        return schema_info.typed_link_facets[name].attributes

    # --- Object operations ---

    def create_object(
        self,
        directory_arn: str,
        schema_facets: list[dict],
        object_attribute_list: list[dict] | None,
        parent_reference: dict | None,
        link_name: str | None,
    ) -> str:
        directory = self._get_directory(directory_arn)
        obj_id = str(uuid.uuid4()).replace("-", "")
        obj = DirectoryObject(
            object_identifier=obj_id,
            schema_facets=schema_facets,
            attributes=object_attribute_list,
        )
        directory.objects[obj_id] = obj
        if parent_reference and link_name:
            parent_id = directory.resolve_object_reference(parent_reference)
            if parent_id not in directory.children:
                directory.children[parent_id] = {}
            directory.children[parent_id][link_name] = obj_id
            if obj_id not in directory.parents:
                directory.parents[obj_id] = {}
            directory.parents[obj_id][parent_id] = link_name
        return obj_id

    def delete_object(self, directory_arn: str, object_reference: dict) -> None:
        directory = self._get_directory(directory_arn)
        obj_id = directory.resolve_object_reference(object_reference)
        if obj_id in directory.parents:
            for parent_id, link_name in directory.parents[obj_id].items():
                if parent_id in directory.children:
                    directory.children[parent_id].pop(link_name, None)
            del directory.parents[obj_id]
        directory.children.pop(obj_id, None)
        directory.objects.pop(obj_id, None)

    def get_object_information(
        self, directory_arn: str, object_reference: dict
    ) -> DirectoryObject:
        directory = self._get_directory(directory_arn)
        obj_id = directory.resolve_object_reference(object_reference)
        return directory.objects[obj_id]

    def get_object_attributes(
        self,
        directory_arn: str,
        object_reference: dict,
        schema_facet: dict,
        attribute_names: list[str],
    ) -> list[dict]:
        directory = self._get_directory(directory_arn)
        obj_id = directory.resolve_object_reference(object_reference)
        obj = directory.objects[obj_id]
        result = []
        for attr in obj.attributes:
            key = attr.get("Key", {})
            if key.get("Name") in attribute_names:
                result.append(attr)
        return result

    def update_object_attributes(
        self,
        directory_arn: str,
        object_reference: dict,
        attribute_updates: list[dict],
    ) -> str:
        directory = self._get_directory(directory_arn)
        obj_id = directory.resolve_object_reference(object_reference)
        obj = directory.objects[obj_id]
        for update in attribute_updates:
            action = update.get("ObjectAttributeAction", {})
            attr_key = update.get("ObjectAttributeKey", {})
            action_type = action.get("ObjectAttributeActionType", "CREATE_OR_UPDATE")
            attr_name = attr_key.get("Name")
            if action_type == "DELETE" and attr_name:
                obj.attributes = [
                    a
                    for a in obj.attributes
                    if a.get("Key", {}).get("Name") != attr_name
                ]
            else:
                obj.attributes = [
                    a
                    for a in obj.attributes
                    if a.get("Key", {}).get("Name") != attr_name
                ]
                new_attr = {
                    "Key": attr_key,
                    "Value": action.get("ObjectAttributeUpdateValue", {}),
                }
                obj.attributes.append(new_attr)
        return obj_id

    def add_facet_to_object(
        self,
        directory_arn: str,
        schema_facet: dict,
        object_attribute_list: list[dict] | None,
        object_reference: dict,
    ) -> None:
        directory = self._get_directory(directory_arn)
        obj_id = directory.resolve_object_reference(object_reference)
        obj = directory.objects[obj_id]
        obj.schema_facets.append(schema_facet)
        if object_attribute_list:
            obj.attributes.extend(object_attribute_list)

    def remove_facet_from_object(
        self,
        directory_arn: str,
        schema_facet: dict,
        object_reference: dict,
    ) -> None:
        directory = self._get_directory(directory_arn)
        obj_id = directory.resolve_object_reference(object_reference)
        obj = directory.objects[obj_id]
        facet_name = schema_facet.get("FacetName")
        schema_arn = schema_facet.get("SchemaArn")
        obj.schema_facets = [
            sf
            for sf in obj.schema_facets
            if not (
                sf.get("FacetName") == facet_name
                and sf.get("SchemaArn") == schema_arn
            )
        ]

    @paginate(pagination_model=PAGINATION_MODEL)
    def list_object_attributes(
        self, directory_arn: str, object_reference: dict
    ) -> list[dict]:
        directory = self._get_directory(directory_arn)
        obj_id = directory.resolve_object_reference(object_reference)
        return directory.objects[obj_id].attributes

    @paginate(pagination_model=PAGINATION_MODEL)
    def list_object_children(
        self, directory_arn: str, object_reference: dict
    ) -> list[tuple[str, str]]:
        directory = self._get_directory(directory_arn)
        obj_id = directory.resolve_object_reference(object_reference)
        children = directory.children.get(obj_id, {})
        return list(children.items())

    @paginate(pagination_model=PAGINATION_MODEL)
    def list_object_parents(
        self, directory_arn: str, object_reference: dict
    ) -> list[tuple[str, str]]:
        directory = self._get_directory(directory_arn)
        obj_id = directory.resolve_object_reference(object_reference)
        parents = directory.parents.get(obj_id, {})
        return list(parents.items())

    @paginate(pagination_model=PAGINATION_MODEL)
    def list_object_parent_paths(
        self, directory_arn: str, object_reference: dict
    ) -> list[dict]:
        directory = self._get_directory(directory_arn)
        obj_id = directory.resolve_object_reference(object_reference)
        paths: list[dict] = []
        self._collect_paths(directory, obj_id, [], paths)
        return paths

    def _collect_paths(
        self,
        directory: Directory,
        obj_id: str,
        current_path: list[str],
        result: list[dict],
    ) -> None:
        parents = directory.parents.get(obj_id, {})
        if not parents:
            path_str = "/" + "/".join(reversed(current_path))
            result.append({"Path": path_str, "ObjectIdentifiers": [obj_id]})
            return
        for parent_id, link_name in parents.items():
            self._collect_paths(
                directory, parent_id, current_path + [link_name], result
            )

    @paginate(pagination_model=PAGINATION_MODEL)
    def list_object_policies(
        self, directory_arn: str, object_reference: dict
    ) -> list[str]:
        directory = self._get_directory(directory_arn)
        obj_id = directory.resolve_object_reference(object_reference)
        return directory.object_policies.get(obj_id, [])

    # --- Attach/Detach operations ---

    def attach_object(
        self,
        directory_arn: str,
        parent_reference: dict,
        child_reference: dict,
        link_name: str,
    ) -> str:
        directory = self._get_directory(directory_arn)
        parent_id = directory.resolve_object_reference(parent_reference)
        child_id = directory.resolve_object_reference(child_reference)
        if parent_id not in directory.children:
            directory.children[parent_id] = {}
        directory.children[parent_id][link_name] = child_id
        if child_id not in directory.parents:
            directory.parents[child_id] = {}
        directory.parents[child_id][parent_id] = link_name
        return child_id

    def detach_object(
        self, directory_arn: str, parent_reference: dict, link_name: str
    ) -> str:
        directory = self._get_directory(directory_arn)
        parent_id = directory.resolve_object_reference(parent_reference)
        children = directory.children.get(parent_id, {})
        child_id = children.pop(link_name, None)
        if child_id and child_id in directory.parents:
            directory.parents[child_id].pop(parent_id, None)
        return child_id or ""

    # --- Policy operations ---

    def attach_policy(
        self, directory_arn: str, policy_reference: dict, object_reference: dict
    ) -> None:
        directory = self._get_directory(directory_arn)
        policy_id = directory.resolve_object_reference(policy_reference)
        obj_id = directory.resolve_object_reference(object_reference)
        if policy_id not in directory.policy_attachments:
            directory.policy_attachments[policy_id] = []
        if obj_id not in directory.policy_attachments[policy_id]:
            directory.policy_attachments[policy_id].append(obj_id)
        if obj_id not in directory.object_policies:
            directory.object_policies[obj_id] = []
        if policy_id not in directory.object_policies[obj_id]:
            directory.object_policies[obj_id].append(policy_id)

    def detach_policy(
        self, directory_arn: str, policy_reference: dict, object_reference: dict
    ) -> None:
        directory = self._get_directory(directory_arn)
        policy_id = directory.resolve_object_reference(policy_reference)
        obj_id = directory.resolve_object_reference(object_reference)
        if policy_id in directory.policy_attachments:
            if obj_id in directory.policy_attachments[policy_id]:
                directory.policy_attachments[policy_id].remove(obj_id)
        if obj_id in directory.object_policies:
            if policy_id in directory.object_policies[obj_id]:
                directory.object_policies[obj_id].remove(policy_id)

    @paginate(pagination_model=PAGINATION_MODEL)
    def list_policy_attachments(
        self, directory_arn: str, policy_reference: dict
    ) -> list[str]:
        directory = self._get_directory(directory_arn)
        policy_id = directory.resolve_object_reference(policy_reference)
        return directory.policy_attachments.get(policy_id, [])

    def lookup_policy(
        self, directory_arn: str, object_reference: dict
    ) -> list[dict]:
        directory = self._get_directory(directory_arn)
        obj_id = directory.resolve_object_reference(object_reference)
        policies = directory.object_policies.get(obj_id, [])
        result = []
        for policy_id in policies:
            result.append({
                "PolicyId": policy_id,
                "PolicyType": "POLICY",
                "ObjectIdentifier": obj_id,
            })
        return result

    # --- Index operations ---

    def create_index(
        self,
        directory_arn: str,
        ordered_indexed_attribute_list: list[dict],
        is_unique: bool,
        parent_reference: dict | None,
        link_name: str | None,
    ) -> str:
        directory = self._get_directory(directory_arn)
        obj_id = str(uuid.uuid4()).replace("-", "")
        index_obj = DirectoryObject(object_identifier=obj_id, schema_facets=[])
        directory.objects[obj_id] = index_obj
        index_info = IndexInfo(
            object_identifier=obj_id,
            ordered_indexed_attribute_list=ordered_indexed_attribute_list,
            is_unique=is_unique,
        )
        directory.indices[obj_id] = index_info
        if parent_reference and link_name:
            parent_id = directory.resolve_object_reference(parent_reference)
            if parent_id not in directory.children:
                directory.children[parent_id] = {}
            directory.children[parent_id][link_name] = obj_id
            if obj_id not in directory.parents:
                directory.parents[obj_id] = {}
            directory.parents[obj_id][parent_id] = link_name
        return obj_id

    def attach_to_index(
        self, directory_arn: str, index_reference: dict, target_reference: dict
    ) -> str:
        directory = self._get_directory(directory_arn)
        index_id = directory.resolve_object_reference(index_reference)
        target_id = directory.resolve_object_reference(target_reference)
        if index_id not in directory.indices:
            raise ResourceNotFoundException(index_id)
        directory.indices[index_id].attached_objects.append(target_id)
        if target_id not in directory.object_indices:
            directory.object_indices[target_id] = []
        directory.object_indices[target_id].append(index_id)
        return target_id

    def detach_from_index(
        self, directory_arn: str, index_reference: dict, target_reference: dict
    ) -> str:
        directory = self._get_directory(directory_arn)
        index_id = directory.resolve_object_reference(index_reference)
        target_id = directory.resolve_object_reference(target_reference)
        if index_id in directory.indices:
            idx = directory.indices[index_id]
            if target_id in idx.attached_objects:
                idx.attached_objects.remove(target_id)
        if target_id in directory.object_indices:
            if index_id in directory.object_indices[target_id]:
                directory.object_indices[target_id].remove(index_id)
        return target_id

    @paginate(pagination_model=PAGINATION_MODEL)
    def list_index(
        self, directory_arn: str, index_reference: dict
    ) -> list[dict]:
        directory = self._get_directory(directory_arn)
        index_id = directory.resolve_object_reference(index_reference)
        if index_id not in directory.indices:
            raise ResourceNotFoundException(index_id)
        idx = directory.indices[index_id]
        result = []
        for obj_id in idx.attached_objects:
            result.append({
                "IndexedAttributes": idx.ordered_indexed_attribute_list,
                "ObjectIdentifier": obj_id,
            })
        return result

    @paginate(pagination_model=PAGINATION_MODEL)
    def list_attached_indices(
        self, directory_arn: str, target_reference: dict
    ) -> list[dict]:
        directory = self._get_directory(directory_arn)
        target_id = directory.resolve_object_reference(target_reference)
        index_ids = directory.object_indices.get(target_id, [])
        result = []
        for index_id in index_ids:
            if index_id in directory.indices:
                idx = directory.indices[index_id]
                result.append({
                    "IndexedAttributes": idx.ordered_indexed_attribute_list,
                    "ObjectIdentifier": index_id,
                })
        return result

    # --- TypedLink instance operations ---

    def attach_typed_link(
        self,
        directory_arn: str,
        source_object_reference: dict,
        target_object_reference: dict,
        typed_link_facet: dict,
        attributes: list[dict],
    ) -> dict:
        directory = self._get_directory(directory_arn)
        source_id = directory.resolve_object_reference(source_object_reference)
        target_id = directory.resolve_object_reference(target_object_reference)
        instance = TypedLinkInstance(
            source_object_id=source_id,
            target_object_id=target_id,
            typed_link_facet=typed_link_facet,
            attributes=attributes,
        )
        directory.typed_links.append(instance)
        return instance.to_specifier(directory)

    def detach_typed_link(
        self, directory_arn: str, typed_link_specifier: dict
    ) -> None:
        directory = self._get_directory(directory_arn)
        source_ref = typed_link_specifier.get("SourceObjectReference", {})
        target_ref = typed_link_specifier.get("TargetObjectReference", {})
        facet = typed_link_specifier.get("TypedLinkFacet", {})
        source_id = directory.resolve_object_reference(source_ref)
        target_id = directory.resolve_object_reference(target_ref)
        facet_name = facet.get("TypedLinkName", "")
        directory.typed_links = [
            tl
            for tl in directory.typed_links
            if not (
                tl.source_object_id == source_id
                and tl.target_object_id == target_id
                and tl.typed_link_facet.get("TypedLinkName") == facet_name
            )
        ]

    def get_link_attributes(
        self,
        directory_arn: str,
        typed_link_specifier: dict,
        attribute_names: list[str],
    ) -> list[dict]:
        directory = self._get_directory(directory_arn)
        source_ref = typed_link_specifier.get("SourceObjectReference", {})
        target_ref = typed_link_specifier.get("TargetObjectReference", {})
        facet = typed_link_specifier.get("TypedLinkFacet", {})
        source_id = directory.resolve_object_reference(source_ref)
        target_id = directory.resolve_object_reference(target_ref)
        facet_name = facet.get("TypedLinkName", "")
        for tl in directory.typed_links:
            if (
                tl.source_object_id == source_id
                and tl.target_object_id == target_id
                and tl.typed_link_facet.get("TypedLinkName") == facet_name
            ):
                if attribute_names:
                    return [
                        a
                        for a in tl.attributes
                        if a.get("AttributeName") in attribute_names
                    ]
                return tl.attributes
        return []

    def update_link_attributes(
        self,
        directory_arn: str,
        typed_link_specifier: dict,
        attribute_updates: list[dict],
    ) -> None:
        directory = self._get_directory(directory_arn)
        source_ref = typed_link_specifier.get("SourceObjectReference", {})
        target_ref = typed_link_specifier.get("TargetObjectReference", {})
        facet = typed_link_specifier.get("TypedLinkFacet", {})
        source_id = directory.resolve_object_reference(source_ref)
        target_id = directory.resolve_object_reference(target_ref)
        facet_name = facet.get("TypedLinkName", "")
        for tl in directory.typed_links:
            if (
                tl.source_object_id == source_id
                and tl.target_object_id == target_id
                and tl.typed_link_facet.get("TypedLinkName") == facet_name
            ):
                for update in attribute_updates:
                    action = update.get("AttributeAction", {})
                    attr_key = update.get("AttributeKey", {})
                    action_type = action.get(
                        "AttributeActionType", "CREATE_OR_UPDATE"
                    )
                    attr_name = attr_key.get("Name")
                    if action_type == "DELETE" and attr_name:
                        tl.attributes = [
                            a
                            for a in tl.attributes
                            if a.get("AttributeName") != attr_name
                        ]
                    else:
                        tl.attributes = [
                            a
                            for a in tl.attributes
                            if a.get("AttributeName") != attr_name
                        ]
                        tl.attributes.append({
                            "AttributeName": attr_name,
                            "Value": action.get("AttributeUpdateValue", {}),
                        })
                break

    @paginate(pagination_model=PAGINATION_MODEL)
    def list_incoming_typed_links(
        self, directory_arn: str, object_reference: dict
    ) -> list[dict]:
        directory = self._get_directory(directory_arn)
        obj_id = directory.resolve_object_reference(object_reference)
        result = []
        for tl in directory.typed_links:
            if tl.target_object_id == obj_id:
                result.append(tl.to_specifier(directory))
        return result

    @paginate(pagination_model=PAGINATION_MODEL)
    def list_outgoing_typed_links(
        self, directory_arn: str, object_reference: dict
    ) -> list[dict]:
        directory = self._get_directory(directory_arn)
        obj_id = directory.resolve_object_reference(object_reference)
        result = []
        for tl in directory.typed_links:
            if tl.source_object_id == obj_id:
                result.append(tl.to_specifier(directory))
        return result

    # --- Directory state operations ---

    def disable_directory(self, directory_arn: str) -> str:
        directory = self._get_directory(directory_arn)
        directory.state = "DISABLED"
        return directory_arn

    def enable_directory(self, directory_arn: str) -> str:
        directory = self._get_directory(directory_arn)
        directory.state = "ENABLED"
        return directory_arn

    # --- Schema operations ---

    @paginate(pagination_model=PAGINATION_MODEL)
    def list_applied_schema_arns(self, directory_arn: str) -> list[str]:
        directory = self._get_directory(directory_arn)
        return directory.applied_schemas

    def get_applied_schema_version(self, schema_arn: str) -> str:
        if schema_arn in self.schemas_states["applied"]:
            return schema_arn
        for arn in self.schemas_states["applied"]:
            if schema_arn in arn or arn.startswith(schema_arn.rsplit("/", 1)[0]):
                return arn
        raise ResourceNotFoundException(schema_arn)

    def get_schema_as_json(self, schema_arn: str) -> tuple[str, str]:
        self._find_schema_arn(schema_arn)
        schema_info = self._get_schema_info(schema_arn)
        return schema_info.name, schema_info.document

    def put_schema_from_json(self, schema_arn: str, document: str) -> str:
        self._find_schema_arn(schema_arn)
        schema_info = self._get_schema_info(schema_arn)
        schema_info.document = document
        try:
            doc = json.loads(document)
            if "facets" in doc:
                for fname, fdata in doc["facets"].items():
                    facet = Facet(
                        name=fname,
                        attributes=fdata.get("attributes", []),
                        object_type=fdata.get("objectType", "NODE"),
                        facet_style=fdata.get("facetStyle"),
                    )
                    schema_info.facets[fname] = facet
        except (json.JSONDecodeError, AttributeError):
            pass
        return schema_arn

    def update_schema(self, schema_arn: str, name: str) -> str:
        self._find_schema_arn(schema_arn)
        schema_info = self._get_schema_info(schema_arn)
        schema_info.name = name
        return schema_arn

    def upgrade_applied_schema(
        self,
        published_schema_arn: str,
        directory_arn: str,
        dry_run: bool,
    ) -> tuple[str, str]:
        directory = self._get_directory(directory_arn)
        if published_schema_arn not in self.schemas_states["published"]:
            raise ResourceNotFoundException(published_schema_arn)
        applied_arn = published_schema_arn.replace("/published/", "/applied/")
        if not dry_run:
            if applied_arn not in self.schemas_states["applied"]:
                self.schemas_states["applied"].append(applied_arn)
            if applied_arn not in directory.applied_schemas:
                directory.applied_schemas.append(applied_arn)
            if published_schema_arn in self.schema_data:
                self.schema_data[applied_arn] = copy.deepcopy(
                    self.schema_data[published_schema_arn]
                )
                self.schema_data[applied_arn].schema_arn = applied_arn
        return applied_arn, directory_arn

    def upgrade_published_schema(
        self,
        development_schema_arn: str,
        published_schema_arn: str,
        minor_version: str,
        dry_run: bool,
    ) -> str:
        if development_schema_arn not in self.schemas_states["development"]:
            raise ResourceNotFoundException(development_schema_arn)
        if published_schema_arn not in self.schemas_states["published"]:
            raise ResourceNotFoundException(published_schema_arn)
        if not dry_run and development_schema_arn in self.schema_data:
            self.schema_data[published_schema_arn] = copy.deepcopy(
                self.schema_data[development_schema_arn]
            )
            self.schema_data[published_schema_arn].schema_arn = published_schema_arn
        return published_schema_arn

    @paginate(pagination_model=PAGINATION_MODEL)
    def list_managed_schema_arns(self) -> list[str]:
        return []

    # --- Batch operations ---

    def batch_read(
        self, directory_arn: str, operations: list[dict]
    ) -> list[dict]:
        responses = []
        for op in operations:
            resp = self._execute_batch_read_op(directory_arn, op)
            responses.append(resp)
        return responses

    def _execute_batch_read_op(self, directory_arn: str, op: dict) -> dict:
        try:
            if "ListObjectAttributes" in op:
                params = op["ListObjectAttributes"]
                directory = self._get_directory(directory_arn)
                obj_id = directory.resolve_object_reference(
                    params["ObjectReference"]
                )
                attrs = directory.objects[obj_id].attributes
                return {
                    "SuccessfulResponse": {
                        "ListObjectAttributes": {"Attributes": attrs}
                    }
                }
            if "ListObjectChildren" in op:
                params = op["ListObjectChildren"]
                directory = self._get_directory(directory_arn)
                obj_id = directory.resolve_object_reference(
                    params["ObjectReference"]
                )
                children = directory.children.get(obj_id, {})
                return {
                    "SuccessfulResponse": {
                        "ListObjectChildren": {"Children": children}
                    }
                }
            if "GetObjectInformation" in op:
                params = op["GetObjectInformation"]
                obj = self.get_object_information(
                    directory_arn, params["ObjectReference"]
                )
                return {
                    "SuccessfulResponse": {
                        "GetObjectInformation": {
                            "SchemaFacets": obj.schema_facets,
                            "ObjectIdentifier": obj.object_identifier,
                        }
                    }
                }
            if "GetObjectAttributes" in op:
                params = op["GetObjectAttributes"]
                attrs = self.get_object_attributes(
                    directory_arn,
                    params["ObjectReference"],
                    params.get("SchemaFacet", {}),
                    params.get("AttributeNames", []),
                )
                return {
                    "SuccessfulResponse": {
                        "GetObjectAttributes": {"Attributes": attrs}
                    }
                }
            if "ListObjectParents" in op:
                params = op["ListObjectParents"]
                directory = self._get_directory(directory_arn)
                obj_id = directory.resolve_object_reference(
                    params["ObjectReference"]
                )
                parents = directory.parents.get(obj_id, {})
                return {
                    "SuccessfulResponse": {
                        "ListObjectParents": {"Parents": dict(parents)}
                    }
                }
            if "ListObjectPolicies" in op:
                params = op["ListObjectPolicies"]
                directory = self._get_directory(directory_arn)
                obj_id = directory.resolve_object_reference(
                    params["ObjectReference"]
                )
                policies = directory.object_policies.get(obj_id, [])
                return {
                    "SuccessfulResponse": {
                        "ListObjectPolicies": {"AttachedPolicyIds": policies}
                    }
                }
            if "ListIncomingTypedLinks" in op:
                params = op["ListIncomingTypedLinks"]
                directory = self._get_directory(directory_arn)
                obj_id = directory.resolve_object_reference(
                    params["ObjectReference"]
                )
                links = [
                    tl.to_specifier(directory)
                    for tl in directory.typed_links
                    if tl.target_object_id == obj_id
                ]
                return {
                    "SuccessfulResponse": {
                        "ListIncomingTypedLinks": {"LinkSpecifiers": links}
                    }
                }
            if "ListOutgoingTypedLinks" in op:
                params = op["ListOutgoingTypedLinks"]
                directory = self._get_directory(directory_arn)
                obj_id = directory.resolve_object_reference(
                    params["ObjectReference"]
                )
                links = [
                    tl.to_specifier(directory)
                    for tl in directory.typed_links
                    if tl.source_object_id == obj_id
                ]
                return {
                    "SuccessfulResponse": {
                        "ListOutgoingTypedLinks": {"TypedLinkSpecifiers": links}
                    }
                }
            if "ListIndex" in op:
                params = op["ListIndex"]
                directory = self._get_directory(directory_arn)
                index_id = directory.resolve_object_reference(
                    params["IndexReference"]
                )
                if index_id in directory.indices:
                    idx = directory.indices[index_id]
                    attachments = [
                        {
                            "IndexedAttributes": idx.ordered_indexed_attribute_list,
                            "ObjectIdentifier": oid,
                        }
                        for oid in idx.attached_objects
                    ]
                else:
                    attachments = []
                return {
                    "SuccessfulResponse": {
                        "ListIndex": {"IndexAttachments": attachments}
                    }
                }
            if "ListPolicyAttachments" in op:
                params = op["ListPolicyAttachments"]
                directory = self._get_directory(directory_arn)
                policy_id = directory.resolve_object_reference(
                    params["PolicyReference"]
                )
                obj_ids = directory.policy_attachments.get(policy_id, [])
                return {
                    "SuccessfulResponse": {
                        "ListPolicyAttachments": {"ObjectIdentifiers": obj_ids}
                    }
                }
            if "LookupPolicy" in op:
                params = op["LookupPolicy"]
                result = self.lookup_policy(
                    directory_arn, params["ObjectReference"]
                )
                return {
                    "SuccessfulResponse": {
                        "LookupPolicy": {"PolicyToPathList": result}
                    }
                }
            if "ListObjectParentPaths" in op:
                params = op["ListObjectParentPaths"]
                directory = self._get_directory(directory_arn)
                obj_id = directory.resolve_object_reference(
                    params["ObjectReference"]
                )
                paths: list[dict] = []
                self._collect_paths(directory, obj_id, [], paths)
                return {
                    "SuccessfulResponse": {
                        "ListObjectParentPaths": {
                            "PathToObjectIdentifiersList": paths
                        }
                    }
                }
            if "GetLinkAttributes" in op:
                params = op["GetLinkAttributes"]
                attrs = self.get_link_attributes(
                    directory_arn,
                    params["TypedLinkSpecifier"],
                    params.get("AttributeNames", []),
                )
                return {
                    "SuccessfulResponse": {
                        "GetLinkAttributes": {"Attributes": attrs}
                    }
                }
            if "ListAttachedIndices" in op:
                params = op["ListAttachedIndices"]
                directory = self._get_directory(directory_arn)
                target_id = directory.resolve_object_reference(
                    params["TargetReference"]
                )
                index_ids = directory.object_indices.get(target_id, [])
                attachments = []
                for idx_id in index_ids:
                    if idx_id in directory.indices:
                        idx = directory.indices[idx_id]
                        attachments.append({
                            "IndexedAttributes": idx.ordered_indexed_attribute_list,
                            "ObjectIdentifier": idx_id,
                        })
                return {
                    "SuccessfulResponse": {
                        "ListAttachedIndices": {"IndexAttachments": attachments}
                    }
                }
        except Exception as exc:
            return {
                "ExceptionResponse": {
                    "Type": type(exc).__name__,
                    "Message": str(exc),
                }
            }
        return {
            "ExceptionResponse": {
                "Type": "NotImplemented",
                "Message": "Batch read operation not supported",
            }
        }

    def batch_write(
        self, directory_arn: str, operations: list[dict]
    ) -> list[dict]:
        responses = []
        for op in operations:
            resp = self._execute_batch_write_op(directory_arn, op)
            responses.append(resp)
        return responses

    def _execute_batch_write_op(self, directory_arn: str, op: dict) -> dict:
        try:
            if "CreateObject" in op:
                params = op["CreateObject"]
                obj_id = self.create_object(
                    directory_arn,
                    params.get("SchemaFacet", []),
                    params.get("ObjectAttributeList"),
                    params.get("ParentReference"),
                    params.get("LinkName"),
                )
                return {
                    "SuccessfulResponse": {
                        "CreateObject": {"ObjectIdentifier": obj_id}
                    }
                }
            if "AttachObject" in op:
                params = op["AttachObject"]
                obj_id = self.attach_object(
                    directory_arn,
                    params["ParentReference"],
                    params["ChildReference"],
                    params["LinkName"],
                )
                return {
                    "SuccessfulResponse": {
                        "AttachObject": {"AttachedObjectIdentifier": obj_id}
                    }
                }
            if "DetachObject" in op:
                params = op["DetachObject"]
                obj_id = self.detach_object(
                    directory_arn,
                    params["ParentReference"],
                    params["LinkName"],
                )
                return {
                    "SuccessfulResponse": {
                        "DetachObject": {"DetachedObjectIdentifier": obj_id}
                    }
                }
            if "UpdateObjectAttributes" in op:
                params = op["UpdateObjectAttributes"]
                obj_id = self.update_object_attributes(
                    directory_arn,
                    params["ObjectReference"],
                    params.get("AttributeUpdates", []),
                )
                return {
                    "SuccessfulResponse": {
                        "UpdateObjectAttributes": {"ObjectIdentifier": obj_id}
                    }
                }
            if "DeleteObject" in op:
                params = op["DeleteObject"]
                self.delete_object(directory_arn, params["ObjectReference"])
                return {"SuccessfulResponse": {"DeleteObject": {}}}
            if "AddFacetToObject" in op:
                params = op["AddFacetToObject"]
                self.add_facet_to_object(
                    directory_arn,
                    params.get("SchemaFacet", {}),
                    params.get("ObjectAttributeList"),
                    params["ObjectReference"],
                )
                return {"SuccessfulResponse": {"AddFacetToObject": {}}}
            if "RemoveFacetFromObject" in op:
                params = op["RemoveFacetFromObject"]
                self.remove_facet_from_object(
                    directory_arn,
                    params.get("SchemaFacet", {}),
                    params["ObjectReference"],
                )
                return {"SuccessfulResponse": {"RemoveFacetFromObject": {}}}
            if "AttachPolicy" in op:
                params = op["AttachPolicy"]
                self.attach_policy(
                    directory_arn,
                    params["PolicyReference"],
                    params["ObjectReference"],
                )
                return {"SuccessfulResponse": {"AttachPolicy": {}}}
            if "DetachPolicy" in op:
                params = op["DetachPolicy"]
                self.detach_policy(
                    directory_arn,
                    params["PolicyReference"],
                    params["ObjectReference"],
                )
                return {"SuccessfulResponse": {"DetachPolicy": {}}}
            if "CreateIndex" in op:
                params = op["CreateIndex"]
                obj_id = self.create_index(
                    directory_arn,
                    params["OrderedIndexedAttributeList"],
                    params.get("IsUnique", False),
                    params.get("ParentReference"),
                    params.get("LinkName"),
                )
                return {
                    "SuccessfulResponse": {
                        "CreateIndex": {"ObjectIdentifier": obj_id}
                    }
                }
            if "AttachToIndex" in op:
                params = op["AttachToIndex"]
                obj_id = self.attach_to_index(
                    directory_arn,
                    params["IndexReference"],
                    params["TargetReference"],
                )
                return {
                    "SuccessfulResponse": {
                        "AttachToIndex": {"AttachedObjectIdentifier": obj_id}
                    }
                }
            if "DetachFromIndex" in op:
                params = op["DetachFromIndex"]
                obj_id = self.detach_from_index(
                    directory_arn,
                    params["IndexReference"],
                    params["TargetReference"],
                )
                return {
                    "SuccessfulResponse": {
                        "DetachFromIndex": {"DetachedObjectIdentifier": obj_id}
                    }
                }
            if "AttachTypedLink" in op:
                params = op["AttachTypedLink"]
                specifier = self.attach_typed_link(
                    directory_arn,
                    params["SourceObjectReference"],
                    params["TargetObjectReference"],
                    params["TypedLinkFacet"],
                    params.get("Attributes", []),
                )
                return {
                    "SuccessfulResponse": {
                        "AttachTypedLink": {"TypedLinkSpecifier": specifier}
                    }
                }
            if "DetachTypedLink" in op:
                params = op["DetachTypedLink"]
                self.detach_typed_link(
                    directory_arn, params["TypedLinkSpecifier"]
                )
                return {"SuccessfulResponse": {"DetachTypedLink": {}}}
            if "UpdateLinkAttributes" in op:
                params = op["UpdateLinkAttributes"]
                self.update_link_attributes(
                    directory_arn,
                    params["TypedLinkSpecifier"],
                    params.get("AttributeUpdates", []),
                )
                return {"SuccessfulResponse": {"UpdateLinkAttributes": {}}}
        except Exception as exc:
            return {
                "ExceptionResponse": {
                    "Type": type(exc).__name__,
                    "Message": str(exc),
                }
            }
        return {
            "ExceptionResponse": {
                "Type": "NotImplemented",
                "Message": "Batch write operation not supported",
            }
        }


clouddirectory_backends = BackendDict(CloudDirectoryBackend, "clouddirectory")
