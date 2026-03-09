from collections.abc import Iterable
from datetime import datetime
from typing import Any, Optional

from moto.core.base_backend import BackendDict, BaseBackend
from moto.core.common_models import BaseModel
from moto.core.utils import unix_time
from moto.moto_api._internal import mock_random
from moto.utilities.tagging_service import TaggingService
from moto.utilities.utils import get_partition

from .exceptions import (
    ApplicationNotFound,
    CampaignNotFound,
    EndpointNotFound,
    EventStreamNotFound,
    ExportJobNotFound,
    ImportJobNotFound,
    JourneyNotFound,
    RecommenderNotFound,
    SegmentNotFound,
    TemplateNotFound,
)


def _now_iso() -> str:
    return datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%fZ")


def _gen_id() -> str:
    return str(mock_random.uuid4()).replace("-", "")


class App(BaseModel):
    def __init__(self, account_id: str, region_name: str, name: str):
        self.application_id = _gen_id()
        self.arn = f"arn:{get_partition(region_name)}:mobiletargeting:{region_name}:{account_id}:apps/{self.application_id}"
        self.name = name
        self.created = unix_time()
        self.settings = AppSettings()
        self.event_stream: Optional[EventStream] = None

    def get_settings(self) -> "AppSettings":
        return self.settings

    def update_settings(self, settings: dict[str, Any]) -> "AppSettings":
        self.settings.update(settings)
        return self.settings

    def delete_event_stream(self) -> "EventStream":
        stream = self.event_stream
        self.event_stream = None
        return stream  # type: ignore

    def get_event_stream(self) -> "EventStream":
        if self.event_stream is None:
            raise EventStreamNotFound()
        return self.event_stream

    def put_event_stream(self, stream_arn: str, role_arn: str) -> "EventStream":
        self.event_stream = EventStream(stream_arn, role_arn)
        return self.event_stream

    def to_json(self) -> dict[str, Any]:
        return {
            "Arn": self.arn,
            "Id": self.application_id,
            "Name": self.name,
            "CreationDate": self.created,
        }


class AppSettings(BaseModel):
    def __init__(self) -> None:
        self.settings: dict[str, Any] = {}
        self.last_modified = _now_iso()

    def update(self, settings: dict[str, Any]) -> None:
        self.settings = settings
        self.last_modified = _now_iso()

    def to_json(self) -> dict[str, Any]:
        return {
            "CampaignHook": self.settings.get("CampaignHook", {}),
            "CloudWatchMetricsEnabled": self.settings.get(
                "CloudWatchMetricsEnabled", False
            ),
            "LastModifiedDate": self.last_modified,
            "Limits": self.settings.get("Limits", {}),
            "QuietTime": self.settings.get("QuietTime", {}),
        }


class EventStream(BaseModel):
    def __init__(self, stream_arn: str, role_arn: str):
        self.stream_arn = stream_arn
        self.role_arn = role_arn
        self.last_modified = _now_iso()

    def to_json(self) -> dict[str, Any]:
        return {
            "DestinationStreamArn": self.stream_arn,
            "RoleArn": self.role_arn,
            "LastModifiedDate": self.last_modified,
        }


# --- Campaign ---


class Campaign(BaseModel):
    def __init__(
        self,
        account_id: str,
        region_name: str,
        application_id: str,
        params: dict[str, Any],
    ):
        self.campaign_id = _gen_id()
        self.application_id = application_id
        self.arn = (
            f"arn:{get_partition(region_name)}:mobiletargeting:{region_name}:"
            f"{account_id}:apps/{application_id}/campaigns/{self.campaign_id}"
        )
        self.params = params
        self.version = 1
        self.created = _now_iso()
        self.last_modified = _now_iso()
        self.state = {"CampaignStatus": "PAUSED"}
        # Version history
        self.versions: list[dict[str, Any]] = []
        self._save_version()

    def _save_version(self) -> None:
        self.versions.append(self._to_json_internal())

    def update(self, params: dict[str, Any]) -> None:
        self.params = params
        self.version += 1
        self.last_modified = _now_iso()
        self._save_version()

    def _to_json_internal(self) -> dict[str, Any]:
        result = dict(self.params)
        result.update(
            {
                "Id": self.campaign_id,
                "ApplicationId": self.application_id,
                "Arn": self.arn,
                "CreationDate": self.created,
                "LastModifiedDate": self.last_modified,
                "Version": self.version,
                "State": self.state,
            }
        )
        return result

    def to_json(self) -> dict[str, Any]:
        return self._to_json_internal()


# --- Segment ---


class Segment(BaseModel):
    def __init__(
        self,
        account_id: str,
        region_name: str,
        application_id: str,
        params: dict[str, Any],
    ):
        self.segment_id = _gen_id()
        self.application_id = application_id
        self.arn = (
            f"arn:{get_partition(region_name)}:mobiletargeting:{region_name}:"
            f"{account_id}:apps/{application_id}/segments/{self.segment_id}"
        )
        self.params = params
        self.segment_type = params.get("SegmentType", "DIMENSIONAL")
        self.version = 1
        self.created = _now_iso()
        self.last_modified = _now_iso()
        self.versions: list[dict[str, Any]] = []
        self._save_version()

    def _save_version(self) -> None:
        self.versions.append(self._to_json_internal())

    def update(self, params: dict[str, Any]) -> None:
        self.params = params
        self.version += 1
        self.last_modified = _now_iso()
        self._save_version()

    def _to_json_internal(self) -> dict[str, Any]:
        result = dict(self.params)
        result.update(
            {
                "Id": self.segment_id,
                "ApplicationId": self.application_id,
                "Arn": self.arn,
                "CreationDate": self.created,
                "LastModifiedDate": self.last_modified,
                "Version": self.version,
                "SegmentType": self.segment_type,
            }
        )
        return result

    def to_json(self) -> dict[str, Any]:
        return self._to_json_internal()


# --- Journey ---


class Journey(BaseModel):
    def __init__(
        self,
        account_id: str,
        region_name: str,
        application_id: str,
        params: dict[str, Any],
    ):
        self.journey_id = _gen_id()
        self.application_id = application_id
        self.arn = (
            f"arn:{get_partition(region_name)}:mobiletargeting:{region_name}:"
            f"{account_id}:apps/{application_id}/journeys/{self.journey_id}"
        )
        self.params = params
        self.state = params.get("State", "DRAFT")
        self.created = _now_iso()
        self.last_modified = _now_iso()

    def update(self, params: dict[str, Any]) -> None:
        self.params = params
        if "State" in params:
            self.state = params["State"]
        self.last_modified = _now_iso()

    def update_state(self, state: str) -> None:
        self.state = state
        self.last_modified = _now_iso()

    def to_json(self) -> dict[str, Any]:
        result = dict(self.params)
        result.update(
            {
                "Id": self.journey_id,
                "ApplicationId": self.application_id,
                "Arn": self.arn,
                "CreationDate": self.created,
                "LastModifiedDate": self.last_modified,
                "State": self.state,
            }
        )
        return result


# --- Template ---


class Template(BaseModel):
    def __init__(
        self,
        template_name: str,
        template_type: str,
        params: dict[str, Any],
    ):
        self.template_name = template_name
        self.template_type = template_type  # EMAIL, SMS, PUSH, VOICE, INAPP
        self.params = params
        self.version = "1"
        self.created = _now_iso()
        self.last_modified = _now_iso()
        self.active_version: Optional[str] = None
        # Store versions: version_number -> params snapshot
        self.versions: dict[str, dict[str, Any]] = {}
        self._save_version()

    def _save_version(self) -> None:
        self.versions[self.version] = self._to_json_internal()

    def update(self, params: dict[str, Any]) -> None:
        self.params = params
        self.version = str(int(self.version) + 1)
        self.last_modified = _now_iso()
        self._save_version()

    def _to_json_internal(self) -> dict[str, Any]:
        result = dict(self.params)
        result.update(
            {
                "TemplateName": self.template_name,
                "TemplateType": self.template_type,
                "Version": self.version,
                "CreationDate": self.created,
                "LastModifiedDate": self.last_modified,
            }
        )
        return result

    def to_json(self) -> dict[str, Any]:
        return self._to_json_internal()


# --- Channel ---


class Channel(BaseModel):
    def __init__(self, application_id: str, channel_type: str, params: dict[str, Any]):
        self.channel_id = _gen_id()
        self.application_id = application_id
        self.channel_type = channel_type
        self.params = params
        self.enabled = params.get("Enabled", True)
        self.created = _now_iso()
        self.last_modified = _now_iso()
        self.version = 1

    def update(self, params: dict[str, Any]) -> None:
        self.params = params
        self.enabled = params.get("Enabled", self.enabled)
        self.last_modified = _now_iso()
        self.version += 1

    def to_json(self) -> dict[str, Any]:
        result = dict(self.params)
        result.update(
            {
                "Id": self.channel_id,
                "ApplicationId": self.application_id,
                "CreationDate": self.created,
                "LastModifiedDate": self.last_modified,
                "Enabled": self.enabled,
                "Version": self.version,
                "Platform": self.channel_type.upper(),
            }
        )
        return result


# --- Endpoint ---


class Endpoint(BaseModel):
    def __init__(
        self,
        application_id: str,
        endpoint_id: str,
        params: dict[str, Any],
    ):
        self.endpoint_id = endpoint_id
        self.application_id = application_id
        self.params = params
        self.created = _now_iso()
        self.effective_date = params.get("EffectiveDate", _now_iso())
        self.user_id = params.get("User", {}).get("UserId", "")

    def update(self, params: dict[str, Any]) -> None:
        self.params = params
        self.effective_date = params.get("EffectiveDate", _now_iso())
        if "User" in params and "UserId" in params["User"]:
            self.user_id = params["User"]["UserId"]

    def to_json(self) -> dict[str, Any]:
        result = dict(self.params)
        result.update(
            {
                "Id": self.endpoint_id,
                "ApplicationId": self.application_id,
                "CreationDate": self.created,
                "EffectiveDate": self.effective_date,
                "CohortId": "1",
            }
        )
        return result


# --- Export/Import Jobs ---


class ExportJob(BaseModel):
    def __init__(self, application_id: str, params: dict[str, Any]):
        self.job_id = _gen_id()
        self.application_id = application_id
        self.params = params
        self.created = _now_iso()
        self.status = "COMPLETED"
        self.completed_pieces = 1
        self.total_pieces = 1

    def to_json(self) -> dict[str, Any]:
        return {
            "Id": self.job_id,
            "ApplicationId": self.application_id,
            "CreationDate": self.created,
            "CompletedPieces": self.completed_pieces,
            "CompletionDate": self.created,
            "Definition": self.params,
            "FailedPieces": 0,
            "JobStatus": self.status,
            "TotalFailures": 0,
            "TotalPieces": self.total_pieces,
            "TotalProcessed": 0,
            "Type": "EXPORT",
        }


class ImportJob(BaseModel):
    def __init__(self, application_id: str, params: dict[str, Any]):
        self.job_id = _gen_id()
        self.application_id = application_id
        self.params = params
        self.created = _now_iso()
        self.status = "COMPLETED"

    def to_json(self) -> dict[str, Any]:
        return {
            "Id": self.job_id,
            "ApplicationId": self.application_id,
            "CreationDate": self.created,
            "CompletedPieces": 1,
            "CompletionDate": self.created,
            "Definition": self.params,
            "FailedPieces": 0,
            "JobStatus": self.status,
            "TotalFailures": 0,
            "TotalPieces": 1,
            "TotalProcessed": 0,
            "Type": "IMPORT",
        }


# --- Recommender Configuration ---


class RecommenderConfig(BaseModel):
    def __init__(self, params: dict[str, Any]):
        self.recommender_id = _gen_id()
        self.params = params
        self.created = _now_iso()
        self.last_modified = _now_iso()

    def update(self, params: dict[str, Any]) -> None:
        self.params = params
        self.last_modified = _now_iso()

    def to_json(self) -> dict[str, Any]:
        result = dict(self.params)
        result.update(
            {
                "Id": self.recommender_id,
                "CreationDate": self.created,
                "LastModifiedDate": self.last_modified,
            }
        )
        return result


# --- Backend ---


# Channel type constants
CHANNEL_TYPES = [
    "ADM",
    "APNS",
    "APNS_SANDBOX",
    "APNS_VOIP",
    "APNS_VOIP_SANDBOX",
    "BAIDU",
    "EMAIL",
    "GCM",
    "SMS",
    "VOICE",
]


class PinpointBackend(BaseBackend):
    """Implementation of Pinpoint APIs."""

    def __init__(self, region_name: str, account_id: str):
        super().__init__(region_name, account_id)
        self.apps: dict[str, App] = {}
        self.tagger = TaggingService()
        # Per-app resources
        self.campaigns: dict[str, dict[str, Campaign]] = {}  # app_id -> {campaign_id -> Campaign}
        self.segments: dict[str, dict[str, Segment]] = {}
        self.journeys: dict[str, dict[str, Journey]] = {}
        self.channels: dict[str, dict[str, Channel]] = {}  # app_id -> {channel_type -> Channel}
        self.endpoints: dict[str, dict[str, Endpoint]] = {}  # app_id -> {endpoint_id -> Endpoint}
        self.export_jobs: dict[str, list[ExportJob]] = {}
        self.import_jobs: dict[str, list[ImportJob]] = {}
        # Global resources
        self.templates: dict[str, Template] = {}  # "name/type" -> Template
        self.recommenders: dict[str, RecommenderConfig] = {}

    def _ensure_app_stores(self, application_id: str) -> None:
        if application_id not in self.campaigns:
            self.campaigns[application_id] = {}
        if application_id not in self.segments:
            self.segments[application_id] = {}
        if application_id not in self.journeys:
            self.journeys[application_id] = {}
        if application_id not in self.channels:
            self.channels[application_id] = {}
        if application_id not in self.endpoints:
            self.endpoints[application_id] = {}
        if application_id not in self.export_jobs:
            self.export_jobs[application_id] = []
        if application_id not in self.import_jobs:
            self.import_jobs[application_id] = []

    # --- App ---

    def create_app(self, name: str, tags: dict[str, str]) -> App:
        app = App(self.account_id, self.region_name, name)
        self.apps[app.application_id] = app
        self._ensure_app_stores(app.application_id)
        tag_list = self.tagger.convert_dict_to_tags_input(tags)
        self.tagger.tag_resource(app.arn, tag_list)
        return app

    def delete_app(self, application_id: str) -> App:
        self.get_app(application_id)
        return self.apps.pop(application_id)

    def get_app(self, application_id: str) -> App:
        if application_id not in self.apps:
            raise ApplicationNotFound()
        return self.apps[application_id]

    def get_apps(self) -> Iterable[App]:
        return self.apps.values()

    def update_application_settings(
        self, application_id: str, settings: dict[str, Any]
    ) -> AppSettings:
        app = self.get_app(application_id)
        return app.update_settings(settings)

    def get_application_settings(self, application_id: str) -> AppSettings:
        app = self.get_app(application_id)
        return app.get_settings()

    # --- Tags ---

    def list_tags_for_resource(self, resource_arn: str) -> dict[str, dict[str, str]]:
        tags = self.tagger.get_tag_dict_for_resource(resource_arn)
        return {"tags": tags}

    def tag_resource(self, resource_arn: str, tags: dict[str, str]) -> None:
        tag_list = TaggingService.convert_dict_to_tags_input(tags)
        self.tagger.tag_resource(resource_arn, tag_list)

    def untag_resource(self, resource_arn: str, tag_keys: list[str]) -> None:
        self.tagger.untag_resource_using_names(resource_arn, tag_keys)

    # --- Event Stream ---

    def put_event_stream(
        self, application_id: str, stream_arn: str, role_arn: str
    ) -> EventStream:
        app = self.get_app(application_id)
        return app.put_event_stream(stream_arn, role_arn)

    def get_event_stream(self, application_id: str) -> EventStream:
        app = self.get_app(application_id)
        return app.get_event_stream()

    def delete_event_stream(self, application_id: str) -> EventStream:
        app = self.get_app(application_id)
        return app.delete_event_stream()

    # --- Campaign ---

    def create_campaign(
        self, application_id: str, params: dict[str, Any]
    ) -> Campaign:
        self.get_app(application_id)
        self._ensure_app_stores(application_id)
        campaign = Campaign(
            self.account_id, self.region_name, application_id, params
        )
        self.campaigns[application_id][campaign.campaign_id] = campaign
        tag_list = self.tagger.convert_dict_to_tags_input(params.get("tags", {}))
        self.tagger.tag_resource(campaign.arn, tag_list)
        return campaign

    def get_campaign(self, application_id: str, campaign_id: str) -> Campaign:
        self.get_app(application_id)
        self._ensure_app_stores(application_id)
        if campaign_id not in self.campaigns[application_id]:
            raise CampaignNotFound()
        return self.campaigns[application_id][campaign_id]

    def get_campaigns(self, application_id: str) -> Iterable[Campaign]:
        self.get_app(application_id)
        self._ensure_app_stores(application_id)
        return self.campaigns[application_id].values()

    def update_campaign(
        self, application_id: str, campaign_id: str, params: dict[str, Any]
    ) -> Campaign:
        campaign = self.get_campaign(application_id, campaign_id)
        campaign.update(params)
        return campaign

    def delete_campaign(self, application_id: str, campaign_id: str) -> Campaign:
        campaign = self.get_campaign(application_id, campaign_id)
        del self.campaigns[application_id][campaign_id]
        return campaign

    def get_campaign_version(
        self, application_id: str, campaign_id: str, version: int
    ) -> dict[str, Any]:
        campaign = self.get_campaign(application_id, campaign_id)
        if version < 1 or version > len(campaign.versions):
            raise CampaignNotFound()
        return campaign.versions[version - 1]

    def get_campaign_versions(
        self, application_id: str, campaign_id: str
    ) -> list[dict[str, Any]]:
        campaign = self.get_campaign(application_id, campaign_id)
        return campaign.versions

    def get_campaign_activities(
        self, application_id: str, campaign_id: str
    ) -> list[dict[str, Any]]:
        self.get_campaign(application_id, campaign_id)
        # Return empty activities list (activities are execution metrics)
        return []

    # --- Segment ---

    def create_segment(
        self, application_id: str, params: dict[str, Any]
    ) -> Segment:
        self.get_app(application_id)
        self._ensure_app_stores(application_id)
        segment = Segment(
            self.account_id, self.region_name, application_id, params
        )
        self.segments[application_id][segment.segment_id] = segment
        tag_list = self.tagger.convert_dict_to_tags_input(params.get("tags", {}))
        self.tagger.tag_resource(segment.arn, tag_list)
        return segment

    def get_segment(self, application_id: str, segment_id: str) -> Segment:
        self.get_app(application_id)
        self._ensure_app_stores(application_id)
        if segment_id not in self.segments[application_id]:
            raise SegmentNotFound()
        return self.segments[application_id][segment_id]

    def get_segments(self, application_id: str) -> Iterable[Segment]:
        self.get_app(application_id)
        self._ensure_app_stores(application_id)
        return self.segments[application_id].values()

    def update_segment(
        self, application_id: str, segment_id: str, params: dict[str, Any]
    ) -> Segment:
        segment = self.get_segment(application_id, segment_id)
        segment.update(params)
        return segment

    def delete_segment(self, application_id: str, segment_id: str) -> Segment:
        segment = self.get_segment(application_id, segment_id)
        del self.segments[application_id][segment_id]
        return segment

    def get_segment_version(
        self, application_id: str, segment_id: str, version: int
    ) -> dict[str, Any]:
        segment = self.get_segment(application_id, segment_id)
        if version < 1 or version > len(segment.versions):
            raise SegmentNotFound()
        return segment.versions[version - 1]

    def get_segment_versions(
        self, application_id: str, segment_id: str
    ) -> list[dict[str, Any]]:
        segment = self.get_segment(application_id, segment_id)
        return segment.versions

    def get_segment_export_jobs(
        self, application_id: str, segment_id: str
    ) -> list[dict[str, Any]]:
        self.get_segment(application_id, segment_id)
        # Return export jobs filtered by segment
        return [
            j.to_json()
            for j in self.export_jobs.get(application_id, [])
            if j.params.get("SegmentId") == segment_id
        ]

    def get_segment_import_jobs(
        self, application_id: str, segment_id: str
    ) -> list[dict[str, Any]]:
        self.get_segment(application_id, segment_id)
        return [
            j.to_json()
            for j in self.import_jobs.get(application_id, [])
            if j.params.get("SegmentId") == segment_id
        ]

    # --- Journey ---

    def create_journey(
        self, application_id: str, params: dict[str, Any]
    ) -> Journey:
        self.get_app(application_id)
        self._ensure_app_stores(application_id)
        journey = Journey(
            self.account_id, self.region_name, application_id, params
        )
        self.journeys[application_id][journey.journey_id] = journey
        tag_list = self.tagger.convert_dict_to_tags_input(params.get("tags", {}))
        self.tagger.tag_resource(journey.arn, tag_list)
        return journey

    def get_journey(self, application_id: str, journey_id: str) -> Journey:
        self.get_app(application_id)
        self._ensure_app_stores(application_id)
        if journey_id not in self.journeys[application_id]:
            raise JourneyNotFound()
        return self.journeys[application_id][journey_id]

    def list_journeys(self, application_id: str) -> Iterable[Journey]:
        self.get_app(application_id)
        self._ensure_app_stores(application_id)
        return self.journeys[application_id].values()

    def update_journey(
        self, application_id: str, journey_id: str, params: dict[str, Any]
    ) -> Journey:
        journey = self.get_journey(application_id, journey_id)
        journey.update(params)
        return journey

    def update_journey_state(
        self, application_id: str, journey_id: str, state: str
    ) -> Journey:
        journey = self.get_journey(application_id, journey_id)
        journey.update_state(state)
        return journey

    def delete_journey(self, application_id: str, journey_id: str) -> Journey:
        journey = self.get_journey(application_id, journey_id)
        del self.journeys[application_id][journey_id]
        return journey

    # --- Template ---

    def _template_key(self, template_name: str, template_type: str) -> str:
        return f"{template_name}/{template_type}"

    def create_template(
        self, template_name: str, template_type: str, params: dict[str, Any]
    ) -> Template:
        key = self._template_key(template_name, template_type)
        template = Template(template_name, template_type, params)
        self.templates[key] = template
        return template

    def get_template(self, template_name: str, template_type: str) -> Template:
        key = self._template_key(template_name, template_type)
        if key not in self.templates:
            raise TemplateNotFound()
        return self.templates[key]

    def update_template(
        self, template_name: str, template_type: str, params: dict[str, Any]
    ) -> Template:
        template = self.get_template(template_name, template_type)
        template.update(params)
        return template

    def delete_template(self, template_name: str, template_type: str) -> Template:
        template = self.get_template(template_name, template_type)
        key = self._template_key(template_name, template_type)
        del self.templates[key]
        return template

    def list_templates(self) -> list[dict[str, Any]]:
        return [t.to_json() for t in self.templates.values()]

    def list_template_versions(
        self, template_name: str, template_type: str
    ) -> list[dict[str, Any]]:
        template = self.get_template(template_name, template_type)
        return list(template.versions.values())

    def update_template_active_version(
        self, template_name: str, template_type: str, version: str
    ) -> None:
        template = self.get_template(template_name, template_type)
        template.active_version = version

    # --- Channel ---

    def update_channel(
        self, application_id: str, channel_type: str, params: dict[str, Any]
    ) -> Channel:
        self.get_app(application_id)
        self._ensure_app_stores(application_id)
        if channel_type in self.channels[application_id]:
            channel = self.channels[application_id][channel_type]
            channel.update(params)
        else:
            channel = Channel(application_id, channel_type, params)
            self.channels[application_id][channel_type] = channel
        return channel

    def get_channel(self, application_id: str, channel_type: str) -> Channel:
        self.get_app(application_id)
        self._ensure_app_stores(application_id)
        if channel_type not in self.channels[application_id]:
            # Return a default empty channel
            channel = Channel(application_id, channel_type, {})
            channel.enabled = False
            self.channels[application_id][channel_type] = channel
        return self.channels[application_id][channel_type]

    def delete_channel(self, application_id: str, channel_type: str) -> Channel:
        self.get_app(application_id)
        self._ensure_app_stores(application_id)
        if channel_type in self.channels[application_id]:
            return self.channels[application_id].pop(channel_type)
        # Return empty channel on delete of non-existent
        return Channel(application_id, channel_type, {"Enabled": False})

    def get_channels(self, application_id: str) -> dict[str, Any]:
        self.get_app(application_id)
        self._ensure_app_stores(application_id)
        channels_data: dict[str, Any] = {}
        for ctype in CHANNEL_TYPES:
            if ctype in self.channels[application_id]:
                channels_data[ctype] = self.channels[application_id][ctype].to_json()
        return {"Channels": channels_data}

    # --- Endpoint ---

    def update_endpoint(
        self, application_id: str, endpoint_id: str, params: dict[str, Any]
    ) -> None:
        self.get_app(application_id)
        self._ensure_app_stores(application_id)
        if endpoint_id in self.endpoints[application_id]:
            self.endpoints[application_id][endpoint_id].update(params)
        else:
            endpoint = Endpoint(application_id, endpoint_id, params)
            self.endpoints[application_id][endpoint_id] = endpoint

    def update_endpoints_batch(
        self, application_id: str, items: list[dict[str, Any]]
    ) -> dict[str, Any]:
        self.get_app(application_id)
        self._ensure_app_stores(application_id)
        results: dict[str, Any] = {}
        for item in items:
            eid = item.get("Id", _gen_id())
            if eid in self.endpoints[application_id]:
                self.endpoints[application_id][eid].update(item)
            else:
                self.endpoints[application_id][eid] = Endpoint(
                    application_id, eid, item
                )
            results[eid] = {"StatusCode": 202, "Message": "Accepted"}
        return results

    def get_endpoint(self, application_id: str, endpoint_id: str) -> Endpoint:
        self.get_app(application_id)
        self._ensure_app_stores(application_id)
        if endpoint_id not in self.endpoints[application_id]:
            raise EndpointNotFound()
        return self.endpoints[application_id][endpoint_id]

    def delete_endpoint(self, application_id: str, endpoint_id: str) -> Endpoint:
        endpoint = self.get_endpoint(application_id, endpoint_id)
        del self.endpoints[application_id][endpoint_id]
        return endpoint

    def get_user_endpoints(
        self, application_id: str, user_id: str
    ) -> list[dict[str, Any]]:
        self.get_app(application_id)
        self._ensure_app_stores(application_id)
        return [
            ep.to_json()
            for ep in self.endpoints[application_id].values()
            if ep.user_id == user_id
        ]

    def delete_user_endpoints(
        self, application_id: str, user_id: str
    ) -> list[dict[str, Any]]:
        self.get_app(application_id)
        self._ensure_app_stores(application_id)
        to_delete = [
            eid
            for eid, ep in self.endpoints[application_id].items()
            if ep.user_id == user_id
        ]
        results = []
        for eid in to_delete:
            results.append(self.endpoints[application_id].pop(eid).to_json())
        return results

    # --- Export/Import Jobs ---

    def create_export_job(
        self, application_id: str, params: dict[str, Any]
    ) -> ExportJob:
        self.get_app(application_id)
        self._ensure_app_stores(application_id)
        job = ExportJob(application_id, params)
        self.export_jobs[application_id].append(job)
        return job

    def get_export_job(self, application_id: str, job_id: str) -> ExportJob:
        self.get_app(application_id)
        self._ensure_app_stores(application_id)
        for job in self.export_jobs[application_id]:
            if job.job_id == job_id:
                return job
        raise ExportJobNotFound()

    def get_export_jobs(self, application_id: str) -> list[ExportJob]:
        self.get_app(application_id)
        self._ensure_app_stores(application_id)
        return self.export_jobs[application_id]

    def create_import_job(
        self, application_id: str, params: dict[str, Any]
    ) -> ImportJob:
        self.get_app(application_id)
        self._ensure_app_stores(application_id)
        job = ImportJob(application_id, params)
        self.import_jobs[application_id].append(job)
        return job

    def get_import_job(self, application_id: str, job_id: str) -> ImportJob:
        self.get_app(application_id)
        self._ensure_app_stores(application_id)
        for job in self.import_jobs[application_id]:
            if job.job_id == job_id:
                return job
        raise ImportJobNotFound()

    def get_import_jobs(self, application_id: str) -> list[ImportJob]:
        self.get_app(application_id)
        self._ensure_app_stores(application_id)
        return self.import_jobs[application_id]

    # --- Recommender ---

    def create_recommender_configuration(
        self, params: dict[str, Any]
    ) -> RecommenderConfig:
        rec = RecommenderConfig(params)
        self.recommenders[rec.recommender_id] = rec
        return rec

    def get_recommender_configuration(
        self, recommender_id: str
    ) -> RecommenderConfig:
        if recommender_id not in self.recommenders:
            raise RecommenderNotFound()
        return self.recommenders[recommender_id]

    def get_recommender_configurations(self) -> list[RecommenderConfig]:
        return list(self.recommenders.values())

    def update_recommender_configuration(
        self, recommender_id: str, params: dict[str, Any]
    ) -> RecommenderConfig:
        rec = self.get_recommender_configuration(recommender_id)
        rec.update(params)
        return rec

    def delete_recommender_configuration(
        self, recommender_id: str
    ) -> RecommenderConfig:
        rec = self.get_recommender_configuration(recommender_id)
        del self.recommenders[recommender_id]
        return rec

    # --- Events ---

    def put_events(
        self, application_id: str, events: dict[str, Any]
    ) -> dict[str, Any]:
        self.get_app(application_id)
        # Accept events and return success for all
        results: dict[str, Any] = {}
        for batch_id, batch_item in events.items():
            endpoint_results: dict[str, Any] = {}
            for event_id in batch_item.get("Events", {}):
                endpoint_results[event_id] = {
                    "StatusCode": 202,
                    "Message": "Accepted",
                }
            results[batch_id] = {
                "EndpointItemResponse": {"StatusCode": 202, "Message": "Accepted"},
                "EventsItemResponse": endpoint_results,
            }
        return results

    # --- Messages ---

    def send_messages(
        self, application_id: str, message_request: dict[str, Any]
    ) -> dict[str, Any]:
        self.get_app(application_id)
        result: dict[str, Any] = {}
        addresses = message_request.get("Addresses", {})
        for addr in addresses:
            result[addr] = {
                "DeliveryStatus": "SUCCESSFUL",
                "StatusCode": 200,
                "StatusMessage": "Message sent",
            }
        endpoints = message_request.get("Endpoints", {})
        for eid in endpoints:
            result[eid] = {
                "DeliveryStatus": "SUCCESSFUL",
                "StatusCode": 200,
                "StatusMessage": "Message sent",
            }
        return {
            "ApplicationId": application_id,
            "RequestId": _gen_id(),
            "Result": result,
        }

    def send_users_messages(
        self, application_id: str, send_request: dict[str, Any]
    ) -> dict[str, Any]:
        self.get_app(application_id)
        result: dict[str, Any] = {}
        users = send_request.get("Users", {})
        for user_id in users:
            result[user_id] = {
                "default": {
                    "DeliveryStatus": "SUCCESSFUL",
                    "StatusCode": 200,
                    "StatusMessage": "Message sent",
                }
            }
        return {
            "ApplicationId": application_id,
            "RequestId": _gen_id(),
            "Result": result,
        }

    # --- Phone / OTP ---

    def phone_number_validate(
        self, number: str, iso_country_code: str
    ) -> dict[str, Any]:
        return {
            "Carrier": "Unknown",
            "City": "Unknown",
            "CleansedPhoneNumberE164": number,
            "CleansedPhoneNumberNational": number,
            "Country": iso_country_code or "US",
            "CountryCodeIso2": iso_country_code or "US",
            "CountryCodeNumeric": "1",
            "County": "Unknown",
            "OriginalCountryCodeIso2": iso_country_code or "US",
            "OriginalPhoneNumber": number,
            "PhoneType": "MOBILE",
            "PhoneTypeCode": 0,
            "Timezone": "America/New_York",
            "ZipCode": "00000",
        }

    def send_otp_message(
        self, application_id: str, send_request: dict[str, Any]
    ) -> dict[str, Any]:
        self.get_app(application_id)
        return {"MessageId": _gen_id()}

    def verify_otp_message(
        self, application_id: str, verify_request: dict[str, Any]
    ) -> dict[str, Any]:
        self.get_app(application_id)
        return {"Valid": True}

    # --- KPI (stub) ---

    def get_application_date_range_kpi(
        self, application_id: str, kpi_name: str
    ) -> dict[str, Any]:
        self.get_app(application_id)
        return {
            "ApplicationId": application_id,
            "KpiName": kpi_name,
            "KpiResult": {"Rows": []},
            "StartTime": _now_iso(),
            "EndTime": _now_iso(),
        }

    def get_campaign_date_range_kpi(
        self, application_id: str, campaign_id: str, kpi_name: str
    ) -> dict[str, Any]:
        self.get_campaign(application_id, campaign_id)
        return {
            "ApplicationId": application_id,
            "CampaignId": campaign_id,
            "KpiName": kpi_name,
            "KpiResult": {"Rows": []},
            "StartTime": _now_iso(),
            "EndTime": _now_iso(),
        }

    def get_journey_date_range_kpi(
        self, application_id: str, journey_id: str, kpi_name: str
    ) -> dict[str, Any]:
        self.get_journey(application_id, journey_id)
        return {
            "ApplicationId": application_id,
            "JourneyId": journey_id,
            "KpiName": kpi_name,
            "KpiResult": {"Rows": []},
            "StartTime": _now_iso(),
            "EndTime": _now_iso(),
        }

    # --- Journey Metrics (stubs) ---

    def get_journey_execution_metrics(
        self, application_id: str, journey_id: str
    ) -> dict[str, Any]:
        self.get_journey(application_id, journey_id)
        return {
            "ApplicationId": application_id,
            "JourneyId": journey_id,
            "LastEvaluatedTime": _now_iso(),
            "Metrics": {},
        }

    def get_journey_execution_activity_metrics(
        self, application_id: str, journey_id: str, activity_id: str
    ) -> dict[str, Any]:
        self.get_journey(application_id, journey_id)
        return {
            "ApplicationId": application_id,
            "JourneyId": journey_id,
            "JourneyActivityId": activity_id,
            "LastEvaluatedTime": _now_iso(),
            "Metrics": {},
        }

    def get_journey_runs(
        self, application_id: str, journey_id: str
    ) -> list[dict[str, Any]]:
        self.get_journey(application_id, journey_id)
        return []

    def get_journey_run_execution_metrics(
        self, application_id: str, journey_id: str, run_id: str
    ) -> dict[str, Any]:
        self.get_journey(application_id, journey_id)
        return {
            "ApplicationId": application_id,
            "JourneyId": journey_id,
            "RunId": run_id,
            "LastEvaluatedTime": _now_iso(),
            "Metrics": {},
        }

    def get_journey_run_execution_activity_metrics(
        self,
        application_id: str,
        journey_id: str,
        run_id: str,
        activity_id: str,
    ) -> dict[str, Any]:
        self.get_journey(application_id, journey_id)
        return {
            "ApplicationId": application_id,
            "JourneyId": journey_id,
            "RunId": run_id,
            "JourneyActivityId": activity_id,
            "LastEvaluatedTime": _now_iso(),
            "Metrics": {},
        }

    # --- Remove Attributes ---

    def remove_attributes(
        self, application_id: str, attribute_type: str, attributes: list[str]
    ) -> dict[str, Any]:
        self.get_app(application_id)
        return {
            "ApplicationId": application_id,
            "AttributeType": attribute_type,
            "Attributes": attributes,
        }

    # --- In-App Messages ---

    def get_in_app_messages(
        self, application_id: str, endpoint_id: str
    ) -> dict[str, Any]:
        self.get_app(application_id)
        return {"InAppMessageCampaigns": []}


pinpoint_backends = BackendDict(PinpointBackend, "pinpoint")
