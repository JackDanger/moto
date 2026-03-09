from moto.ec2.utils import add_tag_specification

from ._base_response import EC2BaseResponse


class HostReservationResponse(EC2BaseResponse):
    def describe_host_reservation_offerings(self) -> str:
        offering_id = self._get_param("OfferingId")
        offerings = self.ec2_backend.describe_host_reservation_offerings(
            offering_id=offering_id,
        )
        template = self.response_template(DESCRIBE_HOST_RESERVATION_OFFERINGS)
        return template.render(offerings=offerings)

    def describe_host_reservations(self) -> str:
        reservation_ids = self._get_param("HostReservationIdSet", [])
        reservations = self.ec2_backend.describe_host_reservations(
            host_reservation_id_set=reservation_ids or None,
        )
        template = self.response_template(DESCRIBE_HOST_RESERVATIONS)
        return template.render(reservations=reservations)

    def get_host_reservation_purchase_preview(self) -> str:
        offering_id = self._get_param("OfferingId")
        host_id_set = self._get_param("HostIdSet", [])
        preview = self.ec2_backend.get_host_reservation_purchase_preview(
            offering_id=offering_id,
            host_id_set=host_id_set,
        )
        template = self.response_template(GET_HOST_RESERVATION_PURCHASE_PREVIEW)
        return template.render(preview=preview)

    def purchase_host_reservation(self) -> str:
        offering_id = self._get_param("OfferingId")
        host_id_set = self._get_param("HostIdSet", [])
        tags = add_tag_specification(self._get_param("TagSpecifications", []))
        reservation = self.ec2_backend.purchase_host_reservation(
            offering_id=offering_id,
            host_id_set=host_id_set,
            tags=tags,
        )
        template = self.response_template(PURCHASE_HOST_RESERVATION)
        return template.render(reservation=reservation)


DESCRIBE_HOST_RESERVATION_OFFERINGS = """<DescribeHostReservationOfferingsResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
  <requestId>7a62c49f-347e-4fc4-9331-6e8eEXAMPLE</requestId>
  <offeringSet>
    {% for offering in offerings %}
    <item>
      <offeringId>{{ offering.offering_id }}</offeringId>
      <instanceFamily>{{ offering.instance_family }}</instanceFamily>
      <paymentOption>{{ offering.payment_option }}</paymentOption>
      <upfrontPrice>{{ offering.upfront_price }}</upfrontPrice>
      <hourlyPrice>{{ offering.hourly_price }}</hourlyPrice>
      <duration>{{ offering.duration }}</duration>
      <currencyCode>{{ offering.currency_code }}</currencyCode>
    </item>
    {% endfor %}
  </offeringSet>
</DescribeHostReservationOfferingsResponse>"""

DESCRIBE_HOST_RESERVATIONS = """<DescribeHostReservationsResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
  <requestId>7a62c49f-347e-4fc4-9331-6e8eEXAMPLE</requestId>
  <hostReservationSet>
    {% for r in reservations %}
    <item>
      <hostReservationId>{{ r.id }}</hostReservationId>
      <offeringId>{{ r.offering_id }}</offeringId>
      <instanceFamily>{{ r.instance_family }}</instanceFamily>
      <paymentOption>{{ r.payment_option }}</paymentOption>
      <state>{{ r.state }}</state>
      <count>{{ r.count }}</count>
      <duration>{{ r.duration }}</duration>
      <upfrontPrice>{{ r.upfront_price }}</upfrontPrice>
      <hourlyPrice>{{ r.hourly_price }}</hourlyPrice>
      <currencyCode>{{ r.currency_code }}</currencyCode>
      <start>{{ r.start }}</start>
      <hostIdSet>
        {% for hid in r.host_id_set %}
        <item>{{ hid }}</item>
        {% endfor %}
      </hostIdSet>
      <tagSet>
        {% for tag in r.get_tags() %}
        <item>
          <key>{{ tag.key }}</key>
          <value>{{ tag.value }}</value>
        </item>
        {% endfor %}
      </tagSet>
    </item>
    {% endfor %}
  </hostReservationSet>
</DescribeHostReservationsResponse>"""

GET_HOST_RESERVATION_PURCHASE_PREVIEW = """<GetHostReservationPurchasePreviewResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
  <requestId>7a62c49f-347e-4fc4-9331-6e8eEXAMPLE</requestId>
  <currencyCode>{{ preview.currency_code }}</currencyCode>
  <totalUpfrontPrice>{{ preview.total_upfront_price }}</totalUpfrontPrice>
  <totalHourlyPrice>{{ preview.total_hourly_price }}</totalHourlyPrice>
  <purchase>
    {% for p in preview.purchase %}
    <item>
      <offeringId>{{ p.offering_id }}</offeringId>
      <instanceFamily>{{ p.instance_family }}</instanceFamily>
      <paymentOption>{{ p.payment_option }}</paymentOption>
      <upfrontPrice>{{ p.upfront_price }}</upfrontPrice>
      <hourlyPrice>{{ p.hourly_price }}</hourlyPrice>
      <duration>{{ p.duration }}</duration>
      <currencyCode>{{ p.currency_code }}</currencyCode>
    </item>
    {% endfor %}
  </purchase>
</GetHostReservationPurchasePreviewResponse>"""

PURCHASE_HOST_RESERVATION = """<PurchaseHostReservationResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
  <requestId>7a62c49f-347e-4fc4-9331-6e8eEXAMPLE</requestId>
  <currencyCode>{{ reservation.currency_code }}</currencyCode>
  <totalUpfrontPrice>{{ reservation.upfront_price }}</totalUpfrontPrice>
  <totalHourlyPrice>{{ reservation.hourly_price }}</totalHourlyPrice>
  <purchase>
    <item>
      <hostReservationId>{{ reservation.id }}</hostReservationId>
      <offeringId>{{ reservation.offering_id }}</offeringId>
      <instanceFamily>{{ reservation.instance_family }}</instanceFamily>
      <paymentOption>{{ reservation.payment_option }}</paymentOption>
      <upfrontPrice>{{ reservation.upfront_price }}</upfrontPrice>
      <hourlyPrice>{{ reservation.hourly_price }}</hourlyPrice>
      <duration>{{ reservation.duration }}</duration>
      <currencyCode>{{ reservation.currency_code }}</currencyCode>
      <hostIdSet>
        {% for hid in reservation.host_id_set %}
        <item>{{ hid }}</item>
        {% endfor %}
      </hostIdSet>
    </item>
  </purchase>
</PurchaseHostReservationResponse>"""
