from goal_actions import Goal, Action
from copy import copy

class WorldModel(object):
    
    def __init__(self, goals: list[Goal], timer, actions: list[Action]) -> None:
        self.goals = goals
        self.actions = actions
        self.timer = timer
        self.unvisited_actions = copy(self.actions)
        
        self.set_highest_goal()
        
    def set_highest_goal(self):
        self.highest_goal = max(self.goals, key=lambda goal: goal.value)
        
    def calculate_discontentment(self) -> int:
        return self.highest_goal.get_discontentment()
    
    def next_action(self) -> Action | None:
        if len(self.unvisited_actions) > 0:
            return self.unvisited_actions.pop(0)
        return None
    
    def apply_action(self, action: Action) -> None:
        action.get_goal_change(self.highest_goal)