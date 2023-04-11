import pygame
import random

SURFACE_COLOR = (233, 204, 149)

SCREEN_WIDTH = 736
SCREEN_HEIGHT = 544
TANK_SPEED = 4
BOARD_WIDTH = 23
BOARD_HEIGHT = 17
BULLET_SPEED = 8

BITS = 32
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
        row = [False] * BOARD_WIDTH
        self.board = []
        for _ in range(BOARD_HEIGHT):
            self.board.append(row.copy())

        size = (SCREEN_WIDTH, SCREEN_HEIGHT)
        self.screen = pygame.display.set_mode(size)
        self.screen.fill(SURFACE_COLOR)
        pygame.display.set_caption("Tank Wars")

    def generate_walls(self, board: list[list[bool]], walls: pygame.sprite.Group):
        for j in range(len(board[0])):
            board[0][j] = True

        for j in range(len(board[0])):
            board[-1][j] = True

        for i in range(len(board)):
            board[i][0] = True

        for i in range(len(board)):
            board[i][-1] = True

        wall_probability = [0, 0, 0, 0, 0, 0, 0, 0, 0, 1]
        for i in range(len(board)):
            for j in range(len(board[0])):
                if wall_probability[random.randint(0, 9)]:
                    board[i][j] = True

        # TODO combine close walls and connect some random ones

        for i in range(len(board)):
            for j in range(len(board[0])):
                if board[i][j]:
                    walls.add(self.model.Wall(j * BITS, i * BITS))

    def start(self):
        # gen walls each round
        # set new bgd with walls
        # create new player tank and enemy tanks
        # loop until level is done

        bgd = self.screen.copy()
        self.walls.draw(self.screen)
        player1 = self.model.Player_Tank(BITS, BITS, TANK_SPEED, BULLET_SPEED, self.bullets)
        self.player_tanks.add(player1)
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
            self.view.draw_game(self.screen, bgd, self.sprites)
            clock.tick(FPS)

        pygame.quit()
