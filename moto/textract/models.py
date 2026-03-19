import json
import time
from collections import defaultdict
from typing import Any, Optional

from moto.core.base_backend import BackendDict, BaseBackend
from moto.core.common_models import BaseModel
from moto.moto_api._internal import mock_random
from moto.sns import sns_backends
from moto.sns.exceptions import TopicNotFound

from .exceptions import (
    InvalidJobIdException,
    InvalidParameterException,
    ResourceNotFoundException,
)


class TextractJobStatus:
    in_progress = "IN_PROGRESS"
    succeeded = "SUCCEEDED"
    failed = "FAILED"
    partial_success = "PARTIAL_SUCCESS"


class TextractJob(BaseModel):
    def __init__(
        self, job: dict[str, Any], notification_channel: Optional[dict[str, str]] = None
    ):
        self.job = job
        self.notification_channel = notification_channel
        self.job_id = str(mock_random.uuid4())

    def to_dict(self) -> dict[str, Any]:
        return self.job

    def send_completion_notification(
        self, account_id: str, region_name: str, document_location: dict[str, Any]
    ) -> None:
        if not self.notification_channel:
            return

        topic_arn = self.notification_channel.get("SNSTopicArn")
        if not topic_arn:
            return

        # Convert document_location from {'S3Object': {'Bucket': '...', 'Name': '...'}} format
        # to {'S3Bucket': '...', 'S3ObjectName': '...'} format as per AWS docs
        s3_object = document_location.get("S3Object", {})
        doc_location = {
            "S3Bucket": s3_object.get("Bucket", ""),
            "S3ObjectName": s3_object.get("Name", ""),
        }

        notification = {
            "JobId": self.job_id,
            "Status": self.job["JobStatus"],
            "API": "StartDocumentTextDetection",
            "JobTag": "",  # Not implemented yet
            "Timestamp": int(time.time() * 1000),  # Convert to milliseconds
            "DocumentLocation": doc_location,
        }

        sns_backend = sns_backends[account_id][region_name]
        try:
            sns_backend.publish(
                message=json.dumps(notification),  # SNS requires message to be a string
                arn=topic_arn,
                subject="Amazon Textract Job Completion",
            )
        except TopicNotFound:
            pass


class TextractAdapter(BaseModel):
    def __init__(
        self,
        adapter_id: str,
        adapter_name: str,
        feature_types: list[str],
        description: str = "",
        auto_update: str = "DISABLED",
        tags: Optional[dict[str, str]] = None,
    ):
        self.adapter_id = adapter_id
        self.adapter_name = adapter_name
        self.feature_types = feature_types
        self.description = description
        self.auto_update = auto_update
        self.tags: dict[str, str] = tags or {}
        self.creation_time = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        self.versions: dict[str, "TextractAdapterVersion"] = {}
        self.arn = ""  # set after creation

    def to_dict(self) -> dict[str, Any]:
        return {
            "AdapterId": self.adapter_id,
            "AdapterName": self.adapter_name,
            "FeatureTypes": self.feature_types,
            "Description": self.description,
            "AutoUpdate": self.auto_update,
            "CreationTime": self.creation_time,
        }


class TextractAdapterVersion(BaseModel):
    def __init__(
        self,
        adapter_id: str,
        version: str,
        dataset: dict[str, Any],
        kms_key_id: str = "",
        output_config: Optional[dict[str, Any]] = None,
        tags: Optional[dict[str, str]] = None,
    ):
        self.adapter_id = adapter_id
        self.version = version
        self.dataset = dataset
        self.kms_key_id = kms_key_id
        self.output_config = output_config or {}
        self.tags: dict[str, str] = tags or {}
        self.status = "ACTIVE"
        self.creation_time = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

    def to_dict(self) -> dict[str, Any]:
        return {
            "AdapterId": self.adapter_id,
            "AdapterVersion": self.version,
            "Status": self.status,
            "CreationTime": self.creation_time,
        }


class TextractBackend(BaseBackend):
    """Implementation of Textract APIs."""

    JOB_STATUS = TextractJobStatus.succeeded
    PAGES = {"Pages": mock_random.randint(5, 500)}
    BLOCKS: list[dict[str, Any]] = []

    def __init__(self, region_name: str, account_id: str):
        super().__init__(region_name, account_id)
        self.async_text_detection_jobs: dict[str, TextractJob] = defaultdict()
        self.async_document_analysis_jobs: dict[str, TextractJob] = defaultdict()
        self.async_expense_analysis_jobs: dict[str, TextractJob] = defaultdict()
        self.async_lending_analysis_jobs: dict[str, TextractJob] = defaultdict()
        self.adapters: dict[str, TextractAdapter] = {}
        self.tagger: dict[str, dict[str, str]] = {}

    def get_document_text_detection(self, job_id: str) -> TextractJob:
        """
        Pagination has not yet been implemented
        """
        job = self.async_text_detection_jobs.get(job_id)
        if not job:
            raise InvalidJobIdException()
        return job

    def detect_document_text(self) -> dict[str, Any]:
        return {
            "Blocks": TextractBackend.BLOCKS,
            "DetectDocumentTextModelVersion": "1.0",
            "DocumentMetadata": {"Pages": TextractBackend.PAGES},
        }

    def start_document_text_detection(
        self,
        document_location: dict[str, Any],
        notification_channel: Optional[dict[str, str]] = None,
    ) -> str:
        """
        The following parameters have not yet been implemented: ClientRequestToken, JobTag, OutputConfig, KmsKeyID
        """
        if not document_location:
            raise InvalidParameterException()

        job = TextractJob(
            {
                "Blocks": TextractBackend.BLOCKS,
                "DetectDocumentTextModelVersion": "1.0",
                "DocumentMetadata": {"Pages": TextractBackend.PAGES},
                "JobStatus": TextractBackend.JOB_STATUS,
            },
            notification_channel=notification_channel,
        )

        self.async_text_detection_jobs[job.job_id] = job

        # Send completion notification since we're mocking an immediate completion
        job.send_completion_notification(
            self.account_id, self.region_name, document_location
        )

        return job.job_id

    def start_document_analysis(
        self, document_location: dict[str, Any], feature_types: list[str]
    ) -> str:
        """
        The following parameters have not yet been implemented: ClientRequestToken, JobTag, NotificationChannel, OutputConfig, KmsKeyID
        """
        if not document_location or not feature_types:
            raise InvalidParameterException()
        job_id = str(mock_random.uuid4())
        self.async_document_analysis_jobs[job_id] = TextractJob(
            {
                "Blocks": TextractBackend.BLOCKS,
                "DetectDocumentTextModelVersion": "1.0",
                "DocumentMetadata": {"Pages": TextractBackend.PAGES},
                "JobStatus": TextractBackend.JOB_STATUS,
            }
        )
        return job_id

    def get_document_analysis(
        self, job_id: str, max_results: Optional[int], next_token: Optional[str] = None
    ) -> TextractJob:
        job = self.async_document_analysis_jobs.get(job_id)
        if not job:
            raise InvalidJobIdException()
        return job

    # --- Synchronous document operations ---

    def analyze_document(
        self, document: dict[str, Any], feature_types: list[str]
    ) -> dict[str, Any]:
        return {
            "Blocks": TextractBackend.BLOCKS,
            "DocumentMetadata": {"Pages": TextractBackend.PAGES},
            "AnalyzeDocumentModelVersion": "1.0",
        }

    def analyze_expense(self, document: dict[str, Any]) -> dict[str, Any]:
        return {
            "DocumentMetadata": {"Pages": TextractBackend.PAGES},
            "ExpenseDocuments": [],
        }

    def analyze_id(self, document_pages: list[dict[str, Any]]) -> dict[str, Any]:
        return {
            "DocumentMetadata": {"Pages": TextractBackend.PAGES},
            "IdentityDocuments": [],
            "AnalyzeIDModelVersion": "1.0",
        }

    # --- Expense analysis async ---

    def start_expense_analysis(
        self, document_location: dict[str, Any]
    ) -> str:
        if not document_location:
            raise InvalidParameterException()
        job = TextractJob(
            {
                "Blocks": TextractBackend.BLOCKS,
                "DocumentMetadata": {"Pages": TextractBackend.PAGES},
                "ExpenseDocuments": [],
                "JobStatus": TextractBackend.JOB_STATUS,
            }
        )
        self.async_expense_analysis_jobs[job.job_id] = job
        return job.job_id

    def get_expense_analysis(self, job_id: str) -> TextractJob:
        job = self.async_expense_analysis_jobs.get(job_id)
        if not job:
            raise InvalidJobIdException()
        return job

    # --- Lending analysis async ---

    def start_lending_analysis(
        self, document_location: dict[str, Any]
    ) -> str:
        if not document_location:
            raise InvalidParameterException()
        job = TextractJob(
            {
                "DocumentMetadata": {"Pages": TextractBackend.PAGES},
                "Results": [],
                "JobStatus": TextractBackend.JOB_STATUS,
            }
        )
        self.async_lending_analysis_jobs[job.job_id] = job
        return job.job_id

    def get_lending_analysis(self, job_id: str) -> TextractJob:
        job = self.async_lending_analysis_jobs.get(job_id)
        if not job:
            raise InvalidJobIdException()
        return job

    def get_lending_analysis_summary(self, job_id: str) -> TextractJob:
        job = self.async_lending_analysis_jobs.get(job_id)
        if not job:
            raise InvalidJobIdException()
        return job

    # --- Adapter CRUD ---

    def _adapter_arn(self, adapter_id: str) -> str:
        return f"arn:aws:textract:{self.region_name}:{self.account_id}:adapter/{adapter_id}"

    def create_adapter(
        self,
        adapter_name: str,
        feature_types: list[str],
        description: str = "",
        auto_update: str = "DISABLED",
        tags: Optional[dict[str, str]] = None,
    ) -> str:
        adapter_id = str(mock_random.uuid4()).replace("-", "")[:12]
        adapter = TextractAdapter(
            adapter_id=adapter_id,
            adapter_name=adapter_name,
            feature_types=feature_types,
            description=description,
            auto_update=auto_update,
            tags=tags or {},
        )
        adapter.arn = self._adapter_arn(adapter_id)
        self.adapters[adapter_id] = adapter
        self.tagger[adapter.arn] = tags or {}
        return adapter_id

    def delete_adapter(self, adapter_id: str) -> None:
        if adapter_id not in self.adapters:
            raise ResourceNotFoundException(adapter_id)
        adapter = self.adapters.pop(adapter_id)
        self.tagger.pop(adapter.arn, None)

    def get_adapter(self, adapter_id: str) -> TextractAdapter:
        if adapter_id not in self.adapters:
            raise ResourceNotFoundException(adapter_id)
        return self.adapters[adapter_id]

    def update_adapter(
        self,
        adapter_id: str,
        adapter_name: Optional[str] = None,
        description: Optional[str] = None,
        auto_update: Optional[str] = None,
    ) -> TextractAdapter:
        adapter = self.get_adapter(adapter_id)
        if adapter_name is not None:
            adapter.adapter_name = adapter_name
        if description is not None:
            adapter.description = description
        if auto_update is not None:
            adapter.auto_update = auto_update
        return adapter

    def list_adapters(
        self,
        max_results: Optional[int] = None,
        next_token: Optional[str] = None,
        after_creation_time: Optional[str] = None,
        before_creation_time: Optional[str] = None,
    ) -> dict[str, Any]:
        adapters = list(self.adapters.values())
        return {
            "Adapters": [a.to_dict() for a in adapters],
        }

    # --- Adapter version CRUD ---

    def create_adapter_version(
        self,
        adapter_id: str,
        dataset: dict[str, Any],
        kms_key_id: str = "",
        output_config: Optional[dict[str, Any]] = None,
        tags: Optional[dict[str, str]] = None,
    ) -> str:
        adapter = self.get_adapter(adapter_id)
        version = str(len(adapter.versions) + 1)
        av = TextractAdapterVersion(
            adapter_id=adapter_id,
            version=version,
            dataset=dataset,
            kms_key_id=kms_key_id,
            output_config=output_config,
            tags=tags or {},
        )
        adapter.versions[version] = av
        return version

    def delete_adapter_version(self, adapter_id: str, adapter_version: str) -> None:
        adapter = self.get_adapter(adapter_id)
        if adapter_version not in adapter.versions:
            raise ResourceNotFoundException(f"{adapter_id}/{adapter_version}")
        del adapter.versions[adapter_version]

    def get_adapter_version(
        self, adapter_id: str, adapter_version: str
    ) -> TextractAdapterVersion:
        adapter = self.get_adapter(adapter_id)
        if adapter_version not in adapter.versions:
            raise ResourceNotFoundException(f"{adapter_id}/{adapter_version}")
        return adapter.versions[adapter_version]

    def list_adapter_versions(
        self,
        adapter_id: Optional[str] = None,
        max_results: Optional[int] = None,
        next_token: Optional[str] = None,
    ) -> dict[str, Any]:
        versions: list[dict[str, Any]] = []
        for aid, adapter in self.adapters.items():
            if adapter_id and aid != adapter_id:
                continue
            for av in adapter.versions.values():
                versions.append(av.to_dict())
        return {"AdapterVersions": versions}

    # --- Tagging ---

    def tag_resource(self, resource_arn: str, tags: dict[str, str]) -> None:
        existing = self.tagger.get(resource_arn, {})
        existing.update(tags)
        self.tagger[resource_arn] = existing

    def untag_resource(self, resource_arn: str, tag_keys: list[str]) -> None:
        existing = self.tagger.get(resource_arn, {})
        for key in tag_keys:
            existing.pop(key, None)
        self.tagger[resource_arn] = existing

    def list_tags_for_resource(self, resource_arn: str) -> dict[str, str]:
        return self.tagger.get(resource_arn, {})


textract_backends = BackendDict(TextractBackend, "textract")
