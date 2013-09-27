'''
Created on Sep 5, 2013

@author: Andresta
'''

class Relation(object):
    '''
    classdocs
    '''

    
    def __init__(self):
        '''
        Constructor
        '''
        
        # list to store relation 
        # (8,10,'Theme','E')
        self.data = []
        
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
            
        for e in events.itervalues():
            # only process if trigger in entity map
            if e[2] in entity_map.keys():
                # get word number for trigger
                t_wn = entity_map[e[2]]
                
                # process argument, it's mandatory        
                args = self.get_equiv_protein(e[3], equiv)                      
                for arg in args:                  
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
                        self.add_relation(t_wn, arg_wn, "Theme", arg_type)
                    else:
                        #print "inter-sentence relation", e
                        self.out_scope.append(e)
                    
                
                # process argument 2 for binding, it's optional                
                if e[4] != '':
                    args = self.get_equiv_protein(e[4], equiv)      
                    for arg in args:  
                        arg_wn = entity_map.get(args, -1)
                        # add relation for trigger and 2nd binding argument
                        if arg_wn >= 0:
                            self.add_relation(t_wn, arg_wn, "Theme2", "P")
                        else:
                            #print "inter-sentence relation", e
                            self.out_scope.append(e)
                    
                # process argument 2 for cause, it's optional
                if e[5] != '':
                    args = self.get_equiv_protein(e[5], equiv)      
                    for arg in args:                                    
                        arg_type = "P"
                        if arg[0] == 'E':
                            # arg is trigger of other event
                            arg = events[arg][2]
                            arg_type = "E"
                        
                        arg_wn = entity_map.get(arg, -1)                
                        # add relation for trigger and cause argument
                        if arg_wn >= 0:
                            self.add_relation(t_wn, arg_wn, "Cause", arg_type)
                        else:
                            #print "inter-sentence relation", e
                            self.out_scope.append(e)
                        
        self.data = list(set(self.data)) 
               
    def get_equiv_protein(self, arg, equiv_list):
        proteins = [arg]
        for equiv in equiv_list:
            if arg in equiv:
                proteins = list(equiv)
                break
        return proteins
                                               
    def add_relation(self, trigger_wn, arg_wn, arg_name, arg_type):
        """
        adding a relation data
        trigger_wn: word number of a trigger
        arg_wn: word number of a argument
        arg_name: "Theme", "Binding2", "Cause"
        arg_type: "P", or "E"
        """
        rel_tuple = (trigger_wn, arg_wn, arg_name, arg_type)
        # check duplicate
        if rel_tuple not in self.data:
            self.data.append(rel_tuple)
    
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
    