from moto.ec2.utils import add_tag_specification

from ._base_response import EC2BaseResponse


class TrafficMirrorResponse(EC2BaseResponse):
    def create_traffic_mirror_filter(self) -> str:
        description = self._get_param("Description", "")
        network_services = self._get_param("NetworkService", [])
        tags = add_tag_specification(
            self._get_param("TagSpecifications", [])
        )
        tmf = self.ec2_backend.create_traffic_mirror_filter(
            description=description,
            network_services=network_services or None,
            tags=tags,
        )
        template = self.response_template(CREATE_TRAFFIC_MIRROR_FILTER)
        return template.render(tmf=tmf)

    def delete_traffic_mirror_filter(self) -> str:
        traffic_mirror_filter_id = self._get_param(
            "TrafficMirrorFilterId"
        )
        self.ec2_backend.delete_traffic_mirror_filter(
            traffic_mirror_filter_id
        )
        template = self.response_template(DELETE_TRAFFIC_MIRROR_FILTER)
        return template.render(
            traffic_mirror_filter_id=traffic_mirror_filter_id
        )

    def describe_traffic_mirror_filters(self) -> str:
        filter_ids = self._get_param("TrafficMirrorFilterId", [])
        filters = self.ec2_backend.describe_traffic_mirror_filters(
            traffic_mirror_filter_ids=filter_ids or None,
        )
        template = self.response_template(
            DESCRIBE_TRAFFIC_MIRROR_FILTERS
        )
        return template.render(filters=filters)

    def create_traffic_mirror_filter_rule(self) -> str:
        traffic_mirror_filter_id = self._get_param(
            "TrafficMirrorFilterId"
        )
        traffic_direction = self._get_param("TrafficDirection")
        rule_number = int(self._get_param("RuleNumber"))
        rule_action = self._get_param("RuleAction")
        protocol = self._get_param("Protocol")
        dst_cidr = self._get_param(
            "DestinationCidrBlock", "0.0.0.0/0"
        )
        src_cidr = self._get_param("SourceCidrBlock", "0.0.0.0/0")
        dst_port_range = self._get_param("DestinationPortRange")
        src_port_range = self._get_param("SourcePortRange")
        description = self._get_param("Description", "")
        rule = self.ec2_backend.create_traffic_mirror_filter_rule(
            traffic_mirror_filter_id=traffic_mirror_filter_id,
            traffic_direction=traffic_direction,
            rule_number=rule_number,
            rule_action=rule_action,
            protocol=int(protocol) if protocol else None,
            destination_cidr_block=dst_cidr,
            source_cidr_block=src_cidr,
            destination_port_range=dst_port_range,
            source_port_range=src_port_range,
            description=description,
        )
        template = self.response_template(
            CREATE_TRAFFIC_MIRROR_FILTER_RULE
        )
        return template.render(rule=rule)

    def delete_traffic_mirror_filter_rule(self) -> str:
        rule_id = self._get_param("TrafficMirrorFilterRuleId")
        self.ec2_backend.delete_traffic_mirror_filter_rule(rule_id)
        template = self.response_template(
            DELETE_TRAFFIC_MIRROR_FILTER_RULE
        )
        return template.render(rule_id=rule_id)

    def describe_traffic_mirror_filter_rules(self) -> str:
        rule_ids = self._get_param("TrafficMirrorFilterRuleId", [])
        filter_id = self._get_param("TrafficMirrorFilterId")
        rules = self.ec2_backend.describe_traffic_mirror_filter_rules(
            traffic_mirror_filter_rule_ids=rule_ids or None,
            traffic_mirror_filter_id=filter_id,
        )
        template = self.response_template(
            DESCRIBE_TRAFFIC_MIRROR_FILTER_RULES
        )
        return template.render(rules=rules)

    def create_traffic_mirror_target(self) -> str:
        network_interface_id = self._get_param("NetworkInterfaceId")
        network_load_balancer_arn = self._get_param(
            "NetworkLoadBalancerArn"
        )
        gateway_lb_endpoint_id = self._get_param(
            "GatewayLoadBalancerEndpointId"
        )
        description = self._get_param("Description", "")
        tags = add_tag_specification(
            self._get_param("TagSpecifications", [])
        )
        tmt = self.ec2_backend.create_traffic_mirror_target(
            network_interface_id=network_interface_id,
            network_load_balancer_arn=network_load_balancer_arn,
            gateway_load_balancer_endpoint_id=gateway_lb_endpoint_id,
            description=description,
            tags=tags,
        )
        template = self.response_template(CREATE_TRAFFIC_MIRROR_TARGET)
        return template.render(tmt=tmt)

    def delete_traffic_mirror_target(self) -> str:
        target_id = self._get_param("TrafficMirrorTargetId")
        self.ec2_backend.delete_traffic_mirror_target(target_id)
        template = self.response_template(DELETE_TRAFFIC_MIRROR_TARGET)
        return template.render(target_id=target_id)

    def describe_traffic_mirror_targets(self) -> str:
        target_ids = self._get_param("TrafficMirrorTargetId", [])
        targets = self.ec2_backend.describe_traffic_mirror_targets(
            traffic_mirror_target_ids=target_ids or None,
        )
        template = self.response_template(
            DESCRIBE_TRAFFIC_MIRROR_TARGETS
        )
        return template.render(targets=targets)

    def create_traffic_mirror_session(self) -> str:
        network_interface_id = self._get_param("NetworkInterfaceId")
        target_id = self._get_param("TrafficMirrorTargetId")
        filter_id = self._get_param("TrafficMirrorFilterId")
        session_number = int(self._get_param("SessionNumber"))
        packet_length = self._get_param("PacketLength")
        virtual_network_id = self._get_param("VirtualNetworkId")
        description = self._get_param("Description", "")
        tags = add_tag_specification(
            self._get_param("TagSpecifications", [])
        )
        tms = self.ec2_backend.create_traffic_mirror_session(
            network_interface_id=network_interface_id,
            traffic_mirror_target_id=target_id,
            traffic_mirror_filter_id=filter_id,
            session_number=session_number,
            packet_length=(
                int(packet_length) if packet_length else None
            ),
            virtual_network_id=(
                int(virtual_network_id) if virtual_network_id else None
            ),
            description=description,
            tags=tags,
        )
        template = self.response_template(CREATE_TRAFFIC_MIRROR_SESSION)
        return template.render(tms=tms)

    def delete_traffic_mirror_session(self) -> str:
        session_id = self._get_param("TrafficMirrorSessionId")
        self.ec2_backend.delete_traffic_mirror_session(session_id)
        template = self.response_template(DELETE_TRAFFIC_MIRROR_SESSION)
        return template.render(session_id=session_id)

    def describe_traffic_mirror_sessions(self) -> str:
        session_ids = self._get_param("TrafficMirrorSessionId", [])
        sessions = self.ec2_backend.describe_traffic_mirror_sessions(
            traffic_mirror_session_ids=session_ids or None,
        )
        template = self.response_template(
            DESCRIBE_TRAFFIC_MIRROR_SESSIONS
        )
        return template.render(sessions=sessions)


CREATE_TRAFFIC_MIRROR_FILTER = """<CreateTrafficMirrorFilterResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
  <requestId>7a62c49f-347e-4fc4-9331-6e8eEXAMPLE</requestId>
  <trafficMirrorFilter>
    <trafficMirrorFilterId>{{ tmf.id }}</trafficMirrorFilterId>
    <description>{{ tmf.description }}</description>
    <networkServiceSet>
      {% for svc in tmf.network_services %}
      <item>{{ svc }}</item>
      {% endfor %}
    </networkServiceSet>
    <tagSet>
      {% for tag in tmf.get_tags() %}
      <item>
        <key>{{ tag.key }}</key>
        <value>{{ tag.value }}</value>
      </item>
      {% endfor %}
    </tagSet>
  </trafficMirrorFilter>
</CreateTrafficMirrorFilterResponse>"""

DELETE_TRAFFIC_MIRROR_FILTER = """<DeleteTrafficMirrorFilterResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
  <requestId>7a62c49f-347e-4fc4-9331-6e8eEXAMPLE</requestId>
  <trafficMirrorFilterId>{{ traffic_mirror_filter_id }}</trafficMirrorFilterId>
</DeleteTrafficMirrorFilterResponse>"""

DESCRIBE_TRAFFIC_MIRROR_FILTERS = """<DescribeTrafficMirrorFiltersResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
  <requestId>7a62c49f-347e-4fc4-9331-6e8eEXAMPLE</requestId>
  <trafficMirrorFilterSet>
    {% for tmf in filters %}
    <item>
      <trafficMirrorFilterId>{{ tmf.id }}</trafficMirrorFilterId>
      <description>{{ tmf.description }}</description>
      <ingressFilterRuleSet>
        {% for rule in tmf.ingress_rules %}
        <item>
          <trafficMirrorFilterRuleId>{{ rule.id }}</trafficMirrorFilterRuleId>
          <trafficMirrorFilterId>{{ rule.traffic_mirror_filter_id }}</trafficMirrorFilterId>
          <trafficDirection>{{ rule.traffic_direction }}</trafficDirection>
          <ruleNumber>{{ rule.rule_number }}</ruleNumber>
          <ruleAction>{{ rule.rule_action }}</ruleAction>
          {% if rule.protocol %}<protocol>{{ rule.protocol }}</protocol>{% endif %}
          <destinationCidrBlock>{{ rule.destination_cidr_block }}</destinationCidrBlock>
          <sourceCidrBlock>{{ rule.source_cidr_block }}</sourceCidrBlock>
        </item>
        {% endfor %}
      </ingressFilterRuleSet>
      <egressFilterRuleSet>
        {% for rule in tmf.egress_rules %}
        <item>
          <trafficMirrorFilterRuleId>{{ rule.id }}</trafficMirrorFilterRuleId>
          <trafficMirrorFilterId>{{ rule.traffic_mirror_filter_id }}</trafficMirrorFilterId>
          <trafficDirection>{{ rule.traffic_direction }}</trafficDirection>
          <ruleNumber>{{ rule.rule_number }}</ruleNumber>
          <ruleAction>{{ rule.rule_action }}</ruleAction>
          {% if rule.protocol %}<protocol>{{ rule.protocol }}</protocol>{% endif %}
          <destinationCidrBlock>{{ rule.destination_cidr_block }}</destinationCidrBlock>
          <sourceCidrBlock>{{ rule.source_cidr_block }}</sourceCidrBlock>
        </item>
        {% endfor %}
      </egressFilterRuleSet>
      <tagSet>
        {% for tag in tmf.get_tags() %}
        <item>
          <key>{{ tag.key }}</key>
          <value>{{ tag.value }}</value>
        </item>
        {% endfor %}
      </tagSet>
    </item>
    {% endfor %}
  </trafficMirrorFilterSet>
</DescribeTrafficMirrorFiltersResponse>"""

CREATE_TRAFFIC_MIRROR_FILTER_RULE = """<CreateTrafficMirrorFilterRuleResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
  <requestId>7a62c49f-347e-4fc4-9331-6e8eEXAMPLE</requestId>
  <trafficMirrorFilterRule>
    <trafficMirrorFilterRuleId>{{ rule.id }}</trafficMirrorFilterRuleId>
    <trafficMirrorFilterId>{{ rule.traffic_mirror_filter_id }}</trafficMirrorFilterId>
    <trafficDirection>{{ rule.traffic_direction }}</trafficDirection>
    <ruleNumber>{{ rule.rule_number }}</ruleNumber>
    <ruleAction>{{ rule.rule_action }}</ruleAction>
    {% if rule.protocol %}<protocol>{{ rule.protocol }}</protocol>{% endif %}
    <destinationCidrBlock>{{ rule.destination_cidr_block }}</destinationCidrBlock>
    <sourceCidrBlock>{{ rule.source_cidr_block }}</sourceCidrBlock>
    <description>{{ rule.description }}</description>
  </trafficMirrorFilterRule>
</CreateTrafficMirrorFilterRuleResponse>"""

DELETE_TRAFFIC_MIRROR_FILTER_RULE = """<DeleteTrafficMirrorFilterRuleResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
  <requestId>7a62c49f-347e-4fc4-9331-6e8eEXAMPLE</requestId>
  <trafficMirrorFilterRuleId>{{ rule_id }}</trafficMirrorFilterRuleId>
</DeleteTrafficMirrorFilterRuleResponse>"""

DESCRIBE_TRAFFIC_MIRROR_FILTER_RULES = """<DescribeTrafficMirrorFilterRulesResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
  <requestId>7a62c49f-347e-4fc4-9331-6e8eEXAMPLE</requestId>
  <trafficMirrorFilterRuleSet>
    {% for rule in rules %}
    <item>
      <trafficMirrorFilterRuleId>{{ rule.id }}</trafficMirrorFilterRuleId>
      <trafficMirrorFilterId>{{ rule.traffic_mirror_filter_id }}</trafficMirrorFilterId>
      <trafficDirection>{{ rule.traffic_direction }}</trafficDirection>
      <ruleNumber>{{ rule.rule_number }}</ruleNumber>
      <ruleAction>{{ rule.rule_action }}</ruleAction>
      {% if rule.protocol %}<protocol>{{ rule.protocol }}</protocol>{% endif %}
      <destinationCidrBlock>{{ rule.destination_cidr_block }}</destinationCidrBlock>
      <sourceCidrBlock>{{ rule.source_cidr_block }}</sourceCidrBlock>
      <description>{{ rule.description }}</description>
    </item>
    {% endfor %}
  </trafficMirrorFilterRuleSet>
</DescribeTrafficMirrorFilterRulesResponse>"""

CREATE_TRAFFIC_MIRROR_TARGET = """<CreateTrafficMirrorTargetResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
  <requestId>7a62c49f-347e-4fc4-9331-6e8eEXAMPLE</requestId>
  <trafficMirrorTarget>
    <trafficMirrorTargetId>{{ tmt.id }}</trafficMirrorTargetId>
    <type>{{ tmt.target_type }}</type>
    {% if tmt.network_interface_id %}
    <networkInterfaceId>{{ tmt.network_interface_id }}</networkInterfaceId>
    {% endif %}
    {% if tmt.network_load_balancer_arn %}
    <networkLoadBalancerArn>{{ tmt.network_load_balancer_arn }}</networkLoadBalancerArn>
    {% endif %}
    <description>{{ tmt.description }}</description>
    <ownerId>{{ tmt.owner_id }}</ownerId>
    <tagSet>
      {% for tag in tmt.get_tags() %}
      <item>
        <key>{{ tag.key }}</key>
        <value>{{ tag.value }}</value>
      </item>
      {% endfor %}
    </tagSet>
  </trafficMirrorTarget>
</CreateTrafficMirrorTargetResponse>"""

DELETE_TRAFFIC_MIRROR_TARGET = """<DeleteTrafficMirrorTargetResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
  <requestId>7a62c49f-347e-4fc4-9331-6e8eEXAMPLE</requestId>
  <trafficMirrorTargetId>{{ target_id }}</trafficMirrorTargetId>
</DeleteTrafficMirrorTargetResponse>"""

DESCRIBE_TRAFFIC_MIRROR_TARGETS = """<DescribeTrafficMirrorTargetsResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
  <requestId>7a62c49f-347e-4fc4-9331-6e8eEXAMPLE</requestId>
  <trafficMirrorTargetSet>
    {% for tmt in targets %}
    <item>
      <trafficMirrorTargetId>{{ tmt.id }}</trafficMirrorTargetId>
      <type>{{ tmt.target_type }}</type>
      {% if tmt.network_interface_id %}
      <networkInterfaceId>{{ tmt.network_interface_id }}</networkInterfaceId>
      {% endif %}
      {% if tmt.network_load_balancer_arn %}
      <networkLoadBalancerArn>{{ tmt.network_load_balancer_arn }}</networkLoadBalancerArn>
      {% endif %}
      <description>{{ tmt.description }}</description>
      <ownerId>{{ tmt.owner_id }}</ownerId>
      <tagSet>
        {% for tag in tmt.get_tags() %}
        <item>
          <key>{{ tag.key }}</key>
          <value>{{ tag.value }}</value>
        </item>
        {% endfor %}
      </tagSet>
    </item>
    {% endfor %}
  </trafficMirrorTargetSet>
</DescribeTrafficMirrorTargetsResponse>"""

CREATE_TRAFFIC_MIRROR_SESSION = """<CreateTrafficMirrorSessionResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
  <requestId>7a62c49f-347e-4fc4-9331-6e8eEXAMPLE</requestId>
  <trafficMirrorSession>
    <trafficMirrorSessionId>{{ tms.id }}</trafficMirrorSessionId>
    <trafficMirrorTargetId>{{ tms.traffic_mirror_target_id }}</trafficMirrorTargetId>
    <trafficMirrorFilterId>{{ tms.traffic_mirror_filter_id }}</trafficMirrorFilterId>
    <networkInterfaceId>{{ tms.network_interface_id }}</networkInterfaceId>
    <ownerId>{{ tms.owner_id }}</ownerId>
    <sessionNumber>{{ tms.session_number }}</sessionNumber>
    {% if tms.packet_length %}<packetLength>{{ tms.packet_length }}</packetLength>{% endif %}
    {% if tms.virtual_network_id %}<virtualNetworkId>{{ tms.virtual_network_id }}</virtualNetworkId>{% endif %}
    <description>{{ tms.description }}</description>
    <tagSet>
      {% for tag in tms.get_tags() %}
      <item>
        <key>{{ tag.key }}</key>
        <value>{{ tag.value }}</value>
      </item>
      {% endfor %}
    </tagSet>
  </trafficMirrorSession>
</CreateTrafficMirrorSessionResponse>"""

DELETE_TRAFFIC_MIRROR_SESSION = """<DeleteTrafficMirrorSessionResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
  <requestId>7a62c49f-347e-4fc4-9331-6e8eEXAMPLE</requestId>
  <trafficMirrorSessionId>{{ session_id }}</trafficMirrorSessionId>
</DeleteTrafficMirrorSessionResponse>"""

DESCRIBE_TRAFFIC_MIRROR_SESSIONS = """<DescribeTrafficMirrorSessionsResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
  <requestId>7a62c49f-347e-4fc4-9331-6e8eEXAMPLE</requestId>
  <trafficMirrorSessionSet>
    {% for tms in sessions %}
    <item>
      <trafficMirrorSessionId>{{ tms.id }}</trafficMirrorSessionId>
      <trafficMirrorTargetId>{{ tms.traffic_mirror_target_id }}</trafficMirrorTargetId>
      <trafficMirrorFilterId>{{ tms.traffic_mirror_filter_id }}</trafficMirrorFilterId>
      <networkInterfaceId>{{ tms.network_interface_id }}</networkInterfaceId>
      <ownerId>{{ tms.owner_id }}</ownerId>
      <sessionNumber>{{ tms.session_number }}</sessionNumber>
      {% if tms.packet_length %}<packetLength>{{ tms.packet_length }}</packetLength>{% endif %}
      {% if tms.virtual_network_id %}<virtualNetworkId>{{ tms.virtual_network_id }}</virtualNetworkId>{% endif %}
      <description>{{ tms.description }}</description>
      <tagSet>
        {% for tag in tms.get_tags() %}
        <item>
          <key>{{ tag.key }}</key>
          <value>{{ tag.value }}</value>
        </item>
        {% endfor %}
      </tagSet>
    </item>
    {% endfor %}
  </trafficMirrorSessionSet>
</DescribeTrafficMirrorSessionsResponse>"""
