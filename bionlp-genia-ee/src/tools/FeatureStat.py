'''
Created on Sep 18, 2013

@author: Andresta
'''

import json, os
from model.Dictionary import WordDictionary, TriggerDictionary
from model.Document import DocumentBuilder

from collections import Counter

source = "E:/corpus/bionlp2011/project_data"

WD = WordDictionary(source)    
WD.load("mix")
       
TD = TriggerDictionary(source)
TD.load("mix")

builder = DocumentBuilder(source, WD, TD)

# counter for dependency
edge_cnt = Counter()
len_cnt = Counter()

# counter for chunk
cdist_cnt = Counter()
nprep_cnt = Counter()

# counter for sentence
wdist_cnt = Counter()
wpos_cnt = Counter()


# file name
dep_fname = "dep_stat.csv" 
chk_fname = "chk_stat.csv"
sen_fname = "sen_stat.csv"  


def get_doc_list(cdir):
    with open(os.path.join(source,cdir+'_doc_ids.json'),'r') as f:
        doc_ids = json.loads(f.read())
    return doc_ids

def build_doc(doc_id):                
    doc = builder.read_raw(doc_id)
    return builder.build_doc_from_raw(doc, is_test=False)

def get_rel(rel, tc, ac):    
    for r in rel.data:
        if r[0] == tc and r[1] == ac:
            return r[2]
    return ''

def list_to_string(string_list):
    string = ""
    for s in string_list:
        string += s + '-'
    return string.rstrip('-')   

def extract_doc(o_doc, dependency = False, chunk = False, sen = False):
                
    for i in range(0, len(o_doc.sen)):            
        
        o_sen = o_doc.sen[i]
        rel = o_sen.rel
        tc_list = o_sen.trigger
        ac_list = o_sen.protein + o_sen.trigger
                    
        for tc in tc_list:                               
            for ac in ac_list:
                rel_type = get_rel(rel,tc,ac)
                if rel_type == '' :continue
                if tc == ac: continue
                
                trig_type = o_sen.words[tc]['type']
                arg_type = o_sen.words[ac]['type']
                                
                """ Dependency """
                if dependency:
                    o_dep = o_sen.dep       
                    # length from trigger to argument
                    upath = o_dep.get_shortest_path(tc, ac, "undirected")
                    # edge name                       
                    edges = list_to_string(o_dep.get_edges_name(upath))                        
                    # direct path from trigger to prot                
                    dpath = o_dep.get_shortest_path(tc, ac)
                    direct = 'T' if dpath != [] else 'F'
                    str_len = str(len(upath)-1)
                    
                    write_tsv(dep_fname, [o_doc.doc_id, str(i), str(tc), str(ac), trig_type, arg_type, rel_type, edges, str_len, direct])
                    
                    edge_cnt[edges] += 1
                    len_cnt[str_len] += 1
                    #print i, tc, ac, trig_type, arg_type, rel_type, len(upath)-1, edges, direct
                
                
                """ Chunk """
                if chunk:
                    o_chunk = o_sen.chunk
                    
                    # length from trigger to argument
                    clen = o_chunk.distance(tc, ac)
                    
                    # chunk type for trigger and protein in the same chunk
                    chk_type = ''
                    if clen == 0:
                        chk_type = o_chunk.get_type(tc)
                    
                    # preposition
                    trig_chk_num = o_chunk.chunk_map[tc]
                    arg_chk_num = o_chunk.chunk_map[ac]
                    preps = ''
                    n_prep = 0
                    for chk_num in range(trig_chk_num+1, arg_chk_num):
                        prep = o_chunk.prep_chunk.get(chk_num,'')
                        if prep != '':
                            preps += prep + ','
                            n_prep += 1
                    preps = preps.rstrip(',')
                    
                    # write data
                    write_tsv(chk_fname, [o_doc.doc_id, str(i), str(tc), str(ac), trig_type, arg_type, rel_type, str(clen), chk_type, preps, str(n_prep)])
                    
                    # statistic
                    cdist_cnt[clen] += 1
                    nprep_cnt[n_prep] += 1
                    
                """ Sentence """
                if sen:
                    
                    tword = o_sen.words[tc]
                    
                    # distance between trigger and argument
                    dist = abs(tc - ac)
                    
                    # pos tag
                    pos = tword['pos_tag']
                    
                    # score
                    score = tword['score']
                    
                    # write data
                    #write_tsv(sen_fname, [o_doc.doc_id, str(i), str(tc), str(ac), tword['string'], trig_type, arg_type, rel_type, str(dist), pos, str(score)])
                    
                    # statistic
                    wdist_cnt[dist] += 1
                    wpos_cnt[pos] += 1
                    
                    

def write_tsv(fname, list_string):
    with open(os.path.join(source,'stat',fname),'a') as f:
        f.write('\t'.join(list_string) + '\n')

def delete_stat(fname):
    dep_path = os.path.join(source,'stat',fname)
    if os.path.exists(dep_path):
        os.unlink(dep_path)
        
if __name__ == '__main__':
        
        
    dependency = False
    chunk = False
    sen = True
    
    # delete existing stat
    if dependency:
        delete_stat(dep_fname)        
    if chunk:
        delete_stat(chk_fname)
    if sen:
        delete_stat(sen_fname)
    
    doc_ids = get_doc_list('mix')
    for d in doc_ids:
        print 'extracting',d 
        extract_doc(build_doc(d), dependency, chunk, sen)
    
    if dependency:
        print "Edge Counter"
        for e in edge_cnt.most_common(80):
            print e
            
        print "\n\nLen Counter"
        for e in len_cnt.most_common(20):
            print e
            
    if chunk:
        print "Chunk distance Counter"
        for e in cdist_cnt.most_common(30):
            print e
            
        print "\n\nNumber Preposition Counter"
        for e in nprep_cnt.most_common(20):
            print e
        
    if sen:
        print "Word distance Counter"
        for e in wdist_cnt.most_common(30):
            print e
            
        print "\n\nPos tag Counter"
        for e in wpos_cnt.most_common(20):
            print e
        
            