import pygame

# GLOBAL VARIABLES
COLOR = (0, 0, 0)
RED = (255, 0, 0)
SURFACE_COLOR = (0, 0, 0)
SCREEN_WIDTH = 500
SCREEN_HEIGHT = 500
TANK_WIDTH = 500
TANK_HEIGHT = 500

# Object class
class Tank(pygame.sprite.Sprite):
    def __init__(self, color: tuple, width: int, height: int, speed: int):
        super().__init__()

        self.image = pygame.Surface([width, height])
        self.image.fill(SURFACE_COLOR)
        # self.image.set_colorkey(COLOR)
        self.speed = speed

        # pygame.draw.rect(self.image, color, pygame.Rect(0, 0, width, height))

        self.rect = self.image.get_rect()
        self.rect.x = 10
        self.rect.y = 10
	
    def update(self, keys: list[bool], mouse_pressed: list[bool], all_sprites_list: list):
        if mouse_pressed[0]: #TODO add debounce and bullet counter
            all_sprites_list.add(Bullet((0, 255, 0), 5, 5, self.rect.x, self.rect.y, 5))

        if keys[pygame.K_w]:
            self.rect = self.rect.move(0, -self.speed)

        if keys[pygame.K_s]:
            self.rect = self.rect.move(0, self.speed)

        if keys[pygame.K_a]:
            self.rect = self.rect.move(-self.speed, 0)

        if keys[pygame.K_d]:
            self.rect = self.rect.move(self.speed, 0)


class Bullet(pygame.sprite.Sprite):
    def __init__(self, color: tuple, height: int, width: int, x: int, y: int, speed: int):
        super().__init__()

        self.image = pygame.Surface([width, height])
        self.image.fill(SURFACE_COLOR)
        # self.image.set_colorkey(COLOR)
        self.speed = speed
        mouse_x, mouse_y = pygame.mouse.get_pos()
        self.movement_vector = mouse_x - x, mouse_y - y

        pygame.draw.rect(self.image, color, pygame.Rect(0, 2, width, height))

        self.rect = self.image.get_rect()
	
    def update(self, *args):
        pass
        # self.rect = self.rect.move(self.movement_vector[0]/self.speed, self.movement_vector[1]/self.speed)
        

pygame.init()

size = (SCREEN_WIDTH, SCREEN_HEIGHT)
screen = pygame.display.set_mode(size)
bgd = screen.copy()
pygame.display.set_caption("Tank Wars")

all_sprites_list = pygame.sprite.Group()

player1 = Tank(RED, 20, 30, 5)

all_sprites_list.add(player1)

exit = True
clock = pygame.time.Clock()

while exit:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            exit = False

    mouse_pressed = pygame.mouse.get_pressed()
    keys = pygame.key.get_pressed()

    all_sprites_list.update(keys, mouse_pressed, all_sprites_list)
    # all_sprites_list.clear(screen, bgd)
    updates = all_sprites_list.draw(screen)
    pygame.display.update()
    clock.tick(60)

pygame.quit()
