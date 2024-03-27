import numpy as np
from copy import deepcopy
from world import WorldModel
from constants import *
import sys
from goal_actions import *

class GOAP(object):
    def __init__(self, depth) -> None:
        self.depth = depth
        self.timer = 0
        
        self.world_state = None
        
        self.hunt_ghosts = Goal(HUNT_GHOSTS, 100)
        self.eat_pellets = Goal(EAT_PELLETS, 1)
        self.goals = [self.hunt_ghosts, self.eat_pellets]
        
        self.follow_path_to_superpellet = FollowPathToSuperPellet(FOLLOW_PATH_TO_SUPERPELLET)
        self.go_to_target_quad = GoToTargetQuadrant(GO_TO_TARGET_QUADRANT)
        
        self.visit_new_quadrant = VisitNewQuadrant(VISIT_NEW_QUADRANT)
        self.wander = Wander(WANDER)
        self.go_close_corner = GoCloseCorner(GO_CLOSE_CORNER)
        
        self.go_to_fruit = GoToFruit(GO_TO_FRUIT)
        
        self.dummy = Dummy(DUMMY)
        
        self.actions_hunt = [
            self.follow_path_to_superpellet,
            self.go_to_target_quad
        ]
        
        self.actions_eat = [
            self.visit_new_quadrant,
            self.wander,
            self.go_close_corner,
            self.go_to_fruit
        ]
        
        self.actions = self.actions_hunt + self.actions_eat + [self.dummy]
        
    
    def update_world_state(self):
        self.world_state = WorldModel(self.goals, self.timer, self.actions)
    
    def plan_action(self, world_model, max_depth):
        models: list[None | WorldModel] = [None] * int(self.depth + 1)
        actions: list[None | Action] = [None] * int(self.depth)
        
        models[0] = world_model
        current_depth = 0
        
        best_action = None
        best_value = sys.maxsize
        
        while current_depth >= 0:
            current_model = models[current_depth]
            assert current_model
            
            if current_depth >= max_depth:
                current_value = current_model.calculate_discontentment()
                
                if current_value < best_value:
                    best_value = current_value
                    assert actions[0]
                    best_action = actions[0]
                    
                current_depth -= 1
                
            else:
                next_action = current_model.next_action()
                
                if next_action:
                    model_copy = deepcopy(current_model)
                    
                    actions[current_depth] = next_action
                    model_copy.apply_action(next_action)
                    
                    models[current_depth + 1] = model_copy
                    
                    current_depth += 1
                    
                else:
                    current_depth -= 1
        
        return best_action
    
    def update_goal_values(self, hunt_mode):
        if hunt_mode:
            self.hunt_ghosts.value = 1000
            self.eat_pellets.value = 1
        else:
            self.hunt_ghosts.value = 1
            self.eat_pellets.value = 1000
    
    def update_action_values(self, own_quadrant, target_quadrant, super_close, fruit_present):
        
        ## Kill Ghost actions values
        if super_close:
            self.super_quad_wander()
        else:
            if own_quadrant != target_quadrant:
                self.quad_wander_super()
            else:
                self.wander_quad_super()
            
        ## Eat pellets actions values
        
        if self.timer >= 0 and self.timer < 2:
            self.corner_wander_change_fruit()
        elif self.timer >= 2 and self.timer < 6:
            self.wander_change_corner_fruit()
        elif self.timer >= 6 and self.timer < 11:
            self.change_wander_corner_fruit()
        if fruit_present:
            self.fruit_wander_corner_change()
            
    def run(self, hunt_mode, own_quadrant, target_quadrant, super_close, fruit_present, dt):
        self.timer += dt
        self.update_world_state()
        self.update_goal_values(hunt_mode)
        self.update_action_values(own_quadrant, target_quadrant, super_close, fruit_present)
        
        next_action = self.plan_action(self.world_state, self.depth)
        return next_action
    
    def super_quad_wander(self):
        self.follow_path_to_superpellet.value = 100 
        self.go_to_target_quad.value = 5
        self.wander.value = 1
    
    def quad_wander_super(self):
        self.follow_path_to_superpellet.value = 1
        self.go_to_target_quad.value = 1000
        self.wander.value = 5
        
    def wander_quad_super(self):
        self.follow_path_to_superpellet.value = 1 
        self.go_to_target_quad.value = 2
        self.wander.value = 100
        
    def corner_wander_change_fruit(self):
        self.go_to_fruit.value = 1
        self.visit_new_quadrant.value = 2
        self.wander.value = 5
        self.go_close_corner.value = 100
        
    def wander_change_corner_fruit(self):
        self.go_to_fruit.value = 1
        self.visit_new_quadrant.value = 5
        self.wander.value = 100
        self.go_close_corner.value = 2
    
    def change_wander_corner_fruit(self):
        self.go_to_fruit.value = 1
        self.visit_new_quadrant.value = 100
        self.wander.value = 5
        self.go_close_corner.value = 2
        
    def fruit_wander_corner_change(self):
        self.go_to_fruit.value = 100
        self.visit_new_quadrant.value = 1
        self.wander.value = 5
        self.go_close_corner.value = 2