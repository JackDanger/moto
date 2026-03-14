"""Handles incoming ivs requests, invokes methods, returns responses."""

import json

from moto.core.responses import BaseResponse

from .models import IVSBackend, ivs_backends


class IVSResponse(BaseResponse):
    """Handler for IVS requests and responses."""

    def __init__(self) -> None:
        super().__init__(service_name="ivs")

    @property
    def ivs_backend(self) -> IVSBackend:
        """Return backend instance specific for this region."""
        return ivs_backends[self.current_account][self.region]

    def create_channel(self) -> str:
        authorized = self._get_param("authorized", False)
        insecure_ingest = self._get_param("insecureIngest", False)
        latency_mode = self._get_param("latencyMode", "LOW")
        name = self._get_param("name")
        preset = self._get_param("preset", "")
        recording_configuration_arn = self._get_param("recordingConfigurationArn", "")
        tags = self._get_param("tags", {})
        channel_type = self._get_param("type", "STANDARD")
        channel, stream_key = self.ivs_backend.create_channel(
            authorized=authorized,
            insecure_ingest=insecure_ingest,
            latency_mode=latency_mode,
            name=name,
            preset=preset,
            recording_configuration_arn=recording_configuration_arn,
            tags=tags,
            channel_type=channel_type,
        )
        return json.dumps({"channel": channel, "streamKey": stream_key})

    def list_channels(self) -> str:
        filter_by_name = self._get_param("filterByName")
        filter_by_recording_configuration_arn = self._get_param(
            "filterByRecordingConfigurationArn"
        )
        max_results = self._get_param("maxResults")
        next_token = self._get_param("nextToken")
        channels, next_token = self.ivs_backend.list_channels(
            filter_by_name=filter_by_name,
            filter_by_recording_configuration_arn=filter_by_recording_configuration_arn,
            max_results=max_results,
            next_token=next_token,
        )
        return json.dumps({"channels": channels, "nextToken": next_token})

    def get_channel(self) -> str:
        arn = self._get_param("arn")
        channel = self.ivs_backend.get_channel(arn=arn)
        return json.dumps({"channel": channel})

    def batch_get_channel(self) -> str:
        arns = self._get_param("arns")
        channels, errors = self.ivs_backend.batch_get_channel(arns=arns)
        return json.dumps({"channels": channels, "errors": errors})

    def update_channel(self) -> str:
        arn = self._get_param("arn")
        authorized = self._get_param("authorized")
        insecure_ingest = self._get_param("insecureIngest")
        latency_mode = self._get_param("latencyMode")
        name = self._get_param("name")
        preset = self._get_param("preset")
        recording_configuration_arn = self._get_param("recordingConfigurationArn")
        channel_type = self._get_param("type")
        channel = self.ivs_backend.update_channel(
            arn=arn,
            authorized=authorized,
            insecure_ingest=insecure_ingest,
            latency_mode=latency_mode,
            name=name,
            preset=preset,
            recording_configuration_arn=recording_configuration_arn,
            channel_type=channel_type,
        )
        return json.dumps({"channel": channel})

    def delete_channel(self) -> None:
        arn = self._get_param("arn")
        self.ivs_backend.delete_channel(arn=arn)

    # Stream Key operations

    def create_stream_key(self) -> str:
        channel_arn = self._get_param("channelArn")
        tags = self._get_param("tags", {})
        stream_key = self.ivs_backend.create_stream_key(
            channel_arn=channel_arn,
            tags=tags,
        )
        return json.dumps({"streamKey": stream_key})

    def get_stream_key(self) -> str:
        arn = self._get_param("arn")
        stream_key = self.ivs_backend.get_stream_key(arn=arn)
        return json.dumps({"streamKey": stream_key})

    def delete_stream_key(self) -> None:
        arn = self._get_param("arn")
        self.ivs_backend.delete_stream_key(arn=arn)

    def batch_get_stream_key(self) -> str:
        arns = self._get_param("arns")
        stream_keys, errors = self.ivs_backend.batch_get_stream_key(arns=arns)
        return json.dumps({"streamKeys": stream_keys, "errors": errors})

    def list_stream_keys(self) -> str:
        channel_arn = self._get_param("channelArn")
        max_results = self._get_param("maxResults")
        next_token = self._get_param("nextToken")
        stream_keys, next_token = self.ivs_backend.list_stream_keys(
            channel_arn=channel_arn,
            max_results=max_results,
            next_token=next_token,
        )
        return json.dumps({"streamKeys": stream_keys, "nextToken": next_token})

    # Playback Key Pair operations

    def import_playback_key_pair(self) -> str:
        name = self._get_param("name")
        public_key_material = self._get_param("publicKeyMaterial")
        tags = self._get_param("tags", {})
        key_pair = self.ivs_backend.import_playback_key_pair(
            name=name,
            public_key_material=public_key_material,
            tags=tags,
        )
        return json.dumps({"keyPair": key_pair})

    def get_playback_key_pair(self) -> str:
        arn = self._get_param("arn")
        key_pair = self.ivs_backend.get_playback_key_pair(arn=arn)
        return json.dumps({"keyPair": key_pair})

    def delete_playback_key_pair(self) -> None:
        arn = self._get_param("arn")
        self.ivs_backend.delete_playback_key_pair(arn=arn)

    def list_playback_key_pairs(self) -> str:
        max_results = self._get_param("maxResults")
        next_token = self._get_param("nextToken")
        key_pairs, next_token = self.ivs_backend.list_playback_key_pairs(
            max_results=max_results,
            next_token=next_token,
        )
        return json.dumps({"keyPairs": key_pairs, "nextToken": next_token})

    # Playback Restriction Policy operations

    def create_playback_restriction_policy(self) -> str:
        allowed_countries = self._get_param("allowedCountries", [])
        allowed_origins = self._get_param("allowedOrigins", [])
        enable_strict_origin_enforcement = self._get_param(
            "enableStrictOriginEnforcement", False
        )
        name = self._get_param("name")
        tags = self._get_param("tags", {})
        policy = self.ivs_backend.create_playback_restriction_policy(
            allowed_countries=allowed_countries,
            allowed_origins=allowed_origins,
            enable_strict_origin_enforcement=enable_strict_origin_enforcement,
            name=name,
            tags=tags,
        )
        return json.dumps({"playbackRestrictionPolicy": policy})

    def get_playback_restriction_policy(self) -> str:
        arn = self._get_param("arn")
        policy = self.ivs_backend.get_playback_restriction_policy(arn=arn)
        return json.dumps({"playbackRestrictionPolicy": policy})

    def update_playback_restriction_policy(self) -> str:
        arn = self._get_param("arn")
        allowed_countries = self._get_param("allowedCountries")
        allowed_origins = self._get_param("allowedOrigins")
        enable_strict_origin_enforcement = self._get_param(
            "enableStrictOriginEnforcement"
        )
        name = self._get_param("name")
        policy = self.ivs_backend.update_playback_restriction_policy(
            arn=arn,
            allowed_countries=allowed_countries,
            allowed_origins=allowed_origins,
            enable_strict_origin_enforcement=enable_strict_origin_enforcement,
            name=name,
        )
        return json.dumps({"playbackRestrictionPolicy": policy})

    def delete_playback_restriction_policy(self) -> tuple[str, dict[str, int]]:
        arn = self._get_param("arn")
        self.ivs_backend.delete_playback_restriction_policy(arn=arn)
        return "", {"status": 204}

    # Recording Configuration operations

    def create_recording_configuration(self) -> str:
        destination_configuration = self._get_param("destinationConfiguration")
        name = self._get_param("name")
        recording_reconnect_window_seconds = self._get_param(
            "recordingReconnectWindowSeconds", 0
        )
        rendition_configuration = self._get_param("renditionConfiguration")
        tags = self._get_param("tags", {})
        thumbnail_configuration = self._get_param("thumbnailConfiguration")
        recording_config = self.ivs_backend.create_recording_configuration(
            destination_configuration=destination_configuration,
            name=name,
            recording_reconnect_window_seconds=recording_reconnect_window_seconds,
            rendition_configuration=rendition_configuration,
            tags=tags,
            thumbnail_configuration=thumbnail_configuration,
        )
        return json.dumps({"recordingConfiguration": recording_config})

    def get_recording_configuration(self) -> str:
        arn = self._get_param("arn")
        recording_config = self.ivs_backend.get_recording_configuration(arn=arn)
        return json.dumps({"recordingConfiguration": recording_config})

    def delete_recording_configuration(self) -> None:
        arn = self._get_param("arn")
        self.ivs_backend.delete_recording_configuration(arn=arn)

    def list_recording_configurations(self) -> str:
        max_results = self._get_param("maxResults")
        next_token = self._get_param("nextToken")
        configs, next_token = self.ivs_backend.list_recording_configurations(
            max_results=max_results,
            next_token=next_token,
        )
        return json.dumps({"recordingConfigurations": configs, "nextToken": next_token})

    # Tag operations

    def tag_resource(self) -> None:
        resource_arn = self._get_param("resourceArn")
        if not resource_arn:
            resource_arn = (
                self.path.split("/tags/")[-1] if "/tags/" in self.path else ""
            )
        tags = self._get_param("tags", {})
        self.ivs_backend.tag_resource(resource_arn=resource_arn, tags=tags)

    def untag_resource(self) -> None:
        resource_arn = self._get_param("resourceArn")
        if not resource_arn:
            resource_arn = (
                self.path.split("/tags/")[-1] if "/tags/" in self.path else ""
            )
        tag_keys = self._get_param("tagKeys", [])
        if not tag_keys:
            tag_keys = self.querystring.get("tagKeys", [])
        self.ivs_backend.untag_resource(resource_arn=resource_arn, tag_keys=tag_keys)

    def list_tags_for_resource(self) -> str:
        resource_arn = self._get_param("resourceArn")
        if not resource_arn:
            resource_arn = (
                self.path.split("/tags/")[-1] if "/tags/" in self.path else ""
            )
        tags = self.ivs_backend.list_tags_for_resource(resource_arn=resource_arn)
        return json.dumps({"tags": tags})
