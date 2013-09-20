"""
Created on Sep 4, 2013

@author: Andresta
"""

import json, os
from features.DependencyFeature import DependencyFeature
from features.SentenceFeature import SentenceFeature
from model.Dictionary import WordDictionary, TriggerDictionary
from model.Document import DocumentBuilder

class FeatureExtraction(object):
    """
    classdocs
    """
    # this is a folder to store all features data
    FEATURE_DIR = "feature"

    # this folder contain data source for all docs
    DATA_DIR = "data"
    
    # this folder contain feature extraction data for all docs
    FEATURE_DIR = "feature"
    
    # suffix and extension for feature data
    FEATURE_SUFIX_EXT = '_feat.json'
        
    # extension of doc data
    DATA_EXT = ".json"
            
    CORPUS_DIR = ["dev","train","test"]
    
    # event label
    EVENT_LABEL = {"None":0,
                   "Gene_expression":1,
                   "Transcription":2,
                   "Protein_catabolism":3,
                   "Phosphorylation":4,
                   "Localization":5,
                   "Binding":6,
                   "Regulation":7,
                   "Positive_regulation":8,
                   "Negative_regulation":9}

    # filter out feature criteria
    FF_MAX_DEP_LEN = 5

    def __init__(self, source, word_dict, trigger_dict):
        """
        Extracting feature from corpus data
        """
        self.src = source
        
                
        self.DF = DependencyFeature("dep")
        self.SF = SentenceFeature("sen", word_dict, trigger_dict)
        
        # statistic
        self.sample_pos = 0
        self.sample_neg = 0
    
    def reset_statistic(self):
        self.sample_pos = 0
        self.sample_neg = 0
    
    def write_feature(self, feature_group, doc_id, data):
        path = self.src + "/" + self.FEATURE_DIR + "/" + feature_group 
        if not os.path.exists(path):
            os.makedirs(path)
        with open(path + "/" + doc_id + self.FEATURE_SUFIX_EXT, 'w') as f:
            for line in data:                
                f.write(json.dumps(line) + '\n')
        
    def extract_tp(self, o_doc):
        """
        extract Trigger-Protein theme pair
        target 
        """
        i = 1
        feature_data = []
        for i in range(0, len(o_doc.sen)):            
            #if i != 2: continue
            o_sen = o_doc.sen[i]
            tc_list = o_sen.trigger_candidate
            p_list = o_sen.protein
                        
            for tc in tc_list:                               
                for p in p_list:
                    
                    #print tc, o_sen.words[tc]["string"], "-", p, o_sen.words[p]["string"]                                        
                    feature = self.get_feature_tp(o_sen, tc, p)                    
                    info = {"doc":o_doc.doc_id, "sen":i, "t":tc, "a":p}
                    
                    label = -1
                    if not o_doc.is_test:
                        label = self.get_tp_label(o_sen, tc, p)  
                        # statistical info
                        if label == 0:
                            self.sample_neg += 1
                        else:
                            self.sample_pos += 1                      
                    
                    # filter feature                    
                    if not self.filter_feature(feature):
                        feature_data.append([info,label,feature])
                    
                    
                        
        #self.write_feature("trigger-theme", o_doc.doc_id, feature_data)
        
        return feature_data
    
    def extract_tt(self, o_doc):
        """
        extract Trigger-Trigger theme pair
        target regulation, positive regulation, and negative regulation
        """
                        
        feature_data = []
        for i in range(0, len(o_doc.sen)):       
            # to prevent duplicate pair
            pair_list = []     
            
            #if i != 2: continue
            o_sen = o_doc.sen[i]
            
            ac_list = o_sen.rel.get_tp_triger()
            tc_list = [t for t in o_sen.trigger_candidate if t not in ac_list] 
            
          
            for tc in tc_list:      
                # argument is a trigger which has relation with protein as argument1                         
                for ac in ac_list:
                    # no relation to it-self, there are few case but small   
                    if tc == ac: continue
                    pair = str(tc)+'-'+str(ac)
                    if pair in pair_list: continue
                    pair_list.append(pair)
                    
                    #print tc, o_sen.words[tc]["string"], "-", p, o_sen.words[p]["string"]                                        
                    feature = self.get_feature_tt(o_sen, tc, ac)                    
                    info = {"doc":o_doc.doc_id, "sen":i, "t" : tc, "a" : ac}
                    
                   
                    label = -1             
                    if not o_doc.is_test:
                        label = self.get_tt_label(o_sen, tc, ac)  
                        # statistical info
                        if label == 0:
                            self.sample_neg += 1
                        else:
                            self.sample_pos += 1                      
                    
                    # filter feature                    
                    if not self.filter_feature(feature):
                        feature_data.append([info,label,feature])
        
        return feature_data
    
    def filter_feature(self, feature):
        retval = False
        
        # filter dependency len between trigger-arg
        if feature['dep_word_dist'] > self.FF_MAX_DEP_LEN:
            retval = True
        
        return retval    
        
    def get_feature_tp(self, o_sen, trig_wn, arg_wn):
        
        feature = {}
        
        # add sentence feature
        self.SF.extract_feature_tp(o_sen, trig_wn, arg_wn)
        feature.update(self.SF.feature)
        
        # add dependency feature
        self.DF.extract_feature(o_sen, trig_wn, arg_wn)
        feature.update(self.DF.feature)
        
        return feature
    
    def get_feature_tt(self, o_sen, trig_wn, arg_wn):
        
        feature = {}
        
        # add sentence feature
        self.SF.extract_feature_tt(o_sen, trig_wn, arg_wn)
        feature.update(self.SF.feature)
        
        # add dependency feature
        self.DF.extract_feature(o_sen, trig_wn, arg_wn)
        feature.update(self.DF.feature)
        
        return feature
        
    def get_tp_label(self, o_sen, trig_wn, arg_wn):
        """
        Label trigger-argument relation with trigger event if there is a relation
        otherwise 0
        argument is a protein
        """
        label = 0
        
        cond1 = o_sen.rel.check_relation(trig_wn, arg_wn, "Theme", "P")
        cond2 = o_sen.rel.check_relation(trig_wn, arg_wn, "Theme2", "P")
        
        if cond1 or cond2:
            label = self.EVENT_LABEL[o_sen.words[trig_wn]["type"]]
        
        return label
    
    def get_tt_label(self, o_sen, trig_wn, arg_wn):
        """
        Label trigger-argument relation with trigger event if there is a relation
        otherwise 0
        argument is a another trigger
        """
        label = 0
        
        if o_sen.rel.check_relation(trig_wn, arg_wn, "Theme", "E"):
            label = self.EVENT_LABEL[o_sen.words[trig_wn]["type"]]
        
        return label
        
        
        
    
if __name__ == "__main__":
    
    
    
    source = "E:/corpus/bionlp2011/project_data"
    doc_id = "PMC-2222968-04-Results-03"
    #doc_id = "PMID-9351352"
    
    WD = WordDictionary(source)    
    WD.load("train")
           
    TD = TriggerDictionary(source)
    TD.load("train")
    
    builder = DocumentBuilder(source, WD, TD)            
    doc = builder.read_raw(doc_id)
    o_doc = builder.build_doc_from_raw(doc, is_test=False)
    
    FE = FeatureExtraction(source, WD, TD)
    FE.extract_tt(o_doc)
    #for f in feature[0:50]:
    #    print f[0]
    #    print f[2]