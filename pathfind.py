import heapq
import logging
from typing import List, Tuple, Set, Optional, Dict, Any
from random import random
from enums import HexType

class PathFinder:
    def __init__(self, q: int, r: int, op: int):
        """
        Инициализация pathfinder для юнита

        Args:
            q: координата q юнита
            r: координата r юнита
            op: очки передвижения юнита
        """
        self.q = q
        self.r = r
        self.op = op

    def get_step(self, current: int, target: int) -> int:
        """Определяет направление шага"""
        if current < target:
            return 1
        elif current > target:
            return -1
        else:
            return 0

    def get_hex_movement_cost(self, hex_type: int) -> int:
        """Возвращает стоимость передвижения по гексу в зависимости от типа"""
        cost_map = {
            HexType.anthill: 1,  # муравейник
            HexType.empty: 1,  # Лес
            HexType.swamp: 2,  # Вода
            HexType.stone: 999,  # Камень - непроходимый
            HexType.acid: 1  # Кислота - низкая стоимость, но опасная
        }
        return cost_map.get(hex_type, 1)

    def is_hex_passable(self, hex_type: int) -> bool:
        """Проверяет, можно ли пройти через гекс"""
        return hex_type != 5  # Камень непроходим

    def is_hex_dangerous(self, hex_type: int) -> bool:
        """Проверяет, опасен ли гекс"""
        return hex_type == 4  # Кислота опасна

    def get_neighbors(self, q: int, r: int) -> List[Tuple[int, int]]:
        """Получает соседние координаты для кубических координат гексов"""
        # Кубические координаты гексов - 6 направлений
        directions = [
            (1, 0),  # Восток
            (1, -1),  # Северо-восток
            (0, -1),  # Северо-запад
            (-1, 0),  # Запад
            (-1, 1),  # Юго-запад
            (0, 1)  # Юго-восток
        ]

        neighbors = []
        for dq, dr in directions:
            neighbors.append((q + dq, r + dr))

        return neighbors

    def heuristic(self, q1: int, r1: int, q2: int, r2: int) -> int:
        """Эвристическая функция для кубических координат гексов"""
        # Манхэттенское расстояние в кубических координатах
        return (abs(q1 - q2) + abs(q1 + r1 - q2 - r2) + abs(r1 - r2)) // 2

    def can_occupy_hex(self, q: int, r: int, game_map: Dict[Tuple[int, int], Any],
                       moving_unit_type: str, player_id: int) -> bool:
        # """
        # Проверяет, может ли юнит занять гекс с учетом ограничений
        #
        # Args:
        #     q, r: координаты гекса
        #     game_map: карта игры
        #     moving_unit_type: тип перемещающегося юнита
        #     player_id: ID игрока
        # """
        hex_key = (q, r)

        # Проверяем существование гекса
        if hex_key not in game_map:
            return False

        hex_obj = game_map[hex_key]
        #
        # Проверяем проходимость
        if not self.is_hex_passable(hex_obj.type):
            return False
        #
        # # Проверяем наличие юнитов (эта логика зависит от структуры ваших данных)
        # # Предполагаем, что у hex_obj есть поле unit или подобное
        # if hasattr(hex_obj, 'unit') and hex_obj.unit is not None:
        #     other_unit = hex_obj.unit
        #
        #     # Нельзя зайти на гекс с чужим юнитом
        #     if hasattr(other_unit, 'player_id') and other_unit.player_id != player_id:
        #         return False
        #
        #     # Нельзя зайти на гекс с дружественным юнитом того же типа
        #     if (hasattr(other_unit, 'player_id') and other_unit.player_id == player_id and
        #             hasattr(other_unit, 'type') and other_unit.type == moving_unit_type):
        #         return False

        return True

    def find_path_astar(self, target_q: int, target_r: int, game_map: Dict[Tuple[int, int], Any],
                        moving_unit_type: str = "default", player_id: int = 1,
                        avoid_dangerous: bool = True) -> List[Dict[str, int]]:
        """
        Находит оптимальный путь используя алгоритм A*

        Args:
            target_q, target_r: целевые координаты
            game_map: карта игры
            moving_unit_type: тип перемещающегося юнита
            player_id: ID игрока
            avoid_dangerous: избегать ли опасные гексы

        Returns:
            Список координат пути в формате [{'q': x, 'r': y}, ...]
        """
        start = (self.q, self.r)
        goal = (target_q, target_r)

        if start == goal:
            return []

        # Проверяем, можем ли мы достичь цели
        if not self.can_occupy_hex(target_q, target_r, game_map, moving_unit_type, player_id):
            return []

        # Очередь с приоритетом для A*
        open_set = []
        heapq.heappush(open_set, (0, start))

        # Словари для отслеживания пути и стоимости
        came_from = {}
        g_score = {start: 0}
        f_score = {start: self.heuristic(self.q, self.r, target_q, target_r)}

        # Множество посещенных узлов
        closed_set = set()

        while open_set:
            current_f, current = heapq.heappop(open_set)

            if current in closed_set:
                continue

            closed_set.add(current)

            # Достигли цели
            if current == goal:
                path = []
                while current in came_from:
                    path.append(current)
                    current = came_from[current]
                path.reverse()

                # Преобразуем в нужный формат
                result = []
                for q, r in path:
                    result.append({'q': q, 'r': r})

                # Ограничиваем путь очками передвижения
                return self.limit_path_by_movement_points(result, game_map)

            # Проверяем соседей
            for neighbor_q, neighbor_r in self.get_neighbors(*current):
                neighbor = (neighbor_q, neighbor_r)

                if neighbor in closed_set:
                    continue

                if not self.can_occupy_hex(neighbor_q, neighbor_r, game_map,
                                           moving_unit_type, player_id):
                    continue

                # Получаем стоимость движения
                hex_obj = game_map.get(neighbor)
                if hex_obj is None:
                    continue

                movement_cost = self.get_hex_movement_cost(hex_obj.type)

                # Добавляем штраф за опасные гексы
                if avoid_dangerous and self.is_hex_dangerous(hex_obj.type):
                    movement_cost += 50

                tentative_g_score = g_score[current] + movement_cost

                if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g_score
                    f_score[neighbor] = tentative_g_score + self.heuristic(neighbor_q, neighbor_r, target_q, target_r)
                    heapq.heappush(open_set, (f_score[neighbor], neighbor))

        return []  # Путь не найден

    def limit_path_by_movement_points(self, path: List[Dict[str, int]],
                                      game_map: Dict[Tuple[int, int], Any]) -> List[Dict[str, int]]:
        """Ограничивает путь доступными очками передвижения"""
        if not path:
            return path

        available_points = self.op
        limited_path = []

        for step in path:
            hex_key = (step['q'], step['r'])
            if hex_key in game_map:
                hex_obj = game_map[hex_key]
                cost = self.get_hex_movement_cost(hex_obj.type)

                if available_points >= cost:
                    limited_path.append(step)
                    available_points -= cost
                else:
                    break

        return limited_path

    def get_path(self, x: int, y: int, game_map: Dict[Tuple[int, int], Any],
                 moving_unit_type: str = "default", player_id: int = 1,
                 use_astar: bool = True,
                 logger: logging.Logger = None) -> List[Dict[str, int]]:
        """
        Основная функция поиска пути (совместимая с вашим API)

        Args:
            x, y: целевые координаты (target_q, target_r)
            game_map: карта игры
            moving_unit_type: тип перемещающегося юнита
            player_id: ID игрока
            use_astar: использовать ли A* или оригинальный алгоритм

        Returns:
            Список координат пути в формате [{'q': x, 'r': y}, ...]
        """
        if use_astar:
            return self.find_path_astar(x, y, game_map, moving_unit_type, player_id)
        else:
            dist = self.get_path_original(x, y, game_map)
            return dist

    def get_path_original(self, x: int, y: int, game_map: Dict[Tuple[int, int], Any]) -> List[Dict[str, int]]:
        """
        Улучшенная версия вашего оригинального алгоритма
        """
        path = []
        cur_x, cur_y = self.q, self.r
        step_x, step_y = self.get_step(cur_x, x), self.get_step(cur_y, y)

        while (cur_x, cur_y) != (x, y):
            # Проверяем, не заблокированы ли оба направления камнем
            next_x_blocked = False
            next_y_blocked = False

            if cur_x != x:
                next_x_pos = (cur_x + step_x, cur_y)
                if (next_x_pos in game_map and
                        not self.is_hex_passable(game_map[next_x_pos].type)):
                    next_x_blocked = True

            if cur_y != y:
                next_y_pos = (cur_x, cur_y + step_y)
                if (next_y_pos in game_map and
                        not self.is_hex_passable(game_map[next_y_pos].type)):
                    next_y_blocked = True

            # Если оба направления заблокированы, прекращаем поиск
            if next_x_blocked and next_y_blocked:
                break

            # Выбираем направление движения
            if cur_x != x and not next_x_blocked and (next_y_blocked or random() <= 0.5):
                cur_x += step_x
                path.append({'q': cur_x, 'r': cur_y})
            elif cur_y != y and not next_y_blocked:
                cur_y += step_y
                path.append({'q': cur_x, 'r': cur_y})
            else:
                # Если не можем двигаться, прекращаем
                break

        # Ограничиваем путь очками передвижения
        return self.limit_path_by_movement_points(path, game_map)

    def find_best_accessible_position(self, target_q: int, target_r: int,
                                      game_map: Dict[Tuple[int, int], Any],
                                      moving_unit_type: str = "default",
                                      player_id: int = 1) -> Optional[Tuple[int, int]]:
        """
        Находит лучшую доступную позицию, если прямой путь к цели невозможен

        Returns:
            Кортеж (q, r) лучшей позиции или None
        """
        visited = set()
        queue = [(self.q, self.r, 0)]  # (q, r, cost)
        best_position = None
        min_distance = float('inf')

        while queue:
            current_q, current_r, current_cost = queue.pop(0)

            if (current_q, current_r) in visited:
                continue

            visited.add((current_q, current_r))

            # Проверяем, лучше ли эта позиция
            distance = self.heuristic(current_q, current_r, target_q, target_r)
            if distance < min_distance and (current_q, current_r) != (self.q, self.r):
                min_distance = distance
                best_position = (current_q, current_r)

            # Добавляем соседей в очередь
            for neighbor_q, neighbor_r in self.get_neighbors(current_q, current_r):
                if (neighbor_q, neighbor_r) in visited:
                    continue

                hex_key = (neighbor_q, neighbor_r)
                if hex_key not in game_map:
                    continue

                if not self.can_occupy_hex(neighbor_q, neighbor_r, game_map,
                                           moving_unit_type, player_id):
                    continue

                hex_obj = game_map[hex_key]
                move_cost = self.get_hex_movement_cost(hex_obj.type)
                new_cost = current_cost + move_cost

                if new_cost <= self.op:
                    queue.append((neighbor_q, neighbor_r, new_cost))

        return best_position


# Пример использования
# def example_usage():
#     """Пример использования улучшенного pathfinder"""
#
#     # Создаем mock объект для гекса
#     class MockHex:
#         def __init__(self, q, r, hex_type):
#             self.q = q
#             self.r = r
#             self.type = hex_type
#             self.unit = None
#
#     # Создаем карту
#     game_map = {}
#     for q in range(-5, 6):
#         for r in range(-5, 6):
#             if abs(q + r) <= 5:  # Ограничиваем размер гексагональной карты
#                 hex_type = 0  # Обычный гекс
#
#                 # Добавляем препятствия
#                 if q == 0 and r == 0:
#                     hex_type = 5  # Камень
#                 elif q == 2 and r == -1:
#                     hex_type = 6  # Кислота
#                 elif abs(q) == 3:
#                     hex_type = 1  # Лес
#
#                 game_map[(q, r)] = MockHex(q, r, hex_type)
#
#     # Создаем pathfinder
#     pathfinder = PathFinder(q=-3, r=2, op=10)
#
#     # Ищем путь с помощью A*
#     path = pathfinder.get_path(3, -2, game_map, use_astar=True)
#
#     print("Путь найден с помощью A*:")
#     for step in path:
#         print(f"  q={step['q']}, r={step['r']}")
#
#     # Ищем путь с помощью оригинального алгоритма
#     path_original = pathfinder.get_path(3, -2, game_map, use_astar=False)
#
#     print("\nПуть найден с помощью оригинального алгоритма:")
#     for step in path_original:
#         print(f"  q={step['q']}, r={step['r']}")
