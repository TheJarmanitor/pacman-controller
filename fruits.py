import pygame
from entity import Entity
from constants import *

class Fruit(Entity):
    def __init__(self, node, nodes) -> None:
        Entity.__init__(self, node, nodes)
        self.name = FRUIT
        self.color = GREEN
        self.lifespan = 5
        self.points = 100
        self.destroy = False
        self.timer = 0
        self.set_between_nodes(RIGHT)
        
    def update(self, dt):
        self.timer += dt
        if self.timer > self.lifespan:
            self.destroy = True