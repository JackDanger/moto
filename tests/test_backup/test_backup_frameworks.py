"""Unit tests for backup framework APIs."""

import boto3
import pytest
from botocore.exceptions import ClientError

from moto import mock_aws


@mock_aws
def test_create_framework():
    client = boto3.client("backup", region_name="eu-west-1")
    resp = client.create_framework(
        FrameworkName="test-framework",
        FrameworkControls=[
            {
                "ControlName": "BACKUP_RESOURCES_PROTECTED_BY_BACKUP_PLAN",
                "ControlScope": {
                    "ComplianceResourceTypes": ["AWS::DynamoDB::Table"],
                },
            },
        ],
        FrameworkDescription="A test framework",
    )
    assert "FrameworkName" in resp
    assert resp["FrameworkName"] == "test-framework"
    assert "FrameworkArn" in resp


@mock_aws
def test_create_framework_already_exists():
    client = boto3.client("backup", region_name="eu-west-1")
    client.create_framework(
        FrameworkName="test-framework",
        FrameworkControls=[
            {"ControlName": "BACKUP_RESOURCES_PROTECTED_BY_BACKUP_PLAN"},
        ],
    )
    with pytest.raises(ClientError) as exc:
        client.create_framework(
            FrameworkName="test-framework",
            FrameworkControls=[
                {"ControlName": "BACKUP_RESOURCES_PROTECTED_BY_BACKUP_PLAN"},
            ],
        )
    assert exc.value.response["Error"]["Code"] == "AlreadyExistsException"


@mock_aws
def test_describe_framework():
    client = boto3.client("backup", region_name="eu-west-1")
    created = client.create_framework(
        FrameworkName="test-framework",
        FrameworkControls=[
            {
                "ControlName": "BACKUP_RESOURCES_PROTECTED_BY_BACKUP_PLAN",
                "ControlScope": {
                    "ComplianceResourceTypes": ["AWS::DynamoDB::Table"],
                },
            },
        ],
        FrameworkDescription="A test framework",
    )
    resp = client.describe_framework(FrameworkName="test-framework")
    assert resp["FrameworkName"] == "test-framework"
    assert resp["FrameworkArn"] == created["FrameworkArn"]
    assert resp["FrameworkDescription"] == "A test framework"
    assert len(resp["FrameworkControls"]) == 1
    assert resp["FrameworkControls"][0]["ControlName"] == "BACKUP_RESOURCES_PROTECTED_BY_BACKUP_PLAN"
    assert resp["DeploymentStatus"] == "COMPLETED"
    assert "CreationTime" in resp


@mock_aws
def test_describe_framework_not_found():
    client = boto3.client("backup", region_name="eu-west-1")
    with pytest.raises(ClientError) as exc:
        client.describe_framework(FrameworkName="nonexistent-framework")
    assert exc.value.response["Error"]["Code"] == "ResourceNotFoundException"


@mock_aws
def test_delete_framework():
    client = boto3.client("backup", region_name="eu-west-1")
    client.create_framework(
        FrameworkName="test-framework",
        FrameworkControls=[
            {"ControlName": "BACKUP_RESOURCES_PROTECTED_BY_BACKUP_PLAN"},
        ],
    )
    client.delete_framework(FrameworkName="test-framework")
    with pytest.raises(ClientError) as exc:
        client.describe_framework(FrameworkName="test-framework")
    assert exc.value.response["Error"]["Code"] == "ResourceNotFoundException"


@mock_aws
def test_delete_framework_not_found():
    client = boto3.client("backup", region_name="eu-west-1")
    with pytest.raises(ClientError) as exc:
        client.delete_framework(FrameworkName="nonexistent-framework")
    assert exc.value.response["Error"]["Code"] == "ResourceNotFoundException"


@mock_aws
def test_list_frameworks():
    client = boto3.client("backup", region_name="eu-west-1")
    for i in range(3):
        client.create_framework(
            FrameworkName=f"framework-{i}",
            FrameworkControls=[
                {"ControlName": "BACKUP_RESOURCES_PROTECTED_BY_BACKUP_PLAN"},
            ],
            FrameworkDescription=f"Framework {i}",
        )
    resp = client.list_frameworks()
    assert len(resp["Frameworks"]) == 3
    names = [f["FrameworkName"] for f in resp["Frameworks"]]
    assert "framework-0" in names
    assert "framework-1" in names
    assert "framework-2" in names
    for f in resp["Frameworks"]:
        assert "FrameworkArn" in f
        assert "NumberOfControls" in f
        assert f["NumberOfControls"] == 1


@mock_aws
def test_list_frameworks_empty():
    client = boto3.client("backup", region_name="eu-west-1")
    resp = client.list_frameworks()
    assert resp["Frameworks"] == []


@mock_aws
def test_update_framework():
    client = boto3.client("backup", region_name="eu-west-1")
    client.create_framework(
        FrameworkName="test-framework",
        FrameworkControls=[
            {"ControlName": "BACKUP_RESOURCES_PROTECTED_BY_BACKUP_PLAN"},
        ],
        FrameworkDescription="Original description",
    )
    resp = client.update_framework(
        FrameworkName="test-framework",
        FrameworkDescription="Updated description",
        FrameworkControls=[
            {"ControlName": "BACKUP_RESOURCES_PROTECTED_BY_BACKUP_PLAN"},
            {"ControlName": "BACKUP_RECOVERY_POINT_MINIMUM_RETENTION_CHECK"},
        ],
    )
    assert resp["FrameworkName"] == "test-framework"
    assert "FrameworkArn" in resp

    described = client.describe_framework(FrameworkName="test-framework")
    assert described["FrameworkDescription"] == "Updated description"
    assert len(described["FrameworkControls"]) == 2


@mock_aws
def test_update_framework_not_found():
    client = boto3.client("backup", region_name="eu-west-1")
    with pytest.raises(ClientError) as exc:
        client.update_framework(
            FrameworkName="nonexistent-framework",
            FrameworkDescription="Updated",
        )
    assert exc.value.response["Error"]["Code"] == "ResourceNotFoundException"


@mock_aws
def test_framework_tagging():
    client = boto3.client("backup", region_name="eu-west-1")
    resp = client.create_framework(
        FrameworkName="test-framework",
        FrameworkControls=[
            {"ControlName": "BACKUP_RESOURCES_PROTECTED_BY_BACKUP_PLAN"},
        ],
        FrameworkTags={"env": "test", "team": "backend"},
    )
    tags = client.list_tags(ResourceArn=resp["FrameworkArn"])
    assert tags["Tags"] == {"env": "test", "team": "backend"}
