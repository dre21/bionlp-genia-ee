'''
Created on Sep 5, 2013

@author: Andresta
'''

from collections import defaultdict 

class Relation(object):
    '''
    classdocs
    '''

    
    def __init__(self):
        '''
        Constructor
        '''
        
        # dict to store relation 
        # 8 : [(10,'Theme','P',12,'Theme','P'), (18,'Theme','P',20,'Theme','P')]
        # 0 : [(3,'Theme','E',12,'Cause','P')]
        # 10 : [(0,'Theme','P',-1,'','')]
        self.data = defaultdict(list)
        
        # this is a list to store inter-sentence relation
        # it will not process
        self.out_scope = []
        
        
    def build(self, entity_map, events, equiv):
        """
        build a relation from events data
        event is a dictionary form
        'E1' : ['E1', 'Negative_regulation', 'T60', 'E2', '', 'T4']
        entity_map is a dictionary
        'T60' : 8
        equiv is list of tuple
        [('T1','T2'),('T5','T6')]
        """
        if type(entity_map) != dict:
            raise TypeError("entity_map must be a dictionary")

        if entity_map == {}: return
        
        # for each event
        for e in events.itervalues():
            # only process if trigger in entity map
            if e[2] not in entity_map.keys(): continue
                    
            # get word number for trigger
            t_wn = entity_map[e[2]]
            
            # process argument, it's mandatory                            
            arg = e[3]
            arg_type = "P"
            if arg[0] == 'E':
                # arg 1 is trigger of other event
                arg = events[arg][2]
                arg_type = "E"
            # get word number for argument
            # word number may not be found in trigger entity
            # because inter sentence relation, need co-reference to solve this
            arg_wn = entity_map.get(arg, -1)
            
            # add relation for trigger and first argument
            if arg_wn >= 0:                
                arg1_tuple = (arg_wn,'Theme',arg_type)
            else:                
                self.out_scope.append(e)
                break
            arg2_tuple = ()       
            
            # process argument 2 for binding, it's optional                
            if e[4] != '':
                arg = e[4]      
                arg_wn = entity_map.get(arg, -1)
                # add relation for trigger and 2nd binding argument
                if arg_wn >= 0:
                    arg2_tuple = (arg_wn,'Theme2','P')
                else:                    
                    self.out_scope.append(e)
                
            # process argument 2 for cause, it's optional
            elif e[5] != '':
                arg = e[5]                                          
                arg_type = "P"
                if arg[0] == 'E':
                    # arg is trigger of other event
                    arg = events[arg][2]
                    arg_type = "E"                
                # get word number for argument
                arg_wn = entity_map.get(arg, -1)                
                # add relation for trigger and cause argument
                if arg_wn >= 0:
                    arg2_tuple = (arg_wn,'Cause',arg_type)
                else:
                    self.out_scope.append(e)
                    
            # add event to relation data
            self.add_relation(t_wn, arg1_tuple, arg2_tuple)
            #self.data[t_wn].append(arg1_tuple + arg2_tuple)
           
               
    def get_equiv_protein(self, arg, equiv_list):
        proteins = [arg]
        for equiv in equiv_list:
            if arg in equiv:
                proteins = list(equiv)
                break
        return proteins
                                               
    def add_relation(self, trigger_wn, arg1_tuple, arg2_tuple = ()):
        """
        adding a relation data
        trigger_wn: word number of a trigger
        arg_wn: word number of a argument
        arg_name: "Theme", "Theme2", "Cause"
        arg_type: "P", or "E"
        """
        args_tuple = arg1_tuple + arg2_tuple
        
        # check duplicate        
        if args_tuple not in self.data[trigger_wn]:
            self.data[trigger_wn].append(args_tuple)

    def check_simple_relation(self, trigger_wn, arg_wn, arg_type = "P"):
        """
        simple relation only has protein as argument
        and there is no argument 2
        """
        retval = False
        relations = self.data.get(trigger_wn,[])
        for rel in relations:
            # rel = (10,'Theme','P')
            # argument1 will always a 'theme'
            cond1 = arg_wn == rel[0]
            cond2 = arg_type == rel[2]            
            if cond1 and cond2:
                return True
        return retval

    '''    
    def get_tp_triger(self):
        """
        return list of trigger node (word number) which has trigger-protein relation
        it's used to get argument candidate of trigger-trigger relation
        """
        trig = []
        for rel in self.data:            
            if rel[2] == "Theme" and rel[3] == "P":
                trig.append(rel[0])
        return trig
    
    def get_tptt_triger(self):
        """
        return list of trigger node (word number) which has relation
        it's used to get argument candidate of trigger-trigger relation
        """
        trig = []
        for rel in self.data:            
            if rel[2] == "Theme":
                trig.append(rel[0])
        return trig
        
    def get_theme(self, trigger_wn):
        """
        return argument1 word number list of a given trigger_wn
        """
        arg1 = []
        
        if type(trigger_wn) != list:
            trigger_wn = [trigger_wn]
        
        for rel in self.data:
            if rel[0] in trigger_wn and rel[2][0:5] == 'Theme':
                arg1.append(rel[1])
                
        return arg1
    
    def check_relation(self,trigger_wn, arg_wn, arg_name = "Theme", arg_type = "P"):
        retval = False
        for rel in self.data:
            if tuple([trigger_wn, arg_wn, arg_name, arg_type]) == rel:
                return True
        return retval
    
    def check_pair(self, trigger_wn, arg_wn):
        retval = False
        for rel in self.data:
            cond1 = trigger_wn + arg_wn == rel[0] + rel[1]
            cond2 = abs(trigger_wn - arg_wn) == abs(rel[0] - rel[1])
            if cond1 and cond2: retval = True
        return retval
    
    
    def delete_relation(self, trigger_wn, arg_wn, arg_name = "Theme", arg_type = "P"):
                
        if self.check_relation(trigger_wn, arg_wn, arg_name, arg_type):
            rel_tuple = (trigger_wn, arg_wn, arg_name, arg_type)
            self.data.remove(rel_tuple)
            return True
        
        return False
    
    '''
            