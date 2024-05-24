from copy import copy

from goal_and_actions import Goal, Action


class WorldModel(object):
    def __init__(self, goals: list[Goal], timer, actions: list[Action]):
        self.goals = copy(goals)
        self.actions = copy(actions)
        self.timer = timer
        self.unvisited_actions = copy(actions)
        
        self.set_highest_goal()
        
    def set_highest_goal(self):
        self.highest_goal = max(self.goals, key=lambda goal: goal.value)
        
    def calculate_discontentment(self):
        return self.highest_goal.get_discontentment()
    
    def next_action(self):
        if len(self.unvisited_actions) > 0:
            return self.unvisited_actions.pop(0)
        else:
            return None
        
    def apply_action(self, action: Action):
        action.get_goal_change(self.highest_goal)