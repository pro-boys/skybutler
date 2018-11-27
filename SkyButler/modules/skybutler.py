import time
from typing import List
from telegram import ParseMode
from telegram import Update, Bot
from telegram.error import BadRequest, Unauthorized
from telegram.utils.helpers import mention_html
from telegram.ext import CommandHandler
from telegram.ext.dispatcher import run_async
from SkyButler.modules.disable import DisableAbleCommandHandler
from SkyButler.modules.helper_funcs.extraction import extract_user_and_text
from SkyButler.modules.helper_funcs.chat_status import bot_admin, is_user_ban_protected, is_user_in_chat, can_restrict, \
    is_bot_admin, is_user_admin
import SkyButler.modules.sql.users_sql as sql
from SkyButler import dispatcher, SUDO_USERS, LOGGER
from SkyButler.modules.helper_funcs.filters import CustomFilters
from SkyButler.modules.translations.strings import sbt

RBAN_ERRORS = {
    "User is an administrator of the chat",
    "Chat not found",
    "Not enough rights to restrict/unrestrict chat member",
    "User_not_participant",
    "Peer_id_invalid",
    "Group chat was deactivated",
    "Need to be inviter of a user to kick it from a basic group",
    "Chat_admin_required",
    "Only the creator of a basic group can kick group administrators",
    "Channel_private",
    "Not in the chat"
}

CREDITS_STRING = """
<b>Credits & Special thanks to:</b>
@SonOfLars - Base
@kubersharma
@kaywhen
@AyraHikari
@ganeshvarma
@Adityaupreti
@Dyneteve
@deletescape
@Sanchith_Hegde
@julianodorneles
@sphericalkat
"""


@run_async
def credits(bot: Bot, update: Update):
    update.effective_message.reply_text(CREDITS_STRING, parse_mode=ParseMode.HTML)


@run_async
def sudolist(bot: Bot, update: Update):
    text = "<b>My sudo users are:</b>"
    for user in SUDO_USERS:
        name = mention_html(user, bot.get_chat(user).first_name)
        text += "\n - {}".format(name)

    update.effective_message.reply_text(text="{}".format(text), parse_mode=ParseMode.HTML)


@run_async
@bot_admin
def rban(bot: Bot, update: Update, args: List[str]):
    message = update.effective_message

    if not args:
        message.reply_text("You don't seem to be referring to a chat/user.")
        return

    user_id, chat_id = extract_user_and_text(message, args)

    if not user_id:
        message.reply_text("You don't seem to be referring to a user.")
        return
    elif not chat_id:
        message.reply_text("You don't seem to be referring to a chat.")
        return

    try:
        chat = bot.get_chat(chat_id.split()[0])
    except BadRequest as excp:
        if excp.message == "Chat not found":
            message.reply_text("Chat not found! Make sure you entered a valid chat ID and I'm part of that chat.")
            return
        else:
            raise

    if chat.type == 'private':
        message.reply_text("I'm sorry, but that's a private chat!")
        return

    if not is_bot_admin(chat, bot.id) or not chat.get_member(bot.id).can_restrict_members:
        message.reply_text("I can't restrict people there! Make sure I'm admin and can ban users.")
        return

    try:
        member = chat.get_member(user_id)
    except BadRequest as excp:
        if excp.message == "User not found":
            message.reply_text("I can't seem to find this user")
            return
        else:
            raise

    if is_user_ban_protected(chat, user_id, member):
        message.reply_text("I really wish I could ban admins...")
        return

    if user_id == bot.id:
        message.reply_text("I'm not gonna BAN myself, are you crazy?")
        return

    try:
        chat.kick_member(user_id)
        message.reply_text("Banned!")
    except BadRequest as excp:
        if excp.message == "Reply message not found":
            # Do not reply
            message.reply_text('Banned!', quote=False)
        elif excp.message in RBAN_ERRORS:
            message.reply_text(excp.message)
        else:
            LOGGER.warning(update)
            LOGGER.exception("ERROR banning user %s in chat %s (%s) due to %s", user_id, chat.title, chat.id,
                             excp.message)
            message.reply_text("Well damn, I can't ban that user.")


@run_async
@bot_admin
def runban(bot: Bot, update: Update, args: List[str]):
    message = update.effective_message

    if not args:
        message.reply_text("You don't seem to be referring to a chat/user.")
        return

    user_id, chat_id = extract_user_and_text(message, args)

    if not user_id:
        message.reply_text("You don't seem to be referring to a user.")
        return
    elif not chat_id:
        message.reply_text("You don't seem to be referring to a chat.")
        return

    try:
        chat = bot.get_chat(chat_id.split()[0])
    except BadRequest as excp:
        if excp.message == "Chat not found":
            message.reply_text("Chat not found! Make sure you entered a valid chat ID and I'm part of that chat.")
            return
        else:
            raise

    if chat.type == 'private':
        message.reply_text("I'm sorry, but that's a private chat!")
        return

    if not is_bot_admin(chat, bot.id) or not chat.get_member(bot.id).can_restrict_members:
        message.reply_text("I can't unrestrict people there! Make sure I'm admin and can unban users.")
        return

    try:
        member = chat.get_member(user_id)
    except BadRequest as excp:
        if excp.message == "User not found":
            message.reply_text("I can't seem to find this user there")
            return
        else:
            raise

    if is_user_in_chat(chat, user_id):
        message.reply_text("Why are you trying to remotely unban someone that\'s already in that chat?")
        return

    if user_id == bot.id:
        message.reply_text("I'm not gonna UNBAN myself, I'm an admin there!")
        return

    try:
        chat.unban_member(user_id)
        message.reply_text("Yep, this user can join that chat!")
    except BadRequest as excp:
        if excp.message == "Reply message not found":
            # Do not reply
            message.reply_text('Unbanned!', quote=False)
        elif excp.message in RBAN_ERRORS:
            message.reply_text(excp.message)
        else:
            LOGGER.warning(update)
            LOGGER.exception("ERROR unbanning user %s in chat %s (%s) due to %s", user_id, chat.title, chat.id,
                             excp.message)
            message.reply_text("Well damn, I can't unban that user.")


@run_async
@bot_admin
def getlink(bot: Bot, update: Update, args: List[str]):
    if args:
        chat_id = str(args[0])
    else:
        update.effective_message.reply_text("You don't seem to be referring to a chat")
    for chat_id in args:
        try:
            chat = bot.getChat(chat_id)
            bot_member = chat.get_member(bot.id)
            if bot_member.can_invite_users:
                invitelink = bot.exportChatInviteLink(chat_id)
                update.effective_message.reply_text("Invite link for: " + chat_id + "\n" + invitelink)
            else:
                update.effective_message.reply_text("I don't have access to the invite link.")
        except BadRequest as excp:
                update.effective_message.reply_text(excp.message + " " + str(chat_id))


@run_async
@bot_admin
def del_chat(bot: Bot, update: Update, args: List[str]):
    message = update.effective_message
    if args:
        chat_id = str(args[0])
        chat_title = sql.get_chatname_by_chatid(chat_id)
        if chat_title is None:
            message.reply_text("I can't seem to find the chat in my database.")
            return
    else:
        update.effective_message.reply_text("You don't seem to be referring to a chat")
        return
    try:
        sql.del_chat(chat_id)
        update.effective_message.reply_text("Chat deleted from db.")
    except BadRequest:
        update.effective_message.reply_text("Attempt failed.")


@run_async
@bot_admin
def ping(bot: Bot, update: Update):
    start_time = time.time()
    bot.send_message(update.effective_chat.id, "Starting ping testing now!")
    end_time = time.time()
    ping_time = float(end_time - start_time)*1000
    update.effective_message.reply_text(" Ping speed was : {}ms".format(ping_time))


PING_HANDLER = CommandHandler("ping", ping, filters=CustomFilters.sudo_filter)
GETLINK_HANDLER = CommandHandler("getlink", getlink, pass_args=True, filters=CustomFilters.sudo_filter)
RBAN_HANDLER = CommandHandler("rban", rban, pass_args=True, filters=CustomFilters.sudo_filter)
RUNBAN_HANDLER = CommandHandler("runban", runban, pass_args=True, filters=CustomFilters.sudo_filter)
DELCHAT_HANDLER = CommandHandler("delchat", del_chat, pass_args=True, filters=CustomFilters.sudo_filter)
SLIST_HANDLER = DisableAbleCommandHandler("sudolist", sudolist)
CREDITS_HANDLER = DisableAbleCommandHandler("credits", credits)

dispatcher.add_handler(SLIST_HANDLER)
dispatcher.add_handler(DELCHAT_HANDLER)
dispatcher.add_handler(CREDITS_HANDLER)
dispatcher.add_handler(PING_HANDLER)
dispatcher.add_handler(GETLINK_HANDLER)
dispatcher.add_handler(RBAN_HANDLER)
dispatcher.add_handler(RUNBAN_HANDLER)
