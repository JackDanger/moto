import datetime
from collections import defaultdict
from typing import Any, Optional

from dateutil import parser

from moto.core.base_backend import BackendDict, BaseBackend
from moto.core.common_models import BaseModel
from moto.core.utils import iso_8601_datetime_with_milliseconds, unix_time
from moto.moto_api._internal import mock_random
from moto.utilities.utils import get_partition

from .exceptions import InvalidInputException, ResourceNotFoundException


class CodeBuildProjectMetadata(BaseModel):
    def __init__(
        self,
        account_id: str,
        region_name: str,
        project_name: str,
        source_version: Optional[str],
        artifacts: Optional[dict[str, Any]],
        build_id: str,
        service_role: str,
    ):
        current_date = iso_8601_datetime_with_milliseconds()
        self.build_metadata: dict[str, Any] = {}

        self.build_metadata["id"] = build_id
        self.build_metadata["arn"] = (
            f"arn:{get_partition(region_name)}:codebuild:{region_name}:{account_id}:build/{build_id}"
        )

        self.build_metadata["buildNumber"] = mock_random.randint(1, 100)
        self.build_metadata["startTime"] = current_date
        self.build_metadata["currentPhase"] = "QUEUED"
        self.build_metadata["buildStatus"] = "IN_PROGRESS"
        self.build_metadata["sourceVersion"] = (
            source_version if source_version else "refs/heads/main"
        )
        self.build_metadata["projectName"] = project_name

        self.build_metadata["phases"] = [
            {
                "phaseType": "SUBMITTED",
                "phaseStatus": "SUCCEEDED",
                "startTime": current_date,
                "endTime": current_date,
                "durationInSeconds": 0,
            },
            {"phaseType": "QUEUED", "startTime": current_date},
        ]

        self.build_metadata["source"] = {
            "type": "CODECOMMIT",  # should be different based on what you pass in
            "location": "https://git-codecommit.eu-west-2.amazonaws.com/v1/repos/testing",
            "gitCloneDepth": 1,
            "gitSubmodulesConfig": {"fetchSubmodules": False},
            "buildspec": "buildspec/stuff.yaml",  # should present in the codebuild project somewhere
            "insecureSsl": False,
        }

        self.build_metadata["secondarySources"] = []
        self.build_metadata["secondarySourceVersions"] = []
        self.build_metadata["artifacts"] = artifacts
        self.build_metadata["secondaryArtifacts"] = []
        self.build_metadata["cache"] = {"type": "NO_CACHE"}

        self.build_metadata["environment"] = {
            "type": "LINUX_CONTAINER",
            "image": "aws/codebuild/amazonlinux2-x86_64-standard:3.0",
            "computeType": "BUILD_GENERAL1_SMALL",
            "environmentVariables": [],
            "privilegedMode": False,
            "imagePullCredentialsType": "CODEBUILD",
        }

        self.build_metadata["serviceRole"] = service_role

        self.build_metadata["logs"] = {
            "deepLink": "https://console.aws.amazon.com/cloudwatch/home?region=eu-west-2#logEvent:group=null;stream=null",
            "cloudWatchLogsArn": f"arn:{get_partition(region_name)}:logs:{region_name}:{account_id}:log-group:null:log-stream:null",
            "cloudWatchLogs": {"status": "ENABLED"},
            "s3Logs": {"status": "DISABLED", "encryptionDisabled": False},
        }

        self.build_metadata["timeoutInMinutes"] = 45
        self.build_metadata["queuedTimeoutInMinutes"] = 480
        self.build_metadata["buildComplete"] = False
        self.build_metadata["initiator"] = "rootme"
        self.build_metadata["encryptionKey"] = (
            f"arn:{get_partition(region_name)}:kms:{region_name}:{account_id}:alias/aws/s3"
        )


class CodeBuild(BaseModel):
    def __init__(
        self,
        account_id: str,
        region: str,
        project_name: str,
        description: Optional[str],
        project_source: dict[str, Any],
        artifacts: dict[str, Any],
        environment: dict[str, Any],
        serviceRole: str = "some_role",
        tags: Optional[list[dict[str, str]]] = None,
        cache: Optional[dict[str, Any]] = None,
        timeout: Optional[int] = 0,
        queued_timeout: Optional[int] = 0,
        source_version: Optional[str] = None,
        logs_config: Optional[dict[str, Any]] = None,
        vpc_config: Optional[dict[str, Any]] = None,
    ):
        self.account_id = account_id
        self.region = region
        self.project_name = project_name
        self.arn = f"arn:{get_partition(region)}:codebuild:{region}:{account_id}:project/{project_name}"
        self.service_role = serviceRole
        self.tags = tags
        self.visibility = "PRIVATE"
        self.resource_access_role: Optional[str] = None
        current_date = unix_time()
        self.project_metadata: dict[str, Any] = {}

        self.project_metadata["name"] = project_name
        if description:
            self.project_metadata["description"] = description
        self.project_metadata["arn"] = self.arn
        self.project_metadata["encryptionKey"] = (
            f"arn:{get_partition(region)}:kms:{region}:{account_id}:alias/aws/s3"
        )
        if serviceRole.startswith("arn:"):
            self.project_metadata["serviceRole"] = serviceRole
        else:
            self.project_metadata["serviceRole"] = (
                f"arn:{get_partition(region)}:iam::{account_id}:role/service-role/{serviceRole}"
            )
        self.project_metadata["lastModifiedDate"] = current_date
        self.project_metadata["created"] = current_date
        self.project_metadata["badge"] = {}
        self.project_metadata["badge"]["badgeEnabled"] = (
            False  # this false needs to be a json false not a python false
        )
        self.project_metadata["environment"] = environment
        self.project_metadata["artifacts"] = artifacts
        self.project_metadata["source"] = project_source
        self.project_metadata["cache"] = cache or {"type": "NO_CACHE"}
        self.project_metadata["timeoutInMinutes"] = timeout or 0
        self.project_metadata["queuedTimeoutInMinutes"] = queued_timeout or 0
        self.project_metadata["tags"] = tags
        if source_version:
            self.project_metadata["sourceVersion"] = source_version
        if logs_config:
            self.project_metadata["logsConfig"] = logs_config
        if vpc_config:
            self.project_metadata["vpcConfig"] = vpc_config


class Webhook(BaseModel):
    def __init__(
        self,
        account_id: str,
        region_name: str,
        project_name: str,
        branch_filter: Optional[str],
        filter_groups: Optional[list[list[dict[str, Any]]]],
        build_type: Optional[str],
    ):
        self.project_name = project_name
        self.branch_filter = branch_filter or ""
        self.filter_groups = filter_groups or []
        self.build_type = build_type or "BUILD"
        self.url = f"https://codebuild.{region_name}.amazonaws.com/webhooks/{project_name}"
        self.payload_url = (
            f"https://codebuild.{region_name}.amazonaws.com/webhook-trigger/{mock_random.uuid4()}"
        )
        self.secret = mock_random.get_random_hex(40)
        self.last_modified_secret = unix_time()

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {
            "url": self.url,
            "payloadUrl": self.payload_url,
            "secret": self.secret,
            "branchFilter": self.branch_filter,
            "filterGroups": self.filter_groups,
            "buildType": self.build_type,
            "lastModifiedSecret": self.last_modified_secret,
        }
        return result


class SourceCredential(BaseModel):
    def __init__(
        self,
        account_id: str,
        region_name: str,
        token: str,
        server_type: str,
        auth_type: str,
        username: Optional[str],
    ):
        self.arn = (
            f"arn:{get_partition(region_name)}:codebuild:{region_name}:{account_id}:token/{server_type}"
        )
        self.token = token
        self.server_type = server_type
        self.auth_type = auth_type
        self.username = username

    def to_info_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {
            "arn": self.arn,
            "serverType": self.server_type,
            "authType": self.auth_type,
        }
        if self.username:
            result["username"] = self.username
        return result


class ReportGroup(BaseModel):
    def __init__(
        self,
        account_id: str,
        region_name: str,
        name: str,
        report_type: str,
        export_config: dict[str, Any],
        tags: Optional[list[dict[str, str]]],
    ):
        partition = get_partition(region_name)
        self.name = name
        self.arn = f"arn:{partition}:codebuild:{region_name}:{account_id}:report-group/{name}"
        self.report_type = report_type
        self.export_config = export_config
        self.tags = tags or []
        current_date = unix_time()
        self.created = current_date
        self.last_modified = current_date
        self.status = "ACTIVE"

    def to_dict(self) -> dict[str, Any]:
        return {
            "arn": self.arn,
            "name": self.name,
            "type": self.report_type,
            "exportConfig": self.export_config,
            "created": self.created,
            "lastModified": self.last_modified,
            "tags": self.tags,
            "status": self.status,
        }


class Fleet(BaseModel):
    def __init__(
        self,
        account_id: str,
        region_name: str,
        name: str,
        base_capacity: int,
        environment_type: str,
        compute_type: str,
        compute_configuration: Optional[dict[str, Any]],
        scaling_configuration: Optional[dict[str, Any]],
        overflow_behavior: Optional[str],
        vpc_config: Optional[dict[str, Any]],
        proxy_configuration: Optional[dict[str, Any]],
        image_id: Optional[str],
        fleet_service_role: Optional[str],
        tags: Optional[list[dict[str, str]]],
    ):
        partition = get_partition(region_name)
        self.fleet_id = mock_random.uuid4()
        self.name = name
        self.arn = f"arn:{partition}:codebuild:{region_name}:{account_id}:fleet/{name}:{self.fleet_id}"
        self.base_capacity = base_capacity
        self.environment_type = environment_type
        self.compute_type = compute_type
        self.compute_configuration = compute_configuration
        self.scaling_configuration = scaling_configuration
        self.overflow_behavior = overflow_behavior or "QUEUE"
        self.vpc_config = vpc_config
        self.proxy_configuration = proxy_configuration
        self.image_id = image_id
        self.fleet_service_role = fleet_service_role
        self.tags = tags or []
        current_date = unix_time()
        self.created = current_date
        self.last_modified = current_date
        self.status = {"statusCode": "ACTIVE", "context": "FLEET_ACTIVE"}

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {
            "arn": self.arn,
            "name": self.name,
            "id": str(self.fleet_id),
            "created": self.created,
            "lastModified": self.last_modified,
            "status": self.status,
            "baseCapacity": self.base_capacity,
            "environmentType": self.environment_type,
            "computeType": self.compute_type,
            "overflowBehavior": self.overflow_behavior,
            "tags": self.tags,
        }
        if self.scaling_configuration:
            result["scalingConfiguration"] = self.scaling_configuration
        if self.compute_configuration:
            result["computeConfiguration"] = self.compute_configuration
        if self.vpc_config:
            result["vpcConfig"] = self.vpc_config
        if self.proxy_configuration:
            result["proxyConfiguration"] = self.proxy_configuration
        if self.image_id:
            result["imageId"] = self.image_id
        if self.fleet_service_role:
            result["fleetServiceRole"] = self.fleet_service_role
        return result


class BuildBatch(BaseModel):
    def __init__(
        self,
        account_id: str,
        region_name: str,
        project_name: str,
        build_batch_id: str,
        service_role: str,
        source_version: Optional[str],
    ):
        partition = get_partition(region_name)
        current_date = iso_8601_datetime_with_milliseconds()
        self.metadata: dict[str, Any] = {
            "id": build_batch_id,
            "arn": f"arn:{partition}:codebuild:{region_name}:{account_id}:build-batch/{build_batch_id}",
            "startTime": current_date,
            "currentPhase": "SUBMITTED",
            "buildBatchStatus": "IN_PROGRESS",
            "projectName": project_name,
            "sourceVersion": source_version or "refs/heads/main",
            "phases": [
                {
                    "phaseType": "SUBMITTED",
                    "phaseStatus": "SUCCEEDED",
                    "startTime": current_date,
                    "endTime": current_date,
                    "durationInSeconds": 0,
                }
            ],
            "source": {"type": "NO_SOURCE"},
            "artifacts": {"type": "NO_ARTIFACTS"},
            "cache": {"type": "NO_CACHE"},
            "environment": {
                "type": "LINUX_CONTAINER",
                "image": "aws/codebuild/amazonlinux2-x86_64-standard:3.0",
                "computeType": "BUILD_GENERAL1_SMALL",
                "environmentVariables": [],
                "privilegedMode": False,
                "imagePullCredentialsType": "CODEBUILD",
            },
            "serviceRole": service_role,
            "encryptionKey": f"arn:{partition}:kms:{region_name}:{account_id}:alias/aws/s3",
            "buildGroups": [],
            "buildBatchNumber": mock_random.randint(1, 100),
            "complete": False,
            "initiator": "rootme",
        }


class Sandbox(BaseModel):
    def __init__(
        self,
        account_id: str,
        region_name: str,
        project_name: Optional[str],
        sandbox_id: str,
    ):
        partition = get_partition(region_name)
        current_date = iso_8601_datetime_with_milliseconds()
        self.sandbox_id = sandbox_id
        self.project_name = project_name
        self.metadata: dict[str, Any] = {
            "id": sandbox_id,
            "arn": f"arn:{partition}:codebuild:{region_name}:{account_id}:sandbox/{sandbox_id}",
            "projectName": project_name or "",
            "startTime": current_date,
            "status": "RUNNING",
        }


class CodeBuildBackend(BaseBackend):
    def __init__(self, region_name: str, account_id: str):
        super().__init__(region_name, account_id)
        self.codebuild_projects: dict[str, CodeBuild] = {}
        self.build_history: dict[str, list[str]] = {}
        self.build_metadata: dict[str, CodeBuildProjectMetadata] = {}
        self.build_metadata_history: dict[str, list[dict[str, Any]]] = defaultdict(list)
        self.webhooks: dict[str, Webhook] = {}
        self.source_credentials: dict[str, SourceCredential] = {}
        self.report_groups: dict[str, ReportGroup] = {}
        self.reports: dict[str, dict[str, Any]] = {}
        self.fleets: dict[str, Fleet] = {}
        self.resource_policies: dict[str, str] = {}
        self.build_batches: dict[str, BuildBatch] = {}
        self.build_batch_history: dict[str, list[str]] = defaultdict(list)
        self.sandboxes: dict[str, Sandbox] = {}
        self.sandbox_history: dict[str, list[str]] = defaultdict(list)
        self.command_executions: dict[str, dict[str, Any]] = {}

    # ---- Project operations ----

    def create_project(
        self,
        project_name: str,
        description: Optional[str],
        project_source: dict[str, Any],
        artifacts: dict[str, Any],
        environment: dict[str, Any],
        service_role: str,
        tags: Optional[list[dict[str, str]]],
        cache: Optional[dict[str, Any]],
        timeout: Optional[int],
        queued_timeout: Optional[int],
        source_version: Optional[str],
        logs_config: Optional[dict[str, Any]],
        vpc_config: Optional[dict[str, Any]],
    ) -> dict[str, Any]:
        self.codebuild_projects[project_name] = CodeBuild(
            self.account_id,
            self.region_name,
            project_name=project_name,
            description=description,
            project_source=project_source,
            artifacts=artifacts,
            environment=environment,
            serviceRole=service_role,
            tags=tags,
            cache=cache,
            timeout=timeout,
            queued_timeout=queued_timeout,
            source_version=source_version,
            logs_config=logs_config,
            vpc_config=vpc_config,
        )

        # empty build history
        self.build_history[project_name] = []

        return self.codebuild_projects[project_name].project_metadata

    def update_project(
        self,
        project_name: str,
        description: Optional[str],
        project_source: Optional[dict[str, Any]],
        artifacts: Optional[dict[str, Any]],
        environment: Optional[dict[str, Any]],
        service_role: Optional[str],
        tags: Optional[list[dict[str, str]]],
        cache: Optional[dict[str, Any]],
        timeout: Optional[int],
        queued_timeout: Optional[int],
        source_version: Optional[str],
        logs_config: Optional[dict[str, Any]],
        vpc_config: Optional[dict[str, Any]],
        encryption_key: Optional[str],
        badge_enabled: Optional[bool],
    ) -> dict[str, Any]:
        if project_name not in self.codebuild_projects:
            raise ResourceNotFoundException(
                f"The provided project arn:{get_partition(self.region_name)}:codebuild:"
                f"{self.region_name}:{self.account_id}:project/{project_name} does not exist"
            )
        project = self.codebuild_projects[project_name]
        md = project.project_metadata
        if description is not None:
            md["description"] = description
        if project_source is not None:
            md["source"] = project_source
        if artifacts is not None:
            md["artifacts"] = artifacts
        if environment is not None:
            md["environment"] = environment
        if service_role is not None:
            project.service_role = service_role
            if service_role.startswith("arn:"):
                md["serviceRole"] = service_role
            else:
                md["serviceRole"] = (
                    f"arn:{get_partition(self.region_name)}:iam::{self.account_id}"
                    f":role/service-role/{service_role}"
                )
        if tags is not None:
            md["tags"] = tags
            project.tags = tags
        if cache is not None:
            md["cache"] = cache
        if timeout is not None:
            md["timeoutInMinutes"] = timeout
        if queued_timeout is not None:
            md["queuedTimeoutInMinutes"] = queued_timeout
        if source_version is not None:
            md["sourceVersion"] = source_version
        if logs_config is not None:
            md["logsConfig"] = logs_config
        if vpc_config is not None:
            md["vpcConfig"] = vpc_config
        if encryption_key is not None:
            md["encryptionKey"] = encryption_key
        if badge_enabled is not None:
            md["badge"]["badgeEnabled"] = badge_enabled
        md["lastModifiedDate"] = unix_time()
        return md

    def update_project_visibility(
        self,
        project_arn: str,
        project_visibility: str,
        resource_access_role: Optional[str],
    ) -> dict[str, Any]:
        # Find project by ARN
        project = None
        for proj in self.codebuild_projects.values():
            if proj.arn == project_arn:
                project = proj
                break
        if project is None:
            raise ResourceNotFoundException(f"Project {project_arn} does not exist")
        project.visibility = project_visibility
        if resource_access_role:
            project.resource_access_role = resource_access_role
        public_alias = ""
        if project_visibility == "PUBLIC_READ":
            public_alias = f"{self.account_id}/{project.project_name}"
        return {
            "projectArn": project_arn,
            "publicProjectAlias": public_alias,
            "projectVisibility": project_visibility,
        }

    def list_projects(self) -> list[str]:
        projects = []

        for project in self.codebuild_projects.keys():
            projects.append(project)

        return projects

    def batch_get_projects(self, names: list[str]) -> list[dict[str, Any]]:
        result = []
        for name in names:
            if name in self.codebuild_projects:
                result.append(self.codebuild_projects[name].project_metadata)
            elif name.startswith("arn:"):
                for project in self.codebuild_projects.values():
                    if name == project.arn:
                        result.append(project.project_metadata)
        return result

    def delete_project(self, project_name: str) -> None:
        self.build_metadata.pop(project_name, None)
        self.codebuild_projects.pop(project_name, None)
        self.webhooks.pop(project_name, None)

    def invalidate_project_cache(self, project_name: str) -> None:
        if project_name not in self.codebuild_projects:
            raise ResourceNotFoundException(
                f"The provided project arn:{get_partition(self.region_name)}:codebuild:"
                f"{self.region_name}:{self.account_id}:project/{project_name} does not exist"
            )

    def list_shared_projects(self) -> list[str]:
        # Shared projects require RAM sharing, which we don't implement.
        # Return empty list like LocalStack does.
        return []

    # ---- Build operations ----

    def start_build(
        self,
        project_name: str,
        source_version: Optional[str] = None,
        artifact_override: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        project = self.codebuild_projects[project_name]
        build_id = f"{project_name}:{mock_random.uuid4()}"

        # construct a new build
        self.build_metadata[project_name] = CodeBuildProjectMetadata(
            self.account_id,
            self.region_name,
            project_name,
            source_version,
            artifact_override,
            build_id,
            project.service_role,
        )

        self.build_history[project_name].append(build_id)

        # update build histroy with metadata for build id
        self.build_metadata_history[project_name].append(
            self.build_metadata[project_name].build_metadata
        )

        return self.build_metadata[project_name].build_metadata

    def retry_build(self, build_id: Optional[str]) -> Optional[dict[str, Any]]:
        if not build_id:
            raise InvalidInputException("Build ID is required")
        # Find original build
        original = None
        for metadata in self.build_metadata_history.values():
            for build in metadata:
                if build["id"] == build_id:
                    original = build
                    break
            if original:
                break
        if original is None:
            raise ResourceNotFoundException(f"Build {build_id} does not exist")
        # Start a new build for the same project
        project_name = original["projectName"]
        return self.start_build(
            project_name,
            source_version=original.get("sourceVersion"),
        )

    def _set_phases(self, phases: list[dict[str, Any]]) -> list[dict[str, Any]]:
        current_date = iso_8601_datetime_with_milliseconds()
        # No phaseStatus for QUEUED on first start
        for existing_phase in phases:
            if existing_phase["phaseType"] == "QUEUED":
                existing_phase["phaseStatus"] = "SUCCEEDED"

        statuses = [
            "PROVISIONING",
            "DOWNLOAD_SOURCE",
            "INSTALL",
            "PRE_BUILD",
            "BUILD",
            "POST_BUILD",
            "UPLOAD_ARTIFACTS",
            "FINALIZING",
            "COMPLETED",
        ]

        for status in statuses:
            phase: dict[str, Any] = {}
            phase["phaseType"] = status
            phase["phaseStatus"] = "SUCCEEDED"
            phase["startTime"] = current_date
            phase["endTime"] = current_date
            phase["durationInSeconds"] = mock_random.randint(10, 100)
            phases.append(phase)

        return phases

    def batch_get_builds(self, ids: list[str]) -> list[dict[str, Any]]:
        batch_build_metadata: list[dict[str, Any]] = []

        for metadata in self.build_metadata_history.values():
            for build in metadata:
                if build["id"] in ids:
                    build["phases"] = self._set_phases(build["phases"])
                    build["endTime"] = iso_8601_datetime_with_milliseconds(
                        parser.parse(build["startTime"])
                        + datetime.timedelta(minutes=mock_random.randint(1, 5))
                    )
                    build["currentPhase"] = "COMPLETED"
                    build["buildStatus"] = "SUCCEEDED"

                    batch_build_metadata.append(build)

        return batch_build_metadata

    def batch_delete_builds(
        self, ids: list[str]
    ) -> tuple[list[str], list[dict[str, Any]]]:
        deleted: list[str] = []
        not_deleted: list[dict[str, Any]] = []
        for build_id in ids:
            found = False
            for project_name, metadata_list in self.build_metadata_history.items():
                for i, build in enumerate(metadata_list):
                    if build["id"] == build_id:
                        metadata_list.pop(i)
                        if build_id in self.build_history.get(project_name, []):
                            self.build_history[project_name].remove(build_id)
                        deleted.append(build_id)
                        found = True
                        break
                if found:
                    break
            if not found:
                not_deleted.append({"id": build_id, "statusCode": "BUILD_NOT_FOUND"})
        return deleted, not_deleted

    def list_builds_for_project(self, project_name: str) -> list[str]:
        try:
            return self.build_history[project_name]
        except KeyError:
            return []

    def list_builds(self) -> list[str]:
        ids = []

        for build_ids in self.build_history.values():
            ids += build_ids
        return ids

    def stop_build(self, build_id: str) -> Optional[dict[str, Any]]:  # type: ignore[return]
        for metadata in self.build_metadata_history.values():
            for build in metadata:
                if build["id"] == build_id:
                    # set completion properties with variable completion time
                    build["phases"] = self._set_phases(build["phases"])
                    build["endTime"] = iso_8601_datetime_with_milliseconds(
                        parser.parse(build["startTime"])
                        + datetime.timedelta(minutes=mock_random.randint(1, 5))
                    )
                    build["currentPhase"] = "COMPLETED"
                    build["buildStatus"] = "STOPPED"

                    return build

    # ---- Build batch operations ----

    def start_build_batch(
        self,
        project_name: str,
        source_version: Optional[str] = None,
    ) -> dict[str, Any]:
        if project_name not in self.codebuild_projects:
            raise ResourceNotFoundException(
                f"Project cannot be found: arn:{get_partition(self.region_name)}:codebuild:"
                f"{self.region_name}:{self.account_id}:project/{project_name}"
            )
        project = self.codebuild_projects[project_name]
        batch_id = f"{project_name}:{mock_random.uuid4()}"
        bb = BuildBatch(
            self.account_id,
            self.region_name,
            project_name,
            batch_id,
            project.service_role,
            source_version,
        )
        self.build_batches[batch_id] = bb
        self.build_batch_history[project_name].append(batch_id)
        return bb.metadata

    def stop_build_batch(self, batch_id: str) -> dict[str, Any]:
        if batch_id not in self.build_batches:
            raise ResourceNotFoundException(f"Build batch {batch_id} does not exist")
        bb = self.build_batches[batch_id]
        bb.metadata["buildBatchStatus"] = "STOPPED"
        bb.metadata["currentPhase"] = "STOPPED"
        bb.metadata["endTime"] = iso_8601_datetime_with_milliseconds()
        bb.metadata["complete"] = True
        return bb.metadata

    def delete_build_batch(
        self, batch_id: str
    ) -> tuple[str, list[str], list[dict[str, Any]]]:
        if batch_id not in self.build_batches:
            raise ResourceNotFoundException(f"Build batch {batch_id} does not exist")
        bb = self.build_batches.pop(batch_id)
        project_name = bb.metadata["projectName"]
        if batch_id in self.build_batch_history.get(project_name, []):
            self.build_batch_history[project_name].remove(batch_id)
        return "200", [batch_id], []

    def retry_build_batch(
        self, batch_id: Optional[str]
    ) -> dict[str, Any]:
        if not batch_id:
            raise InvalidInputException("Build batch ID is required")
        if batch_id not in self.build_batches:
            raise ResourceNotFoundException(f"Build batch {batch_id} does not exist")
        original = self.build_batches[batch_id]
        project_name = original.metadata["projectName"]
        return self.start_build_batch(project_name)

    def list_build_batches(self) -> list[str]:
        return list(self.build_batches.keys())

    def list_build_batches_for_project(
        self, project_name: Optional[str]
    ) -> list[str]:
        if project_name and project_name not in self.codebuild_projects:
            raise ResourceNotFoundException(
                f"The provided project arn:{get_partition(self.region_name)}:codebuild:"
                f"{self.region_name}:{self.account_id}:project/{project_name} does not exist"
            )
        if project_name:
            return self.build_batch_history.get(project_name, [])
        return list(self.build_batches.keys())

    def batch_get_build_batches(
        self, ids: list[str]
    ) -> tuple[list[dict[str, Any]], list[str]]:
        found: list[dict[str, Any]] = []
        not_found: list[str] = []
        for batch_id in ids:
            if batch_id in self.build_batches:
                found.append(self.build_batches[batch_id].metadata)
            else:
                not_found.append(batch_id)
        return found, not_found

    # ---- Webhook operations ----

    def create_webhook(
        self,
        project_name: str,
        branch_filter: Optional[str],
        filter_groups: Optional[list[list[dict[str, Any]]]],
        build_type: Optional[str],
    ) -> dict[str, Any]:
        if project_name not in self.codebuild_projects:
            raise ResourceNotFoundException(
                f"The provided project arn:{get_partition(self.region_name)}:codebuild:"
                f"{self.region_name}:{self.account_id}:project/{project_name} does not exist"
            )
        if project_name in self.webhooks:
            from .exceptions import ResourceAlreadyExistsException

            raise ResourceAlreadyExistsException(
                f"Webhook already exists for project: {project_name}"
            )
        wh = Webhook(
            self.account_id,
            self.region_name,
            project_name,
            branch_filter,
            filter_groups,
            build_type,
        )
        self.webhooks[project_name] = wh
        return wh.to_dict()

    def update_webhook(
        self,
        project_name: str,
        branch_filter: Optional[str],
        filter_groups: Optional[list[list[dict[str, Any]]]],
        build_type: Optional[str],
        rotate_secret: Optional[bool],
    ) -> dict[str, Any]:
        if project_name not in self.webhooks:
            raise ResourceNotFoundException(
                f"No webhook found for project: {project_name}"
            )
        wh = self.webhooks[project_name]
        if branch_filter is not None:
            wh.branch_filter = branch_filter
        if filter_groups is not None:
            wh.filter_groups = filter_groups
        if build_type is not None:
            wh.build_type = build_type
        if rotate_secret:
            wh.secret = mock_random.get_random_hex(40)
            wh.last_modified_secret = unix_time()
        return wh.to_dict()

    def delete_webhook(self, project_name: str) -> None:
        if project_name not in self.webhooks:
            raise ResourceNotFoundException(
                f"No webhook found for project: {project_name}"
            )
        self.webhooks.pop(project_name)

    # ---- Source credential operations ----

    def import_source_credentials(
        self,
        token: str,
        server_type: str,
        auth_type: str,
        username: Optional[str],
        should_overwrite: Optional[bool],
    ) -> str:
        existing = self.source_credentials.get(server_type)
        if existing and not should_overwrite:
            from .exceptions import ResourceAlreadyExistsException

            raise ResourceAlreadyExistsException(
                f"Source credentials for type {server_type} already exist"
            )
        cred = SourceCredential(
            self.account_id,
            self.region_name,
            token,
            server_type,
            auth_type,
            username,
        )
        self.source_credentials[server_type] = cred
        return cred.arn

    def delete_source_credentials(self, arn: str) -> str:
        for key, cred in self.source_credentials.items():
            if cred.arn == arn:
                self.source_credentials.pop(key)
                return arn
        raise ResourceNotFoundException(f"Source credentials {arn} not found")

    def list_source_credentials(self) -> list[dict[str, Any]]:
        return [cred.to_info_dict() for cred in self.source_credentials.values()]

    # ---- Report group operations ----

    def create_report_group(
        self,
        name: str,
        report_type: str,
        export_config: dict[str, Any],
        tags: Optional[list[dict[str, str]]],
    ) -> dict[str, Any]:
        if name in self.report_groups:
            from .exceptions import ResourceAlreadyExistsException

            raise ResourceAlreadyExistsException(
                f"Report group already exists: {name}"
            )
        rg = ReportGroup(
            self.account_id,
            self.region_name,
            name,
            report_type,
            export_config,
            tags,
        )
        self.report_groups[name] = rg
        return rg.to_dict()

    def update_report_group(
        self,
        arn: str,
        export_config: Optional[dict[str, Any]],
        tags: Optional[list[dict[str, str]]],
    ) -> dict[str, Any]:
        rg = None
        for group in self.report_groups.values():
            if group.arn == arn:
                rg = group
                break
        if rg is None:
            raise ResourceNotFoundException(f"Report group {arn} does not exist")
        if export_config is not None:
            rg.export_config = export_config
        if tags is not None:
            rg.tags = tags
        rg.last_modified = unix_time()
        return rg.to_dict()

    def delete_report_group(self, arn: str) -> None:
        to_delete = None
        for name, rg in self.report_groups.items():
            if rg.arn == arn:
                to_delete = name
                break
        if to_delete is None:
            raise ResourceNotFoundException(f"Report group {arn} does not exist")
        self.report_groups.pop(to_delete)
        # Also delete associated reports
        to_remove = [
            r_arn for r_arn, r in self.reports.items()
            if r.get("reportGroupArn") == arn
        ]
        for r_arn in to_remove:
            self.reports.pop(r_arn)

    def batch_get_report_groups(
        self, arns: list[str]
    ) -> tuple[list[dict[str, Any]], list[str]]:
        found: list[dict[str, Any]] = []
        not_found: list[str] = []
        for arn in arns:
            matched = False
            for rg in self.report_groups.values():
                if rg.arn == arn:
                    found.append(rg.to_dict())
                    matched = True
                    break
            if not matched:
                not_found.append(arn)
        return found, not_found

    def list_report_groups(self) -> list[str]:
        return [rg.arn for rg in self.report_groups.values()]

    def list_shared_report_groups(self) -> list[str]:
        return []

    # ---- Report operations ----

    def list_reports(self) -> list[str]:
        return list(self.reports.keys())

    def list_reports_for_report_group(self, report_group_arn: str) -> list[str]:
        return [
            arn for arn, r in self.reports.items()
            if r.get("reportGroupArn") == report_group_arn
        ]

    def delete_report(self, arn: str) -> None:
        self.reports.pop(arn, None)

    def batch_get_reports(
        self, arns: list[str]
    ) -> tuple[list[dict[str, Any]], list[str]]:
        found: list[dict[str, Any]] = []
        not_found: list[str] = []
        for arn in arns:
            if arn in self.reports:
                found.append(self.reports[arn])
            else:
                not_found.append(arn)
        return found, not_found

    def describe_test_cases(self, report_arn: str) -> list[dict[str, Any]]:
        # Returns empty since we don't actually run tests
        return []

    def describe_code_coverages(self, report_arn: str) -> list[dict[str, Any]]:
        return []

    def get_report_group_trend(
        self, report_group_arn: str, trend_field: str
    ) -> tuple[dict[str, Any], list[dict[str, Any]]]:
        stats: dict[str, Any] = {}
        raw_data: list[dict[str, Any]] = []
        return stats, raw_data

    # ---- Fleet operations ----

    def create_fleet(
        self,
        name: str,
        base_capacity: int,
        environment_type: str,
        compute_type: str,
        compute_configuration: Optional[dict[str, Any]],
        scaling_configuration: Optional[dict[str, Any]],
        overflow_behavior: Optional[str],
        vpc_config: Optional[dict[str, Any]],
        proxy_configuration: Optional[dict[str, Any]],
        image_id: Optional[str],
        fleet_service_role: Optional[str],
        tags: Optional[list[dict[str, str]]],
    ) -> dict[str, Any]:
        fleet = Fleet(
            self.account_id,
            self.region_name,
            name,
            base_capacity,
            environment_type,
            compute_type,
            compute_configuration,
            scaling_configuration,
            overflow_behavior,
            vpc_config,
            proxy_configuration,
            image_id,
            fleet_service_role,
            tags,
        )
        self.fleets[fleet.arn] = fleet
        return fleet.to_dict()

    def update_fleet(
        self,
        arn: str,
        base_capacity: Optional[int],
        environment_type: Optional[str],
        compute_type: Optional[str],
        compute_configuration: Optional[dict[str, Any]],
        scaling_configuration: Optional[dict[str, Any]],
        overflow_behavior: Optional[str],
        vpc_config: Optional[dict[str, Any]],
        proxy_configuration: Optional[dict[str, Any]],
        image_id: Optional[str],
        fleet_service_role: Optional[str],
        tags: Optional[list[dict[str, str]]],
    ) -> dict[str, Any]:
        if arn not in self.fleets:
            raise ResourceNotFoundException(f"Fleet {arn} does not exist")
        fleet = self.fleets[arn]
        if base_capacity is not None:
            fleet.base_capacity = base_capacity
        if environment_type is not None:
            fleet.environment_type = environment_type
        if compute_type is not None:
            fleet.compute_type = compute_type
        if compute_configuration is not None:
            fleet.compute_configuration = compute_configuration
        if scaling_configuration is not None:
            fleet.scaling_configuration = scaling_configuration
        if overflow_behavior is not None:
            fleet.overflow_behavior = overflow_behavior
        if vpc_config is not None:
            fleet.vpc_config = vpc_config
        if proxy_configuration is not None:
            fleet.proxy_configuration = proxy_configuration
        if image_id is not None:
            fleet.image_id = image_id
        if fleet_service_role is not None:
            fleet.fleet_service_role = fleet_service_role
        if tags is not None:
            fleet.tags = tags
        fleet.last_modified = unix_time()
        return fleet.to_dict()

    def delete_fleet(self, arn: str) -> None:
        if arn not in self.fleets:
            raise ResourceNotFoundException(f"Fleet {arn} does not exist")
        self.fleets.pop(arn)

    def batch_get_fleets(
        self, names: list[str]
    ) -> tuple[list[dict[str, Any]], list[str]]:
        found: list[dict[str, Any]] = []
        not_found: list[str] = []
        for name in names:
            if name in self.fleets:
                found.append(self.fleets[name].to_dict())
            else:
                # Check by name field too
                matched = False
                for fleet in self.fleets.values():
                    if fleet.name == name or fleet.arn == name:
                        found.append(fleet.to_dict())
                        matched = True
                        break
                if not matched:
                    not_found.append(name)
        return found, not_found

    def list_fleets(self) -> list[str]:
        return [fleet.arn for fleet in self.fleets.values()]

    # ---- Resource policy operations ----

    def put_resource_policy(self, policy: str, resource_arn: str) -> str:
        self.resource_policies[resource_arn] = policy
        return resource_arn

    def get_resource_policy(self, resource_arn: str) -> str:
        if resource_arn not in self.resource_policies:
            raise ResourceNotFoundException(
                f"Resource policy for {resource_arn} does not exist"
            )
        return self.resource_policies[resource_arn]

    def delete_resource_policy(self, resource_arn: str) -> None:
        if resource_arn not in self.resource_policies:
            raise ResourceNotFoundException(
                f"Resource policy for {resource_arn} does not exist"
            )
        self.resource_policies.pop(resource_arn)

    # ---- Curated environment images ----

    def list_curated_environment_images(self) -> list[dict[str, Any]]:
        # Return a static list of curated platforms similar to AWS
        return [
            {
                "languageName": "DOCKER",
                "images": [
                    {
                        "name": "aws/codebuild/amazonlinux2-x86_64-standard:3.0",
                        "description": "Amazon Linux 2 standard image 3.0",
                    },
                    {
                        "name": "aws/codebuild/amazonlinux2-x86_64-standard:4.0",
                        "description": "Amazon Linux 2 standard image 4.0",
                    },
                ],
            }
        ]

    # ---- Sandbox operations ----

    def start_sandbox(
        self, project_name: Optional[str]
    ) -> dict[str, Any]:
        sandbox_id = str(mock_random.uuid4())
        sandbox = Sandbox(
            self.account_id,
            self.region_name,
            project_name,
            sandbox_id,
        )
        self.sandboxes[sandbox_id] = sandbox
        if project_name:
            self.sandbox_history[project_name].append(sandbox_id)
        return sandbox.metadata

    def stop_sandbox(self, sandbox_id: str) -> dict[str, Any]:
        if sandbox_id not in self.sandboxes:
            raise ResourceNotFoundException(f"Sandbox {sandbox_id} does not exist")
        sandbox = self.sandboxes[sandbox_id]
        sandbox.metadata["status"] = "STOPPED"
        sandbox.metadata["endTime"] = iso_8601_datetime_with_milliseconds()
        return sandbox.metadata

    def batch_get_sandboxes(
        self, ids: list[str]
    ) -> tuple[list[dict[str, Any]], list[str]]:
        found: list[dict[str, Any]] = []
        not_found: list[str] = []
        for sid in ids:
            if sid in self.sandboxes:
                found.append(self.sandboxes[sid].metadata)
            else:
                not_found.append(sid)
        return found, not_found

    def list_sandboxes(self) -> list[str]:
        return list(self.sandboxes.keys())

    def list_sandboxes_for_project(self, project_name: str) -> list[str]:
        return self.sandbox_history.get(project_name, [])

    def start_sandbox_connection(
        self, sandbox_id: str
    ) -> dict[str, Any]:
        if sandbox_id not in self.sandboxes:
            raise ResourceNotFoundException(f"Sandbox {sandbox_id} does not exist")
        return {
            "sessionId": str(mock_random.uuid4()),
            "streamUrl": f"wss://ssm.{self.region_name}.amazonaws.com/ssm-session/{sandbox_id}",
            "tokenValue": mock_random.get_random_hex(64),
        }

    # ---- Command execution operations ----

    def start_command_execution(
        self, sandbox_id: str, command: str, cmd_type: Optional[str]
    ) -> dict[str, Any]:
        if sandbox_id not in self.sandboxes:
            raise ResourceNotFoundException(f"Sandbox {sandbox_id} does not exist")
        exec_id = str(mock_random.uuid4())
        execution: dict[str, Any] = {
            "id": exec_id,
            "sandboxId": sandbox_id,
            "command": command,
            "type": cmd_type or "SHELL",
            "status": "IN_PROGRESS",
            "submitTime": iso_8601_datetime_with_milliseconds(),
        }
        self.command_executions[exec_id] = execution
        return execution

    def list_command_executions_for_sandbox(
        self, sandbox_id: str
    ) -> list[dict[str, Any]]:
        return [
            ex for ex in self.command_executions.values()
            if ex.get("sandboxId") == sandbox_id
        ]

    def batch_get_command_executions(
        self, sandbox_id: str, command_execution_ids: list[str]
    ) -> tuple[list[dict[str, Any]], list[str]]:
        found: list[dict[str, Any]] = []
        not_found: list[str] = []
        for eid in command_execution_ids:
            if eid in self.command_executions:
                ex = self.command_executions[eid]
                if ex.get("sandboxId") == sandbox_id:
                    found.append(ex)
                else:
                    not_found.append(eid)
            else:
                not_found.append(eid)
        return found, not_found


codebuild_backends = BackendDict(CodeBuildBackend, "codebuild")
