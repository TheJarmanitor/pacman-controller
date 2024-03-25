import pygame
from vector import Vector2
from constants import *

class Text(object):
    def __init__(self, text, color, x, y, size, time=None, id=None, visible=True):
        self.id = id
        self.text = text
        self.color = color
        self.size = size
        self.visible = visible
        self.position = Vector2(x, y)
        self.timer = 0
        self.lifespan = time
        self.label = None
        self.destroy = False
        self.setup_font("PressStart2P-Regular.ttf")
        self.create_label()
        
    def setup_font(self, fontpath):
        self.font = pygame.font.Font(fontpath, self.size)
     
    def create_label(self):
        self.label = self.font.render(self.text, 1, self.color)
    
    def set_text(self, newtext):
        self.text = str(newtext)
        self.create_label()
    
    def update(self, dt):
        if self.lifespan is not None:
            self.timer += dt
            if self.timer > self.lifespan:
                self.destroy = True
                self.timer = 0
                self.lifespan = None
    
    def render(self, screen):
        if self.visible:
            x, y = self.position.as_tuple()
            screen.blit(self.label, (x, y))
            
            
class TextGroup(object):
    def __init__(self) -> None:
        self.nextid = 10
        self.alltext = {}
        self.setup_text()
        self.show_text(READYTXT)
    
    def add_text(self, text, color, x, y, size, time=None, id=None):
        self.nextid += 1
        self.alltext[self.nextid] = Text(text, color, x, y, size, time, id=id)
        return self.nextid
    
    def remove_text(self, id):
        self.alltext.pop(id)
        
    def setup_text(self):
        size = TILEHEIGHT
        self.alltext[SCORETXT] = Text("0".zfill(8), WHITE, 0, TILEHEIGHT, size)
        self.alltext[LEVELTXT] = Text(str(1).zfill(3), WHITE, 23*TILEWIDTH, TILEHEIGHT, size)
        self.alltext[READYTXT] = Text("READY!", YELLOW, 11.25*TILEWIDTH, 20*TILEHEIGHT, size, visible=False)
        self.alltext[PAUSETXT] = Text("PAUSED!", YELLOW, 10.625*TILEWIDTH, 20*TILEHEIGHT, size, visible=False)
        self.alltext[GAMEOVERTXT] = Text("GAMEOVER!", YELLOW, 10*TILEWIDTH, 20*TILEHEIGHT, size, visible=False)
        self.add_text("SCORE", WHITE, 0, 0, size)
        self.add_text("LEVEL", WHITE, 23*TILEWIDTH, 0, size)
        
    def update(self, dt):
        for tkey in list(self.alltext.keys()):
            self.alltext[tkey].update(dt)
            if self.alltext[tkey].destroy:
                self.remove_text(tkey)
                
    def show_text(self, id):
        self.hide_text()
        self.alltext[id].visible = True
        
    def hide_text(self):
        self.alltext[READYTXT].visible = False
        self.alltext[PAUSETXT].visible = False
        self.alltext[GAMEOVERTXT].visible = False
        
    def update_score(self, score):
        self.update_text(SCORETXT, str(score).zfill(8))
        
    def update_level(self, level):
        self.update_text(LEVELTXT, str(level + 1).zfill(3))
        
    def update_text(self, id, value):
        if id in self.alltext.keys():
            self.alltext[id].set_text(value)
            
    def render(self, screen):
        for tkey in list(self.alltext.keys()):
            self.alltext[tkey].render(screen)