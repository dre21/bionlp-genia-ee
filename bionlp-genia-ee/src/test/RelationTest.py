'''
Created on Sep 11, 2013

@author: Andresta
'''

from model.Relation import Relation

class RelationTest(object):
    '''
    classdocs
    '''


    def __init__(self):
        '''
        Constructor
        '''
        print "Running relation test\n==================="
       
    def run(self):
        self.test1()             
        
    def test1(self):
        entity_map = {'T3':2, 'T7':18, 'T6': 12,'T4': 4,'T5': 9,'T61': 10,'T60': 8}
        equiv = {('T1','T2'),('T3','T4'),('T6','T7')}
        event = {"E19": ["E19", "Regulation", "T74", "E16", "", "T27"], "E18": ["E18", "Regulation", "T74", "E15", "", "T28"], "E31": ["E31", "Gene_expression", "T85", "T58", "", ""], "E30": ["E30", "Negative_regulation", "T84", "E31", "", "T59"], "E11": ["E11", "Positive_regulation", "T69", "T20", "", "T22"], "E10": ["E10", "Positive_regulation", "T69", "T20", "", "T21"], "E13": ["E13", "Gene_expression", "T71", "T24", "", ""], "E12": ["E12", "Negative_regulation", "T70", "E13", "", "T23"], "E15": ["E15", "Phosphorylation", "T73", "T25", "", ""], "E14": ["E14", "Positive_regulation", "T72", "E12", "", ""], "E17": ["E17", "Regulation", "T74", "E15", "", "T27"], "E16": ["E16", "Phosphorylation", "T73", "T26", "", ""], "E9": ["E9", "Gene_expression", "T68", "T19", "", ""], "E8": ["E8", "Positive_regulation", "T67", "E9", "", "T18"], "E5": ["E5", "Gene_expression", "T64", "T15", "", ""], "E4": ["E4", "Positive_regulation", "T63", "E5", "", "T14"], "E7": ["E7", "Negative_regulation", "T66", "T17", "", ""], "E6": ["E6", "Negative_regulation", "T65", "T16", "", "E7"], "E1": ["E1", "Negative_regulation", "T60", "E2", "", "T4"], "E3": ["E3", "Negative_regulation", "T62", "E4", "", "T13"], "E2": ["E2", "Positive_regulation", "T61", "T6", "", "T5"], "E24": ["E24", "Gene_expression", "T78", "T35", "", ""], "E25": ["E25", "Gene_expression", "T79", "T55", "", ""], "E26": ["E26", "Negative_regulation", "T80", "E25", "", "T54"], "E27": ["E27", "Negative_regulation", "T81", "E28", "", "T56"], "E20": ["E20", "Regulation", "T74", "E16", "", "T28"], "E21": ["E21", "Positive_regulation", "T75", "T31", "", ""], "E22": ["E22", "Positive_regulation", "T76", "T32", "", "E21"], "E23": ["E23", "Negative_regulation", "T77", "T33", "", "E21"], "E28": ["E28", "Gene_expression", "T82", "T57", "", ""], "E29": ["E29", "Regulation", "T83", "E27", "", ""]}
        rel = Relation()
        rel.build(entity_map, event, equiv)
        for t,args in rel.data.iteritems():
            print t,args
        print rel.out_scope
        #print "trigger tp:", rel.get_tp_triger()
    
    
    
        
        
        
if __name__ == '__main__':
    
    test = RelationTest()
    test.run()
    
    