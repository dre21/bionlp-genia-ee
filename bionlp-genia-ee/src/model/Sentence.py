"""
Created on Sep 3, 2013

@author: Andresta
"""

class Sentence(object):
    """
    classdocs
    """


    def __init__(self, sentence_data):
        """
        Init sentence object by parsing sentence_data
        sentence_data is a list of dictionary word
        [{"pos_tag": "JJ", "start": 0, "end": 12, "string": "Differential", "stem": "Differenti"}, {...}, ... ]
        """
        if type(sentence_data) != list:
            raise TypeError("sentence_data must be a list")
        
        self.start_offset = sentence_data[0]["start"]
        self.end_offset = sentence_data[-1]["end"]
        
        self.number = -1 
        self.words = sentence_data
        self.nwords = len(sentence_data)
                
        # mapping offset to word number in a sentence
        self.offset_map = {}
        
        # mapping entity id to word number in a sentence
        # it's used when building relation from raw data
        self.entity_map = {}
        
        # list of word number which is marked as trigger candidate
        self.trigger_candidate = []
        
        # list of protein word number
        self.protein = []
        
        # list of trigger word number
        self.trigger = []
        
        # dependency
        self.dep = None
        
        # chunk
        self.chunk = None
        
        # tree
        
        # relation representation
        self.rel = None 
                
        
    def check_offset(self, offset):
        """
        return true if the given offset is in this sentence range
        """
        return offset >= self.start_offset and offset <= self.end_offset
       
    def get_string(self, start_off, nwords):
        """
        return nwords strings starting from start offset
        """
        string = ""
        word_num = self.offset_map.get(start_off,-1)        
        if word_num >= 0:
            for i in range(word_num, word_num+nwords):                
                string += self.words[i]["string"] + " "
        return string.rstrip()

    def add_relation(self, trig_type, trig_wn, arg1_wn, arg1_name, arg2_wn, arg2_name):
        """
        add relation and update word type with event name
        """
        # sanity check, whether word numbers are in range
        if trig_wn >= self.nwords or arg1_wn >= self.nwords or arg2_wn >= self.nwords:
            raise ValueError("Word number out of range")        
        
        # add into trigger list
        if trig_wn not in self.trigger:
            self.trigger.append(trig_wn)
        
        # update word type
        current_word_type = self.words[trig_wn]["type"]
        if current_word_type == 'null' or current_word_type == trig_type:
            self.words[trig_wn]["type"] = trig_type
        else:
            # TODO: log this event
            print 'reassigned word type ' + trig_type + ' to ' + current_word_type + '(' +self.words[trig_wn]['string'] + ')'
            #raise ValueError('Cannot update word type to ' +trig_type+ '! It has been assigned to ' +current_word_type)
        
        # get arg type
        arg1_type = 'P' if self.words[arg1_wn]['type'] == 'Protein' else 'E'
        arg1_tuple = (arg1_wn, arg1_name, arg1_type)
        arg2_tuple = ()
        
        if arg2_wn >= 0:
            arg2_type = 'P' if self.words[arg2_wn]['type'] == 'Protein' else 'E'
            arg2_tuple = (arg2_wn, arg2_name, arg2_type)
        
        self.rel.add_relation(trig_wn, arg1_tuple, arg2_tuple)

    '''
    def update(self, trig_wn, trig_type, arg_wn, arg_name, arg_type):
        # sanity check, whether word numbers are in range
        if trig_wn >= self.nwords or arg_wn >= self.nwords:
            raise ValueError("Word number out of range")
        
        # add into trigger list
        if trig_wn not in self.trigger:
            self.trigger.append(trig_wn)
        
        # update word type
        self.words[trig_wn]["type"] = trig_type
        
        # update relation
        self.rel.add_relation(trig_wn, arg_wn, arg_name, arg_type)
        
    def update_cause(self, trig_wn, cause_wn):
        # sanity check, whether word numbers are in range
        if trig_wn >= self.nwords or cause_wn >= self.nwords:
            raise ValueError("Word number out of range")
        
        word_type = self.words[cause_wn]["type"]
        if word_type == 'null':
            raise ValueError("Word type cannot be null. Word type for cause is either 'Protein' or Trigger type")
        elif word_type == 'Protein':
            arg_type = 'P'
        else:
            arg_type = 'E'
        
        # update relation
        self.rel.add_relation(trig_wn, cause_wn, 'Cause', arg_type)       
        
    def update_theme2(self, trig_wn, theme2_wn):
        # sanity check, whether word numbers are in range
        if trig_wn >= self.nwords or theme2_wn >= self.nwords:
            raise ValueError("Word number out of range")
        
        # delete entry on relation list        
        self.rel.delete_relation(trig_wn, theme2_wn, 'Theme', 'P')
        
        # add theme2 entry
        self.rel.add_relation(trig_wn, theme2_wn, 'Theme2', 'P')
    
    '''
    
    def test(self):
        
        print "start offset:", self.start_offset
        print "end offset:", self.end_offset
        print self.nwords, "words:"
        for w in self.words:
            print w
        print "offset map:"
        for k,v in sorted(self.offset_map.iteritems()):
            print k,v
        print "entity map:"
        for k,v in (self.entity_map.iteritems()):
            print k,v
        print "Trigger candidate:", self.trigger_candidate
        print "Protein:", self.protein
        print "Trigger:", self.trigger
        if self.dep != None:
            print "graph"
            print self.dep.graph
            print "pair"
            print self.dep.pair
        
        if self.rel != None:
            print "relation"
            print self.rel.data
        #print "get string offset 627 for 2 words"
        #print self.get_string(627, 2)
            
if __name__ == "__main__":
    
    sen = [{'pos_tag': 'JJ', 'start': 0, 'end': 12, 'string': 'Differential', 'stem': 'Differenti'}, {'pos_tag': 'NN', 'start': 13, 'end': 22, 'string': 'induction', 'stem': 'induct'}, {'pos_tag': 'IN', 'start': 23, 'end': 25, 'string': 'of', 'stem': 'of'}, {'pos_tag': 'DT', 'start': 26, 'end': 29, 'string': 'the', 'stem': 'the'}, {'pos_tag': 'NN', 'start': 30, 'end': 35, 'string': 'NF-AT', 'stem': 'NF-AT'}, {'pos_tag': 'NN', 'start': 36, 'end': 43, 'string': 'complex', 'stem': 'complex'}, {'pos_tag': 'IN', 'start': 44, 'end': 50, 'string': 'during', 'stem': 'dure'}, {'pos_tag': 'NN', 'start': 51, 'end': 64, 'string': 'restimulation', 'stem': 'restimul'}, {'pos_tag': 'CC', 'start': 65, 'end': 68, 'string': 'and', 'stem': 'and'}, {'pos_tag': 'DT', 'start': 69, 'end': 72, 'string': 'the', 'stem': 'the'}, {'pos_tag': 'NN', 'start': 73, 'end': 82, 'string': 'induction', 'stem': 'induct'}, {'pos_tag': 'IN', 'start': 83, 'end': 85, 'string': 'of', 'stem': 'of'}, {'pos_tag': 'NN', 'start': 86, 'end': 92, 'string': 'T-cell', 'stem': 'T-cell'}, {'pos_tag': 'NN', 'start': 93, 'end': 99, 'string': 'anergy', 'stem': 'anergi'}, {'pos_tag': '.', 'start': 99, 'end': 100, 'string': '.', 'stem': '.'}]
    
    S = Sentence(sen)
    S.test()