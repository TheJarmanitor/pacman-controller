import numpy as np
from copy import deepcopy

class GOAP(object):
    def __init__(self, depth):
        self.depth = depth
    
        return    
        
    def update_world_state(self):
        return
    
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
    