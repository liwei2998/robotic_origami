#!/usr/bin/env python
import bfs_plan as bfs
import numpy as np

def findCreaseByPoints(point1,point2):
    if point1[0] == point2[0]:
        a = 0.0
        if (point1[1]+point2[1])==0:
            c = 0.0
            b = 1.0
            return a,b,c
        c = 1.0
        b = -c*2.0 / (point1[1]+point2[1])
        return a,b,c
    elif point1[1] == point2[1]:
        b = 0.0
        if (point1[0]+point2[0])==0:
            c = 0.0
            a = 1.0
            return a,b,c
        c = 1.0
        a = -c*2.0 / (point1[0]+point2[0])
        return a,b,c
    else:
        k = (point1[1]-point2[1])/(point1[0]-point2[0])
        k = -1.0/k
        x = (point1[0]+point2[0])/2.0
        y = (point1[1]+point2[1])/2.0
        if (-k*x+y)==0.0:
            c = 0.0
            b = 1.0
            a = -b*k
            return a,b,c
        else:
            c = 1.0
            b = -c / (-k*x+y)
            a = -b*k
            return a,b,c

def pointsDistance(point1,point2):
    dx = point1[0]-point2[0]
    dy = point1[1]-point2[1]
    dis = np.sqrt(pow(dx,2)+pow(dy,2))
    return dis

def 
def findCreaseByPolygons(polygon1,polygon2):
    for facet in polygon1.keys():
        poly1 = polygon1[facet]
        poly2 = polygon2[facet]
        crease = []
        if (np.array(poly1)==np.array(poly2)).all():
            continue
        else:
            # print "facet",facet
            # print "poly1",poly1
            # print "poly2",poly2
            for i in range(len(poly1)):
                if (np.array(poly1[i])==np.array(poly2[i])).all():
                    continue
                else:
                    # print "poly1[i]",poly1[i]
                    # print "poly2[i]",poly2[i]
                    a,b,c = findCreaseByPoints(poly1[i],poly2[i])
                    crease.append([a,b,c])
                    mani_point =
                    return a,b,c

path, stack_step, state_dict = bfs.findPath()
polygon1 = state_dict[path[2]]["polygen"]
polygon2 = state_dict[path[3]]["polygen"]
a,b,c=findCreaseByPolygons(polygon1,polygon2)
# print "a,b,c",a,b,c
