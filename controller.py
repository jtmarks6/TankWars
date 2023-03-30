import pygame
import sys
import time
from model import *
from view import *

class Pong:
    def __init__(self) -> None:
        pygame.init()
        pygame.display.set_caption("Pong")
        screen_size = self.width, self.height = 800, 500

        self.surface = pygame.display.set_mode(screen_size, flags=pygame.SCALED, vsync=1)
        self.ball = Ball(self.surface)
        self.paddle1 = Paddle(self.surface, pygame.K_w, pygame.K_s)
        self.paddle2 = Paddle(self.surface, pygame.K_UP, pygame.K_DOWN, False)
        self.player1Score = Score(self.surface, True)
        self.player2Score = Score(self.surface, False)
        self.objects = [self.ball, self.paddle1, self.paddle2]
        self.objectsToRender = [self.ball, self.paddle1, self.paddle2, self.player1Score, self.player2Score]
        self.bouncing = False
        self.last_time = time.time() * 1000

    def startGame(self):
        while True:
            game_time  = time.time() * 1000
            if(game_time - self.last_time < 1000/60):
                continue

            for event in pygame.event.get():
                if event.type == pygame.QUIT: sys.exit()

            keys = pygame.key.get_pressed()
            delta_time = game_time - self.last_time
            for i, obj in enumerate(self.objects):
                obj.move(delta_time, keys)

            if self.ball.left < 0:
                self.player2Score.increment()
                self.ball.bounce(x=True)
            elif self.ball.right > self.width:
                self.player1Score.increment()
                self.ball.bounce(x=True)
                
            if self.ball.left <= self.paddle1.paddle.right and self.paddle1.paddle.bottom >= self.ball.centery and self.ball.centery >= self.paddle1.paddle.top:
                if not self.bouncing:
                    self.bouncing = True
                    self.ball.bounce(x=True)
            elif self.ball.right >= self.paddle2.paddle.left and self.paddle2.paddle.bottom >= self.ball.centery and self.ball.centery >= self.paddle2.paddle.top:
                if not self.bouncing:
                    self.bouncing = True
                    self.ball.bounce(x=True)
            elif self.ball.top < 0 or self.ball.bottom > self.height:
                    self.ball.bounce(y=True)
            else:
                self.bouncing = False

            update_display(self.surface, self.objectsToRender)

            if self.player1Score.score >= 5 or self.player2Score.score >= 5:
                sys.exit()
                
            self.last_time = game_time
