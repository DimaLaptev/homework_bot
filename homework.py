import os
import time

import requests
import http

import telegram
from telegram.ext import Updater, CommandHandler, CallbackContext
from dotenv import load_dotenv

import logging

load_dotenv()


PRACTICUM_TOKEN: str = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN: str = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID: int = os.getenv('TELEGRAM_CHAT_ID')

RETRY_PERIOD: int = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}


HOMEWORK_VERDICTS = {
    'approved': 'The work is verified: the reviewer liked everything!',
    'reviewing': 'The work has been taken for review.',
    'rejected': 'The work has been verified: there are comments.'
}

logging.basicConfig(
    filename='program.log',
    level=logging.DEBUG,
    filemode='w',
    format='%(asctime)s - %(levelname)s - %(message)s - %(name)s',
)
logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler())


def checkout_tokens() -> bool:
    '''checkout of tokens'''
    items = ('PRACTICUM_TOKEN',
             'TELEGRAM_TOKEN',
             'TELEGRAM_CHAT_ID')
    error_items = set()
    for item in items:
        if globals()[item] in None:
            error_items.add(item)
    if len(error_items) == 0:
        return True
    else:
        logging.critical('Tokens not found',
                        f'{" ,".join(error_items)}')
        return False



def send_message(bot, message):
    ...


def get_api_answer(timestamp):
    ...


def check_response(response):
    ...


def parse_status(homework):
    ...

    return f'The status of work verification has changed "{homework_name}". {verdict}'


def main():
    """The main logic of the bot."""

    if not check_tokens():
        raise ValueError('Token not found!')
    

    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    timestamp = int(time.time())

    ...

    while True:
        try:

            ...

        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            ...
        ...


if __name__ == '__main__':
    main()
