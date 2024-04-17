from constants import *

class MazeBase(object):
    def __init__(self):
        self.name = ""
        self.portal_pairs = {}
        self.homeoffset = []
        self.homenodeconnect_left = []
        self.homenodeconnect_right = []
        self.pacman_start = []
        self.fruit_start = []
        self.ghost_node_deny = {UP:None, DOWN:None, LEFT:None, RIGHT:None}

    def setup(self, nodegroup, pacman, ghostgroup):
        self.set_portals(nodegroup)
        self.deny_access(nodegroup, pacman, ghostgroup)

    def deny_access(self, nodegroup, pacman, ghostgroup):
        nodegroup.deny_home_access(pacman)
        nodegroup.deny_home_access_list(ghostgroup)
        x, y = self.addoffset(2, 3)
        nodegroup.deny_access_list(x, y, LEFT, ghostgroup)
        nodegroup.deny_access_list(x, y, RIGHT, ghostgroup)

        for direction in list(self.ghost_node_deny.keys()):
            if self.ghost_node_deny[direction] is not None:
                for x, y in self.ghost_node_deny[direction]:
                    nodegroup.deny_access_list(x, y, direction, ghostgroup)


    def get_pacman_start_node(self, nodegroup):
        pacstartkey = nodegroup.construct_key(*self.pacman_start)
        return nodegroup.nodes_lUT[pacstartkey]

    def get_blinky_start_node(self, nodegroup):
        return self.get_ghost_start(nodegroup, 2, 0)

    def get_pinky_start_node(self, nodegroup):
        return self.get_ghost_start(nodegroup, 2, 3)

    def get_inky_start_node(self, nodegroup):
        return self.get_ghost_start(nodegroup, 0, 3)

    def get_clyde_start_node(self, nodegroup):
        return self.get_ghost_start(nodegroup, 4, 3)

    def get_ghost_start(self, nodegroup, x, y):
        key = nodegroup.construct_key(*self.addoffset(x, y))
        return nodegroup.nodes_lUT[key]

    def get_spawn_node(self, nodegroup):
        spawnkey = nodegroup.construct_key(*self.addoffset(2, 3))
        return nodegroup.nodes_lUT[spawnkey]

    def get_fruit_node(self, nodegroup):
        key = nodegroup.construct_key(*self.fruit_start)
        return nodegroup.nodes_lUT[key]

    def set_portals(self, nodegroup):
        for key in list(self.portal_pairs.keys()):
            p1, p2 = self.portal_pairs[key]
            nodegroup.set_portal_pair(p1, p2)

    def connect_home_nodes(self, nodegroup):
        homekey = nodegroup.create_home_nodes(*self.homeoffset)
        nodegroup.connect_home_nodes(homekey, self.homenodeconnect_left, LEFT)
        nodegroup.connect_home_nodes(homekey, self.homenodeconnect_right, RIGHT)

    def addoffset(self, x, y):
        return x+self.homeoffset[0], y+self.homeoffset[1]

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
        self.ghost_node_deny = {UP:((12, 14), (15, 14), (12, 26), (15, 26))}

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
        self.ghost_node_deny = {UP:((9, 14), (18, 14), (11, 23), (16, 23))}

class MazeController(object):
    def __init__(self):
        self.mazedict = {0:Maze1, 1:Maze2}

    def load_maze(self, level):
        return self.mazedict[level%len(self.mazedict)]()