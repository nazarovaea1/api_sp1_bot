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


def parse_homework_status(homework):
    homework_name = homework.get('homework_name')
    homework_status = homework.get('status')
    homework_statuses = {
        'approved': ('Ревьюеру всё понравилось, можно приступать к следующему '
                     'уроку.'),
        'rejected': 'К сожалению в работе нашлись ошибки.',
    }

    if homework_status not in homework_statuses:
        return 'Статус неизвестен'
    verdict = homework_statuses[homework_status]
    return f'У вас проверили работу "{homework_name}"!\n\n{verdict}'


def get_homework_statuses(current_timestamp):
    prak_homework_api = ('https://praktikum.yandex.ru/api/user_api/'
                         'homework_statuses/')
    homework_statuses = requests.get(
        prak_homework_api,
        headers={'Authorization': f'OAuth {PRAKTIKUM_TOKEN}'},
        params={'from_date': current_timestamp, })
    return homework_statuses.json()
    try:
        homework_statuses.raise_for_status()
    except requests.exceptions.HTTPError as err:
        raise SystemExit(err)


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
            if new_homework.get('homeworks'):
                if (len(new_homework.get('homeworks')[0]) > 0 and
                    new_homework.get('homeworks')[0] is not None):
                    send_message(parse_homework_status(
                        new_homework.get('homeworks')[0]), bot_client)
                else:
                    send_message('Домашек для проверки нет', bot_client)
            current_timestamp = new_homework.get(
                'current_date', current_timestamp)
            time.sleep(300)

        except Exception as e:
            time.sleep(5)
            logging.error(f'Бот столкнулся с ошибкой: {e}')


if __name__ == '__main__':
    main()
