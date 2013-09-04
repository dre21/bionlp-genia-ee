"""
Created on Sep 3, 2013

@author: Andresta
"""

from model.Dictionary import WordDictionary, TriggerDictionary
from model.Sentence import Sentence

class TriggerCandidate(object):
    """
    This class will filter out words which are note good candidate of a trigger
    it reduces number of word to be processed
    """

    # list of allowed pos tag for trigger
    POS_TAG = ["NN","VBN", "JJ", "VB", "VBZ", "VBD", "VBG", "VBP", "NNS"]

    def __init__(self, WDict, TDict):
        """
        Init TriggerCandidate object
        it requires Word dictionary and Trigger dictionary
        """
        if not (isinstance(WDict, WordDictionary) and isinstance(TDict,TriggerDictionary)):
            raise TypeError("Dictionary type is not match")
                
        self.wdict = WDict
        self.tdict = TDict
    
    
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
        
        
    def test(self):
        sen = [{'pos_tag': 'IN', 'end': 3995, 'string': 'Because', 'stem': 'Becaus', 'start': 3988, 'score': 0.0, 'type': 'null'}, {'pos_tag': 'IN', 'end': 3998, 'string': 'of', 'stem': 'of', 'start': 3996, 'score': 0.0, 'type': 'null'}, {'pos_tag': 'DT', 'end': 4002, 'string': 'the', 'stem': 'the', 'start': 3999, 'score': 0.0, 'type': 'null'}, {'pos_tag': 'NN', 'end': 4014, 'string': 'involvement', 'stem': 'involv', 'start': 4003, 'score': 0.0, 'type': 'null'}, {'pos_tag': 'IN', 'end': 4017, 'string': 'of', 'stem': 'of', 'start': 4015, 'score': 0.0, 'type': 'null'}, {'pos_tag': 'NN', 'end': 4022, 'string': 'XXXX', 'stem': 'XXXX', 'start': 4018, 'score': 0.0, 'type': 'null'}, {'pos_tag': 'NNS', 'end': 4032, 'string': 'mutations', 'stem': 'mutat', 'start': 4023, 'score': 0.0, 'type': 'null'}, {'pos_tag': 'IN', 'end': 4035, 'string': 'in', 'stem': 'in', 'start': 4033, 'score': 0.0, 'type': 'null'}, {'pos_tag': 'JJ', 'end': 4045, 'string': 'different', 'stem': 'differ', 'start': 4036, 'score': 0.0, 'type': 'null'}, {'pos_tag': 'JJ', 'end': 4056, 'string': 'autoimmune', 'stem': 'autoimmun', 'start': 4046, 'score': 0.0, 'type': 'null'}, {'pos_tag': 'NNS', 'end': 4065, 'string': 'diseases', 'stem': 'diseas', 'start': 4057, 'score': 0.0, 'type': 'null'}, {'pos_tag': 'CC', 'end': 4069, 'string': 'and', 'stem': 'and', 'start': 4066, 'score': 0.0, 'type': 'null'}, {'pos_tag': 'DT', 'end': 4073, 'string': 'the', 'stem': 'the', 'start': 4070, 'score': 0.0, 'type': 'null'}, {'pos_tag': 'JJ', 'end': 4079, 'string': 'known', 'stem': 'known', 'start': 4074, 'score': 0.0, 'type': 'null'}, {'pos_tag': 'NN', 'end': 4091, 'string': 'interaction', 'stem': 'interact', 'start': 4080, 'score': 0.0, 'type': 'null'}, {'pos_tag': 'IN', 'end': 4096, 'string': 'with', 'stem': 'with', 'start': 4092, 'score': 0.0, 'type': 'null'}, {'pos_tag': 'NN', 'end': 4105, 'string': 'XXXXXXXX', 'stem': 'XXXXXXXX', 'start': 4097, 'score': 0.0, 'type': 'null'}, {'pos_tag': ',', 'end': 4106, 'string': ',', 'stem': ',', 'start': 4105, 'score': 0.0, 'type': 'null'}, {'pos_tag': 'PRP', 'end': 4109, 'string': 'we', 'stem': 'we', 'start': 4107, 'score': 0.0, 'type': 'null'}, {'pos_tag': 'VBD', 'end': 4122, 'string': 'investigated', 'stem': 'investig', 'start': 4110, 'score': 0.0, 'type': 'null'}, {'pos_tag': 'DT', 'end': 4126, 'string': 'the', 'stem': 'the', 'start': 4123, 'score': 0.0, 'type': 'null'}, {'pos_tag': 'NN', 'end': 4133, 'string': 'impact', 'stem': 'impact', 'start': 4127, 'score': 0.0, 'type': 'null'}, {'pos_tag': 'IN', 'end': 4136, 'string': 'of', 'stem': 'of', 'start': 4134, 'score': 0.0, 'type': 'null'}, {'pos_tag': 'NN', 'end': 4142, 'string': 'XXXXX', 'stem': 'XXXXX', 'start': 4137, 'score': 0.0, 'type': 'null'}, {'pos_tag': 'CC', 'end': 4146, 'string': 'and', 'stem': 'and', 'start': 4143, 'score': 0.0, 'type': 'null'}, {'pos_tag': 'NN', 'end': 4152, 'string': 'XXXXX', 'stem': 'XXXXX', 'start': 4147, 'score': 0.0, 'type': 'null'}, {'pos_tag': 'IN', 'end': 4155, 'string': 'on', 'stem': 'on', 'start': 4153, 'score': 0.0, 'type': 'null'}, {'pos_tag': 'DT', 'end': 4159, 'string': 'the', 'stem': 'the', 'start': 4156, 'score': 0.0, 'type': 'null'}, {'pos_tag': 'NN', 'end': 4170, 'string': 'expression', 'stem': 'express', 'start': 4160, 'score': 0.0, 'type': 'null'}, {'pos_tag': 'IN', 'end': 4173, 'string': 'of', 'stem': 'of', 'start': 4171, 'score': 0.0, 'type': 'null'}, {'pos_tag': 'NN', 'end': 4179, 'string': 'XXXXX', 'stem': 'XXXXX', 'start': 4174, 'score': 0.0, 'type': 'null'}, {'pos_tag': 'CC', 'end': 4183, 'string': 'and', 'stem': 'and', 'start': 4180, 'score': 0.0, 'type': 'null'}, {'pos_tag': 'RB', 'end': 4196, 'string': 'subsequently', 'stem': 'subsequ', 'start': 4184, 'score': 0.0, 'type': 'null'}, {'pos_tag': 'IN', 'end': 4199, 'string': 'on', 'stem': 'on', 'start': 4197, 'score': 0.0, 'type': 'null'}, {'pos_tag': 'DT', 'end': 4203, 'string': 'the', 'stem': 'the', 'start': 4200, 'score': 0.0, 'type': 'null'}, {'pos_tag': 'NN', 'end': 4215, 'string': 'development', 'stem': 'develop', 'start': 4204, 'score': 0.0, 'type': 'null'}, {'pos_tag': 'CC', 'end': 4219, 'string': 'and', 'stem': 'and', 'start': 4216, 'score': 0.0, 'type': 'null'}, {'pos_tag': 'NN', 'end': 4228, 'string': 'function', 'stem': 'function', 'start': 4220, 'score': 0.0, 'type': 'null'}, {'pos_tag': 'IN', 'end': 4231, 'string': 'of', 'stem': 'of', 'start': 4229, 'score': 0.0, 'type': 'null'}, {'pos_tag': 'PRP', 'end': 4234, 'string': 'iT', 'stem': 'iT', 'start': 4232, 'score': 0.0, 'type': 'null'}, {'pos_tag': 'NN', 'end': 4238, 'string': 'reg', 'stem': 'reg', 'start': 4235, 'score': 0.0, 'type': 'null'}, {'pos_tag': 'NNS', 'end': 4244, 'string': 'cells', 'stem': 'cell', 'start': 4239, 'score': 0.0, 'type': 'null'}, {'pos_tag': '.', 'end': 4245, 'string': '.', 'stem': '.', 'start': 4244, 'score': 0.0, 'type': 'null'}]
    
        S = Sentence(sen)        
        self.set_candidate(S)
        S.test()
        
if __name__ == "__main__":
    
    source = "E:/corpus/bionlp2011/project_data/"
    
    WD = WordDictionary(source)    
    WD.load("dev")
       
    TD = TriggerDictionary(source)
    TD.load("dev")
    
        
        
    TC = TriggerCandidate(WD, TD)
    TC.test()
        
        
        