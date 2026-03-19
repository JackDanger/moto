"""Handles incoming textract requests, invokes methods, returns responses."""

import json

from moto.core.responses import BaseResponse

from .models import TextractBackend, textract_backends


class TextractResponse(BaseResponse):
    """Handler for Textract requests and responses."""

    def __init__(self) -> None:
        super().__init__(service_name="textract")

    @property
    def textract_backend(self) -> TextractBackend:
        """Return backend instance specific for this region."""
        return textract_backends[self.current_account][self.region]

    def get_document_text_detection(self) -> str:
        params = json.loads(self.body)
        job_id = params.get("JobId")
        job = self.textract_backend.get_document_text_detection(job_id=job_id).to_dict()
        return json.dumps(job)

    def detect_document_text(self) -> str:
        result = self.textract_backend.detect_document_text()
        return json.dumps(result)

    def start_document_text_detection(self) -> str:
        params = json.loads(self.body)
        document_location = params.get("DocumentLocation")
        notification_channel = params.get("NotificationChannel")
        job_id = self.textract_backend.start_document_text_detection(
            document_location=document_location,
            notification_channel=notification_channel,
        )
        return json.dumps({"JobId": job_id})

    def start_document_analysis(self) -> str:
        params = json.loads(self.body)
        document_location = params.get("DocumentLocation")
        feature_types = params.get("FeatureTypes")
        job_id = self.textract_backend.start_document_analysis(
            document_location=document_location, feature_types=feature_types
        )
        return json.dumps({"JobId": job_id})

    def get_document_analysis(self) -> str:
        params = json.loads(self.body)
        job_id = params.get("JobId")
        max_results = params.get("MaxResults")
        next_token = params.get("NextToken")
        job = self.textract_backend.get_document_analysis(
            job_id=job_id, max_results=max_results, next_token=next_token
        ).to_dict()
        return json.dumps(job)

    def analyze_document(self) -> str:
        params = json.loads(self.body)
        document = params.get("Document")
        feature_types = params.get("FeatureTypes", [])
        result = self.textract_backend.analyze_document(
            document=document, feature_types=feature_types
        )
        return json.dumps(result)

    def analyze_expense(self) -> str:
        params = json.loads(self.body)
        document = params.get("Document")
        result = self.textract_backend.analyze_expense(document=document)
        return json.dumps(result)

    def analyze_id(self) -> str:
        params = json.loads(self.body)
        document_pages = params.get("DocumentPages", [])
        result = self.textract_backend.analyze_id(document_pages=document_pages)
        return json.dumps(result)

    def start_expense_analysis(self) -> str:
        params = json.loads(self.body)
        document_location = params.get("DocumentLocation")
        job_id = self.textract_backend.start_expense_analysis(
            document_location=document_location
        )
        return json.dumps({"JobId": job_id})

    def get_expense_analysis(self) -> str:
        params = json.loads(self.body)
        job_id = params.get("JobId")
        job = self.textract_backend.get_expense_analysis(job_id=job_id).to_dict()
        return json.dumps(job)

    def start_lending_analysis(self) -> str:
        params = json.loads(self.body)
        document_location = params.get("DocumentLocation")
        job_id = self.textract_backend.start_lending_analysis(
            document_location=document_location
        )
        return json.dumps({"JobId": job_id})

    def get_lending_analysis(self) -> str:
        params = json.loads(self.body)
        job_id = params.get("JobId")
        job = self.textract_backend.get_lending_analysis(job_id=job_id).to_dict()
        return json.dumps(job)

    def get_lending_analysis_summary(self) -> str:
        params = json.loads(self.body)
        job_id = params.get("JobId")
        job = self.textract_backend.get_lending_analysis_summary(job_id=job_id).to_dict()
        return json.dumps(job)

    def create_adapter(self) -> str:
        params = json.loads(self.body)
        adapter_id = self.textract_backend.create_adapter(
            adapter_name=params.get("AdapterName", ""),
            feature_types=params.get("FeatureTypes", []),
            description=params.get("Description", ""),
            auto_update=params.get("AutoUpdate", "DISABLED"),
            tags=params.get("Tags"),
        )
        return json.dumps({"AdapterId": adapter_id})

    def delete_adapter(self) -> str:
        params = json.loads(self.body)
        self.textract_backend.delete_adapter(adapter_id=params.get("AdapterId", ""))
        return json.dumps({})

    def get_adapter(self) -> str:
        params = json.loads(self.body)
        adapter = self.textract_backend.get_adapter(adapter_id=params.get("AdapterId", ""))
        result = adapter.to_dict()
        result["Tags"] = adapter.tags
        return json.dumps(result)

    def update_adapter(self) -> str:
        params = json.loads(self.body)
        adapter = self.textract_backend.update_adapter(
            adapter_id=params.get("AdapterId", ""),
            adapter_name=params.get("AdapterName"),
            description=params.get("Description"),
            auto_update=params.get("AutoUpdate"),
        )
        return json.dumps({"AdapterId": adapter.adapter_id})

    def list_adapters(self) -> str:
        params = json.loads(self.body)
        result = self.textract_backend.list_adapters(
            max_results=params.get("MaxResults"),
            next_token=params.get("NextToken"),
            after_creation_time=params.get("AfterCreationTime"),
            before_creation_time=params.get("BeforeCreationTime"),
        )
        return json.dumps(result)

    def create_adapter_version(self) -> str:
        params = json.loads(self.body)
        version = self.textract_backend.create_adapter_version(
            adapter_id=params.get("AdapterId", ""),
            dataset=params.get("DatasetConfig", {}),
            kms_key_id=params.get("KMSKeyId", ""),
            output_config=params.get("OutputConfig"),
            tags=params.get("Tags"),
        )
        return json.dumps({"AdapterId": params.get("AdapterId"), "AdapterVersion": version})

    def delete_adapter_version(self) -> str:
        params = json.loads(self.body)
        self.textract_backend.delete_adapter_version(
            adapter_id=params.get("AdapterId", ""),
            adapter_version=params.get("AdapterVersion", ""),
        )
        return json.dumps({})

    def get_adapter_version(self) -> str:
        params = json.loads(self.body)
        av = self.textract_backend.get_adapter_version(
            adapter_id=params.get("AdapterId", ""),
            adapter_version=params.get("AdapterVersion", ""),
        )
        result = av.to_dict()
        result["Tags"] = av.tags
        return json.dumps(result)

    def list_adapter_versions(self) -> str:
        params = json.loads(self.body)
        result = self.textract_backend.list_adapter_versions(
            adapter_id=params.get("AdapterId"),
            max_results=params.get("MaxResults"),
            next_token=params.get("NextToken"),
        )
        return json.dumps(result)

    def tag_resource(self) -> str:
        params = json.loads(self.body)
        self.textract_backend.tag_resource(
            resource_arn=params.get("ResourceARN", ""),
            tags=params.get("Tags", {}),
        )
        return json.dumps({})

    def untag_resource(self) -> str:
        params = json.loads(self.body)
        self.textract_backend.untag_resource(
            resource_arn=params.get("ResourceARN", ""),
            tag_keys=params.get("TagKeys", []),
        )
        return json.dumps({})

    def list_tags_for_resource(self) -> str:
        params = json.loads(self.body)
        tags = self.textract_backend.list_tags_for_resource(
            resource_arn=params.get("ResourceARN", "")
        )
        return json.dumps({"Tags": tags})
