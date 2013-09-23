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
                    
    def _extract_common_feature(self, o_sen, trig_wn, arg_wn, prefix = ''):
                
        o_dep = o_sen.dep
        
        # length from trigger to argument
        upath = o_dep.get_shortest_path(trig_wn, arg_wn, "undirected")
        self.add(prefix+"word_dist", len(upath)-1)
        
        # edges name from trigger to argument
        edges = o_dep.get_edges_name(upath)
        self.add(prefix+self.list_to_string(edges), True) 
        
        # direct path from trigger to prot
        dpath = o_dep.get_shortest_path(trig_wn, arg_wn)
        if dpath != []:
            self.add(prefix+"direct", True)
            
        # extract word feature for parent of trigger
        parent = o_dep.get_parent(trig_wn)
        if parent > 0:
            self.extract_word_feature(o_sen.words[parent], prefix+"t_parent")
            
        # extract word feature for parent of argument
        parent = o_dep.get_parent(arg_wn)
        if parent > 0:
            self.extract_word_feature(o_sen.words[parent], prefix+"a_parent")
        
        
        # extract word feature for child of trigger
        children = o_dep.get_child(trig_wn)
        if children != []:
            for child in children:
                self.extract_word_feature(o_sen.words[child], prefix+"t_child")
                
        # extract word feature for child of argument
        children = o_dep.get_child(arg_wn)
        if children != []:
            for child in children:
                self.extract_word_feature(o_sen.words[child], prefix+"a_child")
                
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
        
        
        # extract common feature trigger-theme
        self._extract_common_feature(o_sen, trig_wn, theme_wn, prefix='t_')
        
        # extract common feature trigger-cause
        self._extract_common_feature(o_sen, trig_wn, cause_wn, prefix='c_')
                
        # average length from trigger to theme and cause
        # use key "word_dist" to be worked with filter
        upath1 = o_dep.get_shortest_path(trig_wn, theme_wn, "undirected")
        upath2 = o_dep.get_shortest_path(trig_wn, cause_wn, "undirected")
        avg = (len(upath1) + len(upath2) - 2) * 1.0 / 2
        self.add("word_dist", avg)
                                            
        # cause theme distance
        upath = o_dep.get_shortest_path(theme_wn, cause_wn, "undirected")
        self.add('tc_dist', len(upath)-1)
                                                            
        # direct path from theme to cause    
        dpath = o_dep.get_shortest_path(theme_wn, cause_wn)
        if dpath != []:
            self.add("path_ac", True)
            
        # direct path from cause to theme    
        dpath = o_dep.get_shortest_path(cause_wn, theme_wn)
        if dpath != []:
            self.add("path_ca", True)
        
        
        # number of trigger candidate between theme and cause
        tc = o_sen.trigger_candidate
        n_tc = 0 
        for t in upath[1:-1]:
            if t in tc: n_tc+=1
        self.add('n_tc', n_tc)
        
        # number of protein between theme and cause
        prots = o_sen.protein
        n_prot = 0
        for p in upath[1:-1]:
            if p in prots: n_prot+=1
        self.add('n_pr', n_prot)
        
        
        
    def extract_feature_t2(self, o_sen, trig_wn, theme1_wn, theme2_wn):
        """
        extract dependency feature for trigger-theme1-theme2 relation
        """
        # reset feature
        self.feature = {}
         
        # extract common feature trigger-theme1
        self._extract_common_feature(o_sen, trig_wn, theme1_wn, prefix='t1_')
        
        # extract common feature trigger-theme2
        self._extract_common_feature(o_sen, trig_wn, theme2_wn, prefix='t2_')
        
        
        o_dep = o_sen.dep
        
        # average length from trigger to theme1-theme2
        # use key "word_dist" to be worked with filter
        upath1 = o_dep.get_shortest_path(trig_wn, theme1_wn, "undirected")
        upath2 = o_dep.get_shortest_path(trig_wn, theme1_wn, "undirected")
        avg = (len(upath1) + len(upath2) - 2) * 1.0 / 2
        self.add("word_dist", avg)
        
        
        
    
    
    
    
    
    
    