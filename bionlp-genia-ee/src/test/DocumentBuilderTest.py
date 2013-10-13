'''
Created on Sep 13, 2013

@author: Andresta
'''

from model.Dictionary import TriggerDictionary, WordDictionary
from model.Document import DocumentBuilder

class DocumentBuilderTest(object):
    '''
    classdocs
    '''


    def __init__(self):
        '''
        Constructor
        '''
        source = "E:/corpus/bionlp2011/project_data/"
        doc_id = "PMID-2160380"
        
        WD = WordDictionary(source)    
        WD.load("train")
               
        TD = TriggerDictionary(source)
        TD.load("train")
        
        self.builder = DocumentBuilder(source, WD, TD)
        
    def run(self):
        self.test1()
        self.test2()
        self.test3()
    
    def test1(self):
        doc_id = "PMID-10352258"
        o_doc = self.builder.build(doc_id, is_test = False)
        
        print "Test 1: document from test corpus\n================================================="
        self.print_info(o_doc)
    
    def test2(self):        
        doc_id = "PMID-2083253"
        o_doc = self.builder.build(doc_id, is_test = True)
        
        print "\n\nTest 2: document from train corpus set is_test=True\n================================================="
        self.print_info(o_doc)
        
    def test3(self):        
        doc_id = "PMC-2222968-04-Results-03"
        o_doc = self.builder.build(doc_id)
        
        print "\n\nTest 3: document from dev corpus\n================================================="
        self.print_info(o_doc)
    
    def print_info(self, o_doc):
        print "doc id:", o_doc.doc_id
        print "is test:", o_doc.is_test
        
        
        for i in range(0, len(o_doc.sen)):
            o_sen = o_doc.sen[i]
            print "sen:", i
            print "-------------------------------"
            j = 0
            for w in o_sen.words:
                print j, w['string'], w['type']
                j+=1
            # list of word number which is marked as trigger candidate
            print "trigger candidate:"
            print o_sen.trigger_candidate            
            # list of protein word number
            print "protein:"
            print o_sen.protein            
            # list of trigger word number
            print "trigger:"
            print o_sen.trigger            
            # dependency
            print "dependency"
            print o_sen.dep.graph
            print o_sen.dep.pair            
            # chunk
            print "chunk"
            print o_sen.chunk.chunk_map
            print o_sen.chunk.chunk_type
            
            # tree
            
            # relation representation
            print "relation:"
            if o_sen.rel != None:
                print o_sen.rel.data.items()
    
    
if __name__ == "__main__":
    
    test = DocumentBuilderTest()
    test.test1()