import pygame
from pygame.locals import *
from vector import Vector2
from constants import *
from entity import Entity

class Pacman(Entity):
    def __init__(self, node) -> None:
        Entity.__init__(self, node)
        self.name = PACMAN
        self.color = YELLOW
        self.direction = LEFT
        self.set_between_nodes(LEFT)
        
        
    def set_position(self):
        self.position = self.node.position.copy()
        
    def update(self, dt):
        self.position += self.directions[self.direction]*self.speed*dt
        direction = self.get_valid_key()
        
        if self.overshot_target():
            self.node = self.target
            if self.node.neighbors[PORTAL] is not None:
                self.node = self.node.neighbors[PORTAL]
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
    
    def eat_pellets(self, pellet_list):
        for pellet in pellet_list:
            if self.collide_check(pellet):
                return pellet
        return None
        
    def collide_ghost(self, ghost):
        return self.collide_check(ghost)
    
    def collide_check(self, other):
        d = self.position - other.position
        d_squared = d.magnitude_squared()
        r_squared = (self.collide_radius + other.radius) ** 2
        if d_squared < r_squared:
            return True
        return False