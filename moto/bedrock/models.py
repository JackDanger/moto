"""BedrockBackend class with methods for supported APIs."""

import re
import uuid
from datetime import datetime
from typing import Any, Optional

from moto.bedrock.exceptions import (
    ResourceInUseException,
    ResourceNotFoundException,
    TooManyTagsException,
    ValidationException,
)
from moto.core.base_backend import BackendDict, BaseBackend
from moto.core.common_models import BaseModel
from moto.utilities.paginator import paginate
from moto.utilities.tagging_service import TaggingService
from moto.utilities.utils import get_partition


def _iso_now() -> str:
    return datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")


# ---------------------------------------------------------------------------
# Model classes
# ---------------------------------------------------------------------------

class ModelCustomizationJob(BaseModel):
    def __init__(
        self,
        job_name: str,
        custom_model_name: str,
        role_arn: str,
        base_model_identifier: str,
        training_data_config: dict[str, str],
        output_data_config: dict[str, str],
        hyper_parameters: dict[str, str],
        region_name: str,
        account_id: str,
        client_request_token: Optional[str],
        customization_type: Optional[str],
        custom_model_kms_key_id: Optional[str],
        job_tags: Optional[list[dict[str, str]]],
        custom_model_tags: Optional[list[dict[str, str]]],
        validation_data_config: Optional[dict[str, Any]],
        vpc_config: Optional[dict[str, Any]],
    ):
        self.job_name = job_name
        self.custom_model_name = custom_model_name
        self.role_arn = role_arn
        self.client_request_token = client_request_token
        self.base_model_identifier = base_model_identifier
        self.customization_type = customization_type
        self.custom_model_kms_key_id = custom_model_kms_key_id
        self.job_tags = job_tags
        self.custom_model_tags = custom_model_tags
        if "s3Uri" not in training_data_config or not re.match(
            r"s3://.*", training_data_config["s3Uri"]
        ):
            raise ValidationException(
                "Validation error detected: "
                f"Value '{training_data_config}' at 'training_data_config' failed to satisfy constraint: "
                "Member must satisfy regular expression pattern: "
                "s3://.*"
            )
        self.training_data_config = training_data_config
        if validation_data_config:
            if "validators" in validation_data_config:
                for validator in validation_data_config["validators"]:
                    if not re.match(r"s3://.*", validator["s3Uri"]):
                        raise ValidationException(
                            "Validation error detected: "
                            f"Value '{validator}' at 'validation_data_config' failed to satisfy constraint: "
                            "Member must satisfy regular expression pattern: "
                            "s3://.*"
                        )
        self.validation_data_config = validation_data_config
        if "s3Uri" not in output_data_config or not re.match(
            r"s3://.*", output_data_config["s3Uri"]
        ):
            raise ValidationException(
                "Validation error detected: "
                f"Value '{output_data_config}' at 'output_data_config' failed to satisfy constraint: "
                "Member must satisfy regular expression pattern: "
                "s3://.*"
            )
        self.output_data_config = output_data_config
        self.hyper_parameters = hyper_parameters
        self.vpc_config = vpc_config
        self.region_name = region_name
        self.account_id = account_id
        self.job_arn = f"arn:{get_partition(self.region_name)}:bedrock:{self.region_name}:{self.account_id}:model-customization-job/{self.job_name}"
        self.output_model_name = f"{self.custom_model_name}-{self.job_name}"
        self.output_model_arn = f"arn:{get_partition(self.region_name)}:bedrock:{self.region_name}:{self.account_id}:custom-model/{self.output_model_name}"
        self.status = "InProgress"
        self.failure_message = "Failure Message"
        self.creation_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.last_modified_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.end_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.base_model_arn = f"arn:{get_partition(self.region_name)}:bedrock:{self.region_name}::foundation-model/{self.base_model_identifier}"
        self.output_model_kms_key_arn = f"arn:{get_partition(self.region_name)}:kms:{self.region_name}:{self.account_id}:key/{self.output_model_name}-kms-key"
        self.training_metrics = {"trainingLoss": 0.0}  # hard coded
        self.validation_metrics = [{"validationLoss": 0.0}]  # hard coded

    def to_dict(self) -> dict[str, Any]:
        dct = {
            "baseModelArn": self.base_model_arn,
            "clientRequestToken": self.client_request_token,
            "creationTime": self.creation_time,
            "customizationType": self.customization_type,
            "endTime": self.end_time,
            "failureMessage": self.failure_message,
            "hyperParameters": self.hyper_parameters,
            "jobArn": self.job_arn,
            "jobName": self.job_name,
            "lastModifiedTime": self.last_modified_time,
            "outputDataConfig": self.output_data_config,
            "outputModelArn": self.output_model_arn,
            "outputModelKmsKeyArn": self.output_model_kms_key_arn,
            "outputModelName": self.output_model_name,
            "roleArn": self.role_arn,
            "status": self.status,
            "trainingDataConfig": self.training_data_config,
            "trainingMetrics": self.training_metrics,
            "validationDataConfig": self.validation_data_config,
            "validationMetrics": self.validation_metrics,
            "vpcConfig": self.vpc_config,
        }
        return {k: v for k, v in dct.items() if v}


class CustomModel(BaseModel):
    def __init__(
        self,
        model_name: str,
        job_name: str,
        job_arn: str,
        base_model_arn: str,
        hyper_parameters: dict[str, str],
        output_data_config: dict[str, str],
        training_data_config: dict[str, str],
        training_metrics: dict[str, float],
        base_model_name: str,
        region_name: str,
        account_id: str,
        customization_type: Optional[str],
        model_kms_key_arn: Optional[str],
        validation_data_config: Optional[dict[str, Any]],
        validation_metrics: Optional[list[dict[str, float]]],
    ):
        self.model_name = model_name
        self.job_name = job_name
        self.job_arn = job_arn
        self.base_model_arn = base_model_arn
        self.customization_type = customization_type
        self.model_kms_key_arn = model_kms_key_arn
        self.hyper_parameters = hyper_parameters
        self.training_data_config = training_data_config
        self.validation_data_config = validation_data_config
        self.output_data_config = output_data_config
        self.training_metrics = training_metrics
        self.validation_metrics = validation_metrics
        self.region_name = region_name
        self.account_id = account_id
        self.model_arn = f"arn:{get_partition(self.region_name)}:bedrock:{self.region_name}:{self.account_id}:custom-model/{self.model_name}"
        self.creation_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.base_model_name = base_model_name

    def to_dict(self) -> dict[str, Any]:
        dct = {
            "baseModelArn": self.base_model_arn,
            "creationTime": self.creation_time,
            "customizationType": self.customization_type,
            "hyperParameters": self.hyper_parameters,
            "jobArn": self.job_arn,
            "jobName": self.job_name,
            "modelArn": self.model_arn,
            "modelKmsKeyArn": self.model_kms_key_arn,
            "modelName": self.model_name,
            "outputDataConfig": self.output_data_config,
            "trainingDataConfig": self.training_data_config,
            "trainingMetrics": self.training_metrics,
            "validationDataConfig": self.validation_data_config,
            "validationMetrics": self.validation_metrics,
        }
        return {k: v for k, v in dct.items() if v}


class ModelInvocationLoggingConfiguration(BaseModel):
    def __init__(self, logging_config: dict[str, Any]) -> None:
        self.logging_config = logging_config


class Guardrail(BaseModel):
    def __init__(
        self,
        name: str,
        region_name: str,
        account_id: str,
        blocked_input_messaging: str,
        blocked_outputs_messaging: str,
        description: Optional[str] = None,
        topic_policy_config: Optional[dict[str, Any]] = None,
        content_policy_config: Optional[dict[str, Any]] = None,
        word_policy_config: Optional[dict[str, Any]] = None,
        sensitive_information_policy_config: Optional[dict[str, Any]] = None,
        contextual_grounding_policy_config: Optional[dict[str, Any]] = None,
        automated_reasoning_policy_config: Optional[dict[str, Any]] = None,
        cross_region_config: Optional[dict[str, Any]] = None,
        kms_key_id: Optional[str] = None,
    ):
        self.name = name
        self.description = description or ""
        self.guardrail_id = str(uuid.uuid4())[:12]
        self.region_name = region_name
        self.account_id = account_id
        partition = get_partition(region_name)
        self.guardrail_arn = f"arn:{partition}:bedrock:{region_name}:{account_id}:guardrail/{self.guardrail_id}"
        self.version = "DRAFT"
        self.next_version = 1
        self.status = "READY"
        self.topic_policy_config = topic_policy_config
        self.content_policy_config = content_policy_config
        self.word_policy_config = word_policy_config
        self.sensitive_information_policy_config = sensitive_information_policy_config
        self.contextual_grounding_policy_config = contextual_grounding_policy_config
        self.automated_reasoning_policy_config = automated_reasoning_policy_config
        self.cross_region_config = cross_region_config
        self.blocked_input_messaging = blocked_input_messaging
        self.blocked_outputs_messaging = blocked_outputs_messaging
        self.kms_key_id = kms_key_id
        now = _iso_now()
        self.created_at = now
        self.updated_at = now
        # Store versioned snapshots: version_number -> dict snapshot
        self.versions: dict[str, dict[str, Any]] = {}

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {
            "name": self.name,
            "description": self.description,
            "guardrailId": self.guardrail_id,
            "guardrailArn": self.guardrail_arn,
            "version": self.version,
            "status": self.status,
            "createdAt": self.created_at,
            "updatedAt": self.updated_at,
            "blockedInputMessaging": self.blocked_input_messaging,
            "blockedOutputsMessaging": self.blocked_outputs_messaging,
        }
        if self.topic_policy_config:
            d["topicPolicy"] = self.topic_policy_config
        if self.content_policy_config:
            d["contentPolicy"] = self.content_policy_config
        if self.word_policy_config:
            d["wordPolicy"] = self.word_policy_config
        if self.sensitive_information_policy_config:
            d["sensitiveInformationPolicy"] = self.sensitive_information_policy_config
        if self.contextual_grounding_policy_config:
            d["contextualGroundingPolicy"] = self.contextual_grounding_policy_config
        if self.automated_reasoning_policy_config:
            d["automatedReasoningPolicy"] = self.automated_reasoning_policy_config
        if self.cross_region_config:
            d["crossRegionDetails"] = self.cross_region_config
        if self.kms_key_id:
            d["kmsKeyArn"] = self.kms_key_id
        return d

    def summary(self) -> dict[str, Any]:
        return {
            "id": self.guardrail_id,
            "arn": self.guardrail_arn,
            "status": self.status,
            "name": self.name,
            "description": self.description,
            "version": self.version,
            "createdAt": self.created_at,
            "updatedAt": self.updated_at,
        }


class ProvisionedModelThroughput(BaseModel):
    def __init__(
        self,
        provisioned_model_name: str,
        model_id: str,
        model_units: int,
        region_name: str,
        account_id: str,
        commitment_duration: Optional[str] = None,
    ):
        self.provisioned_model_name = provisioned_model_name
        self.model_id = model_id
        self.model_units = model_units
        self.desired_model_units = model_units
        self.commitment_duration = commitment_duration
        self.region_name = region_name
        self.account_id = account_id
        self.provisioned_model_id = str(uuid.uuid4())[:12]
        partition = get_partition(region_name)
        self.provisioned_model_arn = f"arn:{partition}:bedrock:{region_name}:{account_id}:provisioned-model/{self.provisioned_model_id}"
        self.model_arn = f"arn:{partition}:bedrock:{region_name}::foundation-model/{model_id}"
        self.desired_model_arn = self.model_arn
        self.foundation_model_arn = self.model_arn
        self.status = "InService"
        now = _iso_now()
        self.creation_time = now
        self.last_modified_time = now
        self.failure_message = ""
        self.commitment_expiration_time = ""

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {
            "modelUnits": self.model_units,
            "desiredModelUnits": self.desired_model_units,
            "provisionedModelName": self.provisioned_model_name,
            "provisionedModelArn": self.provisioned_model_arn,
            "modelArn": self.model_arn,
            "desiredModelArn": self.desired_model_arn,
            "foundationModelArn": self.foundation_model_arn,
            "status": self.status,
            "creationTime": self.creation_time,
            "lastModifiedTime": self.last_modified_time,
        }
        if self.commitment_duration:
            d["commitmentDuration"] = self.commitment_duration
        if self.failure_message:
            d["failureMessage"] = self.failure_message
        if self.commitment_expiration_time:
            d["commitmentExpirationTime"] = self.commitment_expiration_time
        return d

    def summary(self) -> dict[str, Any]:
        d: dict[str, Any] = {
            "provisionedModelName": self.provisioned_model_name,
            "provisionedModelArn": self.provisioned_model_arn,
            "modelArn": self.model_arn,
            "desiredModelArn": self.desired_model_arn,
            "foundationModelArn": self.foundation_model_arn,
            "desiredModelUnits": self.desired_model_units,
            "modelUnits": self.model_units,
            "status": self.status,
            "creationTime": self.creation_time,
            "lastModifiedTime": self.last_modified_time,
        }
        if self.commitment_duration:
            d["commitmentDuration"] = self.commitment_duration
        return d


class EvaluationJob(BaseModel):
    def __init__(
        self,
        job_name: str,
        role_arn: str,
        evaluation_config: dict[str, Any],
        inference_config: dict[str, Any],
        output_data_config: dict[str, Any],
        region_name: str,
        account_id: str,
        job_description: Optional[str] = None,
        customer_encryption_key_id: Optional[str] = None,
        application_type: Optional[str] = None,
    ):
        self.job_name = job_name
        self.role_arn = role_arn
        self.evaluation_config = evaluation_config
        self.inference_config = inference_config
        self.output_data_config = output_data_config
        self.job_description = job_description or ""
        self.customer_encryption_key_id = customer_encryption_key_id
        self.application_type = application_type or "ModelEvaluation"
        self.region_name = region_name
        self.account_id = account_id
        self.job_id = str(uuid.uuid4())[:12]
        partition = get_partition(region_name)
        self.job_arn = f"arn:{partition}:bedrock:{region_name}:{account_id}:evaluation-job/{self.job_id}"
        self.status = "InProgress"
        # Determine job type from evaluation_config
        if "automated" in self.evaluation_config:
            self.job_type = "Automated"
        else:
            self.job_type = "Human"
        now = _iso_now()
        self.creation_time = now
        self.last_modified_time = now
        self.failure_messages: list[str] = []

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {
            "jobName": self.job_name,
            "status": self.status,
            "jobArn": self.job_arn,
            "roleArn": self.role_arn,
            "jobType": self.job_type,
            "evaluationConfig": self.evaluation_config,
            "inferenceConfig": self.inference_config,
            "outputDataConfig": self.output_data_config,
            "creationTime": self.creation_time,
            "lastModifiedTime": self.last_modified_time,
        }
        if self.job_description:
            d["jobDescription"] = self.job_description
        if self.customer_encryption_key_id:
            d["customerEncryptionKeyId"] = self.customer_encryption_key_id
        if self.application_type:
            d["applicationType"] = self.application_type
        if self.failure_messages:
            d["failureMessages"] = self.failure_messages
        return d

    def summary(self) -> dict[str, Any]:
        d: dict[str, Any] = {
            "jobArn": self.job_arn,
            "jobName": self.job_name,
            "status": self.status,
            "creationTime": self.creation_time,
            "jobType": self.job_type,
        }
        if self.application_type:
            d["applicationType"] = self.application_type
        return d


class InferenceProfile(BaseModel):
    def __init__(
        self,
        inference_profile_name: str,
        model_source: dict[str, Any],
        region_name: str,
        account_id: str,
        description: Optional[str] = None,
    ):
        self.inference_profile_name = inference_profile_name
        self.description = description or ""
        self.model_source = model_source
        self.region_name = region_name
        self.account_id = account_id
        self.inference_profile_id = str(uuid.uuid4())[:12]
        partition = get_partition(region_name)
        self.inference_profile_arn = f"arn:{partition}:bedrock:{region_name}:{account_id}:inference-profile/{self.inference_profile_id}"
        self.status = "ACTIVE"
        self.type = "APPLICATION"
        now = _iso_now()
        self.created_at = now
        self.updated_at = now
        # Build models list from model_source
        self.models: list[dict[str, str]] = []
        if "copyFrom" in model_source:
            copy_from = model_source["copyFrom"]
            if isinstance(copy_from, str):
                self.models.append({"modelArn": copy_from})
            elif isinstance(copy_from, list):
                for m in copy_from:
                    self.models.append({"modelArn": m})

    def to_dict(self) -> dict[str, Any]:
        return {
            "inferenceProfileName": self.inference_profile_name,
            "description": self.description,
            "createdAt": self.created_at,
            "updatedAt": self.updated_at,
            "inferenceProfileArn": self.inference_profile_arn,
            "models": self.models,
            "inferenceProfileId": self.inference_profile_id,
            "status": self.status,
            "type": self.type,
        }

    def summary(self) -> dict[str, Any]:
        return {
            "inferenceProfileName": self.inference_profile_name,
            "inferenceProfileArn": self.inference_profile_arn,
            "inferenceProfileId": self.inference_profile_id,
            "description": self.description,
            "status": self.status,
            "type": self.type,
            "createdAt": self.created_at,
            "updatedAt": self.updated_at,
            "models": self.models,
        }


class ModelImportJob(BaseModel):
    def __init__(
        self,
        job_name: str,
        imported_model_name: str,
        role_arn: str,
        model_data_source: dict[str, Any],
        region_name: str,
        account_id: str,
        vpc_config: Optional[dict[str, Any]] = None,
        imported_model_kms_key_id: Optional[str] = None,
    ):
        self.job_name = job_name
        self.imported_model_name = imported_model_name
        self.role_arn = role_arn
        self.model_data_source = model_data_source
        self.vpc_config = vpc_config
        self.imported_model_kms_key_id = imported_model_kms_key_id
        self.region_name = region_name
        self.account_id = account_id
        self.job_id = str(uuid.uuid4())[:12]
        partition = get_partition(region_name)
        self.job_arn = f"arn:{partition}:bedrock:{region_name}:{account_id}:model-import-job/{self.job_id}"
        self.imported_model_arn = f"arn:{partition}:bedrock:{region_name}:{account_id}:imported-model/{self.imported_model_name}"
        self.status = "Completed"
        now = _iso_now()
        self.creation_time = now
        self.last_modified_time = now
        self.end_time = now
        self.failure_message = ""
        self.imported_model_kms_key_arn = ""
        if imported_model_kms_key_id:
            self.imported_model_kms_key_arn = f"arn:{partition}:kms:{region_name}:{account_id}:key/{imported_model_kms_key_id}"

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {
            "jobArn": self.job_arn,
            "jobName": self.job_name,
            "importedModelName": self.imported_model_name,
            "importedModelArn": self.imported_model_arn,
            "roleArn": self.role_arn,
            "modelDataSource": self.model_data_source,
            "status": self.status,
            "creationTime": self.creation_time,
            "lastModifiedTime": self.last_modified_time,
            "endTime": self.end_time,
        }
        if self.failure_message:
            d["failureMessage"] = self.failure_message
        if self.vpc_config:
            d["vpcConfig"] = self.vpc_config
        if self.imported_model_kms_key_arn:
            d["importedModelKmsKeyArn"] = self.imported_model_kms_key_arn
        return d

    def summary(self) -> dict[str, Any]:
        return {
            "jobArn": self.job_arn,
            "jobName": self.job_name,
            "status": self.status,
            "importedModelName": self.imported_model_name,
            "importedModelArn": self.imported_model_arn,
            "creationTime": self.creation_time,
            "lastModifiedTime": self.last_modified_time,
            "endTime": self.end_time,
        }


class ImportedModel(BaseModel):
    def __init__(
        self,
        model_name: str,
        model_arn: str,
        job_name: str,
        job_arn: str,
        model_data_source: dict[str, Any],
        region_name: str,
        account_id: str,
        model_kms_key_arn: Optional[str] = None,
    ):
        self.model_name = model_name
        self.model_arn = model_arn
        self.job_name = job_name
        self.job_arn = job_arn
        self.model_data_source = model_data_source
        self.model_kms_key_arn = model_kms_key_arn
        self.region_name = region_name
        self.account_id = account_id
        self.creation_time = _iso_now()
        self.model_architecture = ""
        self.instruct_supported = False
        self.custom_model_units = 1

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {
            "modelArn": self.model_arn,
            "modelName": self.model_name,
            "jobName": self.job_name,
            "jobArn": self.job_arn,
            "modelDataSource": self.model_data_source,
            "creationTime": self.creation_time,
        }
        if self.model_kms_key_arn:
            d["modelKmsKeyArn"] = self.model_kms_key_arn
        if self.model_architecture:
            d["modelArchitecture"] = self.model_architecture
        return d

    def summary(self) -> dict[str, Any]:
        return {
            "modelArn": self.model_arn,
            "modelName": self.model_name,
            "creationTime": self.creation_time,
        }


class ModelCopyJob(BaseModel):
    def __init__(
        self,
        source_model_arn: str,
        target_model_name: str,
        region_name: str,
        account_id: str,
        model_kms_key_id: Optional[str] = None,
        target_model_tags: Optional[list[dict[str, str]]] = None,
    ):
        self.source_model_arn = source_model_arn
        self.target_model_name = target_model_name
        self.model_kms_key_id = model_kms_key_id
        self.target_model_tags = target_model_tags
        self.region_name = region_name
        self.account_id = account_id
        self.job_id = str(uuid.uuid4())[:12]
        partition = get_partition(region_name)
        self.job_arn = f"arn:{partition}:bedrock:{region_name}:{account_id}:model-copy-job/{self.job_id}"
        self.target_model_arn = f"arn:{partition}:bedrock:{region_name}:{account_id}:custom-model/{target_model_name}"
        self.status = "Completed"
        now = _iso_now()
        self.creation_time = now
        self.failure_message = ""
        # Extract source account from ARN
        parts = source_model_arn.split(":")
        self.source_account_id = parts[4] if len(parts) > 4 else account_id
        self.source_model_name = source_model_arn.split("/")[-1] if "/" in source_model_arn else ""
        self.target_model_kms_key_arn = ""
        if model_kms_key_id:
            self.target_model_kms_key_arn = f"arn:{partition}:kms:{region_name}:{account_id}:key/{model_kms_key_id}"

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {
            "jobArn": self.job_arn,
            "status": self.status,
            "creationTime": self.creation_time,
            "targetModelArn": self.target_model_arn,
            "targetModelName": self.target_model_name,
            "sourceAccountId": self.source_account_id,
            "sourceModelArn": self.source_model_arn,
            "sourceModelName": self.source_model_name,
        }
        if self.target_model_kms_key_arn:
            d["targetModelKmsKeyArn"] = self.target_model_kms_key_arn
        if self.target_model_tags:
            d["targetModelTags"] = self.target_model_tags
        if self.failure_message:
            d["failureMessage"] = self.failure_message
        return d

    def summary(self) -> dict[str, Any]:
        return {
            "jobArn": self.job_arn,
            "status": self.status,
            "creationTime": self.creation_time,
            "targetModelArn": self.target_model_arn,
            "sourceAccountId": self.source_account_id,
            "sourceModelArn": self.source_model_arn,
        }


class ModelInvocationJob(BaseModel):
    def __init__(
        self,
        job_name: str,
        role_arn: str,
        model_id: str,
        input_data_config: dict[str, Any],
        output_data_config: dict[str, Any],
        region_name: str,
        account_id: str,
        client_request_token: Optional[str] = None,
        vpc_config: Optional[dict[str, Any]] = None,
        timeout_duration_in_hours: Optional[int] = None,
        model_invocation_type: Optional[str] = None,
    ):
        self.job_name = job_name
        self.role_arn = role_arn
        self.model_id = model_id
        self.input_data_config = input_data_config
        self.output_data_config = output_data_config
        self.client_request_token = client_request_token
        self.vpc_config = vpc_config
        self.timeout_duration_in_hours = timeout_duration_in_hours or 24
        self.model_invocation_type = model_invocation_type
        self.region_name = region_name
        self.account_id = account_id
        self.job_id = str(uuid.uuid4())[:12]
        partition = get_partition(region_name)
        self.job_arn = f"arn:{partition}:bedrock:{region_name}:{account_id}:model-invocation-job/{self.job_id}"
        self.status = "InProgress"
        self.message = ""
        now = _iso_now()
        self.submit_time = now
        self.last_modified_time = now
        self.end_time = ""
        self.job_expiration_time = ""

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {
            "jobArn": self.job_arn,
            "jobName": self.job_name,
            "modelId": self.model_id,
            "roleArn": self.role_arn,
            "status": self.status,
            "submitTime": self.submit_time,
            "lastModifiedTime": self.last_modified_time,
            "inputDataConfig": self.input_data_config,
            "outputDataConfig": self.output_data_config,
            "timeoutDurationInHours": self.timeout_duration_in_hours,
        }
        if self.client_request_token:
            d["clientRequestToken"] = self.client_request_token
        if self.message:
            d["message"] = self.message
        if self.end_time:
            d["endTime"] = self.end_time
        if self.vpc_config:
            d["vpcConfig"] = self.vpc_config
        if self.job_expiration_time:
            d["jobExpirationTime"] = self.job_expiration_time
        if self.model_invocation_type:
            d["modelInvocationType"] = self.model_invocation_type
        return d

    def summary(self) -> dict[str, Any]:
        d: dict[str, Any] = {
            "jobArn": self.job_arn,
            "jobName": self.job_name,
            "modelId": self.model_id,
            "status": self.status,
            "submitTime": self.submit_time,
            "lastModifiedTime": self.last_modified_time,
            "inputDataConfig": self.input_data_config,
            "outputDataConfig": self.output_data_config,
            "timeoutDurationInHours": self.timeout_duration_in_hours,
        }
        if self.end_time:
            d["endTime"] = self.end_time
        return d


class FoundationModelInfo(BaseModel):
    """Static foundation model info."""
    def __init__(
        self,
        model_id: str,
        model_name: str,
        provider: str,
    ):
        self.model_id = model_id
        self.model_name = model_name
        self.provider_name = provider
        self.model_arn = ""  # Set by caller
        self.input_modalities = ["TEXT"]
        self.output_modalities = ["TEXT"]
        self.customizations_supported: list[str] = []
        self.inference_types_supported = ["ON_DEMAND"]
        self.response_streaming_supported = True
        self.model_lifecycle = {"status": "ACTIVE"}

    def to_dict(self) -> dict[str, Any]:
        return {
            "modelArn": self.model_arn,
            "modelId": self.model_id,
            "modelName": self.model_name,
            "providerName": self.provider_name,
            "inputModalities": self.input_modalities,
            "outputModalities": self.output_modalities,
            "responseStreamingSupported": self.response_streaming_supported,
            "customizationsSupported": self.customizations_supported,
            "inferenceTypesSupported": self.inference_types_supported,
            "modelLifecycle": self.model_lifecycle,
        }

    def summary(self) -> dict[str, Any]:
        return {
            "modelArn": self.model_arn,
            "modelId": self.model_id,
            "modelName": self.model_name,
            "providerName": self.provider_name,
            "inputModalities": self.input_modalities,
            "outputModalities": self.output_modalities,
            "responseStreamingSupported": self.response_streaming_supported,
            "customizationsSupported": self.customizations_supported,
            "inferenceTypesSupported": self.inference_types_supported,
            "modelLifecycle": self.model_lifecycle,
        }


class MarketplaceModelEndpoint(BaseModel):
    def __init__(
        self,
        model_source_identifier: str,
        endpoint_config: dict[str, Any],
        region_name: str,
        account_id: str,
        endpoint_name: Optional[str] = None,
        accept_eula: bool = False,
    ):
        self.model_source_identifier = model_source_identifier
        self.endpoint_config = endpoint_config
        self.accept_eula = accept_eula
        self.endpoint_name = endpoint_name or f"endpoint-{str(uuid.uuid4())[:8]}"
        self.region_name = region_name
        self.account_id = account_id
        partition = get_partition(region_name)
        self.endpoint_arn = f"arn:{partition}:bedrock:{region_name}:{account_id}:marketplace-model-endpoint/{self.endpoint_name}"
        self.status = "ACTIVE"
        self.status_message = ""
        now = _iso_now()
        self.created_at = now
        self.updated_at = now
        self.registered = False

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {
            "endpointArn": self.endpoint_arn,
            "modelSourceIdentifier": self.model_source_identifier,
            "endpointConfig": self.endpoint_config,
            "endpointStatus": self.status,
            "createdAt": self.created_at,
            "updatedAt": self.updated_at,
        }
        if self.status_message:
            d["endpointStatusMessage"] = self.status_message
        return d

    def summary(self) -> dict[str, Any]:
        return self.to_dict()


class PromptRouter(BaseModel):
    def __init__(
        self,
        prompt_router_name: str,
        models: list[dict[str, Any]],
        routing_criteria: dict[str, Any],
        fallback_model: dict[str, Any],
        region_name: str,
        account_id: str,
        description: Optional[str] = None,
    ):
        self.prompt_router_name = prompt_router_name
        self.models = models
        self.routing_criteria = routing_criteria
        self.fallback_model = fallback_model
        self.description = description or ""
        self.region_name = region_name
        self.account_id = account_id
        self.prompt_router_id = str(uuid.uuid4())[:12]
        partition = get_partition(region_name)
        self.prompt_router_arn = f"arn:{partition}:bedrock:{region_name}:{account_id}:prompt-router/{self.prompt_router_id}"
        self.status = "ACTIVE"
        self.type = "custom"
        now = _iso_now()
        self.created_at = now
        self.updated_at = now

    def to_dict(self) -> dict[str, Any]:
        return {
            "promptRouterName": self.prompt_router_name,
            "routingCriteria": self.routing_criteria,
            "description": self.description,
            "createdAt": self.created_at,
            "updatedAt": self.updated_at,
            "promptRouterArn": self.prompt_router_arn,
            "models": self.models,
            "fallbackModel": self.fallback_model,
            "status": self.status,
            "type": self.type,
        }

    def summary(self) -> dict[str, Any]:
        return {
            "promptRouterName": self.prompt_router_name,
            "promptRouterArn": self.prompt_router_arn,
            "description": self.description,
            "status": self.status,
            "type": self.type,
            "createdAt": self.created_at,
            "updatedAt": self.updated_at,
            "routingCriteria": self.routing_criteria,
            "fallbackModel": self.fallback_model,
            "models": self.models,
        }


class CustomModelDeployment(BaseModel):
    def __init__(
        self,
        model_deployment_name: str,
        model_id: str,
        region_name: str,
        account_id: str,
    ):
        self.model_deployment_name = model_deployment_name
        self.model_id = model_id
        self.region_name = region_name
        self.account_id = account_id
        self.deployment_id = str(uuid.uuid4())[:12]
        partition = get_partition(region_name)
        self.deployment_arn = f"arn:{partition}:bedrock:{region_name}:{account_id}:custom-model-deployment/{self.deployment_id}"
        self.status = "ACTIVE"
        now = _iso_now()
        self.created_at = now
        self.last_modified_time = now
        self.failure_message = ""

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {
            "customModelDeploymentIdentifier": self.deployment_id,
            "customModelDeploymentArn": self.deployment_arn,
            "modelDeploymentName": self.model_deployment_name,
            "modelId": self.model_id,
            "status": self.status,
            "createdAt": self.created_at,
            "lastModifiedTime": self.last_modified_time,
        }
        if self.failure_message:
            d["failureMessage"] = self.failure_message
        return d

    def summary(self) -> dict[str, Any]:
        return self.to_dict()


class AutomatedReasoningPolicy(BaseModel):
    def __init__(
        self,
        name: str,
        policy_type: str,
        region_name: str,
        account_id: str,
        description: Optional[str] = None,
        rules: Optional[list[dict[str, Any]]] = None,
    ):
        self.name = name
        self.policy_type = policy_type
        self.description = description or ""
        self.rules = rules or []
        self.region_name = region_name
        self.account_id = account_id
        self.policy_id = str(uuid.uuid4())[:12]
        partition = get_partition(region_name)
        self.policy_arn = f"arn:{partition}:bedrock:{region_name}:{account_id}:automated-reasoning-policy/{self.policy_id}"
        self.status = "ACTIVE"
        self.version = 1
        now = _iso_now()
        self.created_at = now
        self.updated_at = now
        self.build_workflows: dict[str, dict[str, Any]] = {}
        self.test_cases: dict[str, dict[str, Any]] = {}

    def to_dict(self) -> dict[str, Any]:
        return {
            "policyArn": self.policy_arn,
            "name": self.name,
            "description": self.description,
            "policyType": self.policy_type,
            "status": self.status,
            "version": self.version,
            "createdAt": self.created_at,
            "updatedAt": self.updated_at,
            "rules": self.rules,
        }

    def summary(self) -> dict[str, Any]:
        return {
            "policyArn": self.policy_arn,
            "name": self.name,
            "status": self.status,
            "createdAt": self.created_at,
            "updatedAt": self.updated_at,
        }


# ---------------------------------------------------------------------------
# Well-known foundation models (static catalog)
# ---------------------------------------------------------------------------

_FOUNDATION_MODELS = [
    ("amazon.titan-text-express-v1", "Titan Text Express", "Amazon"),
    ("amazon.titan-text-lite-v1", "Titan Text Lite", "Amazon"),
    ("amazon.titan-embed-text-v1", "Titan Embeddings G1 - Text", "Amazon"),
    ("amazon.titan-embed-text-v2:0", "Titan Text Embeddings V2", "Amazon"),
    ("amazon.titan-embed-image-v1", "Titan Multimodal Embeddings G1", "Amazon"),
    ("amazon.titan-image-generator-v1", "Titan Image Generator G1", "Amazon"),
    ("anthropic.claude-v2", "Claude", "Anthropic"),
    ("anthropic.claude-v2:1", "Claude", "Anthropic"),
    ("anthropic.claude-3-sonnet-20240229-v1:0", "Claude 3 Sonnet", "Anthropic"),
    ("anthropic.claude-3-haiku-20240307-v1:0", "Claude 3 Haiku", "Anthropic"),
    ("anthropic.claude-3-opus-20240229-v1:0", "Claude 3 Opus", "Anthropic"),
    ("anthropic.claude-instant-v1", "Claude Instant", "Anthropic"),
    ("ai21.j2-mid-v1", "Jurassic-2 Mid", "AI21 Labs"),
    ("ai21.j2-ultra-v1", "Jurassic-2 Ultra", "AI21 Labs"),
    ("cohere.command-text-v14", "Command", "Cohere"),
    ("cohere.command-light-text-v14", "Command Light", "Cohere"),
    ("cohere.embed-english-v3", "Embed English", "Cohere"),
    ("cohere.embed-multilingual-v3", "Embed Multilingual", "Cohere"),
    ("meta.llama2-13b-chat-v1", "Llama 2 Chat 13B", "Meta"),
    ("meta.llama2-70b-chat-v1", "Llama 2 Chat 70B", "Meta"),
    ("meta.llama3-8b-instruct-v1:0", "Llama 3 8B Instruct", "Meta"),
    ("meta.llama3-70b-instruct-v1:0", "Llama 3 70B Instruct", "Meta"),
    ("mistral.mistral-7b-instruct-v0:2", "Mistral 7B Instruct", "Mistral AI"),
    ("mistral.mixtral-8x7b-instruct-v0:1", "Mixtral 8x7B Instruct", "Mistral AI"),
    ("stability.stable-diffusion-xl-v1", "Stable Diffusion XL", "Stability AI"),
]


# ---------------------------------------------------------------------------
# Backend
# ---------------------------------------------------------------------------

class BedrockBackend(BaseBackend):
    """Implementation of Bedrock APIs."""

    PAGINATION_MODEL = {
        "list_model_customization_jobs": {
            "input_token": "next_token",
            "limit_key": "max_results",
            "limit_default": 100,
            "unique_attribute": "job_arn",
        },
        "list_custom_models": {
            "input_token": "next_token",
            "limit_key": "max_results",
            "limit_default": 100,
            "unique_attribute": "model_arn",
        },
        "list_guardrails": {
            "input_token": "next_token",
            "limit_key": "max_results",
            "limit_default": 100,
            "unique_attribute": "guardrail_id",
        },
        "list_provisioned_model_throughputs": {
            "input_token": "next_token",
            "limit_key": "max_results",
            "limit_default": 100,
            "unique_attribute": "provisioned_model_id",
        },
        "list_evaluation_jobs": {
            "input_token": "next_token",
            "limit_key": "max_results",
            "limit_default": 100,
            "unique_attribute": "job_arn",
        },
        "list_inference_profiles": {
            "input_token": "next_token",
            "limit_key": "max_results",
            "limit_default": 100,
            "unique_attribute": "inference_profile_id",
        },
        "list_model_import_jobs": {
            "input_token": "next_token",
            "limit_key": "max_results",
            "limit_default": 100,
            "unique_attribute": "job_arn",
        },
        "list_model_copy_jobs": {
            "input_token": "next_token",
            "limit_key": "max_results",
            "limit_default": 100,
            "unique_attribute": "job_arn",
        },
        "list_model_invocation_jobs": {
            "input_token": "next_token",
            "limit_key": "max_results",
            "limit_default": 100,
            "unique_attribute": "job_arn",
        },
        "list_imported_models": {
            "input_token": "next_token",
            "limit_key": "max_results",
            "limit_default": 100,
            "unique_attribute": "model_arn",
        },
        "list_marketplace_model_endpoints": {
            "input_token": "next_token",
            "limit_key": "max_results",
            "limit_default": 100,
            "unique_attribute": "endpoint_arn",
        },
        "list_prompt_routers": {
            "input_token": "next_token",
            "limit_key": "max_results",
            "limit_default": 100,
            "unique_attribute": "prompt_router_arn",
        },
        "list_custom_model_deployments": {
            "input_token": "next_token",
            "limit_key": "max_results",
            "limit_default": 100,
            "unique_attribute": "deployment_id",
        },
        "list_automated_reasoning_policies": {
            "input_token": "next_token",
            "limit_key": "max_results",
            "limit_default": 100,
            "unique_attribute": "policy_arn",
        },
    }

    def __init__(self, region_name: str, account_id: str) -> None:
        super().__init__(region_name, account_id)
        self.model_customization_jobs: dict[str, ModelCustomizationJob] = {}
        self.custom_models: dict[str, CustomModel] = {}
        self.model_invocation_logging_configuration: Optional[
            ModelInvocationLoggingConfiguration
        ] = None
        self.tagger = TaggingService()
        self.guardrails: dict[str, Guardrail] = {}
        self.provisioned_model_throughputs: dict[str, ProvisionedModelThroughput] = {}
        self.evaluation_jobs: dict[str, EvaluationJob] = {}
        self.inference_profiles: dict[str, InferenceProfile] = {}
        self.model_import_jobs: dict[str, ModelImportJob] = {}
        self.imported_models: dict[str, ImportedModel] = {}
        self.model_copy_jobs: dict[str, ModelCopyJob] = {}
        self.model_invocation_jobs: dict[str, ModelInvocationJob] = {}
        self.marketplace_model_endpoints: dict[str, MarketplaceModelEndpoint] = {}
        self.prompt_routers: dict[str, PromptRouter] = {}
        self.custom_model_deployments: dict[str, CustomModelDeployment] = {}
        self.automated_reasoning_policies: dict[str, AutomatedReasoningPolicy] = {}
        self.enforced_guardrail_configs: dict[str, dict[str, Any]] = {}
        self.use_case_for_model_access: Optional[dict[str, Any]] = None
        self._init_foundation_models()

    def _init_foundation_models(self) -> None:
        self.foundation_models: dict[str, FoundationModelInfo] = {}
        partition = get_partition(self.region_name)
        for model_id, model_name, provider in _FOUNDATION_MODELS:
            fm = FoundationModelInfo(model_id, model_name, provider)
            fm.model_arn = f"arn:{partition}:bedrock:{self.region_name}::foundation-model/{model_id}"
            self.foundation_models[model_id] = fm

    def _list_arns(self) -> list[str]:
        arns = [job.job_arn for job in self.model_customization_jobs.values()]
        arns += [model.model_arn for model in self.custom_models.values()]
        arns += [g.guardrail_arn for g in self.guardrails.values()]
        arns += [p.provisioned_model_arn for p in self.provisioned_model_throughputs.values()]
        arns += [e.job_arn for e in self.evaluation_jobs.values()]
        arns += [i.inference_profile_arn for i in self.inference_profiles.values()]
        arns += [j.job_arn for j in self.model_import_jobs.values()]
        arns += [m.model_arn for m in self.imported_models.values()]
        arns += [j.job_arn for j in self.model_copy_jobs.values()]
        arns += [j.job_arn for j in self.model_invocation_jobs.values()]
        arns += [e.endpoint_arn for e in self.marketplace_model_endpoints.values()]
        arns += [r.prompt_router_arn for r in self.prompt_routers.values()]
        arns += [d.deployment_arn for d in self.custom_model_deployments.values()]
        arns += [p.policy_arn for p in self.automated_reasoning_policies.values()]
        return arns

    # -------------------------------------------------------------------
    # Model Customization Jobs (existing)
    # -------------------------------------------------------------------

    def create_model_customization_job(
        self,
        job_name: str,
        custom_model_name: str,
        role_arn: str,
        base_model_identifier: str,
        training_data_config: dict[str, Any],
        output_data_config: dict[str, str],
        hyper_parameters: dict[str, str],
        client_request_token: Optional[str],
        customization_type: Optional[str],
        custom_model_kms_key_id: Optional[str],
        job_tags: Optional[list[dict[str, str]]],
        custom_model_tags: Optional[list[dict[str, str]]],
        validation_data_config: Optional[dict[str, Any]],
        vpc_config: Optional[dict[str, Any]],
    ) -> str:
        if job_name in self.model_customization_jobs.keys():
            raise ResourceInUseException(
                f"Model customization job {job_name} already exists"
            )
        if custom_model_name in self.custom_models.keys():
            raise ResourceInUseException(
                f"Custom model {custom_model_name} already exists"
            )
        model_customization_job = ModelCustomizationJob(
            job_name,
            custom_model_name,
            role_arn,
            base_model_identifier,
            training_data_config,
            output_data_config,
            hyper_parameters,
            self.region_name,
            self.account_id,
            client_request_token,
            customization_type,
            custom_model_kms_key_id,
            job_tags,
            custom_model_tags,
            validation_data_config,
            vpc_config,
        )
        self.model_customization_jobs[job_name] = model_customization_job
        if job_tags:
            self.tag_resource(model_customization_job.job_arn, job_tags)
        # Create associated custom model
        custom_model = CustomModel(
            custom_model_name,
            job_name,
            model_customization_job.job_arn,
            model_customization_job.base_model_arn,
            model_customization_job.hyper_parameters,
            model_customization_job.output_data_config,
            model_customization_job.training_data_config,
            model_customization_job.training_metrics,
            model_customization_job.base_model_identifier,
            self.region_name,
            self.account_id,
            model_customization_job.customization_type,
            model_customization_job.output_model_kms_key_arn,
            model_customization_job.validation_data_config,
            model_customization_job.validation_metrics,
        )
        self.custom_models[custom_model_name] = custom_model
        if custom_model_tags:
            self.tag_resource(custom_model.model_arn, custom_model_tags)
        return model_customization_job.job_arn

    def get_model_customization_job(self, job_identifier: str) -> ModelCustomizationJob:
        if job_identifier not in self.model_customization_jobs:
            raise ResourceNotFoundException(
                f"Model customization job {job_identifier} not found"
            )
        else:
            return self.model_customization_jobs[job_identifier]

    def stop_model_customization_job(self, job_identifier: str) -> None:
        if job_identifier in self.model_customization_jobs:
            self.model_customization_jobs[job_identifier].status = "Stopped"
        else:
            raise ResourceNotFoundException(
                f"Model customization job {job_identifier} not found"
            )
        return

    @paginate(pagination_model=PAGINATION_MODEL)
    def list_model_customization_jobs(
        self,
        creation_time_after: Optional[datetime],
        creation_time_before: Optional[datetime],
        status_equals: Optional[str],
        name_contains: Optional[str],
        sort_by: Optional[str],
        sort_order: Optional[str],
    ) -> list[ModelCustomizationJob]:
        customization_jobs_fetched = list(self.model_customization_jobs.values())

        if name_contains is not None:
            customization_jobs_fetched = list(
                filter(
                    lambda x: name_contains in x.job_name,
                    customization_jobs_fetched,
                )
            )

        if creation_time_after is not None:
            customization_jobs_fetched = list(
                filter(
                    lambda x: x.creation_time > str(creation_time_after),
                    customization_jobs_fetched,
                )
            )

        if creation_time_before is not None:
            customization_jobs_fetched = list(
                filter(
                    lambda x: x.creation_time < str(creation_time_before),
                    customization_jobs_fetched,
                )
            )
        if status_equals is not None:
            customization_jobs_fetched = list(
                filter(
                    lambda x: x.status == status_equals,
                    customization_jobs_fetched,
                )
            )

        if sort_by is not None:
            if sort_by == "CreationTime":
                if sort_order is not None and sort_order == "Ascending":
                    customization_jobs_fetched = sorted(
                        customization_jobs_fetched, key=lambda x: x.creation_time
                    )
                elif sort_order is not None and sort_order == "Descending":
                    customization_jobs_fetched = sorted(
                        customization_jobs_fetched,
                        key=lambda x: x.creation_time,
                        reverse=True,
                    )
                else:
                    raise ValidationException(f"Invalid sort order: {sort_order}")
            else:
                raise ValidationException(f"Invalid sort by field: {sort_by}")

        return customization_jobs_fetched

    # -------------------------------------------------------------------
    # Model Invocation Logging Configuration (existing)
    # -------------------------------------------------------------------

    def get_model_invocation_logging_configuration(self) -> Optional[dict[str, Any]]:
        if self.model_invocation_logging_configuration:
            return self.model_invocation_logging_configuration.logging_config
        else:
            return {}

    def put_model_invocation_logging_configuration(
        self, logging_config: dict[str, Any]
    ) -> None:
        invocation_logging = ModelInvocationLoggingConfiguration(logging_config)
        self.model_invocation_logging_configuration = invocation_logging
        return

    def delete_model_invocation_logging_configuration(self) -> None:
        if self.model_invocation_logging_configuration:
            self.model_invocation_logging_configuration.logging_config = {}
        return

    # -------------------------------------------------------------------
    # Custom Models (existing)
    # -------------------------------------------------------------------

    def get_custom_model(self, model_identifier: str) -> CustomModel:
        if model_identifier.startswith("arn:"):
            for model in self.custom_models.values():
                if model.model_arn == model_identifier:
                    return model
            raise ResourceNotFoundException(
                f"Custom model {model_identifier} not found"
            )
        elif model_identifier in self.custom_models:
            return self.custom_models[model_identifier]
        else:
            raise ResourceNotFoundException(
                f"Custom model {model_identifier} not found"
            )

    def delete_custom_model(self, model_identifier: str) -> None:
        if model_identifier in self.custom_models:
            del self.custom_models[model_identifier]
        else:
            raise ResourceNotFoundException(
                f"Custom model {model_identifier} not found"
            )
        return

    @paginate(pagination_model=PAGINATION_MODEL)
    def list_custom_models(
        self,
        creation_time_before: Optional[datetime],
        creation_time_after: Optional[datetime],
        name_contains: Optional[str],
        base_model_arn_equals: Optional[str],
        foundation_model_arn_equals: Optional[str],
        sort_by: Optional[str],
        sort_order: Optional[str],
    ) -> list[CustomModel]:
        """
        The foundation_model_arn_equals-argument is not yet supported
        """
        custom_models_fetched = list(self.custom_models.values())

        if name_contains is not None:
            custom_models_fetched = list(
                filter(
                    lambda x: name_contains in x.job_name,
                    custom_models_fetched,
                )
            )

        if creation_time_after is not None:
            custom_models_fetched = list(
                filter(
                    lambda x: x.creation_time > str(creation_time_after),
                    custom_models_fetched,
                )
            )

        if creation_time_before is not None:
            custom_models_fetched = list(
                filter(
                    lambda x: x.creation_time < str(creation_time_before),
                    custom_models_fetched,
                )
            )
        if base_model_arn_equals is not None:
            custom_models_fetched = list(
                filter(
                    lambda x: x.base_model_arn == base_model_arn_equals,
                    custom_models_fetched,
                )
            )

        if sort_by is not None:
            if sort_by == "CreationTime":
                if sort_order is not None and sort_order == "Ascending":
                    custom_models_fetched = sorted(
                        custom_models_fetched, key=lambda x: x.creation_time
                    )
                elif sort_order is not None and sort_order == "Descending":
                    custom_models_fetched = sorted(
                        custom_models_fetched,
                        key=lambda x: x.creation_time,
                        reverse=True,
                    )
                else:
                    raise ValidationException(f"Invalid sort order: {sort_order}")
            else:
                raise ValidationException(f"Invalid sort by field: {sort_by}")
        return custom_models_fetched

    def create_custom_model(
        self,
        model_name: str,
        model_source_config: Optional[dict[str, Any]] = None,
        model_kms_key_id: Optional[str] = None,
    ) -> dict[str, str]:
        """CreateCustomModel - creates a custom model directly (without a customization job)."""
        if model_name in self.custom_models:
            raise ResourceInUseException(f"Custom model {model_name} already exists")
        partition = get_partition(self.region_name)
        model_arn = f"arn:{partition}:bedrock:{self.region_name}:{self.account_id}:custom-model/{model_name}"
        custom_model = CustomModel(
            model_name=model_name,
            job_name="",
            job_arn="",
            base_model_arn="",
            hyper_parameters={},
            output_data_config={},
            training_data_config={},
            training_metrics={},
            base_model_name="",
            region_name=self.region_name,
            account_id=self.account_id,
            customization_type=None,
            model_kms_key_arn=model_kms_key_id,
            validation_data_config=None,
            validation_metrics=None,
        )
        custom_model.model_arn = model_arn
        self.custom_models[model_name] = custom_model
        return {"modelArn": model_arn}

    # -------------------------------------------------------------------
    # Tagging (existing)
    # -------------------------------------------------------------------

    def tag_resource(self, resource_arn: str, tags: list[dict[str, str]]) -> None:
        if resource_arn not in self._list_arns():
            raise ResourceNotFoundException(f"Resource {resource_arn} not found")
        fixed_tags = []
        if len(tags) + len(self.tagger.list_tags_for_resource(resource_arn)) > 50:
            raise TooManyTagsException(
                "Member must have length less than or equal to 50"
            )
        for tag_dict in tags:
            fixed_tags.append({"Key": tag_dict["key"], "Value": tag_dict["value"]})
        self.tagger.tag_resource(resource_arn, fixed_tags)
        return

    def untag_resource(self, resource_arn: str, tag_keys: list[str]) -> None:
        if resource_arn not in self._list_arns():
            raise ResourceNotFoundException(f"Resource {resource_arn} not found")
        self.tagger.untag_resource_using_names(resource_arn, tag_keys)
        return

    def list_tags_for_resource(self, resource_arn: str) -> list[dict[str, str]]:
        if resource_arn not in self._list_arns():
            raise ResourceNotFoundException(f"Resource {resource_arn} not found")
        tags = self.tagger.list_tags_for_resource(resource_arn)
        fixed_tags = []
        for tag_dict in tags["Tags"]:
            fixed_tags.append({"key": tag_dict["Key"], "value": tag_dict["Value"]})
        return fixed_tags

    # -------------------------------------------------------------------
    # Guardrails
    # -------------------------------------------------------------------

    def create_guardrail(
        self,
        name: str,
        blocked_input_messaging: str,
        blocked_outputs_messaging: str,
        description: Optional[str] = None,
        topic_policy_config: Optional[dict[str, Any]] = None,
        content_policy_config: Optional[dict[str, Any]] = None,
        word_policy_config: Optional[dict[str, Any]] = None,
        sensitive_information_policy_config: Optional[dict[str, Any]] = None,
        contextual_grounding_policy_config: Optional[dict[str, Any]] = None,
        automated_reasoning_policy_config: Optional[dict[str, Any]] = None,
        cross_region_config: Optional[dict[str, Any]] = None,
        kms_key_id: Optional[str] = None,
        tags: Optional[list[dict[str, str]]] = None,
    ) -> dict[str, Any]:
        guardrail = Guardrail(
            name=name,
            region_name=self.region_name,
            account_id=self.account_id,
            blocked_input_messaging=blocked_input_messaging,
            blocked_outputs_messaging=blocked_outputs_messaging,
            description=description,
            topic_policy_config=topic_policy_config,
            content_policy_config=content_policy_config,
            word_policy_config=word_policy_config,
            sensitive_information_policy_config=sensitive_information_policy_config,
            contextual_grounding_policy_config=contextual_grounding_policy_config,
            automated_reasoning_policy_config=automated_reasoning_policy_config,
            cross_region_config=cross_region_config,
            kms_key_id=kms_key_id,
        )
        self.guardrails[guardrail.guardrail_id] = guardrail
        if tags:
            self.tag_resource(guardrail.guardrail_arn, tags)
        return {
            "guardrailId": guardrail.guardrail_id,
            "guardrailArn": guardrail.guardrail_arn,
            "version": guardrail.version,
            "createdAt": guardrail.created_at,
        }

    def _find_guardrail(self, guardrail_identifier: str) -> Guardrail:
        # Could be an ID or an ARN
        if guardrail_identifier in self.guardrails:
            return self.guardrails[guardrail_identifier]
        for g in self.guardrails.values():
            if g.guardrail_arn == guardrail_identifier:
                return g
        raise ResourceNotFoundException(
            f"Could not find guardrail {guardrail_identifier}"
        )

    def get_guardrail(
        self,
        guardrail_identifier: str,
        guardrail_version: Optional[str] = None,
    ) -> dict[str, Any]:
        guardrail = self._find_guardrail(guardrail_identifier)
        if guardrail_version and guardrail_version != "DRAFT":
            if guardrail_version in guardrail.versions:
                return guardrail.versions[guardrail_version]
            raise ResourceNotFoundException(
                f"Could not find guardrail version {guardrail_version}"
            )
        return guardrail.to_dict()

    def update_guardrail(
        self,
        guardrail_identifier: str,
        name: str,
        blocked_input_messaging: str,
        blocked_outputs_messaging: str,
        description: Optional[str] = None,
        topic_policy_config: Optional[dict[str, Any]] = None,
        content_policy_config: Optional[dict[str, Any]] = None,
        word_policy_config: Optional[dict[str, Any]] = None,
        sensitive_information_policy_config: Optional[dict[str, Any]] = None,
        contextual_grounding_policy_config: Optional[dict[str, Any]] = None,
        automated_reasoning_policy_config: Optional[dict[str, Any]] = None,
        cross_region_config: Optional[dict[str, Any]] = None,
        kms_key_id: Optional[str] = None,
    ) -> dict[str, Any]:
        guardrail = self._find_guardrail(guardrail_identifier)
        guardrail.name = name
        guardrail.blocked_input_messaging = blocked_input_messaging
        guardrail.blocked_outputs_messaging = blocked_outputs_messaging
        if description is not None:
            guardrail.description = description
        guardrail.topic_policy_config = topic_policy_config
        guardrail.content_policy_config = content_policy_config
        guardrail.word_policy_config = word_policy_config
        guardrail.sensitive_information_policy_config = sensitive_information_policy_config
        guardrail.contextual_grounding_policy_config = contextual_grounding_policy_config
        guardrail.automated_reasoning_policy_config = automated_reasoning_policy_config
        guardrail.cross_region_config = cross_region_config
        if kms_key_id is not None:
            guardrail.kms_key_id = kms_key_id
        guardrail.updated_at = _iso_now()
        return {
            "guardrailId": guardrail.guardrail_id,
            "guardrailArn": guardrail.guardrail_arn,
            "version": guardrail.version,
            "updatedAt": guardrail.updated_at,
        }

    def delete_guardrail(
        self,
        guardrail_identifier: str,
        guardrail_version: Optional[str] = None,
    ) -> None:
        guardrail = self._find_guardrail(guardrail_identifier)
        if guardrail_version and guardrail_version != "DRAFT":
            if guardrail_version in guardrail.versions:
                del guardrail.versions[guardrail_version]
                return
            raise ResourceNotFoundException(
                f"Could not find guardrail version {guardrail_version}"
            )
        del self.guardrails[guardrail.guardrail_id]

    @paginate(pagination_model=PAGINATION_MODEL)
    def list_guardrails(
        self,
        guardrail_identifier: Optional[str] = None,
    ) -> list[Guardrail]:
        if guardrail_identifier:
            guardrail = self._find_guardrail(guardrail_identifier)
            return [guardrail]
        return list(self.guardrails.values())

    def create_guardrail_version(
        self,
        guardrail_identifier: str,
        description: Optional[str] = None,
    ) -> dict[str, Any]:
        guardrail = self._find_guardrail(guardrail_identifier)
        version_num = str(guardrail.next_version)
        guardrail.next_version += 1
        snapshot = guardrail.to_dict()
        snapshot["version"] = version_num
        if description:
            snapshot["description"] = description
        guardrail.versions[version_num] = snapshot
        return {
            "guardrailId": guardrail.guardrail_id,
            "version": version_num,
        }

    # -------------------------------------------------------------------
    # Provisioned Model Throughput
    # -------------------------------------------------------------------

    def create_provisioned_model_throughput(
        self,
        provisioned_model_name: str,
        model_id: str,
        model_units: int,
        commitment_duration: Optional[str] = None,
        tags: Optional[list[dict[str, str]]] = None,
    ) -> str:
        pmt = ProvisionedModelThroughput(
            provisioned_model_name=provisioned_model_name,
            model_id=model_id,
            model_units=model_units,
            region_name=self.region_name,
            account_id=self.account_id,
            commitment_duration=commitment_duration,
        )
        self.provisioned_model_throughputs[pmt.provisioned_model_id] = pmt
        if tags:
            self.tag_resource(pmt.provisioned_model_arn, tags)
        return pmt.provisioned_model_arn

    def _find_provisioned(self, provisioned_model_id: str) -> ProvisionedModelThroughput:
        if provisioned_model_id in self.provisioned_model_throughputs:
            return self.provisioned_model_throughputs[provisioned_model_id]
        for p in self.provisioned_model_throughputs.values():
            if p.provisioned_model_arn == provisioned_model_id:
                return p
            if p.provisioned_model_name == provisioned_model_id:
                return p
        raise ResourceNotFoundException(
            f"Could not find provisioned model {provisioned_model_id}"
        )

    def get_provisioned_model_throughput(self, provisioned_model_id: str) -> dict[str, Any]:
        pmt = self._find_provisioned(provisioned_model_id)
        return pmt.to_dict()

    def update_provisioned_model_throughput(
        self,
        provisioned_model_id: str,
        desired_provisioned_model_name: Optional[str] = None,
        desired_model_id: Optional[str] = None,
    ) -> None:
        pmt = self._find_provisioned(provisioned_model_id)
        if desired_provisioned_model_name:
            pmt.provisioned_model_name = desired_provisioned_model_name
        if desired_model_id:
            partition = get_partition(self.region_name)
            pmt.desired_model_arn = f"arn:{partition}:bedrock:{self.region_name}::foundation-model/{desired_model_id}"
        pmt.last_modified_time = _iso_now()

    def delete_provisioned_model_throughput(self, provisioned_model_id: str) -> None:
        pmt = self._find_provisioned(provisioned_model_id)
        del self.provisioned_model_throughputs[pmt.provisioned_model_id]

    @paginate(pagination_model=PAGINATION_MODEL)
    def list_provisioned_model_throughputs(
        self,
        creation_time_after: Optional[str] = None,
        creation_time_before: Optional[str] = None,
        status_equals: Optional[str] = None,
        model_arn_equals: Optional[str] = None,
        name_contains: Optional[str] = None,
        sort_by: Optional[str] = None,
        sort_order: Optional[str] = None,
    ) -> list[ProvisionedModelThroughput]:
        results = list(self.provisioned_model_throughputs.values())
        if name_contains:
            results = [r for r in results if name_contains in r.provisioned_model_name]
        if status_equals:
            results = [r for r in results if r.status == status_equals]
        if model_arn_equals:
            results = [r for r in results if r.model_arn == model_arn_equals]
        return results

    # -------------------------------------------------------------------
    # Evaluation Jobs
    # -------------------------------------------------------------------

    def create_evaluation_job(
        self,
        job_name: str,
        role_arn: str,
        evaluation_config: dict[str, Any],
        inference_config: dict[str, Any],
        output_data_config: dict[str, Any],
        job_description: Optional[str] = None,
        customer_encryption_key_id: Optional[str] = None,
        application_type: Optional[str] = None,
        job_tags: Optional[list[dict[str, str]]] = None,
    ) -> str:
        job = EvaluationJob(
            job_name=job_name,
            role_arn=role_arn,
            evaluation_config=evaluation_config,
            inference_config=inference_config,
            output_data_config=output_data_config,
            region_name=self.region_name,
            account_id=self.account_id,
            job_description=job_description,
            customer_encryption_key_id=customer_encryption_key_id,
            application_type=application_type,
        )
        self.evaluation_jobs[job.job_arn] = job
        if job_tags:
            self.tag_resource(job.job_arn, job_tags)
        return job.job_arn

    def _find_evaluation_job(self, job_identifier: str) -> EvaluationJob:
        if job_identifier in self.evaluation_jobs:
            return self.evaluation_jobs[job_identifier]
        for j in self.evaluation_jobs.values():
            if j.job_name == job_identifier or j.job_id == job_identifier:
                return j
        raise ResourceNotFoundException(
            f"Could not find evaluation job {job_identifier}"
        )

    def get_evaluation_job(self, job_identifier: str) -> dict[str, Any]:
        job = self._find_evaluation_job(job_identifier)
        return job.to_dict()

    def stop_evaluation_job(self, job_identifier: str) -> None:
        job = self._find_evaluation_job(job_identifier)
        job.status = "Stopped"
        job.last_modified_time = _iso_now()

    @paginate(pagination_model=PAGINATION_MODEL)
    def list_evaluation_jobs(
        self,
        creation_time_after: Optional[str] = None,
        creation_time_before: Optional[str] = None,
        status_equals: Optional[str] = None,
        application_type_equals: Optional[str] = None,
        name_contains: Optional[str] = None,
        sort_by: Optional[str] = None,
        sort_order: Optional[str] = None,
    ) -> list[EvaluationJob]:
        results = list(self.evaluation_jobs.values())
        if name_contains:
            results = [r for r in results if name_contains in r.job_name]
        if status_equals:
            results = [r for r in results if r.status == status_equals]
        if application_type_equals:
            results = [r for r in results if r.application_type == application_type_equals]
        return results

    def batch_delete_evaluation_job(
        self, job_identifiers: list[str]
    ) -> dict[str, Any]:
        errors: list[dict[str, str]] = []
        deleted: list[dict[str, str]] = []
        for jid in job_identifiers:
            try:
                job = self._find_evaluation_job(jid)
                deleted.append({"jobArn": job.job_arn, "status": job.status})
                del self.evaluation_jobs[job.job_arn]
            except ResourceNotFoundException:
                errors.append({
                    "jobIdentifier": jid,
                    "code": "ResourceNotFoundException",
                    "message": f"Evaluation job {jid} not found",
                })
        return {"errors": errors, "evaluationJobs": deleted}

    # -------------------------------------------------------------------
    # Inference Profiles
    # -------------------------------------------------------------------

    def create_inference_profile(
        self,
        inference_profile_name: str,
        model_source: dict[str, Any],
        description: Optional[str] = None,
        tags: Optional[list[dict[str, str]]] = None,
    ) -> dict[str, Any]:
        ip = InferenceProfile(
            inference_profile_name=inference_profile_name,
            model_source=model_source,
            region_name=self.region_name,
            account_id=self.account_id,
            description=description,
        )
        self.inference_profiles[ip.inference_profile_id] = ip
        if tags:
            self.tag_resource(ip.inference_profile_arn, tags)
        return {
            "inferenceProfileArn": ip.inference_profile_arn,
            "status": ip.status,
        }

    def _find_inference_profile(self, identifier: str) -> InferenceProfile:
        if identifier in self.inference_profiles:
            return self.inference_profiles[identifier]
        for ip in self.inference_profiles.values():
            if ip.inference_profile_arn == identifier or ip.inference_profile_name == identifier:
                return ip
        raise ResourceNotFoundException(
            f"Could not find inference profile {identifier}"
        )

    def get_inference_profile(self, inference_profile_identifier: str) -> dict[str, Any]:
        ip = self._find_inference_profile(inference_profile_identifier)
        return ip.to_dict()

    def delete_inference_profile(self, inference_profile_identifier: str) -> None:
        ip = self._find_inference_profile(inference_profile_identifier)
        del self.inference_profiles[ip.inference_profile_id]

    @paginate(pagination_model=PAGINATION_MODEL)
    def list_inference_profiles(
        self,
        type_equals: Optional[str] = None,
    ) -> list[InferenceProfile]:
        results = list(self.inference_profiles.values())
        if type_equals:
            results = [r for r in results if r.type == type_equals]
        return results

    # -------------------------------------------------------------------
    # Model Import Jobs
    # -------------------------------------------------------------------

    def create_model_import_job(
        self,
        job_name: str,
        imported_model_name: str,
        role_arn: str,
        model_data_source: dict[str, Any],
        vpc_config: Optional[dict[str, Any]] = None,
        imported_model_kms_key_id: Optional[str] = None,
        job_tags: Optional[list[dict[str, str]]] = None,
        imported_model_tags: Optional[list[dict[str, str]]] = None,
    ) -> str:
        job = ModelImportJob(
            job_name=job_name,
            imported_model_name=imported_model_name,
            role_arn=role_arn,
            model_data_source=model_data_source,
            region_name=self.region_name,
            account_id=self.account_id,
            vpc_config=vpc_config,
            imported_model_kms_key_id=imported_model_kms_key_id,
        )
        self.model_import_jobs[job.job_arn] = job
        if job_tags:
            self.tag_resource(job.job_arn, job_tags)
        # Create the imported model
        imported_model = ImportedModel(
            model_name=imported_model_name,
            model_arn=job.imported_model_arn,
            job_name=job_name,
            job_arn=job.job_arn,
            model_data_source=model_data_source,
            region_name=self.region_name,
            account_id=self.account_id,
            model_kms_key_arn=job.imported_model_kms_key_arn or None,
        )
        self.imported_models[imported_model_name] = imported_model
        if imported_model_tags:
            self.tag_resource(imported_model.model_arn, imported_model_tags)
        return job.job_arn

    def _find_model_import_job(self, job_identifier: str) -> ModelImportJob:
        if job_identifier in self.model_import_jobs:
            return self.model_import_jobs[job_identifier]
        for j in self.model_import_jobs.values():
            if j.job_name == job_identifier or j.job_id == job_identifier:
                return j
        raise ResourceNotFoundException(
            f"Could not find model import job {job_identifier}"
        )

    def get_model_import_job(self, job_identifier: str) -> dict[str, Any]:
        job = self._find_model_import_job(job_identifier)
        return job.to_dict()

    @paginate(pagination_model=PAGINATION_MODEL)
    def list_model_import_jobs(
        self,
        creation_time_after: Optional[str] = None,
        creation_time_before: Optional[str] = None,
        status_equals: Optional[str] = None,
        name_contains: Optional[str] = None,
        sort_by: Optional[str] = None,
        sort_order: Optional[str] = None,
    ) -> list[ModelImportJob]:
        results = list(self.model_import_jobs.values())
        if name_contains:
            results = [r for r in results if name_contains in r.job_name]
        if status_equals:
            results = [r for r in results if r.status == status_equals]
        return results

    # -------------------------------------------------------------------
    # Imported Models
    # -------------------------------------------------------------------

    def _find_imported_model(self, model_identifier: str) -> ImportedModel:
        if model_identifier in self.imported_models:
            return self.imported_models[model_identifier]
        for m in self.imported_models.values():
            if m.model_arn == model_identifier:
                return m
        raise ResourceNotFoundException(
            f"Could not find imported model {model_identifier}"
        )

    def get_imported_model(self, model_identifier: str) -> dict[str, Any]:
        model = self._find_imported_model(model_identifier)
        return model.to_dict()

    def delete_imported_model(self, model_identifier: str) -> None:
        model = self._find_imported_model(model_identifier)
        del self.imported_models[model.model_name]

    @paginate(pagination_model=PAGINATION_MODEL)
    def list_imported_models(
        self,
        creation_time_before: Optional[str] = None,
        creation_time_after: Optional[str] = None,
        name_contains: Optional[str] = None,
        sort_by: Optional[str] = None,
        sort_order: Optional[str] = None,
    ) -> list[ImportedModel]:
        results = list(self.imported_models.values())
        if name_contains:
            results = [r for r in results if name_contains in r.model_name]
        return results

    # -------------------------------------------------------------------
    # Model Copy Jobs
    # -------------------------------------------------------------------

    def create_model_copy_job(
        self,
        source_model_arn: str,
        target_model_name: str,
        model_kms_key_id: Optional[str] = None,
        target_model_tags: Optional[list[dict[str, str]]] = None,
    ) -> str:
        job = ModelCopyJob(
            source_model_arn=source_model_arn,
            target_model_name=target_model_name,
            region_name=self.region_name,
            account_id=self.account_id,
            model_kms_key_id=model_kms_key_id,
            target_model_tags=target_model_tags,
        )
        self.model_copy_jobs[job.job_arn] = job
        return job.job_arn

    def get_model_copy_job(self, job_arn: str) -> dict[str, Any]:
        if job_arn not in self.model_copy_jobs:
            raise ResourceNotFoundException(f"Could not find model copy job {job_arn}")
        return self.model_copy_jobs[job_arn].to_dict()

    @paginate(pagination_model=PAGINATION_MODEL)
    def list_model_copy_jobs(
        self,
        creation_time_after: Optional[str] = None,
        creation_time_before: Optional[str] = None,
        status_equals: Optional[str] = None,
        source_account_equals: Optional[str] = None,
        source_model_arn_equals: Optional[str] = None,
        target_model_name_contains: Optional[str] = None,
        sort_by: Optional[str] = None,
        sort_order: Optional[str] = None,
    ) -> list[ModelCopyJob]:
        results = list(self.model_copy_jobs.values())
        if status_equals:
            results = [r for r in results if r.status == status_equals]
        if source_account_equals:
            results = [r for r in results if r.source_account_id == source_account_equals]
        if source_model_arn_equals:
            results = [r for r in results if r.source_model_arn == source_model_arn_equals]
        if target_model_name_contains:
            results = [r for r in results if target_model_name_contains in r.target_model_name]
        return results

    # -------------------------------------------------------------------
    # Model Invocation Jobs (batch inference)
    # -------------------------------------------------------------------

    def create_model_invocation_job(
        self,
        job_name: str,
        role_arn: str,
        model_id: str,
        input_data_config: dict[str, Any],
        output_data_config: dict[str, Any],
        client_request_token: Optional[str] = None,
        vpc_config: Optional[dict[str, Any]] = None,
        timeout_duration_in_hours: Optional[int] = None,
        tags: Optional[list[dict[str, str]]] = None,
        model_invocation_type: Optional[str] = None,
    ) -> str:
        job = ModelInvocationJob(
            job_name=job_name,
            role_arn=role_arn,
            model_id=model_id,
            input_data_config=input_data_config,
            output_data_config=output_data_config,
            region_name=self.region_name,
            account_id=self.account_id,
            client_request_token=client_request_token,
            vpc_config=vpc_config,
            timeout_duration_in_hours=timeout_duration_in_hours,
            model_invocation_type=model_invocation_type,
        )
        self.model_invocation_jobs[job.job_arn] = job
        if tags:
            self.tag_resource(job.job_arn, tags)
        return job.job_arn

    def _find_model_invocation_job(self, job_identifier: str) -> ModelInvocationJob:
        if job_identifier in self.model_invocation_jobs:
            return self.model_invocation_jobs[job_identifier]
        for j in self.model_invocation_jobs.values():
            if j.job_name == job_identifier or j.job_id == job_identifier:
                return j
        raise ResourceNotFoundException(
            f"Could not find model invocation job {job_identifier}"
        )

    def get_model_invocation_job(self, job_identifier: str) -> dict[str, Any]:
        job = self._find_model_invocation_job(job_identifier)
        return job.to_dict()

    def stop_model_invocation_job(self, job_identifier: str) -> None:
        job = self._find_model_invocation_job(job_identifier)
        job.status = "Stopped"
        job.last_modified_time = _iso_now()

    @paginate(pagination_model=PAGINATION_MODEL)
    def list_model_invocation_jobs(
        self,
        submit_time_after: Optional[str] = None,
        submit_time_before: Optional[str] = None,
        status_equals: Optional[str] = None,
        name_contains: Optional[str] = None,
        sort_by: Optional[str] = None,
        sort_order: Optional[str] = None,
    ) -> list[ModelInvocationJob]:
        results = list(self.model_invocation_jobs.values())
        if name_contains:
            results = [r for r in results if name_contains in r.job_name]
        if status_equals:
            results = [r for r in results if r.status == status_equals]
        return results

    # -------------------------------------------------------------------
    # Foundation Models (read-only catalog)
    # -------------------------------------------------------------------

    def get_foundation_model(self, model_identifier: str) -> dict[str, Any]:
        if model_identifier in self.foundation_models:
            return {"modelDetails": self.foundation_models[model_identifier].to_dict()}
        # Try matching by ARN
        for fm in self.foundation_models.values():
            if fm.model_arn == model_identifier:
                return {"modelDetails": fm.to_dict()}
        raise ResourceNotFoundException(
            f"Could not find foundation model {model_identifier}"
        )

    def list_foundation_models(
        self,
        by_provider: Optional[str] = None,
        by_customization_type: Optional[str] = None,
        by_output_modality: Optional[str] = None,
        by_inference_type: Optional[str] = None,
    ) -> list[dict[str, Any]]:
        results = list(self.foundation_models.values())
        if by_provider:
            results = [r for r in results if r.provider_name == by_provider]
        if by_output_modality:
            results = [r for r in results if by_output_modality in r.output_modalities]
        if by_inference_type:
            results = [r for r in results if by_inference_type in r.inference_types_supported]
        return [r.summary() for r in results]

    # -------------------------------------------------------------------
    # Marketplace Model Endpoints
    # -------------------------------------------------------------------

    def create_marketplace_model_endpoint(
        self,
        model_source_identifier: str,
        endpoint_config: dict[str, Any],
        endpoint_name: Optional[str] = None,
        accept_eula: bool = False,
        tags: Optional[list[dict[str, str]]] = None,
    ) -> dict[str, Any]:
        ep = MarketplaceModelEndpoint(
            model_source_identifier=model_source_identifier,
            endpoint_config=endpoint_config,
            region_name=self.region_name,
            account_id=self.account_id,
            endpoint_name=endpoint_name,
            accept_eula=accept_eula,
        )
        self.marketplace_model_endpoints[ep.endpoint_arn] = ep
        if tags:
            self.tag_resource(ep.endpoint_arn, tags)
        return {"marketplaceModelEndpoint": ep.to_dict()}

    def _find_marketplace_endpoint(self, endpoint_arn: str) -> MarketplaceModelEndpoint:
        if endpoint_arn in self.marketplace_model_endpoints:
            return self.marketplace_model_endpoints[endpoint_arn]
        raise ResourceNotFoundException(
            f"Could not find marketplace model endpoint {endpoint_arn}"
        )

    def get_marketplace_model_endpoint(self, endpoint_arn: str) -> dict[str, Any]:
        ep = self._find_marketplace_endpoint(endpoint_arn)
        return {"marketplaceModelEndpoint": ep.to_dict()}

    def update_marketplace_model_endpoint(
        self,
        endpoint_arn: str,
        endpoint_config: dict[str, Any],
    ) -> dict[str, Any]:
        ep = self._find_marketplace_endpoint(endpoint_arn)
        ep.endpoint_config = endpoint_config
        ep.updated_at = _iso_now()
        return {"marketplaceModelEndpoint": ep.to_dict()}

    def delete_marketplace_model_endpoint(self, endpoint_arn: str) -> None:
        self._find_marketplace_endpoint(endpoint_arn)
        del self.marketplace_model_endpoints[endpoint_arn]

    def register_marketplace_model_endpoint(
        self,
        endpoint_identifier: str,
        model_source_identifier: str,
    ) -> dict[str, Any]:
        ep = self._find_marketplace_endpoint(endpoint_identifier)
        ep.registered = True
        ep.model_source_identifier = model_source_identifier
        return {"marketplaceModelEndpoint": ep.to_dict()}

    def deregister_marketplace_model_endpoint(self, endpoint_arn: str) -> None:
        ep = self._find_marketplace_endpoint(endpoint_arn)
        ep.registered = False

    @paginate(pagination_model=PAGINATION_MODEL)
    def list_marketplace_model_endpoints(
        self,
        model_source_equals: Optional[str] = None,
    ) -> list[MarketplaceModelEndpoint]:
        results = list(self.marketplace_model_endpoints.values())
        if model_source_equals:
            results = [r for r in results if r.model_source_identifier == model_source_equals]
        return results

    # -------------------------------------------------------------------
    # Prompt Routers
    # -------------------------------------------------------------------

    def create_prompt_router(
        self,
        prompt_router_name: str,
        models: list[dict[str, Any]],
        routing_criteria: dict[str, Any],
        fallback_model: dict[str, Any],
        description: Optional[str] = None,
        tags: Optional[list[dict[str, str]]] = None,
    ) -> str:
        pr = PromptRouter(
            prompt_router_name=prompt_router_name,
            models=models,
            routing_criteria=routing_criteria,
            fallback_model=fallback_model,
            region_name=self.region_name,
            account_id=self.account_id,
            description=description,
        )
        self.prompt_routers[pr.prompt_router_arn] = pr
        if tags:
            self.tag_resource(pr.prompt_router_arn, tags)
        return pr.prompt_router_arn

    def _find_prompt_router(self, prompt_router_arn: str) -> "PromptRouter":
        if prompt_router_arn in self.prompt_routers:
            return self.prompt_routers[prompt_router_arn]
        # URL path parsing may extract just the ID suffix; search by ARN suffix
        for arn, router in self.prompt_routers.items():
            if arn.endswith(f"/{prompt_router_arn}") or arn == prompt_router_arn:
                return router
        raise ResourceNotFoundException(
            f"Could not find prompt router {prompt_router_arn}"
        )

    def get_prompt_router(self, prompt_router_arn: str) -> dict[str, Any]:
        return self._find_prompt_router(prompt_router_arn).to_dict()

    def delete_prompt_router(self, prompt_router_arn: str) -> None:
        router = self._find_prompt_router(prompt_router_arn)
        del self.prompt_routers[router.prompt_router_arn]

    @paginate(pagination_model=PAGINATION_MODEL)
    def list_prompt_routers(
        self,
        type_filter: Optional[str] = None,
    ) -> list[PromptRouter]:
        results = list(self.prompt_routers.values())
        if type_filter:
            results = [r for r in results if r.type == type_filter]
        return results

    # -------------------------------------------------------------------
    # Custom Model Deployments
    # -------------------------------------------------------------------

    def create_custom_model_deployment(
        self,
        model_deployment_name: str,
        model_id: str,
    ) -> dict[str, Any]:
        dep = CustomModelDeployment(
            model_deployment_name=model_deployment_name,
            model_id=model_id,
            region_name=self.region_name,
            account_id=self.account_id,
        )
        self.custom_model_deployments[dep.deployment_id] = dep
        return {
            "customModelDeploymentArn": dep.deployment_arn,
        }

    def _find_deployment(self, identifier: str) -> CustomModelDeployment:
        if identifier in self.custom_model_deployments:
            return self.custom_model_deployments[identifier]
        for d in self.custom_model_deployments.values():
            if d.deployment_arn == identifier:
                return d
        raise ResourceNotFoundException(
            f"Could not find custom model deployment {identifier}"
        )

    def get_custom_model_deployment(self, identifier: str) -> dict[str, Any]:
        dep = self._find_deployment(identifier)
        return dep.to_dict()

    def update_custom_model_deployment(
        self,
        identifier: str,
        auto_scaling_config: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        dep = self._find_deployment(identifier)
        dep.last_modified_time = _iso_now()
        return {"customModelDeploymentArn": dep.deployment_arn}

    def delete_custom_model_deployment(self, identifier: str) -> None:
        dep = self._find_deployment(identifier)
        del self.custom_model_deployments[dep.deployment_id]

    @paginate(pagination_model=PAGINATION_MODEL)
    def list_custom_model_deployments(self) -> list[CustomModelDeployment]:
        return list(self.custom_model_deployments.values())

    # -------------------------------------------------------------------
    # Foundation Model Agreements (stub)
    # -------------------------------------------------------------------

    def create_foundation_model_agreement(
        self,
        model_id: str,
        offer_token: Optional[str] = None,
    ) -> dict[str, Any]:
        return {"modelId": model_id, "offerToken": offer_token or ""}

    def delete_foundation_model_agreement(
        self,
        model_id: str,
    ) -> dict[str, Any]:
        return {"modelId": model_id}

    def list_foundation_model_agreement_offers(
        self,
        model_id: str,
    ) -> dict[str, Any]:
        return {"modelId": model_id, "offers": []}

    def get_foundation_model_availability(
        self,
        model_id: str,
    ) -> dict[str, Any]:
        return {
            "modelId": model_id,
            "agreementAvailability": {"status": "AVAILABLE"},
        }

    # -------------------------------------------------------------------
    # Enforced Guardrail Configuration (stub)
    # -------------------------------------------------------------------

    def put_enforced_guardrail_configuration(
        self,
        config_id: str,
        guardrail_identifier: str,
        guardrail_version: Optional[str] = None,
    ) -> dict[str, Any]:
        self.enforced_guardrail_configs[config_id] = {
            "configId": config_id,
            "guardrailIdentifier": guardrail_identifier,
            "guardrailVersion": guardrail_version or "DRAFT",
        }
        return self.enforced_guardrail_configs[config_id]

    def delete_enforced_guardrail_configuration(self, config_id: str) -> None:
        if config_id in self.enforced_guardrail_configs:
            del self.enforced_guardrail_configs[config_id]

    def list_enforced_guardrails_configuration(self) -> list[dict[str, Any]]:
        return list(self.enforced_guardrail_configs.values())

    # -------------------------------------------------------------------
    # Use Case for Model Access (stub)
    # -------------------------------------------------------------------

    def get_use_case_for_model_access(self) -> dict[str, Any]:
        return self.use_case_for_model_access or {}

    def put_use_case_for_model_access(
        self, use_cases: Optional[list[dict[str, Any]]] = None
    ) -> dict[str, Any]:
        self.use_case_for_model_access = {"useCases": use_cases or []}
        return self.use_case_for_model_access

    # -------------------------------------------------------------------
    # Automated Reasoning Policies
    # -------------------------------------------------------------------

    def create_automated_reasoning_policy(
        self,
        name: str,
        policy_type: str,
        description: Optional[str] = None,
        rules: Optional[list[dict[str, Any]]] = None,
        tags: Optional[list[dict[str, str]]] = None,
    ) -> dict[str, Any]:
        policy = AutomatedReasoningPolicy(
            name=name,
            policy_type=policy_type,
            region_name=self.region_name,
            account_id=self.account_id,
            description=description,
            rules=rules,
        )
        self.automated_reasoning_policies[policy.policy_arn] = policy
        if tags:
            self.tag_resource(policy.policy_arn, tags)
        return policy.to_dict()

    def _find_ar_policy(self, policy_arn: str) -> AutomatedReasoningPolicy:
        if policy_arn in self.automated_reasoning_policies:
            return self.automated_reasoning_policies[policy_arn]
        # URL path parsing may extract just the ID suffix; search by ARN suffix
        for arn, policy in self.automated_reasoning_policies.items():
            if arn.endswith(f"/{policy_arn}") or arn == policy_arn:
                return policy
        raise ResourceNotFoundException(
            f"Could not find automated reasoning policy {policy_arn}"
        )

    def get_automated_reasoning_policy(self, policy_arn: str) -> dict[str, Any]:
        return self._find_ar_policy(policy_arn).to_dict()

    def update_automated_reasoning_policy(
        self,
        policy_arn: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        rules: Optional[list[dict[str, Any]]] = None,
    ) -> dict[str, Any]:
        policy = self._find_ar_policy(policy_arn)
        if name:
            policy.name = name
        if description is not None:
            policy.description = description
        if rules is not None:
            policy.rules = rules
        policy.updated_at = _iso_now()
        return policy.to_dict()

    def delete_automated_reasoning_policy(self, policy_arn: str) -> None:
        policy = self._find_ar_policy(policy_arn)
        del self.automated_reasoning_policies[policy.policy_arn]

    @paginate(pagination_model=PAGINATION_MODEL)
    def list_automated_reasoning_policies(self) -> list[AutomatedReasoningPolicy]:
        return list(self.automated_reasoning_policies.values())

    def create_automated_reasoning_policy_version(
        self,
        policy_arn: str,
        description: Optional[str] = None,
    ) -> dict[str, Any]:
        policy = self._find_ar_policy(policy_arn)
        policy.version += 1
        policy.updated_at = _iso_now()
        return {
            "policyArn": policy.policy_arn,
            "version": policy.version,
            "status": policy.status,
        }

    def export_automated_reasoning_policy_version(
        self,
        policy_arn: str,
    ) -> dict[str, Any]:
        policy = self._find_ar_policy(policy_arn)
        return {
            "policyArn": policy.policy_arn,
            "version": policy.version,
            "rules": policy.rules,
        }

    # Automated Reasoning Policy Test Cases

    def create_automated_reasoning_policy_test_case(
        self,
        policy_arn: str,
        test_case_name: Optional[str] = None,
        description: Optional[str] = None,
        input_text: Optional[str] = None,
        expected_result: Optional[str] = None,
    ) -> dict[str, Any]:
        policy = self._find_ar_policy(policy_arn)
        test_case_id = str(uuid.uuid4())[:12]
        test_case = {
            "testCaseId": test_case_id,
            "policyArn": policy_arn,
            "name": test_case_name or f"test-{test_case_id}",
            "description": description or "",
            "inputText": input_text or "",
            "expectedResult": expected_result or "",
            "createdAt": _iso_now(),
        }
        policy.test_cases[test_case_id] = test_case
        return test_case

    def get_automated_reasoning_policy_test_case(
        self,
        policy_arn: str,
        test_case_id: str,
    ) -> dict[str, Any]:
        policy = self._find_ar_policy(policy_arn)
        if test_case_id not in policy.test_cases:
            raise ResourceNotFoundException(f"Test case {test_case_id} not found")
        return policy.test_cases[test_case_id]

    def update_automated_reasoning_policy_test_case(
        self,
        policy_arn: str,
        test_case_id: str,
        test_case_name: Optional[str] = None,
        description: Optional[str] = None,
        input_text: Optional[str] = None,
        expected_result: Optional[str] = None,
    ) -> dict[str, Any]:
        policy = self._find_ar_policy(policy_arn)
        if test_case_id not in policy.test_cases:
            raise ResourceNotFoundException(f"Test case {test_case_id} not found")
        tc = policy.test_cases[test_case_id]
        if test_case_name:
            tc["name"] = test_case_name
        if description is not None:
            tc["description"] = description
        if input_text is not None:
            tc["inputText"] = input_text
        if expected_result is not None:
            tc["expectedResult"] = expected_result
        return tc

    def delete_automated_reasoning_policy_test_case(
        self,
        policy_arn: str,
        test_case_id: str,
    ) -> None:
        policy = self._find_ar_policy(policy_arn)
        if test_case_id not in policy.test_cases:
            raise ResourceNotFoundException(f"Test case {test_case_id} not found")
        del policy.test_cases[test_case_id]

    def list_automated_reasoning_policy_test_cases(
        self,
        policy_arn: str,
    ) -> list[dict[str, Any]]:
        policy = self._find_ar_policy(policy_arn)
        return list(policy.test_cases.values())

    # Automated Reasoning Policy Build Workflows

    def start_automated_reasoning_policy_build_workflow(
        self,
        policy_arn: str,
        build_workflow_type: str,
    ) -> dict[str, Any]:
        policy = self._find_ar_policy(policy_arn)
        build_workflow_id = str(uuid.uuid4())[:12]
        workflow = {
            "buildWorkflowId": build_workflow_id,
            "policyArn": policy_arn,
            "type": build_workflow_type,
            "status": "InProgress",
            "createdAt": _iso_now(),
        }
        policy.build_workflows[build_workflow_id] = workflow
        return workflow

    def get_automated_reasoning_policy_build_workflow(
        self,
        policy_arn: str,
        build_workflow_id: str,
    ) -> dict[str, Any]:
        policy = self._find_ar_policy(policy_arn)
        if build_workflow_id not in policy.build_workflows:
            raise ResourceNotFoundException(f"Build workflow {build_workflow_id} not found")
        return policy.build_workflows[build_workflow_id]

    def cancel_automated_reasoning_policy_build_workflow(
        self,
        policy_arn: str,
        build_workflow_id: str,
    ) -> None:
        policy = self._find_ar_policy(policy_arn)
        if build_workflow_id not in policy.build_workflows:
            raise ResourceNotFoundException(f"Build workflow {build_workflow_id} not found")
        policy.build_workflows[build_workflow_id]["status"] = "Cancelled"

    def delete_automated_reasoning_policy_build_workflow(
        self,
        policy_arn: str,
        build_workflow_id: str,
    ) -> None:
        policy = self._find_ar_policy(policy_arn)
        if build_workflow_id not in policy.build_workflows:
            raise ResourceNotFoundException(f"Build workflow {build_workflow_id} not found")
        del policy.build_workflows[build_workflow_id]

    def list_automated_reasoning_policy_build_workflows(
        self,
        policy_arn: str,
    ) -> list[dict[str, Any]]:
        policy = self._find_ar_policy(policy_arn)
        return list(policy.build_workflows.values())

    def get_automated_reasoning_policy_build_workflow_result_assets(
        self,
        policy_arn: str,
        build_workflow_id: str,
    ) -> dict[str, Any]:
        policy = self._find_ar_policy(policy_arn)
        if build_workflow_id not in policy.build_workflows:
            raise ResourceNotFoundException(f"Build workflow {build_workflow_id} not found")
        return {"assets": []}

    def get_automated_reasoning_policy_annotations(
        self,
        policy_arn: str,
        build_workflow_id: str,
    ) -> dict[str, Any]:
        policy = self._find_ar_policy(policy_arn)
        if build_workflow_id not in policy.build_workflows:
            raise ResourceNotFoundException(f"Build workflow {build_workflow_id} not found")
        return {"annotations": []}

    def update_automated_reasoning_policy_annotations(
        self,
        policy_arn: str,
        build_workflow_id: str,
        annotations: Optional[list[dict[str, Any]]] = None,
    ) -> dict[str, Any]:
        policy = self._find_ar_policy(policy_arn)
        if build_workflow_id not in policy.build_workflows:
            raise ResourceNotFoundException(f"Build workflow {build_workflow_id} not found")
        return {"annotations": annotations or []}

    def get_automated_reasoning_policy_next_scenario(
        self,
        policy_arn: str,
        build_workflow_id: str,
    ) -> dict[str, Any]:
        policy = self._find_ar_policy(policy_arn)
        if build_workflow_id not in policy.build_workflows:
            raise ResourceNotFoundException(f"Build workflow {build_workflow_id} not found")
        return {"scenario": None}

    def get_automated_reasoning_policy_test_result(
        self,
        policy_arn: str,
        build_workflow_id: str,
        test_case_id: str,
    ) -> dict[str, Any]:
        policy = self._find_ar_policy(policy_arn)
        if build_workflow_id not in policy.build_workflows:
            raise ResourceNotFoundException(f"Build workflow {build_workflow_id} not found")
        return {
            "testCaseId": test_case_id,
            "buildWorkflowId": build_workflow_id,
            "status": "Passed",
        }

    def list_automated_reasoning_policy_test_results(
        self,
        policy_arn: str,
        build_workflow_id: str,
    ) -> dict[str, Any]:
        policy = self._find_ar_policy(policy_arn)
        if build_workflow_id not in policy.build_workflows:
            raise ResourceNotFoundException(f"Build workflow {build_workflow_id} not found")
        return {"testResults": []}

    def start_automated_reasoning_policy_test_workflow(
        self,
        policy_arn: str,
        build_workflow_id: str,
    ) -> dict[str, Any]:
        policy = self._find_ar_policy(policy_arn)
        if build_workflow_id not in policy.build_workflows:
            raise ResourceNotFoundException(f"Build workflow {build_workflow_id} not found")
        return {
            "policyArn": policy_arn,
            "buildWorkflowId": build_workflow_id,
            "status": "InProgress",
        }


bedrock_backends = BackendDict(BedrockBackend, "bedrock")
