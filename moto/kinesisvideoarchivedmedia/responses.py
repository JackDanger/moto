import json

from moto.core.responses import BaseResponse

from .models import KinesisVideoArchivedMediaBackend, kinesisvideoarchivedmedia_backends


class KinesisVideoArchivedMediaResponse(BaseResponse):
    def __init__(self) -> None:
        super().__init__(service_name="kinesis-video-archived-media")

    @property
    def kinesisvideoarchivedmedia_backend(self) -> KinesisVideoArchivedMediaBackend:
        return kinesisvideoarchivedmedia_backends[self.current_account][self.region]

    def get_hls_streaming_session_url(self) -> str:
        stream_name = self._get_param("StreamName")
        stream_arn = self._get_param("StreamARN")
        hls_streaming_session_url = (
            self.kinesisvideoarchivedmedia_backend.get_hls_streaming_session_url(
                stream_name=stream_name, stream_arn=stream_arn
            )
        )
        return json.dumps({"HLSStreamingSessionURL": hls_streaming_session_url})

    def get_dash_streaming_session_url(self) -> str:
        stream_name = self._get_param("StreamName")
        stream_arn = self._get_param("StreamARN")
        dash_streaming_session_url = (
            self.kinesisvideoarchivedmedia_backend.get_dash_streaming_session_url(
                stream_name=stream_name, stream_arn=stream_arn
            )
        )
        return json.dumps({"DASHStreamingSessionURL": dash_streaming_session_url})

    def get_clip(self) -> tuple[bytes, dict[str, str]]:
        stream_name = self._get_param("StreamName")
        stream_arn = self._get_param("StreamARN")
        content_type, payload = self.kinesisvideoarchivedmedia_backend.get_clip(
            stream_name=stream_name, stream_arn=stream_arn
        )
        new_headers = {"Content-Type": content_type}
        return payload, new_headers

    def get_images(self) -> str:
        stream_name = self._get_param("StreamName")
        stream_arn = self._get_param("StreamARN")
        image_selector_type = self._get_param("ImageSelectorType", "SERVER_TIMESTAMP")
        start_timestamp = self._get_param("StartTimestamp")
        end_timestamp = self._get_param("EndTimestamp")
        sampling_interval = self._get_param("SamplingInterval")
        format_ = self._get_param("Format", "JPEG")
        format_config = self._get_param("FormatConfig")
        width_pixels = self._get_param("WidthPixels")
        height_pixels = self._get_param("HeightPixels")
        max_local_media_size_in_mb = self._get_param("MaxLocalMediaSizeInMB")
        next_token = self._get_param("NextToken")
        images, new_next_token = self.kinesisvideoarchivedmedia_backend.get_images(
            stream_name=stream_name,
            stream_arn=stream_arn,
            image_selector_type=image_selector_type,
            start_timestamp=start_timestamp,
            end_timestamp=end_timestamp,
            sampling_interval=sampling_interval,
            format=format_,
            format_config=format_config,
            width_pixels=width_pixels,
            height_pixels=height_pixels,
            max_local_media_size_in_mb=max_local_media_size_in_mb,
            next_token=next_token,
        )
        result: dict = {"Images": images}
        if new_next_token is not None:
            result["NextToken"] = new_next_token
        return json.dumps(result)

    def get_media_for_fragment_list(self) -> tuple[bytes, dict[str, str]]:
        stream_name = self._get_param("StreamName")
        stream_arn = self._get_param("StreamARN")
        fragments = self._get_param("Fragments", [])
        content_type, payload = (
            self.kinesisvideoarchivedmedia_backend.get_media_for_fragment_list(
                stream_name=stream_name,
                stream_arn=stream_arn,
                fragments=fragments,
            )
        )
        new_headers = {"Content-Type": content_type}
        return payload, new_headers

    def list_fragments(self) -> str:
        stream_name = self._get_param("StreamName")
        stream_arn = self._get_param("StreamARN")
        max_results = self._get_param("MaxResults")
        next_token = self._get_param("NextToken")
        fragment_selector = self._get_param("FragmentSelector")
        fragments, new_next_token = self.kinesisvideoarchivedmedia_backend.list_fragments(
            stream_name=stream_name,
            stream_arn=stream_arn,
            max_results=max_results,
            next_token=next_token,
            fragment_selector=fragment_selector,
        )
        result: dict = {"Fragments": fragments}
        if new_next_token is not None:
            result["NextToken"] = new_next_token
        return json.dumps(result)
