'''
Created on Sep 14, 2013

@author: Andresta
'''
from collections import defaultdict

class GeniaA2Writer(object):
    '''
    classdocs
    '''
    
    # extension for a2 file
    A2_EXT = ".a2"

    def __init__(self, path):
        '''
        Constructor
        '''
        self.path = path
        
        
    def write(self, o_doc):
        # relation 
        # (27, 35, 'Theme', 'P'), (6, 5, 'Theme', 'E')
        trigger_dict, mapping_offset = self.build_trigger(o_doc)
        
        self.build_relation(o_doc, mapping_offset)
        
        
        
        '''
        for k,v in sorted(trigger_dict.iteritems()):
            print k,v
        
        print '\n\n'
        for k,v in sorted(mapping_offset.iteritems()):
            print k,v
        '''
        
    def build_trigger(self, o_doc):
        prot_count = 0        
        triggers = []
        trigger_dict = {}
        # mapping offset to entity id
        # offset: entity_id
        mapping_offset = {}
        
        for sen in o_doc.sen:           
            # mapping for protein
            for p in sorted(sen.protein):
                prot_count += 1
                word = sen.words[p]
                mapping_offset[word['start']] = 'T' + str(prot_count)
            
            for t in sorted(sen.trigger):
                word = sen.words[t]
                triggers.append((word['type'],word['start'],word['end'],word['string']))
                
        # make a dictionary with key is trigger id
        trig_num = prot_count + 1
        for i in range(0,len(triggers)):
            trigger = triggers[i]
            trigger_id = 'T'+str(trig_num)
            trigger_dict[trigger_id] = trigger
            
            # mapping for trigger
            mapping_offset[trigger[1]] = trigger_id 
            
            trig_num += 1
            
        return trigger_dict, mapping_offset
        
    def build_relation(self, o_doc, mapping_offset):
        
        event_name = {}
        event_arg1_pair= defaultdict(list)
        event_arg2_pair= defaultdict(list)
        
        for sen in o_doc.sen:
            # e is tuple (8, 10, 'Theme', 'E') 
            for e in sen.rel.data:
                
                # get trigger id
                t_word = sen.words[e[0]]
                t_offset = t_word["start"]                                
                
                # get argument id
                a_word = sen.words[e[1]]
                a_offset = a_word["start"]                                
                
                event_name[t_offset] = t_word["type"]
                if e[2] == 'Theme':
                    # this is for argument 1
                    event_arg1_pair[t_offset].append((a_offset, e[2], e[3]))
                else:
                    # this is for argument 2, either cause or theme2
                    event_arg2_pair[t_offset].append((a_offset, e[2], e[3]))
                
                print t_offset, a_offset, t_word["type"], e[2], e[3]
                 
        events = {}
        for trig_id, trig_type in sorted(event_name.iteritems()):
            for arg1 in event_arg1_pair[trig_id]:          
                if event_arg2_pair[trig_id] == []:
                    print trig_id, trig_type, arg1
                else:
                    for arg2 in event_arg2_pair[trig_id]:
                        print trig_id, trig_type, arg1, arg2 
            
            
            
            