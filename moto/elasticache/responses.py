from moto.core.responses import ActionResult, BaseResponse, EmptyResult, PaginatedResult

from .exceptions import (
    InvalidParameterCombinationException,
    InvalidParameterValueException,
    PasswordTooShort,
)
from .models import ElastiCacheBackend, elasticache_backends
from .utils import VALID_AUTH_MODE_KEYS, VALID_ENGINE_TYPES, AuthenticationTypes


class ElastiCacheResponse(BaseResponse):
    """Handler for ElastiCache requests and responses."""

    def __init__(self) -> None:
        super().__init__(service_name="elasticache")
        self.automated_parameter_parsing = True

    @property
    def elasticache_backend(self) -> ElastiCacheBackend:
        """Return backend instance specific for this region."""
        return elasticache_backends[self.current_account][self.region]

    def create_user(self) -> ActionResult:
        params = self._get_params()
        user_id = params.get("UserId")
        user_name = params.get("UserName")
        engine = params.get("Engine", "").lower()
        passwords = params.get("Passwords", [])
        no_password_required = self._get_bool_param("NoPasswordRequired")
        authentication_mode = params.get("AuthenticationMode")
        authentication_type = "null"
        tags = params.get("Tags")

        if no_password_required is not None:
            authentication_type = (
                AuthenticationTypes.NOPASSWORD.value
                if no_password_required
                else AuthenticationTypes.PASSWORD.value
            )

        if passwords:
            authentication_type = AuthenticationTypes.PASSWORD.value

        if engine not in VALID_ENGINE_TYPES:
            raise InvalidParameterValueException(
                f'Unknown parameter for Engine: "{engine}", must be one of: {", ".join(VALID_ENGINE_TYPES)}'
            )

        if authentication_mode:
            for key, _ in authentication_mode.items():
                if key not in VALID_AUTH_MODE_KEYS:
                    raise InvalidParameterValueException(
                        f'Unknown parameter in AuthenticationMode: "{key}", must be one of: {", ".join(VALID_AUTH_MODE_KEYS)}'
                    )

            authentication_type = authentication_mode.get("Type")
            authentication_passwords = authentication_mode.get("Passwords", [])

            if passwords and authentication_passwords:
                raise InvalidParameterCombinationException(
                    "Passwords provided via multiple arguments. Use only one argument"
                )

            # if passwords is empty, then we can use the authentication_passwords
            passwords = passwords if passwords else authentication_passwords

        if any(len(p) < 16 for p in passwords):
            raise PasswordTooShort

        access_string = params.get("AccessString")
        user = self.elasticache_backend.create_user(
            user_id=user_id,  # type: ignore[arg-type]
            user_name=user_name,  # type: ignore[arg-type]
            engine=engine,  # type: ignore[arg-type]
            passwords=passwords,
            access_string=access_string,  # type: ignore[arg-type]
            no_password_required=no_password_required,
            authentication_type=authentication_type,
            tags=tags,
        )
        return ActionResult(user)

    def delete_user(self) -> ActionResult:
        params = self._get_params()
        user_id = params.get("UserId")
        user = self.elasticache_backend.delete_user(user_id=user_id)  # type: ignore[arg-type]
        return ActionResult(user)

    def describe_users(self) -> ActionResult:
        params = self._get_params()
        user_id = params.get("UserId")
        users = self.elasticache_backend.describe_users(user_id=user_id)
        return ActionResult({"Users": users})

    def create_cache_cluster(self) -> ActionResult:
        cache_cluster_id = self._get_param("CacheClusterId")
        replication_group_id = self._get_param("ReplicationGroupId")
        az_mode = self._get_param("AZMode")
        preferred_availability_zone = self._get_param("PreferredAvailabilityZone")
        preferred_availability_zones = self._get_param("PreferredAvailabilityZones")
        num_cache_nodes = self._get_int_param("NumCacheNodes")
        cache_node_type = self._get_param("CacheNodeType")
        engine = self._get_param("Engine")
        engine_version = self._get_param("EngineVersion")
        cache_parameter_group_name = self._get_param("CacheParameterGroupName")
        cache_subnet_group_name = self._get_param("CacheSubnetGroupName")
        cache_security_group_names = self._get_param("CacheSecurityGroupNames")
        security_group_ids = self._get_param("SecurityGroupIds")
        tags = self._get_param("Tags", [])
        snapshot_arns = self._get_param("SnapshotArns")
        snapshot_name = self._get_param("SnapshotName")
        preferred_maintenance_window = self._get_param("PreferredMaintenanceWindow")
        port = self._get_param("Port")
        notification_topic_arn = self._get_param("NotificationTopicArn")
        auto_minor_version_upgrade = self._get_bool_param("AutoMinorVersionUpgrade")
        snapshot_retention_limit = self._get_int_param("SnapshotRetentionLimit")
        snapshot_window = self._get_param("SnapshotWindow")
        auth_token = self._get_param("AuthToken")
        outpost_mode = self._get_param("OutpostMode")
        preferred_outpost_arn = self._get_param("PreferredOutpostArn")
        preferred_outpost_arns = self._get_param("PreferredOutpostArns")
        log_delivery_configurations = self._get_param("LogDeliveryConfigurations")
        transit_encryption_enabled = self._get_bool_param("TransitEncryptionEnabled")
        network_type = self._get_param("NetworkType")
        ip_discovery = self._get_param("IpDiscovery")
        # Define the following attributes as they're included in the response even during creation of a cache cluster
        cache_node_ids_to_remove = self._get_param("CacheNodeIdsToRemove", [])
        cache_node_ids_to_reboot = self._get_param("CacheNodeIdsToReboot", [])
        cache_cluster = self.elasticache_backend.create_cache_cluster(
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
        return ActionResult({"CacheCluster": cache_cluster})

    def describe_cache_clusters(self) -> ActionResult:
        cache_cluster_id = self._get_param("CacheClusterId")
        cache_clusters = self.elasticache_backend.describe_cache_clusters(
            cache_cluster_id=cache_cluster_id,
        )
        result = {"CacheClusters": cache_clusters}
        return PaginatedResult(result)

    def delete_cache_cluster(self) -> ActionResult:
        cache_cluster_id = self._get_param("CacheClusterId")
        cache_cluster = self.elasticache_backend.delete_cache_cluster(
            cache_cluster_id=cache_cluster_id,
        )
        return ActionResult({"CacheCluster": cache_cluster})

    def list_tags_for_resource(self) -> ActionResult:
        arn = self._get_param("ResourceName")
        result = self.elasticache_backend.list_tags_for_resource(arn)
        return ActionResult({"TagList": result["Tags"]})

    def add_tags_to_resource(self) -> ActionResult:
        arn = self._get_param("ResourceName")
        tags = self._get_param("Tags", [])
        self.elasticache_backend.add_tags_to_resource(arn, tags)
        return EmptyResult()

    def remove_tags_from_resource(self) -> ActionResult:
        arn = self._get_param("ResourceName")
        tags = self._get_param("TagKeys", [])
        self.elasticache_backend.remove_tags_from_resource(arn, tags)
        return EmptyResult()

    def create_cache_subnet_group(self) -> ActionResult:
        cache_subnet_group_name = self._get_param("CacheSubnetGroupName")
        cache_subnet_group_description = self._get_param("CacheSubnetGroupDescription")
        subnet_ids = self._get_param("SubnetIds", [])
        tags = self._get_param("Tags", [])
        cache_subnet_group = self.elasticache_backend.create_cache_subnet_group(
            cache_subnet_group_name=cache_subnet_group_name,
            cache_subnet_group_description=cache_subnet_group_description,
            subnet_ids=subnet_ids,
            tags=tags,
        )
        return ActionResult({"CacheSubnetGroup": cache_subnet_group})

    def describe_cache_subnet_groups(self) -> ActionResult:
        cache_subnet_group_name = self._get_param("CacheSubnetGroupName")
        cache_subnet_groups = self.elasticache_backend.describe_cache_subnet_groups(
            cache_subnet_group_name=cache_subnet_group_name,
        )
        result = {"CacheSubnetGroups": cache_subnet_groups}
        return PaginatedResult(result)

    def create_replication_group(self) -> ActionResult:
        params = self._get_params()
        replication_group_id = self._get_param("ReplicationGroupId")
        replication_group_description = self._get_param("ReplicationGroupDescription")
        global_replication_group_id = self._get_param("GlobalReplicationGroupId")
        primary_cluster_id = self._get_param("PrimaryClusterId")
        automatic_failover_enabled = self._get_bool_param("AutomaticFailoverEnabled")
        multi_az_enabled = self._get_bool_param("MultiAZEnabled")
        num_cache_clusters = self._get_int_param("NumCacheClusters")
        preferred_cache_cluster_azs = self._get_param("PreferredCacheClusterAZs", [])
        num_node_groups = self._get_int_param("NumNodeGroups")
        replicas_per_node_group = self._get_int_param("ReplicasPerNodeGroup")
        node_group_configuration = self._get_param("NodeGroupConfiguration", [])
        cache_node_type = self._get_param("CacheNodeType")
        engine = self._get_param("Engine")
        engine_version = self._get_param("EngineVersion")
        cache_parameter_group_name = self._get_param("CacheParameterGroupName")
        cache_subnet_group_name = self._get_param("CacheSubnetGroupName")
        cache_security_group_names = self._get_param("CacheSecurityGroupNames")
        security_group_ids = self._get_param("SecurityGroupIds")
        tags = self._get_param("Tags", [])
        snapshot_arns = self._get_param("SnapshotArns")
        snapshot_name = self._get_param("SnapshotName")
        preferred_maintenance_window = self._get_param("PreferredMaintenanceWindow")
        port = self._get_param("Port")
        notification_topic_arn = self._get_param("NotificationTopicArn")
        auto_minor_version_upgrade = self._get_param("AutoMinorVersionUpgrade")
        snapshot_retention_limit = self._get_int_param("SnapshotRetentionLimit")
        snapshot_window = self._get_param("SnapshotWindow")
        auth_token = self._get_param("AuthToken")
        transit_encryption_enabled = self._get_bool_param("TransitEncryptionEnabled")
        at_rest_encryption_enabled = self._get_bool_param("AtRestEncryptionEnabled")
        kms_key_id = self._get_param("KmsKeyId")
        user_group_ids = self._get_param("UserGroupIds")
        log_delivery_configurations = params.get("LogDeliveryConfigurations", [])
        data_tiering_enabled = self._get_param("DataTieringEnabled")
        network_type = self._get_param("NetworkType")
        ip_discovery = self._get_param("IpDiscovery")
        transit_encryption_mode = self._get_param("TransitEncryptionMode")
        cluster_mode = self._get_param("ClusterMode")
        serverless_cache_snapshot_name = self._get_param("ServerlessCacheSnapshotName")
        replication_group = self.elasticache_backend.create_replication_group(
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
        result = {"ReplicationGroup": replication_group}
        return ActionResult(result)

    def describe_replication_groups(self) -> ActionResult:
        replication_group_id = self._get_param("ReplicationGroupId")
        replication_groups = self.elasticache_backend.describe_replication_groups(
            replication_group_id=replication_group_id,
        )
        result = {"ReplicationGroups": replication_groups}
        return PaginatedResult(result)

    def delete_replication_group(self) -> ActionResult:
        replication_group_id = self._get_param("ReplicationGroupId")
        retain_primary_cluster = self._get_bool_param("RetainPrimaryCluster")
        replication_group = self.elasticache_backend.delete_replication_group(
            replication_group_id=replication_group_id,
            retain_primary_cluster=retain_primary_cluster,
        )
        return ActionResult({"ReplicationGroup": replication_group})

    def create_snapshot(self) -> ActionResult:
        snapshot_name = self._get_param("SnapshotName")
        replication_group_id = self._get_param("ReplicationGroupId")
        cache_cluster_id = self._get_param("CacheClusterId")
        kms_key_id = self._get_param("KmsKeyId")
        tags = self._get_param("Tags", [])

        snapshot = self.elasticache_backend.create_snapshot(
            snapshot_name=snapshot_name,
            replication_group_id=replication_group_id,
            cache_cluster_id=cache_cluster_id,
            kms_key_id=kms_key_id,
            tags=tags,
        )

        return ActionResult({"Snapshot": snapshot})

    def describe_snapshots(self) -> ActionResult:
        snapshot_name = self._get_param("SnapshotName")
        snapshot_source = self._get_param("SnapshotSource")
        replication_group_id = self._get_param("ReplicationGroupId")
        cache_cluster_id = self._get_param("CacheClusterId")
        max_records = self._get_param("MaxRecords")
        marker = self._get_param("Marker")

        snapshots = self.elasticache_backend.describe_snapshots(
            snapshot_name=snapshot_name,
            snapshot_source=snapshot_source,
            replication_group_id=replication_group_id,
            cache_cluster_id=cache_cluster_id,
            max_records=max_records,
            marker=marker,
        )

        return ActionResult({"Snapshots": snapshots, "Marker": marker})

    def delete_snapshot(self) -> ActionResult:
        snapshot_name = self._get_param("SnapshotName")

        snapshot = self.elasticache_backend.delete_snapshot(
            snapshot_name=snapshot_name,
        )

        return ActionResult({"Snapshot": snapshot})

    def describe_cache_engine_versions(self) -> ActionResult:
        engine = self._get_param("Engine")
        engine_version = self._get_param("EngineVersion")
        cache_parameter_group_family = self._get_param("CacheParameterGroupFamily")
        default_only = self._get_bool_param("DefaultOnly")

        versions = self.elasticache_backend.describe_cache_engine_versions(
            engine=engine,
            engine_version=engine_version,
            cache_parameter_group_family=cache_parameter_group_family,
            default_only=default_only or False,
        )
        return PaginatedResult({"CacheEngineVersions": versions})

    def describe_cache_parameter_groups(self) -> ActionResult:
        cache_parameter_group_name = self._get_param("CacheParameterGroupName")
        groups = self.elasticache_backend.describe_cache_parameter_groups(
            cache_parameter_group_name=cache_parameter_group_name,
        )
        return PaginatedResult({"CacheParameterGroups": groups})

    def describe_cache_parameters(self) -> ActionResult:
        cache_parameter_group_name = self._get_param("CacheParameterGroupName")
        params = self.elasticache_backend.describe_cache_parameters(
            cache_parameter_group_name=cache_parameter_group_name,
        )
        return PaginatedResult({"Parameters": params})

    def describe_events(self) -> ActionResult:
        source_identifier = self._get_param("SourceIdentifier")
        source_type = self._get_param("SourceType")
        duration = self._get_int_param("Duration")
        events = self.elasticache_backend.describe_events(
            source_identifier=source_identifier,
            source_type=source_type,
            duration=duration,
        )
        return PaginatedResult({"Events": events})

    def describe_serverless_caches(self) -> ActionResult:
        serverless_cache_name = self._get_param("ServerlessCacheName")
        caches = self.elasticache_backend.describe_serverless_caches(
            serverless_cache_name=serverless_cache_name,
        )
        return PaginatedResult({"ServerlessCaches": caches})

    def describe_service_updates(self) -> ActionResult:
        service_update_name = self._get_param("ServiceUpdateName")
        updates = self.elasticache_backend.describe_service_updates(
            service_update_name=service_update_name,
        )
        return PaginatedResult({"ServiceUpdates": updates})

    def describe_update_actions(self) -> ActionResult:
        replication_group_ids = self._get_param("ReplicationGroupIds")
        cache_cluster_ids = self._get_param("CacheClusterIds")
        service_update_name = self._get_param("ServiceUpdateName")
        actions = self.elasticache_backend.describe_update_actions(
            replication_group_ids=replication_group_ids,
            cache_cluster_ids=cache_cluster_ids,
            service_update_name=service_update_name,
        )
        return PaginatedResult({"UpdateActions": actions})

    def batch_apply_update_action(self) -> ActionResult:
        service_update_name = self._get_param("ServiceUpdateName")
        replication_group_ids = self._get_param("ReplicationGroupIds", [])
        cache_cluster_ids = self._get_param("CacheClusterIds", [])
        processed, unprocessed = self.elasticache_backend.batch_apply_update_action(
            service_update_name=service_update_name,
            replication_group_ids=replication_group_ids,
            cache_cluster_ids=cache_cluster_ids,
        )
        return ActionResult({
            "ProcessedUpdateActions": processed,
            "UnprocessedUpdateActions": unprocessed,
        })

    def batch_stop_update_action(self) -> ActionResult:
        service_update_name = self._get_param("ServiceUpdateName")
        replication_group_ids = self._get_param("ReplicationGroupIds", [])
        cache_cluster_ids = self._get_param("CacheClusterIds", [])
        processed, unprocessed = self.elasticache_backend.batch_stop_update_action(
            service_update_name=service_update_name,
            replication_group_ids=replication_group_ids,
            cache_cluster_ids=cache_cluster_ids,
        )
        return ActionResult({
            "ProcessedUpdateActions": processed,
            "UnprocessedUpdateActions": unprocessed,
        })

    def delete_cache_subnet_group(self) -> ActionResult:
        cache_subnet_group_name = self._get_param("CacheSubnetGroupName")
        self.elasticache_backend.delete_cache_subnet_group(
            cache_subnet_group_name=cache_subnet_group_name,
        )
        return EmptyResult()

    def describe_user_groups(self) -> ActionResult:
        user_group_id = self._get_param("UserGroupId")
        groups = self.elasticache_backend.describe_user_groups(
            user_group_id=user_group_id,
        )
        return PaginatedResult({"UserGroups": groups})

    # --- CacheParameterGroup ---

    def create_cache_parameter_group(self) -> ActionResult:
        name = self._get_param("CacheParameterGroupName")
        family = self._get_param("CacheParameterGroupFamily")
        description = self._get_param("Description")
        tags = self._get_param("Tags", [])
        group = self.elasticache_backend.create_cache_parameter_group(
            cache_parameter_group_name=name,
            cache_parameter_group_family=family,
            description=description,
            tags=tags,
        )
        return ActionResult({"CacheParameterGroup": group})

    def delete_cache_parameter_group(self) -> ActionResult:
        name = self._get_param("CacheParameterGroupName")
        self.elasticache_backend.delete_cache_parameter_group(
            cache_parameter_group_name=name,
        )
        return EmptyResult()

    def modify_cache_parameter_group(self) -> ActionResult:
        name = self._get_param("CacheParameterGroupName")
        parameter_name_values = self._get_param("ParameterNameValues", [])
        group = self.elasticache_backend.modify_cache_parameter_group(
            cache_parameter_group_name=name,
            parameter_name_values=parameter_name_values,
        )
        return ActionResult({"CacheParameterGroupName": group.cache_parameter_group_name})

    def reset_cache_parameter_group(self) -> ActionResult:
        name = self._get_param("CacheParameterGroupName")
        reset_all = self._get_bool_param("ResetAllParameters") or False
        parameter_name_values = self._get_param("ParameterNameValues", [])
        group = self.elasticache_backend.reset_cache_parameter_group(
            cache_parameter_group_name=name,
            reset_all_parameters=reset_all,
            parameter_name_values=parameter_name_values,
        )
        return ActionResult({"CacheParameterGroupName": group.cache_parameter_group_name})

    # --- CacheSecurityGroup ---

    def create_cache_security_group(self) -> ActionResult:
        name = self._get_param("CacheSecurityGroupName")
        description = self._get_param("Description")
        tags = self._get_param("Tags", [])
        group = self.elasticache_backend.create_cache_security_group(
            cache_security_group_name=name,
            description=description,
            tags=tags,
        )
        return ActionResult({"CacheSecurityGroup": group})

    def delete_cache_security_group(self) -> ActionResult:
        name = self._get_param("CacheSecurityGroupName")
        self.elasticache_backend.delete_cache_security_group(
            cache_security_group_name=name,
        )
        return EmptyResult()

    def describe_cache_security_groups(self) -> ActionResult:
        name = self._get_param("CacheSecurityGroupName")
        groups = self.elasticache_backend.describe_cache_security_groups(
            cache_security_group_name=name,
        )
        return PaginatedResult({"CacheSecurityGroups": groups})

    def revoke_cache_security_group_ingress(self) -> ActionResult:
        name = self._get_param("CacheSecurityGroupName")
        ec2_sg_name = self._get_param("EC2SecurityGroupName")
        ec2_sg_owner = self._get_param("EC2SecurityGroupOwnerId")
        group = self.elasticache_backend.revoke_cache_security_group_ingress(
            cache_security_group_name=name,
            ec2_security_group_name=ec2_sg_name,
            ec2_security_group_owner_id=ec2_sg_owner,
        )
        return ActionResult({"CacheSecurityGroup": group})

    # --- UserGroup ---

    def create_user_group(self) -> ActionResult:
        user_group_id = self._get_param("UserGroupId")
        engine = self._get_param("Engine", "").lower()
        user_ids = self._get_param("UserIds", [])
        tags = self._get_param("Tags", [])
        group = self.elasticache_backend.create_user_group(
            user_group_id=user_group_id,
            engine=engine,
            user_ids=user_ids if user_ids else None,
            tags=tags,
        )
        return ActionResult(group)

    def delete_user_group(self) -> ActionResult:
        user_group_id = self._get_param("UserGroupId")
        group = self.elasticache_backend.delete_user_group(
            user_group_id=user_group_id,
        )
        return ActionResult(group)

    def modify_user_group(self) -> ActionResult:
        user_group_id = self._get_param("UserGroupId")
        user_ids_to_add = self._get_param("UserIdsToAdd", [])
        user_ids_to_remove = self._get_param("UserIdsToRemove", [])
        group = self.elasticache_backend.modify_user_group(
            user_group_id=user_group_id,
            user_ids_to_add=user_ids_to_add if user_ids_to_add else None,
            user_ids_to_remove=user_ids_to_remove if user_ids_to_remove else None,
        )
        return ActionResult(group)

    # --- ServerlessCache ---

    def create_serverless_cache(self) -> ActionResult:
        params = self._get_params()
        cache = self.elasticache_backend.create_serverless_cache(
            serverless_cache_name=params.get("ServerlessCacheName"),
            engine=params.get("Engine", ""),
            description=params.get("Description"),
            major_engine_version=params.get("MajorEngineVersion"),
            cache_usage_limits=params.get("CacheUsageLimits"),
            kms_key_id=params.get("KmsKeyId"),
            security_group_ids=params.get("SecurityGroupIds", []),
            snapshot_arns_to_restore=params.get("SnapshotArnsToRestore", []),
            subnet_ids=params.get("SubnetIds", []),
            daily_snapshot_time=params.get("DailySnapshotTime"),
            snapshot_retention_limit=params.get("SnapshotRetentionLimit"),
            user_group_id=params.get("UserGroupId"),
            tags=params.get("Tags", []),
        )
        return ActionResult({"ServerlessCache": cache})

    def delete_serverless_cache(self) -> ActionResult:
        name = self._get_param("ServerlessCacheName")
        cache = self.elasticache_backend.delete_serverless_cache(
            serverless_cache_name=name,
        )
        return ActionResult({"ServerlessCache": cache})

    def modify_serverless_cache(self) -> ActionResult:
        params = self._get_params()
        cache = self.elasticache_backend.modify_serverless_cache(
            serverless_cache_name=params.get("ServerlessCacheName"),
            description=params.get("Description"),
            cache_usage_limits=params.get("CacheUsageLimits"),
            daily_snapshot_time=params.get("DailySnapshotTime"),
            snapshot_retention_limit=params.get("SnapshotRetentionLimit"),
            security_group_ids=params.get("SecurityGroupIds"),
            user_group_id=params.get("UserGroupId"),
        )
        return ActionResult({"ServerlessCache": cache})

    # --- ServerlessCacheSnapshot ---

    def create_serverless_cache_snapshot(self) -> ActionResult:
        name = self._get_param("ServerlessCacheSnapshotName")
        cache_name = self._get_param("ServerlessCacheName")
        tags = self._get_param("Tags", [])
        snapshot = self.elasticache_backend.create_serverless_cache_snapshot(
            serverless_cache_snapshot_name=name,
            serverless_cache_name=cache_name,
            tags=tags,
        )
        return ActionResult({"ServerlessCacheSnapshot": snapshot})

    def delete_serverless_cache_snapshot(self) -> ActionResult:
        name = self._get_param("ServerlessCacheSnapshotName")
        snapshot = self.elasticache_backend.delete_serverless_cache_snapshot(
            serverless_cache_snapshot_name=name,
        )
        return ActionResult({"ServerlessCacheSnapshot": snapshot})

    def describe_serverless_cache_snapshots(self) -> ActionResult:
        cache_name = self._get_param("ServerlessCacheName")
        snapshot_name = self._get_param("ServerlessCacheSnapshotName")
        snapshots = self.elasticache_backend.describe_serverless_cache_snapshots(
            serverless_cache_name=cache_name,
            serverless_cache_snapshot_name=snapshot_name,
        )
        return PaginatedResult({"ServerlessCacheSnapshots": snapshots})

    # --- GlobalReplicationGroup ---

    def create_global_replication_group(self) -> ActionResult:
        suffix = self._get_param("GlobalReplicationGroupIdSuffix")
        primary_rg_id = self._get_param("PrimaryReplicationGroupId")
        description = self._get_param("GlobalReplicationGroupDescription")
        grg = self.elasticache_backend.create_global_replication_group(
            global_replication_group_id_suffix=suffix,
            primary_replication_group_id=primary_rg_id,
            global_replication_group_description=description,
        )
        return ActionResult({"GlobalReplicationGroup": grg})

    def delete_global_replication_group(self) -> ActionResult:
        grg_id = self._get_param("GlobalReplicationGroupId")
        retain = self._get_bool_param("RetainPrimaryReplicationGroup") or True
        grg = self.elasticache_backend.delete_global_replication_group(
            global_replication_group_id=grg_id,
            retain_primary_replication_group=retain,
        )
        return ActionResult({"GlobalReplicationGroup": grg})

    def describe_global_replication_groups(self) -> ActionResult:
        grg_id = self._get_param("GlobalReplicationGroupId")
        groups = self.elasticache_backend.describe_global_replication_groups(
            global_replication_group_id=grg_id,
        )
        return PaginatedResult({"GlobalReplicationGroups": groups})

    def modify_global_replication_group(self) -> ActionResult:
        grg_id = self._get_param("GlobalReplicationGroupId")
        apply_immediately = self._get_bool_param("ApplyImmediately") or True
        cache_node_type = self._get_param("CacheNodeType")
        engine_version = self._get_param("EngineVersion")
        description = self._get_param("GlobalReplicationGroupDescription")
        failover = self._get_bool_param("AutomaticFailoverEnabled")
        grg = self.elasticache_backend.modify_global_replication_group(
            global_replication_group_id=grg_id,
            apply_immediately=apply_immediately,
            cache_node_type=cache_node_type,
            engine_version=engine_version,
            global_replication_group_description=description,
            automatic_failover_enabled=failover,
        )
        return ActionResult({"GlobalReplicationGroup": grg})

    # --- ModifyUser ---

    def modify_user(self) -> ActionResult:
        params = self._get_params()
        user_id = params.get("UserId")
        access_string = params.get("AccessString")
        append_access_string = params.get("AppendAccessString")
        passwords = params.get("Passwords")
        no_password_required = self._get_bool_param("NoPasswordRequired")
        authentication_mode = params.get("AuthenticationMode")
        user = self.elasticache_backend.modify_user(
            user_id=user_id,
            access_string=access_string,
            append_access_string=append_access_string,
            passwords=passwords,
            no_password_required=no_password_required,
            authentication_mode=authentication_mode,
        )
        return ActionResult(user)

    # --- ModifyCacheSubnetGroup ---

    def modify_cache_subnet_group(self) -> ActionResult:
        name = self._get_param("CacheSubnetGroupName")
        description = self._get_param("CacheSubnetGroupDescription")
        subnet_ids = self._get_param("SubnetIds")
        group = self.elasticache_backend.modify_cache_subnet_group(
            cache_subnet_group_name=name,
            cache_subnet_group_description=description,
            subnet_ids=subnet_ids,
        )
        return ActionResult({"CacheSubnetGroup": group})

    # --- ModifyCacheCluster ---

    def modify_cache_cluster(self) -> ActionResult:
        cache_cluster_id = self._get_param("CacheClusterId")
        num_cache_nodes = self._get_int_param("NumCacheNodes")
        cache_node_ids_to_remove = self._get_param("CacheNodeIdsToRemove")
        cache_parameter_group_name = self._get_param("CacheParameterGroupName")
        cache_security_group_names = self._get_param("CacheSecurityGroupNames")
        security_group_ids = self._get_param("SecurityGroupIds")
        preferred_maintenance_window = self._get_param("PreferredMaintenanceWindow")
        notification_topic_arn = self._get_param("NotificationTopicArn")
        engine_version = self._get_param("EngineVersion")
        auto_minor_version_upgrade = self._get_bool_param("AutoMinorVersionUpgrade")
        snapshot_retention_limit = self._get_int_param("SnapshotRetentionLimit")
        snapshot_window = self._get_param("SnapshotWindow")
        cache_node_type = self._get_param("CacheNodeType")
        auth_token = self._get_param("AuthToken")
        log_delivery_configurations = self._get_param("LogDeliveryConfigurations")
        cluster = self.elasticache_backend.modify_cache_cluster(
            cache_cluster_id=cache_cluster_id,
            num_cache_nodes=num_cache_nodes,
            cache_node_ids_to_remove=cache_node_ids_to_remove,
            cache_parameter_group_name=cache_parameter_group_name,
            cache_security_group_names=cache_security_group_names,
            security_group_ids=security_group_ids,
            preferred_maintenance_window=preferred_maintenance_window,
            notification_topic_arn=notification_topic_arn,
            engine_version=engine_version,
            auto_minor_version_upgrade=auto_minor_version_upgrade,
            snapshot_retention_limit=snapshot_retention_limit,
            snapshot_window=snapshot_window,
            cache_node_type=cache_node_type,
            auth_token=auth_token,
            log_delivery_configurations=log_delivery_configurations,
        )
        return ActionResult({"CacheCluster": cluster})

    # --- ModifyReplicationGroup ---

    def modify_replication_group(self) -> ActionResult:
        rg_id = self._get_param("ReplicationGroupId")
        description = self._get_param("ReplicationGroupDescription")
        primary_cluster_id = self._get_param("PrimaryClusterId")
        snapshotting_cluster_id = self._get_param("SnapshottingClusterId")
        automatic_failover = self._get_bool_param("AutomaticFailoverEnabled")
        multi_az = self._get_bool_param("MultiAZEnabled")
        cache_node_type = self._get_param("CacheNodeType")
        engine_version = self._get_param("EngineVersion")
        cache_parameter_group_name = self._get_param("CacheParameterGroupName")
        cache_security_group_names = self._get_param("CacheSecurityGroupNames")
        security_group_ids = self._get_param("SecurityGroupIds")
        preferred_maintenance_window = self._get_param("PreferredMaintenanceWindow")
        notification_topic_arn = self._get_param("NotificationTopicArn")
        snapshot_retention_limit = self._get_int_param("SnapshotRetentionLimit")
        snapshot_window = self._get_param("SnapshotWindow")
        log_delivery_configurations = self._get_param("LogDeliveryConfigurations")
        auth_token = self._get_param("AuthToken")
        transit_encryption_enabled = self._get_bool_param("TransitEncryptionEnabled")
        transit_encryption_mode = self._get_param("TransitEncryptionMode")
        user_group_ids_to_add = self._get_param("UserGroupIdsToAdd")
        user_group_ids_to_remove = self._get_param("UserGroupIdsToRemove")
        rg = self.elasticache_backend.modify_replication_group(
            replication_group_id=rg_id,
            replication_group_description=description,
            primary_cluster_id=primary_cluster_id,
            snapshotting_cluster_id=snapshotting_cluster_id,
            automatic_failover_enabled=automatic_failover,
            multi_az_enabled=multi_az,
            cache_node_type=cache_node_type,
            engine_version=engine_version,
            cache_parameter_group_name=cache_parameter_group_name,
            cache_security_group_names=cache_security_group_names,
            security_group_ids=security_group_ids,
            preferred_maintenance_window=preferred_maintenance_window,
            notification_topic_arn=notification_topic_arn,
            snapshot_retention_limit=snapshot_retention_limit,
            snapshot_window=snapshot_window,
            log_delivery_configurations=log_delivery_configurations,
            auth_token=auth_token,
            transit_encryption_enabled=transit_encryption_enabled,
            transit_encryption_mode=transit_encryption_mode,
            user_group_ids_to_add=user_group_ids_to_add,
            user_group_ids_to_remove=user_group_ids_to_remove,
        )
        return ActionResult({"ReplicationGroup": rg})

    # --- CopySnapshot ---

    def copy_snapshot(self) -> ActionResult:
        source = self._get_param("SourceSnapshotName")
        target = self._get_param("TargetSnapshotName")
        target_bucket = self._get_param("TargetBucket")
        kms_key_id = self._get_param("KmsKeyId")
        tags = self._get_param("Tags", [])
        snapshot = self.elasticache_backend.copy_snapshot(
            source_snapshot_name=source,
            target_snapshot_name=target,
            target_bucket=target_bucket,
            kms_key_id=kms_key_id,
            tags=tags,
        )
        return ActionResult({"Snapshot": snapshot})
