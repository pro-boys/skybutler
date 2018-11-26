from SkyButler.modules.sql.translation import prev_locale
from SkyButler.modules.translations.Arabic import ArabicStrings

def sbt(chat_id, t, show_none=True):
    LANGUAGE = prev_locale(chat_id)
    if LANGUAGE:
        LOCALE = LANGUAGE.locale_name
        if LOCALE in ('ar') and t in ArabicStrings:
            return ArabicStrings[t]
        else:
           return t
    elif show_none:
        return t
