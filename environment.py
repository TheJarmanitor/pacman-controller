from run_rl import GameController
from DQN import FcNet, Trainer
from collections import deque
from constants import FREIGHT

import random
import numpy as np
import torch

MAX_MEMORY = 100_000
BATCH_SIZE = 1000
LR = 0.001

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

class Environment:
    def __init__(self, model=None, lr=0.001, gamma=0.9, epsilon=1000):
        self.n_games = 0
        self.lr = lr
        self.gamma = gamma
        self.epsilon = epsilon
        self.model = model
        self.memory = deque(maxlen=MAX_MEMORY)
        self.trainer = Trainer(model, lr, gamma)
        
    def get_state(self, game):
        player_direction = game.pacman.direction
        player_position = game.pacman.position
        pinky_position = game.ghosts.pinky.position
        pinky_mode = 1.0 if game.ghosts.pinky.mode.current == FREIGHT else 0.0
        inky_position = game.ghosts.inky.position
        inky_mode = 1.0 if game.ghosts.inky.mode.current == FREIGHT else 0.0
        blinky_position = game.ghosts.blinky.position
        blinky_mode = 1.0 if game.ghosts.blinky.mode.current == FREIGHT else 0.0
        clyde_position = game.ghosts.clyde.position
        clyde_mode = 1.0 if game.ghosts.clyde.mode.current == FREIGHT else 0.0
        pellets_eaten = game.pellets.num_eaten
        lives = game.lives
        return(
            player_direction,
            player_position.x, player_position.y,
            pinky_position.x, pinky_position.y,
            inky_position.x, inky_position.y, 
            blinky_position.x, blinky_position.y,
            clyde_position.x, clyde_position.y,
            pinky_mode, inky_mode, blinky_mode, clyde_mode,
            pellets_eaten, lives
            )
        
        
    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done))
    
    def train_long_memory(self):
        if len(self.memory) > BATCH_SIZE:
            mini_sample = random.sample(self.memory, BATCH_SIZE) # list of tuples
        else:
            mini_sample = self.memory

        states, actions, rewards, next_states, dones = zip(*mini_sample)
        self.trainer.train_step(states, actions, rewards, next_states, dones)
        #for state, action, reward, nexrt_state, done in mini_sample:
        #    self.trainer.train_step(state, action, reward, next_state, done)

    def train_short_memory(self, state, action, reward, next_state, done):
        self.trainer.train_step(state, action, reward, next_state, done)
        
    def get_action(self, state):
        temp_epsilon = self.epsilon - self.n_games
        final_move = [0,0,0,0]
        
        if np.random.randint(0,2000) < temp_epsilon:
            move = np.random.randint(0,4)
            final_move[move] = 1
        else:
            state0 = torch.tensor(state, dtype=torch.float)
            prediction = self.model(state0)
            move = torch.argmax(prediction).item()
            final_move[move] = 1  
        return final_move
        
    def get_step(self, game):
        
        return game.reward, game.game_over, game.score
    
    def take_action(self, game, action):
        game.pacman.learnt_direction = game.pacman.get_new_direction(action)
            
    
            
def train(model):
    plot_scores = []
    plot_mean_scores = []
    total_score = 0
    record = 0
    env  = Environment(model=model, lr=LR, )
    game = GameController()
    game.start_game()
    while True:
        # get old state
        state_old = env.get_state(game)

        # get move
        final_move = env.get_action(state_old)

        # perform move and get new state
        env.take_action(game, final_move)
        
        #update game state
        game.update(speedup=10)
        #get new state
        state_new = env.get_state(game)
        reward, done, score = env.get_step(game)

        # train short memory
        env.train_short_memory(state_old, final_move, reward, state_new, done)

        # remember
        env.remember(state_old, final_move, reward, state_new, done)

        if done:
            # train long memory, plot result
            env.n_games += 1
            env.train_long_memory()
            
            if score > record:
                record = score
                env.model.save(root_dir="./")
            print('Game', env.n_games, 'Score', score, 'Record:', record)
            game.reward = 0
            game.score = 0
            game.game_over = False

    
        
        
        
        

if __name__ == "__main__":
    
    model = FcNet(17, 4)
    train(model)
        