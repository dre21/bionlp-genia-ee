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
        self._chunk_map = {}
                
        # list of chunck type
        self.chunk_type = []
        
        self._process_chunk_data(chunk_data['data'])
        
    def _process_chunk_data(self, chunks):
        word_num = 0
        chunk_num = 0
        for c in chunks:
            # append chunk type
            self.chunk_type.append(c['type'])
            
            for _ in c['txt'].split(' '):
                self._chunk_map[word_num] = chunk_num
                word_num+=1
            chunk_num+=1
            
        # checking
        if len(self._chunk_map) != self.n_word:
            raise ValueError("Number of word are not the same!")
                
                
            