import pygame
import random
from model import (EMPTY, WALL, TANK, BOMB, BITS)

SURFACE_COLOR = (233, 204, 149)

SCREEN_WIDTH = 736
SCREEN_HEIGHT = 544
TANK_SPEED = 3
ENEMY_TANK_SPEED = 2
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
        self.player_pos = ()

        # Create 2d array for board
        row = [EMPTY] * BOARD_WIDTH
        self.board = []
        for _ in range(BOARD_HEIGHT):
            self.board.append(row.copy())

        size = (SCREEN_WIDTH, SCREEN_HEIGHT)
        self.screen = pygame.display.set_mode(size)
        self.screen.fill(SURFACE_COLOR)
        pygame.display.set_caption("Tank Wars")
        self.bgd = self.screen

    def generate_walls(self, board: list[list[bool]], walls: pygame.sprite.Group):
        for j in range(len(board[0])):
            board[0][j] = WALL

        for j in range(len(board[0])):
            board[-1][j] = WALL

        for i in range(len(board)):
            board[i][0] = WALL

        for i in range(len(board)):
            board[i][-1] = WALL

        for i in range(len(board)):
            for j in range(len(board[0])):
                if random.random() > .9 and board[i][j] == EMPTY:
                    board[i][j] = WALL

        # TODO combine close walls and connect some random ones

        for i in range(len(board)):
            for j in range(len(board[0])):
                if board[i][j] == WALL:
                    walls.add(self.model.Wall(j * BITS, i * BITS))

    def generate_new_level(self):
        row = [EMPTY] * BOARD_WIDTH
        for i in range(BOARD_HEIGHT):
            self.board[i] = row.copy()

        self.walls.empty()
        self.player_tanks.empty()
        self.enemy_tanks.empty()
        self.bullets.empty()

        self.screen.fill(SURFACE_COLOR)
        self.bgd = self.screen.copy()

        self.player_tanks.add(self.model.Player_Tank(random.randrange(1, BOARD_WIDTH - 1) * BITS, random.randrange(1, BOARD_HEIGHT - 1) * BITS, TANK_SPEED, BULLET_SPEED, MAX_BULLETS, self.bullets, self.board))
        for _ in range(random.randint(1,1)): # TODO choose number of tanks range with wave number
            enemy_x = random.randrange(1, BOARD_WIDTH - 1)
            enemy_y = random.randrange(1, BOARD_HEIGHT - 1)
            while self.board[enemy_y][enemy_x] != EMPTY:
                enemy_x = random.randrange(1, BOARD_WIDTH - 1)
                enemy_y = random.randrange(1, BOARD_HEIGHT - 1)

            self.enemy_tanks.add(self.model.Enemy_Tank(enemy_x * BITS, enemy_y * BITS, ENEMY_TANK_SPEED, BULLET_SPEED, MAX_BULLETS, self.bullets, self.board))

        self.generate_walls(self.board, self.walls)

    def start(self):
        exit = True
        clock = pygame.time.Clock()

        while exit:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    exit = False

            if len(self.enemy_tanks.sprites()) == 0 or len(self.player_tanks.sprites()) == 0:
                self.generate_new_level()

            mouse_pressed = pygame.mouse.get_pressed()
            keys = pygame.key.get_pressed()

            self.player_tanks.update(keys, mouse_pressed, self.walls, self.enemy_tanks, self.screen)
            for tank in self.player_tanks:
                self.player_pos = tank.get_pos()
            self.enemy_tanks.update(self.player_pos, self.walls, self.screen)
            self.bullets.update(self.player_tanks, self.enemy_tanks)
            self.view.draw_game(self.screen, self.bgd, self.sprites)
            clock.tick(FPS)

        pygame.quit()
