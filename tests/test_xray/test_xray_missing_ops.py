import json

import boto3

from moto import mock_aws


@mock_aws
def test_create_and_get_group():
    client = boto3.client("xray", region_name="us-east-1")

    resp = client.create_group(
        GroupName="test-group",
        FilterExpression='service("example.com")',
    )
    group = resp["Group"]
    assert group["GroupName"] == "test-group"
    assert group["FilterExpression"] == 'service("example.com")'
    assert "GroupARN" in group

    resp = client.get_group(GroupName="test-group")
    assert resp["Group"]["GroupName"] == "test-group"


@mock_aws
def test_get_groups():
    client = boto3.client("xray", region_name="us-east-1")

    client.create_group(GroupName="group-1")
    client.create_group(GroupName="group-2")

    resp = client.get_groups()
    names = [g["GroupName"] for g in resp["Groups"]]
    assert "group-1" in names
    assert "group-2" in names


@mock_aws
def test_update_group():
    client = boto3.client("xray", region_name="us-east-1")

    client.create_group(GroupName="test-group", FilterExpression="old-filter")
    resp = client.update_group(
        GroupName="test-group", FilterExpression="new-filter"
    )
    assert resp["Group"]["FilterExpression"] == "new-filter"

    # Verify with get
    resp = client.get_group(GroupName="test-group")
    assert resp["Group"]["FilterExpression"] == "new-filter"


@mock_aws
def test_delete_group():
    client = boto3.client("xray", region_name="us-east-1")

    client.create_group(GroupName="test-group")
    client.delete_group(GroupName="test-group")

    resp = client.get_groups()
    assert len(resp["Groups"]) == 0


@mock_aws
def test_create_and_get_sampling_rule():
    client = boto3.client("xray", region_name="us-east-1")

    resp = client.create_sampling_rule(
        SamplingRule={
            "RuleName": "test-rule",
            "ResourceARN": "*",
            "Priority": 1000,
            "FixedRate": 0.05,
            "ReservoirSize": 1,
            "ServiceName": "*",
            "ServiceType": "*",
            "Host": "*",
            "HTTPMethod": "*",
            "URLPath": "*",
            "Version": 1,
        }
    )
    record = resp["SamplingRuleRecord"]
    assert record["SamplingRule"]["RuleName"] == "test-rule"
    assert record["SamplingRule"]["FixedRate"] == 0.05
    assert "CreatedAt" in record

    resp = client.get_sampling_rules()
    assert len(resp["SamplingRuleRecords"]) == 1
    assert resp["SamplingRuleRecords"][0]["SamplingRule"]["RuleName"] == "test-rule"


@mock_aws
def test_update_sampling_rule():
    client = boto3.client("xray", region_name="us-east-1")

    client.create_sampling_rule(
        SamplingRule={
            "RuleName": "test-rule",
            "ResourceARN": "*",
            "Priority": 1000,
            "FixedRate": 0.05,
            "ReservoirSize": 1,
            "ServiceName": "*",
            "ServiceType": "*",
            "Host": "*",
            "HTTPMethod": "*",
            "URLPath": "*",
            "Version": 1,
        }
    )

    resp = client.update_sampling_rule(
        SamplingRuleUpdate={
            "RuleName": "test-rule",
            "FixedRate": 0.10,
            "ReservoirSize": 5,
        }
    )
    record = resp["SamplingRuleRecord"]
    assert record["SamplingRule"]["FixedRate"] == 0.10
    assert record["SamplingRule"]["ReservoirSize"] == 5


@mock_aws
def test_delete_sampling_rule():
    client = boto3.client("xray", region_name="us-east-1")

    client.create_sampling_rule(
        SamplingRule={
            "RuleName": "test-rule",
            "ResourceARN": "*",
            "Priority": 1000,
            "FixedRate": 0.05,
            "ReservoirSize": 1,
            "ServiceName": "*",
            "ServiceType": "*",
            "Host": "*",
            "HTTPMethod": "*",
            "URLPath": "*",
            "Version": 1,
        }
    )

    resp = client.delete_sampling_rule(RuleName="test-rule")
    assert resp["SamplingRuleRecord"]["SamplingRule"]["RuleName"] == "test-rule"

    resp = client.get_sampling_rules()
    assert len(resp["SamplingRuleRecords"]) == 0


@mock_aws
def test_get_sampling_statistic_summaries():
    client = boto3.client("xray", region_name="us-east-1")

    resp = client.get_sampling_statistic_summaries()
    assert "SamplingStatisticSummaries" in resp
    assert resp["SamplingStatisticSummaries"] == []


@mock_aws
def test_encryption_config():
    client = boto3.client("xray", region_name="us-east-1")

    resp = client.get_encryption_config()
    assert resp["EncryptionConfig"]["Type"] == "NONE"
    assert resp["EncryptionConfig"]["Status"] == "ACTIVE"

    resp = client.put_encryption_config(Type="KMS", KeyId="alias/my-key")
    assert resp["EncryptionConfig"]["Type"] == "KMS"
    assert resp["EncryptionConfig"]["KeyId"] == "alias/my-key"

    resp = client.get_encryption_config()
    assert resp["EncryptionConfig"]["Type"] == "KMS"


@mock_aws
def test_get_trace_segment_destination():
    client = boto3.client("xray", region_name="us-east-1")

    resp = client.get_trace_segment_destination()
    assert resp["Destination"] == "XRay"
    assert resp["Status"] == "ACTIVE"


@mock_aws
def test_update_trace_segment_destination():
    client = boto3.client("xray", region_name="us-east-1")

    resp = client.update_trace_segment_destination(Destination="CloudWatchLogs")
    assert resp["Destination"] == "CloudWatchLogs"
    assert resp["Status"] == "ACTIVE"

    resp = client.get_trace_segment_destination()
    assert resp["Destination"] == "CloudWatchLogs"


@mock_aws
def test_update_indexing_rule():
    client = boto3.client("xray", region_name="us-east-1")

    resp = client.get_indexing_rules()
    assert len(resp["IndexingRules"]) == 1

    resp = client.update_indexing_rule(
        Name="Default",
        Rule={"Probabilistic": {"DesiredSamplingPercentage": 50.0}},
    )
    rule = resp["IndexingRule"]
    assert rule["Name"] == "Default"
    assert rule["Rule"]["Probabilistic"]["DesiredSamplingPercentage"] == 50.0


@mock_aws
def test_put_telemetry_records():
    """PutTelemetryRecords is already implemented - verify it works."""
    client = boto3.client("xray", region_name="us-east-1")

    client.put_telemetry_records(
        TelemetryRecords=[
            {
                "Timestamp": 1234567890.0,
                "SegmentsReceivedCount": 10,
                "SegmentsSentCount": 10,
                "SegmentsSpilloverCount": 0,
                "SegmentsRejectedCount": 0,
                "BackendConnectionErrors": {
                    "TimeoutCount": 0,
                    "ConnectionRefusedCount": 0,
                    "HTTPCode4XXCount": 0,
                    "HTTPCode5XXCount": 0,
                    "UnknownHostCount": 0,
                    "OtherCount": 0,
                },
            }
        ],
        Hostname="test-host",
        ResourceARN="arn:aws:ec2:us-east-1:123456789012:instance/i-1234",
    )
    # PutTelemetryRecords returns empty body on success


@mock_aws
def test_batch_get_traces():
    """BatchGetTraces is already implemented - verify it works."""
    client = boto3.client("xray", region_name="us-east-1")

    # Put some trace segments first
    client.put_trace_segments(
        TraceSegmentDocuments=[
            json.dumps(
                {
                    "name": "example.com",
                    "id": "70de5b6f19ff9a0a",
                    "start_time": 1478293365,
                    "trace_id": "1-581cf771-a006649127e371903a2de979",
                    "end_time": 1478293385,
                }
            )
        ]
    )

    resp = client.batch_get_traces(
        TraceIds=["1-581cf771-a006649127e371903a2de979", "1-nonexistent"]
    )
    assert len(resp["Traces"]) == 1
    assert len(resp["UnprocessedTraceIds"]) == 1
    assert resp["Traces"][0]["Id"] == "1-581cf771-a006649127e371903a2de979"


@mock_aws
def test_get_trace_graph():
    """GetTraceGraph is already implemented - verify it works."""
    client = boto3.client("xray", region_name="us-east-1")

    resp = client.get_trace_graph(
        TraceIds=["1-581cf771-a006649127e371903a2de979"]
    )
    assert "Services" in resp
