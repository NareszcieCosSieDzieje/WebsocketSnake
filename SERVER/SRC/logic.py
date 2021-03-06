

import random
from typing import Union


def initialize_direction(snake_coordinates: dict[str, int], board_width: int, board_height: int) -> str:
    x = snake_coordinates['x']
    y = snake_coordinates['y']
    
    valid_directions = ['up', 'down', 'left', 'right']

    TRESHOLD = 4

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


# def append_tail(snake: dict, taken_coordinates: list[dict], board_width: int, board_height: int):
#     opposite_dirs = {
#         'right': 'left',
#         'left': 'right',
#         'up': 'down',
#         'down': 'up'
#     }

#     valid_directions = ['up', 'down', 'left', 'right']

#     head = snake['coordinates'][0]
#     direction = snake['direction']
#     x, y = head['x'], head['y']

#     valid_directions.remove(direction)
#     valid_directions.remove(opposite_dirs[direction])

#     dir = random.choice(valid_directions)
#     if dir == 'up':
#         tail = [{'x': x, 'y': y+1}, {'x': x, 'y': y+2}]
#     elif dir == 'down':   
#         tail = [{'x': x, 'y': y-1}, {'x': x, 'y': y-2}]
#     elif dir == 'right':   
#         tail = [{'x': x+1, 'y': y}, {'x': x+2, 'y': y}]
#     elif dir == 'left':   
#         tail = [{'x': x-1, 'y': y}, {'x': x-2, 'y': y}]

#     for t in tail:
#         if t in taken_coordinates:
#             break
#         else:
#             snake['coordinates'].extend(tail)
#     return snake


def initialize_game_state() -> dict:

    GRID_SIZE = 20
    BOARD_WIDTH = 30
    BOARD_HEIGHT = 30

    snake1_x_coordinate = random.randint(0, BOARD_WIDTH-1)
    snake1_y_coordinate = random.randint(0, BOARD_HEIGHT-1)

    snake1: dict = {
        'coordinates': [{
            'x': snake1_x_coordinate,
            'y': snake1_y_coordinate
        }],
        'grow': False,
        'score': 0
    }

    snake1['direction'] = initialize_direction(snake_coordinates=snake1['coordinates'][0], board_width=BOARD_WIDTH, board_height=BOARD_HEIGHT)
    
    snake2: dict =  {
        'coordinates': [get_free_coordinates(taken_coordinates=snake1['coordinates'], board_width=BOARD_WIDTH, board_height=BOARD_HEIGHT)],
        'grow': False,
        'score': 0
    } 

    snake2['direction'] = initialize_direction(snake_coordinates=snake2['coordinates'][0], board_width=BOARD_WIDTH, board_height=BOARD_HEIGHT)

    food: dict = {
        'coordinates': get_free_coordinates(taken_coordinates=snake1['coordinates']+snake2['coordinates'], board_width=BOARD_WIDTH, board_height=BOARD_HEIGHT),
        'eaten': False
    }

    gridify = lambda pos: pos * GRID_SIZE

    for item in [snake1, snake2]:
        item['coordinates'] = [{'x': gridify(coordinates['x']), 'y': gridify(coordinates['y'])} for coordinates in item['coordinates']]
    
    food['coordinates'] = {'x': gridify(food['coordinates']['x']), 'y': gridify(food['coordinates']['y'])}

    # FIXME CONSTANTS
    BOARD_WIDTH = gridify(BOARD_WIDTH)
    BOARD_HEIGHT = gridify(BOARD_HEIGHT)

    init_state: dict = {
        'grid_size': GRID_SIZE,
        'board_width': BOARD_WIDTH,
        'board_height': BOARD_HEIGHT,
        'snake_1': snake1,
        'snake_2': snake2,
        'food': food
    }

    return init_state


def get_new_food(taken_coordinates: list[dict]) -> dict:
    
    GRID_SIZE = 20
    BOARD_WIDTH = 30
    BOARD_HEIGHT = 30
    new_food_coords = get_free_coordinates(taken_coordinates, BOARD_WIDTH, BOARD_HEIGHT)
    gridify = lambda pos: pos * GRID_SIZE

    food: dict = {
        'coordinates': {'x': gridify(new_food_coords['x']), 'y': gridify(new_food_coords['y'])},
        'eaten': False
    }

    return food


def get_iteration_message(snake1_direction: str, snake2_direction: str, food_eaten=False, game_over=False):
    pass

def pass_iteration_data():
    pass