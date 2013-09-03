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
        
        self.words = sentence_data
        self.nwords = len(sentence_data)
                
        # mapping offset to word number in a sentence
        self.offset_map = self.map(sentence_data)
        
    def check_offset(self, offset):
        """
        return true if the given offset is in this sentence range
        """
        return offset >= self.start_offset and offset <= self.end_offset
    
    def map(self, words):
        """
        return mapping of start offset to word number
        """
        retval = {}
        for i in range(0, len(words)):
            word = words[i]
            retval[word["start"]] = i
        return retval
        
    def test(self):
        
        print "start offset:", self.start_offset
        print "end offset:", self.end_offset
        print self.nwords, "words:"
        for w in self.words:
            print w
        print "map:"
        for k,v in sorted(self.offset_map.iteritems()):
            print k,v
            
if __name__ == "__main__":
    
    sen = [{'pos_tag': 'JJ', 'start': 0, 'end': 12, 'string': 'Differential', 'stem': 'Differenti'}, {'pos_tag': 'NN', 'start': 13, 'end': 22, 'string': 'induction', 'stem': 'induct'}, {'pos_tag': 'IN', 'start': 23, 'end': 25, 'string': 'of', 'stem': 'of'}, {'pos_tag': 'DT', 'start': 26, 'end': 29, 'string': 'the', 'stem': 'the'}, {'pos_tag': 'NN', 'start': 30, 'end': 35, 'string': 'NF-AT', 'stem': 'NF-AT'}, {'pos_tag': 'NN', 'start': 36, 'end': 43, 'string': 'complex', 'stem': 'complex'}, {'pos_tag': 'IN', 'start': 44, 'end': 50, 'string': 'during', 'stem': 'dure'}, {'pos_tag': 'NN', 'start': 51, 'end': 64, 'string': 'restimulation', 'stem': 'restimul'}, {'pos_tag': 'CC', 'start': 65, 'end': 68, 'string': 'and', 'stem': 'and'}, {'pos_tag': 'DT', 'start': 69, 'end': 72, 'string': 'the', 'stem': 'the'}, {'pos_tag': 'NN', 'start': 73, 'end': 82, 'string': 'induction', 'stem': 'induct'}, {'pos_tag': 'IN', 'start': 83, 'end': 85, 'string': 'of', 'stem': 'of'}, {'pos_tag': 'NN', 'start': 86, 'end': 92, 'string': 'T-cell', 'stem': 'T-cell'}, {'pos_tag': 'NN', 'start': 93, 'end': 99, 'string': 'anergy', 'stem': 'anergi'}, {'pos_tag': '.', 'start': 99, 'end': 100, 'string': '.', 'stem': '.'}]
    
    S = Sentence(sen)
    S.test()