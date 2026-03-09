from typing import Any, Optional


class SpotDatafeedSubscription:
    def __init__(
        self,
        ec2_backend: Any,
        bucket: str,
        prefix: Optional[str] = None,
    ):
        self.ec2_backend = ec2_backend
        self.bucket = bucket
        self.prefix = prefix or ""
        self.state = "Active"
        self.owner_id = ec2_backend.account_id
        self.fault = None


class SpotDatafeedBackend:
    def __init__(self) -> None:
        self.spot_datafeed_subscription: Optional[SpotDatafeedSubscription] = None

    def create_spot_datafeed_subscription(
        self, bucket: str, prefix: Optional[str] = None
    ) -> SpotDatafeedSubscription:
        self.spot_datafeed_subscription = SpotDatafeedSubscription(
            self, bucket=bucket, prefix=prefix
        )
        return self.spot_datafeed_subscription

    def delete_spot_datafeed_subscription(self) -> None:
        self.spot_datafeed_subscription = None

    def describe_spot_datafeed_subscription(
        self,
    ) -> Optional[SpotDatafeedSubscription]:
        return self.spot_datafeed_subscription
