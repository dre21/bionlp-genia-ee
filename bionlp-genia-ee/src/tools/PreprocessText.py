'''
Created on Aug 28, 2013

@author: Andresta
'''
import re, os
import logging as log

class PreprocessText(object):
    '''
    classdocs
    '''
    TXT_EXT = ".txt"
    PROTEIN_EXT = ".a1"
    TRIGGER_EXT = ".a2"

    ''' 
    list of word that usually merge with other word using '-' char in genia corpus
    this word must be split the same way as protein
    example: DNA-binding activity ==> DNA binding activity
    '''
    SPLIT_WORD_LIST = ['binding','induced','dominant','associated', "non"]

    def __init__(self, input_dir, output_dir):
        '''
        Constructor
        '''
        
        if input_dir == "" or output_dir == "":
            raise ValueError("input dir and output dir cannot be blank")
        
        self.input_dir = input_dir
        self.output_dir = output_dir

    
    def run(self):
        
        ext = self.TXT_EXT
        count = 0
        log.info("Running PreprocessText ....") 
        
        for doc in [doc_name.rstrip(ext) for doc_name in os.listdir(self.input_dir) if doc_name.endswith(ext)]:
            log.debug(doc)
            
            txt = self.get_text(doc)
            
            # update and split protein
            new_txt = self.update_split_protein(txt, doc)
            
            # split word
            new_txt = self.split_word(new_txt, self.SPLIT_WORD_LIST)
            
            # write to external file
            if len(txt) == len(new_txt):
                self.write_text(new_txt, doc)
                count += 1
            else:
                raise ValueError("New text has different length")
        
        log.info("updating " + str(count) + " documents")
        
            
    
    '''
    return text from txt file of given fname
    '''
    def get_text(self, fname):        
        fpath = self.input_dir + '/' + fname + self.TXT_EXT
        with open(fpath, 'r') as fin:
            txt = fin.read()
        return txt
    
    '''
    write text to file
    '''
    def write_text(self, txt, fname):
        fpath = self.output_dir + '/' + fname + self.TXT_EXT
        with open(fpath, 'w') as f:
            f.write(txt)
    
    def split_word(self, txt, word_list):
        
        tlen = len(txt)
        new_txt = txt
        txt = txt.lower()
        for word in word_list:
            idx = txt.find(word, 0)
            while idx >= 0 :
                
                start = idx - 2
                if start < 0: start = 0
                end = idx + len(word) + 2
                if end > tlen: end = tlen
                
                # update string                               
                string = self.update_string(new_txt[start:end])                
                
                # update text
                new_txt = new_txt[:start] + string + new_txt[end:]
                
                # finde new word
                idx = txt.find(word, idx + len(word))
                
        
        return new_txt
    
    '''
    Update protein in text with placeholder and split it with adjacent word
    - placeholder will have the same length as protein
    - split if only protein is connected using '-' with adjacent word
        ex Id1-Id4 ==> XXX XXX
    '''
    def update_split_protein(self, txt, fname, placeholder_char = "X"):           
        
        #t_fpath = self.input_dir + '/' + fname + self.TXT_EXT
        p_fpath = self.input_dir + '/' + fname + self.PROTEIN_EXT
        
        # proteins is triplet of (start pos, end pos, protein text)
        proteins = self.get_protein_position(p_fpath)
        #txt = self.get_text(t_fpath)
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
            
        
        ''' testing update_split_protein '''
        print "\n\n\nTesting for update_split_protein"
        fname = "PMC-1134658-01-Background"
        txt = self.get_text(fname)
        out = self.update_split_protein(txt, fname)       
        print out
        
        ''' testing split word '''
        print "\n\nTesting split word"
        fname = "PMID-8098881"
        txt = self.get_text(fname)
        out = self.split_word(txt, self.SPLIT_WORD_LIST)
        print txt
        print "========================="
        print out
        
        
if __name__ == '__main__':
    
    log.basicConfig(level=log.DEBUG)
    
    in_dir = "E:/Project/bionlp-genia-ee/data/original/dev"
    out_dir = "E:/Project/bionlp-genia-ee/data/preprocess/dev"        
    
    splitter = PreprocessText(in_dir,out_dir)
    splitter.run()   
    #splitter.test()
        
    
    
    
    