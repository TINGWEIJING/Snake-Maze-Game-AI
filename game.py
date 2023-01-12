import pygame
from agent.bfs import BFSController
from agent.deep_q import DeepQController
from agent.simple_bot import DistanceController

from game_mechanic.mechanic import Direction, GameState

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

    def __init__(self,
                 game_state: GameState,
                 controller: DistanceController = None,
                 render_block_size: int = 10,
                 game_speed: int = 120,
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

        self.game_window = pygame.display.set_mode((self.window_width, self.window_height))
        self.fps = pygame.time.Clock()

    def run(self):
        input_direction = self.game_state.snake_player.curr_direction
        print(input_direction)
        while True:
            # * Game Control
            if self.controller == None:
                input_direction = self.get_keyboard_control_input(input_direction)
            else:
                input_direction = self.controller.compute_next_direction()

            # * Game Logic
            self.game_state.snake_make_next_move(input_direction=input_direction)
            self.game_state.process_action()
            self.game_state.spawn_fruit()
            is_game_over = self.game_state.check_game_over()

            # * Rendering
            self.render()

            # * Game Over Checking
            if is_game_over:
                print(f"SCORE: {game_state.score}")
                # game_over(game_state.score)
                game_state.reset_game()
                if self.controller != None:
                    self.controller.reset(game_state=self.game_state)
                input_direction = game_state.snake_player.curr_direction
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
        self.game_window.blit(score_surface, score_rect)

    def game_over(self,
                  score: int):
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
        pygame.time.wait(1000)
        self.game_window.fill(BLACK_CLR)

        # deactivating pygame library
        # pygame.quit()

        # quit the program
        # quit()
        pass


if __name__ == "__main__":
    game_state = GameState(
        map_height=36,
        map_width=36,
        map_file='./map/dummy_map.txt',
    )
    game_gui = GameGUI(
        game_state=game_state,
        # game_speed=30,
        controller=DeepQController(game_state=game_state, model_file_name='./model/2023_01_12_172229.pt'),
        # controller=BFSController(game_state=game_state),
        # controller=DistanceController(game_state=game_state),
    )
    game_gui.run()
