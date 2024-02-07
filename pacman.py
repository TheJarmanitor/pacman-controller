import pygame
from pygame.locals import *
from vector import Vector2
from constants import *

class Pacman(object):
    def __init__(self) -> None:
        self.name = PACMAN
        self.position = Vector2(200, 400)
        self.directions = {
            STOP: Vector2(),
            UP: Vector2(0, -1),
            DOWN: Vector2(0, 1),
            LEFT: Vector2(-1, 0),
            RIGHT: Vector2(1, 0),
        }
        self.direction = STOP
        self.speed = 100 * TILEWIDTH/16
        self.radius = 10
        self.color = YELLOW
        
    def get_valid_key(self):
        
        key_pressed = pygame.key.get_pressed()
        if (key_pressed[K_UP] or key_pressed[K_w]):
            return UP
        elif (key_pressed[K_DOWN] or key_pressed[K_s]):
            return DOWN
        elif (key_pressed[K_LEFT] or key_pressed[K_a]):
            return LEFT
        elif (key_pressed[K_RIGHT] or key_pressed[K_d]):
            return RIGHT
        return STOP
    
    def render(self, screen):
        p = self.position.as_int()
        pygame.draw.circle(screen, self.color, p, self.radius)
        
        
        
    def update(self, dt):
        self.position += self.directions[self.direction]*self.speed*dt
        direction = self.get_valid_key()
        self.direction = direction
        
    