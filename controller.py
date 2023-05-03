import pygame
import random
import path_finding

from model import (EMPTY, WALL, TANK, BOMB, BITS, BoardCell)

MENU_COLOR = (66, 155, 219)
FONT_COLOR = (12, 21, 56)
SURFACE_COLOR = (233, 204, 149)

SCREEN_WIDTH = 736
SCREEN_HEIGHT = 544
TANK_SPEED = 2
ENEMY_TANK_SPEED = 1
BOARD_WIDTH = 23
BOARD_HEIGHT = 17
BULLET_SPEED = 5
MAX_BULLETS = 4

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
        self.bombs = pygame.sprite.Group()
        self.sprites = [self.walls, self.enemy_tanks, self.bullets, self.bombs, self.player_tanks]
        self.player_pos = ()
        self.level = 0
        self.level_duration = 0
        self.menu = True
        self.font = pygame.font.Font('freesansbold.ttf', 32)

        # Create 2d array for board
        row = [BoardCell(EMPTY, None)] * BOARD_WIDTH
        self.board = []
        for _ in range(BOARD_HEIGHT):
            self.board.append(row.copy())

        size = (SCREEN_WIDTH, SCREEN_HEIGHT)
        self.screen = pygame.display.set_mode(size)
        self.screen.fill(SURFACE_COLOR)
        pygame.display.set_caption("Tank Wars")
        self.bgd = self.screen

    def generate_walls(self, board: list[list[BoardCell]], walls: pygame.sprite.Group):
        for j in range(1, len(board[0]) - 1):
            wall = self.model.Wall(j * BITS, 0 * BITS)
            board[0][j] = BoardCell(WALL, wall)
            walls.add(wall)

        for j in range(1, len(board[0]) - 1):
            wall = self.model.Wall(j * BITS, (len(board) - 1) * BITS)
            board[-1][j] = BoardCell(WALL, wall)
            walls.add(wall)

        for i in range(len(board)):
            wall = self.model.Wall(0 * BITS, i * BITS)
            board[i][0] = BoardCell(WALL, wall)
            walls.add(wall)

        for i in range(len(board)):
            wall = self.model.Wall((len(board[0]) - 1) * BITS, i * BITS)
            board[i][-1] = BoardCell(WALL, wall)
            walls.add(wall)

        for _ in range(random.randint(1, 5)):
            start_x = random.randrange(1, BOARD_WIDTH - 1)
            start_y = random.randrange(1, BOARD_HEIGHT - 1)
            while board[start_y][start_x].status != EMPTY:
                start_x = random.randrange(1, BOARD_WIDTH - 1)
                start_y = random.randrange(1, BOARD_HEIGHT - 1)

            goal_x = random.randrange(1, BOARD_WIDTH - 1)
            goal_y = random.randrange(1, BOARD_HEIGHT - 1)
            while board[goal_y][goal_x].status != EMPTY:
                goal_x = random.randrange(1, BOARD_WIDTH - 1)
                goal_y = random.randrange(1, BOARD_HEIGHT - 1)
            path = path_finding.a_star_no_wall_avoidance(self.board, (start_x, start_y), (goal_x, goal_y))
            if path:
                for cell in path:
                    i = cell[1]
                    j = cell[0]
                    if board[i][j].status == EMPTY:
                        wall = self.model.Wall(j * BITS, i * BITS)
                        board[i][j] = BoardCell(WALL, wall)
                        walls.add(wall)

        for i in range(len(board)):
            for j in range(len(board[0])):
                if random.random() > .95 and board[i][j].status == EMPTY:
                    wall = self.model.Wall(j * BITS, i * BITS)
                    board[i][j] = BoardCell(WALL, wall)
                    walls.add(wall)


    def generate_new_level(self):
        row = [BoardCell(EMPTY, None)] * BOARD_WIDTH
        for i in range(BOARD_HEIGHT):
            self.board[i] = row.copy()

        self.walls.empty()
        self.player_tanks.empty()
        self.enemy_tanks.empty()
        self.bullets.empty()
        self.bombs.empty()

        self.screen.fill(SURFACE_COLOR)
        self.bgd = self.screen.copy()
        
        self.level_duration = 0

        self.player_tanks.add(self.model.Player_Tank(random.randrange(1, BOARD_WIDTH - 1) * BITS, random.randrange(1, BOARD_HEIGHT - 1) * BITS, TANK_SPEED, BULLET_SPEED, MAX_BULLETS, self.bullets, self.board, self.bombs))
        for _ in range((self.level % 6) + 1):
            enemy_x = random.randrange(1, BOARD_WIDTH - 1)
            enemy_y = random.randrange(1, BOARD_HEIGHT - 1)
            while self.board[enemy_y][enemy_x].status != EMPTY:
                enemy_x = random.randrange(1, BOARD_WIDTH - 1)
                enemy_y = random.randrange(1, BOARD_HEIGHT - 1)

            self.enemy_tanks.add(self.model.Enemy_Tank(enemy_x * BITS, enemy_y * BITS, ENEMY_TANK_SPEED, BULLET_SPEED, MAX_BULLETS, self.bullets, self.board))

        self.generate_walls(self.board, self.walls)
        self.level += 1

    def start(self):
        exit = True
        clock = pygame.time.Clock()

        background_sound = pygame.mixer.Sound('assets/background.wav')
        pygame.mixer.Sound.play(background_sound, -1)

        while exit:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    exit = False

            if self.menu:
                self.view.draw_menu(self.screen, MENU_COLOR, FONT_COLOR, self.font, self.level)
                keys = pygame.key.get_pressed()
                if keys[pygame.K_RETURN]:
                    self.menu = False
                    self.screen.fill(SURFACE_COLOR)
                    self.level = 0
                    self.generate_new_level()
            else:
                if len(self.player_tanks.sprites()) == 0:
                    self.menu = True

                if len(self.enemy_tanks.sprites()) == 0:
                    self.generate_new_level()

                self.level_duration += 1

                mouse_pressed = pygame.mouse.get_pressed()
                keys = pygame.key.get_pressed()

                self.player_tanks.update(keys, mouse_pressed, self.walls)
                for tank in self.player_tanks:
                    self.player_pos = tank.get_pos()
                self.enemy_tanks.update(self.player_pos, self.walls, self.level_duration, self.enemy_tanks)
                self.bullets.update(self.player_tanks, self.enemy_tanks)
                self.bombs.update()
                self.view.draw_game(self.screen, self.bgd, self.sprites)

            clock.tick(FPS)

        pygame.quit()
