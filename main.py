import time

import pygame

from mechanic import Direction, GameState
from simple_bot import DistanceController

# initialize map representation
MAP_HEIGHT = 200  # Y
MAP_WIDTH = 200  # X
RENDER_BLOCK_SIZE = 10

GAME_SPEED = 120  # FPS

# Window size
WINDOW_WIDTH = MAP_WIDTH * RENDER_BLOCK_SIZE
WINDOM_HEIGHT = MAP_HEIGHT * RENDER_BLOCK_SIZE

# defining colors
BLACK_CLR = pygame.Color(0, 0, 0)
WHITE_CLR = pygame.Color(255, 255, 255)
RED_CLR = pygame.Color(255, 0, 0)
GREEN_CLR = pygame.Color(0, 255, 0)
BLUE_CLR = pygame.Color(0, 0, 255)
GOLD_CLR = pygame.Color(255, 215, 0)

# Initialising pygame
pygame.init()

# Initialise game window
pygame.display.set_caption('Snake Maze Game')
# GAME_WINDOM = pygame.display.set_mode((WINDOW_WIDTH, WINDOM_HEIGHT))
GAME_WINDOM = None

# FPS (frames per second) controller
FPS = pygame.time.Clock()


def show_score(score: int,
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
    GAME_WINDOM.blit(score_surface, score_rect)


def game_over(score: int):
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
    game_over_rect.midtop = (WINDOW_WIDTH/2, WINDOM_HEIGHT/4)

    # blit will draw the text on screen
    GAME_WINDOM.blit(game_over_surface, game_over_rect)
    pygame.display.flip()

    # after 1 seconds we will quit the program
    # time.sleep(1)
    pygame.time.wait(1000)
    GAME_WINDOM.fill(BLACK_CLR)

    # deactivating pygame library
    # pygame.quit()

    # quit the program
    # quit()


if __name__ == "__main__":
    # Main Function
    game_state = GameState(
        map_height=MAP_HEIGHT,
        map_width=MAP_WIDTH,
        map_file='./map/dummy_map.txt',
    )
    controller = DistanceController(game_state=game_state)
    input_direction = game_state.snake_player.curr_direction

    WINDOW_WIDTH = game_state.map_width * RENDER_BLOCK_SIZE
    WINDOM_HEIGHT = game_state.map_height * RENDER_BLOCK_SIZE
    GAME_WINDOM = pygame.display.set_mode((WINDOW_WIDTH, WINDOM_HEIGHT))

    while True:
        # * Game Control
        # handling key events
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    input_direction = Direction.UP
                if event.key == pygame.K_DOWN:
                    input_direction = Direction.DOWN
                if event.key == pygame.K_LEFT:
                    input_direction = Direction.LEFT
                if event.key == pygame.K_RIGHT:
                    input_direction = Direction.RIGHT

        input_direction = controller.compute_next_direction()

        # * Game Logic
        game_state.snake_make_next_move(input_direction=input_direction)
        game_state.process_action()
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

        # * Game Over Checking
        if game_state.check_game_over():
            game_over(game_state.score)
            game_state.reset_game()
            input_direction = game_state.snake_player.curr_direction
            pygame.event.clear()

        # displaying score countinuously
        show_score(game_state.score, WHITE_CLR, 'times new roman', 20)

        # Refresh game screen
        pygame.display.update()

        # Frame Per Second /Refresh Rate
        FPS.tick(GAME_SPEED)
