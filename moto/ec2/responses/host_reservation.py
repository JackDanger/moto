from moto.core.responses import ActionResult
from moto.ec2.utils import add_tag_specification

from ._base_response import EC2BaseResponse


class HostReservationResponse(EC2BaseResponse):
    def describe_host_reservation_offerings(self) -> ActionResult:
        offering_id = self._get_param("OfferingId")
        offerings = self.ec2_backend.describe_host_reservation_offerings(
            offering_id=offering_id,
        )
        offerings_list = [
            {
                "OfferingId": offering.offering_id,
                "InstanceFamily": offering.instance_family,
                "PaymentOption": offering.payment_option,
                "UpfrontPrice": offering.upfront_price,
                "HourlyPrice": offering.hourly_price,
                "Duration": offering.duration,
                "CurrencyCode": offering.currency_code,
            }
            for offering in offerings
        ]
        return ActionResult({"OfferingSet": offerings_list})

    def describe_host_reservations(self) -> ActionResult:
        reservation_ids = self._get_param("HostReservationIdSet", [])
        reservations = self.ec2_backend.describe_host_reservations(
            host_reservation_id_set=reservation_ids or None,
        )
        reservations_list = [
            {
                "HostReservationId": r.id,
                "OfferingId": r.offering_id,
                "InstanceFamily": r.instance_family,
                "PaymentOption": r.payment_option,
                "State": r.state,
                "Count": r.count,
                "Duration": r.duration,
                "UpfrontPrice": r.upfront_price,
                "HourlyPrice": r.hourly_price,
                "CurrencyCode": r.currency_code,
                "Start": r.start,
                "HostIdSet": r.host_id_set,
                "TagSet": [
                    {"Key": tag.key, "Value": tag.value}
                    for tag in r.get_tags()
                ],
            }
            for r in reservations
        ]
        return ActionResult({"HostReservationSet": reservations_list})

    def get_host_reservation_purchase_preview(self) -> ActionResult:
        offering_id = self._get_param("OfferingId")
        host_id_set = self._get_param("HostIdSet", [])
        preview = self.ec2_backend.get_host_reservation_purchase_preview(
            offering_id=offering_id,
            host_id_set=host_id_set,
        )
        purchase_list = [
            {
                "OfferingId": p["offering_id"],
                "InstanceFamily": p["instance_family"],
                "PaymentOption": p["payment_option"],
                "UpfrontPrice": p["upfront_price"],
                "HourlyPrice": p["hourly_price"],
                "Duration": p["duration"],
                "CurrencyCode": p["currency_code"],
            }
            for p in preview["purchase"]
        ]
        result = {
            "CurrencyCode": preview["currency_code"],
            "TotalUpfrontPrice": preview["total_upfront_price"],
            "TotalHourlyPrice": preview["total_hourly_price"],
            "Purchase": purchase_list,
        }
        return ActionResult(result)

    def purchase_host_reservation(self) -> ActionResult:
        offering_id = self._get_param("OfferingId")
        host_id_set = self._get_param("HostIdSet", [])
        tags = add_tag_specification(self._get_param("TagSpecifications", []))
        reservation = self.ec2_backend.purchase_host_reservation(
            offering_id=offering_id,
            host_id_set=host_id_set,
            tags=tags,
        )
        result = {
            "CurrencyCode": reservation.currency_code,
            "TotalUpfrontPrice": reservation.upfront_price,
            "TotalHourlyPrice": reservation.hourly_price,
            "Purchase": [
                {
                    "HostReservationId": reservation.id,
                    "OfferingId": reservation.offering_id,
                    "InstanceFamily": reservation.instance_family,
                    "PaymentOption": reservation.payment_option,
                    "UpfrontPrice": reservation.upfront_price,
                    "HourlyPrice": reservation.hourly_price,
                    "Duration": reservation.duration,
                    "CurrencyCode": reservation.currency_code,
                    "HostIdSet": reservation.host_id_set,
                }
            ],
        }
        return ActionResult(result)
