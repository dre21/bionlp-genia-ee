'''
Created on Sep 9, 2013

@author: Andresta
'''

from sklearn import preprocessing
from sklearn.externals import joblib

import os

class Scaler(object):
    '''
    classdocs
    '''
    
    # scaler function that can be used
    SCALER_LIST = ["minmax","stdscale","norm"]
    
    
    # directory for saving scaler object
    SCALER_DIR = "classifier/scaler"
            

    def __init__(self, source, funct_name = "norm"):
        """
        Constructor
        """
        if not funct_name in self.SCALER_LIST:
            raise TypeError("funct_name is not recognize")
        
        self._funct_name = funct_name
        
        self._funct = None
        
        self._path = source + '/' + self.SCALER_DIR + '/' + funct_name + '.json' 
    
    def get_function(self):
        return self._funct
    
    def create(self):
        name = self._funct_name
        if name == "minmax":
            self._funct = preprocessing.MinMaxScaler(copy=False)
        elif name == "stdscale":
            self._funct = preprocessing.StandardScaler(copy=False)
        elif name == "norm":
            self._funct = preprocessing.Normalizer(copy=False)
    
    def fit(self, X):
        if self._funct == None:
            raise ValueError("scaler function is not initialized, use create or load function first")
        
        # fit
        self._funct.fit(X)
        
        # save to external file
        joblib.dump(self._funct, self._path)
    
    def fit_transform(self, X):
        if self._funct == None:
            raise ValueError("scaler function is not initialized, use create or load function first")
                            
        # return transformation of X
        return self._funct.transform(X)
    
    def load(self):
        if not os.path.exists(self._path):
            raise ValueError(self._path + " does not exist")
        self._funct = joblib.load(self._path)
        
        