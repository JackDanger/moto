import json
import uuid
from typing import Any

from moto.codepipeline.exceptions import (
    ActionNotFoundException,
    ActionTypeNotFoundException,
    ConflictException,
    InvalidNonceException,
    InvalidStructureException,
    InvalidTagsException,
    JobNotFoundException,
    PipelineExecutionNotFoundException,
    PipelineNotFoundException,
    ResourceNotFoundException,
    StageNotFoundException,
    StageNotRetryableException,
    TooManyTagsException,
    ValidationException,
    WebhookNotFoundException,
)
from moto.core.base_backend import BackendDict, BaseBackend
from moto.core.common_models import BaseModel
from moto.core.utils import iso_8601_datetime_with_milliseconds, utcnow
from moto.iam.exceptions import NotFoundException as IAMNotFoundException
from moto.iam.models import IAMBackend, iam_backends
from moto.utilities.utils import get_partition


class CodePipeline(BaseModel):
    def __init__(self, account_id: str, region: str, pipeline: dict[str, Any]):
        # the version number for a new pipeline is always 1
        pipeline["version"] = 1

        self.pipeline = self.add_default_values(pipeline)
        self.tags: dict[str, str] = {}

        self._arn = f"arn:{get_partition(region)}:codepipeline:{region}:{account_id}:{pipeline['name']}"
        self._created = utcnow()
        self._updated = utcnow()

        # Stage transition states: stage_name -> enabled (True/False)
        self.stage_transitions: dict[str, bool] = {}
        for stage in pipeline.get("stages", []):
            self.stage_transitions[stage["name"]] = True

    @property
    def metadata(self) -> dict[str, str]:
        return {
            "pipelineArn": self._arn,
            "created": iso_8601_datetime_with_milliseconds(self._created),
            "updated": iso_8601_datetime_with_milliseconds(self._updated),
        }

    def add_default_values(self, pipeline: dict[str, Any]) -> dict[str, Any]:
        for stage in pipeline["stages"]:
            for action in stage["actions"]:
                if "runOrder" not in action:
                    action["runOrder"] = 1
                if "configuration" not in action:
                    action["configuration"] = {}
                if "outputArtifacts" not in action:
                    action["outputArtifacts"] = []
                if "inputArtifacts" not in action:
                    action["inputArtifacts"] = []

        return pipeline

    def validate_tags(self, tags: list[dict[str, str]]) -> None:
        for tag in tags:
            if tag["key"].startswith("aws:"):
                raise InvalidTagsException(
                    "Not allowed to modify system tags. "
                    "System tags start with 'aws:'. "
                    "msg=[Caller is an end user and not allowed to mutate system tags]"
                )

        if (len(self.tags) + len(tags)) > 50:
            raise TooManyTagsException(self._arn)


class PipelineExecution(BaseModel):
    def __init__(
        self,
        pipeline_name: str,
        pipeline_version: int,
        pipeline_execution_id: str,
        trigger: dict[str, Any] | None = None,
        source_revisions: list[dict[str, Any]] | None = None,
    ):
        self.pipeline_name = pipeline_name
        self.pipeline_version = pipeline_version
        self.pipeline_execution_id = pipeline_execution_id
        self.status = "InProgress"
        self.status_summary: str | None = None
        self.trigger = trigger or {"triggerType": "StartPipelineExecution", "triggerDetail": ""}
        self.source_revisions = source_revisions or []
        self.last_update_time = utcnow()
        self.start_time = utcnow()
        # action_execution_id -> ActionExecution
        self.action_executions: list[dict[str, Any]] = []

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {
            "pipelineExecutionId": self.pipeline_execution_id,
            "pipelineName": self.pipeline_name,
            "pipelineVersion": self.pipeline_version,
            "status": self.status,
            "artifactRevisions": self.source_revisions,
        }
        if self.status_summary:
            result["statusSummary"] = self.status_summary
        if self.trigger:
            result["trigger"] = self.trigger
        return result

    def to_summary(self) -> dict[str, Any]:
        result: dict[str, Any] = {
            "pipelineExecutionId": self.pipeline_execution_id,
            "status": self.status,
            "startTime": iso_8601_datetime_with_milliseconds(self.start_time),
            "lastUpdateTime": iso_8601_datetime_with_milliseconds(self.last_update_time),
            "sourceRevisions": self.source_revisions,
            "trigger": self.trigger,
        }
        if self.status_summary:
            result["statusSummary"] = self.status_summary
        return result


class CustomActionType(BaseModel):
    def __init__(
        self,
        category: str,
        provider: str,
        version: str,
        settings: dict[str, Any] | None = None,
        configuration_properties: list[dict[str, Any]] | None = None,
        input_artifact_details: dict[str, Any] | None = None,
        output_artifact_details: dict[str, Any] | None = None,
        tags: list[dict[str, str]] | None = None,
    ):
        self.category = category
        self.provider = provider
        self.version = version
        self.description: str = ""
        self.settings = settings or {}
        self.configuration_properties = configuration_properties or []
        self.input_artifact_details = input_artifact_details or {
            "minimumCount": 0,
            "maximumCount": 5,
        }
        self.output_artifact_details = output_artifact_details or {
            "minimumCount": 0,
            "maximumCount": 5,
        }
        self.tags = tags or []

    @property
    def key(self) -> str:
        return f"{self.category}:{self.provider}:{self.version}"

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {
            "id": {
                "category": self.category,
                "owner": "Custom",
                "provider": self.provider,
                "version": self.version,
            },
            "settings": self.settings,
            "inputArtifactDetails": self.input_artifact_details,
            "outputArtifactDetails": self.output_artifact_details,
        }
        if self.configuration_properties:
            result["actionConfigurationProperties"] = self.configuration_properties
        return result


class Webhook(BaseModel):
    def __init__(
        self,
        account_id: str,
        region: str,
        name: str,
        target_pipeline: str,
        target_action: str,
        filters: list[dict[str, Any]],
        authentication: str,
        authentication_configuration: dict[str, Any],
        tags: list[dict[str, str]] | None = None,
    ):
        self.name = name
        self.target_pipeline = target_pipeline
        self.target_action = target_action
        self.filters = filters
        self.authentication = authentication
        self.authentication_configuration = authentication_configuration
        self.tags = {tag["key"]: tag["value"] for tag in (tags or [])}
        self.arn = f"arn:{get_partition(region)}:codepipeline:{region}:{account_id}:webhook:{name}"
        self.url = f"https://webhooks.{region}.codepipeline.amazonaws.com/{name}"
        self.last_triggered = None
        self.registered_with_third_party = False

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {
            "definition": {
                "name": self.name,
                "targetPipeline": self.target_pipeline,
                "targetAction": self.target_action,
                "filters": self.filters,
                "authentication": self.authentication,
                "authenticationConfiguration": self.authentication_configuration,
            },
            "url": self.url,
            "arn": self.arn,
        }
        if self.last_triggered:
            result["lastTriggered"] = iso_8601_datetime_with_milliseconds(self.last_triggered)
        if self.tags:
            result["tags"] = [{"key": k, "value": v} for k, v in self.tags.items()]
        return result


class Job(BaseModel):
    def __init__(
        self,
        job_id: str,
        pipeline_name: str,
        stage_name: str,
        action_name: str,
        action_configuration: dict[str, Any] | None = None,
    ):
        self.id = job_id
        self.pipeline_name = pipeline_name
        self.stage_name = stage_name
        self.action_name = action_name
        self.nonce = str(uuid.uuid4())
        self.status = "Created"
        self.account_id: str | None = None
        self.action_configuration = action_configuration or {}
        self.action_type_id: dict[str, Any] = {}
        self.input_artifacts: list[dict[str, Any]] = []
        self.output_artifacts: list[dict[str, Any]] = []

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "nonce": self.nonce,
            "accountId": self.account_id,
            "data": {
                "actionTypeId": self.action_type_id,
                "actionConfiguration": {"configuration": self.action_configuration},
                "pipelineContext": {
                    "pipelineName": self.pipeline_name,
                    "stage": {"name": self.stage_name},
                    "action": {"name": self.action_name},
                },
                "inputArtifacts": self.input_artifacts,
                "outputArtifacts": self.output_artifacts,
            },
        }


class CodePipelineBackend(BaseBackend):
    def __init__(self, region_name: str, account_id: str):
        super().__init__(region_name, account_id)
        self.pipelines: dict[str, CodePipeline] = {}
        # pipeline_name -> list of PipelineExecution
        self.pipeline_executions: dict[str, list[PipelineExecution]] = {}
        # key -> CustomActionType
        self.custom_action_types: dict[str, CustomActionType] = {}
        # name -> Webhook
        self.webhooks: dict[str, Webhook] = {}
        # job_id -> Job
        self.jobs: dict[str, Job] = {}
        # job_id -> Job (third-party)
        self.third_party_jobs: dict[str, Job] = {}

    @staticmethod
    def default_vpc_endpoint_service(
        service_region: str, zones: list[str]
    ) -> list[dict[str, str]]:
        """Default VPC endpoint service."""
        return BaseBackend.default_vpc_endpoint_service_factory(
            service_region, zones, "codepipeline", policy_supported=False
        )

    @property
    def iam_backend(self) -> IAMBackend:
        return iam_backends[self.account_id][self.partition]

    def _get_pipeline_or_raise(self, name: str) -> CodePipeline:
        pipeline = self.pipelines.get(name)
        if not pipeline:
            raise PipelineNotFoundException(
                f"Account '{self.account_id}' does not have a pipeline with name '{name}'"
            )
        return pipeline

    def create_pipeline(
        self, pipeline: dict[str, Any], tags: list[dict[str, str]]
    ) -> tuple[dict[str, Any], list[dict[str, str]]]:
        name = pipeline["name"]
        if name in self.pipelines:
            raise InvalidStructureException(
                f"A pipeline with the name '{name}' already exists in account '{self.account_id}'"
            )

        try:
            role = self.iam_backend.get_role_by_arn(pipeline["roleArn"])
            trust_policy_statements = json.loads(role.assume_role_policy_document)[
                "Statement"
            ]
            trusted_service_principals = [
                i["Principal"]["Service"] for i in trust_policy_statements
            ]
            if "codepipeline.amazonaws.com" not in trusted_service_principals:
                raise IAMNotFoundException("")
        except IAMNotFoundException:
            raise InvalidStructureException(
                f"CodePipeline is not authorized to perform AssumeRole on role {pipeline['roleArn']}"
            )

        if len(pipeline["stages"]) < 2:
            raise InvalidStructureException(
                "Pipeline has only 1 stage(s). There should be a minimum of 2 stages in a pipeline"
            )

        self.pipelines[pipeline["name"]] = CodePipeline(
            self.account_id, self.region_name, pipeline
        )

        if tags is not None:
            self.pipelines[pipeline["name"]].validate_tags(tags)

            new_tags = {tag["key"]: tag["value"] for tag in tags}
            self.pipelines[pipeline["name"]].tags.update(new_tags)
        else:
            tags = []

        return pipeline, sorted(tags, key=lambda i: i["key"])

    def get_pipeline(self, name: str) -> tuple[dict[str, Any], dict[str, str]]:
        codepipeline = self._get_pipeline_or_raise(name)
        return codepipeline.pipeline, codepipeline.metadata

    def update_pipeline(self, pipeline: dict[str, Any]) -> dict[str, Any]:
        codepipeline = self.pipelines.get(pipeline["name"])

        if not codepipeline:
            raise ResourceNotFoundException(
                f"The account with id '{self.account_id}' does not include a pipeline with the name '{pipeline['name']}'"
            )

        # version number is auto incremented
        pipeline["version"] = codepipeline.pipeline["version"] + 1
        codepipeline._updated = utcnow()
        codepipeline.pipeline = codepipeline.add_default_values(pipeline)

        # Update stage transitions for new stages
        for stage in pipeline.get("stages", []):
            if stage["name"] not in codepipeline.stage_transitions:
                codepipeline.stage_transitions[stage["name"]] = True

        return codepipeline.pipeline

    def list_pipelines(self) -> list[dict[str, str]]:
        pipelines = []

        for name, codepipeline in self.pipelines.items():
            pipelines.append(
                {
                    "name": name,
                    "version": codepipeline.pipeline["version"],
                    "created": codepipeline.metadata["created"],
                    "updated": codepipeline.metadata["updated"],
                }
            )

        return sorted(pipelines, key=lambda i: i["name"])

    def delete_pipeline(self, name: str) -> None:
        self.pipelines.pop(name, None)
        self.pipeline_executions.pop(name, None)

    def list_tags_for_resource(self, arn: str) -> list[dict[str, str]]:
        name = arn.split(":")[-1]
        pipeline = self.pipelines.get(name)

        if not pipeline:
            raise ResourceNotFoundException(
                f"The account with id '{self.account_id}' does not include a pipeline with the name '{name}'"
            )

        tags = [{"key": key, "value": value} for key, value in pipeline.tags.items()]

        return sorted(tags, key=lambda i: i["key"])

    def tag_resource(self, arn: str, tags: list[dict[str, str]]) -> None:
        name = arn.split(":")[-1]
        pipeline = self.pipelines.get(name)

        if not pipeline:
            raise ResourceNotFoundException(
                f"The account with id '{self.account_id}' does not include a pipeline with the name '{name}'"
            )

        pipeline.validate_tags(tags)

        for tag in tags:
            pipeline.tags.update({tag["key"]: tag["value"]})

    def untag_resource(self, arn: str, tag_keys: list[str]) -> None:
        name = arn.split(":")[-1]
        pipeline = self.pipelines.get(name)

        if not pipeline:
            raise ResourceNotFoundException(
                f"The account with id '{self.account_id}' does not include a pipeline with the name '{name}'"
            )

        for key in tag_keys:
            pipeline.tags.pop(key, None)

    # --- Pipeline Execution operations ---

    def start_pipeline_execution(
        self,
        name: str,
        source_revisions: list[dict[str, Any]] | None = None,
        variables: list[dict[str, Any]] | None = None,
    ) -> str:
        codepipeline = self._get_pipeline_or_raise(name)
        execution_id = str(uuid.uuid4())

        execution = PipelineExecution(
            pipeline_name=name,
            pipeline_version=codepipeline.pipeline["version"],
            pipeline_execution_id=execution_id,
            source_revisions=source_revisions,
        )

        if name not in self.pipeline_executions:
            self.pipeline_executions[name] = []
        self.pipeline_executions[name].insert(0, execution)

        return execution_id

    def stop_pipeline_execution(
        self,
        pipeline_name: str,
        pipeline_execution_id: str,
        abandon: bool = False,
        reason: str | None = None,
    ) -> str:
        self._get_pipeline_or_raise(pipeline_name)

        executions = self.pipeline_executions.get(pipeline_name, [])
        execution = None
        for ex in executions:
            if ex.pipeline_execution_id == pipeline_execution_id:
                execution = ex
                break

        if not execution:
            raise PipelineExecutionNotFoundException(
                f"Pipeline execution with ID '{pipeline_execution_id}' does not exist for pipeline '{pipeline_name}'"
            )

        if execution.status not in ("InProgress",):
            raise ConflictException(
                f"Pipeline execution '{pipeline_execution_id}' is not in a state that can be stopped"
            )

        if abandon:
            execution.status = "Abandoned"
        else:
            execution.status = "Stopping"

        if reason:
            execution.status_summary = reason
        execution.last_update_time = utcnow()

        return pipeline_execution_id

    def get_pipeline_execution(
        self, pipeline_name: str, pipeline_execution_id: str
    ) -> dict[str, Any]:
        self._get_pipeline_or_raise(pipeline_name)

        executions = self.pipeline_executions.get(pipeline_name, [])
        for execution in executions:
            if execution.pipeline_execution_id == pipeline_execution_id:
                return execution.to_dict()

        raise PipelineExecutionNotFoundException(
            f"Pipeline execution with ID '{pipeline_execution_id}' does not exist for pipeline '{pipeline_name}'"
        )

    def list_pipeline_executions(
        self, pipeline_name: str, max_results: int | None = None, next_token: str | None = None
    ) -> tuple[list[dict[str, Any]], str | None]:
        self._get_pipeline_or_raise(pipeline_name)

        executions = self.pipeline_executions.get(pipeline_name, [])

        start = 0
        if next_token:
            start = int(next_token)

        if max_results is None:
            max_results = 100

        end = start + max_results
        page = executions[start:end]

        token = None
        if end < len(executions):
            token = str(end)

        return [ex.to_summary() for ex in page], token

    def get_pipeline_state(self, name: str) -> dict[str, Any]:
        codepipeline = self._get_pipeline_or_raise(name)

        stage_states = []
        for stage in codepipeline.pipeline.get("stages", []):
            stage_name = stage["name"]
            transition_enabled = codepipeline.stage_transitions.get(stage_name, True)

            action_states = []
            for action in stage.get("actions", []):
                action_state: dict[str, Any] = {
                    "actionName": action["name"],
                }
                action_states.append(action_state)

            stage_state: dict[str, Any] = {
                "stageName": stage_name,
                "actionStates": action_states,
                "inboundTransitionState": {
                    "enabled": transition_enabled,
                },
            }

            # Add latest execution info if available
            executions = self.pipeline_executions.get(name, [])
            if executions:
                latest = executions[0]
                stage_state["latestExecution"] = {
                    "pipelineExecutionId": latest.pipeline_execution_id,
                    "status": latest.status,
                }

            stage_states.append(stage_state)

        result: dict[str, Any] = {
            "pipelineName": name,
            "pipelineVersion": codepipeline.pipeline["version"],
            "stageStates": stage_states,
            "created": iso_8601_datetime_with_milliseconds(codepipeline._created),
            "updated": iso_8601_datetime_with_milliseconds(codepipeline._updated),
        }

        return result

    def retry_stage_execution(
        self,
        pipeline_name: str,
        stage_name: str,
        pipeline_execution_id: str,
        retry_mode: str,
    ) -> str:
        codepipeline = self._get_pipeline_or_raise(pipeline_name)

        # Validate stage exists
        stage_names = [s["name"] for s in codepipeline.pipeline.get("stages", [])]
        if stage_name not in stage_names:
            raise StageNotFoundException(
                f"Stage '{stage_name}' does not exist in pipeline '{pipeline_name}'"
            )

        # Find the execution
        executions = self.pipeline_executions.get(pipeline_name, [])
        execution = None
        for ex in executions:
            if ex.pipeline_execution_id == pipeline_execution_id:
                execution = ex
                break

        if not execution:
            raise PipelineExecutionNotFoundException(
                f"Pipeline execution with ID '{pipeline_execution_id}' does not exist"
            )

        if execution.status not in ("Failed", "Stopped"):
            raise StageNotRetryableException(
                f"Stage '{stage_name}' in pipeline execution '{pipeline_execution_id}' is not retryable"
            )

        execution.status = "InProgress"
        execution.last_update_time = utcnow()

        return pipeline_execution_id

    def rollback_stage(
        self, pipeline_name: str, stage_name: str, target_pipeline_execution_id: str
    ) -> str:
        codepipeline = self._get_pipeline_or_raise(pipeline_name)

        stage_names = [s["name"] for s in codepipeline.pipeline.get("stages", [])]
        if stage_name not in stage_names:
            raise StageNotFoundException(
                f"Stage '{stage_name}' does not exist in pipeline '{pipeline_name}'"
            )

        new_execution_id = str(uuid.uuid4())

        execution = PipelineExecution(
            pipeline_name=pipeline_name,
            pipeline_version=codepipeline.pipeline["version"],
            pipeline_execution_id=new_execution_id,
            trigger={"triggerType": "RollbackStage", "triggerDetail": stage_name},
        )

        if pipeline_name not in self.pipeline_executions:
            self.pipeline_executions[pipeline_name] = []
        self.pipeline_executions[pipeline_name].insert(0, execution)

        return new_execution_id

    # --- Stage Transition operations ---

    def disable_stage_transition(
        self,
        pipeline_name: str,
        stage_name: str,
        transition_type: str,
        reason: str,
    ) -> None:
        codepipeline = self._get_pipeline_or_raise(pipeline_name)

        stage_names = [s["name"] for s in codepipeline.pipeline.get("stages", [])]
        if stage_name not in stage_names:
            raise StageNotFoundException(
                f"Stage '{stage_name}' does not exist in pipeline '{pipeline_name}'"
            )

        codepipeline.stage_transitions[stage_name] = False

    def enable_stage_transition(
        self,
        pipeline_name: str,
        stage_name: str,
        transition_type: str,
    ) -> None:
        codepipeline = self._get_pipeline_or_raise(pipeline_name)

        stage_names = [s["name"] for s in codepipeline.pipeline.get("stages", [])]
        if stage_name not in stage_names:
            raise StageNotFoundException(
                f"Stage '{stage_name}' does not exist in pipeline '{pipeline_name}'"
            )

        codepipeline.stage_transitions[stage_name] = True

    def override_stage_condition(
        self,
        pipeline_name: str,
        stage_name: str,
        pipeline_execution_id: str,
        condition_type: str,
    ) -> None:
        codepipeline = self._get_pipeline_or_raise(pipeline_name)

        stage_names = [s["name"] for s in codepipeline.pipeline.get("stages", [])]
        if stage_name not in stage_names:
            raise StageNotFoundException(
                f"Stage '{stage_name}' does not exist in pipeline '{pipeline_name}'"
            )
        # In a real implementation this would modify the condition evaluation,
        # but for emulation we just validate and return success.

    # --- Custom Action Type operations ---

    def create_custom_action_type(
        self,
        category: str,
        provider: str,
        version: str,
        settings: dict[str, Any] | None = None,
        configuration_properties: list[dict[str, Any]] | None = None,
        input_artifact_details: dict[str, Any] | None = None,
        output_artifact_details: dict[str, Any] | None = None,
        tags: list[dict[str, str]] | None = None,
    ) -> dict[str, Any]:
        action_type = CustomActionType(
            category=category,
            provider=provider,
            version=version,
            settings=settings,
            configuration_properties=configuration_properties,
            input_artifact_details=input_artifact_details,
            output_artifact_details=output_artifact_details,
            tags=tags,
        )

        self.custom_action_types[action_type.key] = action_type
        return action_type.to_dict()

    def delete_custom_action_type(
        self, category: str, provider: str, version: str
    ) -> None:
        key = f"{category}:{provider}:{version}"
        if key not in self.custom_action_types:
            raise ActionTypeNotFoundException(
                f"No action type found for: category '{category}', owner 'Custom', provider '{provider}', version '{version}'"
            )
        del self.custom_action_types[key]

    def list_action_types(
        self, action_owner_filter: str | None = None
    ) -> list[dict[str, Any]]:
        result = []

        # Built-in AWS action types
        builtin_types = [
            {
                "id": {"category": "Source", "owner": "AWS", "provider": "S3", "version": "1"},
                "inputArtifactDetails": {"minimumCount": 0, "maximumCount": 0},
                "outputArtifactDetails": {"minimumCount": 1, "maximumCount": 1},
            },
            {
                "id": {"category": "Source", "owner": "AWS", "provider": "CodeCommit", "version": "1"},
                "inputArtifactDetails": {"minimumCount": 0, "maximumCount": 0},
                "outputArtifactDetails": {"minimumCount": 1, "maximumCount": 1},
            },
            {
                "id": {"category": "Source", "owner": "AWS", "provider": "CodeStarSourceConnection", "version": "1"},
                "inputArtifactDetails": {"minimumCount": 0, "maximumCount": 0},
                "outputArtifactDetails": {"minimumCount": 1, "maximumCount": 1},
            },
            {
                "id": {"category": "Source", "owner": "AWS", "provider": "ECR", "version": "1"},
                "inputArtifactDetails": {"minimumCount": 0, "maximumCount": 0},
                "outputArtifactDetails": {"minimumCount": 1, "maximumCount": 1},
            },
            {
                "id": {"category": "Build", "owner": "AWS", "provider": "CodeBuild", "version": "1"},
                "inputArtifactDetails": {"minimumCount": 1, "maximumCount": 5},
                "outputArtifactDetails": {"minimumCount": 0, "maximumCount": 5},
            },
            {
                "id": {"category": "Deploy", "owner": "AWS", "provider": "S3", "version": "1"},
                "inputArtifactDetails": {"minimumCount": 1, "maximumCount": 1},
                "outputArtifactDetails": {"minimumCount": 0, "maximumCount": 0},
            },
            {
                "id": {"category": "Deploy", "owner": "AWS", "provider": "CloudFormation", "version": "1"},
                "inputArtifactDetails": {"minimumCount": 0, "maximumCount": 10},
                "outputArtifactDetails": {"minimumCount": 0, "maximumCount": 1},
            },
            {
                "id": {"category": "Deploy", "owner": "AWS", "provider": "CodeDeploy", "version": "1"},
                "inputArtifactDetails": {"minimumCount": 1, "maximumCount": 1},
                "outputArtifactDetails": {"minimumCount": 0, "maximumCount": 0},
            },
            {
                "id": {"category": "Deploy", "owner": "AWS", "provider": "ECS", "version": "1"},
                "inputArtifactDetails": {"minimumCount": 1, "maximumCount": 5},
                "outputArtifactDetails": {"minimumCount": 0, "maximumCount": 0},
            },
            {
                "id": {"category": "Invoke", "owner": "AWS", "provider": "Lambda", "version": "1"},
                "inputArtifactDetails": {"minimumCount": 0, "maximumCount": 5},
                "outputArtifactDetails": {"minimumCount": 0, "maximumCount": 5},
            },
            {
                "id": {"category": "Approval", "owner": "AWS", "provider": "Manual", "version": "1"},
                "inputArtifactDetails": {"minimumCount": 0, "maximumCount": 0},
                "outputArtifactDetails": {"minimumCount": 0, "maximumCount": 0},
            },
            {
                "id": {"category": "Test", "owner": "AWS", "provider": "CodeBuild", "version": "1"},
                "inputArtifactDetails": {"minimumCount": 1, "maximumCount": 5},
                "outputArtifactDetails": {"minimumCount": 0, "maximumCount": 5},
            },
        ]

        if action_owner_filter is None or action_owner_filter == "AWS":
            result.extend(builtin_types)

        # Third-party types
        third_party_types = [
            {
                "id": {"category": "Source", "owner": "ThirdParty", "provider": "GitHub", "version": "1"},
                "inputArtifactDetails": {"minimumCount": 0, "maximumCount": 0},
                "outputArtifactDetails": {"minimumCount": 1, "maximumCount": 1},
            },
        ]

        if action_owner_filter is None or action_owner_filter == "ThirdParty":
            result.extend(third_party_types)

        # Custom action types
        if action_owner_filter is None or action_owner_filter == "Custom":
            for action_type in self.custom_action_types.values():
                result.append(action_type.to_dict())

        return result

    def get_action_type(
        self, category: str, owner: str, provider: str, version: str
    ) -> dict[str, Any]:
        if owner == "Custom":
            key = f"{category}:{provider}:{version}"
            action_type = self.custom_action_types.get(key)
            if not action_type:
                raise ActionTypeNotFoundException(
                    f"No action type found for: category '{category}', owner '{owner}', provider '{provider}', version '{version}'"
                )
            return action_type.to_dict()

        # For built-in types, return a basic representation
        return {
            "id": {
                "category": category,
                "owner": owner,
                "provider": provider,
                "version": version,
            },
            "inputArtifactDetails": {"minimumCount": 0, "maximumCount": 5},
            "outputArtifactDetails": {"minimumCount": 0, "maximumCount": 5},
        }

    # --- Webhook operations ---

    def put_webhook(
        self,
        webhook: dict[str, Any],
        tags: list[dict[str, str]] | None = None,
    ) -> dict[str, Any]:
        name = webhook["name"]
        target_pipeline = webhook["targetPipeline"]

        # Validate pipeline exists
        self._get_pipeline_or_raise(target_pipeline)

        wh = Webhook(
            account_id=self.account_id,
            region=self.region_name,
            name=name,
            target_pipeline=target_pipeline,
            target_action=webhook["targetAction"],
            filters=webhook.get("filters", []),
            authentication=webhook["authentication"],
            authentication_configuration=webhook.get("authenticationConfiguration", {}),
            tags=tags,
        )

        self.webhooks[name] = wh
        return wh.to_dict()

    def delete_webhook(self, name: str) -> None:
        if name not in self.webhooks:
            raise WebhookNotFoundException(
                f"Webhook with name '{name}' does not exist"
            )
        del self.webhooks[name]

    def list_webhooks(self) -> list[dict[str, Any]]:
        return [wh.to_dict() for wh in self.webhooks.values()]

    def register_webhook_with_third_party(self, webhook_name: str) -> None:
        wh = self.webhooks.get(webhook_name)
        if not wh:
            raise WebhookNotFoundException(
                f"Webhook with name '{webhook_name}' does not exist"
            )
        wh.registered_with_third_party = True

    def deregister_webhook_with_third_party(self, webhook_name: str) -> None:
        wh = self.webhooks.get(webhook_name)
        if not wh:
            raise WebhookNotFoundException(
                f"Webhook with name '{webhook_name}' does not exist"
            )
        wh.registered_with_third_party = False

    # --- Job operations ---

    def poll_for_jobs(
        self,
        action_type_id: dict[str, Any],
        max_batch_size: int | None = None,
        query_param: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        if max_batch_size is None:
            max_batch_size = 1

        matching_jobs = []
        for job in self.jobs.values():
            if job.status == "Created":
                matching_jobs.append(job.to_dict())
                if len(matching_jobs) >= max_batch_size:
                    break

        return matching_jobs

    def poll_for_third_party_jobs(
        self,
        action_type_id: dict[str, Any],
        max_batch_size: int | None = None,
    ) -> list[dict[str, Any]]:
        if max_batch_size is None:
            max_batch_size = 1

        matching_jobs = []
        for job in self.third_party_jobs.values():
            if job.status == "Created":
                matching_jobs.append({"clientId": self.account_id, "jobId": job.id})
                if len(matching_jobs) >= max_batch_size:
                    break

        return matching_jobs

    def acknowledge_job(self, job_id: str, nonce: str) -> str:
        job = self.jobs.get(job_id)
        if not job:
            raise JobNotFoundException(f"Job with id '{job_id}' not found")

        if job.nonce != nonce:
            raise InvalidNonceException(f"Nonce mismatch for job '{job_id}'")

        job.status = "InProgress"
        return "InProgress"

    def acknowledge_third_party_job(
        self, job_id: str, nonce: str, client_token: str
    ) -> str:
        job = self.third_party_jobs.get(job_id)
        if not job:
            raise JobNotFoundException(f"Job with id '{job_id}' not found")

        if job.nonce != nonce:
            raise InvalidNonceException(f"Nonce mismatch for job '{job_id}'")

        job.status = "InProgress"
        return "InProgress"

    def put_job_success_result(
        self,
        job_id: str,
        current_revision: dict[str, Any] | None = None,
        continuation_token: str | None = None,
        execution_details: dict[str, Any] | None = None,
        output_variables: dict[str, str] | None = None,
    ) -> None:
        job = self.jobs.get(job_id)
        if not job:
            raise JobNotFoundException(f"Job with id '{job_id}' not found")

        job.status = "Succeeded"

    def put_job_failure_result(
        self,
        job_id: str,
        failure_details: dict[str, Any],
    ) -> None:
        job = self.jobs.get(job_id)
        if not job:
            raise JobNotFoundException(f"Job with id '{job_id}' not found")

        job.status = "Failed"

    def put_third_party_job_success_result(
        self,
        job_id: str,
        client_token: str,
        current_revision: dict[str, Any] | None = None,
        continuation_token: str | None = None,
        execution_details: dict[str, Any] | None = None,
    ) -> None:
        job = self.third_party_jobs.get(job_id)
        if not job:
            raise JobNotFoundException(f"Job with id '{job_id}' not found")

        job.status = "Succeeded"

    def put_third_party_job_failure_result(
        self,
        job_id: str,
        client_token: str,
        failure_details: dict[str, Any],
    ) -> None:
        job = self.third_party_jobs.get(job_id)
        if not job:
            raise JobNotFoundException(f"Job with id '{job_id}' not found")

        job.status = "Failed"

    def get_job_details(self, job_id: str) -> dict[str, Any]:
        job = self.jobs.get(job_id)
        if not job:
            raise JobNotFoundException(f"Job with id '{job_id}' not found")

        return job.to_dict()

    def get_third_party_job_details(
        self, job_id: str, client_token: str
    ) -> dict[str, Any]:
        job = self.third_party_jobs.get(job_id)
        if not job:
            raise JobNotFoundException(f"Job with id '{job_id}' not found")

        return job.to_dict()

    # --- Approval operations ---

    def put_approval_result(
        self,
        pipeline_name: str,
        stage_name: str,
        action_name: str,
        result: dict[str, Any],
        token: str,
    ) -> str:
        self._get_pipeline_or_raise(pipeline_name)

        approved_at = utcnow()
        return iso_8601_datetime_with_milliseconds(approved_at)

    # --- Action Execution operations ---

    def list_action_executions(
        self,
        pipeline_name: str,
        filter_param: dict[str, Any] | None = None,
        max_results: int | None = None,
        next_token: str | None = None,
    ) -> tuple[list[dict[str, Any]], str | None]:
        self._get_pipeline_or_raise(pipeline_name)

        executions = self.pipeline_executions.get(pipeline_name, [])
        action_execution_details: list[dict[str, Any]] = []

        for execution in executions:
            if filter_param and filter_param.get("pipelineExecutionId"):
                if execution.pipeline_execution_id != filter_param["pipelineExecutionId"]:
                    continue

            # Generate action execution details from the pipeline stages
            codepipeline = self.pipelines.get(pipeline_name)
            if codepipeline:
                for stage in codepipeline.pipeline.get("stages", []):
                    for action in stage.get("actions", []):
                        detail: dict[str, Any] = {
                            "pipelineExecutionId": execution.pipeline_execution_id,
                            "actionExecutionId": str(uuid.uuid4()),
                            "pipelineVersion": execution.pipeline_version,
                            "stageName": stage["name"],
                            "actionName": action["name"],
                            "startTime": iso_8601_datetime_with_milliseconds(
                                execution.start_time
                            ),
                            "status": execution.status,
                            "input": {
                                "actionTypeId": action.get("actionTypeId", {}),
                                "configuration": action.get("configuration", {}),
                                "region": self.region_name,
                                "inputArtifacts": action.get("inputArtifacts", []),
                            },
                            "output": {
                                "outputArtifacts": action.get("outputArtifacts", []),
                                "outputVariables": {},
                            },
                        }
                        action_execution_details.append(detail)

        start = 0
        if next_token:
            start = int(next_token)
        if max_results is None:
            max_results = 100
        end = start + max_results
        page = action_execution_details[start:end]

        token = None
        if end < len(action_execution_details):
            token = str(end)

        return page, token

    # --- Rule operations ---

    def list_rule_executions(
        self,
        pipeline_name: str,
        filter_param: dict[str, Any] | None = None,
        max_results: int | None = None,
        next_token: str | None = None,
    ) -> tuple[list[dict[str, Any]], str | None]:
        self._get_pipeline_or_raise(pipeline_name)
        # Rules are a newer feature; return empty for now
        return [], None

    def list_rule_types(self) -> list[dict[str, Any]]:
        # Return empty list — rule types are a newer feature
        return []



    # --- Deploy Action Execution Targets ---

    def list_deploy_action_execution_targets(
        self,
        pipeline_name: str | None,
        action_execution_id: str,
        filters: list[dict[str, Any]] | None = None,
        max_results: int | None = None,
        next_token: str | None = None,
    ) -> tuple[list[dict[str, Any]], str | None]:
        # Validate pipeline exists if provided
        if pipeline_name:
            self._get_pipeline_or_raise(pipeline_name)

        # Deploy action execution targets are generated from action executions.
        # For emulation, return an empty list (no real deployments happen).
        return [], None

    # --- Action Revision operations ---

    def put_action_revision(
        self,
        pipeline_name: str,
        stage_name: str,
        action_name: str,
        action_revision: dict[str, Any],
    ) -> tuple[bool, str]:
        codepipeline = self._get_pipeline_or_raise(pipeline_name)

        # Validate stage exists
        stage_names = [s["name"] for s in codepipeline.pipeline.get("stages", [])]
        if stage_name not in stage_names:
            raise StageNotFoundException(
                f"Stage '{stage_name}' does not exist in pipeline '{pipeline_name}'"
            )

        # Validate action exists in the stage
        stage = next(
            s for s in codepipeline.pipeline["stages"] if s["name"] == stage_name
        )
        action_names = [a["name"] for a in stage.get("actions", [])]
        if action_name not in action_names:
            raise ActionNotFoundException(
                f"Action '{action_name}' does not exist in stage '{stage_name}'"
                f" of pipeline '{pipeline_name}'"
            )

        # Start a new pipeline execution triggered by the action revision
        execution_id = str(uuid.uuid4())
        execution = PipelineExecution(
            pipeline_name=pipeline_name,
            pipeline_version=codepipeline.pipeline["version"],
            pipeline_execution_id=execution_id,
            source_revisions=[
                {
                    "actionName": action_name,
                    "revisionId": action_revision.get("revisionId", ""),
                    "revisionSummary": action_revision.get(
                        "revisionChangeId", ""
                    ),
                }
            ],
        )

        if pipeline_name not in self.pipeline_executions:
            self.pipeline_executions[pipeline_name] = []
        self.pipeline_executions[pipeline_name].insert(0, execution)

        return True, execution_id

    # --- Action Type update operations ---

    def update_action_type(self, action_type: dict[str, Any]) -> None:
        action_id = action_type.get("id", {})
        category = action_id.get("category", "")
        owner = action_id.get("owner", "")
        provider = action_id.get("provider", "")
        version = action_id.get("version", "")

        if owner != "Custom":
            raise ValidationException(
                "Only custom action types can be updated"
            )

        key = f"{category}:{provider}:{version}"
        existing = self.custom_action_types.get(key)
        if not existing:
            raise ActionTypeNotFoundException(
                f"No action type found for: category '{category}',"
                f" owner '{owner}', provider '{provider}',"
                f" version '{version}'"
            )

        # Update mutable fields
        if "inputArtifactDetails" in action_type:
            existing.input_artifact_details = action_type[
                "inputArtifactDetails"
            ]
        if "outputArtifactDetails" in action_type:
            existing.output_artifact_details = action_type[
                "outputArtifactDetails"
            ]
        if "description" in action_type:
            existing.description = action_type["description"]

codepipeline_backends = BackendDict(CodePipelineBackend, "codepipeline")
