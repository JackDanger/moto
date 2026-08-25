"""Handles incoming lexv2models requests, invokes methods, returns responses."""

import json
from urllib.parse import unquote

from moto.core.responses import BaseResponse

from .models import LexModelsV2Backend, lexv2models_backends


class LexModelsV2Response(BaseResponse):
    """Handler for LexModelsV2 requests and responses."""

    def __init__(self) -> None:
        super().__init__(service_name="lexv2-models")

    @property
    def lexv2models_backend(self) -> LexModelsV2Backend:
        """Return backend instance specific for this region."""
        return lexv2models_backends[self.current_account][self.region]

    def create_bot(self) -> str:
        resp = self.lexv2models_backend.create_bot(
            bot_name=self._get_param("botName"),
            description=self._get_param("description"),
            role_arn=self._get_param("roleArn"),
            data_privacy=self._get_param("dataPrivacy"),
            idle_session_ttl_in_seconds=self._get_param("idleSessionTTLInSeconds"),
            bot_tags=self._get_param("botTags"),
            test_bot_alias_tags=self._get_param("testBotAliasTags"),
            bot_type=self._get_param("botType"),
            bot_members=self._get_param("botMembers"),
        )
        return json.dumps(resp)

    def describe_bot(self) -> str:
        bot_id = self._get_param("botId")
        return json.dumps(self.lexv2models_backend.describe_bot(bot_id=bot_id))

    def update_bot(self) -> str:
        bot_id = self._get_param("botId")
        return json.dumps(self.lexv2models_backend.update_bot(
            bot_id=bot_id,
            bot_name=self._get_param("botName"),
            description=self._get_param("description"),
            role_arn=self._get_param("roleArn"),
            data_privacy=self._get_param("dataPrivacy"),
            idle_session_ttl_in_seconds=self._get_param("idleSessionTTLInSeconds"),
            bot_type=self._get_param("botType"),
            bot_members=self._get_param("botMembers"),
        ))

    def list_bots(self) -> str:
        bot_summaries = self.lexv2models_backend.list_bots()
        return json.dumps({"botSummaries": bot_summaries, "nextToken": None})

    def delete_bot(self) -> str:
        bot_id = self._get_param("botId")
        bot_id, bot_status = self.lexv2models_backend.delete_bot(
            bot_id=bot_id,
            skip_resource_in_use_check=self._get_param("skipResourceInUseCheck"),
        )
        return json.dumps({"botId": bot_id, "botStatus": bot_status})

    def create_bot_alias(self) -> str:
        return json.dumps(self.lexv2models_backend.create_bot_alias(
            bot_alias_name=self._get_param("botAliasName"),
            description=self._get_param("description"),
            bot_version=self._get_param("botVersion"),
            bot_alias_locale_settings=self._get_param("botAliasLocaleSettings"),
            conversation_log_settings=self._get_param("conversationLogSettings"),
            sentiment_analysis_settings=self._get_param("sentimentAnalysisSettings"),
            bot_id=self._get_param("botId"),
            tags=self._get_param("tags"),
        ))

    def describe_bot_alias(self) -> str:
        return json.dumps(self.lexv2models_backend.describe_bot_alias(
            bot_alias_id=self._get_param("botAliasId"),
            bot_id=self._get_param("botId"),
        ))

    def update_bot_alias(self) -> str:
        return json.dumps(self.lexv2models_backend.update_bot_alias(
            bot_alias_id=self._get_param("botAliasId"),
            bot_alias_name=self._get_param("botAliasName"),
            description=self._get_param("description"),
            bot_version=self._get_param("botVersion"),
            bot_alias_locale_settings=self._get_param("botAliasLocaleSettings"),
            conversation_log_settings=self._get_param("conversationLogSettings"),
            sentiment_analysis_settings=self._get_param("sentimentAnalysisSettings"),
            bot_id=self._get_param("botId"),
        ))

    def list_bot_aliases(self) -> str:
        bot_id = self._get_param("botId")
        summaries, bot_id = self.lexv2models_backend.list_bot_aliases(
            bot_id=bot_id, max_results=self._get_param("maxResults"),
        )
        return json.dumps({"botAliasSummaries": summaries, "nextToken": None, "botId": bot_id})

    def delete_bot_alias(self) -> str:
        bot_alias_id, bot_id, status = self.lexv2models_backend.delete_bot_alias(
            bot_alias_id=self._get_param("botAliasId"),
            bot_id=self._get_param("botId"),
            skip_resource_in_use_check=self._get_param("skipResourceInUseCheck"),
        )
        return json.dumps({"botAliasId": bot_alias_id, "botId": bot_id, "botAliasStatus": status})

    def create_bot_locale(self) -> str:
        return json.dumps(self.lexv2models_backend.create_bot_locale(
            bot_id=self._get_param("botId"),
            bot_version=self._get_param("botVersion"),
            locale_id=self._get_param("localeId"),
            description=self._get_param("description") or "",
            nlu_intent_confidence_threshold=self._get_param("nluIntentConfidenceThreshold"),
            voice_settings=self._get_param("voiceSettings"),
        ))

    def describe_bot_locale(self) -> str:
        return json.dumps(self.lexv2models_backend.describe_bot_locale(
            bot_id=self._get_param("botId"),
            bot_version=self._get_param("botVersion"),
            locale_id=self._get_param("localeId"),
        ))

    def update_bot_locale(self) -> str:
        return json.dumps(self.lexv2models_backend.update_bot_locale(
            bot_id=self._get_param("botId"),
            bot_version=self._get_param("botVersion"),
            locale_id=self._get_param("localeId"),
            description=self._get_param("description") or "",
            nlu_intent_confidence_threshold=self._get_param("nluIntentConfidenceThreshold"),
            voice_settings=self._get_param("voiceSettings"),
        ))

    def delete_bot_locale(self) -> str:
        return json.dumps(self.lexv2models_backend.delete_bot_locale(
            bot_id=self._get_param("botId"),
            bot_version=self._get_param("botVersion"),
            locale_id=self._get_param("localeId"),
        ))

    def list_bot_locales(self) -> str:
        bot_id = self._get_param("botId")
        bot_version = self._get_param("botVersion")
        summaries = self.lexv2models_backend.list_bot_locales(bot_id=bot_id, bot_version=bot_version)
        return json.dumps({
            "botId": bot_id, "botVersion": bot_version,
            "nextToken": None, "botLocaleSummaries": summaries,
        })

    def build_bot_locale(self) -> str:
        return json.dumps(self.lexv2models_backend.build_bot_locale(
            bot_id=self._get_param("botId"),
            bot_version=self._get_param("botVersion"),
            locale_id=self._get_param("localeId"),
        ))

    def create_bot_version(self) -> str:
        return json.dumps(self.lexv2models_backend.create_bot_version(
            bot_id=self._get_param("botId"),
            description=self._get_param("description") or "",
            bot_version_locale_specification=self._get_param("botVersionLocaleSpecification") or {},
        ))

    def describe_bot_version(self) -> str:
        return json.dumps(self.lexv2models_backend.describe_bot_version(
            bot_id=self._get_param("botId"),
            bot_version=self._get_param("botVersion"),
        ))

    def list_bot_versions(self) -> str:
        bot_id = self._get_param("botId")
        summaries = self.lexv2models_backend.list_bot_versions(bot_id=bot_id)
        return json.dumps({"botId": bot_id, "botVersionSummaries": summaries, "nextToken": None})

    def delete_bot_version(self) -> str:
        bot_id, bot_version, status = self.lexv2models_backend.delete_bot_version(
            bot_id=self._get_param("botId"),
            bot_version=self._get_param("botVersion"),
            skip_resource_in_use_check=self._get_param("skipResourceInUseCheck"),
        )
        return json.dumps({"botId": bot_id, "botVersion": bot_version, "botStatus": status})

    def create_intent(self) -> str:
        return json.dumps(self.lexv2models_backend.create_intent(
            bot_id=self._get_param("botId"),
            bot_version=self._get_param("botVersion"),
            locale_id=self._get_param("localeId"),
            intent_name=self._get_param("intentName"),
            description=self._get_param("description") or "",
            parent_intent_signature=self._get_param("parentIntentSignature"),
            sample_utterances=self._get_param("sampleUtterances"),
            dialog_code_hook=self._get_param("dialogCodeHook"),
            fulfillment_code_hook=self._get_param("fulfillmentCodeHook"),
            intent_confirmation_setting=self._get_param("intentConfirmationSetting"),
            intent_closing_setting=self._get_param("intentClosingSetting"),
            input_contexts=self._get_param("inputContexts"),
            output_contexts=self._get_param("outputContexts"),
            kendra_configuration=self._get_param("kendraConfiguration"),
            initial_response_setting=self._get_param("initialResponseSetting"),
            qn_a_intent_configuration=self._get_param("qnAIntentConfiguration"),
        ))

    def describe_intent(self) -> str:
        return json.dumps(self.lexv2models_backend.describe_intent(
            intent_id=self._get_param("intentId"),
            bot_id=self._get_param("botId"),
            bot_version=self._get_param("botVersion"),
            locale_id=self._get_param("localeId"),
        ))

    def update_intent(self) -> str:
        return json.dumps(self.lexv2models_backend.update_intent(
            intent_id=self._get_param("intentId"),
            bot_id=self._get_param("botId"),
            bot_version=self._get_param("botVersion"),
            locale_id=self._get_param("localeId"),
            intent_name=self._get_param("intentName"),
            description=self._get_param("description") or "",
            parent_intent_signature=self._get_param("parentIntentSignature"),
            sample_utterances=self._get_param("sampleUtterances"),
            dialog_code_hook=self._get_param("dialogCodeHook"),
            fulfillment_code_hook=self._get_param("fulfillmentCodeHook"),
            intent_confirmation_setting=self._get_param("intentConfirmationSetting"),
            intent_closing_setting=self._get_param("intentClosingSetting"),
            input_contexts=self._get_param("inputContexts"),
            output_contexts=self._get_param("outputContexts"),
            kendra_configuration=self._get_param("kendraConfiguration"),
            initial_response_setting=self._get_param("initialResponseSetting"),
            qn_a_intent_configuration=self._get_param("qnAIntentConfiguration"),
        ))

    def delete_intent(self) -> str:
        self.lexv2models_backend.delete_intent(
            intent_id=self._get_param("intentId"),
            bot_id=self._get_param("botId"),
            bot_version=self._get_param("botVersion"),
            locale_id=self._get_param("localeId"),
        )
        return json.dumps({})

    def list_intents(self) -> str:
        bot_id = self._get_param("botId")
        bot_version = self._get_param("botVersion")
        locale_id = self._get_param("localeId")
        summaries = self.lexv2models_backend.list_intents(
            bot_id=bot_id, bot_version=bot_version, locale_id=locale_id,
        )
        return json.dumps({
            "botId": bot_id, "botVersion": bot_version, "localeId": locale_id,
            "intentSummaries": summaries, "nextToken": None,
        })

    def create_slot(self) -> str:
        return json.dumps(self.lexv2models_backend.create_slot(
            bot_id=self._get_param("botId"),
            bot_version=self._get_param("botVersion"),
            locale_id=self._get_param("localeId"),
            intent_id=self._get_param("intentId"),
            slot_name=self._get_param("slotName"),
            description=self._get_param("description") or "",
            slot_type_id=self._get_param("slotTypeId"),
            value_elicitation_setting=self._get_param("valueElicitationSetting"),
            obfuscation_setting=self._get_param("obfuscationSetting"),
            multiple_values_setting=self._get_param("multipleValuesSetting"),
            sub_slot_setting=self._get_param("subSlotSetting"),
        ))

    def describe_slot(self) -> str:
        return json.dumps(self.lexv2models_backend.describe_slot(
            slot_id=self._get_param("slotId"),
            bot_id=self._get_param("botId"),
            bot_version=self._get_param("botVersion"),
            locale_id=self._get_param("localeId"),
            intent_id=self._get_param("intentId"),
        ))

    def update_slot(self) -> str:
        return json.dumps(self.lexv2models_backend.update_slot(
            slot_id=self._get_param("slotId"),
            bot_id=self._get_param("botId"),
            bot_version=self._get_param("botVersion"),
            locale_id=self._get_param("localeId"),
            intent_id=self._get_param("intentId"),
            slot_name=self._get_param("slotName"),
            description=self._get_param("description") or "",
            slot_type_id=self._get_param("slotTypeId"),
            value_elicitation_setting=self._get_param("valueElicitationSetting"),
            obfuscation_setting=self._get_param("obfuscationSetting"),
            multiple_values_setting=self._get_param("multipleValuesSetting"),
            sub_slot_setting=self._get_param("subSlotSetting"),
        ))

    def delete_slot(self) -> str:
        self.lexv2models_backend.delete_slot(
            slot_id=self._get_param("slotId"),
            bot_id=self._get_param("botId"),
            bot_version=self._get_param("botVersion"),
            locale_id=self._get_param("localeId"),
            intent_id=self._get_param("intentId"),
        )
        return json.dumps({})

    def list_slots(self) -> str:
        bot_id = self._get_param("botId")
        bot_version = self._get_param("botVersion")
        locale_id = self._get_param("localeId")
        intent_id = self._get_param("intentId")
        summaries = self.lexv2models_backend.list_slots(
            bot_id=bot_id, bot_version=bot_version,
            locale_id=locale_id, intent_id=intent_id,
        )
        return json.dumps({
            "botId": bot_id, "botVersion": bot_version,
            "localeId": locale_id, "intentId": intent_id,
            "slotSummaries": summaries, "nextToken": None,
        })

    def create_slot_type(self) -> str:
        return json.dumps(self.lexv2models_backend.create_slot_type(
            bot_id=self._get_param("botId"),
            bot_version=self._get_param("botVersion"),
            locale_id=self._get_param("localeId"),
            slot_type_name=self._get_param("slotTypeName"),
            description=self._get_param("description") or "",
            slot_type_values=self._get_param("slotTypeValues"),
            value_selection_setting=self._get_param("valueSelectionSetting"),
            parent_slot_type_signature=self._get_param("parentSlotTypeSignature"),
            external_source_setting=self._get_param("externalSourceSetting"),
            composite_slot_type_setting=self._get_param("compositeSlotTypeSetting"),
        ))

    def describe_slot_type(self) -> str:
        return json.dumps(self.lexv2models_backend.describe_slot_type(
            slot_type_id=self._get_param("slotTypeId"),
            bot_id=self._get_param("botId"),
            bot_version=self._get_param("botVersion"),
            locale_id=self._get_param("localeId"),
        ))

    def update_slot_type(self) -> str:
        return json.dumps(self.lexv2models_backend.update_slot_type(
            slot_type_id=self._get_param("slotTypeId"),
            bot_id=self._get_param("botId"),
            bot_version=self._get_param("botVersion"),
            locale_id=self._get_param("localeId"),
            slot_type_name=self._get_param("slotTypeName"),
            description=self._get_param("description") or "",
            slot_type_values=self._get_param("slotTypeValues"),
            value_selection_setting=self._get_param("valueSelectionSetting"),
            parent_slot_type_signature=self._get_param("parentSlotTypeSignature"),
            external_source_setting=self._get_param("externalSourceSetting"),
            composite_slot_type_setting=self._get_param("compositeSlotTypeSetting"),
        ))

    def delete_slot_type(self) -> str:
        self.lexv2models_backend.delete_slot_type(
            slot_type_id=self._get_param("slotTypeId"),
            bot_id=self._get_param("botId"),
            bot_version=self._get_param("botVersion"),
            locale_id=self._get_param("localeId"),
            skip_resource_in_use_check=self._get_param("skipResourceInUseCheck"),
        )
        return json.dumps({})

    def list_slot_types(self) -> str:
        bot_id = self._get_param("botId")
        bot_version = self._get_param("botVersion")
        locale_id = self._get_param("localeId")
        summaries = self.lexv2models_backend.list_slot_types(
            bot_id=bot_id, bot_version=bot_version, locale_id=locale_id,
        )
        return json.dumps({
            "botId": bot_id, "botVersion": bot_version, "localeId": locale_id,
            "slotTypeSummaries": summaries, "nextToken": None,
        })

    def create_resource_policy(self) -> str:
        resource_arn = unquote(self._get_param("resourceArn"))
        policy = self._get_param("policy")
        resource_arn, revision_id = self.lexv2models_backend.create_resource_policy(
            resource_arn=resource_arn, policy=policy,
        )
        return json.dumps({"resourceArn": resource_arn, "revisionId": revision_id})

    def describe_resource_policy(self) -> str:
        resource_arn = unquote(self._get_param("resourceArn"))
        resource_arn, policy, revision_id = self.lexv2models_backend.describe_resource_policy(
            resource_arn=resource_arn,
        )
        return json.dumps({"resourceArn": resource_arn, "policy": policy, "revisionId": revision_id})

    def update_resource_policy(self) -> str:
        resource_arn = unquote(self._get_param("resourceArn"))
        resource_arn, revision_id = self.lexv2models_backend.update_resource_policy(
            resource_arn=resource_arn,
            policy=self._get_param("policy"),
            expected_revision_id=self._get_param("expectedRevisionId"),
        )
        return json.dumps({"resourceArn": resource_arn, "revisionId": revision_id})

    def delete_resource_policy(self) -> str:
        resource_arn = unquote(self._get_param("resourceArn"))
        resource_arn, revision_id = self.lexv2models_backend.delete_resource_policy(
            resource_arn=resource_arn,
            expected_revision_id=self._get_param("expectedRevisionId"),
        )
        return json.dumps({"resourceArn": resource_arn, "revisionId": revision_id})

    def tag_resource(self) -> str:
        resource_arn = unquote(self.parsed_url.path.split("/tags/")[-1])
        self.lexv2models_backend.tag_resource(
            resource_arn=resource_arn, tags=self._get_param("tags"),
        )
        return json.dumps({})

    def untag_resource(self) -> str:
        resource_arn = unquote(self.parsed_url.path.split("/tags/")[-1])
        tag_keys = self.__dict__["data"]["tagKeys"]
        self.lexv2models_backend.untag_resource(resource_arn=resource_arn, tag_keys=tag_keys)
        return json.dumps({})

    def list_tags_for_resource(self) -> str:
        resource_arn = unquote(self.parsed_url.path.split("/tags/")[-1])
        tags = self.lexv2models_backend.list_tags_for_resource(resource_arn=resource_arn)
        return json.dumps({"tags": tags})
