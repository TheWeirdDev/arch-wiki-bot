#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Telegram bot for searching through ArchWiki pages
# This program is dedicated to the public domain under the GPL3 license.

"""
Written by: @Alireza6677
alireza6677@gmail.com

Updated in 27/05/2021 by: @NicKoehler
"""

import os
import sys
import json
import logging
from uuid import uuid4
from gazpacho import get, Soup
from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Updater, InlineQueryHandler, CommandHandler
from telegram import InlineQueryResultArticle, InputTextMessageContent

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

logger = logging.getLogger(__name__)


def start(update, context):
    update.message.reply_text(
        "This bot can search in arch wiki for you in in-line mode.\n/help for more info.",
    )


def help(update, context):
    update.message.reply_text(
        """To search with this bot you can easily type @archwikibot and then something you want to search. for example :
@archwikibot Tor
or
@archwikibot Cron
...""",
    )


def inlinequery(update, context):
    query = update.inline_query.query
    results = []

    prefix = "https://wiki.archlinux.org/index.php?profile=default&fulltext=Search&search="

    try:
        page = get(prefix + query)
    except Exception as e:
        update.message.reply_text("Sorry, archlinux wiki is offline.")
        logger.error(e)
        return

    html = Soup(page)
    names = html.find("li", {"class": "mw-search-result"}, mode="all")

    for one in names:

        temp = one.find("div", {"class": "mw-search-result-heading"})
        title = temp.text
        description = one.find(
            "div", {"class": "mw-search-result-data"}, mode="first"
        ).text
        link = f"https://wiki.archlinux.org{temp.find('a').attrs['href']}"

        results.append(
            InlineQueryResultArticle(
                id=uuid4(),
                title=title,
                description=description,
                input_message_content=InputTextMessageContent(
                    message_text=title,
                ),
                reply_markup=InlineKeyboardMarkup(
                    [
                        [InlineKeyboardButton("Read the docs", url=link)],
                    ]
                ),
            )
        )

    update.inline_query.answer(results, cache_time=0)


def error(update, context):
    logger.warning(f"Update {update} caused error {context.error}")


def main():
    # Create the Updater and pass it your bot's token.
    try:
        token = os.environ["BOT_TOKEN"]
    except KeyError:
        logger.critical(
            "No BOT_TOKEN environment variable passed. Terminating."
        )
        sys.exit(1)

    updater = Updater(token)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))

    # on noncommand i.e message - echo the message on Telegram
    dp.add_handler(InlineQueryHandler(inlinequery))

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Block until the user presses Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == "__main__":
    main()
