"""Tests for newly implemented DS operations.

Tests conditional forwarders, snapshots, event topics, IP routes,
certificates, RADIUS, client authentication, computer, and reset password.
"""

import boto3
import pytest
from botocore.exceptions import ClientError

from moto import mock_aws

from .test_ds_microsoft_ad import create_test_microsoft_ad
from .test_ds_simple_ad_directory import TEST_REGION, create_test_directory


# --- Conditional Forwarder Tests ---


@mock_aws
def test_create_conditional_forwarder():
    client = boto3.client("ds", region_name=TEST_REGION)
    ec2_client = boto3.client("ec2", region_name=TEST_REGION)
    directory_id = create_test_directory(client, ec2_client)

    client.create_conditional_forwarder(
        DirectoryId=directory_id,
        RemoteDomainName="example.com",
        DnsIpAddrs=["10.0.0.1", "10.0.0.2"],
    )

    result = client.describe_conditional_forwarders(DirectoryId=directory_id)
    forwarders = result["ConditionalForwarders"]
    assert len(forwarders) == 1
    assert forwarders[0]["RemoteDomainName"] == "example.com"
    assert forwarders[0]["DnsIpAddrs"] == ["10.0.0.1", "10.0.0.2"]


@mock_aws
def test_create_conditional_forwarder_duplicate():
    client = boto3.client("ds", region_name=TEST_REGION)
    ec2_client = boto3.client("ec2", region_name=TEST_REGION)
    directory_id = create_test_directory(client, ec2_client)

    client.create_conditional_forwarder(
        DirectoryId=directory_id,
        RemoteDomainName="example.com",
        DnsIpAddrs=["10.0.0.1"],
    )
    with pytest.raises(ClientError) as exc:
        client.create_conditional_forwarder(
            DirectoryId=directory_id,
            RemoteDomainName="example.com",
            DnsIpAddrs=["10.0.0.2"],
        )
    assert exc.value.response["Error"]["Code"] == "EntityAlreadyExistsException"


@mock_aws
def test_delete_conditional_forwarder():
    client = boto3.client("ds", region_name=TEST_REGION)
    ec2_client = boto3.client("ec2", region_name=TEST_REGION)
    directory_id = create_test_directory(client, ec2_client)

    client.create_conditional_forwarder(
        DirectoryId=directory_id,
        RemoteDomainName="example.com",
        DnsIpAddrs=["10.0.0.1"],
    )
    client.delete_conditional_forwarder(
        DirectoryId=directory_id,
        RemoteDomainName="example.com",
    )
    result = client.describe_conditional_forwarders(DirectoryId=directory_id)
    assert len(result["ConditionalForwarders"]) == 0


@mock_aws
def test_delete_conditional_forwarder_not_found():
    client = boto3.client("ds", region_name=TEST_REGION)
    ec2_client = boto3.client("ec2", region_name=TEST_REGION)
    directory_id = create_test_directory(client, ec2_client)

    with pytest.raises(ClientError) as exc:
        client.delete_conditional_forwarder(
            DirectoryId=directory_id,
            RemoteDomainName="nonexistent.com",
        )
    assert exc.value.response["Error"]["Code"] == "EntityDoesNotExistException"


@mock_aws
def test_update_conditional_forwarder():
    client = boto3.client("ds", region_name=TEST_REGION)
    ec2_client = boto3.client("ec2", region_name=TEST_REGION)
    directory_id = create_test_directory(client, ec2_client)

    client.create_conditional_forwarder(
        DirectoryId=directory_id,
        RemoteDomainName="example.com",
        DnsIpAddrs=["10.0.0.1"],
    )
    client.update_conditional_forwarder(
        DirectoryId=directory_id,
        RemoteDomainName="example.com",
        DnsIpAddrs=["10.0.0.3", "10.0.0.4"],
    )
    result = client.describe_conditional_forwarders(DirectoryId=directory_id)
    assert result["ConditionalForwarders"][0]["DnsIpAddrs"] == ["10.0.0.3", "10.0.0.4"]


# --- Snapshot Tests ---


@mock_aws
def test_create_snapshot():
    client = boto3.client("ds", region_name=TEST_REGION)
    ec2_client = boto3.client("ec2", region_name=TEST_REGION)
    directory_id = create_test_directory(client, ec2_client)

    result = client.create_snapshot(DirectoryId=directory_id, Name="my-snapshot")
    snapshot_id = result["SnapshotId"]
    assert snapshot_id.startswith("s-")

    snapshots = client.describe_snapshots(DirectoryId=directory_id)["Snapshots"]
    assert len(snapshots) == 1
    assert snapshots[0]["SnapshotId"] == snapshot_id
    assert snapshots[0]["Name"] == "my-snapshot"
    assert snapshots[0]["Status"] == "Completed"
    assert snapshots[0]["DirectoryId"] == directory_id


@mock_aws
def test_delete_snapshot():
    client = boto3.client("ds", region_name=TEST_REGION)
    ec2_client = boto3.client("ec2", region_name=TEST_REGION)
    directory_id = create_test_directory(client, ec2_client)

    result = client.create_snapshot(DirectoryId=directory_id)
    snapshot_id = result["SnapshotId"]

    result = client.delete_snapshot(SnapshotId=snapshot_id)
    assert result["SnapshotId"] == snapshot_id

    snapshots = client.describe_snapshots(DirectoryId=directory_id)["Snapshots"]
    assert len(snapshots) == 0


@mock_aws
def test_delete_snapshot_not_found():
    client = boto3.client("ds", region_name=TEST_REGION)
    with pytest.raises(ClientError) as exc:
        client.delete_snapshot(SnapshotId="s-0000000000")
    assert exc.value.response["Error"]["Code"] == "EntityDoesNotExistException"


@mock_aws
def test_restore_from_snapshot():
    client = boto3.client("ds", region_name=TEST_REGION)
    ec2_client = boto3.client("ec2", region_name=TEST_REGION)
    directory_id = create_test_directory(client, ec2_client)

    result = client.create_snapshot(DirectoryId=directory_id)
    snapshot_id = result["SnapshotId"]

    # Should not raise
    client.restore_from_snapshot(SnapshotId=snapshot_id)


@mock_aws
def test_restore_from_snapshot_not_found():
    client = boto3.client("ds", region_name=TEST_REGION)
    with pytest.raises(ClientError) as exc:
        client.restore_from_snapshot(SnapshotId="s-0000000000")
    assert exc.value.response["Error"]["Code"] == "EntityDoesNotExistException"


@mock_aws
def test_describe_snapshots_by_id():
    client = boto3.client("ds", region_name=TEST_REGION)
    ec2_client = boto3.client("ec2", region_name=TEST_REGION)
    directory_id = create_test_directory(client, ec2_client)

    s1 = client.create_snapshot(DirectoryId=directory_id, Name="snap1")["SnapshotId"]
    s2 = client.create_snapshot(DirectoryId=directory_id, Name="snap2")["SnapshotId"]

    result = client.describe_snapshots(SnapshotIds=[s1])
    assert len(result["Snapshots"]) == 1
    assert result["Snapshots"][0]["SnapshotId"] == s1


# --- Event Topic Tests ---


@mock_aws
def test_register_and_describe_event_topic():
    client = boto3.client("ds", region_name=TEST_REGION)
    ec2_client = boto3.client("ec2", region_name=TEST_REGION)
    directory_id = create_test_directory(client, ec2_client)

    client.register_event_topic(
        DirectoryId=directory_id,
        TopicName="my-topic",
    )

    result = client.describe_event_topics(DirectoryId=directory_id)
    topics = result["EventTopics"]
    assert len(topics) == 1
    assert topics[0]["DirectoryId"] == directory_id
    assert topics[0]["TopicName"] == "my-topic"
    assert topics[0]["Status"] == "Registered"


@mock_aws
def test_deregister_event_topic():
    client = boto3.client("ds", region_name=TEST_REGION)
    ec2_client = boto3.client("ec2", region_name=TEST_REGION)
    directory_id = create_test_directory(client, ec2_client)

    client.register_event_topic(
        DirectoryId=directory_id,
        TopicName="my-topic",
    )
    client.deregister_event_topic(
        DirectoryId=directory_id,
        TopicName="my-topic",
    )
    result = client.describe_event_topics(DirectoryId=directory_id)
    assert len(result["EventTopics"]) == 0


@mock_aws
def test_deregister_event_topic_not_found():
    client = boto3.client("ds", region_name=TEST_REGION)
    ec2_client = boto3.client("ec2", region_name=TEST_REGION)
    directory_id = create_test_directory(client, ec2_client)

    with pytest.raises(ClientError) as exc:
        client.deregister_event_topic(
            DirectoryId=directory_id,
            TopicName="nonexistent",
        )
    assert exc.value.response["Error"]["Code"] == "EntityDoesNotExistException"


# --- IP Routes Tests ---


@mock_aws
def test_add_and_list_ip_routes():
    client = boto3.client("ds", region_name=TEST_REGION)
    ec2_client = boto3.client("ec2", region_name=TEST_REGION)
    directory_id = create_test_directory(client, ec2_client)

    client.add_ip_routes(
        DirectoryId=directory_id,
        IpRoutes=[
            {"CidrIp": "10.24.34.0/24", "Description": "Route 1"},
            {"CidrIp": "10.24.35.0/24", "Description": "Route 2"},
        ],
    )

    result = client.list_ip_routes(DirectoryId=directory_id)
    routes = result["IpRoutesInfo"]
    assert len(routes) == 2
    cidrs = sorted([r["CidrIp"] for r in routes])
    assert cidrs == ["10.24.34.0/24", "10.24.35.0/24"]


@mock_aws
def test_remove_ip_routes():
    client = boto3.client("ds", region_name=TEST_REGION)
    ec2_client = boto3.client("ec2", region_name=TEST_REGION)
    directory_id = create_test_directory(client, ec2_client)

    client.add_ip_routes(
        DirectoryId=directory_id,
        IpRoutes=[{"CidrIp": "10.24.34.0/24", "Description": "Route 1"}],
    )
    client.remove_ip_routes(
        DirectoryId=directory_id,
        CidrIps=["10.24.34.0/24"],
    )
    result = client.list_ip_routes(DirectoryId=directory_id)
    assert len(result["IpRoutesInfo"]) == 0


@mock_aws
def test_remove_ip_routes_not_found():
    client = boto3.client("ds", region_name=TEST_REGION)
    ec2_client = boto3.client("ec2", region_name=TEST_REGION)
    directory_id = create_test_directory(client, ec2_client)

    with pytest.raises(ClientError) as exc:
        client.remove_ip_routes(
            DirectoryId=directory_id,
            CidrIps=["192.168.1.0/24"],
        )
    assert exc.value.response["Error"]["Code"] == "EntityDoesNotExistException"


@mock_aws
def test_add_ip_routes_duplicate():
    client = boto3.client("ds", region_name=TEST_REGION)
    ec2_client = boto3.client("ec2", region_name=TEST_REGION)
    directory_id = create_test_directory(client, ec2_client)

    client.add_ip_routes(
        DirectoryId=directory_id,
        IpRoutes=[{"CidrIp": "10.24.34.0/24", "Description": "Route 1"}],
    )
    with pytest.raises(ClientError) as exc:
        client.add_ip_routes(
            DirectoryId=directory_id,
            IpRoutes=[{"CidrIp": "10.24.34.0/24", "Description": "Route 1 dup"}],
        )
    assert exc.value.response["Error"]["Code"] == "EntityAlreadyExistsException"


# --- Certificate Tests ---


@mock_aws
def test_register_and_list_certificates():
    client = boto3.client("ds", region_name=TEST_REGION)
    ec2_client = boto3.client("ec2", region_name=TEST_REGION)
    directory_id = create_test_microsoft_ad(client, ec2_client)

    result = client.register_certificate(
        DirectoryId=directory_id,
        CertificateData="-----BEGIN CERTIFICATE-----\nMIIC...\n-----END CERTIFICATE-----",
        Type="ClientCertAuth",
    )
    cert_id = result["CertificateId"]
    assert cert_id.startswith("c-")

    certs = client.list_certificates(DirectoryId=directory_id)["CertificatesInfo"]
    assert len(certs) == 1
    assert certs[0]["CertificateId"] == cert_id
    assert certs[0]["State"] == "Registered"


@mock_aws
def test_describe_certificate():
    client = boto3.client("ds", region_name=TEST_REGION)
    ec2_client = boto3.client("ec2", region_name=TEST_REGION)
    directory_id = create_test_microsoft_ad(client, ec2_client)

    result = client.register_certificate(
        DirectoryId=directory_id,
        CertificateData="-----BEGIN CERTIFICATE-----\nMIIC...\n-----END CERTIFICATE-----",
    )
    cert_id = result["CertificateId"]

    cert = client.describe_certificate(
        DirectoryId=directory_id,
        CertificateId=cert_id,
    )["Certificate"]
    assert cert["CertificateId"] == cert_id
    assert cert["State"] == "Registered"


@mock_aws
def test_deregister_certificate():
    client = boto3.client("ds", region_name=TEST_REGION)
    ec2_client = boto3.client("ec2", region_name=TEST_REGION)
    directory_id = create_test_microsoft_ad(client, ec2_client)

    result = client.register_certificate(
        DirectoryId=directory_id,
        CertificateData="-----BEGIN CERTIFICATE-----\nMIIC...\n-----END CERTIFICATE-----",
    )
    cert_id = result["CertificateId"]

    client.deregister_certificate(DirectoryId=directory_id, CertificateId=cert_id)
    certs = client.list_certificates(DirectoryId=directory_id)["CertificatesInfo"]
    assert len(certs) == 0


@mock_aws
def test_deregister_certificate_not_found():
    client = boto3.client("ds", region_name=TEST_REGION)
    ec2_client = boto3.client("ec2", region_name=TEST_REGION)
    directory_id = create_test_microsoft_ad(client, ec2_client)

    with pytest.raises(ClientError) as exc:
        client.deregister_certificate(
            DirectoryId=directory_id,
            CertificateId="c-0000000000",
        )
    assert exc.value.response["Error"]["Code"] == "EntityDoesNotExistException"


# --- RADIUS Tests ---


@mock_aws
def test_enable_and_disable_radius():
    client = boto3.client("ds", region_name=TEST_REGION)
    ec2_client = boto3.client("ec2", region_name=TEST_REGION)
    directory_id = create_test_directory(client, ec2_client)

    radius_settings = {
        "RadiusServers": ["10.0.0.100"],
        "RadiusPort": 1812,
        "RadiusTimeout": 10,
        "RadiusRetries": 3,
        "SharedSecret": "MySecret123!",
        "AuthenticationProtocol": "PAP",
        "DisplayLabel": "Test RADIUS",
        "UseSameUsername": True,
    }
    client.enable_radius(
        DirectoryId=directory_id,
        RadiusSettings=radius_settings,
    )
    # Should not raise
    client.disable_radius(DirectoryId=directory_id)


@mock_aws
def test_update_radius():
    client = boto3.client("ds", region_name=TEST_REGION)
    ec2_client = boto3.client("ec2", region_name=TEST_REGION)
    directory_id = create_test_directory(client, ec2_client)

    radius_settings = {
        "RadiusServers": ["10.0.0.100"],
        "RadiusPort": 1812,
        "RadiusTimeout": 10,
        "RadiusRetries": 3,
        "SharedSecret": "MySecret123!",
        "AuthenticationProtocol": "PAP",
        "DisplayLabel": "Test RADIUS",
        "UseSameUsername": True,
    }
    client.enable_radius(
        DirectoryId=directory_id,
        RadiusSettings=radius_settings,
    )
    # Update with different settings
    radius_settings["RadiusPort"] = 1813
    client.update_radius(
        DirectoryId=directory_id,
        RadiusSettings=radius_settings,
    )


@mock_aws
def test_update_radius_not_enabled():
    client = boto3.client("ds", region_name=TEST_REGION)
    ec2_client = boto3.client("ec2", region_name=TEST_REGION)
    directory_id = create_test_directory(client, ec2_client)

    with pytest.raises(ClientError) as exc:
        client.update_radius(
            DirectoryId=directory_id,
            RadiusSettings={
                "RadiusServers": ["10.0.0.100"],
                "RadiusPort": 1812,
                "RadiusTimeout": 10,
                "RadiusRetries": 3,
                "SharedSecret": "MySecret123!",
                "AuthenticationProtocol": "PAP",
                "DisplayLabel": "Test RADIUS",
                "UseSameUsername": True,
            },
        )
    assert exc.value.response["Error"]["Code"] == "EntityDoesNotExistException"


# --- Client Authentication Tests ---


@mock_aws
def test_enable_and_disable_client_authentication():
    client = boto3.client("ds", region_name=TEST_REGION)
    ec2_client = boto3.client("ec2", region_name=TEST_REGION)
    directory_id = create_test_microsoft_ad(client, ec2_client)

    client.enable_client_authentication(
        DirectoryId=directory_id,
        Type="SmartCard",
    )
    settings = client.describe_client_authentication_settings(
        DirectoryId=directory_id,
    )["ClientAuthenticationSettingsInfo"]
    assert len(settings) == 1
    assert settings[0]["Type"] == "SmartCard"
    assert settings[0]["Status"] == "Enabled"

    client.disable_client_authentication(
        DirectoryId=directory_id,
        Type="SmartCard",
    )
    settings = client.describe_client_authentication_settings(
        DirectoryId=directory_id,
    )["ClientAuthenticationSettingsInfo"]
    assert len(settings) == 0


@mock_aws
def test_enable_client_authentication_not_microsoft_ad():
    client = boto3.client("ds", region_name=TEST_REGION)
    ec2_client = boto3.client("ec2", region_name=TEST_REGION)
    directory_id = create_test_directory(client, ec2_client)

    with pytest.raises(ClientError) as exc:
        client.enable_client_authentication(
            DirectoryId=directory_id,
            Type="SmartCard",
        )
    assert exc.value.response["Error"]["Code"] == "UnsupportedOperationException"


# --- Computer Tests ---


@mock_aws
def test_create_computer():
    client = boto3.client("ds", region_name=TEST_REGION)
    ec2_client = boto3.client("ec2", region_name=TEST_REGION)
    directory_id = create_test_directory(client, ec2_client)

    result = client.create_computer(
        DirectoryId=directory_id,
        ComputerName="mycomputer",
        Password="MyComp@ss1!",
        ComputerAttributes=[
            {"Name": "department", "Value": "Engineering"},
        ],
    )
    computer = result["Computer"]
    assert computer["ComputerName"] == "mycomputer"
    assert computer["ComputerId"].startswith("comp-")
    assert len(computer["ComputerAttributes"]) == 1


# --- Reset User Password Tests ---


@mock_aws
def test_reset_user_password():
    client = boto3.client("ds", region_name=TEST_REGION)
    ec2_client = boto3.client("ec2", region_name=TEST_REGION)
    directory_id = create_test_directory(client, ec2_client)

    # Should not raise
    client.reset_user_password(
        DirectoryId=directory_id,
        UserName="testuser",
        NewPassword="NewP@ssw0rd!",
    )


@mock_aws
def test_reset_user_password_invalid_directory():
    client = boto3.client("ds", region_name=TEST_REGION)
    with pytest.raises(ClientError) as exc:
        client.reset_user_password(
            DirectoryId="d-0000000000",
            UserName="testuser",
            NewPassword="NewP@ssw0rd!",
        )
    assert exc.value.response["Error"]["Code"] == "EntityDoesNotExistException"
