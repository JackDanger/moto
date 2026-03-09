"""Handles incoming kafka requests, invokes methods, returns responses."""

import json
from urllib.parse import unquote

from moto.core.responses import BaseResponse

from .models import KafkaBackend, kafka_backends


class KafkaResponse(BaseResponse):
    """Handler for Kafka requests and responses."""

    def __init__(self) -> None:
        super().__init__(service_name="kafka")

    @property
    def kafka_backend(self) -> KafkaBackend:
        """Return backend instance specific for this region."""
        return kafka_backends[self.current_account][self.region]

    # ---- Helper to extract ARN from URL path ----

    def _cluster_arn_from_path(self) -> str:
        """Extract cluster ARN from URL path after /clusters/."""
        path = unquote(self.parsed_url.path)
        # Handle both /v1/clusters/{arn} and /v1/clusters/{arn}/sub-resource
        # Also handle /api/v2/clusters/{arn}/...
        for prefix in ["/api/v2/clusters/", "/v1/clusters/"]:
            if prefix in path:
                after = path.split(prefix, 1)[1]
                # The ARN contains colons and slashes, but sub-resources are known suffixes
                # We need to reconstruct: everything up to the known sub-path
                known_suffixes = [
                    "/bootstrap-brokers",
                    "/scram-secrets",
                    "/policy",
                    "/nodes",
                    "/operations",
                    "/client-vpc-connections",
                    "/client-vpc-connection",
                    "/nodes/count",
                    "/nodes/storage",
                    "/nodes/type",
                    "/configuration",
                    "/version",
                    "/connectivity",
                    "/monitoring",
                    "/security",
                    "/storage",
                    "/rebalancing",
                    "/reboot-broker",
                    "/topics",
                ]
                for suffix in known_suffixes:
                    if suffix in after:
                        return after.split(suffix)[0]
                return after
        return ""

    # ---- Cluster operations ----

    def create_cluster_v2(self) -> str:
        cluster_name = self._get_param("clusterName")
        tags = self._get_param("tags")
        provisioned = self._get_param("provisioned")
        serverless = self._get_param("serverless")
        cluster_arn, cluster_name, state, cluster_type = (
            self.kafka_backend.create_cluster_v2(
                cluster_name=cluster_name,
                tags=tags,
                provisioned=provisioned,
                serverless=serverless,
            )
        )
        return json.dumps(
            {
                "clusterArn": cluster_arn,
                "clusterName": cluster_name,
                "state": state,
                "clusterType": cluster_type,
            }
        )

    def describe_cluster_v2(self) -> str:
        cluster_arn = self._cluster_arn_from_path()
        cluster_info = self.kafka_backend.describe_cluster_v2(
            cluster_arn=cluster_arn,
        )
        return json.dumps({"clusterInfo": cluster_info})

    def list_clusters_v2(self) -> str:
        cluster_name_filter = self._get_param("clusterNameFilter")
        cluster_type_filter = self._get_param("clusterTypeFilter")
        max_results = self._get_param("maxResults")
        next_token = self._get_param("nextToken")
        cluster_info_list, next_token = self.kafka_backend.list_clusters_v2(
            cluster_name_filter=cluster_name_filter,
            cluster_type_filter=cluster_type_filter,
            max_results=max_results,
            next_token=next_token,
        )
        return json.dumps(
            {"clusterInfoList": cluster_info_list, "nextToken": next_token}
        )

    def list_tags_for_resource(self) -> str:
        resource_arn = unquote(self.parsed_url.path.split("/tags/")[-1])
        tags = self.kafka_backend.list_tags_for_resource(
            resource_arn=resource_arn,
        )
        return json.dumps({"tags": tags})

    def tag_resource(self) -> str:
        resource_arn = unquote(self._get_param("resourceArn"))
        tags = self._get_param("tags")
        self.kafka_backend.tag_resource(
            resource_arn=resource_arn,
            tags=tags,
        )
        return json.dumps({})

    def untag_resource(self) -> str:
        resource_arn = unquote(self._get_param("resourceArn"))
        tag_keys = self.__dict__["data"]["tagKeys"]
        self.kafka_backend.untag_resource(
            resource_arn=resource_arn,
            tag_keys=tag_keys,
        )
        return json.dumps({})

    def create_cluster(self) -> str:
        broker_node_group_info = self._get_param("brokerNodeGroupInfo")
        client_authentication = self._get_param("clientAuthentication")
        cluster_name = self._get_param("clusterName")
        configuration_info = self._get_param("configurationInfo")
        encryption_info = self._get_param("encryptionInfo")
        enhanced_monitoring = self._get_param("enhancedMonitoring")
        open_monitoring = self._get_param("openMonitoring")
        kafka_version = self._get_param("kafkaVersion")
        logging_info = self._get_param("loggingInfo")
        number_of_broker_nodes = self._get_param("numberOfBrokerNodes")
        tags = self._get_param("tags")
        storage_mode = self._get_param("storageMode")
        cluster_arn, cluster_name, state = self.kafka_backend.create_cluster(
            broker_node_group_info=broker_node_group_info,
            client_authentication=client_authentication,
            cluster_name=cluster_name,
            configuration_info=configuration_info,
            encryption_info=encryption_info,
            enhanced_monitoring=enhanced_monitoring,
            open_monitoring=open_monitoring,
            kafka_version=kafka_version,
            logging_info=logging_info,
            number_of_broker_nodes=number_of_broker_nodes,
            tags=tags,
            storage_mode=storage_mode,
        )
        return json.dumps(
            {"clusterArn": cluster_arn, "clusterName": cluster_name, "state": state}
        )

    def describe_cluster(self) -> str:
        cluster_arn = self._cluster_arn_from_path()
        cluster_info = self.kafka_backend.describe_cluster(
            cluster_arn=cluster_arn,
        )
        return json.dumps({"clusterInfo": cluster_info})

    def delete_cluster(self) -> str:
        cluster_arn = self._cluster_arn_from_path()
        current_version = self._get_param("currentVersion")
        cluster_arn, state = self.kafka_backend.delete_cluster(
            cluster_arn=cluster_arn,
            current_version=current_version,
        )
        return json.dumps({"clusterArn": cluster_arn, "state": state})

    def list_clusters(self) -> str:
        cluster_name_filter = self._get_param("clusterNameFilter")
        max_results = self._get_param("maxResults")
        next_token = self._get_param("nextToken")

        cluster_info_list = self.kafka_backend.list_clusters(
            cluster_name_filter=cluster_name_filter,
            max_results=max_results,
            next_token=next_token,
        )

        return json.dumps(
            {"clusterInfoList": cluster_info_list, "nextToken": next_token}
        )

    # ---- Configuration operations ----

    def create_configuration(self) -> str:
        name = self._get_param("name")
        description = self._get_param("description") or ""
        kafka_versions = self._get_param("kafkaVersions") or []
        server_properties = self._get_param("serverProperties") or ""
        result = self.kafka_backend.create_configuration(
            name=name,
            description=description,
            kafka_versions=kafka_versions,
            server_properties=server_properties,
        )
        return json.dumps(result)

    def describe_configuration(self) -> str:
        path = unquote(self.parsed_url.path)
        arn = path.split("/v1/configurations/", 1)[1]
        # Remove /revisions suffix if present
        if "/revisions" in arn:
            arn = arn.split("/revisions")[0]
        result = self.kafka_backend.describe_configuration(arn=arn)
        return json.dumps(result)

    def delete_configuration(self) -> str:
        path = unquote(self.parsed_url.path)
        arn = path.split("/v1/configurations/", 1)[1]
        result = self.kafka_backend.delete_configuration(arn=arn)
        return json.dumps(result)

    def update_configuration(self) -> str:
        path = unquote(self.parsed_url.path)
        arn = path.split("/v1/configurations/", 1)[1]
        description = self._get_param("description") or ""
        server_properties = self._get_param("serverProperties") or ""
        result = self.kafka_backend.update_configuration(
            arn=arn,
            description=description,
            server_properties=server_properties,
        )
        return json.dumps(result)

    def list_configurations(self) -> str:
        max_results = self._get_param("maxResults")
        next_token = self._get_param("nextToken")
        configs, next_token = self.kafka_backend.list_configurations(
            max_results=max_results,
            next_token=next_token,
        )
        return json.dumps({"configurations": configs, "nextToken": next_token})

    def list_configuration_revisions(self) -> str:
        path = unquote(self.parsed_url.path)
        arn = path.split("/v1/configurations/", 1)[1].split("/revisions")[0]
        max_results = self._get_param("maxResults")
        next_token = self._get_param("nextToken")
        revisions, next_token = self.kafka_backend.list_configuration_revisions(
            arn=arn,
            max_results=max_results,
            next_token=next_token,
        )
        return json.dumps({"revisions": revisions, "nextToken": next_token})

    def describe_configuration_revision(self) -> str:
        path = unquote(self.parsed_url.path)
        parts = path.split("/v1/configurations/", 1)[1]
        arn_and_rest = parts.split("/revisions/")
        arn = arn_and_rest[0]
        revision = int(arn_and_rest[1])
        result = self.kafka_backend.describe_configuration_revision(
            arn=arn, revision=revision
        )
        return json.dumps(result)

    # ---- Replicator operations ----

    def create_replicator(self) -> str:
        replicator_name = self._get_param("replicatorName")
        description = self._get_param("description") or ""
        kafka_clusters = self._get_param("kafkaClusters") or []
        replication_info_list = self._get_param("replicationInfoList") or []
        service_execution_role_arn = self._get_param("serviceExecutionRoleArn") or ""
        tags = self._get_param("tags")
        result = self.kafka_backend.create_replicator(
            replicator_name=replicator_name,
            description=description,
            kafka_clusters=kafka_clusters,
            replication_info_list=replication_info_list,
            service_execution_role_arn=service_execution_role_arn,
            tags=tags,
        )
        return json.dumps(result)

    def describe_replicator(self) -> str:
        path = unquote(self.parsed_url.path)
        replicator_arn = path.split("/replication/v1/replicators/", 1)[1]
        # Remove sub-paths if present
        if "/replication-info" in replicator_arn:
            replicator_arn = replicator_arn.split("/replication-info")[0]
        result = self.kafka_backend.describe_replicator(
            replicator_arn=replicator_arn
        )
        return json.dumps(result)

    def delete_replicator(self) -> str:
        path = unquote(self.parsed_url.path)
        replicator_arn = path.split("/replication/v1/replicators/", 1)[1]
        current_version = self._get_param("currentVersion")
        result = self.kafka_backend.delete_replicator(
            replicator_arn=replicator_arn,
            current_version=current_version,
        )
        return json.dumps(result)

    def list_replicators(self) -> str:
        max_results = self._get_param("maxResults")
        next_token = self._get_param("nextToken")
        replicator_name_filter = self._get_param("replicatorNameFilter")
        replicators, next_token = self.kafka_backend.list_replicators(
            max_results=max_results,
            next_token=next_token,
            replicator_name_filter=replicator_name_filter,
        )
        return json.dumps({"replicators": replicators, "nextToken": next_token})

    def update_replication_info(self) -> str:
        path = unquote(self.parsed_url.path)
        replicator_arn = path.split("/replication/v1/replicators/", 1)[1]
        if "/replication-info" in replicator_arn:
            replicator_arn = replicator_arn.split("/replication-info")[0]
        current_version = self._get_param("currentVersion")
        source_kafka_cluster_arn = self._get_param("sourceKafkaClusterArn") or ""
        target_kafka_cluster_arn = self._get_param("targetKafkaClusterArn") or ""
        consumer_group_replication = self._get_param("consumerGroupReplication")
        topic_replication = self._get_param("topicReplication")
        result = self.kafka_backend.update_replication_info(
            replicator_arn=replicator_arn,
            current_version=current_version,
            source_kafka_cluster_arn=source_kafka_cluster_arn,
            target_kafka_cluster_arn=target_kafka_cluster_arn,
            consumer_group_replication=consumer_group_replication,
            topic_replication=topic_replication,
        )
        return json.dumps(result)

    # ---- VPC Connection operations ----

    def create_vpc_connection(self) -> str:
        target_cluster_arn = self._get_param("targetClusterArn") or ""
        authentication = self._get_param("authentication") or ""
        vpc_id = self._get_param("vpcId") or ""
        client_subnets = self._get_param("clientSubnets") or []
        security_groups = self._get_param("securityGroups") or []
        tags = self._get_param("tags")
        result = self.kafka_backend.create_vpc_connection(
            target_cluster_arn=target_cluster_arn,
            authentication=authentication,
            vpc_id=vpc_id,
            client_subnets=client_subnets,
            security_groups=security_groups,
            tags=tags,
        )
        return json.dumps(result)

    def describe_vpc_connection(self) -> str:
        path = unquote(self.parsed_url.path)
        arn = path.split("/v1/vpc-connection/", 1)[1]
        result = self.kafka_backend.describe_vpc_connection(arn=arn)
        return json.dumps(result)

    def delete_vpc_connection(self) -> str:
        path = unquote(self.parsed_url.path)
        arn = path.split("/v1/vpc-connection/", 1)[1]
        result = self.kafka_backend.delete_vpc_connection(arn=arn)
        return json.dumps(result)

    def list_vpc_connections(self) -> str:
        max_results = self._get_param("maxResults")
        next_token = self._get_param("nextToken")
        connections, next_token = self.kafka_backend.list_vpc_connections(
            max_results=max_results,
            next_token=next_token,
        )
        return json.dumps(
            {"vpcConnections": connections, "nextToken": next_token}
        )

    def list_client_vpc_connections(self) -> str:
        cluster_arn = self._cluster_arn_from_path()
        max_results = self._get_param("maxResults")
        next_token = self._get_param("nextToken")
        connections, next_token = self.kafka_backend.list_client_vpc_connections(
            cluster_arn=cluster_arn,
            max_results=max_results,
            next_token=next_token,
        )
        return json.dumps(
            {"clientVpcConnections": connections, "nextToken": next_token}
        )

    def reject_client_vpc_connection(self) -> str:
        cluster_arn = self._cluster_arn_from_path()
        vpc_connection_arn = self._get_param("vpcConnectionArn") or ""
        self.kafka_backend.reject_client_vpc_connection(
            cluster_arn=cluster_arn,
            vpc_connection_arn=vpc_connection_arn,
        )
        return json.dumps({})

    # ---- Bootstrap Brokers ----

    def get_bootstrap_brokers(self) -> str:
        cluster_arn = self._cluster_arn_from_path()
        result = self.kafka_backend.get_bootstrap_brokers(cluster_arn=cluster_arn)
        return json.dumps(result)

    # ---- Cluster Policy ----

    def get_cluster_policy(self) -> str:
        cluster_arn = self._cluster_arn_from_path()
        result = self.kafka_backend.get_cluster_policy(cluster_arn=cluster_arn)
        return json.dumps(result)

    def put_cluster_policy(self) -> str:
        cluster_arn = self._cluster_arn_from_path()
        current_version = self._get_param("currentVersion")
        policy = self._get_param("policy") or ""
        result = self.kafka_backend.put_cluster_policy(
            cluster_arn=cluster_arn,
            current_version=current_version,
            policy=policy,
        )
        return json.dumps(result)

    def delete_cluster_policy(self) -> str:
        cluster_arn = self._cluster_arn_from_path()
        self.kafka_backend.delete_cluster_policy(cluster_arn=cluster_arn)
        return json.dumps({})

    # ---- SCRAM Secrets ----

    def batch_associate_scram_secret(self) -> str:
        cluster_arn = self._cluster_arn_from_path()
        secret_arn_list = self._get_param("secretArnList") or []
        result = self.kafka_backend.batch_associate_scram_secret(
            cluster_arn=cluster_arn,
            secret_arn_list=secret_arn_list,
        )
        return json.dumps(result)

    def batch_disassociate_scram_secret(self) -> str:
        cluster_arn = self._cluster_arn_from_path()
        secret_arn_list = self._get_param("secretArnList") or []
        result = self.kafka_backend.batch_disassociate_scram_secret(
            cluster_arn=cluster_arn,
            secret_arn_list=secret_arn_list,
        )
        return json.dumps(result)

    def list_scram_secrets(self) -> str:
        cluster_arn = self._cluster_arn_from_path()
        max_results = self._get_param("maxResults")
        next_token = self._get_param("nextToken")
        secrets, next_token = self.kafka_backend.list_scram_secrets(
            cluster_arn=cluster_arn,
            max_results=max_results,
            next_token=next_token,
        )
        return json.dumps({"secretArnList": secrets, "nextToken": next_token})

    # ---- Nodes ----

    def list_nodes(self) -> str:
        cluster_arn = self._cluster_arn_from_path()
        max_results = self._get_param("maxResults")
        next_token = self._get_param("nextToken")
        nodes, next_token = self.kafka_backend.list_nodes(
            cluster_arn=cluster_arn,
            max_results=max_results,
            next_token=next_token,
        )
        return json.dumps({"nodeInfoList": nodes, "nextToken": next_token})

    # ---- Kafka Versions ----

    def list_kafka_versions(self) -> str:
        max_results = self._get_param("maxResults")
        next_token = self._get_param("nextToken")
        versions, next_token = self.kafka_backend.list_kafka_versions(
            max_results=max_results,
            next_token=next_token,
        )
        return json.dumps({"kafkaVersions": versions, "nextToken": next_token})

    def get_compatible_kafka_versions(self) -> str:
        cluster_arn = self._get_param("clusterArn")
        result = self.kafka_backend.get_compatible_kafka_versions(
            cluster_arn=cluster_arn
        )
        return json.dumps({"compatibleKafkaVersions": result})

    # ---- Cluster Operations ----

    def describe_cluster_operation(self) -> str:
        path = unquote(self.parsed_url.path)
        operation_arn = path.split("/v1/operations/", 1)[1]
        result = self.kafka_backend.describe_cluster_operation(
            cluster_operation_arn=operation_arn
        )
        return json.dumps({"clusterOperationInfo": result})

    def describe_cluster_operation_v2(self) -> str:
        path = unquote(self.parsed_url.path)
        operation_arn = path.split("/api/v2/operations/", 1)[1]
        result = self.kafka_backend.describe_cluster_operation_v2(
            cluster_operation_arn=operation_arn
        )
        return json.dumps({"clusterOperationInfo": result})

    def list_cluster_operations(self) -> str:
        cluster_arn = self._cluster_arn_from_path()
        max_results = self._get_param("maxResults")
        next_token = self._get_param("nextToken")
        operations, next_token = self.kafka_backend.list_cluster_operations(
            cluster_arn=cluster_arn,
            max_results=max_results,
            next_token=next_token,
        )
        return json.dumps(
            {"clusterOperationInfoList": operations, "nextToken": next_token}
        )

    def list_cluster_operations_v2(self) -> str:
        cluster_arn = self._cluster_arn_from_path()
        max_results = self._get_param("maxResults")
        next_token = self._get_param("nextToken")
        operations, next_token = self.kafka_backend.list_cluster_operations_v2(
            cluster_arn=cluster_arn,
            max_results=max_results,
            next_token=next_token,
        )
        return json.dumps(
            {"clusterOperationInfoList": operations, "nextToken": next_token}
        )

    # ---- Reboot Broker ----

    def reboot_broker(self) -> str:
        cluster_arn = self._cluster_arn_from_path()
        broker_ids = self._get_param("brokerIds") or []
        result = self.kafka_backend.reboot_broker(
            cluster_arn=cluster_arn,
            broker_ids=broker_ids,
        )
        return json.dumps(result)

    # ---- Update operations ----

    def update_broker_count(self) -> str:
        cluster_arn = self._cluster_arn_from_path()
        current_version = self._get_param("currentVersion") or ""
        target_number = self._get_param("targetNumberOfBrokerNodes") or 3
        result = self.kafka_backend.update_broker_count(
            cluster_arn=cluster_arn,
            current_version=current_version,
            target_number_of_broker_nodes=int(target_number),
        )
        return json.dumps(result)

    def update_broker_storage(self) -> str:
        cluster_arn = self._cluster_arn_from_path()
        current_version = self._get_param("currentVersion") or ""
        target_broker_ebs_volume_info = (
            self._get_param("targetBrokerEBSVolumeInfo") or []
        )
        result = self.kafka_backend.update_broker_storage(
            cluster_arn=cluster_arn,
            current_version=current_version,
            target_broker_ebs_volume_info=target_broker_ebs_volume_info,
        )
        return json.dumps(result)

    def update_broker_type(self) -> str:
        cluster_arn = self._cluster_arn_from_path()
        current_version = self._get_param("currentVersion") or ""
        target_instance_type = self._get_param("targetInstanceType") or ""
        result = self.kafka_backend.update_broker_type(
            cluster_arn=cluster_arn,
            current_version=current_version,
            target_instance_type=target_instance_type,
        )
        return json.dumps(result)

    def update_cluster_configuration(self) -> str:
        cluster_arn = self._cluster_arn_from_path()
        configuration_info = self._get_param("configurationInfo") or {}
        current_version = self._get_param("currentVersion") or ""
        result = self.kafka_backend.update_cluster_configuration(
            cluster_arn=cluster_arn,
            configuration_info=configuration_info,
            current_version=current_version,
        )
        return json.dumps(result)

    def update_cluster_kafka_version(self) -> str:
        cluster_arn = self._cluster_arn_from_path()
        configuration_info = self._get_param("configurationInfo")
        current_version = self._get_param("currentVersion") or ""
        target_kafka_version = self._get_param("targetKafkaVersion") or ""
        result = self.kafka_backend.update_cluster_kafka_version(
            cluster_arn=cluster_arn,
            configuration_info=configuration_info,
            current_version=current_version,
            target_kafka_version=target_kafka_version,
        )
        return json.dumps(result)

    def update_connectivity(self) -> str:
        cluster_arn = self._cluster_arn_from_path()
        connectivity_info = self._get_param("connectivityInfo") or {}
        current_version = self._get_param("currentVersion") or ""
        result = self.kafka_backend.update_connectivity(
            cluster_arn=cluster_arn,
            connectivity_info=connectivity_info,
            current_version=current_version,
        )
        return json.dumps(result)

    def update_monitoring(self) -> str:
        cluster_arn = self._cluster_arn_from_path()
        current_version = self._get_param("currentVersion") or ""
        enhanced_monitoring = self._get_param("enhancedMonitoring")
        open_monitoring = self._get_param("openMonitoring")
        logging_info = self._get_param("loggingInfo")
        result = self.kafka_backend.update_monitoring(
            cluster_arn=cluster_arn,
            current_version=current_version,
            enhanced_monitoring=enhanced_monitoring,
            open_monitoring=open_monitoring,
            logging_info=logging_info,
        )
        return json.dumps(result)

    def update_security(self) -> str:
        cluster_arn = self._cluster_arn_from_path()
        client_authentication = self._get_param("clientAuthentication")
        current_version = self._get_param("currentVersion") or ""
        encryption_info = self._get_param("encryptionInfo")
        result = self.kafka_backend.update_security(
            cluster_arn=cluster_arn,
            client_authentication=client_authentication,
            current_version=current_version,
            encryption_info=encryption_info,
        )
        return json.dumps(result)

    def update_storage(self) -> str:
        cluster_arn = self._cluster_arn_from_path()
        current_version = self._get_param("currentVersion") or ""
        provisioned_throughput = self._get_param("provisionedThroughput")
        storage_mode = self._get_param("storageMode")
        volume_size_gb = self._get_param("volumeSizeGB")
        result = self.kafka_backend.update_storage(
            cluster_arn=cluster_arn,
            current_version=current_version,
            provisioned_throughput=provisioned_throughput,
            storage_mode=storage_mode,
            volume_size_gb=volume_size_gb,
        )
        return json.dumps(result)

    def update_rebalancing(self) -> str:
        cluster_arn = self._cluster_arn_from_path()
        current_version = self._get_param("currentVersion") or ""
        rebalancing = self._get_param("rebalancing") or {}
        result = self.kafka_backend.update_rebalancing(
            cluster_arn=cluster_arn,
            current_version=current_version,
            rebalancing=rebalancing,
        )
        return json.dumps(result)

    # ---- Topic operations ----

    def create_topic(self) -> str:
        cluster_arn = self._cluster_arn_from_path()
        topic_name = self._get_param("topicName") or ""
        partition_count = self._get_param("partitionCount")
        replication_factor = self._get_param("replicationFactor")
        configs = self._get_param("configs")
        result = self.kafka_backend.create_topic(
            cluster_arn=cluster_arn,
            topic_name=topic_name,
            partition_count=partition_count,
            replication_factor=replication_factor,
            configs=configs,
        )
        return json.dumps(result)

    def delete_topic(self) -> str:
        path = unquote(self.parsed_url.path)
        # /v1/clusters/{clusterArn}/topics/{topicName}
        cluster_arn = self._cluster_arn_from_path()
        after_topics = path.split("/topics/", 1)[1]
        # Remove any sub-paths (like /partitions)
        topic_name = after_topics.split("/")[0] if "/" in after_topics else after_topics
        result = self.kafka_backend.delete_topic(
            cluster_arn=cluster_arn,
            topic_name=topic_name,
        )
        return json.dumps(result)

    def describe_topic(self) -> str:
        path = unquote(self.parsed_url.path)
        cluster_arn = self._cluster_arn_from_path()
        after_topics = path.split("/topics/", 1)[1]
        topic_name = after_topics.split("/")[0] if "/" in after_topics else after_topics
        result = self.kafka_backend.describe_topic(
            cluster_arn=cluster_arn,
            topic_name=topic_name,
        )
        return json.dumps(result)

    def list_topics(self) -> str:
        cluster_arn = self._cluster_arn_from_path()
        max_results = self._get_param("maxResults")
        next_token = self._get_param("nextToken")
        topic_name_filter = self._get_param("topicNameFilter")
        topics, next_token = self.kafka_backend.list_topics(
            cluster_arn=cluster_arn,
            max_results=max_results,
            next_token=next_token,
            topic_name_filter=topic_name_filter,
        )
        return json.dumps({"topics": topics, "nextToken": next_token})

    def update_topic(self) -> str:
        path = unquote(self.parsed_url.path)
        cluster_arn = self._cluster_arn_from_path()
        after_topics = path.split("/topics/", 1)[1]
        topic_name = after_topics.split("/")[0] if "/" in after_topics else after_topics
        configs = self._get_param("configs")
        partition_count = self._get_param("partitionCount")
        result = self.kafka_backend.update_topic(
            cluster_arn=cluster_arn,
            topic_name=topic_name,
            configs=configs,
            partition_count=partition_count,
        )
        return json.dumps(result)

    def describe_topic_partitions(self) -> str:
        path = unquote(self.parsed_url.path)
        cluster_arn = self._cluster_arn_from_path()
        after_topics = path.split("/topics/", 1)[1]
        topic_name = after_topics.split("/partitions")[0]
        max_results = self._get_param("maxResults")
        next_token = self._get_param("nextToken")
        partitions, next_token = self.kafka_backend.describe_topic_partitions(
            cluster_arn=cluster_arn,
            topic_name=topic_name,
            max_results=max_results,
            next_token=next_token,
        )
        return json.dumps({"partitions": partitions, "nextToken": next_token})
