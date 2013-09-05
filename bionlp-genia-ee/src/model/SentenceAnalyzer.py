"""
Created on Sep 3, 2013

@author: Andresta
"""

from model.Dictionary import WordDictionary, TriggerDictionary
from model.Sentence import Sentence

class SentenceAnalyzer(object):
    """
    Analyze and construct a sentence object
    1. Determine trigger candidate of the sentence
    2. Update type of word in a sentence
    3. Update score for each word
    """

    # list of allowed pos tag for trigger
    POS_TAG = ["NN","VBN", "JJ", "VB", "VBZ", "VBD", "VBG", "VBP", "NNS"]

    def __init__(self, WDict, TDict):
        """
        Init SentenceAnalyzer object
        it requires Word dictionary and Trigger dictionary
        """
        if not (isinstance(WDict, WordDictionary) and isinstance(TDict,TriggerDictionary)):
            raise TypeError("Dictionary type is not match")
                
        self.wdict = WDict
        self.tdict = TDict
    
    def analyze(self, sentence, proteins, triggers):
        """
        analyze and construct sentence object
        return sentence object
        sentence: sentence data in list representation
        proteins: list of protein
        trigger: list of trigger        
        """
        # create sentence object
        o_sen = Sentence(sentence)
        # update word type with protein & trigger
        self.update_word_type(o_sen, proteins)
        self.update_word_type(o_sen, triggers)
        # set trigger candidate
        self.set_candidate(o_sen)
        
        return o_sen
        
    
    def set_candidate(self, Sentence):
        """
        Set list of word number which is marked as trigger candidate
        and update trigger probability for each word in a sentence
        """
        
        for i in range(0,Sentence.nwords):
            # filter word
            word = Sentence.words[i]
            if not self.filter(word):
                Sentence.trigger_candidate.append(i)
            
            # assign score
            word["score"] = self.get_score(word)
                                            
    def filter(self, word):
        """
        return true if the word is filtered out from a candidate trigger, false otherwise        
        currently only filter based on pos_tag
        """
        remove=False        
        
        # Rule 0, word is not protein
        if word["type"] == "Protein":
            remove = True
        
        # Rule 1, filter by pos tag
        # only pos tag with significant number of trigger occurrence are include
        # IN (preposition) is not used, need further study about this. for simplicity it's not included
        elif word["pos_tag"] not in self.POS_TAG:
            remove = True
            
        # Rule 2, filter by word length
        # only words with length greater than 3 are included
        elif len(word["string"]) < 4:
            remove = True                   
            
        return remove
        
    def get_score(self, word):
        """
        calculate the probability score for trigger candidate
        """
        retval = 0.0
        string = word["string"]
        w = self.wdict.count(string)
        if w != 0:
            retval = self.tdict.count(string) * 1.0 / w
        return retval
        
    def update_word_type(self, Sentence, entity_list):
        """
        Update word type based on protein or trigger type
        entity list is either protein or trigger list
        """
        
        # update entity
        # protein is list format ['T1', 'Protein', '0', '4', 'IL-4']
        # trigger is list format ['T60', 'Negative_regulation', '190', '197', 'inhibit']
        for e in entity_list:
            
            # skip two words entity, currently only handle 1 word trigger
            #TODO: handling multi-word trigger
            if ' ' in e[4]: continue            
            
            # check whether offset of protein is in this sentence
            offset =  int(e[2])                                    
            i = Sentence.offset_map.get(offset,-1)
            if i>0: 
                Sentence.words[i]["type"] = e[1] 
                       
        
        
    def test(self):
        sen = [{'pos_tag': 'PRP', 'end': 149, 'string': 'We', 'stem': 'We', 'start': 147, 'score': 0.0, 'type': 'null'}, {'pos_tag': 'RB', 'end': 159, 'string': 'therefore', 'stem': 'therefor', 'start': 150, 'score': 0.0, 'type': 'null'}, {'pos_tag': 'VBD', 'end': 165, 'string': 'asked', 'stem': 'ask', 'start': 160, 'score': 0.0, 'type': 'null'}, {'pos_tag': 'IN', 'end': 173, 'string': 'whether', 'stem': 'whether', 'start': 166, 'score': 0.0, 'type': 'null'}, {'pos_tag': 'NN', 'end': 178, 'string': 'XXXX', 'stem': 'XXXX', 'start': 174, 'score': 0.0, 'type': 'null'}, {'pos_tag': 'VBZ', 'end': 181, 'string': 'is', 'stem': 'is', 'start': 179, 'score': 0.0, 'type': 'null'}, {'pos_tag': 'JJ', 'end': 186, 'string': 'able', 'stem': 'abl', 'start': 182, 'score': 0.0, 'type': 'null'}, {'pos_tag': 'TO', 'end': 189, 'string': 'to', 'stem': 'to', 'start': 187, 'score': 0.0, 'type': 'null'}, {'pos_tag': 'VB', 'end': 197, 'string': 'inhibit', 'stem': 'inhibit', 'start': 190, 'score': 0.0, 'type': 'null'}, {'pos_tag': 'NN', 'end': 206, 'string': 'XXXXXXXX', 'stem': 'XXXXXXXX', 'start': 198, 'score': 0.0, 'type': 'null'}, {'pos_tag': 'NN', 'end': 216, 'string': 'induction', 'stem': 'induct', 'start': 207, 'score': 0.0, 'type': 'null'}, {'pos_tag': 'IN', 'end': 219, 'string': 'of', 'stem': 'of', 'start': 217, 'score': 0.0, 'type': 'null'}, {'pos_tag': 'NN', 'end': 225, 'string': 'XXXXX', 'stem': 'XXXXX', 'start': 220, 'score': 0.0, 'type': 'null'}, {'pos_tag': 'IN', 'end': 232, 'string': 'during', 'stem': 'dure', 'start': 226, 'score': 0.0, 'type': 'null'}, {'pos_tag': 'DT', 'end': 236, 'string': 'the', 'stem': 'the', 'start': 233, 'score': 0.0, 'type': 'null'}, {'pos_tag': 'NN', 'end': 244, 'string': 'priming', 'stem': 'prime', 'start': 237, 'score': 0.0, 'type': 'null'}, {'pos_tag': 'IN', 'end': 247, 'string': 'of', 'stem': 'of', 'start': 245, 'score': 0.0, 'type': 'null'}, {'pos_tag': 'JJ', 'end': 253, 'string': 'naive', 'stem': 'naiv', 'start': 248, 'score': 0.0, 'type': 'null'}, {'pos_tag': 'NN', 'end': 255, 'string': 'T', 'stem': 'T', 'start': 254, 'score': 0.0, 'type': 'null'}, {'pos_tag': 'NNS', 'end': 261, 'string': 'cells', 'stem': 'cell', 'start': 256, 'score': 0.0, 'type': 'null'}, {'pos_tag': '.', 'end': 262, 'string': '.', 'stem': '.', 'start': 261, 'score': 0.0, 'type': 'null'}]
        proteins = [['T1', 'Protein', '0', '4', 'IL-4'],
                    ['T2', 'Protein', '14', '22', 'TGF-beta'],
                    ['T3', 'Protein', '49', '53', 'IL-4'],
                    ['T4', 'Protein', '174', '178', 'IL-4'],
                    ['T5', 'Protein', '198', '206', 'TGF-beta'],
                    ['T6', 'Protein', '220', '225', 'FOXP3'],
                    ['T7', 'Protein', '269', '272', 'CD4'],
                    ['T8', 'Protein', '273', '279', 'CD45RA'],
                    ['T9', 'Protein', '326', '329', 'CD3'],
                    ['T10', 'Protein', '330', '334', 'CD28']]
        
        triggers = [['T60', 'Negative_regulation', '190', '197', 'inhibit'],
                    ['T61', 'Positive_regulation', '207', '216', 'induction'],
                    ['T62', 'Negative_regulation', '417', '426', 'repressed'],
                    ['T63', 'Positive_regulation', '449', '458', 'induction'],
                    ['T64', 'Gene_expression', '468', '478', 'expression'],
                    ['T65', 'Negative_regulation', '565', '572', 'induced'],
                    ['T66', 'Negative_regulation', '585', '592', 'absence'],
                    ['T67', 'Positive_regulation', '696', '702', 'induce'],
                    ['T68', 'Gene_expression', '709', '719', 'expression']]
        
        S = self.analyze(sen, proteins, triggers)        
        S.test()
        
if __name__ == "__main__":
    
    source = "E:/corpus/bionlp2011/project_data/"
    
    WD = WordDictionary(source)    
    WD.load("dev")
       
    TD = TriggerDictionary(source)
    TD.load("dev")
    
        
        
    TC = SentenceAnalyzer(WD, TD)
    TC.test()
        
        
        