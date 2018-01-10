#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Telegram bot for searching through ArchWiki pages
# This program is dedicated to the public domain under the GPL3 license.

"""
Written by: @Alireza6677
alireza6677@gmail.com
"""
from uuid import uuid4

import logging
import bs4
import requests
import json

from telegram import InlineQueryResultArticle, InputTextMessageContent
from telegram.ext import Updater, InlineQueryHandler, CommandHandler

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)

logger = logging.getLogger(__name__)

def start(bot, update):
    bot.sendMessage(update.message.chat_id, text='This bot can search in arch wiki for you in in-line mode. /help for more info.')

def help(bot, update):
    bot.sendMessage(update.message.chat_id, text="""To search with this bot you can easily type @archwikibot and then something you want to search. for example :
@archwikibot Tor
or
@archwikibot Cron
...""")
    
        
def escape_markdown(text):
    """Helper function to escape telegram markup symbols"""
    escape_chars = '\*_`\['
    return re.sub(r'([%s])' % escape_chars, r'\\\1', text)


def inlinequery(bot, update):
    query = update.inline_query.query
    results = list()

    prefix = "https://wiki.archlinux.org/index.php?profile=default&fulltext=Search&search="
    page = requests.get(prefix + query)
    ex = bs4.BeautifulSoup(page.content , "html.parser")
    names = ex.find_all("div" , {"class" :"mw-search-result-heading"})
    
    for one in names:
        #print(one.a['title'] , " :  " , one.a['href'])
        content = ''
        link = 'https://wiki.archlinux.org' + one.a['href']
            
        results.append(InlineQueryResultArticle(
            id=uuid4(),
            title=one.a['title'], 
            input_message_content=InputTextMessageContent(one.a['title'] + "\n" + link)))



    bot.answerInlineQuery(update.inline_query.id, results=results)

def error(bot, update, error):
    logger.warn('Update "%s" caused error "%s"' % (update, error))

	

        
def main():
    # Create the Updater and pass it your bot's token.
    updater = Updater("REPLACE WITH YOUR TOKEN")
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

if __name__ == '__main__':
    main()
