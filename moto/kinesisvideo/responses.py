from moto.core.responses import ActionResult, BaseResponse, EmptyResult

from .models import KinesisVideoBackend, kinesisvideo_backends


class KinesisVideoResponse(BaseResponse):
    def __init__(self) -> None:
        super().__init__(service_name="kinesisvideo")

    @property
    def kinesisvideo_backend(self) -> KinesisVideoBackend:
        return kinesisvideo_backends[self.current_account][self.region]

    def create_stream(self) -> ActionResult:
        device_name = self._get_param("DeviceName")
        stream_name = self._get_param("StreamName")
        media_type = self._get_param("MediaType")
        kms_key_id = self._get_param("KmsKeyId")
        data_retention_in_hours = self._get_int_param("DataRetentionInHours")
        tags = self._get_param("Tags")
        stream_arn = self.kinesisvideo_backend.create_stream(
            device_name=device_name, stream_name=stream_name, media_type=media_type,
            kms_key_id=kms_key_id, data_retention_in_hours=data_retention_in_hours, tags=tags,
        )
        return ActionResult({"StreamARN": stream_arn})

    def describe_stream(self) -> ActionResult:
        stream_name = self._get_param("StreamName")
        stream_arn = self._get_param("StreamARN")
        stream_info = self.kinesisvideo_backend.describe_stream(
            stream_name=stream_name, stream_arn=stream_arn
        )
        return ActionResult({"StreamInfo": stream_info})

    def update_stream(self) -> ActionResult:
        stream_name = self._get_param("StreamName")
        stream_arn = self._get_param("StreamARN")
        current_version = self._get_param("CurrentVersion")
        device_name = self._get_param("DeviceName")
        media_type = self._get_param("MediaType")
        self.kinesisvideo_backend.update_stream(
            stream_name=stream_name, stream_arn=stream_arn,
            current_version=current_version, device_name=device_name, media_type=media_type,
        )
        return EmptyResult()

    def list_streams(self) -> ActionResult:
        stream_info_list = self.kinesisvideo_backend.list_streams()
        return ActionResult({"StreamInfoList": stream_info_list, "NextToken": None})

    def delete_stream(self) -> ActionResult:
        stream_arn = self._get_param("StreamARN")
        self.kinesisvideo_backend.delete_stream(stream_arn=stream_arn)
        return EmptyResult()

    def get_data_endpoint(self) -> ActionResult:
        stream_name = self._get_param("StreamName")
        stream_arn = self._get_param("StreamARN")
        api_name = self._get_param("APIName")
        data_endpoint = self.kinesisvideo_backend.get_data_endpoint(
            stream_name=stream_name, stream_arn=stream_arn, api_name=api_name
        )
        return ActionResult({"DataEndpoint": data_endpoint})

    def create_signaling_channel(self) -> ActionResult:
        channel_name = self._get_param("ChannelName")
        channel_type = self._get_param("ChannelType")
        single_master_configuration = self._get_param("SingleMasterConfiguration")
        tags = self._get_param("Tags")
        channel_arn = self.kinesisvideo_backend.create_signaling_channel(
            channel_name=channel_name, channel_type=channel_type,
            single_master_configuration=single_master_configuration, tags=tags,
        )
        return ActionResult({"ChannelARN": channel_arn})

    def describe_signaling_channel(self) -> ActionResult:
        channel_name = self._get_param("ChannelName")
        channel_arn = self._get_param("ChannelARN")
        channel_info = self.kinesisvideo_backend.describe_signaling_channel(
            channel_name=channel_name, channel_arn=channel_arn
        )
        return ActionResult({"ChannelInfo": channel_info})

    def update_signaling_channel(self) -> ActionResult:
        channel_arn = self._get_param("ChannelARN")
        current_version = self._get_param("CurrentVersion")
        single_master_configuration = self._get_param("SingleMasterConfiguration")
        self.kinesisvideo_backend.update_signaling_channel(
            channel_arn=channel_arn, current_version=current_version,
            single_master_configuration=single_master_configuration,
        )
        return EmptyResult()

    def delete_signaling_channel(self) -> ActionResult:
        channel_arn = self._get_param("ChannelARN")
        self.kinesisvideo_backend.delete_signaling_channel(channel_arn=channel_arn)
        return EmptyResult()

    def list_signaling_channels(self) -> ActionResult:
        channel_name_condition = self._get_param("ChannelNameCondition")
        channel_info_list = self.kinesisvideo_backend.list_signaling_channels(
            channel_name_condition=channel_name_condition
        )
        return ActionResult({"ChannelInfoList": channel_info_list, "NextToken": None})

    def tag_stream(self) -> ActionResult:
        stream_arn = self._get_param("StreamARN")
        stream_name = self._get_param("StreamName")
        tags = self._get_param("Tags")
        self.kinesisvideo_backend.tag_stream(
            stream_arn=stream_arn, stream_name=stream_name, tags=tags
        )
        return EmptyResult()

    def untag_stream(self) -> ActionResult:
        stream_arn = self._get_param("StreamARN")
        stream_name = self._get_param("StreamName")
        tag_key_list = self._get_param("TagKeyList")
        self.kinesisvideo_backend.untag_stream(
            stream_arn=stream_arn, stream_name=stream_name, tag_key_list=tag_key_list
        )
        return EmptyResult()

    def list_tags_for_stream(self) -> ActionResult:
        stream_arn = self._get_param("StreamARN")
        stream_name = self._get_param("StreamName")
        tags = self.kinesisvideo_backend.list_tags_for_stream(
            stream_arn=stream_arn, stream_name=stream_name
        )
        return ActionResult({"Tags": tags})

    def tag_resource(self) -> ActionResult:
        resource_arn = self._get_param("ResourceARN")
        tags = self._get_param("Tags")
        self.kinesisvideo_backend.tag_resource(resource_arn=resource_arn, tags=tags)
        return EmptyResult()

    def untag_resource(self) -> ActionResult:
        resource_arn = self._get_param("ResourceARN")
        tag_key_list = self._get_param("TagKeyList")
        self.kinesisvideo_backend.untag_resource(resource_arn=resource_arn, tag_key_list=tag_key_list)
        return EmptyResult()

    def list_tags_for_resource(self) -> ActionResult:
        resource_arn = self._get_param("ResourceARN")
        tags = self.kinesisvideo_backend.list_tags_for_resource(resource_arn=resource_arn)
        return ActionResult({"Tags": tags})

    def get_signaling_channel_endpoint(self) -> ActionResult:
        channel_arn = self._get_param("ChannelARN")
        config = self._get_param("SingleMasterChannelEndpointConfiguration")
        endpoints = self.kinesisvideo_backend.get_signaling_channel_endpoint(
            channel_arn=channel_arn,
            single_master_channel_endpoint_configuration=config,
        )
        return ActionResult({"ResourceEndpointList": endpoints})

    def update_data_retention(self) -> ActionResult:
        stream_name = self._get_param("StreamName")
        stream_arn = self._get_param("StreamARN")
        current_version = self._get_param("CurrentVersion")
        operation = self._get_param("Operation")
        change = self._get_param("DataRetentionChangeInHours")
        self.kinesisvideo_backend.update_data_retention(
            stream_name=stream_name,
            stream_arn=stream_arn,
            current_version=current_version,
            operation=operation,
            data_retention_change_in_hours=change,
        )
        return EmptyResult()

    def describe_image_generation_configuration(self) -> ActionResult:
        stream_name = self._get_param("StreamName")
        stream_arn = self._get_param("StreamARN")
        config = self.kinesisvideo_backend.describe_image_generation_configuration(
            stream_name=stream_name, stream_arn=stream_arn
        )
        return ActionResult({"ImageGenerationConfiguration": config})

    def describe_notification_configuration(self) -> ActionResult:
        stream_name = self._get_param("StreamName")
        stream_arn = self._get_param("StreamARN")
        config = self.kinesisvideo_backend.describe_notification_configuration(
            stream_name=stream_name, stream_arn=stream_arn
        )
        return ActionResult({"NotificationConfiguration": config})

    def describe_media_storage_configuration(self) -> ActionResult:
        channel_arn = self._get_param("ChannelARN")
        config = self.kinesisvideo_backend.describe_media_storage_configuration(
            channel_arn=channel_arn
        )
        return ActionResult({"MediaStorageConfiguration": config})

    def describe_stream_storage_configuration(self) -> ActionResult:
        stream_name = self._get_param("StreamName")
        stream_arn = self._get_param("StreamARN")
        config = self.kinesisvideo_backend.describe_stream_storage_configuration(
            stream_name=stream_name, stream_arn=stream_arn
        )
        return ActionResult({"StreamStorageConfigurations": config})

    def describe_mapped_resource_configuration(self) -> ActionResult:
        stream_name = self._get_param("StreamName")
        stream_arn = self._get_param("StreamARN")
        configs = self.kinesisvideo_backend.describe_mapped_resource_configuration(
            stream_name=stream_name, stream_arn=stream_arn
        )
        return ActionResult({"MappedResourceConfigurationList": configs})

    def update_image_generation_configuration(self) -> ActionResult:
        stream_name = self._get_param("StreamName")
        stream_arn = self._get_param("StreamARN")
        config = self._get_param("ImageGenerationConfiguration")
        self.kinesisvideo_backend.update_image_generation_configuration(
            stream_name=stream_name,
            stream_arn=stream_arn,
            image_generation_configuration=config,
        )
        return ActionResult({})

    def update_notification_configuration(self) -> ActionResult:
        stream_name = self._get_param("StreamName")
        stream_arn = self._get_param("StreamARN")
        config = self._get_param("NotificationConfiguration")
        self.kinesisvideo_backend.update_notification_configuration(
            stream_name=stream_name,
            stream_arn=stream_arn,
            notification_configuration=config,
        )
        return ActionResult({})

    def delete_edge_configuration(self) -> ActionResult:
        return ActionResult({})

    def start_edge_configuration_update(self) -> ActionResult:
        return ActionResult({"EdgeConfig": {}, "CreationTime": "2023-01-01T00:00:00Z", "LastUpdatedTime": "2023-01-01T00:00:00Z", "SyncStatus": "ACKNOWLEDGED"})

    def update_media_storage_configuration(self) -> ActionResult:
        return ActionResult({})

    def update_stream_storage_configuration(self) -> ActionResult:
        return ActionResult({})

    def describe_edge_configuration(self) -> ActionResult:
        return ActionResult({"EdgeConfig": {}, "CreationTime": "2023-01-01T00:00:00Z", "LastUpdatedTime": "2023-01-01T00:00:00Z", "SyncStatus": "ACKNOWLEDGED"})

    def list_edge_agent_configurations(self) -> ActionResult:
        return ActionResult({"EdgeConfigs": []})
