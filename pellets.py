import pygame
from vector import Vector2
from constants import *
import numpy as np

class Pellet(object):
    def __init__(self, row, column):
        self.name = PELLET
        self.position = Vector2(column * TILEWIDTH, row * TILEHEIGHT)
        self.color = WHITE
        self.radius = int(4 * TILEWIDTH / 16)
        self.collide_radius = int(6 * TILEWIDTH / 16)
        self.points = 10
        self.visible = True
        
    def render(self, screen):
        if self.visible:
            p = self.position.as_int()
            pygame.draw.circle(screen, self.color, p, self.radius)
            
class PowerPellet(Pellet):
    def __init__(self, row, column):
        super().__init__(row, column)
        self.name = POWERPELLET
        self.radius = int(8 * TILEWIDTH / 16)
        self.points = 50
        self.flash_time = 0.2
        self.time = 0
    
    def update(self, dt):
        self.time += dt
        if self.time > self.flash_time:
            self.visible = not self.visible
            self.time = 0
            
class PelletGroup(object):
    def __init__(self, pelletfile):
        self.pellet_list = []
        self.powerpellets = []
        self.create_pellet_list(pelletfile)
        self.num_eaten = 0
        
    def update(self, dt):
        for powerpellet in self.powerpellets:
            powerpellet.update(dt)
            
    def create_pellet_list(self, pelletfile):
        data = self.read_pellet_file(pelletfile)
        for row in range(data.shape[0]):
            for col in range(data.shape[1]):
                if data[row][col] in ['.', '+']:
                    self.pellet_list.append(Pellet(row, col))
                elif data[row][col] in ['P', 'p']:
                    power_pellet = PowerPellet(row, col)
                    self.pellet_list.append(power_pellet)
                    self.powerpellets.append(power_pellet)
                    
    def read_pellet_file(self, pelletfile):
        return np.loadtxt(pelletfile, dtype='<U1')
    
    def is_empty(self, textfile):
        if len(self.pellet_list) == 0:
            return True
        return False
    
    def render(self, screen):
        for pellet in self.pellet_list:
            pellet.render(screen)
                    
                    