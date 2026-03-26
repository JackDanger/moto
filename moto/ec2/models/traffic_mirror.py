from typing import Any, Optional

from ..utils import (
    random_traffic_mirror_filter_id,
    random_traffic_mirror_filter_rule_id,
    random_traffic_mirror_session_id,
    random_traffic_mirror_target_id,
)
from .core import TaggedEC2Resource


class TrafficMirrorFilterRule:
    def __init__(
        self,
        traffic_mirror_filter_id: str,
        traffic_direction: str,
        rule_number: int,
        rule_action: str,
        protocol: Optional[int] = None,
        destination_cidr_block: str = "0.0.0.0/0",
        source_cidr_block: str = "0.0.0.0/0",
        destination_port_range: Optional[dict[str, int]] = None,
        source_port_range: Optional[dict[str, int]] = None,
        description: str = "",
    ):
        self.id = random_traffic_mirror_filter_rule_id()
        self.traffic_mirror_filter_id = traffic_mirror_filter_id
        self.traffic_direction = traffic_direction
        self.rule_number = rule_number
        self.rule_action = rule_action
        self.protocol = protocol
        self.destination_cidr_block = destination_cidr_block
        self.source_cidr_block = source_cidr_block
        self.destination_port_range = destination_port_range
        self.source_port_range = source_port_range
        self.description = description


class TrafficMirrorFilter(TaggedEC2Resource):
    def __init__(
        self,
        ec2_backend: Any,
        description: str = "",
        network_services: Optional[list[str]] = None,
        tags: Optional[dict[str, str]] = None,
    ):
        self.ec2_backend = ec2_backend
        self.id = random_traffic_mirror_filter_id()
        self.description = description
        self.network_services = network_services or []
        self.ingress_rules: list[TrafficMirrorFilterRule] = []
        self.egress_rules: list[TrafficMirrorFilterRule] = []
        self.add_tags(tags or {})


class TrafficMirrorTarget(TaggedEC2Resource):
    def __init__(
        self,
        ec2_backend: Any,
        network_interface_id: Optional[str] = None,
        network_load_balancer_arn: Optional[str] = None,
        gateway_load_balancer_endpoint_id: Optional[str] = None,
        description: str = "",
        tags: Optional[dict[str, str]] = None,
    ):
        self.ec2_backend = ec2_backend
        self.id = random_traffic_mirror_target_id()
        self.network_interface_id = network_interface_id
        self.network_load_balancer_arn = network_load_balancer_arn
        self.gateway_load_balancer_endpoint_id = (
            gateway_load_balancer_endpoint_id
        )
        self.description = description
        if network_interface_id:
            self.target_type = "network-interface"
        elif network_load_balancer_arn:
            self.target_type = "network-load-balancer"
        elif gateway_load_balancer_endpoint_id:
            self.target_type = "gateway-load-balancer-endpoint"
        else:
            self.target_type = "network-interface"
        self.add_tags(tags or {})

    @property
    def owner_id(self) -> str:
        return self.ec2_backend.account_id


class TrafficMirrorSession(TaggedEC2Resource):
    def __init__(
        self,
        ec2_backend: Any,
        network_interface_id: str,
        traffic_mirror_target_id: str,
        traffic_mirror_filter_id: str,
        session_number: int,
        packet_length: Optional[int] = None,
        virtual_network_id: Optional[int] = None,
        description: str = "",
        tags: Optional[dict[str, str]] = None,
    ):
        self.ec2_backend = ec2_backend
        self.id = random_traffic_mirror_session_id()
        self.network_interface_id = network_interface_id
        self.traffic_mirror_target_id = traffic_mirror_target_id
        self.traffic_mirror_filter_id = traffic_mirror_filter_id
        self.session_number = session_number
        self.packet_length = packet_length
        self.virtual_network_id = virtual_network_id
        self.description = description
        self.add_tags(tags or {})

    @property
    def owner_id(self) -> str:
        return self.ec2_backend.account_id


class TrafficMirrorBackend:
    def __init__(self) -> None:
        self.traffic_mirror_filters: dict[str, TrafficMirrorFilter] = {}
        self.traffic_mirror_targets: dict[str, TrafficMirrorTarget] = {}
        self.traffic_mirror_sessions: dict[str, TrafficMirrorSession] = {}

    def create_traffic_mirror_filter(
        self,
        description: str = "",
        network_services: Optional[list[str]] = None,
        tags: Optional[dict[str, str]] = None,
    ) -> TrafficMirrorFilter:
        tmf = TrafficMirrorFilter(
            self,
            description=description,
            network_services=network_services,
            tags=tags,
        )
        self.traffic_mirror_filters[tmf.id] = tmf
        return tmf

    def delete_traffic_mirror_filter(
        self, traffic_mirror_filter_id: str
    ) -> str:
        if traffic_mirror_filter_id not in self.traffic_mirror_filters:
            from ..exceptions import InvalidTrafficMirrorFilterIdError

            raise InvalidTrafficMirrorFilterIdError(traffic_mirror_filter_id)
        self.traffic_mirror_filters.pop(traffic_mirror_filter_id)
        return traffic_mirror_filter_id

    def describe_traffic_mirror_filters(
        self,
        traffic_mirror_filter_ids: Optional[list[str]] = None,
    ) -> list[TrafficMirrorFilter]:
        filters = list(self.traffic_mirror_filters.values())
        if traffic_mirror_filter_ids:
            filters = [
                f for f in filters if f.id in traffic_mirror_filter_ids
            ]
        return filters

    def create_traffic_mirror_filter_rule(
        self,
        traffic_mirror_filter_id: str,
        traffic_direction: str,
        rule_number: int,
        rule_action: str,
        protocol: Optional[int] = None,
        destination_cidr_block: str = "0.0.0.0/0",
        source_cidr_block: str = "0.0.0.0/0",
        destination_port_range: Optional[dict[str, int]] = None,
        source_port_range: Optional[dict[str, int]] = None,
        description: str = "",
    ) -> TrafficMirrorFilterRule:
        tmf = self.traffic_mirror_filters.get(traffic_mirror_filter_id)
        if not tmf:
            from ..exceptions import InvalidTrafficMirrorFilterIdError

            raise InvalidTrafficMirrorFilterIdError(traffic_mirror_filter_id)
        rule = TrafficMirrorFilterRule(
            traffic_mirror_filter_id=traffic_mirror_filter_id,
            traffic_direction=traffic_direction,
            rule_number=rule_number,
            rule_action=rule_action,
            protocol=protocol,
            destination_cidr_block=destination_cidr_block,
            source_cidr_block=source_cidr_block,
            destination_port_range=destination_port_range,
            source_port_range=source_port_range,
            description=description,
        )
        if traffic_direction == "ingress":
            tmf.ingress_rules.append(rule)
        else:
            tmf.egress_rules.append(rule)
        return rule

    def delete_traffic_mirror_filter_rule(
        self, traffic_mirror_filter_rule_id: str
    ) -> str:
        for tmf in self.traffic_mirror_filters.values():
            for rule_list in [tmf.ingress_rules, tmf.egress_rules]:
                for idx, rule in enumerate(rule_list):
                    if rule.id == traffic_mirror_filter_rule_id:
                        rule_list.pop(idx)
                        return traffic_mirror_filter_rule_id
        from ..exceptions import InvalidTrafficMirrorFilterRuleIdError

        raise InvalidTrafficMirrorFilterRuleIdError(
            traffic_mirror_filter_rule_id
        )

    def describe_traffic_mirror_filter_rules(
        self,
        traffic_mirror_filter_rule_ids: Optional[list[str]] = None,
        traffic_mirror_filter_id: Optional[str] = None,
    ) -> list[TrafficMirrorFilterRule]:
        rules: list[TrafficMirrorFilterRule] = []
        filters = list(self.traffic_mirror_filters.values())
        if traffic_mirror_filter_id:
            filters = [
                f for f in filters if f.id == traffic_mirror_filter_id
            ]
        for tmf in filters:
            rules.extend(tmf.ingress_rules)
            rules.extend(tmf.egress_rules)
        if traffic_mirror_filter_rule_ids:
            rules = [
                r for r in rules if r.id in traffic_mirror_filter_rule_ids
            ]
        return rules

    def create_traffic_mirror_target(
        self,
        network_interface_id: Optional[str] = None,
        network_load_balancer_arn: Optional[str] = None,
        gateway_load_balancer_endpoint_id: Optional[str] = None,
        description: str = "",
        tags: Optional[dict[str, str]] = None,
    ) -> TrafficMirrorTarget:
        tmt = TrafficMirrorTarget(
            self,
            network_interface_id=network_interface_id,
            network_load_balancer_arn=network_load_balancer_arn,
            gateway_load_balancer_endpoint_id=gateway_load_balancer_endpoint_id,
            description=description,
            tags=tags,
        )
        self.traffic_mirror_targets[tmt.id] = tmt
        return tmt

    def delete_traffic_mirror_target(
        self, traffic_mirror_target_id: str
    ) -> str:
        if traffic_mirror_target_id not in self.traffic_mirror_targets:
            from ..exceptions import InvalidTrafficMirrorTargetIdError

            raise InvalidTrafficMirrorTargetIdError(traffic_mirror_target_id)
        self.traffic_mirror_targets.pop(traffic_mirror_target_id)
        return traffic_mirror_target_id

    def describe_traffic_mirror_targets(
        self,
        traffic_mirror_target_ids: Optional[list[str]] = None,
    ) -> list[TrafficMirrorTarget]:
        targets = list(self.traffic_mirror_targets.values())
        if traffic_mirror_target_ids:
            targets = [
                t for t in targets if t.id in traffic_mirror_target_ids
            ]
        return targets

    def create_traffic_mirror_session(
        self,
        network_interface_id: str,
        traffic_mirror_target_id: str,
        traffic_mirror_filter_id: str,
        session_number: int,
        packet_length: Optional[int] = None,
        virtual_network_id: Optional[int] = None,
        description: str = "",
        tags: Optional[dict[str, str]] = None,
    ) -> TrafficMirrorSession:
        tms = TrafficMirrorSession(
            self,
            network_interface_id=network_interface_id,
            traffic_mirror_target_id=traffic_mirror_target_id,
            traffic_mirror_filter_id=traffic_mirror_filter_id,
            session_number=session_number,
            packet_length=packet_length,
            virtual_network_id=virtual_network_id,
            description=description,
            tags=tags,
        )
        self.traffic_mirror_sessions[tms.id] = tms
        return tms

    def delete_traffic_mirror_session(
        self, traffic_mirror_session_id: str
    ) -> str:
        if traffic_mirror_session_id not in self.traffic_mirror_sessions:
            from ..exceptions import InvalidTrafficMirrorSessionIdError

            raise InvalidTrafficMirrorSessionIdError(
                traffic_mirror_session_id
            )
        self.traffic_mirror_sessions.pop(traffic_mirror_session_id)
        return traffic_mirror_session_id

    def describe_traffic_mirror_sessions(
        self,
        traffic_mirror_session_ids: Optional[list[str]] = None,
    ) -> list[TrafficMirrorSession]:
        sessions = list(self.traffic_mirror_sessions.values())
        if traffic_mirror_session_ids:
            sessions = [
                s for s in sessions if s.id in traffic_mirror_session_ids
            ]
        return sessions

    def modify_traffic_mirror_filter_network_services(
        self,
        traffic_mirror_filter_id: str,
        add_network_services: Optional[list[str]] = None,
        remove_network_services: Optional[list[str]] = None,
    ) -> TrafficMirrorFilter:
        tmf = self.traffic_mirror_filters.get(traffic_mirror_filter_id)
        if not tmf:
            from ..exceptions import InvalidTrafficMirrorFilterIdError

            raise InvalidTrafficMirrorFilterIdError(traffic_mirror_filter_id)
        for svc in add_network_services or []:
            if svc not in tmf.network_services:
                tmf.network_services.append(svc)
        for svc in remove_network_services or []:
            if svc in tmf.network_services:
                tmf.network_services.remove(svc)
        return tmf

    def modify_traffic_mirror_filter_rule(
        self,
        traffic_mirror_filter_rule_id: str,
        traffic_direction: Optional[str] = None,
        rule_number: Optional[int] = None,
        rule_action: Optional[str] = None,
        protocol: Optional[int] = None,
        destination_cidr_block: Optional[str] = None,
        source_cidr_block: Optional[str] = None,
        description: Optional[str] = None,
    ) -> TrafficMirrorFilterRule:
        rule = None
        for tmf in self.traffic_mirror_filters.values():
            for r in tmf.ingress_rules + tmf.egress_rules:
                if r.id == traffic_mirror_filter_rule_id:
                    rule = r
                    break
            if rule:
                break
        if not rule:
            from ..exceptions import InvalidTrafficMirrorFilterRuleIdError

            raise InvalidTrafficMirrorFilterRuleIdError(traffic_mirror_filter_rule_id)
        if traffic_direction is not None:
            rule.traffic_direction = traffic_direction
        if rule_number is not None:
            rule.rule_number = rule_number
        if rule_action is not None:
            rule.rule_action = rule_action
        if protocol is not None:
            rule.protocol = protocol
        if destination_cidr_block is not None:
            rule.destination_cidr_block = destination_cidr_block
        if source_cidr_block is not None:
            rule.source_cidr_block = source_cidr_block
        if description is not None:
            rule.description = description
        return rule

    def modify_traffic_mirror_session(
        self,
        traffic_mirror_session_id: str,
        traffic_mirror_target_id: Optional[str] = None,
        traffic_mirror_filter_id: Optional[str] = None,
        session_number: Optional[int] = None,
        packet_length: Optional[int] = None,
        virtual_network_id: Optional[int] = None,
        description: Optional[str] = None,
    ) -> TrafficMirrorSession:
        session = self.traffic_mirror_sessions.get(traffic_mirror_session_id)
        if not session:
            from ..exceptions import InvalidTrafficMirrorSessionIdError

            raise InvalidTrafficMirrorSessionIdError(traffic_mirror_session_id)
        if traffic_mirror_target_id is not None:
            session.traffic_mirror_target_id = traffic_mirror_target_id
        if traffic_mirror_filter_id is not None:
            session.traffic_mirror_filter_id = traffic_mirror_filter_id
        if session_number is not None:
            session.session_number = session_number
        if packet_length is not None:
            session.packet_length = packet_length
        if virtual_network_id is not None:
            session.virtual_network_id = virtual_network_id
        if description is not None:
            session.description = description
        return session
