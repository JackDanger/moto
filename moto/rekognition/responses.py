import json

from moto.core.common_types import TYPE_RESPONSE
from moto.core.responses import BaseResponse

from .models import RekognitionBackend, rekognition_backends


class RekognitionResponse(BaseResponse):
    """Handler for Rekognition requests and responses."""

    def __init__(self) -> None:
        super().__init__(service_name="rekognition")

    @property
    def rekognition_backend(self) -> RekognitionBackend:
        return rekognition_backends[self.current_account][self.region]

    def _get_body(self) -> dict:
        return json.loads(self.body)

    # ---- Collections ----

    def create_collection(self) -> str:
        body = self._get_body()
        return json.dumps(self.rekognition_backend.create_collection(body["CollectionId"]))

    def delete_collection(self) -> str:
        body = self._get_body()
        return json.dumps(self.rekognition_backend.delete_collection(body["CollectionId"]))

    def describe_collection(self) -> str:
        body = self._get_body()
        return json.dumps(self.rekognition_backend.describe_collection(body["CollectionId"]))

    def list_collections(self) -> str:
        body = self._get_body()
        return json.dumps(self.rekognition_backend.list_collections(
            max_results=body.get("MaxResults", 4096), next_token=body.get("NextToken")))

    def index_faces(self) -> str:
        body = self._get_body()
        return json.dumps(self.rekognition_backend.index_faces(
            collection_id=body["CollectionId"], image=body["Image"],
            external_image_id=body.get("ExternalImageId"),
            max_faces=body.get("MaxFaces", 20),
            quality_filter=body.get("QualityFilter", "AUTO"),
            detection_attributes=body.get("DetectionAttributes")))

    def list_faces(self) -> str:
        body = self._get_body()
        return json.dumps(self.rekognition_backend.list_faces(
            collection_id=body["CollectionId"],
            max_results=body.get("MaxResults", 4096),
            next_token=body.get("NextToken")))

    def delete_faces(self) -> str:
        body = self._get_body()
        return json.dumps(self.rekognition_backend.delete_faces(
            collection_id=body["CollectionId"], face_ids=body["FaceIds"]))

    def search_faces(self) -> str:
        body = self._get_body()
        return json.dumps(self.rekognition_backend.search_faces(
            collection_id=body["CollectionId"], face_id=body["FaceId"],
            max_faces=body.get("MaxFaces", 80),
            face_match_threshold=body.get("FaceMatchThreshold", 80.0)))

    def search_faces_by_image(self) -> str:
        body = self._get_body()
        return json.dumps(self.rekognition_backend.search_faces_by_image(
            collection_id=body["CollectionId"], image=body["Image"],
            max_faces=body.get("MaxFaces", 80),
            face_match_threshold=body.get("FaceMatchThreshold", 80.0)))

    # ---- Projects ----

    def create_project(self) -> str:
        body = self._get_body()
        return json.dumps(self.rekognition_backend.create_project(body["ProjectName"]))

    def describe_projects(self) -> str:
        body = self._get_body()
        return json.dumps(self.rekognition_backend.describe_projects(
            project_names=body.get("ProjectNames"),
            max_results=body.get("MaxResults", 100),
            next_token=body.get("NextToken")))

    def delete_project(self) -> str:
        body = self._get_body()
        return json.dumps(self.rekognition_backend.delete_project(body["ProjectArn"]))

    def create_project_version(self) -> str:
        body = self._get_body()
        return json.dumps(self.rekognition_backend.create_project_version(
            project_arn=body["ProjectArn"], version_name=body["VersionName"],
            output_config=body["OutputConfig"],
            training_data=body.get("TrainingData"),
            testing_data=body.get("TestingData"),
            version_description=body.get("VersionDescription")))

    def describe_project_versions(self) -> str:
        body = self._get_body()
        return json.dumps(self.rekognition_backend.describe_project_versions(
            project_arn=body["ProjectArn"],
            version_names=body.get("VersionNames"),
            max_results=body.get("MaxResults", 100),
            next_token=body.get("NextToken")))

    def delete_project_version(self) -> str:
        body = self._get_body()
        return json.dumps(self.rekognition_backend.delete_project_version(body["ProjectVersionArn"]))

    def start_project_version(self) -> str:
        body = self._get_body()
        return json.dumps(self.rekognition_backend.start_project_version(
            project_version_arn=body["ProjectVersionArn"],
            min_inference_units=body["MinInferenceUnits"],
            max_inference_units=body.get("MaxInferenceUnits")))

    def stop_project_version(self) -> str:
        body = self._get_body()
        return json.dumps(self.rekognition_backend.stop_project_version(body["ProjectVersionArn"]))

    # ---- Datasets ----

    def create_dataset(self) -> str:
        body = self._get_body()
        return json.dumps(self.rekognition_backend.create_dataset(
            project_arn=body["ProjectArn"], dataset_type=body["DatasetType"],
            dataset_source=body.get("DatasetSource")))

    def describe_dataset(self) -> str:
        body = self._get_body()
        return json.dumps(self.rekognition_backend.describe_dataset(body["DatasetArn"]))

    def delete_dataset(self) -> str:
        body = self._get_body()
        return json.dumps(self.rekognition_backend.delete_dataset(body["DatasetArn"]))

    def list_dataset_entries(self) -> str:
        body = self._get_body()
        return json.dumps(self.rekognition_backend.list_dataset_entries(
            dataset_arn=body["DatasetArn"],
            contains_labels=body.get("ContainsLabels"),
            labeled=body.get("Labeled"),
            source_ref_contains=body.get("SourceRefContains"),
            has_errors=body.get("HasErrors"),
            max_results=body.get("MaxResults", 100),
            next_token=body.get("NextToken")))

    def list_dataset_labels(self) -> str:
        body = self._get_body()
        return json.dumps(self.rekognition_backend.list_dataset_labels(
            dataset_arn=body["DatasetArn"],
            max_results=body.get("MaxResults", 100),
            next_token=body.get("NextToken")))

    # ---- Stream Processors ----

    def create_stream_processor(self) -> str:
        body = self._get_body()
        return json.dumps(self.rekognition_backend.create_stream_processor(
            name=body["Name"], input_config=body["Input"],
            output_config=body["Output"], role_arn=body["RoleArn"],
            settings=body["Settings"],
            data_sharing_preference=body.get("DataSharingPreference"),
            regions_of_interest=body.get("RegionsOfInterest"),
            notification_channel=body.get("NotificationChannel"),
            kms_key_id=body.get("KmsKeyId"), tags=body.get("Tags")))

    def describe_stream_processor(self) -> str:
        body = self._get_body()
        return json.dumps(self.rekognition_backend.describe_stream_processor(body["Name"]))

    def delete_stream_processor(self) -> str:
        body = self._get_body()
        return json.dumps(self.rekognition_backend.delete_stream_processor(body["Name"]))

    def list_stream_processors(self) -> str:
        body = self._get_body()
        return json.dumps(self.rekognition_backend.list_stream_processors(
            max_results=body.get("MaxResults", 100),
            next_token=body.get("NextToken")))

    def start_stream_processor(self) -> str:
        body = self._get_body()
        return json.dumps(self.rekognition_backend.start_stream_processor(
            name=body["Name"],
            start_selector=body.get("StartSelector"),
            stop_selector=body.get("StopSelector")))

    def stop_stream_processor(self) -> str:
        body = self._get_body()
        return json.dumps(self.rekognition_backend.stop_stream_processor(body["Name"]))

    # ---- Existing operations (preserved) ----

    def get_face_search(self) -> str:
        (job_status, status_message, video_metadata, persons,
         next_token, text_model_version) = self.rekognition_backend.get_face_search()
        return json.dumps({
            "JobStatus": job_status, "StatusMessage": status_message,
            "VideoMetadata": video_metadata, "Persons": persons,
            "NextToken": next_token, "TextModelVersion": text_model_version,
        })

    def get_text_detection(self) -> str:
        (job_status, status_message, video_metadata, text_detections,
         next_token, text_model_version) = self.rekognition_backend.get_text_detection()
        return json.dumps({
            "JobStatus": job_status, "StatusMessage": status_message,
            "VideoMetadata": video_metadata, "TextDetections": text_detections,
            "NextToken": next_token, "TextModelVersion": text_model_version,
        })

    def compare_faces(self) -> str:
        (face_matches, src_orient, tgt_orient, unmatched,
         src_face) = self.rekognition_backend.compare_faces()
        return json.dumps({
            "FaceMatches": face_matches,
            "SourceImageOrientationCorrection": src_orient,
            "TargetImageOrientationCorrection": tgt_orient,
            "UnmatchedFaces": unmatched, "SourceImageFace": src_face,
        })

    def detect_labels(self) -> str:
        (labels, image_properties, label_model_version) = self.rekognition_backend.detect_labels()
        return json.dumps({
            "Labels": labels, "ImageProperties": image_properties,
            "LabelModelVersion": label_model_version,
        })

    def detect_text(self) -> str:
        (text_detections, text_model_version) = self.rekognition_backend.detect_text()
        return json.dumps({"TextDetections": text_detections, "TextModelVersion": text_model_version})

    def detect_custom_labels(self) -> str:
        (custom_labels,) = self.rekognition_backend.detect_custom_labels()
        return json.dumps({"CustomLabels": custom_labels})

    def start_face_search(self) -> TYPE_RESPONSE:
        headers = {"Content-Type": "application/x-amz-json-1.1"}
        job_id = self.rekognition_backend.start_face_search()
        return 200, headers, ('{"JobId":"' + job_id + '"}').encode()

    def start_text_detection(self) -> TYPE_RESPONSE:
        headers = {"Content-Type": "application/x-amz-json-1.1"}
        job_id = self.rekognition_backend.start_text_detection()
        return 200, headers, ('{"JobId":"' + job_id + '"}').encode()
