import pyowm
from pyowm import exceptions
from telegram.ext import run_async

from SkyButler import dispatcher, API_WEATHER
from SkyButler.modules.translations.strings import sbt
from SkyButler.modules.disable import DisableAbleCommandHandler

@run_async
def weather(bot, update, args):
    chat_id = update.effective_chat.id
    if len(args) == 0:
        update.effective_message.reply_text(sbt(chat_id, "Write a location to check the weather."))
        return

    location = " ".join(args)
    if location.lower() == bot.first_name.lower():
        update.effective_message.reply_text(sbt(chat_id, "I will keep an eye on both happy and sad times!"))
        return

    try:
        owm = pyowm.OWM(API_WEATHER)
        observation = owm.weather_at_place(location)
        getloc = observation.get_location()
        thelocation = getloc.get_name()
        if thelocation == None:
            thelocation = "Unknown"
        theweather = observation.get_weather()
        temperature = theweather.get_temperature(unit='celsius').get('temp')
        if temperature == None:
            temperature = "Unknown"

        status = theweather._detailed_status

        update.message.reply_text(sbt(chat_id, "Today in {} is being {}, around {}°C.\n").format(thelocation,
                status, temperature))

    except pyowm.exceptions.api_response_error.NotFoundError:
        update.effective_message.reply_text(sbt(chat_id, "Sorry, location not found."))


__help__ = """
 - /weather <city>: get weather info in a particular place
"""

__mod_name__ = "Weather"

WEATHER_HANDLER = DisableAbleCommandHandler("weather", weather, pass_args=True)

dispatcher.add_handler(WEATHER_HANDLER)
