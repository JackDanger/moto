import boto3
import pytest
from moto import mock_aws


@mock_aws
def test_list_tags_for_detector():
    client = boto3.client("guardduty", region_name="us-east-1")
    detector_id = client.create_detector(
        Enable=True, Tags={"env": "test", "team": "security"}
    )["DetectorId"]

    detector = client.get_detector(DetectorId=detector_id)
    detector_arn = detector["Tags"]  # tags stored on detector

    # Get the ARN from the detector resource
    account_id = "123456789012"
    arn = f"arn:aws:guardduty:us-east-1:{account_id}:detector/{detector_id}"

    resp = client.list_tags_for_resource(ResourceArn=arn)
    assert resp["Tags"]["env"] == "test"
    assert resp["Tags"]["team"] == "security"


@mock_aws
def test_tag_untag_detector():
    client = boto3.client("guardduty", region_name="us-east-1")
    detector_id = client.create_detector(
        Enable=True, Tags={"env": "test"}
    )["DetectorId"]

    account_id = "123456789012"
    arn = f"arn:aws:guardduty:us-east-1:{account_id}:detector/{detector_id}"

    # Add tags
    client.tag_resource(ResourceArn=arn, Tags={"team": "security", "cost": "low"})
    resp = client.list_tags_for_resource(ResourceArn=arn)
    assert resp["Tags"]["env"] == "test"
    assert resp["Tags"]["team"] == "security"
    assert resp["Tags"]["cost"] == "low"

    # Remove tags
    client.untag_resource(ResourceArn=arn, TagKeys=["cost"])
    resp = client.list_tags_for_resource(ResourceArn=arn)
    assert "cost" not in resp["Tags"]
    assert resp["Tags"]["env"] == "test"
    assert resp["Tags"]["team"] == "security"


@mock_aws
def test_tag_nonexistent_resource():
    client = boto3.client("guardduty", region_name="us-east-1")
    arn = "arn:aws:guardduty:us-east-1:123456789012:detector/nonexistent"

    with pytest.raises(client.exceptions.BadRequestException):
        client.tag_resource(ResourceArn=arn, Tags={"key": "value"})


@mock_aws
def test_list_filters():
    client = boto3.client("guardduty", region_name="us-east-1")
    detector_id = client.create_detector(Enable=True)["DetectorId"]

    client.create_filter(
        DetectorId=detector_id,
        Name="filter-1",
        FindingCriteria={"Criterion": {"severity": {"Eq": ["HIGH"]}}},
    )
    client.create_filter(
        DetectorId=detector_id,
        Name="filter-2",
        FindingCriteria={"Criterion": {"severity": {"Eq": ["LOW"]}}},
    )

    resp = client.list_filters(DetectorId=detector_id)
    assert sorted(resp["FilterNames"]) == ["filter-1", "filter-2"]


@mock_aws
def test_tag_ip_set():
    client = boto3.client("guardduty", region_name="us-east-1")
    detector_id = client.create_detector(Enable=True)["DetectorId"]

    ip_set_id = client.create_ip_set(
        DetectorId=detector_id,
        Name="test-ipset",
        Format="TXT",
        Location="s3://mybucket/ipset.txt",
        Activate=True,
        Tags={"initial": "tag"},
    )["IpSetId"]

    account_id = "123456789012"
    arn = (
        f"arn:aws:guardduty:us-east-1:{account_id}"
        f":detector/{detector_id}/ipset/{ip_set_id}"
    )

    client.tag_resource(ResourceArn=arn, Tags={"added": "tag2"})
    resp = client.list_tags_for_resource(ResourceArn=arn)
    assert resp["Tags"]["initial"] == "tag"
    assert resp["Tags"]["added"] == "tag2"
