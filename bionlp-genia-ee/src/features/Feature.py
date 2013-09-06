"""
Created on Sep 6, 2013

@author: Andresta
"""

class Feature(object):
    """
    parent class for all features: Dependency, Sentence, Chunk, etc
    it provides common function
    """


    def __init__(self, prefix):
        """
        Constructor
        """
        self.prefix = prefix
        
        self.feature = {}
        
        
    def add(self, feat_name, value):
        self.feature[self.prefix +'_'+feat_name] = value
        
        
    def extract_word_feature(self, word, prefix):
        
        # pos tag of word
        self.add(prefix + "_pos_"+ word["pos_tag"], True)
        
        
        # features which are not applicable to protein 
        if word["type"] != "Protein":
            # stem of word
            self.add(prefix + '_str_'+ word['stem'], True)
        
            # trigger probability score
            self.add(prefix + '_tscore', word['score'])
            
            