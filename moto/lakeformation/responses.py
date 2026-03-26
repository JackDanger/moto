"""Handles incoming lakeformation requests, invokes methods, returns responses."""

import json
from typing import Any

from moto.core.responses import BaseResponse

from .exceptions import InvalidInput
from .models import (
    LakeFormationBackend,
    ListPermissionsResource,
    ListPermissionsResourceDatabase,
    ListPermissionsResourceDataLocation,
    ListPermissionsResourceTable,
    RessourceType,
    lakeformation_backends,
)


class LakeFormationResponse(BaseResponse):
    """Handler for LakeFormation requests and responses."""

    def __init__(self) -> None:
        super().__init__(service_name="lakeformation")

    @property
    def lakeformation_backend(self) -> LakeFormationBackend:
        """Return backend instance specific for this region."""
        return lakeformation_backends[self.current_account][self.region]

    def describe_resource(self) -> str:
        resource_arn = self._get_param("ResourceArn")
        resource = self.lakeformation_backend.describe_resource(
            resource_arn=resource_arn
        )
        return json.dumps({"ResourceInfo": resource.to_dict()})

    def deregister_resource(self) -> str:
        resource_arn = self._get_param("ResourceArn")
        self.lakeformation_backend.deregister_resource(resource_arn=resource_arn)
        return "{}"

    def register_resource(self) -> str:
        resource_arn = self._get_param("ResourceArn")
        role_arn = self._get_param("RoleArn")
        self.lakeformation_backend.register_resource(
            resource_arn=resource_arn,
            role_arn=role_arn,
        )
        return "{}"

    def list_resources(self) -> str:
        resources = self.lakeformation_backend.list_resources()
        return json.dumps({"ResourceInfoList": [res.to_dict() for res in resources]})

    def get_data_lake_settings(self) -> str:
        catalog_id = self._get_param("CatalogId") or self.current_account
        settings = self.lakeformation_backend.get_data_lake_settings(catalog_id)
        return json.dumps({"DataLakeSettings": settings})

    def put_data_lake_settings(self) -> str:
        catalog_id = self._get_param("CatalogId") or self.current_account
        settings = self._get_param("DataLakeSettings")
        self.lakeformation_backend.put_data_lake_settings(catalog_id, settings)
        return "{}"

    def grant_permissions(self) -> str:
        catalog_id = self._get_param("CatalogId") or self.current_account
        principal = self._get_param("Principal")
        resource = self._get_param("Resource")
        permissions = self._get_param("Permissions")
        permissions_with_grant_options = self._get_param("PermissionsWithGrantOption")
        self.lakeformation_backend.grant_permissions(
            catalog_id=catalog_id,
            principal=principal,
            resource=resource,
            permissions=permissions,
            permissions_with_grant_options=permissions_with_grant_options,
        )
        return "{}"

    def revoke_permissions(self) -> str:
        catalog_id = self._get_param("CatalogId") or self.current_account
        principal = self._get_param("Principal")
        resource = self._get_param("Resource")
        permissions = self._get_param("Permissions")
        permissions_with_grant_options = (
            self._get_param("PermissionsWithGrantOption") or []
        )
        self.lakeformation_backend.revoke_permissions(
            catalog_id=catalog_id,
            principal=principal,
            resource=resource,
            permissions_to_revoke=permissions,
            permissions_with_grant_options_to_revoke=permissions_with_grant_options,
        )
        return "{}"

    def list_permissions(self) -> str:
        catalog_id = self._get_param("CatalogId") or self.current_account
        principal = self._get_param("Principal")
        resource = self._get_param("Resource")
        resource_type_param = self._get_param("ResourceType")
        if principal is not None and resource is None:
            # Error message is the exact string returned by the AWS-CLI
            raise InvalidInput(
                "An error occurred (InvalidInputException) when calling the ListPermissions operation: Resource is mandatory if Principal is set in the input."
            )

        if resource_type_param is None:
            resource_type = None
        else:
            resource_type = RessourceType(resource_type_param)

        if resource is None:
            list_permission_resource = None
        else:
            database_sub_dictionary = resource.get("Database")
            table_sub_dictionary = resource.get("Table")
            catalog_sub_dictionary = resource.get("Catalog")
            data_location_sub_dictionary = resource.get("DataLocation")

            if database_sub_dictionary is None:
                database = None
            else:
                database = ListPermissionsResourceDatabase(
                    name=database_sub_dictionary.get("Name"),
                    catalog_id=database_sub_dictionary.get("CatalogId"),
                )

            if table_sub_dictionary is None:
                table = None
            else:
                table = ListPermissionsResourceTable(
                    database_name=table_sub_dictionary.get("DatabaseName"),
                    name=table_sub_dictionary.get("Name"),
                    catalog_id=table_sub_dictionary.get("CatalogId"),
                    table_wildcard=table_sub_dictionary.get("TableWildcard"),
                )

            if data_location_sub_dictionary is None:
                data_location = None
            else:
                data_location = ListPermissionsResourceDataLocation(
                    resource_arn=data_location_sub_dictionary.get("ResourceArn"),
                    catalog_id=data_location_sub_dictionary.get("CatalogId"),
                )

            list_permission_resource = ListPermissionsResource(
                catalog=catalog_sub_dictionary,
                database=database,
                table=table,
                table_with_columns=None,
                data_location=data_location,
                data_cells_filter=None,
                lf_tag=None,
                lf_tag_policy=None,
            )
        permissions = self.lakeformation_backend.list_permissions(
            catalog_id=catalog_id,
            principal=principal,
            resource=list_permission_resource,
            resource_type=resource_type,
        )
        return json.dumps({"PrincipalResourcePermissions": permissions})

    def create_lf_tag(self) -> str:
        catalog_id = self._get_param("CatalogId") or self.current_account
        key = self._get_param("TagKey")
        values = self._get_param("TagValues")
        self.lakeformation_backend.create_lf_tag(catalog_id, key, values)
        return "{}"

    def get_lf_tag(self) -> str:
        catalog_id = self._get_param("CatalogId") or self.current_account
        key = self._get_param("TagKey")
        tag_values = self.lakeformation_backend.get_lf_tag(catalog_id, key)
        return json.dumps(
            {"CatalogId": catalog_id, "TagKey": key, "TagValues": tag_values}
        )

    def delete_lf_tag(self) -> str:
        catalog_id = self._get_param("CatalogId") or self.current_account
        key = self._get_param("TagKey")
        self.lakeformation_backend.delete_lf_tag(catalog_id, key)
        return "{}"

    def list_lf_tags(self) -> str:
        catalog_id = self._get_param("CatalogId") or self.current_account
        tags = self.lakeformation_backend.list_lf_tags(catalog_id)
        return json.dumps(
            {
                "LFTags": [
                    {"CatalogId": catalog_id, "TagKey": tag, "TagValues": value}
                    for tag, value in tags.items()
                ]
            }
        )

    def update_lf_tag(self) -> str:
        catalog_id = self._get_param("CatalogId") or self.current_account
        tag_key = self._get_param("TagKey")
        to_delete = self._get_param("TagValuesToDelete")
        to_add = self._get_param("TagValuesToAdd")
        self.lakeformation_backend.update_lf_tag(catalog_id, tag_key, to_delete, to_add)
        return "{}"

    def list_data_cells_filter(self) -> str:
        data_cells = self.lakeformation_backend.list_data_cells_filter()
        return json.dumps({"DataCellsFilters": data_cells})

    def batch_grant_permissions(self) -> str:
        catalog_id = self._get_param("CatalogId") or self.current_account
        entries = self._get_param("Entries")
        self.lakeformation_backend.batch_grant_permissions(catalog_id, entries)
        return json.dumps({"Failures": []})

    def batch_revoke_permissions(self) -> str:
        catalog_id = self._get_param("CatalogId") or self.current_account
        entries = self._get_param("Entries")
        self.lakeformation_backend.batch_revoke_permissions(catalog_id, entries)
        return json.dumps({"Failures": []})

    def add_lf_tags_to_resource(self) -> str:
        catalog_id = self._get_param("CatalogId") or self.current_account
        resource = self._get_param("Resource")
        tags = self._get_param("LFTags")
        failures = self.lakeformation_backend.add_lf_tags_to_resource(
            catalog_id, resource, tags
        )
        return json.dumps({"Failures": failures})

    def get_resource_lf_tags(self) -> str:
        catalog_id = self._get_param("CatalogId") or self.current_account
        resource = self._get_param("Resource")
        db, table, columns = self.lakeformation_backend.get_resource_lf_tags(
            catalog_id, resource
        )
        resp: dict[str, Any] = {}
        if db:
            resp["LFTagOnDatabase"] = db
        if table:
            resp["LFTagsOnTable"] = table
        if columns:
            resp["LFTagsOnColumns"] = columns
        return json.dumps(resp)

    def remove_lf_tags_from_resource(self) -> str:
        catalog_id = self._get_param("CatalogId") or self.current_account
        resource = self._get_param("Resource")
        tags = self._get_param("LFTags")
        self.lakeformation_backend.remove_lf_tags_from_resource(
            catalog_id, resource, tags
        )
        return "{}"

    def describe_transaction(self) -> str:
        transaction_id = self._get_param("TransactionId")
        txn = self.lakeformation_backend.describe_transaction(transaction_id)
        return json.dumps({"TransactionDescription": txn.to_dict()})

    def list_transactions(self) -> str:
        status_filter = self._get_param("StatusFilter")
        transactions = self.lakeformation_backend.list_transactions(
            status_filter=status_filter,
        )
        return json.dumps({"Transactions": [t.to_dict() for t in transactions]})

    def start_transaction(self) -> str:
        transaction_type = self._get_param("TransactionType") or "READ_AND_WRITE"
        transaction_id = self.lakeformation_backend.start_transaction(transaction_type)
        return json.dumps({"TransactionId": transaction_id})

    def commit_transaction(self) -> str:
        transaction_id = self._get_param("TransactionId")
        status = self.lakeformation_backend.commit_transaction(transaction_id)
        return json.dumps({"TransactionStatus": status})

    def cancel_transaction(self) -> str:
        transaction_id = self._get_param("TransactionId")
        self.lakeformation_backend.cancel_transaction(transaction_id)
        return "{}"

    def get_data_lake_principal(self) -> str:
        principal = self.lakeformation_backend.get_data_lake_principal()
        return json.dumps({"Identity": principal})

    def get_effective_permissions_for_path(self) -> str:
        catalog_id = self._get_param("CatalogId") or self.current_account
        resource_arn = self._get_param("ResourceArn")
        permissions = self.lakeformation_backend.get_effective_permissions_for_path(
            catalog_id,
            resource_arn,
        )
        return json.dumps({"Permissions": permissions})

    def get_query_state(self) -> str:
        query_id = self._get_param("QueryId")
        state = self.lakeformation_backend.get_query_state(query_id)
        return json.dumps({"State": state})

    def get_query_statistics(self) -> str:
        query_id = self._get_param("QueryId")
        stats = self.lakeformation_backend.get_query_statistics(query_id)
        return json.dumps(stats)

    def get_work_units(self) -> str:
        query_id = self._get_param("QueryId")
        work_units = self.lakeformation_backend.get_work_units(query_id)
        return json.dumps({"WorkUnitRanges": work_units})

    def get_work_unit_results(self) -> str:
        query_id = self._get_param("QueryId")
        work_unit_id = self._get_param("WorkUnitId")
        work_unit_token = self._get_param("WorkUnitToken")
        self.lakeformation_backend.get_work_unit_results(
            query_id, work_unit_id, work_unit_token
        )
        return json.dumps({"ResultStream": ""})

    def get_temporary_glue_partition_credentials(self) -> str:
        table_arn = self._get_param("TableArn")
        partition = self._get_param("Partition")
        supported_permission_types = self._get_param("SupportedPermissionTypes") or []
        creds = self.lakeformation_backend.get_temporary_glue_partition_credentials(
            table_arn,
            partition,
            supported_permission_types,
        )
        return json.dumps(creds)

    def get_temporary_glue_table_credentials(self) -> str:
        table_arn = self._get_param("TableArn")
        supported_permission_types = self._get_param("SupportedPermissionTypes") or []
        creds = self.lakeformation_backend.get_temporary_glue_table_credentials(
            table_arn,
            supported_permission_types,
        )
        return json.dumps(creds)

    def create_data_cells_filter(self) -> str:
        table_data = self._get_param("TableData")
        self.lakeformation_backend.create_data_cells_filter(table_data)
        return "{}"

    def get_data_cells_filter(self) -> str:
        table_catalog_id = self._get_param("TableCatalogId") or self.current_account
        database_name = self._get_param("DatabaseName")
        table_name = self._get_param("TableName")
        name = self._get_param("Name")
        dcf = self.lakeformation_backend.get_data_cells_filter(
            table_catalog_id,
            database_name,
            table_name,
            name,
        )
        return json.dumps({"DataCellsFilter": dcf.to_dict()})

    def delete_data_cells_filter(self) -> str:
        table_catalog_id = self._get_param("TableCatalogId") or self.current_account
        database_name = self._get_param("DatabaseName")
        table_name = self._get_param("TableName")
        name = self._get_param("Name")
        self.lakeformation_backend.delete_data_cells_filter(
            table_catalog_id,
            database_name,
            table_name,
            name,
        )
        return "{}"

    def update_data_cells_filter(self) -> str:
        table_data = self._get_param("TableData")
        self.lakeformation_backend.update_data_cells_filter(table_data)
        return "{}"

    def search_databases_by_lf_tags(self) -> str:
        catalog_id = self._get_param("CatalogId") or self.current_account
        expression = self._get_param("Expression") or []
        results = self.lakeformation_backend.search_databases_by_lf_tags(
            catalog_id,
            expression,
        )
        return json.dumps({"DatabaseList": results})

    def search_tables_by_lf_tags(self) -> str:
        catalog_id = self._get_param("CatalogId") or self.current_account
        expression = self._get_param("Expression") or []
        results = self.lakeformation_backend.search_tables_by_lf_tags(
            catalog_id,
            expression,
        )
        return json.dumps({"TableList": results})

    def start_query_planning(self) -> str:
        query_planning_context = self._get_param("QueryPlanningContext") or {}
        query_string = self._get_param("QueryString") or ""
        result = self.lakeformation_backend.start_query_planning(
            query_planning_context,
            query_string,
        )
        return json.dumps(result)

    def create_lf_tag_expression(self) -> str:
        catalog_id = self._get_param("CatalogId") or self.current_account
        name = self._get_param("Name")
        expression = self._get_param("Expression") or []
        description = self._get_param("Description")
        self.lakeformation_backend.create_lf_tag_expression(
            catalog_id=catalog_id,
            name=name,
            expression=expression,
            description=description,
        )
        return "{}"

    def get_lf_tag_expression(self) -> str:
        catalog_id = self._get_param("CatalogId") or self.current_account
        name = self._get_param("Name")
        ex = self.lakeformation_backend.get_lf_tag_expression(catalog_id, name)
        return json.dumps(ex.to_dict())

    def list_lf_tag_expressions(self) -> str:
        catalog_id = self._get_param("CatalogId") or self.current_account
        max_results = self._get_param("MaxResults")
        next_token = self._get_param("NextToken")
        expressions, next_token = self.lakeformation_backend.list_lf_tag_expressions(
            catalog_id=catalog_id,
            max_results=max_results,
            next_token=next_token,
        )
        result: dict[str, Any] = {
            "LFTagExpressions": [e.to_dict() for e in expressions],
        }
        if next_token is not None:
            result["NextToken"] = next_token
        return json.dumps(result)

    def update_lf_tag_expression(self) -> str:
        catalog_id = self._get_param("CatalogId") or self.current_account
        name = self._get_param("Name")
        expression = self._get_param("Expression")
        description = self._get_param("Description")
        self.lakeformation_backend.update_lf_tag_expression(
            catalog_id=catalog_id,
            name=name,
            expression=expression,
            description=description,
        )
        return "{}"

    def delete_lf_tag_expression(self) -> str:
        catalog_id = self._get_param("CatalogId") or self.current_account
        name = self._get_param("Name")
        self.lakeformation_backend.delete_lf_tag_expression(catalog_id, name)
        return "{}"

    def create_lake_formation_identity_center_configuration(self) -> str:
        catalog_id = self._get_param("CatalogId") or self.current_account
        instance_arn = self._get_param("InstanceArn")
        external_filtering = self._get_param("ExternalFiltering")
        share_recipients = self._get_param("ShareRecipients")
        service_integrations = self._get_param("ServiceIntegrations")
        application_arn = self.lakeformation_backend.create_lake_formation_identity_center_configuration(
            catalog_id=catalog_id,
            instance_arn=instance_arn,
            external_filtering=external_filtering,
            share_recipients=share_recipients,
            service_integrations=service_integrations,
        )
        return json.dumps({"ApplicationArn": application_arn})

    def describe_lake_formation_identity_center_configuration(self) -> str:
        catalog_id = self._get_param("CatalogId") or self.current_account
        config = self.lakeformation_backend.describe_lake_formation_identity_center_configuration(
            catalog_id,
        )
        return json.dumps(config)

    def update_lake_formation_identity_center_configuration(self) -> str:
        catalog_id = self._get_param("CatalogId") or self.current_account
        share_recipients = self._get_param("ShareRecipients")
        service_integrations = self._get_param("ServiceIntegrations")
        application_status = self._get_param("ApplicationStatus")
        external_filtering = self._get_param("ExternalFiltering")
        self.lakeformation_backend.update_lake_formation_identity_center_configuration(
            catalog_id=catalog_id,
            share_recipients=share_recipients,
            service_integrations=service_integrations,
            application_status=application_status,
            external_filtering=external_filtering,
        )
        return "{}"

    def delete_lake_formation_identity_center_configuration(self) -> str:
        catalog_id = self._get_param("CatalogId") or self.current_account
        self.lakeformation_backend.delete_lake_formation_identity_center_configuration(
            catalog_id,
        )
        return "{}"

    def list_lake_formation_opt_ins(self) -> str:
        opt_ins = self.lakeformation_backend.list_lake_formation_opt_ins()
        return json.dumps({"LakeFormationOptInsInfoList": opt_ins})

    def get_temporary_data_location_credentials(self) -> str:
        creds = self.lakeformation_backend.get_temporary_data_location_credentials(
            data_locations=self._get_param("DataLocations") or [],
            credentials_scope=self._get_param("CredentialsScope", ""),
            duration_seconds=self._get_param("DurationSeconds"),
            audit_context=self._get_param("AuditContext"),
        )
        return json.dumps({"Credentials": creds, "AccessibleDataLocations": []})

    def list_table_storage_optimizers(self) -> str:
        catalog_id = self._get_param("CatalogId") or self.current_account
        optimizers = self.lakeformation_backend.list_table_storage_optimizers(
            catalog_id=catalog_id,
            database_name=self._get_param("DatabaseName", ""),
            table_name=self._get_param("TableName", ""),
            storage_optimizer_type=self._get_param("StorageOptimizerType"),
        )
        return json.dumps({"StorageOptimizerList": optimizers})

    def get_table_objects(self) -> str:
        catalog_id = self._get_param("CatalogId") or self.current_account
        objects = self.lakeformation_backend.get_table_objects(
            catalog_id=catalog_id,
            database_name=self._get_param("DatabaseName", ""),
            table_name=self._get_param("TableName", ""),
        )
        return json.dumps({"Objects": objects})

    def create_lake_formation_opt_in(self) -> str:
        self.lakeformation_backend.create_lake_formation_opt_in()
        return json.dumps({})

    def delete_lake_formation_opt_in(self) -> str:
        self.lakeformation_backend.delete_lake_formation_opt_in()
        return json.dumps({})

    def delete_objects_on_cancel(self) -> str:
        self.lakeformation_backend.delete_objects_on_cancel()
        return json.dumps({})

    def extend_transaction(self) -> str:
        self.lakeformation_backend.extend_transaction(
            transaction_id=self._get_param("TransactionId", ""),
        )
        return json.dumps({})

    def update_resource(self) -> str:
        self.lakeformation_backend.update_resource(
            resource_arn=self._get_param("ResourceArn", ""),
            role_arn=self._get_param("RoleArn", ""),
        )
        return json.dumps({})

    def update_table_objects(self) -> str:
        self.lakeformation_backend.update_table_objects()
        return json.dumps({})

    def update_table_storage_optimizer(self) -> str:
        result = self.lakeformation_backend.update_table_storage_optimizer()
        return json.dumps(result)

    def assume_decorated_role_with_saml(self) -> str:
        role_arn = self._get_param("RoleArn", "")
        principal_arn = self._get_param("PrincipalArn", "")
        saml_assertion = self._get_param("SAMLAssertion", "")
        duration_seconds = self._get_param("DurationSeconds")
        creds = self.lakeformation_backend.assume_decorated_role_with_saml(
            role_arn=role_arn,
            principal_arn=principal_arn,
            saml_assertion=saml_assertion,
            duration_seconds=duration_seconds,
        )
        return json.dumps(creds)
