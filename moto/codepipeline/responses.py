import json

from moto.core.responses import BaseResponse

from .models import CodePipelineBackend, codepipeline_backends


class CodePipelineResponse(BaseResponse):
    def __init__(self) -> None:
        super().__init__(service_name="codepipeline")

    @property
    def codepipeline_backend(self) -> CodePipelineBackend:
        return codepipeline_backends[self.current_account][self.region]

    def create_pipeline(self) -> str:
        pipeline, tags = self.codepipeline_backend.create_pipeline(
            self._get_param("pipeline"), self._get_param("tags")
        )

        return json.dumps({"pipeline": pipeline, "tags": tags})

    def get_pipeline(self) -> str:
        pipeline, metadata = self.codepipeline_backend.get_pipeline(
            self._get_param("name")
        )

        return json.dumps({"pipeline": pipeline, "metadata": metadata})

    def update_pipeline(self) -> str:
        pipeline = self.codepipeline_backend.update_pipeline(
            self._get_param("pipeline")
        )

        return json.dumps({"pipeline": pipeline})

    def list_pipelines(self) -> str:
        pipelines = self.codepipeline_backend.list_pipelines()

        return json.dumps({"pipelines": pipelines})

    def delete_pipeline(self) -> str:
        self.codepipeline_backend.delete_pipeline(self._get_param("name"))

        return ""

    def list_tags_for_resource(self) -> str:
        tags = self.codepipeline_backend.list_tags_for_resource(
            self._get_param("resourceArn")
        )

        return json.dumps({"tags": tags})

    def tag_resource(self) -> str:
        self.codepipeline_backend.tag_resource(
            self._get_param("resourceArn"), self._get_param("tags")
        )

        return ""

    def untag_resource(self) -> str:
        self.codepipeline_backend.untag_resource(
            self._get_param("resourceArn"), self._get_param("tagKeys")
        )

        return ""

    # --- Pipeline Execution operations ---

    def start_pipeline_execution(self) -> str:
        execution_id = self.codepipeline_backend.start_pipeline_execution(
            name=self._get_param("name"),
            source_revisions=self._get_param("sourceRevisions"),
            variables=self._get_param("variables"),
        )

        return json.dumps({"pipelineExecutionId": execution_id})

    def stop_pipeline_execution(self) -> str:
        execution_id = self.codepipeline_backend.stop_pipeline_execution(
            pipeline_name=self._get_param("pipelineName"),
            pipeline_execution_id=self._get_param("pipelineExecutionId"),
            abandon=self._get_param("abandon", False),
            reason=self._get_param("reason"),
        )

        return json.dumps({"pipelineExecutionId": execution_id})

    def get_pipeline_execution(self) -> str:
        execution = self.codepipeline_backend.get_pipeline_execution(
            pipeline_name=self._get_param("pipelineName"),
            pipeline_execution_id=self._get_param("pipelineExecutionId"),
        )

        return json.dumps({"pipelineExecution": execution})

    def list_pipeline_executions(self) -> str:
        summaries, next_token = self.codepipeline_backend.list_pipeline_executions(
            pipeline_name=self._get_param("pipelineName"),
            max_results=self._get_param("maxResults"),
            next_token=self._get_param("nextToken"),
        )

        result: dict = {"pipelineExecutionSummaries": summaries}
        if next_token:
            result["nextToken"] = next_token

        return json.dumps(result)

    def get_pipeline_state(self) -> str:
        state = self.codepipeline_backend.get_pipeline_state(
            name=self._get_param("name"),
        )

        return json.dumps(state)

    def retry_stage_execution(self) -> str:
        execution_id = self.codepipeline_backend.retry_stage_execution(
            pipeline_name=self._get_param("pipelineName"),
            stage_name=self._get_param("stageName"),
            pipeline_execution_id=self._get_param("pipelineExecutionId"),
            retry_mode=self._get_param("retryMode"),
        )

        return json.dumps({"pipelineExecutionId": execution_id})

    def rollback_stage(self) -> str:
        execution_id = self.codepipeline_backend.rollback_stage(
            pipeline_name=self._get_param("pipelineName"),
            stage_name=self._get_param("stageName"),
            target_pipeline_execution_id=self._get_param("targetPipelineExecutionId"),
        )

        return json.dumps({"pipelineExecutionId": execution_id})

    # --- Stage Transition operations ---

    def disable_stage_transition(self) -> str:
        self.codepipeline_backend.disable_stage_transition(
            pipeline_name=self._get_param("pipelineName"),
            stage_name=self._get_param("stageName"),
            transition_type=self._get_param("transitionType"),
            reason=self._get_param("reason"),
        )

        return ""

    def enable_stage_transition(self) -> str:
        self.codepipeline_backend.enable_stage_transition(
            pipeline_name=self._get_param("pipelineName"),
            stage_name=self._get_param("stageName"),
            transition_type=self._get_param("transitionType"),
        )

        return ""

    def override_stage_condition(self) -> str:
        self.codepipeline_backend.override_stage_condition(
            pipeline_name=self._get_param("pipelineName"),
            stage_name=self._get_param("stageName"),
            pipeline_execution_id=self._get_param("pipelineExecutionId"),
            condition_type=self._get_param("conditionType"),
        )

        return ""

    # --- Custom Action Type operations ---

    def create_custom_action_type(self) -> str:
        action_type = self.codepipeline_backend.create_custom_action_type(
            category=self._get_param("category"),
            provider=self._get_param("provider"),
            version=self._get_param("version"),
            settings=self._get_param("settings"),
            configuration_properties=self._get_param("configurationProperties"),
            input_artifact_details=self._get_param("inputArtifactDetails"),
            output_artifact_details=self._get_param("outputArtifactDetails"),
            tags=self._get_param("tags"),
        )

        return json.dumps({"actionType": action_type})

    def delete_custom_action_type(self) -> str:
        self.codepipeline_backend.delete_custom_action_type(
            category=self._get_param("category"),
            provider=self._get_param("provider"),
            version=self._get_param("version"),
        )

        return ""

    def list_action_types(self) -> str:
        action_types = self.codepipeline_backend.list_action_types(
            action_owner_filter=self._get_param("actionOwnerFilter"),
        )

        return json.dumps({"actionTypes": action_types})

    def get_action_type(self) -> str:
        action_type = self.codepipeline_backend.get_action_type(
            category=self._get_param("category"),
            owner=self._get_param("owner"),
            provider=self._get_param("provider"),
            version=self._get_param("version"),
        )

        return json.dumps({"actionType": action_type})

    # --- Webhook operations ---

    def put_webhook(self) -> str:
        webhook = self.codepipeline_backend.put_webhook(
            webhook=self._get_param("webhook"),
            tags=self._get_param("tags"),
        )

        return json.dumps({"webhook": webhook})

    def delete_webhook(self) -> str:
        self.codepipeline_backend.delete_webhook(
            name=self._get_param("name"),
        )

        return ""

    def list_webhooks(self) -> str:
        webhooks = self.codepipeline_backend.list_webhooks()

        return json.dumps({"webhooks": webhooks})

    def register_webhook_with_third_party(self) -> str:
        self.codepipeline_backend.register_webhook_with_third_party(
            webhook_name=self._get_param("webhookName"),
        )

        return ""

    def deregister_webhook_with_third_party(self) -> str:
        self.codepipeline_backend.deregister_webhook_with_third_party(
            webhook_name=self._get_param("webhookName"),
        )

        return ""

    # --- Job operations ---

    def poll_for_jobs(self) -> str:
        jobs = self.codepipeline_backend.poll_for_jobs(
            action_type_id=self._get_param("actionTypeId"),
            max_batch_size=self._get_param("maxBatchSize"),
            query_param=self._get_param("queryParam"),
        )

        return json.dumps({"jobs": jobs})

    def poll_for_third_party_jobs(self) -> str:
        jobs = self.codepipeline_backend.poll_for_third_party_jobs(
            action_type_id=self._get_param("actionTypeId"),
            max_batch_size=self._get_param("maxBatchSize"),
        )

        return json.dumps({"jobs": jobs})

    def acknowledge_job(self) -> str:
        status = self.codepipeline_backend.acknowledge_job(
            job_id=self._get_param("jobId"),
            nonce=self._get_param("nonce"),
        )

        return json.dumps({"status": status})

    def acknowledge_third_party_job(self) -> str:
        status = self.codepipeline_backend.acknowledge_third_party_job(
            job_id=self._get_param("jobId"),
            nonce=self._get_param("nonce"),
            client_token=self._get_param("clientToken"),
        )

        return json.dumps({"status": status})

    def put_job_success_result(self) -> str:
        self.codepipeline_backend.put_job_success_result(
            job_id=self._get_param("jobId"),
            current_revision=self._get_param("currentRevision"),
            continuation_token=self._get_param("continuationToken"),
            execution_details=self._get_param("executionDetails"),
            output_variables=self._get_param("outputVariables"),
        )

        return ""

    def put_job_failure_result(self) -> str:
        self.codepipeline_backend.put_job_failure_result(
            job_id=self._get_param("jobId"),
            failure_details=self._get_param("failureDetails"),
        )

        return ""

    def put_third_party_job_success_result(self) -> str:
        self.codepipeline_backend.put_third_party_job_success_result(
            job_id=self._get_param("jobId"),
            client_token=self._get_param("clientToken"),
            current_revision=self._get_param("currentRevision"),
            continuation_token=self._get_param("continuationToken"),
            execution_details=self._get_param("executionDetails"),
        )

        return ""

    def put_third_party_job_failure_result(self) -> str:
        self.codepipeline_backend.put_third_party_job_failure_result(
            job_id=self._get_param("jobId"),
            client_token=self._get_param("clientToken"),
            failure_details=self._get_param("failureDetails"),
        )

        return ""

    def get_job_details(self) -> str:
        job = self.codepipeline_backend.get_job_details(
            job_id=self._get_param("jobId"),
        )

        return json.dumps({"jobDetails": job})

    def get_third_party_job_details(self) -> str:
        job = self.codepipeline_backend.get_third_party_job_details(
            job_id=self._get_param("jobId"),
            client_token=self._get_param("clientToken"),
        )

        return json.dumps({"jobDetails": job})

    # --- Approval operations ---

    def put_approval_result(self) -> str:
        approved_at = self.codepipeline_backend.put_approval_result(
            pipeline_name=self._get_param("pipelineName"),
            stage_name=self._get_param("stageName"),
            action_name=self._get_param("actionName"),
            result=self._get_param("result"),
            token=self._get_param("token"),
        )

        return json.dumps({"approvedAt": approved_at})

    # --- Action Execution operations ---

    def list_action_executions(self) -> str:
        details, next_token = self.codepipeline_backend.list_action_executions(
            pipeline_name=self._get_param("pipelineName"),
            filter_param=self._get_param("filter"),
            max_results=self._get_param("maxResults"),
            next_token=self._get_param("nextToken"),
        )

        result: dict = {"actionExecutionDetails": details}
        if next_token:
            result["nextToken"] = next_token

        return json.dumps(result)

    # --- Rule operations ---

    def list_rule_executions(self) -> str:
        details, next_token = self.codepipeline_backend.list_rule_executions(
            pipeline_name=self._get_param("pipelineName"),
            filter_param=self._get_param("filter"),
            max_results=self._get_param("maxResults"),
            next_token=self._get_param("nextToken"),
        )

        result: dict = {"ruleExecutionDetails": details}
        if next_token:
            result["nextToken"] = next_token

        return json.dumps(result)

    def list_rule_types(self) -> str:
        rule_types = self.codepipeline_backend.list_rule_types()

        return json.dumps({"ruleTypes": rule_types})
    # --- Deploy Action Execution Targets ---

    def list_deploy_action_execution_targets(self) -> str:
        targets, next_token = (
            self.codepipeline_backend.list_deploy_action_execution_targets(
                pipeline_name=self._get_param("pipelineName"),
                action_execution_id=self._get_param("actionExecutionId"),
                filters=self._get_param("filters"),
                max_results=self._get_param("maxResults"),
                next_token=self._get_param("nextToken"),
            )
        )

        result: dict = {"targets": targets}
        if next_token:
            result["nextToken"] = next_token

        return json.dumps(result)

    # --- Action Revision operations ---

    def put_action_revision(self) -> str:
        new_revision, execution_id = (
            self.codepipeline_backend.put_action_revision(
                pipeline_name=self._get_param("pipelineName"),
                stage_name=self._get_param("stageName"),
                action_name=self._get_param("actionName"),
                action_revision=self._get_param("actionRevision"),
            )
        )

        return json.dumps(
            {
                "newRevision": new_revision,
                "pipelineExecutionId": execution_id,
            }
        )

    # --- Action Type update operations ---

    def update_action_type(self) -> str:
        self.codepipeline_backend.update_action_type(
            action_type=self._get_param("actionType"),
        )

        return ""
