import re
from datetime import datetime, timedelta
from typing import Any, Optional

from moto.core.base_backend import BackendDict, BaseBackend
from moto.core.common_models import BaseModel
from moto.core.utils import utcnow
from moto.moto_api._internal import mock_random
from moto.moto_api._internal.managed_state_model import ManagedState

from .exceptions import BadRequestException, ConflictException


class BaseObject(BaseModel):
    def camelCase(self, key: str) -> str:
        words = []
        for word in key.split("_"):
            words.append(word.title())
        return "".join(words)

    def gen_response_object(self) -> dict[str, Any]:
        response_object: dict[str, Any] = {}
        for key, value in self.__dict__.items():
            if "_" in key:
                response_object[self.camelCase(key)] = value
            else:
                response_object[key[0].upper() + key[1:]] = value
        return response_object

    @property
    def response_object(self) -> dict[str, Any]:  # type: ignore[misc]
        return self.gen_response_object()


class FakeTranscriptionJob(BaseObject, ManagedState):
    def __init__(
        self,
        account_id: str,
        region_name: str,
        transcription_job_name: str,
        language_code: Optional[str],
        media_sample_rate_hertz: Optional[int],
        media_format: Optional[str],
        media: dict[str, str],
        output_bucket_name: Optional[str],
        output_key: Optional[str],
        output_encryption_kms_key_id: Optional[str],
        settings: Optional[dict[str, Any]],
        model_settings: Optional[dict[str, Optional[str]]],
        job_execution_settings: Optional[dict[str, Any]],
        content_redaction: Optional[dict[str, Any]],
        identify_language: Optional[bool],
        identify_multiple_languages: Optional[bool],
        language_options: Optional[list[str]],
        subtitles: Optional[dict[str, Any]],
    ):
        ManagedState.__init__(
            self,
            "transcribe::transcriptionjob",
            transitions=[
                (None, "QUEUED"),
                ("QUEUED", "IN_PROGRESS"),
                ("IN_PROGRESS", "COMPLETED"),
            ],
        )
        self._account_id = account_id
        self._region_name = region_name
        self.transcription_job_name = transcription_job_name
        self.language_code = language_code
        self.language_codes: Optional[list[dict[str, Any]]] = None
        self.media_sample_rate_hertz = media_sample_rate_hertz
        self.media_format = media_format
        self.media = media
        self.transcript: Optional[dict[str, str]] = None
        self.start_time: Optional[datetime] = None
        self.completion_time: Optional[datetime] = None
        self.creation_time = utcnow()
        self.failure_reason = None
        self.settings = settings or {
            "ChannelIdentification": False,
            "ShowAlternatives": False,
            "ShowSpeakerLabels": False,
        }
        self.model_settings = model_settings or {"LanguageModelName": None}
        self.job_execution_settings = job_execution_settings or {
            "AllowDeferredExecution": False,
            "DataAccessRoleArn": None,
        }
        self.content_redaction = content_redaction or {
            "RedactionType": None,
            "RedactionOutput": None,
        }
        self.identify_language = identify_language
        self.identify_multiple_languages = identify_multiple_languages
        self.language_options = language_options
        self.identified_language_score: Optional[float] = None
        self._output_bucket_name = output_bucket_name
        self.output_key = output_key
        self._output_encryption_kms_key_id = output_encryption_kms_key_id
        self.output_location_type = (
            "CUSTOMER_BUCKET" if self._output_bucket_name else "SERVICE_BUCKET"
        )
        self.subtitles = subtitles or {"Formats": [], "OutputStartIndex": 0}

    def response_object(self, response_type: str) -> dict[str, Any]:  # type: ignore
        response_field_dict = {
            "CREATE": [
                "TranscriptionJobName",
                "TranscriptionJobStatus",
                "LanguageCode",
                "LanguageCodes",
                "MediaFormat",
                "Media",
                "Settings",
                "StartTime",
                "CreationTime",
                "IdentifyLanguage",
                "IdentifyMultipleLanguages",
                "LanguageOptions",
                "JobExecutionSettings",
                "Subtitles",
            ],
            "GET": [
                "TranscriptionJobName",
                "TranscriptionJobStatus",
                "LanguageCode",
                "LanguageCodes",
                "MediaSampleRateHertz",
                "MediaFormat",
                "Media",
                "Settings",
                "Transcript",
                "StartTime",
                "CreationTime",
                "CompletionTime",
                "IdentifyLanguage",
                "IdentifyMultipleLanguages",
                "LanguageOptions",
                "IdentifiedLanguageScore",
                "Subtitles",
            ],
            "LIST": [
                "TranscriptionJobName",
                "CreationTime",
                "StartTime",
                "CompletionTime",
                "LanguageCode",
                "LanguageCodes",
                "TranscriptionJobStatus",
                "FailureReason",
                "IdentifyLanguage",
                "IdentifyMultipleLanguages",
                "IdentifiedLanguageScore",
                "OutputLocationType",
            ],
        }
        response_fields = response_field_dict[response_type]
        response_object = self.gen_response_object()
        response_object["TranscriptionJobStatus"] = self.status
        if response_type != "LIST":
            return {
                "TranscriptionJob": {
                    k: v
                    for k, v in response_object.items()
                    if k in response_fields and v is not None and v != [None]
                }
            }
        else:
            return {
                k: v
                for k, v in response_object.items()
                if k in response_fields and v is not None and v != [None]
            }

    def advance(self) -> None:
        old_status = self.status
        super().advance()
        new_status = self.status

        if old_status == new_status:
            return

        if new_status == "IN_PROGRESS":
            self.start_time = utcnow()
            if not self.media_sample_rate_hertz:
                self.media_sample_rate_hertz = 44100
            if not self.media_format:
                file_ext = self.media["MediaFileUri"].split(".")[-1].lower()
                self.media_format = (
                    file_ext if file_ext in ["mp3", "mp4", "wav", "flac"] else "mp3"
                )
            if self.identify_language:
                self.identified_language_score = 0.999645948
                # Simply identify first language passed in language_options
                # If none is set, default to "en-US"
                if self.language_options is not None and len(self.language_options) > 0:
                    self.language_code = self.language_options[0]
                else:
                    self.language_code = "en-US"
            if self.identify_multiple_languages:
                self.identified_language_score = 0.999645948
                # Identify first two languages passed in language_options
                # If none is set, default to "en-US"
                self.language_codes: list[dict[str, Any]] = []  # type: ignore[no-redef]
                if self.language_options is None or len(self.language_options) == 0:
                    self.language_codes.append(
                        {"LanguageCode": "en-US", "DurationInSeconds": 123.0}
                    )
                else:
                    self.language_codes.append(
                        {
                            "LanguageCode": self.language_options[0],
                            "DurationInSeconds": 123.0,
                        }
                    )
                    if len(self.language_options) > 1:
                        self.language_codes.append(
                            {
                                "LanguageCode": self.language_options[1],
                                "DurationInSeconds": 321.0,
                            }
                        )
        elif new_status == "COMPLETED":
            self.completion_time = utcnow() + timedelta(seconds=10)
            if self._output_bucket_name:
                remove_json_extension = re.compile("\\.json$")
                transcript_file_prefix = (
                    f"https://s3.{self._region_name}.amazonaws.com/"
                    f"{self._output_bucket_name}/"
                    f"{remove_json_extension.sub('', self.output_key or self.transcription_job_name)}"
                )
                self.output_location_type = "CUSTOMER_BUCKET"
            else:
                transcript_file_prefix = (
                    f"https://s3.{self._region_name}.amazonaws.com/"
                    f"aws-transcribe-{self._region_name}-prod/"
                    f"{self._account_id}/"
                    f"{self.transcription_job_name}/"
                    f"{mock_random.uuid4()}/"
                    "asrOutput"
                )
                self.output_location_type = "SERVICE_BUCKET"
            self.transcript = {"TranscriptFileUri": f"{transcript_file_prefix}.json"}
            self.subtitles["SubtitleFileUris"] = [
                f"{transcript_file_prefix}.{format}"
                for format in self.subtitles["Formats"]
            ]


class FakeVocabulary(BaseObject, ManagedState):
    def __init__(
        self,
        account_id: str,
        region_name: str,
        vocabulary_name: str,
        language_code: str,
        phrases: Optional[list[str]],
        vocabulary_file_uri: Optional[str],
    ):
        # Configured ManagedState
        super().__init__(
            "transcribe::vocabulary",
            transitions=[(None, "PENDING"), ("PENDING", "READY")],
        )
        # Configure internal properties
        self._region_name = region_name
        self.vocabulary_name = vocabulary_name
        self.language_code = language_code
        self.phrases = phrases
        self.vocabulary_file_uri = vocabulary_file_uri
        self.last_modified_time: Optional[datetime] = None
        self.failure_reason = None
        self.download_uri = f"https://s3.{region_name}.amazonaws.com/aws-transcribe-dictionary-model-{region_name}-prod/{account_id}/{vocabulary_name}/{mock_random.uuid4()}/input.txt"

    def response_object(self, response_type: str) -> dict[str, Any]:  # type: ignore
        response_field_dict = {
            "CREATE": [
                "VocabularyName",
                "LanguageCode",
                "VocabularyState",
                "LastModifiedTime",
                "FailureReason",
            ],
            "GET": [
                "VocabularyName",
                "LanguageCode",
                "VocabularyState",
                "LastModifiedTime",
                "FailureReason",
                "DownloadUri",
            ],
            "LIST": [
                "VocabularyName",
                "LanguageCode",
                "LastModifiedTime",
                "VocabularyState",
            ],
        }
        response_fields = response_field_dict[response_type]
        response_object = self.gen_response_object()
        response_object["VocabularyState"] = self.status
        return {
            k: v
            for k, v in response_object.items()
            if k in response_fields and v is not None and v != [None]
        }

    def advance(self) -> None:
        old_status = self.status
        super().advance()
        new_status = self.status

        if old_status != new_status:
            self.last_modified_time = utcnow()


class FakeMedicalTranscriptionJob(BaseObject, ManagedState):
    def __init__(
        self,
        region_name: str,
        medical_transcription_job_name: str,
        language_code: str,
        media_sample_rate_hertz: Optional[int],
        media_format: Optional[str],
        media: dict[str, str],
        output_bucket_name: str,
        output_encryption_kms_key_id: Optional[str],
        settings: Optional[dict[str, Any]],
        specialty: str,
        job_type: str,
    ):
        ManagedState.__init__(
            self,
            "transcribe::medicaltranscriptionjob",
            transitions=[
                (None, "QUEUED"),
                ("QUEUED", "IN_PROGRESS"),
                ("IN_PROGRESS", "COMPLETED"),
            ],
        )
        self._region_name = region_name
        self.medical_transcription_job_name = medical_transcription_job_name
        self.language_code = language_code
        self.media_sample_rate_hertz = media_sample_rate_hertz
        self.media_format = media_format
        self.media = media
        self.transcript: Optional[dict[str, str]] = None
        self.start_time: Optional[datetime] = None
        self.completion_time: Optional[datetime] = None
        self.creation_time = utcnow()
        self.failure_reason = None
        self.settings = settings or {
            "ChannelIdentification": False,
            "ShowAlternatives": False,
        }
        self.specialty = specialty
        self.type = job_type
        self._output_bucket_name = output_bucket_name
        self._output_encryption_kms_key_id = output_encryption_kms_key_id
        self.output_location_type = "CUSTOMER_BUCKET"

    def response_object(self, response_type: str) -> dict[str, Any]:  # type: ignore
        response_field_dict = {
            "CREATE": [
                "MedicalTranscriptionJobName",
                "TranscriptionJobStatus",
                "LanguageCode",
                "MediaFormat",
                "Media",
                "StartTime",
                "CreationTime",
                "Specialty",
                "Type",
            ],
            "GET": [
                "MedicalTranscriptionJobName",
                "TranscriptionJobStatus",
                "LanguageCode",
                "MediaSampleRateHertz",
                "MediaFormat",
                "Media",
                "Transcript",
                "StartTime",
                "CreationTime",
                "CompletionTime",
                "Settings",
                "Specialty",
                "Type",
            ],
            "LIST": [
                "MedicalTranscriptionJobName",
                "CreationTime",
                "StartTime",
                "CompletionTime",
                "LanguageCode",
                "TranscriptionJobStatus",
                "FailureReason",
                "OutputLocationType",
                "Specialty",
                "Type",
            ],
        }
        response_fields = response_field_dict[response_type]
        response_object = self.gen_response_object()
        response_object["TranscriptionJobStatus"] = self.status
        if response_type != "LIST":
            return {
                "MedicalTranscriptionJob": {
                    k: v
                    for k, v in response_object.items()
                    if k in response_fields and v is not None and v != [None]
                }
            }
        else:
            return {
                k: v
                for k, v in response_object.items()
                if k in response_fields and v is not None and v != [None]
            }

    def advance(self) -> None:
        old_status = self.status
        super().advance()
        new_status = self.status

        if old_status == new_status:
            return

        if new_status == "IN_PROGRESS":
            self.start_time = utcnow()
            if not self.media_sample_rate_hertz:
                self.media_sample_rate_hertz = 44100
            if not self.media_format:
                file_ext = self.media["MediaFileUri"].split(".")[-1].lower()
                self.media_format = (
                    file_ext if file_ext in ["mp3", "mp4", "wav", "flac"] else "mp3"
                )
        elif new_status == "COMPLETED":
            self.completion_time = utcnow() + timedelta(seconds=10)
            self.transcript = {
                "TranscriptFileUri": f"https://s3.{self._region_name}.amazonaws.com/{self._output_bucket_name}/medical/{self.medical_transcription_job_name}.json"
            }


class FakeVocabularyFilter(BaseObject):
    def __init__(
        self,
        vocabulary_filter_name: str,
        language_code: str,
        words: Optional[list[str]],
        vocabulary_filter_file_uri: Optional[str],
        tags: Optional[list[dict[str, str]]],
        data_access_role_arn: Optional[str],
    ):
        self.vocabulary_filter_name = vocabulary_filter_name
        self.language_code = language_code
        self.words = words
        self.vocabulary_filter_file_uri = vocabulary_filter_file_uri
        self.tags = tags
        self.data_access_role_arn = data_access_role_arn
        self.last_modified_time = utcnow()
        self.download_uri: Optional[str] = None

    def response_object(self, response_type: str) -> dict[str, Any]:  # type: ignore
        response_field_dict = {
            "CREATE": [
                "VocabularyFilterName",
                "LanguageCode",
                "LastModifiedTime",
            ],
            "GET": [
                "VocabularyFilterName",
                "LanguageCode",
                "LastModifiedTime",
                "DownloadUri",
            ],
            "LIST": [
                "VocabularyFilterName",
                "LanguageCode",
                "LastModifiedTime",
            ],
            "UPDATE": [
                "VocabularyFilterName",
                "LanguageCode",
                "LastModifiedTime",
            ],
        }
        response_fields = response_field_dict[response_type]
        response_object = self.gen_response_object()
        return {
            k: v
            for k, v in response_object.items()
            if k in response_fields and v is not None
        }


class FakeLanguageModel(BaseObject):
    def __init__(
        self,
        language_code: str,
        base_model_name: str,
        model_name: str,
        input_data_config: dict[str, str],
        tags: Optional[list[dict[str, str]]],
    ):
        self.model_name = model_name
        self.language_code = language_code
        self.base_model_name = base_model_name
        self.input_data_config = input_data_config
        self.tags = tags
        self.model_status = "COMPLETED"
        self.create_time = utcnow()
        self.last_modified_time = utcnow()
        self.upgrade_availability = False
        self.failure_reason: Optional[str] = None

    def response_object(self, response_type: str) -> dict[str, Any]:  # type: ignore
        response_field_dict = {
            "CREATE": [
                "LanguageCode",
                "BaseModelName",
                "ModelName",
                "InputDataConfig",
                "ModelStatus",
            ],
            "DESCRIBE": [
                "ModelName",
                "CreateTime",
                "LastModifiedTime",
                "LanguageCode",
                "BaseModelName",
                "ModelStatus",
                "UpgradeAvailability",
                "FailureReason",
                "InputDataConfig",
            ],
            "LIST": [
                "ModelName",
                "CreateTime",
                "LastModifiedTime",
                "LanguageCode",
                "BaseModelName",
                "ModelStatus",
                "UpgradeAvailability",
                "FailureReason",
                "InputDataConfig",
            ],
        }
        response_fields = response_field_dict[response_type]
        response_object = self.gen_response_object()
        return {
            k: v
            for k, v in response_object.items()
            if k in response_fields and v is not None
        }


class FakeMedicalVocabulary(FakeVocabulary):
    def __init__(
        self,
        account_id: str,
        region_name: str,
        vocabulary_name: str,
        language_code: str,
        vocabulary_file_uri: Optional[str],
    ):
        super().__init__(
            account_id,
            region_name,
            vocabulary_name,
            language_code=language_code,
            phrases=None,
            vocabulary_file_uri=vocabulary_file_uri,
        )
        self.model_name = "transcribe::medicalvocabulary"
        self._region_name = region_name
        self.vocabulary_name = vocabulary_name
        self.language_code = language_code
        self.vocabulary_file_uri = vocabulary_file_uri
        self.last_modified_time = None
        self.failure_reason = None
        self.download_uri = f"https://s3.us-east-1.amazonaws.com/aws-transcribe-dictionary-model-{region_name}-prod/{account_id}/medical/{self.vocabulary_name}/{mock_random.uuid4()}/input.txt"


class FakeCallAnalyticsCategory(BaseObject):
    def __init__(
        self,
        category_name: str,
        rules: list[dict[str, Any]],
        input_type: Optional[str],
        tags: Optional[list[dict[str, str]]],
    ):
        self.category_name = category_name
        self.rules = rules
        self.input_type = input_type
        self.tags = tags or []
        self.create_time = utcnow()
        self.last_update_time = utcnow()

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {
            "CategoryName": self.category_name,
            "Rules": self.rules,
            "CreateTime": self.create_time.timestamp(),
            "LastUpdateTime": self.last_update_time.timestamp(),
        }
        if self.input_type:
            result["InputType"] = self.input_type
        if self.tags:
            result["Tags"] = self.tags
        return result


class FakeCallAnalyticsJob(BaseObject, ManagedState):
    def __init__(
        self,
        account_id: str,
        region_name: str,
        call_analytics_job_name: str,
        media: dict[str, str],
        output_location: Optional[str],
        output_encryption_kms_key_id: Optional[str],
        data_access_role_arn: Optional[str],
        settings: Optional[dict[str, Any]],
        tags: Optional[list[dict[str, str]]],
        channel_definitions: Optional[list[dict[str, Any]]],
    ):
        ManagedState.__init__(
            self,
            "transcribe::callanalyticsjob",
            transitions=[
                (None, "QUEUED"),
                ("QUEUED", "IN_PROGRESS"),
                ("IN_PROGRESS", "COMPLETED"),
            ],
        )
        self._account_id = account_id
        self._region_name = region_name
        self.call_analytics_job_name = call_analytics_job_name
        self.media = media
        self.output_location = output_location
        self.output_encryption_kms_key_id = output_encryption_kms_key_id
        self.data_access_role_arn = data_access_role_arn
        self.settings = settings or {}
        self.tags = tags or []
        self.channel_definitions = channel_definitions
        self.language_code: Optional[str] = None
        self.media_sample_rate_hertz: Optional[int] = None
        self.media_format: Optional[str] = None
        self.transcript: Optional[dict[str, str]] = None
        self.start_time: Optional[datetime] = None
        self.completion_time: Optional[datetime] = None
        self.creation_time = utcnow()
        self.failure_reason = None
        self.identified_language_score: Optional[float] = None

    def advance(self) -> None:
        old_status = self.status
        super().advance()
        new_status = self.status

        if old_status == new_status:
            return

        if new_status == "IN_PROGRESS":
            self.start_time = utcnow()
            self.language_code = "en-US"
            self.media_sample_rate_hertz = 44100
            file_ext = self.media.get("MediaFileUri", "").split(".")[-1].lower()
            self.media_format = (
                file_ext if file_ext in ["mp3", "mp4", "wav", "flac"] else "mp3"
            )
        elif new_status == "COMPLETED":
            self.completion_time = utcnow() + timedelta(seconds=10)
            transcript_uri = (
                f"https://s3.{self._region_name}.amazonaws.com/"
                f"aws-transcribe-{self._region_name}-prod/"
                f"{self._account_id}/{self.call_analytics_job_name}/"
                f"{mock_random.uuid4()}/asrOutput.json"
            )
            self.transcript = {"TranscriptFileUri": transcript_uri}

    def to_dict(self, response_type: str = "GET") -> dict[str, Any]:
        result: dict[str, Any] = {
            "CallAnalyticsJobName": self.call_analytics_job_name,
            "CallAnalyticsJobStatus": self.status,
            "Media": self.media,
            "CreationTime": self.creation_time.timestamp(),
        }
        if self.language_code:
            result["LanguageCode"] = self.language_code
        if self.media_sample_rate_hertz:
            result["MediaSampleRateHertz"] = self.media_sample_rate_hertz
        if self.media_format:
            result["MediaFormat"] = self.media_format
        if self.transcript:
            result["Transcript"] = self.transcript
        if self.start_time:
            result["StartTime"] = self.start_time.timestamp()
        if self.completion_time:
            result["CompletionTime"] = self.completion_time.timestamp()
        if self.failure_reason:
            result["FailureReason"] = self.failure_reason
        if self.data_access_role_arn:
            result["DataAccessRoleArn"] = self.data_access_role_arn
        if self.settings:
            result["Settings"] = self.settings
        if self.channel_definitions:
            result["ChannelDefinitions"] = self.channel_definitions
        if self.tags:
            result["Tags"] = self.tags
        return result


class FakeMedicalScribeJob(BaseObject, ManagedState):
    def __init__(
        self,
        account_id: str,
        region_name: str,
        medical_scribe_job_name: str,
        media: dict[str, str],
        output_bucket_name: str,
        output_encryption_kms_key_id: Optional[str],
        data_access_role_arn: str,
        settings: dict[str, Any],
        channel_definitions: Optional[list[dict[str, Any]]],
        tags: Optional[list[dict[str, str]]],
        kms_encryption_context: Optional[dict[str, str]],
        medical_scribe_context: Optional[dict[str, Any]],
    ):
        ManagedState.__init__(
            self,
            "transcribe::medicalscribejob",
            transitions=[
                (None, "QUEUED"),
                ("QUEUED", "IN_PROGRESS"),
                ("IN_PROGRESS", "COMPLETED"),
            ],
        )
        self._account_id = account_id
        self._region_name = region_name
        self.medical_scribe_job_name = medical_scribe_job_name
        self.media = media
        self._output_bucket_name = output_bucket_name
        self._output_encryption_kms_key_id = output_encryption_kms_key_id
        self.data_access_role_arn = data_access_role_arn
        self.settings = settings
        self.channel_definitions = channel_definitions
        self.tags = tags or []
        self.kms_encryption_context = kms_encryption_context
        self.medical_scribe_context = medical_scribe_context
        self.language_code = "en-US"
        self.medical_scribe_output: Optional[dict[str, str]] = None
        self.start_time: Optional[datetime] = None
        self.completion_time: Optional[datetime] = None
        self.creation_time = utcnow()
        self.failure_reason = None

    def advance(self) -> None:
        old_status = self.status
        super().advance()
        new_status = self.status

        if old_status == new_status:
            return

        if new_status == "IN_PROGRESS":
            self.start_time = utcnow()
        elif new_status == "COMPLETED":
            self.completion_time = utcnow() + timedelta(seconds=10)
            self.medical_scribe_output = {
                "TranscriptFileUri": (
                    f"https://s3.{self._region_name}.amazonaws.com/"
                    f"{self._output_bucket_name}/medical-scribe/"
                    f"{self.medical_scribe_job_name}/transcript.json"
                ),
                "ClinicalDocumentUri": (
                    f"https://s3.{self._region_name}.amazonaws.com/"
                    f"{self._output_bucket_name}/medical-scribe/"
                    f"{self.medical_scribe_job_name}/clinical-note.json"
                ),
            }

    def to_dict(self, response_type: str = "GET") -> dict[str, Any]:
        result: dict[str, Any] = {
            "MedicalScribeJobName": self.medical_scribe_job_name,
            "MedicalScribeJobStatus": self.status,
            "LanguageCode": self.language_code,
            "Media": self.media,
            "Settings": self.settings,
            "DataAccessRoleArn": self.data_access_role_arn,
            "CreationTime": self.creation_time.timestamp(),
        }
        if self.medical_scribe_output:
            result["MedicalScribeOutput"] = self.medical_scribe_output
        if self.start_time:
            result["StartTime"] = self.start_time.timestamp()
        if self.completion_time:
            result["CompletionTime"] = self.completion_time.timestamp()
        if self.failure_reason:
            result["FailureReason"] = self.failure_reason
        if self.channel_definitions:
            result["ChannelDefinitions"] = self.channel_definitions
        if self.tags:
            result["Tags"] = self.tags
        return result


class TranscribeBackend(BaseBackend):
    def __init__(self, region_name: str, account_id: str):
        super().__init__(region_name, account_id)
        self.medical_transcriptions: dict[str, FakeMedicalTranscriptionJob] = {}
        self.transcriptions: dict[str, FakeTranscriptionJob] = {}
        self.medical_vocabularies: dict[str, FakeMedicalVocabulary] = {}
        self.vocabularies: dict[str, FakeVocabulary] = {}
        self.vocabulary_filters: dict[str, FakeVocabularyFilter] = {}
        self.language_models: dict[str, FakeLanguageModel] = {}
        self.call_analytics_categories: dict[str, FakeCallAnalyticsCategory] = {}
        self.call_analytics_jobs: dict[str, FakeCallAnalyticsJob] = {}
        self.medical_scribe_jobs: dict[str, FakeMedicalScribeJob] = {}
        self._resource_tags: dict[str, list[dict[str, str]]] = {}

    def start_transcription_job(
        self,
        transcription_job_name: str,
        language_code: Optional[str],
        media_sample_rate_hertz: Optional[int],
        media_format: Optional[str],
        media: dict[str, str],
        output_bucket_name: Optional[str],
        output_key: Optional[str],
        output_encryption_kms_key_id: Optional[str],
        settings: Optional[dict[str, Any]],
        model_settings: Optional[dict[str, Optional[str]]],
        job_execution_settings: Optional[dict[str, Any]],
        content_redaction: Optional[dict[str, Any]],
        identify_language: Optional[bool],
        identify_multiple_languages: Optional[bool],
        language_options: Optional[list[str]],
        subtitles: Optional[dict[str, Any]],
    ) -> dict[str, Any]:
        if transcription_job_name in self.transcriptions:
            raise ConflictException(
                message="The requested job name already exists. Use a different job name."
            )

        vocabulary_name = settings.get("VocabularyName") if settings else None
        if vocabulary_name and vocabulary_name not in self.vocabularies:
            raise BadRequestException(
                message="The requested vocabulary couldn't be found. "
                "Check the vocabulary name and try your request again."
            )

        transcription_job_object = FakeTranscriptionJob(
            account_id=self.account_id,
            region_name=self.region_name,
            transcription_job_name=transcription_job_name,
            language_code=language_code,
            media_sample_rate_hertz=media_sample_rate_hertz,
            media_format=media_format,
            media=media,
            output_bucket_name=output_bucket_name,
            output_key=output_key,
            output_encryption_kms_key_id=output_encryption_kms_key_id,
            settings=settings,
            model_settings=model_settings,
            job_execution_settings=job_execution_settings,
            content_redaction=content_redaction,
            identify_language=identify_language,
            identify_multiple_languages=identify_multiple_languages,
            language_options=language_options,
            subtitles=subtitles,
        )
        self.transcriptions[transcription_job_name] = transcription_job_object

        return transcription_job_object.response_object("CREATE")

    def start_medical_transcription_job(
        self,
        medical_transcription_job_name: str,
        language_code: str,
        media_sample_rate_hertz: Optional[int],
        media_format: Optional[str],
        media: dict[str, str],
        output_bucket_name: str,
        output_encryption_kms_key_id: Optional[str],
        settings: Optional[dict[str, Any]],
        specialty: str,
        type_: str,
    ) -> dict[str, Any]:
        if medical_transcription_job_name in self.medical_transcriptions:
            raise ConflictException(
                message="The requested job name already exists. Use a different job name."
            )

        vocabulary_name = settings.get("VocabularyName") if settings else None
        if vocabulary_name and vocabulary_name not in self.medical_vocabularies:
            raise BadRequestException(
                message="The requested vocabulary couldn't be found. "
                "Check the vocabulary name and try your request again."
            )

        transcription_job_object = FakeMedicalTranscriptionJob(
            region_name=self.region_name,
            medical_transcription_job_name=medical_transcription_job_name,
            language_code=language_code,
            media_sample_rate_hertz=media_sample_rate_hertz,
            media_format=media_format,
            media=media,
            output_bucket_name=output_bucket_name,
            output_encryption_kms_key_id=output_encryption_kms_key_id,
            settings=settings,
            specialty=specialty,
            job_type=type_,
        )

        self.medical_transcriptions[medical_transcription_job_name] = (
            transcription_job_object
        )

        return transcription_job_object.response_object("CREATE")

    def get_transcription_job(self, transcription_job_name: str) -> dict[str, Any]:
        try:
            job = self.transcriptions[transcription_job_name]
            job.advance()  # Fakes advancement through statuses.
            return job.response_object("GET")
        except KeyError:
            raise BadRequestException(
                message="The requested job couldn't be found. "
                "Check the job name and try your request again."
            )

    def get_medical_transcription_job(
        self, medical_transcription_job_name: str
    ) -> dict[str, Any]:
        try:
            job = self.medical_transcriptions[medical_transcription_job_name]
            job.advance()  # Fakes advancement through statuses.
            return job.response_object("GET")
        except KeyError:
            raise BadRequestException(
                message="The requested job couldn't be found. "
                "Check the job name and try your request again."
            )

    def delete_transcription_job(self, transcription_job_name: str) -> None:
        try:
            del self.transcriptions[transcription_job_name]
        except KeyError:
            raise BadRequestException(
                message="The requested job couldn't be found. "
                "Check the job name and try your request again."
            )

    def delete_medical_transcription_job(
        self, medical_transcription_job_name: str
    ) -> None:
        try:
            del self.medical_transcriptions[medical_transcription_job_name]
        except KeyError:
            raise BadRequestException(
                message="The requested job couldn't be found. "
                "Check the job name and try your request again."
            )

    def list_transcription_jobs(
        self,
        state_equals: str,
        job_name_contains: str,
        next_token: str,
        max_results: int,
    ) -> dict[str, Any]:
        jobs = list(self.transcriptions.values())

        if state_equals:
            jobs = [job for job in jobs if job.status == state_equals]

        if job_name_contains:
            jobs = [
                job for job in jobs if job_name_contains in job.transcription_job_name
            ]

        start_offset = int(next_token) if next_token else 0
        end_offset = start_offset + (
            max_results if max_results else 100
        )  # Arbitrarily selected...
        jobs_paginated = jobs[start_offset:end_offset]

        response: dict[str, Any] = {
            "TranscriptionJobSummaries": [
                job.response_object("LIST") for job in jobs_paginated
            ]
        }
        if end_offset < len(jobs):
            response["NextToken"] = str(end_offset)
        if state_equals:
            response["Status"] = state_equals
        return response

    def list_medical_transcription_jobs(
        self, status: str, job_name_contains: str, next_token: str, max_results: int
    ) -> dict[str, Any]:
        jobs = list(self.medical_transcriptions.values())

        if status:
            jobs = [job for job in jobs if job.status == status]

        if job_name_contains:
            jobs = [
                job
                for job in jobs
                if job_name_contains in job.medical_transcription_job_name
            ]

        start_offset = int(next_token) if next_token else 0
        end_offset = start_offset + (
            max_results if max_results else 100
        )  # Arbitrarily selected...
        jobs_paginated = jobs[start_offset:end_offset]

        response: dict[str, Any] = {
            "MedicalTranscriptionJobSummaries": [
                job.response_object("LIST") for job in jobs_paginated
            ]
        }
        if end_offset < len(jobs):
            response["NextToken"] = str(end_offset)
        if status:
            response["Status"] = status
        return response

    def create_vocabulary(
        self,
        vocabulary_name: str,
        language_code: str,
        phrases: Optional[list[str]],
        vocabulary_file_uri: Optional[str],
    ) -> dict[str, Any]:
        if (
            phrases is not None
            and vocabulary_file_uri is not None
            or phrases is None
            and vocabulary_file_uri is None
        ):
            raise BadRequestException(
                message="Either Phrases or VocabularyFileUri field should be provided."
            )
        if phrases is not None and len(phrases) < 1:
            raise BadRequestException(
                message="1 validation error detected: Value '[]' at 'phrases' failed to "
                "satisfy constraint: Member must have length greater than or "
                "equal to 1"
            )
        if vocabulary_name in self.vocabularies:
            raise ConflictException(
                message="The requested vocabulary name already exists. "
                "Use a different vocabulary name."
            )

        vocabulary_object = FakeVocabulary(
            account_id=self.account_id,
            region_name=self.region_name,
            vocabulary_name=vocabulary_name,
            language_code=language_code,
            phrases=phrases,
            vocabulary_file_uri=vocabulary_file_uri,
        )

        self.vocabularies[vocabulary_name] = vocabulary_object

        return vocabulary_object.response_object("CREATE")

    def create_medical_vocabulary(
        self,
        vocabulary_name: str,
        language_code: str,
        vocabulary_file_uri: Optional[str],
    ) -> dict[str, Any]:
        if vocabulary_name in self.medical_vocabularies:
            raise ConflictException(
                message="The requested vocabulary name already exists. "
                "Use a different vocabulary name."
            )

        medical_vocabulary_object = FakeMedicalVocabulary(
            account_id=self.account_id,
            region_name=self.region_name,
            vocabulary_name=vocabulary_name,
            language_code=language_code,
            vocabulary_file_uri=vocabulary_file_uri,
        )

        self.medical_vocabularies[vocabulary_name] = medical_vocabulary_object

        return medical_vocabulary_object.response_object("CREATE")

    def get_vocabulary(self, vocabulary_name: str) -> dict[str, Any]:
        try:
            job = self.vocabularies[vocabulary_name]
            job.advance()  # Fakes advancement through statuses.
            return job.response_object("GET")
        except KeyError:
            raise BadRequestException(
                message="The requested vocabulary couldn't be found. "
                "Check the vocabulary name and try your request again."
            )

    def get_medical_vocabulary(self, vocabulary_name: str) -> dict[str, Any]:
        try:
            job = self.medical_vocabularies[vocabulary_name]
            job.advance()  # Fakes advancement through statuses.
            return job.response_object("GET")
        except KeyError:
            raise BadRequestException(
                message="The requested vocabulary couldn't be found. "
                "Check the vocabulary name and try your request again."
            )

    def delete_vocabulary(self, vocabulary_name: str) -> None:
        try:
            del self.vocabularies[vocabulary_name]
        except KeyError:
            raise BadRequestException(
                message="The requested vocabulary couldn't be found. Check the vocabulary name and try your request again."
            )

    def update_vocabulary(
        self,
        vocabulary_name: str,
        language_code: str,
        phrases: Optional[list[str]],
        vocabulary_file_uri: Optional[str],
    ) -> dict[str, Any]:
        if (
            phrases is not None
            and vocabulary_file_uri is not None
            or phrases is None
            and vocabulary_file_uri is None
        ):
            raise BadRequestException(
                message="Either Phrases or VocabularyFileUri field should be provided."
            )
        try:
            vocab = self.vocabularies[vocabulary_name]
        except KeyError:
            raise BadRequestException(
                message="The requested vocabulary couldn't be found. "
                "Check the vocabulary name and try your request again."
            )
        vocab.language_code = language_code
        if phrases is not None:
            vocab.phrases = phrases
        if vocabulary_file_uri is not None:
            vocab.vocabulary_file_uri = vocabulary_file_uri
        vocab.advance()
        return vocab.response_object("CREATE")

    def delete_medical_vocabulary(self, vocabulary_name: str) -> None:
        try:
            del self.medical_vocabularies[vocabulary_name]
        except KeyError:
            raise BadRequestException(
                message="The requested vocabulary couldn't be found. Check the vocabulary name and try your request again."
            )

    def list_vocabularies(
        self, state_equals: str, name_contains: str, next_token: str, max_results: int
    ) -> dict[str, Any]:
        vocabularies = list(self.vocabularies.values())

        if state_equals:
            vocabularies = [
                vocabulary
                for vocabulary in vocabularies
                if vocabulary.status == state_equals
            ]

        if name_contains:
            vocabularies = [
                vocabulary
                for vocabulary in vocabularies
                if name_contains in vocabulary.vocabulary_name
            ]

        start_offset = int(next_token) if next_token else 0
        end_offset = start_offset + (
            max_results if max_results else 100
        )  # Arbitrarily selected...
        vocabularies_paginated = vocabularies[start_offset:end_offset]

        response: dict[str, Any] = {
            "Vocabularies": [
                vocabulary.response_object("LIST")
                for vocabulary in vocabularies_paginated
            ]
        }
        if end_offset < len(vocabularies):
            response["NextToken"] = str(end_offset)
        if state_equals:
            response["Status"] = state_equals
        return response

    def list_medical_vocabularies(
        self, state_equals: str, name_contains: str, next_token: str, max_results: int
    ) -> dict[str, Any]:
        vocabularies = list(self.medical_vocabularies.values())

        if state_equals:
            vocabularies = [
                vocabulary
                for vocabulary in vocabularies
                if vocabulary.status == state_equals
            ]

        if name_contains:
            vocabularies = [
                vocabulary
                for vocabulary in vocabularies
                if name_contains in vocabulary.vocabulary_name
            ]

        start_offset = int(next_token) if next_token else 0
        end_offset = start_offset + (
            max_results if max_results else 100
        )  # Arbitrarily selected...
        vocabularies_paginated = vocabularies[start_offset:end_offset]

        response: dict[str, Any] = {
            "Vocabularies": [
                vocabulary.response_object("LIST")
                for vocabulary in vocabularies_paginated
            ]
        }
        if end_offset < len(vocabularies):
            response["NextToken"] = str(end_offset)
        if state_equals:
            response["Status"] = state_equals
        return response

    # --- VocabularyFilter CRUD ---

    def create_vocabulary_filter(
        self,
        vocabulary_filter_name: str,
        language_code: str,
        words: Optional[list[str]],
        vocabulary_filter_file_uri: Optional[str],
        tags: Optional[list[dict[str, str]]],
        data_access_role_arn: Optional[str],
    ) -> dict[str, Any]:
        if vocabulary_filter_name in self.vocabulary_filters:
            raise ConflictException(
                message="The requested vocabulary filter name already exists. "
                "Use a different vocabulary filter name."
            )
        if words is None and vocabulary_filter_file_uri is None:
            raise BadRequestException(
                message="Either Words or VocabularyFilterFileUri field should be provided."
            )

        vocabulary_filter = FakeVocabularyFilter(
            vocabulary_filter_name=vocabulary_filter_name,
            language_code=language_code,
            words=words,
            vocabulary_filter_file_uri=vocabulary_filter_file_uri,
            tags=tags,
            data_access_role_arn=data_access_role_arn,
        )
        self.vocabulary_filters[vocabulary_filter_name] = vocabulary_filter
        return vocabulary_filter.response_object("CREATE")

    def get_vocabulary_filter(self, vocabulary_filter_name: str) -> dict[str, Any]:
        try:
            vf = self.vocabulary_filters[vocabulary_filter_name]
            return vf.response_object("GET")
        except KeyError:
            raise BadRequestException(
                message="The requested vocabulary filter couldn't be found. "
                "Check the vocabulary filter name and try your request again."
            )

    def delete_vocabulary_filter(self, vocabulary_filter_name: str) -> None:
        try:
            del self.vocabulary_filters[vocabulary_filter_name]
        except KeyError:
            raise BadRequestException(
                message="The requested vocabulary filter couldn't be found. "
                "Check the vocabulary filter name and try your request again."
            )

    def update_vocabulary_filter(
        self,
        vocabulary_filter_name: str,
        words: Optional[list[str]],
        vocabulary_filter_file_uri: Optional[str],
        data_access_role_arn: Optional[str],
    ) -> dict[str, Any]:
        if vocabulary_filter_name not in self.vocabulary_filters:
            raise BadRequestException(
                message="The requested vocabulary filter couldn't be found. "
                "Check the vocabulary filter name and try your request again."
            )
        vf = self.vocabulary_filters[vocabulary_filter_name]
        if words is not None:
            vf.words = words
        if vocabulary_filter_file_uri is not None:
            vf.vocabulary_filter_file_uri = vocabulary_filter_file_uri
        if data_access_role_arn is not None:
            vf.data_access_role_arn = data_access_role_arn
        vf.last_modified_time = utcnow()
        return vf.response_object("UPDATE")

    def list_vocabulary_filters(
        self,
        name_contains: Optional[str],
        next_token: Optional[str],
        max_results: Optional[int],
    ) -> dict[str, Any]:
        filters = list(self.vocabulary_filters.values())

        if name_contains:
            filters = [
                f for f in filters if name_contains in f.vocabulary_filter_name
            ]

        start_offset = int(next_token) if next_token else 0
        end_offset = start_offset + (max_results if max_results else 100)
        filters_paginated = filters[start_offset:end_offset]

        response: dict[str, Any] = {
            "VocabularyFilters": [
                f.response_object("LIST") for f in filters_paginated
            ]
        }
        if end_offset < len(filters):
            response["NextToken"] = str(end_offset)
        return response

    # --- LanguageModel CRUD ---

    def create_language_model(
        self,
        language_code: str,
        base_model_name: str,
        model_name: str,
        input_data_config: dict[str, str],
        tags: Optional[list[dict[str, str]]],
    ) -> dict[str, Any]:
        if model_name in self.language_models:
            raise ConflictException(
                message="The requested language model name already exists. "
                "Use a different language model name."
            )

        language_model = FakeLanguageModel(
            language_code=language_code,
            base_model_name=base_model_name,
            model_name=model_name,
            input_data_config=input_data_config,
            tags=tags,
        )
        self.language_models[model_name] = language_model
        return language_model.response_object("CREATE")

    def describe_language_model(self, model_name: str) -> dict[str, Any]:
        try:
            model = self.language_models[model_name]
            return {"LanguageModel": model.response_object("DESCRIBE")}
        except KeyError:
            raise BadRequestException(
                message="The requested language model couldn't be found. "
                "Check the language model name and try your request again."
            )

    def delete_language_model(self, model_name: str) -> None:
        try:
            del self.language_models[model_name]
        except KeyError:
            raise BadRequestException(
                message="The requested language model couldn't be found. "
                "Check the language model name and try your request again."
            )

    def list_language_models(
        self,
        status_equals: Optional[str],
        name_contains: Optional[str],
        next_token: Optional[str],
        max_results: Optional[int],
    ) -> dict[str, Any]:
        models = list(self.language_models.values())

        if status_equals:
            models = [m for m in models if m.model_status == status_equals]

        if name_contains:
            models = [m for m in models if name_contains in m.model_name]

        start_offset = int(next_token) if next_token else 0
        end_offset = start_offset + (max_results if max_results else 100)
        models_paginated = models[start_offset:end_offset]

        response: dict[str, Any] = {
            "Models": [m.response_object("LIST") for m in models_paginated]
        }
        if end_offset < len(models):
            response["NextToken"] = str(end_offset)
        return response

    # --- CallAnalyticsCategory CRUD ---

    def create_call_analytics_category(
        self,
        category_name: str,
        rules: list[dict[str, Any]],
        input_type: Optional[str],
        tags: Optional[list[dict[str, str]]],
    ) -> dict[str, Any]:
        if category_name in self.call_analytics_categories:
            raise ConflictException(
                message="The requested category name already exists. Use a different category name."
            )
        category = FakeCallAnalyticsCategory(
            category_name=category_name,
            rules=rules,
            input_type=input_type,
            tags=tags,
        )
        self.call_analytics_categories[category_name] = category
        return {"CategoryProperties": category.to_dict()}

    def get_call_analytics_category(self, category_name: str) -> dict[str, Any]:
        try:
            category = self.call_analytics_categories[category_name]
            return {"CategoryProperties": category.to_dict()}
        except KeyError:
            raise BadRequestException(
                message="The requested category couldn't be found. "
                "Check the category name and try your request again."
            )

    def delete_call_analytics_category(self, category_name: str) -> None:
        try:
            del self.call_analytics_categories[category_name]
        except KeyError:
            raise BadRequestException(
                message="The requested category couldn't be found. "
                "Check the category name and try your request again."
            )

    def update_call_analytics_category(
        self,
        category_name: str,
        rules: list[dict[str, Any]],
        input_type: Optional[str],
    ) -> dict[str, Any]:
        try:
            category = self.call_analytics_categories[category_name]
        except KeyError:
            raise BadRequestException(
                message="The requested category couldn't be found. "
                "Check the category name and try your request again."
            )
        category.rules = rules
        if input_type is not None:
            category.input_type = input_type
        category.last_update_time = utcnow()
        return {"CategoryProperties": category.to_dict()}

    def list_call_analytics_categories(
        self,
        next_token: Optional[str],
        max_results: Optional[int],
    ) -> dict[str, Any]:
        categories = list(self.call_analytics_categories.values())
        start_offset = int(next_token) if next_token else 0
        end_offset = start_offset + (max_results if max_results else 100)
        categories_paginated = categories[start_offset:end_offset]
        response: dict[str, Any] = {
            "Categories": [c.to_dict() for c in categories_paginated]
        }
        if end_offset < len(categories):
            response["NextToken"] = str(end_offset)
        return response

    # --- CallAnalyticsJob CRUD ---

    def start_call_analytics_job(
        self,
        call_analytics_job_name: str,
        media: dict[str, str],
        output_location: Optional[str],
        output_encryption_kms_key_id: Optional[str],
        data_access_role_arn: Optional[str],
        settings: Optional[dict[str, Any]],
        tags: Optional[list[dict[str, str]]],
        channel_definitions: Optional[list[dict[str, Any]]],
    ) -> dict[str, Any]:
        if call_analytics_job_name in self.call_analytics_jobs:
            raise ConflictException(
                message="The requested job name already exists. Use a different job name."
            )
        job = FakeCallAnalyticsJob(
            account_id=self.account_id,
            region_name=self.region_name,
            call_analytics_job_name=call_analytics_job_name,
            media=media,
            output_location=output_location,
            output_encryption_kms_key_id=output_encryption_kms_key_id,
            data_access_role_arn=data_access_role_arn,
            settings=settings,
            tags=tags,
            channel_definitions=channel_definitions,
        )
        self.call_analytics_jobs[call_analytics_job_name] = job
        return {"CallAnalyticsJob": job.to_dict("CREATE")}

    def get_call_analytics_job(self, call_analytics_job_name: str) -> dict[str, Any]:
        try:
            job = self.call_analytics_jobs[call_analytics_job_name]
            job.advance()
            return {"CallAnalyticsJob": job.to_dict("GET")}
        except KeyError:
            raise BadRequestException(
                message="The requested job couldn't be found. "
                "Check the job name and try your request again."
            )

    def delete_call_analytics_job(self, call_analytics_job_name: str) -> None:
        try:
            del self.call_analytics_jobs[call_analytics_job_name]
        except KeyError:
            raise BadRequestException(
                message="The requested job couldn't be found. "
                "Check the job name and try your request again."
            )

    def list_call_analytics_jobs(
        self,
        status: Optional[str],
        job_name_contains: Optional[str],
        next_token: Optional[str],
        max_results: Optional[int],
    ) -> dict[str, Any]:
        jobs = list(self.call_analytics_jobs.values())
        if status:
            jobs = [j for j in jobs if j.status == status]
        if job_name_contains:
            jobs = [j for j in jobs if job_name_contains in j.call_analytics_job_name]
        start_offset = int(next_token) if next_token else 0
        end_offset = start_offset + (max_results if max_results else 100)
        jobs_paginated = jobs[start_offset:end_offset]
        response: dict[str, Any] = {
            "CallAnalyticsJobSummaries": [j.to_dict("LIST") for j in jobs_paginated]
        }
        if end_offset < len(jobs):
            response["NextToken"] = str(end_offset)
        if status:
            response["Status"] = status
        return response

    # --- MedicalScribeJob CRUD ---

    def start_medical_scribe_job(
        self,
        medical_scribe_job_name: str,
        media: dict[str, str],
        output_bucket_name: str,
        output_encryption_kms_key_id: Optional[str],
        kms_encryption_context: Optional[dict[str, str]],
        data_access_role_arn: str,
        settings: dict[str, Any],
        channel_definitions: Optional[list[dict[str, Any]]],
        tags: Optional[list[dict[str, str]]],
        medical_scribe_context: Optional[dict[str, Any]],
    ) -> dict[str, Any]:
        if medical_scribe_job_name in self.medical_scribe_jobs:
            raise ConflictException(
                message="The requested job name already exists. Use a different job name."
            )
        job = FakeMedicalScribeJob(
            account_id=self.account_id,
            region_name=self.region_name,
            medical_scribe_job_name=medical_scribe_job_name,
            media=media,
            output_bucket_name=output_bucket_name,
            output_encryption_kms_key_id=output_encryption_kms_key_id,
            kms_encryption_context=kms_encryption_context,
            data_access_role_arn=data_access_role_arn,
            settings=settings,
            channel_definitions=channel_definitions,
            tags=tags,
            medical_scribe_context=medical_scribe_context,
        )
        self.medical_scribe_jobs[medical_scribe_job_name] = job
        return {"MedicalScribeJob": job.to_dict("CREATE")}

    def get_medical_scribe_job(self, medical_scribe_job_name: str) -> dict[str, Any]:
        try:
            job = self.medical_scribe_jobs[medical_scribe_job_name]
            job.advance()
            return {"MedicalScribeJob": job.to_dict("GET")}
        except KeyError:
            raise BadRequestException(
                message="The requested job couldn't be found. "
                "Check the job name and try your request again."
            )

    def delete_medical_scribe_job(self, medical_scribe_job_name: str) -> None:
        try:
            del self.medical_scribe_jobs[medical_scribe_job_name]
        except KeyError:
            raise BadRequestException(
                message="The requested job couldn't be found. "
                "Check the job name and try your request again."
            )

    def list_medical_scribe_jobs(
        self,
        status: Optional[str],
        job_name_contains: Optional[str],
        next_token: Optional[str],
        max_results: Optional[int],
    ) -> dict[str, Any]:
        jobs = list(self.medical_scribe_jobs.values())
        if status:
            jobs = [j for j in jobs if j.status == status]
        if job_name_contains:
            jobs = [j for j in jobs if job_name_contains in j.medical_scribe_job_name]
        start_offset = int(next_token) if next_token else 0
        end_offset = start_offset + (max_results if max_results else 100)
        jobs_paginated = jobs[start_offset:end_offset]
        response: dict[str, Any] = {
            "MedicalScribeJobSummaries": [j.to_dict("LIST") for j in jobs_paginated]
        }
        if end_offset < len(jobs):
            response["NextToken"] = str(end_offset)
        if status:
            response["Status"] = status
        return response

    # --- UpdateMedicalVocabulary ---

    def update_medical_vocabulary(
        self,
        vocabulary_name: str,
        language_code: str,
        vocabulary_file_uri: Optional[str],
    ) -> dict[str, Any]:
        try:
            vocab = self.medical_vocabularies[vocabulary_name]
        except KeyError:
            raise BadRequestException(
                message="The requested vocabulary couldn't be found. "
                "Check the vocabulary name and try your request again."
            )
        vocab.language_code = language_code
        if vocabulary_file_uri is not None:
            vocab.vocabulary_file_uri = vocabulary_file_uri
        vocab.advance()
        return vocab.response_object("CREATE")

    # --- TagResource / UntagResource / ListTagsForResource ---

    def _arn_for_resource(self, resource_arn: str) -> Optional[Any]:
        """Find any transcribe resource by its ARN."""
        # ARN format: arn:aws:transcribe:{region}:{account}:{type}/{name}
        # Supported types: vocabulary, medical-vocabulary, transcription-job,
        #   medical-transcription-job, language-model, vocabulary-filter,
        #   call-analytics-category, call-analytics-job, medical-scribe-job
        parts = resource_arn.split(":")
        if len(parts) < 6:
            return None
        resource_part = parts[5]  # e.g. "vocabulary/my-vocab"
        if "/" not in resource_part:
            return None
        resource_type, resource_name = resource_part.split("/", 1)
        type_map: dict[str, dict[str, Any]] = {
            "vocabulary": self.vocabularies,
            "medical-vocabulary": self.medical_vocabularies,
            "transcription-job": self.transcriptions,
            "medical-transcription-job": self.medical_transcriptions,
            "language-model": self.language_models,
            "vocabulary-filter": self.vocabulary_filters,
            "call-analytics-category": self.call_analytics_categories,
            "call-analytics-job": self.call_analytics_jobs,
            "medical-scribe-job": self.medical_scribe_jobs,
        }
        store = type_map.get(resource_type)
        if store is None:
            return None
        return store.get(resource_name)

    def tag_resource(
        self, resource_arn: str, tags: list[dict[str, str]]
    ) -> None:
        resource = self._arn_for_resource(resource_arn)
        if resource is None:
            raise BadRequestException(
                message="The requested resource couldn't be found. "
                "Check the ARN and try your request again."
            )
        if not hasattr(resource, "tags") or resource.tags is None:
            resource.tags = []
        existing_keys = {t["Key"] for t in resource.tags}
        for tag in tags:
            if tag["Key"] in existing_keys:
                resource.tags = [t for t in resource.tags if t["Key"] != tag["Key"]]
            resource.tags.append(tag)
        # Also track in central store for ARN-based lookups
        self._resource_tags[resource_arn] = list(resource.tags)

    def untag_resource(
        self, resource_arn: str, tag_keys: list[str]
    ) -> None:
        resource = self._arn_for_resource(resource_arn)
        if resource is None:
            raise BadRequestException(
                message="The requested resource couldn't be found. "
                "Check the ARN and try your request again."
            )
        if hasattr(resource, "tags") and resource.tags:
            resource.tags = [t for t in resource.tags if t["Key"] not in tag_keys]
        self._resource_tags[resource_arn] = getattr(resource, "tags", []) or []

    def list_tags_for_resource(self, resource_arn: str) -> dict[str, Any]:
        resource = self._arn_for_resource(resource_arn)
        if resource is None:
            raise BadRequestException(
                message="The requested resource couldn't be found. "
                "Check the ARN and try your request again."
            )
        tags = getattr(resource, "tags", None) or []
        return {"ResourceArn": resource_arn, "Tags": tags}


transcribe_backends = BackendDict(TranscribeBackend, "transcribe")
