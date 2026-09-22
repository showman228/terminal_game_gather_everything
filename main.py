from game_func import *


def main(*args, **kwargs):
    clear_screen()

    print("Выберите карту для игры: ")
    print("game_map_1: обычный режим")
    print("game_map_2: режим с дверями")
    try:
        choice = int(input(">"))
    except Exception:
        pass

    start_game(choice)



if __name__ == "__main__":
   main()