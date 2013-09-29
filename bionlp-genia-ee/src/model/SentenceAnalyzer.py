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

    def __init__(self, WDict = None, TDict = None):
        """
        Init SentenceAnalyzer object
        Word dictionary and Trigger dictionary are optional for scoring
        """
                        
        self.wdict = WDict
        self.tdict = TDict
    
    def analyze(self, sentence, proteins):
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
        
        # update word type with protein
        self.update_word_protein(o_sen, proteins)                        
                                            
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
            if str3 != 0:
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
            
            if str2 != 0:
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
        # calculate score if dictionaries are present
        if self.wdict != None and self.tdict != None:
            w = self.wdict.count(word)
            if w != 0:
                retval = self.tdict.count(word) * 1.0 / w
        return retval
        
    def update_word_protein(self, o_sen, proteins):
        """
        Update word type with protein       
        """
        # mapping protein id with word number
        protein_mapping = {}
        
        # protein is dictionary format 'T1' : ['T1', 'Protein', '0', '4', 'IL-4']
        for e in proteins.values():
                                                
            # check whether start offset of protein is in sentence offset map
            # and get word number of protein
            offset =  int(e[2])                                
            wn = o_sen.offset_map.get(offset,-1)            
            if wn>=0: 
                o_sen.words[wn]["type"] = 'Protein'
                o_sen.protein.append(wn)
                protein_mapping[e[0]] = wn
                
        o_sen.entity_map.update(protein_mapping)        
    
    def update_word_trigger(self, o_sen, triggers):
        """
        Update word type with trigger       
        """
        # check dependency
        dep = o_sen.dep
        if dep == None:
            raise ValueError("update_word_trigger require dependency to process multi-words trigger")
        
        # mapping trigger id with trigger head word number
        trigger_mapping = {}
        
        # trigger is dictionary format 'T60' : ['T60', 'Negative_regulation', '190', '197', 'inhibit']
        for e in triggers.values():
            
            # skip entity
            if e[1] == 'Entity': continue
            
            # skip trigger more than 3 words
            nword = len(e[4].split(' '))
            if nword > 3: continue
                                                           
            # check whether offset of trigger is in sentence offset map
            # and get word number of first word of trigger
            offset =  int(e[2])                                
            wn = o_sen.offset_map.get(offset,-1)                        
            if wn>=0: 
                # get the head of trigger word number for trigger which has more than 1 word
                if nword > 1:
                    wn = dep.get_head(tuple(range(wn,wn+nword)))
                                
                o_sen.words[wn]["type"] = e[1] 
                o_sen.trigger.append(wn)
                trigger_mapping[e[0]] = wn
                
                # set trigger text
                o_sen.trigger_text[wn] = e[4].lower()
                                
                
        o_sen.entity_map.update(trigger_mapping)      
        
            
    def build_mapping(self, sentence):
        """
        return mapping of start offset to word number of a sentence
        """
        retval = {}
        for i in range(0, len(sentence)):
            word = sentence[i]
            retval[word["start"]] = i
        return retval
              
        
        