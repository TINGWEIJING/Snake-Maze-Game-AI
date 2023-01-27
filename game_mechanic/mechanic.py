import copy
import math
import random
from enum import Enum

import numpy as np


class Direction(Enum):
    UP = 1
    DOWN = 2
    LEFT = 3
    RIGHT = 4

    @classmethod
    def is_opposite(cls, direction_a: 'Direction', direction_b: 'Direction'):
        return (direction_a == Direction.UP and direction_b == Direction.DOWN) or \
            (direction_a == Direction.DOWN and direction_b == Direction.UP) or \
            (direction_a == Direction.LEFT and direction_b == Direction.RIGHT) or \
            (direction_a == Direction.RIGHT and direction_b == Direction.LEFT)

    @classmethod
    def get_all_directions(cls):
        return [
            cls.UP,
            cls.DOWN,
            cls.LEFT,
            cls.RIGHT,
        ]


OPPOSITE_DIRECTION = {
    Direction.UP: Direction.DOWN,
    Direction.DOWN: Direction.UP,
    Direction.LEFT: Direction.RIGHT,
    Direction.RIGHT: Direction.LEFT,
}

DIRECTION__X_POS_CHANGE = {
    Direction.UP: 0,
    Direction.DOWN: 0,
    Direction.LEFT: -1,
    Direction.RIGHT: 1,
}

DIRECTION__Y_POS_CHANGE = {
    Direction.UP: -1,
    Direction.DOWN: 1,
    Direction.LEFT: 0,
    Direction.RIGHT: 0,
}


class SnakePlayer:
    body_coords: 'list[list[int]]'
    curr_direction: Direction
    snake_repr_np: np.ndarray

    def __init__(self,
                 map_height: int,
                 map_width: int,
                 ) -> None:
        self.body_coords = [
            [2, 5],  # head
            [3, 5],
            [4, 5],
            [5, 5]
        ]
        # center_y = map_height // 2
        # center_x = map_width // 2
        # self.body_coords = [
        #     [center_y, center_x],  # head
        #     [center_y - 1, center_x],
        #     [center_y - 2, center_x],
        #     [center_y - 3, center_x]
        # ]
        self.curr_direction = Direction.DOWN
        self.snake_repr_np = np.zeros(shape=(map_height, map_width)).astype(int)

    def create_new_head(self,
                        coord: 'list[int]',
                        ):
        self.body_coords.insert(0, coord)
        self.snake_repr_np[coord[0], coord[1]] = 1

    def remove_last_tail(self):
        last_tail_coord = self.body_coords.pop()
        self.snake_repr_np[last_tail_coord[0], last_tail_coord[1]] = 0

    @property
    def head_coord(self):
        return self.body_coords[0]

    @property
    def tail_coords(self):
        return self.body_coords[1:]


class GameState:
    map_height: int
    map_width: int
    map_repr_np: np.ndarray
    wall_coords: 'list[list[int]]'
    snake_player: SnakePlayer
    fruit_coord: 'list[int]'
    score: int

    is_fruit_eaten: bool
    is_virtual_game: bool  # For simulating the game, and to suppress the hit wall message
    max_frame_iteration: int
    frame_iteration: int

    def __init__(self,
                 map_height: int,
                 map_width: int,
                 map_file: str = None,
                 max_frame_iteration: int = -1,
                 ) -> None:
        self.wall_coords = []
        if map_file != None:
            lines: 'list[str]' = []
            with open(map_file) as f:
                lines = f.readlines()
            # check height & width
            self.map_height = len(lines)
            self.map_width = len(lines[0].strip())
            self.map_repr_np = np.zeros(shape=(self.map_height, self.map_width)).astype(int)

            for y in range(len(lines)):
                line = lines[y].strip()
                for x in range(len(line)):
                    is_wall_val = int(line[x])
                    self.map_repr_np[y, x] = is_wall_val
                    # save wall coord
                    if is_wall_val == 1:
                        self.wall_coords.append([y, x])
        else:
            self.map_height = map_height
            self.map_width = map_width
            self.map_repr_np = np.zeros(shape=(self.map_height, self.map_width)).astype(int)

        self.snake_player = SnakePlayer(map_height=self.map_height, map_width=self.map_width)
        self.is_fruit_eaten = True
        self.score = 0
        self.is_virtual_game = False
        if max_frame_iteration == 0:
            self.max_frame_iteration = int(math.sqrt(self.map_width ** 2 + self.map_height ** 2) * 1.5)
        else:
            self.max_frame_iteration = max_frame_iteration
        self.frame_iteration = 0
        self.spawn_fruit()

    def snake_make_next_move(self, input_direction: Direction):
        snake_direction = self.snake_player.curr_direction
        # avoid making opposite direction
        if not Direction.is_opposite(input_direction, snake_direction):
            snake_direction = input_direction
        # Moving the snake
        snake_new_head_coord = copy.deepcopy(self.snake_player.head_coord)
        snake_new_head_coord[0] += DIRECTION__Y_POS_CHANGE[snake_direction]  # Y
        snake_new_head_coord[1] += DIRECTION__X_POS_CHANGE[snake_direction]  # X

        self.snake_player.create_new_head(coord=snake_new_head_coord)
        self.snake_player.curr_direction = snake_direction
        return snake_direction

    def get_next_possible_directions(self):
        snake_direction = self.snake_player.curr_direction
        return [direction for direction in Direction.get_all_directions()
                if OPPOSITE_DIRECTION[snake_direction] != direction]

    def process_action(self):
        '''
        Eat fruit if head touch fruit
        '''
        snake_head_coord = self.snake_player.head_coord
        if snake_head_coord[0] == self.fruit_coord[0] and snake_head_coord[1] == self.fruit_coord[1]:
            self.score += 10
            self.is_fruit_eaten = True
            self.frame_iteration = -1
        else:
            self.snake_player.remove_last_tail()

        self.frame_iteration += 1

    def spawn_fruit(self):
        if self.is_fruit_eaten:
            is_fruit_overlap = True
            while is_fruit_overlap:
                next_fruit_coord = [random.randrange(1, self.map_height - 2),
                                    random.randrange(1, self.map_width - 2)]
                is_fruit_overlap = False
                # avoid fruit overlap with snake body
                for y_coord, x_coord in self.snake_player.body_coords:
                    if next_fruit_coord[0] == y_coord and next_fruit_coord[1] == x_coord:
                        is_fruit_overlap = True
                        break
                # avoid fruit overlap with wall
                for y_coord, x_coord in self.wall_coords:
                    if next_fruit_coord[0] == y_coord and next_fruit_coord[1] == x_coord:
                        is_fruit_overlap = True
                        break
            self.fruit_coord = next_fruit_coord
            self.is_fruit_eaten = False

    def check_game_over(self):
        snake_head_coord = self.snake_player.head_coord

        # hit surrounding wall
        if snake_head_coord[0] < 0 or snake_head_coord[0] >= self.map_height:
            return True
        if snake_head_coord[1] < 0 or snake_head_coord[1] >= self.map_width:
            return True

        # hit any wall
        if self.map_repr_np[snake_head_coord[0], snake_head_coord[1]] == 1:
            return True

        # eat itself
        for tail_y, tail_x in self.snake_player.tail_coords:
            if snake_head_coord[0] == tail_y and snake_head_coord[1] == tail_x:
                return True

        # trap
        if self.max_frame_iteration > 0 and self.frame_iteration >= self.max_frame_iteration:
            return True

        return False

    def reset_game(self):
        self.snake_player = SnakePlayer(map_height=self.map_height, map_width=self.map_width)
        self.is_fruit_eaten = True
        self.score = 0
        self.frame_iteration = 0
        self.spawn_fruit()

    def is_collision(self, coord: 'list[int]'):
        snake_head_coord = coord

        # hit surrounding wall
        if snake_head_coord[0] < 0 or snake_head_coord[0] >= self.map_height:
            # print("Hit up down boundaries")
            return True
        if snake_head_coord[1] < 0 or snake_head_coord[1] >= self.map_width:
            # print("Hit left right boundaries")
            return True

        # hit any wall
        if self.map_repr_np[snake_head_coord[0], snake_head_coord[1]] == 1:
            # print("Hit walls")
            return True

        # eat itself
        for tail_y, tail_x in self.snake_player.tail_coords:
            if snake_head_coord[0] == tail_y and snake_head_coord[1] == tail_x:
                # print("Hit itself")
                return True

        return False
