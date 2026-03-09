"""Unit tests for backup job APIs."""

import boto3
import pytest
from botocore.exceptions import ClientError

from moto import mock_aws


@mock_aws
def test_start_backup_job():
    client = boto3.client("backup", region_name="eu-west-1")
    client.create_backup_vault(BackupVaultName="test-vault")
    resp = client.start_backup_job(
        BackupVaultName="test-vault",
        ResourceArn="arn:aws:dynamodb:eu-west-1:123456789012:table/mytable",
        IamRoleArn="arn:aws:iam::123456789012:role/backup-role",
    )
    assert "BackupJobId" in resp
    assert "RecoveryPointArn" in resp
    assert "CreationDate" in resp


@mock_aws
def test_start_backup_job_vault_not_found():
    client = boto3.client("backup", region_name="eu-west-1")
    with pytest.raises(ClientError) as exc:
        client.start_backup_job(
            BackupVaultName="nonexistent-vault",
            ResourceArn="arn:aws:dynamodb:eu-west-1:123456789012:table/mytable",
            IamRoleArn="arn:aws:iam::123456789012:role/backup-role",
        )
    assert exc.value.response["Error"]["Code"] == "ResourceNotFoundException"


@mock_aws
def test_describe_backup_job():
    client = boto3.client("backup", region_name="eu-west-1")
    client.create_backup_vault(BackupVaultName="test-vault")
    job = client.start_backup_job(
        BackupVaultName="test-vault",
        ResourceArn="arn:aws:dynamodb:eu-west-1:123456789012:table/mytable",
        IamRoleArn="arn:aws:iam::123456789012:role/backup-role",
    )
    resp = client.describe_backup_job(BackupJobId=job["BackupJobId"])
    assert resp["BackupJobId"] == job["BackupJobId"]
    assert resp["BackupVaultName"] == "test-vault"
    assert resp["ResourceArn"] == "arn:aws:dynamodb:eu-west-1:123456789012:table/mytable"
    assert resp["State"] == "COMPLETED"
    assert resp["ResourceType"] == "DynamoDB"
    assert "RecoveryPointArn" in resp


@mock_aws
def test_describe_backup_job_not_found():
    client = boto3.client("backup", region_name="eu-west-1")
    with pytest.raises(ClientError) as exc:
        client.describe_backup_job(BackupJobId="nonexistent-job-id")
    assert exc.value.response["Error"]["Code"] == "ResourceNotFoundException"


@mock_aws
def test_list_backup_jobs():
    client = boto3.client("backup", region_name="eu-west-1")
    client.create_backup_vault(BackupVaultName="test-vault")
    for i in range(3):
        client.start_backup_job(
            BackupVaultName="test-vault",
            ResourceArn=f"arn:aws:dynamodb:eu-west-1:123456789012:table/table{i}",
            IamRoleArn="arn:aws:iam::123456789012:role/backup-role",
        )
    resp = client.list_backup_jobs()
    assert len(resp["BackupJobs"]) == 3


@mock_aws
def test_list_backup_jobs_filter_by_vault():
    client = boto3.client("backup", region_name="eu-west-1")
    client.create_backup_vault(BackupVaultName="vault-1")
    client.create_backup_vault(BackupVaultName="vault-2")
    client.start_backup_job(
        BackupVaultName="vault-1",
        ResourceArn="arn:aws:dynamodb:eu-west-1:123456789012:table/t1",
        IamRoleArn="arn:aws:iam::123456789012:role/backup-role",
    )
    client.start_backup_job(
        BackupVaultName="vault-2",
        ResourceArn="arn:aws:dynamodb:eu-west-1:123456789012:table/t2",
        IamRoleArn="arn:aws:iam::123456789012:role/backup-role",
    )
    resp = client.list_backup_jobs(ByBackupVaultName="vault-1")
    assert len(resp["BackupJobs"]) == 1
    assert resp["BackupJobs"][0]["BackupVaultName"] == "vault-1"


@mock_aws
def test_list_backup_jobs_filter_by_state():
    client = boto3.client("backup", region_name="eu-west-1")
    client.create_backup_vault(BackupVaultName="test-vault")
    client.start_backup_job(
        BackupVaultName="test-vault",
        ResourceArn="arn:aws:dynamodb:eu-west-1:123456789012:table/t1",
        IamRoleArn="arn:aws:iam::123456789012:role/backup-role",
    )
    # Jobs start as COMPLETED in our mock
    resp = client.list_backup_jobs(ByState="COMPLETED")
    assert len(resp["BackupJobs"]) == 1
    resp = client.list_backup_jobs(ByState="RUNNING")
    assert len(resp["BackupJobs"]) == 0


@mock_aws
def test_list_backup_jobs_empty():
    client = boto3.client("backup", region_name="eu-west-1")
    resp = client.list_backup_jobs()
    assert resp["BackupJobs"] == []


@mock_aws
def test_start_backup_job_with_lifecycle():
    client = boto3.client("backup", region_name="eu-west-1")
    client.create_backup_vault(BackupVaultName="test-vault")
    job = client.start_backup_job(
        BackupVaultName="test-vault",
        ResourceArn="arn:aws:dynamodb:eu-west-1:123456789012:table/mytable",
        IamRoleArn="arn:aws:iam::123456789012:role/backup-role",
        Lifecycle={
            "MoveToColdStorageAfterDays": 30,
            "DeleteAfterDays": 365,
        },
    )
    resp = client.describe_backup_job(BackupJobId=job["BackupJobId"])
    assert resp["RecoveryPointLifecycle"]["MoveToColdStorageAfterDays"] == 30
    assert resp["RecoveryPointLifecycle"]["DeleteAfterDays"] == 365
