import sys
import os
import time
import logging
import http
import json

import requests
import telegram
from dotenv import load_dotenv

import exceptions

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


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
formating = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

file_handler = logging.FileHandler('homeworks.log')
file_handler.setFormatter(formating)
logger.addHandler(file_handler)

consol_handler = logging.StreamHandler(sys.stdout)
consol_handler.setFormatter(formating)
logger.addHandler(consol_handler)


def check_tokens() -> bool:
    """Tokens checkout."""
    return all((PRACTICUM_TOKEN, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID))


def send_message(bot: telegram.Bot, message: str) -> None:
    """Bot sends a messsage."""
    try:
        bot.send_message(TELEGRAM_CHAT_ID, message)
        logging.debug('Message was sent successfully')
    except telegram.TelegramError as error:
        logger.error(f'Message has not been sent: {error}')


def get_api_answer(current_timestamp: int) -> dict:
    """Get of API-Data."""
    timestamp = current_timestamp or int(time.time())
    params = {'from_date': timestamp}
    try:
        homework_statuses = requests.get(
            ENDPOINT,
            headers=HEADERS,
            params=params,
        )
    except requests.RequestException:
        message = 'Request not sent!'
        logger.error(message)
        raise exceptions.RequestError(message)
    if homework_statuses.status_code != http.HTTPStatus.OK:
        message = 'Response code is not 200!'
        logger.error(message)
        raise exceptions.ApiError(message)
    try:
        return homework_statuses.json()
    except json.decoder.JSONDecodeError:
        message = 'JSON-format error!'
        logger.error(message)
        raise ValueError(message)


def check_response(response: dict) -> dict:
    """Checkout of API-response."""
    if not isinstance(response, dict):
        raise TypeError('Response-data is not dict!')
    try:
        homeworks = response['homeworks']
    except KeyError:
        message = 'Key "homeworks" not found in response-data!'
        logger.error(message)
        raise KeyError(message)
    if not isinstance(homeworks, list):
        message = '"Homeworks" is not list!'
        logger.error(message)
        raise TypeError(message)
    if not homeworks:
        message = 'Task list is empty.'
        logger.error(message)
    return homeworks


def parse_status(homework: dict) -> str:
    """Return status of homework."""
    homework_name = homework.get('homework_name')
    homework_status = homework.get('status')
    if not all((homework_name, homework_status)):
        logger.error(
            'Expected keys not found in response-dict!',
        )
        raise KeyError(
            'Expected keys not found in response-dict!',
        )
    verdict = HOMEWORK_VERDICTS.get(homework_status)
    if not verdict:
        raise ValueError(
            'Value not found in list of homeworks verdicts: ',
            f'{homework_status}',
        )
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def main() -> None:
    """Basic logic of bot."""
    if not check_tokens():
        logger.critical('Tokens not found!')
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
            time.sleep(RETRY_PERIOD)
        except(
            TypeError,
            KeyError,
            ValueError,
            telegram.TelegramError,
            exceptions.RequestError,
            exceptions.ApiError,
            json.decoder.JSONDecodeError,
        ) as error:
            message = f'Program has been terminated: {error}'
            send_message(bot, message)
        finally:
            time.sleep(RETRY_PERIOD)


if __name__ == '__main__':
    main()
