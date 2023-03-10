import copy
import random
from enum import Enum


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
    name: str

    def __init__(self, name: str = "", body_coords: 'list[list[int]]' = [
        [10, 5],  # head
        [9, 5],
        [8, 5],
        [7, 5]
    ]) -> None:
        self.body_coords = body_coords
        self.curr_direction = Direction.DOWN
        self.name = name

    @property
    def head_coord(self):
        return self.body_coords[0]

    @property
    def tail_coords(self):
        return self.body_coords[1:]

    def __repr__(self) -> str:
        return f"{self.name} - {self.body_coords}"


class GameState:
    map_height: int
    map_width: int
    map_repr: 'list[list[int]]'
    wall_coords: 'list[list[int]]'
    is_2_player: bool
    snake_player_1: SnakePlayer
    snake_player_2: SnakePlayer
    fruit_coord: 'list[int]'
    score: int

    is_fruit_eaten: bool

    def __init__(self,
                 map_height: int,
                 map_width: int,
                 map_file: str = None,
                 is_2_player: bool = True,) -> None:
        self.wall_coords = []
        if map_file != None:
            lines: 'list[str]' = []
            with open(map_file) as f:
                lines = f.readlines()
            # check height & width
            self.map_height = len(lines)
            self.map_width = len(lines[0].strip())
            self.map_repr = [[0]*self.map_width for _ in range(self.map_height)]

            for y in range(len(lines)):
                line = lines[y].strip()
                for x in range(len(line)):
                    is_wall_val = int(line[x])
                    self.map_repr[y][x] = is_wall_val
                    # save wall coord
                    if is_wall_val == 1:
                        self.wall_coords.append([y, x])
        else:
            self.map_height = map_height
            self.map_width = map_width
            self.map_repr = [[0]*map_width]*map_height

        self.is_2_player = is_2_player
        self.snake_player_1 = SnakePlayer(name="P1")
        self.snake_player_2 = SnakePlayer(name="P2", body_coords=[
            [self.map_height - 10, self.map_width - 5],  # head
            [self.map_height - 9, self.map_width - 5],
            [self.map_height - 8, self.map_width - 5],
            [self.map_height - 7, self.map_width - 5]
        ]) if self.is_2_player else None
        self.is_fruit_eaten = True
        self.score = 0

        self.spawn_fruit()

    def snake_make_next_move(self, snake_player: SnakePlayer, input_direction: Direction):
        snake_direction = snake_player.curr_direction
        # avoid making opposite direction
        if not Direction.is_opposite(input_direction, snake_direction):
            snake_direction = input_direction
        # Moving the snake
        snake_new_head_coord = copy.deepcopy(snake_player.head_coord)
        snake_new_head_coord[0] += DIRECTION__Y_POS_CHANGE[snake_direction]  # Y
        snake_new_head_coord[1] += DIRECTION__X_POS_CHANGE[snake_direction]  # X

        snake_player.body_coords.insert(0, snake_new_head_coord)
        snake_player.curr_direction = snake_direction
        return snake_direction

    def get_next_possible_directions(self, snake_player: SnakePlayer):
        snake_direction = snake_player.curr_direction
        return [direction for direction in Direction.get_all_directions()
                if OPPOSITE_DIRECTION[snake_direction] != direction]

    def process_action(self):
        '''
        Eat fruit if head touch fruit
        '''
        # player 1
        snake_head_coord = self.snake_player_1.head_coord
        if snake_head_coord[0] == self.fruit_coord[0] and snake_head_coord[1] == self.fruit_coord[1]:
            self.score += 10
            self.is_fruit_eaten = True
        else:
            self.snake_player_1.body_coords.pop()
        # player 2
        if self.snake_player_2 != None:
            if not self.is_fruit_eaten:  # priority for player 1 eat fruit
                snake_head_coord = self.snake_player_2.head_coord
                if snake_head_coord[0] == self.fruit_coord[0] and snake_head_coord[1] == self.fruit_coord[1]:
                    self.score += 10
                    self.is_fruit_eaten = True
                else:
                    self.snake_player_2.body_coords.pop()

    def spawn_fruit(self):
        if self.is_fruit_eaten:
            is_fruit_overlap = True
            while is_fruit_overlap:
                next_fruit_coord = [random.randrange(1, self.map_height - 2),
                                    random.randrange(1, self.map_width - 2)]
                is_fruit_overlap = False
                # avoid fruit overlap with snake body player 1
                for y_coord, x_coord in self.snake_player_1.body_coords:
                    if next_fruit_coord[0] == y_coord and next_fruit_coord[1] == x_coord:
                        is_fruit_overlap = True
                        break
                # avoid fruit overlap with snake body player 2
                if self.snake_player_2 != None:
                    for y_coord, x_coord in self.snake_player_2.body_coords:
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
        snake_head_coord = self.snake_player_1.head_coord

        # hit surrounding wall
        if snake_head_coord[0] < 0 or snake_head_coord[0] >= self.map_height:
            print("Hit up down boundaries")
            return True
        if snake_head_coord[1] < 0 or snake_head_coord[1] >= self.map_width:
            print("Hit left right boundaries")
            return True

        # hit any wall
        if self.map_repr[snake_head_coord[0]][snake_head_coord[1]] == 1:
            print("Hit walls")
            return True

        # eat itself
        for tail_y, tail_x in self.snake_player_1.tail_coords:
            if snake_head_coord[0] == tail_y and snake_head_coord[1] == tail_x:
                print("Hit itself")
                return True

        return False

    def reset_game(self):
        print("Reset game")
        self.snake_player_1 = SnakePlayer()
        self.snake_player_2 = SnakePlayer() if self.is_2_player else None
        self.is_fruit_eaten = True
        self.score = 0

        self.spawn_fruit()
