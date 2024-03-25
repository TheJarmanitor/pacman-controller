from constants import *

class MainMode(object):
    def __init__(self):
        self.timer = 0
        self.scatter()
        
        
    def update(self, dt):
        self.timer += dt
        if self.timer > self.time:
            if self.mode == SCATTER:
                self.chase()
            elif self.mode == CHASE:
                self.scatter()
                
    def scatter(self):
        self.mode = SCATTER
        self.time = 7
        self.timer = 0
        
    def chase(self):
        self.mode = CHASE
        self.time = 20
        self.timer = 0
        
        
class ModeController(object):
    def __init__(self, entity):
        self.timer = 0
        self.time = None
        self.mainmode = MainMode()
        self.current = self.mainmode.mode
        self.entity = entity
        
    def update(self, dt):
        self.mainmode.update(dt)
        if self.current == FREIGHT:
            self.timer += dt
            if self.timer > self.time:
                self.time = None
                self.entity.normal_mode()
                self.current = self.mainmode.mode
        else:        
            self.current = self.mainmode.mode
    
    def set_freight_mode(self):
        if self.current in [SCATTER, CHASE]:
            self.current = FREIGHT
            self.time = 7
            self.timer = 0
        elif self.current == FREIGHT:
            self.timer = 0