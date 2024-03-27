import pygame
from pygame.locals import *
from constants import *
from pacman import Pacman
from nodes import NodeGroup
from pellets import PelletGroup
from ghosts import GhostGroup
from fruits import Fruit
from pauser import Pause
from text import TextGroup


class GameController(object):
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode(SCREENSIZE, 0, 32)
        self.clock = pygame.time.Clock()
        self.fruit = None
        self.lives = 3
        self.pause = Pause(True)
        self.score = 0
        self.textgroup = TextGroup()
        

    def set_background(self):
        self.background = pygame.surface.Surface(SCREENSIZE).convert()
        self.background.fill(BLACK)
        
    def start_game(self):
        self.set_background()
        self.nodes = NodeGroup("maze1.txt")
        self.nodes.set_portal_pair((0, 17), (27, 17))
        homekey = self.nodes.create_home_nodes(11.5, 14)
        # print(homekey)
        self.nodes.connect_home_nodes(homekey, (12, 14), LEFT)
        self.nodes.connect_home_nodes(homekey, (15, 14), RIGHT)
        self.pacman = Pacman(self.nodes.get_node_from_tiles(15, 26), self.nodes)
        self.pellets = PelletGroup("maze1.txt")
        self.pacman.superpellet = self.pellets.powerpellets
        
        
         
        self.ghosts = GhostGroup(self.nodes.get_start_temp_node(), self.nodes, self.pacman)
        self.ghosts.blinky.set_start_node(self.nodes.get_node_from_tiles(2 + 11.5, 0 + 14))
        self.ghosts.pinky.set_start_node(self.nodes.get_node_from_tiles(2 + 11.5, 3 + 14))
        self.ghosts.inky.set_start_node(self.nodes.get_node_from_tiles(0 + 11.5, 3 + 14))
        self.ghosts.clyde.set_start_node(self.nodes.get_node_from_tiles(4 + 11.5, 3 + 14))
        self.ghosts.set_spawn_node(self.nodes.get_node_from_tiles(2 + 11.5, 3 + 14))  
        self.pacman.ghosts = self.ghosts
        
        self.nodes.deny_home_access(self.pacman)
        self.nodes.deny_home_access_list(self.ghosts)
        self.nodes.deny_access_list(2+11.5, 3+14, RIGHT, self.ghosts)
        self.nodes.deny_access_list(2+11.5, 3+14, LEFT, self.ghosts)
        self.ghosts.inky.start_node.deny_access(RIGHT, self.ghosts.inky)
        self.ghosts.clyde.start_node.deny_access(LEFT, self.ghosts.clyde)
        self.nodes.deny_access_list(12, 14, UP, self.ghosts)
        self.nodes.deny_access_list(15, 14, UP, self.ghosts)
        self.nodes.deny_access_list(12, 26, UP, self.ghosts)
        self.nodes.deny_access_list(15, 26, UP, self.ghosts)
              
        self.pacman.get_ghost_object(self.ghosts.blinky)

        
    def check_events(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                exit()
            elif event.type == KEYDOWN:
                if event.key == K_SPACE:
                    self.pause.set_pause(player_paused=True)
                    if not self.pause.paused:
                        self.textgroup.hide_text()
                        self.show_entities()
                    else:
                        self.textgroup.show_text(PAUSETXT)
                        self.hide_entities()
    def check_pellet_events(self):
        pellet = self.pacman.eat_pellets(self.pellets.pellet_list)
        if pellet:
            self.pellets.num_eaten += 1
            if self.pellets.num_eaten == 30:
                self.ghosts.inky.start_node.allow_access(RIGHT, self.ghosts.inky)
            if self.pellets.num_eaten == 70:
                self.ghosts.clyde.start_node.allow_access(LEFT, self.ghosts.clyde)
            self.update_score(pellet.points)
            self.pellets.pellet_list.remove(pellet)
            if pellet.name == POWERPELLET:
                self.ghosts.start_freight()
                
    def check_ghost_events(self):
        for ghost in self.ghosts:
            if self.pacman.collide_ghost(ghost):
                if ghost.mode.current is FREIGHT:
                    self.pacman.visible = False
                    ghost.visible = False
                    self.update_score(ghost.points)
                    self.textgroup.add_text(str(ghost.points), WHITE, ghost.position.x, ghost.position.y, 8, time=1)
                    self.ghosts.update_points()
                    self.pause.set_pause(pause_time=1, func=self.show_entities)
                    ghost.start_spawn()
                    self.nodes.allow_home_access(ghost)
                elif ghost.mode.current is not SPAWN:
                    if self.pacman.alive:
                        self.lives -= 1
                        self.pacman.die()
                        self.ghosts.hide()
                        if self.lives <= 0:
                            self.textgroup.show_text(GAMEOVERTXT)
                            self.pause.set_pause(pause_time=1, func=self.restart_game)
                        else:
                            self.pause.set_pause(pause_time=1, func=self.reset_level)
                    
    def check_fruit_events(self):
        if self.pellets.num_eaten in [50, 140]:
            if self.fruit is None:
                self.fruit = Fruit(self.nodes.get_node_from_tiles(9, 20), self.nodes)
                self.pacman.fruit = self.fruit
        if self.fruit is not None:
            if self.pacman.collide_check(self.fruit):
                self.update_score(self.fruit.points)
                self.textgroup.add_text(str(self.fruit.points), WHITE, self.fruit.position.x, self.fruit.position.y, 8, time=1)
                self.fruit = None
            elif self.fruit.destroy:
                self.fruit = None
    
    def show_entities(self):
        self.pacman.visible = True
        self.ghosts.show()
        
    def hide_entities(self):
        self.pacman.visible = False
        self.ghosts.hide()
                
    def restart_game(self):
        self.lives = 3
        self.fruit = None
        self.start_game()
        
        self.score = 0
        self.textgroup.update_score(self.score)
        self.textgroup.show_text(READYTXT)
        
    def reset_level(self):
        self.pacman.reset()
        self.ghosts.reset()
        self.fruit = None
        self.textgroup.show_text(READYTXT)
    
    def update_score(self, points):
        self.score += points
        self.textgroup.update_score(self.score)
    
    def render(self):
        self.screen.blit(self.background, (0,0))
        self.nodes.render(self.screen)
        self.pellets.render(self.screen)
        if self.fruit is not None:
            self.fruit.render(self.screen)
        self.pacman.render(self.screen)
        self.ghosts.render(self.screen)
        self.textgroup.render(self.screen)
        pygame.display.update()        
    
    def update(self):
        dt = self.clock.tick(60) / 1000.0
        self.textgroup.update(dt)
        self.pellets.update(dt)
        if not self.pause.paused:
            self.pacman.update(dt)
            if self.fruit is not None:
                self.fruit.update(dt)
            self.ghosts.update(dt)
            self.check_pellet_events()
            self.check_ghost_events()
            self.check_fruit_events()
            
        after_pause_method = self.pause.update(dt)
        if after_pause_method is not None:
            after_pause_method()
        self.check_events()
        self.render()
        
if __name__ == "__main__":
    game = GameController()
    
    game.start_game()
    
    while True:
        game.update()