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
import unfold_visulization as uvl
# ################## fig.7 plane
# stack1 = [['2'], ['3'], ['4'], ['1'], ['8'], ['5'], ['6'], ['7']]
# #counterclock wise
# polygen1 = {'1': [[0, 105], [0, -45], [-75, -45], [-75, 30]],
#             '3': [[0, -45], [0, -105], [-75, -105], [-75, 30]],
#             '2': [[-75, 30], [-75, -45], [0, -45]],
#             '5': [[0, 105], [0, -105], [-75, -105], [-75, 30]],
#             '4': [[-75, 30], [-75, -105], [0, -105], [0, 105]],
#             '7': [[-75, 30], [0, -45], [-75, -45]],
#             '6': [[-75, 30], [-75, -105], [0, -105], [0, -45]],
#             '8': [[-75, 30], [-75, -45], [0, -45], [0, 105]]}
# facets1 = {'1': [],
#            '3': [],
#            '2': [],
#            '5': [],
#            '4': [],
#            '7': [],
#            '6': [],
#            '8': []}
# graph_edge = {'1': [[[-75,-45],[0,-45]],[[0,-45],[0,105]],[[-75,30],[0,105]],[[-75,-45],[-75,30]]],
#               '3': [[[0,-45], [0,-105]],[[0,-105],[-75,-105]],[[0,-45],[-75,30]],[[-75,-105],[-75,30]]],
#               '2': [[[-75,-45],[0,-45]],[[0,-45],[-75,30]],[[-75,-45],[-75,30]]],
#               '5': [[[0,-105],[-75,-105]],[[0,105],[-75,30]],[[0,105],[0,-105]],[[-75,-105],[-75,30]]],
#               '4': [[[-75, -105],[0,-105]],[[-75, 0],[0,105]],[[-75,-105],[-75,30]],[[0,105],[0,-105]]],
#               '7': [[[0,-45],[-75,-45]],[[-75,30],[0,-45]],[[-75, 45],[-75,30]]],
#               '6': [[[0,-105],[0,-45]],[[-75,-105],[0,-105]],[[-75,30],[0,-45]],[[-75,-105],[-75,30]]],
#               '8': [[[-75,-45],[0,-45]],[[0,-45],[0,105]],[[0,105],[-75,30]],[[-75,-45],[-75,30]]]}
# crease_edge = {'1': [[[-75, 30], [0, 105]], [[-75, -45], [-75, 30]]],
#                '3': [[[0, -45], [-75, 30]], [[-75, -105], [-75, 30]]],
#                '2': [[[0, -45], [-75, 30]], [[-75, -45], [-75, 30]]],
#                '5': [[[0, 105], [-75, 30]], [[0, 105], [0, -105]], [[-75, -105], [-75, 30]]],
#                '4': [[[-75, 30], [0, 105]], [[-75, -105], [-75, 30]], [[0, 105], [0, -105]]],
#                '7': [[[-75, 30], [0, -45]], [[-75, -45], [-75, 30]]],
#                '6': [[[-75, 30], [0, -45]], [[-75, -105], [-75, 30]]],
#                '8': [[[0, 105], [-75, 30]], [[-75, -45], [-75, 30]]]}
# adjacent_facets = {'1':['2','4'],
#                    '2':['1','3'],
#                    '3':['2','4'],
#                    '4':['1','3','5'],
#                    '5':['4','6','8'],
#                    '6':['5','7'],
#                    '7':['6','8'],
#                    '8':['5','7']}
# count = {'1': 1,
#          '3': 1,
#          '2': 2,
#          '5': 1,
#          '4': 0,
#          '7': 3,
#          '6': 2,
#          '8': 2}
#########################samurai hat
stack1 = [['16'],['18'],['4'],['5','6'],['15','17'],['12','14'],['7','9'],['8','10'],['11','13'],['1'],['2'],['3']]
polygen1 = {'1':[[45,75],[-45,75],[0,35]],
            '2':[[45,75],[-45,75],[-60,60],[60,60]],
            '3':[[75,75],[-75,75],[-60,60],[60,60]],
            '4':[[-75,75],[0,0],[75,75]],
            '5':[[-75,75],[0,0],[0,75]],
            '6':[[0,0],[75,75],[0,75]],
            '7':[[-75,75],[-25,25],[0,75]],
            '8':[[0,75],[-60,30],[-25,25]],
            '9':[[75,75],[0,75],[25,25]],
            '10':[[0,75],[25,25],[60,30]],
            '11':[[0,75],[-60,30],[-25,25]],
            '12':[[-75,75],[-25,25],[0,75]],
            '13':[[0,75],[25,25],[60,30]],
            '14':[[75,75],[0,75],[25,25]],
            '15':[[-75,75],[0,0],[0,75]],
            '16':[[-75,75],[0,0],[75,75]],
            '17':[[0,0],[75,75],[0,75]],
            '18':[[-75,75],[0,0],[75,75]]}
facets1 = {'1': [],'3': [],'2': [],'5': [],'4': [],'7': [],'6': [],'8': [],
           '9':[],'10':[],'11':[],'12':[],'13':[],'14':[],'15':[],'16':[],
           '17':[],'18':[]}
graph_edge = {'1':[[[45,75],[-45,75]],[[-45,75],[0,35]],[[0,35],[45,75]]],
              '2':[[[45,75],[-45,75]],[[-45,75],[-60,60]],[[-60,60],[60,60]],[[60,60],[45,75]]],
              '3':[[[75,75],[-75,75]],[[-75,75],[-60,60]],[[-60,60],[60,60]],[[60,60],[75,75]]],
              '4':[[[-75,75],[0,0]],[[0,0],[75,75]],[[75,75],[-75,75]]],
              '5':[[[-75,75],[0,0]],[[0,0],[0,75]],[[0,75],[-75,75]]],
              '6':[[[0,0],[75,75]],[[75,75],[0,75]],[[0,75],[0,0]]],
              '7':[[[-75,75],[-25,25]],[[-25,25],[0,75]],[[0,75],[-75,75]]],
              '8':[[[0,75],[-60,30]],[[-60,30],[-25,25]],[[-25,25],[0,75]]],
              '9':[[[75,75],[0,75]],[[0,75],[25,25]],[[25,25],[75,75]]],
              '10':[[[0,75],[25,25]],[[25,25],[60,30]],[[60,30],[0,75]]],
              '11':[[[0,75],[-60,30]],[[-60,30],[-25,25]],[[-25,25],[0,75]]],
              '12':[[[-75,75],[-25,25]],[[-25,25],[0,75]],[[0,75],[-75,75]]],
              '13':[[[0,75],[25,25]],[[25,25],[60,30]],[[60,30],[0,75]]],
              '14':[[[75,75],[0,75]],[[0,75],[25,25]],[[25,25],[75,75]]],
              '15':[[[-75,75],[0,0]],[[0,0],[0,75]],[[0,75],[-75,75]]],
              '16':[[[-75,75],[0,0]],[[0,0],[75,75]],[[75,75],[-75,75]]],
              '17':[[[0,0],[75,75]],[[75,75],[0,75]],[[0,75],[0,0]]],
              '18':[[[-75,75],[0,0]],[[0,0],[75,75]],[[75,75],[-75,75]]]}
crease_edge = {'1':[[[45,75],[-45,75]]],
              '2':[[[45,75],[-45,75]],[[-60,60],[60,60]]],
              '3':[[[75,75],[-75,75]],[[-60,60],[60,60]]],
              '4':[[[-75,75],[0,0]],[[0,0],[75,75]],[[75,75],[-75,75]]],
              '5':[[[-75,75],[0,0]],[[0,0],[0,75]],[[0,75],[-75,75]]],
              '6':[[[0,0],[75,75]],[[75,75],[0,75]],[[0,75],[0,0]]],
              '7':[[[-25,25],[0,75]],[[0,75],[-75,75]]],
              '8':[[[0,75],[-60,30]],[[-25,25],[0,75]]],
              '9':[[[75,75],[0,75]],[[0,75],[25,25]]],
              '10':[[[0,75],[25,25]],[[60,30],[0,75]]],
              '11':[[[0,75],[-60,30]],[[-25,25],[0,75]]],
              '12':[[[-25,25],[0,75]],[[0,75],[-75,75]]],
              '13':[[[0,75],[25,25]],[[60,30],[0,75]]],
              '14':[[[75,75],[0,75]],[[0,75],[25,25]]],
              '15':[[[-75,75],[0,0]],[[0,0],[0,75]],[[0,75],[-75,75]]],
              '16':[[[-75,75],[0,0]],[[0,0],[75,75]],[[75,75],[-75,75]]],
              '17':[[[0,0],[75,75]],[[75,75],[0,75]],[[0,75],[0,0]]],
              '18':[[[75,75],[-75,75]]]}
adjacent_facets = {'1':['2'],
                   '2':['1','3'],
                   '3':['2','4'],
                   '4':['3','5','6'],
                   '5':['4','7','15'],
                   '6':['4','9','17'],
                   '7':['5','8'],
                   '8':['7','11'],
                   '9':['6','10'],
                   '10':['9','13'],
                   '11':['8','12'],
                   '12':['11','15'],
                   '13':['10','14'],
                   '14':['13','17'],
                   '15':['5','12','16'],
                   '16':['15','17','18'],
                   '17':['6','14','16'],
                   '18':['16']}
count = {'1':3,'2':2,'3':1,'4':0,'5':1,'6':1,'7':2,'8':3,
         '9':2,'10':3,'11':4,'12':3,'13':4,'14':3,'15':2,
         '16':2,'17':2,'18':2}
state1 = {"stack":stack1,"polygen":polygen1,"facet_crease":facets1,
          "graph_edge":graph_edge,"crease_edge":crease_edge,
          "adjacent_facets":adjacent_facets,"count":count,'reflect':0}

state_dict = {"state1":state1}
state_graph = {"state1":[]}
# print '000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000'
# a = {'s':[[[75, 75], [-75, 75]], [[-60, 60], [60, 60]]],'b':[[[45, 75], [-45, 75]]]}
# print [[75, 75], [-75, 75]] in a.values()
# print [[75, 75], [-75, 75]] in a['s']
# print a.values(),type(a.values())
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
    while queue:
        mm=mm+1
        node = queue.popleft()
        # print "node",node
        state_node = state_dict[node]
        # print 'parent stack',state_node['stack']
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
                # print 'children stack',children_states[i]['stack']
                # print 'children_states',children_states
        # print "state graph",state_graph


        if node in state_graph.keys():
            for neighbor in state_graph[node]:
                if neighbor not in parents:
                    parents[neighbor] = node
                    queue.append(neighbor)
                    # print "stack_dict[neighbor][stack]",state_dict[neighbor]["stack"]
                    if len(state_dict[neighbor]["stack"]) == 1:
                        state_graph.setdefault(neighbor,[])
                        break

        if len(state_dict[neighbor]["stack"]) == 1:
            break


    # path = [node]
    # while parents[node] is not None:
    #     path.insert(0, parents[node])
    #     node = parents[node]
    path = [neighbor]
    while parents[neighbor] is not None:
        path.insert(0, parents[neighbor])
        neighbor = parents[neighbor]
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
# print 'nodes',len(state_graph)
# print "path",path
# img = uvl.VisualState(state_dict['state1'],state_dict['state1']['adjacent_facets'],state_dict['state1']['count'])
# uvl.drawOneFig(img)
# imgs=uvl.visualTree(state_graph,path,state_dict)
uvl.drawPolygon1(state_dict['state6'])