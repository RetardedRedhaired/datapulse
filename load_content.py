from core import Ant, Enemy, Resource, Position, Hex


def load_ants(data: dict) -> list:
    ants = list()
    for ant in data.get('ants', {}):
        ants.append(Ant(**ant))
    return ants


def load_enemies(data: dict) -> list:
    enemies = list()
    for enemy in data.get('enemies', {}):
        enemies.append(Enemy(**enemy))
    return enemies


def load_food(data: dict) -> list:
    food = list()
    for resource in data.get('food', {}):
        food.append(Resource(**resource))
    return food


def load_home(data: dict) -> list:
    home = list()
    for pos in data.get('home', {}):
        home.append(Position(**pos))
    return home


def load_map(data: dict) -> dict:
    map = dict()
    for hex in data.get('map', {}):
        map[(hex['q'], hex['r'])] = (Hex(**hex))
    map['spot'] = Position(**data.get('spot', {}))
    return map


def load_data(data: dict) -> tuple:
    ants = load_ants(data)
    enemies = load_enemies(data)
    food = load_food(data)
    home = load_home(data)
    map = load_map(data)
    return ants, enemies, food, home, map


# ---------------- test ----------------
data = {
    "ants": [
        {
            "food": {
                "amount": 0,
                "type": 0
            },
            "health": 100,
            "id": "11111111-2222-3333-4444-555555555555",
            "lastAttack": {
                "q": 10,
                "r": 20
            },
            "lastEnemyAnt": "string",
            "lastMove": [
                {
                    "q": 10,
                    "r": 20
                }
            ],
            "move": [
                {
                    "q": 10,
                    "r": 20
                }
            ],
            "q": 0,
            "r": 0,
            "type": 0
        }
    ],
    "enemies": [
        {
            "attack": 0,
            "food": {
                "amount": 0,
                "type": 0
            },
            "health": 0,
            "q": 10,
            "r": 20,
            "type": 1
        }
    ],
    "food": [
        {
            "amount": 0,
            "q": 10,
            "r": 20,
            "type": 0
        }
    ],
    "home": [
        {
            "q": 10,
            "r": 20
        }
    ],
    "map": [
        {
            "cost": 1,
            "q": 10,
            "r": 20,
            "type": 0
        }
    ],
    "nextTurnIn": 0,
    "score": 0,
    "spot": {
        "q": 10,
        "r": 20
    },
    "turnNo": 0
}

ants, enemies, food, home, map = load_data(data)

print(ants[0].q, ants[0].r)
print(ants[0].get_path(3, 5, map))
