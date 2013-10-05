'''
Created on Oct 1, 2013

@author: Andresta
'''

import os, json, pickle
from collections import Counter, defaultdict

from model.Dictionary import WordDictionary, TriggerDictionary
from model.Document import DocumentBuilder
from rule.Pattern import TemplatePattern as pattern

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

    def __init__(self, source):
        '''
        Constructor
        '''
        self.src = source
        
        self.pattern = defaultdict(pattern)
        
        # pattern frequency
        self.frequency = Counter()
        
        # pattern counter
        self.cnt_pattern_chunk = Counter()
        self.cnt_pattern_clause = Counter()
        self.cnt_pattern_phrase = Counter()
    
    def save(self, cdir):
        # save pattern
        with open(os.path.join(self.src,self.RULE_DIR,cdir+'_pattern.pkl'),'wb') as f:
            pickle.dump(self.pattern, f)
        
        # save frequency
        with open(os.path.join(self.src,self.RULE_DIR,cdir+'_frequency.pkl'),'wb') as f:
            pickle.dump(self.frequency, f)
        
    def load(self, cdir):                 
        with open(os.path.join(self.src,self.RULE_DIR,cdir+'_pattern.pkl'),'rb') as f:
            self.pattern = pickle.load(f)
            
        with open(os.path.join(self.src,self.RULE_DIR,cdir+'_frequency.pkl'),'rb') as f:
            self.frequency = pickle.load(f)
    
    def _build_doc(self, builder, doc_id, is_test = False):                
        doc = builder.read_raw(doc_id)
        return builder.build_doc_from_raw(doc, is_test) 
    
    def generate(self, cdir,word_dict, trigger_dict):
        
        # document builder
        builder = DocumentBuilder(self.src, word_dict, trigger_dict)
        
        # file name to write data
        fname = 'data_'+cdir+'.csv'
        
        doc_ids = self.get_doc_list(cdir)
        print 'generating pattern ....'
        for doc_id in doc_ids:
            o_doc = self._build_doc(builder, doc_id)            
            for i in range(0, len(o_doc.sen)):            
            
                o_sen = o_doc.sen[i]
                rel = o_sen.rel
                trigger_list = o_sen.trigger
                
                # skip if sentence does not have relation
                if rel.data == []: continue
                
                for t_wn in trigger_list:
                    # ge list of theme arguments
                    args1 = self.get_arg1(rel, t_wn)
                    args2 = self.get_arg2(rel, t_wn)
                                        
                    
                    for arg1 in args1:
                        if args2 == []:
                            if t_wn == arg1:
                                print o_doc.doc_id, i , t_wn, arg1
                            else:
                                self.extract_trig_arg(fname, o_doc.doc_id, o_sen, t_wn, arg1)                                
                        else:
                            for arg2 in args2:                                
                                if t_wn == arg2 or arg2 == arg1 or t_wn == arg1 :
                                    print o_doc.doc_id, i , t_wn, arg1, arg2
                                else:
                                    self.extract_trig_arg(fname, o_doc.doc_id, o_sen, t_wn, arg1, arg2)                                                                           
            
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
        
        # make a pattern
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
            
            # pattern
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
        
        # build pattern type
        pattern_type = ''
        for _,v in sorted(pattern.iteritems()):
            pattern_type += v +'-'        
        pattern_type = pattern_type.rstrip('-')        
        
        # build key
        key = ':'.join([t_string,t_pos, pattern_type, container]) 
        
        # increase frequency 
        self.frequency[key] += 1
        
        # update pattern entry
        self.pattern[key].set(dist1,arg1_type,prep1,dist2,arg2_type,prep2)
        
        # increase pattern counter
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
    
    def get_arg1(self, rel, t_wn):
        args = []
        for r in rel.data:
            if r[0] == t_wn and r[2] == 'Theme':
                args.append(r[1])
        return args

    def get_arg2(self, rel, t_wn):
        args = []
        rel_type = ['Theme2', 'Cause']
        for r in rel.data:
            if r[0] == t_wn and r[2] in rel_type:
                args.append(r[1])
        return args
    
    def get_doc_list(self, cdir):
        with open(os.path.join(self.src,cdir+'_doc_ids.json'),'r') as f:
            doc_ids = json.loads(f.read())
            return doc_ids
    
    def _write_tsv(self, fname, list_string):
        with open(os.path.join(self.src,self.RULE_DIR,fname),'a') as f:
            f.write('\t'.join(list_string) + '\n')
        
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
    
    # pattern type for each layer  
    print '\n\nPattern type for CHUNK layer'
    for k,v in sorted(PG.cnt_pattern_chunk.iteritems(), key=operator.itemgetter(1)):
        print k, v
        
    print '\n\nPattern type for PHRASE layer'
    for k,v in sorted(PG.cnt_pattern_phrase.iteritems(), key=operator.itemgetter(1)):
        print k, v
        
    print '\n\nPattern type for CLAUSE layer'
    for k,v in sorted(PG.cnt_pattern_clause.iteritems(), key=operator.itemgetter(1)):
        print k, v
    
    for e in PG.frequency.most_common(3):        
        print e[0], e[1]
        PG.pattern[e[0]].prints()
        
    