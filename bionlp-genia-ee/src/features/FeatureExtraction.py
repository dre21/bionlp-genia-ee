"""
Created on Sep 4, 2013

@author: Andresta
"""
from features.DependencyFeature import DependencyFeature
from features.SentenceFeature import SentenceFeature

class FeatureExtraction(object):
    """
    classdocs
    """
    # this is a folder to store all features data
    FEATURE_DIR = "feature"

    # this folder contain data source for all docs
    DATA_DIR = "data"
    
    # suffix and extension for feature data
    DOCID_SUFIX_EXT = '_feat.json'
        
    # extension of doc data
    DATA_EXT = ".json"
            
    CORPUS_DIR = ["dev","train","test"]
    
    


    def __init__(self, source):
        """
        Extracting feature from corpus data
        """
        self.src = source
        
        self.DF = DependencyFeature("dep")
        self.SF = SentenceFeature("sen")
    
        
    def extract_tt(self, o_doc):
        """
        extract Trigger-Theme pair
        target 
        """
        i = 1
        for i in range(0, len(o_doc.sen)):
            if i != 2: continue
            o_sen = o_doc.sen[i]
            tc_list = o_sen.trigger_candidate
            p_list = o_sen.protein
                        
            for tc in tc_list:
                for p in p_list:                    
                    feature = self.get_feature(o_sen, tc, p)
                    print tc, o_sen.words[tc]["string"], "-", p, o_sen.words[p]["string"]
                    print feature
                    print
                    
    
    def get_feature(self, o_sen, trig_wn, arg_wn):
        
        feature = {}
        
        # add sentence feature
        self.SF.extract_feature(o_sen, trig_wn, arg_wn)
        feature.update(self.SF.feature)
        
        # add dependency feature
        self.DF.extract_feature(o_sen, trig_wn, arg_wn)
        feature.update(self.DF.feature)
        
        return feature
        
        
    
if __name__ == "__main__":
    
    from model.Dictionary import WordDictionary, TriggerDictionary
    from model.Document import DocumentBuilder
    
    source = "E:/corpus/bionlp2011/project_data/"
    doc_id = "PMC-2222968-04-Results-03"
    
    WD = WordDictionary(source)    
    WD.load("train")
           
    TD = TriggerDictionary(source)
    TD.load("train")
    
    builder = DocumentBuilder(source, WD, TD)            
    doc = builder.read_raw(doc_id)
    o_doc = builder.build_doc_from_raw(doc)
    
    FE = FeatureExtraction(source)
    FE.extract_tt(o_doc)