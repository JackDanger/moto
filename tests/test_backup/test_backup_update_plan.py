"""Unit tests for backup update_backup_plan API."""

import boto3
import pytest
from botocore.exceptions import ClientError

from moto import mock_aws


@mock_aws
def test_update_backup_plan():
    client = boto3.client("backup", region_name="eu-west-1")
    client.create_backup_vault(BackupVaultName="test-vault")
    plan = client.create_backup_plan(
        BackupPlan={
            "BackupPlanName": "test-plan",
            "Rules": [
                {"RuleName": "rule1", "TargetBackupVaultName": "test-vault"},
            ],
        },
    )
    original_version = plan["VersionId"]

    resp = client.update_backup_plan(
        BackupPlanId=plan["BackupPlanId"],
        BackupPlan={
            "BackupPlanName": "updated-plan",
            "Rules": [
                {
                    "RuleName": "rule1-updated",
                    "TargetBackupVaultName": "test-vault",
                    "ScheduleExpression": "cron(0 12 ? * * *)",
                },
            ],
        },
    )
    assert resp["BackupPlanId"] == plan["BackupPlanId"]
    assert resp["VersionId"] != original_version
    assert "CreationDate" in resp

    # Verify the plan was actually updated
    got = client.get_backup_plan(BackupPlanId=plan["BackupPlanId"])
    assert got["BackupPlan"]["BackupPlanName"] == "updated-plan"
    assert got["BackupPlan"]["Rules"][0]["RuleName"] == "rule1-updated"
    assert got["BackupPlan"]["Rules"][0]["ScheduleExpression"] == "cron(0 12 ? * * *)"


@mock_aws
def test_update_backup_plan_not_found():
    client = boto3.client("backup", region_name="eu-west-1")
    with pytest.raises(ClientError) as exc:
        client.update_backup_plan(
            BackupPlanId="nonexistent-plan-id",
            BackupPlan={
                "BackupPlanName": "test",
                "Rules": [
                    {
                        "RuleName": "rule1",
                        "TargetBackupVaultName": "vault",
                    },
                ],
            },
        )
    assert exc.value.response["Error"]["Code"] == "ResourceNotFoundException"
