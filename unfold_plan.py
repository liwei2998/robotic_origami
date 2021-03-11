#!/usr/bin/env python
"""
Input consists of a simple graph of { node: [list of neighbors] } plus a source and target node.
"""

from collections import deque
import origami_reflection as osg
import origami_unfold as ou
import copy
import visulization as vl
import math
import matplotlib.pyplot as plt
import time
import helper as hp

################## fig.7 plane
stack1 = [['2'], ['3'], ['4'], ['1'], ['8'], ['5'], ['6'], ['7']]
#counterclock wise
polygen1 = {'1': [[0, 105], [0, -45], [-75, -45], [-75, 30]],
            '3': [[0, -45], [0, -105], [-75, -105], [-75, 30]],
            '2': [[-75, 30], [-75, -45], [0, -45]],
            '5': [[0, 105], [0, -105], [-75, -105], [-75, 30]],
            '4': [[-75, 30], [-75, -105], [0, -105], [0, 105]],
            '7': [[-75, 30], [0, -45], [-75, -45]],
            '6': [[-75, 30], [-75, -105], [0, -105], [0, -45]],
            '8': [[-75, 30], [-75, -45], [0, -45], [0, 105]]}
facets1 = {'1': [],
           '3': [],
           '2': [],
           '5': [],
           '4': [],
           '7': [],
           '6': [],
           '8': []}
graph_edge = {'1': [[[-75,-45],[0,-45]],[[0,-45],[0,105]],[[-75,30],[0,105]],[[-75,-45],[-75,30]]],
              '3': [[[0,-45], [0,-105]],[[0,-105],[-75,-105]],[[0,-45],[-75,30]],[[-75,-105],[-75,30]]],
              '2': [[[-75,-45],[0,-45]],[[0,-45],[-75,30]],[[-75,-45],[-75,30]]],
              '5': [[[0,-105],[-75,-105]],[[0,105],[-75,30]],[[0,105],[0,-105]],[[-75,-105],[-75,30]]],
              '4': [[[-75, -105],[0,-105]],[[-75, 0],[0,105]],[[-75,-105],[-75,30]],[[0,105],[0,-105]]],
              '7': [[[0,-45],[-75,-45]],[[-75,30],[0,-45]],[[-75, 45],[-75,30]]],
              '6': [[[0,-105],[0,-45]],[[-75,-105],[0,-105]],[[-75,30],[0,-45]],[[-75,-105],[-75,30]]],
              '8': [[[-75,-45],[0,-45]],[[0,-45],[0,105]],[[0,105],[-75,30]],[[-75,-45],[-75,30]]]}
crease_edge = {'1': [[[-75, 30], [0, 105]], [[-75, -45], [-75, 30]]],
               '3': [[[0, -45], [-75, 30]], [[-75, -105], [-75, 30]]],
               '2': [[[0, -45], [-75, 30]], [[-75, -45], [-75, 30]]],
               '5': [[[0, 105], [-75, 30]], [[0, 105], [0, -105]], [[-75, -105], [-75, 30]]],
               '4': [[[-75, 30], [0, 105]], [[-75, -105], [-75, 30]], [[0, 105], [0, -105]]],
               '7': [[[-75, 30], [0, -45]], [[-75, -45], [-75, 30]]],
               '6': [[[-75, 30], [0, -45]], [[-75, -105], [-75, 30]]],
               '8': [[[0, 105], [-75, 30]], [[-75, -45], [-75, 30]]]}
adjacent_facets = {'1':['2','4'],
                   '2':['1','3'],
                   '3':['2','4'],
                   '4':['1','3','5'],
                   '5':['4','6','8'],
                   '6':['5','7'],
                   '7':['6','8'],
                   '8':['5','7']}
count = {'1': 1,
         '3': 1,
         '2': 2,
         '5': 1,
         '4': 0,
         '7': 3,
         '6': 2,
         '8': 2}
state1 = {"stack":stack1,"polygen":polygen1,"facet_crease":facets1,
          "graph_edge":graph_edge,"crease_edge":crease_edge,
          "adjacent_facets":adjacent_facets,"count":count}

state_dict = {"state1":state1}
state_graph = {"state1":[]}

def bfs(state_graph, src):
    """Return the shortest path from the source (src) to the target (tgt) in the graph"""

    if src in state_graph is False:
        raise AttributeError("The source '%s' is not in the graph" % src)


    parents = {src: None}
    queue = deque([src])
    k = 2
    # #dynamic generate variable's names, using locals()
    # names = locals()
    mm = 1
    while mm<8:
        mm=mm+1
        node = queue.popleft()
        print "node",node
        state_node = state_dict[node]
        print 'parent stack',state_node['stack']
        # generate children states for this node
        children_states = ou.get_next_layer_states(state_node)
        # print "children states",children_states

        if len(children_states) != 0:
            for i in range(len(children_states)):
                #store each children states
                state_dict["state"+str(k)] = children_states[i]
                #add children states to state_graph
                state_graph.setdefault(node,[]).append("state"+str(k))
                k += 1
                print 'children stack',children_states[i]['stack']
                print 'children_states',children_states
        # print "state graph",state_graph

        if node in state_graph.keys():
            for neighbor in state_graph[node]:
                if neighbor not in parents:
                    parents[neighbor] = node
                    queue.append(neighbor)
                    # print "stack_dict[neighbor][stack]",state_dict[neighbor]["stack"]
                    if len(state_dict[neighbor]["stack"]) == 1:
                        break
        else:
            if len(state_dict[neighbor]["stack"]) == 1:
                break


    path = [node]
    while parents[node] is not None:
        path.insert(0, parents[node])
        node = parents[node]

    return path

def findPath(state_graph=state_graph,src="state1"):
    start_time = time.time()
    path = bfs(state_graph,src)
    total_time = time.time() - start_time
    print "###########################search time: ",total_time
    # print "path",path
    stack_step = []
    for i in range(len(path)):
        step_tmp = copy.deepcopy(state_dict[path[i]]["stack"])
        stack_step.append(step_tmp)
    # print "stack step",stack_step
    return path,stack_step,state_dict

path,stack_step,state_dict = findPath()
# print 'state',state_dict[path[-1]]
print "bfs path",path
