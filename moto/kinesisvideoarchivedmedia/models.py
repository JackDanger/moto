from typing import Any, Optional

from moto.core.base_backend import BackendDict, BaseBackend
from moto.kinesisvideo.models import KinesisVideoBackend, kinesisvideo_backends
from moto.sts.utils import random_session_token


class KinesisVideoArchivedMediaBackend(BaseBackend):
    @property
    def backend(self) -> KinesisVideoBackend:
        return kinesisvideo_backends[self.account_id][self.region_name]

    def _get_streaming_url(
        self, stream_name: str, stream_arn: str, api_name: str
    ) -> str:
        stream = self.backend._get_stream(stream_name, stream_arn)
        data_endpoint = stream.get_data_endpoint(api_name)
        session_token = random_session_token()
        api_to_relative_path = {
            "GET_HLS_STREAMING_SESSION_URL": "/hls/v1/getHLSMasterPlaylist.m3u8",
            "GET_DASH_STREAMING_SESSION_URL": "/dash/v1/getDASHManifest.mpd",
        }
        relative_path = api_to_relative_path[api_name]
        return f"{data_endpoint}{relative_path}?SessionToken={session_token}"

    def get_hls_streaming_session_url(self, stream_name: str, stream_arn: str) -> str:
        # Ignore option parameters as the format of hls_url doesn't depend on them
        api_name = "GET_HLS_STREAMING_SESSION_URL"
        return self._get_streaming_url(stream_name, stream_arn, api_name)

    def get_dash_streaming_session_url(self, stream_name: str, stream_arn: str) -> str:
        # Ignore option parameters as the format of hls_url doesn't depend on them
        api_name = "GET_DASH_STREAMING_SESSION_URL"
        return self._get_streaming_url(stream_name, stream_arn, api_name)

    def get_clip(self, stream_name: str, stream_arn: str) -> tuple[str, bytes]:
        self.backend._get_stream(stream_name, stream_arn)
        content_type = "video/mp4"  # Fixed content_type as it depends on input stream
        payload = b"sample-mp4-video"
        return content_type, payload

    def get_images(
        self,
        stream_name: Optional[str],
        stream_arn: Optional[str],
        image_selector_type: str,
        start_timestamp: Optional[Any],
        end_timestamp: Optional[Any],
        sampling_interval: Optional[int],
        format: str,
        format_config: Optional[dict[str, str]],
        width_pixels: Optional[int],
        height_pixels: Optional[int],
        max_local_media_size_in_mb: Optional[int],
        next_token: Optional[str],
    ) -> tuple[list[dict[str, str]], Optional[str]]:
        """Return stub image frames from the stream (no actual video processing)."""
        self.backend._get_stream(stream_name or "", stream_arn or "")
        # Return an empty images list — we don't process actual video data.
        return [], None

    def get_media_for_fragment_list(
        self,
        stream_name: Optional[str],
        stream_arn: Optional[str],
        fragments: list[str],
    ) -> tuple[str, bytes]:
        """Return stub media data for the requested fragments."""
        if stream_name or stream_arn:
            self.backend._get_stream(stream_name or "", stream_arn or "")
        content_type = "video/webm"
        payload = b"sample-webm-media"
        return content_type, payload

    def list_fragments(
        self,
        stream_name: Optional[str],
        stream_arn: Optional[str],
        max_results: Optional[int],
        next_token: Optional[str],
        fragment_selector: Optional[dict[str, Any]],
    ) -> tuple[list[dict[str, Any]], Optional[str]]:
        """Return an empty fragment list — no actual media data is stored."""
        if stream_name or stream_arn:
            self.backend._get_stream(stream_name or "", stream_arn or "")
        return [], None


kinesisvideoarchivedmedia_backends = BackendDict(
    KinesisVideoArchivedMediaBackend, "kinesis-video-archived-media"
)
