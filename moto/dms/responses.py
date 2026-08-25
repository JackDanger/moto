import json

from moto.core.responses import BaseResponse

from .models import DatabaseMigrationServiceBackend, dms_backends


class DatabaseMigrationServiceResponse(BaseResponse):
    def __init__(self) -> None:
        super().__init__(service_name="dms")

    @property
    def dms_backend(self) -> DatabaseMigrationServiceBackend:
        return dms_backends[self.current_account][self.region]

    # ── Tagging ──────────────────────────────────────────────────────

    def add_tags_to_resource(self) -> str:
        resource_arn = self._get_param("ResourceArn")
        tags = self._get_param("Tags")
        self.dms_backend.add_tags_to_resource(resource_arn=resource_arn, tags=tags)
        return json.dumps({})

    def remove_tags_from_resource(self) -> str:
        resource_arn = self._get_param("ResourceArn")
        tag_keys = self._get_param("TagKeys")
        self.dms_backend.remove_tags_from_resource(
            resource_arn=resource_arn, tag_keys=tag_keys
        )
        return json.dumps({})

    def list_tags_for_resource(self) -> str:
        params = json.loads(self.body)
        resource_arn = params.get("ResourceArn")
        resource_arn_list = params.get("ResourceArnList")

        if resource_arn and resource_arn_list:
            raise ValueError(
                "Both ResourceArn and ResourceArnList cannot be specified."
            )
        if not resource_arn and not resource_arn_list:
            raise ValueError(
                "Either ResourceArn or ResourceArnList should be specified."
            )

        if resource_arn:
            tag_list = self.dms_backend.list_tags_for_resource([resource_arn])
        else:
            tag_list = self.dms_backend.list_tags_for_resource(resource_arn_list)

        return json.dumps({"TagList": tag_list})

    # ── Replication Tasks ────────────────────────────────────────────

    def create_replication_task(self) -> str:
        replication_task_identifier = self._get_param("ReplicationTaskIdentifier")
        source_endpoint_arn = self._get_param("SourceEndpointArn")
        target_endpoint_arn = self._get_param("TargetEndpointArn")
        replication_instance_arn = self._get_param("ReplicationInstanceArn")
        migration_type = self._get_param("MigrationType")
        table_mappings = self._get_param("TableMappings")
        replication_task_settings = self._get_param("ReplicationTaskSettings")
        tags = self._get_param("Tags")
        replication_task = self.dms_backend.create_replication_task(
            replication_task_identifier=replication_task_identifier,
            source_endpoint_arn=source_endpoint_arn,
            target_endpoint_arn=target_endpoint_arn,
            replication_instance_arn=replication_instance_arn,
            migration_type=migration_type,
            table_mappings=table_mappings,
            replication_task_settings=replication_task_settings,
            tags=tags,
        )

        return json.dumps({"ReplicationTask": replication_task.to_dict()})

    def start_replication_task(self) -> str:
        replication_task_arn = self._get_param("ReplicationTaskArn")
        replication_task = self.dms_backend.start_replication_task(
            replication_task_arn=replication_task_arn
        )

        return json.dumps({"ReplicationTask": replication_task.to_dict()})

    def stop_replication_task(self) -> str:
        replication_task_arn = self._get_param("ReplicationTaskArn")
        replication_task = self.dms_backend.stop_replication_task(
            replication_task_arn=replication_task_arn
        )

        return json.dumps({"ReplicationTask": replication_task.to_dict()})

    def delete_replication_task(self) -> str:
        replication_task_arn = self._get_param("ReplicationTaskArn")
        replication_task = self.dms_backend.delete_replication_task(
            replication_task_arn=replication_task_arn
        )

        return json.dumps({"ReplicationTask": replication_task.to_dict()})

    def describe_replication_tasks(self) -> str:
        filters = self._get_param("Filters", [])
        max_records = self._get_int_param("MaxRecords", 100)
        replication_tasks = self.dms_backend.describe_replication_tasks(
            filters=filters, max_records=max_records
        )

        return json.dumps(
            {"ReplicationTasks": [t.to_dict() for t in replication_tasks]}
        )

    def modify_replication_task(self) -> str:
        params = json.loads(self.body)
        task = self.dms_backend.modify_replication_task(
            replication_task_arn=params.get("ReplicationTaskArn"),
            replication_task_identifier=params.get("ReplicationTaskIdentifier"),
            migration_type=params.get("MigrationType"),
            table_mappings=params.get("TableMappings"),
            replication_task_settings=params.get("ReplicationTaskSettings"),
            cdc_start_time=params.get("CdcStartTime"),
            cdc_start_position=params.get("CdcStartPosition"),
            cdc_stop_position=params.get("CdcStopPosition"),
            task_data=params.get("TaskData"),
        )
        return json.dumps({"ReplicationTask": task.to_dict()})

    def move_replication_task(self) -> str:
        replication_task_arn = self._get_param("ReplicationTaskArn")
        target_replication_instance_arn = self._get_param(
            "TargetReplicationInstanceArn"
        )
        task = self.dms_backend.move_replication_task(
            replication_task_arn=replication_task_arn,
            target_replication_instance_arn=target_replication_instance_arn,
        )
        return json.dumps({"ReplicationTask": task.to_dict()})

    # ── Replication Instances ────────────────────────────────────────

    def create_replication_instance(self) -> str:
        params = json.loads(self.body)
        replication_instance = self.dms_backend.create_replication_instance(
            replication_instance_identifier=params.get(
                "ReplicationInstanceIdentifier"
            ),
            allocated_storage=params.get("AllocatedStorage"),
            replication_instance_class=params.get("ReplicationInstanceClass"),
            vpc_security_group_ids=self._get_param("VpcSecurityGroupIds"),
            availability_zone=params.get("AvailabilityZone"),
            replication_subnet_group_identifier=params.get(
                "ReplicationSubnetGroupIdentifier"
            ),
            preferred_maintenance_window=params.get("PreferredMaintenanceWindow"),
            multi_az=params.get("MultiAZ"),
            engine_version=params.get("EngineVersion"),
            auto_minor_version_upgrade=params.get("AutoMinorVersionUpgrade"),
            tags=params.get("Tags"),
            kms_key_id=params.get("KmsKeyId"),
            publicly_accessible=params.get("PubliclyAccessible"),
            dns_name_servers=params.get("DnsNameServers"),
            resource_identifier=params.get("ResourceIdentifier"),
            network_type=params.get("NetworkType"),
            kerberos_authentication_settings=params.get(
                "KerberosAuthenticationSettings"
            ),
        )
        return json.dumps({"ReplicationInstance": replication_instance.to_dict()})

    def describe_replication_instances(self) -> str:
        data = json.loads(self.body)
        filters = data.get("Filters", [])
        max_records = data.get("MaxRecords")
        marker = data.get("Marker")

        replication_instances = self.dms_backend.describe_replication_instances(
            filters=filters,
            max_records=max_records,
            marker=marker,
        )

        instances_dict = [i.to_dict() for i in replication_instances]
        return json.dumps({"ReplicationInstances": instances_dict})

    def delete_replication_instance(self) -> str:
        replication_instance_arn = self._get_param("ReplicationInstanceArn")
        replication_instance = self.dms_backend.delete_replication_instance(
            replication_instance_arn=replication_instance_arn,
        )
        return json.dumps({"ReplicationInstance": replication_instance.to_dict()})

    def modify_replication_instance(self) -> str:
        params = json.loads(self.body)
        instance = self.dms_backend.modify_replication_instance(
            replication_instance_arn=params.get("ReplicationInstanceArn"),
            allocated_storage=params.get("AllocatedStorage"),
            apply_immediately=params.get("ApplyImmediately"),
            replication_instance_class=params.get("ReplicationInstanceClass"),
            vpc_security_group_ids=params.get("VpcSecurityGroupIds"),
            preferred_maintenance_window=params.get("PreferredMaintenanceWindow"),
            multi_az=params.get("MultiAZ"),
            engine_version=params.get("EngineVersion"),
            auto_minor_version_upgrade=params.get("AutoMinorVersionUpgrade"),
            replication_instance_identifier=params.get(
                "ReplicationInstanceIdentifier"
            ),
            network_type=params.get("NetworkType"),
        )
        return json.dumps({"ReplicationInstance": instance.to_dict()})

    def reboot_replication_instance(self) -> str:
        params = json.loads(self.body)
        instance = self.dms_backend.reboot_replication_instance(
            replication_instance_arn=params.get("ReplicationInstanceArn"),
            force_failover=params.get("ForceFailover"),
            force_planned_failover=params.get("ForcePlannedFailover"),
        )
        return json.dumps({"ReplicationInstance": instance.to_dict()})

    def describe_replication_instance_task_logs(self) -> str:
        params = json.loads(self.body)
        result = self.dms_backend.describe_replication_instance_task_logs(
            replication_instance_arn=params.get("ReplicationInstanceArn"),
            max_records=params.get("MaxRecords"),
            marker=params.get("Marker"),
        )
        return json.dumps(result)

    # ── Endpoints ────────────────────────────────────────────────────

    def create_endpoint(self) -> str:
        params = json.loads(self.body)
        endpoint = self.dms_backend.create_endpoint(
            endpoint_identifier=params.get("EndpointIdentifier"),
            endpoint_type=params.get("EndpointType"),
            engine_name=params.get("EngineName"),
            username=params.get("Username"),
            password=params.get("Password"),
            server_name=params.get("ServerName"),
            port=params.get("Port"),
            database_name=params.get("DatabaseName"),
            extra_connection_attributes=params.get("ExtraConnectionAttributes"),
            kms_key_id=params.get("KmsKeyId"),
            tags=params.get("Tags"),
            certificate_arn=params.get("CertificateArn"),
            ssl_mode=params.get("SslMode"),
            service_access_role_arn=params.get("ServiceAccessRoleArn"),
            external_table_definition=params.get("ExternalTableDefinition"),
            dynamo_db_settings=params.get("DynamoDbSettings"),
            s3_settings=params.get("S3Settings"),
            dms_transfer_settings=params.get("DmsTransferSettings"),
            mongo_db_settings=params.get("MongoDbSettings"),
            kinesis_settings=params.get("KinesisSettings"),
            kafka_settings=params.get("KafkaSettings"),
            elasticsearch_settings=params.get("ElasticsearchSettings"),
            neptune_settings=params.get("NeptuneSettings"),
            redshift_settings=params.get("RedshiftSettings"),
            postgre_sql_settings=params.get("PostgreSQLSettings"),
            my_sql_settings=params.get("MySQLSettings"),
            oracle_settings=params.get("OracleSettings"),
            sybase_settings=params.get("SybaseSettings"),
            microsoft_sql_server_settings=params.get("MicrosoftSQLServerSettings"),
            ibm_db2_settings=params.get("IBMDb2Settings"),
            resource_identifier=params.get("ResourceIdentifier"),
            doc_db_settings=params.get("DocDbSettings"),
            redis_settings=params.get("RedisSettings"),
            gcp_my_sql_settings=params.get("GcpMySQLSettings"),
            timestream_settings=params.get("TimestreamSettings"),
        )

        return json.dumps(
            {"Endpoint": {k: v for k, v in endpoint.to_dict().items() if v is not None}}
        )

    def describe_endpoints(self) -> str:
        params = json.loads(self.body)
        filters = params.get("Filters", [])
        max_records = params.get("MaxRecords")
        marker = params.get("Marker")
        endpoints = self.dms_backend.describe_endpoints(
            filters=filters, max_records=max_records, marker=marker
        )
        return json.dumps(
            {
                "Endpoints": [
                    {k: v for k, v in endpoint.to_dict().items() if v is not None}
                    for endpoint in endpoints
                ]
            }
        )

    def delete_endpoint(self) -> str:
        endpoint_arn = self._get_param("EndpointArn")
        endpoint = self.dms_backend.delete_endpoint(
            endpoint_arn=endpoint_arn,
        )
        return json.dumps({"Endpoint": endpoint.to_dict()})

    def modify_endpoint(self) -> str:
        params = json.loads(self.body)
        endpoint = self.dms_backend.modify_endpoint(
            endpoint_arn=params.get("EndpointArn"),
            endpoint_identifier=params.get("EndpointIdentifier"),
            endpoint_type=params.get("EndpointType"),
            engine_name=params.get("EngineName"),
            username=params.get("Username"),
            password=params.get("Password"),
            server_name=params.get("ServerName"),
            port=params.get("Port"),
            database_name=params.get("DatabaseName"),
            extra_connection_attributes=params.get("ExtraConnectionAttributes"),
            certificate_arn=params.get("CertificateArn"),
            ssl_mode=params.get("SslMode"),
            service_access_role_arn=params.get("ServiceAccessRoleArn"),
            external_table_definition=params.get("ExternalTableDefinition"),
            dynamo_db_settings=params.get("DynamoDbSettings"),
            s3_settings=params.get("S3Settings"),
            dms_transfer_settings=params.get("DmsTransferSettings"),
            mongo_db_settings=params.get("MongoDbSettings"),
            kinesis_settings=params.get("KinesisSettings"),
            kafka_settings=params.get("KafkaSettings"),
            elasticsearch_settings=params.get("ElasticsearchSettings"),
            neptune_settings=params.get("NeptuneSettings"),
            redshift_settings=params.get("RedshiftSettings"),
            postgre_sql_settings=params.get("PostgreSQLSettings"),
            my_sql_settings=params.get("MySQLSettings"),
            oracle_settings=params.get("OracleSettings"),
            sybase_settings=params.get("SybaseSettings"),
            microsoft_sql_server_settings=params.get("MicrosoftSQLServerSettings"),
            ibm_db2_settings=params.get("IBMDb2Settings"),
            doc_db_settings=params.get("DocDbSettings"),
            redis_settings=params.get("RedisSettings"),
            gcp_my_sql_settings=params.get("GcpMySQLSettings"),
            timestream_settings=params.get("TimestreamSettings"),
            exact_settings=params.get("ExactSettings"),
        )
        return json.dumps(
            {"Endpoint": {k: v for k, v in endpoint.to_dict().items() if v is not None}}
        )

    # ── Replication Subnet Groups ────────────────────────────────────

    def create_replication_subnet_group(self) -> str:
        params = json.loads(self.body)
        replication_subnet_group = self.dms_backend.create_replication_subnet_group(
            replication_subnet_group_identifier=params.get(
                "ReplicationSubnetGroupIdentifier"
            ),
            replication_subnet_group_description=params.get(
                "ReplicationSubnetGroupDescription"
            ),
            subnet_ids=params.get("SubnetIds"),
            tags=params.get("Tags"),
        )
        return json.dumps(
            {"ReplicationSubnetGroup": replication_subnet_group.to_dict()}
        )

    def describe_replication_subnet_groups(self) -> str:
        params = json.loads(self.body)
        filters = params.get("Filters", [])
        max_records = params.get("MaxRecords")
        marker = params.get("Marker")
        replication_subnet_groups = self.dms_backend.describe_replication_subnet_groups(
            filters=filters, max_records=max_records, marker=marker
        )

        return json.dumps(
            {
                "ReplicationSubnetGroups": [
                    {
                        k: v
                        for k, v in replication_subnet_group.to_dict().items()
                        if v is not None
                    }
                    for replication_subnet_group in replication_subnet_groups
                ]
            }
        )

    def delete_replication_subnet_group(self) -> str:
        replication_subnet_group_identifier = self._get_param(
            "ReplicationSubnetGroupIdentifier"
        )
        self.dms_backend.delete_replication_subnet_group(
            replication_subnet_group_identifier=replication_subnet_group_identifier,
        )
        return json.dumps({})

    def modify_replication_subnet_group(self) -> str:
        params = json.loads(self.body)
        group = self.dms_backend.modify_replication_subnet_group(
            replication_subnet_group_identifier=params.get(
                "ReplicationSubnetGroupIdentifier"
            ),
            replication_subnet_group_description=params.get(
                "ReplicationSubnetGroupDescription"
            ),
            subnet_ids=params.get("SubnetIds"),
        )
        return json.dumps({"ReplicationSubnetGroup": group.to_dict()})

    # ── Connections ──────────────────────────────────────────────────

    def test_connection(self) -> str:
        replication_instance_arn = self._get_param("ReplicationInstanceArn")
        endpoint_arn = self._get_param("EndpointArn")
        connection = self.dms_backend.test_connection(
            replication_instance_arn=replication_instance_arn,
            endpoint_arn=endpoint_arn,
        )
        return json.dumps({"Connection": connection.to_dict()})

    def describe_connections(self) -> str:
        data = json.loads(self.body)
        filters = data.get("Filters", [])
        max_records = data.get("MaxRecords")
        marker = data.get("Marker")

        connections = self.dms_backend.describe_connections(
            filters=filters, max_records=max_records, marker=marker
        )
        connection_list = [c.to_dict() for c in connections]
        return json.dumps({"Connections": connection_list})

    def delete_connection(self) -> str:
        endpoint_arn = self._get_param("EndpointArn")
        replication_instance_arn = self._get_param("ReplicationInstanceArn")
        connection = self.dms_backend.delete_connection(
            endpoint_arn=endpoint_arn,
            replication_instance_arn=replication_instance_arn,
        )
        return json.dumps({"Connection": connection.to_dict()})

    # ── Event Subscriptions ──────────────────────────────────────────

    def create_event_subscription(self) -> str:
        params = json.loads(self.body)
        sub = self.dms_backend.create_event_subscription(
            subscription_name=params.get("SubscriptionName"),
            sns_topic_arn=params.get("SnsTopicArn"),
            source_type=params.get("SourceType"),
            event_categories=params.get("EventCategories"),
            source_ids=params.get("SourceIds"),
            enabled=params.get("Enabled"),
            tags=params.get("Tags"),
        )
        return json.dumps({"EventSubscription": sub.to_dict()})

    def describe_event_subscriptions(self) -> str:
        params = json.loads(self.body)
        subs = self.dms_backend.describe_event_subscriptions(
            subscription_name=params.get("SubscriptionName"),
            filters=params.get("Filters"),
            max_records=params.get("MaxRecords"),
            marker=params.get("Marker"),
        )
        return json.dumps(
            {"EventSubscriptionsList": [s.to_dict() for s in subs]}
        )

    def delete_event_subscription(self) -> str:
        subscription_name = self._get_param("SubscriptionName")
        sub = self.dms_backend.delete_event_subscription(
            subscription_name=subscription_name
        )
        return json.dumps({"EventSubscription": sub.to_dict()})

    def modify_event_subscription(self) -> str:
        params = json.loads(self.body)
        sub = self.dms_backend.modify_event_subscription(
            subscription_name=params.get("SubscriptionName"),
            sns_topic_arn=params.get("SnsTopicArn"),
            source_type=params.get("SourceType"),
            event_categories=params.get("EventCategories"),
            enabled=params.get("Enabled"),
        )
        return json.dumps({"EventSubscription": sub.to_dict()})

    # ── Certificates ─────────────────────────────────────────────────

    def import_certificate(self) -> str:
        params = json.loads(self.body)
        cert = self.dms_backend.import_certificate(
            certificate_identifier=params.get("CertificateIdentifier"),
            certificate_pem=params.get("CertificatePem"),
            certificate_wallet=params.get("CertificateWallet"),
            tags=params.get("Tags"),
        )
        return json.dumps({"Certificate": cert.to_dict()})

    def describe_certificates(self) -> str:
        params = json.loads(self.body)
        certs = self.dms_backend.describe_certificates(
            filters=params.get("Filters"),
            max_records=params.get("MaxRecords"),
            marker=params.get("Marker"),
        )
        return json.dumps({"Certificates": [c.to_dict() for c in certs]})

    def delete_certificate(self) -> str:
        certificate_arn = self._get_param("CertificateArn")
        cert = self.dms_backend.delete_certificate(
            certificate_arn=certificate_arn
        )
        return json.dumps({"Certificate": cert.to_dict()})

    # ── Replication Configs (Serverless) ─────────────────────────────

    def create_replication_config(self) -> str:
        params = json.loads(self.body)
        config = self.dms_backend.create_replication_config(
            replication_config_identifier=params.get("ReplicationConfigIdentifier"),
            source_endpoint_arn=params.get("SourceEndpointArn"),
            target_endpoint_arn=params.get("TargetEndpointArn"),
            compute_config=params.get("ComputeConfig", {}),
            replication_type=params.get("ReplicationType"),
            table_mappings=params.get("TableMappings"),
            replication_settings=params.get("ReplicationSettings"),
            supplemental_settings=params.get("SupplementalSettings"),
            resource_identifier=params.get("ResourceIdentifier"),
            tags=params.get("Tags"),
        )
        return json.dumps({"ReplicationConfig": config.to_dict()})

    def describe_replication_configs(self) -> str:
        params = json.loads(self.body)
        configs = self.dms_backend.describe_replication_configs(
            filters=params.get("Filters"),
            max_records=params.get("MaxRecords"),
            marker=params.get("Marker"),
        )
        return json.dumps(
            {"ReplicationConfigs": [c.to_dict() for c in configs]}
        )

    def delete_replication_config(self) -> str:
        replication_config_arn = self._get_param("ReplicationConfigArn")
        self.dms_backend.delete_replication_config(
            replication_config_arn=replication_config_arn
        )
        return json.dumps({})

    def modify_replication_config(self) -> str:
        params = json.loads(self.body)
        config = self.dms_backend.modify_replication_config(
            replication_config_arn=params.get("ReplicationConfigArn"),
            replication_config_identifier=params.get("ReplicationConfigIdentifier"),
            replication_type=params.get("ReplicationType"),
            table_mappings=params.get("TableMappings"),
            replication_settings=params.get("ReplicationSettings"),
            supplemental_settings=params.get("SupplementalSettings"),
            compute_config=params.get("ComputeConfig"),
            source_endpoint_arn=params.get("SourceEndpointArn"),
            target_endpoint_arn=params.get("TargetEndpointArn"),
        )
        return json.dumps({"ReplicationConfig": config.to_dict()})

    def start_replication(self) -> str:
        params = json.loads(self.body)
        config = self.dms_backend.start_replication(
            replication_config_arn=params.get("ReplicationConfigArn"),
            start_replication_type=params.get("StartReplicationType"),
            cdc_start_time=params.get("CdcStartTime"),
            cdc_start_position=params.get("CdcStartPosition"),
        )
        replication = {
            "ReplicationConfigIdentifier": config.replication_config_identifier,
            "ReplicationConfigArn": config.arn,
            "SourceEndpointArn": config.source_endpoint_arn,
            "TargetEndpointArn": config.target_endpoint_arn,
            "ReplicationType": config.replication_type,
            "Status": config.status,
        }
        return json.dumps({"Replication": replication})

    def stop_replication(self) -> str:
        replication_config_arn = self._get_param("ReplicationConfigArn")
        config = self.dms_backend.stop_replication(
            replication_config_arn=replication_config_arn
        )
        replication = {
            "ReplicationConfigIdentifier": config.replication_config_identifier,
            "ReplicationConfigArn": config.arn,
            "SourceEndpointArn": config.source_endpoint_arn,
            "TargetEndpointArn": config.target_endpoint_arn,
            "ReplicationType": config.replication_type,
            "Status": config.status,
        }
        return json.dumps({"Replication": replication})

    def describe_replications(self) -> str:
        params = json.loads(self.body)
        replications = self.dms_backend.describe_replications(
            filters=params.get("Filters"),
            max_records=params.get("MaxRecords"),
            marker=params.get("Marker"),
        )
        return json.dumps({"Replications": replications})

    # ── Data Providers ───────────────────────────────────────────────

    def create_data_provider(self) -> str:
        params = json.loads(self.body)
        dp = self.dms_backend.create_data_provider(
            data_provider_name=params.get("DataProviderName"),
            engine=params.get("Engine"),
            settings=params.get("Settings", {}),
            description=params.get("Description"),
            tags=params.get("Tags"),
        )
        return json.dumps({"DataProvider": dp.to_dict()})

    def describe_data_providers(self) -> str:
        params = json.loads(self.body)
        providers = self.dms_backend.describe_data_providers(
            filters=params.get("Filters"),
            max_records=params.get("MaxRecords"),
            marker=params.get("Marker"),
        )
        return json.dumps(
            {"DataProviders": [p.to_dict() for p in providers]}
        )

    def modify_data_provider(self) -> str:
        params = json.loads(self.body)
        dp = self.dms_backend.modify_data_provider(
            data_provider_identifier=params.get("DataProviderIdentifier"),
            data_provider_name=params.get("DataProviderName"),
            engine=params.get("Engine"),
            settings=params.get("Settings"),
            description=params.get("Description"),
            exact_settings=params.get("ExactSettings"),
        )
        return json.dumps({"DataProvider": dp.to_dict()})

    def delete_data_provider(self) -> str:
        data_provider_identifier = self._get_param("DataProviderIdentifier")
        dp = self.dms_backend.delete_data_provider(
            data_provider_identifier=data_provider_identifier
        )
        return json.dumps({"DataProvider": dp.to_dict()})

    # ── Instance Profiles ────────────────────────────────────────────

    def create_instance_profile(self) -> str:
        params = json.loads(self.body)
        ip = self.dms_backend.create_instance_profile(
            instance_profile_name=params.get("InstanceProfileName"),
            availability_zone=params.get("AvailabilityZone"),
            kms_key_arn=params.get("KmsKeyArn"),
            publicly_accessible=params.get("PubliclyAccessible"),
            network_type=params.get("NetworkType"),
            description=params.get("Description"),
            subnet_group_identifier=params.get("SubnetGroupIdentifier"),
            vpc_security_groups=params.get("VpcSecurityGroups"),
            tags=params.get("Tags"),
        )
        return json.dumps({"InstanceProfile": ip.to_dict()})

    def describe_instance_profiles(self) -> str:
        params = json.loads(self.body)
        profiles = self.dms_backend.describe_instance_profiles(
            filters=params.get("Filters"),
            max_records=params.get("MaxRecords"),
            marker=params.get("Marker"),
        )
        return json.dumps(
            {"InstanceProfiles": [p.to_dict() for p in profiles]}
        )

    def modify_instance_profile(self) -> str:
        params = json.loads(self.body)
        ip = self.dms_backend.modify_instance_profile(
            instance_profile_identifier=params.get("InstanceProfileIdentifier"),
            instance_profile_name=params.get("InstanceProfileName"),
            availability_zone=params.get("AvailabilityZone"),
            kms_key_arn=params.get("KmsKeyArn"),
            publicly_accessible=params.get("PubliclyAccessible"),
            network_type=params.get("NetworkType"),
            description=params.get("Description"),
            subnet_group_identifier=params.get("SubnetGroupIdentifier"),
            vpc_security_groups=params.get("VpcSecurityGroups"),
        )
        return json.dumps({"InstanceProfile": ip.to_dict()})

    def delete_instance_profile(self) -> str:
        instance_profile_identifier = self._get_param(
            "InstanceProfileIdentifier"
        )
        ip = self.dms_backend.delete_instance_profile(
            instance_profile_identifier=instance_profile_identifier
        )
        return json.dumps({"InstanceProfile": ip.to_dict()})

    # ── Migration Projects ───────────────────────────────────────────

    def create_migration_project(self) -> str:
        params = json.loads(self.body)
        mp = self.dms_backend.create_migration_project(
            migration_project_name=params.get("MigrationProjectName"),
            source_data_provider_descriptors=params.get(
                "SourceDataProviderDescriptors"
            ),
            target_data_provider_descriptors=params.get(
                "TargetDataProviderDescriptors"
            ),
            instance_profile_identifier=params.get("InstanceProfileIdentifier"),
            transformation_rules=params.get("TransformationRules"),
            description=params.get("Description"),
            schema_conversion_application_attributes=params.get(
                "SchemaConversionApplicationAttributes"
            ),
            tags=params.get("Tags"),
        )
        return json.dumps({"MigrationProject": mp.to_dict()})

    def describe_migration_projects(self) -> str:
        params = json.loads(self.body)
        projects = self.dms_backend.describe_migration_projects(
            filters=params.get("Filters"),
            max_records=params.get("MaxRecords"),
            marker=params.get("Marker"),
        )
        return json.dumps(
            {"MigrationProjects": [p.to_dict() for p in projects]}
        )

    def modify_migration_project(self) -> str:
        params = json.loads(self.body)
        mp = self.dms_backend.modify_migration_project(
            migration_project_identifier=params.get("MigrationProjectIdentifier"),
            migration_project_name=params.get("MigrationProjectName"),
            source_data_provider_descriptors=params.get(
                "SourceDataProviderDescriptors"
            ),
            target_data_provider_descriptors=params.get(
                "TargetDataProviderDescriptors"
            ),
            instance_profile_identifier=params.get("InstanceProfileIdentifier"),
            transformation_rules=params.get("TransformationRules"),
            description=params.get("Description"),
            schema_conversion_application_attributes=params.get(
                "SchemaConversionApplicationAttributes"
            ),
        )
        return json.dumps({"MigrationProject": mp.to_dict()})

    def delete_migration_project(self) -> str:
        migration_project_identifier = self._get_param(
            "MigrationProjectIdentifier"
        )
        mp = self.dms_backend.delete_migration_project(
            migration_project_identifier=migration_project_identifier
        )
        return json.dumps({"MigrationProject": mp.to_dict()})

    # ── Data Migrations ──────────────────────────────────────────────

    def create_data_migration(self) -> str:
        params = json.loads(self.body)
        dm = self.dms_backend.create_data_migration(
            data_migration_name=params.get("DataMigrationName"),
            migration_project_identifier=params.get("MigrationProjectIdentifier"),
            data_migration_type=params.get("DataMigrationType"),
            service_access_role_arn=params.get("ServiceAccessRoleArn"),
            source_data_settings=params.get("SourceDataSettings"),
            enable_cloudwatch_logs=params.get("EnableCloudwatchLogs"),
            tags=params.get("Tags"),
        )
        return json.dumps({"DataMigration": dm.to_dict()})

    def describe_data_migrations(self) -> str:
        params = json.loads(self.body)
        migrations = self.dms_backend.describe_data_migrations(
            filters=params.get("Filters"),
            max_records=params.get("MaxRecords"),
            marker=params.get("Marker"),
        )
        return json.dumps(
            {"DataMigrations": [m.to_dict() for m in migrations]}
        )

    def modify_data_migration(self) -> str:
        params = json.loads(self.body)
        dm = self.dms_backend.modify_data_migration(
            data_migration_identifier=params.get("DataMigrationIdentifier"),
            data_migration_name=params.get("DataMigrationName"),
            data_migration_type=params.get("DataMigrationType"),
            service_access_role_arn=params.get("ServiceAccessRoleArn"),
            source_data_settings=params.get("SourceDataSettings"),
            enable_cloudwatch_logs=params.get("EnableCloudwatchLogs"),
        )
        return json.dumps({"DataMigration": dm.to_dict()})

    def delete_data_migration(self) -> str:
        data_migration_identifier = self._get_param("DataMigrationIdentifier")
        dm = self.dms_backend.delete_data_migration(
            data_migration_identifier=data_migration_identifier
        )
        return json.dumps({"DataMigration": dm.to_dict()})

    def start_data_migration(self) -> str:
        params = json.loads(self.body)
        dm = self.dms_backend.start_data_migration(
            data_migration_identifier=params.get("DataMigrationIdentifier"),
            start_type=params.get("StartType"),
        )
        return json.dumps({"DataMigration": dm.to_dict()})

    def stop_data_migration(self) -> str:
        data_migration_identifier = self._get_param("DataMigrationIdentifier")
        dm = self.dms_backend.stop_data_migration(
            data_migration_identifier=data_migration_identifier
        )
        return json.dumps({"DataMigration": dm.to_dict()})

    # ── Account / Describe stubs ─────────────────────────────────────

    def describe_account_attributes(self) -> str:
        result = self.dms_backend.describe_account_attributes()
        return json.dumps(result)

    def describe_endpoint_types(self) -> str:
        params = json.loads(self.body)
        types = self.dms_backend.describe_endpoint_types(
            filters=params.get("Filters"),
            max_records=params.get("MaxRecords"),
            marker=params.get("Marker"),
        )
        return json.dumps({"SupportedEndpointTypes": types})

    def describe_endpoint_settings(self) -> str:
        params = json.loads(self.body)
        settings = self.dms_backend.describe_endpoint_settings(
            engine_name=params.get("EngineName"),
            max_records=params.get("MaxRecords"),
            marker=params.get("Marker"),
        )
        return json.dumps({"EndpointSettings": settings})

    def describe_orderable_replication_instances(self) -> str:
        params = json.loads(self.body)
        instances = self.dms_backend.describe_orderable_replication_instances(
            max_records=params.get("MaxRecords"),
            marker=params.get("Marker"),
        )
        return json.dumps({"OrderableReplicationInstances": instances})

    def describe_event_categories(self) -> str:
        params = json.loads(self.body)
        categories = self.dms_backend.describe_event_categories(
            source_type=params.get("SourceType"),
            filters=params.get("Filters"),
        )
        return json.dumps({"EventCategoryGroupList": categories})

    def describe_events(self) -> str:
        params = json.loads(self.body)
        events = self.dms_backend.describe_events(
            source_identifier=params.get("SourceIdentifier"),
            source_type=params.get("SourceType"),
            start_time=params.get("StartTime"),
            end_time=params.get("EndTime"),
            duration=params.get("Duration"),
            event_categories=params.get("EventCategories"),
            filters=params.get("Filters"),
            max_records=params.get("MaxRecords"),
            marker=params.get("Marker"),
        )
        return json.dumps({"Events": events})

    def describe_table_statistics(self) -> str:
        params = json.loads(self.body)
        result = self.dms_backend.describe_table_statistics(
            replication_task_arn=params.get("ReplicationTaskArn"),
            max_records=params.get("MaxRecords"),
            marker=params.get("Marker"),
            filters=params.get("Filters"),
        )
        return json.dumps(result)

    def describe_replication_table_statistics(self) -> str:
        params = json.loads(self.body)
        result = self.dms_backend.describe_replication_table_statistics(
            replication_config_arn=params.get("ReplicationConfigArn"),
            max_records=params.get("MaxRecords"),
            marker=params.get("Marker"),
            filters=params.get("Filters"),
        )
        return json.dumps(result)

    def describe_schemas(self) -> str:
        params = json.loads(self.body)
        schemas = self.dms_backend.describe_schemas(
            endpoint_arn=params.get("EndpointArn"),
            max_records=params.get("MaxRecords"),
            marker=params.get("Marker"),
        )
        return json.dumps({"Schemas": schemas})

    def refresh_schemas(self) -> str:
        params = json.loads(self.body)
        result = self.dms_backend.refresh_schemas(
            endpoint_arn=params.get("EndpointArn"),
            replication_instance_arn=params.get("ReplicationInstanceArn"),
        )
        return json.dumps(result)

    def describe_refresh_schemas_status(self) -> str:
        endpoint_arn = self._get_param("EndpointArn")
        result = self.dms_backend.describe_refresh_schemas_status(
            endpoint_arn=endpoint_arn
        )
        return json.dumps(result)

    def reload_tables(self) -> str:
        params = json.loads(self.body)
        result = self.dms_backend.reload_tables(
            replication_task_arn=params.get("ReplicationTaskArn"),
            tables_to_reload=params.get("TablesToReload", []),
            reload_option=params.get("ReloadOption"),
        )
        return json.dumps(result)

    def reload_replication_tables(self) -> str:
        params = json.loads(self.body)
        result = self.dms_backend.reload_replication_tables(
            replication_config_arn=params.get("ReplicationConfigArn"),
            tables_to_reload=params.get("TablesToReload", []),
            reload_option=params.get("ReloadOption"),
        )
        return json.dumps(result)

    def describe_applicable_individual_assessments(self) -> str:
        params = json.loads(self.body)
        assessments = self.dms_backend.describe_applicable_individual_assessments(
            replication_task_arn=params.get("ReplicationTaskArn"),
            replication_instance_arn=params.get("ReplicationInstanceArn"),
            source_engine_name=params.get("SourceEngineName"),
            target_engine_name=params.get("TargetEngineName"),
            migration_type=params.get("MigrationType"),
            max_records=params.get("MaxRecords"),
            marker=params.get("Marker"),
        )
        return json.dumps({"IndividualAssessmentNames": assessments})

    def start_replication_task_assessment(self) -> str:
        replication_task_arn = self._get_param("ReplicationTaskArn")
        task = self.dms_backend.start_replication_task_assessment(
            replication_task_arn=replication_task_arn
        )
        return json.dumps({"ReplicationTask": task.to_dict()})

    def describe_replication_task_assessment_results(self) -> str:
        params = json.loads(self.body)
        results = self.dms_backend.describe_replication_task_assessment_results(
            replication_task_arn=params.get("ReplicationTaskArn"),
            max_records=params.get("MaxRecords"),
            marker=params.get("Marker"),
        )
        return json.dumps({"ReplicationTaskAssessmentResults": results})

    def start_replication_task_assessment_run(self) -> str:
        params = json.loads(self.body)
        result = self.dms_backend.start_replication_task_assessment_run(
            replication_task_arn=params.get("ReplicationTaskArn"),
            service_access_role_arn=params.get("ServiceAccessRoleArn"),
            result_location_bucket=params.get("ResultLocationBucket"),
            assessment_run_name=params.get("AssessmentRunName"),
            result_location_folder=params.get("ResultLocationFolder"),
            result_encryption_mode=params.get("ResultEncryptionMode"),
            result_kms_key_arn=params.get("ResultKmsKeyArn"),
            include_only=params.get("IncludeOnly"),
            exclude=params.get("Exclude"),
            tags=params.get("Tags"),
        )
        return json.dumps(result)

    def cancel_replication_task_assessment_run(self) -> str:
        arn = self._get_param("ReplicationTaskAssessmentRunArn")
        result = self.dms_backend.cancel_replication_task_assessment_run(
            replication_task_assessment_run_arn=arn
        )
        return json.dumps(result)

    def delete_replication_task_assessment_run(self) -> str:
        arn = self._get_param("ReplicationTaskAssessmentRunArn")
        result = self.dms_backend.delete_replication_task_assessment_run(
            replication_task_assessment_run_arn=arn
        )
        return json.dumps(result)

    def describe_replication_task_assessment_runs(self) -> str:
        params = json.loads(self.body)
        runs = self.dms_backend.describe_replication_task_assessment_runs(
            filters=params.get("Filters"),
            max_records=params.get("MaxRecords"),
            marker=params.get("Marker"),
        )
        return json.dumps({"ReplicationTaskAssessmentRuns": runs})

    def describe_replication_task_individual_assessments(self) -> str:
        params = json.loads(self.body)
        assessments = self.dms_backend.describe_replication_task_individual_assessments(
            filters=params.get("Filters"),
            max_records=params.get("MaxRecords"),
            marker=params.get("Marker"),
        )
        return json.dumps(
            {"ReplicationTaskIndividualAssessments": assessments}
        )

    def describe_pending_maintenance_actions(self) -> str:
        params = json.loads(self.body)
        actions = self.dms_backend.describe_pending_maintenance_actions(
            replication_instance_arn=params.get("ReplicationInstanceArn"),
            filters=params.get("Filters"),
            max_records=params.get("MaxRecords"),
            marker=params.get("Marker"),
        )
        return json.dumps({"PendingMaintenanceActions": actions})

    def apply_pending_maintenance_action(self) -> str:
        params = json.loads(self.body)
        result = self.dms_backend.apply_pending_maintenance_action(
            replication_instance_arn=params.get("ReplicationInstanceArn"),
            apply_action=params.get("ApplyAction"),
            opt_in_type=params.get("OptInType"),
        )
        return json.dumps(result)

    def describe_engine_versions(self) -> str:
        params = json.loads(self.body)
        versions = self.dms_backend.describe_engine_versions(
            max_records=params.get("MaxRecords"),
            marker=params.get("Marker"),
        )
        return json.dumps({"EngineVersions": versions})

    def update_subscriptions_to_event_bridge(self) -> str:
        params = json.loads(self.body)
        result = self.dms_backend.update_subscriptions_to_event_bridge(
            force_move=params.get("ForceMove")
        )
        return json.dumps(result)

    # ── Fleet Advisor ────────────────────────────────────────────────

    def create_fleet_advisor_collector(self) -> str:
        params = json.loads(self.body)
        result = self.dms_backend.create_fleet_advisor_collector(
            collector_name=params.get("CollectorName"),
            description=params.get("Description"),
            service_access_role_arn=params.get("ServiceAccessRoleArn"),
            s3_bucket_name=params.get("S3BucketName"),
        )
        return json.dumps(result)

    def delete_fleet_advisor_collector(self) -> str:
        collector_referenced_id = self._get_param("CollectorReferencedId")
        self.dms_backend.delete_fleet_advisor_collector(
            collector_referenced_id=collector_referenced_id
        )
        return json.dumps({})

    def delete_fleet_advisor_databases(self) -> str:
        database_ids = self._get_param("DatabaseIds")
        deleted = self.dms_backend.delete_fleet_advisor_databases(
            database_ids=database_ids
        )
        return json.dumps({"DatabaseIds": deleted})

    def describe_fleet_advisor_collectors(self) -> str:
        params = json.loads(self.body)
        collectors = self.dms_backend.describe_fleet_advisor_collectors(
            filters=params.get("Filters"),
            max_records=params.get("MaxRecords"),
            next_token=params.get("NextToken"),
        )
        return json.dumps({"Collectors": collectors})

    def describe_fleet_advisor_databases(self) -> str:
        params = json.loads(self.body)
        databases = self.dms_backend.describe_fleet_advisor_databases(
            filters=params.get("Filters"),
            max_records=params.get("MaxRecords"),
            next_token=params.get("NextToken"),
        )
        return json.dumps({"Databases": databases})

    def describe_fleet_advisor_lsa_analysis(self) -> str:
        params = json.loads(self.body)
        analysis = self.dms_backend.describe_fleet_advisor_lsa_analysis(
            max_records=params.get("MaxRecords"),
            next_token=params.get("NextToken"),
        )
        return json.dumps({"Analysis": analysis})

    def describe_fleet_advisor_schema_object_summary(self) -> str:
        params = json.loads(self.body)
        summary = self.dms_backend.describe_fleet_advisor_schema_object_summary(
            filters=params.get("Filters"),
            max_records=params.get("MaxRecords"),
            next_token=params.get("NextToken"),
        )
        return json.dumps({"FleetAdvisorSchemaObjects": summary})

    def describe_fleet_advisor_schemas(self) -> str:
        params = json.loads(self.body)
        schemas = self.dms_backend.describe_fleet_advisor_schemas(
            filters=params.get("Filters"),
            max_records=params.get("MaxRecords"),
            next_token=params.get("NextToken"),
        )
        return json.dumps({"FleetAdvisorSchemas": schemas})

    def run_fleet_advisor_lsa_analysis(self) -> str:
        result = self.dms_backend.run_fleet_advisor_lsa_analysis()
        return json.dumps(result)

    # ── Recommendations ──────────────────────────────────────────────

    def start_recommendations(self) -> str:
        params = json.loads(self.body)
        self.dms_backend.start_recommendations(
            database_id=params.get("DatabaseId"),
            settings=params.get("Settings", {}),
        )
        return json.dumps({})

    def batch_start_recommendations(self) -> str:
        params = json.loads(self.body)
        errors = self.dms_backend.batch_start_recommendations(
            data=params.get("Data")
        )
        return json.dumps({"ErrorEntries": errors})

    def describe_recommendations(self) -> str:
        params = json.loads(self.body)
        recommendations = self.dms_backend.describe_recommendations(
            filters=params.get("Filters"),
            max_records=params.get("MaxRecords"),
            next_token=params.get("NextToken"),
        )
        return json.dumps({"Recommendations": recommendations})

    def describe_recommendation_limitations(self) -> str:
        params = json.loads(self.body)
        limitations = self.dms_backend.describe_recommendation_limitations(
            filters=params.get("Filters"),
            max_records=params.get("MaxRecords"),
            next_token=params.get("NextToken"),
        )
        return json.dumps({"Limitations": limitations})

    # ── Metadata model / conversion ──────────────────────────────────

    def describe_conversion_configuration(self) -> str:
        migration_project_identifier = self._get_param(
            "MigrationProjectIdentifier"
        )
        result = self.dms_backend.describe_conversion_configuration(
            migration_project_identifier=migration_project_identifier
        )
        return json.dumps(result)

    def modify_conversion_configuration(self) -> str:
        params = json.loads(self.body)
        result = self.dms_backend.modify_conversion_configuration(
            migration_project_identifier=params.get("MigrationProjectIdentifier"),
            conversion_configuration=params.get("ConversionConfiguration"),
        )
        return json.dumps(result)

    def start_metadata_model_conversion(self) -> str:
        params = json.loads(self.body)
        result = self.dms_backend.start_metadata_model_conversion(
            migration_project_identifier=params.get("MigrationProjectIdentifier"),
            selection_rules=params.get("SelectionRules"),
        )
        return json.dumps(result)

    def start_metadata_model_assessment(self) -> str:
        params = json.loads(self.body)
        result = self.dms_backend.start_metadata_model_assessment(
            migration_project_identifier=params.get("MigrationProjectIdentifier"),
            selection_rules=params.get("SelectionRules"),
        )
        return json.dumps(result)

    def start_metadata_model_export_as_script(self) -> str:
        params = json.loads(self.body)
        result = self.dms_backend.start_metadata_model_export_as_script(
            migration_project_identifier=params.get("MigrationProjectIdentifier"),
            selection_rules=params.get("SelectionRules"),
            origin=params.get("Origin"),
            file_name=params.get("FileName"),
        )
        return json.dumps(result)

    def start_metadata_model_export_to_target(self) -> str:
        params = json.loads(self.body)
        result = self.dms_backend.start_metadata_model_export_to_target(
            migration_project_identifier=params.get("MigrationProjectIdentifier"),
            selection_rules=params.get("SelectionRules"),
            overwrite_extension_pack=params.get("OverwriteExtensionPack"),
        )
        return json.dumps(result)

    def start_metadata_model_import(self) -> str:
        params = json.loads(self.body)
        result = self.dms_backend.start_metadata_model_import(
            migration_project_identifier=params.get("MigrationProjectIdentifier"),
            selection_rules=params.get("SelectionRules"),
            origin=params.get("Origin"),
            refresh=params.get("Refresh"),
        )
        return json.dumps(result)

    def start_metadata_model_creation(self) -> str:
        params = json.loads(self.body)
        result = self.dms_backend.start_metadata_model_creation(
            migration_project_identifier=params.get("MigrationProjectIdentifier"),
            selection_rules=params.get("SelectionRules"),
        )
        return json.dumps(result)

    def cancel_metadata_model_conversion(self) -> str:
        migration_project_identifier = self._get_param(
            "MigrationProjectIdentifier"
        )
        result = self.dms_backend.cancel_metadata_model_conversion(
            migration_project_identifier=migration_project_identifier
        )
        return json.dumps(result)

    def cancel_metadata_model_creation(self) -> str:
        migration_project_identifier = self._get_param(
            "MigrationProjectIdentifier"
        )
        result = self.dms_backend.cancel_metadata_model_creation(
            migration_project_identifier=migration_project_identifier
        )
        return json.dumps(result)

    def describe_metadata_model_conversions(self) -> str:
        params = json.loads(self.body)
        result = self.dms_backend.describe_metadata_model_conversions(
            migration_project_identifier=params.get("MigrationProjectIdentifier"),
            filters=params.get("Filters"),
            max_records=params.get("MaxRecords"),
            marker=params.get("Marker"),
        )
        return json.dumps({"Requests": result})

    def describe_metadata_model_exports_as_script(self) -> str:
        params = json.loads(self.body)
        result = self.dms_backend.describe_metadata_model_exports_as_script(
            migration_project_identifier=params.get("MigrationProjectIdentifier"),
            filters=params.get("Filters"),
            max_records=params.get("MaxRecords"),
            marker=params.get("Marker"),
        )
        return json.dumps({"Requests": result})

    def describe_metadata_model_exports_to_target(self) -> str:
        params = json.loads(self.body)
        result = self.dms_backend.describe_metadata_model_exports_to_target(
            migration_project_identifier=params.get("MigrationProjectIdentifier"),
            filters=params.get("Filters"),
            max_records=params.get("MaxRecords"),
            marker=params.get("Marker"),
        )
        return json.dumps({"Requests": result})

    def describe_metadata_model_imports(self) -> str:
        params = json.loads(self.body)
        result = self.dms_backend.describe_metadata_model_imports(
            migration_project_identifier=params.get("MigrationProjectIdentifier"),
            filters=params.get("Filters"),
            max_records=params.get("MaxRecords"),
            marker=params.get("Marker"),
        )
        return json.dumps({"Requests": result})

    def describe_metadata_model_assessments(self) -> str:
        params = json.loads(self.body)
        result = self.dms_backend.describe_metadata_model_assessments(
            migration_project_identifier=params.get("MigrationProjectIdentifier"),
            filters=params.get("Filters"),
            max_records=params.get("MaxRecords"),
            marker=params.get("Marker"),
        )
        return json.dumps({"Requests": result})

    def describe_metadata_model_creations(self) -> str:
        params = json.loads(self.body)
        result = self.dms_backend.describe_metadata_model_creations(
            migration_project_identifier=params.get("MigrationProjectIdentifier"),
            filters=params.get("Filters"),
            max_records=params.get("MaxRecords"),
            marker=params.get("Marker"),
        )
        return json.dumps({"Requests": result})

    def describe_metadata_model(self) -> str:
        params = json.loads(self.body)
        result = self.dms_backend.describe_metadata_model(
            migration_project_identifier=params.get("MigrationProjectIdentifier"),
            filters=params.get("Filters"),
            max_records=params.get("MaxRecords"),
            marker=params.get("Marker"),
        )
        return json.dumps({"Requests": result})

    def describe_metadata_model_children(self) -> str:
        params = json.loads(self.body)
        result = self.dms_backend.describe_metadata_model_children(
            migration_project_identifier=params.get("MigrationProjectIdentifier"),
            parent_path=params.get("ParentPath"),
            filters=params.get("Filters"),
            max_records=params.get("MaxRecords"),
            marker=params.get("Marker"),
        )
        return json.dumps({"Requests": result})

    def export_metadata_model_assessment(self) -> str:
        params = json.loads(self.body)
        result = self.dms_backend.export_metadata_model_assessment(
            migration_project_identifier=params.get("MigrationProjectIdentifier"),
            selection_rules=params.get("SelectionRules"),
            file_name=params.get("FileName"),
            assessment_report_types=params.get("AssessmentReportTypes"),
        )
        return json.dumps(result)

    def start_extension_pack_association(self) -> str:
        migration_project_identifier = self._get_param(
            "MigrationProjectIdentifier"
        )
        result = self.dms_backend.start_extension_pack_association(
            migration_project_identifier=migration_project_identifier
        )
        return json.dumps(result)

    def describe_extension_pack_associations(self) -> str:
        params = json.loads(self.body)
        result = self.dms_backend.describe_extension_pack_associations(
            migration_project_identifier=params.get("MigrationProjectIdentifier"),
            filters=params.get("Filters"),
            max_records=params.get("MaxRecords"),
            marker=params.get("Marker"),
        )
        return json.dumps({"Requests": result})

    def get_target_selection_rules(self) -> str:
        migration_project_identifier = self._get_param(
            "MigrationProjectIdentifier"
        )
        result = self.dms_backend.get_target_selection_rules(
            migration_project_identifier=migration_project_identifier
        )
        return json.dumps(result)
