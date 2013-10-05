'''
Created on Oct 3, 2013

@author: Andresta
'''
import os, json
from collections import defaultdict
from rule.PatternGenerator import PatternGenerator
from rule.Pattern import TemplatePattern, ExtractionPattern
from model.Dictionary import WordDictionary, TriggerDictionary
from model.Document import DocumentBuilder
from corpus.GeniaA2Writer import GeniaA2Writer as A2Writter

class Extraction(object):
    '''
    classdocs
    '''
    
    RULE_DIR = 'rule'
    
    CORPUS_DIR = ['dev','train','mix','test']
    
    EVENT_LABEL = ["Gene_expression",
                   "Transcription",
                   "Protein_catabolism",
                   "Phosphorylation",
                   "Localization",
                   "Binding",
                   "Regulation",
                   "Positive_regulation",
                   "Negative_regulation"]
    
    COMMON_PATTERN_TYPE = ['trg-arg1',
                           'arg2-trg-arg1',
                           'arg1-trg',
                           'trg-prep1-arg1',
                           'trg-prep1-arg1-prep2-arg2',
                           'trg-prep2-arg2-prep1-arg1',
                           'arg2-trg-prep1-arg1',
                           'arg1-arg2-trg',
                           'arg1-trg',
                           'trg-arg1',
                           'arg2-trg-arg1',
                           'arg1-trg-arg2']
    
    # directory for saving output a2 file
    OUT_DIR = "/result"
        
    FILTER_FREQUENCY_MIN = 2
    
    FILTER_DISTANCE_MAX = 10

    def __init__(self, source, learning_corpus, extraction_corpus, dir_name):
        '''
        Constructor
        '''        
        self.src = source
        
        self.learning_corpus = learning_corpus
        
        self.extraction_corpus = extraction_corpus
                                
        # init pattern generator
        self.PG = PatternGenerator(source)
        
        # init a2 writer        
        self.a2 = A2Writter(self.get_out_path(dir_name))
    
    def get_out_path(self, dir_name):
        path = os.path.join(source + self.OUT_DIR,dir_name)
        if not os.path.exists(path):
            os.makedirs(path)        
        return path 
    
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
            #for i in range(0, 5):
                # sentence object
                o_sen = o_doc.sen[i]
                # skip sentence without protein
                if o_sen.protein == []: continue
                
                # patterns which are extracted from a sentence
                extraction_pattern = []         
                
                # trigger candidate and arguments
                tc_list = o_sen.trigger_candidate            
                arg1_list = tc_list + o_sen.protein
                arg2_list = list(arg1_list)
                
                ''' --------------------------------------------------- '''
                '''
                wct = 0
                for word in o_sen.words:
                    print wct, word['start'], word['string'], word['score']
                    wct+=1
                print o_sen.entity_map
                print o_sen.trigger_candidate
                print o_sen.trigger
                print o_sen.protein
                '''
                ''' --------------------------------------------------- '''
                
                # setall tc label
                for tc in tc_list:
                    # set label for TC
                    tc_type = self.get_label(o_sen.words[tc]['string'], trigger_dict)
                    o_sen.words[tc]['type'] = tc_type
                    
                # for every trigger candidate
                for tc in tc_list:                    
                    # pair with every argument 1
                    for arg1 in arg1_list:
                        # trigger and argument must be different word
                        if tc == arg1: continue
                        extraction_pattern.append(self._extract_pattern(o_sen, tc, arg1))
                             
                        # pair with trigger2  if event is binding or regulations family
                        if tc_type in self.EVENT_LABEL[5:]:                        
                            for arg2 in arg2_list:
                                if tc == arg2:continue
                                if arg1 == arg2: continue
                                extraction_pattern.append(self._extract_pattern(o_sen, tc, arg1, arg2))
                            
                # filter the extracted pattern in a sentence
                filered_pattern = self.filter_pattern(extraction_pattern)
                for p in filered_pattern:
                    self.update_sentence(o_sen, p)
                
            # write a2                                
            self.a2.write(o_doc)
                
    def update_sentence(self, o_sen, pattern):
        ttype = o_sen.words[pattern.tc]['type']
        arg1_type = 'P' if pattern.arg1_type == 'Protein' else 'E'
        o_sen.update(pattern.tc, ttype, pattern.arg1, 'Theme', arg1_type)
        
        if pattern.has_arg2():
            arg2_type = 'P' if pattern.arg2_type == 'Protein' else 'E'
            if ttype == 'Binding':
                rel_name = 'Theme2'
            elif type in self.EVENT_LABEL[6:]:
                rel_name = 'Cause'
            else:
                print o_sen.number
                pattern.prints()
                raise ValueError(ttype + ' does not have argument 2')
            o_sen.update(pattern.tc, ttype, pattern.arg2, rel_name, arg2_type)
                
    def _extract_pattern(self, o_sen, tc, arg1, arg2 = -1):
        """
        extract pattern from a given tc, arg1 and arg2 in a sentence o_sen
        """
        # chunk object
        o_chunk = o_sen.chunk
        
        # trigger word object                 
        t_word = o_sen.words[tc]
                
        # init extraction pattern
        e_pattern = ExtractionPattern(tc, t_word['string'], t_word['pos_tag'], arg1, arg2)
        e_pattern.arg1_type = o_sen.words[arg1]['type']
        
        # length from trigger to argument
        e_pattern.dist1 = o_chunk.distance(tc, arg1)        
        
        # preposition
        preps1 = self.get_prep_word(o_sen,tc, arg1)
        preps2 = []        
        
        # make a pattern
        pattern = {}
        pattern[tc] = 'trg'     
        pattern[arg1] = 'arg1'
        
        if arg2 != -1:
            # distance
            e_pattern.dist2 = o_chunk.distance(tc, arg2)
            # argument2 type
            e_pattern.arg2_type = o_sen.words[arg2]['type']
            # preposition
            preps2 = [p for p in self.get_prep_word(o_sen,tc, arg2) if p not in preps1]            
            # pattern
            pattern[arg2] = 'arg2'            
        
        """ define container type """
        # chunk layer
        if e_pattern.dist1 == 0:
            e_pattern.container = 'chunk'                                                                                
        # phrase layer, at least there is preposition 1
        elif len(preps1) == 1:
            e_pattern.container = 'phrase'   
            e_pattern.prep1 = preps1[0][0]            
            pattern[preps1[0][1]] = 'prep1'                  
            # preposition 2 is optional
            if len(preps2) == 1:                
                e_pattern.prep2 = preps2[0][0]
                pattern[preps2[0][1]] = 'prep2'                         
        # clause layer
        else:
            e_pattern.container = 'clause'
        
        # build pattern type
        pattern_type = ''
        for _,v in sorted(pattern.iteritems()):
            pattern_type += v +'-'        
        e_pattern.pattern_type = pattern_type.rstrip('-')
                        
        return e_pattern
        
                
    def filter_pattern(self, extraction_patterns):
        """
        remove pattern in extraction_patterns which are not fulfill the criteria
        retruns an extracted pattern list
        """
        pattern_list = {}
                        
        for pattern in extraction_patterns:
            
            # remove if pattern key is not found in common pattern key
            if pattern.pattern_type not in self.COMMON_PATTERN_TYPE: continue
            
            # remove if pattern is not found in template
            template = self.PG.pattern.get(pattern.get_key(),None)
            if template == None: continue
            
            # remove pattern if frequency of template pattern less than FILTER_FREQUENCY_MIN
            if template.freq < self.FILTER_FREQUENCY_MIN: continue
            pattern.freq = template.freq
            
            # remove if dist1 is larger than defined FILTER_DISTANCE_MAX
            if pattern.dist1 > self.FILTER_DISTANCE_MAX: continue
            
            # if arg1 type is not found in template
            if pattern.arg1_type == 'Protein' and template.pro1_count == 0: continue
            if pattern.arg1_type != 'Protein' and template.evt1_count == 0: continue
                        
            if pattern.has_arg2():
                # if arg2 type is not found in template
                if pattern.arg2_type == 'Protein' and template.pro2_count == 0: continue
                if pattern.arg2_type != 'Protein' and template.evt2_count == 0: continue
                                
            if pattern_list.get(pattern.t_string,None) == None:
                pattern_list[pattern.t_string] = {}
                pattern_list[pattern.t_string]['chunk'] = None
                pattern_list[pattern.t_string]['phrase'] = None
                pattern_list[pattern.t_string]['clause'] = None
            
            # add pattern to list
            # add patter to container, if container is empty
            if pattern_list[pattern.t_string][pattern.container] == None:
                pattern_list[pattern.t_string][pattern.container] = pattern
            # if container is not empty, compare the frequency
            else:
                if pattern_list[pattern.t_string][pattern.container].freq < pattern.freq:
                    pattern_list[pattern.t_string][pattern.container] = pattern
        
        filtered_pattern = []        
        # process pattern for each trigger string
        for container in pattern_list.itervalues():     
            if container['chunk'] != None:
                filtered_pattern.append(container['chunk'])
            elif container['phrase'] != None:
                filtered_pattern.append(container['phrase'])
            else:
                filtered_pattern.append(container['clause'])
               
        return filtered_pattern                
        
    def update_doc_tp(self,o_sen, t_wn, arg1, rel_name):
        pass
        
    def get_label(self, string, TD):
        """
        get label for a given string
        """
        string_label = ''
        evt_cnt = 0
        for label in self.EVENT_LABEL:
            label_cnt = TD.count(string, label)
            if label_cnt > evt_cnt:
                evt_cnt = label_cnt
                string_label = label
                
        if string_label == '':
            raise ValueError('Label is not found')
        return string_label
                
    
        
if __name__ == '__main__':
    
    source = "E:/corpus/bionlp2011/project_data"
    learning_corpus = 'train'
    extraction_corpus = 'dev'
    
    dir_name_eval = "rule-test-model-001"    
    dir_name_final = "rule-model-001"
    
    doc_ids = ['PMID-9796963']

    WD = WordDictionary(source)    
    WD.load("mix")
           
    TD = TriggerDictionary(source)
    TD.load("mix")        

    extraction = Extraction(source, learning_corpus, extraction_corpus, dir_name_eval)
    extraction.extract(WD, TD, doc_ids)
    
        
        