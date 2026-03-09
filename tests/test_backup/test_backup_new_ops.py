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
