from typing import Any

from moto.core.responses import ActionResult, BaseResponse, EmptyResult
from moto.sagemaker.exceptions import AWSValidationException

from .models import SageMakerModelBackend, sagemaker_backends


def format_enum_error(value: str, attribute: str, allowed: Any) -> str:
    return f"Value '{value}' at '{attribute}' failed to satisfy constraint: Member must satisfy enum value set: {allowed}"


class SageMakerResponse(BaseResponse):
    def __init__(self) -> None:
        super().__init__(service_name="sagemaker")
        self.automated_parameter_parsing = True

    @property
    def sagemaker_backend(self) -> SageMakerModelBackend:
        return sagemaker_backends[self.current_account][self.region]

    def describe_model(self) -> ActionResult:
        model_name = self._get_param("ModelName")
        model = self.sagemaker_backend.describe_model(model_name)
        return ActionResult(model.response_object)

    def create_model(self) -> ActionResult:
        model_name = self._get_param("ModelName")
        execution_role_arn = self._get_param("ExecutionRoleArn")
        primary_container = self._get_param("PrimaryContainer")
        vpc_config = self._get_param("VpcConfig")
        containers = self._get_param("Containers")
        tags = self._get_param("Tags")
        model = self.sagemaker_backend.create_model(
            model_name=model_name,
            execution_role_arn=execution_role_arn,
            primary_container=primary_container,
            vpc_config=vpc_config,
            containers=containers,
            tags=tags,
        )
        return ActionResult(model.response_create)

    def delete_model(self) -> ActionResult:
        model_name = self._get_param("ModelName")
        self.sagemaker_backend.delete_model(model_name)
        return EmptyResult()

    def list_models(self) -> ActionResult:
        models = self.sagemaker_backend.list_models()
        return ActionResult({"Models": [model.response_object for model in models]})

    def create_notebook_instance(self) -> ActionResult:
        sagemaker_notebook = self.sagemaker_backend.create_notebook_instance(
            notebook_instance_name=self._get_param("NotebookInstanceName"),
            instance_type=self._get_param("InstanceType"),
            subnet_id=self._get_param("SubnetId"),
            security_group_ids=self._get_param("SecurityGroupIds"),
            role_arn=self._get_param("RoleArn"),
            kms_key_id=self._get_param("KmsKeyId"),
            tags=self._get_param("Tags"),
            lifecycle_config_name=self._get_param("LifecycleConfigName"),
            direct_internet_access=self._get_param("DirectInternetAccess"),
            volume_size_in_gb=self._get_param("VolumeSizeInGB"),
            accelerator_types=self._get_param("AcceleratorTypes"),
            default_code_repository=self._get_param("DefaultCodeRepository"),
            additional_code_repositories=self._get_param("AdditionalCodeRepositories"),
            root_access=self._get_param("RootAccess"),
        )
        return ActionResult({"NotebookInstanceArn": sagemaker_notebook.arn})

    def describe_notebook_instance(self) -> ActionResult:
        notebook_instance_name = self._get_param("NotebookInstanceName")
        notebook_instance = self.sagemaker_backend.get_notebook_instance(
            notebook_instance_name
        )
        return ActionResult(notebook_instance.to_dict())

    def start_notebook_instance(self) -> ActionResult:
        notebook_instance_name = self._get_param("NotebookInstanceName")
        self.sagemaker_backend.start_notebook_instance(notebook_instance_name)
        return EmptyResult()

    def stop_notebook_instance(self) -> ActionResult:
        notebook_instance_name = self._get_param("NotebookInstanceName")
        self.sagemaker_backend.stop_notebook_instance(notebook_instance_name)
        return EmptyResult()

    def delete_notebook_instance(self) -> ActionResult:
        notebook_instance_name = self._get_param("NotebookInstanceName")
        self.sagemaker_backend.delete_notebook_instance(notebook_instance_name)
        return EmptyResult()

    def list_notebook_instances(self) -> ActionResult:
        sort_by = self._get_param("SortBy", "Name")
        sort_order = self._get_param("SortOrder", "Ascending")
        name_contains = self._get_param("NameContains")
        status = self._get_param("StatusEquals")
        max_results = self._get_param("MaxResults")
        next_token = self._get_param("NextToken")
        instances, next_token = self.sagemaker_backend.list_notebook_instances(
            sort_by=sort_by,
            sort_order=sort_order,
            name_contains=name_contains,
            status=status,
            max_results=max_results,
            next_token=next_token,
        )
        return ActionResult(
            {
                "NotebookInstances": [i.to_dict() for i in instances],
                "NextToken": next_token,
            }
        )

    def list_tags(self) -> ActionResult:
        arn = self._get_param("ResourceArn")
        max_results = self._get_param("MaxResults")
        next_token = self._get_param("NextToken")
        paged_results, next_token = self.sagemaker_backend.list_tags(
            arn=arn, MaxResults=max_results, NextToken=next_token
        )
        response = {"Tags": paged_results, "NextToken": next_token}
        return ActionResult(response)

    def add_tags(self) -> ActionResult:
        arn = self._get_param("ResourceArn")
        tags = self._get_param("Tags")
        tags = self.sagemaker_backend.add_tags(arn, tags)
        return ActionResult({"Tags": tags})

    def delete_tags(self) -> ActionResult:
        arn = self._get_param("ResourceArn")
        tag_keys = self._get_param("TagKeys")
        self.sagemaker_backend.delete_tags(arn, tag_keys)
        return EmptyResult()

    def create_endpoint_config(self) -> ActionResult:
        endpoint_config = self.sagemaker_backend.create_endpoint_config(
            endpoint_config_name=self._get_param("EndpointConfigName"),
            async_inference_config=self._get_param("AsyncInferenceConfig"),
            production_variants=self._get_param("ProductionVariants"),
            data_capture_config=self._get_param("DataCaptureConfig"),
            tags=self._get_param("Tags"),
            kms_key_id=self._get_param("KmsKeyId"),
        )
        return ActionResult({"EndpointConfigArn": endpoint_config.endpoint_config_arn})

    def describe_endpoint_config(self) -> ActionResult:
        endpoint_config_name = self._get_param("EndpointConfigName")
        response = self.sagemaker_backend.describe_endpoint_config(endpoint_config_name)
        return ActionResult(response)

    def delete_endpoint_config(self) -> ActionResult:
        endpoint_config_name = self._get_param("EndpointConfigName")
        self.sagemaker_backend.delete_endpoint_config(endpoint_config_name)
        return EmptyResult()

    def create_endpoint(self) -> ActionResult:
        endpoint = self.sagemaker_backend.create_endpoint(
            endpoint_name=self._get_param("EndpointName"),
            endpoint_config_name=self._get_param("EndpointConfigName"),
            tags=self._get_param("Tags"),
        )
        return ActionResult({"EndpointArn": endpoint.arn})

    def describe_endpoint(self) -> ActionResult:
        endpoint_name = self._get_param("EndpointName")
        response = self.sagemaker_backend.describe_endpoint(endpoint_name)
        return ActionResult(response)

    def delete_endpoint(self) -> ActionResult:
        endpoint_name = self._get_param("EndpointName")
        self.sagemaker_backend.delete_endpoint(endpoint_name)
        return EmptyResult()

    def create_processing_job(self) -> ActionResult:
        processing_job = self.sagemaker_backend.create_processing_job(
            app_specification=self._get_param("AppSpecification"),
            experiment_config=self._get_param("ExperimentConfig"),
            network_config=self._get_param("NetworkConfig"),
            processing_inputs=self._get_param("ProcessingInputs"),
            processing_job_name=self._get_param("ProcessingJobName"),
            processing_output_config=self._get_param("ProcessingOutputConfig"),
            role_arn=self._get_param("RoleArn"),
            stopping_condition=self._get_param("StoppingCondition"),
            tags=self._get_param("Tags"),
        )
        response = {"ProcessingJobArn": processing_job.arn}
        return ActionResult(response)

    def describe_processing_job(self) -> ActionResult:
        processing_job_name = self._get_param("ProcessingJobName")
        response = self.sagemaker_backend.describe_processing_job(processing_job_name)
        return ActionResult(response)

    def create_transform_job(self) -> ActionResult:
        transform_job = self.sagemaker_backend.create_transform_job(
            transform_job_name=self._get_param("TransformJobName"),
            model_name=self._get_param("ModelName"),
            max_concurrent_transforms=self._get_param("MaxConcurrentTransforms"),
            model_client_config=self._get_param("ModelClientConfig"),
            max_payload_in_mb=self._get_param("MaxPayloadInMB"),
            batch_strategy=self._get_param("BatchStrategy"),
            environment=self._get_param("Environment"),
            transform_input=self._get_param("TransformInput"),
            transform_output=self._get_param("TransformOutput"),
            data_capture_config=self._get_param("DataCaptureConfig"),
            transform_resources=self._get_param("TransformResources"),
            data_processing=self._get_param("DataProcessing"),
            tags=self._get_param("Tags"),
            experiment_config=self._get_param("ExperimentConfig"),
        )
        response = {
            "TransformJobArn": transform_job.arn,
        }
        return ActionResult(response)

    def describe_transform_job(self) -> ActionResult:
        transform_job_name = self._get_param("TransformJobName")
        response = self.sagemaker_backend.describe_transform_job(
            transform_job_name=transform_job_name
        )
        return ActionResult(response)

    def create_training_job(self) -> ActionResult:
        training_job = self.sagemaker_backend.create_training_job(
            training_job_name=self._get_param("TrainingJobName"),
            hyper_parameters=self._get_param("HyperParameters"),
            algorithm_specification=self._get_param("AlgorithmSpecification"),
            role_arn=self._get_param("RoleArn"),
            input_data_config=self._get_param("InputDataConfig"),
            output_data_config=self._get_param("OutputDataConfig"),
            resource_config=self._get_param("ResourceConfig"),
            vpc_config=self._get_param("VpcConfig"),
            stopping_condition=self._get_param("StoppingCondition"),
            tags=self._get_param("Tags"),
            enable_network_isolation=self._get_param("EnableNetworkIsolation", False),
            enable_inter_container_traffic_encryption=self._get_param(
                "EnableInterContainerTrafficEncryption", False
            ),
            enable_managed_spot_training=self._get_param(
                "EnableManagedSpotTraining", False
            ),
            checkpoint_config=self._get_param("CheckpointConfig"),
            debug_hook_config=self._get_param("DebugHookConfig"),
            debug_rule_configurations=self._get_param("DebugRuleConfigurations"),
            tensor_board_output_config=self._get_param("TensorBoardOutputConfig"),
            experiment_config=self._get_param("ExperimentConfig"),
        )
        response = {
            "TrainingJobArn": training_job.arn,
        }
        return ActionResult(response)

    def describe_training_job(self) -> ActionResult:
        training_job_name = self._get_param("TrainingJobName")
        response = self.sagemaker_backend.describe_training_job(training_job_name)
        return ActionResult(response)

    def create_notebook_instance_lifecycle_config(self) -> ActionResult:
        lifecycle_configuration = (
            self.sagemaker_backend.create_notebook_instance_lifecycle_config(
                notebook_instance_lifecycle_config_name=self._get_param(
                    "NotebookInstanceLifecycleConfigName"
                ),
                on_create=self._get_param("OnCreate"),
                on_start=self._get_param("OnStart"),
            )
        )
        response = {
            "NotebookInstanceLifecycleConfigArn": lifecycle_configuration.arn,
        }
        return ActionResult(response)

    def describe_notebook_instance_lifecycle_config(self) -> ActionResult:
        response = self.sagemaker_backend.describe_notebook_instance_lifecycle_config(
            notebook_instance_lifecycle_config_name=self._get_param(
                "NotebookInstanceLifecycleConfigName"
            )
        )
        return ActionResult(response)

    def delete_notebook_instance_lifecycle_config(self) -> ActionResult:
        self.sagemaker_backend.delete_notebook_instance_lifecycle_config(
            notebook_instance_lifecycle_config_name=self._get_param(
                "NotebookInstanceLifecycleConfigName"
            )
        )
        return EmptyResult()

    def search(self) -> ActionResult:
        response = self.sagemaker_backend.search(
            resource=self._get_param("Resource"),
            search_expression=self._get_param("SearchExpression"),
        )
        return ActionResult(response)

    def list_experiments(self) -> ActionResult:
        MaxResults = self._get_param("MaxResults")
        NextToken = self._get_param("NextToken")

        paged_results, next_token = self.sagemaker_backend.list_experiments(
            MaxResults=MaxResults, NextToken=NextToken
        )

        experiment_summaries = [
            {
                "ExperimentName": experiment_data.experiment_name,
                "ExperimentArn": experiment_data.arn,
                "CreationTime": experiment_data.creation_time,
                "LastModifiedTime": experiment_data.last_modified_time,
            }
            for experiment_data in paged_results
        ]

        response = {
            "ExperimentSummaries": experiment_summaries,
            "NextToken": next_token,
        }

        return ActionResult(response)

    def delete_experiment(self) -> ActionResult:
        self.sagemaker_backend.delete_experiment(
            experiment_name=self._get_param("ExperimentName")
        )
        return EmptyResult()

    def create_experiment(self) -> ActionResult:
        response = self.sagemaker_backend.create_experiment(
            experiment_name=self._get_param("ExperimentName")
        )
        return ActionResult(response)

    def describe_experiment(self) -> ActionResult:
        response = self.sagemaker_backend.describe_experiment(
            experiment_name=self._get_param("ExperimentName")
        )
        return ActionResult(response)

    def list_trials(self) -> ActionResult:
        MaxResults = self._get_param("MaxResults")
        NextToken = self._get_param("NextToken")

        paged_results, next_token = self.sagemaker_backend.list_trials(
            NextToken=NextToken,
            MaxResults=MaxResults,
            experiment_name=self._get_param("ExperimentName"),
            trial_component_name=self._get_param("TrialComponentName"),
        )

        trial_summaries = [
            {
                "TrialName": trial_data.trial_name,
                "TrialArn": trial_data.arn,
                "CreationTime": trial_data.creation_time,
                "LastModifiedTime": trial_data.last_modified_time,
            }
            for trial_data in paged_results
        ]

        response = {"TrialSummaries": trial_summaries, "NextToken": next_token}

        return ActionResult(response)

    def create_trial(self) -> ActionResult:
        response = self.sagemaker_backend.create_trial(
            trial_name=self._get_param("TrialName"),
            experiment_name=self._get_param("ExperimentName"),
        )
        return ActionResult(response)

    def list_trial_components(self) -> ActionResult:
        MaxResults = self._get_param("MaxResults")
        NextToken = self._get_param("NextToken")

        paged_results, next_token = self.sagemaker_backend.list_trial_components(
            NextToken=NextToken,
            MaxResults=MaxResults,
            trial_name=self._get_param("TrialName"),
        )

        trial_component_summaries = [
            {
                "TrialComponentName": trial_component_data.trial_component_name,
                "TrialComponentArn": trial_component_data.arn,
                "CreationTime": trial_component_data.creation_time,
                "LastModifiedTime": trial_component_data.last_modified_time,
            }
            for trial_component_data in paged_results
        ]

        response = {
            "TrialComponentSummaries": trial_component_summaries,
            "NextToken": next_token,
        }

        return ActionResult(response)

    def create_trial_component(self) -> ActionResult:
        response = self.sagemaker_backend.create_trial_component(
            trial_component_name=self._get_param("TrialComponentName"),
            start_time=self._get_param("StartTime"),
            end_time=self._get_param("EndTime"),
            display_name=self._get_param("DisplayName"),
            parameters=self._get_param("Parameters"),
            input_artifacts=self._get_param("InputArtifacts"),
            output_artifacts=self._get_param("OutputArtifacts"),
            metadata_properties=self._get_param("MetadataProperties"),
            status=self._get_param("Status"),
            trial_name=self._get_param("TrialName"),
        )
        return ActionResult(response)

    def describe_trial(self) -> ActionResult:
        trial_name = self._get_param("TrialName")
        response = self.sagemaker_backend.describe_trial(trial_name)
        return ActionResult(response)

    def delete_trial(self) -> ActionResult:
        trial_name = self._get_param("TrialName")
        self.sagemaker_backend.delete_trial(trial_name)
        return EmptyResult()

    def delete_trial_component(self) -> ActionResult:
        trial_component_name = self._get_param("TrialComponentName")
        self.sagemaker_backend.delete_trial_component(trial_component_name)
        return EmptyResult()

    def describe_trial_component(self) -> ActionResult:
        trial_component_name = self._get_param("TrialComponentName")
        response = self.sagemaker_backend.describe_trial_component(trial_component_name)
        return ActionResult(response)

    def associate_trial_component(self) -> ActionResult:
        trial_name = self._get_param("TrialName")
        trial_component_name = self._get_param("TrialComponentName")
        response = self.sagemaker_backend.associate_trial_component(
            trial_name, trial_component_name
        )
        return ActionResult(response)

    def disassociate_trial_component(self) -> ActionResult:
        trial_component_name = self._get_param("TrialComponentName")
        trial_name = self._get_param("TrialName")
        response = self.sagemaker_backend.disassociate_trial_component(
            trial_name, trial_component_name
        )
        return ActionResult(response)

    def update_trial_component(self) -> ActionResult:
        response = self.sagemaker_backend.update_trial_component(
            trial_component_name=self._get_param("TrialComponentName"),
            status=self._get_param("Status"),
            display_name=self._get_param("DisplayName"),
            start_time=self._get_param("StartTime"),
            end_time=self._get_param("EndTime"),
            parameters=self._get_param("Parameters"),
            parameters_to_remove=self._get_param("ParametersToRemove"),
            input_artifacts=self._get_param("InputArtifacts"),
            input_artifacts_to_remove=self._get_param("InputArtifactsToRemove"),
            output_artifacts=self._get_param("OutputArtifacts"),
            output_artifacts_to_remove=self._get_param("OutputArtifactsToRemove"),
        )
        return ActionResult(response)

    def describe_pipeline(self) -> ActionResult:
        response = self.sagemaker_backend.describe_pipeline(
            self._get_param("PipelineName")
        )
        return ActionResult(response)

    def start_pipeline_execution(self) -> ActionResult:
        response = self.sagemaker_backend.start_pipeline_execution(
            self._get_param("PipelineName"),
            self._get_param("PipelineExecutionDisplayName"),
            self._get_param("PipelineParameters"),
            self._get_param("PipelineExecutionDescription"),
            self._get_param("ParallelismConfiguration"),
            self._get_param("ClientRequestToken"),
        )
        return ActionResult(response)

    def describe_pipeline_execution(self) -> ActionResult:
        response = self.sagemaker_backend.describe_pipeline_execution(
            self._get_param("PipelineExecutionArn")
        )
        return ActionResult(response)

    def describe_pipeline_definition_for_execution(self) -> ActionResult:
        response = self.sagemaker_backend.describe_pipeline_definition_for_execution(
            self._get_param("PipelineExecutionArn")
        )
        return ActionResult(response)

    def list_pipeline_parameters_for_execution(self) -> ActionResult:
        response = self.sagemaker_backend.list_pipeline_parameters_for_execution(
            self._get_param("PipelineExecutionArn")
        )
        return ActionResult(response)

    def list_pipeline_executions(self) -> ActionResult:
        response = self.sagemaker_backend.list_pipeline_executions(
            self._get_param("PipelineName")
        )
        return ActionResult(response)

    def create_pipeline(self) -> ActionResult:
        pipeline = self.sagemaker_backend.create_pipeline(
            pipeline_name=self._get_param("PipelineName"),
            pipeline_display_name=self._get_param("PipelineDisplayName"),
            pipeline_definition=self._get_param("PipelineDefinition"),
            pipeline_definition_s3_location=self._get_param(
                "PipelineDefinitionS3Location"
            ),
            pipeline_description=self._get_param("PipelineDescription"),
            role_arn=self._get_param("RoleArn"),
            tags=self._get_param("Tags"),
            parallelism_configuration=self._get_param("ParallelismConfiguration"),
        )
        response = {
            "PipelineArn": pipeline.arn,
        }

        return ActionResult(response)

    def delete_pipeline(self) -> ActionResult:
        arn = self.sagemaker_backend.delete_pipeline(
            pipeline_name=self._get_param("PipelineName"),
        )
        response = {"PipelineArn": arn}
        return ActionResult(response)

    def update_pipeline(self) -> ActionResult:
        arn = self.sagemaker_backend.update_pipeline(
            pipeline_name=self._get_param("PipelineName"),
            pipeline_display_name=self._get_param("PipelineDisplayName"),
            pipeline_definition=self._get_param("PipelineDefinition"),
            pipeline_definition_s3_location=self._get_param(
                "PipelineDefinitionS3Location"
            ),
            pipeline_description=self._get_param("PipelineDescription"),
            role_arn=self._get_param("RoleArn"),
            parallelism_configuration=self._get_param("ParallelismConfiguration"),
        )

        response = {"PipelineArn": arn}
        return ActionResult(response)

    def list_pipelines(self) -> ActionResult:
        max_results_range = range(1, 101)
        allowed_sort_by = ("Name", "CreationTime")
        allowed_sort_order = ("Ascending", "Descending")

        pipeline_name_prefix = self._get_param("PipelineNamePrefix")
        created_after = self._get_param("CreatedAfter")
        created_before = self._get_param("CreatedBefore")
        sort_by = self._get_param("SortBy", "CreationTime")
        sort_order = self._get_param("SortOrder", "Descending")
        next_token = self._get_param("NextToken")
        max_results = self._get_param("MaxResults")

        errors = []
        if max_results and max_results not in max_results_range:
            errors.append(
                f"Value '{max_results}' at 'maxResults' failed to satisfy constraint: Member must have value less than or equal to {max_results_range[-1]}"
            )

        if sort_by not in allowed_sort_by:
            errors.append(format_enum_error(sort_by, "SortBy", allowed_sort_by))
        if sort_order not in allowed_sort_order:
            errors.append(
                format_enum_error(sort_order, "SortOrder", allowed_sort_order)
            )
        if errors:
            raise AWSValidationException(
                f"{len(errors)} validation errors detected: {';'.join(errors)}"
            )

        response = self.sagemaker_backend.list_pipelines(
            pipeline_name_prefix=pipeline_name_prefix,
            created_after=created_after,
            created_before=created_before,
            next_token=next_token,
            max_results=max_results,
            sort_by=sort_by,
            sort_order=sort_order,
        )

        return ActionResult(response)

    def list_processing_jobs(self) -> ActionResult:
        max_results_range = range(1, 101)
        allowed_sort_by = ["Name", "CreationTime", "Status"]
        allowed_sort_order = ["Ascending", "Descending"]
        allowed_status_equals = [
            "Completed",
            "Stopped",
            "InProgress",
            "Stopping",
            "Failed",
        ]

        max_results = self._get_int_param("MaxResults")
        sort_by = self._get_param("SortBy", "CreationTime")
        sort_order = self._get_param("SortOrder", "Ascending")
        status_equals = self._get_param("StatusEquals")
        next_token = self._get_param("NextToken")
        errors = []
        if max_results and max_results not in max_results_range:
            errors.append(
                f"Value '{max_results}' at 'maxResults' failed to satisfy constraint: Member must have value less than or equal to {max_results_range[-1]}"
            )

        if sort_by not in allowed_sort_by:
            errors.append(format_enum_error(sort_by, "sortBy", allowed_sort_by))
        if sort_order not in allowed_sort_order:
            errors.append(
                format_enum_error(sort_order, "sortOrder", allowed_sort_order)
            )

        if status_equals and status_equals not in allowed_status_equals:
            errors.append(
                format_enum_error(status_equals, "statusEquals", allowed_status_equals)
            )

        if errors != []:
            raise AWSValidationException(
                f"{len(errors)} validation errors detected: {';'.join(errors)}"
            )

        response = self.sagemaker_backend.list_processing_jobs(
            next_token=next_token,
            max_results=max_results,
            creation_time_after=self._get_param("CreationTimeAfter"),
            creation_time_before=self._get_param("CreationTimeBefore"),
            last_modified_time_after=self._get_param("LastModifiedTimeAfter"),
            last_modified_time_before=self._get_param("LastModifiedTimeBefore"),
            name_contains=self._get_param("NameContains"),
            status_equals=status_equals,
        )
        return ActionResult(response)

    def list_transform_jobs(self) -> ActionResult:
        max_results_range = range(1, 101)
        allowed_sort_by = ["Name", "CreationTime", "Status"]
        allowed_sort_order = ["Ascending", "Descending"]
        allowed_status_equals = [
            "Completed",
            "Stopped",
            "InProgress",
            "Stopping",
            "Failed",
        ]

        max_results = self._get_int_param("MaxResults")
        sort_by = self._get_param("SortBy", "CreationTime")
        sort_order = self._get_param("SortOrder", "Ascending")
        status_equals = self._get_param("StatusEquals")
        next_token = self._get_param("NextToken")
        errors = []
        if max_results and max_results not in max_results_range:
            errors.append(
                f"Value '{max_results}' at 'maxResults' failed to satisfy constraint: Member must have value less than or equal to {max_results_range[-1]}"
            )

        if sort_by not in allowed_sort_by:
            errors.append(format_enum_error(sort_by, "sortBy", allowed_sort_by))
        if sort_order not in allowed_sort_order:
            errors.append(
                format_enum_error(sort_order, "sortOrder", allowed_sort_order)
            )

        if status_equals and status_equals not in allowed_status_equals:
            errors.append(
                format_enum_error(status_equals, "statusEquals", allowed_status_equals)
            )

        if errors != []:
            raise AWSValidationException(
                f"{len(errors)} validation errors detected: {';'.join(errors)}"
            )

        response = self.sagemaker_backend.list_transform_jobs(
            next_token=next_token,
            max_results=max_results,
            creation_time_after=self._get_param("CreationTimeAfter"),
            creation_time_before=self._get_param("CreationTimeBefore"),
            last_modified_time_after=self._get_param("LastModifiedTimeAfter"),
            last_modified_time_before=self._get_param("LastModifiedTimeBefore"),
            name_contains=self._get_param("NameContains"),
            status_equals=status_equals,
        )
        return ActionResult(response)

    def list_training_jobs(self) -> ActionResult:
        max_results_range = range(1, 101)
        allowed_sort_by = ["Name", "CreationTime", "Status"]
        allowed_sort_order = ["Ascending", "Descending"]
        allowed_status_equals = [
            "Completed",
            "Stopped",
            "InProgress",
            "Stopping",
            "Failed",
        ]

        max_results = self._get_int_param("MaxResults")
        sort_by = self._get_param("SortBy", "CreationTime")
        sort_order = self._get_param("SortOrder", "Ascending")
        status_equals = self._get_param("StatusEquals")
        next_token = self._get_param("NextToken")
        errors = []
        if max_results and max_results not in max_results_range:
            errors.append(
                f"Value '{max_results}' at 'maxResults' failed to satisfy constraint: Member must have value less than or equal to {max_results_range[-1]}"
            )

        if sort_by not in allowed_sort_by:
            errors.append(format_enum_error(sort_by, "sortBy", allowed_sort_by))
        if sort_order not in allowed_sort_order:
            errors.append(
                format_enum_error(sort_order, "sortOrder", allowed_sort_order)
            )

        if status_equals and status_equals not in allowed_status_equals:
            errors.append(
                format_enum_error(status_equals, "statusEquals", allowed_status_equals)
            )

        if errors != []:
            raise AWSValidationException(
                f"{len(errors)} validation errors detected: {';'.join(errors)}"
            )

        response = self.sagemaker_backend.list_training_jobs(
            next_token=next_token,
            max_results=max_results,
            creation_time_after=self._get_param("CreationTimeAfter"),
            creation_time_before=self._get_param("CreationTimeBefore"),
            last_modified_time_after=self._get_param("LastModifiedTimeAfter"),
            last_modified_time_before=self._get_param("LastModifiedTimeBefore"),
            name_contains=self._get_param("NameContains"),
            status_equals=status_equals,
        )
        return ActionResult(response)

    def update_endpoint_weights_and_capacities(self) -> ActionResult:
        endpoint_name = self._get_param("EndpointName")
        desired_weights_and_capacities = self._get_param("DesiredWeightsAndCapacities")
        endpoint_arn = self.sagemaker_backend.update_endpoint_weights_and_capacities(
            endpoint_name=endpoint_name,
            desired_weights_and_capacities=desired_weights_and_capacities,
        )
        return ActionResult({"EndpointArn": endpoint_arn})

    def list_model_package_groups(self) -> ActionResult:
        creation_time_after = self._get_param("CreationTimeAfter")
        creation_time_before = self._get_param("CreationTimeBefore")
        max_results = self._get_param("MaxResults")
        name_contains = self._get_param("NameContains")
        next_token = self._get_param("NextToken")
        sort_by = self._get_param("SortBy")
        sort_order = self._get_param("SortOrder")
        (
            model_package_group_summary_list,
            next_token,
        ) = self.sagemaker_backend.list_model_package_groups(
            creation_time_after=creation_time_after,
            creation_time_before=creation_time_before,
            max_results=max_results,
            name_contains=name_contains,
            next_token=next_token,
            sort_by=sort_by,
            sort_order=sort_order,
        )
        model_package_group_summary_list_response_object = [
            x.gen_response_object() for x in model_package_group_summary_list
        ]
        return ActionResult(
            {
                "ModelPackageGroupSummaryList": model_package_group_summary_list_response_object,
                "NextToken": next_token,
            }
        )

    def list_model_packages(self) -> ActionResult:
        creation_time_after = self._get_param("CreationTimeAfter")
        creation_time_before = self._get_param("CreationTimeBefore")
        max_results = self._get_param("MaxResults")
        name_contains = self._get_param("NameContains")
        model_approval_status = self._get_param("ModelApprovalStatus")
        model_package_group_name = self._get_param("ModelPackageGroupName")
        model_package_type = self._get_param("ModelPackageType", "Unversioned")
        next_token = self._get_param("NextToken")
        sort_by = self._get_param("SortBy")
        sort_order = self._get_param("SortOrder")
        (
            model_package_summary_list,
            next_token,
        ) = self.sagemaker_backend.list_model_packages(
            creation_time_after=creation_time_after,
            creation_time_before=creation_time_before,
            max_results=max_results,
            name_contains=name_contains,
            model_approval_status=model_approval_status,
            model_package_group_name=model_package_group_name,
            model_package_type=model_package_type,
            next_token=next_token,
            sort_by=sort_by,
            sort_order=sort_order,
        )
        model_package_summary_list_response_object = [
            x.gen_response_object() for x in model_package_summary_list
        ]
        return ActionResult(
            {
                "ModelPackageSummaryList": model_package_summary_list_response_object,
                "NextToken": next_token,
            }
        )

    def describe_model_package(self) -> ActionResult:
        model_package_name = self._get_param("ModelPackageName")
        model_package = self.sagemaker_backend.describe_model_package(
            model_package_name=model_package_name,
        )
        return ActionResult(
            model_package.gen_response_object(),
        )

    def describe_model_package_group(self) -> ActionResult:
        model_package_group_name = self._get_param("ModelPackageGroupName")
        model_package_group = self.sagemaker_backend.describe_model_package_group(
            model_package_group_name=model_package_group_name,
        )
        return ActionResult(
            model_package_group.gen_response_object(),
        )

    def update_model_package(self) -> ActionResult:
        model_package_arn = self._get_param("ModelPackageArn")
        model_approval_status = self._get_param("ModelApprovalStatus")
        approval_dexcription = self._get_param("ApprovalDescription")
        customer_metadata_properties = self._get_param("CustomerMetadataProperties")
        customer_metadata_properties_to_remove = self._get_param(
            "CustomerMetadataPropertiesToRemove", []
        )
        additional_inference_specification_to_add = self._get_param(
            "AdditionalInferenceSpecificationsToAdd"
        )
        updated_model_package_arn = self.sagemaker_backend.update_model_package(
            model_package_arn=model_package_arn,
            model_approval_status=model_approval_status,
            approval_description=approval_dexcription,
            customer_metadata_properties=customer_metadata_properties,
            customer_metadata_properties_to_remove=customer_metadata_properties_to_remove,
            additional_inference_specifications_to_add=additional_inference_specification_to_add,
        )
        return ActionResult({"ModelPackageArn": updated_model_package_arn})

    def create_model_package(self) -> ActionResult:
        model_package_name = self._get_param("ModelPackageName")
        model_package_group_name = self._get_param("ModelPackageGroupName")
        model_package_description = self._get_param("ModelPackageDescription")
        inference_specification = self._get_param("InferenceSpecification")
        validation_specification = self._get_param("ValidationSpecification")
        source_algorithm_specification = self._get_param("SourceAlgorithmSpecification")
        certify_for_marketplace = self._get_param("CertifyForMarketplace", False)
        tags = self._get_param("Tags")
        model_approval_status = self._get_param("ModelApprovalStatus")
        metadata_properties = self._get_param("MetadataProperties")
        model_metrics = self._get_param("ModelMetrics")
        client_token = self._get_param("ClientToken")
        customer_metadata_properties = self._get_param("CustomerMetadataProperties")
        drift_check_baselines = self._get_param("DriftCheckBaselines")
        domain = self._get_param("Domain")
        task = self._get_param("Task")
        sample_payload_url = self._get_param("SamplePayloadUrl")
        additional_inference_specifications = self._get_param(
            "AdditionalInferenceSpecifications", None
        )
        model_package_arn = self.sagemaker_backend.create_model_package(
            model_package_name=model_package_name,
            model_package_group_name=model_package_group_name,
            model_package_description=model_package_description,
            inference_specification=inference_specification,
            validation_specification=validation_specification,
            source_algorithm_specification=source_algorithm_specification,
            certify_for_marketplace=certify_for_marketplace,
            tags=tags,
            model_approval_status=model_approval_status,
            metadata_properties=metadata_properties,
            model_metrics=model_metrics,
            customer_metadata_properties=customer_metadata_properties,
            drift_check_baselines=drift_check_baselines,
            domain=domain,
            task=task,
            sample_payload_url=sample_payload_url,
            additional_inference_specifications=additional_inference_specifications,
            client_token=client_token,
        )
        return ActionResult({"ModelPackageArn": model_package_arn})

    def create_model_package_group(self) -> ActionResult:
        model_package_group_name = self._get_param("ModelPackageGroupName")
        model_package_group_description = self._get_param(
            "ModelPackageGroupDescription"
        )
        tags = self._get_param("Tags")
        model_package_group_arn = self.sagemaker_backend.create_model_package_group(
            model_package_group_name=model_package_group_name,
            model_package_group_description=model_package_group_description,
            tags=tags,
        )
        return ActionResult({"ModelPackageGroupArn": model_package_group_arn})

    def create_feature_group(self) -> ActionResult:
        feature_group_arn = self.sagemaker_backend.create_feature_group(
            feature_group_name=self._get_param("FeatureGroupName"),
            record_identifier_feature_name=self._get_param(
                "RecordIdentifierFeatureName"
            ),
            event_time_feature_name=self._get_param("EventTimeFeatureName"),
            feature_definitions=self._get_param("FeatureDefinitions"),
            offline_store_config=self._get_param("OfflineStoreConfig"),
            role_arn=self._get_param("RoleArn"),
            tags=self._get_param("Tags"),
        )
        return ActionResult({"FeatureGroupArn": feature_group_arn})

    def describe_feature_group(self) -> ActionResult:
        resp = self.sagemaker_backend.describe_feature_group(
            feature_group_name=self._get_param("FeatureGroupName"),
        )
        return ActionResult(resp)

    def create_cluster(self) -> ActionResult:
        cluster_name = self._get_param("ClusterName")
        instance_groups = self._get_param("InstanceGroups")
        vpc_config = self._get_param("VpcConfig")
        tags = self._get_param("Tags")
        cluster_arn = self.sagemaker_backend.create_cluster(
            cluster_name=cluster_name,
            instance_groups=instance_groups,
            vpc_config=vpc_config,
            tags=tags,
        )
        return ActionResult({"ClusterArn": cluster_arn})

    def delete_cluster(self) -> ActionResult:
        cluster_name = self._get_param("ClusterName")
        cluster_arn = self.sagemaker_backend.delete_cluster(
            cluster_name=cluster_name,
        )
        return ActionResult({"ClusterArn": cluster_arn})

    def describe_cluster(self) -> ActionResult:
        cluster_name = self._get_param("ClusterName")
        cluster_description = self.sagemaker_backend.describe_cluster(
            cluster_name=cluster_name,
        )
        return ActionResult(cluster_description)

    def describe_cluster_node(self) -> ActionResult:
        cluster_name = self._get_param("ClusterName")
        node_id = self._get_param("NodeId")
        node_details = self.sagemaker_backend.describe_cluster_node(
            cluster_name=cluster_name,
            node_id=node_id,
        )
        return ActionResult({"NodeDetails": node_details})

    def list_clusters(self) -> ActionResult:
        creation_time_after = self._get_param("CreationTimeAfter")
        creation_time_before = self._get_param("CreationTimeBefore")
        max_results = self._get_param("MaxResults")
        name_contains = self._get_param("NameContains")
        next_token = self._get_param("NextToken")
        sort_by = self._get_param("SortBy")
        sort_order = self._get_param("SortOrder")
        clusters, next_token = self.sagemaker_backend.list_clusters(
            creation_time_after=creation_time_after,
            creation_time_before=creation_time_before,
            max_results=max_results,
            name_contains=name_contains,
            next_token=next_token,
            sort_by=sort_by,
            sort_order=sort_order,
        )
        cluster_summaries = [cluster.summary() for cluster in clusters]
        return ActionResult(
            {"NextToken": next_token, "ClusterSummaries": cluster_summaries}
        )

    def list_cluster_nodes(self) -> ActionResult:
        cluster_name = self._get_param("ClusterName")
        creation_time_after = self._get_param("CreationTimeAfter")
        creation_time_before = self._get_param("CreationTimeBefore")
        instance_group_name_contains = self._get_param("InstanceGroupNameContains")
        max_results = self._get_param("MaxResults")
        next_token = self._get_param("NextToken")
        sort_by = self._get_param("SortBy")
        sort_order = self._get_param("SortOrder")
        cluster_nodes, next_token = self.sagemaker_backend.list_cluster_nodes(
            cluster_name=cluster_name,
            creation_time_after=creation_time_after,
            creation_time_before=creation_time_before,
            instance_group_name_contains=instance_group_name_contains,
            max_results=max_results,
            next_token=next_token,
            sort_by=sort_by,
            sort_order=sort_order,
        )
        cluster_node_summaries = [node.summary() for node in cluster_nodes]
        return ActionResult(
            {"NextToken": next_token, "ClusterNodeSummaries": cluster_node_summaries}
        )

    def create_model_bias_job_definition(self) -> ActionResult:
        account_id = self.current_account
        job_definition_name = self._get_param("JobDefinitionName")
        tags = self._get_param("Tags", [])
        role_arn = self._get_param("RoleArn")
        job_resources = self._get_param("JobResources")
        stopping_condition = self._get_param("StoppingCondition")
        environment = self._get_param("Environment", {})
        network_config = self._get_param("NetworkConfig", {})
        model_bias_baseline_config = self._get_param("ModelBiasBaselineConfig", {})
        model_bias_app_specification = self._get_param("ModelBiasAppSpecification")
        model_bias_job_input = self._get_param("ModelBiasJobInput")
        model_bias_job_output_config = self._get_param("ModelBiasJobOutputConfig")

        response = self.sagemaker_backend.create_model_bias_job_definition(
            account_id=account_id,
            job_definition_name=job_definition_name,
            tags=tags,
            role_arn=role_arn,
            job_resources=job_resources,
            stopping_condition=stopping_condition,
            environment=environment,
            network_config=network_config,
            model_bias_baseline_config=model_bias_baseline_config,
            model_bias_app_specification=model_bias_app_specification,
            model_bias_job_input=model_bias_job_input,
            model_bias_job_output_config=model_bias_job_output_config,
        )
        return ActionResult(response)

    def list_model_bias_job_definitions(self) -> ActionResult:
        result, next_token = self.sagemaker_backend.list_model_bias_job_definitions()
        return ActionResult({"JobDefinitionSummaries": result, "NextToken": next_token})

    def describe_model_bias_job_definition(self) -> ActionResult:
        job_definition_name = self._get_param("JobDefinitionName")
        job_definition = self.sagemaker_backend.describe_model_bias_job_definition(
            job_definition_name
        )
        return ActionResult(job_definition)

    def delete_model_bias_job_definition(self) -> ActionResult:
        job_definition_name = self._get_param("JobDefinitionName")
        self.sagemaker_backend.delete_model_bias_job_definition(job_definition_name)
        return EmptyResult()

    def create_data_quality_job_definition(self) -> ActionResult:
        account_id = self.current_account
        job_definition_name = self._get_param("JobDefinitionName")
        tags = self._get_param("Tags", [])
        role_arn = self._get_param("RoleArn")
        job_resources = self._get_param("JobResources")
        stopping_condition = self._get_param("StoppingCondition")
        environment = self._get_param("Environment", {})
        network_config = self._get_param("NetworkConfig", {})
        data_quality_baseline_config = self._get_param("DataQualityBaselineConfig", {})
        data_quality_app_specification = self._get_param("DataQualityAppSpecification")
        data_quality_job_input = self._get_param("DataQualityJobInput")
        data_quality_job_output_config = self._get_param("DataQualityJobOutputConfig")

        response = self.sagemaker_backend.create_data_quality_job_definition(
            account_id=account_id,
            job_definition_name=job_definition_name,
            tags=tags,
            role_arn=role_arn,
            job_resources=job_resources,
            stopping_condition=stopping_condition,
            environment=environment,
            network_config=network_config,
            data_quality_baseline_config=data_quality_baseline_config,
            data_quality_app_specification=data_quality_app_specification,
            data_quality_job_input=data_quality_job_input,
            data_quality_job_output_config=data_quality_job_output_config,
        )
        return ActionResult(response)

    def list_data_quality_job_definitions(self) -> ActionResult:
        result, next_token = self.sagemaker_backend.list_data_quality_job_definitions()
        return ActionResult({"JobDefinitionSummaries": result, "NextToken": next_token})

    def describe_data_quality_job_definition(self) -> ActionResult:
        job_definition_name = self._get_param("JobDefinitionName")
        job_definition = self.sagemaker_backend.describe_data_quality_job_definition(
            job_definition_name
        )
        return ActionResult(job_definition)

    def delete_data_quality_job_definition(self) -> ActionResult:
        job_definition_name = self._get_param("JobDefinitionName")
        self.sagemaker_backend.delete_data_quality_job_definition(job_definition_name)
        return EmptyResult()

    def create_auto_ml_job_v2(self) -> ActionResult:
        auto_ml_job_name = self._get_param("AutoMLJobName")
        auto_ml_job_input_data_config = self._get_param("AutoMLJobInputDataConfig")
        output_data_config = self._get_param("OutputDataConfig")
        auto_ml_problem_type_config = self._get_param("AutoMLProblemTypeConfig")
        role_arn = self._get_param("RoleArn")
        tags = self._get_param("Tags")
        security_config = self._get_param("SecurityConfig")
        auto_ml_job_objective = self._get_param("AutoMLJobObjective")
        model_deploy_config = self._get_param("ModelDeployConfig")
        data_split_config = self._get_param("DataSplitConfig")
        auto_ml_job_arn = self.sagemaker_backend.create_auto_ml_job_v2(
            auto_ml_job_name=auto_ml_job_name,
            auto_ml_job_input_data_config=auto_ml_job_input_data_config,
            output_data_config=output_data_config,
            auto_ml_problem_type_config=auto_ml_problem_type_config,
            role_arn=role_arn,
            tags=tags,
            security_config=security_config,
            auto_ml_job_objective=auto_ml_job_objective,
            model_deploy_config=model_deploy_config,
            data_split_config=data_split_config,
        )
        return ActionResult({"AutoMLJobArn": auto_ml_job_arn})

    def describe_auto_ml_job_v2(self) -> ActionResult:
        auto_ml_job_name = self._get_param("AutoMLJobName")
        auto_ml_job_description = self.sagemaker_backend.describe_auto_ml_job_v2(
            auto_ml_job_name=auto_ml_job_name,
        )
        return ActionResult(auto_ml_job_description)

    def list_auto_ml_jobs(self) -> ActionResult:
        creation_time_after = self._get_param("CreationTimeAfter")
        creation_time_before = self._get_param("CreationTimeBefore")
        last_modified_time_after = self._get_param("LastModifiedTimeAfter")
        last_modified_time_before = self._get_param("LastModifiedTimeBefore")
        name_contains = self._get_param("NameContains")
        status_equals = self._get_param("StatusEquals")
        sort_order = self._get_param("SortOrder")
        sort_by = self._get_param("SortBy")
        max_results = self._get_param("MaxResults")
        next_token = self._get_param("NextToken")
        auto_ml_jobs, next_token = self.sagemaker_backend.list_auto_ml_jobs(
            creation_time_after=creation_time_after,
            creation_time_before=creation_time_before,
            last_modified_time_after=last_modified_time_after,
            last_modified_time_before=last_modified_time_before,
            name_contains=name_contains,
            status_equals=status_equals,
            sort_order=sort_order,
            sort_by=sort_by,
            max_results=max_results,
            next_token=next_token,
        )
        auto_ml_job_summaries = [auto_ml_job.summary() for auto_ml_job in auto_ml_jobs]
        return ActionResult(
            {"AutoMLJobSummaries": auto_ml_job_summaries, "NextToken": next_token}
        )

    def stop_auto_ml_job(self) -> ActionResult:
        auto_ml_job_name = self._get_param("AutoMLJobName")
        self.sagemaker_backend.stop_auto_ml_job(
            auto_ml_job_name=auto_ml_job_name,
        )
        return EmptyResult()

    def list_endpoints(self) -> ActionResult:
        sort_by = self._get_param("SortBy")
        sort_order = self._get_param("SortOrder")
        next_token = self._get_param("NextToken")
        max_results = self._get_param("MaxResults")
        name_contains = self._get_param("NameContains")
        creation_time_before = self._get_param("CreationTimeBefore")
        creation_time_after = self._get_param("CreationTimeAfter")
        last_modified_time_before = self._get_param("LastModifiedTimeBefore")
        last_modified_time_after = self._get_param("LastModifiedTimeAfter")
        status_equals = self._get_param("StatusEquals")
        endpoints, next_token = self.sagemaker_backend.list_endpoints(
            sort_by=sort_by,
            sort_order=sort_order,
            next_token=next_token,
            max_results=max_results,
            name_contains=name_contains,
            creation_time_before=creation_time_before,
            creation_time_after=creation_time_after,
            last_modified_time_before=last_modified_time_before,
            last_modified_time_after=last_modified_time_after,
            status_equals=status_equals,
        )
        endpoint_summaries = [endpoint.summary() for endpoint in endpoints]
        return ActionResult({"Endpoints": endpoint_summaries, "NextToken": next_token})

    def list_endpoint_configs(self) -> ActionResult:
        sort_by = self._get_param("SortBy")
        sort_order = self._get_param("SortOrder")
        next_token = self._get_param("NextToken")
        max_results = self._get_param("MaxResults")
        name_contains = self._get_param("NameContains")
        creation_time_before = self._get_param("CreationTimeBefore")
        creation_time_after = self._get_param("CreationTimeAfter")
        endpoint_configs, next_token = self.sagemaker_backend.list_endpoint_configs(
            sort_by=sort_by,
            sort_order=sort_order,
            next_token=next_token,
            max_results=max_results,
            name_contains=name_contains,
            creation_time_before=creation_time_before,
            creation_time_after=creation_time_after,
        )
        endpoint_summaries = [
            endpoint_config.summary() for endpoint_config in endpoint_configs
        ]
        return ActionResult(
            {"EndpointConfigs": endpoint_summaries, "NextToken": next_token}
        )

    def create_compilation_job(self) -> ActionResult:
        compilation_job_name = self._get_param("CompilationJobName")
        role_arn = self._get_param("RoleArn")
        model_package_version_arn = self._get_param("ModelPackageVersionArn")
        input_config = self._get_param("InputConfig")
        output_config = self._get_param("OutputConfig")
        vpc_config = self._get_param("VpcConfig")
        stopping_condition = self._get_param("StoppingCondition")
        tags = self._get_param("Tags")
        compilation_job_arn = self.sagemaker_backend.create_compilation_job(
            compilation_job_name=compilation_job_name,
            role_arn=role_arn,
            model_package_version_arn=model_package_version_arn,
            input_config=input_config,
            output_config=output_config,
            vpc_config=vpc_config,
            stopping_condition=stopping_condition,
            tags=tags,
        )
        return ActionResult({"CompilationJobArn": compilation_job_arn})

    def describe_compilation_job(self) -> ActionResult:
        compilation_job_name = self._get_param("CompilationJobName")
        compilation_job_description = self.sagemaker_backend.describe_compilation_job(
            compilation_job_name=compilation_job_name,
        )
        return ActionResult(compilation_job_description)

    def list_compilation_jobs(self) -> ActionResult:
        next_token = self._get_param("NextToken")
        max_results = self._get_param("MaxResults")
        creation_time_after = self._get_param("CreationTimeAfter")
        creation_time_before = self._get_param("CreationTimeBefore")
        last_modified_time_after = self._get_param("LastModifiedTimeAfter")
        last_modified_time_before = self._get_param("LastModifiedTimeBefore")
        name_contains = self._get_param("NameContains")
        status_equals = self._get_param("StatusEquals")
        sort_by = self._get_param("SortBy")
        sort_order = self._get_param("SortOrder")
        compilation_jobs, next_token = self.sagemaker_backend.list_compilation_jobs(
            next_token=next_token,
            max_results=max_results,
            creation_time_after=creation_time_after,
            creation_time_before=creation_time_before,
            last_modified_time_after=last_modified_time_after,
            last_modified_time_before=last_modified_time_before,
            name_contains=name_contains,
            status_equals=status_equals,
            sort_by=sort_by,
            sort_order=sort_order,
        )
        compilation_job_summaries = [x.summary() for x in compilation_jobs]
        return ActionResult(
            {
                "CompilationJobSummaries": compilation_job_summaries,
                "NextToken": next_token,
            }
        )

    def delete_compilation_job(self) -> ActionResult:
        compilation_job_name = self._get_param("CompilationJobName")
        self.sagemaker_backend.delete_compilation_job(
            compilation_job_name=compilation_job_name,
        )
        return EmptyResult()

    def create_domain(self) -> ActionResult:
        domain_name = self._get_param("DomainName")
        auth_mode = self._get_param("AuthMode")
        default_user_settings = self._get_param("DefaultUserSettings")
        domain_settings = self._get_param("DomainSettings")
        subnet_ids = self._get_param("SubnetIds")
        vpc_id = self._get_param("VpcId")
        tags = self._get_param("Tags")
        app_network_access_type = self._get_param("AppNetworkAccessType")
        home_efs_file_system_kms_key_id = self._get_param("HomeEfsFileSystemKmsKeyId")
        kms_key_id = self._get_param("KmsKeyId")
        app_security_group_management = self._get_param("AppSecurityGroupManagement")
        default_space_settings = self._get_param("DefaultSpaceSettings")
        resp = self.sagemaker_backend.create_domain(
            domain_name=domain_name,
            auth_mode=auth_mode,
            default_user_settings=default_user_settings,
            domain_settings=domain_settings,
            subnet_ids=subnet_ids,
            vpc_id=vpc_id,
            tags=tags,
            app_network_access_type=app_network_access_type,
            home_efs_file_system_kms_key_id=home_efs_file_system_kms_key_id,
            kms_key_id=kms_key_id,
            app_security_group_management=app_security_group_management,
            default_space_settings=default_space_settings,
        )
        return ActionResult(resp)

    def describe_domain(self) -> ActionResult:
        domain_id = self._get_param("DomainId")
        domain_description = self.sagemaker_backend.describe_domain(
            domain_id=domain_id,
        )
        return ActionResult(domain_description)

    def list_domains(self) -> ActionResult:
        next_token = self._get_param("NextToken")
        max_results = self._get_param("MaxResults")
        domains, next_token = self.sagemaker_backend.list_domains(
            next_token=next_token,
            max_results=max_results,
        )
        domain_summaries = [domain.summary() for domain in domains]
        return ActionResult({"Domains": domain_summaries, "NextToken": next_token})

    def delete_domain(self) -> ActionResult:
        domain_id = self._get_param("DomainId")
        retention_policy = self._get_param("RetentionPolicy")
        self.sagemaker_backend.delete_domain(
            domain_id=domain_id,
            retention_policy=retention_policy,
        )
        return EmptyResult()

    def create_model_explainability_job_definition(self) -> ActionResult:
        job_definition_name = self._get_param("JobDefinitionName")
        model_explainability_baseline_config = self._get_param(
            "ModelExplainabilityBaselineConfig"
        )
        model_explainability_app_specification = self._get_param(
            "ModelExplainabilityAppSpecification"
        )
        model_explainability_job_input = self._get_param("ModelExplainabilityJobInput")
        model_explainability_job_output_config = self._get_param(
            "ModelExplainabilityJobOutputConfig"
        )
        job_resources = self._get_param("JobResources")
        network_config = self._get_param("NetworkConfig")
        role_arn = self._get_param("RoleArn")
        stopping_condition = self._get_param("StoppingCondition")
        tags = self._get_param("Tags")
        job_definition_arn = self.sagemaker_backend.create_model_explainability_job_definition(
            job_definition_name=job_definition_name,
            model_explainability_baseline_config=model_explainability_baseline_config,
            model_explainability_app_specification=model_explainability_app_specification,
            model_explainability_job_input=model_explainability_job_input,
            model_explainability_job_output_config=model_explainability_job_output_config,
            job_resources=job_resources,
            network_config=network_config,
            role_arn=role_arn,
            stopping_condition=stopping_condition,
            tags=tags,
        )
        return ActionResult({"JobDefinitionArn": job_definition_arn})

    def describe_model_explainability_job_definition(self) -> ActionResult:
        job_definition_name = self._get_param("JobDefinitionName")
        description = (
            self.sagemaker_backend.describe_model_explainability_job_definition(
                job_definition_name=job_definition_name,
            )
        )
        return ActionResult(description)

    def list_model_explainability_job_definitions(self) -> ActionResult:
        endpoint_name = self._get_param("EndpointName")
        sort_by = self._get_param("SortBy")
        sort_order = self._get_param("SortOrder")
        next_token = self._get_param("NextToken")
        max_results = self._get_param("MaxResults")
        name_contains = self._get_param("NameContains")
        creation_time_before = self._get_param("CreationTimeBefore")
        creation_time_after = self._get_param("CreationTimeAfter")
        job_definitions, next_token = (
            self.sagemaker_backend.list_model_explainability_job_definitions(
                endpoint_name=endpoint_name,
                sort_by=sort_by,
                sort_order=sort_order,
                next_token=next_token,
                max_results=max_results,
                name_contains=name_contains,
                creation_time_before=creation_time_before,
                creation_time_after=creation_time_after,
            )
        )
        job_definition_summaries = [job.summary() for job in job_definitions]
        return ActionResult(
            {
                "JobDefinitionSummaries": job_definition_summaries,
                "NextToken": next_token,
            }
        )

    def delete_model_explainability_job_definition(self) -> ActionResult:
        job_definition_name = self._get_param("JobDefinitionName")
        self.sagemaker_backend.delete_model_explainability_job_definition(
            job_definition_name=job_definition_name,
        )
        return EmptyResult()

    def create_hyper_parameter_tuning_job(self) -> ActionResult:
        hyper_parameter_tuning_job_name = self._get_param("HyperParameterTuningJobName")
        hyper_parameter_tuning_job_config = self._get_param(
            "HyperParameterTuningJobConfig"
        )
        training_job_definition = self._get_param("TrainingJobDefinition")
        training_job_definitions = self._get_param("TrainingJobDefinitions")
        warm_start_config = self._get_param("WarmStartConfig")
        tags = self._get_param("Tags")
        autotune = self._get_param("Autotune")
        hyper_parameter_tuning_job_arn = (
            self.sagemaker_backend.create_hyper_parameter_tuning_job(
                hyper_parameter_tuning_job_name=hyper_parameter_tuning_job_name,
                hyper_parameter_tuning_job_config=hyper_parameter_tuning_job_config,
                training_job_definition=training_job_definition,
                training_job_definitions=training_job_definitions,
                warm_start_config=warm_start_config,
                tags=tags,
                autotune=autotune,
            )
        )
        return ActionResult(
            {"HyperParameterTuningJobArn": hyper_parameter_tuning_job_arn}
        )

    def describe_hyper_parameter_tuning_job(self) -> ActionResult:
        hyper_parameter_tuning_job_name = self._get_param("HyperParameterTuningJobName")
        hyper_parameter_tuning_job_description = (
            self.sagemaker_backend.describe_hyper_parameter_tuning_job(
                hyper_parameter_tuning_job_name=hyper_parameter_tuning_job_name,
            )
        )
        return ActionResult(hyper_parameter_tuning_job_description)

    def list_hyper_parameter_tuning_jobs(self) -> ActionResult:
        next_token = self._get_param("NextToken")
        max_results = self._get_param("MaxResults")
        sort_by = self._get_param("SortBy")
        sort_order = self._get_param("SortOrder")
        name_contains = self._get_param("NameContains")
        creation_time_after = self._get_param("CreationTimeAfter")
        creation_time_before = self._get_param("CreationTimeBefore")
        last_modified_time_after = self._get_param("LastModifiedTimeAfter")
        last_modified_time_before = self._get_param("LastModifiedTimeBefore")
        status_equals = self._get_param("StatusEquals")
        hyper_parameter_tuning_jobs, next_token = (
            self.sagemaker_backend.list_hyper_parameter_tuning_jobs(
                next_token=next_token,
                max_results=max_results,
                sort_by=sort_by,
                sort_order=sort_order,
                name_contains=name_contains,
                creation_time_after=creation_time_after,
                creation_time_before=creation_time_before,
                last_modified_time_after=last_modified_time_after,
                last_modified_time_before=last_modified_time_before,
                status_equals=status_equals,
            )
        )
        hyper_parameter_tuning_job_summaries = [
            job.summary() for job in hyper_parameter_tuning_jobs
        ]
        return ActionResult(
            {
                "HyperParameterTuningJobSummaries": hyper_parameter_tuning_job_summaries,
                "NextToken": next_token,
            }
        )

    def delete_hyper_parameter_tuning_job(self) -> ActionResult:
        hyper_parameter_tuning_job_name = self._get_param("HyperParameterTuningJobName")
        self.sagemaker_backend.delete_hyper_parameter_tuning_job(
            hyper_parameter_tuning_job_name=hyper_parameter_tuning_job_name,
        )
        return EmptyResult()

    def create_model_quality_job_definition(self) -> ActionResult:
        job_definition_name = self._get_param("JobDefinitionName")
        model_quality_baseline_config = self._get_param("ModelQualityBaselineConfig")
        model_quality_app_specification = self._get_param(
            "ModelQualityAppSpecification"
        )
        model_quality_job_input = self._get_param("ModelQualityJobInput")
        model_quality_job_output_config = self._get_param("ModelQualityJobOutputConfig")
        job_resources = self._get_param("JobResources")
        network_config = self._get_param("NetworkConfig")
        role_arn = self._get_param("RoleArn")
        stopping_condition = self._get_param("StoppingCondition")
        tags = self._get_param("Tags")
        job_definition_arn = self.sagemaker_backend.create_model_quality_job_definition(
            job_definition_name=job_definition_name,
            model_quality_baseline_config=model_quality_baseline_config,
            model_quality_app_specification=model_quality_app_specification,
            model_quality_job_input=model_quality_job_input,
            model_quality_job_output_config=model_quality_job_output_config,
            job_resources=job_resources,
            network_config=network_config,
            role_arn=role_arn,
            stopping_condition=stopping_condition,
            tags=tags,
        )
        return ActionResult({"JobDefinitionArn": job_definition_arn})

    def describe_model_quality_job_definition(self) -> ActionResult:
        job_definition_name = self._get_param("JobDefinitionName")
        description = self.sagemaker_backend.describe_model_quality_job_definition(
            job_definition_name=job_definition_name,
        )
        return ActionResult(description)

    def list_model_quality_job_definitions(self) -> ActionResult:
        endpoint_name = self._get_param("EndpointName")
        sort_by = self._get_param("SortBy")
        sort_order = self._get_param("SortOrder")
        next_token = self._get_param("NextToken")
        max_results = self._get_param("MaxResults")
        name_contains = self._get_param("NameContains")
        creation_time_before = self._get_param("CreationTimeBefore")
        creation_time_after = self._get_param("CreationTimeAfter")
        job_definitions, next_token = (
            self.sagemaker_backend.list_model_quality_job_definitions(
                endpoint_name=endpoint_name,
                sort_by=sort_by,
                sort_order=sort_order,
                next_token=next_token,
                max_results=max_results,
                name_contains=name_contains,
                creation_time_before=creation_time_before,
                creation_time_after=creation_time_after,
            )
        )
        job_definition_summaries = [x.summary() for x in job_definitions]
        return ActionResult(
            {
                "JobDefinitionSummaries": job_definition_summaries,
                "NextToken": next_token,
            }
        )

    def delete_model_quality_job_definition(self) -> ActionResult:
        job_definition_name = self._get_param("JobDefinitionName")
        self.sagemaker_backend.delete_model_quality_job_definition(
            job_definition_name=job_definition_name,
        )
        return EmptyResult()

    def create_model_card(self) -> ActionResult:
        model_card_name = self._get_param("ModelCardName")
        security_config = self._get_param("SecurityConfig")
        content = self._get_param("Content")
        model_card_status = self._get_param("ModelCardStatus")
        tags = self._get_param("Tags")
        model_card_arn = self.sagemaker_backend.create_model_card(
            model_card_name=model_card_name,
            security_config=security_config,
            content=content,
            model_card_status=model_card_status,
            tags=tags,
        )
        return ActionResult({"ModelCardArn": model_card_arn})

    def list_model_cards(self) -> ActionResult:
        creation_time_after = self._get_param("CreationTimeAfter")
        creation_time_before = self._get_param("CreationTimeBefore")
        max_results = self._get_param("MaxResults")
        name_contains = self._get_param("NameContains")
        model_card_status = self._get_param("ModelCardStatus")
        next_token = self._get_param("NextToken")
        sort_by = self._get_param("SortBy")
        sort_order = self._get_param("SortOrder")
        model_cards, next_token = self.sagemaker_backend.list_model_cards(
            creation_time_after=creation_time_after,
            creation_time_before=creation_time_before,
            max_results=max_results,
            name_contains=name_contains,
            model_card_status=model_card_status,
            next_token=next_token,
            sort_by=sort_by,
            sort_order=sort_order,
        )
        model_card_summaries = [model_card.summary() for model_card in model_cards]
        return ActionResult(
            {"ModelCardSummaries": model_card_summaries, "NextToken": next_token}
        )

    def list_model_card_versions(self) -> ActionResult:
        creation_time_after = self._get_param("CreationTimeAfter")
        creation_time_before = self._get_param("CreationTimeBefore")
        max_results = self._get_param("MaxResults")
        model_card_name = self._get_param("ModelCardName")
        model_card_status = self._get_param("ModelCardStatus")
        next_token = self._get_param("NextToken")
        sort_by = self._get_param("SortBy")
        sort_order = self._get_param("SortOrder")
        model_card_versions, next_token = (
            self.sagemaker_backend.list_model_card_versions(
                creation_time_after=creation_time_after,
                creation_time_before=creation_time_before,
                max_results=max_results,
                model_card_name=model_card_name,
                model_card_status=model_card_status,
                next_token=next_token,
                sort_by=sort_by,
                sort_order=sort_order,
            )
        )
        model_card_version_summaries = [
            mcv.version_summary() for mcv in model_card_versions
        ]
        return ActionResult(
            {
                "ModelCardVersionSummaryList": model_card_version_summaries,
                "NextToken": next_token,
            }
        )

    def update_model_card(self) -> ActionResult:
        model_card_name = self._get_param("ModelCardName")
        content = self._get_param("Content")
        model_card_status = self._get_param("ModelCardStatus")
        model_card_arn = self.sagemaker_backend.update_model_card(
            model_card_name=model_card_name,
            content=content,
            model_card_status=model_card_status,
        )
        return ActionResult({"ModelCardArn": model_card_arn})

    def describe_model_card(self) -> ActionResult:
        model_card_name = self._get_param("ModelCardName")
        model_card_version = self._get_param("ModelCardVersion")
        model_card_description = self.sagemaker_backend.describe_model_card(
            model_card_name=model_card_name,
            model_card_version=model_card_version,
        )
        return ActionResult(model_card_description)

    def delete_model_card(self) -> ActionResult:
        model_card_name = self._get_param("ModelCardName")
        self.sagemaker_backend.delete_model_card(
            model_card_name=model_card_name,
        )
        return EmptyResult()

    def create_action(self) -> ActionResult:
        actionname = self._get_param("ActionName")
        source = self._get_param("Source")
        actiontype = self._get_param("ActionType")
        description = self._get_param("Description")
        status = self._get_param("Status")
        properties = self._get_param("Properties")
        metadataproperties = self._get_param("MetadataProperties")
        tags = self._get_param("Tags")
        result = self.sagemaker_backend.create_action(actionname=actionname, source=source, actiontype=actiontype, description=description, status=status, properties=properties, metadataproperties=metadataproperties, tags=tags)
        return ActionResult(result)

    def describe_action(self) -> ActionResult:
        name = self._get_param("ActionName")
        result = self.sagemaker_backend.describe_action(name=name)
        return ActionResult(result)

    def list_actions(self) -> ActionResult:
        results = self.sagemaker_backend.list_actions()
        return ActionResult({"ActionSummaries": results})

    def update_action(self) -> ActionResult:
        actionname = self._get_param("ActionName")
        source = self._get_param("Source")
        actiontype = self._get_param("ActionType")
        description = self._get_param("Description")
        status = self._get_param("Status")
        properties = self._get_param("Properties")
        metadataproperties = self._get_param("MetadataProperties")
        result = self.sagemaker_backend.update_action(actionname=actionname, source=source, actiontype=actiontype, description=description, status=status, properties=properties, metadataproperties=metadataproperties)
        return ActionResult(result)

    def delete_action(self) -> ActionResult:
        name = self._get_param("ActionName")
        self.sagemaker_backend.delete_action(name=name)
        return ActionResult({})

    def create_algorithm(self) -> ActionResult:
        algorithmname = self._get_param("AlgorithmName")
        algorithmdescription = self._get_param("AlgorithmDescription")
        trainingspecification = self._get_param("TrainingSpecification")
        inferencespecification = self._get_param("InferenceSpecification")
        validationspecification = self._get_param("ValidationSpecification")
        certifyformarketplace = self._get_param("CertifyForMarketplace")
        tags = self._get_param("Tags")
        result = self.sagemaker_backend.create_algorithm(algorithmname=algorithmname, algorithmdescription=algorithmdescription, trainingspecification=trainingspecification, inferencespecification=inferencespecification, validationspecification=validationspecification, certifyformarketplace=certifyformarketplace, tags=tags)
        return ActionResult(result)

    def describe_algorithm(self) -> ActionResult:
        name = self._get_param("AlgorithmName")
        result = self.sagemaker_backend.describe_algorithm(name=name)
        return ActionResult(result)

    def list_algorithms(self) -> ActionResult:
        results = self.sagemaker_backend.list_algorithms()
        return ActionResult({"AlgorithmSummaryList": results})

    def delete_algorithm(self) -> ActionResult:
        name = self._get_param("AlgorithmName")
        self.sagemaker_backend.delete_algorithm(name=name)
        return ActionResult({})

    def create_app(self) -> ActionResult:
        appname = self._get_param("AppName")
        domainid = self._get_param("DomainId")
        userprofilename = self._get_param("UserProfileName")
        spacename = self._get_param("SpaceName")
        apptype = self._get_param("AppType")
        resourcespec = self._get_param("ResourceSpec")
        tags = self._get_param("Tags")
        result = self.sagemaker_backend.create_app(appname=appname, domainid=domainid, userprofilename=userprofilename, spacename=spacename, apptype=apptype, resourcespec=resourcespec, tags=tags)
        return ActionResult(result)

    def describe_app(self) -> ActionResult:
        domainid = self._get_param("DomainId")
        apptype = self._get_param("AppType")
        appname = self._get_param("AppName")
        result = self.sagemaker_backend.describe_app(domainid=domainid, apptype=apptype, appname=appname)
        return ActionResult(result)

    def list_apps(self) -> ActionResult:
        results = self.sagemaker_backend.list_apps()
        return ActionResult({"Apps": results})

    def delete_app(self) -> ActionResult:
        domainid = self._get_param("DomainId")
        apptype = self._get_param("AppType")
        appname = self._get_param("AppName")
        self.sagemaker_backend.delete_app(domainid=domainid, apptype=apptype, appname=appname)
        return ActionResult({})

    def create_app_image_config(self) -> ActionResult:
        appimageconfigname = self._get_param("AppImageConfigName")
        kernelgatewayimageconfig = self._get_param("KernelGatewayImageConfig")
        jupyterlabappimageconfig = self._get_param("JupyterLabAppImageConfig")
        codeeditorappimageconfig = self._get_param("CodeEditorAppImageConfig")
        tags = self._get_param("Tags")
        result = self.sagemaker_backend.create_app_image_config(appimageconfigname=appimageconfigname, kernelgatewayimageconfig=kernelgatewayimageconfig, jupyterlabappimageconfig=jupyterlabappimageconfig, codeeditorappimageconfig=codeeditorappimageconfig, tags=tags)
        return ActionResult(result)

    def describe_app_image_config(self) -> ActionResult:
        name = self._get_param("AppImageConfigName")
        result = self.sagemaker_backend.describe_app_image_config(name=name)
        return ActionResult(result)

    def list_app_image_configs(self) -> ActionResult:
        results = self.sagemaker_backend.list_app_image_configs()
        return ActionResult({"AppImageConfigs": results})

    def update_app_image_config(self) -> ActionResult:
        appimageconfigname = self._get_param("AppImageConfigName")
        kernelgatewayimageconfig = self._get_param("KernelGatewayImageConfig")
        jupyterlabappimageconfig = self._get_param("JupyterLabAppImageConfig")
        codeeditorappimageconfig = self._get_param("CodeEditorAppImageConfig")
        result = self.sagemaker_backend.update_app_image_config(appimageconfigname=appimageconfigname, kernelgatewayimageconfig=kernelgatewayimageconfig, jupyterlabappimageconfig=jupyterlabappimageconfig, codeeditorappimageconfig=codeeditorappimageconfig)
        return ActionResult(result)

    def delete_app_image_config(self) -> ActionResult:
        name = self._get_param("AppImageConfigName")
        self.sagemaker_backend.delete_app_image_config(name=name)
        return ActionResult({})

    def create_artifact(self) -> ActionResult:
        artifactname = self._get_param("ArtifactName")
        source = self._get_param("Source")
        artifacttype = self._get_param("ArtifactType")
        properties = self._get_param("Properties")
        metadataproperties = self._get_param("MetadataProperties")
        tags = self._get_param("Tags")
        result = self.sagemaker_backend.create_artifact(artifactname=artifactname, source=source, artifacttype=artifacttype, properties=properties, metadataproperties=metadataproperties, tags=tags)
        return ActionResult(result)

    def describe_artifact(self) -> ActionResult:
        name = self._get_param("ArtifactName")
        result = self.sagemaker_backend.describe_artifact(name=name)
        return ActionResult(result)

    def list_artifacts(self) -> ActionResult:
        results = self.sagemaker_backend.list_artifacts()
        return ActionResult({"ArtifactSummaries": results})

    def update_artifact(self) -> ActionResult:
        artifactname = self._get_param("ArtifactName")
        source = self._get_param("Source")
        artifacttype = self._get_param("ArtifactType")
        properties = self._get_param("Properties")
        metadataproperties = self._get_param("MetadataProperties")
        result = self.sagemaker_backend.update_artifact(artifactname=artifactname, source=source, artifacttype=artifacttype, properties=properties, metadataproperties=metadataproperties)
        return ActionResult(result)

    def delete_artifact(self) -> ActionResult:
        name = self._get_param("ArtifactName")
        self.sagemaker_backend.delete_artifact(name=name)
        return ActionResult({})

    def create_code_repository(self) -> ActionResult:
        coderepositoryname = self._get_param("CodeRepositoryName")
        gitconfig = self._get_param("GitConfig")
        tags = self._get_param("Tags")
        result = self.sagemaker_backend.create_code_repository(coderepositoryname=coderepositoryname, gitconfig=gitconfig, tags=tags)
        return ActionResult(result)

    def describe_code_repository(self) -> ActionResult:
        name = self._get_param("CodeRepositoryName")
        result = self.sagemaker_backend.describe_code_repository(name=name)
        return ActionResult(result)

    def list_code_repositories(self) -> ActionResult:
        results = self.sagemaker_backend.list_code_repositories()
        return ActionResult({"CodeRepositorySummaryList": results})

    def update_code_repository(self) -> ActionResult:
        coderepositoryname = self._get_param("CodeRepositoryName")
        gitconfig = self._get_param("GitConfig")
        result = self.sagemaker_backend.update_code_repository(coderepositoryname=coderepositoryname, gitconfig=gitconfig)
        return ActionResult(result)

    def delete_code_repository(self) -> ActionResult:
        name = self._get_param("CodeRepositoryName")
        self.sagemaker_backend.delete_code_repository(name=name)
        return ActionResult({})

    def create_context(self) -> ActionResult:
        contextname = self._get_param("ContextName")
        source = self._get_param("Source")
        contexttype = self._get_param("ContextType")
        description = self._get_param("Description")
        properties = self._get_param("Properties")
        tags = self._get_param("Tags")
        result = self.sagemaker_backend.create_context(contextname=contextname, source=source, contexttype=contexttype, description=description, properties=properties, tags=tags)
        return ActionResult(result)

    def describe_context(self) -> ActionResult:
        name = self._get_param("ContextName")
        result = self.sagemaker_backend.describe_context(name=name)
        return ActionResult(result)

    def list_contexts(self) -> ActionResult:
        results = self.sagemaker_backend.list_contexts()
        return ActionResult({"ContextSummaries": results})

    def update_context(self) -> ActionResult:
        contextname = self._get_param("ContextName")
        source = self._get_param("Source")
        contexttype = self._get_param("ContextType")
        description = self._get_param("Description")
        properties = self._get_param("Properties")
        result = self.sagemaker_backend.update_context(contextname=contextname, source=source, contexttype=contexttype, description=description, properties=properties)
        return ActionResult(result)

    def delete_context(self) -> ActionResult:
        name = self._get_param("ContextName")
        self.sagemaker_backend.delete_context(name=name)
        return ActionResult({})

    def create_device_fleet(self) -> ActionResult:
        devicefleetname = self._get_param("DeviceFleetName")
        rolearn = self._get_param("RoleArn")
        description = self._get_param("Description")
        outputconfig = self._get_param("OutputConfig")
        enableiotrolealias = self._get_param("EnableIotRoleAlias")
        tags = self._get_param("Tags")
        result = self.sagemaker_backend.create_device_fleet(devicefleetname=devicefleetname, rolearn=rolearn, description=description, outputconfig=outputconfig, enableiotrolealias=enableiotrolealias, tags=tags)
        return ActionResult(result)

    def describe_device_fleet(self) -> ActionResult:
        name = self._get_param("DeviceFleetName")
        result = self.sagemaker_backend.describe_device_fleet(name=name)
        return ActionResult(result)

    def list_device_fleets(self) -> ActionResult:
        results = self.sagemaker_backend.list_device_fleets()
        return ActionResult({"DeviceFleetSummaries": results})

    def update_device_fleet(self) -> ActionResult:
        devicefleetname = self._get_param("DeviceFleetName")
        rolearn = self._get_param("RoleArn")
        description = self._get_param("Description")
        outputconfig = self._get_param("OutputConfig")
        enableiotrolealias = self._get_param("EnableIotRoleAlias")
        result = self.sagemaker_backend.update_device_fleet(devicefleetname=devicefleetname, rolearn=rolearn, description=description, outputconfig=outputconfig, enableiotrolealias=enableiotrolealias)
        return ActionResult(result)

    def delete_device_fleet(self) -> ActionResult:
        name = self._get_param("DeviceFleetName")
        self.sagemaker_backend.delete_device_fleet(name=name)
        return ActionResult({})

    def create_edge_deployment_plan(self) -> ActionResult:
        edgedeploymentplanname = self._get_param("EdgeDeploymentPlanName")
        modelconfigs = self._get_param("ModelConfigs")
        devicefleetname = self._get_param("DeviceFleetName")
        stages = self._get_param("Stages")
        tags = self._get_param("Tags")
        result = self.sagemaker_backend.create_edge_deployment_plan(edgedeploymentplanname=edgedeploymentplanname, modelconfigs=modelconfigs, devicefleetname=devicefleetname, stages=stages, tags=tags)
        return ActionResult(result)

    def describe_edge_deployment_plan(self) -> ActionResult:
        name = self._get_param("EdgeDeploymentPlanName")
        result = self.sagemaker_backend.describe_edge_deployment_plan(name=name)
        return ActionResult(result)

    def list_edge_deployment_plans(self) -> ActionResult:
        results = self.sagemaker_backend.list_edge_deployment_plans()
        return ActionResult({"EdgeDeploymentPlanSummaries": results})

    def delete_edge_deployment_plan(self) -> ActionResult:
        name = self._get_param("EdgeDeploymentPlanName")
        self.sagemaker_backend.delete_edge_deployment_plan(name=name)
        return ActionResult({})

    def create_flow_definition(self) -> ActionResult:
        flowdefinitionname = self._get_param("FlowDefinitionName")
        humanloopconfig = self._get_param("HumanLoopConfig")
        humanlooprequestsource = self._get_param("HumanLoopRequestSource")
        humanloopactivationconfig = self._get_param("HumanLoopActivationConfig")
        outputconfig = self._get_param("OutputConfig")
        rolearn = self._get_param("RoleArn")
        tags = self._get_param("Tags")
        result = self.sagemaker_backend.create_flow_definition(flowdefinitionname=flowdefinitionname, humanloopconfig=humanloopconfig, humanlooprequestsource=humanlooprequestsource, humanloopactivationconfig=humanloopactivationconfig, outputconfig=outputconfig, rolearn=rolearn, tags=tags)
        return ActionResult(result)

    def describe_flow_definition(self) -> ActionResult:
        name = self._get_param("FlowDefinitionName")
        result = self.sagemaker_backend.describe_flow_definition(name=name)
        return ActionResult(result)

    def list_flow_definitions(self) -> ActionResult:
        results = self.sagemaker_backend.list_flow_definitions()
        return ActionResult({"FlowDefinitionSummaries": results})

    def delete_flow_definition(self) -> ActionResult:
        name = self._get_param("FlowDefinitionName")
        self.sagemaker_backend.delete_flow_definition(name=name)
        return ActionResult({})

    def create_hub(self) -> ActionResult:
        hubname = self._get_param("HubName")
        hubdescription = self._get_param("HubDescription")
        hubdisplayname = self._get_param("HubDisplayName")
        hubsearchkeywords = self._get_param("HubSearchKeywords")
        s3storageconfig = self._get_param("S3StorageConfig")
        tags = self._get_param("Tags")
        result = self.sagemaker_backend.create_hub(hubname=hubname, hubdescription=hubdescription, hubdisplayname=hubdisplayname, hubsearchkeywords=hubsearchkeywords, s3storageconfig=s3storageconfig, tags=tags)
        return ActionResult(result)

    def describe_hub(self) -> ActionResult:
        name = self._get_param("HubName")
        result = self.sagemaker_backend.describe_hub(name=name)
        return ActionResult(result)

    def list_hubs(self) -> ActionResult:
        results = self.sagemaker_backend.list_hubs()
        return ActionResult({"HubSummaries": results})

    def update_hub(self) -> ActionResult:
        hubname = self._get_param("HubName")
        hubdescription = self._get_param("HubDescription")
        hubdisplayname = self._get_param("HubDisplayName")
        hubsearchkeywords = self._get_param("HubSearchKeywords")
        s3storageconfig = self._get_param("S3StorageConfig")
        result = self.sagemaker_backend.update_hub(hubname=hubname, hubdescription=hubdescription, hubdisplayname=hubdisplayname, hubsearchkeywords=hubsearchkeywords, s3storageconfig=s3storageconfig)
        return ActionResult(result)

    def delete_hub(self) -> ActionResult:
        name = self._get_param("HubName")
        self.sagemaker_backend.delete_hub(name=name)
        return ActionResult({})

    def create_human_task_ui(self) -> ActionResult:
        humantaskuiname = self._get_param("HumanTaskUiName")
        uitemplate = self._get_param("UiTemplate")
        tags = self._get_param("Tags")
        result = self.sagemaker_backend.create_human_task_ui(humantaskuiname=humantaskuiname, uitemplate=uitemplate, tags=tags)
        return ActionResult(result)

    def describe_human_task_ui(self) -> ActionResult:
        name = self._get_param("HumanTaskUiName")
        result = self.sagemaker_backend.describe_human_task_ui(name=name)
        return ActionResult(result)

    def list_human_task_uis(self) -> ActionResult:
        results = self.sagemaker_backend.list_human_task_uis()
        return ActionResult({"HumanTaskUiSummaries": results})

    def delete_human_task_ui(self) -> ActionResult:
        name = self._get_param("HumanTaskUiName")
        self.sagemaker_backend.delete_human_task_ui(name=name)
        return ActionResult({})

    def create_image(self) -> ActionResult:
        imagename = self._get_param("ImageName")
        rolearn = self._get_param("RoleArn")
        displayname = self._get_param("DisplayName")
        description = self._get_param("Description")
        tags = self._get_param("Tags")
        result = self.sagemaker_backend.create_image(imagename=imagename, rolearn=rolearn, displayname=displayname, description=description, tags=tags)
        return ActionResult(result)

    def describe_image(self) -> ActionResult:
        name = self._get_param("ImageName")
        result = self.sagemaker_backend.describe_image(name=name)
        return ActionResult(result)

    def list_images(self) -> ActionResult:
        results = self.sagemaker_backend.list_images()
        return ActionResult({"Images": results})

    def update_image(self) -> ActionResult:
        imagename = self._get_param("ImageName")
        rolearn = self._get_param("RoleArn")
        displayname = self._get_param("DisplayName")
        description = self._get_param("Description")
        result = self.sagemaker_backend.update_image(imagename=imagename, rolearn=rolearn, displayname=displayname, description=description)
        return ActionResult(result)

    def delete_image(self) -> ActionResult:
        name = self._get_param("ImageName")
        self.sagemaker_backend.delete_image(name=name)
        return ActionResult({})

    def create_inference_component(self) -> ActionResult:
        inferencecomponentname = self._get_param("InferenceComponentName")
        endpointname = self._get_param("EndpointName")
        variantname = self._get_param("VariantName")
        specification = self._get_param("Specification")
        runtimeconfig = self._get_param("RuntimeConfig")
        tags = self._get_param("Tags")
        result = self.sagemaker_backend.create_inference_component(inferencecomponentname=inferencecomponentname, endpointname=endpointname, variantname=variantname, specification=specification, runtimeconfig=runtimeconfig, tags=tags)
        return ActionResult(result)

    def describe_inference_component(self) -> ActionResult:
        name = self._get_param("InferenceComponentName")
        result = self.sagemaker_backend.describe_inference_component(name=name)
        return ActionResult(result)

    def list_inference_components(self) -> ActionResult:
        results = self.sagemaker_backend.list_inference_components()
        return ActionResult({"InferenceComponents": results})

    def update_inference_component(self) -> ActionResult:
        inferencecomponentname = self._get_param("InferenceComponentName")
        endpointname = self._get_param("EndpointName")
        variantname = self._get_param("VariantName")
        specification = self._get_param("Specification")
        runtimeconfig = self._get_param("RuntimeConfig")
        result = self.sagemaker_backend.update_inference_component(inferencecomponentname=inferencecomponentname, endpointname=endpointname, variantname=variantname, specification=specification, runtimeconfig=runtimeconfig)
        return ActionResult(result)

    def delete_inference_component(self) -> ActionResult:
        name = self._get_param("InferenceComponentName")
        self.sagemaker_backend.delete_inference_component(name=name)
        return ActionResult({})

    def create_inference_experiment(self) -> ActionResult:
        name = self._get_param("Name")
        type = self._get_param("Type")
        endpointname = self._get_param("EndpointName")
        modelvariants = self._get_param("ModelVariants")
        description = self._get_param("Description")
        schedule = self._get_param("Schedule")
        datastorageconfig = self._get_param("DataStorageConfig")
        shadowmodeconfig = self._get_param("ShadowModeConfig")
        tags = self._get_param("Tags")
        result = self.sagemaker_backend.create_inference_experiment(name=name, type=type, endpointname=endpointname, modelvariants=modelvariants, description=description, schedule=schedule, datastorageconfig=datastorageconfig, shadowmodeconfig=shadowmodeconfig, tags=tags)
        return ActionResult(result)

    def describe_inference_experiment(self) -> ActionResult:
        name = self._get_param("Name")
        result = self.sagemaker_backend.describe_inference_experiment(name=name)
        return ActionResult(result)

    def list_inference_experiments(self) -> ActionResult:
        results = self.sagemaker_backend.list_inference_experiments()
        return ActionResult({"InferenceExperiments": results})

    def update_inference_experiment(self) -> ActionResult:
        name = self._get_param("Name")
        type = self._get_param("Type")
        endpointname = self._get_param("EndpointName")
        modelvariants = self._get_param("ModelVariants")
        description = self._get_param("Description")
        schedule = self._get_param("Schedule")
        datastorageconfig = self._get_param("DataStorageConfig")
        shadowmodeconfig = self._get_param("ShadowModeConfig")
        result = self.sagemaker_backend.update_inference_experiment(name=name, type=type, endpointname=endpointname, modelvariants=modelvariants, description=description, schedule=schedule, datastorageconfig=datastorageconfig, shadowmodeconfig=shadowmodeconfig)
        return ActionResult(result)

    def delete_inference_experiment(self) -> ActionResult:
        name = self._get_param("Name")
        self.sagemaker_backend.delete_inference_experiment(name=name)
        return ActionResult({})

    def create_labeling_job(self) -> ActionResult:
        labelingjobname = self._get_param("LabelingJobName")
        labelattributename = self._get_param("LabelAttributeName")
        inputconfig = self._get_param("InputConfig")
        outputconfig = self._get_param("OutputConfig")
        rolearn = self._get_param("RoleArn")
        labelcategoryconfigs3uri = self._get_param("LabelCategoryConfigS3Uri")
        humantaskconfig = self._get_param("HumanTaskConfig")
        tags = self._get_param("Tags")
        result = self.sagemaker_backend.create_labeling_job(labelingjobname=labelingjobname, labelattributename=labelattributename, inputconfig=inputconfig, outputconfig=outputconfig, rolearn=rolearn, labelcategoryconfigs3uri=labelcategoryconfigs3uri, humantaskconfig=humantaskconfig, tags=tags)
        return ActionResult(result)

    def describe_labeling_job(self) -> ActionResult:
        name = self._get_param("LabelingJobName")
        result = self.sagemaker_backend.describe_labeling_job(name=name)
        return ActionResult(result)

    def list_labeling_jobs(self) -> ActionResult:
        results = self.sagemaker_backend.list_labeling_jobs()
        return ActionResult({"LabelingJobSummaryList": results})

    def stop_labeling_job(self) -> ActionResult:
        name = self._get_param("LabelingJobName")
        self.sagemaker_backend.stop_labeling_job(name=name)
        return ActionResult({})

    def create_mlflow_app(self) -> ActionResult:
        name = self._get_param("Name")
        spacesettingsoverride = self._get_param("SpaceSettingsOverride")
        userprofilename = self._get_param("UserProfileName")
        domainid = self._get_param("DomainId")
        tags = self._get_param("Tags")
        result = self.sagemaker_backend.create_mlflow_app(name=name, spacesettingsoverride=spacesettingsoverride, userprofilename=userprofilename, domainid=domainid, tags=tags)
        return ActionResult(result)

    def describe_mlflow_app(self) -> ActionResult:
        name = self._get_param("Name")
        result = self.sagemaker_backend.describe_mlflow_app(name=name)
        return ActionResult(result)

    def list_mlflow_apps(self) -> ActionResult:
        results = self.sagemaker_backend.list_mlflow_apps()
        return ActionResult({"MlflowApps": results})

    def update_mlflow_app(self) -> ActionResult:
        name = self._get_param("Name")
        spacesettingsoverride = self._get_param("SpaceSettingsOverride")
        userprofilename = self._get_param("UserProfileName")
        domainid = self._get_param("DomainId")
        result = self.sagemaker_backend.update_mlflow_app(name=name, spacesettingsoverride=spacesettingsoverride, userprofilename=userprofilename, domainid=domainid)
        return ActionResult(result)

    def delete_mlflow_app(self) -> ActionResult:
        name = self._get_param("Name")
        self.sagemaker_backend.delete_mlflow_app(name=name)
        return ActionResult({})

    def create_mlflow_tracking_server(self) -> ActionResult:
        trackingservername = self._get_param("TrackingServerName")
        artifactstoreuri = self._get_param("ArtifactStoreUri")
        trackingserversize = self._get_param("TrackingServerSize")
        mlflowversion = self._get_param("MlflowVersion")
        rolearn = self._get_param("RoleArn")
        automaticmodelregistration = self._get_param("AutomaticModelRegistration")
        weeklymaintenancewindowstart = self._get_param("WeeklyMaintenanceWindowStart")
        tags = self._get_param("Tags")
        result = self.sagemaker_backend.create_mlflow_tracking_server(trackingservername=trackingservername, artifactstoreuri=artifactstoreuri, trackingserversize=trackingserversize, mlflowversion=mlflowversion, rolearn=rolearn, automaticmodelregistration=automaticmodelregistration, weeklymaintenancewindowstart=weeklymaintenancewindowstart, tags=tags)
        return ActionResult(result)

    def describe_mlflow_tracking_server(self) -> ActionResult:
        name = self._get_param("TrackingServerName")
        result = self.sagemaker_backend.describe_mlflow_tracking_server(name=name)
        return ActionResult(result)

    def list_mlflow_tracking_servers(self) -> ActionResult:
        results = self.sagemaker_backend.list_mlflow_tracking_servers()
        return ActionResult({"TrackingServerSummaries": results})

    def update_mlflow_tracking_server(self) -> ActionResult:
        trackingservername = self._get_param("TrackingServerName")
        artifactstoreuri = self._get_param("ArtifactStoreUri")
        trackingserversize = self._get_param("TrackingServerSize")
        mlflowversion = self._get_param("MlflowVersion")
        rolearn = self._get_param("RoleArn")
        automaticmodelregistration = self._get_param("AutomaticModelRegistration")
        weeklymaintenancewindowstart = self._get_param("WeeklyMaintenanceWindowStart")
        result = self.sagemaker_backend.update_mlflow_tracking_server(trackingservername=trackingservername, artifactstoreuri=artifactstoreuri, trackingserversize=trackingserversize, mlflowversion=mlflowversion, rolearn=rolearn, automaticmodelregistration=automaticmodelregistration, weeklymaintenancewindowstart=weeklymaintenancewindowstart)
        return ActionResult(result)

    def delete_mlflow_tracking_server(self) -> ActionResult:
        name = self._get_param("TrackingServerName")
        self.sagemaker_backend.delete_mlflow_tracking_server(name=name)
        return ActionResult({})

    def create_monitoring_schedule(self) -> ActionResult:
        monitoringschedulename = self._get_param("MonitoringScheduleName")
        monitoringscheduleconfig = self._get_param("MonitoringScheduleConfig")
        tags = self._get_param("Tags")
        result = self.sagemaker_backend.create_monitoring_schedule(monitoringschedulename=monitoringschedulename, monitoringscheduleconfig=monitoringscheduleconfig, tags=tags)
        return ActionResult(result)

    def describe_monitoring_schedule(self) -> ActionResult:
        name = self._get_param("MonitoringScheduleName")
        result = self.sagemaker_backend.describe_monitoring_schedule(name=name)
        return ActionResult(result)

    def list_monitoring_schedules(self) -> ActionResult:
        results = self.sagemaker_backend.list_monitoring_schedules()
        return ActionResult({"MonitoringScheduleSummaries": results})

    def update_monitoring_schedule(self) -> ActionResult:
        monitoringschedulename = self._get_param("MonitoringScheduleName")
        monitoringscheduleconfig = self._get_param("MonitoringScheduleConfig")
        result = self.sagemaker_backend.update_monitoring_schedule(monitoringschedulename=monitoringschedulename, monitoringscheduleconfig=monitoringscheduleconfig)
        return ActionResult(result)

    def delete_monitoring_schedule(self) -> ActionResult:
        name = self._get_param("MonitoringScheduleName")
        self.sagemaker_backend.delete_monitoring_schedule(name=name)
        return ActionResult({})

    def create_optimization_job(self) -> ActionResult:
        optimizationjobname = self._get_param("OptimizationJobName")
        rolearn = self._get_param("RoleArn")
        modelsource = self._get_param("ModelSource")
        deploymentinstancetype = self._get_param("DeploymentInstanceType")
        optimizationconfigs = self._get_param("OptimizationConfigs")
        outputconfig = self._get_param("OutputConfig")
        stoppingcondition = self._get_param("StoppingCondition")
        tags = self._get_param("Tags")
        result = self.sagemaker_backend.create_optimization_job(optimizationjobname=optimizationjobname, rolearn=rolearn, modelsource=modelsource, deploymentinstancetype=deploymentinstancetype, optimizationconfigs=optimizationconfigs, outputconfig=outputconfig, stoppingcondition=stoppingcondition, tags=tags)
        return ActionResult(result)

    def describe_optimization_job(self) -> ActionResult:
        name = self._get_param("OptimizationJobName")
        result = self.sagemaker_backend.describe_optimization_job(name=name)
        return ActionResult(result)

    def list_optimization_jobs(self) -> ActionResult:
        results = self.sagemaker_backend.list_optimization_jobs()
        return ActionResult({"OptimizationJobSummaries": results})

    def delete_optimization_job(self) -> ActionResult:
        name = self._get_param("OptimizationJobName")
        self.sagemaker_backend.delete_optimization_job(name=name)
        return ActionResult({})

    def stop_optimization_job(self) -> ActionResult:
        name = self._get_param("OptimizationJobName")
        self.sagemaker_backend.stop_optimization_job(name=name)
        return ActionResult({})

    def create_partner_app(self) -> ActionResult:
        name = self._get_param("Name")
        type = self._get_param("Type")
        executionrolearn = self._get_param("ExecutionRoleArn")
        maintenanceconfig = self._get_param("MaintenanceConfig")
        tier = self._get_param("Tier")
        applicationconfig = self._get_param("ApplicationConfig")
        authtype = self._get_param("AuthType")
        enableiamsessionbasedidentity = self._get_param("EnableIamSessionBasedIdentity")
        clienttoken = self._get_param("ClientToken")
        tags = self._get_param("Tags")
        result = self.sagemaker_backend.create_partner_app(name=name, type=type, executionrolearn=executionrolearn, maintenanceconfig=maintenanceconfig, tier=tier, applicationconfig=applicationconfig, authtype=authtype, enableiamsessionbasedidentity=enableiamsessionbasedidentity, clienttoken=clienttoken, tags=tags)
        return ActionResult(result)

    def describe_partner_app(self) -> ActionResult:
        name = self._get_param("Name")
        result = self.sagemaker_backend.describe_partner_app(name=name)
        return ActionResult(result)

    def list_partner_apps(self) -> ActionResult:
        results = self.sagemaker_backend.list_partner_apps()
        return ActionResult({"PartnerApps": results})

    def update_partner_app(self) -> ActionResult:
        name = self._get_param("Name")
        type = self._get_param("Type")
        executionrolearn = self._get_param("ExecutionRoleArn")
        maintenanceconfig = self._get_param("MaintenanceConfig")
        tier = self._get_param("Tier")
        applicationconfig = self._get_param("ApplicationConfig")
        authtype = self._get_param("AuthType")
        enableiamsessionbasedidentity = self._get_param("EnableIamSessionBasedIdentity")
        clienttoken = self._get_param("ClientToken")
        result = self.sagemaker_backend.update_partner_app(name=name, type=type, executionrolearn=executionrolearn, maintenanceconfig=maintenanceconfig, tier=tier, applicationconfig=applicationconfig, authtype=authtype, enableiamsessionbasedidentity=enableiamsessionbasedidentity, clienttoken=clienttoken)
        return ActionResult(result)

    def delete_partner_app(self) -> ActionResult:
        name = self._get_param("Name")
        self.sagemaker_backend.delete_partner_app(name=name)
        return ActionResult({})

    def create_project(self) -> ActionResult:
        projectname = self._get_param("ProjectName")
        projectdescription = self._get_param("ProjectDescription")
        servicecatalogprovisioningdetails = self._get_param("ServiceCatalogProvisioningDetails")
        tags = self._get_param("Tags")
        result = self.sagemaker_backend.create_project(projectname=projectname, projectdescription=projectdescription, servicecatalogprovisioningdetails=servicecatalogprovisioningdetails, tags=tags)
        return ActionResult(result)

    def describe_project(self) -> ActionResult:
        name = self._get_param("ProjectName")
        result = self.sagemaker_backend.describe_project(name=name)
        return ActionResult(result)

    def list_projects(self) -> ActionResult:
        results = self.sagemaker_backend.list_projects()
        return ActionResult({"ProjectSummaryList": results})

    def update_project(self) -> ActionResult:
        projectname = self._get_param("ProjectName")
        projectdescription = self._get_param("ProjectDescription")
        servicecatalogprovisioningdetails = self._get_param("ServiceCatalogProvisioningDetails")
        result = self.sagemaker_backend.update_project(projectname=projectname, projectdescription=projectdescription, servicecatalogprovisioningdetails=servicecatalogprovisioningdetails)
        return ActionResult(result)

    def delete_project(self) -> ActionResult:
        name = self._get_param("ProjectName")
        self.sagemaker_backend.delete_project(name=name)
        return ActionResult({})

    def create_space(self) -> ActionResult:
        spacename = self._get_param("SpaceName")
        domainid = self._get_param("DomainId")
        spacesettings = self._get_param("SpaceSettings")
        spacedisplayname = self._get_param("SpaceDisplayName")
        ownershipsettings = self._get_param("OwnershipSettings")
        spacesharingsettings = self._get_param("SpaceSharingSettings")
        tags = self._get_param("Tags")
        result = self.sagemaker_backend.create_space(spacename=spacename, domainid=domainid, spacesettings=spacesettings, spacedisplayname=spacedisplayname, ownershipsettings=ownershipsettings, spacesharingsettings=spacesharingsettings, tags=tags)
        return ActionResult(result)

    def describe_space(self) -> ActionResult:
        name = self._get_param("SpaceName")
        result = self.sagemaker_backend.describe_space(name=name)
        return ActionResult(result)

    def list_spaces(self) -> ActionResult:
        results = self.sagemaker_backend.list_spaces()
        return ActionResult({"Spaces": results})

    def update_space(self) -> ActionResult:
        spacename = self._get_param("SpaceName")
        domainid = self._get_param("DomainId")
        spacesettings = self._get_param("SpaceSettings")
        spacedisplayname = self._get_param("SpaceDisplayName")
        ownershipsettings = self._get_param("OwnershipSettings")
        spacesharingsettings = self._get_param("SpaceSharingSettings")
        result = self.sagemaker_backend.update_space(spacename=spacename, domainid=domainid, spacesettings=spacesettings, spacedisplayname=spacedisplayname, ownershipsettings=ownershipsettings, spacesharingsettings=spacesharingsettings)
        return ActionResult(result)

    def delete_space(self) -> ActionResult:
        name = self._get_param("SpaceName")
        self.sagemaker_backend.delete_space(name=name)
        return ActionResult({})

    def create_studio_lifecycle_config(self) -> ActionResult:
        studiolifecycleconfigname = self._get_param("StudioLifecycleConfigName")
        studiolifecycleconfigcontent = self._get_param("StudioLifecycleConfigContent")
        studiolifecycleconfigapptype = self._get_param("StudioLifecycleConfigAppType")
        tags = self._get_param("Tags")
        result = self.sagemaker_backend.create_studio_lifecycle_config(studiolifecycleconfigname=studiolifecycleconfigname, studiolifecycleconfigcontent=studiolifecycleconfigcontent, studiolifecycleconfigapptype=studiolifecycleconfigapptype, tags=tags)
        return ActionResult(result)

    def describe_studio_lifecycle_config(self) -> ActionResult:
        name = self._get_param("StudioLifecycleConfigName")
        result = self.sagemaker_backend.describe_studio_lifecycle_config(name=name)
        return ActionResult(result)

    def list_studio_lifecycle_configs(self) -> ActionResult:
        results = self.sagemaker_backend.list_studio_lifecycle_configs()
        return ActionResult({"StudioLifecycleConfigs": results})

    def delete_studio_lifecycle_config(self) -> ActionResult:
        name = self._get_param("StudioLifecycleConfigName")
        self.sagemaker_backend.delete_studio_lifecycle_config(name=name)
        return ActionResult({})

    def create_user_profile(self) -> ActionResult:
        userprofilename = self._get_param("UserProfileName")
        domainid = self._get_param("DomainId")
        singlesignonuseridentifier = self._get_param("SingleSignOnUserIdentifier")
        singlesignonuservalue = self._get_param("SingleSignOnUserValue")
        usersettings = self._get_param("UserSettings")
        tags = self._get_param("Tags")
        result = self.sagemaker_backend.create_user_profile(userprofilename=userprofilename, domainid=domainid, singlesignonuseridentifier=singlesignonuseridentifier, singlesignonuservalue=singlesignonuservalue, usersettings=usersettings, tags=tags)
        return ActionResult(result)

    def describe_user_profile(self) -> ActionResult:
        name = self._get_param("UserProfileName")
        result = self.sagemaker_backend.describe_user_profile(name=name)
        return ActionResult(result)

    def list_user_profiles(self) -> ActionResult:
        results = self.sagemaker_backend.list_user_profiles()
        return ActionResult({"UserProfiles": results})

    def update_user_profile(self) -> ActionResult:
        userprofilename = self._get_param("UserProfileName")
        domainid = self._get_param("DomainId")
        singlesignonuseridentifier = self._get_param("SingleSignOnUserIdentifier")
        singlesignonuservalue = self._get_param("SingleSignOnUserValue")
        usersettings = self._get_param("UserSettings")
        result = self.sagemaker_backend.update_user_profile(userprofilename=userprofilename, domainid=domainid, singlesignonuseridentifier=singlesignonuseridentifier, singlesignonuservalue=singlesignonuservalue, usersettings=usersettings)
        return ActionResult(result)

    def delete_user_profile(self) -> ActionResult:
        name = self._get_param("UserProfileName")
        self.sagemaker_backend.delete_user_profile(name=name)
        return ActionResult({})

    def create_workforce(self) -> ActionResult:
        workforcename = self._get_param("WorkforceName")
        cognitoconfig = self._get_param("CognitoConfig")
        oidcconfig = self._get_param("OidcConfig")
        sourceipconfig = self._get_param("SourceIpConfig")
        workforcevpcconfig = self._get_param("WorkforceVpcConfig")
        tags = self._get_param("Tags")
        result = self.sagemaker_backend.create_workforce(workforcename=workforcename, cognitoconfig=cognitoconfig, oidcconfig=oidcconfig, sourceipconfig=sourceipconfig, workforcevpcconfig=workforcevpcconfig, tags=tags)
        return ActionResult(result)

    def describe_workforce(self) -> ActionResult:
        name = self._get_param("WorkforceName")
        result = self.sagemaker_backend.describe_workforce(name=name)
        return ActionResult(result)

    def list_workforces(self) -> ActionResult:
        results = self.sagemaker_backend.list_workforces()
        return ActionResult({"Workforces": results})

    def update_workforce(self) -> ActionResult:
        workforcename = self._get_param("WorkforceName")
        cognitoconfig = self._get_param("CognitoConfig")
        oidcconfig = self._get_param("OidcConfig")
        sourceipconfig = self._get_param("SourceIpConfig")
        workforcevpcconfig = self._get_param("WorkforceVpcConfig")
        result = self.sagemaker_backend.update_workforce(workforcename=workforcename, cognitoconfig=cognitoconfig, oidcconfig=oidcconfig, sourceipconfig=sourceipconfig, workforcevpcconfig=workforcevpcconfig)
        return ActionResult(result)

    def delete_workforce(self) -> ActionResult:
        name = self._get_param("WorkforceName")
        self.sagemaker_backend.delete_workforce(name=name)
        return ActionResult({})

    def create_workteam(self) -> ActionResult:
        workteamname = self._get_param("WorkteamName")
        workforcename = self._get_param("WorkforceName")
        memberdefinitions = self._get_param("MemberDefinitions")
        description = self._get_param("Description")
        notificationconfiguration = self._get_param("NotificationConfiguration")
        tags = self._get_param("Tags")
        result = self.sagemaker_backend.create_workteam(workteamname=workteamname, workforcename=workforcename, memberdefinitions=memberdefinitions, description=description, notificationconfiguration=notificationconfiguration, tags=tags)
        return ActionResult(result)

    def describe_workteam(self) -> ActionResult:
        name = self._get_param("WorkteamName")
        result = self.sagemaker_backend.describe_workteam(name=name)
        return ActionResult(result)

    def list_workteams(self) -> ActionResult:
        results = self.sagemaker_backend.list_workteams()
        return ActionResult({"Workteams": results})

    def update_workteam(self) -> ActionResult:
        workteamname = self._get_param("WorkteamName")
        workforcename = self._get_param("WorkforceName")
        memberdefinitions = self._get_param("MemberDefinitions")
        description = self._get_param("Description")
        notificationconfiguration = self._get_param("NotificationConfiguration")
        result = self.sagemaker_backend.update_workteam(workteamname=workteamname, workforcename=workforcename, memberdefinitions=memberdefinitions, description=description, notificationconfiguration=notificationconfiguration)
        return ActionResult(result)

    def delete_workteam(self) -> ActionResult:
        name = self._get_param("WorkteamName")
        self.sagemaker_backend.delete_workteam(name=name)
        return ActionResult({})

    def add_association(self) -> ActionResult:
        self._get_param("SourceArn")
        self._get_param("DestinationArn")
        self._get_param("AssociationType")
        return ActionResult({'SourceArn': 'source_arn', 'DestinationArn': 'destination_arn'})

    def attach_cluster_node_volume(self) -> ActionResult:
        self._get_param("ClusterName")
        self._get_param("InstanceGroupName")
        self._get_param("InstanceId")
        return ActionResult({})

    def batch_add_cluster_nodes(self) -> ActionResult:
        self._get_param("ClusterName")
        self._get_param("NodeGroups")
        return ActionResult({})

    def batch_delete_cluster_nodes(self) -> ActionResult:
        self._get_param("ClusterName")
        self._get_param("NodeIds")
        return ActionResult({})

    def batch_describe_model_package(self) -> ActionResult:
        self._get_param("ModelPackageArnList")
        return ActionResult({'ModelPackageSummaries': {}, 'BatchDescribeModelPackageErrorMap': {}})

    def batch_reboot_cluster_nodes(self) -> ActionResult:
        self._get_param("ClusterName")
        self._get_param("NodeIds")
        return ActionResult({})

    def batch_replace_cluster_nodes(self) -> ActionResult:
        self._get_param("ClusterName")
        self._get_param("NodeIds")
        return ActionResult({})

    def create_auto_ml_job(self) -> ActionResult:
        self._get_param("AutoMLJobName")
        self._get_param("InputDataConfig")
        self._get_param("OutputDataConfig")
        self._get_param("RoleArn")
        return ActionResult({'AutoMLJobArn': '_arn'})

    def create_cluster_scheduler_config(self) -> ActionResult:
        self._get_param("Name")
        self._get_param("ClusterArn")
        self._get_param("SchedulerConfig")
        return ActionResult({'ClusterSchedulerConfigArn': '_arn', 'ClusterSchedulerConfigId': 'csc-00000000'})

    def create_compute_quota(self) -> ActionResult:
        self._get_param("Name")
        self._get_param("ClusterArn")
        self._get_param("ComputeQuotaConfig")
        return ActionResult({'ComputeQuotaArn': '_arn', 'ComputeQuotaId': 'cq-00000000'})

    def create_edge_deployment_stage(self) -> ActionResult:
        self._get_param("EdgeDeploymentPlanName")
        self._get_param("Stages")
        return ActionResult({})

    def create_edge_packaging_job(self) -> ActionResult:
        self._get_param("EdgePackagingJobName")
        self._get_param("CompilationJobName")
        self._get_param("ModelName")
        self._get_param("ModelVersion")
        self._get_param("RoleArn")
        self._get_param("OutputConfig")
        return ActionResult({})

    def create_hub_content_presigned_urls(self) -> ActionResult:
        self._get_param("HubName")
        self._get_param("HubContentName")
        self._get_param("HubContentType")
        self._get_param("HubContentVersion")
        return ActionResult({'AuthorizedUrl': 'https://example.com/presigned'})

    def create_hub_content_reference(self) -> ActionResult:
        self._get_param("HubName")
        self._get_param("SageMakerPublicHubContentArn")
        self._get_param("HubContentName")
        self._get_param("MinVersion")
        return ActionResult({'HubArn': '_arn', 'HubContentReferenceArn': '_arn'})

    def create_image_version(self) -> ActionResult:
        self._get_param("BaseImage")
        self._get_param("ImageName")
        self._get_param("ClientToken")
        return ActionResult({'ImageVersionArn': '_arn'})

    def create_inference_recommendations_job(self) -> ActionResult:
        self._get_param("JobName")
        self._get_param("JobType")
        self._get_param("RoleArn")
        self._get_param("InputConfig")
        return ActionResult({'JobArn': '_arn'})

    def create_model_card_export_job(self) -> ActionResult:
        self._get_param("ModelCardName")
        self._get_param("ModelCardVersion")
        self._get_param("ModelCardExportJobName")
        self._get_param("OutputConfig")
        return ActionResult({'ModelCardExportJobArn': '_arn'})

    def create_partner_app_presigned_url(self) -> ActionResult:
        self._get_param("Arn")
        self._get_param("ExpiresInSeconds")
        self._get_param("SessionExpirationDurationInSeconds")
        return ActionResult({'AuthorizedUrl': 'https://example.com/presigned'})

    def create_presigned_domain_url(self) -> ActionResult:
        self._get_param("DomainId")
        self._get_param("UserProfileName")
        self._get_param("SessionExpirationDurationInSeconds")
        self._get_param("ExpiresInSeconds")
        self._get_param("SpaceName")
        self._get_param("LandingUri")
        return ActionResult({'AuthorizedUrl': 'https://example.com/presigned'})

    def create_presigned_mlflow_app_url(self) -> ActionResult:
        self._get_param("SpaceName")
        self._get_param("DomainId")
        self._get_param("SessionExpirationDurationInSeconds")
        self._get_param("ExpiresInSeconds")
        return ActionResult({'AuthorizedUrl': 'https://example.com/presigned'})

    def create_presigned_mlflow_tracking_server_url(self) -> ActionResult:
        self._get_param("TrackingServerName")
        self._get_param("ExpiresInSeconds")
        self._get_param("SessionExpirationDurationInSeconds")
        return ActionResult({'AuthorizedUrl': 'https://example.com/presigned'})

    def create_presigned_notebook_instance_url(self) -> ActionResult:
        self._get_param("NotebookInstanceName")
        self._get_param("SessionExpirationDurationInSeconds")
        return ActionResult({'AuthorizedUrl': 'https://example.com/presigned'})

    def create_training_plan(self) -> ActionResult:
        self._get_param("TrainingPlanName")
        self._get_param("TrainingPlanOfferingId")
        return ActionResult({'TrainingPlanArn': '_arn'})

    def delete_association(self) -> ActionResult:
        self._get_param("SourceArn")
        self._get_param("DestinationArn")
        return ActionResult({'SourceArn': 'source_arn', 'DestinationArn': 'destination_arn'})

    def delete_cluster_scheduler_config(self) -> ActionResult:
        self._get_param("ClusterSchedulerConfigId")
        return ActionResult({})

    def delete_compute_quota(self) -> ActionResult:
        self._get_param("ComputeQuotaId")
        return ActionResult({})

    def delete_edge_deployment_stage(self) -> ActionResult:
        self._get_param("EdgeDeploymentPlanName")
        self._get_param("StageName")
        return ActionResult({})

    def delete_feature_group(self) -> ActionResult:
        self._get_param("FeatureGroupName")
        return ActionResult({})

    def delete_hub_content(self) -> ActionResult:
        self._get_param("HubName")
        self._get_param("HubContentType")
        self._get_param("HubContentName")
        self._get_param("HubContentVersion")
        return ActionResult({})

    def delete_hub_content_reference(self) -> ActionResult:
        self._get_param("HubName")
        self._get_param("HubContentType")
        self._get_param("HubContentName")
        return ActionResult({})

    def delete_image_version(self) -> ActionResult:
        self._get_param("ImageName")
        self._get_param("Version")
        self._get_param("Alias")
        return ActionResult({})

    def delete_model_package(self) -> ActionResult:
        self._get_param("ModelPackageName")
        return ActionResult({})

    def delete_model_package_group(self) -> ActionResult:
        self._get_param("ModelPackageGroupName")
        return ActionResult({})

    def delete_model_package_group_policy(self) -> ActionResult:
        self._get_param("ModelPackageGroupName")
        return ActionResult({})

    def delete_processing_job(self) -> ActionResult:
        self._get_param("ProcessingJobName")
        return ActionResult({})

    def delete_training_job(self) -> ActionResult:
        self._get_param("TrainingJobName")
        return ActionResult({})

    def deregister_devices(self) -> ActionResult:
        self._get_param("DeviceFleetName")
        self._get_param("DeviceNames")
        return ActionResult({})

    def describe_auto_ml_job(self) -> ActionResult:
        self._get_param("AutoMLJobName")
        return ActionResult({'AutoMLJobName': 'aml', 'AutoMLJobArn': '_arn', 'InputDataConfig': [], 'OutputDataConfig': {}, 'RoleArn': 'arn:aws:iam::role/r', 'AutoMLJobStatus': 'Completed', 'CreationTime': '2024-01-01T00:00:00Z'})

    def describe_cluster_event(self) -> ActionResult:
        self._get_param("ClusterName")
        self._get_param("EventId")
        return ActionResult({'Event': {'EventType': 'UpdateCompleted', 'Message': 'Cluster updated'}})

    def describe_cluster_scheduler_config(self) -> ActionResult:
        self._get_param("ClusterSchedulerConfigId")
        return ActionResult({'ClusterSchedulerConfigId': 'csc-00000000', 'Status': 'Completed'})

    def describe_compute_quota(self) -> ActionResult:
        self._get_param("ComputeQuotaId")
        return ActionResult({'ComputeQuotaId': 'cq-00000000', 'Status': 'Completed'})

    def describe_device(self) -> ActionResult:
        self._get_param("DeviceName")
        self._get_param("DeviceFleetName")
        return ActionResult({'DeviceName': 'd', 'DeviceFleetName': 'df', 'RegistrationTime': '2024-01-01T00:00:00Z'})

    def describe_edge_packaging_job(self) -> ActionResult:
        self._get_param("EdgePackagingJobName")
        return ActionResult({'EdgePackagingJobArn': '_arn', 'EdgePackagingJobName': 'epj', 'EdgePackagingJobStatus': 'Completed'})

    def describe_feature_metadata(self) -> ActionResult:
        self._get_param("FeatureGroupName")
        self._get_param("FeatureName")
        return ActionResult({'FeatureGroupArn': '_arn', 'FeatureGroupName': 'fg', 'FeatureName': 'f', 'FeatureType': 'String', 'Parameters': []})

    def describe_hub_content(self) -> ActionResult:
        self._get_param("HubName")
        self._get_param("HubContentType")
        self._get_param("HubContentName")
        self._get_param("HubContentVersion")
        return ActionResult({'HubContentName': 'hc', 'HubContentArn': '_arn', 'HubContentType': 'Model', 'HubContentStatus': 'Available', 'HubContentDocument': '{}'})

    def describe_image_version(self) -> ActionResult:
        self._get_param("ImageName")
        self._get_param("Version")
        self._get_param("Alias")
        return ActionResult({'ImageVersionArn': '_arn', 'ImageVersionStatus': 'CREATED', 'Version': 1})

    def describe_inference_recommendations_job(self) -> ActionResult:
        self._get_param("JobName")
        return ActionResult({'JobName': 'irj', 'JobArn': '_arn', 'JobType': 'Default', 'Status': 'COMPLETED', 'CreationTime': '2024-01-01T00:00:00Z', 'RoleArn': 'arn:aws:iam::role/r', 'InputConfig': {}})

    def describe_lineage_group(self) -> ActionResult:
        self._get_param("LineageGroupName")
        return ActionResult({'LineageGroupName': 'lg', 'LineageGroupArn': '_arn'})

    def describe_model_card_export_job(self) -> ActionResult:
        self._get_param("ModelCardExportJobArn")
        return ActionResult({'ModelCardExportJobName': 'mcej', 'ModelCardExportJobArn': '_arn', 'Status': 'Completed', 'ModelCardName': 'mc', 'ModelCardVersion': 1, 'OutputConfig': {}, 'CreatedAt': '2024-01-01T00:00:00Z'})

    def describe_reserved_capacity(self) -> ActionResult:
        self._get_param("ClusterName")
        self._get_param("ReservedCapacityId")
        return ActionResult({'ReservedCapacityArn': '_arn', 'Status': 'Active'})

    def describe_subscribed_workteam(self) -> ActionResult:
        self._get_param("WorkteamArn")
        return ActionResult({'SubscribedWorkteam': {'WorkteamArn': '_arn', 'ListingId': 'listing-00000000'}})

    def describe_training_plan(self) -> ActionResult:
        self._get_param("TrainingPlanName")
        return ActionResult({'TrainingPlanArn': '_arn', 'TrainingPlanName': 'tp', 'Status': 'Active'})

    def detach_cluster_node_volume(self) -> ActionResult:
        self._get_param("ClusterName")
        self._get_param("InstanceGroupName")
        self._get_param("InstanceId")
        return ActionResult({})

    def disable_sagemaker_servicecatalog_portfolio(self) -> ActionResult:
        return ActionResult({})

    def enable_sagemaker_servicecatalog_portfolio(self) -> ActionResult:
        return ActionResult({})

    def get_device_fleet_report(self) -> ActionResult:
        self._get_param("DeviceFleetName")
        return ActionResult({'DeviceFleetArn': '_arn', 'DeviceFleetName': 'df', 'OutputConfig': {}})

    def get_lineage_group_policy(self) -> ActionResult:
        self._get_param("LineageGroupName")
        return ActionResult({'LineageGroupArn': '_arn', 'ResourcePolicy': '{}'})

    def get_model_package_group_policy(self) -> ActionResult:
        self._get_param("ModelPackageGroupName")
        return ActionResult({'ResourcePolicy': '{}'})

    def get_sagemaker_servicecatalog_portfolio_status(self) -> ActionResult:
        return ActionResult({'Status': 'Enabled'})

    def get_scaling_configuration_recommendation(self) -> ActionResult:
        self._get_param("InferenceRecommendationsJobName")
        self._get_param("RecommendationId")
        self._get_param("EndpointName")
        self._get_param("TargetCpuUtilizationPerCore")
        self._get_param("ScalingPolicyObjective")
        return ActionResult({})

    def get_search_suggestions(self) -> ActionResult:
        self._get_param("Resource")
        self._get_param("SuggestionQuery")
        return ActionResult({'PropertyNameSuggestions': []})

    def import_hub_content(self) -> ActionResult:
        self._get_param("HubName")
        self._get_param("HubContentName")
        self._get_param("HubContentType")
        self._get_param("DocumentSchemaVersion")
        self._get_param("HubContentDisplayName")
        self._get_param("HubContentDescription")
        self._get_param("HubContentDocument")
        return ActionResult({'HubArn': '_arn', 'HubContentArn': '_arn'})

    def list_aliases(self) -> ActionResult:
        self._get_param("ImageName")
        return ActionResult({'SageMakerImageVersionAliases': []})

    def list_associations(self) -> ActionResult:
        return ActionResult({'AssociationSummaries': []})


    def list_candidates_for_auto_ml_job(self) -> ActionResult:
        self._get_param("AutoMLJobName")
        return ActionResult({'Candidates': []})

    def list_cluster_events(self) -> ActionResult:
        self._get_param("ClusterName")
        return ActionResult({'ClusterEvents': []})

    def list_cluster_scheduler_configs(self) -> ActionResult:
        return ActionResult({'ClusterSchedulerConfigSummaries': []})

    def list_compute_quotas(self) -> ActionResult:
        return ActionResult({'ComputeQuotaSummaries': []})

    def list_devices(self) -> ActionResult:
        return ActionResult({'DeviceSummaries': []})

    def list_edge_packaging_jobs(self) -> ActionResult:
        return ActionResult({'EdgePackagingJobSummaries': []})

    def list_feature_groups(self) -> ActionResult:
        return ActionResult({'FeatureGroupSummaries': []})

    def list_hub_content_versions(self) -> ActionResult:
        self._get_param("HubName")
        self._get_param("HubContentType")
        self._get_param("HubContentName")
        return ActionResult({'HubContentSummaries': []})

    def list_hub_contents(self) -> ActionResult:
        self._get_param("HubName")
        self._get_param("HubContentType")
        return ActionResult({'HubContentSummaries': []})

    def list_image_versions(self) -> ActionResult:
        self._get_param("ImageName")
        return ActionResult({'ImageVersions': []})

    def list_inference_recommendations_job_steps(self) -> ActionResult:
        self._get_param("JobName")
        return ActionResult({'Steps': []})

    def list_inference_recommendations_jobs(self) -> ActionResult:
        return ActionResult({'InferenceRecommendationsJobs': []})

    def list_labeling_jobs_for_workteam(self) -> ActionResult:
        self._get_param("WorkteamArn")
        return ActionResult({'LabelingJobSummaryList': []})

    def list_lineage_groups(self) -> ActionResult:
        return ActionResult({'LineageGroupSummaries': []})

    def list_model_card_export_jobs(self) -> ActionResult:
        self._get_param("ModelCardName")
        return ActionResult({'ModelCardExportJobSummaries': []})

    def list_model_metadata(self) -> ActionResult:
        return ActionResult({'ModelMetadataSummaries': []})

    def list_monitoring_alert_history(self) -> ActionResult:
        return ActionResult({'MonitoringAlertHistory': []})

    def list_monitoring_alerts(self) -> ActionResult:
        self._get_param("MonitoringScheduleName")
        return ActionResult({'MonitoringAlertSummaries': []})

    def list_monitoring_executions(self) -> ActionResult:
        return ActionResult({'MonitoringExecutionSummaries': []})

    def list_notebook_instance_lifecycle_configs(self) -> ActionResult:
        return ActionResult({'NotebookInstanceLifecycleConfigs': []})

    def list_pipeline_execution_steps(self) -> ActionResult:
        self._get_param("PipelineExecutionArn")
        return ActionResult({'PipelineExecutionSteps': []})

    def list_pipeline_versions(self) -> ActionResult:
        self._get_param("PipelineName")
        return ActionResult({'PipelineVersionSummaries': []})

    def list_resource_catalogs(self) -> ActionResult:
        return ActionResult({'ResourceCatalogs': []})

    def list_stage_devices(self) -> ActionResult:
        self._get_param("EdgeDeploymentPlanName")
        self._get_param("StageName")
        return ActionResult({'DeviceDeploymentSummaries': []})

    def list_subscribed_workteams(self) -> ActionResult:
        return ActionResult({'SubscribedWorkteams': []})

    def list_training_jobs_for_hyper_parameter_tuning_job(self) -> ActionResult:
        self._get_param("HyperParameterTuningJobName")
        return ActionResult({'TrainingJobSummaries': []})

    def list_training_plans(self) -> ActionResult:
        return ActionResult({'TrainingPlanSummaries': []})

    def list_ultra_servers_by_reserved_capacity(self) -> ActionResult:
        self._get_param("ClusterName")
        self._get_param("ReservedCapacityId")
        return ActionResult({'UltraServerSummaries': []})

    def put_model_package_group_policy(self) -> ActionResult:
        self._get_param("ModelPackageGroupName")
        self._get_param("ResourcePolicy")
        return ActionResult({'ModelPackageGroupArn': '_arn'})

    def query_lineage(self) -> ActionResult:
        self._get_param("StartArns")
        self._get_param("Direction")
        self._get_param("IncludeEdges")
        self._get_param("Filters")
        return ActionResult({'Vertices': [], 'Edges': []})

    def register_devices(self) -> ActionResult:
        self._get_param("DeviceFleetName")
        self._get_param("Devices")
        return ActionResult({})

    def render_ui_template(self) -> ActionResult:
        self._get_param("UiTemplate")
        self._get_param("Task")
        self._get_param("RoleArn")
        self._get_param("HumanTaskUiArn")
        return ActionResult({'RenderedContent': '<html></html>', 'Errors': []})

    def retry_pipeline_execution(self) -> ActionResult:
        self._get_param("PipelineExecutionArn")
        self._get_param("ClientRequestToken")
        self._get_param("ParallelismConfiguration")
        return ActionResult({'PipelineExecutionArn': '_arn'})

    def search_training_plan_offerings(self) -> ActionResult:
        self._get_param("InstanceType")
        self._get_param("InstanceCount")
        return ActionResult({'TrainingPlanOfferings': []})

    def send_pipeline_execution_step_failure(self) -> ActionResult:
        self._get_param("CallbackToken")
        self._get_param("FailureReason")
        self._get_param("ClientRequestToken")
        return ActionResult({'PipelineExecutionArn': '_arn'})

    def send_pipeline_execution_step_success(self) -> ActionResult:
        self._get_param("CallbackToken")
        self._get_param("OutputParameters")
        self._get_param("ClientRequestToken")
        return ActionResult({'PipelineExecutionArn': '_arn'})

    def start_edge_deployment_stage(self) -> ActionResult:
        self._get_param("EdgeDeploymentPlanName")
        self._get_param("StageName")
        return ActionResult({})

    def start_inference_experiment(self) -> ActionResult:
        self._get_param("Name")
        return ActionResult({'InferenceExperimentArn': '_arn'})

    def start_mlflow_tracking_server(self) -> ActionResult:
        self._get_param("TrackingServerName")
        return ActionResult({'TrackingServerArn': '_arn'})

    def start_monitoring_schedule(self) -> ActionResult:
        self._get_param("MonitoringScheduleName")
        return ActionResult({})

    def start_session(self) -> ActionResult:
        self._get_param("ResourceArn")
        return ActionResult({'StreamUrl': 'https://example.com/session'})

    def stop_compilation_job(self) -> ActionResult:
        self._get_param("CompilationJobName")
        return ActionResult({})

    def stop_edge_deployment_stage(self) -> ActionResult:
        self._get_param("EdgeDeploymentPlanName")
        self._get_param("StageName")
        return ActionResult({})

    def stop_edge_packaging_job(self) -> ActionResult:
        self._get_param("EdgePackagingJobName")
        return ActionResult({})

    def stop_hyper_parameter_tuning_job(self) -> ActionResult:
        self._get_param("HyperParameterTuningJobName")
        return ActionResult({})

    def stop_inference_experiment(self) -> ActionResult:
        self._get_param("Name")
        self._get_param("ModelVariantActions")
        self._get_param("DesiredModelVariants")
        self._get_param("DesiredState")
        self._get_param("Reason")
        return ActionResult({'InferenceExperimentArn': '_arn'})

    def stop_inference_recommendations_job(self) -> ActionResult:
        self._get_param("JobName")
        return ActionResult({})

    def stop_mlflow_tracking_server(self) -> ActionResult:
        self._get_param("TrackingServerName")
        return ActionResult({'TrackingServerArn': '_arn'})

    def stop_monitoring_schedule(self) -> ActionResult:
        self._get_param("MonitoringScheduleName")
        return ActionResult({})

    def stop_pipeline_execution(self) -> ActionResult:
        self._get_param("PipelineExecutionArn")
        self._get_param("ClientRequestToken")
        return ActionResult({'PipelineExecutionArn': '_arn'})

    def stop_processing_job(self) -> ActionResult:
        self._get_param("ProcessingJobName")
        return ActionResult({})

    def stop_training_job(self) -> ActionResult:
        self._get_param("TrainingJobName")
        return ActionResult({})

    def stop_transform_job(self) -> ActionResult:
        self._get_param("TransformJobName")
        return ActionResult({})

    def update_cluster(self) -> ActionResult:
        self._get_param("ClusterName")
        self._get_param("InstanceGroups")
        self._get_param("NodeRecovery")
        return ActionResult({'ClusterArn': '_arn'})

    def update_cluster_scheduler_config(self) -> ActionResult:
        self._get_param("ClusterSchedulerConfigId")
        self._get_param("SchedulerConfig")
        return ActionResult({'ClusterSchedulerConfigArn': '_arn', 'ClusterSchedulerConfigId': 'csc-00000000'})

    def update_cluster_software(self) -> ActionResult:
        self._get_param("ClusterName")
        return ActionResult({'ClusterArn': '_arn'})

    def update_compute_quota(self) -> ActionResult:
        self._get_param("ComputeQuotaId")
        self._get_param("ComputeQuotaConfig")
        return ActionResult({'ComputeQuotaArn': '_arn', 'ComputeQuotaId': 'cq-00000000'})

    def update_devices(self) -> ActionResult:
        self._get_param("DeviceFleetName")
        self._get_param("Devices")
        return ActionResult({})

    def update_domain(self) -> ActionResult:
        self._get_param("DomainId")
        self._get_param("DefaultUserSettings")
        self._get_param("DomainSettingsForUpdate")
        self._get_param("AppSecurityGroupManagement")
        self._get_param("DefaultSpaceSettings")
        self._get_param("SubnetIds")
        self._get_param("AppNetworkAccessType")
        self._get_param("TagPropagation")
        return ActionResult({'DomainArn': '_arn'})

    def update_endpoint(self) -> ActionResult:
        self._get_param("EndpointName")
        self._get_param("EndpointConfigName")
        self._get_param("RetainAllVariantProperties")
        self._get_param("ExcludeRetainedVariantProperties")
        self._get_param("DeploymentConfig")
        self._get_param("RetainDeploymentConfig")
        return ActionResult({'EndpointArn': '_arn'})

    def update_experiment(self) -> ActionResult:
        self._get_param("ExperimentName")
        self._get_param("DisplayName")
        self._get_param("Description")
        return ActionResult({'ExperimentArn': '_arn'})

    def update_feature_group(self) -> ActionResult:
        self._get_param("FeatureGroupName")
        self._get_param("FeatureAdditions")
        self._get_param("OnlineStoreConfig")
        self._get_param("ThroughputConfig")
        return ActionResult({'FeatureGroupArn': '_arn'})

    def update_feature_metadata(self) -> ActionResult:
        self._get_param("FeatureGroupName")
        self._get_param("FeatureName")
        self._get_param("Description")
        self._get_param("ParameterAdditions")
        self._get_param("ParameterRemovals")
        return ActionResult({})

    def update_hub_content(self) -> ActionResult:
        self._get_param("HubName")
        self._get_param("HubContentName")
        self._get_param("HubContentType")
        self._get_param("HubContentVersion")
        return ActionResult({'HubArn': '_arn', 'HubContentArn': '_arn'})

    def update_hub_content_reference(self) -> ActionResult:
        self._get_param("HubName")
        self._get_param("HubContentName")
        self._get_param("HubContentType")
        self._get_param("MinVersion")
        return ActionResult({'HubArn': '_arn', 'HubContentReferenceArn': '_arn'})

    def update_image_version(self) -> ActionResult:
        self._get_param("ImageName")
        self._get_param("Version")
        self._get_param("Alias")
        self._get_param("AliasesToAdd")
        self._get_param("AliasesToDelete")
        return ActionResult({'ImageVersionArn': '_arn'})

    def update_monitoring_alert(self) -> ActionResult:
        self._get_param("MonitoringScheduleName")
        self._get_param("MonitoringAlertName")
        self._get_param("DatapointsToAlert")
        self._get_param("EvaluationPeriod")
        return ActionResult({'MonitoringScheduleArn': '_arn'})

    def update_notebook_instance(self) -> ActionResult:
        self._get_param("NotebookInstanceName")
        self._get_param("InstanceType")
        self._get_param("RoleArn")
        self._get_param("LifecycleConfigName")
        self._get_param("DisassociateLifecycleConfig")
        self._get_param("VolumeSizeInGB")
        self._get_param("DefaultCodeRepository")
        self._get_param("AdditionalCodeRepositories")
        self._get_param("AcceleratorTypes")
        self._get_param("DisassociateAcceleratorTypes")
        self._get_param("DisassociateDefaultCodeRepository")
        self._get_param("DisassociateAdditionalCodeRepositories")
        self._get_param("RootAccess")
        self._get_param("InstanceMetadataServiceConfiguration")
        return ActionResult({})

    def update_notebook_instance_lifecycle_config(self) -> ActionResult:
        self._get_param("NotebookInstanceLifecycleConfigName")
        self._get_param("OnCreate")
        self._get_param("OnStart")
        return ActionResult({})

    def update_pipeline_execution(self) -> ActionResult:
        self._get_param("PipelineExecutionArn")
        self._get_param("PipelineExecutionDescription")
        self._get_param("PipelineExecutionDisplayName")
        self._get_param("ParallelismConfiguration")
        return ActionResult({'PipelineExecutionArn': '_arn'})

    def update_pipeline_version(self) -> ActionResult:
        self._get_param("PipelineName")
        self._get_param("PipelineVersion")
        return ActionResult({'PipelineArn': '_arn'})

    def update_training_job(self) -> ActionResult:
        self._get_param("TrainingJobName")
        self._get_param("ProfilerConfig")
        self._get_param("ProfilerRuleConfigurations")
        self._get_param("ResourceConfig")
        self._get_param("RemoteDebugConfig")
        return ActionResult({'TrainingJobArn': '_arn'})

    def update_trial(self) -> ActionResult:
        self._get_param("TrialName")
        self._get_param("DisplayName")
        return ActionResult({'TrialArn': '_arn'})

    def update_inference_component_runtime_config(self) -> ActionResult:
        self._get_param("InferenceComponentName")
        self._get_param("DesiredRuntimeConfig")
        return ActionResult({})

