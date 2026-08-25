import base64
import json
import struct

from moto.core.common_types import TYPE_RESPONSE
from moto.core.responses import BaseResponse
from moto.moto_api._internal import mock_random as random

from .models import SageMakerRuntimeBackend, sagemakerruntime_backends


def _crc32(data: bytes) -> int:
    """CRC32 using zlib, matching AWS EventStream spec."""
    import zlib

    return zlib.crc32(data) & 0xFFFFFFFF


def _encode_string_header(name: str, value: str) -> bytes:
    """Encode a single EventStream header with string type (type=7)."""
    name_bytes = name.encode("utf-8")
    value_bytes = value.encode("utf-8")
    return (
        struct.pack("!B", len(name_bytes))
        + name_bytes
        + struct.pack("!B", 7)
        + struct.pack("!H", len(value_bytes))
        + value_bytes
    )


def _encode_event_stream_frame(headers: dict[str, str], payload: bytes) -> bytes:
    """
    Encode a single AWS binary EventStream frame.

    Wire format:
      [total_length: 4][headers_length: 4][prelude_crc: 4]
      [headers: variable][payload: variable]
      [message_crc: 4]
    """
    headers_data = b""
    for k, v in headers.items():
        headers_data += _encode_string_header(k, v)

    headers_length = len(headers_data)
    total_length = 4 + 4 + 4 + headers_length + len(payload) + 4

    prelude = struct.pack("!II", total_length, headers_length)
    prelude_crc = _crc32(prelude)

    prelude_with_crc = prelude + struct.pack("!I", prelude_crc)
    message_body = prelude_with_crc + headers_data + payload
    message_crc = _crc32(message_body)

    return message_body + struct.pack("!I", message_crc)


class SageMakerRuntimeResponse(BaseResponse):
    """Handler for SageMakerRuntime requests and responses."""

    def __init__(self) -> None:
        super().__init__(service_name="sagemaker-runtime")

    @property
    def sagemakerruntime_backend(self) -> SageMakerRuntimeBackend:
        """Return backend instance specific for this region."""
        return sagemakerruntime_backends[self.current_account][self.region]

    def invoke_endpoint(self) -> TYPE_RESPONSE:
        params = self._get_params()
        unique_repr = {
            key: value
            for key, value in self.headers.items()
            if key.lower().startswith("x-amzn-sagemaker")
        }
        unique_repr["Accept"] = self.headers.get("Accept")
        unique_repr["Body"] = self.body
        endpoint_name = params.get("EndpointName")
        (
            body,
            content_type,
            invoked_production_variant,
            custom_attributes,
        ) = self.sagemakerruntime_backend.invoke_endpoint(
            endpoint_name=endpoint_name,  # type: ignore[arg-type]
            unique_repr=base64.b64encode(json.dumps(unique_repr).encode("utf-8")),
        )
        headers = {"Content-Type": content_type}
        if invoked_production_variant:
            headers["x-Amzn-Invoked-Production-Variant"] = invoked_production_variant
        if custom_attributes:
            headers["X-Amzn-SageMaker-Custom-Attributes"] = custom_attributes
        return 200, headers, body

    def invoke_endpoint_with_response_stream(self) -> TYPE_RESPONSE:
        unique_repr = {
            key: value
            for key, value in self.headers.items()
            if key.lower().startswith("x-amzn-sagemaker")
        }
        unique_repr["Accept"] = self.headers.get("X-Amzn-SageMaker-Accept")
        unique_repr["Body"] = self.body
        endpoint_name = self.path.split("/")[2]
        (
            body,
            content_type,
            invoked_production_variant,
            custom_attributes,
        ) = self.sagemakerruntime_backend.invoke_endpoint_with_response_stream(
            endpoint_name=endpoint_name,  # type: ignore[arg-type]
            unique_repr=base64.b64encode(json.dumps(unique_repr).encode("utf-8")),
        )
        payload = body if isinstance(body, bytes) else body.encode("utf-8")
        # Encode payload as an EventStream PayloadPart frame
        event_frame = _encode_event_stream_frame(
            headers={
                ":event-type": "PayloadPart",
                ":content-type": "application/octet-stream",
                ":message-type": "event",
            },
            payload=payload,
        )
        response_headers = {
            "Content-Type": "application/vnd.amazon.eventstream",
            "X-Amzn-SageMaker-Content-Type": content_type,
        }
        if invoked_production_variant:
            response_headers[
                "x-Amzn-Invoked-Production-Variant"
            ] = invoked_production_variant
        if custom_attributes:
            response_headers[
                "X-Amzn-SageMaker-Custom-Attributes"
            ] = custom_attributes
        return 200, response_headers, event_frame

    def invoke_endpoint_async(self) -> TYPE_RESPONSE:
        endpoint_name = self.path.split("/")[2]
        input_location = self.headers.get("X-Amzn-SageMaker-InputLocation")
        inference_id = self.headers.get("X-Amzn-SageMaker-Inference-Id")
        output_location, failure_location = (
            self.sagemakerruntime_backend.invoke_endpoint_async(
                endpoint_name, input_location
            )
        )
        resp = {"InferenceId": inference_id or str(random.uuid4())}
        headers = {
            "X-Amzn-SageMaker-OutputLocation": output_location,
            "X-Amzn-SageMaker-FailureLocation": failure_location,
        }
        return 200, headers, json.dumps(resp)
