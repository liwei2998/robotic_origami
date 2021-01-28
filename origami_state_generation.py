#!/usr/bin/env python
import numpy_indexed as npi
from shapely.geometry import *
import copy
import numpy as np
# ##############plane
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
#
# state1 = {"stack":stack1,"polygen":polygen1,"facet_crease":facets1}
# graph_edge = {"1":[[[-150,30],[-150,105]],[[-150,105],[0,105]]],
#               "2":[[[-150,30],[-150,-45]]],
#               "3":[[[-150,-45],[-150,-105]],[[-150,-105],[-75,-105]]],
#               "4":[[[-75,-105],[0,-105]]],
#               "5":[[[0,-105],[75,-105]]],
#               "6":[[[75,-105],[150,-105]],[[150,-105],[150,-45]]],
#               "7":[[[150,-45],[150,30]]],
#               "8":[[[150,30],[150,105]],[[150,105],[0,105]]]}

def ifLineColinear(line1,line2):
    '''
    input two lines, return if they are colinear and meet at a vertex
    '''
    "line1 = [[0,0],[1,1]]"
    if line1[0][0] == line1[1][0] and line2[0][0] == line2[1][0]:
        k1 = 0
        k2 = 0
    elif line1[0][0] == line1[1][0] and line2[0][0] != line2[1][0]:
        return 0
    elif line1[0][0] != line1[1][0] and line2[0][0] == line2[1][0]:
        return 0
    else:
        k1 = (float(line1[0][1]) - float(line1[1][1]))/(float(line1[0][0]) - float(line1[1][0]))
        k2 = (float(line2[0][1]) - float(line2[1][1]))/(float(line2[0][0]) - float(line2[1][0]))
    is_meet = npi.intersection(line1,line2)
    if k1 == k2 and len(is_meet) > 0:
        return 1
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

# def ifLineSame(line1,line2):
#     if len(npi.difference(line1,line2)) == 0:
#         return 1
#     else:
#         return 0

def CombineLinearLines(line1,line2):
    '''
    input two colinear lines, return the combined one line
    '''
    "line1 = [[0,0],[1,1]]"
    new_line = npi.exclusive(line1,line2)
    new_line = new_line.tolist()
    return new_line

def findAllCreases(stack,facet_crease):
    creases = []
    for i in range(len(stack)):
        for j in range(len(stack[i])):
            facet = stack[i][j]
            for k in range(len(facet_crease[facet])):
                creases.append(facet_crease[facet][k])

    return creases

def findNonRepetiveCreases(creases):
    #serach for non-repetitive creases
    #each crease will appear and only appear twice
    crease = []
    index = []
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

# def findMininalSetCrease1(crease):
#     #find linear creases, and combine them
#     min_crease = []
#     lin_crease = []
#     colinear_num = []
#     if len(crease) == 1:
#         min_crease = crease
#         return min_crease
#     for i in range(len(crease)):
#         line1 = crease[i]
#         for j in range(i+1,len(crease)):
#             line2 = crease[j]
#             if ifLineSame(line1,line2)==1:
#                 continue
#             #combine linear creases
#
#             if ifLineColinear(line1,line2)==1:
#                 min_crease.append(CombineLinearLines(line1,line2))
#                 colinear_num.append(j)
#                 colinear_num.append(i)
#                 break
#             #if the line is not colinear with any other lines
#         if j == (len(crease)-1) and i not in colinear_num:
#             min_crease.append(line1)
#     return min_crease

# creases = findAllCreases(stack1,facets1)
# print "crease",creases
# crease = findNonRepetiveCreases(creases)
# print "crease",crease
# min_crease = findMininalSetCrease(crease)
# print "min_crease",min_crease
#how to set(min_crease)

def is_inPoly(polygen,point):
    #determine if a point is in a polygen
    line = LineString(polygen)
    pointt = Point(point)
    polygen = Polygon(line)
    return polygen.contains(pointt)

def findFeasibleCrease(crease,polygen):
    # find feasible creases among min_crease
    # discard the creases that cross any facet
    feasible_crease=[]
    for k in range(len(crease)):
        point1 = crease[k][0]
        point2 = crease[k][1]
        dx = (point1[0] - point2[0])/20
        dy = (point1[1] - point2[1])/20
        point1 = [point1[0]+dx,point1[1]+dy]
        point2 = [point2[0]-dx,point2[1]-dy]
        count = 0
        for facet in polygen.keys():
            count = count + 1
            poly = polygen[facet]
            if is_inPoly(poly,point1)==1 or is_inPoly(poly,point2)==1:
                break
            # if this creasse does not cross any facet
            elif count == len(polygen):
                feasible_crease.append(crease[k])

    return feasible_crease

def lineToFunction(line):
    "input line[[x1,y1],[x2,y2]], return k,b (ax+by+c=0)"
    # a = y2-y1, b = x1-x2, c=x2*y1-x1*y2
    a = line[1][1] - line[0][1]
    b = line[0][0] - line[1][0]
    c = line[1][0]*line[0][1] - line[0][0]*line[1][1]
    return a,b,c

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
        elif product < 0:
            return reverseLineDirection(crease)

def divideStack(crease,stack,polygon):
    #define base at the right of crease, crease has direction
    base = []
    flap = []
    crease = ifReverseLineDirection(polygon,crease)
    # print "crease",crease
    a,b,c = lineToFunction(crease)
    for i in range(len(stack)):
        base_tmp = []
        flap_tmp = []
        for j in range(len(stack[i])):
            facet = stack[i][j]
            poly = polygon[facet]
            for k in range(len(poly)):
                # product represents the relationship between a point and a line
                product = a*poly[k][0]+b*poly[k][1]+c
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
# poly1=[[-75, -105],[-75, 30],[0, 105], [0, -105]]
# poly2=[[-75, 30], [0, 105], [0,-45], [-75,-45]]
# print "is intersection",polygenIntersectionCheck(poly1,poly2)
# feasible_crease = findFeasibleCrease(min_crease,stack1,polygen1)
# print "feasible_crease",feasible_crease
# base,flap = divideStack(feasible_crease[0],stack1,polygen1,"+")
# print "base_stack",base
# print "flap_stack",flap

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

##############plane
stack1 = [['1','2','3','4'],['5','6'],['7','8']]
#counterclock wise
polygen1 = {"1":[[0,105],[-150,105],[-150,30],[-75,30]],
            "2":[[-75,30],[-150,30],[-150,-45]],
            "3":[[-150,-45],[-150,-105],[-75,-105],[-75,30]],
            "4":[[-75,30],[-75,-105],[0,-105],[0,105]],
            "5":[[-75,30],[-75,-105],[0,-105],[0,105]],
            "6":[[-150,-45],[-150,-105],[-75,-105],[-75,30]],
            "7":[[-75,30],[-75,-45],[-150,-45]],
            "8":[[0,105],[0,-45],[-75,-45],[-75,30]]
            }
facets1 = {"1":[[[-150,30],[-75,30]],[[-75,30],[0,105]]],
           "2":[[[-150,-45],[-75,30]],[[-75,30],[-150,30]]],
           "3":[[[-75,-105],[-75,30]],[[-75,30],[-150,-45]]],
           "4":[[[-75,30],[-75,-105]],[[0,105],[-75,30]]],
           "5":[[[-75,30],[-75,-105]],[[0,105],[-75,30]]],
           "6":[[[-75,-105],[-75,30]],[[-75,30],[-150,-45]]],
           "7":[[[-75,-45],[-75,30]]],
           "8":[[[-75,-45],[-75,30]]]
           }

state1 = {"stack":stack1,"polygen":polygen1,"facet_crease":facets1}
graph_edge = {"1":[[[-150,30],[-150,105]],[[-150,105],[0,105]]],
              "2":[[[-150,30],[-150,-45]]],
              "3":[[[-150,-45],[-150,-105]],[[-150,-105],[-75,-105]]],
              "4":[[[-75,-105],[0,-105]],[[0,-105],[0,105]]],
              "5":[[[-75,-105],[0,-105]],[[0,-105],[0,105]]],
              "6":[[[-150,-45],[-150,-105]],[[-150,-105],[-75,-105]]],
              "7":[[[-75,30],[-150,-45]],[[-75,-45],[-150,-45]]],
              "8":[[[0,105],[-75,30]],[[-75,-45],[0,-45]],[[0,-45],[0,105]]]}


def ifCutGraph(crease,stack,height,graph_edge=graph_edge):
    #test if a crease cuts the origami graph
    #if 2 points of the crease are all on the edge of a graph, return true
    count = 0
    tmp = 999

    for i in range(len(crease)):
        point = crease[i]
        for j in stack[height]:
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

def findMinimalCreasebyHeight(stack,facet_crease):
    h_crease = {"min":[],"max":[]}
    min_h = 0
    max_h = len(stack) - 1
    if max_h == min_h:
        creases = findAllCreases(stack[min_h],facet_crease)
        crease = findNonRepetiveCreases(creases)
        min_h_crease = findMininalSetCrease(crease)
        h_crease["min"] = min_h_crease
        h_crease["max"] = min_h_crease
    else:
        creases = findAllCreases(stack[min_h],facet_crease)
        crease = findNonRepetiveCreases(creases)
        min_h_crease = findMininalSetCrease(crease)
        h_crease["min"] = min_h_crease

        creases = findAllCreases(stack[max_h],facet_crease)
        crease = findNonRepetiveCreases(creases)
        max_h_crease = findMininalSetCrease(crease)
        h_crease["max"] = max_h_crease
    return h_crease

def findReflectionCrease(stack,facet_crease):
    reflect_crease={"min":[],"max":[]}
    h_crease = findMinimalCreasebyHeight(stack,facet_crease)
    if len(stack)==1:
        h_crease_tmp = h_crease["min"]
        # print "h_crease",h_crease_tmp
        for i in range(len(h_crease_tmp)):
            crease = h_crease_tmp[i]
            # print "crease",crease
            if ifCutGraph(crease,stack,0)==1:
                reflect_crease["min"].append(crease)
                reflect_crease["max"].append(crease)
            else:
                continue
        return reflect_crease

    elif len(stack)>1:
        min_h_crease = h_crease["min"]
        for i in range(len(min_h_crease)):
            crease = min_h_crease[i]
            if ifCutGraph(crease,stack,0)==1:
                reflect_crease["min"].append(crease)
            else:
                continue

        max_h_crease = h_crease["max"]
        for i in range(len(max_h_crease)):
            crease = max_h_crease[i]
            if ifCutGraph(crease,stack,(len(stack)-1))==1:
                reflect_crease["max"].append(crease)
            else:
                continue
        return reflect_crease

creases = findAllCreases(stack1,facets1)
# print "crease",creases
crease = findNonRepetiveCreases(creases)
# print "crease",crease
min_crease = findMininalSetCrease(crease)
# print "min_crease",min_crease
reflect_creases = findReflectionCrease(stack1,facets1)
print "reflect creases",reflect_creases

def divideReflectStack(reflect_crease,height,stack,polygon):
    #specially for reflection fold, return base, flap and sign(mountain or valley)
    #define base at the right of crease, crease has direction
    base = []
    flap = []
    crease = ifReverseLineDirection(polygon,reflect_crease)
    if height == "min":
        sign = '-'
        a,b,c = lineToFunction(crease)
        for facet in stack[0]:
            base_tmp = []
            flap_tmp = []
            poly = polygon[facet]
            for k in range(len(poly)):
                # product represents the relationship between a point and a line
                product = a*poly[k][0]+b*poly[k][1]+c
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
        for i in range(1,len(stack)):
            base.append(stack[i])
        return base,flap,sign

    if height == "max":
        sign = '+'
        a,b,c = lineToFunction(crease)
        for i in range(len(stack)-2,-1,-1):
            base.append(stack[i])
        for facet in stack[len(stack)-1]:
            base_tmp = []
            flap_tmp = []
            poly = polygon[facet]
            for k in range(len(poly)):
                # product represents the relationship between a point and a line
                product = a*poly[k][0]+b*poly[k][1]+c
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

        return base,flap,sign

base,flap,sign = divideReflectStack(reflect_creases["max"][0],"max",stack1,polygen1)
print "base, flap, sign",base,flap,sign

def reverseReflectStack(base,flap,reflect_crease,polygen,sign):
    '''
    input base stack and flap stack, return reversed reflection stack
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

def ifEdgeReverse(flap):
    #determine the set of edge that need to be reversed
    flap_facets = (np.array(flap)).flatten()
    flap_facets = flap_facets.tolist()
    return flap_facets

def reverseGraphEdge(crease,reverse_edge_facet,graph_edge):
    reversed_edge = copy.deepcopy(graph_edge)
    for facet in reverse_edge_facet:
        edges = graph_edge[facet]
        edge_tmp = []
        for i in range(len(edges)):
            edge = edges[i]
            edge = reverseLine(crease,edge)
            edge_tmp.append(edge)
        reversed_edge[facet] = edge_tmp
    return reversed_edge

def newStateCrease(crease,facet_crease):
    #delete folded crease in new state

    for facet in facet_crease.keys():
        new_creases = copy.deepcopy(facet_crease[facet])
        for i in range(len(new_creases)):
            # print "new",new_creases[i]
            if ifLineColinear(crease,new_creases[i]) == 1:
                # print "1",facet_crease[facet][i]
                del facet_crease[facet][i]

    return facet_crease

def lineToAxis(line):
    dx = line[1][0]-line[0][0]
    dy = line[1][1]-line[0][1]
    axis=[dx,dy]
    axis = np.array(axis)/np.linalg.norm(np.array(axis))
    return axis

def ifLineColinear1(line1,line2):
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

def ifCreaseinFacet(crease,facet_crease):
    # return facets that contain the crease
    c_facet = {}
    tmp = 999
    for facet in facet_crease.keys():
        f_crease = facet_crease[facet]
        for i in range(len(f_crease)):
            crease_tmp = f_crease[i]
            if ifLineColinear1(crease,crease_tmp) == 1:
                c_facet.setdefault(facet,crease_tmp)
                tmp = 888
                break
        if tmp == 888:
            tmp = 999
            continue
    return c_facet


# flap = [['7','8']]
# flap_facets = ifEdgeReverse(flap)
# creaseee = [[0, 105], [-150, -45]]
# reversed_edge = reverseGraphEdge(creaseee,flap_facets,graph_edge)
# # print "reversed edge",reversed_edge
# crease_facet = ifCreaseinFacet(creaseee,facets1)
# print "crease facet",crease_facet

def findLayerofFacet(facet,stack):
    for i in range(len(stack)):
        facets = stack[i]
        if facet in facets:
            return i

def findLayersofFacets(facets,stack):
    facet_layer = []
    for facet in facets:
        layer = findLayerofFacet(facet,stack)
        facet_layer.append(layer)
    facet_layer = set(facet_layer)
    facet_layer = list(facet_layer)
    return facet_layer

def findOtherFacetsinLayer(facets,layer,stack):
    facetss = stack[layer]
    other_facets = npi.difference(facetss,facets)
    return other_facets

# facet_layer = findLayersofFacets(flap_facets,stack1)
# print "facet layers",facet_layer
# other_facets = findOtherFacetsinLayer(flap_facets,facet_layer[0],stack1)
# print "other facets",other_facets

def newStateEdge(reversed_edge,crease_facet,flap_facets,stack,facet_crease):
    new_edges = copy.deepcopy(reversed_edge)
    layers = findLayersofFacets(flap_facets,stack)
    tmp = 999
    for facet in flap_facets:
        new_edge = crease_facet[facet]
        new_edges[facet].append(new_edge)
        for i in layers:
            other_facets = findOtherFacetsinLayer(flap_facets,i,stack)
            for j in other_facets:
                creaseee = facet_crease[j]
                for k in creaseee:
                    if ifLineSame(new_edge,k) == 1:
                        new_edges[j].append(new_edge)
                        tmp = 888
                        break
                if tmp == 888:
                    break
            if tmp == 888:
                break
        if tmp == 888:
            tmp = 999
            continue
    return new_edges

# new_edges = newStateEdge(reversed_edge,crease_facet,flap_facets,stack1,facets1)
# print "new state edges",new_edges


def generateNextStateInformation(stack,polygen,facet_crease,crease,sign):
    '''
    Given a feasible crease fold, previous stack and polygen and facet_crease information,
    return new stack and polygen and facet_crease information.
    '''
    #search for base and flap according to this crease
    # print "crease",crease
    base,flap = divideStack(crease,stack,polygen)
    # print "base, flap",base,flap
    #generate new stack
    reversed_stack = reverseStack(base,flap,crease,polygen,sign)
    # print "reversed stack", reversed_stack
    #generate new polygen
    reversed_polygen = reversePolygen(flap,crease,polygen)
    # print "reversed polygen",reversed_polygen
    #generate new facet creases
    reversed_creases = reverseCrease(flap,crease,facet_crease)
    # print "reversed crease",reversed_creases
    new_crease = newStateCrease(crease,reversed_creases)
    return reversed_stack,reversed_polygen,new_crease


def generateNextLayerStates(state):
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
    #generate new states for each feasible crease
    for i in range(len(feasible_crease)):
        state_tmp = {}
        new_stack,new_polygen,new_creases = generateNextStateInformation(state["stack"],state["polygen"],
                                                                         state["facet_crease"],feasible_crease[i],
                                                                         "+")
        state_tmp["stack"] = new_stack
        state_tmp["polygen"] = new_polygen
        state_tmp["facet_crease"] = new_creases
        state_tmp["fold"] = "valley"

        state_tmp0 = copy.deepcopy(state_tmp)
        new_states.append(state_tmp0)

        state_tmp = {}
        new_stack,new_polygen,new_creases = generateNextStateInformation(state["stack"],state["polygen"],
                                                                         state["facet_crease"],feasible_crease[i],
                                                                         "-")
        state_tmp["stack"] = new_stack
        state_tmp["polygen"] = new_polygen
        state_tmp["facet_crease"] = new_creases
        state_tmp["fold"] = "mountain"
        state_tmp0 = copy.deepcopy(state_tmp)
        new_states.append(state_tmp0)
    return new_states

# state2 = generateNextLayerStates(new_states[2])
# print "new state",state2
#
# new_statess1 = generateNextLayerStates(new_states[0])
# print "new_states1",new_statess1
