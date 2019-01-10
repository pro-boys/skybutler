import telegram.ext as tg
from telegram import Update
from SkyButler.modules.sql.global_bans_sql import is_user_gbanned

CMD_STARTERS = ('/', '!')


class SkyCommandHandler(tg.CommandHandler):
    def __init__(self, command, callback, **kwargs):
        if "admin_ok" in kwargs:
            del kwargs["admin_ok"]
        super().__init__(command, callback, **kwargs)

    def check_update(self, update):
        if (isinstance(update, Update)
                and (update.message or update.edited_message and self.allow_edited)):
            message = update.message or update.edited_message

            if is_user_gbanned(update.effective_user.id):
                return False

            if message.text and len(message.text) > 1:
                first_word = message.text_html.split(None, 1)[0]
                if len(first_word) > 1 and any(first_word.startswith(start) for start in CMD_STARTERS):
                    command = first_word[1:].split('@')
                    command.append(
                        message.bot.username)  # in case the command was sent without a username

                    if not (command[0].lower() in self.command
                            and command[1].lower() == message.bot.username.lower()):
                        return False

                    if self.filters is None:
                        res = True
                    elif isinstance(self.filters, list):
                        res = any(func(message) for func in self.filters)
                    else:
                        res = self.filters(message)

                    return res

        return False


class CustomRegexHandler(tg.RegexHandler):
    def __init__(self, pattern, callback, friendly="", **kwargs):
        super().__init__(pattern, callback, **kwargs)
