import json
from random import random, randint


from enums import HexType, ResourcesType, UnitType
from utils import get_step


class Position:
    """Позиция игрового объекта."""

    def __init__(self, q=None, r=None):
        self.q, self.r = q, r


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

    def get_useful_hex(self, map: dict = {}):
        """Возвращает координаты ближайшей полезной точки."""
        # пока возвращает рандомные координаты
        if self.food:
            return map['spot']
        return self.q + randint(-10, 10), self.r + randint(-10, 10)

    def get_path(self, x, y, map: dict = {}):
        """Возвращает список координат, описывающих путь до точки (x, y)."""
        path = list()
        cur_x, cur_y = self.q, self.r
        step_x, step_y = get_step(cur_x, x), get_step(cur_y, y)

        while ((cur_x, cur_y) != (x, y)):
            if cur_x != x and random() <= 0.5:
                cur_x += step_x
                path.append({'q': cur_x, 'r': cur_y})
            elif cur_y != y:
                cur_y += step_y
                path.append({'q': cur_x, 'r': cur_y})

        # # Добавить уменьшение self.op если Тип гекса - грязь
        # if map.get((cur_x, cur_y)) and map[(cur_x, cur_y)].type == HexType.swamp:
        #     self.op -= 1

        return path[:self.op]
