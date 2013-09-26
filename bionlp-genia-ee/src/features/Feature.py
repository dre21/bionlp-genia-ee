"""
Created on Sep 6, 2013

@author: Andresta
"""
import re

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
                
        # word stem
        stem = 'PRO' if  word["type"] == "Protein" else word['string']                    
        self.add(prefix + '_stem_'+ stem, True)
        
        # string after pruning '-' and '/'
        #string = 'PRO' if  word["type"] == "Protein" else word['string']
        #string = re.sub('\-|\/','',string)
        #self.add(prefix + '_str_'+ stem, True)
                
        # trigger probability score
        self.add(prefix + '_tscore', word['score'])
            
            