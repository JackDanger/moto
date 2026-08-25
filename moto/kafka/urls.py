"""kafka base URL and path."""

from .responses import KafkaResponse

url_bases = [
    r"https?://kafka\.(.+)\.amazonaws\.com",
]

url_paths = {
    # V2 API - clusters
    "{0}/api/v2/clusters$": KafkaResponse.dispatch,
    "{0}/api/v2/clusters/(?P<clusterArn>.+)/operations$": KafkaResponse.dispatch,
    "{0}/api/v2/clusters/(?P<clusterArn>.+)$": KafkaResponse.dispatch,
    # V2 API - operations
    "{0}/api/v2/operations/(?P<clusterOperationArn>.+)$": KafkaResponse.dispatch,
    # Tags
    "{0}/v1/tags/(?P<resourceArn>.+)$": KafkaResponse.dispatch,
    # Kafka versions
    "{0}/v1/kafka-versions$": KafkaResponse.dispatch,
    # Compatible kafka versions
    "{0}/v1/compatible-kafka-versions$": KafkaResponse.dispatch,
    # Configurations
    "{0}/v1/configurations$": KafkaResponse.dispatch,
    "{0}/v1/configurations/(?P<arn>.+)/revisions/(?P<revision>[0-9]+)$": KafkaResponse.dispatch,
    "{0}/v1/configurations/(?P<arn>.+)/revisions$": KafkaResponse.dispatch,
    "{0}/v1/configurations/(?P<arn>.+)$": KafkaResponse.dispatch,
    # Replicators
    "{0}/replication/v1/replicators$": KafkaResponse.dispatch,
    "{0}/replication/v1/replicators/(?P<replicatorArn>.+)/replication-info$": KafkaResponse.dispatch,
    "{0}/replication/v1/replicators/(?P<replicatorArn>.+)$": KafkaResponse.dispatch,
    # VPC connections
    "{0}/v1/vpc-connections$": KafkaResponse.dispatch,
    "{0}/v1/vpc-connection$": KafkaResponse.dispatch,
    "{0}/v1/vpc-connection/(?P<arn>.+)$": KafkaResponse.dispatch,
    # Operations (v1)
    "{0}/v1/operations/(?P<clusterOperationArn>.+)$": KafkaResponse.dispatch,
    # Cluster sub-resources (order matters - more specific first)
    "{0}/v1/clusters/(?P<clusterArn>.+)/topics/(?P<topicName>.+)/partitions$": KafkaResponse.dispatch,
    "{0}/v1/clusters/(?P<clusterArn>.+)/topics/(?P<topicName>.+)$": KafkaResponse.dispatch,
    "{0}/v1/clusters/(?P<clusterArn>.+)/topics$": KafkaResponse.dispatch,
    "{0}/v1/clusters/(?P<clusterArn>.+)/bootstrap-brokers$": KafkaResponse.dispatch,
    "{0}/v1/clusters/(?P<clusterArn>.+)/scram-secrets$": KafkaResponse.dispatch,
    "{0}/v1/clusters/(?P<clusterArn>.+)/policy$": KafkaResponse.dispatch,
    "{0}/v1/clusters/(?P<clusterArn>.+)/nodes/count$": KafkaResponse.dispatch,
    "{0}/v1/clusters/(?P<clusterArn>.+)/nodes/storage$": KafkaResponse.dispatch,
    "{0}/v1/clusters/(?P<clusterArn>.+)/nodes/type$": KafkaResponse.dispatch,
    "{0}/v1/clusters/(?P<clusterArn>.+)/nodes$": KafkaResponse.dispatch,
    "{0}/v1/clusters/(?P<clusterArn>.+)/operations$": KafkaResponse.dispatch,
    "{0}/v1/clusters/(?P<clusterArn>.+)/client-vpc-connections$": KafkaResponse.dispatch,
    "{0}/v1/clusters/(?P<clusterArn>.+)/client-vpc-connection$": KafkaResponse.dispatch,
    "{0}/v1/clusters/(?P<clusterArn>.+)/configuration$": KafkaResponse.dispatch,
    "{0}/v1/clusters/(?P<clusterArn>.+)/version$": KafkaResponse.dispatch,
    "{0}/v1/clusters/(?P<clusterArn>.+)/connectivity$": KafkaResponse.dispatch,
    "{0}/v1/clusters/(?P<clusterArn>.+)/monitoring$": KafkaResponse.dispatch,
    "{0}/v1/clusters/(?P<clusterArn>.+)/security$": KafkaResponse.dispatch,
    "{0}/v1/clusters/(?P<clusterArn>.+)/storage$": KafkaResponse.dispatch,
    "{0}/v1/clusters/(?P<clusterArn>.+)/rebalancing$": KafkaResponse.dispatch,
    "{0}/v1/clusters/(?P<clusterArn>.+)/reboot-broker$": KafkaResponse.dispatch,
    # Clusters (must be last to not shadow sub-resources)
    "{0}/v1/clusters$": KafkaResponse.dispatch,
    "{0}/v1/clusters/(?P<clusterArn>[^/]+)/policy$": KafkaResponse.dispatch,
    "{0}/v1/clusters/(?P<clusterArn>.+)$": KafkaResponse.dispatch,
}
