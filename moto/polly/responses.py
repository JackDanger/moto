import json
import re
from typing import Any, Union
from urllib.parse import urlsplit

from moto.core.responses import BaseResponse

from .models import PollyBackend, polly_backends
from .resources import LANGUAGE_CODES, VOICE_IDS

LEXICON_NAME_REGEX = re.compile(r"^[0-9A-Za-z]{1,20}$")


class PollyResponse(BaseResponse):
    def __init__(self) -> None:
        super().__init__(service_name="polly")

    @property
    def polly_backend(self) -> PollyBackend:
        return polly_backends[self.current_account][self.region]

    @property
    def json(self) -> dict[str, Any]:  # type: ignore[misc]
        if not hasattr(self, "_json"):
            self._json = json.loads(self.body)
        return self._json

    def _error(self, code: str, message: str) -> tuple[str, dict[str, int]]:
        return json.dumps({"__type": code, "message": message}), {"status": 400}

    def _get_action(self) -> str:
        # Amazon is now naming things /v1/api_name
        url_parts = urlsplit(self.uri).path.lstrip("/").split("/")
        # [0] = 'v1'

        return url_parts[1]

    # DescribeVoices
    def voices(self) -> Union[str, tuple[str, dict[str, int]]]:
        language_code = self._get_param("LanguageCode")
        engine = self._get_param("Engine")

        if language_code is not None and language_code not in LANGUAGE_CODES:
            all_codes = ", ".join(LANGUAGE_CODES)  # type: ignore
            msg = (
                f"1 validation error detected: Value '{language_code}' at 'languageCode' failed to satisfy constraint: "
                f"Member must satisfy enum value set: [{all_codes}]"
            )
            return msg, {"status": 400}

        voices = self.polly_backend.describe_voices(language_code, engine=engine)

        return json.dumps({"Voices": voices})

    def lexicons(self) -> Union[str, tuple[str, dict[str, int]]]:
        # Dish out requests based on methods

        # anything after the /v1/lexicons/
        args = urlsplit(self.uri).path.lstrip("/").split("/")[2:]

        if self.method == "GET":
            if len(args) == 0:
                return self._get_lexicons_list()
            else:
                return self._get_lexicon(*args)
        elif self.method == "PUT":
            return self._put_lexicons(*args)
        elif self.method == "DELETE":
            return self._delete_lexicon(*args)

        return self._error("InvalidAction", "Bad route")

    # PutLexicon
    def _put_lexicons(
        self, lexicon_name: str
    ) -> Union[str, tuple[str, dict[str, int]]]:
        if LEXICON_NAME_REGEX.match(lexicon_name) is None:
            return self._error(
                "InvalidParameterValue", "Lexicon name must match [0-9A-Za-z]{1,20}"
            )

        if "Content" not in self.json:
            return self._error("MissingParameter", "Content is missing from the body")

        self.polly_backend.put_lexicon(lexicon_name, self.json["Content"])

        return ""

    # ListLexicons
    def _get_lexicons_list(self) -> str:
        result = {"Lexicons": self.polly_backend.list_lexicons()}

        return json.dumps(result)

    # GetLexicon
    def _get_lexicon(self, lexicon_name: str) -> Union[str, tuple[str, dict[str, int]]]:
        try:
            lexicon = self.polly_backend.get_lexicon(lexicon_name)
        except KeyError:
            return self._error("LexiconNotFoundException", "Lexicon not found")

        result = {
            "Lexicon": {"Name": lexicon_name, "Content": lexicon.content},
            "LexiconAttributes": lexicon.to_dict()["Attributes"],
        }

        return json.dumps(result)

    # DeleteLexicon
    def _delete_lexicon(
        self, lexicon_name: str
    ) -> Union[str, tuple[str, dict[str, int]]]:
        try:
            self.polly_backend.delete_lexicon(lexicon_name)
        except KeyError:
            return self._error("LexiconNotFoundException", "Lexicon not found")

        return ""

    # StartSpeechSynthesisTask / GetSpeechSynthesisTask / ListSpeechSynthesisTasks
    def synthesis_tasks(self) -> Union[str, tuple[str, dict[str, int]]]:
        url_parts = urlsplit(self.uri).path.lstrip("/").split("/")
        # url_parts: ['v1', 'synthesisTasks'] or ['v1', 'synthesisTasks', '<task_id>']

        if self.method == "POST":
            return self._start_speech_synthesis_task()
        elif self.method == "GET":
            if len(url_parts) >= 3 and url_parts[2]:
                task_id = url_parts[2]
                return self._get_speech_synthesis_task(task_id)
            else:
                return self._list_speech_synthesis_tasks()
        return self._error("InvalidAction", "Bad route")

    def _start_speech_synthesis_task(self) -> Union[str, tuple[str, dict[str, int]]]:
        if "OutputFormat" not in self.json:
            return self._error("MissingParameter", "Missing parameter OutputFormat")
        if "OutputS3BucketName" not in self.json:
            return self._error("MissingParameter", "Missing parameter OutputS3BucketName")
        if "Text" not in self.json:
            return self._error("MissingParameter", "Missing parameter Text")
        if "VoiceId" not in self.json:
            return self._error("MissingParameter", "Missing parameter VoiceId")

        task = self.polly_backend.start_speech_synthesis_task(
            engine=self.json.get("Engine"),
            language_code=self.json.get("LanguageCode"),
            lexicon_names=self.json.get("LexiconNames"),
            output_format=self.json["OutputFormat"],
            output_s3_bucket_name=self.json["OutputS3BucketName"],
            output_s3_key_prefix=self.json.get("OutputS3KeyPrefix"),
            sample_rate=self.json.get("SampleRate"),
            sns_topic_arn=self.json.get("SnsTopicArn"),
            speech_mark_types=self.json.get("SpeechMarkTypes"),
            text_type=self.json.get("TextType"),
            voice_id=self.json["VoiceId"],
        )
        return json.dumps({"SynthesisTask": task})

    def _get_speech_synthesis_task(
        self, task_id: str
    ) -> Union[str, tuple[str, dict[str, int]]]:
        try:
            task = self.polly_backend.get_speech_synthesis_task(task_id)
        except KeyError:
            return self._error("SynthesisTaskNotFoundException", "Synthesis task not found")
        return json.dumps({"SynthesisTask": task})

    def _list_speech_synthesis_tasks(self) -> str:
        max_results_str = self._get_param("MaxResults")
        max_results = int(max_results_str) if max_results_str is not None else None
        next_token = self._get_param("NextToken")
        status = self._get_param("Status")

        tasks, new_next_token = self.polly_backend.list_speech_synthesis_tasks(
            max_results=max_results,
            next_token=next_token,
            status=status,
        )
        result: dict[str, Any] = {"SynthesisTasks": tasks}
        if new_next_token is not None:
            result["NextToken"] = new_next_token
        return json.dumps(result)

    # SynthesizeSpeech
    def speech(self) -> tuple[str, dict[str, Any]]:
        # Sanity check params
        args = {
            "lexicon_names": None,
            "sample_rate": 22050,
            "speech_marks": None,
            "text": None,
            "text_type": "text",
        }

        if "LexiconNames" in self.json:
            for lex in self.json["LexiconNames"]:
                try:
                    self.polly_backend.get_lexicon(lex)
                except KeyError:
                    return self._error("LexiconNotFoundException", "Lexicon not found")

            args["lexicon_names"] = self.json["LexiconNames"]

        if "OutputFormat" not in self.json:
            return self._error("MissingParameter", "Missing parameter OutputFormat")
        if self.json["OutputFormat"] not in ("json", "mp3", "ogg_vorbis", "pcm"):
            return self._error(
                "InvalidParameterValue", "Not one of json, mp3, ogg_vorbis, pcm"
            )
        args["output_format"] = self.json["OutputFormat"]

        if "SampleRate" in self.json:
            sample_rate = int(self.json["SampleRate"])
            if sample_rate not in (8000, 16000, 22050):
                return self._error(
                    "InvalidSampleRateException",
                    "The specified sample rate is not valid.",
                )
            args["sample_rate"] = sample_rate

        if "SpeechMarkTypes" in self.json:
            for value in self.json["SpeechMarkTypes"]:
                if value not in ("sentance", "ssml", "viseme", "word"):
                    return self._error(
                        "InvalidParameterValue",
                        "Not one of sentance, ssml, viseme, word",
                    )
            args["speech_marks"] = self.json["SpeechMarkTypes"]

        if "Text" not in self.json:
            return self._error("MissingParameter", "Missing parameter Text")
        args["text"] = self.json["Text"]

        if "TextType" in self.json:
            if self.json["TextType"] not in ("ssml", "text"):
                return self._error("InvalidParameterValue", "Not one of ssml, text")
            args["text_type"] = self.json["TextType"]

        if "VoiceId" not in self.json:
            return self._error("MissingParameter", "Missing parameter VoiceId")
        if self.json["VoiceId"] not in VOICE_IDS:
            all_voices = ", ".join(VOICE_IDS)  # type: ignore
            return self._error("InvalidParameterValue", f"Not one of {all_voices}")
        args["voice_id"] = self.json["VoiceId"]

        # More validation
        if len(args["text"]) > 3000:  # type: ignore
            return self._error("TextLengthExceededException", "Text too long")

        if args["speech_marks"] is not None and args["output_format"] != "json":
            return self._error(
                "MarksNotSupportedForFormatException", "OutputFormat must be json"
            )
        if args["speech_marks"] is not None and args["text_type"] == "text":
            return self._error(
                "SsmlMarksNotSupportedForTextTypeException", "TextType must be ssml"
            )

        content_type = "audio/json"
        if args["output_format"] == "mp3":
            content_type = "audio/mpeg"
        elif args["output_format"] == "ogg_vorbis":
            content_type = "audio/ogg"
        elif args["output_format"] == "pcm":
            content_type = "audio/pcm"

        request_characters = len(args["text"])  # type: ignore[arg-type]
        headers = {
            "Content-Type": content_type,
            "x-amzn-RequestCharacters": str(request_characters),
        }

        return "\x00\x00\x00\x00\x00\x00\x00\x00", headers
