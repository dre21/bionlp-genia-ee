'''
Created on Sep 10, 2013

@author: Andresta
'''
import os, json

from datetime import datetime as dt
from model.Dictionary import WordDictionary, TriggerDictionary
from model.Document import DocumentBuilder
from features.FeatureExtraction import FeatureExtraction
from classifier.Scaler import Scaler
from classifier.SVM import SVM
from sklearn.feature_extraction import DictVectorizer
from sklearn.svm import LinearSVC
from sklearn.externals import joblib


class Prediction(object):
    '''
    classdocs
    '''
    
    # suffix and extension of id file
    DOCID_SUFFIX_EXT = "_doc_ids.json"
        

    def __init__(self, source, dict_type):
        '''
        Constructor
        '''
        self.src = source
        self.dict_type = dict_type
        self.wdict = None
        self.tdict = None
        self.doc_builder = None
        self.extraction = None
        
        self.vec = DictVectorizer()
        
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
        
    
    
    def predict(self, docid_list_fname, scaler_function):
        """
        return prediction of given docid_list
        """
        X = []
        Y = []     
        info = []
          
        dt_start = dt.now()
        if not isinstance(docid_list_fname, list):
            # get list of doc ids from file
            path = self.src + '/' + docid_list_fname + self.DOCID_SUFFIX_EXT
            if not os.path.exists(path):
                raise ValueError(path + " is not exist")
            with open(path, 'r') as f: 
                doc_ids = json.loads(f.read())
        else:
            doc_ids = docid_list_fname
            
        # init feature
        print "now extracting", len(doc_ids), "docs"
        for doc_id in doc_ids:             
            o_doc = self.doc_builder.build(doc_id)
            samples = self.extraction.extract_tp(o_doc)            
            
            for sample in samples:
                X.append(sample[2])
                Y.append(sample[1])
                info.append(sample[0])
            
        print "number of generated sample data: " + str(len(X))
        print "time to extract feature", dt.now() - dt_start
                        
        
        # init svm classifier
        svm = SVM(self.src, "linear", grid_search = True, class_weight = 'auto')
        svm.load()
        
        return svm.predict(X), Y, info
        
        
        
if __name__ == "__main__":
    
    from sklearn.metrics import precision_recall_fscore_support
    
    source = "E:/corpus/bionlp2011/project_data"
    dict_type = "train"
    doc_ids = ["PMC-2222968-04-Results-03"]
    doc_ids = "dev"
    
    prediction = Prediction(source, dict_type)
    Ypred, Ytest, info = prediction.predict(doc_ids, "norm")
    
    result = precision_recall_fscore_support(Ytest, Ypred, labels = [1,2,3,4,5,6,7,8,9])
    
    print "precision"
    print result[0]
    print "recall"
    print result[1]
    print "f1-score"
    print result[2]
    print "support"
    print result[3]
    
    '''
    for i in range(0,len(info)):
        if Ypred[i] > 0 or Ytest[i] > 0:
            print info[i], Ytest[i] , Ypred[i]
    '''
    
    
    
    