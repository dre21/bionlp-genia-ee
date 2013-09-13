'''
Created on Sep 10, 2013

@author: Andresta
'''
import os, json

from datetime import datetime as dt
from model.Dictionary import WordDictionary, TriggerDictionary
from model.Document import DocumentBuilder
from features.FeatureExtraction import FeatureExtraction
from classifier.SVM import SVM


class Prediction(object):
    '''
    classdocs
    '''
    
    # suffix and extension of id file
    DOCID_SUFFIX_EXT = "_doc_ids.json"
    
    # directory for saving svm model
    MODEL_DIR = "/model"
        

    def __init__(self, source, dir_name, dict_type):
        '''
        Constructor
        '''
        self.src = source
        self.path = self.get_path(source, dir_name)
        
        self.dict_type = dict_type
        self.wdict = None
        self.tdict = None
        self.doc_builder = None
        self.extraction = None                
        
        self._set(dict_type)
    
    def _set(self, dict_type):
        """
        initialize dictionary type to be used in feature extraction process
        initialize document builder
        initialize feature extraction
        """       
        
        self.wdict = WordDictionary(self.src)    
        self.wdict.load(dict_type)
               
        self.tdict = TriggerDictionary(self.src)
        self.tdict.load(dict_type)
        
        self.doc_builder = DocumentBuilder(self.src, self.wdict, self.tdict)         
        self.extraction = FeatureExtraction(self.src, self.wdict, self.tdict)
        
        
    def get_path(self, source, dir_name):
        """
        check whether given dir_name is exist
        raise error if it does not exist
        return full path of dir_name
        """
        path = source + self.MODEL_DIR + '/' + dir_name
        if not os.path.exists(path):
            raise ValueError(path + "exist!!, chose anoher dir_name for learning")
        
        return path
        
    def get_feature(self, doc_ids, step):
        """
        extract feature and return X, Y for a given step
        step are either one of these:
        'tp' => trigger-protein relation
        'tt' => trigger-trigger relation to predict regulation event with trigger argument  
        """
        if step not in ["tt","tp"]:
            raise ValueError("only support step for tt and tp")
        
        X = []
        Y = []
        info = []
        
        dt_start = dt.now()        
        
        # reset statistic of extraction
        self.extraction.reset_statistic()
                      
        # init feature
        print "now extracting", len(doc_ids), "docs"
        for doc_id in doc_ids:             
            o_doc = self.doc_builder.build(doc_id)
            if step == 'tp':
                samples = self.extraction.extract_tp(o_doc)
            elif step == 'tt':
                samples = self.extraction.extract_tt(o_doc)
            
            for sample in samples:
                X.append(sample[2])
                Y.append(sample[1])      
                info.append(sample[0])             
        
        # print statistic
        pos = self.extraction.sample_pos
        neg = self.extraction.sample_neg
        stat = (pos, neg, pos + neg)
        print stat
        print "percentege of positif data:", pos * 100.0 / (pos + neg)        
        print "time to extract feature", dt.now() - dt_start
        
        return X,Y, info
    
    def get_docid_list(self, docid_list_fname):
        """
        return list of file
        """
        if not isinstance(docid_list_fname, list):
            # get list of doc ids from file
            path = self.src + '/' + docid_list_fname + self.DOCID_SUFFIX_EXT
            if not os.path.exists(path):
                raise ValueError(path + " is not exist")
            with open(path, 'r') as f: 
                doc_ids = json.loads(f.read())
        else:
            doc_ids = docid_list_fname
        
        return doc_ids
    
    def predict_tp(self, docid_list_fname, grid_search):
        """
        return prediction of given docid_list
        """
        # get list of file
        doc_ids = self.get_docid_list(docid_list_fname)
        
        # get features and target
        X, Y, info = self.get_feature(doc_ids, 'tp')
        
        # init svm classifier
        svm = SVM(self.path, "trig-prot", "linear", grid_search = grid_search, class_weight = 'auto')
        svm.load()
        
        return svm.predict(X), Y, info
        
    def predict_tt(self, docid_list_fname, grid_search):
        """
        return prediction of given docid_list
        """
        # get list of file
        doc_ids = self.get_docid_list(docid_list_fname)
        
        # get features and target
        X, Y, info = self.get_feature(doc_ids, 'tt')
        
        # init svm classifier
        svm = SVM(self.path, "trig-trig", "linear", grid_search = grid_search, class_weight = 'auto')
        svm.load()
        
        return svm.predict(X), Y, info
        
