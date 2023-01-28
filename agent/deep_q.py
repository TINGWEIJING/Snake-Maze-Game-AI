import math
import random
from collections import deque

import numpy as np
import pygame
import torch

from agent.model import Linear_QNet, QTrainer
from agent.simple_bot import DistanceController
from game_mechanic.mechanic import Direction, GameState, SnakePlayer
from helper.helper import plot

MAX_MEMORY = 100_000
BATCH_SIZE = 1000
LR = 0.001


CIRCULAR_DIRECTION_INDEX = {
    Direction.UP: 4,
    Direction.RIGHT: 5,
    Direction.DOWN: 6,
    Direction.LEFT: 7,
}

CIRCULAR_DIRECTION_LIST = list(CIRCULAR_DIRECTION_INDEX.keys())

RENDER_BLOCK_SIZE = 10

GAME_SPEED = 1500  # FPS

# defining colors
BLACK_CLR = pygame.Color(0, 0, 0)
WHITE_CLR = pygame.Color(255, 255, 255)
RED_CLR = pygame.Color(255, 0, 0)
GREEN_CLR = pygame.Color(0, 255, 0)
BLUE_CLR = pygame.Color(0, 0, 255)
GOLD_CLR = pygame.Color(255, 215, 0)

GAME_WINDOM = None

# FPS (frames per second) controller
FPS = pygame.time.Clock()


class DeepQController(DistanceController):
    model: Linear_QNet

    def __init__(self,
                 model_file_name: str,
                 game_state: GameState,
                 snake_player: SnakePlayer = None,
                 ) -> None:
        super().__init__(game_state, snake_player)

        self.model = Linear_QNet(11, 256, 3)
        self.model.load_state_dict(torch.load(model_file_name))
        self.model.eval()

    def get_state(self):
        game_state = self.game_state
        head = game_state.snake_player.head_coord
        point_l = [head[0], head[1] - 1]
        point_r = [head[0], head[1] + 1]
        point_u = [head[0] - 1, head[1]]
        point_d = [head[0] + 1, head[1]]

        dir_l = game_state.snake_player.curr_direction == Direction.LEFT
        dir_r = game_state.snake_player.curr_direction == Direction.RIGHT
        dir_u = game_state.snake_player.curr_direction == Direction.UP
        dir_d = game_state.snake_player.curr_direction == Direction.DOWN

        state = [
            # Danger straight
            (dir_r and game_state.is_collision(point_r)) or
            (dir_l and game_state.is_collision(point_l)) or
            (dir_u and game_state.is_collision(point_u)) or
            (dir_d and game_state.is_collision(point_d)),

            # Danger right
            (dir_u and game_state.is_collision(point_r)) or
            (dir_d and game_state.is_collision(point_l)) or
            (dir_l and game_state.is_collision(point_u)) or
            (dir_r and game_state.is_collision(point_d)),

            # Danger left
            (dir_d and game_state.is_collision(point_r)) or
            (dir_u and game_state.is_collision(point_l)) or
            (dir_r and game_state.is_collision(point_u)) or
            (dir_l and game_state.is_collision(point_d)),

            # Move direction
            dir_l,
            dir_r,
            dir_u,
            dir_d,

            # Food location
            game_state.fruit_coord[1] < game_state.snake_player.head_coord[1],  # food left
            game_state.fruit_coord[1] > game_state.snake_player.head_coord[1],  # food right
            game_state.fruit_coord[0] < game_state.snake_player.head_coord[0],  # food up
            game_state.fruit_coord[0] > game_state.snake_player.head_coord[0]  # food down
        ]

        return np.array(state, dtype=int)

    def compute_next_direction(self) -> Direction:
        # return super().compute_next_direction()
        final_move = [0, 0, 0]
        state = self.get_state()
        state0 = torch.tensor(state, dtype=torch.float)
        prediction = self.model(state0)
        move = torch.argmax(prediction).item()
        final_move[move] = 1

        # convert move to direction
        input_direction = self.snake_player.curr_direction
        if np.array_equal(final_move, [0, 0, 1]):  # turn left
            input_direction = CIRCULAR_DIRECTION_LIST[(CIRCULAR_DIRECTION_INDEX[self.snake_player.curr_direction] - 1) % 4]
        elif np.array_equal(final_move, [0, 1, 0]):  # turn right
            input_direction = CIRCULAR_DIRECTION_LIST[(CIRCULAR_DIRECTION_INDEX[self.snake_player.curr_direction] + 1) % 4]
        else:  # [1, 0, 0] straight
            input_direction = self.snake_player.curr_direction

        return input_direction

    def reset(self, game_state: GameState, snake_player: SnakePlayer = None):
        super().reset(game_state, snake_player)


class DeepQAgent():

    def __init__(self, load_model_file: str = ''):
        self.n_games = 0
        self.epsilon = 0  # randomness
        self.gamma = 0.9  # discount rate
        self.memory = deque(maxlen=MAX_MEMORY)  # popleft()
        self.model = Linear_QNet(11, 256, 3)
        # load model
        if len(load_model_file.strip()) > 0:
            self.model.load_state_dict(torch.load(load_model_file))
            print(f'Loaded {load_model_file}')
        self.trainer = QTrainer(self.model, lr=LR, gamma=self.gamma)

    def get_state(self, game_state: GameState):
        head = game_state.snake_player.head_coord
        point_l = [head[0], head[1] - 1]
        point_r = [head[0], head[1] + 1]
        point_u = [head[0] - 1, head[1]]
        point_d = [head[0] + 1, head[1]]

        dir_l = game_state.snake_player.curr_direction == Direction.LEFT
        dir_r = game_state.snake_player.curr_direction == Direction.RIGHT
        dir_u = game_state.snake_player.curr_direction == Direction.UP
        dir_d = game_state.snake_player.curr_direction == Direction.DOWN

        state = [
            # Danger straight
            (dir_r and game_state.is_collision(point_r)) or
            (dir_l and game_state.is_collision(point_l)) or
            (dir_u and game_state.is_collision(point_u)) or
            (dir_d and game_state.is_collision(point_d)),

            # Danger right
            (dir_u and game_state.is_collision(point_r)) or
            (dir_d and game_state.is_collision(point_l)) or
            (dir_l and game_state.is_collision(point_u)) or
            (dir_r and game_state.is_collision(point_d)),

            # Danger left
            (dir_d and game_state.is_collision(point_r)) or
            (dir_u and game_state.is_collision(point_l)) or
            (dir_r and game_state.is_collision(point_u)) or
            (dir_l and game_state.is_collision(point_d)),

            # Move direction
            dir_l,
            dir_r,
            dir_u,
            dir_d,

            # Food location
            game_state.fruit_coord[1] < game_state.snake_player.head_coord[1],  # food left
            game_state.fruit_coord[1] > game_state.snake_player.head_coord[1],  # food right
            game_state.fruit_coord[0] < game_state.snake_player.head_coord[0],  # food up
            game_state.fruit_coord[0] > game_state.snake_player.head_coord[0]  # food down
        ]

        return np.array(state, dtype=int)

    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done))  # popleft if MAX_MEMORY is reached

    def train_long_memory(self):
        if len(self.memory) > BATCH_SIZE:
            mini_sample = random.sample(self.memory, BATCH_SIZE)  # list of tuples
        else:
            mini_sample = self.memory

        states, actions, rewards, next_states, dones = zip(*mini_sample)
        self.trainer.train_step(states, actions, rewards, next_states, dones)
        # for state, action, reward, nexrt_state, done in mini_sample:
        #    self.trainer.train_step(state, action, reward, next_state, done)

    def train_short_memory(self, state, action, reward, next_state, done):
        self.trainer.train_step(state, action, reward, next_state, done)

    def get_action(self, state):
        # random moves: tradeoff exploration / exploitation
        self.epsilon = 80 - self.n_games
        final_move = [0, 0, 0]
        if random.randint(0, 200) < self.epsilon:
            move = random.randint(0, 2)
            final_move[move] = 1
        else:
            state0 = torch.tensor(state, dtype=torch.float)
            prediction = self.model(state0)
            move = torch.argmax(prediction).item()
            final_move[move] = 1

        return final_move


def train():
    plot_scores = []
    plot_mean_scores = []
    total_score = 0
    record = 0
    agent = DeepQAgent()

    game_state = GameState(
        map_height=50,
        map_width=50,
        map_file='./map/dummy_map.txt',
    )
    pygame.init()
    WINDOW_WIDTH = game_state.map_width * RENDER_BLOCK_SIZE
    WINDOM_HEIGHT = game_state.map_height * RENDER_BLOCK_SIZE
    GAME_WINDOM = pygame.display.set_mode((WINDOW_WIDTH, WINDOM_HEIGHT))

    while True:
        # get old state
        state_old = agent.get_state(game_state)

        # get move
        final_move = agent.get_action(state_old)

        # perform move and get new state
        # reward, done, score = game.play_step(final_move)

        # convert move to direction
        input_direction = game_state.snake_player.curr_direction
        if np.array_equal(final_move, [0, 0, 1]):  # turn left
            input_direction = CIRCULAR_DIRECTION_LIST[(CIRCULAR_DIRECTION_INDEX[game_state.snake_player.curr_direction] - 1) % 4]
        elif np.array_equal(final_move, [0, 1, 0]):  # turn right
            input_direction = CIRCULAR_DIRECTION_LIST[(CIRCULAR_DIRECTION_INDEX[game_state.snake_player.curr_direction] + 1) % 4]
        else:  # [1, 0, 0] straight
            input_direction = game_state.snake_player.curr_direction

        game_state.snake_make_next_move(input_direction)
        game_state.process_action()

        done = game_state.check_game_over() or game_state.frame_iteration > 100*len(game_state.snake_player.body_coords)
        score = game_state.score
        reward = 0
        if done:
            reward = -10
        elif game_state.is_fruit_eaten:
            reward = 10
        else:
            head_coord = game_state.snake_player.head_coord
            prev_head_coord = game_state.snake_player.body_coords[1]
            fruit_coord = game_state.fruit_coord
            curr_dist = math.dist(head_coord,
                                  fruit_coord,)
            prev_dist = math.dist(prev_head_coord,
                                  fruit_coord,)
            # print(f"dist_to_fruit: {dist_to_fruit}")
            reward = -1 if prev_dist < curr_dist else 0

        state_new = agent.get_state(game_state)

        game_state.spawn_fruit()

        # * Rendering
        GAME_WINDOM.fill(BLACK_CLR)

        # render white wall
        for coord_y, coord_x in game_state.wall_coords:
            pygame.draw.rect(GAME_WINDOM,
                             WHITE_CLR,
                             pygame.Rect(
                                 coord_x * RENDER_BLOCK_SIZE,
                                 coord_y * RENDER_BLOCK_SIZE,
                                 RENDER_BLOCK_SIZE,
                                 RENDER_BLOCK_SIZE)
                             )

        # render snake tail
        for coord in game_state.snake_player.tail_coords:
            pygame.draw.rect(GAME_WINDOM, GREEN_CLR,
                             pygame.Rect(coord[1] * RENDER_BLOCK_SIZE, coord[0] * RENDER_BLOCK_SIZE, RENDER_BLOCK_SIZE, RENDER_BLOCK_SIZE))
        snake_head_coord = game_state.snake_player.head_coord
        # render snake head
        pygame.draw.rect(GAME_WINDOM, RED_CLR,
                         pygame.Rect(snake_head_coord[1] * RENDER_BLOCK_SIZE, snake_head_coord[0] * RENDER_BLOCK_SIZE, RENDER_BLOCK_SIZE, RENDER_BLOCK_SIZE))
        # render fruit
        pygame.draw.rect(GAME_WINDOM,
                         GOLD_CLR,
                         pygame.Rect(
                             game_state.fruit_coord[1] * RENDER_BLOCK_SIZE,
                             game_state.fruit_coord[0] * RENDER_BLOCK_SIZE,
                             RENDER_BLOCK_SIZE,
                             RENDER_BLOCK_SIZE)
                         )

        # Refresh game screen
        pygame.display.update()

        # train short memory
        agent.train_short_memory(state_old, final_move, reward, state_new, done)

        # remember
        agent.remember(state_old, final_move, reward, state_new, done)

        if done:
            # train long memory, plot result
            game_state.reset_game()
            agent.n_games += 1
            agent.train_long_memory()

            if score > record:
                record = score
                agent.model.save()

            print('Game', agent.n_games, 'Score', score, 'Record:', record)

            plot_scores.append(score)
            total_score += score
            mean_score = total_score / agent.n_games
            plot_mean_scores.append(mean_score)
            plot(plot_scores, plot_mean_scores)

        # Frame Per Second /Refresh Rate
        FPS.tick(GAME_SPEED)


if __name__ == '__main__':
    train()
