import pygame
from pygame.locals import *
from algorithms import *
from constants import *
from entity import Entity
from sprites import PacmanSprites
from GOAP import GOAP
import sys
import numpy as np
from vector import Vector2


class Pacman(Entity):
    def __init__(self, node, nodes):
        Entity.__init__(self, node )
        self.name = PACMAN    
        self.color = YELLOW
        self.direction = LEFT
        self.set_between_nodes(LEFT)
        self.alive = True
        self.sprites = PacmanSprites(self)
        self.nodes = nodes
        # self.learnt_direction = LEFT
        
        self.next_quad = {
            TOP_LEFT: TOP_RIGHT,
            TOP_RIGHT: BOT_RIGHT,
            BOT_RIGHT: BOT_LEFT,
            BOT_LEFT: TOP_LEFT
        }
        
        self.GOAP = GOAP(10)
        self.GOAP_timer = 0
        self.hunt_ready = False
        self.quadrant_danger = 0
        self.powerpellet_in_quadrant = False
        self.enemies_on_freight = False
        self.quadrant = self.get_quadrant(self.node)
        self.target_quadrant = None
        
        
        
    def get_ghostgroup_object(self, ghosts):
        self.ghosts = ghosts
        self.enemies = self.ghosts
        
    def get_pelletgroup_object(self, pellets):
        self.pellets = pellets
        

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
        self.execute_GOAP(dt)
        self.GOAP_timer += dt
        self.sprites.update(dt)
        self.position += self.directions[self.direction]*self.speed*dt
        # direction = self.get_valid_key()
        # direction = self.goal_direction_dij(self.directions, self.goal)
        # direction = self.learnt_direction
        if self.overshot_target():
            self.node = self.target
            directions = self.valid_directions()
            direction = self.direction_method(directions)
            self.target = self.get_new_target(direction)
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
            if self.opposite_direction(self.direction):
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

    
    def get_new_direction(self, action):
        if action[0] == 1:
            return UP
        if action[1] == 1:
            return DOWN
        if action[2] == 1:
            return LEFT
        if action[3] == 1:
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
        r_squared = (self.collide_radius + other.collide_radius)**2
        if d_squared <= r_squared:
            return True
        return False
    
    def update_hunt_ready(self):
        rng = np.random.randint(0,100)
        # print(self.quadrant_danger)
        if (rng <= 25 * self.quadrant_danger and self.closest_powerpellet() is not None) or self.enemies_on_freight:
            return True
        else:
            return False
            
    def execute_GOAP(self, dt):
        self.quadrant = self.get_quadrant(self.node)
        self.quadrant_danger = self.update_quadrant_danger()
        self.hunt_ready = self.update_hunt_ready()
        self.powerpellet_in_quadrant = self.update_powerpellet_quad()
        self.enemies_on_freight = self.update_ghost_freight()
        self.powerpellet_left = len(self.pellets.powerpellets)
        
        next_action = self.GOAP.run(
            self.hunt_ready,
            self.quadrant_danger,
            self.powerpellet_in_quadrant,
            self.enemies_on_freight,
            self.powerpellet_left,
            dt
        )
        # print(next_action.name)
        
        if next_action is not None:
            if next_action.name == ESCAPE_TO_NEXT_QUADRANT:
                self.exec_escape_to_next_quad()
            elif next_action.name == GO_TO_NEAREST_GHOST:
                self.exec_go_to_nearest_ghost()
            elif next_action.name == GO_TO_NEAREST_POWERPELLET:
                self.exec_go_to_nearest_powerpellet()
            elif next_action.name == GO_TO_TARGET_CORNER:
                self.exec_go_to_target_corner()
            elif next_action.name == SELECT_NEW_QUADRANT:
                self.exec_select_new_quadrant()
            elif next_action.name == WANDER_AROUND_QUADRANT:
                self.exec_wander_around_quadrant()
    
    def exec_escape_to_next_quad(self):
        self.target_quadrant = self.next_quad[self.quadrant]
        self.goal = self.goal_from_quadrant(self.target_quadrant)
        self.direction_method = self.goal_direction_dij
    
    def exec_go_to_nearest_ghost(self):
        closest_ghost = self.get_closest_ghost()
        self.goal = closest_ghost.node
        self.direction_method = self.goal_direction_dij
    
    def exec_go_to_nearest_powerpellet(self):
        closest_pellet = self.closest_powerpellet()
        if closest_pellet is not None:
            self.goal = self.nodes.get_closest_node(closest_pellet.position)
            self.direction_method = self.goal_direction_dij
        else:
            self.exec_escape_to_next_quad()
    
    def exec_go_to_target_corner(self):
        self.goal = self.goal_from_quadrant(self.target_quadrant)
        self.direction_method = self.goal_direction_dij
    
    def exec_select_new_quadrant(self):
        self.target_quadrant = np.random.choice([TOP_LEFT, TOP_RIGHT, BOT_LEFT, BOT_RIGHT].remove(self.quadrant))
        
        

    def get_dijkstra_path(self, directions, target_node):
        last_target_node = target_node
        last_target_node = self.nodes.get_vector_from_LUT_node(last_target_node)
        # print(last_target_node)
        own_target = self.target
        own_target = self.nodes.get_vector_from_LUT_node(own_target)
        
        # print(last_target_node)
        previous_nodes, shortest_path = a_star(self.nodes, own_target)
        # print(previous_nodes.keys())
        # print(shortest_path)
        # print_result(previous_nodes, shortest_path, own_target, last_target_node)
        path = []
        node = last_target_node
        while node != own_target:
            path.append(node)
            node = previous_nodes[node]
        path.append(own_target)
        path.reverse()
        
        return path
    
    def goal_direction_dij(self, directions):
        path = self.get_dijkstra_path(directions, self.goal)
        own_target = self.target
        own_target = self.nodes.get_vector_from_LUT_node(own_target)
        path.append(own_target)
        
        next_node = path[1]
        if own_target[0] > next_node[0] and LEFT in directions:
            return LEFT
        if own_target[0] < next_node[0] and RIGHT in directions:
            return RIGHT
        if own_target[1] > next_node[1] and UP in directions:
            return UP
        if own_target[1] < next_node[1] and DOWN in directions:
            return DOWN
        else:
            return self.random_direction(directions)
        
    def get_closest_ghost(self):
        min_distance = sys.maxsize
        closest_ghost = None
        for ghost in self.enemies:
            distance = (ghost.position - self.position).magnitude_squared()
            if distance < min_distance:
                min_distance = distance
                closest_ghost = ghost
        return closest_ghost
    
    def update_ghost_freight(self):
        for ghost in self.enemies:
            if ghost.mode.current == FREIGHT:
                return True
        return False
    
    
    def closest_powerpellet(self):
        min_distance = sys.maxsize
        closest_pellet = None
        for pellet in self.pellets.powerpellets:
            # if pellet.visible:
            #     continue
            distance = (pellet.position - self.position).magnitude_squared()
            if distance < min_distance:
                min_distance = distance
                closest_pellet = pellet
        return closest_pellet
    
    def get_quadrant(self, object):
        if object is None:
            return None
        x, y = object.position.x, object.position.y
        
        in_left_half = x <= (SCREENWIDTH/2)
        in_top_half = y <= (SCREENHEIGHT/2)
        
        if in_top_half:
            if in_left_half:
                return TOP_LEFT
            else:
                return TOP_RIGHT
        else:
            if in_left_half:
                return BOT_LEFT
            else:
                return BOT_RIGHT
    
    def update_quadrant_danger(self):
        enemies_on_quadrant = 0
        for enemy in self.enemies:
            quadrant = self.get_quadrant(enemy.node)
            if quadrant == self.quadrant:
                enemies_on_quadrant += 1
        return enemies_on_quadrant
    
    def update_powerpellet_quad(self):
        pellet = self.closest_powerpellet()
        if pellet is not None:
            quadrant = self.get_quadrant(pellet)
            if quadrant == self.quadrant:
                return True
        return False
    
    def goal_from_quadrant(self, quadrant):
        if quadrant == TOP_LEFT:
            return Vector2(16, 64)
        elif quadrant == TOP_RIGHT:
            return Vector2(416, 64)
        elif quadrant == BOT_LEFT:
            return Vector2(16, 464)
        elif quadrant == BOT_RIGHT:
            return Vector2(416, 464)
        return None
        
        
        
        