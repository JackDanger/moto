import boto3
import pytest
from botocore.exceptions import ClientError

from moto import mock_aws


@mock_aws
def test_delete_configuration():
    client = boto3.client("mq", region_name="us-east-1")
    config_id = client.create_configuration(
        EngineType="ACTIVEMQ", EngineVersion="5.17.6", Name="myconfig"
    )["Id"]

    resp = client.delete_configuration(ConfigurationId=config_id)

    assert resp["ConfigurationId"] == config_id

    # Verify it's actually gone
    with pytest.raises(ClientError) as exc:
        client.describe_configuration(ConfigurationId=config_id)
    assert exc.value.response["Error"]["Code"] == "NotFoundException"


@mock_aws
def test_delete_configuration_unknown():
    client = boto3.client("mq", region_name="us-east-1")

    with pytest.raises(ClientError) as exc:
        client.delete_configuration(ConfigurationId="c-unknown")
    assert exc.value.response["Error"]["Code"] == "NotFoundException"


@mock_aws
def test_list_configuration_revisions():
    client = boto3.client("mq", region_name="us-east-1")
    config_id = client.create_configuration(
        EngineType="ACTIVEMQ", EngineVersion="5.17.6", Name="myconfig"
    )["Id"]

    # Update to create a second revision
    client.update_configuration(
        ConfigurationId=config_id,
        Data="dXBkYXRlZA==",
        Description="second revision",
    )

    resp = client.list_configuration_revisions(ConfigurationId=config_id)

    assert resp["ConfigurationId"] == config_id
    assert len(resp["Revisions"]) == 2
    assert resp["Revisions"][0]["Revision"] == 1
    assert resp["Revisions"][1]["Revision"] == 2
    assert resp["Revisions"][1]["Description"] == "second revision"


@mock_aws
def test_list_configuration_revisions_unknown():
    client = boto3.client("mq", region_name="us-east-1")

    with pytest.raises(ClientError) as exc:
        client.list_configuration_revisions(ConfigurationId="c-unknown")
    assert exc.value.response["Error"]["Code"] == "NotFoundException"


@mock_aws
def test_describe_broker_engine_types():
    client = boto3.client("mq", region_name="us-east-1")

    resp = client.describe_broker_engine_types()

    assert "BrokerEngineTypes" in resp
    engine_types = resp["BrokerEngineTypes"]
    assert len(engine_types) >= 2

    type_names = [et["EngineType"] for et in engine_types]
    assert "ACTIVEMQ" in type_names
    assert "RABBITMQ" in type_names

    for et in engine_types:
        assert len(et["EngineVersions"]) > 0
        for ev in et["EngineVersions"]:
            assert "Name" in ev


@mock_aws
def test_describe_broker_instance_options():
    client = boto3.client("mq", region_name="us-east-1")

    resp = client.describe_broker_instance_options()

    assert "BrokerInstanceOptions" in resp
    options = resp["BrokerInstanceOptions"]
    assert len(options) > 0

    for opt in options:
        assert "AvailabilityZones" in opt
        assert "EngineType" in opt
        assert "HostInstanceType" in opt
        assert "StorageType" in opt
        assert "SupportedDeploymentModes" in opt
        assert "SupportedEngineVersions" in opt

    # Verify both engine types present
    engine_types = {opt["EngineType"] for opt in options}
    assert "ACTIVEMQ" in engine_types
    assert "RABBITMQ" in engine_types


@mock_aws
def test_promote():
    client = boto3.client("mq", region_name="us-east-1")
    broker_id = client.create_broker(
        AutoMinorVersionUpgrade=False,
        BrokerName="testbroker",
        DeploymentMode="ACTIVE_STANDBY_MULTI_AZ",
        EngineType="ACTIVEMQ",
        EngineVersion="5.17.6",
        HostInstanceType="mq.m5.large",
        PubliclyAccessible=True,
        Users=[{"Username": "admin", "Password": "adm1n"}],
    )["BrokerId"]

    resp = client.promote(BrokerId=broker_id, Mode="SWITCHOVER")

    assert resp["BrokerId"] == broker_id


@mock_aws
def test_promote_unknown_broker():
    client = boto3.client("mq", region_name="us-east-1")

    with pytest.raises(ClientError) as exc:
        client.promote(BrokerId="unknown", Mode="SWITCHOVER")
    assert exc.value.response["Error"]["Code"] == "NotFoundException"
