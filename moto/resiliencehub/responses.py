import json
from urllib.parse import unquote

from moto.core.responses import BaseResponse

from .exceptions import ValidationException
from .models import ResilienceHubBackend, resiliencehub_backends


class ResilienceHubResponse(BaseResponse):
    def __init__(self) -> None:
        super().__init__(service_name="resiliencehub")

    @property
    def resiliencehub_backend(self) -> ResilienceHubBackend:
        return resiliencehub_backends[self.current_account][self.region]

    def create_app(self) -> str:
        params = json.loads(self.body)
        assessment_schedule = params.get("assessmentSchedule")
        description = params.get("description")
        event_subscriptions = params.get("eventSubscriptions")
        name = params.get("name")
        permission_model = params.get("permissionModel")
        policy_arn = params.get("policyArn")
        tags = params.get("tags")
        app = self.resiliencehub_backend.create_app(
            assessment_schedule=assessment_schedule,
            description=description,
            event_subscriptions=event_subscriptions,
            name=name,
            permission_model=permission_model,
            policy_arn=policy_arn,
            tags=tags,
        )
        return json.dumps({"app": app.to_json()})

    def update_app(self) -> str:
        params = json.loads(self.body)
        app = self.resiliencehub_backend.update_app(
            app_arn=params.get("appArn"),
            assessment_schedule=params.get("assessmentSchedule"),
            clear_resiliency_policy_arn=params.get("clearResiliencyPolicyArn", False),
            description=params.get("description"),
            event_subscriptions=params.get("eventSubscriptions"),
            permission_model=params.get("permissionModel"),
            policy_arn=params.get("policyArn"),
        )
        return json.dumps({"app": app.to_json()})

    def delete_app(self) -> str:
        params = json.loads(self.body)
        app_arn = self.resiliencehub_backend.delete_app(
            app_arn=params.get("appArn"),
        )
        return json.dumps({"appArn": app_arn})

    def create_resiliency_policy(self) -> str:
        params = json.loads(self.body)
        data_location_constraint = params.get("dataLocationConstraint")
        policy = params.get("policy")
        policy_description = params.get("policyDescription")
        policy_name = params.get("policyName")
        tags = params.get("tags")
        tier = params.get("tier")

        required_policy_types = ["Software", "Hardware", "AZ"]
        all_policy_types = required_policy_types + ["Region"]
        if any(p_type not in all_policy_types for p_type in policy.keys()):
            raise ValidationException(
                "1 validation error detected: Value at 'policy' failed to satisfy constraint: Map keys must satisfy constraint: [Member must satisfy enum value set: [Software, Hardware, Region, AZ]]"
            )
        for required_key in required_policy_types:
            if required_key not in policy.keys():
                raise ValidationException(
                    f"FailureType {required_key.upper()} does not exist"
                )

        policy = self.resiliencehub_backend.create_resiliency_policy(
            data_location_constraint=data_location_constraint,
            policy=policy,
            policy_description=policy_description,
            policy_name=policy_name,
            tags=tags,
            tier=tier,
        )
        return json.dumps({"policy": policy.to_json()})

    def update_resiliency_policy(self) -> str:
        params = json.loads(self.body)
        policy = self.resiliencehub_backend.update_resiliency_policy(
            policy_arn=params.get("policyArn"),
            data_location_constraint=params.get("dataLocationConstraint"),
            policy=params.get("policy"),
            policy_description=params.get("policyDescription"),
            policy_name=params.get("policyName"),
            tier=params.get("tier"),
        )
        return json.dumps({"policy": policy.to_json()})

    def delete_resiliency_policy(self) -> str:
        params = json.loads(self.body)
        policy_arn = self.resiliencehub_backend.delete_resiliency_policy(
            policy_arn=params.get("policyArn"),
        )
        return json.dumps({"policyArn": policy_arn})

    def list_apps(self) -> str:
        params = self._get_params()
        app_arn = params.get("appArn")
        max_results = int(params.get("maxResults", 100))
        name = params.get("name")
        next_token = params.get("nextToken")
        reverse_order = params.get("reverseOrder") == "true"
        app_summaries, next_token = self.resiliencehub_backend.list_apps(
            app_arn=app_arn,
            max_results=max_results,
            name=name,
            next_token=next_token,
            reverse_order=reverse_order,
        )
        return json.dumps(
            {
                "appSummaries": [a.to_json() for a in app_summaries],
                "nextToken": next_token,
            }
        )

    def list_app_assessments(self) -> str:
        supported_params = [
            "appArn",
            "assessmentName",
            "assessmentStatus",
            "complianceStatus",
            "invoker",
            "maxResults",
            "nextToken",
            "reverseOrder",
        ]
        provided_params = [p for p in self.querystring.keys() if p in supported_params]
        request_identifier = json.dumps(
            {key: self.querystring[key] for key in sorted(provided_params)}
        )
        summaries = self.resiliencehub_backend.list_app_assessments(
            request_identifier=request_identifier,
        )
        return json.dumps({"assessmentSummaries": summaries})

    def describe_app(self) -> str:
        params = json.loads(self.body)
        app_arn = params.get("appArn")
        app = self.resiliencehub_backend.describe_app(
            app_arn=app_arn,
        )
        return json.dumps({"app": app.to_json()})

    def list_resiliency_policies(self) -> str:
        params = self._get_params()
        max_results = int(params.get("maxResults", 100))
        next_token = params.get("nextToken")
        policy_name = params.get("policyName")
        (
            resiliency_policies,
            next_token,
        ) = self.resiliencehub_backend.list_resiliency_policies(
            max_results=max_results,
            next_token=next_token,
            policy_name=policy_name,
        )
        policies = [p.to_json() for p in resiliency_policies]
        return json.dumps({"nextToken": next_token, "resiliencyPolicies": policies})

    def describe_resiliency_policy(self) -> str:
        params = json.loads(self.body)
        policy_arn = params.get("policyArn")
        policy = self.resiliencehub_backend.describe_resiliency_policy(
            policy_arn=policy_arn,
        )
        return json.dumps({"policy": policy.to_json()})

    def tag_resource(self) -> str:
        params = json.loads(self.body)
        resource_arn = unquote(self.parsed_url.path.split("/tags/")[-1])
        tags = params.get("tags")
        self.resiliencehub_backend.tag_resource(
            resource_arn=resource_arn,
            tags=tags,
        )
        return "{}"

    def untag_resource(self) -> str:
        resource_arn = unquote(self.parsed_url.path.split("/tags/")[-1])
        tag_keys = self.querystring.get("tagKeys", [])
        self.resiliencehub_backend.untag_resource(
            resource_arn=resource_arn,
            tag_keys=tag_keys,
        )
        return "{}"

    def list_tags_for_resource(self) -> str:
        resource_arn = unquote(self.uri.split("/tags/")[-1])
        tags = self.resiliencehub_backend.list_tags_for_resource(
            resource_arn=resource_arn,
        )
        return json.dumps({"tags": tags})

    def import_resources_to_draft_app_version(self) -> str:
        app_arn = self._get_param("appArn")
        eks_sources = self._get_param("eksSources")
        source_arns = self._get_param("sourceArns")
        terraform_sources = self._get_param("terraformSources")

        app_version = self.resiliencehub_backend.import_resources_to_draft_app_version(
            app_arn=app_arn,
            eks_sources=eks_sources,
            source_arns=source_arns,
            terraform_sources=terraform_sources,
        )
        return json.dumps(
            {
                "appArn": app_version.app_arn,
                "appVersion": app_version.version_name,
                "eksSources": eks_sources,
                "sourceArns": source_arns,
                "status": app_version.status,
                "terraformSources": terraform_sources,
            }
        )

    def list_app_version_app_components(self) -> str:
        app_arn = self._get_param("appArn")
        app_version = self._get_param("appVersion")
        components = self.resiliencehub_backend.list_app_version_app_components(
            app_arn, app_version
        )
        return json.dumps(
            {
                "appArn": app_arn,
                "appVersion": app_version,
                "appComponents": [c.to_json() for c in components],
            }
        )

    def create_app_version_app_component(self) -> str:
        app_arn = self._get_param("appArn")
        name = self._get_param("name")
        _type = self._get_param("type")
        component = self.resiliencehub_backend.create_app_version_app_component(
            app_arn=app_arn,
            name=name,
            _type=_type,
        )
        return json.dumps(
            {
                "appArn": app_arn,
                "appComponent": component.to_json(),
                "appVersion": "draft",
            }
        )

    def update_app_version_app_component(self) -> str:
        params = json.loads(self.body)
        component = self.resiliencehub_backend.update_app_version_app_component(
            app_arn=params.get("appArn"),
            component_id=params.get("id"),
            additional_info=params.get("additionalInfo"),
            name=params.get("name"),
            _type=params.get("type"),
        )
        return json.dumps(
            {
                "appArn": params.get("appArn"),
                "appComponent": component.to_json(),
                "appVersion": "draft",
            }
        )

    def delete_app_version_app_component(self) -> str:
        params = json.loads(self.body)
        component = self.resiliencehub_backend.delete_app_version_app_component(
            app_arn=params.get("appArn"),
            component_id=params.get("id"),
        )
        return json.dumps(
            {
                "appArn": params.get("appArn"),
                "appComponent": component.to_json() if component else None,
                "appVersion": "draft",
            }
        )

    def describe_app_version_app_component(self) -> str:
        params = json.loads(self.body)
        component = self.resiliencehub_backend.describe_app_version_app_component(
            app_arn=params.get("appArn"),
            app_version_name=params.get("appVersion"),
            component_id=params.get("id"),
        )
        return json.dumps(
            {
                "appArn": params.get("appArn"),
                "appComponent": component.to_json(),
                "appVersion": params.get("appVersion"),
            }
        )

    def create_app_version_resource(self) -> str:
        app_arn = self._get_param("appArn")
        app_components = self._get_param("appComponents")
        logical_resource_id = self._get_param("logicalResourceId")
        physical_resource_id = self._get_param("physicalResourceId")
        resource_type = self._get_param("resourceType")

        resource = self.resiliencehub_backend.create_app_version_resource(
            app_arn=app_arn,
            app_components=app_components,
            logical_resource_id=logical_resource_id,
            physical_resource_id=physical_resource_id,
            resource_type=resource_type,
        )

        return json.dumps(
            {
                "appArn": app_arn,
                "appVersion": "draft",
                "physicalResource": resource.to_json(),
            }
        )

    def update_app_version_resource(self) -> str:
        params = json.loads(self.body)
        resource = self.resiliencehub_backend.update_app_version_resource(
            app_arn=params.get("appArn"),
            additional_info=params.get("additionalInfo"),
            app_components=params.get("appComponents"),
            excluded=params.get("excluded"),
            logical_resource_id=params.get("logicalResourceId"),
            physical_resource_id=params.get("physicalResourceId"),
            resource_name=params.get("resourceName"),
            resource_type=params.get("resourceType"),
        )
        return json.dumps(
            {
                "appArn": params.get("appArn"),
                "appVersion": "draft",
                "physicalResource": resource.to_json(),
            }
        )

    def delete_app_version_resource(self) -> str:
        params = json.loads(self.body)
        resource = self.resiliencehub_backend.delete_app_version_resource(
            app_arn=params.get("appArn"),
            logical_resource_id=params.get("logicalResourceId"),
            physical_resource_id=params.get("physicalResourceId"),
            resource_name=params.get("resourceName"),
        )
        return json.dumps(
            {
                "appArn": params.get("appArn"),
                "appVersion": "draft",
                "physicalResource": resource.to_json(),
            }
        )

    def describe_app_version_resource(self) -> str:
        params = json.loads(self.body)
        resource = self.resiliencehub_backend.describe_app_version_resource(
            app_arn=params.get("appArn"),
            app_version_name=params.get("appVersion"),
            logical_resource_id=params.get("logicalResourceId"),
            physical_resource_id=params.get("physicalResourceId"),
            resource_name=params.get("resourceName"),
        )
        return json.dumps(
            {
                "appArn": params.get("appArn"),
                "appVersion": params.get("appVersion"),
                "physicalResource": resource.to_json(),
            }
        )

    def list_app_version_resources(self) -> str:
        app_arn = self._get_param("appArn")
        app_version = self._get_param("appVersion")
        resources = self.resiliencehub_backend.list_app_version_resources(
            app_arn, app_version
        )
        return json.dumps({"physicalResources": [r.to_json() for r in resources]})

    def list_app_versions(self) -> str:
        app_arn = self._get_param("appArn")
        versions = self.resiliencehub_backend.list_app_versions(app_arn)
        return json.dumps({"appVersions": [v.to_json() for v in versions]})

    def publish_app_version(self) -> str:
        app_arn = self._get_param("appArn")
        version_name = self._get_param("versionName")
        version = self.resiliencehub_backend.publish_app_version(app_arn, version_name)
        return json.dumps({"appArn": app_arn, **version.to_json()})

    def describe_app_version(self) -> str:
        params = json.loads(self.body)
        app_arn, version = self.resiliencehub_backend.describe_app_version(
            app_arn=params.get("appArn"),
            app_version_name=params.get("appVersion"),
        )
        resp: dict = {
            "appArn": app_arn,
            "appVersion": version.app_version,
        }
        if version.additional_info:
            resp["additionalInfo"] = version.additional_info
        return json.dumps(resp)

    def update_app_version(self) -> str:
        params = json.loads(self.body)
        version = self.resiliencehub_backend.update_app_version(
            app_arn=params.get("appArn"),
            additional_info=params.get("additionalInfo"),
        )
        resp: dict = {
            "appArn": params.get("appArn"),
            "appVersion": version.app_version,
        }
        if version.additional_info:
            resp["additionalInfo"] = version.additional_info
        return json.dumps(resp)

    def describe_app_version_template(self) -> str:
        params = json.loads(self.body)
        app_arn, body, app_version = (
            self.resiliencehub_backend.describe_app_version_template(
                app_arn=params.get("appArn"),
                app_version_name=params.get("appVersion"),
            )
        )
        return json.dumps(
            {
                "appArn": app_arn,
                "appTemplateBody": body,
                "appVersion": app_version,
            }
        )

    def put_draft_app_version_template(self) -> str:
        params = json.loads(self.body)
        app_arn, app_version = (
            self.resiliencehub_backend.put_draft_app_version_template(
                app_arn=params.get("appArn"),
                app_template_body=params.get("appTemplateBody"),
            )
        )
        return json.dumps({"appArn": app_arn, "appVersion": app_version})

    def describe_draft_app_version_resources_import_status(self) -> str:
        params = json.loads(self.body)
        result = (
            self.resiliencehub_backend.describe_draft_app_version_resources_import_status(
                app_arn=params.get("appArn"),
            )
        )
        return json.dumps(result)

    def describe_app_version_resources_resolution_status(self) -> str:
        params = json.loads(self.body)
        result = (
            self.resiliencehub_backend.describe_app_version_resources_resolution_status(
                app_arn=params.get("appArn"),
                app_version_name=params.get("appVersion"),
                resolution_id=params.get("resolutionId"),
            )
        )
        return json.dumps(result)

    def resolve_app_version_resources(self) -> str:
        params = json.loads(self.body)
        result = self.resiliencehub_backend.resolve_app_version_resources(
            app_arn=params.get("appArn"),
            app_version_name=params.get("appVersion"),
        )
        return json.dumps(result)

    # --- Assessment operations ---

    def start_app_assessment(self) -> str:
        params = json.loads(self.body)
        assessment = self.resiliencehub_backend.start_app_assessment(
            app_arn=params.get("appArn"),
            app_version=params.get("appVersion"),
            assessment_name=params.get("assessmentName"),
            tags=params.get("tags"),
        )
        return json.dumps({"assessment": assessment.to_json()})

    def describe_app_assessment(self) -> str:
        params = json.loads(self.body)
        assessment = self.resiliencehub_backend.describe_app_assessment(
            assessment_arn=params.get("assessmentArn"),
        )
        return json.dumps({"assessment": assessment.to_json()})

    def delete_app_assessment(self) -> str:
        params = json.loads(self.body)
        assessment_arn, status = self.resiliencehub_backend.delete_app_assessment(
            assessment_arn=params.get("assessmentArn"),
        )
        return json.dumps(
            {"assessmentArn": assessment_arn, "assessmentStatus": status}
        )

    # --- Recommendation template operations ---

    def create_recommendation_template(self) -> str:
        params = json.loads(self.body)
        template = self.resiliencehub_backend.create_recommendation_template(
            assessment_arn=params.get("assessmentArn"),
            name=params.get("name"),
            bucket_name=params.get("bucketName"),
            fmt=params.get("format"),
            recommendation_ids=params.get("recommendationIds"),
            recommendation_types=params.get("recommendationTypes"),
            tags=params.get("tags"),
        )
        return json.dumps({"recommendationTemplate": template.to_json()})

    def delete_recommendation_template(self) -> str:
        params = json.loads(self.body)
        template_arn, status = (
            self.resiliencehub_backend.delete_recommendation_template(
                template_arn=params.get("recommendationTemplateArn"),
            )
        )
        return json.dumps(
            {"recommendationTemplateArn": template_arn, "status": status}
        )

    def list_recommendation_templates(self) -> str:
        params = self._get_params()
        max_results = int(params.get("maxResults", 100))
        next_token = params.get("nextToken")
        templates, next_token = (
            self.resiliencehub_backend.list_recommendation_templates(
                assessment_arn=params.get("assessmentArn"),
                name=params.get("name"),
                recommendation_template_arn=params.get("recommendationTemplateArn"),
                status=params.get("status"),
                reverse_order=params.get("reverseOrder") == "true",
                max_results=max_results,
                next_token=next_token,
            )
        )
        return json.dumps(
            {
                "nextToken": next_token,
                "recommendationTemplates": [t.to_json() for t in templates],
            }
        )

    # --- Resource mapping operations ---

    def add_draft_app_version_resource_mappings(self) -> str:
        params = json.loads(self.body)
        app_arn, app_version, mappings = (
            self.resiliencehub_backend.add_draft_app_version_resource_mappings(
                app_arn=params.get("appArn"),
                resource_mappings=params.get("resourceMappings", []),
            )
        )
        return json.dumps(
            {
                "appArn": app_arn,
                "appVersion": app_version,
                "resourceMappings": mappings,
            }
        )

    def remove_draft_app_version_resource_mappings(self) -> str:
        params = json.loads(self.body)
        app_arn, app_version = (
            self.resiliencehub_backend.remove_draft_app_version_resource_mappings(
                app_arn=params.get("appArn"),
                app_registry_app_names=params.get("appRegistryAppNames"),
                eks_source_names=params.get("eksSourceNames"),
                logical_stack_names=params.get("logicalStackNames"),
                resource_group_names=params.get("resourceGroupNames"),
                resource_names=params.get("resourceNames"),
                terraform_source_names=params.get("terraformSourceNames"),
            )
        )
        return json.dumps({"appArn": app_arn, "appVersion": app_version})

    def list_app_version_resource_mappings(self) -> str:
        params = json.loads(self.body)
        max_results = params.get("maxResults", 100)
        next_token = params.get("nextToken")
        mappings, next_token = (
            self.resiliencehub_backend.list_app_version_resource_mappings(
                app_arn=params.get("appArn"),
                app_version_name=params.get("appVersion"),
                max_results=max_results,
                next_token=next_token,
            )
        )
        return json.dumps(
            {"nextToken": next_token, "resourceMappings": mappings}
        )

    # --- Input source operations ---

    def delete_app_input_source(self) -> str:
        params = json.loads(self.body)
        app_arn, input_source = (
            self.resiliencehub_backend.delete_app_input_source(
                app_arn=params.get("appArn"),
                eks_source_cluster_namespace=params.get(
                    "eksSourceClusterNamespace"
                ),
                source_arn=params.get("sourceArn"),
                terraform_source=params.get("terraformSource"),
            )
        )
        return json.dumps({"appArn": app_arn, "appInputSource": input_source})

    def list_app_input_sources(self) -> str:
        params = json.loads(self.body)
        max_results = params.get("maxResults", 100)
        next_token = params.get("nextToken")
        sources, next_token = self.resiliencehub_backend.list_app_input_sources(
            app_arn=params.get("appArn"),
            app_version_name=params.get("appVersion"),
            max_results=max_results,
            next_token=next_token,
        )
        return json.dumps({"appInputSources": sources, "nextToken": next_token})

    # --- Assessment-related list operations ---

    def list_alarm_recommendations(self) -> str:
        params = json.loads(self.body)
        max_results = params.get("maxResults", 100)
        next_token = params.get("nextToken")
        recommendations, next_token = (
            self.resiliencehub_backend.list_alarm_recommendations(
                assessment_arn=params.get("assessmentArn"),
                max_results=max_results,
                next_token=next_token,
            )
        )
        return json.dumps(
            {"alarmRecommendations": recommendations, "nextToken": next_token}
        )

    def list_sop_recommendations(self) -> str:
        params = json.loads(self.body)
        max_results = params.get("maxResults", 100)
        next_token = params.get("nextToken")
        recommendations, next_token = (
            self.resiliencehub_backend.list_sop_recommendations(
                assessment_arn=params.get("assessmentArn"),
                max_results=max_results,
                next_token=next_token,
            )
        )
        return json.dumps(
            {"sopRecommendations": recommendations, "nextToken": next_token}
        )

    def list_test_recommendations(self) -> str:
        params = json.loads(self.body)
        max_results = params.get("maxResults", 100)
        next_token = params.get("nextToken")
        recommendations, next_token = (
            self.resiliencehub_backend.list_test_recommendations(
                assessment_arn=params.get("assessmentArn"),
                max_results=max_results,
                next_token=next_token,
            )
        )
        return json.dumps(
            {"testRecommendations": recommendations, "nextToken": next_token}
        )

    def list_app_component_compliances(self) -> str:
        params = json.loads(self.body)
        max_results = params.get("maxResults", 100)
        next_token = params.get("nextToken")
        compliances, next_token = (
            self.resiliencehub_backend.list_app_component_compliances(
                assessment_arn=params.get("assessmentArn"),
                max_results=max_results,
                next_token=next_token,
            )
        )
        return json.dumps(
            {"componentCompliances": compliances, "nextToken": next_token}
        )

    def list_app_component_recommendations(self) -> str:
        params = json.loads(self.body)
        max_results = params.get("maxResults", 100)
        next_token = params.get("nextToken")
        recommendations, next_token = (
            self.resiliencehub_backend.list_app_component_recommendations(
                assessment_arn=params.get("assessmentArn"),
                max_results=max_results,
                next_token=next_token,
            )
        )
        return json.dumps(
            {"componentRecommendations": recommendations, "nextToken": next_token}
        )

    def list_app_assessment_compliance_drifts(self) -> str:
        params = json.loads(self.body)
        max_results = params.get("maxResults", 100)
        next_token = params.get("nextToken")
        drifts, next_token = (
            self.resiliencehub_backend.list_app_assessment_compliance_drifts(
                assessment_arn=params.get("assessmentArn"),
                max_results=max_results,
                next_token=next_token,
            )
        )
        return json.dumps({"complianceDrifts": drifts, "nextToken": next_token})

    def list_app_assessment_resource_drifts(self) -> str:
        params = json.loads(self.body)
        max_results = params.get("maxResults", 100)
        next_token = params.get("nextToken")
        drifts, next_token = (
            self.resiliencehub_backend.list_app_assessment_resource_drifts(
                assessment_arn=params.get("assessmentArn"),
                max_results=max_results,
                next_token=next_token,
            )
        )
        return json.dumps({"resourceDrifts": drifts, "nextToken": next_token})

    def list_unsupported_app_version_resources(self) -> str:
        params = json.loads(self.body)
        max_results = params.get("maxResults", 100)
        next_token = params.get("nextToken")
        resources, next_token = (
            self.resiliencehub_backend.list_unsupported_app_version_resources(
                app_arn=params.get("appArn"),
                app_version_name=params.get("appVersion"),
                resolution_id=params.get("resolutionId"),
                max_results=max_results,
                next_token=next_token,
            )
        )
        result: dict = {
            "nextToken": next_token,
            "unsupportedResources": resources,
        }
        if params.get("resolutionId"):
            result["resolutionId"] = params.get("resolutionId")
        return json.dumps(result)

    def list_suggested_resiliency_policies(self) -> str:
        params = self._get_params()
        max_results = int(params.get("maxResults", 100))
        next_token = params.get("nextToken")
        policies, next_token = (
            self.resiliencehub_backend.list_suggested_resiliency_policies(
                max_results=max_results,
                next_token=next_token,
            )
        )
        return json.dumps(
            {
                "nextToken": next_token,
                "resiliencyPolicies": [p.to_json() for p in policies],
            }
        )

    # --- Metrics operations ---

    def start_metrics_export(self) -> str:
        params = json.loads(self.body)
        export_id, status = self.resiliencehub_backend.start_metrics_export(
            bucket_name=params.get("bucketName"),
        )
        return json.dumps({"metricsExportId": export_id, "status": status})

    def describe_metrics_export(self) -> str:
        params = json.loads(self.body)
        result = self.resiliencehub_backend.describe_metrics_export(
            metrics_export_id=params.get("metricsExportId"),
        )
        return json.dumps(result)

    def list_metrics(self) -> str:
        params = json.loads(self.body)
        rows, next_token = self.resiliencehub_backend.list_metrics(
            conditions=params.get("conditions"),
            data_source=params.get("dataSource"),
            fields=params.get("fields"),
            max_results=params.get("maxResults"),
            next_token=params.get("nextToken"),
            sorts=params.get("sorts"),
        )
        return json.dumps({"nextToken": next_token, "rows": rows})

    # --- Resource grouping operations ---

    def start_resource_grouping_recommendation_task(self) -> str:
        params = json.loads(self.body)
        result = (
            self.resiliencehub_backend.start_resource_grouping_recommendation_task(
                app_arn=params.get("appArn"),
            )
        )
        return json.dumps(result)

    def describe_resource_grouping_recommendation_task(self) -> str:
        params = json.loads(self.body)
        result = (
            self.resiliencehub_backend.describe_resource_grouping_recommendation_task(
                app_arn=params.get("appArn"),
                grouping_id=params.get("groupingId"),
            )
        )
        return json.dumps(result)

    def list_resource_grouping_recommendations(self) -> str:
        params = self._get_params()
        max_results = int(params.get("maxResults", 100))
        next_token = params.get("nextToken")
        recommendations, next_token = (
            self.resiliencehub_backend.list_resource_grouping_recommendations(
                app_arn=params.get("appArn"),
                max_results=max_results,
                next_token=next_token,
            )
        )
        return json.dumps(
            {
                "groupingRecommendations": recommendations,
                "nextToken": next_token,
            }
        )

    def accept_resource_grouping_recommendations(self) -> str:
        params = json.loads(self.body)
        app_arn, failed = (
            self.resiliencehub_backend.accept_resource_grouping_recommendations(
                app_arn=params.get("appArn"),
                entries=params.get("entries", []),
            )
        )
        return json.dumps({"appArn": app_arn, "failedEntries": failed})

    def reject_resource_grouping_recommendations(self) -> str:
        params = json.loads(self.body)
        app_arn, failed = (
            self.resiliencehub_backend.reject_resource_grouping_recommendations(
                app_arn=params.get("appArn"),
                entries=params.get("entries", []),
            )
        )
        return json.dumps({"appArn": app_arn, "failedEntries": failed})

    # --- Batch operations ---

    def batch_update_recommendation_status(self) -> str:
        params = json.loads(self.body)
        app_arn, failed, successful = (
            self.resiliencehub_backend.batch_update_recommendation_status(
                app_arn=params.get("appArn"),
                request_entries=params.get("requestEntries", []),
            )
        )
        return json.dumps(
            {
                "appArn": app_arn,
                "failedEntries": failed,
                "successfulEntries": successful,
            }
        )
