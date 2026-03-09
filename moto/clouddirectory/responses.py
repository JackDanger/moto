"""Handles incoming clouddirectory requests, invokes methods, returns responses."""

import json

from moto.core.responses import BaseResponse

from .models import CloudDirectoryBackend, clouddirectory_backends


class CloudDirectoryResponse(BaseResponse):
    """Handler for CloudDirectory requests and responses."""

    def __init__(self) -> None:
        super().__init__(service_name="clouddirectory")

    @property
    def clouddirectory_backend(self) -> "CloudDirectoryBackend":
        """Return backend instance specific for this region."""
        return clouddirectory_backends[self.current_account][self.region]

    def apply_schema(self) -> str:
        directory_arn = self.headers.get("x-amz-data-partition")
        published_schema_arn = self._get_param("PublishedSchemaArn")
        self.clouddirectory_backend.apply_schema(
            directory_arn=directory_arn,
            published_schema_arn=published_schema_arn,
        )
        return json.dumps(
            {
                "AppliedSchemaArn": published_schema_arn,
                "DirectoryArn": directory_arn,
            }
        )

    def publish_schema(self) -> str:
        development_schema_arn = self.headers.get("x-amz-data-partition")
        version = self._get_param("Version")
        minor_version = self._get_param("MinorVersion")
        name = self._get_param("Name")
        schema = self.clouddirectory_backend.publish_schema(
            name=name,
            version=version,
            minor_version=minor_version,
            development_schema_arn=development_schema_arn,
        )
        return json.dumps({"PublishedSchemaArn": schema})

    def create_directory(self) -> str:
        name = self._get_param("Name")
        schema_arn = self.headers.get("x-amz-data-partition")
        directory = self.clouddirectory_backend.create_directory(
            name=name,
            schema_arn=schema_arn,
        )

        return json.dumps(
            {
                "DirectoryArn": directory.directory_arn,
                "Name": name,
                "ObjectIdentifier": directory.object_identifier,
                "AppliedSchemaArn": directory.schema_arn,
            }
        )

    def create_schema(self) -> str:
        name = self._get_param("Name")
        schema = self.clouddirectory_backend.create_schema(
            name=name,
        )
        return json.dumps({"SchemaArn": schema})

    def list_directories(self) -> str:
        next_token = self._get_param("NextToken")
        max_results = self._get_param("MaxResults")
        state = self._get_param("state")
        directories, next_token = self.clouddirectory_backend.list_directories(
            state=state, next_token=next_token, max_results=max_results
        )
        directory_list = [directory.to_dict() for directory in directories]
        return json.dumps({"Directories": directory_list, "NextToken": next_token})

    def tag_resource(self) -> str:
        resource_arn = self._get_param("ResourceArn")
        tags = self._get_param("Tags")
        self.clouddirectory_backend.tag_resource(
            resource_arn=resource_arn,
            tags=tags,
        )
        return json.dumps({})

    def untag_resource(self) -> str:
        resource_arn = self._get_param("ResourceArn")
        tag_keys = self._get_param("TagKeys")
        self.clouddirectory_backend.untag_resource(
            resource_arn=resource_arn,
            tag_keys=tag_keys,
        )
        return json.dumps({})

    def delete_directory(self) -> str:
        arn = self.headers.get("x-amz-data-partition")
        directory_arn = self.clouddirectory_backend.delete_directory(
            directory_arn=arn,
        )
        return json.dumps({"DirectoryArn": directory_arn})

    def delete_schema(self) -> str:
        arn = self.headers.get("x-amz-data-partition")
        self.clouddirectory_backend.delete_schema(
            schema_arn=arn,
        )
        return json.dumps({"SchemaArn": arn})

    def list_development_schema_arns(self) -> str:
        next_token = self._get_param("NextToken")
        max_results = self._get_param("MaxResults")
        schemas, next_token = self.clouddirectory_backend.list_development_schema_arns(
            next_token=next_token,
            max_results=max_results,
        )
        return json.dumps({"SchemaArns": schemas, "NextToken": next_token})

    def list_published_schema_arns(self) -> str:
        next_token = self._get_param("NextToken")
        max_results = self._get_param("MaxResults")
        schemas, next_token = self.clouddirectory_backend.list_published_schema_arns(
            next_token=next_token,
            max_results=max_results,
        )
        return json.dumps({"SchemaArns": schemas, "NextToken": next_token})

    def get_directory(self) -> str:
        arn = self.headers.get("x-amz-data-partition")
        directory = self.clouddirectory_backend.get_directory(
            directory_arn=arn,
        )
        return json.dumps({"Directory": directory.to_dict()})

    def list_tags_for_resource(self) -> str:
        resource_arn = self._get_param("ResourceArn")
        next_token = self._get_param("NextToken")
        max_results = self._get_param("MaxResults")
        tags = self.clouddirectory_backend.list_tags_for_resource(
            resource_arn=resource_arn,
            next_token=next_token,
            max_results=max_results,
        )
        return json.dumps({"Tags": tags, "NextToken": next_token})

    # --- Facet operations ---

    def create_facet(self) -> str:
        schema_arn = self.headers.get("x-amz-data-partition")
        name = self._get_param("Name")
        attributes = self._get_param("Attributes")
        object_type = self._get_param("ObjectType")
        facet_style = self._get_param("FacetStyle")
        self.clouddirectory_backend.create_facet(
            schema_arn=schema_arn,
            name=name,
            attributes=attributes,
            object_type=object_type,
            facet_style=facet_style,
        )
        return json.dumps({})

    def delete_facet(self) -> str:
        schema_arn = self.headers.get("x-amz-data-partition")
        name = self._get_param("Name")
        self.clouddirectory_backend.delete_facet(
            schema_arn=schema_arn,
            name=name,
        )
        return json.dumps({})

    def get_facet(self) -> str:
        schema_arn = self.headers.get("x-amz-data-partition")
        name = self._get_param("Name")
        facet = self.clouddirectory_backend.get_facet(
            schema_arn=schema_arn,
            name=name,
        )
        return json.dumps({"Facet": facet.to_dict()})

    def update_facet(self) -> str:
        schema_arn = self.headers.get("x-amz-data-partition")
        name = self._get_param("Name")
        attribute_updates = self._get_param("AttributeUpdates")
        object_type = self._get_param("ObjectType")
        self.clouddirectory_backend.update_facet(
            schema_arn=schema_arn,
            name=name,
            attribute_updates=attribute_updates,
            object_type=object_type,
        )
        return json.dumps({})

    def list_facet_names(self) -> str:
        schema_arn = self.headers.get("x-amz-data-partition")
        next_token = self._get_param("NextToken")
        max_results = self._get_param("MaxResults")
        names, next_token = self.clouddirectory_backend.list_facet_names(
            schema_arn=schema_arn,
            next_token=next_token,
            max_results=max_results,
        )
        return json.dumps({"FacetNames": names, "NextToken": next_token})

    def list_facet_attributes(self) -> str:
        schema_arn = self.headers.get("x-amz-data-partition")
        name = self._get_param("Name")
        next_token = self._get_param("NextToken")
        max_results = self._get_param("MaxResults")
        attributes, next_token = self.clouddirectory_backend.list_facet_attributes(
            schema_arn=schema_arn,
            name=name,
            next_token=next_token,
            max_results=max_results,
        )
        return json.dumps({"Attributes": attributes, "NextToken": next_token})

    # --- TypedLink Facet operations ---

    def create_typed_link_facet(self) -> str:
        schema_arn = self.headers.get("x-amz-data-partition")
        facet = self._get_param("Facet")
        self.clouddirectory_backend.create_typed_link_facet(
            schema_arn=schema_arn,
            facet=facet,
        )
        return json.dumps({})

    def delete_typed_link_facet(self) -> str:
        schema_arn = self.headers.get("x-amz-data-partition")
        name = self._get_param("Name")
        self.clouddirectory_backend.delete_typed_link_facet(
            schema_arn=schema_arn,
            name=name,
        )
        return json.dumps({})

    def get_typed_link_facet_information(self) -> str:
        schema_arn = self.headers.get("x-amz-data-partition")
        name = self._get_param("Name")
        identity_order = self.clouddirectory_backend.get_typed_link_facet_information(
            schema_arn=schema_arn,
            name=name,
        )
        return json.dumps({"IdentityAttributeOrder": identity_order})

    def update_typed_link_facet(self) -> str:
        schema_arn = self.headers.get("x-amz-data-partition")
        name = self._get_param("Name")
        attribute_updates = self._get_param("AttributeUpdates")
        identity_attribute_order = self._get_param("IdentityAttributeOrder")
        self.clouddirectory_backend.update_typed_link_facet(
            schema_arn=schema_arn,
            name=name,
            attribute_updates=attribute_updates,
            identity_attribute_order=identity_attribute_order,
        )
        return json.dumps({})

    def list_typed_link_facet_names(self) -> str:
        schema_arn = self.headers.get("x-amz-data-partition")
        next_token = self._get_param("NextToken")
        max_results = self._get_param("MaxResults")
        names, next_token = self.clouddirectory_backend.list_typed_link_facet_names(
            schema_arn=schema_arn,
            next_token=next_token,
            max_results=max_results,
        )
        return json.dumps({"FacetNames": names, "NextToken": next_token})

    def list_typed_link_facet_attributes(self) -> str:
        schema_arn = self.headers.get("x-amz-data-partition")
        name = self._get_param("Name")
        next_token = self._get_param("NextToken")
        max_results = self._get_param("MaxResults")
        attributes, next_token = (
            self.clouddirectory_backend.list_typed_link_facet_attributes(
                schema_arn=schema_arn,
                name=name,
                next_token=next_token,
                max_results=max_results,
            )
        )
        return json.dumps({"Attributes": attributes, "NextToken": next_token})

    # --- Object operations ---

    def create_object(self) -> str:
        directory_arn = self.headers.get("x-amz-data-partition")
        schema_facets = self._get_param("SchemaFacets")
        object_attribute_list = self._get_param("ObjectAttributeList")
        parent_reference = self._get_param("ParentReference")
        link_name = self._get_param("LinkName")
        obj_id = self.clouddirectory_backend.create_object(
            directory_arn=directory_arn,
            schema_facets=schema_facets or [],
            object_attribute_list=object_attribute_list,
            parent_reference=parent_reference,
            link_name=link_name,
        )
        return json.dumps({"ObjectIdentifier": obj_id})

    def delete_object(self) -> str:
        directory_arn = self.headers.get("x-amz-data-partition")
        object_reference = self._get_param("ObjectReference")
        self.clouddirectory_backend.delete_object(
            directory_arn=directory_arn,
            object_reference=object_reference,
        )
        return json.dumps({})

    def get_object_information(self) -> str:
        directory_arn = self.headers.get("x-amz-data-partition")
        object_reference = self._get_param("ObjectReference")
        obj = self.clouddirectory_backend.get_object_information(
            directory_arn=directory_arn,
            object_reference=object_reference,
        )
        return json.dumps(
            {
                "SchemaFacets": obj.schema_facets,
                "ObjectIdentifier": obj.object_identifier,
            }
        )

    def get_object_attributes(self) -> str:
        directory_arn = self.headers.get("x-amz-data-partition")
        object_reference = self._get_param("ObjectReference")
        schema_facet = self._get_param("SchemaFacet")
        attribute_names = self._get_param("AttributeNames")
        attrs = self.clouddirectory_backend.get_object_attributes(
            directory_arn=directory_arn,
            object_reference=object_reference,
            schema_facet=schema_facet,
            attribute_names=attribute_names or [],
        )
        return json.dumps({"Attributes": attrs})

    def update_object_attributes(self) -> str:
        directory_arn = self.headers.get("x-amz-data-partition")
        object_reference = self._get_param("ObjectReference")
        attribute_updates = self._get_param("AttributeUpdates")
        obj_id = self.clouddirectory_backend.update_object_attributes(
            directory_arn=directory_arn,
            object_reference=object_reference,
            attribute_updates=attribute_updates or [],
        )
        return json.dumps({"ObjectIdentifier": obj_id})

    def add_facet_to_object(self) -> str:
        directory_arn = self.headers.get("x-amz-data-partition")
        schema_facet = self._get_param("SchemaFacet")
        object_attribute_list = self._get_param("ObjectAttributeList")
        object_reference = self._get_param("ObjectReference")
        self.clouddirectory_backend.add_facet_to_object(
            directory_arn=directory_arn,
            schema_facet=schema_facet,
            object_attribute_list=object_attribute_list,
            object_reference=object_reference,
        )
        return json.dumps({})

    def remove_facet_from_object(self) -> str:
        directory_arn = self.headers.get("x-amz-data-partition")
        schema_facet = self._get_param("SchemaFacet")
        object_reference = self._get_param("ObjectReference")
        self.clouddirectory_backend.remove_facet_from_object(
            directory_arn=directory_arn,
            schema_facet=schema_facet,
            object_reference=object_reference,
        )
        return json.dumps({})

    def list_object_attributes(self) -> str:
        directory_arn = self.headers.get("x-amz-data-partition")
        object_reference = self._get_param("ObjectReference")
        next_token = self._get_param("NextToken")
        max_results = self._get_param("MaxResults")
        attrs, next_token = self.clouddirectory_backend.list_object_attributes(
            directory_arn=directory_arn,
            object_reference=object_reference,
            next_token=next_token,
            max_results=max_results,
        )
        return json.dumps({"Attributes": attrs, "NextToken": next_token})

    def list_object_children(self) -> str:
        directory_arn = self.headers.get("x-amz-data-partition")
        object_reference = self._get_param("ObjectReference")
        next_token = self._get_param("NextToken")
        max_results = self._get_param("MaxResults")
        children, next_token = self.clouddirectory_backend.list_object_children(
            directory_arn=directory_arn,
            object_reference=object_reference,
            next_token=next_token,
            max_results=max_results,
        )
        children_dict = dict(children)
        return json.dumps({"Children": children_dict, "NextToken": next_token})

    def list_object_parents(self) -> str:
        directory_arn = self.headers.get("x-amz-data-partition")
        object_reference = self._get_param("ObjectReference")
        next_token = self._get_param("NextToken")
        max_results = self._get_param("MaxResults")
        parents, next_token = self.clouddirectory_backend.list_object_parents(
            directory_arn=directory_arn,
            object_reference=object_reference,
            next_token=next_token,
            max_results=max_results,
        )
        parents_dict = dict(parents)
        return json.dumps({"Parents": parents_dict, "NextToken": next_token})

    def list_object_parent_paths(self) -> str:
        directory_arn = self.headers.get("x-amz-data-partition")
        object_reference = self._get_param("ObjectReference")
        next_token = self._get_param("NextToken")
        max_results = self._get_param("MaxResults")
        paths, next_token = self.clouddirectory_backend.list_object_parent_paths(
            directory_arn=directory_arn,
            object_reference=object_reference,
            next_token=next_token,
            max_results=max_results,
        )
        return json.dumps(
            {"PathToObjectIdentifiersList": paths, "NextToken": next_token}
        )

    def list_object_policies(self) -> str:
        directory_arn = self.headers.get("x-amz-data-partition")
        object_reference = self._get_param("ObjectReference")
        next_token = self._get_param("NextToken")
        max_results = self._get_param("MaxResults")
        policies, next_token = self.clouddirectory_backend.list_object_policies(
            directory_arn=directory_arn,
            object_reference=object_reference,
            next_token=next_token,
            max_results=max_results,
        )
        return json.dumps({"AttachedPolicyIds": policies, "NextToken": next_token})

    # --- Attach/Detach operations ---

    def attach_object(self) -> str:
        directory_arn = self.headers.get("x-amz-data-partition")
        parent_reference = self._get_param("ParentReference")
        child_reference = self._get_param("ChildReference")
        link_name = self._get_param("LinkName")
        obj_id = self.clouddirectory_backend.attach_object(
            directory_arn=directory_arn,
            parent_reference=parent_reference,
            child_reference=child_reference,
            link_name=link_name,
        )
        return json.dumps({"AttachedObjectIdentifier": obj_id})

    def detach_object(self) -> str:
        directory_arn = self.headers.get("x-amz-data-partition")
        parent_reference = self._get_param("ParentReference")
        link_name = self._get_param("LinkName")
        obj_id = self.clouddirectory_backend.detach_object(
            directory_arn=directory_arn,
            parent_reference=parent_reference,
            link_name=link_name,
        )
        return json.dumps({"DetachedObjectIdentifier": obj_id})

    # --- Policy operations ---

    def attach_policy(self) -> str:
        directory_arn = self.headers.get("x-amz-data-partition")
        policy_reference = self._get_param("PolicyReference")
        object_reference = self._get_param("ObjectReference")
        self.clouddirectory_backend.attach_policy(
            directory_arn=directory_arn,
            policy_reference=policy_reference,
            object_reference=object_reference,
        )
        return json.dumps({})

    def detach_policy(self) -> str:
        directory_arn = self.headers.get("x-amz-data-partition")
        policy_reference = self._get_param("PolicyReference")
        object_reference = self._get_param("ObjectReference")
        self.clouddirectory_backend.detach_policy(
            directory_arn=directory_arn,
            policy_reference=policy_reference,
            object_reference=object_reference,
        )
        return json.dumps({})

    def list_policy_attachments(self) -> str:
        directory_arn = self.headers.get("x-amz-data-partition")
        policy_reference = self._get_param("PolicyReference")
        next_token = self._get_param("NextToken")
        max_results = self._get_param("MaxResults")
        obj_ids, next_token = self.clouddirectory_backend.list_policy_attachments(
            directory_arn=directory_arn,
            policy_reference=policy_reference,
            next_token=next_token,
            max_results=max_results,
        )
        return json.dumps({"ObjectIdentifiers": obj_ids, "NextToken": next_token})

    def lookup_policy(self) -> str:
        directory_arn = self.headers.get("x-amz-data-partition")
        object_reference = self._get_param("ObjectReference")
        result = self.clouddirectory_backend.lookup_policy(
            directory_arn=directory_arn,
            object_reference=object_reference,
        )
        return json.dumps({"PolicyToPathList": result, "NextToken": None})

    # --- Index operations ---

    def create_index(self) -> str:
        directory_arn = self.headers.get("x-amz-data-partition")
        ordered_indexed_attribute_list = self._get_param("OrderedIndexedAttributeList")
        is_unique = self._get_param("IsUnique") or False
        parent_reference = self._get_param("ParentReference")
        link_name = self._get_param("LinkName")
        obj_id = self.clouddirectory_backend.create_index(
            directory_arn=directory_arn,
            ordered_indexed_attribute_list=ordered_indexed_attribute_list,
            is_unique=is_unique,
            parent_reference=parent_reference,
            link_name=link_name,
        )
        return json.dumps({"ObjectIdentifier": obj_id})

    def attach_to_index(self) -> str:
        directory_arn = self.headers.get("x-amz-data-partition")
        index_reference = self._get_param("IndexReference")
        target_reference = self._get_param("TargetReference")
        obj_id = self.clouddirectory_backend.attach_to_index(
            directory_arn=directory_arn,
            index_reference=index_reference,
            target_reference=target_reference,
        )
        return json.dumps({"AttachedObjectIdentifier": obj_id})

    def detach_from_index(self) -> str:
        directory_arn = self.headers.get("x-amz-data-partition")
        index_reference = self._get_param("IndexReference")
        target_reference = self._get_param("TargetReference")
        obj_id = self.clouddirectory_backend.detach_from_index(
            directory_arn=directory_arn,
            index_reference=index_reference,
            target_reference=target_reference,
        )
        return json.dumps({"DetachedObjectIdentifier": obj_id})

    def list_index(self) -> str:
        directory_arn = self.headers.get("x-amz-data-partition")
        index_reference = self._get_param("IndexReference")
        next_token = self._get_param("NextToken")
        max_results = self._get_param("MaxResults")
        attachments, next_token = self.clouddirectory_backend.list_index(
            directory_arn=directory_arn,
            index_reference=index_reference,
            next_token=next_token,
            max_results=max_results,
        )
        return json.dumps({"IndexAttachments": attachments, "NextToken": next_token})

    def list_attached_indices(self) -> str:
        directory_arn = self.headers.get("x-amz-data-partition")
        target_reference = self._get_param("TargetReference")
        next_token = self._get_param("NextToken")
        max_results = self._get_param("MaxResults")
        attachments, next_token = self.clouddirectory_backend.list_attached_indices(
            directory_arn=directory_arn,
            target_reference=target_reference,
            next_token=next_token,
            max_results=max_results,
        )
        return json.dumps({"IndexAttachments": attachments, "NextToken": next_token})

    # --- TypedLink instance operations ---

    def attach_typed_link(self) -> str:
        directory_arn = self.headers.get("x-amz-data-partition")
        source_object_reference = self._get_param("SourceObjectReference")
        target_object_reference = self._get_param("TargetObjectReference")
        typed_link_facet = self._get_param("TypedLinkFacet")
        attributes = self._get_param("Attributes")
        specifier = self.clouddirectory_backend.attach_typed_link(
            directory_arn=directory_arn,
            source_object_reference=source_object_reference,
            target_object_reference=target_object_reference,
            typed_link_facet=typed_link_facet,
            attributes=attributes or [],
        )
        return json.dumps({"TypedLinkSpecifier": specifier})

    def detach_typed_link(self) -> str:
        directory_arn = self.headers.get("x-amz-data-partition")
        typed_link_specifier = self._get_param("TypedLinkSpecifier")
        self.clouddirectory_backend.detach_typed_link(
            directory_arn=directory_arn,
            typed_link_specifier=typed_link_specifier,
        )
        return json.dumps({})

    def get_link_attributes(self) -> str:
        directory_arn = self.headers.get("x-amz-data-partition")
        typed_link_specifier = self._get_param("TypedLinkSpecifier")
        attribute_names = self._get_param("AttributeNames")
        attrs = self.clouddirectory_backend.get_link_attributes(
            directory_arn=directory_arn,
            typed_link_specifier=typed_link_specifier,
            attribute_names=attribute_names or [],
        )
        return json.dumps({"Attributes": attrs})

    def update_link_attributes(self) -> str:
        directory_arn = self.headers.get("x-amz-data-partition")
        typed_link_specifier = self._get_param("TypedLinkSpecifier")
        attribute_updates = self._get_param("AttributeUpdates")
        self.clouddirectory_backend.update_link_attributes(
            directory_arn=directory_arn,
            typed_link_specifier=typed_link_specifier,
            attribute_updates=attribute_updates or [],
        )
        return json.dumps({})

    def list_incoming_typed_links(self) -> str:
        directory_arn = self.headers.get("x-amz-data-partition")
        object_reference = self._get_param("ObjectReference")
        next_token = self._get_param("NextToken")
        max_results = self._get_param("MaxResults")
        links, next_token = self.clouddirectory_backend.list_incoming_typed_links(
            directory_arn=directory_arn,
            object_reference=object_reference,
            next_token=next_token,
            max_results=max_results,
        )
        return json.dumps({"LinkSpecifiers": links, "NextToken": next_token})

    def list_outgoing_typed_links(self) -> str:
        directory_arn = self.headers.get("x-amz-data-partition")
        object_reference = self._get_param("ObjectReference")
        next_token = self._get_param("NextToken")
        max_results = self._get_param("MaxResults")
        links, next_token = self.clouddirectory_backend.list_outgoing_typed_links(
            directory_arn=directory_arn,
            object_reference=object_reference,
            next_token=next_token,
            max_results=max_results,
        )
        return json.dumps({"TypedLinkSpecifiers": links, "NextToken": next_token})

    # --- Directory state operations ---

    def disable_directory(self) -> str:
        directory_arn = self.headers.get("x-amz-data-partition")
        arn = self.clouddirectory_backend.disable_directory(
            directory_arn=directory_arn,
        )
        return json.dumps({"DirectoryArn": arn})

    def enable_directory(self) -> str:
        directory_arn = self.headers.get("x-amz-data-partition")
        arn = self.clouddirectory_backend.enable_directory(
            directory_arn=directory_arn,
        )
        return json.dumps({"DirectoryArn": arn})

    # --- Schema operations ---

    def list_applied_schema_arns(self) -> str:
        directory_arn = self._get_param("DirectoryArn")
        next_token = self._get_param("NextToken")
        max_results = self._get_param("MaxResults")
        arns, next_token = self.clouddirectory_backend.list_applied_schema_arns(
            directory_arn=directory_arn,
            next_token=next_token,
            max_results=max_results,
        )
        return json.dumps({"SchemaArns": arns, "NextToken": next_token})

    def get_applied_schema_version(self) -> str:
        schema_arn = self._get_param("SchemaArn")
        applied_arn = self.clouddirectory_backend.get_applied_schema_version(
            schema_arn=schema_arn,
        )
        return json.dumps({"AppliedSchemaArn": applied_arn})

    def get_schema_as_json(self) -> str:
        schema_arn = self.headers.get("x-amz-data-partition")
        name, document = self.clouddirectory_backend.get_schema_as_json(
            schema_arn=schema_arn,
        )
        return json.dumps({"Name": name, "Document": document})

    def put_schema_from_json(self) -> str:
        schema_arn = self.headers.get("x-amz-data-partition")
        document = self._get_param("Document")
        arn = self.clouddirectory_backend.put_schema_from_json(
            schema_arn=schema_arn,
            document=document,
        )
        return json.dumps({"Arn": arn})

    def update_schema(self) -> str:
        schema_arn = self.headers.get("x-amz-data-partition")
        name = self._get_param("Name")
        arn = self.clouddirectory_backend.update_schema(
            schema_arn=schema_arn,
            name=name,
        )
        return json.dumps({"SchemaArn": arn})

    def upgrade_applied_schema(self) -> str:
        published_schema_arn = self._get_param("PublishedSchemaArn")
        directory_arn = self._get_param("DirectoryArn")
        dry_run = self._get_param("DryRun") or False
        upgraded_arn, dir_arn = self.clouddirectory_backend.upgrade_applied_schema(
            published_schema_arn=published_schema_arn,
            directory_arn=directory_arn,
            dry_run=dry_run,
        )
        return json.dumps(
            {"UpgradedSchemaArn": upgraded_arn, "DirectoryArn": dir_arn}
        )

    def upgrade_published_schema(self) -> str:
        development_schema_arn = self._get_param("DevelopmentSchemaArn")
        published_schema_arn = self._get_param("PublishedSchemaArn")
        minor_version = self._get_param("MinorVersion")
        dry_run = self._get_param("DryRun") or False
        upgraded_arn = self.clouddirectory_backend.upgrade_published_schema(
            development_schema_arn=development_schema_arn,
            published_schema_arn=published_schema_arn,
            minor_version=minor_version,
            dry_run=dry_run,
        )
        return json.dumps({"UpgradedSchemaArn": upgraded_arn})

    def list_managed_schema_arns(self) -> str:
        next_token = self._get_param("NextToken")
        max_results = self._get_param("MaxResults")
        arns, next_token = self.clouddirectory_backend.list_managed_schema_arns(
            next_token=next_token,
            max_results=max_results,
        )
        return json.dumps({"SchemaArns": arns, "NextToken": next_token})

    # --- Batch operations ---

    def batch_read(self) -> str:
        directory_arn = self.headers.get("x-amz-data-partition")
        operations = self._get_param("Operations")
        responses = self.clouddirectory_backend.batch_read(
            directory_arn=directory_arn,
            operations=operations or [],
        )
        return json.dumps({"Responses": responses})

    def batch_write(self) -> str:
        directory_arn = self.headers.get("x-amz-data-partition")
        operations = self._get_param("Operations")
        responses = self.clouddirectory_backend.batch_write(
            directory_arn=directory_arn,
            operations=operations or [],
        )
        return json.dumps({"Responses": responses})
