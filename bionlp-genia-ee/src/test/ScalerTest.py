'''
Created on Sep 9, 2013

@author: Andresta
'''

from classifier.Scaler import Scaler
from sklearn import datasets

class ScalerTest(object):
    '''
    classdocs
    '''


    def __init__(self, source):
        '''
        Constructor
        '''
        self.source = source
        
        
    def test_minmax(self):
        # load iris
        iris = datasets.load_iris()
                
        # init scaler 1 by create
        min_max_scaler1 = Scaler(self.source, "minmax")
        min_max_scaler1.create()
        print "scaler 1 by create"
        print min_max_scaler1
        
        # fit transform
        print "fit and transform iris dataset", iris.data.shape      
        iris_scale = min_max_scaler1.fit_transform(iris.data)
        scaler1_min = min_max_scaler1.get_function().min_
        scaler1_scale = min_max_scaler1.get_function().scale_
        print "min_", scaler1_min
        print "scale_", scaler1_scale
        
        # init scaler 2 by load
        min_max_scaler2 = Scaler(source, "minmax")
        min_max_scaler2.load()
        print "scaler 2 by load"
        print min_max_scaler2
        
        # fit transform using scaler 2
        print "min of scaler1 and scaler2 are the same: ", scaler1_min == min_max_scaler2.get_function().min_
        print "scale of scaler1 and scaler2 are the same: ", scaler1_scale == min_max_scaler2.get_function().scale_
        
if __name__ == "__main__":
    
    source = "E:/corpus/bionlp2011/project_test"
    test = ScalerTest(source)
    test.test_minmax()
        
