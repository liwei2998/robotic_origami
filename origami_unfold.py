#!/usr/bin/env python
import numpy_indexed as npi
from shapely.geometry import *
import copy
import numpy as np
import matplotlib.pyplot as plt
from compiler.ast import flatten
import helper as hp
import origami_reflection as osg

################## fig.7 plane
stack1 = [['2'], ['3'], ['4'], ['1'], ['8'], ['5'], ['6'], ['7']]
#counterclock wise
polygen1 = {'1': [[0, 105], [0, -45], [-75, -45], [-75, 30]],
            '3': [[0, -45], [0, -105], [-75, -105], [-75, 30]],
            '2': [[-75, 30], [-75, -45], [0, -45]],
            '5': [[0, 105], [0, -105], [-75, -105], [-75, 30]],
            '4': [[-75, 30], [-75, -105], [0, -105], [0, 105]],
            '7': [[-75, 30], [0, -45], [-75, -45]],
            '6': [[-75, 30], [-75, -105], [0, -105], [0, -45]],
            '8': [[-75, 30], [-75, -45], [0, -45], [0, 105]]}
facets1 = {'1': [],
           '3': [],
           '2': [],
           '5': [],
           '4': [],
           '7': [],
           '6': [],
           '8': []}
graph_edge = {'1': [[[-75,-45],[0,-45]],[[0,-45],[0,105]],[[-75,30],[0,105]],[[-75,-45],[-75,30]]],
              '3': [[[0,-45], [0,-105]],[[0,-105],[-75,-105]],[[0,-45],[-75,30]],[[-75,-105],[-75,30]]],
              '2': [[[-75,-45],[0,-45]],[[0,-45],[-75,30]],[[-75,-45],[-75,30]]],
              '5': [[[0,-105],[-75,-105]],[[0,105],[-75,30]],[[0,105],[0,-105]],[[-75,-105],[-75,30]]],
              '4': [[[-75, -105],[0,-105]],[[-75, 0],[0,105]],[[-75,-105],[-75,30]],[[0,105],[0,-105]]],
              '7': [[[0,-45],[-75,-45]],[[-75,30],[0,-45]],[[-75, 45],[-75,30]]],
              '6': [[[0,-105],[0,-45]],[[-75,-105],[0,-105]],[[-75,30],[0,-45]],[[-75,-105],[-75,30]]],
              '8': [[[-75,-45],[0,-45]],[[0,-45],[0,105]],[[0,105],[-75,30]],[[-75,-45],[-75,30]]]}
crease_edge = {'1': [[[-75, 30], [0, 105]], [[-75, -45], [-75, 30]]],
               '3': [[[0, -45], [-75, 30]], [[-75, -105], [-75, 30]]],
               '2': [[[0, -45], [-75, 30]], [[-75, -45], [-75, 30]]],
               '5': [[[0, 105], [-75, 30]], [[0, 105], [0, -105]], [[-75, -105], [-75, 30]]],
               '4': [[[-75, 30], [0, 105]], [[-75, -105], [-75, 30]], [[0, 105], [0, -105]]],
               '7': [[[-75, 30], [0, -45]], [[-75, -45], [-75, 30]]],
               '6': [[[-75, 30], [0, -45]], [[-75, -105], [-75, 30]]],
               '8': [[[0, 105], [-75, 30]], [[-75, -45], [-75, 30]]]}
adjacent_facets = {'1':['2','4'],
                   '2':['1','3'],
                   '3':['2','4'],
                   '4':['1','3','5'],
                   '5':['4','6','8'],
                   '6':['5','7'],
                   '7':['6','8'],
                   '8':['5','7']}
count = {'1': 1,
         '3': 1,
         '2': 2,
         '5': 1,
         '4': 0,
         '7': 3,
         '6': 2,
         '8': 2}
state1 = {"stack":stack1,"polygen":polygen1,"facet_crease":facets1,
          "graph_edge":graph_edge,"crease_edge":crease_edge,
          "adjacent_facets":adjacent_facets,"count":count}

def get_common_crease(facet1,facet2,state):
    #input 2 adjacent facets, return the common crease between them
    crease_edge = state['crease_edge']
    creases1 = crease_edge[facet1]
    creases2 = crease_edge[facet2]
    for crease1 in creases1:
        for crease2 in creases2:
            if osg.ifLineSame(crease1,crease2):
                return crease1

def combine_linear_lines(lines):
    #input lines, combine the linear ones and remain the non-linear one
    #find the linear ones
    if len(lines) == 1:
        return lines
    linear_index = []

    new_lines = []
    # print 'lines',lines
    for i in range(len(lines)):
        linear_temp = []
        line1 = lines[i]
        if i in linear_index:
            continue
        linear_index.append(i)
        linear_temp.append(line1)
        for j in range(i,len(lines)):
            line2 = lines[j]
            if j in linear_index:
                continue
            if osg.ifLineColinear(line1,line2) == 1:
                linear_index.append(j)
                linear_temp.append(line2)
        # print 'linear index',linear_index
        # print 'linear temp',linear_temp
        new_lines= new_lines + osg.CombineLinearLines(linear_temp)
    return new_lines


def get_feasible_unfold_crease(facets,state):
    # input a facet list,
    # output a crease that can be feasibly unfolded, the output is non-repetitive
    # only the crease edge can be unfolded

    # 1: get all unfoldable creases (non-repeatitive)
    crease_edge = state['crease_edge']
    adjacent_facets = state['adjacent_facets']
    unfold_creases = []
    for i in range(len(facets)):
        for j in range(len(facets[i])):
            facet = facets[i][j]
            creases = crease_edge[facet]
            for crease in creases:
                if crease not in unfold_creases and [crease[1],crease[0]] not in unfold_creases:
                    unfold_creases.append(crease)
    # print 'unfold_creasessss',unfold_creases
    # 2: determine which crease is feasible
    # 2.1
    remove_facets = []
    if len(unfold_creases) == 1:
        return unfold_creases, remove_facets
    # 2.2
    elif len(facets) == 1:
        if len(facets[0]) == 1:
            return None, None
        elif len(facets[0]) > 1:
            for i in range(len(facets[0])):
                facet = facets[0][i]
                # print 'facet',facet
                # get its adj facets
                adj_facets = adjacent_facets[facet]
                adj_facets = npi.intersection(adj_facets,flatten(facets))
                # print 'adj facets2',adj_facets
                #delete infeasible unfold creases
                if len(adj_facets) == 0:
                    if len(crease_edge[facet]) > 1:
                        remove_facets.append(facet)
                        for k in range(len(crease_edge[facet])):
                            if crease_edge[facet][k] in unfold_creases:
                                unfold_creases.remove(crease_edge[facet][k])
                            elif [crease_edge[facet][k][1],crease_edge[facet][k][0]] in unfold_creases:
                                unfold_creases.remove([crease_edge[facet][k][1],crease_edge[facet][k][0]])
            # print 'unfold creases func',unfold_creases
            unfold_crease = combine_linear_lines(unfold_creases)
            if len(unfold_crease) == 0:
                return None, None
            print 'unfold crease func',unfold_crease
            return unfold_crease, remove_facets
    # 2.3
    elif len(facets) > 1:
        for i in range(len(facets)):
            for j in range(len(facets[i])):
                facet = facets[i][j]
                # print 'facet',facet
                # get its adj facets
                adj_facets = adjacent_facets[facet]
                adj_facets = npi.intersection(adj_facets,flatten(facets))
                # print 'adj facets2',adj_facets
                #delete infeasible creases
                if len(adj_facets) == 0:
                    if len(crease_edge[facet]) > 1:
                        remove_facets.append(facet)
                        for k in range(len(crease_edge[facet])):
                            if crease_edge[facet][k] in unfold_creases:
                                unfold_creases.remove(crease_edge[facet][k])
                            elif [crease_edge[facet][k][1],crease_edge[facet][k][0]] in unfold_creases:
                                unfold_creases.remove([crease_edge[facet][k][1],crease_edge[facet][k][0]])
                elif len(adj_facets) > 0:
                    for adj_facet in adj_facets:
                        layers = osg.findLayersofFacets([facet,adj_facet],state['stack'])
                        if len(layers) > 1:
                            common_crease = get_common_crease(facet,adj_facet,state)
                            # print 'common crease',common_crease
                            if common_crease in unfold_creases:
                                unfold_creases.remove(common_crease)
                            elif [common_crease[1],common_crease[0]] in unfold_creases:
                                unfold_creases.remove([common_crease[1],common_crease[0]])
        unfold_crease = combine_linear_lines(unfold_creases)
        if len(unfold_crease) == 0:
            return None, None
        return unfold_crease, remove_facets

def sort_facets_by_layer(state,facets):
    #sort the input facets by layer
    if len(facets) == 1:
        return [facets]

    stack = state['stack']
    facet_stack = {}
    for facet in facets:
        layer = osg.findLayerofFacet(facet,stack)
        facet_stack.setdefault(facet,layer)
    sort_temp = sorted(facet_stack.items(),key=lambda item:item[1])
    new_stack = []
    for i in range(len(sort_temp)-1):
        stack_temp = []
        facet1 = sort_temp[i][0]
        layer1 = sort_temp[i][1]
        stack_temp.append(facet1)
        for j in range(i+1,len(sort_temp)):
            facet2 = sort_temp[j][0]
            layer2 = sort_temp[j][1]
            if layer1 == layer2:
                stack_temp.append(facet2)
            else:
                break
        new_stack.append(stack_temp)
    return new_stack

def get_unfold_flap(state,root_facet='4'):
    #determine feasible unfoldable flap
    #intially unfold from top to the bottom
    # there are two situations that the unfold direction will be changed

    def reverse2sign(reverse):
        if reverse is False:
            return '-'
        if reverse is True:
            return '+'

    def situation0(state,reverse=False):
        #normal situation
        # when reverse=false, unfold from top to bottom
        # when reverse =true, unfold from bottom to top
        stack = copy.deepcopy(state['stack'])

        if reverse is False:
            flap = [stack[-1]]
        elif reverse is True:
            flap = [stack[0]]

        # print 'initial flap',flap
        unfold_crease, remove_facets = get_feasible_unfold_crease(flap,state)
        # print 'unfold_crease',unfold_crease

        if unfold_crease is not None:
            # print 'flap in situation',flap
            # print 'remove facet',remove_facets
            if len(unfold_crease) == 1:
                flap1 = copy.deepcopy(flap)
                for i in range(len(flap1)):
                    for j in range(len(flap1[i])):
                        facet = flap1[i][j]
                        print 'facet',facet
                        if facet in remove_facets:
                            flap[i].remove(facet)
                return [flap], reverse2sign(reverse), unfold_crease
            elif len(unfold_crease) > 1:
                situation2(state,reverse,flap)

        #if unfold crease is none, find new unfoldable flap
        if reverse is False:
            for i in range(-2,-len(stack)-1,-1):
                flap = flap + [stack[i]]
                flap = flap[::-1]
                # print 'false reverse flap',flap
                if root_facet in flatten(flap):
                    situation1(state)
                    break

                unfold_crease, remove_facets = get_feasible_unfold_crease(flap,state)
                # print 'false reverse unfold_crease',unfold_crease
                if unfold_crease is not None:
                    if len(unfold_crease) == 1:
                        flap1 = copy.deepcopy(flap)
                        for i in range(len(flap1)):
                            for j in range(len(flap1[i])):
                                facet = flap[i][j]
                                if facet in remove_facets:
                                    flap[i].remove(facet)
                        return [flap], reverse2sign(reverse), unfold_crease
                    elif len(unfold_crease) > 1:
                        situation2(state,reverse,flap)
                        break

        elif reverse is True:
            for i in range(1,len(stack)):
                flap = flap + [stack[i]]
                if root_facet in flatten(flap):
                    print 'this origami cannot be unfolded!'
                    return None
                unfold_crease, remove_facets = get_feasible_unfold_crease(flap,state)
                if unfold_crease is not None:
                    if len(unfold_crease) == 1:
                        flap1 = copy.deepcopy(flap)
                        for i in range(len(flap1)):
                            for j in range(len(flap1[i])):
                                facet = flap[i][j]
                                if facet in remove_facets:
                                    flap[i].remove(facet)
                        return [flap], reverse2sign(reverse), unfold_crease
                    elif len(unfold_crease) > 1:
                        situation2(state,reverse,flap)
                        break

    def situation1(state,reverse=True):
        # if contain root facet, reverse unfold direction
        situation0(state,reverse)

    def situation2(state,reverse,flap):
        # if contain non-conlinear creases, determine the combination of facets
        # divide the facets according to its adj facets
        new_flap = []
        adjacent_facets = state['adjacent_facets']
        for i in range(len(flap)):
            new_flap_temp = []
            for j in range(len(flap[i])):
                facet = flap[i][j]
                if facet not in flatten(new_flap):
                    layer = 999
                else:
                    #determine which layer of the new_flap
                    for layer in range(len(new_flap)):
                        if facet in new_flap[layer]:
                            break
                # print 'facet',facet
                # print 'layer',layer
                new_flap_temp.append(facet)
                adj_facets = adjacent_facets[facet]
                adj_facets = npi.intersection(adj_facets,flatten(flap))
                new_flap_temp = new_flap_temp + flatten(adj_facets)
                new_flap_temp = set(new_flap_temp)
                new_flap_temp = list(new_flap_temp)
                # print 'new flap temp',new_flap_temp
                if layer == 999:
                    new_flap.append(new_flap_temp)
                else:
                    new_flap[layer] = new_flap[layer] + new_flap_temp
                    new_flap[layer] = set(new_flap[layer])
                    new_flap[layer] = list(new_flap[layer])
        for i in range(len(new_flap)):
            new_flap[i] = sort_facets_by_layer(state,new_flap[i])
        # print 'new flap in unfold flap func',new_flap
        unfold_creases = []
        for i in range(len(new_flap)):
            unfold_crease, remove_facets = get_feasible_unfold_crease(new_flap[i],state)
            # print 'unfold crease in unfold flap func',unfold_crease
            if unfold_crease is None or len(unfold_crease) != 1:
                print 'situation2 error!'
                return None
            unfold_creases.append(unfold_crease)
            flap1 = copy.deepcopy(flap)
            for i in range(len(flap1)):
                for j in range(len(flap1[i])):
                    facet = flap[i][j]
                    if facet in remove_facets:
                        flap[i].remove(facet)
        return new_flap, reverse2sign(reverse), unfold_creases

    return situation0(state)

def get_base_and_flap(flap,state):
    stack = copy.deepcopy(state['stack'])
    # print 'flap in fnccccccc',flap
    # print 'stack in fnccccccc',stack
    # if len(flap) == 1:
    #     flap = flap[0]
    base = []
    for i in range(len(stack)):
        facets = stack[i]
        # print 'facets',facets
        if len(npi.intersection(facets,flatten(flap))) == 0:
            # print 'base facets',facets
            base.append(facets)
        elif len(npi.intersection(facets,flatten(flap))) == len(facets):
            break
        else:
            facets = npi.difference(facets,flatten(flap))
            # print 'else facets',facets
            facets = facets.tolist()
            base.append(facets)

    return base,flap

def reverseStack(base,flap,crease,polygen,stack,sign):
    '''
    input base stack and flap stack, return reversed stack
    '''
    #sign + is valley, sign - is mountain
    new_stack = []
    polygen = osg.reversePolygen(flap,crease,polygen)
    if sign == "+":
        #flap above the base
        #base stack will be remained, add base first
        new_stack = base
        #reverse the flap
        new_flap = flap[::-1]
        #determine layer of bottom flap facet
        index = osg.findLayerofFacet(new_flap[0][0],stack)
        index = index + 1 #new flap should be inserted to this index layer
        layer_tmp = 0
        for i in range(index,index+len(new_flap)):
            # print 'index',i
            # print 'layer_tmp',layer_tmp
            new_stack[i] = new_stack[i] + new_flap[layer_tmp]
            layer_tmp = layer_tmp + 1

    elif sign == "-":
        #flap below the base
        #base stack will be remained, add base first
        new_stack = base
        #reverse the flap
        new_flap = flap[::-1]
        #determine layer of bottom flap facet
        index = osg.findLayerofFacet(new_flap[-1][0],stack)
        index = index - 1 #new flap should be inserted to this index layer
        layer_tmp = len(new_flap) - 1
        # print 'new stack',new_stack
        # print 'new flap',new_flap
        for i in range(index,index-len(new_flap),-1):
            # print 'index',i
            # print 'layer_tmp',layer_tmp
            new_stack[i] = new_stack[i] + new_flap[layer_tmp]
            layer_tmp = layer_tmp - 1

    return new_stack


def reverseCrease(flap,crease,crease_set):
    new_crease_set = copy.deepcopy(crease_set)
    # remain creases in base stack
    # reverse creases in flap stack
    # print 'crease in reverseCrease func',crease
    for i in range(len(flap)):
        for j in range(len(flap[i])):
            facet = flap[i][j]
            # print 'facet in reverseCrease func',facet
            creases = crease_set[facet]
            # print 'creases',creases
            new_creases = []
            for k in range(len(creases)):
                # print 'crease[k]',creases[k]
                new_creases.append(osg.reverseLine(crease,creases[k]))
            new_crease_set[facet] = new_creases
    return new_crease_set

def CreaseDisassemble(crease_set,long_crease):
    #disassemble long creases into short creases
    creases = []
    for facet in crease_set.keys():
        crease_tmp = crease_set[facet]
        for i in range(len(crease_tmp)):
            crease = crease_tmp[i]
            if osg.ifLineColinear(long_crease,crease) == 1 and crease not in creases:
                creases.append(crease)
    return creases

def get_folded_creases_and_facets(creases,crease_set,flap,sign,stack):
    #in new crease edge, graph_edge, facet_crease, folded creases need to be delete or add
    #output facets and creases that should be modified in old crease set

    #find facets that has the creases
    facets = {}
    for crease in creases:
        for facet in crease_set.keys():
            crease_temps = crease_set[facet]
            for crease_temp in crease_temps:
                if osg.ifLineSame(crease,crease_temp) == 1 and facet not in facets:
                    facets.setdefault(facet,crease_temp)
    # print 'facets',facets

    #find related facets
    crease_facet = {}
    if sign == '-':
        flap_facet = flap[0][0]
        layer = osg.findLayerofFacet(flap_facet,stack)
        layers = np.arange(len(stack)-1,layer-1-len(flap),-1)
    elif sign == '+':
        flap_facet = flap[-1][0]
        layer = osg.findLayerofFacet(flap_facet,stack)
        layers = np.arange(0,layer+1+len(flap))
    layers = layers.tolist()
    for facet in facets.keys():
        index = osg.findLayerofFacet(facet,stack)
        if index in layers:
            crease_facet[facet] = facets[facet]

    return crease_facet

def get_new_edge(flap,crease,sign,state,mode='crease_edge'):
    #reverse crease in crease_edge, delete folded crease_edge
    if mode == 'crease_edge':
        crease_set = copy.deepcopy(state['crease_edge'])
    elif mode == 'graph_edge':
        crease_set = copy.deepcopy(state['graph_edge'])
    stack = copy.deepcopy(state['stack'])

    creases = CreaseDisassemble(crease_edge,crease)
    #get modified facets and corresponding creass
    modified_facet = get_folded_creases_and_facets(creases,crease_set,flap,sign,stack)
    #delete the modified crease and facets
    for facet in modified_facet.keys():
        modified_crease = modified_facet[facet]
        if modified_crease in crease_set[facet]:
            crease_set[facet].remove(modified_crease)
        elif osg.reverseLine(modified_crease) in crease_set[facet]:
            crease_set[facet].remove(osg.reverseLine(modified_crease))

    reversed_edge = reverseCrease(flap,crease,crease_set)
    return reversed_edge

def get_new_facet_crease(flap,crease,sign,state):
    #reverse crease in facet_crease, add folded crease
    facet_crease = copy.deepcopy(state['facet_crease'])
    stack = copy.deepcopy(state['stack'])
    crease_edge = copy.deepcopy(state['crease_edge'])

    reversed_facet_crease = reverseCrease(flap,crease,facet_crease)
    #first add folded crease
    creases = CreaseDisassemble(crease_edge,crease)
    #get modified facets and corresponding creass
    modified_facet = get_folded_creases_and_facets(creases,crease_edge,flap,sign,stack)
    # print 'modified facet',modified_facet
    ######ccw or cw can be modified here
    ######ccw or cw can be modified here

    for facet in modified_facet.keys():
        modified_crease = modified_facet[facet]
        # print 'modified crease',modified_crease
        reversed_facet_crease.setdefault(facet,[])
        reversed_facet_crease[facet].append(modified_crease)

    return reversed_facet_crease

def get_new_count(flap,state):
    new_count = copy.deepcopy(state['count'])
    flap_temp = flatten(flap)

    for facet in flap_temp:
        new_count[facet] = new_count[facet] - 1
    return new_count



# crease1 = get_feasible_unfold_crease([['7']],state1)
# # print 'crease1',crease1
# crease2 = get_feasible_unfold_crease([['6'],['7']],state1)
# # print 'crease2',crease2
# flap, reverse, unfold_crease = get_unfold_flap(state1)
# # print 'flap',flap
# # print 'reverse',reverse
# # print 'unfold crease',unfold_crease
# base,flap = get_base_and_flap(flap,state1)
# # print 'base',base
# # print 'flap',flap
# reversed_stack = reverseStack(base,flap,unfold_crease[0],state1['polygen'],state1['stack'],'-')
# # print 'reversed stack',reversed_stack
# new_crease_edge = get_new_edge(flap,unfold_crease[0],'-',state1,mode='crease_edge')
# # print 'new crease_edge',new_crease_edge
# new_graph_edge = get_new_edge(flap,unfold_crease[0],'-',state1,mode='graph_edge')
# # print 'new graph_edge',new_graph_edge
# new_polygen = osg.reversePolygen(flap,unfold_crease[0],state1['polygen'])
# # print 'new polygen',new_polygen
# new_facet_crease = get_new_facet_crease(flap,unfold_crease[0],'-',state1)
# # print 'new facet crease',new_facet_crease




def get_next_layer_states(state):
    '''
    input parent node state information, return next layer's children states
    '''
    new_states = []

    stack = state["stack"]
    polygen = state["polygen"]
    adj_facets = state["adjacent_facets"]

    #find foldable flap, the fold direction and unfold crease
    intial_flap, sign, unfold_crease = get_unfold_flap(state)
    print 'initial flap',intial_flap
    print 'sign', sign
    print 'unfold crease',unfold_crease
    for i in range(len(unfold_crease)):
        print '***********************************************'
        state_tmp = {}

        flap = intial_flap[i]
        crease = unfold_crease[i]

        #decide base and flap
        base,flap = get_base_and_flap(flap,state)
        # print 'base',base
        # print 'flap',flap
        #reverse stack
        new_stack = reverseStack(base,flap,crease,polygen,stack,sign)
        print 'new_stack',new_stack
        #reverse polygen
        new_polygen = osg.reversePolygen(flap,crease,polygen)
        # print 'new polygen',new_polygen
        #reverse crease edge
        new_crease_edge = get_new_edge(flap,crease,sign,state,mode='crease_edge')
        # print 'new crease edge',new_crease_edge
        #reverse graph edge
        new_graph_edge = get_new_edge(flap,crease,sign,state,mode='graph_edge')
        # print 'new graph edge',new_graph_edge
        #reverse facet_crease
        new_facet_crease = get_new_facet_crease(flap,crease,sign,state)
        # print 'new facet crease',new_facet_crease
        #new count
        new_count = get_new_count(flap,state)
        # print 'new count',new_count

        state_tmp["stack"] = new_stack
        state_tmp["count"] = new_count
        state_tmp["polygen"] = new_polygen
        state_tmp["facet_crease"] = new_facet_crease

        state_tmp["graph_edge"] = new_graph_edge
        state_tmp["crease_edge"] = new_crease_edge
        state_tmp["adjacent_facets"] = adj_facets
        state_tmp0 = copy.deepcopy(state_tmp)
        new_states.append(state_tmp0)

    return new_states
