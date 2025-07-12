import os
import json
import requests
from dotenv import load_dotenv

from load_content import load_data
from utils import get_moves


load_dotenv()
TOKEN = os.getenv('TOKEN')
URL_ARENA = os.getenv('URL_ARENA')

headers = {
    'X-API-Key': TOKEN
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


def main():
    data = get_arena_data()
    ants, enemies, food, home, map = load_data(data)
    moves = get_moves(ants, map)

    # print(json.dumps(data, indent=4))


if __name__ == '__main__':
    main()
