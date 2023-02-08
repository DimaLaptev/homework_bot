import sys
import os
import time

import json

import logging

import requests
from http import HTTPStatus

import telegram

from dotenv import load_dotenv


load_dotenv()


PRACTICUM_TOKEN = os.getenv('YA_TOKEN')
TELEGRAM_TOKEN = os.getenv('TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_ID')

RETRY_PERIOD: int = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}


HOMEWORK_VERDICTS = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}

'''Custom exceptions.'''
class RequestError(Exception):
    def __init__(self, code_status):
        self.code_status = code_status
        super().__init__(f'Code API-request: {code_status}')


class ApiError(Exception):
    def __init__(self):
        super().__init__('No access to API.')


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
formating = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

file_handler = logging.FileHandler('homeworks.log')
file_handler.setFormatter(formating)
logger.addHandler(file_handler)

consol_handler = logging.StreamHandler(sys.stdout)
consol_handler.setFormatter(formating)
logger.addHandler(consol_handler)


def check_tokens():
    """Tokens checkout."""
    if (
        PRACTICUM_TOKEN is None
        or TELEGRAM_TOKEN is None
        or TELEGRAM_CHAT_ID is None
    ):
        logger.critical('Tokens not found!')
        return False
    return True


def send_message(bot, message):
    """Bot sends a messsage."""
    try:
        bot.send_message(TELEGRAM_CHAT_ID, message)
    except telegram.TelegramError as error:
        logger.error(
            f'Message has not been sent: {error}')
    else:
        logging.debug('Message was sent successfully')


def get_api_answer(current_timestamp):
    """Get of API-Data."""
    timestamp = current_timestamp or int(time.time())
    params = {'from_date': timestamp}
    try:
        homework_statuses = requests.get(
            ENDPOINT,
            headers=HEADERS,
            params=params,
        )
    except requests.RequestException as error:
        message = f'Request not sent: {error}'
        logger.error(message)
        raise RequestError(message)
    if homework_statuses.status_code != HTTPStatus.OK:
        message = 'Response code is not 200!'
        logger.error(message)
        raise ApiError(message)
    try:
        return homework_statuses.json()
    except json.decoder.JSONDecodeError:
        message = 'JSON-format error!'
        logger.error(message)
        raise ValueError(message)


def check_response(response):
    """Checkout of API-response"""
    try:
        homeworks = response['homeworks']
    except KeyError:
        message = 'Key "homeworks" not found in response-data!'
        logger.error(message)
        raise KeyError(message)
    if not isinstance(response, dict):
        raise TypeError('Response-data is not dict!')
    if not isinstance(homeworks, list):
        message = '"Homeworks" is not list!'
        logger.error(message)
        raise TypeError(message)
    if len(homeworks) == 0:
        message = 'Task list is empty.'
        logger.error(message)
    return homeworks


def parse_status(homework):
    """Return status of this work from 
       the information about a particular homework."""
    if 'homework_name' not in homework:
        message = 'Key "homework_name" not found in response-dict!'
        logger.error(message)
        raise KeyError(message)
    if 'status' not in homework:
        message = 'Key "status" not found in response-dict!'
        logger.error(message)
        raise KeyError(message)
    homework_name = homework['homework_name']
    homework_status = homework['status']
    if homework_status not in HOMEWORK_VERDICTS:
        raise Exception(
            f'Value not found in list of homeworks verdicts: ',
            f'{homework_status}',
        )
    verdict = HOMEWORK_VERDICTS[homework_status]
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def main():
    """Basic logic of bot."""
    if not check_tokens():
        raise KeyError('Required environment variable is missing')

    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    current_timestamp = int(time.time())
    last_homework = 0

    while True:
        try:
            response = get_api_answer(current_timestamp)
            homework = check_response(response)
            if homework != last_homework:
                last_homework = homework
                message = parse_status(homework[0])
                send_message(bot, message)
            current_timestamp = response.get('current_date')
            print(message)
            time.sleep(RETRY_PERIOD)
        except Exception as error:
            message = f'Program has been terminated: {error}'
            send_message(bot, message)
            time.sleep(RETRY_PERIOD)


if __name__ == '__main__':
    main()
