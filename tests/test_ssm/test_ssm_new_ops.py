"""Tests for newly implemented SSM operations: associations, OpsItems, activations, data sync, automation."""

import boto3
import pytest
from moto import mock_aws


# ============================================================================
# Association tests
# ============================================================================

@mock_aws
def test_create_association():
    client = boto3.client("ssm", region_name="us-east-1")
    resp = client.create_association(
        Name="AWS-RunShellScript",
        Targets=[{"Key": "InstanceIds", "Values": ["i-1234567890abcdef0"]}],
        ScheduleExpression="rate(1 hour)",
    )
    desc = resp["AssociationDescription"]
    assert desc["Name"] == "AWS-RunShellScript"
    assert desc["AssociationId"]
    assert desc["Targets"] == [{"Key": "InstanceIds", "Values": ["i-1234567890abcdef0"]}]
    assert desc["ScheduleExpression"] == "rate(1 hour)"


@mock_aws
def test_create_association_with_instance_id():
    client = boto3.client("ssm", region_name="us-east-1")
    resp = client.create_association(
        Name="AWS-RunShellScript",
        InstanceId="i-1234567890abcdef0",
    )
    desc = resp["AssociationDescription"]
    assert desc["InstanceId"] == "i-1234567890abcdef0"


@mock_aws
def test_describe_association_by_id():
    client = boto3.client("ssm", region_name="us-east-1")
    create_resp = client.create_association(
        Name="AWS-RunShellScript",
        Targets=[{"Key": "InstanceIds", "Values": ["i-1234567890abcdef0"]}],
    )
    association_id = create_resp["AssociationDescription"]["AssociationId"]

    resp = client.describe_association(AssociationId=association_id)
    desc = resp["AssociationDescription"]
    assert desc["AssociationId"] == association_id
    assert desc["Name"] == "AWS-RunShellScript"


@mock_aws
def test_describe_association_by_name():
    client = boto3.client("ssm", region_name="us-east-1")
    client.create_association(
        Name="AWS-RunShellScript",
        Targets=[{"Key": "InstanceIds", "Values": ["i-1234567890abcdef0"]}],
    )

    resp = client.describe_association(Name="AWS-RunShellScript")
    desc = resp["AssociationDescription"]
    assert desc["Name"] == "AWS-RunShellScript"


@mock_aws
def test_update_association():
    client = boto3.client("ssm", region_name="us-east-1")
    create_resp = client.create_association(
        Name="AWS-RunShellScript",
        Targets=[{"Key": "InstanceIds", "Values": ["i-1234567890abcdef0"]}],
    )
    association_id = create_resp["AssociationDescription"]["AssociationId"]

    resp = client.update_association(
        AssociationId=association_id,
        ScheduleExpression="rate(2 hours)",
        MaxConcurrency="10",
    )
    desc = resp["AssociationDescription"]
    assert desc["ScheduleExpression"] == "rate(2 hours)"
    assert desc["MaxConcurrency"] == "10"
    assert desc["AssociationVersion"] == "2"


@mock_aws
def test_delete_association_by_id():
    client = boto3.client("ssm", region_name="us-east-1")
    create_resp = client.create_association(
        Name="AWS-RunShellScript",
        Targets=[{"Key": "InstanceIds", "Values": ["i-1234567890abcdef0"]}],
    )
    association_id = create_resp["AssociationDescription"]["AssociationId"]

    client.delete_association(AssociationId=association_id)

    with pytest.raises(client.exceptions.DoesNotExistException):
        client.describe_association(AssociationId=association_id)


@mock_aws
def test_delete_association_by_name():
    client = boto3.client("ssm", region_name="us-east-1")
    client.create_association(
        Name="AWS-RunShellScript",
        InstanceId="i-1234567890abcdef0",
    )

    client.delete_association(Name="AWS-RunShellScript", InstanceId="i-1234567890abcdef0")

    resp = client.list_associations()
    assert len(resp["Associations"]) == 0


@mock_aws
def test_list_associations():
    client = boto3.client("ssm", region_name="us-east-1")
    client.create_association(
        Name="AWS-RunShellScript",
        Targets=[{"Key": "InstanceIds", "Values": ["i-111"]}],
    )
    client.create_association(
        Name="AWS-RunPatchBaseline",
        Targets=[{"Key": "InstanceIds", "Values": ["i-222"]}],
    )

    resp = client.list_associations()
    assert len(resp["Associations"]) == 2
    names = {a["Name"] for a in resp["Associations"]}
    assert names == {"AWS-RunShellScript", "AWS-RunPatchBaseline"}


# ============================================================================
# OpsItem tests
# ============================================================================

@mock_aws
def test_create_ops_item():
    client = boto3.client("ssm", region_name="us-east-1")
    resp = client.create_ops_item(
        Title="Test OpsItem",
        Source="test",
        Description="A test ops item",
        Priority=3,
    )
    assert resp["OpsItemId"].startswith("oi-")
    assert "OpsItemArn" in resp


@mock_aws
def test_get_ops_item():
    client = boto3.client("ssm", region_name="us-east-1")
    create_resp = client.create_ops_item(
        Title="Test OpsItem",
        Source="test",
        Description="A test ops item",
    )
    ops_item_id = create_resp["OpsItemId"]

    resp = client.get_ops_item(OpsItemId=ops_item_id)
    item = resp["OpsItem"]
    assert item["OpsItemId"] == ops_item_id
    assert item["Title"] == "Test OpsItem"
    assert item["Source"] == "test"
    assert item["Status"] == "Open"


@mock_aws
def test_update_ops_item():
    client = boto3.client("ssm", region_name="us-east-1")
    create_resp = client.create_ops_item(
        Title="Test OpsItem",
        Source="test",
        Description="original",
    )
    ops_item_id = create_resp["OpsItemId"]

    client.update_ops_item(
        OpsItemId=ops_item_id,
        Title="Updated Title",
        Status="Resolved",
        Priority=1,
    )

    resp = client.get_ops_item(OpsItemId=ops_item_id)
    item = resp["OpsItem"]
    assert item["Title"] == "Updated Title"
    assert item["Status"] == "Resolved"
    assert item["Priority"] == 1


@mock_aws
def test_get_ops_item_not_found():
    client = boto3.client("ssm", region_name="us-east-1")
    with pytest.raises(client.exceptions.DoesNotExistException):
        client.get_ops_item(OpsItemId="oi-doesnotexist")


@mock_aws
def test_describe_ops_items():
    client = boto3.client("ssm", region_name="us-east-1")
    client.create_ops_item(Title="Item 1", Source="test", Description="desc1")
    client.create_ops_item(Title="Item 2", Source="test", Description="desc2")

    resp = client.describe_ops_items()
    summaries = resp["OpsItemSummaries"]
    assert len(summaries) == 2
    titles = {s["Title"] for s in summaries}
    assert titles == {"Item 1", "Item 2"}


@mock_aws
def test_get_ops_summary_with_items():
    client = boto3.client("ssm", region_name="us-east-1")
    client.create_ops_item(Title="Item 1", Source="test", Description="desc")

    resp = client.get_ops_summary()
    assert len(resp["Entities"]) == 1


# ============================================================================
# Activation tests
# ============================================================================

@mock_aws
def test_create_activation():
    client = boto3.client("ssm", region_name="us-east-1")
    resp = client.create_activation(
        IamRole="arn:aws:iam::123456789012:role/SSMRole",
        Description="Test activation",
        DefaultInstanceName="test-instance",
        RegistrationLimit=5,
    )
    assert "ActivationId" in resp
    assert "ActivationCode" in resp
    assert resp["ActivationId"].startswith("act-")


@mock_aws
def test_describe_activations():
    client = boto3.client("ssm", region_name="us-east-1")
    client.create_activation(
        IamRole="arn:aws:iam::123456789012:role/SSMRole",
        Description="Test activation 1",
    )
    client.create_activation(
        IamRole="arn:aws:iam::123456789012:role/SSMRole",
        Description="Test activation 2",
    )

    resp = client.describe_activations()
    assert len(resp["ActivationList"]) == 2


@mock_aws
def test_delete_activation():
    client = boto3.client("ssm", region_name="us-east-1")
    create_resp = client.create_activation(
        IamRole="arn:aws:iam::123456789012:role/SSMRole",
    )
    activation_id = create_resp["ActivationId"]

    client.delete_activation(ActivationId=activation_id)

    resp = client.describe_activations()
    assert len(resp["ActivationList"]) == 0


@mock_aws
def test_delete_activation_not_found():
    client = boto3.client("ssm", region_name="us-east-1")
    with pytest.raises(client.exceptions.DoesNotExistException):
        client.delete_activation(ActivationId="act-doesnotexist")


# ============================================================================
# Resource Data Sync tests
# ============================================================================

@mock_aws
def test_create_resource_data_sync():
    client = boto3.client("ssm", region_name="us-east-1")
    client.create_resource_data_sync(
        SyncName="my-sync",
        S3Destination={
            "BucketName": "my-bucket",
            "SyncFormat": "JsonSerDe",
            "Region": "us-east-1",
        },
    )

    resp = client.list_resource_data_sync()
    assert len(resp["ResourceDataSyncItems"]) == 1
    assert resp["ResourceDataSyncItems"][0]["SyncName"] == "my-sync"


@mock_aws
def test_create_resource_data_sync_duplicate():
    client = boto3.client("ssm", region_name="us-east-1")
    client.create_resource_data_sync(
        SyncName="my-sync",
        S3Destination={
            "BucketName": "my-bucket",
            "SyncFormat": "JsonSerDe",
            "Region": "us-east-1",
        },
    )

    with pytest.raises(client.exceptions.ClientError) as exc:
        client.create_resource_data_sync(
            SyncName="my-sync",
            S3Destination={
                "BucketName": "other-bucket",
                "SyncFormat": "JsonSerDe",
                "Region": "us-east-1",
            },
        )
    assert "ValidationException" in str(exc.value)


@mock_aws
def test_delete_resource_data_sync():
    client = boto3.client("ssm", region_name="us-east-1")
    client.create_resource_data_sync(
        SyncName="my-sync",
        S3Destination={
            "BucketName": "my-bucket",
            "SyncFormat": "JsonSerDe",
            "Region": "us-east-1",
        },
    )

    client.delete_resource_data_sync(SyncName="my-sync")

    resp = client.list_resource_data_sync()
    assert len(resp["ResourceDataSyncItems"]) == 0


@mock_aws
def test_delete_resource_data_sync_not_found():
    client = boto3.client("ssm", region_name="us-east-1")
    with pytest.raises(client.exceptions.DoesNotExistException):
        client.delete_resource_data_sync(SyncName="nonexistent")


@mock_aws
def test_list_resource_data_sync_empty():
    client = boto3.client("ssm", region_name="us-east-1")
    resp = client.list_resource_data_sync()
    assert resp["ResourceDataSyncItems"] == []


# ============================================================================
# Automation Execution tests
# ============================================================================

@mock_aws
def test_start_automation_execution():
    client = boto3.client("ssm", region_name="us-east-1")
    resp = client.start_automation_execution(
        DocumentName="AWS-RestartEC2Instance",
        Parameters={"InstanceId": ["i-1234567890abcdef0"]},
    )
    assert "AutomationExecutionId" in resp
    exec_id = resp["AutomationExecutionId"]
    assert len(exec_id) > 0


@mock_aws
def test_get_automation_execution():
    client = boto3.client("ssm", region_name="us-east-1")
    start_resp = client.start_automation_execution(
        DocumentName="AWS-RestartEC2Instance",
        Parameters={"InstanceId": ["i-1234567890abcdef0"]},
    )
    exec_id = start_resp["AutomationExecutionId"]

    resp = client.get_automation_execution(AutomationExecutionId=exec_id)
    execution = resp["AutomationExecution"]
    assert execution["AutomationExecutionId"] == exec_id
    assert execution["DocumentName"] == "AWS-RestartEC2Instance"
    assert execution["AutomationExecutionStatus"] == "InProgress"
    assert execution["Parameters"] == {"InstanceId": ["i-1234567890abcdef0"]}


@mock_aws
def test_get_automation_execution_not_found():
    client = boto3.client("ssm", region_name="us-east-1")
    with pytest.raises(client.exceptions.DoesNotExistException):
        client.get_automation_execution(AutomationExecutionId="00000000-0000-0000-0000-000000000000")


@mock_aws
def test_stop_automation_execution():
    client = boto3.client("ssm", region_name="us-east-1")
    start_resp = client.start_automation_execution(
        DocumentName="AWS-RestartEC2Instance",
    )
    exec_id = start_resp["AutomationExecutionId"]

    client.stop_automation_execution(AutomationExecutionId=exec_id, Type="Cancel")

    resp = client.get_automation_execution(AutomationExecutionId=exec_id)
    assert resp["AutomationExecution"]["AutomationExecutionStatus"] == "Cancelled"
    assert "ExecutionEndTime" in resp["AutomationExecution"]


@mock_aws
def test_stop_automation_execution_not_found():
    client = boto3.client("ssm", region_name="us-east-1")
    with pytest.raises(client.exceptions.DoesNotExistException):
        client.stop_automation_execution(AutomationExecutionId="00000000-0000-0000-0000-000000000000")


@mock_aws
def test_describe_automation_executions():
    client = boto3.client("ssm", region_name="us-east-1")
    client.start_automation_execution(DocumentName="AWS-RestartEC2Instance")
    client.start_automation_execution(DocumentName="AWS-StopEC2Instance")

    resp = client.describe_automation_executions()
    executions = resp["AutomationExecutionMetadataList"]
    assert len(executions) == 2
    doc_names = {e["DocumentName"] for e in executions}
    assert doc_names == {"AWS-RestartEC2Instance", "AWS-StopEC2Instance"}


@mock_aws
def test_describe_automation_executions_empty():
    client = boto3.client("ssm", region_name="us-east-1")
    resp = client.describe_automation_executions()
    assert resp["AutomationExecutionMetadataList"] == []
