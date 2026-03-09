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
        return connect_backends[self.current_account][self.region]

    def _get_param_from_path(self, name: str) -> str:
        """Extract a named parameter from the URL path."""
        val = self._get_param(name)
        return unquote(val) if val else ""

    def _get_instance_id(self) -> str:
        return self._get_param_from_path("InstanceId")

    # ---- Instance ----

    def create_instance(self) -> str:
        params = json.loads(self.body) if self.body else {}
        result = self.connect_backend.create_instance(
            identity_management_type=str(params["IdentityManagementType"]),
            instance_alias=params.get("InstanceAlias"),
            inbound_calls_enabled=params.get("InboundCallsEnabled", False),
            outbound_calls_enabled=params.get("OutboundCallsEnabled", False),
            tags=params.get("Tags"),
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
            max_results=max_results, next_token=next_token
        )
        response: dict[str, Any] = {"InstanceSummaryList": results}
        if token:
            response["NextToken"] = token
        return json.dumps(response)

    def delete_instance(self) -> str:
        instance_id = self._get_instance_id()
        self.connect_backend.delete_instance(instance_id=instance_id)
        return "{}"

    # ---- Instance Attribute ----

    def describe_instance_attribute(self) -> str:
        instance_id = self._get_instance_id()
        attribute_type = self._get_param_from_path("AttributeType")
        result = self.connect_backend.describe_instance_attribute(
            instance_id=instance_id, attribute_type=attribute_type
        )
        return json.dumps({"Attribute": result})

    def update_instance_attribute(self) -> str:
        instance_id = self._get_instance_id()
        attribute_type = self._get_param_from_path("AttributeType")
        params = json.loads(self.body) if self.body else {}
        self.connect_backend.update_instance_attribute(
            instance_id=instance_id,
            attribute_type=attribute_type,
            value=str(params["Value"]),
        )
        return "{}"

    # ---- Analytics Data Association ----

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

    def list_users(self) -> str:
        instance_id = self._get_instance_id()
        results = self.connect_backend.list_users(instance_id=instance_id)
        return json.dumps({"UserSummaryList": results})

    def list_user_hierarchy_groups(self) -> str:
        instance_id = self._get_instance_id()
        results = self.connect_backend.list_user_hierarchy_groups(
            instance_id=instance_id
        )
        return json.dumps({"UserHierarchyGroupSummaryList": results})

    def list_views(self) -> str:
        instance_id = self._get_instance_id()
        results = self.connect_backend.list_views(instance_id=instance_id)
        return json.dumps({"ViewsSummaryList": results})

    def list_rules(self) -> str:
        instance_id = self._get_instance_id()
        results = self.connect_backend.list_rules(instance_id=instance_id)
        return json.dumps({"RuleSummaryList": results})

    def list_task_templates(self) -> str:
        instance_id = self._get_instance_id()
        results = self.connect_backend.list_task_templates(instance_id=instance_id)
        return json.dumps({"TaskTemplates": results})

    def list_integration_associations(self) -> str:
        instance_id = self._get_instance_id()
        results = self.connect_backend.list_integration_associations(
            instance_id=instance_id
        )
        return json.dumps({"IntegrationAssociationSummaryList": results})

    def list_routing_profile_queues(self) -> str:
        instance_id = self._get_instance_id()
        routing_profile_id = self._get_param("RoutingProfileId")
        results = self.connect_backend.list_routing_profile_queues(
            instance_id=instance_id, routing_profile_id=routing_profile_id
        )
        return json.dumps({"RoutingProfileQueueConfigSummaryList": results})

    def associate_analytics_data_set(self) -> str:
        instance_id = self._get_instance_id()
        params = json.loads(self.body) if self.body else {}
        result = self.connect_backend.associate_analytics_data_set(
            instance_id=instance_id,
            data_set_id=str(params["DataSetId"]),
            target_account_id=params.get("TargetAccountId"),
        )
        return json.dumps(result)

    def disassociate_analytics_data_set(self) -> str:
        instance_id = self._get_instance_id()
        params = json.loads(self.body) if self.body else {}
        self.connect_backend.disassociate_analytics_data_set(
            instance_id=instance_id, data_set_id=str(params["DataSetId"])
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

    # ---- Agent Status ----

    def create_agent_status(self) -> str:
        instance_id = self._get_instance_id()
        params = json.loads(self.body) if self.body else {}
        result = self.connect_backend.create_agent_status(
            instance_id=instance_id,
            name=str(params["Name"]),
            state=str(params["State"]),
            description=params.get("Description", ""),
            display_order=params.get("DisplayOrder"),
            tags=params.get("Tags"),
        )
        return json.dumps(result)

    def describe_agent_status(self) -> str:
        instance_id = self._get_instance_id()
        agent_status_id = self._get_param_from_path("AgentStatusId")
        result = self.connect_backend.describe_agent_status(
            instance_id=instance_id, agent_status_id=agent_status_id
        )
        return json.dumps({"AgentStatus": result})

    def update_agent_status(self) -> str:
        instance_id = self._get_instance_id()
        agent_status_id = self._get_param_from_path("AgentStatusId")
        params = json.loads(self.body) if self.body else {}
        self.connect_backend.update_agent_status(
            instance_id=instance_id,
            agent_status_id=agent_status_id,
            name=params.get("Name"),
            description=params.get("Description"),
            state=params.get("State"),
            display_order=params.get("DisplayOrder"),
            reset_order_number=params.get("ResetOrderNumber", False),
        )
        return "{}"

    # ---- Contact Flow ----

    def create_contact_flow(self) -> str:
        instance_id = self._get_instance_id()
        params = json.loads(self.body) if self.body else {}
        result = self.connect_backend.create_contact_flow(
            instance_id=instance_id,
            name=str(params["Name"]),
            flow_type=str(params["Type"]),
            content=str(params["Content"]),
            description=params.get("Description", ""),
            status=params.get("Status", "PUBLISHED"),
            tags=params.get("Tags"),
        )
        return json.dumps(result)

    def describe_contact_flow(self) -> str:
        instance_id = self._get_instance_id()
        contact_flow_id = self._get_param_from_path("ContactFlowId")
        result = self.connect_backend.describe_contact_flow(
            instance_id=instance_id, contact_flow_id=contact_flow_id
        )
        return json.dumps({"ContactFlow": result})

    def update_contact_flow_content(self) -> str:
        instance_id = self._get_instance_id()
        contact_flow_id = self._get_param_from_path("ContactFlowId")
        params = json.loads(self.body) if self.body else {}
        self.connect_backend.update_contact_flow_content(
            instance_id=instance_id,
            contact_flow_id=contact_flow_id,
            content=str(params["Content"]),
        )
        return "{}"

    def update_contact_flow_name(self) -> str:
        instance_id = self._get_instance_id()
        contact_flow_id = self._get_param_from_path("ContactFlowId")
        params = json.loads(self.body) if self.body else {}
        self.connect_backend.update_contact_flow_name(
            instance_id=instance_id,
            contact_flow_id=contact_flow_id,
            name=params.get("Name"),
            description=params.get("Description"),
        )
        return "{}"

    def delete_contact_flow(self) -> str:
        instance_id = self._get_instance_id()
        contact_flow_id = self._get_param_from_path("ContactFlowId")
        self.connect_backend.delete_contact_flow(
            instance_id=instance_id, contact_flow_id=contact_flow_id
        )
        return "{}"

    # ---- Contact Flow Module ----

    def create_contact_flow_module(self) -> str:
        instance_id = self._get_instance_id()
        params = json.loads(self.body) if self.body else {}
        result = self.connect_backend.create_contact_flow_module(
            instance_id=instance_id,
            name=str(params["Name"]),
            content=str(params["Content"]),
            description=params.get("Description", ""),
            tags=params.get("Tags"),
        )
        return json.dumps(result)

    def describe_contact_flow_module(self) -> str:
        instance_id = self._get_instance_id()
        module_id = self._get_param_from_path("ContactFlowModuleId")
        result = self.connect_backend.describe_contact_flow_module(
            instance_id=instance_id, contact_flow_module_id=module_id
        )
        return json.dumps({"ContactFlowModule": result})

    def delete_contact_flow_module(self) -> str:
        instance_id = self._get_instance_id()
        module_id = self._get_param_from_path("ContactFlowModuleId")
        self.connect_backend.delete_contact_flow_module(
            instance_id=instance_id, contact_flow_module_id=module_id
        )
        return "{}"

    # ---- Hours of Operation ----

    def create_hours_of_operation(self) -> str:
        instance_id = self._get_instance_id()
        params = json.loads(self.body) if self.body else {}
        result = self.connect_backend.create_hours_of_operation(
            instance_id=instance_id,
            name=str(params["Name"]),
            time_zone=str(params["TimeZone"]),
            config=params["Config"],
            description=params.get("Description", ""),
            tags=params.get("Tags"),
        )
        return json.dumps(result)

    def describe_hours_of_operation(self) -> str:
        instance_id = self._get_instance_id()
        hours_id = self._get_param_from_path("HoursOfOperationId")
        result = self.connect_backend.describe_hours_of_operation(
            instance_id=instance_id, hours_of_operation_id=hours_id
        )
        return json.dumps({"HoursOfOperation": result})

    def update_hours_of_operation(self) -> str:
        instance_id = self._get_instance_id()
        hours_id = self._get_param_from_path("HoursOfOperationId")
        params = json.loads(self.body) if self.body else {}
        self.connect_backend.update_hours_of_operation(
            instance_id=instance_id,
            hours_of_operation_id=hours_id,
            name=params.get("Name"),
            description=params.get("Description"),
            time_zone=params.get("TimeZone"),
            config=params.get("Config"),
        )
        return "{}"

    def delete_hours_of_operation(self) -> str:
        instance_id = self._get_instance_id()
        hours_id = self._get_param_from_path("HoursOfOperationId")
        self.connect_backend.delete_hours_of_operation(
            instance_id=instance_id, hours_of_operation_id=hours_id
        )
        return "{}"

    # ---- Prompt ----

    def create_prompt(self) -> str:
        instance_id = self._get_instance_id()
        params = json.loads(self.body) if self.body else {}
        result = self.connect_backend.create_prompt(
            instance_id=instance_id,
            name=str(params["Name"]),
            s3_uri=str(params["S3Uri"]),
            description=params.get("Description", ""),
            tags=params.get("Tags"),
        )
        return json.dumps(result)

    def describe_prompt(self) -> str:
        instance_id = self._get_instance_id()
        prompt_id = self._get_param_from_path("PromptId")
        result = self.connect_backend.describe_prompt(
            instance_id=instance_id, prompt_id=prompt_id
        )
        return json.dumps({"Prompt": result})

    def update_prompt(self) -> str:
        instance_id = self._get_instance_id()
        prompt_id = self._get_param_from_path("PromptId")
        params = json.loads(self.body) if self.body else {}
        result = self.connect_backend.update_prompt(
            instance_id=instance_id, prompt_id=prompt_id,
            name=params.get("Name"), description=params.get("Description"),
            s3_uri=params.get("S3Uri"),
        )
        return json.dumps(result)

    def delete_prompt(self) -> str:
        instance_id = self._get_instance_id()
        prompt_id = self._get_param_from_path("PromptId")
        self.connect_backend.delete_prompt(instance_id=instance_id, prompt_id=prompt_id)
        return "{}"

    # ---- Queue ----

    def create_queue(self) -> str:
        instance_id = self._get_instance_id()
        params = json.loads(self.body) if self.body else {}
        result = self.connect_backend.create_queue(
            instance_id=instance_id,
            name=str(params["Name"]),
            hours_of_operation_id=str(params["HoursOfOperationId"]),
            description=params.get("Description", ""),
            outbound_caller_config=params.get("OutboundCallerConfig"),
            max_contacts=params.get("MaxContacts"),
            tags=params.get("Tags"),
        )
        return json.dumps(result)

    def describe_queue(self) -> str:
        instance_id = self._get_instance_id()
        queue_id = self._get_param_from_path("QueueId")
        result = self.connect_backend.describe_queue(
            instance_id=instance_id, queue_id=queue_id
        )
        return json.dumps({"Queue": result})

    def update_queue_name(self) -> str:
        instance_id = self._get_instance_id()
        queue_id = self._get_param_from_path("QueueId")
        params = json.loads(self.body) if self.body else {}
        self.connect_backend.update_queue_name(
            instance_id=instance_id, queue_id=queue_id,
            name=params.get("Name"), description=params.get("Description"),
        )
        return "{}"

    def update_queue_status(self) -> str:
        instance_id = self._get_instance_id()
        queue_id = self._get_param_from_path("QueueId")
        params = json.loads(self.body) if self.body else {}
        self.connect_backend.update_queue_status(
            instance_id=instance_id, queue_id=queue_id, status=str(params["Status"]),
        )
        return "{}"

    def update_queue_max_contacts(self) -> str:
        instance_id = self._get_instance_id()
        queue_id = self._get_param_from_path("QueueId")
        params = json.loads(self.body) if self.body else {}
        self.connect_backend.update_queue_max_contacts(
            instance_id=instance_id, queue_id=queue_id, max_contacts=int(params["MaxContacts"]),
        )
        return "{}"

    def update_queue_hours_of_operation(self) -> str:
        instance_id = self._get_instance_id()
        queue_id = self._get_param_from_path("QueueId")
        params = json.loads(self.body) if self.body else {}
        self.connect_backend.update_queue_hours_of_operation(
            instance_id=instance_id, queue_id=queue_id,
            hours_of_operation_id=str(params["HoursOfOperationId"]),
        )
        return "{}"

    def update_queue_outbound_caller_config(self) -> str:
        instance_id = self._get_instance_id()
        queue_id = self._get_param_from_path("QueueId")
        params = json.loads(self.body) if self.body else {}
        self.connect_backend.update_queue_outbound_caller_config(
            instance_id=instance_id, queue_id=queue_id,
            outbound_caller_config=params["OutboundCallerConfig"],
        )
        return "{}"

    def delete_queue(self) -> str:
        instance_id = self._get_instance_id()
        queue_id = self._get_param_from_path("QueueId")
        self.connect_backend.delete_queue(instance_id=instance_id, queue_id=queue_id)
        return "{}"

    # ---- Quick Connect ----

    def create_quick_connect(self) -> str:
        instance_id = self._get_instance_id()
        params = json.loads(self.body) if self.body else {}
        result = self.connect_backend.create_quick_connect(
            instance_id=instance_id,
            name=str(params["Name"]),
            quick_connect_config=params["QuickConnectConfig"],
            description=params.get("Description", ""),
            tags=params.get("Tags"),
        )
        return json.dumps(result)

    def describe_quick_connect(self) -> str:
        instance_id = self._get_instance_id()
        qc_id = self._get_param_from_path("QuickConnectId")
        result = self.connect_backend.describe_quick_connect(
            instance_id=instance_id, quick_connect_id=qc_id
        )
        return json.dumps({"QuickConnect": result})

    def update_quick_connect_name(self) -> str:
        instance_id = self._get_instance_id()
        qc_id = self._get_param_from_path("QuickConnectId")
        params = json.loads(self.body) if self.body else {}
        self.connect_backend.update_quick_connect_name(
            instance_id=instance_id, quick_connect_id=qc_id,
            name=params.get("Name"), description=params.get("Description"),
        )
        return "{}"

    def update_quick_connect_config(self) -> str:
        instance_id = self._get_instance_id()
        qc_id = self._get_param_from_path("QuickConnectId")
        params = json.loads(self.body) if self.body else {}
        self.connect_backend.update_quick_connect_config(
            instance_id=instance_id, quick_connect_id=qc_id,
            quick_connect_config=params["QuickConnectConfig"],
        )
        return "{}"

    def delete_quick_connect(self) -> str:
        instance_id = self._get_instance_id()
        qc_id = self._get_param_from_path("QuickConnectId")
        self.connect_backend.delete_quick_connect(
            instance_id=instance_id, quick_connect_id=qc_id
        )
        return "{}"

    # ---- Routing Profile ----

    def create_routing_profile(self) -> str:
        instance_id = self._get_instance_id()
        params = json.loads(self.body) if self.body else {}
        result = self.connect_backend.create_routing_profile(
            instance_id=instance_id,
            name=str(params["Name"]),
            description=str(params["Description"]),
            default_outbound_queue_id=str(params["DefaultOutboundQueueId"]),
            media_concurrencies=params["MediaConcurrencies"],
            tags=params.get("Tags"),
        )
        return json.dumps(result)

    def describe_routing_profile(self) -> str:
        instance_id = self._get_instance_id()
        rp_id = self._get_param_from_path("RoutingProfileId")
        result = self.connect_backend.describe_routing_profile(
            instance_id=instance_id, routing_profile_id=rp_id
        )
        return json.dumps({"RoutingProfile": result})

    def update_routing_profile_name(self) -> str:
        instance_id = self._get_instance_id()
        rp_id = self._get_param_from_path("RoutingProfileId")
        params = json.loads(self.body) if self.body else {}
        self.connect_backend.update_routing_profile_name(
            instance_id=instance_id, routing_profile_id=rp_id,
            name=params.get("Name"), description=params.get("Description"),
        )
        return "{}"

    def update_routing_profile_concurrency(self) -> str:
        instance_id = self._get_instance_id()
        rp_id = self._get_param_from_path("RoutingProfileId")
        params = json.loads(self.body) if self.body else {}
        self.connect_backend.update_routing_profile_concurrency(
            instance_id=instance_id, routing_profile_id=rp_id,
            media_concurrencies=params["MediaConcurrencies"],
        )
        return "{}"

    def update_routing_profile_default_outbound_queue(self) -> str:
        instance_id = self._get_instance_id()
        rp_id = self._get_param_from_path("RoutingProfileId")
        params = json.loads(self.body) if self.body else {}
        self.connect_backend.update_routing_profile_default_outbound_queue(
            instance_id=instance_id, routing_profile_id=rp_id,
            default_outbound_queue_id=str(params["DefaultOutboundQueueId"]),
        )
        return "{}"

    def delete_routing_profile(self) -> str:
        instance_id = self._get_instance_id()
        rp_id = self._get_param_from_path("RoutingProfileId")
        self.connect_backend.delete_routing_profile(
            instance_id=instance_id, routing_profile_id=rp_id
        )
        return "{}"

    # ---- Security Profile ----

    def create_security_profile(self) -> str:
        instance_id = self._get_instance_id()
        params = json.loads(self.body) if self.body else {}
        result = self.connect_backend.create_security_profile(
            instance_id=instance_id,
            security_profile_name=str(params["SecurityProfileName"]),
            description=params.get("Description", ""),
            permissions=params.get("Permissions"),
            tags=params.get("Tags"),
            allowed_access_control_tags=params.get("AllowedAccessControlTags"),
            tag_restricted_resources=params.get("TagRestrictedResources"),
        )
        return json.dumps(result)

    def describe_security_profile(self) -> str:
        instance_id = self._get_instance_id()
        sp_id = self._get_param_from_path("SecurityProfileId")
        result = self.connect_backend.describe_security_profile(
            instance_id=instance_id, security_profile_id=sp_id
        )
        return json.dumps({"SecurityProfile": result})

    def update_security_profile(self) -> str:
        instance_id = self._get_instance_id()
        sp_id = self._get_param_from_path("SecurityProfileId")
        params = json.loads(self.body) if self.body else {}
        self.connect_backend.update_security_profile(
            instance_id=instance_id, security_profile_id=sp_id,
            security_profile_name=params.get("SecurityProfileName"),
            description=params.get("Description"),
            permissions=params.get("Permissions"),
            allowed_access_control_tags=params.get("AllowedAccessControlTags"),
            tag_restricted_resources=params.get("TagRestrictedResources"),
        )
        return "{}"

    def delete_security_profile(self) -> str:
        instance_id = self._get_instance_id()
        sp_id = self._get_param_from_path("SecurityProfileId")
        self.connect_backend.delete_security_profile(
            instance_id=instance_id, security_profile_id=sp_id
        )
        return "{}"

    # ---- User ----

    def create_user(self) -> str:
        instance_id = self._get_instance_id()
        params = json.loads(self.body) if self.body else {}
        result = self.connect_backend.create_user(
            instance_id=instance_id,
            username=str(params["Username"]),
            security_profile_ids=params["SecurityProfileIds"],
            routing_profile_id=str(params["RoutingProfileId"]),
            phone_config=params.get("PhoneConfig"),
            identity_info=params.get("IdentityInfo"),
            directory_user_id=params.get("DirectoryUserId"),
            hierarchy_group_id=params.get("HierarchyGroupId"),
            tags=params.get("Tags"),
        )
        return json.dumps(result)

    def describe_user(self) -> str:
        instance_id = self._get_instance_id()
        user_id = self._get_param_from_path("UserId")
        result = self.connect_backend.describe_user(
            instance_id=instance_id, user_id=user_id
        )
        return json.dumps({"User": result})

    def update_user_identity_info(self) -> str:
        instance_id = self._get_instance_id()
        user_id = self._get_param_from_path("UserId")
        params = json.loads(self.body) if self.body else {}
        self.connect_backend.update_user_identity_info(
            instance_id=instance_id, user_id=user_id, identity_info=params["IdentityInfo"],
        )
        return "{}"

    def update_user_phone_config(self) -> str:
        instance_id = self._get_instance_id()
        user_id = self._get_param_from_path("UserId")
        params = json.loads(self.body) if self.body else {}
        self.connect_backend.update_user_phone_config(
            instance_id=instance_id, user_id=user_id, phone_config=params["PhoneConfig"],
        )
        return "{}"

    def update_user_routing_profile(self) -> str:
        instance_id = self._get_instance_id()
        user_id = self._get_param_from_path("UserId")
        params = json.loads(self.body) if self.body else {}
        self.connect_backend.update_user_routing_profile(
            instance_id=instance_id, user_id=user_id,
            routing_profile_id=str(params["RoutingProfileId"]),
        )
        return "{}"

    def update_user_security_profiles(self) -> str:
        instance_id = self._get_instance_id()
        user_id = self._get_param_from_path("UserId")
        params = json.loads(self.body) if self.body else {}
        self.connect_backend.update_user_security_profiles(
            instance_id=instance_id, user_id=user_id,
            security_profile_ids=params["SecurityProfileIds"],
        )
        return "{}"

    def update_user_hierarchy(self) -> str:
        instance_id = self._get_instance_id()
        user_id = self._get_param_from_path("UserId")
        params = json.loads(self.body) if self.body else {}
        self.connect_backend.update_user_hierarchy(
            instance_id=instance_id, user_id=user_id,
            hierarchy_group_id=params.get("HierarchyGroupId"),
        )
        return "{}"

    def delete_user(self) -> str:
        instance_id = self._get_instance_id()
        user_id = self._get_param_from_path("UserId")
        self.connect_backend.delete_user(instance_id=instance_id, user_id=user_id)
        return "{}"

    def search_users(self) -> str:
        params = json.loads(self.body) if self.body else {}
        instance_id = str(params["InstanceId"])
        search_criteria = params.get("SearchCriteria")
        results = self.connect_backend.search_users(
            instance_id=instance_id, search_criteria=search_criteria
        )
        return json.dumps({"Users": results, "ApproximateTotalCount": len(results)})

    # ---- User Hierarchy Group ----

    def create_user_hierarchy_group(self) -> str:
        instance_id = self._get_instance_id()
        params = json.loads(self.body) if self.body else {}
        result = self.connect_backend.create_user_hierarchy_group(
            instance_id=instance_id,
            name=str(params["Name"]),
            parent_group_id=params.get("ParentGroupId"),
            tags=params.get("Tags"),
        )
        return json.dumps(result)

    def describe_user_hierarchy_group(self) -> str:
        instance_id = self._get_instance_id()
        group_id = self._get_param_from_path("HierarchyGroupId")
        result = self.connect_backend.describe_user_hierarchy_group(
            instance_id=instance_id, hierarchy_group_id=group_id
        )
        return json.dumps({"HierarchyGroup": result})

    # ---- User Hierarchy Structure ----

    def describe_user_hierarchy_structure(self) -> str:
        instance_id = self._get_instance_id()
        result = self.connect_backend.describe_user_hierarchy_structure(
            instance_id=instance_id
        )
        return json.dumps({"HierarchyStructure": result})

    # ---- Vocabulary ----

    def create_vocabulary(self) -> str:
        instance_id = self._get_instance_id()
        params = json.loads(self.body) if self.body else {}
        result = self.connect_backend.create_vocabulary(
            instance_id=instance_id,
            vocabulary_name=str(params["VocabularyName"]),
            language_code=str(params["LanguageCode"]),
            content=str(params["Content"]),
            tags=params.get("Tags"),
        )
        return json.dumps(result)

    def describe_vocabulary(self) -> str:
        instance_id = self._get_instance_id()
        vocab_id = self._get_param_from_path("VocabularyId")
        result = self.connect_backend.describe_vocabulary(
            instance_id=instance_id, vocabulary_id=vocab_id
        )
        return json.dumps({"Vocabulary": result})

    def delete_vocabulary(self) -> str:
        instance_id = self._get_instance_id()
        vocab_id = self._get_param_from_path("VocabularyId")
        result = self.connect_backend.delete_vocabulary(
            instance_id=instance_id, vocabulary_id=vocab_id
        )
        return json.dumps(result)

    def search_vocabularies(self) -> str:
        instance_id = self._get_instance_id()
        params = json.loads(self.body) if self.body else {}
        results = self.connect_backend.search_vocabularies(
            instance_id=instance_id,
            state=params.get("State"),
            name_starts_with=params.get("NameStartsWith"),
            language_code=params.get("LanguageCode"),
        )
        return json.dumps({"VocabularySummaryList": results})

    # ---- View ----

    def create_view(self) -> str:
        instance_id = self._get_instance_id()
        params = json.loads(self.body) if self.body else {}
        result = self.connect_backend.create_view(
            instance_id=instance_id,
            name=str(params["Name"]),
            status=str(params["Status"]),
            content=params["Content"],
            description=params.get("Description", ""),
            tags=params.get("Tags"),
        )
        return json.dumps(result)

    def describe_view(self) -> str:
        instance_id = self._get_instance_id()
        view_id = self._get_param_from_path("ViewId")
        result = self.connect_backend.describe_view(
            instance_id=instance_id, view_id=view_id
        )
        return json.dumps({"View": result})

    # ---- Phone Number ----

    def describe_phone_number(self) -> str:
        phone_number_id = self._get_param_from_path("PhoneNumberId")
        result = self.connect_backend.describe_phone_number(
            phone_number_id=phone_number_id
        )
        return json.dumps({"ClaimedPhoneNumberSummary": result})

    # ---- Traffic Distribution Group ----

    def create_traffic_distribution_group(self) -> str:
        params = json.loads(self.body) if self.body else {}
        result = self.connect_backend.create_traffic_distribution_group(
            name=str(params["Name"]),
            instance_arn=str(params["InstanceArn"]),
            description=params.get("Description", ""),
            tags=params.get("Tags"),
        )
        return json.dumps(result)

    def describe_traffic_distribution_group(self) -> str:
        tdg_id = self._get_param_from_path("TrafficDistributionGroupId")
        result = self.connect_backend.describe_traffic_distribution_group(
            traffic_distribution_group_id=tdg_id
        )
        return json.dumps({"TrafficDistributionGroup": result})

    # ---- Evaluation Form ----

    def create_evaluation_form(self) -> str:
        instance_id = self._get_instance_id()
        params = json.loads(self.body) if self.body else {}
        result = self.connect_backend.create_evaluation_form(
            instance_id=instance_id,
            title=str(params["Title"]),
            description=params.get("Description", ""),
            items=params.get("Items"),
            scoring_strategy=params.get("ScoringStrategy"),
        )
        return json.dumps(result)

    def describe_evaluation_form(self) -> str:
        instance_id = self._get_instance_id()
        form_id = self._get_param_from_path("EvaluationFormId")
        result = self.connect_backend.describe_evaluation_form(
            instance_id=instance_id, evaluation_form_id=form_id
        )
        return json.dumps({"EvaluationForm": result})

    # ---- Rule ----

    def create_rule(self) -> str:
        instance_id = self._get_instance_id()
        params = json.loads(self.body) if self.body else {}
        result = self.connect_backend.create_rule(
            instance_id=instance_id,
            name=str(params["Name"]),
            trigger_event_source=params["TriggerEventSource"],
            function=str(params["Function"]),
            actions=params["Actions"],
            publish_status=str(params["PublishStatus"]),
        )
        return json.dumps(result)

    def describe_rule(self) -> str:
        instance_id = self._get_instance_id()
        rule_id = self._get_param_from_path("RuleId")
        result = self.connect_backend.describe_rule(
            instance_id=instance_id, rule_id=rule_id
        )
        return json.dumps({"Rule": result})

    def update_rule(self) -> str:
        instance_id = self._get_instance_id()
        rule_id = self._get_param_from_path("RuleId")
        params = json.loads(self.body) if self.body else {}
        self.connect_backend.update_rule(
            instance_id=instance_id, rule_id=rule_id,
            name=str(params["Name"]), function=str(params["Function"]),
            actions=params["Actions"], publish_status=str(params["PublishStatus"]),
        )
        return "{}"

    def delete_rule(self) -> str:
        instance_id = self._get_instance_id()
        rule_id = self._get_param_from_path("RuleId")
        self.connect_backend.delete_rule(instance_id=instance_id, rule_id=rule_id)
        return "{}"

    # ---- Phone Number: Claim, Release, Update, Search ----

    def claim_phone_number(self) -> str:
        params = json.loads(self.body) if self.body else {}
        target_arn = str(params["TargetArn"])
        instance_id = target_arn.split("/")[-1]
        result = self.connect_backend.claim_phone_number(
            instance_id=instance_id,
            phone_number=str(params["PhoneNumber"]),
            phone_number_country_code=str(params["PhoneNumberCountryCode"]),
            phone_number_type=str(params["PhoneNumberType"]),
            description=params.get("PhoneNumberDescription", ""),
            tags=params.get("Tags"),
        )
        return json.dumps(result)

    def release_phone_number(self) -> str:
        phone_number_id = self._get_param_from_path("PhoneNumberId")
        self.connect_backend.release_phone_number(phone_number_id=phone_number_id)
        return "{}"

    def update_phone_number(self) -> str:
        phone_number_id = self._get_param_from_path("PhoneNumberId")
        params = json.loads(self.body) if self.body else {}
        result = self.connect_backend.update_phone_number(
            phone_number_id=phone_number_id,
            target_arn=params.get("TargetArn"),
            instance_id=params.get("InstanceId"),
        )
        return json.dumps(result)

    def search_available_phone_numbers(self) -> str:
        params = json.loads(self.body) if self.body else {}
        results = self.connect_backend.search_available_phone_numbers(
            target_arn=str(params["TargetArn"]),
            phone_number_country_code=str(params["PhoneNumberCountryCode"]),
            phone_number_type=str(params["PhoneNumberType"]),
            phone_number_prefix=params.get("PhoneNumberPrefix"),
            max_results=params.get("MaxResults", 10),
        )
        return json.dumps({"AvailableNumbersList": results})

    # ---- Contact Attributes ----

    def get_contact_attributes(self) -> str:
        instance_id = self._get_instance_id()
        contact_id = self._get_param_from_path("InitialContactId")
        result = self.connect_backend.get_contact_attributes(
            instance_id=instance_id, initial_contact_id=contact_id
        )
        return json.dumps({"Attributes": result})

    def update_contact_attributes(self) -> str:
        params = json.loads(self.body) if self.body else {}
        instance_id = str(params["InstanceId"])
        initial_contact_id = str(params["InitialContactId"])
        attributes = params.get("Attributes", {})
        self.connect_backend.update_contact_attributes(
            instance_id=instance_id,
            initial_contact_id=initial_contact_id,
            attributes=attributes,
        )
        return "{}"

    # ---- Tags ----

    def _get_resource_arn(self) -> str:
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
        self.connect_backend.untag_resource(resource_arn=resource_arn, tag_keys=tag_keys)
        return "{}"

    def list_tags_for_resource(self) -> str:
        resource_arn = self._get_resource_arn()
        tags = self.connect_backend.list_tags_for_resource(resource_arn=resource_arn)
        return json.dumps({"tags": tags})
