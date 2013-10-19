'''
Created on Sep 13, 2013

@author: Andresta
'''

from model.Dictionary import TriggerDictionary, WordDictionary
from model.Document import DocumentBuilder
from rule.Extraction import Extraction

class DocumentBuilderTest(object):
    '''
    classdocs
    '''


    def __init__(self, dic_corpus):
        '''
        Constructor
        '''
        self.source = "E:/corpus/bionlp2011/project_data/"        
        
        self.WD = WordDictionary(self.source)    
        self.WD.load(dic_corpus)
               
        self.TD = TriggerDictionary(self.source)
        self.TD.load(dic_corpus)
        
        self.builder = DocumentBuilder(self.source, self.WD, self.TD)
        
    def run(self):
        self.test1()
        self.test2()
        self.test3()
    
    def test1(self):
        doc_id = "PMC-2806624-03-RESULTS-02"
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
        
    def test4(self):
        learning_corpus = 'mix'
        extraction_corpus = 'dev'
        extraction = Extraction(self.source, learning_corpus, extraction_corpus)
        
        doc_id = 'PMC-2806624-03-RESULTS-02'
        o_doc = self.builder.build(doc_id, is_test = True)        
        extraction.extract_doc(o_doc, self.TD)
        
        print "Test 4: document from extraction rules"
        print "================================================="
        self.print_info(o_doc)
    
    def print_info(self, o_doc):
        print "doc id:", o_doc.doc_id
        print "is test:", o_doc.is_test
        
        
        for i in range(0, len(o_doc.sen)):
            o_sen = o_doc.sen[i]
            print "sen:", i
            print "-------------------------------"
            j= 0
            for w in o_sen.words:
                print j, w['start'], w['string'], w['pos_tag'], w['type'], w['score']
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
            print 'root', o_sen.dep.root
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
                print o_sen.rel.data 
    
    
if __name__ == "__main__":
    dic_corpus = 'train'
    test = DocumentBuilderTest(dic_corpus)
    test.test4()