#!/usr/bin/env python
"""
Input consists of a simple graph of { node: [list of neighbors] } plus a source and target node.
"""

from collections import deque
import origami_reflection as osg
import copy
import visulization as vl
import math
import matplotlib.pyplot as plt
import time
import helper as hp
#################### simple hat
# rot = [[0,-1,0],[1,0,0],[0,0,1]]
# stack1 = [['1','2','3','4','5','6','7','8']]
# # #counterclock wise
# polygen1 = {"1":[[-105,105],[105,105],[105,150],[-105,150]],
#             "2":[[0,0],[105,105],[-105,105]],
#             "3":[[0,0],[-105,105],[-105,0]],
#             "4":[[0,0],[105,0],[105,105]],
#             "5":[[0,0],[-105,0],[-105,-105]],
#             "6":[[0,0],[-105,-105],[105,-105]],
#             "7":[[0,0],[105,-105],[105,0]],
#             "8":[[-105,-105],[-105,-150],[105,-150],[105,-105]]
#             }
# facets1 = {"1":[[[-105,105],[105,105]]],
#            "2":[[[0,0],[105,105]],[[105,105],[-105,105]],[[-105,105],[0,0]]],
#            "3":[[[0,0],[-105,105]],[[-105,0],[0,0]]],
#            "4":[[[0,0],[105,0]],[[105,105],[0,0]]],
#            "5":[[[0,0],[-105,0]],[[-105,-105],[0,0]]],
#            "6":[[[0,0],[-105,-105]],[[-105,-105],[105,-105]],[[105,-105],[0,0]]],
#            "7":[[[0,0],[105,-105]],[[105,0],[0,0]]],
#            "8":[[[105,-105],[-105,-105]]]
#            }
# graph_edge = {"1":[[[105,105],[105,150]],[[105,150],[-105,150]],[[-105,150],[-105,105]]],
#               # "2":[[[-150,30],[-150,-45]]],
#               "3":[[[-105,105],[-105,0]]],
#               "4":[[[105,0],[105,105]]],
#               "5":[[[-105,0],[-105,-105]]],
#               # "6":[[[150,-105],[150,-45]],[[75,-105],[150,-105]]],
#               "7":[[[105,-105],[105,0]]],
#               "8":[[[-105,-105],[-105,-150]],[[-105,-150],[105,-150]],[[105,-150],[105,-105]]]}
# crease_edge = {}
# adjacent_facets = {'1':['2'],
#                    '2':['1','3','4'],
#                    '3':['2','5'],
#                    '4':['2','7'],
#                    '5':['3','6'],
#                    '6':['5','7','8'],
#                    '7':['6','4'],
#                    '8':['6']}
# crease_angle = {'1':{'2':'+'},
#                 '2':{'1':'+','3':'-','4':'-'},
#                 '3':{'2':'-','5':'-'},
#                 '4':{'2':'-','7':'-'},
#                 '5':{'3':'-','6':'+'},
#                 '6':{'5':'+','7':'+','8':'+'},
#                 '7':{'6':'+','4':'-'},
#                 '8':{'6':'+'}}
# ##############plane
# stack1 = [['1','2','3','4'],['5','6','7','8']]
# #counterclock wise
# polygen1 = {"1":[[0,105],[-150,105],[-150,30],[-75,30]],
#             "2":[[-75,30],[-150,30],[-150,-45]],
#             "3":[[-150,-45],[-150,-105],[-75,-105],[-75,30]],
#             "4":[[-75,30],[-75,-105],[0,-105],[0,105]],
#             "5":[[-75,30],[-75,-105],[0,-105],[0,105]],
#             "6":[[-150,-45],[-150,-105],[-75,-105],[-75,30]],
#             "7":[[-75,30],[-150,30],[-150,-45]],
#             "8":[[0,105],[-150,105],[-150,30],[-75,30]]
#             }
# facets1 = {"1":[[[-150,30],[-75,30]],[[-75,30],[0,105]]],
#            "2":[[[-150,-45],[-75,30]],[[-75,30],[-150,30]]],
#            "3":[[[-75,-105],[-75,30]],[[-75,30],[-150,-45]]],
#            "4":[[[-75,30],[-75,-105]],[[0,105],[-75,30]]],
#            "5":[[[-75,30],[-75,-105]],[[0,105],[-75,30]]],
#            "6":[[[-75,-105],[-75,30]],[[-75,30],[-150,-45]]],
#            "7":[[[-150,-45],[-75,30]],[[-75,30],[-150,30]]],
#            "8":[[[-150,30],[-75,30]],[[-75,30],[0,105]]]
#            }
#
# graph_edge = {"1":[[[-150,30],[-150,105]],[[-150,105],[0,105]]],
#               "2":[[[-150,30],[-150,-45]]],
#               "3":[[[-150,-45],[-150,-105]],[[-150,-105],[-75,-105]]],
#               "4":[[[-75,-105],[0,-105]],[[0,-105],[0,105]]],
#               "5":[[[-75,-105],[0,-105]],[[0,-105],[0,105]]],
#               "6":[[[-150,-45],[-150,-105]],[[-150,-105],[-75,-105]]],
#               "7":[[[-150,30],[-150,-45]]],
#               "8":[[[-150,30],[-150,105]],[[-150,105],[0,105]]]}
# crease_edge={'5': [[[0,-105],[0,105]]],
#              # '7': [[[-75, 30], [-150, -45]]],
#              # '6': [[[-75, 30], [-150, -45]]],
#              '4': [[[0,-105], [0,105]]]}
# adjacent_facets = {'1':['2','4'],
#                    '2':['1','3'],
#                    '3':['2','4'],
#                    '4':['1','3','5'],
#                    '5':['4','6','8'],
#                    '6':['5','7'],
#                    '7':['6','8'],
#                    '8':['5','7']}
################## fig.1 simple folds
# facets1 = {"1":[[[100,100],[0,0]],[[0,0],[-100,100]]],
#           "2":[[[100,100],[0,0]],[[0,0],[100,-100]]],
#           "3":[[[0,0],[100,-100]],[[0,0],[-100,-100]]],
#           "4":[[[0,0],[-100,-100]],[[0,0],[-100,100]]]}
#
# polygen1 = {"1":[[100,100],[0,0],[-100,100]],
#             "2":[[100,100],[100,-100],[0,0]],
#             "3":[[100,-100],[0,0],[-100,-100]],
#             "4":[[0,0],[-100,-100],[-100,100]]}
# stack1 = [["1","2","3","4"]]
################### fig.7 plane
# stack1 = [['1','2','3','4','5','6','7','8']]
# #counterclock wise
# polygen1 = {"1":[[0,105],[-150,105],[-150,30],[-75,30]],
#             "2":[[-75,30],[-150,30],[-150,-45]],
#             "3":[[-150,-45],[-150,-105],[-75,-105],[-75,30]],
#             "4":[[-75,30],[-75,-105],[0,-105],[0,105]],
#             "5":[[0,105],[0,-105],[75,-105],[75,30]],
#             "6":[[75,30],[75,-105],[150,-105],[150,-45]],
#             "7":[[75,30],[150,-45],[150,30]],
#             "8":[[75,30],[150,30],[150,105],[0,105]]
#             }
# facets1 = {"1":[[[-150,30],[-75,30]],[[-75,30],[0,105]]],
#            "2":[[[-150,-45],[-75,30]],[[-75,30],[-150,30]]],
#            "3":[[[-75,-105],[-75,30]],[[-75,30],[-150,-45]]],
#            "4":[[[-75,30],[-75,-105]],[[0,-105],[0,105]],[[0,105],[-75,30]]],
#            "5":[[[0,105],[0,-105]],[[75,-105],[75,30]],[[75,30],[0,105]]],
#            "6":[[[75,30],[75,-105]],[[150,-45],[75,30]]],
#            "7":[[[75,30],[150,-45]],[[150,30],[75,30]]],
#            "8":[[[75,30],[150,30]],[[0,105],[75,30]]]
#            }
# graph_edge = {"1":[[[-150,30],[-150,105]],[[-150,105],[0,105]]],
#               "2":[[[-150,30],[-150,-45]]],
#               "3":[[[-150,-45],[-150,-105]],[[-150,-105],[-75,-105]]],
#               "4":[[[-75,-105],[0,-105]]],
#               "5":[[[0,-105],[75,-105]]],
#               "6":[[[150,-105],[150,-45]],[[75,-105],[150,-105]]],
#               "7":[[[150,-45],[150,30]]],
#               "8":[[[150,30],[150,105]],[[150,105],[0,105]]]}
# crease_edge = {}
# adjacent_facets = {'1':['2','4'],
#                    '2':['1','3'],
#                    '3':['2','4'],
#                    '4':['1','3','5'],
#                    '5':['4','6','8'],
#                    '6':['5','7'],
#                    '7':['6','8'],
#                    '8':['5','7']}
# # crease_angle = {'1':{'2':'-','4':'-'},
# #                 '2':{'1':'-','3':'-'},
# #                 '3':{'2':'-','4':'-'},
# #                 '4':{'1':'-','3':'-','5':'+'},
# #                 '5':{'4':'+','8':'-','6':'-'},
# #                 '6':{'5':'-','7':'-'},
# #                 '7':{'6':'-','8':'+'},
# #                 '8':{'7':'+','5':'-'}}
# # crease_angle = {'1':{'2':'-','4':'+'},
# #                 '2':{'1':'-','3':'+'},
# #                 '3':{'2':'+','4':'-'},
# #                 '4':{'1':'+','3':'-','5':'+'},
# #                 '5':{'4':'+','8':'+','6':'-'},
# #                 '6':{'5':'-','7':'+'},
# #                 '7':{'6':'+','8':'-'},
# #                 '8':{'7':'-','5':'+'}}
# crease_angle = {'1':{'2':'+','4':'+'},
#                 '2':{'1':'+','3':'+'},
#                 '3':{'2':'+','4':'-'},
#                 '4':{'1':'+','3':'-','5':'+'},
#                 '5':{'4':'+','8':'+','6':'-'},
#                 '6':{'5':'-','7':'+'},
#                 '7':{'6':'+','8':'+'},
#                 '8':{'7':'+','5':'+'}}
# ################### fig7. cup
stack1 = [['1','2','3','4','5','6','7','8']]
# #counterclock wise
polygen1 = {"1":[[105,105],[0,210],[-105,105]],
            "2":[[-70,0],[-105,105],[-210,0]],
            "3":[[-70,0],[70,0],[105,105],[-105,105]],
            "4":[[210,0],[105,105],[70,0]],
            "5":[[-70,0],[-210,0],[-105,-105]],
            "6":[[-70,0],[-105,-105],[105,-105],[70,0]],
            "7":[[210,0],[70,0],[105,-105]],
            "8":[[105,-105],[-105,-105],[0,-210]]
            }
facets1 = {"1":[[[-105,105],[105,105]]],
           "2":[[[-210,0],[-70,0]],[[-70,0],[-105,105]]],
           "3":[[[-70,0],[70,0]],[[70,0],[105,105]],[[105,105],[-105,105]],[[-105,105],[-70,0]]],
           "4":[[[70,0],[210,0]],[[105,105],[70,0]]],
           "5":[[[-105,-105],[-70,0]],[[-70,0],[-210,0]]],
           "6":[[[-70,0],[-105,-105]],[[-105,-105],[105,-105]],[[105,-105],[70,0]],[[70,0],[-70,0]]],
           "7":[[[210,0],[70,0]],[[70,0],[105,-105]]],
           "8":[[[105,-105],[-105,-105]]]
           }
adjacent_facets = {'1':['3'],
                   '2':['3','5'],
                   '3':['1','2','4','6'],
                   '4':['3','7'],
                   '5':['2','6'],
                   '6':['3','5','7','8'],
                   '7':['4','6'],
                   '8':['6']}
crease_edge = {}
graph_edge = {'1':[[[105,105],[0,210]],[[0,210],[-105,105]]],
              '2':[[[-105,105],[-210,0]]],
              '4':[[[210,0],[105,105]]],
              '5':[[[-210,0],[-105,-105]]],
              '7':[[[105,-105],[210,0]]],
              '8':[[[-105,-105],[0,-210]],[[0,-210],[105,-105]]]}
crease_angle = {'1':{'3':'+'},
                '2':{'3':'+','5':'-'},
                '3':{'1':'+','2':'+','4':'+','6':'-'},
                '4':{'3':'+','7':'-'},
                '5':{'2':'-','6':'-'},
                '6':{'5':'-','7':'-','3':'-','8':'+'},
                '7':{'6':'-','4':'-'},
                '8':{'6':'+'}}
count = {'1':0,
         '2':0,
         '3':0,
         '4':0,
         '5':0,
         '6':0,
         '7':0,
         '8':0}
state1 = {"stack":stack1,"polygen":polygen1,"facet_crease":facets1,
          "graph_edge":graph_edge,"crease_edge":crease_edge,
          "adjacent_facets":adjacent_facets,"fold":"valley","reflect":0,"crease_angle":crease_angle,
          "count":count,"overlap":0,"method":"flexflip"}

state_dict = {"state1":state1}
state_graph = {"state1":[]}
state_graph_culled = {'state1':[]}

def ifTwoNodesSame(state_node1,state_node2):
    # if the stacks are the same, then the two nodes are the same
    stack1_tmp = state_node1["stack"]
    stack2_tmp = state_node2["stack"]
    if len(stack1_tmp) != len(stack2_tmp):
        return 0
    else:
        for i in range(len(stack1_tmp)):
            s1 = sorted(stack1_tmp[i])
            s2 = sorted(stack2_tmp[i])
            if s1 != s2:
                return 0
        return 1

def ifNodeVisit(state_node,state_dict):
    # test if the node is the same as node that has been visited
    for state in state_dict.keys():
        state_node1 = state_dict[state]
        if ifTwoNodesSame(state_node1,state_node) == 1:
            return 1,state
    return 0,'state0'

def bfs(state_graph, src, tgt_stack):
    """Return the shortest path from the source (src) to the target (tgt) in the graph"""

    if src in state_graph is False:
        raise AttributeError("The source '%s' is not in the graph" % src)


    parents = {src: None}
    queue = deque([src])
    k = 2
    # #dynamic generate variable's names, using locals()
    # names = locals()
    mm = 1
    while queue:
        mm=mm+1
        node = queue.popleft()
        # print "node",node
        state_node = state_dict[node]
        # generate children states for this node
        children_states = osg.generateNextLayerStates(state_node)
        # print "children states",children_states
        if len(children_states) != 0:
            for i in range(len(children_states)):
                a,state = ifNodeVisit(children_states[i],state_dict)
                # if a == 1:
                #     state_graph_culled.setdefault(node,[]).append(state)
                #     continue
                #store each children states
                state_dict["state"+str(k)] = children_states[i]
                #add children states to state_graph
                state_graph.setdefault(node,[]).append("state"+str(k))
                state_graph_culled.setdefault(node,[]).append("state"+str(k))
                k += 1
        elif len(children_states) == 0:
            # state_graph.setdefault(node,[])
            state_graph_culled.setdefault(node,[])
        # print "state graph",state_graph

        if node in state_graph.keys():
            for neighbor in state_graph[node]:
                if neighbor not in parents:
                    parents[neighbor] = node
                    queue.append(neighbor)
                    # print "stack_dict[neighbor][stack]",state_dict[neighbor]["stack"]
                    if state_dict[neighbor]["stack"] == tgt_stack:
                        break
        else:
            if state_node["stack"] == tgt_stack:
                break


    path = [node]
    while parents[node] is not None:
        path.insert(0, parents[node])
        node = parents[node]

    return path
# simple hat
# goal = [['1'],['2'],['6'],['7','5'],['4','3'],['8']]
#fig.5 simple fold
# path = bfs(state_graph,"state1",[['3'],['4'],['1'],['2']])
# fig.7 plane
# path = bfs(state_graph,"state1",[['2'],['3'],['4'],['1'],['8'],['5'],['6'],['7']])
# reflection plane [['3'],['2'],['1'],['4'],['5'],['8'],['7'],['6']]
#fig.7 cup
# path = bfs(state_graph,"state1",[['8'],['6'],['3'],['4'],['7'],['2'],['5'],['1']])
#fig.7 cup_deprecated
# path = bfs(state_graph,"state1",[['4'],['7'],['2'],['5'],['8'],['6'],['3'],['1']])
###### print "state_graph",state_graph["state175"]
###### print "state175",state_dict['state175']["stack"]
# print "path",path

def findPath(state_graph=state_graph,src="state1",goal_stack=[['8'],['6'],['3'],['4'],['7'],['2'],['5'],['1']]):
    start_time = time.time()
    path = bfs(state_graph,src,goal_stack)
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
# print "bfs path",path
# print 'stack',stack_step
# img = osg.VisualState(state_dict['state8'],adjacent_facets,state_dict["state7"]["count"])
# vl.drawOneFig(img)
# print 'count',state_dict['state13']['count']
# vl.visualParentChildren(state_graph_culled,"state2",state_dict,adjacent_facets)
# vl.visualParentChildren(state_graph_culled,"state4",state_dict,adjacent_facets)
# print "stack step",stack_step
# print "graph",state_graph['state2'],state_graph_culled['state2']
# print "state_graph_culled",state_graph_culled
# imgs=vl.visualTree(state_graph,path,state_dict)
# vl.drawGraph(state_dict,state_graph_culled,path)
# vl.visualSteps(state_dict,path)

def dijkstra(graph, start, end):
    # empty dictionary to hold distances
    distances = {}
    # list of vertices in path to current vertex
    predecessors = {}

    # get all the nodes that need to be assessed
    to_assess = graph.keys()

    # set all initial distances to infinity
    #  and no predecessor for any node
    for node in graph:
        distances[node] = float('inf')
        predecessors[node] = None

    # set the initial collection of
    # permanently labelled nodes to be empty
    sp_set = []

    # set the distance from the start node to be 0
    distances[start] = 0

    # as long as there are still nodes to assess:
    while len(sp_set) < len(to_assess):

        # chop out any nodes with a permanent label
        still_in = {node: distances[node]\
                    for node in [node for node in\
                    to_assess if node not in sp_set]}

        # find the closest node to the current node
        closest = min(still_in, key = distances.get)

        # and add it to the permanently labelled nodes
        sp_set.append(closest)

        # then for all the neighbours of
        # the closest node (that was just added to
        # the permanent set)
        for node in graph[closest]:
            # if a shorter path to that node can be found
            if distances[node] > distances[closest] +\
                       graph[closest][node]:

                # update the distance with
                # that shorter distance
                distances[node] = distances[closest] +\
                       graph[closest][node]

                # set the predecessor for that node
                predecessors[node] = closest

    # once the loop is complete the final
    # path needs to be calculated - this can
    # be done by backtracking through the predecessors
    path = [end]
    while start not in path:

        path.append(predecessors[path[-1]])

    # return the path in order start -> end, and it's cost
    return path[::-1], distances[end]

def findDijkstraFromTree(state_dict,graph,init_end):
    #find the optimal path from a tree
    #init_end is the first goal state found by bfs
    dijkstra_dis = 10000
    for end in graph.keys():
        if state_dict[end]['stack'] == state_dict[init_end]['stack']:
            path, dis = dijkstra(graph,'state1',end)
            if dis < dijkstra_dis:
                dijkstra_path = path
                dijkstra_dis = dis
    return dijkstra_path,dijkstra_dis

def findAllPathsFromTree(state_dict,graph,init_end,pattern='cup'):
    paths = []
    diss = []
    tmp = 0
    for end in state_dict.keys():
        if len(state_dict[end]['stack']) == len(state_dict[init_end]['stack']):
            path,dis = dijkstra(graph,'state1',end)
            for i in range(len(path)-1):
                # node1 = path[i]
                node2 = path[i+1]
                # print 'weight',hp.determineWeight(state_dict[node1],state_dict[node2])
                if hp.determineWeight(state_dict[node2]) >= 1000000000:
                    tmp = 1
                    break
            if tmp == 1:
                tmp = 0
                continue
            paths.append(path)
            diss.append(dis)
    return paths,diss

graph = hp.WeightedGraph(state_dict,state_graph_culled)
# print 'weighted graph',graph
# vl.visualSteps(state_dict,path)
#####################################cut1: cut larger bottom facet configurations and scoop reflection##########################################
imgs=vl.visualTree(state_graph_culled,path,state_dict)
# vl.drawGraph(state_dict,state_graph_culled,path)
####################################cut2: cut paths that cannot reach the goal###############################
paths,dis = findAllPathsFromTree(state_dict,graph,path[-1])
# print 'path',paths, dis
# cuted_state_graph = hp.CutedGraph(state_dict,state_graph_culled,paths)
# imgs=vl.visualTree(cuted_state_graph,path,state_dict,pattern='cup')
# vl.drawGraph(state_dict,cuted_state_graph,path)
###################################cut 3: cut symmetric paths########################################
unique_paths = hp.cutedPaths(paths,state_dict)
cuted_state_graph = hp.CutedGraph(state_dict,state_graph_culled,unique_paths)
# print 'unique paths',unique_paths
# imgs=vl.visualTree(cuted_state_graph,path,state_dict)
# vl.drawGraph(state_dict,cuted_state_graph,path)
#######################dijkstra path
graph1 = hp.WeightedGraph(state_dict,cuted_state_graph)
# print 'unique_paths[0][-1]',unique_paths[0][-1]
dijkstra_path, dijkstra_dis = findDijkstraFromTree(state_dict,graph1,path[-1])
# print 'dijkstra_path',dijkstra_path
# print 'dijkstra_dis',dijkstra_dis
# imgs=vl.visualTree(cuted_state_graph,path,state_dict)
# vl.visualSteps(state_dict,dijkstra_path)
