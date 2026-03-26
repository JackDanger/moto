"""Handles incoming bedrockruntime requests, invokes methods, returns responses."""

import json
from typing import Any

from moto.core.responses import ActionResult, BaseResponse
from moto.utilities.constants import APPLICATION_JSON

from .models import BedrockRuntimeBackend, bedrockruntime_backends


class BedrockRuntimeResponse(BaseResponse):
    """Handler for BedrockRuntime requests and responses."""

    def __init__(self) -> None:
        super().__init__(service_name="bedrock-runtime")
        self.automated_parameter_parsing = True

    @property
    def bedrockruntime_backend(self) -> BedrockRuntimeBackend:
        """Return backend instance specific for this region."""
        return bedrockruntime_backends[self.current_account][self.region]

    def invoke_model(self) -> ActionResult:
        payload = self._get_param("body")
        content_type = self._get_param("contentType", APPLICATION_JSON)
        if content_type == APPLICATION_JSON:
            payload = json.loads(payload)
        accept = self._get_param("accept", APPLICATION_JSON)
        model_id = self._get_param("modelId")
        performance_config_latency = self._get_param(
            "performanceConfigLatency", "standard"
        )
        service_tier = self._get_param("serviceTier", "default")
        inference_result = self.bedrockruntime_backend.invoke_model(
            payload=payload,
            model_id=model_id,
        )
        body: Any = inference_result
        if accept == APPLICATION_JSON:
            body = json.dumps(inference_result)
        result = {
            "body": body,
            "contentType": "application/json",
            "performanceConfigLatency": performance_config_latency,
            "serviceTier": service_tier,
        }
        return ActionResult(result)

    def converse(self) -> ActionResult:
        model_id = self._get_param("modelId")
        messages = self._get_param("messages")
        system = self._get_param("system")
        inference_config = self._get_param("inferenceConfig")
        additional_model_request_fields = self._get_param("additionalModelRequestFields")
        additional_model_response_field_paths = self._get_param("additionalModelResponseFieldPaths")
        tool_config = self._get_param("toolConfig")
        guardrail_config = self._get_param("guardrailConfig")
        prompt_variables = self._get_param("promptVariables")
        performance_config = self._get_param("performanceConfig")
        request_metadata = self._get_param("requestMetadata")
        result = self.bedrockruntime_backend.converse(
            model_id=model_id,
            messages=messages or [],
            system=system,
            inference_config=inference_config,
            additional_model_request_fields=additional_model_request_fields,
            additional_model_response_field_paths=additional_model_response_field_paths,
            tool_config=tool_config,
            guardrail_config=guardrail_config,
            prompt_variables=prompt_variables,
            performance_config=performance_config,
            request_metadata=request_metadata,
        )
        return ActionResult(result)

    def converse_stream(self) -> ActionResult:
        model_id = self._get_param("modelId")
        messages = self._get_param("messages")
        system = self._get_param("system")
        inference_config = self._get_param("inferenceConfig")
        additional_model_request_fields = self._get_param("additionalModelRequestFields")
        additional_model_response_field_paths = self._get_param("additionalModelResponseFieldPaths")
        tool_config = self._get_param("toolConfig")
        guardrail_config = self._get_param("guardrailConfig")
        prompt_variables = self._get_param("promptVariables")
        performance_config = self._get_param("performanceConfig")
        request_metadata = self._get_param("requestMetadata")
        result = self.bedrockruntime_backend.converse_stream(
            model_id=model_id,
            messages=messages or [],
            system=system,
            inference_config=inference_config,
            additional_model_request_fields=additional_model_request_fields,
            additional_model_response_field_paths=additional_model_response_field_paths,
            tool_config=tool_config,
            guardrail_config=guardrail_config,
            prompt_variables=prompt_variables,
            performance_config=performance_config,
            request_metadata=request_metadata,
        )
        return ActionResult(result)

    def count_tokens(self) -> ActionResult:
        model_id = self._get_param("modelId")
        messages = self._get_param("messages")
        system = self._get_param("system")
        tool_config = self._get_param("toolConfig")
        result = self.bedrockruntime_backend.count_tokens(
            model_id=model_id,
            messages=messages,
            system=system,
            tool_config=tool_config,
        )
        return ActionResult(result)

    def apply_guardrail(self) -> ActionResult:
        guardrail_identifier = self._get_param("guardrailIdentifier")
        guardrail_version = self._get_param("guardrailVersion")
        source = self._get_param("source")
        content = self._get_param("content")
        result = self.bedrockruntime_backend.apply_guardrail(
            guardrail_identifier=guardrail_identifier,
            guardrail_version=guardrail_version,
            source=source,
            content=content or [],
        )
        return ActionResult(result)

    def start_async_invoke(self) -> ActionResult:
        model_id = self._get_param("modelId")
        model_input = self._get_param("modelInput")
        output_data_config = self._get_param("outputDataConfig")
        client_request_token = self._get_param("clientRequestToken")
        tags = self._get_param("tags")
        result = self.bedrockruntime_backend.start_async_invoke(
            model_id=model_id,
            model_input=model_input or {},
            output_data_config=output_data_config,
            client_request_token=client_request_token,
            tags=tags,
        )
        return ActionResult(result)

    def get_async_invoke(self) -> ActionResult:
        invocation_arn = self._get_param("invocationArn")
        result = self.bedrockruntime_backend.get_async_invoke(
            invocation_arn=invocation_arn,
        )
        return ActionResult(result)

    def list_async_invokes(self) -> ActionResult:
        max_results = self._get_param("maxResults")
        next_token = self._get_param("nextToken")
        status_equals = self._get_param("statusEquals")
        submit_time_after = self._get_param("submitTimeAfter")
        submit_time_before = self._get_param("submitTimeBefore")
        sort_by = self._get_param("sortBy")
        sort_order = self._get_param("sortOrder")
        result = self.bedrockruntime_backend.list_async_invokes(
            max_results=max_results,
            next_token=next_token,
            status_equals=status_equals,
            submit_time_after=submit_time_after,
            submit_time_before=submit_time_before,
            sort_by=sort_by,
            sort_order=sort_order,
        )
        return ActionResult(result)

    def invoke_model_with_response_stream(self) -> ActionResult:
        """Stub for InvokeModelWithResponseStream - returns basic response."""
        model_id = self._get_param("modelId")
        body = self._get_param("body")
        content_type = self._get_param("contentType", APPLICATION_JSON)
        accept = self._get_param("accept", APPLICATION_JSON)
        result = {
            "body": json.dumps({}),
            "contentType": "application/json",
        }
        return ActionResult(result)

    def invoke_model_with_bidirectional_stream(self) -> ActionResult:
        """Stub for InvokeModelWithBidirectionalStream."""
        result = {
            "body": json.dumps({}),
        }
        return ActionResult(result)
