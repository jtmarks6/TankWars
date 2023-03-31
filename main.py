import pygame
import random

TANK_COLOR = (28, 116, 155)
WALL_COLOR = (206, 157, 98)
SURFACE_COLOR = (233, 204, 149)
BULLET_COLOR = (128, 111, 92)

SCREEN_WIDTH = 736
SCREEN_HEIGHT = 544
TANK_WIDTH = 500
TANK_HEIGHT = 500
TANK_SPEED = 4
BOARD_WIDTH = 23
BOARD_HEIGHT = 17
BULLET_WIDTH = 4
BULLET_HEIGHT = 4
BULLET_SPEED = 8

BITS = 32
FPS = 60


def distance_between(x1: float, x2: float, y1: float, y2: float) -> float:
    return (abs(y2 - y1) ** 2 + abs(x1 - x2) ** 2) ** .5


class Player_Tank(pygame.sprite.Sprite):
    def __init__(self, color: tuple, width: int, height: int, x: int, y: int, speed: int):
        super().__init__()

        # self.image = pygame.Surface([width, height])
        self.image = pygame.image.load('assets/tank.png')
        # self.image.set_colorkey(COLOR)
        self.speed = speed

        # pygame.draw.rect(self.image, color, pygame.Rect(0, 0, width, height))

        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    def update(self, keys: list[bool], mouse_pressed: list[bool], player_tanks: list):
        if mouse_pressed[0]:  # TODO add debounce and bullet counter
            player_tanks.add(Bullet(BULLET_COLOR, BULLET_WIDTH, BULLET_HEIGHT,
                             self.rect.x + 16, self.rect.y + 16, BULLET_SPEED))

        if keys[pygame.K_w]:
            self.rect = self.rect.move(0, -self.speed)
            if pygame.sprite.spritecollideany(self, walls):
                self.rect = self.rect.move(0, self.speed)

        if keys[pygame.K_s]:
            self.rect = self.rect.move(0, self.speed)
            if pygame.sprite.spritecollideany(self, walls):
                self.rect = self.rect.move(0, -self.speed)

        if keys[pygame.K_a]:
            self.rect = self.rect.move(-self.speed, 0)
            if pygame.sprite.spritecollideany(self, walls):
                self.rect = self.rect.move(self.speed, 0)

        if keys[pygame.K_d]:
            self.rect = self.rect.move(self.speed, 0)
            if pygame.sprite.spritecollideany(self, walls):
                self.rect = self.rect.move(-self.speed, 0)


class Bullet(pygame.sprite.Sprite):
    def __init__(self, color: tuple, width: int, height: int, x: int, y: int, speed: int):
        super().__init__()

        # self.image = pygame.Surface([width, height])
        # self.image.fill(color)
        # self.image.set_colorkey(COLOR)
        self.image = pygame.image.load('assets/bullet.png')
        self.speed = speed
        mouse_x, mouse_y = pygame.mouse.get_pos()
        self.movement_vector = mouse_x - x, mouse_y - y
        self.bounces = 0

        # pygame.draw.rect(self.image, color, pygame.Rect(0, 0, width, height))

        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    def update(self, *args):
        x = (self.movement_vector[0]/(((self.movement_vector[0] **
             2) + (self.movement_vector[1] ** 2)) ** .5)) * self.speed
        y = (self.movement_vector[1]/(((self.movement_vector[0] **
             2) + (self.movement_vector[1] ** 2)) ** .5)) * self.speed
        self.rect = self.rect.move(x, y)

        collide_list = pygame.sprite.spritecollide(self, walls, False)
        for wall in collide_list:
            if self.bounces > 0:
                self.kill()
            else:
                collided_side = sorted([
                    (abs(self.rect.right - wall.rect.left), "left"),
                    (abs(self.rect.left - wall.rect.right), "right"),
                    (abs(self.rect.bottom - wall.rect.top), "top"),
                    (abs(self.rect.top - wall.rect.bottom), "bottom"),
                ])[0][1]

                # TODO consider higher resolution to fix clipping through corners bug

                self.bounces += 1
                if collided_side == "left":
                    self.movement_vector = self.movement_vector[0] * - \
                        1, self.movement_vector[1]
                    self.rect.right = wall.rect.left
                elif collided_side == "right":
                    self.movement_vector = self.movement_vector[0] * - \
                        1, self.movement_vector[1]
                    self.rect.left = wall.rect.right
                elif collided_side == "top":
                    self.movement_vector = self.movement_vector[0], self.movement_vector[1] * -1
                    self.rect.bottom = wall.rect.top
                else:
                    self.movement_vector = self.movement_vector[0], self.movement_vector[1] * -1
                    self.rect.top = wall.rect.bottom


class Wall(pygame.sprite.Sprite):
    def __init__(self, color: tuple, width: int, height: int, x: int, y: int):
        super().__init__()

        # self.image = pygame.Surface([width, height])
        self.image = pygame.image.load('assets/wall.png')

        # pygame.draw.rect(self.image, color, pygame.Rect(0, 0, width, height))

        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y


def generate_walls(board: list[list[bool]], walls: pygame.sprite.Group):
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
                walls.add(Wall(WALL_COLOR, BITS, BITS, j * BITS, i * BITS))


pygame.init()

player_tanks = pygame.sprite.Group()
enemy_tanks = pygame.sprite.Group()
walls = pygame.sprite.Group()
bullets = pygame.sprite.Group()
row = [False] * BOARD_WIDTH
board = []
for i in range(BOARD_HEIGHT):
    board.append(row.copy())

generate_walls(board, walls)

size = (SCREEN_WIDTH, SCREEN_HEIGHT)
screen = pygame.display.set_mode(size)
screen.fill(SURFACE_COLOR)
walls.draw(screen)
bgd = screen.copy()
pygame.display.set_caption("Tank Wars")

player1 = Player_Tank(TANK_COLOR, BITS, BITS, BITS, BITS, TANK_SPEED)
player_tanks.add(player1)

exit = True
clock = pygame.time.Clock()


while exit:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            exit = False

    mouse_pressed = pygame.mouse.get_pressed()
    keys = pygame.key.get_pressed()

    player_tanks.update(keys, mouse_pressed, player_tanks)

    player_tanks.clear(screen, bgd)
    player_tanks.draw(screen)
    pygame.display.update()
    clock.tick(FPS)

pygame.quit()
