'''
Created on Sep 13, 2013

@author: Andresta
'''

from Prediction import Prediction
from sklearn.metrics import precision_recall_fscore_support

class PredictionTest(object):
    '''
    classdocs
    '''


    def __init__(self):
        '''
        Constructor
        '''
        source = "E:/corpus/bionlp2011/project_data"
        dict_type = "train"

        self.label = ["Gene_expression","Transcription","Protein_catabolism","Phosphorylation","Localization","Binding","Regulation","Positive_regulation","Negative_regulation"]        
        self.prediction = Prediction(source, dict_type)
    
    def run(self):
        self.test1()
        self.test2()
        
    def test1(self):
        doc_ids = "dev"
        
        print "Test 1: Trigger-Protein prediction on dev corpus"
        print "Print precision recall and f1 score for each class"
        print "========================================================="
        
        Ypred, Ytest, info = self.prediction.predict_tp(doc_ids, grid_search = True)    
        result = precision_recall_fscore_support(Ytest, Ypred, labels = [1,2,3,4,5,6,7,8,9])
        
        print self.label
        print "precision"
        print result[0]
        print "recall"
        print result[1]
        print "f1-score"
        print result[2]
        print "support"
        print result[3]
        
    def test2(self):
        doc_ids = "dev"
        
        print "\n\nTrigger-Trigger prediction on dev corpus"
        print "Print precision recall and f1 score for each class"
        print "========================================================="
        
        Ypred, Ytest, info = self.prediction.predict_tt(doc_ids, grid_search = True)
        result = precision_recall_fscore_support(Ytest, Ypred, labels = [7,8,9])
        
        print self.label[6:9]
        print "precision"
        print result[0]
        print "recall"
        print result[1]
        print "f1-score"
        print result[2]
        print "support"
        print result[3]
        
        
if __name__ == "__main__":
    
    test = PredictionTest()
    test.run()