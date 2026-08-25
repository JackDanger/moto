from typing import Optional


class VolumeAttributeBackend:
    def describe_volume_attribute(
        self, volume_id: str, attribute: str
    ) -> dict[str, str]:
        # Verify volume exists
        self.get_volume(volume_id)  # type: ignore[attr-defined]
        if attribute == "autoEnableIO":
            return {"volume_id": volume_id, "auto_enable_io": "false"}
        elif attribute == "productCodes":
            return {"volume_id": volume_id, "product_codes": []}
        return {"volume_id": volume_id}

    def modify_volume_attribute(
        self, volume_id: str, auto_enable_io: Optional[bool] = None
    ) -> bool:
        # Verify volume exists
        self.get_volume(volume_id)  # type: ignore[attr-defined]
        # In real AWS this sets the autoEnableIO attribute;
        # for mock purposes we just validate and return success
        return True
