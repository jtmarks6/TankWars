import pygame
import random
from model import (EMPTY, WALL, TANK, BOMB, BITS)

SURFACE_COLOR = (233, 204, 149)

SCREEN_WIDTH = 736
SCREEN_HEIGHT = 544
TANK_SPEED = 4
BOARD_WIDTH = 23
BOARD_HEIGHT = 17
BULLET_SPEED = 8
MAX_BULLETS = 2

FPS = 60

class TankWarsController():
    def __init__(self, model, view):
        pygame.init()

        self.model = model
        self.view = view
        self.player_tanks = pygame.sprite.Group()
        self.enemy_tanks = pygame.sprite.Group()
        self.walls = pygame.sprite.Group()
        self.bullets = pygame.sprite.Group()
        self.sprites = [self.player_tanks, self.enemy_tanks, self.walls, self.bullets]

        # Create 2d array for board
        row = [EMPTY] * BOARD_WIDTH
        self.board = []
        for _ in range(BOARD_HEIGHT):
            self.board.append(row.copy())

        size = (SCREEN_WIDTH, SCREEN_HEIGHT)
        self.screen = pygame.display.set_mode(size)
        self.screen.fill(SURFACE_COLOR)
        pygame.display.set_caption("Tank Wars")

    def generate_walls(self, board: list[list[bool]], walls: pygame.sprite.Group):
        for j in range(len(board[0])):
            board[0][j] = WALL

        for j in range(len(board[0])):
            board[-1][j] = WALL

        for i in range(len(board)):
            board[i][0] = WALL

        for i in range(len(board)):
            board[i][-1] = WALL

        wall_probability = [0, 0, 0, 0, 0, 0, 0, 0, 0, 1]
        for i in range(len(board)):
            for j in range(len(board[0])):
                if wall_probability[random.randint(0, 9)] and board[i][j] == EMPTY:
                    board[i][j] = WALL

        # TODO combine close walls and connect some random ones

        for i in range(len(board)):
            for j in range(len(board[0])):
                if board[i][j] == WALL:
                    walls.add(self.model.Wall(j * BITS, i * BITS))

    def start(self):
        # gen walls each round
        # set new bgd with walls
        # create new player tank and enemy tanks
        # loop until level is done

        bgd = self.screen.copy()
        self.walls.draw(self.screen)
        self.player_tanks.add(self.model.Player_Tank(random.randrange(1, BOARD_WIDTH) * BITS, random.randrange(1, BOARD_HEIGHT) * BITS, TANK_SPEED, BULLET_SPEED, MAX_BULLETS, self.bullets, self.board))
        self.generate_walls(self.board, self.walls)

        exit = True
        clock = pygame.time.Clock()

        while exit:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    exit = False

            mouse_pressed = pygame.mouse.get_pressed()
            keys = pygame.key.get_pressed()

            self.player_tanks.update(keys, mouse_pressed, self.walls)
            self.bullets.update(self.player_tanks, self.enemy_tanks)
            self.view.draw_game(self.screen, bgd, self.sprites)
            clock.tick(FPS)

        pygame.quit()
