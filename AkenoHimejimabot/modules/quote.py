# Python-telegram-bot libraries
import telegram
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from telegram import ReplyKeyboardMarkup, ChatAction
from functools import wraps

# Logging and requests libraries
import logging

# Importing JSON library
import json
import random

# Import Pandas library
import pandas as pd



# Logging module for debugging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                     level=logging.INFO)

# Converting our JSON file into a Pandas DataFrame
df = pd.read_json('quotes.json')

# Converting into a list
quote_text = list(x for x in df["quoteText"])

# Creating a reply keyboard
reply_keyboard = [['/quote']]
markup = ReplyKeyboardMarkup(reply_keyboard, resize_keyboard = True)

# Typing animation to show to user to imitate human interaction
def send_action(action):
    def decorator(func):
        @wraps(func)
        def command_func(*args, **kwargs):
            bot, update = args
            bot.send_chat_action(chat_id=update.effective_message.chat_id, action=action)
            return func(bot, update, **kwargs)
        return command_func
    return decorator

send_typing_action = send_action(ChatAction.TYPING)

# Quote Message function to display the quotes
@send_typing_action
def quote_message(bot, update):
    random_quote = random.choice(quote_text)
    bot.send_message(chat_id = update.message.chat_id, text = random_quote)

quote_message_handler = CommandHandler('quote', quote_message)
dispatcher.add_handler(quote_message_handler)

# Updater function to start polling
updater.start_polling()
updater.idle()
