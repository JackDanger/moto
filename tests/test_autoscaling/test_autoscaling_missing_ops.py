import boto3
import pytest
from botocore.exceptions import ClientError

from moto import mock_aws
from tests import EXAMPLE_AMI_ID

from .utils import setup_networking


def _create_asg_with_lc(client, name="test-asg", region="us-east-1"):
    """Helper to create an ASG with a launch configuration."""
    mocked_networking = setup_networking(region)
    client.create_launch_configuration(
        LaunchConfigurationName="test-lc",
        ImageId=EXAMPLE_AMI_ID,
        InstanceType="t2.micro",
    )
    client.create_auto_scaling_group(
        AutoScalingGroupName=name,
        LaunchConfigurationName="test-lc",
        MinSize=1,
        MaxSize=3,
        VPCZoneIdentifier=mocked_networking["subnet1"],
    )
    return mocked_networking


# --- DisableMetricsCollection ---


@mock_aws
def test_disable_metrics_collection_specific():
    client = boto3.client("autoscaling", region_name="us-east-1")
    _create_asg_with_lc(client)

    client.enable_metrics_collection(
        AutoScalingGroupName="test-asg",
        Metrics=["GroupMinSize", "GroupMaxSize", "GroupDesiredCapacity"],
        Granularity="1Minute",
    )

    # Verify metrics are enabled
    groups = client.describe_auto_scaling_groups(AutoScalingGroupNames=["test-asg"])
    enabled = {m["Metric"] for m in groups["AutoScalingGroups"][0]["EnabledMetrics"]}
    assert "GroupMinSize" in enabled
    assert "GroupMaxSize" in enabled

    # Disable specific metrics
    client.disable_metrics_collection(
        AutoScalingGroupName="test-asg",
        Metrics=["GroupMinSize"],
    )

    groups = client.describe_auto_scaling_groups(AutoScalingGroupNames=["test-asg"])
    enabled = {m["Metric"] for m in groups["AutoScalingGroups"][0]["EnabledMetrics"]}
    assert "GroupMinSize" not in enabled
    assert "GroupMaxSize" in enabled
    assert "GroupDesiredCapacity" in enabled


@mock_aws
def test_disable_metrics_collection_all():
    client = boto3.client("autoscaling", region_name="us-east-1")
    _create_asg_with_lc(client)

    client.enable_metrics_collection(
        AutoScalingGroupName="test-asg",
        Metrics=["GroupMinSize", "GroupMaxSize"],
        Granularity="1Minute",
    )
    # Disable all
    client.disable_metrics_collection(AutoScalingGroupName="test-asg")

    groups = client.describe_auto_scaling_groups(AutoScalingGroupNames=["test-asg"])
    assert groups["AutoScalingGroups"][0]["EnabledMetrics"] == []


# --- CompleteLifecycleAction ---


@mock_aws
def test_complete_lifecycle_action():
    client = boto3.client("autoscaling", region_name="us-east-1")
    _create_asg_with_lc(client)

    client.put_lifecycle_hook(
        AutoScalingGroupName="test-asg",
        LifecycleHookName="test-hook",
        LifecycleTransition="autoscaling:EC2_INSTANCE_LAUNCHING",
    )

    resp = client.complete_lifecycle_action(
        LifecycleHookName="test-hook",
        AutoScalingGroupName="test-asg",
        LifecycleActionResult="CONTINUE",
    )
    assert resp["ResponseMetadata"]["HTTPStatusCode"] == 200


@mock_aws
def test_complete_lifecycle_action_bad_hook():
    client = boto3.client("autoscaling", region_name="us-east-1")
    _create_asg_with_lc(client)

    with pytest.raises(ClientError) as exc:
        client.complete_lifecycle_action(
            LifecycleHookName="nonexistent-hook",
            AutoScalingGroupName="test-asg",
            LifecycleActionResult="CONTINUE",
        )
    assert exc.value.response["Error"]["Code"] == "ValidationError"


# --- RecordLifecycleActionHeartbeat ---


@mock_aws
def test_record_lifecycle_action_heartbeat():
    client = boto3.client("autoscaling", region_name="us-east-1")
    _create_asg_with_lc(client)

    client.put_lifecycle_hook(
        AutoScalingGroupName="test-asg",
        LifecycleHookName="test-hook",
        LifecycleTransition="autoscaling:EC2_INSTANCE_LAUNCHING",
    )

    resp = client.record_lifecycle_action_heartbeat(
        LifecycleHookName="test-hook",
        AutoScalingGroupName="test-asg",
    )
    assert resp["ResponseMetadata"]["HTTPStatusCode"] == 200


@mock_aws
def test_record_lifecycle_action_heartbeat_bad_hook():
    client = boto3.client("autoscaling", region_name="us-east-1")
    _create_asg_with_lc(client)

    with pytest.raises(ClientError) as exc:
        client.record_lifecycle_action_heartbeat(
            LifecycleHookName="nonexistent-hook",
            AutoScalingGroupName="test-asg",
        )
    assert exc.value.response["Error"]["Code"] == "ValidationError"


# --- RollbackInstanceRefresh ---


@mock_aws
def test_rollback_instance_refresh():
    client = boto3.client("autoscaling", region_name="us-east-1")
    _create_asg_with_lc(client)

    start_resp = client.start_instance_refresh(
        AutoScalingGroupName="test-asg",
    )
    refresh_id = start_resp["InstanceRefreshId"]

    rollback_resp = client.rollback_instance_refresh(
        AutoScalingGroupName="test-asg",
    )
    assert rollback_resp["InstanceRefreshId"] == refresh_id

    # Verify status changed
    desc = client.describe_instance_refreshes(AutoScalingGroupName="test-asg")
    statuses = {r["InstanceRefreshId"]: r["Status"] for r in desc["InstanceRefreshes"]}
    assert statuses[refresh_id] == "RollbackInProgress"


@mock_aws
def test_rollback_instance_refresh_no_active():
    client = boto3.client("autoscaling", region_name="us-east-1")
    _create_asg_with_lc(client)

    with pytest.raises(ClientError) as exc:
        client.rollback_instance_refresh(AutoScalingGroupName="test-asg")
    assert exc.value.response["Error"]["Code"] == "ResourceContention"


# --- Traffic Sources ---


@mock_aws
def test_attach_describe_detach_traffic_sources():
    client = boto3.client("autoscaling", region_name="us-east-1")
    _create_asg_with_lc(client)

    # Attach
    client.attach_traffic_sources(
        AutoScalingGroupName="test-asg",
        TrafficSources=[
            {"Identifier": "arn:aws:elasticloadbalancing:us-east-1:123456789012:targetgroup/my-tg/abc123", "Type": "elbv2"},
        ],
    )

    # Describe
    resp = client.describe_traffic_sources(AutoScalingGroupName="test-asg")
    sources = resp["TrafficSources"]
    assert len(sources) == 1
    assert sources[0]["Identifier"] == "arn:aws:elasticloadbalancing:us-east-1:123456789012:targetgroup/my-tg/abc123"
    assert sources[0]["State"] == "InService"

    # Attach another
    client.attach_traffic_sources(
        AutoScalingGroupName="test-asg",
        TrafficSources=[
            {"Identifier": "arn:aws:vpc-lattice:us-east-1:123456789012:targetgroup/tg-abc", "Type": "vpc-lattice"},
        ],
    )
    resp = client.describe_traffic_sources(AutoScalingGroupName="test-asg")
    assert len(resp["TrafficSources"]) == 2

    # Detach first
    client.detach_traffic_sources(
        AutoScalingGroupName="test-asg",
        TrafficSources=[
            {"Identifier": "arn:aws:elasticloadbalancing:us-east-1:123456789012:targetgroup/my-tg/abc123"},
        ],
    )
    resp = client.describe_traffic_sources(AutoScalingGroupName="test-asg")
    assert len(resp["TrafficSources"]) == 1
    assert resp["TrafficSources"][0]["Identifier"].startswith("arn:aws:vpc-lattice")


@mock_aws
def test_attach_traffic_sources_idempotent():
    client = boto3.client("autoscaling", region_name="us-east-1")
    _create_asg_with_lc(client)

    ts = {"Identifier": "arn:aws:elasticloadbalancing:us-east-1:123456789012:targetgroup/my-tg/abc123", "Type": "elbv2"}

    client.attach_traffic_sources(
        AutoScalingGroupName="test-asg", TrafficSources=[ts]
    )
    client.attach_traffic_sources(
        AutoScalingGroupName="test-asg", TrafficSources=[ts]
    )

    resp = client.describe_traffic_sources(AutoScalingGroupName="test-asg")
    assert len(resp["TrafficSources"]) == 1


# --- GetPredictiveScalingForecast ---


@mock_aws
def test_get_predictive_scaling_forecast():
    client = boto3.client("autoscaling", region_name="us-east-1")
    _create_asg_with_lc(client)

    # Create a predictive scaling policy
    client.put_scaling_policy(
        AutoScalingGroupName="test-asg",
        PolicyName="pred-policy",
        PolicyType="PredictiveScaling",
        PredictiveScalingConfiguration={
            "MetricSpecifications": [
                {
                    "TargetValue": 50.0,
                    "PredefinedMetricPairSpecification": {
                        "PredefinedMetricType": "ASGCPUUtilization",
                    },
                }
            ],
            "Mode": "ForecastOnly",
        },
    )

    resp = client.get_predictive_scaling_forecast(
        AutoScalingGroupName="test-asg",
        PolicyName="pred-policy",
        StartTime="2025-01-01T00:00:00Z",
        EndTime="2025-01-02T00:00:00Z",
    )
    assert "LoadForecast" in resp
    assert "CapacityForecast" in resp
    assert resp["LoadForecast"] == []
    assert resp["CapacityForecast"]["Timestamps"] == []
    assert resp["CapacityForecast"]["Values"] == []
    assert "UpdateTime" in resp
