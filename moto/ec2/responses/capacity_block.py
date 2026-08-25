from moto.core.responses import ActionResult

from ._base_response import EC2BaseResponse


class CapacityBlockResponse(EC2BaseResponse):
    def describe_capacity_block_offerings(self) -> ActionResult:
        instance_type = self._get_param("InstanceType")
        instance_count = int(self._get_param("InstanceCount", "1"))
        duration = int(self._get_param("CapacityDurationHours", "24"))
        offerings = self.ec2_backend.describe_capacity_block_offerings(
            instance_type=instance_type,
            instance_count=instance_count,
            capacity_duration_hours=duration,
        )
        offering_list = []
        for offering in offerings:
            offering_dict = {
                "CapacityBlockOfferingId": offering.id,
                "InstanceType": offering.instance_type,
                "AvailabilityZone": offering.availability_zone,
                "InstanceCount": offering.instance_count,
                "CapacityBlockDurationHours": offering.capacity_duration_hours,
                "CurrencyCode": offering.currency_code,
                "UpfrontFee": offering.upfront_fee,
                "StartDate": offering.start_date,
                "EndDate": offering.end_date,
                "Tenancy": offering.tenancy,
            }
            offering_list.append(offering_dict)
        return ActionResult({"CapacityBlockOfferings": offering_list})

    def purchase_capacity_block(self) -> ActionResult:
        offering_id = self._get_param("CapacityBlockOfferingId")
        instance_platform = self._get_param("InstancePlatform", "Linux/UNIX")
        result = self.ec2_backend.purchase_capacity_block(
            capacity_block_offering_id=offering_id,
            instance_platform=instance_platform,
        )
        capacity_reservation = {
            "CapacityReservationId": result.capacity_reservation_id,
            "InstanceType": result.instance_type,
            "InstancePlatform": result.instance_platform,
            "AvailabilityZone": result.availability_zone,
            "InstanceCount": result.instance_count,
            "State": result.state,
        }
        return ActionResult({"CapacityReservation": capacity_reservation})
