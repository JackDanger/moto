from moto.core.responses import ActionResult, EmptyResult

from ._base_response import EC2BaseResponse


class VolumeAttributeResponse(EC2BaseResponse):
    def describe_volume_attribute(self) -> ActionResult:
        volume_id = self._get_param("VolumeId")
        attribute = self._get_param("Attribute")
        result = self.ec2_backend.describe_volume_attribute(
            volume_id=volume_id,
            attribute=attribute,
        )

        response = {"VolumeId": result.volume_id}

        if attribute == "autoEnableIO":
            response["AutoEnableIO"] = {"Value": result.auto_enable_io}
        elif attribute == "productCodes":
            response["ProductCodes"] = {}

        return ActionResult(response)

    def modify_volume_attribute(self) -> ActionResult:
        volume_id = self._get_param("VolumeId")
        auto_enable_io = self._get_param("AutoEnableIO")
        self.ec2_backend.modify_volume_attribute(
            volume_id=volume_id,
            auto_enable_io=auto_enable_io,
        )
        return ActionResult({"Return": True})
