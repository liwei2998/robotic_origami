#!/usr/bin/env python

import numpy as np
import cv2
import matplotlib.pyplot as plt
import copy
import matplotlib.gridspec as gridspec
from compiler.ast import flatten
import networkx as nx
import helper as hp
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

def rotationFromImg(weight,height,hat=0):
    #return rotation matrix
    if hat == 0:
        rot_mat = [[1,0,weight/2],
                   [0,-1,height/2],
                   [0,0,1]]
    else:
        rot_mat = [[0,1,weight/2],
                   [1,0,height/2],
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

def decideOddEven(stack,fold,count):
    #return odd and even facets, used for filling different colors
    # if valley fold, even is dark
    light_facets = []
    dark_facets = []
    # print "count",count
    # print 'stack',stack
    if count >= 66 and count < 88:
        dark_facets.append(stack[0])
        for i in range(1,len(stack)):
            k = i - 1
            if k % 2 == 1:
                light_facets.append(stack[i])
            elif k % 2 == 0:
                dark_facets.append(stack[i])
    elif count >= 88 and count < 100:
        light_facets.append(stack[-1])
        for i in range(0,len(stack)-1):
            k = i + count
            if k % 2 == 1:
                light_facets.append(stack[i])
            elif k % 2 == 0:
                dark_facets.append(stack[i])
    elif count >= 100:
        light_facets.append(stack[-1])
        dark_facets.append(stack[0])
        for i in range(1,len(stack)-1):
            k = i + count - 1
            if k % 2 == 1:
                light_facets.append(stack[i])
            elif k % 2 == 0:
                dark_facets.append(stack[i])
    else:
        for i in range(len(stack)):
            k = i + count
            if k % 2 == 1:
                light_facets.append(stack[i])
            elif k % 2 == 0:
                dark_facets.append(stack[i])

    light_facets = flatten(light_facets)
    dark_facets = flatten(dark_facets)
    # print 'light',light_facets
    # print 'dark',dark_facets
    return light_facets,dark_facets

def drawPolygon(polygon,stack1,canvas,rot_mat,fold,count,reflec=0):
    rot_poly = PolygoninImag(rot_mat,polygon)
    odd, even = decideOddEven(stack1,fold,count)
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

def drawPolygonwithCrease(polygon,stack1,canvas,rot_mat,fold,count,min_crease,feasible_crease,crease_set1=[],crease_set2=[],reflect=0):
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
    odd, even = decideOddEven(stack1,fold,count)
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
            index = i*column + j+i
            # print "index",index
            if index >= img_num:
                break
            # title = "step" + str(index+1)
            plt.subplot(column,row,index+1)
            plt.imshow(imgs[index])
            # plt.title(title,fontsize=12) #,fontweight='bold'
            plt.xticks([])
            plt.yticks([])

def drawMultiFigsGraph(imgs,row):
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


def drawTree(imgs,column,row,img_num):
    gs0 = gridspec.GridSpec(column,1)
    gs1 = gridspec.GridSpecFromSubplotSpec(1,3,subplot_spec=gs0[0])
    gs2 = gridspec.GridSpecFromSubplotSpec(1,row[1],subplot_spec=gs0[1])
    gs3 = gridspec.GridSpecFromSubplotSpec(1,row[2],subplot_spec=gs0[2])
    gs4 = gridspec.GridSpecFromSubplotSpec(1,row[3],subplot_spec=gs0[3])
    gs5 = gridspec.GridSpecFromSubplotSpec(1,row[4],subplot_spec=gs0[4])
    gs6 = gridspec.GridSpecFromSubplotSpec(1,row[5],subplot_spec=gs0[5])
    ax1 = plt.subplot(gs1[0,1])
    ax1.imshow(imgs[0])
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
            ax.imshow(imgs[num])
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

def drawGraph(state_dict,state_graph_culled,path,weight=0,pos=0):
    # G = nx.DiGraph()
    G = nx.Graph()
    layer = len(path)
    w = 6
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
            children = sorted(children)
            # print "children",children
            # print "layer",layer
            src = children
            num = len(children)
            for i in range(len(children)):
                pos.setdefault(children[i],[])
                if num == 1:
                    pos[children[i]] = [w/2,layer]
                elif num == 3:
                    pos[children[i]] = [w/3*(i+1)-1,layer]
                elif num == 7:
                    pos[children[i]] = [7/7*(i+1)-1,layer]
                else:
                    pos[children[i]] = [w/num*(i+1),layer]
            layer = layer - 1
        # print "src",src

    for state in state_graph_culled.keys():
        G.add_node(state,desc=state)
        for kid in state_graph_culled[state]:
            G.add_node(kid,desc=kid)
            weight = hp.determineWeight(state_dict[state],state_dict[kid])
            # print "weight",weight
            G.add_edge(state,kid,weight=weight)
    nx.draw_networkx(G,pos=pos,arrows=True,arrowstyle='->',arrowsize=18,node_size=3000,node_color='#00CED1',node_shape='s',alpha=0.5,width=3)
    # F = G.to_directed()
    # nx.draw_networkx(F,pos=pos,arrows=True,arrowstyle='->',node_size=3000,node_color='#00CED1',node_shape='s',alpha=0.5,width=3)
    edge_labels = nx.get_edge_attributes(G,'weight')
    nx.draw_networkx_edge_labels(G,pos,edge_labels=edge_labels,font_size=8)
    # nx.draw_networkx_edge_labels(G,pos,arrows=True)

    # node_labels = nx.get_node_attributes(G,'desc')
    # nx.draw_networkx_labels(G,pos,labels=node_labels,font_size=8)
    limits = plt.axis('off')
    plt.show()
