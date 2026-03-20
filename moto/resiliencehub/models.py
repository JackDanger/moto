import json
from typing import Any, Optional

from moto.core.base_backend import BackendDict, BaseBackend
from moto.core.common_models import BaseModel
from moto.core.utils import unix_time
from moto.moto_api._internal import mock_random
from moto.utilities.paginator import paginate
from moto.utilities.tagging_service import TaggingService
from moto.utilities.utils import get_partition

from .exceptions import (
    AppAssessmentNotFound,
    AppComponentNotFound,
    AppNotFound,
    AppVersionNotFound,
    AppVersionResourceNotFound,
    RecommendationTemplateNotFound,
    ResiliencyPolicyNotFound,
)

PAGINATION_MODEL = {
    "list_apps": {
        "input_token": "next_token",
        "limit_key": "max_results",
        "limit_default": 100,
        "unique_attribute": "arn",
    },
    "list_resiliency_policies": {
        "input_token": "next_token",
        "limit_key": "max_results",
        "limit_default": 100,
        "unique_attribute": "arn",
    },
    "list_recommendation_templates": {
        "input_token": "next_token",
        "limit_key": "max_results",
        "limit_default": 100,
        "unique_attribute": "arn",
    },
    "list_suggested_resiliency_policies": {
        "input_token": "next_token",
        "limit_key": "max_results",
        "limit_default": 100,
        "unique_attribute": "arn",
    },
    "list_app_version_resource_mappings": {
        "input_token": "next_token",
        "limit_key": "max_results",
        "limit_default": 100,
        "unique_attribute": ["physicalResourceId", "identifier"],
    },
    "list_alarm_recommendations": {
        "input_token": "next_token",
        "limit_key": "max_results",
        "limit_default": 100,
        "unique_attribute": "recommendation_id",
    },
    "list_sop_recommendations": {
        "input_token": "next_token",
        "limit_key": "max_results",
        "limit_default": 100,
        "unique_attribute": "recommendation_id",
    },
    "list_test_recommendations": {
        "input_token": "next_token",
        "limit_key": "max_results",
        "limit_default": 100,
        "unique_attribute": "recommendation_id",
    },
    "list_app_component_compliances": {
        "input_token": "next_token",
        "limit_key": "max_results",
        "limit_default": 100,
        "unique_attribute": "app_component_name",
    },
    "list_app_component_recommendations": {
        "input_token": "next_token",
        "limit_key": "max_results",
        "limit_default": 100,
        "unique_attribute": "app_component_name",
    },
    "list_app_input_sources": {
        "input_token": "next_token",
        "limit_key": "max_results",
        "limit_default": 100,
        "unique_attribute": "source_arn",
    },
    "list_app_assessment_compliance_drifts": {
        "input_token": "next_token",
        "limit_key": "max_results",
        "limit_default": 100,
        "unique_attribute": "drift_type",
    },
    "list_app_assessment_resource_drifts": {
        "input_token": "next_token",
        "limit_key": "max_results",
        "limit_default": 100,
        "unique_attribute": "drift_type",
    },
    "list_unsupported_app_version_resources": {
        "input_token": "next_token",
        "limit_key": "max_results",
        "limit_default": 100,
        "unique_attribute": "physical_resource_id",
    },
    "list_resource_grouping_recommendations": {
        "input_token": "next_token",
        "limit_key": "max_results",
        "limit_default": 100,
        "unique_attribute": "grouping_recommendation_id",
    },
}


class AppComponent(BaseModel):
    def __init__(
        self,
        _id: str,
        name: str,
        _type: str,
        additional_info: Optional[dict[str, list[str]]] = None,
    ):
        self.id = _id
        self.name = name
        self.type = _type
        self.additional_info = additional_info or {}

    def to_json(self) -> dict[str, Any]:
        resp: dict[str, Any] = {
            "id": self.id,
            "name": self.name,
            "type": self.type,
        }
        if self.additional_info:
            resp["additionalInfo"] = self.additional_info
        return resp


class App(BaseModel):
    def __init__(
        self,
        backend: "ResilienceHubBackend",
        assessment_schedule: str,
        description: str,
        event_subscriptions: list[dict[str, Any]],
        name: str,
        permission_model: dict[str, Any],
        policy_arn: str,
    ):
        self.backend = backend
        self.arn = f"arn:{get_partition(backend.region_name)}:resiliencehub:{backend.region_name}:{backend.account_id}:app/{mock_random.uuid4()}"
        self.assessment_schedule = assessment_schedule or "Disabled"
        self.compliance_status = "NotAssessed"
        self.description = description
        self.creation_time = unix_time()
        self.event_subscriptions = event_subscriptions
        self.name = name
        self.permission_model = permission_model
        self.policy_arn = policy_arn
        self.resilience_score = 0.0
        self.status = "Active"
        self.app_versions: list[AppVersion] = []
        self.input_sources: list[dict[str, Any]] = []
        self.app_template_body: str = ""

        app_version = AppVersion(app_arn=self.arn, version_name=None, identifier=0)
        self.app_versions.append(app_version)

    def get_version(self, version_name: str) -> "AppVersion":
        for v in self.app_versions:
            if v.app_version == version_name:
                return v
        raise AppVersionNotFound

    def to_json(self) -> dict[str, Any]:
        resp = {
            "appArn": self.arn,
            "assessmentSchedule": self.assessment_schedule,
            "complianceStatus": self.compliance_status,
            "creationTime": self.creation_time,
            "driftStatus": "NotChecked",
            "name": self.name,
            "resilienceScore": self.resilience_score,
            "status": self.status,
            "tags": self.backend.list_tags_for_resource(self.arn),
        }
        if self.description is not None:
            resp["description"] = self.description
        if self.event_subscriptions:
            resp["eventSubscriptions"] = self.event_subscriptions
        if self.permission_model:
            resp["permissionModel"] = self.permission_model
        if self.policy_arn:
            resp["policyArn"] = self.policy_arn
        return resp


class Resource:
    def __init__(
        self,
        logical_resource_id: dict[str, Any],
        physical_resource_id: str,
        resource_type: str,
        components: list[AppComponent],
        resource_name: Optional[str] = None,
        additional_info: Optional[dict[str, list[str]]] = None,
        excluded: bool = False,
    ):
        self.logical_resource_id = logical_resource_id
        self.physical_resource_id = physical_resource_id
        self.resource_type = resource_type
        self.components = components
        self.resource_name = resource_name or logical_resource_id.get("identifier", "")
        self.additional_info = additional_info or {}
        self.excluded = excluded

    def to_json(self) -> dict[str, Any]:
        resp: dict[str, Any] = {
            "appComponents": [c.to_json() for c in self.components],
            "resourceType": self.resource_type,
            "logicalResourceId": self.logical_resource_id,
            "physicalResourceId": {"identifier": self.physical_resource_id},
            "resourceName": self.resource_name,
        }
        if self.additional_info:
            resp["additionalInfo"] = self.additional_info
        if self.excluded:
            resp["excluded"] = self.excluded
        return resp


class AppVersion(BaseModel):
    def __init__(self, app_arn: str, version_name: Optional[str], identifier: int):
        self.app_arn = app_arn
        self.eks_sources: list[dict[str, Any]] = []
        self.source_arns: list[str] = []
        self.terraform_sources: list[dict[str, str]] = []
        self.app_version = "release" if version_name else "draft"
        self.identifier = identifier
        self.creation_time = unix_time()
        self.version_name = version_name
        self.app_components: list[AppComponent] = []
        self.status = "Pending"
        self.resources: list[Resource] = []
        self.resource_mappings: list[dict[str, Any]] = []
        self.additional_info: dict[str, list[str]] = {}

    def to_json(self) -> dict[str, Any]:
        resp = {
            "appVersion": self.app_version,
            "creationTime": self.creation_time,
            "identifier": self.identifier,
        }
        if self.version_name:
            resp["versionName"] = self.version_name
        return resp


class Policy(BaseModel):
    def __init__(
        self,
        backend: "ResilienceHubBackend",
        policy: dict[str, dict[str, int]],
        policy_name: str,
        data_location_constraint: str,
        policy_description: str,
        tier: str,
    ):
        self.arn = f"arn:{get_partition(backend.region_name)}:resiliencehub:{backend.region_name}:{backend.account_id}:resiliency-policy/{mock_random.uuid4()}"
        self.backend = backend
        self.data_location_constraint = data_location_constraint
        self.creation_time = unix_time()
        self.policy = policy
        self.policy_description = policy_description
        self.policy_name = policy_name
        self.tier = tier

    def to_json(self) -> dict[str, Any]:
        resp = {
            "creationTime": self.creation_time,
            "policy": self.policy,
            "policyArn": self.arn,
            "policyName": self.policy_name,
            "tags": self.backend.list_tags_for_resource(self.arn),
            "tier": self.tier,
        }
        if self.data_location_constraint:
            resp["dataLocationConstraint"] = self.data_location_constraint
        if self.policy_description:
            resp["policyDescription"] = self.policy_description
        return resp


class AppAssessment(BaseModel):
    def __init__(
        self,
        backend: "ResilienceHubBackend",
        app_arn: str,
        app_version: str,
        assessment_name: str,
    ):
        self.backend = backend
        self.arn = f"arn:{get_partition(backend.region_name)}:resiliencehub:{backend.region_name}:{backend.account_id}:app-assessment/{mock_random.uuid4()}"
        self.app_arn = app_arn
        self.app_version = app_version
        self.assessment_name = assessment_name
        self.assessment_status = "Success"
        self.compliance_status = "PolicyBreached"
        self.creation_time = unix_time()
        self.end_time = unix_time()
        self.invoker = "User"
        self.cost = {}
        self.compliance = {}
        self.policy = {}
        self.resilience_score = {
            "disruptionScore": {},
            "score": 0.0,
        }
        self.resource_errors_count = 0
        # Store recommendation data
        self.alarm_recommendations: list[dict[str, Any]] = []
        self.sop_recommendations: list[dict[str, Any]] = []
        self.test_recommendations: list[dict[str, Any]] = []
        self.component_compliances: list[dict[str, Any]] = []
        self.component_recommendations: list[dict[str, Any]] = []
        self.compliance_drifts: list[dict[str, Any]] = []
        self.resource_drifts: list[dict[str, Any]] = []

    def to_json(self) -> dict[str, Any]:
        resp: dict[str, Any] = {
            "appArn": self.app_arn,
            "appVersion": self.app_version,
            "assessmentArn": self.arn,
            "assessmentName": self.assessment_name,
            "assessmentStatus": self.assessment_status,
            "complianceStatus": self.compliance_status,
            "cost": self.cost,
            "compliance": self.compliance,
            "creationTime": self.creation_time,
            "endTime": self.end_time,
            "invoker": self.invoker,
            "policy": self.policy,
            "resilienceScore": self.resilience_score,
            "resourceErrorsCount": self.resource_errors_count,
            "tags": self.backend.list_tags_for_resource(self.arn),
        }
        return resp

    def to_summary(self) -> dict[str, Any]:
        return {
            "appArn": self.app_arn,
            "appVersion": self.app_version,
            "assessmentArn": self.arn,
            "assessmentName": self.assessment_name,
            "assessmentStatus": self.assessment_status,
            "complianceStatus": self.compliance_status,
            "cost": self.cost,
            "creationTime": self.creation_time,
            "endTime": self.end_time,
            "invoker": self.invoker,
            "resilienceScore": self.resilience_score.get("score", 0.0),
        }


class RecommendationTemplate(BaseModel):
    def __init__(
        self,
        backend: "ResilienceHubBackend",
        assessment_arn: str,
        name: str,
        bucket_name: Optional[str] = None,
        fmt: Optional[str] = None,
        recommendation_ids: Optional[list[str]] = None,
        recommendation_types: Optional[list[str]] = None,
    ):
        self.backend = backend
        self.arn = f"arn:{get_partition(backend.region_name)}:resiliencehub:{backend.region_name}:{backend.account_id}:recommendation-template/{mock_random.uuid4()}"
        self.assessment_arn = assessment_arn
        self.name = name
        self.bucket_name = bucket_name
        self.format = fmt or "CfnYaml"
        self.recommendation_ids = recommendation_ids or []
        self.recommendation_types = recommendation_types or [
            "Alarm",
            "Sop",
            "Test",
        ]
        self.status = "Success"
        self.start_time = unix_time()
        self.end_time = unix_time()
        self.templates_location = {
            "bucket": bucket_name or f"resiliencehub-{backend.region_name}-{backend.account_id}",
            "prefix": f"recommendations/{mock_random.uuid4()}",
        }

    def to_json(self) -> dict[str, Any]:
        resp: dict[str, Any] = {
            "assessmentArn": self.assessment_arn,
            "endTime": self.end_time,
            "format": self.format,
            "name": self.name,
            "recommendationTemplateArn": self.arn,
            "recommendationTypes": self.recommendation_types,
            "startTime": self.start_time,
            "status": self.status,
            "tags": self.backend.list_tags_for_resource(self.arn),
            "templatesLocation": self.templates_location,
        }
        if self.recommendation_ids:
            resp["recommendationIds"] = self.recommendation_ids
        return resp


class ResilienceHubBackend(BaseBackend):
    def __init__(self, region_name: str, account_id: str):
        super().__init__(region_name, account_id)
        self.apps: dict[str, App] = {}
        self.policies: dict[str, Policy] = {}
        self.assessments: dict[str, AppAssessment] = {}
        self.recommendation_templates: dict[str, RecommendationTemplate] = {}
        self.tagger = TaggingService()
        self.metrics_exports: dict[str, dict[str, Any]] = {}
        self.resource_grouping_tasks: dict[str, dict[str, Any]] = {}

        self.app_assessments_queue: list[list[dict[str, Any]]] = []
        self.app_assessments_results: dict[str, list[dict[str, Any]]] = {}

    def create_app(
        self,
        assessment_schedule: str,
        description: str,
        event_subscriptions: list[dict[str, Any]],
        name: str,
        permission_model: dict[str, Any],
        policy_arn: str,
        tags: dict[str, str],
    ) -> App:
        """
        The ClientToken-parameter is not yet implemented
        """
        app = App(
            backend=self,
            assessment_schedule=assessment_schedule,
            description=description,
            event_subscriptions=event_subscriptions,
            name=name,
            permission_model=permission_model,
            policy_arn=policy_arn,
        )
        self.apps[app.arn] = app
        self.tag_resource(app.arn, tags)
        return app

    def update_app(
        self,
        app_arn: str,
        assessment_schedule: Optional[str],
        clear_resiliency_policy_arn: bool,
        description: Optional[str],
        event_subscriptions: Optional[list[dict[str, Any]]],
        permission_model: Optional[dict[str, Any]],
        policy_arn: Optional[str],
    ) -> App:
        app = self.describe_app(app_arn)
        if assessment_schedule is not None:
            app.assessment_schedule = assessment_schedule
        if description is not None:
            app.description = description
        if event_subscriptions is not None:
            app.event_subscriptions = event_subscriptions
        if permission_model is not None:
            app.permission_model = permission_model
        if clear_resiliency_policy_arn:
            app.policy_arn = ""
        elif policy_arn is not None:
            app.policy_arn = policy_arn
        return app

    def delete_app(self, app_arn: str) -> str:
        if app_arn not in self.apps:
            raise AppNotFound(app_arn)
        del self.apps[app_arn]
        return app_arn

    def create_resiliency_policy(
        self,
        data_location_constraint: str,
        policy: dict[str, Any],
        policy_description: str,
        policy_name: str,
        tags: dict[str, str],
        tier: str,
    ) -> Policy:
        """
        The ClientToken-parameter is not yet implemented
        """
        pol = Policy(
            backend=self,
            data_location_constraint=data_location_constraint,
            policy=policy,
            policy_description=policy_description,
            policy_name=policy_name,
            tier=tier,
        )
        self.policies[pol.arn] = pol
        self.tag_resource(pol.arn, tags)
        return pol

    def update_resiliency_policy(
        self,
        policy_arn: str,
        data_location_constraint: Optional[str],
        policy: Optional[dict[str, Any]],
        policy_description: Optional[str],
        policy_name: Optional[str],
        tier: Optional[str],
    ) -> Policy:
        pol = self.describe_resiliency_policy(policy_arn)
        if data_location_constraint is not None:
            pol.data_location_constraint = data_location_constraint
        if policy is not None:
            pol.policy = policy
        if policy_description is not None:
            pol.policy_description = policy_description
        if policy_name is not None:
            pol.policy_name = policy_name
        if tier is not None:
            pol.tier = tier
        return pol

    def delete_resiliency_policy(self, policy_arn: str) -> str:
        if policy_arn not in self.policies:
            raise ResiliencyPolicyNotFound(policy_arn)
        del self.policies[policy_arn]
        return policy_arn

    @paginate(PAGINATION_MODEL)
    def list_apps(self, app_arn: str, name: str, reverse_order: bool) -> list[App]:
        """
        The FromAssessmentTime/ToAssessmentTime-parameters are not yet implemented
        """
        if name:
            app_summaries = [a for a in self.apps.values() if a.name == name]
        elif app_arn:
            app_summaries = [self.apps[app_arn]]
        else:
            app_summaries = list(self.apps.values())
        if reverse_order:
            app_summaries.reverse()
        return app_summaries

    def list_app_assessments(self, request_identifier: str) -> list[dict[str, Any]]:
        """
        Moto will not actually execute any assessments, so this operation will return an empty list by default.
        You can use a dedicated API to override this, by configuring a queue of expected results.

        A request to `list_app_assessments` will take the first result from that queue, with subsequent calls with the same parameters returning the same result.

        Calling `list_app_assessments` with a different set of parameters will return the second result from that queue - and so on, or an empty list of the queue is empty.

        Configure this queue by making an HTTP request to `/moto-api/static/resilience-hub-assessments/response`. An example invocation looks like this:

        .. sourcecode:: python

            summary1 = {"appArn": "app_arn1", "appVersion": "some version", ...}
            summary2 = {"appArn": "app_arn2", ...}
            results = {"results": [[summary1, summary2], [summary2]], "region": "us-east-1"}
            resp = requests.post(
                "http://motoapi.amazonaws.com/moto-api/static/resilience-hub-assessments/response",
                json=results,
            )

            assert resp.status_code == 201

            client = boto3.client("lambda", region_name="us-east-1")
            # First result
            resp = client.list_app_assessments() # [summary1, summary2]
            # Second result
            resp = client.list_app_assessments(assessmentStatus="Pending") # [summary2]

        If you're using MotoServer, make sure to make this request to where MotoServer is running:

        .. sourcecode:: python

            http://localhost:5000/moto-api/static/resilience-hub-assessments/response

        """
        if request_identifier in self.app_assessments_results:
            return self.app_assessments_results[request_identifier]
        if self.app_assessments_queue:
            self.app_assessments_results[request_identifier] = (
                self.app_assessments_queue.pop(0)
            )
            return self.app_assessments_results[request_identifier]
        # Also return summaries from assessments created via start_app_assessment
        return [a.to_summary() for a in self.assessments.values()]

    def describe_app(self, app_arn: str) -> App:
        if app_arn not in self.apps:
            raise AppNotFound(app_arn)
        return self.apps[app_arn]

    @paginate(pagination_model=PAGINATION_MODEL)
    def list_resiliency_policies(self, policy_name: str) -> list[Policy]:
        if policy_name:
            return [p for p in self.policies.values() if p.policy_name == policy_name]
        return list(self.policies.values())

    def describe_resiliency_policy(self, policy_arn: str) -> Policy:
        if policy_arn not in self.policies:
            raise ResiliencyPolicyNotFound(policy_arn)
        return self.policies[policy_arn]

    def tag_resource(self, resource_arn: str, tags: dict[str, str]) -> None:
        self.tagger.tag_resource(
            resource_arn, TaggingService.convert_dict_to_tags_input(tags)
        )

    def untag_resource(self, resource_arn: str, tag_keys: list[str]) -> None:
        self.tagger.untag_resource_using_names(resource_arn, tag_keys)

    def list_tags_for_resource(self, resource_arn: str) -> dict[str, str]:
        return self.tagger.get_tag_dict_for_resource(resource_arn)

    def import_resources_to_draft_app_version(
        self,
        app_arn: str,
        eks_sources: list[dict[str, Any]],
        source_arns: list[str],
        terraform_sources: list[dict[str, str]],
    ) -> AppVersion:
        app = self.describe_app(app_arn)
        app_version = app.get_version("draft")

        app_version.eks_sources.extend(eks_sources)
        app_version.source_arns.extend(source_arns)
        app_version.terraform_sources.extend(terraform_sources)

        # Default AppComponent when importing data
        # AWS seems to create other components as well, based on the provided sources
        app_version.app_components.append(
            AppComponent(
                _id="appcommon",
                name="appcommon",
                _type="AWS::ResilienceHub::AppCommonAppComponent",
            )
        )
        return app_version

    def create_app_version_app_component(
        self, app_arn: str, name: str, _type: str
    ) -> AppComponent:
        app = self.describe_app(app_arn)
        app_version = app.get_version("draft")
        component = AppComponent(_id=name, name=name, _type=_type)
        app_version.app_components.append(component)
        return component

    def update_app_version_app_component(
        self,
        app_arn: str,
        component_id: str,
        additional_info: Optional[dict[str, list[str]]],
        name: Optional[str],
        _type: Optional[str],
    ) -> AppComponent:
        app = self.describe_app(app_arn)
        app_version = app.get_version("draft")
        for component in app_version.app_components:
            if component.id == component_id:
                if name is not None:
                    component.name = name
                if _type is not None:
                    component.type = _type
                if additional_info is not None:
                    component.additional_info = additional_info
                return component
        raise AppComponentNotFound(component_id)

    def delete_app_version_app_component(
        self, app_arn: str, component_id: str
    ) -> Optional[AppComponent]:
        app = self.describe_app(app_arn)
        app_version = app.get_version("draft")
        for idx, component in enumerate(app_version.app_components):
            if component.id == component_id:
                return app_version.app_components.pop(idx)
        raise AppComponentNotFound(component_id)

    def describe_app_version_app_component(
        self, app_arn: str, app_version_name: str, component_id: str
    ) -> AppComponent:
        app = self.describe_app(app_arn)
        version = app.get_version(app_version_name)
        for component in version.app_components:
            if component.id == component_id:
                return component
        raise AppComponentNotFound(component_id)

    def list_app_version_app_components(
        self, app_arn: str, app_version: str
    ) -> list[AppComponent]:
        app = self.describe_app(app_arn)
        return app.get_version(app_version).app_components

    def create_app_version_resource(
        self,
        app_arn: str,
        app_components: list[str],
        logical_resource_id: dict[str, str],
        physical_resource_id: str,
        resource_type: str,
    ) -> Resource:
        app = self.describe_app(app_arn)
        app_version = app.get_version("draft")

        components = [c for c in app_version.app_components if c.id in app_components]

        resource = Resource(
            logical_resource_id=logical_resource_id,
            physical_resource_id=physical_resource_id,
            resource_type=resource_type,
            components=components,
        )
        app_version.resources.append(resource)
        return resource

    def update_app_version_resource(
        self,
        app_arn: str,
        additional_info: Optional[dict[str, list[str]]],
        app_components: Optional[list[str]],
        excluded: Optional[bool],
        logical_resource_id: Optional[dict[str, str]],
        physical_resource_id: Optional[str],
        resource_name: Optional[str],
        resource_type: Optional[str],
    ) -> Resource:
        app = self.describe_app(app_arn)
        app_version = app.get_version("draft")

        # Find resource by physical_resource_id, logical_resource_id, or resource_name
        target = None
        for resource in app_version.resources:
            if physical_resource_id and resource.physical_resource_id == physical_resource_id:
                target = resource
                break
            if resource_name and resource.resource_name == resource_name:
                target = resource
                break
            if (
                logical_resource_id
                and resource.logical_resource_id.get("identifier")
                == logical_resource_id.get("identifier")
            ):
                target = resource
                break

        if target is None:
            raise AppVersionResourceNotFound(resource_name or physical_resource_id or "unknown")

        if additional_info is not None:
            target.additional_info = additional_info
        if app_components is not None:
            target.components = [
                c for c in app_version.app_components if c.id in app_components
            ]
        if excluded is not None:
            target.excluded = excluded
        if logical_resource_id is not None:
            target.logical_resource_id = logical_resource_id
        if physical_resource_id is not None:
            target.physical_resource_id = physical_resource_id
        if resource_name is not None:
            target.resource_name = resource_name
        if resource_type is not None:
            target.resource_type = resource_type
        return target

    def delete_app_version_resource(
        self,
        app_arn: str,
        logical_resource_id: Optional[dict[str, str]],
        physical_resource_id: Optional[str],
        resource_name: Optional[str],
    ) -> Resource:
        app = self.describe_app(app_arn)
        app_version = app.get_version("draft")

        for idx, resource in enumerate(app_version.resources):
            if physical_resource_id and resource.physical_resource_id == physical_resource_id:
                return app_version.resources.pop(idx)
            if resource_name and resource.resource_name == resource_name:
                return app_version.resources.pop(idx)
            if (
                logical_resource_id
                and resource.logical_resource_id.get("identifier")
                == logical_resource_id.get("identifier")
            ):
                return app_version.resources.pop(idx)

        raise AppVersionResourceNotFound(resource_name or physical_resource_id or "unknown")

    def describe_app_version_resource(
        self,
        app_arn: str,
        app_version_name: str,
        logical_resource_id: Optional[dict[str, str]],
        physical_resource_id: Optional[str],
        resource_name: Optional[str],
    ) -> Resource:
        app = self.describe_app(app_arn)
        version = app.get_version(app_version_name)

        for resource in version.resources:
            if physical_resource_id and resource.physical_resource_id == physical_resource_id:
                return resource
            if resource_name and resource.resource_name == resource_name:
                return resource
            if (
                logical_resource_id
                and resource.logical_resource_id.get("identifier")
                == logical_resource_id.get("identifier")
            ):
                return resource

        raise AppVersionResourceNotFound(resource_name or physical_resource_id or "unknown")

    def list_app_version_resources(
        self, app_arn: str, app_version: str
    ) -> list[Resource]:
        app = self.describe_app(app_arn)
        return app.get_version(app_version).resources

    def list_app_versions(self, app_arn: str) -> list[AppVersion]:
        app = self.describe_app(app_arn)
        return app.app_versions

    def publish_app_version(self, app_arn: str, version_name: str) -> AppVersion:
        app = self.describe_app(app_arn)
        version = AppVersion(
            app_arn=app_arn, version_name=version_name, identifier=len(app.app_versions)
        )
        for old_version in app.app_versions:
            if old_version.app_version == "release":
                old_version.app_version = str(old_version.identifier)
        app.app_versions.append(version)
        return version

    def describe_app_version(
        self, app_arn: str, app_version_name: str
    ) -> tuple[str, AppVersion]:
        app = self.describe_app(app_arn)
        version = app.get_version(app_version_name)
        return app_arn, version

    def update_app_version(
        self, app_arn: str, additional_info: Optional[dict[str, list[str]]]
    ) -> AppVersion:
        app = self.describe_app(app_arn)
        version = app.get_version("draft")
        if additional_info is not None:
            version.additional_info = additional_info
        return version

    def describe_app_version_template(
        self, app_arn: str, app_version_name: str
    ) -> tuple[str, str, str]:
        app = self.describe_app(app_arn)
        app.get_version(app_version_name)  # Validate version exists
        body = app.app_template_body or json.dumps({"resources": [], "appComponents": []})
        return app_arn, body, app_version_name

    def put_draft_app_version_template(
        self, app_arn: str, app_template_body: str
    ) -> tuple[str, str]:
        app = self.describe_app(app_arn)
        app.get_version("draft")  # Validate draft exists
        app.app_template_body = app_template_body
        return app_arn, "draft"

    def describe_draft_app_version_resources_import_status(
        self, app_arn: str
    ) -> dict[str, Any]:
        app = self.describe_app(app_arn)
        app.get_version("draft")
        return {
            "appArn": app_arn,
            "appVersion": "draft",
            "status": "Success",
            "statusChangeTime": unix_time(),
        }

    def describe_app_version_resources_resolution_status(
        self, app_arn: str, app_version_name: str, resolution_id: Optional[str]
    ) -> dict[str, Any]:
        app = self.describe_app(app_arn)
        app.get_version(app_version_name)
        return {
            "appArn": app_arn,
            "appVersion": app_version_name,
            "resolutionId": resolution_id or str(mock_random.uuid4()),
            "status": "Success",
        }

    def resolve_app_version_resources(
        self, app_arn: str, app_version_name: str
    ) -> dict[str, Any]:
        app = self.describe_app(app_arn)
        app.get_version(app_version_name)
        resolution_id = str(mock_random.uuid4())
        return {
            "appArn": app_arn,
            "appVersion": app_version_name,
            "resolutionId": resolution_id,
            "status": "Success",
        }

    # --- Assessment operations ---

    def start_app_assessment(
        self,
        app_arn: str,
        app_version: str,
        assessment_name: str,
        tags: Optional[dict[str, str]],
    ) -> AppAssessment:
        self.describe_app(app_arn)
        assessment = AppAssessment(
            backend=self,
            app_arn=app_arn,
            app_version=app_version,
            assessment_name=assessment_name,
        )
        self.assessments[assessment.arn] = assessment
        if tags:
            self.tag_resource(assessment.arn, tags)
        return assessment

    def describe_app_assessment(self, assessment_arn: str) -> AppAssessment:
        if assessment_arn not in self.assessments:
            raise AppAssessmentNotFound(assessment_arn)
        return self.assessments[assessment_arn]

    def delete_app_assessment(self, assessment_arn: str) -> tuple[str, str]:
        if assessment_arn not in self.assessments:
            raise AppAssessmentNotFound(assessment_arn)
        del self.assessments[assessment_arn]
        return assessment_arn, "Success"

    # --- Recommendation template operations ---

    def create_recommendation_template(
        self,
        assessment_arn: str,
        name: str,
        bucket_name: Optional[str],
        fmt: Optional[str],
        recommendation_ids: Optional[list[str]],
        recommendation_types: Optional[list[str]],
        tags: Optional[dict[str, str]],
    ) -> RecommendationTemplate:
        template = RecommendationTemplate(
            backend=self,
            assessment_arn=assessment_arn,
            name=name,
            bucket_name=bucket_name,
            fmt=fmt,
            recommendation_ids=recommendation_ids,
            recommendation_types=recommendation_types,
        )
        self.recommendation_templates[template.arn] = template
        if tags:
            self.tag_resource(template.arn, tags)
        return template

    def delete_recommendation_template(self, template_arn: str) -> tuple[str, str]:
        if template_arn not in self.recommendation_templates:
            raise RecommendationTemplateNotFound(template_arn)
        del self.recommendation_templates[template_arn]
        return template_arn, "Success"

    @paginate(pagination_model=PAGINATION_MODEL)
    def list_recommendation_templates(
        self,
        assessment_arn: Optional[str],
        name: Optional[str],
        recommendation_template_arn: Optional[str],
        status: Optional[list[str]],
        reverse_order: bool = False,
    ) -> list[RecommendationTemplate]:
        templates = list(self.recommendation_templates.values())
        if assessment_arn:
            templates = [t for t in templates if t.assessment_arn == assessment_arn]
        if name:
            templates = [t for t in templates if t.name == name]
        if recommendation_template_arn:
            templates = [t for t in templates if t.arn == recommendation_template_arn]
        if status:
            templates = [t for t in templates if t.status in status]
        if reverse_order:
            templates.reverse()
        return templates

    # --- Resource mapping operations ---

    def add_draft_app_version_resource_mappings(
        self, app_arn: str, resource_mappings: list[dict[str, Any]]
    ) -> tuple[str, str, list[dict[str, Any]]]:
        app = self.describe_app(app_arn)
        version = app.get_version("draft")
        version.resource_mappings.extend(resource_mappings)
        return app_arn, "draft", version.resource_mappings

    def remove_draft_app_version_resource_mappings(
        self,
        app_arn: str,
        app_registry_app_names: Optional[list[str]],
        eks_source_names: Optional[list[str]],
        logical_stack_names: Optional[list[str]],
        resource_group_names: Optional[list[str]],
        resource_names: Optional[list[str]],
        terraform_source_names: Optional[list[str]],
    ) -> tuple[str, str]:
        app = self.describe_app(app_arn)
        version = app.get_version("draft")

        names_to_remove: set[str] = set()
        for name_list in [
            app_registry_app_names,
            eks_source_names,
            logical_stack_names,
            resource_group_names,
            resource_names,
            terraform_source_names,
        ]:
            if name_list:
                names_to_remove.update(name_list)

        if names_to_remove:
            version.resource_mappings = [
                m
                for m in version.resource_mappings
                if m.get("resourceName") not in names_to_remove
                and m.get("physicalResourceId", {}).get("identifier") not in names_to_remove
            ]

        return app_arn, "draft"

    @paginate(pagination_model=PAGINATION_MODEL)
    def list_app_version_resource_mappings(
        self, app_arn: str, app_version_name: str
    ) -> list[dict[str, Any]]:
        app = self.describe_app(app_arn)
        version = app.get_version(app_version_name)
        return version.resource_mappings

    # --- Input source operations ---

    def delete_app_input_source(
        self,
        app_arn: str,
        eks_source_cluster_namespace: Optional[dict[str, str]],
        source_arn: Optional[str],
        terraform_source: Optional[dict[str, str]],
    ) -> tuple[str, dict[str, Any]]:
        app = self.describe_app(app_arn)
        removed_source: dict[str, Any] = {}
        if source_arn:
            app.input_sources = [s for s in app.input_sources if s.get("sourceArn") != source_arn]
            removed_source = {"sourceArn": source_arn, "importType": "CFN_STACK"}
        elif eks_source_cluster_namespace:
            removed_source = {
                "eksSourceClusterNamespace": eks_source_cluster_namespace,
                "importType": "EKS",
            }
        elif terraform_source:
            removed_source = {"terraformSource": terraform_source, "importType": "TERRAFORM"}
        return app_arn, removed_source

    @paginate(pagination_model=PAGINATION_MODEL)
    def list_app_input_sources(
        self, app_arn: str, app_version_name: str
    ) -> list[dict[str, Any]]:
        app = self.describe_app(app_arn)
        app.get_version(app_version_name)
        # Build input sources from the draft version's source_arns, eks_sources, terraform_sources
        version = app.get_version(app_version_name)
        sources: list[dict[str, Any]] = []
        for arn in version.source_arns:
            sources.append({"importType": "CFN_STACK", "sourceArn": arn, "resourceCount": 0})
        for eks in version.eks_sources:
            sources.append({"importType": "EKS", "eksSourceClusterNamespace": eks, "resourceCount": 0})
        for tf in version.terraform_sources:
            sources.append({"importType": "TERRAFORM", "terraformSource": tf, "resourceCount": 0})
        sources.extend(app.input_sources)
        return sources

    # --- Assessment-related list operations (return empty lists by default) ---

    @paginate(pagination_model=PAGINATION_MODEL)
    def list_alarm_recommendations(self, assessment_arn: str) -> list[dict[str, Any]]:
        if assessment_arn in self.assessments:
            return self.assessments[assessment_arn].alarm_recommendations
        return []

    @paginate(pagination_model=PAGINATION_MODEL)
    def list_sop_recommendations(self, assessment_arn: str) -> list[dict[str, Any]]:
        if assessment_arn in self.assessments:
            return self.assessments[assessment_arn].sop_recommendations
        return []

    @paginate(pagination_model=PAGINATION_MODEL)
    def list_test_recommendations(self, assessment_arn: str) -> list[dict[str, Any]]:
        if assessment_arn in self.assessments:
            return self.assessments[assessment_arn].test_recommendations
        return []

    @paginate(pagination_model=PAGINATION_MODEL)
    def list_app_component_compliances(
        self, assessment_arn: str
    ) -> list[dict[str, Any]]:
        if assessment_arn in self.assessments:
            return self.assessments[assessment_arn].component_compliances
        return []

    @paginate(pagination_model=PAGINATION_MODEL)
    def list_app_component_recommendations(
        self, assessment_arn: str
    ) -> list[dict[str, Any]]:
        if assessment_arn in self.assessments:
            return self.assessments[assessment_arn].component_recommendations
        return []

    @paginate(pagination_model=PAGINATION_MODEL)
    def list_app_assessment_compliance_drifts(
        self, assessment_arn: str
    ) -> list[dict[str, Any]]:
        if assessment_arn in self.assessments:
            return self.assessments[assessment_arn].compliance_drifts
        return []

    @paginate(pagination_model=PAGINATION_MODEL)
    def list_app_assessment_resource_drifts(
        self, assessment_arn: str
    ) -> list[dict[str, Any]]:
        if assessment_arn in self.assessments:
            return self.assessments[assessment_arn].resource_drifts
        return []

    @paginate(pagination_model=PAGINATION_MODEL)
    def list_unsupported_app_version_resources(
        self, app_arn: str, app_version_name: str, resolution_id: Optional[str]
    ) -> list[dict[str, Any]]:
        self.describe_app(app_arn)
        # In the mock, we don't track unsupported resources - return empty
        return []

    @paginate(pagination_model=PAGINATION_MODEL)
    def list_suggested_resiliency_policies(self) -> list[Policy]:
        # Return empty list - suggested policies are AWS-managed
        return []

    # --- Metrics operations ---

    def start_metrics_export(self, bucket_name: str) -> tuple[str, str]:
        export_id = str(mock_random.uuid4())
        self.metrics_exports[export_id] = {
            "metricsExportId": export_id,
            "status": "Success",
            "exportLocation": {
                "bucket": bucket_name,
                "prefix": f"resiliencehub-metrics/{export_id}",
            },
        }
        return export_id, "Success"

    def describe_metrics_export(self, metrics_export_id: str) -> dict[str, Any]:
        if metrics_export_id in self.metrics_exports:
            return self.metrics_exports[metrics_export_id]
        return {
            "metricsExportId": metrics_export_id,
            "status": "Failed",
            "errorMessage": "Export not found",
        }

    def list_metrics(
        self,
        conditions: Optional[list[dict[str, Any]]],
        data_source: Optional[str],
        fields: Optional[list[dict[str, str]]],
        max_results: Optional[int],
        next_token: Optional[str],
        sorts: Optional[list[dict[str, str]]],
    ) -> tuple[list[list[Any]], Optional[str]]:
        # Return empty metrics
        return [], None

    # --- Resource grouping operations ---

    def start_resource_grouping_recommendation_task(
        self, app_arn: str
    ) -> dict[str, Any]:
        self.describe_app(app_arn)
        grouping_id = str(mock_random.uuid4())
        task = {
            "appArn": app_arn,
            "groupingId": grouping_id,
            "status": "Success",
        }
        self.resource_grouping_tasks[grouping_id] = task
        return task

    def describe_resource_grouping_recommendation_task(
        self, app_arn: str, grouping_id: Optional[str]
    ) -> dict[str, Any]:
        self.describe_app(app_arn)
        if grouping_id and grouping_id in self.resource_grouping_tasks:
            return self.resource_grouping_tasks[grouping_id]
        return {
            "groupingId": grouping_id or str(mock_random.uuid4()),
            "status": "Success",
        }

    @paginate(pagination_model=PAGINATION_MODEL)
    def list_resource_grouping_recommendations(
        self, app_arn: str
    ) -> list[dict[str, Any]]:
        self.describe_app(app_arn)
        return []

    def accept_resource_grouping_recommendations(
        self, app_arn: str, entries: list[dict[str, Any]]
    ) -> tuple[str, list[dict[str, Any]]]:
        self.describe_app(app_arn)
        # All entries succeed
        return app_arn, []

    def reject_resource_grouping_recommendations(
        self, app_arn: str, entries: list[dict[str, Any]]
    ) -> tuple[str, list[dict[str, Any]]]:
        self.describe_app(app_arn)
        # All entries succeed
        return app_arn, []

    # --- Batch operations ---

    def batch_update_recommendation_status(
        self, app_arn: str, request_entries: list[dict[str, Any]]
    ) -> tuple[str, list[dict[str, Any]], list[dict[str, Any]]]:
        self.describe_app(app_arn)
        successful = []
        for entry in request_entries:
            successful.append(
                {
                    "entryId": entry.get("entryId", ""),
                    "excluded": entry.get("excluded", False),
                    "excludeReason": entry.get("excludeReason", ""),
                    "item": entry.get("item", {}),
                    "referenceId": entry.get("referenceId", ""),
                }
            )
        return app_arn, [], successful


resiliencehub_backends = BackendDict(ResilienceHubBackend, "resiliencehub")
