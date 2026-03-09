from ._base_response import EC2BaseResponse


class InstanceMetadataDefaultsResponse(EC2BaseResponse):
    def get_instance_metadata_defaults(self) -> str:
        defaults = self.ec2_backend.get_instance_metadata_defaults()
        template = self.response_template(GET_INSTANCE_METADATA_DEFAULTS)
        return template.render(defaults=defaults)

    def modify_instance_metadata_defaults(self) -> str:
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
        template = self.response_template(MODIFY_INSTANCE_METADATA_DEFAULTS)
        return template.render()


GET_INSTANCE_METADATA_DEFAULTS = """<GetInstanceMetadataDefaultsResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
  <requestId>7a62c49f-347e-4fc4-9331-6e8eEXAMPLE</requestId>
  <accountLevel>
    {% if defaults.http_tokens %}
    <httpTokens>{{ defaults.http_tokens }}</httpTokens>
    {% endif %}
    {% if defaults.http_put_response_hop_limit %}
    <httpPutResponseHopLimit>{{ defaults.http_put_response_hop_limit }}</httpPutResponseHopLimit>
    {% endif %}
    {% if defaults.http_endpoint %}
    <httpEndpoint>{{ defaults.http_endpoint }}</httpEndpoint>
    {% endif %}
    {% if defaults.instance_metadata_tags %}
    <instanceMetadataTags>{{ defaults.instance_metadata_tags }}</instanceMetadataTags>
    {% endif %}
  </accountLevel>
</GetInstanceMetadataDefaultsResponse>"""

MODIFY_INSTANCE_METADATA_DEFAULTS = """<ModifyInstanceMetadataDefaultsResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
  <requestId>7a62c49f-347e-4fc4-9331-6e8eEXAMPLE</requestId>
  <return>true</return>
</ModifyInstanceMetadataDefaultsResponse>"""
