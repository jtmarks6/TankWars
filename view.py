import pygame

def draw_game(screen: pygame.Surface, bgd: pygame.Surface, sprites: list[pygame.sprite.Group]):
    for group in sprites:
        group.clear(screen, bgd)
        group.draw(screen)

    pygame.display.update()
