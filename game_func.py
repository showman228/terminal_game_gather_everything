import time
import random
import os
from typing import Tuple, List
from pynput import keyboard
from constaints import *
from game_func import *

# Управление
def print_control() -> None:
    print("Управление героем: \n w-вверх \n a - влево \n d - вправо \n s - вниз \n e - открыть & \n esc - выход")

# очистка консоли
def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

# выводит карту на консоль
def print_game_map(game_map: List[List[int]]) -> None:
    max_len = max(len(str(item)) for row in game_map for item in row)
    for row in game_map:
        formatted_row = " ".join(f"{item:>{max_len}}" for item in row)
        print(f"[ {formatted_row} ]")

# находит пустые места на карте
def free_space_on_game_map(game_map: List[List[int]]) -> List[List[int]]:
    free_space = []
    for i in range(1, len(game_map) - 1):
        for j in range(1, len(game_map[i]) - 1):
            if game_map[i][j] != "#":
                free_space.append([i, j])

    return free_space

# нужна для красивого отображения в консоли
def update_cursor(x, y):
    print(f"\033[{y + 8};{x * 2 + 3}H", end="")

# основная часть кода
class GameSession:
    def __init__(self, game_map: List[List[int]], start_x: int, start_y: int):
        self.game_map = [row[:] for row in game_map] # копия карты для дальнейшего быстрого запуска а также чтобы ставили новые зведзды и ключи не очищая при этом основную карту (исходник)

        self.x = start_x
        self.y = start_y
        self.count_point = 0 # кол-во очков
        self.count_keys = 0 # кол-во ключей
        self.flag_get_point = False # если True: + 1 к очкам
        self.flag_end_game = False
        self.start_time = time.time() # старт отсчета
        self.elapsed_time = 0 # разница по времени (сколько прошло)
        self.time_limit = TIME_LIMIT
        self.flag_time_limit = False # если время перевалило за лимит

        self.game_map[self.y][self.x] = '@' # устанавливаем героя на карту
        self.coordinates = free_space_on_game_map(game_map) # список свободных мест

    # отслеживает на удержавание на определенную клавишу
    def on_press(self, key):
        try:
            old_x, old_y = self.x, self.y
            new_x, new_y = self.x, self.y

            if key.char == 'w': new_y -= 1
            elif key.char == 's': new_y += 1
            elif key.char == 'a': new_x -= 1
            elif key.char == 'd': new_x += 1
            elif key.char == 'e':
                # дальше прописаны случае когда мы стоит рядом с дверью
                # если у нас есть ключ - мы откроем дверь, иначе нет и не сможем через нее пройти
                if self.game_map[new_y - 1][new_x] == "&" and self.count_keys > 0:
                    self.count_keys -= 1
                    self.game_map[new_y - 1][new_x] = " "
                    update_cursor(new_x, new_y - 1)
                    print(" ", end="", flush=True)
    
                elif self.game_map[new_y + 1][new_x] == "&" and self.count_keys > 0:
                    self.count_keys -= 1
                    self.game_map[new_y + 1][new_x] = " "
                    update_cursor(new_x, new_y + 1)
                    print(" ", end="", flush=True)
    
                elif self.game_map[new_y][new_x + 1] == "&" and self.count_keys > 0:
                    self.count_keys -= 1
                    self.game_map[new_y][new_x + 1] = " "
                    update_cursor(new_x + 1, new_y)
                    print(" ", end="", flush=True)
    
                elif self.game_map[new_y][new_x - 1] == "&" and self.count_keys > 0:
                    self.count_keys -= 1
                    self.game_map[new_y][new_x - 1] = " "
                    update_cursor(new_x - 1, new_y)
                    print(" ", end="", flush=True)

            else: return 

            # не можем проходить через закрытые двери а также стены
            if self.game_map[new_y][new_x] == "#" or self.game_map[new_y][new_x] == "&":
                return

            # условие на подбирание очков (звезд)
            if self.game_map[new_y][new_x] == "*":
                self.count_point += 1
                self.flag_get_point = True

            # условие на подбирание ключей
            if self.game_map[new_y][new_x] == "?":
                self.count_keys += 1

            # не забываем обновить позицию героя
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

    # считаем время
    def update_time(self):
        self.elapsed_time = int(time.time() - self.start_time)
        
        # Выводим время под картой (смещение + 10 строк)
        print(f"\033[{len(self.game_map) + 9};1H Прошло времени: {self.elapsed_time} / {self.time_limit}", end="", flush=True)
        print()

    # если мы подобрали звезду -> ставим новую на свободное место (на " ")
    def update_checkpoint(self) -> None:
        p_y, p_x = random.choice(self.coordinates)
        self.coordinates.remove([p_y, p_x])
        self.game_map[p_y][p_x] = '*'
        update_cursor(p_x, p_y)
        print("*", end='', flush=True)

    # если мы подобрали ключ -> ставим новый ключ на свободное место (на " ")
    def update_key(self) -> None:
        p_y, p_x = random.choice(self.coordinates)
        while self.game_map[p_y][p_x] == '*' or self.game_map[p_y][p_x] == "?":
            self.coordinates.remove([p_y, p_x])
            p_y, p_x = random.choice(self.coordinates)
            
        self.game_map[p_y][p_x] = "?"
        update_cursor(p_x, p_y)
        print("?", end="", flush=True)

    # показываем звезды на карте
    def show_points(self):
        print(f"\033[{len(self.game_map) + 10};1H {self.count_point}/5 Очков собрано" + " "*1000, end="", flush=True)
        print()

    # показываем ключи на карте 
    def show_keys(self):
        print(f"\033[{len(self.game_map) + 11};1H {self.count_keys}/2 ? собрано", end="", flush=True)
        print() 

    # сам движок для запуска сессии
    def run(self):
        clear_screen()
        print_control()
        print_game_map(self.game_map)

        # ставим чекпоинт и 2 ключа
        self.update_checkpoint()
        for _ in range(2):
            self.update_key()

        self.start_time = time.time()

        # отслеживаем нажатия по клавиатуре
        listner = keyboard.Listener(on_press=self.on_press, on_release=self.on_release)
        listner.start()

        # цикл игры (сессии) где отслеживаются события игры
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
                clear_screen()
                print(f"\nПоздравляем, вы собрали все поинты за: {self.elapsed_time} секунд")
                break

            self.show_points()
            self.show_keys()

        listner.stop()


def start_game(*args, **kwargs):
    clear_screen()

    while True:
        print("Выберите карту для игры: ")
        print("game_map_1: \n")
        print(print_game_map(GAME_MAP_1))
        print("game_map_2: \n")
        print(print_game_map(GAME_MAP_2))
        print("game_map_3: \n")
        print(print_game_map(GAME_MAP_3))
        print("game_map_4: \n")
        print(print_game_map(GAME_MAP_4))
        print("game_map_5: \n")
        print(print_game_map(GAME_MAP_5))

        try:
            choice = int(input(">"))
            if choice == 1:
                selected_map = GAME_MAP_1
            elif choice == 2:
                selected_map = GAME_MAP_2
            elif choice == 3:
                selected_map = GAME_MAP_3
            elif choice == 4:
                selected_map = GAME_MAP_4
            elif choice == 5:
                selected_map == GAME_MAP_5
            else:
                continue
        except Exception:
            continue
        
        # собираем 5 различных вариантов
        sp = []
        for _ in range(5):
            free_space = random.choice(free_space_on_game_map(selected_map))
            sp.append(free_space)

        edit_selected_map = [row[:] for row in selected_map]
        position_chosen = False

        # показываем их пользователю
        for val in sp:
            clear_screen()
            print("Выберите стартовую позицию: ")
            px, py = val
            edit_selected_map[py][px] = "@"
            print_game_map(edit_selected_map)
            try:
                choice = input("(y)es/(n)ext: ")
                if choice.lower() == "y":
                    selected_map[py][px] = "@"
                    position_chosen = True
                    break
                elif choice.lower() == "n":
                    edit_selected_map[py][px] = " " 
                    continue
            except Exception:
                pass

        # если варианты закончились, спрашиваем, не желает ли окончить игру пользователь
        if position_chosen:
            game = GameSession(selected_map, px, py)
            game.run()
            break
        else:
            print("Вы хотите выйти?")
            try:
                exit_choice = input("(y)es/(n)o: ")
                if exit_choice.lower() == "y":
                    break
                elif exit_choice.lower() == "n":
                    pass
            except Exception:
                pass

    print("Спасибо за игру!")


if __name__ == "__main__":
    start_game()