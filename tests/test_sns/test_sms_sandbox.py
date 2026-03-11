import boto3
import pytest
from botocore.exceptions import ClientError

from moto import mock_aws


@mock_aws
def test_create_and_list_sms_sandbox_phone_number():
    client = boto3.client("sns", region_name="us-east-1")

    # Initially empty
    resp = client.list_sms_sandbox_phone_numbers()
    assert resp["PhoneNumbers"] == []

    # Add a phone number
    client.create_sms_sandbox_phone_number(PhoneNumber="+12065551234")

    resp = client.list_sms_sandbox_phone_numbers()
    assert len(resp["PhoneNumbers"]) == 1
    assert resp["PhoneNumbers"][0]["PhoneNumber"] == "+12065551234"
    assert resp["PhoneNumbers"][0]["Status"] == "Pending"


@mock_aws
def test_create_sms_sandbox_phone_number_with_language():
    client = boto3.client("sns", region_name="us-east-1")
    client.create_sms_sandbox_phone_number(
        PhoneNumber="+12065551234", LanguageCode="ja-JP"
    )

    resp = client.list_sms_sandbox_phone_numbers()
    assert len(resp["PhoneNumbers"]) == 1
    assert resp["PhoneNumbers"][0]["Status"] == "Pending"


@mock_aws
def test_verify_sms_sandbox_phone_number():
    client = boto3.client("sns", region_name="us-east-1")

    client.create_sms_sandbox_phone_number(PhoneNumber="+12065551234")
    client.verify_sms_sandbox_phone_number(
        PhoneNumber="+12065551234", OneTimePassword="123456"
    )

    resp = client.list_sms_sandbox_phone_numbers()
    assert resp["PhoneNumbers"][0]["Status"] == "Verified"


@mock_aws
def test_verify_sms_sandbox_phone_number_not_found():
    client = boto3.client("sns", region_name="us-east-1")

    with pytest.raises(ClientError) as exc:
        client.verify_sms_sandbox_phone_number(
            PhoneNumber="+12065559999", OneTimePassword="123456"
        )
    assert exc.value.response["Error"]["Code"] == "ResourceNotFound"


@mock_aws
def test_delete_sms_sandbox_phone_number():
    client = boto3.client("sns", region_name="us-east-1")

    client.create_sms_sandbox_phone_number(PhoneNumber="+12065551234")
    client.delete_sms_sandbox_phone_number(PhoneNumber="+12065551234")

    resp = client.list_sms_sandbox_phone_numbers()
    assert resp["PhoneNumbers"] == []


@mock_aws
def test_delete_sms_sandbox_phone_number_not_found():
    client = boto3.client("sns", region_name="us-east-1")

    with pytest.raises(ClientError) as exc:
        client.delete_sms_sandbox_phone_number(PhoneNumber="+12065559999")
    assert exc.value.response["Error"]["Code"] == "ResourceNotFound"


@mock_aws
def test_multiple_sandbox_phone_numbers():
    client = boto3.client("sns", region_name="us-east-1")

    client.create_sms_sandbox_phone_number(PhoneNumber="+12065551111")
    client.create_sms_sandbox_phone_number(PhoneNumber="+12065552222")
    client.create_sms_sandbox_phone_number(PhoneNumber="+12065553333")

    resp = client.list_sms_sandbox_phone_numbers()
    assert len(resp["PhoneNumbers"]) == 3

    # Verify one, delete another
    client.verify_sms_sandbox_phone_number(
        PhoneNumber="+12065551111", OneTimePassword="123456"
    )
    client.delete_sms_sandbox_phone_number(PhoneNumber="+12065553333")

    resp = client.list_sms_sandbox_phone_numbers()
    assert len(resp["PhoneNumbers"]) == 2
    numbers = {p["PhoneNumber"]: p["Status"] for p in resp["PhoneNumbers"]}
    assert numbers["+12065551111"] == "Verified"
    assert numbers["+12065552222"] == "Pending"
