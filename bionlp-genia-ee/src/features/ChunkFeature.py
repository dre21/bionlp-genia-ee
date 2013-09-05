"""
Created on Sep 5, 2013

@author: Andresta
"""

class ChunkFeature(object):
    """
    classdocs
    """


    def __init__(self, prefix):
        """
        Constructor
        """
        self.prefix = prefix
        
        
    def extract_feature(self, o_sen, trig_wn, arg_wn):
        """
        extract chunk feature between trig_wn and arg_wn in o_sen
        return dictionary of feature-value pair
        """