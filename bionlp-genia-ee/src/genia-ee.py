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


def predict_dev(src, dir_name):
    dict_type = 'train'
    docs = 'dev'
    
    prediction = Prediction(src, dir_name, dict_type)
    
    prediction.predict(docs)


if __name__ == '__main__':
    
    source = "E:/corpus/bionlp2011/project_data"
    dir_name = "model-001"    
    
    learn_dev_train(source, dir_name)
    
    #predict_dev(source, dir_name, dict_type)