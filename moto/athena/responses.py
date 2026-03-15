import json
from typing import Union

from moto.core.responses import BaseResponse

from .models import AthenaBackend, athena_backends


class AthenaResponse(BaseResponse):
    def __init__(self) -> None:
        super().__init__(service_name="athena")

    @property
    def athena_backend(self) -> AthenaBackend:
        return athena_backends[self.current_account][self.region]

    def create_work_group(self) -> Union[tuple[str, dict[str, int]], str]:
        name = self._get_param("Name")
        description = self._get_param("Description")
        configuration = self._get_param("Configuration", {})
        tags = self._get_param("Tags")
        work_group = self.athena_backend.create_work_group(
            name, configuration, description, tags
        )
        if not work_group:
            return self.error("WorkGroup already exists", 400)
        return json.dumps(
            {
                "CreateWorkGroupResponse": {
                    "ResponseMetadata": {
                        "RequestId": "384ac68d-3775-11df-8963-01868b7c937a"
                    }
                }
            }
        )

    def list_work_groups(self) -> str:
        return json.dumps({"WorkGroups": self.athena_backend.list_work_groups()})

    def get_work_group(self) -> str:
        name = self._get_param("WorkGroup")
        return json.dumps({"WorkGroup": self.athena_backend.get_work_group(name)})

    def update_work_group(self) -> Union[tuple[str, dict[str, int]], str]:
        name = self._get_param("WorkGroup")
        description = self._get_param("Description")
        configuration_updates = self._get_param("ConfigurationUpdates")
        state = self._get_param("State")
        result = self.athena_backend.update_work_group(
            name, description, configuration_updates, state
        )
        if not result:
            return self.error("WorkGroup does not exist", 400)
        return json.dumps({})

    def delete_work_group(self) -> str:
        name = self._get_param("WorkGroup")
        self.athena_backend.delete_work_group(name)
        return "{}"

    def start_query_execution(self) -> Union[tuple[str, dict[str, int]], str]:
        query = self._get_param("QueryString")
        context = self._get_param("QueryExecutionContext")
        config = self._get_param("ResultConfiguration")
        workgroup = self._get_param("WorkGroup")
        execution_parameters = self._get_param("ExecutionParameters")
        if workgroup and not self.athena_backend.get_work_group(workgroup):
            return self.error("WorkGroup does not exist", 400)
        q_exec_id = self.athena_backend.start_query_execution(
            query=query,
            context=context,
            config=config,
            workgroup=workgroup,
            execution_parameters=execution_parameters,
        )
        return json.dumps({"QueryExecutionId": q_exec_id})

    def get_query_execution(self) -> str:
        exec_id = self._get_param("QueryExecutionId")
        execution = self.athena_backend.get_query_execution(exec_id)
        ddl_commands = ("ALTER", "CREATE", "DESCRIBE", "DROP", "MSCK", "SHOW")
        statement_type = "DML"
        if execution.query.upper().startswith(ddl_commands):
            statement_type = "DDL"
        result = {
            "QueryExecution": {
                "QueryExecutionId": exec_id,
                "Query": execution.query,
                "StatementType": statement_type,
                "ResultConfiguration": execution.config,
                "ResultReuseConfiguration": {
                    "ResultReuseByAgeConfiguration": {"Enabled": False}
                },
                "QueryExecutionContext": execution.context,
                "Status": {
                    "State": execution.status,
                    "SubmissionDateTime": execution.start_time,
                    "CompletionDateTime": execution.end_time,
                },
                "Statistics": {
                    "EngineExecutionTimeInMillis": 0,
                    "DataScannedInBytes": 0,
                    "TotalExecutionTimeInMillis": 0,
                    "QueryQueueTimeInMillis": 0,
                    "ServicePreProcessingTimeInMillis": 0,
                    "QueryPlanningTimeInMillis": 0,
                    "ServiceProcessingTimeInMillis": 0,
                    "ResultReuseInformation": {"ReusedPreviousResult": False},
                },
                "WorkGroup": execution.workgroup.name if execution.workgroup else None,
            }
        }
        if execution.execution_parameters is not None:
            result["QueryExecution"]["ExecutionParameters"] = (
                execution.execution_parameters
            )
        return json.dumps(result)

    def create_capacity_reservation(self) -> Union[tuple[str, dict[str, int]], str]:
        name = self._get_param("Name")
        target_dpus = self._get_param("TargetDpus")
        tags = self._get_param("Tags")
        self.athena_backend.create_capacity_reservation(name, target_dpus, tags)
        return json.dumps({})

    def get_capacity_reservation(self) -> Union[str, tuple[str, dict[str, int]]]:
        name = self._get_param("Name")
        capacity_reservation = self.athena_backend.get_capacity_reservation(name)
        if not capacity_reservation:
            return self.error("Capacity reservation does not exist", 400)
        return json.dumps(
            {
                "CapacityReservation": {
                    "Name": capacity_reservation.name,
                    "TargetDpus": capacity_reservation.target_dpus,
                    "Tags": capacity_reservation.tags,
                }
            }
        )

    def list_capacity_reservations(self) -> str:
        capacity_reservations = self.athena_backend.list_capacity_reservations()
        return json.dumps({"CapacityReservations": capacity_reservations})

    def update_capacity_reservation(self) -> str:
        name = self._get_param("Name")
        target_dpus = self._get_param("TargetDpus")
        self.athena_backend.update_capacity_reservation(name, target_dpus)
        return "{}"

    def get_query_results(self) -> str:
        exec_id = self._get_param("QueryExecutionId")
        result = self.athena_backend.get_query_results(exec_id)
        return json.dumps(result.to_dict())

    def list_query_executions(self) -> str:
        workgroup = self._get_param("WorkGroup")
        executions = self.athena_backend.list_query_executions(workgroup)
        return json.dumps({"QueryExecutionIds": list(executions.keys())})

    def stop_query_execution(self) -> str:
        exec_id = self._get_param("QueryExecutionId")
        self.athena_backend.stop_query_execution(exec_id)
        return json.dumps({})

    def error(self, msg: str, status: int) -> tuple[str, dict[str, int]]:
        return (
            json.dumps({"__type": "InvalidRequestException", "Message": msg}),
            {"status": status},
        )

    def create_named_query(self) -> Union[tuple[str, dict[str, int]], str]:
        name = self._get_param("Name")
        description = self._get_param("Description")
        database = self._get_param("Database")
        query_string = self._get_param("QueryString")
        workgroup = self._get_param("WorkGroup") or "primary"
        if not self.athena_backend.get_work_group(workgroup):
            return self.error("WorkGroup does not exist", 400)
        query_id = self.athena_backend.create_named_query(
            name, description, database, query_string, workgroup
        )
        return json.dumps({"NamedQueryId": query_id})

    def get_named_query(self) -> str:
        query_id = self._get_param("NamedQueryId")
        nq = self.athena_backend.get_named_query(query_id)
        return json.dumps(
            {
                "NamedQuery": {
                    "Name": nq.name,  # type: ignore[union-attr]
                    "Description": nq.description,  # type: ignore[union-attr]
                    "Database": nq.database,  # type: ignore[union-attr]
                    "QueryString": nq.query_string,  # type: ignore[union-attr]
                    "NamedQueryId": nq.id,  # type: ignore[union-attr]
                    "WorkGroup": nq.workgroup.name,  # type: ignore[union-attr]
                }
            }
        )

    def delete_named_query(self) -> str:
        query_id = self._get_param("NamedQueryId")
        self.athena_backend.delete_named_query(query_id)
        return json.dumps({})

    def batch_get_named_query(self) -> str:
        named_query_ids = self._get_param("NamedQueryIds")
        named_queries, unprocessed = self.athena_backend.batch_get_named_query(
            named_query_ids
        )
        return json.dumps(
            {
                "NamedQueries": [
                    {
                        "Name": nq.name,
                        "Description": nq.description,
                        "Database": nq.database,
                        "QueryString": nq.query_string,
                        "NamedQueryId": nq.id,
                        "WorkGroup": nq.workgroup.name,
                    }
                    for nq in named_queries
                ],
                "UnprocessedNamedQueryIds": unprocessed,
            }
        )

    def batch_get_query_execution(self) -> str:
        query_execution_ids = self._get_param("QueryExecutionIds")
        executions, unprocessed = self.athena_backend.batch_get_query_execution(
            query_execution_ids
        )
        result_executions = []
        for execution in executions:
            ddl_commands = ("ALTER", "CREATE", "DESCRIBE", "DROP", "MSCK", "SHOW")
            statement_type = "DML"
            if execution.query.upper().startswith(ddl_commands):
                statement_type = "DDL"
            exec_dict = {
                "QueryExecutionId": execution.id,
                "Query": execution.query,
                "StatementType": statement_type,
                "ResultConfiguration": execution.config,
                "ResultReuseConfiguration": {
                    "ResultReuseByAgeConfiguration": {"Enabled": False}
                },
                "QueryExecutionContext": execution.context,
                "Status": {
                    "State": execution.status,
                    "SubmissionDateTime": execution.start_time,
                    "CompletionDateTime": execution.end_time,
                },
                "Statistics": {
                    "EngineExecutionTimeInMillis": 0,
                    "DataScannedInBytes": 0,
                    "TotalExecutionTimeInMillis": 0,
                    "QueryQueueTimeInMillis": 0,
                    "ServicePreProcessingTimeInMillis": 0,
                    "QueryPlanningTimeInMillis": 0,
                    "ServiceProcessingTimeInMillis": 0,
                    "ResultReuseInformation": {"ReusedPreviousResult": False},
                },
                "WorkGroup": (
                    execution.workgroup.name if execution.workgroup else None
                ),
            }
            if execution.execution_parameters is not None:
                exec_dict["ExecutionParameters"] = execution.execution_parameters
            result_executions.append(exec_dict)
        return json.dumps(
            {
                "QueryExecutions": result_executions,
                "UnprocessedQueryExecutionIds": unprocessed,
            }
        )

    def list_data_catalogs(self) -> str:
        return json.dumps(
            {"DataCatalogsSummary": self.athena_backend.list_data_catalogs()}
        )

    def list_tags_for_resource(self) -> Union[tuple[str, dict[str, int]], str]:
        resource_arn = self._get_param("ResourceARN")
        tags = self.athena_backend.list_tags_for_resource(resource_arn)
        if not tags:
            return self.error(f"Athena Resource, {resource_arn} Does Not Exist", 400)
        return json.dumps(tags)

    def tag_resource(self) -> str:
        """Handler for tag_resource API call."""
        resource_arn = self._get_param("ResourceARN")
        tags = self._get_param("Tags")
        response = self.athena_backend.tag_resource(resource_arn, tags)
        return json.dumps(response)

    def untag_resource(self) -> str:
        """Handler for untag_resource API call."""
        resource_arn = self._get_param("ResourceARN")
        tag_keys = self._get_param("TagKeys")
        response = self.athena_backend.untag_resource(resource_arn, tag_keys)
        return json.dumps(response)

    def get_data_catalog(self) -> str:
        name = self._get_param("Name")
        return json.dumps({"DataCatalog": self.athena_backend.get_data_catalog(name)})

    def delete_data_catalog(self) -> str:
        name = self._get_param("Name")
        self.athena_backend.delete_data_catalog(name)
        return json.dumps({})

    def update_data_catalog(self) -> str:
        name = self._get_param("Name")
        catalog_type = self._get_param("Type")
        description = self._get_param("Description")
        parameters = self._get_param("Parameters")
        self.athena_backend.update_data_catalog(
            name, catalog_type, description, parameters
        )
        return json.dumps({})

    def create_data_catalog(self) -> Union[tuple[str, dict[str, int]], str]:
        name = self._get_param("Name")
        catalog_type = self._get_param("Type")
        description = self._get_param("Description")
        parameters = self._get_param("Parameters")
        tags = self._get_param("Tags")
        data_catalog = self.athena_backend.create_data_catalog(
            name, catalog_type, description, parameters, tags
        )
        if not data_catalog:
            return self.error("DataCatalog already exists", 400)
        return json.dumps(
            {
                "CreateDataCatalogResponse": {
                    "ResponseMetadata": {
                        "RequestId": "384ac68d-3775-11df-8963-01868b7c937a"
                    }
                }
            }
        )

    def list_named_queries(self) -> str:
        next_token = self._get_param("NextToken")
        max_results = self._get_param("MaxResults")
        work_group = self._get_param("WorkGroup") or "primary"
        named_queries, next_token = self.athena_backend.list_named_queries(
            next_token=next_token, max_results=max_results, work_group=work_group
        )
        named_query_ids = [nq.id for nq in named_queries]
        return json.dumps({"NamedQueryIds": named_query_ids, "NextToken": next_token})

    def create_prepared_statement(self) -> Union[str, tuple[str, dict[str, int]]]:
        statement_name = self._get_param("StatementName")
        work_group = self._get_param("WorkGroup")
        query_statement = self._get_param("QueryStatement")
        description = self._get_param("Description")
        if not self.athena_backend.get_work_group(work_group):
            return self.error("WorkGroup does not exist", 400)
        self.athena_backend.create_prepared_statement(
            statement_name=statement_name,
            workgroup=work_group,
            query_statement=query_statement,
            description=description,
        )
        return json.dumps({})

    def delete_prepared_statement(self) -> str:
        statement_name = self._get_param("StatementName")
        work_group = self._get_param("WorkGroup")
        self.athena_backend.delete_prepared_statement(statement_name, work_group)
        return json.dumps({})

    def update_prepared_statement(self) -> Union[str, tuple[str, dict[str, int]]]:
        statement_name = self._get_param("StatementName")
        work_group = self._get_param("WorkGroup")
        query_statement = self._get_param("QueryStatement")
        description = self._get_param("Description")
        self.athena_backend.update_prepared_statement(
            statement_name=statement_name,
            work_group=work_group,
            query_statement=query_statement,
            description=description,
        )
        return json.dumps({})

    def list_prepared_statements(self) -> str:
        work_group = self._get_param("WorkGroup")
        prepared_statements = self.athena_backend.list_prepared_statements(
            work_group=work_group,
        )
        return json.dumps(
            {
                "PreparedStatements": [
                    {
                        "StatementName": ps.statement_name,
                        "LastModifiedTime": ps.last_modified_time.timestamp()
                        if hasattr(ps, "last_modified_time") and ps.last_modified_time
                        else None,
                    }
                    for ps in prepared_statements
                ]
            }
        )

    def batch_get_prepared_statement(self) -> str:
        prepared_statement_names = self._get_param("PreparedStatementNames")
        work_group = self._get_param("WorkGroup")
        prepared_statements, unprocessed = (
            self.athena_backend.batch_get_prepared_statement(
                prepared_statement_names, work_group
            )
        )
        return json.dumps(
            {
                "PreparedStatements": [
                    {
                        "StatementName": ps.statement_name,
                        "QueryStatement": ps.query_statement,
                        "WorkGroupName": ps.workgroup,
                        "Description": ps.description,
                    }
                    for ps in prepared_statements
                ],
                "UnprocessedPreparedStatementNames": unprocessed,
            }
        )

    def cancel_capacity_reservation(self) -> str:
        name = self._get_param("Name")
        self.athena_backend.cancel_capacity_reservation(name)
        return json.dumps({})

    def delete_capacity_reservation(self) -> str:
        name = self._get_param("Name")
        self.athena_backend.delete_capacity_reservation(name)
        return json.dumps({})

    def get_prepared_statement(self) -> str:
        statement_name = self._get_param("StatementName")
        work_group = self._get_param("WorkGroup")
        ps = self.athena_backend.get_prepared_statement(
            statement_name=statement_name,
            work_group=work_group,
        )
        return json.dumps(
            {
                "PreparedStatement": {
                    "StatementName": ps.statement_name,  # type: ignore[union-attr]
                    "QueryStatement": ps.query_statement,  # type: ignore[union-attr]
                    "WorkGroupName": ps.workgroup,  # type: ignore[union-attr]
                    "Description": ps.description,  # type: ignore[union-attr]
                    # "LastModifiedTime": ps.last_modified_time,  # type: ignore[union-attr]
                }
            }
        )

    def get_database(self) -> Union[str, tuple[str, dict[str, int]]]:
        catalog_name = self._get_param("CatalogName")
        database_name = self._get_param("DatabaseName")
        db = self.athena_backend.get_database(catalog_name, database_name)
        if db is None:
            return self.error(
                f"Database {database_name} not found in catalog {catalog_name}", 400
            )
        return json.dumps(
            {
                "Database": {
                    "Name": db.name,
                    "Description": db.description,
                    "Parameters": db.parameters,
                }
            }
        )

    def list_databases(self) -> str:
        catalog_name = self._get_param("CatalogName")
        databases = self.athena_backend.list_databases(catalog_name)
        return json.dumps(
            {
                "DatabaseList": [
                    {
                        "Name": db.name,
                        "Description": db.description,
                        "Parameters": db.parameters,
                    }
                    for db in databases
                ]
            }
        )

    def get_table_metadata(self) -> Union[str, tuple[str, dict[str, int]]]:
        catalog_name = self._get_param("CatalogName")
        database_name = self._get_param("DatabaseName")
        table_name = self._get_param("TableName")
        tm = self.athena_backend.get_table_metadata(
            catalog_name, database_name, table_name
        )
        if tm is None:
            return self.error(
                f"Table {table_name} not found in database {database_name}", 400
            )
        return json.dumps(
            {
                "TableMetadata": {
                    "Name": tm.name,
                    "TableType": tm.table_type,
                    "Columns": tm.columns,
                    "PartitionKeys": tm.partition_keys,
                    "Parameters": tm.parameters,
                    "CreateTime": tm.create_time,
                }
            }
        )

    def list_engine_versions(self) -> str:
        engine_versions = self.athena_backend.list_engine_versions()
        return json.dumps({"EngineVersions": engine_versions})

    def list_application_dpu_sizes(self) -> str:
        dpu_sizes = self.athena_backend.list_application_dpu_sizes()
        return json.dumps({"ApplicationDPUSizes": dpu_sizes})

    def get_capacity_assignment_configuration(self) -> str:
        name = self._get_param("CapacityReservationName")
        result = self.athena_backend.get_capacity_assignment_configuration(name)
        return json.dumps(result)

    def start_session(self) -> Union[str, tuple[str, dict[str, int]]]:
        work_group = self._get_param("WorkGroup")
        engine_configuration = self._get_param("EngineConfiguration")
        notebook_version = self._get_param("NotebookVersion")
        description = self._get_param("Description")
        if work_group and not self.athena_backend.get_work_group(work_group):
            return self.error("WorkGroup does not exist", 400)
        result = self.athena_backend.start_session(
            work_group=work_group,
            engine_configuration=engine_configuration,
            notebook_version=notebook_version,
            description=description,
        )
        return json.dumps(result)

    def get_session(self) -> Union[str, tuple[str, dict[str, int]]]:
        session_id = self._get_param("SessionId")
        result = self.athena_backend.get_session(session_id)
        if result is None:
            return self.error(f"Session {session_id} was not found", 400)
        return json.dumps(result)

    def get_session_status(self) -> Union[str, tuple[str, dict[str, int]]]:
        session_id = self._get_param("SessionId")
        result = self.athena_backend.get_session_status(session_id)
        if result is None:
            return self.error(f"Session {session_id} was not found", 400)
        return json.dumps(result)

    def terminate_session(self) -> Union[str, tuple[str, dict[str, int]]]:
        session_id = self._get_param("SessionId")
        result = self.athena_backend.terminate_session(session_id)
        if result is None:
            return self.error(f"Session {session_id} was not found", 400)
        return json.dumps(result)

    def list_sessions(self) -> str:
        work_group = self._get_param("WorkGroup")
        sessions = self.athena_backend.list_sessions(work_group)
        return json.dumps(
            {
                "Sessions": sessions,
                "Description": "",
            }
        )

    def create_presigned_notebook_url(self) -> Union[str, tuple[str, dict[str, int]]]:
        session_id = self._get_param("SessionId")
        result = self.athena_backend.create_presigned_notebook_url(session_id)
        if result is None:
            return self.error(f"Session {session_id} was not found", 400)
        return json.dumps(result)

    def get_calculation_execution(self) -> Union[str, tuple[str, dict[str, int]]]:
        calc_id = self._get_param("CalculationExecutionId")
        result = self.athena_backend.get_calculation_execution(calc_id)
        if result is None:
            return self.error(f"CalculationExecution {calc_id} was not found", 400)
        return json.dumps(result)

    def get_calculation_execution_code(
        self,
    ) -> Union[str, tuple[str, dict[str, int]]]:
        calc_id = self._get_param("CalculationExecutionId")
        result = self.athena_backend.get_calculation_execution_code(calc_id)
        if result is None:
            return self.error(f"CalculationExecution {calc_id} was not found", 400)
        return json.dumps(result)

    def get_calculation_execution_status(
        self,
    ) -> Union[str, tuple[str, dict[str, int]]]:
        calc_id = self._get_param("CalculationExecutionId")
        result = self.athena_backend.get_calculation_execution_status(calc_id)
        if result is None:
            return self.error(f"CalculationExecution {calc_id} was not found", 400)
        return json.dumps(result)

    def list_calculation_executions(self) -> str:
        session_id = self._get_param("SessionId")
        calculations = self.athena_backend.list_calculation_executions(session_id)
        return json.dumps({"Calculations": calculations})

    def get_notebook_metadata(self) -> Union[str, tuple[str, dict[str, int]]]:
        notebook_id = self._get_param("NotebookId")
        result = self.athena_backend.get_notebook_metadata(notebook_id)
        if result is None:
            return self.error(f"Notebook {notebook_id} was not found", 400)
        return json.dumps(result)

    def list_notebook_metadata(self) -> str:
        work_group = self._get_param("WorkGroup")
        notebooks = self.athena_backend.list_notebook_metadata(work_group)
        return json.dumps({"NotebookMetadataList": notebooks})

    def list_notebook_sessions(self) -> str:
        notebook_id = self._get_param("NotebookId")
        sessions = self.athena_backend.list_notebook_sessions(notebook_id)
        return json.dumps({"NotebookSessionsList": sessions})

    def create_notebook(self) -> Union[str, tuple[str, dict[str, int]]]:
        work_group = self._get_param("WorkGroup")
        name = self._get_param("Name")
        client_request_token = self._get_param("ClientRequestToken")
        if work_group and not self.athena_backend.get_work_group(work_group):
            return self.error("WorkGroup does not exist", 400)
        notebook_id = self.athena_backend.create_notebook(
            work_group=work_group,
            name=name,
            client_request_token=client_request_token,
        )
        return json.dumps({"NotebookId": notebook_id})

    def delete_notebook(self) -> str:
        notebook_id = self._get_param("NotebookId")
        self.athena_backend.delete_notebook(notebook_id)
        return json.dumps({})

    def update_notebook(self) -> str:
        notebook_id = self._get_param("NotebookId")
        payload = self._get_param("Payload")
        type_ = self._get_param("Type")
        session_id = self._get_param("SessionId")
        client_request_token = self._get_param("ClientRequestToken")
        self.athena_backend.update_notebook(
            notebook_id=notebook_id,
            payload=payload,
            type_=type_,
            session_id=session_id,
            client_request_token=client_request_token,
        )
        return json.dumps({})

    def update_notebook_metadata(self) -> str:
        notebook_id = self._get_param("NotebookId")
        name = self._get_param("Name")
        client_request_token = self._get_param("ClientRequestToken")
        self.athena_backend.update_notebook_metadata(
            notebook_id=notebook_id,
            name=name,
            client_request_token=client_request_token,
        )
        return json.dumps({})

    def export_notebook(self) -> Union[str, tuple[str, dict[str, int]]]:
        notebook_id = self._get_param("NotebookId")
        result = self.athena_backend.export_notebook(notebook_id)
        if result is None:
            return self.error(f"Notebook {notebook_id} was not found", 400)
        return json.dumps(result)

    def import_notebook(self) -> Union[str, tuple[str, dict[str, int]]]:
        work_group = self._get_param("WorkGroup")
        name = self._get_param("Name")
        payload = self._get_param("Payload")
        notebook_s3_location_uri = self._get_param("NotebookS3LocationUri")
        type_ = self._get_param("Type") or "IPYNB"
        client_request_token = self._get_param("ClientRequestToken")
        if work_group and not self.athena_backend.get_work_group(work_group):
            return self.error("WorkGroup does not exist", 400)
        notebook_id = self.athena_backend.import_notebook(
            work_group=work_group,
            name=name,
            payload=payload,
            notebook_s3_location_uri=notebook_s3_location_uri,
            type_=type_,
            client_request_token=client_request_token,
        )
        return json.dumps({"NotebookId": notebook_id})

    def update_named_query(self) -> str:
        named_query_id = self._get_param("NamedQueryId")
        name = self._get_param("Name")
        description = self._get_param("Description")
        query_string = self._get_param("QueryString")
        self.athena_backend.update_named_query(
            named_query_id=named_query_id,
            name=name,
            description=description,
            query_string=query_string,
        )
        return json.dumps({})

    def put_capacity_assignment_configuration(self) -> str:
        capacity_reservation_name = self._get_param("CapacityReservationName")
        capacity_assignments = self._get_param("CapacityAssignments") or []
        self.athena_backend.put_capacity_assignment_configuration(
            capacity_reservation_name=capacity_reservation_name,
            capacity_assignments=capacity_assignments,
        )
        return json.dumps({})

    def start_calculation_execution(self) -> Union[str, tuple[str, dict[str, int]]]:
        session_id = self._get_param("SessionId")
        description = self._get_param("Description")
        code_block = self._get_param("CodeBlock")
        result = self.athena_backend.start_calculation_execution(
            session_id=session_id,
            description=description,
            code_block=code_block,
        )
        return json.dumps(result)

    def stop_calculation_execution(self) -> Union[str, tuple[str, dict[str, int]]]:
        calculation_execution_id = self._get_param("CalculationExecutionId")
        state = self.athena_backend.stop_calculation_execution(calculation_execution_id)
        if state is None:
            return self.error(
                f"CalculationExecution {calculation_execution_id} was not found", 400
            )
        return json.dumps({"State": state})

    def get_session_endpoint(self) -> Union[str, tuple[str, dict[str, int]]]:
        session_id = self._get_param("SessionId")
        result = self.athena_backend.get_session_endpoint(session_id)
        if result is None:
            return self.error(f"Session {session_id} was not found", 400)
        return json.dumps(result)

    def list_executors(self) -> str:
        session_id = self._get_param("SessionId")
        result = self.athena_backend.list_executors(session_id)
        return json.dumps(result)

    def list_table_metadata(self) -> str:
        catalog_name = self._get_param("CatalogName")
        database_name = self._get_param("DatabaseName")
        tables = self.athena_backend.list_table_metadata(catalog_name, database_name)
        return json.dumps(
            {
                "TableMetadataList": [
                    {
                        "Name": tm.name,
                        "TableType": tm.table_type,
                        "Columns": tm.columns,
                        "PartitionKeys": tm.partition_keys,
                        "Parameters": tm.parameters,
                        "CreateTime": tm.create_time,
                    }
                    for tm in tables
                ]
            }
        )

    def get_resource_dashboard(self) -> Union[str, tuple[str, dict[str, int]]]:
        resource_arn = self._get_param("ResourceARN") or ""
        result = self.athena_backend.get_resource_dashboard(resource_arn)
        return json.dumps(result)

    def get_query_runtime_statistics(self) -> Union[str, tuple[str, dict[str, int]]]:
        query_execution_id = self._get_param("QueryExecutionId")

        ps = self.athena_backend.get_query_runtime_statistics(
            query_execution_id=query_execution_id
        )

        if ps is None:
            return self.error(f"QueryExecution {query_execution_id} was not found", 400)

        return json.dumps(
            {
                "QueryRuntimeStatistics": {
                    "OutputStage": {
                        "ExecutionTime": 100,
                        "InputBytes": 0,
                        "InputRows": 0,
                        "OutputBytes": 1,
                        "OutputRows": 1,
                        "StageId": 1,
                        "State": ps.status,
                    },
                    "Rows": {
                        "InputBytes": 0,
                        "InputRows": 0,
                        "OutputBytes": 2,
                        "OutputRows": 2,
                    },
                    "Timeline": {
                        "EngineExecutionTimeInMillis": 0,
                        "QueryPlanningTimeInMillis": 0,
                        "QueryQueueTimeInMillis": 0,
                        "ServicePreProcessingTimeInMillis": 0,
                        "ServiceProcessingTimeInMillis": 0,
                        "TotalExecutionTimeInMillis": 0,
                    },
                }
            }
        )
