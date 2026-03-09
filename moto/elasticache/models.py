import copy
import random
import string
from re import compile as re_compile
from typing import Any, Optional, Union

from moto.core.base_backend import BackendDict, BaseBackend
from moto.core.common_models import BaseModel
from moto.core.utils import utcnow
from moto.utilities.tagging_service import TaggingService
from moto.utilities.utils import get_partition

from ..moto_api._internal import mock_random
from .exceptions import (
    CacheClusterAlreadyExists,
    CacheClusterNotFound,
    CacheParameterGroupAlreadyExists,
    CacheParameterGroupNotFound,
    CacheSecurityGroupAlreadyExists,
    CacheSecurityGroupNotFound,
    CacheSubnetGroupAlreadyExists,
    CacheSubnetGroupNotFound,
    GlobalReplicationGroupAlreadyExists,
    GlobalReplicationGroupNotFound,
    InvalidARNFault,
    InvalidParameterCombinationException,
    InvalidParameterValueException,
    InvalidSubnet,
    ReplicationGroupAlreadyExists,
    ReplicationGroupNotFound,
    ServerlessCacheAlreadyExists,
    ServerlessCacheNotFound,
    SnapshotAlreadyExists,
    SnapshotNotFound,
    UserAlreadyExists,
    UserGroupAlreadyExists,
    UserGroupNotFound,
    UserNotFound,
)
from .utils import AuthenticationTypes


class User(BaseModel):
    def __init__(
        self,
        account_id: str,
        region: str,
        user_id: str,
        user_name: str,
        access_string: str,
        engine: str,
        no_password_required: bool,
        passwords: Optional[list[str]] = None,
        authentication_type: Optional[str] = None,
        tags: Optional[list[dict[str, str]]] = None,
    ):
        self.id = user_id
        self.name = user_name
        self.engine = engine

        self.passwords = passwords or []
        self.access_string = access_string
        self.no_password_required = no_password_required
        self.status = "active"
        self.minimum_engine_version = "6.0"
        self.user_group_ids: list[str] = []
        self.region = region
        self.arn = f"arn:{get_partition(self.region)}:elasticache:{self.region}:{account_id}:user:{self.id}"
        self.authentication_type = authentication_type
        self.tags = tags or []

    @property
    def authentication(self) -> dict[str, Union[str, int, None]]:
        return {
            "Type": "no-password"
            if self.no_password_required
            else self.authentication_type,
            "PasswordCount": len(self.passwords) if self.passwords else None,
        }


class CacheCluster(BaseModel):
    def __init__(
        self,
        account_id: str,
        region_name: str,
        cache_cluster_id: str,
        cache_node_type: str,
        replication_group_id: Optional[str],
        az_mode: Optional[str],
        preferred_availability_zone: Optional[str],
        num_cache_nodes: Optional[int],
        engine: Optional[str],
        engine_version: Optional[str],
        cache_parameter_group_name: Optional[str],
        cache_subnet_group_name: Optional[str],
        transit_encryption_enabled: Optional[bool],
        network_type: Optional[str],
        ip_discovery: Optional[str],
        snapshot_name: Optional[str],
        preferred_maintenance_window: Optional[str],
        port: Optional[int],
        notification_topic_arn: Optional[str],
        auto_minor_version_upgrade: Optional[bool],
        snapshot_retention_limit: Optional[int],
        snapshot_window: Optional[str],
        auth_token: Optional[str],
        outpost_mode: Optional[str],
        preferred_outpost_arn: Optional[str],
        preferred_availability_zones: Optional[list[str]],
        cache_security_group_names: Optional[list[str]],
        security_group_ids: Optional[list[str]],
        tags: Optional[list[dict[str, str]]],
        snapshot_arns: Optional[list[str]],
        preferred_outpost_arns: Optional[list[str]],
        log_delivery_configurations: list[dict[str, Any]],
        cache_node_ids_to_remove: Optional[list[str]],
        cache_node_ids_to_reboot: Optional[list[str]],
    ):
        self.cache_cluster_id = cache_cluster_id
        self.az_mode = az_mode
        self.preferred_availability_zone = preferred_availability_zone
        self.preferred_availability_zones = preferred_availability_zones or []
        self.engine = engine or "redis"
        self.engine_version = engine_version
        if engine == "redis":
            self.num_cache_nodes = 1
            self.replication_group_id = replication_group_id
            self.snapshot_arns = snapshot_arns or []
            self.snapshot_name = snapshot_name
            self.snapshot_window = snapshot_window
        if engine == "memcached":
            if num_cache_nodes is None:
                self.num_cache_nodes = 1
            elif 1 <= num_cache_nodes <= 40:
                self.num_cache_nodes = num_cache_nodes
        self.cache_node_type = cache_node_type
        self.cache_parameter_group_name = cache_parameter_group_name
        self.cache_subnet_group_name = cache_subnet_group_name
        self.cache_security_group_names = cache_security_group_names or []
        self.security_group_ids = security_group_ids or []
        self.tags = tags or []
        self.preferred_maintenance_window = preferred_maintenance_window
        self.port = port or 6379
        self.notification_topic_arn = notification_topic_arn
        self.auto_minor_version_upgrade = auto_minor_version_upgrade
        self.snapshot_retention_limit = snapshot_retention_limit or 0
        self.auth_token = auth_token
        self.auth_token_enabled = bool(auth_token)
        self.outpost_mode = outpost_mode
        self.preferred_outpost_arn = preferred_outpost_arn
        self.preferred_outpost_arns = preferred_outpost_arns or []
        self.log_delivery_configurations = log_delivery_configurations or []
        self.transit_encryption_enabled = transit_encryption_enabled
        self.network_type = network_type
        self.ip_discovery = ip_discovery
        self.cache_node_ids_to_remove = cache_node_ids_to_remove
        self.cache_node_ids_to_reboot = cache_node_ids_to_reboot

        self.cache_cluster_create_time = utcnow()
        self.auth_token_last_modified_date = utcnow()
        self.cache_cluster_status = "available"
        self.arn = f"arn:{get_partition(region_name)}:elasticache:{region_name}:{account_id}:cluster:{cache_cluster_id}"
        self.cache_node_id = str(mock_random.uuid4())
        self.status = "available"


class CacheSubnetGroup(BaseModel):
    def __init__(
        self,
        account_id: str,
        region_name: str,
        cache_subnet_group_name: str,
        cache_subnet_group_description: str,
        subnet_ids: list[str],
        tags: Optional[list[dict[str, str]]],
    ):
        self.cache_subnet_group_name = cache_subnet_group_name
        self.cache_subnet_group_description = cache_subnet_group_description
        self.subnet_ids = subnet_ids
        self.tags = tags or []

        # Only import ec2_backends if necessary
        from moto.ec2.models import ec2_backends

        ec2_backend = ec2_backends[account_id][region_name]
        self.supported_network_types = []
        self.subnets = []
        vpc_exists = False
        try:
            # Get VPC details from provided subnet IDs
            subnets = ec2_backend.describe_subnets(subnet_ids=subnet_ids)
            vpc_exists = True
        except Exception as e:
            # Should raise InvalidSubnet if subnet_ids are invalid
            if "InvalidSubnet" in str(e):
                for subnet_id in subnet_ids:
                    subnet_response: dict[str, Any] = {}
                    subnet_response["subnet_identifier"] = subnet_id
                    subnet_response["Subnet_availability_zone"] = {"Name": "us-east-1a"}
                    subnet_response["supported_network_types"] = ["ipv4"]
                    self.subnets.append(subnet_response)
                vpcs = ["vpc-0123456789abcdef0"]
                self.supported_network_types = ["ipv4"]

        if vpc_exists:
            vpcs = []
            for subnet in subnets:
                subnet_response = {}
                vpcs.append(subnet.vpc_id)
                subnet_response["subnet_identifier"] = subnet.id
                subnet_response["subnet_availability_zone"] = subnet.availability_zone
                subnet_response["supported_network_types"] = []
                if subnet.vpc_id != vpcs[0]:
                    raise InvalidSubnet(subnet_id=subnet.id)

                # ipv6 native subnets only appends ipv6
                # You can't mix ipv6 native subnets with other types of subnets
                if subnet.ipv6_native:
                    self.supported_network_types.append("ipv6")
                    subnet_response["supported_network_types"].append("ipv6")

                # ipv4 only and dual_stack subnets both append ipv4
                elif subnet.cidr_block:
                    self.supported_network_types.append("ipv4")
                    subnet_response["supported_network_types"].append("ipv4")

                if subnet.ipv6_cidr_block_associations and subnet.cidr_block:
                    self.supported_network_types.append("dual_stack")
                    subnet_response["supported_network_types"].append("dual_stack")

                self.subnets.append(subnet_response)

            if self.supported_network_types:
                self.supported_network_types = list(set(self.supported_network_types))

        self.arn = f"arn:aws:elasticache:{region_name}:{account_id}:subnetgroup:{cache_subnet_group_name}"
        self.vpc_id = vpcs[0] if vpcs else None


class ReplicationGroup(BaseModel):
    def __init__(
        self,
        account_id: str,
        region_name: str,
        replication_group_id: str,
        preferred_cache_cluster_azs: Optional[list[str]],
        num_cache_clusters: Optional[int],
        num_node_groups: Optional[int],
        replicas_per_node_group: Optional[int],
        node_group_configuration: list[dict[str, Any]],
        preferred_maintenance_window: Optional[str],
        replication_group_description: str,
        primary_cluster_id: Optional[str],
        automatic_failover_enabled: bool,
        global_replication_group_id: Optional[str],
        multi_az_enabled: Optional[bool],
        port: Optional[int],
        snapshot_retention_limit: int,
        snapshot_window: Optional[str],
        cluster_mode: Optional[str],
        cache_node_type: Optional[str],
        auth_token: Optional[str],
        transit_encryption_enabled: Optional[bool],
        at_rest_encryption_enabled: Optional[bool],
        kms_key_id: Optional[str],
        user_group_ids: list[str],
        log_delivery_configurations: list[dict[str, Any]],
        data_tiering_enabled: Optional[bool],
        auto_minor_version_upgrade: Optional[bool],
        engine: Optional[str],
        network_type: Optional[str],
        ip_discovery: Optional[str],
        transit_encryption_mode: Optional[str],
        cache_security_group_names: Optional[list[str]],
        cache_subnet_group_name: Optional[str],
        security_group_ids: Optional[list[str]],
        tags: Optional[list[dict[str, str]]],
        notification_topic_arn: Optional[str],
        serverless_cache_snapshot_name: Optional[str],
        cache_parameter_group_name: Optional[str],
        engine_version: Optional[str],
        snapshot_arns: Optional[list[str]],
        snapshot_name: Optional[str],
    ):
        tags = tags or []
        self.cluster_mode = cluster_mode or "disabled"
        self.replication_group_id = replication_group_id
        self.description = replication_group_description
        self.port = port or 6379
        self.status = "available"

        preferred_cache_cluster_azs = preferred_cache_cluster_azs or []
        replicas_per_node_group = replicas_per_node_group or 0

        # This field is only present if we are creating a
        # secondary replication group and associating it with an existing
        # global replication group and primary cluster.
        if global_replication_group_id:
            self.global_replication_group_id = global_replication_group_id
            self.global_replication_group_member_role = "SECONDARY"
        else:
            self.global_replication_group_id = ""

        # Leaving off PendingModifiedValues for now
        # until global_replication_group is implemented.
        self.primary_cluster_id = primary_cluster_id

        self.node_groups = []
        random_str = "".join(
            random.choices(string.ascii_lowercase + string.digits, k=6)
        )
        region_short = "use1"
        replication_group_domain = (
            f"{replication_group_id}.{random_str}.{region_short}.cache.amazonaws.com"
        )
        self.member_clusters: list[str] = []
        self.member_clusters_outpost_arns: list[str] = []
        if not num_node_groups:
            num_node_groups = 1

        for i in range(num_node_groups):
            node_group: dict[str, Any] = {}
            node_group["node_group_id"] = f"{i + 1:0>4}"
            node_group["status"] = "available"
            node_group["node_group_members"] = []

            if self.cluster_mode == "enabled":
                if i == 0:
                    node_group["slots"] = "0-5461"
                else:
                    # slots cannot overlap among node groups
                    node_group["slots"] = (
                        f"{(5460 * (i)) + (i + 1)}-{(5460 * (i + 1)) + (i + 1)}"
                    )

                replicas_per_node_group = replicas_per_node_group or 0
                self._set_node_members_clusters_enabled(
                    member_clusters=self.member_clusters,
                    replication_group_id=replication_group_id,
                    replicas_per_node_group=replicas_per_node_group,
                    node_group_configuration=node_group_configuration,
                    node_group=node_group,
                    member_clusters_outpost_arns=self.member_clusters_outpost_arns,
                )

                self.configuration_endpoint: dict[str, Any] = {}
                self.configuration_endpoint["address"] = (
                    f"clustercfg.{replication_group_domain}"
                )
                self.configuration_endpoint["port"] = self.port

            # self.cluster_mode is disabled or not set
            else:
                node_group["primary_endpoint_address"] = (
                    f"master.{replication_group_domain}"
                )
                node_group["reader_endpoint_address"] = (
                    f"replica.{replication_group_domain}"
                )
                node_group["port"] = self.port
                node_group["primary_endpoint"] = {
                    "address": node_group["primary_endpoint_address"],
                    "port": self.port,
                }

                num_cache_clusters = num_cache_clusters or 1

                self._set_node_members_clusters_disabled(
                    member_clusters=self.member_clusters,
                    replication_group_id=replication_group_id,
                    replication_group_domain=replication_group_domain,
                    node_group=node_group,
                    preferred_cache_cluster_azs=preferred_cache_cluster_azs,
                    num_cache_clusters=num_cache_clusters,
                    replicas_per_node_group=replicas_per_node_group,
                )
            self.node_groups.append(node_group)

        self.automatic_failover = (
            "enabled" if automatic_failover_enabled else "disabled"
        )
        self.multi_az = "enabled" if multi_az_enabled else "disabled"
        self.snapshot_retention_limit = snapshot_retention_limit or 0
        self.snapshot_window = snapshot_window or "05:00-6:00"
        self.snapshotting_cluster_id = None
        if self.snapshot_retention_limit > 0:
            if len(self.member_clusters) > 1:
                self.snapshotting_cluster_id = self.member_clusters[1]
            else:
                self.snapshotting_cluster_id = self.member_clusters[0]
        self.cluster_enabled = True if self.cluster_mode == "enabled" else False
        self.cache_node_type = cache_node_type or "cache.t4g.micro"
        self.auth_token_enabled = bool(auth_token)
        self.auth_token_last_modified_date = (
            utcnow() if self.auth_token_enabled else None
        )
        self.transit_encryption_enabled = transit_encryption_enabled or False
        self.at_rest_encryption_enabled = at_rest_encryption_enabled or False
        self.kms_key_id = kms_key_id
        self.arn = f"arn:aws:elasticache:{region_name}:{account_id}:replicationgroup:{replication_group_id}"
        self.user_group_ids = user_group_ids or []
        self.log_delivery_configurations = self._get_log_delivery_configurations(
            log_delivery_configurations
        )
        self.replication_group_create_time = utcnow()
        self.data_tiering = "enabled" if data_tiering_enabled else "disabled"
        self.auto_minor_version_upgrade = auto_minor_version_upgrade
        self.network_type = network_type or "ipv4"
        self.ip_discovery = ip_discovery or "ipv4"
        self.transit_encryption_mode = transit_encryption_mode
        self.engine = engine or "redis"

        # Parameters not returned by create or describe replication group
        self.cache_security_group_names = cache_security_group_names
        self.cache_subnet_group_name = cache_subnet_group_name
        self.security_group_ids = security_group_ids
        self.tags = tags
        self.preferred_maintenance_window = preferred_maintenance_window
        self.notification_topic_arn = notification_topic_arn
        self.serverless_cache_snapshot_name = serverless_cache_snapshot_name
        self.cache_parameter_group_name = cache_parameter_group_name
        self.engine_version = engine_version
        self.snapshot_arns = snapshot_arns
        self.snapshot_name = snapshot_name

    @property
    def global_replication_group_info(self) -> dict[str, str]:
        return {
            "GlobalReplicationGroupId": self.global_replication_group_id,
            "GlobalReplicationGroupMemberRole": self.global_replication_group_member_role,
        }

    def _get_log_delivery_configurations(
        self, log_delivery_configurations: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        log_delivery_configurations_resp = []
        if log_delivery_configurations:
            for log_delivery_configuration in log_delivery_configurations:
                log_config_resp = copy.copy(log_delivery_configuration)
                log_config_resp["status"] = "active"
                log_config_resp["message"] = "Log delivery configuration is active."

                log_delivery_configurations_resp.append(log_config_resp)
        return log_delivery_configurations_resp

    # This method will set populate the node_group with node_group_members
    # and member_clusters with the cache_cluster_ids of the primary and replicas.
    def _set_node_members_clusters_enabled(
        self,
        member_clusters: list[str],
        replication_group_id: str,
        replicas_per_node_group: int,
        node_group_configuration: list[dict[str, Any]],
        node_group: dict[str, Any],
        member_clusters_outpost_arns: list[str],
    ) -> None:
        replica_count = replicas_per_node_group
        primary_node = {}
        primary_node["cache_cluster_id"] = (
            f"{replication_group_id}-{node_group['node_group_id']}-001"
        )
        primary_node["cache_node_id"] = node_group["node_group_id"]

        # Set the PreferredAvailabilityZone,
        # default to us-east-1a for moto only
        primary_node["preferred_availability_zone"] = "us-east-1a"

        # With node_group_configurations
        node_config = {}
        if node_group_configuration:
            for config in node_group_configuration:
                if node_group["node_group_id"] == config.get("NodeGroupId"):
                    node_config = config
                    # overwrite slots if part of node config
                    if config.get("Slots"):
                        node_group["slots"] = config.get("Slots")

                    replica_count_val = config.get("ReplicaCount")
                    if replica_count_val is not None:
                        replica_count = int(replica_count_val)
                    else:
                        replica_count = replicas_per_node_group

                    primary_node["preferred_availability_zone"] = config.get(
                        "PrimaryAvailabilityZone", "us-east-1a"
                    )
                    primary_outpost_arn = config.get("PrimaryOutpostArn", "")
                    if primary_outpost_arn:
                        primary_node["preferred_outpost_arn"] = primary_outpost_arn
                        member_clusters_outpost_arns.append(primary_outpost_arn)

        node_group["node_group_members"].append(primary_node)
        member_clusters.append(primary_node["cache_cluster_id"])

        #  Loop through the number of replicas per node group
        for r in range(1, replica_count + 1):
            replica_node = {}
            # r + 1 because primary is 001
            replica_node["cache_cluster_id"] = (
                f"{replication_group_id}-{node_group['node_group_id']}-{r + 1:0>3}"
            )
            replica_node["cache_node_id"] = node_group["node_group_id"]

            # Set the ReplicaAvailabiilityZone,
            # default to us-east-1b for moto only
            replica_node["preferred_availability_zone"] = "us-east-1b"

            if node_config:
                replica_az = node_config.get("ReplicaAvailabilityZones")
                if replica_az:
                    if len(replica_az) >= r:
                        replica_node["preferred_availability_zone"] = replica_az[r - 1]
                    elif len(replica_az) >= 1:
                        replica_node["preferred_availability_zone"] = replica_az[0]
                replica_outpost_arns = node_config.get("ReplicaOutpostArns", [])
                if replica_outpost_arns:
                    if len(replica_outpost_arns) >= r:
                        replica_node["preferred_outpost_arn"] = replica_outpost_arns[
                            r - 1
                        ]
                    elif len(replica_outpost_arns) >= 1:
                        replica_node["preferred_outpost_arn"] = replica_outpost_arns[0]

                    member_clusters_outpost_arns.append(
                        replica_node["preferred_outpost_arn"]
                    )

            node_group["node_group_members"].append(replica_node)
            member_clusters.append(replica_node["cache_cluster_id"])

    def _set_node_members_clusters_disabled(
        self,
        member_clusters: list[str],
        replication_group_id: str,
        replication_group_domain: str,
        node_group: dict[str, Any],
        preferred_cache_cluster_azs: list[str],
        num_cache_clusters: int,
        replicas_per_node_group: int,
    ) -> None:
        primary_node: dict[str, Any] = {}
        primary_node["cache_cluster_id"] = f"{replication_group_id}-001"
        primary_node["cache_node_id"] = node_group["node_group_id"]
        primary_node["read_endpoint"] = {}
        primary_node["read_endpoint"]["address"] = (
            f"{primary_node['cache_cluster_id']}.{replication_group_domain}"
        )
        primary_node["read_endpoint"]["port"] = self.port

        if preferred_cache_cluster_azs:
            primary_node["preferred_availability_zone"] = preferred_cache_cluster_azs[0]
        else:
            primary_node["preferred_availability_zone"] = "us-east-1a"

        primary_node["current_role"] = "primary"
        node_group["node_group_members"].append(primary_node)
        member_clusters.append(primary_node["cache_cluster_id"])

        if replicas_per_node_group:
            num_cache_clusters = replicas_per_node_group + 1
        else:
            num_cache_clusters = 1

        # Use num_cache_clusters when cluster_mode is disabled
        for r in range(1, num_cache_clusters):
            replica_node: dict[str, Any] = {}
            # r + 1 because primary is 001
            replica_node["cache_cluster_id"] = f"{replication_group_id}-{r + 1:0>3}"
            replica_node["cache_node_id"] = node_group["node_group_id"]
            replica_node["read_endpoint"] = {}
            replica_node["read_endpoint"]["address"] = (
                f"{replica_node['cache_cluster_id']}.{replication_group_domain}"
            )
            replica_node["read_endpoint"]["port"] = self.port

            if preferred_cache_cluster_azs:
                if len(preferred_cache_cluster_azs) > r:
                    replica_az = preferred_cache_cluster_azs[r]
                elif len(preferred_cache_cluster_azs) >= 2:
                    replica_az = preferred_cache_cluster_azs[1]
                else:
                    replica_az = preferred_cache_cluster_azs[0]
            else:
                replica_az = "us-east-1b"

            replica_node["preferred_availability_zone"] = replica_az
            replica_node["current_role"] = "replica"

            node_group["node_group_members"].append(replica_node)
            member_clusters.append(replica_node["cache_cluster_id"])


class Snapshot(BaseModel):
    def __init__(
        self,
        account_id: str,
        region_name: str,
        automatic_failover: Optional[bool],
        auto_minor_version_upgrade: Optional[bool],
        cache_cluster_create_time: Optional[str],
        cache_cluster_id: Optional[str],
        cache_node_type: Optional[str],
        cache_parameter_group_name: Optional[str],
        cache_subnet_group_name: Optional[str],
        engine: Optional[str],
        engine_version: Optional[str],
        kms_key_id: Optional[str],
        num_cache_nodes: Optional[int],
        num_node_groups: Optional[int],
        port: Optional[int],
        preferred_availability_zone: Optional[str],
        preferred_maintenance_window: Optional[str],
        preferred_outpost_arn: Optional[str],
        replication_group_description: Optional[str],
        replication_group_id: Optional[str],
        snapshot_name: Optional[str],
        snapshot_retention_limit: Optional[int],
        snapshot_source: Optional[str],
        snapshot_status: Optional[str],
        snapshot_window: Optional[str],
        topic_arn: Optional[str],
        tags: Optional[list[dict[str, str]]],
        vpc_id: Optional[str] = None,
    ):
        self.arn = f"arn:{get_partition(region_name)}:elasticache:{region_name}:{account_id}:snapshot:{snapshot_name}"
        self.automatic_failover = automatic_failover
        self.auto_minor_version_upgrade = auto_minor_version_upgrade
        self.cache_cluster_create_time = cache_cluster_create_time
        self.cache_cluster_id = cache_cluster_id
        self.cache_node_type = cache_node_type
        self.cache_parameter_group_name = cache_parameter_group_name
        self.cache_subnet_group_name = cache_subnet_group_name
        self.engine = engine
        self.engine_version = engine_version
        self.kms_key_id = kms_key_id
        self.num_cache_nodes = num_cache_nodes
        self.num_node_groups = num_node_groups
        self.port = port
        self.preferred_availability_zone = preferred_availability_zone
        self.preferred_maintenance_window = preferred_maintenance_window
        self.preferred_outpost_arn = preferred_outpost_arn
        self.replication_group_description = replication_group_description
        self.replication_group_id = replication_group_id
        self.snapshot_name = snapshot_name
        self.snapshot_retention_limit = snapshot_retention_limit
        self.snapshot_source = snapshot_source or "manual"
        self.snapshot_status = snapshot_status
        self.snapshot_window = snapshot_window
        self.topic_arn = topic_arn
        self.tags = tags or []
        self.vpc_id = vpc_id


class CacheParameterGroup(BaseModel):
    def __init__(
        self,
        account_id: str,
        region: str,
        cache_parameter_group_name: str,
        cache_parameter_group_family: str,
        description: str,
        tags: Optional[list[dict[str, str]]] = None,
    ):
        self.cache_parameter_group_name = cache_parameter_group_name
        self.cache_parameter_group_family = cache_parameter_group_family
        self.description = description
        self.is_global = False
        self.arn = f"arn:{get_partition(region)}:elasticache:{region}:{account_id}:parametergroup:{cache_parameter_group_name}"
        self.tags = tags or []
        # User-modified parameters (key -> value)
        self.parameters: dict[str, str] = {}


class CacheSecurityGroup(BaseModel):
    def __init__(
        self,
        account_id: str,
        region: str,
        cache_security_group_name: str,
        description: str,
        tags: Optional[list[dict[str, str]]] = None,
    ):
        self.cache_security_group_name = cache_security_group_name
        self.description = description
        self.owner_id = account_id
        self.arn = f"arn:{get_partition(region)}:elasticache:{region}:{account_id}:securitygroup:{cache_security_group_name}"
        self.ec2_security_groups: list[dict[str, str]] = []
        self.tags = tags or []


class UserGroup(BaseModel):
    def __init__(
        self,
        account_id: str,
        region: str,
        user_group_id: str,
        engine: str,
        user_ids: Optional[list[str]] = None,
        tags: Optional[list[dict[str, str]]] = None,
    ):
        self.user_group_id = user_group_id
        self.engine = engine
        self.user_ids = user_ids or ["default"]
        self.status = "active"
        self.minimum_engine_version = "6.0"
        self.replication_groups: list[str] = []
        self.serverless_caches: list[str] = []
        self.arn = f"arn:{get_partition(region)}:elasticache:{region}:{account_id}:usergroup:{user_group_id}"
        self.tags = tags or []


class ServerlessCache(BaseModel):
    def __init__(
        self,
        account_id: str,
        region: str,
        serverless_cache_name: str,
        engine: str,
        description: Optional[str] = None,
        major_engine_version: Optional[str] = None,
        cache_usage_limits: Optional[dict[str, Any]] = None,
        kms_key_id: Optional[str] = None,
        security_group_ids: Optional[list[str]] = None,
        snapshot_arns_to_restore: Optional[list[str]] = None,
        subnet_ids: Optional[list[str]] = None,
        daily_snapshot_time: Optional[str] = None,
        snapshot_retention_limit: Optional[int] = None,
        user_group_id: Optional[str] = None,
        tags: Optional[list[dict[str, str]]] = None,
    ):
        self.serverless_cache_name = serverless_cache_name
        self.engine = engine
        self.description = description or ""
        self.major_engine_version = major_engine_version or "7"
        self.full_engine_version = f"{self.major_engine_version}.1.0"
        self.cache_usage_limits = cache_usage_limits or {
            "DataStorage": {"Maximum": 5, "Minimum": 1, "Unit": "GB"},
            "ECPUPerSecond": {"Maximum": 15000, "Minimum": 1000},
        }
        self.kms_key_id = kms_key_id
        self.security_group_ids = security_group_ids or []
        self.subnet_ids = subnet_ids or []
        self.daily_snapshot_time = daily_snapshot_time or "03:00"
        self.snapshot_retention_limit = snapshot_retention_limit or 0
        self.user_group_id = user_group_id
        self.status = "available"
        self.create_time = utcnow()
        self.arn = f"arn:{get_partition(region)}:elasticache:{region}:{account_id}:serverlesscache:{serverless_cache_name}"
        self.tags = tags or []
        self.endpoint = {
            "Address": f"{serverless_cache_name}.serverless.{region}.cache.amazonaws.com",
            "Port": 6379,
        }
        self.reader_endpoint = {
            "Address": f"{serverless_cache_name}.serverless.{region}.cache.amazonaws.com",
            "Port": 6379,
        }


class GlobalReplicationGroup(BaseModel):
    def __init__(
        self,
        account_id: str,
        region: str,
        global_replication_group_id_suffix: str,
        primary_replication_group_id: str,
        global_replication_group_description: Optional[str] = None,
    ):
        self.global_replication_group_id_suffix = global_replication_group_id_suffix
        self.global_replication_group_id = f"lstgl-{global_replication_group_id_suffix}"
        self.global_replication_group_description = global_replication_group_description or ""
        self.status = "available"
        self.cache_node_type = "cache.r6g.large"
        self.engine = "redis"
        self.engine_version = "7.1.0"
        self.cluster_enabled = False
        self.auth_token_enabled = False
        self.transit_encryption_enabled = False
        self.at_rest_encryption_enabled = False
        self.arn = f"arn:{get_partition(region)}:elasticache::{account_id}:globalreplicationgroup:{self.global_replication_group_id}"
        self.members: list[dict[str, Any]] = [
            {
                "ReplicationGroupId": primary_replication_group_id,
                "ReplicationGroupRegion": region,
                "Role": "PRIMARY",
                "AutomaticFailover": "enabled",
                "Status": "associated",
            }
        ]
        self.global_node_groups: list[dict[str, Any]] = []


class ServerlessCacheSnapshot(BaseModel):
    def __init__(
        self,
        account_id: str,
        region: str,
        serverless_cache_snapshot_name: str,
        serverless_cache_name: str,
        serverless_cache: Optional["ServerlessCache"] = None,
        tags: Optional[list[dict[str, str]]] = None,
    ):
        self.serverless_cache_snapshot_name = serverless_cache_snapshot_name
        self.serverless_cache_name = serverless_cache_name
        self.status = "available"
        self.create_time = utcnow()
        self.arn = f"arn:{get_partition(region)}:elasticache:{region}:{account_id}:serverlesscachesnapshot:{serverless_cache_snapshot_name}"
        self.tags = tags or []
        self.serverless_cache_configuration: dict[str, Any] = {}
        if serverless_cache:
            self.serverless_cache_configuration = {
                "ServerlessCacheName": serverless_cache.serverless_cache_name,
                "Engine": serverless_cache.engine,
                "MajorEngineVersion": serverless_cache.major_engine_version,
            }


class ElastiCacheBackend(BaseBackend):
    """Implementation of ElastiCache APIs."""

    def __init__(self, region_name: str, account_id: str):
        super().__init__(region_name, account_id)
        self.arn_regex = re_compile(
            r"^arn:aws:elasticache:.*:[0-9]*:(cluster|snapshot|subnetgroup|replicationgroup|user|parametergroup|securitygroup|usergroup|serverlesscache|globalreplicationgroup|serverlesscachesnapshot):.*$"
        )
        self.users = {}
        self.users["default"] = User(
            account_id=self.account_id,
            region=self.region_name,
            user_id="default",
            user_name="default",
            engine="redis",
            access_string="on ~* +@all",
            no_password_required=True,
        )

        self.cache_clusters: dict[str, Any] = {}
        self.cache_subnet_groups: dict[str, CacheSubnetGroup] = {}
        self.replication_groups: dict[str, ReplicationGroup] = {}
        self.snapshots: dict[str, Snapshot] = {}
        self.cache_parameter_groups: dict[str, CacheParameterGroup] = {}
        self.cache_security_groups: dict[str, CacheSecurityGroup] = {}
        self.user_groups: dict[str, UserGroup] = {}
        self.serverless_caches: dict[str, ServerlessCache] = {}
        self.global_replication_groups: dict[str, GlobalReplicationGroup] = {}
        self.serverless_cache_snapshots: dict[str, ServerlessCacheSnapshot] = {}
        self.tagging_service = TaggingService()

    def _get_snapshots_by_param(
        self,
        ref_id: Optional[str] = None,
        source: Optional[str] = None,
    ) -> list[Snapshot]:
        source_map = {
            "system": "automated",
            "user": "manual",
        }

        snapshots = list(self.snapshots.values())

        if ref_id:
            snapshots = [
                s
                for s in snapshots
                if s.cache_cluster_id == ref_id or s.replication_group_id == ref_id
            ]

        if source:
            actual_source = source_map.get(source.lower(), source.lower())
            snapshots = [s for s in snapshots if s.snapshot_source == actual_source]

        return snapshots

    def _get_vpc_id_from_cluster(self, cache_cluster_id: str) -> Optional[str]:
        if cache_cluster_id and cache_cluster_id in self.cache_clusters:
            cache_cluster = self.cache_clusters[cache_cluster_id]
            subnet_group_name = cache_cluster.cache_subnet_group_name
            if subnet_group_name and subnet_group_name in self.cache_subnet_groups:
                return self.cache_subnet_groups[subnet_group_name].vpc_id
        return None

    def create_user(
        self,
        user_id: str,
        user_name: str,
        engine: str,
        passwords: list[str],
        access_string: str,
        no_password_required: bool,
        authentication_type: str,  # contain it to the str in the enums TODO
        tags: Optional[list[dict[str, str]]] = None,
    ) -> User:
        if user_id in self.users:
            raise UserAlreadyExists

        if authentication_type not in AuthenticationTypes._value2member_map_:
            raise InvalidParameterValueException(
                f"Input Authentication type: {authentication_type} is not in the allowed list: [password,no-password-required,iam]"
            )

        if (
            no_password_required
            and authentication_type != AuthenticationTypes.NOPASSWORD
        ):
            raise InvalidParameterCombinationException(
                f"No password required flag is true but provided authentication type is {authentication_type}"
            )

        if passwords and authentication_type != AuthenticationTypes.PASSWORD:
            raise InvalidParameterCombinationException(
                f"Password field is not allowed with authentication type: {authentication_type}"
            )

        if not passwords and authentication_type == AuthenticationTypes.PASSWORD:
            raise InvalidParameterCombinationException(
                "A user with Authentication Mode: password, must have at least one password"
            )

        user = User(
            account_id=self.account_id,
            region=self.region_name,
            user_id=user_id,
            user_name=user_name,
            engine=engine,
            passwords=passwords,
            access_string=access_string,
            no_password_required=no_password_required,
            authentication_type=authentication_type,
            tags=tags,
        )

        if tags:
            self.tagging_service.tag_resource(user.arn, tags)

        self.users[user_id] = user
        return user

    def delete_user(self, user_id: str) -> User:
        if user_id in self.users:
            user = self.users[user_id]
            if user.status == "active":
                user.status = "deleting"
            return user
        raise UserNotFound(user_id)

    def describe_users(self, user_id: Optional[str]) -> list[User]:
        """
        Only the `user_id` parameter is currently supported.
        Pagination is not yet implemented.
        """
        if user_id:
            if user_id in self.users:
                user = self.users[user_id]
                if user.status == "deleting":
                    self.users.pop(user_id)
                return [user]
            else:
                raise UserNotFound(user_id)
        return list(self.users.values())

    def create_cache_cluster(
        self,
        cache_cluster_id: str,
        replication_group_id: str,
        az_mode: str,
        preferred_availability_zone: str,
        num_cache_nodes: int,
        cache_node_type: str,
        engine: str,
        engine_version: str,
        cache_parameter_group_name: str,
        cache_subnet_group_name: str,
        transit_encryption_enabled: bool,
        network_type: str,
        ip_discovery: str,
        snapshot_name: str,
        preferred_maintenance_window: str,
        port: int,
        notification_topic_arn: str,
        auto_minor_version_upgrade: bool,
        snapshot_retention_limit: int,
        snapshot_window: str,
        auth_token: str,
        outpost_mode: str,
        preferred_outpost_arn: str,
        preferred_availability_zones: list[str],
        cache_security_group_names: list[str],
        security_group_ids: list[str],
        tags: list[dict[str, str]],
        snapshot_arns: list[str],
        preferred_outpost_arns: list[str],
        log_delivery_configurations: list[dict[str, Any]],
        cache_node_ids_to_remove: list[str],
        cache_node_ids_to_reboot: list[str],
    ) -> CacheCluster:
        if cache_cluster_id in self.cache_clusters:
            raise CacheClusterAlreadyExists(cache_cluster_id)
        if cache_node_type is None or cache_node_type == "":
            raise InvalidParameterValueException(
                "The parameter CacheNodeType must be provided and must not be null."
            )
        cache_cluster = CacheCluster(
            account_id=self.account_id,
            region_name=self.region_name,
            cache_cluster_id=cache_cluster_id,
            replication_group_id=replication_group_id,
            az_mode=az_mode,
            preferred_availability_zone=preferred_availability_zone,
            preferred_availability_zones=preferred_availability_zones,
            num_cache_nodes=num_cache_nodes,
            cache_node_type=cache_node_type,
            engine=engine,
            engine_version=engine_version,
            cache_parameter_group_name=cache_parameter_group_name,
            cache_subnet_group_name=cache_subnet_group_name,
            cache_security_group_names=cache_security_group_names,
            security_group_ids=security_group_ids,
            tags=tags,
            snapshot_arns=snapshot_arns,
            snapshot_name=snapshot_name,
            preferred_maintenance_window=preferred_maintenance_window,
            port=port,
            notification_topic_arn=notification_topic_arn,
            auto_minor_version_upgrade=auto_minor_version_upgrade,
            snapshot_retention_limit=snapshot_retention_limit,
            snapshot_window=snapshot_window,
            auth_token=auth_token,
            outpost_mode=outpost_mode,
            preferred_outpost_arn=preferred_outpost_arn,
            preferred_outpost_arns=preferred_outpost_arns,
            log_delivery_configurations=log_delivery_configurations,
            transit_encryption_enabled=transit_encryption_enabled,
            network_type=network_type,
            ip_discovery=ip_discovery,
            cache_node_ids_to_remove=cache_node_ids_to_remove,
            cache_node_ids_to_reboot=cache_node_ids_to_reboot,
        )

        if tags:
            self.tagging_service.tag_resource(cache_cluster.arn, tags)

        self.cache_clusters[cache_cluster_id] = cache_cluster
        return cache_cluster

    def describe_cache_clusters(
        self, cache_cluster_id: Optional[str] = None
    ) -> list[CacheCluster]:
        if cache_cluster_id:
            if cache_cluster_id in self.cache_clusters:
                cache_cluster = self.cache_clusters[cache_cluster_id]
                return [cache_cluster]
            else:
                raise CacheClusterNotFound(cache_cluster_id)
        return list(self.cache_clusters.values())

    def delete_cache_cluster(self, cache_cluster_id: str) -> CacheCluster:
        if cache_cluster_id:
            if cache_cluster_id in self.cache_clusters:
                cache_cluster = self.cache_clusters[cache_cluster_id]
                cache_cluster.cache_cluster_status = "deleting"
                return cache_cluster
        raise CacheClusterNotFound(cache_cluster_id)

    def create_cache_subnet_group(
        self,
        cache_subnet_group_name: str,
        cache_subnet_group_description: str,
        subnet_ids: list[str],
        tags: Optional[list[dict[str, str]]],
    ) -> CacheSubnetGroup:
        if cache_subnet_group_name in self.cache_subnet_groups:
            raise CacheSubnetGroupAlreadyExists(cache_subnet_group_name)

        cache_subnet_group = CacheSubnetGroup(
            account_id=self.account_id,
            region_name=self.region_name,
            cache_subnet_group_name=cache_subnet_group_name,
            cache_subnet_group_description=cache_subnet_group_description,
            subnet_ids=subnet_ids,
            tags=tags,
        )

        if tags:
            self.tagging_service.tag_resource(cache_subnet_group.arn, tags)

        self.cache_subnet_groups[cache_subnet_group_name] = cache_subnet_group
        return cache_subnet_group

    def describe_cache_subnet_groups(
        self,
        cache_subnet_group_name: Optional[str] = None,
    ) -> list[CacheSubnetGroup]:
        if cache_subnet_group_name:
            if cache_subnet_group_name in self.cache_subnet_groups:
                cache_subnet_group = self.cache_subnet_groups[cache_subnet_group_name]
                return [cache_subnet_group]
            else:
                raise CacheSubnetGroupNotFound(cache_subnet_group_name)
        return list(self.cache_subnet_groups.values())

    def list_tags_for_resource(self, arn: str) -> dict[str, list[dict[str, str]]]:
        if self.arn_regex.match(arn):
            return self.tagging_service.list_tags_for_resource(arn)
        else:
            raise InvalidARNFault(arn)

    def add_tags_to_resource(self, arn: str, tags: list[dict[str, str]]) -> None:
        # Docs user "ResourceName" as input but the param is technically the ARN, will just use arn
        self.tagging_service.tag_resource(arn, tags)

    def remove_tags_from_resource(self, arn: str, tags: list[str]) -> None:
        # Docs user "ResourceName" as input but the param is technically the ARN, will just use arn
        self.tagging_service.untag_resource_using_names(arn, tags)

    def create_replication_group(
        self,
        replication_group_id: str,
        replication_group_description: str,
        global_replication_group_id: str,
        primary_cluster_id: str,
        automatic_failover_enabled: bool,
        multi_az_enabled: bool,
        num_cache_clusters: int,
        preferred_cache_cluster_azs: list[str],
        num_node_groups: int,
        replicas_per_node_group: int,
        node_group_configuration: list[dict[str, Any]],
        cache_node_type: str,
        engine: str,
        engine_version: str,
        cache_parameter_group_name: str,
        cache_subnet_group_name: str,
        cache_security_group_names: list[str],
        security_group_ids: list[str],
        tags: list[dict[str, str]],
        snapshot_arns: list[str],
        snapshot_name: str,
        preferred_maintenance_window: str,
        port: int,
        notification_topic_arn: str,
        auto_minor_version_upgrade: bool,
        snapshot_retention_limit: int,
        snapshot_window: str,
        auth_token: str,
        transit_encryption_enabled: bool,
        at_rest_encryption_enabled: bool,
        kms_key_id: str,
        user_group_ids: list[str],
        log_delivery_configurations: list[dict[str, Any]],
        data_tiering_enabled: bool,
        network_type: str,
        ip_discovery: str,
        transit_encryption_mode: str,
        cluster_mode: str,
        serverless_cache_snapshot_name: str,
    ) -> ReplicationGroup:
        if replication_group_id in self.replication_groups:
            raise ReplicationGroupAlreadyExists(replication_group_id)
        replication_group = ReplicationGroup(
            account_id=self.account_id,
            region_name=self.region_name,
            replication_group_id=replication_group_id,
            replication_group_description=replication_group_description,
            global_replication_group_id=global_replication_group_id,
            primary_cluster_id=primary_cluster_id,
            automatic_failover_enabled=automatic_failover_enabled,
            multi_az_enabled=multi_az_enabled,
            num_cache_clusters=num_cache_clusters,
            preferred_cache_cluster_azs=preferred_cache_cluster_azs,
            num_node_groups=num_node_groups,
            replicas_per_node_group=replicas_per_node_group,
            node_group_configuration=node_group_configuration,
            cache_node_type=cache_node_type,
            engine=engine,
            engine_version=engine_version,
            cache_parameter_group_name=cache_parameter_group_name,
            cache_subnet_group_name=cache_subnet_group_name,
            cache_security_group_names=cache_security_group_names,
            security_group_ids=security_group_ids,
            tags=tags,
            snapshot_arns=snapshot_arns,
            snapshot_name=snapshot_name,
            preferred_maintenance_window=preferred_maintenance_window,
            port=port,
            notification_topic_arn=notification_topic_arn,
            auto_minor_version_upgrade=auto_minor_version_upgrade,
            snapshot_retention_limit=snapshot_retention_limit,
            snapshot_window=snapshot_window,
            auth_token=auth_token,
            transit_encryption_enabled=transit_encryption_enabled,
            at_rest_encryption_enabled=at_rest_encryption_enabled,
            kms_key_id=kms_key_id,
            user_group_ids=user_group_ids,
            log_delivery_configurations=log_delivery_configurations,
            data_tiering_enabled=data_tiering_enabled,
            network_type=network_type,
            ip_discovery=ip_discovery,
            transit_encryption_mode=transit_encryption_mode,
            cluster_mode=cluster_mode,
            serverless_cache_snapshot_name=serverless_cache_snapshot_name,
        )

        if tags:
            self.tagging_service.tag_resource(replication_group.arn, tags)

        self.replication_groups[replication_group_id] = replication_group
        return replication_group

    def describe_replication_groups(
        self,
        replication_group_id: Optional[str] = None,
    ) -> list[ReplicationGroup]:
        if replication_group_id:
            if replication_group_id in self.replication_groups:
                replication_group = self.replication_groups[replication_group_id]
                return [replication_group]
            else:
                raise ReplicationGroupNotFound(replication_group_id)
        return list(self.replication_groups.values())

    def delete_replication_group(
        self, replication_group_id: str, retain_primary_cluster: Optional[bool]
    ) -> ReplicationGroup:
        if replication_group_id not in self.replication_groups:
            raise ReplicationGroupNotFound(replication_group_id)

        replication_group = self.replication_groups[replication_group_id]
        replication_group.status = "deleting"
        if not retain_primary_cluster:
            replication_group = self.replication_groups[replication_group_id]
            primary_id = replication_group.primary_cluster_id
            if primary_id and primary_id in replication_group.member_clusters:
                replication_group.member_clusters.remove(primary_id)
            replication_group.primary_cluster_id = ""
        return replication_group

    def create_snapshot(
        self,
        snapshot_name: str,
        replication_group_id: Optional[str],
        cache_cluster_id: Optional[str],
        kms_key_id: Optional[str],
        tags: Optional[list[dict[str, str]]],
    ) -> Snapshot:
        resource = None
        num_node_groups = None
        vpc_id = None

        if snapshot_name in self.snapshots:
            raise SnapshotAlreadyExists(snapshot_name)
        if replication_group_id and cache_cluster_id:
            raise InvalidParameterCombinationException(
                "Only one of CacheClusterId or ReplicationGroupId can be provided."
            )
        if replication_group_id:
            if replication_group_id not in self.replication_groups:
                raise ReplicationGroupNotFound(replication_group_id)
            resource = self.replication_groups[replication_group_id]
            num_node_groups = len(resource.node_groups)
        elif cache_cluster_id:
            if cache_cluster_id not in self.cache_clusters:
                raise CacheClusterNotFound(cache_cluster_id)
            resource = self.cache_clusters[cache_cluster_id]
            vpc_id = self._get_vpc_id_from_cluster(cache_cluster_id)
        else:
            raise InvalidParameterValueException(
                "One of CacheClusterId or ReplicationGroupId must be provided."
            )

        snapshot = Snapshot(
            account_id=self.account_id,
            region_name=self.region_name,
            automatic_failover=getattr(resource, "automatic_failover", None),
            auto_minor_version_upgrade=getattr(
                resource, "auto_minor_version_upgrade", None
            ),
            cache_cluster_create_time=getattr(
                resource, "cache_cluster_create_time", None
            ),
            cache_cluster_id=getattr(resource, "cache_cluster_id", None),
            cache_node_type=getattr(resource, "cache_node_type", None),
            cache_parameter_group_name=getattr(
                resource, "cache_parameter_group_name", None
            ),
            cache_subnet_group_name=getattr(resource, "cache_subnet_group_name", None),
            engine=getattr(resource, "engine", None),
            engine_version=getattr(resource, "engine_version", None),
            kms_key_id=kms_key_id,
            num_cache_nodes=getattr(resource, "num_cache_nodes", None),
            num_node_groups=num_node_groups,
            port=getattr(resource, "port", None),
            preferred_availability_zone=getattr(
                resource, "preferred_availability_zone", None
            ),
            preferred_maintenance_window=getattr(
                resource, "preferred_maintenance_window", None
            ),
            preferred_outpost_arn=getattr(resource, "preferred_outpost_arn", None),
            replication_group_description=getattr(resource, "description", None),
            replication_group_id=getattr(resource, "replication_group_id", None),
            snapshot_name=snapshot_name,
            snapshot_retention_limit=getattr(
                resource, "snapshot_retention_limit", None
            ),
            snapshot_status="available",
            snapshot_source="manual",
            snapshot_window=getattr(resource, "snapshot_window", None),
            topic_arn=getattr(resource, "notification_topic_arn", None),
            tags=tags or [],
            vpc_id=vpc_id,
        )

        if tags:
            self.tagging_service.tag_resource(snapshot.arn, tags)

        self.snapshots[snapshot_name] = snapshot
        return snapshot

    def describe_snapshots(
        self,
        replication_group_id: Optional[str] = None,
        cache_cluster_id: Optional[str] = None,
        snapshot_name: Optional[str] = None,
        snapshot_source: Optional[str] = None,
        marker: Optional[str] = None,
        max_records: Optional[int] = None,
        show_node_group_config: Optional[bool] = None,
    ) -> list[Snapshot]:
        if snapshot_name:
            try:
                return [self.snapshots[snapshot_name]]
            except KeyError:
                raise SnapshotNotFound(snapshot_name)

        if replication_group_id and cache_cluster_id:
            raise InvalidParameterCombinationException(
                "Only one of CacheClusterId or ReplicationGroupId can be provided."
            )

        if replication_group_id and replication_group_id not in self.replication_groups:
            raise ReplicationGroupNotFound(replication_group_id)

        if cache_cluster_id and cache_cluster_id not in self.cache_clusters:
            raise CacheClusterNotFound(cache_cluster_id)

        ref_id = replication_group_id or cache_cluster_id

        if snapshot_source or ref_id:
            return self._get_snapshots_by_param(ref_id=ref_id, source=snapshot_source)

        return list(self.snapshots.values())

    def delete_snapshot(self, snapshot_name: str) -> Snapshot:
        if snapshot_name in self.snapshots:
            snapshot = self.snapshots[snapshot_name]
            snapshot.snapshot_status = "deleting"

            self.snapshots.pop(snapshot_name)

            return snapshot
        raise SnapshotNotFound(snapshot_name)

    def describe_cache_engine_versions(
        self,
        engine: Optional[str] = None,
        engine_version: Optional[str] = None,
        cache_parameter_group_family: Optional[str] = None,
        default_only: bool = False,
    ) -> list[dict[str, Any]]:
        versions = [
            {
                "Engine": "redis",
                "EngineVersion": "7.1.0",
                "CacheParameterGroupFamily": "redis7",
                "CacheEngineDescription": "Redis",
                "CacheEngineVersionDescription": "redis version 7.1.0",
            },
            {
                "Engine": "redis",
                "EngineVersion": "7.0.7",
                "CacheParameterGroupFamily": "redis7.0",
                "CacheEngineDescription": "Redis",
                "CacheEngineVersionDescription": "redis version 7.0.7",
            },
            {
                "Engine": "redis",
                "EngineVersion": "6.2.6",
                "CacheParameterGroupFamily": "redis6.x",
                "CacheEngineDescription": "Redis",
                "CacheEngineVersionDescription": "redis version 6.2.6",
            },
            {
                "Engine": "memcached",
                "EngineVersion": "1.6.22",
                "CacheParameterGroupFamily": "memcached1.6",
                "CacheEngineDescription": "memcached",
                "CacheEngineVersionDescription": "memcached version 1.6.22",
            },
        ]
        if engine:
            versions = [v for v in versions if v["Engine"] == engine]
        if engine_version:
            versions = [v for v in versions if v["EngineVersion"] == engine_version]
        if cache_parameter_group_family:
            versions = [v for v in versions if v["CacheParameterGroupFamily"] == cache_parameter_group_family]
        if default_only:
            versions = versions[:1] if versions else []
        return versions

    def describe_cache_parameter_groups(
        self,
        cache_parameter_group_name: Optional[str] = None,
    ) -> list[CacheParameterGroup]:
        # Include default groups + user-created groups
        defaults = self._default_parameter_groups()
        all_groups = defaults + list(self.cache_parameter_groups.values())
        if cache_parameter_group_name:
            matched = [g for g in all_groups if g.cache_parameter_group_name == cache_parameter_group_name]
            if not matched:
                raise CacheParameterGroupNotFound(cache_parameter_group_name)
            return matched
        return all_groups

    def _default_parameter_groups(self) -> list[CacheParameterGroup]:
        defaults_spec = [
            ("default.redis7", "redis7", "Default parameter group for redis7"),
            ("default.redis6.x", "redis6.x", "Default parameter group for redis6.x"),
            ("default.memcached1.6", "memcached1.6", "Default parameter group for memcached1.6"),
        ]
        result = []
        for name, family, desc in defaults_spec:
            pg = CacheParameterGroup(
                account_id=self.account_id,
                region=self.region_name,
                cache_parameter_group_name=name,
                cache_parameter_group_family=family,
                description=desc,
            )
            result.append(pg)
        return result

    def describe_cache_parameters(
        self,
        cache_parameter_group_name: str,
    ) -> list[dict[str, Any]]:
        # Return a minimal set of commonly used parameters
        params = [
            {
                "ParameterName": "maxmemory-policy",
                "ParameterValue": "volatile-lru",
                "Description": "Max memory policy",
                "Source": "system",
                "DataType": "string",
                "AllowedValues": "volatile-lru,allkeys-lru,volatile-lfu,allkeys-lfu,volatile-random,allkeys-random,volatile-ttl,noeviction",
                "IsModifiable": True,
                "MinimumEngineVersion": "6.0.0",
                "ChangeType": "immediate",
            },
            {
                "ParameterName": "activedefrag",
                "ParameterValue": "no",
                "Description": "Enabled active defragmentation",
                "Source": "system",
                "DataType": "string",
                "AllowedValues": "yes,no",
                "IsModifiable": True,
                "MinimumEngineVersion": "6.0.0",
                "ChangeType": "immediate",
            },
        ]
        return params

    def describe_events(
        self,
        source_identifier: Optional[str] = None,
        source_type: Optional[str] = None,
        duration: Optional[int] = None,
    ) -> list[dict[str, Any]]:
        # Return empty events list (no events generated in mock)
        return []

    def describe_serverless_caches(
        self,
        serverless_cache_name: Optional[str] = None,
    ) -> list[ServerlessCache]:
        if serverless_cache_name:
            if serverless_cache_name in self.serverless_caches:
                return [self.serverless_caches[serverless_cache_name]]
            raise ServerlessCacheNotFound(serverless_cache_name)
        return list(self.serverless_caches.values())

    def describe_service_updates(
        self,
        service_update_name: Optional[str] = None,
    ) -> list[dict[str, Any]]:
        # No service updates in mock
        return []

    def describe_update_actions(
        self,
        replication_group_ids: Optional[list[str]] = None,
        cache_cluster_ids: Optional[list[str]] = None,
        service_update_name: Optional[str] = None,
    ) -> list[dict[str, Any]]:
        # No update actions in mock
        return []

    def batch_apply_update_action(
        self,
        service_update_name: str,
        replication_group_ids: Optional[list[str]] = None,
        cache_cluster_ids: Optional[list[str]] = None,
    ) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
        processed: list[dict[str, Any]] = []
        unprocessed: list[dict[str, Any]] = []
        if replication_group_ids:
            for rg_id in replication_group_ids:
                if rg_id in self.replication_groups:
                    processed.append({
                        "ReplicationGroupId": rg_id,
                        "ServiceUpdateName": service_update_name,
                        "UpdateActionStatus": "waiting-to-start",
                    })
                else:
                    unprocessed.append({
                        "ReplicationGroupId": rg_id,
                        "ServiceUpdateName": service_update_name,
                        "ErrorType": "replication-group-not-found",
                        "ErrorMessage": f"Replication group {rg_id} not found",
                    })
        if cache_cluster_ids:
            for cc_id in cache_cluster_ids:
                if cc_id in self.cache_clusters:
                    processed.append({
                        "CacheClusterId": cc_id,
                        "ServiceUpdateName": service_update_name,
                        "UpdateActionStatus": "waiting-to-start",
                    })
                else:
                    unprocessed.append({
                        "CacheClusterId": cc_id,
                        "ServiceUpdateName": service_update_name,
                        "ErrorType": "cache-cluster-not-found",
                        "ErrorMessage": f"Cache cluster {cc_id} not found",
                    })
        return processed, unprocessed

    def batch_stop_update_action(
        self,
        service_update_name: str,
        replication_group_ids: Optional[list[str]] = None,
        cache_cluster_ids: Optional[list[str]] = None,
    ) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
        processed: list[dict[str, Any]] = []
        unprocessed: list[dict[str, Any]] = []
        if replication_group_ids:
            for rg_id in replication_group_ids:
                if rg_id in self.replication_groups:
                    processed.append({
                        "ReplicationGroupId": rg_id,
                        "ServiceUpdateName": service_update_name,
                        "UpdateActionStatus": "stopped",
                    })
                else:
                    unprocessed.append({
                        "ReplicationGroupId": rg_id,
                        "ServiceUpdateName": service_update_name,
                        "ErrorType": "replication-group-not-found",
                        "ErrorMessage": f"Replication group {rg_id} not found",
                    })
        if cache_cluster_ids:
            for cc_id in cache_cluster_ids:
                if cc_id in self.cache_clusters:
                    processed.append({
                        "CacheClusterId": cc_id,
                        "ServiceUpdateName": service_update_name,
                        "UpdateActionStatus": "stopped",
                    })
                else:
                    unprocessed.append({
                        "CacheClusterId": cc_id,
                        "ServiceUpdateName": service_update_name,
                        "ErrorType": "cache-cluster-not-found",
                        "ErrorMessage": f"Cache cluster {cc_id} not found",
                    })
        return processed, unprocessed

    def delete_cache_subnet_group(
        self,
        cache_subnet_group_name: str,
    ) -> None:
        if cache_subnet_group_name not in self.cache_subnet_groups:
            raise CacheSubnetGroupNotFound(cache_subnet_group_name)
        del self.cache_subnet_groups[cache_subnet_group_name]

    def describe_user_groups(
        self,
        user_group_id: Optional[str] = None,
    ) -> list[UserGroup]:
        if user_group_id:
            if user_group_id in self.user_groups:
                return [self.user_groups[user_group_id]]
            raise UserGroupNotFound(user_group_id)
        return list(self.user_groups.values())

    # --- CacheParameterGroup operations ---

    def create_cache_parameter_group(
        self,
        cache_parameter_group_name: str,
        cache_parameter_group_family: str,
        description: str,
        tags: Optional[list[dict[str, str]]] = None,
    ) -> CacheParameterGroup:
        if cache_parameter_group_name in self.cache_parameter_groups:
            raise CacheParameterGroupAlreadyExists(cache_parameter_group_name)
        # Also check if it collides with default group names
        for dg in self._default_parameter_groups():
            if dg.cache_parameter_group_name == cache_parameter_group_name:
                raise CacheParameterGroupAlreadyExists(cache_parameter_group_name)
        group = CacheParameterGroup(
            account_id=self.account_id,
            region=self.region_name,
            cache_parameter_group_name=cache_parameter_group_name,
            cache_parameter_group_family=cache_parameter_group_family,
            description=description,
            tags=tags,
        )
        if tags:
            self.tagging_service.tag_resource(group.arn, tags)
        self.cache_parameter_groups[cache_parameter_group_name] = group
        return group

    def delete_cache_parameter_group(
        self,
        cache_parameter_group_name: str,
    ) -> None:
        if cache_parameter_group_name not in self.cache_parameter_groups:
            raise CacheParameterGroupNotFound(cache_parameter_group_name)
        del self.cache_parameter_groups[cache_parameter_group_name]

    def modify_cache_parameter_group(
        self,
        cache_parameter_group_name: str,
        parameter_name_values: list[dict[str, str]],
    ) -> CacheParameterGroup:
        if cache_parameter_group_name not in self.cache_parameter_groups:
            raise CacheParameterGroupNotFound(cache_parameter_group_name)
        group = self.cache_parameter_groups[cache_parameter_group_name]
        for pnv in parameter_name_values:
            name = pnv.get("ParameterName", "")
            value = pnv.get("ParameterValue", "")
            if name:
                group.parameters[name] = value
        return group

    def reset_cache_parameter_group(
        self,
        cache_parameter_group_name: str,
        reset_all_parameters: bool,
        parameter_name_values: Optional[list[dict[str, str]]] = None,
    ) -> CacheParameterGroup:
        if cache_parameter_group_name not in self.cache_parameter_groups:
            raise CacheParameterGroupNotFound(cache_parameter_group_name)
        group = self.cache_parameter_groups[cache_parameter_group_name]
        if reset_all_parameters:
            group.parameters = {}
        elif parameter_name_values:
            for pnv in parameter_name_values:
                name = pnv.get("ParameterName", "")
                if name in group.parameters:
                    del group.parameters[name]
        return group

    # --- CacheSecurityGroup operations ---

    def create_cache_security_group(
        self,
        cache_security_group_name: str,
        description: str,
        tags: Optional[list[dict[str, str]]] = None,
    ) -> CacheSecurityGroup:
        if cache_security_group_name in self.cache_security_groups:
            raise CacheSecurityGroupAlreadyExists(cache_security_group_name)
        group = CacheSecurityGroup(
            account_id=self.account_id,
            region=self.region_name,
            cache_security_group_name=cache_security_group_name,
            description=description,
            tags=tags,
        )
        if tags:
            self.tagging_service.tag_resource(group.arn, tags)
        self.cache_security_groups[cache_security_group_name] = group
        return group

    def delete_cache_security_group(
        self,
        cache_security_group_name: str,
    ) -> None:
        if cache_security_group_name not in self.cache_security_groups:
            raise CacheSecurityGroupNotFound(cache_security_group_name)
        del self.cache_security_groups[cache_security_group_name]

    def describe_cache_security_groups(
        self,
        cache_security_group_name: Optional[str] = None,
    ) -> list[CacheSecurityGroup]:
        if cache_security_group_name:
            if cache_security_group_name in self.cache_security_groups:
                return [self.cache_security_groups[cache_security_group_name]]
            raise CacheSecurityGroupNotFound(cache_security_group_name)
        return list(self.cache_security_groups.values())

    def revoke_cache_security_group_ingress(
        self,
        cache_security_group_name: str,
        ec2_security_group_name: str,
        ec2_security_group_owner_id: str,
    ) -> CacheSecurityGroup:
        if cache_security_group_name not in self.cache_security_groups:
            raise CacheSecurityGroupNotFound(cache_security_group_name)
        group = self.cache_security_groups[cache_security_group_name]
        group.ec2_security_groups = [
            sg for sg in group.ec2_security_groups
            if not (sg.get("EC2SecurityGroupName") == ec2_security_group_name
                    and sg.get("EC2SecurityGroupOwnerId") == ec2_security_group_owner_id)
        ]
        return group

    # --- UserGroup operations ---

    def create_user_group(
        self,
        user_group_id: str,
        engine: str,
        user_ids: Optional[list[str]] = None,
        tags: Optional[list[dict[str, str]]] = None,
    ) -> UserGroup:
        if user_group_id in self.user_groups:
            raise UserGroupAlreadyExists(user_group_id)
        # Validate user IDs exist
        all_user_ids = list(user_ids) if user_ids else ["default"]
        for uid in all_user_ids:
            if uid not in self.users:
                raise UserNotFound(uid)
        group = UserGroup(
            account_id=self.account_id,
            region=self.region_name,
            user_group_id=user_group_id,
            engine=engine,
            user_ids=all_user_ids,
            tags=tags,
        )
        if tags:
            self.tagging_service.tag_resource(group.arn, tags)
        # Update user records
        for uid in all_user_ids:
            if uid in self.users:
                self.users[uid].user_group_ids.append(user_group_id)
        self.user_groups[user_group_id] = group
        return group

    def delete_user_group(
        self,
        user_group_id: str,
    ) -> UserGroup:
        if user_group_id not in self.user_groups:
            raise UserGroupNotFound(user_group_id)
        group = self.user_groups[user_group_id]
        group.status = "deleting"
        # Remove group from users
        for uid in group.user_ids:
            if uid in self.users and user_group_id in self.users[uid].user_group_ids:
                self.users[uid].user_group_ids.remove(user_group_id)
        del self.user_groups[user_group_id]
        return group

    def modify_user_group(
        self,
        user_group_id: str,
        user_ids_to_add: Optional[list[str]] = None,
        user_ids_to_remove: Optional[list[str]] = None,
    ) -> UserGroup:
        if user_group_id not in self.user_groups:
            raise UserGroupNotFound(user_group_id)
        group = self.user_groups[user_group_id]
        if user_ids_to_add:
            for uid in user_ids_to_add:
                if uid not in self.users:
                    raise UserNotFound(uid)
                if uid not in group.user_ids:
                    group.user_ids.append(uid)
                    self.users[uid].user_group_ids.append(user_group_id)
        if user_ids_to_remove:
            for uid in user_ids_to_remove:
                if uid in group.user_ids:
                    group.user_ids.remove(uid)
                    if uid in self.users and user_group_id in self.users[uid].user_group_ids:
                        self.users[uid].user_group_ids.remove(user_group_id)
        return group

    # --- ServerlessCache operations ---

    def create_serverless_cache(
        self,
        serverless_cache_name: str,
        engine: str,
        description: Optional[str] = None,
        major_engine_version: Optional[str] = None,
        cache_usage_limits: Optional[dict[str, Any]] = None,
        kms_key_id: Optional[str] = None,
        security_group_ids: Optional[list[str]] = None,
        snapshot_arns_to_restore: Optional[list[str]] = None,
        subnet_ids: Optional[list[str]] = None,
        daily_snapshot_time: Optional[str] = None,
        snapshot_retention_limit: Optional[int] = None,
        user_group_id: Optional[str] = None,
        tags: Optional[list[dict[str, str]]] = None,
    ) -> ServerlessCache:
        if serverless_cache_name in self.serverless_caches:
            raise ServerlessCacheAlreadyExists(serverless_cache_name)
        cache = ServerlessCache(
            account_id=self.account_id,
            region=self.region_name,
            serverless_cache_name=serverless_cache_name,
            engine=engine,
            description=description,
            major_engine_version=major_engine_version,
            cache_usage_limits=cache_usage_limits,
            kms_key_id=kms_key_id,
            security_group_ids=security_group_ids,
            snapshot_arns_to_restore=snapshot_arns_to_restore,
            subnet_ids=subnet_ids,
            daily_snapshot_time=daily_snapshot_time,
            snapshot_retention_limit=snapshot_retention_limit,
            user_group_id=user_group_id,
            tags=tags,
        )
        if tags:
            self.tagging_service.tag_resource(cache.arn, tags)
        self.serverless_caches[serverless_cache_name] = cache
        return cache

    def delete_serverless_cache(
        self,
        serverless_cache_name: str,
    ) -> ServerlessCache:
        if serverless_cache_name not in self.serverless_caches:
            raise ServerlessCacheNotFound(serverless_cache_name)
        cache = self.serverless_caches.pop(serverless_cache_name)
        cache.status = "deleting"
        return cache

    def modify_serverless_cache(
        self,
        serverless_cache_name: str,
        description: Optional[str] = None,
        cache_usage_limits: Optional[dict[str, Any]] = None,
        daily_snapshot_time: Optional[str] = None,
        snapshot_retention_limit: Optional[int] = None,
        security_group_ids: Optional[list[str]] = None,
        user_group_id: Optional[str] = None,
    ) -> ServerlessCache:
        if serverless_cache_name not in self.serverless_caches:
            raise ServerlessCacheNotFound(serverless_cache_name)
        cache = self.serverless_caches[serverless_cache_name]
        if description is not None:
            cache.description = description
        if cache_usage_limits is not None:
            cache.cache_usage_limits = cache_usage_limits
        if daily_snapshot_time is not None:
            cache.daily_snapshot_time = daily_snapshot_time
        if snapshot_retention_limit is not None:
            cache.snapshot_retention_limit = snapshot_retention_limit
        if security_group_ids is not None:
            cache.security_group_ids = security_group_ids
        if user_group_id is not None:
            cache.user_group_id = user_group_id
        return cache

    # --- ServerlessCacheSnapshot operations ---

    def create_serverless_cache_snapshot(
        self,
        serverless_cache_snapshot_name: str,
        serverless_cache_name: str,
        tags: Optional[list[dict[str, str]]] = None,
    ) -> ServerlessCacheSnapshot:
        if serverless_cache_name not in self.serverless_caches:
            raise ServerlessCacheNotFound(serverless_cache_name)
        if serverless_cache_snapshot_name in self.serverless_cache_snapshots:
            raise SnapshotAlreadyExists(serverless_cache_snapshot_name)
        sc = self.serverless_caches[serverless_cache_name]
        snapshot = ServerlessCacheSnapshot(
            account_id=self.account_id,
            region=self.region_name,
            serverless_cache_snapshot_name=serverless_cache_snapshot_name,
            serverless_cache_name=serverless_cache_name,
            serverless_cache=sc,
            tags=tags,
        )
        if tags:
            self.tagging_service.tag_resource(snapshot.arn, tags)
        self.serverless_cache_snapshots[serverless_cache_snapshot_name] = snapshot
        return snapshot

    def delete_serverless_cache_snapshot(
        self,
        serverless_cache_snapshot_name: str,
    ) -> ServerlessCacheSnapshot:
        if serverless_cache_snapshot_name not in self.serverless_cache_snapshots:
            raise SnapshotNotFound(serverless_cache_snapshot_name)
        snapshot = self.serverless_cache_snapshots.pop(serverless_cache_snapshot_name)
        snapshot.status = "deleting"
        return snapshot

    def describe_serverless_cache_snapshots(
        self,
        serverless_cache_name: Optional[str] = None,
        serverless_cache_snapshot_name: Optional[str] = None,
    ) -> list[ServerlessCacheSnapshot]:
        snapshots = list(self.serverless_cache_snapshots.values())
        if serverless_cache_snapshot_name:
            snapshots = [s for s in snapshots if s.serverless_cache_snapshot_name == serverless_cache_snapshot_name]
            if not snapshots:
                raise SnapshotNotFound(serverless_cache_snapshot_name)
        if serverless_cache_name:
            snapshots = [s for s in snapshots if s.serverless_cache_name == serverless_cache_name]
        return snapshots

    # --- GlobalReplicationGroup operations ---

    def create_global_replication_group(
        self,
        global_replication_group_id_suffix: str,
        primary_replication_group_id: str,
        global_replication_group_description: Optional[str] = None,
    ) -> GlobalReplicationGroup:
        full_id = f"lstgl-{global_replication_group_id_suffix}"
        if full_id in self.global_replication_groups:
            raise GlobalReplicationGroupAlreadyExists(full_id)
        if primary_replication_group_id not in self.replication_groups:
            raise ReplicationGroupNotFound(primary_replication_group_id)
        grg = GlobalReplicationGroup(
            account_id=self.account_id,
            region=self.region_name,
            global_replication_group_id_suffix=global_replication_group_id_suffix,
            primary_replication_group_id=primary_replication_group_id,
            global_replication_group_description=global_replication_group_description,
        )
        # Copy engine details from the primary replication group
        primary = self.replication_groups[primary_replication_group_id]
        grg.engine = primary.engine
        grg.cache_node_type = primary.cache_node_type
        grg.at_rest_encryption_enabled = primary.at_rest_encryption_enabled
        grg.transit_encryption_enabled = primary.transit_encryption_enabled
        grg.auth_token_enabled = primary.auth_token_enabled
        grg.cluster_enabled = primary.cluster_enabled
        self.global_replication_groups[full_id] = grg
        return grg

    def delete_global_replication_group(
        self,
        global_replication_group_id: str,
        retain_primary_replication_group: bool,
    ) -> GlobalReplicationGroup:
        if global_replication_group_id not in self.global_replication_groups:
            raise GlobalReplicationGroupNotFound(global_replication_group_id)
        grg = self.global_replication_groups.pop(global_replication_group_id)
        grg.status = "deleting"
        return grg

    def describe_global_replication_groups(
        self,
        global_replication_group_id: Optional[str] = None,
    ) -> list[GlobalReplicationGroup]:
        if global_replication_group_id:
            if global_replication_group_id in self.global_replication_groups:
                return [self.global_replication_groups[global_replication_group_id]]
            raise GlobalReplicationGroupNotFound(global_replication_group_id)
        return list(self.global_replication_groups.values())

    def modify_global_replication_group(
        self,
        global_replication_group_id: str,
        apply_immediately: bool,
        cache_node_type: Optional[str] = None,
        engine_version: Optional[str] = None,
        global_replication_group_description: Optional[str] = None,
        automatic_failover_enabled: Optional[bool] = None,
    ) -> GlobalReplicationGroup:
        if global_replication_group_id not in self.global_replication_groups:
            raise GlobalReplicationGroupNotFound(global_replication_group_id)
        grg = self.global_replication_groups[global_replication_group_id]
        if cache_node_type is not None:
            grg.cache_node_type = cache_node_type
        if engine_version is not None:
            grg.engine_version = engine_version
        if global_replication_group_description is not None:
            grg.global_replication_group_description = global_replication_group_description
        return grg

    # --- ModifyUser ---

    def modify_user(
        self,
        user_id: str,
        access_string: Optional[str] = None,
        append_access_string: Optional[str] = None,
        passwords: Optional[list[str]] = None,
        no_password_required: Optional[bool] = None,
        authentication_mode: Optional[dict[str, Any]] = None,
    ) -> User:
        if user_id not in self.users:
            raise UserNotFound(user_id)
        user = self.users[user_id]
        if access_string is not None:
            user.access_string = access_string
        if append_access_string is not None:
            user.access_string = f"{user.access_string} {append_access_string}"
        if passwords is not None:
            user.passwords = passwords
            if passwords:
                user.authentication_type = "password"
                user.no_password_required = False
        if no_password_required is not None:
            user.no_password_required = no_password_required
            if no_password_required:
                user.authentication_type = "no-password-required"
        if authentication_mode:
            auth_type = authentication_mode.get("Type")
            if auth_type:
                user.authentication_type = auth_type
            auth_passwords = authentication_mode.get("Passwords", [])
            if auth_passwords:
                user.passwords = auth_passwords
        return user

    # --- ModifyCacheSubnetGroup ---

    def modify_cache_subnet_group(
        self,
        cache_subnet_group_name: str,
        cache_subnet_group_description: Optional[str] = None,
        subnet_ids: Optional[list[str]] = None,
    ) -> CacheSubnetGroup:
        if cache_subnet_group_name not in self.cache_subnet_groups:
            raise CacheSubnetGroupNotFound(cache_subnet_group_name)
        group = self.cache_subnet_groups[cache_subnet_group_name]
        if cache_subnet_group_description is not None:
            group.cache_subnet_group_description = cache_subnet_group_description
        if subnet_ids is not None:
            group.subnet_ids = subnet_ids
        return group

    # --- ModifyCacheCluster ---

    def modify_cache_cluster(
        self,
        cache_cluster_id: str,
        num_cache_nodes: Optional[int] = None,
        cache_node_ids_to_remove: Optional[list[str]] = None,
        cache_parameter_group_name: Optional[str] = None,
        cache_security_group_names: Optional[list[str]] = None,
        security_group_ids: Optional[list[str]] = None,
        preferred_maintenance_window: Optional[str] = None,
        notification_topic_arn: Optional[str] = None,
        engine_version: Optional[str] = None,
        auto_minor_version_upgrade: Optional[bool] = None,
        snapshot_retention_limit: Optional[int] = None,
        snapshot_window: Optional[str] = None,
        cache_node_type: Optional[str] = None,
        auth_token: Optional[str] = None,
        log_delivery_configurations: Optional[list[dict[str, Any]]] = None,
    ) -> CacheCluster:
        if cache_cluster_id not in self.cache_clusters:
            raise CacheClusterNotFound(cache_cluster_id)
        cluster = self.cache_clusters[cache_cluster_id]
        if num_cache_nodes is not None:
            cluster.num_cache_nodes = num_cache_nodes
        if cache_node_ids_to_remove is not None:
            cluster.cache_node_ids_to_remove = cache_node_ids_to_remove
        if cache_parameter_group_name is not None:
            cluster.cache_parameter_group_name = cache_parameter_group_name
        if cache_security_group_names is not None:
            cluster.cache_security_group_names = cache_security_group_names
        if security_group_ids is not None:
            cluster.security_group_ids = security_group_ids
        if preferred_maintenance_window is not None:
            cluster.preferred_maintenance_window = preferred_maintenance_window
        if notification_topic_arn is not None:
            cluster.notification_topic_arn = notification_topic_arn
        if engine_version is not None:
            cluster.engine_version = engine_version
        if auto_minor_version_upgrade is not None:
            cluster.auto_minor_version_upgrade = auto_minor_version_upgrade
        if snapshot_retention_limit is not None:
            cluster.snapshot_retention_limit = snapshot_retention_limit
        if snapshot_window is not None:
            cluster.snapshot_window = snapshot_window
        if cache_node_type is not None:
            cluster.cache_node_type = cache_node_type
        if auth_token is not None:
            cluster.auth_token = auth_token
            cluster.auth_token_enabled = True
        if log_delivery_configurations is not None:
            cluster.log_delivery_configurations = log_delivery_configurations
        return cluster

    # --- ModifyReplicationGroup ---

    def modify_replication_group(
        self,
        replication_group_id: str,
        replication_group_description: Optional[str] = None,
        primary_cluster_id: Optional[str] = None,
        snapshotting_cluster_id: Optional[str] = None,
        automatic_failover_enabled: Optional[bool] = None,
        multi_az_enabled: Optional[bool] = None,
        cache_node_type: Optional[str] = None,
        engine_version: Optional[str] = None,
        cache_parameter_group_name: Optional[str] = None,
        cache_security_group_names: Optional[list[str]] = None,
        security_group_ids: Optional[list[str]] = None,
        preferred_maintenance_window: Optional[str] = None,
        notification_topic_arn: Optional[str] = None,
        snapshot_retention_limit: Optional[int] = None,
        snapshot_window: Optional[str] = None,
        log_delivery_configurations: Optional[list[dict[str, Any]]] = None,
        auth_token: Optional[str] = None,
        transit_encryption_enabled: Optional[bool] = None,
        transit_encryption_mode: Optional[str] = None,
        user_group_ids_to_add: Optional[list[str]] = None,
        user_group_ids_to_remove: Optional[list[str]] = None,
    ) -> ReplicationGroup:
        if replication_group_id not in self.replication_groups:
            raise ReplicationGroupNotFound(replication_group_id)
        rg = self.replication_groups[replication_group_id]
        if replication_group_description is not None:
            rg.description = replication_group_description
        if primary_cluster_id is not None:
            rg.primary_cluster_id = primary_cluster_id
        if snapshotting_cluster_id is not None:
            rg.snapshotting_cluster_id = snapshotting_cluster_id
        if automatic_failover_enabled is not None:
            rg.automatic_failover = "enabled" if automatic_failover_enabled else "disabled"
        if multi_az_enabled is not None:
            rg.multi_az = "enabled" if multi_az_enabled else "disabled"
        if cache_node_type is not None:
            rg.cache_node_type = cache_node_type
        if engine_version is not None:
            rg.engine_version = engine_version
        if cache_parameter_group_name is not None:
            rg.cache_parameter_group_name = cache_parameter_group_name
        if cache_security_group_names is not None:
            rg.cache_security_group_names = cache_security_group_names
        if security_group_ids is not None:
            rg.security_group_ids = security_group_ids
        if preferred_maintenance_window is not None:
            rg.preferred_maintenance_window = preferred_maintenance_window
        if notification_topic_arn is not None:
            rg.notification_topic_arn = notification_topic_arn
        if snapshot_retention_limit is not None:
            rg.snapshot_retention_limit = snapshot_retention_limit
        if snapshot_window is not None:
            rg.snapshot_window = snapshot_window
        if log_delivery_configurations is not None:
            rg.log_delivery_configurations = rg._get_log_delivery_configurations(log_delivery_configurations)
        if auth_token is not None:
            rg.auth_token_enabled = bool(auth_token)
        if transit_encryption_enabled is not None:
            rg.transit_encryption_enabled = transit_encryption_enabled
        if transit_encryption_mode is not None:
            rg.transit_encryption_mode = transit_encryption_mode
        if user_group_ids_to_add:
            for ugid in user_group_ids_to_add:
                if ugid not in rg.user_group_ids:
                    rg.user_group_ids.append(ugid)
        if user_group_ids_to_remove:
            for ugid in user_group_ids_to_remove:
                if ugid in rg.user_group_ids:
                    rg.user_group_ids.remove(ugid)
        return rg

    # --- CopySnapshot ---

    def copy_snapshot(
        self,
        source_snapshot_name: str,
        target_snapshot_name: str,
        target_bucket: Optional[str] = None,
        kms_key_id: Optional[str] = None,
        tags: Optional[list[dict[str, str]]] = None,
    ) -> Snapshot:
        if source_snapshot_name not in self.snapshots:
            raise SnapshotNotFound(source_snapshot_name)
        if target_snapshot_name in self.snapshots:
            raise SnapshotAlreadyExists(target_snapshot_name)
        source = self.snapshots[source_snapshot_name]
        new_snapshot = Snapshot(
            account_id=self.account_id,
            region_name=self.region_name,
            automatic_failover=source.automatic_failover,
            auto_minor_version_upgrade=source.auto_minor_version_upgrade,
            cache_cluster_create_time=source.cache_cluster_create_time,
            cache_cluster_id=source.cache_cluster_id,
            cache_node_type=source.cache_node_type,
            cache_parameter_group_name=source.cache_parameter_group_name,
            cache_subnet_group_name=source.cache_subnet_group_name,
            engine=source.engine,
            engine_version=source.engine_version,
            kms_key_id=kms_key_id or source.kms_key_id,
            num_cache_nodes=source.num_cache_nodes,
            num_node_groups=source.num_node_groups,
            port=source.port,
            preferred_availability_zone=source.preferred_availability_zone,
            preferred_maintenance_window=source.preferred_maintenance_window,
            preferred_outpost_arn=source.preferred_outpost_arn,
            replication_group_description=source.replication_group_description,
            replication_group_id=source.replication_group_id,
            snapshot_name=target_snapshot_name,
            snapshot_retention_limit=source.snapshot_retention_limit,
            snapshot_source="manual",
            snapshot_status="available",
            snapshot_window=source.snapshot_window,
            topic_arn=source.topic_arn,
            tags=tags or [],
            vpc_id=source.vpc_id,
        )
        if tags:
            self.tagging_service.tag_resource(new_snapshot.arn, tags)
        self.snapshots[target_snapshot_name] = new_snapshot
        return new_snapshot


    def describe_cache_engine_versions(
        self,
        engine: Optional[str] = None,
        engine_version: Optional[str] = None,
        cache_parameter_group_family: Optional[str] = None,
        default_only: bool = False,
    ) -> list[dict[str, Any]]:
        versions = [
            {
                "Engine": "redis",
                "EngineVersion": "7.1.0",
                "CacheParameterGroupFamily": "redis7",
                "CacheEngineDescription": "Redis",
                "CacheEngineVersionDescription": "redis version 7.1.0",
            },
            {
                "Engine": "redis",
                "EngineVersion": "7.0.7",
                "CacheParameterGroupFamily": "redis7.0",
                "CacheEngineDescription": "Redis",
                "CacheEngineVersionDescription": "redis version 7.0.7",
            },
            {
                "Engine": "redis",
                "EngineVersion": "6.2.6",
                "CacheParameterGroupFamily": "redis6.x",
                "CacheEngineDescription": "Redis",
                "CacheEngineVersionDescription": "redis version 6.2.6",
            },
            {
                "Engine": "memcached",
                "EngineVersion": "1.6.22",
                "CacheParameterGroupFamily": "memcached1.6",
                "CacheEngineDescription": "memcached",
                "CacheEngineVersionDescription": "memcached version 1.6.22",
            },
        ]
        if engine:
            versions = [v for v in versions if v["Engine"] == engine]
        if engine_version:
            versions = [v for v in versions if v["EngineVersion"] == engine_version]
        if cache_parameter_group_family:
            versions = [
                v
                for v in versions
                if v["CacheParameterGroupFamily"] == cache_parameter_group_family
            ]
        if default_only:
            versions = versions[:1] if versions else []
        return versions

    def describe_cache_parameter_groups(
        self,
        cache_parameter_group_name: Optional[str] = None,
    ) -> list[dict[str, Any]]:
        groups = [
            {
                "CacheParameterGroupName": "default.redis7",
                "CacheParameterGroupFamily": "redis7",
                "Description": "Default parameter group for redis7",
                "IsGlobal": False,
                "ARN": f"arn:{get_partition(self.region_name)}:elasticache:{self.region_name}:{self.account_id}:parametergroup:default.redis7",
            },
            {
                "CacheParameterGroupName": "default.redis6.x",
                "CacheParameterGroupFamily": "redis6.x",
                "Description": "Default parameter group for redis6.x",
                "IsGlobal": False,
                "ARN": f"arn:{get_partition(self.region_name)}:elasticache:{self.region_name}:{self.account_id}:parametergroup:default.redis6.x",
            },
            {
                "CacheParameterGroupName": "default.memcached1.6",
                "CacheParameterGroupFamily": "memcached1.6",
                "Description": "Default parameter group for memcached1.6",
                "IsGlobal": False,
                "ARN": f"arn:{get_partition(self.region_name)}:elasticache:{self.region_name}:{self.account_id}:parametergroup:default.memcached1.6",
            },
        ]
        if cache_parameter_group_name:
            groups = [
                g
                for g in groups
                if g["CacheParameterGroupName"] == cache_parameter_group_name
            ]
            if not groups:
                raise InvalidParameterValueException(
                    f"Cache parameter group {cache_parameter_group_name} not found."
                )
        return groups

    def describe_cache_parameters(
        self,
        cache_parameter_group_name: str,
    ) -> list[dict[str, Any]]:
        return [
            {
                "ParameterName": "maxmemory-policy",
                "ParameterValue": "volatile-lru",
                "Description": "Max memory policy",
                "Source": "system",
                "DataType": "string",
                "AllowedValues": "volatile-lru,allkeys-lru,volatile-lfu,allkeys-lfu,volatile-random,allkeys-random,volatile-ttl,noeviction",
                "IsModifiable": True,
                "MinimumEngineVersion": "6.0.0",
                "ChangeType": "immediate",
            },
            {
                "ParameterName": "activedefrag",
                "ParameterValue": "no",
                "Description": "Enabled active defragmentation",
                "Source": "system",
                "DataType": "string",
                "AllowedValues": "yes,no",
                "IsModifiable": True,
                "MinimumEngineVersion": "6.0.0",
                "ChangeType": "immediate",
            },
        ]

    def describe_events(
        self,
        source_identifier: Optional[str] = None,
        source_type: Optional[str] = None,
        duration: Optional[int] = None,
    ) -> list[dict[str, Any]]:
        return []

    def describe_serverless_caches(
        self,
        serverless_cache_name: Optional[str] = None,
    ) -> list[dict[str, Any]]:
        return []

    def describe_service_updates(
        self,
        service_update_name: Optional[str] = None,
    ) -> list[dict[str, Any]]:
        return []

    def describe_update_actions(
        self,
        replication_group_ids: Optional[list[str]] = None,
        cache_cluster_ids: Optional[list[str]] = None,
        service_update_name: Optional[str] = None,
    ) -> list[dict[str, Any]]:
        return []

    def describe_user_groups(
        self,
        user_group_id: Optional[str] = None,
    ) -> list[dict[str, Any]]:
        return []


elasticache_backends = BackendDict(ElastiCacheBackend, "elasticache")
