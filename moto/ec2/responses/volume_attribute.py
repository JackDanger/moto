from ._base_response import EC2BaseResponse


class VolumeAttributeResponse(EC2BaseResponse):
    def describe_volume_attribute(self) -> str:
        volume_id = self._get_param("VolumeId")
        attribute = self._get_param("Attribute")
        result = self.ec2_backend.describe_volume_attribute(
            volume_id=volume_id,
            attribute=attribute,
        )
        template = self.response_template(DESCRIBE_VOLUME_ATTRIBUTE)
        return template.render(result=result, attribute=attribute)

    def modify_volume_attribute(self) -> str:
        volume_id = self._get_param("VolumeId")
        auto_enable_io = self._get_param("AutoEnableIO")
        self.ec2_backend.modify_volume_attribute(
            volume_id=volume_id,
            auto_enable_io=auto_enable_io,
        )
        template = self.response_template(MODIFY_VOLUME_ATTRIBUTE)
        return template.render()


DESCRIBE_VOLUME_ATTRIBUTE = """<DescribeVolumeAttributeResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
  <requestId>7a62c49f-347e-4fc4-9331-6e8eEXAMPLE</requestId>
  <volumeId>{{ result.volume_id }}</volumeId>
  {% if attribute == 'autoEnableIO' %}
  <autoEnableIO>
    <value>{{ result.auto_enable_io }}</value>
  </autoEnableIO>
  {% elif attribute == 'productCodes' %}
  <productCodes/>
  {% endif %}
</DescribeVolumeAttributeResponse>"""

MODIFY_VOLUME_ATTRIBUTE = """<ModifyVolumeAttributeResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
  <requestId>7a62c49f-347e-4fc4-9331-6e8eEXAMPLE</requestId>
  <return>true</return>
</ModifyVolumeAttributeResponse>"""
