from moto.core.responses import ActionResult

from ._base_response import EC2BaseResponse


class SpotDatafeedResponse(EC2BaseResponse):
    def create_spot_datafeed_subscription(self) -> ActionResult:
        bucket = self._get_param("Bucket")
        prefix = self._get_param("Prefix")
        self.error_on_dryrun()
        sub = self.ec2_backend.create_spot_datafeed_subscription(
            bucket=bucket,
            prefix=prefix,
        )
        result = {
            "SpotDatafeedSubscription": {
                "OwnerId": sub.owner_id,
                "Bucket": sub.bucket,
                "Prefix": sub.prefix,
                "State": sub.state,
            }
        }
        return ActionResult(result)

    def delete_spot_datafeed_subscription(self) -> ActionResult:
        self.error_on_dryrun()
        self.ec2_backend.delete_spot_datafeed_subscription()
        return ActionResult({"Return": True})

    def describe_spot_datafeed_subscription(self) -> ActionResult:
        sub = self.ec2_backend.describe_spot_datafeed_subscription()
        if sub:
            result = {
                "SpotDatafeedSubscription": {
                    "OwnerId": sub.owner_id,
                    "Bucket": sub.bucket,
                    "Prefix": sub.prefix,
                    "State": sub.state,
                }
            }
        else:
            result = {}
        return ActionResult(result)
