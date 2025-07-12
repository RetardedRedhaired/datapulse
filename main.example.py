import requests
import google.generativeai as genai
import os
import time
import json
import logging

# --- Конфигурация ---
API_TOKEN = os.getenv('DATSPULSE_API_TOKEN')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
BASE_URL = 'https://games-test.datsteam.dev'
LOG_FILE = 'bot_activity.log'

# --- Настройка логирования ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE, encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# --- Настройка клиентов ---

# Настройка клиента Gemini
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-2.5-flash')

# Настройка сессии для HTTP-запросов
session = requests.Session()
session.headers.update({'X-Auth-Token': API_TOKEN})

# --- Функции для взаимодействия с API игры ---

def get_game_state():
    """Получает текущее состояние арены, используя сессию."""
    try:
        response = session.get(f'{BASE_URL}/api/arena')
        response.raise_for_status()
        logger.info("Состояние игры успешно получено.")
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"Ошибка при получении состояния игры: {e}")
        return None

def send_moves(moves):
    """Отправляет команды на передвижение юнитов, используя сессию."""
    try:
        response = session.post(
            f'{BASE_URL}/api/move',
            json={"moves": moves}
        )
        response.raise_for_status()
        logger.info("Команды успешно отправлены.")
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"Ошибка при отправке команд: {e}")
        return None

def register_for_round():
    """Регистрируется на текущий раунд игры."""
    try:
        logger.info("Попытка регистрации на раунд...")
        response = session.post(f'{BASE_URL}/api/register')
        response.raise_for_status()
        registration_data = response.json()
        logger.info(f"Успешная регистрация на раунд: {registration_data.get('name')} (Лобби завершится через: {registration_data.get('lobbyEndsIn')} сек.)")
        return True
    except requests.exceptions.RequestException as e:
        logger.error(f"Ошибка при регистрации на раунд: {e}")
        logger.warning("Возможно, регистрация уже прошла или раунд неактивен.")
        return False

# --- Функции для взаимодействия с Gemini ---

def create_prompt_for_gemini(game_state):
    """Создает текстовый промпт для Gemini на основе состояния игры."""
    my_ants = game_state.get('ants', [])
    visible_enemies = game_state.get('enemies', [])
    visible_food = game_state.get('food', [])

    prompt = f"""
    Привет, Gemini. Ты — ИИ-стратег для игры DatsPulse. Проанализируй текущую ситуацию и предложи оптимальные действия для каждого моего муравья.

    **Цель игры:** Собрать как можно больше ресурсов с высокой калорийностью (нектар > хлеб > яблоко).
    **Правила:**
    - Рабочие (type 0) эффективны в сборе (грузоподъемность 8).
    - Бойцы (type 1) сильны в атаке (атака 70).
    - Разведчики (type 2) имеют лучший обзор (обзор 4).
    - Чтобы собрать ресурс, муравей должен закончить ход на гексе с ним.
    - Чтобы сдать ресурсы, нужно закончить ход на гексе своего муравейника.

    **Текущая ситуация (ход #{game_state.get('turnNo', 0)}):**
    - Мой счет: {game_state.get('score', 0)}
    - Мой муравейник находится в гексах: {json.dumps(game_state.get('home', []), indent=2)}
    - Главный гекс муравейника (где появляются юниты): {json.dumps(game_state.get('spot', {}), indent=2)}

    **Мои муравьи ({len(my_ants)}):**
    {json.dumps(my_ants, indent=2)}

    **Видимые враги ({len(visible_enemies)}):**
    {json.dumps(visible_enemies, indent=2)}

    **Видимые ресурсы ({len(visible_food)}):**
    {json.dumps(visible_food, indent=2)}

    **Твоя задача:**
    Для КАЖДОГО моего муравья (по его 'id') предложи путь ('path') для следующего хода.
    - Разведчиков (type 2) отправляй исследовать карту.
    - Рабочих (type 0) отправляй за ближайшими и самыми ценными ресурсами. Если рабочий несет ресурс, отправь его домой.
    - Бойцов (type 1) используй для защиты рабочих или атаки врагов.
    - Путь ('path') — это список координат `{{"q": x, "r": y}}`. Ты можешь указывать путь из нескольких шагов.
    - Если муравью лучше остаться на месте, верни для него пустой список path.

    **Ответ дай СТРОГО в формате JSON, без каких-либо пояснений или текста до/после JSON. Формат:**
    {{
      "moves": [
        {{
          "ant_id": "id-муравья-1",
          "path": [{{"q": x1, "r": y1}}, {{"q": x2, "r": y2}}]
        }},
        {{
          "ant_id": "id-муравья-2",
          "path": []
        }}
      ]
    }}
    """
    return prompt


def get_strategy_from_gemini(prompt):
    """Отправляет промпт в Gemini и получает стратегию и логирует время выполнения."""
    try:
        logger.info("Запрашиваю стратегию у Gemini...")
        start_time = time.time() # Записываем время до запроса
        response = model.generate_content(prompt)
        end_time = time.time() # Записываем время после получения ответа

        time_taken = end_time - start_time
        logger.info(f"Время, затраченное Gemini на размышление: {time_taken:.2f} секунд.")

        cleaned_response = response.text.strip().replace('```json', '').replace('```', '')
        logger.info(f"Ответ от Gemini получен:\n{cleaned_response}")
        return json.loads(cleaned_response)
    except Exception as e:
        logger.error(f"Ошибка при работе с Gemini API: {e}")
        return None


# --- Главный цикл игры ---

def main_loop():
    """Основной цикл, который управляет ботом."""
    # Попытка регистрации на раунд при запуске
    if not register_for_round():
        logger.critical("Не удалось зарегистрироваться на раунд. Бот не будет запущен.")
        return

    while True:
        game_state = get_game_state()

        if not game_state:
            logger.info("Не удалось получить состояние игры, ждем...")
            time.sleep(1)
            continue

        next_turn_in = game_state.get('nextTurnIn', 2.0)

        prompt = create_prompt_for_gemini(game_state)
        strategy = get_strategy_from_gemini(prompt)

        if strategy and 'moves' in strategy:
            moves_to_send = []
            for move in strategy['moves']:
                moves_to_send.append({
                    "ant": move['ant_id'],
                    "path": move['path']
                })
            send_moves(moves_to_send)

        wait_time = max(0, next_turn_in - 0.2)
        logger.info(f"Ход #{game_state.get('turnNo')}. Ждем {wait_time:.2f} секунд до следующего хода.")
        time.sleep(wait_time)


if __name__ == '__main__':
    if not API_TOKEN or not GEMINI_API_KEY:
        logger.critical("Ошибка: Установите переменные окружения DATSPULSE_API_TOKEN и GEMINI_API_KEY.")
    else:
        main_loop()