'''
Created on Sep 13, 2013

@author: Andresta
'''

from model.Dictionary import TriggerDictionary, WordDictionary
from model.SentenceAnalyzer import SentenceAnalyzer

class SentenceAnalyzerTest(object):
    '''
    classdocs
    '''


    def __init__(self):
        '''
        Constructor
        '''
        source = "E:/corpus/bionlp2011/project_data/"
    
        WD = WordDictionary(source)    
        WD.load("dev")
       
        TD = TriggerDictionary(source)
        TD.load("dev")
                    
        self.TC = SentenceAnalyzer(WD, TD)
        
    def run(self):
        self.test1()
        self.test2()
    
    def test1(self):
        sen = [{'pos_tag': 'PRP', 'end': 149, 'string': 'We', 'stem': 'We', 'start': 147, 'score': 0.0, 'type': 'null'}, {'pos_tag': 'RB', 'end': 159, 'string': 'therefore', 'stem': 'therefor', 'start': 150, 'score': 0.0, 'type': 'null'}, {'pos_tag': 'VBD', 'end': 165, 'string': 'asked', 'stem': 'ask', 'start': 160, 'score': 0.0, 'type': 'null'}, {'pos_tag': 'IN', 'end': 173, 'string': 'whether', 'stem': 'whether', 'start': 166, 'score': 0.0, 'type': 'null'}, {'pos_tag': 'NN', 'end': 178, 'string': 'XXXX', 'stem': 'XXXX', 'start': 174, 'score': 0.0, 'type': 'null'}, {'pos_tag': 'VBZ', 'end': 181, 'string': 'is', 'stem': 'is', 'start': 179, 'score': 0.0, 'type': 'null'}, {'pos_tag': 'JJ', 'end': 186, 'string': 'able', 'stem': 'abl', 'start': 182, 'score': 0.0, 'type': 'null'}, {'pos_tag': 'TO', 'end': 189, 'string': 'to', 'stem': 'to', 'start': 187, 'score': 0.0, 'type': 'null'}, {'pos_tag': 'VB', 'end': 197, 'string': 'inhibit', 'stem': 'inhibit', 'start': 190, 'score': 0.0, 'type': 'null'}, {'pos_tag': 'NN', 'end': 206, 'string': 'XXXXXXXX', 'stem': 'XXXXXXXX', 'start': 198, 'score': 0.0, 'type': 'null'}, {'pos_tag': 'NN', 'end': 216, 'string': 'induction', 'stem': 'induct', 'start': 207, 'score': 0.0, 'type': 'null'}, {'pos_tag': 'IN', 'end': 219, 'string': 'of', 'stem': 'of', 'start': 217, 'score': 0.0, 'type': 'null'}, {'pos_tag': 'NN', 'end': 225, 'string': 'XXXXX', 'stem': 'XXXXX', 'start': 220, 'score': 0.0, 'type': 'null'}, {'pos_tag': 'IN', 'end': 232, 'string': 'during', 'stem': 'dure', 'start': 226, 'score': 0.0, 'type': 'null'}, {'pos_tag': 'DT', 'end': 236, 'string': 'the', 'stem': 'the', 'start': 233, 'score': 0.0, 'type': 'null'}, {'pos_tag': 'NN', 'end': 244, 'string': 'priming', 'stem': 'prime', 'start': 237, 'score': 0.0, 'type': 'null'}, {'pos_tag': 'IN', 'end': 247, 'string': 'of', 'stem': 'of', 'start': 245, 'score': 0.0, 'type': 'null'}, {'pos_tag': 'JJ', 'end': 253, 'string': 'naive', 'stem': 'naiv', 'start': 248, 'score': 0.0, 'type': 'null'}, {'pos_tag': 'NN', 'end': 255, 'string': 'T', 'stem': 'T', 'start': 254, 'score': 0.0, 'type': 'null'}, {'pos_tag': 'NNS', 'end': 261, 'string': 'cells', 'stem': 'cell', 'start': 256, 'score': 0.0, 'type': 'null'}, {'pos_tag': '.', 'end': 262, 'string': '.', 'stem': '.', 'start': 261, 'score': 0.0, 'type': 'null'}]        
        proteins = {'T1': ['T1', 'Protein', '0', '4', 'IL-4'],
                    'T2': ['T2', 'Protein', '14', '22', 'TGF-beta'],
                    'T3': ['T3', 'Protein', '49', '53', 'IL-4'],
                    'T4': ['T4', 'Protein', '174', '178', 'IL-4'],
                    'T5': ['T5', 'Protein', '198', '206', 'TGF-beta'],
                    'T6': ['T6', 'Protein', '220', '225', 'FOXP3'],
                    'T7': ['T7', 'Protein', '269', '272', 'CD4'],
                    'T8': ['T8', 'Protein', '273', '279', 'CD45RA'],
                    'T9': ['T9', 'Protein', '326', '329', 'CD3'],
                    'T10': ['T10', 'Protein', '330', '334', 'CD28'],
                    'T11': ['T11', 'Protein', '354', '362', 'TGF-beta'],
                    'T12': ['T12', 'Protein', '370', '374', 'IL-4'],
                    'T13': ['T13', 'Protein', '400', '404', 'IL-4'],
                    'T14': ['T14', 'Protein', '431', '439', 'TGF-beta'],
                    'T15': ['T15', 'Protein', '462', '467', 'FOXP3']}
        
        triggers = {'T60': ['T60', 'Negative_regulation', '190', '197', 'inhibit'],
                    'T61': ['T61', 'Positive_regulation', '207', '216', 'induction'],
                    'T62': ['T62', 'Negative_regulation', '417', '426', 'repressed'],
                    'T63': ['T63', 'Positive_regulation', '449', '458', 'induction'],
                    'T64': ['T64', 'Gene_expression', '468', '478', 'expression'],
                    'T65': ['T65', 'Negative_regulation', '565', '572', 'induced'],
                    'T66': ['T66', 'Negative_regulation', '585', '592', 'absence'],
                    'T67': ['T67', 'Positive_regulation', '696', '702', 'induce'],
                    'T68': ['T68', 'Gene_expression', '709', '719', 'expression']}
        
        print "Test 1\n==============================================================="
        S = self.TC.analyze(sen, proteins, triggers)        
        S.test()
        print "\n\n"
        
    def test2(self):
        
        sen = [{'pos_tag': 'NN', 'end': 574, 'string': 'XXXXXXXXXXX', 'stem': 'XXXXXXXXXXX', 'start': 563, 'score': 0.0, 'type': 'null'}, {'pos_tag': ',', 'end': 575, 'string': ',', 'stem': ',', 'start': 574, 'score': 0.0, 'type': 'null'}, {'pos_tag': 'RB', 'end': 586, 'string': 'originally', 'stem': 'origin', 'start': 576, 'score': 0.0, 'type': 'null'}, {'pos_tag': 'VBN', 'end': 597, 'string': 'identified', 'stem': 'identifi', 'start': 587, 'score': 0.0, 'type': 'null'}, {'pos_tag': 'CC', 'end': 601, 'string': 'and', 'stem': 'and', 'start': 598, 'score': 0.0, 'type': 'null'}, {'pos_tag': 'VBN', 'end': 610, 'string': 'purified', 'stem': 'purifi', 'start': 602, 'score': 0.0, 'type': 'null'}, {'pos_tag': 'IN', 'end': 618, 'string': 'through', 'stem': 'through', 'start': 611, 'score': 0.0, 'type': 'null'}, {'pos_tag': 'PRP$', 'end': 622, 'string': 'its', 'stem': 'it', 'start': 619, 'score': 0.0, 'type': 'null'}, {'pos_tag': 'VBG', 'end': 630, 'string': 'binding', 'stem': 'bind', 'start': 623, 'score': 0.0, 'type': 'null'}, {'pos_tag': 'NNS', 'end': 636, 'string': 'sites', 'stem': 'site', 'start': 631, 'score': 0.0, 'type': 'null'}, {'pos_tag': 'IN', 'end': 639, 'string': 'on', 'stem': 'on', 'start': 637, 'score': 0.0, 'type': 'null'}, {'pos_tag': 'DT', 'end': 643, 'string': 'the', 'stem': 'the', 'start': 640, 'score': 0.0, 'type': 'null'}, {'pos_tag': 'NN', 'end': 649, 'string': 'HIV-1', 'stem': 'HIV-1', 'start': 644, 'score': 0.0, 'type': 'null'}, {'pos_tag': 'NN', 'end': 658, 'string': 'promoter', 'stem': 'promot', 'start': 650, 'score': 0.0, 'type': 'null'}, {'pos_tag': ',', 'end': 659, 'string': ',', 'stem': ',', 'start': 658, 'score': 0.0, 'type': 'null'}, {'pos_tag': 'VBD', 'end': 663, 'string': 'was', 'stem': 'wa', 'start': 660, 'score': 0.0, 'type': 'null'}, {'pos_tag': 'VBN', 'end': 669, 'string': 'found', 'stem': 'found', 'start': 664, 'score': 0.0, 'type': 'null'}, {'pos_tag': 'TO', 'end': 672, 'string': 'to', 'stem': 'to', 'start': 670, 'score': 0.0, 'type': 'null'}, {'pos_tag': 'VB', 'end': 677, 'string': 'bind', 'stem': 'bind', 'start': 673, 'score': 0.0, 'type': 'null'}, {'pos_tag': 'TO', 'end': 680, 'string': 'to', 'stem': 'to', 'start': 678, 'score': 0.0, 'type': 'null'}, {'pos_tag': 'DT', 'end': 684, 'string': 'the', 'stem': 'the', 'start': 681, 'score': 0.0, 'type': 'null'}, {'pos_tag': 'NN', 'end': 694, 'string': 'XXXXXXXXX', 'stem': 'XXXXXXXXX', 'start': 685, 'score': 0.0, 'type': 'null'}, {'pos_tag': 'NN', 'end': 703, 'string': 'enhancer', 'stem': 'enhanc', 'start': 695, 'score': 0.0, 'type': 'null'}, {'pos_tag': 'CC', 'end': 707, 'string': 'and', 'stem': 'and', 'start': 704, 'score': 0.0, 'type': 'null'}, {'pos_tag': 'TO', 'end': 710, 'string': 'to', 'stem': 'to', 'start': 708, 'score': 0.0, 'type': 'null'}, {'pos_tag': 'NNS', 'end': 720, 'string': 'promoters', 'stem': 'promot', 'start': 711, 'score': 0.0, 'type': 'null'}, {'pos_tag': 'IN', 'end': 724, 'string': 'for', 'stem': 'for', 'start': 721, 'score': 0.0, 'type': 'null'}, {'pos_tag': 'JJ', 'end': 732, 'string': 'several', 'stem': 'sever', 'start': 725, 'score': 0.0, 'type': 'null'}, {'pos_tag': 'NNS', 'end': 738, 'string': 'genes', 'stem': 'gene', 'start': 733, 'score': 0.0, 'type': 'null'}, {'pos_tag': 'VBN', 'end': 748, 'string': 'expressed', 'stem': 'express', 'start': 739, 'score': 0.0, 'type': 'null'}, {'pos_tag': 'IN', 'end': 751, 'string': 'at', 'stem': 'at', 'start': 749, 'score': 0.0, 'type': 'null'}, {'pos_tag': 'RB', 'end': 765, 'string': 'significantly', 'stem': 'significantli', 'start': 752, 'score': 0.0, 'type': 'null'}, {'pos_tag': 'JJR', 'end': 773, 'string': 'earlier', 'stem': 'earlier', 'start': 766, 'score': 0.0, 'type': 'null'}, {'pos_tag': 'NNS', 'end': 780, 'string': 'stages', 'stem': 'stage', 'start': 774, 'score': 0.0, 'type': 'null'}, {'pos_tag': 'IN', 'end': 783, 'string': 'of', 'stem': 'of', 'start': 781, 'score': 0.0, 'type': 'null'}, {'pos_tag': 'NN', 'end': 790, 'string': 'T-cell', 'stem': 'T-cell', 'start': 784, 'score': 0.0, 'type': 'null'}, {'pos_tag': 'NN', 'end': 802, 'string': 'development', 'stem': 'develop', 'start': 791, 'score': 0.0, 'type': 'null'}, {'pos_tag': 'IN', 'end': 807, 'string': 'than', 'stem': 'than', 'start': 803, 'score': 0.0, 'type': 'null'}, {'pos_tag': 'DT', 'end': 811, 'string': 'the', 'stem': 'the', 'start': 808, 'score': 0.0, 'type': 'null'}, {'pos_tag': 'NN', 'end': 821, 'string': 'XXXXXXXXX', 'stem': 'XXXXXXXXX', 'start': 812, 'score': 0.0, 'type': 'null'}, {'pos_tag': 'NN', 'end': 826, 'string': 'gene', 'stem': 'gene', 'start': 822, 'score': 0.0, 'type': 'null'}, {'pos_tag': '-LRB-', 'end': 828, 'string': '(', 'stem': '(', 'start': 827, 'score': 0.0, 'type': 'null'}, {'pos_tag': 'FW', 'end': 832, 'string': 'e.g.', 'stem': 'e.g.', 'start': 828, 'score': 0.0, 'type': 'null'}, {'pos_tag': ',', 'end': 833, 'string': ',', 'stem': ',', 'start': 832, 'score': 0.0, 'type': 'null'}, {'pos_tag': 'NN', 'end': 840, 'string': 'XXXXXX', 'stem': 'XXXXXX', 'start': 834, 'score': 0.0, 'type': 'null'}, {'pos_tag': 'CC', 'end': 844, 'string': 'and', 'stem': 'and', 'start': 841, 'score': 0.0, 'type': 'null'}, {'pos_tag': 'NN', 'end': 854, 'string': 'XXXXXXXXX', 'stem': 'XXXXXXXXX', 'start': 845, 'score': 0.0, 'type': 'null'}, {'pos_tag': '-RRB-', 'end': 855, 'string': ')', 'stem': ')', 'start': 854, 'score': 0.0, 'type': 'null'}, {'pos_tag': '.', 'end': 856, 'string': '.', 'stem': '.', 'start': 855, 'score': 0.0, 'type': 'null'}]
        
        protein = {
                    'T10': ['T10', 'Protein', '957', '966', 'TCR delta'],
                    'T8': ['T8', 'Protein', '845', '854', 'CD3 delta'],
                    'T9': ['T9', 'Protein', '882', '893', 'TCF-1 alpha'],
                    'T6': ['T6', 'Protein', '812', '821', 'TCR alpha'],
                    'T7': ['T7', 'Protein', '834', '840', 'p56lck'],
                    'T4': ['T4', 'Protein', '563', '574', 'TCF-1 alpha'],
                    'T5': ['T5', 'Protein', '685', '694', 'TCR alpha'],
                    'T2': ['T2', 'Protein', '87', '110', 'T-cell receptor C alpha'],
                    'T3': ['T3', 'Protein', '441', '452', 'TCF-1 alpha'],
                    'T1': ['T1', 'Protein', '16', '27', 'TCF-1 alpha']
                  }
        
        trigger = { 'T29':['T29', 'Binding', '673', '677', 'bind'],
                    'T28':['T28', 'Entity', '116', '124', 'enhancer'],
                    'T27':['T27', 'Positive_regulation', '73', '82', 'activates'],
                    'T38':['T38', 'Positive_regulation', '2427', '2433', 'depend'],
                    'T39':['T39', 'Entity', '2553', '2561', 'enhancer'],
                    'T36':['T36', 'Entity', '2001', '2009', 'enhancer'],
                    'T37':['T37', 'Transcription', '2376', '2400', 'transcriptional activity'],
                    'T34':['T34', 'Positive_regulation', '1129', '1136', 'derived'],
                    'T35':['T35', 'Positive_regulation', '1978', '1986', 'required'],
                    'T32':['T32', 'Positive_regulation', '711', '720', 'promoters'],
                    'T33':['T33', 'Gene_expression', '739', '748', 'expressed'],
                    'T30':['T30', 'Entity', '695', '703', 'enhancer'],
                    'T31':['T31', 'Entity', '711', '720', 'promoters']
                   }
        
        print "Test 2\n==============================================================="
        S = self.TC.analyze(sen, protein, trigger)        
        S.test()
        print "\n\n"
        
if __name__ == "__main__":
    
    
    test = SentenceAnalyzerTest()
    test.run()
    
    