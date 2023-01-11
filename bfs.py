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
        # 1. Get the fruit location from self.game_state.fruit_coord
        fruit_coord = tuple(self.game_state.fruit_coord)
        # 2. Get the current location of the snake from self.snake_player.head_coord()
        snake_head_coord = tuple(copy.deepcopy(self.snake_player.head_coord))
        # 3. Use BFS to find the path to the fruit location, the possible moves can be taken from self.game_state.get_next_possible_directions()
        queue = []
        visited = set()
        # prev is a 2D array storing Direction
        prev = [[None for _ in range(self.game_state.map_width)] for _ in range(self.game_state.map_height)]

        queue.append(snake_head_coord)
        visited.add(snake_head_coord)
        
        while len(queue) > 0:
            curr_coord = queue.pop(0)
            if curr_coord == fruit_coord:
                break
            for direction in self.game_state.get_next_possible_directions():
                next_head_coord_y = curr_coord[0] + DIRECTION__Y_POS_CHANGE[direction]
                next_head_coord_x = curr_coord[1] + DIRECTION__X_POS_CHANGE[direction]
                next_head_coord = (next_head_coord_y, next_head_coord_x)
                # Check if the next_head_coord is still within the maze 
                if next_head_coord_y < 0 or next_head_coord_y >= self.game_state.map_height or next_head_coord_x < 0 or next_head_coord_x >= self.game_state.map_width:
                    continue
                # If the next coordinate is a wall/obstacle
                if self.game_state.map_repr[next_head_coord_y][next_head_coord_x] == 1:
                    continue
                if next_head_coord not in visited:
                    visited.add(next_head_coord)
                    prev[next_head_coord_y][next_head_coord_x] = direction
                    queue.append(next_head_coord)

        # Reconstruct the path
        curr_coord = fruit_coord
        while curr_coord != snake_head_coord:
            if prev[curr_coord[0]][curr_coord[1]] == None:
                break
            self.path.append(prev[curr_coord[0]][curr_coord[1]])
            curr_coord = (curr_coord[0] - DIRECTION__Y_POS_CHANGE[prev[curr_coord[0]][curr_coord[1]]], curr_coord[1] - DIRECTION__X_POS_CHANGE[prev[curr_coord[0]][curr_coord[1]]])

        # 4. Save the entire path to the self.path list
        self.path.reverse()

    def compute_next_direction(self, gamestate) -> Direction:
        virtual_game_state = copy.deepcopy(gamestate)
        self.game_state = virtual_game_state
        self.snake_player = virtual_game_state.snake_player
        if len(self.path) == 0:
            self.bfs()
        if len(self.path) == 0:
            random.seed()
            possible_moves = self.game_state.get_next_possible_directions()
            print('Random')
            # Return a random move
            return possible_moves[random.randint(0, len(possible_moves) - 1)]
        return self.path.pop(0)
