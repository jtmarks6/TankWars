import pygame

def draw_menu(screen: pygame.Surface, MENU_COLOR: tuple, FONT_COLOR: tuple, font: pygame.font, level: int):
    screen.fill(MENU_COLOR)    
    title = font.render('Tank Wars', True, FONT_COLOR, MENU_COLOR)
    textRect = title.get_rect()
    textRect.center = (screen.get_width() // 2, screen.get_height() // 4)
    screen.blit(title, textRect)

    instructions = font.render('Press Enter to Start', True, FONT_COLOR, MENU_COLOR)
    instructionsRect = instructions.get_rect()
    instructionsRect.center = (screen.get_width() // 2, screen.get_height() // 2)
    screen.blit(instructions, instructionsRect)

    if level > 0:
        level = font.render(f'Survived: {level}', True, FONT_COLOR, MENU_COLOR)
        levelRect = level.get_rect()
        levelRect.center = (screen.get_width() // 2, (screen.get_height() // 4) * 3)
        screen.blit(level, levelRect)

    pygame.display.update()

def draw_game(screen: pygame.Surface, bgd: pygame.Surface, sprites: list[pygame.sprite.Group]):
    for group in sprites:
        group.clear(screen, bgd)
        group.draw(screen)

    pygame.display.update()
