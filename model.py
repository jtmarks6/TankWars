import pygame


class Ball:
    def __init__(self, surface: pygame.Surface) -> None:
        radius = 15

        self.centerx, self.centery = radius * 2, surface.get_height() / 2
        self.radius = radius
        self.surface = surface
        self.green = 0, 255, 0
        self.velocity = [.3, .3]
        self.left = self.centerx - radius
        self.right = self.centerx + radius
        self.top = self.centery - radius
        self.bottom = self.centery + radius

    def move(self, delta_time: float, keys: list[bool]):
        self.centerx += self.velocity[0] * delta_time
        self.centery += self.velocity[1] * delta_time

        self.left = self.centerx - self.radius
        self.right = self.centerx + self.radius
        self.top = self.centery - self.radius
        self.bottom = self.centery + self.radius

    def draw(self):
        pygame.draw.circle(self.surface, self.green, (self.centerx, self.centery), self.radius)

    def bounce(self, x: bool = False, y: bool = False):
        if x:
            self.velocity[0] *= -1

        if y:
            self.velocity[1] *= -1


class Paddle:
    def __init__(self, surface: pygame.Surface, up_key, down_key, player1: bool =  True) -> None:
        width, height = 30, 150
        x_pos, y_pos = (0, 0) if player1 else (surface.get_width() - width, 0)

        self.paddle_speed = .5
        self.white = 255, 255, 255
        self.paddle = pygame.Rect(x_pos, y_pos, width, height)
        self.surface = surface
        self.up = up_key
        self.down = down_key

    def move(self, delta_time: float, keys: list[bool]):
        if keys[self.up] and self.paddle.top > 0:
            self.paddle.move_ip(0, -self.paddle_speed * delta_time)
        elif keys[self.down] and self.paddle.bottom < self.surface.get_height():
            self.paddle.move_ip(0, self.paddle_speed * delta_time)

    def draw(self):
        pygame.draw.rect(self.surface, self.white, self.paddle)

class Score:
    def __init__(self, surface: pygame.Surface, player1: bool =  True) -> None:
        self.font = pygame.font.Font('freesansbold.ttf', 32)
        self.score = 0
        self.green = 0, 255, 0
        self.surface = surface
        self.text = self.font.render(str(self.score), True, self.green)
        self.textRect = self.text.get_rect()
        self.textRect.centerx = (surface.get_width() // 2)
        if player1:
            self.textRect.centerx -= 150
        else:
            self.textRect.centerx += 150

    def increment(self):
        self.score += 1
        self.text = self.font.render(str(self.score), True, self.green)

    def draw(self):
        self.surface.blit(self.text, self.textRect)
