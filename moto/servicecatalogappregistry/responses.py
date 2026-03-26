"""Handles incoming servicecatalogappregistry requests, invokes methods, returns responses."""

import json
from urllib.parse import unquote

from moto.core.responses import BaseResponse
from moto.servicecatalogappregistry.exceptions import ValidationException

from .models import (
    Application,
    AppRegistryBackend,
    servicecatalogappregistry_backends,
)


class AppRegistryResponse(BaseResponse):
    """Handler for AppRegistry requests and responses."""

    def __init__(self) -> None:
        super().__init__(service_name="servicecatalog-appregistry")

    @property
    def servicecatalogappregistry_backend(self) -> AppRegistryBackend:
        """Return backend instance specific for this region."""
        return servicecatalogappregistry_backends[self.current_account][self.region]

    def create_application(self) -> str:
        name = self._get_param("name")
        description = self._get_param("description")
        tags = self._get_param("tags") or {}
        client_token = self._get_param("clientToken")
        application = self.servicecatalogappregistry_backend.create_application(
            name=name,
            description=description,
            tags=tags,
            client_token=client_token,
        )
        return json.dumps({"application": application.to_json()})

    def get_application(self) -> str:
        application = unquote(self._get_param("application"))
        app = self.servicecatalogappregistry_backend.get_application(application)
        return json.dumps(app.to_json())

    def update_application(self) -> str:
        application = unquote(self._get_param("application"))
        name = self._get_param("name")
        description = self._get_param("description")
        app = self.servicecatalogappregistry_backend.update_application(
            application=application,
            name=name,
            description=description,
        )
        return json.dumps({"application": app.to_json()})

    def delete_application(self) -> str:
        application = unquote(self._get_param("application"))
        app = self.servicecatalogappregistry_backend.delete_application(application)
        return json.dumps({"application": app.to_json()})

    def list_applications(self) -> str:
        applications = self.servicecatalogappregistry_backend.list_applications()
        json_list = []
        for app in applications:
            json_list.append(app.to_json())
        return json.dumps({"applications": json_list})

    def create_attribute_group(self) -> str:
        name = self._get_param("name")
        description = self._get_param("description")
        attributes = self._get_param("attributes")
        tags = self._get_param("tags") or {}
        client_token = self._get_param("clientToken")
        ag = self.servicecatalogappregistry_backend.create_attribute_group(
            name=name,
            description=description,
            attributes=attributes,
            tags=tags,
            client_token=client_token,
        )
        return json.dumps({"attributeGroup": ag.to_json()})

    def get_attribute_group(self) -> str:
        attribute_group = unquote(self._get_param("attributeGroup"))
        ag = self.servicecatalogappregistry_backend.get_attribute_group(attribute_group)
        return json.dumps(ag.to_json())

    def update_attribute_group(self) -> str:
        attribute_group = unquote(self._get_param("attributeGroup"))
        name = self._get_param("name")
        description = self._get_param("description")
        attributes = self._get_param("attributes")
        ag = self.servicecatalogappregistry_backend.update_attribute_group(
            attribute_group=attribute_group,
            name=name,
            description=description,
            attributes=attributes,
        )
        return json.dumps({"attributeGroup": ag.to_json()})

    def delete_attribute_group(self) -> str:
        attribute_group = unquote(self._get_param("attributeGroup"))
        ag = self.servicecatalogappregistry_backend.delete_attribute_group(attribute_group)
        return json.dumps({"attributeGroup": ag.to_json()})

    def list_attribute_groups(self) -> str:
        ags = self.servicecatalogappregistry_backend.list_attribute_groups()
        return json.dumps({"attributeGroups": [ag.to_json() for ag in ags]})

    def associate_attribute_group(self) -> str:
        application = unquote(self._get_param("application"))
        attribute_group = unquote(self._get_param("attributeGroup"))
        result = self.servicecatalogappregistry_backend.associate_attribute_group(
            application=application,
            attribute_group=attribute_group,
        )
        return json.dumps(result)

    def disassociate_attribute_group(self) -> str:
        application = unquote(self._get_param("application"))
        attribute_group = unquote(self._get_param("attributeGroup"))
        result = self.servicecatalogappregistry_backend.disassociate_attribute_group(
            application=application,
            attribute_group=attribute_group,
        )
        return json.dumps(result)

    def list_associated_attribute_groups(self) -> str:
        application = unquote(self._get_param("application"))
        arns = self.servicecatalogappregistry_backend.list_associated_attribute_groups(application)
        return json.dumps({"attributeGroups": arns})

    def list_attribute_groups_for_application(self) -> str:
        application = unquote(self._get_param("application"))
        ags = self.servicecatalogappregistry_backend.list_attribute_groups_for_application(application)
        return json.dumps({"attributeGroupsDetails": ags})

    def associate_resource(self) -> str:
        application = unquote(self._get_param("application"))
        resource_type = self._get_param("resourceType")
        resource = unquote(self._get_param("resource"))
        options = self._get_param("options")
        app = None
        app = self._find_app_by_any_value(application)
        if options is None:
            options = []
        new_resource = self.servicecatalogappregistry_backend.associate_resource(
            app.arn,
            resource_type,
            resource,
            options,
        )
        return json.dumps(new_resource)

    def disassociate_resource(self) -> str:
        application = unquote(self._get_param("application"))
        resource_type = self._get_param("resourceType")
        resource = unquote(self._get_param("resource"))
        result = self.servicecatalogappregistry_backend.disassociate_resource(
            application=application,
            resource_type=resource_type,
            resource=resource,
        )
        return json.dumps(result)

    def get_associated_resource(self) -> str:
        application = unquote(self._get_param("application"))
        resource_type = self._get_param("resourceType")
        resource = unquote(self._get_param("resource"))
        result = self.servicecatalogappregistry_backend.get_associated_resource(
            application=application,
            resource_type=resource_type,
            resource=resource,
        )
        return json.dumps({"resource": result})

    def list_associated_resources(self) -> str:
        application = unquote(self._get_param("application"))
        app = self._find_app_by_any_value(application)
        return_list = []
        for resource in app.associated_resources.values():
            return_list.append(resource.to_json())
        return json.dumps({"resources": return_list})

    def sync_resource(self) -> str:
        resource_type = self._get_param("resourceType")
        resource = unquote(self._get_param("resource"))
        result = self.servicecatalogappregistry_backend.sync_resource(
            resource_type=resource_type,
            resource=resource,
        )
        return json.dumps(result)

    def list_tags_for_resource(self) -> str:
        resource_arn = unquote(self._get_param("resourceArn"))
        tags = self.servicecatalogappregistry_backend.list_tags_for_resource(resource_arn)
        return json.dumps({"tags": tags})

    def tag_resource(self) -> str:
        resource_arn = unquote(self._get_param("resourceArn"))
        tags = self._get_param("tags") or {}
        self.servicecatalogappregistry_backend.tag_resource(resource_arn, tags)
        return json.dumps({})

    def untag_resource(self) -> str:
        resource_arn = unquote(self._get_param("resourceArn"))
        tag_keys = self.querystring.get("tagKeys", [])
        self.servicecatalogappregistry_backend.untag_resource(resource_arn, tag_keys)
        return json.dumps({})

    def _find_app_by_any_value(self, search: str) -> Application:
        app = None
        if search in self.servicecatalogappregistry_backend.applications:
            app = self.servicecatalogappregistry_backend.applications[search]
        else:
            for a in self.servicecatalogappregistry_backend.applications.values():
                if search == a.id:
                    app = a
                elif search == a.name:
                    app = a
        if app is None:
            raise ValidationException
        return app

    def put_configuration(self) -> None:
        configuration = self._get_param("configuration")
        self.servicecatalogappregistry_backend.put_configuration(
            configuration=configuration,
        )

    def get_configuration(self) -> str:
        return json.dumps(
            {"configuration": self.servicecatalogappregistry_backend.configuration}
        )
