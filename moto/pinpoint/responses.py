"""Handles incoming pinpoint requests, invokes methods, returns responses."""

import json
from urllib.parse import unquote

from moto.core.common_types import TYPE_RESPONSE
from moto.core.responses import BaseResponse

from .models import PinpointBackend, pinpoint_backends


class PinpointResponse(BaseResponse):
    """Handler for Pinpoint requests and responses."""

    def __init__(self) -> None:
        super().__init__(service_name="pinpoint")

    @property
    def pinpoint_backend(self) -> PinpointBackend:
        """Return backend instance specific for this region."""
        return pinpoint_backends[self.current_account][self.region]

    # --- App ---

    def create_app(self) -> TYPE_RESPONSE:
        params = json.loads(self.body)
        name = params.get("Name")
        tags = params.get("tags", {})
        app = self.pinpoint_backend.create_app(name=name, tags=tags)
        return 201, {"status": 201}, json.dumps(app.to_json())

    def delete_app(self) -> str:
        application_id = self.path.split("/")[-1]
        app = self.pinpoint_backend.delete_app(application_id=application_id)
        return json.dumps(app.to_json())

    def get_app(self) -> str:
        application_id = self.path.split("/")[-1]
        app = self.pinpoint_backend.get_app(application_id=application_id)
        return json.dumps(app.to_json())

    def get_apps(self) -> str:
        apps = self.pinpoint_backend.get_apps()
        resp = {"Item": [a.to_json() for a in apps]}
        return json.dumps(resp)

    def update_application_settings(self) -> str:
        application_id = self.path.split("/")[-2]
        settings = json.loads(self.body)
        app_settings = self.pinpoint_backend.update_application_settings(
            application_id=application_id, settings=settings
        )
        response = app_settings.to_json()
        response["ApplicationId"] = application_id
        return json.dumps(response)

    def get_application_settings(self) -> str:
        application_id = self.path.split("/")[-2]
        app_settings = self.pinpoint_backend.get_application_settings(
            application_id=application_id
        )
        response = app_settings.to_json()
        response["ApplicationId"] = application_id
        return json.dumps(response)

    # --- Tags ---

    def list_tags_for_resource(self) -> str:
        resource_arn = unquote(self.path).split("/tags/")[-1]
        tags = self.pinpoint_backend.list_tags_for_resource(resource_arn=resource_arn)
        return json.dumps(tags)

    def tag_resource(self) -> str:
        resource_arn = unquote(self.path).split("/tags/")[-1]
        tags = json.loads(self.body).get("tags", {})
        self.pinpoint_backend.tag_resource(resource_arn=resource_arn, tags=tags)
        return "{}"

    def untag_resource(self) -> str:
        resource_arn = unquote(self.path).split("/tags/")[-1]
        tag_keys = self.querystring.get("tagKeys")
        self.pinpoint_backend.untag_resource(
            resource_arn=resource_arn,
            tag_keys=tag_keys,  # type: ignore[arg-type]
        )
        return "{}"

    # --- Event Stream ---

    def put_event_stream(self) -> str:
        application_id = self.path.split("/")[-2]
        params = json.loads(self.body)
        stream_arn = params.get("DestinationStreamArn")
        role_arn = params.get("RoleArn")
        event_stream = self.pinpoint_backend.put_event_stream(
            application_id=application_id, stream_arn=stream_arn, role_arn=role_arn
        )
        resp = event_stream.to_json()
        resp["ApplicationId"] = application_id
        return json.dumps(resp)

    def get_event_stream(self) -> str:
        application_id = self.path.split("/")[-2]
        event_stream = self.pinpoint_backend.get_event_stream(
            application_id=application_id
        )
        resp = event_stream.to_json()
        resp["ApplicationId"] = application_id
        return json.dumps(resp)

    def delete_event_stream(self) -> str:
        application_id = self.path.split("/")[-2]
        event_stream = self.pinpoint_backend.delete_event_stream(
            application_id=application_id
        )
        resp = event_stream.to_json()
        resp["ApplicationId"] = application_id
        return json.dumps(resp)

    # --- Campaign ---

    def create_campaign(self) -> TYPE_RESPONSE:
        # /v1/apps/{app-id}/campaigns
        application_id = self.path.split("/")[-2]
        params = json.loads(self.body)
        campaign = self.pinpoint_backend.create_campaign(
            application_id=application_id, params=params
        )
        return 201, {"status": 201}, json.dumps(campaign.to_json())

    def get_campaign(self) -> str:
        # /v1/apps/{app-id}/campaigns/{campaign-id}
        parts = self.path.split("/")
        application_id = parts[-3]
        campaign_id = parts[-1]
        campaign = self.pinpoint_backend.get_campaign(
            application_id=application_id, campaign_id=campaign_id
        )
        return json.dumps(campaign.to_json())

    def get_campaigns(self) -> str:
        # /v1/apps/{app-id}/campaigns
        application_id = self.path.split("/")[-2]
        campaigns = self.pinpoint_backend.get_campaigns(
            application_id=application_id
        )
        return json.dumps({"Item": [c.to_json() for c in campaigns]})

    def update_campaign(self) -> str:
        # /v1/apps/{app-id}/campaigns/{campaign-id}
        parts = self.path.split("/")
        application_id = parts[-3]
        campaign_id = parts[-1]
        params = json.loads(self.body)
        campaign = self.pinpoint_backend.update_campaign(
            application_id=application_id, campaign_id=campaign_id, params=params
        )
        return json.dumps(campaign.to_json())

    def delete_campaign(self) -> str:
        parts = self.path.split("/")
        application_id = parts[-3]
        campaign_id = parts[-1]
        campaign = self.pinpoint_backend.delete_campaign(
            application_id=application_id, campaign_id=campaign_id
        )
        return json.dumps(campaign.to_json())

    def get_campaign_version(self) -> str:
        # /v1/apps/{app-id}/campaigns/{campaign-id}/versions/{version}
        parts = self.path.split("/")
        application_id = parts[-5]
        campaign_id = parts[-3]
        version = int(parts[-1])
        result = self.pinpoint_backend.get_campaign_version(
            application_id=application_id,
            campaign_id=campaign_id,
            version=version,
        )
        return json.dumps(result)

    def get_campaign_versions(self) -> str:
        # /v1/apps/{app-id}/campaigns/{campaign-id}/versions
        parts = self.path.split("/")
        application_id = parts[-4]
        campaign_id = parts[-2]
        versions = self.pinpoint_backend.get_campaign_versions(
            application_id=application_id, campaign_id=campaign_id
        )
        return json.dumps({"Item": versions})

    def get_campaign_activities(self) -> str:
        # /v1/apps/{app-id}/campaigns/{campaign-id}/activities
        parts = self.path.split("/")
        application_id = parts[-4]
        campaign_id = parts[-2]
        activities = self.pinpoint_backend.get_campaign_activities(
            application_id=application_id, campaign_id=campaign_id
        )
        return json.dumps({"Item": activities})

    def get_campaign_date_range_kpi(self) -> str:
        # /v1/apps/{app-id}/campaigns/{campaign-id}/kpis/daterange/{kpi-name}
        parts = self.path.split("/")
        application_id = parts[-6]
        campaign_id = parts[-4]
        kpi_name = parts[-1]
        result = self.pinpoint_backend.get_campaign_date_range_kpi(
            application_id=application_id,
            campaign_id=campaign_id,
            kpi_name=kpi_name,
        )
        return json.dumps(result)

    # --- Segment ---

    def create_segment(self) -> TYPE_RESPONSE:
        application_id = self.path.split("/")[-2]
        params = json.loads(self.body)
        segment = self.pinpoint_backend.create_segment(
            application_id=application_id, params=params
        )
        return 201, {"status": 201}, json.dumps(segment.to_json())

    def get_segment(self) -> str:
        parts = self.path.split("/")
        application_id = parts[-3]
        segment_id = parts[-1]
        segment = self.pinpoint_backend.get_segment(
            application_id=application_id, segment_id=segment_id
        )
        return json.dumps(segment.to_json())

    def get_segments(self) -> str:
        application_id = self.path.split("/")[-2]
        segments = self.pinpoint_backend.get_segments(
            application_id=application_id
        )
        return json.dumps({"Item": [s.to_json() for s in segments]})

    def update_segment(self) -> str:
        parts = self.path.split("/")
        application_id = parts[-3]
        segment_id = parts[-1]
        params = json.loads(self.body)
        segment = self.pinpoint_backend.update_segment(
            application_id=application_id, segment_id=segment_id, params=params
        )
        return json.dumps(segment.to_json())

    def delete_segment(self) -> str:
        parts = self.path.split("/")
        application_id = parts[-3]
        segment_id = parts[-1]
        segment = self.pinpoint_backend.delete_segment(
            application_id=application_id, segment_id=segment_id
        )
        return json.dumps(segment.to_json())

    def get_segment_version(self) -> str:
        parts = self.path.split("/")
        application_id = parts[-5]
        segment_id = parts[-3]
        version = int(parts[-1])
        result = self.pinpoint_backend.get_segment_version(
            application_id=application_id,
            segment_id=segment_id,
            version=version,
        )
        return json.dumps(result)

    def get_segment_versions(self) -> str:
        parts = self.path.split("/")
        application_id = parts[-4]
        segment_id = parts[-2]
        versions = self.pinpoint_backend.get_segment_versions(
            application_id=application_id, segment_id=segment_id
        )
        return json.dumps({"Item": versions})

    def get_segment_export_jobs(self) -> str:
        parts = self.path.split("/")
        application_id = parts[-5]
        segment_id = parts[-3]
        jobs = self.pinpoint_backend.get_segment_export_jobs(
            application_id=application_id, segment_id=segment_id
        )
        return json.dumps({"Item": jobs})

    def get_segment_import_jobs(self) -> str:
        parts = self.path.split("/")
        application_id = parts[-5]
        segment_id = parts[-3]
        jobs = self.pinpoint_backend.get_segment_import_jobs(
            application_id=application_id, segment_id=segment_id
        )
        return json.dumps({"Item": jobs})

    # --- Journey ---

    def create_journey(self) -> TYPE_RESPONSE:
        application_id = self.path.split("/")[-2]
        params = json.loads(self.body)
        journey = self.pinpoint_backend.create_journey(
            application_id=application_id, params=params
        )
        return 201, {"status": 201}, json.dumps(journey.to_json())

    def get_journey(self) -> str:
        parts = self.path.split("/")
        application_id = parts[-3]
        journey_id = parts[-1]
        journey = self.pinpoint_backend.get_journey(
            application_id=application_id, journey_id=journey_id
        )
        return json.dumps(journey.to_json())

    def list_journeys(self) -> str:
        application_id = self.path.split("/")[-2]
        journeys = self.pinpoint_backend.list_journeys(
            application_id=application_id
        )
        return json.dumps({"Item": [j.to_json() for j in journeys]})

    def update_journey(self) -> str:
        parts = self.path.split("/")
        application_id = parts[-3]
        journey_id = parts[-1]
        params = json.loads(self.body)
        journey = self.pinpoint_backend.update_journey(
            application_id=application_id, journey_id=journey_id, params=params
        )
        return json.dumps(journey.to_json())

    def update_journey_state(self) -> str:
        # /v1/apps/{app-id}/journeys/{journey-id}/state
        parts = self.path.split("/")
        application_id = parts[-4]
        journey_id = parts[-2]
        params = json.loads(self.body)
        state = params.get("State", "ACTIVE")
        journey = self.pinpoint_backend.update_journey_state(
            application_id=application_id, journey_id=journey_id, state=state
        )
        return json.dumps(journey.to_json())

    def delete_journey(self) -> str:
        parts = self.path.split("/")
        application_id = parts[-3]
        journey_id = parts[-1]
        journey = self.pinpoint_backend.delete_journey(
            application_id=application_id, journey_id=journey_id
        )
        return json.dumps(journey.to_json())

    def get_journey_date_range_kpi(self) -> str:
        parts = self.path.split("/")
        application_id = parts[-6]
        journey_id = parts[-4]
        kpi_name = parts[-1]
        result = self.pinpoint_backend.get_journey_date_range_kpi(
            application_id=application_id,
            journey_id=journey_id,
            kpi_name=kpi_name,
        )
        return json.dumps(result)

    def get_journey_execution_metrics(self) -> str:
        # /v1/apps/{app-id}/journeys/{journey-id}/execution-metrics
        parts = self.path.split("/")
        application_id = parts[-4]
        journey_id = parts[-2]
        result = self.pinpoint_backend.get_journey_execution_metrics(
            application_id=application_id, journey_id=journey_id
        )
        return json.dumps(result)

    def get_journey_execution_activity_metrics(self) -> str:
        # /v1/apps/{app-id}/journeys/{journey-id}/activities/{activity-id}/execution-metrics
        parts = self.path.split("/")
        application_id = parts[-6]
        journey_id = parts[-4]
        activity_id = parts[-2]
        result = self.pinpoint_backend.get_journey_execution_activity_metrics(
            application_id=application_id,
            journey_id=journey_id,
            activity_id=activity_id,
        )
        return json.dumps(result)

    def get_journey_runs(self) -> str:
        # /v1/apps/{app-id}/journeys/{journey-id}/runs
        parts = self.path.split("/")
        application_id = parts[-4]
        journey_id = parts[-2]
        runs = self.pinpoint_backend.get_journey_runs(
            application_id=application_id, journey_id=journey_id
        )
        return json.dumps({"Item": runs})

    def get_journey_run_execution_metrics(self) -> str:
        # /v1/apps/{app-id}/journeys/{journey-id}/runs/{run-id}/execution-metrics
        parts = self.path.split("/")
        application_id = parts[-6]
        journey_id = parts[-4]
        run_id = parts[-2]
        result = self.pinpoint_backend.get_journey_run_execution_metrics(
            application_id=application_id,
            journey_id=journey_id,
            run_id=run_id,
        )
        return json.dumps(result)

    def get_journey_run_execution_activity_metrics(self) -> str:
        # /v1/apps/{app-id}/journeys/{jid}/runs/{rid}/activities/{aid}/execution-metrics
        parts = self.path.split("/")
        application_id = parts[-8]
        journey_id = parts[-6]
        run_id = parts[-4]
        activity_id = parts[-2]
        result = self.pinpoint_backend.get_journey_run_execution_activity_metrics(
            application_id=application_id,
            journey_id=journey_id,
            run_id=run_id,
            activity_id=activity_id,
        )
        return json.dumps(result)

    # --- Template (Email/SMS/Push/Voice/InApp) ---

    def _template_from_path(self, template_type: str) -> tuple[str, str]:
        """Extract template name from path. Type is known from URL pattern."""
        # /v1/templates/{template-name}/{type}
        parts = self.path.split("/")
        template_name = parts[-2] if parts[-1] == template_type.lower() else parts[-1]
        # Handle case where template_type is in path
        for i, p in enumerate(parts):
            if p == "templates" and i + 1 < len(parts):
                template_name = parts[i + 1]
                break
        return template_name, template_type

    def create_email_template(self) -> TYPE_RESPONSE:
        parts = self.path.split("/")
        template_name = parts[-2]
        params = json.loads(self.body)
        template = self.pinpoint_backend.create_template(
            template_name=template_name, template_type="EMAIL", params=params
        )
        resp = {"CreateTemplateMessageBody": {"Arn": "", "Message": "Created", "RequestID": template.template_name}}
        return 201, {"status": 201}, json.dumps(resp)

    def get_email_template(self) -> str:
        parts = self.path.split("/")
        template_name = parts[-2]
        template = self.pinpoint_backend.get_template(
            template_name=template_name, template_type="EMAIL"
        )
        return json.dumps(template.to_json())

    def update_email_template(self) -> str:
        parts = self.path.split("/")
        template_name = parts[-2]
        params = json.loads(self.body)
        self.pinpoint_backend.update_template(
            template_name=template_name, template_type="EMAIL", params=params
        )
        return json.dumps({"MessageBody": {"Message": "Accepted", "RequestID": template_name}})

    def delete_email_template(self) -> str:
        parts = self.path.split("/")
        template_name = parts[-2]
        self.pinpoint_backend.delete_template(
            template_name=template_name, template_type="EMAIL"
        )
        return json.dumps({"MessageBody": {"Message": "Accepted", "RequestID": template_name}})

    def create_sms_template(self) -> TYPE_RESPONSE:
        parts = self.path.split("/")
        template_name = parts[-2]
        params = json.loads(self.body)
        template = self.pinpoint_backend.create_template(
            template_name=template_name, template_type="SMS", params=params
        )
        resp = {"CreateTemplateMessageBody": {"Arn": "", "Message": "Created", "RequestID": template.template_name}}
        return 201, {"status": 201}, json.dumps(resp)

    def get_sms_template(self) -> str:
        parts = self.path.split("/")
        template_name = parts[-2]
        template = self.pinpoint_backend.get_template(
            template_name=template_name, template_type="SMS"
        )
        return json.dumps(template.to_json())

    def update_sms_template(self) -> str:
        parts = self.path.split("/")
        template_name = parts[-2]
        params = json.loads(self.body)
        self.pinpoint_backend.update_template(
            template_name=template_name, template_type="SMS", params=params
        )
        return json.dumps({"MessageBody": {"Message": "Accepted", "RequestID": template_name}})

    def delete_sms_template(self) -> str:
        parts = self.path.split("/")
        template_name = parts[-2]
        self.pinpoint_backend.delete_template(
            template_name=template_name, template_type="SMS"
        )
        return json.dumps({"MessageBody": {"Message": "Accepted", "RequestID": template_name}})

    def create_push_template(self) -> TYPE_RESPONSE:
        parts = self.path.split("/")
        template_name = parts[-2]
        params = json.loads(self.body)
        template = self.pinpoint_backend.create_template(
            template_name=template_name, template_type="PUSH", params=params
        )
        resp = {"CreateTemplateMessageBody": {"Arn": "", "Message": "Created", "RequestID": template.template_name}}
        return 201, {"status": 201}, json.dumps(resp)

    def get_push_template(self) -> str:
        parts = self.path.split("/")
        template_name = parts[-2]
        template = self.pinpoint_backend.get_template(
            template_name=template_name, template_type="PUSH"
        )
        return json.dumps(template.to_json())

    def update_push_template(self) -> str:
        parts = self.path.split("/")
        template_name = parts[-2]
        params = json.loads(self.body)
        self.pinpoint_backend.update_template(
            template_name=template_name, template_type="PUSH", params=params
        )
        return json.dumps({"MessageBody": {"Message": "Accepted", "RequestID": template_name}})

    def delete_push_template(self) -> str:
        parts = self.path.split("/")
        template_name = parts[-2]
        self.pinpoint_backend.delete_template(
            template_name=template_name, template_type="PUSH"
        )
        return json.dumps({"MessageBody": {"Message": "Accepted", "RequestID": template_name}})

    def create_voice_template(self) -> TYPE_RESPONSE:
        parts = self.path.split("/")
        template_name = parts[-2]
        params = json.loads(self.body)
        template = self.pinpoint_backend.create_template(
            template_name=template_name, template_type="VOICE", params=params
        )
        resp = {"CreateTemplateMessageBody": {"Arn": "", "Message": "Created", "RequestID": template.template_name}}
        return 201, {"status": 201}, json.dumps(resp)

    def get_voice_template(self) -> str:
        parts = self.path.split("/")
        template_name = parts[-2]
        template = self.pinpoint_backend.get_template(
            template_name=template_name, template_type="VOICE"
        )
        return json.dumps(template.to_json())

    def update_voice_template(self) -> str:
        parts = self.path.split("/")
        template_name = parts[-2]
        params = json.loads(self.body)
        self.pinpoint_backend.update_template(
            template_name=template_name, template_type="VOICE", params=params
        )
        return json.dumps({"MessageBody": {"Message": "Accepted", "RequestID": template_name}})

    def delete_voice_template(self) -> str:
        parts = self.path.split("/")
        template_name = parts[-2]
        self.pinpoint_backend.delete_template(
            template_name=template_name, template_type="VOICE"
        )
        return json.dumps({"MessageBody": {"Message": "Accepted", "RequestID": template_name}})

    def create_in_app_template(self) -> TYPE_RESPONSE:
        parts = self.path.split("/")
        template_name = parts[-2]
        params = json.loads(self.body)
        template = self.pinpoint_backend.create_template(
            template_name=template_name, template_type="INAPP", params=params
        )
        resp = {"CreateTemplateMessageBody": {"Arn": "", "Message": "Created", "RequestID": template.template_name}}
        return 201, {"status": 201}, json.dumps(resp)

    def get_in_app_template(self) -> str:
        parts = self.path.split("/")
        template_name = parts[-2]
        template = self.pinpoint_backend.get_template(
            template_name=template_name, template_type="INAPP"
        )
        return json.dumps(template.to_json())

    def update_in_app_template(self) -> str:
        parts = self.path.split("/")
        template_name = parts[-2]
        params = json.loads(self.body)
        self.pinpoint_backend.update_template(
            template_name=template_name, template_type="INAPP", params=params
        )
        return json.dumps({"MessageBody": {"Message": "Accepted", "RequestID": template_name}})

    def delete_in_app_template(self) -> str:
        parts = self.path.split("/")
        template_name = parts[-2]
        self.pinpoint_backend.delete_template(
            template_name=template_name, template_type="INAPP"
        )
        return json.dumps({"MessageBody": {"Message": "Accepted", "RequestID": template_name}})

    def list_templates(self) -> str:
        templates = self.pinpoint_backend.list_templates()
        return json.dumps({"Item": templates})

    def list_template_versions(self) -> str:
        # /v1/templates/{template-name}/{template-type}/versions
        parts = self.path.split("/")
        template_name = parts[-3]
        template_type = parts[-2].upper()
        versions = self.pinpoint_backend.list_template_versions(
            template_name=template_name, template_type=template_type
        )
        return json.dumps({"Item": versions})

    def update_template_active_version(self) -> str:
        # /v1/templates/{template-name}/{template-type}/active-version
        parts = self.path.split("/")
        template_name = parts[-3]
        template_type = parts[-2].upper()
        params = json.loads(self.body)
        version = params.get("Version", "1")
        self.pinpoint_backend.update_template_active_version(
            template_name=template_name,
            template_type=template_type,
            version=version,
        )
        return json.dumps({"MessageBody": {"Message": "Accepted", "RequestID": template_name}})

    # --- Channels ---

    def _channel_response(self, method: str, channel_type: str) -> str:
        """Handle GET/PUT/DELETE for a channel type."""
        # /v1/apps/{app-id}/channels/{channel_slug}
        parts = self.path.split("/")
        application_id = parts[-3]
        if method == "GET":
            channel = self.pinpoint_backend.get_channel(
                application_id=application_id, channel_type=channel_type
            )
            return json.dumps(channel.to_json())
        elif method == "PUT":
            params = json.loads(self.body)
            channel = self.pinpoint_backend.update_channel(
                application_id=application_id,
                channel_type=channel_type,
                params=params,
            )
            return json.dumps(channel.to_json())
        else:  # DELETE
            channel = self.pinpoint_backend.delete_channel(
                application_id=application_id, channel_type=channel_type
            )
            return json.dumps(channel.to_json())

    # ADM
    def get_adm_channel(self) -> str:
        return self._channel_response("GET", "ADM")

    def update_adm_channel(self) -> str:
        return self._channel_response("PUT", "ADM")

    def delete_adm_channel(self) -> str:
        return self._channel_response("DELETE", "ADM")

    # APNS
    def get_apns_channel(self) -> str:
        return self._channel_response("GET", "APNS")

    def update_apns_channel(self) -> str:
        return self._channel_response("PUT", "APNS")

    def delete_apns_channel(self) -> str:
        return self._channel_response("DELETE", "APNS")

    # APNS Sandbox
    def get_apns_sandbox_channel(self) -> str:
        return self._channel_response("GET", "APNS_SANDBOX")

    def update_apns_sandbox_channel(self) -> str:
        return self._channel_response("PUT", "APNS_SANDBOX")

    def delete_apns_sandbox_channel(self) -> str:
        return self._channel_response("DELETE", "APNS_SANDBOX")

    # APNS VOIP
    def get_apns_voip_channel(self) -> str:
        return self._channel_response("GET", "APNS_VOIP")

    def update_apns_voip_channel(self) -> str:
        return self._channel_response("PUT", "APNS_VOIP")

    def delete_apns_voip_channel(self) -> str:
        return self._channel_response("DELETE", "APNS_VOIP")

    # APNS VOIP Sandbox
    def get_apns_voip_sandbox_channel(self) -> str:
        return self._channel_response("GET", "APNS_VOIP_SANDBOX")

    def update_apns_voip_sandbox_channel(self) -> str:
        return self._channel_response("PUT", "APNS_VOIP_SANDBOX")

    def delete_apns_voip_sandbox_channel(self) -> str:
        return self._channel_response("DELETE", "APNS_VOIP_SANDBOX")

    # Baidu
    def get_baidu_channel(self) -> str:
        return self._channel_response("GET", "BAIDU")

    def update_baidu_channel(self) -> str:
        return self._channel_response("PUT", "BAIDU")

    def delete_baidu_channel(self) -> str:
        return self._channel_response("DELETE", "BAIDU")

    # Email
    def get_email_channel(self) -> str:
        return self._channel_response("GET", "EMAIL")

    def update_email_channel(self) -> str:
        return self._channel_response("PUT", "EMAIL")

    def delete_email_channel(self) -> str:
        return self._channel_response("DELETE", "EMAIL")

    # GCM
    def get_gcm_channel(self) -> str:
        return self._channel_response("GET", "GCM")

    def update_gcm_channel(self) -> str:
        return self._channel_response("PUT", "GCM")

    def delete_gcm_channel(self) -> str:
        return self._channel_response("DELETE", "GCM")

    # SMS
    def get_sms_channel(self) -> str:
        return self._channel_response("GET", "SMS")

    def update_sms_channel(self) -> str:
        return self._channel_response("PUT", "SMS")

    def delete_sms_channel(self) -> str:
        return self._channel_response("DELETE", "SMS")

    # Voice
    def get_voice_channel(self) -> str:
        return self._channel_response("GET", "VOICE")

    def update_voice_channel(self) -> str:
        return self._channel_response("PUT", "VOICE")

    def delete_voice_channel(self) -> str:
        return self._channel_response("DELETE", "VOICE")

    # All channels
    def get_channels(self) -> str:
        # /v1/apps/{app-id}/channels
        application_id = self.path.split("/")[-2]
        result = self.pinpoint_backend.get_channels(
            application_id=application_id
        )
        return json.dumps(result)

    # --- Endpoint ---

    def update_endpoint(self) -> str:
        # PUT /v1/apps/{app-id}/endpoints/{endpoint-id}
        parts = self.path.split("/")
        application_id = parts[-3]
        endpoint_id = parts[-1]
        params = json.loads(self.body)
        self.pinpoint_backend.update_endpoint(
            application_id=application_id,
            endpoint_id=endpoint_id,
            params=params,
        )
        return json.dumps({"MessageBody": {"Message": "Accepted", "RequestID": endpoint_id}})

    def update_endpoints_batch(self) -> str:
        # PUT /v1/apps/{app-id}/endpoints
        application_id = self.path.split("/")[-2]
        params = json.loads(self.body)
        items = params.get("Item", [])
        result = self.pinpoint_backend.update_endpoints_batch(
            application_id=application_id, items=items
        )
        return json.dumps({"MessageBody": {"Message": "Accepted"}, "Result": result})

    def get_endpoint(self) -> str:
        # GET /v1/apps/{app-id}/endpoints/{endpoint-id}
        parts = self.path.split("/")
        application_id = parts[-3]
        endpoint_id = parts[-1]
        endpoint = self.pinpoint_backend.get_endpoint(
            application_id=application_id, endpoint_id=endpoint_id
        )
        return json.dumps(endpoint.to_json())

    def delete_endpoint(self) -> str:
        parts = self.path.split("/")
        application_id = parts[-3]
        endpoint_id = parts[-1]
        endpoint = self.pinpoint_backend.delete_endpoint(
            application_id=application_id, endpoint_id=endpoint_id
        )
        return json.dumps(endpoint.to_json())

    def get_user_endpoints(self) -> str:
        # GET /v1/apps/{app-id}/users/{user-id}
        parts = self.path.split("/")
        application_id = parts[-3]
        user_id = parts[-1]
        endpoints = self.pinpoint_backend.get_user_endpoints(
            application_id=application_id, user_id=user_id
        )
        return json.dumps({"Item": endpoints})

    def delete_user_endpoints(self) -> str:
        # DELETE /v1/apps/{app-id}/users/{user-id}
        parts = self.path.split("/")
        application_id = parts[-3]
        user_id = parts[-1]
        endpoints = self.pinpoint_backend.delete_user_endpoints(
            application_id=application_id, user_id=user_id
        )
        return json.dumps({"Item": endpoints})

    # --- Export/Import Jobs ---

    def create_export_job(self) -> TYPE_RESPONSE:
        # POST /v1/apps/{app-id}/jobs/export
        application_id = self.path.split("/")[-3]
        params = json.loads(self.body)
        job = self.pinpoint_backend.create_export_job(
            application_id=application_id, params=params
        )
        return 201, {"status": 201}, json.dumps(job.to_json())

    def get_export_job(self) -> str:
        # GET /v1/apps/{app-id}/jobs/export/{job-id}
        parts = self.path.split("/")
        application_id = parts[-4]
        job_id = parts[-1]
        job = self.pinpoint_backend.get_export_job(
            application_id=application_id, job_id=job_id
        )
        return json.dumps(job.to_json())

    def get_export_jobs(self) -> str:
        # GET /v1/apps/{app-id}/jobs/export
        application_id = self.path.split("/")[-3]
        jobs = self.pinpoint_backend.get_export_jobs(
            application_id=application_id
        )
        return json.dumps({"Item": [j.to_json() for j in jobs]})

    def create_import_job(self) -> TYPE_RESPONSE:
        application_id = self.path.split("/")[-3]
        params = json.loads(self.body)
        job = self.pinpoint_backend.create_import_job(
            application_id=application_id, params=params
        )
        return 201, {"status": 201}, json.dumps(job.to_json())

    def get_import_job(self) -> str:
        parts = self.path.split("/")
        application_id = parts[-4]
        job_id = parts[-1]
        job = self.pinpoint_backend.get_import_job(
            application_id=application_id, job_id=job_id
        )
        return json.dumps(job.to_json())

    def get_import_jobs(self) -> str:
        application_id = self.path.split("/")[-3]
        jobs = self.pinpoint_backend.get_import_jobs(
            application_id=application_id
        )
        return json.dumps({"Item": [j.to_json() for j in jobs]})

    # --- Recommender ---

    def create_recommender_configuration(self) -> TYPE_RESPONSE:
        params = json.loads(self.body)
        rec = self.pinpoint_backend.create_recommender_configuration(params=params)
        return 201, {"status": 201}, json.dumps(rec.to_json())

    def get_recommender_configuration(self) -> str:
        recommender_id = self.path.split("/")[-1]
        rec = self.pinpoint_backend.get_recommender_configuration(
            recommender_id=recommender_id
        )
        return json.dumps(rec.to_json())

    def get_recommender_configurations(self) -> str:
        recs = self.pinpoint_backend.get_recommender_configurations()
        return json.dumps({"Item": [r.to_json() for r in recs]})

    def update_recommender_configuration(self) -> str:
        recommender_id = self.path.split("/")[-1]
        params = json.loads(self.body)
        rec = self.pinpoint_backend.update_recommender_configuration(
            recommender_id=recommender_id, params=params
        )
        return json.dumps(rec.to_json())

    def delete_recommender_configuration(self) -> str:
        recommender_id = self.path.split("/")[-1]
        rec = self.pinpoint_backend.delete_recommender_configuration(
            recommender_id=recommender_id
        )
        return json.dumps(rec.to_json())

    # --- Events ---

    def put_events(self) -> str:
        # POST /v1/apps/{app-id}/events
        application_id = self.path.split("/")[-2]
        params = json.loads(self.body)
        batch_events = params.get("BatchItem", {})
        result = self.pinpoint_backend.put_events(
            application_id=application_id, events=batch_events
        )
        return json.dumps({"Results": result})

    # --- Messages ---

    def send_messages(self) -> str:
        # POST /v1/apps/{app-id}/messages
        application_id = self.path.split("/")[-2]
        params = json.loads(self.body)
        result = self.pinpoint_backend.send_messages(
            application_id=application_id, message_request=params
        )
        return json.dumps(result)

    def send_users_messages(self) -> str:
        # POST /v1/apps/{app-id}/users-messages
        application_id = self.path.split("/")[-2]
        params = json.loads(self.body)
        result = self.pinpoint_backend.send_users_messages(
            application_id=application_id, send_request=params
        )
        return json.dumps(result)

    def send_o_t_p_message(self) -> str:
        # POST /v1/apps/{app-id}/otp
        application_id = self.path.split("/")[-2]
        params = json.loads(self.body)
        result = self.pinpoint_backend.send_otp_message(
            application_id=application_id, send_request=params
        )
        return json.dumps(result)

    def verify_o_t_p_message(self) -> str:
        # POST /v1/apps/{app-id}/verify-otp
        application_id = self.path.split("/")[-2]
        params = json.loads(self.body)
        result = self.pinpoint_backend.verify_otp_message(
            application_id=application_id, verify_request=params
        )
        return json.dumps(result)

    # --- Phone Number Validate ---

    def phone_number_validate(self) -> str:
        params = json.loads(self.body)
        number = params.get("PhoneNumber", "")
        iso_code = params.get("IsoCountryCode", "US")
        result = self.pinpoint_backend.phone_number_validate(
            number=number, iso_country_code=iso_code
        )
        return json.dumps(result)

    # --- KPI ---

    def get_application_date_range_kpi(self) -> str:
        # /v1/apps/{app-id}/kpis/daterange/{kpi-name}
        parts = self.path.split("/")
        application_id = parts[-4]
        kpi_name = parts[-1]
        result = self.pinpoint_backend.get_application_date_range_kpi(
            application_id=application_id, kpi_name=kpi_name
        )
        return json.dumps(result)

    # --- Remove Attributes ---

    def remove_attributes(self) -> str:
        # PUT /v1/apps/{app-id}/attributes/{attribute-type}
        parts = self.path.split("/")
        application_id = parts[-3]
        attribute_type = parts[-1]
        params = json.loads(self.body)
        attributes = params.get("Blacklist", [])
        result = self.pinpoint_backend.remove_attributes(
            application_id=application_id,
            attribute_type=attribute_type,
            attributes=attributes,
        )
        return json.dumps(result)

    # --- In-App Messages ---

    def get_in_app_messages(self) -> str:
        # GET /v1/apps/{app-id}/endpoints/{endpoint-id}/inappmessages
        parts = self.path.split("/")
        application_id = parts[-4]
        endpoint_id = parts[-2]
        result = self.pinpoint_backend.get_in_app_messages(
            application_id=application_id, endpoint_id=endpoint_id
        )
        return json.dumps(result)
