import pygame
from pygame.locals import *
from constants import *
from pacman import Pacman
from nodes import NodeGroup
from pellets import PelletGroup
from ghosts import GhostGroup
from fruits import Fruit


class GameController(object):
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode(SCREENSIZE, 0, 32)
        self.clock = pygame.time.Clock()
        self.fruit = None
        

    def set_background(self):
        self.background = pygame.surface.Surface(SCREENSIZE).convert()
        self.background.fill(BLACK)
        
    def start_game(self):
        self.set_background()
        self.nodes = NodeGroup("maze1.txt")
        self.nodes.set_portal_pair((0, 17), (27, 17))
        homekey = self.nodes.create_home_nodes(11.5, 14)
        self.nodes.connect_home_nodes(homekey, (12, 14), LEFT)
        self.nodes.connect_home_nodes(homekey, (15, 14), RIGHT)
        self.pacman = Pacman(self.nodes.get_node_from_tiles(15, 26))
        self.pellets = PelletGroup("maze1.txt")
        self.ghosts = GhostGroup(self.nodes.get_start_temp_node(), self.pacman)
        self.ghosts.blinky.set_start_node(self.nodes.get_node_from_tiles(2 + 11.5, 0 + 14))
        self.ghosts.pinky.set_start_node(self.nodes.get_node_from_tiles(2 + 11.5, 3 + 14))
        self.ghosts.inky.set_start_node(self.nodes.get_node_from_tiles(0 + 11.5, 3 + 14))
        self.ghosts.clyde.set_start_node(self.nodes.get_node_from_tiles(4 + 11.5, 3 + 14))
        self.ghosts.set_spawn_node(self.nodes.get_node_from_tiles(2 + 11.5, 3 + 14))        

        
    def check_events(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                exit()
    
    def check_pellet_events(self):
        pellet = self.pacman.eat_pellets(self.pellets.pellet_list)
        if pellet:
            self.pellets.num_eaten += 1
            self.pellets.pellet_list.remove(pellet)
            if pellet.name == POWERPELLET:
                self.ghosts.start_freight()
                
    def check_ghost_events(self):
        for ghost in self.ghosts:
            if self.pacman.collide_ghost(ghost):
                if ghost.mode.current is FREIGHT:
                    ghost.start_spawn()
                    
    def check_fruit_events(self):
        if self.pellets.num_eaten in [50, 140]:
            if self.fruit is None:
                self.fruit = Fruit(self.nodes.get_node_from_tiles(9, 20))
        if self.fruit is not None:
            if self.pacman.collide_check(self.fruit):
                self.fruit = None
            elif self.fruit.destroy:
                self.fruit = None
    
    def render(self):
        self.screen.blit(self.background, (0,0))
        self.nodes.render(self.screen)
        self.pellets.render(self.screen)
        if self.fruit is not None:
            self.fruit.render(self.screen)
        self.pacman.render(self.screen)
        self.ghosts.render(self.screen)
        pygame.display.update()        
    
    def update(self):
        dt = self.clock.tick(60) / 1000.0
        self.pacman.update(dt)
        self.pellets.update(dt)
        if self.fruit is not None:
            self.fruit.update(dt)
        self.ghosts.update(dt)
        self.check_pellet_events()
        self.check_ghost_events()
        self.check_fruit_events()
        self.check_events()
        self.render()
        
if __name__ == "__main__":
    game = GameController()
    
    game.start_game()
    
    while True:
        game.update()