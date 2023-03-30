import pygame

black = 0, 0, 0

def update_display(surface: pygame.Surface, objects: list):
    surface.fill(black)

    for obj in objects:
        obj.draw()

    pygame.display.update()
