"""Tests for newly implemented backup operations."""

import json

import boto3
import pytest
from moto import mock_aws


@mock_aws
def test_describe_global_settings():
    client = boto3.client("backup", region_name="us-east-1")
    resp = client.describe_global_settings()
    assert "GlobalSettings" in resp
    assert resp["GlobalSettings"]["isCrossAccountBackupEnabled"] == "false"


@mock_aws
def test_update_global_settings():
    client = boto3.client("backup", region_name="us-east-1")
    client.update_global_settings(
        GlobalSettings={"isCrossAccountBackupEnabled": "true"}
    )
    resp = client.describe_global_settings()
    assert resp["GlobalSettings"]["isCrossAccountBackupEnabled"] == "true"


@mock_aws
def test_describe_region_settings():
    client = boto3.client("backup", region_name="us-east-1")
    resp = client.describe_region_settings()
    assert "ResourceTypeOptInPreference" in resp
    assert resp["ResourceTypeOptInPreference"]["EBS"] is True
    assert resp["ResourceTypeOptInPreference"]["S3"] is True


@mock_aws
def test_update_region_settings():
    client = boto3.client("backup", region_name="us-east-1")
    client.update_region_settings(
        ResourceTypeOptInPreference={"EBS": False}
    )
    resp = client.describe_region_settings()
    assert resp["ResourceTypeOptInPreference"]["EBS"] is False
    assert resp["ResourceTypeOptInPreference"]["S3"] is True


@mock_aws
def test_get_supported_resource_types():
    client = boto3.client("backup", region_name="us-east-1")
    resp = client.get_supported_resource_types()
    assert "ResourceTypes" in resp
    assert "EBS" in resp["ResourceTypes"]
    assert "S3" in resp["ResourceTypes"]
    assert "DynamoDB" in resp["ResourceTypes"]
    assert len(resp["ResourceTypes"]) >= 10


@mock_aws
def test_list_backup_plan_templates():
    client = boto3.client("backup", region_name="us-east-1")
    resp = client.list_backup_plan_templates()
    assert "BackupPlanTemplatesList" in resp
    assert len(resp["BackupPlanTemplatesList"]) >= 1
    template = resp["BackupPlanTemplatesList"][0]
    assert "BackupPlanTemplateId" in template
    assert "BackupPlanTemplateName" in template


@mock_aws
def test_get_backup_plan_from_json():
    client = boto3.client("backup", region_name="us-east-1")
    plan_doc = {
        "BackupPlanName": "TestPlan",
        "Rules": [
            {
                "RuleName": "DailyBackup",
                "TargetBackupVaultName": "Default",
                "ScheduleExpression": "cron(0 5 ? * * *)",
            }
        ],
    }
    resp = client.get_backup_plan_from_json(
        BackupPlanTemplateJson=json.dumps(plan_doc)
    )
    assert "BackupPlan" in resp
    assert resp["BackupPlan"]["BackupPlanName"] == "TestPlan"


@mock_aws
def test_list_backup_plan_versions():
    client = boto3.client("backup", region_name="us-east-1")
    plan = client.create_backup_plan(
        BackupPlan={
            "BackupPlanName": "TestPlan",
            "Rules": [
                {
                    "RuleName": "DailyBackup",
                    "TargetBackupVaultName": "Default",
                    "ScheduleExpression": "cron(0 5 ? * * *)",
                }
            ],
        }
    )
    plan_id = plan["BackupPlanId"]
    resp = client.list_backup_plan_versions(BackupPlanId=plan_id)
    assert "BackupPlanVersionsList" in resp
    assert len(resp["BackupPlanVersionsList"]) == 1
    assert resp["BackupPlanVersionsList"][0]["BackupPlanId"] == plan_id


@mock_aws
def test_list_copy_jobs_empty():
    client = boto3.client("backup", region_name="us-east-1")
    resp = client.list_copy_jobs()
    assert "CopyJobs" in resp
    assert resp["CopyJobs"] == []


@mock_aws
def test_list_protected_resources_empty():
    client = boto3.client("backup", region_name="us-east-1")
    resp = client.list_protected_resources()
    assert "Results" in resp
    assert resp["Results"] == []


@mock_aws
def test_describe_protected_resource_not_found():
    client = boto3.client("backup", region_name="us-east-1")
    with pytest.raises(client.exceptions.ResourceNotFoundException):
        client.describe_protected_resource(
            ResourceArn="arn:aws:ec2:us-east-1:123456789012:volume/vol-12345"
        )


@mock_aws
def test_describe_recovery_point_vault_not_found():
    client = boto3.client("backup", region_name="us-east-1")
    with pytest.raises(client.exceptions.ResourceNotFoundException):
        client.describe_recovery_point(
            BackupVaultName="nonexistent",
            RecoveryPointArn="arn:aws:backup:us-east-1:123456789012:recovery-point:abc",
        )


@mock_aws
def test_describe_copy_job_not_found():
    client = boto3.client("backup", region_name="us-east-1")
    with pytest.raises(client.exceptions.ResourceNotFoundException):
        client.describe_copy_job(CopyJobId="nonexistent-id")


@mock_aws
def test_vault_access_policy_lifecycle():
    client = boto3.client("backup", region_name="us-east-1")
    client.create_backup_vault(BackupVaultName="test-vault")

    policy = json.dumps({
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": "*",
                "Action": "backup:DescribeBackupVault",
                "Resource": "*",
            }
        ],
    })
    client.put_backup_vault_access_policy(
        BackupVaultName="test-vault", Policy=policy
    )
    resp = client.get_backup_vault_access_policy(
        BackupVaultName="test-vault"
    )
    assert resp["BackupVaultName"] == "test-vault"
    assert "Policy" in resp

    client.delete_backup_vault_access_policy(
        BackupVaultName="test-vault"
    )
    with pytest.raises(client.exceptions.ResourceNotFoundException):
        client.get_backup_vault_access_policy(
            BackupVaultName="test-vault"
        )


@mock_aws
def test_vault_access_policy_vault_not_found():
    client = boto3.client("backup", region_name="us-east-1")
    with pytest.raises(client.exceptions.ResourceNotFoundException):
        client.get_backup_vault_access_policy(
            BackupVaultName="nonexistent"
        )


@mock_aws
def test_vault_notifications_lifecycle():
    client = boto3.client("backup", region_name="us-east-1")
    client.create_backup_vault(BackupVaultName="test-vault")

    client.put_backup_vault_notifications(
        BackupVaultName="test-vault",
        SNSTopicArn="arn:aws:sns:us-east-1:123456789012:my-topic",
        BackupVaultEvents=["BACKUP_JOB_COMPLETED", "RESTORE_JOB_COMPLETED"],
    )
    resp = client.get_backup_vault_notifications(
        BackupVaultName="test-vault"
    )
    assert resp["BackupVaultName"] == "test-vault"
    assert resp["SNSTopicArn"] == "arn:aws:sns:us-east-1:123456789012:my-topic"
    assert "BACKUP_JOB_COMPLETED" in resp["BackupVaultEvents"]

    client.delete_backup_vault_notifications(
        BackupVaultName="test-vault"
    )
    with pytest.raises(client.exceptions.ResourceNotFoundException):
        client.get_backup_vault_notifications(
            BackupVaultName="test-vault"
        )


@mock_aws
def test_vault_notifications_vault_not_found():
    client = boto3.client("backup", region_name="us-east-1")
    with pytest.raises(client.exceptions.ResourceNotFoundException):
        client.get_backup_vault_notifications(
            BackupVaultName="nonexistent"
        )


@mock_aws
def test_restore_testing_plan_lifecycle():
    client = boto3.client("backup", region_name="us-east-1")
    resp = client.create_restore_testing_plan(
        RestoreTestingPlan={
            "RestoreTestingPlanName": "test-plan",
            "ScheduleExpression": "cron(0 5 ? * * *)",
            "RecoveryPointSelection": {
                "Algorithm": "LATEST_WITHIN_WINDOW",
                "RecoveryPointTypes": ["CONTINUOUS"],
                "IncludeVaults": ["*"],
            },
        }
    )
    assert resp["RestoreTestingPlanName"] == "test-plan"
    assert "RestoreTestingPlanArn" in resp

    get_resp = client.get_restore_testing_plan(
        RestoreTestingPlanName="test-plan"
    )
    plan = get_resp["RestoreTestingPlan"]
    assert plan["RestoreTestingPlanName"] == "test-plan"
    assert plan["ScheduleExpression"] == "cron(0 5 ? * * *)"

    list_resp = client.list_restore_testing_plans()
    assert len(list_resp["RestoreTestingPlans"]) == 1

    client.delete_restore_testing_plan(
        RestoreTestingPlanName="test-plan"
    )
    list_resp = client.list_restore_testing_plans()
    assert len(list_resp["RestoreTestingPlans"]) == 0


@mock_aws
def test_restore_testing_plan_not_found():
    client = boto3.client("backup", region_name="us-east-1")
    with pytest.raises(client.exceptions.ResourceNotFoundException):
        client.get_restore_testing_plan(
            RestoreTestingPlanName="nonexistent"
        )


@mock_aws
def test_restore_testing_selection_lifecycle():
    client = boto3.client("backup", region_name="us-east-1")
    client.create_restore_testing_plan(
        RestoreTestingPlan={
            "RestoreTestingPlanName": "test-plan",
            "ScheduleExpression": "cron(0 5 ? * * *)",
            "RecoveryPointSelection": {
                "Algorithm": "LATEST_WITHIN_WINDOW",
                "RecoveryPointTypes": ["CONTINUOUS"],
                "IncludeVaults": ["*"],
            },
        }
    )

    resp = client.create_restore_testing_selection(
        RestoreTestingPlanName="test-plan",
        RestoreTestingSelection={
            "RestoreTestingSelectionName": "test-selection",
            "ProtectedResourceType": "EBS",
            "IamRoleArn": "arn:aws:iam::123456789012:role/test-role",
        },
    )
    assert resp["RestoreTestingSelectionName"] == "test-selection"

    get_resp = client.get_restore_testing_selection(
        RestoreTestingPlanName="test-plan",
        RestoreTestingSelectionName="test-selection",
    )
    sel = get_resp["RestoreTestingSelection"]
    assert sel["RestoreTestingSelectionName"] == "test-selection"
    assert sel["ProtectedResourceType"] == "EBS"

    list_resp = client.list_restore_testing_selections(
        RestoreTestingPlanName="test-plan"
    )
    assert len(list_resp["RestoreTestingSelections"]) == 1

    client.delete_restore_testing_selection(
        RestoreTestingPlanName="test-plan",
        RestoreTestingSelectionName="test-selection",
    )
    list_resp = client.list_restore_testing_selections(
        RestoreTestingPlanName="test-plan"
    )
    assert len(list_resp["RestoreTestingSelections"]) == 0


@mock_aws
def test_restore_testing_selection_not_found():
    client = boto3.client("backup", region_name="us-east-1")
    client.create_restore_testing_plan(
        RestoreTestingPlan={
            "RestoreTestingPlanName": "test-plan",
            "ScheduleExpression": "cron(0 5 ? * * *)",
            "RecoveryPointSelection": {
                "Algorithm": "LATEST_WITHIN_WINDOW",
                "RecoveryPointTypes": ["CONTINUOUS"],
                "IncludeVaults": ["*"],
            },
        }
    )
    with pytest.raises(client.exceptions.ResourceNotFoundException):
        client.get_restore_testing_selection(
            RestoreTestingPlanName="test-plan",
            RestoreTestingSelectionName="nonexistent",
        )


# --- Legal Hold Tests ---


@mock_aws
def test_legal_hold_create_get_list():
    client = boto3.client("backup", region_name="us-east-1")
    resp = client.create_legal_hold(
        Title="TestHold",
        Description="A test legal hold",
        RecoveryPointSelection={
            "VaultNames": ["my-vault"],
            "ResourceIdentifiers": ["*"],
        },
        Tags={"env": "test"},
    )
    assert resp["Title"] == "TestHold"
    assert resp["Description"] == "A test legal hold"
    assert resp["Status"] == "ACTIVE"
    assert "LegalHoldId" in resp
    assert "LegalHoldArn" in resp
    hold_id = resp["LegalHoldId"]

    # Get
    resp = client.get_legal_hold(LegalHoldId=hold_id)
    assert resp["Title"] == "TestHold"
    assert resp["Status"] == "ACTIVE"
    assert resp["RecoveryPointSelection"]["VaultNames"] == ["my-vault"]

    # List
    resp = client.list_legal_holds()
    assert len(resp["LegalHolds"]) == 1
    assert resp["LegalHolds"][0]["LegalHoldId"] == hold_id


@mock_aws
def test_legal_hold_cancel():
    client = boto3.client("backup", region_name="us-east-1")
    resp = client.create_legal_hold(Title="ToCancel", Description="Will cancel")
    hold_id = resp["LegalHoldId"]

    client.cancel_legal_hold(
        LegalHoldId=hold_id,
        CancelDescription="No longer needed",
    )
    resp = client.get_legal_hold(LegalHoldId=hold_id)
    assert resp["Status"] == "CANCELED"
    assert "CancellationDate" in resp


@mock_aws
def test_legal_hold_not_found():
    client = boto3.client("backup", region_name="us-east-1")
    with pytest.raises(client.exceptions.ResourceNotFoundException):
        client.get_legal_hold(LegalHoldId="nonexistent")


@mock_aws
def test_legal_hold_cancel_already_canceled():
    client = boto3.client("backup", region_name="us-east-1")
    resp = client.create_legal_hold(Title="X", Description="Y")
    hold_id = resp["LegalHoldId"]
    client.cancel_legal_hold(LegalHoldId=hold_id, CancelDescription="done")
    with pytest.raises(client.exceptions.InvalidRequestException):
        client.cancel_legal_hold(LegalHoldId=hold_id, CancelDescription="again")


# --- Export Backup Plan Template ---


@mock_aws
def test_export_backup_plan_template():
    client = boto3.client("backup", region_name="us-east-1")
    plan_resp = client.create_backup_plan(
        BackupPlan={
            "BackupPlanName": "test-export",
            "Rules": [
                {
                    "RuleName": "daily",
                    "TargetBackupVaultName": "Default",
                }
            ],
        }
    )
    plan_id = plan_resp["BackupPlanId"]

    resp = client.export_backup_plan_template(BackupPlanId=plan_id)
    assert "BackupPlanTemplateJson" in resp
    template = json.loads(resp["BackupPlanTemplateJson"])
    assert template["BackupPlanName"] == "test-export"


@mock_aws
def test_export_backup_plan_template_not_found():
    client = boto3.client("backup", region_name="us-east-1")
    with pytest.raises(client.exceptions.ResourceNotFoundException):
        client.export_backup_plan_template(BackupPlanId="nonexistent")


# --- Get Backup Plan From Template ---


@mock_aws
def test_get_backup_plan_from_template():
    client = boto3.client("backup", region_name="us-east-1")
    templates = client.list_backup_plan_templates()
    template_id = templates["BackupPlanTemplatesList"][0]["BackupPlanTemplateId"]

    resp = client.get_backup_plan_from_template(BackupPlanTemplateId=template_id)
    assert "BackupPlanDocument" in resp
    assert "BackupPlanName" in resp["BackupPlanDocument"]
    assert "Rules" in resp["BackupPlanDocument"]


@mock_aws
def test_get_backup_plan_from_template_not_found():
    client = boto3.client("backup", region_name="us-east-1")
    with pytest.raises(client.exceptions.ResourceNotFoundException):
        client.get_backup_plan_from_template(
            BackupPlanTemplateId="nonexistent-template-id"
        )


# --- Restore Jobs ---


@mock_aws
def test_restore_job_lifecycle():
    client = boto3.client("backup", region_name="us-east-1")
    resp = client.start_restore_job(
        RecoveryPointArn="arn:aws:backup:us-east-1:123456789012:recovery-point:abc-123",
        IamRoleArn="arn:aws:iam::123456789012:role/restore-role",
        Metadata={"key1": "val1"},
        ResourceType="DynamoDB",
    )
    assert "RestoreJobId" in resp
    job_id = resp["RestoreJobId"]

    # Describe
    resp = client.describe_restore_job(RestoreJobId=job_id)
    assert resp["RestoreJobId"] == job_id
    assert resp["Status"] == "COMPLETED"
    assert resp["ResourceType"] == "DynamoDB"
    assert "CreatedResourceArn" in resp

    # List
    resp = client.list_restore_jobs()
    assert len(resp["RestoreJobs"]) == 1
    assert resp["RestoreJobs"][0]["RestoreJobId"] == job_id


@mock_aws
def test_restore_job_not_found():
    client = boto3.client("backup", region_name="us-east-1")
    with pytest.raises(client.exceptions.ResourceNotFoundException):
        client.describe_restore_job(RestoreJobId="nonexistent")


@mock_aws
def test_list_restore_jobs_empty():
    client = boto3.client("backup", region_name="us-east-1")
    resp = client.list_restore_jobs()
    assert "RestoreJobs" in resp
    assert len(resp["RestoreJobs"]) == 0


@mock_aws
def test_get_restore_job_metadata():
    client = boto3.client("backup", region_name="us-east-1")
    resp = client.start_restore_job(
        RecoveryPointArn="arn:aws:backup:us-east-1:123456789012:recovery-point:abc-123",
        IamRoleArn="arn:aws:iam::123456789012:role/restore-role",
        Metadata={"region": "us-east-1"},
    )
    job_id = resp["RestoreJobId"]

    resp = client.get_restore_job_metadata(RestoreJobId=job_id)
    assert resp["RestoreJobId"] == job_id
    assert resp["Metadata"]["region"] == "us-east-1"


@mock_aws
def test_put_restore_validation_result():
    client = boto3.client("backup", region_name="us-east-1")
    resp = client.start_restore_job(
        RecoveryPointArn="arn:aws:backup:us-east-1:123456789012:recovery-point:abc-123",
        IamRoleArn="arn:aws:iam::123456789012:role/restore-role",
        Metadata={},
    )
    job_id = resp["RestoreJobId"]

    client.put_restore_validation_result(
        RestoreJobId=job_id,
        ValidationStatus="SUCCESSFUL",
        ValidationStatusMessage="All good",
    )

    resp = client.describe_restore_job(RestoreJobId=job_id)
    assert resp["ValidationStatus"] == "SUCCESSFUL"
    assert resp["ValidationStatusMessage"] == "All good"


# --- Recovery Points ---


@mock_aws
def test_list_recovery_points_by_backup_vault_empty():
    client = boto3.client("backup", region_name="us-east-1")
    client.create_backup_vault(BackupVaultName="test-vault")

    resp = client.list_recovery_points_by_backup_vault(
        BackupVaultName="test-vault"
    )
    assert "RecoveryPoints" in resp
    assert len(resp["RecoveryPoints"]) == 0


@mock_aws
def test_list_recovery_points_by_backup_vault_not_found():
    client = boto3.client("backup", region_name="us-east-1")
    with pytest.raises(client.exceptions.ResourceNotFoundException):
        client.list_recovery_points_by_backup_vault(
            BackupVaultName="nonexistent"
        )


@mock_aws
def test_list_recovery_points_by_resource_empty():
    client = boto3.client("backup", region_name="us-east-1")
    resp = client.list_recovery_points_by_resource(
        ResourceArn="arn:aws:dynamodb:us-east-1:123456789012:table/mytable"
    )
    assert "RecoveryPoints" in resp
    assert len(resp["RecoveryPoints"]) == 0
