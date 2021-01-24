#!/usr/bin/env python
"""
Input consists of a simple graph of { node: [list of neighbors] } plus a source and target node.
"""

from collections import deque
import origami_state_generation as osg
import copy
import visulization as vl
import math
import matplotlib.pyplot as plt
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
#################### fig.7 plane
stack1 = [['1','2','3','4','5','6','7','8']]
#counterclock wise
polygen1 = {"1":[[0,105],[-150,105],[-150,30],[-75,30]],
            "2":[[-75,30],[-150,30],[-150,-45]],
            "3":[[-150,-45],[-150,-105],[-75,-105],[-75,30]],
            "4":[[-75,30],[-75,-105],[0,-105],[0,105]],
            "5":[[0,105],[0,-105],[75,-105],[75,30]],
            "6":[[75,30],[75,-105],[150,-105],[150,-45]],
            "7":[[75,30],[150,-45],[150,30]],
            "8":[[75,30],[150,30],[150,105],[0,105]]
            }
facets1 = {"1":[[[-150,30],[-75,30]],[[-75,30],[0,105]]],
           "2":[[[-150,-45],[-75,30]],[[-75,30],[-150,30]]],
           "3":[[[-75,-105],[-75,30]],[[-75,30],[-150,-45]]],
           "4":[[[-75,30],[-75,-105]],[[0,-105],[0,105]],[[0,105],[-75,30]]],
           "5":[[[0,105],[0,-105]],[[75,-105],[75,30]],[[75,30],[0,105]]],
           "6":[[[75,30],[75,-105]],[[150,-45],[75,30]]],
           "7":[[[75,30],[150,-45]],[[150,30],[75,30]]],
           "8":[[[75,30],[150,30]],[[0,105],[75,30]]]
           }
################### fig7. cup
# stack1 = [['1','2','3','4','5','6','7','8']]
# #counterclock wise
# polygen1 = {"1":[[50,50],[0,100],[-50,50]],
#             "2":[[-33,0],[-50,50],[-100,0]],
#             "3":[[-33,0],[-50,50],[50,50],[33,0]],
#             "4":[[100,0],[50,50],[33,0]],
#             "5":[[-33,0],[-100,0],[-50,-50]],
#             "6":[[-33,0],[-50,-50],[50,-50],[33,0]],
#             "7":[[100,0],[50,-50],[33,0]],
#             "8":[[50,-50],[0,-100],[-50,-50]]
#             }
# facets1 = {"1":[[[-50,50],[50,50]]],
#            "2":[[[-100,0],[-33,0]],[[-33,0],[-50,50]]],
#            "3":[[[-50,50],[-33,0]],[[-33,0],[33,0]],[[33,0],[50,50]],[[50,50],[-50,50]]],
#            "4":[[[50,50],[33,0]],[[33,0],[100,0]]],
#            "5":[[[-50,-50],[-33,0]],[[-33,0],[-100,0]]],
#            "6":[[[-33,0],[-50,-50]],[[-50,-50],[50,-50]],[[50,-50],[33,0]],[[33,0],[-33,0]]],
#            "7":[[[100,0],[33,0]],[[33,0],[50,-50]]],
#            "8":[[[50,-50],[-50,-50]]]
#            }
state1 = {"stack":stack1,"polygen":polygen1,"facet_crease":facets1}
state_dict = {"state1":state1}
state_graph = {"state1":[]}

def bfs(state_graph, src, tgt_stack):
    """Return the shortest path from the source (src) to the target (tgt) in the graph"""

    if src in state_graph is False:
        raise AttributeError("The source '%s' is not in the graph" % src)


    parents = {src: None}
    queue = deque([src])
    k = 2
    # #dynamic generate variable's names, using locals()
    # names = locals()
    a = 1
    while queue:
        a = a+1
        node = queue.popleft()
        # print "node",node
        state_node = state_dict[node]
        # generate children states for this node
        children_states = osg.generateNextLayerStates(state_node)
        # print "children states",children_states
        if len(children_states) != 0:
            for i in range(len(children_states)):
                #store each children states
                state_dict["state"+str(k)] = children_states[i]
                #add children states to state_graph
                state_graph.setdefault(node,[]).append("state"+str(k))
                k += 1
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

#fig.5 simple fold
# path = bfs(state_graph,"state1",[['3'],['4'],['1'],['2']])
# fig.7 plane
# path = bfs(state_graph,"state1",[['2'],['3'],['4'],['1'],['8'],['5'],['6'],['7']])
#fig.7 cup
# path = bfs(state_graph,"state1",[['8'],['6'],['3'],['4'],['7'],['2'],['5'],['1']])
#fig.7 cup_deprecated
# path = bfs(state_graph,"state1",[['4'],['7'],['2'],['5'],['8'],['6'],['3'],['1']])
###### print "state_graph",state_graph["state175"]
###### print "state175",state_dict['state175']["stack"]
# print "path",path
# stack_step = []
# for i in range(len(path)):
#     step_tmp = copy.deepcopy(state_dict[path[i]]["stack"])
#     stack_step.append(step_tmp)
# print "stack step",stack_step

def visualSteps(state_dict,path):
    img_num = len(path)
    column = int(img_num/4)+1
    row = 3
    w = 350 #plane
    h = 320 #plane
    w = 250 #cup
    h = 250 #cup
    w = 300 #fig5
    h = 300 #fig5
    imgs=[]
    for i in range(len(path)):
        canvas = vl.init_canvas(w,h)
        rot_mat = vl.rotationFromImg(w,h)
        img=vl.drawPolygon(state_dict[path[i]]["polygen"],state_dict[path[i]]["stack"],canvas,rot_mat)
        imgs.append(img)
    vl.drawMultiFigs(imgs,column,row)
    plt.show()

def findPath(state_graph=state_graph,src="state1",goal_stack=[['2'],['3'],['4'],['1'],['8'],['5'],['6'],['7']]):
    path = bfs(state_graph,src,goal_stack)
    # print "path",path
    stack_step = []
    for i in range(len(path)):
        step_tmp = copy.deepcopy(state_dict[path[i]]["stack"])
        stack_step.append(step_tmp)
    # print "stack step",stack_step
    return path,stack_step,state_dict

# path,stack_step,state_dict = findPath()
# visualSteps(state_dict,path)
