'''
Created on Sep 14, 2013

@author: Andresta
'''

from model.Dictionary import TriggerDictionary, WordDictionary
from model.Document import DocumentBuilder
from corpus.GeniaA2Writer import GeniaA2Writer



class GeniaA2WriterTest(object):
    '''
    classdocs
    '''
    

    def __init__(self):
        '''
        Constructor
        '''
        '''
        Constructor
        '''
        source = "E:/corpus/bionlp2011/project_data/"        
        
        WD = WordDictionary(source)    
        WD.load("train")
               
        TD = TriggerDictionary(source)
        TD.load("train")
        
        self.builder = DocumentBuilder(source, WD, TD)
        self.a2writter = GeniaA2Writer('')
    
    def test1(self):
        doc_id = 'PMC-2222968-04-Results-03'
        o_doc = self.builder.build(doc_id)
        
        self.a2writter.write(o_doc)
        
        
if __name__ == "__main__":
    
    test = GeniaA2WriterTest()
    test.test1()