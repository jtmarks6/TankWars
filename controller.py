import pygame
from model import *
from view import *

SURFACE_COLOR = (233, 204, 149)

SCREEN_WIDTH = 736
SCREEN_HEIGHT = 544
TANK_SPEED = 4
BOARD_WIDTH = 23
BOARD_HEIGHT = 17
BULLET_SPEED = 8

BITS = 32
FPS = 60

pygame.init()

player_tanks = pygame.sprite.Group()
enemy_tanks = pygame.sprite.Group()
walls = pygame.sprite.Group()
bullets = pygame.sprite.Group()

row = [False] * BOARD_WIDTH
board = []
for _ in range(BOARD_HEIGHT):
    board.append(row.copy())
del row

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
                walls.add(Wall(j * BITS, i * BITS))

generate_walls(board, walls)

size = (SCREEN_WIDTH, SCREEN_HEIGHT)
screen = pygame.display.set_mode(size)
screen.fill(SURFACE_COLOR)
walls.draw(screen)
bgd = screen.copy()
pygame.display.set_caption("Tank Wars")

player1 = Player_Tank(BITS, BITS, TANK_SPEED, BULLET_SPEED)
player_tanks.add(player1)

exit = True
clock = pygame.time.Clock()


while exit:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            exit = False

    mouse_pressed = pygame.mouse.get_pressed()
    keys = pygame.key.get_pressed()

    player_tanks.update(keys, mouse_pressed)
    draw_game()
    clock.tick(FPS)

pygame.quit()
