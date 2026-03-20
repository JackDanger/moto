import boto3
import pytest
from botocore.exceptions import ClientError

from moto import mock_aws


def create_basic_workgroup(client, name="athena_workgroup"):
    client.create_work_group(
        Name=name,
        Description="Test work group",
        Configuration={
            "ResultConfiguration": {"OutputLocation": "s3://bucket-name/prefix/"}
        },
    )


# --- delete_named_query ---


@mock_aws
def test_delete_named_query():
    client = boto3.client("athena", region_name="us-east-1")
    query_id = client.create_named_query(
        Name="query-name",
        Database="target_db",
        QueryString="SELECT * FROM table1",
    )["NamedQueryId"]

    # Delete should succeed
    resp = client.delete_named_query(NamedQueryId=query_id)
    assert resp["ResponseMetadata"]["HTTPStatusCode"] == 200

    # Verify it's gone from the list
    listed = client.list_named_queries()
    assert query_id not in listed["NamedQueryIds"]


@mock_aws
def test_delete_named_query_nonexistent():
    """Deleting a nonexistent named query should not raise an error (idempotent)."""
    client = boto3.client("athena", region_name="us-east-1")
    resp = client.delete_named_query(NamedQueryId="nonexistent-id")
    assert resp["ResponseMetadata"]["HTTPStatusCode"] == 200


# --- batch_get_named_query ---


@mock_aws
def test_batch_get_named_query():
    client = boto3.client("athena", region_name="us-east-1")
    q1 = client.create_named_query(
        Name="query1", Database="db1", QueryString="SELECT 1"
    )["NamedQueryId"]
    q2 = client.create_named_query(
        Name="query2", Database="db2", QueryString="SELECT 2"
    )["NamedQueryId"]

    resp = client.batch_get_named_query(NamedQueryIds=[q1, q2])
    assert len(resp["NamedQueries"]) == 2
    assert resp["UnprocessedNamedQueryIds"] == []

    names = {nq["Name"] for nq in resp["NamedQueries"]}
    assert names == {"query1", "query2"}


@mock_aws
def test_batch_get_named_query_with_invalid():
    client = boto3.client("athena", region_name="us-east-1")
    q1 = client.create_named_query(
        Name="query1", Database="db1", QueryString="SELECT 1"
    )["NamedQueryId"]

    resp = client.batch_get_named_query(NamedQueryIds=[q1, "nonexistent-id"])
    assert len(resp["NamedQueries"]) == 1
    assert resp["NamedQueries"][0]["Name"] == "query1"
    assert len(resp["UnprocessedNamedQueryIds"]) == 1
    assert resp["UnprocessedNamedQueryIds"][0]["NamedQueryId"] == "nonexistent-id"


# --- batch_get_query_execution ---


@mock_aws
def test_batch_get_query_execution():
    client = boto3.client("athena", region_name="us-east-1")
    create_basic_workgroup(client)
    e1 = client.start_query_execution(
        QueryString="SELECT 1",
        QueryExecutionContext={"Database": "db"},
        ResultConfiguration={"OutputLocation": "s3://bucket/prefix/"},
        WorkGroup="athena_workgroup",
    )["QueryExecutionId"]
    e2 = client.start_query_execution(
        QueryString="SELECT 2",
        QueryExecutionContext={"Database": "db"},
        ResultConfiguration={"OutputLocation": "s3://bucket/prefix/"},
        WorkGroup="athena_workgroup",
    )["QueryExecutionId"]

    resp = client.batch_get_query_execution(QueryExecutionIds=[e1, e2])
    assert len(resp["QueryExecutions"]) == 2
    assert resp["UnprocessedQueryExecutionIds"] == []
    queries = {qe["Query"] for qe in resp["QueryExecutions"]}
    assert queries == {"SELECT 1", "SELECT 2"}


@mock_aws
def test_batch_get_query_execution_with_invalid():
    client = boto3.client("athena", region_name="us-east-1")
    create_basic_workgroup(client)
    e1 = client.start_query_execution(
        QueryString="SELECT 1",
        QueryExecutionContext={"Database": "db"},
        ResultConfiguration={"OutputLocation": "s3://bucket/prefix/"},
        WorkGroup="athena_workgroup",
    )["QueryExecutionId"]

    resp = client.batch_get_query_execution(
        QueryExecutionIds=[e1, "nonexistent-id"]
    )
    assert len(resp["QueryExecutions"]) == 1
    assert len(resp["UnprocessedQueryExecutionIds"]) == 1
    assert (
        resp["UnprocessedQueryExecutionIds"][0]["QueryExecutionId"] == "nonexistent-id"
    )


# --- delete_data_catalog ---


@mock_aws
def test_delete_data_catalog():
    client = boto3.client("athena", region_name="us-east-1")
    client.create_data_catalog(
        Name="test_catalog",
        Type="GLUE",
        Description="Test",
        Parameters={"catalog-id": "123"},
        Tags=[],
    )

    resp = client.delete_data_catalog(Name="test_catalog")
    assert resp["ResponseMetadata"]["HTTPStatusCode"] == 200

    # Verify it's gone
    catalogs = client.list_data_catalogs()
    assert len(catalogs["DataCatalogsSummary"]) == 0


@mock_aws
def test_delete_data_catalog_nonexistent():
    client = boto3.client("athena", region_name="us-east-1")
    with pytest.raises(ClientError) as exc:
        client.delete_data_catalog(Name="nonexistent")
    err = exc.value.response["Error"]
    assert err["Code"] == "InvalidArgumentException"


# --- update_data_catalog ---


@mock_aws
def test_update_data_catalog():
    client = boto3.client("athena", region_name="us-east-1")
    client.create_data_catalog(
        Name="test_catalog",
        Type="GLUE",
        Description="Original",
        Parameters={"catalog-id": "123"},
        Tags=[],
    )

    client.update_data_catalog(
        Name="test_catalog",
        Type="LAMBDA",
        Description="Updated",
        Parameters={"function": "arn:aws:lambda:us-east-1:123:function:my-func"},
    )

    dc = client.get_data_catalog(Name="test_catalog")["DataCatalog"]
    assert dc["Type"] == "LAMBDA"
    assert dc["Description"] == "Updated"
    assert dc["Parameters"]["function"] == "arn:aws:lambda:us-east-1:123:function:my-func"


@mock_aws
def test_update_data_catalog_nonexistent():
    client = boto3.client("athena", region_name="us-east-1")
    with pytest.raises(ClientError) as exc:
        client.update_data_catalog(
            Name="nonexistent", Type="GLUE", Description="test"
        )
    err = exc.value.response["Error"]
    assert err["Code"] == "InvalidArgumentException"


# --- delete_prepared_statement ---


@mock_aws
def test_delete_prepared_statement():
    client = boto3.client("athena", region_name="us-east-1")
    create_basic_workgroup(client)
    client.create_prepared_statement(
        StatementName="test-stmt",
        WorkGroup="athena_workgroup",
        QueryStatement="SELECT * FROM t",
    )

    resp = client.delete_prepared_statement(
        StatementName="test-stmt", WorkGroup="athena_workgroup"
    )
    assert resp["ResponseMetadata"]["HTTPStatusCode"] == 200


@mock_aws
def test_delete_prepared_statement_nonexistent():
    client = boto3.client("athena", region_name="us-east-1")
    create_basic_workgroup(client)
    with pytest.raises(ClientError) as exc:
        client.delete_prepared_statement(
            StatementName="nonexistent", WorkGroup="athena_workgroup"
        )
    err = exc.value.response["Error"]
    assert err["Code"] == "InvalidArgumentException"


# --- batch_get_prepared_statement ---


@mock_aws
def test_batch_get_prepared_statement():
    client = boto3.client("athena", region_name="us-east-1")
    create_basic_workgroup(client)
    client.create_prepared_statement(
        StatementName="stmt1",
        WorkGroup="athena_workgroup",
        QueryStatement="SELECT 1",
    )
    client.create_prepared_statement(
        StatementName="stmt2",
        WorkGroup="athena_workgroup",
        QueryStatement="SELECT 2",
    )

    resp = client.batch_get_prepared_statement(
        PreparedStatementNames=["stmt1", "stmt2"],
        WorkGroup="athena_workgroup",
    )
    assert len(resp["PreparedStatements"]) == 2
    assert resp["UnprocessedPreparedStatementNames"] == []
    names = {ps["StatementName"] for ps in resp["PreparedStatements"]}
    assert names == {"stmt1", "stmt2"}


@mock_aws
def test_batch_get_prepared_statement_with_invalid():
    client = boto3.client("athena", region_name="us-east-1")
    create_basic_workgroup(client)
    client.create_prepared_statement(
        StatementName="stmt1",
        WorkGroup="athena_workgroup",
        QueryStatement="SELECT 1",
    )

    resp = client.batch_get_prepared_statement(
        PreparedStatementNames=["stmt1", "nonexistent"],
        WorkGroup="athena_workgroup",
    )
    assert len(resp["PreparedStatements"]) == 1
    assert len(resp["UnprocessedPreparedStatementNames"]) == 1
    assert (
        resp["UnprocessedPreparedStatementNames"][0]["StatementName"] == "nonexistent"
    )


# --- cancel_capacity_reservation ---


@mock_aws
def test_cancel_capacity_reservation():
    client = boto3.client("athena", region_name="us-east-1")
    client.create_capacity_reservation(
        TargetDpus=100, Name="test-reservation", Tags=[]
    )

    resp = client.cancel_capacity_reservation(Name="test-reservation")
    assert resp["ResponseMetadata"]["HTTPStatusCode"] == 200

    # After cancel, target DPUs should be 0
    cr = client.get_capacity_reservation(Name="test-reservation")
    assert cr["CapacityReservation"]["TargetDpus"] == 0


@mock_aws
def test_cancel_capacity_reservation_nonexistent():
    client = boto3.client("athena", region_name="us-east-1")
    with pytest.raises(ClientError) as exc:
        client.cancel_capacity_reservation(Name="nonexistent")
    err = exc.value.response["Error"]
    assert err["Code"] == "InvalidArgumentException"


# --- delete_capacity_reservation ---


@mock_aws
def test_delete_capacity_reservation():
    client = boto3.client("athena", region_name="us-east-1")
    client.create_capacity_reservation(
        TargetDpus=100, Name="test-reservation", Tags=[]
    )

    resp = client.delete_capacity_reservation(Name="test-reservation")
    assert resp["ResponseMetadata"]["HTTPStatusCode"] == 200

    # Verify it's gone
    reservations = client.list_capacity_reservations()
    assert len(reservations["CapacityReservations"]) == 0


@mock_aws
def test_delete_capacity_reservation_nonexistent():
    client = boto3.client("athena", region_name="us-east-1")
    with pytest.raises(ClientError) as exc:
        client.delete_capacity_reservation(Name="nonexistent")
    err = exc.value.response["Error"]
    assert err["Code"] == "InvalidArgumentException"


# --- list_named_queries pagination fix ---


@mock_aws
def test_list_named_queries_pagination():
    """Regression test: list_named_queries used to return string IDs which broke pagination."""
    client = boto3.client("athena", region_name="us-east-1")
    create_basic_workgroup(client)

    # Create 3 named queries
    ids = []
    for i in range(3):
        q = client.create_named_query(
            Name=f"query-{i}",
            Database="db",
            QueryString=f"SELECT {i}",
            WorkGroup="athena_workgroup",
        )
        ids.append(q["NamedQueryId"])

    # Paginate with MaxResults=2 to trigger pagination
    resp1 = client.list_named_queries(WorkGroup="athena_workgroup", MaxResults=2)
    assert len(resp1["NamedQueryIds"]) == 2
    assert resp1["NextToken"] is not None

    # Get second page
    resp2 = client.list_named_queries(
        WorkGroup="athena_workgroup", MaxResults=2, NextToken=resp1["NextToken"]
    )
    assert len(resp2["NamedQueryIds"]) == 1

    # All IDs should be accounted for
    all_ids = set(resp1["NamedQueryIds"]) | set(resp2["NamedQueryIds"])
    assert all_ids == set(ids)
