import logging
import os
import time

import requests
from dotenv import load_dotenv
from telegram import Bot

logging.basicConfig(
    level=logging.DEBUG,
    filename='main.log',
    format='%(asctime)s, %(levelname)s, %(name)s, %(message)s'
)

load_dotenv()


PRAKTIKUM_TOKEN = os.getenv('PRAKTIKUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
HOMEWORK_STATUS = {
    'approved': ('Ревьюеру всё понравилось, можно приступать к следующему '
                 'уроку.'),
    'rejected': 'К сожалению в работе нашлись ошибки.',
}
PRAK_HOMEWORK_API = ('https://praktikum.yandex.ru/api/user_api/'
                     'homework_statuses/')


def parse_homework_status(homework):
    homework_name = homework.get('homework_name')
    homework_status = homework.get('status')
    if homework_status not in HOMEWORK_STATUS:
        return 'Статус неизвестен'
    verdict = HOMEWORK_STATUS[homework_status]
    return f'У вас проверили работу "{homework_name}"!\n\n{verdict}'


def get_homework_statuses(current_timestamp):
    try:
        homework_statuses = requests.get(
            PRAK_HOMEWORK_API,
            headers={'Authorization': f'OAuth {PRAKTIKUM_TOKEN}'},
            params={'from_date': current_timestamp, })
        return homework_statuses.json()
    except requests.exceptions.RequestException:
        return {}


def send_message(message, bot_client):
    return bot_client.send_message(chat_id=CHAT_ID, text=message)
    logging.info('Сообщение отправлено')


def main():
    bot_client = Bot(token=TELEGRAM_TOKEN)
    logging.debug('Бот запущен')
    while True:
        try:
            current_timestamp = int(time.time())
            new_homework = get_homework_statuses(current_timestamp)
            hw = new_homework.get('homeworks', {})
            if new_homework.get('homeworks'):
                if (len(hw)[0]) > 0:
                    send_message(parse_homework_status(hw[0]), bot_client)
                else:
                    send_message('Домашек для проверки нет', bot_client)
            current_timestamp = new_homework.get(
                'current_date', current_timestamp)
            time.sleep(10)

        except Exception as e:
            time.sleep(300)
            logging.error(f'Бот столкнулся с ошибкой: {e}')


if __name__ == '__main__':
    main()
