import numpy as np
from copy import deepcopy
from world import WorldModel
from constants import (
    EAT_PELLETS,
    ESCAPE_TO_NEXT_QUADRANT,
    HUNT_GHOSTS,
    GO_TO_NEAREST_GHOST,
    GO_TO_NEAREST_POWERPELLET,
    GO_TO_TARGET_CORNER,
    SELECT_NEW_QUADRANT,
    WANDER_AROUND_QUADRANT,
)

from goal_and_actions import (
    Action,
    DummyAction,
    EscapeToNextQuadrant,
    Goal,
    GoToNearestPowerpellet,
    GoToNearestGhost,
    GoToTargetCorner,
    SelectNewQuadrant,
    WanderAroundQuadrant,
)

class GOAP(object):
    def __init__(self, depth):
        self.depth = depth
        self.timer = 0
        
        # Goals
        self.hunt_ghosts = Goal(HUNT_GHOSTS, 1)
        self.eat_pellets = Goal(EAT_PELLETS, 100)
        
        self.goals = [self.hunt_ghosts, self.eat_pellets]
        
        #actions for hunting ghosts
        self.go_to_nearest_powerpellet = GoToNearestPowerpellet(GO_TO_NEAREST_POWERPELLET)
        self.go_to_nearest_ghost = GoToNearestGhost(GO_TO_NEAREST_GHOST)
        self.escape_to_next_quad = EscapeToNextQuadrant(ESCAPE_TO_NEXT_QUADRANT)
        
        #actions for eating pellets
        self.go_to_target_corner = GoToTargetCorner(GO_TO_TARGET_CORNER)
        self.wander_around_quadrant = WanderAroundQuadrant(WANDER_AROUND_QUADRANT)
        self.select_new_quadrant = SelectNewQuadrant(SELECT_NEW_QUADRANT)
        
        #dummy action
        self.dummy = DummyAction("Dummy")
        
        self.actions_hunt = [
            self.go_to_nearest_powerpellet,
            self.go_to_nearest_ghost,
        ]

        self.actions_eat = [
            self.go_to_target_corner,
            self.wander_around_quadrant,
            self.select_new_quadrant
        ]
        
        self.actions = self.actions_hunt + self.actions_eat + [self.dummy] 
        
        self.update_world_state()  
        
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
    
    def update_goals_values(self, hunt_ready, powerpellet_left):
        if hunt_ready and powerpellet_left > 0:
            self.hunt_ghosts.value = 100
            self.eat_pellets.value = 1
        else:
            self.hunt_ghosts.value = 1
            self.eat_pellets.value = 100
    
    def update_action_values(self, enemies_on_quadrant, powerpellet_on_quadrant, enemies_on_freight, powerpellet_left):
        
        ## function action order first_second_third
        
        if enemies_on_quadrant > 2 and powerpellet_left > 0:
            if powerpellet_on_quadrant:
                self.powerpellet_hunt_escape()
            if enemies_on_freight:
                self.hunt_escape_powerpellet()
        else:
            self.escape_powerpellet_hunt()
            

        #eat pellet actions
        if self.timer >= 0.0 and self.timer <= 2.0:
            self.corner_wander_newquad()
        elif self.timer > 2.0 and self.timer <= 6.0:
            self.wander_newquad_corner()
        elif self.timer > 6.0 and self.timer <= 10.0:
            self.newquad_corner_wander()
        else:
            self.timer = 0.0
            
    def run(self, hunt_ready, enemies_on_quadrant, powerpellet_on_quadrant, enemies_on_freight, powerpellet_left, dt):
        self.timer += dt
        self.update_world_state()
        self.update_goals_values(hunt_ready, powerpellet_left)
        self.update_action_values(enemies_on_quadrant, powerpellet_on_quadrant, enemies_on_freight, powerpellet_left)
        next_action = self.plan_action(self.world_state, self.depth)
        return next_action
    
    def powerpellet_hunt_escape(self):
        self.go_to_nearest_powerpellet.value = 100
        self.go_to_nearest_ghost.value = 5
        self.escape_to_next_quad.value = 1
    
    def hunt_escape_powerpellet(self):
        self.go_to_nearest_powerpellet.value = 1
        self.go_to_nearest_ghost.value = 100
        self.escape_to_next_quad.value = 5
        
    def escape_powerpellet_hunt(self):
        self.go_to_nearest_powerpellet.value = 5
        self.go_to_nearest_ghost.value = 1
        self.escape_to_next_quad.value = 100
        
    def corner_wander_newquad(self):
        self.go_to_target_corner.value = 100
        self.wander_around_quadrant.value = 5
        self.select_new_quadrant.value = 1
        
    def wander_newquad_corner(self):
        self.go_to_target_corner.value = 1
        self.wander_around_quadrant.value = 100
        self.select_new_quadrant.value = 5
    
    def newquad_corner_wander(self):
        self.go_to_target_corner.value = 5
        self.wander_around_quadrant.value = 1
        self.select_new_quadrant.value = 100