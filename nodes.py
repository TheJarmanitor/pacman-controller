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
        self.access = {UP:[PACMAN, BLINKY, PINKY, INKY, CLYDE, FRUIT],
                       DOWN:[PACMAN, BLINKY, PINKY, INKY, CLYDE, FRUIT],
                       LEFT:[PACMAN, BLINKY, PINKY, INKY, CLYDE, FRUIT],
                       RIGHT:[PACMAN, BLINKY, PINKY, INKY, CLYDE, FRUIT]}
        self.neighbors_cost = {}
        
    def deny_access(self, direction, entity):
        if entity.name in self.access[direction]:
            self.access[direction].remove(entity.name)

    def allow_access(self, direction, entity):
        if entity.name not in self.access[direction]:
            self.access[direction].append(entity.name)
        
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
        self.costs = self.get_nodes()
        
    def read_maze_file(self, textfile):
        return np.loadtxt(textfile, dtype='<U1')
    
    def create_node_table(self, data, xoffset=0, yoffset=0):
        for row in list(range(data.shape[0])):
            for col in list(range(data.shape[1])):
                if data[row][col] in self.node_symbols:
                    x, y = self.construct_key(col + xoffset, row + yoffset)
                    x, y = int(x), int(y)
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
    
    def deny_access(self, col, row, direction, entity):
        node = self.get_node_from_tiles(col, row)
        if node is not None:
            node.deny_access(direction, entity)

    def allow_access(self, col, row, direction, entity):
        node = self.get_node_from_tiles(col, row)
        if node is not None:
            node.allow_access(direction, entity)

    def deny_access_list(self, col, row, direction, entities):
        for entity in entities:
            self.deny_access(col, row, direction, entity)

    def allow_access_list(self, col, row, direction, entities):
        for entity in entities:
            self.allow_access(col, row, direction, entity)

    def deny_home_access(self, entity):
        self.nodes_LUT[self.homekey].deny_access(DOWN, entity)

    def allow_home_access(self, entity):
        self.nodes_LUT[self.homekey].allow_access(DOWN, entity)

    def deny_home_access_list(self, entities):
        for entity in entities:
            self.deny_home_access(entity)

    def allow_home_access_list(self, entities):
        for entity in entities:
            self.allow_home_access(entity)
                    
    def render(self, screen):
        for node in self.nodes_LUT.values():
            node.render(screen)
           
    ############################## djistkra functions ##############################
    
    def get_list_of_nodes_pixels(self):
        return list(self.nodes_LUT)
    
    def get_pixels_from_node(self, node):
        id = list(self.nodes_LUT.values()).index(node)
        list_of_pixels = self.get_list_of_nodes_pixels()
        return list_of_pixels[id]
    
    def get_neighors_obj(self, node):
        node_obj = self.get_node_from_pixels(node[0], node[1])
        return node_obj.neighbors 
            
    def get_neighbors(self, node):
        neighbors_obj = self.get_neighors_obj(node)
        values = neighbors_obj.values()
        neighbors_obj_2 = []
        for direction in values:
            if direction is not None:
                neighbors_obj_2.append(direction)
        list_neighbors = []
        for neighbor in neighbors_obj_2:
            # print(self.get_pixels_from_node(neighbor))
            list_neighbors.append(self.get_pixels_from_node(neighbor))
        return list_neighbors
    
    def get_nodes(self):
        cost_dict = {}
        list_of_nodes_pixels = self.get_list_of_nodes_pixels() 
        for node in list_of_nodes_pixels:
            # pixels = self.get_node_from_pixels(*node)
            neighbors = self.get_neighors_obj(node)
            temp_neighbors = neighbors.values()
            temp_list = []
            for direction in temp_neighbors:
                if direction is not None:
                     temp_list.append(1)
                else:
                    temp_list.append(None)
            
            cost_dict[node] = temp_list
            
        return cost_dict