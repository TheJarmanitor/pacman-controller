from constants import *

class MazeBase(object):
    def __init__(self):
        self.portal_pairs = {}
        self.homeoffset = (0, 0)
        self.ghost_node_deny = {UP:(), DOWN:(), LEFT:(), RIGHT:()}

    def set_portal_pairs(self, nodes):
        for pair in list(self.portal_pairs.values()):
            nodes.set_portal_pair(*pair)

    def connect_home_nodes(self, nodes):
        key = nodes.create_home_nodes(*self.homeoffset)
        nodes.connect_home_nodes(key, self.homenodeconnect_left, LEFT)
        nodes.connect_home_nodes(key, self.homenodeconnect_right, RIGHT)

    def add_offset(self, x, y):
        return x+self.homeoffset[0], y+self.homeoffset[1]

    def deny_ghosts_access(self, ghosts, nodes):
        nodes.deny_access_list(*(self.add_offset(2, 3) + (LEFT, ghosts)))
        nodes.deny_access_list(*(self.add_offset(2, 3) + (RIGHT, ghosts)))

        for direction in list(self.ghost_node_deny.keys()):
            for values in self.ghost_node_deny[direction]:
                nodes.deny_access_list(*(values + (direction, ghosts)))


class Maze1(MazeBase):
    def __init__(self):
        MazeBase.__init__(self)
        self.name = "maze1"
        self.portal_pairs = {0:((0, 17), (27, 17))}
        self.homeoffset = (11.5, 14)
        self.homenodeconnect_left = (12, 14)
        self.homenodeconnect_right = (15, 14)
        self.pacman_start = (15, 26)
        self.fruit_start = (9, 20)
        self.ghost_node_deny = {UP:((12, 14), (15, 14), (12, 26), (15, 26)), LEFT:(self.add_offset(2, 3),),
                              RIGHT:(self.add_offset(2, 3),)}


class Maze2(MazeBase):
    def __init__(self):
        MazeBase.__init__(self)
        self.name = "maze2"
        self.portal_pairs = {0:((0, 4), (27, 4)), 1:((0, 26), (27, 26))}
        self.homeoffset = (11.5, 14)
        self.homenodeconnect_left = (9, 14)
        self.homenodeconnect_right = (18, 14)
        self.pacman_start = (16, 26)
        self.fruit_start = (11, 20)
        self.ghost_node_deny = {UP:((9, 14), (18, 14), (11, 23), (16, 23)), LEFT:(self.add_offset(2, 3),),
                              RIGHT:(self.add_offset(2, 3),)}


class MazeData(object):
    def __init__(self):
        self.obj = None
        self.mazedict = {0:Maze1, 1:Maze2}

    def load_maze(self, level):
        self.obj = self.mazedict[level%len(self.mazedict)]()
