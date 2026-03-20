import boto3
import pytest
from moto import mock_aws


@mock_aws
def test_create_ip_set():
    client = boto3.client("guardduty", region_name="us-east-1")
    detector_id = client.create_detector(Enable=True)["DetectorId"]

    resp = client.create_ip_set(
        DetectorId=detector_id,
        Name="test-ipset",
        Format="TXT",
        Location="s3://mybucket/ipset.txt",
        Activate=True,
    )
    assert "IpSetId" in resp
    assert len(resp["IpSetId"]) == 32


@mock_aws
def test_get_ip_set():
    client = boto3.client("guardduty", region_name="us-east-1")
    detector_id = client.create_detector(Enable=True)["DetectorId"]

    ip_set_id = client.create_ip_set(
        DetectorId=detector_id,
        Name="test-ipset",
        Format="TXT",
        Location="s3://mybucket/ipset.txt",
        Activate=True,
    )["IpSetId"]

    resp = client.get_ip_set(DetectorId=detector_id, IpSetId=ip_set_id)
    assert resp["Name"] == "test-ipset"
    assert resp["Format"] == "TXT"
    assert resp["Location"] == "s3://mybucket/ipset.txt"
    assert resp["Status"] == "ACTIVE"


@mock_aws
def test_get_ip_set_inactive():
    client = boto3.client("guardduty", region_name="us-east-1")
    detector_id = client.create_detector(Enable=True)["DetectorId"]

    ip_set_id = client.create_ip_set(
        DetectorId=detector_id,
        Name="test-ipset",
        Format="TXT",
        Location="s3://mybucket/ipset.txt",
        Activate=False,
    )["IpSetId"]

    resp = client.get_ip_set(DetectorId=detector_id, IpSetId=ip_set_id)
    assert resp["Status"] == "INACTIVE"


@mock_aws
def test_update_ip_set():
    client = boto3.client("guardduty", region_name="us-east-1")
    detector_id = client.create_detector(Enable=True)["DetectorId"]

    ip_set_id = client.create_ip_set(
        DetectorId=detector_id,
        Name="test-ipset",
        Format="TXT",
        Location="s3://mybucket/ipset.txt",
        Activate=True,
    )["IpSetId"]

    client.update_ip_set(
        DetectorId=detector_id,
        IpSetId=ip_set_id,
        Name="updated-ipset",
        Location="s3://mybucket/ipset2.txt",
        Activate=False,
    )

    resp = client.get_ip_set(DetectorId=detector_id, IpSetId=ip_set_id)
    assert resp["Name"] == "updated-ipset"
    assert resp["Location"] == "s3://mybucket/ipset2.txt"
    assert resp["Status"] == "INACTIVE"


@mock_aws
def test_delete_ip_set():
    client = boto3.client("guardduty", region_name="us-east-1")
    detector_id = client.create_detector(Enable=True)["DetectorId"]

    ip_set_id = client.create_ip_set(
        DetectorId=detector_id,
        Name="test-ipset",
        Format="TXT",
        Location="s3://mybucket/ipset.txt",
        Activate=True,
    )["IpSetId"]

    client.delete_ip_set(DetectorId=detector_id, IpSetId=ip_set_id)

    with pytest.raises(client.exceptions.BadRequestException):
        client.get_ip_set(DetectorId=detector_id, IpSetId=ip_set_id)


@mock_aws
def test_list_ip_sets():
    client = boto3.client("guardduty", region_name="us-east-1")
    detector_id = client.create_detector(Enable=True)["DetectorId"]

    ip_set_id1 = client.create_ip_set(
        DetectorId=detector_id,
        Name="ipset-1",
        Format="TXT",
        Location="s3://mybucket/ipset1.txt",
        Activate=True,
    )["IpSetId"]

    ip_set_id2 = client.create_ip_set(
        DetectorId=detector_id,
        Name="ipset-2",
        Format="STIX",
        Location="s3://mybucket/ipset2.txt",
        Activate=False,
    )["IpSetId"]

    resp = client.list_ip_sets(DetectorId=detector_id)
    assert sorted(resp["IpSetIds"]) == sorted([ip_set_id1, ip_set_id2])


@mock_aws
def test_get_ip_set_not_found():
    client = boto3.client("guardduty", region_name="us-east-1")
    detector_id = client.create_detector(Enable=True)["DetectorId"]

    with pytest.raises(client.exceptions.BadRequestException):
        client.get_ip_set(DetectorId=detector_id, IpSetId="nonexistent")
