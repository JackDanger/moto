from collections.abc import Iterable
from datetime import datetime
from typing import Any, Optional

from moto.core.base_backend import BackendDict, BaseBackend
from moto.core.common_models import BaseModel
from moto.core.utils import utcnow
from moto.moto_api._internal.managed_state_model import ManagedState
from moto.utilities.tagging_service import TaggingService
from moto.utilities.utils import get_partition

from .exceptions import (
    InvalidResourceStateFault,
    ResourceAlreadyExistsFault,
    ResourceNotFoundFault,
    ValidationError,
)
from .utils import filter_tasks, random_id


class DatabaseMigrationServiceBackend(BaseBackend):
    def __init__(self, region_name: str, account_id: str):
        super().__init__(region_name, account_id)
        self.replication_tasks: dict[str, FakeReplicationTask] = {}
        self.replication_instances: dict[str, FakeReplicationInstance] = {}
        self.endpoints: dict[str, Endpoint] = {}
        self.replication_subnet_groups: dict[str, FakeReplicationSubnetGroup] = {}
        self.connections: list[FakeConnection] = []
        self.event_subscriptions: dict[str, FakeEventSubscription] = {}
        self.certificates: dict[str, FakeCertificate] = {}
        self.replication_configs: dict[str, FakeReplicationConfig] = {}
        self.data_providers: dict[str, FakeDataProvider] = {}
        self.instance_profiles: dict[str, FakeInstanceProfile] = {}
        self.migration_projects: dict[str, FakeMigrationProject] = {}
        self.data_migrations: dict[str, FakeDataMigration] = {}
        self.tagger = TaggingService()

    # ── Tagging ──────────────────────────────────────────────────────

    def add_tags_to_resource(
        self, resource_arn: str, tags: list[dict[str, str]]
    ) -> None:
        self.tagger.tag_resource(resource_arn, tags)

    def remove_tags_from_resource(
        self, resource_arn: str, tag_keys: list[str]
    ) -> None:
        self.tagger.untag_resource_using_names(resource_arn, tag_keys)

    def list_tags_for_resource(
        self, resource_arn_list: list[str]
    ) -> list[dict[str, Any]]:
        result = []
        for resource_arn in resource_arn_list:
            tags = self.tagger.get_tag_dict_for_resource(resource_arn)
            for key, value in tags.items():
                result.append({"Key": key, "ResourceArn": resource_arn, "Value": value})
        return result

    # ── Replication Tasks ────────────────────────────────────────────

    def create_replication_task(
        self,
        replication_task_identifier: str,
        source_endpoint_arn: str,
        target_endpoint_arn: str,
        replication_instance_arn: str,
        migration_type: str,
        table_mappings: str,
        replication_task_settings: str,
        tags: Optional[list[dict[str, str]]] = None,
    ) -> "FakeReplicationTask":
        replication_task = FakeReplicationTask(
            replication_task_identifier=replication_task_identifier,
            source_endpoint_arn=source_endpoint_arn,
            target_endpoint_arn=target_endpoint_arn,
            replication_instance_arn=replication_instance_arn,
            migration_type=migration_type,
            table_mappings=table_mappings,
            replication_task_settings=replication_task_settings,
            account_id=self.account_id,
            region_name=self.region_name,
        )

        if self.replication_tasks.get(replication_task.arn):
            raise ResourceAlreadyExistsFault(
                "The resource you are attempting to create already exists."
            )

        self.replication_tasks[replication_task.arn] = replication_task

        if tags:
            self.tagger.tag_resource(replication_task.arn, tags)

        return replication_task

    def start_replication_task(
        self, replication_task_arn: str
    ) -> "FakeReplicationTask":
        if not self.replication_tasks.get(replication_task_arn):
            raise ResourceNotFoundFault("Replication task could not be found.")

        return self.replication_tasks[replication_task_arn].start()

    def stop_replication_task(self, replication_task_arn: str) -> "FakeReplicationTask":
        if not self.replication_tasks.get(replication_task_arn):
            raise ResourceNotFoundFault("Replication task could not be found.")

        return self.replication_tasks[replication_task_arn].stop()

    def delete_replication_task(
        self, replication_task_arn: str
    ) -> "FakeReplicationTask":
        if not self.replication_tasks.get(replication_task_arn):
            raise ResourceNotFoundFault("Replication task could not be found.")

        task = self.replication_tasks[replication_task_arn]
        task.delete()
        self.replication_tasks.pop(replication_task_arn)

        return task

    def describe_replication_tasks(
        self, filters: list[dict[str, Any]], max_records: int
    ) -> Iterable["FakeReplicationTask"]:
        replication_tasks = filter_tasks(list(self.replication_tasks.values()), filters)

        if max_records and max_records > 0:
            replication_tasks = replication_tasks[:max_records]

        return replication_tasks

    def modify_replication_task(
        self,
        replication_task_arn: str,
        replication_task_identifier: Optional[str] = None,
        migration_type: Optional[str] = None,
        table_mappings: Optional[str] = None,
        replication_task_settings: Optional[str] = None,
        cdc_start_time: Optional[str] = None,
        cdc_start_position: Optional[str] = None,
        cdc_stop_position: Optional[str] = None,
        task_data: Optional[str] = None,
    ) -> "FakeReplicationTask":
        if not self.replication_tasks.get(replication_task_arn):
            raise ResourceNotFoundFault("Replication task could not be found.")

        task = self.replication_tasks[replication_task_arn]
        if replication_task_identifier is not None:
            task.id = replication_task_identifier
        if migration_type is not None:
            task.migration_type = migration_type
        if table_mappings is not None:
            task.table_mappings = table_mappings
        if replication_task_settings is not None:
            task.replication_task_settings = replication_task_settings
        return task

    def move_replication_task(
        self,
        replication_task_arn: str,
        target_replication_instance_arn: str,
    ) -> "FakeReplicationTask":
        if not self.replication_tasks.get(replication_task_arn):
            raise ResourceNotFoundFault("Replication task could not be found.")

        task = self.replication_tasks[replication_task_arn]
        task.replication_instance_arn = target_replication_instance_arn
        return task

    # ── Replication Instances ────────────────────────────────────────

    def create_replication_instance(
        self,
        replication_instance_identifier: str,
        replication_instance_class: str,
        allocated_storage: Optional[int] = None,
        vpc_security_group_ids: Optional[list[str]] = None,
        availability_zone: Optional[str] = None,
        replication_subnet_group_identifier: Optional[str] = None,
        preferred_maintenance_window: Optional[str] = None,
        multi_az: Optional[bool] = False,
        engine_version: Optional[str] = None,
        auto_minor_version_upgrade: Optional[bool] = True,
        tags: Optional[list[dict[str, str]]] = None,
        kms_key_id: Optional[str] = None,
        publicly_accessible: Optional[bool] = True,
        dns_name_servers: Optional[str] = None,
        resource_identifier: Optional[str] = None,
        network_type: Optional[str] = None,
        kerberos_authentication_settings: Optional[dict[str, str]] = None,
    ) -> "FakeReplicationInstance":
        replication_instance = FakeReplicationInstance(
            replication_instance_identifier=replication_instance_identifier,
            replication_instance_class=replication_instance_class,
            allocated_storage=allocated_storage,
            vpc_security_group_ids=vpc_security_group_ids or [],
            availability_zone=availability_zone,
            replication_subnet_group_identifier=replication_subnet_group_identifier,
            preferred_maintenance_window=preferred_maintenance_window,
            multi_az=multi_az,
            engine_version=engine_version,
            auto_minor_version_upgrade=auto_minor_version_upgrade,
            tags=tags or [],
            kms_key_id=kms_key_id,
            publicly_accessible=publicly_accessible,
            dns_name_servers=dns_name_servers,
            resource_identifier=resource_identifier,
            network_type=network_type,
            kerberos_authentication_settings=kerberos_authentication_settings or {},
            account_id=self.account_id,
            region_name=self.region_name,
        )

        if self.replication_instances.get(replication_instance.arn):
            raise ResourceAlreadyExistsFault(
                "The resource you are attempting to create already exists."
            )

        self.replication_instances[replication_instance.arn] = replication_instance
        if tags:
            self.tagger.tag_resource(replication_instance.arn, tags)

        return replication_instance

    def describe_replication_instances(
        self,
        filters: Optional[list[dict[str, Any]]] = None,
        max_records: Optional[int] = None,
        marker: Optional[str] = None,
    ) -> list["FakeReplicationInstance"]:
        replication_instances = list(self.replication_instances.values())

        if filters:
            for filter_obj in filters:
                filter_name = filter_obj.get("Name", "")
                filter_values = filter_obj.get("Values", [])

                if filter_name == "replication-instance-id":
                    replication_instances = [
                        instance
                        for instance in replication_instances
                        if instance.id in filter_values
                    ]
                elif filter_name == "replication-instance-arn":
                    replication_instances = [
                        instance
                        for instance in replication_instances
                        if instance.arn in filter_values
                    ]
                elif filter_name == "replication-instance-class":
                    replication_instances = [
                        instance
                        for instance in replication_instances
                        if instance.replication_instance_class in filter_values
                    ]
                elif filter_name == "engine-version":
                    replication_instances = [
                        instance
                        for instance in replication_instances
                        if instance.engine_version in filter_values
                    ]
        for replication_instance in replication_instances:
            replication_instance.advance()
        return replication_instances

    def delete_replication_instance(
        self, replication_instance_arn: str
    ) -> "FakeReplicationInstance":
        if not self.replication_instances.get(replication_instance_arn):
            raise ResourceNotFoundFault("Replication instance could not be found.")

        replication_instance = self.replication_instances[replication_instance_arn]
        replication_instance.delete()
        self.replication_instances.pop(replication_instance_arn)

        # remove any connections we might have tested linked to this instance
        connections = [
            connection
            for connection in self.connections
            if connection.replication_instance_arn == replication_instance_arn
        ]
        for connection in connections:
            self.connections.remove(connection)

        return replication_instance

    def modify_replication_instance(
        self,
        replication_instance_arn: str,
        allocated_storage: Optional[int] = None,
        apply_immediately: Optional[bool] = None,
        replication_instance_class: Optional[str] = None,
        vpc_security_group_ids: Optional[list[str]] = None,
        preferred_maintenance_window: Optional[str] = None,
        multi_az: Optional[bool] = None,
        engine_version: Optional[str] = None,
        auto_minor_version_upgrade: Optional[bool] = None,
        replication_instance_identifier: Optional[str] = None,
        network_type: Optional[str] = None,
    ) -> "FakeReplicationInstance":
        if not self.replication_instances.get(replication_instance_arn):
            raise ResourceNotFoundFault("Replication instance could not be found.")

        instance = self.replication_instances[replication_instance_arn]
        if allocated_storage is not None:
            instance.allocated_storage = allocated_storage
        if replication_instance_class is not None:
            instance.replication_instance_class = replication_instance_class
        if vpc_security_group_ids is not None:
            instance.vpc_security_groups = [
                {"VpcSecurityGroupId": sg_id, "Status": "active"}
                for sg_id in vpc_security_group_ids
            ]
        if preferred_maintenance_window is not None:
            instance.preferred_maintenance_window = preferred_maintenance_window
        if multi_az is not None:
            instance.multi_az = multi_az
        if engine_version is not None:
            instance.engine_version = engine_version
        if auto_minor_version_upgrade is not None:
            instance.auto_minor_version_upgrade = auto_minor_version_upgrade
        if replication_instance_identifier is not None:
            instance.id = replication_instance_identifier
        if network_type is not None:
            instance.network_type = network_type
        return instance

    def reboot_replication_instance(
        self,
        replication_instance_arn: str,
        force_failover: Optional[bool] = None,
        force_planned_failover: Optional[bool] = None,
    ) -> "FakeReplicationInstance":
        if not self.replication_instances.get(replication_instance_arn):
            raise ResourceNotFoundFault("Replication instance could not be found.")

        instance = self.replication_instances[replication_instance_arn]
        instance.status = "rebooting"
        # Immediately transition back to available for mock
        instance.status = "available"
        return instance

    def describe_replication_instance_task_logs(
        self,
        replication_instance_arn: str,
        max_records: Optional[int] = None,
        marker: Optional[str] = None,
    ) -> dict[str, Any]:
        if not self.replication_instances.get(replication_instance_arn):
            raise ResourceNotFoundFault("Replication instance could not be found.")

        return {
            "ReplicationInstanceArn": replication_instance_arn,
            "ReplicationInstanceTaskLogs": [],
        }

    # ── Endpoints ────────────────────────────────────────────────────

    def create_endpoint(
        self,
        endpoint_identifier: str,
        endpoint_type: str,
        engine_name: str,
        username: str,
        password: str,
        server_name: str,
        port: int,
        database_name: str,
        extra_connection_attributes: str,
        kms_key_id: str,
        tags: Optional[list[dict[str, str]]],
        certificate_arn: str,
        ssl_mode: str,
        service_access_role_arn: str,
        external_table_definition: str,
        dynamo_db_settings: Optional[dict[str, Any]],
        s3_settings: Optional[dict[str, Any]],
        dms_transfer_settings: Optional[dict[str, Any]],
        mongo_db_settings: Optional[dict[str, Any]],
        kinesis_settings: Optional[dict[str, Any]],
        kafka_settings: Optional[dict[str, Any]],
        elasticsearch_settings: Optional[dict[str, Any]],
        neptune_settings: Optional[dict[str, Any]],
        redshift_settings: Optional[dict[str, Any]],
        postgre_sql_settings: Optional[dict[str, Any]],
        my_sql_settings: Optional[dict[str, Any]],
        oracle_settings: Optional[dict[str, Any]],
        sybase_settings: Optional[dict[str, Any]],
        microsoft_sql_server_settings: Optional[dict[str, Any]],
        ibm_db2_settings: Optional[dict[str, Any]],
        resource_identifier: Optional[str],
        doc_db_settings: Optional[dict[str, Any]],
        redis_settings: Optional[dict[str, Any]],
        gcp_my_sql_settings: Optional[dict[str, Any]],
        timestream_settings: Optional[dict[str, Any]],
    ) -> "Endpoint":
        if endpoint_type not in ["source", "target"]:
            raise ValidationError("Invalid endpoint type")

        endpoint = Endpoint(
            endpoint_identifier=endpoint_identifier,
            endpoint_type=endpoint_type,
            engine_name=engine_name,
            engine_display_name=engine_name,
            username=username,
            password=password,
            server_name=server_name,
            port=port,
            database_name=database_name,
            extra_connection_attributes=extra_connection_attributes,
            status="creating",
            kms_key_id=kms_key_id,
            certificate_arn=certificate_arn,
            ssl_mode=ssl_mode,
            service_access_role_arn=service_access_role_arn,
            external_table_definition=external_table_definition,
            external_id=None,
            dynamo_db_settings=dynamo_db_settings,
            s3_settings=s3_settings,
            dms_transfer_settings=dms_transfer_settings,
            mongo_db_settings=mongo_db_settings,
            kinesis_settings=kinesis_settings,
            kafka_settings=kafka_settings,
            elasticsearch_settings=elasticsearch_settings,
            neptune_settings=neptune_settings,
            redshift_settings=redshift_settings,
            postgre_sql_settings=postgre_sql_settings,
            my_sql_settings=my_sql_settings,
            oracle_settings=oracle_settings,
            sybase_settings=sybase_settings,
            microsoft_sql_server_settings=microsoft_sql_server_settings,
            ibm_db2_settings=ibm_db2_settings,
            resource_identifier=resource_identifier,
            doc_db_settings=doc_db_settings,
            redis_settings=redis_settings,
            gcp_my_sql_settings=gcp_my_sql_settings,
            timestream_settings=timestream_settings,
            account_id=self.account_id,
            region_name=self.region_name,
        )

        if tags:
            self.tagger.tag_resource(endpoint.endpoint_arn, tags)

        self.endpoints[endpoint.endpoint_identifier] = endpoint
        return endpoint

    def describe_endpoints(
        self,
        filters: list[dict[str, Any]],
        max_records: Optional[int],
        marker: Optional[str],
    ) -> list["Endpoint"]:
        endpoints = list(self.endpoints.values())
        filter_map = {
            "endpoint-arn": "endpoint_arn",
            "endpoint-type": "endpoint_type",
            "endpoint-id": "endpoint_identifier",
            "engine-name": "engine_name",
        }

        for f in filters:
            filter_name = f.get("Name")
            filter_values = f.get("Values", [])
            if filter_name not in filter_map:
                raise ValueError(f"Invalid filter name: {filter_name}")

            attribute = filter_map[filter_name]
            endpoints = [
                endpoint
                for endpoint in endpoints
                if getattr(endpoint, attribute) in filter_values
            ]
        return endpoints

    def delete_endpoint(self, endpoint_arn: str) -> "Endpoint":
        endpoints = [
            endpoint
            for endpoint in list(self.endpoints.values())
            if endpoint.endpoint_arn == endpoint_arn
        ]

        if len(endpoints) == 0:
            raise ResourceNotFoundFault("Endpoint could not be found.")
        endpoint = endpoints[0]
        endpoint.delete()
        self.endpoints.pop(endpoint.endpoint_identifier)

        connections = [
            connection
            for connection in self.connections
            if connection.endpoint_arn == endpoint_arn
        ]
        for connection in connections:
            self.connections.remove(connection)
        return endpoint

    def modify_endpoint(
        self,
        endpoint_arn: str,
        endpoint_identifier: Optional[str] = None,
        endpoint_type: Optional[str] = None,
        engine_name: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        server_name: Optional[str] = None,
        port: Optional[int] = None,
        database_name: Optional[str] = None,
        extra_connection_attributes: Optional[str] = None,
        certificate_arn: Optional[str] = None,
        ssl_mode: Optional[str] = None,
        service_access_role_arn: Optional[str] = None,
        external_table_definition: Optional[str] = None,
        dynamo_db_settings: Optional[dict[str, Any]] = None,
        s3_settings: Optional[dict[str, Any]] = None,
        dms_transfer_settings: Optional[dict[str, Any]] = None,
        mongo_db_settings: Optional[dict[str, Any]] = None,
        kinesis_settings: Optional[dict[str, Any]] = None,
        kafka_settings: Optional[dict[str, Any]] = None,
        elasticsearch_settings: Optional[dict[str, Any]] = None,
        neptune_settings: Optional[dict[str, Any]] = None,
        redshift_settings: Optional[dict[str, Any]] = None,
        postgre_sql_settings: Optional[dict[str, Any]] = None,
        my_sql_settings: Optional[dict[str, Any]] = None,
        oracle_settings: Optional[dict[str, Any]] = None,
        sybase_settings: Optional[dict[str, Any]] = None,
        microsoft_sql_server_settings: Optional[dict[str, Any]] = None,
        ibm_db2_settings: Optional[dict[str, Any]] = None,
        doc_db_settings: Optional[dict[str, Any]] = None,
        redis_settings: Optional[dict[str, Any]] = None,
        gcp_my_sql_settings: Optional[dict[str, Any]] = None,
        timestream_settings: Optional[dict[str, Any]] = None,
        exact_settings: Optional[bool] = None,
    ) -> "Endpoint":
        endpoints = [
            ep for ep in self.endpoints.values() if ep.endpoint_arn == endpoint_arn
        ]
        if not endpoints:
            raise ResourceNotFoundFault("Endpoint could not be found.")

        ep = endpoints[0]
        old_id = ep.endpoint_identifier
        if endpoint_identifier is not None:
            ep.endpoint_identifier = endpoint_identifier
        if endpoint_type is not None:
            ep.endpoint_type = endpoint_type
        if engine_name is not None:
            ep.engine_name = engine_name
            ep.engine_display_name = engine_name
        if username is not None:
            ep.username = username
        if password is not None:
            ep.password = password
        if server_name is not None:
            ep.server_name = server_name
        if port is not None:
            ep.port = port
        if database_name is not None:
            ep.database_name = database_name
        if extra_connection_attributes is not None:
            ep.extra_connection_attributes = extra_connection_attributes
        if certificate_arn is not None:
            ep.certificate_arn = certificate_arn
        if ssl_mode is not None:
            ep.ssl_mode = ssl_mode
        if service_access_role_arn is not None:
            ep.service_access_role_arn = service_access_role_arn
        if external_table_definition is not None:
            ep.external_table_definition = external_table_definition
        if dynamo_db_settings is not None:
            ep.dynamo_db_settings = dynamo_db_settings
        if s3_settings is not None:
            ep.s3_settings = s3_settings
        if dms_transfer_settings is not None:
            ep.dms_transfer_settings = dms_transfer_settings
        if mongo_db_settings is not None:
            ep.mongo_db_settings = mongo_db_settings
        if kinesis_settings is not None:
            ep.kinesis_settings = kinesis_settings
        if kafka_settings is not None:
            ep.kafka_settings = kafka_settings
        if elasticsearch_settings is not None:
            ep.elasticsearch_settings = elasticsearch_settings
        if neptune_settings is not None:
            ep.neptune_settings = neptune_settings
        if redshift_settings is not None:
            ep.redshift_settings = redshift_settings
        if postgre_sql_settings is not None:
            ep.postgre_sql_settings = postgre_sql_settings
        if my_sql_settings is not None:
            ep.my_sql_settings = my_sql_settings
        if oracle_settings is not None:
            ep.oracle_settings = oracle_settings
        if sybase_settings is not None:
            ep.sybase_settings = sybase_settings
        if microsoft_sql_server_settings is not None:
            ep.microsoft_sql_server_settings = microsoft_sql_server_settings
        if ibm_db2_settings is not None:
            ep.ibm_db2_settings = ibm_db2_settings
        if doc_db_settings is not None:
            ep.doc_db_settings = doc_db_settings
        if redis_settings is not None:
            ep.redis_settings = redis_settings
        if gcp_my_sql_settings is not None:
            ep.gcp_my_sql_settings = gcp_my_sql_settings
        if timestream_settings is not None:
            ep.timestream_settings = timestream_settings

        # Update dict key if identifier changed
        if endpoint_identifier is not None and endpoint_identifier != old_id:
            self.endpoints.pop(old_id, None)
            self.endpoints[endpoint_identifier] = ep

        return ep

    # ── Replication Subnet Groups ────────────────────────────────────

    def create_replication_subnet_group(
        self,
        replication_subnet_group_identifier: str,
        replication_subnet_group_description: str,
        subnet_ids: list[str],
        tags: Optional[list[dict[str, str]]] = None,
    ) -> "FakeReplicationSubnetGroup":
        replication_subnet_group = FakeReplicationSubnetGroup(
            replication_subnet_group_identifier=replication_subnet_group_identifier,
            replication_subnet_group_description=replication_subnet_group_description,
        )
        if tags:
            self.tagger.tag_resource(
                replication_subnet_group.replication_subnet_group_identifier, tags
            )
        if self.replication_subnet_groups.get(replication_subnet_group_identifier):
            raise ResourceAlreadyExistsFault(
                "The resource you are attempting to create already exists."
            )

        self.replication_subnet_groups[
            replication_subnet_group.replication_subnet_group_identifier
        ] = replication_subnet_group
        return replication_subnet_group

    def describe_replication_subnet_groups(
        self,
        filters: list[dict[str, Any]],
        max_records: Optional[int],
        marker: Optional[str],
    ) -> list["FakeReplicationSubnetGroup"]:
        subnet_groups = list(self.replication_subnet_groups.values())
        filter_map = {
            "replication-subnet-group-id": "replication_subnet_group_identifier"
        }

        for f in filters:
            filter_name = f.get("Name")
            filter_values = f.get("Values", [])
            if filter_name not in filter_map:
                raise ValueError(f"Invalid filter name: {filter_name}")

            attribute = filter_map[filter_name]
            subnet_groups = [
                subnet_group
                for subnet_group in subnet_groups
                if getattr(subnet_group, attribute) in filter_values
            ]

        return subnet_groups

    def delete_replication_subnet_group(
        self, replication_subnet_group_identifier: str
    ) -> "FakeReplicationSubnetGroup":
        if not self.replication_subnet_groups.get(replication_subnet_group_identifier):
            raise ResourceNotFoundFault("Replication subnet group could not be found.")

        replication_subnet_group = self.replication_subnet_groups[
            replication_subnet_group_identifier
        ]
        self.replication_subnet_groups.pop(replication_subnet_group_identifier)
        return replication_subnet_group

    def modify_replication_subnet_group(
        self,
        replication_subnet_group_identifier: str,
        replication_subnet_group_description: Optional[str] = None,
        subnet_ids: Optional[list[str]] = None,
    ) -> "FakeReplicationSubnetGroup":
        if not self.replication_subnet_groups.get(replication_subnet_group_identifier):
            raise ResourceNotFoundFault("Replication subnet group could not be found.")

        group = self.replication_subnet_groups[replication_subnet_group_identifier]
        if replication_subnet_group_description is not None:
            group.description = replication_subnet_group_description
        if subnet_ids is not None:
            group.subnetIds = subnet_ids
        return group

    # ── Connections ──────────────────────────────────────────────────

    def test_connection(
        self, replication_instance_arn: str, endpoint_arn: str
    ) -> "FakeConnection":
        if not self.replication_instances.get(replication_instance_arn):
            raise ResourceNotFoundFault("Replication instance could not be found.")
        replication_instance = self.replication_instances[replication_instance_arn]
        endpoints = [
            endpoint
            for endpoint in list(self.endpoints.values())
            if endpoint.endpoint_arn == endpoint_arn
        ]

        if len(endpoints) == 0:
            raise ResourceNotFoundFault("Endpoint could not be found.")
        endpoint = endpoints[0]
        connections = self.connections
        connections = [
            connection
            for connection in connections
            if connection.replication_instance_arn == replication_instance_arn
        ]
        connections = [
            connection
            for connection in connections
            if connection.endpoint_arn == endpoint_arn
        ]
        if len(connections) == 0:
            connection = FakeConnection(
                replication_instance_arn=replication_instance.arn,
                endpoint_arn=endpoint.endpoint_arn,
                replication_instance_identifier=replication_instance.id,
                endpoint_identifier=endpoint.endpoint_identifier,
            )
            self.connections.append(connection)
        return connection

    def describe_connections(
        self,
        filters: list[dict[str, Any]],
        max_records: Optional[int],
        marker: Optional[str],
    ) -> list["FakeConnection"]:
        filter_map = {
            "endpoint-arn": "endpoint_arn",
            "replication-instance-arn": "replication_instance_arn",
        }
        connections = self.connections
        for f in filters:
            filter_name = f.get("Name")
            filter_values = f.get("Values", [])
            if filter_name not in filter_map:
                raise ValueError(f"Invalid filter name: {filter_name}")

            attribute = filter_map[filter_name]
            connections = [
                connection
                for connection in self.connections
                if getattr(connection, attribute) in filter_values
            ]
        for connection in connections:
            connection.advance()
        return connections

    def delete_connection(
        self, endpoint_arn: str, replication_instance_arn: str
    ) -> "FakeConnection":
        matching = [
            c
            for c in self.connections
            if c.endpoint_arn == endpoint_arn
            and c.replication_instance_arn == replication_instance_arn
        ]
        if not matching:
            raise ResourceNotFoundFault("Connection could not be found.")
        connection = matching[0]
        self.connections.remove(connection)
        return connection

    # ── Event Subscriptions ──────────────────────────────────────────

    def create_event_subscription(
        self,
        subscription_name: str,
        sns_topic_arn: str,
        source_type: Optional[str] = None,
        event_categories: Optional[list[str]] = None,
        source_ids: Optional[list[str]] = None,
        enabled: Optional[bool] = True,
        tags: Optional[list[dict[str, str]]] = None,
    ) -> "FakeEventSubscription":
        if subscription_name in self.event_subscriptions:
            raise ResourceAlreadyExistsFault(
                "The resource you are attempting to create already exists."
            )

        sub = FakeEventSubscription(
            subscription_name=subscription_name,
            sns_topic_arn=sns_topic_arn,
            source_type=source_type,
            event_categories=event_categories or [],
            source_ids=source_ids or [],
            enabled=enabled if enabled is not None else True,
            account_id=self.account_id,
            region_name=self.region_name,
        )
        self.event_subscriptions[subscription_name] = sub
        if tags:
            self.tagger.tag_resource(sub.arn, tags)
        return sub

    def describe_event_subscriptions(
        self,
        subscription_name: Optional[str] = None,
        filters: Optional[list[dict[str, Any]]] = None,
        max_records: Optional[int] = None,
        marker: Optional[str] = None,
    ) -> list["FakeEventSubscription"]:
        if subscription_name:
            sub = self.event_subscriptions.get(subscription_name)
            if not sub:
                raise ResourceNotFoundFault("Subscription could not be found.")
            return [sub]
        return list(self.event_subscriptions.values())

    def delete_event_subscription(
        self, subscription_name: str
    ) -> "FakeEventSubscription":
        if subscription_name not in self.event_subscriptions:
            raise ResourceNotFoundFault("Subscription could not be found.")
        return self.event_subscriptions.pop(subscription_name)

    def modify_event_subscription(
        self,
        subscription_name: str,
        sns_topic_arn: Optional[str] = None,
        source_type: Optional[str] = None,
        event_categories: Optional[list[str]] = None,
        enabled: Optional[bool] = None,
    ) -> "FakeEventSubscription":
        if subscription_name not in self.event_subscriptions:
            raise ResourceNotFoundFault("Subscription could not be found.")

        sub = self.event_subscriptions[subscription_name]
        if sns_topic_arn is not None:
            sub.sns_topic_arn = sns_topic_arn
        if source_type is not None:
            sub.source_type = source_type
        if event_categories is not None:
            sub.event_categories = event_categories
        if enabled is not None:
            sub.enabled = enabled
        return sub

    # ── Certificates ─────────────────────────────────────────────────

    def import_certificate(
        self,
        certificate_identifier: str,
        certificate_pem: Optional[str] = None,
        certificate_wallet: Optional[str] = None,
        tags: Optional[list[dict[str, str]]] = None,
    ) -> "FakeCertificate":
        if certificate_identifier in self.certificates:
            raise ResourceAlreadyExistsFault(
                "The resource you are attempting to create already exists."
            )

        cert = FakeCertificate(
            certificate_identifier=certificate_identifier,
            certificate_pem=certificate_pem,
            certificate_wallet=certificate_wallet,
            account_id=self.account_id,
            region_name=self.region_name,
        )
        self.certificates[certificate_identifier] = cert
        if tags:
            self.tagger.tag_resource(cert.arn, tags)
        return cert

    def describe_certificates(
        self,
        filters: Optional[list[dict[str, Any]]] = None,
        max_records: Optional[int] = None,
        marker: Optional[str] = None,
    ) -> list["FakeCertificate"]:
        certs = list(self.certificates.values())
        if filters:
            for f in filters:
                name = f.get("Name", "")
                vals = f.get("Values", [])
                if name == "certificate-id":
                    certs = [c for c in certs if c.certificate_identifier in vals]
                elif name == "certificate-arn":
                    certs = [c for c in certs if c.arn in vals]
        return certs

    def delete_certificate(
        self, certificate_arn: str
    ) -> "FakeCertificate":
        matching = [
            c for c in self.certificates.values() if c.arn == certificate_arn
        ]
        if not matching:
            raise ResourceNotFoundFault("Certificate could not be found.")
        cert = matching[0]
        self.certificates.pop(cert.certificate_identifier)
        return cert

    # ── Replication Configs (Serverless) ─────────────────────────────

    def create_replication_config(
        self,
        replication_config_identifier: str,
        source_endpoint_arn: str,
        target_endpoint_arn: str,
        compute_config: dict[str, Any],
        replication_type: str,
        table_mappings: str,
        replication_settings: Optional[str] = None,
        supplemental_settings: Optional[str] = None,
        resource_identifier: Optional[str] = None,
        tags: Optional[list[dict[str, str]]] = None,
    ) -> "FakeReplicationConfig":
        if replication_config_identifier in self.replication_configs:
            raise ResourceAlreadyExistsFault(
                "The resource you are attempting to create already exists."
            )

        config = FakeReplicationConfig(
            replication_config_identifier=replication_config_identifier,
            source_endpoint_arn=source_endpoint_arn,
            target_endpoint_arn=target_endpoint_arn,
            compute_config=compute_config,
            replication_type=replication_type,
            table_mappings=table_mappings,
            replication_settings=replication_settings,
            supplemental_settings=supplemental_settings,
            resource_identifier=resource_identifier,
            account_id=self.account_id,
            region_name=self.region_name,
        )
        self.replication_configs[replication_config_identifier] = config
        if tags:
            self.tagger.tag_resource(config.arn, tags)
        return config

    def describe_replication_configs(
        self,
        filters: Optional[list[dict[str, Any]]] = None,
        max_records: Optional[int] = None,
        marker: Optional[str] = None,
    ) -> list["FakeReplicationConfig"]:
        configs = list(self.replication_configs.values())
        if filters:
            for f in filters:
                name = f.get("Name", "")
                vals = f.get("Values", [])
                if name == "replication-config-arn":
                    configs = [c for c in configs if c.arn in vals]
                elif name == "replication-config-id":
                    configs = [
                        c
                        for c in configs
                        if c.replication_config_identifier in vals
                    ]
        return configs

    def delete_replication_config(
        self, replication_config_arn: str
    ) -> None:
        matching = [
            c
            for c in self.replication_configs.values()
            if c.arn == replication_config_arn
        ]
        if not matching:
            raise ResourceNotFoundFault("Replication config could not be found.")
        self.replication_configs.pop(matching[0].replication_config_identifier)

    def modify_replication_config(
        self,
        replication_config_arn: str,
        replication_config_identifier: Optional[str] = None,
        replication_type: Optional[str] = None,
        table_mappings: Optional[str] = None,
        replication_settings: Optional[str] = None,
        supplemental_settings: Optional[str] = None,
        compute_config: Optional[dict[str, Any]] = None,
        source_endpoint_arn: Optional[str] = None,
        target_endpoint_arn: Optional[str] = None,
    ) -> "FakeReplicationConfig":
        matching = [
            c
            for c in self.replication_configs.values()
            if c.arn == replication_config_arn
        ]
        if not matching:
            raise ResourceNotFoundFault("Replication config could not be found.")

        config = matching[0]
        old_id = config.replication_config_identifier
        if replication_config_identifier is not None:
            config.replication_config_identifier = replication_config_identifier
        if replication_type is not None:
            config.replication_type = replication_type
        if table_mappings is not None:
            config.table_mappings = table_mappings
        if replication_settings is not None:
            config.replication_settings = replication_settings
        if supplemental_settings is not None:
            config.supplemental_settings = supplemental_settings
        if compute_config is not None:
            config.compute_config = compute_config
        if source_endpoint_arn is not None:
            config.source_endpoint_arn = source_endpoint_arn
        if target_endpoint_arn is not None:
            config.target_endpoint_arn = target_endpoint_arn

        if replication_config_identifier and replication_config_identifier != old_id:
            self.replication_configs.pop(old_id, None)
            self.replication_configs[replication_config_identifier] = config
        return config

    def start_replication(
        self,
        replication_config_arn: str,
        start_replication_type: str,
        cdc_start_time: Optional[str] = None,
        cdc_start_position: Optional[str] = None,
    ) -> "FakeReplicationConfig":
        matching = [
            c
            for c in self.replication_configs.values()
            if c.arn == replication_config_arn
        ]
        if not matching:
            raise ResourceNotFoundFault("Replication config could not be found.")
        config = matching[0]
        config.status = "running"
        return config

    def stop_replication(
        self, replication_config_arn: str
    ) -> "FakeReplicationConfig":
        matching = [
            c
            for c in self.replication_configs.values()
            if c.arn == replication_config_arn
        ]
        if not matching:
            raise ResourceNotFoundFault("Replication config could not be found.")
        config = matching[0]
        config.status = "stopped"
        return config

    def describe_replications(
        self,
        filters: Optional[list[dict[str, Any]]] = None,
        max_records: Optional[int] = None,
        marker: Optional[str] = None,
    ) -> list[dict[str, Any]]:
        configs = list(self.replication_configs.values())
        if filters:
            for f in filters:
                name = f.get("Name", "")
                vals = f.get("Values", [])
                if name == "replication-config-arn":
                    configs = [c for c in configs if c.arn in vals]
        result = []
        for c in configs:
            result.append({
                "ReplicationConfigIdentifier": c.replication_config_identifier,
                "ReplicationConfigArn": c.arn,
                "SourceEndpointArn": c.source_endpoint_arn,
                "TargetEndpointArn": c.target_endpoint_arn,
                "ReplicationType": c.replication_type,
                "Status": c.status,
                "StopReason": "",
                "ReplicationStats": {},
            })
        return result

    # ── Data Providers ───────────────────────────────────────────────

    def create_data_provider(
        self,
        data_provider_name: str,
        engine: str,
        settings: dict[str, Any],
        description: Optional[str] = None,
        tags: Optional[list[dict[str, str]]] = None,
    ) -> "FakeDataProvider":
        if data_provider_name in self.data_providers:
            raise ResourceAlreadyExistsFault(
                "The resource you are attempting to create already exists."
            )

        dp = FakeDataProvider(
            data_provider_name=data_provider_name,
            engine=engine,
            settings=settings,
            description=description,
            account_id=self.account_id,
            region_name=self.region_name,
        )
        self.data_providers[data_provider_name] = dp
        if tags:
            self.tagger.tag_resource(dp.arn, tags)
        return dp

    def describe_data_providers(
        self,
        filters: Optional[list[dict[str, Any]]] = None,
        max_records: Optional[int] = None,
        marker: Optional[str] = None,
    ) -> list["FakeDataProvider"]:
        providers = list(self.data_providers.values())
        if filters:
            for f in filters:
                name = f.get("Name", "")
                vals = f.get("Values", [])
                if name == "data-provider-identifier":
                    providers = [p for p in providers if p.data_provider_name in vals or p.arn in vals]
        return providers

    def modify_data_provider(
        self,
        data_provider_identifier: str,
        data_provider_name: Optional[str] = None,
        engine: Optional[str] = None,
        settings: Optional[dict[str, Any]] = None,
        description: Optional[str] = None,
        exact_settings: Optional[bool] = None,
    ) -> "FakeDataProvider":
        dp = self.data_providers.get(data_provider_identifier)
        if not dp:
            # Try by ARN
            matching = [p for p in self.data_providers.values() if p.arn == data_provider_identifier]
            if not matching:
                raise ResourceNotFoundFault("Data provider could not be found.")
            dp = matching[0]

        old_name = dp.data_provider_name
        if data_provider_name is not None:
            dp.data_provider_name = data_provider_name
        if engine is not None:
            dp.engine = engine
        if settings is not None:
            dp.settings = settings
        if description is not None:
            dp.description = description

        if data_provider_name and data_provider_name != old_name:
            self.data_providers.pop(old_name, None)
            self.data_providers[data_provider_name] = dp
        return dp

    def delete_data_provider(
        self, data_provider_identifier: str
    ) -> "FakeDataProvider":
        dp = self.data_providers.get(data_provider_identifier)
        if not dp:
            matching = [p for p in self.data_providers.values() if p.arn == data_provider_identifier]
            if not matching:
                raise ResourceNotFoundFault("Data provider could not be found.")
            dp = matching[0]
        self.data_providers.pop(dp.data_provider_name)
        return dp

    # ── Instance Profiles ────────────────────────────────────────────

    def create_instance_profile(
        self,
        instance_profile_name: str,
        availability_zone: Optional[str] = None,
        kms_key_arn: Optional[str] = None,
        publicly_accessible: Optional[bool] = None,
        network_type: Optional[str] = None,
        description: Optional[str] = None,
        subnet_group_identifier: Optional[str] = None,
        vpc_security_groups: Optional[list[str]] = None,
        tags: Optional[list[dict[str, str]]] = None,
    ) -> "FakeInstanceProfile":
        if instance_profile_name in self.instance_profiles:
            raise ResourceAlreadyExistsFault(
                "The resource you are attempting to create already exists."
            )

        ip = FakeInstanceProfile(
            instance_profile_name=instance_profile_name,
            availability_zone=availability_zone,
            kms_key_arn=kms_key_arn,
            publicly_accessible=publicly_accessible if publicly_accessible is not None else False,
            network_type=network_type,
            description=description,
            subnet_group_identifier=subnet_group_identifier,
            vpc_security_groups=vpc_security_groups or [],
            account_id=self.account_id,
            region_name=self.region_name,
        )
        self.instance_profiles[instance_profile_name] = ip
        if tags:
            self.tagger.tag_resource(ip.arn, tags)
        return ip

    def describe_instance_profiles(
        self,
        filters: Optional[list[dict[str, Any]]] = None,
        max_records: Optional[int] = None,
        marker: Optional[str] = None,
    ) -> list["FakeInstanceProfile"]:
        profiles = list(self.instance_profiles.values())
        if filters:
            for f in filters:
                name = f.get("Name", "")
                vals = f.get("Values", [])
                if name == "instance-profile-identifier":
                    profiles = [
                        p
                        for p in profiles
                        if p.instance_profile_name in vals or p.arn in vals
                    ]
        return profiles

    def modify_instance_profile(
        self,
        instance_profile_identifier: str,
        instance_profile_name: Optional[str] = None,
        availability_zone: Optional[str] = None,
        kms_key_arn: Optional[str] = None,
        publicly_accessible: Optional[bool] = None,
        network_type: Optional[str] = None,
        description: Optional[str] = None,
        subnet_group_identifier: Optional[str] = None,
        vpc_security_groups: Optional[list[str]] = None,
    ) -> "FakeInstanceProfile":
        ip = self.instance_profiles.get(instance_profile_identifier)
        if not ip:
            matching = [
                p
                for p in self.instance_profiles.values()
                if p.arn == instance_profile_identifier
            ]
            if not matching:
                raise ResourceNotFoundFault("Instance profile could not be found.")
            ip = matching[0]

        old_name = ip.instance_profile_name
        if instance_profile_name is not None:
            ip.instance_profile_name = instance_profile_name
        if availability_zone is not None:
            ip.availability_zone = availability_zone
        if kms_key_arn is not None:
            ip.kms_key_arn = kms_key_arn
        if publicly_accessible is not None:
            ip.publicly_accessible = publicly_accessible
        if network_type is not None:
            ip.network_type = network_type
        if description is not None:
            ip.description = description
        if subnet_group_identifier is not None:
            ip.subnet_group_identifier = subnet_group_identifier
        if vpc_security_groups is not None:
            ip.vpc_security_groups = vpc_security_groups

        if instance_profile_name and instance_profile_name != old_name:
            self.instance_profiles.pop(old_name, None)
            self.instance_profiles[instance_profile_name] = ip
        return ip

    def delete_instance_profile(
        self, instance_profile_identifier: str
    ) -> "FakeInstanceProfile":
        ip = self.instance_profiles.get(instance_profile_identifier)
        if not ip:
            matching = [
                p
                for p in self.instance_profiles.values()
                if p.arn == instance_profile_identifier
            ]
            if not matching:
                raise ResourceNotFoundFault("Instance profile could not be found.")
            ip = matching[0]
        self.instance_profiles.pop(ip.instance_profile_name)
        return ip

    # ── Migration Projects ───────────────────────────────────────────

    def create_migration_project(
        self,
        migration_project_name: str,
        source_data_provider_descriptors: Optional[list[dict[str, Any]]] = None,
        target_data_provider_descriptors: Optional[list[dict[str, Any]]] = None,
        instance_profile_identifier: Optional[str] = None,
        transformation_rules: Optional[str] = None,
        description: Optional[str] = None,
        schema_conversion_application_attributes: Optional[dict[str, Any]] = None,
        tags: Optional[list[dict[str, str]]] = None,
    ) -> "FakeMigrationProject":
        if migration_project_name in self.migration_projects:
            raise ResourceAlreadyExistsFault(
                "The resource you are attempting to create already exists."
            )

        mp = FakeMigrationProject(
            migration_project_name=migration_project_name,
            source_data_provider_descriptors=source_data_provider_descriptors or [],
            target_data_provider_descriptors=target_data_provider_descriptors or [],
            instance_profile_identifier=instance_profile_identifier,
            transformation_rules=transformation_rules,
            description=description,
            schema_conversion_application_attributes=schema_conversion_application_attributes,
            account_id=self.account_id,
            region_name=self.region_name,
        )
        self.migration_projects[migration_project_name] = mp
        if tags:
            self.tagger.tag_resource(mp.arn, tags)
        return mp

    def describe_migration_projects(
        self,
        filters: Optional[list[dict[str, Any]]] = None,
        max_records: Optional[int] = None,
        marker: Optional[str] = None,
    ) -> list["FakeMigrationProject"]:
        projects = list(self.migration_projects.values())
        if filters:
            for f in filters:
                name = f.get("Name", "")
                vals = f.get("Values", [])
                if name == "migration-project-identifier":
                    projects = [
                        p
                        for p in projects
                        if p.migration_project_name in vals or p.arn in vals
                    ]
        return projects

    def modify_migration_project(
        self,
        migration_project_identifier: str,
        migration_project_name: Optional[str] = None,
        source_data_provider_descriptors: Optional[list[dict[str, Any]]] = None,
        target_data_provider_descriptors: Optional[list[dict[str, Any]]] = None,
        instance_profile_identifier: Optional[str] = None,
        transformation_rules: Optional[str] = None,
        description: Optional[str] = None,
        schema_conversion_application_attributes: Optional[dict[str, Any]] = None,
    ) -> "FakeMigrationProject":
        mp = self.migration_projects.get(migration_project_identifier)
        if not mp:
            matching = [
                p
                for p in self.migration_projects.values()
                if p.arn == migration_project_identifier
            ]
            if not matching:
                raise ResourceNotFoundFault("Migration project could not be found.")
            mp = matching[0]

        old_name = mp.migration_project_name
        if migration_project_name is not None:
            mp.migration_project_name = migration_project_name
        if source_data_provider_descriptors is not None:
            mp.source_data_provider_descriptors = source_data_provider_descriptors
        if target_data_provider_descriptors is not None:
            mp.target_data_provider_descriptors = target_data_provider_descriptors
        if instance_profile_identifier is not None:
            mp.instance_profile_identifier = instance_profile_identifier
        if transformation_rules is not None:
            mp.transformation_rules = transformation_rules
        if description is not None:
            mp.description = description
        if schema_conversion_application_attributes is not None:
            mp.schema_conversion_application_attributes = (
                schema_conversion_application_attributes
            )

        if migration_project_name and migration_project_name != old_name:
            self.migration_projects.pop(old_name, None)
            self.migration_projects[migration_project_name] = mp
        return mp

    def delete_migration_project(
        self, migration_project_identifier: str
    ) -> "FakeMigrationProject":
        mp = self.migration_projects.get(migration_project_identifier)
        if not mp:
            matching = [
                p
                for p in self.migration_projects.values()
                if p.arn == migration_project_identifier
            ]
            if not matching:
                raise ResourceNotFoundFault("Migration project could not be found.")
            mp = matching[0]
        self.migration_projects.pop(mp.migration_project_name)
        return mp

    # ── Data Migrations ──────────────────────────────────────────────

    def create_data_migration(
        self,
        data_migration_name: str,
        migration_project_identifier: str,
        data_migration_type: str,
        service_access_role_arn: str,
        source_data_settings: Optional[list[dict[str, Any]]] = None,
        enable_cloudwatch_logs: Optional[bool] = None,
        tags: Optional[list[dict[str, str]]] = None,
    ) -> "FakeDataMigration":
        if data_migration_name in self.data_migrations:
            raise ResourceAlreadyExistsFault(
                "The resource you are attempting to create already exists."
            )

        dm = FakeDataMigration(
            data_migration_name=data_migration_name,
            migration_project_identifier=migration_project_identifier,
            data_migration_type=data_migration_type,
            service_access_role_arn=service_access_role_arn,
            source_data_settings=source_data_settings or [],
            enable_cloudwatch_logs=enable_cloudwatch_logs or False,
            account_id=self.account_id,
            region_name=self.region_name,
        )
        self.data_migrations[data_migration_name] = dm
        if tags:
            self.tagger.tag_resource(dm.arn, tags)
        return dm

    def describe_data_migrations(
        self,
        filters: Optional[list[dict[str, Any]]] = None,
        max_records: Optional[int] = None,
        marker: Optional[str] = None,
    ) -> list["FakeDataMigration"]:
        migrations = list(self.data_migrations.values())
        if filters:
            for f in filters:
                name = f.get("Name", "")
                vals = f.get("Values", [])
                if name == "data-migration-identifier":
                    migrations = [
                        m
                        for m in migrations
                        if m.data_migration_name in vals or m.arn in vals
                    ]
        return migrations

    def modify_data_migration(
        self,
        data_migration_identifier: str,
        data_migration_name: Optional[str] = None,
        data_migration_type: Optional[str] = None,
        service_access_role_arn: Optional[str] = None,
        source_data_settings: Optional[list[dict[str, Any]]] = None,
        enable_cloudwatch_logs: Optional[bool] = None,
    ) -> "FakeDataMigration":
        dm = self.data_migrations.get(data_migration_identifier)
        if not dm:
            matching = [
                m
                for m in self.data_migrations.values()
                if m.arn == data_migration_identifier
            ]
            if not matching:
                raise ResourceNotFoundFault("Data migration could not be found.")
            dm = matching[0]

        old_name = dm.data_migration_name
        if data_migration_name is not None:
            dm.data_migration_name = data_migration_name
        if data_migration_type is not None:
            dm.data_migration_type = data_migration_type
        if service_access_role_arn is not None:
            dm.service_access_role_arn = service_access_role_arn
        if source_data_settings is not None:
            dm.source_data_settings = source_data_settings
        if enable_cloudwatch_logs is not None:
            dm.enable_cloudwatch_logs = enable_cloudwatch_logs

        if data_migration_name and data_migration_name != old_name:
            self.data_migrations.pop(old_name, None)
            self.data_migrations[data_migration_name] = dm
        return dm

    def delete_data_migration(
        self, data_migration_identifier: str
    ) -> "FakeDataMigration":
        dm = self.data_migrations.get(data_migration_identifier)
        if not dm:
            matching = [
                m
                for m in self.data_migrations.values()
                if m.arn == data_migration_identifier
            ]
            if not matching:
                raise ResourceNotFoundFault("Data migration could not be found.")
            dm = matching[0]
        self.data_migrations.pop(dm.data_migration_name)
        return dm

    def start_data_migration(
        self,
        data_migration_identifier: str,
        start_type: str,
    ) -> "FakeDataMigration":
        dm = self.data_migrations.get(data_migration_identifier)
        if not dm:
            matching = [
                m
                for m in self.data_migrations.values()
                if m.arn == data_migration_identifier
            ]
            if not matching:
                raise ResourceNotFoundFault("Data migration could not be found.")
            dm = matching[0]
        dm.status = "running"
        return dm

    def stop_data_migration(
        self, data_migration_identifier: str
    ) -> "FakeDataMigration":
        dm = self.data_migrations.get(data_migration_identifier)
        if not dm:
            matching = [
                m
                for m in self.data_migrations.values()
                if m.arn == data_migration_identifier
            ]
            if not matching:
                raise ResourceNotFoundFault("Data migration could not be found.")
            dm = matching[0]
        dm.status = "stopped"
        return dm

    # ── Describe / List stubs (return empty or static) ───────────────

    def describe_account_attributes(self) -> dict[str, Any]:
        return {
            "AccountQuotas": [
                {
                    "AccountQuotaName": "ReplicationInstances",
                    "Used": len(self.replication_instances),
                    "Max": 60,
                },
                {
                    "AccountQuotaName": "AllocatedStorage",
                    "Used": sum(
                        i.allocated_storage
                        for i in self.replication_instances.values()
                    ),
                    "Max": 100000,
                },
                {
                    "AccountQuotaName": "Endpoints",
                    "Used": len(self.endpoints),
                    "Max": 1000,
                },
                {
                    "AccountQuotaName": "ReplicationSubnetGroups",
                    "Used": len(self.replication_subnet_groups),
                    "Max": 60,
                },
                {
                    "AccountQuotaName": "ReplicationTasks",
                    "Used": len(self.replication_tasks),
                    "Max": 200,
                },
                {
                    "AccountQuotaName": "EventSubscriptions",
                    "Used": len(self.event_subscriptions),
                    "Max": 60,
                },
                {
                    "AccountQuotaName": "Certificates",
                    "Used": len(self.certificates),
                    "Max": 100,
                },
            ],
            "UniqueAccountIdentifier": self.account_id,
        }

    def describe_endpoint_types(
        self,
        filters: Optional[list[dict[str, Any]]] = None,
        max_records: Optional[int] = None,
        marker: Optional[str] = None,
    ) -> list[dict[str, Any]]:
        engine_types = [
            ("mysql", "MySQL", True, True),
            ("oracle", "Oracle", True, True),
            ("postgres", "PostgreSQL", True, True),
            ("mariadb", "MariaDB", True, True),
            ("aurora", "Amazon Aurora MySQL", True, True),
            ("aurora-postgresql", "Amazon Aurora PostgreSQL", True, True),
            ("redshift", "Amazon Redshift", False, True),
            ("s3", "Amazon S3", True, True),
            ("db2", "IBM Db2 LUW", True, True),
            ("azuredb", "Azure SQL Database", True, False),
            ("sybase", "SAP ASE", True, True),
            ("dynamodb", "Amazon DynamoDB", False, True),
            ("mongodb", "MongoDB", True, False),
            ("kinesis", "Amazon Kinesis", False, True),
            ("kafka", "Apache Kafka", False, True),
            ("elasticsearch", "Amazon OpenSearch Service", False, True),
            ("docdb", "Amazon DocumentDB", True, False),
            ("sqlserver", "Microsoft SQL Server", True, True),
            ("neptune", "Amazon Neptune", False, True),
        ]
        result = []
        for ename, edisplay, supports_source, supports_target in engine_types:
            if supports_source:
                result.append({
                    "EngineName": ename,
                    "EngineDisplayName": edisplay,
                    "SupportsCDC": True,
                    "EndpointType": "source",
                    "ReplicationInstanceEngineMinimumVersion": "3.4.7",
                })
            if supports_target:
                result.append({
                    "EngineName": ename,
                    "EngineDisplayName": edisplay,
                    "SupportsCDC": True,
                    "EndpointType": "target",
                    "ReplicationInstanceEngineMinimumVersion": "3.4.7",
                })
        return result

    def describe_endpoint_settings(
        self,
        engine_name: str,
        max_records: Optional[int] = None,
        marker: Optional[str] = None,
    ) -> list[dict[str, Any]]:
        return []

    def describe_orderable_replication_instances(
        self,
        max_records: Optional[int] = None,
        marker: Optional[str] = None,
    ) -> list[dict[str, Any]]:
        instance_classes = [
            "dms.t2.micro",
            "dms.t2.small",
            "dms.t2.medium",
            "dms.t2.large",
            "dms.c4.large",
            "dms.c4.xlarge",
            "dms.c4.2xlarge",
            "dms.c4.4xlarge",
            "dms.r4.large",
            "dms.r4.xlarge",
            "dms.r4.2xlarge",
            "dms.r4.4xlarge",
            "dms.r4.8xlarge",
        ]
        result = []
        for ic in instance_classes:
            result.append({
                "EngineVersion": "3.5.2",
                "ReplicationInstanceClass": ic,
                "StorageType": "gp2",
                "MinAllocatedStorage": 5,
                "MaxAllocatedStorage": 6144,
                "DefaultAllocatedStorage": 50,
                "IncludedAllocatedStorage": 50,
                "AvailabilityZones": [
                    f"{self.region_name}a",
                    f"{self.region_name}b",
                    f"{self.region_name}c",
                ],
                "ReleaseStatus": "GA",
            })
        return result

    def describe_event_categories(
        self,
        source_type: Optional[str] = None,
        filters: Optional[list[dict[str, Any]]] = None,
    ) -> list[dict[str, Any]]:
        categories = [
            {
                "SourceType": "replication-instance",
                "EventCategories": [
                    "low storage",
                    "configuration change",
                    "maintenance",
                    "deletion",
                    "creation",
                    "failover",
                    "failure",
                ],
            },
            {
                "SourceType": "replication-task",
                "EventCategories": [
                    "state change",
                    "creation",
                    "deletion",
                    "failure",
                    "configuration change",
                ],
            },
        ]
        if source_type:
            categories = [c for c in categories if c["SourceType"] == source_type]
        return categories

    def describe_events(
        self,
        source_identifier: Optional[str] = None,
        source_type: Optional[str] = None,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
        duration: Optional[int] = None,
        event_categories: Optional[list[str]] = None,
        filters: Optional[list[dict[str, Any]]] = None,
        max_records: Optional[int] = None,
        marker: Optional[str] = None,
    ) -> list[dict[str, Any]]:
        return []

    def describe_table_statistics(
        self,
        replication_task_arn: str,
        max_records: Optional[int] = None,
        marker: Optional[str] = None,
        filters: Optional[list[dict[str, Any]]] = None,
    ) -> dict[str, Any]:
        if not self.replication_tasks.get(replication_task_arn):
            raise ResourceNotFoundFault("Replication task could not be found.")
        return {
            "ReplicationTaskArn": replication_task_arn,
            "TableStatistics": [],
        }

    def describe_replication_table_statistics(
        self,
        replication_config_arn: str,
        max_records: Optional[int] = None,
        marker: Optional[str] = None,
        filters: Optional[list[dict[str, Any]]] = None,
    ) -> dict[str, Any]:
        return {
            "ReplicationConfigArn": replication_config_arn,
            "ReplicationTableStatistics": [],
        }

    def describe_schemas(
        self,
        endpoint_arn: str,
        max_records: Optional[int] = None,
        marker: Optional[str] = None,
    ) -> list[str]:
        return []

    def refresh_schemas(
        self, endpoint_arn: str, replication_instance_arn: str
    ) -> dict[str, Any]:
        return {
            "RefreshSchemasStatus": {
                "EndpointArn": endpoint_arn,
                "ReplicationInstanceArn": replication_instance_arn,
                "Status": "successful",
                "LastRefreshDate": utcnow().isoformat(),
                "LastFailureMessage": "",
            }
        }

    def describe_refresh_schemas_status(
        self, endpoint_arn: str
    ) -> dict[str, Any]:
        return {
            "RefreshSchemasStatus": {
                "EndpointArn": endpoint_arn,
                "ReplicationInstanceArn": "",
                "Status": "successful",
                "LastRefreshDate": utcnow().isoformat(),
                "LastFailureMessage": "",
            }
        }

    def reload_tables(
        self,
        replication_task_arn: str,
        tables_to_reload: list[dict[str, str]],
        reload_option: Optional[str] = None,
    ) -> dict[str, Any]:
        if not self.replication_tasks.get(replication_task_arn):
            raise ResourceNotFoundFault("Replication task could not be found.")
        return {"ReplicationTaskArn": replication_task_arn}

    def reload_replication_tables(
        self,
        replication_config_arn: str,
        tables_to_reload: list[dict[str, str]],
        reload_option: Optional[str] = None,
    ) -> dict[str, Any]:
        return {"ReplicationConfigArn": replication_config_arn}

    def describe_applicable_individual_assessments(
        self,
        replication_task_arn: Optional[str] = None,
        replication_instance_arn: Optional[str] = None,
        source_engine_name: Optional[str] = None,
        target_engine_name: Optional[str] = None,
        migration_type: Optional[str] = None,
        max_records: Optional[int] = None,
        marker: Optional[str] = None,
    ) -> list[str]:
        return [
            "table-compatibility",
            "unsupported-data-types",
            "large-objects",
            "memory-limitations",
        ]

    def start_replication_task_assessment(
        self, replication_task_arn: str
    ) -> "FakeReplicationTask":
        if not self.replication_tasks.get(replication_task_arn):
            raise ResourceNotFoundFault("Replication task could not be found.")
        return self.replication_tasks[replication_task_arn]

    def describe_replication_task_assessment_results(
        self,
        replication_task_arn: Optional[str] = None,
        max_records: Optional[int] = None,
        marker: Optional[str] = None,
    ) -> list[dict[str, Any]]:
        return []

    def start_replication_task_assessment_run(
        self,
        replication_task_arn: str,
        service_access_role_arn: str,
        result_location_bucket: str,
        assessment_run_name: str,
        result_location_folder: Optional[str] = None,
        result_encryption_mode: Optional[str] = None,
        result_kms_key_arn: Optional[str] = None,
        include_only: Optional[list[str]] = None,
        exclude: Optional[list[str]] = None,
        tags: Optional[list[dict[str, str]]] = None,
    ) -> dict[str, Any]:
        if not self.replication_tasks.get(replication_task_arn):
            raise ResourceNotFoundFault("Replication task could not be found.")
        run_id = random_id(True, 17)
        run_arn = (
            f"arn:{get_partition(self.region_name)}:dms:{self.region_name}:"
            f"{self.account_id}:assessment-run:{run_id}"
        )
        return {
            "ReplicationTaskAssessmentRun": {
                "ReplicationTaskAssessmentRunArn": run_arn,
                "ReplicationTaskArn": replication_task_arn,
                "Status": "starting",
                "ReplicationTaskAssessmentRunCreationDate": utcnow().isoformat(),
                "AssessmentProgress": {"IndividualAssessmentCount": 0, "IndividualAssessmentCompletedCount": 0},
                "AssessmentRunName": assessment_run_name,
                "ServiceAccessRoleArn": service_access_role_arn,
                "ResultLocationBucket": result_location_bucket,
                "ResultLocationFolder": result_location_folder or "",
                "ResultEncryptionMode": result_encryption_mode or "SSE_S3",
            }
        }

    def cancel_replication_task_assessment_run(
        self, replication_task_assessment_run_arn: str
    ) -> dict[str, Any]:
        return {
            "ReplicationTaskAssessmentRun": {
                "ReplicationTaskAssessmentRunArn": replication_task_assessment_run_arn,
                "Status": "cancelling",
            }
        }

    def delete_replication_task_assessment_run(
        self, replication_task_assessment_run_arn: str
    ) -> dict[str, Any]:
        return {
            "ReplicationTaskAssessmentRun": {
                "ReplicationTaskAssessmentRunArn": replication_task_assessment_run_arn,
                "Status": "deleting",
            }
        }

    def describe_replication_task_assessment_runs(
        self,
        filters: Optional[list[dict[str, Any]]] = None,
        max_records: Optional[int] = None,
        marker: Optional[str] = None,
    ) -> list[dict[str, Any]]:
        return []

    def describe_replication_task_individual_assessments(
        self,
        filters: Optional[list[dict[str, Any]]] = None,
        max_records: Optional[int] = None,
        marker: Optional[str] = None,
    ) -> list[dict[str, Any]]:
        return []

    def describe_pending_maintenance_actions(
        self,
        replication_instance_arn: Optional[str] = None,
        filters: Optional[list[dict[str, Any]]] = None,
        max_records: Optional[int] = None,
        marker: Optional[str] = None,
    ) -> list[dict[str, Any]]:
        return []

    def apply_pending_maintenance_action(
        self,
        replication_instance_arn: str,
        apply_action: str,
        opt_in_type: str,
    ) -> dict[str, Any]:
        if not self.replication_instances.get(replication_instance_arn):
            raise ResourceNotFoundFault("Replication instance could not be found.")
        return {
            "ResourcePendingMaintenanceActions": {
                "ResourceIdentifier": replication_instance_arn,
                "PendingMaintenanceActionDetails": [
                    {
                        "Action": apply_action,
                        "OptInStatus": opt_in_type,
                    }
                ],
            }
        }

    def describe_engine_versions(
        self,
        max_records: Optional[int] = None,
        marker: Optional[str] = None,
    ) -> list[dict[str, Any]]:
        return [
            {
                "Version": "3.5.2",
                "Lifecycle": "GA",
                "ReleaseStatus": "GA",
                "LaunchDate": "2023-01-01T00:00:00Z",
                "AutoUpgradeDate": "",
                "DeprecationDate": "",
                "AvailableUpgrades": [],
            },
            {
                "Version": "3.4.7",
                "Lifecycle": "GA",
                "ReleaseStatus": "GA",
                "LaunchDate": "2022-01-01T00:00:00Z",
                "AutoUpgradeDate": "",
                "DeprecationDate": "",
                "AvailableUpgrades": ["3.5.2"],
            },
        ]

    def update_subscriptions_to_event_bridge(
        self, force_move: Optional[bool] = None
    ) -> dict[str, Any]:
        return {"Result": "Subscriptions were updated successfully."}

    # ── Fleet Advisor stubs ──────────────────────────────────────────

    def create_fleet_advisor_collector(
        self,
        collector_name: str,
        description: Optional[str] = None,
        service_access_role_arn: Optional[str] = None,
        s3_bucket_name: Optional[str] = None,
    ) -> dict[str, Any]:
        collector_id = random_id(True, 24)
        return {
            "CollectorReferencedId": collector_id,
            "CollectorName": collector_name,
            "Description": description or "",
            "ServiceAccessRoleArn": service_access_role_arn or "",
            "S3BucketName": s3_bucket_name or "",
        }

    def delete_fleet_advisor_collector(self, collector_referenced_id: str) -> None:
        pass

    def delete_fleet_advisor_databases(
        self, database_ids: list[str]
    ) -> list[str]:
        return database_ids

    def describe_fleet_advisor_collectors(
        self,
        filters: Optional[list[dict[str, Any]]] = None,
        max_records: Optional[int] = None,
        next_token: Optional[str] = None,
    ) -> list[dict[str, Any]]:
        return []

    def describe_fleet_advisor_databases(
        self,
        filters: Optional[list[dict[str, Any]]] = None,
        max_records: Optional[int] = None,
        next_token: Optional[str] = None,
    ) -> list[dict[str, Any]]:
        return []

    def describe_fleet_advisor_lsa_analysis(
        self,
        max_records: Optional[int] = None,
        next_token: Optional[str] = None,
    ) -> list[dict[str, Any]]:
        return []

    def describe_fleet_advisor_schema_object_summary(
        self,
        filters: Optional[list[dict[str, Any]]] = None,
        max_records: Optional[int] = None,
        next_token: Optional[str] = None,
    ) -> list[dict[str, Any]]:
        return []

    def describe_fleet_advisor_schemas(
        self,
        filters: Optional[list[dict[str, Any]]] = None,
        max_records: Optional[int] = None,
        next_token: Optional[str] = None,
    ) -> list[dict[str, Any]]:
        return []

    def run_fleet_advisor_lsa_analysis(self) -> dict[str, Any]:
        lsa_id = random_id(True, 20)
        return {
            "LsaAnalysisId": lsa_id,
            "Status": "COMPLETED",
        }

    # ── Recommendations stubs ────────────────────────────────────────

    def start_recommendations(
        self, database_id: str, settings: dict[str, Any]
    ) -> None:
        pass

    def batch_start_recommendations(
        self, data: Optional[list[dict[str, Any]]] = None
    ) -> list[dict[str, Any]]:
        return []

    def describe_recommendations(
        self,
        filters: Optional[list[dict[str, Any]]] = None,
        max_records: Optional[int] = None,
        next_token: Optional[str] = None,
    ) -> list[dict[str, Any]]:
        return []

    def describe_recommendation_limitations(
        self,
        filters: Optional[list[dict[str, Any]]] = None,
        max_records: Optional[int] = None,
        next_token: Optional[str] = None,
    ) -> list[dict[str, Any]]:
        return []

    # ── Metadata model / conversion stubs ────────────────────────────

    def describe_conversion_configuration(
        self, migration_project_identifier: str
    ) -> dict[str, Any]:
        return {
            "MigrationProjectIdentifier": migration_project_identifier,
            "ConversionConfiguration": "{}",
        }

    def modify_conversion_configuration(
        self,
        migration_project_identifier: str,
        conversion_configuration: str,
    ) -> dict[str, Any]:
        return {
            "MigrationProjectIdentifier": migration_project_identifier,
        }

    def start_metadata_model_conversion(
        self, migration_project_identifier: str, selection_rules: str
    ) -> dict[str, Any]:
        request_id = random_id(True, 20)
        return {
            "RequestIdentifier": request_id,
        }

    def start_metadata_model_assessment(
        self, migration_project_identifier: str, selection_rules: str
    ) -> dict[str, Any]:
        request_id = random_id(True, 20)
        return {
            "RequestIdentifier": request_id,
        }

    def start_metadata_model_export_as_script(
        self,
        migration_project_identifier: str,
        selection_rules: str,
        origin: str,
        file_name: Optional[str] = None,
    ) -> dict[str, Any]:
        request_id = random_id(True, 20)
        return {
            "RequestIdentifier": request_id,
        }

    def start_metadata_model_export_to_target(
        self,
        migration_project_identifier: str,
        selection_rules: str,
        overwrite_extension_pack: Optional[bool] = None,
    ) -> dict[str, Any]:
        request_id = random_id(True, 20)
        return {
            "RequestIdentifier": request_id,
        }

    def start_metadata_model_import(
        self,
        migration_project_identifier: str,
        selection_rules: str,
        origin: str,
        refresh: Optional[bool] = None,
    ) -> dict[str, Any]:
        request_id = random_id(True, 20)
        return {
            "RequestIdentifier": request_id,
        }

    def start_metadata_model_creation(
        self, migration_project_identifier: str, selection_rules: str
    ) -> dict[str, Any]:
        request_id = random_id(True, 20)
        return {
            "RequestIdentifier": request_id,
        }

    def cancel_metadata_model_conversion(
        self, migration_project_identifier: str
    ) -> dict[str, Any]:
        request_id = random_id(True, 20)
        return {
            "RequestIdentifier": request_id,
        }

    def cancel_metadata_model_creation(
        self, migration_project_identifier: str
    ) -> dict[str, Any]:
        request_id = random_id(True, 20)
        return {
            "RequestIdentifier": request_id,
        }

    def describe_metadata_model_conversions(
        self,
        migration_project_identifier: str,
        filters: Optional[list[dict[str, Any]]] = None,
        max_records: Optional[int] = None,
        marker: Optional[str] = None,
    ) -> list[dict[str, Any]]:
        return []

    def describe_metadata_model_exports_as_script(
        self,
        migration_project_identifier: str,
        filters: Optional[list[dict[str, Any]]] = None,
        max_records: Optional[int] = None,
        marker: Optional[str] = None,
    ) -> list[dict[str, Any]]:
        return []

    def describe_metadata_model_exports_to_target(
        self,
        migration_project_identifier: str,
        filters: Optional[list[dict[str, Any]]] = None,
        max_records: Optional[int] = None,
        marker: Optional[str] = None,
    ) -> list[dict[str, Any]]:
        return []

    def describe_metadata_model_imports(
        self,
        migration_project_identifier: str,
        filters: Optional[list[dict[str, Any]]] = None,
        max_records: Optional[int] = None,
        marker: Optional[str] = None,
    ) -> list[dict[str, Any]]:
        return []

    def describe_metadata_model_assessments(
        self,
        migration_project_identifier: str,
        filters: Optional[list[dict[str, Any]]] = None,
        max_records: Optional[int] = None,
        marker: Optional[str] = None,
    ) -> list[dict[str, Any]]:
        return []

    def describe_metadata_model_creations(
        self,
        migration_project_identifier: str,
        filters: Optional[list[dict[str, Any]]] = None,
        max_records: Optional[int] = None,
        marker: Optional[str] = None,
    ) -> list[dict[str, Any]]:
        return []

    def describe_metadata_model(
        self,
        migration_project_identifier: str,
        filters: Optional[list[dict[str, Any]]] = None,
        max_records: Optional[int] = None,
        marker: Optional[str] = None,
    ) -> list[dict[str, Any]]:
        return []

    def describe_metadata_model_children(
        self,
        migration_project_identifier: str,
        parent_path: Optional[str] = None,
        filters: Optional[list[dict[str, Any]]] = None,
        max_records: Optional[int] = None,
        marker: Optional[str] = None,
    ) -> list[dict[str, Any]]:
        return []

    def export_metadata_model_assessment(
        self,
        migration_project_identifier: str,
        selection_rules: str,
        file_name: Optional[str] = None,
        assessment_report_types: Optional[list[str]] = None,
    ) -> dict[str, Any]:
        return {
            "PdfReport": {"S3ObjectKey": "", "ContentLength": 0},
            "CsvReport": {"S3ObjectKey": "", "ContentLength": 0},
        }

    def start_extension_pack_association(
        self, migration_project_identifier: str
    ) -> dict[str, Any]:
        request_id = random_id(True, 20)
        return {
            "RequestIdentifier": request_id,
        }

    def describe_extension_pack_associations(
        self,
        migration_project_identifier: str,
        filters: Optional[list[dict[str, Any]]] = None,
        max_records: Optional[int] = None,
        marker: Optional[str] = None,
    ) -> list[dict[str, Any]]:
        return []

    def get_target_selection_rules(
        self,
        migration_project_identifier: str,
    ) -> dict[str, Any]:
        return {
            "TargetSelectionRules": "{}",
        }


# ── Model classes ────────────────────────────────────────────────────


class Endpoint(BaseModel):
    def __init__(
        self,
        endpoint_identifier: str,
        endpoint_type: str,
        engine_name: str,
        engine_display_name: str,
        username: str,
        password: str,
        server_name: str,
        port: int,
        database_name: str,
        extra_connection_attributes: str,
        status: str,
        kms_key_id: str,
        certificate_arn: Optional[str],
        ssl_mode: Optional[str],
        service_access_role_arn: Optional[str],
        external_table_definition: Optional[str],
        external_id: Optional[str],
        dynamo_db_settings: Optional[dict[str, Any]],
        s3_settings: Optional[dict[str, Any]],
        dms_transfer_settings: Optional[dict[str, Any]],
        mongo_db_settings: Optional[dict[str, Any]],
        kinesis_settings: Optional[dict[str, Any]],
        kafka_settings: Optional[dict[str, Any]],
        elasticsearch_settings: Optional[dict[str, Any]],
        neptune_settings: Optional[dict[str, Any]],
        redshift_settings: Optional[dict[str, Any]],
        postgre_sql_settings: Optional[dict[str, Any]],
        my_sql_settings: Optional[dict[str, Any]],
        oracle_settings: Optional[dict[str, Any]],
        sybase_settings: Optional[dict[str, Any]],
        microsoft_sql_server_settings: Optional[dict[str, Any]],
        ibm_db2_settings: Optional[dict[str, Any]],
        resource_identifier: Optional[str],
        doc_db_settings: Optional[dict[str, Any]],
        redis_settings: Optional[dict[str, Any]],
        gcp_my_sql_settings: Optional[dict[str, Any]],
        timestream_settings: Optional[dict[str, Any]],
        account_id: str,
        region_name: str,
    ):
        self.endpoint_identifier = endpoint_identifier
        self.endpoint_type = endpoint_type
        self.engine_name = engine_name
        self.engine_display_name = engine_display_name
        self.username = username
        self.password = password
        self.server_name = server_name
        self.port = port
        self.database_name = database_name
        self.extra_connection_attributes = extra_connection_attributes
        self.status = status
        self.kms_key_id = kms_key_id

        self.id = resource_identifier if resource_identifier else random_id(True, 27)
        self.endpoint_arn = f"arn:{get_partition(region_name)}:dms:{region_name}:{account_id}:endpoint:{self.id}"

        self.certificate_arn = certificate_arn
        self.ssl_mode = ssl_mode
        self.service_access_role_arn = service_access_role_arn
        self.external_table_definition = external_table_definition
        self.external_id = external_id
        self.dynamo_db_settings = dynamo_db_settings
        self.s3_settings = s3_settings
        self.dms_transfer_settings = dms_transfer_settings
        self.mongo_db_settings = mongo_db_settings
        self.kinesis_settings = kinesis_settings
        self.kafka_settings = kafka_settings
        self.elasticsearch_settings = elasticsearch_settings
        self.neptune_settings = neptune_settings
        self.redshift_settings = redshift_settings
        self.postgre_sql_settings = postgre_sql_settings
        self.my_sql_settings = my_sql_settings
        self.oracle_settings = oracle_settings
        self.sybase_settings = sybase_settings
        self.microsoft_sql_server_settings = microsoft_sql_server_settings
        self.ibm_db2_settings = ibm_db2_settings
        self.doc_db_settings = doc_db_settings
        self.redis_settings = redis_settings
        self.gcp_my_sql_settings = gcp_my_sql_settings
        self.timestream_settings = timestream_settings

    def to_dict(self) -> dict[str, Any]:
        return {
            "EndpointIdentifier": self.endpoint_identifier,
            "EndpointType": self.endpoint_type,
            "EngineName": self.engine_name,
            "EngineDisplayName": self.engine_display_name,
            "Username": self.username,
            "ServerName": self.server_name,
            "Port": self.port,
            "DatabaseName": self.database_name,
            "ExtraConnectionAttributes": self.extra_connection_attributes,
            "Status": self.status,
            "KmsKeyId": self.kms_key_id,
            "EndpointArn": self.endpoint_arn,
            "CertificateArn": self.certificate_arn,
            "SslMode": self.ssl_mode,
            "ServiceAccessRoleArn": self.service_access_role_arn,
            "ExternalTableDefinition": self.external_table_definition,
            "ExternalId": self.external_id,
            "DynamoDbSettings": self.dynamo_db_settings,
            "S3Settings": self.s3_settings,
            "DmsTransferSettings": self.dms_transfer_settings,
            "MongoDbSettings": self.mongo_db_settings,
            "KinesisSettings": self.kinesis_settings,
            "KafkaSettings": self.kafka_settings,
            "ElasticsearchSettings": self.elasticsearch_settings,
            "NeptuneSettings": self.neptune_settings,
            "RedshiftSettings": self.redshift_settings,
            "PostgreSQLSettings": self.postgre_sql_settings,
            "MySQLSettings": self.my_sql_settings,
            "OracleSettings": self.oracle_settings,
            "SybaseSettings": self.sybase_settings,
            "MicrosoftSQLServerSettings": self.microsoft_sql_server_settings,
            "IBMDb2Settings": self.ibm_db2_settings,
            "DocDbSettings": self.doc_db_settings,
            "RedisSettings": self.redis_settings,
            "GcpMySQLSettings": self.gcp_my_sql_settings,
            "TimestreamSettings": self.timestream_settings,
        }

    def delete(self) -> "Endpoint":
        self.status = "deleting"
        return self


class FakeReplicationTask(BaseModel):
    def __init__(
        self,
        replication_task_identifier: str,
        migration_type: str,
        replication_instance_arn: str,
        source_endpoint_arn: str,
        target_endpoint_arn: str,
        table_mappings: str,
        replication_task_settings: str,
        account_id: str,
        region_name: str,
    ):
        self.id = replication_task_identifier
        self.region = region_name
        self.migration_type = migration_type
        self.replication_instance_arn = replication_instance_arn
        self.source_endpoint_arn = source_endpoint_arn
        self.target_endpoint_arn = target_endpoint_arn
        self.table_mappings = table_mappings
        self.replication_task_settings = replication_task_settings

        self.arn = f"arn:{get_partition(region_name)}:dms:{region_name}:{account_id}:task:{self.id}"
        self.status = "creating"

        self.creation_date = utcnow()
        self.start_date: Optional[datetime] = None
        self.stop_date: Optional[datetime] = None

    def to_dict(self) -> dict[str, Any]:
        start_date = self.start_date.isoformat() if self.start_date else None
        stop_date = self.stop_date.isoformat() if self.stop_date else None

        return {
            "ReplicationTaskIdentifier": self.id,
            "SourceEndpointArn": self.source_endpoint_arn,
            "TargetEndpointArn": self.target_endpoint_arn,
            "ReplicationInstanceArn": self.replication_instance_arn,
            "MigrationType": self.migration_type,
            "TableMappings": self.table_mappings,
            "ReplicationTaskSettings": self.replication_task_settings,
            "Status": self.status,
            "ReplicationTaskCreationDate": self.creation_date.isoformat(),
            "ReplicationTaskStartDate": start_date,
            "ReplicationTaskArn": self.arn,
            "ReplicationTaskStats": {
                "FullLoadProgressPercent": 100,
                "ElapsedTimeMillis": 100,
                "TablesLoaded": 1,
                "TablesLoading": 0,
                "TablesQueued": 0,
                "TablesErrored": 0,
                "FreshStartDate": start_date,
                "StartDate": start_date,
                "StopDate": stop_date,
                "FullLoadStartDate": start_date,
                "FullLoadFinishDate": stop_date,
            },
        }

    def ready(self) -> "FakeReplicationTask":
        self.status = "ready"
        return self

    def start(self) -> "FakeReplicationTask":
        self.status = "starting"
        self.start_date = utcnow()
        self.run()
        return self

    def stop(self) -> "FakeReplicationTask":
        if self.status != "running":
            raise InvalidResourceStateFault("Replication task is not running")

        self.status = "stopped"
        self.stop_date = utcnow()
        return self

    def delete(self) -> "FakeReplicationTask":
        self.status = "deleting"
        return self

    def run(self) -> "FakeReplicationTask":
        self.status = "running"
        return self


class FakeReplicationInstance(ManagedState):
    def __init__(
        self,
        replication_instance_identifier: str,
        replication_instance_class: str,
        account_id: str,
        region_name: str,
        allocated_storage: Optional[int] = None,
        vpc_security_group_ids: Optional[list[str]] = None,
        availability_zone: Optional[str] = None,
        replication_subnet_group_identifier: Optional[str] = None,
        preferred_maintenance_window: Optional[str] = None,
        multi_az: Optional[bool] = False,
        engine_version: Optional[str] = None,
        auto_minor_version_upgrade: Optional[bool] = True,
        tags: Optional[list[dict[str, str]]] = None,
        kms_key_id: Optional[str] = None,
        publicly_accessible: Optional[bool] = True,
        dns_name_servers: Optional[str] = None,
        resource_identifier: Optional[str] = None,
        network_type: Optional[str] = None,
        kerberos_authentication_settings: Optional[dict[str, str]] = None,
    ):
        ManagedState.__init__(
            self,
            model_name="dms::replicationinstance",
            transitions=[("creating", "available")],
        )

        self.id = replication_instance_identifier
        self.replication_instance_class = replication_instance_class
        self.region = region_name
        self.allocated_storage = allocated_storage or 50
        self.vpc_security_groups = [
            {"VpcSecurityGroupId": sg_id, "Status": "active"}
            for sg_id in (vpc_security_group_ids or [])
        ]
        self.availability_zone = availability_zone
        self.replication_subnet_group_identifier = replication_subnet_group_identifier
        self.preferred_maintenance_window = preferred_maintenance_window
        self.multi_az = multi_az
        self.engine_version = engine_version
        self.auto_minor_version_upgrade = auto_minor_version_upgrade
        self.tags = tags or []
        self.kms_key_id = kms_key_id
        self.publicly_accessible = publicly_accessible
        self.dns_name_servers = dns_name_servers
        self.resource_identifier = resource_identifier
        self.network_type = network_type
        self.kerberos_authentication_settings = kerberos_authentication_settings or {}
        self.arn = f"arn:{get_partition(region_name)}:dms:{region_name}:{account_id}:rep:{self.id}"
        self.creation_date = utcnow()
        self.private_ip_addresses = ["10.0.0.1"]
        self.public_ip_addresses = ["54.0.0.1"] if publicly_accessible else []
        self.ipv6_addresses: list[str] = []

    def to_dict(self) -> dict[str, Any]:
        kerberos_settings = None
        if self.kerberos_authentication_settings:
            kerberos_settings = {
                "KeyCacheSecretId": self.kerberos_authentication_settings.get(
                    "KeyCacheSecretId"
                ),
                "KeyCacheSecretIamArn": self.kerberos_authentication_settings.get(
                    "KeyCacheSecretIamArn"
                ),
                "Krb5FileContents": self.kerberos_authentication_settings.get(
                    "Krb5FileContents"
                ),
            }

        subnet_group = None
        if self.replication_subnet_group_identifier:
            subnet_group = {
                "ReplicationSubnetGroupIdentifier": self.replication_subnet_group_identifier,
                "ReplicationSubnetGroupDescription": f"Subnet group for {self.id}",
                "VpcId": "vpc-12345",
                "SubnetGroupStatus": "Complete",
                "Subnets": [
                    {
                        "SubnetIdentifier": "subnet-12345",
                        "SubnetAvailabilityZone": {
                            "Name": self.availability_zone or "us-east-1a"
                        },
                        "SubnetStatus": "Active",
                    }
                ],
                "SupportedNetworkTypes": [self.network_type]
                if self.network_type
                else ["IPV4"],
            }

        return {
            "ReplicationInstanceIdentifier": self.id,
            "ReplicationInstanceClass": self.replication_instance_class,
            "ReplicationInstanceStatus": self.status,
            "AllocatedStorage": self.allocated_storage,
            "InstanceCreateTime": self.creation_date.isoformat(),
            "VpcSecurityGroups": self.vpc_security_groups,
            "AvailabilityZone": self.availability_zone,
            "ReplicationSubnetGroup": subnet_group,
            "PreferredMaintenanceWindow": self.preferred_maintenance_window,
            "PendingModifiedValues": {},
            "MultiAZ": self.multi_az,
            "EngineVersion": self.engine_version,
            "AutoMinorVersionUpgrade": self.auto_minor_version_upgrade,
            "KmsKeyId": self.kms_key_id,
            "ReplicationInstanceArn": self.arn,
            "ReplicationInstancePublicIpAddress": self.public_ip_addresses[0]
            if self.public_ip_addresses
            else None,
            "ReplicationInstancePrivateIpAddress": self.private_ip_addresses[0]
            if self.private_ip_addresses
            else None,
            "ReplicationInstancePublicIpAddresses": self.public_ip_addresses,
            "ReplicationInstancePrivateIpAddresses": self.private_ip_addresses,
            "ReplicationInstanceIpv6Addresses": self.ipv6_addresses,
            "PubliclyAccessible": self.publicly_accessible,
            "SecondaryAvailabilityZone": f"{self.availability_zone}b"
            if self.multi_az
            else None,
            "FreeUntil": None,
            "DnsNameServers": self.dns_name_servers,
            "NetworkType": self.network_type,
            "KerberosAuthenticationSettings": kerberos_settings,
        }

    def delete(self) -> "FakeReplicationInstance":
        self.status = "deleting"
        return self


class FakeReplicationSubnetGroup(BaseModel):
    def __init__(
        self,
        replication_subnet_group_identifier: str,
        replication_subnet_group_description: str,
        subnetIds: Optional[list[str]] = None,
        tags: Optional[list[dict[str, str]]] = None,
    ):
        self.replication_subnet_group_identifier = replication_subnet_group_identifier
        self.description = replication_subnet_group_description
        self.subnetIds = subnetIds
        self.tags = tags or []

    def to_dict(self) -> dict[str, Any]:
        return {
            "ReplicationSubnetGroupIdentifier": self.replication_subnet_group_identifier,
            "ReplicationSubnetGroupDescription": self.description,
            "VpcId": "vpc-12345",
            "SubnetGroupStatus": "Complete",
            "Subnets": [
                {
                    "SubnetIdentifier": "subnet-12345",
                    "SubnetAvailabilityZone": {"Name": "us-east-1a"},
                    "SubnetStatus": "Active",
                }
            ],
            "SupportedNetworkTypes": ["IPV4"],
        }


class FakeConnection(ManagedState):
    def __init__(
        self,
        replication_instance_arn: str,
        endpoint_arn: str,
        replication_instance_identifier: str,
        endpoint_identifier: str,
    ):
        ManagedState.__init__(
            self,
            model_name="dms::connection",
            transitions=[("testing", "successful")],
        )

        self.replication_instance_arn = replication_instance_arn
        self.endpoint_arn = endpoint_arn
        self.replication_instance_identifier = replication_instance_identifier
        self.endpoint_identifier = endpoint_identifier

    def to_dict(self) -> dict[str, Any]:
        return {
            "ReplicationInstanceArn": self.replication_instance_arn,
            "EndpointArn": self.endpoint_arn,
            "Status": self.status,
            "LastFailureMessage": "",
            "EndpointIdentifier": self.endpoint_identifier,
            "ReplicationInstanceIdentifier": self.replication_instance_identifier,
        }


class FakeEventSubscription(BaseModel):
    def __init__(
        self,
        subscription_name: str,
        sns_topic_arn: str,
        source_type: Optional[str],
        event_categories: list[str],
        source_ids: list[str],
        enabled: bool,
        account_id: str,
        region_name: str,
    ):
        self.subscription_name = subscription_name
        self.sns_topic_arn = sns_topic_arn
        self.source_type = source_type or ""
        self.event_categories = event_categories
        self.source_ids = source_ids
        self.enabled = enabled
        self.status = "active"
        self.creation_time = utcnow()
        self.arn = (
            f"arn:{get_partition(region_name)}:dms:{region_name}:{account_id}:"
            f"es:{self.subscription_name}"
        )
        self.customer_aws_id = account_id

    def to_dict(self) -> dict[str, Any]:
        return {
            "CustomerAwsId": self.customer_aws_id,
            "CustSubscriptionId": self.subscription_name,
            "SnsTopicArn": self.sns_topic_arn,
            "Status": self.status,
            "SubscriptionCreationTime": self.creation_time.isoformat(),
            "SourceType": self.source_type,
            "SourceIdsList": self.source_ids,
            "EventCategoriesList": self.event_categories,
            "Enabled": self.enabled,
        }


class FakeCertificate(BaseModel):
    def __init__(
        self,
        certificate_identifier: str,
        certificate_pem: Optional[str],
        certificate_wallet: Optional[str],
        account_id: str,
        region_name: str,
    ):
        self.certificate_identifier = certificate_identifier
        self.certificate_pem = certificate_pem
        self.certificate_wallet = certificate_wallet
        self.creation_date = utcnow()
        self.arn = (
            f"arn:{get_partition(region_name)}:dms:{region_name}:{account_id}:"
            f"cert:{random_id(True, 24)}"
        )
        self.key_length = 2048
        self.signing_algorithm = "SHA256withRSA"
        self.valid_from_date = self.creation_date
        self.valid_to_date = self.creation_date

    def to_dict(self) -> dict[str, Any]:
        return {
            "CertificateIdentifier": self.certificate_identifier,
            "CertificateCreationDate": self.creation_date.isoformat(),
            "CertificatePem": self.certificate_pem,
            "CertificateWallet": self.certificate_wallet,
            "CertificateArn": self.arn,
            "CertificateOwner": "",
            "ValidFromDate": self.valid_from_date.isoformat(),
            "ValidToDate": self.valid_to_date.isoformat(),
            "SigningAlgorithm": self.signing_algorithm,
            "KeyLength": self.key_length,
        }


class FakeReplicationConfig(BaseModel):
    def __init__(
        self,
        replication_config_identifier: str,
        source_endpoint_arn: str,
        target_endpoint_arn: str,
        compute_config: dict[str, Any],
        replication_type: str,
        table_mappings: str,
        replication_settings: Optional[str],
        supplemental_settings: Optional[str],
        resource_identifier: Optional[str],
        account_id: str,
        region_name: str,
    ):
        self.replication_config_identifier = replication_config_identifier
        self.source_endpoint_arn = source_endpoint_arn
        self.target_endpoint_arn = target_endpoint_arn
        self.compute_config = compute_config
        self.replication_type = replication_type
        self.table_mappings = table_mappings
        self.replication_settings = replication_settings
        self.supplemental_settings = supplemental_settings
        rid = resource_identifier or random_id(True, 24)
        self.arn = (
            f"arn:{get_partition(region_name)}:dms:{region_name}:{account_id}:"
            f"replication-config:{rid}"
        )
        self.status = "created"
        self.creation_date = utcnow()

    def to_dict(self) -> dict[str, Any]:
        return {
            "ReplicationConfigIdentifier": self.replication_config_identifier,
            "ReplicationConfigArn": self.arn,
            "SourceEndpointArn": self.source_endpoint_arn,
            "TargetEndpointArn": self.target_endpoint_arn,
            "ReplicationType": self.replication_type,
            "ComputeConfig": self.compute_config,
            "ReplicationSettings": self.replication_settings,
            "SupplementalSettings": self.supplemental_settings,
            "TableMappings": self.table_mappings,
            "ReplicationConfigCreateTime": self.creation_date.isoformat(),
        }


class FakeDataProvider(BaseModel):
    def __init__(
        self,
        data_provider_name: str,
        engine: str,
        settings: dict[str, Any],
        description: Optional[str],
        account_id: str,
        region_name: str,
    ):
        self.data_provider_name = data_provider_name
        self.engine = engine
        self.settings = settings
        self.description = description or ""
        self.creation_date = utcnow()
        rid = random_id(True, 24)
        self.arn = (
            f"arn:{get_partition(region_name)}:dms:{region_name}:{account_id}:"
            f"data-provider:{rid}"
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "DataProviderName": self.data_provider_name,
            "DataProviderArn": self.arn,
            "DataProviderCreationTime": self.creation_date.isoformat(),
            "Description": self.description,
            "Engine": self.engine,
            "Settings": self.settings,
        }


class FakeInstanceProfile(BaseModel):
    def __init__(
        self,
        instance_profile_name: str,
        availability_zone: Optional[str],
        kms_key_arn: Optional[str],
        publicly_accessible: bool,
        network_type: Optional[str],
        description: Optional[str],
        subnet_group_identifier: Optional[str],
        vpc_security_groups: list[str],
        account_id: str,
        region_name: str,
    ):
        self.instance_profile_name = instance_profile_name
        self.availability_zone = availability_zone
        self.kms_key_arn = kms_key_arn
        self.publicly_accessible = publicly_accessible
        self.network_type = network_type
        self.description = description or ""
        self.subnet_group_identifier = subnet_group_identifier
        self.vpc_security_groups = vpc_security_groups
        self.creation_date = utcnow()
        rid = random_id(True, 24)
        self.arn = (
            f"arn:{get_partition(region_name)}:dms:{region_name}:{account_id}:"
            f"instance-profile:{rid}"
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "InstanceProfileArn": self.arn,
            "AvailabilityZone": self.availability_zone,
            "KmsKeyArn": self.kms_key_arn,
            "PubliclyAccessible": self.publicly_accessible,
            "NetworkType": self.network_type,
            "InstanceProfileName": self.instance_profile_name,
            "Description": self.description,
            "InstanceProfileCreationTime": self.creation_date.isoformat(),
            "SubnetGroupIdentifier": self.subnet_group_identifier,
            "VpcSecurityGroups": self.vpc_security_groups,
        }


class FakeMigrationProject(BaseModel):
    def __init__(
        self,
        migration_project_name: str,
        source_data_provider_descriptors: list[dict[str, Any]],
        target_data_provider_descriptors: list[dict[str, Any]],
        instance_profile_identifier: Optional[str],
        transformation_rules: Optional[str],
        description: Optional[str],
        schema_conversion_application_attributes: Optional[dict[str, Any]],
        account_id: str,
        region_name: str,
    ):
        self.migration_project_name = migration_project_name
        self.source_data_provider_descriptors = source_data_provider_descriptors
        self.target_data_provider_descriptors = target_data_provider_descriptors
        self.instance_profile_identifier = instance_profile_identifier
        self.transformation_rules = transformation_rules
        self.description = description or ""
        self.schema_conversion_application_attributes = (
            schema_conversion_application_attributes
        )
        self.creation_date = utcnow()
        rid = random_id(True, 24)
        self.arn = (
            f"arn:{get_partition(region_name)}:dms:{region_name}:{account_id}:"
            f"migration-project:{rid}"
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "MigrationProjectName": self.migration_project_name,
            "MigrationProjectArn": self.arn,
            "MigrationProjectCreationTime": self.creation_date.isoformat(),
            "SourceDataProviderDescriptors": self.source_data_provider_descriptors,
            "TargetDataProviderDescriptors": self.target_data_provider_descriptors,
            "InstanceProfileArn": self.instance_profile_identifier,
            "InstanceProfileName": "",
            "TransformationRules": self.transformation_rules,
            "Description": self.description,
            "SchemaConversionApplicationAttributes": self.schema_conversion_application_attributes,
        }


class FakeDataMigration(BaseModel):
    def __init__(
        self,
        data_migration_name: str,
        migration_project_identifier: str,
        data_migration_type: str,
        service_access_role_arn: str,
        source_data_settings: list[dict[str, Any]],
        enable_cloudwatch_logs: bool,
        account_id: str,
        region_name: str,
    ):
        self.data_migration_name = data_migration_name
        self.migration_project_identifier = migration_project_identifier
        self.data_migration_type = data_migration_type
        self.service_access_role_arn = service_access_role_arn
        self.source_data_settings = source_data_settings
        self.enable_cloudwatch_logs = enable_cloudwatch_logs
        self.status = "created"
        self.creation_date = utcnow()
        rid = random_id(True, 24)
        self.arn = (
            f"arn:{get_partition(region_name)}:dms:{region_name}:{account_id}:"
            f"data-migration:{rid}"
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "DataMigrationName": self.data_migration_name,
            "DataMigrationArn": self.arn,
            "DataMigrationCreateTime": self.creation_date.isoformat(),
            "DataMigrationType": self.data_migration_type,
            "ServiceAccessRoleArn": self.service_access_role_arn,
            "MigrationProjectArn": self.migration_project_identifier,
            "DataMigrationSettings": {
                "EnableCloudwatchLogs": self.enable_cloudwatch_logs,
            },
            "SourceDataSettings": self.source_data_settings,
            "DataMigrationStatus": self.status,
        }


dms_backends = BackendDict(DatabaseMigrationServiceBackend, "dms")
