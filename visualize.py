"""Tree-Based Equation Solver by Areez Chishtie: Visualize Module
(CSC111 Winter 2024 Project 2)

Description
===============================

Contains functions relating to visualizing graphs.

Copyright
===============================

The functions 'hierarchy_pos' and '_hierarchy_pos' ARE NOT MINE.
Copyright information for these functions is included in their
docstrings.

The remainder of this file is Copyright © 2024 Areez Chishtie. All
rights reserved."""

import random
import networkx as nx
import matplotlib.pyplot as plt


def visualize(graph: tuple):
    """
    Open a visualization of the given graph.

    Preconditions:
        - the graph is given as in Unit.get_graph.
    """
    edges, labels = graph
    g = nx.Graph()

    if len(edges) == 1 and edges[0][0] == edges[0][1]:  # if graph contains only one vertex
        g.add_node(edges[0][0])
    else:
        g.add_edges_from(edges)

    pos = hierarchy_pos(g, 0)
    nx.draw_networkx(g, pos, None, False)
    nx.draw_networkx_labels(g, pos, labels)
    plt.show()

###########################################################################
# THE FOLLOWING CODE IS NOT MINE. SOURCES ARE INCLUDED IN THE DOCSTRINGS. #
###########################################################################

def hierarchy_pos(G, root = None, width = 1., vert_gap = 0.2, vert_loc = 0, xcenter = 0.5):

    '''
    From Joel's answer at https://stackoverflow.com/a/29597209/2966723.  
    Licensed under Creative Commons Attribution-Share Alike 
    
    If the graph is a tree this will return the positions to plot this in a 
    hierarchical layout.
    
    G: the graph (must be a tree)
    
    root: the root node of current branch 
    - if the tree is directed and this is not given, 
      the root will be found and used
    - if the tree is directed and this is given, then 
      the positions will be just for the descendants of this node.
    - if the tree is undirected and not given, 
      then a random choice will be used.
    
    width: horizontal space allocated for this branch - avoids overlap with other branches
    
    vert_gap: gap between levels of hierarchy
    
    vert_loc: vertical location of root
    
    xcenter: horizontal location of root
    '''
    if not nx.is_tree(G):
        raise TypeError('cannot use hierarchy_pos on a graph that is not a tree')

    if root is None:
        if isinstance(G, nx.DiGraph):
            root = next(iter(nx.topological_sort(G)))  #allows back compatibility with nx version 1.11
        else:
            root = random.choice(list(G.nodes))

    def _hierarchy_pos(G, root, width=1., vert_gap = 0.2, vert_loc = 0, xcenter = 0.5, pos = None, parent = None):
        '''
        see hierarchy_pos docstring for most arguments

        pos: a dict saying where all nodes go if they have been assigned
        parent: parent of this branch. - only affects it if non-directed

        '''
    
        if pos is None:
            pos = {root:(xcenter,vert_loc)}
        else:
            pos[root] = (xcenter, vert_loc)
        children = list(G.neighbors(root))
        if not isinstance(G, nx.DiGraph) and parent is not None:
            children.remove(parent)  
        if len(children)!=0:
            dx = width/len(children) 
            nextx = xcenter - width/2 - dx/2
            for child in children:
                nextx += dx
                pos = _hierarchy_pos(G,child, width = dx, vert_gap = vert_gap, 
                                    vert_loc = vert_loc-vert_gap, xcenter=nextx,
                                    pos=pos, parent = root)
        return pos

            
    return _hierarchy_pos(G, root, width, vert_gap, vert_loc, xcenter)


if __name__ == '__main__':
    import doctest
    doctest.testmod(verbose=True)

    import python_ta
    python_ta.check_all(config={
        'max-line-length': 120,
        'disable': ['E1136', 'E1101'],
        # 'extra-imports': [],
        'max-nested-blocks': 4
    })
