#!/usr/bin/env python
#some helper funtions
from shapely.ops import cascaded_union
import geopandas as gpd
from shapely.geometry import *
import copy
from compiler.ast import flatten
###########################public functions##############################
def flatArea(state):
    #return the flat area of the state
    area = 0.0
    for i in range(len(state['stack'])):
        area_tmp = 0.0
        for j in range(len(state['stack'][i])):
            facet = state['stack'][i][j]
            line = LineString(state['polygen'][facet])
            poly = Polygon(line)
            area_tmp += poly.area
        if area_tmp > area:
            area = area_tmp
    return area

def determineWeight(state2):
    #an edge connect state1 and state2
    #return the weight of this edge
    #4 situation score, divide flat area
    #weight is the score, the larger the better

    #1: valley, non-reflect
    if state2['fold'] == 'valley' and state2['reflect'] == 0:
        weight = 1
    #2: mountain, non-reflect
    if state2['fold'] == 'mountain' and state2['reflect'] == 0:
        weight = 2
    #3: valley, reflect
    if state2['fold'] == 'valley' and state2['reflect'] == 1 and state2['method'] == "flexflip":
        weight = 1
    #4: mountain, reflect
    if state2['fold'] == 'mountain' and state2['reflect'] == 1 and state2['method'] == "flexflip":
        weight = 2
    #5: reflect, scooping
    if state2['reflect'] == 1 and state2['method'] == "scooping":
        weight = 1000000000

    weight = weight / (flatArea(state2) /(420*210))
    #if overlap1
    # if state2['overlap'] == 1:
    #     weight = weight / 10
    #if overlap2
    if state2['overlap'] == 2:
        weight = 1000000000
    return weight
###########################public functions##############################



##########################origami reflection functions###############################
def ifOverlap(base,flap,polygon):
    #determine if the area of the base < the area of the flap
    #if yes, this fold is hard to execute, and the weight will increase
    #return 0 if flap < base
    #return 1 if flap = base
    #return 2 if flap > base
    base_area = 0.0
    flap_area = 0.0
    for i in range(len(base)):
        base_area_tmp = 0.0
        for j in range(len(base[i])):
            facet = base[i][j]
            line = LineString(polygon[facet])
            poly = Polygon(line)
            base_area_tmp += poly.area
        if base_area_tmp >= base_area:
            base_area = base_area_tmp
    for i in range(len(flap)):
        flap_area_tmp = 0.0
        for j in range(len(flap[i])):
            facet = flap[i][j]
            line = LineString(polygon[facet])
            poly = Polygon(line)
            flap_area_tmp += poly.area
        if flap_area_tmp >= flap_area:
            flap_area = flap_area_tmp
    if flap_area < base_area:
        return 0
    elif flap_area == base_area:
        return 1
    elif flap_area > base_area:
        return 2
##########################origami reflection functions###############################


################################bfs plan functions################################
def WeightedGraph(state_dict,state_graph):
    graph = {}
    for state in state_graph.keys():
        graph.setdefault(state,{})
        for kid in state_graph[state]:
            weight = determineWeight(state_dict[kid])
            # print "weight",weight
            graph[state].setdefault(kid,weight)
        #save the last node
        if len(state_graph[state]) == 1 and state_graph[state][0] not in state_graph.keys():
            graph.setdefault(state_graph[state][0],{})
    return graph

def CutedGraph(state_dict,state_graph_culled,unique_paths):
    #return non-symmetric state_graph
    graph = {}
    paths = flatten(unique_paths)
    for node1 in state_graph_culled.keys():
        if node1 in paths:
            graph.setdefault(node1,[])
            for node2 in state_graph_culled[node1]:
                if node2 in paths:
                    graph[node1].append(node2)
                    # #save the last node
                    # if node2 not in state_graph_culled.keys():
                    #     graph.setdefault(node2,[])

    return graph
#*******************************cut tree************************************#
def ifNodeSameorSymmetric(state_node1,state_node2):
    #determine if two nodes in the same layer are the same or symmetric
    # return 1 if yes
    #if stacks are the same, the nodes are the same
    def ifStacksSame(stack1,stack2):
        #return if two stacks are the same
        if len(stack1) != len(stack2):
            return 0
        else:
            for i in range(len(stack1)):
                s1 = stack1[i]
                s2 = stack2[i]
                if len(s1) != len(s2):
                    return 0
                for j in range(len(s1)):
                    s11 = sorted(s1[j])
                    s22 = sorted(s2[j])
                    if s11 != s22:
                        return 0
        return 1
    if ifStacksSame(state_node1['stack'],state_node2['stack']) == 1:
        return 1
    #if 'method' 'reflection' 'fold', any of which are different, the nodes are not same or symmetric
    if state_node1['method'] != state_node2['method']:
        return 0
    if state_node1['reflect'] != state_node2['reflect']:
        return 0
    if state_node1['fold'] != state_node2['fold']:
        return 0
    #if len(stack) are different, the nodes are different
    if len(state_node1['stack']) != len(state_node2['stack']):
        return 0
    else:
        # if each layer has the same area, the nodes are symmetric
        for i in range(len(state_node1['stack'])):
            area1 = 0.0
            area2 = 0.0
            stack1 = state_node1['stack'][i]
            stack2 = state_node2['stack'][i]
            for j in range(len(stack1)):
                facet = stack1[j]
                line = LineString(state_node1['polygen'][facet])
                poly = Polygon(line)
                area1 += poly.area
            for j in range(len(stack2)):
                facet = stack2[j]
                line = LineString(state_node2['polygen'][facet])
                poly = Polygon(line)
                area2 += poly.area
            if area1 != area2:
                return 0
        return 1

def ifPathSameorSymmetric(path1,path2,state_dict):
    #determine if two paths are the same or symmetric
    #if every nodes in path1 are the same or symmetric with nodes in path2, the two paths are the same
    #return 1 if yes
    if len(path1) != len(path2):
        return 0
    for i in range(len(path1)):
        node1 = path1[i]
        node2 = path2[i]
        if ifNodeSameorSymmetric(state_dict[node1],state_dict[node2]) == 0:
            return 0
    return 1

def cutedPaths(paths,state_dict):
    #return non-symmetric paths
    index = [] #store the indexes of symmetric paths
    unique_paths = []
    for i in range(len(paths)):
        #if j is searched before
        if i in index:
            continue
        path1 = paths[i]
        path = copy.deepcopy(path1)
        unique_paths.append(path)
        index.append(i)
        for j in range(i,len(paths)):
            #if j is searched before
            if j in index:
                continue
            path2 = paths[j]
            if ifPathSameorSymmetric(path1,path2,state_dict) == 1:
                index.append(j)

    return unique_paths
#*******************************cut tree************************************#
################################bfs plan functions################################

################################visualization functions################################
def decideRows(row_max,row):
    #use for drawing tree, decides the num of rows in each layer
    new_row = []
    if row_max % 2 == 0:
        for i in range(len(row)):
            if row[i] % 2 == 0:
                new_row.append(row_max*2)
            else:
                new_row.append(row_max*2-1)
    elif row_max % 2 == 1:
        for i in range(len(row)):
            if row[i] % 2 == 1:
                new_row.append(row_max*2)
            else:
                new_row.append(row_max*2-1)
    return new_row
# def drawTree(imgs,column,row,img_num):
#     # draw a search tree
#     gs0 = gridspec.GridSpec(column,1)
#     row_max = max(row)
#     print 'row_max',row_max
#     new_row = hp.decideRows(row_max,row)
#     gs1 = gridspec.GridSpecFromSubplotSpec(1,new_row[0],subplot_spec=gs0[0])
#     gs2 = gridspec.GridSpecFromSubplotSpec(1,new_row[1],subplot_spec=gs0[1])
#     gs3 = gridspec.GridSpecFromSubplotSpec(1,new_row[2],subplot_spec=gs0[2])
#     gs4 = gridspec.GridSpecFromSubplotSpec(1,new_row[3],subplot_spec=gs0[3])
#     gs5 = gridspec.GridSpecFromSubplotSpec(1,new_row[4],subplot_spec=gs0[4])
#     gs6 = gridspec.GridSpecFromSubplotSpec(1,new_row[5],subplot_spec=gs0[5])
#     # ax1 = plt.subplot(gs1[0,1])
#     # ax1.imshow(imgs[0][0])
#     plt.title("state1",fontsize=8)
#     plt.xticks([])
#     plt.yticks([])
#     num = 0
#     print 'new_row',new_row
#     for k in range(0,len(row)):
#         print 'row[k]',row[k]
#         for i in range(0,row[k]):
#             print 'i',2*i+int((new_row[k]+0.5)/2)-2*int((row[k]+0.5)/2)
#             if k == 0:
#                 ax = plt.subplot(gs1[0,2*i+int((new_row[k]+0.5)/2)-2*int((row[k]+0.5)/2)])
#             elif k == 1:
#                 ax = plt.subplot(gs2[0,2*i+int((new_row[k]+0.5)/2)-2*int((row[k]+0.5)/2)])
#             elif k == 2:
#                 ax = plt.subplot(gs3[0,2*i+int((new_row[k]+0.5)/2)-2*int((row[k]+0.5)/2)])
#             elif k == 3:
#                 ax = plt.subplot(gs4[0,2*i+int((new_row[k]+0.5)/2)-2*int((row[k]+0.5)/2)])
#             elif k == 4:
#                 ax = plt.subplot(gs5[0,2*i+int((new_row[k]+0.5)/2)-2*int((row[k]+0.5)/2)])
#             elif k == 5:
#                 ax = plt.subplot(gs6[0,2*i+int((new_row[k]+0.5)/2)-2*int((row[k]+0.5)/2)])
#             ax.imshow(imgs[num][0])
#             title = imgs[num][1]
#             num = num + 1
#             # title = "node" + str(num)
#             plt.title(title,fontsize=8)
#             plt.xticks([])
#             plt.yticks([])
#
#
#         # title = "node" + str(i)
#         # plt.title(title,fontsize=12)
#         # plt.xticks([])
#         # plt.yticks([])
#     plt.tight_layout()
################################visualization functions################################
