from run_rl import GameController
from DQN import FcNet, ConvNet, Trainer
from collections import deque
from constants import FREIGHT

import random
import numpy as np
import torch
from vector import Vector2
import pygame

# import cv2
from torchvision import transforms
from PIL import Image

from itertools import count


MAX_MEMORY = 100_000
BATCH_SIZE = 1000
LR = 5e-5


class Environment:
    def __init__(self, model=None, lr=0.001, gamma=0.9, epsilon=0.5):
        self.n_games = 0
        self.lr = lr
        self.gamma = gamma
        self.epsilon = epsilon
        self.min_epsilon = 0.1
        self.epsilon_steps = 1000
        self.model = model
        self.memory = deque(maxlen=MAX_MEMORY)
        self.trainer = Trainer(model, lr, gamma)
        
    def get_state(self, game):
        player_direction = game.pacman.direction
        player_position = game.pacman.position
        # closest_ghost = min(game.ghosts, key=lambda x: (player_position - x.position).magnitude())
        # ghost_position = closest_ghost.position
        # ghost_mode = 1.0 if closest_ghost.mode.current == FREIGHT else 0.0
        blinky_position = game.ghosts.blinky.position
        blinky_mode = 1.0 if game.ghosts.blinky.mode.current == FREIGHT else 0.0
        pinky_position = game.ghosts.pinky.position
        pinky_mode = 1.0 if game.ghosts.pinky.mode.current == FREIGHT else 0.0
        inky_position = game.ghosts.inky.position 
        inky_mode = 1.0 if game.ghosts.inky.mode.current == FREIGHT else 0.0
        clyde_position = game.ghosts.clyde.position 
        clyde_mode = 1.0 if game.ghosts.clyde.mode.current == FREIGHT else 0.0
        
        #get closest pellet position
        closest_pellet = min(game.pellets.pellet_list, key=lambda x: (player_position - x.position).magnitude())
        closest_powerpellet = min(game.pellets.powerpellets, key=lambda x: (player_position - x.position).magnitude())
        
        
        return(
            player_direction,
            player_position.x, player_position.y,
            pinky_position.x, pinky_position.y,
            inky_position.x, inky_position.y, 
            blinky_position.x, blinky_position.y,
            clyde_position.x, clyde_position.y,
            # ghost_position.x, ghost_position.y,
            closest_pellet.position.x, closest_pellet.position.y,
            closest_powerpellet.position.x, closest_powerpellet.position.y,
            pinky_mode, inky_mode, blinky_mode, clyde_mode,
            # ghost_mode
            )
    # def get_state_conv(self, game):
        
    #     capture = pygame.surfarray.array3d(game.screen)
    #     capture = capture.transpose([1,0,2])
    #     capture_bgr = cv2.cvtColor(capture, cv2.COLOR_RGB2BGR)
        
    #     image_state = Image.fromarray(capture_bgr)
        
    #     transform = transforms.Compose([
    #                 transforms.Resize((64, 64)),
    #                 transforms.ToTensor(),
    #             ])
        
    #     transformed_capture = transform(image_state)
        
    #     return transformed_capture
        
        
    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done))
    
    def train_long_memory(self):
        if len(self.memory) > BATCH_SIZE:
            mini_sample = random.sample(self.memory, BATCH_SIZE) # list of tuples
        else:
            mini_sample = self.memory
        states, actions, rewards, next_states, dones = zip(*mini_sample)
        self.trainer.train_step(states, actions, rewards, next_states, dones, update=True)
        #for state, action, reward, nexrt_state, done in mini_sample:
        #    self.trainer.train_step(state, action, reward, next_state, done)

    def train_short_memory(self, state, action, reward, next_state, done):
        self.trainer.train_step(state, action, reward, next_state, done)
        
    def get_action(self, state, pretrained=False):
        
        final_move = [0,0,0,0]
        
        if not pretrained:
            epsilon = self.epsilon
        else:
            epsilon = self.min_epsilon
        if random.uniform(0,1) < epsilon:
            move = np.random.randint(0,4)
            final_move[move] = 1
        else:
            state0 = torch.tensor(state, dtype=torch.float)
            prediction = self.trainer.policy_net(state0)
            move = torch.argmax(prediction).item()
            final_move[move] = 1  
            
        return final_move
    
    def take_action(self, game, action):
        game.pacman.learnt_direction = game.pacman.get_new_direction(action)
            
    
            
def train(model, max_steps=10000, speedup=1, skip = 5):
    plot_scores = []
    plot_mean_scores = []
    plot_rewards = []
    plot_mean_rewards = []
    record = 0
    env  = Environment(model=model, lr=LR, epsilon=0.5)
    game = GameController()
    game.start_game()
    total_score = 0
    total_reward = 0
    for i in range(max_steps * speedup):
        dt = game.clock.tick(60) * speedup / 1000.0 
        state_old = env.get_state(game)
            # print(state_old.shape)
        final_move = env.get_action(state_old)

            # get move

        if i  % skip // speedup == 0:
            # print(final_move)
            env.take_action(game, final_move)
            
        game.update(dt)
        reward, done, score = game.play_step()
        # print(reward)
        #get new state
        state_new = env.get_state(game)
        total_reward += reward
# train short memory
        
        env.train_short_memory(state_old, final_move, reward, state_new, done)

    # remember
        env.remember(state_old, final_move, reward, state_new, done)

        if i % env.epsilon_steps  == 0:
            print("iteration", i // speedup, "epsilon", env.epsilon)
            env.epsilon = max(env.min_epsilon, env.epsilon - 0.01)
            
        if done:
            # train long memory, plot result
            env.n_games += 1
            if env.n_games % 100 == 0:
                env.train_long_memory()
            plot_scores.append(score)
            mean_score = sum(plot_scores)/len(plot_scores)
            plot_mean_scores.append(mean_score)
            
            plot_rewards.append(reward)
            mean_reward = np.mean(plot_rewards)
            plot_mean_rewards.append(mean_reward)
            
            print("game", env.n_games, "last score", score, "average score", mean_score)
            
            
                
            if i % 100 == 0:
                model.save(filename="model.pth", root_dir="./models")
            
            game.reward = 0
            game.score = 0
            game.game_over = False
            
def play(modelfile, skip=5):
    model = FcNet(19, 4)
    model.load_state_dict(torch.load(modelfile))
    env = Environment(model=model)
    game = GameController()
    game.start_game()
    for i in count(0):
        dt = game.clock.tick(60) / 1000.0 
        if i % skip == 0:
            state = env.get_state(game)
            move = env.get_action(state, pretrained=True)
            # print(move)
            env.take_action(game, move)
        game.update(dt)
        reward, done, score = game.play_step()
        if done:
            env.n_games += 1
            print("game", env.n_games, "last score", score)
            game.reward = 0
            game.score = 0
            game.game_over = False
            

            
                 

if __name__ == "__main__":
    
    model = FcNet(19, 4)
    model
    # train(model, speedup=5, skip=20)
    play("models/model.pth", skip=5)
        