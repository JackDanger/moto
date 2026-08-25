import boto3
import pytest
from botocore.exceptions import ClientError

from moto import mock_aws
from tests import DEFAULT_ACCOUNT_ID


@mock_aws
def test_provision_permission_set():
    ssoadmin = boto3.client("sso-admin", "us-east-1")

    instance_arn = ssoadmin.list_instances()["Instances"][0]["InstanceArn"]

    p_set_arn = ssoadmin.create_permission_set(InstanceArn=instance_arn, Name="pset1")[
        "PermissionSet"
    ]["PermissionSetArn"]

    status = ssoadmin.provision_permission_set(
        InstanceArn=instance_arn,
        PermissionSetArn=p_set_arn,
        TargetType="AWS_ACCOUNT",
    )["PermissionSetProvisioningStatus"]

    assert status["AccountId"] == DEFAULT_ACCOUNT_ID
    assert status["CreatedDate"]
    assert status["PermissionSetArn"] == p_set_arn
    assert status["Status"] == "SUCCEEDED"


@mock_aws
def test_list_permission_sets_provisioned_to_account():
    ssoadmin = boto3.client("sso-admin", "us-east-1")

    instance_arn = ssoadmin.list_instances()["Instances"][0]["InstanceArn"]

    p_set_arn = ssoadmin.create_permission_set(InstanceArn=instance_arn, Name="pset1")[
        "PermissionSet"
    ]["PermissionSetArn"]

    provisioned = ssoadmin.list_permission_sets_provisioned_to_account(
        AccountId=DEFAULT_ACCOUNT_ID, InstanceArn=instance_arn
    )["PermissionSets"]
    assert len(provisioned) == 0

    accounts = ssoadmin.list_accounts_for_provisioned_permission_set(
        InstanceArn=instance_arn, PermissionSetArn=p_set_arn
    )["AccountIds"]
    assert accounts == []

    ssoadmin.provision_permission_set(
        InstanceArn=instance_arn,
        PermissionSetArn=p_set_arn,
        TargetType="AWS_ACCOUNT",
    )

    provisioned = ssoadmin.list_permission_sets_provisioned_to_account(
        AccountId=DEFAULT_ACCOUNT_ID, InstanceArn=instance_arn
    )["PermissionSets"]
    assert provisioned == [p_set_arn]

    accounts = ssoadmin.list_accounts_for_provisioned_permission_set(
        InstanceArn=instance_arn, PermissionSetArn=p_set_arn
    )["AccountIds"]
    assert accounts == [DEFAULT_ACCOUNT_ID]


@mock_aws
def test_permission_set_tagging_lifecycle():
    ssoadmin = boto3.client("sso-admin", "us-east-1")

    instance_arn = ssoadmin.list_instances()["Instances"][0]["InstanceArn"]
    p_set_arn = ssoadmin.create_permission_set(InstanceArn=instance_arn, Name="pset1")[
        "PermissionSet"
    ]["PermissionSetArn"]

    tags = ssoadmin.list_tags_for_resource(InstanceArn=instance_arn, ResourceArn=p_set_arn)["Tags"]
    assert tags == []

    ssoadmin.tag_resource(
        InstanceArn=instance_arn,
        ResourceArn=p_set_arn,
        Tags=[{"Key": "env", "Value": "test"}, {"Key": "owner", "Value": "jack"}],
    )
    tags = ssoadmin.list_tags_for_resource(InstanceArn=instance_arn, ResourceArn=p_set_arn)["Tags"]
    assert sorted(tags, key=lambda t: t["Key"]) == [
        {"Key": "env", "Value": "test"},
        {"Key": "owner", "Value": "jack"},
    ]

    # Re-tagging an existing key overwrites its value rather than duplicating it.
    ssoadmin.tag_resource(
        InstanceArn=instance_arn,
        ResourceArn=p_set_arn,
        Tags=[{"Key": "env", "Value": "prod"}],
    )
    tags = ssoadmin.list_tags_for_resource(InstanceArn=instance_arn, ResourceArn=p_set_arn)["Tags"]
    assert sorted(tags, key=lambda t: t["Key"]) == [
        {"Key": "env", "Value": "prod"},
        {"Key": "owner", "Value": "jack"},
    ]

    ssoadmin.untag_resource(InstanceArn=instance_arn, ResourceArn=p_set_arn, TagKeys=["owner"])
    tags = ssoadmin.list_tags_for_resource(InstanceArn=instance_arn, ResourceArn=p_set_arn)["Tags"]
    assert tags == [{"Key": "env", "Value": "prod"}]


@mock_aws
def test_application_tagging_lifecycle():
    ssoadmin = boto3.client("sso-admin", "us-east-1")
    instance_arn = ssoadmin.list_instances()["Instances"][0]["InstanceArn"]
    app_arn = ssoadmin.create_application(
        ApplicationProviderArn="arn:aws:sso::aws:applicationProvider/custom",
        InstanceArn=instance_arn,
        Name="testapp",
    )["ApplicationArn"]

    ssoadmin.tag_resource(
        InstanceArn=instance_arn, ResourceArn=app_arn, Tags=[{"Key": "k", "Value": "v"}]
    )
    tags = ssoadmin.list_tags_for_resource(InstanceArn=instance_arn, ResourceArn=app_arn)["Tags"]
    assert tags == [{"Key": "k", "Value": "v"}]


@mock_aws
def test_tag_operations_on_nonexistent_resource_raise():
    ssoadmin = boto3.client("sso-admin", "us-east-1")
    instance_arn = ssoadmin.list_instances()["Instances"][0]["InstanceArn"]
    bogus_arn = f"{instance_arn}/ps-doesnotexist0000000"

    with pytest.raises(ClientError) as exc:
        ssoadmin.list_tags_for_resource(InstanceArn=instance_arn, ResourceArn=bogus_arn)
    assert exc.value.response["Error"]["Code"] == "ResourceNotFoundException"

    with pytest.raises(ClientError) as exc:
        ssoadmin.tag_resource(
            InstanceArn=instance_arn, ResourceArn=bogus_arn, Tags=[{"Key": "k", "Value": "v"}]
        )
    assert exc.value.response["Error"]["Code"] == "ResourceNotFoundException"

    with pytest.raises(ClientError) as exc:
        ssoadmin.untag_resource(InstanceArn=instance_arn, ResourceArn=bogus_arn, TagKeys=["k"])
    assert exc.value.response["Error"]["Code"] == "ResourceNotFoundException"
