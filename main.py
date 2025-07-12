import os
import json
import requests
import time
import logging
import datetime

from dotenv import load_dotenv

from register import register
from load_content import load_data
from utils import get_moves


load_dotenv()
TOKEN = os.getenv('TOKEN')
URL_ARENA = os.getenv('URL_ARENA')
URL_MOVE = os.getenv('URL_MOVE')

headers = {
    'X-Auth-Token': TOKEN
}
session = requests.Session()
session.headers.update(headers)

def setup_logger():
    """
    Настраивает логгер для записи сообщений в файл с уникальным именем,
    включающим временную метку.
    """
    # Создаем имя файла лога с временной меткой
    # Формат: app_log_YYYY-MM-DD_HH-MM-SS.log
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    log_filename = f"app_log_{timestamp}.log"

    # Убедимся, что директория для логов существует (опционально)
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True) # Создаст директорию, если ее нет
    full_log_path = os.path.join(log_dir, log_filename)

    # 1. Получаем объект логгера
    logger = logging.getLogger('my_app')
    logger.setLevel(logging.DEBUG)  # Устанавливаем минимальный уровень для логгера

    # Проверяем, есть ли уже обработчики, чтобы избежать дублирования
    if not logger.handlers:
        # 2. Создаем обработчик для записи в файл
        file_handler = logging.FileHandler(full_log_path, encoding='utf-8')
        file_handler.setLevel(logging.INFO)  # Уровень для файла: INFO и выше

        # 3. Создаем форматтер
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        # 4. Привязываем форматтер к обработчику
        file_handler.setFormatter(formatter)

        # 5. Добавляем обработчик к логгеру
        logger.addHandler(file_handler)

        # (Опционально) Добавляем обработчик для вывода в консоль
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG) # Уровень для консоли: DEBUG и выше
        console_formatter = logging.Formatter('%(levelname)s: %(message)s')
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)

    return logger

def get_arena_data():
    try:
        response = session.get(url=URL_ARENA)
    except Exception as error:
        print(f'\nОШИБКА: {error}\n')
    else:
        return response.json()


def post_moves(moves):
    data = {'moves': moves}
    try:
        response = session.post(url=URL_MOVE, data=json.dumps(data))
    except Exception as error:
        print(f'\nОШИБКА: {error}\n')
    else:
        data = response.json()
        return data


def main(logger):
    current_turn = -1
    while True:
        data = get_arena_data()
        ants, enemies, food, home, map, turn_no, next_turn_in = load_data(data)

        if current_turn == turn_no:
            time.sleep(0.6)
            continue

        moves = get_moves(ants, map, food, enemies, logger, home)
        logger.info(moves)
        post_moves(moves)

        current_turn = turn_no

    # print(json.dumps(data, indent=2))


if __name__ == '__main__':
    app_logger = setup_logger()

    while register() >= 0:
        time.sleep(1)

    main(app_logger)

