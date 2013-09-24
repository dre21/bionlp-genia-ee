'''
Created on Sep 23, 2013

@author: Andresta
'''

class Chunk(object):
    '''
    classdocs
    '''


    def __init__(self, chunk_data):
        '''
        Constructor
        '''
        self.n_chunk = chunk_data['nchunk']
        self.n_word = chunk_data['nword']
        
        
        # word number - chunk number mapping
        self.chunk_map = {}
                
        # list of chunck type
        self.chunk_type = []
        
        # dict of word number that belongs to prep chunk
        self.prep_chunk = {}
        
        self._process_chunk_data(chunk_data['data'])
        
    def _process_chunk_data(self, chunks):
        word_num = 0
        chunk_num = 0
        for c in chunks:
            # append chunk type
            self.chunk_type.append(c['type'])
            
            word_list = c['txt'].split(' ')
            
            if c['type'] == 'PP':                
                self.prep_chunk[chunk_num] = word_num                
            
            for _ in word_list:
                self.chunk_map[word_num] = chunk_num
                word_num+=1
            chunk_num+=1
            
        # checking
        if len(self.chunk_map) != self.n_word:
            raise ValueError("Number of word are not the same!")
                
    def same_chunk(self, wn1, wn2):
        """
        check whether both word number are in the same chunk
        """
        if self.chunk_map[wn1] == self.chunk_map[wn2]:
            return True
        else:
            return False   
        
    def distance(self, wn1, wn2):    
        """
        return distance in number of chunk between word number 1 and 2
        """
        return abs(self.chunk_map[wn1] - self.chunk_map[wn2])
    
    def get_type(self, wn):
        """
        return chunk type of given word number
        """
        return self.chunk_type[self.chunk_map[wn]]
    
    def get_word_number(self, chunk_number):
        word_num = []
        for wrd, chk in self.chunk_map.iteritems():
            if chunk_number == chk:
                word_num.append(wrd)
        return word_num
    