from room import Room
from player import Player
from world import World
from util import Stack
from util import Queue
from util import Graph

import random
from ast import literal_eval

# Load world
world = World()


# You may uncomment the smaller graphs for development and testing purposes.
# map_file = "maps/test_line.txt"
# map_file = "maps/test_cross.txt"
# map_file = "maps/test_loop.txt"
# map_file = "maps/test_loop_fork.txt"
map_file = "maps/main_maze.txt"

# Loads the map into a dictionary
room_graph=literal_eval(open(map_file, "r").read())
world.load_graph(room_graph)

# Print an ASCII map
world.print_rooms()

player = Player(world.starting_room)

# Fill this out with directions to walk
# traversal_path = ['n', 'n']
traversal_path = []

# U- Understand: 
    # - Run a dfs to map out the world and create a an adjacency list, find the path to the room
    # - Create an adjacency list from the dfs traversal path and run bfs to find the shortest route
# P- Plan:
    # - Use get_exits to add neighbors to the stack
    # - Travel A single direction until it can no longer be traveled, travel next direction
    # - Record location of id when traveling, When no longer able to travel, reverse direction, get neighbors


# Execute: 

# helper function to verify paths have been visited
def check_paths(graph):
    # for every room in graph
    for room in graph:
        # for each direction in a room
        for direction in graph[room]:
            # see if path is unchecked
            if graph[room][direction] == '?':
                return True
    return False

# helper function path to room
def path_to_room(graph, starting_room, ending_room):
    # create a queue to keep track of the path to our mystery room
    neighbors_to_visit = Queue()
    # enqueue the starting node
    neighbors_to_visit.enqueue([(starting_room, 'none')])
    # create a set for visited rooms
    visited = set()
    # while the queue is not empty
    while neighbors_to_visit.size() > 0:
        # there's something in the queue, run it
        current_path = neighbors_to_visit.dequeue()
        # grab the last room from the path
        current_room = current_path[-1][0]
        # if it hasn't been visited 
        if current_room not in visited:
            # check if it is our target
            if current_room == ending_room:
                # if so, return the path we took to get here
                return current_path
            # mark the room visited
            visited.add(current_room)
            # check all paths in our room
            for travel_direction in graph[current_room]:
                # if we still need to visit the room in this direction
                if graph[current_room][travel_direction] != '?' and graph[current_room][travel_direction] not in visited:
                    path_copy = current_path.copy()
                    # add the path and the neighbor to the queue
                    path_copy.append((graph[current_room][travel_direction], travel_direction))
                    neighbors_to_visit.enqueue(path_copy)

# helper function for travel
def user_travel(availablePaths, paths):
    # if can go north, go north
    if 'n' in availablePaths and paths['n'] == '?':
        player.travel('n')
        return 'n' 
    # if can't go north, go south
    elif 's' in availablePaths and paths['s'] == '?':
        player.travel('s')
        return 's' 
    # if can't go north or south, go east
    elif 'e' in availablePaths and paths['e'] == '?':
        player.travel('e')
        return 'e' 
    # if can't go north, south, or east, go west
    elif 'w' in availablePaths and paths['w'] == '?':
        player.travel('w')
        return 'w' 
    # if can't go north, east, south or west, there has been an issue
    else:
        raise IndexError('Error: no valid directions in which user can travel')

# helper function for traveling backwards
def reverse_dir(direction):
    reverse_directions = {'n':'s', 'e':'w', 's':'n', 'w':'e'}
    
    return reverse_directions[direction]

# the main code 
def traversal():
    # graph object to map room linkages
    graph_of_rooms = {}
    # variable to store our complete path
    complete_path = []
    # variable for id of previous_room
    previous_room = -1
    # set a variable for the current room
    current_room = player.current_room.id
    # to keep track of our movements
    moved = 'none'
    moved_reverse = 'none'
    # stack for paths needed to visit
    rooms_to_visit = Stack()

    i = 0 # safety break for while loop
    # create a loop
    while True:
        # set current room
        current_room = player.current_room.id
        # get all the available exits for current room using Player class 
        availablePaths = player.current_room.get_exits()

        # if we have moved from our initial room
        if moved != 'none':
            # add to graph the move we made
            graph_of_rooms[previous_room][moved] = current_room
            # get the opposite direction of the direction we moved
            moved_reverse = reverse_dir(moved)
            # record our movement in the complete path
            complete_path.append(moved)
        # if previous room has unvisited paths
        if previous_room != -1:
            # for every direction in the room
            for direction in graph_of_rooms[previous_room]:
                # if the direction is unexplored
                if graph_of_rooms[previous_room][direction] == '?':
                    # add it to the stack of rooms need to visit
                    rooms_to_visit.push((previous_room, direction))
        # if the room is not yet in our graph of rooms, add it
        if current_room not in graph_of_rooms:
            #  add room as dictionary in our graph of rooms dictionary 
            graph_of_rooms[current_room] = {}
            # for the direction available from this room
            for direction in availablePaths:
                # if the direction is the one we came from
                if direction == moved_reverse:
                    # we don't want to revisit it, add it to the dict
                    graph_of_rooms[current_room][direction] = previous_room
                else:
                    # add the ? for next room to the graph
                    graph_of_rooms[current_room][direction] = '?'

        # are there paths remaining from the previous step?
        paths_remaining = False
        for direction in graph_of_rooms[current_room]:
            if graph_of_rooms[current_room][direction] == '?':
                paths_remaining = True
                
        # if all paths were not explored for the room 
        if paths_remaining:
            # set the current room as the previous one
            previous_room = current_room
            # travel again direction
            moved = user_travel(availablePaths, graph_of_rooms[current_room])
        else:
            # get the next value from the stack
            ending_room = rooms_to_visit.pop()

            # revisit the last unexplored path
            visiting_next = path_to_room(graph_of_rooms, current_room, ending_room[0])
            # for each in the path
            for index in range(1, len(visiting_next)):
                # travel
                player.travel(visiting_next[index][1])
                # add to path
                complete_path.append(visiting_next[index][1])
            # clean our variables
            moved = 'none'
            moved_reverse = 'none'
            previous_room = ending_room[0]

        # stop the function if something is going wrong (we have looped too many times)
        i += 1
        if i > 15000:
            break
        # check if any path direction still has an unknown room
        if check_paths(graph_of_rooms) is False:
            # once all the paths have been evaluated, we can end our loop and return the path to the room
            break

    return complete_path

traversal_path = traversal()



# TRAVERSAL TEST - DO NOT MODIFY
visited_rooms = set()
player.current_room = world.starting_room
visited_rooms.add(player.current_room)

for move in traversal_path:
    player.travel(move)
    visited_rooms.add(player.current_room)

if len(visited_rooms) == len(room_graph):
    print(f"TESTS PASSED: {len(traversal_path)} moves, {len(visited_rooms)} rooms visited")
else:
    print("TESTS FAILED: INCOMPLETE TRAVERSAL")
    print(f"{len(room_graph) - len(visited_rooms)} unvisited rooms")



#######
# UNCOMMENT TO WALK AROUND
# #######
# player.current_room.print_room_description(player)
# while True:
#     cmds = input("-> ").lower().split(" ")
#     if cmds[0] in ["n", "s", "e", "w"]:
#         player.travel(cmds[0], True)
#     elif cmds[0] == "q":
#         break
#     else:
#         print("I did not understand that command.")
