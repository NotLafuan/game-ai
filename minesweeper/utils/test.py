import itertools
import numpy as np
import utilsModule

board = [[-1, -1, 1, 1, 0, 0, 0, 0, 1, 1, 2, -1, 1, 0, 0, 0],
         [-1, 3, 11, 1, 0, 0, 0, 0, 1, 11, 3, -1, 1, 0, 0, 0],
         [-1, 2, 2, 2, 1, 0, 1, 1, 3, 4, 11, 3, 2, 1, 1, 0],
         [-1, 1, 1, 11, 1, 0, 1, 11, 3, 11, 11, 2, 1, 11, 1, 0],
         [-1, 2, 2, 2, 1, 0, 1, 1, 3, 11, 3, 1, 1, 2, 2, 1],
         [-1, 2, 11, 1, 0, 0, 0, 1, 3, 3, 2, 0, 0, 1, 11, 2],
         [-1, 1, 1, 2, 1, 1, 0, 1, 11, 11, 1, 0, 0, 1, 2, 11],
         [-1, 1, 1, 2, 11, 2, 1, 2, 2, 2, 2, 1, 2, 1, 2, 1],
         [-1, 2, 11, 2, 1, 2, 11, 2, 2, 1, 2, 11, 3, 11, 2, 1],
         [-1, -1, 3, 2, 1, 2, 3, 11, 2, 11, 2, 2, 11, 3, 11, 2],
         [-1, -1, 11, 1, 1, 11, 2, 1, 2, 1, 1, 1, 1, 2, 2, 11],
         [-1, -1, 3, 1, 1, 1, 1, 0, 1, 1, 1, 0, 0, 0, 1, 1],
         [1, 1, 1, 0, 0, 1, 2, 2, 2, 11, 1, 0, 0, 0, 0, 0],
         [0, 0, 0, 1, 1, 2, 11, -1, -1, 1, 1, 0, 0, 0, 0, 0],
         [0, 0, 0, 1, -1, -1, -1, -1, -1, 1, 1, 1, 0, 0, 0, 0],
         [0, 0, 0, 1, -1, -1, -1, -1, -1, 1, 11, 1, 0, 0, 0, 0]]

guess_tiles = [(0, 0), (1, 0), (11, 0), (0, 1), (11, 1), (0, 2), (0, 3), (0, 4), (0, 5), (0, 6), (0, 7), (0, 8),
               (0, 9), (1, 9), (1, 10), (0, 11), (1, 11), (7, 13), (8, 13), (4, 14), (5, 14), (6, 14), (8, 14), (4, 15), (8, 15)]

number_tiles = [(2, 0), (3, 0), (8, 0), (9, 0), (10, 0), (12, 0), (1, 1), (3, 1), (8, 1), (10, 1), (12, 1), (1, 2), (2, 2), (3, 2), (4, 2), (6, 2), (7, 2), (8, 2), (9, 2), (11, 2), (12, 2), (13, 2), (14, 2), (1, 3), (2, 3), (4, 3), (6, 3), (8, 3), (11, 3), (12, 3), (14, 3), (1, 4), (2, 4), (3, 4), (4, 4), (6, 4), (7, 4), (8, 4), (10, 4), (11, 4), (12, 4), (13, 4), (14, 4), (15, 4), (1, 5), (3, 5), (7, 5), (8, 5), (9, 5), (10, 5), (13, 5), (15, 5), (1, 6), (2, 6), (3, 6), (4, 6), (5, 6), (7, 6), (10, 6), (13, 6), (14, 6), (1, 7), (2, 7), (3, 7), (5, 7), (6, 7), (7, 7), (8, 7), (9, 7), (10, 7),
                (11, 7), (12, 7), (13, 7), (14, 7), (15, 7), (1, 8), (3, 8), (4, 8), (5, 8), (7, 8), (8, 8), (9, 8), (10, 8), (12, 8), (14, 8), (15, 8), (2, 9), (3, 9), (4, 9), (5, 9), (6, 9), (8, 9), (10, 9), (11, 9), (13, 9), (15, 9), (3, 10), (4, 10), (6, 10), (7, 10), (8, 10), (9, 10), (10, 10), (11, 10), (12, 10), (13, 10), (14, 10), (2, 11), (3, 11), (4, 11), (5, 11), (6, 11), (8, 11), (9, 11), (10, 11), (14, 11), (15, 11), (0, 12), (1, 12), (2, 12), (5, 12), (6, 12), (7, 12), (8, 12), (10, 12), (3, 13), (4, 13), (5, 13), (9, 13), (10, 13), (3, 14), (9, 14), (10, 14), (11, 14), (3, 15), (9, 15), (11, 15)]


def surround_coords(x: int, y: int) -> list[tuple[int, int]]:
    lst = []
    for i, j in itertools.product([-1, 0, 1], repeat=2):
        lst.append((x+i, y+j))
    return lst


def test_bombs(bombs: list[int | None]) -> bool:
    for x, y in number_tiles:
        surround_bombs = []
        for coords in surround_coords(x, y):
            if coords in guess_tiles:
                index = guess_tiles.index(coords)
                surround_bombs.append(bombs[index])
            try:
                if coords[1] < 0 or coords[0] < 0:
                    continue
                if board[coords[1]][coords[0]] == 11:
                    surround_bombs.append(1)
            except IndexError:
                pass
        if (surround_bombs.count(1)) > board[y][x]:
            return False
        if (surround_bombs.count(None) + surround_bombs.count(1)) < board[y][x]:
            return False
    return True


def possible_bombs() -> np.ndarray:
    lst = []
    bombs = [None]*len(guess_tiles)
    used_bombs = [[] for _ in range(len(guess_tiles))]
    turn = 0
    while turn != -1:
        print(f"turn {turn} len_guess {len(guess_tiles)}")
        if turn == len(guess_tiles):  # index out for range
            turn -= 1  # go back one step
            used_bombs[turn] = []
            bombs[turn] = None
            turn -= 1  # go back one more step
        else:
            # check for unused number
            number_to_use = -1
            for choice in [0, 1]:
                if choice not in used_bombs[turn]:
                    number_to_use = choice
                    break
            # no other unused number
            if number_to_use < 0:
                used_bombs[turn] = []
                bombs[turn] = None
                turn -= 1  # go back one step
            # test the number
            else:
                bombs[turn] = number_to_use
                used_bombs[turn].append(number_to_use)
                if test_bombs(bombs):
                    turn += 1
                else:
                    bombs[turn] = None
        if None not in bombs and test_bombs(bombs):
            lst.append(bombs.copy())
        print(
            f"bomb_full {None not in bombs:1d} test_bombs {test_bombs(bombs):1d}")
    print('possibilities', len(lst))
    if not lst:
        raise IndexError
    for bombs in lst:
        for number in bombs:
            print(number, '', end='')
        print('bombs')
    return np.array(lst).mean(axis=0)


print(python_result := possible_bombs())
width = 16
height = 16
coords = surround_coords(2, 5)
for coord in coords:
    print(coord)
print(c_result := utilsModule._possible_bombs(
    width,  height, board,  guess_tiles,  number_tiles))

for py, c in zip(python_result, c_result):
    print(py, c)
