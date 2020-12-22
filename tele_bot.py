from config import TB_TOKEN, CONFIG, use_mutex, tele_queue, job_queue
from telegram import Update, Bot, InputMediaPhoto
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

import logging
import re

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

START_MSG = "Started the bot here!"


class TelegramBot:
    def __init__(self):
        self.updater = Updater(TB_TOKEN)
        self.bot = Bot(TB_TOKEN)
        self.dp = self.updater.dispatcher
        self.init_handlers()
        logger.info("Telegram Bot initialised")

    def init_handlers(self):
        self.dp.add_handler(CommandHandler('start', start_cmd))
        self.dp.add_handler(CommandHandler('toggle', toggle_cmd))
        self.dp.add_handler(CommandHandler('latest', latest_cmd))

    def run(self):
        try:  # Non-fatal ValueError always occurs when running updater.idle() in sub-thread, so just hiding it here
            self.updater.start_polling()
            self.updater.idle()
        except ValueError:
            pass

    # UTILITIES
    def start_messaging_queue(self) -> None:
        logger.info("Starting to read message queue...")
        while True:
            tweet_items = tele_queue.get()
            tweet_str, *tweet_photos = tweet_items
            if not tweet_str:  # exit condition - no more tweets
                break
            elif tweet_photos:
                #  send the photos with the tweet text as caption
                logger.info("Sending message with image(s):\n" + tweet_str)
                if len(tweet_photos) == 1:
                    self.bot.send_photo(chat_id=CONFIG['chat_id'], photo=tweet_photos[0], caption=tweet_str)
                else:
                    tweet_media_group = [InputMediaPhoto(media=each) for each in tweet_photos]
                    self.bot.send_message(chat_id=CONFIG['chat_id'], text=tweet_str)
                    self.bot.send_media_group(chat_id=CONFIG['chat_id'], media=tweet_media_group)
            else:
                logger.info("Sending message:\n" + tweet_str)
                self.bot.send_message(chat_id=CONFIG['chat_id'], text=tweet_str)
            tele_queue.task_done()


# UTILITIES
"""
def extract_image_url(tweet):
    url_list = []
    while result := re.search("https://t.co(\S)*(\s)*", tweet):
        tweet = tweet[result.span()[1]:]
        url = str(result.group()).strip()
        url_list.append(url)
    return url_list
"""


# HANDLERS
@use_mutex
def start_cmd(update: Update, context: CallbackContext) -> None:
    logging.info(f"/start - Telegram Bot started in chat ID: {update.message.chat_id}")
    CONFIG['chat_id'] = update.message.chat_id
    update.message.reply_text(START_MSG)


@use_mutex
def toggle_cmd(update: Update, context: CallbackContext) -> None:
    if not CONFIG['chat_id']:
        logging.warn("/toggle - Tried to run while not initialised")
        return
    logging.info(f"/toggle - Toggling 'enabled' to: {not CONFIG['enabled']}")
    if not CONFIG['enabled']:
        update.message.reply_text("I'll continue sending you tweets now!")
    else:
        update.message.reply_text("I'll stop sending you tweets for now. Use /toggle to re-enable me!")
    CONFIG['enabled'] = not CONFIG['enabled']


def latest_cmd(update: Update, context: CallbackContext) -> None:
    if not CONFIG['chat_id']:
        logging.warn("/latest - Tried to run while not initialised")
        return
    logging.info(f"/latest - Running")
    update.message.reply_text("Got it! Here are the latest tweets...")
    job_queue.put('latest')  # request the job thread to fill the tweet queue here


if __name__ == "__main__":
    tb = TelegramBot()
    tb.bot.send_photo(chat_id=234058962, photo="https://pbs.twimg.com/media/Ep2BhyzU0AAa0Uo?format=jpg&name=large")