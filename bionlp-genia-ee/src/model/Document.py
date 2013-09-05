"""
Created on Sep 4, 2013

@author: Andresta
"""

import json
from datetime import datetime as dt
from model.Dictionary import TriggerDictionary, WordDictionary
from model.SentenceAnalyzer import SentenceAnalyzer 
from model.Dependency import Dependency
from model.Relation import Relation

class Document(object):
    """
    classdocs
    """


    def __init__(self, doc_id, is_test = False):
        """
        Constructor
        """
        self.doc_id = doc_id
        self.is_test = is_test
        
        # list of sentence object
        self.sen = []
                
        
    def add_sentence(self, o_sen):
        """
        adding sentence object o_sen to sen list
        """
        self.sen.append(o_sen)
                   
        
    def test(self):
        
        print "doc id:", self.doc_id
        print "is test:", self.is_test
        
        for s in self.sen:
            s.test()
            print "\n"
        
        
        
class DocumentBuilder(object):
    """
    Read document data and build a document object
    """
    
    # this folder contain data source for all docs
    DATA_DIR = "data"
    
    # extension for document data
    DATA_EXT = ".json"
    
    # sufix and extension for doc list
    DOCID_SUFIX_EXT = '_doc_ids.json'
    
       
    CORPUS_DIR = ["dev","train","mix"]
           
    
    def __init__(self, source, word_dict, trigger_dict):
       
        if not (isinstance(trigger_dict, TriggerDictionary) and isinstance(word_dict, WordDictionary)):
            raise TypeError("Dictionaries must be a TriggerDictionary and WordDictionary")
                
        self.src = source
        self.td = trigger_dict
        self.wd = word_dict
        
        self.sa = None
        
        self.init_trigger_candidate()
        
    def init_trigger_candidate(self):
        """
        Init trigger candidate object for filtering word as candidate of trigger
        """
        self.sa = SentenceAnalyzer(self.wd, self.td)
        
    
    def build_doc_from_raw(self, doc):
        """
        build a document object from raw data provided by genia reader
        it returns document object
        doc: document raw data
        """
        
        # create document object
        o_doc = Document(doc["doc_id"], doc["test"])
        
        
        # process document sentence        
        for i in range(0,doc["nsen"]):
            # create sentence object
            o_sen = self.sa.analyze(doc["sen"][i], doc["protein"],doc["trigger"])      
            
            # add dependency to sentence
            o_sen.dep = Dependency(doc["dep"][i])
                  
            # add chunk to sentence
            # TODO: add chunk to sentence
            
            # add tree to sentence
            # TODO: add tree to sentence
            
            # add relation to sentence
            o_sen.rel = Relation(o_sen.entity_map, doc["event"], doc["equiv"])
            
            
            # add sentence object to document object
            o_doc.add_sentence(o_sen)
                                                               
        return o_doc
                
        
    def read_raw(self, doc_id):
        fpath = self.src + '/' + self.DATA_DIR +'/' + doc_id + self.DATA_EXT
        with open(fpath, 'r') as f:
            doc = json.loads(f.read())
        return doc
        
    def test(self, doc_id):
        
        start = dt.now()
        doc = self.read_raw(doc_id)
        o_doc = self.build_doc_from_raw(doc)
        #o_doc.test()
        end = dt.now()
        print "building " + doc_id + " for ", end-start, "seconds"
        

if __name__ == "__main__":
    
    source = "E:/corpus/bionlp2011/project_data/"
    doc_id = "PMC-2222968-04-Results-03"
    
    WD = WordDictionary(source)    
    WD.load("train")
           
    TD = TriggerDictionary(source)
    TD.load("train")
    
    builder = DocumentBuilder(source, WD, TD)
    builder.test(doc_id)