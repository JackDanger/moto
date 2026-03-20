"""Handles incoming memorydb requests, invokes methods, returns responses."""

import json

from moto.core.responses import ActionResult, BaseResponse

from .models import MemoryDBBackend, memorydb_backends


class MemoryDBResponse(BaseResponse):
    """Handler for MemoryDB requests and responses."""

    def __init__(self) -> None:
        super().__init__(service_name="memorydb")

    @property
    def memorydb_backend(self) -> MemoryDBBackend:
        """Return backend instance specific for this region."""
        return memorydb_backends[self.current_account][self.region]

    def create_cluster(self) -> ActionResult:
        params = json.loads(self.body)
        cluster_name = params.get("ClusterName")
        node_type = params.get("NodeType")
        parameter_group_name = params.get("ParameterGroupName")
        description = params.get("Description")
        num_shards = params.get("NumShards")
        num_replicas_per_shard = params.get("NumReplicasPerShard")
        subnet_group_name = params.get("SubnetGroupName")
        security_group_ids = params.get("SecurityGroupIds")
        maintenance_window = params.get("MaintenanceWindow")
        port = params.get("Port")
        sns_topic_arn = params.get("SnsTopicArn")
        tls_enabled = params.get("TLSEnabled")
        kms_key_id = params.get("KmsKeyId")
        snapshot_arns = params.get("SnapshotArns")
        snapshot_name = params.get("SnapshotName")
        snapshot_retention_limit = params.get("SnapshotRetentionLimit")
        tags = params.get("Tags")
        snapshot_window = params.get("SnapshotWindow")
        acl_name = params.get("ACLName")
        engine_version = params.get("EngineVersion")
        auto_minor_version_upgrade = params.get("AutoMinorVersionUpgrade")
        data_tiering = params.get("DataTiering")
        cluster = self.memorydb_backend.create_cluster(
            cluster_name=cluster_name,
            node_type=node_type,
            parameter_group_name=parameter_group_name,
            description=description,
            num_shards=num_shards,
            num_replicas_per_shard=num_replicas_per_shard,
            subnet_group_name=subnet_group_name,
            security_group_ids=security_group_ids,
            maintenance_window=maintenance_window,
            port=port,
            sns_topic_arn=sns_topic_arn,
            tls_enabled=tls_enabled,
            kms_key_id=kms_key_id,
            snapshot_arns=snapshot_arns,
            snapshot_name=snapshot_name,
            snapshot_retention_limit=snapshot_retention_limit,
            tags=tags,
            snapshot_window=snapshot_window,
            acl_name=acl_name,
            engine_version=engine_version,
            auto_minor_version_upgrade=auto_minor_version_upgrade,
            data_tiering=data_tiering,
        )
        return ActionResult({"Cluster": cluster.to_dict()})

    def create_subnet_group(self) -> ActionResult:
        params = json.loads(self.body)
        subnet_group_name = params.get("SubnetGroupName")
        description = params.get("Description")
        subnet_ids = params.get("SubnetIds")
        tags = params.get("Tags")
        subnet_group = self.memorydb_backend.create_subnet_group(
            subnet_group_name=subnet_group_name,
            description=description,
            subnet_ids=subnet_ids,
            tags=tags,
        )
        return ActionResult({"SubnetGroup": subnet_group.to_dict()})

    def create_snapshot(self) -> ActionResult:
        params = json.loads(self.body)
        cluster_name = params.get("ClusterName")
        snapshot_name = params.get("SnapshotName")
        kms_key_id = params.get("KmsKeyId")
        tags = params.get("Tags")
        snapshot = self.memorydb_backend.create_snapshot(
            cluster_name=cluster_name,
            snapshot_name=snapshot_name,
            kms_key_id=kms_key_id,
            tags=tags,
        )
        return ActionResult({"Snapshot": snapshot.to_dict()})

    def describe_clusters(self) -> ActionResult:
        params = json.loads(self.body)
        cluster_name = params.get("ClusterName")
        show_shard_details = params.get("ShowShardDetails")
        clusters = self.memorydb_backend.describe_clusters(
            cluster_name=cluster_name,
        )
        return ActionResult(
            {
                "Clusters": [
                    cluster.to_desc_dict() if show_shard_details else cluster.to_dict()
                    for cluster in clusters
                ]
            }
        )

    def describe_snapshots(self) -> ActionResult:
        params = json.loads(self.body)
        cluster_name = params.get("ClusterName")
        snapshot_name = params.get("SnapshotName")
        source = params.get("Source")
        show_detail = params.get("ShowDetail")
        snapshots = self.memorydb_backend.describe_snapshots(
            cluster_name=cluster_name,
            snapshot_name=snapshot_name,
            source=source,
        )
        return ActionResult(
            {
                "Snapshots": [
                    snapshot.to_desc_dict() if show_detail else snapshot.to_dict()
                    for snapshot in snapshots
                ]
            }
        )

    def describe_subnet_groups(self) -> ActionResult:
        params = json.loads(self.body)
        subnet_group_name = params.get("SubnetGroupName")
        subnet_groups = self.memorydb_backend.describe_subnet_groups(
            subnet_group_name=subnet_group_name,
        )
        return ActionResult({"SubnetGroups": [sg.to_dict() for sg in subnet_groups]})

    def list_tags(self) -> ActionResult:
        params = json.loads(self.body)
        resource_arn = params.get("ResourceArn")
        tag_list = self.memorydb_backend.list_tags(
            resource_arn=resource_arn,
        )
        return ActionResult({"TagList": tag_list})

    def tag_resource(self) -> ActionResult:
        params = json.loads(self.body)
        resource_arn = params.get("ResourceArn")
        tags = params.get("Tags")
        tag_list = self.memorydb_backend.tag_resource(
            resource_arn=resource_arn,
            tags=tags,
        )
        return ActionResult({"TagList": tag_list})

    def untag_resource(self) -> ActionResult:
        params = json.loads(self.body)
        resource_arn = params.get("ResourceArn")
        tag_keys = params.get("TagKeys")
        tag_list = self.memorydb_backend.untag_resource(
            resource_arn=resource_arn,
            tag_keys=tag_keys,
        )
        return ActionResult({"TagList": tag_list})

    def update_cluster(self) -> ActionResult:
        params = json.loads(self.body)
        cluster_name = params.get("ClusterName")
        description = params.get("Description")
        security_group_ids = params.get("SecurityGroupIds")
        maintenance_window = params.get("MaintenanceWindow")
        sns_topic_arn = params.get("SnsTopicArn")
        sns_topic_status = params.get("SnsTopicStatus")
        parameter_group_name = params.get("ParameterGroupName")
        snapshot_window = params.get("SnapshotWindow")
        snapshot_retention_limit = params.get("SnapshotRetentionLimit")
        node_type = params.get("NodeType")
        engine_version = params.get("EngineVersion")
        replica_configuration = params.get("ReplicaConfiguration")
        shard_configuration = params.get("ShardConfiguration")
        acl_name = params.get("ACLName")
        cluster = self.memorydb_backend.update_cluster(
            cluster_name=cluster_name,
            description=description,
            security_group_ids=security_group_ids,
            maintenance_window=maintenance_window,
            sns_topic_arn=sns_topic_arn,
            sns_topic_status=sns_topic_status,
            parameter_group_name=parameter_group_name,
            snapshot_window=snapshot_window,
            snapshot_retention_limit=snapshot_retention_limit,
            node_type=node_type,
            engine_version=engine_version,
            replica_configuration=replica_configuration,
            shard_configuration=shard_configuration,
            acl_name=acl_name,
        )
        return ActionResult({"Cluster": cluster.to_dict()})

    def delete_cluster(self) -> ActionResult:
        params = json.loads(self.body)
        cluster_name = params.get("ClusterName")
        final_snapshot_name = params.get("FinalSnapshotName")
        cluster = self.memorydb_backend.delete_cluster(
            cluster_name=cluster_name,
            final_snapshot_name=final_snapshot_name,
        )
        return ActionResult({"Cluster": cluster.to_dict()})

    def delete_snapshot(self) -> ActionResult:
        params = json.loads(self.body)
        snapshot_name = params.get("SnapshotName")
        snapshot = self.memorydb_backend.delete_snapshot(
            snapshot_name=snapshot_name,
        )
        return ActionResult({"Snapshot": snapshot.to_dict()})

    def delete_subnet_group(self) -> ActionResult:
        params = json.loads(self.body)
        subnet_group_name = params.get("SubnetGroupName")
        subnet_group = self.memorydb_backend.delete_subnet_group(
            subnet_group_name=subnet_group_name,
        )
        return ActionResult({"SubnetGroup": subnet_group.to_dict()})

    # ACL operations
    def create_acl(self) -> ActionResult:
        params = json.loads(self.body)
        acl = self.memorydb_backend.create_acl(
            acl_name=params.get("ACLName"),
            user_names=params.get("UserNames", []),
            tags=params.get("Tags", []),
        )
        return ActionResult({"ACL": acl.to_dict()})

    def describe_ac_ls(self) -> ActionResult:
        params = json.loads(self.body)
        acls = self.memorydb_backend.describe_acls(acl_name=params.get("ACLName"))
        return ActionResult({"ACLs": [acl.to_dict() for acl in acls]})

    def delete_acl(self) -> ActionResult:
        params = json.loads(self.body)
        acl = self.memorydb_backend.delete_acl(acl_name=params.get("ACLName"))
        return ActionResult({"ACL": acl.to_dict()})

    def update_acl(self) -> ActionResult:
        params = json.loads(self.body)
        acl = self.memorydb_backend.update_acl(
            acl_name=params.get("ACLName"),
            user_names_to_add=params.get("UserNamesToAdd"),
            user_names_to_remove=params.get("UserNamesToRemove"),
        )
        return ActionResult({"ACL": acl.to_dict()})

    # User operations
    def create_user(self) -> ActionResult:
        params = json.loads(self.body)
        user = self.memorydb_backend.create_user(
            user_name=params.get("UserName"),
            access_string=params.get("AccessString", ""),
            authentication_mode=params.get("AuthenticationMode"),
            tags=params.get("Tags", []),
        )
        return ActionResult({"User": user.to_dict()})

    def describe_users(self) -> ActionResult:
        params = json.loads(self.body)
        users = self.memorydb_backend.describe_users(user_name=params.get("UserName"))
        return ActionResult({"Users": [user.to_dict() for user in users]})

    def delete_user(self) -> ActionResult:
        params = json.loads(self.body)
        user = self.memorydb_backend.delete_user(user_name=params.get("UserName"))
        return ActionResult({"User": user.to_dict()})

    def update_user(self) -> ActionResult:
        params = json.loads(self.body)
        user = self.memorydb_backend.update_user(
            user_name=params.get("UserName"),
            access_string=params.get("AccessString"),
            authentication_mode=params.get("AuthenticationMode"),
        )
        return ActionResult({"User": user.to_dict()})

    # Parameter Group operations
    def create_parameter_group(self) -> ActionResult:
        params = json.loads(self.body)
        pg = self.memorydb_backend.create_parameter_group(
            name=params.get("ParameterGroupName"),
            family=params.get("Family", "memorydb_redis7"),
            description=params.get("Description", ""),
            tags=params.get("Tags", []),
        )
        return ActionResult({"ParameterGroup": pg.to_dict()})

    def describe_parameter_groups(self) -> ActionResult:
        params = json.loads(self.body)
        pgs = self.memorydb_backend.describe_parameter_groups(name=params.get("ParameterGroupName"))
        return ActionResult({"ParameterGroups": [pg.to_dict() for pg in pgs]})

    def delete_parameter_group(self) -> ActionResult:
        params = json.loads(self.body)
        pg = self.memorydb_backend.delete_parameter_group(name=params.get("ParameterGroupName"))
        return ActionResult({"ParameterGroup": pg.to_dict()})

    def update_parameter_group(self) -> ActionResult:
        params = json.loads(self.body)
        pg = self.memorydb_backend.update_parameter_group(
            name=params.get("ParameterGroupName"),
            parameter_name_values=params.get("ParameterNameValues", []),
        )
        return ActionResult({"ParameterGroup": pg.to_dict()})

    # Other list operations
    def describe_service_updates(self) -> ActionResult:
        updates = self.memorydb_backend.describe_service_updates()
        return ActionResult({"ServiceUpdates": updates})

    def describe_events(self) -> ActionResult:
        events = self.memorydb_backend.describe_events()
        return ActionResult({"Events": events})

    def describe_engine_versions(self) -> ActionResult:
        versions = self.memorydb_backend.describe_engine_versions()
        return ActionResult({"EngineVersions": versions})

    def describe_reserved_nodes(self) -> ActionResult:
        nodes = self.memorydb_backend.describe_reserved_nodes()
        return ActionResult({"ReservedNodes": nodes})

    def describe_reserved_nodes_offerings(self) -> ActionResult:
        offerings = self.memorydb_backend.describe_reserved_nodes_offerings()
        return ActionResult({"ReservedNodesOfferings": offerings})

    def copy_snapshot(self) -> ActionResult:
        params = json.loads(self.body)
        snapshot = self.memorydb_backend.copy_snapshot(
            source_snapshot_name=params.get("SourceSnapshotName"),
            target_snapshot_name=params.get("TargetSnapshotName"),
            kms_key_id=params.get("KmsKeyId"),
            tags=params.get("Tags", []),
        )
        return ActionResult({"Snapshot": snapshot.to_dict()})

    def update_subnet_group(self) -> ActionResult:
        params = json.loads(self.body)
        sg = self.memorydb_backend.update_subnet_group(
            subnet_group_name=params.get("SubnetGroupName"),
            description=params.get("Description"),
            subnet_ids=params.get("SubnetIds"),
        )
        return ActionResult({"SubnetGroup": sg.to_dict()})

    def reset_parameter_group(self) -> ActionResult:
        params = json.loads(self.body)
        pg = self.memorydb_backend.reset_parameter_group(
            parameter_group_name=params.get("ParameterGroupName"),
            all_parameters=params.get("AllParameters", False),
            parameter_names=params.get("ParameterNames"),
        )
        return ActionResult({"ParameterGroup": pg.to_dict()})

    def describe_parameters(self) -> ActionResult:
        params = json.loads(self.body)
        parameters = self.memorydb_backend.describe_parameters(
            parameter_group_name=params.get("ParameterGroupName"),
        )
        return ActionResult({"Parameters": parameters})

    def list_allowed_node_type_updates(self) -> ActionResult:
        params = json.loads(self.body)
        result = self.memorydb_backend.list_allowed_node_type_updates(
            cluster_name=params.get("ClusterName"),
        )
        return ActionResult(result)

    def batch_update_cluster(self) -> ActionResult:
        params = json.loads(self.body)
        processed, unprocessed = self.memorydb_backend.batch_update_cluster(
            cluster_names=params.get("ClusterNames", []),
            service_update=params.get("ServiceUpdate"),
        )
        return ActionResult({"ProcessedClusters": processed, "UnprocessedClusters": unprocessed})

    def purchase_reserved_nodes_offering(self) -> ActionResult:
        params = json.loads(self.body)
        result = self.memorydb_backend.purchase_reserved_nodes_offering(
            reserved_nodes_offering_id=params.get("ReservedNodesOfferingId"),
            reservation_id=params.get("ReservationId"),
            node_count=params.get("NodeCount", 1),
            tags=params.get("Tags", []),
        )
        return ActionResult({"ReservedNode": result})

    # --- Stub operations (return minimal valid responses) ---

    def create_multi_region_cluster(self) -> ActionResult:
        return ActionResult({"MultiRegionCluster": {}})

    def delete_multi_region_cluster(self) -> ActionResult:
        return ActionResult({"MultiRegionCluster": {}})

    def describe_multi_region_clusters(self) -> ActionResult:
        return ActionResult({"MultiRegionClusters": [], "NextToken": None})

    def describe_multi_region_parameter_groups(self) -> ActionResult:
        return ActionResult({"MultiRegionParameterGroups": [], "NextToken": None})

    def describe_multi_region_parameters(self) -> ActionResult:
        return ActionResult({"Parameters": [], "NextToken": None})

    def failover_shard(self) -> ActionResult:
        return ActionResult({"Cluster": {}})

    def list_allowed_multi_region_cluster_updates(self) -> ActionResult:
        return ActionResult({"MultiRegionParameterGroupName": "", "Parameters": []})

    def update_multi_region_cluster(self) -> ActionResult:
        return ActionResult({"MultiRegionCluster": {}})
