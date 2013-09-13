'''
Created on Sep 8, 2013

@author: Andresta
'''

import os

from sklearn.grid_search import GridSearchCV
from sklearn.svm import SVC
from sklearn.svm import LinearSVC
from sklearn.externals import joblib
from sklearn.feature_extraction import DictVectorizer

from datetime import datetime as dt 

from classifier.Scaler import Scaler

class SVM(object):
    '''
    classdocs
    '''

    SVM_CLASS = ["svc", "linear"]        
    
    DEFAULT_C_VALUES = [0.1,1.0,10,100,100]
    
    DEFAULT_GAMMA_VALUES = [1e-2, 1e-3, 1e-4]
    
    DEFAULT_SCORING = 'f1'        
    
    CACHE_SIZE = 2048
    
    CROSS_VALIDATION = 5

    def __init__(self, path, prefix, svm_class, grid_search = True, class_weight = None, scaler_type = 'norm', kernel_list = ["linear"], C = [], gamma = []):
        '''
        Constructor
        '''        
        if not svm_class in self.SVM_CLASS:
            raise TypeError("svm_class is not recognize")
        
        self.grid_search = grid_search
        
        self._svm_class = svm_class
        
        self.class_weight = class_weight
        
        self.scaler_type = scaler_type
        
        self._svm = None
        
        self._vec = None         
        
        self._scaler = Scaler(path, scaler_type)                       
        
        self._svm_path = ""
        
        self._vec_path = ""
        
        self.tuned_params = self.build_param(kernel_list, C, gamma)
         
        self.set_path(path, prefix, svm_class, grid_search)
    
    
    def set_path(self, path, prefix, svm_class, grid_search):
        path = path + '/'+ prefix + '_'
                
        # set vec path
        self._vec_path = path + 'dict_vectorizer.vec'  
        
        # set svm path
        path += svm_class 
        if grid_search:
            path += '_gs'
        
        self._svm_path = path + '.model' 
            
    def build_param(self, kernels, C, gamma):
        
        params = []
        
        if C == []:
            C = self.DEFAULT_C_VALUES
        if gamma == []:
            gamma = self.DEFAULT_GAMMA_VALUES
        
        
        if "linear" in kernels:
            param = {'C': C}
            params.append(param)
    
        # only for non linear svm
        if self._svm_class != "linear":
            if "rbf" in kernels:
                param = {'kernel' : ['rbf'], 'C': C, 'gamma': gamma}
                params.append(param)
        
        if params == []:
            raise ValueError("no param has been set. change kernels and svm class accordingly to generate correct param")
        return params
        
    def create(self):
        estimator = None
        
        # create svm
        if self._svm_class == "svc":
            estimator = SVC(C=1.0, kernel='linear', class_weight = self.class_weight , cache_size = self.CACHE_SIZE)
        elif self._svm_class == "linear":
            estimator = LinearSVC(C=1.0, class_weight = self.class_weight)     
        
        if self.grid_search:
            self._svm =   GridSearchCV(estimator, self.tuned_params, cv = self.CROSS_VALIDATION, scoring = self.DEFAULT_SCORING)
        else:
            self._svm = estimator
            
            
        # create vectorizer
        self._vec = DictVectorizer()
        
        # create scaler
        self._scaler.create()
        
      
    def learn(self, Xtrain, Ytrain):
        if self._svm == None:
            raise ValueError("svm class is not initialized, call create() first")
        
        # vectorize and scale training data
        Xtrain = self.vectorize_scale(Xtrain, fit = True)
        
        # train classifier        
        dt_start = dt.now()
        print "training svm classifier"
        print self._svm        
        print "learning...."
        self._svm.fit(Xtrain, Ytrain)
        
        # save to external file        
        joblib.dump(self._svm, self._svm_path)
        
        print "time for training: ", dt.now() - dt_start
    
    def vectorize_scale(self, X, fit = True):
        
        dt_start = dt.now()        
        
        if fit:
            # fitting vector with data, only used during training
            print "Learn a list of feature name -> indices mappings"
            self._vec.fit(X)
                    
        # converting feature X into vector
        print "Transform feature->value dicts to array or sparse matrix"
        X = self._vec.transform(X)
        print "dim X:", X.shape        
        # save vectorizer for used in prediction
        joblib.dump(self._vec, self._vec_path)
                
        print "scaling feature"
        # fit
        if fit:
            self._scaler.fit(X)             
        # transform
        X = self._scaler.transform(X)
        print "time for feature conversion & scaling: ", dt.now() - dt_start
        
        return X
    
    def predict(self, Xtest):
        if self._svm == None:
            raise ValueError("svm class is not initialized, call load() first")
        
        print "predicting using svm classifier"
        print self._svm
        
        # vectorize without fit and scale training data
        Xtest = self.vectorize_scale(Xtest, fit = False)
        
        # predicting
        print "predicting X"        
        return self._svm.predict(Xtest)
        
    
    def load(self):
        """
        load svm object model        
        """
        if not os.path.exists(self._svm_path):
            raise ValueError(self._svm_path + " does not exist")
        
        if not os.path.exists(self._vec_path):
            raise ValueError(self._vec_path + " does not exist")
                
        self._svm = joblib.load(self._svm_path)
        self._vec = joblib.load(self._vec_path)
        self._scaler.load()
        