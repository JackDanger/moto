"""LexModelsV2Backend class with methods for supported APIs."""

import uuid
from datetime import datetime
from typing import Any, Optional

from moto.core.base_backend import BackendDict, BaseBackend

from ..utilities.tagging_service import TaggingService
from .exceptions import ConflictException, ResourceNotFoundException


class FakeBot:
    failure_reasons: list[str]

    def __init__(
        self,
        account_id: str,
        region_name: str,
        bot_name: str,
        description: str,
        role_arn: str,
        data_privacy: Optional[dict[str, Any]],
        idle_session_ttl_in_seconds: int,
        bot_type: str,
        bot_members: Optional[dict[str, Any]],
    ):
        self.account_id = account_id
        self.region_name = region_name
        self.id = str(uuid.uuid4())
        self.bot_name = bot_name
        self.description = description
        self.role_arn = role_arn
        self.data_privacy = data_privacy
        self.idle_session_ttl_in_seconds = idle_session_ttl_in_seconds
        self.bot_type = bot_type
        self.bot_members = bot_members
        self.status = "Available"
        self.creation_date_time = datetime.now().isoformat()
        self.last_updated_date_time = datetime.now().isoformat()
        self.failure_reasons = []
        self.arn = self._generate_arn()

    def _generate_arn(self) -> str:
        return f"arn:aws:lex:{self.region_name}:{self.account_id}:bot/{self.id}"


class FakeBotAlias:
    parent_bot_networks: list[str]
    history_events: list[str]

    def __init__(
        self,
        account_id: str,
        region_name: str,
        bot_alias_name: str,
        description: str,
        bot_version: str,
        bot_alias_locale_settings: Optional[dict[str, Any]],
        conversation_log_settings: Optional[dict[str, Any]],
        sentiment_analysis_settings: Optional[dict[str, Any]],
        bot_id: str,
    ):
        self.account_id = account_id
        self.region_name = region_name
        self.id = str(uuid.uuid4())
        self.bot_alias_name = bot_alias_name
        self.description = description
        self.bot_version = bot_version
        self.bot_alias_locale_settings = bot_alias_locale_settings
        self.conversation_log_settings = conversation_log_settings
        self.sentiment_analysis_settings = sentiment_analysis_settings
        self.status = "Available"
        self.bot_id = bot_id
        self.creation_date_time = datetime.now().isoformat()
        self.last_updated_date_time = datetime.now().isoformat()
        self.parent_bot_networks = []
        self.history_events = []
        self.arn = self._generate_arn()

    def _generate_arn(self) -> str:
        return f"arn:aws:lex:{self.region_name}:{self.account_id}:bot-alias/{self.bot_id}/{self.id}"


class FakeBotLocale:
    def __init__(
        self,
        bot_id: str,
        bot_version: str,
        locale_id: str,
        description: str,
        nlu_intent_confidence_threshold: float,
        voice_settings: Optional[dict[str, Any]],
    ):
        self.bot_id = bot_id
        self.bot_version = bot_version
        self.locale_id = locale_id
        self.description = description
        self.nlu_intent_confidence_threshold = nlu_intent_confidence_threshold
        self.voice_settings = voice_settings
        self.status = "Built"
        self.creation_date_time = datetime.now().isoformat()
        self.last_updated_date_time = datetime.now().isoformat()
        self.last_build_submitted_date_time = datetime.now().isoformat()
        self.failure_reasons: list[str] = []
        self.intents_count = 0
        self.slot_types_count = 0
        self.bot_locale_history_events: list[dict[str, Any]] = []
        self.recommended_actions: list[str] = []


class FakeBotVersion:
    def __init__(
        self,
        account_id: str,
        region_name: str,
        bot_id: str,
        description: str,
        bot_version_locale_specification: dict[str, Any],
    ):
        self.account_id = account_id
        self.region_name = region_name
        self.bot_id = bot_id
        self.bot_version = str(uuid.uuid4())[:8]
        self.description = description
        self.bot_version_locale_specification = bot_version_locale_specification
        self.status = "Available"
        self.creation_date_time = datetime.now().isoformat()
        self.failure_reasons: list[str] = []


class FakeIntent:
    def __init__(
        self,
        bot_id: str,
        bot_version: str,
        locale_id: str,
        intent_name: str,
        description: str,
        parent_intent_signature: Optional[str],
        sample_utterances: Optional[list[dict[str, Any]]],
        dialog_code_hook: Optional[dict[str, Any]],
        fulfillment_code_hook: Optional[dict[str, Any]],
        intent_confirmation_setting: Optional[dict[str, Any]],
        intent_closing_setting: Optional[dict[str, Any]],
        input_contexts: Optional[list[dict[str, Any]]],
        output_contexts: Optional[list[dict[str, Any]]],
        kendra_configuration: Optional[dict[str, Any]],
        initial_response_setting: Optional[dict[str, Any]],
        qn_a_intent_configuration: Optional[dict[str, Any]],
    ):
        self.intent_id = str(uuid.uuid4())
        self.bot_id = bot_id
        self.bot_version = bot_version
        self.locale_id = locale_id
        self.intent_name = intent_name
        self.description = description
        self.parent_intent_signature = parent_intent_signature
        self.sample_utterances = sample_utterances or []
        self.dialog_code_hook = dialog_code_hook
        self.fulfillment_code_hook = fulfillment_code_hook
        self.intent_confirmation_setting = intent_confirmation_setting
        self.intent_closing_setting = intent_closing_setting
        self.input_contexts = input_contexts or []
        self.output_contexts = output_contexts or []
        self.kendra_configuration = kendra_configuration
        self.initial_response_setting = initial_response_setting
        self.qn_a_intent_configuration = qn_a_intent_configuration
        self.creation_date_time = datetime.now().isoformat()
        self.last_updated_date_time = datetime.now().isoformat()


class FakeSlot:
    def __init__(
        self,
        bot_id: str,
        bot_version: str,
        locale_id: str,
        intent_id: str,
        slot_name: str,
        description: str,
        slot_type_id: Optional[str],
        value_elicitation_setting: Optional[dict[str, Any]],
        obfuscation_setting: Optional[dict[str, Any]],
        multiple_values_setting: Optional[dict[str, Any]],
        sub_slot_setting: Optional[dict[str, Any]],
    ):
        self.slot_id = str(uuid.uuid4())
        self.bot_id = bot_id
        self.bot_version = bot_version
        self.locale_id = locale_id
        self.intent_id = intent_id
        self.slot_name = slot_name
        self.description = description
        self.slot_type_id = slot_type_id
        self.value_elicitation_setting = value_elicitation_setting
        self.obfuscation_setting = obfuscation_setting
        self.multiple_values_setting = multiple_values_setting
        self.sub_slot_setting = sub_slot_setting
        self.creation_date_time = datetime.now().isoformat()
        self.last_updated_date_time = datetime.now().isoformat()


class FakeSlotType:
    def __init__(
        self,
        bot_id: str,
        bot_version: str,
        locale_id: str,
        slot_type_name: str,
        description: str,
        slot_type_values: Optional[list[dict[str, Any]]],
        value_selection_setting: Optional[dict[str, Any]],
        parent_slot_type_signature: Optional[str],
        external_source_setting: Optional[dict[str, Any]],
        composite_slot_type_setting: Optional[dict[str, Any]],
    ):
        self.slot_type_id = str(uuid.uuid4())
        self.bot_id = bot_id
        self.bot_version = bot_version
        self.locale_id = locale_id
        self.slot_type_name = slot_type_name
        self.description = description
        self.slot_type_values = slot_type_values or []
        self.value_selection_setting = value_selection_setting
        self.parent_slot_type_signature = parent_slot_type_signature
        self.external_source_setting = external_source_setting
        self.composite_slot_type_setting = composite_slot_type_setting
        self.creation_date_time = datetime.now().isoformat()
        self.last_updated_date_time = datetime.now().isoformat()


class FakeResourcePolicy:
    def __init__(self, resource_arn: str, policy: str):
        self.resource_arn = resource_arn
        self.policy = policy
        self.revision_id = str(uuid.uuid4())


class LexModelsV2Backend(BaseBackend):
    """Implementation of LexModelsV2 APIs."""

    def __init__(self, region_name: str, account_id: str):
        super().__init__(region_name, account_id)
        self.bots: dict[str, FakeBot] = {}
        self.bot_aliases: dict[str, FakeBotAlias] = {}
        self.bot_locales: dict[tuple[str, str, str], FakeBotLocale] = {}
        self.bot_versions: dict[tuple[str, str], FakeBotVersion] = {}
        self.intents: dict[str, FakeIntent] = {}
        self.slots: dict[str, FakeSlot] = {}
        self.slot_types: dict[str, FakeSlotType] = {}
        self.resource_policies: dict[str, FakeResourcePolicy] = {}
        self.tagger = TaggingService()

    def create_bot(
        self,
        bot_name: str,
        description: str,
        role_arn: str,
        data_privacy: Optional[dict[str, Any]],
        idle_session_ttl_in_seconds: int,
        bot_tags: Optional[dict[str, str]],
        test_bot_alias_tags: Optional[dict[str, str]],
        bot_type: str,
        bot_members: Optional[dict[str, Any]],
    ) -> dict[str, Any]:
        bot = FakeBot(
            account_id=self.account_id, region_name=self.region_name,
            bot_name=bot_name, description=description, role_arn=role_arn,
            data_privacy=data_privacy,
            idle_session_ttl_in_seconds=idle_session_ttl_in_seconds,
            bot_type=bot_type, bot_members=bot_members,
        )
        self.bots[bot.id] = bot
        if bot_tags:
            self.tag_resource(bot.arn, bot_tags)
        test_alias = FakeBotAlias(
            account_id=self.account_id, region_name=self.region_name,
            bot_alias_name="TestBotAlias", description="", bot_version="DRAFT",
            bot_alias_locale_settings={}, conversation_log_settings={},
            sentiment_analysis_settings={}, bot_id=bot.id,
        )
        self.bot_aliases[test_alias.id] = test_alias
        return {
            "botId": bot.id, "botName": bot.bot_name, "description": bot.description,
            "roleArn": bot.role_arn, "dataPrivacy": bot.data_privacy,
            "idleSessionTTLInSeconds": bot.idle_session_ttl_in_seconds,
            "botStatus": bot.status, "creationDateTime": bot.creation_date_time,
            "botTags": self.list_tags_for_resource(bot.arn),
            "testBotAliasTags": test_bot_alias_tags,
            "botType": bot.bot_type, "botMembers": bot.bot_members,
        }

    def describe_bot(self, bot_id: str) -> dict[str, Any]:
        if bot_id not in self.bots:
            raise ResourceNotFoundException(f"Could not find bot: {bot_id}")
        bot = self.bots[bot_id]
        return {
            "botId": bot.id, "botName": bot.bot_name, "description": bot.description,
            "roleArn": bot.role_arn, "dataPrivacy": bot.data_privacy,
            "idleSessionTTLInSeconds": bot.idle_session_ttl_in_seconds,
            "botStatus": bot.status, "creationDateTime": bot.creation_date_time,
            "lastUpdatedDateTime": bot.last_updated_date_time,
            "botType": bot.bot_type, "botMembers": bot.bot_members,
            "failureReasons": bot.failure_reasons,
        }

    def update_bot(
        self, bot_id: str, bot_name: str, description: str, role_arn: str,
        data_privacy: Optional[dict[str, Any]], idle_session_ttl_in_seconds: int,
        bot_type: str, bot_members: Optional[dict[str, Any]],
    ) -> dict[str, Any]:
        if bot_id not in self.bots:
            raise ResourceNotFoundException(f"Could not find bot: {bot_id}")
        bot = self.bots[bot_id]
        bot.bot_name = bot_name
        bot.description = description
        bot.role_arn = role_arn
        bot.data_privacy = data_privacy
        bot.idle_session_ttl_in_seconds = idle_session_ttl_in_seconds
        bot.bot_type = bot_type
        bot.bot_members = bot_members
        bot.last_updated_date_time = datetime.now().isoformat()
        return {
            "botId": bot.id, "botName": bot.bot_name, "description": bot.description,
            "roleArn": bot.role_arn, "dataPrivacy": bot.data_privacy,
            "idleSessionTTLInSeconds": bot.idle_session_ttl_in_seconds,
            "botStatus": bot.status, "creationDateTime": bot.creation_date_time,
            "lastUpdatedDateTime": bot.last_updated_date_time,
            "botType": bot.bot_type, "botMembers": bot.bot_members,
        }

    def list_bots(self) -> list[dict[str, Any]]:
        return [
            {
                "botId": bot.id, "botName": bot.bot_name, "description": bot.description,
                "botStatus": bot.status, "latestBotVersion": 1,
                "lastUpdatedDateTime": bot.last_updated_date_time, "botType": bot.bot_type,
            }
            for bot in self.bots.values()
        ]

    def delete_bot(self, bot_id: str, skip_resource_in_use_check: bool) -> tuple[str, str]:
        if bot_id not in self.bots:
            raise ResourceNotFoundException(f"Could not find bot: {bot_id}")
        bot = self.bots.pop(bot_id)
        return bot.id, bot.status

    def create_bot_alias(
        self, bot_alias_name: str, description: str, bot_version: str,
        bot_alias_locale_settings: Optional[dict[str, Any]],
        conversation_log_settings: Optional[dict[str, Any]],
        sentiment_analysis_settings: Optional[dict[str, Any]],
        bot_id: str, tags: Optional[dict[str, str]],
    ) -> dict[str, Any]:
        bot_alias = FakeBotAlias(
            self.account_id, self.region_name, bot_alias_name, description, bot_version,
            bot_alias_locale_settings, conversation_log_settings, sentiment_analysis_settings, bot_id,
        )
        self.bot_aliases[bot_alias.id] = bot_alias
        if tags:
            self.tag_resource(bot_alias.arn, tags)
        return {
            "botAliasId": bot_alias.id, "botAliasName": bot_alias.bot_alias_name,
            "description": bot_alias.description, "botVersion": bot_alias.bot_version,
            "botAliasLocaleSettings": bot_alias.bot_alias_locale_settings,
            "conversationLogSettings": bot_alias.conversation_log_settings,
            "sentimentAnalysisSettings": bot_alias.sentiment_analysis_settings,
            "botAliasStatus": bot_alias.status, "creationDateTime": bot_alias.creation_date_time,
            "botId": bot_alias.bot_id, "tags": self.list_tags_for_resource(bot_alias.arn),
        }

    def describe_bot_alias(self, bot_alias_id: str, bot_id: str) -> dict[str, Any]:
        if bot_alias_id not in self.bot_aliases:
            raise ResourceNotFoundException(f"Could not find bot alias: {bot_alias_id}")
        ba = self.bot_aliases[bot_alias_id]
        return {
            "botAliasId": ba.id, "botAliasName": ba.bot_alias_name,
            "description": ba.description, "botVersion": ba.bot_version,
            "botAliasLocaleSettings": ba.bot_alias_locale_settings,
            "conversationLogSettings": ba.conversation_log_settings,
            "sentimentAnalysisSettings": ba.sentiment_analysis_settings,
            "botAliasHistoryEvents": ba.history_events,
            "botAliasStatus": ba.status, "botId": ba.bot_id,
            "creationDateTime": ba.creation_date_time,
            "lastUpdatedDateTime": ba.last_updated_date_time,
            "parentBotNetworks": ba.parent_bot_networks,
        }

    def update_bot_alias(
        self, bot_alias_id: str, bot_alias_name: str, description: str, bot_version: str,
        bot_alias_locale_settings: Optional[dict[str, Any]],
        conversation_log_settings: Optional[dict[str, Any]],
        sentiment_analysis_settings: Optional[dict[str, Any]], bot_id: str,
    ) -> dict[str, Any]:
        if bot_alias_id not in self.bot_aliases:
            raise ResourceNotFoundException(f"Could not find bot alias: {bot_alias_id}")
        ba = self.bot_aliases[bot_alias_id]
        ba.bot_alias_name = bot_alias_name
        ba.description = description
        ba.bot_version = bot_version
        ba.bot_alias_locale_settings = bot_alias_locale_settings
        ba.conversation_log_settings = conversation_log_settings
        ba.sentiment_analysis_settings = sentiment_analysis_settings
        ba.bot_id = bot_id
        ba.last_updated_date_time = datetime.now().isoformat()
        return {
            "botAliasId": ba.id, "botAliasName": ba.bot_alias_name,
            "description": ba.description, "botVersion": ba.bot_version,
            "botAliasLocaleSettings": ba.bot_alias_locale_settings,
            "conversationLogSettings": ba.conversation_log_settings,
            "sentimentAnalysisSettings": ba.sentiment_analysis_settings,
            "botAliasStatus": ba.status, "botId": ba.bot_id,
            "creationDateTime": ba.creation_date_time,
            "lastUpdatedDateTime": ba.last_updated_date_time,
        }

    def list_bot_aliases(self, bot_id: str, max_results: int) -> tuple[list[dict[str, Any]], Optional[str]]:
        summaries = [
            {
                "botAliasId": ba.id, "botAliasName": ba.bot_alias_name,
                "description": ba.description, "botVersion": ba.bot_version,
                "botAliasStatus": ba.status, "creationDateTime": ba.creation_date_time,
                "lastUpdatedDateTime": ba.last_updated_date_time,
            }
            for ba in self.bot_aliases.values()
            if ba.bot_id == bot_id
        ]
        return summaries, bot_id

    def delete_bot_alias(self, bot_alias_id: str, bot_id: str, skip_resource_in_use_check: bool) -> tuple[str, str, str]:
        if bot_alias_id not in self.bot_aliases:
            raise ResourceNotFoundException(f"Could not find bot alias: {bot_alias_id}")
        ba = self.bot_aliases.pop(bot_alias_id)
        return ba.id, ba.bot_id, ba.status

    def create_bot_locale(
        self, bot_id: str, bot_version: str, locale_id: str, description: str,
        nlu_intent_confidence_threshold: float, voice_settings: Optional[dict[str, Any]],
    ) -> dict[str, Any]:
        key = (bot_id, bot_version, locale_id)
        if key in self.bot_locales:
            raise ConflictException(
                f"Bot locale already exists for bot {bot_id} version {bot_version} locale {locale_id}"
            )
        locale = FakeBotLocale(
            bot_id=bot_id, bot_version=bot_version, locale_id=locale_id,
            description=description,
            nlu_intent_confidence_threshold=nlu_intent_confidence_threshold,
            voice_settings=voice_settings,
        )
        self.bot_locales[key] = locale
        return {
            "botId": bot_id, "botVersion": bot_version, "localeId": locale_id,
            "localeName": locale_id, "description": description,
            "nluIntentConfidenceThreshold": nlu_intent_confidence_threshold,
            "voiceSettings": voice_settings, "botLocaleStatus": locale.status,
            "creationDateTime": locale.creation_date_time,
        }

    def describe_bot_locale(self, bot_id: str, bot_version: str, locale_id: str) -> dict[str, Any]:
        key = (bot_id, bot_version, locale_id)
        if key not in self.bot_locales:
            raise ResourceNotFoundException(
                f"Could not find locale {locale_id} for bot {bot_id} version {bot_version}"
            )
        locale = self.bot_locales[key]
        return {
            "botId": bot_id, "botVersion": bot_version,
            "localeId": locale.locale_id, "localeName": locale.locale_id,
            "description": locale.description,
            "nluIntentConfidenceThreshold": locale.nlu_intent_confidence_threshold,
            "voiceSettings": locale.voice_settings,
            "intentsCount": locale.intents_count,
            "slotTypesCount": locale.slot_types_count,
            "botLocaleStatus": locale.status, "failureReasons": locale.failure_reasons,
            "creationDateTime": locale.creation_date_time,
            "lastUpdatedDateTime": locale.last_updated_date_time,
            "lastBuildSubmittedDateTime": locale.last_build_submitted_date_time,
            "botLocaleHistoryEvents": locale.bot_locale_history_events,
            "recommendedActions": locale.recommended_actions,
        }

    def update_bot_locale(
        self, bot_id: str, bot_version: str, locale_id: str, description: str,
        nlu_intent_confidence_threshold: float, voice_settings: Optional[dict[str, Any]],
    ) -> dict[str, Any]:
        key = (bot_id, bot_version, locale_id)
        if key not in self.bot_locales:
            raise ResourceNotFoundException(
                f"Could not find locale {locale_id} for bot {bot_id} version {bot_version}"
            )
        locale = self.bot_locales[key]
        locale.description = description
        locale.nlu_intent_confidence_threshold = nlu_intent_confidence_threshold
        locale.voice_settings = voice_settings
        locale.last_updated_date_time = datetime.now().isoformat()
        return {
            "botId": bot_id, "botVersion": bot_version,
            "localeId": locale.locale_id, "localeName": locale.locale_id,
            "description": locale.description,
            "nluIntentConfidenceThreshold": locale.nlu_intent_confidence_threshold,
            "voiceSettings": locale.voice_settings, "botLocaleStatus": locale.status,
            "failureReasons": locale.failure_reasons,
            "creationDateTime": locale.creation_date_time,
            "lastUpdatedDateTime": locale.last_updated_date_time,
            "recommendedActions": locale.recommended_actions,
        }

    def delete_bot_locale(self, bot_id: str, bot_version: str, locale_id: str) -> dict[str, Any]:
        key = (bot_id, bot_version, locale_id)
        if key not in self.bot_locales:
            raise ResourceNotFoundException(
                f"Could not find locale {locale_id} for bot {bot_id} version {bot_version}"
            )
        self.bot_locales.pop(key)
        return {"botId": bot_id, "botVersion": bot_version, "localeId": locale_id, "botLocaleStatus": "Deleting"}

    def list_bot_locales(self, bot_id: str, bot_version: str) -> list[dict[str, Any]]:
        return [
            {
                "localeId": locale.locale_id, "localeName": locale.locale_id,
                "description": locale.description, "botLocaleStatus": locale.status,
                "lastUpdatedDateTime": locale.last_updated_date_time,
                "lastBuildSubmittedDateTime": locale.last_build_submitted_date_time,
            }
            for (bid, bv, _), locale in self.bot_locales.items()
            if bid == bot_id and bv == bot_version
        ]

    def build_bot_locale(self, bot_id: str, bot_version: str, locale_id: str) -> dict[str, Any]:
        key = (bot_id, bot_version, locale_id)
        if key not in self.bot_locales:
            raise ResourceNotFoundException(
                f"Could not find locale {locale_id} for bot {bot_id} version {bot_version}"
            )
        locale = self.bot_locales[key]
        locale.status = "Built"
        locale.last_build_submitted_date_time = datetime.now().isoformat()
        return {
            "botId": bot_id, "botVersion": bot_version, "localeId": locale_id,
            "botLocaleStatus": locale.status,
            "lastBuildSubmittedDateTime": locale.last_build_submitted_date_time,
        }

    def create_bot_version(
        self, bot_id: str, description: str, bot_version_locale_specification: dict[str, Any],
    ) -> dict[str, Any]:
        if bot_id not in self.bots:
            raise ResourceNotFoundException(f"Could not find bot: {bot_id}")
        bot = self.bots[bot_id]
        version = FakeBotVersion(
            account_id=self.account_id, region_name=self.region_name,
            bot_id=bot_id, description=description,
            bot_version_locale_specification=bot_version_locale_specification,
        )
        self.bot_versions[(bot_id, version.bot_version)] = version
        return {
            "botId": bot_id, "description": description, "botVersion": version.bot_version,
            "botVersionLocaleSpecification": bot_version_locale_specification,
            "botStatus": bot.status, "creationDateTime": version.creation_date_time,
            "failureReasons": version.failure_reasons,
        }

    def describe_bot_version(self, bot_id: str, bot_version: str) -> dict[str, Any]:
        key = (bot_id, bot_version)
        if key not in self.bot_versions:
            raise ResourceNotFoundException(
                f"Could not find bot version {bot_version} for bot {bot_id}"
            )
        if bot_id not in self.bots:
            raise ResourceNotFoundException(f"Could not find bot: {bot_id}")
        bot = self.bots[bot_id]
        version = self.bot_versions[key]
        return {
            "botId": bot_id, "botName": bot.bot_name, "botVersion": bot_version,
            "description": version.description, "roleArn": bot.role_arn,
            "dataPrivacy": bot.data_privacy,
            "idleSessionTTLInSeconds": bot.idle_session_ttl_in_seconds,
            "botStatus": version.status, "failureReasons": version.failure_reasons,
            "creationDateTime": version.creation_date_time,
            "botType": bot.bot_type, "botMembers": bot.bot_members,
        }

    def list_bot_versions(self, bot_id: str) -> list[dict[str, Any]]:
        if bot_id not in self.bots:
            raise ResourceNotFoundException(f"Could not find bot: {bot_id}")
        return [
            {
                "botVersion": v.bot_version, "description": v.description,
                "botStatus": v.status, "creationDateTime": v.creation_date_time,
            }
            for (bid, _), v in self.bot_versions.items()
            if bid == bot_id
        ]

    def delete_bot_version(self, bot_id: str, bot_version: str, skip_resource_in_use_check: bool) -> tuple[str, str, str]:
        key = (bot_id, bot_version)
        if key not in self.bot_versions:
            raise ResourceNotFoundException(
                f"Could not find bot version {bot_version} for bot {bot_id}"
            )
        version = self.bot_versions.pop(key)
        return bot_id, bot_version, version.status

    def create_intent(
        self, bot_id: str, bot_version: str, locale_id: str,
        intent_name: str, description: str, parent_intent_signature: Optional[str],
        sample_utterances: Optional[list[dict[str, Any]]],
        dialog_code_hook: Optional[dict[str, Any]],
        fulfillment_code_hook: Optional[dict[str, Any]],
        intent_confirmation_setting: Optional[dict[str, Any]],
        intent_closing_setting: Optional[dict[str, Any]],
        input_contexts: Optional[list[dict[str, Any]]],
        output_contexts: Optional[list[dict[str, Any]]],
        kendra_configuration: Optional[dict[str, Any]],
        initial_response_setting: Optional[dict[str, Any]],
        qn_a_intent_configuration: Optional[dict[str, Any]],
    ) -> dict[str, Any]:
        intent = FakeIntent(
            bot_id=bot_id, bot_version=bot_version, locale_id=locale_id,
            intent_name=intent_name, description=description,
            parent_intent_signature=parent_intent_signature,
            sample_utterances=sample_utterances, dialog_code_hook=dialog_code_hook,
            fulfillment_code_hook=fulfillment_code_hook,
            intent_confirmation_setting=intent_confirmation_setting,
            intent_closing_setting=intent_closing_setting,
            input_contexts=input_contexts, output_contexts=output_contexts,
            kendra_configuration=kendra_configuration,
            initial_response_setting=initial_response_setting,
            qn_a_intent_configuration=qn_a_intent_configuration,
        )
        self.intents[intent.intent_id] = intent
        key = (bot_id, bot_version, locale_id)
        if key in self.bot_locales:
            self.bot_locales[key].intents_count += 1
        return {
            "intentId": intent.intent_id, "intentName": intent.intent_name,
            "description": intent.description,
            "parentIntentSignature": intent.parent_intent_signature,
            "sampleUtterances": intent.sample_utterances,
            "dialogCodeHook": intent.dialog_code_hook,
            "fulfillmentCodeHook": intent.fulfillment_code_hook,
            "intentConfirmationSetting": intent.intent_confirmation_setting,
            "intentClosingSetting": intent.intent_closing_setting,
            "inputContexts": intent.input_contexts,
            "outputContexts": intent.output_contexts,
            "kendraConfiguration": intent.kendra_configuration,
            "botId": bot_id, "botVersion": bot_version, "localeId": locale_id,
            "creationDateTime": intent.creation_date_time,
            "initialResponseSetting": intent.initial_response_setting,
            "qnAIntentConfiguration": intent.qn_a_intent_configuration,
        }

    def describe_intent(self, intent_id: str, bot_id: str, bot_version: str, locale_id: str) -> dict[str, Any]:
        if intent_id not in self.intents:
            raise ResourceNotFoundException(f"Could not find intent: {intent_id}")
        intent = self.intents[intent_id]
        return {
            "intentId": intent.intent_id, "intentName": intent.intent_name,
            "description": intent.description,
            "parentIntentSignature": intent.parent_intent_signature,
            "sampleUtterances": intent.sample_utterances,
            "dialogCodeHook": intent.dialog_code_hook,
            "fulfillmentCodeHook": intent.fulfillment_code_hook,
            "intentConfirmationSetting": intent.intent_confirmation_setting,
            "intentClosingSetting": intent.intent_closing_setting,
            "inputContexts": intent.input_contexts,
            "outputContexts": intent.output_contexts,
            "kendraConfiguration": intent.kendra_configuration,
            "botId": intent.bot_id, "botVersion": intent.bot_version,
            "localeId": intent.locale_id, "creationDateTime": intent.creation_date_time,
            "lastUpdatedDateTime": intent.last_updated_date_time,
            "initialResponseSetting": intent.initial_response_setting,
            "qnAIntentConfiguration": intent.qn_a_intent_configuration,
        }

    def update_intent(
        self, intent_id: str, bot_id: str, bot_version: str, locale_id: str,
        intent_name: str, description: str, parent_intent_signature: Optional[str],
        sample_utterances: Optional[list[dict[str, Any]]],
        dialog_code_hook: Optional[dict[str, Any]],
        fulfillment_code_hook: Optional[dict[str, Any]],
        intent_confirmation_setting: Optional[dict[str, Any]],
        intent_closing_setting: Optional[dict[str, Any]],
        input_contexts: Optional[list[dict[str, Any]]],
        output_contexts: Optional[list[dict[str, Any]]],
        kendra_configuration: Optional[dict[str, Any]],
        initial_response_setting: Optional[dict[str, Any]],
        qn_a_intent_configuration: Optional[dict[str, Any]],
    ) -> dict[str, Any]:
        if intent_id not in self.intents:
            raise ResourceNotFoundException(f"Could not find intent: {intent_id}")
        intent = self.intents[intent_id]
        intent.intent_name = intent_name
        intent.description = description
        intent.parent_intent_signature = parent_intent_signature
        intent.sample_utterances = sample_utterances or []
        intent.dialog_code_hook = dialog_code_hook
        intent.fulfillment_code_hook = fulfillment_code_hook
        intent.intent_confirmation_setting = intent_confirmation_setting
        intent.intent_closing_setting = intent_closing_setting
        intent.input_contexts = input_contexts or []
        intent.output_contexts = output_contexts or []
        intent.kendra_configuration = kendra_configuration
        intent.initial_response_setting = initial_response_setting
        intent.qn_a_intent_configuration = qn_a_intent_configuration
        intent.last_updated_date_time = datetime.now().isoformat()
        return {
            "intentId": intent.intent_id, "intentName": intent.intent_name,
            "description": intent.description,
            "parentIntentSignature": intent.parent_intent_signature,
            "sampleUtterances": intent.sample_utterances,
            "dialogCodeHook": intent.dialog_code_hook,
            "fulfillmentCodeHook": intent.fulfillment_code_hook,
            "intentConfirmationSetting": intent.intent_confirmation_setting,
            "intentClosingSetting": intent.intent_closing_setting,
            "inputContexts": intent.input_contexts,
            "outputContexts": intent.output_contexts,
            "kendraConfiguration": intent.kendra_configuration,
            "botId": intent.bot_id, "botVersion": intent.bot_version,
            "localeId": intent.locale_id, "creationDateTime": intent.creation_date_time,
            "lastUpdatedDateTime": intent.last_updated_date_time,
            "initialResponseSetting": intent.initial_response_setting,
            "qnAIntentConfiguration": intent.qn_a_intent_configuration,
        }

    def delete_intent(self, intent_id: str, bot_id: str, bot_version: str, locale_id: str) -> None:
        if intent_id not in self.intents:
            raise ResourceNotFoundException(f"Could not find intent: {intent_id}")
        intent = self.intents.pop(intent_id)
        key = (intent.bot_id, intent.bot_version, intent.locale_id)
        if key in self.bot_locales:
            self.bot_locales[key].intents_count = max(0, self.bot_locales[key].intents_count - 1)

    def list_intents(self, bot_id: str, bot_version: str, locale_id: str) -> list[dict[str, Any]]:
        return [
            {
                "intentId": intent.intent_id, "intentName": intent.intent_name,
                "description": intent.description,
                "parentIntentSignature": intent.parent_intent_signature,
                "lastUpdatedDateTime": intent.last_updated_date_time,
            }
            for intent in self.intents.values()
            if intent.bot_id == bot_id and intent.bot_version == bot_version and intent.locale_id == locale_id
        ]

    def create_slot(
        self, bot_id: str, bot_version: str, locale_id: str, intent_id: str,
        slot_name: str, description: str, slot_type_id: Optional[str],
        value_elicitation_setting: Optional[dict[str, Any]],
        obfuscation_setting: Optional[dict[str, Any]],
        multiple_values_setting: Optional[dict[str, Any]],
        sub_slot_setting: Optional[dict[str, Any]],
    ) -> dict[str, Any]:
        slot = FakeSlot(
            bot_id=bot_id, bot_version=bot_version, locale_id=locale_id, intent_id=intent_id,
            slot_name=slot_name, description=description, slot_type_id=slot_type_id,
            value_elicitation_setting=value_elicitation_setting,
            obfuscation_setting=obfuscation_setting,
            multiple_values_setting=multiple_values_setting,
            sub_slot_setting=sub_slot_setting,
        )
        self.slots[slot.slot_id] = slot
        return {
            "slotId": slot.slot_id, "slotName": slot.slot_name, "description": slot.description,
            "slotTypeId": slot.slot_type_id,
            "valueElicitationSetting": slot.value_elicitation_setting,
            "obfuscationSetting": slot.obfuscation_setting,
            "botId": bot_id, "botVersion": bot_version, "localeId": locale_id, "intentId": intent_id,
            "creationDateTime": slot.creation_date_time,
            "multipleValuesSetting": slot.multiple_values_setting,
            "subSlotSetting": slot.sub_slot_setting,
        }

    def describe_slot(self, slot_id: str, bot_id: str, bot_version: str, locale_id: str, intent_id: str) -> dict[str, Any]:
        if slot_id not in self.slots:
            raise ResourceNotFoundException(f"Could not find slot: {slot_id}")
        slot = self.slots[slot_id]
        return {
            "slotId": slot.slot_id, "slotName": slot.slot_name, "description": slot.description,
            "slotTypeId": slot.slot_type_id,
            "valueElicitationSetting": slot.value_elicitation_setting,
            "obfuscationSetting": slot.obfuscation_setting,
            "botId": slot.bot_id, "botVersion": slot.bot_version,
            "localeId": slot.locale_id, "intentId": slot.intent_id,
            "creationDateTime": slot.creation_date_time,
            "lastUpdatedDateTime": slot.last_updated_date_time,
            "multipleValuesSetting": slot.multiple_values_setting,
            "subSlotSetting": slot.sub_slot_setting,
        }

    def update_slot(
        self, slot_id: str, bot_id: str, bot_version: str, locale_id: str, intent_id: str,
        slot_name: str, description: str, slot_type_id: Optional[str],
        value_elicitation_setting: Optional[dict[str, Any]],
        obfuscation_setting: Optional[dict[str, Any]],
        multiple_values_setting: Optional[dict[str, Any]],
        sub_slot_setting: Optional[dict[str, Any]],
    ) -> dict[str, Any]:
        if slot_id not in self.slots:
            raise ResourceNotFoundException(f"Could not find slot: {slot_id}")
        slot = self.slots[slot_id]
        slot.slot_name = slot_name
        slot.description = description
        slot.slot_type_id = slot_type_id
        slot.value_elicitation_setting = value_elicitation_setting
        slot.obfuscation_setting = obfuscation_setting
        slot.multiple_values_setting = multiple_values_setting
        slot.sub_slot_setting = sub_slot_setting
        slot.last_updated_date_time = datetime.now().isoformat()
        return {
            "slotId": slot.slot_id, "slotName": slot.slot_name, "description": slot.description,
            "slotTypeId": slot.slot_type_id,
            "valueElicitationSetting": slot.value_elicitation_setting,
            "obfuscationSetting": slot.obfuscation_setting,
            "botId": slot.bot_id, "botVersion": slot.bot_version,
            "localeId": slot.locale_id, "intentId": slot.intent_id,
            "creationDateTime": slot.creation_date_time,
            "lastUpdatedDateTime": slot.last_updated_date_time,
            "multipleValuesSetting": slot.multiple_values_setting,
            "subSlotSetting": slot.sub_slot_setting,
        }

    def delete_slot(self, slot_id: str, bot_id: str, bot_version: str, locale_id: str, intent_id: str) -> None:
        if slot_id not in self.slots:
            raise ResourceNotFoundException(f"Could not find slot: {slot_id}")
        self.slots.pop(slot_id)

    def list_slots(self, bot_id: str, bot_version: str, locale_id: str, intent_id: str) -> list[dict[str, Any]]:
        return [
            {
                "slotId": slot.slot_id, "slotName": slot.slot_name, "description": slot.description,
                "slotTypeId": slot.slot_type_id,
                "valueElicitationSetting": slot.value_elicitation_setting,
                "lastUpdatedDateTime": slot.last_updated_date_time,
            }
            for slot in self.slots.values()
            if slot.bot_id == bot_id and slot.bot_version == bot_version
            and slot.locale_id == locale_id and slot.intent_id == intent_id
        ]

    def create_slot_type(
        self, bot_id: str, bot_version: str, locale_id: str,
        slot_type_name: str, description: str,
        slot_type_values: Optional[list[dict[str, Any]]],
        value_selection_setting: Optional[dict[str, Any]],
        parent_slot_type_signature: Optional[str],
        external_source_setting: Optional[dict[str, Any]],
        composite_slot_type_setting: Optional[dict[str, Any]],
    ) -> dict[str, Any]:
        slot_type = FakeSlotType(
            bot_id=bot_id, bot_version=bot_version, locale_id=locale_id,
            slot_type_name=slot_type_name, description=description,
            slot_type_values=slot_type_values,
            value_selection_setting=value_selection_setting,
            parent_slot_type_signature=parent_slot_type_signature,
            external_source_setting=external_source_setting,
            composite_slot_type_setting=composite_slot_type_setting,
        )
        self.slot_types[slot_type.slot_type_id] = slot_type
        key = (bot_id, bot_version, locale_id)
        if key in self.bot_locales:
            self.bot_locales[key].slot_types_count += 1
        return {
            "slotTypeId": slot_type.slot_type_id, "slotTypeName": slot_type.slot_type_name,
            "description": slot_type.description, "slotTypeValues": slot_type.slot_type_values,
            "valueSelectionSetting": slot_type.value_selection_setting,
            "parentSlotTypeSignature": slot_type.parent_slot_type_signature,
            "botId": bot_id, "botVersion": bot_version, "localeId": locale_id,
            "creationDateTime": slot_type.creation_date_time,
            "externalSourceSetting": slot_type.external_source_setting,
            "compositeSlotTypeSetting": slot_type.composite_slot_type_setting,
        }

    def describe_slot_type(self, slot_type_id: str, bot_id: str, bot_version: str, locale_id: str) -> dict[str, Any]:
        if slot_type_id not in self.slot_types:
            raise ResourceNotFoundException(f"Could not find slot type: {slot_type_id}")
        st = self.slot_types[slot_type_id]
        return {
            "slotTypeId": st.slot_type_id, "slotTypeName": st.slot_type_name,
            "description": st.description, "slotTypeValues": st.slot_type_values,
            "valueSelectionSetting": st.value_selection_setting,
            "parentSlotTypeSignature": st.parent_slot_type_signature,
            "botId": st.bot_id, "botVersion": st.bot_version, "localeId": st.locale_id,
            "creationDateTime": st.creation_date_time,
            "lastUpdatedDateTime": st.last_updated_date_time,
            "externalSourceSetting": st.external_source_setting,
            "compositeSlotTypeSetting": st.composite_slot_type_setting,
        }

    def update_slot_type(
        self, slot_type_id: str, bot_id: str, bot_version: str, locale_id: str,
        slot_type_name: str, description: str,
        slot_type_values: Optional[list[dict[str, Any]]],
        value_selection_setting: Optional[dict[str, Any]],
        parent_slot_type_signature: Optional[str],
        external_source_setting: Optional[dict[str, Any]],
        composite_slot_type_setting: Optional[dict[str, Any]],
    ) -> dict[str, Any]:
        if slot_type_id not in self.slot_types:
            raise ResourceNotFoundException(f"Could not find slot type: {slot_type_id}")
        st = self.slot_types[slot_type_id]
        st.slot_type_name = slot_type_name
        st.description = description
        st.slot_type_values = slot_type_values or []
        st.value_selection_setting = value_selection_setting
        st.parent_slot_type_signature = parent_slot_type_signature
        st.external_source_setting = external_source_setting
        st.composite_slot_type_setting = composite_slot_type_setting
        st.last_updated_date_time = datetime.now().isoformat()
        return {
            "slotTypeId": st.slot_type_id, "slotTypeName": st.slot_type_name,
            "description": st.description, "slotTypeValues": st.slot_type_values,
            "valueSelectionSetting": st.value_selection_setting,
            "parentSlotTypeSignature": st.parent_slot_type_signature,
            "botId": st.bot_id, "botVersion": st.bot_version, "localeId": st.locale_id,
            "creationDateTime": st.creation_date_time,
            "lastUpdatedDateTime": st.last_updated_date_time,
            "externalSourceSetting": st.external_source_setting,
            "compositeSlotTypeSetting": st.composite_slot_type_setting,
        }

    def delete_slot_type(self, slot_type_id: str, bot_id: str, bot_version: str, locale_id: str, skip_resource_in_use_check: bool) -> None:
        if slot_type_id not in self.slot_types:
            raise ResourceNotFoundException(f"Could not find slot type: {slot_type_id}")
        st = self.slot_types.pop(slot_type_id)
        key = (st.bot_id, st.bot_version, st.locale_id)
        if key in self.bot_locales:
            self.bot_locales[key].slot_types_count = max(0, self.bot_locales[key].slot_types_count - 1)

    def list_slot_types(self, bot_id: str, bot_version: str, locale_id: str) -> list[dict[str, Any]]:
        return [
            {
                "slotTypeId": st.slot_type_id, "slotTypeName": st.slot_type_name,
                "description": st.description,
                "parentSlotTypeSignature": st.parent_slot_type_signature,
                "lastUpdatedDateTime": st.last_updated_date_time,
                "slotTypeCategory": "Custom",
            }
            for st in self.slot_types.values()
            if st.bot_id == bot_id and st.bot_version == bot_version and st.locale_id == locale_id
        ]

    def create_resource_policy(self, resource_arn: str, policy: str) -> tuple[str, str]:
        rp = FakeResourcePolicy(resource_arn, policy)
        self.resource_policies[rp.resource_arn] = rp
        return rp.resource_arn, rp.revision_id

    def describe_resource_policy(self, resource_arn: str) -> tuple[str, str, str]:
        if resource_arn not in self.resource_policies:
            raise ResourceNotFoundException(f"Could not find resource policy for: {resource_arn}")
        rp = self.resource_policies[resource_arn]
        return rp.resource_arn, rp.policy, rp.revision_id

    def update_resource_policy(self, resource_arn: str, policy: str, expected_revision_id: str) -> tuple[str, str]:
        if resource_arn not in self.resource_policies:
            raise ResourceNotFoundException(f"Could not find resource policy for: {resource_arn}")
        rp = self.resource_policies[resource_arn]
        if expected_revision_id != rp.revision_id:
            raise Exception("Revision ID mismatch")
        rp.policy = policy
        rp.revision_id = str(uuid.uuid4())
        return rp.resource_arn, rp.revision_id

    def delete_resource_policy(self, resource_arn: str, expected_revision_id: str) -> tuple[str, str]:
        if resource_arn not in self.resource_policies:
            raise ResourceNotFoundException(f"Could not find resource policy for: {resource_arn}")
        rp = self.resource_policies[resource_arn]
        if expected_revision_id != rp.revision_id:
            raise Exception("Revision ID mismatch")
        rp = self.resource_policies.pop(resource_arn)
        return rp.resource_arn, rp.revision_id

    def tag_resource(self, resource_arn: str, tags: dict[str, str]) -> None:
        tags_list = [{"Key": k, "Value": v} for k, v in tags.items()]
        self.tagger.tag_resource(resource_arn, tags_list)

    def untag_resource(self, resource_arn: str, tag_keys: list[str]) -> None:
        self.tagger.untag_resource_using_names(resource_arn, tag_keys)

    def list_tags_for_resource(self, resource_arn: str) -> dict[str, str]:
        return self.tagger.get_tag_dict_for_resource(resource_arn)


lexv2models_backends = BackendDict(LexModelsV2Backend, "lexv2-models")
