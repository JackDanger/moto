import boto3
import pytest
from botocore.exceptions import ClientError

from moto import mock_aws


def _create_service(client):
    """Helper: create an HTTP namespace and service, return service_id."""
    operation_id = client.create_http_namespace(Name="mynamespace")["OperationId"]
    namespace_id = client.get_operation(OperationId=operation_id)["Operation"][
        "Targets"
    ]["NAMESPACE"]
    service_id = client.create_service(Name="my service", NamespaceId=namespace_id)[
        "Service"
    ]["Id"]
    return service_id


@mock_aws
def test_get_service_attributes_empty():
    client = boto3.client("servicediscovery", region_name="us-east-1")
    service_id = _create_service(client)

    resp = client.get_service_attributes(ServiceId=service_id)

    assert "ServiceAttributes" in resp
    assert resp["ServiceAttributes"]["Attributes"] == {}
    assert "ServiceArn" in resp["ServiceAttributes"]


@mock_aws
def test_update_and_get_service_attributes():
    client = boto3.client("servicediscovery", region_name="us-east-1")
    service_id = _create_service(client)

    client.update_service_attributes(
        ServiceId=service_id,
        Attributes={"port": "8080", "protocol": "tcp"},
    )

    resp = client.get_service_attributes(ServiceId=service_id)
    assert resp["ServiceAttributes"]["Attributes"] == {
        "port": "8080",
        "protocol": "tcp",
    }


@mock_aws
def test_update_service_attributes_overwrites():
    client = boto3.client("servicediscovery", region_name="us-east-1")
    service_id = _create_service(client)

    client.update_service_attributes(
        ServiceId=service_id,
        Attributes={"port": "8080"},
    )
    client.update_service_attributes(
        ServiceId=service_id,
        Attributes={"port": "9090", "host": "localhost"},
    )

    resp = client.get_service_attributes(ServiceId=service_id)
    assert resp["ServiceAttributes"]["Attributes"] == {
        "port": "9090",
        "host": "localhost",
    }


@mock_aws
def test_delete_service_attributes():
    client = boto3.client("servicediscovery", region_name="us-east-1")
    service_id = _create_service(client)

    client.update_service_attributes(
        ServiceId=service_id,
        Attributes={"port": "8080", "protocol": "tcp", "host": "localhost"},
    )

    client.delete_service_attributes(
        ServiceId=service_id,
        Attributes=["port", "protocol"],
    )

    resp = client.get_service_attributes(ServiceId=service_id)
    assert resp["ServiceAttributes"]["Attributes"] == {"host": "localhost"}


@mock_aws
def test_delete_service_attributes_nonexistent_key():
    client = boto3.client("servicediscovery", region_name="us-east-1")
    service_id = _create_service(client)

    # Should not raise even if key doesn't exist
    client.delete_service_attributes(
        ServiceId=service_id,
        Attributes=["nonexistent"],
    )

    resp = client.get_service_attributes(ServiceId=service_id)
    assert resp["ServiceAttributes"]["Attributes"] == {}


@mock_aws
def test_get_service_attributes_unknown_service():
    client = boto3.client("servicediscovery", region_name="us-east-1")

    with pytest.raises(ClientError) as exc:
        client.get_service_attributes(ServiceId="srv-unknown")
    err = exc.value.response["Error"]
    assert err["Code"] == "ServiceNotFound"


@mock_aws
def test_update_service_attributes_unknown_service():
    client = boto3.client("servicediscovery", region_name="us-east-1")

    with pytest.raises(ClientError) as exc:
        client.update_service_attributes(
            ServiceId="srv-unknown",
            Attributes={"key": "value"},
        )
    err = exc.value.response["Error"]
    assert err["Code"] == "ServiceNotFound"


@mock_aws
def test_delete_service_attributes_unknown_service():
    client = boto3.client("servicediscovery", region_name="us-east-1")

    with pytest.raises(ClientError) as exc:
        client.delete_service_attributes(
            ServiceId="srv-unknown",
            Attributes=["key"],
        )
    err = exc.value.response["Error"]
    assert err["Code"] == "ServiceNotFound"
