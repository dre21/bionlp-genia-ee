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
        
           
    def get_prep_word(self, o_sen, wn1, wn2):
        """
        return tuple of prepositions (string,word_number)                
        """
        o_chunk = o_sen.chunk
        preps_word = []
        wn1_chk_num = o_chunk.chunk_map[wn1]
        wn2_chk_num = o_chunk.chunk_map[wn2]
        for chk_num in range(wn1_chk_num+1, wn2_chk_num):
            prep = o_chunk.prep_chunk.get(chk_num,None)
            if prep != None:
                preps_word.append(prep)                
        
        return preps_word
        
    
    def _extract_common_feature(self, o_sen, trig_wn, arg_wn, prefix = ''):
        """
        extract common chunk feature between trig_wn and arg_wn in o_sen
        """
        o_chunk = o_sen.chunk
        o_dep = o_sen.dep        
        is_clause = True
                
        """ capture feature of events expressed in a chunk layer """
        # is in the same chunk
        if o_chunk.same_chunk(trig_wn, arg_wn):            
            self.add(prefix + 'chk',True)
            self.add(prefix + o_chunk.get_type(trig_wn), True)
            self.add(prefix + 'dist', 0)
                                            
        else:
            """ capture feature of events expressed in a phrase and clause layer """
            # check any preposition chunk in between trigger and argument
            if trig_wn < arg_wn:                
                preps = self.get_prep_word(o_sen, trig_wn, arg_wn)
                if len(preps) == 1:
                    # prep is tuple (preposition_string, word_number)
                    prep = preps[0]
                    # preposition must be next chunk of trigger
                    trig_cn = o_chunk.chunk_map[trig_wn]
                    prep_cn = o_chunk.chunk_map[prep[1]]
                    if trig_cn + 1 == prep_cn:
                        self.add(prefix + 'prep',True)
                        self.add(prefix + 'p_'+ prep[0], True)
                        is_clause = False                                            
                                
            if is_clause:
                self.add(prefix + 'clause',True)
            
            # set distance
            upath = o_dep.get_shortest_path(trig_wn, arg_wn, "undirected")
            chunk_nums = []
            for node in upath:
                chunk_nums.append(o_chunk.chunk_map[node])
            self.add(prefix + 'dist', len(set(chunk_nums)) - 1)
                                       
        
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
        
        o_chk = o_sen.chunk
        
        # extract common feature
        self._extract_common_feature(o_sen, trig_wn, theme_wn)
        self._extract_common_feature(o_sen, trig_wn, cause_wn, prefix='c_')
        
        # arg1 and arg2 in same chunk?
        args_same_chk = o_chk.same_chunk(theme_wn, cause_wn)
        
        # distance between chunk
        if args_same_chk:
            self.add('arg_1chk', True)
            self.add('arg_dist', 0)
        else:
            upath = o_sen.dep.get_shortest_path(theme_wn, cause_wn, "undirected")
            chunk_nums = []
            for node in upath:
                chunk_nums.append(o_chk.chunk_map[node])
            self.add('arg_dist', len(set(chunk_nums)) - 1)
        
        #self._extract_common_feature(o_sen, theme_wn, cause_wn, prefix='ac')
        
        
    def extract_feature_t2(self, o_sen, trig_wn, theme1_wn, theme2_wn):
        """
        extract chunk feature for trigger-theme1-theme2 relation
        """
        # reset feature
        self.feature = {}
        
        o_chk = o_sen.chunk
                        
        # extract common feature
        self._extract_common_feature(o_sen, trig_wn, theme1_wn)
        self._extract_common_feature(o_sen, trig_wn, theme2_wn, prefix='t2_')
        
        # arg1 and arg2 in same chunk?
        args_same_chk = o_chk.same_chunk(theme1_wn, theme2_wn)
        
        # distance between chunk
        if args_same_chk:
            self.add('arg_1chk', True)
            self.add('arg_dist', 0)
        else:        
            # set distance
            upath = o_sen.dep.get_shortest_path(theme1_wn, theme2_wn, "undirected")
            chunk_nums = []
            for node in upath:
                chunk_nums.append(o_chk.chunk_map[node])
            self.add('arg_dist', len(set(chunk_nums)) - 1)
        
        # preposition between argument
        preps = self.get_prep_word(o_sen, theme1_wn, theme2_wn)
        for prep in preps:
            # add prep. prep is tupple (preposition_string, word_number)
            self.add('arg_prep_'+prep[0], True)
        
        #self._extract_common_feature(o_sen, theme1_wn, theme2_wn, prefix='t12_')
        
        
        
        