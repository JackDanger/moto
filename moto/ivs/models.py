"""IVSBackend class with methods for supported APIs."""

from typing import Any, Optional

from moto.core.base_backend import BackendDict, BaseBackend
from moto.ivs.exceptions import ConflictException, ResourceNotFoundException
from moto.moto_api._internal import mock_random
from moto.utilities.paginator import paginate
from moto.utilities.utils import get_partition


class IVSBackend(BaseBackend):
    """Implementation of IVS APIs."""

    PAGINATION_MODEL = {
        "list_channels": {
            "input_token": "next_token",
            "limit_key": "max_results",
            "limit_default": 100,
            "unique_attribute": "arn",
        },
        "list_stream_keys": {
            "input_token": "next_token",
            "limit_key": "max_results",
            "limit_default": 100,
            "unique_attribute": "arn",
        },
        "list_playback_key_pairs": {
            "input_token": "next_token",
            "limit_key": "max_results",
            "limit_default": 100,
            "unique_attribute": "arn",
        },
        "list_recording_configurations": {
            "input_token": "next_token",
            "limit_key": "max_results",
            "limit_default": 100,
            "unique_attribute": "arn",
        },
        "list_playback_restriction_policies": {
            "input_token": "next_token",
            "limit_key": "max_results",
            "limit_default": 100,
            "unique_attribute": "arn",
        },
        "list_streams": {
            "input_token": "next_token",
            "limit_key": "max_results",
            "limit_default": 100,
            "unique_attribute": "channelArn",
        },
        "list_stream_sessions": {
            "input_token": "next_token",
            "limit_key": "max_results",
            "limit_default": 100,
            "unique_attribute": "streamId",
        },
    }

    def __init__(self, region_name: str, account_id: str):
        super().__init__(region_name, account_id)
        self.channels: list[dict[str, Any]] = []
        self.stream_keys: list[dict[str, Any]] = []
        self.playback_key_pairs: list[dict[str, Any]] = []
        self.recording_configurations: list[dict[str, Any]] = []
        self.playback_restriction_policies: dict[str, dict[str, Any]] = {}
        self.streams: list[dict[str, Any]] = []
        self.stream_sessions: dict[str, list[dict[str, Any]]] = {}
        self.tags_store: dict[str, dict[str, str]] = {}

    def _arn_partition(self) -> str:
        return get_partition(self.region_name)

    def create_channel(
        self,
        authorized: bool,
        insecure_ingest: bool,
        latency_mode: str,
        name: str,
        preset: str,
        recording_configuration_arn: str,
        tags: dict[str, str],
        channel_type: str,
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        channel_id = mock_random.get_random_string(12)
        channel_arn = f"arn:{self._arn_partition()}:ivs:{self.region_name}:{self.account_id}:channel/{channel_id}"
        channel = {
            "arn": channel_arn,
            "authorized": authorized,
            "ingestEndpoint": "ingest.example.com",
            "insecureIngest": insecure_ingest,
            "latencyMode": latency_mode,
            "name": name,
            "playbackUrl": f"https://playback.example.com/{self.region_name}.{self.account_id}.{channel_id}.m3u8",
            "preset": preset,
            "recordingConfigurationArn": recording_configuration_arn,
            "tags": tags,
            "type": channel_type,
        }
        self.channels.append(channel)
        if tags:
            self.tags_store[channel_arn] = dict(tags)
        stream_key = self._create_stream_key_internal(channel_arn, tags)
        return channel, stream_key

    def _create_stream_key_internal(
        self, channel_arn: str, tags: Optional[dict[str, str]] = None
    ) -> dict[str, Any]:
        stream_key_id = mock_random.get_random_string(12)
        stream_key_arn = f"arn:{self._arn_partition()}:ivs:{self.region_name}:{self.account_id}:stream-key/{stream_key_id}"
        stream_key = {
            "arn": stream_key_arn,
            "channelArn": channel_arn,
            "tags": tags or {},
            "value": f"sk_{self.region_name}_{mock_random.token_urlsafe(32)}",
        }
        self.stream_keys.append(stream_key)
        if tags:
            self.tags_store[stream_key_arn] = dict(tags)
        return stream_key

    @paginate(pagination_model=PAGINATION_MODEL)  # type: ignore[misc]
    def list_channels(  # type: ignore[misc]
        self,
        filter_by_name: Optional[str],
        filter_by_recording_configuration_arn: Optional[str],
    ) -> list[dict[str, Any]]:
        if filter_by_name is not None:
            channels = [
                channel
                for channel in self.channels
                if channel["name"] == filter_by_name
            ]
        elif filter_by_recording_configuration_arn is not None:
            channels = [
                channel
                for channel in self.channels
                if channel["recordingConfigurationArn"]
                == filter_by_recording_configuration_arn
            ]
        else:
            channels = self.channels
        return channels

    def _find_channel(self, arn: str) -> dict[str, Any]:
        try:
            return next(channel for channel in self.channels if channel["arn"] == arn)
        except StopIteration:
            raise ResourceNotFoundException(f"Resource: {arn} not found")

    def get_channel(self, arn: str) -> dict[str, Any]:
        return self._find_channel(arn)

    def batch_get_channel(
        self, arns: list[str]
    ) -> tuple[list[dict[str, Any]], list[dict[str, str]]]:
        return [channel for channel in self.channels if channel["arn"] in arns], []

    def update_channel(
        self,
        arn: str,
        authorized: Optional[bool],
        insecure_ingest: Optional[bool],
        latency_mode: Optional[str],
        name: Optional[str],
        preset: Optional[str],
        recording_configuration_arn: Optional[str],
        channel_type: Optional[str],
    ) -> dict[str, Any]:
        channel = self._find_channel(arn)
        if authorized is not None:
            channel["authorized"] = authorized
        if insecure_ingest is not None:
            channel["insecureIngest"] = insecure_ingest
        if latency_mode is not None:
            channel["latencyMode"] = latency_mode
        if name is not None:
            channel["name"] = name
        if preset is not None:
            channel["preset"] = preset
        if recording_configuration_arn is not None:
            channel["recordingConfigurationArn"] = recording_configuration_arn
        if channel_type is not None:
            channel["type"] = channel_type
        return channel

    def delete_channel(self, arn: str) -> None:
        self._find_channel(arn)
        self.channels = [channel for channel in self.channels if channel["arn"] != arn]
        self.tags_store.pop(arn, None)
        self.stream_keys = [sk for sk in self.stream_keys if sk["channelArn"] != arn]

    # Stream Key operations

    def create_stream_key(
        self, channel_arn: str, tags: Optional[dict[str, str]] = None
    ) -> dict[str, Any]:
        self._find_channel(channel_arn)
        return self._create_stream_key_internal(channel_arn, tags)

    def get_stream_key(self, arn: str) -> dict[str, Any]:
        try:
            return next(sk for sk in self.stream_keys if sk["arn"] == arn)
        except StopIteration:
            raise ResourceNotFoundException(f"Resource: {arn} not found")

    def delete_stream_key(self, arn: str) -> None:
        self.get_stream_key(arn)
        self.stream_keys = [sk for sk in self.stream_keys if sk["arn"] != arn]
        self.tags_store.pop(arn, None)

    def batch_get_stream_key(
        self, arns: list[str]
    ) -> tuple[list[dict[str, Any]], list[dict[str, str]]]:
        return [sk for sk in self.stream_keys if sk["arn"] in arns], []

    @paginate(pagination_model=PAGINATION_MODEL)  # type: ignore[misc]
    def list_stream_keys(  # type: ignore[misc]
        self,
        channel_arn: str,
    ) -> list[dict[str, Any]]:
        return [sk for sk in self.stream_keys if sk["channelArn"] == channel_arn]

    # Playback Key Pair operations

    def import_playback_key_pair(
        self,
        name: Optional[str],
        public_key_material: str,
        tags: Optional[dict[str, str]] = None,
    ) -> dict[str, Any]:
        pkp_id = mock_random.get_random_string(12)
        pkp_arn = f"arn:{self._arn_partition()}:ivs:{self.region_name}:{self.account_id}:playback-key/{pkp_id}"
        fingerprint = mock_random.get_random_hex(20)
        key_pair = {
            "arn": pkp_arn,
            "fingerprint": fingerprint,
            "name": name or "",
            "tags": tags or {},
        }
        self.playback_key_pairs.append(key_pair)
        if tags:
            self.tags_store[pkp_arn] = dict(tags)
        return key_pair

    def get_playback_key_pair(self, arn: str) -> dict[str, Any]:
        try:
            return next(pkp for pkp in self.playback_key_pairs if pkp["arn"] == arn)
        except StopIteration:
            raise ResourceNotFoundException(f"Resource: {arn} not found")

    def delete_playback_key_pair(self, arn: str) -> None:
        self.get_playback_key_pair(arn)
        self.playback_key_pairs = [
            pkp for pkp in self.playback_key_pairs if pkp["arn"] != arn
        ]
        self.tags_store.pop(arn, None)

    @paginate(pagination_model=PAGINATION_MODEL)  # type: ignore[misc]
    def list_playback_key_pairs(self) -> list[dict[str, Any]]:  # type: ignore[misc]
        return self.playback_key_pairs

    # Recording Configuration operations

    def create_recording_configuration(
        self,
        destination_configuration: dict[str, Any],
        name: Optional[str],
        recording_reconnect_window_seconds: int,
        rendition_configuration: Optional[dict[str, Any]],
        tags: Optional[dict[str, str]],
        thumbnail_configuration: Optional[dict[str, Any]],
    ) -> dict[str, Any]:
        rc_id = mock_random.get_random_string(12)
        rc_arn = f"arn:{self._arn_partition()}:ivs:{self.region_name}:{self.account_id}:recording-configuration/{rc_id}"
        recording_config = {
            "arn": rc_arn,
            "destinationConfiguration": destination_configuration,
            "name": name or "",
            "recordingReconnectWindowSeconds": recording_reconnect_window_seconds,
            "renditionConfiguration": rendition_configuration or {},
            "state": "ACTIVE",
            "tags": tags or {},
            "thumbnailConfiguration": thumbnail_configuration or {},
        }
        self.recording_configurations.append(recording_config)
        if tags:
            self.tags_store[rc_arn] = dict(tags)
        return recording_config

    def get_recording_configuration(self, arn: str) -> dict[str, Any]:
        try:
            return next(rc for rc in self.recording_configurations if rc["arn"] == arn)
        except StopIteration:
            raise ResourceNotFoundException(f"Resource: {arn} not found")

    def delete_recording_configuration(self, arn: str) -> None:
        self.get_recording_configuration(arn)
        for channel in self.channels:
            if channel.get("recordingConfigurationArn") == arn:
                raise ConflictException(
                    f"Recording configuration {arn} is in use by channel {channel['arn']}"
                )
        self.recording_configurations = [
            rc for rc in self.recording_configurations if rc["arn"] != arn
        ]
        self.tags_store.pop(arn, None)

    @paginate(pagination_model=PAGINATION_MODEL)  # type: ignore[misc]
    def list_recording_configurations(  # type: ignore[misc]
        self,
    ) -> list[dict[str, Any]]:
        return self.recording_configurations

    # Playback Restriction Policy operations

    def create_playback_restriction_policy(
        self,
        allowed_countries: Optional[list[str]] = None,
        allowed_origins: Optional[list[str]] = None,
        enable_strict_origin_enforcement: bool = False,
        name: Optional[str] = None,
        tags: Optional[dict[str, str]] = None,
    ) -> dict[str, Any]:
        policy_id = mock_random.get_random_string(12)
        policy_arn = f"arn:{self._arn_partition()}:ivs:{self.region_name}:{self.account_id}:playback-restriction-policy/{policy_id}"
        policy: dict[str, Any] = {
            "arn": policy_arn,
            "name": name or "",
            "allowedCountries": allowed_countries or [],
            "allowedOrigins": allowed_origins or [],
            "enableStrictOriginEnforcement": enable_strict_origin_enforcement,
            "tags": tags or {},
        }
        self.playback_restriction_policies[policy_arn] = policy
        if tags:
            self.tags_store[policy_arn] = dict(tags)
        return policy

    def get_playback_restriction_policy(self, arn: str) -> dict[str, Any]:
        if arn not in self.playback_restriction_policies:
            raise ResourceNotFoundException(f"Resource: {arn} not found")
        return self.playback_restriction_policies[arn]

    def update_playback_restriction_policy(
        self,
        arn: str,
        allowed_countries: Optional[list[str]] = None,
        allowed_origins: Optional[list[str]] = None,
        enable_strict_origin_enforcement: Optional[bool] = None,
        name: Optional[str] = None,
    ) -> dict[str, Any]:
        policy = self.get_playback_restriction_policy(arn)
        if allowed_countries is not None:
            policy["allowedCountries"] = allowed_countries
        if allowed_origins is not None:
            policy["allowedOrigins"] = allowed_origins
        if enable_strict_origin_enforcement is not None:
            policy["enableStrictOriginEnforcement"] = enable_strict_origin_enforcement
        if name is not None:
            policy["name"] = name
        return policy

    def delete_playback_restriction_policy(self, arn: str) -> None:
        self.get_playback_restriction_policy(arn)
        del self.playback_restriction_policies[arn]
        self.tags_store.pop(arn, None)

    @paginate(pagination_model=PAGINATION_MODEL)  # type: ignore[misc]
    def list_playback_restriction_policies(  # type: ignore[misc]
        self,
    ) -> list[dict[str, Any]]:
        return list(self.playback_restriction_policies.values())

    # Stream operations

    @paginate(pagination_model=PAGINATION_MODEL)  # type: ignore[misc]
    def list_streams(  # type: ignore[misc]
        self,
        filter_by: Optional[dict[str, Any]] = None,
    ) -> list[dict[str, Any]]:
        streams = self.streams
        if filter_by:
            health = filter_by.get("health")
            if health:
                streams = [s for s in streams if s.get("health") == health]
        return streams

    def stop_stream(self, channel_arn: str) -> None:
        self._find_channel(channel_arn)
        self.streams = [s for s in self.streams if s.get("channelArn") != channel_arn]

    def put_metadata(self, channel_arn: str, metadata: str) -> None:
        self._find_channel(channel_arn)

    @paginate(pagination_model=PAGINATION_MODEL)  # type: ignore[misc]
    def list_stream_sessions(  # type: ignore[misc]
        self,
        channel_arn: str,
    ) -> list[dict[str, Any]]:
        return self.stream_sessions.get(channel_arn, [])

    def get_stream_session(
        self, channel_arn: str, stream_id: Optional[str] = None
    ) -> dict[str, Any]:
        self._find_channel(channel_arn)
        sessions = self.stream_sessions.get(channel_arn, [])
        if stream_id:
            try:
                session = next(s for s in sessions if s["streamId"] == stream_id)
            except StopIteration:
                raise ResourceNotFoundException(
                    f"Resource: {stream_id} not found"
                )
        elif sessions:
            session = sessions[-1]
        else:
            session = {
                "channelArn": channel_arn,
                "streamId": mock_random.get_random_string(12),
                "startTime": "",
                "endTime": "",
                "health": "HEALTHY",
                "state": "LIVE",
                "truncatedEvents": [],
            }
        return session

    def start_viewer_session_revocation(
        self,
        channel_arn: str,
        viewer_id: str,
        viewer_session_versions_less_than_or_equal_to: Optional[int] = None,
    ) -> None:
        self._find_channel(channel_arn)

    def batch_start_viewer_session_revocation(
        self,
        viewer_sessions: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        errors = []
        for vs in viewer_sessions:
            channel_arn = vs.get("channelArn", "")
            try:
                self._find_channel(channel_arn)
            except ResourceNotFoundException:
                errors.append(
                    {
                        "channelArn": channel_arn,
                        "viewerId": vs.get("viewerId", ""),
                        "code": "ResourceNotFoundException",
                        "message": f"Resource: {channel_arn} not found",
                    }
                )
        return errors

    # Tag operations

    def tag_resource(self, resource_arn: str, tags: dict[str, str]) -> None:
        self._find_resource(resource_arn)
        if resource_arn not in self.tags_store:
            self.tags_store[resource_arn] = {}
        self.tags_store[resource_arn].update(tags)
        resource = self._get_resource_by_arn(resource_arn)
        if resource is not None:
            resource["tags"] = dict(self.tags_store[resource_arn])

    def untag_resource(self, resource_arn: str, tag_keys: list[str]) -> None:
        self._find_resource(resource_arn)
        if resource_arn in self.tags_store:
            for key in tag_keys:
                self.tags_store[resource_arn].pop(key, None)
            resource = self._get_resource_by_arn(resource_arn)
            if resource is not None:
                resource["tags"] = dict(self.tags_store[resource_arn])

    def list_tags_for_resource(self, resource_arn: str) -> dict[str, str]:
        self._find_resource(resource_arn)
        return self.tags_store.get(resource_arn, {})

    def _find_resource(self, arn: str) -> None:
        if self._get_resource_by_arn(arn) is not None:
            return
        raise ResourceNotFoundException(f"Resource: {arn} not found")

    def _get_resource_by_arn(self, arn: str) -> Optional[dict[str, Any]]:
        for channel in self.channels:
            if channel["arn"] == arn:
                return channel
        for sk in self.stream_keys:
            if sk["arn"] == arn:
                return sk
        for pkp in self.playback_key_pairs:
            if pkp["arn"] == arn:
                return pkp
        for rc in self.recording_configurations:
            if rc["arn"] == arn:
                return rc
        if arn in self.playback_restriction_policies:
            return self.playback_restriction_policies[arn]
        return None


ivs_backends = BackendDict(IVSBackend, "ivs")
