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
        
        self.kill_ghost = Goal(KILL_GHOST, 1)
        self.eat_superpellets = Goal(EAT_SUPERPELLETS, 100)
        self.goals = [self.kill_ghost, self.eat_superpellets]
        
        self.follow_path_to_target = FollowPathToTarget(FOLLOW_PATH_TO_TARGET)
        self.go_to_target_quad = StayInQuadrant(GO_TO_TARGET_QUADRANT)
        self.accelerate = Accelerate(ACCELERATE)
        
        self.visit_new_quadrant = VisitNewQuadrant(VISIT_NEW_QUADRANT)
        self.wander = Wander(WANDER)
        self.go_close_corner = GoCloseCorner(GO_CLOSE_CORNER)
        self.dummy = Dummy(DUMMY)
        
        self.actions_kill = [
            self.follow_path_to_target,
            self.go_to_target_quad,
            self.accelerate
        ]
        
        self.actions_eat = [
            self.visit_new_quadrant,
            self.wander,
            self.go_close_corner
        ]
        
        self.actions = self.actions_kill + self.actions_eat + [self.dummy]
        
    
    def update_world_state(self):
        self.world_state = WorldModel(self.goals, self.timer, self.actions)
    
    def plan_action(self, world_model, max_depth):
        models = [None] * int(self.depth + 1)
        actions = [None] * int(self.depth)
        
        models[0] = world_model
        current_depth = 0
        
        best_action = None
        best_value = np.inf
        
        while current_depth >= 0:
            if current_depth >= max_depth:
                current_value = models[current_depth].calculate_discontentment()
                
                if current_value < best_value:
                    best_value = current_value
                    best_action = deepcopy(actions[0])
                    
                current_depth -= 1
                
            else:
                next_action = models[current_depth].next_action()
                
                if next_action:
                    models[current_depth + 1] = deepcopy(models[current_depth])
                    
                    actions[current_depth] = next_action
                    models[current_depth + 1].apply_action(next_action)
                    
                    current_depth += 1
                    
                else:
                    current_depth -= 1
        
        return best_action
    
    def update_goal_values(self, kill_flag):
        if kill_flag:
            self.kill_ghost.value = 1
            self.eat_superpellets = 1000
        else:
            self.kill_ghost.value = 1000
            self.eat_superpellets.value = 1
    
    def update_action_values(self, own_quadrant, enemy_quadrant):
        
        ## Kill Ghost actions values
        if own_quadrant == enemy_quadrant:
            self.follow_acc_quad()
        elif own_quadrant == enemy_quadrant * -1:
            self.quad_acc_follow()
        else:
            self.acc_quad_follow()
            
        ## Eat Superpellets actions values
        
        if self.timer >= 0 and self.timer < 2:
            self.corner_wander_change()
        elif self.timer >= 2 and self.timer < 6:
            self.wander_change_corner()
        elif self.timer >= 6 and self.timer < 11:
            self.change_wander_corner()
            
    def run(self, kill_flag, own_quadrant, enemy_quadrant, dt):
        self.timer += dt
        self.update_world_state()
        self.update_goal_values(kill_flag)
        self.update_action_values(own_quadrant, enemy_quadrant)
        
        next_action = self.plan_action(self.world_state, self.depth)
        return next_action
    
    def quad_acc_follow(self):
        self.follow_path_to_target.value = 1
        self.go_to_target_quad.value = 100
        self.accelerate.value = 5
        
    def acc_quad_follow(self):
        self.follow_path_to_target.value = 2
        self.go_to_target_quad.value = 5
        self.accelerate.value = 100
        
    def follow_acc_quad(self):
        self.follow_path_to_target.value = 100
        self.go_to_target_quad.value = 5
        self.accelerate.value = 2
            
    
    def change_wander_corner(self):
        self.visit_new_quadrant.value = 100
        self.wander.value = 5
        self.go_close_corner.value = 2
        
    def wander_change_corner(self):
        self.visit_new_quadrant.value = 5
        self.wander.value = 100
        self.go_close_corner.value = 2
        
    def corner_wander_change(self):
        self.visit_new_quadrant.value = 1
        self.wander.value = 5
        self.go_close_corner.value = 100
        