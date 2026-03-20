import json

from moto.core.responses import BaseResponse

from .models import MediaPackageBackend, mediapackage_backends


class MediaPackageResponse(BaseResponse):
    def __init__(self) -> None:
        super().__init__(service_name="mediapackage")

    @property
    def mediapackage_backend(self) -> MediaPackageBackend:
        return mediapackage_backends[self.current_account][self.region]

    def create_channel(self) -> str:
        description = self._get_param("description")
        channel_id = self._get_param("id")
        tags = self._get_param("tags")
        channel = self.mediapackage_backend.create_channel(
            description=description, channel_id=channel_id, tags=tags
        )
        return json.dumps(channel.to_dict())

    def list_channels(self) -> str:
        channels = self.mediapackage_backend.list_channels()
        return json.dumps({"channels": channels})

    def describe_channel(self) -> str:
        channel_id = self._get_param("id")
        channel = self.mediapackage_backend.describe_channel(channel_id=channel_id)
        return json.dumps(channel.to_dict())

    def delete_channel(self) -> str:
        channel_id = self._get_param("id")
        channel = self.mediapackage_backend.delete_channel(channel_id=channel_id)
        return json.dumps(channel.to_dict())

    def update_channel(self) -> str:
        channel_id = self._get_param("id")
        description = self._get_param("description")
        channel = self.mediapackage_backend.update_channel(
            channel_id=channel_id, description=description
        )
        return json.dumps(channel.to_dict())

    def create_origin_endpoint(self) -> str:
        authorization = self._get_param("authorization")
        channel_id = self._get_param("channelId")
        cmaf_package = self._get_param("cmafPackage")
        dash_package = self._get_param("dashPackage")
        description = self._get_param("description")
        hls_package = self._get_param("hlsPackage")
        endpoint_id = self._get_param("id")
        manifest_name = self._get_param("manifestName")
        mss_package = self._get_param("mssPackage")
        origination = self._get_param("origination")
        startover_window_seconds = self._get_int_param("startoverWindowSeconds")
        tags = self._get_param("tags")
        time_delay_seconds = self._get_int_param("timeDelaySeconds")
        whitelist = self._get_param("whitelist")
        origin_endpoint = self.mediapackage_backend.create_origin_endpoint(
            authorization=authorization,
            channel_id=channel_id,
            cmaf_package=cmaf_package,
            dash_package=dash_package,
            description=description,
            hls_package=hls_package,
            endpoint_id=endpoint_id,
            manifest_name=manifest_name,
            mss_package=mss_package,
            origination=origination,
            startover_window_seconds=startover_window_seconds,
            tags=tags,
            time_delay_seconds=time_delay_seconds,
            whitelist=whitelist,  # type: ignore[arg-type]
        )
        return json.dumps(origin_endpoint.to_dict())

    def list_origin_endpoints(self) -> str:
        origin_endpoints = self.mediapackage_backend.list_origin_endpoints()
        return json.dumps({"originEndpoints": origin_endpoints})

    def describe_origin_endpoint(self) -> str:
        endpoint_id = self._get_param("id")
        endpoint = self.mediapackage_backend.describe_origin_endpoint(
            endpoint_id=endpoint_id
        )
        return json.dumps(endpoint.to_dict())

    def delete_origin_endpoint(self) -> str:
        endpoint_id = self._get_param("id")
        endpoint = self.mediapackage_backend.delete_origin_endpoint(
            endpoint_id=endpoint_id
        )
        return json.dumps(endpoint.to_dict())

    def update_origin_endpoint(self) -> str:
        authorization = self._get_param("authorization")
        cmaf_package = self._get_param("cmafPackage")
        dash_package = self._get_param("dashPackage")
        description = self._get_param("description")
        hls_package = self._get_param("hlsPackage")
        endpoint_id = self._get_param("id")
        manifest_name = self._get_param("manifestName")
        mss_package = self._get_param("mssPackage")
        origination = self._get_param("origination")
        startover_window_seconds = self._get_int_param("startoverWindowSeconds")
        time_delay_seconds = self._get_int_param("timeDelaySeconds")
        whitelist = self._get_param("whitelist")
        origin_endpoint = self.mediapackage_backend.update_origin_endpoint(
            authorization=authorization,
            cmaf_package=cmaf_package,
            dash_package=dash_package,
            description=description,
            hls_package=hls_package,
            endpoint_id=endpoint_id,
            manifest_name=manifest_name,
            mss_package=mss_package,
            origination=origination,
            startover_window_seconds=startover_window_seconds,
            time_delay_seconds=time_delay_seconds,
            whitelist=whitelist,  # type: ignore[arg-type]
        )
        return json.dumps(origin_endpoint.to_dict())

    def create_harvest_job(self) -> str:
        harvest_job_id = self._get_param("id")
        start_time = self._get_param("startTime")
        end_time = self._get_param("endTime")
        s3_destination = self._get_param("s3Destination")
        origin_endpoint_id = self._get_param("originEndpointId")
        job = self.mediapackage_backend.create_harvest_job(
            harvest_job_id=harvest_job_id,
            start_time=start_time,
            end_time=end_time,
            s3_destination=s3_destination,
            origin_endpoint_id=origin_endpoint_id,
        )
        return json.dumps(job)

    def describe_harvest_job(self) -> str:
        harvest_job_id = self._get_param("id")
        job = self.mediapackage_backend.describe_harvest_job(
            harvest_job_id=harvest_job_id
        )
        return json.dumps(job)

    def list_harvest_jobs(self) -> str:
        jobs = self.mediapackage_backend.list_harvest_jobs()
        return json.dumps({"harvestJobs": jobs})

    def tag_resource(self) -> str:
        resource_arn = self._get_param("resourceArn") or self.path.split("/tags/")[-1]
        tags = self._get_param("tags") or {}
        self.mediapackage_backend.tag_resource(resource_arn=resource_arn, tags=tags)
        return json.dumps({})

    def untag_resource(self) -> str:
        resource_arn = self.path.split("/tags/")[-1]
        tag_keys = self.querystring.get("tagKeys", [])
        self.mediapackage_backend.untag_resource(resource_arn=resource_arn, tag_keys=tag_keys)
        return json.dumps({})

    def list_tags_for_resource(self) -> str:
        resource_arn = self.path.split("/tags/")[-1]
        tags = self.mediapackage_backend.list_tags_for_resource(resource_arn=resource_arn)
        return json.dumps({"tags": tags})
