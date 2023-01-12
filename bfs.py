import time
from mechanic import (DIRECTION__X_POS_CHANGE, DIRECTION__Y_POS_CHANGE, OPPOSITE_DIRECTION,
                      Direction, GameState, SnakePlayer)
import copy
import math
import random

class BFSController:
    game_state: GameState
    snake_player: SnakePlayer
    path: list[Direction]

    def __init__(self, game_state: GameState, snake_player: SnakePlayer = None) -> None:
        self.game_state = game_state
        self.snake_player = snake_player if snake_player != None else game_state.snake_player
        self.path = []

    def bfs(self):
        game_copy = copy.deepcopy(self.game_state)
        game_copy.is_virtual_game = True
        snake_copy = copy.deepcopy(self.snake_player)
        # 1. Get the fruit location from self.game_state.fruit_coord
        fruit_coord = tuple(game_copy.fruit_coord)
        # 2. Get the current location of the snake from self.snake_player.head_coord()
        snake_head_coord = tuple(snake_copy.head_coord)
        # 3. Use BFS to find the path to the fruit location, the possible moves can be taken from self.game_state.get_next_possible_directions()
        queue = []
        visited = set()
        # prev is a dictionary, <cur_game_state, Direction>
        prev = {}

        queue.append(game_copy)
        visited.add(snake_head_coord)
        curr_game: GameState
        print('Begin BFS for fruit coordinate', fruit_coord)
        while len(queue) > 0:
            curr_game: GameState = queue.pop(0)
            if curr_game.is_fruit_eaten:
                break
            for direction in curr_game.get_next_possible_directions():
                next_head_coord_y = curr_game.snake_player.head_coord[0] + DIRECTION__Y_POS_CHANGE[direction]
                next_head_coord_x = curr_game.snake_player.head_coord[1] + DIRECTION__X_POS_CHANGE[direction]
                next_head_coord = (next_head_coord_y, next_head_coord_x)
                if next_head_coord in visited:
                    continue
                next_game = copy.deepcopy(curr_game)
                next_game.snake_make_next_move(direction)
                next_game.process_action()
                # If the next move is invalid (out of maze, touch body)
                if next_game.check_game_over():
                    del next_game
                    continue
                prev[next_game] = tuple([curr_game, direction])
                queue.append(next_game)
                visited.add(next_head_coord)
        # Reconstruct the path
        if curr_game.is_fruit_eaten: # There exist a path to the fruit
            while curr_game != game_copy:
                [prev_game_state, prev_direction] = prev[curr_game]
                self.path.append(prev_direction)
                curr_game = prev_game_state
        # 4. Save the entire path to the self.path list
        self.path.reverse()

    def compute_next_direction(self, gamestate: GameState) -> Direction:
        self.game_state = gamestate
        self.snake_player = gamestate.snake_player
        if len(self.path) == 0:
            self.bfs()
        if len(self.path) == 0:
            random.seed()
            possible_moves = self.game_state.get_next_possible_directions()
            print('Random')
            # Return a random move
            return possible_moves[random.randint(0, len(possible_moves) - 1)]
        return self.path.pop(0)
