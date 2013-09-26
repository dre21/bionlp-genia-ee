'''
Created on Sep 26, 2013

@author: Andresta
'''
import re, os
from collections import Counter

mc_counter = Counter()
tp_counter = Counter()
fp_counter = Counter()
fn_counter = Counter()


def get_doc_list(cdir):
    return [d.rstrip('.txt') for d in os.listdir(cdir) if d.endswith('.txt')]

    
def get_trigger_relation(fpath):
    triggers = {}
    events = {}
    equivs = []
    with open(fpath, 'r') as fin:
        for line in fin:
            line = line.rstrip('\n')
            # process trigger
            if line[0] == 'T':
                t = re.split("\\t|\\s+",line,4)
                triggers[int(t[2])] = t
            
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

def compare(source, result, out_dir, doc_id):
    ext = '.a2'
    path1 = source +'/'+ doc_id + ext
    path2 = result +'/'+ doc_id + ext
    
    trigger1, event1, _ = get_trigger_relation(path1)
    trigger2, event2, _ = get_trigger_relation(path2)
    
    t_offset = trigger1.keys() + trigger2.keys()
                
    for offset in sorted(set(t_offset)):
        t1 = trigger1.get(offset,None)
        t2 = trigger2.get(offset,None)
        
        t1_type = ''
        t1_str = ''
        t1_args = []
        t2_type = ''
        t2_str = ''
        t2_args = []
        
        if t1 != None:
            t1_type = t1[1]
            t1_str = t1[4]
            # find argument
            for e in event1.itervalues():
                if e[2] == t1[0]:
                    arg1 = e[3]
                    if arg1 != '':
                        arg1 = arg1 if arg1[0] == 'T' else event1[arg1][2]
                    arg3 = e[5]
                    if arg3 != '':
                        arg3 = arg3 if arg3[0] == 'T' else event1[arg3][2]
                    t1_args.append((arg1,e[4],arg3))
            
        if t2 != None:
            t2_type = t2[1]
            t2_str = t2[4]
            # find argument
            for e in event2.itervalues():
                if e[2] == t2[0]:
                    arg1 = e[3]
                    if arg1 != '':
                        arg1 = arg1 if arg1[0] == 'T' else event2[arg1][2]
                    arg3 = e[5]
                    if arg3 != '':
                        arg3 = arg3 if arg3[0] == 'T' else event2[arg3][2]
                    t2_args.append((arg1,e[4],arg3))
        
            
        write_tsv(out_dir, doc_id, offset, t1_type, t1_str, t1_args, t2_type, t2_str, t2_args) 
    
    
def write_tsv(out_dir, doc_id, offset, t1_type, t1_str, t1_args, t2_type, t2_str, t2_args):
    fname = 'RESULT_ANALYSIST.csv'
    
    str_t1_args = str(t1_args)[1:-1]
    str_t2_args = str(t2_args)[1:-1]
    
    list_string = [doc_id, str(offset), t1_type, t1_str, str_t1_args, t2_type, t2_str, str_t2_args]
        
    if t1_type == t2_type: 
        result_t = 'TP'
        tp_counter[doc_id] += 1
    elif t1_type == '': 
        result_t = 'FP'
        fp_counter[doc_id] += 1
    elif t2_type == '': 
        result_t = 'FN'
        fn_counter[doc_id] += 1
    else: 
        result_t = 'MC'
        mc_counter[doc_id] += 1
    list_string.append(result_t)
         
    result_a = 'OK' if str_t1_args == str_t2_args else 'NO'
    list_string.append(result_a)
                
    with open(os.path.join(out_dir,fname),'a') as f:
        f.write('\t'.join(list_string) + '\n')
        
        
if __name__ == '__main__':
    source = 'E:/corpus/bionlp2011/original/dev/'
    result = 'E:/corpus/bionlp2011/project_data/result/'
    out_dir = result
    model = 'test-model-021'
    
    for doc_id in get_doc_list(source):
        compare(source,result+model,out_dir,doc_id)
    
    print "True positive counter"
    for i in tp_counter.most_common(25):
        print i
        
    print "\nFalse positive counter"
    for i in fp_counter.most_common(25):
        print i
        
    print "\nFalse negative counter"
    for i in fn_counter.most_common(25):
        print i
        
    print "\nMiss classified counter"
    for i in mc_counter.most_common(25):
        print i
    