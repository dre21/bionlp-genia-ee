'''
Created on Oct 2, 2013

@author: Andresta
'''

class TemplatePattern(object):
    '''
    classdocs
    '''


    def __init__(self):
        '''
        Constructor
        '''        
        # preposition
        self.prep1 = []
        self.prep2 = []
        
        # distance
        self.dist1 = []
        self.dist2 = []
        
        self.pro1_count = 0
        self.evt1_count = 0
        
        self.pro2_count = 0
        self.evt2_count = 0
        
        self.freq = 0
        
    def set(self, dist1, arg1_type, prep1='', dist2=-1, arg2_type='', prep2=''):
        
        """ set argument 1 """
        if dist1 not in self.dist1:
            self.dist1.append(dist1)
            
        if arg1_type == 'P':
            self.pro1_count+=1
        elif arg1_type == 'E':
            self.evt1_count+=1
        
        if prep1 != '' and prep1 not in self.prep1:
            self.prep1.append(prep1)
        
        """ optionally, set argument 2 """
        if dist2 != -1 and dist2 not in self.dist2:
            self.dist2.append(dist2)
            
        if arg2_type == 'P':
            self.pro2_count+=1
        elif arg2_type == 'E':
            self.evt2_count+=1
            
        if prep2 != '' and  prep2 not in self.prep2:
            self.prep2.append(prep2)
            
        # increase frequenct
        self.freq += 1

    def prints(self):
        print 'frequency:', self.freq
        print 'argument 1'
        print 'prep1:', self.prep1
        print 'dist1:', sorted(self.dist1)
        print '# arg1 pro:', self.pro1_count
        print '# arg1 evt:', self.evt1_count
        print 'argument 2'
        print 'prep2:', self.prep2
        print 'dist2:', sorted(self.dist2)
        print '# arg2 pro:', self.pro2_count
        print '# arg2 evt:', self.evt2_count
        


class ExtractionPattern(object):
    
    def __init__(self, tc, t_string, pos_tag, arg1, arg2 = -1):
        
        self.tc = tc
        self.arg1 = arg1
        self.arg2 = arg2
        
        self.t_string = t_string.lower()
        self.pos = pos_tag
        
        self.container = ''
        self.pattern_type = ''
        
        self.freq = 0
        
        # preposition
        self.prep1 = ''
        self.prep2 = ''
        
        # distance
        self.dist1 = -1
        self.dist2 = -1
        
        # argument type
        self.arg1_type = 'null'
        self.arg2_type = 'null'
        
    def has_arg2(self):
        return self.dist2 != -1
    
    def get_key(self):
        return ':'.join([self.t_string,self.pos, self.pattern_type, self.container])
    
    def prints(self):
        print '================================================'
        print 'key:', self.get_key()
        print self.container, '=>', self.pattern_type     
        print 'freq:', self.freq   
        print 'trigger:', self.tc, self.t_string, self.pos
        print '-------'
        print self.arg1 ,'-', self.arg1_type
        print 'dist1:', self.dist1
        print 'prep1:',self.prep1
        if self.arg2!= -1:
            print '-------'
            print self.arg2 ,'-', self.arg2_type
            print 'dist2:', self.dist2
            print 'prep2:',self.prep2
        
    