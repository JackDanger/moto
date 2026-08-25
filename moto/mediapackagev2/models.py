"""mediapackagev2Backend class with methods for supported APIs."""

from datetime import datetime
from typing import Any, Optional

from moto.core.base_backend import BackendDict, BaseBackend
from moto.core.common_models import BaseModel
from moto.moto_api._internal import mock_random
from moto.utilities.paginator import paginate
from moto.utilities.tagging_service import TaggingService

from .exceptions import (
    ChannelGroupNotEmpty,
    ChannelGroupNotFound,
    ChannelNotFound,
    HarvestJobNotFound,
    OriginEndpointNotFound,
    OriginEndpointPolicyNotFound,
    ChannelPolicyNotFound,
)
from .utils import PAGINATION_MODEL


class OriginEndpoint(BaseModel):
    def __init__(
        self,
        channel: "Channel",
        origin_endpoint_name: str,
        container_type: str,
        segment: Optional[dict[str, Any]] = None,
        description: str = "",
        startover_window_seconds: int = 0,
        hls_manifests: Optional[list[dict[str, Any]]] = None,
        low_latency_hls_manifests: Optional[list[dict[str, Any]]] = None,
        dash_manifests: Optional[list[dict[str, Any]]] = None,
        mss_manifests: Optional[list[dict[str, Any]]] = None,
        force_endpoint_error_configuration: Optional[dict[str, Any]] = None,
        tags: Optional[dict[str, str]] = None,
    ):
        self.channel = channel
        self.channel_group_name = channel.channel_group_name
        self.channel_name = channel.channel_name
        self.origin_endpoint_name = origin_endpoint_name
        self.container_type = container_type
        self.segment = segment or {}
        self.description = description
        self.startover_window_seconds = startover_window_seconds
        self.hls_manifests = hls_manifests or []
        self.low_latency_hls_manifests = low_latency_hls_manifests or []
        self.dash_manifests = dash_manifests or []
        self.mss_manifests = mss_manifests or []
        self.force_endpoint_error_configuration = force_endpoint_error_configuration
        self.tags: dict[str, str] = tags or {}
        self.policy: Optional[str] = None
        self.cdn_auth_configuration: Optional[dict[str, Any]] = None

        self.arn = f"{channel.arn}/originEndpoint/{origin_endpoint_name}"
        now = datetime.now()
        self.created_at = now
        self.modified_at = now
        self.reset_at: Optional[datetime] = None
        self.e_tag = mock_random.get_random_hex(10)

        self.harvest_jobs: dict[str, "HarvestJob"] = {}


class HarvestJob(BaseModel):
    def __init__(
        self,
        endpoint: OriginEndpoint,
        harvest_job_name: str,
        harvested_manifests: dict[str, Any],
        schedule_configuration: dict[str, Any],
        destination: dict[str, Any],
        description: str = "",
        tags: Optional[dict[str, str]] = None,
    ):
        self.endpoint = endpoint
        self.channel_group_name = endpoint.channel_group_name
        self.channel_name = endpoint.channel_name
        self.origin_endpoint_name = endpoint.origin_endpoint_name
        self.harvest_job_name = harvest_job_name
        self.harvested_manifests = harvested_manifests
        self.schedule_configuration = schedule_configuration
        self.destination = destination
        self.description = description
        self.tags: dict[str, str] = tags or {}

        self.arn = f"{endpoint.arn}/harvestJob/{harvest_job_name}"
        now = datetime.now()
        self.created_at = now
        self.modified_at = now
        self.status = "QUEUED"
        self.error_message = ""
        self.e_tag = mock_random.get_random_hex(10)


class Channel(BaseModel):
    def __init__(self, group: "ChannelGroup", channel_name: str, description: str = "",
                 input_type: str = "HLS", tags: Optional[dict[str, str]] = None):
        self.group = group
        self.channel_group_name = group.channel_group_name
        self.channel_name = channel_name
        self.arn = f"{group.arn}/channel/{channel_name}"
        self.description = description

        ingest_domain1 = group.egress_domain.replace(".egress", "-1.ingest")
        ingest_domain2 = group.egress_domain.replace(".egress", "-2.ingest")
        self.ingest_endpoints = [
            {
                "Id": "1",
                "Url": f"https://{ingest_domain1}/in/v1/{group.channel_group_name}/1/{channel_name}/index",
            },
            {
                "Id": "2",
                "Url": f"https://{ingest_domain2}/in/v1/{group.channel_group_name}/2/{channel_name}/index",
            },
        ]

        self.e_tag = mock_random.get_random_hex(10)
        self.tags: dict[str, str] = tags or {}

        self.input_switch_configuration: dict[str, Any] = {"MQCSInputSwitching": False}
        self.output_header_configuration: dict[str, Any] = {"PublishMQCS": False}

        self.input_type = input_type
        self.policy: Optional[str] = None

        now = datetime.now()
        self.created_at = now
        self.modified_at = now

        self.origin_endpoints: dict[str, OriginEndpoint] = {}


class ChannelGroup(BaseModel):
    def __init__(
        self,
        account_id: str,
        region_name: str,
        channel_group_name: str,
        description: str = "",
        tags: Optional[dict[str, str]] = None,
    ):
        self.channel_group_name = channel_group_name
        self.arn = f"arn:aws:mediapackagev2:{region_name}:{account_id}:channelGroup/{channel_group_name}"
        self.egress_domain = f"{mock_random.get_random_hex(6)}.egress.{mock_random.get_random_hex(6)}.mediapackagev2.{region_name}.amazonaws.com"
        now = datetime.now()
        self.created_at = now
        self.modified_at = now
        self.e_tag = mock_random.get_random_hex(10)
        self.description = description
        self.tags: dict[str, str] = tags or {}

        self.channels: dict[str, Channel] = {}

    def create_channel(self, channel_name: str, **kwargs: Any) -> Channel:
        channel = Channel(group=self, channel_name=channel_name, **kwargs)
        self.channels[channel_name] = channel
        return channel


class MediaPackagev2Backend(BaseBackend):
    def __init__(self, region_name: str, account_id: str):
        super().__init__(region_name, account_id)
        self.channel_groups: dict[str, ChannelGroup] = {}
        self.tagger = TaggingService()

    def create_channel_group(
        self,
        channel_group_name: str,
        description: str = "",
        tags: Optional[dict[str, str]] = None,
    ) -> ChannelGroup:
        group = ChannelGroup(
            account_id=self.account_id,
            region_name=self.region_name,
            channel_group_name=channel_group_name,
            description=description,
            tags=tags,
        )
        self.channel_groups[channel_group_name] = group
        if tags:
            self.tagger.tag_resource(group.arn, [{"Key": k, "Value": v} for k, v in tags.items()])
        return group

    def update_channel_group(
        self,
        channel_group_name: str,
        description: Optional[str] = None,
    ) -> ChannelGroup:
        group = self.get_channel_group(channel_group_name)
        if description is not None:
            group.description = description
        group.modified_at = datetime.now()
        group.e_tag = mock_random.get_random_hex(10)
        return group

    def create_channel(
        self,
        channel_group_name: str,
        channel_name: str,
        description: str = "",
        input_type: str = "HLS",
        tags: Optional[dict[str, str]] = None,
    ) -> Channel:
        group = self.get_channel_group(channel_group_name)
        channel = group.create_channel(
            channel_name,
            description=description,
            input_type=input_type,
            tags=tags,
        )
        if tags:
            self.tagger.tag_resource(
                channel.arn, [{"Key": k, "Value": v} for k, v in tags.items()]
            )
        return channel

    def update_channel(
        self,
        channel_group_name: str,
        channel_name: str,
        description: Optional[str] = None,
        input_switch_configuration: Optional[dict[str, Any]] = None,
        output_header_configuration: Optional[dict[str, Any]] = None,
    ) -> Channel:
        channel = self.get_channel(channel_group_name, channel_name)
        if description is not None:
            channel.description = description
        if input_switch_configuration is not None:
            channel.input_switch_configuration = input_switch_configuration
        if output_header_configuration is not None:
            channel.output_header_configuration = output_header_configuration
        channel.modified_at = datetime.now()
        channel.e_tag = mock_random.get_random_hex(10)
        return channel

    def get_channel_group(self, channel_group_name: str) -> ChannelGroup:
        if channel_group_name not in self.channel_groups:
            raise ChannelGroupNotFound
        return self.channel_groups[channel_group_name]

    @paginate(PAGINATION_MODEL)
    def list_channel_groups(self) -> list[ChannelGroup]:
        return list(self.channel_groups.values())

    def get_channel(self, channel_group_name: str, channel_name: str) -> Channel:
        group = self.get_channel_group(channel_group_name)
        if channel_name not in group.channels:
            raise ChannelNotFound
        return group.channels[channel_name]

    @paginate(PAGINATION_MODEL)
    def list_channels(self, channel_group_name: str) -> list[Channel]:
        group = self.get_channel_group(channel_group_name)
        return list(group.channels.values())

    def delete_channel_group(self, channel_group_name: str) -> None:
        if channel := self.channel_groups.get(channel_group_name):
            if channel.channels:
                raise ChannelGroupNotEmpty
        self.channel_groups.pop(channel_group_name, None)

    def delete_channel(self, channel_group_name: str, channel_name: str) -> None:
        group = self.get_channel_group(channel_group_name)
        group.channels.pop(channel_name, None)

    # Channel Policy
    def put_channel_policy(
        self, channel_group_name: str, channel_name: str, policy: str
    ) -> None:
        channel = self.get_channel(channel_group_name, channel_name)
        channel.policy = policy

    def get_channel_policy(
        self, channel_group_name: str, channel_name: str
    ) -> dict[str, Any]:
        channel = self.get_channel(channel_group_name, channel_name)
        if channel.policy is None:
            raise ChannelPolicyNotFound
        return {
            "ChannelGroupName": channel_group_name,
            "ChannelName": channel_name,
            "Policy": channel.policy,
        }

    def delete_channel_policy(
        self, channel_group_name: str, channel_name: str
    ) -> None:
        channel = self.get_channel(channel_group_name, channel_name)
        channel.policy = None

    # Origin Endpoints
    def create_origin_endpoint(
        self,
        channel_group_name: str,
        channel_name: str,
        origin_endpoint_name: str,
        container_type: str,
        segment: Optional[dict[str, Any]] = None,
        description: str = "",
        startover_window_seconds: int = 0,
        hls_manifests: Optional[list[dict[str, Any]]] = None,
        low_latency_hls_manifests: Optional[list[dict[str, Any]]] = None,
        dash_manifests: Optional[list[dict[str, Any]]] = None,
        mss_manifests: Optional[list[dict[str, Any]]] = None,
        force_endpoint_error_configuration: Optional[dict[str, Any]] = None,
        tags: Optional[dict[str, str]] = None,
    ) -> OriginEndpoint:
        channel = self.get_channel(channel_group_name, channel_name)
        endpoint = OriginEndpoint(
            channel=channel,
            origin_endpoint_name=origin_endpoint_name,
            container_type=container_type,
            segment=segment,
            description=description,
            startover_window_seconds=startover_window_seconds,
            hls_manifests=hls_manifests,
            low_latency_hls_manifests=low_latency_hls_manifests,
            dash_manifests=dash_manifests,
            mss_manifests=mss_manifests,
            force_endpoint_error_configuration=force_endpoint_error_configuration,
            tags=tags,
        )
        channel.origin_endpoints[origin_endpoint_name] = endpoint
        if tags:
            self.tagger.tag_resource(
                endpoint.arn, [{"Key": k, "Value": v} for k, v in tags.items()]
            )
        return endpoint

    def get_origin_endpoint(
        self,
        channel_group_name: str,
        channel_name: str,
        origin_endpoint_name: str,
    ) -> OriginEndpoint:
        channel = self.get_channel(channel_group_name, channel_name)
        if origin_endpoint_name not in channel.origin_endpoints:
            raise OriginEndpointNotFound
        return channel.origin_endpoints[origin_endpoint_name]

    def update_origin_endpoint(
        self,
        channel_group_name: str,
        channel_name: str,
        origin_endpoint_name: str,
        container_type: Optional[str] = None,
        segment: Optional[dict[str, Any]] = None,
        description: Optional[str] = None,
        startover_window_seconds: Optional[int] = None,
        hls_manifests: Optional[list[dict[str, Any]]] = None,
        low_latency_hls_manifests: Optional[list[dict[str, Any]]] = None,
        dash_manifests: Optional[list[dict[str, Any]]] = None,
        mss_manifests: Optional[list[dict[str, Any]]] = None,
        force_endpoint_error_configuration: Optional[dict[str, Any]] = None,
    ) -> OriginEndpoint:
        endpoint = self.get_origin_endpoint(
            channel_group_name, channel_name, origin_endpoint_name
        )
        if container_type is not None:
            endpoint.container_type = container_type
        if segment is not None:
            endpoint.segment = segment
        if description is not None:
            endpoint.description = description
        if startover_window_seconds is not None:
            endpoint.startover_window_seconds = startover_window_seconds
        if hls_manifests is not None:
            endpoint.hls_manifests = hls_manifests
        if low_latency_hls_manifests is not None:
            endpoint.low_latency_hls_manifests = low_latency_hls_manifests
        if dash_manifests is not None:
            endpoint.dash_manifests = dash_manifests
        if mss_manifests is not None:
            endpoint.mss_manifests = mss_manifests
        if force_endpoint_error_configuration is not None:
            endpoint.force_endpoint_error_configuration = (
                force_endpoint_error_configuration
            )
        endpoint.modified_at = datetime.now()
        endpoint.e_tag = mock_random.get_random_hex(10)
        return endpoint

    @paginate(PAGINATION_MODEL)
    def list_origin_endpoints(
        self, channel_group_name: str, channel_name: str
    ) -> list[OriginEndpoint]:
        channel = self.get_channel(channel_group_name, channel_name)
        return list(channel.origin_endpoints.values())

    def delete_origin_endpoint(
        self,
        channel_group_name: str,
        channel_name: str,
        origin_endpoint_name: str,
    ) -> None:
        channel = self.get_channel(channel_group_name, channel_name)
        channel.origin_endpoints.pop(origin_endpoint_name, None)

    # Origin Endpoint Policy
    def put_origin_endpoint_policy(
        self,
        channel_group_name: str,
        channel_name: str,
        origin_endpoint_name: str,
        policy: str,
        cdn_auth_configuration: Optional[dict[str, Any]] = None,
    ) -> None:
        endpoint = self.get_origin_endpoint(
            channel_group_name, channel_name, origin_endpoint_name
        )
        endpoint.policy = policy
        if cdn_auth_configuration is not None:
            endpoint.cdn_auth_configuration = cdn_auth_configuration

    def get_origin_endpoint_policy(
        self,
        channel_group_name: str,
        channel_name: str,
        origin_endpoint_name: str,
    ) -> dict[str, Any]:
        endpoint = self.get_origin_endpoint(
            channel_group_name, channel_name, origin_endpoint_name
        )
        if endpoint.policy is None:
            raise OriginEndpointPolicyNotFound
        result: dict[str, Any] = {
            "ChannelGroupName": channel_group_name,
            "ChannelName": channel_name,
            "OriginEndpointName": origin_endpoint_name,
            "Policy": endpoint.policy,
        }
        if endpoint.cdn_auth_configuration:
            result["CdnAuthConfiguration"] = endpoint.cdn_auth_configuration
        return result

    def delete_origin_endpoint_policy(
        self,
        channel_group_name: str,
        channel_name: str,
        origin_endpoint_name: str,
    ) -> None:
        endpoint = self.get_origin_endpoint(
            channel_group_name, channel_name, origin_endpoint_name
        )
        endpoint.policy = None
        endpoint.cdn_auth_configuration = None

    # Harvest Jobs
    def create_harvest_job(
        self,
        channel_group_name: str,
        channel_name: str,
        origin_endpoint_name: str,
        harvested_manifests: dict[str, Any],
        schedule_configuration: dict[str, Any],
        destination: dict[str, Any],
        description: str = "",
        harvest_job_name: Optional[str] = None,
        tags: Optional[dict[str, str]] = None,
    ) -> HarvestJob:
        endpoint = self.get_origin_endpoint(
            channel_group_name, channel_name, origin_endpoint_name
        )
        if not harvest_job_name:
            harvest_job_name = mock_random.get_random_hex(12)
        job = HarvestJob(
            endpoint=endpoint,
            harvest_job_name=harvest_job_name,
            harvested_manifests=harvested_manifests,
            schedule_configuration=schedule_configuration,
            destination=destination,
            description=description,
            tags=tags,
        )
        endpoint.harvest_jobs[harvest_job_name] = job
        if tags:
            self.tagger.tag_resource(
                job.arn, [{"Key": k, "Value": v} for k, v in tags.items()]
            )
        return job

    def get_harvest_job(
        self,
        channel_group_name: str,
        channel_name: str,
        origin_endpoint_name: str,
        harvest_job_name: str,
    ) -> HarvestJob:
        endpoint = self.get_origin_endpoint(
            channel_group_name, channel_name, origin_endpoint_name
        )
        if harvest_job_name not in endpoint.harvest_jobs:
            raise HarvestJobNotFound
        return endpoint.harvest_jobs[harvest_job_name]

    def cancel_harvest_job(
        self,
        channel_group_name: str,
        channel_name: str,
        origin_endpoint_name: str,
        harvest_job_name: str,
    ) -> None:
        job = self.get_harvest_job(
            channel_group_name, channel_name, origin_endpoint_name, harvest_job_name
        )
        job.status = "CANCELLED"
        job.modified_at = datetime.now()

    def list_harvest_jobs(
        self,
        channel_group_name: str,
        channel_name: Optional[str] = None,
        origin_endpoint_name: Optional[str] = None,
        status: Optional[str] = None,
    ) -> list[HarvestJob]:
        group = self.get_channel_group(channel_group_name)
        jobs: list[HarvestJob] = []
        for ch in group.channels.values():
            if channel_name and ch.channel_name != channel_name:
                continue
            for ep in ch.origin_endpoints.values():
                if origin_endpoint_name and ep.origin_endpoint_name != origin_endpoint_name:
                    continue
                for job in ep.harvest_jobs.values():
                    if status and job.status != status:
                        continue
                    jobs.append(job)
        return jobs

    # Reset operations
    def reset_channel_state(
        self, channel_group_name: str, channel_name: str
    ) -> dict[str, Any]:
        channel = self.get_channel(channel_group_name, channel_name)
        now = datetime.now()
        return {
            "ChannelGroupName": channel_group_name,
            "ChannelName": channel_name,
            "Arn": channel.arn,
            "ResetAt": now.isoformat(),
        }

    def reset_origin_endpoint_state(
        self,
        channel_group_name: str,
        channel_name: str,
        origin_endpoint_name: str,
    ) -> dict[str, Any]:
        endpoint = self.get_origin_endpoint(
            channel_group_name, channel_name, origin_endpoint_name
        )
        now = datetime.now()
        endpoint.reset_at = now
        return {
            "ChannelGroupName": channel_group_name,
            "ChannelName": channel_name,
            "OriginEndpointName": origin_endpoint_name,
            "Arn": endpoint.arn,
            "ResetAt": now.isoformat(),
        }

    # Tagging
    def tag_resource(self, resource_arn: str, tags: dict[str, str]) -> None:
        self.tagger.tag_resource(
            resource_arn, [{"Key": k, "Value": v} for k, v in tags.items()]
        )

    def untag_resource(self, resource_arn: str, tag_keys: list[str]) -> None:
        self.tagger.untag_resource_using_names(resource_arn, tag_keys)

    def list_tags_for_resource(self, resource_arn: str) -> dict[str, str]:
        tag_list = self.tagger.list_tags_for_resource(resource_arn).get("Tags", [])
        return {t["Key"]: t["Value"] for t in tag_list}


mediapackagev2_backends = BackendDict(MediaPackagev2Backend, "mediapackagev2")
