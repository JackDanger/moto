from typing import Any, Optional

from moto.core.utils import iso_8601_datetime_with_milliseconds, utcnow

from ..utils import random_id
from .core import TaggedEC2Resource


class HostReservationOffering:
    def __init__(
        self,
        offering_id: str,
        instance_family: str,
        payment_option: str,
        upfront_price: str,
        hourly_price: str,
        duration: int,
        currency_code: str = "USD",
    ):
        self.offering_id = offering_id
        self.instance_family = instance_family
        self.payment_option = payment_option
        self.upfront_price = upfront_price
        self.hourly_price = hourly_price
        self.duration = duration
        self.currency_code = currency_code


class HostReservation(TaggedEC2Resource):
    def __init__(
        self,
        ec2_backend: Any,
        offering_id: str,
        host_id_set: list[str],
        instance_family: str = "m5",
        payment_option: str = "AllUpfront",
        tags: Optional[dict[str, str]] = None,
    ):
        self.ec2_backend = ec2_backend
        self.id = random_id(prefix="hr-")
        self.offering_id = offering_id
        self.host_id_set = host_id_set
        self.instance_family = instance_family
        self.payment_option = payment_option
        self.state = "active"
        self.count = len(host_id_set)
        self.duration = 31536000
        self.upfront_price = "0.0"
        self.hourly_price = "0.0"
        self.currency_code = "USD"
        self._start = utcnow()
        self._end = None
        self.add_tags(tags or {})

    @property
    def start(self) -> str:
        return iso_8601_datetime_with_milliseconds(self._start)


# Default offerings
DEFAULT_OFFERINGS = [
    HostReservationOffering(
        offering_id="hro-0001example",
        instance_family="m5",
        payment_option="AllUpfront",
        upfront_price="1000.00",
        hourly_price="0.00",
        duration=31536000,
    ),
    HostReservationOffering(
        offering_id="hro-0002example",
        instance_family="c5",
        payment_option="NoUpfront",
        upfront_price="0.00",
        hourly_price="1.50",
        duration=31536000,
    ),
]


class HostReservationBackend:
    def __init__(self) -> None:
        self.host_reservations: dict[str, HostReservation] = {}

    def describe_host_reservation_offerings(
        self,
        offering_id: Optional[str] = None,
    ) -> list[HostReservationOffering]:
        offerings = DEFAULT_OFFERINGS
        if offering_id:
            offerings = [o for o in offerings if o.offering_id == offering_id]
        return offerings

    def describe_host_reservations(
        self,
        host_reservation_id_set: Optional[list[str]] = None,
    ) -> list[HostReservation]:
        reservations = list(self.host_reservations.values())
        if host_reservation_id_set:
            reservations = [r for r in reservations if r.id in host_reservation_id_set]
        return reservations

    def get_host_reservation_purchase_preview(
        self,
        offering_id: str,
        host_id_set: list[str],
    ) -> dict[str, Any]:
        return {
            "currency_code": "USD",
            "total_upfront_price": "0.00",
            "total_hourly_price": "0.00",
            "purchase": [
                {
                    "host_id_set": host_id_set,
                    "offering_id": offering_id,
                    "instance_family": "m5",
                    "payment_option": "AllUpfront",
                    "upfront_price": "0.00",
                    "hourly_price": "0.00",
                    "duration": 31536000,
                    "currency_code": "USD",
                }
            ],
        }

    def purchase_host_reservation(
        self,
        offering_id: str,
        host_id_set: list[str],
        tags: Optional[dict[str, str]] = None,
    ) -> HostReservation:
        reservation = HostReservation(
            self,
            offering_id=offering_id,
            host_id_set=host_id_set,
            tags=tags,
        )
        self.host_reservations[reservation.id] = reservation
        return reservation
