from run_rl import GameController
from DQN import FcNet, Trainer
from collections import deque
from constants import FREIGHT

import random
import numpy as np
import torch
from vector import Vector2

MAX_MEMORY = 100_000
BATCH_SIZE = 1000
LR = 0.0001

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

class Environment:
    def __init__(self, model=None, lr=0.001, gamma=0.9, epsilon=0.8):
        self.n_games = 0
        self.lr = lr
        self.gamma = gamma
        self.epsilon = epsilon
        self.min_epsilon = 0.1
        self.epsilon_steps = 10
        self.model = model
        self.memory = deque(maxlen=MAX_MEMORY)
        self.trainer = Trainer(model, lr, gamma)
        
    def get_state(self, game):
        def translate_valid_directions(valid_directions):
            valid_translation = [0,0,0,0]
            if 1 in valid_directions:
                valid_translation[0] = 1
            if -1 in valid_directions:
                valid_translation[1] = 1
            if 2 in valid_directions:
                valid_translation[2] = 1
            if -2 in valid_directions:
                valid_translation[3] = 1
            return valid_translation
        player_direction = game.pacman.direction
        player_position = game.pacman.position
        blinky_position = game.ghosts.blinky.position
        blinky_mode = 1.0 if game.ghosts.blinky.mode.current == FREIGHT else 0.0
        pinky_position = game.ghosts.pinky.position
        pinky_mode = 1.0 if game.ghosts.pinky.mode.current == FREIGHT else 0.0
        inky_position = game.ghosts.inky.position if game.pellets.num_eaten > 30 else Vector2(-1,-1)
        inky_mode = 1.0 if game.ghosts.inky.mode.current == FREIGHT else 0.0
        clyde_position = game.ghosts.clyde.position if game.pellets.num_eaten > 70 else Vector2(-1,-1)
        clyde_mode = 1.0 if game.ghosts.clyde.mode.current == FREIGHT else 0.0
        
        #get closest pellet position
        closest_pellet = min(game.pellets.pellet_list, key=lambda x: (player_position - x.position).magnitude())
        closest_powerpellet = min(game.pellets.powerpellets, key=lambda x: (player_position - x.position).magnitude())
        
        valid_directions = translate_valid_directions(game.pacman.valid_directions())
        
        return(
            player_direction,
            player_position.x, player_position.y,
            pinky_position.x, pinky_position.y,
            inky_position.x, inky_position.y, 
            blinky_position.x, blinky_position.y,
            clyde_position.x, clyde_position.y,
            closest_pellet.position.x, closest_pellet.position.y,
            closest_powerpellet.position.x, closest_powerpellet.position.y,
            pinky_mode, inky_mode, blinky_mode, clyde_mode,
            valid_directions[0], valid_directions[1], valid_directions[2], valid_directions[3],
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
        
        final_move = [0,0,0,0,0]
        
        if random.uniform(0,1) < self.epsilon:
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
            
    
            
def train(model, max_games=10000):
    plot_scores = []
    plot_mean_scores = []
    total_score = 0
    plot_rewards = []
    plot_mean_rewards = []
    total_reward = 0
    record = 0
    env  = Environment(model=model, lr=LR, epsilon=0.5)
    game = GameController()
    game.start_game()
    for i in range(max_games):
        while True:
            # get old state
            state_old = env.get_state(game)

            # get move
            final_move = env.get_action(state_old)
            # print(game.pacman.valid_directions()

            # perform move and get new state
            # if random.uniform(0,1) < walk_length:
            #     env.take_action(game, final_move)
            env.take_action(game, final_move)
            
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
                plot_scores.append(score)
                total_score += score
                mean_score = total_score / env.n_games
                plot_mean_scores.append(mean_score)
                
                plot_rewards.append(reward)
                total_reward += reward
                mean_reward = total_reward / env.n_games
                plot_mean_rewards.append(mean_reward)
                
                print("score: ", score)
                
                
                if env.n_games % env.epsilon_steps == 0:
                    
                    print('game', env.n_games, 'Mean Score', mean_score, 'reward', reward, 'Mean Reward', mean_reward)
                    env.epsilon = max(env.min_epsilon, env.epsilon - 0.01)
                    
                if env.n_games % 100 == 0:
                    model.save(filename="model.pth", root_dir="./models")
                
                game.reward = 0
                game.score = 0
                game.game_over = False
                break
            
                 

if __name__ == "__main__":
    
    model = FcNet(23, 5)
    train(model)
        