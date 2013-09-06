"""
Created on Sep 5, 2013

@author: Andresta
"""

class DependencyFeature(object):
    """
    classdocs
    """


    def __init__(self, prefix):
        """
        Constructor
        """
        self.prefix = prefix
        
        self.feature = {}
        
    def add(self, feat_name, value):
        self.feature[self.prefix +'_'+feat_name] = value
        
    def extract_feature(self, o_sen, trig_wn, arg_wn):
        """
        extract dependency feature between trig_wn and arg_wn in o_sen
        """       
        # reset feature
        self.feature = {}
        
        o_dep = o_sen.dep
        
        # length from trigger to argument
        upath = o_dep.get_shortest_path(trig_wn, arg_wn, "undirected")
        self.add("wordlen", len(upath)-1)
        
        # direct path from trigger to prot
        dpath = o_dep.get_shortest_path(trig_wn, arg_wn)
        if dpath != []:
            self.add("direct", True)
        
        
        
    def extract_word_feature(self, word, prefix):
        
        # pos tag of word
        self.add(prefix + "_pos_"+ word["pos_tag"], True)
        
        # stem of word
        self.add(prefix + "_pos_"+ word["stem"], True)
        