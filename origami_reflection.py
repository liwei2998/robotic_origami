#!/usr/bin/env python
import numpy_indexed as npi
from shapely.geometry import *
import copy
import numpy as np
import visulization as vl
import matplotlib.pyplot as plt
from compiler.ast import flatten
# ##############plane
# stack1 = [['1','2','3','4'],['5','6'],['7','8']]
# #counterclock wise
# polygen1 = {"1":[[0,105],[-150,105],[-150,30],[-75,30]],
#             "2":[[-75,30],[-150,30],[-150,-45]],
#             "3":[[-150,-45],[-150,-105],[-75,-105],[-75,30]],
#             "4":[[-75,30],[-75,-105],[0,-105],[0,105]],
#             "5":[[-75,30],[-75,-105],[0,-105],[0,105]],
#             "6":[[-150,-45],[-150,-105],[-75,-105],[-75,30]],
#             "7":[[-75,30],[-75,-45],[-150,-45]],
#             "8":[[0,105],[0,-45],[-75,-45],[-75,30]]
#             }
# facets1 = {"1":[[[-150,30],[-75,30]],[[-75,30],[0,105]]],
#            "2":[[[-150,-45],[-75,30]],[[-75,30],[-150,30]]],
#            "3":[[[-75,-105],[-75,30]],[[-75,30],[-150,-45]]],
#            "4":[[[-75,30],[-75,-105]],[[0,105],[-75,30]]],
#            "5":[[[-75,30],[-75,-105]],[[0,105],[-75,30]]],
#            "6":[[[-75,-105],[-75,30]],[[-75,30],[-150,-45]]],
#            "7":[[[-75,-45],[-75,30]]],
#            "8":[[[-75,-45],[-75,30]]]
#            }
# graph_edge = {"1":[[[-150,30],[-150,105]],[[-150,105],[0,105]]],
#               "2":[[[-150,30],[-150,-45]]],
#               "3":[[[-150,-45],[-150,-105]],[[-150,-105],[-75,-105]]],
#               "4":[[[-75,-105],[0,-105]],[[0,-105],[0,105]]],
#               "5":[[[-75,-105],[0,-105]],[[0,-105],[0,105]],[[0,105],[-75,30]]],
#               "6":[[[-150,-45],[-150,-105]],[[-150,-105],[-75,-105]],[[-75,30],[-150,-45]]],
#               "7":[[[-75,30],[-150,-45]],[[-75,-45],[-150,-45]]],
#               "8":[[[0,105],[-75,30]],[[-75,-45],[0,-45]],[[0,-45],[0,105]]]}
# crease_edge={'8': [[[0, 105], [-75, 30]]],
#              '5': [[[0, 105], [-75, 30]],[[0,-105],[0,105]]],
#              '7': [[[-75, 30], [-150, -45]]],
#              '6': [[[-75, 30], [-150, -45]]],
#              '4': [[[0,-105], [0,105]]]}
# state1 = {"stack":stack1,"polygen":polygen1,"facet_crease":facets1,"graph_edge":graph_edge,"crease_edge":crease_edge}
##############plane
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
# state1 = {"stack":stack1,"polygen":polygen1,"facet_crease":facets1}
# graph_edge = {"1":[[[-150,30],[-150,105]],[[-150,105],[0,105]]],
#               "2":[[[-150,30],[-150,-45]]],
#               "3":[[[-150,-45],[-150,-105]],[[-150,-105],[-75,-105]]],
#               "4":[[[-75,-105],[0,-105]],[[0,-105],[0,105]]],
#               "5":[[[-75,-105],[0,-105]],[[0,-105],[0,105]]],
#               "6":[[[-150,-45],[-150,-105]],[[-150,-105],[-75,-105]]],
#               "7":[[[-150,30],[-150,-45]]],
#               "8":[[[-150,30],[-150,105]],[[-150,105],[0,105]]]}

def lineToAxis(line):
    dx = line[1][0]-line[0][0]
    dy = line[1][1]-line[0][1]
    axis=[dx,dy]
    axis = np.array(axis)/np.linalg.norm(np.array(axis))
    return axis

def lineToFunction(line):
    "input line[[x1,y1],[x2,y2]], return k,b (ax+by+c=0)"
    # a = y2-y1, b = x1-x2, c=x2*y1-x1*y2
    a = line[1][1] - line[0][1]
    b = line[0][0] - line[1][0]
    c = line[1][0]*line[0][1] - line[0][0]*line[1][1]
    return a,b,c

def ifLineColinear1(line1,line2):
    '''
    input two lines, return if they are colinear
    a) colinear b) has intersection
    '''
    axis1 = lineToAxis(line1)
    axis2 = lineToAxis(line2)
    if (axis1==axis2).all() or (axis1==(-axis2)).all():
        is_meet = npi.intersection(line1,line2)
        if len(is_meet) > 0:
            return 1
        else:
            new_line = [line1[0],line2[0]]
            new_axis = lineToAxis(new_line)
            if (axis1==new_axis).all() or (axis1==(-new_axis)).all():
                return 1
            else:
                return 0
    else:
        return 0

def ifLineColinear(line1,line2):
    '''
    input two lines, return if they are colinear
    a) colinear b) has intersection
    '''
    axis1 = lineToAxis(line1)
    axis2 = lineToAxis(line2)
    if (axis1==axis2).all() or (axis1==(-axis2)).all():
        is_meet = npi.intersection(line1,line2)
        if len(is_meet) > 0:
            return 1
        else:
            return 0
    else:
        return 0

def ifLineSame(line1,line2):
    result=0
    a1=line1[0]
    a2=line1[1]
    b1=line2[0]
    b2=line2[1]
    if a1==b1 and a2==b2:
        result=1
    elif a1==b2 and a2==b1:
        result=1
    return result

def CombineLinearLines1(line1,line2):
    '''
    input two colinear lines, return the combined one line
    '''
    "line1 = [[0,0],[1,1]]"
    new_line = npi.exclusive(line1,line2)
    new_line = new_line.tolist()
    return new_line

def pointDistance(point1,point2):
    #return distance between 2 points
    dx = point1[0] - point2[0]
    dy = point1[1] - point2[1]
    dis = np.sqrt(dx*dx + dy*dy)
    return dis

def CombineLinearLines(line1,line2):
    '''
    input two colinear lines, return the combined one line
    '''
    "line1 = [[0,0],[1,1]]"
    p1 = npi.intersection(line1,line2)
    p1 = (p1[0]).tolist()
    points = npi.exclusive(line1,line2)
    p2 = (points[0]).tolist()
    p3 = (points[1]).tolist()
    # print "p2",p2
    # print "p3",p3
    l1 = [p1,p2]
    l2 = [p1,p3]
    axis1 = lineToAxis(l1)
    axis2 = lineToAxis(l2)
    # print "axis1",axis1,type(axis1)
    # print "axis2",axis2,type(axis2)
    if axis1[0]*axis2[0]+axis1[1]*axis2[1] <= 0:
        new_line = points.tolist()
    elif axis1[0]*axis2[0]+axis1[1]*axis2[1] > 0:
        d1 = pointDistance(p1,p2)
        d2 = pointDistance(p1,p3)
        if d1>=d2:
            new_line = [p1,p2]
        else:
            new_line = [p1,p3]
    return new_line

def findAllCreases(stack,facet_crease):
    creases = []
    # print "stack",stack
    for i in range(len(stack)):
        for j in range(len(stack[i])):
            facet = stack[i][j]
            # print "facet",facet
            # print "facet crease[facet]",facet_crease[facet]
            for k in range(len(facet_crease[facet])):
                creases.append(facet_crease[facet][k])
    return creases

def findNonRepetiveCreases(creases):
    #serach for non-repetitive creases
    #each crease will appear and only appear twice
    crease = []
    index = []
    if creases is None:
        return crease
    for i in range(len(creases)):
        line1 = creases[i]
        for j in range(i+1,len(creases)):
            line2 = creases[j]
            if ifLineSame(line1,line2) == 1:
                index.append(j)
                if i not in index:
                    crease.append(line1)
                    break
            else:
                continue
    return crease

def findMininalSetCrease1(crease):
    #find linear creases, and combine them
    min_crease = []
    colinear_num = []
    if len(crease) == 1:
        min_crease = crease
        return min_crease
    for i in range(len(crease)):
        line1 = crease[i]
        for j in range(i+1,len(crease)):
            line2 = crease[j]
            if ifLineSame(line1,line2)==1:
                continue
            #combine linear creases
            if ifLineColinear(line1,line2)==1:
                min_crease.append(CombineLinearLines(line1,line2))
                colinear_num.append(j)
                colinear_num.append(i)
                break
            #if the line is not colinear with any other lines
        if j == (len(crease)-1) and i not in colinear_num:
            min_crease.append(line1)
    return min_crease

def findMininalSetCrease(crease):
    #find linear creases, and combine them
    min_crease = []
    colinear_num = []
    if len(crease) == 1:
        min_crease = crease
        return min_crease
    for i in range(len(crease)):
        line1 = crease[i]
        for j in range(i+1,len(crease)):
            line2 = crease[j]
            if ifLineSame(line1,line2)==1:
                continue
            #combine linear creases
            if ifLineColinear(line1,line2)==1:
                min_crease.append(CombineLinearLines(line1,line2))
                colinear_num.append(j)
                colinear_num.append(i)
                break
            #if the line is not colinear with any other lines
        if j == (len(crease)-1) and i not in colinear_num:
            min_crease.append(line1)
    return min_crease

def is_inPoly(polygen,point):
    #determine if a point is in a polygen
    line = LineString(polygen)
    pointt = Point(point)
    polygen = Polygon(line)
    return polygen.contains(pointt)

def ifLineCrossPolygon(line,polygon):
    #return if a line cross a polygon
    #return 1 if cross
    a,b,c = lineToFunction(line)
    sign_tmp = []
    for i in range(len(polygon)):
        point = polygon[i]
        tmp = a*point[0] + b*point[1] + c
        sign_tmp.append(tmp)
    count1 = 0
    count2 = 0
    for i in range(len(sign_tmp)):
        if sign_tmp[i] >= 0:
            count1 = count1 + 1
        if sign_tmp[i] <= 0:
            count2 = count2 + 1
    if count1 == len(sign_tmp) or count2 == len(sign_tmp):
        return 0
    else:
        return 1

def findFeasibleCrease(crease,polygen):
    # find feasible creases among min_crease
    # discard the creases that cross any facet
    feasible_crease=[]
    for k in range(len(crease)):
        line = crease[k]
        # print "crease",line
        count = 0
        for facet in polygen.keys():
            count = count + 1
            poly = polygen[facet]
            # print "facet",facet
            # print "poly",poly
            if ifLineCrossPolygon(line,poly)==1:
                # print "line cross"
                break
            # if this creasse does not cross any facet
            elif count == len(polygen):
                feasible_crease.append(crease[k])
    return feasible_crease

# creases = findAllCreases(stack1,facets1)
# print "crease",creases
# crease = findNonRepetiveCreases(creases)
# print "crease",crease
# min_crease = findMininalSetCrease(crease)
# print "min_crease",min_crease
# feasible_crease = findFeasibleCrease(min_crease,polygen1)
# print "feasible crease", feasible_crease

def findMinimalCreasebyHeight(stack,facet_crease):
    #find minimal crease by height
    h_crease = {"min":[],"max":[]}
    min_h = 0
    max_h = len(stack) - 1
    if max_h == min_h:
        creases = findAllCreases(stack[min_h],facet_crease)
        crease = findNonRepetiveCreases(creases)
        if len(crease) == 0:
            return h_crease
        min_h_crease = findMininalSetCrease(crease)
        h_crease["min"] = min_h_crease
        h_crease["max"] = min_h_crease
    else:
        creases = findAllCreases(stack[min_h],facet_crease)
        crease = findNonRepetiveCreases(creases)
        if len(crease) == 0:
            return h_crease
        min_h_crease = findMininalSetCrease(crease)
        h_crease["min"] = min_h_crease

        creases = findAllCreases(stack[max_h],facet_crease)
        crease = findNonRepetiveCreases(creases)
        if len(crease) == 0:
            return h_crease
        max_h_crease = findMininalSetCrease(crease)
        h_crease["max"] = max_h_crease
    return h_crease

def ifPointInLine(point,line_func):
    a=line_func[0]
    b=line_func[1]
    c=line_func[2]
    x=point[0]
    y=point[1]
    is_in = a*x+b*y+c
    if is_in == 0:
        return 1
    else:
        return 0

def ifCutGraph(crease,stack,height,graph_edge):
    #test if a crease cuts the origami graph
    #if 2 points of the crease are all on the edge of a graph, return true
    count = 0
    tmp = 999
    for i in range(len(crease)):
        point = crease[i]
        for j in stack[height]:
            if j not in graph_edge.keys():
                continue
            lines = graph_edge[j]
            for line in lines:
                a,b,c = lineToFunction(line)
                line_func = [a,b,c]
                if ifPointInLine(point,line_func)==1:
                    count = count + 1
                    tmp = 888
                    break
            if count == 1 and tmp == 888:
                tmp = 999
                break
            if count == 2:
                return 1
    if count == 2:
        return 1
    else:
        return 0

# polygen = {'1': [[0, 105], [0, -45], [-75, -45], [-75, 30]],
#            '3': [[-150, -45], [-150, -105], [-75, -105], [-75, 30]],
#            '2': [[-75, 30], [-75, -45], [-150, -45]],
#            '5': [[-75, 30], [-75, -105], [0, -105], [0, 105]],
#            '4': [[-75, 30], [-75, -105], [0, -105], [0, 105]],
#            '7': [[-75, 30], [-75, -45], [-150, -45]],
#            '6': [[-150, -45], [-150, -105], [-75, -105], [-75, 30]],
#            '8': [[0, 105], [0, -45], [-75, -45], [-75, 30]]}
# facet_crease = {'1': [[[-75, -45], [-75, 30]]],
#                 '3': [[[-75, -105], [-75, 30]]],
#                 '2': [[[-75, 30], [-75, -45]]],
#                 '5': [[[-75, 30], [-75, -105]]],
#                 '4': [[[-75, 30], [-75, -105]]],
#                 '7': [[[-75, 30], [-75, -45]]],
#                 '6': [[[-75, -105], [-75, 30]]],
#                 '8': [[[-75, -45], [-75, 30]]]}
# stack = [['3', '4'], ['5', '6'], ['7', '8'], ['1', '2']]
# graph_edge = {'1': [[[-75, -45], [0, -45]], [[0, -45], [0, 105]], [[-75, 30], [0, 105]]],
#               '3': [[[-150, -45], [-150, -105]], [[-150, -105], [-75, -105]], [[-150, -45], [-75, 30]], [[-150, -45], [-75, 30]]],
#               '2': [[[-75, -45], [-150, -45]], [[-150, -45], [-75, 30]]],
#               '5': [[[-75, -105], [0, -105]], [[0, -105], [0, 105]]],
#               '4': [[[-75, -105], [0, -105]], [[0, -105], [0, 105]], [[-75, 30], [0, 105]], [[-75, 30], [0, 105]]],
#               '7': [[[-75, -45], [-150, -45]], [[-150, -45], [-75, 30]]],
#               '6': [[[-150, -45], [-150, -105]], [[-150, -105], [-75, -105]]],
#               '8': [[[-75, -45], [0, -45]], [[0, -45], [0, 105]], [[-75, 30], [0, 105]]]}
# polygen = {'1': [[-105, 105], [105, 105], [105, 60], [-105, 60]],
#            '3': [[0, 0], [-105, 105], [-105, 0]],
#            '2': [[0, 0], [105, 105], [-105, 105]],
#            '5': [[0, 0], [-105, 0], [-105, -105]],
#            '4': [[0, 0], [105, 0], [105, 105]],
#            '7': [[0, 0], [105, -105], [105, 0]],
#            '6': [[0, 0], [-105, -105], [105, -105]],
#            '8': [[-105, -105], [-105, -150], [105, -150], [105, -105]]}
# facet_crease = {'1': [],
#                 '3': [[[0, 0], [-105, 105]], [[-105, 0], [0, 0]]],
#                 '2': [[[0, 0], [105, 105]], [[-105, 105], [0, 0]]],
#                 '5': [[[0, 0], [-105, 0]], [[-105, -105], [0, 0]]],
#                 '4': [[[0, 0], [105, 0]], [[105, 105], [0, 0]]],
#                 '7': [[[0, 0], [105, -105]], [[105, 0], [0, 0]]],
#                 '6': [[[0, 0], [-105, -105]], [[105, -105], [-105, -105]], [[105, -105], [0, 0]]],
#                 '8': [[[105, -105], [-105, -105]]]}
# stack = [['2', '3', '4', '5', '6', '7', '8'], ['1']]
# graph_edge = {'1': [[[105, 105], [105, 60]], [[105, 60], [-105, 60]], [[-105, 60], [-105, 105]], [[-105, 105], [105, 105]]],
#               '3': [[[-105, 105], [-105, 0]]],
#               '2': [[[-105, 105], [105, 105]]],
#               '5': [[[-105, 0], [-105, -105]]],
#               '4': [[[105, 0], [105, 105]]],
#               '7': [[[105, -105], [105, 0]]],
#               '8': [[[-105, -105], [-105, -150]], [[-105, -150], [105, -150]], [[105, -150], [105, -105]]]}
def findReflectionCrease(stack,facet_crease,polygon,graph_edge):
    #find reflection crease either in the min or max height
    #reflection crease is in findMinimalCreasebyHeight and cutGraph
    reflect_crease={"min":[],"max":[]}
    h_crease = findMinimalCreasebyHeight(stack,facet_crease)
    if len(stack)==1:
        h_crease_tmp = h_crease["min"]
        # print "h_crease",h_crease_tmp
        for i in range(len(h_crease_tmp)):
            crease = h_crease_tmp[i]
            # print "crease",crease
            if ifCutGraph(crease,stack,0,graph_edge)==1:
                reflect_crease["min"].append(crease)
                reflect_crease["max"].append(crease)
        return reflect_crease

    elif len(stack)>1:
        min_h_crease = h_crease["min"]
        if len(min_h_crease) == 0:
            reflect_crease["min"] = min_h_crease
        else:
            for i in range(len(min_h_crease)):
                crease = min_h_crease[i]
                if ifCutGraph(crease,stack,0,graph_edge)==1:
                    reflect_crease["min"].append(crease)
                else:
                    continue

        max_h_crease = h_crease["max"]
        if len(max_h_crease) == 0:
            reflect_crease["max"] = max_h_crease
        else:
            for i in range(len(max_h_crease)):
                crease = max_h_crease[i]
                if ifCutGraph(crease,stack,(len(stack)-1),graph_edge)==1:
                    reflect_crease["max"].append(crease)
                else:
                    continue
        return reflect_crease
# reflect_crease = findReflectionCrease(stack,facet_crease,polygen,graph_edge)
# print "reflecttt",reflect_crease
def is_inPoly(polygen,point):
    #determine if a point is in a polygen
    line = LineString(polygen)
    pointt = Point(point)
    polygen = Polygon(line)
    return polygen.contains(pointt)

def ifCreaseCrossLayerPolygons(crease,stack,polygon,layer):
    #return if a crease cross polygons in a layer
    # return 1 if yes
    for facet in stack[layer]:
        poly = polygon[facet]
        if ifLineCrossPolygon(crease,poly) == 1:
            return 1
    return 0

def findCreaseSets(crease,stack,polygon,height,facet_crease):
    #find all crease sets that contains this crease
    #find crease sets that contain either max or min reflection crease
    crease_tmp = [crease]
    crease_set = [[crease]]
    tmp = 999
    #if contain the max height crease
    if height > 0:
        for i in range(height-1,0,-1):
            for facet in stack[i]:
                # print "facet",facet
                for k in facet_crease[facet]:
                    if ifLineColinear(k,crease)==1:
                        if ifCreaseCrossLayerPolygons(k,stack,polygon,i)==1:
                            return crease_set
                        else:
                            # print "crease k",k
                            crease_tmp.append(k)
                            tmp = copy.deepcopy(crease_tmp)
                            crease_set.append(tmp)
                            tmp = 888
                            break
                if tmp == 888:
                    tmp = 999
                    break
        return crease_set
    #if contain the min height crease
    elif height == 0:
        for i in range(1,len(stack)-1):
            for facet in stack[i]:
                # print "facet",facet
                for k in facet_crease[facet]:
                    if ifLineColinear(k,crease)==1:
                        if ifCreaseCrossLayerPolygons(k,stack,polygon,i)==1:
                            return crease_set
                        else:
                            # print "crease k",k
                            crease_tmp.append(k)
                            tmp = copy.deepcopy(crease_tmp)
                            crease_set.append(tmp)
                            tmp = 888
                            break
                if tmp == 888:
                    tmp = 999
                    break
        return crease_set
# crease_sets = findCreaseSets(reflect_crease['min'][0],stack,polygen,0,facet_crease)
# print "crease setsss",crease_sets
def findLayerofFacet(facet,stack):
    for i in range(len(stack)):
        facets = stack[i]
        if facet in facets:
            return i

def findLayersofFacets(facets,stack):
    facet_layer = []
    for i in range(len(facets)):
        for j in range(len(facets[i])):
            facet = facets[i][j]
            layer = findLayerofFacet(facet,stack)
            facet_layer.append(layer)
    facet_layer = set(facet_layer)
    facet_layer = list(facet_layer)
    return facet_layer

def findSameCreaseFacets(facet_crease,crease,adj_facets,stack):
    # input a crease, return pair facets that share the same crease
    facets = []
    facet_tmp = []
    #first find all facets that contain this crease
    for facet in facet_crease.keys():
        crease_tmp = facet_crease[facet]
        for i in range(len(crease_tmp)):
            c_tmp = crease_tmp[i]
            if ifLineSame(c_tmp,crease) == 1:
                facet_tmp.append(facet)
    # print "facet_tmp",facet_tmp
    # if only 2 facets connected by this crease, then return
    if len(facet_tmp) == 2:
        facets.append(facet_tmp)
        return facets

    # if multiple facets are connected, then find facet pairs in the same height
    # find facet pairs: a) adjacent, b) on the same layer
    count = [] #record the facet and its pair indexes
    for i in range(len(facet_tmp)):
        if i in count:
            continue
        facet = facet_tmp[i]
        adj_facets_tmp = adj_facets[facet]
        # find adjacent facets
        adj_tmp = npi.intersection(adj_facets_tmp,facet_tmp)
        # if this facet does not have any adj facets, continue
        if len(adj_tmp) == 0:
            continue
        # if this facet has adj facet, but this adj facet does not in the same layer, continue
        elif findLayerofFacet(adj_tmp[0],stack) != findLayerofFacet(facet,stack):
            continue
        else:
            facets.append([facet,adj_tmp[0]])
            count.append(i)
            count.append(facet_tmp.index(adj_tmp[0]))

    return facets

def CreaseDisassemble(facet_crease,long_crease):
    #disassemble long creases into short creases
    creases = []
    for facet in facet_crease.keys():
        crease_tmp = facet_crease[facet]
        for i in range(len(crease_tmp)):
            crease = crease_tmp[i]
            if ifLineColinear(long_crease,crease) == 1 and crease not in creases:
                creases.append(crease)
    return creases

def reverseLineDirection(line):
    tmp = line[0]
    line[0] = line[1]
    line[1] = tmp
    return line

def ifReverseLineDirection(polygon,crease,root_facet='4'):
    #determine if the direction of the crease needs to be reversed
    #if root_facet at the right of the crease, no need to reverse
    # if at the left, reverse line's direction to ensure the root_facet is always at base
    a,b,c = lineToFunction(crease)
    poly = polygon[root_facet]
    for i in range(len(poly)):
        product = a*poly[i][0]+b*poly[i][1]+c
        if product > 0:
            return crease
        # crease direction reverse, crease angle reverse too
        elif product < 0:
            return reverseLineDirection(crease)

def divideStack(crease,stack,polygon):
    #define base at the right of crease, crease has direction
    base = []
    flap = []
    crease = ifReverseLineDirection(polygon,crease)
    # print "crease",crease
    a,b,c = lineToFunction(crease)
    a,b,c = float(a),float(b),float(c)
    # print "a,b,c",a,b,c
    for i in range(len(stack)):
        base_tmp = []
        flap_tmp = []
        for j in range(len(stack[i])):
            facet = stack[i][j]
            # print "facet",facet
            poly = polygon[facet]
            for k in range(len(poly)):
                # product represents the relationship between a point and a line
                product = a*float(poly[k][0])+b*float(poly[k][1])+c
                # print "product",product
                if product > 0:
                    base_tmp.append(facet)
                    break
                elif product < 0:
                    flap_tmp.append(facet)
                    break
        if len(base_tmp)!=0:
            base.append(base_tmp)
        if len(flap_tmp)!=0:
            flap.append(flap_tmp)
    return base,flap

def findFlapsbyCreaseSet(crease_set,stack,height,polygon,root_facet='4'):
    #input a crease set, return feasible flaps
    flaps = []
    count = 1
    init_h = height
    for i in range(len(crease_set)):
        flap_tmp = []
        crease = crease_set[i]
        crease = ifReverseLineDirection(polygon,crease,root_facet)
        a,b,c = lineToFunction(crease)
        for facet in stack[height]:
            poly = polygon[facet]
            for k in range(len(poly)):
                # product represents the relationship between a point and a line
                product = a*poly[k][0]+b*poly[k][1]+c
                if product < 0:
                    flap_tmp.append(facet)
                    break
        flaps.append(flap_tmp)
        if count == len(crease_set):
            if init_h > 0:
                flaps = flaps[::-1]
            return flaps
        if init_h > 0:
            count = count + 1
            height = height - 1
        elif init_h == 0:
            count = count + 1
            height = height + 1
# flaps0 = findFlapsbyCreaseSet(crease_sets[0],stack,0,polygen)
# print "flaps0",flaps0
# flaps1 = findFlapsbyCreaseSet(crease_sets[1],stack,3,polygen)
# print "flaps1",flaps1
# flaps2 = findFlapsbyCreaseSet(crease_sets[2],stack,3,polygen)
# print "flaps2",flaps2
def findFacetwithSameEdge(crease_edge,stack,edge,facet):
    #return facet that shares the same edge
    facets = []
    # print "edge",edge
    for i in crease_edge.keys():
        edges = crease_edge[i]
        for j in edges:
            # print "crease edgeee",j
            if ifLineSame(edge,j)==1 and i != facet:
                facets.append(i)
                break
    return facets

def findOtherFacetsinLayer(facets,layer,stack):
    facets_tmp = [x for j in facets for x in j]
    facetss = stack[layer]
    other_facets = npi.difference(facetss,facets_tmp)
    other_facets = [x for x in other_facets]
    return other_facets

def polygenIntersectionCheck(poly1,poly2):
    #check if two polygens have intersection
    #return 1 if has intersection
    line1 = LineString(poly1)
    line2 = LineString(poly2)
    polygon1 = Polygon(line1)
    polygon2 = Polygon(line2)
    area = polygon1.intersection(polygon2).area
    # print "area",area
    if area >= 1:
        return 1
    else:
        return 0

def ifFlapReflect(flaps,stack,polygen):
    # return if the flap facets has intersection with other facets
    # if yes, it is reflectable, return 1
    # if not, return 0
    flap_tmp = [x for j in flaps for x in j]
    stack_tmp = [x for j in stack for x in j]
    other_facets = npi.difference(stack_tmp,flap_tmp)
    # print "flap tmp",flap_tmp
    # print "stack_tmp",stack_tmp
    # print "other facets",other_facets
    for facet1 in flap_tmp:
        # print "facet1",facet1
        poly1 = polygen[facet1]
        for facet2 in other_facets:
            # print "facet2",facet2
            poly2 = polygen[facet2]
            if polygenIntersectionCheck(poly1,poly2) == 1:
                return 1
            else:
                continue
    return 0

def ifHasAdjacents(facet,facets,adjacent_facets):
    #input a facet, test if its adjacent_facets are in facets
    # return 0 if no
    adj_facets = adjacent_facets[facet]
    is_adj = npi.intersection(adj_facets,facets)
    if len(is_adj) == 0:
        return 0
    else:
        return 1

def ifFlapsFeasible(flaps,crease_edge,stack,adjacent_facets):
    #return if the flap facets are feasible
    # facets in flaps are feasible when a) it does not have crease_edge
    # or b) two facets share the same crease_edge
    # and c) flap facets are adjacent pairs
    # a) or (b) and c))
    # return 1 if yes
    flap_tmp = [x for j in flaps for x in j]
    # print "flap_tmp",flap_tmp
    # count = 0
    for i in range(len(flap_tmp)):
        facet = flap_tmp[i]
        tmp = npi.difference(flap_tmp,[facet])
        if facet not in crease_edge.keys():
            # count = count + 1
            continue
        else:
            if ifHasAdjacents(facet,flap_tmp,adjacent_facets) == 0:
                return 0
            edges = crease_edge[facet]
            for k in edges:
                same_edge_facets = findFacetwithSameEdge(crease_edge,stack,k,facet)
                # print "same_edge_facets",same_edge_facets
                is_in = npi.intersection(same_edge_facets,tmp)
                is_in = len(is_in)
                if is_in > 0:
                    continue
                else:
                    return 0
    return 1
#
# adjacent_facets = {'1':['2','4'],
#                    '2':['1','3'],
#                    '3':['2','4'],
#                    '4':['1','3','5'],
#                    '5':['4','6','8'],
#                    '6':['5','7'],
#                    '7':['6','8'],
#                    '8':['5','7']}
# crease_edge = {'1': [[[-75, 30], [0, 105]]],
#                '3': [[[-150, -45], [-75, 30]]],
#                '2': [[[-150, -45], [-75, 30]]],
#                '5': [[[0, -105], [0, 105]]],
#                '4': [[[0, -105], [0, 105]], [[-75, 30], [0, 105]]],
#                '7': [[[-150, -45], [-75, 30]]],
#                '8': [[[-75, 30], [0, 105]]]}
# adjacent_facets = {'1':['2'],
#                    '2':['1','3','4'],
#                    '3':['2','5'],
#                    '4':['2','7'],
#                    '5':['3','6'],
#                    '6':['5','7','8'],
#                    '7':['6','4'],
#                    '8':['6']}
# crease_edge = {'1': [[[-105, 105], [105, 105]]], '2': [[[-105, 105], [105, 105]]]}
# print "if flaps0 feasible?",ifFlapsFeasible(flaps0,crease_edge,stack,adjacent_facets)
# print "if flaps1 feasible?",ifFlapsFeasible(flaps1,crease_edge,stack,adjacent_facets)
# print "if flaps2 feasible?",ifFlapsFeasible(flaps2,crease_edge,stack,adjacent_facets)
def divideReflectStack(crease_set,height,stack,polygon,crease_edge):
    #specially for reflection fold, return base, flap and sign(mountain or valley)
    #define base at the right of crease, crease has direction
    base = []
    fold = "unkown"
    stack_info = {"base":[],"flap":[],"crease_set":[],"fold":fold}

    flaps = findFlapsbyCreaseSet(crease_set,stack,height,polygon)
    stack_info["flap"] = flaps
    stack_info["crease_set"] = crease_set
    layer_num = len(flaps)
    # print "flaps",flaps
    count = 0
    if height > 0:
        fold = "valley"
        stack_info["fold"] = fold
        for i in range(height,-1,-1):
            if count < layer_num:
                count = count + 1
                other_facets = findOtherFacetsinLayer(flaps,i,stack)
                # print "othre facets", other_facets
                if len(other_facets) > 0:
                    base.append(other_facets)
            else:
                base.append(stack[i])
        base = base[::-1]
        stack_info["base"] = base
        return stack_info
    elif height == 0:
        fold = "mountain"
        stack_info["fold"] = fold
        for i in range(0,len(stack)):
            if count < layer_num:
                count = count + 1
                other_facets = findOtherFacetsinLayer(flaps,i,stack)
                if len(other_facets) > 0:
                    base.append(other_facets)
            else:
                base.append(stack[i])
        stack_info["base"] = base
        return stack_info

def reversePoint(crease,point):
    a,b,c = lineToFunction(crease)
    x = point[0]
    y = point[1]
    reversed_point = []
    if a == 0 and b != 0:
        x1 = x
        y1 = -2*c/b - y
    if b == 0 and a != 0:
        y1 = y
        x1 = -2*c/a - x
    if a !=0 and b!= 0:
        x1 = -1*(2*a*b*y + (a*a-b*b)*x + 2*a*c) / (a*a + b*b)
        y1 = -1*((b*b-a*a)*y + 2*a*b*x + 2*b*c) / (a*a + b*b)
    reversed_point.append(x1)
    reversed_point.append(y1)
    return reversed_point

def reverseLine(crease,line):
    point1 = line[0]
    point2 = line[1]
    reversed_line = []
    new_point1 = reversePoint(crease,point1)
    new_point2 = reversePoint(crease,point2)
    reversed_line.append(new_point1)
    reversed_line.append(new_point2)
    return reversed_line

def reverseCrease(flap,crease,facet_crease):
    new_facet_crease = copy.deepcopy(facet_crease)
    # remain creases in base stack
    # reverse creases in flap stack
    for i in range(len(flap)):
        for j in range(len(flap[i])):
            facet = flap[i][j]
            creases = facet_crease[facet]
            new_creases = []
            for k in range(len(creases)):
                new_creases.append(reverseLine(crease,creases[k]))
            new_facet_crease[facet] = new_creases
    return new_facet_crease

# def findAdjandSameCreaseFacet(facet,facet_crease,crease,adjacent_facets):
#     #return a facet that a) adjacent to input facet
#     # and b) has the same creases as the facet
#     adj_facets = adjacent_facets[facet]
#     # print "adj_facets",adj_facets
#     for i in range(len(adj_facets)):
#         facett = adj_facets[i]
#         creases = facet_crease[facett]
#         # print "facett",facett
#         for k in creases:
#             if ifLineColinear(k,crease)==1:
#                 print "faaacet",facett
#                 print "creaseee",k
#                 return facett

def findAdjandSameCreaseFacet(facet,facet_crease,crease,adjacent_facets):
    #return a facet that a) adjacent to input facet
    # and b) has the same creases as the facet
    adj_facets = adjacent_facets[facet]
    # print "adj_facets",adj_facets

    # if the crease not colinear with any creases in this facet, return None
    count = 0
    for i in facet_crease[facet]:
        if ifLineColinear(i,crease) == 1:
            break
        else:
            count += 1
    if count == len(facet_crease[facet]):
        return None

    # search it adjacent facets, see who has the same crease
    for i in range(len(adj_facets)):
        facett = adj_facets[i]
        creases = facet_crease[facett]
        # print "facett",facett
        for k in creases:
            if ifLineColinear(k,crease)==1:
                # print "faaacet",facett
                # print "creaseee",k
                return facett

def newStateCrease(crease,facet_crease,flaps,adjacent_facets):
    #delete folded crease in new state
    flap_tmp = [x for j in flaps for x in j]
    # print "crease",crease
    # print "flap_tmp",flap_tmp
    #find all facets that contain this creasse
    for i in range(len(flap_tmp)):
        facet = flap_tmp[i]
        # print "facettt",facet
        f_tmp = findAdjandSameCreaseFacet(facet,facet_crease,crease,adjacent_facets)
        flap_tmp.append(f_tmp)
    # print "flap_tmp1",flap_tmp
    flap_tmp = set(flap_tmp)
    flap_tmp = list(flap_tmp)
    if None in flap_tmp:
        flap_tmp.remove(None)
    # print "flap_tmp2",flap_tmp
    for facet in flap_tmp:
        # print "facet",facet
        new_creases = copy.deepcopy(facet_crease[facet])
        for i in range(len(new_creases)):
            # print "new",new_creases[i]
            if ifLineColinear(crease,new_creases[i]) == 1:
                # print "1",facet_crease[facet][i]
                del facet_crease[facet][i]

    return facet_crease

def reversePolygen(flap,crease,polygon):
    new_polygen = copy.deepcopy(polygon)
    # remain polygens in base stack
    # reverse polygens in flap stack
    for i in range(len(flap)):
        for j in range(len(flap[i])):
            facet = flap[i][j]
            poly = polygon[facet]
            new_poly = []
            for k in range(len(poly)):
                new_poly.append(reversePoint(crease,poly[k]))
            new_polygen[facet] = new_poly
    return new_polygen

def reverseGraphEdge(crease,flap,graph_edge):
    # reverse graph edges in flaps
    # remain graph edges in base
    flap = np.array(flap)
    flap = flap.flatten()
    reversed_edge = copy.deepcopy(graph_edge)
    for i in range(len(flap)):
        facet = flap[i]
        if facet not in graph_edge.keys():
            continue
        edges = graph_edge[facet]
        edge_tmp = []
        for i in range(len(edges)):
            edge = edges[i]
            edge = reverseLine(crease,edge)
            edge_tmp.append(edge)
        reversed_edge[facet] = edge_tmp
    return reversed_edge

def ifCreaseinFacet(crease,facet_crease):
    # return facets that contain the crease
    c_facet = {}
    tmp = 999
    for facet in facet_crease.keys():
        f_crease = facet_crease[facet]
        for i in range(len(f_crease)):
            crease_tmp = f_crease[i]
            if ifLineColinear(crease,crease_tmp) == 1:
                c_facet.setdefault(facet,crease_tmp)
                tmp = 888
                break
        if tmp == 888:
            tmp = 999
            continue
    return c_facet

def newStateEdge(reversed_edge,crease,flap_facets,stack,facet_crease):
    # folded crease will be added to new_reversed_edge and new_edge
    # find facets that contain this crease
    crease_facet = ifCreaseinFacet(crease,facet_crease)
    new_reversed_edge = copy.deepcopy(reversed_edge)
    new_edges = {}
    layers = findLayersofFacets(flap_facets,stack)
    tmp = 999
    for m in range(len(flap_facets)):
        for n in range(len(flap_facets[m])):
            facet = flap_facets[m][n]
            if facet not in crease_facet.keys():
                continue
            new_edge = crease_facet[facet]
            new_edge = copy.deepcopy(new_edge)
            if facet not in new_reversed_edge.keys():
                new_reversed_edge.setdefault(facet,[])
            new_reversed_edge[facet].append(new_edge)
            new_edges.setdefault(facet,new_edge)
            for i in layers:
                other_facets = findOtherFacetsinLayer(flap_facets,i,stack)
                # print "other facets",other_facets
                for j in other_facets:
                    # print 'j',j
                    creaseee = facet_crease[j]
                    for k in creaseee:
                        if ifLineSame(new_edge,k) == 1:
                            new_reversed_edge.setdefault(j,[])
                            new_reversed_edge[j].append(new_edge)
                            new_edges.setdefault(j,new_edge)
                            tmp = 888
                            break
                    if tmp == 888:
                        break
                if tmp == 888:
                    break
            if tmp == 888:
                tmp = 999
                continue
    return new_reversed_edge,new_edges

def reverseCreaseEdge(crease,flap,crease_edge):
    # reverse crease edges in flaps
    # remain crease edges in base
    flap = np.array(flap)
    flap = flap.flatten()
    reversed_edge = copy.deepcopy(crease_edge)
    for i in range(len(flap)):
        facet = flap[i]
        if facet not in crease_edge.keys():
            continue
        edges = crease_edge[facet]
        edge_tmp = []
        for i in range(len(edges)):
            edge = edges[i]
            edge = reverseLine(crease,edge)
            edge_tmp.append(edge)
        reversed_edge[facet] = edge_tmp
    return reversed_edge

def findCreaseEdge(new_edges,crease_edges):
    crease_edge = copy.deepcopy(crease_edges)
    for facet in new_edges.keys():
        crease_edge.setdefault(facet,[])
        crease_edge[facet].append(new_edges[facet])
    return crease_edge

def reverseStack(base,flap,crease,polygen,sign):
    '''
    input base stack and flap stack, return reversed stack
    '''
    #sign + is valley, sign - is mountain
    new_stack = []
    polygen = reversePolygen(flap,crease,polygen)
    if sign == "+":
        #flap above the base
        #base stack will be remained, add base first
        for i in range(len(base)):
            new_stack.append(base[i])
        #reverse the flap
        new_flap = flap[::-1]

        #polygen intersection polygen intersection check
        layer = 0 #layer is to determine which layer should the flap be in
        tmp = 0
        #the layer that the bottom of flap has intersection with the base
        for i in range(len(base)):
            for j in range(len(base[i])):
                facet = base[i][j]
                poly1 = polygen[facet]
                for k in range(len(new_flap[0])):
                    poly2 = polygen[new_flap[0][k]]
                    if polygenIntersectionCheck(poly1,poly2)==1:
                        layer = i+1
                        tmp = 1
                        break
                if tmp == 1:
                    tmp = 0
                    break
        # flap is totally above the base
        # print "layer",layer
        if len(new_stack)<=layer:
            # print "+above"
            for j in range(len(new_flap)):
                new_stack.append(new_flap[j])
            # print "new stack",new_stack
        # flap can be contained in base
        elif len(new_stack)>=(layer+len(new_flap)):
            # print "+contain"
            layer_tmp = 0
            for i in range(layer,len(new_stack)):
                if layer_tmp<len(new_flap):
                    new_stack[i] = new_stack[i] + new_flap[layer_tmp]
                    layer_tmp = layer_tmp+1
                else:
                    break

        # some of flap above the base, and some of flap contained in base
        else:
            # print "+mix above below"
            layer_tmp = 0
            for i in range(len(new_stack)):
                if i >= layer:
                    new_stack[i] = new_stack[i] + new_flap[layer_tmp]
                    layer_tmp = layer_tmp+1
                else:
                    continue
            for j in range(layer_tmp,len(new_flap)):
                new_stack.append(new_flap[j])
    elif sign == "-":
        #flap below the base
        #base stack will be remained, add base first
        for i in range(len(base)):
            new_stack.append(base[i])
        #reverse the flap
        new_flap = flap[::-1]
        #polygen intersection polygen intersection check
        layer = 0 #layer is to determine which layer should the flap be in
        tmp = 0
        #the layer that the bottom of flap has intersection with the base
        for i in range(len(base)):
            for j in range(len(base[i])):
                facet = base[i][j]
                poly1 = polygen[facet]
                for k in range(len(new_flap[-1])):
                    poly2 = polygen[new_flap[-1][k]]
                    if polygenIntersectionCheck(poly1,poly2)==1:
                        layer = i
                        tmp = 2
                        break
                if tmp == 2:
                    break
            if tmp == 2:
                break
        if tmp == 0 and i == (len(base)-1):
            layer = 1
        # flap is totally below the base
        # print "layer",layer
        if layer==0:
            # print "-below"
            for j in range(len(flap)):
                new_stack.insert(0,flap[j])#new_flap reverse insert, equals to flap insert
        # flap can be contained in base
        elif (layer-len(new_flap))>=0:
            # print "-contain"
            layer_tmp = len(new_flap)-1
            for i in range(layer-1,(layer-1-len(new_flap)),-1):
                new_stack[i] = new_stack[i] + new_flap[layer_tmp]
                layer_tmp = layer_tmp - 1
        # some of flap above the base, and some of flap contained in base
        else:
            # print "-mix above below"
            layer_tmp = len(new_flap)-1
            for i in range(layer-1,-1,-1):
                new_stack[i] = new_stack[i] + new_flap[layer_tmp]
                layer_tmp = layer_tmp - 1

            for j in range(layer_tmp,-1,-1):
                new_stack.insert(0,new_flap[j])

    return new_stack


# flaps0 = findFlapsbyCreaseSet(crease_sets[0],stack1,h,polygen1)
# print "flaps0",flaps0
# flaps = findFlapsbyCreaseSet(crease_sets[1],stack1,h,polygen1)
# print "flaps",flaps
# crease_edge={'5': [[[0,-105],[0,105]]],
#              '4': [[[0,-105], [0,105]]]}
# print "is flaps0 feasible?",ifFlapsFeasible(flaps0,crease_edge,stack1)
# print "is flaps feasible?",ifFlapsFeasible(flaps,crease_edge,stack1)

# reversed_edge = reverseGraphEdge(reflect_crease["max"][0],flap,graph_edge)
# print "reversed edge",reversed_edge
# crease_facet = ifCreaseinFacet(reflect_crease["max"][0],facets1)
# print "crease facet",crease_facet
# new_graph_edge,new_edges = newStateEdge(reversed_edge,crease_facet,flap,stack1,facets1)
# print "new graph edges",new_graph_edge
# print "new edges",new_edges
#
# crease_edge = reverseCreaseEdge(reflect_crease["max"][0],flap,crease_edge)
# crease_edge = findCreaseEdge(new_edges,crease_edge)
# print "crease edge",crease_edge

def ifAnyFacetSame(stack1,stack2):
    # return if any elements are the same in stack1, 2
    # return 1 if yes
    stack1 = sorted(stack1)
    stack2 = sorted(stack2)
    for i in stack1:
        if i in stack2:
            return 1
    return 0

def newStateCreaseAngle(crease_angle,crease_edge,stack,root_facet='4'):
    #if root crease in crease_edge, return new crease angle
    crease_angle = {'1':{'2':'-','4':'-'},
                    '2':{'1':'-','3':'-'},
                    '3':{'2':'-','4':'-'},
                    '4':{'1':'-','3':'-','5':'+'},
                    '5':{'4':'+','8':'-','6':'-'},
                    '6':{'5':'-','7':'-'},
                    '7':{'6':'-','8':'-'},
                    '8':{'7':'-','5':'-'}}
    if root_facet not in crease_edge.keys():
        return crease_angle
        
    crease_edges = crease_edge[root_facet]
    root_crease = [[0,-105],[0,105]]
    for i in range(len(crease_edges)):
        if ifLineSame(crease_edges[i],root_crease) == 1:
            crease_angle = {'1':{'2':'-','4':'-'},
                            '2':{'1':'-','3':'-'},
                            '3':{'2':'-','4':'-'},
                            '4':{'1':'-','3':'-','5':'+'},
                            '5':{'4':'+','8':'+','6':'+'},
                            '6':{'5':'+','7':'+'},
                            '7':{'6':'+','8':'+'},
                            '8':{'7':'+','5':'+'}}
            return crease_angle
    return crease_angle

def generateNextStateInformation(state,crease,sign,crease_sets=0,reflect=0):
    '''
    Given a feasible crease fold, previous stack and polygen and facet_crease information,
    return new stack and polygen and facet_crease information.
    '''
    stack = state["stack"]
    polygen = state["polygen"]
    crease_edge = state["crease_edge"]
    facet_crease = state["facet_crease"]
    adj_facets = state["adjacent_facets"]
    graph_edge = state["graph_edge"]
    count = state["count"]
    crease_angle = state["crease_angle"]

    if reflect == 0:
        #search for base and flap according to this crease
        base,flap = divideStack(crease,stack,polygen)
        # print "base, flap",base,flap
    elif reflect == 1:
        #valley fold
        if sign == "+":
            h = len(stack) - 1
        #mountain fold
        elif sign == '-':
            h = 0

        #generate new stack info
        stack_info = divideReflectStack(crease_sets,h,stack,polygen,crease_edge)
        # print "stack info crease",stack_info["crease_set"]
        base = stack_info["base"]
        flap = stack_info["flap"]
        crease_set = stack_info["crease_set"]
        # print "base", base
        # print "flap", flap
        # print "crease set", crease_set
        crease = crease_set[0]

    #generate new stack
    reversed_stack = reverseStack(base,flap,crease,polygen,sign)
    # print "reversed stack", reversed_stack

    #generate new count
    if sign == '-' and len(flap) % 2 == 1 and len(stack) != len(reversed_stack):
        count = count + 1
    elif sign == '+' and count % 2 == 1 and (findLayerofFacet(base[0][0],stack)+count) % 2 == 0 and len(flap) % 2 == 0:
        count = count + 1

    # if reversed_stack[0] == ['1', '2', '7', '8']:
    #     print "**********************************************************************"
    #     print "count",count
    #generate new polygen
    reversed_polygen = reversePolygen(flap,crease,polygen)
    # print "reversed polygen",reversed_polygen
    #generate new facet creases
    reversed_creases = reverseCrease(flap,crease,facet_crease)
    # print "reversed crease",reversed_creases
    new_crease = newStateCrease(crease,reversed_creases,flap,adj_facets)

    #generate new graph edges and new crease edge
    reversed_edge = reverseGraphEdge(crease,flap,graph_edge)
    # print "reversed edge",reversed_edge
    # crease_facet = ifCreaseinFacet(crease,facets1)
    # print "crease facet",crease_facet
    new_graph_edge,new_edges = newStateEdge(reversed_edge,crease,flap,stack,facet_crease)
    # print "new graph edges",new_graph_edge
    # print "new edges",new_edges
    crease_edge = reverseCreaseEdge(crease,flap,crease_edge)
    crease_edge = findCreaseEdge(new_edges,crease_edge)
    #generate new crease angles
    new_crease_angle = newStateCreaseAngle(crease_angle,crease_edge,stack)
    # print "crease edge",crease_edge
    return reversed_stack,count,new_crease_angle,reversed_polygen,new_crease,new_graph_edge,crease_edge

def ifReflectable(state):
    # determine if this state can be reflection folded
    # return 0 if not Reflectable
    # return 1 if only can be valley folded
    # return 2 if only can be mountain folded
    # return 3 if can be both valley and monutain
    a = 999
    b = 999
    m = 0
    crease_set_min = []
    crease_set_max = []
    if len(state["stack"]) == 1:
        return m,crease_set_min,crease_set_max
    reflect_crease = findReflectionCrease(state["stack"],state["facet_crease"],state["polygen"],state["graph_edge"])
    # print "reflect crease",reflect_crease
    if len(reflect_crease["min"]) != 0:
        h = 0
        for r_crease in reflect_crease["min"]:
            crease_sets = findCreaseSets(r_crease,state["stack"],state["polygen"],h,state["facet_crease"])
            for i in range(len(crease_sets)):
                flaps = findFlapsbyCreaseSet(crease_sets[i],state['stack'],h,state['polygen'])
                if ifFlapsFeasible(flaps,state["crease_edge"],state["stack"],state["adjacent_facets"]) == 0:
                    continue
                elif ifFlapsFeasible(flaps,state["crease_edge"],state["stack"],state["adjacent_facets"]) == 1 and ifFlapReflect(flaps,state["stack"],state["polygen"]) == 1:
                    b = 888
                    crease_set_min = crease_sets[i]
                    break
            if b == 888:
                break

    if len(reflect_crease["max"]) != 0:
        h = len(state["stack"]) - 1
        # if len(crease_set_min)!=0:
        #     print "graph_edge",state['graph_edge']
        #     print "reflect crease",reflect_crease["max"]
        for r_crease in reflect_crease["max"]:
            crease_sets = findCreaseSets(r_crease,state["stack"],state["polygen"],h,state["facet_crease"])
            for i in range(len(crease_sets)):
                flaps = findFlapsbyCreaseSet(crease_sets[i],state['stack'],h,state['polygen'])
                if ifFlapsFeasible(flaps,state["crease_edge"],state["stack"],state["adjacent_facets"]) == 0:
                    continue
                elif ifFlapsFeasible(flaps,state["crease_edge"],state["stack"],state["adjacent_facets"]) == 1 and ifFlapReflect(flaps,state["stack"],state["polygen"]) == 1:
                    # print "flaaaaap",flaps
                    a = 888
                    crease_set_max = crease_sets[i]
                    break
            if a == 888:
                break
    if a == 888 and b == 888:
        m = 3
        return m,crease_set_min,crease_set_max
    if a == 999 and b == 888:
        m = 2
        return m,crease_set_min,crease_set_max
    if a == 888 and b == 999:
        m = 1
        return m,crease_set_min,crease_set_max
    else:
        m = 0
        return m,crease_set_min,crease_set_max

def CreaseDisassembleLayers(facet_crease,long_crease,adj_facets,stack):
    # return facet pairs that containing the disamebled creases, and in different layers
    #disassemble long creases into short creases
    #the disassembled creases are in different layers
    creases = CreaseDisassemble(facet_crease,long_crease)

    #find all facets pairs and their layers
    facet_pair_tmp = []
    for i in range(len(creases)):
        facets_pair = findSameCreaseFacets(facet_crease,creases[i],adj_facets,stack)
        # store all facet pairs and their layers
        for j in range(len(facets_pair)):
            layer = findLayersofFacets(facets_pair[j],stack)
            if len(layer)>1:
                print "CreaseDisameble error, findSameCreaseFacets error"
                return 0
            facet_pair_tmp.append([facets_pair[j][0],facets_pair[j][1],layer])

    #delete facets pairs that in the same layer
    count = []
    facet_pairs = []
    for pair_tmp in facet_pair_tmp:
        layer = pair_tmp[2]
        #if facet pair in this layer has been added, continue
        if layer in count:
            continue
        elif layer not in count:
            count.append(layer)
            facet_pairs.append(pair_tmp[:2])
    return facet_pairs

def determineSign(facet_crease,long_crease,adj_facets,polygon,base,crease_angle,stack,reflec=0,h=0):
    # find facet pairs that contain this long crease, and the pairs are in different layers
    same_facets = CreaseDisassembleLayers(facet_crease,long_crease,adj_facets,stack)
    # print "same facet",same_facets
    # print "long crease",long_crease
    base1 = copy.deepcopy(base)
    # print "base",base1
    base = [x for j in base for x in j]
    # print "base",base
    count = 0
    num = len(same_facets)
    temp = 0
    #if reflection folded, determine num
    if reflec == 1:
        num = 0
        for i in range(len(same_facets)):
            pair_tmp = same_facets[i]
            if pair_tmp[0] in base1[h] or pair_tmp[1] in base1[h]:
                num =num +1
        # print "num",num
    # if same_facets == [['5', '6'], ['7', '8']]:
    #     print "***************************************************************"
    #     print "same_facets",same_facets
    #     print "long crease",long_crease
    #     print "stack",stack
    #     print "base",base1
    #     print "base1[h]",base1[h]
    #     print "crease angle",crease_angle
    for i in range(len(same_facets)):
        facet_pairs = same_facets[i]
        # print "pair",same_facets[i]
        #if this facet pair not in the layer that will be reflection folded, continue
        if reflec == 1:
            # print "facet pair[0]",facet_pairs[0],facet_pairs[1]
            if facet_pairs[0] not in base1[h] and facet_pairs[1] not in base1[h]:
                continue
        # determine the root facet
        # print "facet pairs",facet_pairs
        if facet_pairs[0] in base:
            root_facet = facet_pairs[0]
            other_facet = facet_pairs[1]
        elif facet_pairs[1] in base:
            root_facet = facet_pairs[1]
            other_facet = facet_pairs[0]
        # print "root",root_facet
        # print "other",other_facet
        # print "angle",crease_angle
        sign_tmp = crease_angle[root_facet][other_facet]
        # print "sign tmp",sign_tmp
        if sign_tmp == '+':
            tmp = 1
        elif sign_tmp == '-':
            tmp = 0
        count = count + tmp
        temp = temp + 1
        if temp == num:
            break

    if count == 0:
        sign = '-'
    elif count == num:
        sign = '+'
    else:
        sign = 'n'
    return sign

def generateNextLayerStates(state,adj_facets,crease_angle):
    '''
    input parent node state information, return next layer's children states
    '''
    new_states = []
    #find minimal set of lines taht contain all creases
    creases = findAllCreases(state["stack"],state["facet_crease"])
    # print "creases",creases
    crease = findNonRepetiveCreases(creases)
    # print "crease",crease
    min_crease = findMininalSetCrease(crease)
    # print "min_creases",min_crease
    #how to set(min_crease)
    #find all feasible creases
    feasible_crease = findFeasibleCrease(min_crease,state["polygen"])
    # print "feasible crease",feasible_crease
    # print "stack",state["stack"]
    # if state["stack"][0] == ['7', '8']:
    #     print "******************************************************************"
    crease_angle = copy.deepcopy(state["crease_angle"])
    # print "angle",crease_angle
    # crease_angle = copy.deepcopy(crease_angle)
    #generate new states for each feasible crease
    for i in range(len(feasible_crease)):
        base,_ = divideStack(feasible_crease[i],state['stack'],state['polygen'])
        # if state['stack'] == [['1','2','3','4'],['5','6','7','8']]:
        #     print "****************************************************************"
        #     print "crease edge['4']",state['crease_edge']['4']
        # print "crease",feasible_crease[i]
        sign = determineSign(state["facet_crease"],feasible_crease[i],adj_facets,state["polygen"],base,crease_angle,state['stack'])
        state_tmp = {}
        # print "sign",sign
        if sign == 'n':
            continue
        elif sign == '+':
            state_tmp["fold"] = "valley"
        elif sign == '-':
            state_tmp["fold"] = "mountain"

        new_stack,count,new_crease_angle,new_polygen,new_creases,new_graph_edge,crease_edge = generateNextStateInformation(state,feasible_crease[i],
                                                                                                                           sign)
        state_tmp["stack"] = new_stack
        state_tmp["count"] = count
        state_tmp["crease_angle"] = new_crease_angle
        state_tmp["polygen"] = new_polygen
        state_tmp["facet_crease"] = new_creases

        state_tmp["graph_edge"] = new_graph_edge
        state_tmp["crease_edge"] = crease_edge
        state_tmp["adjacent_facets"] = adj_facets
        state_tmp["reflect"] = 0
        # print "count",count
        # print " crease angle",new_crease_angle

        state_tmp0 = copy.deepcopy(state_tmp)
        new_states.append(state_tmp0)

    reflec, crease_set_min, crease_set_max = ifReflectable(state)
    # print "if reflectable?",ifReflectable(state)
    # print "stack",state["stack"]

    if reflec == 1:
        # valley fold
        state_tmp = {}
        stack = state["stack"]
        h = len(stack) - 1
        stack_info = divideReflectStack(crease_set_max,h,stack,state['polygen'],state['crease_edge'])
        base = stack_info["base"]
        sign = determineSign(state["facet_crease"],crease_set_max[0],adj_facets,state["polygen"],base,crease_angle,state['stack'],reflec=1,h=h)
        if sign == '+':
            new_stack,count,new_crease_angle,new_polygen,new_creases,new_graph_edge,crease_edge = generateNextStateInformation(state,0,"+",
                                                                                                                               crease_sets=crease_set_max,
                                                                                                                               reflect=1)
            state_tmp["stack"] = new_stack
            state_tmp["polygen"] = new_polygen
            state_tmp["facet_crease"] = new_creases
            state_tmp["fold"] = "valley"
            state_tmp["graph_edge"] = new_graph_edge
            state_tmp["crease_edge"] = crease_edge
            state_tmp["adjacent_facets"] = adj_facets
            state_tmp["reflect"] = 1
            state_tmp["count"] = count
            state_tmp["crease_angle"] = new_crease_angle
            state_tmp0 = copy.deepcopy(state_tmp)
            new_states.append(state_tmp0)
            # print "reflect crease",crease_set_max[0]
            # print "reflec1"

    if reflec == 2:
        # mountain fold
        state_tmp = {}
        stack = state["stack"]
        h = 0
        stack_info = divideReflectStack(crease_set_min,h,stack,state['polygen'],state['crease_edge'])
        base = stack_info["base"]
        sign = determineSign(state["facet_crease"],crease_set_min[0],adj_facets,state["polygen"],base,crease_angle,state['stack'],reflec=1,h=h)
        if sign == '-':
            new_stack,count,new_crease_angle,new_polygen,new_creases,new_graph_edge,crease_edge = generateNextStateInformation(state,0,"-",
                                                                                                                               crease_sets=crease_set_min,
                                                                                                                               reflect=1)
            state_tmp["stack"] = new_stack
            state_tmp["polygen"] = new_polygen
            state_tmp["facet_crease"] = new_creases
            state_tmp["fold"] = "mountain"
            state_tmp["graph_edge"] = new_graph_edge
            state_tmp["crease_edge"] = crease_edge
            state_tmp["adjacent_facets"] = adj_facets
            state_tmp["reflect"] = 1
            state_tmp["count"] = count
            state_tmp["crease_angle"] = new_crease_angle

            state_tmp0 = copy.deepcopy(state_tmp)
            new_states.append(state_tmp0)
            # print "reflect crease", crease_set_min[0]
            # print "reflec2"

    if reflec == 3:
        # valley fold
        state_tmp = {}
        stack = state["stack"]
        h = len(stack) - 1
        stack_info = divideReflectStack(crease_set_max,h,stack,state['polygen'],state['crease_edge'])
        base = stack_info["base"]
        # print "#######################################################"
        sign = determineSign(state["facet_crease"],crease_set_max[0],adj_facets,state["polygen"],base,crease_angle,state['stack'],reflec=1,h=h)
        # print "sign31",sign
        if sign == '+':
            new_stack,count,new_crease_angle,new_polygen,new_creases,new_graph_edge,crease_edge = generateNextStateInformation(state,0,"+",
                                                                                                                               crease_sets=crease_set_max,
                                                                                                                               reflect=1)
            state_tmp["stack"] = new_stack
            state_tmp["polygen"] = new_polygen
            state_tmp["facet_crease"] = new_creases
            state_tmp["fold"] = "valley"
            state_tmp["graph_edge"] = new_graph_edge
            state_tmp["crease_edge"] = crease_edge
            state_tmp["adjacent_facets"] = adj_facets
            state_tmp["reflect"] = 1
            state_tmp["count"] = count
            state_tmp["crease_angle"] = new_crease_angle
            state_tmp0 = copy.deepcopy(state_tmp)
            new_states.append(state_tmp0)
            # print "reflect crease", crease_set_max[0]
            # print "reflec31"

        # mountain fold
        state_tmp = {}
        stack = state["stack"]
        h = 0
        stack_info = divideReflectStack(crease_set_min,h,stack,state['polygen'],state['crease_edge'])
        base = stack_info["base"]
        sign = determineSign(state["facet_crease"],crease_set_min[0],adj_facets,state["polygen"],base,crease_angle,state['stack'],reflec=1,h=h)
        # print "sign32",sign
        if sign == '-':
            new_stack,count,new_crease_angle,new_polygen,new_creases,new_graph_edge,crease_edge = generateNextStateInformation(state,0,"-",
                                                                                                        crease_sets=crease_set_min,
                                                                                                        reflect=1)
            state_tmp["stack"] = new_stack
            state_tmp["polygen"] = new_polygen
            state_tmp["facet_crease"] = new_creases
            state_tmp["fold"] = "mountain"
            state_tmp["graph_edge"] = new_graph_edge
            state_tmp["crease_edge"] = crease_edge
            state_tmp["adjacent_facets"] = adj_facets
            state_tmp["reflect"] = 1
            state_tmp["count"] = count
            state_tmp["crease_angle"] = new_crease_angle

            state_tmp0 = copy.deepcopy(state_tmp)
            new_states.append(state_tmp0)
            # print "reflect crease", crease_set_min[0]
            # print "reflec32"

    return new_states

def VisualState(state,adj_facets,count=0,w=350,h=320):
    '''
    input a state, visuliaze this state
    '''
    #find minimal set of lines taht contain all creases
    creases = findAllCreases(state["stack"],state["facet_crease"])
    crease = findNonRepetiveCreases(creases)

    min_crease = findMininalSetCrease(crease)
    # print "min_creases",min_crease
    #find all feasible creases
    feasible_crease = findFeasibleCrease(min_crease,state["polygen"])
    # print "feasible crease",feasible_crease
    reflec, crease_set_min, crease_set_max = ifReflectable(state)
    # print "reflec",reflec,crease_set_min,crease_set_max

    #prepare canvas
    fold = state["fold"]
    ref = state["reflect"]
    canvas = vl.init_canvas(w,h,reflec=ref)
    rot_mat = vl.rotationFromImg(w,h,0)
    fe = []
    if len(feasible_crease)!=0:
        fe = copy.deepcopy(feasible_crease)

    if reflec==1:
        c_set1 = copy.deepcopy(crease_set_max)
        c_set2 = []
    elif reflec==2:
        c_set2 = copy.deepcopy(crease_set_min)
        c_set1 = []
    elif reflec==3:
        c_set1 = copy.deepcopy(crease_set_max)
        c_set2 = copy.deepcopy(crease_set_min)
    elif reflec==0:
        c_set1 = []
        c_set2 = []
    # print "ref",ref
    img = vl.drawPolygonwithCrease(state["polygen"],state["stack"],canvas,
                                   rot_mat,fold,count,min_crease,fe,
                                   crease_set1=c_set1,crease_set2=c_set2,
                                   reflect=ref)

    return img

# def visualState(state_dict,path,polygen2=polygen2,stack2=stack2):
#     img_num = len(path) + 1
#     print "img num",img_num
#     row = 3
#     if img_num % row == 0:
#         column = int(img_num/3)
#     else:
#         column = int(img_num/3) + 1
#     print "column",column
#     # w = 350 #plane
#     # h = 320 #plane
#     # w = 250 #cup
#     # h = 250 #cup
#     # w = 300 #fig5
#     # h = 300 #fig5
#     w = 450
#     h = 350
#     imgs=[]
#     count = 0
#     canvas = vl.init_canvas(w,h)
#     rot_mat = vl.rotationFromImg(w,h,0)
#     img=vl.drawPolygon(polygen2,stack2,canvas,rot_mat,0,count=0)
#     imgs.append(img)
#     for i in range(len(path)):
#         canvas = vl.init_canvas(w,h)
#         rot_mat = vl.rotationFromImg(w,h,0)
#         fold = state_dict[path[i]]["fold"]
#         stack = state_dict[path[i]]["stack"]
#         if i == 0:
#             stack2 = state_dict[path[0]]["stack"]
#         else:
#             stack2 = state_dict[path[i-1]]["stack"]
#         if fold == "mountain" and (len(stack2)-len(stack)) % 2 == 1:
#             count = count + 1
#
#         img=vl.drawPolygon(state_dict[path[i]]["polygen"],stack,canvas,rot_mat,fold,count)
#         imgs.append(img)
#     vl.drawMultiFigs(imgs,column,row,img_num)
#     plt.show()
# crease_edge = {'8': [[[-75, 30], [0, 105]], [[-75, -45], [-75, 30]]],
#                '5': [[[0, -105], [0, 105]], [[-75, 30], [0, 105]], [[-75, -105], [-75, 30]]],
#                '4': [[[0, -105], [0, 105]]],
#                '7': [[[0, -45], [-75, 30]], [[-75, -45], [-75, 30]]],
#                '6': [[[0, -45], [-75, 30]], [[-75, -105], [-75, 30]]]}
# graph_edge = {'1': [[[-150, 30], [-150, 105]], [[-150, 105], [0, 105]]],
#               '3': [[[-150, -45], [-150, -105]], [[-150, -105], [-75, -105]]],
#               '2': [[[-150, 30], [-150, -45]]],
#               '5': [[[-75, -105], [0, -105]], [[0, -105], [0, 105]], [[-75, 30], [0, 105]], [[-75, -105], [-75, 30]]],
#               '4': [[[-75, -105], [0, -105]], [[0, -105], [0, 105]]],
#               '7': [[[-75, -45], [0, -45]], [[0, -45], [-75, 30]], [[-75, -45], [-75, 30]]],
#               '6': [[[0, -45], [0, -105]], [[0, -105], [-75, -105]], [[0, -45], [-75, 30]], [[-75, -105], [-75, 30]]],
#               '8': [[[-75, -45], [0, -45]], [[0, -45], [0, 105]], [[-75, 30], [0, 105]], [[-75, -45], [-75, 30]]]}
# polygen1 = {'1': [[0, 105], [-150, 105], [-150, 30], [-75, 30]],
#             '3': [[-150, -45], [-150, -105], [-75, -105], [-75, 30]],
#             '2': [[-75, 30], [-150, 30], [-150, -45]],
#             '5': [[-75, 30], [-75, -105], [0, -105], [0, 105]],
#             '4': [[-75, 30], [-75, -105], [0, -105], [0, 105]],
#             '7': [[-75, 30], [-75, -45], [0, -45]],
#             '6': [[0, -45], [0, -105], [-75, -105], [-75, 30]],
#             '8': [[0, 105], [0, -45], [-75, -45], [-75, 30]]}
# facets1 = {'1': [[[-150, 30], [-75, 30]]],
#            '3': [],
#            '2': [[[-75, 30], [-150, 30]]],
#            '5': [],
#            '4': [],
#            '7': [],
#            '6': [],
#            '8': []}
# adjacent_facets = {'1':['2','4'],
#                    '2':['1','3'],
#                    '3':['2','4'],
#                    '4':['1','3','5'],
#                    '5':['4','6','8'],
#                    '6':['5','7'],
#                    '7':['6','8'],
#                    '8':['5','7']}
# state1 = {"stack":stack1,"polygen":polygen1,"facet_crease":facets1,
#           "graph_edge":graph_edge,"crease_edge":crease_edge,
#           "adjacent_facets":adjacent_facets}
# new_state = generateNextLayerStates(state1)
# print "new_state[0]",new_state[0]