import os
import time

import requests
import telegram
from telegram import Bot
from datetime import datetime, timedelta
import logging

from dotenv import load_dotenv

logging.basicConfig(
    level=logging.DEBUG,
    filename='main.log', 
    format='%(asctime)s, %(levelname)s, %(name)s, %(message)s'
)

load_dotenv()


PRAKTIKUM_TOKEN = os.getenv("PRAKTIKUM_TOKEN")
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
from_date = time.time()


def parse_homework_status(homework):
    homework_name = homework['homework_name']
    homework_status = homework['status']
    print(homework_name)
    if homework_status == 'rejected':
        verdict = 'К сожалению в работе нашлись ошибки.'
    else:
        verdict = 'Ревьюеру всё понравилось, можно приступать к следующему уроку.'
    return f'У вас проверили работу "{homework_name}"!\n\n{verdict}'


def get_homework_statuses(current_timestamp):
    
    from_date = current_timestamp
    homework_statuses = requests.get('https://praktikum.yandex.ru/api/user_api/homework_statuses/',
                        headers={'Authorization': f'OAuth {PRAKTIKUM_TOKEN}'},
                        params={'from_date': from_date,})
    return homework_statuses.json()


def send_message(message, bot_client):
    return bot_client.send_message(chat_id=CHAT_ID, text=message)
    logging.info('Сообщение отправлено')


def main():
    # проинициализировать бота здесь
    now_date = datetime.now()
    ten_days_before = now_date - timedelta(days = 10)
    ten_days_before_tmstmp = ten_days_before.timestamp()
    bot_client = Bot(token=TELEGRAM_TOKEN)
    #current_timestamp = int(time.time()) # начальное значение timestamp
    current_timestamp = int(ten_days_before_tmstmp)
    logging.debug('Бот запущен')

    while True:
        try:
            new_homework = get_homework_statuses(current_timestamp)
            if new_homework.get('homeworks'):
                send_message(parse_homework_status(new_homework.get('homeworks')[0]), bot_client)
            current_timestamp = new_homework.get('current_date', current_timestamp)  # обновить timestamp
            time.sleep(300)  # опрашивать раз в пять минут

        except Exception as e:
            print(f'Бот столкнулся с ошибкой: {e}')
            time.sleep(5)
            logging.error(f'Бот столкнулся с ошибкой: {e}')


if __name__ == '__main__':
    main()
