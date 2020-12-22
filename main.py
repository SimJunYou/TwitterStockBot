from tele_bot import TelegramBot
from twit_bot import TwitterBot
from config import CONFIG, USERS, job_queue
from threading import Thread
import logging

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


def main():
    logger.info("Initialising Telegram bot...")
    tele = TelegramBot()
    logger.info("Initialising Twitter bot...")
    twit = TwitterBot()

    logger.info("Running Telegram bot in its own thread to handle commands...")
    telegram_bot_thread = Thread(target=tele.run, daemon=True)
    telegram_bot_thread.start()

    # Main thread handles job requests between the bots
    while True:
        job = job_queue.get()
        logger.info("Received job: " + job)
        if job == 'latest':
            twit.get_latest_tweets()
            tele.start_messaging_queue()
        elif job == 'message' and CONFIG['enabled']:
            tele.start_messaging_queue()
        # to add more tasks later on
        job_queue.task_done()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        logger.info("Program ended")
