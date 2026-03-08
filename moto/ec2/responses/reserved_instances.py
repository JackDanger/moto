from typing import Any

from moto.core.responses import ActionResult

from ._base_response import EC2BaseResponse


class ReservedInstances(EC2BaseResponse):
    def cancel_reserved_instances_listing(self) -> None:
        self.error_on_dryrun()

        raise NotImplementedError(
            "ReservedInstances.cancel_reserved_instances_listing is not yet implemented"
        )

    def create_reserved_instances_listing(self) -> None:
        self.error_on_dryrun()

        raise NotImplementedError(
            "ReservedInstances.create_reserved_instances_listing is not yet implemented"
        )

    def describe_reserved_instances(self) -> str:
        template = self.response_template(DESCRIBE_RESERVED_INSTANCES_TEMPLATE)
        return template.render()

    def describe_reserved_instances_listings(self) -> str:
        template = self.response_template(DESCRIBE_RESERVED_INSTANCES_LISTINGS_TEMPLATE)
        return template.render()

    def describe_reserved_instances_offerings(self) -> ActionResult:
        self.error_on_dryrun()

        # Basic support for filters commonly used by clients
        # Supported filters:
        #  - availability-zone
        #  - instance-type
        #  - product-description
        #  - offering-type
        filters = self._filters_from_querystring()

        offerings = self.ec2_backend.describe_reserved_instances_offerings(filters)
        result: dict[str, Any] = {"ReservedInstancesOfferings": offerings}
        # Pagination is not implemented; always return the full list
        return ActionResult(result)

    def purchase_reserved_instances_offering(self) -> None:
        self.error_on_dryrun()

        raise NotImplementedError(
            "ReservedInstances.purchase_reserved_instances_offering is not yet implemented"
        )


DESCRIBE_RESERVED_INSTANCES_TEMPLATE = """<DescribeReservedInstancesResponse xmlns="http://ec2.amazonaws.com/doc/2013-10-15/">
  <requestId>59dbff89-35bd-4eac-99ed-be587EXAMPLE</requestId>
  <reservedInstancesSet/>
</DescribeReservedInstancesResponse>"""

DESCRIBE_RESERVED_INSTANCES_LISTINGS_TEMPLATE = """<DescribeReservedInstancesListingsResponse xmlns="http://ec2.amazonaws.com/doc/2013-10-15/">
  <requestId>59dbff89-35bd-4eac-99ed-be587EXAMPLE</requestId>
  <reservedInstancesListingsSet/>
</DescribeReservedInstancesListingsResponse>"""
