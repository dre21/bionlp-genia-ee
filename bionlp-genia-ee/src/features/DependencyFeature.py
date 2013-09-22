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
        
    def list_to_string(self, string_list):
        string = ""
        for s in string_list:
            string += s + '-'
        return string.rstrip('-') 
                    
    def _extract_common_feature(self, o_sen, trig_wn, arg_wn):
                
        o_dep = o_sen.dep
        
        # length from trigger to argument
        upath = o_dep.get_shortest_path(trig_wn, arg_wn, "undirected")
        self.add("word_dist", len(upath)-1)
        
        # edges name from trigger to argument
        edges = o_dep.get_edges_name(upath)
        self.add(self.list_to_string(edges), True) 
        
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
        
        
        # extract word feature for child of trigger
        children = o_dep.get_child(trig_wn)
        if children != []:
            for child in children:
                self.extract_word_feature(o_sen.words[child], "t_child")
                
        # extract word feature for child of argument
        children = o_dep.get_child(arg_wn)
        if children != []:
            for child in children:
                self.extract_word_feature(o_sen.words[child], "a_child")
                
    def extract_feature_tp(self, o_sen, trig_wn, arg_wn):
        """
        extract dependency feature between trig_wn and arg_wn in o_sen
        """       
        # reset feature
        self.feature = {}
        
        self._extract_common_feature(o_sen, trig_wn, arg_wn)
    
    def extract_feature_tt(self, o_sen, trig_wn, arg_wn):
        """
        extract dependency feature between trig_wn and arg_wn in o_sen
        """       
        # reset feature
        self.feature = {}
        
        self._extract_common_feature(o_sen, trig_wn, arg_wn)
        
        o_dep = o_sen.dep
        
        # number of trigger candidate between trig_wn and arg_wn
        upath = o_dep.get_shortest_path(trig_wn, arg_wn, "undirected")
        tc = o_sen.trigger_candidate
        n_tc = 0 
        for t in upath[1:-1]:
            if t in tc: n_tc+=1
        self.add('n_tc', n_tc)
    
    def extract_feature_tac(self, o_sen, trig_wn, theme_wn, cause_wn):
        """
        extract dependency feature for trigger-theme-cause relation
        """
        # reset feature
        self.feature = {}
        
        o_dep = o_sen.dep
        
        
        # dependency distance trigger to theme
        upath = o_dep.get_shortest_path(trig_wn, theme_wn, "undirected")
        self.add("dis_ta", len(upath)-1)
        
        upath = o_dep.get_shortest_path(trig_wn, cause_wn, "undirected")
        # dependency distance trigger to cause
        # use key 'word_dist' to be processed by filter
        self.add("word_dist", len(upath)-1)
        
        
        # path from trigger to theme
        dpath = o_dep.get_shortest_path(trig_wn, theme_wn)
        if dpath != []:
            self.add("path_ta", True)
        
        # path from trigger to cause    
        dpath = o_dep.get_shortest_path(trig_wn, cause_wn)
        if dpath != []:
            self.add("path_tc", True)
            
        # path from theme to cause    
        dpath = o_dep.get_shortest_path(theme_wn, cause_wn)
        if dpath != []:
            self.add("path_ac", True)
            
        # path from cause to theme    
        dpath = o_dep.get_shortest_path(cause_wn, theme_wn)
        if dpath != []:
            self.add("path_ca", True)
        
        
     
    
        
        
    
    
    
    
    
    
    
    