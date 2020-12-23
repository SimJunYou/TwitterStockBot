from config import TB_TOKEN, CONFIG, USERS, use_mutex, tele_queue, job_queue
from telegram import Update, Bot, InputMediaPhoto, ParseMode
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

import logging

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

START_MSG = ("Bot started. Will send you latest tweets from the people here:\n"
             + "\n".join(USERS) + "\n\n"
             + "You can also use /latest to get their most recent tweets if you're impatient, "
             + "or /recommend to search for their portfolios and recommendations."
             + "Also, you can use /toggle if I'm getting annoying.\n\n"
             + "Disclaimer: Not liable for any financial losses.")


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
        self.dp.add_handler(CommandHandler('recommend', recommend_cmd))

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
            if not CONFIG['enabled']:
                continue

            tweet_str, *tweet_photos = tweet_items
            if tweet_photos:
                #  send the photos with the tweet text as caption
                logger.info("Sending message with image(s):\n" + tweet_str)
                if len(tweet_photos) == 1:
                    self.bot.send_photo(chat_id=CONFIG['chat_id'],
                                        photo=tweet_photos[0],
                                        caption=tweet_str)
                else:
                    tweet_media_group = [InputMediaPhoto(media=each) for each in tweet_photos]
                    self.bot.send_message(chat_id=CONFIG['chat_id'],
                                          text=tweet_str)
                    self.bot.send_media_group(chat_id=CONFIG['chat_id'],
                                              media=tweet_media_group)
            else:
                logger.info("Sending message:\n" + tweet_str)
                self.bot.send_message(chat_id=CONFIG['chat_id'],
                                      text=tweet_str)
            tele_queue.task_done()


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
    logging.info(f"/latest - Called")
    update.message.reply_text("Got it! Here are the latest tweets...")
    job_queue.put('latest')  # request the job thread to fill the tweet queue here
    logging.info(f"/latest - Placed job request for latest tweets")


def recommend_cmd(update: Update, context: CallbackContext) -> None:
    if not CONFIG['chat_id']:
        logging.warn("/recommend - Tried to run while not initialised")
        return
    logging.info(f"/recommend - Called")
    update.message.reply_text("Let me look for their recommendations...")
    job_queue.put('recommend')
    logging.info(f"/recommend - Placed job request for recommendations")


# for debug only
if __name__ == "__main__":
    tb = TelegramBot()
    tb.bot.send_photo(chat_id=234058962, photo="https://pbs.twimg.com/media/Ep2BhyzU0AAa0Uo?format=jpg&name=large")