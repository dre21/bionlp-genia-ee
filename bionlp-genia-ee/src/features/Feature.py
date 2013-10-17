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

    EVENTS = ['Gene_expression', 'Transcription', 'Protein_catabolism', 'Phosphorylation', 'Localization',
              'Binding', 'Regulation','Positive_regulation','Negative_regulation']

    def __init__(self, prefix):
        """
        Constructor
        """
        self.prefix = prefix
        
        self.feature = {}
        
        
    def add(self, feat_name, value):
        self.feature[self.prefix +'_'+feat_name] = value
        
    def get_string_pattern(self, position):
        string = ''
        for _, node in sorted(position.iteritems()):
            string += node + '-' 
        return string.rstrip('-')
        
    def extract_word_feature(self, word, prefix, score = True):
        
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
        if score:
            self.add(prefix + '_tscore', word['score'])
        
        #self.add(prefix + 'tc', word['score'] > 0.02)
            
        
            