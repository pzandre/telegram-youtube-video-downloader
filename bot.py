#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# This program is dedicated to the public domain under the CC0 license.

import logging
import os
from dotenv import load_dotenv
from pytube import YouTube
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from slugify import slugify

# Read environment variables file
load_dotenv()

TOKEN = os.getenv('TOKEN')

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


# Define a few command handlers. These usually take the two arguments update and
# context. Error handlers also receive the raised TelegramError object in error.
def start(update, context):
    """Send a message when the command /start is issued."""
    # update.message.reply_text('Hey! Please send a valid Youtube video URL.')
    context.bot.send_message(chat_id=update.effective_chat.id, text="Hey! Please send a valid Youtube video URL.")


def help(update, context):
    """Send a message when the command /help is issued."""
    update.message.reply_text('Just pass a valid URL.')


def echo(update, context):
    """Echo the user message."""
    update.message.reply_text(update.message.text)


def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def download(update, context):
    """Process the URL to return the video file"""
    URL = update.message.text
    video = YouTube(URL)
    video_streams = video.streams.filter(file_extension='mp4').get_by_itag(22)
    filename = slugify(video_streams.title)
    video_streams.download(filename=filename)
    context.bot.send_video(chat_id=update.message.chat_id,
                           video=open(f'{filename}.mp4', 'rb'),
                           timeout=120)
    os.remove(f'{filename}.mp4')


def main():
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    updater = Updater(TOKEN, use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))

    # on noncommand i.e message - echo the message on Telegram
    dp.add_handler(MessageHandler(Filters.text, download))   

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()

