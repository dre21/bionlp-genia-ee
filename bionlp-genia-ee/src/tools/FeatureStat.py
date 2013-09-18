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
WD.load("train")
       
TD = TriggerDictionary(source)
TD.load("train")

builder = DocumentBuilder(source, WD, TD)

# counter for dependency
edge_cnt = Counter()
len_cnt = Counter()

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

def extract_doc(o_doc):
            
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
                o_dep = o_sen.dep       
                # length from trigger to argument
                upath = o_dep.get_shortest_path(tc, ac, "undirected")
                # edge name                       
                edges = list_to_string(o_dep.get_edges_name(upath))                        
                # direct path from trigger to prot                
                dpath = o_dep.get_shortest_path(tc, ac)
                direct = 'T' if dpath != [] else 'F'
                str_len = str(len(upath)-1)
                
                #write_csv("dep_stat.csv", [o_doc.doc_id, str(i), str(tc), str(ac), trig_type, arg_type, rel_type, edges, str_len, direct])
                
                edge_cnt[edges] += 1
                len_cnt[str_len] += 1
                #print i, tc, ac, trig_type, arg_type, rel_type, len(upath)-1, edges, direct

def write_csv(fname, list_string):
    with open(os.path.join(source,'stat',fname),'a') as f:
        f.write(','.join(list_string) + '\n')


if __name__ == '__main__':
    
    dep_fname = "dep_stat.csv"
    
    # delete previous stat
    dep_path = os.path.join(source,'stat',dep_fname)
    if os.path.exists(dep_path):
        os.unlink(dep_path)
    
    doc_ids = get_doc_list('mix')
    for d in doc_ids:
        print 'extracting',d 
        extract_doc(build_doc(d))
        
    print "Edge Counter"
    for e in edge_cnt.most_common(80):
        print e
        
    print "\n\nLen Counter"
    for e in len_cnt.most_common(20):
        print e
        
        