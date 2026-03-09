"""KafkaBackend class with methods for supported APIs."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any, Optional

from moto.core.base_backend import BackendDict, BaseBackend
from moto.core.common_models import BaseModel
from moto.utilities.utils import get_partition

from ..utilities.tagging_service import TaggingService
from .exceptions import BadRequestException, ConflictException, NotFoundException

# Standard Kafka versions for ListKafkaVersions and GetCompatibleKafkaVersions
KAFKA_VERSIONS = [
    "1.1.1",
    "2.2.1",
    "2.3.1",
    "2.4.1",
    "2.4.1.1",
    "2.5.1",
    "2.6.0",
    "2.6.1",
    "2.6.2",
    "2.7.0",
    "2.7.1",
    "2.7.2",
    "2.8.0",
    "2.8.1",
    "2.8.2.tiered",
    "3.1.1",
    "3.2.0",
    "3.3.1",
    "3.3.2",
    "3.4.0",
    "3.5.1",
    "3.6.0",
]

# Compatible upgrade paths
COMPATIBLE_KAFKA_VERSIONS = {
    "1.1.1": ["2.2.1"],
    "2.2.1": ["2.3.1"],
    "2.3.1": ["2.4.1", "2.4.1.1"],
    "2.4.1": ["2.5.1"],
    "2.4.1.1": ["2.5.1"],
    "2.5.1": ["2.6.0", "2.6.1", "2.6.2"],
    "2.6.0": ["2.6.1", "2.6.2", "2.7.0"],
    "2.6.1": ["2.6.2", "2.7.0", "2.7.1"],
    "2.6.2": ["2.7.0", "2.7.1", "2.7.2"],
    "2.7.0": ["2.7.1", "2.7.2", "2.8.0"],
    "2.7.1": ["2.7.2", "2.8.0", "2.8.1"],
    "2.7.2": ["2.8.0", "2.8.1"],
    "2.8.0": ["2.8.1", "2.8.2.tiered", "3.1.1"],
    "2.8.1": ["2.8.2.tiered", "3.1.1", "3.2.0"],
    "2.8.2.tiered": ["3.1.1", "3.2.0"],
    "3.1.1": ["3.2.0", "3.3.1"],
    "3.2.0": ["3.3.1", "3.3.2"],
    "3.3.1": ["3.3.2", "3.4.0"],
    "3.3.2": ["3.4.0", "3.5.1"],
    "3.4.0": ["3.5.1", "3.6.0"],
    "3.5.1": ["3.6.0"],
    "3.6.0": [],
}


class FakeKafkaCluster(BaseModel):
    def __init__(
        self,
        cluster_name: str,
        account_id: str,
        region_name: str,
        cluster_type: str,
        tags: Optional[dict[str, str]] = None,
        broker_node_group_info: Optional[dict[str, Any]] = None,
        kafka_version: Optional[str] = None,
        number_of_broker_nodes: Optional[int] = None,
        configuration_info: Optional[dict[str, Any]] = None,
        serverless_config: Optional[dict[str, Any]] = None,
        encryption_info: Optional[dict[str, Any]] = None,
        enhanced_monitoring: str = "DEFAULT",
        open_monitoring: Optional[dict[str, Any]] = None,
        logging_info: Optional[dict[str, Any]] = None,
        storage_mode: str = "LOCAL",
        current_version: str = "1.0",
        client_authentication: Optional[dict[str, Any]] = None,
        state: str = "CREATING",
        active_operation_arn: Optional[str] = None,
        zookeeper_connect_string: Optional[str] = None,
        zookeeper_connect_string_tls: Optional[str] = None,
    ):
        # General attributes
        self.cluster_id = str(uuid.uuid4())
        self.cluster_name = cluster_name
        self.account_id = account_id
        self.region_name = region_name
        self.cluster_type = cluster_type
        self.tags = tags or {}
        self.state = state
        self.creation_time = datetime.now().isoformat()
        self.current_version = current_version
        self.active_operation_arn = active_operation_arn
        self.arn = self._generate_arn()

        # Attributes specific to PROVISIONED clusters
        self.broker_node_group_info = broker_node_group_info
        self.kafka_version = kafka_version
        self.number_of_broker_nodes = number_of_broker_nodes
        self.configuration_info = configuration_info
        self.encryption_info = encryption_info
        self.enhanced_monitoring = enhanced_monitoring
        self.open_monitoring = open_monitoring
        self.logging_info = logging_info
        self.storage_mode = storage_mode
        self.client_authentication = client_authentication
        self.zookeeper_connect_string = zookeeper_connect_string
        self.zookeeper_connect_string_tls = zookeeper_connect_string_tls
        self.connectivity_info: Optional[dict[str, Any]] = None

        # Attributes specific to SERVERLESS clusters
        self.serverless_config = serverless_config

        # SCRAM secrets
        self.scram_secrets: list[str] = []

        # Cluster policy
        self.cluster_policy: Optional[str] = None
        self.cluster_policy_version: str = "1"

        # Topics
        self.topics: dict[str, FakeTopic] = {}

        # VPC connections associated with this cluster
        self.client_vpc_connections: list[str] = []

    def _generate_arn(self) -> str:
        resource_type = (
            "cluster" if self.cluster_type == "PROVISIONED" else "serverless-cluster"
        )
        partition = get_partition(self.region_name)
        return f"arn:{partition}:kafka:{self.region_name}:{self.account_id}:{resource_type}/{self.cluster_id}"

    def _increment_version(self) -> str:
        """Increment the current version and return the new version string."""
        try:
            ver = int(self.current_version)
            self.current_version = str(ver + 1)
        except ValueError:
            self.current_version = "2"
        return self.current_version


class FakeConfiguration(BaseModel):
    def __init__(
        self,
        name: str,
        account_id: str,
        region_name: str,
        description: str,
        kafka_versions: list[str],
        server_properties: str,
    ):
        self.name = name
        self.account_id = account_id
        self.region_name = region_name
        self.description = description
        self.kafka_versions = kafka_versions
        self.state = "ACTIVE"
        self.creation_time = datetime.now().isoformat()
        partition = get_partition(region_name)
        self.arn = f"arn:{partition}:kafka:{region_name}:{account_id}:configuration/{name}/{str(uuid.uuid4())}"
        self.revisions: list[dict[str, Any]] = []
        self._add_revision(description, server_properties)

    def _add_revision(self, description: str, server_properties: str) -> dict[str, Any]:
        revision_number = len(self.revisions) + 1
        revision = {
            "creationTime": datetime.now().isoformat(),
            "description": description,
            "revision": revision_number,
            "serverProperties": server_properties,
        }
        self.revisions.append(revision)
        return revision

    @property
    def latest_revision(self) -> dict[str, Any]:
        return self.revisions[-1]


class FakeReplicator(BaseModel):
    def __init__(
        self,
        replicator_name: str,
        account_id: str,
        region_name: str,
        description: str,
        kafka_clusters: list[dict[str, Any]],
        replication_info_list: list[dict[str, Any]],
        service_execution_role_arn: str,
        tags: Optional[dict[str, str]] = None,
    ):
        self.replicator_name = replicator_name
        self.account_id = account_id
        self.region_name = region_name
        self.description = description
        self.kafka_clusters = kafka_clusters
        self.replication_info_list = replication_info_list
        self.service_execution_role_arn = service_execution_role_arn
        self.tags = tags or {}
        self.state = "RUNNING"
        self.creation_time = datetime.now().isoformat()
        self.current_version = "1"
        partition = get_partition(region_name)
        self.arn = f"arn:{partition}:kafka:{region_name}:{account_id}:replicator/{replicator_name}/{str(uuid.uuid4())}"


class FakeVpcConnection(BaseModel):
    def __init__(
        self,
        account_id: str,
        region_name: str,
        target_cluster_arn: str,
        authentication: str,
        vpc_id: str,
        client_subnets: list[str],
        security_groups: list[str],
        tags: Optional[dict[str, str]] = None,
    ):
        self.account_id = account_id
        self.region_name = region_name
        self.target_cluster_arn = target_cluster_arn
        self.authentication = authentication
        self.vpc_id = vpc_id
        self.client_subnets = client_subnets
        self.security_groups = security_groups
        self.tags = tags or {}
        self.state = "AVAILABLE"
        self.creation_time = datetime.now().isoformat()
        partition = get_partition(region_name)
        self.arn = f"arn:{partition}:kafka:{region_name}:{account_id}:vpc-connection/{str(uuid.uuid4())}"


class FakeClusterOperation(BaseModel):
    def __init__(
        self,
        cluster_arn: str,
        account_id: str,
        region_name: str,
        operation_type: str,
    ):
        self.cluster_arn = cluster_arn
        self.account_id = account_id
        self.region_name = region_name
        self.operation_type = operation_type
        self.creation_time = datetime.now().isoformat()
        self.end_time = datetime.now().isoformat()
        self.operation_state = "UPDATE_COMPLETE"
        partition = get_partition(region_name)
        self.arn = f"arn:{partition}:kafka:{region_name}:{account_id}:cluster-operation/{str(uuid.uuid4())}"

    def to_dict(self) -> dict[str, Any]:
        return {
            "clusterArn": self.cluster_arn,
            "clusterOperationArn": self.arn,
            "creationTime": self.creation_time,
            "endTime": self.end_time,
            "operationState": self.operation_state,
            "operationType": self.operation_type,
        }

    def to_dict_v2(self) -> dict[str, Any]:
        return {
            "clusterArn": self.cluster_arn,
            "clusterOperationArn": self.arn,
            "clusterType": "PROVISIONED",
            "startTime": self.creation_time,
            "endTime": self.end_time,
            "operationState": self.operation_state,
            "operationType": self.operation_type,
        }


class FakeTopic(BaseModel):
    def __init__(
        self,
        cluster_arn: str,
        account_id: str,
        region_name: str,
        topic_name: str,
        partition_count: int = 1,
        replication_factor: int = 1,
        configs: Optional[dict[str, str]] = None,
    ):
        self.cluster_arn = cluster_arn
        self.account_id = account_id
        self.region_name = region_name
        self.topic_name = topic_name
        self.partition_count = partition_count
        self.replication_factor = replication_factor
        self.configs = configs or {}
        self.status = "ACTIVE"
        partition = get_partition(region_name)
        cluster_id = cluster_arn.rsplit("/", 1)[-1] if "/" in cluster_arn else "unknown"
        self.arn = f"arn:{partition}:kafka:{region_name}:{account_id}:topic/{cluster_id}/{topic_name}"


class KafkaBackend(BaseBackend):
    """Implementation of Kafka APIs."""

    def __init__(self, region_name: str, account_id: str):
        super().__init__(region_name, account_id)
        self.clusters: dict[str, FakeKafkaCluster] = {}
        self.configurations: dict[str, FakeConfiguration] = {}
        self.replicators: dict[str, FakeReplicator] = {}
        self.vpc_connections: dict[str, FakeVpcConnection] = {}
        self.cluster_operations: dict[str, FakeClusterOperation] = {}
        self.tagger = TaggingService()

    def _get_cluster(self, cluster_arn: str) -> FakeKafkaCluster:
        if cluster_arn not in self.clusters:
            raise NotFoundException(
                f"The cluster with the Amazon Resource Name (ARN) {cluster_arn} was not found."
            )
        return self.clusters[cluster_arn]

    def _get_configuration(self, arn: str) -> FakeConfiguration:
        if arn not in self.configurations:
            raise NotFoundException(
                f"The configuration with the Amazon Resource Name (ARN) {arn} was not found."
            )
        return self.configurations[arn]

    def _create_operation(
        self, cluster_arn: str, operation_type: str
    ) -> FakeClusterOperation:
        operation = FakeClusterOperation(
            cluster_arn=cluster_arn,
            account_id=self.account_id,
            region_name=self.region_name,
            operation_type=operation_type,
        )
        self.cluster_operations[operation.arn] = operation
        return operation

    # ---- Cluster operations ----

    def create_cluster_v2(
        self,
        cluster_name: str,
        tags: Optional[dict[str, str]],
        provisioned: Optional[dict[str, Any]],
        serverless: Optional[dict[str, Any]],
    ) -> tuple[str, str, str, str]:
        if provisioned:
            cluster_type = "PROVISIONED"
            broker_node_group_info = provisioned.get("brokerNodeGroupInfo")
            kafka_version = provisioned.get("kafkaVersion", "default-kafka-version")
            number_of_broker_nodes = int(provisioned.get("numberOfBrokerNodes", 1))
            storage_mode = provisioned.get("storageMode", "LOCAL")
            serverless_config = None
        elif serverless:
            cluster_type = "SERVERLESS"
            broker_node_group_info = None
            kafka_version = None
            number_of_broker_nodes = None
            storage_mode = None
            serverless_config = serverless
        else:
            raise BadRequestException(
                "Either provisioned or serverless must be provided."
            )

        new_cluster = FakeKafkaCluster(
            cluster_name=cluster_name,
            account_id=self.account_id,
            region_name=self.region_name,
            cluster_type=cluster_type,
            broker_node_group_info=broker_node_group_info,
            kafka_version=kafka_version,
            number_of_broker_nodes=number_of_broker_nodes,
            serverless_config=serverless_config,
            tags=tags,
            state="CREATING",
            storage_mode=storage_mode if storage_mode else "LOCAL",
            current_version="1.0",
        )

        self.clusters[new_cluster.arn] = new_cluster

        if tags:
            self.tag_resource(new_cluster.arn, tags)

        return (
            new_cluster.arn,
            new_cluster.cluster_name,
            new_cluster.state,
            new_cluster.cluster_type,
        )

    def describe_cluster_v2(self, cluster_arn: str) -> dict[str, Any]:
        cluster = self._get_cluster(cluster_arn)

        cluster_info: dict[str, Any] = {
            "activeOperationArn": "arn:aws:kafka:region:account-id:operation/active-operation",
            "clusterArn": cluster.arn,
            "clusterName": cluster.cluster_name,
            "clusterType": cluster.cluster_type,
            "creationTime": cluster.creation_time,
            "currentVersion": cluster.current_version,
            "state": cluster.state,
            "stateInfo": {
                "code": "string",
                "message": "Cluster state details.",
            },
            "tags": self.list_tags_for_resource(cluster.arn),
        }

        if cluster.cluster_type == "PROVISIONED":
            cluster_info.update(
                {
                    "provisioned": {
                        "brokerNodeGroupInfo": cluster.broker_node_group_info or {},
                        "clientAuthentication": cluster.client_authentication or {},
                        "currentBrokerSoftwareInfo": {
                            "configurationArn": (cluster.configuration_info or {}).get(
                                "arn", "string"
                            ),
                            "configurationRevision": (
                                cluster.configuration_info or {}
                            ).get("revision", 1),
                            "kafkaVersion": cluster.kafka_version,
                        },
                        "encryptionInfo": cluster.encryption_info or {},
                        "enhancedMonitoring": cluster.enhanced_monitoring,
                        "openMonitoring": cluster.open_monitoring or {},
                        "loggingInfo": cluster.logging_info or {},
                        "numberOfBrokerNodes": cluster.number_of_broker_nodes or 0,
                        "zookeeperConnectString": cluster.zookeeper_connect_string
                        or "zookeeper.example.com:2181",
                        "zookeeperConnectStringTls": cluster.zookeeper_connect_string_tls
                        or "zookeeper.example.com:2181",
                        "storageMode": cluster.storage_mode,
                        "customerActionStatus": "NONE",
                    }
                }
            )

        elif cluster.cluster_type == "SERVERLESS":
            cluster_info.update(
                {
                    "serverless": {
                        "vpcConfigs": cluster.serverless_config.get("vpcConfigs", [])
                        if cluster.serverless_config
                        else [],
                        "clientAuthentication": cluster.serverless_config.get(
                            "clientAuthentication", {}
                        )
                        if cluster.serverless_config
                        else {},
                    }
                }
            )

        return cluster_info

    def list_clusters_v2(
        self,
        cluster_name_filter: Optional[str],
        cluster_type_filter: Optional[str],
        max_results: Optional[int],
        next_token: Optional[str],
    ) -> tuple[list[dict[str, Any]], Optional[str]]:
        cluster_info_list = []
        for cluster_arn in self.clusters:
            cluster_info = self.describe_cluster_v2(cluster_arn)
            cluster_info_list.append(cluster_info)

        return cluster_info_list, None

    def create_cluster(
        self,
        broker_node_group_info: dict[str, Any],
        client_authentication: Optional[dict[str, Any]],
        cluster_name: str,
        configuration_info: Optional[dict[str, Any]] = None,
        encryption_info: Optional[dict[str, Any]] = None,
        enhanced_monitoring: str = "DEFAULT",
        open_monitoring: Optional[dict[str, Any]] = None,
        kafka_version: str = "2.8.1",
        logging_info: Optional[dict[str, Any]] = None,
        number_of_broker_nodes: int = 1,
        tags: Optional[dict[str, str]] = None,
        storage_mode: str = "LOCAL",
    ) -> tuple[str, str, str]:
        new_cluster = FakeKafkaCluster(
            cluster_name=cluster_name,
            account_id=self.account_id,
            region_name=self.region_name,
            cluster_type="PROVISIONED",
            broker_node_group_info=broker_node_group_info,
            client_authentication=client_authentication,
            kafka_version=kafka_version,
            number_of_broker_nodes=number_of_broker_nodes,
            configuration_info=configuration_info,
            encryption_info=encryption_info,
            enhanced_monitoring=enhanced_monitoring,
            open_monitoring=open_monitoring,
            logging_info=logging_info,
            storage_mode=storage_mode,
        )

        self.clusters[new_cluster.arn] = new_cluster

        if tags:
            self.tag_resource(new_cluster.arn, tags)

        return new_cluster.arn, new_cluster.cluster_name, new_cluster.state

    def describe_cluster(self, cluster_arn: str) -> dict[str, Any]:
        cluster = self._get_cluster(cluster_arn)

        return {
            "activeOperationArn": "arn:aws:kafka:region:account-id:operation/active-operation",
            "brokerNodeGroupInfo": cluster.broker_node_group_info or {},
            "clientAuthentication": cluster.client_authentication or {},
            "clusterArn": cluster.arn,
            "clusterName": cluster.cluster_name,
            "creationTime": cluster.creation_time,
            "currentBrokerSoftwareInfo": {
                "configurationArn": (cluster.configuration_info or {}).get(
                    "arn", "string"
                ),
                "configurationRevision": (cluster.configuration_info or {}).get(
                    "revision", 1
                ),
                "kafkaVersion": cluster.kafka_version,
            },
            "currentVersion": cluster.current_version,
            "encryptionInfo": cluster.encryption_info or {},
            "enhancedMonitoring": cluster.enhanced_monitoring,
            "openMonitoring": cluster.open_monitoring or {},
            "loggingInfo": cluster.logging_info or {},
            "numberOfBrokerNodes": cluster.number_of_broker_nodes or 0,
            "state": cluster.state,
            "stateInfo": {
                "code": "string",
                "message": "Cluster state details.",
            },
            "tags": self.list_tags_for_resource(cluster.arn),
            "zookeeperConnectString": cluster.zookeeper_connect_string
            or "zookeeper.example.com:2181",
            "zookeeperConnectStringTls": cluster.zookeeper_connect_string_tls
            or "zookeeper.example.com:2181",
            "storageMode": cluster.storage_mode,
            "customerActionStatus": "NONE",
        }

    def list_clusters(
        self,
        cluster_name_filter: Optional[str],
        max_results: Optional[int],
        next_token: Optional[str],
    ) -> list[dict[str, Any]]:
        cluster_info_list = [
            {
                "clusterArn": cluster.arn,
                "clusterName": cluster.cluster_name,
                "state": cluster.state,
                "creationTime": cluster.creation_time,
                "clusterType": cluster.cluster_type,
            }
            for _cluster_arn, cluster in self.clusters.items()
        ]

        return cluster_info_list

    def delete_cluster(self, cluster_arn: str, current_version: str) -> tuple[str, str]:
        cluster = self._get_cluster(cluster_arn)
        self.clusters.pop(cluster_arn)
        return cluster_arn, cluster.state

    # ---- Configuration operations ----

    def create_configuration(
        self,
        name: str,
        description: str,
        kafka_versions: list[str],
        server_properties: str,
    ) -> dict[str, Any]:
        config = FakeConfiguration(
            name=name,
            account_id=self.account_id,
            region_name=self.region_name,
            description=description,
            kafka_versions=kafka_versions or [],
            server_properties=server_properties,
        )
        self.configurations[config.arn] = config
        return {
            "arn": config.arn,
            "creationTime": config.creation_time,
            "latestRevision": {
                "creationTime": config.latest_revision["creationTime"],
                "description": config.latest_revision["description"],
                "revision": config.latest_revision["revision"],
            },
            "name": config.name,
            "state": config.state,
        }

    def describe_configuration(self, arn: str) -> dict[str, Any]:
        config = self._get_configuration(arn)
        return {
            "arn": config.arn,
            "creationTime": config.creation_time,
            "description": config.description,
            "kafkaVersions": config.kafka_versions,
            "latestRevision": {
                "creationTime": config.latest_revision["creationTime"],
                "description": config.latest_revision["description"],
                "revision": config.latest_revision["revision"],
            },
            "name": config.name,
            "state": config.state,
        }

    def delete_configuration(self, arn: str) -> dict[str, Any]:
        config = self._get_configuration(arn)
        config.state = "DELETING"
        self.configurations.pop(arn)
        return {"arn": arn, "state": "DELETING"}

    def update_configuration(
        self,
        arn: str,
        description: str,
        server_properties: str,
    ) -> dict[str, Any]:
        config = self._get_configuration(arn)
        revision = config._add_revision(description or "", server_properties)
        return {
            "arn": config.arn,
            "latestRevision": {
                "creationTime": revision["creationTime"],
                "description": revision["description"],
                "revision": revision["revision"],
            },
        }

    def list_configurations(
        self,
        max_results: Optional[int],
        next_token: Optional[str],
    ) -> tuple[list[dict[str, Any]], Optional[str]]:
        configs = []
        for config in self.configurations.values():
            configs.append(
                {
                    "arn": config.arn,
                    "creationTime": config.creation_time,
                    "description": config.description,
                    "kafkaVersions": config.kafka_versions,
                    "latestRevision": {
                        "creationTime": config.latest_revision["creationTime"],
                        "description": config.latest_revision["description"],
                        "revision": config.latest_revision["revision"],
                    },
                    "name": config.name,
                    "state": config.state,
                }
            )
        return configs, None

    def list_configuration_revisions(
        self,
        arn: str,
        max_results: Optional[int],
        next_token: Optional[str],
    ) -> tuple[list[dict[str, Any]], Optional[str]]:
        config = self._get_configuration(arn)
        revisions = [
            {
                "creationTime": r["creationTime"],
                "description": r["description"],
                "revision": r["revision"],
            }
            for r in config.revisions
        ]
        return revisions, None

    def describe_configuration_revision(
        self, arn: str, revision: int
    ) -> dict[str, Any]:
        config = self._get_configuration(arn)
        for rev in config.revisions:
            if rev["revision"] == revision:
                return {
                    "arn": config.arn,
                    "creationTime": rev["creationTime"],
                    "description": rev["description"],
                    "revision": rev["revision"],
                    "serverProperties": rev["serverProperties"],
                }
        raise NotFoundException(
            f"Revision {revision} for configuration {arn} was not found."
        )

    # ---- Replicator operations ----

    def create_replicator(
        self,
        replicator_name: str,
        description: str,
        kafka_clusters: list[dict[str, Any]],
        replication_info_list: list[dict[str, Any]],
        service_execution_role_arn: str,
        tags: Optional[dict[str, str]] = None,
    ) -> dict[str, Any]:
        replicator = FakeReplicator(
            replicator_name=replicator_name,
            account_id=self.account_id,
            region_name=self.region_name,
            description=description,
            kafka_clusters=kafka_clusters,
            replication_info_list=replication_info_list,
            service_execution_role_arn=service_execution_role_arn,
            tags=tags,
        )
        self.replicators[replicator.arn] = replicator
        if tags:
            self.tag_resource(replicator.arn, tags)
        return {
            "replicatorArn": replicator.arn,
            "replicatorName": replicator.replicator_name,
            "replicatorState": replicator.state,
        }

    def describe_replicator(self, replicator_arn: str) -> dict[str, Any]:
        if replicator_arn not in self.replicators:
            raise NotFoundException(
                f"The replicator with the ARN {replicator_arn} was not found."
            )
        replicator = self.replicators[replicator_arn]
        return {
            "creationTime": replicator.creation_time,
            "currentVersion": replicator.current_version,
            "isReplicatorReference": False,
            "kafkaClusters": replicator.kafka_clusters,
            "replicationInfoList": replicator.replication_info_list,
            "replicatorArn": replicator.arn,
            "replicatorDescription": replicator.description,
            "replicatorName": replicator.replicator_name,
            "replicatorResourceArn": replicator.arn,
            "replicatorState": replicator.state,
            "serviceExecutionRoleArn": replicator.service_execution_role_arn,
            "stateInfo": {},
            "tags": self.list_tags_for_resource(replicator.arn),
        }

    def delete_replicator(
        self, replicator_arn: str, current_version: Optional[str]
    ) -> dict[str, Any]:
        if replicator_arn not in self.replicators:
            raise NotFoundException(
                f"The replicator with the ARN {replicator_arn} was not found."
            )
        self.replicators.pop(replicator_arn)
        return {
            "replicatorArn": replicator_arn,
            "replicatorState": "DELETING",
        }

    def list_replicators(
        self,
        max_results: Optional[int],
        next_token: Optional[str],
        replicator_name_filter: Optional[str],
    ) -> tuple[list[dict[str, Any]], Optional[str]]:
        replicators = []
        for replicator in self.replicators.values():
            if replicator_name_filter and replicator_name_filter not in replicator.replicator_name:
                continue
            replicators.append(
                {
                    "creationTime": replicator.creation_time,
                    "currentVersion": replicator.current_version,
                    "isReplicatorReference": False,
                    "replicatorArn": replicator.arn,
                    "replicatorName": replicator.replicator_name,
                    "replicatorState": replicator.state,
                }
            )
        return replicators, None

    def update_replication_info(
        self,
        replicator_arn: str,
        current_version: str,
        source_kafka_cluster_arn: str,
        target_kafka_cluster_arn: str,
        consumer_group_replication: Optional[dict[str, Any]],
        topic_replication: Optional[dict[str, Any]],
    ) -> dict[str, Any]:
        if replicator_arn not in self.replicators:
            raise NotFoundException(
                f"The replicator with the ARN {replicator_arn} was not found."
            )
        replicator = self.replicators[replicator_arn]
        # Update replication info entries
        for info in replicator.replication_info_list:
            if consumer_group_replication:
                info["consumerGroupReplication"] = consumer_group_replication
            if topic_replication:
                info["topicReplication"] = topic_replication
        replicator.current_version = str(int(replicator.current_version) + 1)
        return {
            "replicatorArn": replicator.arn,
            "replicatorState": replicator.state,
        }

    # ---- VPC Connection operations ----

    def create_vpc_connection(
        self,
        target_cluster_arn: str,
        authentication: str,
        vpc_id: str,
        client_subnets: list[str],
        security_groups: list[str],
        tags: Optional[dict[str, str]] = None,
    ) -> dict[str, Any]:
        vpc_conn = FakeVpcConnection(
            account_id=self.account_id,
            region_name=self.region_name,
            target_cluster_arn=target_cluster_arn,
            authentication=authentication,
            vpc_id=vpc_id,
            client_subnets=client_subnets,
            security_groups=security_groups,
            tags=tags,
        )
        self.vpc_connections[vpc_conn.arn] = vpc_conn
        if tags:
            self.tag_resource(vpc_conn.arn, tags)
        # Associate with target cluster if it exists
        if target_cluster_arn in self.clusters:
            self.clusters[target_cluster_arn].client_vpc_connections.append(vpc_conn.arn)
        return {
            "vpcConnectionArn": vpc_conn.arn,
            "state": vpc_conn.state,
            "authentication": vpc_conn.authentication,
            "vpcId": vpc_conn.vpc_id,
            "clientSubnets": vpc_conn.client_subnets,
            "securityGroups": vpc_conn.security_groups,
            "creationTime": vpc_conn.creation_time,
            "tags": vpc_conn.tags,
        }

    def describe_vpc_connection(self, arn: str) -> dict[str, Any]:
        if arn not in self.vpc_connections:
            raise NotFoundException(
                f"The VPC connection with the ARN {arn} was not found."
            )
        vpc_conn = self.vpc_connections[arn]
        return {
            "vpcConnectionArn": vpc_conn.arn,
            "targetClusterArn": vpc_conn.target_cluster_arn,
            "state": vpc_conn.state,
            "authentication": vpc_conn.authentication,
            "vpcId": vpc_conn.vpc_id,
            "subnets": vpc_conn.client_subnets,
            "securityGroups": vpc_conn.security_groups,
            "creationTime": vpc_conn.creation_time,
            "tags": self.list_tags_for_resource(vpc_conn.arn),
        }

    def delete_vpc_connection(self, arn: str) -> dict[str, Any]:
        if arn not in self.vpc_connections:
            raise NotFoundException(
                f"The VPC connection with the ARN {arn} was not found."
            )
        vpc_conn = self.vpc_connections.pop(arn)
        # Remove from cluster associations
        if vpc_conn.target_cluster_arn in self.clusters:
            cluster = self.clusters[vpc_conn.target_cluster_arn]
            if arn in cluster.client_vpc_connections:
                cluster.client_vpc_connections.remove(arn)
        return {
            "vpcConnectionArn": arn,
            "state": "DELETING",
        }

    def list_vpc_connections(
        self,
        max_results: Optional[int],
        next_token: Optional[str],
    ) -> tuple[list[dict[str, Any]], Optional[str]]:
        connections = []
        for vpc_conn in self.vpc_connections.values():
            connections.append(
                {
                    "vpcConnectionArn": vpc_conn.arn,
                    "targetClusterArn": vpc_conn.target_cluster_arn,
                    "creationTime": vpc_conn.creation_time,
                    "authentication": vpc_conn.authentication,
                    "vpcId": vpc_conn.vpc_id,
                    "state": vpc_conn.state,
                }
            )
        return connections, None

    def list_client_vpc_connections(
        self,
        cluster_arn: str,
        max_results: Optional[int],
        next_token: Optional[str],
    ) -> tuple[list[dict[str, Any]], Optional[str]]:
        cluster = self._get_cluster(cluster_arn)
        connections = []
        for vpc_arn in cluster.client_vpc_connections:
            if vpc_arn in self.vpc_connections:
                vpc_conn = self.vpc_connections[vpc_arn]
                connections.append(
                    {
                        "vpcConnectionArn": vpc_conn.arn,
                        "owner": vpc_conn.account_id,
                        "authentication": vpc_conn.authentication,
                        "creationTime": vpc_conn.creation_time,
                        "state": vpc_conn.state,
                    }
                )
        return connections, None

    def reject_client_vpc_connection(
        self, cluster_arn: str, vpc_connection_arn: str
    ) -> None:
        self._get_cluster(cluster_arn)
        if vpc_connection_arn in self.vpc_connections:
            self.vpc_connections[vpc_connection_arn].state = "REJECTED"

    # ---- Bootstrap Brokers ----

    def get_bootstrap_brokers(self, cluster_arn: str) -> dict[str, Any]:
        cluster = self._get_cluster(cluster_arn)
        num_brokers = cluster.number_of_broker_nodes or 3
        broker_strings = []
        tls_strings = []
        sasl_scram_strings = []
        sasl_iam_strings = []
        for i in range(1, num_brokers + 1):
            broker_strings.append(
                f"b-{i}.{cluster.cluster_name}.kafka.{cluster.region_name}.amazonaws.com:9092"
            )
            tls_strings.append(
                f"b-{i}.{cluster.cluster_name}.kafka.{cluster.region_name}.amazonaws.com:9094"
            )
            sasl_scram_strings.append(
                f"b-{i}.{cluster.cluster_name}.kafka.{cluster.region_name}.amazonaws.com:9096"
            )
            sasl_iam_strings.append(
                f"b-{i}.{cluster.cluster_name}.kafka.{cluster.region_name}.amazonaws.com:9098"
            )
        return {
            "bootstrapBrokerString": ",".join(broker_strings),
            "bootstrapBrokerStringTls": ",".join(tls_strings),
            "bootstrapBrokerStringSaslScram": ",".join(sasl_scram_strings),
            "bootstrapBrokerStringSaslIam": ",".join(sasl_iam_strings),
            "bootstrapBrokerStringPublicTls": "",
            "bootstrapBrokerStringPublicSaslScram": "",
            "bootstrapBrokerStringPublicSaslIam": "",
            "bootstrapBrokerStringVpcConnectivityTls": "",
            "bootstrapBrokerStringVpcConnectivitySaslScram": "",
            "bootstrapBrokerStringVpcConnectivitySaslIam": "",
        }

    # ---- Cluster Policy ----

    def get_cluster_policy(self, cluster_arn: str) -> dict[str, Any]:
        cluster = self._get_cluster(cluster_arn)
        if cluster.cluster_policy is None:
            raise NotFoundException(
                f"No cluster policy found for cluster {cluster_arn}."
            )
        return {
            "currentVersion": cluster.cluster_policy_version,
            "policy": cluster.cluster_policy,
        }

    def put_cluster_policy(
        self,
        cluster_arn: str,
        current_version: Optional[str],
        policy: str,
    ) -> dict[str, Any]:
        cluster = self._get_cluster(cluster_arn)
        cluster.cluster_policy = policy
        try:
            ver = int(cluster.cluster_policy_version)
            cluster.cluster_policy_version = str(ver + 1)
        except ValueError:
            cluster.cluster_policy_version = "2"
        return {"currentVersion": cluster.cluster_policy_version}

    def delete_cluster_policy(self, cluster_arn: str) -> None:
        cluster = self._get_cluster(cluster_arn)
        cluster.cluster_policy = None

    # ---- SCRAM Secrets ----

    def batch_associate_scram_secret(
        self, cluster_arn: str, secret_arn_list: list[str]
    ) -> dict[str, Any]:
        cluster = self._get_cluster(cluster_arn)
        unprocessed: list[dict[str, Any]] = []
        for secret_arn in secret_arn_list:
            if secret_arn in cluster.scram_secrets:
                unprocessed.append(
                    {
                        "errorCode": "InvalidParameterException",
                        "errorMessage": f"Secret {secret_arn} is already associated.",
                        "secretArn": secret_arn,
                    }
                )
            else:
                cluster.scram_secrets.append(secret_arn)
        return {
            "clusterArn": cluster_arn,
            "unprocessedScramSecrets": unprocessed,
        }

    def batch_disassociate_scram_secret(
        self, cluster_arn: str, secret_arn_list: list[str]
    ) -> dict[str, Any]:
        cluster = self._get_cluster(cluster_arn)
        unprocessed: list[dict[str, Any]] = []
        for secret_arn in secret_arn_list:
            if secret_arn in cluster.scram_secrets:
                cluster.scram_secrets.remove(secret_arn)
            else:
                unprocessed.append(
                    {
                        "errorCode": "InvalidParameterException",
                        "errorMessage": f"Secret {secret_arn} is not associated.",
                        "secretArn": secret_arn,
                    }
                )
        return {
            "clusterArn": cluster_arn,
            "unprocessedScramSecrets": unprocessed,
        }

    def list_scram_secrets(
        self,
        cluster_arn: str,
        max_results: Optional[int],
        next_token: Optional[str],
    ) -> tuple[list[str], Optional[str]]:
        cluster = self._get_cluster(cluster_arn)
        return cluster.scram_secrets, None

    # ---- Nodes ----

    def list_nodes(
        self,
        cluster_arn: str,
        max_results: Optional[int],
        next_token: Optional[str],
    ) -> tuple[list[dict[str, Any]], Optional[str]]:
        cluster = self._get_cluster(cluster_arn)
        nodes = []
        num_brokers = cluster.number_of_broker_nodes or 3
        for i in range(1, num_brokers + 1):
            broker_info = {
                "nodeType": "BROKER",
                "nodeARN": f"{cluster.arn}/broker/{i}",
                "brokerNodeInfo": {
                    "attachedENIId": f"eni-{uuid.uuid4().hex[:12]}",
                    "brokerId": float(i),
                    "clientSubnet": (cluster.broker_node_group_info or {}).get(
                        "clientSubnets", ["subnet-00000"]
                    )[0],
                    "clientVpcIpAddress": f"10.0.{i}.{i}",
                    "currentBrokerSoftwareInfo": {
                        "kafkaVersion": cluster.kafka_version or "2.8.1",
                    },
                    "endpoints": [
                        f"b-{i}.{cluster.cluster_name}.kafka.{cluster.region_name}.amazonaws.com"
                    ],
                },
            }
            nodes.append(broker_info)
        return nodes, None

    # ---- Kafka Versions ----

    def list_kafka_versions(
        self,
        max_results: Optional[int],
        next_token: Optional[str],
    ) -> tuple[list[dict[str, Any]], Optional[str]]:
        versions = [
            {"version": v, "status": "ACTIVE"} for v in KAFKA_VERSIONS
        ]
        return versions, None

    def get_compatible_kafka_versions(
        self, cluster_arn: Optional[str]
    ) -> list[dict[str, Any]]:
        if cluster_arn:
            cluster = self._get_cluster(cluster_arn)
            source_version = cluster.kafka_version or "2.8.1"
            targets = COMPATIBLE_KAFKA_VERSIONS.get(source_version, [])
            return [
                {
                    "sourceVersion": source_version,
                    "targetVersions": targets,
                }
            ]
        # Return all compatible versions
        result = []
        for source, targets in COMPATIBLE_KAFKA_VERSIONS.items():
            if targets:
                result.append(
                    {
                        "sourceVersion": source,
                        "targetVersions": targets,
                    }
                )
        return result

    # ---- Cluster Operations ----

    def describe_cluster_operation(
        self, cluster_operation_arn: str
    ) -> dict[str, Any]:
        if cluster_operation_arn not in self.cluster_operations:
            raise NotFoundException(
                f"The cluster operation with the ARN {cluster_operation_arn} was not found."
            )
        operation = self.cluster_operations[cluster_operation_arn]
        return operation.to_dict()

    def describe_cluster_operation_v2(
        self, cluster_operation_arn: str
    ) -> dict[str, Any]:
        if cluster_operation_arn not in self.cluster_operations:
            raise NotFoundException(
                f"The cluster operation with the ARN {cluster_operation_arn} was not found."
            )
        operation = self.cluster_operations[cluster_operation_arn]
        return operation.to_dict_v2()

    def list_cluster_operations(
        self,
        cluster_arn: str,
        max_results: Optional[int],
        next_token: Optional[str],
    ) -> tuple[list[dict[str, Any]], Optional[str]]:
        self._get_cluster(cluster_arn)
        operations = [
            op.to_dict()
            for op in self.cluster_operations.values()
            if op.cluster_arn == cluster_arn
        ]
        return operations, None

    def list_cluster_operations_v2(
        self,
        cluster_arn: str,
        max_results: Optional[int],
        next_token: Optional[str],
    ) -> tuple[list[dict[str, Any]], Optional[str]]:
        self._get_cluster(cluster_arn)
        operations = [
            op.to_dict_v2()
            for op in self.cluster_operations.values()
            if op.cluster_arn == cluster_arn
        ]
        return operations, None

    # ---- Reboot Broker ----

    def reboot_broker(
        self, cluster_arn: str, broker_ids: list[str]
    ) -> dict[str, Any]:
        self._get_cluster(cluster_arn)
        operation = self._create_operation(cluster_arn, "REBOOT_BROKER")
        return {
            "clusterArn": cluster_arn,
            "clusterOperationArn": operation.arn,
        }

    # ---- Update operations ----

    def update_broker_count(
        self,
        cluster_arn: str,
        current_version: str,
        target_number_of_broker_nodes: int,
    ) -> dict[str, Any]:
        cluster = self._get_cluster(cluster_arn)
        cluster.number_of_broker_nodes = target_number_of_broker_nodes
        cluster._increment_version()
        operation = self._create_operation(cluster_arn, "UPDATE_BROKER_COUNT")
        return {
            "clusterArn": cluster_arn,
            "clusterOperationArn": operation.arn,
        }

    def update_broker_storage(
        self,
        cluster_arn: str,
        current_version: str,
        target_broker_ebs_volume_info: list[dict[str, Any]],
    ) -> dict[str, Any]:
        cluster = self._get_cluster(cluster_arn)
        cluster._increment_version()
        operation = self._create_operation(cluster_arn, "UPDATE_BROKER_STORAGE")
        return {
            "clusterArn": cluster_arn,
            "clusterOperationArn": operation.arn,
        }

    def update_broker_type(
        self,
        cluster_arn: str,
        current_version: str,
        target_instance_type: str,
    ) -> dict[str, Any]:
        cluster = self._get_cluster(cluster_arn)
        if cluster.broker_node_group_info:
            cluster.broker_node_group_info["instanceType"] = target_instance_type
        cluster._increment_version()
        operation = self._create_operation(cluster_arn, "UPDATE_BROKER_TYPE")
        return {
            "clusterArn": cluster_arn,
            "clusterOperationArn": operation.arn,
        }

    def update_cluster_configuration(
        self,
        cluster_arn: str,
        configuration_info: dict[str, Any],
        current_version: str,
    ) -> dict[str, Any]:
        cluster = self._get_cluster(cluster_arn)
        cluster.configuration_info = configuration_info
        cluster._increment_version()
        operation = self._create_operation(cluster_arn, "UPDATE_CLUSTER_CONFIGURATION")
        return {
            "clusterArn": cluster_arn,
            "clusterOperationArn": operation.arn,
        }

    def update_cluster_kafka_version(
        self,
        cluster_arn: str,
        configuration_info: Optional[dict[str, Any]],
        current_version: str,
        target_kafka_version: str,
    ) -> dict[str, Any]:
        cluster = self._get_cluster(cluster_arn)
        cluster.kafka_version = target_kafka_version
        if configuration_info:
            cluster.configuration_info = configuration_info
        cluster._increment_version()
        operation = self._create_operation(cluster_arn, "UPDATE_CLUSTER_KAFKA_VERSION")
        return {
            "clusterArn": cluster_arn,
            "clusterOperationArn": operation.arn,
        }

    def update_connectivity(
        self,
        cluster_arn: str,
        connectivity_info: dict[str, Any],
        current_version: str,
    ) -> dict[str, Any]:
        cluster = self._get_cluster(cluster_arn)
        cluster.connectivity_info = connectivity_info
        cluster._increment_version()
        operation = self._create_operation(cluster_arn, "UPDATE_CONNECTIVITY")
        return {
            "clusterArn": cluster_arn,
            "clusterOperationArn": operation.arn,
        }

    def update_monitoring(
        self,
        cluster_arn: str,
        current_version: str,
        enhanced_monitoring: Optional[str],
        open_monitoring: Optional[dict[str, Any]],
        logging_info: Optional[dict[str, Any]],
    ) -> dict[str, Any]:
        cluster = self._get_cluster(cluster_arn)
        if enhanced_monitoring:
            cluster.enhanced_monitoring = enhanced_monitoring
        if open_monitoring:
            cluster.open_monitoring = open_monitoring
        if logging_info:
            cluster.logging_info = logging_info
        cluster._increment_version()
        operation = self._create_operation(cluster_arn, "UPDATE_MONITORING")
        return {
            "clusterArn": cluster_arn,
            "clusterOperationArn": operation.arn,
        }

    def update_security(
        self,
        cluster_arn: str,
        client_authentication: Optional[dict[str, Any]],
        current_version: str,
        encryption_info: Optional[dict[str, Any]],
    ) -> dict[str, Any]:
        cluster = self._get_cluster(cluster_arn)
        if client_authentication:
            cluster.client_authentication = client_authentication
        if encryption_info:
            cluster.encryption_info = encryption_info
        cluster._increment_version()
        operation = self._create_operation(cluster_arn, "UPDATE_SECURITY")
        return {
            "clusterArn": cluster_arn,
            "clusterOperationArn": operation.arn,
        }

    def update_storage(
        self,
        cluster_arn: str,
        current_version: str,
        provisioned_throughput: Optional[dict[str, Any]],
        storage_mode: Optional[str],
        volume_size_gb: Optional[int],
    ) -> dict[str, Any]:
        cluster = self._get_cluster(cluster_arn)
        if storage_mode:
            cluster.storage_mode = storage_mode
        cluster._increment_version()
        operation = self._create_operation(cluster_arn, "UPDATE_STORAGE")
        return {
            "clusterArn": cluster_arn,
            "clusterOperationArn": operation.arn,
        }

    def update_rebalancing(
        self,
        cluster_arn: str,
        current_version: str,
        rebalancing: dict[str, Any],
    ) -> dict[str, Any]:
        cluster = self._get_cluster(cluster_arn)
        cluster._increment_version()
        operation = self._create_operation(cluster_arn, "UPDATE_REBALANCING")
        return {
            "clusterArn": cluster_arn,
            "clusterOperationArn": operation.arn,
        }

    # ---- Topic operations ----

    def create_topic(
        self,
        cluster_arn: str,
        topic_name: str,
        partition_count: Optional[int],
        replication_factor: Optional[int],
        configs: Optional[dict[str, str]],
    ) -> dict[str, Any]:
        cluster = self._get_cluster(cluster_arn)
        if topic_name in cluster.topics:
            raise ConflictException(f"Topic {topic_name} already exists.")
        topic = FakeTopic(
            cluster_arn=cluster_arn,
            account_id=self.account_id,
            region_name=self.region_name,
            topic_name=topic_name,
            partition_count=partition_count or 1,
            replication_factor=replication_factor or 1,
            configs=configs,
        )
        cluster.topics[topic_name] = topic
        return {
            "topicArn": topic.arn,
            "topicName": topic.topic_name,
            "status": topic.status,
        }

    def delete_topic(
        self, cluster_arn: str, topic_name: str
    ) -> dict[str, Any]:
        cluster = self._get_cluster(cluster_arn)
        if topic_name not in cluster.topics:
            raise NotFoundException(f"Topic {topic_name} was not found.")
        topic = cluster.topics.pop(topic_name)
        return {
            "topicArn": topic.arn,
            "topicName": topic.topic_name,
            "status": "DELETING",
        }

    def describe_topic(
        self, cluster_arn: str, topic_name: str
    ) -> dict[str, Any]:
        cluster = self._get_cluster(cluster_arn)
        if topic_name not in cluster.topics:
            raise NotFoundException(f"Topic {topic_name} was not found.")
        topic = cluster.topics[topic_name]
        return {
            "topicArn": topic.arn,
            "topicName": topic.topic_name,
            "replicationFactor": topic.replication_factor,
            "partitionCount": topic.partition_count,
            "configs": topic.configs,
            "status": topic.status,
        }

    def list_topics(
        self,
        cluster_arn: str,
        max_results: Optional[int],
        next_token: Optional[str],
        topic_name_filter: Optional[str],
    ) -> tuple[list[dict[str, Any]], Optional[str]]:
        cluster = self._get_cluster(cluster_arn)
        topics = []
        for topic in cluster.topics.values():
            if topic_name_filter and topic_name_filter not in topic.topic_name:
                continue
            topics.append(
                {
                    "topicArn": topic.arn,
                    "topicName": topic.topic_name,
                    "status": topic.status,
                }
            )
        return topics, None

    def update_topic(
        self,
        cluster_arn: str,
        topic_name: str,
        configs: Optional[dict[str, str]],
        partition_count: Optional[int],
    ) -> dict[str, Any]:
        cluster = self._get_cluster(cluster_arn)
        if topic_name not in cluster.topics:
            raise NotFoundException(f"Topic {topic_name} was not found.")
        topic = cluster.topics[topic_name]
        if configs is not None:
            topic.configs = configs
        if partition_count is not None:
            topic.partition_count = partition_count
        return {
            "topicArn": topic.arn,
            "topicName": topic.topic_name,
            "status": topic.status,
        }

    def describe_topic_partitions(
        self,
        cluster_arn: str,
        topic_name: str,
        max_results: Optional[int],
        next_token: Optional[str],
    ) -> tuple[list[dict[str, Any]], Optional[str]]:
        cluster = self._get_cluster(cluster_arn)
        if topic_name not in cluster.topics:
            raise NotFoundException(f"Topic {topic_name} was not found.")
        topic = cluster.topics[topic_name]
        partitions = []
        for i in range(topic.partition_count):
            partitions.append(
                {
                    "partitionIndex": i,
                    "isr": [1],
                    "leader": 1,
                    "replicas": [1],
                }
            )
        return partitions, None

    # ---- Tagging ----

    def list_tags_for_resource(self, resource_arn: str) -> dict[str, str]:
        return self.tagger.get_tag_dict_for_resource(resource_arn)

    def tag_resource(self, resource_arn: str, tags: dict[str, str]) -> None:
        tags_list = [{"Key": k, "Value": v} for k, v in tags.items()]
        self.tagger.tag_resource(resource_arn, tags_list)

    def untag_resource(self, resource_arn: str, tag_keys: list[str]) -> None:
        self.tagger.untag_resource_using_names(resource_arn, tag_keys)


kafka_backends = BackendDict(KafkaBackend, "kafka")
