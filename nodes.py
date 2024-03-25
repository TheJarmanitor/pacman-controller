import pygame
import numpy as np
from vector import Vector2
from constants import *

class Node(object):
    def __init__(self, x, y):
        self.position = Vector2(x, y)
        self.neighbors = {
            UP: None,
            DOWN: None,
            LEFT: None,
            RIGHT: None,
            PORTAL: None
        }
    def render(self, screen):
        for n in self.neighbors.keys():
            if self.neighbors[n] is not None and n != PORTAL:
                line_start = self.position.as_tuple()
                line_end = self.neighbors[n].position.as_tuple()
                pygame.draw.line(screen, WHITE, line_start, line_end, 4)
                pygame.draw.circle(screen, RED, self.position.as_int(), 12)
                
class NodeGroup(object):
    def __init__(self, level) -> None:
        self.level = level
        self.nodes_LUT = {}
        self.node_symbols = ['+', 'P', 'n']
        self.path_symbols = ['.', '-', '|', 'p']
        data = self.read_maze_file(level)
        self.create_node_table(data)
        self.connect_horizontally(data)
        self.connect_vertically(data)
        self.homekey = None
        
    def read_maze_file(self, textfile):
        return np.loadtxt(textfile, dtype='<U1')
    
    def create_node_table(self, data, xoffset=0, yoffset=0):
        for row in list(range(data.shape[0])):
            for col in list(range(data.shape[1])):
                if data[row][col] in self.node_symbols:
                    x, y = self.construct_key(col + xoffset, row + yoffset)
                    self.nodes_LUT[(x,y)] = Node(x, y)
                    
    def construct_key(self, x, y):
        return x * TILEWIDTH, y * TILEHEIGHT
    
    
    
    def connect_horizontally(self, data, xoffset=0, yoffset=0):
        for row in list(range(data.shape[0])):
            key = None
            for col in list(range(data.shape[1])):
                if data[row][col] in self.node_symbols:
                    if key is None:
                        key = self.construct_key(col+xoffset, row+yoffset)
                    else:
                        otherkey = self.construct_key(col+xoffset, row+yoffset)
                        self.nodes_LUT[key].neighbors[RIGHT] = self.nodes_LUT[otherkey]
                        self.nodes_LUT[otherkey].neighbors[LEFT] = self.nodes_LUT[key]
                        key = otherkey
                elif data[row][col] not in self.path_symbols:
                    key = None


                    
    def connect_vertically(self, data, xoffset=0, yoffset=0):
        data_t = data.transpose()
        for col in list(range(data_t.shape[0])):
            key = None
            for row in list(range(data_t.shape[1])):
                if data_t[col][row] in self.node_symbols:
                    if key is None:
                        key = self.construct_key(col+xoffset, row+yoffset)
                    else:
                        otherkey = self.construct_key(col+xoffset, row+yoffset)
                        self.nodes_LUT[key].neighbors[DOWN] = self.nodes_LUT[otherkey]
                        self.nodes_LUT[otherkey].neighbors[UP] = self.nodes_LUT[key]
                        key = otherkey
                elif data_t[col][row] not in self.path_symbols:
                    key = None
    def set_portal_pair(self, pair1, pair2):
        key_1 = self.construct_key(*pair1)
        key_2 = self.construct_key(*pair2)
        if key_1 in self.nodes_LUT.keys() and key_2 in self.nodes_LUT.keys():
            self.nodes_LUT[key_1].neighbors[PORTAL] = self.nodes_LUT[key_2]
            self.nodes_LUT[key_2].neighbors[PORTAL] = self.nodes_LUT[key_1]
    
    def create_home_nodes(self, xoffset, yoffset):
        homedata = np.array([['X','X','+','X','X'],
                             ['X','X','.','X','X'],
                             ['+','X','.','X','+'],
                             ['+','.','+','.','+'],
                             ['+','X','X','X','+']])
        self.create_node_table(homedata, xoffset, yoffset)
        self.connect_horizontally(homedata, xoffset, yoffset)
        self.connect_vertically(homedata, xoffset, yoffset)
        self.homekey = self.construct_key(2 + xoffset, yoffset)
        return self.homekey
    
    def connect_home_nodes(self, homekey, otherkey, direction):
        key = self.construct_key(*otherkey)
        self.nodes_LUT[homekey].neighbors[direction] = self.nodes_LUT[key]
        self.nodes_LUT[key].neighbors[direction * -1] = self.nodes_LUT[homekey]
                    
    def get_node_from_pixels(self, xpixel, ypixel):
        if (xpixel, ypixel) in self.nodes_LUT.keys():
            return self.nodes_LUT[(xpixel, ypixel)]
        return None
    
    def get_node_from_tiles(self, col, row):
        x, y = self.construct_key(col, row)
        if (x, y) in self.nodes_LUT.keys():
            return self.nodes_LUT[(x, y)]
        return None
    
    def get_start_temp_node(self):
        nodes = list(self.nodes_LUT.values())
        return nodes[0]
                    
    def render(self, screen):
        for node in self.nodes_LUT.values():
            node.render(screen)
            
            
            
        
