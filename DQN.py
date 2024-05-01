## pytorch libraries
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
import os

## other libraries
import numpy as np


class FcNet(nn.Module):
    def __init__(self, state_space, action_space):
        super(FcNet, self).__init__()
        self.fc1 = nn.Linear(state_space, 512)
        self.fc2 = nn.Linear(512, 512)
        self.fc3 = nn.Linear(512, 512)
        self.fc4 = nn.Linear(512, action_space)
        
    def forward(self, x):
        x = F.relu(self.fc1(x))
        x = F.relu(self.fc2(x))
        x = F.relu(self.fc3(x))
        x = self.fc4(x)
        return x
    
    def save(self, filename="model.pth", root_dir="./models"):
        if not os.path.exists(root_dir):
            os.makedirs(root_dir)
        filename = os.path.join(root_dir, filename)
        torch.save(self.state_dict(), filename)
    
class ConvNet(nn.Module):
    def __init__(self, action_space):
        super(ConvNet, self).__init__()
        self.conv1 = nn.Conv2d(3, 32, 5, 1)
        self.conv2 = nn.Conv2d(32, 64, 5, 1)
        self.conv3 = nn.Conv2d(64, 128, 5, 1)
        self.pool = nn.MaxPool2d(2, 2)
        self.fc1 = nn.Linear(128*4*4, 128)
        self.fc2 = nn.Linear(128, action_space)
        
    def forward(self, x):
        x = self.pool(F.relu(self.conv1(x)))
        x = self.pool(F.relu(self.conv2(x)))
        x = self.pool(F.relu(self.conv3(x)))
        x = x.view(-1, 128*4*4)
        x = F.relu(self.fc1(x))
        x = self.fc2(x)
        return x
    
    def save(self, filename="model.pth", root_dir="./models"):
        if not os.path.exists(root_dir):
            os.makedirs(root_dir)
        filename = os.path.join(root_dir, filename)
        torch.save(self.state_dict(), filename)
    
class Trainer():
    def __init__(self, model, lr, gamma, optimizer=None, criterion=None):
        self.model = model
        self.lr = lr
        self.gamma = gamma

        self.optimizer = optim.RMSprop(self.model.parameters(), 
                                  lr=lr, 
                                  alpha=0.95, 
                                  eps=0.01) if not optimizer else optimizer

        self.criterion = nn.SmoothL1Loss() if not criterion else criterion
        
    def train_step(self, state, action, reward, next_state, done):
        state = torch.tensor(state, dtype=torch.float)
        next_state = torch.tensor(next_state, dtype=torch.float)
        action = torch.tensor(action, dtype=torch.long)
        reward = torch.tensor(reward, dtype=torch.float)
        policy_net = self.model
        
        if len(state.shape) == 1:

            state = torch.unsqueeze(state, 0)
            next_state = torch.unsqueeze(next_state, 0)
            action = torch.unsqueeze(action, 0)
            reward = torch.unsqueeze(reward, 0)
            done = (done, )
        
        pred = self.model(state)
        
        target = policy_net(state)
        for idx in range(len(done)):
            Q_new = reward[idx]
            if not done[idx]:
                Q_new = reward[idx] + self.gamma * torch.max(self.model(next_state[idx]))

            target[idx][torch.argmax(action[idx]).item()] = Q_new
    
        # 2: Q_new = r + y * max(next_predicted Q value) -> only do this if not done
        # pred.clone()
        # preds[argmax(action)] = Q_new
        loss = self.criterion(target, pred)
        self.optimizer.zero_grad()
        loss.backward()

        self.optimizer.step()
        
        
        
        
    

    