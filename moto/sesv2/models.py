"""SESV2Backend class with methods for supported APIs."""

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
        if self.kinesis_firehose_destination: r["KinesisFirehoseDestination"] = self.kinesis_firehose_destination
        if self.cloud_watch_destination: r["CloudWatchDestination"] = self.cloud_watch_destination
        if self.sns_destination: r["SnsDestination"] = self.sns_destination
        if self.pinpoint_destination: r["PinpointDestination"] = self.pinpoint_destination
        return r

class SESV2Backend(BaseBackend):
    """Implementation of SESV2 APIs, piggy back on v1 SES"""

    def __init__(self, region_name: str, account_id: str):
        super().__init__(region_name, account_id)

        # Store local variables in v1 backend for interoperability
        self.core_backend = ses_backends[self.account_id][self.region_name]
        self.email_templates = {}
        self.config_set_event_destinations = {}
        self.account_details = {}
        self.account_sending_enabled = True
        self.account_suppression_attributes = {}
        self.suppressed_destinations: dict[str, SuppressedDestination] = {}
        self.multi_region_endpoints: list[dict[str, Any]] = []

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

        return

    def delete_email_identity_policy(
        self, email_identity: str, policy_name: str
    ) -> None:
        if email_identity not in self.core_backend.email_identities:
            raise NotFoundException(email_identity)

        email_id = self.core_backend.email_identities[email_identity]

        if policy_name in email_id.policies:
            del email_id.policies[policy_name]

        return

    def update_email_identity_policy(
        self, email_identity: str, policy_name: str, policy: str
    ) -> None:
        if email_identity not in self.core_backend.email_identities:
            raise NotFoundException(email_identity)

        email_id = self.core_backend.email_identities[email_identity]

        email_id.policies[policy_name] = policy

        return

    def get_email_identity_policies(self, email_identity: str) -> dict[str, Any]:
        email_id = self.get_email_identity(email_identity)

        return email_id.policies


    def create_email_template(self, template_name, template_content):
        if template_name in self.email_templates:
            raise AlreadyExistsException(f"Template already exists with name: {template_name}")
        self.email_templates[template_name] = EmailTemplate(template_name=template_name, template_content=template_content)

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

    def create_configuration_set_event_destination(self, configuration_set_name, event_destination_name, event_destination):
        self.core_backend.describe_configuration_set(configuration_set_name=configuration_set_name)
        if configuration_set_name not in self.config_set_event_destinations:
            self.config_set_event_destinations[configuration_set_name] = {}
        dests = self.config_set_event_destinations[configuration_set_name]
        if event_destination_name in dests:
            raise AlreadyExistsException(f"Event destination already exists: {event_destination_name}")
        dests[event_destination_name] = EventDestination(name=event_destination_name, enabled=event_destination.get("Enabled", False), matching_event_types=event_destination.get("MatchingEventTypes", []), kinesis_firehose_destination=event_destination.get("KinesisFirehoseDestination"), cloud_watch_destination=event_destination.get("CloudWatchDestination"), sns_destination=event_destination.get("SnsDestination"), pinpoint_destination=event_destination.get("PinpointDestination"))

    def get_configuration_set_event_destinations(self, configuration_set_name):
        self.core_backend.describe_configuration_set(configuration_set_name=configuration_set_name)
        return list(self.config_set_event_destinations.get(configuration_set_name, {}).values())

    def update_configuration_set_event_destination(self, configuration_set_name, event_destination_name, event_destination):
        self.core_backend.describe_configuration_set(configuration_set_name=configuration_set_name)
        dests = self.config_set_event_destinations.get(configuration_set_name, {})
        if event_destination_name not in dests:
            raise SESV2NotFoundException(f"Event destination not found: {event_destination_name}")
        dests[event_destination_name] = EventDestination(name=event_destination_name, enabled=event_destination.get("Enabled", False), matching_event_types=event_destination.get("MatchingEventTypes", []), kinesis_firehose_destination=event_destination.get("KinesisFirehoseDestination"), cloud_watch_destination=event_destination.get("CloudWatchDestination"), sns_destination=event_destination.get("SnsDestination"), pinpoint_destination=event_destination.get("PinpointDestination"))

    def delete_configuration_set_event_destination(self, configuration_set_name, event_destination_name):
        self.core_backend.describe_configuration_set(configuration_set_name=configuration_set_name)
        dests = self.config_set_event_destinations.get(configuration_set_name, {})
        if event_destination_name not in dests:
            raise SESV2NotFoundException(f"Event destination not found: {event_destination_name}")
        del dests[event_destination_name]

    def create_custom_verification_email_template(self, template_name, from_email_address, template_subject, template_content, success_redirection_url, failure_redirection_url):
        self.core_backend.create_custom_verification_email_template(template_name=template_name, from_email_address=from_email_address, template_subject=template_subject, template_content=template_content, success_redirection_url=success_redirection_url, failure_redirection_url=failure_redirection_url)

    def get_custom_verification_email_template(self, template_name):
        return self.core_backend.get_custom_verification_email_template(template_name)

    def update_custom_verification_email_template(self, template_name, from_email_address, template_subject, template_content, success_redirection_url, failure_redirection_url):
        self.core_backend.update_custom_verification_email_template(template_name=template_name, from_email_address=from_email_address, template_subject=template_subject, template_content=template_content, success_redirection_url=success_redirection_url, failure_redirection_url=failure_redirection_url)

    def delete_custom_verification_email_template(self, template_name):
        self.core_backend.delete_custom_verification_email_template(template_name)

    @paginate(pagination_model=PAGINATION_MODEL)
    def list_custom_verification_email_templates(self):
        return self.core_backend.list_custom_verification_email_templates()

    def put_account_details(self, mail_type, website_url, contact_language, use_case_description, additional_contact_email_addresses, production_access_enabled):
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
        return {"DedicatedIpAutoWarmupEnabled": False, "EnforcementStatus": "HEALTHY", "ProductionAccessEnabled": self.account_details.get("ProductionAccessEnabled", False), "SendQuota": {"Max24HourSend": 200.0, "MaxSendRate": 1.0, "SentLast24Hours": 0.0}, "SendingEnabled": self.account_sending_enabled, "SuppressionAttributes": self.account_suppression_attributes, "Details": self.account_details if self.account_details else None}

    def put_account_sending_attributes(self, sending_enabled):
        self.account_sending_enabled = sending_enabled

    def put_account_suppression_attributes(self, suppressed_reasons):
        self.account_suppression_attributes = {"SuppressedReasons": suppressed_reasons}

    def put_configuration_set_sending_options(self, configuration_set_name, sending_enabled):
        config_set = self.core_backend.describe_configuration_set(configuration_set_name=configuration_set_name)
        config_set.enabled = sending_enabled

    def put_configuration_set_reputation_options(self, configuration_set_name, reputation_metrics_enabled):
        config_set = self.core_backend.describe_configuration_set(configuration_set_name=configuration_set_name)
        config_set.reputation_options = {"ReputationMetricsEnabled": reputation_metrics_enabled}

    def tag_resource(self, resource_arn: str, tags: list[dict[str, str]]) -> None:
        self.core_backend.tagger.tag_resource(resource_arn, tags)

    def untag_resource(self, resource_arn: str, tag_keys: list[str]) -> None:
        self.core_backend.tagger.untag_resource_using_names(resource_arn, tag_keys)

    def list_tags_for_resource(self, resource_arn: str) -> list[dict[str, str]]:
        tags = self.core_backend.tagger.list_tags_for_resource(resource_arn)
        return tags.get("Tags", [])


    def put_suppressed_destination(self, email_address: str, reason: str) -> None:
        self.suppressed_destinations[email_address] = SuppressedDestination(
            email_address=email_address, reason=reason
        )

    def get_suppressed_destination(self, email_address: str) -> SuppressedDestination:
        if email_address not in self.suppressed_destinations:
            raise SESV2NotFoundException(
                f"Suppressed destination {email_address} does not exist."
            )
        return self.suppressed_destinations[email_address]

    def list_suppressed_destinations(self) -> list[SuppressedDestination]:
        return list(self.suppressed_destinations.values())

    def delete_suppressed_destination(self, email_address: str) -> None:
        if email_address not in self.suppressed_destinations:
            raise SESV2NotFoundException(
                f"Suppressed destination {email_address} does not exist."
            )
        del self.suppressed_destinations[email_address]

    def get_dedicated_ips(self, pool_name: Optional[str] = None) -> list[dict[str, Any]]:
        pools = self.core_backend.dedicated_ip_pools
        ips: list[dict[str, Any]] = []
        if pool_name:
            if pool_name not in pools:
                raise NotFoundException(pool_name)
            ips.append({
                "Ip": "192.0.2.1",
                "WarmupStatus": "DONE",
                "WarmupPercentage": 100,
                "PoolName": pool_name,
            })
        else:
            for name in pools:
                ips.append({
                    "Ip": "192.0.2.1",
                    "WarmupStatus": "DONE",
                    "WarmupPercentage": 100,
                    "PoolName": name,
                })
        return ips

    def get_dedicated_ip(self, ip: str) -> dict[str, Any]:
        return {
            "Ip": ip,
            "WarmupStatus": "DONE",
            "WarmupPercentage": 100,
            "PoolName": "default",
        }

    def put_dedicated_ip_warmup_attributes(
        self, ip: str, warmup_percentage: int
    ) -> None:
        # No real IPs in mock, just accept the call
        pass

    def get_deliverability_dashboard_options(self) -> dict[str, Any]:
        return {
            "DashboardEnabled": False,
            "AccountStatus": "DISABLED",
        }

    def get_blacklist_reports(
        self, blacklist_item_names: list[str]
    ) -> dict[str, list[Any]]:
        return {name: [] for name in blacklist_item_names}

    def put_configuration_set_vdm_options(
        self, configuration_set_name: str, vdm_options: dict[str, Any]
    ) -> None:
        config_set = self.core_backend.describe_configuration_set(
            configuration_set_name=configuration_set_name
        )
        config_set.vdm_options = vdm_options

    def put_email_identity_configuration_set_attributes(
        self, email_identity: str, configuration_set_name: Optional[str] = None
    ) -> None:
        if email_identity not in self.core_backend.email_identities:
            raise NotFoundException(email_identity)
        identity = self.core_backend.email_identities[email_identity]
        identity.configuration_set_name = configuration_set_name

    def put_email_identity_dkim_signing_attributes(
        self,
        email_identity: str,
        signing_attributes_origin: str,
        signing_attributes: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        if email_identity not in self.core_backend.email_identities:
            raise NotFoundException(email_identity)
        identity = self.core_backend.email_identities[email_identity]
        dkim_attrs = identity.dkim_attributes or {}
        dkim_attrs["SigningAttributesOrigin"] = signing_attributes_origin
        dkim_attrs["Status"] = "SUCCESS"
        identity.dkim_attributes = dkim_attrs
        return {
            "DkimStatus": "SUCCESS",
            "DkimTokens": [
                f"token1._domainkey.{email_identity}",
                f"token2._domainkey.{email_identity}",
                f"token3._domainkey.{email_identity}",
            ],
        }

    def list_multi_region_endpoints(self) -> list[dict[str, Any]]:
        return self.multi_region_endpoints


sesv2_backends = BackendDict(SESV2Backend, "sesv2")
