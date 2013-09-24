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
        
        
    def _extract_common_feature(self, o_sen, trig_wn, arg_wn, prefix = ''):
        """
        extract common chunk feature between trig_wn and arg_wn in o_sen
        """
        o_chunk = o_sen.chunk
        
        """ capture feature of events expressed in a chunk layer """
        # is in the same chunk
        if o_chunk.same_chunk(trig_wn, arg_wn):
            self.add(prefix + 'same',True)
            
            # chunk type of trigger and argument 
            self.add(prefix + 'c_type', o_chunk.get_type(trig_wn))
                        
        
        """ capture feature of events expressed in a phrase layer """
        
        
        
        """ capture feature of events expressed in a clause layer """
        
        
        
        
    def extract_feature_tp(self, o_sen, trig_wn, arg_wn):
        """
        extract dependency feature between trig_wn and arg_wn in o_sen
        """       
        # reset feature
        self.feature = {}
        
        self._extract_common_feature(o_sen, trig_wn, arg_wn)
        
        
        
        