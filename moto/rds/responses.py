from typing import Any

from moto.core.parse import XFormedDict

from moto.core.responses import ActionResult, BaseResponse, EmptyResult, PaginatedResult
from moto.ec2.models import ec2_backends

from .exceptions import DBParameterGroupNotFoundError
from .models import RDSBackend, rds_backends


class RDSResponse(BaseResponse):
    PROTOCOL_PARSER_MAP_TYPE = XFormedDict

    def __init__(self) -> None:
        super().__init__(service_name="rds")
        self.automated_parameter_parsing = True

    @property
    def backend(self) -> RDSBackend:
        return rds_backends[self.current_account][self.region]

    @property
    def global_backend(self) -> RDSBackend:
        """Return backend instance of the region that stores Global Clusters"""
        return rds_backends[self.current_account]["us-east-1"]

    def create_db_instance(self) -> ActionResult:
        db_kwargs = self.params
        database = self.backend.create_db_instance(db_kwargs)
        result = {"DBInstance": database}
        return ActionResult(result)

    def create_db_instance_read_replica(self) -> ActionResult:
        db_kwargs = self.params
        database = self.backend.create_db_instance_read_replica(db_kwargs)
        result = {"DBInstance": database}
        return ActionResult(result)

    def describe_db_instances(self) -> ActionResult:
        db_instance_identifier = self.params.get("DBInstanceIdentifier")
        filters = self.params.get("Filters", [])
        filter_dict = {f["Name"]: f["Values"] for f in filters}
        db_instances = list(
            self.backend.describe_db_instances(
                db_instance_identifier, filters=filter_dict
            )
        )
        result = {"DBInstances": db_instances}
        return PaginatedResult(result)

    def modify_db_instance(self) -> ActionResult:
        db_instance_identifier = self.params.get("DBInstanceIdentifier")
        db_kwargs = self.params
        # This is a hack because the backend code expects the parameter to be
        # lowercased before validation is performed.  We need to move the
        # lowercasing to a backend setter (in one place) and then do the validation.
        if "PreferredMaintenanceWindow" in db_kwargs:
            db_kwargs["PreferredMaintenanceWindow"] = db_kwargs[
                "PreferredMaintenanceWindow"
            ].lower()
        new_db_instance_identifier = self.params.get("NewDBInstanceIdentifier")
        if new_db_instance_identifier:
            db_kwargs["new_db_instance_identifier"] = new_db_instance_identifier
        database = self.backend.modify_db_instance(db_instance_identifier, db_kwargs)
        result = {"DBInstance": database}
        return ActionResult(result)

    def delete_db_instance(self) -> ActionResult:
        db_snapshot_name = self.params.get("FinalDBSnapshotIdentifier")
        if db_snapshot_name is not None:
            self.backend.validate_db_snapshot_identifier(
                db_snapshot_name, parameter_name="FinalDBSnapshotIdentifier"
            )
        database = self.backend.delete_db_instance(**self.params)
        result = {"DBInstance": database}
        return ActionResult(result)

    def reboot_db_instance(self) -> ActionResult:
        db_instance_identifier = self.params.get("DBInstanceIdentifier")
        database = self.backend.reboot_db_instance(db_instance_identifier)
        result = {"DBInstance": database}
        return ActionResult(result)

    def create_db_snapshot(self) -> ActionResult:
        self.backend.validate_db_snapshot_identifier(
            self.params["DBSnapshotIdentifier"],
            parameter_name="DBSnapshotIdentifier",
        )
        snapshot = self.backend.create_db_snapshot(**self.params)
        result = {"DBSnapshot": snapshot}
        return ActionResult(result)

    def create_db_shard_group(self) -> ActionResult:
        kwargs = self.params
        db_shard_group = self.backend.create_db_shard_group(kwargs)
        return ActionResult(db_shard_group)

    def describe_db_shard_groups(self) -> ActionResult:
        db_shard_group_identifier = self.params.get("DBShardGroupIdentifier", None)
        filters = self.params.get("Filters", [])
        filter_dict = {f["Name"]: f["Values"] for f in filters}
        shard_groups = self.backend.describe_db_shard_groups(
            db_shard_group_identifier, filter_dict
        )
        result = {"DBShardGroups": shard_groups, "Marker": None}
        return ActionResult(result)

    def copy_db_snapshot(self) -> ActionResult:
        target_snapshot_identifier = self.params.get("TargetDBSnapshotIdentifier")
        self.backend.validate_db_snapshot_identifier(
            target_snapshot_identifier, parameter_name="TargetDBSnapshotIdentifier"
        )
        snapshot = self.backend.copy_db_snapshot(**self.params)
        result = {"DBSnapshot": snapshot}
        return ActionResult(result)

    def describe_db_snapshots(self) -> ActionResult:
        db_instance_identifier = self.params.get("DBInstanceIdentifier")
        db_snapshot_identifier = self.params.get("DBSnapshotIdentifier")
        snapshot_type = self.params.get("SnapshotType")
        filters = self.params.get("Filters", [])
        filter_dict = {f["Name"]: f["Values"] for f in filters}
        snapshots = self.backend.describe_db_snapshots(
            db_instance_identifier, db_snapshot_identifier, snapshot_type, filter_dict
        )
        result = {"DBSnapshots": snapshots}
        return ActionResult(result)

    def promote_read_replica(self) -> ActionResult:
        db_kwargs = self.params
        database = self.backend.promote_read_replica(db_kwargs)
        result = {"DBInstance": database}
        return ActionResult(result)

    def delete_db_snapshot(self) -> ActionResult:
        db_snapshot_identifier = self.params.get("DBSnapshotIdentifier")
        snapshot = self.backend.delete_db_snapshot(db_snapshot_identifier)
        result = {"DBSnapshot": snapshot}
        return ActionResult(result)

    def restore_db_instance_from_db_snapshot(self) -> ActionResult:
        db_snapshot_identifier = self.params.get("DBSnapshotIdentifier")
        db_kwargs = self.params
        new_instance = self.backend.restore_db_instance_from_db_snapshot(
            db_snapshot_identifier, db_kwargs
        )
        result = {"DBInstance": new_instance}
        return ActionResult(result)

    def restore_db_instance_to_point_in_time(self) -> ActionResult:
        source_db_identifier = self.params.get("SourceDBInstanceIdentifier")
        target_db_identifier = self.params.get("TargetDBInstanceIdentifier")

        db_kwargs = self.params
        new_instance = self.backend.restore_db_instance_to_point_in_time(
            source_db_identifier, target_db_identifier, db_kwargs
        )
        result = {"DBInstance": new_instance}
        return ActionResult(result)

    def restore_db_cluster_to_point_in_time(self) -> ActionResult:
        cluster = self.backend.restore_db_cluster_to_point_in_time(**self.params)
        result = {"DBCluster": cluster}
        return ActionResult(result)

    def failover_db_cluster(self) -> ActionResult:
        cluster = self.backend.failover_db_cluster(**self.params)
        result = {"DBCluster": cluster}
        return ActionResult(result)

    def list_tags_for_resource(self) -> ActionResult:
        arn = self.params.get("ResourceName")
        tags = self.backend.list_tags_for_resource(arn)
        result = {"TagList": tags}
        return ActionResult(result)

    def add_tags_to_resource(self) -> ActionResult:
        arn = self.params.get("ResourceName")
        tags = self.params.get("Tags", [])
        self.backend.add_tags_to_resource(arn, tags)
        return EmptyResult()

    def remove_tags_from_resource(self) -> ActionResult:
        arn = self.params.get("ResourceName")
        tag_keys = self.params.get("TagKeys")
        self.backend.remove_tags_from_resource(arn, tag_keys)
        return EmptyResult()

    def stop_db_instance(self) -> ActionResult:
        db_instance_identifier = self.params.get("DBInstanceIdentifier")
        db_snapshot_identifier = self.params.get("DBSnapshotIdentifier")
        if db_snapshot_identifier is not None:
            self.backend.validate_db_snapshot_identifier(
                db_snapshot_identifier, parameter_name="DBSnapshotIdentifier"
            )

        database = self.backend.stop_db_instance(
            db_instance_identifier, db_snapshot_identifier
        )
        result = {"DBInstance": database}
        return ActionResult(result)

    def start_db_instance(self) -> ActionResult:
        db_instance_identifier = self.params.get("DBInstanceIdentifier")
        database = self.backend.start_db_instance(db_instance_identifier)
        result = {"DBInstance": database}
        return ActionResult(result)

    def create_db_security_group(self) -> ActionResult:
        group_name = self.params.get("DBSecurityGroupName")
        description = self.params.get("DBSecurityGroupDescription")
        tags = self.params.get("Tags", [])
        security_group = self.backend.create_db_security_group(
            group_name, description, tags
        )
        result = {"DBSecurityGroup": security_group}
        return ActionResult(result)

    def describe_db_security_groups(self) -> ActionResult:
        security_group_name = self.params.get("DBSecurityGroupName")
        security_groups = self.backend.describe_security_groups(security_group_name)
        result = {"DBSecurityGroups": security_groups}
        return ActionResult(result)

    def delete_db_security_group(self) -> ActionResult:
        security_group_name = self.params.get("DBSecurityGroupName")
        security_group = self.backend.delete_security_group(security_group_name)
        result = {"DBSecurityGroup": security_group}
        return ActionResult(result)

    def authorize_db_security_group_ingress(self) -> ActionResult:
        security_group_name = self.params.get("DBSecurityGroupName")
        cidr_ip = self.params.get("CIDRIP")
        security_group = self.backend.authorize_security_group(
            security_group_name, cidr_ip
        )
        result = {"DBSecurityGroup": security_group}
        return ActionResult(result)

    def create_db_subnet_group(self) -> ActionResult:
        subnet_name = self.params.get("DBSubnetGroupName")
        description = self.params.get("DBSubnetGroupDescription")
        subnet_ids = self.params.get("SubnetIds", [])
        tags = self.params.get("Tags", [])
        subnets = [
            ec2_backends[self.current_account][self.region].get_subnet(subnet_id)
            for subnet_id in subnet_ids
        ]
        subnet_group = self.backend.create_subnet_group(
            subnet_name, description, subnets, tags
        )
        result = {"DBSubnetGroup": subnet_group}
        return ActionResult(result)

    def describe_db_subnet_groups(self) -> ActionResult:
        subnet_name = self.params.get("DBSubnetGroupName")
        subnet_groups = self.backend.describe_db_subnet_groups(subnet_name)
        result = {"DBSubnetGroups": subnet_groups}
        return ActionResult(result)

    def modify_db_subnet_group(self) -> ActionResult:
        subnet_name = self.params.get("DBSubnetGroupName")
        description = self.params.get("DBSubnetGroupDescription")
        subnet_ids = self.params.get("SubnetIds", [])
        subnets = [
            ec2_backends[self.current_account][self.region].get_subnet(subnet_id)
            for subnet_id in subnet_ids
        ]
        subnet_group = self.backend.modify_db_subnet_group(
            subnet_name, description, subnets
        )
        result = {"DBSubnetGroup": subnet_group}
        return ActionResult(result)

    def delete_db_subnet_group(self) -> ActionResult:
        subnet_name = self.params.get("DBSubnetGroupName")
        subnet_group = self.backend.delete_subnet_group(subnet_name)
        result = {"DBSubnetGroup": subnet_group}
        return ActionResult(result)

    def create_option_group(self) -> ActionResult:
        kwargs = self.params
        option_group = self.backend.create_option_group(kwargs)
        result = {"OptionGroup": option_group}
        return ActionResult(result)

    def delete_option_group(self) -> ActionResult:
        name = self.params["OptionGroupName"]
        option_group = self.backend.delete_option_group(name)
        result = {"OptionGroup": option_group}
        return ActionResult(result)

    def describe_option_groups(self) -> ActionResult:
        kwargs = self.params
        option_groups = self.backend.describe_option_groups(kwargs)
        result = {"OptionGroupsList": option_groups}
        return PaginatedResult(result)

    def describe_option_group_options(self) -> ActionResult:
        engine_name = self.params.get("EngineName")
        major_engine_version = self.params.get("MajorEngineVersion")
        options = self.backend.describe_option_group_options(
            engine_name, major_engine_version
        )
        return ActionResult({"OptionGroupOptions": options})

    def modify_option_group(self) -> ActionResult:
        option_group_name = self.params.get("OptionGroupName")
        options_to_include = self.params.get("OptionsToInclude", [])
        options_to_remove = self.params.get("OptionsToRemove", [])
        option_group = self.backend.modify_option_group(
            option_group_name, options_to_include, options_to_remove
        )
        result = {"OptionGroup": option_group}
        return ActionResult(result)

    def create_db_parameter_group(self) -> ActionResult:
        kwargs = self.params
        db_parameter_group = self.backend.create_db_parameter_group(kwargs)
        result = {"DBParameterGroup": db_parameter_group}
        return ActionResult(result)

    def copy_db_parameter_group(self) -> ActionResult:
        target_db_parameter_group = self.backend.copy_db_parameter_group(**self.params)
        result = {"DBParameterGroup": target_db_parameter_group}
        return ActionResult(result)

    def describe_db_parameter_groups(self) -> ActionResult:
        kwargs = self.params
        db_parameter_groups = self.backend.describe_db_parameter_groups(kwargs)
        result = {"DBParameterGroups": db_parameter_groups}
        return PaginatedResult(result)

    def modify_db_parameter_group(self) -> ActionResult:
        db_parameter_group_name = self.params.get("DBParameterGroupName")
        param_list = self.params.get("Parameters", [])
        # Raw dict is stored on the backend, so we need the original PascalCase items.
        db_parameter_group_parameters = [param.original_dict() for param in param_list]
        db_parameter_group = self.backend.modify_db_parameter_group(
            db_parameter_group_name, db_parameter_group_parameters
        )
        result = {"DBParameterGroupName": db_parameter_group.name}
        return ActionResult(result)

    def modify_db_cluster_parameter_group(self) -> ActionResult:
        db_parameter_group_name = self.params.get("DBClusterParameterGroupName")
        param_list = self.params.get("Parameters", [])
        # Raw dict is stored on the backend, so we need the original PascalCase items.
        db_parameter_group_parameters = [param.original_dict() for param in param_list]
        db_parameter_group = self.backend.modify_db_cluster_parameter_group(
            db_parameter_group_name, db_parameter_group_parameters
        )
        result = {"DBClusterParameterGroupName": db_parameter_group.name}
        return ActionResult(result)

    def describe_db_parameters(self) -> ActionResult:
        db_parameter_group_name = self.params.get("DBParameterGroupName")
        db_parameter_groups = self.backend.describe_db_parameter_groups(
            {"db_parameter_group_name": db_parameter_group_name}
        )
        if not db_parameter_groups:
            raise DBParameterGroupNotFoundError(db_parameter_group_name)
        parameters = db_parameter_groups[0].parameters.values()
        result = {"Parameters": parameters}
        return ActionResult(result)

    def delete_db_parameter_group(self) -> ActionResult:
        name = self.params["DBParameterGroupName"]
        db_parameter_group = self.backend.delete_db_parameter_group(name)
        return ActionResult(db_parameter_group)

    def describe_db_cluster_parameters(self) -> ActionResult:
        db_parameter_group_name = self.params.get("DBClusterParameterGroupName")
        db_parameter_groups = self.backend.describe_db_cluster_parameters(
            db_parameter_group_name
        )
        if db_parameter_groups is None:
            raise DBParameterGroupNotFoundError(db_parameter_group_name)
        result = {"Parameters": db_parameter_groups}
        return ActionResult(result)

    def create_db_cluster(self) -> ActionResult:
        kwargs = self.params
        cluster = self.backend.create_db_cluster(kwargs)
        result = {"DBCluster": cluster}
        return ActionResult(result)

    def modify_db_cluster(self) -> ActionResult:
        kwargs = self.params
        cluster = self.backend.modify_db_cluster(kwargs)
        result = {"DBCluster": cluster}
        return ActionResult(result)

    def describe_db_clusters(self) -> ActionResult:
        _id = self.params.get("DBClusterIdentifier")
        filters = self.params.get("Filters", [])
        filter_dict = {f["Name"]: f["Values"] for f in filters}
        clusters = self.backend.describe_db_clusters(
            db_cluster_identifier=_id, filters=filter_dict
        )
        result = {"DBClusters": clusters}
        return ActionResult(result)

    def delete_db_cluster(self) -> ActionResult:
        _id = self.params.get("DBClusterIdentifier")
        snapshot_name = self.params.get("FinalDBSnapshotIdentifier")
        cluster = self.backend.delete_db_cluster(
            cluster_identifier=_id, snapshot_name=snapshot_name
        )
        result = {"DBCluster": cluster}
        return ActionResult(result)

    def start_db_cluster(self) -> ActionResult:
        _id = self.params.get("DBClusterIdentifier")
        cluster = self.backend.start_db_cluster(cluster_identifier=_id)
        result = {"DBCluster": cluster}
        return ActionResult(result)

    def stop_db_cluster(self) -> ActionResult:
        _id = self.params.get("DBClusterIdentifier")
        cluster = self.backend.stop_db_cluster(cluster_identifier=_id)
        result = {"DBCluster": cluster}
        return ActionResult(result)

    def create_db_cluster_snapshot(self) -> ActionResult:
        snapshot = self.backend.create_db_cluster_snapshot(**self.params)
        result = {"DBClusterSnapshot": snapshot}
        return ActionResult(result)

    def copy_db_cluster_snapshot(self) -> ActionResult:
        snapshot = self.backend.copy_db_cluster_snapshot(**self.params)
        result = {"DBClusterSnapshot": snapshot}
        return ActionResult(result)

    def describe_db_cluster_snapshots(self) -> ActionResult:
        db_cluster_identifier = self.params.get("DBClusterIdentifier")
        db_snapshot_identifier = self.params.get("DBClusterSnapshotIdentifier")
        snapshot_type = self.params.get("SnapshotType")
        filters = self.params.get("Filters", [])
        filter_dict = {f["Name"]: f["Values"] for f in filters}
        snapshots = self.backend.describe_db_cluster_snapshots(
            db_cluster_identifier, db_snapshot_identifier, snapshot_type, filter_dict
        )
        results = {"DBClusterSnapshots": snapshots}
        return ActionResult(results)

    def delete_db_cluster_snapshot(self) -> ActionResult:
        db_snapshot_identifier = self.params["DBClusterSnapshotIdentifier"]
        snapshot = self.backend.delete_db_cluster_snapshot(db_snapshot_identifier)
        result = {"DBClusterSnapshot": snapshot}
        return ActionResult(result)

    def restore_db_cluster_from_snapshot(self) -> ActionResult:
        db_snapshot_identifier = self.params.get("SnapshotIdentifier")
        db_kwargs = self.params
        new_cluster = self.backend.restore_db_cluster_from_snapshot(
            db_snapshot_identifier, db_kwargs
        )
        result = {"DBCluster": new_cluster}
        return ActionResult(result)

    def start_export_task(self) -> ActionResult:
        kwargs = self.params
        export_task = self.backend.start_export_task(kwargs)
        return ActionResult(export_task)

    def cancel_export_task(self) -> ActionResult:
        export_task_identifier = self.params.get("ExportTaskIdentifier")
        export_task = self.backend.cancel_export_task(export_task_identifier)
        return ActionResult(export_task)

    def describe_export_tasks(self) -> ActionResult:
        export_task_identifier = self.params.get("ExportTaskIdentifier")
        tasks = self.backend.describe_export_tasks(export_task_identifier)
        result = {"ExportTasks": tasks}
        return ActionResult(result)

    def create_event_subscription(self) -> ActionResult:
        kwargs = self.params
        subscription = self.backend.create_event_subscription(kwargs)
        result = {"EventSubscription": subscription}
        return ActionResult(result)

    def delete_event_subscription(self) -> ActionResult:
        subscription_name = self.params.get("SubscriptionName")
        subscription = self.backend.delete_event_subscription(subscription_name)
        result = {"EventSubscription": subscription}
        return ActionResult(result)

    def describe_event_subscriptions(self) -> ActionResult:
        subscription_name = self.params.get("SubscriptionName")
        subscriptions = self.backend.describe_event_subscriptions(subscription_name)
        result = {"EventSubscriptionsList": subscriptions}
        return ActionResult(result)

    def modify_event_subscription(self) -> ActionResult:
        kwargs = self.params
        subscription = self.backend.modify_event_subscription(kwargs)
        result = {"EventSubscription": subscription}
        return ActionResult(result)

    def describe_orderable_db_instance_options(self) -> ActionResult:
        engine = self.params.get("Engine")
        engine_version = self.params.get("EngineVersion")
        options = self.backend.describe_orderable_db_instance_options(
            engine, engine_version
        )
        result = {"OrderableDBInstanceOptions": options}
        return PaginatedResult(result)

    def describe_global_clusters(self) -> ActionResult:
        clusters = self.global_backend.describe_global_clusters()
        result = {"GlobalClusters": clusters}
        return ActionResult(result)

    def create_global_cluster(self) -> ActionResult:
        params = self.params
        cluster = self.global_backend.create_global_cluster(
            global_cluster_identifier=params["GlobalClusterIdentifier"],
            source_db_cluster_identifier=params.get("SourceDBClusterIdentifier"),
            engine=params.get("Engine"),
            engine_version=params.get("EngineVersion"),
            storage_encrypted=params.get("StorageEncrypted"),
            deletion_protection=params.get("DeletionProtection"),
        )
        result = {"GlobalCluster": cluster}
        return ActionResult(result)

    def delete_global_cluster(self) -> ActionResult:
        params = self.params
        cluster = self.global_backend.delete_global_cluster(
            global_cluster_identifier=params["GlobalClusterIdentifier"],
        )
        result = {"GlobalCluster": cluster}
        return ActionResult(result)

    def modify_global_cluster(self) -> ActionResult:
        params = self.params
        cluster = self.global_backend.modify_global_cluster(
            global_cluster_identifier=params["GlobalClusterIdentifier"],
            new_global_cluster_identifier=params.get("NewGlobalClusterIdentifier"),
            deletion_protection=params.get("DeletionProtection"),
            engine_version=params.get("EngineVersion"),
            allow_major_version_upgrade=params.get("AllowMajorVersionUpgrade"),
        )
        result = {"GlobalCluster": cluster}
        return ActionResult(result)

    def remove_from_global_cluster(self) -> ActionResult:
        params = self.params
        global_cluster = self.backend.remove_from_global_cluster(
            global_cluster_identifier=params["GlobalClusterIdentifier"],
            db_cluster_identifier=params["DbClusterIdentifier"],
        )
        result = {"GlobalCluster": global_cluster}
        return ActionResult(result)

    def failover_global_cluster(self) -> ActionResult:
        params = self.params
        global_cluster = self.global_backend.failover_global_cluster(
            global_cluster_identifier=params["GlobalClusterIdentifier"],
            target_db_cluster_identifier=params["TargetDbClusterIdentifier"],
        )
        result = {"GlobalCluster": global_cluster}
        return ActionResult(result)

    def switchover_global_cluster(self) -> ActionResult:
        params = self.params
        global_cluster = self.global_backend.switchover_global_cluster(
            global_cluster_identifier=params["GlobalClusterIdentifier"],
            target_db_cluster_identifier=params["TargetDbClusterIdentifier"],
        )
        result = {"GlobalCluster": global_cluster}
        return ActionResult(result)

    def describe_db_engine_versions(self) -> ActionResult:
        engine = self.params.get("Engine")
        engine_version = self.params.get("EngineVersion")
        versions = self.backend.describe_db_engine_versions(
            engine=engine,
            engine_version=engine_version,
        )
        result = {"DBEngineVersions": versions}
        return PaginatedResult(result)

    def describe_event_categories(self) -> ActionResult:
        source_type = self.params.get("SourceType")
        categories = self.backend.describe_event_categories(source_type=source_type)
        result = {"EventCategoriesMapList": categories}
        return ActionResult(result)

    def add_source_identifier_to_subscription(self) -> ActionResult:
        subscription_name = self.params.get("SubscriptionName")
        source_identifier = self.params.get("SourceIdentifier")
        subscription = self.backend.add_source_identifier_to_subscription(
            subscription_name=subscription_name,
            source_identifier=source_identifier,
        )
        result = {"EventSubscription": subscription}
        return ActionResult(result)

    def remove_source_identifier_from_subscription(self) -> ActionResult:
        subscription_name = self.params.get("SubscriptionName")
        source_identifier = self.params.get("SourceIdentifier")
        subscription = self.backend.remove_source_identifier_from_subscription(
            subscription_name=subscription_name,
            source_identifier=source_identifier,
        )
        result = {"EventSubscription": subscription}
        return ActionResult(result)

    def apply_pending_maintenance_action(self) -> ActionResult:
        resource_identifier = self.params.get("ResourceIdentifier")
        apply_action = self.params.get("ApplyAction")
        opt_in_type = self.params.get("OptInType")
        result_data = self.backend.apply_pending_maintenance_action(
            resource_identifier=resource_identifier,
            apply_action=apply_action,
            opt_in_type=opt_in_type,
        )
        result = {"ResourcePendingMaintenanceActions": result_data}
        return ActionResult(result)

    def describe_pending_maintenance_actions(self) -> ActionResult:
        resource_identifier = self.params.get("ResourceIdentifier")
        actions = self.backend.describe_pending_maintenance_actions(
            resource_identifier=resource_identifier,
        )
        result = {"PendingMaintenanceActions": actions}
        return PaginatedResult(result)

    def describe_engine_default_cluster_parameters(self) -> ActionResult:
        db_parameter_group_family = self.params.get("DBParameterGroupFamily")
        result_data = self.backend.describe_engine_default_cluster_parameters(
            db_parameter_group_family=db_parameter_group_family,
        )
        result = {"EngineDefaults": result_data}
        return ActionResult(result)

    def describe_engine_default_parameters(self) -> ActionResult:
        db_parameter_group_family = self.params.get("DBParameterGroupFamily")
        result_data = self.backend.describe_engine_default_parameters(
            db_parameter_group_family=db_parameter_group_family,
        )
        result = {"EngineDefaults": result_data}
        return ActionResult(result)

    def describe_valid_db_instance_modifications(self) -> ActionResult:
        db_instance_identifier = self.params.get("DBInstanceIdentifier")
        result_data = self.backend.describe_valid_db_instance_modifications(
            db_instance_identifier=db_instance_identifier,
        )
        result = {"ValidDBInstanceModificationsMessage": result_data}
        return ActionResult(result)

    def create_db_cluster_parameter_group(self) -> ActionResult:
        db_cluster_parameter_group_name = self.params.get("DBClusterParameterGroupName")
        db_parameter_group_family = self.params.get("DBParameterGroupFamily")
        description = self.params.get("Description")
        tags = self.params.get("Tags", [])
        db_cluster_parameter_group = self.backend.create_db_cluster_parameter_group(
            db_cluster_parameter_group_name=db_cluster_parameter_group_name,
            db_parameter_group_family=db_parameter_group_family,
            description=description,
            tags=tags,
        )
        result = {"DBClusterParameterGroup": db_cluster_parameter_group}
        return ActionResult(result)

    def describe_db_cluster_parameter_groups(self) -> ActionResult:
        group_name = self.params.get("DBClusterParameterGroupName")
        db_parameter_groups = self.backend.describe_db_cluster_parameter_groups(
            group_name=group_name,
        )
        result = {"DBClusterParameterGroups": db_parameter_groups}
        return ActionResult(result)

    def delete_db_cluster_parameter_group(self) -> ActionResult:
        db_cluster_parameter_group_name = self.params.get("DBClusterParameterGroupName")
        self.backend.delete_db_cluster_parameter_group(
            db_cluster_parameter_group_name=db_cluster_parameter_group_name,
        )
        return EmptyResult()

    def copy_db_cluster_parameter_group(self) -> ActionResult:
        source_db_cluster_parameter_group_identifier = self.params.get(
            "SourceDBClusterParameterGroupIdentifier"
        )
        target_db_cluster_parameter_group_identifier = self.params.get(
            "TargetDBClusterParameterGroupIdentifier"
        )
        target_db_cluster_parameter_group_description = self.params.get(
            "TargetDBClusterParameterGroupDescription"
        )
        tags = self.params.get("Tags", [])
        target_group = self.backend.copy_db_cluster_parameter_group(
            source_db_cluster_parameter_group_identifier=source_db_cluster_parameter_group_identifier,
            target_db_cluster_parameter_group_identifier=target_db_cluster_parameter_group_identifier,
            target_db_cluster_parameter_group_description=target_db_cluster_parameter_group_description,
            tags=tags,
        )
        result = {"DBClusterParameterGroup": target_group}
        return ActionResult(result)

    def promote_read_replica_db_cluster(self) -> ActionResult:
        db_cluster_identifier = self.params.get("DBClusterIdentifier")
        cluster = self.backend.promote_read_replica_db_cluster(db_cluster_identifier)
        result = {"DBCluster": cluster}
        return ActionResult(result)

    def describe_db_snapshot_attributes(self) -> ActionResult:
        params = self.params
        db_snapshot_identifier = params["DBSnapshotIdentifier"]
        db_snapshot_attributes_result = self.backend.describe_db_snapshot_attributes(
            db_snapshot_identifier=db_snapshot_identifier,
        )
        result = {
            "DBSnapshotAttributesResult": {
                "DBSnapshotIdentifier": db_snapshot_identifier,
                "DBSnapshotAttributes": [
                    {"AttributeName": name, "AttributeValues": values}
                    for name, values in db_snapshot_attributes_result.items()
                ],
            }
        }
        return ActionResult(result)

    def modify_db_snapshot_attribute(self) -> ActionResult:
        params = self.params
        db_snapshot_identifier = params["DBSnapshotIdentifier"]
        db_snapshot_attributes_result = self.backend.modify_db_snapshot_attribute(
            db_snapshot_identifier=db_snapshot_identifier,
            attribute_name=params["AttributeName"],
            values_to_add=params.get("ValuesToAdd"),
            values_to_remove=params.get("ValuesToRemove"),
        )
        result = {
            "DBSnapshotAttributesResult": {
                "DBSnapshotIdentifier": db_snapshot_identifier,
                "DBSnapshotAttributes": [
                    {"AttributeName": name, "AttributeValues": values}
                    for name, values in db_snapshot_attributes_result.items()
                ],
            }
        }
        return ActionResult(result)

    def describe_db_cluster_snapshot_attributes(self) -> ActionResult:
        params = self.params
        db_cluster_snapshot_identifier = params["DBClusterSnapshotIdentifier"]
        db_cluster_snapshot_attributes_result = (
            self.backend.describe_db_cluster_snapshot_attributes(
                db_cluster_snapshot_identifier=db_cluster_snapshot_identifier,
            )
        )
        result = {
            "DBClusterSnapshotAttributesResult": {
                "DBClusterSnapshotIdentifier": db_cluster_snapshot_identifier,
                "DBClusterSnapshotAttributes": [
                    {"AttributeName": name, "AttributeValues": values}
                    for name, values in db_cluster_snapshot_attributes_result.items()
                ],
            }
        }
        return ActionResult(result)

    def modify_db_cluster_snapshot_attribute(self) -> ActionResult:
        params = self.params
        db_cluster_snapshot_identifier = params["DBClusterSnapshotIdentifier"]
        db_cluster_snapshot_attributes_result = (
            self.backend.modify_db_cluster_snapshot_attribute(
                db_cluster_snapshot_identifier=db_cluster_snapshot_identifier,
                attribute_name=params["AttributeName"],
                values_to_add=params.get("ValuesToAdd"),
                values_to_remove=params.get("ValuesToRemove"),
            )
        )
        result = {
            "DBClusterSnapshotAttributesResult": {
                "DBClusterSnapshotIdentifier": db_cluster_snapshot_identifier,
                "DBClusterSnapshotAttributes": [
                    {"AttributeName": name, "AttributeValues": values}
                    for name, values in db_cluster_snapshot_attributes_result.items()
                ],
            }
        }
        return ActionResult(result)

    def describe_db_proxies(self) -> ActionResult:
        params = self.params
        db_proxy_name = params.get("DBProxyName")
        # filters = params.get("Filters")
        marker = params.get("Marker")
        db_proxies = self.backend.describe_db_proxies(
            db_proxy_name=db_proxy_name,
            # filters=filters,
        )
        result = {
            "DBProxies": db_proxies,
            "Marker": marker,
        }
        return ActionResult(result)

    def create_db_proxy(self) -> ActionResult:
        params = self.params
        db_proxy_name = params["DBProxyName"]
        engine_family = params["EngineFamily"]
        auth = params["Auth"]
        role_arn = params["RoleArn"]
        vpc_subnet_ids = params["VpcSubnetIds"]
        vpc_security_group_ids = params.get("VpcSecurityGroupIds")
        require_tls = params.get("RequireTLS")
        idle_client_timeout = params.get("IdleClientTimeout")
        debug_logging = params.get("DebugLogging")
        tags = self.params.get("Tags", [])
        db_proxy = self.backend.create_db_proxy(
            db_proxy_name=db_proxy_name,
            engine_family=engine_family,
            auth=auth,
            role_arn=role_arn,
            vpc_subnet_ids=vpc_subnet_ids,
            vpc_security_group_ids=vpc_security_group_ids,
            require_tls=require_tls,
            idle_client_timeout=idle_client_timeout,
            debug_logging=debug_logging,
            tags=tags,
        )
        result = {"DBProxy": db_proxy}
        return ActionResult(result)

    def register_db_proxy_targets(self) -> ActionResult:
        db_proxy_name = self.params.get("DBProxyName")
        target_group_name = self.params.get("TargetGroupName")
        db_cluster_identifiers = self.params.get("DBClusterIdentifiers", [])
        db_instance_identifiers = self.params.get("DBInstanceIdentifiers", [])
        targets = self.backend.register_db_proxy_targets(
            db_proxy_name=db_proxy_name,
            target_group_name=target_group_name,
            db_cluster_identifiers=db_cluster_identifiers,
            db_instance_identifiers=db_instance_identifiers,
        )
        result = {"DBProxyTargets": targets}
        return ActionResult(result)

    def deregister_db_proxy_targets(self) -> ActionResult:
        db_proxy_name = self.params.get("DBProxyName")
        target_group_name = self.params.get("TargetGroupName")
        db_cluster_identifiers = self.params.get("DBClusterIdentifiers", [])
        db_instance_identifiers = self.params.get("DBInstanceIdentifiers", [])
        self.backend.deregister_db_proxy_targets(
            db_proxy_name=db_proxy_name,
            target_group_name=target_group_name,
            db_cluster_identifiers=db_cluster_identifiers,
            db_instance_identifiers=db_instance_identifiers,
        )
        return EmptyResult()

    def describe_db_proxy_targets(self) -> ActionResult:
        proxy_name = self.params.get("DBProxyName")
        targets = self.backend.describe_db_proxy_targets(proxy_name=proxy_name)
        result = {"Targets": targets}
        return ActionResult(result)

    def delete_db_proxy(self) -> ActionResult:
        proxy_name = self.params.get("DBProxyName")
        proxy = self.backend.delete_db_proxy(proxy_name=proxy_name)
        result = {"DBProxy": proxy}
        return ActionResult(result)

    def describe_db_proxy_target_groups(self) -> ActionResult:
        proxy_name = self.params.get("DBProxyName")
        groups = self.backend.describe_db_proxy_target_groups(proxy_name=proxy_name)
        result = {"TargetGroups": groups}
        return ActionResult(result)

    def modify_db_proxy_target_group(self) -> ActionResult:
        proxy_name = self.params.get("DBProxyName")
        config = self.params.get("ConnectionPoolConfig", {})
        group = self.backend.modify_db_proxy_target_group(
            proxy_name=proxy_name, config=config
        )
        result = {"DBProxyTargetGroup": group}
        return ActionResult(result)

    def describe_db_instance_automated_backups(self) -> ActionResult:
        automated_backups = self.backend.describe_db_instance_automated_backups(
            **self.params
        )
        result = {"DBInstanceAutomatedBackups": automated_backups}
        return ActionResult(result)

    def describe_events(self) -> ActionResult:
        events = self.backend.describe_events(**self.params)
        result = {"Events": events}
        return ActionResult(result)

    def describe_db_log_files(self) -> ActionResult:
        log_files = self.backend.describe_db_log_files(**self.params)
        result = {"DescribeDBLogFiles": log_files}
        return ActionResult(result)

    def create_blue_green_deployment(self) -> ActionResult:
        bg_kwargs = self.params
        bg_deployment = self.backend.create_blue_green_deployment(bg_kwargs)
        result = {"BlueGreenDeployment": bg_deployment}
        return ActionResult(result)

    def describe_blue_green_deployments(self) -> ActionResult:
        filters = self.params.get("Filters", [])
        filter_dict = {f["Name"]: f["Values"] for f in filters}
        self.params["filters"] = filter_dict
        bg_deployments = self.backend.describe_blue_green_deployments(**self.params)
        result = {"BlueGreenDeployments": bg_deployments}
        return PaginatedResult(result)

    def switchover_blue_green_deployment(self) -> ActionResult:
        bg_deployment = self.backend.switchover_blue_green_deployment(**self.params)
        result = {"BlueGreenDeployment": bg_deployment}
        return ActionResult(result)

    def delete_blue_green_deployment(self) -> ActionResult:
        bg_deployment = self.backend.delete_blue_green_deployment(**self.params)
        result = {"BlueGreenDeployment": bg_deployment}
        return ActionResult(result)

    def describe_account_attributes(self) -> ActionResult:
        quotas = self.backend.describe_account_attributes()
        result = {"AccountQuotas": quotas}
        return ActionResult(result)

    def describe_certificates(self) -> ActionResult:
        certificate_identifier = self.params.get("CertificateIdentifier")
        certs = self.backend.describe_certificates(
            certificate_identifier=certificate_identifier,
        )
        result = {
            "Certificates": certs,
            "DefaultCertificateForNewLaunches": "rds-ca-rsa2048-g1",
        }
        return ActionResult(result)

    def create_db_cluster_endpoint(self) -> ActionResult:
        params = self.params
        endpoint = self.backend.create_db_cluster_endpoint(
            db_cluster_identifier=params["DBClusterIdentifier"],
            db_cluster_endpoint_identifier=params["DBClusterEndpointIdentifier"],
            endpoint_type=params.get("EndpointType", "CUSTOM"),
            static_members=params.get("StaticMembers"),
            excluded_members=params.get("ExcludedMembers"),
            tags=params.get("Tags", []),
        )
        return ActionResult(endpoint)

    def describe_db_cluster_endpoints(self) -> ActionResult:
        params = self.params
        filters = params.get("Filters", [])
        filter_dict = {f["Name"]: f["Values"] for f in filters}
        endpoints = self.backend.describe_db_cluster_endpoints(
            db_cluster_identifier=params.get("DBClusterIdentifier"),
            db_cluster_endpoint_identifier=params.get("DBClusterEndpointIdentifier"),
            filters=filter_dict,
        )
        result = {"DBClusterEndpoints": endpoints}
        return ActionResult(result)

    def modify_db_cluster_endpoint(self) -> ActionResult:
        params = self.params
        endpoint = self.backend.modify_db_cluster_endpoint(
            db_cluster_endpoint_identifier=params["DBClusterEndpointIdentifier"],
            endpoint_type=params.get("EndpointType"),
            static_members=params.get("StaticMembers"),
            excluded_members=params.get("ExcludedMembers"),
        )
        return ActionResult(endpoint)

    def delete_db_cluster_endpoint(self) -> ActionResult:
        endpoint = self.backend.delete_db_cluster_endpoint(
            db_cluster_endpoint_identifier=self.params["DBClusterEndpointIdentifier"],
        )
        return ActionResult(endpoint)

    def create_db_proxy_endpoint(self) -> ActionResult:
        params = self.params
        endpoint = self.backend.create_db_proxy_endpoint(
            db_proxy_name=params["DBProxyName"],
            db_proxy_endpoint_name=params["DBProxyEndpointName"],
            vpc_subnet_ids=params["VpcSubnetIds"],
            vpc_security_group_ids=params.get("VpcSecurityGroupIds"),
            target_role=params.get("TargetRole", "READ_WRITE"),
            tags=params.get("Tags", []),
        )
        result = {"DBProxyEndpoint": endpoint}
        return ActionResult(result)

    def describe_db_proxy_endpoints(self) -> ActionResult:
        params = self.params
        endpoints = self.backend.describe_db_proxy_endpoints(
            db_proxy_name=params.get("DBProxyName"),
            db_proxy_endpoint_name=params.get("DBProxyEndpointName"),
        )
        result = {"DBProxyEndpoints": endpoints}
        return ActionResult(result)

    def delete_db_proxy_endpoint(self) -> ActionResult:
        endpoint = self.backend.delete_db_proxy_endpoint(
            db_proxy_endpoint_name=self.params["DBProxyEndpointName"],
        )
        result = {"DBProxyEndpoint": endpoint}
        return ActionResult(result)

    def delete_db_instance_automated_backup(self) -> ActionResult:
        backup = self.backend.delete_db_instance_automated_backup(
            dbi_resource_id=self.params.get("DbiResourceId"),
            db_instance_automated_backups_arn=self.params.get(
                "DBInstanceAutomatedBackupsArn"
            ),
        )
        result = {"DBInstanceAutomatedBackup": backup}
        return ActionResult(result)

    def describe_db_cluster_automated_backups(self) -> ActionResult:
        backups = self.backend.describe_db_cluster_automated_backups(
            db_cluster_identifier=self.params.get("DBClusterIdentifier"),
        )
        result = {"DBClusterAutomatedBackups": backups}
        return ActionResult(result)

    def copy_option_group(self) -> ActionResult:
        params = self.params
        option_group = self.backend.copy_option_group(
            source_option_group_identifier=params["SourceOptionGroupIdentifier"],
            target_option_group_identifier=params["TargetOptionGroupIdentifier"],
            target_option_group_description=params["TargetOptionGroupDescription"],
            tags=params.get("Tags", []),
        )
        result = {"OptionGroup": option_group}
        return ActionResult(result)

    def add_role_to_db_instance(self) -> ActionResult:
        db_instance_identifier = self.params.get("DBInstanceIdentifier")
        role_arn = self.params.get("RoleArn")
        feature_name = self.params.get("FeatureName")
        self.backend.add_role_to_db_instance(
            db_instance_identifier=db_instance_identifier,
            role_arn=role_arn,
            feature_name=feature_name,
        )
        return EmptyResult()

    def add_role_to_db_cluster(self) -> ActionResult:
        db_cluster_identifier = self.params.get("DBClusterIdentifier")
        role_arn = self.params.get("RoleArn")
        feature_name = self.params.get("FeatureName")
        self.backend.add_role_to_db_cluster(
            db_cluster_identifier=db_cluster_identifier,
            role_arn=role_arn,
            feature_name=feature_name,
        )
        return EmptyResult()

    # ---- CustomDBEngineVersion ----

    def create_custom_db_engine_version(self) -> ActionResult:
        cev = self.backend.create_custom_db_engine_version(self.params)
        return ActionResult(
            {
                "Engine": cev.engine,
                "EngineVersion": cev.engine_version,
                "DBEngineDescription": cev.db_engine_description,
                "DBEngineVersionDescription": cev.db_engine_version_description,
                "DBEngineVersionArn": cev.db_engine_version_arn,
                "Status": cev.status,
                "CreateTime": cev.create_time.isoformat(),
                "DatabaseInstallationFilesS3BucketName": cev.database_installation_files_s3_bucket_name,
                "DatabaseInstallationFilesS3Prefix": cev.database_installation_files_s3_prefix,
                "KMSKeyId": cev.kms_key_id,
                "MajorEngineVersion": cev.major_engine_version,
                "SupportedEngineModes": cev.supported_engine_modes,
                "SupportsParallelQuery": cev.supports_parallel_query,
                "SupportsGlobalDatabases": cev.supports_global_databases,
                "Tags": cev.tags,
            }
        )

    def delete_custom_db_engine_version(self) -> ActionResult:
        engine = self.params["Engine"]
        engine_version = self.params["EngineVersion"]
        cev = self.backend.delete_custom_db_engine_version(engine, engine_version)
        return ActionResult(
            {
                "Engine": cev.engine,
                "EngineVersion": cev.engine_version,
                "DBEngineDescription": cev.db_engine_description,
                "DBEngineVersionDescription": cev.db_engine_version_description,
                "DBEngineVersionArn": cev.db_engine_version_arn,
                "Status": cev.status,
                "CreateTime": cev.create_time.isoformat(),
                "MajorEngineVersion": cev.major_engine_version,
                "Tags": cev.tags,
            }
        )

    def modify_custom_db_engine_version(self) -> ActionResult:
        engine = self.params["Engine"]
        engine_version = self.params["EngineVersion"]
        description = self.params.get("Description")
        status = self.params.get("Status")
        cev = self.backend.modify_custom_db_engine_version(
            engine, engine_version, description=description, status=status
        )
        return ActionResult(
            {
                "Engine": cev.engine,
                "EngineVersion": cev.engine_version,
                "DBEngineDescription": cev.db_engine_description,
                "DBEngineVersionDescription": cev.db_engine_version_description,
                "DBEngineVersionArn": cev.db_engine_version_arn,
                "Status": cev.status,
                "CreateTime": cev.create_time.isoformat(),
                "MajorEngineVersion": cev.major_engine_version,
                "Tags": cev.tags,
            }
        )

    # ---- Integration (zero-ETL) ----

    def create_integration(self) -> ActionResult:
        integration = self.backend.create_integration(self.params)
        return ActionResult(
            {
                "IntegrationArn": integration.integration_arn,
                "IntegrationName": integration.integration_name,
                "SourceArn": integration.source_arn,
                "TargetArn": integration.target_arn,
                "KMSKeyId": integration.kms_key_id,
                "AdditionalEncryptionContext": integration.additional_encryption_context,
                "Description": integration.description,
                "DataFilter": integration.data_filter,
                "Status": integration.status,
                "CreateTime": integration.create_time.isoformat(),
                "Errors": integration.errors,
                "Tags": integration.tags,
            }
        )

    def delete_integration(self) -> ActionResult:
        integration_identifier = self.params["IntegrationIdentifier"]
        integration = self.backend.delete_integration(integration_identifier)
        return ActionResult(
            {
                "IntegrationArn": integration.integration_arn,
                "IntegrationName": integration.integration_name,
                "SourceArn": integration.source_arn,
                "TargetArn": integration.target_arn,
                "Status": integration.status,
                "CreateTime": integration.create_time.isoformat(),
                "Tags": integration.tags,
            }
        )

    def describe_integrations(self) -> ActionResult:
        integration_identifier = self.params.get("IntegrationIdentifier")
        integration_name = self.params.get("IntegrationName")
        integrations = self.backend.describe_integrations(
            integration_identifier=integration_identifier,
            integration_name=integration_name,
        )
        results = []
        for i in integrations:
            results.append(
                {
                    "IntegrationArn": i.integration_arn,
                    "IntegrationName": i.integration_name,
                    "SourceArn": i.source_arn,
                    "TargetArn": i.target_arn,
                    "KMSKeyId": i.kms_key_id,
                    "AdditionalEncryptionContext": i.additional_encryption_context,
                    "Description": i.description,
                    "DataFilter": i.data_filter,
                    "Status": i.status,
                    "CreateTime": i.create_time.isoformat(),
                    "Errors": i.errors,
                    "Tags": i.tags,
                }
            )
        return ActionResult({"Integrations": results})

    def modify_integration(self) -> ActionResult:
        integration_identifier = self.params["IntegrationIdentifier"]
        integration_name = self.params.get("IntegrationName")
        description = self.params.get("Description")
        data_filter = self.params.get("DataFilter")
        integration = self.backend.modify_integration(
            integration_identifier,
            integration_name=integration_name,
            description=description,
            data_filter=data_filter,
        )
        return ActionResult(
            {
                "IntegrationArn": integration.integration_arn,
                "IntegrationName": integration.integration_name,
                "SourceArn": integration.source_arn,
                "TargetArn": integration.target_arn,
                "KMSKeyId": integration.kms_key_id,
                "Description": integration.description,
                "DataFilter": integration.data_filter,
                "Status": integration.status,
                "CreateTime": integration.create_time.isoformat(),
                "Tags": integration.tags,
            }
        )

    # ---- TenantDatabase ----

    def create_tenant_database(self) -> ActionResult:
        tenant_db = self.backend.create_tenant_database(self.params)
        return ActionResult({"TenantDatabase": _tenant_db_dict(tenant_db)})

    def delete_tenant_database(self) -> ActionResult:
        db_instance_identifier = self.params["DBInstanceIdentifier"]
        tenant_db_name = self.params["TenantDBName"]
        final_snapshot = self.params.get("FinalDBSnapshotIdentifier")
        tenant_db = self.backend.delete_tenant_database(
            db_instance_identifier, tenant_db_name, final_snapshot
        )
        return ActionResult({"TenantDatabase": _tenant_db_dict(tenant_db)})

    def describe_tenant_databases(self) -> ActionResult:
        db_instance_identifier = self.params.get("DBInstanceIdentifier")
        tenant_db_name = self.params.get("TenantDBName")
        tenant_dbs = self.backend.describe_tenant_databases(
            db_instance_identifier=db_instance_identifier,
            tenant_db_name=tenant_db_name,
        )
        result = {"TenantDatabases": [_tenant_db_dict(t) for t in tenant_dbs]}
        return PaginatedResult(result)

    def modify_tenant_database(self) -> ActionResult:
        db_instance_identifier = self.params["DBInstanceIdentifier"]
        tenant_db_name = self.params["TenantDBName"]
        master_user_password = self.params.get("MasterUserPassword")
        new_tenant_db_name = self.params.get("NewTenantDBName")
        tenant_db = self.backend.modify_tenant_database(
            db_instance_identifier,
            tenant_db_name,
            master_user_password=master_user_password,
            new_tenant_db_name=new_tenant_db_name,
        )
        return ActionResult({"TenantDatabase": _tenant_db_dict(tenant_db)})

    def describe_db_snapshot_tenant_databases(self) -> ActionResult:
        db_snapshot_identifier = self.params.get("DBSnapshotIdentifier")
        db_instance_identifier = self.params.get("DBInstanceIdentifier")
        dbi_resource_id = self.params.get("DbiResourceId")
        snapshot_type = self.params.get("SnapshotType")
        results = self.backend.describe_db_snapshot_tenant_databases(
            db_snapshot_identifier=db_snapshot_identifier,
            db_instance_identifier=db_instance_identifier,
            dbi_resource_id=dbi_resource_id,
            snapshot_type=snapshot_type,
        )
        return ActionResult({"DBSnapshotTenantDatabases": results})

    # ---- ActivityStream ----

    def start_activity_stream(self) -> ActionResult:
        resource_arn = self.params["ResourceArn"]
        mode = self.params.get("Mode")
        kms_key_id = self.params.get("KmsKeyId")
        apply_immediately = self.params.get("ApplyImmediately", True)
        engine_native = self.params.get("EngineNativeAuditFieldsIncluded", False)
        result = self.backend.start_activity_stream(
            resource_arn,
            mode=mode,
            kms_key_id=kms_key_id,
            apply_immediately=apply_immediately,
            engine_native_audit_fields_included=engine_native,
        )
        return ActionResult(result)

    def stop_activity_stream(self) -> ActionResult:
        resource_arn = self.params["ResourceArn"]
        apply_immediately = self.params.get("ApplyImmediately", True)
        result = self.backend.stop_activity_stream(
            resource_arn, apply_immediately=apply_immediately
        )
        return ActionResult(result)

    def modify_activity_stream(self) -> ActionResult:
        resource_arn = self.params.get("ResourceArn")
        audit_policy_state = self.params.get("AuditPolicyState")
        result = self.backend.modify_activity_stream(
            resource_arn=resource_arn,
            audit_policy_state=audit_policy_state,
        )
        return ActionResult(result)

    # ---- DBShardGroup (delete/modify/reboot) ----

    def delete_db_shard_group(self) -> ActionResult:
        db_shard_group_identifier = self.params["DBShardGroupIdentifier"]
        shard_group = self.backend.delete_db_shard_group(db_shard_group_identifier)
        return ActionResult(shard_group)

    def modify_db_shard_group(self) -> ActionResult:
        db_shard_group_identifier = self.params["DBShardGroupIdentifier"]
        max_acu = self.params.get("MaxACU")
        min_acu = self.params.get("MinACU")
        compute_redundancy = self.params.get("ComputeRedundancy")
        shard_group = self.backend.modify_db_shard_group(
            db_shard_group_identifier,
            max_acu=max_acu,
            min_acu=min_acu,
            compute_redundancy=compute_redundancy,
        )
        return ActionResult(shard_group)

    def reboot_db_shard_group(self) -> ActionResult:
        db_shard_group_identifier = self.params["DBShardGroupIdentifier"]
        shard_group = self.backend.reboot_db_shard_group(db_shard_group_identifier)
        return ActionResult(shard_group)

    # ---- ReservedDBInstances ----

    def describe_reserved_db_instances_offerings(self) -> ActionResult:
        offering_id = self.params.get("ReservedDBInstancesOfferingId")
        db_instance_class = self.params.get("DBInstanceClass")
        duration = self.params.get("Duration")
        product_description = self.params.get("ProductDescription")
        offering_type = self.params.get("OfferingType")
        multi_az = self.params.get("MultiAZ")
        offerings = self.backend.describe_reserved_db_instances_offerings(
            reserved_db_instances_offering_id=offering_id,
            db_instance_class=db_instance_class,
            duration=duration,
            product_description=product_description,
            offering_type=offering_type,
            multi_az=multi_az,
        )
        results = []
        for o in offerings:
            results.append(
                {
                    "ReservedDBInstancesOfferingId": o.reserved_db_instances_offering_id,
                    "DBInstanceClass": o.db_instance_class,
                    "Duration": o.duration,
                    "FixedPrice": o.fixed_price,
                    "UsagePrice": o.usage_price,
                    "CurrencyCode": o.currency_code,
                    "ProductDescription": o.product_description,
                    "OfferingType": o.offering_type,
                    "MultiAZ": o.multi_az,
                    "RecurringCharges": o.recurring_charges,
                }
            )
        return ActionResult({"ReservedDBInstancesOfferings": results})

    def purchase_reserved_db_instances_offering(self) -> ActionResult:
        offering_id = self.params["ReservedDBInstancesOfferingId"]
        reserved_id = self.params.get("ReservedDBInstanceId")
        count = self.params.get("DBInstanceCount", 1)
        tags = self.params.get("Tags", [])
        reserved = self.backend.purchase_reserved_db_instances_offering(
            reserved_db_instances_offering_id=offering_id,
            reserved_db_instance_id=reserved_id,
            db_instance_count=count,
            tags=tags,
        )
        return ActionResult({"ReservedDBInstance": _reserved_db_dict(reserved)})

    def describe_reserved_db_instances(self) -> ActionResult:
        reserved_id = self.params.get("ReservedDBInstanceId")
        offering_id = self.params.get("ReservedDBInstancesOfferingId")
        db_instance_class = self.params.get("DBInstanceClass")
        duration = self.params.get("Duration")
        product_description = self.params.get("ProductDescription")
        offering_type = self.params.get("OfferingType")
        multi_az = self.params.get("MultiAZ")
        results = self.backend.describe_reserved_db_instances(
            reserved_db_instance_id=reserved_id,
            reserved_db_instances_offering_id=offering_id,
            db_instance_class=db_instance_class,
            duration=duration,
            product_description=product_description,
            offering_type=offering_type,
            multi_az=multi_az,
        )
        return ActionResult(
            {
                "ReservedDBInstances": [_reserved_db_dict(r) for r in results],
            }
        )

    # ---- DBRecommendation ----

    def describe_db_recommendations(self) -> ActionResult:
        last_updated_after = self.params.get("LastUpdatedAfter")
        last_updated_before = self.params.get("LastUpdatedBefore")
        locale = self.params.get("Locale")
        recommendations = self.backend.describe_db_recommendations(
            last_updated_after=last_updated_after,
            last_updated_before=last_updated_before,
            locale=locale,
        )
        return ActionResult({"DBRecommendations": recommendations})

    def remove_role_from_db_cluster(self) -> ActionResult:
        db_cluster_identifier = self.params.get("DBClusterIdentifier")
        role_arn = self.params.get("RoleArn")
        feature_name = self.params.get("FeatureName")
        self.backend.remove_role_from_db_cluster(
            db_cluster_identifier=db_cluster_identifier,
            role_arn=role_arn,
            feature_name=feature_name,
        )
        return EmptyResult()

    def reboot_db_cluster(self) -> ActionResult:
        db_cluster_identifier = self.params.get("DBClusterIdentifier")
        cluster = self.backend.reboot_db_cluster(db_cluster_identifier)
        result = {"DBCluster": cluster}
        return ActionResult(result)

    def reset_db_parameter_group(self) -> ActionResult:
        db_parameter_group_name = self.params.get("DBParameterGroupName")
        group = self.backend.reset_db_parameter_group(db_parameter_group_name)
        result = {"DBParameterGroupName": group.name}
        return ActionResult(result)

    def reset_db_cluster_parameter_group(self) -> ActionResult:
        db_cluster_parameter_group_name = self.params.get("DBClusterParameterGroupName")
        group = self.backend.reset_db_cluster_parameter_group(db_cluster_parameter_group_name)
        result = {"DBClusterParameterGroupName": group.name}
        return ActionResult(result)

    def describe_source_regions(self) -> ActionResult:
        regions = self.backend.describe_source_regions()
        result = {"SourceRegions": regions}
        return ActionResult(result)

    def describe_db_major_engine_versions(self) -> ActionResult:
        versions = self.backend.describe_db_major_engine_versions()
        result = {"DBMajorEngineVersions": versions}
        return ActionResult(result)

    def disable_http_endpoint(self) -> ActionResult:
        resource_arn = self.params.get("ResourceArn", "")
        result = self.backend.disable_http_endpoint(resource_arn=resource_arn)
        return ActionResult(result)

    def enable_http_endpoint(self) -> ActionResult:
        resource_arn = self.params.get("ResourceArn", "")
        result = self.backend.enable_http_endpoint(resource_arn=resource_arn)
        return ActionResult(result)

    def modify_certificates(self) -> ActionResult:
        certificate_identifier = self.params.get("CertificateIdentifier")
        remove_customer_override = self.params.get("RemoveCustomerOverride")
        result = self.backend.modify_certificates(
            certificate_identifier=certificate_identifier,
            remove_customer_override=remove_customer_override,
        )
        return ActionResult(result)


def _tenant_db_dict(tenant_db: Any) -> dict:
    return {
        "DBInstanceIdentifier": tenant_db.db_instance_identifier,
        "TenantDBName": tenant_db.tenant_db_name,
        "MasterUsername": tenant_db.master_username,
        "CharacterSetName": tenant_db.character_set_name,
        "NcharCharacterSetName": tenant_db.nchar_character_set_name,
        "Status": tenant_db.status,
        "TenantDatabaseCreateTime": tenant_db.create_time.isoformat(),
        "TenantDatabaseResourceId": tenant_db.tenant_database_resource_id,
        "TenantDatabaseARN": tenant_db.tenant_database_arn,
        "DbiResourceId": tenant_db.dbi_resource_id,
    }


def _reserved_db_dict(reserved: Any) -> dict:
    return {
        "ReservedDBInstanceId": reserved.reserved_db_instance_id,
        "ReservedDBInstancesOfferingId": reserved.reserved_db_instances_offering_id,
        "DBInstanceClass": reserved.db_instance_class,
        "Duration": reserved.duration,
        "FixedPrice": reserved.fixed_price,
        "UsagePrice": reserved.usage_price,
        "CurrencyCode": reserved.currency_code,
        "ProductDescription": reserved.product_description,
        "OfferingType": reserved.offering_type,
        "MultiAZ": reserved.multi_az,
        "RecurringCharges": reserved.recurring_charges,
        "DBInstanceCount": reserved.db_instance_count,
        "State": reserved.state,
        "StartTime": reserved.start_time.isoformat(),
        "ReservedDBInstanceArn": reserved.reserved_db_instance_arn,
    }
