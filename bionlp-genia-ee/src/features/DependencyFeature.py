"""
Created on Sep 5, 2013

@author: Andresta
"""

from features.Feature import Feature

class DependencyFeature(Feature):
    """
    classdocs
    """


    def __init__(self, prefix):
        """
        Constructor
        """
        super(DependencyFeature, self).__init__(prefix)
                    
    def extract_feature(self, o_sen, trig_wn, arg_wn):
        """
        extract dependency feature between trig_wn and arg_wn in o_sen
        """       
        # reset feature
        self.feature = {}
        
        o_dep = o_sen.dep
        
        # length from trigger to argument
        upath = o_dep.get_shortest_path(trig_wn, arg_wn, "undirected")
        self.add("word_dist", len(upath)-1)
        
        # direct path from trigger to prot
        dpath = o_dep.get_shortest_path(trig_wn, arg_wn)
        if dpath != []:
            self.add("direct", True)
            
        # extract word feature for parent of trigger
        parent = o_dep.get_parent(trig_wn)
        if parent > 0:
            self.extract_word_feature(o_sen.words[parent], "t_parent")
            
        # extract word feature for parent of argument
        parent = o_dep.get_parent(arg_wn)
        if parent > 0:
            self.extract_word_feature(o_sen.words[parent], "a_parent")
        
        
        # extract word feature for parent of argument
        
        
        