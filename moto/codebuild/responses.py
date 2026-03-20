import json
import re
from typing import Any

from moto.core.responses import BaseResponse
from moto.utilities.utils import get_partition

from .exceptions import (
    InvalidInputException,
    ResourceAlreadyExistsException,
    ResourceNotFoundException,
)
from .models import CodeBuildBackend, codebuild_backends


def _validate_required_params_source(source: dict[str, Any]) -> None:
    if source["type"] not in [
        "BITBUCKET",
        "CODECOMMIT",
        "CODEPIPELINE",
        "GITHUB",
        "GITHUB_ENTERPRISE",
        "NO_SOURCE",
        "S3",
    ]:
        raise InvalidInputException("Invalid type provided: Project source type")

    if "location" not in source:
        raise InvalidInputException("Project source location is required")

    if source["location"] == "":
        raise InvalidInputException("Project source location is required")


def _validate_required_params_service_role(
    account_id: str, region_name: str, service_role: str
) -> None:
    if not service_role.startswith(
        f"arn:{get_partition(region_name)}:iam::{account_id}:role/"
    ):
        raise InvalidInputException(
            "Invalid service role: Service role account ID does not match caller's account"
        )


def _validate_required_params_artifacts(artifacts: dict[str, Any]) -> None:
    if artifacts["type"] not in ["CODEPIPELINE", "S3", "NO_ARTIFACTS"]:
        raise InvalidInputException("Invalid type provided: Artifact type")

    if artifacts["type"] == "NO_ARTIFACTS":
        if "location" in artifacts:
            raise InvalidInputException(
                "Invalid artifacts: artifact type NO_ARTIFACTS should have null location"
            )
    elif "location" not in artifacts or artifacts["location"] == "":
        raise InvalidInputException("Project source location is required")


def _validate_required_params_environment(environment: dict[str, Any]) -> None:
    if environment["type"] not in [
        "WINDOWS_CONTAINER",
        "LINUX_CONTAINER",
        "LINUX_GPU_CONTAINER",
        "ARM_CONTAINER",
    ]:
        raise InvalidInputException(f"Invalid type provided: {environment['type']}")

    if environment["computeType"] not in [
        "BUILD_GENERAL1_SMALL",
        "BUILD_GENERAL1_MEDIUM",
        "BUILD_GENERAL1_LARGE",
        "BUILD_GENERAL1_2XLARGE",
    ]:
        raise InvalidInputException(
            f"Invalid compute type provided: {environment['computeType']}"
        )


def _validate_required_params_project_name(name: str) -> None:
    if len(name) >= 150:
        raise InvalidInputException(
            "Only alphanumeric characters, dash, and underscore are supported"
        )

    if not re.match(r"^[A-Za-z]{1}.*[^!£$%^&*()+=|?`¬{}@~#:;<>\\/\[\]]$", name):
        raise InvalidInputException(
            "Only alphanumeric characters, dash, and underscore are supported"
        )


def _validate_required_params_id(build_id: str, build_ids: list[str]) -> None:
    if ":" not in build_id:
        raise InvalidInputException("Invalid build ID provided")

    if build_id not in build_ids:
        raise ResourceNotFoundException(f"Build {build_id} does not exist")


class CodeBuildResponse(BaseResponse):
    @property
    def codebuild_backend(self) -> CodeBuildBackend:
        return codebuild_backends[self.current_account][self.region]

    # ---- Project operations ----

    def create_project(self) -> str:
        _validate_required_params_source(self._get_param("source"))
        service_role = self._get_param("serviceRole")
        _validate_required_params_service_role(
            self.current_account, self.region, service_role
        )
        _validate_required_params_artifacts(self._get_param("artifacts"))
        _validate_required_params_environment(self._get_param("environment"))
        _validate_required_params_project_name(self._get_param("name"))

        if self._get_param("name") in self.codebuild_backend.codebuild_projects.keys():
            name = self._get_param("name")
            raise ResourceAlreadyExistsException(
                f"Project already exists: arn:{get_partition(self.region)}:codebuild:{self.region}:{self.current_account}:project/{name}"
            )

        project_metadata = self.codebuild_backend.create_project(
            project_name=self._get_param("name"),
            description=self._get_param("description"),
            project_source=self._get_param("source"),
            artifacts=self._get_param("artifacts"),
            environment=self._get_param("environment"),
            service_role=service_role,
            tags=self._get_param("tags"),
            cache=self._get_param("cache"),
            timeout=self._get_param("timeoutInMinutes"),
            queued_timeout=self._get_param("queuedTimeoutInMinutes"),
            source_version=self._get_param("sourceVersion"),
            logs_config=self._get_param("logsConfig"),
            vpc_config=self._get_param("vpcConfig"),
        )

        return json.dumps({"project": project_metadata})

    def update_project(self) -> str:
        name = self._get_param("name")
        if not name:
            raise InvalidInputException("Project name is required")
        _validate_required_params_project_name(name)

        source = self._get_param("source")
        if source:
            _validate_required_params_source(source)
        service_role = self._get_param("serviceRole")
        if service_role:
            _validate_required_params_service_role(
                self.current_account, self.region, service_role
            )
        artifacts = self._get_param("artifacts")
        if artifacts:
            _validate_required_params_artifacts(artifacts)
        environment = self._get_param("environment")
        if environment:
            _validate_required_params_environment(environment)

        project_metadata = self.codebuild_backend.update_project(
            project_name=name,
            description=self._get_param("description"),
            project_source=source,
            artifacts=artifacts,
            environment=environment,
            service_role=service_role,
            tags=self._get_param("tags"),
            cache=self._get_param("cache"),
            timeout=self._get_param("timeoutInMinutes"),
            queued_timeout=self._get_param("queuedTimeoutInMinutes"),
            source_version=self._get_param("sourceVersion"),
            logs_config=self._get_param("logsConfig"),
            vpc_config=self._get_param("vpcConfig"),
            encryption_key=self._get_param("encryptionKey"),
            badge_enabled=self._get_param("badgeEnabled"),
        )

        return json.dumps({"project": project_metadata})

    def update_project_visibility(self) -> str:
        project_arn = self._get_param("projectArn")
        project_visibility = self._get_param("projectVisibility")
        resource_access_role = self._get_param("resourceAccessRole")
        if not project_arn:
            raise InvalidInputException("Project ARN is required")
        if not project_visibility:
            raise InvalidInputException("Project visibility is required")
        result = self.codebuild_backend.update_project_visibility(
            project_arn, project_visibility, resource_access_role
        )
        return json.dumps(result)

    def list_projects(self) -> str:
        project_metadata = self.codebuild_backend.list_projects()
        return json.dumps({"projects": project_metadata})

    def batch_get_projects(self) -> str:
        names = self._get_param("names")
        project_metadata = self.codebuild_backend.batch_get_projects(names)
        return json.dumps({"projects": project_metadata})

    def delete_project(self) -> str:
        _validate_required_params_project_name(self._get_param("name"))

        self.codebuild_backend.delete_project(self._get_param("name"))
        return "{}"

    def invalidate_project_cache(self) -> str:
        project_name = self._get_param("projectName")
        if not project_name:
            raise InvalidInputException("Project name is required")
        _validate_required_params_project_name(project_name)
        self.codebuild_backend.invalidate_project_cache(project_name)
        return "{}"

    def list_shared_projects(self) -> str:
        projects = self.codebuild_backend.list_shared_projects()
        return json.dumps({"projects": projects})

    # ---- Build operations ----

    def start_build(self) -> str:
        _validate_required_params_project_name(self._get_param("projectName"))

        if (
            self._get_param("projectName")
            not in self.codebuild_backend.codebuild_projects.keys()
        ):
            name = self._get_param("projectName")
            raise ResourceNotFoundException(
                f"Project cannot be found: arn:{get_partition(self.region)}:codebuild:{self.region}:{self.current_account}:project/{name}"
            )

        metadata = self.codebuild_backend.start_build(
            self._get_param("projectName"),
            self._get_param("sourceVersion"),
            self._get_param("artifactsOverride"),
        )
        return json.dumps({"build": metadata})

    def retry_build(self) -> str:
        build_id = self._get_param("id")
        metadata = self.codebuild_backend.retry_build(build_id)
        return json.dumps({"build": metadata})

    def batch_get_builds(self) -> str:
        for build_id in self._get_param("ids"):
            if ":" not in build_id:
                raise InvalidInputException("Invalid build ID provided")

        metadata = self.codebuild_backend.batch_get_builds(self._get_param("ids"))
        return json.dumps({"builds": metadata})

    def batch_delete_builds(self) -> str:
        ids = self._get_param("ids")
        if not ids:
            raise InvalidInputException("Build IDs are required")
        deleted, not_deleted = self.codebuild_backend.batch_delete_builds(ids)
        return json.dumps({"buildsDeleted": deleted, "buildsNotDeleted": not_deleted})

    def list_builds(self) -> str:
        ids = self.codebuild_backend.list_builds()
        return json.dumps({"ids": ids})

    def list_builds_for_project(self) -> str:
        _validate_required_params_project_name(self._get_param("projectName"))

        if (
            self._get_param("projectName")
            not in self.codebuild_backend.codebuild_projects.keys()
        ):
            name = self._get_param("projectName")
            raise ResourceNotFoundException(
                f"The provided project arn:{get_partition(self.region)}:codebuild:{self.region}:{self.current_account}:project/{name} does not exist"
            )

        ids = self.codebuild_backend.list_builds_for_project(
            self._get_param("projectName")
        )

        return json.dumps({"ids": ids})

    def stop_build(self) -> str:
        _validate_required_params_id(
            self._get_param("id"), self.codebuild_backend.list_builds()
        )

        metadata = self.codebuild_backend.stop_build(self._get_param("id"))
        return json.dumps({"build": metadata})

    # ---- Build batch operations ----

    def start_build_batch(self) -> str:
        project_name = self._get_param("projectName")
        if not project_name:
            raise InvalidInputException("Project name is required")
        _validate_required_params_project_name(project_name)
        metadata = self.codebuild_backend.start_build_batch(
            project_name,
            self._get_param("sourceVersion"),
        )
        return json.dumps({"buildBatch": metadata})

    def stop_build_batch(self) -> str:
        batch_id = self._get_param("id")
        if not batch_id:
            raise InvalidInputException("Build batch ID is required")
        metadata = self.codebuild_backend.stop_build_batch(batch_id)
        return json.dumps({"buildBatch": metadata})

    def delete_build_batch(self) -> str:
        batch_id = self._get_param("id")
        if not batch_id:
            raise InvalidInputException("Build batch ID is required")
        status_code, deleted, not_deleted = self.codebuild_backend.delete_build_batch(
            batch_id
        )
        return json.dumps({
            "statusCode": status_code,
            "buildsDeleted": deleted,
            "buildsNotDeleted": not_deleted,
        })

    def retry_build_batch(self) -> str:
        batch_id = self._get_param("id")
        metadata = self.codebuild_backend.retry_build_batch(batch_id)
        return json.dumps({"buildBatch": metadata})

    def list_build_batches(self) -> str:
        ids = self.codebuild_backend.list_build_batches()
        return json.dumps({"ids": ids})

    def list_build_batches_for_project(self) -> str:
        project_name = self._get_param("projectName")
        ids = self.codebuild_backend.list_build_batches_for_project(project_name)
        return json.dumps({"ids": ids})

    def batch_get_build_batches(self) -> str:
        ids = self._get_param("ids")
        if not ids:
            raise InvalidInputException("Build batch IDs are required")
        found, not_found = self.codebuild_backend.batch_get_build_batches(ids)
        return json.dumps({
            "buildBatches": found,
            "buildBatchesNotFound": not_found,
        })

    # ---- Webhook operations ----

    def create_webhook(self) -> str:
        project_name = self._get_param("projectName")
        if not project_name:
            raise InvalidInputException("Project name is required")
        webhook = self.codebuild_backend.create_webhook(
            project_name,
            self._get_param("branchFilter"),
            self._get_param("filterGroups"),
            self._get_param("buildType"),
        )
        return json.dumps({"webhook": webhook})

    def update_webhook(self) -> str:
        project_name = self._get_param("projectName")
        if not project_name:
            raise InvalidInputException("Project name is required")
        webhook = self.codebuild_backend.update_webhook(
            project_name,
            self._get_param("branchFilter"),
            self._get_param("filterGroups"),
            self._get_param("buildType"),
            self._get_param("rotateSecret"),
        )
        return json.dumps({"webhook": webhook})

    def delete_webhook(self) -> str:
        project_name = self._get_param("projectName")
        if not project_name:
            raise InvalidInputException("Project name is required")
        self.codebuild_backend.delete_webhook(project_name)
        return "{}"

    # ---- Source credential operations ----

    def import_source_credentials(self) -> str:
        token = self._get_param("token")
        server_type = self._get_param("serverType")
        auth_type = self._get_param("authType")
        username = self._get_param("username")
        should_overwrite = self._get_param("shouldOverwrite")
        if not token:
            raise InvalidInputException("Token is required")
        if not server_type:
            raise InvalidInputException("Server type is required")
        if not auth_type:
            raise InvalidInputException("Auth type is required")
        arn = self.codebuild_backend.import_source_credentials(
            token, server_type, auth_type, username, should_overwrite
        )
        return json.dumps({"arn": arn})

    def delete_source_credentials(self) -> str:
        arn = self._get_param("arn")
        if not arn:
            raise InvalidInputException("ARN is required")
        result_arn = self.codebuild_backend.delete_source_credentials(arn)
        return json.dumps({"arn": result_arn})

    def list_source_credentials(self) -> str:
        infos = self.codebuild_backend.list_source_credentials()
        return json.dumps({"sourceCredentialsInfos": infos})

    # ---- Report group operations ----

    def create_report_group(self) -> str:
        name = self._get_param("name")
        report_type = self._get_param("type")
        export_config = self._get_param("exportConfig")
        tags = self._get_param("tags")
        if not name:
            raise InvalidInputException("Report group name is required")
        if not report_type:
            raise InvalidInputException("Report group type is required")
        if not export_config:
            raise InvalidInputException("Export config is required")
        report_group = self.codebuild_backend.create_report_group(
            name, report_type, export_config, tags
        )
        return json.dumps({"reportGroup": report_group})

    def update_report_group(self) -> str:
        arn = self._get_param("arn")
        if not arn:
            raise InvalidInputException("Report group ARN is required")
        export_config = self._get_param("exportConfig")
        tags = self._get_param("tags")
        report_group = self.codebuild_backend.update_report_group(
            arn, export_config, tags
        )
        return json.dumps({"reportGroup": report_group})

    def delete_report_group(self) -> str:
        arn = self._get_param("arn")
        if not arn:
            raise InvalidInputException("Report group ARN is required")
        self.codebuild_backend.delete_report_group(arn)
        return "{}"

    def batch_get_report_groups(self) -> str:
        arns = self._get_param("reportGroupArns")
        if not arns:
            raise InvalidInputException("Report group ARNs are required")
        found, not_found = self.codebuild_backend.batch_get_report_groups(arns)
        return json.dumps({
            "reportGroups": found,
            "reportGroupsNotFound": not_found,
        })

    def list_report_groups(self) -> str:
        arns = self.codebuild_backend.list_report_groups()
        return json.dumps({"reportGroups": arns})

    def list_shared_report_groups(self) -> str:
        arns = self.codebuild_backend.list_shared_report_groups()
        return json.dumps({"reportGroups": arns})

    # ---- Report operations ----

    def list_reports(self) -> str:
        arns = self.codebuild_backend.list_reports()
        return json.dumps({"reports": arns})

    def list_reports_for_report_group(self) -> str:
        report_group_arn = self._get_param("reportGroupArn")
        if not report_group_arn:
            raise InvalidInputException("Report group ARN is required")
        arns = self.codebuild_backend.list_reports_for_report_group(report_group_arn)
        return json.dumps({"reports": arns})

    def delete_report(self) -> str:
        arn = self._get_param("arn")
        if not arn:
            raise InvalidInputException("Report ARN is required")
        self.codebuild_backend.delete_report(arn)
        return "{}"

    def batch_get_reports(self) -> str:
        arns = self._get_param("reportArns")
        if not arns:
            raise InvalidInputException("Report ARNs are required")
        found, not_found = self.codebuild_backend.batch_get_reports(arns)
        return json.dumps({"reports": found, "reportsNotFound": not_found})

    def describe_test_cases(self) -> str:
        report_arn = self._get_param("reportArn")
        if not report_arn:
            raise InvalidInputException("Report ARN is required")
        test_cases = self.codebuild_backend.describe_test_cases(report_arn)
        return json.dumps({"testCases": test_cases})

    def describe_code_coverages(self) -> str:
        report_arn = self._get_param("reportArn")
        if not report_arn:
            raise InvalidInputException("Report ARN is required")
        coverages = self.codebuild_backend.describe_code_coverages(report_arn)
        return json.dumps({"codeCoverages": coverages})

    def get_report_group_trend(self) -> str:
        report_group_arn = self._get_param("reportGroupArn")
        trend_field = self._get_param("trendField")
        if not report_group_arn:
            raise InvalidInputException("Report group ARN is required")
        if not trend_field:
            raise InvalidInputException("Trend field is required")
        stats, raw_data = self.codebuild_backend.get_report_group_trend(
            report_group_arn, trend_field
        )
        return json.dumps({"stats": stats, "rawData": raw_data})

    # ---- Fleet operations ----

    def create_fleet(self) -> str:
        name = self._get_param("name")
        base_capacity = self._get_param("baseCapacity")
        environment_type = self._get_param("environmentType")
        compute_type = self._get_param("computeType")
        if not name:
            raise InvalidInputException("Fleet name is required")
        if base_capacity is None:
            raise InvalidInputException("Base capacity is required")
        if not environment_type:
            raise InvalidInputException("Environment type is required")
        if not compute_type:
            raise InvalidInputException("Compute type is required")
        fleet = self.codebuild_backend.create_fleet(
            name=name,
            base_capacity=base_capacity,
            environment_type=environment_type,
            compute_type=compute_type,
            compute_configuration=self._get_param("computeConfiguration"),
            scaling_configuration=self._get_param("scalingConfiguration"),
            overflow_behavior=self._get_param("overflowBehavior"),
            vpc_config=self._get_param("vpcConfig"),
            proxy_configuration=self._get_param("proxyConfiguration"),
            image_id=self._get_param("imageId"),
            fleet_service_role=self._get_param("fleetServiceRole"),
            tags=self._get_param("tags"),
        )
        return json.dumps({"fleet": fleet})

    def update_fleet(self) -> str:
        arn = self._get_param("arn")
        if not arn:
            raise InvalidInputException("Fleet ARN is required")
        fleet = self.codebuild_backend.update_fleet(
            arn=arn,
            base_capacity=self._get_param("baseCapacity"),
            environment_type=self._get_param("environmentType"),
            compute_type=self._get_param("computeType"),
            compute_configuration=self._get_param("computeConfiguration"),
            scaling_configuration=self._get_param("scalingConfiguration"),
            overflow_behavior=self._get_param("overflowBehavior"),
            vpc_config=self._get_param("vpcConfig"),
            proxy_configuration=self._get_param("proxyConfiguration"),
            image_id=self._get_param("imageId"),
            fleet_service_role=self._get_param("fleetServiceRole"),
            tags=self._get_param("tags"),
        )
        return json.dumps({"fleet": fleet})

    def delete_fleet(self) -> str:
        arn = self._get_param("arn")
        if not arn:
            raise InvalidInputException("Fleet ARN is required")
        self.codebuild_backend.delete_fleet(arn)
        return "{}"

    def batch_get_fleets(self) -> str:
        names = self._get_param("names")
        if not names:
            raise InvalidInputException("Fleet names are required")
        found, not_found = self.codebuild_backend.batch_get_fleets(names)
        return json.dumps({"fleets": found, "fleetsNotFound": not_found})

    def list_fleets(self) -> str:
        arns = self.codebuild_backend.list_fleets()
        return json.dumps({"fleets": arns})

    # ---- Resource policy operations ----

    def put_resource_policy(self) -> str:
        policy = self._get_param("policy")
        resource_arn = self._get_param("resourceArn")
        if not policy:
            raise InvalidInputException("Policy is required")
        if not resource_arn:
            raise InvalidInputException("Resource ARN is required")
        result_arn = self.codebuild_backend.put_resource_policy(policy, resource_arn)
        return json.dumps({"resourceArn": result_arn})

    def get_resource_policy(self) -> str:
        resource_arn = self._get_param("resourceArn")
        if not resource_arn:
            raise InvalidInputException("Resource ARN is required")
        policy = self.codebuild_backend.get_resource_policy(resource_arn)
        return json.dumps({"policy": policy})

    def delete_resource_policy(self) -> str:
        resource_arn = self._get_param("resourceArn")
        if not resource_arn:
            raise InvalidInputException("Resource ARN is required")
        self.codebuild_backend.delete_resource_policy(resource_arn)
        return "{}"

    # ---- Curated environment images ----

    def list_curated_environment_images(self) -> str:
        platforms = self.codebuild_backend.list_curated_environment_images()
        return json.dumps({"platforms": platforms})

    # ---- Sandbox operations ----

    def start_sandbox(self) -> str:
        project_name = self._get_param("projectName")
        sandbox = self.codebuild_backend.start_sandbox(project_name)
        return json.dumps({"sandbox": sandbox})

    def stop_sandbox(self) -> str:
        sandbox_id = self._get_param("id")
        if not sandbox_id:
            raise InvalidInputException("Sandbox ID is required")
        sandbox = self.codebuild_backend.stop_sandbox(sandbox_id)
        return json.dumps({"sandbox": sandbox})

    def batch_get_sandboxes(self) -> str:
        ids = self._get_param("ids")
        if not ids:
            raise InvalidInputException("Sandbox IDs are required")
        found, not_found = self.codebuild_backend.batch_get_sandboxes(ids)
        return json.dumps({"sandboxes": found, "sandboxesNotFound": not_found})

    def list_sandboxes(self) -> str:
        ids = self.codebuild_backend.list_sandboxes()
        return json.dumps({"ids": ids})

    def list_sandboxes_for_project(self) -> str:
        project_name = self._get_param("projectName")
        if not project_name:
            raise InvalidInputException("Project name is required")
        ids = self.codebuild_backend.list_sandboxes_for_project(project_name)
        return json.dumps({"ids": ids})

    def start_sandbox_connection(self) -> str:
        sandbox_id = self._get_param("sandboxId")
        if not sandbox_id:
            raise InvalidInputException("Sandbox ID is required")
        ssm_session = self.codebuild_backend.start_sandbox_connection(sandbox_id)
        return json.dumps({"ssmSession": ssm_session})

    # ---- Command execution operations ----

    def start_command_execution(self) -> str:
        sandbox_id = self._get_param("sandboxId")
        command = self._get_param("command")
        if not sandbox_id:
            raise InvalidInputException("Sandbox ID is required")
        if not command:
            raise InvalidInputException("Command is required")
        execution = self.codebuild_backend.start_command_execution(
            sandbox_id, command, self._get_param("type")
        )
        return json.dumps({"commandExecution": execution})

    def list_command_executions_for_sandbox(self) -> str:
        sandbox_id = self._get_param("sandboxId")
        if not sandbox_id:
            raise InvalidInputException("Sandbox ID is required")
        executions = self.codebuild_backend.list_command_executions_for_sandbox(
            sandbox_id
        )
        return json.dumps({"commandExecutions": executions})

    def batch_get_command_executions(self) -> str:
        sandbox_id = self._get_param("sandboxId")
        command_execution_ids = self._get_param("commandExecutionIds")
        if not sandbox_id:
            raise InvalidInputException("Sandbox ID is required")
        if not command_execution_ids:
            raise InvalidInputException("Command execution IDs are required")
        found, not_found = self.codebuild_backend.batch_get_command_executions(
            sandbox_id, command_execution_ids
        )
        return json.dumps({
            "commandExecutions": found,
            "commandExecutionsNotFound": not_found,
        })
