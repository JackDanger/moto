"""
Response handlers for AWS CloudWatch Synthetics API emulation in Moto.
"""

import json
from typing import Any, Union
from urllib.parse import unquote

from moto.core.responses import TYPE_RESPONSE, BaseResponse
from moto.synthetics.models import SyntheticsBackend, synthetics_backends


def _make_response(body: str, status: int = 200) -> TYPE_RESPONSE:
    return status, {"Content-Type": "application/json"}, body


class SyntheticsResponse(BaseResponse):
    """
    Handles API responses for AWS CloudWatch Synthetics operations.
    """

    def __init__(self) -> None:
        super().__init__(service_name="synthetics")

    @property
    def synthetics_backend(self) -> SyntheticsBackend:
        return synthetics_backends[self.current_account][self.region]

    def tags(
        self, request: Any, full_url: str, headers: Any
    ) -> TYPE_RESPONSE:
        self.setup_class(request, full_url, headers)
        if request.method == "POST":
            return _make_response(self._tag_resource())
        if request.method == "DELETE":
            return _make_response(self._untag_resource())
        if request.method == "GET":
            return _make_response(self._list_tags_for_resource())
        return _make_response("{}", 400)

    def canary(
        self, request: Any, full_url: str, headers: Any
    ) -> TYPE_RESPONSE:
        self.setup_class(request, full_url, headers)
        if request.method == "POST":
            return _make_response(self._create_canary())
        if request.method == "GET":
            return _make_response(self._get_canary())
        if request.method == "DELETE":
            return _make_response(self._delete_canary())
        if request.method == "PATCH":
            return _make_response(self._update_canary())
        return _make_response("{}", 400)

    def canaries(
        self, request: Any, full_url: str, headers: Any
    ) -> TYPE_RESPONSE:
        self.setup_class(request, full_url, headers)
        return _make_response(self._describe_canaries())

    def canaries_last_run(
        self, request: Any, full_url: str, headers: Any
    ) -> TYPE_RESPONSE:
        self.setup_class(request, full_url, headers)
        return _make_response(self._describe_canaries_last_run())

    def canary_start(
        self, request: Any, full_url: str, headers: Any
    ) -> TYPE_RESPONSE:
        self.setup_class(request, full_url, headers)
        return _make_response(self._start_canary())

    def canary_stop(
        self, request: Any, full_url: str, headers: Any
    ) -> TYPE_RESPONSE:
        self.setup_class(request, full_url, headers)
        return _make_response(self._stop_canary())

    def canary_runs(
        self, request: Any, full_url: str, headers: Any
    ) -> TYPE_RESPONSE:
        self.setup_class(request, full_url, headers)
        return _make_response(self._get_canary_runs())

    def canary_dry_run_start(
        self, request: Any, full_url: str, headers: Any
    ) -> TYPE_RESPONSE:
        self.setup_class(request, full_url, headers)
        return _make_response(self._start_canary_dry_run())

    def runtime_versions(
        self, request: Any, full_url: str, headers: Any
    ) -> TYPE_RESPONSE:
        self.setup_class(request, full_url, headers)
        return _make_response(self._describe_runtime_versions())

    def group_dispatch(
        self, request: Any, full_url: str, headers: Any
    ) -> TYPE_RESPONSE:
        self.setup_class(request, full_url, headers)
        if request.method == "POST":
            return _make_response(self._create_group())
        if request.method == "GET":
            return _make_response(self._get_group())
        if request.method == "DELETE":
            return _make_response(self._delete_group())
        return _make_response("{}", 400)

    def groups_list(
        self, request: Any, full_url: str, headers: Any
    ) -> TYPE_RESPONSE:
        self.setup_class(request, full_url, headers)
        return _make_response(self._list_groups())

    def group_associate(
        self, request: Any, full_url: str, headers: Any
    ) -> TYPE_RESPONSE:
        self.setup_class(request, full_url, headers)
        return _make_response(self._associate_resource())

    def group_disassociate(
        self, request: Any, full_url: str, headers: Any
    ) -> TYPE_RESPONSE:
        self.setup_class(request, full_url, headers)
        return _make_response(self._disassociate_resource())

    def group_resources(
        self, request: Any, full_url: str, headers: Any
    ) -> TYPE_RESPONSE:
        self.setup_class(request, full_url, headers)
        return _make_response(self._list_group_resources())

    def resource_groups(
        self, request: Any, full_url: str, headers: Any
    ) -> TYPE_RESPONSE:
        self.setup_class(request, full_url, headers)
        return _make_response(self._list_associated_groups())

    # --- Internal handler methods (called by dispatch and custom handlers) ---
    # Methods prefixed with _ are internal; unprefixed versions are for dispatch.

    def create_canary(self) -> str:
        return self._create_canary()

    def _create_canary(self) -> str:
        params = json.loads(self.body)
        canary = self.synthetics_backend.create_canary(
            name=params["Name"],
            code=params.get("Code", {}),
            artifact_s3_location=params.get("ArtifactS3Location", "s3://dummy"),
            execution_role_arn=params.get(
                "ExecutionRoleArn", "arn:aws:iam::123:role/service-role"
            ),
            schedule=params.get("Schedule", {"Expression": "rate(5 minutes)"}),
            run_config=params.get("RunConfig", {"TimeoutInSeconds": 60}),
            success_retention_period_in_days=params.get(
                "SuccessRetentionPeriodInDays", 31
            ),
            failure_retention_period_in_days=params.get(
                "FailureRetentionPeriodInDays", 31
            ),
            runtime_version=params.get("RuntimeVersion", "syn-nodejs-puppeteer-3.8"),
            vpc_config=params.get("VpcConfig"),
            resources_to_replicate_tags=params.get("ResourcesToReplicateTags"),
            provisioned_resource_cleanup=params.get("ProvisionedResourceCleanup"),
            browser_configs=params.get("BrowserConfigs"),
            tags=params.get("Tags", {}),
            artifact_config=params.get("ArtifactConfig"),
        )
        return json.dumps({"Canary": canary.to_dict()})

    def get_canary(self) -> str:
        return self._get_canary()

    def _get_canary(self) -> str:
        name = unquote(self.path.split("/canary/")[-1].split("/")[0])
        canary = self.synthetics_backend.get_canary(name)
        return json.dumps({"Canary": canary.to_dict()})

    def delete_canary(self) -> str:
        return self._delete_canary()

    def _delete_canary(self) -> str:
        name = unquote(self.path.split("/canary/")[-1].split("/")[0])
        self.synthetics_backend.delete_canary(name)
        return json.dumps({})

    def update_canary(self) -> str:
        return self._update_canary()

    def _update_canary(self) -> str:
        name = unquote(self.path.split("/canary/")[-1].split("/")[0])
        params = json.loads(self.body)
        self.synthetics_backend.update_canary(
            name=name,
            code=params.get("Code"),
            execution_role_arn=params.get("ExecutionRoleArn"),
            runtime_version=params.get("RuntimeVersion"),
            schedule=params.get("Schedule"),
            run_config=params.get("RunConfig"),
            success_retention_period_in_days=params.get(
                "SuccessRetentionPeriodInDays"
            ),
            failure_retention_period_in_days=params.get(
                "FailureRetentionPeriodInDays"
            ),
            vpc_config=params.get("VpcConfig"),
            artifact_s3_location=params.get("ArtifactS3Location"),
            artifact_config=params.get("ArtifactConfig"),
            provisioned_resource_cleanup=params.get("ProvisionedResourceCleanup"),
            browser_configs=params.get("BrowserConfigs"),
        )
        return json.dumps({})

    def start_canary(self) -> str:
        return self._start_canary()

    def _start_canary(self) -> str:
        name = unquote(self.path.split("/canary/")[-1].split("/")[0])
        self.synthetics_backend.start_canary(name)
        return json.dumps({})

    def stop_canary(self) -> str:
        return self._stop_canary()

    def _stop_canary(self) -> str:
        name = unquote(self.path.split("/canary/")[-1].split("/")[0])
        self.synthetics_backend.stop_canary(name)
        return json.dumps({})

    def start_canary_dry_run(self) -> str:
        return self._start_canary_dry_run()

    def _start_canary_dry_run(self) -> str:
        name = unquote(self.path.split("/canary/")[-1].split("/")[0])
        result = self.synthetics_backend.start_canary_dry_run(name)
        return json.dumps({"DryRunConfig": result})

    def describe_canaries(self) -> str:
        return self._describe_canaries()

    def _describe_canaries(self) -> str:
        params = json.loads(self.body) if self.body else {}
        names = params.get("Names")
        canaries, _ = self.synthetics_backend.describe_canaries(None, None, names)
        return json.dumps({"Canaries": [c.to_dict() for c in canaries]})

    def describe_canaries_last_run(self) -> str:
        return self._describe_canaries_last_run()

    def _describe_canaries_last_run(self) -> str:
        params = json.loads(self.body) if self.body else {}
        names = params.get("Names")
        result = self.synthetics_backend.describe_canaries_last_run(names)
        return json.dumps({"CanariesLastRun": result})

    def describe_runtime_versions(self) -> str:
        return self._describe_runtime_versions()

    def _describe_runtime_versions(self) -> str:
        versions = self.synthetics_backend.describe_runtime_versions()
        return json.dumps({"RuntimeVersions": versions})

    def get_canary_runs(self) -> str:
        return self._get_canary_runs()

    def _get_canary_runs(self) -> str:
        name = unquote(self.path.split("/canary/")[-1].split("/")[0])
        runs = self.synthetics_backend.get_canary_runs(name)
        return json.dumps({"CanaryRuns": [r.to_dict() for r in runs]})

    def create_group(self) -> str:
        return self._create_group()

    def _create_group(self) -> str:
        params = json.loads(self.body)
        group = self.synthetics_backend.create_group(
            name=params["Name"],
            tags=params.get("Tags"),
        )
        return json.dumps({"Group": group.to_dict()})

    def get_group(self) -> str:
        return self._get_group()

    def _get_group(self) -> str:
        group_id = unquote(self.path.split("/group/")[-1].split("/")[0])
        group = self.synthetics_backend.get_group(group_id)
        return json.dumps({"Group": group.to_dict()})

    def delete_group(self) -> str:
        return self._delete_group()

    def _delete_group(self) -> str:
        group_id = unquote(self.path.split("/group/")[-1].split("/")[0])
        self.synthetics_backend.delete_group(group_id)
        return json.dumps({})

    def list_groups(self) -> str:
        return self._list_groups()

    def _list_groups(self) -> str:
        groups = self.synthetics_backend.list_groups()
        return json.dumps({"Groups": [g.summary_dict() for g in groups]})

    def associate_resource(self) -> str:
        return self._associate_resource()

    def _associate_resource(self) -> str:
        group_id = unquote(self.path.split("/group/")[-1].split("/")[0])
        params = json.loads(self.body)
        resource_arn = params["ResourceArn"]
        self.synthetics_backend.associate_resource(group_id, resource_arn)
        return json.dumps({})

    def disassociate_resource(self) -> str:
        return self._disassociate_resource()

    def _disassociate_resource(self) -> str:
        group_id = unquote(self.path.split("/group/")[-1].split("/")[0])
        params = json.loads(self.body)
        resource_arn = params["ResourceArn"]
        self.synthetics_backend.disassociate_resource(group_id, resource_arn)
        return json.dumps({})

    def list_group_resources(self) -> str:
        return self._list_group_resources()

    def _list_group_resources(self) -> str:
        group_id = unquote(self.path.split("/group/")[-1].split("/")[0])
        resources = self.synthetics_backend.list_group_resources(group_id)
        return json.dumps({"Resources": resources})

    def list_associated_groups(self) -> str:
        return self._list_associated_groups()

    def _list_associated_groups(self) -> str:
        resource_arn = unquote(self.path.split("/resource/")[-1].split("/")[0])
        groups = self.synthetics_backend.list_associated_groups(resource_arn)
        return json.dumps({"Groups": [g.summary_dict() for g in groups]})

    def tag_resource(self) -> str:
        return self._tag_resource()

    def _tag_resource(self) -> str:
        resource_arn = unquote(self.path).split("tags/")[-1]
        params = json.loads(self.body)
        tags = params.get("Tags", {})
        self.synthetics_backend.tag_resource(resource_arn, tags)
        return json.dumps({})

    def untag_resource(self) -> str:
        return self._untag_resource()

    def _untag_resource(self) -> str:
        resource_arn = unquote(self.path).split("tags/")[-1]
        tag_keys = self.querystring.get("tagKeys", [])
        self.synthetics_backend.untag_resource(resource_arn, tag_keys)
        return json.dumps({})

    def list_tags_for_resource(self) -> str:
        return self._list_tags_for_resource()

    def _list_tags_for_resource(self) -> str:
        resource_arn = unquote(self.path).split("tags/")[-1]
        tags = self.synthetics_backend.list_tags_for_resource(resource_arn)
        return json.dumps({"Tags": tags})
