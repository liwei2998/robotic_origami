#!/usr/bin/env python
import numpy_indexed as npi
from shapely.geometry import *
import copy
#clockwise?
facets1 = {"1":[[[1,1],[0,0]],[[0,0],[-1,1]]],
          "2":[[[1,-1],[0,0]],[[0,0],[1,1]]],
          "3":[[[1,-1],[0,0]],[[0,0],[-1,-1]]],
          "4":[[[-1,-1],[0,0]],[[0,0],[-1,1]]]}

polygen1 = {"1":[[1,1],[0,0],[-1,1]],
            "2":[[1,1],[1,-1],[0,0]],
            "3":[[1,-1],[0,0],[-1,-1]],
            "4":[[0,0],[-1,-1],[-1,1]]}
stack1 = [["1","2","3","4"]]

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
        k1 = (line1[0][1] - line1[1][1])/(line1[0][0] - line1[1][0])
        k2 = (line2[0][1] - line2[1][1])/(line2[0][0] - line2[1][0])
    is_meet = npi.intersection(line1,line2)

    if k1 == k2 and len(is_meet) > 0:
        return 1
    else:
        return 0
# print "is inter",npi.intersection([[-150, 30], [-75, 30]],[[150,30],[75,30]])
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

# stack2 = [['3','4','5','6','7','8'],['1','2']]
# # #counterclock wise
# polygen1 = {'1': [[0, 105], [0, -45], [-75, -45], [-75, 30]],
#             '3': [[-150, -45], [-150, -105], [-75, -105], [-75, 30]],
#             '2': [[-75, 30], [-75, -45], [-150, -45]],
#             '5': [[0, 105], [0, -105], [75, -105], [75, 30]],
#             '4': [[-75, 30], [-75, -105], [0, -105], [0, 105]],
#             '7': [[75, 30], [150, -45], [150, 30]],
#             '6': [[75, 30], [75, -105], [150, -105], [150, -45]],
#             '8': [[75, 30], [150, 30], [150, 105], [0, 105]]}
# facets1 = {'1': [[[-75, -45], [-75, 30]]],
#            '3': [[[-75, -105], [-75, 30]]],
#            '2': [[[-75, 30], [-75, -45]]],
#            '5': [[[0, 105], [0, -105]], [[75, 30], [75, -105]], [[75, 30], [0, 105]]],
#            '4': [[[-75, 30], [-75, -105]], [[0, 105], [0, -105]]],
#            '7': [[[75, 30], [150, -45]], [[75, 30], [150, 30]]],
#            '6': [[[75, 30], [75, -105]], [[150, -45], [75, 30]]],
#            '8': [[[75, 30], [150, 30]], [[0, 105], [75, 30]]]}
# min_creases=[[[-75, -105], [-75, -45]], [[0, -105], [0, 105]], [[75, -105], [75, 30]], [[0, 105], [150, -45]], [[150, 30], [75, 30]]]
# print "feasible crease",findFeasibleCrease(min_creases,polygen1)

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

# s1+: flap above base
# stackk = [['3','4','5','6','7','8'],['1','2']]
# polygennn = {"1":[[0,105],[0,-45],[-75,-45],[-75,30]],
#             "2":[[-75,30],[-150,30],[-75,-45]],
#             "3":[[-150,-45],[-150,-105],[-75,-105],[-75,30]],
#             "4":[[-75,30],[-75,-105],[0,-105],[0,105]],
#             "5":[[0,105],[0,-105],[75,-105],[75,30]],
#             "6":[[75,30],[75,-105],[150,-105],[150,-45]],
#             "7":[[75,30],[150,-45],[150,30]],
#             "8":[[75,30],[150,30],[150,105],[0,105]]}
# crease_l = [[0,105],[150,-45]]
# crease_l = [[-75,-105],[-75,30]]
# s2+: flap is contained in base
# stackk = [['4','5','6','7','8'],['1'],['2'],['3']]
# polygennn = {"1":[[0,105],[0,-45],[-75,-45],[-75,30]],
#             "2":[[-75,30],[-75,-45],[0,-45]],
#             "3":[[0,-45],[0,-105],[-75,-105],[-75,30]],
#             "4":[[-75,30],[-75,-105],[0,-105],[0,105]],
#             "5":[[0,105],[0,-105],[75,-105],[75,30]],
#             "6":[[75,30],[75,-105],[150,-105],[150,-45]],
#             "7":[[75,30],[150,-45],[150,30]],
#             "8":[[75,30],[150,30],[150,105],[0,105]]}
# crease_l = [[0,105],[150,-45]]
# s3+: some flap above and some flap below tha base
# stackk = [['7','8'],['3','4','5','6'],['1','2']]
# polygennn = {"1":[[0,105],[0,-45],[-75,-45],[-75,30]],
#             "2":[[-75,30],[-75,-45],[0,-45]],
#             "3":[[0,-45],[0,-105],[-75,-105],[-75,30]],
#             "4":[[-75,30],[-75,-105],[0,-105],[0,105]],
#             "5":[[0,105],[0,-105],[75,-105],[75,30]],
#             "6":[[75,30],[75,-105],[150,-105],[150,-45]],
#             "7":[[75,30],[150,-45],[75,-45]],
#             "8":[[75,30],[75,-45],[0,-45],[0,105]]}
# crease_l = [[75,30],[75,-105]]
# s1-: flap below base
# stackk = [['3','4','5','6','7','8'],['1','2']]
# polygennn = {"1":[[0,105],[0,-45],[-75,-45],[-75,30]],
#             "2":[[-75,30],[-150,30],[-75,-45]],
#             "3":[[-150,-45],[-150,-105],[-75,-105],[-75,30]],
#             "4":[[-75,30],[-75,-105],[0,-105],[0,105]],
#             "5":[[0,105],[0,-105],[75,-105],[75,30]],
#             "6":[[75,30],[75,-105],[150,-105],[150,-45]],
#             "7":[[75,30],[150,-45],[150,30]],
#             "8":[[75,30],[150,30],[150,105],[0,105]]}
# crease_l = [[0,105],[150,-45]]
# s2-: flap is contained in base
# stackk = [['3'],['2'],['1'],['4','5','6','7','8']]
# polygennn = {"1":[[0,105],[0,-45],[-75,-45],[-75,30]],
#             "2":[[-75,30],[-75,-45],[0,-45]],
#             "3":[[0,-45],[0,-105],[-75,-105],[-75,30]],
#             "4":[[-75,30],[-75,-105],[0,-105],[0,105]],
#             "5":[[0,105],[0,-105],[75,-105],[75,30]],
#             "6":[[75,30],[75,-105],[150,-105],[150,-45]],
#             "7":[[75,30],[150,-45],[150,30]],
#             "8":[[75,30],[150,30],[150,105],[0,105]]}
# crease_l = [[0,105],[150,-45]]
# s3-: some flap above and some flap below tha base
# stackk = [['1','2'],['3','4','5','6'],['7','8']]
# polygennn = {"1":[[0,105],[0,-45],[-75,-45],[-75,30]],
#             "2":[[-75,30],[-75,-45],[0,-45]],
#             "3":[[0,-45],[0,-105],[-75,-105],[-75,30]],
#             "4":[[-75,30],[-75,-105],[0,-105],[0,105]],
#             "5":[[0,105],[0,-105],[75,-105],[75,30]],
#             "6":[[75,30],[75,-105],[150,-105],[150,-45]],
#             "7":[[75,30],[150,-45],[75,-45]],
#             "8":[[75,30],[75,-45],[0,-45],[0,105]]}
# crease_l = [[75,-105],[75,30]]
# goal stack test
# stackk = [['3','6'],['2','7'],['1','8'],['4','5']]
# polygennn = {"1":[[0,105],[0,-45],[-75,-45],[-75,30]],
#             "2":[[-75,30],[-75,-45],[0,-45]],
#             "3":[[0,-45],[0,-105],[-75,-105],[-75,30]],
#             "4":[[-75,30],[-75,-105],[0,-105],[0,105]],
#             "5":[[0,105],[0,-105],[75,-105],[75,30]],
#             "6":[[75,30],[75,-105],[0,-105],[0,-45]],
#             "7":[[75,30],[75,-45],[0,-45]],
#             "8":[[75,30],[75,-45],[0,-45],[0,105]]}
# crease_l = [[0,-105],[0,105]]
# base,flap = divideStack(crease_l,stackk,polygennn)
# print "base,flap",base,flap
# new_stack = reverseStack(base,flap,crease_l,polygennn,"+")
# print "new_stack",new_stack
# reversed_polygen = reversePolygen(flap,feasible_crease[0],polygen1)
# print "reversed polygen",reversed_polygen
# reversed_creases = reverseCrease(flap,feasible_crease[0],facets1)
# print "reversed crease",reversed_creases

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

        state_tmp0 = copy.deepcopy(state_tmp)
        new_states.append(state_tmp0)

        state_tmp = {}
        new_stack,new_polygen,new_creases = generateNextStateInformation(state["stack"],state["polygen"],
                                                                         state["facet_crease"],feasible_crease[i],
                                                                         "-")
        state_tmp["stack"] = new_stack
        state_tmp["polygen"] = new_polygen
        state_tmp["facet_crease"] = new_creases

        state_tmp0 = copy.deepcopy(state_tmp)
        new_states.append(state_tmp0)
    return new_states
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

state1 = {"stack":stack1,"polygen":polygen1,"facet_crease":facets1}

# state2 = generateNextLayerStates(new_states[2])
# print "new state",state2
#
# new_statess1 = generateNextLayerStates(new_states[0])
# print "new_states1",new_statess1
