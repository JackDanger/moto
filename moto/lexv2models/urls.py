"""lexv2models base URL and path."""

from .responses import LexModelsV2Response

url_bases = [
    r"https?://lex\.(.+)\.amazonaws\.com",
    r"https?://models-v2-lex\.(.+)\.amazonaws\.com",
]

url_paths = {
    "{0}/bots/$": LexModelsV2Response.dispatch,
    "{0}/bots/(?P<botId>[^/]+)/$": LexModelsV2Response.dispatch,
    # Bot aliases
    "{0}/bots/(?P<botId>[^/]+)/botaliases/$": LexModelsV2Response.dispatch,
    "{0}/bots/(?P<botId>[^/]+)/botaliases/(?P<botAliasId>[^/]+)/$": LexModelsV2Response.dispatch,
    # Bot versions
    "{0}/bots/(?P<botId>[^/]+)/botversions/$": LexModelsV2Response.dispatch,
    "{0}/bots/(?P<botId>[^/]+)/botversions/(?P<botVersion>[^/]+)/$": LexModelsV2Response.dispatch,
    # Bot locales
    "{0}/bots/(?P<botId>[^/]+)/botversions/(?P<botVersion>[^/]+)/botlocales/$": LexModelsV2Response.dispatch,
    "{0}/bots/(?P<botId>[^/]+)/botversions/(?P<botVersion>[^/]+)/botlocales/(?P<localeId>[^/]+)/$": LexModelsV2Response.dispatch,
    # Build bot locale
    "{0}/bots/(?P<botId>[^/]+)/botversions/(?P<botVersion>[^/]+)/botlocales/(?P<localeId>[^/]+)/build$": LexModelsV2Response.dispatch,
    # Intents
    "{0}/bots/(?P<botId>[^/]+)/botversions/(?P<botVersion>[^/]+)/botlocales/(?P<localeId>[^/]+)/intents/$": LexModelsV2Response.dispatch,
    "{0}/bots/(?P<botId>[^/]+)/botversions/(?P<botVersion>[^/]+)/botlocales/(?P<localeId>[^/]+)/intents/(?P<intentId>[^/]+)/$": LexModelsV2Response.dispatch,
    # Slots
    "{0}/bots/(?P<botId>[^/]+)/botversions/(?P<botVersion>[^/]+)/botlocales/(?P<localeId>[^/]+)/intents/(?P<intentId>[^/]+)/slots/$": LexModelsV2Response.dispatch,
    "{0}/bots/(?P<botId>[^/]+)/botversions/(?P<botVersion>[^/]+)/botlocales/(?P<localeId>[^/]+)/intents/(?P<intentId>[^/]+)/slots/(?P<slotId>[^/]+)/$": LexModelsV2Response.dispatch,
    # Slot types
    "{0}/bots/(?P<botId>[^/]+)/botversions/(?P<botVersion>[^/]+)/botlocales/(?P<localeId>[^/]+)/slottypes/$": LexModelsV2Response.dispatch,
    "{0}/bots/(?P<botId>[^/]+)/botversions/(?P<botVersion>[^/]+)/botlocales/(?P<localeId>[^/]+)/slottypes/(?P<slotTypeId>[^/]+)/$": LexModelsV2Response.dispatch,
    # Resource policies
    "{0}/policy/(?P<resourceArn>.+)/$": LexModelsV2Response.dispatch,
    # Tags
    "{0}/tags/(?P<resourceARN>[^/]+)$": LexModelsV2Response.dispatch,
    "{0}/tags/(?P<arn_prefix>[^/]+)/(?P<bot_id>[^/]+)$": LexModelsV2Response.dispatch,
}
