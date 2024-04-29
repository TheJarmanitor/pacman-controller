from run_rl import GameController
from DQN import FcNet, Trainer
from collections import deque
from constants import FREIGHT

import numpy as np

MAX_MEMORY = 100_000
BATCH_SIZE = 1000
LR = 0.001

class Environment:
    def __init__(self, model=None, lr=0, gamma=0, epsilon=100):
        self.n_games = 0
        self.lr = lr
        self.gamma = gamma
        self.epsilon = epsilon
        self.model = model
        self.memory = deque(maxlen=MAX_MEMORY)
        
    def get_state(self, game):
        player_position = game.pacman.position
        pinky_position = game.ghosts.pinky.position
        pinky_mode = 1.0 if game.ghosts.pinky.mode.current == FREIGHT else 0.0
        inky_position = game.ghosts.inky.position
        inky_mode = 1.0 if game.ghosts.inky.mode.current == FREIGHT else 0.0
        blinky_position = game.ghosts.blinky.position
        blinky_mode = 1.0 if game.ghosts.blinky.mode.current == FREIGHT else 0.0
        clyde_position = game.ghosts.clyde.position
        clyde_mode = 1.0 if game.ghosts.clyde.mode.current == FREIGHT else 0.0
        score = game.score
        lives = game.lives
        return(player_position.x, player_position.y,
               pinky_position.x, pinky_position.y,
               inky_position.x, inky_position.y, 
               blinky_position.x, blinky_position.y,
               clyde_position.x, clyde_position.y,
               pinky_mode, inky_mode, blinky_mode, clyde_mode,
               score, lives)
        
    def get_action(self):
        self.epsilon -= self.n_games
        final_move = [0,0,0,0]
        
        if np.random.randint(0,200) < self.epsilon:
            move = np.random.randint(0,4)
            final_move[move] = 1
        else:
            final_move = [0,0,0,0]    
        return final_move
        
    
    def take_action(self, game, frames=1):
        for i in range(frames):
            action = self.get_action()
            game.pacman.learnt_direction = game.pacman.get_new_direction(action)
            game.update()
        
        
        
        

if __name__ == "__main__":
    game = GameController()
    env = Environment()
    game.start_game()
    while True:
        # print(env.get_state(game))
        env.take_action(game)
        