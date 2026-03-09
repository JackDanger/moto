"""Tests for newly implemented Redshift operations."""

import json

import boto3
import pytest
from botocore.exceptions import ClientError

from moto import mock_aws


def _create_cluster(client, identifier="test-cluster"):
    client.create_cluster(
        DBName="testdb",
        ClusterIdentifier=identifier,
        ClusterType="single-node",
        NodeType="dc2.large",
        MasterUsername="admin",
        MasterUserPassword="Password123",
    )


def _create_snapshot(client, cluster_id="test-cluster", snapshot_id="test-snapshot"):
    return client.create_cluster_snapshot(
        ClusterIdentifier=cluster_id,
        SnapshotIdentifier=snapshot_id,
    )


@mock_aws
def test_copy_cluster_snapshot():
    client = boto3.client("redshift", region_name="us-east-1")
    _create_cluster(client)
    _create_snapshot(client)
    response = client.copy_cluster_snapshot(
        SourceSnapshotIdentifier="test-snapshot",
        TargetSnapshotIdentifier="copied-snapshot",
    )
    snapshot = response["Snapshot"]
    assert snapshot["SnapshotIdentifier"] == "copied-snapshot"
    assert snapshot["ClusterIdentifier"] == "test-cluster"
    assert snapshot["Status"] == "available"


@mock_aws
def test_copy_cluster_snapshot_not_found():
    client = boto3.client("redshift", region_name="us-east-1")
    with pytest.raises(ClientError) as exc:
        client.copy_cluster_snapshot(
            SourceSnapshotIdentifier="nonexistent",
            TargetSnapshotIdentifier="copy",
        )
    assert exc.value.response["Error"]["Code"] == "ClusterSnapshotNotFound"


@mock_aws
def test_authorize_snapshot_access():
    client = boto3.client("redshift", region_name="us-east-1")
    _create_cluster(client)
    _create_snapshot(client)
    response = client.authorize_snapshot_access(
        SnapshotIdentifier="test-snapshot",
        AccountWithRestoreAccess="111122223333",
    )
    snapshot = response["Snapshot"]
    assert snapshot["SnapshotIdentifier"] == "test-snapshot"
    accounts = snapshot.get("AccountsWithRestoreAccess", [])
    assert any(a["AccountId"] == "111122223333" for a in accounts)


@mock_aws
def test_revoke_snapshot_access():
    client = boto3.client("redshift", region_name="us-east-1")
    _create_cluster(client)
    _create_snapshot(client)
    client.authorize_snapshot_access(
        SnapshotIdentifier="test-snapshot",
        AccountWithRestoreAccess="111122223333",
    )
    response = client.revoke_snapshot_access(
        SnapshotIdentifier="test-snapshot",
        AccountWithRestoreAccess="111122223333",
    )
    assert response["Snapshot"]["SnapshotIdentifier"] == "test-snapshot"


@mock_aws
def test_create_scheduled_action():
    client = boto3.client("redshift", region_name="us-east-1")
    response = client.create_scheduled_action(
        ScheduledActionName="test-action",
        TargetAction={
            "ResizeCluster": {
                "ClusterIdentifier": "test-cluster",
                "ClusterType": "multi-node",
                "NodeType": "dc2.large",
                "NumberOfNodes": 2,
            }
        },
        Schedule="at(2025-12-01T00:00:00)",
        IamRole="arn:aws:iam::123456789012:role/TestRole",
        ScheduledActionDescription="Test scheduled action",
        Enable=True,
    )
    assert response["ScheduledActionName"] == "test-action"
    assert response["State"] == "ACTIVE"
    assert response["Schedule"] == "at(2025-12-01T00:00:00)"


@mock_aws
def test_describe_scheduled_actions():
    client = boto3.client("redshift", region_name="us-east-1")
    client.create_scheduled_action(
        ScheduledActionName="action-1",
        TargetAction={"PauseCluster": {"ClusterIdentifier": "c1"}},
        Schedule="at(2025-12-01T00:00:00)",
        IamRole="arn:aws:iam::123456789012:role/TestRole",
    )
    response = client.describe_scheduled_actions()
    assert len(response["ScheduledActions"]) == 1


@mock_aws
def test_delete_scheduled_action():
    client = boto3.client("redshift", region_name="us-east-1")
    client.create_scheduled_action(
        ScheduledActionName="test-action",
        TargetAction={"PauseCluster": {"ClusterIdentifier": "c1"}},
        Schedule="at(2025-12-01T00:00:00)",
        IamRole="arn:aws:iam::123456789012:role/TestRole",
    )
    client.delete_scheduled_action(ScheduledActionName="test-action")
    with pytest.raises(ClientError) as exc:
        client.describe_scheduled_actions(ScheduledActionName="test-action")
    assert "ScheduledActionNotFound" in exc.value.response["Error"]["Code"]


@mock_aws
def test_modify_scheduled_action():
    client = boto3.client("redshift", region_name="us-east-1")
    client.create_scheduled_action(
        ScheduledActionName="test-action",
        TargetAction={"PauseCluster": {"ClusterIdentifier": "c1"}},
        Schedule="at(2025-12-01T00:00:00)",
        IamRole="arn:aws:iam::123456789012:role/TestRole",
        Enable=True,
    )
    response = client.modify_scheduled_action(
        ScheduledActionName="test-action",
        Enable=False,
    )
    assert response["State"] == "DISABLED"


@mock_aws
def test_modify_cluster_iam_roles():
    client = boto3.client("redshift", region_name="us-east-1")
    _create_cluster(client)
    role_arn = "arn:aws:iam::123456789012:role/RedshiftRole"
    response = client.modify_cluster_iam_roles(
        ClusterIdentifier="test-cluster",
        AddIamRoles=[role_arn],
    )
    assert any(r["IamRoleArn"] == role_arn for r in response["Cluster"]["IamRoles"])


@mock_aws
def test_create_authentication_profile():
    client = boto3.client("redshift", region_name="us-east-1")
    content = json.dumps({"AllowDBUserOverride": "1"})
    response = client.create_authentication_profile(
        AuthenticationProfileName="test-profile",
        AuthenticationProfileContent=content,
    )
    assert response["AuthenticationProfileName"] == "test-profile"
    assert response["AuthenticationProfileContent"] == content


@mock_aws
def test_describe_authentication_profiles():
    client = boto3.client("redshift", region_name="us-east-1")
    content = json.dumps({"AllowDBUserOverride": "1"})
    client.create_authentication_profile(
        AuthenticationProfileName="profile-1",
        AuthenticationProfileContent=content,
    )
    response = client.describe_authentication_profiles()
    assert len(response["AuthenticationProfiles"]) == 1


@mock_aws
def test_delete_authentication_profile():
    client = boto3.client("redshift", region_name="us-east-1")
    content = json.dumps({"AllowDBUserOverride": "1"})
    client.create_authentication_profile(
        AuthenticationProfileName="test-profile",
        AuthenticationProfileContent=content,
    )
    client.delete_authentication_profile(AuthenticationProfileName="test-profile")
    response = client.describe_authentication_profiles()
    assert len(response["AuthenticationProfiles"]) == 0


@mock_aws
def test_modify_authentication_profile():
    client = boto3.client("redshift", region_name="us-east-1")
    client.create_authentication_profile(
        AuthenticationProfileName="test-profile",
        AuthenticationProfileContent=json.dumps({"k": "v1"}),
    )
    new_content = json.dumps({"k": "v2"})
    response = client.modify_authentication_profile(
        AuthenticationProfileName="test-profile",
        AuthenticationProfileContent=new_content,
    )
    assert response["AuthenticationProfileContent"] == new_content


@mock_aws
def test_batch_delete_cluster_snapshots():
    client = boto3.client("redshift", region_name="us-east-1")
    _create_cluster(client)
    _create_snapshot(client, snapshot_id="snap-1")
    _create_snapshot(client, snapshot_id="snap-2")
    response = client.batch_delete_cluster_snapshots(
        Identifiers=[
            {"SnapshotIdentifier": "snap-1"},
            {"SnapshotIdentifier": "snap-2"},
        ]
    )
    assert "snap-1" in response.get("Resources", [])
    assert "snap-2" in response.get("Resources", [])


@mock_aws
def test_create_usage_limit():
    client = boto3.client("redshift", region_name="us-east-1")
    _create_cluster(client)
    response = client.create_usage_limit(
        ClusterIdentifier="test-cluster",
        FeatureType="spectrum",
        LimitType="data-scanned",
        Amount=100,
    )
    assert response["ClusterIdentifier"] == "test-cluster"
    assert response["FeatureType"] == "spectrum"
    assert response["Amount"] == 100
    assert response["UsageLimitId"].startswith("rul-")


@mock_aws
def test_describe_usage_limits():
    client = boto3.client("redshift", region_name="us-east-1")
    _create_cluster(client)
    client.create_usage_limit(
        ClusterIdentifier="test-cluster",
        FeatureType="spectrum",
        LimitType="data-scanned",
        Amount=100,
    )
    response = client.describe_usage_limits()
    assert len(response["UsageLimits"]) == 1


@mock_aws
def test_delete_usage_limit():
    client = boto3.client("redshift", region_name="us-east-1")
    _create_cluster(client)
    create_resp = client.create_usage_limit(
        ClusterIdentifier="test-cluster",
        FeatureType="spectrum",
        LimitType="data-scanned",
        Amount=100,
    )
    client.delete_usage_limit(UsageLimitId=create_resp["UsageLimitId"])
    response = client.describe_usage_limits()
    assert len(response["UsageLimits"]) == 0


@mock_aws
def test_modify_usage_limit():
    client = boto3.client("redshift", region_name="us-east-1")
    _create_cluster(client)
    create_resp = client.create_usage_limit(
        ClusterIdentifier="test-cluster",
        FeatureType="spectrum",
        LimitType="data-scanned",
        Amount=100,
        BreachAction="log",
    )
    response = client.modify_usage_limit(
        UsageLimitId=create_resp["UsageLimitId"],
        Amount=200,
        BreachAction="emit-metric",
    )
    assert response["Amount"] == 200
    assert response["BreachAction"] == "emit-metric"


@mock_aws
def test_authorize_endpoint_access():
    client = boto3.client("redshift", region_name="us-east-1")
    _create_cluster(client)
    response = client.authorize_endpoint_access(
        ClusterIdentifier="test-cluster",
        Account="111122223333",
    )
    assert response["ClusterIdentifier"] == "test-cluster"
    assert response["Grantee"] == "111122223333"
    assert response["Status"] == "Authorized"


@mock_aws
def test_describe_endpoint_authorization():
    client = boto3.client("redshift", region_name="us-east-1")
    _create_cluster(client)
    client.authorize_endpoint_access(
        ClusterIdentifier="test-cluster",
        Account="111122223333",
    )
    response = client.describe_endpoint_authorization(
        ClusterIdentifier="test-cluster",
    )
    assert len(response["EndpointAuthorizationList"]) == 1


@mock_aws
def test_revoke_endpoint_access_for_cluster():
    client = boto3.client("redshift", region_name="us-east-1")
    _create_cluster(client)
    client.authorize_endpoint_access(
        ClusterIdentifier="test-cluster",
        Account="111122223333",
    )
    response = client.revoke_endpoint_access(
        ClusterIdentifier="test-cluster",
        Account="111122223333",
    )
    assert response["Status"] == "Revoking"
