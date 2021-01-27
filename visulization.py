#!/usr/bin/env python

import numpy as np
import cv2
import matplotlib.pyplot as plt
import copy
from compiler.ast import flatten
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


def init_canvas(width, height, color=(230,245,253)):
    canvas = np.ones((height, width, 3), dtype="uint8")
    canvas[:] = color
    return canvas

def rotationFromImg(weight,height):
    #return rotation matrix
    rot_mat = [[1,0,weight/2],
               [0,-1,height/2],
               [0,0,1]]
    return rot_mat

def PointsinImg(rot_mat,point):
    # return rotated Points
    point.append(1)
    new_point = np.dot(rot_mat,point)
    new_point = new_point[:2]
    return new_point

def PolygoninImag(rot_mat,polygon):
    rot_poly = copy.deepcopy(polygon)
    for facet in rot_poly.keys():
        poly = rot_poly[facet]
        for i in range(len(poly)):
            poly[i] = PointsinImg(rot_mat,poly[i])
    return rot_poly

def decideOddEven(stack):
    #return odd and even facets, used for filling different colors
    odd_facets = []
    even_facets = []
    for i in range(len(stack)):
        if i % 2 ==0:
            even_facets.append(stack[i])
        elif i % 2 == 1:
            odd_facets.append(stack[i])
    # odd_facets = np.array(odd_facets)
    # even_facets = np.array(even_facets)
    # odd_facets.flatten()
    # even_facets.flatten()
    # odd_facets = odd_facets.tolist()
    # even_facets= even_facets.tolist()
    odd_facets = flatten(odd_facets)
    even_facets = flatten(even_facets)
    return odd_facets,even_facets

def drawPolygon(polygon,stack,canvas,rot_mat):
    rot_poly = PolygoninImag(rot_mat,polygon)
    odd, even = decideOddEven(stack)
    # print "odd",odd
    # print "even",even
    for i in range(len(stack)):
        for j in range(len(stack[i])):
            facet = stack[i][j]
            # print "poly",rot_poly[facet]
            # print "facet",facet
            cv2.polylines(canvas,[np.array(rot_poly[facet])],True,(61,139,110),thickness=8)
            if facet in odd:
                cv2.fillPoly(canvas,[np.array(rot_poly[facet])],(193,255,193)) #,,,(112,255,202) (193,255,193)
            elif facet in even:
                cv2.fillPoly(canvas,[np.array(rot_poly[facet])],(90,205,162)) # ,,(112,255,202) (193,255,193)

    # cv2.imshow('poly', canvas)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()
    return canvas


# drawPolygon(polygen1,stack1,rot_mat)
# img = drawPolygon(polygen1,stack1,canvas,rot_mat)

def drawMultiFigs(imgs,column,row):
    for i in range(column):
        for j in range(row):
            index = i*column + j+i
            print "index",index
            title = "step" + str(index+1)
            plt.subplot(column,row,index+1)
            plt.imshow(imgs[index])
            plt.title(title,fontsize=12) #,fontweight='bold'
            plt.xticks([])
            plt.yticks([])
