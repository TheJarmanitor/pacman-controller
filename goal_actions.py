from constants import *

class Goal(object):
    def __init__(self, name, value) -> None:
        self.name = name
        self.value = value
        
    def get_discontentment(self) -> int:
        return self.value * self.value
    
    def update_value(self, new_value):
        self.value = new_value
        
class Action(object):
    def __init__(self, name) -> None:
        self.name = name
        self.value = 0
        
    def get_goal_change(self, goal):
        raise NotImplementedError()
    
class FollowPathToTarget(Action):
    def __init__(self, name) -> None:
        super().__init__(name)
        self.value = 5
        
    def get_goal_change(self, goal):
        if goal.name == KILL_GHOST:
            goal.value -= self.value
        else:
            goal.value += 100
            
class StayInQuadrant(Action):
    def __init__(self, name) -> None:
        super().__init__(name)
        self.value = 4
        
    def get_goal_change(self, goal):
        if goal.name == KILL_GHOST:
            goal.value -= self.value
        else:
            goal.value += 100
            
class Accelerate(Action):
    def __init__(self, name) -> None:
        super().__init__(name)
        self.value = 2
        
    def get_goal_change(self, goal):
        if goal.name == KILL_GHOST:
            goal.value -= self.value
        else:
            goal.value += 100
            
class VisitNewQuadrant(Action):
    def __init__(self, name) -> None:
        super().__init__(name)
        self.value = 4
        
    def get_goal_change(self, goal):
        if goal.name == EAT_SUPERPELLETS:
            goal.value -= self.value
        else:
            goal.value += 100
            
class Wander(Action):
    def __init__(self, name) -> None:
        super().__init__(name)
        self.value = 10
        
    def get_goal_change(self, goal):
        if goal.name == EAT_SUPERPELLETS:
            goal.value -= self.value
        else:
            goal.value += 100
            
class GoCloseCorner(Action):
    def __init__(self, name) -> None:
        super().__init__(name)
        self.value = 2
        
    def get_goal_change(self, goal):
        if goal.name == EAT_SUPERPELLETS:
            goal.value -= self.value
        else:
            goal.value += 100
            
class Dummy(Action):
    def __init__(self, name) -> None:
        super().__init__(name)
        self.value = 1
        
    def get_goal_change(self, goal):
        goal.value -= self.value