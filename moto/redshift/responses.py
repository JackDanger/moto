from moto.core.responses import ActionResult, BaseResponse, EmptyResult

from .models import RedshiftBackend, redshift_backends


class RedshiftResponse(BaseResponse):
    RESPONSE_KEY_PATH_TO_TRANSFORMER = {
        "CreateClusterResult.Cluster.ClusterStatus": lambda _: "creating",
        "RestoreFromClusterSnapshotResult.Cluster.ClusterStatus": lambda _: "creating",
    }

    def __init__(self) -> None:
        super().__init__(service_name="redshift")
        self.automated_parameter_parsing = True

    @property
    def redshift_backend(self) -> RedshiftBackend:
        return redshift_backends[self.current_account][self.region]

    def create_cluster(self) -> ActionResult:
        cluster_kwargs = {
            "cluster_identifier": self._get_param("ClusterIdentifier"),
            "node_type": self._get_param("NodeType"),
            "master_username": self._get_param("MasterUsername"),
            "master_user_password": self._get_param("MasterUserPassword"),
            "db_name": self._get_param("DBName"),
            "cluster_type": self._get_param("ClusterType"),
            "cluster_security_groups": self._get_param("ClusterSecurityGroups", []),
            "vpc_security_group_ids": self._get_param("VpcSecurityGroupIds", []),
            "cluster_subnet_group_name": self._get_param("ClusterSubnetGroupName"),
            "availability_zone": self._get_param("AvailabilityZone"),
            "preferred_maintenance_window": self._get_param(
                "PreferredMaintenanceWindow"
            ),
            "cluster_parameter_group_name": self._get_param(
                "ClusterParameterGroupName"
            ),
            "automated_snapshot_retention_period": self._get_int_param(
                "AutomatedSnapshotRetentionPeriod"
            ),
            "port": self._get_int_param("Port"),
            "cluster_version": self._get_param("ClusterVersion"),
            "allow_version_upgrade": self._get_bool_param("AllowVersionUpgrade", True),
            "number_of_nodes": self._get_int_param("NumberOfNodes"),
            "publicly_accessible": self._get_bool_param("PubliclyAccessible", False),
            "encrypted": self._get_bool_param("Encrypted", False),
            "region_name": self.region,
            "tags": self._get_param("Tags", []),
            "iam_roles_arn": self._get_param("IamRoles", []),
            "enhanced_vpc_routing": self._get_bool_param("EnhancedVpcRouting", False),
            "kms_key_id": self._get_param("KmsKeyId"),
        }
        cluster = self.redshift_backend.create_cluster(**cluster_kwargs)
        return ActionResult({"Cluster": cluster})

    def pause_cluster(self) -> ActionResult:
        cluster_id = self._get_param("ClusterIdentifier")
        cluster = self.redshift_backend.pause_cluster(cluster_id)
        return ActionResult({"Cluster": cluster})

    def resume_cluster(self) -> ActionResult:
        cluster_id = self._get_param("ClusterIdentifier")
        cluster = self.redshift_backend.resume_cluster(cluster_id)
        return ActionResult({"Cluster": cluster})

    def restore_from_cluster_snapshot(self) -> ActionResult:
        enhanced_vpc_routing = self._get_bool_param("EnhancedVpcRouting")
        node_type = self._get_param("NodeType")
        number_of_nodes = self._get_int_param("NumberOfNodes")
        restore_kwargs = {
            "snapshot_identifier": self._get_param("SnapshotIdentifier"),
            "cluster_identifier": self._get_param("ClusterIdentifier"),
            "port": self._get_int_param("Port"),
            "availability_zone": self._get_param("AvailabilityZone"),
            "allow_version_upgrade": self._get_bool_param("AllowVersionUpgrade"),
            "cluster_subnet_group_name": self._get_param("ClusterSubnetGroupName"),
            "publicly_accessible": self._get_param("PubliclyAccessible"),
            "cluster_parameter_group_name": self._get_param(
                "ClusterParameterGroupName"
            ),
            "cluster_security_groups": self._get_param("ClusterSecurityGroups", []),
            "vpc_security_group_ids": self._get_param("VpcSecurityGroupIds", []),
            "preferred_maintenance_window": self._get_param(
                "PreferredMaintenanceWindow"
            ),
            "automated_snapshot_retention_period": self._get_int_param(
                "AutomatedSnapshotRetentionPeriod"
            ),
            "region_name": self.region,
            "iam_roles_arn": self._get_param("IamRoles", []),
        }
        if enhanced_vpc_routing is not None:
            restore_kwargs["enhanced_vpc_routing"] = enhanced_vpc_routing
        if node_type is not None:
            restore_kwargs["node_type"] = node_type
        if number_of_nodes is not None:
            restore_kwargs["number_of_nodes"] = number_of_nodes
        cluster = self.redshift_backend.restore_from_cluster_snapshot(**restore_kwargs)
        return ActionResult({"Cluster": cluster})

    def describe_clusters(self) -> ActionResult:
        cluster_identifier = self._get_param("ClusterIdentifier")
        tag_keys = self._get_param("TagKeys")
        clusters = self.redshift_backend.describe_clusters(cluster_identifier, tag_keys)

        return ActionResult({"Clusters": clusters})

    def modify_cluster(self) -> ActionResult:
        request_kwargs = {
            "cluster_identifier": self._get_param("ClusterIdentifier"),
            "new_cluster_identifier": self._get_param("NewClusterIdentifier"),
            "node_type": self._get_param("NodeType"),
            "master_user_password": self._get_param("MasterUserPassword"),
            "cluster_type": self._get_param("ClusterType"),
            "cluster_security_groups": self._get_param("ClusterSecurityGroups", []),
            "vpc_security_group_ids": self._get_param("VpcSecurityGroupIds", []),
            "cluster_subnet_group_name": self._get_param("ClusterSubnetGroupName"),
            "preferred_maintenance_window": self._get_param(
                "PreferredMaintenanceWindow"
            ),
            "cluster_parameter_group_name": self._get_param(
                "ClusterParameterGroupName"
            ),
            "automated_snapshot_retention_period": self._get_int_param(
                "AutomatedSnapshotRetentionPeriod"
            ),
            "cluster_version": self._get_param("ClusterVersion"),
            "allow_version_upgrade": self._get_bool_param("AllowVersionUpgrade"),
            "number_of_nodes": self._get_int_param("NumberOfNodes"),
            "publicly_accessible": self._get_param("PubliclyAccessible"),
            "encrypted": self._get_param("Encrypted"),
            "iam_roles_arn": self._get_param("IamRoles", []),
            "enhanced_vpc_routing": self._get_param("EnhancedVpcRouting"),
        }
        cluster_kwargs = {}
        # We only want parameters that were actually passed in, otherwise
        # we'll stomp all over our cluster metadata with None values.
        for key, value in request_kwargs.items():
            if value is not None and value != []:
                cluster_kwargs[key] = value

        cluster = self.redshift_backend.modify_cluster(**cluster_kwargs)

        return ActionResult({"Cluster": cluster})

    def delete_cluster(self) -> ActionResult:
        request_kwargs = {
            "cluster_identifier": self._get_param("ClusterIdentifier"),
            "final_cluster_snapshot_identifier": self._get_param(
                "FinalClusterSnapshotIdentifier"
            ),
            "skip_final_snapshot": self._get_bool_param("SkipFinalClusterSnapshot"),
        }

        cluster = self.redshift_backend.delete_cluster(**request_kwargs)

        return ActionResult({"Cluster": cluster})

    def create_cluster_subnet_group(self) -> ActionResult:
        cluster_subnet_group_name = self._get_param("ClusterSubnetGroupName")
        description = self._get_param("Description")
        subnet_ids = self._get_param("SubnetIds", [])
        tags = self._get_param("Tags", [])

        subnet_group = self.redshift_backend.create_cluster_subnet_group(
            cluster_subnet_group_name=cluster_subnet_group_name,
            description=description,
            subnet_ids=subnet_ids,
            region_name=self.region,
            tags=tags,
        )

        return ActionResult({"ClusterSubnetGroup": subnet_group})

    def describe_cluster_subnet_groups(self) -> ActionResult:
        subnet_identifier = self._get_param("ClusterSubnetGroupName")
        subnet_groups = self.redshift_backend.describe_cluster_subnet_groups(
            subnet_identifier
        )

        return ActionResult({"ClusterSubnetGroups": subnet_groups})

    def delete_cluster_subnet_group(self) -> ActionResult:
        subnet_identifier = self._get_param("ClusterSubnetGroupName")
        self.redshift_backend.delete_cluster_subnet_group(subnet_identifier)

        return EmptyResult()

    def create_cluster_security_group(self) -> ActionResult:
        cluster_security_group_name = self._get_param("ClusterSecurityGroupName")
        description = self._get_param("Description")
        tags = self._get_param("Tags", [])

        security_group = self.redshift_backend.create_cluster_security_group(
            cluster_security_group_name=cluster_security_group_name,
            description=description,
            tags=tags,
        )

        return ActionResult({"ClusterSecurityGroup": security_group})

    def describe_cluster_security_groups(self) -> ActionResult:
        cluster_security_group_name = self._get_param("ClusterSecurityGroupName")
        security_groups = self.redshift_backend.describe_cluster_security_groups(
            cluster_security_group_name
        )

        return ActionResult({"ClusterSecurityGroups": security_groups})

    def delete_cluster_security_group(self) -> ActionResult:
        security_group_identifier = self._get_param("ClusterSecurityGroupName")
        self.redshift_backend.delete_cluster_security_group(security_group_identifier)

        return EmptyResult()

    def authorize_cluster_security_group_ingress(self) -> ActionResult:
        cluster_security_group_name = self._get_param("ClusterSecurityGroupName")
        cidr_ip = self._get_param("CIDRIP")

        security_group = self.redshift_backend.authorize_cluster_security_group_ingress(
            cluster_security_group_name, cidr_ip
        )
        result = {
            "ClusterSecurityGroup": {
                "ClusterSecurityGroupName": cluster_security_group_name,
                "Description": security_group.description,
                "IPRanges": [
                    {
                        "Status": "authorized",
                        "CIDRIP": cidr_ip,
                        "Tags": security_group.tags,
                    },
                ],
            }
        }
        return ActionResult(result)

    def create_cluster_parameter_group(self) -> ActionResult:
        cluster_parameter_group_name = self._get_param("ParameterGroupName")
        group_family = self._get_param("ParameterGroupFamily")
        description = self._get_param("Description")
        tags = self._get_param("Tags", [])

        parameter_group = self.redshift_backend.create_cluster_parameter_group(
            cluster_parameter_group_name, group_family, description, self.region, tags
        )

        return ActionResult({"ClusterParameterGroup": parameter_group})

    def describe_cluster_parameter_groups(self) -> ActionResult:
        cluster_parameter_group_name = self._get_param("ParameterGroupName")
        parameter_groups = self.redshift_backend.describe_cluster_parameter_groups(
            cluster_parameter_group_name
        )

        return ActionResult({"ParameterGroups": parameter_groups})

    def delete_cluster_parameter_group(self) -> ActionResult:
        cluster_parameter_group_name = self._get_param("ParameterGroupName")
        self.redshift_backend.delete_cluster_parameter_group(
            cluster_parameter_group_name
        )

        return EmptyResult()

    def describe_default_cluster_parameters(self) -> ActionResult:
        family = self._get_param("ParameterGroupFamily")
        params = self.redshift_backend.describe_default_cluster_parameters()
        return ActionResult(
            {
                "DefaultClusterParameters": {
                    "ParameterGroupFamily": family,
                    "Parameters": params,
                }
            }
        )

    def describe_cluster_parameters(self) -> ActionResult:
        group_name = self._get_param("ParameterGroupName")
        params = self.redshift_backend.describe_cluster_parameters(
            parameter_group_name=group_name
        )
        return ActionResult(
            {
                "Parameters": params,
            }
        )

    def create_cluster_snapshot(self) -> ActionResult:
        cluster_identifier = self._get_param("ClusterIdentifier")
        snapshot_identifier = self._get_param("SnapshotIdentifier")
        tags = self._get_param("Tags", [])

        snapshot = self.redshift_backend.create_cluster_snapshot(
            cluster_identifier, snapshot_identifier, self.region, tags
        )
        return ActionResult({"Snapshot": snapshot})

    def describe_cluster_snapshots(self) -> ActionResult:
        cluster_identifier = self._get_param("ClusterIdentifier")
        snapshot_identifier = self._get_param("SnapshotIdentifier")
        snapshot_type = self._get_param("SnapshotType")
        snapshots = self.redshift_backend.describe_cluster_snapshots(
            cluster_identifier, snapshot_identifier, snapshot_type
        )
        return ActionResult({"Snapshots": snapshots})

    def delete_cluster_snapshot(self) -> ActionResult:
        snapshot_identifier = self._get_param("SnapshotIdentifier")
        snapshot = self.redshift_backend.delete_cluster_snapshot(snapshot_identifier)

        return ActionResult({"Snapshot": snapshot})

    def create_snapshot_copy_grant(self) -> ActionResult:
        copy_grant_kwargs = {
            "snapshot_copy_grant_name": self._get_param("SnapshotCopyGrantName"),
            "kms_key_id": self._get_param("KmsKeyId"),
            "region_name": self._get_param("Region"),
        }

        copy_grant = self.redshift_backend.create_snapshot_copy_grant(
            **copy_grant_kwargs
        )
        return ActionResult({"SnapshotCopyGrant": copy_grant})

    def delete_snapshot_copy_grant(self) -> ActionResult:
        copy_grant_kwargs = {
            "snapshot_copy_grant_name": self._get_param("SnapshotCopyGrantName")
        }
        self.redshift_backend.delete_snapshot_copy_grant(**copy_grant_kwargs)
        return EmptyResult()

    def describe_snapshot_copy_grants(self) -> ActionResult:
        copy_grant_kwargs = {
            "snapshot_copy_grant_name": self._get_param("SnapshotCopyGrantName")
        }

        copy_grants = self.redshift_backend.describe_snapshot_copy_grants(
            **copy_grant_kwargs
        )
        return ActionResult({"SnapshotCopyGrants": copy_grants})

    def create_tags(self) -> ActionResult:
        resource_name = self._get_param("ResourceName")
        tags = self._get_param("Tags", [])

        self.redshift_backend.create_tags(resource_name, tags)

        return EmptyResult()

    def describe_tags(self) -> ActionResult:
        resource_name = self._get_param("ResourceName")
        resource_type = self._get_param("ResourceType")

        tagged_resources = self.redshift_backend.describe_tags(
            resource_name, resource_type
        )
        return ActionResult({"TaggedResources": tagged_resources})

    def delete_tags(self) -> ActionResult:
        resource_name = self._get_param("ResourceName")
        tag_keys = self._get_param("TagKeys", [])

        self.redshift_backend.delete_tags(resource_name, tag_keys)

        return EmptyResult()

    def enable_snapshot_copy(self) -> ActionResult:
        snapshot_copy_kwargs = {
            "cluster_identifier": self._get_param("ClusterIdentifier"),
            "destination_region": self._get_param("DestinationRegion"),
            "retention_period": self._get_param("RetentionPeriod", 7),
            "snapshot_copy_grant_name": self._get_param("SnapshotCopyGrantName"),
        }
        cluster = self.redshift_backend.enable_snapshot_copy(**snapshot_copy_kwargs)

        return ActionResult({"Cluster": cluster})

    def disable_snapshot_copy(self) -> ActionResult:
        snapshot_copy_kwargs = {
            "cluster_identifier": self._get_param("ClusterIdentifier")
        }
        cluster = self.redshift_backend.disable_snapshot_copy(**snapshot_copy_kwargs)

        return ActionResult({"Cluster": cluster})

    def modify_snapshot_copy_retention_period(self) -> ActionResult:
        snapshot_copy_kwargs = {
            "cluster_identifier": self._get_param("ClusterIdentifier"),
            "retention_period": self._get_param("RetentionPeriod"),
        }
        cluster = self.redshift_backend.modify_snapshot_copy_retention_period(
            **snapshot_copy_kwargs
        )

        return ActionResult({"Clusters": [cluster]})

    def get_cluster_credentials(self) -> ActionResult:
        cluster_identifier = self._get_param("ClusterIdentifier")
        db_user = self._get_param("DbUser")
        auto_create = self._get_bool_param("AutoCreate", False)
        duration_seconds = self._get_int_param("DurationSeconds", 900)

        cluster_credentials = self.redshift_backend.get_cluster_credentials(
            cluster_identifier, db_user, auto_create, duration_seconds
        )

        return ActionResult(cluster_credentials)

    def enable_logging(self) -> ActionResult:
        cluster_identifier = self._get_param("ClusterIdentifier")
        bucket_name = self._get_param("BucketName")
        s3_key_prefix = self._get_param("S3KeyPrefix")
        log_destination_type = self._get_param("LogDestinationType")
        log_exports = self._get_param("LogExports")
        config = self.redshift_backend.enable_logging(
            cluster_identifier=cluster_identifier,
            bucket_name=bucket_name,
            s3_key_prefix=s3_key_prefix,
            log_destination_type=log_destination_type,
            log_exports=log_exports,
        )
        return ActionResult(config)

    def disable_logging(self) -> ActionResult:
        cluster_identifier = self._get_param("ClusterIdentifier")
        config = self.redshift_backend.disable_logging(
            cluster_identifier=cluster_identifier,
        )
        return ActionResult(config)

    def describe_logging_status(self) -> ActionResult:
        cluster_identifier = self._get_param("ClusterIdentifier")
        config = self.redshift_backend.describe_logging_status(
            cluster_identifier=cluster_identifier,
        )
        return ActionResult(config)

    def create_snapshot_schedule(self) -> ActionResult:
        schedule_identifier = self._get_param("ScheduleIdentifier")
        schedule_definitions = self._get_param("ScheduleDefinitions", [])
        tags = self._get_param("Tags", [])
        schedule = self.redshift_backend.create_snapshot_schedule(
            schedule_identifier=schedule_identifier,
            schedule_definitions=schedule_definitions,
            tags=tags,
        )
        return ActionResult(schedule)

    def delete_snapshot_schedule(self) -> ActionResult:
        schedule_identifier = self._get_param("ScheduleIdentifier")
        self.redshift_backend.delete_snapshot_schedule(schedule_identifier)
        return EmptyResult()

    def modify_snapshot_schedule(self) -> ActionResult:
        schedule_identifier = self._get_param("ScheduleIdentifier")
        schedule_definitions = self._get_param("ScheduleDefinitions", [])
        schedule = self.redshift_backend.modify_snapshot_schedule(
            schedule_identifier=schedule_identifier,
            schedule_definitions=schedule_definitions,
        )
        return ActionResult(schedule)

    def describe_snapshot_schedules(self) -> ActionResult:
        schedule_identifier = self._get_param("ScheduleIdentifier")
        schedules = self.redshift_backend.describe_snapshot_schedules(
            schedule_identifier=schedule_identifier,
        )
        return ActionResult({"SnapshotSchedules": schedules})

    def describe_account_attributes(self) -> ActionResult:
        attributes = self.redshift_backend.describe_account_attributes()
        return ActionResult({"AccountAttributes": attributes})

    def describe_authentication_profiles(self) -> ActionResult:
        profile_name = self._get_param("AuthenticationProfileName")
        profiles = self.redshift_backend.describe_authentication_profiles(
            authentication_profile_name=profile_name,
        )
        return ActionResult({"AuthenticationProfiles": profiles})

    def describe_cluster_db_revisions(self) -> ActionResult:
        revisions = self.redshift_backend.describe_cluster_db_revisions()
        return ActionResult({"ClusterDbRevisions": revisions})

    def describe_cluster_tracks(self) -> ActionResult:
        tracks = self.redshift_backend.describe_cluster_tracks()
        return ActionResult({"MaintenanceTracks": tracks})

    def describe_cluster_versions(self) -> ActionResult:
        versions = self.redshift_backend.describe_cluster_versions()
        return ActionResult({"ClusterVersions": versions})

    def describe_custom_domain_associations(self) -> ActionResult:
        associations = self.redshift_backend.describe_custom_domain_associations()
        return ActionResult({"Associations": associations})

    def describe_data_shares(self) -> ActionResult:
        data_shares = self.redshift_backend.describe_data_shares()
        return ActionResult({"DataShares": data_shares})

    def describe_data_shares_for_consumer(self) -> ActionResult:
        data_shares = self.redshift_backend.describe_data_shares_for_consumer()
        return ActionResult({"DataShares": data_shares})

    def describe_data_shares_for_producer(self) -> ActionResult:
        data_shares = self.redshift_backend.describe_data_shares_for_producer()
        return ActionResult({"DataShares": data_shares})

    def describe_endpoint_access(self) -> ActionResult:
        cluster_identifier = self._get_param("ClusterIdentifier")
        endpoint_name = self._get_param("EndpointName")
        endpoints = self.redshift_backend.describe_endpoint_access(
            cluster_identifier=cluster_identifier,
            endpoint_name=endpoint_name,
        )
        return ActionResult({"EndpointAccessList": endpoints})

    def describe_endpoint_authorization(self) -> ActionResult:
        cluster_identifier = self._get_param("ClusterIdentifier")
        account = self._get_param("Account")
        grantee = self._get_param("Grantee")
        authorizations = self.redshift_backend.describe_endpoint_authorization(
            cluster_identifier=cluster_identifier,
            account=account,
            grantee=grantee,
        )
        return ActionResult({"EndpointAuthorizationList": authorizations})

    def describe_event_categories(self) -> ActionResult:
        categories = self.redshift_backend.describe_event_categories()
        return ActionResult({"EventCategoriesMapList": categories})

    def describe_event_subscriptions(self) -> ActionResult:
        subscription_name = self._get_param("SubscriptionName")
        subscriptions = self.redshift_backend.describe_event_subscriptions(
            subscription_name=subscription_name,
        )
        return ActionResult({"EventSubscriptionsList": subscriptions})

    def describe_events(self) -> ActionResult:
        events = self.redshift_backend.describe_events()
        return ActionResult({"Events": events})

    def describe_hsm_client_certificates(self) -> ActionResult:
        hsm_client_certificate_identifier = self._get_param(
            "HsmClientCertificateIdentifier"
        )
        certificates = self.redshift_backend.describe_hsm_client_certificates(
            hsm_client_certificate_identifier=hsm_client_certificate_identifier,
        )
        return ActionResult({"HsmClientCertificates": certificates})

    def describe_hsm_configurations(self) -> ActionResult:
        hsm_configuration_identifier = self._get_param("HsmConfigurationIdentifier")
        configurations = self.redshift_backend.describe_hsm_configurations(
            hsm_configuration_identifier=hsm_configuration_identifier,
        )
        return ActionResult({"HsmConfigurations": configurations})

    def describe_inbound_integrations(self) -> ActionResult:
        integrations = self.redshift_backend.describe_inbound_integrations()
        return ActionResult({"InboundIntegrations": integrations})

    def describe_integrations(self) -> ActionResult:
        integrations = self.redshift_backend.describe_integrations()
        return ActionResult({"Integrations": integrations})

    def describe_orderable_cluster_options(self) -> ActionResult:
        options = self.redshift_backend.describe_orderable_cluster_options()
        return ActionResult({"OrderableClusterOptions": options})

    def describe_redshift_idc_applications(self) -> ActionResult:
        applications = self.redshift_backend.describe_redshift_idc_applications()
        return ActionResult({"RedshiftIdcApplications": applications})

    def describe_reserved_node_exchange_status(self) -> ActionResult:
        details = self.redshift_backend.describe_reserved_node_exchange_status()
        return ActionResult({"ReservedNodeExchangeStatusDetails": details})

    def describe_reserved_node_offerings(self) -> ActionResult:
        offerings = self.redshift_backend.describe_reserved_node_offerings()
        return ActionResult({"ReservedNodeOfferings": offerings})

    def describe_reserved_nodes(self) -> ActionResult:
        nodes = self.redshift_backend.describe_reserved_nodes()
        return ActionResult({"ReservedNodes": nodes})

    def describe_scheduled_actions(self) -> ActionResult:
        scheduled_action_name = self._get_param("ScheduledActionName")
        actions = self.redshift_backend.describe_scheduled_actions(
            scheduled_action_name=scheduled_action_name,
        )
        return ActionResult({"ScheduledActions": actions})

    def describe_storage(self) -> ActionResult:
        storage = self.redshift_backend.describe_storage()
        return ActionResult(storage)

    def describe_table_restore_status(self) -> ActionResult:
        statuses = self.redshift_backend.describe_table_restore_status()
        return ActionResult({"TableRestoreStatusDetails": statuses})

    def describe_usage_limits(self) -> ActionResult:
        usage_limit_id = self._get_param("UsageLimitId")
        cluster_identifier = self._get_param("ClusterIdentifier")
        feature_type = self._get_param("FeatureType")
        limits = self.redshift_backend.describe_usage_limits(
            usage_limit_id=usage_limit_id,
            cluster_identifier=cluster_identifier,
            feature_type=feature_type,
        )
        return ActionResult({"UsageLimits": limits})

    def get_cluster_credentials_with_iam(self) -> ActionResult:
        cluster_identifier = self._get_param("ClusterIdentifier")
        db_name = self._get_param("DbName")
        duration_seconds = self._get_int_param("DurationSeconds", 900)
        credentials = self.redshift_backend.get_cluster_credentials_with_iam(
            cluster_identifier=cluster_identifier,
            db_name=db_name,
            duration_seconds=duration_seconds,
        )
        return ActionResult(credentials)

    def list_recommendations(self) -> ActionResult:
        recommendations = self.redshift_backend.list_recommendations()
        return ActionResult({"Recommendations": recommendations})

    def revoke_endpoint_access(self) -> ActionResult:
        cluster_identifier = self._get_param("ClusterIdentifier")
        account = self._get_param("Account")
        force = self._get_bool_param("Force", False)
        if cluster_identifier and account:
            result = self.redshift_backend.revoke_endpoint_access_for_cluster(
                cluster_identifier=cluster_identifier,
                account=account,
                force=force,
            )
        else:
            result = self.redshift_backend.revoke_endpoint_access()
        return ActionResult(result)

    def copy_cluster_snapshot(self) -> ActionResult:
        source_snapshot_identifier = self._get_param("SourceSnapshotIdentifier")
        target_snapshot_identifier = self._get_param("TargetSnapshotIdentifier")
        snapshot = self.redshift_backend.copy_cluster_snapshot(
            source_snapshot_identifier=source_snapshot_identifier,
            target_snapshot_identifier=target_snapshot_identifier,
        )
        return ActionResult({"Snapshot": snapshot})

    def authorize_snapshot_access(self) -> ActionResult:
        snapshot_identifier = self._get_param("SnapshotIdentifier")
        account_with_restore_access = self._get_param("AccountWithRestoreAccess")
        snapshot = self.redshift_backend.authorize_snapshot_access(
            snapshot_identifier=snapshot_identifier,
            account_with_restore_access=account_with_restore_access,
        )
        return ActionResult({"Snapshot": snapshot})

    def revoke_snapshot_access(self) -> ActionResult:
        snapshot_identifier = self._get_param("SnapshotIdentifier")
        account_with_restore_access = self._get_param("AccountWithRestoreAccess")
        snapshot = self.redshift_backend.revoke_snapshot_access(
            snapshot_identifier=snapshot_identifier,
            account_with_restore_access=account_with_restore_access,
        )
        return ActionResult({"Snapshot": snapshot})

    def create_scheduled_action(self) -> ActionResult:
        scheduled_action_name = self._get_param("ScheduledActionName")
        target_action = self._get_param("TargetAction", {})
        schedule = self._get_param("Schedule")
        iam_role = self._get_param("IamRole")
        description = self._get_param("ScheduledActionDescription", "")
        start_time = self._get_param("StartTime")
        end_time = self._get_param("EndTime")
        enable = self._get_bool_param("Enable", True)
        result = self.redshift_backend.create_scheduled_action(
            scheduled_action_name=scheduled_action_name,
            target_action=target_action,
            schedule=schedule,
            iam_role=iam_role,
            scheduled_action_description=description,
            start_time=start_time,
            end_time=end_time,
            enable=enable,
        )
        return ActionResult(result)

    def delete_scheduled_action(self) -> ActionResult:
        scheduled_action_name = self._get_param("ScheduledActionName")
        self.redshift_backend.delete_scheduled_action(scheduled_action_name)
        return EmptyResult()

    def modify_scheduled_action(self) -> ActionResult:
        scheduled_action_name = self._get_param("ScheduledActionName")
        target_action = self._get_param("TargetAction")
        schedule = self._get_param("Schedule")
        iam_role = self._get_param("IamRole")
        description = self._get_param("ScheduledActionDescription")
        start_time = self._get_param("StartTime")
        end_time = self._get_param("EndTime")
        enable = self._get_bool_param("Enable")
        result = self.redshift_backend.modify_scheduled_action(
            scheduled_action_name=scheduled_action_name,
            target_action=target_action,
            schedule=schedule,
            iam_role=iam_role,
            scheduled_action_description=description,
            start_time=start_time,
            end_time=end_time,
            enable=enable,
        )
        return ActionResult(result)

    def modify_cluster_iam_roles(self) -> ActionResult:
        cluster_identifier = self._get_param("ClusterIdentifier")
        add_iam_roles = self._get_param("AddIamRoles", [])
        remove_iam_roles = self._get_param("RemoveIamRoles", [])
        cluster = self.redshift_backend.modify_cluster_iam_roles(
            cluster_identifier=cluster_identifier,
            add_iam_roles=add_iam_roles,
            remove_iam_roles=remove_iam_roles,
        )
        return ActionResult({"Cluster": cluster})

    def create_authentication_profile(self) -> ActionResult:
        profile_name = self._get_param("AuthenticationProfileName")
        profile_content = self._get_param("AuthenticationProfileContent")
        result = self.redshift_backend.create_authentication_profile(
            authentication_profile_name=profile_name,
            authentication_profile_content=profile_content,
        )
        return ActionResult(result)

    def delete_authentication_profile(self) -> ActionResult:
        profile_name = self._get_param("AuthenticationProfileName")
        result = self.redshift_backend.delete_authentication_profile(
            authentication_profile_name=profile_name,
        )
        return ActionResult(result)

    def modify_authentication_profile(self) -> ActionResult:
        profile_name = self._get_param("AuthenticationProfileName")
        profile_content = self._get_param("AuthenticationProfileContent")
        result = self.redshift_backend.modify_authentication_profile(
            authentication_profile_name=profile_name,
            authentication_profile_content=profile_content,
        )
        return ActionResult(result)

    def batch_delete_cluster_snapshots(self) -> ActionResult:
        identifiers_raw = self._get_param("Identifiers", [])
        identifiers = []
        for item in identifiers_raw:
            if isinstance(item, dict):
                identifiers.append(item.get("SnapshotIdentifier", ""))
            else:
                identifiers.append(str(item))
        deleted, errors = self.redshift_backend.batch_delete_cluster_snapshots(
            identifiers=identifiers,
        )
        result: dict = {"Resources": deleted}
        if errors:
            result["Errors"] = errors
        return ActionResult(result)

    def batch_modify_cluster_snapshots(self) -> ActionResult:
        snapshot_identifier_list = self._get_param("SnapshotIdentifierList", [])
        retention = self._get_int_param("ManualSnapshotRetentionPeriod")
        force = self._get_bool_param("Force", False)
        modified, errors = self.redshift_backend.batch_modify_cluster_snapshots(
            snapshot_identifier_list=snapshot_identifier_list,
            manual_snapshot_retention_period=retention,
            force=force,
        )
        result: dict = {"Resources": modified}
        if errors:
            result["Errors"] = errors
        return ActionResult(result)

    def get_reserved_node_exchange_offerings(self) -> ActionResult:
        reserved_node_id = self._get_param("ReservedNodeId")
        offerings = self.redshift_backend.get_reserved_node_exchange_offerings(
            reserved_node_id=reserved_node_id,
        )
        return ActionResult({"ReservedNodeOfferings": offerings})

    def accept_reserved_node_exchange(self) -> ActionResult:
        reserved_node_id = self._get_param("ReservedNodeId")
        target_offering_id = self._get_param("TargetReservedNodeOfferingId")
        result = self.redshift_backend.accept_reserved_node_exchange(
            reserved_node_id=reserved_node_id,
            target_reserved_node_offering_id=target_offering_id,
        )
        return ActionResult(result)

    def create_usage_limit(self) -> ActionResult:
        cluster_identifier = self._get_param("ClusterIdentifier")
        feature_type = self._get_param("FeatureType")
        limit_type = self._get_param("LimitType")
        amount = self._get_int_param("Amount")
        period = self._get_param("Period", "monthly")
        breach_action = self._get_param("BreachAction", "log")
        tags = self._get_param("Tags", [])
        result = self.redshift_backend.create_usage_limit(
            cluster_identifier=cluster_identifier,
            feature_type=feature_type,
            limit_type=limit_type,
            amount=amount,
            period=period,
            breach_action=breach_action,
            tags=tags,
        )
        return ActionResult(result)

    def delete_usage_limit(self) -> ActionResult:
        usage_limit_id = self._get_param("UsageLimitId")
        self.redshift_backend.delete_usage_limit(usage_limit_id)
        return EmptyResult()

    def modify_usage_limit(self) -> ActionResult:
        usage_limit_id = self._get_param("UsageLimitId")
        amount = self._get_int_param("Amount")
        breach_action = self._get_param("BreachAction")
        result = self.redshift_backend.modify_usage_limit(
            usage_limit_id=usage_limit_id,
            amount=amount,
            breach_action=breach_action,
        )
        return ActionResult(result)

    def describe_node_configuration_options(self) -> ActionResult:
        action_type = self._get_param("ActionType")
        cluster_identifier = self._get_param("ClusterIdentifier")
        snapshot_identifier = self._get_param("SnapshotIdentifier")
        filters = self._get_param("Filter", [])
        options = self.redshift_backend.describe_node_configuration_options(
            action_type=action_type,
            cluster_identifier=cluster_identifier,
            snapshot_identifier=snapshot_identifier,
            filters=filters,
        )
        return ActionResult({"NodeConfigurationOptionList": options})

    def describe_partners(self) -> ActionResult:
        account_id = self._get_param("AccountId")
        cluster_identifier = self._get_param("ClusterIdentifier")
        database_name = self._get_param("DatabaseName")
        partner_name = self._get_param("PartnerName")
        partners = self.redshift_backend.describe_partners(
            account_id=account_id,
            cluster_identifier=cluster_identifier,
            database_name=database_name,
            partner_name=partner_name,
        )
        return ActionResult({"PartnerIntegrationInfoList": partners})

    def describe_resize(self) -> ActionResult:
        cluster_identifier = self._get_param("ClusterIdentifier")
        result = self.redshift_backend.describe_resize(
            cluster_identifier=cluster_identifier,
        )
        return ActionResult(result)

    def get_identity_center_auth_token(self) -> ActionResult:
        cluster_ids = self._get_param("ClusterIds", [])
        result = self.redshift_backend.get_identity_center_auth_token(
            cluster_ids=cluster_ids,
        )
        return ActionResult(result)

    def get_reserved_node_exchange_configuration_options(self) -> ActionResult:
        action_type = self._get_param("ActionType")
        cluster_identifier = self._get_param("ClusterIdentifier")
        snapshot_identifier = self._get_param("SnapshotIdentifier")
        options = (
            self.redshift_backend.get_reserved_node_exchange_configuration_options(
                action_type=action_type,
                cluster_identifier=cluster_identifier,
                snapshot_identifier=snapshot_identifier,
            )
        )
        return ActionResult({"ReservedNodeConfigurationOptionList": options})

    def authorize_endpoint_access(self) -> ActionResult:
        cluster_identifier = self._get_param("ClusterIdentifier")
        account = self._get_param("Account")
        vpc_ids = self._get_param("VpcIds", [])
        result = self.redshift_backend.authorize_endpoint_access(
            cluster_identifier=cluster_identifier,
            account=account,
            vpc_ids=vpc_ids if vpc_ids else None,
        )
        return ActionResult(result)

    def create_event_subscription(self) -> ActionResult:
        subscription_name = self._get_param("SubscriptionName")
        sns_topic_arn = self._get_param("SnsTopicArn")
        source_type = self._get_param("SourceType")
        source_ids = self._get_param("SourceIds", [])
        event_categories = self._get_param("EventCategories", [])
        severity = self._get_param("Severity", "ERROR")
        enabled = self._get_bool_param("Enabled", True)
        tags = self._get_param("Tags", [])
        result = self.redshift_backend.create_event_subscription(
            subscription_name=subscription_name,
            sns_topic_arn=sns_topic_arn,
            source_type=source_type,
            source_ids=source_ids if source_ids else None,
            event_categories=event_categories if event_categories else None,
            severity=severity,
            enabled=enabled,
            tags=tags,
        )
        return ActionResult({"EventSubscription": result})

    def delete_event_subscription(self) -> ActionResult:
        subscription_name = self._get_param("SubscriptionName")
        self.redshift_backend.delete_event_subscription(subscription_name)
        return EmptyResult()

    def modify_event_subscription(self) -> ActionResult:
        subscription_name = self._get_param("SubscriptionName")
        sns_topic_arn = self._get_param("SnsTopicArn")
        source_type = self._get_param("SourceType")
        source_ids = self._get_param("SourceIds")
        event_categories = self._get_param("EventCategories")
        severity = self._get_param("Severity")
        enabled = self._get_bool_param("Enabled")
        result = self.redshift_backend.modify_event_subscription(
            subscription_name=subscription_name,
            sns_topic_arn=sns_topic_arn,
            source_type=source_type,
            source_ids=source_ids,
            event_categories=event_categories,
            severity=severity,
            enabled=enabled,
        )
        return ActionResult({"EventSubscription": result})

    def create_hsm_client_certificate(self) -> ActionResult:
        hsm_client_certificate_identifier = self._get_param(
            "HsmClientCertificateIdentifier"
        )
        tags = self._get_param("Tags", [])
        result = self.redshift_backend.create_hsm_client_certificate(
            hsm_client_certificate_identifier=hsm_client_certificate_identifier,
            tags=tags,
        )
        return ActionResult({"HsmClientCertificate": result})

    def delete_hsm_client_certificate(self) -> ActionResult:
        hsm_client_certificate_identifier = self._get_param(
            "HsmClientCertificateIdentifier"
        )
        self.redshift_backend.delete_hsm_client_certificate(
            hsm_client_certificate_identifier
        )
        return EmptyResult()

    def create_hsm_configuration(self) -> ActionResult:
        hsm_configuration_identifier = self._get_param("HsmConfigurationIdentifier")
        description = self._get_param("Description")
        hsm_ip_address = self._get_param("HsmIpAddress")
        hsm_partition_name = self._get_param("HsmPartitionName")
        hsm_partition_password = self._get_param("HsmPartitionPassword")
        hsm_server_public_certificate = self._get_param("HsmServerPublicCertificate")
        tags = self._get_param("Tags", [])
        result = self.redshift_backend.create_hsm_configuration(
            hsm_configuration_identifier=hsm_configuration_identifier,
            description=description,
            hsm_ip_address=hsm_ip_address,
            hsm_partition_name=hsm_partition_name,
            hsm_partition_password=hsm_partition_password,
            hsm_server_public_certificate=hsm_server_public_certificate,
            tags=tags,
        )
        return ActionResult({"HsmConfiguration": result})

    def delete_hsm_configuration(self) -> ActionResult:
        hsm_configuration_identifier = self._get_param("HsmConfigurationIdentifier")
        self.redshift_backend.delete_hsm_configuration(hsm_configuration_identifier)
        return EmptyResult()

    def create_endpoint_access(self) -> ActionResult:
        cluster_identifier = self._get_param("ClusterIdentifier")
        endpoint_name = self._get_param("EndpointName")
        subnet_group_name = self._get_param("SubnetGroupName")
        vpc_security_group_ids = self._get_param("VpcSecurityGroupIds", [])
        result = self.redshift_backend.create_endpoint_access(
            cluster_identifier=cluster_identifier,
            endpoint_name=endpoint_name,
            subnet_group_name=subnet_group_name,
            vpc_security_group_ids=vpc_security_group_ids
            if vpc_security_group_ids
            else None,
        )
        return ActionResult(result)

    def delete_endpoint_access(self) -> ActionResult:
        endpoint_name = self._get_param("EndpointName")
        result = self.redshift_backend.delete_endpoint_access(endpoint_name)
        return ActionResult(result)

    def modify_endpoint_access(self) -> ActionResult:
        endpoint_name = self._get_param("EndpointName")
        vpc_security_group_ids = self._get_param("VpcSecurityGroupIds", [])
        result = self.redshift_backend.modify_endpoint_access(
            endpoint_name=endpoint_name,
            vpc_security_group_ids=vpc_security_group_ids
            if vpc_security_group_ids
            else None,
        )
        return ActionResult(result)

    def add_partner(self) -> ActionResult:
        account_id = self._get_param("AccountId")
        cluster_identifier = self._get_param("ClusterIdentifier")
        database_name = self._get_param("DatabaseName")
        partner_name = self._get_param("PartnerName")
        result = self.redshift_backend.add_partner(
            account_id=account_id,
            cluster_identifier=cluster_identifier,
            database_name=database_name,
            partner_name=partner_name,
        )
        return ActionResult(result)

    def delete_partner(self) -> ActionResult:
        account_id = self._get_param("AccountId")
        cluster_identifier = self._get_param("ClusterIdentifier")
        database_name = self._get_param("DatabaseName")
        partner_name = self._get_param("PartnerName")
        result = self.redshift_backend.delete_partner(
            account_id=account_id,
            cluster_identifier=cluster_identifier,
            database_name=database_name,
            partner_name=partner_name,
        )
        return ActionResult(result)

    def update_partner_status(self) -> ActionResult:
        account_id = self._get_param("AccountId")
        cluster_identifier = self._get_param("ClusterIdentifier")
        database_name = self._get_param("DatabaseName")
        partner_name = self._get_param("PartnerName")
        status = self._get_param("Status")
        status_message = self._get_param("StatusMessage")
        result = self.redshift_backend.update_partner_status(
            account_id=account_id,
            cluster_identifier=cluster_identifier,
            database_name=database_name,
            partner_name=partner_name,
            status=status,
            status_message=status_message,
        )
        return ActionResult(result)

    def put_resource_policy(self) -> ActionResult:
        resource_arn = self._get_param("ResourceArn")
        policy = self._get_param("Policy")
        result = self.redshift_backend.put_resource_policy(
            resource_arn=resource_arn,
            policy=policy,
        )
        return ActionResult({"ResourcePolicy": result})

    def get_resource_policy(self) -> ActionResult:
        resource_arn = self._get_param("ResourceArn")
        result = self.redshift_backend.get_resource_policy(
            resource_arn=resource_arn,
        )
        return ActionResult({"ResourcePolicy": result})

    def delete_resource_policy(self) -> ActionResult:
        resource_arn = self._get_param("ResourceArn")
        self.redshift_backend.delete_resource_policy(
            resource_arn=resource_arn,
        )
        return EmptyResult()

    def rotate_encryption_key(self) -> ActionResult:
        cluster_identifier = self._get_param("ClusterIdentifier")
        cluster = self.redshift_backend.rotate_encryption_key(
            cluster_identifier=cluster_identifier,
        )
        return ActionResult({"Cluster": cluster})

    def cancel_resize(self) -> ActionResult:
        cluster_identifier = self._get_param("ClusterIdentifier")
        result = self.redshift_backend.cancel_resize(
            cluster_identifier=cluster_identifier,
        )
        return ActionResult(result)

    def modify_cluster_parameter_group(self) -> ActionResult:
        parameter_group_name = self._get_param("ParameterGroupName")
        parameters = self._get_param("Parameters", [])
        result = self.redshift_backend.modify_cluster_parameter_group(
            parameter_group_name=parameter_group_name,
            parameters=parameters,
        )
        return ActionResult(result)

    def reset_cluster_parameter_group(self) -> ActionResult:
        parameter_group_name = self._get_param("ParameterGroupName")
        reset_all = self._get_bool_param("ResetAllParameters", True)
        parameters = self._get_param("Parameters", [])
        result = self.redshift_backend.reset_cluster_parameter_group(
            parameter_group_name=parameter_group_name,
            reset_all_parameters=reset_all,
            parameters=parameters,
        )
        return ActionResult(result)

    def modify_cluster_snapshot(self) -> ActionResult:
        snapshot_identifier = self._get_param("SnapshotIdentifier")
        retention = self._get_int_param("ManualSnapshotRetentionPeriod")
        force = self._get_bool_param("Force", False)
        snapshot = self.redshift_backend.modify_cluster_snapshot(
            snapshot_identifier=snapshot_identifier,
            manual_snapshot_retention_period=retention,
            force=force,
        )
        return ActionResult({"Snapshot": snapshot})

    def modify_cluster_subnet_group(self) -> ActionResult:
        cluster_subnet_group_name = self._get_param("ClusterSubnetGroupName")
        description = self._get_param("Description")
        subnet_ids = self._get_param("SubnetIds", [])
        subnet_group = self.redshift_backend.modify_cluster_subnet_group(
            cluster_subnet_group_name=cluster_subnet_group_name,
            description=description,
            subnet_ids=subnet_ids if subnet_ids else None,
        )
        return ActionResult({"ClusterSubnetGroup": subnet_group})

    def modify_aqua_configuration(self) -> ActionResult:
        cluster_identifier = self._get_param("ClusterIdentifier")
        aqua_configuration_status = self._get_param("AquaConfigurationStatus")
        result = self.redshift_backend.modify_aqua_configuration(
            cluster_identifier=cluster_identifier,
            aqua_configuration_status=aqua_configuration_status,
        )
        return ActionResult(result)

    def reboot_cluster(self) -> ActionResult:
        cluster_identifier = self._get_param("ClusterIdentifier")
        cluster = self.redshift_backend.reboot_cluster(
            cluster_identifier=cluster_identifier,
        )
        return ActionResult({"Cluster": cluster})

    def modify_cluster_db_revision(self) -> ActionResult:
        cluster_identifier = self._get_param("ClusterIdentifier")
        revision_target = self._get_param("RevisionTarget")
        cluster = self.redshift_backend.modify_cluster_db_revision(
            cluster_identifier=cluster_identifier,
            revision_target=revision_target,
        )
        return ActionResult({"Cluster": cluster})

    def modify_cluster_maintenance(self) -> ActionResult:
        cluster_identifier = self._get_param("ClusterIdentifier")
        defer_maintenance = self._get_bool_param("DeferMaintenance")
        defer_maintenance_identifier = self._get_param("DeferMaintenanceIdentifier")
        defer_maintenance_start_time = self._get_param("DeferMaintenanceStartTime")
        defer_maintenance_end_time = self._get_param("DeferMaintenanceEndTime")
        defer_maintenance_duration = self._get_int_param("DeferMaintenanceDuration")
        cluster = self.redshift_backend.modify_cluster_maintenance(
            cluster_identifier=cluster_identifier,
            defer_maintenance=defer_maintenance,
            defer_maintenance_identifier=defer_maintenance_identifier,
            defer_maintenance_start_time=defer_maintenance_start_time,
            defer_maintenance_end_time=defer_maintenance_end_time,
            defer_maintenance_duration=defer_maintenance_duration,
        )
        return ActionResult({"Cluster": cluster})

    def create_custom_domain_association(self) -> ActionResult:
        cluster_identifier = self._get_param("ClusterIdentifier")
        custom_domain_name = self._get_param("CustomDomainName")
        custom_domain_certificate_arn = self._get_param("CustomDomainCertificateArn")
        result = self.redshift_backend.create_custom_domain_association(
            cluster_identifier=cluster_identifier,
            custom_domain_name=custom_domain_name,
            custom_domain_certificate_arn=custom_domain_certificate_arn,
        )
        return ActionResult(result)

    def delete_custom_domain_association(self) -> ActionResult:
        cluster_identifier = self._get_param("ClusterIdentifier")
        custom_domain_name = self._get_param("CustomDomainName")
        self.redshift_backend.delete_custom_domain_association(
            cluster_identifier=cluster_identifier,
            custom_domain_name=custom_domain_name,
        )
        return EmptyResult()

    def modify_custom_domain_association(self) -> ActionResult:
        cluster_identifier = self._get_param("ClusterIdentifier")
        custom_domain_name = self._get_param("CustomDomainName")
        custom_domain_certificate_arn = self._get_param("CustomDomainCertificateArn")
        result = self.redshift_backend.modify_custom_domain_association(
            cluster_identifier=cluster_identifier,
            custom_domain_name=custom_domain_name,
            custom_domain_certificate_arn=custom_domain_certificate_arn,
        )
        return ActionResult(result)

    def authorize_data_share(self) -> ActionResult:
        data_share_arn = self._get_param("DataShareArn")
        consumer_identifier = self._get_param("ConsumerIdentifier")
        result = self.redshift_backend.authorize_data_share(
            data_share_arn=data_share_arn,
            consumer_identifier=consumer_identifier,
        )
        return ActionResult(result)

    def deauthorize_data_share(self) -> ActionResult:
        data_share_arn = self._get_param("DataShareArn")
        consumer_identifier = self._get_param("ConsumerIdentifier")
        result = self.redshift_backend.deauthorize_data_share(
            data_share_arn=data_share_arn,
            consumer_identifier=consumer_identifier,
        )
        return ActionResult(result)

    def reject_data_share(self) -> ActionResult:
        data_share_arn = self._get_param("DataShareArn")
        result = self.redshift_backend.reject_data_share(
            data_share_arn=data_share_arn,
        )
        return ActionResult(result)

    def associate_data_share_consumer(self) -> ActionResult:
        data_share_arn = self._get_param("DataShareArn")
        associate_entire_account = self._get_bool_param("AssociateEntireAccount", False)
        consumer_arn = self._get_param("ConsumerArn")
        consumer_region = self._get_param("ConsumerRegion")
        result = self.redshift_backend.associate_data_share_consumer(
            data_share_arn=data_share_arn,
            associate_entire_account=associate_entire_account,
            consumer_arn=consumer_arn,
            consumer_region=consumer_region,
        )
        return ActionResult(result)

    def disassociate_data_share_consumer(self) -> ActionResult:
        data_share_arn = self._get_param("DataShareArn")
        disassociate_entire_account = self._get_bool_param(
            "DisassociateEntireAccount", False
        )
        consumer_arn = self._get_param("ConsumerArn")
        consumer_region = self._get_param("ConsumerRegion")
        result = self.redshift_backend.disassociate_data_share_consumer(
            data_share_arn=data_share_arn,
            disassociate_entire_account=disassociate_entire_account,
            consumer_arn=consumer_arn,
            consumer_region=consumer_region,
        )
        return ActionResult(result)

    def revoke_cluster_security_group_ingress(self) -> ActionResult:
        security_group_name = self._get_param("ClusterSecurityGroupName")
        cidr_ip = self._get_param("CIDRIP")
        security_group = self.redshift_backend.revoke_cluster_security_group_ingress(
            security_group_name=security_group_name,
            cidr_ip=cidr_ip,
        )
        return ActionResult({"ClusterSecurityGroup": security_group})

    def modify_cluster_snapshot_schedule(self) -> ActionResult:
        cluster_identifier = self._get_param("ClusterIdentifier")
        schedule_identifier = self._get_param("ScheduleIdentifier")
        disassociate = self._get_bool_param("DisassociateSchedule", False)
        self.redshift_backend.modify_cluster_snapshot_schedule(
            cluster_identifier=cluster_identifier,
            schedule_identifier=schedule_identifier,
            disassociate_schedule=disassociate,
        )
        return EmptyResult()

    def create_integration(self) -> ActionResult:
        return ActionResult(
            {
                "IntegrationArn": "",
                "IntegrationName": "",
                "SourceArn": "",
                "TargetArn": "",
                "Status": "creating",
                "Errors": [],
                "CreateTime": None,
                "Description": "",
                "KMSKeyId": "",
                "AdditionalEncryptionContext": {},
                "Tags": [],
            }
        )

    def create_redshift_idc_application(self) -> ActionResult:
        return ActionResult({"RedshiftIdcApplication": {}})

    def delete_integration(self) -> ActionResult:
        return ActionResult(
            {
                "IntegrationArn": "",
                "IntegrationName": "",
                "SourceArn": "",
                "TargetArn": "",
                "Status": "deleting",
                "Errors": [],
                "CreateTime": None,
                "Description": "",
                "KMSKeyId": "",
                "AdditionalEncryptionContext": {},
                "Tags": [],
            }
        )

    def delete_redshift_idc_application(self) -> ActionResult:
        return EmptyResult()

    def deregister_namespace(self) -> ActionResult:
        return ActionResult({"Status": ""})

    def failover_primary_compute(self) -> ActionResult:
        return ActionResult({"Cluster": {}})

    def modify_integration(self) -> ActionResult:
        return ActionResult(
            {
                "IntegrationArn": "",
                "IntegrationName": "",
                "SourceArn": "",
                "TargetArn": "",
                "Status": "active",
                "Errors": [],
                "CreateTime": None,
                "Description": "",
                "KMSKeyId": "",
                "AdditionalEncryptionContext": {},
                "Tags": [],
            }
        )

    def modify_lakehouse_configuration(self) -> ActionResult:
        return ActionResult(
            {
                "ClusterIdentifier": "",
                "LakehouseIdcApplicationArn": "",
                "LakehouseRegistrationStatus": "",
                "CatalogArn": "",
            }
        )

    def modify_redshift_idc_application(self) -> ActionResult:
        return ActionResult({"RedshiftIdcApplication": {}})

    def purchase_reserved_node_offering(self) -> ActionResult:
        return ActionResult({"ReservedNode": {}})

    def register_namespace(self) -> ActionResult:
        return ActionResult({"Status": ""})

    def resize_cluster(self) -> ActionResult:
        return ActionResult({"Cluster": {"ClusterIdentifier": ""}})

    def restore_table_from_cluster_snapshot(self) -> ActionResult:
        return ActionResult(
            {
                "TableRestoreStatus": {
                    "TableRestoreRequestId": "stub",
                    "Status": "IN_PROGRESS",
                }
            }
        )
