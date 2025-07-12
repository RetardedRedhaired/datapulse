import enum


class HexType(enum.IntEnum):
    """Типы гексов."""

    anthill = 1
    empty = 2
    swamp = 3
    acid = 4
    stone = 5


class ResourcesType(enum.IntEnum):
    """Типы ресурсов."""

    apple = 1
    bread = 2
    nectar = 3


class UnitType(enum.IntEnum):
    """Типы юнитов."""

    worker = 0
    warrior = 1
    scout = 2
