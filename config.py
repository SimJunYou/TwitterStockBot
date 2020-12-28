from threading import Lock
from queue import Queue
from dotenv import load_dotenv, find_dotenv
import os
import logging

# Global config values for the bot
CONFIG = {'enabled': True,
          'realtime': True,
          'chat_id': None}
CONFIG_MUTEX = Lock()

# Global logging level
LOG_LVL = logging.INFO


# Decorator function for the mutex lock and acquire
def use_mutex(func):
    def wrapper(*args):
        CONFIG_MUTEX.acquire()
        output = func(*args)
        CONFIG_MUTEX.release()
        return output
    return wrapper


# Message queues for IPC
tele_queue = Queue()
job_queue = Queue()

# Tokens for API access (both Telegram and Twitter)
load_dotenv(find_dotenv())
TB_TOKEN = os.environ.get("TB_TOKEN")
C_KEY = os.environ.get("C_KEY")
C_SEC = os.environ.get("C_SEC")
A_KEY = os.environ.get("A_KEY")
A_SEC = os.environ.get("A_SEC")
TW_KEY_SET = (C_KEY, C_SEC, A_KEY, A_SEC)

# Twitter Users to watch for
USERS = ['@saxena_puru',
         '@cperruna',
         '@bot_stweet']
