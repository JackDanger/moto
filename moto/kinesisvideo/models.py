from typing import Any, Optional

from moto.core.base_backend import BackendDict, BaseBackend
from moto.core.common_models import BaseModel
from moto.core.utils import utcnow
from moto.moto_api._internal import mock_random as random
from moto.utilities.utils import get_partition

from .exceptions import (
    AccessDeniedException,
    ResourceInUseException,
    ResourceNotFoundException,
)


class Stream(BaseModel):
    def __init__(
        self,
        account_id: str,
        region_name: str,
        device_name: str,
        stream_name: str,
        media_type: str,
        kms_key_id: str,
        data_retention_in_hours: int,
        tags: dict[str, str],
    ):
        self.region_name = region_name
        self.stream_name = stream_name
        self.device_name = device_name
        self.media_type = media_type
        self.kms_key_id = kms_key_id
        self.data_retention_in_hours = data_retention_in_hours
        self.tags = tags or {}
        self.status = "ACTIVE"
        self.version = random.get_random_string(include_digits=False, lower_case=True)
        self.creation_time = utcnow()
        stream_arn = f"arn:{get_partition(region_name)}:kinesisvideo:{region_name}:{account_id}:stream/{stream_name}/1598784211076"
        self.data_endpoint_number = random.get_random_hex()
        self.arn = stream_arn

    def get_data_endpoint(self, api_name: str) -> str:
        data_endpoint_prefix = "s-" if api_name in ("PUT_MEDIA", "GET_MEDIA") else "b-"
        return f"https://{data_endpoint_prefix}{self.data_endpoint_number}.kinesisvideo.{self.region_name}.amazonaws.com"

    def to_dict(self) -> dict[str, Any]:
        return {
            "DeviceName": self.device_name,
            "StreamName": self.stream_name,
            "StreamARN": self.arn,
            "MediaType": self.media_type,
            "KmsKeyId": self.kms_key_id,
            "Version": self.version,
            "Status": self.status,
            "CreationTime": self.creation_time,
            "DataRetentionInHours": self.data_retention_in_hours,
        }


class SignalingChannel(BaseModel):
    def __init__(
        self,
        account_id: str,
        region_name: str,
        channel_name: str,
        channel_type: str,
        single_master_configuration: Optional[dict[str, Any]],
        tags: Optional[list[dict[str, str]]],
    ):
        self.region_name = region_name
        self.channel_name = channel_name
        self.channel_type = channel_type or "SINGLE_MASTER"
        self.single_master_configuration = single_master_configuration or {
            "MessageTtlSeconds": 60
        }
        self.tags_list = tags or []
        self.tags: dict[str, str] = {t["Key"]: t["Value"] for t in self.tags_list}
        self.status = "ACTIVE"
        self.version = random.get_random_string(include_digits=False, lower_case=True)
        self.creation_time = utcnow()
        channel_id = random.get_random_hex(8)
        self.arn = f"arn:{get_partition(region_name)}:kinesisvideo:{region_name}:{account_id}:channel/{channel_name}/{channel_id}"

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {
            "ChannelName": self.channel_name,
            "ChannelARN": self.arn,
            "ChannelType": self.channel_type,
            "ChannelStatus": self.status,
            "CreationTime": self.creation_time,
            "Version": self.version,
        }
        if self.single_master_configuration:
            result["SingleMasterConfiguration"] = self.single_master_configuration
        return result


class KinesisVideoBackend(BaseBackend):
    def __init__(self, region_name: str, account_id: str):
        super().__init__(region_name, account_id)
        self.streams: dict[str, Stream] = {}
        self.signaling_channels: dict[str, SignalingChannel] = {}
        self.tags_store: dict[str, dict[str, str]] = {}

    def create_stream(
        self,
        device_name: str,
        stream_name: str,
        media_type: str,
        kms_key_id: str,
        data_retention_in_hours: int,
        tags: dict[str, str],
    ) -> str:
        streams = [s for s in self.streams.values() if s.stream_name == stream_name]
        if len(streams) > 0:
            raise ResourceInUseException(f"The stream {stream_name} already exists.")
        stream = Stream(
            self.account_id, self.region_name, device_name, stream_name,
            media_type, kms_key_id, data_retention_in_hours, tags,
        )
        self.streams[stream.arn] = stream
        if tags:
            self.tags_store[stream.arn] = dict(tags)
        return stream.arn

    def _get_stream(self, stream_name: str, stream_arn: str) -> Stream:
        if stream_name:
            streams = [s for s in self.streams.values() if s.stream_name == stream_name]
            if len(streams) == 0:
                raise ResourceNotFoundException()
            return streams[0]
        if not (stream := self.streams.get(stream_arn)):
            raise ResourceNotFoundException()
        return stream

    def describe_stream(self, stream_name: str, stream_arn: str) -> dict[str, Any]:
        stream = self._get_stream(stream_name, stream_arn)
        return stream.to_dict()

    def update_stream(
        self, stream_name: Optional[str], stream_arn: Optional[str],
        current_version: str, device_name: Optional[str], media_type: Optional[str],
    ) -> None:
        stream = self._get_stream(stream_name or "", stream_arn or "")
        if current_version != stream.version:
            raise AccessDeniedException("The stream version does not match the current version.")
        if device_name is not None:
            stream.device_name = device_name
        if media_type is not None:
            stream.media_type = media_type
        stream.version = random.get_random_string(include_digits=False, lower_case=True)

    def list_streams(self) -> list[dict[str, Any]]:
        return [s.to_dict() for s in self.streams.values()]

    def delete_stream(self, stream_arn: str) -> None:
        stream = self.streams.get(stream_arn)
        if stream is None:
            raise ResourceNotFoundException()
        del self.streams[stream_arn]
        self.tags_store.pop(stream_arn, None)

    def get_data_endpoint(self, stream_name: str, stream_arn: str, api_name: str) -> str:
        stream = self._get_stream(stream_name, stream_arn)
        return stream.get_data_endpoint(api_name)

    def create_signaling_channel(
        self, channel_name: str, channel_type: Optional[str],
        single_master_configuration: Optional[dict[str, Any]],
        tags: Optional[list[dict[str, str]]],
    ) -> str:
        for ch in self.signaling_channels.values():
            if ch.channel_name == channel_name:
                raise ResourceInUseException(f"The signaling channel {channel_name} already exists.")
        channel = SignalingChannel(
            self.account_id, self.region_name, channel_name,
            channel_type or "SINGLE_MASTER", single_master_configuration, tags,
        )
        self.signaling_channels[channel.arn] = channel
        if channel.tags:
            self.tags_store[channel.arn] = dict(channel.tags)
        return channel.arn

    def _get_signaling_channel(
        self, channel_name: Optional[str] = None, channel_arn: Optional[str] = None,
    ) -> SignalingChannel:
        if channel_arn:
            ch = self.signaling_channels.get(channel_arn)
            if ch:
                return ch
        if channel_name:
            for ch in self.signaling_channels.values():
                if ch.channel_name == channel_name:
                    return ch
        raise ResourceNotFoundException(message="The signaling channel was not found.")

    def describe_signaling_channel(
        self, channel_name: Optional[str], channel_arn: Optional[str],
    ) -> dict[str, Any]:
        channel = self._get_signaling_channel(channel_name, channel_arn)
        return channel.to_dict()

    def update_signaling_channel(
        self, channel_arn: str, current_version: str,
        single_master_configuration: Optional[dict[str, Any]],
    ) -> None:
        channel = self._get_signaling_channel(channel_arn=channel_arn)
        if current_version != channel.version:
            raise AccessDeniedException("The channel version does not match the current version.")
        if single_master_configuration is not None:
            channel.single_master_configuration = single_master_configuration
        channel.version = random.get_random_string(include_digits=False, lower_case=True)

    def delete_signaling_channel(self, channel_arn: str) -> None:
        channel = self._get_signaling_channel(channel_arn=channel_arn)
        del self.signaling_channels[channel.arn]
        self.tags_store.pop(channel.arn, None)

    def list_signaling_channels(
        self, channel_name_condition: Optional[dict[str, str]] = None,
    ) -> list[dict[str, Any]]:
        channels = list(self.signaling_channels.values())
        if channel_name_condition:
            operator = channel_name_condition.get("ComparisonOperator", "BEGINS_WITH")
            value = channel_name_condition.get("ComparisonValue", "")
            if operator == "BEGINS_WITH":
                channels = [c for c in channels if c.channel_name.startswith(value)]
        return [c.to_dict() for c in channels]

    def tag_stream(
        self, stream_arn: Optional[str], stream_name: Optional[str], tags: dict[str, str],
    ) -> None:
        stream = self._get_stream(stream_name or "", stream_arn or "")
        stream.tags.update(tags)
        self.tags_store.setdefault(stream.arn, {}).update(tags)

    def untag_stream(
        self, stream_arn: Optional[str], stream_name: Optional[str], tag_key_list: list[str],
    ) -> None:
        stream = self._get_stream(stream_name or "", stream_arn or "")
        for key in tag_key_list:
            stream.tags.pop(key, None)
            if stream.arn in self.tags_store:
                self.tags_store[stream.arn].pop(key, None)

    def list_tags_for_stream(
        self, stream_arn: Optional[str], stream_name: Optional[str],
    ) -> dict[str, str]:
        stream = self._get_stream(stream_name or "", stream_arn or "")
        return stream.tags

    def tag_resource(self, resource_arn: str, tags: list[dict[str, str]]) -> None:
        tags_dict = {t["Key"]: t["Value"] for t in tags}
        if resource_arn in self.streams:
            self.streams[resource_arn].tags.update(tags_dict)
        elif resource_arn in self.signaling_channels:
            self.signaling_channels[resource_arn].tags.update(tags_dict)
            self.signaling_channels[resource_arn].tags_list.extend(tags)
        else:
            raise ResourceNotFoundException(message=f"Resource {resource_arn} not found")
        self.tags_store.setdefault(resource_arn, {}).update(tags_dict)

    def untag_resource(self, resource_arn: str, tag_key_list: list[str]) -> None:
        if resource_arn in self.streams:
            for key in tag_key_list:
                self.streams[resource_arn].tags.pop(key, None)
        elif resource_arn in self.signaling_channels:
            for key in tag_key_list:
                self.signaling_channels[resource_arn].tags.pop(key, None)
            self.signaling_channels[resource_arn].tags_list = [
                t for t in self.signaling_channels[resource_arn].tags_list
                if t["Key"] not in tag_key_list
            ]
        else:
            raise ResourceNotFoundException(message=f"Resource {resource_arn} not found")
        if resource_arn in self.tags_store:
            for key in tag_key_list:
                self.tags_store[resource_arn].pop(key, None)

    def list_tags_for_resource(self, resource_arn: str) -> dict[str, str]:
        if resource_arn in self.streams:
            return self.streams[resource_arn].tags
        if resource_arn in self.signaling_channels:
            return self.signaling_channels[resource_arn].tags
        raise ResourceNotFoundException(message=f"Resource {resource_arn} not found")

    def get_signaling_channel_endpoint(
        self, channel_arn: str, single_master_channel_endpoint_configuration: Optional[dict[str, Any]]
    ) -> list[dict[str, str]]:
        for ch in self.signaling_channels.values():
            if ch.arn == channel_arn:
                protocols = ["WSS", "HTTPS"]
                if single_master_channel_endpoint_configuration:
                    protocols = single_master_channel_endpoint_configuration.get("Protocols", protocols)
                return [
                    {"Protocol": p, "ResourceEndpoint": f"https://{ch.arn}.kinesisvideo.{self.region_name}.amazonaws.com"}
                    for p in protocols
                ]
        raise ResourceNotFoundException(message=f"Channel {channel_arn} not found")

    def update_data_retention(
        self,
        stream_name: Optional[str],
        stream_arn: Optional[str],
        current_version: str,
        operation: str,
        data_retention_change_in_hours: int,
    ) -> None:
        stream = self._get_stream(stream_name or "", stream_arn or "")
        if current_version != stream.version:
            raise AccessDeniedException("The stream version does not match the current version.")
        if operation == "INCREASE_DATA_RETENTION":
            stream.data_retention_in_hours = (stream.data_retention_in_hours or 0) + data_retention_change_in_hours
        elif operation == "DECREASE_DATA_RETENTION":
            stream.data_retention_in_hours = max(0, (stream.data_retention_in_hours or 0) - data_retention_change_in_hours)

    def describe_image_generation_configuration(
        self, stream_name: Optional[str], stream_arn: Optional[str]
    ) -> dict[str, Any]:
        stream = self._get_stream(stream_name or "", stream_arn or "")
        return getattr(stream, "image_generation_configuration", {}) or {}

    def describe_notification_configuration(
        self, stream_name: Optional[str], stream_arn: Optional[str]
    ) -> dict[str, Any]:
        stream = self._get_stream(stream_name or "", stream_arn or "")
        return getattr(stream, "notification_configuration", {}) or {}

    def describe_media_storage_configuration(self, channel_arn: str) -> dict[str, Any]:
        for ch in self.signaling_channels.values():
            if ch.arn == channel_arn:
                return getattr(ch, "media_storage_configuration", {}) or {}
        raise ResourceNotFoundException(message=f"Channel {channel_arn} not found")

    def describe_stream_storage_configuration(
        self, stream_name: Optional[str], stream_arn: Optional[str]
    ) -> dict[str, Any]:
        stream = self._get_stream(stream_name or "", stream_arn or "")
        return getattr(stream, "stream_storage_configuration", {}) or {}

    def describe_mapped_resource_configuration(
        self, stream_name: Optional[str], stream_arn: Optional[str]
    ) -> list[dict[str, Any]]:
        stream = self._get_stream(stream_name or "", stream_arn or "")
        return getattr(stream, "mapped_resource_configuration", []) or []


kinesisvideo_backends = BackendDict(KinesisVideoBackend, "kinesisvideo")

    def update_image_generation_configuration(
        self,
        stream_name: Optional[str],
        stream_arn: Optional[str],
        image_generation_configuration: Optional[dict] = None,
    ) -> None:
        stream = self._get_stream(stream_name or "", stream_arn or "")
        stream.image_generation_configuration = image_generation_configuration or {}

    def update_notification_configuration(
        self,
        stream_name: Optional[str],
        stream_arn: Optional[str],
        notification_configuration: Optional[dict] = None,
    ) -> None:
        stream = self._get_stream(stream_name or "", stream_arn or "")
        stream.notification_configuration = notification_configuration or {}
