import os
import json
import requests
import time
from dotenv import load_dotenv

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


def main():
    data = get_arena_data()
    ants, enemies, food, home, map = load_data(data)
    moves = get_moves(ants, map, food, enemies)
    post_moves(moves)

    print(json.dumps(data, indent=2))


if __name__ == '__main__':
    while True:
        main()
        time.sleep(1)

