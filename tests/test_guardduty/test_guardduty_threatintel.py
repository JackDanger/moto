import boto3
import pytest
from moto import mock_aws


@mock_aws
def test_create_threat_intel_set():
    client = boto3.client("guardduty", region_name="us-east-1")
    detector_id = client.create_detector(Enable=True)["DetectorId"]

    resp = client.create_threat_intel_set(
        DetectorId=detector_id,
        Name="test-tis",
        Format="TXT",
        Location="s3://mybucket/tis.txt",
        Activate=True,
    )
    assert "ThreatIntelSetId" in resp
    assert len(resp["ThreatIntelSetId"]) == 32


@mock_aws
def test_get_threat_intel_set():
    client = boto3.client("guardduty", region_name="us-east-1")
    detector_id = client.create_detector(Enable=True)["DetectorId"]

    tis_id = client.create_threat_intel_set(
        DetectorId=detector_id,
        Name="test-tis",
        Format="TXT",
        Location="s3://mybucket/tis.txt",
        Activate=True,
    )["ThreatIntelSetId"]

    resp = client.get_threat_intel_set(
        DetectorId=detector_id, ThreatIntelSetId=tis_id
    )
    assert resp["Name"] == "test-tis"
    assert resp["Format"] == "TXT"
    assert resp["Location"] == "s3://mybucket/tis.txt"
    assert resp["Status"] == "ACTIVE"


@mock_aws
def test_get_threat_intel_set_inactive():
    client = boto3.client("guardduty", region_name="us-east-1")
    detector_id = client.create_detector(Enable=True)["DetectorId"]

    tis_id = client.create_threat_intel_set(
        DetectorId=detector_id,
        Name="test-tis",
        Format="TXT",
        Location="s3://mybucket/tis.txt",
        Activate=False,
    )["ThreatIntelSetId"]

    resp = client.get_threat_intel_set(
        DetectorId=detector_id, ThreatIntelSetId=tis_id
    )
    assert resp["Status"] == "INACTIVE"


@mock_aws
def test_update_threat_intel_set():
    client = boto3.client("guardduty", region_name="us-east-1")
    detector_id = client.create_detector(Enable=True)["DetectorId"]

    tis_id = client.create_threat_intel_set(
        DetectorId=detector_id,
        Name="test-tis",
        Format="TXT",
        Location="s3://mybucket/tis.txt",
        Activate=True,
    )["ThreatIntelSetId"]

    client.update_threat_intel_set(
        DetectorId=detector_id,
        ThreatIntelSetId=tis_id,
        Name="updated-tis",
        Location="s3://mybucket/tis2.txt",
        Activate=False,
    )

    resp = client.get_threat_intel_set(
        DetectorId=detector_id, ThreatIntelSetId=tis_id
    )
    assert resp["Name"] == "updated-tis"
    assert resp["Location"] == "s3://mybucket/tis2.txt"
    assert resp["Status"] == "INACTIVE"


@mock_aws
def test_delete_threat_intel_set():
    client = boto3.client("guardduty", region_name="us-east-1")
    detector_id = client.create_detector(Enable=True)["DetectorId"]

    tis_id = client.create_threat_intel_set(
        DetectorId=detector_id,
        Name="test-tis",
        Format="TXT",
        Location="s3://mybucket/tis.txt",
        Activate=True,
    )["ThreatIntelSetId"]

    client.delete_threat_intel_set(
        DetectorId=detector_id, ThreatIntelSetId=tis_id
    )

    with pytest.raises(client.exceptions.BadRequestException):
        client.get_threat_intel_set(
            DetectorId=detector_id, ThreatIntelSetId=tis_id
        )


@mock_aws
def test_list_threat_intel_sets():
    client = boto3.client("guardduty", region_name="us-east-1")
    detector_id = client.create_detector(Enable=True)["DetectorId"]

    tis_id1 = client.create_threat_intel_set(
        DetectorId=detector_id,
        Name="tis-1",
        Format="TXT",
        Location="s3://mybucket/tis1.txt",
        Activate=True,
    )["ThreatIntelSetId"]

    tis_id2 = client.create_threat_intel_set(
        DetectorId=detector_id,
        Name="tis-2",
        Format="STIX",
        Location="s3://mybucket/tis2.txt",
        Activate=False,
    )["ThreatIntelSetId"]

    resp = client.list_threat_intel_sets(DetectorId=detector_id)
    assert sorted(resp["ThreatIntelSetIds"]) == sorted([tis_id1, tis_id2])


@mock_aws
def test_get_threat_intel_set_not_found():
    client = boto3.client("guardduty", region_name="us-east-1")
    detector_id = client.create_detector(Enable=True)["DetectorId"]

    with pytest.raises(client.exceptions.BadRequestException):
        client.get_threat_intel_set(
            DetectorId=detector_id, ThreatIntelSetId="nonexistent"
        )
