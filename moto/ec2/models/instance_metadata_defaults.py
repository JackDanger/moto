from typing import Optional


class InstanceMetadataDefaultsBackend:
    def __init__(self) -> None:
        self.instance_metadata_defaults: dict[str, Optional[str]] = {
            "http_tokens": None,
            "http_put_response_hop_limit": None,
            "http_endpoint": None,
            "instance_metadata_tags": None,
        }

    def get_instance_metadata_defaults(self) -> dict[str, Optional[str]]:
        return self.instance_metadata_defaults

    def modify_instance_metadata_defaults(
        self,
        http_tokens: Optional[str] = None,
        http_put_response_hop_limit: Optional[int] = None,
        http_endpoint: Optional[str] = None,
        instance_metadata_tags: Optional[str] = None,
    ) -> bool:
        if http_tokens is not None:
            self.instance_metadata_defaults["http_tokens"] = http_tokens
        if http_put_response_hop_limit is not None:
            self.instance_metadata_defaults["http_put_response_hop_limit"] = str(
                http_put_response_hop_limit
            )
        if http_endpoint is not None:
            self.instance_metadata_defaults["http_endpoint"] = http_endpoint
        if instance_metadata_tags is not None:
            self.instance_metadata_defaults["instance_metadata_tags"] = (
                instance_metadata_tags
            )
        return True
