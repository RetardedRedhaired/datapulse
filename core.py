import json
from random import random, randint

from enums import HexType, ResourcesType, UnitType
from utils import get_step


class Position:
    """Позиция игрового объекта."""

    def __init__(self, q=None, r=None):
        self.q, self.r = q, r

    def __eq__(self, other):
        if isinstance(other, tuple):
            return other == self.q, self.r
        return NotImplemented


class Hex(Position):
    """Класс базовой ячейки карты."""

    def __init__(self, q=None, r=None, type=None, cost=None):
        super().__init__(q, r)
        self.type = type
        self.cost = cost


class Resource(Position):
    """Класс ресурса."""

    def __init__(self, q=None, r=None, amount=None, type=None):
        super().__init__(q, r)
        self.amount = amount
        self.type = type


class Unit:
    """Класс юнита."""

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


class Enemy(Unit):
    """Класс вражеского юнита."""


class Ant(Unit):
    """Класс муравья (дружественный юнит)."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.op = (5, 4, 7)[self.type]

    def get_useful_hex(self, map: dict = {}, food: list = [], enemies: list = []):
        """Возвращает координаты ближайшей полезной точки."""
        dest_hex = Position(self.q + randint(-100, 100),
                            self.r + randint(-100, 100))

        # 4 - кислота
        while map.get((dest_hex.q, dest_hex.r)) and map[(dest_hex.q, dest_hex.r)].type == 4:
            dest_hex = Position(self.q + randint(-100, 100),
                                self.r + randint(-100, 100))

        # Боец атакует врага, остальные берут еду и возвращаются
        if self.food['amount'] > 0:
            return map['spot']
        # if enemies and self.type == 1:  # боец
        #     return Position(enemies[0].q, enemies[0].r)
        if (self.q, self.r) == map['spot']:
            return dest_hex
        if food:
            return Position(food[0].q, food[0].r)
        return dest_hex

    def get_path(self, x, y, map):
        """Возвращает список координат, описывающих путь до точки (x, y)."""
        path = list()
        cur_x, cur_y = self.q, self.r
        step_x, step_y = get_step(cur_x, x), get_step(cur_y, y)

        while ((cur_x, cur_y) != (x, y)):

            if (map.get((cur_x+step_x, cur_y)) and map[(cur_x+step_x, cur_y)].type == 4
                    and map.get((cur_x, cur_y+step_y)) and map[(cur_x, cur_y+step_y)].type == 4):
                break

            if cur_x != x and random() <= 0.5:
                cur_x += step_x
                path.append({'q': cur_x, 'r': cur_y})
            elif cur_y != y:
                cur_y += step_y
                path.append({'q': cur_x, 'r': cur_y})

        return path[:self.op]
