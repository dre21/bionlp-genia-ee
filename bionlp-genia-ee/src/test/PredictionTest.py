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
        dir_name = "test-model-01"
        dict_type = "train"

        self.label = ["Gene_expression","Transcription","Protein_catabolism","Phosphorylation","Localization","Binding","Regulation","Positive_regulation","Negative_regulation"]        
        self.prediction = Prediction(source, dir_name, dict_type)
    
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
        
        self.prediction.set_prediction_docs(doc_ids)
        Ypred, Ytest, info = self.prediction.predict_tt(grid_search = True)
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
        
    def test3(self):
        doc_ids = ["PMID-7747447", "PMID-7749985", "PMID-7759875", "PMID-7759956","PMC-1920263-04-MATERIALS_AND_METHODS-03","PMC-2222968-04-Results-03"]

        print "\n\nTrigger-Protein prediction on 6 docs from dev corpus"
        print "Print info result"
        print "========================================================="
        
        self.prediction.set_prediction_docs(doc_ids)
        Ypred, Ytest, info = self.prediction.predict_tt(grid_search = True)
        
         
        
        for i in range(0, len(Ypred)):
            if Ypred[i] > 0:
                print info[i], Ypred[i], Ytest[i]
        
        
if __name__ == "__main__":
    
    test = PredictionTest()
    test.test3()