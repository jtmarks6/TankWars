import pygame
import random

BITS = 32

class Player_Tank(pygame.sprite.Sprite):
    def __init__(self, x: int, y: int, speed: int, bullet_speed: int):
        super().__init__()

        self.image = pygame.image.load('assets/tank.png')
        self.speed = speed

        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.bullets = pygame.sprite.Group()
        self.bullet_speed = bullet_speed

    def update(self, keys: list[bool], mouse_pressed: list[bool]):
        if mouse_pressed[0]:  # TODO add debounce and bullet counter
            self.bullets.add(Bullet(self.rect.x + (BITS / 2), self.rect.y + (BITS / 2), self.bullet_speed))

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
        
        self.bullets.update()

class Bullet(pygame.sprite.Sprite): # TODO fix rounded slope to be float
    def __init__(self, x: int, y: int, speed: int):
        super().__init__()

        self.image = pygame.image.load('assets/bullet.png')
        self.speed = speed
        mouse_x, mouse_y = pygame.mouse.get_pos()
        self.movement_vector = mouse_x - x, mouse_y - y
        self.bounces = 0

        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    def update(self):
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
    def __init__(self, x: int, y: int):
        super().__init__()

        self.image = pygame.image.load('assets/wall.png')

        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
