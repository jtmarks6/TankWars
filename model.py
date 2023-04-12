import pygame

BITS = 32

EMPTY = 0
WALL = 1
TANK = 2
BOMB = 3

class Player_Tank(pygame.sprite.Sprite):
    def __init__(self, x: int, y: int, speed: int, bullet_speed: int, max_bullets: int, bullets: pygame.sprite.Group, board: list[list[int]]):
        super().__init__()

        self.image = pygame.image.load('assets/tank.png')
        self.speed = speed
        self.bullets = bullets
        self.shot_bullets = pygame.sprite.Group()
        self.bullet_speed = bullet_speed
        self.max_bullets = max_bullets
        self.debounce = False
        self.rect = self.image.get_rect()
        self.board = board
        self.last_board_pos = (x // BITS, y // BITS)

        self.rect.x = x
        self.rect.y = y
        self.board[y // BITS][x // BITS] = TANK

    def update(self, keys: list[bool], mouse_pressed: list[bool], walls: pygame.sprite.Group):
        if mouse_pressed[0]:
            if not self.debounce and len(self.shot_bullets.sprites()) < self.max_bullets:
                bullet = Bullet(self.rect.x + (BITS / 2), self.rect.y + (BITS / 2), self.bullet_speed, walls)
                self.shot_bullets.add(bullet)
                self.bullets.add(bullet)
                self.debounce = True
        else:
            self.debounce = False

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
        
        x_index = self.rect.x // BITS
        y_index = self.rect.y // BITS
        if (x_index, y_index) != self.last_board_pos:
            self.board[self.last_board_pos[1]][self.last_board_pos[0]] = EMPTY
            self.board[y_index][x_index] = TANK
            self.last_board_pos = (x_index, y_index)

class Bullet(pygame.sprite.Sprite): # TODO fix rounded slope to be float
    def __init__(self, x: int, y: int, speed: int, walls: pygame.sprite.Group):
        super().__init__()

        self.image = pygame.image.load('assets/bullet.png')
        self.speed = speed
        mouse_x, mouse_y = pygame.mouse.get_pos()
        self.movement_vector = mouse_x - x, mouse_y - y
        self.bounces = 0
        self.walls = walls
        self.rect = self.image.get_rect()

        self.rect.x = x
        self.rect.y = y

    def update(self, player_tanks: pygame.sprite.Group, enemy_tanks: pygame.sprite.Group):
        x = (self.movement_vector[0]/(((self.movement_vector[0] ** 2) + (self.movement_vector[1] ** 2)) ** .5)) * self.speed
        y = (self.movement_vector[1]/(((self.movement_vector[0] ** 2) + (self.movement_vector[1] ** 2)) ** .5)) * self.speed
        self.rect = self.rect.move(x, y)

        # pygame.sprite.spritecollide(self, player_tanks, True)
        pygame.sprite.spritecollide(self, enemy_tanks, True)

        wall_collide_list = pygame.sprite.spritecollide(self, self.walls, False)
        for wall in wall_collide_list:
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
    def __init__(self, x: int, y: int):
        super().__init__()

        self.image = pygame.image.load('assets/wall.png')

        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
