import json
from urllib.parse import unquote

from moto.core.responses import ActionResult, BaseResponse, EmptyResult
from moto.core.serialize import never_return

from .models import MediaPackagev2Backend, mediapackagev2_backends


class mediapackagev2Response(BaseResponse):
    """Handler for mediapackagev2 requests and responses."""

    RESPONSE_KEY_PATH_TO_TRANSFORMER = {
        # InputType is only returned on GET
        "CreateChannel.CreateChannelResponse.InputType": never_return
    }

    def __init__(self) -> None:
        super().__init__(service_name="mediapackagev2")

    @property
    def mediapackagev2_backend(self) -> MediaPackagev2Backend:
        return mediapackagev2_backends[self.current_account][self.region]

    def _get_uri_param(self, name: str) -> str:
        """Extract a parameter from the URL path."""
        val = self.parsed_url.path.split("/")
        # Find the param after its key segment
        # URL pattern: /channelGroup/{CG}/channel/{CH}/originEndpoint/{OE}/harvestJob/{HJ}
        segments = {
            "ChannelGroupName": "channelGroup",
            "ChannelName": "channel",
            "OriginEndpointName": "originEndpoint",
            "HarvestJobName": "harvestJob",
            "ResourceArn": "tags",
        }
        key_segment = segments.get(name)
        if key_segment:
            parts = self.parsed_url.path.strip("/").split("/")
            for i, part in enumerate(parts):
                if part == key_segment and i + 1 < len(parts):
                    return unquote(parts[i + 1])
        return ""

    def create_channel_group(self) -> ActionResult:
        channel_group_name = self._get_param("ChannelGroupName")
        description = self._get_param("Description", "")
        tags = self._get_param("Tags")
        group = self.mediapackagev2_backend.create_channel_group(
            channel_group_name=channel_group_name,
            description=description,
            tags=tags,
        )
        return ActionResult(result=group)

    def update_channel_group(self) -> ActionResult:
        channel_group_name = self._get_uri_param("ChannelGroupName")
        description = self._get_param("Description")
        group = self.mediapackagev2_backend.update_channel_group(
            channel_group_name=channel_group_name,
            description=description,
        )
        return ActionResult(result=group)

    def create_channel(self) -> ActionResult:
        channel_group_name = self._get_uri_param("ChannelGroupName")
        channel_name = self._get_param("ChannelName")
        description = self._get_param("Description", "")
        input_type = self._get_param("InputType", "HLS")
        tags = self._get_param("Tags")
        channel = self.mediapackagev2_backend.create_channel(
            channel_group_name=channel_group_name,
            channel_name=channel_name,
            description=description,
            input_type=input_type,
            tags=tags,
        )
        return ActionResult(result=channel)

    def update_channel(self) -> ActionResult:
        channel_group_name = self._get_uri_param("ChannelGroupName")
        channel_name = self._get_uri_param("ChannelName")
        description = self._get_param("Description")
        input_switch_configuration = self._get_param("InputSwitchConfiguration")
        output_header_configuration = self._get_param("OutputHeaderConfiguration")
        channel = self.mediapackagev2_backend.update_channel(
            channel_group_name=channel_group_name,
            channel_name=channel_name,
            description=description,
            input_switch_configuration=input_switch_configuration,
            output_header_configuration=output_header_configuration,
        )
        return ActionResult(result=channel)

    def get_channel_group(self) -> ActionResult:
        channel_group_name = self._get_uri_param("ChannelGroupName")
        group = self.mediapackagev2_backend.get_channel_group(
            channel_group_name=channel_group_name,
        )
        return ActionResult(result=group)

    def list_channel_groups(self) -> ActionResult:
        max_results = self._get_int_param("maxResults")
        next_token = self._get_param("nextToken")

        groups, next_token = self.mediapackagev2_backend.list_channel_groups(
            max_results=max_results,
            next_token=next_token,
        )
        return ActionResult(result={"Items": groups, "NextToken": next_token})

    def get_channel(self) -> ActionResult:
        channel_group_name = self._get_uri_param("ChannelGroupName")
        channel_name = self._get_uri_param("ChannelName")
        channel = self.mediapackagev2_backend.get_channel(
            channel_group_name=channel_group_name,
            channel_name=channel_name,
        )
        return ActionResult(result=channel)

    def list_channels(self) -> ActionResult:
        channel_group_name = self._get_uri_param("ChannelGroupName")
        max_results = self._get_int_param("maxResults")
        next_token = self._get_param("nextToken")
        channels, next_token = self.mediapackagev2_backend.list_channels(
            channel_group_name=channel_group_name,
            max_results=max_results,
            next_token=next_token,
        )
        return ActionResult(result={"Items": channels, "NextToken": next_token})

    def delete_channel_group(self) -> ActionResult:
        channel_group_name = self._get_uri_param("ChannelGroupName")
        self.mediapackagev2_backend.delete_channel_group(
            channel_group_name=channel_group_name
        )
        return EmptyResult()

    def delete_channel(self) -> ActionResult:
        channel_group_name = self._get_uri_param("ChannelGroupName")
        channel_name = self._get_uri_param("ChannelName")
        self.mediapackagev2_backend.delete_channel(
            channel_group_name=channel_group_name,
            channel_name=channel_name,
        )
        return EmptyResult()

    # Channel Policy
    def put_channel_policy(self) -> ActionResult:
        channel_group_name = self._get_uri_param("ChannelGroupName")
        channel_name = self._get_uri_param("ChannelName")
        policy = self._get_param("Policy")
        self.mediapackagev2_backend.put_channel_policy(
            channel_group_name=channel_group_name,
            channel_name=channel_name,
            policy=policy,
        )
        return EmptyResult()

    def get_channel_policy(self) -> ActionResult:
        channel_group_name = self._get_uri_param("ChannelGroupName")
        channel_name = self._get_uri_param("ChannelName")
        result = self.mediapackagev2_backend.get_channel_policy(
            channel_group_name=channel_group_name,
            channel_name=channel_name,
        )
        return ActionResult(result=result)

    def delete_channel_policy(self) -> ActionResult:
        channel_group_name = self._get_uri_param("ChannelGroupName")
        channel_name = self._get_uri_param("ChannelName")
        self.mediapackagev2_backend.delete_channel_policy(
            channel_group_name=channel_group_name,
            channel_name=channel_name,
        )
        return EmptyResult()

    # Origin Endpoints
    def create_origin_endpoint(self) -> ActionResult:
        channel_group_name = self._get_uri_param("ChannelGroupName")
        channel_name = self._get_uri_param("ChannelName")
        origin_endpoint_name = self._get_param("OriginEndpointName")
        container_type = self._get_param("ContainerType")
        segment = self._get_param("Segment")
        description = self._get_param("Description", "")
        startover_window_seconds = self._get_int_param("StartoverWindowSeconds", 0)
        hls_manifests = self._get_param("HlsManifests")
        low_latency_hls_manifests = self._get_param("LowLatencyHlsManifests")
        dash_manifests = self._get_param("DashManifests")
        mss_manifests = self._get_param("MssManifests")
        force_endpoint_error_configuration = self._get_param(
            "ForceEndpointErrorConfiguration"
        )
        tags = self._get_param("Tags")
        endpoint = self.mediapackagev2_backend.create_origin_endpoint(
            channel_group_name=channel_group_name,
            channel_name=channel_name,
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
        return ActionResult(result=endpoint)

    def get_origin_endpoint(self) -> ActionResult:
        channel_group_name = self._get_uri_param("ChannelGroupName")
        channel_name = self._get_uri_param("ChannelName")
        origin_endpoint_name = self._get_uri_param("OriginEndpointName")
        endpoint = self.mediapackagev2_backend.get_origin_endpoint(
            channel_group_name=channel_group_name,
            channel_name=channel_name,
            origin_endpoint_name=origin_endpoint_name,
        )
        return ActionResult(result=endpoint)

    def update_origin_endpoint(self) -> ActionResult:
        channel_group_name = self._get_uri_param("ChannelGroupName")
        channel_name = self._get_uri_param("ChannelName")
        origin_endpoint_name = self._get_uri_param("OriginEndpointName")
        container_type = self._get_param("ContainerType")
        segment = self._get_param("Segment")
        description = self._get_param("Description")
        startover_window_seconds = self._get_int_param("StartoverWindowSeconds")
        hls_manifests = self._get_param("HlsManifests")
        low_latency_hls_manifests = self._get_param("LowLatencyHlsManifests")
        dash_manifests = self._get_param("DashManifests")
        mss_manifests = self._get_param("MssManifests")
        force_endpoint_error_configuration = self._get_param(
            "ForceEndpointErrorConfiguration"
        )
        endpoint = self.mediapackagev2_backend.update_origin_endpoint(
            channel_group_name=channel_group_name,
            channel_name=channel_name,
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
        )
        return ActionResult(result=endpoint)

    def list_origin_endpoints(self) -> ActionResult:
        channel_group_name = self._get_uri_param("ChannelGroupName")
        channel_name = self._get_uri_param("ChannelName")
        max_results = self._get_int_param("maxResults")
        next_token = self._get_param("nextToken")
        endpoints, next_token = self.mediapackagev2_backend.list_origin_endpoints(
            channel_group_name=channel_group_name,
            channel_name=channel_name,
            max_results=max_results,
            next_token=next_token,
        )
        return ActionResult(result={"Items": endpoints, "NextToken": next_token})

    def delete_origin_endpoint(self) -> ActionResult:
        channel_group_name = self._get_uri_param("ChannelGroupName")
        channel_name = self._get_uri_param("ChannelName")
        origin_endpoint_name = self._get_uri_param("OriginEndpointName")
        self.mediapackagev2_backend.delete_origin_endpoint(
            channel_group_name=channel_group_name,
            channel_name=channel_name,
            origin_endpoint_name=origin_endpoint_name,
        )
        return EmptyResult()

    # Origin Endpoint Policy
    def put_origin_endpoint_policy(self) -> ActionResult:
        channel_group_name = self._get_uri_param("ChannelGroupName")
        channel_name = self._get_uri_param("ChannelName")
        origin_endpoint_name = self._get_uri_param("OriginEndpointName")
        policy = self._get_param("Policy")
        cdn_auth_configuration = self._get_param("CdnAuthConfiguration")
        self.mediapackagev2_backend.put_origin_endpoint_policy(
            channel_group_name=channel_group_name,
            channel_name=channel_name,
            origin_endpoint_name=origin_endpoint_name,
            policy=policy,
            cdn_auth_configuration=cdn_auth_configuration,
        )
        return EmptyResult()

    def get_origin_endpoint_policy(self) -> ActionResult:
        channel_group_name = self._get_uri_param("ChannelGroupName")
        channel_name = self._get_uri_param("ChannelName")
        origin_endpoint_name = self._get_uri_param("OriginEndpointName")
        result = self.mediapackagev2_backend.get_origin_endpoint_policy(
            channel_group_name=channel_group_name,
            channel_name=channel_name,
            origin_endpoint_name=origin_endpoint_name,
        )
        return ActionResult(result=result)

    def delete_origin_endpoint_policy(self) -> ActionResult:
        channel_group_name = self._get_uri_param("ChannelGroupName")
        channel_name = self._get_uri_param("ChannelName")
        origin_endpoint_name = self._get_uri_param("OriginEndpointName")
        self.mediapackagev2_backend.delete_origin_endpoint_policy(
            channel_group_name=channel_group_name,
            channel_name=channel_name,
            origin_endpoint_name=origin_endpoint_name,
        )
        return EmptyResult()

    # Harvest Jobs
    def create_harvest_job(self) -> ActionResult:
        channel_group_name = self._get_uri_param("ChannelGroupName")
        channel_name = self._get_uri_param("ChannelName")
        origin_endpoint_name = self._get_uri_param("OriginEndpointName")
        harvested_manifests = self._get_param("HarvestedManifests")
        schedule_configuration = self._get_param("ScheduleConfiguration")
        destination = self._get_param("Destination")
        description = self._get_param("Description", "")
        harvest_job_name = self._get_param("HarvestJobName")
        tags = self._get_param("Tags")
        job = self.mediapackagev2_backend.create_harvest_job(
            channel_group_name=channel_group_name,
            channel_name=channel_name,
            origin_endpoint_name=origin_endpoint_name,
            harvested_manifests=harvested_manifests,
            schedule_configuration=schedule_configuration,
            destination=destination,
            description=description,
            harvest_job_name=harvest_job_name,
            tags=tags,
        )
        return ActionResult(result=job)

    def get_harvest_job(self) -> ActionResult:
        channel_group_name = self._get_uri_param("ChannelGroupName")
        channel_name = self._get_uri_param("ChannelName")
        origin_endpoint_name = self._get_uri_param("OriginEndpointName")
        harvest_job_name = self._get_uri_param("HarvestJobName")
        job = self.mediapackagev2_backend.get_harvest_job(
            channel_group_name=channel_group_name,
            channel_name=channel_name,
            origin_endpoint_name=origin_endpoint_name,
            harvest_job_name=harvest_job_name,
        )
        return ActionResult(result=job)

    def cancel_harvest_job(self) -> ActionResult:
        channel_group_name = self._get_uri_param("ChannelGroupName")
        channel_name = self._get_uri_param("ChannelName")
        origin_endpoint_name = self._get_uri_param("OriginEndpointName")
        harvest_job_name = self._get_uri_param("HarvestJobName")
        self.mediapackagev2_backend.cancel_harvest_job(
            channel_group_name=channel_group_name,
            channel_name=channel_name,
            origin_endpoint_name=origin_endpoint_name,
            harvest_job_name=harvest_job_name,
        )
        return EmptyResult()

    def list_harvest_jobs(self) -> ActionResult:
        channel_group_name = self._get_uri_param("ChannelGroupName")
        channel_name = self._get_param("channelName")
        origin_endpoint_name = self._get_param("originEndpointName")
        status = self._get_param("status")
        jobs = self.mediapackagev2_backend.list_harvest_jobs(
            channel_group_name=channel_group_name,
            channel_name=channel_name,
            origin_endpoint_name=origin_endpoint_name,
            status=status,
        )
        return ActionResult(result={"Items": jobs})

    # Reset operations
    def reset_channel_state(self) -> ActionResult:
        channel_group_name = self._get_uri_param("ChannelGroupName")
        channel_name = self._get_uri_param("ChannelName")
        result = self.mediapackagev2_backend.reset_channel_state(
            channel_group_name=channel_group_name,
            channel_name=channel_name,
        )
        return ActionResult(result=result)

    def reset_origin_endpoint_state(self) -> ActionResult:
        channel_group_name = self._get_uri_param("ChannelGroupName")
        channel_name = self._get_uri_param("ChannelName")
        origin_endpoint_name = self._get_uri_param("OriginEndpointName")
        result = self.mediapackagev2_backend.reset_origin_endpoint_state(
            channel_group_name=channel_group_name,
            channel_name=channel_name,
            origin_endpoint_name=origin_endpoint_name,
        )
        return ActionResult(result=result)

    # Tagging
    def tag_resource(self) -> ActionResult:
        resource_arn = self._get_uri_param("ResourceArn")
        tags = self._get_param("Tags")
        if tags:
            self.mediapackagev2_backend.tag_resource(
                resource_arn=resource_arn,
                tags=tags,
            )
        return EmptyResult()

    def untag_resource(self) -> ActionResult:
        resource_arn = self._get_uri_param("ResourceArn")
        tag_keys = self.querystring.get("tagKeys", [])
        if tag_keys:
            self.mediapackagev2_backend.untag_resource(
                resource_arn=resource_arn,
                tag_keys=tag_keys,
            )
        return EmptyResult()

    def list_tags_for_resource(self) -> ActionResult:
        resource_arn = self._get_uri_param("ResourceArn")
        tags = self.mediapackagev2_backend.list_tags_for_resource(
            resource_arn=resource_arn,
        )
        return ActionResult(result={"Tags": tags})
