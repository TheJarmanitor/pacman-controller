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
        self.fc1 = nn.Linear(state_space, 128)
        self.fc2 = nn.Linear(128, 128)
        self.fc3 = nn.Linear(128, action_space)
        
    def forward(self, x):
        x = F.relu(self.fc1(x))
        x = F.relu(self.fc2(x))
        x = self.fc3(x)
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

        self.optimizer = optim.Adam(
            self.model.parameters(), 
            lr=self.lr
            ) if not optimizer else optimizer

        self.criterion = nn.MSELoss() if not criterion else criterion
        
        
        
    

    