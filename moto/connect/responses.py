"""Handles incoming connect requests, invokes methods, returns responses."""

import json
from typing import Any, Optional
from urllib.parse import unquote

from moto.core.responses import BaseResponse

from .models import ConnectBackend, connect_backends


class ConnectResponse(BaseResponse):
    """Handler for Connect requests and responses."""

    def __init__(self) -> None:
        super().__init__(service_name="connect")

    @property
    def connect_backend(self) -> ConnectBackend:
        """Return backend instance specific for this region."""
        return connect_backends[self.current_account][self.region]

    def _get_instance_id(self) -> str:
        """Extract instance_id from request path params."""
        instance_id = self._get_param("InstanceId")
        return unquote(instance_id) if instance_id else ""

    def list_agent_statuses(self) -> str:
        instance_id = self._get_instance_id()
        results = self.connect_backend.list_agent_statuses(instance_id=instance_id)
        return json.dumps({"AgentStatusSummaryList": results})

    def list_approved_origins(self) -> str:
        instance_id = self._get_instance_id()
        results = self.connect_backend.list_approved_origins(instance_id=instance_id)
        return json.dumps({"Origins": results})

    def list_bots(self) -> str:
        instance_id = self._get_instance_id()
        results = self.connect_backend.list_bots(instance_id=instance_id)
        return json.dumps({"LexBots": results})

    def list_contact_evaluations(self) -> str:
        instance_id = self._get_instance_id()
        results = self.connect_backend.list_contact_evaluations(instance_id=instance_id)
        return json.dumps({"EvaluationSummaryList": results})

    def list_contact_flow_modules(self) -> str:
        instance_id = self._get_instance_id()
        results = self.connect_backend.list_contact_flow_modules(instance_id=instance_id)
        return json.dumps({"ContactFlowModulesSummaryList": results})

    def list_contact_flow_versions(self) -> str:
        instance_id = self._get_instance_id()
        contact_flow_id = self._get_param("ContactFlowId")
        results = self.connect_backend.list_contact_flow_versions(
            instance_id=instance_id, contact_flow_id=contact_flow_id
        )
        return json.dumps({"ContactFlowVersionSummaryList": results})

    def list_contact_flows(self) -> str:
        instance_id = self._get_instance_id()
        results = self.connect_backend.list_contact_flows(instance_id=instance_id)
        return json.dumps({"ContactFlowSummaryList": results})

    def list_contact_references(self) -> str:
        instance_id = self._get_instance_id()
        results = self.connect_backend.list_contact_references(instance_id=instance_id)
        return json.dumps({"ReferenceSummaryList": results})

    def list_default_vocabularies(self) -> str:
        instance_id = self._get_instance_id()
        results = self.connect_backend.list_default_vocabularies(instance_id=instance_id)
        return json.dumps({"DefaultVocabularyList": results})

    def list_evaluation_form_versions(self) -> str:
        instance_id = self._get_instance_id()
        evaluation_form_id = self._get_param("EvaluationFormId")
        results = self.connect_backend.list_evaluation_form_versions(
            instance_id=instance_id, evaluation_form_id=evaluation_form_id
        )
        return json.dumps({"EvaluationFormVersionSummaryList": results})

    def list_evaluation_forms(self) -> str:
        instance_id = self._get_instance_id()
        results = self.connect_backend.list_evaluation_forms(instance_id=instance_id)
        return json.dumps({"EvaluationFormSummaryList": results})

    def list_flow_associations(self) -> str:
        instance_id = self._get_instance_id()
        results = self.connect_backend.list_flow_associations(instance_id=instance_id)
        return json.dumps({"FlowAssociationSummaryList": results})

    def list_hours_of_operation_overrides(self) -> str:
        instance_id = self._get_instance_id()
        hours_of_operation_id = self._get_param("HoursOfOperationId")
        results = self.connect_backend.list_hours_of_operation_overrides(
            instance_id=instance_id, hours_of_operation_id=hours_of_operation_id
        )
        return json.dumps({"HoursOfOperationOverrideList": results})

    def list_hours_of_operations(self) -> str:
        instance_id = self._get_instance_id()
        results = self.connect_backend.list_hours_of_operations(instance_id=instance_id)
        return json.dumps({"HoursOfOperationSummaryList": results})

    def list_instance_attributes(self) -> str:
        instance_id = self._get_instance_id()
        results = self.connect_backend.list_instance_attributes(instance_id=instance_id)
        return json.dumps({"Attributes": results})

    def list_instance_storage_configs(self) -> str:
        instance_id = self._get_instance_id()
        results = self.connect_backend.list_instance_storage_configs(
            instance_id=instance_id
        )
        return json.dumps({"StorageConfigs": results})

    def list_lambda_functions(self) -> str:
        instance_id = self._get_instance_id()
        results = self.connect_backend.list_lambda_functions(instance_id=instance_id)
        return json.dumps({"LambdaFunctions": results})

    def list_phone_numbers(self) -> str:
        instance_id = self._get_instance_id()
        results = self.connect_backend.list_phone_numbers(instance_id=instance_id)
        return json.dumps({"PhoneNumberSummaryList": results})

    def list_phone_numbers_v2(self) -> str:
        results = self.connect_backend.list_phone_numbers_v2()
        return json.dumps({"ListPhoneNumbersSummaryList": results})

    def list_prompts(self) -> str:
        instance_id = self._get_instance_id()
        results = self.connect_backend.list_prompts(instance_id=instance_id)
        return json.dumps({"PromptSummaryList": results})

    def list_queue_quick_connects(self) -> str:
        instance_id = self._get_instance_id()
        queue_id = self._get_param("QueueId")
        results = self.connect_backend.list_queue_quick_connects(
            instance_id=instance_id, queue_id=queue_id
        )
        return json.dumps({"QuickConnectSummaryList": results})

    def list_queues(self) -> str:
        instance_id = self._get_instance_id()
        results = self.connect_backend.list_queues(instance_id=instance_id)
        return json.dumps({"QueueSummaryList": results})

    def list_quick_connects(self) -> str:
        instance_id = self._get_instance_id()
        results = self.connect_backend.list_quick_connects(instance_id=instance_id)
        return json.dumps({"QuickConnectSummaryList": results})

    def list_routing_profiles(self) -> str:
        instance_id = self._get_instance_id()
        results = self.connect_backend.list_routing_profiles(instance_id=instance_id)
        return json.dumps({"RoutingProfileSummaryList": results})

    def list_security_keys(self) -> str:
        instance_id = self._get_instance_id()
        results = self.connect_backend.list_security_keys(instance_id=instance_id)
        return json.dumps({"SecurityKeys": results})

    def list_security_profile_applications(self) -> str:
        instance_id = self._get_instance_id()
        security_profile_id = self._get_param("SecurityProfileId")
        results = self.connect_backend.list_security_profile_applications(
            instance_id=instance_id, security_profile_id=security_profile_id
        )
        return json.dumps({"Applications": results})

    def list_security_profile_permissions(self) -> str:
        instance_id = self._get_instance_id()
        security_profile_id = self._get_param("SecurityProfileId")
        results = self.connect_backend.list_security_profile_permissions(
            instance_id=instance_id, security_profile_id=security_profile_id
        )
        return json.dumps({"Permissions": results})

    def list_security_profiles(self) -> str:
        instance_id = self._get_instance_id()
        results = self.connect_backend.list_security_profiles(instance_id=instance_id)
        return json.dumps({"SecurityProfileSummaryList": results})

    def list_use_cases(self) -> str:
        instance_id = self._get_instance_id()
        integration_association_id = self._get_param("IntegrationAssociationId")
        results = self.connect_backend.list_use_cases(
            instance_id=instance_id,
            integration_association_id=integration_association_id,
        )
        return json.dumps({"UseCaseSummaryList": results})

    def associate_analytics_data_set(self) -> str:
        instance_id = self._get_instance_id()
        params = json.loads(self.body) if self.body else {}
        data_set_id = str(params["DataSetId"])
        target_account_id = params.get("TargetAccountId")

        result = self.connect_backend.associate_analytics_data_set(
            instance_id=instance_id,
            data_set_id=data_set_id,
            target_account_id=target_account_id,
        )

        return json.dumps(result)

    def disassociate_analytics_data_set(self) -> str:
        instance_id = self._get_instance_id()
        params = json.loads(self.body) if self.body else {}
        data_set_id = str(params["DataSetId"])

        self.connect_backend.disassociate_analytics_data_set(
            instance_id=instance_id,
            data_set_id=data_set_id,
        )

        return "{}"

    def list_analytics_data_associations(self) -> str:
        instance_id = self._get_instance_id()
        data_set_id = self._get_param("DataSetId")
        max_results = self._get_int_param("maxResults")
        next_token = self._get_param("nextToken")

        results: list[dict[str, str]]
        token: Optional[str]
        results, token = self.connect_backend.list_analytics_data_associations(
            instance_id=instance_id,
            data_set_id=data_set_id,
            max_results=max_results,
            next_token=next_token,
        )

        response: dict[str, Any] = {"Results": results}
        if token:
            response["NextToken"] = token

        return json.dumps(response)

    def create_instance(self) -> str:
        params = json.loads(self.body) if self.body else {}
        identity_management_type = str(params["IdentityManagementType"])
        instance_alias = params.get("InstanceAlias")
        inbound_calls_enabled = params.get("InboundCallsEnabled", False)
        outbound_calls_enabled = params.get("OutboundCallsEnabled", False)
        tags = params.get("Tags")

        result = self.connect_backend.create_instance(
            identity_management_type=identity_management_type,
            instance_alias=instance_alias,
            inbound_calls_enabled=inbound_calls_enabled,
            outbound_calls_enabled=outbound_calls_enabled,
            tags=tags,
        )

        return json.dumps(result)

    def describe_instance(self) -> str:
        instance_id = self._get_instance_id()

        instance = self.connect_backend.describe_instance(instance_id=instance_id)

        return json.dumps({"Instance": instance})

    def list_instances(self) -> str:
        max_results = self._get_int_param("maxResults")
        next_token = self._get_param("nextToken")

        results: list[dict[str, Any]]
        token: Optional[str]
        results, token = self.connect_backend.list_instances(
            max_results=max_results,
            next_token=next_token,
        )

        response: dict[str, Any] = {"InstanceSummaryList": results}
        if token:
            response["NextToken"] = token

        return json.dumps(response)

    def delete_instance(self) -> str:
        instance_id = self._get_instance_id()

        self.connect_backend.delete_instance(instance_id=instance_id)

        return "{}"

    def _get_resource_arn(self) -> str:
        """Extract resourceArn from request path params."""
        resource_arn = self._get_param("resourceArn")
        return unquote(resource_arn) if resource_arn else ""

    def tag_resource(self) -> str:
        resource_arn = self._get_resource_arn()
        params = json.loads(self.body) if self.body else {}
        tags = params.get("tags", {})

        self.connect_backend.tag_resource(resource_arn=resource_arn, tags=tags)

        return "{}"

    def untag_resource(self) -> str:
        resource_arn = self._get_resource_arn()
        tag_keys = self.querystring.get("tagKeys", [])

        self.connect_backend.untag_resource(
            resource_arn=resource_arn, tag_keys=tag_keys
        )

        return "{}"

    def list_tags_for_resource(self) -> str:
        resource_arn = self._get_resource_arn()

        tags = self.connect_backend.list_tags_for_resource(resource_arn=resource_arn)

        return json.dumps({"tags": tags})
