'''
Created on Sep 2, 2013

@author: Andresta
'''

import json
from collections import Counter, defaultdict

class WordDictionary(object):
    '''
    classdocs
    '''
    
    # this folder contain data source for all docs
    DATA_DIR = "data"

    # this folder contain dictionary
    DICT_DIR = "dict"
    
    # sufix and extension for doc list
    DOCID_SUFIX_EXT = '_doc_ids.json'
    
    # sufix and extension for word dictionary
    WDICT_SUFIX_EXT = '_word_dict.json'
    
    CORPUS_DIR = ["dev","train","mix"]
    
    DATA_EXT = ".json"

    
    def __init__(self, source):
        '''
        Constructor
        '''
        self.src = source
    
    '''
    build all word dictionaries (dev, train, and mix)
    and save it to dict folder
    '''
    def build(self):
        for cdir in self.CORPUS_DIR:
            print "building " +cdir+ " word dictionary"
            fpath = self.src + '/' + self.DICT_DIR + '/' + cdir + self.WDICT_SUFIX_EXT
            with open(fpath, 'w') as f:
                f.write(json.dumps(self.build_dict(cdir)))
    
    '''
    build a dictionary based on corpus dir
    return dict of word
    dict = { word1 : count, .... , wordn : count }
    corpus_dir = "dev", "train", or "mix" (train and dev)  
    '''    
    def build_dict(self, corpus_dir):        
        if corpus_dir not in self.CORPUS_DIR:
            raise ValueError("wrong value. choose 'dev', 'train', or 'mix'")
        
        # get list of document
        doc_ids = self.get_doc_ids(corpus_dir)
        
        # init Counter
        cnt = Counter()
        
        for doc_id in doc_ids:
            sentences = self.get_sentences(doc_id)
            for sen in sentences:
                for w in sen:
                    string = w["string"]
                    if string.isalpha() and len(string) > 1:
                        string = string.lower()
                        cnt[string] += 1
        
        print "the dictionary contains:", len(cnt), "words"
        
        return dict(cnt)        
        
        
    '''
    get list of document id
    corpus_dir = "dev", "train", or "mix" (train and dev)  
    '''
    def get_doc_ids(self, corpus_dir):
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
    
    '''
    return list of sentence from document
    '''
    def get_sentences(self,doc_id):
        fpath = self.src + '/' + self.DATA_DIR +'/' + doc_id + self.DATA_EXT
        with open(fpath, 'r') as f:
            doc = json.loads(f.read())
            
        return doc["sen"]
        
       
class TriggerDictionary(object):
    
    # this folder contain data source for all docs
    DATA_DIR = "data"

    # this folder contain dictionary
    DICT_DIR = "dict"
    
    # sufix and extension for doc list
    DOCID_SUFIX_EXT = '_doc_ids.json'
    
    # sufix and extension for word dictionary
    TDICT_SUFIX_EXT = '_trigger_dict.json'
    
    CORPUS_DIR = ["dev","train","mix"]
    
    DATA_EXT = ".json"
    
    
    def __init__(self, source):
        
        self.src = source
        
    
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
            for t in triggers:
                # format of trigger
                # ["T60", "Negative_regulation", "190", "197", "inhibit"]
                string = t[4].lower()                
                ttype = t[1]
                td[string][ttype] += 1
                
                
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
    
    def test(self, corpus_dir):
        self.build_dict(corpus_dir)
    
        
        
if __name__ == "__main__":
    
    source = "E:/corpus/bionlp2011/project_data/"
    WD = WordDictionary(source)
    WD.build()
       
    
    TD = TriggerDictionary(source)
    TD.build()
    
    
    doc_list = False
    get_sen = False
    builddict = False
    
    
    if doc_list:
        doc_ids = WD.get_doc_ids("mix")
        for doc in doc_ids:
            print doc
        print "mix", len(doc_ids)
    if get_sen:
        doc_id = "PMC-1064873-05-Materials_and_methods-04"
        sentences = WD.get_sentences(doc_id)
        for sen in sentences:
            for w in sen:
                string = w["string"] 
                print string, string.isalpha()
    
        
        