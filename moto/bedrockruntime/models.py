"""BedrockRuntimeBackend class with methods for supported APIs."""

import uuid
from collections import OrderedDict
from typing import Any, Optional

from moto.core.base_backend import BackendDict, BaseBackend
from moto.core.utils import utcnow


class AsyncInvocation:
    """Represents an async model invocation."""

    def __init__(
        self,
        invocation_id: str,
        model_id: str,
        region: str,
        account_id: str,
        output_data_config: Optional[dict[str, Any]] = None,
    ) -> None:
        self.invocation_id = invocation_id
        self.model_id = model_id
        self.region = region
        self.account_id = account_id
        self.output_data_config = output_data_config or {}
        self.status = "Completed"
        self.submit_time = utcnow().isoformat()
        self.end_time = utcnow().isoformat()

    @property
    def invocation_arn(self) -> str:
        return f"arn:aws:bedrock:{self.region}:{self.account_id}:async-invoke/{self.invocation_id}"

    def to_dict(self) -> dict[str, Any]:
        return {
            "invocationArn": self.invocation_arn,
            "modelArn": self.model_id,
            "outputDataConfig": self.output_data_config,
            "status": self.status,
            "submitTime": self.submit_time,
            "endTime": self.end_time,
        }


class BedrockRuntimeBackend(BaseBackend):
    """Implementation of BedrockRuntime APIs."""

    def __init__(self, region_name: str, account_id: str) -> None:
        super().__init__(region_name, account_id)
        self._async_invocations: OrderedDict[str, AsyncInvocation] = OrderedDict()

    def invoke_model(
        self,
        payload: dict[str, Any],
        model_id: str,
    ) -> dict[str, Any]:
        assert payload is not None
        assert model_id is not None
        inference_result: dict[str, Any] = {}
        return inference_result

    def converse(
        self,
        model_id: str,
        messages: list[dict[str, Any]],
        system: Optional[list[dict[str, Any]]] = None,
        inference_config: Optional[dict[str, Any]] = None,
        additional_model_request_fields: Optional[dict[str, Any]] = None,
        additional_model_response_field_paths: Optional[list[str]] = None,
        tool_config: Optional[dict[str, Any]] = None,
        guardrail_config: Optional[dict[str, Any]] = None,
        prompt_variables: Optional[dict[str, Any]] = None,
        performance_config: Optional[dict[str, Any]] = None,
        request_metadata: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        """Return a stub Converse response."""
        return {
            "output": {
                "message": {
                    "role": "assistant",
                    "content": [
                        {"text": "This is a mock response from bedrock-runtime."}
                    ],
                }
            },
            "stopReason": "end_turn",
            "usage": {
                "inputTokens": 10,
                "outputTokens": 10,
                "totalTokens": 20,
            },
            "metrics": {
                "latencyMs": 100,
            },
        }

    def converse_stream(
        self,
        model_id: str,
        messages: list[dict[str, Any]],
        system: Optional[list[dict[str, Any]]] = None,
        inference_config: Optional[dict[str, Any]] = None,
        additional_model_request_fields: Optional[dict[str, Any]] = None,
        additional_model_response_field_paths: Optional[list[str]] = None,
        tool_config: Optional[dict[str, Any]] = None,
        guardrail_config: Optional[dict[str, Any]] = None,
        prompt_variables: Optional[dict[str, Any]] = None,
        performance_config: Optional[dict[str, Any]] = None,
        request_metadata: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        """Return a stub ConverseStream response."""
        return {
            "stream": [
                {
                    "contentBlockDelta": {
                        "contentBlockIndex": 0,
                        "delta": {"text": "Mock streaming response."},
                    }
                },
                {
                    "messageStop": {
                        "stopReason": "end_turn",
                    }
                },
            ],
            "usage": {
                "inputTokens": 10,
                "outputTokens": 5,
                "totalTokens": 15,
            },
        }

    def count_tokens(
        self,
        model_id: str,
        messages: Optional[list[dict[str, Any]]] = None,
        system: Optional[list[dict[str, Any]]] = None,
        tool_config: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        """Return a stub CountTokens response."""
        return {
            "inputTokenCount": 10,
        }

    def apply_guardrail(
        self,
        guardrail_identifier: str,
        guardrail_version: str,
        source: str,
        content: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """Return a stub ApplyGuardrail response."""
        return {
            "usage": {
                "topicPolicyUnitsProcessed": 0,
                "contentPolicyUnitsProcessed": 0,
                "wordPolicyUnitsProcessed": 0,
                "sensitiveInformationPolicyUnitsProcessed": 0,
                "sensitiveInformationPolicyFreeUnitsProcessed": 0,
                "contextualGroundingPolicyUnitsProcessed": 0,
            },
            "action": "NONE",
            "outputs": [],
            "assessments": [],
        }

    def start_async_invoke(
        self,
        model_id: str,
        model_input: dict[str, Any],
        output_data_config: Optional[dict[str, Any]] = None,
        client_request_token: Optional[str] = None,
        tags: Optional[list[dict[str, Any]]] = None,
    ) -> dict[str, Any]:
        """Start an async model invocation."""
        invocation_id = str(uuid.uuid4())
        invocation = AsyncInvocation(
            invocation_id=invocation_id,
            model_id=model_id,
            region=self.region_name,
            account_id=self.account_id,
            output_data_config=output_data_config or {},
        )
        self._async_invocations[invocation_id] = invocation
        return {"invocationArn": invocation.invocation_arn}

    def get_async_invoke(self, invocation_arn: str) -> dict[str, Any]:
        """Get an async invocation by ARN."""
        # Extract invocation_id from ARN
        invocation_id = invocation_arn.split("/")[-1]
        invocation = self._async_invocations.get(invocation_id)
        if invocation is None:
            from moto.core.exceptions import JsonRESTError

            raise JsonRESTError(
                "ResourceNotFoundException", f"Invocation not found: {invocation_arn}"
            )
        return invocation.to_dict()

    def list_async_invokes(
        self,
        max_results: Optional[int] = None,
        next_token: Optional[str] = None,
        status_equals: Optional[str] = None,
        submit_time_after: Optional[str] = None,
        submit_time_before: Optional[str] = None,
        sort_by: Optional[str] = None,
        sort_order: Optional[str] = None,
    ) -> dict[str, Any]:
        """List async invocations."""
        invocations = list(self._async_invocations.values())
        if status_equals:
            invocations = [i for i in invocations if i.status == status_equals]
        return {
            "asyncInvokeSummaries": [i.to_dict() for i in invocations],
        }


# Using `ec2` for the service name to work around lack of regions for bedrock-runtime in Botocore.
# https://github.com/getmoto/moto/issues/7745
bedrockruntime_backends = BackendDict(BedrockRuntimeBackend, "ec2")
