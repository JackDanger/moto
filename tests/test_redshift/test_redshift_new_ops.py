"""Tests for newly implemented Redshift operations."""
import json

import boto3
import pytest
from moto import mock_aws


@mock_aws
def test_event_subscription_crud():
    client = boto3.client("redshift", region_name="us-east-1")

    # Create
    resp = client.create_event_subscription(
        SubscriptionName="test-sub",
        SnsTopicArn="arn:aws:sns:us-east-1:123456789012:my-topic",
        SourceType="cluster",
        Severity="ERROR",
        Enabled=True,
    )
    sub = resp["EventSubscription"]
    assert sub["CustSubscriptionId"] == "test-sub"
    assert sub["SnsTopicArn"] == "arn:aws:sns:us-east-1:123456789012:my-topic"
    assert sub["SourceType"] == "cluster"
    assert sub["Severity"] == "ERROR"
    assert sub["Enabled"] is True
    assert sub["Status"] == "active"

    # Describe all
    resp = client.describe_event_subscriptions()
    assert len(resp["EventSubscriptionsList"]) == 1
    assert resp["EventSubscriptionsList"][0]["CustSubscriptionId"] == "test-sub"

    # Describe by name
    resp = client.describe_event_subscriptions(SubscriptionName="test-sub")
    assert len(resp["EventSubscriptionsList"]) == 1

    # Modify
    resp = client.modify_event_subscription(
        SubscriptionName="test-sub",
        Severity="INFO",
        Enabled=False,
    )
    sub = resp["EventSubscription"]
    assert sub["Severity"] == "INFO"
    assert sub["Enabled"] is False

    # Delete
    client.delete_event_subscription(SubscriptionName="test-sub")
    resp = client.describe_event_subscriptions()
    assert len(resp["EventSubscriptionsList"]) == 0


@mock_aws
def test_event_subscription_not_found():
    client = boto3.client("redshift", region_name="us-east-1")
    with pytest.raises(client.exceptions.SubscriptionNotFoundFault):
        client.describe_event_subscriptions(SubscriptionName="nonexistent")

    with pytest.raises(client.exceptions.SubscriptionNotFoundFault):
        client.delete_event_subscription(SubscriptionName="nonexistent")


@mock_aws
def test_hsm_client_certificate_crud():
    client = boto3.client("redshift", region_name="us-east-1")

    # Create
    resp = client.create_hsm_client_certificate(
        HsmClientCertificateIdentifier="test-cert",
    )
    cert = resp["HsmClientCertificate"]
    assert cert["HsmClientCertificateIdentifier"] == "test-cert"
    assert "BEGIN CERTIFICATE" in cert["HsmClientCertificatePublicKey"]

    # Describe all
    resp = client.describe_hsm_client_certificates()
    assert len(resp["HsmClientCertificates"]) == 1

    # Describe by ID
    resp = client.describe_hsm_client_certificates(
        HsmClientCertificateIdentifier="test-cert"
    )
    assert len(resp["HsmClientCertificates"]) == 1

    # Delete
    client.delete_hsm_client_certificate(
        HsmClientCertificateIdentifier="test-cert"
    )
    resp = client.describe_hsm_client_certificates()
    assert len(resp["HsmClientCertificates"]) == 0


@mock_aws
def test_hsm_client_certificate_already_exists():
    client = boto3.client("redshift", region_name="us-east-1")
    client.create_hsm_client_certificate(
        HsmClientCertificateIdentifier="test-cert"
    )
    with pytest.raises(client.exceptions.HsmClientCertificateAlreadyExistsFault):
        client.create_hsm_client_certificate(
            HsmClientCertificateIdentifier="test-cert"
        )


@mock_aws
def test_hsm_configuration_crud():
    client = boto3.client("redshift", region_name="us-east-1")

    # Create
    resp = client.create_hsm_configuration(
        HsmConfigurationIdentifier="test-config",
        Description="Test HSM config",
        HsmIpAddress="10.0.0.1",
        HsmPartitionName="partition1",
        HsmPartitionPassword="password123",
        HsmServerPublicCertificate="-----BEGIN CERTIFICATE-----\nMOCK\n-----END CERTIFICATE-----",
    )
    config = resp["HsmConfiguration"]
    assert config["HsmConfigurationIdentifier"] == "test-config"
    assert config["Description"] == "Test HSM config"
    assert config["HsmIpAddress"] == "10.0.0.1"
    assert config["HsmPartitionName"] == "partition1"

    # Describe all
    resp = client.describe_hsm_configurations()
    assert len(resp["HsmConfigurations"]) == 1

    # Describe by ID
    resp = client.describe_hsm_configurations(
        HsmConfigurationIdentifier="test-config"
    )
    assert len(resp["HsmConfigurations"]) == 1

    # Delete
    client.delete_hsm_configuration(
        HsmConfigurationIdentifier="test-config"
    )
    resp = client.describe_hsm_configurations()
    assert len(resp["HsmConfigurations"]) == 0


@mock_aws
def test_hsm_configuration_already_exists():
    client = boto3.client("redshift", region_name="us-east-1")
    client.create_hsm_configuration(
        HsmConfigurationIdentifier="test-config",
        Description="d",
        HsmIpAddress="10.0.0.1",
        HsmPartitionName="p",
        HsmPartitionPassword="pw",
        HsmServerPublicCertificate="cert",
    )
    with pytest.raises(client.exceptions.HsmConfigurationAlreadyExistsFault):
        client.create_hsm_configuration(
            HsmConfigurationIdentifier="test-config",
            Description="d",
            HsmIpAddress="10.0.0.1",
            HsmPartitionName="p",
            HsmPartitionPassword="pw",
            HsmServerPublicCertificate="cert",
        )


@mock_aws
def test_endpoint_access_crud():
    client = boto3.client("redshift", region_name="us-east-1")

    # Need a cluster first
    client.create_cluster(
        ClusterIdentifier="test-cluster",
        NodeType="dc2.large",
        MasterUsername="admin",
        MasterUserPassword="Password1!",
    )

    # Create endpoint
    resp = client.create_endpoint_access(
        ClusterIdentifier="test-cluster",
        EndpointName="test-endpoint",
        SubnetGroupName="default",
    )
    assert resp["ClusterIdentifier"] == "test-cluster"
    assert resp["EndpointName"] == "test-endpoint"
    assert resp["EndpointStatus"] == "active"

    # Describe all
    resp = client.describe_endpoint_access()
    assert len(resp["EndpointAccessList"]) == 1

    # Describe by name
    resp = client.describe_endpoint_access(EndpointName="test-endpoint")
    assert len(resp["EndpointAccessList"]) == 1
    assert resp["EndpointAccessList"][0]["EndpointName"] == "test-endpoint"

    # Delete
    resp = client.delete_endpoint_access(EndpointName="test-endpoint")
    assert resp["EndpointStatus"] == "deleting"

    resp = client.describe_endpoint_access()
    assert len(resp["EndpointAccessList"]) == 0


@mock_aws
def test_partner_crud():
    client = boto3.client("redshift", region_name="us-east-1")

    # Need a cluster
    client.create_cluster(
        ClusterIdentifier="test-cluster",
        NodeType="dc2.large",
        MasterUsername="admin",
        MasterUserPassword="Password1!",
    )

    # Add partner
    resp = client.add_partner(
        AccountId="123456789012",
        ClusterIdentifier="test-cluster",
        DatabaseName="dev",
        PartnerName="test-partner",
    )
    assert resp["DatabaseName"] == "dev"
    assert resp["PartnerName"] == "test-partner"

    # Describe
    resp = client.describe_partners(
        AccountId="123456789012",
        ClusterIdentifier="test-cluster",
    )
    assert len(resp["PartnerIntegrationInfoList"]) == 1
    partner = resp["PartnerIntegrationInfoList"][0]
    assert partner["PartnerName"] == "test-partner"
    assert partner["Status"] == "Active"

    # Update status
    resp = client.update_partner_status(
        AccountId="123456789012",
        ClusterIdentifier="test-cluster",
        DatabaseName="dev",
        PartnerName="test-partner",
        Status="Inactive",
        StatusMessage="Paused by admin",
    )
    assert resp["PartnerName"] == "test-partner"

    # Verify update
    resp = client.describe_partners(
        AccountId="123456789012",
        ClusterIdentifier="test-cluster",
    )
    assert resp["PartnerIntegrationInfoList"][0]["Status"] == "Inactive"
    assert resp["PartnerIntegrationInfoList"][0]["StatusMessage"] == "Paused by admin"

    # Delete partner
    resp = client.delete_partner(
        AccountId="123456789012",
        ClusterIdentifier="test-cluster",
        DatabaseName="dev",
        PartnerName="test-partner",
    )
    assert resp["PartnerName"] == "test-partner"

    # Verify deleted
    resp = client.describe_partners(
        AccountId="123456789012",
        ClusterIdentifier="test-cluster",
    )
    assert len(resp["PartnerIntegrationInfoList"]) == 0


@mock_aws
def test_resource_policy_crud():
    client = boto3.client("redshift", region_name="us-east-1")

    arn = "arn:aws:redshift:us-east-1:123456789012:namespace:test-ns"
    policy_doc = json.dumps({"Version": "2012-10-17", "Statement": []})

    # Put
    resp = client.put_resource_policy(
        ResourceArn=arn,
        Policy=policy_doc,
    )
    assert resp["ResourcePolicy"]["ResourceArn"] == arn
    assert resp["ResourcePolicy"]["Policy"] == policy_doc

    # Get
    resp = client.get_resource_policy(ResourceArn=arn)
    assert resp["ResourcePolicy"]["ResourceArn"] == arn
    assert resp["ResourcePolicy"]["Policy"] == policy_doc

    # Delete
    client.delete_resource_policy(ResourceArn=arn)

    # Get after delete should fail
    with pytest.raises(client.exceptions.ResourceNotFoundFault):
        client.get_resource_policy(ResourceArn=arn)


@mock_aws
def test_rotate_encryption_key():
    client = boto3.client("redshift", region_name="us-east-1")
    client.create_cluster(
        ClusterIdentifier="test-cluster",
        NodeType="dc2.large",
        MasterUsername="admin",
        MasterUserPassword="Password1!",
        Encrypted=True,
        KmsKeyId="arn:aws:kms:us-east-1:123456789012:key/test-key",
    )

    resp = client.rotate_encryption_key(ClusterIdentifier="test-cluster")
    assert resp["Cluster"]["ClusterIdentifier"] == "test-cluster"


@mock_aws
def test_cancel_resize():
    client = boto3.client("redshift", region_name="us-east-1")
    client.create_cluster(
        ClusterIdentifier="test-cluster",
        NodeType="dc2.large",
        MasterUsername="admin",
        MasterUserPassword="Password1!",
    )

    resp = client.cancel_resize(ClusterIdentifier="test-cluster")
    assert resp["Status"] == "NONE"
    assert resp["TargetNodeType"] == "dc2.large"


@mock_aws
def test_enable_logging_and_describe():
    client = boto3.client("redshift", region_name="us-east-1")
    client.create_cluster(
        ClusterIdentifier="test-cluster",
        NodeType="dc2.large",
        MasterUsername="admin",
        MasterUserPassword="Password1!",
    )

    # Enable logging
    resp = client.enable_logging(
        ClusterIdentifier="test-cluster",
        LogDestinationType="cloudwatch",
        LogExports=["connectionlog", "userlog"],
    )
    assert resp["LoggingEnabled"] is True

    # Describe logging status
    resp = client.describe_logging_status(ClusterIdentifier="test-cluster")
    assert resp["LoggingEnabled"] is True


@mock_aws
def test_describe_cluster_versions_returns_list():
    client = boto3.client("redshift", region_name="us-east-1")
    resp = client.describe_cluster_versions()
    assert "ClusterVersions" in resp
    assert isinstance(resp["ClusterVersions"], list)


@mock_aws
def test_describe_reserved_nodes_returns_list():
    client = boto3.client("redshift", region_name="us-east-1")
    resp = client.describe_reserved_nodes()
    assert "ReservedNodes" in resp
    assert isinstance(resp["ReservedNodes"], list)


@mock_aws
def test_describe_storage():
    client = boto3.client("redshift", region_name="us-east-1")
    resp = client.describe_storage()
    assert "TotalBackupSizeInMegaBytes" in resp
    assert "TotalProvisionedStorageInMegaBytes" in resp


@mock_aws
def test_describe_authentication_profiles_empty():
    client = boto3.client("redshift", region_name="us-east-1")
    resp = client.describe_authentication_profiles()
    assert "AuthenticationProfiles" in resp
    assert isinstance(resp["AuthenticationProfiles"], list)


@mock_aws
def test_describe_cluster_db_revisions_empty():
    client = boto3.client("redshift", region_name="us-east-1")
    resp = client.describe_cluster_db_revisions()
    assert "ClusterDbRevisions" in resp
    assert isinstance(resp["ClusterDbRevisions"], list)


@mock_aws
def test_describe_data_shares_empty():
    client = boto3.client("redshift", region_name="us-east-1")
    resp = client.describe_data_shares()
    assert "DataShares" in resp
    assert isinstance(resp["DataShares"], list)


@mock_aws
def test_describe_integrations_empty():
    client = boto3.client("redshift", region_name="us-east-1")
    resp = client.describe_integrations()
    assert "Integrations" in resp
    assert isinstance(resp["Integrations"], list)


@mock_aws
def test_get_reserved_node_exchange_configuration_options():
    client = boto3.client("redshift", region_name="us-east-1")
    resp = client.get_reserved_node_exchange_configuration_options(
        ActionType="restore-cluster"
    )
    assert "ReservedNodeConfigurationOptionList" in resp
    assert isinstance(resp["ReservedNodeConfigurationOptionList"], list)
