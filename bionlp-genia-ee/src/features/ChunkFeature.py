"""
Created on Sep 5, 2013

@author: Andresta
"""

from features.Feature import Feature


class ChunkFeature(Feature):
    """
    classdocs
    """


    def __init__(self, prefix):
        """
        Constructor
        """
        self.prefix = prefix
        
    
    def get_chunk_type(self, o_chunk, trig_wn, arg_wn):
        """
        return list of chunk type between trigger_wn and arg_wn
        include the type of trigger chunk and argument chunk
        """
        chk_types = []
        trig_chk_num = o_chunk.chunk_map[trig_wn]
        arg_chk_num = o_chunk.chunk_map[arg_wn]
        for chk_num in range(trig_chk_num, arg_chk_num+1):
            chk_types.append(o_chunk.chunk_type[chk_num])
        return chk_types
    
    def _extract_common_feature(self, o_sen, trig_wn, arg_wn, prefix = ''):
        """
        extract common chunk feature between trig_wn and arg_wn in o_sen
        """
        o_chunk = o_sen.chunk
        
        # chunk type of trigger and argument 
        self.add(prefix + 't_type', o_chunk.get_type(trig_wn))
        self.add(prefix + 'a_type', o_chunk.get_type(arg_wn))
        
        
        """ capture feature of events expressed in a chunk layer """
        # is in the same chunk
        self.add(prefix + 'same',o_chunk.same_chunk(trig_wn, arg_wn))
                                            
        
        """ capture feature of events expressed in a phrase layer """
        # check any preposition chunk in between trigger and argument
        if trig_wn < arg_wn:            
            chunk_types = self.get_chunk_type(o_chunk, trig_wn, arg_wn)
            self.add(prefix + 'prep', 'PP' in chunk_types)
                        
        
        """ capture feature of events expressed in a clause layer """
        # distance between chunk
        self.add(prefix + 'dist', o_chunk.distance(trig_wn, arg_wn))
        
        
        
    def extract_feature_tp(self, o_sen, trig_wn, arg_wn):
        """
        extract chunk feature between trig_wn and arg_wn in o_sen
        """       
        # reset feature
        self.feature = {}
        
        self._extract_common_feature(o_sen, trig_wn, arg_wn)
        
    def extract_feature_tt(self, o_sen, trig_wn, arg_wn):
        """
        extract chunk feature between trig_wn and arg_wn in o_sen
        """       
        # reset feature
        self.feature = {}
        
        self._extract_common_feature(o_sen, trig_wn, arg_wn)
        
        