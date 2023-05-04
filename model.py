import pygame
import path_finding
import math
from raycast import *

BoardCell = namedtuple('BoardCell', ['status', 'sprite'])

BITS = 32

EMPTY = 0
WALL = 1
TANK = 2
BOMB = 3


class Player_Tank(pygame.sprite.Sprite):
    def __init__(self, x: int, y: int, speed: int, bullet_speed: int, max_bullets: int, bullets: pygame.sprite.Group, board: list[list[BoardCell]], bombs: pygame.sprite.Group):
        super().__init__()

        self.original_image = pygame.image.load(
            'assets/tank.png').convert_alpha()
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
        self.bombs = bombs
        self.dropped_bombs = pygame.sprite.Group()
        self.moving_y = False

        self.rect.x = x
        self.rect.y = y
        self.board[y // BITS][x // BITS] = BoardCell(TANK, self)

    def update(self, keys: list[bool], mouse_pressed: list[bool], walls: pygame.sprite.Group):
        if mouse_pressed[0]:
            if not self.debounce and len(self.shot_bullets.sprites()) < self.max_bullets:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                x = self.rect.centerx
                y = self.rect.centery
                movement_vector = pygame.math.Vector2(mouse_x - x, mouse_y - y)
                bullet = Bullet(x, y, movement_vector,
                                self.bullet_speed, walls, self)
                self.shot_bullets.add(bullet)
                self.bullets.add(bullet)
                self.debounce = True
        else:
            self.debounce = False

        if keys[pygame.K_SPACE] and len(self.dropped_bombs) == 0:
            bomb = Bomb(self.rect.centerx, self.rect.centery, 120, self.board)
            self.bombs.add(bomb)
            self.dropped_bombs.add(bomb)

        old_center = self.rect.center

        if keys[pygame.K_w] ^ keys[pygame.K_s]:
            if keys[pygame.K_w]:
                self.rect = self.rect.move(0, -self.speed)
                collisions = pygame.sprite.spritecollide(self, walls, False)
                if collisions:
                    self.rect.top = collisions[0].rect.bottom
            elif keys[pygame.K_s]:
                self.rect = self.rect.move(0, self.speed)
                collisions = pygame.sprite.spritecollide(self, walls, False)
                if collisions:
                    self.rect.bottom = collisions[0].rect.top

        elif keys[pygame.K_a] ^ keys[pygame.K_d]:
            if keys[pygame.K_a]:
                self.rect = self.rect.move(-self.speed, 0)
                collisions = pygame.sprite.spritecollide(self, walls, False)
                if collisions:
                    self.rect.left = collisions[0].rect.right
            elif keys[pygame.K_d]:
                self.rect = self.rect.move(self.speed, 0)
                collisions = pygame.sprite.spritecollide(self, walls, False)
                if collisions:
                    self.rect.right = collisions[0].rect.left

        dx = self.rect.centerx - old_center[0]
        dy = self.rect.centery - old_center[1]

        if dy or dx:
            direction = math.atan2(dy, dx)
            angle = math.degrees(-direction) - 90
            old_center = self.rect.center
            self.image = pygame.transform.rotate(self.original_image, angle)
            self.rect = self.image.get_rect(center=old_center)
            new_center = self.rect.center
            dx += old_center[0] - new_center[0]
            dy += old_center[1] - new_center[1]

        if dx or dy:
            x_index = self.rect.x // BITS
            y_index = self.rect.y // BITS
            if (x_index, y_index) != self.last_board_pos:
                self.board[self.last_board_pos[1]
                           ][self.last_board_pos[0]] = BoardCell(EMPTY, None)
                self.board[y_index][x_index] = BoardCell(TANK, self)
                self.last_board_pos = (x_index, y_index)

    def get_pos(self) -> tuple:
        return self.rect


class Enemy_Tank(pygame.sprite.Sprite):
    def __init__(self, x: int, y: int, speed: int, bullet_speed: int, max_bullets: int, bullets: pygame.sprite.Group, board: list[list[BoardCell]]):
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
        self.board[y // BITS][x // BITS] = BoardCell(TANK, self)

    def update(self, player_pos: pygame.rect, walls: pygame.sprite.Group, level_duration: int, enemy_tanks: pygame.sprite.Group):
        player_board_pos = (player_pos.centerx // 32, player_pos.centery // 32)

        def find_path():
            start_pos = (self.rect.x // BITS, self.rect.y // BITS)
            adjacent_cells = {
                (player_board_pos[0] + 1, player_board_pos[1]),
                (player_board_pos[0] - 1, player_board_pos[1]),
                (player_board_pos[0], player_board_pos[1] + 1),
                (player_board_pos[0], player_board_pos[1] - 1),
            }
            goal = adjacent_cells.pop()
            while self.board[goal[1]][goal[0]].status != 0:
                if not adjacent_cells:
                    return

                goal = adjacent_cells.pop()

            if goal:
                self.path = path_finding.a_star(self.board, start_pos, goal)
                self.path_index = 0
                self.last_player_board_pos = player_board_pos

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
                self.image = pygame.transform.rotate(
                    self.original_image, angle)
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
                    self.board[self.last_board_pos[1]
                               ][self.last_board_pos[0]] = BoardCell(EMPTY, None)
                    self.board[y_index][x_index] = BoardCell(TANK, self)
                    self.last_board_pos = (x_index, y_index)
        else:
            ray_to_player_x = player_pos.centerx - self.rect.centerx
            ray_to_player_y = player_pos.centery - self.rect.centery

            movement_vector = pygame.math.Vector2(
                ray_to_player_x, ray_to_player_y)
            test_bullet = pygame.Rect(
                self.rect.centerx, self.rect.centery, 4, 4)
            next_position = test_bullet.move(movement_vector)
            collision = raycast(test_bullet, next_position,
                                movement_vector, walls)
            if collision or level_duration < 120:
                find_path()

        ray_to_player_x = player_pos.centerx - self.rect.centerx
        ray_to_player_y = player_pos.centery - self.rect.centery

        movement_vector = pygame.math.Vector2(ray_to_player_x, ray_to_player_y)
        test_bullet = pygame.Rect(self.rect.centerx, self.rect.centery, 4, 4)
        next_position = test_bullet.move(movement_vector)
        wall_collision = raycast(
            test_bullet, next_position, movement_vector, walls)
        enemy_tank_collision = raycast(
            test_bullet, next_position, movement_vector, enemy_tanks)

        # if level_duration > 120 and not wall_collision and not enemy_tank_collision and self.cooldown <= 0 and len(self.shot_bullets.sprites()) < self.max_bullets:
        #     bullet = Bullet(self.rect.centerx, self.rect.centery, movement_vector, self.bullet_speed, walls, self)
        #     self.shot_bullets.add(bullet)
        #     self.bullets.add(bullet)
        #     self.cooldown = 120
        # else:
        #     if self.cooldown > 0:
        #         self.cooldown -= 1

    def kill(self):
        kill_sound = pygame.mixer.Sound('assets/tank_kill.mp3')
        kill_sound.set_volume(.60)
        pygame.mixer.Sound.play(kill_sound)
        pygame.sprite.Sprite.kill(self)
        self.board[self.last_board_pos[1]
                   ][self.last_board_pos[0]] = BoardCell(EMPTY, None)


class Bullet(pygame.sprite.Sprite):  # TODO fix rounded slope to be float
    def __init__(self, x: int, y: int, movement_vector: pygame.math.Vector2, speed: int, walls: pygame.sprite.Group, parent: pygame.sprite):
        super().__init__()

        self.image = pygame.image.load('assets/bullet.png')
        self.speed = speed
        self.movement_vector = movement_vector
        self.bounces = 0
        self.walls = walls
        self.rect = self.image.get_rect()
        self.parent = parent
        self.x = x
        self.y = y

        self.rect.x = x
        self.rect.y = y
        self.bullet_hit_sound = pygame.mixer.Sound('assets/bullet_hit.wav')

    def update(self, player_tanks: pygame.sprite.Group, enemy_tanks: pygame.sprite.Group):
        movement_vector = pygame.math.Vector2(self.movement_vector)
        if movement_vector.length() != 0:
            movement_vector.normalize_ip()
        movement_vector *= self.speed
        next_position = self.rect.move(movement_vector)
        self.x += movement_vector.x
        self.y += movement_vector.y

        collision = raycast(self.rect, next_position,
                            movement_vector, player_tanks)
        if collision and collision.sprite != self.parent:
            pygame.mixer.Sound.play(self.bullet_hit_sound)
            collision.sprite.kill()
            self.kill()

        collision = raycast(self.rect, next_position,
                            movement_vector, enemy_tanks)
        if collision and collision.sprite != self.parent:
            pygame.mixer.Sound.play(self.bullet_hit_sound)
            collision.sprite.kill()
            self.kill()

        collision = raycast(self.rect, next_position,
                            movement_vector, self.walls)
        if collision:
            if self.bounces > 0:
                pygame.mixer.Sound.play(self.bullet_hit_sound)
                self.kill()
            else:
                self.bounces += 1
                movement_vector = pygame.math.Vector2(self.movement_vector)
                if movement_vector.length() != 0:
                    movement_vector.normalize_ip()
                movement_vector *= collision.distance
                next_position = self.rect.move(movement_vector)
                self.x = next_position.x
                self.y = next_position.y

                if collision.side == LEFT_SIDE or collision.side == RIGHT_SIDE:
                    self.movement_vector = self.movement_vector[0] * - \
                        1, self.movement_vector[1]
                else:
                    self.movement_vector = self.movement_vector[0], self.movement_vector[1] * -1

        self.rect.x = self.x
        self.rect.y = self.y


class Wall(pygame.sprite.Sprite):
    def __init__(self, x: int, y: int):
        super().__init__()

        self.image = pygame.image.load('assets/wall.png')
        self.rect = self.image.get_rect()

        self.rect.x = x
        self.rect.y = y


class Bomb(pygame.sprite.Sprite):
    def __init__(self, x: int, y: int, fuse_time: int, board: list[list[BoardCell]]):
        super().__init__()

        self.image = pygame.image.load('assets/bomb.png')
        self.fuse = fuse_time
        self.rect = self.image.get_rect()
        self.board = board
        self.x = x // BITS
        self.y = y // BITS

        self.rect.x = self.x * BITS
        self.rect.y = self.y * BITS
        self.bomb_sound = pygame.mixer.Sound('assets/bomb.mp3')

    def update(self):  # TODO walls sometimes don't break
        if self.fuse == 0:
            pygame.mixer.Sound.play(self.bomb_sound)
            if self.x + 1 < len(self.board[0]) - 1:
                if self.board[self.y][self.x + 1].status != EMPTY:
                    self.board[self.y][self.x + 1].sprite.kill()
                    self.board[self.y][self.x + 1] = BoardCell(EMPTY, None)

                if self.y + 1 < len(self.board) - 1 and self.board[self.y + 1][self.x + 1].status != EMPTY:
                    self.board[self.y + 1][self.x + 1].sprite.kill()
                    self.board[self.y + 1][self.x + 1] = BoardCell(EMPTY, None)

                if self.y - 1 >= 1 and self.board[self.y - 1][self.x + 1].status != EMPTY:
                    self.board[self.y - 1][self.x + 1].sprite.kill()
                    self.board[self.y - 1][self.x + 1] = BoardCell(EMPTY, None)

            if self.x - 1 >= 1:
                if self.board[self.y][self.x - 1].status != EMPTY:
                    self.board[self.y][self.x - 1].sprite.kill()
                    self.board[self.y][self.x - 1] = BoardCell(EMPTY, None)

                if self.y + 1 < len(self.board) - 1 and self.board[self.y + 1][self.x - 1].status != EMPTY:
                    self.board[self.y + 1][self.x - 1].sprite.kill()
                    self.board[self.y + 1][self.x - 1] = BoardCell(EMPTY, None)

                if self.y - 1 >= 1 and self.board[self.y - 1][self.x - 1].status != EMPTY:
                    self.board[self.y - 1][self.x - 1].sprite.kill()
                    self.board[self.y - 1][self.x - 1] = BoardCell(EMPTY, None)

            if self.y + 1 < len(self.board) - 1 and self.board[self.y + 1][self.x].status != EMPTY:
                self.board[self.y + 1][self.x].sprite.kill()
                self.board[self.y + 1][self.x] = BoardCell(EMPTY, None)

            if self.y - 1 >= 1 and self.board[self.y - 1][self.x].status != EMPTY:
                self.board[self.y - 1][self.x].sprite.kill()
                self.board[self.y - 1][self.x] = BoardCell(EMPTY, None)

            if self.board[self.y][self.x].status != EMPTY:
                self.board[self.y][self.x].sprite.kill()
                self.board[self.y][self.x] = BoardCell(EMPTY, None)

            self.kill()
        else:
            self.fuse -= 1
