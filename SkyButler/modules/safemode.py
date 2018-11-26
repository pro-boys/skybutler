import html
from typing import Optional, List
from telegram import ParseMode
from telegram import Update, Bot
from telegram.ext import Filters
from telegram.utils.helpers import mention_html
from telegram.ext.dispatcher import run_async
from SkyButler.modules.log_channel import loggable
from SkyButler import dispatcher
from SkyButler.modules.disable import DisableAbleCommandHandler
from SkyButler.modules.sql.users_sql import set_safemode, get_safemode
from SkyButler.modules.helper_funcs.chat_status import bot_admin, can_restrict, user_admin
from SkyButler.modules.translations.strings import sbt


@run_async
@bot_admin
@user_admin
@can_restrict
@loggable
def safe_mode(bot: Bot, update: Update, args: List[str]) -> str:
    chat = update.effective_chat  # type: Optional[Chat]
    user = update.effective_user  # type: Optional[User]
    message = update.effective_message  # type: Optional[Message]

    if len(args) == 0:
        message.reply_text(sbt(chat.id, "Unrecognised argument - please use a number, 'off', or 'no'."))
        return ""

    if len(args) >= 1:
        val = args[0].lower()
        if val == "off" or val == "no" or val == "0":
            set_safemode(chat.id, 0)
            message.reply_text(sbt(chat.id, "Safemode has been disabled."))
            return "<b>{}:</b>" \
                   "\n#SAFEMODE" \
                   "\n<b>Admin:</b> {}" \
                   "\nDisabled safemode".format(html.escape(chat.title), mention_html(user.id, user.first_name))

        elif val.isdigit():
            safemode = int(val)
            if safemode < 1:
                message.reply_text(sbt(chat.id, "Safemode has to be either 1 or max 60!"))
                return ""

            elif safemode > 60:
                message.reply_text(sbt(chat.id, "Safemode has to be either 1 or max 60!"))
                return ""

            else:
                set_safemode(chat.id, safemode)
                message.reply_text(sbt(chat.id, "Safemode has been set to *{}h*").format(safemode), parse_mode=ParseMode.MARKDOWN)
                return "<b>{}:</b>" \
                       "\n#SAFEMODE" \
                       "\n<b>Admin:</b> {}" \
                       "\nSet safemode to <code>{}h</code>".format(html.escape(chat.title),
                                                                    mention_html(user.id, user.first_name), safemode)

        else:
            message.reply_text(sbt(chat.id, "Unrecognised argument - please use a number, 'off', or 'no'."))

    return ""


@run_async
def safe_status(bot: Bot, update: Update):
    chat = update.effective_chat  # type: Optional[Chat]
    chat_id = update.effective_chat.id # type: Optional[Chat]
    limit = get_safemode(chat.id)
    if limit == 0:
        update.effective_message.reply_text(sbt(chat_id, "Safemode is disabled"))
    else:
        update.effective_message.reply_text(sbt(chat_id,
            "Safemode is enabled and its time its set to *{}h*").format(limit), parse_mode=ParseMode.MARKDOWN)


def __chat_settings__(chat_id, user_id):
    limit = get_safemode(chat_id)
    if limit == 0:
        return sbt(chat_id, "Safemode is disabled")
    else:
        return sbt(chat_id, "Safemode is enabled and its time its set to {}h.").format(limit)


__help__ = """
 - /safestatus: Get the current safemode settings

*Admin only:*
 - /safemode <int/'no'/'off'>: Restricts every user that joins after enabling safemode from sending media for how much you set it
"""

__mod_name__ = "Safemode"


SAFEMODE_HANDLER = DisableAbleCommandHandler("safemode", safe_mode, pass_args=True, filters=Filters.group)
SAFESTATUS_HANDLER = DisableAbleCommandHandler("safestatus", safe_status, filters=Filters.group)

dispatcher.add_handler(SAFEMODE_HANDLER)
dispatcher.add_handler(SAFESTATUS_HANDLER)
