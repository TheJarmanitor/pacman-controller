import pygame

from pygame.locals import *
from vector import Vector2
from constants import *
from random import randint

class Entity(object):
    def __init__(self, node) -> None:
        self.name = None
        self.directions = {STOP:Vector2(),
                           DOWN:Vector2(0,1),
                           UP:Vector2(0,-1),
                           LEFT:Vector2(-1,0),
                           RIGHT:Vector2(1,0)}
        self.direction = STOP
        self.direction_method = self.random_direction
        
        self.set_speed(100)
        self.radius = 10
        self.collide_radius = 5
        self.color = WHITE
        self.visible = True
        self.goal = None
        self.set_start_node(node)
        
    def set_start_node(self, node):
        self.node = node
        self.start_node = node
        self.target = node
        self.set_position()
        
    def reset(self):
        self.set_start_node(self.start_node)
        self.direction = STOP
        self.speed = 100
        self.visible = True
        
    def set_position(self):
        self.position = self.node.position.copy()
        
    def set_between_nodes(self, direction):
        if self.node.neighbors[direction] is not None:
            self.target = self.node.neighbors[direction]
            self.position = (self.node.position + self.target.position) / 2
        
    def update(self, dt):
        self.position += self.directions[self.direction]*self.speed*dt
        
        if self.overshot_target():
            self.node = self.target
            directions = self.valid_directions()
            direction = self.direction_method(directions)
            
            self.target = self.get_new_target(direction)
            if self.target is not self.node:
                self.direction = direction
            else:
                self.target = self.get_new_target(self.direction)
                
            self.set_position()
            
    def goal_direction(self, directions):
        distances = []
        for direction in directions:
            vec = self.node.position + self.directions[direction] * TILEWIDTH - self.goal
            distances.append(vec.magnitude_squared())
        index = distances.index(min(distances))
        return directions[index]
    
    def valid_directions(self):
        directions = []
        for key in [UP, DOWN, LEFT, RIGHT]:
            if self.valid_direction(key):
                if key != self.direction * -1:
                    directions.append(key)
        if len(directions) == 0:
            directions.append(self.direction * -1)
        return directions
    
    def random_direction(self, directions):
        return directions[randint(0, len(directions) - 1)]
    
    
    def valid_direction(self, direction):
        if direction is not STOP:
            if self.node.neighbors[direction] is not None:
                return True
        return False
    
    def get_new_target(self, direction):
        if self.valid_direction(direction):
            return self.node.neighbors[direction]
        return self.node
    
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
    
    def set_speed(self, speed):
        self.speed = speed * TILEWIDTH / 16
        
    def render(self, screen):
        if self.visible:
            p = self.position.as_int()
            pygame.draw.circle(screen, self.color, p, self.radius)