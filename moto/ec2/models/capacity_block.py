from typing import Any, Optional

from moto.core.utils import iso_8601_datetime_with_milliseconds, utcnow

from ..utils import random_id


class CapacityBlockOffering:
    def __init__(
        self,
        instance_type: str = "p5.48xlarge",
        availability_zone: str = "us-east-1a",
        capacity_duration_hours: int = 24,
        instance_count: int = 1,
        currency_code: str = "USD",
        upfront_fee: str = "0.00",
    ):
        self.id = random_id(prefix="cbr-")
        self.instance_type = instance_type
        self.availability_zone = availability_zone
        self.capacity_duration_hours = capacity_duration_hours
        self.instance_count = instance_count
        self.currency_code = currency_code
        self.upfront_fee = upfront_fee
        self._start_date = utcnow()
        self._end_date = utcnow()
        self.tenancy = "default"

    @property
    def start_date(self) -> str:
        return iso_8601_datetime_with_milliseconds(self._start_date)

    @property
    def end_date(self) -> str:
        return iso_8601_datetime_with_milliseconds(self._end_date)


class CapacityBlockBackend:
    def describe_capacity_block_offerings(
        self,
        instance_type: Optional[str] = None,
        instance_count: int = 1,
        capacity_duration_hours: int = 24,
    ) -> list[CapacityBlockOffering]:
        offering = CapacityBlockOffering(
            instance_type=instance_type or "p5.48xlarge",
            instance_count=instance_count,
            capacity_duration_hours=capacity_duration_hours,
        )
        return [offering]

    def purchase_capacity_block(
        self,
        capacity_block_offering_id: str,
        instance_platform: str = "Linux/UNIX",
    ) -> dict[str, Any]:
        return {
            "capacity_reservation_id": random_id(prefix="cr-"),
            "instance_type": "p5.48xlarge",
            "instance_platform": instance_platform,
            "availability_zone": "us-east-1a",
            "instance_count": 1,
            "state": "payment-pending",
        }
