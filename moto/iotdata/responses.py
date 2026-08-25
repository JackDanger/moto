import base64
import json
from typing import Any
from urllib.parse import unquote

from moto.core.responses import BaseResponse

from .models import IoTDataPlaneBackend, iotdata_backends


class IoTDataPlaneResponse(BaseResponse):
    def __init__(self) -> None:
        super().__init__(service_name="iot-data")

    def setup_class(
        self, request: Any, full_url: str, headers: Any, use_raw_body: bool = False
    ) -> None:
        super().setup_class(request, full_url, headers, use_raw_body=True)

    @property
    def iotdata_backend(self) -> IoTDataPlaneBackend:
        return iotdata_backends[self.current_account][self.region]

    def update_thing_shadow(self) -> str:
        thing_name = self._get_param("thingName")
        shadow_name = self.querystring.get("name", [None])[0]
        payload = self.iotdata_backend.update_thing_shadow(
            thing_name=thing_name,
            payload=self.body,
            shadow_name=shadow_name,
        )
        return json.dumps(payload.to_response_dict())

    def get_thing_shadow(self) -> str:
        thing_name = self._get_param("thingName")
        shadow_name = self.querystring.get("name", [None])[0]
        payload = self.iotdata_backend.get_thing_shadow(
            thing_name=thing_name, shadow_name=shadow_name
        )
        return json.dumps(payload.to_dict())

    def delete_thing_shadow(self) -> str:
        thing_name = self._get_param("thingName")
        shadow_name = self.querystring.get("name", [None])[0]
        payload = self.iotdata_backend.delete_thing_shadow(
            thing_name=thing_name, shadow_name=shadow_name
        )
        return json.dumps(payload.to_dict())

    def publish(self) -> str:
        topic = self.path.split("/topics/")[-1]
        # a uri parameter containing forward slashes is not correctly url encoded when we're running in server mode.
        # https://github.com/pallets/flask/issues/900
        topic = unquote(topic) if "%" in topic else topic
        qos_str = self.querystring.get("qos", ["0"])[0]
        try:
            qos = int(qos_str)
        except (ValueError, TypeError):
            qos = 0
        retain_str = self.querystring.get("retain", ["false"])[0]
        retain = retain_str.lower() == "true"
        self.iotdata_backend.publish(topic=topic, payload=self.body, qos=qos, retain=retain)
        return json.dumps({})

    def list_named_shadows_for_thing(self) -> str:
        thing_name = self._get_param("thingName")
        shadows = self.iotdata_backend.list_named_shadows_for_thing(thing_name)
        return json.dumps({"results": shadows})

    def delete_connection(self) -> str:
        # client_id is in the URI path: /connections/{clientId}
        client_id = self.path.split("/connections/")[-1]
        client_id = unquote(client_id) if "%" in client_id else client_id
        self.iotdata_backend.delete_connection(client_id)
        return json.dumps({})

    def get_retained_message(self) -> str:
        # topic is in the URI path: /retainedMessage/{topic}
        topic = self.path.split("/retainedMessage/", 1)[-1]
        topic = unquote(topic) if "%" in topic else topic
        msg = self.iotdata_backend.get_retained_message(topic)
        return json.dumps(
            {
                "topic": msg.topic,
                "payload": base64.b64encode(msg.payload).decode("utf-8"),
                "qos": msg.qos,
                "lastModifiedTime": msg.last_modified_time,
            }
        )

    def list_retained_messages(self) -> str:
        next_token = self.querystring.get("nextToken", [None])[0]
        max_results_str = self.querystring.get("maxResults", [None])[0]
        max_results = int(max_results_str) if max_results_str is not None else None
        msgs, new_token = self.iotdata_backend.list_retained_messages(
            next_token=next_token, max_results=max_results
        )
        retained_topics = [
            {
                "topic": m.topic,
                "payloadSize": len(m.payload),
                "qos": m.qos,
                "lastModifiedTime": m.last_modified_time,
            }
            for m in msgs
        ]
        result: dict[str, Any] = {"retainedTopics": retained_topics}
        if new_token is not None:
            result["nextToken"] = new_token
        return json.dumps(result)
