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
        return kafka_backends[self.current_account][self.region]

    def _cluster_arn_from_path(self) -> str:
        path = unquote(self.parsed_url.path)
        for prefix in ["/api/v2/clusters/", "/v1/clusters/"]:
            if prefix in path:
                after = path.split(prefix, 1)[1]
                for suffix in ["/bootstrap-brokers", "/scram-secrets", "/policy", "/nodes/count", "/nodes/storage", "/nodes/type", "/nodes", "/operations", "/client-vpc-connections", "/client-vpc-connection", "/configuration", "/version", "/connectivity", "/monitoring", "/security", "/storage", "/rebalancing", "/reboot-broker", "/topics"]:
                    if suffix in after:
                        return after.split(suffix)[0]
                return after
        return ""

    def create_cluster_v2(self) -> str:
        cluster_arn, cluster_name, state, cluster_type = self.kafka_backend.create_cluster_v2(cluster_name=self._get_param("clusterName"), tags=self._get_param("tags"), provisioned=self._get_param("provisioned"), serverless=self._get_param("serverless"))
        return json.dumps({"clusterArn": cluster_arn, "clusterName": cluster_name, "state": state, "clusterType": cluster_type})

    def describe_cluster_v2(self) -> str:
        return json.dumps({"clusterInfo": self.kafka_backend.describe_cluster_v2(cluster_arn=self._cluster_arn_from_path())})

    def list_clusters_v2(self) -> str:
        cl, nt = self.kafka_backend.list_clusters_v2(cluster_name_filter=self._get_param("clusterNameFilter"), cluster_type_filter=self._get_param("clusterTypeFilter"), max_results=self._get_param("maxResults"), next_token=self._get_param("nextToken"))
        return json.dumps({"clusterInfoList": cl, "nextToken": nt})

    def list_tags_for_resource(self) -> str:
        return json.dumps({"tags": self.kafka_backend.list_tags_for_resource(resource_arn=unquote(self.parsed_url.path.split("/tags/")[-1]))})

    def tag_resource(self) -> str:
        self.kafka_backend.tag_resource(resource_arn=unquote(self._get_param("resourceArn")), tags=self._get_param("tags"))
        return json.dumps({})

    def untag_resource(self) -> str:
        self.kafka_backend.untag_resource(resource_arn=unquote(self._get_param("resourceArn")), tag_keys=self.__dict__["data"]["tagKeys"])
        return json.dumps({})

    def create_cluster(self) -> str:
        arn, name, state = self.kafka_backend.create_cluster(broker_node_group_info=self._get_param("brokerNodeGroupInfo"), client_authentication=self._get_param("clientAuthentication"), cluster_name=self._get_param("clusterName"), configuration_info=self._get_param("configurationInfo"), encryption_info=self._get_param("encryptionInfo"), enhanced_monitoring=self._get_param("enhancedMonitoring"), open_monitoring=self._get_param("openMonitoring"), kafka_version=self._get_param("kafkaVersion"), logging_info=self._get_param("loggingInfo"), number_of_broker_nodes=self._get_param("numberOfBrokerNodes"), tags=self._get_param("tags"), storage_mode=self._get_param("storageMode"))
        return json.dumps({"clusterArn": arn, "clusterName": name, "state": state})

    def describe_cluster(self) -> str:
        return json.dumps({"clusterInfo": self.kafka_backend.describe_cluster(cluster_arn=self._cluster_arn_from_path())})

    def delete_cluster(self) -> str:
        arn, state = self.kafka_backend.delete_cluster(cluster_arn=self._cluster_arn_from_path(), current_version=self._get_param("currentVersion"))
        return json.dumps({"clusterArn": arn, "state": state})

    def list_clusters(self) -> str:
        cl = self.kafka_backend.list_clusters(cluster_name_filter=self._get_param("clusterNameFilter"), max_results=self._get_param("maxResults"), next_token=self._get_param("nextToken"))
        return json.dumps({"clusterInfoList": cl, "nextToken": self._get_param("nextToken")})

    def create_configuration(self) -> str:
        return json.dumps(self.kafka_backend.create_configuration(name=self._get_param("name"), description=self._get_param("description") or "", kafka_versions=self._get_param("kafkaVersions") or [], server_properties=self._get_param("serverProperties") or ""))

    def describe_configuration(self) -> str:
        path = unquote(self.parsed_url.path)
        arn = path.split("/v1/configurations/", 1)[1]
        if "/revisions" in arn:
            arn = arn.split("/revisions")[0]
        return json.dumps(self.kafka_backend.describe_configuration(arn=arn))

    def delete_configuration(self) -> str:
        return json.dumps(self.kafka_backend.delete_configuration(arn=unquote(self.parsed_url.path).split("/v1/configurations/", 1)[1]))

    def update_configuration(self) -> str:
        return json.dumps(self.kafka_backend.update_configuration(arn=unquote(self.parsed_url.path).split("/v1/configurations/", 1)[1], description=self._get_param("description") or "", server_properties=self._get_param("serverProperties") or ""))

    def list_configurations(self) -> str:
        configs, nt = self.kafka_backend.list_configurations(max_results=self._get_param("maxResults"), next_token=self._get_param("nextToken"))
        return json.dumps({"configurations": configs, "nextToken": nt})

    def list_configuration_revisions(self) -> str:
        path = unquote(self.parsed_url.path)
        arn = path.split("/v1/configurations/", 1)[1].split("/revisions")[0]
        revs, nt = self.kafka_backend.list_configuration_revisions(arn=arn, max_results=self._get_param("maxResults"), next_token=self._get_param("nextToken"))
        return json.dumps({"revisions": revs, "nextToken": nt})

    def describe_configuration_revision(self) -> str:
        path = unquote(self.parsed_url.path)
        parts = path.split("/v1/configurations/", 1)[1].split("/revisions/")
        return json.dumps(self.kafka_backend.describe_configuration_revision(arn=parts[0], revision=int(parts[1])))

    def create_replicator(self) -> str:
        return json.dumps(self.kafka_backend.create_replicator(replicator_name=self._get_param("replicatorName"), description=self._get_param("description") or "", kafka_clusters=self._get_param("kafkaClusters") or [], replication_info_list=self._get_param("replicationInfoList") or [], service_execution_role_arn=self._get_param("serviceExecutionRoleArn") or "", tags=self._get_param("tags")))

    def describe_replicator(self) -> str:
        path = unquote(self.parsed_url.path)
        ra = path.split("/replication/v1/replicators/", 1)[1]
        if "/replication-info" in ra:
            ra = ra.split("/replication-info")[0]
        return json.dumps(self.kafka_backend.describe_replicator(replicator_arn=ra))

    def delete_replicator(self) -> str:
        return json.dumps(self.kafka_backend.delete_replicator(replicator_arn=unquote(self.parsed_url.path).split("/replication/v1/replicators/", 1)[1], current_version=self._get_param("currentVersion")))

    def list_replicators(self) -> str:
        reps, nt = self.kafka_backend.list_replicators(max_results=self._get_param("maxResults"), next_token=self._get_param("nextToken"), replicator_name_filter=self._get_param("replicatorNameFilter"))
        return json.dumps({"replicators": reps, "nextToken": nt})

    def update_replication_info(self) -> str:
        path = unquote(self.parsed_url.path)
        ra = path.split("/replication/v1/replicators/", 1)[1]
        if "/replication-info" in ra:
            ra = ra.split("/replication-info")[0]
        return json.dumps(self.kafka_backend.update_replication_info(replicator_arn=ra, current_version=self._get_param("currentVersion"), source_kafka_cluster_arn=self._get_param("sourceKafkaClusterArn") or "", target_kafka_cluster_arn=self._get_param("targetKafkaClusterArn") or "", consumer_group_replication=self._get_param("consumerGroupReplication"), topic_replication=self._get_param("topicReplication")))

    def create_vpc_connection(self) -> str:
        return json.dumps(self.kafka_backend.create_vpc_connection(target_cluster_arn=self._get_param("targetClusterArn") or "", authentication=self._get_param("authentication") or "", vpc_id=self._get_param("vpcId") or "", client_subnets=self._get_param("clientSubnets") or [], security_groups=self._get_param("securityGroups") or [], tags=self._get_param("tags")))

    def describe_vpc_connection(self) -> str:
        return json.dumps(self.kafka_backend.describe_vpc_connection(arn=unquote(self.parsed_url.path).split("/v1/vpc-connection/", 1)[1]))

    def delete_vpc_connection(self) -> str:
        return json.dumps(self.kafka_backend.delete_vpc_connection(arn=unquote(self.parsed_url.path).split("/v1/vpc-connection/", 1)[1]))

    def list_vpc_connections(self) -> str:
        conns, nt = self.kafka_backend.list_vpc_connections(max_results=self._get_param("maxResults"), next_token=self._get_param("nextToken"))
        return json.dumps({"vpcConnections": conns, "nextToken": nt})

    def list_client_vpc_connections(self) -> str:
        conns, nt = self.kafka_backend.list_client_vpc_connections(cluster_arn=self._cluster_arn_from_path(), max_results=self._get_param("maxResults"), next_token=self._get_param("nextToken"))
        return json.dumps({"clientVpcConnections": conns, "nextToken": nt})

    def reject_client_vpc_connection(self) -> str:
        self.kafka_backend.reject_client_vpc_connection(cluster_arn=self._cluster_arn_from_path(), vpc_connection_arn=self._get_param("vpcConnectionArn") or "")
        return json.dumps({})

    def get_bootstrap_brokers(self) -> str:
        return json.dumps(self.kafka_backend.get_bootstrap_brokers(cluster_arn=self._cluster_arn_from_path()))

    def get_cluster_policy(self) -> str:
        return json.dumps(self.kafka_backend.get_cluster_policy(cluster_arn=self._cluster_arn_from_path()))

    def put_cluster_policy(self) -> str:
        return json.dumps(self.kafka_backend.put_cluster_policy(cluster_arn=self._cluster_arn_from_path(), current_version=self._get_param("currentVersion"), policy=self._get_param("policy") or ""))

    def delete_cluster_policy(self) -> str:
        self.kafka_backend.delete_cluster_policy(cluster_arn=self._cluster_arn_from_path())
        return json.dumps({})

    def batch_associate_scram_secret(self) -> str:
        return json.dumps(self.kafka_backend.batch_associate_scram_secret(cluster_arn=self._cluster_arn_from_path(), secret_arn_list=self._get_param("secretArnList") or []))

    def batch_disassociate_scram_secret(self) -> str:
        return json.dumps(self.kafka_backend.batch_disassociate_scram_secret(cluster_arn=self._cluster_arn_from_path(), secret_arn_list=self._get_param("secretArnList") or []))

    def list_scram_secrets(self) -> str:
        secrets, nt = self.kafka_backend.list_scram_secrets(cluster_arn=self._cluster_arn_from_path(), max_results=self._get_param("maxResults"), next_token=self._get_param("nextToken"))
        return json.dumps({"secretArnList": secrets, "nextToken": nt})

    def list_nodes(self) -> str:
        nodes, nt = self.kafka_backend.list_nodes(cluster_arn=self._cluster_arn_from_path(), max_results=self._get_param("maxResults"), next_token=self._get_param("nextToken"))
        return json.dumps({"nodeInfoList": nodes, "nextToken": nt})

    def list_kafka_versions(self) -> str:
        versions, nt = self.kafka_backend.list_kafka_versions(max_results=self._get_param("maxResults"), next_token=self._get_param("nextToken"))
        return json.dumps({"kafkaVersions": versions, "nextToken": nt})

    def get_compatible_kafka_versions(self) -> str:
        return json.dumps({"compatibleKafkaVersions": self.kafka_backend.get_compatible_kafka_versions(cluster_arn=self._get_param("clusterArn"))})

    def describe_cluster_operation(self) -> str:
        return json.dumps({"clusterOperationInfo": self.kafka_backend.describe_cluster_operation(cluster_operation_arn=unquote(self.parsed_url.path).split("/v1/operations/", 1)[1])})

    def describe_cluster_operation_v2(self) -> str:
        return json.dumps({"clusterOperationInfo": self.kafka_backend.describe_cluster_operation_v2(cluster_operation_arn=unquote(self.parsed_url.path).split("/api/v2/operations/", 1)[1])})

    def list_cluster_operations(self) -> str:
        ops, nt = self.kafka_backend.list_cluster_operations(cluster_arn=self._cluster_arn_from_path(), max_results=self._get_param("maxResults"), next_token=self._get_param("nextToken"))
        return json.dumps({"clusterOperationInfoList": ops, "nextToken": nt})

    def list_cluster_operations_v2(self) -> str:
        ops, nt = self.kafka_backend.list_cluster_operations_v2(cluster_arn=self._cluster_arn_from_path(), max_results=self._get_param("maxResults"), next_token=self._get_param("nextToken"))
        return json.dumps({"clusterOperationInfoList": ops, "nextToken": nt})

    def reboot_broker(self) -> str:
        return json.dumps(self.kafka_backend.reboot_broker(cluster_arn=self._cluster_arn_from_path(), broker_ids=self._get_param("brokerIds") or []))

    def update_broker_count(self) -> str:
        return json.dumps(self.kafka_backend.update_broker_count(cluster_arn=self._cluster_arn_from_path(), current_version=self._get_param("currentVersion") or "", target_number_of_broker_nodes=int(self._get_param("targetNumberOfBrokerNodes") or 3)))

    def update_broker_storage(self) -> str:
        return json.dumps(self.kafka_backend.update_broker_storage(cluster_arn=self._cluster_arn_from_path(), current_version=self._get_param("currentVersion") or "", target_broker_ebs_volume_info=self._get_param("targetBrokerEBSVolumeInfo") or []))

    def update_broker_type(self) -> str:
        return json.dumps(self.kafka_backend.update_broker_type(cluster_arn=self._cluster_arn_from_path(), current_version=self._get_param("currentVersion") or "", target_instance_type=self._get_param("targetInstanceType") or ""))

    def update_cluster_configuration(self) -> str:
        return json.dumps(self.kafka_backend.update_cluster_configuration(cluster_arn=self._cluster_arn_from_path(), configuration_info=self._get_param("configurationInfo") or {}, current_version=self._get_param("currentVersion") or ""))

    def update_cluster_kafka_version(self) -> str:
        return json.dumps(self.kafka_backend.update_cluster_kafka_version(cluster_arn=self._cluster_arn_from_path(), configuration_info=self._get_param("configurationInfo"), current_version=self._get_param("currentVersion") or "", target_kafka_version=self._get_param("targetKafkaVersion") or ""))

    def update_connectivity(self) -> str:
        return json.dumps(self.kafka_backend.update_connectivity(cluster_arn=self._cluster_arn_from_path(), connectivity_info=self._get_param("connectivityInfo") or {}, current_version=self._get_param("currentVersion") or ""))

    def update_monitoring(self) -> str:
        return json.dumps(self.kafka_backend.update_monitoring(cluster_arn=self._cluster_arn_from_path(), current_version=self._get_param("currentVersion") or "", enhanced_monitoring=self._get_param("enhancedMonitoring"), open_monitoring=self._get_param("openMonitoring"), logging_info=self._get_param("loggingInfo")))

    def update_security(self) -> str:
        return json.dumps(self.kafka_backend.update_security(cluster_arn=self._cluster_arn_from_path(), client_authentication=self._get_param("clientAuthentication"), current_version=self._get_param("currentVersion") or "", encryption_info=self._get_param("encryptionInfo")))

    def update_storage(self) -> str:
        return json.dumps(self.kafka_backend.update_storage(cluster_arn=self._cluster_arn_from_path(), current_version=self._get_param("currentVersion") or "", provisioned_throughput=self._get_param("provisionedThroughput"), storage_mode=self._get_param("storageMode"), volume_size_gb=self._get_param("volumeSizeGB")))

    def update_rebalancing(self) -> str:
        return json.dumps(self.kafka_backend.update_rebalancing(cluster_arn=self._cluster_arn_from_path(), current_version=self._get_param("currentVersion") or "", rebalancing=self._get_param("rebalancing") or {}))

    def create_topic(self) -> str:
        return json.dumps(self.kafka_backend.create_topic(cluster_arn=self._cluster_arn_from_path(), topic_name=self._get_param("topicName") or "", partition_count=self._get_param("partitionCount"), replication_factor=self._get_param("replicationFactor"), configs=self._get_param("configs")))

    def delete_topic(self) -> str:
        path = unquote(self.parsed_url.path)
        after_topics = path.split("/topics/", 1)[1]
        tn = after_topics.split("/")[0] if "/" in after_topics else after_topics
        return json.dumps(self.kafka_backend.delete_topic(cluster_arn=self._cluster_arn_from_path(), topic_name=tn))

    def describe_topic(self) -> str:
        path = unquote(self.parsed_url.path)
        after_topics = path.split("/topics/", 1)[1]
        tn = after_topics.split("/")[0] if "/" in after_topics else after_topics
        return json.dumps(self.kafka_backend.describe_topic(cluster_arn=self._cluster_arn_from_path(), topic_name=tn))

    def list_topics(self) -> str:
        topics, nt = self.kafka_backend.list_topics(cluster_arn=self._cluster_arn_from_path(), max_results=self._get_param("maxResults"), next_token=self._get_param("nextToken"), topic_name_filter=self._get_param("topicNameFilter"))
        return json.dumps({"topics": topics, "nextToken": nt})

    def update_topic(self) -> str:
        path = unquote(self.parsed_url.path)
        after_topics = path.split("/topics/", 1)[1]
        tn = after_topics.split("/")[0] if "/" in after_topics else after_topics
        return json.dumps(self.kafka_backend.update_topic(cluster_arn=self._cluster_arn_from_path(), topic_name=tn, configs=self._get_param("configs"), partition_count=self._get_param("partitionCount")))

    def describe_topic_partitions(self) -> str:
        path = unquote(self.parsed_url.path)
        tn = path.split("/topics/", 1)[1].split("/partitions")[0]
        parts, nt = self.kafka_backend.describe_topic_partitions(cluster_arn=self._cluster_arn_from_path(), topic_name=tn, max_results=self._get_param("maxResults"), next_token=self._get_param("nextToken"))
        return json.dumps({"partitions": parts, "nextToken": nt})
