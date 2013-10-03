'''
Created on Oct 3, 2013

@author: Andresta
'''
import os, json

from rule.PatternGenerator import PatternGenerator
from rule.Pattern import Pattern
from model.Dictionary import WordDictionary, TriggerDictionary
from model.Document import DocumentBuilder

class Extraction(object):
    '''
    classdocs
    '''
    
    RULE_DIR = 'rule'
    
    CORPUS_DIR = ['dev','train','mix','test']
    
    
    FILTER_FREQUENCY_MIN = 2
    
    FILTER_DISTANCE_MAX = 10

    def __init__(self, source, learning_corpus, extraction_corpus):
        '''
        Constructor
        '''        
        self.src = source
        
        self.learning_corpus = learning_corpus
        
        self.extraction_corpus = extraction_corpus
        
                
        # init pattern generator
        self.PG = PatternGenerator(source)
    
    def get_doc_list(self, cdir):
        with open(os.path.join(self.src,cdir+'_doc_ids.json'),'r') as f:
            doc_ids = json.loads(f.read())
            return doc_ids
        
    def _build_doc(self, builder, doc_id, is_test = False):                
        doc = builder.read_raw(doc_id)
        return builder.build_doc_from_raw(doc, is_test)
    
    def get_prep_word(self, o_sen, trig_wn, arg_wn):
        """
        return tuple of prepositions (string,word_number)                
        """
        o_chunk = o_sen.chunk
        preps_word = []
        trig_chk_num = o_chunk.chunk_map[trig_wn]
        arg_chk_num = o_chunk.chunk_map[arg_wn]
        for chk_num in range(trig_chk_num+1, arg_chk_num):
            prep = o_chunk.prep_chunk.get(chk_num,None)
            if prep != None:
                preps_word.append(prep)                
        
        return preps_word
    
    def extract(self, word_dict, trigger_dict, doc_ids = []):
        
        # document builder
        builder = DocumentBuilder(self.src, word_dict, trigger_dict)
        
        # load pattern data
        self.PG.load(self.learning_corpus)
        
        if doc_ids == []:
            doc_ids = self.get_doc_list(self.extraction_corpus)
            
        print 'extracting document ....'
        for doc_id in doc_ids:
            o_doc = self._build_doc(builder, doc_id)
            
            for i in range(0, len(o_doc.sen)):            
                # sentence object
                o_sen = o_doc.sen[i]
                
                # trigger candidate and arguments
                tc_list = o_sen.trigger_candidate            
                arg1_list = tc_list + o_sen.protein
                arg2_list = list(arg1_list)
                
                wct = 0
                for word in o_sen.words:
                    print wct, word['start'], word['string']
                    wct+=1
                print o_sen.entity_map
                print o_sen.trigger
                
                for tc in tc_list:
                    for arg1 in arg1_list:
                        
                        if tc == arg1: continue
                        self._extract_relation(o_sen, tc, arg1)
                                                 
                            
                            
    
    def _extract_relation(self, o_sen, tc, arg1, arg2 = -1):
        #print '_extract_relation',o_sen.number, tc, arg1, arg2
        o_chunk = o_sen.chunk        
        container = ''
        t_word = o_sen.words[tc]
        t_arg = o_sen.words[arg1]
        
        # length from trigger to argument
        dist1 = o_chunk.distance(tc, arg1)
        
        # preposition
        preps1 = self.get_prep_word(o_sen,tc, arg1)
        
        # make a pattern
        pattern = {}
        pattern[tc] = 'trg'     
        pattern[arg1] = 'arg1'
        
        """ define container type """
        # chunk layer
        if dist1 == 0:
            container = 'chunk'                                                                                
        # phrase layer, at least there is preposition 1
        elif len(preps1) == 1:
            container = 'phrase'            
            pattern[preps1[0][1]] = 'prep1'      
            prep1 = preps1[0][0]                          
        # clause layer
        else:
            container = 'clause'
        
        # build pattern type
        pattern_type = ''
        for _,v in sorted(pattern.iteritems()):
            pattern_type += v +'-'        
        pattern_type = pattern_type.rstrip('-')
        
        # build key
        key = ':'.join([t_word['string'],t_word['pos_tag'], pattern_type, container]) 
        
        # get frequency and pattern template
        template = self.PG.pattern.get(key,None)        
        if template != None:
            freq = template.freq
            if freq < self.FILTER_FREQUENCY_MIN: return
            if dist1 > max(template.dist1): return
            if container == 'phrase' and prep1 not in template.prep1: return
        
            print o_sen.number, container, pattern_type, t_word['string'], t_word['pos_tag'], tc, t_word['start'], 'arg:',arg1, 'dist:',dist1,'freq:',freq, 'p_cnt:', template.pro1_count, 'e_cnt:', template.evt1_count 
        

if __name__ == '__main__':
    
    source = "E:/corpus/bionlp2011/project_data"
    learning_corpus = 'train'
    extraction_corpus = 'test'
    
    doc_ids = ['PMID-9796963']

    WD = WordDictionary(source)    
    WD.load("mix")
           
    TD = TriggerDictionary(source)
    TD.load("mix")        

    extraction = Extraction(source, learning_corpus, extraction_corpus)
    extraction.extract(WD, TD, doc_ids)
    
        
        