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
        self.extract_word_feature(o_sen.words[arg_wn], prefix+"a",score = False)
        
        # extract word feature for words around trigger candidate
        if trig_wn - 1 >= 0:
            self.extract_word_feature(o_sen.words[trig_wn-1], prefix+"tw-1", score = False)
        if trig_wn + 1 < nword:
            self.extract_word_feature(o_sen.words[trig_wn+1], prefix+"tw+1", score = False)
            
        # extract word feature for words around protein
        if arg_wn - 1 >= 0:
            self.extract_word_feature(o_sen.words[arg_wn-1], prefix+"pw-1", score = False)
        if arg_wn + 1 < nword:
            self.extract_word_feature(o_sen.words[arg_wn+1], prefix+"pw+1", score = False)
        
    
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
        
        t_word = o_sen.words[trig_wn]
        
        # extract common feature
        self._extract_common_feature(o_sen, trig_wn, arg_wn)    
        
        # trigger base stem
        self.add('base', t_word['stem'].lower().replace('-',''))            


        # number of protein between trigger and argument
        n_prot = 0
        for p in o_sen.protein:
            if self.in_between(p, trig_wn, arg_wn):
                n_prot += 1
        self.add('n_prot', n_prot)
        
        # is adjacent
        self.add("adj", abs(trig_wn - arg_wn) == 1)

        # probability of trigger on each event
        self.add('score_1', self.get_score(t_word, 'Gene_expression'))
        self.add('score_2', self.get_score(t_word, 'Transcription'))
        self.add('score_3', self.get_score(t_word, 'Protein_catabolism'))
        self.add('score_4', self.get_score(t_word, 'Phosphorylation'))
        self.add('score_5', self.get_score(t_word, 'Localization'))
        self.add('score_6', self.get_score(t_word, 'Binding'))
        self.add('score_7', self.get_score(t_word, 'Regulation'))
        self.add('score_8', self.get_score(t_word, 'Positive_regulation'))
        self.add('score_9', self.get_score(t_word, 'Negative_regulation'))
        
    
    def extract_feature_tt(self, o_sen, trig_wn, arg_wn):
        """
        extract sentence feature 
        """       
        # reset feature
        self.feature = {}
        
        t_word = o_sen.words[trig_wn]
        
        # extract common feature
        self._extract_common_feature(o_sen, trig_wn, arg_wn)
        
        # trigger base stem
        self.add('base', t_word['stem'].lower().replace('-',''))
        
        # is adjacent
        self.add("adj", abs(trig_wn - arg_wn) == 1)
        
        # argument type
        arg_type = o_sen.words[arg_wn]["type"]
        self.add("a_type", arg_type)
        
        # probability of argument event
        self.add('arg_prob', self.get_score(o_sen.words[trig_wn], arg_type))
                
        # probability of trigger on each event
        self.add('score_7', self.get_score(t_word, 'Regulation'))
        self.add('score_8', self.get_score(t_word, 'Positive_regulation'))
        self.add('score_9', self.get_score(t_word, 'Negative_regulation'))
        
        # average probability of other event
        score = 0
        for e in self.EVENTS[0:6]:
            score += self.get_score(t_word, e)
        self.add('score0', score * 1.0 / 6)
        
    def extract_feature_tac(self, o_sen, trig_wn, theme_wn, cause_wn):
        """
        extract sentence feature for trigger-theme-cause relation
        """
        
        # reset feature
        self.feature = {}
        
        # extract common feature for trigger-theme
        self._extract_common_feature(o_sen, trig_wn, theme_wn)
        
        # extract common feature for trigger-cause
        self._extract_common_feature(o_sen, trig_wn, cause_wn, prefix='ca_')                      
        
        # type of theme
        self.add("a_type", o_sen.words[theme_wn]["type"])
        
        # type of cause
        self.add("c_type", o_sen.words[cause_wn]["type"])
        
        # type of trigger
        self.add("t_type", o_sen.words[trig_wn]["type"])
        
        # position of theme and cause
        #self.add('c_pos_bef', cause_wn < theme_wn)
        
        #position = {trig_wn:'tr', theme_wn:'th', cause_wn:'ca'}
        #self.add('pattern_'+ self.get_string_pattern(position), True)
        
        # distance between theme and cause
        #self.add('dis_ac',abs(theme_wn - cause_wn))
        
        
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
        
        #position = {trig_wn:'tr', theme1_wn:'t1', theme2_wn:'t2'}
        #self.add('pattern_'+ self.get_string_pattern(position), True)
        
        # distance between themes
        #self.add('dis_t-t',abs(theme2_wn - theme1_wn))
        
        
        
    
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
        
        
        
        
        
        