import math
import pygame

from typing import Optional
from collections import namedtuple

LEFT_SIDE = 0
RIGHT_SIDE = 1
TOP_SIDE = 2
BOTTOM_SIDE = 3

Collision = namedtuple('Collision', ['point', 'distance', 'side', 'sprite'])
Point = namedtuple('Point', ['x', 'y'])

def intersection_point(m1, b1, m2, b2) -> Point:
    if m1 == float('inf'):  # first line is vertical
        x = b1
        y = m2 * x + b2
    elif m2 == float('inf'):  # second line is vertical
        x = b2
        y = m1 * x + b1
    else:  # neither line is vertical
        x = (b2 - b1) / (m1 - m2)
        y = m1 * x + b1

    return Point(x, y)

def raycast(start_pos: pygame.rect, end_pos: pygame.rect, movement_vector: pygame.math.Vector2, sprites: pygame.sprite.Group) -> Optional[Collision]:
    left = True if movement_vector.x > 0 else False
    right = True if movement_vector.x < 0 else False
    top = True if movement_vector.y > 0 else False
    bottom = True if movement_vector.y < 0 else False
    if movement_vector.x == 0:  # vertical movement
        slope = float('inf')
    else:
        slope = movement_vector.y / movement_vector.x
    closest_collision = None
    min_distance = float('inf')

    for sprite in sprites:
        left_side = sprite.rect.left
        right_side = sprite.rect.right
        top_side = sprite.rect.top
        bottom_side = sprite.rect.bottom

        # Left side check
        if left and left_side >= start_pos.left and left_side <= end_pos.right:
            start_point = start_pos.topright
            b = start_point[1] - slope * start_point[0] if slope != float('inf') else start_point[1]
            collision = intersection_point(slope, b, float('inf'), left_side)
            if collision.y > bottom_side or collision.y < top_side:
                collision = None
            
            if not collision:
                start_point = start_pos.topleft
                b = start_point[1] - slope * start_point[0]
                collision = intersection_point(slope, b, float('inf'), left_side)
                if collision.y > bottom_side or collision.y < top_side:
                    collision = None

            if not collision:
                start_point = start_pos.bottomright
                b = start_point[1] - slope * start_point[0]
                collision = intersection_point(slope, b, float('inf'), left_side)
                if collision.y > bottom_side or collision.y < top_side:
                    collision = None

            if not collision:
                start_point = start_pos.bottomleft
                b = start_point[1] - slope * start_point[0]
                collision = intersection_point(slope, b, float('inf'), left_side)
                if collision.y > bottom_side or collision.y < top_side:
                    collision = None

            if collision:
                distance = math.sqrt((collision.x - start_point[0])**2 + (collision.y - start_point[1])**2)
                if distance < min_distance:
                    closest_collision = Collision(collision, distance, LEFT_SIDE, sprite)
                    min_distance = distance

        # Right side check
        if right and right_side <= start_pos.right and right_side >= end_pos.left:
            start_point = start_pos.topleft
            b = start_point[1] - slope * start_point[0]
            collision = intersection_point(slope, b, float('inf'), right_side)
            if collision.y > bottom_side or collision.y < top_side:
                collision = None
            
            if not collision:
                start_point = start_pos.topright
                b = start_point[1] - slope * start_point[0]
                collision = intersection_point(slope, b, float('inf'), right_side)
                if collision.y > bottom_side or collision.y < top_side:
                    collision = None

            if not collision:
                start_point = start_pos.bottomleft
                b = start_point[1] - slope * start_point[0]
                collision = intersection_point(slope, b, float('inf'), right_side)
                if collision.y > bottom_side or collision.y < top_side:
                    collision = None

            if not collision:
                start_point = start_pos.bottomright
                b = start_point[1] - slope * start_point[0]
                collision = intersection_point(slope, b, float('inf'), right_side)
                if collision.y > bottom_side or collision.y < top_side:
                    collision = None

            if collision:
                distance = math.sqrt((collision.x - start_point[0])**2 + (collision.y - start_point[1])**2)
                if distance < min_distance:
                    closest_collision = Collision(collision, distance, RIGHT_SIDE, sprite)
                    min_distance = distance

        # Top side check
        if top and top_side >= start_pos.top and top_side <= end_pos.bottom:
            start_point = start_pos.bottomright
            b = start_point[1] - slope * start_point[0]
            collision = intersection_point(slope, b, 0, top_side)
            if collision.x < left_side or collision.x > right_side:
                collision = None
            
            if not collision:
                start_point = start_pos.topright
                b = start_point[1] - slope * start_point[0]
                collision = intersection_point(slope, b, 0, top_side)
                if collision.x < left_side or collision.x > right_side:
                    collision = None

            if not collision:
                start_point = start_pos.topleft
                b = start_point[1] - slope * start_point[0]
                collision = intersection_point(slope, b, 0, top_side)
                if collision.x < left_side or collision.x > right_side:
                    collision = None

            if not collision:
                start_point = start_pos.topright
                b = start_point[1] - slope * start_point[0]
                collision = intersection_point(slope, b, 0, top_side)
                if collision.x < left_side or collision.x > right_side:
                    collision = None

            if collision:
                distance = math.sqrt((collision.x - start_point[0])**2 + (collision.y - start_point[1])**2)
                if distance < min_distance:
                    closest_collision = Collision(collision, distance, TOP_SIDE, sprite)
                    min_distance = distance
        
        # Bottom side check
        if bottom and bottom_side <= start_pos.bottom and bottom_side >= end_pos.top:
            start_point = start_pos.topright
            b = start_point[1] - slope * start_point[0]
            collision = intersection_point(slope, b, 0, bottom_side)
            if collision.x < left_side or collision.x > right_side:
                collision = None
            
            if not collision:
                start_point = start_pos.bottomright
                b = start_point[1] - slope * start_point[0]
                collision = intersection_point(slope, b, 0, bottom_side)
                if collision.x < left_side or collision.x > right_side:
                    collision = None

            if not collision:
                start_point = start_pos.topleft
                b = start_point[1] - slope * start_point[0]
                collision = intersection_point(slope, b, 0, bottom_side)
                if collision.x < left_side or collision.x > right_side:
                    collision = None

            if not collision:
                start_point = start_pos.topright
                b = start_point[1] - slope * start_point[0]
                collision = intersection_point(slope, b, 0, bottom_side)
                if collision.x < left_side or collision.x > right_side:
                    collision = None

            if collision:
                distance = math.sqrt((collision.x - start_point[0])**2 + (collision.y - start_point[1])**2)
                if distance < min_distance:
                    closest_collision = Collision(collision, distance, BOTTOM_SIDE, sprite)
                    min_distance = distance

    return closest_collision
