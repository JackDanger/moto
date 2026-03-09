"""ConnectBackend class with methods for supported APIs."""

import hashlib
import uuid
from datetime import datetime, timezone
from typing import Any, Optional

from moto.core.base_backend import BackendDict, BaseBackend
from moto.core.common_models import BaseModel
from moto.utilities.paginator import paginate
from moto.utilities.tagging_service import TaggingService

from .exceptions import InvalidParameterException, ResourceNotFoundException

PAGINATION_MODEL = {
    "list_analytics_data_associations": {
        "input_token": "next_token",
        "limit_key": "max_results",
        "limit_default": 1000,
        "unique_attribute": "DataSetId",
        "output_token": "next_token",
    },
    "list_instances": {
        "input_token": "next_token",
        "limit_key": "max_results",
        "limit_default": 10,
        "unique_attribute": "Id",
        "output_token": "next_token",
    },
}


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class Instance(BaseModel):
    def __init__(
        self,
        identity_management_type: str,
        inbound_calls_enabled: bool,
        outbound_calls_enabled: bool,
        account_id: str,
        region: str,
        instance_alias: Optional[str] = None,
        tags: Optional[dict[str, str]] = None,
    ) -> None:
        self.id = str(uuid.uuid4())
        self.arn = f"arn:aws:connect:{region}:{account_id}:instance/{self.id}"
        self.identity_management_type = identity_management_type
        self.instance_alias = instance_alias
        self.created_time = datetime.now(timezone.utc)
        self.service_role = f"arn:aws:iam::{account_id}:role/aws-service-role/connect.amazonaws.com/AWSServiceRoleForAmazonConnect"
        self.instance_status = "ACTIVE"
        self.inbound_calls_enabled = inbound_calls_enabled
        self.outbound_calls_enabled = outbound_calls_enabled
        self.instance_access_url = f"https://{instance_alias or self.id}.my.connect.aws"
        self.tags = tags or {}
        # Instance attributes storage
        self.attributes: dict[str, str] = {
            "INBOUND_CALLS": str(inbound_calls_enabled).lower(),
            "OUTBOUND_CALLS": str(outbound_calls_enabled).lower(),
            "CONTACTFLOW_LOGS": "false",
            "CONTACT_LENS": "true",
            "AUTO_RESOLVE_BEST_VOICES": "true",
            "USE_CUSTOM_TTS_VOICES": "false",
            "EARLY_MEDIA": "true",
            "MULTI_PARTY_CONFERENCE": "false",
            "MULTI_PARTY_CHAT_CONFERENCE": "false",
            "HIGH_VOLUME_OUTBOUND": "false",
            "ENHANCED_CONTACT_MONITORING": "false",
            "ENHANCED_CHAT_MONITORING": "false",
        }

    def to_dict(self) -> dict[str, Any]:
        """Return full instance details for DescribeInstance."""
        result: dict[str, Any] = {
            "Id": self.id,
            "Arn": self.arn,
            "IdentityManagementType": self.identity_management_type,
            "CreatedTime": self.created_time.isoformat(),
            "ServiceRole": self.service_role,
            "InstanceStatus": self.instance_status,
            "InboundCallsEnabled": self.inbound_calls_enabled,
            "OutboundCallsEnabled": self.outbound_calls_enabled,
            "InstanceAccessUrl": self.instance_access_url,
        }
        if self.instance_alias:
            result["InstanceAlias"] = self.instance_alias
        if self.tags:
            result["Tags"] = self.tags
        return result

    def to_summary_dict(self) -> dict[str, Any]:
        """Return summary for ListInstances."""
        result: dict[str, Any] = {
            "Id": self.id,
            "Arn": self.arn,
            "IdentityManagementType": self.identity_management_type,
            "CreatedTime": self.created_time.isoformat(),
            "ServiceRole": self.service_role,
            "InstanceStatus": self.instance_status,
            "InboundCallsEnabled": self.inbound_calls_enabled,
            "OutboundCallsEnabled": self.outbound_calls_enabled,
            "InstanceAccessUrl": self.instance_access_url,
        }
        if self.instance_alias:
            result["InstanceAlias"] = self.instance_alias
        return result


class AnalyticsDataAssociation(BaseModel):
    """Represents an analytics data association for a Connect instance."""

    def __init__(
        self,
        instance_id: str,
        data_set_id: str,
        target_account_id: str,
        source_account_id: str,
        region: str,
    ) -> None:
        self.instance_id = instance_id
        self.data_set_id = data_set_id
        self.target_account_id = target_account_id
        self.resource_share_id = str(uuid.uuid4())
        self.resource_share_arn = f"arn:aws:ram:{region}:{source_account_id}:resource-share/{self.resource_share_id}"
        self.resource_share_status = "ACTIVE"

    def to_dict(self) -> dict[str, str]:
        return {
            "DataSetId": self.data_set_id,
            "TargetAccountId": self.target_account_id,
            "ResourceShareId": self.resource_share_id,
            "ResourceShareArn": self.resource_share_arn,
            "ResourceShareStatus": self.resource_share_status,
        }


class AgentStatus(BaseModel):
    def __init__(
        self,
        instance_arn: str,
        name: str,
        state: str,
        description: str = "",
        display_order: Optional[int] = None,
        tags: Optional[dict[str, str]] = None,
    ) -> None:
        self.agent_status_id = str(uuid.uuid4())
        self.arn = f"{instance_arn}/agent-status/{self.agent_status_id}"
        self.name = name
        self.description = description
        self.type = "CUSTOM"
        self.display_order = display_order
        self.state = state
        self.tags = tags or {}
        self.last_modified_time = _now_iso()
        self.last_modified_region = instance_arn.split(":")[3]

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {
            "AgentStatusARN": self.arn,
            "AgentStatusId": self.agent_status_id,
            "Name": self.name,
            "Description": self.description,
            "Type": self.type,
            "State": self.state,
            "Tags": self.tags,
            "LastModifiedTime": self.last_modified_time,
            "LastModifiedRegion": self.last_modified_region,
        }
        if self.display_order is not None:
            result["DisplayOrder"] = self.display_order
        return result


class ContactFlow(BaseModel):
    def __init__(
        self,
        instance_arn: str,
        name: str,
        flow_type: str,
        content: str,
        description: str = "",
        status: str = "PUBLISHED",
        tags: Optional[dict[str, str]] = None,
    ) -> None:
        self.id = str(uuid.uuid4())
        self.arn = f"{instance_arn}/contact-flow/{self.id}"
        self.name = name
        self.type = flow_type
        self.state = "ACTIVE"
        self.status = status
        self.description = description
        self.content = content
        self.tags = tags or {}
        self.flow_content_sha256 = hashlib.sha256(content.encode()).hexdigest()

    def to_dict(self) -> dict[str, Any]:
        return {
            "Arn": self.arn,
            "Id": self.id,
            "Name": self.name,
            "Type": self.type,
            "State": self.state,
            "Status": self.status,
            "Description": self.description,
            "Content": self.content,
            "Tags": self.tags,
            "FlowContentSha256": self.flow_content_sha256,
        }


class ContactFlowModule(BaseModel):
    def __init__(
        self,
        instance_arn: str,
        name: str,
        content: str,
        description: str = "",
        tags: Optional[dict[str, str]] = None,
    ) -> None:
        self.id = str(uuid.uuid4())
        self.arn = f"{instance_arn}/flow-module/{self.id}"
        self.name = name
        self.content = content
        self.description = description
        self.state = "ACTIVE"
        self.status = "PUBLISHED"
        self.tags = tags or {}
        self.flow_module_content_sha256 = hashlib.sha256(content.encode()).hexdigest()

    def to_dict(self) -> dict[str, Any]:
        return {
            "Arn": self.arn,
            "Id": self.id,
            "Name": self.name,
            "Content": self.content,
            "Description": self.description,
            "State": self.state,
            "Status": self.status,
            "Tags": self.tags,
            "FlowModuleContentSha256": self.flow_module_content_sha256,
        }


class HoursOfOperation(BaseModel):
    def __init__(
        self,
        instance_arn: str,
        name: str,
        time_zone: str,
        config: list[dict[str, Any]],
        description: str = "",
        tags: Optional[dict[str, str]] = None,
    ) -> None:
        self.hours_of_operation_id = str(uuid.uuid4())
        self.arn = f"{instance_arn}/operating-hours/{self.hours_of_operation_id}"
        self.name = name
        self.description = description
        self.time_zone = time_zone
        self.config = config
        self.tags = tags or {}
        self.last_modified_time = _now_iso()
        self.last_modified_region = instance_arn.split(":")[3]

    def to_dict(self) -> dict[str, Any]:
        return {
            "HoursOfOperationId": self.hours_of_operation_id,
            "HoursOfOperationArn": self.arn,
            "Name": self.name,
            "Description": self.description,
            "TimeZone": self.time_zone,
            "Config": self.config,
            "Tags": self.tags,
            "LastModifiedTime": self.last_modified_time,
            "LastModifiedRegion": self.last_modified_region,
        }


class Prompt(BaseModel):
    def __init__(
        self,
        instance_arn: str,
        name: str,
        s3_uri: str,
        description: str = "",
        tags: Optional[dict[str, str]] = None,
    ) -> None:
        self.prompt_id = str(uuid.uuid4())
        self.arn = f"{instance_arn}/prompt/{self.prompt_id}"
        self.name = name
        self.description = description
        self.s3_uri = s3_uri
        self.tags = tags or {}
        self.last_modified_time = _now_iso()
        self.last_modified_region = instance_arn.split(":")[3]

    def to_dict(self) -> dict[str, Any]:
        return {
            "PromptARN": self.arn,
            "PromptId": self.prompt_id,
            "Name": self.name,
            "Description": self.description,
            "Tags": self.tags,
            "LastModifiedTime": self.last_modified_time,
            "LastModifiedRegion": self.last_modified_region,
        }


class Queue(BaseModel):
    def __init__(
        self,
        instance_arn: str,
        name: str,
        hours_of_operation_id: str,
        description: str = "",
        outbound_caller_config: Optional[dict[str, str]] = None,
        max_contacts: Optional[int] = None,
        tags: Optional[dict[str, str]] = None,
    ) -> None:
        self.queue_id = str(uuid.uuid4())
        self.arn = f"{instance_arn}/queue/{self.queue_id}"
        self.name = name
        self.description = description
        self.hours_of_operation_id = hours_of_operation_id
        self.outbound_caller_config = outbound_caller_config or {}
        self.max_contacts = max_contacts or 0
        self.status = "ENABLED"
        self.tags = tags or {}
        self.last_modified_time = _now_iso()
        self.last_modified_region = instance_arn.split(":")[3]

    def to_dict(self) -> dict[str, Any]:
        return {
            "Name": self.name,
            "QueueArn": self.arn,
            "QueueId": self.queue_id,
            "Description": self.description,
            "OutboundCallerConfig": self.outbound_caller_config,
            "HoursOfOperationId": self.hours_of_operation_id,
            "MaxContacts": self.max_contacts,
            "Status": self.status,
            "Tags": self.tags,
            "LastModifiedTime": self.last_modified_time,
            "LastModifiedRegion": self.last_modified_region,
        }


class QuickConnect(BaseModel):
    def __init__(
        self,
        instance_arn: str,
        name: str,
        quick_connect_config: dict[str, Any],
        description: str = "",
        tags: Optional[dict[str, str]] = None,
    ) -> None:
        self.quick_connect_id = str(uuid.uuid4())
        self.arn = f"{instance_arn}/transfer-destination/{self.quick_connect_id}"
        self.name = name
        self.description = description
        self.quick_connect_config = quick_connect_config
        self.tags = tags or {}
        self.last_modified_time = _now_iso()
        self.last_modified_region = instance_arn.split(":")[3]

    def to_dict(self) -> dict[str, Any]:
        return {
            "QuickConnectARN": self.arn,
            "QuickConnectId": self.quick_connect_id,
            "Name": self.name,
            "Description": self.description,
            "QuickConnectConfig": self.quick_connect_config,
            "Tags": self.tags,
            "LastModifiedTime": self.last_modified_time,
            "LastModifiedRegion": self.last_modified_region,
        }


class RoutingProfile(BaseModel):
    def __init__(
        self,
        instance_id: str,
        instance_arn: str,
        name: str,
        description: str,
        default_outbound_queue_id: str,
        media_concurrencies: list[dict[str, Any]],
        tags: Optional[dict[str, str]] = None,
    ) -> None:
        self.routing_profile_id = str(uuid.uuid4())
        self.arn = f"{instance_arn}/routing-profile/{self.routing_profile_id}"
        self.instance_id = instance_id
        self.name = name
        self.description = description
        self.default_outbound_queue_id = default_outbound_queue_id
        self.media_concurrencies = media_concurrencies
        self.tags = tags or {}
        self.number_of_associated_queues = 0
        self.last_modified_time = _now_iso()
        self.last_modified_region = instance_arn.split(":")[3]

    def to_dict(self) -> dict[str, Any]:
        return {
            "InstanceId": self.instance_id,
            "Name": self.name,
            "RoutingProfileArn": self.arn,
            "RoutingProfileId": self.routing_profile_id,
            "Description": self.description,
            "MediaConcurrencies": self.media_concurrencies,
            "DefaultOutboundQueueId": self.default_outbound_queue_id,
            "Tags": self.tags,
            "NumberOfAssociatedQueues": self.number_of_associated_queues,
            "LastModifiedTime": self.last_modified_time,
            "LastModifiedRegion": self.last_modified_region,
        }


class SecurityProfile(BaseModel):
    def __init__(
        self,
        instance_arn: str,
        security_profile_name: str,
        description: str = "",
        permissions: Optional[list[str]] = None,
        tags: Optional[dict[str, str]] = None,
        allowed_access_control_tags: Optional[dict[str, str]] = None,
        tag_restricted_resources: Optional[list[str]] = None,
    ) -> None:
        self.security_profile_id = str(uuid.uuid4())
        self.arn = f"{instance_arn}/security-profile/{self.security_profile_id}"
        self.security_profile_name = security_profile_name
        self.description = description
        self.permissions = permissions or []
        self.tags = tags or {}
        self.allowed_access_control_tags = allowed_access_control_tags or {}
        self.tag_restricted_resources = tag_restricted_resources or []
        self.last_modified_time = _now_iso()
        self.last_modified_region = instance_arn.split(":")[3]

    def to_dict(self) -> dict[str, Any]:
        return {
            "Id": self.security_profile_id,
            "Arn": self.arn,
            "SecurityProfileName": self.security_profile_name,
            "Description": self.description,
            "Tags": self.tags,
            "AllowedAccessControlTags": self.allowed_access_control_tags,
            "TagRestrictedResources": self.tag_restricted_resources,
            "LastModifiedTime": self.last_modified_time,
            "LastModifiedRegion": self.last_modified_region,
        }


class User(BaseModel):
    def __init__(
        self,
        instance_id: str,
        instance_arn: str,
        username: str,
        security_profile_ids: list[str],
        routing_profile_id: str,
        phone_config: Optional[dict[str, Any]] = None,
        identity_info: Optional[dict[str, str]] = None,
        directory_user_id: Optional[str] = None,
        hierarchy_group_id: Optional[str] = None,
        tags: Optional[dict[str, str]] = None,
    ) -> None:
        self.user_id = str(uuid.uuid4())
        self.arn = f"{instance_arn}/agent/{self.user_id}"
        self.username = username
        self.identity_info = identity_info or {}
        self.phone_config = phone_config or {"PhoneType": "SOFT_PHONE", "AutoAccept": False, "AfterContactWorkTimeLimit": 0}
        self.directory_user_id = directory_user_id
        self.security_profile_ids = security_profile_ids
        self.routing_profile_id = routing_profile_id
        self.hierarchy_group_id = hierarchy_group_id
        self.tags = tags or {}
        self.last_modified_time = _now_iso()
        self.last_modified_region = instance_arn.split(":")[3]

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {
            "Id": self.user_id,
            "Arn": self.arn,
            "Username": self.username,
            "IdentityInfo": self.identity_info,
            "PhoneConfig": self.phone_config,
            "SecurityProfileIds": self.security_profile_ids,
            "RoutingProfileId": self.routing_profile_id,
            "Tags": self.tags,
            "LastModifiedTime": self.last_modified_time,
            "LastModifiedRegion": self.last_modified_region,
        }
        if self.directory_user_id:
            result["DirectoryUserId"] = self.directory_user_id
        if self.hierarchy_group_id:
            result["HierarchyGroupId"] = self.hierarchy_group_id
        return result


class UserHierarchyGroup(BaseModel):
    def __init__(
        self,
        instance_arn: str,
        name: str,
        parent_group_id: Optional[str] = None,
        level_id: str = "1",
        tags: Optional[dict[str, str]] = None,
    ) -> None:
        self.hierarchy_group_id = str(uuid.uuid4())
        self.arn = f"{instance_arn}/agent-group/{self.hierarchy_group_id}"
        self.name = name
        self.level_id = level_id
        self.parent_group_id = parent_group_id
        self.tags = tags or {}
        self.last_modified_time = _now_iso()
        self.last_modified_region = instance_arn.split(":")[3]

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {
            "Id": self.hierarchy_group_id,
            "Arn": self.arn,
            "Name": self.name,
            "LevelId": self.level_id,
            "Tags": self.tags,
            "LastModifiedTime": self.last_modified_time,
            "LastModifiedRegion": self.last_modified_region,
        }
        return result


class Vocabulary(BaseModel):
    def __init__(
        self,
        instance_arn: str,
        vocabulary_name: str,
        language_code: str,
        content: str,
        tags: Optional[dict[str, str]] = None,
    ) -> None:
        self.vocabulary_id = str(uuid.uuid4())
        self.arn = f"{instance_arn}/vocabulary/{self.vocabulary_id}"
        self.name = vocabulary_name
        self.language_code = language_code
        self.state = "ACTIVE"
        self.content = content
        self.tags = tags or {}
        self.last_modified_time = _now_iso()

    def to_dict(self) -> dict[str, Any]:
        return {
            "Name": self.name,
            "Id": self.vocabulary_id,
            "Arn": self.arn,
            "LanguageCode": self.language_code,
            "State": self.state,
            "LastModifiedTime": self.last_modified_time,
            "Content": self.content,
            "Tags": self.tags,
        }


class View(BaseModel):
    def __init__(
        self,
        instance_arn: str,
        name: str,
        status: str,
        content: dict[str, Any],
        description: str = "",
        tags: Optional[dict[str, str]] = None,
    ) -> None:
        self.view_id = str(uuid.uuid4())
        self.arn = f"{instance_arn}/view/{self.view_id}"
        self.name = name
        self.status = status
        self.type = "CUSTOMER_MANAGED"
        self.description = description
        self.version = 1
        self.content = content
        self.tags = tags or {}

    def to_dict(self) -> dict[str, Any]:
        return {
            "Id": self.view_id,
            "Arn": self.arn,
            "Name": self.name,
            "Status": self.status,
            "Type": self.type,
            "Description": self.description,
            "Version": self.version,
            "Content": self.content,
            "Tags": self.tags,
        }


class PhoneNumber(BaseModel):
    def __init__(
        self,
        instance_arn: str,
        phone_number: str,
        phone_number_country_code: str,
        phone_number_type: str,
        description: str = "",
        tags: Optional[dict[str, str]] = None,
    ) -> None:
        self.phone_number_id = str(uuid.uuid4())
        self.arn = f"{instance_arn}/phone-number/{self.phone_number_id}"
        self.phone_number = phone_number
        self.phone_number_country_code = phone_number_country_code
        self.phone_number_type = phone_number_type
        self.description = description
        self.target_arn = instance_arn
        self.instance_id = instance_arn.split("/")[-1]
        self.tags = tags or {}
        self.phone_number_status = {"Status": "CLAIMED"}

    def to_dict(self) -> dict[str, Any]:
        return {
            "PhoneNumberId": self.phone_number_id,
            "PhoneNumberArn": self.arn,
            "PhoneNumber": self.phone_number,
            "PhoneNumberCountryCode": self.phone_number_country_code,
            "PhoneNumberType": self.phone_number_type,
            "PhoneNumberDescription": self.description,
            "TargetArn": self.target_arn,
            "InstanceId": self.instance_id,
            "Tags": self.tags,
            "PhoneNumberStatus": self.phone_number_status,
        }


class TrafficDistributionGroup(BaseModel):
    def __init__(
        self,
        name: str,
        instance_arn: str,
        account_id: str,
        region: str,
        description: str = "",
        tags: Optional[dict[str, str]] = None,
    ) -> None:
        self.traffic_distribution_group_id = str(uuid.uuid4())
        self.arn = f"arn:aws:connect:{region}:{account_id}:traffic-distribution-group/{self.traffic_distribution_group_id}"
        self.name = name
        self.description = description
        self.instance_arn = instance_arn
        self.status = "ACTIVE"
        self.tags = tags or {}
        self.is_default = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "Id": self.traffic_distribution_group_id,
            "Arn": self.arn,
            "Name": self.name,
            "Description": self.description,
            "InstanceArn": self.instance_arn,
            "Status": self.status,
            "Tags": self.tags,
            "IsDefault": self.is_default,
        }


class EvaluationForm(BaseModel):
    def __init__(
        self,
        instance_arn: str,
        title: str,
        description: str = "",
        items: Optional[list[dict[str, Any]]] = None,
        scoring_strategy: Optional[dict[str, str]] = None,
        tags: Optional[dict[str, str]] = None,
    ) -> None:
        self.evaluation_form_id = str(uuid.uuid4())
        self.arn = f"{instance_arn}/evaluation-form/{self.evaluation_form_id}"
        self.title = title
        self.description = description
        self.items = items or []
        self.scoring_strategy = scoring_strategy
        self.status = "DRAFT"
        self.version = 1
        self.tags = tags or {}
        self.created_time = _now_iso()
        self.last_modified_time = _now_iso()

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {
            "EvaluationFormId": self.evaluation_form_id,
            "EvaluationFormArn": self.arn,
            "Title": self.title,
            "Description": self.description,
            "Status": self.status,
            "Items": self.items,
            "EvaluationFormVersion": self.version,
            "CreatedTime": self.created_time,
            "LastModifiedTime": self.last_modified_time,
            "Tags": self.tags,
        }
        if self.scoring_strategy:
            result["ScoringStrategy"] = self.scoring_strategy
        return result


class Rule(BaseModel):
    def __init__(
        self,
        instance_arn: str,
        name: str,
        trigger_event_source: dict[str, Any],
        function: str,
        actions: list[dict[str, Any]],
        publish_status: str,
        tags: Optional[dict[str, str]] = None,
    ) -> None:
        self.rule_id = str(uuid.uuid4())
        self.arn = f"{instance_arn}/rule/{self.rule_id}"
        self.name = name
        self.trigger_event_source = trigger_event_source
        self.function = function
        self.actions = actions
        self.publish_status = publish_status
        self.tags = tags or {}
        self.created_time = _now_iso()
        self.last_updated_time = _now_iso()

    def to_dict(self) -> dict[str, Any]:
        return {
            "RuleId": self.rule_id,
            "RuleArn": self.arn,
            "Name": self.name,
            "TriggerEventSource": self.trigger_event_source,
            "Function": self.function,
            "Actions": self.actions,
            "PublishStatus": self.publish_status,
            "CreatedTime": self.created_time,
            "LastUpdatedTime": self.last_updated_time,
            "Tags": self.tags,
        }


class ConnectBackend(BaseBackend):
    """Backend for Amazon Connect API."""

    def __init__(self, region_name: str, account_id: str) -> None:
        super().__init__(region_name, account_id)
        self.instances: dict[str, Instance] = {}
        self.analytics_data_associations: dict[
            str, dict[str, AnalyticsDataAssociation]
        ] = {}
        # Per-instance resource stores: instance_id -> resource_id -> resource
        self.agent_statuses: dict[str, dict[str, AgentStatus]] = {}
        self.contact_flows: dict[str, dict[str, ContactFlow]] = {}
        self.contact_flow_modules: dict[str, dict[str, ContactFlowModule]] = {}
        self.hours_of_operations: dict[str, dict[str, HoursOfOperation]] = {}
        self.prompts: dict[str, dict[str, Prompt]] = {}
        self.queues: dict[str, dict[str, Queue]] = {}
        self.quick_connects: dict[str, dict[str, QuickConnect]] = {}
        self.routing_profiles: dict[str, dict[str, RoutingProfile]] = {}
        self.security_profiles: dict[str, dict[str, SecurityProfile]] = {}
        self.users: dict[str, dict[str, User]] = {}
        self.user_hierarchy_groups: dict[str, dict[str, UserHierarchyGroup]] = {}
        self.vocabularies: dict[str, dict[str, Vocabulary]] = {}
        self.views: dict[str, dict[str, View]] = {}
        self.evaluation_forms: dict[str, dict[str, EvaluationForm]] = {}
        self.rules: dict[str, dict[str, Rule]] = {}
        # Global (not per-instance) stores
        self.phone_numbers: dict[str, PhoneNumber] = {}
        self.traffic_distribution_groups: dict[str, TrafficDistributionGroup] = {}
        # Per-instance contact attributes: instance_id -> contact_id -> attributes
        self.contact_attributes: dict[str, dict[str, dict[str, str]]] = {}
        self.tagger = TaggingService()

    def tag_resource(self, resource_arn: str, tags: dict[str, str]) -> None:
        self.tagger.tag_resource(
            resource_arn, TaggingService.convert_dict_to_tags_input(tags)
        )

    def untag_resource(self, resource_arn: str, tag_keys: list[str]) -> None:
        self.tagger.untag_resource_using_names(resource_arn, tag_keys)

    def list_tags_for_resource(self, resource_arn: str) -> dict[str, str]:
        return self.tagger.get_tag_dict_for_resource(resource_arn)

    def _get_instance_or_raise(self, instance_id: str) -> Instance:
        """Get instance by ID or raise ResourceNotFoundException."""
        if instance_id not in self.instances:
            raise ResourceNotFoundException(f"Instance with id {instance_id} not found")
        return self.instances[instance_id]

    # ---- Instance CRUD ----

    def create_instance(
        self,
        identity_management_type: str,
        inbound_calls_enabled: bool,
        outbound_calls_enabled: bool,
        instance_alias: Optional[str] = None,
        tags: Optional[dict[str, str]] = None,
    ) -> dict[str, str]:
        if not identity_management_type:
            raise InvalidParameterException(
                "IdentityManagementType is a required parameter"
            )
        instance = Instance(
            identity_management_type=identity_management_type,
            inbound_calls_enabled=inbound_calls_enabled,
            outbound_calls_enabled=outbound_calls_enabled,
            instance_alias=instance_alias,
            account_id=self.account_id,
            region=self.region_name,
            tags=tags,
        )
        self.instances[instance.id] = instance
        if tags:
            self.tag_resource(instance.arn, tags)
        return {"Id": instance.id, "Arn": instance.arn}

    def describe_instance(self, instance_id: str) -> dict[str, Any]:
        if not instance_id:
            raise InvalidParameterException("InstanceId is a required parameter")
        instance = self._get_instance_or_raise(instance_id)
        return instance.to_dict()

    @paginate(pagination_model=PAGINATION_MODEL)  # type: ignore[misc]
    def list_instances(
        self,
        max_results: Optional[int] = None,
        next_token: Optional[str] = None,
    ) -> list[dict[str, str]]:
        sorted_instances = sorted(
            self.instances.values(),
            key=lambda i: (i.created_time, i.id),
        )
        return [instance.to_summary_dict() for instance in sorted_instances]

    def delete_instance(self, instance_id: str) -> None:
        if not instance_id:
            raise InvalidParameterException("InstanceId is a required parameter")
        self._get_instance_or_raise(instance_id)
        del self.instances[instance_id]
        if instance_id in self.analytics_data_associations:
            del self.analytics_data_associations[instance_id]

    # ---- Instance Attribute ----

    def describe_instance_attribute(
        self, instance_id: str, attribute_type: str
    ) -> dict[str, str]:
        instance = self._get_instance_or_raise(instance_id)
        value = instance.attributes.get(attribute_type)
        if value is None:
            raise ResourceNotFoundException(
                f"Attribute {attribute_type} not found for instance {instance_id}"
            )
        return {"AttributeType": attribute_type, "Value": value}

    # ---- Analytics Data Association ----

    def associate_analytics_data_set(
        self,
        instance_id: str,
        data_set_id: str,
        target_account_id: Optional[str] = None,
    ) -> dict[str, str]:
        if not instance_id:
            raise InvalidParameterException("InstanceId is a required parameter")
        if not data_set_id:
            raise InvalidParameterException("DataSetId is a required parameter")
        self._get_instance_or_raise(instance_id)
        if not target_account_id:
            target_account_id = self.account_id
        if instance_id in self.analytics_data_associations:
            if data_set_id in self.analytics_data_associations[instance_id]:
                raise InvalidParameterException(
                    f"Analytics data association for data set {data_set_id} already exists for instance {instance_id}"
                )
        if instance_id not in self.analytics_data_associations:
            self.analytics_data_associations[instance_id] = {}
        association = AnalyticsDataAssociation(
            instance_id=instance_id,
            data_set_id=data_set_id,
            target_account_id=target_account_id,
            source_account_id=self.account_id,
            region=self.region_name,
        )
        self.analytics_data_associations[instance_id][data_set_id] = association
        return {
            "DataSetId": association.data_set_id,
            "TargetAccountId": association.target_account_id,
            "ResourceShareId": association.resource_share_id,
            "ResourceShareArn": association.resource_share_arn,
            "ResourceShareStatus": association.resource_share_status,
        }

    def disassociate_analytics_data_set(
        self, instance_id: str, data_set_id: str
    ) -> None:
        if not instance_id:
            raise InvalidParameterException("InstanceId is a required parameter")
        if not data_set_id:
            raise InvalidParameterException("DataSetId is a required parameter")
        self._get_instance_or_raise(instance_id)
        if instance_id not in self.analytics_data_associations:
            raise ResourceNotFoundException(
                f"Analytics data association for data set {data_set_id} not found for instance {instance_id}"
            )
        if data_set_id not in self.analytics_data_associations[instance_id]:
            raise ResourceNotFoundException(
                f"Analytics data association for data set {data_set_id} not found for instance {instance_id}"
            )
        del self.analytics_data_associations[instance_id][data_set_id]
        if not self.analytics_data_associations[instance_id]:
            del self.analytics_data_associations[instance_id]

    def list_agent_statuses(self, instance_id: str) -> list[dict[str, Any]]:
        self._get_instance_or_raise(instance_id)
        return []

    def list_approved_origins(self, instance_id: str) -> list[str]:
        self._get_instance_or_raise(instance_id)
        return []

    def list_bots(self, instance_id: str) -> list[dict[str, Any]]:
        self._get_instance_or_raise(instance_id)
        return []

    def list_contact_evaluations(self, instance_id: str) -> list[dict[str, Any]]:
        self._get_instance_or_raise(instance_id)
        return []

    def list_contact_flow_modules(self, instance_id: str) -> list[dict[str, Any]]:
        self._get_instance_or_raise(instance_id)
        return []

    def list_contact_flow_versions(
        self, instance_id: str, contact_flow_id: str
    ) -> list[dict[str, Any]]:
        self._get_instance_or_raise(instance_id)
        return []

    def list_contact_flows(self, instance_id: str) -> list[dict[str, Any]]:
        self._get_instance_or_raise(instance_id)
        return []

    def list_contact_references(self, instance_id: str) -> list[dict[str, Any]]:
        self._get_instance_or_raise(instance_id)
        return []

    def list_default_vocabularies(self, instance_id: str) -> list[dict[str, Any]]:
        self._get_instance_or_raise(instance_id)
        return []

    def list_evaluation_form_versions(
        self, instance_id: str, evaluation_form_id: str
    ) -> list[dict[str, Any]]:
        self._get_instance_or_raise(instance_id)
        return []

    def list_evaluation_forms(self, instance_id: str) -> list[dict[str, Any]]:
        self._get_instance_or_raise(instance_id)
        return []

    def list_flow_associations(self, instance_id: str) -> list[dict[str, Any]]:
        self._get_instance_or_raise(instance_id)
        return []

    def list_hours_of_operation_overrides(
        self, instance_id: str, hours_of_operation_id: str
    ) -> list[dict[str, Any]]:
        self._get_instance_or_raise(instance_id)
        return []

    def list_hours_of_operations(self, instance_id: str) -> list[dict[str, Any]]:
        self._get_instance_or_raise(instance_id)
        return []

    def list_instance_attributes(self, instance_id: str) -> list[dict[str, Any]]:
        self._get_instance_or_raise(instance_id)
        return []

    def list_instance_storage_configs(self, instance_id: str) -> list[dict[str, Any]]:
        self._get_instance_or_raise(instance_id)
        return []

    def list_lambda_functions(self, instance_id: str) -> list[str]:
        self._get_instance_or_raise(instance_id)
        return []

    def list_phone_numbers(self, instance_id: str) -> list[dict[str, Any]]:
        self._get_instance_or_raise(instance_id)
        return []

    def list_phone_numbers_v2(self) -> list[dict[str, Any]]:
        return []

    def list_prompts(self, instance_id: str) -> list[dict[str, Any]]:
        self._get_instance_or_raise(instance_id)
        return []

    def list_queue_quick_connects(
        self, instance_id: str, queue_id: str
    ) -> list[dict[str, Any]]:
        self._get_instance_or_raise(instance_id)
        return []

    def list_queues(self, instance_id: str) -> list[dict[str, Any]]:
        self._get_instance_or_raise(instance_id)
        return []

    def list_quick_connects(self, instance_id: str) -> list[dict[str, Any]]:
        self._get_instance_or_raise(instance_id)
        return []

    def list_routing_profiles(self, instance_id: str) -> list[dict[str, Any]]:
        self._get_instance_or_raise(instance_id)
        return []

    def list_security_keys(self, instance_id: str) -> list[dict[str, Any]]:
        self._get_instance_or_raise(instance_id)
        return []

    def list_security_profile_applications(
        self, instance_id: str, security_profile_id: str
    ) -> list[dict[str, Any]]:
        self._get_instance_or_raise(instance_id)
        return []

    def list_security_profile_permissions(
        self, instance_id: str, security_profile_id: str
    ) -> list[dict[str, Any]]:
        self._get_instance_or_raise(instance_id)
        return []

    def list_security_profiles(self, instance_id: str) -> list[dict[str, Any]]:
        self._get_instance_or_raise(instance_id)
        return []

    def list_use_cases(
        self, instance_id: str, integration_association_id: str
    ) -> list[dict[str, Any]]:
        self._get_instance_or_raise(instance_id)
        return []

    @paginate(pagination_model=PAGINATION_MODEL)  # type: ignore[misc]
    def list_analytics_data_associations(
        self,
        instance_id: str,
        data_set_id: Optional[str] = None,
        max_results: Optional[int] = None,
        next_token: Optional[str] = None,
    ) -> list[dict[str, str]]:
        if not instance_id:
            raise InvalidParameterException("InstanceId is a required parameter")
        self._get_instance_or_raise(instance_id)
        if instance_id not in self.analytics_data_associations:
            return []
        associations = list(self.analytics_data_associations[instance_id].values())
        if data_set_id:
            associations = [a for a in associations if a.data_set_id == data_set_id]
        associations.sort(key=lambda a: a.data_set_id)
        return [a.to_dict() for a in associations]

    # ---- Agent Status ----

    def create_agent_status(
        self,
        instance_id: str,
        name: str,
        state: str,
        description: str = "",
        display_order: Optional[int] = None,
        tags: Optional[dict[str, str]] = None,
    ) -> dict[str, str]:
        instance = self._get_instance_or_raise(instance_id)
        agent_status = AgentStatus(
            instance_arn=instance.arn,
            name=name,
            state=state,
            description=description,
            display_order=display_order,
            tags=tags,
        )
        if instance_id not in self.agent_statuses:
            self.agent_statuses[instance_id] = {}
        self.agent_statuses[instance_id][agent_status.agent_status_id] = agent_status
        if tags:
            self.tag_resource(agent_status.arn, tags)
        return {
            "AgentStatusARN": agent_status.arn,
            "AgentStatusId": agent_status.agent_status_id,
        }

    def describe_agent_status(
        self, instance_id: str, agent_status_id: str
    ) -> dict[str, Any]:
        self._get_instance_or_raise(instance_id)
        statuses = self.agent_statuses.get(instance_id, {})
        if agent_status_id not in statuses:
            raise ResourceNotFoundException(
                f"Agent status {agent_status_id} not found in instance {instance_id}"
            )
        return statuses[agent_status_id].to_dict()

    # ---- Contact Flow ----

    def create_contact_flow(
        self,
        instance_id: str,
        name: str,
        flow_type: str,
        content: str,
        description: str = "",
        status: str = "PUBLISHED",
        tags: Optional[dict[str, str]] = None,
    ) -> dict[str, str]:
        instance = self._get_instance_or_raise(instance_id)
        contact_flow = ContactFlow(
            instance_arn=instance.arn,
            name=name,
            flow_type=flow_type,
            content=content,
            description=description,
            status=status,
            tags=tags,
        )
        if instance_id not in self.contact_flows:
            self.contact_flows[instance_id] = {}
        self.contact_flows[instance_id][contact_flow.id] = contact_flow
        if tags:
            self.tag_resource(contact_flow.arn, tags)
        return {"ContactFlowId": contact_flow.id, "ContactFlowArn": contact_flow.arn}

    def describe_contact_flow(
        self, instance_id: str, contact_flow_id: str
    ) -> dict[str, Any]:
        self._get_instance_or_raise(instance_id)
        flows = self.contact_flows.get(instance_id, {})
        if contact_flow_id not in flows:
            raise ResourceNotFoundException(
                f"Contact flow {contact_flow_id} not found in instance {instance_id}"
            )
        return flows[contact_flow_id].to_dict()

    # ---- Contact Flow Module ----

    def create_contact_flow_module(
        self,
        instance_id: str,
        name: str,
        content: str,
        description: str = "",
        tags: Optional[dict[str, str]] = None,
    ) -> dict[str, str]:
        instance = self._get_instance_or_raise(instance_id)
        module = ContactFlowModule(
            instance_arn=instance.arn,
            name=name,
            content=content,
            description=description,
            tags=tags,
        )
        if instance_id not in self.contact_flow_modules:
            self.contact_flow_modules[instance_id] = {}
        self.contact_flow_modules[instance_id][module.id] = module
        if tags:
            self.tag_resource(module.arn, tags)
        return {"Id": module.id, "Arn": module.arn}

    def describe_contact_flow_module(
        self, instance_id: str, contact_flow_module_id: str
    ) -> dict[str, Any]:
        self._get_instance_or_raise(instance_id)
        modules = self.contact_flow_modules.get(instance_id, {})
        if contact_flow_module_id not in modules:
            raise ResourceNotFoundException(
                f"Contact flow module {contact_flow_module_id} not found in instance {instance_id}"
            )
        return modules[contact_flow_module_id].to_dict()

    # ---- Hours of Operation ----

    def create_hours_of_operation(
        self,
        instance_id: str,
        name: str,
        time_zone: str,
        config: list[dict[str, Any]],
        description: str = "",
        tags: Optional[dict[str, str]] = None,
    ) -> dict[str, str]:
        instance = self._get_instance_or_raise(instance_id)
        hours = HoursOfOperation(
            instance_arn=instance.arn,
            name=name,
            time_zone=time_zone,
            config=config,
            description=description,
            tags=tags,
        )
        if instance_id not in self.hours_of_operations:
            self.hours_of_operations[instance_id] = {}
        self.hours_of_operations[instance_id][hours.hours_of_operation_id] = hours
        if tags:
            self.tag_resource(hours.arn, tags)
        return {
            "HoursOfOperationId": hours.hours_of_operation_id,
            "HoursOfOperationArn": hours.arn,
        }

    def describe_hours_of_operation(
        self, instance_id: str, hours_of_operation_id: str
    ) -> dict[str, Any]:
        self._get_instance_or_raise(instance_id)
        hours_map = self.hours_of_operations.get(instance_id, {})
        if hours_of_operation_id not in hours_map:
            raise ResourceNotFoundException(
                f"Hours of operation {hours_of_operation_id} not found in instance {instance_id}"
            )
        return hours_map[hours_of_operation_id].to_dict()

    # ---- Prompt ----

    def create_prompt(
        self,
        instance_id: str,
        name: str,
        s3_uri: str,
        description: str = "",
        tags: Optional[dict[str, str]] = None,
    ) -> dict[str, str]:
        instance = self._get_instance_or_raise(instance_id)
        prompt = Prompt(
            instance_arn=instance.arn,
            name=name,
            s3_uri=s3_uri,
            description=description,
            tags=tags,
        )
        if instance_id not in self.prompts:
            self.prompts[instance_id] = {}
        self.prompts[instance_id][prompt.prompt_id] = prompt
        if tags:
            self.tag_resource(prompt.arn, tags)
        return {"PromptARN": prompt.arn, "PromptId": prompt.prompt_id}

    def describe_prompt(self, instance_id: str, prompt_id: str) -> dict[str, Any]:
        self._get_instance_or_raise(instance_id)
        prompts = self.prompts.get(instance_id, {})
        if prompt_id not in prompts:
            raise ResourceNotFoundException(
                f"Prompt {prompt_id} not found in instance {instance_id}"
            )
        return prompts[prompt_id].to_dict()

    # ---- Queue ----

    def create_queue(
        self,
        instance_id: str,
        name: str,
        hours_of_operation_id: str,
        description: str = "",
        outbound_caller_config: Optional[dict[str, str]] = None,
        max_contacts: Optional[int] = None,
        tags: Optional[dict[str, str]] = None,
    ) -> dict[str, str]:
        instance = self._get_instance_or_raise(instance_id)
        queue = Queue(
            instance_arn=instance.arn,
            name=name,
            hours_of_operation_id=hours_of_operation_id,
            description=description,
            outbound_caller_config=outbound_caller_config,
            max_contacts=max_contacts,
            tags=tags,
        )
        if instance_id not in self.queues:
            self.queues[instance_id] = {}
        self.queues[instance_id][queue.queue_id] = queue
        if tags:
            self.tag_resource(queue.arn, tags)
        return {"QueueId": queue.queue_id, "QueueArn": queue.arn}

    def describe_queue(self, instance_id: str, queue_id: str) -> dict[str, Any]:
        self._get_instance_or_raise(instance_id)
        queues = self.queues.get(instance_id, {})
        if queue_id not in queues:
            raise ResourceNotFoundException(
                f"Queue {queue_id} not found in instance {instance_id}"
            )
        return queues[queue_id].to_dict()

    # ---- Quick Connect ----

    def create_quick_connect(
        self,
        instance_id: str,
        name: str,
        quick_connect_config: dict[str, Any],
        description: str = "",
        tags: Optional[dict[str, str]] = None,
    ) -> dict[str, str]:
        instance = self._get_instance_or_raise(instance_id)
        qc = QuickConnect(
            instance_arn=instance.arn,
            name=name,
            quick_connect_config=quick_connect_config,
            description=description,
            tags=tags,
        )
        if instance_id not in self.quick_connects:
            self.quick_connects[instance_id] = {}
        self.quick_connects[instance_id][qc.quick_connect_id] = qc
        if tags:
            self.tag_resource(qc.arn, tags)
        return {"QuickConnectARN": qc.arn, "QuickConnectId": qc.quick_connect_id}

    def describe_quick_connect(
        self, instance_id: str, quick_connect_id: str
    ) -> dict[str, Any]:
        self._get_instance_or_raise(instance_id)
        qcs = self.quick_connects.get(instance_id, {})
        if quick_connect_id not in qcs:
            raise ResourceNotFoundException(
                f"Quick connect {quick_connect_id} not found in instance {instance_id}"
            )
        return qcs[quick_connect_id].to_dict()

    # ---- Routing Profile ----

    def create_routing_profile(
        self,
        instance_id: str,
        name: str,
        description: str,
        default_outbound_queue_id: str,
        media_concurrencies: list[dict[str, Any]],
        tags: Optional[dict[str, str]] = None,
    ) -> dict[str, str]:
        instance = self._get_instance_or_raise(instance_id)
        rp = RoutingProfile(
            instance_id=instance_id,
            instance_arn=instance.arn,
            name=name,
            description=description,
            default_outbound_queue_id=default_outbound_queue_id,
            media_concurrencies=media_concurrencies,
            tags=tags,
        )
        if instance_id not in self.routing_profiles:
            self.routing_profiles[instance_id] = {}
        self.routing_profiles[instance_id][rp.routing_profile_id] = rp
        if tags:
            self.tag_resource(rp.arn, tags)
        return {
            "RoutingProfileArn": rp.arn,
            "RoutingProfileId": rp.routing_profile_id,
        }

    def describe_routing_profile(
        self, instance_id: str, routing_profile_id: str
    ) -> dict[str, Any]:
        self._get_instance_or_raise(instance_id)
        rps = self.routing_profiles.get(instance_id, {})
        if routing_profile_id not in rps:
            raise ResourceNotFoundException(
                f"Routing profile {routing_profile_id} not found in instance {instance_id}"
            )
        return rps[routing_profile_id].to_dict()

    # ---- Security Profile ----

    def create_security_profile(
        self,
        instance_id: str,
        security_profile_name: str,
        description: str = "",
        permissions: Optional[list[str]] = None,
        tags: Optional[dict[str, str]] = None,
        allowed_access_control_tags: Optional[dict[str, str]] = None,
        tag_restricted_resources: Optional[list[str]] = None,
    ) -> dict[str, str]:
        instance = self._get_instance_or_raise(instance_id)
        sp = SecurityProfile(
            instance_arn=instance.arn,
            security_profile_name=security_profile_name,
            description=description,
            permissions=permissions,
            tags=tags,
            allowed_access_control_tags=allowed_access_control_tags,
            tag_restricted_resources=tag_restricted_resources,
        )
        if instance_id not in self.security_profiles:
            self.security_profiles[instance_id] = {}
        self.security_profiles[instance_id][sp.security_profile_id] = sp
        if tags:
            self.tag_resource(sp.arn, tags)
        return {
            "SecurityProfileId": sp.security_profile_id,
            "SecurityProfileArn": sp.arn,
        }

    def describe_security_profile(
        self, instance_id: str, security_profile_id: str
    ) -> dict[str, Any]:
        self._get_instance_or_raise(instance_id)
        sps = self.security_profiles.get(instance_id, {})
        if security_profile_id not in sps:
            raise ResourceNotFoundException(
                f"Security profile {security_profile_id} not found in instance {instance_id}"
            )
        return sps[security_profile_id].to_dict()

    # ---- User ----

    def create_user(
        self,
        instance_id: str,
        username: str,
        security_profile_ids: list[str],
        routing_profile_id: str,
        phone_config: Optional[dict[str, Any]] = None,
        identity_info: Optional[dict[str, str]] = None,
        directory_user_id: Optional[str] = None,
        hierarchy_group_id: Optional[str] = None,
        tags: Optional[dict[str, str]] = None,
    ) -> dict[str, str]:
        instance = self._get_instance_or_raise(instance_id)
        user = User(
            instance_id=instance_id,
            instance_arn=instance.arn,
            username=username,
            security_profile_ids=security_profile_ids,
            routing_profile_id=routing_profile_id,
            phone_config=phone_config,
            identity_info=identity_info,
            directory_user_id=directory_user_id,
            hierarchy_group_id=hierarchy_group_id,
            tags=tags,
        )
        if instance_id not in self.users:
            self.users[instance_id] = {}
        self.users[instance_id][user.user_id] = user
        if tags:
            self.tag_resource(user.arn, tags)
        return {"UserId": user.user_id, "UserArn": user.arn}

    def describe_user(self, instance_id: str, user_id: str) -> dict[str, Any]:
        self._get_instance_or_raise(instance_id)
        users = self.users.get(instance_id, {})
        if user_id not in users:
            raise ResourceNotFoundException(
                f"User {user_id} not found in instance {instance_id}"
            )
        return users[user_id].to_dict()

    # ---- User Hierarchy Group ----

    def create_user_hierarchy_group(
        self,
        instance_id: str,
        name: str,
        parent_group_id: Optional[str] = None,
        tags: Optional[dict[str, str]] = None,
    ) -> dict[str, str]:
        instance = self._get_instance_or_raise(instance_id)
        group = UserHierarchyGroup(
            instance_arn=instance.arn,
            name=name,
            parent_group_id=parent_group_id,
            tags=tags,
        )
        if instance_id not in self.user_hierarchy_groups:
            self.user_hierarchy_groups[instance_id] = {}
        self.user_hierarchy_groups[instance_id][group.hierarchy_group_id] = group
        if tags:
            self.tag_resource(group.arn, tags)
        return {
            "HierarchyGroupId": group.hierarchy_group_id,
            "HierarchyGroupArn": group.arn,
        }

    def describe_user_hierarchy_group(
        self, instance_id: str, hierarchy_group_id: str
    ) -> dict[str, Any]:
        self._get_instance_or_raise(instance_id)
        groups = self.user_hierarchy_groups.get(instance_id, {})
        if hierarchy_group_id not in groups:
            raise ResourceNotFoundException(
                f"Hierarchy group {hierarchy_group_id} not found in instance {instance_id}"
            )
        return groups[hierarchy_group_id].to_dict()

    # ---- User Hierarchy Structure ----

    def describe_user_hierarchy_structure(
        self, instance_id: str
    ) -> dict[str, Any]:
        self._get_instance_or_raise(instance_id)
        # Return a default 5-level hierarchy structure
        return {
            "LevelOne": {"Id": "1", "Arn": f"arn:aws:connect:{self.region_name}:{self.account_id}:instance/{instance_id}/agent-group-type/level-1", "Name": "Organization"},
            "LevelTwo": {"Id": "2", "Arn": f"arn:aws:connect:{self.region_name}:{self.account_id}:instance/{instance_id}/agent-group-type/level-2", "Name": "Division"},
            "LevelThree": {"Id": "3", "Arn": f"arn:aws:connect:{self.region_name}:{self.account_id}:instance/{instance_id}/agent-group-type/level-3", "Name": "Department"},
            "LevelFour": {"Id": "4", "Arn": f"arn:aws:connect:{self.region_name}:{self.account_id}:instance/{instance_id}/agent-group-type/level-4", "Name": "Team"},
            "LevelFive": {"Id": "5", "Arn": f"arn:aws:connect:{self.region_name}:{self.account_id}:instance/{instance_id}/agent-group-type/level-5", "Name": "Agent"},
        }

    # ---- Vocabulary ----

    def create_vocabulary(
        self,
        instance_id: str,
        vocabulary_name: str,
        language_code: str,
        content: str,
        tags: Optional[dict[str, str]] = None,
    ) -> dict[str, str]:
        instance = self._get_instance_or_raise(instance_id)
        vocab = Vocabulary(
            instance_arn=instance.arn,
            vocabulary_name=vocabulary_name,
            language_code=language_code,
            content=content,
            tags=tags,
        )
        if instance_id not in self.vocabularies:
            self.vocabularies[instance_id] = {}
        self.vocabularies[instance_id][vocab.vocabulary_id] = vocab
        if tags:
            self.tag_resource(vocab.arn, tags)
        return {
            "VocabularyArn": vocab.arn,
            "VocabularyId": vocab.vocabulary_id,
            "State": vocab.state,
        }

    def describe_vocabulary(
        self, instance_id: str, vocabulary_id: str
    ) -> dict[str, Any]:
        self._get_instance_or_raise(instance_id)
        vocabs = self.vocabularies.get(instance_id, {})
        if vocabulary_id not in vocabs:
            raise ResourceNotFoundException(
                f"Vocabulary {vocabulary_id} not found in instance {instance_id}"
            )
        return vocabs[vocabulary_id].to_dict()

    # ---- View ----

    def create_view(
        self,
        instance_id: str,
        name: str,
        status: str,
        content: dict[str, Any],
        description: str = "",
        tags: Optional[dict[str, str]] = None,
    ) -> dict[str, str]:
        instance = self._get_instance_or_raise(instance_id)
        view = View(
            instance_arn=instance.arn,
            name=name,
            status=status,
            content=content,
            description=description,
            tags=tags,
        )
        if instance_id not in self.views:
            self.views[instance_id] = {}
        self.views[instance_id][view.view_id] = view
        if tags:
            self.tag_resource(view.arn, tags)
        return {"View": view.to_dict()}

    def describe_view(self, instance_id: str, view_id: str) -> dict[str, Any]:
        self._get_instance_or_raise(instance_id)
        views = self.views.get(instance_id, {})
        if view_id not in views:
            raise ResourceNotFoundException(
                f"View {view_id} not found in instance {instance_id}"
            )
        return views[view_id].to_dict()

    # ---- Phone Number ----

    def claim_phone_number(
        self,
        instance_id: str,
        phone_number: str,
        phone_number_country_code: str,
        phone_number_type: str,
        description: str = "",
        tags: Optional[dict[str, str]] = None,
    ) -> dict[str, str]:
        instance = self._get_instance_or_raise(instance_id)
        pn = PhoneNumber(
            instance_arn=instance.arn,
            phone_number=phone_number,
            phone_number_country_code=phone_number_country_code,
            phone_number_type=phone_number_type,
            description=description,
            tags=tags,
        )
        self.phone_numbers[pn.phone_number_id] = pn
        if tags:
            self.tag_resource(pn.arn, tags)
        return {
            "PhoneNumberId": pn.phone_number_id,
            "PhoneNumberArn": pn.arn,
        }

    def describe_phone_number(self, phone_number_id: str) -> dict[str, Any]:
        if phone_number_id not in self.phone_numbers:
            raise ResourceNotFoundException(
                f"Phone number {phone_number_id} not found"
            )
        return self.phone_numbers[phone_number_id].to_dict()

    # ---- Traffic Distribution Group ----

    def create_traffic_distribution_group(
        self,
        name: str,
        instance_arn: str,
        description: str = "",
        tags: Optional[dict[str, str]] = None,
    ) -> dict[str, str]:
        tdg = TrafficDistributionGroup(
            name=name,
            instance_arn=instance_arn,
            account_id=self.account_id,
            region=self.region_name,
            description=description,
            tags=tags,
        )
        self.traffic_distribution_groups[tdg.traffic_distribution_group_id] = tdg
        if tags:
            self.tag_resource(tdg.arn, tags)
        return {
            "Id": tdg.traffic_distribution_group_id,
            "Arn": tdg.arn,
        }

    def describe_traffic_distribution_group(
        self, traffic_distribution_group_id: str
    ) -> dict[str, Any]:
        if traffic_distribution_group_id not in self.traffic_distribution_groups:
            raise ResourceNotFoundException(
                f"Traffic distribution group {traffic_distribution_group_id} not found"
            )
        return self.traffic_distribution_groups[
            traffic_distribution_group_id
        ].to_dict()

    # ---- Evaluation Form ----

    def create_evaluation_form(
        self,
        instance_id: str,
        title: str,
        description: str = "",
        items: Optional[list[dict[str, Any]]] = None,
        scoring_strategy: Optional[dict[str, str]] = None,
    ) -> dict[str, str]:
        instance = self._get_instance_or_raise(instance_id)
        form = EvaluationForm(
            instance_arn=instance.arn,
            title=title,
            description=description,
            items=items,
            scoring_strategy=scoring_strategy,
        )
        if instance_id not in self.evaluation_forms:
            self.evaluation_forms[instance_id] = {}
        self.evaluation_forms[instance_id][form.evaluation_form_id] = form
        return {
            "EvaluationFormId": form.evaluation_form_id,
            "EvaluationFormArn": form.arn,
        }

    def describe_evaluation_form(
        self, instance_id: str, evaluation_form_id: str
    ) -> dict[str, Any]:
        self._get_instance_or_raise(instance_id)
        forms = self.evaluation_forms.get(instance_id, {})
        if evaluation_form_id not in forms:
            raise ResourceNotFoundException(
                f"Evaluation form {evaluation_form_id} not found in instance {instance_id}"
            )
        return forms[evaluation_form_id].to_dict()

    # ---- Rule ----

    def create_rule(
        self,
        instance_id: str,
        name: str,
        trigger_event_source: dict[str, Any],
        function: str,
        actions: list[dict[str, Any]],
        publish_status: str,
    ) -> dict[str, str]:
        instance = self._get_instance_or_raise(instance_id)
        rule = Rule(
            instance_arn=instance.arn,
            name=name,
            trigger_event_source=trigger_event_source,
            function=function,
            actions=actions,
            publish_status=publish_status,
        )
        if instance_id not in self.rules:
            self.rules[instance_id] = {}
        self.rules[instance_id][rule.rule_id] = rule
        return {"RuleArn": rule.arn, "RuleId": rule.rule_id}

    def describe_rule(self, instance_id: str, rule_id: str) -> dict[str, Any]:
        self._get_instance_or_raise(instance_id)
        rules = self.rules.get(instance_id, {})
        if rule_id not in rules:
            raise ResourceNotFoundException(
                f"Rule {rule_id} not found in instance {instance_id}"
            )
        return rules[rule_id].to_dict()

    # ---- Contact / Contact Attributes ----

    def get_contact_attributes(
        self, instance_id: str, initial_contact_id: str
    ) -> dict[str, str]:
        self._get_instance_or_raise(instance_id)
        attrs = self.contact_attributes.get(instance_id, {}).get(
            initial_contact_id, {}
        )
        return attrs

    def update_contact_attributes(
        self,
        instance_id: str,
        initial_contact_id: str,
        attributes: dict[str, str],
    ) -> None:
        self._get_instance_or_raise(instance_id)
        if instance_id not in self.contact_attributes:
            self.contact_attributes[instance_id] = {}
        if initial_contact_id not in self.contact_attributes[instance_id]:
            self.contact_attributes[instance_id][initial_contact_id] = {}
        self.contact_attributes[instance_id][initial_contact_id].update(attributes)


connect_backends = BackendDict(ConnectBackend, "connect")
