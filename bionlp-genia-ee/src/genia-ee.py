'''
Created on Sep 16, 2013

@author: Andresta
'''

from Prediction import Prediction
from Learning import Learning
from sklearn.metrics import precision_recall_fscore_support


def learn_dev_train(src, dir_name):
    dict_type = 'mix'
    docs = 'mix'
    
    learning = Learning(src, dir_name, dict_type)
    
    learning.learn_tp(docs, grid_search = True)        
    learning.learn_tt(docs, grid_search = True)
    learning.learn_tc(docs, grid_search = True)
    learning.learn_t2(docs, grid_search = True)

def predict_test(src, dir_name):
    dict_type = 'mix'
    docs = 'test'
    
    prediction = Prediction(src, dir_name, dict_type)
    
    prediction.predict(docs)

def learn_train(src, dir_name):
    dict_type = 'train'
    docs = 'train'
    
    learning = Learning(src, dir_name, dict_type)
    
    learning.learn_tp(docs, grid_search = True)        
    learning.learn_tt(docs, grid_search = True)
    learning.learn_tc(docs, grid_search = True)
    learning.learn_t2(docs, grid_search = True)

def predict_dev(src, dir_name):
    dict_type = 'train'
    docs = 'dev'
    
    """ ----- print validation score for each step ----- """
    validation = Prediction(src, dir_name, dict_type)
    
    # validation score for tp    
    validation.set_prediction_docs(docs, is_test = False)
    Ypred,Ytest,_ = validation.predict_tp(grid_search = True)
    print "Gene_expression Transcription Protein_catabolism Phosphorylation Localization Binding"
    print "Regulation Positive_regulation Negative_regulation"
    print_matrix(Ytest, Ypred, [1,2,3,4,5,6,7,8,9])
    
    # validation score for tt    
    validation.set_prediction_docs(docs, is_test = False)
    Ypred,Ytest,_ = validation.predict_tt(grid_search = True)
    print "Regulation Positive_regulation Negative_regulation"
    print_matrix(Ytest, Ypred, [7,8,9])
    
    # validation score for tc
    validation.set_prediction_docs(docs, is_test = False)
    Ypred,Ytest,_ = validation.predict_tc(grid_search = True)
    print "Trigger-Argument-Cause prediction"
    print_matrix(Ytest, Ypred, [1])
    
    # validation score for t2
    validation.set_prediction_docs(docs, is_test = False)
    Ypred,Ytest,_ = validation.predict_t2(grid_search = True)
    print "Trigger-Theme1-Theme2 prediction"
    print_matrix(Ytest, Ypred, [1])
    
    
    """ ----- make a prediction for dev corpus  ----- """
    prediction = Prediction(src, dir_name, dict_type)    
    prediction.predict(docs)


def print_matrix(Ytest, Ypred, labels = None):
    result = precision_recall_fscore_support(Ytest, Ypred, labels = labels)
    print "precision"
    print result[0]
    print "recall"
    print result[1]
    print "f1-score"
    print result[2]
    print "\n\n"

if __name__ == '__main__':
    
    source = "E:/corpus/bionlp2011/project_data"

    dir_name_eval = "test-model-021"    
    dir_name_final = "model-021"
    
    # evaluation
    learn_train(source, dir_name_eval)
    predict_dev(source, dir_name_eval)
    
    # final prediction
    learn_dev_train(source, dir_name_final)
    predict_test(source, dir_name_final)
    
    