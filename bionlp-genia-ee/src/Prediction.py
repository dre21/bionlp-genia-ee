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
        svm = SVM(self.src, "trig-prot", "linear", grid_search = grid_search, class_weight = 'auto')
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
        svm = SVM(self.src, "trig-prot", "linear", grid_search = grid_search, class_weight = 'auto')
        svm.load()
        
        return svm.predict(X), Y, info
        
if __name__ == "__main__":
    
    from sklearn.metrics import precision_recall_fscore_support
    
    source = "E:/corpus/bionlp2011/project_data"
    dict_type = "train"
    doc_ids = ["PMC-2222968-04-Results-03"]
    doc_ids = "dev"
    
    prediction = Prediction(source, dict_type)
    
    
    print "Trigger-Protein prediction on dev corpus\n================================"
    Ypred, Ytest, info = prediction.predict_tp(doc_ids, grid_search = True)    
    result = precision_recall_fscore_support(Ytest, Ypred, labels = [1,2,3,4,5,6,7,8,9])
    
    print "precision"
    print result[0]
    print "recall"
    print result[1]
    print "f1-score"
    print result[2]
    print "support"
    print result[3]
    
    print "\n\nTrigger-Trigger prediction on dev corpus\n================================"
    Ypred, Ytest, info = prediction.predict_tt(doc_ids, grid_search = True)
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
    
    
    
    