import argparse


def get_parser():
    parser = argparse.ArgumentParser(description='Snake Maze Game')

    parser.add_argument("--map_height",
                        type=int,
                        default=36,
                        )
    parser.add_argument("--map_width",
                        type=int,
                        default=36,
                        )
    parser.add_argument("--map_file",
                        type=str,
                        default="./map/simple_map.txt",
                        )
    parser.add_argument("--game_speed",
                        type=int,
                        default=120,
                        )
    parser.add_argument("--render_block_size",
                        type=int,
                        default=5,
                        )
    parser.add_argument("--agent",
                        type=str,
                        default="distance",
                        choices=[
                            "human",
                            "distance",
                            "bfs",
                            "dql",
                        ],
                        )
    parser.add_argument("--model_file",
                        type=str,
                        default="./model/2023_01_12_172229.pt",
                        )
    parser.add_argument("--rounds",
                        type=int,
                        default=-1,
                        )
    parser.add_argument("--max_frame_iteration",
                        type=int,
                        default=0,
                        )
    return parser

def get_deep_q_learning_parser():
    parser = argparse.ArgumentParser(description='Snake Maze Game Deep Q Learning')

    parser.add_argument("--map_height",
                        type=int,
                        default=36,
                        )
    parser.add_argument("--map_width",
                        type=int,
                        default=36,
                        )
    parser.add_argument("--map_file",
                        type=str,
                        default="./map/simple_map.txt",
                        )
    parser.add_argument("--game_speed",
                        type=int,
                        default=120,
                        )
    parser.add_argument("--render_block_size",
                        type=int,
                        default=5,
                        )
    parser.add_argument("--output_model_file",
                        type=str,
                        default="",
                        )
    parser.add_argument("--rounds",
                        type=int,
                        default=-1,
                        )
    return parser
