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
        self._path = path
        
        
    def write(self, o_doc):
        # relation 
        # (27, 35, 'Theme', 'P'), (6, 5, 'Theme', 'E')
        #print "writing:", o_doc.doc_id        
        trigger_list, mapping_offset = self.create_trigger(o_doc)
        
        event_list = self.create_relation(o_doc, mapping_offset)
        
        path = self._path + '/' + o_doc.doc_id + self.A2_EXT
        
        
        with open(path,'wb') as f:            
            # write trigger
            for t in trigger_list:
                f.write(t[0] + '\t' + t[1] + ' ' + str(t[2]) + ' ' + str(t[3]) + '\t' + t[4] + '\n')
        
            # write event
            # event list: 1 [u'Negative_regulation', 'T60', 'Theme', 'E2', 'E', 'Cause', 'T4', 'P']
            for eid, evt in event_list.iteritems():
                f.write('E'+str(eid) + '\t' + evt[0] + ':' + evt[1] + ' Theme:' + evt[3])
                # if there is second argument
                if len(evt) > 5:
                    f.write(' ' + evt[5] + ':' + evt[6])                
                f.write('\n')
        
        '''
        print '\n\n'
        for k,v in sorted(mapping_offset.iteritems()):
            print k,v
        '''
        
    def create_trigger(self, o_doc):
        prot_count = 0        
        temp_triggers = []
        trigger_list = []
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
                temp_triggers.append((word['type'],word['start'],word['end'],word['string']))
                
        # make a dictionary with key is trigger id
        trig_num = prot_count + 1
        for i in range(0,len(temp_triggers)):
            t = temp_triggers[i]
            trigger_id = 'T'+str(trig_num)
            trigger_list.append(tuple([trigger_id]) + t)
            
            # mapping for trigger
            mapping_offset[t[1]] = trigger_id 
            
            trig_num += 1
            
        return trigger_list, mapping_offset
    
    def create_relation(self, o_doc, mapping_offset):
        all_events = {}
        event_cnt = 1        
        for sen in o_doc.sen:
            events = {}                        
            trig_evt_map = defaultdict(list)
            
            '''
            print '\n----------------', sen.number, '----------------'
            for k,v in sen.rel.data.iteritems():
                print 'rel:', k,v
            print '\n'
            '''         
            # duplicating argument
            for _ in range(0,3):
                duplicate = defaultdict(list)
                for trig, args in sen.rel.data.iteritems():
                    for arg in args:                    
                        if len(arg) > 3:
                            total_dup = 1
                            if arg[2] == 'E': total_dup = total_dup * len(sen.rel.data[arg[0]])
                            if arg[5] == 'E': total_dup = total_dup * len(sen.rel.data[arg[3]])
                            
                            if args.count(arg) != total_dup :
                                for _ in range(1,total_dup):
                                    duplicate[trig].append(arg)
                        else:                        
                            if arg[2] == 'E' and args.count(arg) != len(sen.rel.data[arg[0]]):
                                for _ in range(1,len(sen.rel.data[arg[0]])):
                                    duplicate[trig].append(arg)
                        
                # update relation with duplicate
                for trig, args in duplicate.iteritems():
                    sen.rel.data[trig] += args
            
            # relation items
            # 8 : [(10,'Theme','P',12,'Theme','P'), (18,'Theme','P',20,'Theme','P')]
            for trig, args in sen.rel.data.iteritems():
                # get trigger id
                t_word = sen.words[trig]
                t_offset = t_word['start']
                t_type = t_word['type']
                                
                # get all arguments group                
                sorted_args = sorted(args, key=lambda x: len(x))
                #print args, sorted_args
                for arg in sorted_args:
                    # adding trigger to event dict
                    events[event_cnt] = [t_type, mapping_offset[t_offset]]
                    trig_evt_map[mapping_offset[t_offset]].append(event_cnt)
                    
                    # get argument 1                    
                    a1_word = sen.words[arg[0]]
                    a1_offset = a1_word['start']
                    # adding arg1 name to event dict
                    events[event_cnt].append(arg[1])
                    # adding arg1 id to event dict
                    events[event_cnt].append(mapping_offset[a1_offset])
                    # adding arg1 type (P or E) to event dict
                    events[event_cnt].append(arg[2])
                                                            
                    # get argument 2 if exist
                    if len(arg) > 3:
                        a2_word = sen.words[arg[3]]
                        a2_offset = a2_word['start']
                        # adding arg2 name to event dict
                        events[event_cnt].append(arg[4])
                        # adding arg2 id to event dict
                        events[event_cnt].append(mapping_offset[a2_offset])
                        # adding arg2 type (P or E) to event dict
                        events[event_cnt].append(arg[5])
                
                    event_cnt += 1
                    
            # update trigger with event id
            tcnt = {}
            for k,v in trig_evt_map.iteritems():
                tcnt[k] = len(v)
                #print k, len(v)
           
            used_event = []
            for e_id, evt in events.iteritems():          
                #print e_id,evt      
                if len(evt) > 5:
                    # both argument to replace
                    if  evt[4] == 'E' and evt[7] == 'E':
                        tid1 = evt[3]
                        tid2 = evt[6]
                        offset1 = tcnt[tid1] - 1
                        offset2 = tcnt[tid2] - 1                        
                        #print 'tid1-offset',tid1, offset1
                        #print 'tid2-offset',tid2, offset2
                        tmp_evt = list(evt)
                        tmp_evt[3] = 'E' + str(trig_evt_map[tid1][offset1])
                        tmp_evt[6] = 'E' + str(trig_evt_map[tid2][offset2])
                        #print 'tmp:', tmp_evt 
                        #print 'used:',used_event
                        if tmp_evt in used_event:
                            #print 'in used'
                            tcnt[tid1] -= 1
                            if tcnt[tid1] == 0: 
                                tcnt[tid1] = len(trig_evt_map[tid1])
                                tcnt[tid2] -= 1
                                if tcnt[tid2] == 0: tcnt[tid2] = len(trig_evt_map[tid2])
                            tid1 = evt[3]
                            tid2 = evt[6]
                            offset1 = tcnt[tid1] - 1
                            offset2 = tcnt[tid2] - 1                        
                            #print 'tid1-offset',tid1, offset1
                            #print 'tid2-offset',tid2, offset2
                            evt[3] = 'E' + str(trig_evt_map[tid1][offset1])
                            evt[6] = 'E' + str(trig_evt_map[tid2][offset2])
                        else:
                            #print 'not used'
                            evt[3] = 'E' + str(trig_evt_map[tid1][offset1])
                            evt[6] = 'E' + str(trig_evt_map[tid2][offset2])
                        used_event.append(evt)
                        
                    # event with only argument1 to replace
                    elif evt[4] == 'E':
                        tid = evt[3]
                        offset = tcnt[tid] - 1                        
                        #print 'tid-offset',tid, offset
                        tmp_evt = list(evt)
                        tmp_evt[3] = 'E' + str(trig_evt_map[tid][offset])
                        #print 'tmp:', tmp_evt, 
                        #print 'used:',used_event
                        if tmp_evt in used_event:
                            tcnt[tid] -= 1
                            if tcnt[tid] == 0: tcnt[tid] = len(trig_evt_map[tid])
                            tid = evt[3]
                            offset = tcnt[tid] - 1                        
                            #print 'tid-offset',tid, offset
                            evt[3] = 'E' + str(trig_evt_map[tid][offset])
                        else:
                            evt[3] = 'E' + str(trig_evt_map[tid][offset])
                        used_event.append(evt)
                    # event with only argument2 to replace
                    elif evt[7] == 'E':
                        tid = evt[6]
                        offset = tcnt[tid] - 1                        
                        #print 'tid-offset',tid, offset
                        tmp_evt = list(evt)
                        tmp_evt[6] = 'E' + str(trig_evt_map[tid][offset])
                        #print 'tmp:', tmp_evt, 
                        #print 'used:',used_event
                        if tmp_evt in used_event:
                            tcnt[tid] -= 1
                            if tcnt[tid] == 0: tcnt[tid] = len(trig_evt_map[tid])
                            tid = evt[6]
                            offset = tcnt[tid] - 1                        
                            #print 'tid-offset',tid, offset
                            evt[6] = 'E' + str(trig_evt_map[tid][offset])
                        else:
                            evt[6] = 'E' + str(trig_evt_map[tid][offset])
                        used_event.append(evt)
                else:
                    # event with only 1 argument
                    if evt[4] == 'E':
                        tid = evt[3]
                        offset = tcnt[tid] - 1                        
                        #print 'tid-offset',tid, offset
                        tmp_evt = list(evt)
                        tmp_evt[3] = 'E' + str(trig_evt_map[tid][offset])
                        #print 'tmp:', tmp_evt, 
                        #print 'used:',used_event
                        if tmp_evt in used_event:
                            tcnt[tid] -= 1
                            if tcnt[tid] == 0: tcnt[tid] = len(trig_evt_map[tid])
                            tid = evt[3]
                            offset = tcnt[tid] - 1                        
                            #print 'tid-offset',tid, offset
                            evt[3] = 'E' + str(trig_evt_map[tid][offset])
                        else:
                            evt[3] = 'E' + str(trig_evt_map[tid][offset])
                        used_event.append(evt)
                             
            #for k,v in trig_evt_map.iteritems():
            #    print k,v
            #for k,v in events.iteritems():
            #    print k,v
            all_events.update(events)
        return all_events
            
        
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
                
                #print t_offset, a_offset, t_word["type"], e[2], e[3]
                 
        
        
        # count number of event for each trigger
        event_cnt = {}        
        for trig_id in sorted(event_name.keys()):
            n_evt = len(event_arg1_pair[trig_id]) 
            if len(event_arg2_pair[trig_id]) > 0:
                n_evt = n_evt * len(event_arg2_pair[trig_id])
            #print trig_id, n_evt
            event_cnt[trig_id] = n_evt
        
        '''
        print '\nevent_arg1_pair'
        for k,v in event_arg1_pair.iteritems():
            print k,v
        print '\nevent_arg2_pair'
        for k,v in event_arg2_pair.iteritems():
            print k,v
        '''
            
        # build event dict
        events = {}
        for trig_id, trig_type in sorted(event_name.iteritems()):
            '''
            print '\nTrigID - TrigType'
            print trig_id, trig_type
            '''
            events[trig_id] = []
            for arg1 in event_arg1_pair[trig_id]:    
                '''print 'arg1:',arg1'''
                # if there is no second argument      
                if event_arg2_pair[trig_id] == []:
                    
                    # handle duplication for trigger-trigger event
                    theme_duplicate = event_cnt.get(arg1[0], 1)
                    for i in range (1,theme_duplicate+1):
                                            
                        events[trig_id].append({'type':trig_type,
                                                'theme':arg1[0],
                                                'theme-type':arg1[2],
                                                'arg-dup':i})
                        
                # there is second argument either theme2 for binding or cause for regulation    
                else:
                    for arg2 in event_arg2_pair[trig_id]:
                                                 
                        # handle duplication for trigger-trigger event
                        theme_duplicate = event_cnt.get(arg1[0], 1)
                        theme2_duplicate = event_cnt.get(arg2[0], 1)                        
                        for i in range(1, theme_duplicate + 1):
                            for j in range(1, theme2_duplicate + 1):
                        
                                temp_dict = {'type':trig_type,
                                             'theme':arg1[0],
                                             'theme-type':arg1[2],
                                             'arg-dup':i,
                                             'arg2-dup':j,}
                                
                                if arg2[1] == 'Cause':
                                    temp_dict['cause'] = arg2[0]
                                    temp_dict['cause-type'] = arg2[2]
                                elif arg2[1] == 'Theme2' and trig_type == 'Binding':
                                    temp_dict['theme2'] = arg2[0]
                                    temp_dict['theme2-type'] = arg2[2]
                                else:
                                    raise ValueError('No option for this')
                                
                                events[trig_id].append(temp_dict)                        
        
        
        # event number mapping
        event_num = 1
        event_num_map = {}
        for k,v in sorted(events.iteritems()):
            for i in range(0, len(v)):
                key = str(k) +'-'+ str(i+1)
                val = 'E' + str(event_num)
                event_num_map[key] = val 
                event_num += 1
        '''
        print '\nEvents'
        for k,v in sorted(events.iteritems()):
            print k,v
            
        print '\nEvent_num_map'
        for k,v in sorted(event_num_map.iteritems()):
            print k,v
        '''
                
        # construct final event list
        event_list = []
        for k,v in sorted(events.iteritems()):
            for i in range(0, len(v)):
                e = v[i]
                evt_id = event_num_map[str(k) +'-'+ str(i+1)]
                evt_type = e['type']
                trig_id = mapping_offset[k]                
                
                # process theme1
                if e['theme-type'] == 'P':
                    theme1_id = mapping_offset[e['theme']]
                else:
                    theme1_id = event_num_map[str(e['theme']) +'-'+ str(e['arg-dup'])]
                                                
                # process theme2
                theme2_id = e.get('theme2','')
                if theme2_id != '':
                    theme2_id = mapping_offset[theme2_id]
                    
                # process cause                
                cause_type = e.get('cause-type','')
                if cause_type == 'P':
                    cause_id = mapping_offset[e['cause']]
                elif cause_type == 'E':
                    cause_id = event_num_map[str(e['cause']) +'-'+ str(e['arg2-dup'])]
                else:
                    cause_id = ''
                
                event_list.append((evt_id,evt_type,trig_id,theme1_id,theme2_id,cause_id))
                 
        return event_list
    
    
    
    