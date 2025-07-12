def get_step(coord_1, coord_2):
    return -1 if coord_2 - coord_1 < 0 else 1


def get_moves(ants: list, map: dict) -> list:
    moves = list()
    for ant in ants:
        cur_ant = dict()
        cur_ant['ant'] = ant.id
        x, y = ant.get_useful_hex(map)
        cur_ant['path'] = ant.get_path(x, y, map)
        moves.append(cur_ant)
    return moves
