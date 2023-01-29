import math
from datetime import datetime
from pathlib import Path

import numpy as np
import pygame

from agent.deep_q import (CIRCULAR_DIRECTION_INDEX, CIRCULAR_DIRECTION_LIST,
                          DeepQAgent)
from game import GameGUI
from game_mechanic.mechanic import GameState
from helper.helper import plot
from param import get_deep_q_learning_parser

if __name__ == "__main__":
    parser = get_deep_q_learning_parser()
    args = parser.parse_args()
    map_height: int = args.map_height
    map_width: int = args.map_width
    map_file: str = args.map_file
    game_speed: int = args.game_speed
    render_block_size: int = args.render_block_size
    output_model_file: str = args.output_model_file
    load_model_file: str = args.load_model_file
    rounds: int = args.rounds

    if len(output_model_file.strip()) < 1:
        now = datetime.now()
        output_model_dir = Path('./model/').absolute()
        output_model_dir.mkdir(exist_ok=True)
        output_model_file = str(output_model_dir / f'{now.strftime("%Y_%m_%d_%H%M%S")}.pt')

    # * Print args
    print("="*20)
    print(f"map_height: {map_height}")
    print(f"map_width: {map_width}")
    print(f"map_file: {map_file}")
    print(f"game_speed: {game_speed}")
    print(f"render_block_size: {render_block_size}")
    print(f"output_model_file: {output_model_file}")
    print(f"load_model_file: {load_model_file}")
    print(f"rounds: {rounds}")
    print("="*20)

    _game_state = GameState(
        map_height=map_height,
        map_width=map_width,
        map_file=map_file,
    )
    game_gui = GameGUI(
        game_state=_game_state,
        render_block_size=render_block_size,
        game_speed=game_speed,
        max_round=rounds,
    )

    plot_scores = []
    plot_mean_scores = []
    total_score = 0
    record = 0
    agent = DeepQAgent(load_model_file=load_model_file)

    input_direction = game_gui.game_state.snake_player.curr_direction

    while True:
        # * Game Control
        # get old state
        state_old = agent.get_state(game_gui.game_state)

        pygame.event.get()  # ! Fix game hang in Windows OS

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

        # * Trace
        agent.trace_step(game_state=game_gui.game_state)

        done = game_gui.game_state.check_game_over() or game_gui.game_state.frame_iteration > 100*len(game_gui.game_state.snake_player.body_coords)
        score = game_gui.game_state.score
        reward = 0

        # * Post Trace
        agent.post_processing(game_state=game_gui.game_state)

        if done:
            reward = -10
        elif game_gui.game_state.is_fruit_eaten:
            reward = 15
        else:
            head_coord = game_gui.game_state.snake_player.head_coord
            prev_head_coord = game_gui.game_state.snake_player.body_coords[1]
            fruit_coord = game_gui.game_state.fruit_coord
            curr_dist = math.dist(head_coord,
                                  fruit_coord,)
            prev_dist = math.dist(prev_head_coord,
                                  fruit_coord,)
            # print(f"dist_to_fruit: {dist_to_fruit}")
            # check is distance is decrease
            if prev_dist < curr_dist:
                reward = -2
            else:
                # repeat step penalty
                reward -= max(0.5, agent.is_repeating_count*0.1)

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

            agent.clear_trace()

            if score > record:
                record = score
                agent.model.save(output_model_file=output_model_file)

            print('Game', agent.n_games, 'Score', score, 'Record:', record)

            plot_scores.append(score)
            total_score += score
            mean_score = total_score / agent.n_games
            plot_mean_scores.append(mean_score)
            plot(plot_scores, plot_mean_scores, output_model_file=output_model_file)

            if agent.n_games >= rounds and rounds >= 0:
                # deactivating pygame library
                pygame.quit()

                # quit the program
                quit()

        # Refresh game screen
        pygame.display.update()

        # Frame Per Second /Refresh Rate
        game_gui.fps.tick(game_gui.game_speed)
