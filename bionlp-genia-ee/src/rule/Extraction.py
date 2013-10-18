'''
Created on Oct 3, 2013

@author: Andresta
'''
import os, json
from collections import defaultdict
from rule.PatternGenerator import PatternGenerator
from rule.Pattern import TemplatePattern, ExtractionPattern, Pattern
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
                                
        # init template generator
        self.PG = PatternGenerator(source)
        
        # init a2 writer        
        self.a2 = A2Writter(self.get_out_path(dir_name))
        
        self.pattern = Pattern()
    
    def get_out_path(self, dir_name):
        path = os.path.join(source + self.OUT_DIR,dir_name)
        if not os.path.exists(path):
            os.makedirs(path)        
        return path 
    
    def get_doc_list(self, cdir):
        with open(os.path.join(self.src,cdir+'_doc_ids.json'),'r') as f:
            doc_ids = json.loads(f.read())
            return doc_ids
        
    def _build_doc(self, builder, doc_id, is_test = True):                
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
        
        # load template data
        self.PG.load(self.learning_corpus)
        
        if doc_ids == []:
            doc_ids = self.get_doc_list(self.extraction_corpus)
            
        print 'extracting document ....'
        for doc_id in doc_ids:
            print doc_id
            o_doc = self._build_doc(builder, doc_id)            
            
            for i in range(0, len(o_doc.sen)):                                
                print '\nsen:', i
                print '----------------------------------------'
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
                
                # setall tc label
                for tc in tc_list:
                    # set label for TC
                    tc_type = self.get_label(o_sen.words[tc]['string'], trigger_dict)
                    o_sen.words[tc]['type'] = tc_type
                    
                # for every trigger candidate
                for tc in tc_list:              
                    tword = o_sen.words[tc]
                    for arg1 in arg1_list:
                        if tc == arg1: continue
                        # trigger with only 1 argument           
                        #print tc, arg1             
                        template, key = self.get_template(o_sen, tc, arg1)
                        if template != None:
                            if self.get_pattern_frequency(key) > 20 and template.freq > 4:
                                print tword['start'], tword['string'], tword['pos_tag'], tword['type'], tc, arg1, key, self.pattern.get_distance_chkdep(o_sen, tc, arg1)
                                print template.freq, ':',template.pro1_count, template.evt1_count, max(template.dist1), template.prep1
                                                
                        for arg2 in arg2_list:                     
                            #print tc, arg1, arg2           
                            if tc == arg2 or arg2 == arg1 or tc == arg1 : continue
                            template, key = self.get_template(o_sen, tc, arg1, arg2)
                            if template != None:
                                if self.get_pattern_frequency(key) > 20 and template.freq > 4:
                                    print tword['start'], tword['string'], tword['pos_tag'], tword['type'],tc, arg1, arg2, key, self.pattern.get_distance_chkdep(o_sen, tc, arg1), self.pattern.get_distance_chkdep(o_sen, tc, arg2)
                                    print template.freq, ':', template.pro1_count, template.evt1_count, max(template.dist1), template.prep1,  '-', template.pro2_count, template.evt2_count, max(template.dist2), template.prep2 
                    
                
    def get_pattern_frequency(self, key):
        k = key.split(':')
        return self.PG.frequency[k[3]+':'+k[2]]
        
    
    def get_template(self, o_sen, t_wn, arg1, arg2 = -1):
        
        t_word = o_sen.words[t_wn]
        
        if arg2 < 0:
            pattern, layer, prep1 = self.pattern.get_pattern_1arg(o_sen, t_wn, arg1)
        else:
            pattern, layer, prep1, prep2 = self.pattern.get_pattern_2arg(o_sen, t_wn, arg1, arg2)            
        # build key
        key = ':'.join([t_word['string'],t_word['pos_tag'], pattern, layer])
        
        return self.PG.template.get(key,None), key
    
    def pattern_1arg(self, o_sen, t_wn, arg1):
        prep_string = ''
        position = {t_wn:'trig', arg1:'arg1'}
        # word object
        t_word = o_sen.words[t_wn]
        t_arg1 = o_sen.words[arg1]
        
        if self.pattern.is_chunk(o_sen, t_wn, arg1):            
            layer = 'chunk'    
            
        elif self.pattern.is_phrase(o_sen, t_wn, arg1):                        
            layer = 'phrase'            
            # get preposition, if more than 1 get the nearest prep to argument
            preps = self.pattern.get_prep_word(o_sen,t_wn, arg1)
            prep_string = preps[-1][0] 
            prep_wn = preps[-1][1]
            position[prep_wn] = 'prep1'
        else:
            layer = 'clause'
            
        # build template type
        pattern = self.pattern.get_pattern_str(position)        
        # build key
        key = ':'.join([t_word['string'],t_word['pos_tag'], pattern, layer])   
        
       
    def update_non_regulation(self, o_sen, pattern):
        ttype = o_sen.words[pattern.tc]['type']
        if ttype in self.EVENT_LABEL[6:]: return
        arg1_type = 'P' if pattern.arg1_type == 'Protein' else 'E'
        if arg1_type == 'P':
            o_sen.update(pattern.tc, ttype, pattern.arg1, 'Theme', arg1_type)
        
            if pattern.has_arg2():
                arg2_type = 'P' if pattern.arg2_type == 'Protein' else 'E'
                if ttype == 'Binding':
                    rel_name = 'Theme2'
                elif ttype in self.EVENT_LABEL[6:]:
                    rel_name = 'Cause'
                else:
                    print o_sen.number
                    pattern.prints()
                    raise ValueError(ttype + ' does not have argument 2')
                if arg2_type == 'P' and ttype != 'Binding':
                    o_sen.update(pattern.tc, ttype, pattern.arg2, rel_name, arg2_type)
                    
    def update_regulation(self, o_sen, pattern):
        ttype = o_sen.words[pattern.tc]['type']
        if ttype in self.EVENT_LABEL[0:6]: return
        arg1_type = 'P' if pattern.arg1_type == 'Protein' else 'E'
        if arg1_type == 'P':
            o_sen.update(pattern.tc, ttype, pattern.arg1, 'Theme', arg1_type)
        
            if pattern.has_arg2():
                arg2_type = 'P' if pattern.arg2_type == 'Protein' else 'E'
                if ttype == 'Binding':
                    rel_name = 'Theme2'
                elif ttype in self.EVENT_LABEL[6:]:
                    rel_name = 'Cause'
                else:
                    print o_sen.number
                    pattern.prints()
                    raise ValueError(ttype + ' does not have argument 2')
                if arg2_type == 'P':
                    o_sen.update(pattern.tc, ttype, pattern.arg2, rel_name, arg2_type)
                
    def _extract_pattern(self, o_sen, tc, arg1, arg2 = -1):
        """
        extract template from a given tc, arg1 and arg2 in a sentence o_sen
        """
        # chunk object
        o_chunk = o_sen.chunk
        
        # trigger word object                 
        t_word = o_sen.words[tc]
                
        # init extraction template
        e_pattern = ExtractionPattern(tc, t_word['string'], t_word['pos_tag'], arg1, arg2)
        e_pattern.arg1_type = o_sen.words[arg1]['type']
        
        # length from trigger to argument
        e_pattern.dist1 = o_chunk.distance(tc, arg1)        
        
        # preposition
        preps1 = self.get_prep_word(o_sen,tc, arg1)
        preps2 = []        
        
        # make a template
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
            # template
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
        
        # build template type
        pattern_type = ''
        for _,v in sorted(pattern.iteritems()):
            pattern_type += v +'-'        
        e_pattern.pattern_type = pattern_type.rstrip('-')
                        
        return e_pattern
        
                
    def filter_pattern(self, extraction_patterns):
        """
        remove template in extraction_patterns which are not fulfill the criteria
        retruns an extracted template list
        """
        pattern_list = {}
                        
        for pattern in extraction_patterns:
            
            # remove if template key is not found in common template key
            if pattern.pattern_type not in self.COMMON_PATTERN_TYPE: continue
            
            # remove if template is not found in template
            template = self.PG.template.get(pattern.get_key(),None)
            if template == None: continue
            
            # remove template if frequency of template template less than FILTER_FREQUENCY_MIN
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
                pattern_list[pattern.t_string]['chunk'] = []
                pattern_list[pattern.t_string]['phrase'] = []
                pattern_list[pattern.t_string]['clause'] = []
            
            
            # add template to list
            # add patter to container, if container is empty
            if pattern_list[pattern.t_string][pattern.container] == []:
                pattern_list[pattern.t_string][pattern.container].append(pattern)
            # if container is not empty, compare the frequency
            else:
                #template.prints()
                if pattern_list[pattern.t_string][pattern.container][0].pattern_type == pattern.pattern_type:
                    pattern_list[pattern.t_string][pattern.container].append(pattern)
                elif pattern_list[pattern.t_string][pattern.container][0].freq < pattern.freq:
                    pattern_list[pattern.t_string][pattern.container] = [pattern]
        
        filtered_pattern = []        
        # process template for each trigger string
        for string, container in pattern_list.iteritems():
            #print string, len(container['chunk']), len(container['phrase']), len(container['clause'])           
            if container['chunk'] != []:
                for p in container['chunk']:
                    #print 'chunk:',p.t_string
                    filtered_pattern.append(p)
            elif container['phrase'] != []:
                for p in container['phrase']:
                    #print 'phrase:',p.t_string
                    filtered_pattern.append(p)
            else:
                for p in container['clause']:
                    #print 'clause:',p.t_string
                    filtered_pattern.append(p)
               
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
            print string
            raise ValueError('Label is not found')
        return string_label
                
    
        
if __name__ == '__main__':
    
    source = "E:/corpus/bionlp2011/project_data"
    learning_corpus = 'mix'
    extraction_corpus = 'dev'
    
    dir_name_eval = "rule-test-model-002"    
    dir_name_final = "rule-model-002"
    
    doc_ids = ['PMC-2806624-03-RESULTS-02']

    WD = WordDictionary(source)    
    WD.load("mix")
           
    TD = TriggerDictionary(source)
    TD.load("mix")        

    extraction = Extraction(source, learning_corpus, extraction_corpus, dir_name_eval)
    extraction.extract(WD, TD, doc_ids)
    
        
        