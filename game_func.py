import time
import random
import os
from typing import Tuple, List
from pynput import keyboard
from constaints import *
from game_func import *
# добавить механику дверей и ключей чтобы открывать новые пути добавить режим "как можно быстрее", "успеть за 60 сек"

game_map = GAME_MAP_2

def print_control() -> None:
    print("Управление героем: \n w-вверх \n a - влево \n d - вправо \n s - вниз \n esc - выход")

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_game_map(game_map: List[List[int]]) -> None:
    max_len = max(len(str(item)) for row in game_map for item in row)
    for row in game_map:
        formatted_row = " ".join(f"{item:>{max_len}}" for item in row)
        print(f"[ {formatted_row} ]")

def random_point_on_game_map(game_map: List[List[int]]) -> List[Tuple[int]]:
    free_space = []
    for i in range(1, len(game_map) - 1):
        for j in range(1, len(game_map[i]) - 1):
            if game_map[i][j] != "#":
                free_space.append((i, j))

    return free_space

def update_cursor(x, y):
    print(f"\033[{y + 7};{x * 2 + 3}H", end="")

def update_time(time_limit: int):
    global ELAPSED_TIME
    ELAPSED_TIME = int(time.time() - START_TIME)
    
    # Выводим время под картой (смещение + 9 строк)
    print(f"\033[{len(game_map) + 9};1H Прошло времени: {ELAPSED_TIME} / {time_limit}", end="", flush=True)
    print()

def update_checkpoint(game_map: List[List[int]], coordinates: List[Tuple[int]]) -> None:
    p_y, p_x = random.choice(coordinates)
    game_map[p_y][p_x] = '🦵🏿'
    update_cursor(p_x, p_y)
    print("🦵🏿", end='', flush=True)

def show_point(count_point: int):
    print(f"\033[{len(game_map) + 10};1H {count_point}/5 Очков собрано", end="", flush=True)
    print()


def on_press_1(key):
    global X, Y, game_map, COUNT_POINT, FLAG_GET_POINT, FLAG_END_GAME
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
        if game_map[new_y][new_x] == '#':
            return

        if game_map[new_y][new_x] == "🦵🏿":
            COUNT_POINT += 1
            FLAG_GET_POINT = True

        # Убираем 🧑🏿‍🦽 со старой позиции
        game_map[old_y][old_x] = ' '

        # Перемещаем героя
        X = new_x
        Y = new_y

        # Ставим 🧑🏿‍🦽 на новую позицию
        game_map[Y][X] = '🧑🏿‍🦽'

        # Обновляем только старую клетку (используем flush=True для мгновенного вывода)
        update_cursor(old_x, old_y)
        print(' ', end='', flush=True)

        # Обновляем только новую клетку
        update_cursor(X, Y)
        print('🧑🏿‍🦽', end='', flush=True)
        
        # Отводим курсор вниз под карту, чтобы он не мерцал поверх символа '🧑🏿‍🦽'
        print(f"\033[{len(game_map) + 8};1H", end="", flush=True)

    except AttributeError:
        if key == keyboard.Key.esc:
            FLAG_END_GAME = True
            return False

def on_release_1(key):
    if key == keyboard.Key.esc:
        return False


def game_mode_1():
    global START_TIME, FLAG_END_GAME, FLAG_GET_POINT, ELAPSED_TIME

    clear_screen()
    print_control()
    print_game_map(game_map)

    coordinates = random_point_on_game_map(game_map)
    update_checkpoint(game_map, coordinates)
    
    START_TIME = time.time()    
    
    listener = keyboard.Listener(on_press=on_press_1, on_release=on_release_1)
    listener.start()
    
    while not FLAG_END_GAME:
        update_time(TIME_LIMIT)
        time.sleep(0.1)
        if FLAG_GET_POINT:
            update_checkpoint(game_map, coordinates)
            FLAG_GET_POINT = False
    
        if COUNT_POINT == 5:
            FLAG_END_GAME = True

        show_point(COUNT_POINT)
    
    listener.stop()
    
    # print(f"\033[{len(game_map) + 12};1H", end="", flush=True)
    
    if COUNT_POINT == 5 and FLAG_END_GAME:
        print(f"Поздравляем, вы собрали все поинты за: {ELAPSED_TIME} секунд")
    else:
        print("Игра прервана")

def game_mode_2(*args, **kwargs):
    global START_TIME, FLAG_END_GAME, FLAG_GET_POINT, ELAPSED_TIME, FLAG_TIME_LIMIT 


    if ELAPSED_TIME >= TIME_LIMIT:
        FLAG_END_GAME = True
        FLAG_TIME_LIMIT = True

    elif FLAG_END_GAME and FLAG_TIME_LIMIT:
        print(f"Время вышло, вы успели собрать {COUNT_POINT}")