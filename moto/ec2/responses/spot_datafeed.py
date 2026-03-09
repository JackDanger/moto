from ._base_response import EC2BaseResponse


class SpotDatafeedResponse(EC2BaseResponse):
    def create_spot_datafeed_subscription(self) -> str:
        bucket = self._get_param("Bucket")
        prefix = self._get_param("Prefix")
        self.error_on_dryrun()
        sub = self.ec2_backend.create_spot_datafeed_subscription(
            bucket=bucket,
            prefix=prefix,
        )
        template = self.response_template(CREATE_SPOT_DATAFEED_SUBSCRIPTION)
        return template.render(sub=sub)

    def delete_spot_datafeed_subscription(self) -> str:
        self.error_on_dryrun()
        self.ec2_backend.delete_spot_datafeed_subscription()
        template = self.response_template(DELETE_SPOT_DATAFEED_SUBSCRIPTION)
        return template.render()

    def describe_spot_datafeed_subscription(self) -> str:
        sub = self.ec2_backend.describe_spot_datafeed_subscription()
        template = self.response_template(DESCRIBE_SPOT_DATAFEED_SUBSCRIPTION)
        return template.render(sub=sub)


CREATE_SPOT_DATAFEED_SUBSCRIPTION = """<CreateSpotDatafeedSubscriptionResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
  <requestId>7a62c49f-347e-4fc4-9331-6e8eEXAMPLE</requestId>
  <spotDatafeedSubscription>
    <ownerId>{{ sub.owner_id }}</ownerId>
    <bucket>{{ sub.bucket }}</bucket>
    <prefix>{{ sub.prefix }}</prefix>
    <state>{{ sub.state }}</state>
  </spotDatafeedSubscription>
</CreateSpotDatafeedSubscriptionResponse>"""

DELETE_SPOT_DATAFEED_SUBSCRIPTION = """<DeleteSpotDatafeedSubscriptionResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
  <requestId>7a62c49f-347e-4fc4-9331-6e8eEXAMPLE</requestId>
  <return>true</return>
</DeleteSpotDatafeedSubscriptionResponse>"""

DESCRIBE_SPOT_DATAFEED_SUBSCRIPTION = """<DescribeSpotDatafeedSubscriptionResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
  <requestId>7a62c49f-347e-4fc4-9331-6e8eEXAMPLE</requestId>
  {% if sub %}
  <spotDatafeedSubscription>
    <ownerId>{{ sub.owner_id }}</ownerId>
    <bucket>{{ sub.bucket }}</bucket>
    <prefix>{{ sub.prefix }}</prefix>
    <state>{{ sub.state }}</state>
  </spotDatafeedSubscription>
  {% endif %}
</DescribeSpotDatafeedSubscriptionResponse>"""
