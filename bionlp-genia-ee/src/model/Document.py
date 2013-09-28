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
from model.Chunk import Chunk

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

    def update(self, sen_num, trig_wn, trig_type, arg_wn, arg_name, arg_type):
        self.sen[sen_num].update(trig_wn, trig_type, arg_wn, arg_name, arg_type)
        
    def update_relation(self, rel_type, sen_num, trig_wn, arg_wn):
        """
        only update relation
        rel_type: ['cause', 'theme2']
        trigger-argument-cause ==> add cause relation
        binding-argument1-argument2 ==> update relation from theme to theme2
        """
        if rel_type == 'cause':
            self.sen[sen_num].update_cause(trig_wn, arg_wn)
        elif rel_type == 'theme2':
            self.sen[sen_num].update_theme2(trig_wn, arg_wn)
        else:
            raise ValueError("")        
                    
        
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
        
    def build(self, doc_id, is_test = False):
        """
        return document object
        """
        return self.build_doc_from_raw(self.read_raw(doc_id), is_test)
    
    def build_doc_from_raw(self, doc, is_test):
        """
        build a document object from raw data provided by genia reader
        it returns document object
        doc: document raw data
        """
        
        # create document object
        o_doc = Document(doc["doc_id"], doc["test"])
        # force is_test property value by a provided value if document is not from test corpus
        # to make dev document a test doc for validation purpose
        if doc["test"] == False:
            o_doc.is_test = is_test
        
        
        # process document sentence        
        for i in range(0,doc["nsen"]):
            # remove these property if document is marked as a test doc            
            if o_doc.is_test:
                doc["trigger"] = []
                doc["even"] = []
                doc["equiv"] = []
                
                       
            # create sentence object
            o_sen = self.sa.analyze(doc["sen"][i], doc["protein"],[])      
            o_sen.number = i
            
            # add dependency to sentence
            o_sen.dep = Dependency(doc["dep"][i])
                  
            # add chunk to sentence
            o_sen.chunk = Chunk(doc['chunk'][i])
            
            # add tree to sentence
            # TODO: add tree to sentence
            
            # add relation to sentence
            o_sen.rel = Relation()
            if not o_doc.is_test:
                o_sen.rel.build(o_sen.entity_map, doc["event"], doc["equiv"])
                self.sa.update_trigger_word(o_sen,doc["trigger"])
            # add sentence object to document object
            o_doc.add_sentence(o_sen)                         
                                                      
        return o_doc
                
        
    def read_raw(self, doc_id):
        fpath = self.src + '/' + self.DATA_DIR +'/' + doc_id + self.DATA_EXT
        with open(fpath, 'r') as f:
            doc = json.loads(f.read())
        return doc
       
