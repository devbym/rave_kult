#!/usr/bin/env python

import json
import logging
import re
from datetime import timedelta, datetime as dt
from enum import Enum, auto

import config
import telegram

from telegram import (InlineKeyboardButton, InlineKeyboardMarkup,
                      InlineQueryResultArticle, InputTextMessageContent,
                      KeyboardButton, ParseMode,
                      ReplyKeyboardMarkup, ReplyKeyboardRemove, Update)
from telegram.ext import (CallbackContext, CallbackQueryHandler,
                          CommandHandler, ConversationHandler, Filters,
                          MessageHandler, Updater)

"""This bot will be dedicated to the CZ Raves Channel where it will perform several functions.
1 WEEKLY - Post a weekly summary of the upcoming events in a certain location. Initially limited Prague
2 SEARCH - Provide a search function to search events on a specific date (location search to be implemented later)
3 INFO - Provide convenient links to external resources related to events. eg. ticketshop, organisator
4 INVITES - 
"""

class Monthnames(Enum):
    January = 1 
    February = 2
    March = 3
    April=4
    May=5
    June=6
    July=7
    August = 8
    September = 9
    October = 10
    November = 11
    December = 12

    def __repr__(self) -> str:
        return super().name.__repr__()

    @classmethod
    def from_date(cls, date):
        return cls(date.month)



class Weekday(Enum):
    Monday = 1
    Tuesday = 2
    Wednesday = 3
    Thursday = 4
    Friday = 5
    Saturday = 6
    Sunday = 7

    def __repr__(cls) -> str:
        return super().name.__repr__()

    @classmethod
    def from_date(cls, date,isoformat=False):
        if isoformat:
            _year,week,weekday = date.isocalendar()
            weekday = weekday+1
        return cls(date.isoweekday())
    

class CurrentWeek(Enum):
    """Get range of complete, Separate weekend"""
    _length = timedelta(days=7)
    BaseDay = dt.now().isoweekday()).value
    _offset = timedelta(days=7-BaseDay)
    FirstDay = timedelta(days=BaseDay*-1)
    LastDay =  timedelta(days=BaseDay-7)

# Objective 1  - Post a weekly summary of the upcoming events in Prague on the cz_raves channel
# A table of events
# Script that fires at a set time > use crontab
# reads a template file

# A week starts on Monday(0)

def setLogger():
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
    return logging.getLogger(__name__)

def getEvents():
    with open("events.json", mode="r", encoding="utf-8") as fo:
        fd = json.load(fo)
        eventData = fd['events']['2022']
        logger.info("Events loaded")
    return eventData

def getToken():
    with open("/home/m/Documents/Dev/BOTS/sleutels.json", "r", encoding='utf-8') as keyfile:
        keys = json.load(keyfile)
        TOKEN = keys.get('Telegram')['KEY']
    return TOKEN



def start(update: Update, context: CallbackContext) -> int:
    """Starts the conversation and asks the user about their location."""
    kb = [
        [KeyboardButton("Share location (mobile only)", request_location=True)],
        [KeyboardButton("Select location manually",callback_data={})],
        [KeyboardButton("Visit the website",url="t.me/cz_raves")]
        ]
    markup = ReplyKeyboardMarkup(kb, one_time_keyboard=True)
    update.message.reply_text(
        '👽 Greetings! Welcome to Rave Kult! \n\n ' +
        'Use the bot to search for events,check updates, mark your attendance & send invites\n\n' +
        'Follow our channel: t.me/cz_raves \n' +
        '- /help - See helpmenu\n',
        reply_markup=markup,
    )
    logger.info(f"User {update.effective_user.full_name} started the bot\nLANG: {update.effective_user.language_code}")
    #logger.info(update.callback_query)
    return kb_remove(update)
      
def kb_remove(update:Update):
    logger.info("No user input received")
    update.message.reply_markup = ReplyKeyboardRemove()


def get_help(update: Update, context: CallbackContext):
    kb = [[InlineKeyboardButton(
        "Message the developer", url='telegram.me/devbym')],[InlineKeyboardButton("Resident Advisor", url="residentadvisor.org")]]
    user = update.message.from_user     
    # markup = InlineKeyboardMarkup(kb, one_time_keyboard=True)
    logger.info("Help for %s: %s", user.first_name, update.message.text)
    context.bot.send_message(
        update.effective_chat.id,text=
        f'Rave Cult Event bot (v{config.VERSION}) - Helpmenu\n\n' +
        'events - List all events for your current location\n' +
        'today - Returns events in this weekend for your current location  \n'
        '/weekend - Returns events in this weekend for your current location\n',
        reply_markup=ReplyKeyboardRemove())


def events(update: Update, context: CallbackContext,**kwargs):
    tdy = dt.today()
    ev = allEvents[str(tdy.month)]
    if ev:
        context.bot.send_message(chat_id=update.effective_chat.id,text=
        f"Events in\n---{Monthnames.from_date(tdy).name}--- ")
        for day in ev:
            if ev[day]: 
                context.bot.send_message(chat_id=update.effective_chat.id,text=f"<b>📍On {Weekday(int(day)+1).name} {day} {Monthnames.from_date(tdy).name}</b>",parse_mode=ParseMode.HTML)
                for name in ev[day]:
                    event = ev[day][name]
                    context.bot.send_message(
                        chat_id=update.effective_chat.id, text=f"<b>{name}</b>\n\n{event['location']} - {event['venue']}\n Check more: <a href='www.example.com'>here</a>",parse_mode=ParseMode.HTML)
            else:
                pass
    else:
        context.bot.send_message(
                    chat_id=update.effective_chat.id, text="No events found")


def today(update: Update, context: CallbackContext,**kwargs):
    dd = dt.today()
    m = dd.month
    d = dd.day
    # FIX: The correct day is not selected, keeps replying "Friday"
    ev = allEvents[str(m)]
    if ev.get(str(d)):
        ev = ev[str(d)]
        context.bot.send_message(chat_id=update.effective_chat.id, text=f"📍Today {Weekday(dd.weekday()).name}:")
        for name in ev:
            event = ev[name]
            context.bot.send_message(
                chat_id=update.effective_chat.id, text=f"<b>{name}</b> in\n <b>{event['location']}</b> \n\n <I>Buy tickets <a href='example.com'>here</a></I>",parse_mode=ParseMode.HTML)
    else:
        context.bot.send_message(
            chat_id=update.effective_chat.id, text="No events found")



def button(update: Update, context: CallbackContext) -> None:
    """Parses the CallbackQuery and updates the message text."""
    query = update.callback_query
    query.answer()
    user = update.effective_user  # type: Optional[User]
    chat = update.effective_chat
    user_member = chat.get_member(user.id)
    # CallbackQueries need to be answered, even if no notification to the user is needed
    # Some clients may have trouble otherwise. See https://core.telegram.org/bots/api#callbackquery

    logger.info(f"Selected: {query.data} by {user.first_name}")
    update.edit_message_text(text=f"Try Again!: {query.data}")





def unknown(update: Update, context: CallbackContext):
    context.bot.send_message(
        chat_id=update.effective_chat.id, text="That is not a command.")
    return ConversationHandler.END


def errorhandler(update: Update, context: CallbackContext):
    logger.error("An error occured",exc_info=True)
    context.bot.send_message(
        chat_id=update.effective_chat.id, text="Error")
    return ConversationHandler.END   

def setMessageHandlers(dispatcher):
    dispatcher.add_handler(MessageHandler(
        Filters.text & Filters.regex(r'^(events|Events)'), events))
    dispatcher.add_handler(MessageHandler(
        Filters.text & Filters.regex(r'^(today|Today)'), today))
    return dispatcher

def main(token):
    """Assign the dispatcher and updater with the API token. Run the bot.
    HANDLERS:
    1 - events: Returns events on a certain date
    2 - today: Returns todays events
    4 - weekend: Return coming weekend
    """
    updater = Updater(token)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher = setMessageHandlers(dispatcher)


    dispatcher.add_handler(CallbackQueryHandler(button))
    dispatcher.add_handler(CommandHandler('help', get_help))
    dispatcher.add_handler(MessageHandler(Filters.command, unknown))

    dispatcher.add_error_handler(errorhandler)
    # Start the Bot
    updater.start_polling(drop_pending_updates=True)

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and this will stop the bot gracefully.
    updater.logger.info("Bot polling started")
    updater.idle()


if __name__ == '__main__':
    logger = setLogger()
    # Load events
    allEvents = getEvents()
    # Load API token
    TOKEN = getToken()
    # Run the main loop
    main(TOKEN)
