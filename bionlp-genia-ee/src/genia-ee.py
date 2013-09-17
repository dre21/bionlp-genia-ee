'''
Created on Sep 16, 2013

@author: Andresta
'''

from Prediction import Prediction
from Learning import Learning

def learn_dev_train(src, dir_name):
    dict_type = 'mix'
    docs = 'mix'
    
    learning = Learning(src, dir_name, dict_type)
    
    learning.learn_tp(docs, grid_search = True)        
    learning.learn_tt(docs, grid_search = True)

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

def predict_dev(src, dir_name):
    dict_type = 'train'
    docs = 'dev'
    
    prediction = Prediction(src, dir_name, dict_type)
    
    prediction.predict(docs)


if __name__ == '__main__':
    
    source = "E:/corpus/bionlp2011/project_data"
    dir_name_eval = "test-model-001"    
    dir_name_final = "model-001"
    
    # evaluation
    learn_train(src, dir_name)
    predict_dev(source, dir_name)
    
    # final prediction
    learn_dev_train(source, dir_name)
    predict_test(source, dir_name)
    
    