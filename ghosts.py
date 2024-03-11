import pygame
from pygame.locals import *
from vector import Vector2
from constants import *
from entity import Entity

class Ghost(Entity):
    def __init__(self, node) -> None:
        Entity.__init__(self, node)
        self.name = GHOST
        self.poinst = 200
        self.goal = Vector2()
        self.direction_method = self.random_direction 