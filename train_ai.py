import math
from datetime import datetime

import numpy as np
import pygame

from agent.deep_q import (CIRCULAR_DIRECTION_INDEX, CIRCULAR_DIRECTION_LIST,
                          DeepQAgent)
from game import GameGUI
from game_mechanic.mechanic import Direction, GameState
from helper.helper import plot

if __name__ == "__main__":
    now = datetime.now()
    model_file_name = f'{now.strftime("%_Y_%m_%d_%H%M%S")}.pt'

    _game_state = GameState(
        map_height=36,
        map_width=36,
        map_file='./map/dummy_map.txt',
    )
    game_gui = GameGUI(
        game_state=_game_state,
        # game_speed=30,
        # controller=DistanceController(game_state=game_state)
    )

    plot_scores = []
    plot_mean_scores = []
    total_score = 0
    record = 0
    agent = DeepQAgent()

    input_direction = game_gui.game_state.snake_player.curr_direction
    print(input_direction)
    while True:
        # * Game Control
        # get old state
        state_old = agent.get_state(game_gui.game_state)

        # get move
        final_move = agent.get_action(state_old)

        # convert move to direction
        input_direction = game_gui.game_state.snake_player.curr_direction
        if np.array_equal(final_move, [0, 0, 1]):  # turn left
            input_direction = CIRCULAR_DIRECTION_LIST[(CIRCULAR_DIRECTION_INDEX[game_gui.game_state.snake_player.curr_direction] - 1) % 4]
        elif np.array_equal(final_move, [0, 1, 0]):  # turn right
            input_direction = CIRCULAR_DIRECTION_LIST[(CIRCULAR_DIRECTION_INDEX[game_gui.game_state.snake_player.curr_direction] + 1) % 4]
        else:  # [1, 0, 0] straight
            input_direction = game_gui.game_state.snake_player.curr_direction

        # * Game Logic
        game_gui.game_state.snake_make_next_move(input_direction=input_direction)
        game_gui.game_state.process_action()

        done = game_gui.game_state.check_game_over() or game_gui.game_state.frame_iteration > 100*len(game_gui.game_state.snake_player.body_coords)
        score = game_gui.game_state.score
        reward = 0
        if done:
            reward = -10
        elif game_gui.game_state.is_fruit_eaten:
            reward = 10
        else:
            head_coord = game_gui.game_state.snake_player.head_coord
            prev_head_coord = game_gui.game_state.snake_player.body_coords[1]
            fruit_coord = game_gui.game_state.fruit_coord
            curr_dist = math.dist(head_coord,
                                  fruit_coord,)
            prev_dist = math.dist(prev_head_coord,
                                  fruit_coord,)
            # print(f"dist_to_fruit: {dist_to_fruit}")
            reward = -1 if prev_dist < curr_dist else 0

        state_new = agent.get_state(game_gui.game_state)

        game_gui.game_state.spawn_fruit()
        is_game_over = done

        # * Rendering
        game_gui.render()

        # train short memory
        agent.train_short_memory(state_old, final_move, reward, state_new, done)

        # remember
        agent.remember(state_old, final_move, reward, state_new, done)

        # * Game Over Checking
        if is_game_over:
            print(f"SCORE: {game_gui.game_state.score}")
            # game_over(game_state.score)
            game_gui.game_state.reset_game()
            if game_gui.controller != None:
                game_gui.controller.reset(game_state=game_gui.game_state)
            input_direction = game_gui.game_state.snake_player.curr_direction
            pygame.event.clear()

            agent.n_games += 1
            agent.train_long_memory()

            if score > record:
                record = score
                agent.model.save(file_name=model_file_name)

            print('Game', agent.n_games, 'Score', score, 'Record:', record)

            plot_scores.append(score)
            total_score += score
            mean_score = total_score / agent.n_games
            plot_mean_scores.append(mean_score)
            plot(plot_scores, plot_mean_scores)

        # Refresh game screen
        pygame.display.update()

        # Frame Per Second /Refresh Rate
        game_gui.fps.tick(game_gui.game_speed)
