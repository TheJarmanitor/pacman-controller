import pygame
from pygame.locals import *
from constants import *
from entity import Entity
from sprites import PacmanSprites

class Pacman(Entity):
    def __init__(self, node):
        Entity.__init__(self, node )
        self.name = PACMAN    
        self.color = YELLOW
        self.direction = LEFT
        self.set_between_nodes(LEFT)
        self.alive = True
        self.sprites = PacmanSprites(self)
        self.learnt_direction = LEFT

    def reset(self):
        Entity.reset(self)
        self.direction = LEFT
        self.set_between_nodes(LEFT)
        self.alive = True
        self.image = self.sprites.get_start_image()
        self.sprites.reset()

    def die(self):
        self.alive = False
        self.direction = STOP

    def update(self, dt):	
        self.sprites.update(dt)
        self.position += self.directions[self.direction]*self.speed*dt
        # direction = self.get_valid_key()
        direction = self.learnt_direction
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
        if key_pressed[K_UP]:
            return UP
        if key_pressed[K_DOWN]:
            return DOWN
        if key_pressed[K_LEFT]:
            return LEFT
        if key_pressed[K_RIGHT]:
            return RIGHT
        return STOP 
    
    # def get_new_direction(self,action):
    #     # turn left [1,0,0,0]
    #     if action[0] == 1:
    #         if self.direction == UP:
    #             return LEFT
    #         if self.direction == LEFT:
    #             return DOWN
    #         if self.direction == DOWN:
    #             return RIGHT
    #         if self.direction == RIGHT:
    #             return UP 
    #     ##turn right [0,1,0,0]
    #     elif action[1] == 1:
    #         if self.direction == UP:
    #             return RIGHT
    #         if self.direction == RIGHT:
    #             return DOWN
    #         if self.direction == DOWN:
    #             return LEFT
    #         if self.direction == LEFT:
    #             return UP
    #     ## Go back [0,0,1,0]
    #     elif action[2] == 1:
    #         return self.reverse_direction()
    #     ## keep direction [0,0,0,1]
    #     elif action[3] == 1:
    #         return self.direction
    
    def get_new_direction(self, action):
        if action[0] == 1:
            return UP
        if action[1] == 1:
            return DOWN
        if action[2] == 1:
            return LEFT
        if action[3] == 1:
            return RIGHT
        if action[4] == 1:
            return self.direction
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
        r_squared = (self.collide_radius + other.collide_radius)**2
        if d_squared <= r_squared:
            return True
        return False
