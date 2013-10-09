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
        self.add(prefix+"dist", len(upath)-1)
        
        # number of trigger candidate between trigger and theme
        tc = o_sen.trigger_candidate
        n_tc = 0 
        for t in upath[1:-1]:
            if t in tc: n_tc+=1
        self.add('n_tc', n_tc)
        
        # edges name from trigger to argument
        edges = o_dep.get_edges_name(upath)
        self.add(prefix+self.list_to_string(edges), True) 
        
        # direct path from trigger to prot
        dpath_trg_arg = o_dep.get_shortest_path(trig_wn, arg_wn)
        dpath_arg_trig = o_dep.get_shortest_path(arg_wn, trig_wn)
        
        if dpath_trg_arg != []:
            # set type
            self.add(prefix+"type1", True)
            # edges from trigger to protein
            self.add(prefix+self.list_to_string(o_dep.get_edges_name(dpath_trg_arg)), True)
        elif dpath_arg_trig != []:
            self.add(prefix+"type2", True)
            # edges from trigger to protein
            self.add(prefix+self.list_to_string(o_dep.get_edges_name(dpath_arg_trig)), True)
        else:
            self.add(prefix+"type3", True)
            self.add(prefix+self.list_to_string(o_dep.get_edges_name(upath)), True)
            
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
        upath1 = o_dep.get_shortest_path(trig_wn, theme_wn, "undirected")
        upath2 = o_dep.get_shortest_path(trig_wn, cause_wn, "undirected")
        avg = (len(upath1) + len(upath2) - 2) * 1.0 / 2
        self.add("avg_dist", avg)
                                            
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
        upath2 = o_dep.get_shortest_path(trig_wn, theme2_wn, "undirected")
        avg = (len(upath1) + len(upath2) - 2) * 1.0 / 2
        self.add("avg_dist", avg)
        
        # cause distance between theme
        upath = o_dep.get_shortest_path(theme1_wn, theme2_wn, "undirected")
        self.add('t2_dist', len(upath)-1)
        
    def extract_feature_evt(self, o_sen, trig_wn, arg_wn):
        """
        extract dependency feature for simple event
        """        
        o_dep = o_sen.dep
                
                
        # extract word feature for parent of trigger
        trig_parent = o_dep.get_parent(trig_wn)
        if trig_parent >= 0:
            self.extract_word_feature(o_sen.words[trig_parent], "t_parent")
            
        # extract word feature for parent of argument
        arg_parent = o_dep.get_parent(arg_wn)
        if arg_parent >= 0:
            self.extract_word_feature(o_sen.words[arg_parent], "a_parent")
        
        # type of dependency
        dpath_trg_arg = o_dep.get_shortest_path(trig_wn, arg_wn)
        dpath_arg_trig = o_dep.get_shortest_path(arg_wn, trig_wn)
        upath = o_dep.get_shortest_path(trig_wn, arg_wn, "undirected")
        
        if dpath_trg_arg != []:
            # set type
            self.add("type1", True)
            # directed edges from trigger to protein
            self.add('t1-'+self.list_to_string(o_dep.get_edges_name(dpath_trg_arg)), True)
            # trigger is parent of protein 
            self.add('t1-trig-parent',trig_parent == arg_wn)
        elif dpath_arg_trig != []:
            self.add("type2", True)
            # directed edges from protein to trigger 
            self.add('t2-'+self.list_to_string(o_dep.get_edges_name(dpath_arg_trig)), True)
            # protein is parent of trigger 
            self.add('t2-arg-parent',trig_parent == arg_wn)
        else:
            self.add("type3", True)
            # undirected edges from trigger to protein
            self.add('t3-'+self.list_to_string(o_dep.get_edges_name(upath)), True)
    
        # number of trigger candidate between trigger and theme
        tc = o_sen.trigger_candidate
        n_tc = 0 
        for t in upath[1:-1]:
            if t in tc: n_tc+=1
        self.add('n_tc', n_tc)
        
        
    
    
    
    