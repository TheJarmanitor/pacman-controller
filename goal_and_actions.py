from constants import EAT_PELLETS, KILL_GHOSTS, ESCAPE

class Goal(object):
    def __init__(self, name, value):
        self.name = name
        self.value = value
        
    def get_discontentment(self) -> int:
        return self.value * self.value
    
    def update_value(self, new_value):
        self.value = new_value
        
class Action(object):
    def __init__(self, name):
        self.name = name
        self.value = 0
        
    def get_goal_change(self, goal:Goal) -> int:
        raise NotImplementedError
    
########## Specific Actions ##########

'''
Goals:
    Eat pellets
    Hunt ghosts
    Escape
Actions:
    Eat pellets:
        Go to nearest corner
        wander around quadrant
    Hunt ghost:
        Go to nearest PowerPellet
        Go to nearest ghost
    Escape:
        select different quadrant
        got to quadran's corner
'''

class GoToClosestCorner(Action):
    def __init__(self, name):
        self.value = 5
        
    def get_goal_change(self, goal: Goal) -> int:
        if goal.name == EAT_PELLETS:
            goal.value -= self.value
        else:
            goal.value += 100
            
class WanderAroundQuadrant(Action):
    def __init__(self, name):
        self.value = 3
        
    def get_goal_change(self, goal: Goal) -> int:
        if goal.name == EAT_PELLETS:
            goal.value += self.value
        else:
            goal.value -= 100
            
class GoToNearestPowerpellet(Action):
    def __init__(self, name):
        self.value = 10
        
    def get_goal_change(self, goal: Goal) -> int:
        if goal.name == KILL_GHOSTS:
            goal.value -= self.value
        else:
            goal.value += 100

class GoToNearestGhost(Action):
    def __init__(self, name):
        self.value = 5
        
    def get_goal_change(self, goal: Goal) -> int:
        if goal.name == KILL_GHOSTS:
            goal.value += self.value
        else:
            goal.value -= 100
            
class SelectNewQuadrant(Action):
    def __init__(self, name):
        self.value = 5
        
    def get_goal_change(self, goal: Goal) -> int:
        if goal.name == ESCAPE:
            goal.value += self.value
        else:
            goal.value -= 100
            
class GoToQuadrantCorner(Action):
    def __init__(self, name):
        self.value = 3
        
    def get_goal_change(self, goal: Goal) -> int:
        if goal.name == ESCAPE:
            goal.value -= self.value
        else:
            goal.value += 100
            
class DummyAction(Action):
    def __init__(self, name):
        self.value = 1
        
    def get_goal_change(self, goal: Goal) -> int:
        goal.value -= self.value