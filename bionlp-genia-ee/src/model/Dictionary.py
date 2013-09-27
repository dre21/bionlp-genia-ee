'''
Created on Sep 2, 2013

@author: Andresta
'''

import json, os
from collections import Counter, defaultdict
from tools.PorterStemmer import PorterStemmer

class Dictionary(object):
    # this folder contain data source for all docs
    DATA_DIR = "data"

    # this folder contain dictionary
    DICT_DIR = "dict"
    
    # suffix and extension for doc list
    DOCID_SUFIX_EXT = '_doc_ids.json'
    
    # suffix and extension for word dictionary
    WDICT_SUFIX_EXT = '_word_dict.json'
    
    # suffix and extension for word dictionary
    TDICT_SUFIX_EXT = '_trigger_dict.json'
        
    CORPUS_DIR = ["dev","train","mix"]
    
    DATA_EXT = ".json"
    
    def __init__(self, source):
        """
        Constructor
        """
        self.src = source
        
        self.data = {}
    
    def get_doc_ids(self, corpus_dir):
        """
        get list of document id
        corpus_dir = "dev", "train", or "mix" (train and dev)  
        """
        if corpus_dir not in self.CORPUS_DIR:
            raise ValueError("wrong value. choose 'dev', 'train', or 'mix'")
        
        doc_ids = []
        if corpus_dir == "dev" or corpus_dir == "train":
            fpath = self.src + '/' + corpus_dir + self.DOCID_SUFIX_EXT
            with open(fpath, 'r') as f:
                doc_ids = json.loads(f.read())        
        elif corpus_dir == "mix":
            doc_ids = self.get_doc_ids("dev") + self.get_doc_ids("train")
        
        return doc_ids
    

class WordDictionary(Dictionary):
    """
    classdocs
    """       
    
    def __init__(self, source):
        '''
        Constructor
        '''
        super(WordDictionary, self).__init__(source)               
    
    def load(self, corpus_dir):
        """
        Load a dictionary data
        corpus_dir is dev, train, or mix
        """
        if corpus_dir not in self.CORPUS_DIR:
            raise ValueError("wrong value. choose 'dev', 'train', or 'mix'")
        
        fpath = self.src + '/' + self.DICT_DIR + '/' + corpus_dir + self.WDICT_SUFIX_EXT
        if not os.path.exists(fpath):
            print "Dictionary data is not exist"
            print "Building dictionary data"
            self.build()            
        
        with open(fpath, 'r') as f:
            self.data = json.loads(f.read())
            
    def count(self, word):
        """
        return number of word occurrence in dictionary
        """   
        if self.data == {}:
            raise ValueError("Dictionary data has not been loaded")
        return self.data.get(word.lower(), 0)
        
        
    def build(self):
        """
        build all word dictionaries (dev, train, and mix)
        and save it to dict folder
        """
        for cdir in self.CORPUS_DIR:
            print "building " +cdir+ " word dictionary"
            fpath = self.src + '/' + self.DICT_DIR + '/' + cdir + self.WDICT_SUFIX_EXT
            with open(fpath, 'w') as f:
                f.write(json.dumps(self.build_dict(cdir)))

    
    def build_dict(self, corpus_dir):
        """
        build a dictionary based on corpus dir
        return dict of word
        dict = { word1 : count, .... , wordn : count }
        corpus_dir = "dev", "train", or "mix" (train and dev)  
        """        
        if corpus_dir not in self.CORPUS_DIR:
            raise ValueError("wrong value. choose 'dev', 'train', or 'mix'")
        
        # get list of document
        doc_ids = self.get_doc_ids(corpus_dir)
        
        # init Counter
        cnt = Counter()
        
        for doc_id in doc_ids:
            sentences = self.get_sentences(doc_id)
            for sen in sentences:
                nwords = len(sen)
                for i in range(0,nwords):
                    w = sen[i]
                    string = w["string"]
                    stem = w['stem']
                    if not string.isdigit() and len(string) > 1:
                        string = string.lower()
                        stem = stem.lower()
                        cnt[string] += 1
                        cnt[stem] += 1
                        
                    # adding bigram to dict
                    if i+1 < nwords:
                        w2 = sen[i+1]
                        string2 = w2["string"].lower()
                        cnt[string +' '+ string2] += 1
                        
                    # adding trigram to dict
                    if i+2 < nwords:
                        w3 = sen[i+2]
                        string3 = w3["string"].lower()
                        cnt[string +' '+ string2 +' '+ string3] += 1
        
        print "the dictionary contains:", len(cnt), "words"
        
        return dict(cnt)        
                            
    def get_sentences(self,doc_id):
        """
        return list of sentence from document
        """
        fpath = self.src + '/' + self.DATA_DIR +'/' + doc_id + self.DATA_EXT
        with open(fpath, 'r') as f:
            doc = json.loads(f.read())
            
        return doc["sen"]
    
    
    def test(self, test_name):
        Stemmer = PorterStemmer()
        if test_name == "loading":
            words = ["induction","inducted","restimulated","binding","binds","up-regulate","mRNA expression","binding activity"]            
            self.load("dev")
            
            print "\n\n----------------------------"
            print "Using original string"            
            for w in words:
                cnt = self.count(w)
                print w, cnt
            
            print "\n\n----------------------------"
            print "Using stem version of string"
            for w in words:
                w = Stemmer.stem(w, 0, len(w)-1)
                cnt = self.count(w)
                print w, cnt
                
            print "\n\n"
       
class TriggerDictionary(Dictionary):       
    
    def __init__(self, source):
        
        super(TriggerDictionary,self).__init__(source)
        self.Stemmer = PorterStemmer()
        
    def load(self, corpus_dir):
        """
        Load a trigger dictionary data
        corpus_dir is dev, train, or mix
        """
        if corpus_dir not in self.CORPUS_DIR:
            raise ValueError("wrong value. choose 'dev', 'train', or 'mix'")
        
        fpath = self.src + '/' + self.DICT_DIR + '/' + corpus_dir + self.TDICT_SUFIX_EXT
        if not os.path.exists(fpath):
            print "Trigger dictionary data is not exist"
            print "Now building new trigger dictionary data ..."
            self.build()
        
        with open(fpath, 'r') as f:
            self.data = json.loads(f.read())
            
            
    def count(self, word, ttype = ""):
        """
        return number of word occurrence in dictionary
        """   
        if self.data == {}:
            raise ValueError("Dictionary data has not been loaded")
        # get counter
        ttype_cnt = self.data.get(word.lower(), None)
        retval = 0
        if ttype_cnt != None:
            if ttype != "":
                retval = ttype_cnt.get(ttype,0)
            else:
                # get count for all event type
                for v in ttype_cnt.itervalues():
                    retval+=v
        return retval
            
    
    def build(self):
        """
        build all trigger dictionaries (dev, train, and mix)
        and save it to dict folder
        """
        for cdir in self.CORPUS_DIR:
            print "building " +cdir+ " trigger dictionary"
            fpath = self.src + '/' + self.DICT_DIR + '/' + cdir + self.TDICT_SUFIX_EXT
            with open(fpath, 'w') as f:
                f.write(json.dumps(self.build_dict(cdir)))
                 
                 
    def build_dict(self, corpus_dir):
        if corpus_dir not in self.CORPUS_DIR:
            raise ValueError("wrong value. choose 'dev', 'train', or 'mix'")
        
        # get list of document
        doc_ids = self.get_doc_ids(corpus_dir)
        
        # init default dict with counter
        td = defaultdict(Counter)
        
        for doc_id in doc_ids:
            triggers = self.get_triggers(doc_id)
            for t in triggers.values():
                # format of trigger
                # ["T60", "Negative_regulation", "190", "197", "inhibit"]
                string = t[4].lower()                               
                ttype = t[1]
                td[string][ttype] += 1
                # only process single word trigger for steming      
                if " " not in string:          
                    stem = self.Stemmer.stem(string, 0, len(string)-1)                    
                    td[stem][ttype] += 1
                
                
        print "the dictionary contains:", len(td), "trigger words"
        
        return dict(td)
            
    def get_triggers(self, doc_id):
        """
        return list of trigger from document
        """
        fpath = self.src + '/' + self.DATA_DIR +'/' + doc_id + self.DATA_EXT
        with open(fpath, 'r') as f:
            doc = json.loads(f.read())
            
        return doc["trigger"]
                
    def test(self, test_name):
           
        if test_name == "loading":            
            trigger = {"induction":"Positive_regulation",
                       "restimulated":"Regulation",
                       "binding":"Binding",
                       "binds":"Binding",
                       "mRNA expression":"Transcription",
                       "binding activity":"Binding"}
            
            print "\n\n----------------------------"
            print "Using original string"
            self.load("dev")
            for t,ttype in trigger.iteritems():
                cnt1 = self.count(t)
                cnt2 = self.count(t, ttype)
                print t, "All", cnt1
                print t, ttype, cnt2
                
            print "\n\n----------------------------"
            print "Using stem version of string"
            for t,ttype in trigger.iteritems():
                t = self.Stemmer.stem(t, 0, len(t)-1)
                cnt1 = self.count(t)
                cnt2 = self.count(t, ttype)
                print t, "All", cnt1
                print t, ttype, cnt2
                
            print "\n\n"
        
if __name__ == "__main__":
    
    source = "E:/corpus/bionlp2011/project_data/"
    
    WD = WordDictionary(source)    
    WD.build()
    WD.test("loading")
           
    TD = TriggerDictionary(source)
    TD.build()
    TD.test("loading")
        
    
        
        