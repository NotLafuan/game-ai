import itertools
import random
import time
import pyautogui
import cv2
import numpy as np
import os
from utils import *


class Reader:
    def __init__(self) -> None:
        self.templates: list[cv2.Mat] = [cv2.imread(os.path.join('tiles', file))
                                         for file in os.listdir('tiles')]
        self.find_width_height()

    def find_width_height(self) -> None:
        rect = get_window_rect_from_name('Minesweeper')
        img = pyautogui.screenshot()
        img = np.array(img)
        img = img[:, :, ::-1].copy()  # RGB2BGR
        window = img[rect.top:rect.bottom, rect.left:rect.right]
        x, y = 23, 152
        self.width: int = 0
        self.height: int = 0
        while True:  # for width
            image = window[y:y+24, x+(self.width*24):x+(self.width*24)+24]
            try:
                mse(self.templates[0], image)
                self.width += 1
            except:
                break
        while True:  # for height
            image = window[y+(self.height*24):y+(self.height*24)+24, x:x+24]
            try:
                mse(self.templates[0], image)
                self.height += 1
            except:
                break

    @property
    def tile_images(self) -> list[list[cv2.Mat]]:
        rect = get_window_rect_from_name('Minesweeper')
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

    @property
    def tiles(self) -> list[list[int]]:
        tiles = []
        for row in self.tile_images:
            tile_row = []
            for tile_image in row:
                tile_row.append(compare_image(tile_image, self.templates))
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


class AI(Reader):
    def __init__(self) -> None:
        super().__init__()
        self._number_tiles = []
        self._guess_tiles = []
        self.read_tiles()

    def read_tiles(self) -> None:
        time.sleep(0.1)
        self.board: list[list[int]] = self.tiles

    def number_neighbour(self, x: int, y: int) -> bool:
        neighbour_tiles = list(itertools.product([-1, 0, 1], repeat=2))
        for i, j in neighbour_tiles:
            try:
                j = y+j
                i = x+i
                if j < 0 or i < 0:
                    continue
                if self.board[j][i] > 0 and self.board[j][i] < 9:
                    return True
            except:
                pass
        return False

    def clear_properties(self) -> None:
        self._number_tiles = []
        self._guess_tiles = []

    def surround_coords(self, x: int, y: int) -> list[tuple[int, int]]:
        lst = []
        for i, j in itertools.product([-1, 0, 1], repeat=2):
            lst.append((x+i, y+j))
        return lst

    def test_bombs(self, bombs: list[int | None]) -> bool:
        for x, y in self.number_tiles:
            surround_bombs = []
            for coords in self.surround_coords(x, y):
                if coords in self.guess_tiles:
                    index = self.guess_tiles.index(coords)
                    surround_bombs.append(bombs[index])
                try:
                    if coords[1] < 0 or coords[0] < 0:
                        continue
                    if self.board[coords[1]][coords[0]] == 11:
                        surround_bombs.append(1)
                except IndexError:
                    pass
            if (surround_bombs.count(1)) > self.board[y][x]:
                return False
            if (surround_bombs.count(None) + surround_bombs.count(1)) < self.board[y][x]:
                return False
        return True

    @property
    def number_tiles(self) -> list[tuple[int, int]]:
        if self._number_tiles:
            return self._number_tiles
        self.read_tiles()
        lst = []
        for j in range(self.height):
            for i in range(self.width):
                if self.board[j][i] > 0 and self.board[j][i] < 9:
                    lst.append((i, j))
        self._number_tiles = lst
        return self._number_tiles

    @property
    def guess_tiles(self) -> list[tuple[int, int]]:
        if self._guess_tiles:
            return self._guess_tiles
        self.read_tiles()
        lst = []
        for j in range(self.height):
            for i in range(self.width):
                if self.board[j][i] == -1:
                    if self.number_neighbour(i, j):
                        lst.append((i, j))
        self._guess_tiles = lst
        return self._guess_tiles

    @property
    def possible_bombs(self) -> np.ndarray:
        self.clear_properties()
        lst = []
        bombs = [None]*len(self.guess_tiles)
        used_bombs = [[] for _ in range(len(self.guess_tiles))]
        turn = 0
        while turn != -1:
            try:
                if turn == len(self.guess_tiles):  # index out for range
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
                        if self.test_bombs(bombs):
                            turn += 1
                        else:
                            bombs[turn] = None
                if None not in bombs and self.test_bombs(bombs):
                    lst.append(bombs.copy())
            except KeyboardInterrupt:
                print('KeyboardInterrupt')
                time.sleep(0.5)
                pyautogui.hotkey('alt', 'tab')
                time.sleep(0.1)
                break
        print('possiblities', len(lst))
        if not lst:
            raise IndexError
        return np.array(lst).mean(axis=0)

    def choose_and_click(self):
        if not self.number_tiles:
            click([(random.randint(0, self.width-1),
                    random.randint(0, self.height-1))])
            self.clear_properties()
        else:
            possible_bombs = self.possible_bombs.copy()
            print(possible_bombs)
            if 1 in possible_bombs:
                coords = []
                for i in np.where(possible_bombs == 1)[0]:
                    coords.append(self.guess_tiles[i])
                right_click(coords)
            if 0 in possible_bombs:
                coords = []
                for i in np.where(possible_bombs == 0)[0]:
                    coords.append(self.guess_tiles[i])
                click(coords)
            else:
                i = np.argmin(possible_bombs)
                click([self.guess_tiles[i]])

    def print_guess(self, include_spaces: bool = True) -> None:
        text = ''
        for y, row in enumerate(self.tiles):
            for x, tile in enumerate(row):
                if (x, y) in self.guess_tiles:
                    text += f'O '
                elif tile == 0:
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


if __name__ == '__main__':
    pyautogui.PAUSE = 0.0001
    while True:
        question = input()
        if question in ['q', 'Q']:
            break
        os.system('cls')
        ai = AI()
        try:
            pyautogui.hotkey('alt', 'tab')
            time.sleep(0.5)
            while True:
                ai.print_tiles(include_spaces=False)
                ai.choose_and_click()
                if any(9 in tile for tile in ai.board):
                    print('BOMB!')
                    break
        except IndexError:
            print('IndexError')
