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
    slope = movement_vector.y / movement_vector.x if movement_vector.x != 0 else float('inf')
    closest_collision = None
    min_distance = float('inf')
    max_distance = math.sqrt((movement_vector[0])**2 + (movement_vector[1])**2)

    for sprite in sprites:
        left_side = sprite.rect.left
        right_side = sprite.rect.right
        top_side = sprite.rect.top
        bottom_side = sprite.rect.bottom

        # Left side check
        if left and left_side >= start_pos.left and left_side <= end_pos.right:
            collisions = []
            def check_right(start_point) -> Optional[Collision]:
                b = start_point[1] - slope * start_point[0]
                collision = intersection_point(slope, b, float('inf'), left_side)
                if bottom_side >= collision.y and collision.y >= top_side:
                    distance = math.sqrt((collision.x - start_point[0])**2 + (collision.y - start_point[1])**2)
                    if distance <= max_distance:
                        collisions.append(Collision(collision, distance, LEFT_SIDE, sprite))
            
            check_right(start_pos.topright)
            check_right(start_pos.topleft)
            check_right(start_pos.bottomright)
            check_right(start_pos.bottomleft)

            if collisions:
                collisions.sort(key=lambda c: c.distance)
                collision = collisions[0]
                if collision.distance < min_distance:
                    closest_collision = collision
                    min_distance = collision.distance

        # Right side check
        if right and right_side <= start_pos.right and right_side >= end_pos.left:
            collisions = []
            def check_right(start_point) -> Optional[Collision]:
                b = start_point[1] - slope * start_point[0]
                collision = intersection_point(slope, b, float('inf'), right_side)
                if bottom_side >= collision.y and collision.y >= top_side:
                    distance = math.sqrt((collision.x - start_point[0])**2 + (collision.y - start_point[1])**2)
                    if distance <= max_distance:
                        collisions.append(Collision(collision, distance, RIGHT_SIDE, sprite))
            
            check_right(start_pos.topright)
            check_right(start_pos.topleft)
            check_right(start_pos.bottomright)
            check_right(start_pos.bottomleft)

            if collisions:
                collisions.sort(key=lambda c: c.distance)
                collision = collisions[0]
                if collision.distance < min_distance:
                    closest_collision = collision
                    min_distance = collision.distance

        # Top side check
        if top and top_side >= start_pos.top and top_side <= end_pos.bottom:
            collisions = []
            def check_top(start_point) -> Optional[Collision]:
                b = start_point[1] - slope * start_point[0] if slope != float('inf') else start_point[0]
                collision = intersection_point(slope, b, 0, top_side)
                if left_side <= collision.x and collision.x <= right_side:
                    distance = math.sqrt((collision.x - start_point[0])**2 + (collision.y - start_point[1])**2)
                    if distance <= max_distance:
                        collisions.append(Collision(collision, distance, TOP_SIDE, sprite))
            
            check_top(start_pos.topright)
            check_top(start_pos.topleft)
            check_top(start_pos.bottomright)
            check_top(start_pos.bottomleft)

            if collisions:
                collisions.sort(key=lambda c: c.distance)
                collision = collisions[0]
                if collision.distance < min_distance:
                    closest_collision = collision
                    min_distance = collision.distance
        
        # Bottom side check
        if bottom and bottom_side <= start_pos.bottom and bottom_side >= end_pos.top:
            collisions = []
            def check_bottom(start_point) -> Optional[Collision]:
                b = start_point[1] - slope * start_point[0] if slope != float('inf') else start_point[0]
                collision = intersection_point(slope, b, 0, bottom_side)
                if left_side <= collision.x and collision.x <= right_side:
                    distance = math.sqrt((collision.x - start_point[0])**2 + (collision.y - start_point[1])**2)
                    if distance <= max_distance:
                        collisions.append(Collision(collision, distance, BOTTOM_SIDE, sprite))
            
            check_bottom(start_pos.topright)
            check_bottom(start_pos.topleft)
            check_bottom(start_pos.bottomright)
            check_bottom(start_pos.bottomleft)

            if collisions:
                collisions.sort(key=lambda c: c.distance)
                collision = collisions[0]
                if collision.distance < min_distance:
                    closest_collision = collision
                    min_distance = collision.distance

    return closest_collision
