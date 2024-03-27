import pygame
from pygame.locals import *
from vector import Vector2
from constants import *
from entity import Entity
from random import choice
from GOAP import GOAP

class Pacman(Entity):
    def __init__(self, node) -> None:
        Entity.__init__(self, node)
        self.name = PACMAN
        self.color = YELLOW
        self.direction = LEFT
        self.set_between_nodes(LEFT)
        self.alive = True
        
        self.goal = Vector2()
        self.direction_method = self.wander_biased
        
        self.GOAP = GOAP(depth=3)
        self.GOAP_timer = 0
        self.kill_flag = False
        self.killed_timer = 0
        
        self.acc_timer = 0
        
    def reset(self):
        Entity.reset(self)
        self.direction = LEFT
        self.set_between_nodes(LEFT)
        self.alive = True
        
    def die(self):
        self.alive = False
        self.direction = STOP
        
    def set_position(self):
        self.position = self.node.position.copy()
    
    def get_ghost_object(self, ghost):
        self.ghost = ghost
        self.enemy = self.ghost
        
    def get_closest_ghost(self, ghosts):
        closest_disance = 1000
        closest_ghost = None
        for ghost in ghosts:
            distance = self.position - ghost.position
            if distance.magnitude() < closest_disance:
                closest_disance = distance.magnitude()
                closest_ghost = ghost
        return closest_ghost
        
    def update(self, dt):
        self.exec_GOAP(dt)
        self.goal = self.ghost.position
        self.GOAP_timer += dt
        self.killed_timer += dt
        self.timer += dt
        self.acc_timer += dt
        self.position += self.directions[self.direction]*self.speed*dt
        # direction = self.get_valid_key()
        
        if self.overshot_target():
            self.node = self.target
            directions = self.valid_directions()
            direction  = self.direction_method(directions)
            if self.node.neighbors[PORTAL] is not None:
                self.node = self.node.neighbors[PORTAL]
            self.target = self.get_new_target(direction)
            if self.target is not self.node:
                self.direction = direction
            else:
                self.target = self.get_new_target(self.direction)
            
            # if self.target is self.node:
            #     self.direction = STOP
            self.set_position()
            
        # else:
        #     if self.opposite_direction(direction):
        #         self.reverse_direction()
    
    
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
    
    def update_kill_flag(self):
        if self.kill_flag:
            if int(self.killed_timer) >= 7:
                self.kill_flag = False
        else:
            enemy_distance = self.position - self.enemy.position
            if enemy_distance.magnitude() < 10:
                self.kill_flag = True
                self.killed_timer = 0
                
    def update_quadrant(self, check_position):
        left_half = check_position.x <= (SCREENWIDTH / 2)
        top_half = check_position.y <= (SCREENHEIGHT / 2)
        
        if top_half:
            if left_half:
                return TOP_LEFT
            else:
                return TOP_RIGHT
        else:
            if left_half:
                return BOT_LEFT
            else:
                return BOT_RIGHT
            
    def exec_GOAP(self, dt):
        self.update_kill_flag()
        self.quadrant = self.update_quadrant(self.position)
        self.enemy_quadrant = self.update_quadrant(self.enemy.position)
        next_action = self.GOAP.run(
            self.kill_flag,
            self.quadrant,
            self.enemy_quadrant,
            dt
        )
        
        if next_action is not None:
            if next_action.name == FOLLOW_PATH_TO_TARGET:
                self.exec_follow_target(self.enemy)
            elif next_action.name == GO_TO_TARGET_QUADRANT:
                self.exec_go_to_target_quad()
            elif next_action.name == ACCELERATE:
                self.exec_accelerate()
            elif next_action.name == VISIT_NEW_QUADRANT:
                self.exec_visit_new_quadrant()
            elif next_action.name == WANDER:
                self.exec_wander()
            elif next_action.name == GO_CLOSE_CORNER:
                self.exec_go_close_corner()
            else:
                self.exec_dummy()
                
    def exec_follow_target(self):
        self.direction_method = self.goal_direction_dijkstra
        self.goal = self.enemy.position
        
    def exec_go_to_target_quad(self):
        self.goal = self.goal_quadrant(self.quadrant)
        
    def exec_accelerate(self):
        if self.acc_timer <= 3:
            self.speed = 200
        else:
            self.speed = 150
            self.acc_timer = 0
            
    def exec_visit_new_quadrant(self):
        quads = [TOP_LEFT, TOP_RIGHT, BOT_LEFT, BOT_RIGHT]
        quads.remove(self.quadrant)
        quad = choice(quads)
        self.goal = self.goal_quadrant(quad)
        return quad
    
    def exec_Wansder(self):
        self.direction_method = self.wander_biased
        
    def exec_go_close_corner(self):
        self.goal = self.goal_quadrant(self.quadrant)
        
        
    def goal_quadrant(self, quadrant):
        if quadrant == TOP_LEFT:
            return Vector2(16, 64)
        elif quadrant == TOP_RIGHT:
            return Vector2(416, 64)
        elif quadrant == BOT_LEFT:
            return Vector2(16, 464)
        elif quadrant == BOT_RIGHT:
            return Vector2(416, 464)
        return None
            