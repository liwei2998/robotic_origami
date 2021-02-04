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

#################### simple hat
# # rot = [[0,-1,0],[1,0,0],[0,0,1]]
# stack1 = [['1','2','3','4','5','6','7','8']]
# #counterclock wise
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
#################### fig.7 plane
# global stack2
# global polygen2
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
graph_edge = {"1":[[[-150,30],[-150,105]],[[-150,105],[0,105]]],
              "2":[[[-150,30],[-150,-45]]],
              "3":[[[-150,-45],[-150,-105]],[[-150,-105],[-75,-105]]],
              "4":[[[-75,-105],[0,-105]]],
              "5":[[[0,-105],[75,-105]]],
              "6":[[[150,-105],[150,-45]],[[75,-105],[150,-105]]],
              "7":[[[150,-45],[150,30]]],
              "8":[[[150,30],[150,105]],[[150,105],[0,105]]]}
crease_edge = {}
adjacent_facets = {'1':['2','4'],
                   '2':['1','3'],
                   '3':['2','4'],
                   '4':['1','3','5'],
                   '5':['4','6','8'],
                   '6':['5','7'],
                   '7':['6','8'],
                   '8':['5','7']}
crease_angle = {'1':{'2':'+','4':'-'},
                '2':{'1':'+','3':'-'},
                '3':{'2':'-','4':'-'},
                '4':{'1':'-','3':'-','5':'+'},
                '5':{'4':'+','8':'-','6':'-'},
                '6':{'5':'-','7':'-'},
                '7':{'6':'-','8':'+'},
                '8':{'7':'+','5':'-'}}
# ################### fig7. cup
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
# adjacent_facets = {'1':['3'],
#                    '2':['3','5'],
#                    '3':['1','2','4','6'],
#                    '4':['3','7'],
#                    '5':['2','6'],
#                    '6':['3','5','7','8'],
#                    '7':['4','6'],
#                    '8':['1']}
# crease_edge = {}
# graph_edge = {'1':[[[50,50],[0,100]],[[0,100],[-50,50]]],
#               '2':[[[-50,50],[-100,0]]],
#               '4':[[[100,0],[50,50]]],
#               '5':[[[-100,0],[-50,-50]]],
#               '7':[[[100,0],[50,-50]]],
#               '8':[[[50,-50],[0,-100]],[[0,-100],[-50,-50]]]}
# state1 = {"stack":stack1,"polygen":polygen1,"facet_crease":facets1}
state1 = {"stack":stack1,"polygen":polygen1,"facet_crease":facets1,
          "graph_edge":graph_edge,"crease_edge":crease_edge,
          "adjacent_facets":adjacent_facets,"fold":"valley","reflect":0,"crease_angle":crease_angle,
          "count":0}

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
        a=a+1
        node = queue.popleft()
        # print "node",node
        state_node = state_dict[node]

        # generate children states for this node
        children_states = osg.generateNextLayerStates(state_node,state1["adjacent_facets"],state1["crease_angle"])
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

#,polygen2=polygen2,stack2=stack2s
def visualSteps(state_dict,path):
    img_num = len(path) #+ 1
    print "img num",img_num
    row = 3
    if img_num % row == 0:
        column = int(img_num/3)
    else:
        column = int(img_num/3) + 1
    print "column",column
    # w = 350 #plane
    # h = 320 #plane
    # w = 250 #cup
    # h = 250 #cup
    # w = 300 #fig5
    # h = 300 #fig5
    w = 450
    h = 350
    imgs=[]
    count = 0
    # canvas = vl.init_canvas(w,h)
    # rot_mat = vl.rotationFromImg(w,h,0)
    # img=vl.drawPolygon(polygen2,stack2,canvas,rot_mat,0,count=0)
    # imgs.append(img)
    for i in range(len(path)):
        canvas = vl.init_canvas(w,h)
        rot_mat = vl.rotationFromImg(w,h,0)
        fold = state_dict[path[i]]["fold"]
        stack = state_dict[path[i]]["stack"]
        if i == 0:
            stack2 = state_dict[path[0]]["stack"]
        else:
            stack2 = state_dict[path[i-1]]["stack"]
        if fold == "mountain" and (len(stack2)-len(stack)) % 2 == 1:
            count = count + 1

        img=vl.drawPolygon(state_dict[path[i]]["polygen"],stack,canvas,rot_mat,fold,count)
        imgs.append(img)
    vl.drawMultiFigs(imgs,column,row,img_num)
    plt.show()

def findPath(state_graph=state_graph,src="state1",goal_stack=[['3'],['2'],['1'],['4'],['5'],['8'],['7'],['6']]):
    path = bfs(state_graph,src,goal_stack)
    # print "path",path
    stack_step = []
    for i in range(len(path)):
        step_tmp = copy.deepcopy(state_dict[path[i]]["stack"])
        stack_step.append(step_tmp)
    # print "stack step",stack_step
    return path,stack_step,state_dict

def visualParentChildren(state_graph,parent_state,state_dict,adjacent_facets):
    # visualize parent and its children
    imgs = []
    count = state_dict[parent_state]["count"]
    img = osg.VisualState(state_dict[parent_state],adjacent_facets,count)
    # vl.drawOneFig(img)
    imgs.append(img)
    for node in state_graph[parent_state]:
        count = state_dict[node]["count"]
        img = osg.VisualState(state_dict[node],adjacent_facets,count)
        imgs.append(img)
    vl.drawMultiFigsGraph(imgs,len(state_graph[parent_state]))
    plt.show()

def visualTree(state_graph,path,state_dict):
    #visualize a tree
    column = len(path)
    row = [1]
    src = ['state1']
    imgs = []
    for i in range(column):
        src_list_tmp = []
        row_tmp = 0
        for j in src:
            # print "j",j
            img = osg.VisualState(state_dict[j],state1["adjacent_facets"],state_dict[j]["count"])
            img_tmp = copy.deepcopy(img)
            imgs.append(img_tmp)
            if j not in state_graph.keys():
                continue
            row_tmp = row_tmp + len(state_graph[j])
            src_tmp = state_graph[j]
            src_list_tmp.append(src_tmp)
        src = [x for j in src_list_tmp for x in j]
        row.append(row_tmp)
    # print "columnnn",column
    row = row[:column]
    # print "rowwww",row
    img_num = sum(row)
    # print "imgss",len(imgs)
    # print "img num",img_num
    vl.drawTree(imgs,column,row,img_num)
    plt.show()
    return imgs



path,stack_step,state_dict = findPath()
print "path",path
# img = osg.VisualState(state_dict['state8'],adjacent_facets,state_dict["state7"]["count"])
# vl.drawOneFig(img)
# state_dict["state4"]["reflect"]=1
# visualParentChildren(state_graph,"state8",state_dict,adjacent_facets)
# for i in range(len(path)):
#     print "state dict",state_dict[path[i]]
print "stack step",stack_step
print "graph",state_graph
imgs=visualTree(state_graph,path,state_dict)
# vl.drawOneFig(imgs[9])
# visualSteps(state_dict,path)
# for i in range(1,46):
#     node = "state"+str(i)
#     print "state dict",state_dict[node]["reflect"]
# print "path",path
