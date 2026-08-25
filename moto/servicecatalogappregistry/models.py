"""AppRegistryBackend class with methods for supported APIs."""

import datetime
import re
from typing import Any

from moto.core.base_backend import BackendDict, BaseBackend
from moto.core.common_models import BaseModel
from moto.moto_api._internal import mock_random
from moto.resourcegroups.models import FakeResourceGroup
from moto.servicecatalogappregistry.exceptions import (
    ResourceNotFoundException,
    ValidationException,
)
from moto.utilities.tagging_service import TaggingService
from moto.utilities.utils import get_partition


class AttributeGroup(BaseModel):
    def __init__(
        self,
        name: str,
        description: str,
        attributes: str,
        region: str,
        account_id: str,
    ):
        self.id = mock_random.get_random_string(
            length=27, include_digits=True, lower_case=True
        )
        self.arn = f"arn:{get_partition(region)}:servicecatalog:{region}:{account_id}:attribute-groups/{self.id}"
        self.name = name
        self.description = description
        self.attributes = attributes
        self.creationTime = datetime.datetime.now()
        self.lastUpdateTime = self.creationTime
        self.tags: dict[str, str] = {}

    def to_json(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "arn": self.arn,
            "name": self.name,
            "description": self.description,
            "attributes": self.attributes,
            "creationTime": str(self.creationTime),
            "lastUpdateTime": str(self.lastUpdateTime),
            "tags": self.tags,
        }


class Application(BaseModel):
    def __init__(
        self,
        name: str,
        description: str,
        region: str,
        account_id: str,
    ):
        self.id = mock_random.get_random_string(
            length=27, include_digits=True, lower_case=True
        )
        self.arn = f"arn:{get_partition(region)}:servicecatalog:{region}:{account_id}:applications/{self.id}"
        self.name = name
        self.description = description
        self.creationTime = datetime.datetime.now()
        self.lastUpdateTime = self.creationTime
        self.tags: dict[str, str] = {}
        self.applicationTag: dict[str, str] = {"awsApplication": self.arn}

        self.associated_resources: dict[str, AssociatedResource] = {}
        self.associated_attribute_groups: dict[str, str] = {}  # arn -> arn

    def to_json(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "arn": self.arn,
            "name": self.name,
            "description": self.description,
            "creationTime": str(self.creationTime),
            "lastUpdateTime": str(self.lastUpdateTime),
            "tags": self.tags,
            "applicationTag": self.applicationTag,
        }


class AssociatedResource(BaseBackend):
    def __init__(
        self,
        resource_type: str,
        resource: str,
        options: list[str],
        application: Application,
        account_id: str,
        region_name: str,
    ):
        if resource_type == "CFN_STACK":
            from moto.cloudformation.exceptions import ValidationError
            from moto.cloudformation.models import cloudformation_backends

            self.resource = resource
            match = re.search(
                r"^arn:aws:cloudformation:(us(-gov)?|ap|ca|cn|eu|sa)-(central|(north|south)?(east|west)?)-\d:\d{12}:stack/\w[a-zA-Z0-9\-]{0,127}/[a-f0-9]{8}(-[a-f0-9]{4}){3}-[a-f0-9]{12}$",
                resource,
            )
            if match is not None:
                self.name = resource.split("/")[1]
            else:
                self.name = resource
            cf_backend = cloudformation_backends[account_id][region_name]
            try:
                cf_backend.get_stack(self.name)
            except ValidationError:
                raise ResourceNotFoundException(
                    f"No CloudFormation stack called '{self.name}' found"
                )
        elif resource_type == "RESOURCE_TAG_VALUE":
            tags = {
                "EnableAWSServiceCatalogAppRegistry": "true",
                "aws:servicecatalog:applicationName": application.name,
                "aws:servicecatalog:applicationId": application.id,
                "aws:servicecatalog:applicationArn": application.arn,
            }
            new_resource_group = FakeResourceGroup(
                account_id,
                region_name,
                f"AWS_AppRegistry_AppTag_{account_id}-{application.name}",
                {"Type": "TAG_FILTERS_1_0", "Query": resource},
                None,
                tags,
            )
            self.resource = new_resource_group.arn
            self.name = new_resource_group._name
            self.query = resource
        else:
            raise ValidationException
        self.resource_type = resource_type
        self.options = options

    def to_json(self) -> dict[str, Any]:
        return_dict = {
            "name": self.name,
            "arn": self.resource,
            "resourceType": self.resource_type,
            "options": self.options,
        }
        if self.resource_type == "RESOURCE_TAG_VALUE":
            return_dict["resourceDetails"] = {"tagValue": self.query}  # type: ignore
        return return_dict


class AppRegistryBackend(BaseBackend):
    """Implementation of AppRegistry APIs."""

    def __init__(self, region_name: str, account_id: str):
        super().__init__(region_name, account_id)
        self.applications: dict[str, Application] = {}
        self.attribute_groups: dict[str, AttributeGroup] = {}
        self.tagger = TaggingService()
        self.configuration: dict[str, Any] = {"tagQueryConfiguration": {}}

    def _find_app(self, search: str) -> Application:
        """Find application by ARN, ID, or name."""
        if search in self.applications:
            return self.applications[search]
        for app in self.applications.values():
            if search == app.id or search == app.name:
                return app
        raise ResourceNotFoundException(f"Application not found: {search}")

    def _find_attribute_group(self, search: str) -> AttributeGroup:
        """Find attribute group by ARN, ID, or name."""
        if search in self.attribute_groups:
            return self.attribute_groups[search]
        for ag in self.attribute_groups.values():
            if search == ag.id or search == ag.name:
                return ag
        raise ResourceNotFoundException(f"AttributeGroup not found: {search}")

    def create_application(
        self, name: str, description: str, tags: dict[str, str], client_token: str
    ) -> Application:
        app = Application(
            name,
            description,
            region=self.region_name,
            account_id=self.account_id,
        )
        self.applications[app.arn] = app
        self._tag_resource(app.arn, tags)
        return app

    def get_application(self, application: str) -> Application:
        return self._find_app(application)

    def update_application(
        self, application: str, name: str, description: str
    ) -> Application:
        app = self._find_app(application)
        if name is not None:
            app.name = name
        if description is not None:
            app.description = description
        app.lastUpdateTime = datetime.datetime.now()
        return app

    def delete_application(self, application: str) -> Application:
        app = self._find_app(application)
        del self.applications[app.arn]
        return app

    def list_applications(self) -> list[Application]:
        return list(self.applications.values())

    def create_attribute_group(
        self,
        name: str,
        description: str,
        attributes: str,
        tags: dict[str, str],
        client_token: str,
    ) -> AttributeGroup:
        ag = AttributeGroup(
            name,
            description,
            attributes,
            region=self.region_name,
            account_id=self.account_id,
        )
        self.attribute_groups[ag.arn] = ag
        self._tag_resource(ag.arn, tags or {})
        return ag

    def get_attribute_group(self, attribute_group: str) -> AttributeGroup:
        return self._find_attribute_group(attribute_group)

    def update_attribute_group(
        self, attribute_group: str, name: str, description: str, attributes: str
    ) -> AttributeGroup:
        ag = self._find_attribute_group(attribute_group)
        if name is not None:
            ag.name = name
        if description is not None:
            ag.description = description
        if attributes is not None:
            ag.attributes = attributes
        ag.lastUpdateTime = datetime.datetime.now()
        return ag

    def delete_attribute_group(self, attribute_group: str) -> AttributeGroup:
        ag = self._find_attribute_group(attribute_group)
        del self.attribute_groups[ag.arn]
        return ag

    def list_attribute_groups(self) -> list[AttributeGroup]:
        return list(self.attribute_groups.values())

    def associate_attribute_group(
        self, application: str, attribute_group: str
    ) -> dict[str, str]:
        app = self._find_app(application)
        ag = self._find_attribute_group(attribute_group)
        app.associated_attribute_groups[ag.arn] = ag.arn
        return {"applicationArn": app.arn, "attributeGroupArn": ag.arn}

    def disassociate_attribute_group(
        self, application: str, attribute_group: str
    ) -> dict[str, str]:
        app = self._find_app(application)
        ag = self._find_attribute_group(attribute_group)
        app.associated_attribute_groups.pop(ag.arn, None)
        return {"applicationArn": app.arn, "attributeGroupArn": ag.arn}

    def list_associated_attribute_groups(
        self, application: str
    ) -> list[str]:
        app = self._find_app(application)
        return list(app.associated_attribute_groups.keys())

    def list_attribute_groups_for_application(
        self, application: str
    ) -> list[dict[str, Any]]:
        app = self._find_app(application)
        result = []
        for ag_arn in app.associated_attribute_groups.keys():
            if ag_arn in self.attribute_groups:
                ag = self.attribute_groups[ag_arn]
                result.append({"id": ag.id, "arn": ag.arn, "name": ag.name, "createdBy": self.account_id})
        return result

    def associate_resource(
        self, application: str, resource_type: str, resource: str, options: list[str]
    ) -> dict[str, Any]:
        app = self.applications[application]
        new_resource = AssociatedResource(
            resource_type, resource, options, app, self.account_id, self.region_name
        )
        app.associated_resources[new_resource.resource] = new_resource
        return {"applicationArn": app.arn, "resourceArn": resource, "options": options}

    def disassociate_resource(
        self, application: str, resource_type: str, resource: str
    ) -> dict[str, str]:
        app = self._find_app(application)
        # Find resource by name or arn
        to_delete = None
        for res_arn, res in app.associated_resources.items():
            if res.name == resource or res.resource == resource or res_arn == resource:
                to_delete = res_arn
                break
        if to_delete:
            del app.associated_resources[to_delete]
        return {"applicationArn": app.arn, "resourceArn": resource}

    def get_associated_resource(
        self, application: str, resource_type: str, resource: str
    ) -> dict[str, Any]:
        app = self._find_app(application)
        for res in app.associated_resources.values():
            if res.name == resource or res.resource == resource:
                return res.to_json()
        raise ResourceNotFoundException(f"Resource not found: {resource}")

    def sync_resource(
        self, resource_type: str, resource: str
    ) -> dict[str, Any]:
        # Find which application this resource is associated with
        for app in self.applications.values():
            for res in app.associated_resources.values():
                if res.name == resource or res.resource == resource:
                    return {
                        "applicationArn": app.arn,
                        "resourceArn": res.resource,
                        "actionTaken": "NO_ACTION",
                    }
        raise ResourceNotFoundException(f"Resource not found: {resource}")

    def list_tags_for_resource(self, resource_arn: str) -> dict[str, str]:
        return self.tagger.get_tag_dict_for_resource(resource_arn)

    def tag_resource(self, resource_arn: str, tags: dict[str, str]) -> None:
        self._tag_resource(resource_arn, tags)

    def untag_resource(self, resource_arn: str, tag_keys: list[str]) -> None:
        self._untag_resource(resource_arn, tag_keys)

    def _list_tags_for_resource(self, arn: str) -> dict[str, str]:
        return self.tagger.get_tag_dict_for_resource(arn)

    def _tag_resource(self, arn: str, tags: dict[str, str]) -> None:
        self.tagger.tag_resource(arn, TaggingService.convert_dict_to_tags_input(tags))

    def _untag_resource(self, arn: str, tag_keys: list[str]) -> None:
        self.tagger.untag_resource_using_names(arn, tag_keys)

    def put_configuration(self, configuration: dict[str, Any]) -> None:
        self.configuration = configuration

    def get_configuration(
        self,
    ) -> dict[str, Any]:
        return self.configuration


servicecatalogappregistry_backends = BackendDict(
    AppRegistryBackend, "servicecatalog-appregistry"
)
