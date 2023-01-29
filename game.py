import pygame

from agent.bfs import BFSController
from agent.deep_q import DeepQController
from agent.simple_bot import DistanceController
from game_mechanic.mechanic import Direction, GameState
from param import get_parser

# defining colors
BLACK_CLR = pygame.Color(0, 0, 0)
WHITE_CLR = pygame.Color(255, 255, 255)
RED_CLR = pygame.Color(255, 0, 0)
GREEN_CLR = pygame.Color(0, 255, 0)
BLUE_CLR = pygame.Color(0, 0, 255)
GOLD_CLR = pygame.Color(255, 215, 0)


class GameGUI:
    map_height: int
    map_width: int
    render_block_size: int
    game_speed: int
    window_width: int
    window_height: int
    game_window: pygame.Surface
    fps: pygame.time.Clock

    game_state: GameState
    controller: DistanceController
    max_round: int
    curr_round: int

    def __init__(self,
                 game_state: GameState,
                 controller: DistanceController = None,
                 render_block_size: int = 10,
                 game_speed: int = 120,
                 max_round: int = -1,
                 ) -> None:
        pygame.init()
        pygame.display.set_caption('Snake Maze Game')

        self.game_state = game_state
        self.controller = controller

        self.map_height = game_state.map_height
        self.map_width = game_state.map_width
        self.render_block_size = render_block_size
        self.game_speed = game_speed
        self.window_height = self.map_height * self.render_block_size
        self.window_width = self.map_width * self.render_block_size

        self.max_round = max_round
        self.curr_round = 0

        self.game_window = pygame.display.set_mode((self.window_width, self.window_height))
        self.fps = pygame.time.Clock()

    def run(self):
        input_direction = self.game_state.snake_player.curr_direction
        while True:
            # * Game Control
            input_direction = self.get_keyboard_control_input(input_direction)
            if self.controller != None:
                input_direction = self.controller.compute_next_direction()

            # * Game Logic
            self.game_state.snake_make_next_move(input_direction=input_direction)
            self.game_state.process_action()
            self.game_state.spawn_fruit()
            is_game_over = self.game_state.check_game_over()

            # * Post Trace
            self.controller.post_processing()

            # * Rendering
            self.render()

            # * Game Over Checking
            if is_game_over:
                print(f"ROUND: {self.curr_round} SCORE: {self.game_state.score}")
                print(f"frame: {self.game_state.frame_iteration}")
                self.game_over(game_state.score)
                # game_over(game_state.score)
                self.game_state.reset_game()
                if self.controller != None:
                    self.controller.reset(game_state=self.game_state)
                input_direction = self.game_state.snake_player.curr_direction
                pygame.event.clear()

            # Refresh game screen
            pygame.display.update()

            # Frame Per Second /Refresh Rate
            self.fps.tick(self.game_speed)

    def render(self):
        # * Rendering
        self.game_window.fill(BLACK_CLR)

        # render white wall
        for coord_y, coord_x in self.game_state.wall_coords:
            pygame.draw.rect(self.game_window,
                             WHITE_CLR,
                             pygame.Rect(
                                 coord_x * self.render_block_size,
                                 coord_y * self.render_block_size,
                                 self.render_block_size,
                                 self.render_block_size)
                             )

        # render snake tail
        for coord in self.game_state.snake_player.tail_coords:
            pygame.draw.rect(self.game_window, GREEN_CLR,
                             pygame.Rect(coord[1] * self.render_block_size, coord[0] * self.render_block_size, self.render_block_size, self.render_block_size))
        snake_head_coord = self.game_state.snake_player.head_coord
        # render snake head
        pygame.draw.rect(self.game_window, RED_CLR,
                         pygame.Rect(snake_head_coord[1] * self.render_block_size, snake_head_coord[0] * self.render_block_size, self.render_block_size, self.render_block_size))
        # render fruit
        pygame.draw.rect(self.game_window,
                         GOLD_CLR,
                         pygame.Rect(
                             self.game_state.fruit_coord[1] * self.render_block_size,
                             self.game_state.fruit_coord[0] * self.render_block_size,
                             self.render_block_size,
                             self.render_block_size)
                         )
        # displaying score countinuously
        self.show_score(self.game_state.score, WHITE_CLR, 'times new roman', int(20 * (self.render_block_size / 10)))

    def get_keyboard_control_input(self, default_direction: Direction):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    return Direction.LEFT
                elif event.key == pygame.K_RIGHT:
                    return Direction.RIGHT
                elif event.key == pygame.K_UP:
                    return Direction.UP
                elif event.key == pygame.K_DOWN:
                    return Direction.DOWN

        return default_direction

    def show_score(self,
                   score: int,
                   color,
                   font,
                   size):
        # creating font object score_font
        score_font = pygame.font.SysFont(font, size)
        # create the display surface object
        # score_surface
        score_surface = score_font.render('Score : ' + str(score), True, color)
        # create a rectangular object for the text
        # surface object
        score_rect = score_surface.get_rect()
        # displaying text
        # self.game_window.blit(score_surface, score_rect)
        self.game_window.blit(score_surface, (1 * self.render_block_size, 1 * self.render_block_size))

    def game_over(self,
                  score: int):
        self.curr_round += 1

        # creating font object my_font
        my_font = pygame.font.SysFont('times new roman', 50)

        # creating a text surface on which text
        # will be drawn
        game_over_surface = my_font.render(
            'Your Score is : ' + str(score), True, RED_CLR)

        # create a rectangular object for the text
        # surface object
        game_over_rect = game_over_surface.get_rect()

        # setting position of the text
        game_over_rect.midtop = (self.window_width/2, self.window_height/4)

        # blit will draw the text on screen
        self.game_window.blit(game_over_surface, game_over_rect)
        pygame.display.flip()

        # after 1 seconds we will quit the program
        # time.sleep(1)
        pygame.time.wait(5)
        self.game_window.fill(BLACK_CLR)

        if self.curr_round >= self.max_round and self.max_round >= 0:
            # deactivating pygame library
            pygame.quit()

            # quit the program
            quit()


if __name__ == "__main__":
    parser = get_parser()
    args = parser.parse_args()
    map_height: int = args.map_height
    map_width: int = args.map_width
    map_file: str = args.map_file
    game_speed: int = args.game_speed
    render_block_size: int = args.render_block_size
    agent: str = args.agent
    model_file: str = args.model_file
    rounds: int = args.rounds
    max_frame_iteration: int = args.max_frame_iteration

    # * Print args
    print("="*20)
    print(f"map_height: {map_height}")
    print(f"map_width: {map_width}")
    print(f"map_file: {map_file}")
    print(f"game_speed: {game_speed}")
    print(f"render_block_size: {render_block_size}")
    print(f"agent: {agent}")
    print(f"model_file: {model_file}")
    print(f"rounds: {rounds}")
    print(f"max_frame_iteration: {max_frame_iteration}")
    print("="*20)

    game_state = GameState(
        map_height=map_height,
        map_width=map_width,
        map_file=map_file,
        max_frame_iteration=max_frame_iteration,
    )

    # * Select controller
    if agent == "distance":
        controller = DistanceController(game_state=game_state)
    elif agent == "bfs":
        controller = BFSController(game_state=game_state)
    elif agent == "dql":
        controller = DeepQController(game_state=game_state, model_file_name=model_file)
    else:
        controller = None

    game_gui = GameGUI(
        game_state=game_state,
        game_speed=game_speed,
        controller=controller,
        render_block_size=render_block_size,
        max_round=rounds
    )
    game_gui.run()
