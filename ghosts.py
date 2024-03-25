import pygame
from pygame.locals import *
from vector import Vector2
from constants import *
from entity import Entity
from modes import ModeController

class Ghost(Entity):
    def __init__(self, node, pacman=None, blinky=None) -> None:
        Entity.__init__(self, node)
        self.name = GHOST
        self.poinst = 200
        self.goal = Vector2()
        self.direction_method = self.goal_direction
        self.pacman = pacman
        self.mode = ModeController(self)
        self.blinky = blinky
        self.homenode = node
        
        
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
    
    def spawn(self):
        self.goal = self.spawn_node.position
        
    def set_spawn_mode(self, node):
        self.spawn_node = node
        
    def start_spawn(self):
        self.mode.set_spawn_mode()
        if self.mode.set_spawn_mode:
            self.set_speed(150)
            self.direction_method = self.goal_direction
            self.spawn()
        
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
        
class Blinky(Ghost):
    def __init__(self, node, pacman=None, blinky=None) -> None:
        Ghost.__init__(self, node, pacman, blinky)
        self.name = BLINKY
        self.color = RED
        
class Pinky(Ghost):
    def __init__(self, node, pacman=None, blinky=None) -> None:
        Ghost.__init__(self, node, pacman, blinky)
        self.name = PINKY
        self.color = PINK
        
    def scatter(self):
        self.goal = Vector2(TILEWIDTH * NCOLS, 0)
        
    def chase(self):
        self.goal = self.pacman.position + self.pacman.directions[self.pacman.direction] * TILEWIDTH * 4
        
class Inky(Ghost):
    def __init__(self, node, pacman=None, blinky=None) -> None:
        Ghost.__init__(self, node, pacman, blinky)
        self.name = INKY
        self.color = TEAL
        
    def scatter(self):
        self.goal = Vector2(TILEWIDTH * NCOLS, TILEHEIGHT * NROWS)
        
    def chase(self):
        vec_1 = self.pacman.position + self.pacman.directions[self.pacman.direction] * TILEWIDTH * 2
        vec_2 = (vec_1 - self.blinky.position) * 2
        self.goal = self.blinky.position + vec_2
        
class Clyde(Ghost):
    def __init__(self, node, pacman=None, blinky=None) -> None:
        Ghost.__init__(self, node, pacman, blinky)
        self.name = CLYDE
        self.color = ORANGE
        
    def scatter(self):
        self.goal = Vector2(0, TILEHEIGHT * NROWS)
        
    def chase(self):
        d = self.pacman.position - self.position
        d_squared = d.magnitude_squared()
        if d_squared <= (TILEWIDTH * 8) ** 2:
            self.scatter()
        else:
            self.goal = self.pacman.position + self.pacman.directions[self.pacman.direction] * TILEWIDTH * 4


class GhostGroup(object):
    def __init__(self, node, pacman) -> None:
        self.blinky = Blinky(node, pacman)
        self.pinky = Pinky(node, pacman)
        self.inky = Inky(node, pacman, self.blinky)
        self.clyde = Clyde(node, pacman)
        self.ghosts = [self.blinky, self.pinky, self.inky, self.clyde]
        
    def __iter__(self):
        return iter(self.ghosts)
    
    def update(self, dt):
        for ghost in self.ghosts:
            ghost.update(dt)
            
    def start_freight(self):
        for ghost in self.ghosts:
            ghost.start_freight()
        self.reset_points()
        
    def set_spawn_node(self, node):
        for ghost in self:
            ghost.set_spawn_mode(node)
            
    def update_points(self):
        for ghost in self:
            ghost.points *= 2
            
    def reset_points(self):
        for ghost in self:
            ghost.points = 200
            
    def reset(self):
        for ghost in self:
            ghost.reset()
            
    def hide(self):
        for ghost in self:
            ghost.visible = False
    
    def show(self):
        for ghost in self:
            ghost.visible = True
            
    def render(self, screen):
        for ghost in self.ghosts:
            ghost.render(screen)
            