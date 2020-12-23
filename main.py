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

    logger.info("Running command-handling Telegram bot in its own thread...")
    tele_command_thread = Thread(target=tele.run, daemon=True)
    tele_command_thread.start()

    logger.info("Running message-sending Telegram bot in its own thread...")
    tele_message_thread = Thread(target=tele.start_messaging_queue, daemon=True)
    tele_message_thread.start()

    logger.info("Running tweet-tracking Twitter bot in its own thread...")
    tele_message_thread = Thread(target=twit.start_track_stream, daemon=True)
    tele_message_thread.start()

    # Main thread handles job requests between the bots
    while True:
        logger.info("Awaiting job")
        job = job_queue.get()
        logger.info("Received job: " + job)
        if job == 'latest':
            twit.get_latest_tweets()
        elif job == 'recommend':
            twit.get_recommendations()
        # to add more tasks later on
        job_queue.task_done()
        logger.info("Completed job: " + job)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        logger.info("Program ended")
