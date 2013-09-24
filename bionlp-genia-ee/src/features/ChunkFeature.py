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
    
    def get_prep_word(self, o_sen, trig_wn, arg_wn):
        """
        return list of preposition word        
        """
        o_chunk = o_sen.chunk
        prep_word = []
        
        trig_chk_num = o_chunk.chunk_map[trig_wn]
        arg_chk_num = o_chunk.chunk_map[arg_wn]
        for chk_num in range(trig_chk_num+1, arg_chk_num):
            word_num = o_chunk.prep_chunk.get(chk_num,-1)
            if word_num >= 0:
                word = o_sen.words[word_num]
                prep_word.append(word['string'])
        return prep_word
        
    
    def _extract_common_feature(self, o_sen, trig_wn, arg_wn, prefix = ''):
        """
        extract common chunk feature between trig_wn and arg_wn in o_sen
        """
        o_chunk = o_sen.chunk
        
        # chunk type of trigger and argument 
        self.add(prefix + 't_type_'+o_chunk.get_type(trig_wn), True)
        self.add(prefix + 'a_type_'+o_chunk.get_type(arg_wn), True)
        
        
        """ capture feature of events expressed in a chunk layer """
        # is in the same chunk
        self.add(prefix + 'same',o_chunk.same_chunk(trig_wn, arg_wn))
                                            
        
        """ capture feature of events expressed in a phrase layer """
        # check any preposition chunk in between trigger and argument
        n_prep_words = 0
        if trig_wn < arg_wn:            
            prep_words = self.get_prep_word(o_sen, trig_wn, arg_wn)
            n_prep_words = len(prep_words)
            for p in prep_words:
                self.add(prefix+'p_'+p, True)
            
        self.add(prefix + 'n_prep',n_prep_words)
                        
        
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
        
    def extract_feature_tac(self, o_sen, trig_wn, theme_wn, cause_wn):
        """
        extract chunk feature for trigger-theme-cause relation
        """
        # reset feature
        self.feature = {}
        
        # extract common feature
        self._extract_common_feature(o_sen, trig_wn, theme_wn, prefix='t_')
        self._extract_common_feature(o_sen, trig_wn, cause_wn, prefix='c_')
        
    def extract_feature_t2(self, o_sen, trig_wn, theme1_wn, theme2_wn):
        """
        extract chunk feature for trigger-theme1-theme2 relation
        """
        # reset feature
        self.feature = {}
        
        o_chunk = o_sen.chunk
        
        # extract common feature
        self._extract_common_feature(o_sen, trig_wn, theme1_wn, prefix='t1_')
        self._extract_common_feature(o_sen, trig_wn, theme2_wn, prefix='t2_')
        
        # theme1 and theme2 in same chunk
        self.add('t2_same', o_chunk.same_chunk(theme1_wn, theme2_wn))
        
        # dist in chunk between argument
        self.add('t2_dis', o_chunk.distance(theme1_wn, theme2_wn))
        
        