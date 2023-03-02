import ctypes
import cv2
import numpy as np
import pyautogui
import utils.utilsModule


def get_window_rect_from_name(name: str):
    hwnd = ctypes.windll.user32.FindWindowW(0, name)
    rect = ctypes.wintypes.RECT()
    ctypes.windll.user32.GetWindowRect(hwnd, ctypes.pointer(rect))
    return rect


def mse(imageA: cv2.Mat, imageB: cv2.Mat) -> float:
    '''The 'Mean Squared Error' between the two images is the
       sum of the squared difference between the two images;
       NOTE: the two images must have the same dimension'''
    err = np.sum((imageA.astype('float') - imageB.astype('float')) ** 2)
    err /= float(imageA.shape[0] * imageA.shape[1])

    # return the MSE, the lower the error, the more "similar"
    return err


def compare_image(image: cv2.Mat, templates: list[cv2.Mat]) -> int:
    '''Return the index of the closest image in templates'''
    lowest = np.inf
    lowest_index = 0
    for i, template in enumerate(templates):
        if (result := mse(template, image)) < lowest:
            lowest = result
            lowest_index = i
    return lowest_index-1


def click(coords: list[tuple[int, int]]):
    rect = get_window_rect_from_name('Minesweeper')
    x1, y1 = rect.left+23, rect.top+152
    for x, y in coords:
        pyautogui.moveTo(x1+(x*24)+12, y1+(y*24)+12)
        pyautogui.click()


def right_click(coords: list[tuple[int, int]]):
    rect = get_window_rect_from_name('Minesweeper')
    x1, y1 = rect.left+23, rect.top+152
    for x, y in coords:
        pyautogui.moveTo(x1+(x*24)+12, y1+(y*24)+12)
        pyautogui.rightClick()


def distance(A: tuple[int, int], B: tuple[int, int]):
    pointA = np.array(A)
    pointB = np.array(B)
    sum_sq = np.sum(np.square(pointA - pointB))
    return np.sqrt(sum_sq)


def possible_bombs(width: int,  height: int,
                   board: list[tuple[int, int]],
                   guess_tiles: list[tuple[int, int]],
                   number_tiles: list[tuple[int, int]]) -> list[float]:
    return utilsModule._possible_bombs(width,  height, board,  guess_tiles,  number_tiles)
