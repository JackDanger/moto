from typing import Any

from moto.core.responses import ActionResult

from ._base_response import EC2BaseResponse


class InstanceMetadataDefaultsResponse(EC2BaseResponse):
    def get_instance_metadata_defaults(self) -> ActionResult:
        # get_instance_metadata_defaults returns a plain dict keyed by snake_case
        # names, not a model object.
        defaults = self.ec2_backend.get_instance_metadata_defaults()
        account_level: dict[str, Any] = {}
        for key, member in (
            ("http_tokens", "HttpTokens"),
            ("http_put_response_hop_limit", "HttpPutResponseHopLimit"),
            ("http_endpoint", "HttpEndpoint"),
            ("instance_metadata_tags", "InstanceMetadataTags"),
        ):
            if defaults.get(key):
                account_level[member] = defaults[key]
        return ActionResult({"AccountLevel": account_level})

    def modify_instance_metadata_defaults(self) -> ActionResult:
        http_tokens = self._get_param("HttpTokens")
        hop_limit = self._get_param("HttpPutResponseHopLimit")
        http_endpoint = self._get_param("HttpEndpoint")
        instance_metadata_tags = self._get_param("InstanceMetadataTags")
        self.ec2_backend.modify_instance_metadata_defaults(
            http_tokens=http_tokens,
            http_put_response_hop_limit=int(hop_limit) if hop_limit else None,
            http_endpoint=http_endpoint,
            instance_metadata_tags=instance_metadata_tags,
        )
        return ActionResult({"Return": True})
