#!/usr/bin/env python

import numpy as np
import cv2
import matplotlib.pyplot as plt
import copy
import matplotlib.gridspec as gridspec
from matplotlib.patches import ConnectionPatch
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.collections import PolyCollection
from compiler.ast import flatten
import networkx as nx
import helper as hp
import math
import origami_reflection as osg
from shapely.ops import cascaded_union
import geopandas as gpd
from shapely.geometry import *
import numpy_indexed as npi
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

#light blue:(230,245,253)
#light blue: (240,255,255) pink:(255,240,245)
def init_canvas(width, height,reflec=0, color1=(230,245,253), color2=(255,240,245)):
    canvas = np.ones((height, width, 3), dtype="uint8")
    if reflec == 0:
        canvas[:] = color1
    elif reflec == 1:
        canvas[:] = color2
    return canvas

def init_canvas1(width, height,reflec=0, color1=(230,245,253), color2=(255,240,245)):
    canvas = np.ones((height, width, 3), dtype="uint8")
    canvas[:] = (255,255,255)
    return canvas

def rotationFromImg(weight,height,hat=0):
    #return rotation matrix
    if hat == 0:
        rot_mat = [[1,0,weight/2],
                   [0,-1,height/2],
                   [0,0,1]]
    elif hat == 1:
        rot_mat = [[0,1,weight/2],
                   [1,0,height/2],
                   [0,0,1]]
    elif hat == 2:
        rot_mat = [[-1,0,weight/2],
                   [0,1,height/2],
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

def LineRotation(rot_mat,line):
    point1 = line[0]
    point2 = line[1]
    new_p1 = PointsinImg(rot_mat,point1)
    new_p2 = PointsinImg(rot_mat,point2)
    new_p1 = new_p1[:2]
    new_p2 = new_p2[:2]
    new_line = [new_p1,new_p2]
    return new_line

def CreaseinImag(rot_mat,crease):
    new_creases = copy.deepcopy(crease)
    for i in range(len(crease)):
        new_crease = LineRotation(rot_mat,crease[i])
        new_creases[i] = new_crease
    return new_creases

def EdgeRotation(rot_mat,edge_dict):
    rot_edge = copy.deepcopy(edge_dict)
    for edge in rot_edge.keys():
        lines = rot_edge[edge]
        for line in lines:
            line = LineRotation(rot_mat,line)
    return rot_edge

def decideLightDark(count):
    light_facets = []
    dark_facets = []
    for key in count.keys():
        if count[key] % 2 == 1:
            light_facets.append(key)
        elif count[key] % 2 == 0:
            dark_facets.append(key)
    return light_facets,dark_facets


def drawPolygon(polygon,stack1,canvas,rot_mat,count,reflec=0):
    rot_poly = PolygoninImag(rot_mat,polygon)
    odd, even = decideLightDark(count)
    color11 = (139,58,98)
    color21 = (255,181,197)
    color31 = (205,96,144)
    color10 = (61,139,110)
    color20 = (193,255,193)
    color30 = (90,205,162)
    if reflec == 0:
        color1 = color10
        color2 = color20
        color3 = color30
    elif reflec == 1:
        color1 = color11
        color2 = color21
        color3 = color31
    # print "odd",odd
    # print "even",even
    for i in range(len(stack1)):
        for j in range(len(stack1[i])):
            facet = stack1[i][j]
            # print "poly",rot_poly[facet]
            # print "facet",facet
            cv2.polylines(canvas,[np.array(rot_poly[facet])],True,color1,thickness=8) #green:(61,139,110) gold:(76,129,139) purple:(139,102,139)
            if facet in odd:
                cv2.fillPoly(canvas,[np.array(rot_poly[facet])],color2) #green:(193,255,193) gold:(139,236,255) purple:(255,187,255)
            elif facet in even:
                cv2.fillPoly(canvas,[np.array(rot_poly[facet])],color3) #green:(90,205,162) gold:(112,190,205) purple:(205,150,205)

    # cv2.imshow('poly', canvas)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()
    return canvas

def drawline(img,pt1,pt2,color,thickness=5,style='dotted',gap=22):
    dist =((pt1[0]-pt2[0])**2+(pt1[1]-pt2[1])**2)**.5
    pts= []
    for i in np.arange(0,dist,gap):
        r=i/dist
        x=int((pt1[0]*(1-r)+pt2[0]*r)+.5)
        y=int((pt1[1]*(1-r)+pt2[1]*r)+.5)
        p = (x,y)
        pts.append(p)

    if style=='dotted':
        for p in pts:
            cv2.circle(img,p,thickness,color,-1)
    else:
        s=pts[0]
        e=pts[0]
        i=0
        for p in pts:
            s=e
            e=p
            if i % 2==1:
                cv2.line(img,s,e,color,thickness)
            i+=1

def drawPolygonwithCrease(polygon,stack1,canvas,rot_mat,count,min_crease,feasible_crease,crease_set1=[],crease_set2=[],reflect=0):
    rot_min_creases = CreaseinImag(rot_mat,min_crease)
    rot_feasible_creases = CreaseinImag(rot_mat,feasible_crease)
    rot_poly = PolygoninImag(rot_mat,polygon)
    rot_c_set1 = copy.deepcopy(crease_set1)
    # print "c_set",rot_c_set1
    if len(crease_set1)!=0:
        rot_c_set1 = CreaseinImag(rot_mat,crease_set1)
    rot_c_set2 = copy.deepcopy(crease_set2)
    if len(crease_set2)!=0:
        rot_c_set2 = CreaseinImag(rot_mat,crease_set2)
    odd, even = decideLightDark(count)
    color11 = (139,58,98)
    color21 = (255,181,197)
    color31 = (205,96,144)
    color10 = (61,139,110)
    color20 = (193,255,193)
    color30 = (90,205,162)
    if reflect == 0:
        color1 = color10
        color2 = color20
        color3 = color30
    elif reflect == 1:
        color1 = color11
        color2 = color21
        color3 = color31
    # print "odd",odd
    # print "even",even
    # print "stack1",stack1
    for i in range(len(stack1)):
        for j in range(len(stack1[i])):
            facet = stack1[i][j]
            # print "poly",rot_poly[facet]
            # print "facet",facet
            cv2.polylines(canvas,[np.array(rot_poly[facet])],True,color1,thickness=8) #green:(61,139,110) pink:(139,58,98) gold:(76,129,139) purple:(139,102,139)
            if facet in odd:
                cv2.fillPoly(canvas,[np.array(rot_poly[facet])],color2) #green:(193,255,193) pink:(255,181,197) gold:(139,236,255) purple:(255,187,255)
            elif facet in even:
                cv2.fillPoly(canvas,[np.array(rot_poly[facet])],color3) #green:(90,205,162) pink:(205,96,144) gold:(112,190,205) purple:(205,150,205)
    for i in range(len(rot_min_creases)):
        p1 = rot_min_creases[i][0]
        p2 = rot_min_creases[i][1]
        drawline(canvas,p1,p2,(255,99,71))
    for i in range(len(rot_feasible_creases)):
        p1 = rot_feasible_creases[i][0]
        p2 = rot_feasible_creases[i][1]
        p1 = (p1[0],p1[1])
        p2 = (p2[0],p2[1])
        cv2.line(canvas,p1,p2,color=(255,99,71),thickness=7)
    for i in range(len(rot_c_set1)):
        p1 = rot_c_set1[i][0]
        p2 = rot_c_set1[i][1]
        p1 = (p1[0],p1[1])
        p2 = (p2[0],p2[1])
        cv2.line(canvas,p1,p2,color=(255,99,71),thickness=7) #blue(0,245,255)
        # drawline(canvas,p1,p2,(255,99,71))
    for i in range(len(rot_c_set2)):
        p1 = rot_c_set2[i][0]
        p2 = rot_c_set2[i][1]
        p1 = (p1[0],p1[1])
        p2 = (p2[0],p2[1])
        cv2.line(canvas,p1,p2,color=(255,99,71),thickness=7)
        # drawline(canvas,p1,p2,(255,99,71))
    # cv2.imshow('poly', canvas)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()
    return canvas

def VisualState(state,adj_facets,count,pattern,w=340,h=280):
    '''
    input a state, visuliaze this state
    '''
    if pattern == 'samurai':
        creases = osg.findAllCreases(state["stack"],state["crease_edge"])
    else:
        #find minimal set of lines taht contain all creases
        creases = osg.findAllCreases(state["stack"],state["facet_crease"])
    # print "creassssss",state['facet_crease']
    # print 'creases',creases
    crease = osg.findNonRepetiveCreases(creases)
    # print 'crease',crease
    min_crease = osg.findMininalSetCrease(crease)
    # print "min_creases",min_crease
    #find all feasible creases
    feasible_crease = osg.findFeasibleCrease(min_crease,state["polygen"])
    # print "feasible crease",feasible_crease
    reflec, crease_set_min, crease_set_max = osg.ifReflectable(state,pattern)
    # print "reflec",reflec,crease_set_min,crease_set_max

    #prepare canvas
    ref = state["reflect"]
    # canvas = init_canvas1(w,h,reflec=ref)
    canvas = init_canvas(w,h,reflec=ref)
    rot_mat = rotationFromImg(w,h,0)
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
    # print 'count',count
    img = drawPolygonwithCrease(state["polygen"],state["stack"],canvas,
                               rot_mat,count,min_crease,fe,
                               crease_set1=c_set1,crease_set2=c_set2,
                               reflect=ref)

    return img

rot_mat = rotationFromImg(300,300,0)

def clockwiseangle_and_distance(point):
    refvec = [0, 1]
    # Vector between point and the origin: v = p - o
    vector = [point[0]-origin[0], point[1]-origin[1]]
    # Length of vector: ||v||
    lenvector = math.hypot(vector[0], vector[1])
    # If length is zero there is no angle
    if lenvector == 0:
        return -math.pi, 0
    # Normalize vector: v/||v||
    normalized = [vector[0]/lenvector, vector[1]/lenvector]
    dotprod = normalized[0]*refvec[0] + normalized[1]*refvec[1]     # x1*x2 + y1*y2
    diffprod = refvec[1]*normalized[0] - refvec[0]*normalized[1]     # x1*y2 - y1*x2
    angle = math.atan2(diffprod, dotprod)
    # Negative angles represent counter-clockwise angles so we need to subtract them
    # from 2*pi (360 degrees)
    if angle < 0:
        return 2*math.pi+angle, lenvector
    # I return first the angle because that's the primary sorting criterium
    # but if two vectors have the same angle then the shorter distance should come first.
    return angle, lenvector

def RightTurn(p1, p2, p3):
    if (p3[1]-p1[1])*(p2[0]-p1[0]) >= (p2[1]-p1[1])*(p3[0]-p1[0]):
        return False
    return True

def GrahamScan(P):
    P.sort() # Sort the set of points
    L_upper = [P[0], P[1]] # Initialize upper part
    # Compute the upper part of the hull
    for i in range(2,len(P)):
        L_upper.append(P[i])
        while len(L_upper) > 2 and not RightTurn(L_upper[-1],L_upper[-2],L_upper[-3]):
            del L_upper[-2]
    L_lower = [P[-1], P[-2]]	# Initialize the lower part
    # Compute the lower part of the hull
    for i in range(len(P)-3,-1,-1):
        L_lower.append(P[i])
        while len(L_lower) > 2 and not RightTurn(L_lower[-1],L_lower[-2],L_lower[-3]):
            del L_lower[-2]
    del L_lower[0]
    del L_lower[-1]
    L = L_upper + L_lower		# Build the full hull
    return L

def drawPolygon1(state,rot_mat=rot_mat):
    polygon = state['polygen']
    stack1 = state['stack']

    # color1 = (61,139,110)
    # color2 = (193,255,193)
    # color3 = (90,205,162)

    fig = plt.figure()
    ax = fig.gca(projection='3d')
    layer_poly = []

    for i in range(len(stack1)-1,-1,-1):
        temp = []
        for j in range(len(stack1[i])):
            facet = stack1[i][j]
            poly = polygon[facet]
            # print 'poly1',poly
            temp = temp + poly
        # temp = np.array(temp)
        # global origin
        # origin = [np.mean(temp[:,0]),np.mean(temp[:,1])]
        # # print 'origin',origin
        # temp = sorted(temp, key=clockwiseangle_and_distance)
        # # print 'temp',temp
        temp = GrahamScan(temp)
        # print 'temp',temp
        layer_poly.append(temp)

    ys = np.arange(1,len(stack1)*10+1,10)
    # ys = [0]


    color = []
    for i in range(len(stack1)-1,-1,-1):
        if i % 2 == 0:
            color.append(('#3CB371')) #dark
        else:
            color.append(('#C1FFC1')) #light
    # polyy = PolyCollection(layer_poly, facecolors=[('#C1FFC1'),('#3CB371'),('#C1FFC1'),('#3CB371'),('#C1FFC1'),('#3CB371'),('#C1FFC1'),('#3CB371')])
    polyy = PolyCollection(layer_poly, facecolors=color)
    polyy.set_alpha(0.7)
    ax.add_collection3d(polyy, zs=ys, zdir='y')
    ax.set_xlabel('x')
    ax.set_xlim3d(-150, 165)
    ax.set_ylabel('layer')
    ax.set_ylim3d(0, len(stack1)*10+4)
    # ax.set_ylim3d(-1,1)
    ax.set_zlabel('z')
    ax.set_zlim3d(-150,165)
    ax.grid(False)
    ax.view_init(15,-42)
    plt.show()


def drawOneFig(img):
    title = "node"
    plt.imshow(img)
    plt.title(title,fontsize=12)
    plt.xticks([])
    plt.yticks([])
    plt.show()

# drawPolygon(polygen1,stack1,rot_mat)
# img = drawPolygon(polygen1,stack1,canvas,rot_mat)

def drawMultiFigs(imgs,column,row,img_num):
    for i in range(column):
        for j in range(row):
            index = i*column + j-i
            # print "index",index
            if index >= img_num:
                break
            # title = "step" + str(index+1)
            plt.subplot(column,row,index+1)
            plt.imshow(imgs[index])
            # plt.title(title,fontsize=12) #,fontweight='bold'
            plt.xticks([])
            plt.yticks([])

###############visuliaze parent kids graph###############################
def drawMultiFigsGraph(imgs,row):
    #draw a parent children graph
    gs0 = gridspec.GridSpec(2,1)
    gs1 = gridspec.GridSpecFromSubplotSpec(1,3,subplot_spec=gs0[0])
    gs2 = gridspec.GridSpecFromSubplotSpec(1,row,subplot_spec=gs0[1])
    ax1 = plt.subplot(gs1[0,1])
    ax1.imshow(imgs[0])
    plt.title("parent node",fontsize=12)
    plt.xticks([])
    plt.yticks([])
    for i in range(1,len(imgs)):
        ax = plt.subplot(gs2[0,i-1])
        ax.imshow(imgs[i])
        title = "node" + str(i)
        plt.title(title,fontsize=12)
        plt.xticks([])
        plt.yticks([])
    plt.tight_layout()

def visualParentChildren(state_graph,parent_state,state_dict,adjacent_facets):
    # visualize parent and its children nodes
    imgs = []
    count = state_dict[parent_state]["count"]
    # print "count",count
    img = VisualState(state_dict[parent_state],adjacent_facets,count)
    # vl.drawOneFig(img)
    imgs.append(img)
    if parent_state in state_graph.keys():
        img_num = len(state_graph[parent_state])
        for node in state_graph[parent_state]:
            count = state_dict[node]["count"]
            img = VisualState(state_dict[node],adjacent_facets,count)
            imgs.append(img)
    else:
        img_num = 1
    drawMultiFigsGraph(imgs,img_num)
    plt.show()
###############visuliaze parent kids graph###############################

##################visualize the search tree#####################################
# def drawTree(imgs,column,row,img_num):
#     # draw a search tree
#     gs0 = gridspec.GridSpec(column,1)
#     gs1 = gridspec.GridSpecFromSubplotSpec(1,3,subplot_spec=gs0[0])
#     gs2 = gridspec.GridSpecFromSubplotSpec(1,row[1],subplot_spec=gs0[1])
#     gs3 = gridspec.GridSpecFromSubplotSpec(1,row[2],subplot_spec=gs0[2])
#     gs4 = gridspec.GridSpecFromSubplotSpec(1,row[3],subplot_spec=gs0[3])
#     gs5 = gridspec.GridSpecFromSubplotSpec(1,row[4],subplot_spec=gs0[4])
#     gs6 = gridspec.GridSpecFromSubplotSpec(1,row[5],subplot_spec=gs0[5])
#     ax1 = plt.subplot(gs1[0,1])
#     ax1.imshow(imgs[0][0])
#     plt.title("state1",fontsize=8)
#     plt.xticks([])
#     plt.yticks([])
#     num = 1
#     # gs2.update(wspace=0,hspace=0)
#     # gs3.update(wspace=0,hspace=0)
#     # gs4.update(wspace=0,hspace=0)
#     # gs5.update(wspace=0,hspace=0)
#     # gs6.update(wspace=0,hspace=0)
#     for k in range(1,len(row)):
#         for i in range(1,row[k]+1):
#             if k == 1:
#                 ax = plt.subplot(gs2[0,i-1])
#             elif k == 2:
#                 ax = plt.subplot(gs3[0,i-1])
#             elif k == 3:
#                 ax = plt.subplot(gs4[0,i-1])
#             elif k == 4:
#                 ax = plt.subplot(gs5[0,i-1])
#             elif k == 5:
#                 ax = plt.subplot(gs6[0,i-1])
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

def drawTree(imgs,column,row,img_num):
    # draw a search tree
    gs0 = gridspec.GridSpec(column,1)
    # print 'row',row
    gs1 = gridspec.GridSpecFromSubplotSpec(1,3,subplot_spec=gs0[0])
    gs2 = gridspec.GridSpecFromSubplotSpec(1,row[1],subplot_spec=gs0[1])
    gs3 = gridspec.GridSpecFromSubplotSpec(1,row[2],subplot_spec=gs0[2])
    gs4 = gridspec.GridSpecFromSubplotSpec(1,row[3],subplot_spec=gs0[3])
    gs5 = gridspec.GridSpecFromSubplotSpec(1,row[4],subplot_spec=gs0[4])
    gs6 = gridspec.GridSpecFromSubplotSpec(1,row[5],subplot_spec=gs0[5])
    ax1 = plt.subplot(gs1[0,1])
    ax1.imshow(imgs[0][0])
    plt.title("node1",fontsize=8)
    plt.xticks([])
    plt.yticks([])
    num = 1
    # gs2.update(wspace=0,hspace=0)
    # gs3.update(wspace=0,hspace=0)
    # gs4.update(wspace=0,hspace=0)
    # gs5.update(wspace=0,hspace=0)
    # gs6.update(wspace=0,hspace=0)
    for k in range(1,len(row)):
        for i in range(1,row[k]+1):
            if k == 1:
                ax = plt.subplot(gs2[0,i-1])
            elif k == 2:
                ax = plt.subplot(gs3[0,i-1])
            elif k == 3:
                ax = plt.subplot(gs4[0,i-1])
            elif k == 4:
                ax = plt.subplot(gs5[0,i-1])
            elif k == 5:
                ax = plt.subplot(gs6[0,i-1])
            ax.imshow(imgs[num][0])
            title = imgs[num][1]
            num = num + 1
            title = "node" + str(num)
            plt.title(title,fontsize=8)
            plt.xticks([])
            plt.yticks([])


        # title = "node" + str(i)
        # plt.title(title,fontsize=12)
        # plt.xticks([])
        # plt.yticks([])
    plt.tight_layout()

def drawTree_samurai(imgs,column,row,img_num):
    # draw a search tree
    gs0 = gridspec.GridSpec(column,1)
    # print 'row',row
    gs1 = gridspec.GridSpecFromSubplotSpec(1,3,subplot_spec=gs0[0])
    gs2 = gridspec.GridSpecFromSubplotSpec(1,row[1],subplot_spec=gs0[1])
    gs3 = gridspec.GridSpecFromSubplotSpec(1,row[2],subplot_spec=gs0[2])
    gs4 = gridspec.GridSpecFromSubplotSpec(1,row[3],subplot_spec=gs0[3])
    gs5 = gridspec.GridSpecFromSubplotSpec(1,row[4],subplot_spec=gs0[4])
    gs6 = gridspec.GridSpecFromSubplotSpec(1,row[5],subplot_spec=gs0[5])
    gs7 = gridspec.GridSpecFromSubplotSpec(1,row[6],subplot_spec=gs0[1])
    gs8 = gridspec.GridSpecFromSubplotSpec(1,row[7],subplot_spec=gs0[2])
    gs9 = gridspec.GridSpecFromSubplotSpec(1,row[8],subplot_spec=gs0[3])
    gs10 = gridspec.GridSpecFromSubplotSpec(1,row[9],subplot_spec=gs0[4])
    gs11 = gridspec.GridSpecFromSubplotSpec(1,row[10],subplot_spec=gs0[5])
    ax1 = plt.subplot(gs1[0,1])
    ax1.imshow(imgs[0][0])
    plt.title("node1",fontsize=8)
    plt.xticks([])
    plt.yticks([])
    num = 1
    # gs2.update(wspace=0,hspace=0)
    # gs3.update(wspace=0,hspace=0)
    # gs4.update(wspace=0,hspace=0)
    # gs5.update(wspace=0,hspace=0)
    # gs6.update(wspace=0,hspace=0)
    for k in range(1,len(row)):
        for i in range(1,row[k]+1):
            if k == 1:
                ax = plt.subplot(gs2[0,i-1])
            elif k == 2:
                ax = plt.subplot(gs3[0,i-1])
            elif k == 3:
                ax = plt.subplot(gs4[0,i-1])
            elif k == 4:
                ax = plt.subplot(gs5[0,i-1])
            elif k == 5:
                ax = plt.subplot(gs6[0,i-1])

            elif k == 6:
                ax = plt.subplot(gs7[0,i-1])
            elif k == 7:
                ax = plt.subplot(gs8[0,i-1])
            elif k == 8:
                ax = plt.subplot(gs9[0,i-1])
            elif k == 9:
                ax = plt.subplot(gs10[0,i-1])
            elif k == 10:
                ax = plt.subplot(gs11[0,i-1])
            ax.imshow(imgs[num][0])
            title = imgs[num][1]
            num = num + 1
            title = "node" + str(num)
            plt.title(title,fontsize=8)
            plt.xticks([])
            plt.yticks([])


        # title = "node" + str(i)
        # plt.title(title,fontsize=12)
        # plt.xticks([])
        # plt.yticks([])
    plt.tight_layout()

def visualTree(state_graph,path,state_dict,pattern='cup'):
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
            # print 'count',state_dict[j]['count']
            img = VisualState(state_dict[j],state_dict['state1']["adjacent_facets"],state_dict[j]["count"],pattern)
            img_tmp = copy.deepcopy(img)
            imgs.append([img_tmp,j])
            if j not in state_graph.keys():
                continue
            src_tmp = state_graph[j]
            src_tmpp = []
            for state in src_tmp:
                src_tmpp.append(state)
            src_list_tmp.append(src_tmpp)
            row_tmp = row_tmp + len(src_tmpp)
        src = [x for j in src_list_tmp for x in j]
        row.append(row_tmp)
    # print "columnnn",column
    row = row[:column]
    # print "rowwww",row
    img_num = sum(row)
    # print "imgss",len(imgs)
    # print "img num",img_num
    if pattern == 'samurai':
        drawTree_samurai(imgs,column,row,img_num+1)
    else:
        drawTree(imgs,column,row,img_num+1)
    plt.show()
    return imgs
##############visualize the search tree#####################################

######################visulize the search graph#############################
def drawGraph(state_dict,state_graph_culled,path,pattern='cup',weight=0,pos=0):
    #draw the search graph
    # G = nx.DiGraph()
    G = nx.DiGraph()
    layer = len(path)
    w = 6 #airplane
    # w = 8
    pos = {'state1':(3,layer)}
    src = ['state1']
    k = 1
    layer = layer - 1
    while layer > 0:
        state = 'state' + str(k)
        k = k + 1
        if state in src:
            children = []
            for i in range(len(src)):
                if len(state_graph_culled[src[i]]) == 0:
                    continue
                for kid in state_graph_culled[src[i]]:

                    children.append(kid)
            children = set(children)
            children = list(children)
            children = sorted(children, key=lambda x: int(x[5:]))
            # print "children",children
            # print "layer",layer
            src = children
            num = len(children)
            for i in range(len(children)):
                pos.setdefault(children[i],[])
                if num == 1:
                    pos[children[i]] = [w/2,layer]
                else:
                    pos[children[i]] = [2*i+4-num,layer]
            layer = layer - 1
    # print "src",src
    # print "pos",pos

    #pruned based on the physics
    for state in pos.keys():
        G.add_node(state,desc=state)
        if state not in state_graph_culled.keys():
            continue
        for kid in state_graph_culled[state]:
            if kid not in pos.keys():
                continue
            G.add_node(kid,desc=kid)
            weight = hp.determineWeight(state_dict[kid])
            # print "weight",weight
            G.add_edge(state,kid,weight=weight)
    #not pruned
    # for state in state_graph_culled.keys():
    #     G.add_node(state,desc=state)
    #     for kid in state_graph_culled[state]:
    #         G.add_node(kid,desc=kid)
    #         weight = hp.determineWeight(state_dict[kid])
    #         # print "weight",weight
    #         G.add_edge(state,kid,weight=weight)
    nx.draw_networkx(G,pos=pos,with_labels=False,arrows=False,arrowstyle='->',arrowsize=10,node_size=5000,node_color='#00CED1',node_shape='s',alpha=0.5,width=2) #for tree
    # nx.draw_networkx(G,pos=pos,arrows=True,arrowstyle='->',arrowsize=18,node_size=3000,node_color='#00CED1',node_shape='s',alpha=0.5,width=3) #for graph
    # F = G.to_directed()
    # nx.draw_networkx(F,pos=pos,arrows=True,arrowstyle='->',node_size=3000,node_color='#00CED1',node_shape='s',alpha=0.5,width=3)
    # edge_labels = nx.get_edge_attributes(G,'weight')
    # nx.draw_networkx_edge_labels(G,pos,edge_labels=edge_labels,font_size=10)
    # nx.draw_networkx_edge_labels(G,pos,arrows=True)

    node_labels = nx.get_node_attributes(G,'desc')
    nx.draw_networkx_labels(G,pos,labels=node_labels,font_size=8)
    limits = plt.axis('off')
    plt.show()
######################visulize the search graph#############################

#####################visualize the fold sequnce#############################
#,polygen2=polygen2,stack2=stack2s
def visualSteps(state_dict,path):
    #visuliaze fold sequnce
    img_num = len(path) #+ 1
    # print "img num",img_num
    row = 4
    if img_num % row == 0:
        column = int(img_num/3)
    else:
        column = int(img_num/3) + 1
    # print "column",column
    # w = 350 #plane
    # h = 320 #plane
    # w = 250 #cup
    # h = 250 #cup
    # w = 300 #fig5
    # h = 300 #fig5
    w = 340
    h = 340
    imgs=[]
    # canvas = init_canvas(w,h)
    # rot_mat = rotationFromImg(w,h,0)
    # img=drawPolygon(polygen2,stack2,canvas,rot_mat,0,count=0)
    # imgs.append(img)
    for i in range(len(path)):
        canvas = init_canvas(w,h)
        rot_mat = rotationFromImg(w,h,2)

        stack = state_dict[path[i]]["stack"]
        count = state_dict[path[i]]['count']

        img=drawPolygon(state_dict[path[i]]["polygen"],stack,canvas,rot_mat,count)
        imgs.append(img)
    drawMultiFigs(imgs,column,row,img_num)
    plt.show()
#####################visualize the fold sequnce#############################
