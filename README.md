# Snake Maze Game
- [Snake Maze Game](#snake-maze-game)
  - [Quick Start](#quick-start)
  - [Run Snake Game](#run-snake-game)
    - [Example](#example)
  - [Deep Q-Learning Training](#deep-q-learning-training)
    - [Example](#example-1)
  - [Map Generation](#map-generation)

## Quick Start
1. Create python environment.
   - Using `venv`
        ```bash
        python -m venv venv
        ```
   - Using conda
        ```bash
        conda create --name snake_env
        ```
2. Activate python environment.
   - Using `venv`
        ```bash
        ./venv/Scripts/Activate.ps1 # Windows PowerShell
        .\venv\Scripts\activate # Windows cmd
        source venv/bin/activate # Linux
        ```
   - Using conda
        ```bash
        conda activate snake_env
        ```
3. Install libraries.
    ```bash
    pip install -r requirements.txt
    ```
4. Install PyTorch. Please refer https://pytorch.org/get-started/locally/.

## Run Snake Game
Run `python game.py` with following arguments (Ctrl + C for force quit):

| Arg                     | Type | Default                        | Choices                             | Description                                                                                                                                                   |
| ----------------------- | ---- | ------------------------------ | ----------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `--map_height`          | int  | 36                             | -                                   | Set height of the blank map if not using any map from map file.                                                                                               |
| `--map_width`           | int  | 36                             | -                                   | Set width of the blank map if not using any map from map file.                                                                                                |
| `--map_file`            | str  | "./map/simple_map.txt"         | -                                   | Load map from map file. <br> Pass "" empty string to use blank map.                                                                                           |
| `--game_speed`          | int  | 120                            | -                                   | Control min FPS of the game.                                                                                                                                  |
| `--render_block_size`   | int  | 5                              | -                                   | Game rendering size. Higher value bigger screen.                                                                                                              |
| `--agent`               | str  | "distance"                     | ["human", "distance", "bfs", "dql"] | AI Agent or Human Control.<br>"human": Human control<br>"distance": One Step Ahead Distance Decision<br>"bfs": Breadth-first search<br>"dql": Deep Q-Learning |
| `--model_file`          | str  | "./model/u_map_45.pt" | -                                   | File path of the Deep Q-Learning model if using "dql" agent.                                                                                                  |
| `--rounds`              | int  | -1                             | -                                   | Number of rounds to play. -1 indicate infinite round.                                                                                                         |
| `--max_frame_iteration` | int  | 0                              | -                                   | Use to detect trapping. 0 indicate auto detect, -1 to turn off detection.                                                                                     |

### Example
```bash
# simplest command
python game.py

# specify game speed, agent and map file
python game.py --game_speed 30 --agent distance --map_file "./map/simple_map.txt"

# One Step Ahead Distance Decision agent
python game.py --rounds 2 --agent distance --map_file "./map/GOL_45.txt"

# Breadth-first search agent
python game.py --rounds 2 --agent bfs --map_file "./map/GOL_45.txt"

# Deep Q-Learning agent
python game.py --rounds 2 --agent dql --model_file "./model/2023_01_12_175446.pt" --map_file "./map/GOL_45.txt"
```

## Deep Q-Learning Training
Run `python train_ai.py` with following arguments (Ctrl + C for force quit):

| Arg                   | Type | Default                | Choices | Description                                                                                                                         |
| --------------------- | ---- | ---------------------- | ------- | ----------------------------------------------------------------------------------------------------------------------------------- |
| `--map_height`        | int  | 36                     | -       | Set height of the blank map if not using any map from map file.                                                                     |
| `--map_width`         | int  | 36                     | -       | Set width of the blank map if not using any map from map file.                                                                      |
| `--map_file`          | str  | "./map/simple_map.txt" | -       | Load map from map file. <br> Pass "" empty string to use blank map.                                                                 |
| `--game_speed`        | int  | 120                    | -       | Control min FPS of the game.                                                                                                        |
| `--render_block_size` | int  | 5                      | -       | Game rendering size. Higher value bigger screen.                                                                                    |
| `--output_model_file` | str  | ""                     | -       | Output file path of the Deep Q-Learning model training. "" empty string for auto file naming according to the datetime.             |
| `--load_model_file`   | str  | ""                     | -       | Pretrained model loading file path of the Deep Q-Learning. For fine tuning purpose. "" empty string to not fine tuning any model. |
| `--rounds`            | int  | -1                     | -       | Number of rounds to play. -1 indicate infinite round.                                                                               |

### Example
```bash
# simplest command
python train_ai.py

# Training from scratch
python train_ai.py --output_model_file "./model/custom_model.pt" --map_file "./map/GOL_45.txt"

# Fine tuning
python train_ai.py --output_model_file "./model/tuned_model.pt" --load_model_file "./model/2023_01_12_175446.pt" --map_file "./map/CPU_45.txt"
```

## Map Generation
Run any of the Jupyter notebook files under `./map_generator` to generate specific map.