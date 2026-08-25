from moto.core.responses import ActionResult, BaseResponse, EmptyResult

from .models import TranscribeBackend, transcribe_backends


class TranscribeResponse(BaseResponse):
    def __init__(self) -> None:
        super().__init__(service_name="transcribe")

    @property
    def transcribe_backend(self) -> TranscribeBackend:
        return transcribe_backends[self.current_account][self.region]

    def start_transcription_job(self) -> ActionResult:
        name = self._get_param("TranscriptionJobName")
        response = self.transcribe_backend.start_transcription_job(
            transcription_job_name=name,
            language_code=self._get_param("LanguageCode"),
            media_sample_rate_hertz=self._get_param("MediaSampleRateHertz"),
            media_format=self._get_param("MediaFormat"),
            media=self._get_param("Media"),
            output_bucket_name=self._get_param("OutputBucketName"),
            output_key=self._get_param("OutputKey"),
            output_encryption_kms_key_id=self._get_param("OutputEncryptionKMSKeyId"),
            settings=self._get_param("Settings"),
            model_settings=self._get_param("ModelSettings"),
            job_execution_settings=self._get_param("JobExecutionSettings"),
            content_redaction=self._get_param("ContentRedaction"),
            identify_language=self._get_param("IdentifyLanguage"),
            identify_multiple_languages=self._get_param("IdentifyMultipleLanguages"),
            language_options=self._get_param("LanguageOptions"),
            subtitles=self._get_param("Subtitles"),
        )
        return ActionResult(response)

    def start_medical_transcription_job(self) -> ActionResult:
        name = self._get_param("MedicalTranscriptionJobName")
        response = self.transcribe_backend.start_medical_transcription_job(
            medical_transcription_job_name=name,
            language_code=self._get_param("LanguageCode"),
            media_sample_rate_hertz=self._get_param("MediaSampleRateHertz"),
            media_format=self._get_param("MediaFormat"),
            media=self._get_param("Media"),
            output_bucket_name=self._get_param("OutputBucketName"),
            output_encryption_kms_key_id=self._get_param("OutputEncryptionKMSKeyId"),
            settings=self._get_param("Settings"),
            specialty=self._get_param("Specialty"),
            type_=self._get_param("Type"),
        )
        return ActionResult(response)

    def list_transcription_jobs(self) -> ActionResult:
        state_equals = self._get_param("Status")
        job_name_contains = self._get_param("JobNameContains")
        next_token = self._get_param("NextToken")
        max_results = self._get_param("MaxResults")

        response = self.transcribe_backend.list_transcription_jobs(
            state_equals=state_equals,
            job_name_contains=job_name_contains,
            next_token=next_token,
            max_results=max_results,
        )
        return ActionResult(response)

    def list_medical_transcription_jobs(self) -> ActionResult:
        status = self._get_param("Status")
        job_name_contains = self._get_param("JobNameContains")
        next_token = self._get_param("NextToken")
        max_results = self._get_param("MaxResults")

        response = self.transcribe_backend.list_medical_transcription_jobs(
            status=status,
            job_name_contains=job_name_contains,
            next_token=next_token,
            max_results=max_results,
        )
        return ActionResult(response)

    def get_transcription_job(self) -> ActionResult:
        transcription_job_name = self._get_param("TranscriptionJobName")
        response = self.transcribe_backend.get_transcription_job(
            transcription_job_name=transcription_job_name
        )
        return ActionResult(response)

    def get_medical_transcription_job(self) -> ActionResult:
        medical_transcription_job_name = self._get_param("MedicalTranscriptionJobName")
        response = self.transcribe_backend.get_medical_transcription_job(
            medical_transcription_job_name=medical_transcription_job_name
        )
        return ActionResult(response)

    def delete_transcription_job(self) -> ActionResult:
        transcription_job_name = self._get_param("TranscriptionJobName")
        self.transcribe_backend.delete_transcription_job(
            transcription_job_name=transcription_job_name
        )
        return EmptyResult()

    def delete_medical_transcription_job(self) -> ActionResult:
        medical_transcription_job_name = self._get_param("MedicalTranscriptionJobName")
        self.transcribe_backend.delete_medical_transcription_job(
            medical_transcription_job_name=medical_transcription_job_name
        )
        return EmptyResult()

    def create_vocabulary(self) -> ActionResult:
        vocabulary_name = self._get_param("VocabularyName")
        language_code = self._get_param("LanguageCode")
        phrases = self._get_param("Phrases")
        vocabulary_file_uri = self._get_param("VocabularyFileUri")
        response = self.transcribe_backend.create_vocabulary(
            vocabulary_name=vocabulary_name,
            language_code=language_code,
            phrases=phrases,
            vocabulary_file_uri=vocabulary_file_uri,
        )
        return ActionResult(response)

    def create_medical_vocabulary(self) -> ActionResult:
        vocabulary_name = self._get_param("VocabularyName")
        language_code = self._get_param("LanguageCode")
        vocabulary_file_uri = self._get_param("VocabularyFileUri")
        response = self.transcribe_backend.create_medical_vocabulary(
            vocabulary_name=vocabulary_name,
            language_code=language_code,
            vocabulary_file_uri=vocabulary_file_uri,
        )
        return ActionResult(response)

    def get_vocabulary(self) -> ActionResult:
        vocabulary_name = self._get_param("VocabularyName")
        response = self.transcribe_backend.get_vocabulary(
            vocabulary_name=vocabulary_name
        )
        return ActionResult(response)

    def get_medical_vocabulary(self) -> ActionResult:
        vocabulary_name = self._get_param("VocabularyName")
        response = self.transcribe_backend.get_medical_vocabulary(
            vocabulary_name=vocabulary_name
        )
        return ActionResult(response)

    def list_vocabularies(self) -> ActionResult:
        state_equals = self._get_param("StateEquals")
        name_contains = self._get_param("NameContains")
        next_token = self._get_param("NextToken")
        max_results = self._get_param("MaxResults")

        response = self.transcribe_backend.list_vocabularies(
            state_equals=state_equals,
            name_contains=name_contains,
            next_token=next_token,
            max_results=max_results,
        )
        return ActionResult(response)

    def list_medical_vocabularies(self) -> ActionResult:
        state_equals = self._get_param("StateEquals")
        name_contains = self._get_param("NameContains")
        next_token = self._get_param("NextToken")
        max_results = self._get_param("MaxResults")

        response = self.transcribe_backend.list_medical_vocabularies(
            state_equals=state_equals,
            name_contains=name_contains,
            next_token=next_token,
            max_results=max_results,
        )
        return ActionResult(response)

    def delete_vocabulary(self) -> ActionResult:
        vocabulary_name = self._get_param("VocabularyName")
        self.transcribe_backend.delete_vocabulary(vocabulary_name=vocabulary_name)
        return EmptyResult()

    def update_vocabulary(self) -> ActionResult:
        vocabulary_name = self._get_param("VocabularyName")
        language_code = self._get_param("LanguageCode")
        phrases = self._get_param("Phrases")
        vocabulary_file_uri = self._get_param("VocabularyFileUri")
        response = self.transcribe_backend.update_vocabulary(
            vocabulary_name=vocabulary_name,
            language_code=language_code,
            phrases=phrases,
            vocabulary_file_uri=vocabulary_file_uri,
        )
        return ActionResult(response)

    def delete_medical_vocabulary(self) -> ActionResult:
        vocabulary_name = self._get_param("VocabularyName")
        self.transcribe_backend.delete_medical_vocabulary(
            vocabulary_name=vocabulary_name
        )
        return EmptyResult()

    # --- CallAnalyticsCategory CRUD ---

    def create_call_analytics_category(self) -> ActionResult:
        response = self.transcribe_backend.create_call_analytics_category(
            category_name=self._get_param("CategoryName"),
            rules=self._get_param("Rules"),
            input_type=self._get_param("InputType"),
            tags=self._get_param("Tags"),
        )
        return ActionResult(response)

    def get_call_analytics_category(self) -> ActionResult:
        response = self.transcribe_backend.get_call_analytics_category(
            category_name=self._get_param("CategoryName"),
        )
        return ActionResult(response)

    def delete_call_analytics_category(self) -> ActionResult:
        self.transcribe_backend.delete_call_analytics_category(
            category_name=self._get_param("CategoryName"),
        )
        return EmptyResult()

    def update_call_analytics_category(self) -> ActionResult:
        response = self.transcribe_backend.update_call_analytics_category(
            category_name=self._get_param("CategoryName"),
            rules=self._get_param("Rules"),
            input_type=self._get_param("InputType"),
        )
        return ActionResult(response)

    def list_call_analytics_categories(self) -> ActionResult:
        response = self.transcribe_backend.list_call_analytics_categories(
            next_token=self._get_param("NextToken"),
            max_results=self._get_param("MaxResults"),
        )
        return ActionResult(response)

    # --- CallAnalyticsJob CRUD ---

    def start_call_analytics_job(self) -> ActionResult:
        response = self.transcribe_backend.start_call_analytics_job(
            call_analytics_job_name=self._get_param("CallAnalyticsJobName"),
            media=self._get_param("Media"),
            output_location=self._get_param("OutputLocation"),
            output_encryption_kms_key_id=self._get_param("OutputEncryptionKMSKeyId"),
            data_access_role_arn=self._get_param("DataAccessRoleArn"),
            settings=self._get_param("Settings"),
            tags=self._get_param("Tags"),
            channel_definitions=self._get_param("ChannelDefinitions"),
        )
        return ActionResult(response)

    def get_call_analytics_job(self) -> ActionResult:
        response = self.transcribe_backend.get_call_analytics_job(
            call_analytics_job_name=self._get_param("CallAnalyticsJobName"),
        )
        return ActionResult(response)

    def delete_call_analytics_job(self) -> ActionResult:
        self.transcribe_backend.delete_call_analytics_job(
            call_analytics_job_name=self._get_param("CallAnalyticsJobName"),
        )
        return EmptyResult()

    def list_call_analytics_jobs(self) -> ActionResult:
        response = self.transcribe_backend.list_call_analytics_jobs(
            status=self._get_param("Status"),
            job_name_contains=self._get_param("JobNameContains"),
            next_token=self._get_param("NextToken"),
            max_results=self._get_param("MaxResults"),
        )
        return ActionResult(response)

    # --- MedicalScribeJob CRUD ---

    def start_medical_scribe_job(self) -> ActionResult:
        response = self.transcribe_backend.start_medical_scribe_job(
            medical_scribe_job_name=self._get_param("MedicalScribeJobName"),
            media=self._get_param("Media"),
            output_bucket_name=self._get_param("OutputBucketName"),
            output_encryption_kms_key_id=self._get_param("OutputEncryptionKMSKeyId"),
            kms_encryption_context=self._get_param("KMSEncryptionContext"),
            data_access_role_arn=self._get_param("DataAccessRoleArn"),
            settings=self._get_param("Settings"),
            channel_definitions=self._get_param("ChannelDefinitions"),
            tags=self._get_param("Tags"),
            medical_scribe_context=self._get_param("MedicalScribeContext"),
        )
        return ActionResult(response)

    def get_medical_scribe_job(self) -> ActionResult:
        response = self.transcribe_backend.get_medical_scribe_job(
            medical_scribe_job_name=self._get_param("MedicalScribeJobName"),
        )
        return ActionResult(response)

    def delete_medical_scribe_job(self) -> ActionResult:
        self.transcribe_backend.delete_medical_scribe_job(
            medical_scribe_job_name=self._get_param("MedicalScribeJobName"),
        )
        return EmptyResult()

    def list_medical_scribe_jobs(self) -> ActionResult:
        response = self.transcribe_backend.list_medical_scribe_jobs(
            status=self._get_param("Status"),
            job_name_contains=self._get_param("JobNameContains"),
            next_token=self._get_param("NextToken"),
            max_results=self._get_param("MaxResults"),
        )
        return ActionResult(response)

    # --- UpdateMedicalVocabulary ---

    def update_medical_vocabulary(self) -> ActionResult:
        response = self.transcribe_backend.update_medical_vocabulary(
            vocabulary_name=self._get_param("VocabularyName"),
            language_code=self._get_param("LanguageCode"),
            vocabulary_file_uri=self._get_param("VocabularyFileUri"),
        )
        return ActionResult(response)

    # --- TagResource / UntagResource / ListTagsForResource ---

    def tag_resource(self) -> ActionResult:
        self.transcribe_backend.tag_resource(
            resource_arn=self._get_param("ResourceArn"),
            tags=self._get_param("Tags"),
        )
        return EmptyResult()

    def untag_resource(self) -> ActionResult:
        self.transcribe_backend.untag_resource(
            resource_arn=self._get_param("ResourceArn"),
            tag_keys=self._get_param("TagKeys"),
        )
        return EmptyResult()

    def list_tags_for_resource(self) -> ActionResult:
        response = self.transcribe_backend.list_tags_for_resource(
            resource_arn=self._get_param("ResourceArn"),
        )
        return ActionResult(response)

    # --- VocabularyFilter CRUD ---

    def create_vocabulary_filter(self) -> ActionResult:
        response = self.transcribe_backend.create_vocabulary_filter(
            vocabulary_filter_name=self._get_param("VocabularyFilterName"),
            language_code=self._get_param("LanguageCode"),
            words=self._get_param("Words"),
            vocabulary_filter_file_uri=self._get_param("VocabularyFilterFileUri"),
            tags=self._get_param("Tags"),
            data_access_role_arn=self._get_param("DataAccessRoleArn"),
        )
        return ActionResult(response)

    def get_vocabulary_filter(self) -> ActionResult:
        response = self.transcribe_backend.get_vocabulary_filter(
            vocabulary_filter_name=self._get_param("VocabularyFilterName"),
        )
        return ActionResult(response)

    def delete_vocabulary_filter(self) -> ActionResult:
        self.transcribe_backend.delete_vocabulary_filter(
            vocabulary_filter_name=self._get_param("VocabularyFilterName"),
        )
        return EmptyResult()

    def update_vocabulary_filter(self) -> ActionResult:
        response = self.transcribe_backend.update_vocabulary_filter(
            vocabulary_filter_name=self._get_param("VocabularyFilterName"),
            words=self._get_param("Words"),
            vocabulary_filter_file_uri=self._get_param("VocabularyFilterFileUri"),
            data_access_role_arn=self._get_param("DataAccessRoleArn"),
        )
        return ActionResult(response)

    def list_vocabulary_filters(self) -> ActionResult:
        response = self.transcribe_backend.list_vocabulary_filters(
            name_contains=self._get_param("NameContains"),
            next_token=self._get_param("NextToken"),
            max_results=self._get_param("MaxResults"),
        )
        return ActionResult(response)

    # --- LanguageModel CRUD ---

    def create_language_model(self) -> ActionResult:
        response = self.transcribe_backend.create_language_model(
            language_code=self._get_param("LanguageCode"),
            base_model_name=self._get_param("BaseModelName"),
            model_name=self._get_param("ModelName"),
            input_data_config=self._get_param("InputDataConfig"),
            tags=self._get_param("Tags"),
        )
        return ActionResult(response)

    def describe_language_model(self) -> ActionResult:
        response = self.transcribe_backend.describe_language_model(
            model_name=self._get_param("ModelName"),
        )
        return ActionResult(response)

    def delete_language_model(self) -> ActionResult:
        self.transcribe_backend.delete_language_model(
            model_name=self._get_param("ModelName"),
        )
        return EmptyResult()

    def list_language_models(self) -> ActionResult:
        response = self.transcribe_backend.list_language_models(
            status_equals=self._get_param("StatusEquals"),
            name_contains=self._get_param("NameContains"),
            next_token=self._get_param("NextToken"),
            max_results=self._get_param("MaxResults"),
        )
        return ActionResult(response)
