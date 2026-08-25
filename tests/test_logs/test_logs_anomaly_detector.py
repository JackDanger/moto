import boto3
import pytest
from botocore.exceptions import ClientError

from moto import mock_aws


@mock_aws
def test_create_log_anomaly_detector():
    client = boto3.client("logs", region_name="us-east-1")
    # Create a log group first
    client.create_log_group(logGroupName="/test/log-group")

    resp = client.create_log_anomaly_detector(
        logGroupArnList=[
            "arn:aws:logs:us-east-1:123456789012:log-group:/test/log-group"
        ],
        detectorName="my-detector",
        evaluationFrequency="FIVE_MIN",
        filterPattern="ERROR",
        anomalyVisibilityTime=7,
    )
    assert "anomalyDetectorArn" in resp
    assert "anomaly-detector" in resp["anomalyDetectorArn"]


@mock_aws
def test_get_log_anomaly_detector():
    client = boto3.client("logs", region_name="us-east-1")

    create_resp = client.create_log_anomaly_detector(
        logGroupArnList=[
            "arn:aws:logs:us-east-1:123456789012:log-group:/test/log-group"
        ],
        detectorName="my-detector",
        evaluationFrequency="TEN_MIN",
    )
    arn = create_resp["anomalyDetectorArn"]

    resp = client.get_log_anomaly_detector(anomalyDetectorArn=arn)
    assert resp["detectorName"] == "my-detector"
    assert resp["evaluationFrequency"] == "TEN_MIN"
    assert resp["anomalyDetectorStatus"] == "TRAINING"
    assert resp["anomalyVisibilityTime"] == 7
    assert len(resp["logGroupArnList"]) == 1


@mock_aws
def test_get_log_anomaly_detector_not_found():
    client = boto3.client("logs", region_name="us-east-1")
    with pytest.raises(ClientError) as exc:
        client.get_log_anomaly_detector(
            anomalyDetectorArn="arn:aws:logs:us-east-1:123456789012:anomaly-detector:nonexistent"
        )
    assert exc.value.response["Error"]["Code"] == "ResourceNotFoundException"


@mock_aws
def test_update_log_anomaly_detector():
    client = boto3.client("logs", region_name="us-east-1")

    create_resp = client.create_log_anomaly_detector(
        logGroupArnList=[
            "arn:aws:logs:us-east-1:123456789012:log-group:/test/log-group"
        ],
        detectorName="my-detector",
        evaluationFrequency="FIVE_MIN",
    )
    arn = create_resp["anomalyDetectorArn"]

    client.update_log_anomaly_detector(
        anomalyDetectorArn=arn,
        evaluationFrequency="ONE_HOUR",
        enabled=False,
    )

    resp = client.get_log_anomaly_detector(anomalyDetectorArn=arn)
    assert resp["evaluationFrequency"] == "ONE_HOUR"
    assert resp["anomalyDetectorStatus"] == "PAUSED"


@mock_aws
def test_delete_log_anomaly_detector():
    client = boto3.client("logs", region_name="us-east-1")

    create_resp = client.create_log_anomaly_detector(
        logGroupArnList=[
            "arn:aws:logs:us-east-1:123456789012:log-group:/test/log-group"
        ],
        detectorName="my-detector",
    )
    arn = create_resp["anomalyDetectorArn"]

    client.delete_log_anomaly_detector(anomalyDetectorArn=arn)

    with pytest.raises(ClientError) as exc:
        client.get_log_anomaly_detector(anomalyDetectorArn=arn)
    assert exc.value.response["Error"]["Code"] == "ResourceNotFoundException"


@mock_aws
def test_list_log_anomaly_detectors():
    client = boto3.client("logs", region_name="us-east-1")

    client.create_log_anomaly_detector(
        logGroupArnList=[
            "arn:aws:logs:us-east-1:123456789012:log-group:/test/group-1"
        ],
        detectorName="detector-1",
    )
    client.create_log_anomaly_detector(
        logGroupArnList=[
            "arn:aws:logs:us-east-1:123456789012:log-group:/test/group-2"
        ],
        detectorName="detector-2",
    )

    resp = client.list_log_anomaly_detectors()
    assert len(resp["anomalyDetectors"]) == 2


@mock_aws
def test_list_log_anomaly_detectors_filter():
    client = boto3.client("logs", region_name="us-east-1")

    group_1_arn = "arn:aws:logs:us-east-1:123456789012:log-group:/test/group-1"
    group_2_arn = "arn:aws:logs:us-east-1:123456789012:log-group:/test/group-2"

    client.create_log_anomaly_detector(
        logGroupArnList=[group_1_arn],
        detectorName="detector-1",
    )
    client.create_log_anomaly_detector(
        logGroupArnList=[group_2_arn],
        detectorName="detector-2",
    )

    resp = client.list_log_anomaly_detectors(
        filterLogGroupArn=group_1_arn,
    )
    assert len(resp["anomalyDetectors"]) == 1
    assert resp["anomalyDetectors"][0]["detectorName"] == "detector-1"


@mock_aws
def test_list_log_anomaly_detectors_empty():
    client = boto3.client("logs", region_name="us-east-1")
    resp = client.list_log_anomaly_detectors()
    assert resp["anomalyDetectors"] == []
