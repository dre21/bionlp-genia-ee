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
        
        # set sentence mapping
        o_sen.offset_map = self.build_mapping(sentence)
        
        # update word type with protein & trigger
        self.update_word_type(o_sen, proteins)
        
        if triggers != []:
            self.update_word_type(o_sen, triggers)
        
        # set trigger candidate
        self.set_candidate_multi(o_sen)
                                            
        return o_sen
            
    def set_candidate(self, Sentence):
        """
        Set list of word number which is marked as trigger candidate
        and update trigger probability for each word in a sentence
        """
        
        for i in range(0,Sentence.nwords):
            
            word = Sentence.words[i]
            
            # assign score
            word["score"] = self.get_score(word['string'])
            word['score-2'] = self.get_score(word['stem'])
            # filter word
            if not self.filter(word):
                Sentence.trigger_candidate.append(i)
            
    def set_candidate_multi(self, Sentence):
        """
        Set list of word number which is marked as trigger candidate
        and update trigger probability for each word in a sentence
        allow multi-words trigger
        """
        
        # list of used word
        used = []
        
        for i in range(0,Sentence.nwords):
            if i in used: continue
            
            w1 = Sentence.words[i]
            
            # assign string
            str1 = w1['string']
            str2 = ''
            str3 = ''
            
            # assign score
            w1["score"] = self.get_score(str1)
            w1['score-2'] = self.get_score(w1['stem'])
            
            # get bigram
            if i+1 < Sentence.nwords:                
                w2 = Sentence.words[i+1]
                str2 = str1 +' '+ w2['string']
            
                # get trigram
                if i+2 < Sentence.nwords:  
                    w3 = Sentence.words[i+2]              
                    str3 = str2 +' '+ w3['string'] 
                    
            
            # procees trigger candidate
            # check wheter to accept str3
            if str3 != '':
                str3_score = self.get_score(str3)
                cond1 = str3_score > 0.01
                cond2 = w2['type'] != 'Protein'
                cond3 = w3['type'] != 'Protein'                
                if cond1 and cond2 and cond3:
                    Sentence.trigger_candidate.append((i,i+1,i+2))
                    used = [i+1,i+2]
                    w1["score"] = str3_score
                    w2["score"] = str3_score
                    w3["score"] = str3_score
                    continue
            
            if str2 != '':
                str2_score =  self.get_score(str2)
                cond1 = str2_score > 0.01
                cond2 = w2['type'] != 'Protein'
                if cond1 and cond2:
                    Sentence.trigger_candidate.append((i,i+1))
                    used = [i+1]
                    w1['score'] = str2_score
                    w2['score'] = str2_score
                    continue
                
            if not self.filter(w1):
                Sentence.trigger_candidate.append((i))     
        
                                            
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
            
        # Rule 3, filter by score
        elif word['score'] < 0.1:
            remove = True
            
        return remove
        
    def get_score(self, word):
        """
        calculate the probability score for trigger candidate
        """
        retval = 0.0
        #stem = word["stem"]
        #string = word["string"]
        w = self.wdict.count(word)
        if w != 0:
            retval = self.tdict.count(word) * 1.0 / w
        return retval
        
    def update_word_type(self, Sentence, entity_list):
        """
        Update word type based on protein or trigger type
        entity list is either protein or trigger list        
        """
        mapping = {}
        # update entity
        # protein is list format 'T1' : ['T1', 'Protein', '0', '4', 'IL-4']
        # trigger is list format 'T60' : ['T60', 'Negative_regulation', '190', '197', 'inhibit']
        for e in entity_list.values():
            
            # skip two words trigger, currently only handle 1 word trigger
            # skip entity type, we ignore entity for task 1
            #TODO: handling multi-word trigger
            #if ' ' in e[4] and e[1] != "Protein": continue
            if e[1] == "Entity": continue            
                        
            nword = len(e[4].split(' '))
            if nword > 3 and  e[1] != "Protein": continue
            
            # check whether offset of protein is in this sentence
            offset =  int(e[2])                                
            i = Sentence.offset_map.get(offset,-1)            
            if i>=0: 
                Sentence.words[i]["type"] = e[1] 
                                
                if e[1] == "Protein":
                    wn_tuple = i
                    Sentence.protein.append(wn_tuple)
                else:
                    if nword == 1:
                        wn_tuple = i                        
                    elif nword == 2:
                        wn_tuple = (i,i+1)
                        Sentence.words[i+1]["type"] = e[1]
                    elif nword == 3:
                        wn_tuple = (i,i+1,i+2)          
                        Sentence.words[i+1]["type"] = e[1]
                        Sentence.words[i+2]["type"] = e[1]          
                    Sentence.trigger.append(wn_tuple)
                
                mapping[e[0]] = wn_tuple 
                
        Sentence.entity_map.update(mapping)        
                       
    def build_mapping(self, sentence):
        """
        return mapping of start offset to word number of a sentence
        """
        retval = {}
        for i in range(0, len(sentence)):
            word = sentence[i]
            retval[word["start"]] = i
        return retval
              
        
        