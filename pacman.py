import pygame
from pygame.locals import *
from vector import Vector2
from constants import *

class Pacman(object):
    def __init__(self, node) -> None:
        self.name = PACMAN
        self.directions = {STOP:Vector2(),
                           DOWN:Vector2(0,1),
                           UP:Vector2(0,-1),
                           LEFT:Vector2(-1,0),
                           RIGHT:Vector2(1,0)}
        self.direction = STOP
        self.speed = 100 * TILEWIDTH/16
        self.radius = 10
        self.color = YELLOW
        
        self.node = node
        self.set_position()
        self.target = node
        
    def set_position(self):
        self.position = self.node.position.copy()
        
    def update(self, dt):
        self.position += self.directions[self.direction]*self.speed*dt
        direction = self.get_valid_key()
        
        if self.overshot_target():
            self.node = self.target
            self.target = self.get_new_target(direction)
            if self.target is not self.node:
                self.direction = direction
            else:
                self.target = self.get_new_target(self.direction)
            
            if self.target is self.node:
                self.direction = STOP
            self.set_position()
            
        else:
            if self.opposite_direction(direction):
                self.reverse_direction()
    
    def valid_direction(self, direction):
        if direction is not STOP:
            if self.node.neighbors[direction] is not None:
                return True
        return False
    
    def get_new_target(self, direction):
        if self.valid_direction(direction):
            return self.node.neighbors[direction]
        return self.node
    
    def get_valid_key(self):     
        key_pressed = pygame.key.get_pressed()
        if (key_pressed[K_DOWN] or key_pressed[K_s]):
            return DOWN
        if (key_pressed[K_UP] or key_pressed[K_w]):
            return UP
        if (key_pressed[K_LEFT] or key_pressed[K_a]):
            return LEFT
        if (key_pressed[K_RIGHT] or key_pressed[K_d]):
            return RIGHT
        return STOP    
    
    def overshot_target(self):
        if self.target is not None:
            vec1 = self.target.position - self.node.position
            vec2 = self.position - self.node.position
            node_to_target = vec1.magnitude_squared()
            node_to_self = vec2.magnitude_squared()
            return node_to_self >= node_to_target
        return False
    
    def reverse_direction(self):
        self.direction *= -1
        temp = self.node
        self.node = self.target
        self.target = temp
        
    def opposite_direction(self, direction):
        if direction is not STOP:
            if direction == self.direction * -1:
                return True
        return False
    
    def render(self, screen):
        p = self.position.as_int()
        pygame.draw.circle(screen, self.color, p, self.radius)
        
        
        
        
    