import time
import random
import os
from typing import Tuple, List
from pynput import keyboard
from constaints import *
from game_func import *
# закинуть функции в отдельный файл, добавить механику дверей и ключей чтобы открывать новые пути добавить режим "как можно быстрее", "успеть за 60 сек"

def print_control() -> None:
    print("Управление героем: \n w-вверх \n a - влево \n d - вправо \n s - вниз \n esc - выход")

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_game_map() -> None:
    max_len = max(len(str(item)) for row in GAME_MAP for item in row)
    for row in GAME_MAP:
        formatted_row = " ".join(f"{item:>{max_len}}" for item in row)
        print(f"[ {formatted_row} ]")

def random_point_on_game_map() -> List[Tuple[int]]:
    global GAME_MAP
    free_space = []
    for i in range(1, len(GAME_MAP) - 1):
        for j in range(1, len(GAME_MAP[i]) - 1):
            if GAME_MAP[i][j] != "#":
                free_space.append((i, j))

    return free_space

def update_cursor(x, y):
    print(f"\033[{y + 7};{x * 2 + 3}H", end="")

def update_time():
    global FLAG_END_GAME, ELAPSED_TIME
    ELAPSED_TIME = int(time.time() - START_TIME)
    
    # Выводим время под картой (смещение + 9 строк)
    print(f"\033[{len(GAME_MAP) + 9};1H Прошло времени: {ELAPSED_TIME}", end="", flush=True)
    print()

def update_checkpoint(coordinates: List[Tuple[int]]) -> None:
    global GAME_MAP
    p_y, p_x = random.choice(coordinates)
    GAME_MAP[p_y][p_x] = '!'
    update_cursor(p_x, p_y)
    print("!", end='', flush=True)

def show_point():
    global COUNT_POINT
    print(f"\033[{len(GAME_MAP) + 10};1H {COUNT_POINT}/5 Очков собрано", end="", flush=True)
    print()


def on_press(key):
    global X, Y, GAME_MAP, FLAG_END_GAME, COUNT_POINT, FLAG_GET_POINT

    try:
        old_x = X
        old_y = Y

        new_x = X
        new_y = Y

        if key.char == 'w':
            new_y -= 1
        elif key.char == 's':
            new_y += 1
        elif key.char == 'a':
            new_x -= 1
        elif key.char == 'd':
            new_x += 1
        else:
            return

        # Проверяем, можно ли перейти
        if GAME_MAP[new_y][new_x] == '#':
            return

        if GAME_MAP[new_y][new_x] == "!":
            COUNT_POINT += 1
            FLAG_GET_POINT = True

        # Убираем @ со старой позиции
        GAME_MAP[old_y][old_x] = ' '

        # Перемещаем героя
        X = new_x
        Y = new_y

        # Ставим @ на новую позицию
        GAME_MAP[Y][X] = '@'

        # Обновляем только старую клетку (используем flush=True для мгновенного вывода)
        update_cursor(old_x, old_y)
        print(' ', end='', flush=True)

        # Обновляем только новую клетку
        update_cursor(X, Y)
        print('@', end='', flush=True)
        
        # Отводим курсор вниз под карту, чтобы он не мерцал поверх символа '@'
        print(f"\033[{len(GAME_MAP) + 8};1H", end="", flush=True)

    except AttributeError:
        if key == keyboard.Key.esc:
            FLAG_END_GAME = True
            return False

def on_release(key):
    if key == keyboard.Key.esc:
        return False


def menu(*args, **kwargs):
    global START_TIME, FLAG_END_GAME, FLAG_GET_POINT, ELAPSED_TIME
    
    coordinates = random_point_on_game_map()
    update_checkpoint(coordinates)
    
    clear_screen()
    print_control()
    
    print_game_map()
        
    START_TIME = time.time()    
    
    listener = keyboard.Listener(on_press=on_press, on_release=on_release)
    listener.start()
    
    while not FLAG_END_GAME:
        update_time()
        time.sleep(0.1)
        if FLAG_GET_POINT:
            update_checkpoint(coordinates=coordinates)
            FLAG_GET_POINT = False
    
        if COUNT_POINT == 5:
            FLAG_END_GAME = True
    
        show_point()
    
    listener.stop()
    
    print(f"\033[{len(GAME_MAP) + 12};1H", end="", flush=True)
    
    if COUNT_POINT == 5 and FLAG_END_GAME:
        print(f"Поздравляем, вы собрали все поинты за: {ELAPSED_TIME} секунд")
    else:
        print("Игра прервана")