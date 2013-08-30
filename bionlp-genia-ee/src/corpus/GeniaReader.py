'''
Created on Aug 27, 2013

@author: Andresta
'''

import os, re, json
from collections import defaultdict

class GeniaReader(object):
    '''
    read all necessary file and convert it to internal format, then save it for latter feature extraction
    '''
    
    ''' list of extension'''
    TXT_EXT = ".txt"
    
    PROTEIN_EXT = ".a1"
    
    TRIGGER_REL_EXT = ".a2"
    
    CHUNK_EXT = ".chk"
    
    MCCCJ_TREE_EXT = ".txt.ss.mcccjtok.mcccj"
    
    MCCCJ_SD_EXT = ".txt.ss.mcccjtok.mcccj.basic.sd"
    

    CORPUS_DIR = ["dev","train","test"]    
    
    # this folder contains original corpus of bionlp2011: txt, a1, and a2 files 
    ORIGINAL_DIR = "original"
    
    # this folder contains parsed corpus (tree and dependency) and also chunk file
    PARSED_DIR = "parse"    

    def __init__(self, source, dest):
        '''
        Constructor
        '''
        self.src = source
        self.dest = dest
        
        
    def run(self):
        # read all files from dir
        for cdir in self.CORPUS_DIR:
            # reading txt a1 and a2 from original dir
            path = self.get_full_path(self.ORIGINAL_DIR, cdir)
    
    
    def load_data(self, cdir, is_test):
        '''
        list all files then read them
        '''
        
        ext = self.TXT_EXT
            
        for doc_id in self.get_doc_list(cdir, ext):
            self.load_doc(cdir, doc_id, is_test)
            
          
    def load_doc(self, cdir, fname):
        triggers = []
        events = []
                
        # path for original file
        fpath = self.get_full_path(self.ORIGINAL_DIR,cdir) + '/' + fname
        
        txt = self.get_text(fpath + self.TXT_EXT)        
        proteins = self.get_protein(fpath + self.PROTEIN_EXT)                
        if cdir != 'test':            
            triggers, events = self.get_trigger_relation(fpath + self.TRIGGER_REL_EXT)
        
        
        # path for parsed file
        fpath = self.get_full_path(self.PARSED_DIR,cdir) + '/' + fname
        
        chunks = self.get_chunk(fpath + self.CHUNK_EXT)
        tree = self.get_tree_mcccj(fpath + self.MCCCJ_TREE_EXT)
        dep = self.get_dependency(fpath + self.MCCCJ_SD_EXT)
        
        doc = {"txt":txt,
               "protein":proteins,
               "trigger":triggers,
               "event":events,
               "chunk":chunks,
               "tree":tree,
               "dep":dep}
        
        print txt
        for prot in proteins:
            print prot
        for trig in triggers:
            print trig     
        for e in events:
            print e
        for line in chunks:
            print line   
        for line in tree:
            print line
        for line in dep:
            print line
            
        self.write_to_file(doc, fname)
    
    
    def write_to_file(self, doc_to_write, fname):
        with open(self.dest + '/' + fname + '.json', 'w') as fout:
            fout.write(json.dumps(doc_to_write))
        
    
    '''
    return list of file names in cdir directory
    '''
    def get_doc_list(self, cdir, ext_filter):
        return [d.rstrip(ext_filter) for d in os.listdir(self.cdir) if d.endswith(ext_filter)]
            
    '''
    return text from txt file of given fpath
    '''
    def get_text(self, fpath):
        with open(fpath, 'r') as fin:
            txt = fin.read()
        return txt
            
    '''
    return list of protein
    pretein representation:
    ['T84', 'Negative_regulation', '2665', '2673', 'decrease']
    '''
    def get_protein(self, fpath):
        proteins = []
        with open(fpath, 'r') as fin:
            for line in fin:
                line = line.rstrip('\n')
                proteins.append(re.split("\\t|\\s+",line,4))
        return proteins
    
    '''
    return list of trigger and event tuple
    trigger tuple: (id, trigger type, start idx, end idx, trigger text)
    event tuple: (id, event type, trigger_id, theme1 id, theme2 id, cause id)
    '''
    def get_trigger_relation(self, fpath):
        triggers = []
        events = []
        with open(fpath, 'r') as fin:
            for line in fin:
                line = line.rstrip('\n')
                # process trigger
                if line[0] == 'T':
                    triggers.append(re.split("\\t|\\s+",line,4))
                
                # process event
                elif line[0] == 'E':                    
                    evt = re.split("\\t|\\s+",line)
                    eid = evt[0]
                    etype,_,trigid = evt[1].partition(':')
                    theme1 = evt[2].split(':')[1]
                    if len(evt) > 3:
                        argtype,_,argid = evt[3].partition(':')
                        if argtype == 'Theme2':
                            theme2 = argid
                            cause = ""
                        elif argtype == 'Cause':
                            theme2 = ""
                            cause = argid
                        else:
                            theme2 = ""
                            cause = ""
                    events.append((eid, etype, trigid, theme1, theme2, cause))
                    
                    
                    
                    
        return triggers, events
        
    '''
    return chunk data for a document
    chunk data is list of chunk in a sentence
    ex chunk in a sentence
    [{'txt': 'XXXX', 'type': 'NP'}, {'txt': 'Inhibits', 'type': 'VP'}, {'txt': 'XXXXXXXX Mediated iTreg Commitment', 'type': 'NP'}]
    '''
    def get_chunk(self, fpath):        
        chunk_data = []
        with open(fpath, 'r') as fin:
            for line in fin:
                line_par = line[1:-3].split('] [')
                chunks_line = []
                for par in line_par:                    
                    chk_type,_,text = par.partition(' ') 
                    chunks_line.append({"type":chk_type, "txt":text})
                chunk_data.append(chunks_line)
        return chunk_data
    
    '''
    tree representation in a sentence, order by word number
    [['NP', 'NN', 'XXXX'], ['VP', 'VBZ', 'Inhibits'], ['VP', 'NP', 'NN', 'XXXXXXXX'], ..... ]
    '''
    def get_tree_mcccj(self, fpath):
        tree_data = []
        stack = []
        with open(fpath,'r') as fin:
            for line in fin:
                line_par = line[7:-3].split(' ')
                tree_line = []
                for par in line_par:
                    if par[0] == '(':
                        # push to stack
                        stack.append(par[1:])
                    else:
                        # found a leave of tree (word)
                        npop = par.count(')')
                        word_tree = list(stack)
                        word_tree.append(par.rstrip(')'))
                        for _ in xrange(npop):
                            stack.pop()
                        tree_line.append(word_tree)
                tree_data.append(tree_line)
                
                
        return tree_data
    
    '''
    return list of dependency by sentence
    ex dependency in a sentence
    {'2': [('1)', 'nsubj'), ('6)', 'dobj')], '6': [('3)', 'nn'), ('4)', 'amod'), ('5)', 'nn')]}
    '''
    def get_dependency(self, fpath):
        dep_data = []
        with open(fpath, 'r') as fin:
            dep_line = defaultdict(list)
            for line in fin:
                if line != "\n":
                    par = re.split("\\(|\\,\s",line.rstrip('\n'))
                    gov = par[1].rsplit('-',1)[1]
                    dep = par[2].rsplit('-',1)[1]
                    dep_line[gov].append((dep,par[0]))
                else:
                    if len(dep_line) > 0:
                        dep_data.append(dict(dep_line))
                    dep_line = defaultdict(list) 
                
        return dep_data
    
    '''
    cdir: dev, train, or test
    ctype: original or parsed
    '''
    def get_full_path(self, ctype, cdir):
        return self.src + '/' + ctype + '/' + cdir

if __name__ == "__main__":
    
    source = "E:/corpus/bionlp2011"
    dest = "E:/Project/bionlp-genia-ee/data"
    doc_id = "PMC-2222968-04-Results-03"
    
    Reader = GeniaReader(source,dest)
    Reader.load_doc("dev", doc_id)
    
    
    
    
    
    
        