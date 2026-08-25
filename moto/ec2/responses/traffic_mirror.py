from moto.core.responses import ActionResult
from moto.ec2.utils import add_tag_specification

from ._base_response import EC2BaseResponse


class TrafficMirrorResponse(EC2BaseResponse):
    def delete_traffic_mirror_filter(self) -> ActionResult:
        traffic_mirror_filter_id = self._get_param("TrafficMirrorFilterId")
        self.ec2_backend.delete_traffic_mirror_filter(traffic_mirror_filter_id)
        result = {"TrafficMirrorFilterId": traffic_mirror_filter_id}
        return ActionResult(result)

    def create_traffic_mirror_filter_rule(self) -> ActionResult:
        traffic_mirror_filter_id = self._get_param("TrafficMirrorFilterId")
        traffic_direction = self._get_param("TrafficDirection")
        rule_number = int(self._get_param("RuleNumber"))
        rule_action = self._get_param("RuleAction")
        protocol = self._get_param("Protocol")
        dst_cidr = self._get_param("DestinationCidrBlock", "0.0.0.0/0")
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
        rule_dict = {
            "TrafficMirrorFilterRuleId": rule.id,
            "TrafficMirrorFilterId": rule.traffic_mirror_filter_id,
            "TrafficDirection": rule.traffic_direction,
            "RuleNumber": rule.rule_number,
            "RuleAction": rule.rule_action,
            "DestinationCidrBlock": rule.destination_cidr_block,
            "SourceCidrBlock": rule.source_cidr_block,
            "Description": rule.description,
        }
        if rule.protocol:
            rule_dict["Protocol"] = rule.protocol
        result = {"TrafficMirrorFilterRule": rule_dict}
        return ActionResult(result)

    def delete_traffic_mirror_filter_rule(self) -> ActionResult:
        rule_id = self._get_param("TrafficMirrorFilterRuleId")
        self.ec2_backend.delete_traffic_mirror_filter_rule(rule_id)
        result = {"TrafficMirrorFilterRuleId": rule_id}
        return ActionResult(result)

    def describe_traffic_mirror_filter_rules(self) -> ActionResult:
        rule_ids = self._get_param("TrafficMirrorFilterRuleId", [])
        filter_id = self._get_param("TrafficMirrorFilterId")
        rules = self.ec2_backend.describe_traffic_mirror_filter_rules(
            traffic_mirror_filter_rule_ids=rule_ids or None,
            traffic_mirror_filter_id=filter_id,
        )
        result = {
            "TrafficMirrorFilterRules": [
                {
                    "TrafficMirrorFilterRuleId": rule.id,
                    "TrafficMirrorFilterId": rule.traffic_mirror_filter_id,
                    "TrafficDirection": rule.traffic_direction,
                    "RuleNumber": rule.rule_number,
                    "RuleAction": rule.rule_action,
                    "DestinationCidrBlock": rule.destination_cidr_block,
                    "SourceCidrBlock": rule.source_cidr_block,
                    "Description": rule.description,
                    **({"Protocol": rule.protocol} if rule.protocol else {}),
                }
                for rule in rules
            ]
        }
        return ActionResult(result)

    def delete_traffic_mirror_target(self) -> ActionResult:
        target_id = self._get_param("TrafficMirrorTargetId")
        self.ec2_backend.delete_traffic_mirror_target(target_id)
        result = {"TrafficMirrorTargetId": target_id}
        return ActionResult(result)

    def create_traffic_mirror_session(self) -> ActionResult:
        network_interface_id = self._get_param("NetworkInterfaceId")
        target_id = self._get_param("TrafficMirrorTargetId")
        filter_id = self._get_param("TrafficMirrorFilterId")
        session_number = int(self._get_param("SessionNumber"))
        packet_length = self._get_param("PacketLength")
        virtual_network_id = self._get_param("VirtualNetworkId")
        description = self._get_param("Description", "")
        tags = add_tag_specification(self._get_param("TagSpecifications", []))
        tms = self.ec2_backend.create_traffic_mirror_session(
            network_interface_id=network_interface_id,
            traffic_mirror_target_id=target_id,
            traffic_mirror_filter_id=filter_id,
            session_number=session_number,
            packet_length=(int(packet_length) if packet_length else None),
            virtual_network_id=(
                int(virtual_network_id) if virtual_network_id else None
            ),
            description=description,
            tags=tags,
        )
        tms_dict = {
            "TrafficMirrorSessionId": tms.id,
            "TrafficMirrorTargetId": tms.traffic_mirror_target_id,
            "TrafficMirrorFilterId": tms.traffic_mirror_filter_id,
            "NetworkInterfaceId": tms.network_interface_id,
            "OwnerId": tms.owner_id,
            "SessionNumber": tms.session_number,
            "Description": tms.description,
            "Tags": [{"Key": tag.key, "Value": tag.value} for tag in tms.get_tags()],
        }
        if tms.packet_length:
            tms_dict["PacketLength"] = tms.packet_length
        if tms.virtual_network_id:
            tms_dict["VirtualNetworkId"] = tms.virtual_network_id
        result = {"TrafficMirrorSession": tms_dict}
        return ActionResult(result)

    def delete_traffic_mirror_session(self) -> ActionResult:
        session_id = self._get_param("TrafficMirrorSessionId")
        self.ec2_backend.delete_traffic_mirror_session(session_id)
        result = {"TrafficMirrorSessionId": session_id}
        return ActionResult(result)

    def modify_traffic_mirror_filter_network_services(self) -> ActionResult:
        filter_id = self._get_param("TrafficMirrorFilterId")
        add_services = self._get_param("AddNetworkService", [])
        remove_services = self._get_param("RemoveNetworkService", [])
        tmf = self.ec2_backend.modify_traffic_mirror_filter_network_services(
            traffic_mirror_filter_id=filter_id,
            add_network_services=add_services or None,
            remove_network_services=remove_services or None,
        )
        result = {
            "TrafficMirrorFilter": {
                "TrafficMirrorFilterId": tmf.id,
                "Description": tmf.description,
                "NetworkServiceSet": [{"Item": svc} for svc in tmf.network_services],
            }
        }
        return ActionResult(result)

    def modify_traffic_mirror_filter_rule(self) -> ActionResult:
        rule_id = self._get_param("TrafficMirrorFilterRuleId")
        traffic_direction = self._get_param("TrafficDirection")
        rule_number = self._get_param("RuleNumber")
        rule_action = self._get_param("RuleAction")
        protocol = self._get_param("Protocol")
        dst_cidr = self._get_param("DestinationCidrBlock")
        src_cidr = self._get_param("SourceCidrBlock")
        description = self._get_param("Description")
        rule = self.ec2_backend.modify_traffic_mirror_filter_rule(
            traffic_mirror_filter_rule_id=rule_id,
            traffic_direction=traffic_direction,
            rule_number=int(rule_number) if rule_number else None,
            rule_action=rule_action,
            protocol=int(protocol) if protocol else None,
            destination_cidr_block=dst_cidr,
            source_cidr_block=src_cidr,
            description=description,
        )
        rule_dict = {
            "TrafficMirrorFilterRuleId": rule.id,
            "TrafficMirrorFilterId": rule.traffic_mirror_filter_id,
            "TrafficDirection": rule.traffic_direction,
            "RuleNumber": rule.rule_number,
            "RuleAction": rule.rule_action,
            "DestinationCidrBlock": rule.destination_cidr_block,
            "SourceCidrBlock": rule.source_cidr_block,
            "Description": rule.description,
        }
        if rule.protocol:
            rule_dict["Protocol"] = rule.protocol
        result = {"TrafficMirrorFilterRule": rule_dict}
        return ActionResult(result)

    def modify_traffic_mirror_session(self) -> ActionResult:
        session_id = self._get_param("TrafficMirrorSessionId")
        target_id = self._get_param("TrafficMirrorTargetId")
        filter_id = self._get_param("TrafficMirrorFilterId")
        session_number = self._get_param("SessionNumber")
        packet_length = self._get_param("PacketLength")
        virtual_network_id = self._get_param("VirtualNetworkId")
        description = self._get_param("Description")
        session = self.ec2_backend.modify_traffic_mirror_session(
            traffic_mirror_session_id=session_id,
            traffic_mirror_target_id=target_id,
            traffic_mirror_filter_id=filter_id,
            session_number=int(session_number) if session_number else None,
            packet_length=int(packet_length) if packet_length else None,
            virtual_network_id=int(virtual_network_id) if virtual_network_id else None,
            description=description,
        )
        tms_dict = {
            "TrafficMirrorSessionId": session.id,
            "TrafficMirrorTargetId": session.traffic_mirror_target_id,
            "TrafficMirrorFilterId": session.traffic_mirror_filter_id,
            "NetworkInterfaceId": session.network_interface_id,
            "OwnerId": session.owner_id,
            "SessionNumber": session.session_number,
            "Description": session.description,
        }
        if session.packet_length:
            tms_dict["PacketLength"] = session.packet_length
        if session.virtual_network_id:
            tms_dict["VirtualNetworkId"] = session.virtual_network_id
        result = {"TrafficMirrorSession": tms_dict}
        return ActionResult(result)

    def describe_traffic_mirror_sessions(self) -> ActionResult:
        session_ids = self._get_param("TrafficMirrorSessionId", [])
        sessions = self.ec2_backend.describe_traffic_mirror_sessions(
            traffic_mirror_session_ids=session_ids or None,
        )
        result = {
            "TrafficMirrorSessions": [
                {
                    "TrafficMirrorSessionId": tms.id,
                    "TrafficMirrorTargetId": tms.traffic_mirror_target_id,
                    "TrafficMirrorFilterId": tms.traffic_mirror_filter_id,
                    "NetworkInterfaceId": tms.network_interface_id,
                    "OwnerId": tms.owner_id,
                    "SessionNumber": tms.session_number,
                    "Description": tms.description,
                    "Tags": [
                        {"Key": tag.key, "Value": tag.value} for tag in tms.get_tags()
                    ],
                    **(
                        {"PacketLength": tms.packet_length} if tms.packet_length else {}
                    ),
                    **(
                        {"VirtualNetworkId": tms.virtual_network_id}
                        if tms.virtual_network_id
                        else {}
                    ),
                }
                for tms in sessions
            ]
        }
        return ActionResult(result)
