"""Tests for newly added IoT and Glue operations."""

import boto3
import pytest
from moto import mock_aws


# === IoT Tests ===


@mock_aws
def test_iot_get_statistics():
    client = boto3.client("iot", region_name="us-east-1")
    # Create a thing so count > 0
    client.create_thing(thingName="test-thing-1")
    client.create_thing(thingName="test-thing-2")
    resp = client.get_statistics(queryString="thingName:*")
    assert "statistics" in resp
    assert resp["statistics"]["count"] == 2


@mock_aws
def test_iot_get_statistics_empty():
    client = boto3.client("iot", region_name="us-east-1")
    resp = client.get_statistics(queryString="thingName:*")
    assert resp["statistics"]["count"] == 0


@mock_aws
def test_iot_get_v2_logging_options():
    client = boto3.client("iot", region_name="us-east-1")
    resp = client.get_v2_logging_options()
    assert "defaultLogLevel" in resp
    assert resp["defaultLogLevel"] == "WARN"
    assert resp["disableAllLogs"] is False


@mock_aws
def test_iot_list_audit_findings():
    client = boto3.client("iot", region_name="us-east-1")
    resp = client.list_audit_findings()
    assert "findings" in resp
    assert resp["findings"] == []


@mock_aws
def test_iot_list_audit_mitigation_actions_tasks():
    client = boto3.client("iot", region_name="us-east-1")
    resp = client.list_audit_mitigation_actions_tasks(
        startTime="2024-01-01T00:00:00Z",
        endTime="2024-12-31T23:59:59Z",
    )
    assert "tasks" in resp
    assert resp["tasks"] == []


@mock_aws
def test_iot_list_audit_suppressions():
    client = boto3.client("iot", region_name="us-east-1")
    resp = client.list_audit_suppressions()
    assert "suppressions" in resp
    assert resp["suppressions"] == []


@mock_aws
def test_iot_list_audit_tasks():
    client = boto3.client("iot", region_name="us-east-1")
    resp = client.list_audit_tasks(
        startTime="2024-01-01T00:00:00Z",
        endTime="2024-12-31T23:59:59Z",
    )
    assert "tasks" in resp
    assert resp["tasks"] == []


@mock_aws
def test_iot_list_detect_mitigation_actions_executions():
    client = boto3.client("iot", region_name="us-east-1")
    resp = client.list_detect_mitigation_actions_executions()
    assert "actionsExecutions" in resp
    assert resp["actionsExecutions"] == []


@mock_aws
def test_iot_list_detect_mitigation_actions_tasks():
    client = boto3.client("iot", region_name="us-east-1")
    resp = client.list_detect_mitigation_actions_tasks(
        startTime="2024-01-01T00:00:00Z",
        endTime="2024-12-31T23:59:59Z",
    )
    assert "tasks" in resp
    assert resp["tasks"] == []


@mock_aws
def test_iot_get_topic_rule_destination_not_found():
    client = boto3.client("iot", region_name="us-east-1")
    with pytest.raises(client.exceptions.ResourceNotFoundException):
        client.get_topic_rule_destination(
            arn="arn:aws:iot:us-east-1:123456789012:ruledestination/http/abc"
        )


# Verify existing ops still work
@mock_aws
def test_iot_list_authorizers():
    client = boto3.client("iot", region_name="us-east-1")
    resp = client.list_authorizers()
    assert "authorizers" in resp


@mock_aws
def test_iot_list_billing_groups():
    client = boto3.client("iot", region_name="us-east-1")
    resp = client.list_billing_groups()
    assert "billingGroups" in resp


@mock_aws
def test_iot_list_custom_metrics():
    client = boto3.client("iot", region_name="us-east-1")
    resp = client.list_custom_metrics()
    assert "metricNames" in resp


@mock_aws
def test_iot_list_dimensions():
    client = boto3.client("iot", region_name="us-east-1")
    resp = client.list_dimensions()
    assert "dimensionNames" in resp


@mock_aws
def test_iot_list_fleet_metrics():
    client = boto3.client("iot", region_name="us-east-1")
    resp = client.list_fleet_metrics()
    assert "fleetMetrics" in resp


@mock_aws
def test_iot_list_job_templates():
    client = boto3.client("iot", region_name="us-east-1")
    resp = client.list_job_templates()
    assert "jobTemplates" in resp


@mock_aws
def test_iot_list_attached_policies():
    client = boto3.client("iot", region_name="us-east-1")
    # Create a certificate to use as target
    cert_resp = client.create_keys_and_certificate(setAsActive=True)
    cert_arn = cert_resp["certificateArn"]
    resp = client.list_attached_policies(target=cert_arn)
    assert "policies" in resp


# === Glue Tests ===


@mock_aws
def test_glue_list_schemas_empty():
    client = boto3.client("glue", region_name="us-east-1")
    resp = client.list_schemas()
    assert "Schemas" in resp
    assert resp["Schemas"] == []


@mock_aws
def test_glue_list_schemas_with_data():
    client = boto3.client("glue", region_name="us-east-1")
    client.create_registry(RegistryName="test-registry")
    client.create_schema(
        RegistryId={"RegistryName": "test-registry"},
        SchemaName="test-schema",
        DataFormat="AVRO",
        Compatibility="NONE",
        SchemaDefinition='{"type": "record", "name": "Test", "fields": []}',
    )
    resp = client.list_schemas()
    assert len(resp["Schemas"]) == 1
    assert resp["Schemas"][0]["SchemaName"] == "test-schema"


@mock_aws
def test_glue_list_schema_versions():
    client = boto3.client("glue", region_name="us-east-1")
    client.create_registry(RegistryName="test-registry")
    client.create_schema(
        RegistryId={"RegistryName": "test-registry"},
        SchemaName="test-schema",
        DataFormat="AVRO",
        Compatibility="NONE",
        SchemaDefinition='{"type": "record", "name": "Test", "fields": []}',
    )
    resp = client.list_schema_versions(
        SchemaId={"RegistryName": "test-registry", "SchemaName": "test-schema"}
    )
    assert "Schemas" in resp


@mock_aws
def test_glue_list_dev_endpoints():
    client = boto3.client("glue", region_name="us-east-1")
    resp = client.list_dev_endpoints()
    assert "DevEndpointNames" in resp
    assert resp["DevEndpointNames"] == []


@mock_aws
def test_glue_list_ml_transforms():
    client = boto3.client("glue", region_name="us-east-1")
    resp = client.list_ml_transforms()
    assert "TransformIds" in resp
    assert resp["TransformIds"] == []


@mock_aws
def test_glue_search_tables_empty():
    client = boto3.client("glue", region_name="us-east-1")
    resp = client.search_tables()
    assert "TableList" in resp
    assert resp["TableList"] == []


@mock_aws
def test_glue_search_tables_with_data():
    client = boto3.client("glue", region_name="us-east-1")
    client.create_database(DatabaseInput={"Name": "test-db"})
    client.create_table(
        DatabaseName="test-db",
        TableInput={
            "Name": "test-table",
            "StorageDescriptor": {
                "Columns": [{"Name": "col1", "Type": "string"}],
                "Location": "s3://bucket/key",
                "InputFormat": "org.apache.hadoop.mapred.TextInputFormat",
                "OutputFormat": "org.apache.hadoop.hive.ql.io.HiveIgnoreKeyTextOutputFormat",
                "SerdeInfo": {"SerializationLibrary": "org.apache.hadoop.hive.serde2.lazy.LazySimpleSerDe"},
            },
        },
    )
    resp = client.search_tables()
    assert len(resp["TableList"]) == 1
    assert resp["TableList"][0]["Name"] == "test-table"


@mock_aws
def test_glue_search_tables_with_text():
    client = boto3.client("glue", region_name="us-east-1")
    client.create_database(DatabaseInput={"Name": "test-db"})
    for name in ["alpha-table", "beta-table", "gamma"]:
        client.create_table(
            DatabaseName="test-db",
            TableInput={
                "Name": name,
                "StorageDescriptor": {
                    "Columns": [{"Name": "col1", "Type": "string"}],
                    "Location": "s3://bucket/key",
                    "InputFormat": "org.apache.hadoop.mapred.TextInputFormat",
                    "OutputFormat": "org.apache.hadoop.hive.ql.io.HiveIgnoreKeyTextOutputFormat",
                    "SerdeInfo": {"SerializationLibrary": "org.apache.hadoop.hive.serde2.lazy.LazySimpleSerDe"},
                },
            },
        )
    resp = client.search_tables(SearchText="table")
    assert len(resp["TableList"]) == 2


@mock_aws
def test_glue_list_statements():
    client = boto3.client("glue", region_name="us-east-1")
    # Create a session first
    session_resp = client.create_session(
        Id="test-session",
        Role="arn:aws:iam::123456789012:role/test",
        Command={"Name": "glueetl", "PythonVersion": "3"},
    )
    resp = client.list_statements(SessionId="test-session")
    assert "Statements" in resp
    assert resp["Statements"] == []


@mock_aws
def test_glue_list_custom_entity_types():
    client = boto3.client("glue", region_name="us-east-1")
    resp = client.list_custom_entity_types()
    assert "CustomEntityTypes" in resp
    assert resp["CustomEntityTypes"] == []


@mock_aws
def test_glue_list_column_statistics_task_runs():
    client = boto3.client("glue", region_name="us-east-1")
    resp = client.list_column_statistics_task_runs()
    assert "ColumnStatisticsTaskRunIds" in resp
    assert resp["ColumnStatisticsTaskRunIds"] == []


@mock_aws
def test_glue_list_data_quality_results():
    client = boto3.client("glue", region_name="us-east-1")
    resp = client.list_data_quality_results()
    assert "Results" in resp
    assert resp["Results"] == []


@mock_aws
def test_glue_list_data_quality_rule_recommendation_runs():
    client = boto3.client("glue", region_name="us-east-1")
    resp = client.list_data_quality_rule_recommendation_runs()
    assert "Runs" in resp
    assert resp["Runs"] == []


@mock_aws
def test_glue_list_data_quality_ruleset_evaluation_runs():
    client = boto3.client("glue", region_name="us-east-1")
    resp = client.list_data_quality_ruleset_evaluation_runs()
    assert "Runs" in resp
    assert resp["Runs"] == []


@mock_aws
def test_glue_list_registries():
    """Verify existing list_registries still works."""
    client = boto3.client("glue", region_name="us-east-1")
    resp = client.list_registries()
    assert "Registries" in resp


@mock_aws
def test_glue_list_crawlers():
    """Verify existing list_crawlers still works."""
    client = boto3.client("glue", region_name="us-east-1")
    resp = client.list_crawlers()
    assert "CrawlerNames" in resp


@mock_aws
def test_glue_list_jobs():
    """Verify existing list_jobs still works."""
    client = boto3.client("glue", region_name="us-east-1")
    resp = client.list_jobs()
    assert "JobNames" in resp


@mock_aws
def test_glue_list_triggers():
    """Verify existing list_triggers still works."""
    client = boto3.client("glue", region_name="us-east-1")
    resp = client.list_triggers()
    assert "TriggerNames" in resp


@mock_aws
def test_glue_list_workflows():
    """Verify existing list_workflows still works."""
    client = boto3.client("glue", region_name="us-east-1")
    resp = client.list_workflows()
    assert "Workflows" in resp


@mock_aws
def test_glue_list_sessions():
    """Verify existing list_sessions still works."""
    client = boto3.client("glue", region_name="us-east-1")
    resp = client.list_sessions()
    assert "Sessions" in resp


@mock_aws
def test_glue_list_blueprints():
    """Verify existing list_blueprints still works."""
    client = boto3.client("glue", region_name="us-east-1")
    resp = client.list_blueprints()
    assert "Blueprints" in resp


@mock_aws
def test_glue_list_data_quality_rulesets():
    """Verify existing list_data_quality_rulesets still works."""
    client = boto3.client("glue", region_name="us-east-1")
    resp = client.list_data_quality_rulesets()
    assert "Rulesets" in resp
