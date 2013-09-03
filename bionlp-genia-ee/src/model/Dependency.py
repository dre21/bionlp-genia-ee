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
        self.graph = {}
        
        # gov-dep pair type representation using dictionary
        self.pair = {}
        
        self.set_graph_pair(dependency_data["data"])
        
        
        
    def set_graph_pair(self, dep): 
        """
        set graph, a simple dict-list style graph representation 
        and pair, gov-dep type representation using dictionary
        from a given dep
        
        graph = {'A': ['B', 'C'],
                 'B': ['C', 'D'],
                 'C': ['D'], ... }
        
        pair = {'11-10' : 'det',
                '11-12' : 'prep', ... }
        
        dep = {'11': [('10', 'det'), ('12', 'prep')], '3': [('6', 'pobj')], ... }
        """
        graph = defaultdict(list)
        pair = {}
        for k,lst in dep.iteritems():
            for v in lst:
                d = v[0]
                graph[int(k)].append(int(d))
                pair[k+"-"+d] = v[1]
        
        self.graph = graph
        self.pair = pair
        
    def test(self):
        print "root", self.root
        
        print "Print graph"
        for k,v in self.graph.iteritems():
            print k,v
        
        print "Print pair"
        for k,v in self.pair.iteritems():
            print k,v
            

if __name__ == "__main__":
        
    dep_sen = {'root': '20', 'data': {'27': [('25', 'det'), ('26', 'amod'), ('28', 'prep'), ('33', 'rcmod')], '21': [('23', 'pobj')], '24': [('27', 'pobj')], '10': [('8', 'det'), ('9', 'nn'), ('12', 'appos')], '12': [('11', 'punct'), ('13', 'punct')], '20': [('1', 'nsubj'), ('21', 'prep'), ('35', 'punct')], '14': [('16', 'pobj')], '17': [('19', 'pobj')], '16': [('15', 'amod'), ('17', 'prep')], '19': [('18', 'amod')], '23': [('22', 'det'), ('24', 'prep')], '28': [('29', 'pobj')], '1': [('2', 'prep'), ('7', 'prep'), ('14', 'prep')], '33': [('30', 'nsubjpass'), ('31', 'aux'), ('32', 'auxpass'), ('34', 'xcomp')], '2': [('6', 'pobj')], '7': [('10', 'pobj')], '6': [('3', 'amod'), ('4', 'nn'), ('5', 'nn')]}, 'nword': 35}
    
    Dep = Dependency(dep_sen)
    Dep.test()    
        
    