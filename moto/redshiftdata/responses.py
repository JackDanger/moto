import json

from moto.core.common_types import TYPE_RESPONSE
from moto.core.responses import BaseResponse

from .models import RedshiftDataAPIServiceBackend, redshiftdata_backends


class RedshiftDataAPIServiceResponse(BaseResponse):
    def __init__(self) -> None:
        super().__init__(service_name="redshift-data")

    @property
    def redshiftdata_backend(self) -> RedshiftDataAPIServiceBackend:
        return redshiftdata_backends[self.current_account][self.region]

    def cancel_statement(self) -> TYPE_RESPONSE:
        statement_id = self._get_param("Id")
        self.redshiftdata_backend.cancel_statement(statement_id=statement_id)
        return 200, {}, json.dumps({"Status": True})

    def describe_statement(self) -> TYPE_RESPONSE:
        statement_id = self._get_param("Id")
        statement = self.redshiftdata_backend.describe_statement(
            statement_id=statement_id
        )
        return 200, {}, json.dumps(dict(statement))

    def execute_statement(self) -> TYPE_RESPONSE:
        cluster_identifier = self._get_param("ClusterIdentifier")
        database = self._get_param("Database")
        db_user = self._get_param("DbUser")
        parameters = self._get_param("Parameters")
        secret_arn = self._get_param("SecretArn")
        sql = self._get_param("Sql")
        statement = self.redshiftdata_backend.execute_statement(
            cluster_identifier=cluster_identifier,
            database=database,
            db_user=db_user,
            parameters=parameters,
            secret_arn=secret_arn,
            sql=sql,
        )

        return (
            200,
            {},
            json.dumps(
                {
                    "ClusterIdentifier": statement.cluster_identifier,
                    "CreatedAt": statement.created_at,
                    "Database": statement.database,
                    "DbUser": statement.db_user,
                    "Id": statement.id,
                    "SecretArn": statement.secret_arn,
                }
            ),
        )

    def batch_execute_statement(self) -> TYPE_RESPONSE:
        cluster_identifier = self._get_param("ClusterIdentifier")
        database = self._get_param("Database")
        db_user = self._get_param("DbUser")
        sqls = self._get_param("Sqls")
        secret_arn = self._get_param("SecretArn")
        statement_name = self._get_param("StatementName")
        workgroup_name = self._get_param("WorkgroupName")
        statement = self.redshiftdata_backend.batch_execute_statement(
            cluster_identifier=cluster_identifier,
            database=database,
            db_user=db_user,
            sqls=sqls,
            secret_arn=secret_arn,
            statement_name=statement_name,
            workgroup_name=workgroup_name,
        )
        return (
            200,
            {},
            json.dumps(
                {
                    "ClusterIdentifier": statement.cluster_identifier,
                    "CreatedAt": statement.created_at,
                    "Database": statement.database,
                    "DbUser": statement.db_user,
                    "Id": statement.id,
                    "SecretArn": statement.secret_arn,
                    "SubStatements": [{"Id": sid} for sid in statement.sub_statements],
                }
            ),
        )

    def describe_table(self) -> TYPE_RESPONSE:
        database = self._get_param("Database")
        schema = self._get_param("Schema")
        table = self._get_param("Table")
        result = self.redshiftdata_backend.describe_table(
            database=database,
            schema=schema,
            table=table,
        )
        return 200, {}, json.dumps(result)

    def get_statement_result_v2(self) -> TYPE_RESPONSE:
        statement_id = self._get_param("Id")
        result = self.redshiftdata_backend.get_statement_result_v2(statement_id)
        return 200, {}, json.dumps(result)

    def list_databases(self) -> TYPE_RESPONSE:
        database = self._get_param("Database")
        cluster_identifier = self._get_param("ClusterIdentifier")
        databases = self.redshiftdata_backend.list_databases(
            database=database,
            cluster_identifier=cluster_identifier,
        )
        return 200, {}, json.dumps({"Databases": databases})

    def list_schemas(self) -> TYPE_RESPONSE:
        database = self._get_param("Database")
        schema_pattern = self._get_param("SchemaPattern")
        schemas = self.redshiftdata_backend.list_schemas(
            database=database,
            schema_pattern=schema_pattern,
        )
        return 200, {}, json.dumps({"Schemas": schemas})

    def list_statements(self) -> TYPE_RESPONSE:
        statement_name = self._get_param("StatementName")
        status = self._get_param("Status")
        statements = self.redshiftdata_backend.list_statements(
            statement_name=statement_name,
            status=status,
        )
        return (
            200,
            {},
            json.dumps(
                {
                    "Statements": [
                        {
                            "Id": s.id,
                            "QueryString": s.query_string,
                            "Status": s.status,
                            "CreatedAt": s.created_at,
                            "UpdatedAt": s.updated_at,
                        }
                        for s in statements
                    ]
                }
            ),
        )

    def list_tables(self) -> TYPE_RESPONSE:
        database = self._get_param("Database")
        schema_pattern = self._get_param("SchemaPattern")
        table_pattern = self._get_param("TablePattern")
        tables = self.redshiftdata_backend.list_tables(
            database=database,
            schema_pattern=schema_pattern,
            table_pattern=table_pattern,
        )
        return 200, {}, json.dumps({"Tables": tables})

    def get_statement_result(self) -> TYPE_RESPONSE:
        statement_id = self._get_param("Id")
        statement_result = self.redshiftdata_backend.get_statement_result(
            statement_id=statement_id
        )

        return 200, {}, json.dumps(dict(statement_result))
