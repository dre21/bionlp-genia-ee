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
        super(ChunkFeature, self).__init__(prefix)                
           
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
        
        """ capture feature of events expressed in a chunk layer """
        # is in the same chunk
        if o_chunk.same_chunk(trig_wn, arg_wn):            
            self.add(prefix+'l_chk',True)
            self.add(prefix+o_chunk.get_type(trig_wn), True)
            self.add(prefix+'dist',0)
                                            
        else:
            """ capture feature of events expressed in a phrase or clause layer """
            # check any preposition chunk in between trigger and argument    
            if trig_wn < arg_wn:
                preps = self.get_prep_word(o_sen, trig_wn, arg_wn)
                if len(preps) == 1:
                    # prep must be next chunk of trigger
                    trig_cn = o_sen.chunk.chunk_map[trig_wn]
                    prep_cn = o_sen.chunk.chunk_map[preps[0][1]]
                    if trig_cn + 1 == prep_cn:
                        self.add(prefix+'l_prep', True)
                        self.add(prefix+'prep_'+preps[0][0], True)
                    else:
                        self.add(prefix+'l_clause', True)
                         
            # distance between chunk using dependency
            upath = o_dep.get_shortest_path(trig_wn, arg_wn, "undirected")
            chunk_nums = []
            for node in upath:
                chunk_nums.append(o_chunk.chunk_map[node])                
            self.add(prefix+'dist', len(set(chunk_nums))-1)
                  
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
        self._extract_common_feature(o_sen, trig_wn, theme_wn, prefix='a_')
        self._extract_common_feature(o_sen, trig_wn, cause_wn, prefix='c_')
        self._extract_common_feature(o_sen, theme_wn, cause_wn, prefix='ac')
               
    def extract_feature_t2(self, o_sen, trig_wn, theme1_wn, theme2_wn):
        """
        extract chunk feature for trigger-theme1-theme2 relation
        """
        # reset feature
        self.feature = {}
                        
        # extract common feature
        self._extract_common_feature(o_sen, trig_wn, theme1_wn, prefix='t1_')
        self._extract_common_feature(o_sen, trig_wn, theme2_wn, prefix='t2_')
        self._extract_common_feature(o_sen, theme1_wn, theme2_wn, prefix='t12_')
        
    def extract_feature_evt(self, o_sen, trig_wn, arg_wn):
        """ 
        extract chunk feature for simple event
        """
        # reset feature
        self.feature = {}
        
        self._extract_common_feature(o_sen, trig_wn, arg_wn)
        
        
    def extract_feature_bnd(self, o_sen, trig_wn, arg1_wn, arg2_wn = -1):
        """
        extract dependency feature for binding event
        """        
        # reset feature
        self.feature = {}
        
        o_chunk = o_sen.chunk
        
        self._extract_common_feature(o_sen, trig_wn, arg1_wn)
        if arg2_wn != -1:
            
            self._extract_common_feature(o_sen, trig_wn, arg2_wn, 'th2')
        
            # arg 1 and 2 in same chunk
            self.add('arg_1chk', o_chunk.same_chunk(arg1_wn, arg2_wn))
            
            # preposition between arguments
            preps = self.get_prep_word(o_sen, arg1_wn, arg2_wn)
            for prep in preps:
                self.add('prep_'+prep[0], True)
            
            
    def extract_feature_reg(self, o_sen, trig_wn, arg1_wn, arg2_wn):
        """
        extract feature for regulation relation
        """ 
        # reset feature
        self.feature = {}
        
        self._extract_common_feature(o_sen, trig_wn, arg1_wn)
        if arg2_wn != -1:            
            self._extract_common_feature(o_sen, trig_wn, arg2_wn, 'th2')
            
            # preposition between arguments
            preps = self.get_prep_word(o_sen, arg1_wn, arg2_wn)
            for prep in preps:
                self.add('prep_'+prep[0], True)
        