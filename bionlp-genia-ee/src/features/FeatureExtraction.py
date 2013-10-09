"""
Created on Sep 4, 2013

@author: Andresta
"""

import json, os
from features.DependencyFeature import DependencyFeature
from features.SentenceFeature import SentenceFeature
from features.ChunkFeature import ChunkFeature
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
    EVENT_LABEL = {"null":0,
                   "Gene_expression":1,
                   "Transcription":2,
                   "Protein_catabolism":3,
                   "Phosphorylation":4,
                   "Localization":5,
                   "Binding":6,
                   "Regulation":7,
                   "Positive_regulation":8,
                   "Negative_regulation":9}
    
    # regulation list
    REGULATION_EVENT = ['Regulation','Positive_regulation','Negative_regulation']

    # filter out feature criteria
    FF_MAX_DEP_DIST = 5
    
    FF_MAX_CHK_DIST = 10
    
    FF_MAX_WORD_DIST = 15
    

    def __init__(self, source, word_dict, trigger_dict):
        """
        Extracting feature from corpus data
        """
        self.src = source
        
        # feature extraction
        self.DF = DependencyFeature("dep")
        self.SF = SentenceFeature("sen", word_dict, trigger_dict)
        self.CF = ChunkFeature('chk')
        
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
      
    def filter_feature(self, feature):
        retval = False
        
        # filter dependency len between trigger-arg
        if feature.get('dep_dist',0) > self.FF_MAX_DEP_DIST:
            retval = True
                
        elif feature.get('chk_dist',0) > self.FF_MAX_CHK_DIST:
            retval = True
            
        #elif feature.get('sen_dist',0) > self.FF_MAX_WORD_DIST:
        #    retval = True
        
        return retval  
        
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
            
            ac_list = o_sen.rel.get_tptt_triger()
            tc_list = [t for t in o_sen.trigger_candidate if t not in o_sen.rel.get_tp_triger()] 
            
          
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
                
    def extract_tc(self, o_doc):
        """
        Extract feature for trigger-cause relation
        trigger type is Regulation, Positive regulation or Negative regulation
        """
        # to prevent duplicate pair
        pair_list = []
        
        feature_data = []
        
        for i in range(0, len(o_doc.sen)):            
            # get sentence
            o_sen = o_doc.sen[i]            
            
            # trigger candidates are trigger with regulation event
            tc_list = list(o_sen.trigger_candidate)
            for wn in o_sen.trigger_candidate:
                if o_sen.words[wn]["type"] not in self.REGULATION_EVENT:                    
                    tc_list.remove(wn)
            
            # list of protein that have been used, these will be exclude from cause candidate
            prot_used = o_sen.rel.get_theme(o_sen.rel.get_tp_triger())
            pc_list = [p for p in o_sen.protein if p not in prot_used]
            
            # list of trigger that have been used by tt, these will be exclude from cause candidate
            trig_used = o_sen.rel.get_theme(tc_list)
            tp_list = [t for t in o_sen.rel.get_tp_triger() if t not in trig_used]
                                                                                                                                
            # cause candidates are protein and trigger which has relation with protein as argument1 
            cc_list = set(pc_list + tp_list + tc_list)
            
                        
            
            # for each tc
            for tc in tc_list:                
                # for each arg1 of tc 
                for ac in o_sen.rel.get_theme(tc):
                    # for each cause candidate                                     
                    for cc in cc_list:
                        
                        # no relation to it-self   
                        if tc == cc: continue
                        # no same relation to theme and cause
                        if ac == cc: continue
                        # if ac and cc already have connection each other
                        if o_sen.rel.check_relation(cc, tc, "Theme", "E"): continue
                        
                                                
                        
                        feature = self.get_feature_tac(o_sen, tc, ac, cc)                    
                        info = {'doc':o_doc.doc_id, 'sen':i, 't':tc, 'a':ac, 'c':cc}
                                                       
                        label = 0             
                        if not o_doc.is_test:
                            label = self.get_tac_label(o_sen, tc, ac, cc)  
                            # statistical info
                            if label == 0:
                                self.sample_neg += 1
                            else:
                                self.sample_pos += 1                      
                        
                        # filter feature                    
                        if not self.filter_feature(feature):
                            feature_data.append([info,label,feature])
                                                     
        
        return feature_data
    
    def extract_t2(self, o_doc):
        """
        extract feature for binding theme-theme2 relation
        trigger type is only binding
        """
        feature_data = []
        
        # store pair of theme1-theme2 that have been executed
        # to prevent duplicate extraction
        # ex trigger-arg1-arg2  8-7-6 is equal to 8-6-7, only execute once
        pair = []
        
        for i in range(0, len(o_doc.sen)):            
            # get sentence
            o_sen = o_doc.sen[i]          
                                                
            # trigger candidates are trigger with binding event
            tc_list = list(o_sen.trigger_candidate)
            for wn in o_sen.trigger_candidate:
                if o_sen.words[wn]["type"] != 'Binding':                    
                    tc_list.remove(wn)
                    
            # get arguments for all binding event
            ac_list = o_sen.rel.get_theme(tc_list)
            
            for tc in tc_list:
                for ac1 in ac_list:
                    for ac2 in ac_list:

                        if ac1 == ac2: continue
                        # binding relation trigger-theme must be exist
                        if not o_sen.rel.check_pair(tc, ac1): continue                        
                        if str(tc)+'-'+str(ac2)+'-'+str(ac1) in pair: continue
                        # flip position                        
                        pair.append(str(tc)+'-'+str(ac1)+'-'+str(ac2))
                                                
                        feature = self.get_feature_t2(o_sen, tc, ac1, ac2)                    
                        info = {'doc':o_doc.doc_id, 'sen':i, 't':tc, 'a1':ac1, 'a2':ac2}
                        
                        label = 0
                        if not o_doc.is_test:
                            label = self.get_t2_label(o_sen, tc, ac1, ac2)
                            # statistical info
                            if label == 0:
                                self.sample_neg += 1
                            else:
                                self.sample_pos += 1     
                        
                        # filter feature                    
                        if not self.filter_feature(feature):                        
                            feature_data.append([info,label,feature])
                          
        return feature_data      
    
    def extract_evt(self, o_doc):
        """
        extract simple event (trigger-theme) relation 
        """
        i = 1
        feature_data = []
        for i in range(0, len(o_doc.sen)):            

            o_sen = o_doc.sen[i]
            tc_list = o_sen.trigger_candidate
            p_list = o_sen.protein
                        
            for tc in tc_list:                               
                for p in p_list:
                                                           
                    feature = self.get_feature_tp(o_sen, tc, p)                    
                    info = {"doc":o_doc.doc_id, "sen":i, "t":tc, "a":p}
                    
                    label = -1
                    if not o_doc.is_test:
                        label = self.get_evt_label(o_sen, tc, p)  
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
    
    
    def get_feature_tp(self, o_sen, trig_wn, arg_wn):
        
        feature = {}
        
        # add sentence feature
        self.SF.extract_feature_tp(o_sen, trig_wn, arg_wn)
        feature.update(self.SF.feature)
        
        # add dependency feature
        self.DF.extract_feature_tp(o_sen, trig_wn, arg_wn)
        feature.update(self.DF.feature)
        
        # add chunk feature
        self.CF.extract_feature_tp(o_sen, trig_wn, arg_wn)
        feature.update(self.CF.feature)
        
        return feature
    
    def get_feature_tt(self, o_sen, trig_wn, arg_wn):
        
        feature = {}
        
        # add sentence feature
        self.SF.extract_feature_tt(o_sen, trig_wn, arg_wn)
        feature.update(self.SF.feature)
        
        # add dependency feature
        self.DF.extract_feature_tt(o_sen, trig_wn, arg_wn)
        feature.update(self.DF.feature)
        
        # add chunk feature
        self.CF.extract_feature_tt(o_sen, trig_wn, arg_wn)
        feature.update(self.CF.feature)
        
        return feature
        
    def get_feature_tac(self, o_sen, trig_wn, theme_wn, cause_wn):
        """
        get feature for trigger-theme-cause relation
        input are trigger, theme, and cause word number
        """
        feature = {}
        
        # add sentence feature
        self.SF.extract_feature_tac(o_sen, trig_wn, theme_wn, cause_wn)
        feature.update(self.SF.feature)
        
        # add dependency feature
        self.DF.extract_feature_tac(o_sen, trig_wn, theme_wn, cause_wn)
        feature.update(self.DF.feature)
        
        # add chunk feature
        self.CF.extract_feature_tac(o_sen, trig_wn, theme_wn, cause_wn)
        feature.update(self.CF.feature)
        
        
        return feature
        
    def get_feature_t2(self, o_sen, trig_wn, theme1_wn, theme2_wn):
        """
        get feature for binding trigger-theme1-theme2 relation
        input are trigger, theme1, and theme2 word number
        """
        feature = {}
        
        # add sentence feature
        self.SF.extract_feature_t2(o_sen, trig_wn, theme1_wn, theme2_wn)
        feature.update(self.SF.feature)
        
        # add dependency feature
        self.DF.extract_feature_t2(o_sen, trig_wn, theme1_wn, theme2_wn)
        feature.update(self.DF.feature)
        
        # add chunk feature
        self.CF.extract_feature_t2(o_sen, trig_wn, theme1_wn, theme2_wn)
        feature.update(self.CF.feature)
        
        return feature
        
    def get_feature_evt(self, o_sen, trig_wn, arg_wn):
        """
        get features for simple event
        """
        feature = {}
        
        # add sentence feature
        self.SF.extract_feature_evt(o_sen, trig_wn, arg_wn)
        feature.update(self.SF.feature)
        
        # add dependency feature
        self.DF.extract_feature_evt(o_sen, trig_wn, arg_wn)
        feature.update(self.DF.feature)
        
        # add chunk feature
        self.CF.extract_feature_evt(o_sen, trig_wn, arg_wn)
        feature.update(self.CF.feature)
        
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
        
    def get_tac_label(self, o_sen, trig_wn, arg_wn, cause_wn):
        """
        binary label whether there is relation for trigger-theme1-cause
        """ 
        label = 0
        
        cond1 = o_sen.rel.check_relation(trig_wn, arg_wn, "Theme", "P")
        cond2 = o_sen.rel.check_relation(trig_wn, arg_wn, "Theme", "E")
        cond3 = o_sen.rel.check_relation(trig_wn, cause_wn, "Cause", "P")
        cond4 = o_sen.rel.check_relation(trig_wn, cause_wn, "Cause", "E")
        
        if (cond1 or cond2) and (cond3 or cond4):
            label = 1
        
        return label
        
    def get_t2_label(self, o_sen, trig_wn, arg1_wn, arg2_wn):
        """
        binary label whether there is relation for trigger-theme1-theme2
        """ 
        label = 0
        
        cond1 = o_sen.rel.check_relation(trig_wn, arg1_wn, "Theme", "P")
        cond2 = o_sen.rel.check_relation(trig_wn, arg2_wn, "Theme2", "P")
        cond3 = o_sen.rel.check_relation(trig_wn, arg1_wn, "Theme2", "P")
        cond4 = o_sen.rel.check_relation(trig_wn, arg2_wn, "Theme", "P")
        if (cond1 and cond2) or (cond3 and cond4):
            label = 1
            
        return label
    
    def get_evt_label(self,o_sen, trig_wn, arg_wn):
        """
        label for simple event [Gene_expression, Transcription, Protein_catabolism, Phosphorylation, Localization]
        """
        label = 0
        
        if o_sen.rel.check_relation(trig_wn, arg_wn, "Theme", "P"):
            label = self.EVENT_LABEL[o_sen.words[trig_wn]["type"]]
            # only label for 1 to 5
            if label > 5:
                label = 0
                
        return label
    
if __name__ == "__main__":
    
    
    
    source = "E:/corpus/bionlp2011/project_data"
    doc_id = "PMID-10080948"
    #doc_id = "PMID-9351352"
    
    WD = WordDictionary(source)    
    WD.load("train")
           
    TD = TriggerDictionary(source)
    TD.load("train")
    
    builder = DocumentBuilder(source, WD, TD)            
    doc = builder.read_raw(doc_id)

    o_doc = builder.build_doc_from_raw(doc, is_test=False)
    
    FE = FeatureExtraction(source, WD, TD)
    feature = FE.extract_evt(o_doc)
    for f in feature[0:50]:
        print f[0], f[1]
        print f[2]
    