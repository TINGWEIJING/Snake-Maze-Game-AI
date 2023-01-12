import copy
import math

from game_mechanic.mechanic import (DIRECTION__X_POS_CHANGE,
                                    DIRECTION__Y_POS_CHANGE, Direction,
                                    GameState, SnakePlayer)


class DistanceController:
    game_state: GameState
    snake_player: SnakePlayer

    def __init__(self, game_state: GameState, snake_player: SnakePlayer = None) -> None:
        self.game_state = game_state
        self.snake_player = snake_player if snake_player != None else game_state.snake_player

    def compute_next_direction(self) -> Direction:
        # next_possible_directions = self.game_state.get_next_possible_directions(snake_player=self.snake_player)
        next_possible_directions = self.game_state.get_next_possible_directions()
        fruit_coord = self.game_state.fruit_coord
        snake_head_coord = copy.deepcopy(self.snake_player.head_coord)

        min_score = 10000
        min_score_direction = self.snake_player.curr_direction

        for direction in next_possible_directions:
            next_head_coord_y = snake_head_coord[0] + DIRECTION__Y_POS_CHANGE[direction]
            next_head_coord_x = snake_head_coord[1] + DIRECTION__X_POS_CHANGE[direction]

            is_direction_bad = False

            # skip if moving towards any wall
            if self.game_state.map_repr_np[next_head_coord_y, next_head_coord_x] == 1:
                continue

            # skip if moving towards any tails
            for tail_y, tail_x in self.snake_player.tail_coords:
                if next_head_coord_y == tail_y and next_head_coord_x == tail_x:
                    is_direction_bad = True
                    break
            
            if not is_direction_bad:
                dist_to_fruit = math.dist(
                    (next_head_coord_y,
                    next_head_coord_x),
                    fruit_coord)
                if dist_to_fruit <= min_score:
                    min_score = dist_to_fruit
                    min_score_direction = direction

        return min_score_direction

    def reset(self, game_state: GameState, snake_player: SnakePlayer = None):
        self.game_state = game_state
        self.snake_player = snake_player if snake_player != None else game_state.snake_player
