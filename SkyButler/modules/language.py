from telegram.ext import CommandHandler, Filters
from telegram import ParseMode
from SkyButler import dispatcher
from SkyButler.modules.translations.strings import sbt
from SkyButler.modules.sql.translation import switch_to_locale, prev_locale
from SkyButler.modules.translations.list_locale import list_locales
from SkyButler.modules.helper_funcs.chat_status import user_admin


@user_admin
def change_locale(bot, update, args):
    chat = update.effective_chat
    if len(args) > 0:
        locale = args[0].lower()
        if locale in list_locales:
            if locale in  ('en', 'ar'):
                switch_to_locale(chat.id, locale)
                update.message.reply_text(sbt(update.effective_chat.id, 'Switched to {} successfully!').format(list_locales[locale]))
            else:
                update.message.reply_text(sbt(update.effective_chat.id, "{} not supported yet!").format(list_locales[locale]))
        else:
            update.message.reply_text(sbt(update.effective_chat.id, "Is that even a valid language code? Use an internationally accepted ISO code!"))
    else:
        update.message.reply_text(sbt(update.effective_chat.id, "You haven't give me a locale to begin with!"))


def curn_locale(bot, update):
    chat_id = update.effective_chat.id
    LANGUAGE = prev_locale(chat_id)
    if LANGUAGE:
        locale = LANGUAGE.locale_name
        native_lang = list_locales[locale]
        update.message.reply_text(sbt(chat_id, "Current locale for this chat is: *{}*").format(native_lang), parse_mode = ParseMode.MARKDOWN)
    else:
        update.message.reply_text("Current locale for this chat is: *English*", parse_mode = ParseMode.MARKDOWN)

__help__ = """
 - /setlocale <locale>

Currently available languages:
 - en (English)
 - ar (Arabic)
"""

__mod_name__ = "Locale"


CURN_LOCALE_HANDLER = CommandHandler("localenow", curn_locale)
LOCALE_HANDLER = CommandHandler("setlocale", change_locale, pass_args=True, filters=Filters.group)
dispatcher.add_handler(LOCALE_HANDLER)
dispatcher.add_handler(CURN_LOCALE_HANDLER)
