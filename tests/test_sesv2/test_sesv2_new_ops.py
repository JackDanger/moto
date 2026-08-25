"""Tests for new SESv2 operations."""

import boto3
import pytest
from botocore.exceptions import ClientError

from moto import mock_aws


@mock_aws
def test_create_email_template():
    client = boto3.client("sesv2", region_name="us-east-1")
    client.create_email_template(TemplateName="my-template", TemplateContent={"Subject": "Hello {{name}}", "Text": "Dear {{name}}", "Html": "<h1>Hello</h1>"})
    result = client.get_email_template(TemplateName="my-template")
    assert result["TemplateName"] == "my-template"
    assert result["TemplateContent"]["Subject"] == "Hello {{name}}"


@mock_aws
def test_create_email_template_duplicate():
    client = boto3.client("sesv2", region_name="us-east-1")
    client.create_email_template(TemplateName="my-template", TemplateContent={"Subject": "Hello"})
    with pytest.raises(ClientError) as e:
        client.create_email_template(TemplateName="my-template", TemplateContent={"Subject": "Hello"})
    assert e.value.response["Error"]["Code"] == "AlreadyExistsException"


@mock_aws
def test_get_email_template_not_found():
    client = boto3.client("sesv2", region_name="us-east-1")
    with pytest.raises(ClientError) as e:
        client.get_email_template(TemplateName="nonexistent")
    assert e.value.response["Error"]["Code"] == "NotFoundException"


@mock_aws
def test_update_email_template():
    client = boto3.client("sesv2", region_name="us-east-1")
    client.create_email_template(TemplateName="my-template", TemplateContent={"Subject": "Old"})
    client.update_email_template(TemplateName="my-template", TemplateContent={"Subject": "New"})
    result = client.get_email_template(TemplateName="my-template")
    assert result["TemplateContent"]["Subject"] == "New"


@mock_aws
def test_update_email_template_not_found():
    client = boto3.client("sesv2", region_name="us-east-1")
    with pytest.raises(ClientError) as e:
        client.update_email_template(TemplateName="nonexistent", TemplateContent={"Subject": "x"})
    assert e.value.response["Error"]["Code"] == "NotFoundException"


@mock_aws
def test_delete_email_template():
    client = boto3.client("sesv2", region_name="us-east-1")
    client.create_email_template(TemplateName="my-template", TemplateContent={"Subject": "test"})
    client.delete_email_template(TemplateName="my-template")
    with pytest.raises(ClientError) as e:
        client.get_email_template(TemplateName="my-template")
    assert e.value.response["Error"]["Code"] == "NotFoundException"


@mock_aws
def test_list_email_templates():
    client = boto3.client("sesv2", region_name="us-east-1")
    assert client.list_email_templates()["TemplatesMetadata"] == []
    for i in range(3):
        client.create_email_template(TemplateName=f"t-{i}", TemplateContent={"Subject": f"S{i}"})
    result = client.list_email_templates()
    assert len(result["TemplatesMetadata"]) == 3
    for t in result["TemplatesMetadata"]:
        assert "CreatedTimestamp" in t


@mock_aws
def test_create_configuration_set_event_destination():
    client = boto3.client("sesv2", region_name="us-east-1")
    client.create_configuration_set(ConfigurationSetName="my-cs")
    client.create_configuration_set_event_destination(
        ConfigurationSetName="my-cs", EventDestinationName="my-dest",
        EventDestination={"Enabled": True, "MatchingEventTypes": ["SEND", "BOUNCE"],
                          "SnsDestination": {"TopicArn": "arn:aws:sns:us-east-1:123456789012:t"}})
    result = client.get_configuration_set_event_destinations(ConfigurationSetName="my-cs")
    assert len(result["EventDestinations"]) == 1
    assert result["EventDestinations"][0]["Name"] == "my-dest"
    assert result["EventDestinations"][0]["Enabled"] is True


@mock_aws
def test_create_event_destination_duplicate():
    client = boto3.client("sesv2", region_name="us-east-1")
    client.create_configuration_set(ConfigurationSetName="my-cs")
    kw = {"ConfigurationSetName": "my-cs", "EventDestinationName": "d", "EventDestination": {"Enabled": True, "MatchingEventTypes": ["SEND"]}}
    client.create_configuration_set_event_destination(**kw)
    with pytest.raises(ClientError) as e:
        client.create_configuration_set_event_destination(**kw)
    assert e.value.response["Error"]["Code"] == "AlreadyExistsException"


@mock_aws
def test_update_configuration_set_event_destination():
    client = boto3.client("sesv2", region_name="us-east-1")
    client.create_configuration_set(ConfigurationSetName="my-cs")
    client.create_configuration_set_event_destination(
        ConfigurationSetName="my-cs", EventDestinationName="d",
        EventDestination={"Enabled": True, "MatchingEventTypes": ["SEND"]})
    client.update_configuration_set_event_destination(
        ConfigurationSetName="my-cs", EventDestinationName="d",
        EventDestination={"Enabled": False, "MatchingEventTypes": ["BOUNCE"]})
    result = client.get_configuration_set_event_destinations(ConfigurationSetName="my-cs")
    assert result["EventDestinations"][0]["Enabled"] is False
    assert result["EventDestinations"][0]["MatchingEventTypes"] == ["BOUNCE"]


@mock_aws
def test_delete_configuration_set_event_destination():
    client = boto3.client("sesv2", region_name="us-east-1")
    client.create_configuration_set(ConfigurationSetName="my-cs")
    client.create_configuration_set_event_destination(
        ConfigurationSetName="my-cs", EventDestinationName="d",
        EventDestination={"Enabled": True, "MatchingEventTypes": ["SEND"]})
    client.delete_configuration_set_event_destination(ConfigurationSetName="my-cs", EventDestinationName="d")
    result = client.get_configuration_set_event_destinations(ConfigurationSetName="my-cs")
    assert len(result["EventDestinations"]) == 0


@mock_aws
def test_delete_event_destination_not_found():
    client = boto3.client("sesv2", region_name="us-east-1")
    client.create_configuration_set(ConfigurationSetName="my-cs")
    with pytest.raises(ClientError) as e:
        client.delete_configuration_set_event_destination(ConfigurationSetName="my-cs", EventDestinationName="nope")
    assert e.value.response["Error"]["Code"] == "NotFoundException"


@mock_aws
def test_create_custom_verification_email_template():
    client = boto3.client("sesv2", region_name="us-east-1")
    client.create_custom_verification_email_template(
        TemplateName="v-tmpl", FromEmailAddress="v@example.com", TemplateSubject="Verify",
        TemplateContent="<html>Click</html>", SuccessRedirectionURL="https://e.com/s", FailureRedirectionURL="https://e.com/f")
    result = client.get_custom_verification_email_template(TemplateName="v-tmpl")
    assert result["TemplateName"] == "v-tmpl"
    assert result["FromEmailAddress"] == "v@example.com"


@mock_aws
def test_update_custom_verification_email_template():
    client = boto3.client("sesv2", region_name="us-east-1")
    client.create_custom_verification_email_template(
        TemplateName="v-tmpl", FromEmailAddress="v@example.com", TemplateSubject="Verify",
        TemplateContent="<html>Click</html>", SuccessRedirectionURL="https://e.com/s", FailureRedirectionURL="https://e.com/f")
    client.update_custom_verification_email_template(
        TemplateName="v-tmpl", FromEmailAddress="new@example.com", TemplateSubject="New",
        TemplateContent="<html>New</html>", SuccessRedirectionURL="https://e.com/s2", FailureRedirectionURL="https://e.com/f2")
    result = client.get_custom_verification_email_template(TemplateName="v-tmpl")
    assert result["FromEmailAddress"] == "new@example.com"


@mock_aws
def test_delete_custom_verification_email_template():
    client = boto3.client("sesv2", region_name="us-east-1")
    client.create_custom_verification_email_template(
        TemplateName="v-tmpl", FromEmailAddress="v@example.com", TemplateSubject="V",
        TemplateContent="<html>C</html>", SuccessRedirectionURL="https://e.com/s", FailureRedirectionURL="https://e.com/f")
    client.delete_custom_verification_email_template(TemplateName="v-tmpl")
    assert len(client.list_custom_verification_email_templates()["CustomVerificationEmailTemplates"]) == 0


@mock_aws
def test_list_custom_verification_email_templates():
    client = boto3.client("sesv2", region_name="us-east-1")
    assert client.list_custom_verification_email_templates()["CustomVerificationEmailTemplates"] == []
    for i in range(3):
        client.create_custom_verification_email_template(
            TemplateName=f"t-{i}", FromEmailAddress=f"v{i}@e.com", TemplateSubject=f"V{i}",
            TemplateContent=f"<html>{i}</html>", SuccessRedirectionURL=f"https://e.com/s{i}", FailureRedirectionURL=f"https://e.com/f{i}")
    assert len(client.list_custom_verification_email_templates()["CustomVerificationEmailTemplates"]) == 3


@mock_aws
def test_get_account():
    client = boto3.client("sesv2", region_name="us-east-1")
    result = client.get_account()
    assert result["SendingEnabled"] is True
    assert result["EnforcementStatus"] == "HEALTHY"
    assert "SendQuota" in result


@mock_aws
def test_put_account_details():
    client = boto3.client("sesv2", region_name="us-east-1")
    client.put_account_details(MailType="MARKETING", WebsiteURL="https://example.com", ContactLanguage="EN", UseCaseDescription="Marketing")
    result = client.get_account()
    assert result["Details"]["MailType"] == "MARKETING"


@mock_aws
def test_put_account_sending_attributes():
    client = boto3.client("sesv2", region_name="us-east-1")
    client.put_account_sending_attributes(SendingEnabled=False)
    assert client.get_account()["SendingEnabled"] is False
    client.put_account_sending_attributes(SendingEnabled=True)
    assert client.get_account()["SendingEnabled"] is True


@mock_aws
def test_put_account_suppression_attributes():
    client = boto3.client("sesv2", region_name="us-east-1")
    client.put_account_suppression_attributes(SuppressedReasons=["BOUNCE", "COMPLAINT"])
    assert client.get_account()["SuppressionAttributes"]["SuppressedReasons"] == ["BOUNCE", "COMPLAINT"]


@mock_aws
def test_put_configuration_set_sending_options():
    client = boto3.client("sesv2", region_name="us-east-1")
    client.create_configuration_set(ConfigurationSetName="my-cs")
    client.put_configuration_set_sending_options(ConfigurationSetName="my-cs", SendingEnabled=False)
    config = client.get_configuration_set(ConfigurationSetName="my-cs")
    assert config["SendingOptions"]["SendingEnabled"] is False
    client.put_configuration_set_sending_options(ConfigurationSetName="my-cs", SendingEnabled=True)
    config = client.get_configuration_set(ConfigurationSetName="my-cs")
    assert config["SendingOptions"]["SendingEnabled"] is True


@mock_aws
def test_put_configuration_set_reputation_options():
    client = boto3.client("sesv2", region_name="us-east-1")
    client.create_configuration_set(ConfigurationSetName="my-cs")
    client.put_configuration_set_reputation_options(ConfigurationSetName="my-cs", ReputationMetricsEnabled=True)
    config = client.get_configuration_set(ConfigurationSetName="my-cs")
    assert config["ReputationOptions"]["ReputationMetricsEnabled"] is True
