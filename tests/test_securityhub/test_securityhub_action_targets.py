import boto3
import pytest
from botocore.exceptions import ClientError
from moto import mock_aws


@mock_aws
def test_create_action_target():
    client = boto3.client("securityhub", region_name="us-east-1")
    client.enable_security_hub()

    resp = client.create_action_target(
        Name="test-target", Description="A test action target", Id="test1"
    )
    assert "ActionTargetArn" in resp
    assert "action/custom/test1" in resp["ActionTargetArn"]


@mock_aws
def test_describe_action_targets():
    client = boto3.client("securityhub", region_name="us-east-1")
    client.enable_security_hub()

    arn = client.create_action_target(
        Name="target-1", Description="First target", Id="t1"
    )["ActionTargetArn"]

    client.create_action_target(
        Name="target-2", Description="Second target", Id="t2"
    )

    # Describe all
    resp = client.describe_action_targets()
    assert len(resp["ActionTargets"]) == 2

    # Describe specific
    resp = client.describe_action_targets(ActionTargetArns=[arn])
    assert len(resp["ActionTargets"]) == 1
    assert resp["ActionTargets"][0]["Name"] == "target-1"


@mock_aws
def test_describe_action_targets_not_found():
    client = boto3.client("securityhub", region_name="us-east-1")
    client.enable_security_hub()

    with pytest.raises(ClientError) as exc:
        client.describe_action_targets(
            ActionTargetArns=[
                "arn:aws:securityhub:us-east-1:123456789012:action/custom/nonexistent"
            ]
        )
    assert exc.value.response["Error"]["Code"] == "ResourceNotFoundException"


@mock_aws
def test_update_action_target():
    client = boto3.client("securityhub", region_name="us-east-1")
    client.enable_security_hub()

    arn = client.create_action_target(
        Name="original", Description="Original desc", Id="t1"
    )["ActionTargetArn"]

    client.update_action_target(
        ActionTargetArn=arn, Name="updated", Description="Updated desc"
    )

    resp = client.describe_action_targets(ActionTargetArns=[arn])
    assert resp["ActionTargets"][0]["Name"] == "updated"
    assert resp["ActionTargets"][0]["Description"] == "Updated desc"


@mock_aws
def test_delete_action_target():
    client = boto3.client("securityhub", region_name="us-east-1")
    client.enable_security_hub()

    arn = client.create_action_target(
        Name="target", Description="To delete", Id="t1"
    )["ActionTargetArn"]

    resp = client.delete_action_target(ActionTargetArn=arn)
    assert resp["ActionTargetArn"] == arn

    # Verify it's gone
    resp = client.describe_action_targets()
    assert len(resp["ActionTargets"]) == 0


@mock_aws
def test_delete_action_target_not_found():
    client = boto3.client("securityhub", region_name="us-east-1")
    client.enable_security_hub()

    with pytest.raises(ClientError) as exc:
        client.delete_action_target(
            ActionTargetArn="arn:aws:securityhub:us-east-1:123456789012:action/custom/nonexistent"
        )
    assert exc.value.response["Error"]["Code"] == "ResourceNotFoundException"


@mock_aws
def test_create_duplicate_action_target():
    client = boto3.client("securityhub", region_name="us-east-1")
    client.enable_security_hub()

    client.create_action_target(
        Name="target", Description="First", Id="t1"
    )

    with pytest.raises(ClientError) as exc:
        client.create_action_target(
            Name="target-dup", Description="Duplicate", Id="t1"
        )
    assert exc.value.response["Error"]["Code"] == "ResourceConflictException"


@mock_aws
def test_batch_update_findings():
    client = boto3.client("securityhub", region_name="us-east-1")
    client.enable_security_hub()

    # Import a finding first
    client.batch_import_findings(
        Findings=[
            {
                "SchemaVersion": "2018-10-08",
                "Id": "finding-1",
                "ProductArn": "arn:aws:securityhub:us-east-1:123456789012:product/aws/inspector",
                "GeneratorId": "gen-1",
                "AwsAccountId": "123456789012",
                "Types": ["Software and Configuration Checks"],
                "CreatedAt": "2024-01-01T00:00:00Z",
                "UpdatedAt": "2024-01-01T00:00:00Z",
                "Severity": {"Label": "HIGH"},
                "Title": "Test Finding",
                "Description": "A test finding",
                "Resources": [
                    {
                        "Type": "AwsEc2Instance",
                        "Id": "arn:aws:ec2:us-east-1:123456789012:instance/i-12345",
                    }
                ],
            }
        ]
    )

    # Update the finding
    resp = client.batch_update_findings(
        FindingIdentifiers=[
            {
                "Id": "finding-1",
                "ProductArn": "arn:aws:securityhub:us-east-1:123456789012:product/aws/inspector",
            }
        ],
        Note={"Text": "Updated via test", "UpdatedBy": "tester"},
        Severity={"Label": "CRITICAL"},
        Workflow={"Status": "RESOLVED"},
    )
    assert len(resp["ProcessedFindings"]) == 1
    assert len(resp["UnprocessedFindings"]) == 0

    # Verify update
    findings = client.get_findings()["Findings"]
    assert len(findings) == 1
    assert findings[0]["Note"]["Text"] == "Updated via test"
    assert findings[0]["Severity"]["Label"] == "CRITICAL"
    assert findings[0]["Workflow"]["Status"] == "RESOLVED"


@mock_aws
def test_batch_update_findings_not_found():
    client = boto3.client("securityhub", region_name="us-east-1")
    client.enable_security_hub()

    resp = client.batch_update_findings(
        FindingIdentifiers=[
            {
                "Id": "nonexistent",
                "ProductArn": "arn:aws:securityhub:us-east-1:123456789012:product/aws/inspector",
            }
        ],
        Note={"Text": "Should fail", "UpdatedBy": "tester"},
    )
    assert len(resp["ProcessedFindings"]) == 0
    assert len(resp["UnprocessedFindings"]) == 1
    assert resp["UnprocessedFindings"][0]["ErrorCode"] == "FindingNotFound"


@mock_aws
def test_enable_disable_product_subscription():
    client = boto3.client("securityhub", region_name="us-east-1")
    client.enable_security_hub()

    resp = client.enable_import_findings_for_product(
        ProductArn="arn:aws:securityhub:us-east-1::product/aws/inspector"
    )
    subscription_arn = resp["ProductSubscriptionArn"]
    assert "product-subscription" in subscription_arn

    # List
    resp = client.list_enabled_products_for_import()
    assert subscription_arn in resp["ProductSubscriptions"]

    # Disable
    client.disable_import_findings_for_product(
        ProductSubscriptionArn=subscription_arn
    )
    resp = client.list_enabled_products_for_import()
    assert len(resp["ProductSubscriptions"]) == 0


@mock_aws
def test_securityhub_tagging():
    client = boto3.client("securityhub", region_name="us-east-1")
    client.enable_security_hub(Tags={"env": "test"})

    hub_arn = "arn:aws:securityhub:us-east-1:123456789012:hub/default"

    # List tags
    resp = client.list_tags_for_resource(ResourceArn=hub_arn)
    assert resp["Tags"]["env"] == "test"

    # Add tags
    client.tag_resource(ResourceArn=hub_arn, Tags={"team": "security"})
    resp = client.list_tags_for_resource(ResourceArn=hub_arn)
    assert resp["Tags"]["team"] == "security"
    assert resp["Tags"]["env"] == "test"

    # Remove tags
    client.untag_resource(ResourceArn=hub_arn, TagKeys=["env"])
    resp = client.list_tags_for_resource(ResourceArn=hub_arn)
    assert "env" not in resp["Tags"]
    assert resp["Tags"]["team"] == "security"
