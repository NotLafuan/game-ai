import os
import msvcrt
from enum import IntEnum
from dataclasses import dataclass
from time import sleep, time
from typing import Any
import colorama

colorama.init()


@dataclass
class Point:
    x: int
    y: int
    __slots__ = ['x', 'y', 'index']

    def __iter__(self):
        self.index = 0
        return self

    def __next__(self):
        if self.index == 2:
            raise StopIteration
        if self.index == 0:
            self.index += 1
            return self.x
        if self.index == 1:
            self.index += 1
            return self.y


class Key(IntEnum):
    ESC = 27
    X_BUTTON = 255
    SPACE = 32
    ENTER = 13
    NUMBER_0 = 48
    NUMBER_1 = 49
    NUMBER_2 = 50
    NUMBER_3 = 51
    NUMBER_4 = 52
    NUMBER_5 = 53
    NUMBER_6 = 54
    NUMBER_7 = 55
    NUMBER_8 = 56
    NUMBER_9 = 57
    A = 97
    B = 98
    C = 99
    D = 100
    E = 101
    F = 102
    G = 103
    H = 104
    I = 105
    J = 106
    K = 107
    L = 108
    M = 109
    N = 110
    O = 111
    P = 112
    Q = 113
    R = 114
    S = 115
    T = 116
    U = 117
    V = 118
    W = 119
    X = 120
    Y = 121
    Z = 122
    A_CAPS = 65
    B_CAPS = 66
    C_CAPS = 67
    D_CAPS = 68
    E_CAPS = 69
    F_CAPS = 70
    G_CAPS = 71
    H_CAPS = 72
    I_CAPS = 73
    J_CAPS = 74
    K_CAPS = 75
    L_CAPS = 76
    M_CAPS = 77
    N_CAPS = 78
    O_CAPS = 79
    P_CAPS = 80
    Q_CAPS = 81
    R_CAPS = 82
    S_CAPS = 83
    T_CAPS = 84
    U_CAPS = 85
    V_CAPS = 86
    W_CAPS = 87
    X_CAPS = 88
    Y_CAPS = 89
    Z_CAPS = 90


@dataclass
class Sudoku():
    board = [
        [0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0]
    ]

    def __init__(self):
        self.empty_poses = self.empty_poses_func()

    def copy_board(self, board: list[list[int]]):
        for y in range(9):
            for x in range(9):
                self.board[y][x] = board[y][x]
        self.empty_poses = self.empty_poses_func()

    def empty_poses_func(self) -> list[Point]:
        poses = []
        for y, row in enumerate(self.board):
            for x, item in enumerate(row):
                if item == 0:
                    poses.append(Point(x, y))
        return poses

    def __str__(self):
        # center on screen 25x13
        width, height = os.get_terminal_size()
        space_height = (height - 13) // 2
        space_width = (width - 25) // 2
        # making board text
        text = '\n' * space_height
        for j, row in enumerate(self.board):
            text += ' ' * space_width
            if j % 3 == 0:
                text += ' -----------------------\n' + ' ' * space_width
            for i, item in enumerate(row):
                if i % 3 == 0:
                    text += '| '
                text += f'{item} ' if item > 0 else '  '
            text += '|\n'
        text += ' ' * space_width + ' -----------------------\n'
        text = text[:-1]
        text += '\n' * space_height
        cursor = '\033[A' * text.count('\n')
        return cursor + text

    def posibble_number(self, x: int, y: int):
        if self.board[y][x] != 0:
            return 0

        number_found = []
        for row in self.board:
            if row[x] != 0:
                if row[x] not in number_found:
                    number_found.append(row[x])
        for item in self.board[y]:
            if item != 0:
                if item not in number_found:
                    number_found.append(item)

        x_lower = (x//3) * 3
        x_upper = ((x//3) * 3) + 3
        y_lower = (y//3) * 3
        y_upper = ((y//3) * 3) + 3

        for row in self.board[y_lower:y_upper]:
            for item in row[x_lower:x_upper]:
                if item not in number_found:
                    number_found.append(item)

        all_number = [1, 2, 3, 4, 5, 6, 7, 8, 9]
        return [number for number in all_number if number not in number_found]

    def insert_number(self, x: int, y: int, number: int):
        self.board[y][x] = number

    def clear_slot(self, x: int, y: int):
        self.board[y][x] = 0


@dataclass
class AI():
    used_number = [[[] for _ in range(9)] for _ in range(9)]

    def solve(self, sudoku: Sudoku, print_progress=False, slowmode=False, slowmode_delay=0.1):
        turn = 0
        while turn < len(sudoku.empty_poses):
            x, y = sudoku.empty_poses[turn]
            sudoku.clear_slot(x, y)  # clear current slot
            if not sudoku.posibble_number(x, y):
                turn -= 1
                continue
            # check for unused number
            number_to_use = 0
            for choice in sudoku.posibble_number(x, y):
                if choice not in self.used_number[y][x]:
                    number_to_use = choice
            # no other unused number
            if not number_to_use:
                self.used_number[y][x] = []
                sudoku.clear_slot(x, y)
                turn -= 1
            else:
                a = self.used_number[y][x]
                sudoku.insert_number(x, y, number_to_use)
                self.used_number[y][x].append(number_to_use)
                turn += 1

            if print_progress:
                print(sudoku, end='')
                if slowmode:
                    sleep(slowmode_delay)


class BoardMaker():
    def __init__(self):
        self.board = [[0 for _ in range(9)] for _ in range(9)]
        self.selected = Point(0, 0)

    def __str__(self):
        # center on screen 25x13
        width, height = os.get_terminal_size()
        space_height = (height - 13) // 2
        space_width = (width - 25) // 2
        # making board text
        text = '\n' * space_height
        for j, row in enumerate(self.board):
            text += ' ' * space_width
            if j % 3 == 0:
                text += ' -----------------------\n' + ' ' * space_width
            for i, item in enumerate(row):
                if i % 3 == 0:
                    text += '| '
                if i == self.selected.x and j == self.selected.y:
                    text += '█ '
                else:
                    text += f'{item} ' if item > 0 else '  '
            text += '|\n'
        text += ' ' * space_width + ' -----------------------\n'
        text = text[:-1]
        text += '\n' * space_height
        cursor = '\033[A' * text.count('\n')
        return cursor + text

    def maker(self):
        while True:
            keypress = ord(msvcrt.getch()) if msvcrt.kbhit() else 0
            while not keypress:
                keypress = ord(msvcrt.getch()) if msvcrt.kbhit() else 0
                continue

            match keypress:
                case Key.W:
                    self.selected.y -= 1
                case Key.A:
                    self.selected.x -= 1
                case Key.S:
                    self.selected.y += 1
                case Key.D:
                    self.selected.x += 1
                case Key.ENTER:
                    return self.board
                case other:
                    number = other - Key.NUMBER_0
                    if number < 0 or number > 9:
                        continue
                    self.board[self.selected.y][self.selected.x] = number
                    self.selected.x += 1
                    if self.selected.x > 8:
                        self.selected.x = 0
                        self.selected.y += 1

            # x looping
            self.selected.x = 8 if self.selected.x < 0 else self.selected.x
            self.selected.x = 0 if self.selected.x > 8 else self.selected.x
            # y looping
            self.selected.y = 8 if self.selected.y < 0 else self.selected.y
            self.selected.y = 0 if self.selected.y > 8 else self.selected.y

            print(self, end='')


if __name__ == '__main__':
    sudoku = Sudoku()
    ai = AI()
    boardMaker = BoardMaker()

    print(boardMaker, end='')
    board = boardMaker.maker()
    sudoku.copy_board(board)

    print(sudoku, end='')
    # os.system('pause')
    start_time = time()

    ai.solve(sudoku)
    # ai.solve(sudoku, print_progress=True)
    # ai.solve(sudoku, print_progress=True, slowmode=True)

    print(sudoku, end='')
    elapsed = time() - start_time
    print(f'Time taken: {elapsed} s')
    os.system('pause')
