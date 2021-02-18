#!/usr/bin/env python
#some helper funtions
from shapely.ops import cascaded_union
import geopandas as gpd
from shapely.geometry import *
import copy
###########################public functions##############################
def determineWeight(state1,state2):
    #an edge connect state1 and state2
    #return the weight of this edge
    # 8 kinds of transitions
    #weight is the distance, the lower the better

    #1: flexflip, valley, non-reflect
    if state2['method'] == 'flexflip' and state2['fold'] == 'valley' and state2['reflect'] == 0:
        weight = 1
    #2: flexflip, valley, reflect
    if state2['method'] == 'flexflip' and state2['fold'] == 'valley' and state2['reflect'] == 1:
        weight = 5
    #3: flexflip, mountain, non-reflect
    if state2['method'] == 'flexflip' and state2['fold'] == 'mountain' and state2['reflect'] == 0:
        weight = 3
    #4: flexflip, mountain, reflect
    if state2['method'] == 'flexflip' and state2['fold'] == 'mountain' and state2['reflect'] == 1:
        weight = 7
    #5: scooping, valley, non-reflect
    if state2['method'] == 'scooping' and state2['fold'] == 'valley' and state2['reflect'] == 0:
        weight = 2
    #6: scooping, valley, reflect
    if state2['method'] == 'scooping' and state2['fold'] == 'valley' and state2['reflect'] == 1:
        weight = 6
    #7: scooping, mountain, non-reflect
    if state2['method'] == 'scooping' and state2['fold'] == 'mountain' and state2['reflect'] == 0:
        weight = 4
    #8: scooping, mountain, reflect
    if state2['method'] == 'scooping' and state2['fold'] == 'mountain' and state2['reflect'] == 1:
        weight = 8
    #if overlap 1
    if state2['overlap'] == 1:
        weight = weight + 10
    #if overlap2
    if state2['overlap'] == 2:
        weight = weight + 20
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
            weight = determineWeight(state_dict[state],state_dict[kid])
            # print "weight",weight
            graph[state].setdefault(kid,weight)
        #save the last node
        if len(state_graph[state]) == 1 and state_graph[state][0] not in state_graph.keys():
            graph.setdefault(state_graph[state][0],{})
    return graph

#*******************************cut tree************************************#
def ifNodeSameorSymmetric(state_node1,state_node2):
    #determine if two nodes in the same layer are the same or symmetric
    # return 1 if yes
    #if stacks are the same, the nodes are the same
    if state_node1['stack'] == state_node2['stack']:
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

def cutPaths(paths,state_dict):
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
