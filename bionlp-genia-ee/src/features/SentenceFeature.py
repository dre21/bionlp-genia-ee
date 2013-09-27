"""
Created on Sep 6, 2013

@author: Andresta
"""

from features.Feature import Feature
from model.Dictionary import WordDictionary, TriggerDictionary

class SentenceFeature(Feature):
    """
    classdocs
    """


    def __init__(self, prefix, WDict, TDict):
        """
        Constructor
        """                
        if not (isinstance(WDict, WordDictionary) and isinstance(TDict,TriggerDictionary)):
            raise TypeError("Dictionary type is not match")
        
        super(SentenceFeature, self).__init__(prefix)
                
        self.wdict = WDict
        self.tdict = TDict
        
    def _extract_common_feature(self, o_sen, trig_wn, arg_wn, prefix = ''):
       
        nword = o_sen.nwords        
        
        ''' ------ position ------ '''
        # trigger first or last in sen
        self.add(prefix+"tfirst", trig_wn == 0)        
        self.add(prefix+"tlast", trig_wn == nword)
            
        # arg first or last in sen
        self.add(prefix+"afirst", arg_wn == 0)
        self.add(prefix+"alast", arg_wn == nword)
            
        # argument before trigger
        self.add(prefix+"a_bef_t", arg_wn < trig_wn)
            
        # word distance trigger to argument
        self.add(prefix+"dist", abs(trig_wn - arg_wn))
        
        
        ''' ------ word feature ------ '''
        # extract word feature for trigger
        self.extract_word_feature(o_sen.words[trig_wn], prefix+"t")
        
        # extract word feature for argument
        self.extract_word_feature(o_sen.words[arg_wn], prefix+"a")
        
        # extract word feature for words around trigger candidate
        if trig_wn - 1 >= 0:
            self.extract_word_feature(o_sen.words[trig_wn-1], prefix+"tw-1")
        if trig_wn + 1 < nword:
            self.extract_word_feature(o_sen.words[trig_wn+1], prefix+"tw+1")
            
        # extract word feature for words around protein
        if arg_wn - 1 >= 0:
            self.extract_word_feature(o_sen.words[arg_wn-1], prefix+"pw-1")
        if arg_wn + 1 < nword:
            self.extract_word_feature(o_sen.words[arg_wn+1], prefix+"pw+1")
        
    
    def in_between(self, i, trig_wn, arg_wn):
        if trig_wn > arg_wn:
            start = arg_wn
            end = trig_wn
        else:
            start = trig_wn
            end = arg_wn
        
        if i > start and i < end:
            return True
        else:
            return False
          
    def extract_feature_tp(self, o_sen, trig_wn, arg_wn):
        """
        extract sentence feature 
        """       
        # reset feature
        self.feature = {}
        
        # extract common feature
        self._extract_common_feature(o_sen, trig_wn, arg_wn)                


        # number of protein between trigger and argument
        n_prot = 0
        for p in o_sen.protein:
            if self.in_between(p, trig_wn, arg_wn):
                n_prot += 1
        self.add('n_prot', n_prot)
        
        # is adjacent
        self.add("adj", abs(trig_wn - arg_wn) == 1)

        # probability of trigger on each event
        self.add('score_1', self.get_score(o_sen.words[trig_wn], 'Gene_expression'))
        self.add('score_2', self.get_score(o_sen.words[trig_wn], 'Transcription'))
        self.add('score_3', self.get_score(o_sen.words[trig_wn], 'Protein_catabolism'))
        self.add('score_4', self.get_score(o_sen.words[trig_wn], 'Phosphorylation'))
        self.add('score_5', self.get_score(o_sen.words[trig_wn], 'Localization'))
        self.add('score_6', self.get_score(o_sen.words[trig_wn], 'Binding'))
        self.add('score_7', self.get_score(o_sen.words[trig_wn], 'Regulation'))
        self.add('score_8', self.get_score(o_sen.words[trig_wn], 'Positive_regulation'))
        self.add('score_9', self.get_score(o_sen.words[trig_wn], 'Negative_regulation'))
        
    
    def extract_feature_tt(self, o_sen, trig_wn, arg_wn):
        """
        extract sentence feature 
        """       
        # reset feature
        self.feature = {}
        
        # extract common feature
        self._extract_common_feature(o_sen, trig_wn, arg_wn)
        
        # is adjacent
        self.add("adj", abs(trig_wn - arg_wn) == 1)
        
        # argument type
        arg_type = o_sen.words[arg_wn]["type"]
        self.add("a_type", arg_type)
        
        # probability of argument event
        self.add('arg_prob', self.get_score(o_sen.words[trig_wn], arg_type))
                
        # probability of trigger on each event
        self.add('score_7', self.get_score(o_sen.words[trig_wn], 'Regulation'))
        self.add('score_8', self.get_score(o_sen.words[trig_wn], 'Positive_regulation'))
        self.add('score_9', self.get_score(o_sen.words[trig_wn], 'Negative_regulation'))
        
    def extract_feature_tac(self, o_sen, trig_wn, theme_wn, cause_wn):
        """
        extract sentence feature for trigger-theme-cause relation
        """
        
        # reset feature
        self.feature = {}
        
        # extract common feature for trigger-theme
        self._extract_common_feature(o_sen, trig_wn, theme_wn, prefix='th_')
        
        # extract common feature for trigger-cause
        self._extract_common_feature(o_sen, trig_wn, cause_wn, prefix='ca_')                      
        
        # type of theme
        self.add("a_type", o_sen.words[theme_wn]["type"])
        
        # type of cause
        self.add("c_type", o_sen.words[cause_wn]["type"])
        
        # type of trigger
        self.add("t_type", o_sen.words[trig_wn]["type"])
        
        # position of theme and cause
        self.add('c_pos_bef', cause_wn < theme_wn)
        
        # distance between theme and cause
        self.add('dis_ac',abs(theme_wn - cause_wn))
        
        
    def extract_feature_t2(self, o_sen, trig_wn, theme1_wn, theme2_wn):
        """
        extract sentence feature for trigger-theme1-theme2 relation
        """
        # reset feature
        self.feature = {}
        
        # extract common feature trigger-theme1
        self._extract_common_feature(o_sen, trig_wn, theme1_wn, prefix='t1_')
        
        # extract common feature trigger-theme2
        self._extract_common_feature(o_sen, trig_wn, theme2_wn, prefix='t2_')
        
        # redundant
        # position of theme1 relative to trigger, is it left of trigger?
        #self.add('t1_l', theme1_wn < trig_wn)
        # position of theme2 relative to trigger, is it left of trigger?
        #self.add('t2_l', theme2_wn < trig_wn)
        
        # distance between themes
        self.add('dis_t-t',abs(theme2_wn - theme1_wn))
        
        
        
    
    def get_score(self, word, event_type):
        """
        calculate the probability score of trigger candidate for given event_type
        """
        retval = 0.0
        string = word["string"]
        w = self.wdict.count(string)
        if w != 0:
            retval = self.tdict.count(string, event_type) * 1.0 / w
        return retval
        
        
        
        
        
        