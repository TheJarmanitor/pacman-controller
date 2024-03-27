import sys

def dijkstra(nodes, start_node):
    unvisited_nodes = list(nodes.costs)
    shortet_path = {}
    previous_nodes = {}
    
    max_value = sys.maxsize
    
    for node in unvisited_nodes:
        shortet_path[node] = max_value
    shortet_path[start_node] = 0
    
    while unvisited_nodes:
        current_min_node = None
        for node in unvisited_nodes:
            if current_min_node is None:
                current_min_node = node
            elif shortet_path[node] < shortet_path[current_min_node]:
                current_min_node = node
                
        neighbors = nodes.get_neighbors(current_min_node)
        for neighbor in neighbors:
            tentative_value = shortet_path[current_min_node] + 1
            if tentative_value < shortet_path[neighbor]:
                shortet_path[neighbor] = tentative_value
                previous_nodes[neighbor] = current_min_node
                
        unvisited_nodes.remove(current_min_node)
        
    return previous_nodes, shortet_path

def print_result(previous_nodes, shortest_path, start_node, target_node):
    path = []
    node = target_node
    
    while node != start_node:
        path.append(node)
        node = previous_nodes[node]
 
    # Add the start node manually
    path.append(start_node)
    
    print("We found the following best path with a value of {}.".format(shortest_path[target_node]))
    print(path)
    
    
### A* algorithm

def heuristic(node1, node2):
    # manhattan distance
    return abs(node1[0] - node2[0]) + abs(node1[1] - node2[1])


def dijkstra_or_a_star(nodes, start_node, a_star=False):
    unvisited_nodes = list(nodes.costs)
    print(unvisited_nodes)
    
    shortest_path = {}
    previous_nodes = {}

    max_value = sys.maxsize
    for node in unvisited_nodes:
        shortest_path[node] = max_value
    shortest_path[start_node] = 0
    # print(shortest_path)

    while unvisited_nodes:
        current_min_node = None
        for node in unvisited_nodes:
            if current_min_node is None:
                current_min_node = node
            elif shortest_path[node] < shortest_path[current_min_node]:
                current_min_node = node

        neighbors = nodes.get_neighbors(current_min_node)
        # print(shortest_path)
        for neighbor in neighbors:
            if a_star:
                tentative_value = shortest_path[current_min_node] 
                + heuristic(current_min_node,neighbor) 
            else:
                tentative_value = shortest_path[current_min_node] + 1
                
            if neighbor not in shortest_path.keys():
                 shortest_path[neighbor] = max_value
            if tentative_value < shortest_path[neighbor]:
                shortest_path[neighbor] = tentative_value
                # We also update the best path to the current node
                previous_nodes[neighbor] = current_min_node
    
        # After visiting its neighbors, we mark the node as "visited"
        unvisited_nodes.remove(current_min_node)
    return previous_nodes, shortest_path
    
    