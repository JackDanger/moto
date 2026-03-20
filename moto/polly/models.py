import datetime
import uuid
from typing import Any, Optional
from xml.etree import ElementTree as ET

from moto.core.base_backend import BackendDict, BaseBackend
from moto.core.common_models import BaseModel

from .resources import VOICE_DATA
from .utils import make_arn_for_lexicon


class Lexicon(BaseModel):
    def __init__(self, name: str, content: str, account_id: str, region_name: str):
        self.name = name
        self.content = content
        self.size = 0
        self.alphabet = None
        self.last_modified = None
        self.language_code = None
        self.lexemes_count = 0
        self.arn = make_arn_for_lexicon(account_id, name, region_name)

        self.update()

    def update(self, content: Optional[str] = None) -> None:
        if content is not None:
            self.content = content

        # Probably a very naive approach, but it'll do for now.
        try:
            root = ET.fromstring(self.content)
            self.size = len(self.content)
            self.last_modified = int(  # type: ignore
                (
                    datetime.datetime.now() - datetime.datetime(1970, 1, 1)
                ).total_seconds()
            )
            self.lexemes_count = len(root.findall("."))

            for key, value in root.attrib.items():
                if key.endswith("alphabet"):
                    self.alphabet = value  # type: ignore
                elif key.endswith("lang"):
                    self.language_code = value  # type: ignore

        except Exception as err:
            raise ValueError(f"Failure parsing XML: {err}")

    def to_dict(self) -> dict[str, Any]:
        return {
            "Attributes": {
                "Alphabet": self.alphabet,
                "LanguageCode": self.language_code,
                "LastModified": self.last_modified,
                "LexemesCount": self.lexemes_count,
                "LexiconArn": self.arn,
                "Size": self.size,
            }
        }

    def __repr__(self) -> str:
        return f"<Lexicon {self.name}>"


class SpeechSynthesisTask(BaseModel):
    def __init__(
        self,
        engine: Optional[str],
        language_code: Optional[str],
        lexicon_names: Optional[list[str]],
        output_format: str,
        output_s3_bucket_name: str,
        output_s3_key_prefix: Optional[str],
        sample_rate: Optional[str],
        sns_topic_arn: Optional[str],
        speech_mark_types: Optional[list[str]],
        text_type: Optional[str],
        voice_id: str,
    ):
        self.task_id = str(uuid.uuid4())
        self.task_status = "completed"
        self.task_status_reason: Optional[str] = None
        self.engine = engine or "standard"
        self.language_code = language_code
        self.lexicon_names = lexicon_names or []
        self.output_format = output_format
        self.output_s3_bucket_name = output_s3_bucket_name
        self.output_s3_key_prefix = output_s3_key_prefix or ""
        self.sample_rate = sample_rate
        self.sns_topic_arn = sns_topic_arn
        self.speech_mark_types = speech_mark_types or []
        self.text_type = text_type or "text"
        self.voice_id = voice_id
        self.creation_time = datetime.datetime.now(datetime.timezone.utc).timestamp()
        self.request_characters = 0
        self.output_uri = (
            f"https://s3.amazonaws.com/{output_s3_bucket_name}/"
            f"{self.output_s3_key_prefix}{self.task_id}.{output_format}"
        )

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {
            "TaskId": self.task_id,
            "TaskStatus": self.task_status,
            "OutputUri": self.output_uri,
            "CreationTime": self.creation_time,
            "RequestCharacters": self.request_characters,
            "Engine": self.engine,
            "OutputFormat": self.output_format,
            "VoiceId": self.voice_id,
            "TextType": self.text_type,
            "LexiconNames": self.lexicon_names,
            "SpeechMarkTypes": self.speech_mark_types,
        }
        if self.language_code is not None:
            result["LanguageCode"] = self.language_code
        if self.sample_rate is not None:
            result["SampleRate"] = self.sample_rate
        if self.sns_topic_arn is not None:
            result["SnsTopicArn"] = self.sns_topic_arn
        if self.task_status_reason is not None:
            result["TaskStatusReason"] = self.task_status_reason
        return result


class PollyBackend(BaseBackend):
    def __init__(self, region_name: str, account_id: str):
        super().__init__(region_name, account_id)
        self._lexicons: dict[str, Lexicon] = {}
        self._speech_synthesis_tasks: dict[str, SpeechSynthesisTask] = {}

    def describe_voices(self, language_code: str) -> list[dict[str, Any]]:
        """
        Pagination is not yet implemented
        """
        if language_code is None:
            return VOICE_DATA

        return [item for item in VOICE_DATA if item["LanguageCode"] == language_code]

    def delete_lexicon(self, name: str) -> None:
        # implement here
        del self._lexicons[name]

    def get_lexicon(self, name: str) -> Lexicon:
        # Raises KeyError
        return self._lexicons[name]

    def list_lexicons(self) -> list[dict[str, Any]]:
        """
        Pagination is not yet implemented
        """

        result = []

        for name, lexicon in self._lexicons.items():
            lexicon_dict = lexicon.to_dict()
            lexicon_dict["Name"] = name

            result.append(lexicon_dict)

        return result

    def put_lexicon(self, name: str, content: str) -> None:
        # If lexicon content is bad, it will raise ValueError
        if name in self._lexicons:
            # Regenerated all the stats from the XML
            # but keeps the ARN
            self._lexicons[name].update(content)
        else:
            lexicon = Lexicon(
                name, content, self.account_id, region_name=self.region_name
            )
            self._lexicons[name] = lexicon

    def start_speech_synthesis_task(
        self,
        engine: Optional[str],
        language_code: Optional[str],
        lexicon_names: Optional[list[str]],
        output_format: str,
        output_s3_bucket_name: str,
        output_s3_key_prefix: Optional[str],
        sample_rate: Optional[str],
        sns_topic_arn: Optional[str],
        speech_mark_types: Optional[list[str]],
        text_type: Optional[str],
        voice_id: str,
    ) -> dict[str, Any]:
        task = SpeechSynthesisTask(
            engine=engine,
            language_code=language_code,
            lexicon_names=lexicon_names,
            output_format=output_format,
            output_s3_bucket_name=output_s3_bucket_name,
            output_s3_key_prefix=output_s3_key_prefix,
            sample_rate=sample_rate,
            sns_topic_arn=sns_topic_arn,
            speech_mark_types=speech_mark_types,
            text_type=text_type,
            voice_id=voice_id,
        )
        self._speech_synthesis_tasks[task.task_id] = task
        return task.to_dict()

    def get_speech_synthesis_task(self, task_id: str) -> dict[str, Any]:
        if task_id not in self._speech_synthesis_tasks:
            raise KeyError(task_id)
        return self._speech_synthesis_tasks[task_id].to_dict()

    def list_speech_synthesis_tasks(
        self,
        max_results: Optional[int],
        next_token: Optional[str],
        status: Optional[str],
    ) -> tuple[list[dict[str, Any]], Optional[str]]:
        tasks = list(self._speech_synthesis_tasks.values())

        if status is not None:
            tasks = [t for t in tasks if t.task_status == status]

        # Simple pagination: use next_token as an index offset
        start = 0
        if next_token is not None:
            try:
                start = int(next_token)
            except ValueError:
                start = 0

        page_size = max_results if max_results is not None else 100
        page = tasks[start : start + page_size]
        new_next_token: Optional[str] = None
        if start + page_size < len(tasks):
            new_next_token = str(start + page_size)

        return [t.to_dict() for t in page], new_next_token


polly_backends = BackendDict(PollyBackend, "polly")
