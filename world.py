from goal_actions import Goal, Action
from copy import deepcopy

class WorldModel(object):
    
    def __init__(self, goals: list[Goal], timer, actions: list[Action]) -> None:
        self.goals = goals
        self.actions = actions
        self.timer = timer
        
        self.set_highest_goal()
        
    def set_highest_goal(self):
        self.highest_goal = max(self.goals, key=lambda goal: goal.value)
        
    def calculate_discontentment(self) -> int:
        return self.highest_goal.get_discontentment()
    
    def next_action(self) -> Action | None:
        current_actions = deepcopy(self.actions)
        return current_actions.pop(0) if current_actions else None
    
    def apply_action(self, action: Action) -> None:
        action.get_goal_change(self.highest_goal)