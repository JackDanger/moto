"""Unit tests for backup selection APIs."""

import boto3
import pytest
from botocore.exceptions import ClientError

from moto import mock_aws


@mock_aws
def test_create_backup_selection():
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
    resp = client.create_backup_selection(
        BackupPlanId=plan["BackupPlanId"],
        BackupSelection={
            "SelectionName": "test-selection",
            "IamRoleArn": "arn:aws:iam::123456789012:role/backup-role",
            "Resources": ["arn:aws:dynamodb:eu-west-1:123456789012:table/*"],
        },
    )
    assert "SelectionId" in resp
    assert "BackupPlanId" in resp
    assert resp["BackupPlanId"] == plan["BackupPlanId"]
    assert "CreationDate" in resp


@mock_aws
def test_create_backup_selection_invalid_plan():
    client = boto3.client("backup", region_name="eu-west-1")
    with pytest.raises(ClientError) as exc:
        client.create_backup_selection(
            BackupPlanId="nonexistent-plan",
            BackupSelection={
                "SelectionName": "test-selection",
                "IamRoleArn": "arn:aws:iam::123456789012:role/backup-role",
                "Resources": ["*"],
            },
        )
    assert exc.value.response["Error"]["Code"] == "ResourceNotFoundException"


@mock_aws
def test_get_backup_selection():
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
    sel = client.create_backup_selection(
        BackupPlanId=plan["BackupPlanId"],
        BackupSelection={
            "SelectionName": "test-selection",
            "IamRoleArn": "arn:aws:iam::123456789012:role/backup-role",
            "Resources": ["arn:aws:dynamodb:eu-west-1:123456789012:table/*"],
        },
    )
    resp = client.get_backup_selection(
        BackupPlanId=plan["BackupPlanId"],
        SelectionId=sel["SelectionId"],
    )
    assert resp["BackupPlanId"] == plan["BackupPlanId"]
    assert resp["SelectionId"] == sel["SelectionId"]
    assert "BackupSelection" in resp
    assert resp["BackupSelection"]["SelectionName"] == "test-selection"
    assert resp["BackupSelection"]["IamRoleArn"] == "arn:aws:iam::123456789012:role/backup-role"


@mock_aws
def test_get_backup_selection_not_found():
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
    with pytest.raises(ClientError) as exc:
        client.get_backup_selection(
            BackupPlanId=plan["BackupPlanId"],
            SelectionId="nonexistent-selection-id",
        )
    assert exc.value.response["Error"]["Code"] == "ResourceNotFoundException"


@mock_aws
def test_delete_backup_selection():
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
    sel = client.create_backup_selection(
        BackupPlanId=plan["BackupPlanId"],
        BackupSelection={
            "SelectionName": "test-selection",
            "IamRoleArn": "arn:aws:iam::123456789012:role/backup-role",
            "Resources": ["*"],
        },
    )
    client.delete_backup_selection(
        BackupPlanId=plan["BackupPlanId"],
        SelectionId=sel["SelectionId"],
    )
    # Verify it's gone
    with pytest.raises(ClientError) as exc:
        client.get_backup_selection(
            BackupPlanId=plan["BackupPlanId"],
            SelectionId=sel["SelectionId"],
        )
    assert exc.value.response["Error"]["Code"] == "ResourceNotFoundException"


@mock_aws
def test_list_backup_selections():
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
    for i in range(3):
        client.create_backup_selection(
            BackupPlanId=plan["BackupPlanId"],
            BackupSelection={
                "SelectionName": f"selection-{i}",
                "IamRoleArn": "arn:aws:iam::123456789012:role/backup-role",
                "Resources": ["*"],
            },
        )
    resp = client.list_backup_selections(BackupPlanId=plan["BackupPlanId"])
    assert len(resp["BackupSelectionsList"]) == 3
    names = [s["SelectionName"] for s in resp["BackupSelectionsList"]]
    assert "selection-0" in names
    assert "selection-1" in names
    assert "selection-2" in names


@mock_aws
def test_list_backup_selections_empty():
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
    resp = client.list_backup_selections(BackupPlanId=plan["BackupPlanId"])
    assert resp["BackupSelectionsList"] == []
