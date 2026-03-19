import datetime
from collections import OrderedDict
from typing import Any

from moto.core.base_backend import BackendDict, BaseBackend
from moto.core.common_models import BaseModel
from moto.core.exceptions import JsonRESTError
from moto.moto_api._internal import mock_random
from moto.utilities.utils import get_partition

PAGINATION_MODEL = {
    "list_channels": {
        "input_token": "next_token",
        "limit_key": "max_results",
        "limit_default": 100,
        "unique_attribute": "arn",
    },
    "list_inputs": {
        "input_token": "next_token",
        "limit_key": "max_results",
        "limit_default": 100,
        "unique_attribute": "arn",
    },
    "list_input_security_groups": {
        "input_token": "next_token",
        "limit_key": "max_results",
        "limit_default": 100,
        "unique_attribute": "arn",
    },
    "list_multiplexes": {
        "input_token": "next_token",
        "limit_key": "max_results",
        "limit_default": 100,
        "unique_attribute": "arn",
    },
    "list_clusters": {
        "input_token": "next_token",
        "limit_key": "max_results",
        "limit_default": 100,
        "unique_attribute": "arn",
    },
    "list_networks": {
        "input_token": "next_token",
        "limit_key": "max_results",
        "limit_default": 100,
        "unique_attribute": "arn",
    },
    "list_sdi_sources": {
        "input_token": "next_token",
        "limit_key": "max_results",
        "limit_default": 100,
        "unique_attribute": "arn",
    },
    "list_signal_maps": {
        "input_token": "next_token",
        "limit_key": "max_results",
        "limit_default": 100,
        "unique_attribute": "arn",
    },
    "list_cloud_watch_alarm_templates": {
        "input_token": "next_token",
        "limit_key": "max_results",
        "limit_default": 100,
        "unique_attribute": "arn",
    },
    "list_cloud_watch_alarm_template_groups": {
        "input_token": "next_token",
        "limit_key": "max_results",
        "limit_default": 100,
        "unique_attribute": "arn",
    },
    "list_event_bridge_rule_templates": {
        "input_token": "next_token",
        "limit_key": "max_results",
        "limit_default": 100,
        "unique_attribute": "arn",
    },
    "list_event_bridge_rule_template_groups": {
        "input_token": "next_token",
        "limit_key": "max_results",
        "limit_default": 100,
        "unique_attribute": "arn",
    },
}




class MediaLiveError(JsonRESTError):
    code = 400


class NotFoundException(MediaLiveError):
    def __init__(self, message: str):
        super().__init__("NotFoundException", message)
        self.code = 404


class Input(BaseModel):
    def __init__(self, **kwargs: Any):
        self.arn = kwargs.get("arn")
        self.attached_channels = kwargs.get("attached_channels", [])
        self.destinations = kwargs.get("destinations", [])
        self.id = kwargs.get("input_id")
        self.input_class = kwargs.get("input_class", "STANDARD")
        self.input_devices = kwargs.get("input_devices", [])
        self.input_source_type = kwargs.get("input_source_type", "STATIC")
        self.media_connect_flows = kwargs.get("media_connect_flows", [])
        self.name = kwargs.get("name")
        self.role_arn = kwargs.get("role_arn")
        self.security_groups = kwargs.get("security_groups", [])
        self.sources = kwargs.get("sources", [])
        # Possible states: 'CREATING'|'DETACHED'|'ATTACHED'|'DELETING'|'DELETED'
        self.state = kwargs.get("state")
        self.tags = kwargs.get("tags")
        self.input_type = kwargs.get("input_type")
        self.input_partner_ids: list[str] = kwargs.get("input_partner_ids", [])

    def to_dict(self) -> dict[str, Any]:
        return {
            "arn": self.arn,
            "attachedChannels": self.attached_channels,
            "destinations": self.destinations,
            "id": self.input_id,
            "inputClass": self.input_class,
            "inputDevices": self.input_devices,
            "inputPartnerIds": self.input_partner_ids,
            "inputSourceType": self.input_source_type,
            "mediaConnectFlows": self.media_connect_flows,
            "name": self.name,
            "roleArn": self.role_arn,
            "securityGroups": self.security_groups,
            "sources": self.sources,
            "state": self.state,
            "tags": self.tags,
            "type": self.input_type,
        }


    def _resolve_transient_states(self) -> None:
        if self.state in ["CREATING"]:
            self.state = "DETACHED"
        elif self.state == "DELETING":
            self.state = "DELETED"


class Channel(BaseModel):
    def __init__(self, **kwargs: Any):
        self.arn = kwargs.get("arn")
        self.cdi_input_specification = kwargs.get("cdi_input_specification")
        self.channel_class = kwargs.get("channel_class", "STANDARD")
        self.destinations = kwargs.get("destinations")
        self.egress_endpoints = kwargs.get("egress_endpoints", [])
        self.encoder_settings = kwargs.get("encoder_settings")
        self.id = kwargs.get("channel_id")
        self.input_attachments = kwargs.get("input_attachments")
        self.input_specification = kwargs.get("input_specification")
        self.log_level = kwargs.get("log_level")
        self.name = kwargs.get("name")
        self.pipeline_details = kwargs.get("pipeline_details", [])
        self.role_arn = kwargs.get("role_arn")
        self.state = kwargs.get("state")
        self.tags = kwargs.get("tags")
        self._previous_state = None

    @property
    def pipelines_running_count(self) -> int:
        return 1 if self.channel_class == "SINGLE_PIPELINE" else 2

    def _resolve_transient_states(self) -> None:
        if self.state in ["CREATING", "STOPPING"]:
            self.state = "IDLE"
        elif self.state == "STARTING":
            self.state = "RUNNING"
        elif self.state == "DELETING":
            self.state = "DELETED"
        elif self.state == "UPDATING":
            self.state = self._previous_state
            self._previous_state = None


class InputSecurityGroup(BaseModel):
    def __init__(self, **kwargs: Any):
        self.arn = kwargs.get("arn")
        self.group_id = kwargs.get("group_id")
        self.inputs: list[str] = kwargs.get("inputs", [])
        self.state = kwargs.get("state", "IDLE")
        self.tags = kwargs.get("tags", {})
        self.whitelist_rules = kwargs.get("whitelist_rules", [])

    def to_dict(self) -> dict[str, Any]:
        return {
            "arn": self.arn,
            "id": self.group_id,
            "inputs": self.inputs,
            "state": self.state,
            "tags": self.tags,
            "whitelistRules": self.whitelist_rules,
        }


class Multiplex(BaseModel):
    def __init__(self, **kwargs: Any):
        self.arn = kwargs.get("arn")
        self.availability_zones = kwargs.get("availability_zones", [])
        self.destinations = kwargs.get("destinations", [])
        self.multiplex_id = kwargs.get("multiplex_id")
        self.multiplex_settings = kwargs.get("multiplex_settings", {})
        self.name = kwargs.get("name")
        self.pipelines_running_count = kwargs.get("pipelines_running_count", 0)
        self.program_count = kwargs.get("program_count", 0)
        self.state = kwargs.get("state", "IDLE")
        self.tags = kwargs.get("tags", {})

    def to_dict(self, exclude: Optional[list[str]] = None) -> dict[str, Any]:
        data = {
            "arn": self.arn,
            "availabilityZones": self.availability_zones,
            "destinations": self.destinations,
            "id": self.multiplex_id,
            "multiplexSettings": self.multiplex_settings,
            "name": self.name,
            "pipelinesRunningCount": self.pipelines_running_count,
            "programCount": self.program_count,
            "state": self.state,
            "tags": self.tags,
        }
        if exclude:
            for key in exclude:
                del data[key]
        return data

    def _resolve_transient_states(self) -> None:
        if self.state in ["CREATING", "STOPPING"]:
            self.state = "IDLE"
        elif self.state == "STARTING":
            self.state = "RUNNING"
        elif self.state == "DELETING":
            self.state = "DELETED"


class MultiplexProgram(BaseModel):
    def __init__(self, **kwargs: Any):
        self.channel_id = kwargs.get("channel_id")
        self.multiplex_program_settings = kwargs.get("multiplex_program_settings", {})
        self.packet_identifiers_map = kwargs.get("packet_identifiers_map", {})
        self.pipeline_details = kwargs.get("pipeline_details", [])
        self.program_name = kwargs.get("program_name")

    def to_dict(self) -> dict[str, Any]:
        return {
            "channelId": self.channel_id,
            "multiplexProgramSettings": self.multiplex_program_settings,
            "packetIdentifiersMap": self.packet_identifiers_map,
            "pipelineDetails": self.pipeline_details,
            "programName": self.program_name,
        }


class Cluster(BaseModel):
    def __init__(self, **kwargs: Any):
        self.arn = kwargs.get("arn")
        self.channel_ids: list[str] = kwargs.get("channel_ids", [])
        self.cluster_type = kwargs.get("cluster_type", "ON_PREMISES")
        self.cluster_id = kwargs.get("cluster_id")
        self.instance_role_arn = kwargs.get("instance_role_arn")
        self.name = kwargs.get("name")
        self.network_settings = kwargs.get("network_settings", {})
        self.state = kwargs.get("state", "IDLE")
        self.tags = kwargs.get("tags", {})

    def to_dict(self) -> dict[str, Any]:
        return {
            "arn": self.arn,
            "channelIds": self.channel_ids,
            "clusterType": self.cluster_type,
            "id": self.cluster_id,
            "instanceRoleArn": self.instance_role_arn,
            "name": self.name,
            "networkSettings": self.network_settings,
            "state": self.state,
            "tags": self.tags,
        }

    def _resolve_transient_states(self) -> None:
        if self.state in ["CREATING"]:
            self.state = "IDLE"
        elif self.state == "DELETING":
            self.state = "DELETED"


class Network(BaseModel):
    def __init__(self, **kwargs: Any):
        self.arn = kwargs.get("arn")
        self.associated_cluster_ids: list[str] = kwargs.get(
            "associated_cluster_ids", []
        )
        self.network_id = kwargs.get("network_id")
        self.ip_pools = kwargs.get("ip_pools", [])
        self.name = kwargs.get("name")
        self.routes = kwargs.get("routes", [])
        self.state = kwargs.get("state", "IDLE")
        self.tags = kwargs.get("tags", {})

    def to_dict(self) -> dict[str, Any]:
        return {
            "arn": self.arn,
            "associatedClusterIds": self.associated_cluster_ids,
            "id": self.network_id,
            "ipPools": self.ip_pools,
            "name": self.name,
            "routes": self.routes,
            "state": self.state,
            "tags": self.tags,
        }

    def _resolve_transient_states(self) -> None:
        if self.state in ["CREATING"]:
            self.state = "IDLE"
        elif self.state == "DELETING":
            self.state = "DELETED"


class Node(BaseModel):
    def __init__(self, **kwargs: Any):
        self.arn = kwargs.get("arn")
        self.channel_placement_groups: list[str] = kwargs.get(
            "channel_placement_groups", []
        )
        self.cluster_id = kwargs.get("cluster_id")
        self.connection_state = kwargs.get("connection_state", "DISCONNECTED")
        self.instance_arn = kwargs.get("instance_arn")
        self.managed_instance_id = kwargs.get("managed_instance_id")
        self.name = kwargs.get("name")
        self.node_id = kwargs.get("node_id")
        self.node_interface_mappings = kwargs.get("node_interface_mappings", [])
        self.role = kwargs.get("role", "BACKUP")
        self.state = kwargs.get("state", "IDLE")
        self.tags = kwargs.get("tags", {})

    def to_dict(self) -> dict[str, Any]:
        return {
            "arn": self.arn,
            "channelPlacementGroups": self.channel_placement_groups,
            "clusterId": self.cluster_id,
            "connectionState": self.connection_state,
            "id": self.node_id,
            "instanceArn": self.instance_arn,
            "managedInstanceId": self.managed_instance_id,
            "name": self.name,
            "nodeInterfaceMappings": self.node_interface_mappings,
            "role": self.role,
            "state": self.state,
            "tags": self.tags,
        }

    def _resolve_transient_states(self) -> None:
        if self.state in ["CREATING"]:
            self.state = "IDLE"
        elif self.state == "DELETING":
            self.state = "DELETED"


class ChannelPlacementGroup(BaseModel):
    def __init__(self, **kwargs: Any):
        self.arn = kwargs.get("arn")
        self.channels: list[str] = kwargs.get("channels", [])
        self.cluster_id = kwargs.get("cluster_id")
        self.group_id = kwargs.get("group_id")
        self.name = kwargs.get("name")
        self.nodes: list[str] = kwargs.get("nodes", [])
        self.state = kwargs.get("state", "IDLE")
        self.tags = kwargs.get("tags", {})

    def to_dict(self) -> dict[str, Any]:
        return {
            "arn": self.arn,
            "channels": self.channels,
            "clusterId": self.cluster_id,
            "id": self.group_id,
            "name": self.name,
            "nodes": self.nodes,
            "state": self.state,
            "tags": self.tags,
        }


class SdiSource(BaseModel):
    def __init__(self, **kwargs: Any):
        self.arn = kwargs.get("arn")
        self.sdi_source_id = kwargs.get("sdi_source_id")
        self.inputs: list[str] = kwargs.get("inputs", [])
        self.name = kwargs.get("name")
        self.mode = kwargs.get("mode", "QUADRANT")
        self.state = kwargs.get("state", "IDLE")
        self.tags = kwargs.get("tags", {})
        self.type = kwargs.get("sdi_type", "SINGLE")

    def to_dict(self) -> dict[str, Any]:
        return {
            "arn": self.arn,
            "id": self.sdi_source_id,
            "inputs": self.inputs,
            "mode": self.mode,
            "name": self.name,
            "state": self.state,
            "tags": self.tags,
            "type": self.type,
        }


class CloudWatchAlarmTemplateGroup(BaseModel):
    def __init__(self, **kwargs: Any):
        self.arn = kwargs.get("arn")
        self.created_at = kwargs.get("created_at")
        self.description = kwargs.get("description", "")
        self.group_id = kwargs.get("group_id")
        self.modified_at = kwargs.get("modified_at")
        self.name = kwargs.get("name")
        self.tags = kwargs.get("tags", {})
        self.template_count = 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "arn": self.arn,
            "createdAt": self.created_at,
            "description": self.description,
            "id": self.group_id,
            "modifiedAt": self.modified_at,
            "name": self.name,
            "tags": self.tags,
            "templateCount": self.template_count,
        }


class CloudWatchAlarmTemplate(BaseModel):
    def __init__(self, **kwargs: Any):
        self.arn = kwargs.get("arn")
        self.comparison_operator = kwargs.get("comparison_operator")
        self.created_at = kwargs.get("created_at")
        self.datapoints_to_alarm = kwargs.get("datapoints_to_alarm")
        self.description = kwargs.get("description", "")
        self.evaluation_periods = kwargs.get("evaluation_periods")
        self.group_id = kwargs.get("group_id")
        self.template_id = kwargs.get("template_id")
        self.metric_name = kwargs.get("metric_name")
        self.modified_at = kwargs.get("modified_at")
        self.name = kwargs.get("name")
        self.period = kwargs.get("period")
        self.statistic = kwargs.get("statistic")
        self.tags = kwargs.get("tags", {})
        self.target_resource_type = kwargs.get("target_resource_type")
        self.threshold = kwargs.get("threshold")
        self.treat_missing_data = kwargs.get("treat_missing_data")

    def to_dict(self) -> dict[str, Any]:
        return {
            "arn": self.arn,
            "comparisonOperator": self.comparison_operator,
            "createdAt": self.created_at,
            "datapointsToAlarm": self.datapoints_to_alarm,
            "description": self.description,
            "evaluationPeriods": self.evaluation_periods,
            "groupId": self.group_id,
            "id": self.template_id,
            "metricName": self.metric_name,
            "modifiedAt": self.modified_at,
            "name": self.name,
            "period": self.period,
            "statistic": self.statistic,
            "tags": self.tags,
            "targetResourceType": self.target_resource_type,
            "threshold": self.threshold,
            "treatMissingData": self.treat_missing_data,
        }


class EventBridgeRuleTemplateGroup(BaseModel):
    def __init__(self, **kwargs: Any):
        self.arn = kwargs.get("arn")
        self.created_at = kwargs.get("created_at")
        self.description = kwargs.get("description", "")
        self.group_id = kwargs.get("group_id")
        self.modified_at = kwargs.get("modified_at")
        self.name = kwargs.get("name")
        self.tags = kwargs.get("tags", {})
        self.template_count = 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "arn": self.arn,
            "createdAt": self.created_at,
            "description": self.description,
            "id": self.group_id,
            "modifiedAt": self.modified_at,
            "name": self.name,
            "tags": self.tags,
            "templateCount": self.template_count,
        }


class EventBridgeRuleTemplate(BaseModel):
    def __init__(self, **kwargs: Any):
        self.arn = kwargs.get("arn")
        self.created_at = kwargs.get("created_at")
        self.description = kwargs.get("description", "")
        self.event_targets = kwargs.get("event_targets", [])
        self.event_type = kwargs.get("event_type")
        self.group_id = kwargs.get("group_id")
        self.template_id = kwargs.get("template_id")
        self.modified_at = kwargs.get("modified_at")
        self.name = kwargs.get("name")
        self.tags = kwargs.get("tags", {})

    def to_dict(self) -> dict[str, Any]:
        return {
            "arn": self.arn,
            "createdAt": self.created_at,
            "description": self.description,
            "eventTargets": self.event_targets,
            "eventType": self.event_type,
            "groupId": self.group_id,
            "id": self.template_id,
            "modifiedAt": self.modified_at,
            "name": self.name,
            "tags": self.tags,
        }


class SignalMap(BaseModel):
    def __init__(self, **kwargs: Any):
        self.arn = kwargs.get("arn")
        self.cloud_watch_alarm_template_group_ids = kwargs.get(
            "cloud_watch_alarm_template_group_ids", []
        )
        self.created_at = kwargs.get("created_at")
        self.description = kwargs.get("description", "")
        self.discovery_entry_point_arn = kwargs.get("discovery_entry_point_arn")
        self.error_message = kwargs.get("error_message")
        self.event_bridge_rule_template_group_ids = kwargs.get(
            "event_bridge_rule_template_group_ids", []
        )
        self.failed_media_resource_map = kwargs.get("failed_media_resource_map", {})
        self.signal_map_id = kwargs.get("signal_map_id")
        self.last_discovered_at = kwargs.get("last_discovered_at")
        self.last_successful_monitor_deployment_at = kwargs.get(
            "last_successful_monitor_deployment_at"
        )
        self.media_resource_map = kwargs.get("media_resource_map", {})
        self.modified_at = kwargs.get("modified_at")
        self.monitor_changes_pending_deployment = kwargs.get(
            "monitor_changes_pending_deployment", False
        )
        self.monitor_deployment = kwargs.get("monitor_deployment", {})
        self.name = kwargs.get("name")
        self.status = kwargs.get("status", "CREATE_COMPLETE")
        self.tags = kwargs.get("tags", {})

    def to_dict(self) -> dict[str, Any]:
        return {
            "arn": self.arn,
            "cloudWatchAlarmTemplateGroupIds": self.cloud_watch_alarm_template_group_ids,
            "createdAt": self.created_at,
            "description": self.description,
            "discoveryEntryPointArn": self.discovery_entry_point_arn,
            "errorMessage": self.error_message,
            "eventBridgeRuleTemplateGroupIds": self.event_bridge_rule_template_group_ids,
            "failedMediaResourceMap": self.failed_media_resource_map,
            "id": self.signal_map_id,
            "lastDiscoveredAt": self.last_discovered_at,
            "lastSuccessfulMonitorDeploymentAt": self.last_successful_monitor_deployment_at,
            "mediaResourceMap": self.media_resource_map,
            "modifiedAt": self.modified_at,
            "monitorChangesPendingDeployment": self.monitor_changes_pending_deployment,
            "monitorDeployment": self.monitor_deployment,
            "name": self.name,
            "status": self.status,
            "tags": self.tags,
        }


def _now_iso() -> str:
    return datetime.datetime.now(datetime.timezone.utc).strftime(
        "%Y-%m-%dT%H:%M:%S.%fZ"
    )


class MediaLiveBackend(BaseBackend):
    def __init__(self, region_name: str, account_id: str):
        super().__init__(region_name, account_id)
        self._channels: dict[str, Channel] = OrderedDict()
        self._inputs: dict[str, Input] = OrderedDict()
        self._input_security_groups: dict[str, InputSecurityGroup] = OrderedDict()
        self._multiplexes: dict[str, Multiplex] = OrderedDict()
        self._multiplex_programs: dict[str, dict[str, MultiplexProgram]] = {}
        self._clusters: dict[str, Cluster] = OrderedDict()
        self._networks: dict[str, Network] = OrderedDict()
        self._nodes: dict[str, dict[str, Node]] = {}  # cluster_id -> {node_id -> Node}
        self._channel_placement_groups: dict[str, dict[str, ChannelPlacementGroup]] = {}
        self._sdi_sources: dict[str, SdiSource] = OrderedDict()
        self._cw_alarm_template_groups: dict[str, CloudWatchAlarmTemplateGroup] = (
            OrderedDict()
        )
        self._cw_alarm_templates: dict[str, CloudWatchAlarmTemplate] = OrderedDict()
        self._eb_rule_template_groups: dict[str, EventBridgeRuleTemplateGroup] = (
            OrderedDict()
        )
        self._eb_rule_templates: dict[str, EventBridgeRuleTemplate] = OrderedDict()
        self._signal_maps: dict[str, SignalMap] = OrderedDict()
        self._tags: dict[str, dict[str, str]] = {}  # arn -> {key: value}
        self._schedules: dict[str, list[dict[str, Any]]] = {}  # channel_id -> actions

    def _arn(self, resource_type: str, resource_id: str) -> str:
        partition = get_partition(self.region_name)
        return (
            f"arn:{partition}:medialive:{self.region_name}:"
            f"{self.account_id}:{resource_type}:{resource_id}"
        )

    def _store_tags(self, arn: str, tags: Optional[dict[str, str]]) -> None:
        if tags:
            self._tags[arn] = tags

    # ---- Channel ----

    def create_channel(
        self,
        cdi_input_specification: dict[str, Any],
        channel_class: str,
        destinations: list[dict[str, Any]],
        encoder_settings: dict[str, Any],
        input_attachments: list[dict[str, Any]],
        input_specification: dict[str, str],
        log_level: str,
        name: str,
        role_arn: str,
        tags: dict[str, str],
    ) -> Channel:
        """
        The RequestID and Reserved parameters are not yet implemented
        """
        channel_id = mock_random.uuid4().hex
        arn = f"arn:{get_partition(self.region_name)}:medialive:channel:{channel_id}"
        channel = Channel(
            arn=arn,
            cdi_input_specification=cdi_input_specification,
            channel_class=channel_class or "STANDARD",
            destinations=destinations,
            egress_endpoints=[],
            encoder_settings=encoder_settings,
            channel_id=channel_id,
            input_attachments=input_attachments,
            input_specification=input_specification,
            log_level=log_level,
            name=name,
            pipeline_details=[],
            role_arn=role_arn,
            state="CREATING",
            tags=tags,
        )
        self._channels[channel_id] = channel
        self._store_tags(arn, tags)
        return channel

    def list_channels(self) -> list[Channel]:
        return list(self._channels.values())

    def describe_channel(self, channel_id: str) -> Channel:
        if channel_id not in self._channels:
            raise NotFoundException(f"Channel {channel_id} not found")
        channel = self._channels[channel_id]
        channel._resolve_transient_states()
        return channel

    def delete_channel(self, channel_id: str) -> Channel:
        if channel_id not in self._channels:
            raise NotFoundException(f"Channel {channel_id} not found")
        channel = self._channels[channel_id]
        channel.state = "DELETING"
        return channel

    def start_channel(self, channel_id: str) -> Channel:
        if channel_id not in self._channels:
            raise NotFoundException(f"Channel {channel_id} not found")
        channel = self._channels[channel_id]
        channel.state = "STARTING"
        return channel

    def stop_channel(self, channel_id: str) -> Channel:
        if channel_id not in self._channels:
            raise NotFoundException(f"Channel {channel_id} not found")
        channel = self._channels[channel_id]
        channel.state = "STOPPING"
        return channel

    def update_channel(
        self,
        channel_id: str,
        cdi_input_specification: dict[str, str],
        destinations: list[dict[str, Any]],
        encoder_settings: dict[str, Any],
        input_attachments: list[dict[str, Any]],
        input_specification: dict[str, str],
        log_level: str,
        name: str,
        role_arn: str,
    ) -> Channel:
        if channel_id not in self._channels:
            raise NotFoundException(f"Channel {channel_id} not found")
        channel = self._channels[channel_id]
        channel.cdi_input_specification = cdi_input_specification
        channel.destinations = destinations
        channel.encoder_settings = encoder_settings
        channel.input_attachments = input_attachments
        channel.input_specification = input_specification
        channel.log_level = log_level
        channel.name = name
        channel.role_arn = role_arn

        channel._resolve_transient_states()
        channel._previous_state = channel.state
        channel.state = "UPDATING"

        return channel

    def update_channel_class(
        self,
        channel_id: str,
        channel_class: str,
        destinations: list[dict[str, Any]],
    ) -> Channel:
        if channel_id not in self._channels:
            raise NotFoundException(f"Channel {channel_id} not found")
        channel = self._channels[channel_id]
        channel.channel_class = channel_class
        if destinations is not None:
            channel.destinations = destinations
        channel._resolve_transient_states()
        channel._previous_state = channel.state
        channel.state = "UPDATING"
        return channel

    def restart_channel_pipelines(
        self,
        channel_id: str,
        pipeline_ids: Optional[list[str]],
    ) -> Channel:
        if channel_id not in self._channels:
            raise NotFoundException(f"Channel {channel_id} not found")
        channel = self._channels[channel_id]
        return channel

    # ---- Input ----

    def create_input(
        self,
        destinations: list[dict[str, str]],
        input_devices: list[dict[str, str]],
        input_security_groups: list[str],
        media_connect_flows: list[dict[str, str]],
        name: str,
        role_arn: str,
        sources: list[dict[str, str]],
        tags: dict[str, str],
        input_type: str,
    ) -> Input:
        """
        The VPC and RequestId parameters are not yet implemented
        """
        input_id = mock_random.uuid4().hex
        arn = f"arn:{get_partition(self.region_name)}:medialive:input:{input_id}"
        a_input = Input(
            arn=arn,
            input_id=input_id,
            destinations=destinations,
            input_devices=input_devices,
            input_security_groups=input_security_groups,
            media_connect_flows=media_connect_flows,
            name=name,
            role_arn=role_arn,
            sources=sources,
            tags=tags,
            input_type=input_type,
            state="CREATING",
        )
        self._inputs[input_id] = a_input
        self._store_tags(arn, tags)
        return a_input

    def describe_input(self, input_id: str) -> Input:
        if input_id not in self._inputs:
            raise NotFoundException(f"Input {input_id} not found")
        a_input = self._inputs[input_id]
        a_input._resolve_transient_states()
        return a_input

    def list_inputs(self) -> list[Input]:
        return list(self._inputs.values())

    def delete_input(self, input_id: str) -> None:
        if input_id not in self._inputs:
            raise NotFoundException(f"Input {input_id} not found")
        a_input = self._inputs[input_id]
        a_input.state = "DELETING"

    def update_input(
        self,
        destinations: list[dict[str, str]],
        input_devices: list[dict[str, str]],
        input_id: str,
        input_security_groups: list[str],
        media_connect_flows: list[dict[str, str]],
        name: str,
        role_arn: str,
        sources: list[dict[str, str]],
    ) -> Input:
        if input_id not in self._inputs:
            raise NotFoundException(f"Input {input_id} not found")
        a_input = self._inputs[input_id]
        a_input.destinations = destinations
        a_input.input_devices = input_devices
        a_input.security_groups = input_security_groups
        a_input.media_connect_flows = media_connect_flows
        a_input.name = name
        a_input.role_arn = role_arn
        a_input.sources = sources
        return a_input

    def create_partner_input(
        self,
        input_id: str,
        request_id: Optional[str],
        tags: Optional[dict[str, str]],
    ) -> Input:
        if input_id not in self._inputs:
            raise NotFoundException(f"Input {input_id} not found")
        parent = self._inputs[input_id]
        partner_id = mock_random.uuid4().hex
        arn = f"arn:{get_partition(self.region_name)}:medialive:input:{partner_id}"
        partner = Input(
            arn=arn,
            input_id=partner_id,
            destinations=parent.destinations,
            input_devices=[],
            media_connect_flows=[],
            name=f"{parent.name}-partner",
            role_arn=parent.role_arn,
            sources=[],
            tags=tags or {},
            input_type=parent.input_type,
            state="CREATING",
            input_partner_ids=[input_id],
        )
        self._inputs[partner_id] = partner
        parent.input_partner_ids.append(partner_id)
        self._store_tags(arn, tags)
        return partner

    # ---- InputSecurityGroup ----

    def create_input_security_group(
        self,
        tags: Optional[dict[str, str]],
        whitelist_rules: Optional[list[dict[str, str]]],
    ) -> InputSecurityGroup:
        group_id = mock_random.uuid4().hex
        arn = self._arn("inputSecurityGroup", group_id)
        group = InputSecurityGroup(
            arn=arn,
            group_id=group_id,
            state="IDLE",
            tags=tags or {},
            whitelist_rules=whitelist_rules or [],
        )
        self._input_security_groups[group_id] = group
        self._store_tags(arn, tags)
        return group

    def describe_input_security_group(self, group_id: str) -> InputSecurityGroup:
        if group_id not in self._input_security_groups:
            raise NotFoundException(f"InputSecurityGroup {group_id} not found")
        return self._input_security_groups[group_id]

    @paginate(PAGINATION_MODEL)
    def list_input_security_groups(self) -> list[InputSecurityGroup]:
        return list(self._input_security_groups.values())

    def delete_input_security_group(self, group_id: str) -> None:
        if group_id not in self._input_security_groups:
            raise NotFoundException(f"InputSecurityGroup {group_id} not found")
        del self._input_security_groups[group_id]

    def update_input_security_group(
        self,
        group_id: str,
        tags: Optional[dict[str, str]],
        whitelist_rules: Optional[list[dict[str, str]]],
    ) -> InputSecurityGroup:
        if group_id not in self._input_security_groups:
            raise NotFoundException(f"InputSecurityGroup {group_id} not found")
        group = self._input_security_groups[group_id]
        if tags is not None:
            group.tags = tags
        if whitelist_rules is not None:
            group.whitelist_rules = whitelist_rules
        return group

    # ---- Multiplex ----

    def create_multiplex(
        self,
        availability_zones: list[str],
        multiplex_settings: dict[str, Any],
        name: str,
        tags: Optional[dict[str, str]],
    ) -> Multiplex:
        multiplex_id = mock_random.uuid4().hex
        arn = self._arn("multiplex", multiplex_id)
        multiplex = Multiplex(
            arn=arn,
            availability_zones=availability_zones or [],
            multiplex_id=multiplex_id,
            multiplex_settings=multiplex_settings or {},
            name=name,
            state="CREATING",
            tags=tags or {},
        )
        self._multiplexes[multiplex_id] = multiplex
        self._multiplex_programs[multiplex_id] = OrderedDict()
        self._store_tags(arn, tags)
        return multiplex

    def describe_multiplex(self, multiplex_id: str) -> Multiplex:
        if multiplex_id not in self._multiplexes:
            raise NotFoundException(f"Multiplex {multiplex_id} not found")
        m = self._multiplexes[multiplex_id]
        m._resolve_transient_states()
        m.program_count = len(self._multiplex_programs.get(multiplex_id, {}))
        return m

    @paginate(PAGINATION_MODEL)
    def list_multiplexes(self) -> list[Multiplex]:
        return list(self._multiplexes.values())

    def delete_multiplex(self, multiplex_id: str) -> Multiplex:
        if multiplex_id not in self._multiplexes:
            raise NotFoundException(f"Multiplex {multiplex_id} not found")
        m = self._multiplexes[multiplex_id]
        m.state = "DELETING"
        return m

    def start_multiplex(self, multiplex_id: str) -> Multiplex:
        if multiplex_id not in self._multiplexes:
            raise NotFoundException(f"Multiplex {multiplex_id} not found")
        m = self._multiplexes[multiplex_id]
        m._resolve_transient_states()
        m.state = "STARTING"
        return m

    def stop_multiplex(self, multiplex_id: str) -> Multiplex:
        if multiplex_id not in self._multiplexes:
            raise NotFoundException(f"Multiplex {multiplex_id} not found")
        m = self._multiplexes[multiplex_id]
        m._resolve_transient_states()
        m.state = "STOPPING"
        return m

    def update_multiplex(
        self,
        multiplex_id: str,
        multiplex_settings: Optional[dict[str, Any]],
        name: Optional[str],
    ) -> Multiplex:
        if multiplex_id not in self._multiplexes:
            raise NotFoundException(f"Multiplex {multiplex_id} not found")
        m = self._multiplexes[multiplex_id]
        if multiplex_settings is not None:
            m.multiplex_settings = multiplex_settings
        if name is not None:
            m.name = name
        m._resolve_transient_states()
        return m

    # ---- MultiplexProgram ----

    def create_multiplex_program(
        self,
        multiplex_id: str,
        multiplex_program_settings: dict[str, Any],
        program_name: str,
    ) -> MultiplexProgram:
        if multiplex_id not in self._multiplexes:
            raise NotFoundException(f"Multiplex {multiplex_id} not found")
        program = MultiplexProgram(
            multiplex_program_settings=multiplex_program_settings or {},
            program_name=program_name,
        )
        self._multiplex_programs[multiplex_id][program_name] = program
        return program

    def describe_multiplex_program(
        self, multiplex_id: str, program_name: str
    ) -> MultiplexProgram:
        if multiplex_id not in self._multiplexes:
            raise NotFoundException(f"Multiplex {multiplex_id} not found")
        programs = self._multiplex_programs.get(multiplex_id, {})
        if program_name not in programs:
            raise NotFoundException(f"MultiplexProgram {program_name} not found")
        return programs[program_name]

    def list_multiplex_programs(self, multiplex_id: str) -> list[MultiplexProgram]:
        if multiplex_id not in self._multiplexes:
            raise NotFoundException(f"Multiplex {multiplex_id} not found")
        return list(self._multiplex_programs.get(multiplex_id, {}).values())

    def delete_multiplex_program(
        self, multiplex_id: str, program_name: str
    ) -> MultiplexProgram:
        if multiplex_id not in self._multiplexes:
            raise NotFoundException(f"Multiplex {multiplex_id} not found")
        programs = self._multiplex_programs.get(multiplex_id, {})
        if program_name not in programs:
            raise NotFoundException(f"MultiplexProgram {program_name} not found")
        return programs.pop(program_name)

    def update_multiplex_program(
        self,
        multiplex_id: str,
        multiplex_program_settings: Optional[dict[str, Any]],
        program_name: str,
    ) -> MultiplexProgram:
        if multiplex_id not in self._multiplexes:
            raise NotFoundException(f"Multiplex {multiplex_id} not found")
        programs = self._multiplex_programs.get(multiplex_id, {})
        if program_name not in programs:
            raise NotFoundException(f"MultiplexProgram {program_name} not found")
        prog = programs[program_name]
        if multiplex_program_settings is not None:
            prog.multiplex_program_settings = multiplex_program_settings
        return prog

    # ---- Cluster ----

    def create_cluster(
        self,
        cluster_type: Optional[str],
        instance_role_arn: Optional[str],
        name: Optional[str],
        network_settings: Optional[dict[str, Any]],
        tags: Optional[dict[str, str]],
    ) -> Cluster:
        cluster_id = mock_random.uuid4().hex
        arn = self._arn("cluster", cluster_id)
        cluster = Cluster(
            arn=arn,
            cluster_id=cluster_id,
            cluster_type=cluster_type or "ON_PREMISES",
            instance_role_arn=instance_role_arn,
            name=name,
            network_settings=network_settings or {},
            state="CREATING",
            tags=tags or {},
        )
        self._clusters[cluster_id] = cluster
        self._nodes[cluster_id] = OrderedDict()
        self._channel_placement_groups[cluster_id] = OrderedDict()
        self._store_tags(arn, tags)
        return cluster

    def describe_cluster(self, cluster_id: str) -> Cluster:
        if cluster_id not in self._clusters:
            raise NotFoundException(f"Cluster {cluster_id} not found")
        c = self._clusters[cluster_id]
        c._resolve_transient_states()
        return c

    @paginate(PAGINATION_MODEL)
    def list_clusters(self) -> list[Cluster]:
        return list(self._clusters.values())

    def delete_cluster(self, cluster_id: str) -> Cluster:
        if cluster_id not in self._clusters:
            raise NotFoundException(f"Cluster {cluster_id} not found")
        c = self._clusters[cluster_id]
        c.state = "DELETING"
        return c

    def update_cluster(
        self,
        cluster_id: str,
        name: Optional[str],
        network_settings: Optional[dict[str, Any]],
    ) -> Cluster:
        if cluster_id not in self._clusters:
            raise NotFoundException(f"Cluster {cluster_id} not found")
        c = self._clusters[cluster_id]
        if name is not None:
            c.name = name
        if network_settings is not None:
            c.network_settings = network_settings
        return c

    # ---- Network ----

    def create_network(
        self,
        ip_pools: Optional[list[dict[str, str]]],
        name: Optional[str],
        routes: Optional[list[dict[str, Any]]],
        tags: Optional[dict[str, str]],
    ) -> Network:
        network_id = mock_random.uuid4().hex
        arn = self._arn("network", network_id)
        network = Network(
            arn=arn,
            network_id=network_id,
            ip_pools=ip_pools or [],
            name=name,
            routes=routes or [],
            state="IDLE",
            tags=tags or {},
        )
        self._networks[network_id] = network
        self._store_tags(arn, tags)
        return network

    def describe_network(self, network_id: str) -> Network:
        if network_id not in self._networks:
            raise NotFoundException(f"Network {network_id} not found")
        n = self._networks[network_id]
        n._resolve_transient_states()
        return n

    @paginate(PAGINATION_MODEL)
    def list_networks(self) -> list[Network]:
        return list(self._networks.values())

    def delete_network(self, network_id: str) -> Network:
        if network_id not in self._networks:
            raise NotFoundException(f"Network {network_id} not found")
        n = self._networks[network_id]
        n.state = "DELETING"
        return n

    def update_network(
        self,
        network_id: str,
        ip_pools: Optional[list[dict[str, str]]],
        name: Optional[str],
        routes: Optional[list[dict[str, Any]]],
    ) -> Network:
        if network_id not in self._networks:
            raise NotFoundException(f"Network {network_id} not found")
        n = self._networks[network_id]
        if ip_pools is not None:
            n.ip_pools = ip_pools
        if name is not None:
            n.name = name
        if routes is not None:
            n.routes = routes
        return n

    # ---- Node ----

    def create_node(
        self,
        cluster_id: str,
        name: Optional[str],
        node_interface_mappings: Optional[list[dict[str, Any]]],
        role: Optional[str],
        tags: Optional[dict[str, str]],
    ) -> Node:
        if cluster_id not in self._clusters:
            raise NotFoundException(f"Cluster {cluster_id} not found")
        node_id = mock_random.uuid4().hex
        arn = self._arn("node", node_id)
        node = Node(
            arn=arn,
            cluster_id=cluster_id,
            name=name,
            node_id=node_id,
            node_interface_mappings=node_interface_mappings or [],
            role=role or "BACKUP",
            state="IDLE",
            tags=tags or {},
        )
        self._nodes[cluster_id][node_id] = node
        self._store_tags(arn, tags)
        return node

    def describe_node(self, cluster_id: str, node_id: str) -> Node:
        if cluster_id not in self._clusters:
            raise NotFoundException(f"Cluster {cluster_id} not found")
        nodes = self._nodes.get(cluster_id, {})
        if node_id not in nodes:
            raise NotFoundException(f"Node {node_id} not found")
        n = nodes[node_id]
        n._resolve_transient_states()
        return n

    def list_nodes(self, cluster_id: str) -> list[Node]:
        if cluster_id not in self._clusters:
            raise NotFoundException(f"Cluster {cluster_id} not found")
        return list(self._nodes.get(cluster_id, {}).values())

    def delete_node(self, cluster_id: str, node_id: str) -> Node:
        if cluster_id not in self._clusters:
            raise NotFoundException(f"Cluster {cluster_id} not found")
        nodes = self._nodes.get(cluster_id, {})
        if node_id not in nodes:
            raise NotFoundException(f"Node {node_id} not found")
        n = nodes[node_id]
        n.state = "DELETING"
        return n

    def update_node(
        self,
        cluster_id: str,
        node_id: str,
        name: Optional[str],
        role: Optional[str],
    ) -> Node:
        if cluster_id not in self._clusters:
            raise NotFoundException(f"Cluster {cluster_id} not found")
        nodes = self._nodes.get(cluster_id, {})
        if node_id not in nodes:
            raise NotFoundException(f"Node {node_id} not found")
        n = nodes[node_id]
        if name is not None:
            n.name = name
        if role is not None:
            n.role = role
        return n

    def update_node_state(
        self,
        cluster_id: str,
        node_id: str,
        state: Optional[str],
    ) -> Node:
        if cluster_id not in self._clusters:
            raise NotFoundException(f"Cluster {cluster_id} not found")
        nodes = self._nodes.get(cluster_id, {})
        if node_id not in nodes:
            raise NotFoundException(f"Node {node_id} not found")
        n = nodes[node_id]
        if state is not None:
            n.state = state
        return n

    def create_node_registration_script(
        self,
        cluster_id: str,
        node_id: Optional[str],
        name: Optional[str],
    ) -> str:
        if cluster_id not in self._clusters:
            raise NotFoundException(f"Cluster {cluster_id} not found")
        return "#!/bin/bash\n# Mock node registration script\necho 'registered'"

    # ---- ChannelPlacementGroup ----

    def create_channel_placement_group(
        self,
        cluster_id: str,
        name: Optional[str],
        nodes: Optional[list[str]],
        tags: Optional[dict[str, str]],
    ) -> ChannelPlacementGroup:
        if cluster_id not in self._clusters:
            raise NotFoundException(f"Cluster {cluster_id} not found")
        group_id = mock_random.uuid4().hex
        arn = self._arn("channelPlacementGroup", group_id)
        group = ChannelPlacementGroup(
            arn=arn,
            cluster_id=cluster_id,
            group_id=group_id,
            name=name,
            nodes=nodes or [],
            state="IDLE",
            tags=tags or {},
        )
        self._channel_placement_groups[cluster_id][group_id] = group
        self._store_tags(arn, tags)
        return group

    def describe_channel_placement_group(
        self, cluster_id: str, group_id: str
    ) -> ChannelPlacementGroup:
        if cluster_id not in self._clusters:
            raise NotFoundException(f"Cluster {cluster_id} not found")
        groups = self._channel_placement_groups.get(cluster_id, {})
        if group_id not in groups:
            raise NotFoundException(f"ChannelPlacementGroup {group_id} not found")
        return groups[group_id]

    def list_channel_placement_groups(
        self, cluster_id: str
    ) -> list[ChannelPlacementGroup]:
        if cluster_id not in self._clusters:
            raise NotFoundException(f"Cluster {cluster_id} not found")
        return list(self._channel_placement_groups.get(cluster_id, {}).values())

    def delete_channel_placement_group(
        self, cluster_id: str, group_id: str
    ) -> ChannelPlacementGroup:
        if cluster_id not in self._clusters:
            raise NotFoundException(f"Cluster {cluster_id} not found")
        groups = self._channel_placement_groups.get(cluster_id, {})
        if group_id not in groups:
            raise NotFoundException(f"ChannelPlacementGroup {group_id} not found")
        group = groups[group_id]
        group.state = "DELETING"
        return group

    def update_channel_placement_group(
        self,
        cluster_id: str,
        group_id: str,
        name: Optional[str],
        nodes: Optional[list[str]],
    ) -> ChannelPlacementGroup:
        if cluster_id not in self._clusters:
            raise NotFoundException(f"Cluster {cluster_id} not found")
        groups = self._channel_placement_groups.get(cluster_id, {})
        if group_id not in groups:
            raise NotFoundException(f"ChannelPlacementGroup {group_id} not found")
        group = groups[group_id]
        if name is not None:
            group.name = name
        if nodes is not None:
            group.nodes = nodes
        return group

    # ---- SdiSource ----

    def create_sdi_source(
        self,
        mode: Optional[str],
        name: Optional[str],
        tags: Optional[dict[str, str]],
        sdi_type: Optional[str],
    ) -> SdiSource:
        sdi_source_id = mock_random.uuid4().hex
        arn = self._arn("sdiSource", sdi_source_id)
        source = SdiSource(
            arn=arn,
            sdi_source_id=sdi_source_id,
            mode=mode or "QUADRANT",
            name=name,
            state="IDLE",
            tags=tags or {},
            sdi_type=sdi_type or "SINGLE",
        )
        self._sdi_sources[sdi_source_id] = source
        self._store_tags(arn, tags)
        return source

    def describe_sdi_source(self, sdi_source_id: str) -> SdiSource:
        if sdi_source_id not in self._sdi_sources:
            raise NotFoundException(f"SdiSource {sdi_source_id} not found")
        return self._sdi_sources[sdi_source_id]

    @paginate(PAGINATION_MODEL)
    def list_sdi_sources(self) -> list[SdiSource]:
        return list(self._sdi_sources.values())

    def delete_sdi_source(self, sdi_source_id: str) -> None:
        if sdi_source_id not in self._sdi_sources:
            raise NotFoundException(f"SdiSource {sdi_source_id} not found")
        del self._sdi_sources[sdi_source_id]

    def update_sdi_source(
        self,
        sdi_source_id: str,
        mode: Optional[str],
        name: Optional[str],
        sdi_type: Optional[str],
    ) -> SdiSource:
        if sdi_source_id not in self._sdi_sources:
            raise NotFoundException(f"SdiSource {sdi_source_id} not found")
        s = self._sdi_sources[sdi_source_id]
        if mode is not None:
            s.mode = mode
        if name is not None:
            s.name = name
        if sdi_type is not None:
            s.type = sdi_type
        return s

    # ---- CloudWatchAlarmTemplateGroup ----

    def create_cloud_watch_alarm_template_group(
        self,
        description: Optional[str],
        name: str,
        tags: Optional[dict[str, str]],
    ) -> CloudWatchAlarmTemplateGroup:
        group_id = mock_random.uuid4().hex
        arn = self._arn("cloudWatchAlarmTemplateGroup", group_id)
        now = _now_iso()
        group = CloudWatchAlarmTemplateGroup(
            arn=arn,
            created_at=now,
            description=description or "",
            group_id=group_id,
            modified_at=now,
            name=name,
            tags=tags or {},
        )
        self._cw_alarm_template_groups[group_id] = group
        self._store_tags(arn, tags)
        return group

    def get_cloud_watch_alarm_template_group(
        self, identifier: str
    ) -> CloudWatchAlarmTemplateGroup:
        if identifier not in self._cw_alarm_template_groups:
            # Try by name
            for g in self._cw_alarm_template_groups.values():
                if g.name == identifier or g.arn == identifier:
                    return g
            raise NotFoundException(
                f"CloudWatchAlarmTemplateGroup {identifier} not found"
            )
        return self._cw_alarm_template_groups[identifier]

    @paginate(PAGINATION_MODEL)
    def list_cloud_watch_alarm_template_groups(
        self,
    ) -> list[CloudWatchAlarmTemplateGroup]:
        return list(self._cw_alarm_template_groups.values())

    def delete_cloud_watch_alarm_template_group(self, identifier: str) -> None:
        group = self.get_cloud_watch_alarm_template_group(identifier)
        del self._cw_alarm_template_groups[group.group_id]

    def update_cloud_watch_alarm_template_group(
        self,
        identifier: str,
        description: Optional[str],
    ) -> CloudWatchAlarmTemplateGroup:
        group = self.get_cloud_watch_alarm_template_group(identifier)
        if description is not None:
            group.description = description
        group.modified_at = _now_iso()
        return group

    # ---- CloudWatchAlarmTemplate ----

    def create_cloud_watch_alarm_template(
        self,
        comparison_operator: str,
        datapoints_to_alarm: Optional[int],
        description: Optional[str],
        evaluation_periods: int,
        group_identifier: str,
        metric_name: str,
        name: str,
        period: int,
        statistic: str,
        tags: Optional[dict[str, str]],
        target_resource_type: str,
        threshold: float,
        treat_missing_data: str,
    ) -> CloudWatchAlarmTemplate:
        # Resolve group
        group = self.get_cloud_watch_alarm_template_group(group_identifier)
        template_id = mock_random.uuid4().hex
        arn = self._arn("cloudWatchAlarmTemplate", template_id)
        now = _now_iso()
        template = CloudWatchAlarmTemplate(
            arn=arn,
            comparison_operator=comparison_operator,
            created_at=now,
            datapoints_to_alarm=datapoints_to_alarm,
            description=description or "",
            evaluation_periods=evaluation_periods,
            group_id=group.group_id,
            template_id=template_id,
            metric_name=metric_name,
            modified_at=now,
            name=name,
            period=period,
            statistic=statistic,
            tags=tags or {},
            target_resource_type=target_resource_type,
            threshold=threshold,
            treat_missing_data=treat_missing_data,
        )
        self._cw_alarm_templates[template_id] = template
        group.template_count += 1
        self._store_tags(arn, tags)
        return template

    def get_cloud_watch_alarm_template(
        self, identifier: str
    ) -> CloudWatchAlarmTemplate:
        if identifier not in self._cw_alarm_templates:
            for t in self._cw_alarm_templates.values():
                if t.name == identifier or t.arn == identifier:
                    return t
            raise NotFoundException(f"CloudWatchAlarmTemplate {identifier} not found")
        return self._cw_alarm_templates[identifier]

    @paginate(PAGINATION_MODEL)
    def list_cloud_watch_alarm_templates(self) -> list[CloudWatchAlarmTemplate]:
        return list(self._cw_alarm_templates.values())

    def delete_cloud_watch_alarm_template(self, identifier: str) -> None:
        template = self.get_cloud_watch_alarm_template(identifier)
        # Decrement group count
        if template.group_id in self._cw_alarm_template_groups:
            self._cw_alarm_template_groups[template.group_id].template_count -= 1
        del self._cw_alarm_templates[template.template_id]

    def update_cloud_watch_alarm_template(
        self,
        identifier: str,
        comparison_operator: Optional[str],
        datapoints_to_alarm: Optional[int],
        description: Optional[str],
        evaluation_periods: Optional[int],
        group_identifier: Optional[str],
        metric_name: Optional[str],
        period: Optional[int],
        statistic: Optional[str],
        target_resource_type: Optional[str],
        threshold: Optional[float],
        treat_missing_data: Optional[str],
    ) -> CloudWatchAlarmTemplate:
        template = self.get_cloud_watch_alarm_template(identifier)
        if comparison_operator is not None:
            template.comparison_operator = comparison_operator
        if datapoints_to_alarm is not None:
            template.datapoints_to_alarm = datapoints_to_alarm
        if description is not None:
            template.description = description
        if evaluation_periods is not None:
            template.evaluation_periods = evaluation_periods
        if group_identifier is not None:
            group = self.get_cloud_watch_alarm_template_group(group_identifier)
            template.group_id = group.group_id
        if metric_name is not None:
            template.metric_name = metric_name
        if period is not None:
            template.period = period
        if statistic is not None:
            template.statistic = statistic
        if target_resource_type is not None:
            template.target_resource_type = target_resource_type
        if threshold is not None:
            template.threshold = threshold
        if treat_missing_data is not None:
            template.treat_missing_data = treat_missing_data
        template.modified_at = _now_iso()
        return template

    # ---- EventBridgeRuleTemplateGroup ----

    def create_event_bridge_rule_template_group(
        self,
        description: Optional[str],
        name: str,
        tags: Optional[dict[str, str]],
    ) -> EventBridgeRuleTemplateGroup:
        group_id = mock_random.uuid4().hex
        arn = self._arn("eventBridgeRuleTemplateGroup", group_id)
        now = _now_iso()
        group = EventBridgeRuleTemplateGroup(
            arn=arn,
            created_at=now,
            description=description or "",
            group_id=group_id,
            modified_at=now,
            name=name,
            tags=tags or {},
        )
        self._eb_rule_template_groups[group_id] = group
        self._store_tags(arn, tags)
        return group

    def get_event_bridge_rule_template_group(
        self, identifier: str
    ) -> EventBridgeRuleTemplateGroup:
        if identifier not in self._eb_rule_template_groups:
            for g in self._eb_rule_template_groups.values():
                if g.name == identifier or g.arn == identifier:
                    return g
            raise NotFoundException(
                f"EventBridgeRuleTemplateGroup {identifier} not found"
            )
        return self._eb_rule_template_groups[identifier]

    @paginate(PAGINATION_MODEL)
    def list_event_bridge_rule_template_groups(
        self,
    ) -> list[EventBridgeRuleTemplateGroup]:
        return list(self._eb_rule_template_groups.values())

    def delete_event_bridge_rule_template_group(self, identifier: str) -> None:
        group = self.get_event_bridge_rule_template_group(identifier)
        del self._eb_rule_template_groups[group.group_id]

    def update_event_bridge_rule_template_group(
        self,
        identifier: str,
        description: Optional[str],
    ) -> EventBridgeRuleTemplateGroup:
        group = self.get_event_bridge_rule_template_group(identifier)
        if description is not None:
            group.description = description
        group.modified_at = _now_iso()
        return group

    # ---- EventBridgeRuleTemplate ----

    def create_event_bridge_rule_template(
        self,
        description: Optional[str],
        event_targets: Optional[list[dict[str, Any]]],
        event_type: str,
        group_identifier: str,
        name: str,
        tags: Optional[dict[str, str]],
    ) -> EventBridgeRuleTemplate:
        group = self.get_event_bridge_rule_template_group(group_identifier)
        template_id = mock_random.uuid4().hex
        arn = self._arn("eventBridgeRuleTemplate", template_id)
        now = _now_iso()
        template = EventBridgeRuleTemplate(
            arn=arn,
            created_at=now,
            description=description or "",
            event_targets=event_targets or [],
            event_type=event_type,
            group_id=group.group_id,
            template_id=template_id,
            modified_at=now,
            name=name,
            tags=tags or {},
        )
        self._eb_rule_templates[template_id] = template
        group.template_count += 1
        self._store_tags(arn, tags)
        return template

    def get_event_bridge_rule_template(
        self, identifier: str
    ) -> EventBridgeRuleTemplate:
        if identifier not in self._eb_rule_templates:
            for t in self._eb_rule_templates.values():
                if t.name == identifier or t.arn == identifier:
                    return t
            raise NotFoundException(f"EventBridgeRuleTemplate {identifier} not found")
        return self._eb_rule_templates[identifier]

    @paginate(PAGINATION_MODEL)
    def list_event_bridge_rule_templates(self) -> list[EventBridgeRuleTemplate]:
        return list(self._eb_rule_templates.values())

    def delete_event_bridge_rule_template(self, identifier: str) -> None:
        template = self.get_event_bridge_rule_template(identifier)
        if template.group_id in self._eb_rule_template_groups:
            self._eb_rule_template_groups[template.group_id].template_count -= 1
        del self._eb_rule_templates[template.template_id]

    def update_event_bridge_rule_template(
        self,
        identifier: str,
        description: Optional[str],
        event_targets: Optional[list[dict[str, Any]]],
        event_type: Optional[str],
        group_identifier: Optional[str],
    ) -> EventBridgeRuleTemplate:
        template = self.get_event_bridge_rule_template(identifier)
        if description is not None:
            template.description = description
        if event_targets is not None:
            template.event_targets = event_targets
        if event_type is not None:
            template.event_type = event_type
        if group_identifier is not None:
            group = self.get_event_bridge_rule_template_group(group_identifier)
            template.group_id = group.group_id
        template.modified_at = _now_iso()
        return template

    # ---- SignalMap ----

    def create_signal_map(
        self,
        cloud_watch_alarm_template_group_identifiers: Optional[list[str]],
        description: Optional[str],
        discovery_entry_point_arn: str,
        event_bridge_rule_template_group_identifiers: Optional[list[str]],
        name: str,
        tags: Optional[dict[str, str]],
    ) -> SignalMap:
        signal_map_id = mock_random.uuid4().hex
        arn = self._arn("signalMap", signal_map_id)
        now = _now_iso()
        signal_map = SignalMap(
            arn=arn,
            cloud_watch_alarm_template_group_ids=(
                cloud_watch_alarm_template_group_identifiers or []
            ),
            created_at=now,
            description=description or "",
            discovery_entry_point_arn=discovery_entry_point_arn,
            event_bridge_rule_template_group_ids=(
                event_bridge_rule_template_group_identifiers or []
            ),
            signal_map_id=signal_map_id,
            modified_at=now,
            name=name,
            status="CREATE_COMPLETE",
            tags=tags or {},
        )
        self._signal_maps[signal_map_id] = signal_map
        self._store_tags(arn, tags)
        return signal_map

    def get_signal_map(self, identifier: str) -> SignalMap:
        if identifier not in self._signal_maps:
            for sm in self._signal_maps.values():
                if sm.name == identifier or sm.arn == identifier:
                    return sm
            raise NotFoundException(f"SignalMap {identifier} not found")
        return self._signal_maps[identifier]

    @paginate(PAGINATION_MODEL)
    def list_signal_maps(self) -> list[SignalMap]:
        return list(self._signal_maps.values())

    def delete_signal_map(self, identifier: str) -> None:
        sm = self.get_signal_map(identifier)
        del self._signal_maps[sm.signal_map_id]

    def start_update_signal_map(
        self,
        identifier: str,
        cloud_watch_alarm_template_group_identifiers: Optional[list[str]],
        description: Optional[str],
        discovery_entry_point_arn: Optional[str],
        event_bridge_rule_template_group_identifiers: Optional[list[str]],
        name: Optional[str],
    ) -> SignalMap:
        sm = self.get_signal_map(identifier)
        if cloud_watch_alarm_template_group_identifiers is not None:
            sm.cloud_watch_alarm_template_group_ids = (
                cloud_watch_alarm_template_group_identifiers
            )
        if description is not None:
            sm.description = description
        if discovery_entry_point_arn is not None:
            sm.discovery_entry_point_arn = discovery_entry_point_arn
        if event_bridge_rule_template_group_identifiers is not None:
            sm.event_bridge_rule_template_group_ids = (
                event_bridge_rule_template_group_identifiers
            )
        if name is not None:
            sm.name = name
        sm.modified_at = _now_iso()
        sm.status = "UPDATE_COMPLETE"
        return sm

    def start_monitor_deployment(
        self, identifier: str, dry_run: bool = False
    ) -> SignalMap:
        sm = self.get_signal_map(identifier)
        sm.monitor_deployment = {
            "status": "DRY_RUN_COMPLETE" if dry_run else "COMPLETE"
        }
        sm.monitor_changes_pending_deployment = False
        sm.modified_at = _now_iso()
        return sm

    def start_delete_monitor_deployment(self, identifier: str) -> SignalMap:
        sm = self.get_signal_map(identifier)
        sm.monitor_deployment = {}
        sm.modified_at = _now_iso()
        return sm

    # ---- Tags ----

    def create_tags(self, resource_arn: str, tags: Optional[dict[str, str]]) -> None:
        if tags:
            existing = self._tags.get(resource_arn, {})
            existing.update(tags)
            self._tags[resource_arn] = existing

    def delete_tags(self, resource_arn: str, tag_keys: list[str]) -> None:
        existing = self._tags.get(resource_arn, {})
        for key in tag_keys:
            existing.pop(key, None)

    def list_tags_for_resource(self, resource_arn: str) -> dict[str, str]:
        return self._tags.get(resource_arn, {})

    # ---- Schedule ----

    def batch_update_schedule(
        self,
        channel_id: str,
        creates: Optional[dict[str, Any]],
        deletes: Optional[dict[str, Any]],
    ) -> dict[str, Any]:
        if channel_id not in self._channels:
            raise NotFoundException(f"Channel {channel_id} not found")
        if channel_id not in self._schedules:
            self._schedules[channel_id] = []

        deleted_actions: list[str] = []
        if deletes and deletes.get("actionNames"):
            names_to_delete = set(deletes["actionNames"])
            self._schedules[channel_id] = [
                a
                for a in self._schedules[channel_id]
                if a.get("actionName") not in names_to_delete
            ]
            deleted_actions = list(names_to_delete)

        created_actions: list[dict[str, Any]] = []
        if creates and creates.get("scheduleActions"):
            for action in creates["scheduleActions"]:
                self._schedules[channel_id].append(action)
                created_actions.append(action)

        return {
            "creates": {"scheduleActions": created_actions},
            "deletes": {"actionNames": deleted_actions},
        }

    def describe_schedule(self, channel_id: str) -> list[dict[str, Any]]:
        if channel_id not in self._channels:
            raise NotFoundException(f"Channel {channel_id} not found")
        return self._schedules.get(channel_id, [])

    def delete_schedule(self, channel_id: str) -> None:
        if channel_id not in self._channels:
            raise NotFoundException(f"Channel {channel_id} not found")
        self._schedules[channel_id] = []

    # ---- Batch operations ----

    def batch_delete(
        self,
        channel_ids: Optional[list[str]],
        input_ids: Optional[list[str]],
        input_security_group_ids: Optional[list[str]],
        multiplex_ids: Optional[list[str]],
    ) -> dict[str, list[dict[str, str]]]:
        failed: list[dict[str, str]] = []
        successful: list[dict[str, str]] = []

        for cid in channel_ids or []:
            if cid in self._channels:
                self._channels[cid].state = "DELETING"
                successful.append({"arn": self._channels[cid].arn, "id": cid})
            else:
                failed.append(
                    {"arn": "", "code": "404", "id": cid, "message": "Not found"}
                )

        for iid in input_ids or []:
            if iid in self._inputs:
                self._inputs[iid].state = "DELETING"
                successful.append({"arn": self._inputs[iid].arn, "id": iid})
            else:
                failed.append(
                    {"arn": "", "code": "404", "id": iid, "message": "Not found"}
                )

        for gid in input_security_group_ids or []:
            if gid in self._input_security_groups:
                del self._input_security_groups[gid]
                successful.append({"id": gid})
            else:
                failed.append(
                    {"arn": "", "code": "404", "id": gid, "message": "Not found"}
                )

        for mid in multiplex_ids or []:
            if mid in self._multiplexes:
                self._multiplexes[mid].state = "DELETING"
                successful.append({"arn": self._multiplexes[mid].arn, "id": mid})
            else:
                failed.append(
                    {"arn": "", "code": "404", "id": mid, "message": "Not found"}
                )

        return {"failed": failed, "successful": successful}

    def batch_start(
        self,
        channel_ids: Optional[list[str]],
        multiplex_ids: Optional[list[str]],
    ) -> dict[str, list[dict[str, str]]]:
        failed: list[dict[str, str]] = []
        successful: list[dict[str, str]] = []

        for cid in channel_ids or []:
            if cid in self._channels:
                self._channels[cid].state = "STARTING"
                successful.append({"arn": self._channels[cid].arn, "id": cid})
            else:
                failed.append(
                    {"arn": "", "code": "404", "id": cid, "message": "Not found"}
                )

        for mid in multiplex_ids or []:
            if mid in self._multiplexes:
                self._multiplexes[mid].state = "STARTING"
                successful.append({"arn": self._multiplexes[mid].arn, "id": mid})
            else:
                failed.append(
                    {"arn": "", "code": "404", "id": mid, "message": "Not found"}
                )

        return {"failed": failed, "successful": successful}

    def batch_stop(
        self,
        channel_ids: Optional[list[str]],
        multiplex_ids: Optional[list[str]],
    ) -> dict[str, list[dict[str, str]]]:
        failed: list[dict[str, str]] = []
        successful: list[dict[str, str]] = []

        for cid in channel_ids or []:
            if cid in self._channels:
                self._channels[cid].state = "STOPPING"
                successful.append({"arn": self._channels[cid].arn, "id": cid})
            else:
                failed.append(
                    {"arn": "", "code": "404", "id": cid, "message": "Not found"}
                )

        for mid in multiplex_ids or []:
            if mid in self._multiplexes:
                self._multiplexes[mid].state = "STOPPING"
                successful.append({"arn": self._multiplexes[mid].arn, "id": mid})
            else:
                failed.append(
                    {"arn": "", "code": "404", "id": mid, "message": "Not found"}
                )

        return {"failed": failed, "successful": successful}

    # ---- Account Configuration ----

    def describe_account_configuration(self) -> dict[str, Any]:
        return {"accountConfiguration": {"kmsKeyId": None}}

    def update_account_configuration(
        self, account_configuration: Optional[dict[str, Any]]
    ) -> dict[str, Any]:
        return {"accountConfiguration": account_configuration or {"kmsKeyId": None}}

    # ---- Stubs for InputDevice, Offering, Reservation (no local state) ----

    def list_input_devices(self) -> list[Any]:
        return []

    def describe_input_device(self, input_device_id: str) -> dict[str, Any]:
        raise NotFoundException(f"InputDevice {input_device_id} not found")

    def update_input_device(
        self, input_device_id: str, **kwargs: Any
    ) -> dict[str, Any]:
        raise NotFoundException(f"InputDevice {input_device_id} not found")

    def accept_input_device_transfer(self, input_device_id: str) -> None:
        raise NotFoundException(f"InputDevice {input_device_id} not found")

    def cancel_input_device_transfer(self, input_device_id: str) -> None:
        raise NotFoundException(f"InputDevice {input_device_id} not found")

    def reject_input_device_transfer(self, input_device_id: str) -> None:
        raise NotFoundException(f"InputDevice {input_device_id} not found")

    def reboot_input_device(self, input_device_id: str) -> None:
        raise NotFoundException(f"InputDevice {input_device_id} not found")

    def start_input_device(self, input_device_id: str) -> None:
        raise NotFoundException(f"InputDevice {input_device_id} not found")

    def stop_input_device(self, input_device_id: str) -> None:
        raise NotFoundException(f"InputDevice {input_device_id} not found")

    def start_input_device_maintenance_window(self, input_device_id: str) -> None:
        raise NotFoundException(f"InputDevice {input_device_id} not found")

    def transfer_input_device(self, input_device_id: str, **kwargs: Any) -> None:
        raise NotFoundException(f"InputDevice {input_device_id} not found")

    def describe_input_device_thumbnail(
        self, input_device_id: str, accept: str
    ) -> bytes:
        raise NotFoundException(f"InputDevice {input_device_id} not found")

    def list_input_device_transfers(self, transfer_type: str) -> list[Any]:
        return []

    def claim_device(self, **kwargs: Any) -> None:
        pass  # No-op stub

    def list_offerings(self) -> list[Any]:
        return []

    def describe_offering(self, offering_id: str) -> dict[str, Any]:
        raise NotFoundException(f"Offering {offering_id} not found")

    def purchase_offering(self, offering_id: str, **kwargs: Any) -> dict[str, Any]:
        raise NotFoundException(f"Offering {offering_id} not found")

    def list_reservations(self) -> list[Any]:
        return []

    def describe_reservation(self, reservation_id: str) -> dict[str, Any]:
        raise NotFoundException(f"Reservation {reservation_id} not found")

    def delete_reservation(self, reservation_id: str) -> dict[str, Any]:
        raise NotFoundException(f"Reservation {reservation_id} not found")

    def update_reservation(self, reservation_id: str, **kwargs: Any) -> dict[str, Any]:
        raise NotFoundException(f"Reservation {reservation_id} not found")

    # ---- Misc stubs ----

    def describe_thumbnails(
        self, channel_id: str, pipeline_id: str, thumbnail_type: str
    ) -> list[Any]:
        if channel_id not in self._channels:
            raise NotFoundException(f"Channel {channel_id} not found")
        return []

    def list_alerts(self, channel_id: str) -> list[Any]:
        return []

    def list_cluster_alerts(self, cluster_id: str) -> list[Any]:
        if cluster_id not in self._clusters:
            raise NotFoundException(f"Cluster {cluster_id} not found")
        return []

    def list_multiplex_alerts(self, multiplex_id: str) -> list[Any]:
        if multiplex_id not in self._multiplexes:
            raise NotFoundException(f"Multiplex {multiplex_id} not found")
        return []

    def list_versions(self) -> list[dict[str, Any]]:
        return [{"engineVersions": [{"version": "1.0"}]}]


medialive_backends = BackendDict(MediaLiveBackend, "medialive")
