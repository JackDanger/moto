"""Tests for additional Glue operations:
- CustomEntityType CRUD
- GetDataQualityModel
- DeleteColumnStatisticsForTable
- DeleteColumnStatisticsForPartition
"""

import boto3
import pytest
from botocore.exceptions import ClientError
from moto import mock_aws


@mock_aws
def test_create_and_get_custom_entity_type():
    client = boto3.client("glue", region_name="us-east-1")
    resp = client.create_custom_entity_type(
        Name="test-entity",
        RegexString=r"\d{3}-\d{2}-\d{4}",
        ContextWords=["ssn", "social"],
    )
    assert resp["Name"] == "test-entity"

    got = client.get_custom_entity_type(Name="test-entity")
    assert got["Name"] == "test-entity"
    assert got["RegexString"] == r"\d{3}-\d{2}-\d{4}"
    assert got["ContextWords"] == ["ssn", "social"]


@mock_aws
def test_get_custom_entity_type_not_found():
    client = boto3.client("glue", region_name="us-east-1")
    with pytest.raises(ClientError) as exc:
        client.get_custom_entity_type(Name="nonexistent")
    assert exc.value.response["Error"]["Code"] == "EntityNotFoundException"


@mock_aws
def test_delete_custom_entity_type():
    client = boto3.client("glue", region_name="us-east-1")
    client.create_custom_entity_type(
        Name="to-delete",
        RegexString=r"\d+",
    )
    resp = client.delete_custom_entity_type(Name="to-delete")
    assert resp["Name"] == "to-delete"

    # Verify it's gone
    with pytest.raises(ClientError) as exc:
        client.get_custom_entity_type(Name="to-delete")
    assert exc.value.response["Error"]["Code"] == "EntityNotFoundException"


@mock_aws
def test_delete_custom_entity_type_not_found():
    client = boto3.client("glue", region_name="us-east-1")
    with pytest.raises(ClientError) as exc:
        client.delete_custom_entity_type(Name="nonexistent")
    assert exc.value.response["Error"]["Code"] == "EntityNotFoundException"


@mock_aws
def test_list_custom_entity_types_empty():
    client = boto3.client("glue", region_name="us-east-1")
    resp = client.list_custom_entity_types()
    assert resp["CustomEntityTypes"] == []


@mock_aws
def test_list_custom_entity_types_with_data():
    client = boto3.client("glue", region_name="us-east-1")
    client.create_custom_entity_type(Name="entity1", RegexString=r"\d+")
    client.create_custom_entity_type(Name="entity2", RegexString=r"[a-z]+")
    resp = client.list_custom_entity_types()
    names = [e["Name"] for e in resp["CustomEntityTypes"]]
    assert "entity1" in names
    assert "entity2" in names


@mock_aws
def test_get_data_quality_model_not_found():
    client = boto3.client("glue", region_name="us-east-1")
    with pytest.raises(ClientError) as exc:
        client.get_data_quality_model(ProfileId="fake-profile-id")
    assert exc.value.response["Error"]["Code"] == "EntityNotFoundException"


@mock_aws
def test_delete_column_statistics_for_table():
    client = boto3.client("glue", region_name="us-east-1")
    # Create a database and table first
    client.create_database(DatabaseInput={"Name": "testdb"})
    client.create_table(
        DatabaseName="testdb",
        TableInput={
            "Name": "testtable",
            "StorageDescriptor": {
                "Columns": [{"Name": "col1", "Type": "string"}],
                "InputFormat": "",
                "OutputFormat": "",
                "SerdeInfo": {},
            },
        },
    )
    # Should succeed (no-op since we don't store column stats)
    client.delete_column_statistics_for_table(
        DatabaseName="testdb",
        TableName="testtable",
        ColumnName="col1",
    )


@mock_aws
def test_delete_column_statistics_for_table_missing_table():
    client = boto3.client("glue", region_name="us-east-1")
    client.create_database(DatabaseInput={"Name": "testdb"})
    with pytest.raises(ClientError) as exc:
        client.delete_column_statistics_for_table(
            DatabaseName="testdb",
            TableName="nonexistent",
            ColumnName="col1",
        )
    assert exc.value.response["Error"]["Code"] == "EntityNotFoundException"


@mock_aws
def test_delete_column_statistics_for_partition():
    client = boto3.client("glue", region_name="us-east-1")
    client.create_database(DatabaseInput={"Name": "testdb"})
    client.create_table(
        DatabaseName="testdb",
        TableInput={
            "Name": "testtable",
            "StorageDescriptor": {
                "Columns": [{"Name": "col1", "Type": "string"}],
                "InputFormat": "",
                "OutputFormat": "",
                "SerdeInfo": {},
            },
            "PartitionKeys": [{"Name": "year", "Type": "string"}],
        },
    )
    # Should succeed (no-op)
    client.delete_column_statistics_for_partition(
        DatabaseName="testdb",
        TableName="testtable",
        PartitionValues=["2024"],
        ColumnName="col1",
    )


@mock_aws
def test_delete_column_statistics_for_partition_missing_table():
    client = boto3.client("glue", region_name="us-east-1")
    client.create_database(DatabaseInput={"Name": "testdb"})
    with pytest.raises(ClientError) as exc:
        client.delete_column_statistics_for_partition(
            DatabaseName="testdb",
            TableName="nonexistent",
            PartitionValues=["2024"],
            ColumnName="col1",
        )
    assert exc.value.response["Error"]["Code"] == "EntityNotFoundException"
