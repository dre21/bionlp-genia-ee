"""
Created on Sep 6, 2013

@author: Andresta
"""

class SentenceFeature(object):
    """
    classdocs
    """


    def __init__(self, prefix):
        """
        Constructor
        """
        self.prefix = prefix
        
        self.feature = {}
        
    def add(self, feat_name, value):
        self.feature[self.prefix +'_'+feat_name] = value
        
        
    def extract_feature(self, o_sen, trig_wn, arg_wn):
        """
        extract sentence feature 
        """       
        # reset feature
        self.feature = {}
                
        nword = o_sen.nwords        
        
        # trigger first or last in sen
        if trig_wn == 0:
            self.add("tfirst", True)
        if trig_wn == nword:
            self.add("tlast", True)
            
        # arg first or last in sen
        if arg_wn == 0:
            self.add("afirst", True)
        if arg_wn == nword:
            self.add("alast", True)
            
        # extract word feature for trigger
        self.extract_word_feature(o_sen.words[trig_wn], "t")
        
        # extract word feature for argument
        self.extract_word_feature(o_sen.words[arg_wn], "a")
        
        # extract word feature for words around trigger candidate
        if trig_wn - 1 >= 0:
            self.extract_word_feature(o_sen.words[trig_wn-1], "tw-1")
        if trig_wn + 1 <= nword:
            self.extract_word_feature(o_sen.words[trig_wn+1], "tw+1")
            
        # extract word feature for words around protein
        if arg_wn - 1 >= 0:
            self.extract_word_feature(o_sen.words[arg_wn-1], "pw-1")
        if arg_wn + 1 <= nword:
            self.extract_word_feature(o_sen.words[arg_wn+1], "pw+1")
        
        
        
        
    def extract_word_feature(self, word, prefix):
        
        # pos tag of word
        self.add(prefix + "_pos_"+ word["pos_tag"], True)
        
        # stem of word
        # it's useless getting stem of protein, skip it 
        if word["type"] != "Protein":
            self.add(prefix + "_str_"+ word["stem"], True)
        
            # probability
        
        
        
        
        
        
        
        
        
        
        