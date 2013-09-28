"""
Created on Sep 3, 2013

@author: Andresta
"""

from collections import defaultdict

class Dependency(object):
    """
    classdocs
    """


    def __init__(self, dependency_data):
        """
        Init a sentence dependency object by parsing dependency_data
        dependency_data is a dictionary
        {'root': '2', 'data': {'11': [('10', 'det'), ('12', 'prep')], 'xx' : [] } }
        """
        if type(dependency_data) != dict:
            raise TypeError("dependency_data must be a dictionary")
        
        self.root = int(dependency_data["root"]) - 1
        
        # simple dict-list style graph representation    
        # this graph stores directed graph representation  
        self.graph = {}
        
        # simple dict-list style graph representation    
        # this graph stores undirected graph representation
        self.u_graph = {}
        
        # gov-dep pair type representation using dictionary
        # order does not matter gov-dep or dep-gov,        
        self.pair = {}
        
        self.set_graph_pair(dependency_data["data"])
                        
    def set_graph_pair(self, dependency_data): 
        """
        set directed and undirected graph, using simple dict-list style graph representation 
        and pair of gov-dep type representation using dictionary
        from a given dependency_data
        
        graph = {'A': ['B', 'C'],
                 'B': ['C', 'D'],
                 'C': ['D'], ... }
        
        pair = {[11,10] : 'det',
                [11,12] : 'prep', ... }
        
        dep = {'11': [('10', 'det'), ('12', 'prep')], '3': [('6', 'pobj')], ... }
        """
        graph = defaultdict(list)
        u_graph = defaultdict(list)
        pair = {}
        for k,lst in dependency_data.iteritems():
            for v in lst:
                d = v[0]
                gov = int(k) - 1
                dep = int(d) - 1
                # add to graph
                graph[gov].append(dep)
                
                # add to undirected graph
                u_graph[gov].append(dep)
                u_graph[dep].append(gov)
                
                # add pair information
                pair[tuple(sorted([gov,dep]))] = v[1]
        
        self.graph = graph
        self.u_graph = u_graph
        self.pair = pair
        
    def get_shortest_path(self, start, end, graph_type = "directed", path=[]):
        """
        return shortest path from start to end, empty list if no path found
        graphtype is either directed or undirected        
        """
        if graph_type.lower() == "directed":
            graph = self.graph
        elif graph_type.lower() == "undirected":
            graph = self.u_graph
        else:
            raise ValueError("graph_type is either directed or undirected")
        
        path = path + [start]
        if start == end:
            return path
        if not graph.has_key(start):
            return []
        shorthest = []
        for node in graph[start]:
            if node not in path:
                newpath = self.get_shortest_path(node, end, graph_type, path)
                if newpath:
                    if not shorthest or len(newpath) < len(shorthest):
                        shorthest = newpath
        return shorthest       
                    
    def get_parent(self, node):
        """ 
        get parent of given node
        return -1 if parent is not found (word is a root)
        """        
        if node == self.root:
            parent = -1
        else:
            for k, v in self.graph.iteritems():
                if node in v:
                    parent = k
                    break
        return parent
            
    def get_child(self, node):
        """
        return list of children nodes for a given node,
        empty list if no children
        """
        return self.graph.get(node,[])
          
    def get_edges_name(self, path):        
        if len(path) < 2: return []
        
        edges = []
        for i in range(0, len(path)-1):
            gov = path[i]
            dep = path[i+1]
            pair = tuple(sorted([gov,dep]))
            edge = self.pair[pair]
            edges.append(edge)
        
        return edges
    
    def get_head(self, wn_tuple):
        """
        return head of a given wn_tuple
        """
        if type(wn_tuple) == tuple:
            temp_head = []
            for gov in self.graph.iterkeys():
                for wn in wn_tuple:
                    if wn == gov: temp_head.append(wn)  
            if len(temp_head) > 0:     
                head = sorted(temp_head)[0]
            else:
                # if all wn in tuple are dependence
                # choose the first word in tuple
                head = wn_tuple[0]
            
        else: 
            head = wn_tuple
        
        
        
        return head
                    
    def test(self):
        print "root", self.root
        
        print "Print graph"
        for k,v in self.graph.iteritems():
            print k,v
            
        print "Print undirected graph"
        for k,v in self.u_graph.iteritems():
            print k,v
        
        print "Print pair"
        for k,v in self.pair.iteritems():
            print k,v


if __name__ == "__main__":
        
    dep_sen = {'root': '3', 'data': {'11': [('10', 'nn'), ('12', 'prep')], '12': [('13', 'pobj')], '20': [('18', 'amod'), ('19', 'nn')], '14': [('16', 'pobj')], '17': [('20', 'pobj')], '16': [('15', 'det'), ('17', 'prep')], '3': [('1', 'nsubj'), ('2', 'advmod'), ('7', 'ccomp'), ('21', 'punct')], '7': [('4', 'complm'), ('5', 'nsubj'), ('6', 'cop'), ('9', 'xcomp')], '9': [('8', 'aux'), ('11', 'dobj'), ('14', 'prep')]}, 'nword': 21}
    
    Dep = Dependency(dep_sen)
    Dep.test()    
    path = Dep.get_shortest_path(8, 4)
    upath = Dep.get_shortest_path(8, 4, "undirected")
    print "path 8->4", path
    print "edges 8->4", Dep.get_edges_name(path)
    print "undirected path 8->4", upath
    print "undirected edges 8->4", Dep.get_edges_name(upath)
    print "parent 11", Dep.get_parent(11)
    print "parent 3", Dep.get_parent(3)    
    