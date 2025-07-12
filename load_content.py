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
