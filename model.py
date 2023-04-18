import pygame
import path_finding
import math
from raycast import *

BITS = 32

EMPTY = 0
WALL = 1
TANK = 2
BOMB = 3

RIGHT_ANGLE = 270
UP_ANGLE = 0
LEFT_ANGLE = 90
DOWN_ANGLE = 180

class Player_Tank(pygame.sprite.Sprite):
    def __init__(self, x: int, y: int, speed: int, bullet_speed: int, max_bullets: int, bullets: pygame.sprite.Group, board: list[list[int]]):
        super().__init__()

        self.original_image = pygame.image.load('assets/tank.png').convert_alpha()
        self.image = self.original_image
        self.mask = pygame.mask.from_surface(self.image)
        self.speed = speed
        self.bullets = bullets
        self.shot_bullets = pygame.sprite.Group()
        self.bullet_speed = bullet_speed
        self.max_bullets = max_bullets
        self.debounce = False
        self.rect = self.image.get_rect()
        self.board = board
        self.last_board_pos = (x // BITS, y // BITS)
        self.angle = 0

        self.rect.x = x
        self.rect.y = y
        self.board[y // BITS][x // BITS] = TANK

    def update(self, keys: list[bool], mouse_pressed: list[bool], walls: pygame.sprite.Group, enemy_tanks: pygame.sprite.Group, screen):
        if mouse_pressed[0]: # TODO use https://www.reddit.com/r/gamedev/comments/lovizf/angle_between_player_and_target_in_degrees/ to animate
            if not self.debounce and len(self.shot_bullets.sprites()) < self.max_bullets:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                x = self.rect.x + (BITS / 2)
                y = self.rect.y + (BITS / 2)
                movement_vector = pygame.math.Vector2(mouse_x - x, mouse_y - y)
                bullet = Bullet(x, y, movement_vector, self.bullet_speed, walls, self)
                self.shot_bullets.add(bullet)
                self.bullets.add(bullet)
                self.debounce = True
        else:
            self.debounce = False

        dx = 0
        dy = 0
        if keys[pygame.K_w] ^ keys[pygame.K_s]:
            if keys[pygame.K_w]:
                dy = -self.speed
            elif keys[pygame.K_s]:
                dy = self.speed

        elif keys[pygame.K_a] ^ keys[pygame.K_d]:
            if keys[pygame.K_a]:
                dx = -self.speed
            elif keys[pygame.K_d]:
                dx = self.speed

        if dy or dx:
            direction = math.atan2(dy, dx)
            angle = math.degrees(-direction) - 90
            old_center = self.rect.center
            self.image = pygame.transform.rotate(self.original_image, angle)
            self.rect = self.image.get_rect(center=old_center)
            new_center = self.rect.center
            dx += old_center[0] - new_center[0]
            dy += old_center[1] - new_center[1]
        
        if dx:
            movement_vector = pygame.math.Vector2(dx, 0)
            movement_vector.normalize_ip()
            movement_vector *= self.speed
            next_position = self.rect.move(movement_vector)

            collision = raycast(self.rect, next_position, movement_vector, walls)
            if collision:
                pygame.draw.circle(screen, (0,0,255), collision.point, 2)
                movement_vector = pygame.math.Vector2(dx, 0)
                movement_vector.normalize_ip()
                movement_vector *= int(collision.distance)
                next_position = self.rect.move(movement_vector)
            
            self.rect = next_position
                
        if dy: # left corner doesn't line up when going down
            movement_vector = pygame.math.Vector2(0, dy)
            movement_vector.normalize_ip()
            movement_vector *= self.speed
            next_position = self.rect.move(movement_vector)

            collision = raycast(self.rect, next_position, movement_vector, walls)
            if collision:
                pygame.draw.circle(screen, (0,0,255), collision.point, 2)
                movement_vector = pygame.math.Vector2(0, dy)
                movement_vector.normalize_ip()
                movement_vector *= int(collision.distance)
                next_position = self.rect.move(movement_vector)

            self.rect = next_position

        if dx or dy:
            x_index = self.rect.x // BITS
            y_index = self.rect.y // BITS
            if (x_index, y_index) != self.last_board_pos:
                self.board[self.last_board_pos[1]][self.last_board_pos[0]] = EMPTY
                self.board[y_index][x_index] = TANK
                self.last_board_pos = (x_index, y_index)
                if self.board[y_index][x_index] == 1 or pygame.sprite.spritecollideany(self, walls):
                    for row in self.board:
                        print(row)
                    print("")
    
    def get_pos(self) -> tuple:
        return self.rect

class Enemy_Tank(pygame.sprite.Sprite):
    def __init__(self, x: int, y: int, speed: int, bullet_speed: int, max_bullets: int, bullets: pygame.sprite.Group, board: list[list[int]]):
        super().__init__()

        self.original_image = pygame.image.load('assets/enemy_tank.png')
        self.image = self.original_image
        self.speed = speed
        self.bullets = bullets
        self.shot_bullets = pygame.sprite.Group()
        self.bullet_speed = bullet_speed
        self.max_bullets = max_bullets
        self.debounce = False
        self.rect = self.image.get_rect()
        self.board = board
        self.last_board_pos = (x // BITS, y // BITS)
        self.angle = 0
        self.path = []
        self.path_index = 0
        self.last_player_board_pos = ()
        self.cooldown = 0

        self.rect.x = x
        self.rect.y = y
        self.board[y // BITS][x // BITS] = TANK

    def update(self, player_pos: tuple, walls: pygame.sprite.Group, screen):
        player_board_pos = (player_pos[0] // 32, player_pos[1] // 32)

        def find_path():
            start_pos = (self.rect.x // BITS, self.rect.y // BITS)
            adjacent_cells = {
                (player_board_pos[0] + 1, player_board_pos[1]),
                (player_board_pos[0] - 1, player_board_pos[1]),
                (player_board_pos[0], player_board_pos[1] + 1),
                (player_board_pos[0], player_board_pos[1] - 1),
            }
            goal = adjacent_cells.pop()
            # for row in self.board:
            #     print(row)
            # print("")
            while self.board[goal[1]][goal[0]] != 0:
                if not adjacent_cells:
                    return
                
                goal = adjacent_cells.pop()

            if goal:
                self.path = path_finding.a_star(self.board, start_pos, goal)
                self.path_index = 0
                self.last_player_board_pos = player_board_pos
                # print(player_pos, self.path)

        if self.path and self.path_index < len(self.path):
            target_cell = self.path[self.path_index]
            target_x = target_cell[0] * BITS
            target_y = target_cell[1] * BITS
            
            # Calculate the direction to move in
            dx = target_x - self.rect.x
            dy = target_y - self.rect.y
            dist = math.sqrt(dx ** 2 + dy ** 2)
            
            if dist > self.speed:
                # Move towards the target
                direction = math.atan2(dy, dx)
                self.rect.x += math.cos(direction) * self.speed
                self.rect.y += math.sin(direction) * self.speed

                angle = math.degrees(-direction) - 90
                self.image = pygame.transform.rotate(self.original_image, angle)
                self.rect = self.image.get_rect(center=self.rect.center)
            else:
                # Move to the next cell in the path
                self.rect.x = target_x
                self.rect.y = target_y
                self.path_index += 1
                if player_board_pos != self.last_player_board_pos:
                    find_path()


                x_index = self.rect.x // BITS
                y_index = self.rect.y // BITS
                if (x_index, y_index) != self.last_board_pos:
                    self.board[self.last_board_pos[1]][self.last_board_pos[0]] = EMPTY
                    self.board[y_index][x_index] = TANK
                    self.last_board_pos = (x_index, y_index)
        else:
            find_path() # TODO if tank is not visible

        enemy_tank_center = self.rect.center
        ray_to_player_x = player_pos[0] - enemy_tank_center[0]
        ray_to_player_y = player_pos[1] - enemy_tank_center[1]

        movement_vector =pygame.math.Vector2(ray_to_player_x, ray_to_player_y)
        print(movement_vector)
        next_position = self.rect.move(movement_vector)
        collision = raycast(self.rect, next_position, movement_vector, walls)
        if collision:
            pygame.draw.circle(screen, (255,0,0), collision.point, 2)

        if not collision and self.cooldown <= 0 and len(self.shot_bullets.sprites()) < self.max_bullets:
            bullet = Bullet(self.rect.x + (BITS / 2), self.rect.y + (BITS / 2), movement_vector, self.bullet_speed, walls, self)
            self.shot_bullets.add(bullet)
            self.bullets.add(bullet)
            self.cooldown = 120
        else:
            if self.cooldown > 0:
                self.cooldown -= 1

    def kill(self):
        pygame.sprite.Sprite.kill(self)
        self.board[self.last_board_pos[1]][self.last_board_pos[0]] = EMPTY

class Bullet(pygame.sprite.Sprite): # TODO fix rounded slope to be float
    def __init__(self, x: int, y: int, movement_vector: pygame.math.Vector2, speed: int, walls: pygame.sprite.Group, parent: pygame.sprite):
        super().__init__()

        self.image = pygame.image.load('assets/bullet.png')
        self.speed = speed
        self.movement_vector = movement_vector
        self.bounces = 0
        self.walls = walls
        self.rect = self.image.get_rect()
        self.parent = parent

        self.rect.x = x
        self.rect.y = y

    def update(self, player_tanks: pygame.sprite.Group, enemy_tanks: pygame.sprite.Group):
        movement_vector = pygame.math.Vector2(self.movement_vector)
        movement_vector.normalize_ip()
        movement_vector *= self.speed
        next_position = self.rect.move(movement_vector)

        collision = raycast(self.rect, next_position, movement_vector, player_tanks)
        if collision and collision.sprite != self.parent:
            collision.sprite.kill()
            self.kill()

        collision = raycast(self.rect, next_position, movement_vector, enemy_tanks)
        if collision and collision.sprite != self.parent:
            collision.sprite.kill()
            self.kill()

        collision = raycast(self.rect, next_position, movement_vector, self.walls)
        if collision:
            if self.bounces > 0:
                self.kill()
            else:
                self.bounces += 1
                movement_vector = pygame.math.Vector2(self.movement_vector)
                movement_vector.normalize_ip()
                movement_vector *= collision.distance
                next_position = self.rect.move(movement_vector)

                if collision.side == LEFT_SIDE or collision.side == RIGHT_SIDE:
                    self.movement_vector = self.movement_vector[0] * -1, self.movement_vector[1]
                else:
                    self.movement_vector = self.movement_vector[0], self.movement_vector[1] * -1

        self.rect = next_position

class Wall(pygame.sprite.Sprite):
    def __init__(self, x: int, y: int):
        super().__init__()

        self.image = pygame.image.load('assets/wall.png')

        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
