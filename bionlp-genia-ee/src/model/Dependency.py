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
        
        self.root = int(dependency_data["root"])
        
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
                gov = int(k)
                dep = int(d)
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
            return None
        shorthest = None
        for node in graph[start]:
            if node not in path:
                newpath = self.get_shortest_path(node, end, graph_type, path)
                if newpath:
                    if not shorthest or len(newpath) < len(shorthest):
                        shorthest = newpath
        return shorthest       
                    
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
    path = Dep.get_shortest_path(9, 5)
    upath = Dep.get_shortest_path(9, 5, "undirected")
    print "path 9->5", path
    print "undirected path 9->5", upath
        
    