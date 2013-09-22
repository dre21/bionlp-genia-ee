'''
Created on Sep 14, 2013

@author: Andresta
'''

from model.Dictionary import TriggerDictionary, WordDictionary
from model.Document import DocumentBuilder
from corpus.GeniaA2Writer import GeniaA2Writer
from Prediction import Prediction


class GeniaA2WriterTest(object):
    '''
    classdocs
    '''
    
    source = "E:/corpus/bionlp2011/project_data/"

    def __init__(self):
        '''
        Constructor
        '''
        '''
        Constructor
        '''
               
        out_path = "E:/corpus/bionlp2011/project_test/result/model1" 
        
        WD = WordDictionary(self.source)    
        WD.load("train")
               
        TD = TriggerDictionary(self.source)
        TD.load("train")
        
        self.builder = DocumentBuilder(self.source, WD, TD)
        self.a2writter = GeniaA2Writer(out_path)
    
    def test1(self):
        doc_id = 'PMC-2222968-04-Results-03'
        o_doc = self.builder.build(doc_id)
        
        self.a2writter.write(o_doc)
        
    def test2(self):
        dir_name_eval = "test-model-002-cause"    
        doc_ids = ['PMC-2222968-04-Results-03']
        dict_type = 'train'
        
        prediction = Prediction(self.source, dir_name_eval, dict_type)    
        prediction.predict(doc_ids)
        
        o_doc = prediction.docs[doc_ids[0]]
        for sen in o_doc.sen:
            sen.test()
        self.a2writter.write(o_doc)
        
if __name__ == "__main__":
    
    test = GeniaA2WriterTest()
    test.test2()