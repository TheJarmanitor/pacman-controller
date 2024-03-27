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

'''
Goal 1: Hunt all ghosts
    action 1: get to super pellet
    action 2: go to each ghost's quadrant
Goal 2: Eat pellets
    action 1: go to new quadrant
    action 2: wander around
    action 3: go to close corner
Goal 3: Eat Fruit
    action 1: go to fruit
    action 2: wander around
    
    
    

'''
#### Goal 1 actions
class FollowPathToSuperPellet(Action):
    def __init__(self, name) -> None:
        super().__init__(name)
        self.value = 5
        
    def get_goal_change(self, goal):
        if goal.name == HUNT_GHOSTS:
            goal.value -= self.value
        else:
            goal.value += 100
            
class GoToTargetQuadrant(Action):
    def __init__(self, name) -> None:
        super().__init__(name)
        self.value = 4
        
    def get_goal_change(self, goal):
        if goal.name == HUNT_GHOSTS:
            goal.value -= self.value
        else:
            goal.value += 100
            
class VisitNewQuadrant(Action):
    def __init__(self, name) -> None:
        super().__init__(name)
        self.value = 3
        
    def get_goal_change(self, goal):
        if goal.name == EAT_PELLETS:
            goal.value -= self.value
        else:
            goal.value += 100
            
class Wander(Action):
    def __init__(self, name) -> None:
        super().__init__(name)
        self.value = 10
        
    def get_goal_change(self, goal):
        if goal.name == EAT_PELLETS:
            goal.value -= self.value
        else:
            goal.value += 100
            
class GoCloseCorner(Action):
    def __init__(self, name) -> None:
        super().__init__(name)
        self.value = 2
        
    def get_goal_change(self, goal):
        if goal.name == EAT_PELLETS:
            goal.value -= self.value
        else:
            goal.value += 100

class GoToFruit(Action):
    def __init__(self, name) -> None:
        super().__init__(name)
        self.value = 10
        
    def get_goal_change(self, goal):
        if goal.name == EAT_PELLETS:
            goal.value -= self.value
        else:
            goal.value += 100
            
class Dummy(Action):
    def __init__(self, name) -> None:
        super().__init__(name)
        self.value = 1
        
    def get_goal_change(self, goal):
        goal.value -= self.value