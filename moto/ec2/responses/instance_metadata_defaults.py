from moto.core.responses import ActionResult

from ._base_response import EC2BaseResponse


class InstanceMetadataDefaultsResponse(EC2BaseResponse):
    def get_instance_metadata_defaults(self) -> ActionResult:
        defaults = self.ec2_backend.get_instance_metadata_defaults()
        account_level = {}
        if defaults.http_tokens:
            account_level["HttpTokens"] = defaults.http_tokens
        if defaults.http_put_response_hop_limit:
            account_level["HttpPutResponseHopLimit"] = defaults.http_put_response_hop_limit
        if defaults.http_endpoint:
            account_level["HttpEndpoint"] = defaults.http_endpoint
        if defaults.instance_metadata_tags:
            account_level["InstanceMetadataTags"] = defaults.instance_metadata_tags
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
