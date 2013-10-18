'''
Created on Oct 1, 2013

@author: Andresta
'''

import os, json, pickle
from collections import Counter, defaultdict
from model.Dictionary import WordDictionary, TriggerDictionary
from model.Document import DocumentBuilder
from rule.Pattern import TemplatePattern as template, Pattern 
class PatternGenerator(object):
    '''
    classdocs
    '''
    
    COMMON_PATTERN_TYPE = {'trg-arg1' : 11,
                           'arg2-trg-arg1': 12,
                           'arg1-trg' : 13 ,
                           'trg-prep1-arg1' : 21,
                           'trg-prep1-arg1-prep2-arg2': 22,
                           'trg-prep2-arg2-prep1-arg1': 23,
                           'arg2-trg-prep1-arg1' : 24,
                           'arg1-arg2-trg' : 31,
                           'arg1-trg' : 32,
                           'trg-arg1' : 33,
                           'arg2-trg-arg1' : 34,
                           'arg1-trg-arg2' : 35}
    
    RULE_DIR = 'rule'
    
    FNAME_PATTERN = 'template.pkl'
    
    FNAME_FREQUENCY = 'frequency.pkl'
    
    FNAME_STAT_DATA = 'pattern_data.csv'

    def __init__(self, source):
        '''
        Constructor
        '''
        self.src = source
        
        self.template = defaultdict(template)
        
        # pattern frequency
        self.frequency = Counter()
        
        self.pattern = Pattern()
        
        # template counter
        self.cnt_pattern_chunk = Counter()
        self.cnt_pattern_clause = Counter()
        self.cnt_pattern_phrase = Counter()
        self.cnt_pattern_non = Counter()
    
    def save(self, cdir):
        # save template
        with open(os.path.join(self.src, self.RULE_DIR,cdir+'_'+self.FNAME_PATTERN), 'wb') as f:
            pickle.dump(self.template, f)
        
        # save frequency
        with open(os.path.join(self.src, self.RULE_DIR,cdir+'_'+self.FNAME_FREQUENCY), 'wb') as f:
            pickle.dump(self.frequency, f)
        
    def load(self, cdir):                 
        with open(os.path.join(self.src, self.RULE_DIR,cdir+'_'+self.FNAME_PATTERN), 'rb') as f:
            self.template = pickle.load(f)
            
        with open(os.path.join(self.src, self.RULE_DIR,cdir+'_'+self.FNAME_FREQUENCY), 'rb') as f:
            self.frequency = pickle.load(f)
    
    def _build_doc(self, builder, doc_id, is_test = False):                
        doc = builder.read_raw(doc_id)
        return builder.build_doc_from_raw(doc, is_test) 
    
    def generate(self, cdir,word_dict, trigger_dict):
        
        # document builder
        builder = DocumentBuilder(self.src, word_dict, trigger_dict)
        
        # delete statistic data
        path = os.path.join(self.src, self.RULE_DIR, cdir+'_'+self.FNAME_STAT_DATA)
        if os.path.exists(path):
            os.unlink(path)
        
        doc_ids = self.get_doc_list(cdir)
        print 'generating template ....'
        for doc_id in doc_ids:
            print doc_id
            o_doc = self._build_doc(builder, doc_id)            
            for i in range(0, len(o_doc.sen)):            
            
                o_sen = o_doc.sen[i]
                rel = o_sen.rel
                trigger_list = o_sen.trigger
                
                # skip if sentence does not have relation
                if rel.data == []: continue
                
                for t_wn in trigger_list:
                    
                    # skip if trigger is not in trigger candidate
                    if t_wn not in o_sen.trigger_candidate: continue
                    # ge list of theme arguments
                    args1 = self.get_arg1(rel, t_wn)
                    args2 = self.get_arg2(rel, t_wn)
                                        
                    
                    for arg1 in args1:
                        # trigger with only 1 argument
                        if args2 == []:
                            # skip self loop
                            if t_wn == arg1:
                                print o_doc.doc_id, i , t_wn, arg1
                            else:
                                self.extract_rule_1arg(cdir, o_doc.doc_id, o_sen, t_wn, arg1)                                                        
                        else:
                            # trigger with 2 arguments
                            for arg2 in args2:                                
                                if t_wn == arg2 or arg2 == arg1 or t_wn == arg1 :
                                    print o_doc.doc_id, i , t_wn, arg1, arg2
                                else:
                                    self.extract_rule_2arg(cdir, o_doc.doc_id, o_sen, t_wn, arg1, arg2)                                                                           
            
    def extract_rule_1arg(self, cdir, doc_id, o_sen, t_wn, arg1):
        
        t_word = o_sen.words[t_wn]
        t_arg1 = o_sen.words[arg1]
                
        pattern, layer, prep_string = self.pattern.get_pattern_1arg(o_sen, t_wn, arg1)  
        
        if pattern != '':      
            # get distance
            dist = self.pattern.get_distance_chkdep(o_sen, t_wn, arg1)
            # build key
            key = ':'.join([t_word['string'],t_word['pos_tag'], pattern, layer])                         
            # update template entry
            self.template[key].set(dist,t_arg1['type'],prep_string)
            
            """ statistic """
            # increase frequency 
            self.frequency[layer+':'+pattern] += 1
            # increase counter
            self._add_counter(layer, pattern)
            # statistic information
            str_list = [doc_id, str(o_sen.number), str(t_wn), str(arg1), '', t_word['string'],t_word['pos_tag']]
            str_list += [t_arg1['type'], '', pattern, layer, str(dist), '0', prep_string, '']        
            self._write_tsv(cdir, str_list)
        else:
            self.cnt_pattern_non['1arg'] += 1
        
    def extract_rule_2arg(self, cdir, doc_id, o_sen, t_wn, arg1, arg2):
    
        t_word = o_sen.words[t_wn]
        t_arg1 = o_sen.words[arg1]
        t_arg2 = o_sen.words[arg2]
        
        pattern, layer, prep1_string, prep2_string = self.pattern.get_pattern_2arg(o_sen, t_wn, arg1, arg2)     
        
        if pattern != '':   
            # get distance
            dist1 = self.pattern.get_distance_chkdep(o_sen, t_wn, arg1)        
            dist2 = self.pattern.get_distance_chkdep(o_sen, t_wn, arg2)                
            # build key
            key = ':'.join([t_word['string'],t_word['pos_tag'], pattern, layer])                         
            # update template entry
            self.template[key].set(dist1,t_arg1['type'],prep1_string,dist2,t_arg2['type'],prep2_string)
                    
            """ statistic """
            # increase frequency 
            self.frequency[layer+':'+pattern] += 1
            # increase counter
            self._add_counter(layer, pattern)
            # statistic information
            str_list = [doc_id, str(o_sen.number), str(t_wn), str(arg1), str(arg2), t_word['string'],t_word['pos_tag']]
            str_list += [t_arg1['type'], t_arg2['type'], pattern, layer, str(dist1), str(dist2), prep1_string, prep2_string]        
            self._write_tsv(cdir, str_list)
            
            '''
            if pattern == 'arg2-prep1-trig-arg1':
                print '========================================='
                print doc_id, o_sen.number, t_wn, arg1, arg2
            '''
        else:
            self.cnt_pattern_non['2arg'] += 1
    
        
       
    def extract_trig_arg(self, fname, doc_id, o_sen, t_wn, arg1, arg2 = -1):
        
        o_chunk = o_sen.chunk        
        container = ''
        t_word = o_sen.words[t_wn]
        t_arg = o_sen.words[arg1]
        
        # trigger argument info
        t_string = t_word['string'].lower()
        t_pos = t_word['pos_tag']
        arg1_type = 'P' if t_arg['type'] == 'Protein' else 'E'
        arg2_type = ''
                    
        # length from trigger to argument
        dist1 = o_chunk.distance(t_wn, arg1)
        dist2 = -1
        
        # preposition
        preps1 = self.get_prep_word(o_sen,t_wn, arg1)
        preps2 = []        
        prep1 = ''
        prep2 = ''
        
        # make a template
        pattern = {}
        pattern[t_wn] = 'trg'     
        pattern[arg1] = 'arg1'
                
        if arg2 != -1:
            # distance
            dist2 = o_chunk.distance(t_wn, arg1)
            # argument type
            t_arg2 = o_sen.words[arg2]
            arg2_type = 'P' if t_arg2['type'] == 'Protein' else 'E'
            # preposition
            preps2 = [p for p in self.get_prep_word(o_sen,t_wn, arg2) if p not in preps1]
            
            # template
            pattern[arg2] = 'arg2'
        
        # chunk layer
        if dist1 == 0:
            container = 'chunk'                        
                                                        
        # phrase layer, at least there is preposition 1
        elif len(preps1) == 1:
            container = 'phrase'            
            pattern[preps1[0][1]] = 'prep1'      
            prep1 = preps1[0][0]      
            # preposition 2 is optional
            if len(preps2) == 1:
                pattern[preps2[0][1]] = 'prep2'
                prep2 = preps2[0][0]        
        # clause layer
        else:
            container = 'clause'
        
        # build template type
        pattern_type = ''
        for _,v in sorted(pattern.iteritems()):
            pattern_type += v +'-'        
        pattern_type = pattern_type.rstrip('-')        
        
        # build key
        key = ':'.join([t_string,t_pos, pattern_type, container]) 
        
        # increase frequency 
        self.frequency[key] += 1
        
        # update template entry
        self.template[key].set(dist1,arg1_type,prep1,dist2,arg2_type,prep2)
        
        # increase template counter
        if container == 'chunk':
            self.cnt_pattern_chunk[pattern_type] += 1
        elif container == 'phrase':
            self.cnt_pattern_phrase[pattern_type] += 1
        else:
            self.cnt_pattern_clause[pattern_type] += 1
        
        # statistic information
        str_list = [doc_id, str(o_sen.number), str(t_wn), str(arg1), str(arg2), t_string, t_pos]
        str_list += [arg1_type, arg2_type, pattern_type, container, str(dist1), str(dist2), prep1, prep2]        
        self._write_tsv(fname, str_list)
        
    
    
    
    def get_arg1(self, rel, t_wn):
        args = []
        # relation data (8,10,'Theme','E')
        for r in rel.data:
            if r[0] == t_wn and r[2] == 'Theme':
                args.append(r[1])
        return args

    def get_arg2(self, rel, t_wn):
        args = []
        # relation data (8,10,'Theme','E')
        rel_type = ['Theme2', 'Cause']
        for r in rel.data:
            if r[0] == t_wn and r[2] in rel_type:
                args.append(r[1])
        return args
    
    def get_doc_list(self, cdir):
        with open(os.path.join(self.src,cdir+'_doc_ids.json'),'r') as f:
            doc_ids = json.loads(f.read())
            return doc_ids
    
    def _write_tsv(self, cdir, list_string):
        path = os.path.join(self.src, self.RULE_DIR, cdir+'_'+self.FNAME_STAT_DATA)
        with open(path,'a') as f:
            f.write('\t'.join(list_string) + '\n')
        
    def _add_counter(self, layer, pattern):
        if layer == 'chunk':
            self.cnt_pattern_chunk[pattern] += 1
        elif layer == 'phrase':
            self.cnt_pattern_phrase[pattern] += 1
        else:
            self.cnt_pattern_clause[pattern] += 1
        
if __name__ == '__main__':
    import operator
    source = "E:/corpus/bionlp2011/project_data"

    WD = WordDictionary(source)    
    WD.load("mix")
           
    TD = TriggerDictionary(source)
    TD.load("mix")

    PG = PatternGenerator(source)
    PG.generate('mix', WD, TD)
    PG.save('mix')
    
    #PG.load('mix')
    
    # template type for each layer  
    print '\n\nPattern type for CHUNK layer'
    for k,v in sorted(PG.cnt_pattern_chunk.iteritems(), key=operator.itemgetter(1)):
        print k, v
        
    print '\n\nPattern type for PHRASE layer'
    for k,v in sorted(PG.cnt_pattern_phrase.iteritems(), key=operator.itemgetter(1)):
        print k, v
        
    print '\n\nPattern type for CLAUSE layer'
    for k,v in sorted(PG.cnt_pattern_clause.iteritems(), key=operator.itemgetter(1)):
        print k, v
        
    print '\n\nPattern that cannot be captured'
    for k,v in PG.cnt_pattern_non.iteritems():
        print k, v
    '''
    for e in PG.frequency.most_common(3):        
        print e[0], e[1]
        PG.template[e[0]].prints()
    ''' 
    