#!/usr/bin/env python
"""
Input consists of a simple graph of { node: [list of neighbors] } plus a source and target node.
"""

from collections import deque
import origami_state_generation as osg
import copy
# facets1 = {"1":[[[1,1],[0,0]],[[0,0],[-1,1]]],
#           "2":[[[1,1],[0,0]],[[0,0],[1,-1]]],
#           "3":[[[0,0],[1,-1]],[[0,0],[-1,-1]]],
#           "4":[[[0,0],[-1,-1]],[[0,0],[-1,1]]]}
#
# polygen1 = {"1":[[1,1],[0,0],[-1,1]],
#             "2":[[1,1],[1,-1],[0,0]],
#             "3":[[1,-1],[0,0],[-1,-1]],
#             "4":[[0,0],[-1,-1],[-1,1]]}
# stack1 = [["1","2","3","4"]]
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
state_dict = {"state1":state1}
state_graph = {"state1":[]}

def bfs(state_graph, src, tgt_stack):
    """Return the shortest path from the source (src) to the target (tgt) in the graph"""

    if src in state_graph is False:
        raise AttributeError("The source '%s' is not in the graph" % src)


    parents = {src: None}
    queue = deque([src])
    k = 2
    # #dynamic generate variable's names, using locals()
    # names = locals()
    a = 1
    while queue:
        node = queue.popleft()
        print "node",node
        state_node = state_dict[node]
        # generate children states for this node
        children_states = osg.generateNextLayerStates(state_node)
        print "children states",children_states
        if len(children_states) != 0:
            for i in range(len(children_states)):
                #store each children states
                state_dict["state"+str(k)] = children_states[i]
                #add children states to state_graph
                state_graph.setdefault(node,[]).append("state"+str(k))
                k += 1
        print "state graph",state_graph

        if node in state_graph.keys():
            for neighbor in state_graph[node]:
                if neighbor not in parents:
                    parents[neighbor] = node
                    queue.append(neighbor)
                    print "stack_node[stack]",state_node["stack"]
                    if state_node["stack"] == tgt_stack:
                        break
        else:
            if state_node["stack"] == tgt_stack:
                break


    path = [node]ase [[[0, -105], [0, 105]], [[-46, 151], [29, 76]], [[-150, 30], [-75, 30]], [[-75, -105], [-75, 30]], [[29, 151], [29, 76]]]

    while parents[node] is not None:
        path.insert(0, parents[node])
        node = parents[node]

    return path


path = bfs(state_graph,"state1",[['3'],['2'],['1'],['4'],['5'],['8'],['7'],['6']])
print "path",path
stack_step = []
for i in range(len(path)):
    step_tmp = copy.deepcopy(state_dict[path[i]]["stack"])
    stack_step.append(step_tmp)
print "stack step",stack_step
