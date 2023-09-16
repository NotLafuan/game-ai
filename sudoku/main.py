import os
from time import sleep, time
import msvcrt


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

    def copy_board(self, board):
        for y in range(9):
            for x in range(9):
                self.board[y][x] = board[y][x]
        self.empty_poses = self.empty_poses_func()

    def empty_poses_func(self):
        poses = []
        for y, row in enumerate(self.board):
            for x, item in enumerate(row):
                if item == 0:
                    poses.append((x, y))
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
        return text

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


class AI():
    used_number = [[[] for _ in range(9)] for _ in range(9)]

    def solve(self, sudoku, print_progress=False, slowmode=False, slowmode_delay=0.1):
        turn = 0
        while turn < len(sudoku.empty_poses):
            x, y = sudoku.empty_poses[turn]
            sudoku.clear_slot(x, y)  # clear current slot
            if not sudoku.posibble_number(x, y):
                turn -= 1
                break
            # check for unused number
            number_to_use = 0
            for choice in sudoku.posibble_number(x, y):
                if choice not in self.used_number[y][x]:
                    number_to_use = choice
            # no other unused number
            if not number_to_use:
                self.used_number[y][x] = []
                sudoku.clear_slot(x, y)
                turn -= 1  # go back one step
            # test a number
            else:
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
        self.selected = [0, 0]

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
                if i == self.selected[0] and j == self.selected[1]:
                    text += '█ '
                else:
                    text += f'{item} ' if item > 0 else '  '
            text += '|\n'
        text += ' ' * space_width + ' -----------------------\n'
        text = text[:-1]
        text += '\n' * space_height
        return text

    def maker(self):
        while True:
            keypress = ord(msvcrt.getch()) if msvcrt.kbhit() else 0

            if not keypress:
                break
            # right
            if keypress == 100 or keypress == 77:
                self.selected[0] += 1
            # left
            if keypress == 97 or keypress == 75:
                self.selected[0] -= 1
            # up
            if keypress == 119 or keypress == 72:
                self.selected[1] -= 1
            # down
            if keypress == 115 or keypress == 80:
                self.selected[1] += 1

            # assigning the numbers
            if keypress >= 48 and keypress <= 57:
                # 0
                if keypress == 48:
                    self.board[self.selected[1]][self.selected[0]] = 0
                # 1
                if keypress == 49:
                    self.board[self.selected[1]][self.selected[0]] = 1
                # 2
                if keypress == 50:
                    self.board[self.selected[1]][self.selected[0]] = 2
                # 3
                if keypress == 51:
                    self.board[self.selected[1]][self.selected[0]] = 3
                # 4
                if keypress == 52:
                    self.board[self.selected[1]][self.selected[0]] = 4
                # 5
                if keypress == 53:
                    self.board[self.selected[1]][self.selected[0]] = 5
                # 6
                if keypress == 54:
                    self.board[self.selected[1]][self.selected[0]] = 6
                # 7
                if keypress == 55:
                    self.board[self.selected[1]][self.selected[0]] = 7
                # 8
                if keypress == 56:
                    self.board[self.selected[1]][self.selected[0]] = 8
                # 9
                if keypress == 57:
                    self.board[self.selected[1]][self.selected[0]] = 9
                self.selected[0] += 1
                if self.selected[0] > 8:
                    self.selected[0] = 0
                    self.selected[1] += 1

            # x looping
            self.selected[0] = 8 if self.selected[0] < 0 else self.selected[0]
            self.selected[0] = 0 if self.selected[0] > 8 else self.selected[0]
            # y looping
            self.selected[1] = 8 if self.selected[1] < 0 else self.selected[1]
            self.selected[1] = 0 if self.selected[1] > 8 else self.selected[1]

            # enter
            if keypress == 13:
                return self.board

            print(self.__str__(), end='')


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
