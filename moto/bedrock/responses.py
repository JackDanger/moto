"""Handles incoming bedrock requests, invokes methods, returns responses."""

import json
from urllib.parse import unquote

from moto.core.responses import BaseResponse

from .models import BedrockBackend, bedrock_backends


class BedrockResponse(BaseResponse):
    """Handler for Bedrock requests and responses."""

    def __init__(self) -> None:
        super().__init__(service_name="bedrock")

    @property
    def bedrock_backend(self) -> BedrockBackend:
        """Return backend instance specific for this region."""
        return bedrock_backends[self.current_account][self.region]

    # -------------------------------------------------------------------
    # Model Customization Jobs (existing)
    # -------------------------------------------------------------------

    def create_model_customization_job(self) -> str:
        params = json.loads(self.body)
        job_name = params.get("jobName")
        custom_model_name = params.get("customModelName")
        role_arn = params.get("roleArn")
        client_request_token = params.get("clientRequestToken")
        base_model_identifier = params.get("baseModelIdentifier")
        customization_type = params.get("customizationType")
        custom_model_kms_key_id = params.get("customModelKmsKeyId")
        job_tags = params.get("jobTags")
        custom_model_tags = params.get("customModelTags")
        training_data_config = params.get("trainingDataConfig")
        validation_data_config = params.get("validationDataConfig")
        output_data_config = params.get("outputDataConfig")
        hyper_parameters = params.get("hyperParameters")
        vpc_config = params.get("vpcConfig")
        job_arn = self.bedrock_backend.create_model_customization_job(
            job_name=job_name,
            custom_model_name=custom_model_name,
            role_arn=role_arn,
            client_request_token=client_request_token,
            base_model_identifier=base_model_identifier,
            customization_type=customization_type,
            custom_model_kms_key_id=custom_model_kms_key_id,
            job_tags=job_tags,
            custom_model_tags=custom_model_tags,
            training_data_config=training_data_config,
            validation_data_config=validation_data_config,
            output_data_config=output_data_config,
            hyper_parameters=hyper_parameters,
            vpc_config=vpc_config,
        )
        return json.dumps({"jobArn": job_arn})

    def get_model_customization_job(self) -> str:
        job_identifier = self.path.split("/")[-1]
        model_customization_job = self.bedrock_backend.get_model_customization_job(
            job_identifier=job_identifier
        )
        return json.dumps(dict(model_customization_job.to_dict()))

    def get_model_invocation_logging_configuration(self) -> str:
        logging_config = (
            self.bedrock_backend.get_model_invocation_logging_configuration()
        )
        return json.dumps({"loggingConfig": logging_config})

    def put_model_invocation_logging_configuration(self) -> None:
        params = json.loads(self.body)
        logging_config = params.get("loggingConfig")
        self.bedrock_backend.put_model_invocation_logging_configuration(
            logging_config=logging_config
        )
        return

    def tag_resource(self) -> None:
        params = json.loads(self.body)
        resource_arn = params.get("resourceARN")
        tags = params.get("tags")
        self.bedrock_backend.tag_resource(
            resource_arn=resource_arn,
            tags=tags,
        )
        return

    def untag_resource(self) -> str:
        params = json.loads(self.body)
        resource_arn = params.get("resourceARN")
        tag_keys = params.get("tagKeys")
        self.bedrock_backend.untag_resource(
            resource_arn=resource_arn,
            tag_keys=tag_keys,
        )
        return json.dumps({})

    def list_tags_for_resource(self) -> str:
        params = json.loads(self.body)
        resource_arn = params.get("resourceARN")
        tags = self.bedrock_backend.list_tags_for_resource(
            resource_arn=resource_arn,
        )
        return json.dumps({"tags": tags})

    def get_custom_model(self) -> str:
        model_identifier = unquote(self.path.split("/")[-1])
        custom_model = self.bedrock_backend.get_custom_model(
            model_identifier=model_identifier
        )
        return json.dumps(dict(custom_model.to_dict()))

    def list_custom_models(self) -> str:
        params = self._get_params()
        creation_time_before = params.get("creationTimeBefore")
        creation_time_after = params.get("creationTimeAfter")
        name_contains = params.get("nameContains")
        base_model_arn_equals = params.get("baseModelArnEquals")
        foundation_model_arn_equals = params.get("foundationModelArnEquals")
        max_results = params.get("maxResults")
        next_token = params.get("nextToken")
        sort_by = params.get("sortBy")
        sort_order = params.get("sortOrder")

        max_results = int(max_results) if max_results else None
        model_summaries, next_token = self.bedrock_backend.list_custom_models(
            creation_time_before=creation_time_before,
            creation_time_after=creation_time_after,
            name_contains=name_contains,
            base_model_arn_equals=base_model_arn_equals,
            foundation_model_arn_equals=foundation_model_arn_equals,
            max_results=max_results,
            next_token=next_token,
            sort_by=sort_by,
            sort_order=sort_order,
        )
        summaries = [
            {
                "modelArn": model.model_arn,
                "modelName": model.model_name,
                "creationTime": model.creation_time,
                "baseModelArn": model.base_model_arn,
                "baseModelName": model.base_model_name,
                "jobArn": model.job_arn,
                "customizationType": model.customization_type,
            }
            for model in model_summaries
        ]
        return json.dumps({"nextToken": next_token, "modelSummaries": summaries})

    def list_model_customization_jobs(self) -> str:
        params = self._get_params()
        creation_time_after = params.get("creationTimeAfter")
        creation_time_before = params.get("creationTimeBefore")
        status_equals = params.get("statusEquals")
        name_contains = params.get("nameContains")
        max_results = self._get_int_param("maxResults")
        next_token = params.get("nextToken")
        sort_by = params.get("sortBy")
        sort_order = params.get("sortOrder")

        jobs, next_token = self.bedrock_backend.list_model_customization_jobs(
            creation_time_after=creation_time_after,
            creation_time_before=creation_time_before,
            status_equals=status_equals,
            name_contains=name_contains,
            max_results=max_results,
            next_token=next_token,
            sort_by=sort_by,
            sort_order=sort_order,
        )
        job_summaries = [
            {
                "jobArn": job.job_arn,
                "baseModelArn": job.base_model_arn,
                "jobName": job.job_name,
                "status": job.status,
                "lastModifiedTime": job.last_modified_time,
                "creationTime": job.creation_time,
                "endTime": job.end_time,
                "customModelArn": job.output_model_arn,
                "customModelName": job.custom_model_name,
                "customizationType": job.customization_type,
            }
            for job in jobs
        ]
        return json.dumps(
            {
                "nextToken": next_token,
                "modelCustomizationJobSummaries": job_summaries,
            }
        )

    def delete_custom_model(self) -> str:
        model_identifier = self.path.split("/")[-1]
        self.bedrock_backend.delete_custom_model(
            model_identifier=model_identifier,
        )
        return json.dumps({})

    def stop_model_customization_job(self) -> str:
        job_identifier = self.path.split("/")[-2]
        self.bedrock_backend.stop_model_customization_job(
            job_identifier=job_identifier,
        )
        return json.dumps({})

    def delete_model_invocation_logging_configuration(self) -> str:
        self.bedrock_backend.delete_model_invocation_logging_configuration()
        return json.dumps({})

    def create_custom_model(self) -> str:
        params = json.loads(self.body)
        model_name = params.get("modelName", "")
        model_source_config = params.get("modelSourceConfig")
        model_kms_key_id = params.get("modelKmsKeyId")
        result = self.bedrock_backend.create_custom_model(
            model_name=model_name,
            model_source_config=model_source_config,
            model_kms_key_id=model_kms_key_id,
        )
        return json.dumps(result)

    # -------------------------------------------------------------------
    # Guardrails
    # -------------------------------------------------------------------

    def create_guardrail(self) -> str:
        params = json.loads(self.body)
        result = self.bedrock_backend.create_guardrail(
            name=params.get("name", ""),
            blocked_input_messaging=params.get("blockedInputMessaging", ""),
            blocked_outputs_messaging=params.get("blockedOutputsMessaging", ""),
            description=params.get("description"),
            topic_policy_config=params.get("topicPolicyConfig"),
            content_policy_config=params.get("contentPolicyConfig"),
            word_policy_config=params.get("wordPolicyConfig"),
            sensitive_information_policy_config=params.get("sensitiveInformationPolicyConfig"),
            contextual_grounding_policy_config=params.get("contextualGroundingPolicyConfig"),
            automated_reasoning_policy_config=params.get("automatedReasoningPolicyConfig"),
            cross_region_config=params.get("crossRegionConfig"),
            kms_key_id=params.get("kmsKeyId"),
            tags=params.get("tags"),
        )
        return json.dumps(result)

    def get_guardrail(self) -> str:
        # Path: /guardrails/{guardrailIdentifier}
        guardrail_identifier = unquote(self.path.split("/")[-1])
        params = self._get_params()
        guardrail_version = params.get("guardrailVersion")
        result = self.bedrock_backend.get_guardrail(
            guardrail_identifier=guardrail_identifier,
            guardrail_version=guardrail_version,
        )
        return json.dumps(result)

    def update_guardrail(self) -> str:
        guardrail_identifier = unquote(self.path.split("/")[-1])
        params = json.loads(self.body)
        result = self.bedrock_backend.update_guardrail(
            guardrail_identifier=guardrail_identifier,
            name=params.get("name", ""),
            blocked_input_messaging=params.get("blockedInputMessaging", ""),
            blocked_outputs_messaging=params.get("blockedOutputsMessaging", ""),
            description=params.get("description"),
            topic_policy_config=params.get("topicPolicyConfig"),
            content_policy_config=params.get("contentPolicyConfig"),
            word_policy_config=params.get("wordPolicyConfig"),
            sensitive_information_policy_config=params.get("sensitiveInformationPolicyConfig"),
            contextual_grounding_policy_config=params.get("contextualGroundingPolicyConfig"),
            automated_reasoning_policy_config=params.get("automatedReasoningPolicyConfig"),
            cross_region_config=params.get("crossRegionConfig"),
            kms_key_id=params.get("kmsKeyId"),
        )
        return json.dumps(result)

    def delete_guardrail(self) -> str:
        guardrail_identifier = unquote(self.path.split("/")[-1])
        params = self._get_params()
        guardrail_version = params.get("guardrailVersion")
        self.bedrock_backend.delete_guardrail(
            guardrail_identifier=guardrail_identifier,
            guardrail_version=guardrail_version,
        )
        return json.dumps({})

    def list_guardrails(self) -> str:
        params = self._get_params()
        max_results = self._get_int_param("maxResults")
        next_token = params.get("nextToken")
        guardrail_identifier = params.get("guardrailIdentifier")
        guardrails, next_token = self.bedrock_backend.list_guardrails(
            guardrail_identifier=guardrail_identifier,
            max_results=max_results,
            next_token=next_token,
        )
        summaries = [g.summary() for g in guardrails]
        return json.dumps({"guardrails": summaries, "nextToken": next_token})

    def create_guardrail_version(self) -> str:
        guardrail_identifier = unquote(self.path.split("/")[-1])
        params = json.loads(self.body)
        result = self.bedrock_backend.create_guardrail_version(
            guardrail_identifier=guardrail_identifier,
            description=params.get("description"),
        )
        return json.dumps(result)

    # -------------------------------------------------------------------
    # Provisioned Model Throughput
    # -------------------------------------------------------------------

    def create_provisioned_model_throughput(self) -> str:
        params = json.loads(self.body)
        arn = self.bedrock_backend.create_provisioned_model_throughput(
            provisioned_model_name=params.get("provisionedModelName", ""),
            model_id=params.get("modelId", ""),
            model_units=params.get("modelUnits", 1),
            commitment_duration=params.get("commitmentDuration"),
            tags=params.get("tags"),
        )
        return json.dumps({"provisionedModelArn": arn})

    def get_provisioned_model_throughput(self) -> str:
        provisioned_model_id = unquote(self.path.split("/")[-1])
        result = self.bedrock_backend.get_provisioned_model_throughput(provisioned_model_id)
        return json.dumps(result)

    def update_provisioned_model_throughput(self) -> str:
        provisioned_model_id = unquote(self.path.split("/")[-1])
        params = json.loads(self.body)
        self.bedrock_backend.update_provisioned_model_throughput(
            provisioned_model_id=provisioned_model_id,
            desired_provisioned_model_name=params.get("desiredProvisionedModelName"),
            desired_model_id=params.get("desiredModelId"),
        )
        return json.dumps({})

    def delete_provisioned_model_throughput(self) -> str:
        provisioned_model_id = unquote(self.path.split("/")[-1])
        self.bedrock_backend.delete_provisioned_model_throughput(provisioned_model_id)
        return json.dumps({})

    def list_provisioned_model_throughputs(self) -> str:
        params = self._get_params()
        max_results = self._get_int_param("maxResults")
        next_token = params.get("nextToken")
        throughputs, next_token = self.bedrock_backend.list_provisioned_model_throughputs(
            creation_time_after=params.get("creationTimeAfter"),
            creation_time_before=params.get("creationTimeBefore"),
            status_equals=params.get("statusEquals"),
            model_arn_equals=params.get("modelArnEquals"),
            name_contains=params.get("nameContains"),
            sort_by=params.get("sortBy"),
            sort_order=params.get("sortOrder"),
            max_results=max_results,
            next_token=next_token,
        )
        summaries = [t.summary() for t in throughputs]
        return json.dumps({"nextToken": next_token, "provisionedModelSummaries": summaries})

    # -------------------------------------------------------------------
    # Evaluation Jobs
    # -------------------------------------------------------------------

    def create_evaluation_job(self) -> str:
        params = json.loads(self.body)
        job_arn = self.bedrock_backend.create_evaluation_job(
            job_name=params.get("jobName", ""),
            role_arn=params.get("roleArn", ""),
            evaluation_config=params.get("evaluationConfig", {}),
            inference_config=params.get("inferenceConfig", {}),
            output_data_config=params.get("outputDataConfig", {}),
            job_description=params.get("jobDescription"),
            customer_encryption_key_id=params.get("customerEncryptionKeyId"),
            application_type=params.get("applicationType"),
            job_tags=params.get("jobTags"),
        )
        return json.dumps({"jobArn": job_arn})

    def get_evaluation_job(self) -> str:
        job_identifier = unquote(self.path.split("/")[-1])
        result = self.bedrock_backend.get_evaluation_job(job_identifier)
        return json.dumps(result)

    def stop_evaluation_job(self) -> str:
        # Path: /evaluation-job/{jobIdentifier}/stop
        job_identifier = unquote(self.path.split("/")[-2])
        self.bedrock_backend.stop_evaluation_job(job_identifier)
        return json.dumps({})

    def list_evaluation_jobs(self) -> str:
        params = self._get_params()
        max_results = self._get_int_param("maxResults")
        next_token = params.get("nextToken")
        jobs, next_token = self.bedrock_backend.list_evaluation_jobs(
            creation_time_after=params.get("creationTimeAfter"),
            creation_time_before=params.get("creationTimeBefore"),
            status_equals=params.get("statusEquals"),
            application_type_equals=params.get("applicationTypeEquals"),
            name_contains=params.get("nameContains"),
            sort_by=params.get("sortBy"),
            sort_order=params.get("sortOrder"),
            max_results=max_results,
            next_token=next_token,
        )
        summaries = [j.summary() for j in jobs]
        return json.dumps({"nextToken": next_token, "jobSummaries": summaries})

    def batch_delete_evaluation_job(self) -> str:
        params = json.loads(self.body)
        result = self.bedrock_backend.batch_delete_evaluation_job(
            job_identifiers=params.get("jobIdentifiers", []),
        )
        return json.dumps(result)

    # -------------------------------------------------------------------
    # Inference Profiles
    # -------------------------------------------------------------------

    def create_inference_profile(self) -> str:
        params = json.loads(self.body)
        result = self.bedrock_backend.create_inference_profile(
            inference_profile_name=params.get("inferenceProfileName", ""),
            model_source=params.get("modelSource", {}),
            description=params.get("description"),
            tags=params.get("tags"),
        )
        return json.dumps(result)

    def get_inference_profile(self) -> str:
        identifier = unquote(self.path.split("/")[-1])
        result = self.bedrock_backend.get_inference_profile(identifier)
        return json.dumps(result)

    def delete_inference_profile(self) -> str:
        identifier = unquote(self.path.split("/")[-1])
        self.bedrock_backend.delete_inference_profile(identifier)
        return json.dumps({})

    def list_inference_profiles(self) -> str:
        params = self._get_params()
        max_results = self._get_int_param("maxResults")
        next_token = params.get("nextToken")
        type_equals = params.get("typeEquals")
        profiles, next_token = self.bedrock_backend.list_inference_profiles(
            type_equals=type_equals,
            max_results=max_results,
            next_token=next_token,
        )
        summaries = [p.summary() for p in profiles]
        return json.dumps({"inferenceProfileSummaries": summaries, "nextToken": next_token})

    # -------------------------------------------------------------------
    # Model Import Jobs
    # -------------------------------------------------------------------

    def create_model_import_job(self) -> str:
        params = json.loads(self.body)
        job_arn = self.bedrock_backend.create_model_import_job(
            job_name=params.get("jobName", ""),
            imported_model_name=params.get("importedModelName", ""),
            role_arn=params.get("roleArn", ""),
            model_data_source=params.get("modelDataSource", {}),
            vpc_config=params.get("vpcConfig"),
            imported_model_kms_key_id=params.get("importedModelKmsKeyId"),
            job_tags=params.get("jobTags"),
            imported_model_tags=params.get("importedModelTags"),
        )
        return json.dumps({"jobArn": job_arn})

    def get_model_import_job(self) -> str:
        job_identifier = unquote(self.path.split("/")[-1])
        result = self.bedrock_backend.get_model_import_job(job_identifier)
        return json.dumps(result)

    def list_model_import_jobs(self) -> str:
        params = self._get_params()
        max_results = self._get_int_param("maxResults")
        next_token = params.get("nextToken")
        jobs, next_token = self.bedrock_backend.list_model_import_jobs(
            creation_time_after=params.get("creationTimeAfter"),
            creation_time_before=params.get("creationTimeBefore"),
            status_equals=params.get("statusEquals"),
            name_contains=params.get("nameContains"),
            sort_by=params.get("sortBy"),
            sort_order=params.get("sortOrder"),
            max_results=max_results,
            next_token=next_token,
        )
        summaries = [j.summary() for j in jobs]
        return json.dumps({"nextToken": next_token, "modelImportJobSummaries": summaries})

    # -------------------------------------------------------------------
    # Imported Models
    # -------------------------------------------------------------------

    def get_imported_model(self) -> str:
        model_identifier = unquote(self.path.split("/")[-1])
        result = self.bedrock_backend.get_imported_model(model_identifier)
        return json.dumps(result)

    def delete_imported_model(self) -> str:
        model_identifier = unquote(self.path.split("/")[-1])
        self.bedrock_backend.delete_imported_model(model_identifier)
        return json.dumps({})

    def list_imported_models(self) -> str:
        params = self._get_params()
        max_results = self._get_int_param("maxResults")
        next_token = params.get("nextToken")
        models, next_token = self.bedrock_backend.list_imported_models(
            creation_time_before=params.get("creationTimeBefore"),
            creation_time_after=params.get("creationTimeAfter"),
            name_contains=params.get("nameContains"),
            sort_by=params.get("sortBy"),
            sort_order=params.get("sortOrder"),
            max_results=max_results,
            next_token=next_token,
        )
        summaries = [m.summary() for m in models]
        return json.dumps({"nextToken": next_token, "modelSummaries": summaries})

    # -------------------------------------------------------------------
    # Model Copy Jobs
    # -------------------------------------------------------------------

    def create_model_copy_job(self) -> str:
        params = json.loads(self.body)
        job_arn = self.bedrock_backend.create_model_copy_job(
            source_model_arn=params.get("sourceModelArn", ""),
            target_model_name=params.get("targetModelName", ""),
            model_kms_key_id=params.get("modelKmsKeyId"),
            target_model_tags=params.get("targetModelTags"),
        )
        return json.dumps({"jobArn": job_arn})

    def get_model_copy_job(self) -> str:
        job_arn = unquote(self.path.split("/")[-1])
        result = self.bedrock_backend.get_model_copy_job(job_arn)
        return json.dumps(result)

    def list_model_copy_jobs(self) -> str:
        params = self._get_params()
        max_results = self._get_int_param("maxResults")
        next_token = params.get("nextToken")
        jobs, next_token = self.bedrock_backend.list_model_copy_jobs(
            creation_time_after=params.get("creationTimeAfter"),
            creation_time_before=params.get("creationTimeBefore"),
            status_equals=params.get("statusEquals"),
            source_account_equals=params.get("sourceAccountEquals"),
            source_model_arn_equals=params.get("sourceModelArnEquals"),
            target_model_name_contains=params.get("targetModelNameContains"),
            sort_by=params.get("sortBy"),
            sort_order=params.get("sortOrder"),
            max_results=max_results,
            next_token=next_token,
        )
        summaries = [j.summary() for j in jobs]
        return json.dumps({"nextToken": next_token, "modelCopyJobSummaries": summaries})

    # -------------------------------------------------------------------
    # Model Invocation Jobs (batch inference)
    # -------------------------------------------------------------------

    def create_model_invocation_job(self) -> str:
        params = json.loads(self.body)
        job_arn = self.bedrock_backend.create_model_invocation_job(
            job_name=params.get("jobName", ""),
            role_arn=params.get("roleArn", ""),
            model_id=params.get("modelId", ""),
            input_data_config=params.get("inputDataConfig", {}),
            output_data_config=params.get("outputDataConfig", {}),
            client_request_token=params.get("clientRequestToken"),
            vpc_config=params.get("vpcConfig"),
            timeout_duration_in_hours=params.get("timeoutDurationInHours"),
            tags=params.get("tags"),
            model_invocation_type=params.get("modelInvocationType"),
        )
        return json.dumps({"jobArn": job_arn})

    def get_model_invocation_job(self) -> str:
        job_identifier = unquote(self.path.split("/")[-1])
        result = self.bedrock_backend.get_model_invocation_job(job_identifier)
        return json.dumps(result)

    def stop_model_invocation_job(self) -> str:
        # Path: /model-invocation-job/{jobIdentifier}/stop
        job_identifier = unquote(self.path.split("/")[-2])
        self.bedrock_backend.stop_model_invocation_job(job_identifier)
        return json.dumps({})

    def list_model_invocation_jobs(self) -> str:
        params = self._get_params()
        max_results = self._get_int_param("maxResults")
        next_token = params.get("nextToken")
        jobs, next_token = self.bedrock_backend.list_model_invocation_jobs(
            submit_time_after=params.get("submitTimeAfter"),
            submit_time_before=params.get("submitTimeBefore"),
            status_equals=params.get("statusEquals"),
            name_contains=params.get("nameContains"),
            sort_by=params.get("sortBy"),
            sort_order=params.get("sortOrder"),
            max_results=max_results,
            next_token=next_token,
        )
        summaries = [j.summary() for j in jobs]
        return json.dumps({"nextToken": next_token, "invocationJobSummaries": summaries})

    # -------------------------------------------------------------------
    # Foundation Models
    # -------------------------------------------------------------------

    def get_foundation_model(self) -> str:
        model_identifier = unquote(self.path.split("/")[-1])
        result = self.bedrock_backend.get_foundation_model(model_identifier)
        return json.dumps(result)

    def list_foundation_models(self) -> str:
        params = self._get_params()
        summaries = self.bedrock_backend.list_foundation_models(
            by_provider=params.get("byProvider"),
            by_customization_type=params.get("byCustomizationType"),
            by_output_modality=params.get("byOutputModality"),
            by_inference_type=params.get("byInferenceType"),
        )
        return json.dumps({"modelSummaries": summaries})

    # -------------------------------------------------------------------
    # Marketplace Model Endpoints
    # -------------------------------------------------------------------

    def create_marketplace_model_endpoint(self) -> str:
        params = json.loads(self.body)
        result = self.bedrock_backend.create_marketplace_model_endpoint(
            model_source_identifier=params.get("modelSourceIdentifier", ""),
            endpoint_config=params.get("endpointConfig", {}),
            endpoint_name=params.get("endpointName"),
            accept_eula=params.get("acceptEula", False),
            tags=params.get("tags"),
        )
        return json.dumps(result)

    def get_marketplace_model_endpoint(self) -> str:
        endpoint_arn = unquote(self.path.split("/")[-1])
        result = self.bedrock_backend.get_marketplace_model_endpoint(endpoint_arn)
        return json.dumps(result)

    def update_marketplace_model_endpoint(self) -> str:
        endpoint_arn = unquote(self.path.split("/")[-1])
        params = json.loads(self.body)
        result = self.bedrock_backend.update_marketplace_model_endpoint(
            endpoint_arn=endpoint_arn,
            endpoint_config=params.get("endpointConfig", {}),
        )
        return json.dumps(result)

    def delete_marketplace_model_endpoint(self) -> str:
        endpoint_arn = unquote(self.path.split("/")[-1])
        self.bedrock_backend.delete_marketplace_model_endpoint(endpoint_arn)
        return json.dumps({})

    def register_marketplace_model_endpoint(self) -> str:
        # Path: /marketplace-model/endpoints/{endpointIdentifier}/registration
        endpoint_identifier = unquote(self.path.split("/")[-2])
        params = json.loads(self.body)
        result = self.bedrock_backend.register_marketplace_model_endpoint(
            endpoint_identifier=endpoint_identifier,
            model_source_identifier=params.get("modelSourceIdentifier", ""),
        )
        return json.dumps(result)

    def deregister_marketplace_model_endpoint(self) -> str:
        # Path: /marketplace-model/endpoints/{endpointArn}/registration
        endpoint_arn = unquote(self.path.split("/")[-2])
        self.bedrock_backend.deregister_marketplace_model_endpoint(endpoint_arn)
        return json.dumps({})

    def list_marketplace_model_endpoints(self) -> str:
        params = self._get_params()
        max_results = self._get_int_param("maxResults")
        next_token = params.get("nextToken")
        endpoints, next_token = self.bedrock_backend.list_marketplace_model_endpoints(
            model_source_equals=params.get("modelSourceEquals"),
            max_results=max_results,
            next_token=next_token,
        )
        summaries = [e.summary() for e in endpoints]
        return json.dumps({"marketplaceModelEndpoints": summaries, "nextToken": next_token})

    # -------------------------------------------------------------------
    # Prompt Routers
    # -------------------------------------------------------------------

    def create_prompt_router(self) -> str:
        params = json.loads(self.body)
        arn = self.bedrock_backend.create_prompt_router(
            prompt_router_name=params.get("promptRouterName", ""),
            models=params.get("models", []),
            routing_criteria=params.get("routingCriteria", {}),
            fallback_model=params.get("fallbackModel", {}),
            description=params.get("description"),
            tags=params.get("tags"),
        )
        return json.dumps({"promptRouterArn": arn})

    def get_prompt_router(self) -> str:
        prompt_router_arn = unquote(self.path.split("/")[-1])
        result = self.bedrock_backend.get_prompt_router(prompt_router_arn)
        return json.dumps(result)

    def delete_prompt_router(self) -> str:
        prompt_router_arn = unquote(self.path.split("/")[-1])
        self.bedrock_backend.delete_prompt_router(prompt_router_arn)
        return json.dumps({})

    def list_prompt_routers(self) -> str:
        params = self._get_params()
        max_results = self._get_int_param("maxResults")
        next_token = params.get("nextToken")
        routers, next_token = self.bedrock_backend.list_prompt_routers(
            type_filter=params.get("type"),
            max_results=max_results,
            next_token=next_token,
        )
        summaries = [r.summary() for r in routers]
        return json.dumps({"promptRouterSummaries": summaries, "nextToken": next_token})

    # -------------------------------------------------------------------
    # Custom Model Deployments
    # -------------------------------------------------------------------

    def create_custom_model_deployment(self) -> str:
        params = json.loads(self.body)
        result = self.bedrock_backend.create_custom_model_deployment(
            model_deployment_name=params.get("modelDeploymentName", ""),
            model_id=params.get("modelId", ""),
        )
        return json.dumps(result)

    def get_custom_model_deployment(self) -> str:
        identifier = unquote(self.path.split("/")[-1])
        result = self.bedrock_backend.get_custom_model_deployment(identifier)
        return json.dumps(result)

    def update_custom_model_deployment(self) -> str:
        identifier = unquote(self.path.split("/")[-1])
        params = json.loads(self.body)
        result = self.bedrock_backend.update_custom_model_deployment(
            identifier=identifier,
            auto_scaling_config=params.get("autoScalingConfig"),
        )
        return json.dumps(result)

    def delete_custom_model_deployment(self) -> str:
        identifier = unquote(self.path.split("/")[-1])
        self.bedrock_backend.delete_custom_model_deployment(identifier)
        return json.dumps({})

    def list_custom_model_deployments(self) -> str:
        params = self._get_params()
        max_results = self._get_int_param("maxResults")
        next_token = params.get("nextToken")
        deployments, next_token = self.bedrock_backend.list_custom_model_deployments(
            max_results=max_results,
            next_token=next_token,
        )
        summaries = [d.summary() for d in deployments]
        return json.dumps({"customModelDeploymentSummaries": summaries, "nextToken": next_token})

    # -------------------------------------------------------------------
    # Foundation Model Agreements (stub)
    # -------------------------------------------------------------------

    def create_foundation_model_agreement(self) -> str:
        params = json.loads(self.body)
        result = self.bedrock_backend.create_foundation_model_agreement(
            model_id=params.get("modelId", ""),
            offer_token=params.get("offerToken"),
        )
        return json.dumps(result)

    def delete_foundation_model_agreement(self) -> str:
        params = json.loads(self.body)
        result = self.bedrock_backend.delete_foundation_model_agreement(
            model_id=params.get("modelId", ""),
        )
        return json.dumps(result)

    def list_foundation_model_agreement_offers(self) -> str:
        model_id = unquote(self.path.split("/")[-1])
        result = self.bedrock_backend.list_foundation_model_agreement_offers(model_id)
        return json.dumps(result)

    def get_foundation_model_availability(self) -> str:
        model_id = unquote(self.path.split("/")[-1])
        result = self.bedrock_backend.get_foundation_model_availability(model_id)
        return json.dumps(result)

    # -------------------------------------------------------------------
    # Enforced Guardrail Configuration (stub)
    # -------------------------------------------------------------------

    def put_enforced_guardrail_configuration(self) -> str:
        params = json.loads(self.body)
        result = self.bedrock_backend.put_enforced_guardrail_configuration(
            config_id=params.get("configId", "default"),
            guardrail_identifier=params.get("guardrailIdentifier", ""),
            guardrail_version=params.get("guardrailVersion"),
        )
        return json.dumps(result)

    def delete_enforced_guardrail_configuration(self) -> str:
        config_id = unquote(self.path.split("/")[-1])
        self.bedrock_backend.delete_enforced_guardrail_configuration(config_id)
        return json.dumps({})

    def list_enforced_guardrails_configuration(self) -> str:
        result = self.bedrock_backend.list_enforced_guardrails_configuration()
        return json.dumps({"configurations": result})

    # -------------------------------------------------------------------
    # Use Case for Model Access (stub)
    # -------------------------------------------------------------------

    def get_use_case_for_model_access(self) -> str:
        result = self.bedrock_backend.get_use_case_for_model_access()
        return json.dumps(result)

    def put_use_case_for_model_access(self) -> str:
        params = json.loads(self.body)
        result = self.bedrock_backend.put_use_case_for_model_access(
            use_cases=params.get("useCases"),
        )
        return json.dumps(result)

    # -------------------------------------------------------------------
    # Automated Reasoning Policies
    # -------------------------------------------------------------------

    def create_automated_reasoning_policy(self) -> str:
        params = json.loads(self.body)
        result = self.bedrock_backend.create_automated_reasoning_policy(
            name=params.get("name", ""),
            policy_type=params.get("policyType", ""),
            description=params.get("description"),
            rules=params.get("rules"),
            tags=params.get("tags"),
        )
        return json.dumps(result)

    def get_automated_reasoning_policy(self) -> str:
        policy_arn = unquote(self.path.split("/")[-1])
        result = self.bedrock_backend.get_automated_reasoning_policy(policy_arn)
        return json.dumps(result)

    def update_automated_reasoning_policy(self) -> str:
        policy_arn = unquote(self.path.split("/")[-1])
        params = json.loads(self.body)
        result = self.bedrock_backend.update_automated_reasoning_policy(
            policy_arn=policy_arn,
            name=params.get("name"),
            description=params.get("description"),
            rules=params.get("rules"),
        )
        return json.dumps(result)

    def delete_automated_reasoning_policy(self) -> str:
        policy_arn = unquote(self.path.split("/")[-1])
        self.bedrock_backend.delete_automated_reasoning_policy(policy_arn)
        return json.dumps({})

    def list_automated_reasoning_policies(self) -> str:
        params = self._get_params()
        max_results = self._get_int_param("maxResults")
        next_token = params.get("nextToken")
        policies, next_token = self.bedrock_backend.list_automated_reasoning_policies(
            max_results=max_results,
            next_token=next_token,
        )
        summaries = [p.summary() for p in policies]
        return json.dumps({"policies": summaries, "nextToken": next_token})

    def create_automated_reasoning_policy_version(self) -> str:
        # Path: /automated-reasoning-policies/{policyArn}/versions
        policy_arn = unquote(self.path.split("/")[-2])
        params = json.loads(self.body)
        result = self.bedrock_backend.create_automated_reasoning_policy_version(
            policy_arn=policy_arn,
            description=params.get("description"),
        )
        return json.dumps(result)

    def export_automated_reasoning_policy_version(self) -> str:
        # Path: /automated-reasoning-policies/{policyArn}/export
        policy_arn = unquote(self.path.split("/")[-2])
        result = self.bedrock_backend.export_automated_reasoning_policy_version(policy_arn)
        return json.dumps(result)

    def create_automated_reasoning_policy_test_case(self) -> str:
        # Path: /automated-reasoning-policies/{policyArn}/test-cases
        policy_arn = unquote(self.path.split("/")[-2])
        params = json.loads(self.body)
        result = self.bedrock_backend.create_automated_reasoning_policy_test_case(
            policy_arn=policy_arn,
            test_case_name=params.get("name"),
            description=params.get("description"),
            input_text=params.get("inputText"),
            expected_result=params.get("expectedResult"),
        )
        return json.dumps(result)

    def get_automated_reasoning_policy_test_case(self) -> str:
        # Path: /automated-reasoning-policies/{policyArn}/test-cases/{testCaseId}
        test_case_id = unquote(self.path.split("/")[-1])
        policy_arn = unquote(self.path.split("/")[-3])
        result = self.bedrock_backend.get_automated_reasoning_policy_test_case(
            policy_arn=policy_arn,
            test_case_id=test_case_id,
        )
        return json.dumps(result)

    def update_automated_reasoning_policy_test_case(self) -> str:
        test_case_id = unquote(self.path.split("/")[-1])
        policy_arn = unquote(self.path.split("/")[-3])
        params = json.loads(self.body)
        result = self.bedrock_backend.update_automated_reasoning_policy_test_case(
            policy_arn=policy_arn,
            test_case_id=test_case_id,
            test_case_name=params.get("name"),
            description=params.get("description"),
            input_text=params.get("inputText"),
            expected_result=params.get("expectedResult"),
        )
        return json.dumps(result)

    def delete_automated_reasoning_policy_test_case(self) -> str:
        test_case_id = unquote(self.path.split("/")[-1])
        policy_arn = unquote(self.path.split("/")[-3])
        self.bedrock_backend.delete_automated_reasoning_policy_test_case(
            policy_arn=policy_arn,
            test_case_id=test_case_id,
        )
        return json.dumps({})

    def list_automated_reasoning_policy_test_cases(self) -> str:
        # Path: /automated-reasoning-policies/{policyArn}/test-cases
        policy_arn = unquote(self.path.split("/")[-2])
        result = self.bedrock_backend.list_automated_reasoning_policy_test_cases(policy_arn)
        return json.dumps({"testCases": result})

    def start_automated_reasoning_policy_build_workflow(self) -> str:
        # Path: /automated-reasoning-policies/{policyArn}/build-workflows/{buildWorkflowType}/start
        build_workflow_type = unquote(self.path.split("/")[-2])
        policy_arn = unquote(self.path.split("/")[-4])
        result = self.bedrock_backend.start_automated_reasoning_policy_build_workflow(
            policy_arn=policy_arn,
            build_workflow_type=build_workflow_type,
        )
        return json.dumps(result)

    def get_automated_reasoning_policy_build_workflow(self) -> str:
        # Path: /automated-reasoning-policies/{policyArn}/build-workflows/{buildWorkflowId}
        build_workflow_id = unquote(self.path.split("/")[-1])
        policy_arn = unquote(self.path.split("/")[-3])
        result = self.bedrock_backend.get_automated_reasoning_policy_build_workflow(
            policy_arn=policy_arn,
            build_workflow_id=build_workflow_id,
        )
        return json.dumps(result)

    def cancel_automated_reasoning_policy_build_workflow(self) -> str:
        # Path: /automated-reasoning-policies/{policyArn}/build-workflows/{buildWorkflowId}/cancel
        build_workflow_id = unquote(self.path.split("/")[-2])
        policy_arn = unquote(self.path.split("/")[-4])
        self.bedrock_backend.cancel_automated_reasoning_policy_build_workflow(
            policy_arn=policy_arn,
            build_workflow_id=build_workflow_id,
        )
        return json.dumps({})

    def delete_automated_reasoning_policy_build_workflow(self) -> str:
        # Path: /automated-reasoning-policies/{policyArn}/build-workflows/{buildWorkflowId}
        build_workflow_id = unquote(self.path.split("/")[-1])
        policy_arn = unquote(self.path.split("/")[-3])
        self.bedrock_backend.delete_automated_reasoning_policy_build_workflow(
            policy_arn=policy_arn,
            build_workflow_id=build_workflow_id,
        )
        return json.dumps({})

    def list_automated_reasoning_policy_build_workflows(self) -> str:
        # Path: /automated-reasoning-policies/{policyArn}/build-workflows
        policy_arn = unquote(self.path.split("/")[-2])
        result = self.bedrock_backend.list_automated_reasoning_policy_build_workflows(policy_arn)
        return json.dumps({"buildWorkflows": result})

    def get_automated_reasoning_policy_build_workflow_result_assets(self) -> str:
        # Path: /automated-reasoning-policies/{policyArn}/build-workflows/{buildWorkflowId}/result-assets
        build_workflow_id = unquote(self.path.split("/")[-2])
        policy_arn = unquote(self.path.split("/")[-4])
        result = self.bedrock_backend.get_automated_reasoning_policy_build_workflow_result_assets(
            policy_arn=policy_arn,
            build_workflow_id=build_workflow_id,
        )
        return json.dumps(result)

    def get_automated_reasoning_policy_annotations(self) -> str:
        # Path: /automated-reasoning-policies/{policyArn}/build-workflows/{buildWorkflowId}/annotations
        build_workflow_id = unquote(self.path.split("/")[-2])
        policy_arn = unquote(self.path.split("/")[-4])
        result = self.bedrock_backend.get_automated_reasoning_policy_annotations(
            policy_arn=policy_arn,
            build_workflow_id=build_workflow_id,
        )
        return json.dumps(result)

    def update_automated_reasoning_policy_annotations(self) -> str:
        build_workflow_id = unquote(self.path.split("/")[-2])
        policy_arn = unquote(self.path.split("/")[-4])
        params = json.loads(self.body)
        result = self.bedrock_backend.update_automated_reasoning_policy_annotations(
            policy_arn=policy_arn,
            build_workflow_id=build_workflow_id,
            annotations=params.get("annotations"),
        )
        return json.dumps(result)

    def get_automated_reasoning_policy_next_scenario(self) -> str:
        # Path: /automated-reasoning-policies/{policyArn}/build-workflows/{buildWorkflowId}/scenarios
        build_workflow_id = unquote(self.path.split("/")[-2])
        policy_arn = unquote(self.path.split("/")[-4])
        result = self.bedrock_backend.get_automated_reasoning_policy_next_scenario(
            policy_arn=policy_arn,
            build_workflow_id=build_workflow_id,
        )
        return json.dumps(result)

    def get_automated_reasoning_policy_test_result(self) -> str:
        # Path: /automated-reasoning-policies/{policyArn}/build-workflows/{buildWorkflowId}/test-cases/{testCaseId}/test-results
        test_case_id = unquote(self.path.split("/")[-2])
        build_workflow_id = unquote(self.path.split("/")[-4])
        policy_arn = unquote(self.path.split("/")[-6])
        result = self.bedrock_backend.get_automated_reasoning_policy_test_result(
            policy_arn=policy_arn,
            build_workflow_id=build_workflow_id,
            test_case_id=test_case_id,
        )
        return json.dumps(result)

    def list_automated_reasoning_policy_test_results(self) -> str:
        # Path: /automated-reasoning-policies/{policyArn}/build-workflows/{buildWorkflowId}/test-results
        build_workflow_id = unquote(self.path.split("/")[-2])
        policy_arn = unquote(self.path.split("/")[-4])
        result = self.bedrock_backend.list_automated_reasoning_policy_test_results(
            policy_arn=policy_arn,
            build_workflow_id=build_workflow_id,
        )
        return json.dumps(result)

    def start_automated_reasoning_policy_test_workflow(self) -> str:
        # Path: /automated-reasoning-policies/{policyArn}/build-workflows/{buildWorkflowId}/test-workflows
        build_workflow_id = unquote(self.path.split("/")[-2])
        policy_arn = unquote(self.path.split("/")[-4])
        result = self.bedrock_backend.start_automated_reasoning_policy_test_workflow(
            policy_arn=policy_arn,
            build_workflow_id=build_workflow_id,
        )
        return json.dumps(result)
