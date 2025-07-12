import os
import json
import requests
from dotenv import load_dotenv


load_dotenv()
TOKEN = os.getenv('TOKEN')
URL_REGISTER = os.getenv('URL_REGISTER')

headers = {
    'X-API-Key': TOKEN
}
session = requests.Session()
session.headers.update(headers)


def main():
    try:
        response = session.post(url=URL_REGISTER)
    except Exception as error:
        print(f'\nОШИБКА: {error}\n')
    else:
        data = response.json()
        print(data)
        return data


if __name__ == '__main__':
    main()
