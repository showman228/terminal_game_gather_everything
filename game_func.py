import time
import random
import os
from typing import Tuple, List
from pynput import keyboard
from constaints import *
from game_func import *
# добавить механику дверей и ключей чтобы открывать новые пути добавить режим "как можно быстрее", "успеть за 60 сек"

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

class GameSession:
    def __init__(self, game_map: List[List[int]]):
        self.game_map = [row[:] for row in game_map] # копия карты

        self.x = 1
        self.y = 1
        self.count_point = 0
        self.flag_get_point = False
        self.flag_end_game = False
        self.start_time = time.time()
        self.elapsed_time = 0
        self.time_limit = TIME_LIMIT
        self.flag_time_limit = False

        self.game_map[self.y][self.x] = '@'
        self.coordinates = random_point_on_game_map(game_map)


    def on_press(self, key):
        try:
            old_x, old_y = self.x, self.y
            new_x, new_y = self.x, self.y

            if key.char == 'w': new_y -= 1
            elif key.char == 's': new_y += 1
            elif key.char == 'a': new_x -= 1
            elif key.char == 'd': new_x += 1
            else: return 

            if self.game_map[new_y][new_x] == "#":
                return

            if self.game_map[new_y][new_x] == "!":
                self.count_point += 1
                self.flag_get_point = True

            self.game_map[new_y][new_x] = " "
            self.x, self.y = new_x, new_y
            self.game_map[self.y][self.x] = "@"

            update_cursor(old_x, old_y)
            print(" ", end="", flush=True)

            update_cursor(self.x, self.y)
            print("@", end="", flush=True)

            print(f"\033[{len(self.game_map) + 8};1H", end="", flush=True)

        except AttributeError:
            if key == keyboard.Key.esc:
                self.flag_end_game = True
                return False


    def on_release(self, key):
        if key == keyboard.Key.esc:
            return False
        
    def update_time(self):

        self.elapsed_time = int(time.time() - self.start_time)
        
        # Выводим время под картой (смещение + 10 строк)
        print(f"\033[{len(self.game_map) + 10};1H Прошло времени: {self.elapsed_time} / {self.time_limit}", end="", flush=True)
        print()

    def update_checkpoint(self) -> None:
        p_y, p_x = random.choice(self.coordinates)
        self.game_map[p_y][p_x] = '!'
        update_cursor(p_x, p_y)
        print("!", end='', flush=True)

    def show_point(self):
        print(f"\033[{len(self.game_map) + 10};1H {self.count_point}/5 Очков собрано", end="", flush=True)
        print()


    def run(self):
        clear_screen()
        print_control()
        print_game_map(self.game_map)

        self.update_checkpoint()
        self.start_time = time.time()

        listner = keyboard.Listener(on_press=self.on_press, on_release=self.on_release)
        listner.start()

        while not self.flag_end_game:
            self.update_time()
            time.sleep(0.1)

            if self.elapsed_time >= self.time_limit:
                self.flag_time_limit = True
                print(f"\nВремя вышло, вы успели собрать {self.count_point} очков.")
                break

            if self.flag_get_point:
                self.update_checkpoint()
                self.flag_get_point = False

            if self.count_point >= 5:
                self.flag_end_game = True
                print(f"\nПоздравляем, вы собрали все поинты за: {self.elapsed_time} секунд")
                break

            self.show_point()

        listner.stop()


def start_game(choice: int):
    if choice == 1:
        selected_map = GAME_MAP_1
    elif choice == 2:
        selected_map = GAME_MAP_2
    else:
        selected_map = GAME_MAP_1 # Значение по умолчанию
        
    game = GameSession(selected_map)
    game.run()