"""SESV2Backend class with methods for supported APIs."""

import uuid
from typing import Any, Optional

from moto.core.base_backend import BackendDict, BaseBackend
from moto.utilities.paginator import paginate
from moto.core.common_models import BaseModel
from moto.core.utils import iso_8601_datetime_with_milliseconds

from ..ses.exceptions import NotFoundException
from ..ses.models import (
    ConfigurationSet,
    CustomVerificationEmailTemplate,
    Contact,
    ContactList,
    DedicatedIpPool,
    EmailIdentity,
    Message,
    RawMessage,
    ses_backends,
)
from ..ses.utils import get_arn
from .exceptions import AlreadyExistsException, SESV2NotFoundException


class SuppressedDestination(BaseModel):
    def __init__(self, email_address: str, reason: str) -> None:
        self.email_address = email_address
        self.reason = reason
        self.last_update_time = iso_8601_datetime_with_milliseconds()
        self.created_timestamp = iso_8601_datetime_with_milliseconds()

    def to_dict(self) -> dict[str, Any]:
        return {
            "EmailAddress": self.email_address,
            "Reason": self.reason,
            "LastUpdateTime": self.last_update_time,
        }

    def to_full_dict(self) -> dict[str, Any]:
        return {
            "EmailAddress": self.email_address,
            "Reason": self.reason,
            "LastUpdateTime": self.last_update_time,
            "Attributes": {
                "MessageId": "fake-message-id",
                "CreatedAt": self.created_timestamp,
            },
        }


class DedicatedIp(BaseModel):
    def __init__(self, ip: str, warmup_status: str, warmup_percentage: int, pool_name: str) -> None:
        self.ip = ip
        self.warmup_status = warmup_status
        self.warmup_percentage = warmup_percentage
        self.pool_name = pool_name

    def to_dict(self) -> dict[str, Any]:
        return {
            "Ip": self.ip,
            "WarmupStatus": self.warmup_status,
            "WarmupPercentage": self.warmup_percentage,
            "PoolName": self.pool_name,
        }


PAGINATION_MODEL = {
    "list_dedicated_ip_pools": {
        "input_token": "next_token",
        "limit_key": "page_size",
        "limit_default": 100,
        "unique_attribute": ["pool_name"],
    },
    "list_email_identities": {
        "input_token": "next_token",
        "limit_key": "page_size",
        "limit_default": 100,
        "unique_attribute": "IdentityName",
    },
    "list_configuration_sets": {
        "input_token": "next_token",
        "limit_key": "page_size",
        "limit_default": 100,
        "unique_attribute": "configuration_set_name",
    },
    "list_email_templates": {
        "input_token": "next_token",
        "limit_key": "page_size",
        "limit_default": 10,
        "unique_attribute": "template_name",
    },
    "list_custom_verification_email_templates": {
        "input_token": "next_token",
        "limit_key": "page_size",
        "limit_default": 50,
        "unique_attribute": "template_name",
    },
}


class EmailTemplate(BaseModel):
    def __init__(self, template_name, template_content):
        self.template_name = template_name
        self.template_content = template_content
        self.created_timestamp = iso_8601_datetime_with_milliseconds()

    def to_metadata_dict(self):
        return {"TemplateName": self.template_name, "CreatedTimestamp": self.created_timestamp}


class EventDestination(BaseModel):
    def __init__(self, name, enabled, matching_event_types, kinesis_firehose_destination=None, cloud_watch_destination=None, sns_destination=None, pinpoint_destination=None):
        self.name = name
        self.enabled = enabled
        self.matching_event_types = matching_event_types
        self.kinesis_firehose_destination = kinesis_firehose_destination
        self.cloud_watch_destination = cloud_watch_destination
        self.sns_destination = sns_destination
        self.pinpoint_destination = pinpoint_destination

    def to_dict(self):
        r = {"Name": self.name, "Enabled": self.enabled, "MatchingEventTypes": self.matching_event_types}
        if self.kinesis_firehose_destination:
            r["KinesisFirehoseDestination"] = self.kinesis_firehose_destination
        if self.cloud_watch_destination:
            r["CloudWatchDestination"] = self.cloud_watch_destination
        if self.sns_destination:
            r["SnsDestination"] = self.sns_destination
        if self.pinpoint_destination:
            r["PinpointDestination"] = self.pinpoint_destination
        return r


class ImportJob(BaseModel):
    def __init__(
        self,
        import_destination: dict[str, Any],
        import_data_source: dict[str, Any],
    ) -> None:
        self.job_id = str(uuid.uuid4())
        self.import_destination = import_destination
        self.import_data_source = import_data_source
        self.job_status = "COMPLETED"
        self.created_timestamp = iso_8601_datetime_with_milliseconds()
        self.completed_timestamp = iso_8601_datetime_with_milliseconds()

    def to_dict(self) -> dict[str, Any]:
        return {
            "JobId": self.job_id,
            "ImportDestination": self.import_destination,
            "JobStatus": self.job_status,
            "CreatedTimestamp": self.created_timestamp,
        }

    def to_full_dict(self) -> dict[str, Any]:
        return {
            "JobId": self.job_id,
            "ImportDestination": self.import_destination,
            "ImportDataSource": self.import_data_source,
            "JobStatus": self.job_status,
            "CreatedTimestamp": self.created_timestamp,
            "CompletedTimestamp": self.completed_timestamp,
            "ProcessedRecordsCount": 0,
            "FailedRecordsCount": 0,
        }


class ExportJob(BaseModel):
    def __init__(
        self,
        export_data_source: dict[str, Any],
        export_destination: dict[str, Any],
    ) -> None:
        self.job_id = str(uuid.uuid4())
        self.export_data_source = export_data_source
        self.export_destination = export_destination
        self.job_status = "COMPLETED"
        self.created_timestamp = iso_8601_datetime_with_milliseconds()
        self.completed_timestamp = iso_8601_datetime_with_milliseconds()

    def to_dict(self) -> dict[str, Any]:
        return {
            "JobId": self.job_id,
            "JobStatus": self.job_status,
            "CreatedTimestamp": self.created_timestamp,
            "ExportSourceType": self.export_data_source.get(
                "MetricsDataSource", {}
            ).get("Namespace", "VDM"),
        }

    def to_full_dict(self) -> dict[str, Any]:
        return {
            "JobId": self.job_id,
            "ExportDataSource": self.export_data_source,
            "ExportDestination": self.export_destination,
            "JobStatus": self.job_status,
            "CreatedTimestamp": self.created_timestamp,
            "CompletedTimestamp": self.completed_timestamp,
            "Statistics": {
                "ProcessedRecordsCount": 0,
                "ExportedRecordsCount": 0,
            },
        }


class SESV2Backend(BaseBackend):
    """Implementation of SESV2 APIs, piggy back on v1 SES"""

    def __init__(self, region_name: str, account_id: str):
        super().__init__(region_name, account_id)

        # Store local variables in v1 backend for interoperability
        self.core_backend = ses_backends[self.account_id][self.region_name]
        self.email_templates: dict[str, EmailTemplate] = {}
        self.config_set_event_destinations: dict[str, dict[str, EventDestination]] = {}
        self.account_details: dict[str, Any] = {}
        self.account_sending_enabled = True
        self.account_suppression_attributes: dict[str, Any] = {}
        self.suppressed_destinations: dict[str, SuppressedDestination] = {}
        self.account_vdm_attributes: dict[str, Any] = {}
        self.account_dedicated_ip_warmup_enabled = False
        self.multi_region_endpoints: dict[str, dict[str, Any]] = {}
        self.import_jobs: dict[str, ImportJob] = {}
        self.export_jobs: dict[str, ExportJob] = {}

    def create_contact_list(self, params: dict[str, Any]) -> None:
        name = params["ContactListName"]
        description = params.get("Description")
        topics = [] if "Topics" not in params else params["Topics"]
        new_list = ContactList(name, str(description), topics)

        if params.get("Tags"):
            self.core_backend.tagger.tag_resource(
                arn=get_arn(self, "ses", f"contact-list/{name}"),
                tags=params["Tags"],
            )

        self.core_backend.contacts_lists[name] = new_list

    def get_contact_list(self, contact_list_name: str) -> ContactList:
        if contact_list_name in self.core_backend.contacts_lists:
            return self.core_backend.contacts_lists[contact_list_name]
        else:
            raise NotFoundException(
                f"List with name: {contact_list_name} doesn't exist."
            )

    def list_contact_lists(self) -> list[ContactList]:
        return self.core_backend.contacts_lists.values()  # type: ignore[return-value]

    def delete_contact_list(self, name: str) -> None:
        if name in self.core_backend.contacts_lists:
            del self.core_backend.contacts_lists[name]
        else:
            raise NotFoundException(f"List with name: {name} doesn't exist")

    def create_contact(self, contact_list_name: str, params: dict[str, Any]) -> None:
        contact_list = self.get_contact_list(contact_list_name)
        contact_list.create_contact(contact_list_name, params)
        return

    def get_contact(self, email: str, contact_list_name: str) -> Contact:
        contact_list = self.get_contact_list(contact_list_name)
        contact = contact_list.get_contact(email)
        return contact

    def list_contacts(self, contact_list_name: str) -> list[Contact]:
        contact_list = self.get_contact_list(contact_list_name)
        contacts = contact_list.list_contacts()
        return contacts

    def delete_contact(self, email: str, contact_list_name: str) -> None:
        contact_list = self.get_contact_list(contact_list_name)
        contact_list.delete_contact(email)
        return

    def update_contact(
        self, contact_list_name: str, email_address: str, params: dict[str, Any]
    ) -> None:
        contact_list = self.get_contact_list(contact_list_name)
        contact = contact_list.get_contact(email_address)
        if "TopicPreferences" in params:
            contact.topic_preferences = params["TopicPreferences"]
        if "UnsubscribeAll" in params:
            contact.unsubscribe_all = params["UnsubscribeAll"]
        contact.last_updated_timestamp = iso_8601_datetime_with_milliseconds()

    def update_contact_list(
        self, contact_list_name: str, params: dict[str, Any]
    ) -> None:
        contact_list = self.get_contact_list(contact_list_name)
        if "Description" in params:
            contact_list.description = params["Description"]
        if "Topics" in params:
            contact_list.topics = params["Topics"]
        contact_list.last_updated_timestamp = iso_8601_datetime_with_milliseconds()

    def send_email(
        self, source: str, destinations: dict[str, list[str]], subject: str, body: str
    ) -> Message:
        message = self.core_backend.send_email(
            source=source,
            destinations=destinations,
            subject=subject,
            body=body,
        )
        return message

    def send_raw_email(
        self, source: str, destinations: list[str], raw_data: str
    ) -> RawMessage:
        message = self.core_backend.send_raw_email(
            source=source, destinations=destinations, raw_data=raw_data
        )
        return message

    def send_bulk_email(
        self,
        from_email_address: Optional[str],
        default_content: dict[str, Any],
        bulk_email_entries: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        results = []
        for _entry in bulk_email_entries:
            msg_id = str(uuid.uuid4())
            results.append({
                "Status": "SUCCESS",
                "MessageId": msg_id,
            })
        return results

    def send_custom_verification_email(
        self, email_address: str, template_name: str,
        configuration_set_name: Optional[str] = None,
    ) -> str:
        self.core_backend.get_custom_verification_email_template(template_name)
        return str(uuid.uuid4())

    def create_email_identity(
        self,
        email_identity: str,
        tags: Optional[list[dict[str, str]]],
        dkim_signing_attributes: Optional[object],
        configuration_set_name: Optional[str],
    ) -> EmailIdentity:
        if tags:
            self.core_backend.tagger.tag_resource(
                arn=get_arn(self, "ses", f"email-identity/{email_identity}"),
                tags=tags,
            )

        return self.core_backend.create_email_identity_v2(
            email_identity, tags, dkim_signing_attributes, configuration_set_name
        )

    def delete_email_identity(
        self,
        email_identity: str,
    ) -> None:
        self.core_backend.delete_identity(email_identity)

    @paginate(pagination_model=PAGINATION_MODEL)
    def list_email_identities(self) -> list[EmailIdentity]:
        identities = list(self.core_backend.email_identities.values())
        return identities

    def create_configuration_set(
        self,
        configuration_set_name: str,
        tracking_options: dict[str, str],
        delivery_options: dict[str, Any],
        reputation_options: dict[str, Any],
        sending_options: dict[str, bool],
        tags: list[dict[str, str]],
        suppression_options: dict[str, list[str]],
        vdm_options: dict[str, dict[str, str]],
    ) -> None:
        self.core_backend.create_configuration_set_v2(
            configuration_set_name=configuration_set_name,
            tracking_options=tracking_options,
            delivery_options=delivery_options,
            reputation_options=reputation_options,
            sending_options=sending_options,
            tags=tags,
            suppression_options=suppression_options,
            vdm_options=vdm_options,
        )

    def delete_configuration_set(self, configuration_set_name: str) -> None:
        self.core_backend.delete_configuration_set(configuration_set_name)

    def get_configuration_set(self, configuration_set_name: str) -> ConfigurationSet:
        config_set = self.core_backend.describe_configuration_set(
            configuration_set_name=configuration_set_name
        )
        return config_set

    @paginate(pagination_model=PAGINATION_MODEL)
    def list_configuration_sets(self) -> list[ConfigurationSet]:
        return self.core_backend._list_all_configuration_sets()

    def create_dedicated_ip_pool(
        self, pool_name: str, tags: list[dict[str, str]], scaling_mode: str
    ) -> None:
        if pool_name not in self.core_backend.dedicated_ip_pools:
            new_pool = DedicatedIpPool(
                pool_name=pool_name, tags=tags, scaling_mode=scaling_mode
            )

            if tags:
                self.core_backend.tagger.tag_resource(
                    arn=get_arn(self, "ses", f"dedicated-ip-pool/{pool_name}"),
                    tags=tags,
                )

            self.core_backend.dedicated_ip_pools[pool_name] = new_pool

    def delete_dedicated_ip_pool(self, pool_name: str) -> None:
        self.core_backend.dedicated_ip_pools.pop(pool_name)

    @paginate(pagination_model=PAGINATION_MODEL)
    def list_dedicated_ip_pools(self) -> list[str]:
        return list(self.core_backend.dedicated_ip_pools.keys())

    def get_dedicated_ip_pool(self, pool_name: str) -> DedicatedIpPool:
        if not self.core_backend.dedicated_ip_pools.get(pool_name, None):
            raise NotFoundException(pool_name)
        return self.core_backend.dedicated_ip_pools[pool_name]

    def get_email_identity(self, email_identity: str) -> EmailIdentity:
        if email_identity not in self.core_backend.email_identities:
            raise NotFoundException(email_identity)
        return self.core_backend.email_identities[email_identity]

    def create_email_identity_policy(
        self, email_identity: str, policy_name: str, policy: str
    ) -> None:
        email_id = self.get_email_identity(email_identity)
        email_id.policies[policy_name] = policy

    def delete_email_identity_policy(
        self, email_identity: str, policy_name: str
    ) -> None:
        if email_identity not in self.core_backend.email_identities:
            raise NotFoundException(email_identity)
        email_id = self.core_backend.email_identities[email_identity]
        if policy_name in email_id.policies:
            del email_id.policies[policy_name]

    def update_email_identity_policy(
        self, email_identity: str, policy_name: str, policy: str
    ) -> None:
        if email_identity not in self.core_backend.email_identities:
            raise NotFoundException(email_identity)
        email_id = self.core_backend.email_identities[email_identity]
        email_id.policies[policy_name] = policy

    def get_email_identity_policies(self, email_identity: str) -> dict[str, Any]:
        email_id = self.get_email_identity(email_identity)
        return email_id.policies

    def create_email_template(self, template_name, template_content):
        if template_name in self.email_templates:
            raise AlreadyExistsException(f"Template already exists with name: {template_name}")
        self.email_templates[template_name] = EmailTemplate(
            template_name=template_name, template_content=template_content
        )

    def get_email_template(self, template_name):
        if template_name not in self.email_templates:
            raise SESV2NotFoundException(f"Template not found with name: {template_name}")
        return self.email_templates[template_name]

    def update_email_template(self, template_name, template_content):
        if template_name not in self.email_templates:
            raise SESV2NotFoundException(f"Template not found with name: {template_name}")
        self.email_templates[template_name].template_content = template_content

    def delete_email_template(self, template_name):
        if template_name not in self.email_templates:
            raise SESV2NotFoundException(f"Template not found with name: {template_name}")
        del self.email_templates[template_name]

    @paginate(pagination_model=PAGINATION_MODEL)
    def list_email_templates(self):
        return list(self.email_templates.values())

    def test_render_email_template(
        self, template_name: str, template_data: str
    ) -> str:
        template = self.get_email_template(template_name)
        content = template.template_content
        html = content.get("Html", {}).get("Data", "") if isinstance(content.get("Html"), dict) else ""
        text = content.get("Text", {}).get("Data", "") if isinstance(content.get("Text"), dict) else ""
        subject_val = content.get("Subject")
        subject = subject_val.get("Data", "") if isinstance(subject_val, dict) else (subject_val or "")
        rendered = html or text or subject or ""
        return rendered

    def create_configuration_set_event_destination(
        self, configuration_set_name, event_destination_name, event_destination
    ):
        self.core_backend.describe_configuration_set(configuration_set_name=configuration_set_name)
        if configuration_set_name not in self.config_set_event_destinations:
            self.config_set_event_destinations[configuration_set_name] = {}
        dests = self.config_set_event_destinations[configuration_set_name]
        if event_destination_name in dests:
            raise AlreadyExistsException(f"Event destination already exists: {event_destination_name}")
        dests[event_destination_name] = EventDestination(
            name=event_destination_name,
            enabled=event_destination.get("Enabled", False),
            matching_event_types=event_destination.get("MatchingEventTypes", []),
            kinesis_firehose_destination=event_destination.get("KinesisFirehoseDestination"),
            cloud_watch_destination=event_destination.get("CloudWatchDestination"),
            sns_destination=event_destination.get("SnsDestination"),
            pinpoint_destination=event_destination.get("PinpointDestination"),
        )

    def get_configuration_set_event_destinations(self, configuration_set_name):
        self.core_backend.describe_configuration_set(configuration_set_name=configuration_set_name)
        return list(self.config_set_event_destinations.get(configuration_set_name, {}).values())

    def update_configuration_set_event_destination(
        self, configuration_set_name, event_destination_name, event_destination
    ):
        self.core_backend.describe_configuration_set(configuration_set_name=configuration_set_name)
        dests = self.config_set_event_destinations.get(configuration_set_name, {})
        if event_destination_name not in dests:
            raise SESV2NotFoundException(f"Event destination not found: {event_destination_name}")
        dests[event_destination_name] = EventDestination(
            name=event_destination_name,
            enabled=event_destination.get("Enabled", False),
            matching_event_types=event_destination.get("MatchingEventTypes", []),
            kinesis_firehose_destination=event_destination.get("KinesisFirehoseDestination"),
            cloud_watch_destination=event_destination.get("CloudWatchDestination"),
            sns_destination=event_destination.get("SnsDestination"),
            pinpoint_destination=event_destination.get("PinpointDestination"),
        )

    def delete_configuration_set_event_destination(self, configuration_set_name, event_destination_name):
        self.core_backend.describe_configuration_set(configuration_set_name=configuration_set_name)
        dests = self.config_set_event_destinations.get(configuration_set_name, {})
        if event_destination_name not in dests:
            raise SESV2NotFoundException(f"Event destination not found: {event_destination_name}")
        del dests[event_destination_name]

    def create_custom_verification_email_template(
        self, template_name, from_email_address, template_subject,
        template_content, success_redirection_url, failure_redirection_url
    ):
        self.core_backend.create_custom_verification_email_template(
            template_name=template_name,
            from_email_address=from_email_address,
            template_subject=template_subject,
            template_content=template_content,
            success_redirection_url=success_redirection_url,
            failure_redirection_url=failure_redirection_url,
        )

    def get_custom_verification_email_template(self, template_name):
        return self.core_backend.get_custom_verification_email_template(template_name)

    def update_custom_verification_email_template(
        self, template_name, from_email_address, template_subject,
        template_content, success_redirection_url, failure_redirection_url
    ):
        self.core_backend.update_custom_verification_email_template(
            template_name=template_name,
            from_email_address=from_email_address,
            template_subject=template_subject,
            template_content=template_content,
            success_redirection_url=success_redirection_url,
            failure_redirection_url=failure_redirection_url,
        )

    def delete_custom_verification_email_template(self, template_name):
        self.core_backend.delete_custom_verification_email_template(template_name)

    @paginate(pagination_model=PAGINATION_MODEL)
    def list_custom_verification_email_templates(self):
        return self.core_backend.list_custom_verification_email_templates()

    def put_account_details(
        self, mail_type, website_url, contact_language,
        use_case_description, additional_contact_email_addresses, production_access_enabled
    ):
        self.account_details = {"MailType": mail_type, "WebsiteURL": website_url}
        if contact_language is not None:
            self.account_details["ContactLanguage"] = contact_language
        if use_case_description is not None:
            self.account_details["UseCaseDescription"] = use_case_description
        if additional_contact_email_addresses is not None:
            self.account_details["AdditionalContactEmailAddresses"] = additional_contact_email_addresses
        if production_access_enabled is not None:
            self.account_details["ProductionAccessEnabled"] = production_access_enabled

    def get_account(self):
        result = {
            "DedicatedIpAutoWarmupEnabled": self.account_dedicated_ip_warmup_enabled,
            "EnforcementStatus": "HEALTHY",
            "ProductionAccessEnabled": self.account_details.get("ProductionAccessEnabled", False),
            "SendQuota": {"Max24HourSend": 200.0, "MaxSendRate": 1.0, "SentLast24Hours": 0.0},
            "SendingEnabled": self.account_sending_enabled,
            "SuppressionAttributes": self.account_suppression_attributes,
        }
        if self.account_vdm_attributes:
            result["VdmAttributes"] = self.account_vdm_attributes
        if self.account_details:
            result["Details"] = self.account_details
        return result

    def put_account_sending_attributes(self, sending_enabled):
        self.account_sending_enabled = sending_enabled

    def put_account_suppression_attributes(self, suppressed_reasons):
        self.account_suppression_attributes = {"SuppressedReasons": suppressed_reasons}

    def put_account_dedicated_ip_warmup_attributes(self, auto_warmup_enabled: bool = False) -> None:
        self.account_dedicated_ip_warmup_enabled = auto_warmup_enabled

    def put_account_vdm_attributes(self, vdm_attributes: dict[str, Any]) -> None:
        self.account_vdm_attributes = vdm_attributes

    def put_configuration_set_sending_options(self, configuration_set_name, sending_enabled):
        config_set = self.core_backend.describe_configuration_set(
            configuration_set_name=configuration_set_name
        )
        config_set.enabled = sending_enabled

    def put_configuration_set_reputation_options(self, configuration_set_name, reputation_metrics_enabled):
        config_set = self.core_backend.describe_configuration_set(
            configuration_set_name=configuration_set_name
        )
        config_set.reputation_options = {"ReputationMetricsEnabled": reputation_metrics_enabled}

    def put_configuration_set_delivery_options(
        self, configuration_set_name: str, tls_policy: Optional[str] = None,
        sending_pool_name: Optional[str] = None,
    ) -> None:
        config_set = self.core_backend.describe_configuration_set(
            configuration_set_name=configuration_set_name
        )
        config_set.delivery_options = {
            "TlsPolicy": tls_policy or "OPTIONAL",
            "SendingPoolName": sending_pool_name or "",
        }

    def put_configuration_set_suppression_options(
        self, configuration_set_name: str, suppressed_reasons: Optional[list[str]] = None
    ) -> None:
        config_set = self.core_backend.describe_configuration_set(
            configuration_set_name=configuration_set_name
        )
        config_set.suppression_options = {"SuppressedReasons": suppressed_reasons or []}

    def put_configuration_set_tracking_options(
        self, configuration_set_name: str, custom_redirect_domain: Optional[str] = None
    ) -> None:
        config_set = self.core_backend.describe_configuration_set(
            configuration_set_name=configuration_set_name
        )
        config_set.tracking_options = {"CustomRedirectDomain": custom_redirect_domain or ""}

    def put_configuration_set_archiving_options(
        self, configuration_set_name: str, archive_arn: Optional[str] = None
    ) -> None:
        config_set = self.core_backend.describe_configuration_set(
            configuration_set_name=configuration_set_name
        )
        config_set.archiving_options = {"ArchiveArn": archive_arn or ""}

    def tag_resource(self, resource_arn: str, tags: list[dict[str, str]]) -> None:
        self.core_backend.tagger.tag_resource(resource_arn, tags)

    def untag_resource(self, resource_arn: str, tag_keys: list[str]) -> None:
        self.core_backend.tagger.untag_resource_using_names(resource_arn, tag_keys)

    def list_tags_for_resource(self, resource_arn: str) -> list[dict[str, str]]:
        tags = self.core_backend.tagger.list_tags_for_resource(resource_arn)
        return tags.get("Tags", [])

    # ===== Suppressed Destinations =====

    def put_suppressed_destination(self, email_address: str, reason: str) -> None:
        self.suppressed_destinations[email_address] = SuppressedDestination(
            email_address=email_address, reason=reason
        )

    def get_suppressed_destination(self, email_address: str) -> SuppressedDestination:
        if email_address not in self.suppressed_destinations:
            raise SESV2NotFoundException(
                f"Suppressed destination {email_address} not found."
            )
        return self.suppressed_destinations[email_address]

    def list_suppressed_destinations(self) -> list[SuppressedDestination]:
        return list(self.suppressed_destinations.values())

    def delete_suppressed_destination(self, email_address: str) -> None:
        if email_address not in self.suppressed_destinations:
            raise SESV2NotFoundException(
                f"Suppressed destination {email_address} not found."
            )
        del self.suppressed_destinations[email_address]

    # ===== Dedicated IP operations =====

    def get_dedicated_ips(self, pool_name: Optional[str] = None) -> list[dict[str, Any]]:
        return []

    def get_dedicated_ip(self, ip: str) -> dict[str, Any]:
        raise SESV2NotFoundException(f"Dedicated IP {ip} not found.")

    def put_dedicated_ip_warmup_attributes(self, ip: str, warmup_percentage: int) -> None:
        pass

    def put_dedicated_ip_in_pool(self, ip: str, destination_pool_name: str) -> None:
        pass

    def put_dedicated_ip_pool_scaling_attributes(
        self, pool_name: str, scaling_mode: str
    ) -> None:
        if pool_name not in self.core_backend.dedicated_ip_pools:
            raise SESV2NotFoundException(f"Dedicated IP pool {pool_name} not found.")
        self.core_backend.dedicated_ip_pools[pool_name].scaling_mode = scaling_mode

    # ===== Deliverability Dashboard =====

    def get_deliverability_dashboard_options(self) -> dict[str, Any]:
        return {
            "DashboardEnabled": False,
            "AccountStatus": "DISABLED",
            "SubscriptionExpiryDate": iso_8601_datetime_with_milliseconds(),
            "ActiveSubscribedDomains": [],
            "PendingExpirationSubscribedDomains": [],
        }

    def put_deliverability_dashboard_option(self, dashboard_enabled: bool = False) -> None:
        pass

    def create_deliverability_test_report(
        self, from_email_address: str, content: dict[str, Any],
        report_name: Optional[str] = None, tags: Optional[list[dict[str, str]]] = None,
    ) -> dict[str, Any]:
        report_id = str(uuid.uuid4())
        return {
            "ReportId": report_id,
            "DeliverabilityTestStatus": "COMPLETED",
        }

    def get_deliverability_test_report(self, report_id: str) -> dict[str, Any]:
        return {
            "DeliverabilityTestReport": {
                "ReportId": report_id,
                "ReportName": "test-report",
                "Subject": "Test",
                "FromEmailAddress": "test@example.com",
                "CreateDate": iso_8601_datetime_with_milliseconds(),
                "DeliverabilityTestStatus": "COMPLETED",
            },
            "OverallPlacement": {
                "InboxPercentage": 100.0,
                "SpamPercentage": 0.0,
                "MissingPercentage": 0.0,
                "SpfPercentage": 100.0,
                "DkimPercentage": 100.0,
            },
            "IspPlacements": [],
            "Message": "",
            "Tags": [],
        }

    def list_deliverability_test_reports(self) -> list[dict[str, Any]]:
        return []

    def get_domain_statistics_report(
        self, domain: str, start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> dict[str, Any]:
        return {
            "OverallVolume": {
                "VolumeStatistics": {
                    "InboxRawCount": 0,
                    "SpamRawCount": 0,
                    "ProjectedInbox": 0,
                    "ProjectedSpam": 0,
                },
                "ReadRatePercent": 0.0,
                "DomainIspPlacements": [],
            },
            "DailyVolumes": [],
        }

    def get_domain_deliverability_campaign(self, campaign_id: str) -> dict[str, Any]:
        return {
            "DomainDeliverabilityCampaign": {
                "CampaignId": campaign_id,
                "ImageUrl": "",
                "Subject": "",
                "FromAddress": "",
                "SendingIps": [],
                "InboxCount": 0,
                "SpamCount": 0,
                "ReadRate": 0.0,
                "DeleteRate": 0.0,
                "ReadDeleteRate": 0.0,
                "ProjectedVolume": 0,
                "Esps": [],
            }
        }

    def list_domain_deliverability_campaigns(
        self, subscribed_domain: str, start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> list[dict[str, Any]]:
        return []

    # ===== Blacklist Reports =====

    def get_blacklist_reports(
        self, blacklist_item_names: Optional[list[str]] = None
    ) -> dict[str, Any]:
        return {"BlacklistReport": {}}

    # ===== VDM Attributes =====

    def put_configuration_set_vdm_attributes(
        self, configuration_set_name: str, vdm_options: dict[str, dict[str, str]]
    ) -> None:
        config_set = self.core_backend.describe_configuration_set(
            configuration_set_name=configuration_set_name
        )
        config_set.vdm_options = vdm_options

    # ===== Email Identity Configuration Set =====

    def put_email_identity_configuration_set_attributes(
        self, email_identity: str, configuration_set_name: Optional[str]
    ) -> None:
        if email_identity not in self.core_backend.email_identities:
            raise NotFoundException(email_identity)
        email_id = self.core_backend.email_identities[email_identity]
        email_id.configuration_set_name = configuration_set_name

    # ===== DKIM Signing =====

    def put_email_identity_dkim_signing_attributes(
        self, email_identity: str, signing_attributes_origin: str,
        signing_attributes: Optional[dict[str, Any]] = None
    ) -> dict[str, Any]:
        if email_identity not in self.core_backend.email_identities:
            raise NotFoundException(email_identity)
        email_id = self.core_backend.email_identities[email_identity]
        email_id.dkim_attributes["SigningAttributesOrigin"] = signing_attributes_origin
        if signing_attributes_origin == "EXTERNAL":
            email_id.dkim_attributes["Status"] = "PENDING"
            email_id.dkim_attributes["SigningEnabled"] = True
        else:
            email_id.dkim_attributes["Status"] = "SUCCESS"
            email_id.dkim_attributes["SigningEnabled"] = True
        return {
            "DkimStatus": email_id.dkim_attributes.get("Status", "NOT_STARTED"),
            "DkimTokens": [
                f"token1-{email_identity}",
                f"token2-{email_identity}",
                f"token3-{email_identity}",
            ],
        }

    def put_email_identity_dkim_attributes(
        self, email_identity: str, signing_enabled: bool = True
    ) -> None:
        if email_identity not in self.core_backend.email_identities:
            raise NotFoundException(email_identity)
        email_id = self.core_backend.email_identities[email_identity]
        email_id.dkim_attributes["SigningEnabled"] = signing_enabled

    def put_email_identity_feedback_attributes(
        self, email_identity: str, email_forwarding_enabled: bool = True
    ) -> None:
        if email_identity not in self.core_backend.email_identities:
            raise NotFoundException(email_identity)
        email_id = self.core_backend.email_identities[email_identity]
        email_id.feedback_forwarding_status = email_forwarding_enabled

    def put_email_identity_mail_from_attributes(
        self, email_identity: str, mail_from_domain: Optional[str] = None,
        behavior_on_mx_failure: Optional[str] = None,
    ) -> None:
        if email_identity not in self.core_backend.email_identities:
            raise NotFoundException(email_identity)
        email_id = self.core_backend.email_identities[email_identity]
        email_id.mail_from_attributes = {
            "MailFromDomain": mail_from_domain or "",
            "MailFromDomainStatus": "SUCCESS" if mail_from_domain else "NONE",
            "BehaviorOnMxFailure": behavior_on_mx_failure or "USE_DEFAULT_VALUE",
        }

    # ===== Multi-Region Endpoints =====

    def list_multi_region_endpoints(self) -> list[dict[str, Any]]:
        return list(self.multi_region_endpoints.values())

    def create_multi_region_endpoint(
        self, endpoint_name: str, details: dict[str, Any],
        tags: Optional[list[dict[str, str]]] = None,
    ) -> dict[str, Any]:
        endpoint_id = str(uuid.uuid4())
        status = "READY"
        endpoint = {
            "EndpointName": endpoint_name,
            "EndpointId": endpoint_id,
            "Status": status,
            "Details": details,
            "CreatedTimestamp": iso_8601_datetime_with_milliseconds(),
            "LastUpdatedTimestamp": iso_8601_datetime_with_milliseconds(),
        }
        self.multi_region_endpoints[endpoint_name] = endpoint
        return {"EndpointId": endpoint_id, "Status": status}

    def get_multi_region_endpoint(self, endpoint_name: str) -> dict[str, Any]:
        if endpoint_name not in self.multi_region_endpoints:
            raise SESV2NotFoundException(
                f"Multi-region endpoint {endpoint_name} not found."
            )
        return self.multi_region_endpoints[endpoint_name]

    def delete_multi_region_endpoint(self, endpoint_name: str) -> None:
        if endpoint_name not in self.multi_region_endpoints:
            raise SESV2NotFoundException(
                f"Multi-region endpoint {endpoint_name} not found."
            )
        del self.multi_region_endpoints[endpoint_name]

    # ===== Import Jobs =====

    def create_import_job(
        self, import_destination: dict[str, Any], import_data_source: dict[str, Any]
    ) -> str:
        job = ImportJob(
            import_destination=import_destination,
            import_data_source=import_data_source,
        )
        self.import_jobs[job.job_id] = job
        return job.job_id

    def get_import_job(self, job_id: str) -> ImportJob:
        if job_id not in self.import_jobs:
            raise SESV2NotFoundException(f"Import job {job_id} not found.")
        return self.import_jobs[job_id]

    def list_import_jobs(self) -> list[ImportJob]:
        return list(self.import_jobs.values())

    # ===== Export Jobs =====

    def create_export_job(
        self, export_data_source: dict[str, Any], export_destination: dict[str, Any]
    ) -> str:
        job = ExportJob(
            export_data_source=export_data_source,
            export_destination=export_destination,
        )
        self.export_jobs[job.job_id] = job
        return job.job_id

    def get_export_job(self, job_id: str) -> ExportJob:
        if job_id not in self.export_jobs:
            raise SESV2NotFoundException(f"Export job {job_id} not found.")
        return self.export_jobs[job_id]

    def list_export_jobs(self) -> list[ExportJob]:
        return list(self.export_jobs.values())

    def cancel_export_job(self, job_id: str) -> None:
        if job_id not in self.export_jobs:
            raise SESV2NotFoundException(f"Export job {job_id} not found.")
        self.export_jobs[job_id].job_status = "CANCELLED"

    # ===== Insights =====

    def get_message_insights(self, message_id: str) -> dict[str, Any]:
        return {
            "MessageId": message_id,
            "FromEmailAddress": "",
            "Subject": "",
            "EmailTags": [],
            "Insights": [],
        }

    def get_email_address_insights(self, email_address: str) -> dict[str, Any]:
        return {
            "EmailAddressInsights": {
                "EmailAddress": email_address,
                "Insights": [],
            }
        }

    # ===== Recommendations =====

    def list_recommendations(self) -> list[dict[str, Any]]:
        return []

    # ===== Metrics =====

    def batch_get_metric_data(
        self, queries: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        results = []
        for query in queries:
            results.append({
                "Id": query.get("Id", ""),
                "Timestamps": [],
                "Values": [],
            })
        return results

    # ===== Tenants (stubs) =====

    def create_tenant(self, params: dict[str, Any]) -> dict[str, Any]:
        tenant_id = str(uuid.uuid4())
        return {"TenantId": tenant_id}

    def delete_tenant(self, params: dict[str, Any]) -> None:
        pass

    def get_tenant(self, params: dict[str, Any]) -> dict[str, Any]:
        return {
            "TenantId": params.get("TenantId", ""),
            "TenantName": params.get("TenantName", ""),
            "TenantStatus": "ACTIVE",
            "CreatedTimestamp": iso_8601_datetime_with_milliseconds(),
        }

    def list_tenants(self) -> list[dict[str, Any]]:
        return []

    def create_tenant_resource_association(
        self, params: dict[str, Any]
    ) -> dict[str, Any]:
        return {}

    def delete_tenant_resource_association(self, params: dict[str, Any]) -> None:
        pass

    def list_tenant_resources(self, params: dict[str, Any]) -> list[dict[str, Any]]:
        return []

    def list_resource_tenants(self, params: dict[str, Any]) -> list[dict[str, Any]]:
        return []

    # ===== Reputation Entities (stubs) =====

    def get_reputation_entity(
        self, entity_type: str, entity_reference: str
    ) -> dict[str, Any]:
        return {
            "ReputationEntityType": entity_type,
            "ReputationEntityReference": entity_reference,
            "CustomerManagedStatus": "DISABLED",
        }

    def list_reputation_entities(self) -> list[dict[str, Any]]:
        return []

    def update_reputation_entity_customer_managed_status(
        self, entity_type: str, entity_reference: str, customer_managed_status: str
    ) -> None:
        pass

    def update_reputation_entity_policy(
        self, entity_type: str, entity_reference: str, policy: str
    ) -> None:
        pass


sesv2_backends = BackendDict(SESV2Backend, "sesv2")
