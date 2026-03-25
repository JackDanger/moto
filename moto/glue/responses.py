import json
from typing import Any, Optional, Union

from moto.core.responses import ActionResult, BaseResponse, EmptyResult

from .exceptions import EntityNotFoundException, InvalidInputException
from .models import (
    FakeCrawler,
    FakeJob,
    FakeSession,
    FakeTrigger,
    GlueBackend,
    glue_backends,
)
from .utils import Action, Predicate, validate_crawl_filters


class GlueResponse(BaseResponse):
    def __init__(self) -> None:
        super().__init__(service_name="glue")

    @property
    def glue_backend(self) -> GlueBackend:
        return glue_backends[self.current_account][self.region]

    @property
    def parameters(self) -> dict[str, Any]:  # type: ignore[misc]
        return json.loads(self.body)

    def create_database(self) -> ActionResult:
        database_input = self.parameters.get("DatabaseInput")
        database_name = database_input.get("Name")  # type: ignore
        if "CatalogId" in self.parameters:
            database_input["CatalogId"] = self.parameters.get("CatalogId")  # type: ignore
        self.glue_backend.create_database(
            database_name,
            database_input,  # type: ignore[arg-type]
            self.parameters.get("Tags"),
        )
        return EmptyResult()

    def get_database(self) -> ActionResult:
        database_name = self.parameters.get("Name")
        database = self.glue_backend.get_database(database_name)  # type: ignore[arg-type]
        return ActionResult({"Database": database.as_dict()})

    def get_databases(self) -> ActionResult:
        database_list = self.glue_backend.get_databases()
        return ActionResult(
            {"DatabaseList": [database.as_dict() for database in database_list]}
        )

    def update_database(self) -> ActionResult:
        database_input = self.parameters.get("DatabaseInput")
        database_name = self.parameters.get("Name")
        if "CatalogId" in self.parameters:
            database_input["CatalogId"] = self.parameters.get("CatalogId")  # type: ignore
        self.glue_backend.update_database(database_name, database_input)  # type: ignore[arg-type]
        return EmptyResult()

    def delete_database(self) -> EmptyResult:
        name = self.parameters.get("Name")
        self.glue_backend.delete_database(name)  # type: ignore[arg-type]
        return EmptyResult()

    def create_table(self) -> ActionResult:
        database_name = self.parameters.get("DatabaseName")
        table_input = self.parameters.get("TableInput")
        if not table_input:
            raise InvalidInputException("CreateTable", "TableInput is required.")
        table_name = table_input.get("Name")  # type: ignore
        self.glue_backend.create_table(database_name, table_name, table_input)  # type: ignore[arg-type]
        return EmptyResult()

    def get_table(self) -> ActionResult:
        database_name = self.parameters.get("DatabaseName")
        table_name = self.parameters.get("Name")
        table = self.glue_backend.get_table(database_name, table_name)  # type: ignore[arg-type]

        return ActionResult({"Table": table.as_dict()})

    def update_table(self) -> ActionResult:
        database_name = self.parameters.get("DatabaseName")
        table_input = self.parameters.get("TableInput")
        if not table_input:
            raise InvalidInputException("UpdateTable", "TableInput is required.")
        table_name = table_input.get("Name")  # type: ignore
        self.glue_backend.update_table(database_name, table_name, table_input)  # type: ignore[arg-type]
        return EmptyResult()

    def get_table_versions(self) -> ActionResult:
        database_name = self.parameters.get("DatabaseName")
        table_name = self.parameters.get("TableName")
        versions = self.glue_backend.get_table_versions(database_name, table_name)  # type: ignore[arg-type]
        return ActionResult(
            {
                "TableVersions": [
                    {"Table": data, "VersionId": version}
                    for version, data in versions.items()
                ]
            }
        )

    def get_table_version(self) -> ActionResult:
        database_name = self.parameters.get("DatabaseName")
        table_name = self.parameters.get("TableName")
        ver_id = self.parameters.get("VersionId")
        return ActionResult(
            self.glue_backend.get_table_version(database_name, table_name, ver_id)  # type: ignore[arg-type]
        )

    def delete_table_version(self) -> ActionResult:
        database_name = self.parameters.get("DatabaseName")
        table_name = self.parameters.get("TableName")
        version_id = self.parameters.get("VersionId")
        self.glue_backend.delete_table_version(database_name, table_name, version_id)  # type: ignore[arg-type]
        return EmptyResult()

    def get_tables(self) -> ActionResult:
        database_name = self.parameters.get("DatabaseName")
        expression = self.parameters.get("Expression")
        tables = self.glue_backend.get_tables(database_name, expression)  # type: ignore[arg-type]
        return ActionResult({"TableList": [table.as_dict() for table in tables]})

    def delete_table(self) -> ActionResult:
        database_name = self.parameters.get("DatabaseName")
        table_name = self.parameters.get("Name")
        self.glue_backend.delete_table(database_name, table_name)  # type: ignore[arg-type]
        return EmptyResult()

    def batch_delete_table(self) -> ActionResult:
        database_name = self.parameters.get("DatabaseName")

        tables = self.parameters.get("TablesToDelete")
        errors = self.glue_backend.batch_delete_table(database_name, tables)  # type: ignore[arg-type]

        out = {}
        if errors:
            out["Errors"] = errors

        return ActionResult(out)

    def get_partitions(self) -> ActionResult:
        database_name = self.parameters.get("DatabaseName")
        table_name = self.parameters.get("TableName")
        expression = self.parameters.get("Expression")
        partitions = self.glue_backend.get_partitions(
            database_name,  # type: ignore[arg-type]
            table_name,  # type: ignore[arg-type]
            expression,  # type: ignore[arg-type]
        )

        return ActionResult({"Partitions": [p.as_dict() for p in partitions]})

    def get_partition(self) -> ActionResult:
        database_name = self.parameters.get("DatabaseName")
        table_name = self.parameters.get("TableName")
        values = self.parameters.get("PartitionValues")

        p = self.glue_backend.get_partition(database_name, table_name, values)  # type: ignore[arg-type]

        return ActionResult({"Partition": p.as_dict()})

    def batch_get_partition(self) -> ActionResult:
        database_name = self.parameters.get("DatabaseName")
        table_name = self.parameters.get("TableName")
        partitions_to_get = self.parameters.get("PartitionsToGet")

        partitions = self.glue_backend.batch_get_partition(
            database_name,  # type: ignore[arg-type]
            table_name,  # type: ignore[arg-type]
            partitions_to_get,  # type: ignore[arg-type]
        )

        return ActionResult({"Partitions": partitions})

    def create_partition(self) -> ActionResult:
        database_name = self.parameters.get("DatabaseName")
        table_name = self.parameters.get("TableName")
        part_input = self.parameters.get("PartitionInput")

        self.glue_backend.create_partition(database_name, table_name, part_input)  # type: ignore[arg-type]
        return EmptyResult()

    def batch_create_partition(self) -> ActionResult:
        database_name = self.parameters.get("DatabaseName")
        table_name = self.parameters.get("TableName")
        partition_input = self.parameters.get("PartitionInputList")
        errors_output = self.glue_backend.batch_create_partition(
            database_name,  # type: ignore[arg-type]
            table_name,  # type: ignore[arg-type]
            partition_input,  # type: ignore[arg-type]
        )

        out = {}
        if errors_output:
            out["Errors"] = errors_output

        return ActionResult(out)

    def update_partition(self) -> ActionResult:
        database_name = self.parameters.get("DatabaseName")
        table_name = self.parameters.get("TableName")
        part_input = self.parameters.get("PartitionInput")
        part_to_update = self.parameters.get("PartitionValueList")

        self.glue_backend.update_partition(
            database_name,  # type: ignore[arg-type]
            table_name,  # type: ignore[arg-type]
            part_input,  # type: ignore[arg-type]
            part_to_update,  # type: ignore[arg-type]
        )
        return EmptyResult()

    def batch_update_partition(self) -> ActionResult:
        database_name = self.parameters.get("DatabaseName")
        table_name = self.parameters.get("TableName")
        entries = self.parameters.get("Entries")

        errors_output = self.glue_backend.batch_update_partition(
            database_name,  # type: ignore[arg-type]
            table_name,  # type: ignore[arg-type]
            entries,  # type: ignore[arg-type]
        )

        out = {}
        if errors_output:
            out["Errors"] = errors_output

        return ActionResult(out)

    def delete_partition(self) -> ActionResult:
        database_name = self.parameters.get("DatabaseName")
        table_name = self.parameters.get("TableName")
        part_to_delete = self.parameters.get("PartitionValues")

        self.glue_backend.delete_partition(database_name, table_name, part_to_delete)  # type: ignore[arg-type]
        return EmptyResult()

    def batch_delete_partition(self) -> ActionResult:
        database_name = self.parameters.get("DatabaseName")
        table_name = self.parameters.get("TableName")
        parts = self.parameters.get("PartitionsToDelete")

        errors_output = self.glue_backend.batch_delete_partition(
            database_name,  # type: ignore[arg-type]
            table_name,  # type: ignore[arg-type]
            parts,  # type: ignore[arg-type]
        )

        out = {}
        if errors_output:
            out["Errors"] = errors_output

        return ActionResult(out)

    def create_crawler(self) -> ActionResult:
        self.glue_backend.create_crawler(
            name=self.parameters.get("Name"),  # type: ignore[arg-type]
            role=self.parameters.get("Role"),  # type: ignore[arg-type]
            database_name=self.parameters.get("DatabaseName"),  # type: ignore[arg-type]
            description=self.parameters.get("Description"),  # type: ignore[arg-type]
            targets=self.parameters.get("Targets"),  # type: ignore[arg-type]
            schedule=self.parameters.get("Schedule"),  # type: ignore[arg-type]
            classifiers=self.parameters.get("Classifiers"),  # type: ignore[arg-type]
            table_prefix=self.parameters.get("TablePrefix"),  # type: ignore[arg-type]
            schema_change_policy=self.parameters.get("SchemaChangePolicy"),  # type: ignore[arg-type]
            recrawl_policy=self.parameters.get("RecrawlPolicy"),  # type: ignore[arg-type]
            lineage_configuration=self.parameters.get("LineageConfiguration"),  # type: ignore[arg-type]
            configuration=self.parameters.get("Configuration"),  # type: ignore[arg-type]
            crawler_security_configuration=self.parameters.get(  # type: ignore[arg-type]
                "CrawlerSecurityConfiguration"
            ),
            tags=self.parameters.get("Tags"),  # type: ignore[arg-type]
        )
        return EmptyResult()

    def get_crawler(self) -> ActionResult:
        name = self.parameters.get("Name")
        crawler = self.glue_backend.get_crawler(name)  # type: ignore[arg-type]
        return ActionResult({"Crawler": crawler.as_dict()})

    def get_crawlers(self) -> ActionResult:
        crawlers = self.glue_backend.get_crawlers()
        return ActionResult({"Crawlers": [crawler.as_dict() for crawler in crawlers]})

    def list_crawlers(self) -> ActionResult:
        next_token = self._get_param("NextToken")
        max_results = self._get_int_param("MaxResults")
        tags = self._get_param("Tags")
        crawlers, next_token = self.glue_backend.list_crawlers(
            next_token=next_token, max_results=max_results
        )
        filtered_crawler_names = self.filter_crawlers_by_tags(crawlers, tags)
        return ActionResult(
            {
                "CrawlerNames": list(filtered_crawler_names),
                "NextToken": next_token,
            }
        )

    def filter_crawlers_by_tags(
        self, crawlers: list[FakeCrawler], tags: dict[str, str]
    ) -> list[str]:
        if not tags:
            return [crawler.get_name() for crawler in crawlers]
        return [
            crawler.get_name()
            for crawler in crawlers
            if self.is_tags_match(crawler.arn, tags)
        ]

    def start_crawler(self) -> ActionResult:
        name = self.parameters.get("Name")
        self.glue_backend.start_crawler(name)  # type: ignore[arg-type]
        return EmptyResult()

    def stop_crawler(self) -> ActionResult:
        name = self.parameters.get("Name")
        self.glue_backend.stop_crawler(name)  # type: ignore[arg-type]
        return EmptyResult()

    def delete_crawler(self) -> ActionResult:
        name = self.parameters.get("Name")
        self.glue_backend.delete_crawler(name)  # type: ignore[arg-type]
        return EmptyResult()

    def list_crawls(self) -> ActionResult:
        crawler_name = self.parameters.get("CrawlerName")
        filters = validate_crawl_filters(self.parameters.get("Filters", []))
        crawls = self.glue_backend.list_crawls(crawler_name, filters)[0]
        return ActionResult({"Crawls": [crawl.as_dict() for crawl in crawls]})

    def create_job(self) -> ActionResult:
        name = self._get_param("Name")
        description = self._get_param("Description")
        log_uri = self._get_param("LogUri")
        role = self._get_param("Role")
        execution_property = self._get_param("ExecutionProperty")
        command = self._get_param("Command")
        default_arguments = self._get_param("DefaultArguments")
        non_overridable_arguments = self._get_param("NonOverridableArguments")
        connections = self._get_param("Connections")
        max_retries = self._get_int_param("MaxRetries")
        allocated_capacity = self._get_int_param("AllocatedCapacity")
        timeout = self._get_int_param("Timeout")
        max_capacity = self._get_param("MaxCapacity")
        security_configuration = self._get_param("SecurityConfiguration")
        tags = self._get_param("Tags")
        notification_property = self._get_param("NotificationProperty")
        glue_version = self._get_param("GlueVersion")
        number_of_workers = self._get_int_param("NumberOfWorkers")
        worker_type = self._get_param("WorkerType")
        code_gen_configuration_nodes = self._get_param("CodeGenConfigurationNodes")
        execution_class = self._get_param("ExecutionClass")
        source_control_details = self._get_param("SourceControlDetails")
        self.glue_backend.create_job(
            name=name,
            description=description,
            log_uri=log_uri,
            role=role,
            execution_property=execution_property,
            command=command,
            default_arguments=default_arguments,
            non_overridable_arguments=non_overridable_arguments,
            connections=connections,
            max_retries=max_retries,
            allocated_capacity=allocated_capacity,
            timeout=timeout,
            max_capacity=max_capacity,
            security_configuration=security_configuration,
            tags=tags,
            notification_property=notification_property,
            glue_version=glue_version,
            number_of_workers=number_of_workers,
            worker_type=worker_type,
            code_gen_configuration_nodes=code_gen_configuration_nodes,
            execution_class=execution_class,
            source_control_details=source_control_details,
        )
        return ActionResult({"Name": name})

    def get_job(self) -> ActionResult:
        name = self.parameters.get("JobName")
        job = self.glue_backend.get_job(name)  # type: ignore[arg-type]
        return ActionResult({"Job": job.as_dict()})

    def get_jobs(self) -> ActionResult:
        next_token = self._get_param("NextToken")
        max_results = self._get_int_param("MaxResults")
        jobs, next_token = self.glue_backend.get_jobs(
            next_token=next_token, max_results=max_results
        )
        return ActionResult(
            {
                "Jobs": [job.as_dict() for job in jobs],
                "NextToken": next_token,
            }
        )

    def start_job_run(self) -> ActionResult:
        allocated_capacity = self._get_int_param("AllocatedCapacity")
        notification_property = self._get_param("NotificationProperty")
        number_of_workers = self._get_int_param("NumberOfWorkers")
        security_configuration = self._get_param("SecurityConfiguration")
        timeout = self._get_int_param("Timeout")
        worker_type = self._get_param("WorkerType")
        name = self._get_param("JobName")
        arguments = self._get_param("Arguments")
        max_capacity = self._get_float_param("MaxCapacity")
        previous_job_run_id = self._get_param("JobRunId")

        if allocated_capacity and max_capacity:
            raise InvalidInputException(
                "StartJobRun", "Please set only Allocated Capacity or Max Capacity"
            )

        job_run_id = self.glue_backend.start_job_run(
            name,
            arguments,
            allocated_capacity,
            max_capacity,
            timeout,
            worker_type,
            security_configuration,
            number_of_workers,
            notification_property,
            previous_job_run_id,
        )
        return ActionResult({"JobRunId": job_run_id})

    def get_job_run(self) -> ActionResult:
        name = self.parameters.get("JobName")
        run_id = self.parameters.get("RunId")
        job_run = self.glue_backend.get_job_run(name, run_id)  # type: ignore[arg-type]
        return ActionResult({"JobRun": job_run.as_dict()})

    def get_job_runs(self) -> ActionResult:
        job_name = self._get_param("JobName")
        next_token = self._get_param("NextToken")
        max_results = self._get_int_param("MaxResults")
        job_runs, next_token = self.glue_backend.get_job_runs(
            job_name,
            next_token=next_token,
            max_results=max_results,
        )
        return ActionResult(
            {
                "JobRuns": [job_run.as_dict() for job_run in job_runs],
                "NextToken": next_token,
            }
        )

    def list_jobs(self) -> ActionResult:
        next_token = self._get_param("NextToken")
        max_results = self._get_int_param("MaxResults")
        tags = self._get_param("Tags")
        jobs, next_token = self.glue_backend.list_jobs(
            next_token=next_token, max_results=max_results
        )
        filtered_job_names = self.filter_jobs_by_tags(jobs, tags)
        return ActionResult(
            {
                "JobNames": list(filtered_job_names),
                "NextToken": next_token,
            }
        )

    def delete_job(self) -> ActionResult:
        name = self.parameters.get("JobName")
        self.glue_backend.delete_job(name)  # type: ignore[arg-type]
        return ActionResult({"JobName": name})

    def get_tags(self) -> ActionResult:
        resource_arn = self.parameters.get("ResourceArn")
        tags = self.glue_backend.get_tags(resource_arn)  # type: ignore[arg-type]
        return ActionResult({"Tags": tags})

    def tag_resource(self) -> ActionResult:
        resource_arn = self.parameters.get("ResourceArn")
        tags = self.parameters.get("TagsToAdd", {})
        self.glue_backend.tag_resource(resource_arn, tags)  # type: ignore[arg-type]
        return EmptyResult()

    def untag_resource(self) -> ActionResult:
        resource_arn = self._get_param("ResourceArn")
        tag_keys = self.parameters.get("TagsToRemove")
        self.glue_backend.untag_resource(resource_arn, tag_keys)  # type: ignore[arg-type]
        return EmptyResult()

    def filter_jobs_by_tags(
        self, jobs: list[FakeJob], tags: dict[str, str]
    ) -> list[str]:
        if not tags:
            return [job.get_name() for job in jobs]
        return [job.get_name() for job in jobs if self.is_tags_match(job.arn, tags)]

    def filter_triggers_by_tags(
        self, triggers: list[FakeTrigger], tags: dict[str, str]
    ) -> list[str]:
        if not tags:
            return [trigger.get_name() for trigger in triggers]
        return [
            trigger.get_name()
            for trigger in triggers
            if self.is_tags_match(trigger.arn, tags)
        ]

    def is_tags_match(self, resource_arn: str, tags: dict[str, str]) -> bool:
        glue_resource_tags = self.glue_backend.get_tags(resource_arn)
        mutual_keys = set(glue_resource_tags).intersection(tags)
        for key in mutual_keys:
            if glue_resource_tags[key] == tags[key]:
                return True
        return False

    def create_registry(self) -> ActionResult:
        registry_name = self._get_param("RegistryName")
        description = self._get_param("Description")
        tags = self._get_param("Tags")
        registry = self.glue_backend.create_registry(registry_name, description, tags)
        return ActionResult(registry)

    def delete_registry(self) -> ActionResult:
        registry_id = self._get_param("RegistryId")
        registry = self.glue_backend.delete_registry(registry_id)
        return ActionResult(registry)

    def get_registry(self) -> ActionResult:
        registry_id = self._get_param("RegistryId")
        registry = self.glue_backend.get_registry(registry_id)
        return ActionResult(registry)

    def list_registries(self) -> ActionResult:
        registries = self.glue_backend.list_registries()
        return ActionResult({"Registries": registries})

    def create_schema(self) -> ActionResult:
        registry_id = self._get_param("RegistryId")
        schema_name = self._get_param("SchemaName")
        data_format = self._get_param("DataFormat")
        compatibility = self._get_param("Compatibility")
        description = self._get_param("Description")
        tags = self._get_param("Tags")
        schema_definition = self._get_param("SchemaDefinition")
        schema = self.glue_backend.create_schema(
            registry_id,
            schema_name,
            data_format,
            compatibility,
            schema_definition,
            description,
            tags,
        )
        return ActionResult(schema)

    def register_schema_version(self) -> ActionResult:
        schema_id = self._get_param("SchemaId")
        schema_definition = self._get_param("SchemaDefinition")
        schema_version = self.glue_backend.register_schema_version(
            schema_id, schema_definition
        )
        return ActionResult(schema_version)

    def get_schema_version(self) -> ActionResult:
        schema_id = self._get_param("SchemaId")
        schema_version_id = self._get_param("SchemaVersionId")
        schema_version_number = self._get_param("SchemaVersionNumber")

        schema_version = self.glue_backend.get_schema_version(
            schema_id, schema_version_id, schema_version_number
        )
        return ActionResult(schema_version)

    def get_schema_by_definition(self) -> ActionResult:
        schema_id = self._get_param("SchemaId")
        schema_definition = self._get_param("SchemaDefinition")
        schema_version = self.glue_backend.get_schema_by_definition(
            schema_id, schema_definition
        )
        return ActionResult(schema_version)

    def put_schema_version_metadata(self) -> ActionResult:
        schema_id = self._get_param("SchemaId")
        schema_version_number = self._get_param("SchemaVersionNumber")
        schema_version_id = self._get_param("SchemaVersionId")
        metadata_key_value = self._get_param("MetadataKeyValue")
        schema_version = self.glue_backend.put_schema_version_metadata(
            schema_id, schema_version_number, schema_version_id, metadata_key_value
        )
        return ActionResult(schema_version)

    def get_schema(self) -> ActionResult:
        schema_id = self._get_param("SchemaId")
        schema = self.glue_backend.get_schema(schema_id)
        return ActionResult(schema)

    def delete_schema(self) -> ActionResult:
        schema_id = self._get_param("SchemaId")
        schema = self.glue_backend.delete_schema(schema_id)
        return ActionResult(schema)

    def update_schema(self) -> ActionResult:
        schema_id = self._get_param("SchemaId")
        compatibility = self._get_param("Compatibility")
        description = self._get_param("Description")
        schema = self.glue_backend.update_schema(schema_id, compatibility, description)
        return ActionResult(schema)

    def create_session(self) -> ActionResult:
        self.glue_backend.create_session(
            session_id=self.parameters.get("Id"),  # type: ignore[arg-type]
            description=self.parameters.get("Description"),  # type: ignore[arg-type]
            role=self.parameters.get("Role"),  # type: ignore[arg-type]
            command=self.parameters.get("Command"),  # type: ignore[arg-type]
            timeout=self.parameters.get("Timeout"),  # type: ignore[arg-type]
            idle_timeout=self.parameters.get("IdleTimeout"),  # type: ignore[arg-type]
            default_arguments=self.parameters.get("DefaultArguments"),  # type: ignore[arg-type]
            connections=self.parameters.get("Connections"),  # type: ignore[arg-type]
            max_capacity=self.parameters.get("MaxCapacity"),  # type: ignore[arg-type]
            number_of_workers=self.parameters.get("NumberOfWorkers"),  # type: ignore[arg-type]
            worker_type=self.parameters.get("WorkerType"),  # type: ignore[arg-type]
            security_configuration=self.parameters.get("SecurityConfiguration"),  # type: ignore[arg-type]
            glue_version=self.parameters.get("GlueVersion"),  # type: ignore[arg-type]
            tags=self.parameters.get("Tags"),  # type: ignore[arg-type]
            request_origin=self.parameters.get("RequestOrigin"),  # type: ignore[arg-type]
        )
        return EmptyResult()

    def get_session(self) -> ActionResult:
        session_id = self.parameters.get("Id")
        session = self.glue_backend.get_session(session_id)  # type: ignore[arg-type]
        return ActionResult({"Session": session.as_dict()})

    def list_sessions(self) -> ActionResult:
        next_token = self._get_param("NextToken")
        max_results = self._get_int_param("MaxResults")
        tags = self._get_param("Tags")
        sessions, next_token = self.glue_backend.list_sessions(
            next_token=next_token, max_results=max_results
        )
        filtered_session_ids = self._filter_sessions_by_tags(sessions, tags)

        return ActionResult(
            {
                "Ids": list(filtered_session_ids),
                "Sessions": [
                    self.glue_backend.get_session(session_id).as_dict()
                    for session_id in filtered_session_ids
                ],
                "NextToken": next_token,
            }
        )

    def _filter_sessions_by_tags(
        self, sessions: list[FakeSession], tags: dict[str, str]
    ) -> list[str]:
        if not tags:
            return [session.get_id() for session in sessions]
        return [
            session.get_id()
            for session in sessions
            if self.is_tags_match(session.arn, tags)
        ]

    def stop_session(self) -> ActionResult:
        session_id = self.parameters.get("Id")
        self.glue_backend.stop_session(session_id)  # type: ignore[arg-type]
        return ActionResult({"Id": session_id})

    def delete_session(self) -> ActionResult:
        session_id = self.parameters.get("Id")
        self.glue_backend.delete_session(session_id)  # type: ignore[arg-type]
        return ActionResult({"Id": session_id})

    def batch_get_crawlers(self) -> ActionResult:
        crawler_names = self._get_param("CrawlerNames")
        crawlers = self.glue_backend.batch_get_crawlers(crawler_names)
        crawlers_not_found = list(
            set(crawler_names) - {crawler["Name"] for crawler in crawlers}
        )
        return ActionResult(
            {
                "Crawlers": crawlers,
                "CrawlersNotFound": crawlers_not_found,
            }
        )

    def batch_get_jobs(self) -> ActionResult:
        job_names = self._get_param("JobNames")
        jobs = self.glue_backend.batch_get_jobs(job_names)
        jobs_not_found = list(set(job_names) - {job["Name"] for job in jobs})
        return ActionResult(
            {
                "Jobs": jobs,
                "JobsNotFound": jobs_not_found,
            }
        )

    def get_partition_indexes(self) -> ActionResult:
        return ActionResult({"PartitionIndexDescriptorList": []})

    def create_trigger(self) -> ActionResult:
        name = self._get_param("Name")
        workflow_name = self._get_param("WorkflowName")
        trigger_type = self._get_param("Type")
        schedule = self._get_param("Schedule")

        predicate_input: Optional[dict[str, Union[str, list[dict[str, str]]]]] = (
            self._get_param("Predicate")
        )
        if predicate_input:
            predicate = Predicate(predicate_input)
        else:
            predicate = None

        actions = [Action(inputs) for inputs in self._get_param("Actions", [])]
        description = self._get_param("Description")
        start_on_creation = self._get_param("StartOnCreation")
        tags = self._get_param("Tags")
        event_batching_condition = self._get_param("EventBatchingCondition")

        if trigger_type == "CONDITIONAL" and not predicate:
            raise InvalidInputException(
                "CreateTrigger", "Predicate cannot be null or empty"
            )

        self.glue_backend.create_trigger(
            name=name,
            workflow_name=workflow_name,
            trigger_type=trigger_type,
            schedule=schedule,
            predicate=predicate,
            actions=actions,
            description=description,
            start_on_creation=start_on_creation,
            tags=tags,
            event_batching_condition=event_batching_condition,
        )
        return ActionResult({"Name": name})

    def get_trigger(self) -> ActionResult:
        name = self.parameters.get("Name")
        trigger = self.glue_backend.get_trigger(name)  # type: ignore[arg-type]
        return ActionResult({"Trigger": trigger.as_dict()})

    def get_triggers(self) -> ActionResult:
        next_token = self._get_param("NextToken")
        dependent_job_name = self._get_param("DependentJobName")
        max_results = self._get_int_param("MaxResults")
        triggers, next_token = self.glue_backend.get_triggers(
            next_token=next_token,
            dependent_job_name=dependent_job_name,
            max_results=max_results,
        )
        return ActionResult(
            {
                "Triggers": [trigger.as_dict() for trigger in triggers],
                "NextToken": next_token,
            }
        )

    def list_triggers(self) -> ActionResult:
        next_token = self._get_param("NextToken")
        dependent_job_name = self._get_param("DependentJobName")
        max_results = self._get_int_param("MaxResults")
        tags = self._get_param("Tags")
        triggers, next_token = self.glue_backend.list_triggers(
            next_token=next_token,
            dependent_job_name=dependent_job_name,
            max_results=max_results,
        )
        filtered_trigger_names = self.filter_triggers_by_tags(triggers, tags)
        return ActionResult(
            {
                "TriggerNames": list(filtered_trigger_names),
                "NextToken": next_token,
            }
        )

    def batch_get_triggers(self) -> ActionResult:
        trigger_names = self._get_param("TriggerNames")
        triggers = self.glue_backend.batch_get_triggers(trigger_names)
        triggers_not_found = list(
            set(trigger_names) - {trigger["Name"] for trigger in triggers}
        )
        return ActionResult(
            {
                "Triggers": triggers,
                "TriggersNotFound": triggers_not_found,
            }
        )

    def start_trigger(self) -> ActionResult:
        name = self.parameters.get("Name")
        self.glue_backend.start_trigger(name)  # type: ignore[arg-type]
        return ActionResult({"Name": name})

    def stop_trigger(self) -> ActionResult:
        name = self.parameters.get("Name")
        self.glue_backend.stop_trigger(name)  # type: ignore[arg-type]
        return ActionResult({"Name": name})

    def delete_trigger(self) -> ActionResult:
        name = self.parameters.get("Name")
        self.glue_backend.delete_trigger(name)  # type: ignore[arg-type]
        return ActionResult({"Name": name})

    def get_dev_endpoints(self) -> ActionResult:
        next_token = self._get_param("NextToken")
        max_results = self._get_int_param("MaxResults")

        endpoints, next_token = self.glue_backend.get_dev_endpoints(
            next_token=next_token, max_results=max_results
        )

        return ActionResult(
            {
                "DevEndpoints": [endpoint.as_dict() for endpoint in endpoints],
                "NextToken": next_token,
            }
        )

    def create_dev_endpoint(self) -> ActionResult:
        endpoint_name = self._get_param("EndpointName")
        role_arn = self._get_param("RoleArn")
        security_group_ids = self._get_param("SecurityGroupIds")
        subnet_id = self._get_param("SubnetId")
        public_key = self._get_param("PublicKey")
        public_keys = self._get_param("PublicKeys")
        number_of_nodes = self._get_int_param("NumberOfNodes")
        worker_type = self._get_param("WorkerType", "Standard")
        glue_version = self._get_param("GlueVersion", "1.0")
        number_of_workers = self._get_int_param("NumberOfWorkers")
        extra_python_libs_s3_path = self._get_param("ExtraPythonLibsS3Path")
        extra_jars_s3_path = self._get_param("ExtraJarsS3Path")
        security_configuration = self._get_param("SecurityConfiguration")
        tags = self._get_param("Tags")
        arguments = self._get_param("Arguments")

        dev_endpoint = self.glue_backend.create_dev_endpoint(
            endpoint_name=endpoint_name,
            role_arn=role_arn,
            security_group_ids=security_group_ids,
            subnet_id=subnet_id,
            public_key=public_key,
            public_keys=public_keys,
            number_of_nodes=number_of_nodes,
            worker_type=worker_type,
            glue_version=glue_version,
            number_of_workers=number_of_workers,
            extra_python_libs_s3_path=extra_python_libs_s3_path,
            extra_jars_s3_path=extra_jars_s3_path,
            security_configuration=security_configuration,
            tags=tags,
            arguments=arguments,
        )

        return ActionResult(dev_endpoint.as_dict())

    def get_dev_endpoint(self) -> ActionResult:
        endpoint_name = self._get_param("EndpointName")
        dev_endpoint = self.glue_backend.get_dev_endpoint(endpoint_name)
        return ActionResult({"DevEndpoint": dev_endpoint.as_dict()})

    def delete_dev_endpoint(self) -> ActionResult:
        endpoint_name = self._get_param("EndpointName")
        self.glue_backend.delete_dev_endpoint(endpoint_name)
        return EmptyResult()

    def create_connection(self) -> ActionResult:
        catalog_id = self._get_param("CatalogId")
        connection_input = self._get_param("ConnectionInput")
        tags = self._get_param("Tags")
        create_connection_status = self.glue_backend.create_connection(
            catalog_id=catalog_id,
            connection_input=connection_input,
            tags=tags,
        )
        return ActionResult({"CreateConnectionStatus": create_connection_status})

    def get_connection(self) -> ActionResult:
        catalog_id = self._get_param("CatalogId")
        name = self._get_param("Name")
        hide_password = self._get_param("HidePassword")
        apply_override_for_compute_environment = self._get_param(
            "ApplyOverrideForComputeEnvironment"
        )
        connection = self.glue_backend.get_connection(
            catalog_id=catalog_id,
            name=name,
            hide_password=hide_password,
            apply_override_for_compute_environment=apply_override_for_compute_environment,
        )
        return ActionResult({"Connection": connection.as_dict()})

    def get_connections(self) -> ActionResult:
        catalog_id = self._get_param("CatalogId")
        filter = self._get_param("Filter")
        hide_password = self._get_param("HidePassword")
        next_token = self._get_param("NextToken")
        max_results = self._get_param("MaxResults")
        connections, next_token = self.glue_backend.get_connections(
            catalog_id=catalog_id,
            filter=filter,
            hide_password=hide_password,
            next_token=next_token,
            max_results=max_results,
        )
        connection_list = [connection.as_dict() for connection in connections]
        return ActionResult(
            {"ConnectionList": connection_list, "NextToken": next_token}
        )

    def put_data_catalog_encryption_settings(self) -> ActionResult:
        params = self.parameters
        catalog_id = params.get("CatalogId", None)
        data_catalog_encryption_settings = params.get(
            "DataCatalogEncryptionSettings", {}
        )

        self.glue_backend.put_data_catalog_encryption_settings(
            catalog_id=catalog_id,
            data_catalog_encryption_settings=data_catalog_encryption_settings,
        )

        return EmptyResult()

    def get_data_catalog_encryption_settings(self) -> ActionResult:
        params = self.parameters
        catalog_id = params.get("CatalogId", None)

        response = self.glue_backend.get_data_catalog_encryption_settings(
            catalog_id=catalog_id,
        )

        return ActionResult(response)

    def put_resource_policy(self) -> ActionResult:
        params = json.loads(self.body)
        policy_in_json = params.get("PolicyInJson")
        resource_arn = params.get("ResourceArn")
        policy_hash_condition = params.get("PolicyHashCondition")
        policy_exists_condition = params.get("PolicyExistsCondition")
        enable_hybrid = params.get("EnableHybrid")

        policy_hash = self.glue_backend.put_resource_policy(
            policy_in_json=policy_in_json,
            resource_arn=resource_arn,
            policy_hash_condition=policy_hash_condition,
            policy_exists_condition=policy_exists_condition,
            enable_hybrid=enable_hybrid,
        )

        return ActionResult(policy_hash)

    def get_resource_policy(self) -> ActionResult:
        params = json.loads(self.body)
        resource_arn = params.get("ResourceArn")
        response = self.glue_backend.get_resource_policy(
            resource_arn=resource_arn,
        )

        return ActionResult(response)

    def delete_resource_policy(self) -> ActionResult:
        params = json.loads(self.body)
        policy_hash_condition = params.get("PolicyHashCondition")
        resource_arn = params.get("ResourceArn")
        self.glue_backend.delete_resource_policy(
            resource_arn=resource_arn,
            policy_hash_condition=policy_hash_condition,
        )

        return EmptyResult()

    def create_workflow(self) -> ActionResult:
        name = self._get_param("Name")
        default_run_properties = self._get_param("DefaultRunProperties")
        description = self._get_param("Description")
        max_concurrent_runs = self._get_int_param("MaxConcurrentRuns")
        tags = self._get_param("Tags")

        workflow_name = self.glue_backend.create_workflow(
            name,
            default_run_properties,
            description,
            max_concurrent_runs,
            tags,
        )
        return ActionResult({"Name": workflow_name})

    def get_workflow(self) -> ActionResult:
        name = self._get_param("Name")

        workflow = self.glue_backend.get_workflow(name)
        return ActionResult({"Workflow": workflow})

    def list_workflows(self) -> ActionResult:
        next_token = self._get_param("NextToken")
        max_results = self._get_int_param("MaxResults")

        workflows, next_token = self.glue_backend.list_workflows(
            next_token=next_token, max_results=max_results
        )
        return ActionResult(
            {
                "NextToken": next_token,
                "Workflows": workflows,
            }
        )

    def batch_get_workflows(self) -> ActionResult:
        names = self._get_param("Names")
        workflows = []
        missing_workflows = []

        for name in names:
            try:
                workflow = self.glue_backend.get_workflow(name)
                workflows.append(workflow)
            except EntityNotFoundException:
                missing_workflows.append(name)

        return ActionResult(
            {"MissingWorkflows": missing_workflows, "Workflows": workflows}
        )

    def update_workflow(self) -> ActionResult:
        name = self._get_param("Name")
        default_run_properties = self._get_param("DefaultRunProperties")
        description = self._get_param("Description")
        max_concurrent_runs = self._get_int_param("MaxConcurrentRuns")

        name = self.glue_backend.update_workflow(
            name,
            default_run_properties,
            description,
            max_concurrent_runs,
        )

        return ActionResult({"Name": name})

    def delete_workflow(self) -> ActionResult:
        name = self._get_param("Name")
        name = self.glue_backend.delete_workflow(name)

        return ActionResult({"Name": name})

    def get_workflow_run(self) -> ActionResult:
        workflow_name = self._get_param("Name")
        run_id = self._get_param("RunId")

        workflow_run = self.glue_backend.get_workflow_run(workflow_name, run_id)
        return ActionResult({"Run": workflow_run})

    def get_workflow_runs(self) -> ActionResult:
        workflow_name = self._get_param("Name")
        next_token = self._get_param("NextToken")
        max_results = self._get_int_param("MaxResults")

        workflow_runs, next_token = self.glue_backend.get_workflow_runs(
            workflow_name,
            next_token=next_token,
            max_results=max_results,
        )
        return ActionResult(
            {
                "Runs": workflow_runs,
                "NextToken": next_token,
            }
        )

    def start_workflow_run(self) -> ActionResult:
        workflow_name = self._get_param("Name")
        properties = self._get_param("RunProperties")

        run_id = self.glue_backend.start_workflow_run(workflow_name, properties)
        return ActionResult({"RunId": run_id})

    def stop_workflow_run(self) -> ActionResult:
        workflow_name = self._get_param("Name")
        run_id = self._get_param("RunId")

        self.glue_backend.stop_workflow_run(workflow_name, run_id)
        return EmptyResult()

    def get_workflow_run_properties(self) -> ActionResult:
        workflow_name = self._get_param("Name")
        run_id = self._get_param("RunId")

        run_properties = self.glue_backend.get_workflow_run_properties(
            workflow_name, run_id
        )
        return ActionResult({"RunProperties": run_properties})

    def put_workflow_run_properties(self) -> ActionResult:
        workflow_name = self._get_param("Name")
        run_id = self._get_param("RunId")
        run_properties = self._get_param("RunProperties")

        self.glue_backend.put_workflow_run_properties(
            workflow_name, run_id, run_properties
        )
        return EmptyResult()

    def create_security_configuration(self) -> ActionResult:
        name = self._get_param("Name")
        configuration = self._get_param("EncryptionConfiguration")

        sc = self.glue_backend.create_security_configuration(name, configuration)
        return ActionResult({"Name": sc.name, "CreatedTimestamp": sc.created_time})

    def get_security_configuration(self) -> ActionResult:
        name = self._get_param("Name")
        security_configuration = self.glue_backend.get_security_configuration(name)
        return ActionResult({"SecurityConfiguration": security_configuration.as_dict()})

    def delete_security_configuration(self) -> ActionResult:
        name = self._get_param("Name")
        self.glue_backend.delete_security_configuration(name)
        return EmptyResult()

    def get_security_configurations(self) -> ActionResult:
        security_configurations = self.glue_backend.get_security_configurations()

        return ActionResult(
            {
                "SecurityConfigurations": [
                    sc.as_dict() for sc in security_configurations
                ],
                "NextToken": None,
            }
        )

    # --- Catalogs ---

    def create_catalog(self) -> ActionResult:
        name = self._get_param("Name")
        catalog_input = self._get_param("CatalogInput")
        tags = self._get_param("Tags")
        self.glue_backend.create_catalog(name, catalog_input or {}, tags)
        return EmptyResult()

    def get_catalog(self) -> ActionResult:
        catalog_id = self._get_param("CatalogId")
        catalog = self.glue_backend.get_catalog(catalog_id)
        return ActionResult({"Catalog": catalog.as_dict()})

    def update_catalog(self) -> ActionResult:
        catalog_id = self._get_param("CatalogId")
        catalog_input = self._get_param("CatalogInput")
        self.glue_backend.update_catalog(catalog_id, catalog_input or {})
        return EmptyResult()

    def delete_catalog(self) -> ActionResult:
        catalog_id = self._get_param("CatalogId")
        self.glue_backend.delete_catalog(catalog_id)
        return EmptyResult()

    # --- Data Quality Rulesets ---

    def create_data_quality_ruleset(self) -> ActionResult:
        name = self._get_param("Name")
        ruleset = self._get_param("Ruleset")
        description = self._get_param("Description")
        target_table = self._get_param("TargetTable")
        tags = self._get_param("Tags")
        self.glue_backend.create_data_quality_ruleset(
            name, ruleset, description, target_table, tags
        )
        return ActionResult({"Name": name})

    def get_data_quality_ruleset(self) -> ActionResult:
        name = self._get_param("Name")
        dq = self.glue_backend.get_data_quality_ruleset(name)
        return ActionResult(dq.as_dict())

    def update_data_quality_ruleset(self) -> ActionResult:
        name = self._get_param("Name")
        ruleset = self._get_param("Ruleset")
        description = self._get_param("Description")
        self.glue_backend.update_data_quality_ruleset(name, ruleset, description)
        return ActionResult({"Name": name})

    def delete_data_quality_ruleset(self) -> ActionResult:
        name = self._get_param("Name")
        self.glue_backend.delete_data_quality_ruleset(name)
        return EmptyResult()

    def list_data_quality_rulesets(self) -> ActionResult:
        next_token = self._get_param("NextToken")
        max_results = self._get_int_param("MaxResults")
        rulesets, next_token = self.glue_backend.list_data_quality_rulesets(
            next_token=next_token, max_results=max_results
        )
        return ActionResult(
            {
                "Rulesets": [r.as_dict() for r in rulesets],
                "NextToken": next_token,
            }
        )

    # --- Blueprints ---

    def create_blueprint(self) -> ActionResult:
        name = self._get_param("Name")
        blueprint_location = self._get_param("BlueprintLocation")
        description = self._get_param("Description")
        tags = self._get_param("Tags")
        self.glue_backend.create_blueprint(name, blueprint_location, description, tags)
        return ActionResult({"Name": name})

    def get_blueprint(self) -> ActionResult:
        name = self._get_param("Name")
        bp = self.glue_backend.get_blueprint(name)
        return ActionResult({"Blueprint": bp.as_dict()})

    def update_blueprint(self) -> ActionResult:
        name = self._get_param("Name")
        blueprint_location = self._get_param("BlueprintLocation")
        description = self._get_param("Description")
        self.glue_backend.update_blueprint(name, blueprint_location, description)
        return ActionResult({"Name": name})

    def delete_blueprint(self) -> ActionResult:
        name = self._get_param("Name")
        self.glue_backend.delete_blueprint(name)
        return EmptyResult()

    def list_blueprints(self) -> ActionResult:
        next_token = self._get_param("NextToken")
        max_results = self._get_int_param("MaxResults")
        blueprints, next_token = self.glue_backend.list_blueprints(
            next_token=next_token, max_results=max_results
        )
        return ActionResult(
            {
                "Blueprints": [bp.name for bp in blueprints],
                "NextToken": next_token,
            }
        )

    # --- ML Transforms ---

    def create_ml_transform(self) -> ActionResult:
        name = self._get_param("Name")
        input_record_tables = self._get_param("InputRecordTables")
        parameters = self._get_param("Parameters")
        role = self._get_param("Role")
        description = self._get_param("Description")
        glue_version = self._get_param("GlueVersion")
        max_capacity = self._get_param("MaxCapacity")
        worker_type = self._get_param("WorkerType")
        number_of_workers = self._get_int_param("NumberOfWorkers")
        timeout = self._get_int_param("Timeout")
        max_retries = self._get_int_param("MaxRetries")
        tags = self._get_param("Tags")
        transform = self.glue_backend.create_ml_transform(
            name=name,
            input_record_tables=input_record_tables,
            parameters=parameters,
            role=role,
            description=description,
            glue_version=glue_version,
            max_capacity=max_capacity,
            worker_type=worker_type,
            number_of_workers=number_of_workers,
            timeout=timeout,
            max_retries=max_retries,
            tags=tags,
        )
        return ActionResult({"TransformId": transform.transform_id})

    def get_ml_transform(self) -> ActionResult:
        transform_id = self._get_param("TransformId")
        transform = self.glue_backend.get_ml_transform(transform_id)
        return ActionResult(transform.as_dict())

    def update_ml_transform(self) -> ActionResult:
        transform_id = self._get_param("TransformId")
        self.glue_backend.update_ml_transform(
            transform_id=transform_id,
            name=self._get_param("Name"),
            description=self._get_param("Description"),
            parameters=self._get_param("Parameters"),
            role=self._get_param("Role"),
            glue_version=self._get_param("GlueVersion"),
            max_capacity=self._get_param("MaxCapacity"),
            worker_type=self._get_param("WorkerType"),
            number_of_workers=self._get_int_param("NumberOfWorkers"),
            timeout=self._get_int_param("Timeout"),
            max_retries=self._get_int_param("MaxRetries"),
        )
        return ActionResult({"TransformId": transform_id})

    def delete_ml_transform(self) -> ActionResult:
        transform_id = self._get_param("TransformId")
        self.glue_backend.delete_ml_transform(transform_id)
        return ActionResult({"TransformId": transform_id})

    def get_ml_transforms(self) -> ActionResult:
        next_token = self._get_param("NextToken")
        max_results = self._get_int_param("MaxResults")
        transforms, next_token = self.glue_backend.list_ml_transforms(
            next_token=next_token, max_results=max_results
        )
        return ActionResult(
            {
                "Transforms": [t.as_dict() for t in transforms],
                "NextToken": next_token,
            }
        )

    # --- Classifiers ---

    def create_classifier(self) -> ActionResult:
        self.glue_backend.create_classifier(
            grok_classifier=self._get_param("GrokClassifier"),
            xml_classifier=self._get_param("XMLClassifier"),
            json_classifier=self._get_param("JsonClassifier"),
            csv_classifier=self._get_param("CsvClassifier"),
        )
        return EmptyResult()

    def get_classifier(self) -> ActionResult:
        name = self._get_param("Name")
        classifier = self.glue_backend.get_classifier(name)
        return ActionResult({"Classifier": classifier.as_dict()})

    def update_classifier(self) -> ActionResult:
        self.glue_backend.update_classifier(
            grok_classifier=self._get_param("GrokClassifier"),
            xml_classifier=self._get_param("XMLClassifier"),
            json_classifier=self._get_param("JsonClassifier"),
            csv_classifier=self._get_param("CsvClassifier"),
        )
        return EmptyResult()

    def delete_classifier(self) -> ActionResult:
        name = self._get_param("Name")
        self.glue_backend.delete_classifier(name)
        return EmptyResult()

    def get_classifiers(self) -> ActionResult:
        next_token = self._get_param("NextToken")
        max_results = self._get_int_param("MaxResults")
        classifiers, next_token = self.glue_backend.list_classifiers(
            next_token=next_token, max_results=max_results
        )
        return ActionResult(
            {
                "Classifiers": [c.as_dict() for c in classifiers],
                "NextToken": next_token,
            }
        )

    # --- Resource Policies (batch) ---

    def get_resource_policies(self) -> ActionResult:
        policies = self.glue_backend.get_resource_policies()
        return ActionResult(
            {
                "GetResourcePoliciesResponseList": policies,
                "NextToken": None,
            }
        )

    # --- Catalog Import Status ---

    def get_catalog_import_status(self) -> ActionResult:
        status = self.glue_backend.get_catalog_import_status()
        return ActionResult({"ImportStatus": status})

    # --- Column Statistics ---

    def get_column_statistics_for_table(self) -> ActionResult:
        database_name = self._get_param("DatabaseName")
        table_name = self._get_param("TableName")
        column_names = self._get_param("ColumnNames") or []
        result = self.glue_backend.get_column_statistics_for_table(
            database_name, table_name, column_names
        )
        return ActionResult(result)

    def get_column_statistics_for_partition(self) -> ActionResult:
        database_name = self._get_param("DatabaseName")
        table_name = self._get_param("TableName")
        partition_values = self._get_param("PartitionValues") or []
        column_names = self._get_param("ColumnNames") or []
        result = self.glue_backend.get_column_statistics_for_partition(
            database_name, table_name, partition_values, column_names
        )
        return ActionResult(result)

    # --- Column Statistics Task Runs ---

    def get_column_statistics_task_run(self) -> ActionResult:
        run_id = self._get_param("ColumnStatisticsTaskRunId")
        run = self.glue_backend.get_column_statistics_task_run(run_id)
        return ActionResult({"ColumnStatisticsTaskRun": run})

    def get_column_statistics_task_runs(self) -> ActionResult:
        database_name = self._get_param("DatabaseName")
        table_name = self._get_param("TableName")
        runs = self.glue_backend.get_column_statistics_task_runs(
            database_name, table_name
        )
        return ActionResult(
            {
                "ColumnStatisticsTaskRuns": runs,
                "NextToken": None,
            }
        )

    # --- Crawler Metrics ---

    def get_crawler_metrics(self) -> ActionResult:
        crawler_names = self._get_param("CrawlerNameList")
        metrics = self.glue_backend.get_crawler_metrics(crawler_names)
        return ActionResult(
            {
                "CrawlerMetricsList": metrics,
                "NextToken": None,
            }
        )

    # --- Data Quality Results / Runs ---

    def get_data_quality_result(self) -> ActionResult:
        result_id = self._get_param("ResultId")
        self.glue_backend.get_data_quality_result(result_id)
        return EmptyResult()  # never reached

    def get_data_quality_rule_recommendation_run(self) -> ActionResult:
        run_id = self._get_param("RunId")
        run = self.glue_backend.get_data_quality_rule_recommendation_run(run_id)
        return ActionResult(run)

    def get_data_quality_ruleset_evaluation_run(self) -> ActionResult:
        run_id = self._get_param("RunId")
        run = self.glue_backend.get_data_quality_ruleset_evaluation_run(run_id)
        return ActionResult(run)

    # --- Blueprint Runs ---

    def get_blueprint_run(self) -> ActionResult:
        blueprint_name = self._get_param("BlueprintName")
        run_id = self._get_param("RunId")
        run = self.glue_backend.get_blueprint_run(blueprint_name, run_id)
        return ActionResult({"BlueprintRun": run})

    def get_blueprint_runs(self) -> ActionResult:
        blueprint_name = self._get_param("BlueprintName")
        runs = self.glue_backend.get_blueprint_runs(blueprint_name)
        return ActionResult(
            {
                "BlueprintRuns": runs,
                "NextToken": None,
            }
        )

    # --- ML Task Runs ---

    def get_ml_task_run(self) -> ActionResult:
        transform_id = self._get_param("TransformId")
        task_run_id = self._get_param("TaskRunId")
        self.glue_backend.get_ml_task_run(transform_id, task_run_id)
        return EmptyResult()  # never reached

    def get_ml_task_runs(self) -> ActionResult:
        transform_id = self._get_param("TransformId")
        runs = self.glue_backend.get_ml_task_runs(transform_id)
        return ActionResult(
            {
                "TaskRuns": runs,
                "NextToken": None,
            }
        )

    # --- GetMapping ---

    def get_mapping(self) -> ActionResult:
        source = self._get_param("Source")
        mapping = self.glue_backend.get_mapping(source)
        return ActionResult({"Mapping": mapping})

    # --- GetEntityRecords ---

    def get_entity_records(self) -> ActionResult:
        entity_name = self._get_param("EntityName")
        records = self.glue_backend.get_entity_records(entity_name)
        return ActionResult({"Records": records})

    # --- GetStatement ---

    def get_statement(self) -> ActionResult:
        session_id = self._get_param("SessionId")
        statement_id = self._get_int_param("Id")
        statement = self.glue_backend.get_statement(session_id, statement_id)
        return ActionResult({"Statement": statement})

    # --- Usage Profiles ---

    def create_usage_profile(self) -> ActionResult:
        name = self._get_param("Name")
        description = self._get_param("Description")
        configuration = self._get_param("Configuration")
        tags = self._get_param("Tags")
        profile = self.glue_backend.create_usage_profile(
            name, description, configuration, tags
        )
        return ActionResult({"Name": profile.name})

    def get_usage_profile(self) -> ActionResult:
        name = self._get_param("Name")
        profile = self.glue_backend.get_usage_profile(name)
        return ActionResult(profile.as_dict())

    def update_usage_profile(self) -> ActionResult:
        name = self._get_param("Name")
        description = self._get_param("Description")
        configuration = self._get_param("Configuration")
        self.glue_backend.update_usage_profile(name, description, configuration)
        return EmptyResult()

    def delete_usage_profile(self) -> ActionResult:
        name = self._get_param("Name")
        self.glue_backend.delete_usage_profile(name)
        return EmptyResult()

    def list_usage_profiles(self) -> ActionResult:
        next_token = self._get_param("NextToken")
        max_results = self._get_int_param("MaxResults")
        profiles, next_token = self.glue_backend.list_usage_profiles(
            next_token=next_token, max_results=max_results
        )
        return ActionResult(
            {
                "Profiles": [p.as_dict() for p in profiles],
                "NextToken": next_token,
            }
        )

    def list_schemas(self) -> ActionResult:
        registry_id = self.parameters.get("RegistryId")
        schemas = self.glue_backend.list_schemas(registry_id=registry_id)
        return ActionResult({"Schemas": schemas})

    def list_schema_versions(self) -> ActionResult:
        schema_id = self.parameters.get("SchemaId")
        versions = self.glue_backend.list_schema_versions(schema_id=schema_id)
        return ActionResult({"Schemas": versions})

    def list_dev_endpoints(self) -> ActionResult:
        dev_endpoints = self.glue_backend.list_dev_endpoints()
        return ActionResult(
            {
                "DevEndpointNames": [ep.endpoint_name for ep in dev_endpoints],
            }
        )

    def list_ml_transforms(self) -> ActionResult:
        next_token = self._get_param("NextToken")
        max_results = self._get_int_param("MaxResults")
        transforms, next_token = self.glue_backend.list_ml_transforms(
            next_token=next_token, max_results=max_results
        )
        return ActionResult(
            {
                "TransformIds": [t.transform_id for t in transforms],
                "NextToken": next_token,
            }
        )

    def search_tables(self) -> ActionResult:
        catalog_id = self.parameters.get("CatalogId")
        search_text = self.parameters.get("SearchText")
        filters = self.parameters.get("Filters")
        max_results = self.parameters.get("MaxResults")
        next_token = self.parameters.get("NextToken")
        tables, new_token = self.glue_backend.search_tables(
            catalog_id=catalog_id,
            search_text=search_text,
            filters=filters,
            max_results=max_results,
            next_token=next_token,
        )
        return ActionResult(
            {
                "TableList": [table.as_dict() for table in tables],
                "NextToken": new_token,
            }
        )

    def list_statements(self) -> ActionResult:
        session_id = self.parameters.get("SessionId")
        statements = self.glue_backend.list_statements(session_id=session_id)
        return ActionResult({"Statements": statements})

    def list_custom_entity_types(self) -> ActionResult:
        result = self.glue_backend.list_custom_entity_types(
            max_results=self.parameters.get("MaxResults"),
            next_token=self.parameters.get("NextToken"),
        )
        return ActionResult(result)

    def list_column_statistics_task_runs(self) -> ActionResult:
        result = self.glue_backend.list_column_statistics_task_runs(
            max_results=self.parameters.get("MaxResults"),
            next_token=self.parameters.get("NextToken"),
        )
        return ActionResult(result)

    def list_data_quality_results(self) -> ActionResult:
        result = self.glue_backend.list_data_quality_results(
            max_results=self.parameters.get("MaxResults"),
            next_token=self.parameters.get("NextToken"),
        )
        return ActionResult(result)

    def list_data_quality_rule_recommendation_runs(self) -> ActionResult:
        result = self.glue_backend.list_data_quality_rule_recommendation_runs(
            max_results=self.parameters.get("MaxResults"),
            next_token=self.parameters.get("NextToken"),
        )
        return ActionResult(result)

    def list_data_quality_ruleset_evaluation_runs(self) -> ActionResult:
        result = self.glue_backend.list_data_quality_ruleset_evaluation_runs(
            max_results=self.parameters.get("MaxResults"),
            next_token=self.parameters.get("NextToken"),
        )
        return ActionResult(result)

    def create_custom_entity_type(self) -> ActionResult:
        entity = self.glue_backend.create_custom_entity_type(
            name=self.parameters["Name"],
            regex_string=self.parameters["RegexString"],
            context_words=self.parameters.get("ContextWords"),
            tags=self.parameters.get("Tags"),
        )
        return ActionResult({"Name": entity.name})

    def get_custom_entity_type(self) -> ActionResult:
        name = self.parameters["Name"]
        entity = self.glue_backend.get_custom_entity_type(name)
        return ActionResult(entity.as_dict())

    def delete_custom_entity_type(self) -> ActionResult:
        name = self.parameters["Name"]
        deleted_name = self.glue_backend.delete_custom_entity_type(name)
        return ActionResult({"Name": deleted_name})

    def get_data_quality_model(self) -> ActionResult:
        self.glue_backend.get_data_quality_model(
            profile_id=self.parameters["ProfileId"],
            statistic_id=self.parameters.get("StatisticId"),
        )
        return EmptyResult()

    def delete_column_statistics_for_table(self) -> ActionResult:
        self.glue_backend.delete_column_statistics_for_table(
            database_name=self.parameters["DatabaseName"],
            table_name=self.parameters["TableName"],
            column_name=self.parameters["ColumnName"],
        )
        return EmptyResult()

    def delete_column_statistics_for_partition(self) -> ActionResult:
        self.glue_backend.delete_column_statistics_for_partition(
            database_name=self.parameters["DatabaseName"],
            table_name=self.parameters["TableName"],
            partition_values=self.parameters["PartitionValues"],
            column_name=self.parameters["ColumnName"],
        )
        return EmptyResult()

    def update_dev_endpoint(self) -> ActionResult:
        self.glue_backend.update_dev_endpoint(
            endpoint_name=self.parameters["EndpointName"],
            public_key=self.parameters.get("PublicKey"),
            custom_libraries=self.parameters.get("CustomLibraries"),
            update_etl_libraries=self.parameters.get("UpdateEtlLibraries", False),
            add_public_keys=self.parameters.get("AddPublicKeys"),
            delete_public_keys=self.parameters.get("DeletePublicKeys"),
            add_arguments=self.parameters.get("AddArguments"),
            delete_arguments=self.parameters.get("DeleteArguments"),
        )
        return EmptyResult()

    def get_catalogs(self) -> ActionResult:
        catalogs = self.glue_backend.get_catalogs()
        return ActionResult({"CatalogList": [c.as_dict() for c in catalogs]})

    def update_crawler(self) -> ActionResult:
        self.glue_backend.update_crawler(
            name=self.parameters["Name"],
            role=self.parameters.get("Role"),
            database_name=self.parameters.get("DatabaseName"),
            description=self.parameters.get("Description"),
            targets=self.parameters.get("Targets"),
            schedule=self.parameters.get("Schedule"),
            classifiers=self.parameters.get("Classifiers"),
            table_prefix=self.parameters.get("TablePrefix"),
            schema_change_policy=self.parameters.get("SchemaChangePolicy"),
            recrawl_policy=self.parameters.get("RecrawlPolicy"),
            lineage_configuration=self.parameters.get("LineageConfiguration"),
            configuration=self.parameters.get("Configuration"),
            crawler_security_configuration=self.parameters.get(
                "CrawlerSecurityConfiguration"
            ),
        )
        return EmptyResult()

    def update_crawler_schedule(self) -> ActionResult:
        self.glue_backend.update_crawler_schedule(
            crawler_name=self.parameters["CrawlerName"],
            schedule=self.parameters.get("Schedule"),
        )
        return EmptyResult()

    def start_crawler_schedule(self) -> ActionResult:
        self.glue_backend.start_crawler_schedule(
            crawler_name=self.parameters["CrawlerName"],
        )
        return EmptyResult()

    def stop_crawler_schedule(self) -> ActionResult:
        self.glue_backend.stop_crawler_schedule(
            crawler_name=self.parameters["CrawlerName"],
        )
        return EmptyResult()

    def update_job(self) -> ActionResult:
        name = self.glue_backend.update_job(
            name=self.parameters["JobName"],
            job_update=self.parameters["JobUpdate"],
        )
        return ActionResult({"JobName": name})

    def batch_stop_job_run(self) -> ActionResult:
        successful, errors = self.glue_backend.batch_stop_job_run(
            job_name=self.parameters["JobName"],
            job_run_ids=self.parameters["JobRunIds"],
        )
        return ActionResult({"SuccessfulSubmissions": successful, "Errors": errors})

    def get_job_bookmark(self) -> ActionResult:
        result = self.glue_backend.get_job_bookmark(
            job_name=self.parameters["JobName"],
            run_id=self.parameters.get("RunId"),
        )
        return ActionResult(result)

    def reset_job_bookmark(self) -> ActionResult:
        result = self.glue_backend.reset_job_bookmark(
            job_name=self.parameters["JobName"],
        )
        return ActionResult(result)

    def update_trigger(self) -> ActionResult:
        trigger = self.glue_backend.update_trigger(
            name=self.parameters["Name"],
            trigger_update=self.parameters["TriggerUpdate"],
        )
        return ActionResult({"Trigger": trigger.as_dict()})

    def update_connection(self) -> ActionResult:
        self.glue_backend.update_connection(
            catalog_id=self.parameters.get("CatalogId", ""),
            name=self.parameters["Name"],
            connection_input=self.parameters["ConnectionInput"],
        )
        return EmptyResult()

    def delete_connection(self) -> ActionResult:
        self.glue_backend.delete_connection(
            catalog_id=self.parameters.get("CatalogId", ""),
            name=self.parameters["ConnectionName"],
        )
        return EmptyResult()

    def batch_delete_connection(self) -> ActionResult:
        succeeded, errors = self.glue_backend.batch_delete_connection(
            catalog_id=self.parameters.get("CatalogId", ""),
            connection_names=self.parameters["ConnectionNameList"],
        )
        return ActionResult({"Succeeded": succeeded, "Errors": errors})

    def batch_get_dev_endpoints(self) -> ActionResult:
        endpoints, not_found = self.glue_backend.batch_get_dev_endpoints(
            endpoint_names=self.parameters["DevEndpointNames"],
        )
        result: dict[str, Any] = {"DevEndpoints": endpoints}
        if not_found:
            result["DevEndpointsNotFound"] = not_found
        return ActionResult(result)

    def update_registry(self) -> ActionResult:
        result = self.glue_backend.update_registry(
            registry_id=self.parameters["RegistryId"],
            description=self.parameters["Description"],
        )
        return ActionResult(result)

    def batch_get_blueprints(self) -> ActionResult:
        blueprints, missing = self.glue_backend.batch_get_blueprints(
            names=self.parameters["Names"],
        )
        result: dict[str, Any] = {"Blueprints": blueprints}
        if missing:
            result["MissingBlueprints"] = missing
        return ActionResult(result)

    def batch_get_custom_entity_types(self) -> ActionResult:
        entities, missing = self.glue_backend.batch_get_custom_entity_types(
            names=self.parameters["Names"],
        )
        result: dict[str, Any] = {"CustomEntityTypes": entities}
        if missing:
            result["CustomEntityTypesNotFound"] = missing
        return ActionResult(result)

    def resume_workflow_run(self) -> ActionResult:
        result = self.glue_backend.resume_workflow_run(
            name=self.parameters["Name"],
            run_id=self.parameters["RunId"],
            node_ids=self.parameters["NodeIds"],
        )
        return ActionResult(result)

    def run_statement(self) -> ActionResult:
        result = self.glue_backend.run_statement(
            session_id=self.parameters["SessionId"],
            code=self.parameters["Code"],
            request_origin=self.parameters.get("RequestOrigin"),
        )
        return ActionResult(result)

    def cancel_statement(self) -> ActionResult:
        self.glue_backend.cancel_statement(
            session_id=self.parameters["SessionId"],
            statement_id=self.parameters["Id"],
            request_origin=self.parameters.get("RequestOrigin"),
        )
        return EmptyResult()

    def import_catalog_to_glue(self) -> ActionResult:
        self.glue_backend.import_catalog_to_glue(
            catalog_id=self.parameters.get("CatalogId"),
        )
        return EmptyResult()

    def batch_delete_table_version(self) -> ActionResult:
        errors = self.glue_backend.batch_delete_table_version(
            database_name=self.parameters["DatabaseName"],
            table_name=self.parameters["TableName"],
            version_ids=self.parameters["VersionIds"],
        )
        return ActionResult({"Errors": errors})

    def create_partition_index(self) -> ActionResult:
        self.glue_backend.create_partition_index(
            database_name=self.parameters["DatabaseName"],
            table_name=self.parameters["TableName"],
            partition_index=self.parameters["PartitionIndex"],
        )
        return EmptyResult()

    def delete_partition_index(self) -> ActionResult:
        self.glue_backend.delete_partition_index(
            database_name=self.parameters["DatabaseName"],
            table_name=self.parameters["TableName"],
            index_name=self.parameters["IndexName"],
        )
        return EmptyResult()

    def create_user_defined_function(self) -> ActionResult:
        self.glue_backend.create_user_defined_function(
            database_name=self.parameters["DatabaseName"],
            function_input=self.parameters["FunctionInput"],
        )
        return EmptyResult()

    def get_user_defined_function(self) -> ActionResult:
        udf = self.glue_backend.get_user_defined_function(
            database_name=self.parameters["DatabaseName"],
            function_name=self.parameters["FunctionName"],
        )
        return ActionResult({"UserDefinedFunction": udf})

    def get_user_defined_functions(self) -> ActionResult:
        udfs = self.glue_backend.get_user_defined_functions(
            database_name=self.parameters["DatabaseName"],
            pattern=self.parameters.get("Pattern", "*"),
        )
        return ActionResult({"UserDefinedFunctions": udfs})

    def update_user_defined_function(self) -> ActionResult:
        self.glue_backend.update_user_defined_function(
            database_name=self.parameters["DatabaseName"],
            function_name=self.parameters["FunctionName"],
            function_input=self.parameters["FunctionInput"],
        )
        return EmptyResult()

    def delete_user_defined_function(self) -> ActionResult:
        self.glue_backend.delete_user_defined_function(
            database_name=self.parameters["DatabaseName"],
            function_name=self.parameters["FunctionName"],
        )
        return EmptyResult()

    def check_schema_version_validity(self) -> ActionResult:
        result = self.glue_backend.check_schema_version_validity(
            data_format=self.parameters["DataFormat"],
            schema_definition=self.parameters["SchemaDefinition"],
        )
        return ActionResult(result)

    def delete_schema_versions(self) -> ActionResult:
        results = self.glue_backend.delete_schema_versions(
            schema_id=self.parameters["SchemaId"],
            versions=self.parameters["Versions"],
        )
        return ActionResult({"SchemaVersionErrors": results})

    def start_blueprint_run(self) -> ActionResult:
        run_id = self.glue_backend.start_blueprint_run(
            name=self.parameters["BlueprintName"],
            role_arn=self.parameters["RoleArn"],
            parameters=self.parameters.get("Parameters"),
        )
        return ActionResult({"RunId": run_id})

    # --- Column Statistics Update ---

    def update_column_statistics_for_table(self) -> ActionResult:
        result = self.glue_backend.update_column_statistics_for_table(
            database_name=self.parameters["DatabaseName"],
            table_name=self.parameters["TableName"],
            column_statistics_list=self.parameters["ColumnStatisticsList"],
        )
        return ActionResult(result)

    def update_column_statistics_for_partition(self) -> ActionResult:
        result = self.glue_backend.update_column_statistics_for_partition(
            database_name=self.parameters["DatabaseName"],
            table_name=self.parameters["TableName"],
            partition_values=self.parameters["PartitionValues"],
            column_statistics_list=self.parameters["ColumnStatisticsList"],
        )
        return ActionResult(result)

    # --- Integration ---

    def create_integration(self) -> ActionResult:
        integration = self.glue_backend.create_integration(
            integration_name=self.parameters["IntegrationName"],
            source_arn=self.parameters["SourceArn"],
            target_arn=self.parameters["TargetArn"],
            description=self.parameters.get("Description"),
            kms_key_id=self.parameters.get("KmsKeyId"),
            additional_encryption_context=self.parameters.get(
                "AdditionalEncryptionContext"
            ),
            tags=self.parameters.get("Tags"),
        )
        return ActionResult(integration.as_dict())

    def delete_integration(self) -> ActionResult:
        result = self.glue_backend.delete_integration(
            integration_arn=self.parameters["IntegrationIdentifier"],
        )
        return ActionResult(result)

    def describe_integrations(self) -> ActionResult:
        integrations = self.glue_backend.describe_integrations(
            integration_identifier=self.parameters.get("IntegrationIdentifier"),
        )
        return ActionResult({"Integrations": [i.as_dict() for i in integrations]})

    def modify_integration(self) -> ActionResult:
        integration = self.glue_backend.modify_integration(
            integration_identifier=self.parameters["IntegrationIdentifier"],
            description=self.parameters.get("Description"),
        )
        return ActionResult(integration.as_dict())

    # --- Integration Resource Properties ---

    def create_integration_resource_property(self) -> ActionResult:
        result = self.glue_backend.create_integration_resource_property(
            resource_arn=self.parameters["ResourceArn"],
            source_processing_properties=self.parameters.get(
                "SourceProcessingProperties"
            ),
            target_processing_properties=self.parameters.get(
                "TargetProcessingProperties"
            ),
        )
        return ActionResult(result)

    def get_integration_resource_property(self) -> ActionResult:
        result = self.glue_backend.get_integration_resource_property(
            resource_arn=self.parameters["ResourceArn"],
        )
        return ActionResult(result)

    def update_integration_resource_property(self) -> ActionResult:
        result = self.glue_backend.update_integration_resource_property(
            resource_arn=self.parameters["ResourceArn"],
            source_processing_properties=self.parameters.get(
                "SourceProcessingProperties"
            ),
            target_processing_properties=self.parameters.get(
                "TargetProcessingProperties"
            ),
        )
        return ActionResult(result)

    def delete_integration_resource_property(self) -> ActionResult:
        self.glue_backend.delete_integration_resource_property(
            resource_arn=self.parameters["ResourceArn"],
        )
        return EmptyResult()

    def list_integration_resource_properties(self) -> ActionResult:
        results = self.glue_backend.list_integration_resource_properties(
            resource_arn=self.parameters.get("ResourceArn"),
        )
        return ActionResult({"IntegrationResourcePropertyList": results})

    # --- Integration Table Properties ---

    def create_integration_table_properties(self) -> ActionResult:
        result = self.glue_backend.create_integration_table_properties(
            resource_arn=self.parameters["ResourceArn"],
            table_name=self.parameters["TableName"],
            source_table_config=self.parameters.get("SourceTableConfig"),
            target_table_config=self.parameters.get("TargetTableConfig"),
        )
        return ActionResult(result)

    def get_integration_table_properties(self) -> ActionResult:
        result = self.glue_backend.get_integration_table_properties(
            resource_arn=self.parameters["ResourceArn"],
            table_name=self.parameters["TableName"],
        )
        return ActionResult(result)

    def update_integration_table_properties(self) -> ActionResult:
        result = self.glue_backend.update_integration_table_properties(
            resource_arn=self.parameters["ResourceArn"],
            table_name=self.parameters["TableName"],
            source_table_config=self.parameters.get("SourceTableConfig"),
            target_table_config=self.parameters.get("TargetTableConfig"),
        )
        return ActionResult(result)

    def delete_integration_table_properties(self) -> ActionResult:
        self.glue_backend.delete_integration_table_properties(
            resource_arn=self.parameters["ResourceArn"],
            table_name=self.parameters["TableName"],
        )
        return EmptyResult()

    def describe_inbound_integrations(self) -> ActionResult:
        results = self.glue_backend.describe_inbound_integrations(
            integration_arn=self.parameters.get("IntegrationArn"),
            target_arn=self.parameters.get("TargetArn"),
        )
        return ActionResult({"InboundIntegrations": results})

    # --- Column Statistics Task Settings ---

    def create_column_statistics_task_settings(self) -> ActionResult:
        self.glue_backend.create_column_statistics_task_settings(
            database_name=self.parameters["DatabaseName"],
            table_name=self.parameters["TableName"],
            role=self.parameters["Role"],
            schedule=self.parameters.get("Schedule"),
            column_name_list=self.parameters.get("ColumnNameList"),
            sample_size=self.parameters.get("SampleSize", 0.0),
            catalog_id=self.parameters.get("CatalogID"),
            security_configuration=self.parameters.get("SecurityConfiguration"),
        )
        return EmptyResult()

    def get_column_statistics_task_settings(self) -> ActionResult:
        result = self.glue_backend.get_column_statistics_task_settings(
            database_name=self.parameters["DatabaseName"],
            table_name=self.parameters["TableName"],
        )
        return ActionResult({"ColumnStatisticsTaskSettings": result})

    def update_column_statistics_task_settings(self) -> ActionResult:
        self.glue_backend.update_column_statistics_task_settings(
            database_name=self.parameters["DatabaseName"],
            table_name=self.parameters["TableName"],
            role=self.parameters.get("Role"),
            schedule=self.parameters.get("Schedule"),
            column_name_list=self.parameters.get("ColumnNameList"),
            sample_size=self.parameters.get("SampleSize"),
            security_configuration=self.parameters.get("SecurityConfiguration"),
        )
        return EmptyResult()

    def delete_column_statistics_task_settings(self) -> ActionResult:
        self.glue_backend.delete_column_statistics_task_settings(
            database_name=self.parameters["DatabaseName"],
            table_name=self.parameters["TableName"],
        )
        return EmptyResult()

    def start_column_statistics_task_run(self) -> ActionResult:
        run_id = self.glue_backend.start_column_statistics_task_run(
            database_name=self.parameters["DatabaseName"],
            table_name=self.parameters["TableName"],
        )
        return ActionResult({"ColumnStatisticsTaskRunId": run_id})

    def stop_column_statistics_task_run(self) -> ActionResult:
        self.glue_backend.stop_column_statistics_task_run(
            database_name=self.parameters["DatabaseName"],
            table_name=self.parameters["TableName"],
        )
        return EmptyResult()

    def start_column_statistics_task_run_schedule(self) -> ActionResult:
        self.glue_backend.start_column_statistics_task_run_schedule(
            database_name=self.parameters["DatabaseName"],
            table_name=self.parameters["TableName"],
        )
        return EmptyResult()

    def stop_column_statistics_task_run_schedule(self) -> ActionResult:
        self.glue_backend.stop_column_statistics_task_run_schedule(
            database_name=self.parameters["DatabaseName"],
            table_name=self.parameters["TableName"],
        )
        return EmptyResult()

    # --- Data Quality Runs ---

    def start_data_quality_rule_recommendation_run(self) -> ActionResult:
        run_id = self.glue_backend.start_data_quality_rule_recommendation_run(
            data_source=self.parameters["DataSource"],
            role=self.parameters["Role"],
            number_of_workers=self.parameters.get("NumberOfWorkers"),
            timeout=self.parameters.get("Timeout"),
            created_ruleset_name=self.parameters.get("CreatedRulesetName"),
        )
        return ActionResult({"RunId": run_id})

    def start_data_quality_ruleset_evaluation_run(self) -> ActionResult:
        run_id = self.glue_backend.start_data_quality_ruleset_evaluation_run(
            data_source=self.parameters["DataSource"],
            role=self.parameters["Role"],
            ruleset_names=self.parameters["RulesetNames"],
            number_of_workers=self.parameters.get("NumberOfWorkers"),
            timeout=self.parameters.get("Timeout"),
            additional_data_sources=self.parameters.get("AdditionalDataSources"),
        )
        return ActionResult({"RunId": run_id})

    def cancel_data_quality_rule_recommendation_run(self) -> ActionResult:
        self.glue_backend.cancel_data_quality_rule_recommendation_run(
            run_id=self.parameters["RunId"],
        )
        return EmptyResult()

    def cancel_data_quality_ruleset_evaluation_run(self) -> ActionResult:
        self.glue_backend.cancel_data_quality_ruleset_evaluation_run(
            run_id=self.parameters["RunId"],
        )
        return EmptyResult()

    # --- Data Quality Extras ---

    def batch_get_data_quality_result(self) -> ActionResult:
        result = self.glue_backend.batch_get_data_quality_result(
            result_ids=self.parameters["ResultIds"],
        )
        return ActionResult(result)

    def get_data_quality_model_result(self) -> ActionResult:
        self.glue_backend.get_data_quality_model_result(
            profile_id=self.parameters["ProfileId"],
            statistic_id=self.parameters.get("StatisticId"),
        )
        return EmptyResult()

    def list_data_quality_statistics(self) -> ActionResult:
        results = self.glue_backend.list_data_quality_statistics(
            statistic_id=self.parameters.get("StatisticId"),
            profile_id=self.parameters.get("ProfileId"),
        )
        return ActionResult({"Statistics": results})

    def list_data_quality_statistic_annotations(self) -> ActionResult:
        results = self.glue_backend.list_data_quality_statistic_annotations(
            statistic_id=self.parameters.get("StatisticId"),
            profile_id=self.parameters.get("ProfileId"),
        )
        return ActionResult({"Annotations": results})

    def batch_put_data_quality_statistic_annotation(self) -> ActionResult:
        result = self.glue_backend.batch_put_data_quality_statistic_annotation(
            inclusion_annotations=self.parameters["InclusionAnnotations"],
        )
        return ActionResult(result)

    def put_data_quality_profile_annotation(self) -> ActionResult:
        self.glue_backend.put_data_quality_profile_annotation(
            profile_id=self.parameters["ProfileId"],
            inclusion_annotation=self.parameters["InclusionAnnotation"],
        )
        return EmptyResult()

    def create_table_optimizer(self) -> ActionResult:
        self.glue_backend.create_table_optimizer(
            catalog_id=self.parameters.get("CatalogId", ""),
            database_name=self.parameters.get("DatabaseName", ""),
            table_name=self.parameters.get("TableName", ""),
            type_=self.parameters.get("Type", ""),
            configuration=self.parameters.get("TableOptimizerConfiguration", {}),
        )
        return EmptyResult()

    def get_table_optimizer(self) -> ActionResult:
        optimizer = self.glue_backend.get_table_optimizer(
            catalog_id=self.parameters.get("CatalogId", ""),
            database_name=self.parameters.get("DatabaseName", ""),
            table_name=self.parameters.get("TableName", ""),
            type_=self.parameters.get("Type", ""),
        )
        return ActionResult(
            {
                "CatalogId": self.parameters.get("CatalogId", ""),
                "DatabaseName": self.parameters.get("DatabaseName", ""),
                "TableName": self.parameters.get("TableName", ""),
                "TableOptimizer": optimizer.as_dict(),
            }
        )

    def update_table_optimizer(self) -> ActionResult:
        self.glue_backend.update_table_optimizer(
            catalog_id=self.parameters.get("CatalogId", ""),
            database_name=self.parameters.get("DatabaseName", ""),
            table_name=self.parameters.get("TableName", ""),
            type_=self.parameters.get("Type", ""),
            configuration=self.parameters.get("TableOptimizerConfiguration", {}),
        )
        return EmptyResult()

    def delete_table_optimizer(self) -> ActionResult:
        self.glue_backend.delete_table_optimizer(
            catalog_id=self.parameters.get("CatalogId", ""),
            database_name=self.parameters.get("DatabaseName", ""),
            table_name=self.parameters.get("TableName", ""),
            type_=self.parameters.get("Type", ""),
        )
        return EmptyResult()

    def batch_get_table_optimizer(self) -> ActionResult:
        entries = self.parameters.get("Entries", [])
        results = self.glue_backend.batch_get_table_optimizer(entries=entries)
        return ActionResult({"TableOptimizers": results, "Failures": []})

    def list_table_optimizer_runs(self) -> ActionResult:
        runs = self.glue_backend.list_table_optimizer_runs(
            catalog_id=self.parameters.get("CatalogId", ""),
            database_name=self.parameters.get("DatabaseName", ""),
            table_name=self.parameters.get("TableName", ""),
            type_=self.parameters.get("Type", ""),
        )
        return ActionResult({"TableOptimizerRuns": runs})

    # --- Connection Types ---

    def register_connection_type(self) -> ActionResult:
        params = self.parameters
        connection_type = params.get("ConnectionType")
        integration_type = params.get("IntegrationType", "CUSTOM")
        connection_properties = params.get("ConnectionProperties") or {}
        connector_auth = params.get("ConnectorAuthenticationConfiguration") or {}
        rest_config = params.get("RestConfiguration") or {}
        description = params.get("Description")
        capabilities = params.get("Capabilities")
        ct = self.glue_backend.create_connection_type(
            connection_type=connection_type,
            integration_type=integration_type,
            connection_properties=connection_properties,
            connector_authentication_configuration=connector_auth,
            rest_configuration=rest_config,
            description=description,
            capabilities=capabilities,
        )
        return ActionResult({"ConnectionTypeArn": ct.arn})

    def describe_connection_type(self) -> ActionResult:
        connection_type = self.parameters.get("ConnectionType")
        ct = self.glue_backend.get_connection_type(connection_type)
        return ActionResult(ct.as_dict())

    def list_connection_types(self) -> ActionResult:
        types_list = self.glue_backend.list_connection_types()
        return ActionResult({"ConnectionTypes": [ct.as_dict() for ct in types_list]})

    def delete_connection_type(self) -> EmptyResult:
        connection_type = self.parameters.get("ConnectionType")
        self.glue_backend.delete_connection_type(connection_type)
        return EmptyResult()

    # --- Glue Identity Center Configuration ---

    def create_glue_identity_center_configuration(self) -> ActionResult:
        instance_arn = self.parameters.get("InstanceArn")
        application_arn = self.parameters.get("ApplicationArn")
        scopes = self.parameters.get("Scopes") or []
        user_background_sessions_enabled = self.parameters.get(
            "UserBackgroundSessionsEnabled", False
        )
        config = self.glue_backend.create_glue_identity_center_configuration(
            instance_arn=instance_arn,
            application_arn=application_arn,
            scopes=scopes,
            user_background_sessions_enabled=user_background_sessions_enabled,
        )
        return ActionResult({"ApplicationArn": config.application_arn})

    def get_glue_identity_center_configuration(self) -> ActionResult:
        config = self.glue_backend.get_glue_identity_center_configuration()
        return ActionResult(config.as_dict())

    def update_glue_identity_center_configuration(self) -> EmptyResult:
        instance_arn = self.parameters.get("InstanceArn")
        application_arn = self.parameters.get("ApplicationArn")
        scopes = self.parameters.get("Scopes")
        user_background_sessions_enabled = self.parameters.get(
            "UserBackgroundSessionsEnabled"
        )
        self.glue_backend.update_glue_identity_center_configuration(
            instance_arn=instance_arn,
            application_arn=application_arn,
            scopes=scopes,
            user_background_sessions_enabled=user_background_sessions_enabled,
        )
        return EmptyResult()

    def delete_glue_identity_center_configuration(self) -> EmptyResult:
        self.glue_backend.delete_glue_identity_center_configuration()
        return EmptyResult()

    # --- Materialized View Refresh Task Runs ---

    def start_materialized_view_refresh_task_run(self) -> ActionResult:
        catalog_id = self.parameters.get("CatalogId")
        database_name = self.parameters.get("DatabaseName")
        table_name = self.parameters.get("TableName")
        task = self.glue_backend.start_materialized_view_refresh_task_run(
            catalog_id=catalog_id or "",
            database_name=database_name,
            table_name=table_name,
        )
        return ActionResult({"MaterializedViewRefreshTaskRunId": task.task_run_id})

    def get_materialized_view_refresh_task_run(self) -> ActionResult:
        task_run_id = self.parameters.get("MaterializedViewRefreshTaskRunId")
        task = self.glue_backend.get_materialized_view_refresh_task_run(task_run_id)
        return ActionResult({"MaterializedViewRefreshTaskRun": task.as_dict()})

    def list_materialized_view_refresh_task_runs(self) -> ActionResult:
        catalog_id = self.parameters.get("CatalogId")
        database_name = self.parameters.get("DatabaseName")
        table_name = self.parameters.get("TableName")
        task_run_id = self.parameters.get("MaterializedViewRefreshTaskRunId")
        tasks = self.glue_backend.list_materialized_view_refresh_task_runs(
            catalog_id=catalog_id,
            database_name=database_name,
            table_name=table_name,
            task_run_id=task_run_id,
        )
        return ActionResult(
            {"MaterializedViewRefreshTaskRuns": [t.as_dict() for t in tasks]}
        )

    def stop_materialized_view_refresh_task_run(self) -> EmptyResult:
        database_name = self.parameters.get("DatabaseName")
        table_name = self.parameters.get("TableName")
        self.glue_backend.stop_materialized_view_refresh_task_run_by_table(
            database_name, table_name
        )
        return EmptyResult()

    # --- ML Task Run operations ---

    def cancel_ml_task_run(self) -> str:
        transform_id = self.parameters.get("TransformId")
        task_run_id = self.parameters.get("TaskRunId")
        result = self.glue_backend.cancel_ml_task_run(transform_id, task_run_id)
        return json.dumps(result)

    def start_ml_evaluation_task_run(self) -> str:
        transform_id = self.parameters.get("TransformId")
        task_run_id = self.glue_backend.start_ml_evaluation_task_run(transform_id)
        return json.dumps({"TaskRunId": task_run_id})

    def start_ml_labeling_set_generation_task_run(self) -> str:
        transform_id = self.parameters.get("TransformId")
        output_s3_path = self.parameters.get("OutputS3Path")
        task_run_id = self.glue_backend.start_ml_labeling_set_generation_task_run(
            transform_id, output_s3_path
        )
        return json.dumps({"TaskRunId": task_run_id})

    def start_export_labels_task_run(self) -> str:
        transform_id = self.parameters.get("TransformId")
        output_s3_path = self.parameters.get("OutputS3Path")
        task_run_id = self.glue_backend.start_export_labels_task_run(
            transform_id, output_s3_path
        )
        return json.dumps({"TaskRunId": task_run_id})

    def start_import_labels_task_run(self) -> str:
        transform_id = self.parameters.get("TransformId")
        input_s3_path = self.parameters.get("InputS3Path")
        replace_all_labels = self.parameters.get("ReplaceAllLabels", False)
        task_run_id = self.glue_backend.start_import_labels_task_run(
            transform_id, input_s3_path, replace_all_labels
        )
        return json.dumps({"TaskRunId": task_run_id})

    # --- Schema operations ---

    def get_schema_versions_diff(self) -> str:
        schema_id = self.parameters.get("SchemaId")
        first_version = self.parameters.get("FirstSchemaVersionNumber")
        second_version = self.parameters.get("SecondSchemaVersionNumber")
        schema_diff_type = self.parameters.get("SchemaDiffType")
        result = self.glue_backend.get_schema_versions_diff(
            schema_id, first_version, second_version, schema_diff_type
        )
        return json.dumps(result)

    def query_schema_version_metadata(self) -> str:
        schema_id = self.parameters.get("SchemaId")
        schema_version_number = self.parameters.get("SchemaVersionNumber")
        schema_version_id = self.parameters.get("SchemaVersionId")
        result = self.glue_backend.query_schema_version_metadata(
            schema_id, schema_version_number, schema_version_id
        )
        return json.dumps(result)

    def remove_schema_version_metadata(self) -> str:
        schema_id = self.parameters.get("SchemaId")
        schema_version_number = self.parameters.get("SchemaVersionNumber")
        schema_version_id = self.parameters.get("SchemaVersionId")
        metadata_key_value = self.parameters.get("MetadataKeyValue")
        result = self.glue_backend.remove_schema_version_metadata(
            schema_id, schema_version_number, schema_version_id, metadata_key_value
        )
        return json.dumps(result)

    # --- Entity operations ---

    def describe_entity(self) -> str:
        connection_name = self.parameters.get("ConnectionName")
        entity_name = self.parameters.get("EntityName")
        result = self.glue_backend.describe_entity(connection_name, entity_name)
        return json.dumps(result)

    def list_entities(self) -> str:
        connection_name = self.parameters.get("ConnectionName")
        result = self.glue_backend.list_entities(connection_name)
        return json.dumps(result)

    # --- Stub operations ---

    def create_script(self) -> str:
        result = self.glue_backend.create_script(self.parameters)
        return json.dumps(result)

    def get_dataflow_graph(self) -> str:
        result = self.glue_backend.get_dataflow_graph(self.parameters)
        return json.dumps(result)

    def get_plan(self) -> str:
        result = self.glue_backend.get_plan(
            mapping=self.parameters.get("Mapping", []),
            source=self.parameters.get("Source", {}),
            sinks=self.parameters.get("Sinks"),
            location=self.parameters.get("Location"),
            language=self.parameters.get("Language", "PYTHON"),
        )
        return json.dumps(result)

    def get_unfiltered_table_metadata(self) -> str:
        result = self.glue_backend.get_unfiltered_table_metadata(
            catalog_id=self.parameters.get("CatalogId", ""),
            database_name=self.parameters.get("DatabaseName", ""),
            table_name=self.parameters.get("Name", ""),
            supported_permission_types=self.parameters.get("SupportedPermissionTypes", []),
        )
        return json.dumps(result)

    def get_unfiltered_partitions_metadata(self) -> str:
        result = self.glue_backend.get_unfiltered_partitions_metadata(
            catalog_id=self.parameters.get("CatalogId", ""),
            database_name=self.parameters.get("DatabaseName", ""),
            table_name=self.parameters.get("TableName", ""),
            supported_permission_types=self.parameters.get("SupportedPermissionTypes", []),
        )
        return json.dumps(result)

    def get_unfiltered_partition_metadata(self) -> str:
        result = self.glue_backend.get_unfiltered_partition_metadata(
            catalog_id=self.parameters.get("CatalogId", ""),
            database_name=self.parameters.get("DatabaseName", ""),
            table_name=self.parameters.get("TableName", ""),
            partition_values=self.parameters.get("PartitionValues", []),
            supported_permission_types=self.parameters.get("SupportedPermissionTypes", []),
        )
        return json.dumps(result)

    def test_connection(self) -> str:
        result = self.glue_backend.test_connection(
            connection_name=self.parameters.get("ConnectionName"),
            connection_type=self.parameters.get("ConnectionType"),
        )
        return json.dumps(result or {})

    def update_job_from_source_control(self) -> str:
        result = self.glue_backend.update_job_from_source_control(
            job_name=self.parameters.get("JobName"),
            provider=self.parameters.get("Provider"),
            repository_name=self.parameters.get("RepositoryName"),
            repository_owner=self.parameters.get("RepositoryOwner"),
            branch_name=self.parameters.get("BranchName"),
            folder=self.parameters.get("Folder"),
            commit_id=self.parameters.get("CommitId"),
            auth_strategy=self.parameters.get("AuthStrategy"),
            auth_token=self.parameters.get("AuthToken"),
        )
        return json.dumps(result)

    def update_source_control_from_job(self) -> str:
        result = self.glue_backend.update_source_control_from_job(
            job_name=self.parameters.get("JobName"),
            provider=self.parameters.get("Provider"),
            repository_name=self.parameters.get("RepositoryName"),
            repository_owner=self.parameters.get("RepositoryOwner"),
            branch_name=self.parameters.get("BranchName"),
            folder=self.parameters.get("Folder"),
            commit_id=self.parameters.get("CommitId"),
            auth_strategy=self.parameters.get("AuthStrategy"),
            auth_token=self.parameters.get("AuthToken"),
        )
        return json.dumps(result)
