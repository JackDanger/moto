from ._base_response import EC2BaseResponse


class CapacityBlockResponse(EC2BaseResponse):
    def describe_capacity_block_offerings(self) -> str:
        instance_type = self._get_param("InstanceType")
        instance_count = int(self._get_param("InstanceCount", "1"))
        duration = int(self._get_param("CapacityDurationHours", "24"))
        offerings = self.ec2_backend.describe_capacity_block_offerings(
            instance_type=instance_type,
            instance_count=instance_count,
            capacity_duration_hours=duration,
        )
        template = self.response_template(DESCRIBE_CAPACITY_BLOCK_OFFERINGS)
        return template.render(offerings=offerings)

    def purchase_capacity_block(self) -> str:
        offering_id = self._get_param("CapacityBlockOfferingId")
        instance_platform = self._get_param("InstancePlatform", "Linux/UNIX")
        result = self.ec2_backend.purchase_capacity_block(
            capacity_block_offering_id=offering_id,
            instance_platform=instance_platform,
        )
        template = self.response_template(PURCHASE_CAPACITY_BLOCK)
        return template.render(result=result)


DESCRIBE_CAPACITY_BLOCK_OFFERINGS = """<DescribeCapacityBlockOfferingsResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
  <requestId>7a62c49f-347e-4fc4-9331-6e8eEXAMPLE</requestId>
  <capacityBlockOfferingSet>
    {% for offering in offerings %}
    <item>
      <capacityBlockOfferingId>{{ offering.id }}</capacityBlockOfferingId>
      <instanceType>{{ offering.instance_type }}</instanceType>
      <availabilityZone>{{ offering.availability_zone }}</availabilityZone>
      <instanceCount>{{ offering.instance_count }}</instanceCount>
      <capacityBlockDurationHours>{{ offering.capacity_duration_hours }}</capacityBlockDurationHours>
      <currencyCode>{{ offering.currency_code }}</currencyCode>
      <upfrontFee>{{ offering.upfront_fee }}</upfrontFee>
      <startDate>{{ offering.start_date }}</startDate>
      <endDate>{{ offering.end_date }}</endDate>
      <tenancy>{{ offering.tenancy }}</tenancy>
    </item>
    {% endfor %}
  </capacityBlockOfferingSet>
</DescribeCapacityBlockOfferingsResponse>"""

PURCHASE_CAPACITY_BLOCK = """<PurchaseCapacityBlockResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
  <requestId>7a62c49f-347e-4fc4-9331-6e8eEXAMPLE</requestId>
  <capacityReservation>
    <capacityReservationId>{{ result.capacity_reservation_id }}</capacityReservationId>
    <instanceType>{{ result.instance_type }}</instanceType>
    <instancePlatform>{{ result.instance_platform }}</instancePlatform>
    <availabilityZone>{{ result.availability_zone }}</availabilityZone>
    <instanceCount>{{ result.instance_count }}</instanceCount>
    <state>{{ result.state }}</state>
  </capacityReservation>
</PurchaseCapacityBlockResponse>"""
