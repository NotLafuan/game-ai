import itertools
import time
import pyautogui
import ctypes
import cv2
import numpy as np
import os


def GetWindowRectFromName(name: str) -> tuple:
    hwnd = ctypes.windll.user32.FindWindowW(0, name)
    rect = ctypes.wintypes.RECT()
    ctypes.windll.user32.GetWindowRect(hwnd, ctypes.pointer(rect))
    return rect


class Reader:
    def __init__(self, width: int = 9, height: int = 9) -> None:
        self.width = width
        self.height = height
        self.templates: list[cv2.Mat] = [cv2.imread(os.path.join('tiles', file))
                                         for file in os.listdir('tiles')]

    @property
    def tile_images(self) -> list[list[cv2.Mat]]:
        rect = GetWindowRectFromName('Minesweeper')
        img = pyautogui.screenshot()
        img = np.array(img)
        img = img[:, :, ::-1].copy()  # RGB2BGR
        window = img[rect.top:rect.bottom, rect.left:rect.right]

        tiles = []
        x, y = 23, 152
        for j in range(self.height):
            row = []
            for i in range(self.width):
                row.append(window[y+(j*24):y+(j*24)+24, x+(i*24):x+(i*24)+24])
            tiles.append(row)
        return tiles

    def mse(self, imageA, imageB) -> float:
        # the 'Mean Squared Error' between the two images is the
        # sum of the squared difference between the two images;
        # NOTE: the two images must have the same dimension
        err = np.sum((imageA.astype('float') - imageB.astype('float')) ** 2)
        err /= float(imageA.shape[0] * imageA.shape[1])

        # return the MSE, the lower the error, the more "similar"
        # the two images are
        return err

    def compare_tile(self, tile: cv2.Mat) -> int:
        lowest = np.inf
        lowest_index = 0
        for i, template in enumerate(self.templates):
            if (result := self.mse(template, tile)) < lowest:
                lowest = result
                lowest_index = i
        return lowest_index-1

    @property
    def tiles(self) -> list[list[int]]:
        tiles = []
        for row in self.tile_images:
            tile_row = []
            for tile_image in row:
                tile_row.append(self.compare_tile(tile_image))
            tiles.append(tile_row)
        return tiles

    def print_tiles(self, include_spaces: bool = True) -> None:
        text = ''
        for row in self.tiles:
            for tile in row:
                if tile == 0:
                    text += f'  '
                elif tile == -1:
                    text += f'X '
                elif tile == 9 or tile == 10:
                    text += f'B '
                elif tile == 11:
                    text += f'F '
                else:
                    text += f'{tile} '
            text += '\n'
        if include_spaces:
            text += '\n' * (os.get_terminal_size().lines -
                            text.count('\n') - 1)
        print(text, end='', flush=True)


class AI:
    def __init__(self, reader: Reader):
        self.reader = reader
        self.read_tiles()
        self._opened_tiles = []
        self._guess_tiles = []
        self.flagged_tiles = []

    def read_tiles(self) -> None:
        self.board: list[list[int]] = self.reader.tiles.copy()

    def click(self, coords: list[tuple[int, int]]):
        rect = GetWindowRectFromName('Minesweeper')
        x1, y1 = rect.left+23, rect.top+152
        for x, y in coords:
            pyautogui.moveTo(x1+(x*24)+12, y1+(y*24)+12)
            pyautogui.click()

    def surround_opened(self, x: int, y: int):
        possible_tiles = list(itertools.product([-1, 0, 1], repeat=2))
        for i, j in possible_tiles:
            try:
                if self.board[y+j][x+i] > 0:
                    return True
            except:
                pass

    def distance(self, A: tuple[int, int], B: tuple[int, int]):
        pointA = np.array(A)
        pointB = np.array(B)
        sum_sq = np.sum(np.square(pointA - pointB))
        return np.sqrt(sum_sq)

    @property
    def guess_tiles(self) -> list[tuple[int, int]]:
        if not self._guess_tiles:
            lst = []
            for j in range(self.reader.height):
                for i in range(self.reader.width):
                    if self.board[j][i] == -1:
                        if self.surround_opened(i, j):
                            lst.append((i, j))
            if not lst:
                return lst
            # # sort by distance
            # new_lst = [lst.pop(0)]
            # while lst:
            #     shortest = np.inf
            #     shortest_coord_index = 0
            #     for i, coord in enumerate(lst):
            #         if (distance := self.distance(new_lst[-1], coord)) < shortest:
            #             shortest = distance
            #             shortest_coord_index = i
            #     new_lst.append(lst.pop(shortest_coord_index))
            # # take flags to the back
            # print(new_lst)
            # for i, coord in enumerate(new_lst):
            #     if coord in self.flagged_tiles:
            #         # new_lst.insert(0, new_lst.pop(i))
            #         new_lst.append(new_lst.pop(i))
            # print()
            # print(new_lst)
            # replace value
            self._guess_tiles = lst
        return self._guess_tiles

    @property
    def opened_tiles(self) -> list[tuple[int, int]]:
        if not self._opened_tiles:
            lst = []
            for j in range(self.reader.height):
                for i in range(self.reader.width):
                    if self.board[j][i] > 0:
                        lst.append((i, j))
            self._opened_tiles = lst
        return self._opened_tiles

    def clear_properties(self) -> None:
        self._opened_tiles = []
        self._guess_tiles = []

    def surround_coords(self, x: int, y: int) -> list[tuple[int, int]]:
        lst = []
        for i, j in itertools.product([-1, 0, 1], repeat=2):
            lst.append((x+i, y+j))
        return lst

    def test_bombs(self, bombs: list[int | None]) -> bool:
        for x, y in self.opened_tiles:
            surround_bombs = []
            for coords in self.surround_coords(x, y):
                if coords in self.guess_tiles:
                    index = self.guess_tiles.index(coords)
                    surround_bombs.append(bombs[index])
            if surround_bombs.count(1) > self.board[y][x]:
                return False
            if (surround_bombs.count(None) + surround_bombs.count(1)) < self.board[y][x]:
                return False
        return True

    def add_flags(self, possible_bombs: list[int]) -> None:
        for i, bomb in enumerate(possible_bombs):
            if bomb == 1:
                if self.guess_tiles[i] not in self.flagged_tiles:
                    self.flagged_tiles.append(self.guess_tiles[i])

    def get_flag(self) -> list[int]:
        lst = []
        for guess_tile in self.guess_tiles:
            if guess_tile in self.flagged_tiles:
                lst.append(1)
            else:
                lst.append(0)
        return lst

    @property
    def possible_bombs(self) -> np.ndarray:
        lst = []
        self.clear_properties()
        turn = 0
        flags = self.get_flag()
        bombs = [None]*len(self.guess_tiles)
        used_bombs = [[] for _ in range(len(self.guess_tiles))]
        has_reached_end = False
        while not (len(used_bombs[0]) == 2 and not turn and has_reached_end):
            if turn == len(self.guess_tiles):
                turn -= 1  # go back one step
                used_bombs[turn] = []
                bombs[turn] = None
                turn -= 1  # go back one more step
            if flags[turn] == 1:
                used_bombs[turn] = [0, 1]
                bombs[turn] = 1
                if self.test_bombs(bombs):
                    turn += 1
                else:
                    bombs[turn] = None
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
                    while flags[turn] == 1:
                        used_bombs[turn] = []
                        bombs[turn] = None
                        turn -= 1  # go back one step
                # test a number
                else:
                    bombs[turn] = number_to_use
                    used_bombs[turn].append(number_to_use)
                    if self.test_bombs(bombs):
                        turn += 1
                    else:
                        bombs[turn] = None
            if None not in bombs and self.test_bombs(bombs):
                lst.append(bombs.copy())
                if not has_reached_end:
                    has_reached_end = True
        return np.array(lst).mean(axis=0)

    @property
    def possible_bombs_bruteforce(self) -> np.ndarray:
        lst = []
        self.clear_properties()
        for bombs in list(itertools.product([0, 1], repeat=len(self.guess_tiles))):
            if self.test_bombs(bombs, self.opened_tiles, self.guess_tiles):
                lst.append(bombs)
                print(bombs)
        return np.array(lst).mean(axis=0)

    def choose_and_click(self):
        time.sleep(0.1)
        self.read_tiles()
        if not self.opened_tiles:
            # self.click([(random.randint(0, self.reader.width-1),
            #            random.randint(0, self.reader.height-1))])
            self.click([(1, 1)])
        else:
            possible_bombs = self.possible_bombs.copy()
            self.add_flags(possible_bombs)
            print(possible_bombs)
            if 0 in possible_bombs:
                coords = []
                for i in np.where(possible_bombs == 0)[0]:
                    coords.append(self.guess_tiles[i])
                self.click(coords)
            else:
                i = np.argmin(possible_bombs)
                self.click([self.guess_tiles[i]])


if __name__ == '__main__':
    while True:
        question = input()
        if question in ['q', 'Q']:
            break
        os.system('cls')
        try:
            pyautogui.PAUSE = 0.001
            pyautogui.hotkey('alt', 'tab')
            time.sleep(1)
            # reader = Reader(width=9, height=9)
            reader = Reader(width=16, height=16)
            # reader = Reader(width=30, height=16)
            while True:
                ai = AI(reader)
                ai.reader.print_tiles(False)
                ai.choose_and_click()
        except IndexError:
            pass
