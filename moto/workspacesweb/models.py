"""WorkSpacesWebBackend class with methods for supported APIs."""

import datetime
import uuid
from typing import Any, Optional

from moto.core.base_backend import BackendDict, BaseBackend
from moto.core.common_models import BaseModel
from moto.core.exceptions import JsonRESTError
from moto.utilities.utils import get_partition

from ..utilities.tagging_service import TaggingService


class ResourceNotFoundException(JsonRESTError):
    code = 404

    def __init__(self, msg: str) -> None:
        super().__init__("ResourceNotFoundException", msg)


class FakeUserSettings(BaseModel):
    def __init__(
        self,
        additional_encryption_context: Any,
        client_token: str,
        cookie_synchronization_configuration: str,
        copy_allowed: bool,
        customer_managed_key: str,
        deep_link_allowed: bool,
        disconnect_timeout_in_minutes: int,
        download_allowed: bool,
        idle_disconnect_timeout_in_minutes: int,
        paste_allowed: bool,
        print_allowed: bool,
        upload_allowed: bool,
        region_name: str,
        account_id: str,
    ):
        self.user_settings_id = str(uuid.uuid4())
        self.arn = self.arn_formatter(self.user_settings_id, account_id, region_name)
        self.additional_encryption_context = additional_encryption_context
        self.client_token = client_token
        self.cookie_synchronization_configuration = cookie_synchronization_configuration
        self.copy_allowed = copy_allowed if copy_allowed else "Disabled"
        self.customer_managed_key = customer_managed_key
        self.deep_link_allowed = deep_link_allowed if deep_link_allowed else "Disabled"
        self.disconnect_timeout_in_minutes = disconnect_timeout_in_minutes
        self.download_allowed = download_allowed if download_allowed else "Disabled"
        self.idle_disconnect_timeout_in_minutes = idle_disconnect_timeout_in_minutes
        self.paste_allowed = paste_allowed if paste_allowed else "Disabled"
        self.print_allowed = print_allowed if print_allowed else "Disabled"
        self.upload_allowed = upload_allowed if upload_allowed else "Disabled"
        self.associated_portal_arns: list[str] = []

    def arn_formatter(self, _id: str, account_id: str, region_name: str) -> str:
        return f"arn:{get_partition(region_name)}:workspaces-web:{region_name}:{account_id}:user-settings/{_id}"

    def to_dict(self) -> dict[str, Any]:
        return {
            "associatedPortalArns": self.associated_portal_arns,
            "additionalEncryptionContext": self.additional_encryption_context,
            "clientToken": self.client_token,
            "cookieSynchronizationConfiguration": self.cookie_synchronization_configuration,
            "copyAllowed": self.copy_allowed,
            "customerManagedKey": self.customer_managed_key,
            "deepLinkAllowed": self.deep_link_allowed,
            "disconnectTimeoutInMinutes": self.disconnect_timeout_in_minutes,
            "downloadAllowed": self.download_allowed,
            "idleDisconnectTimeoutInMinutes": self.idle_disconnect_timeout_in_minutes,
            "pasteAllowed": self.paste_allowed,
            "printAllowed": self.print_allowed,
            "uploadAllowed": self.upload_allowed,
            "userSettingsArn": self.arn,
        }


class FakeUserAccessLoggingSettings(BaseModel):
    def __init__(
        self,
        client_token: str,
        kinesis_stream_arn: str,
        region_name: str,
        account_id: str,
    ):
        self.user_access_logging_settings_id = str(uuid.uuid4())
        self.arn = self.arn_formatter(
            self.user_access_logging_settings_id, account_id, region_name
        )
        self.client_token = client_token
        self.kinesis_stream_arn = kinesis_stream_arn
        self.associated_portal_arns: list[str] = []

    def arn_formatter(self, _id: str, account_id: str, region_name: str) -> str:
        return f"arn:{get_partition(region_name)}:workspaces-web:{region_name}:{account_id}:user-access-logging-settings/{_id}"

    def to_dict(self) -> dict[str, Any]:
        return {
            "associatedPortalArns": self.associated_portal_arns,
            "kinesisStreamArn": self.kinesis_stream_arn,
            "userAccessLoggingSettingsArn": self.arn,
        }


class FakeNetworkSettings(BaseModel):
    def __init__(
        self,
        security_group_ids: list[str],
        subnet_ids: list[str],
        vpc_id: str,
        region_name: str,
        account_id: str,
    ):
        self.network_settings_id = str(uuid.uuid4())
        self.arn = self.arn_formatter(self.network_settings_id, account_id, region_name)
        self.security_group_ids = security_group_ids
        self.subnet_ids = subnet_ids
        self.vpc_id = vpc_id
        self.associated_portal_arns: list[str] = []

    def arn_formatter(self, _id: str, account_id: str, region_name: str) -> str:
        return f"arn:{get_partition(region_name)}:workspaces-web:{region_name}:{account_id}:network-settings/{_id}"

    def to_dict(self) -> dict[str, Any]:
        return {
            "associatedPortalArns": self.associated_portal_arns,
            "networkSettingsArn": self.arn,
            "securityGroupIds": self.security_group_ids,
            "subnetIds": self.subnet_ids,
            "vpcId": self.vpc_id,
        }


class FakeBrowserSettings(BaseModel):
    def __init__(
        self,
        additional_encryption_context: Any,
        browser_policy: str,
        client_token: str,
        customer_managed_key: str,
        region_name: str,
        account_id: str,
    ):
        self.browser_settings_id = str(uuid.uuid4())
        self.arn = self.arn_formatter(self.browser_settings_id, account_id, region_name)
        self.additional_encryption_context = additional_encryption_context
        self.browser_policy = browser_policy
        self.client_token = client_token
        self.customer_managed_key = customer_managed_key
        self.associated_portal_arns: list[str] = []

    def arn_formatter(self, _id: str, account_id: str, region_name: str) -> str:
        return f"arn:{get_partition(region_name)}:workspaces-web:{region_name}:{account_id}:browser-settings/{_id}"

    def to_dict(self) -> dict[str, Any]:
        return {
            "associatedPortalArns": self.associated_portal_arns,
            "browserSettingsArn": self.arn,
            "additionalEncryptionContext": self.additional_encryption_context,
            "browserPolicy": self.browser_policy,
            "customerManagedKey": self.customer_managed_key,
        }


class FakeIpAccessSettings(BaseModel):
    def __init__(
        self,
        additional_encryption_context: Any,
        client_token: str,
        customer_managed_key: str,
        description: str,
        display_name: str,
        ip_rules: list[dict[str, Any]],
        tags: Any,
        region_name: str,
        account_id: str,
    ):
        self.ip_access_settings_id = str(uuid.uuid4())
        self.arn = self.arn_formatter(self.ip_access_settings_id, account_id, region_name)
        self.additional_encryption_context = additional_encryption_context
        self.client_token = client_token
        self.customer_managed_key = customer_managed_key
        self.description = description
        self.display_name = display_name
        self.ip_rules = ip_rules or []
        self.associated_portal_arns: list[str] = []
        self.creation_date = datetime.datetime.now().isoformat()

    def arn_formatter(self, _id: str, account_id: str, region_name: str) -> str:
        return f"arn:{get_partition(region_name)}:workspaces-web:{region_name}:{account_id}:ip-access-settings/{_id}"

    def to_dict(self) -> dict[str, Any]:
        return {
            "associatedPortalArns": self.associated_portal_arns,
            "creationDate": self.creation_date,
            "description": self.description,
            "displayName": self.display_name,
            "ipAccessSettingsArn": self.arn,
            "ipRules": self.ip_rules,
        }


class FakeTrustStore(BaseModel):
    def __init__(
        self,
        certificate_list: list[str],
        client_token: str,
        tags: Any,
        region_name: str,
        account_id: str,
    ):
        self.trust_store_id = str(uuid.uuid4())
        self.arn = self.arn_formatter(self.trust_store_id, account_id, region_name)
        self.certificate_list = certificate_list or []
        self.client_token = client_token
        self.associated_portal_arns: list[str] = []

    def arn_formatter(self, _id: str, account_id: str, region_name: str) -> str:
        return f"arn:{get_partition(region_name)}:workspaces-web:{region_name}:{account_id}:trust-store/{_id}"

    def to_dict(self) -> dict[str, Any]:
        return {
            "associatedPortalArns": self.associated_portal_arns,
            "trustStoreArn": self.arn,
        }


class FakeIdentityProvider(BaseModel):
    def __init__(
        self,
        portal_arn: str,
        identity_provider_details: dict[str, str],
        identity_provider_name: str,
        identity_provider_type: str,
        client_token: str,
        region_name: str,
        account_id: str,
    ):
        self.identity_provider_id = str(uuid.uuid4())
        self.arn = self.arn_formatter(self.identity_provider_id, account_id, region_name)
        self.portal_arn = portal_arn
        self.identity_provider_details = identity_provider_details or {}
        self.identity_provider_name = identity_provider_name
        self.identity_provider_type = identity_provider_type
        self.client_token = client_token

    def arn_formatter(self, _id: str, account_id: str, region_name: str) -> str:
        return f"arn:{get_partition(region_name)}:workspaces-web:{region_name}:{account_id}:identity-provider/{_id}"

    def to_dict(self) -> dict[str, Any]:
        return {
            "identityProviderArn": self.arn,
            "identityProviderDetails": self.identity_provider_details,
            "identityProviderName": self.identity_provider_name,
            "identityProviderType": self.identity_provider_type,
        }


class FakeDataProtectionSettings(BaseModel):
    def __init__(
        self,
        additional_encryption_context: Any,
        client_token: str,
        customer_managed_key: str,
        description: str,
        display_name: str,
        inline_redaction_configuration: Any,
        tags: Any,
        region_name: str,
        account_id: str,
    ):
        self.data_protection_settings_id = str(uuid.uuid4())
        self.arn = self.arn_formatter(self.data_protection_settings_id, account_id, region_name)
        self.additional_encryption_context = additional_encryption_context
        self.client_token = client_token
        self.customer_managed_key = customer_managed_key
        self.description = description
        self.display_name = display_name
        self.inline_redaction_configuration = inline_redaction_configuration
        self.associated_portal_arns: list[str] = []
        self.creation_date = datetime.datetime.now().isoformat()

    def arn_formatter(self, _id: str, account_id: str, region_name: str) -> str:
        return f"arn:{get_partition(region_name)}:workspaces-web:{region_name}:{account_id}:data-protection-settings/{_id}"

    def to_dict(self) -> dict[str, Any]:
        return {
            "associatedPortalArns": self.associated_portal_arns,
            "creationDate": self.creation_date,
            "dataProtectionSettingsArn": self.arn,
            "description": self.description,
            "displayName": self.display_name,
            "inlineRedactionConfiguration": self.inline_redaction_configuration,
        }


class FakeSessionLogger(BaseModel):
    def __init__(
        self,
        client_token: str,
        display_name: str,
        event_filter: Any,
        log_configuration: Any,
        tags: Any,
        region_name: str,
        account_id: str,
    ):
        self.session_logger_id = str(uuid.uuid4())
        self.arn = self.arn_formatter(self.session_logger_id, account_id, region_name)
        self.client_token = client_token
        self.display_name = display_name
        self.event_filter = event_filter
        self.log_configuration = log_configuration
        self.associated_portal_arns: list[str] = []

    def arn_formatter(self, _id: str, account_id: str, region_name: str) -> str:
        return f"arn:{get_partition(region_name)}:workspaces-web:{region_name}:{account_id}:session-logger/{_id}"

    def to_dict(self) -> dict[str, Any]:
        return {
            "associatedPortalArns": self.associated_portal_arns,
            "displayName": self.display_name,
            "eventFilter": self.event_filter,
            "logConfiguration": self.log_configuration,
            "sessionLoggerArn": self.arn,
        }


class FakeSession(BaseModel):
    def __init__(
        self,
        portal_id: str,
        username: str,
        session_id: str,
        region_name: str,
        account_id: str,
    ):
        self.session_id = session_id or str(uuid.uuid4())
        self.portal_id = portal_id
        self.username = username
        self.status = "Active"
        self.start_time = datetime.datetime.now().isoformat()
        self.client_ip_addresses: list[str] = []

    def to_dict(self) -> dict[str, Any]:
        return {
            "clientIpAddresses": self.client_ip_addresses,
            "portalId": self.portal_id,
            "sessionId": self.session_id,
            "startTime": self.start_time,
            "status": self.status,
            "username": self.username,
        }


class FakePortal(BaseModel):
    def __init__(
        self,
        additional_encryption_context: Any,
        authentication_type: str,
        client_token: str,
        customer_managed_key: str,
        display_name: str,
        instance_type: str,
        max_concurrent_sessions: str,
        region_name: str,
        account_id: str,
    ):
        self.portal_id = str(uuid.uuid4())
        self.arn = self.arn_formatter(self.portal_id, account_id, region_name)
        self.additional_encryption_context = additional_encryption_context
        self.authentication_type = authentication_type
        self.client_token = client_token
        self.customer_managed_key = customer_managed_key
        self.display_name = display_name
        self.instance_type = instance_type
        self.max_concurrent_sessions = max_concurrent_sessions
        self.portal_endpoint = f"{self.portal_id}.portal.aws"
        self.browser_type = "Chrome"
        self.creation_time = datetime.datetime.now().isoformat()
        self.status = "CREATED"
        self.renderer_type = "AppStream"
        self.status_reason = "TestStatusReason"
        self.browser_settings_arn: Optional[str] = None
        self.network_settings_arn: Optional[str] = None
        self.trust_store_arn: Optional[str] = None
        self.ip_access_settings_arn: Optional[str] = None
        self.user_access_logging_settings_arn: Optional[str] = None
        self.user_settings_arn: Optional[str] = None
        self.data_protection_settings_arn: Optional[str] = None
        self.session_logger_arn: Optional[str] = None
        self.saml_metadata: str = "<EntityDescriptor></EntityDescriptor>"
        self.sign_in_url: str = f"https://{self.portal_id}.portal.aws/login"

    def arn_formatter(self, _id: str, account_id: str, region_name: str) -> str:
        return f"arn:{get_partition(region_name)}:workspaces-web:{region_name}:{account_id}:portal/{_id}"

    def to_dict(self) -> dict[str, Any]:
        return {
            "additionalEncryptionContext": self.additional_encryption_context,
            "authenticationType": self.authentication_type,
            "browserSettingsArn": self.browser_settings_arn,
            "browserType": self.browser_type,
            "creationDate": self.creation_time,
            "customerManagedKey": self.customer_managed_key,
            "dataProtectionSettingsArn": self.data_protection_settings_arn,
            "displayName": self.display_name,
            "instanceType": self.instance_type,
            "ipAccessSettingsArn": self.ip_access_settings_arn,
            "maxConcurrentSessions": self.max_concurrent_sessions,
            "networkSettingsArn": self.network_settings_arn,
            "portalArn": self.arn,
            "portalEndpoint": self.portal_endpoint,
            "portalStatus": self.status,
            "rendererType": self.renderer_type,
            "statusReason": self.status_reason,
            "trustStoreArn": self.trust_store_arn,
            "userAccessLoggingSettingsArn": self.user_access_logging_settings_arn,
            "userSettingsArn": self.user_settings_arn,
        }


class WorkSpacesWebBackend(BaseBackend):
    """Implementation of WorkSpacesWeb APIs."""

    def __init__(self, region_name: str, account_id: str):
        super().__init__(region_name, account_id)
        self.network_settings: dict[str, FakeNetworkSettings] = {}
        self.browser_settings: dict[str, FakeBrowserSettings] = {}
        self.user_settings: dict[str, FakeUserSettings] = {}
        self.user_access_logging_settings: dict[str, FakeUserAccessLoggingSettings] = {}
        self.portals: dict[str, FakePortal] = {}
        self.ip_access_settings: dict[str, FakeIpAccessSettings] = {}
        self.trust_stores: dict[str, FakeTrustStore] = {}
        self.identity_providers: dict[str, FakeIdentityProvider] = {}
        self.data_protection_settings: dict[str, FakeDataProtectionSettings] = {}
        self.session_loggers: dict[str, FakeSessionLogger] = {}
        self.sessions: dict[str, FakeSession] = {}
        self.tagger = TaggingService()

    def create_network_settings(
        self,
        security_group_ids: list[str],
        subnet_ids: list[str],
        tags: dict[str, str],
        vpc_id: str,
    ) -> str:
        network_settings_object = FakeNetworkSettings(
            security_group_ids,
            subnet_ids,
            vpc_id,
            self.region_name,
            self.account_id,
        )
        self.network_settings[network_settings_object.arn] = network_settings_object
        if tags:
            self.tag_resource("TEMP_CLIENT_TOKEN", network_settings_object.arn, tags)
        return network_settings_object.arn

    def list_network_settings(self) -> list[dict[str, str]]:
        return [
            {"networkSettingsArn": network_setting.arn, "vpcId": network_setting.vpc_id}
            for network_setting in self.network_settings.values()
        ]

    def get_network_settings(self, network_settings_arn: str) -> dict[str, Any]:
        if network_settings_arn not in self.network_settings:
            raise ResourceNotFoundException(f"NetworkSettings {network_settings_arn} not found")
        return self.network_settings[network_settings_arn].to_dict()

    def delete_network_settings(self, network_settings_arn: str) -> None:
        self.network_settings.pop(network_settings_arn, None)

    def update_network_settings(
        self,
        network_settings_arn: str,
        security_group_ids: Optional[list[str]],
        subnet_ids: Optional[list[str]],
        vpc_id: Optional[str],
    ) -> dict[str, Any]:
        if network_settings_arn not in self.network_settings:
            raise ResourceNotFoundException(f"NetworkSettings {network_settings_arn} not found")
        obj = self.network_settings[network_settings_arn]
        if security_group_ids is not None:
            obj.security_group_ids = security_group_ids
        if subnet_ids is not None:
            obj.subnet_ids = subnet_ids
        if vpc_id is not None:
            obj.vpc_id = vpc_id
        return obj.to_dict()

    def create_browser_settings(
        self,
        additional_encryption_context: Any,
        browser_policy: str,
        client_token: str,
        customer_managed_key: str,
        tags: Optional[list[dict[str, str]]] = None,
    ) -> str:
        browser_settings_object = FakeBrowserSettings(
            additional_encryption_context,
            browser_policy,
            client_token,
            customer_managed_key,
            self.region_name,
            self.account_id,
        )
        self.browser_settings[browser_settings_object.arn] = browser_settings_object
        if tags:
            self.tag_resource(client_token, browser_settings_object.arn, tags)
        return browser_settings_object.arn

    def list_browser_settings(self) -> list[dict[str, str]]:
        return [
            {"browserSettingsArn": browser_setting.arn}
            for browser_setting in self.browser_settings.values()
        ]

    def get_browser_settings(self, browser_settings_arn: str) -> dict[str, Any]:
        if browser_settings_arn not in self.browser_settings:
            raise ResourceNotFoundException(f"BrowserSettings {browser_settings_arn} not found")
        return self.browser_settings[browser_settings_arn].to_dict()

    def delete_browser_settings(self, browser_settings_arn: str) -> None:
        self.browser_settings.pop(browser_settings_arn, None)

    def update_browser_settings(
        self,
        browser_settings_arn: str,
        browser_policy: Optional[str],
    ) -> dict[str, Any]:
        if browser_settings_arn not in self.browser_settings:
            raise ResourceNotFoundException(f"BrowserSettings {browser_settings_arn} not found")
        obj = self.browser_settings[browser_settings_arn]
        if browser_policy is not None:
            obj.browser_policy = browser_policy
        return obj.to_dict()

    def create_portal(
        self,
        additional_encryption_context: Any,
        authentication_type: str,
        client_token: str,
        customer_managed_key: str,
        display_name: str,
        instance_type: str,
        max_concurrent_sessions: str,
        tags: Optional[list[dict[str, str]]] = None,
    ) -> tuple[str, str]:
        portal_object = FakePortal(
            additional_encryption_context,
            authentication_type,
            client_token,
            customer_managed_key,
            display_name,
            instance_type,
            max_concurrent_sessions,
            self.region_name,
            self.account_id,
        )
        self.portals[portal_object.arn] = portal_object
        if tags:
            self.tag_resource(client_token, portal_object.arn, tags)
        return portal_object.arn, portal_object.portal_endpoint

    def list_portals(self) -> list[dict[str, Any]]:
        return [
            {
                "authenticationType": portal.authentication_type,
                "browserSettingsArn": portal.browser_settings_arn,
                "browserType": portal.browser_type,
                "creationDate": portal.creation_time,
                "customerManagedKey": portal.customer_managed_key,
                "displayName": portal.display_name,
                "instanceType": portal.instance_type,
                "ipAccessSettingsArn": portal.ip_access_settings_arn,
                "maxConcurrentSessions": portal.max_concurrent_sessions,
                "networkSettingsArn": portal.network_settings_arn,
                "portalArn": portal.arn,
                "portalEndpoint": portal.portal_endpoint,
                "portalStatus": portal.status,
                "rendererType": portal.renderer_type,
                "statusReason": portal.status_reason,
                "trustStoreArn": portal.trust_store_arn,
                "userAccessLoggingSettingsArn": portal.user_access_logging_settings_arn,
                "userSettingsArn": portal.user_settings_arn,
            }
            for portal in self.portals.values()
        ]

    def get_portal(self, portal_arn: str) -> dict[str, Any]:
        if portal_arn not in self.portals:
            raise ResourceNotFoundException(f"Portal {portal_arn} not found")
        return self.portals[portal_arn].to_dict()

    def delete_portal(self, portal_arn: str) -> None:
        self.portals.pop(portal_arn, None)

    def update_portal(
        self,
        portal_arn: str,
        authentication_type: Optional[str],
        display_name: Optional[str],
        instance_type: Optional[str],
        max_concurrent_sessions: Optional[int],
    ) -> dict[str, Any]:
        if portal_arn not in self.portals:
            raise ResourceNotFoundException(f"Portal {portal_arn} not found")
        obj = self.portals[portal_arn]
        if authentication_type is not None:
            obj.authentication_type = authentication_type
        if display_name is not None:
            obj.display_name = display_name
        if instance_type is not None:
            obj.instance_type = instance_type
        if max_concurrent_sessions is not None:
            obj.max_concurrent_sessions = max_concurrent_sessions
        return obj.to_dict()

    def get_portal_service_provider_metadata(self, portal_arn: str) -> dict[str, Any]:
        if portal_arn not in self.portals:
            raise ResourceNotFoundException(f"Portal {portal_arn} not found")
        portal = self.portals[portal_arn]
        return {
            "portalArn": portal.arn,
            "serviceProviderSamlMetadata": portal.saml_metadata,
        }

    def associate_browser_settings(
        self, browser_settings_arn: str, portal_arn: str
    ) -> tuple[str, str]:
        browser_settings_object = self.browser_settings[browser_settings_arn]
        portal_object = self.portals[portal_arn]
        browser_settings_object.associated_portal_arns.append(portal_arn)
        portal_object.browser_settings_arn = browser_settings_arn
        return browser_settings_arn, portal_arn

    def disassociate_browser_settings(self, portal_arn: str) -> None:
        if portal_arn not in self.portals:
            raise ResourceNotFoundException(f"Portal {portal_arn} not found")
        portal = self.portals[portal_arn]
        if portal.browser_settings_arn:
            bsa = portal.browser_settings_arn
            portal.browser_settings_arn = None
            if bsa in self.browser_settings:
                bs = self.browser_settings[bsa]
                if portal_arn in bs.associated_portal_arns:
                    bs.associated_portal_arns.remove(portal_arn)

    def associate_network_settings(
        self, network_settings_arn: str, portal_arn: str
    ) -> tuple[str, str]:
        network_settings_object = self.network_settings[network_settings_arn]
        portal_object = self.portals[portal_arn]
        network_settings_object.associated_portal_arns.append(portal_arn)
        portal_object.network_settings_arn = network_settings_arn
        return network_settings_arn, portal_arn

    def disassociate_network_settings(self, portal_arn: str) -> None:
        if portal_arn not in self.portals:
            raise ResourceNotFoundException(f"Portal {portal_arn} not found")
        portal = self.portals[portal_arn]
        if portal.network_settings_arn:
            nsa = portal.network_settings_arn
            portal.network_settings_arn = None
            if nsa in self.network_settings:
                ns = self.network_settings[nsa]
                if portal_arn in ns.associated_portal_arns:
                    ns.associated_portal_arns.remove(portal_arn)

    def create_user_settings(
        self,
        additional_encryption_context: Any,
        client_token: Any,
        cookie_synchronization_configuration: Any,
        copy_allowed: Any,
        customer_managed_key: Any,
        deep_link_allowed: Any,
        disconnect_timeout_in_minutes: Any,
        download_allowed: Any,
        idle_disconnect_timeout_in_minutes: Any,
        paste_allowed: Any,
        print_allowed: Any,
        tags: Any,
        upload_allowed: Any,
    ) -> str:
        user_settings_object = FakeUserSettings(
            additional_encryption_context,
            client_token,
            cookie_synchronization_configuration,
            copy_allowed,
            customer_managed_key,
            deep_link_allowed,
            disconnect_timeout_in_minutes,
            download_allowed,
            idle_disconnect_timeout_in_minutes,
            paste_allowed,
            print_allowed,
            upload_allowed,
            self.region_name,
            self.account_id,
        )
        self.user_settings[user_settings_object.arn] = user_settings_object
        if tags:
            self.tag_resource(client_token, user_settings_object.arn, tags)
        return user_settings_object.arn

    def get_user_settings(self, user_settings_arn: str) -> dict[str, Any]:
        if user_settings_arn not in self.user_settings:
            raise ResourceNotFoundException(f"UserSettings {user_settings_arn} not found")
        return self.user_settings[user_settings_arn].to_dict()

    def delete_user_settings(self, user_settings_arn: str) -> None:
        self.user_settings.pop(user_settings_arn, None)

    def update_user_settings(
        self,
        user_settings_arn: str,
        copy_allowed: Optional[str],
        download_allowed: Optional[str],
        paste_allowed: Optional[str],
        print_allowed: Optional[str],
        upload_allowed: Optional[str],
        disconnect_timeout_in_minutes: Optional[int],
        idle_disconnect_timeout_in_minutes: Optional[int],
        deep_link_allowed: Optional[str],
        cookie_synchronization_configuration: Optional[Any],
    ) -> dict[str, Any]:
        if user_settings_arn not in self.user_settings:
            raise ResourceNotFoundException(f"UserSettings {user_settings_arn} not found")
        obj = self.user_settings[user_settings_arn]
        if copy_allowed is not None:
            obj.copy_allowed = copy_allowed
        if download_allowed is not None:
            obj.download_allowed = download_allowed
        if paste_allowed is not None:
            obj.paste_allowed = paste_allowed
        if print_allowed is not None:
            obj.print_allowed = print_allowed
        if upload_allowed is not None:
            obj.upload_allowed = upload_allowed
        if disconnect_timeout_in_minutes is not None:
            obj.disconnect_timeout_in_minutes = disconnect_timeout_in_minutes
        if idle_disconnect_timeout_in_minutes is not None:
            obj.idle_disconnect_timeout_in_minutes = idle_disconnect_timeout_in_minutes
        if deep_link_allowed is not None:
            obj.deep_link_allowed = deep_link_allowed
        if cookie_synchronization_configuration is not None:
            obj.cookie_synchronization_configuration = cookie_synchronization_configuration
        return obj.to_dict()

    def create_user_access_logging_settings(
        self, client_token: Any, kinesis_stream_arn: Any, tags: Any
    ) -> str:
        user_access_logging_settings_object = FakeUserAccessLoggingSettings(
            client_token, kinesis_stream_arn, self.region_name, self.account_id
        )
        self.user_access_logging_settings[user_access_logging_settings_object.arn] = (
            user_access_logging_settings_object
        )
        if tags:
            self.tag_resource(
                client_token, user_access_logging_settings_object.arn, tags
            )
        return user_access_logging_settings_object.arn

    def get_user_access_logging_settings(
        self, user_access_logging_settings_arn: str
    ) -> dict[str, Any]:
        if user_access_logging_settings_arn not in self.user_access_logging_settings:
            raise ResourceNotFoundException(f"UserAccessLoggingSettings {user_access_logging_settings_arn} not found")
        return self.user_access_logging_settings[
            user_access_logging_settings_arn
        ].to_dict()

    def delete_user_access_logging_settings(
        self, user_access_logging_settings_arn: str
    ) -> None:
        self.user_access_logging_settings.pop(user_access_logging_settings_arn, None)

    def update_user_access_logging_settings(
        self,
        user_access_logging_settings_arn: str,
        kinesis_stream_arn: Optional[str],
    ) -> dict[str, Any]:
        if user_access_logging_settings_arn not in self.user_access_logging_settings:
            raise ResourceNotFoundException(f"UserAccessLoggingSettings {user_access_logging_settings_arn} not found")
        obj = self.user_access_logging_settings[user_access_logging_settings_arn]
        if kinesis_stream_arn is not None:
            obj.kinesis_stream_arn = kinesis_stream_arn
        return obj.to_dict()

    def associate_user_settings(
        self, portal_arn: str, user_settings_arn: str
    ) -> tuple[str, str]:
        user_settings_object = self.user_settings[user_settings_arn]
        portal_object = self.portals[portal_arn]
        user_settings_object.associated_portal_arns.append(portal_arn)
        portal_object.user_settings_arn = user_settings_arn
        return portal_arn, user_settings_arn

    def disassociate_user_settings(self, portal_arn: str) -> None:
        if portal_arn not in self.portals:
            raise ResourceNotFoundException(f"Portal {portal_arn} not found")
        portal = self.portals[portal_arn]
        if portal.user_settings_arn:
            usa = portal.user_settings_arn
            portal.user_settings_arn = None
            if usa in self.user_settings:
                us = self.user_settings[usa]
                if portal_arn in us.associated_portal_arns:
                    us.associated_portal_arns.remove(portal_arn)

    def associate_user_access_logging_settings(
        self, portal_arn: str, user_access_logging_settings_arn: str
    ) -> tuple[str, str]:
        user_access_logging_settings_object = self.user_access_logging_settings[
            user_access_logging_settings_arn
        ]
        portal_object = self.portals[portal_arn]
        user_access_logging_settings_object.associated_portal_arns.append(portal_arn)
        portal_object.user_access_logging_settings_arn = (
            user_access_logging_settings_arn
        )
        return portal_arn, user_access_logging_settings_arn

    def disassociate_user_access_logging_settings(self, portal_arn: str) -> None:
        if portal_arn not in self.portals:
            raise ResourceNotFoundException(f"Portal {portal_arn} not found")
        portal = self.portals[portal_arn]
        if portal.user_access_logging_settings_arn:
            uala = portal.user_access_logging_settings_arn
            portal.user_access_logging_settings_arn = None
            if uala in self.user_access_logging_settings:
                uals = self.user_access_logging_settings[uala]
                if portal_arn in uals.associated_portal_arns:
                    uals.associated_portal_arns.remove(portal_arn)

    def list_user_settings(self) -> list[dict[str, str]]:
        return [
            {"userSettingsArn": user_settings.arn}
            for user_settings in self.user_settings.values()
        ]

    def list_user_access_logging_settings(self) -> list[dict[str, str]]:
        return [
            {"userAccessLoggingSettingsArn": user_access_logging_settings.arn}
            for user_access_logging_settings in self.user_access_logging_settings.values()
        ]

    # IpAccessSettings
    def create_ip_access_settings(
        self,
        additional_encryption_context: Any,
        client_token: str,
        customer_managed_key: str,
        description: str,
        display_name: str,
        ip_rules: list[dict[str, Any]],
        tags: Any,
    ) -> str:
        obj = FakeIpAccessSettings(
            additional_encryption_context,
            client_token,
            customer_managed_key,
            description,
            display_name,
            ip_rules,
            tags,
            self.region_name,
            self.account_id,
        )
        self.ip_access_settings[obj.arn] = obj
        if tags:
            self.tag_resource(client_token or "token", obj.arn, tags)
        return obj.arn

    def list_ip_access_settings(self) -> list[dict[str, Any]]:
        return [
            {
                "ipAccessSettingsArn": obj.arn,
                "displayName": obj.display_name,
                "description": obj.description,
                "creationDate": obj.creation_date,
            }
            for obj in self.ip_access_settings.values()
        ]

    def get_ip_access_settings(self, ip_access_settings_arn: str) -> dict[str, Any]:
        if ip_access_settings_arn not in self.ip_access_settings:
            raise ResourceNotFoundException(f"IpAccessSettings {ip_access_settings_arn} not found")
        return self.ip_access_settings[ip_access_settings_arn].to_dict()

    def update_ip_access_settings(
        self,
        ip_access_settings_arn: str,
        description: Optional[str],
        display_name: Optional[str],
        ip_rules: Optional[list[dict[str, Any]]],
    ) -> dict[str, Any]:
        if ip_access_settings_arn not in self.ip_access_settings:
            raise ResourceNotFoundException(f"IpAccessSettings {ip_access_settings_arn} not found")
        obj = self.ip_access_settings[ip_access_settings_arn]
        if description is not None:
            obj.description = description
        if display_name is not None:
            obj.display_name = display_name
        if ip_rules is not None:
            obj.ip_rules = ip_rules
        return obj.to_dict()

    def delete_ip_access_settings(self, ip_access_settings_arn: str) -> None:
        self.ip_access_settings.pop(ip_access_settings_arn, None)

    def associate_ip_access_settings(
        self, portal_arn: str, ip_access_settings_arn: str
    ) -> tuple[str, str]:
        if portal_arn not in self.portals:
            raise ResourceNotFoundException(f"Portal {portal_arn} not found")
        if ip_access_settings_arn not in self.ip_access_settings:
            raise ResourceNotFoundException(f"IpAccessSettings {ip_access_settings_arn} not found")
        portal = self.portals[portal_arn]
        obj = self.ip_access_settings[ip_access_settings_arn]
        portal.ip_access_settings_arn = ip_access_settings_arn
        if portal_arn not in obj.associated_portal_arns:
            obj.associated_portal_arns.append(portal_arn)
        return ip_access_settings_arn, portal_arn

    def disassociate_ip_access_settings(self, portal_arn: str) -> None:
        if portal_arn not in self.portals:
            raise ResourceNotFoundException(f"Portal {portal_arn} not found")
        portal = self.portals[portal_arn]
        if portal.ip_access_settings_arn:
            iasa = portal.ip_access_settings_arn
            portal.ip_access_settings_arn = None
            if iasa in self.ip_access_settings:
                ias = self.ip_access_settings[iasa]
                if portal_arn in ias.associated_portal_arns:
                    ias.associated_portal_arns.remove(portal_arn)

    # TrustStore
    def create_trust_store(
        self,
        certificate_list: list[str],
        client_token: str,
        tags: Any,
    ) -> str:
        obj = FakeTrustStore(
            certificate_list,
            client_token,
            tags,
            self.region_name,
            self.account_id,
        )
        self.trust_stores[obj.arn] = obj
        if tags:
            self.tag_resource(client_token or "token", obj.arn, tags)
        return obj.arn

    def list_trust_stores(self) -> list[dict[str, Any]]:
        return [{"trustStoreArn": obj.arn} for obj in self.trust_stores.values()]

    def get_trust_store(self, trust_store_arn: str) -> dict[str, Any]:
        if trust_store_arn not in self.trust_stores:
            raise ResourceNotFoundException(f"TrustStore {trust_store_arn} not found")
        return self.trust_stores[trust_store_arn].to_dict()

    def update_trust_store(
        self,
        trust_store_arn: str,
        certificates_to_add: Optional[list[str]],
        certificates_to_delete: Optional[list[str]],
    ) -> str:
        if trust_store_arn not in self.trust_stores:
            raise ResourceNotFoundException(f"TrustStore {trust_store_arn} not found")
        obj = self.trust_stores[trust_store_arn]
        if certificates_to_add:
            obj.certificate_list.extend(certificates_to_add)
        if certificates_to_delete:
            obj.certificate_list = [c for c in obj.certificate_list if c not in certificates_to_delete]
        return trust_store_arn

    def delete_trust_store(self, trust_store_arn: str) -> None:
        self.trust_stores.pop(trust_store_arn, None)

    def get_trust_store_certificate(self, trust_store_arn: str, thumbprint: str) -> dict[str, Any]:
        if trust_store_arn not in self.trust_stores:
            raise ResourceNotFoundException(f"TrustStore {trust_store_arn} not found")
        return {
            "certificate": {
                "thumbprint": thumbprint,
                "body": "",
                "issuer": "CN=Example",
                "notValidAfter": "2030-01-01T00:00:00Z",
                "notValidBefore": "2020-01-01T00:00:00Z",
                "subject": "CN=Example",
            },
            "trustStoreArn": trust_store_arn,
        }

    def list_trust_store_certificates(self, trust_store_arn: str) -> list[dict[str, Any]]:
        if trust_store_arn not in self.trust_stores:
            raise ResourceNotFoundException(f"TrustStore {trust_store_arn} not found")
        return [
            {"thumbprint": f"thumb-{i}", "trustStoreArn": trust_store_arn}
            for i in range(len(self.trust_stores[trust_store_arn].certificate_list))
        ]

    def associate_trust_store(
        self, portal_arn: str, trust_store_arn: str
    ) -> tuple[str, str]:
        if portal_arn not in self.portals:
            raise ResourceNotFoundException(f"Portal {portal_arn} not found")
        if trust_store_arn not in self.trust_stores:
            raise ResourceNotFoundException(f"TrustStore {trust_store_arn} not found")
        portal = self.portals[portal_arn]
        obj = self.trust_stores[trust_store_arn]
        portal.trust_store_arn = trust_store_arn
        if portal_arn not in obj.associated_portal_arns:
            obj.associated_portal_arns.append(portal_arn)
        return portal_arn, trust_store_arn

    def disassociate_trust_store(self, portal_arn: str) -> None:
        if portal_arn not in self.portals:
            raise ResourceNotFoundException(f"Portal {portal_arn} not found")
        portal = self.portals[portal_arn]
        if portal.trust_store_arn:
            tsa = portal.trust_store_arn
            portal.trust_store_arn = None
            if tsa in self.trust_stores:
                ts = self.trust_stores[tsa]
                if portal_arn in ts.associated_portal_arns:
                    ts.associated_portal_arns.remove(portal_arn)

    # IdentityProvider
    def create_identity_provider(
        self,
        portal_arn: str,
        identity_provider_details: dict[str, str],
        identity_provider_name: str,
        identity_provider_type: str,
        client_token: str,
        tags: Any,
    ) -> str:
        obj = FakeIdentityProvider(
            portal_arn,
            identity_provider_details,
            identity_provider_name,
            identity_provider_type,
            client_token,
            self.region_name,
            self.account_id,
        )
        self.identity_providers[obj.arn] = obj
        return obj.arn

    def list_identity_providers(self, portal_arn: str) -> list[dict[str, Any]]:
        return [
            obj.to_dict()
            for obj in self.identity_providers.values()
            if obj.portal_arn == portal_arn
        ]

    def get_identity_provider(self, identity_provider_arn: str) -> dict[str, Any]:
        if identity_provider_arn not in self.identity_providers:
            raise ResourceNotFoundException(f"IdentityProvider {identity_provider_arn} not found")
        return self.identity_providers[identity_provider_arn].to_dict()

    def update_identity_provider(
        self,
        identity_provider_arn: str,
        identity_provider_details: Optional[dict[str, str]],
        identity_provider_name: Optional[str],
        identity_provider_type: Optional[str],
    ) -> dict[str, Any]:
        if identity_provider_arn not in self.identity_providers:
            raise ResourceNotFoundException(f"IdentityProvider {identity_provider_arn} not found")
        obj = self.identity_providers[identity_provider_arn]
        if identity_provider_details is not None:
            obj.identity_provider_details = identity_provider_details
        if identity_provider_name is not None:
            obj.identity_provider_name = identity_provider_name
        if identity_provider_type is not None:
            obj.identity_provider_type = identity_provider_type
        return obj.to_dict()

    def delete_identity_provider(self, identity_provider_arn: str) -> None:
        self.identity_providers.pop(identity_provider_arn, None)

    # DataProtectionSettings
    def create_data_protection_settings(
        self,
        additional_encryption_context: Any,
        client_token: str,
        customer_managed_key: str,
        description: str,
        display_name: str,
        inline_redaction_configuration: Any,
        tags: Any,
    ) -> str:
        obj = FakeDataProtectionSettings(
            additional_encryption_context,
            client_token,
            customer_managed_key,
            description,
            display_name,
            inline_redaction_configuration,
            tags,
            self.region_name,
            self.account_id,
        )
        self.data_protection_settings[obj.arn] = obj
        if tags:
            self.tag_resource(client_token or "token", obj.arn, tags)
        return obj.arn

    def list_data_protection_settings(self) -> list[dict[str, Any]]:
        return [
            {
                "dataProtectionSettingsArn": obj.arn,
                "displayName": obj.display_name,
                "description": obj.description,
                "creationDate": obj.creation_date,
            }
            for obj in self.data_protection_settings.values()
        ]

    def get_data_protection_settings(self, data_protection_settings_arn: str) -> dict[str, Any]:
        if data_protection_settings_arn not in self.data_protection_settings:
            raise ResourceNotFoundException(f"DataProtectionSettings {data_protection_settings_arn} not found")
        return self.data_protection_settings[data_protection_settings_arn].to_dict()

    def update_data_protection_settings(
        self,
        data_protection_settings_arn: str,
        description: Optional[str],
        display_name: Optional[str],
        inline_redaction_configuration: Optional[Any],
    ) -> dict[str, Any]:
        if data_protection_settings_arn not in self.data_protection_settings:
            raise ResourceNotFoundException(f"DataProtectionSettings {data_protection_settings_arn} not found")
        obj = self.data_protection_settings[data_protection_settings_arn]
        if description is not None:
            obj.description = description
        if display_name is not None:
            obj.display_name = display_name
        if inline_redaction_configuration is not None:
            obj.inline_redaction_configuration = inline_redaction_configuration
        return obj.to_dict()

    def delete_data_protection_settings(self, data_protection_settings_arn: str) -> None:
        self.data_protection_settings.pop(data_protection_settings_arn, None)

    def associate_data_protection_settings(
        self, portal_arn: str, data_protection_settings_arn: str
    ) -> tuple[str, str]:
        if portal_arn not in self.portals:
            raise ResourceNotFoundException(f"Portal {portal_arn} not found")
        if data_protection_settings_arn not in self.data_protection_settings:
            raise ResourceNotFoundException(f"DataProtectionSettings {data_protection_settings_arn} not found")
        portal = self.portals[portal_arn]
        obj = self.data_protection_settings[data_protection_settings_arn]
        portal.data_protection_settings_arn = data_protection_settings_arn
        if portal_arn not in obj.associated_portal_arns:
            obj.associated_portal_arns.append(portal_arn)
        return data_protection_settings_arn, portal_arn

    def disassociate_data_protection_settings(self, portal_arn: str) -> None:
        if portal_arn not in self.portals:
            raise ResourceNotFoundException(f"Portal {portal_arn} not found")
        portal = self.portals[portal_arn]
        if portal.data_protection_settings_arn:
            dpsa = portal.data_protection_settings_arn
            portal.data_protection_settings_arn = None
            if dpsa in self.data_protection_settings:
                dps = self.data_protection_settings[dpsa]
                if portal_arn in dps.associated_portal_arns:
                    dps.associated_portal_arns.remove(portal_arn)

    # SessionLogger
    def create_session_logger(
        self,
        client_token: str,
        display_name: str,
        event_filter: Any,
        log_configuration: Any,
        tags: Any,
    ) -> str:
        obj = FakeSessionLogger(
            client_token,
            display_name,
            event_filter,
            log_configuration,
            tags,
            self.region_name,
            self.account_id,
        )
        self.session_loggers[obj.arn] = obj
        if tags:
            self.tag_resource(client_token or "token", obj.arn, tags)
        return obj.arn

    def list_session_loggers(self) -> list[dict[str, Any]]:
        return [
            {
                "sessionLoggerArn": obj.arn,
                "displayName": obj.display_name,
                "logConfiguration": obj.log_configuration,
            }
            for obj in self.session_loggers.values()
        ]

    def get_session_logger(self, session_logger_arn: str) -> dict[str, Any]:
        if session_logger_arn not in self.session_loggers:
            raise ResourceNotFoundException(f"SessionLogger {session_logger_arn} not found")
        return self.session_loggers[session_logger_arn].to_dict()

    def update_session_logger(
        self,
        session_logger_arn: str,
        display_name: Optional[str],
        event_filter: Optional[Any],
        log_configuration: Optional[Any],
    ) -> dict[str, Any]:
        if session_logger_arn not in self.session_loggers:
            raise ResourceNotFoundException(f"SessionLogger {session_logger_arn} not found")
        obj = self.session_loggers[session_logger_arn]
        if display_name is not None:
            obj.display_name = display_name
        if event_filter is not None:
            obj.event_filter = event_filter
        if log_configuration is not None:
            obj.log_configuration = log_configuration
        return obj.to_dict()

    def delete_session_logger(self, session_logger_arn: str) -> None:
        self.session_loggers.pop(session_logger_arn, None)

    def associate_session_logger(
        self, portal_arn: str, session_logger_arn: str
    ) -> tuple[str, str]:
        if portal_arn not in self.portals:
            raise ResourceNotFoundException(f"Portal {portal_arn} not found")
        if session_logger_arn not in self.session_loggers:
            raise ResourceNotFoundException(f"SessionLogger {session_logger_arn} not found")
        portal = self.portals[portal_arn]
        obj = self.session_loggers[session_logger_arn]
        portal.session_logger_arn = session_logger_arn
        if portal_arn not in obj.associated_portal_arns:
            obj.associated_portal_arns.append(portal_arn)
        return portal_arn, session_logger_arn

    def disassociate_session_logger(self, portal_arn: str) -> None:
        if portal_arn not in self.portals:
            raise ResourceNotFoundException(f"Portal {portal_arn} not found")
        portal = self.portals[portal_arn]
        if portal.session_logger_arn:
            sla = portal.session_logger_arn
            portal.session_logger_arn = None
            if sla in self.session_loggers:
                sl = self.session_loggers[sla]
                if portal_arn in sl.associated_portal_arns:
                    sl.associated_portal_arns.remove(portal_arn)

    # Sessions
    def list_sessions(self, portal_id: str) -> list[dict[str, Any]]:
        return [
            s.to_dict()
            for s in self.sessions.values()
            if s.portal_id == portal_id
        ]

    def get_session(self, portal_id: str, session_id: str) -> dict[str, Any]:
        key = f"{portal_id}/{session_id}"
        if key not in self.sessions:
            raise ResourceNotFoundException(f"Session {session_id} not found")
        return self.sessions[key].to_dict()

    def expire_session(self, portal_id: str, session_id: str) -> None:
        key = f"{portal_id}/{session_id}"
        if key in self.sessions:
            self.sessions[key].status = "Expired"

    # Tags
    def tag_resource(self, client_token: str, resource_arn: str, tags: Any) -> None:
        self.tagger.tag_resource(resource_arn, tags)

    def untag_resource(self, resource_arn: str, tag_keys: Any) -> None:
        self.tagger.untag_resource_using_names(resource_arn, tag_keys)

    def list_tags_for_resource(self, resource_arn: str) -> list[dict[str, str]]:
        tags = self.tagger.get_tag_dict_for_resource(resource_arn)
        Tags = []
        for key, value in tags.items():
            Tags.append({"Key": key, "Value": value})
        return Tags


workspacesweb_backends = BackendDict(WorkSpacesWebBackend, "workspaces-web")
