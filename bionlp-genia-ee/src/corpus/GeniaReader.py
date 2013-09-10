'''
Created on Aug 27, 2013

@author: Andresta
'''

import os, re, json
from collections import defaultdict
from tools.PorterStemmer import PorterStemmer

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
    
    # this folder contains pre-processed text, all proteins are replaced by placeholder
    PREPROCESS_DIR = "preprocess"
    
    # this folder contain data source for all docs
    DATA_DIR = "data"
    
    # bracket char coding
    #BRACKET_CHAR = {'-LRB-':'(', '-RRB-':')', '-RSB-':']', '-LSB-':'[', '-LCB-':'{', '-RCB-':'}'}

    def __init__(self, source, dest):
        '''
        Constructor
        '''
        self.src = source
        self.dest = dest
        
        self.Dep = DependencyReader()
        self.Tree = ParseTreeReader()
        self.Chunk = ChunkReader()
        self.Stemmer = PorterStemmer()
        
        
    def run(self):
        # read all files from dir
        for cdir in self.CORPUS_DIR:
            print "reading content of " + cdir + " directory"
            doc_ids = self.load_save_data(cdir)
            print str(len(doc_ids)) + " doc have been read"
            
            # write doc ids to file
            fpath = self.dest + '/' + cdir + '_doc_ids.json'
            self.write_to_file(doc_ids, fpath)
    
    '''
    this function returns list of doc_id for a given cdir
    and do:
    1. list files under cdir
    2. load all necessary file for a given doc_id
    3. check it consistency
    4. save it as json    
    '''
    def load_save_data(self, cdir):
                
        ext = self.TXT_EXT
        doc_ids = self.get_doc_list(self.get_full_path(self.ORIGINAL_DIR,cdir), ext)
        
        # there is a document that cannot be parsed by mcccj parser
        # no event in that document, so we can just skip it
        if cdir == "train":
            print "Skip PMID-8632999"
            doc_ids.remove("PMID-8632999")
        
        for doc_id in doc_ids:            
            # load doc data
            doc = self.load_doc(cdir, doc_id)
            
            # check consistency
            self.check_consistency(doc)
            
            # save to file
            fpath = self.dest + '/' + self.DATA_DIR + '/' + doc_id + '.json'
            self.write_to_file(doc, fpath)
        
           
        return doc_ids
    
    '''
    read document data
    and return doc representation
    '''
    def load_doc(self, cdir, doc_id):
        # init variable
        triggers = []
        events = []
        equivs = []
        is_test = True
        
        # path for original file
        ori_fpath = self.get_full_path(self.ORIGINAL_DIR,cdir) + '/' + doc_id
        
        txt = self.get_text(ori_fpath + self.TXT_EXT)        
        proteins = self.get_protein(ori_fpath + self.PROTEIN_EXT)                
        if cdir != 'test':            
            triggers, events, equivs = self.get_trigger_relation(ori_fpath + self.TRIGGER_REL_EXT)
            is_test = False
        
        # path for parsed file
        parsed_fpath = self.get_full_path(self.PARSED_DIR,cdir) + '/' + doc_id
        
        chunks = self.get_chunk(parsed_fpath + self.CHUNK_EXT)
        tree = self.get_tree_mcccj(parsed_fpath + self.MCCCJ_TREE_EXT)
        dep = self.get_dependency(parsed_fpath + self.MCCCJ_SD_EXT)
        
        # path for preprocess file
        pre_fpath = self.get_full_path(self.PREPROCESS_DIR, cdir) + '/' + doc_id
        sentences = self.get_sentences(pre_fpath + self.TXT_EXT)        
        
        
        # create doc representation
        doc = {"doc_id": doc_id,
               "test": is_test,
               "path1": ori_fpath,
               "path2": parsed_fpath,
               "nsen": len(tree),
               "txt":txt,
               "sen": sentences,
               "protein":proteins,
               "equiv":equivs,
               "trigger":triggers,
               "event":events,
               "chunk":chunks,
               "tree":tree,
               "dep":dep}
        
        return doc
                    
                    
    
    '''
    update/add offset of word
    offset is relative position in the abstract
    and add stem of word
    '''
    def update_word_info(self, txt, sentences):
        
        search_offset = 0
        
        for sentence in sentences:
            for word in sentence:
                string = word["string"]
                #if string in self.BRACKET_CHAR:
                #    string = self.BRACKET_CHAR[string]
                start = txt.find(string, search_offset)
                if start == -1:
                    
                    # try to convert back " into ''
                    # in parser " are represented as '' so we need to convert back to original char
                    # but there are some cases that '' is actually '' as in =>  4'',6-Diamidino-2-phenylindole 
                    string = string.replace("\"","\'\'")
                    start = txt.find(string, search_offset)
                    
                    if start == -1:                        
                        print string
                        print sentence
                        raise ValueError("string not found")
                    
                    word["string"] = string
                    
                end = start + len(string)  
                # add offset
                word["start"] = start
                word["end"] = end
                # add stem using porter stemmer
                word["stem"] = self.Stemmer.stem(string, 0, len(string)-1)
                search_offset = end                
            
        return sentences
        
    
    '''
    write to file
    '''
    def write_to_file(self, doc_to_write, fpath):
        with open(fpath, 'w') as fout:
            fout.write(json.dumps(doc_to_write))
    
    '''
    check consistency for chunk, tree, and dep data type
    they must have same number of line and number of word for each line
    '''
    def check_consistency(self, doc):
        chunck = doc["chunk"]
        tree = doc["tree"]
        dep = doc["dep"]
        
        # check number of sentence
        #print "number of sentence:", len(chunck), len(tree),len(dep)
        if len(chunck) != len(tree) or len(tree) != len(dep):            
            raise ValueError("Chunck, Tree and Dep has different number of sentence")
        
        # check number of line
        for i in range(0,len(chunck)):
            #print i, "number of words: ", chunck[i]["nword"], tree[i]["nword"], dep[i]["nword"]
            if chunck[i]["nword"] != tree[i]["nword"] or tree[i]["nword"] != dep[i]["nword"]:                
                print tree[i]
                print chunck[i]
                print dep[i]
                raise ValueError("Different number of word in sentence " + str(i) + " doc: " + doc["doc_id"])
    
    '''
    print to screen document representation
    '''
    def print_doc(self, doc):  
        
        print "doc id: ", doc["doc_id"]
        print "is test: ", doc["test"]
        print "ori path: ", doc["path1"]
        print "parsed path: ", doc["path2"]        
        print "number of sentence:", doc["nsen"]
        print doc["txt"]
        print "Sentences:"
        for sen in doc["sen"]:
            print sen
        print "Proteins:"
        for line in doc["protein"].values():
            print line
        print "Equivs:"
        for line in doc["equiv"]:
            print line
        print "Triggers:"
        for line in doc["trigger"].values():
            print line   
        print "Events:"  
        for line in doc["event"].values():
            print line
        print "Chunks:"
        for line in doc["chunk"]:
            print line
        print "Trees:"   
        for line in doc["tree"]:
            print line
        print "Dependencies:"
        for line in doc["dep"]:
            print line
    
    '''
    return list of file names in cdir directory
    '''
    def get_doc_list(self, cdir, ext_filter):
        return [d.rstrip(ext_filter) for d in os.listdir(cdir) if d.endswith(ext_filter)]
            
    '''
    return text from txt file of given fpath
    '''
    def get_text(self, fpath):
        with open(fpath, 'r') as fin:
            txt = fin.read()
        return txt
            
    '''
    return protein dict
    pretein representation:
    'T84' : ['T84', 'Negative_regulation', '2665', '2673', 'decrease']
    '''
    def get_protein(self, fpath):
        proteins = {}
        with open(fpath, 'r') as fin:
            for line in fin:
                line = line.rstrip('\n')
                p = re.split("\\t|\\s+",line,4)
                proteins[p[0]] = p
        return proteins
    
    '''
    return trigger dictionary, event dictionary and equiv tuple
    trigger 
    id : (id, trigger type, start idx, end idx, trigger text)
    event tuple
    id : (id, event type, trigger_id, theme1 id, theme2 id, cause id)
    equiv tuple: (protein1, protein2)
    e
    '''
    def get_trigger_relation(self, fpath):
        triggers = {}
        events = {}
        equivs = []
        with open(fpath, 'r') as fin:
            for line in fin:
                line = line.rstrip('\n')
                # process trigger
                if line[0] == 'T':
                    t = re.split("\\t|\\s+",line,4)
                    triggers[t[0]] = t
                
                # process event
                elif line[0] == 'E':                    
                    evt = re.split("\\t|\\s+",line)
                    eid = evt[0]
                    etype,_,trigid = evt[1].partition(':')
                    theme1 = evt[2].split(':')[1]
                    theme2 = ""
                    cause = ""
                    if len(evt) > 3:
                        argtype,_,argid = evt[3].partition(':')
                        if argtype == 'Theme2':
                            theme2 = argid
                            cause = ""
                        elif argtype == 'Cause':
                            theme2 = ""
                            cause = argid                        
                    events[eid] = list((eid, etype, trigid, theme1, theme2, cause))
                
                # process equiv
                elif line[0] == '*':
                    equiv = re.split("\\t|\\s",line)
                    equivs.append(tuple(equiv[2:]))
                    
                    
                    
        return triggers, events, equivs
        
    '''
    return chunk data
    '''
    def get_chunk(self, fpath):        
        return self.Chunk.read(fpath)
    
    '''
    return parse tree data
    '''
    def get_tree_mcccj(self, fpath):
        return self.Tree.read(fpath)
    
    '''
    return sentences of a document
    get_tree_mcccj must be called first
    '''
    def get_sentences(self, preprocess_txt_fpath, check = False):
        pre_txt = self.get_text(preprocess_txt_fpath)
        sentences = self.update_word_info(pre_txt,  self.Tree.sentences)     
        
        if check:
            for sentence in sentences:
                for word in sentence:
                    if pre_txt[word["start"]:word["end"]] != word["string"]:
                        print pre_txt[word["start"]:word["end"]], "=>", word
                        #raise ValueError("string in txt and word do not match")
        
        return sentences
    
    '''
    return dependency data
    '''
    def get_dependency(self, fpath):
        return self.Dep.read(fpath)
    
    '''
    cdir: dev, train, or test
    ctype: original or parsed
    '''
    def get_full_path(self, ctype, cdir):
        return self.src + '/' + ctype + '/' + cdir

            
            
    
class DependencyReader:
          
    '''
    return list of dependency by sentence
    ex dependency in a sentence
    {
        root: '2'
        nword: '6'
        data: {'2': [('1)', 'nsubj'), ('6)', 'dobj')], '6': [('3)', 'nn'), ('4)', 'amod'), ('5)', 'nn')]}
    }
    '''
    def read(self, fpath):        
        dep_doc = []
        with open(fpath, 'r') as fin:
            dep_line = defaultdict(list)
            root = []
            non_root = []
            n_word = 0
            for line in fin:
                if line != "\n":
                    par = re.split("\\(|\\,\s",line.rstrip(')\n'))
                    
                    # find gov and add it as candidate of root
                    gov = par[1].rsplit('-',1)[1]
                    root.append(gov)
                    
                    # find dep and add it as non root
                    dep = par[2].rsplit('-',1)[1]
                    non_root.append(dep)
                    
                    # save gov dep representation
                    dep_line[gov].append((dep,par[0]))
                    # update total word number
                    n_word = self.get_nword(n_word, gov, dep)
                    
                    
                else:
                    # add dep to doc
                    if len(dep_line) > 0:                       
                        dep_sentence = {}
                        dep_sentence["data"] = dict(dep_line)
                        dep_sentence["root"] = self.check_root(root, non_root)
                        dep_sentence["nword"] = n_word
                        dep_doc.append(dep_sentence)
                    
                    # reinit temp variable
                    dep_line = defaultdict(list) 
                    root = []
                    non_root = []
                    n_word = 0
                
        return dep_doc
        
    
    '''
    check root and return a root from list
    '''
    def check_root(self, root_list, non_root):
        root = [x for x in root_list if x not in non_root]
        root = list(set(root))
        if len(root) != 1:
            print root
            raise ValueError("root value is not single")
        
        return root[0]
        
    '''
    update number of word in a sentence
    total number of word is the largest dep value
    int current_nword : current total word
    str gov: word number of gov word
    str dep: word number of dep word
    '''
    def get_nword(self, current_nword, gov, dep):
        dep_number = int(dep)
        gov_number = int(gov)
        if gov_number > current_nword:
            current_nword = gov_number
        if dep_number > current_nword:
            current_nword = dep_number
        return current_nword
    
    def test(self, fpath):
        dep_data = self.read(fpath)
        line = 1
        for dep in dep_data:
            print "sentence:",line
            print "nword:", dep["nword"]
            print "root:", dep["root"]
            print dep["data"]
            print
            line += 1
      

class ParseTreeReader:
    
    # bracket char coding
    BRACKET_CHAR = {'-LRB-':'(', '-RRB-':')', '-RSB-':']', '-LSB-':'[', '-LCB-':'{', '-RCB-':'}', "``":"\"", "\'\'":"\""}
    
    def __init__(self):
        # sentences extracted from parse tree
        # format of sentence
        # {string, pos_tag, star, end, other info, ... ....}
        self.sentences = []
    
    '''
    return tree representation in a sentence, order by word number
    {
        nword: 6
        data: [['NP', 'NN', 'XXXX'], ['VP', 'VBZ', 'Inhibits'], ['VP', 'NP', 'NN', 'XXXXXXXX'], ..... ]
    }
    '''
    def read(self, fpath):
        # re-init sentences
        self.sentences = []
        # init variable
        tree_data = []
        stack = []
        
        with open(fpath,'r') as fin:
            for line in fin:
                line_par = line[7:-3].split(' ')
                tree_line = []
                tree_sentence = {}
                nword = 0
                sentence = []
                for par in line_par:
                    if par[0] == '(':
                        # push to stack
                        stack.append(par[1:])
                    else:
                        # found a leave of tree (word)
                        npop = par.count(')')
                        string = self.clean_string(par.rstrip(')'))
                        word_tree = list(stack)
                        word_tree.append(string)
                        for _ in xrange(npop):
                            stack.pop()
                        tree_line.append(word_tree)
                        nword += 1
                        
                        # add word to sentence
                        # {string, pos_tag, star, end, other info, ... ....}
                        word = {"string":string,"pos_tag":word_tree[-2], "score":0.0, "type":"null"}
                        sentence.append(word)
                
                if len(sentence) > 1:
                    tree_sentence["nword"] = nword
                    tree_sentence["data"] = tree_line
                    tree_data.append(tree_sentence)
                    
                    # append sentence
                    self.sentences.append(sentence)
                
        return tree_data
    
    '''
    this function remove coded bracket into bracket char
    ex '-LRB-' => '('
    '''
    def clean_string(self, word):
        for code,char in self.BRACKET_CHAR.iteritems():
            word = word.replace(code,char)
        return word
        
        

    def test(self, fpath):
        tree_data = self.read(fpath)
        line = 1
        for tree in tree_data:
            print "sentence:",line
            print "nword:", tree["nword"]    
            print tree["data"]
            print
            line += 1
            
        print "sentences"
        for sentence in self.sentences:
            print sentence


class ChunkReader:
    
    # bracket char coding
    BRACKET_CHAR = {'-LRB-':'(', '-RRB-':')', '-RSB-':']', '-LSB-':'[', '-LCB-':'{', '-RCB-':'}', "``":"\"", "\'\'":"\""}
    
    '''
    return chunk data for a document
    chunk data is list of chunk in a sentence
    ex chunk in a sentence
    {
        nword: 6
        nchunk: 3
        data: [{'txt': 'XXXX', 'type': 'NP'}, {'txt': 'Inhibits', 'type': 'VP'}, {'txt': 'XXXXXXXX Mediated iTreg Commitment', 'type': 'NP'}]
    }
    '''
    def read(self, fpath):
        chunk_data = []
        with open(fpath, 'r') as fin:
            for line in fin:
                line_par = line[1:-3].split('] [')
                chunks_line = []
                chunk_sentence = {}
                nword = 0
                for par in line_par:                    
                    chk_type,_,text = par.partition(' ') 
                    chunks_line.append({"type":chk_type, "txt":self.clean_string(text)})
                    nword += self.get_nword(text)
                if nword > 1:
                    chunk_sentence["nword"] = nword
                    chunk_sentence["nchunk"] = len(chunks_line)
                    chunk_sentence["data"] = chunks_line
                    chunk_data.append(chunk_sentence)
        return chunk_data
    
    '''
    this function remove coded bracket into bracket char
    ex '-LRB-' => '('
    '''
    def clean_string(self, word):
        for code,char in self.BRACKET_CHAR.iteritems():
            word = word.replace(code,char)
        return word
        
    
    '''
    return number of word in a chunk text
    words are separated by a space
    '''
    def get_nword(self, chunk_text):
        return chunk_text.count(" ") + 1
    
    def test(self, fpath):
        chunk_data = self.read(fpath)        
        line = 1
        for chunks in chunk_data:
            print "sentence:",line
            print "nword:", chunks["nword"]
            print "nchunk:", chunks["nchunk"]       
            print chunks["data"]
            print
            line += 1


if __name__ == "__main__":
    
    source = "E:/corpus/bionlp2011"
    dest = "E:/corpus/bionlp2011/project_data/"
    
    doc_id = "PMC-2222968-33-caption-08"
    
    Reader = GeniaReader(source,dest)
    Reader.run()
    
    
    # testing
    dependency = False
    parse_tree = False
    chunk = False
    sentence = False
    load_doc = False
    
    if dependency:
        dep_fpath = "E:/corpus/bionlp2011/parse/dev/" + doc_id + ".txt.ss.mcccjtok.mcccj.basic.sd"
        Dep = DependencyReader()
        Dep.test(dep_fpath)
    
    if parse_tree:
        tree_fpath = "E:/corpus/bionlp2011/parse/dev/" + doc_id + ".txt.ss.mcccjtok.mcccj"
        Tree = ParseTreeReader()
        Tree.test(tree_fpath)
    
    if chunk:
        chunk_fpath = "E:/corpus/bionlp2011/parse/dev/" + doc_id + ".chk"
        Chunk = ChunkReader()
        Chunk.test(chunk_fpath) 
    
    if sentence:
        tree_fpath = "E:/corpus/bionlp2011/parse/dev/" + doc_id + ".txt.ss.mcccjtok.mcccj"
        protein_fpath = "E:/corpus/bionlp2011/original/dev/" + doc_id + ".a1"
        pretxt_fpath = "E:/corpus/bionlp2011/preprocess/dev/" + doc_id + ".txt"
        
        Reader.get_tree_mcccj(tree_fpath)
        sentences = Reader.get_sentences(pretxt_fpath, True)
                
        for sentence in sentences:
            print sentence
        
    
    if load_doc:
        
        cdir = "dev"
        doc_id = "PMC-2806624-01-INTRODUCTION"
                
        doc = Reader.load_doc(cdir, doc_id)
        Reader.check_consistency(doc)
        Reader.print_doc(doc)
        
        #out_fpath = Reader.dest + '/temp/' + doc_id + '.json'
        #Reader.write_to_file(doc, out_fpath)
        