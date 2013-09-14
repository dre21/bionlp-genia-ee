'''
Created on Sep 14, 2013

@author: Andresta
'''
import os, re
from collections import Counter


def get_doc_path(source, dir_list):
    doc_path = []
    for cdir in dir_list:
        path = source + '/original/' + cdir
        doc_path += [path +'/'+ d.rstrip('.txt') for d in os.listdir(path) if d.endswith('.txt')]
    return doc_path


def check_duplicate_offset_entity(source):
    
    prot_duplicate = []
    trig_duplicate = []
    trigger_word = Counter()
    
    doc_path = get_doc_path(source, ["dev","train","test"])    
    for path in doc_path:
        last_offset = -1
        with open(path + '.a1', 'r') as f:
            for line in f:
                line = line.rstrip('\n')
                p = re.split("\\t|\\s+",line,4)
                cur_offset = int(p[2])
                if last_offset == cur_offset:
                    prot_duplicate.append(path)
                    break
                else:
                    last_offset = cur_offset
    
    doc_path = get_doc_path(source, ["dev","train"])      
    for path in doc_path:
        last_offset = -1
        with open(path + '.a2', 'r') as f:
            for line in f:
                if line[0] != 'T': continue                
                line = line.rstrip('\n')
                t = re.split("\\t|\\s+",line,4)
                cur_offset = int(t[2])
                if last_offset == cur_offset:
                    trig_duplicate.append(path + '\t' + t[4])
                    trigger_word[t[4]] += 1
                    break
                else:
                    last_offset = cur_offset
    
    print "====================================="
    print "protein duplicate offset:", len(prot_duplicate)    
    for path in prot_duplicate:
        print path
    
    print "\n\n====================================="
    print "trigger duplicate offset:", len(trig_duplicate)
    for i in range(0, len(trig_duplicate)):
        print trig_duplicate[i]
    
    print "\n\n====================================="
    print "List of word with more than 1 tag:"
    for pair in trigger_word.most_common(40):
        print pair
    

if __name__ == '__main__':
    source = "E:/corpus/bionlp2011"
    
    check_duplicate_offset_entity(source)