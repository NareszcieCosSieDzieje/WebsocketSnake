

import random
from typing import Union


def initialize_direction(snake_coordinates: dict[str, int], board_width: int, board_height: int) -> str:
    x = snake_coordinates['x']
    y = snake_coordinates['y']
    
    valid_directions = ['up', 'down', 'left', 'right'] # TODO ENUM 

    TRESHOLD = 3

    if x - TRESHOLD <= 0:
        valid_directions.remove('left')
    if y - TRESHOLD <= 0:
        valid_directions.remove('up')
    if x >= board_width - TRESHOLD:
        valid_directions.remove('right')
    if y >= board_height - TRESHOLD:
        valid_directions.remove('down')
    
    direction = random.choice(valid_directions)
    return direction

def get_free_coordinates(taken_coordinates: list[dict], board_width: int, board_height: int) -> dict[str, int]:
    x = None
    y = None

    taken_x_coordinates = [c['x'] for c in taken_coordinates]
    taken_y_coordinates = [c['y'] for c in taken_coordinates]

    while True:
        x = random.randint(0, board_width-1)
        if all(map(lambda tx: abs(tx[0] - tx[1]) > 1, zip([x]*len(taken_x_coordinates), taken_x_coordinates))):
            break

    while True:
        y = random.randint(0, board_height-1)
        if all(map(lambda ty: abs(ty[0] - ty[1]) > 1, zip([y]*len(taken_y_coordinates), taken_y_coordinates))):
            break

    return {'x': x, 'y': y}


def initialize_game_state():

    BOARD_WIDTH = 40
    BOARD_HEIGHT = 40

    snake1_x_coordinate = random.randint(0, BOARD_WIDTH-1)
    snake1_y_coordinate = random.randint(0, BOARD_HEIGHT-1)

    snake1: dict[str, Union[int, str]] = {
        'x': snake1_x_coordinate,
        'y': snake1_y_coordinate
    }

    snake1['direction'] = initialize_direction(snake_coordinates=snake1, board_width=BOARD_WIDTH, board_height=BOARD_HEIGHT)
    
    snake2 = get_free_coordinates(taken_coordinates=[snake1], board_width=BOARD_WIDTH, board_height=BOARD_HEIGHT)

    snake2['direction'] = initialize_direction(snake_coordinates=snake2, board_width=BOARD_WIDTH, board_height=BOARD_HEIGHT)
    
    food = get_free_coordinates([snake1, snake2], board_width=BOARD_WIDTH, board_height=BOARD_HEIGHT)

    init_state = {
        'snake_1': snake1,
        'snake_2': snake2,
        'food': food
    }

    return init_state


# TODO: CHYBA PO STRONIE KLIENTA
# def check_collisions(snake_1: list[dict], snake_2: list[dict], food: list[dict], board_width: int, board_height: int):
#     if snake_1[]
    