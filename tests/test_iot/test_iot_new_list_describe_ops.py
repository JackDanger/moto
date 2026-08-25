"""Tests for newly implemented IoT List and Describe operations."""

import boto3
import pytest

from moto import mock_aws


# --- Streams ---


@mock_aws
def test_list_streams_empty():
    client = boto3.client("iot", region_name="us-east-1")
    result = client.list_streams()
    assert result["streams"] == []


@mock_aws
def test_create_and_list_streams():
    client = boto3.client("iot", region_name="us-east-1")
    client.create_stream(
        streamId="test-stream",
        description="A test stream",
        files=[{"fileId": 1, "s3Location": {"bucket": "mybucket", "key": "mykey"}}],
        roleArn="arn:aws:iam::123456789012:role/test-role",
    )
    result = client.list_streams()
    assert len(result["streams"]) == 1
    assert result["streams"][0]["streamId"] == "test-stream"
    assert "streamArn" in result["streams"][0]


@mock_aws
def test_describe_stream():
    client = boto3.client("iot", region_name="us-east-1")
    client.create_stream(
        streamId="test-stream",
        description="A test stream",
        files=[{"fileId": 1, "s3Location": {"bucket": "mybucket", "key": "mykey"}}],
        roleArn="arn:aws:iam::123456789012:role/test-role",
    )
    result = client.describe_stream(streamId="test-stream")
    info = result["streamInfo"]
    assert info["streamId"] == "test-stream"
    assert info["description"] == "A test stream"
    assert len(info["files"]) == 1
    assert "streamArn" in info


@mock_aws
def test_describe_stream_not_found():
    client = boto3.client("iot", region_name="us-east-1")
    with pytest.raises(client.exceptions.ResourceNotFoundException):
        client.describe_stream(streamId="nonexistent")


@mock_aws
def test_delete_stream():
    client = boto3.client("iot", region_name="us-east-1")
    client.create_stream(
        streamId="test-stream",
        files=[{"fileId": 1, "s3Location": {"bucket": "mybucket", "key": "mykey"}}],
        roleArn="arn:aws:iam::123456789012:role/test-role",
    )
    client.delete_stream(streamId="test-stream")
    result = client.list_streams()
    assert len(result["streams"]) == 0


# --- Mitigation Actions ---


@mock_aws
def test_list_mitigation_actions_empty():
    client = boto3.client("iot", region_name="us-east-1")
    result = client.list_mitigation_actions()
    assert result["actionIdentifiers"] == []


@mock_aws
def test_create_and_list_mitigation_actions():
    client = boto3.client("iot", region_name="us-east-1")
    client.create_mitigation_action(
        actionName="test-action",
        roleArn="arn:aws:iam::123456789012:role/test-role",
        actionParams={
            "updateDeviceCertificateParams": {"action": "DEACTIVATE"}
        },
    )
    result = client.list_mitigation_actions()
    assert len(result["actionIdentifiers"]) == 1
    assert result["actionIdentifiers"][0]["actionName"] == "test-action"


@mock_aws
def test_describe_mitigation_action():
    client = boto3.client("iot", region_name="us-east-1")
    client.create_mitigation_action(
        actionName="test-action",
        roleArn="arn:aws:iam::123456789012:role/test-role",
        actionParams={
            "updateDeviceCertificateParams": {"action": "DEACTIVATE"}
        },
    )
    result = client.describe_mitigation_action(actionName="test-action")
    assert result["actionName"] == "test-action"
    assert "actionArn" in result
    assert "actionId" in result
    assert result["roleArn"] == "arn:aws:iam::123456789012:role/test-role"


@mock_aws
def test_describe_mitigation_action_not_found():
    client = boto3.client("iot", region_name="us-east-1")
    with pytest.raises(client.exceptions.ResourceNotFoundException):
        client.describe_mitigation_action(actionName="nonexistent")


# --- Scheduled Audits ---


@mock_aws
def test_list_scheduled_audits_empty():
    client = boto3.client("iot", region_name="us-east-1")
    result = client.list_scheduled_audits()
    assert result["scheduledAudits"] == []


@mock_aws
def test_create_and_list_scheduled_audits():
    client = boto3.client("iot", region_name="us-east-1")
    client.create_scheduled_audit(
        scheduledAuditName="test-audit",
        frequency="DAILY",
        targetCheckNames=["DEVICE_CERTIFICATE_EXPIRING_CHECK"],
    )
    result = client.list_scheduled_audits()
    assert len(result["scheduledAudits"]) == 1
    assert result["scheduledAudits"][0]["scheduledAuditName"] == "test-audit"
    assert result["scheduledAudits"][0]["frequency"] == "DAILY"


@mock_aws
def test_describe_scheduled_audit():
    client = boto3.client("iot", region_name="us-east-1")
    client.create_scheduled_audit(
        scheduledAuditName="test-audit",
        frequency="WEEKLY",
        dayOfWeek="MON",
        targetCheckNames=["DEVICE_CERTIFICATE_EXPIRING_CHECK"],
    )
    result = client.describe_scheduled_audit(scheduledAuditName="test-audit")
    assert result["scheduledAuditName"] == "test-audit"
    assert result["frequency"] == "WEEKLY"
    assert result["dayOfWeek"] == "MON"
    assert "scheduledAuditArn" in result


@mock_aws
def test_describe_scheduled_audit_not_found():
    client = boto3.client("iot", region_name="us-east-1")
    with pytest.raises(client.exceptions.ResourceNotFoundException):
        client.describe_scheduled_audit(scheduledAuditName="nonexistent")


# --- OTA Updates ---


@mock_aws
def test_list_ota_updates_empty():
    client = boto3.client("iot", region_name="us-east-1")
    result = client.list_ota_updates()
    assert result["otaUpdates"] == []


@mock_aws
def test_create_and_list_ota_updates():
    client = boto3.client("iot", region_name="us-east-1")
    client.create_ota_update(
        otaUpdateId="test-ota",
        targets=["arn:aws:iot:us-east-1:123456789012:thing/myThing"],
        files=[
            {
                "fileName": "firmware.bin",
                "fileLocation": {
                    "s3Location": {"bucket": "mybucket", "key": "firmware.bin"},
                },
                "fileType": 0,
            }
        ],
        roleArn="arn:aws:iam::123456789012:role/test-role",
    )
    result = client.list_ota_updates()
    assert len(result["otaUpdates"]) == 1
    assert result["otaUpdates"][0]["otaUpdateId"] == "test-ota"


# --- CA Certificates listing ---


@mock_aws
def test_list_ca_certificates_empty():
    client = boto3.client("iot", region_name="us-east-1")
    result = client.list_ca_certificates()
    assert result["certificates"] == []


# --- Provisioning Template Versions ---


@mock_aws
def test_list_provisioning_template_versions():
    client = boto3.client("iot", region_name="us-east-1")
    client.create_provisioning_template(
        templateName="test-template",
        templateBody='{"Parameters":{"AWS::IoT::Certificate::Id":{"Type":"String"}}}',
        provisioningRoleArn="arn:aws:iam::123456789012:role/test-role",
    )
    result = client.list_provisioning_template_versions(templateName="test-template")
    assert len(result["versions"]) == 1
    assert result["versions"][0]["versionId"] == 1
    assert result["versions"][0]["isDefaultVersion"] is True


@mock_aws
def test_list_provisioning_template_versions_not_found():
    client = boto3.client("iot", region_name="us-east-1")
    with pytest.raises(client.exceptions.ResourceNotFoundException):
        client.list_provisioning_template_versions(templateName="nonexistent")


@mock_aws
def test_describe_provisioning_template_version():
    client = boto3.client("iot", region_name="us-east-1")
    client.create_provisioning_template(
        templateName="test-template",
        templateBody='{"Parameters":{"AWS::IoT::Certificate::Id":{"Type":"String"}}}',
        provisioningRoleArn="arn:aws:iam::123456789012:role/test-role",
    )
    result = client.describe_provisioning_template_version(
        templateName="test-template", versionId=1
    )
    assert result["versionId"] == 1
    assert result["isDefaultVersion"] is True
    assert "templateBody" in result


@mock_aws
def test_describe_provisioning_template_version_not_found():
    client = boto3.client("iot", region_name="us-east-1")
    client.create_provisioning_template(
        templateName="test-template",
        templateBody='{"Parameters":{"AWS::IoT::Certificate::Id":{"Type":"String"}}}',
        provisioningRoleArn="arn:aws:iam::123456789012:role/test-role",
    )
    with pytest.raises(client.exceptions.ResourceNotFoundException):
        client.describe_provisioning_template_version(
            templateName="test-template", versionId=999
        )


# --- Account Audit Configuration ---


@mock_aws
def test_describe_account_audit_configuration_default():
    client = boto3.client("iot", region_name="us-east-1")
    result = client.describe_account_audit_configuration()
    assert "roleArn" in result
    assert "auditCheckConfigurations" in result


@mock_aws
def test_update_and_describe_account_audit_configuration():
    client = boto3.client("iot", region_name="us-east-1")
    client.update_account_audit_configuration(
        roleArn="arn:aws:iam::123456789012:role/audit-role",
        auditCheckConfigurations={
            "DEVICE_CERTIFICATE_EXPIRING_CHECK": {"enabled": True}
        },
    )
    result = client.describe_account_audit_configuration()
    assert result["roleArn"] == "arn:aws:iam::123456789012:role/audit-role"
    assert "DEVICE_CERTIFICATE_EXPIRING_CHECK" in result["auditCheckConfigurations"]


# --- Describe stubs (should raise ResourceNotFoundException) ---


@mock_aws
def test_describe_audit_finding_not_found():
    client = boto3.client("iot", region_name="us-east-1")
    with pytest.raises(client.exceptions.ResourceNotFoundException):
        client.describe_audit_finding(findingId="nonexistent-finding-id")


@mock_aws
def test_describe_audit_mitigation_actions_task_not_found():
    client = boto3.client("iot", region_name="us-east-1")
    with pytest.raises(client.exceptions.ResourceNotFoundException):
        client.describe_audit_mitigation_actions_task(taskId="nonexistent-task-id")


@mock_aws
def test_describe_audit_suppression_not_found():
    client = boto3.client("iot", region_name="us-east-1")
    with pytest.raises(client.exceptions.ResourceNotFoundException):
        client.describe_audit_suppression(
            checkName="DEVICE_CERTIFICATE_EXPIRING_CHECK",
            resourceIdentifier={"deviceCertificateId": "a" * 64},
        )


@mock_aws
def test_describe_audit_task_not_found():
    client = boto3.client("iot", region_name="us-east-1")
    with pytest.raises(client.exceptions.ResourceNotFoundException):
        client.describe_audit_task(taskId="nonexistent-task-id")


@mock_aws
def test_describe_detect_mitigation_actions_task_not_found():
    client = boto3.client("iot", region_name="us-east-1")
    with pytest.raises(client.exceptions.ResourceNotFoundException):
        client.describe_detect_mitigation_actions_task(taskId="nonexistent-task-id")


# --- Empty list stubs ---


@mock_aws
def test_list_active_violations_empty():
    client = boto3.client("iot", region_name="us-east-1")
    result = client.list_active_violations()
    assert result["activeViolations"] == []


@mock_aws
def test_list_violation_events_empty():
    client = boto3.client("iot", region_name="us-east-1")
    result = client.list_violation_events(
        startTime="2024-01-01T00:00:00Z",
        endTime="2024-12-31T23:59:59Z",
    )
    assert result["violationEvents"] == []


@mock_aws
def test_list_metric_values_empty():
    client = boto3.client("iot", region_name="us-east-1")
    result = client.list_metric_values(
        thingName="myThing",
        metricName="myMetric",
        startTime="2024-01-01T00:00:00Z",
        endTime="2024-12-31T23:59:59Z",
    )
    assert result["metricDatumList"] == []


@mock_aws
def test_list_related_resources_for_audit_finding_empty():
    client = boto3.client("iot", region_name="us-east-1")
    result = client.list_related_resources_for_audit_finding(
        findingId="test-finding-id"
    )
    assert result["relatedResources"] == []


@mock_aws
def test_list_managed_job_templates_empty():
    client = boto3.client("iot", region_name="us-east-1")
    result = client.list_managed_job_templates()
    assert result["managedJobTemplates"] == []


@mock_aws
def test_describe_managed_job_template_not_found():
    client = boto3.client("iot", region_name="us-east-1")
    with pytest.raises(client.exceptions.ResourceNotFoundException):
        client.describe_managed_job_template(templateName="nonexistent")


# --- Existing audit/detect list ops (already had backend, just needed responses) ---


@mock_aws
def test_list_audit_findings_empty():
    client = boto3.client("iot", region_name="us-east-1")
    result = client.list_audit_findings()
    assert result["findings"] == []


@mock_aws
def test_list_audit_mitigation_actions_executions_empty():
    client = boto3.client("iot", region_name="us-east-1")
    result = client.list_audit_mitigation_actions_executions(
        taskId="test-task", findingId="test-finding"
    )
    assert result["actionsExecutions"] == []


@mock_aws
def test_list_audit_mitigation_actions_tasks_empty():
    client = boto3.client("iot", region_name="us-east-1")
    result = client.list_audit_mitigation_actions_tasks(
        startTime="2024-01-01T00:00:00Z",
        endTime="2024-12-31T23:59:59Z",
    )
    assert result["tasks"] == []


@mock_aws
def test_list_audit_suppressions_empty():
    client = boto3.client("iot", region_name="us-east-1")
    result = client.list_audit_suppressions()
    assert result["suppressions"] == []


@mock_aws
def test_list_audit_tasks_empty():
    client = boto3.client("iot", region_name="us-east-1")
    result = client.list_audit_tasks(
        startTime="2024-01-01T00:00:00Z",
        endTime="2024-12-31T23:59:59Z",
    )
    assert result["tasks"] == []


@mock_aws
def test_list_detect_mitigation_actions_executions_empty():
    client = boto3.client("iot", region_name="us-east-1")
    result = client.list_detect_mitigation_actions_executions()
    assert result["actionsExecutions"] == []


@mock_aws
def test_list_detect_mitigation_actions_tasks_empty():
    client = boto3.client("iot", region_name="us-east-1")
    result = client.list_detect_mitigation_actions_tasks(
        startTime="2024-01-01T00:00:00Z",
        endTime="2024-12-31T23:59:59Z",
    )
    assert result["tasks"] == []
