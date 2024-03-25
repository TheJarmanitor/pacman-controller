import pygame
from pygame.locals import *
from vector import Vector2
from constants import *
from entity import Entity
from modes import ModeController

class Ghost(Entity):
    def __init__(self, node, pacman=None) -> None:
        Entity.__init__(self, node)
        self.name = GHOST
        self.poinst = 200
        self.goal = Vector2()
        self.direction_method = self.goal_direction
        self.pacman = pacman
        self.mode = ModeController(self)
        
        
    def update(self, dt):
        self.mode.update(dt)
        if self.mode.current is SCATTER:
            self.scatter()
        elif self.mode.current is CHASE:
            self.chase()
        Entity.update(self, dt)
    
    def scatter(self):
        self.goal = Vector2()
        
    def chase(self):
        self.goal = self.pacman.position
        
    def start_freight(self):
        self.mode.set_freight_mode()
        if self.mode.current == FREIGHT:
            self.color = BLUE
            self.set_speed(50)
            self.direction_method = self.random_direction
            
    def normal_mode(self):
        self.color = WHITE
        self.set_speed(100)
        self.direction_method = self.goal_direction
        