import os
import requests
from dotenv import load_dotenv


load_dotenv()
TOKEN = os.getenv('TOKEN')
URL_REGISTER = os.getenv('URL_REGISTER')

headers = {
    'X-Auth-Token': TOKEN
}
session = requests.Session()
session.headers.update(headers)


def register():
    try:
        response = session.post(url=URL_REGISTER)
    except Exception as error:
        print(f'\nОШИБКА: {error}\n')
    else:
        data = response.json()
        print(data)
        return data.get('lobbyEndsIn', 0)


if __name__ == '__main__':
    register()
