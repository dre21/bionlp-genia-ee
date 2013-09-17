'''
Created on Sep 10, 2013

@author: Andresta
'''

import os
from Prediction import Prediction
from Learning import Learning
from sklearn.metrics import precision_recall_fscore_support
from classifier.SVM import SVM


class SVMTest(object):
    '''
    classdocs
    '''

    def __init__(self, source):
        '''
        Constructor
        '''
        self.src = source
        self.dir_name = "testing"
        self.dict_type = "train"

    
    def learn(self, tp = True, tt = True, tc = True):
        
        learning_docs = 'train'
        
        # delete temporary dir if exist
        path = self.src + '/model/' + self.dir_name
        self.delete_dir(path)
        
        learning = Learning(self.src, self.dir_name, self.dict_type)
        
        if tp:
            learning.learn_tp(learning_docs, grid_search = True)
            
        if tt:
            learning.learn_tt(learning_docs, grid_search = True)
            
        if tc:
            learning.learn_tc(learning_docs, grid_search = True)
            
    
    def check_tp(self):
               
        valid_docs = 'dev'
                
        # validation
        validation = Prediction(self.src, self.dir_name, self.dict_type)
        validation.set_prediction_docs(valid_docs, is_test = False)
        Ypred,Ytest,_ = validation.predict_tp(grid_search = True)
        
        # print result
        print "\n\n====================================================================================="
        print "Gene_expression Transcription Protein_catabolism Phosphorylation Localization Binding"
        print "Regulation Positive_regulation Negative_regulation\n"
        self.print_matrix(Ytest, Ypred, [1,2,3,4,5,6,7,8,9])
        
    def check_tt(self):
               
        valid_docs = 'dev'
                
        # validation
        validation = Prediction(self.src, self.dir_name, self.dict_type)
        validation.set_prediction_docs(valid_docs, is_test = False)
        Ypred,Ytest,_ = validation.predict_tt(grid_search = True)
        
        # print result
        print "\n\n====================================================================================="        
        print "Regulation Positive_regulation Negative_regulation\n"
        self.print_matrix(Ytest, Ypred, [7,8,9])
    
    def check_tc(self):
               
        valid_docs = 'dev'
                
        # validation
        validation = Prediction(self.src, self.dir_name, self.dict_type)
        validation.set_prediction_docs(valid_docs, is_test = False)
        Ypred,Ytest,_ = validation.predict_tc(grid_search = True)
        
        # print result
        print "\n\n====================================================================================="
        print "Cause prediction"
        self.print_matrix(Ytest, Ypred, [1])
    
    def delete_dir(self, folder):
        if not os.path.exists(folder): return
                    
        for f in os.listdir(folder):
            os.unlink(os.path.join(folder,f))
        os.removedirs(folder)
    
    
    def print_matrix(self, Ytest, Ypred, labels = None):
        result = precision_recall_fscore_support(Ytest, Ypred, labels = labels)
        print "precision"
        print result[0]
        print "recall"
        print result[1]
        print "f1-score"
        print result[2]
        
        
if __name__ == "__main__":
    
    source = "E:/corpus/bionlp2011/project_data"
    test = SVMTest(source)
    test.learn()
    test.check_tp()
    test.check_tt()
    test.check_tc()