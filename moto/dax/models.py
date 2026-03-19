"""DAXBackend class with methods for supported APIs."""

from collections.abc import Iterable
from datetime import datetime, timezone
from typing import Any, Optional

from moto.core.base_backend import BackendDict, BaseBackend
from moto.core.common_models import BaseModel
from moto.core.utils import unix_time
from moto.moto_api._internal import mock_random as random
from moto.moto_api._internal.managed_state_model import ManagedState
from moto.utilities.paginator import paginate
from moto.utilities.tagging_service import TaggingService
from moto.utilities.utils import get_partition

from .exceptions import (
    ClusterNotFoundFault,
    NodeNotFoundFault,
    ParameterGroupAlreadyExistsFault,
    ParameterGroupNotFoundFault,
    SubnetGroupAlreadyExistsFault,
    SubnetGroupNotFoundFault,
)
from .utils import PAGINATION_MODEL


# Default DAX parameters (subset of what AWS returns)
DEFAULT_PARAMETERS = [
    {
        "ParameterName": "query-ttl-millis",
        "ParameterType": "DEFAULT",
        "ParameterValue": "300000",
        "NodeTypeSpecificValues": [],
        "Description": "Duration in milliseconds for queries to remain cached",
        "Source": "user",
        "DataType": "integer",
        "AllowedValues": "0-",
        "IsModifiable": "TRUE",
        "ChangeType": "IMMEDIATE",
    },
    {
        "ParameterName": "record-ttl-millis",
        "ParameterType": "DEFAULT",
        "ParameterValue": "300000",
        "NodeTypeSpecificValues": [],
        "Description": "Duration in milliseconds for records to remain valid in cache",
        "Source": "user",
        "DataType": "integer",
        "AllowedValues": "0-",
        "IsModifiable": "TRUE",
        "ChangeType": "IMMEDIATE",
    },
]


class DaxParameterGroup(BaseModel):
    def __init__(self, name: str = "default.dax1.0", description: str = "") -> None:
        self.name = name
        self.status = "in-sync"
        self.description = description
        # Each parameter group has its own copy of parameters
        self.parameters = [dict(p) for p in DEFAULT_PARAMETERS]

    def to_json(self) -> dict[str, Any]:
        return {
            "ParameterGroupName": self.name,
            "ParameterApplyStatus": self.status,
            "NodeIdsToReboot": [],
        }

    def to_describe_json(self) -> dict[str, Any]:
        return {
            "ParameterGroupName": self.name,
            "Description": self.description,
        }


class DaxNode:
    def __init__(self, endpoint: "DaxEndpoint", name: str, index: int):
        self.node_id = f"{name}-{chr(ord('a') + index)}"  # name-a, name-b, etc
        self.node_endpoint = {
            "Address": f"{self.node_id}.{endpoint.cluster_hex}.nodes.dax-clusters.{endpoint.region}.amazonaws.com",
            "Port": endpoint.port,
        }
        self.create_time = unix_time()
        # AWS spreads nodes across zones, i.e. three nodes will probably end up in us-east-1a, us-east-1b, us-east-1c
        # For simplicity, we'll 'deploy' everything to us-east-1a
        self.availability_zone = f"{endpoint.region}a"
        self.status = "available"
        self.parameter_status = "in-sync"

    def to_json(self) -> dict[str, Any]:
        return {
            "NodeId": self.node_id,
            "Endpoint": self.node_endpoint,
            "NodeCreateTime": self.create_time,
            "AvailabilityZone": self.availability_zone,
            "NodeStatus": self.status,
            "ParameterGroupStatus": self.parameter_status,
        }


class DaxEndpoint:
    def __init__(self, name: str, cluster_hex: str, region: str):
        self.name = name
        self.cluster_hex = cluster_hex
        self.region = region
        self.port = 8111

    def to_json(self, full: bool = False) -> dict[str, Any]:
        dct: dict[str, Any] = {"Port": self.port}
        if full:
            dct["Address"] = (
                f"{self.name}.{self.cluster_hex}.dax-clusters.{self.region}.amazonaws.com"
            )
            dct["URL"] = f"dax://{dct['Address']}"
        return dct


class DaxSubnetGroup(BaseModel):
    def __init__(
        self,
        name: str,
        description: str,
        subnet_ids: list[str],
        region: str,
    ) -> None:
        self.name = name
        self.description = description
        self.subnet_ids = subnet_ids
        self.vpc_id = f"vpc-{random.get_random_hex(8)}"
        self.region = region

    def to_json(self) -> dict[str, Any]:
        return {
            "SubnetGroupName": self.name,
            "Description": self.description,
            "VpcId": self.vpc_id,
            "Subnets": [
                {
                    "SubnetIdentifier": sid,
                    "SubnetAvailabilityZone": f"{self.region}a",
                }
                for sid in self.subnet_ids
            ],
        }


class DaxCluster(BaseModel, ManagedState):
    def __init__(
        self,
        account_id: str,
        region: str,
        name: str,
        description: str,
        node_type: str,
        replication_factor: int,
        iam_role_arn: str,
        sse_specification: dict[str, Any],
        encryption_type: str,
    ):
        # Configure ManagedState
        super().__init__(
            model_name="dax::cluster",
            transitions=[("creating", "available"), ("deleting", "deleted")],
        )
        # Set internal properties
        self.name = name
        self.description = description
        self.arn = (
            f"arn:{get_partition(region)}:dax:{region}:{account_id}:cache/{self.name}"
        )
        self.node_type = node_type
        self.replication_factor = replication_factor
        self.cluster_hex = random.get_random_hex(6)
        self.endpoint = DaxEndpoint(
            name=name, cluster_hex=self.cluster_hex, region=region
        )
        self.nodes = [self._create_new_node(i) for i in range(0, replication_factor)]
        self.preferred_maintenance_window = "thu:23:30-fri:00:30"
        self.subnet_group = "default"
        self.iam_role_arn = iam_role_arn
        self.parameter_group = DaxParameterGroup()
        self.security_groups = [
            {
                "SecurityGroupIdentifier": f"sg-{random.get_random_hex(10)}",
                "Status": "active",
            }
        ]
        self.sse_specification = sse_specification
        self.encryption_type = encryption_type
        self.notification_topic_arn: Optional[str] = None
        self.notification_topic_status: Optional[str] = None

    def _create_new_node(self, idx: int) -> DaxNode:
        return DaxNode(endpoint=self.endpoint, name=self.name, index=idx)

    def increase_replication_factor(self, new_replication_factor: int) -> None:
        for idx in range(self.replication_factor, new_replication_factor):
            self.nodes.append(self._create_new_node(idx))
        self.replication_factor = new_replication_factor

    def decrease_replication_factor(
        self, new_replication_factor: int, node_ids_to_remove: list[str]
    ) -> None:
        if node_ids_to_remove:
            self.nodes = [n for n in self.nodes if n.node_id not in node_ids_to_remove]
        else:
            self.nodes = self.nodes[0:new_replication_factor]
        self.replication_factor = new_replication_factor

    def delete(self) -> None:
        self.status = "deleting"

    def is_deleted(self) -> bool:
        return self.status == "deleted"

    def to_json(self) -> dict[str, Any]:
        use_full_repr = self.status == "available"
        dct = {
            "ClusterName": self.name,
            "Description": self.description,
            "ClusterArn": self.arn,
            "TotalNodes": self.replication_factor,
            "ActiveNodes": 0,
            "NodeType": self.node_type,
            "Status": self.status,
            "ClusterDiscoveryEndpoint": self.endpoint.to_json(use_full_repr),
            "PreferredMaintenanceWindow": self.preferred_maintenance_window,
            "SubnetGroup": self.subnet_group,
            "IamRoleArn": self.iam_role_arn,
            "ParameterGroup": self.parameter_group.to_json(),
            "SSEDescription": {
                "Status": "ENABLED"
                if self.sse_specification.get("Enabled") is True
                else "DISABLED"
            },
            "ClusterEndpointEncryptionType": self.encryption_type,
            "SecurityGroups": self.security_groups,
        }
        if use_full_repr:
            dct["Nodes"] = [n.to_json() for n in self.nodes]
        return dct


class DAXBackend(BaseBackend):
    def __init__(self, region_name: str, account_id: str):
        super().__init__(region_name, account_id)
        self._clusters: dict[str, DaxCluster] = {}
        self._tagger = TaggingService()
        self._parameter_groups: dict[str, DaxParameterGroup] = {
            "default.dax1.0": DaxParameterGroup(
                name="default.dax1.0",
                description="Default parameter group for dax1.0",
            ),
        }
        self._subnet_groups: dict[str, DaxSubnetGroup] = {}
        self._events: list[dict[str, Any]] = []

    @property
    def clusters(self) -> dict[str, DaxCluster]:
        self._clusters = {
            name: cluster
            for name, cluster in self._clusters.items()
            if cluster.status != "deleted"
        }
        return self._clusters

    def _add_event(
        self, source_name: str, source_type: str, message: str
    ) -> None:
        self._events.append(
            {
                "SourceName": source_name,
                "SourceType": source_type,
                "Message": message,
                "Date": datetime.now(timezone.utc).timestamp(),
            }
        )

    def create_cluster(
        self,
        cluster_name: str,
        node_type: str,
        description: str,
        replication_factor: int,
        iam_role_arn: str,
        tags: list[dict[str, str]],
        sse_specification: dict[str, Any],
        encryption_type: str,
    ) -> DaxCluster:
        """
        The following parameters are not yet processed:
        AvailabilityZones, SubnetGroupNames, SecurityGroups, PreferredMaintenanceWindow, NotificationTopicArn, ParameterGroupName
        """
        cluster = DaxCluster(
            account_id=self.account_id,
            region=self.region_name,
            name=cluster_name,
            description=description,
            node_type=node_type,
            replication_factor=replication_factor,
            iam_role_arn=iam_role_arn,
            sse_specification=sse_specification,
            encryption_type=encryption_type,
        )
        self.clusters[cluster_name] = cluster
        self._tagger.tag_resource(cluster.arn, tags)
        self._add_event(cluster_name, "CLUSTER", f"Cluster {cluster_name} created.")
        return cluster

    def delete_cluster(self, cluster_name: str) -> DaxCluster:
        if cluster_name not in self.clusters:
            raise ClusterNotFoundFault()
        self.clusters[cluster_name].delete()
        self._add_event(cluster_name, "CLUSTER", f"Cluster {cluster_name} deleted.")
        return self.clusters[cluster_name]

    @paginate(PAGINATION_MODEL)
    def describe_clusters(self, cluster_names: Iterable[str]) -> list[DaxCluster]:
        clusters = self.clusters
        if not cluster_names:
            cluster_names = clusters.keys()

        for name in cluster_names:
            if name in self.clusters:
                self.clusters[name].advance()

        # Clusters may have been deleted while advancing the states
        clusters = self.clusters
        for name in cluster_names:
            if name not in self.clusters:
                raise ClusterNotFoundFault(name)
        return [cluster for name, cluster in clusters.items() if name in cluster_names]

    def update_cluster(
        self,
        cluster_name: str,
        description: Optional[str],
        preferred_maintenance_window: Optional[str],
        notification_topic_arn: Optional[str],
        notification_topic_status: Optional[str],
        parameter_group_name: Optional[str],
        security_group_ids: Optional[list[str]],
    ) -> DaxCluster:
        if cluster_name not in self.clusters:
            raise ClusterNotFoundFault()
        cluster = self.clusters[cluster_name]
        if description is not None:
            cluster.description = description
        if preferred_maintenance_window is not None:
            cluster.preferred_maintenance_window = preferred_maintenance_window
        if notification_topic_arn is not None:
            cluster.notification_topic_arn = notification_topic_arn
        if notification_topic_status is not None:
            cluster.notification_topic_status = notification_topic_status
        if parameter_group_name is not None:
            if parameter_group_name not in self._parameter_groups:
                raise ParameterGroupNotFoundFault(parameter_group_name)
            cluster.parameter_group = DaxParameterGroup(name=parameter_group_name)
        if security_group_ids is not None:
            cluster.security_groups = [
                {"SecurityGroupIdentifier": sg_id, "Status": "active"}
                for sg_id in security_group_ids
            ]
        self._add_event(
            cluster_name, "CLUSTER", f"Cluster {cluster_name} updated."
        )
        return cluster

    def reboot_node(self, cluster_name: str, node_id: str) -> DaxCluster:
        if cluster_name not in self.clusters:
            raise ClusterNotFoundFault()
        cluster = self.clusters[cluster_name]
        node_found = False
        for node in cluster.nodes:
            if node.node_id == node_id:
                node_found = True
                break
        if not node_found:
            raise NodeNotFoundFault(node_id)
        self._add_event(
            node_id, "NODE", f"Node {node_id} rebooted."
        )
        return cluster

    def list_tags(self, resource_name: str) -> dict[str, list[dict[str, str]]]:
        """
        Pagination is not yet implemented
        """
        # resource_name can be the name, or the full ARN
        name = resource_name.split("/")[-1]
        if name not in self.clusters:
            raise ClusterNotFoundFault()
        return self._tagger.list_tags_for_resource(self.clusters[name].arn)

    def tag_resource(
        self, resource_name: str, tags: list[dict[str, str]]
    ) -> list[dict[str, str]]:
        name = resource_name.split("/")[-1]
        if name not in self.clusters:
            raise ClusterNotFoundFault()
        self._tagger.tag_resource(self.clusters[name].arn, tags)
        return self._tagger.list_tags_for_resource(self.clusters[name].arn)["Tags"]

    def untag_resource(
        self, resource_name: str, tag_keys: list[str]
    ) -> list[dict[str, str]]:
        name = resource_name.split("/")[-1]
        if name not in self.clusters:
            raise ClusterNotFoundFault()
        self._tagger.untag_resource_using_names(self.clusters[name].arn, tag_keys)
        return self._tagger.list_tags_for_resource(self.clusters[name].arn)["Tags"]

    def increase_replication_factor(
        self, cluster_name: str, new_replication_factor: int
    ) -> DaxCluster:
        """
        The AvailabilityZones-parameter is not yet implemented
        """
        if cluster_name not in self.clusters:
            raise ClusterNotFoundFault()
        self.clusters[cluster_name].increase_replication_factor(new_replication_factor)
        return self.clusters[cluster_name]

    def decrease_replication_factor(
        self,
        cluster_name: str,
        new_replication_factor: int,
        node_ids_to_remove: list[str],
    ) -> DaxCluster:
        """
        The AvailabilityZones-parameter is not yet implemented
        """
        if cluster_name not in self.clusters:
            raise ClusterNotFoundFault()
        self.clusters[cluster_name].decrease_replication_factor(
            new_replication_factor, node_ids_to_remove
        )
        return self.clusters[cluster_name]

    # Parameter Group operations

    def create_parameter_group(
        self, parameter_group_name: str, description: str
    ) -> DaxParameterGroup:
        if parameter_group_name in self._parameter_groups:
            raise ParameterGroupAlreadyExistsFault(parameter_group_name)
        pg = DaxParameterGroup(name=parameter_group_name, description=description or "")
        self._parameter_groups[parameter_group_name] = pg
        self._add_event(
            parameter_group_name,
            "PARAMETER_GROUP",
            f"ParameterGroup {parameter_group_name} created.",
        )
        return pg

    def delete_parameter_group(self, parameter_group_name: str) -> str:
        if parameter_group_name not in self._parameter_groups:
            raise ParameterGroupNotFoundFault(parameter_group_name)
        del self._parameter_groups[parameter_group_name]
        return f"ParameterGroup {parameter_group_name} has been deleted."

    def describe_parameter_groups(
        self, parameter_group_names: list[str]
    ) -> list[DaxParameterGroup]:
        if not parameter_group_names:
            return list(self._parameter_groups.values())
        result = []
        for name in parameter_group_names:
            if name not in self._parameter_groups:
                raise ParameterGroupNotFoundFault(name)
            result.append(self._parameter_groups[name])
        return result

    def describe_parameters(
        self, parameter_group_name: str, source: Optional[str]
    ) -> list[dict[str, Any]]:
        if parameter_group_name not in self._parameter_groups:
            raise ParameterGroupNotFoundFault(parameter_group_name)
        pg = self._parameter_groups[parameter_group_name]
        params = pg.parameters
        if source:
            params = [p for p in params if p.get("Source") == source]
        return params

    def update_parameter_group(
        self,
        parameter_group_name: str,
        parameter_name_values: list[dict[str, str]],
    ) -> DaxParameterGroup:
        if parameter_group_name not in self._parameter_groups:
            raise ParameterGroupNotFoundFault(parameter_group_name)
        pg = self._parameter_groups[parameter_group_name]
        for pnv in parameter_name_values:
            pname = pnv.get("ParameterName", "")
            pvalue = pnv.get("ParameterValue", "")
            for param in pg.parameters:
                if param["ParameterName"] == pname:
                    param["ParameterValue"] = pvalue
                    break
        return pg

    def describe_default_parameters(self) -> list[dict[str, Any]]:
        return [dict(p) for p in DEFAULT_PARAMETERS]

    # Subnet Group operations

    def create_subnet_group(
        self,
        subnet_group_name: str,
        description: str,
        subnet_ids: list[str],
    ) -> DaxSubnetGroup:
        if subnet_group_name in self._subnet_groups:
            raise SubnetGroupAlreadyExistsFault(subnet_group_name)
        sg = DaxSubnetGroup(
            name=subnet_group_name,
            description=description or "",
            subnet_ids=subnet_ids,
            region=self.region_name,
        )
        self._subnet_groups[subnet_group_name] = sg
        self._add_event(
            subnet_group_name,
            "SUBNET_GROUP",
            f"SubnetGroup {subnet_group_name} created.",
        )
        return sg

    def delete_subnet_group(self, subnet_group_name: str) -> str:
        if subnet_group_name not in self._subnet_groups:
            raise SubnetGroupNotFoundFault(subnet_group_name)
        del self._subnet_groups[subnet_group_name]
        return f"SubnetGroup {subnet_group_name} has been deleted."

    def describe_subnet_groups(
        self, subnet_group_names: list[str]
    ) -> list[DaxSubnetGroup]:
        if not subnet_group_names:
            return list(self._subnet_groups.values())
        result = []
        for name in subnet_group_names:
            if name not in self._subnet_groups:
                raise SubnetGroupNotFoundFault(name)
            result.append(self._subnet_groups[name])
        return result

    def update_subnet_group(
        self,
        subnet_group_name: str,
        description: Optional[str],
        subnet_ids: Optional[list[str]],
    ) -> DaxSubnetGroup:
        if subnet_group_name not in self._subnet_groups:
            raise SubnetGroupNotFoundFault(subnet_group_name)
        sg = self._subnet_groups[subnet_group_name]
        if description is not None:
            sg.description = description
        if subnet_ids is not None:
            sg.subnet_ids = subnet_ids
        return sg

    # Events

    def describe_events(
        self,
        source_name: Optional[str],
        source_type: Optional[str],
    ) -> list[dict[str, Any]]:
        """Pagination and time filtering not yet implemented."""
        events = self._events
        if source_name:
            events = [e for e in events if e["SourceName"] == source_name]
        if source_type:
            events = [e for e in events if e["SourceType"] == source_type]
        return events



dax_backends = BackendDict(DAXBackend, "dax")
