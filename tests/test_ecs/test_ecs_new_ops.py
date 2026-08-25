import json

import boto3
import pytest
from botocore.exceptions import ClientError

from moto import mock_aws
from moto.core import DEFAULT_ACCOUNT_ID as ACCOUNT_ID
from moto.ec2 import utils as ec2_utils
from tests import EXAMPLE_AMI_ID


def _create_cluster_with_task(client, cluster_name="test-cluster"):
    """Helper to create a cluster, register a task def, and run a task."""
    client.create_cluster(clusterName=cluster_name)
    client.register_task_definition(
        family="test_task",
        containerDefinitions=[
            {
                "name": "hello_world",
                "image": "docker/hello-world:latest",
                "cpu": 256,
                "memory": 512,
            }
        ],
    )
    resp = client.run_task(
        cluster=cluster_name,
        taskDefinition="test_task",
        launchType="FARGATE",
        count=1,
        networkConfiguration={
            "awsvpcConfiguration": {
                "subnets": [],
                "securityGroups": [],
            }
        },
    )
    return resp["tasks"][0]


# --- PutAccountSettingDefault ---


@mock_aws
def test_put_account_setting_default():
    client = boto3.client("ecs", region_name="us-east-1")

    resp = client.put_account_setting_default(
        name="serviceLongArnFormat", value="enabled"
    )
    assert resp["setting"]["name"] == "serviceLongArnFormat"
    assert resp["setting"]["value"] == "enabled"


@mock_aws
def test_put_account_setting_default_invalid_name():
    client = boto3.client("ecs", region_name="us-east-1")

    with pytest.raises(ClientError) as exc:
        client.put_account_setting_default(name="invalid", value="enabled")
    err = exc.value.response["Error"]
    assert err["Code"] == "InvalidParameterException"


@mock_aws
def test_put_account_setting_default_all_valid_names():
    client = boto3.client("ecs", region_name="us-east-1")

    valid_names = [
        "serviceLongArnFormat",
        "taskLongArnFormat",
        "containerInstanceLongArnFormat",
        "containerLongArnFormat",
        "awsvpcTrunking",
        "containerInsights",
        "dualStackIPv6",
    ]
    for name in valid_names:
        resp = client.put_account_setting_default(name=name, value="enabled")
        assert resp["setting"]["name"] == name
        assert resp["setting"]["value"] == "enabled"


# --- GetTaskProtection / UpdateTaskProtection ---


@mock_aws
def test_get_task_protection_no_tasks():
    client = boto3.client("ecs", region_name="us-east-1")
    client.create_cluster(clusterName="test-cluster")

    resp = client.get_task_protection(cluster="test-cluster")
    assert resp["protectedTasks"] == []
    assert resp["failures"] == []


@mock_aws
def test_get_task_protection_with_tasks():
    client = boto3.client("ecs", region_name="us-east-1")
    task = _create_cluster_with_task(client)
    task_arn = task["taskArn"]

    resp = client.get_task_protection(cluster="test-cluster", tasks=[task_arn])
    assert len(resp["protectedTasks"]) == 1
    assert resp["protectedTasks"][0]["taskArn"] == task_arn
    assert resp["protectedTasks"][0]["protectionEnabled"] is False


@mock_aws
def test_get_task_protection_missing_task():
    client = boto3.client("ecs", region_name="us-east-1")
    client.create_cluster(clusterName="test-cluster")

    resp = client.get_task_protection(
        cluster="test-cluster", tasks=["nonexistent-task"]
    )
    assert len(resp["failures"]) == 1
    assert resp["failures"][0]["reason"] == "TASK_NOT_FOUND"


@mock_aws
def test_update_task_protection():
    client = boto3.client("ecs", region_name="us-east-1")
    task = _create_cluster_with_task(client)
    task_arn = task["taskArn"]

    resp = client.update_task_protection(
        cluster="test-cluster",
        tasks=[task_arn],
        protectionEnabled=True,
        expiresInMinutes=60,
    )
    assert len(resp["protectedTasks"]) == 1
    assert resp["protectedTasks"][0]["protectionEnabled"] is True
    assert "expirationDate" in resp["protectedTasks"][0]

    # Verify via get
    resp = client.get_task_protection(cluster="test-cluster", tasks=[task_arn])
    assert resp["protectedTasks"][0]["protectionEnabled"] is True


@mock_aws
def test_update_task_protection_disable():
    client = boto3.client("ecs", region_name="us-east-1")
    task = _create_cluster_with_task(client)
    task_arn = task["taskArn"]

    # Enable first
    client.update_task_protection(
        cluster="test-cluster",
        tasks=[task_arn],
        protectionEnabled=True,
        expiresInMinutes=60,
    )

    # Disable
    resp = client.update_task_protection(
        cluster="test-cluster",
        tasks=[task_arn],
        protectionEnabled=False,
    )
    assert resp["protectedTasks"][0]["protectionEnabled"] is False
    assert "expirationDate" not in resp["protectedTasks"][0]


@mock_aws
def test_update_task_protection_missing_task():
    client = boto3.client("ecs", region_name="us-east-1")
    client.create_cluster(clusterName="test-cluster")

    resp = client.update_task_protection(
        cluster="test-cluster",
        tasks=["nonexistent-task"],
        protectionEnabled=True,
    )
    assert len(resp["failures"]) == 1
    assert resp["failures"][0]["reason"] == "TASK_NOT_FOUND"


# --- ExecuteCommand ---


@mock_aws
def test_execute_command():
    client = boto3.client("ecs", region_name="us-east-1")
    task = _create_cluster_with_task(client)
    task_arn = task["taskArn"]

    resp = client.execute_command(
        cluster="test-cluster",
        task=task_arn,
        command="/bin/bash",
        interactive=True,
    )
    assert resp["clusterArn"].endswith("cluster/test-cluster")
    assert resp["taskArn"] == task_arn
    assert resp["interactive"] is True
    assert "session" in resp
    assert "sessionId" in resp["session"]
    assert "streamUrl" in resp["session"]
    assert "tokenValue" in resp["session"]


@mock_aws
def test_execute_command_task_not_found():
    client = boto3.client("ecs", region_name="us-east-1")
    client.create_cluster(clusterName="test-cluster")

    with pytest.raises(ClientError) as exc:
        client.execute_command(
            cluster="test-cluster",
            task="nonexistent-task",
            command="/bin/bash",
            interactive=True,
        )
    err = exc.value.response["Error"]
    assert err["Code"] == "InvalidParameterException"


# --- ListServicesByNamespace ---


@mock_aws
def test_list_services_by_namespace_empty():
    client = boto3.client("ecs", region_name="us-east-1")

    resp = client.list_services_by_namespace(namespace="test-namespace")
    assert resp["serviceArns"] == []


# --- UpdateClusterSettings ---


@mock_aws
def test_update_cluster_settings():
    client = boto3.client("ecs", region_name="us-east-1")
    client.create_cluster(clusterName="test-cluster")

    resp = client.update_cluster_settings(
        cluster="test-cluster",
        settings=[{"name": "containerInsights", "value": "enabled"}],
    )
    cluster = resp["cluster"]
    assert cluster["settings"] == [
        {"name": "containerInsights", "value": "enabled"}
    ]


@mock_aws
def test_update_cluster_settings_verify_persistence():
    client = boto3.client("ecs", region_name="us-east-1")
    client.create_cluster(clusterName="test-cluster")

    client.update_cluster_settings(
        cluster="test-cluster",
        settings=[{"name": "containerInsights", "value": "enabled"}],
    )

    # Verify with describe
    resp = client.describe_clusters(clusters=["test-cluster"])
    cluster = resp["clusters"][0]
    assert cluster["settings"] == [
        {"name": "containerInsights", "value": "enabled"}
    ]


# --- SubmitContainerStateChange / SubmitTaskStateChange ---


@mock_aws
def test_submit_container_state_change():
    client = boto3.client("ecs", region_name="us-east-1")

    resp = client.submit_container_state_change(
        cluster="default",
        task="some-task-id",
        containerName="my-container",
        status="RUNNING",
    )
    assert resp["acknowledgment"] == "ACCEPT"


@mock_aws
def test_submit_task_state_change():
    client = boto3.client("ecs", region_name="us-east-1")

    resp = client.submit_task_state_change(
        cluster="default",
        task="some-task-id",
        status="RUNNING",
    )
    assert resp["acknowledgment"] == "ACCEPT"
