'''
Created on Aug 28, 2013

@author: Andresta
'''
import re

class PreprocessText(object):
    '''
    classdocs
    '''
    TXT_EXT = ".txt"
    PROTEIN_EXT = ".a1"
    TRIGGER_EXT = ".a2"

    def __init__(self, input_dir, output_dir):
        '''
        Constructor
        '''
        self.input_dir = input_dir
        self.output_dir = output_dir
                
    
    '''
    return text from txt file of given fpath
    '''
    def get_text(self, fpath):
        with open(fpath, 'r') as fin:
            txt = fin.read()
        return txt
        
    '''
    Update protein in text with placeholder and split it with adjacent word
    - placeholder will have the same length as protein
    - split if only protein is connected using '-' with adjacent word
        ex Id1-Id4 ==> XXX XXX
    '''
    def update_split_protein(self, fname, placeholder_char = "X"):           
        
        t_fpath = self.input_dir + '/' + fname + self.TXT_EXT
        p_fpath = self.input_dir + '/' + fname + self.PROTEIN_EXT
        
        # proteins is triplet of (start pos, end pos, protein text)
        proteins = self.get_protein_position(p_fpath)
        txt = self.get_text(t_fpath)
        old_len = len(txt)
        
        # update protein with placeholder
        for prot in proteins:                                   
            start = int(prot[0]) - 2
            if start < 0: start = 0
            end = int(prot[1]) + 2
            if end > old_len: end = old_len
            
            new_string = self.update_string(txt[start:end],prot[2],placeholder_char)                         
            txt = txt[:start] + new_string + txt[end:]
           
        if (old_len != len(txt)):
            raise ValueError("length after modification is changed")
        return txt
    
    
    '''
    update string with placeholder and remove '-' adjacent char
    '''
    def update_string(self, string, substring = "", placeholder_char = ""):
        new_string = string
        
        # update string with placeholder
        if not (placeholder_char == "" or substring == ""):
            new_string = string.replace(substring, placeholder_char * len(substring))
        
        
        # check char before
        result = re.match("[A-Z0-9]\-", string[:2], flags=re.IGNORECASE)
        if result:
            new_string = new_string[0:1] + " " + new_string[2:]
        
        # check char after 
        result = re.match("\-[A-Z0-9]", string[-2:], flags=re.IGNORECASE)
        if result:
            new_string = new_string[:-2] + " " + new_string[-1:]
        
        return new_string
        
    '''
    return list of triplet (start pos, end pos, protein text) from protein a1 file
    '''
    def get_protein_position(self, in_fpath):
        positions = []
        with open(in_fpath, 'r') as f:
            for line in f:
                ps = re.split("\\t|\\s+",line,5)
                positions.append((ps[2],ps[3],ps[4]))
        return positions
        
    
    def test(self):
        
        ''' test for update_string '''
        print "test for update_string"
        
        texts = {"1-Id4, " : "Id4",  
                 ", BMP-2, " : "BMP-2",
                 ", -4, " : "-4"}
        
        for txt, prot in texts.iteritems():
            print txt, prot, " ==> ", self.update_string(txt, prot, "X")
            
        
        ''' update_split_protein '''
        print "\n\n\nTesting for update_split_protein"
        fname = "PMC-1134658-01-Background"
        out = self.update_split_protein(fname)       
        print out
        
        
if __name__ == '__main__':
    
    in_dir = "E:/bionlp2011/dataset/BioNLP-ST_2011_genia_devel_data_rev1"
    fname = "PMC-1134658-01-Background"
    
    splitter = PreprocessText(in_dir,"")   
    splitter.test()
        
    
    
    
    