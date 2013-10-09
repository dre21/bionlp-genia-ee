'''
Created on Sep 8, 2013

@author: Andresta
'''
import os, json

from datetime import datetime as dt
from model.Dictionary import WordDictionary, TriggerDictionary
from model.Document import DocumentBuilder
from features.FeatureExtraction import FeatureExtraction
from classifier.SVM import SVM

class Learning(object):
    '''
    Learning steps:
    1. define docs for learning
    2. extract features
    3. build input data for classifier
    4. build a model and save it
    '''

    # suffix and extension of id file
    DOCID_SUFFIX_EXT = "_doc_ids.json"
    
    # directory for saving svm model
    MODEL_DIR = "/model"
    
    def __init__(self, source, dir_name, dict_type):
        '''
        Constructor
        '''        
        self.src = source
        self.path = self.set_path(source, dir_name)
        
        self.dict_type = dict_type
        self.wdict = None
        self.tdict = None
        self.doc_builder = None
        self.extraction = None
                        
        self._set(dict_type)                                
    
    def set_path(self, source, dir_name):
        """
        check whether given dir_name is exist
        raise error if exist, otherwise create new one
        return full path of dir_name
        """
        path = source + self.MODEL_DIR + '/' + dir_name
        if os.path.exists(path):
            raise ValueError(path + "exist!!, chose anoher dir_name for learning")
        else:
            # create dir_name
            os.makedirs(path)
        return path
        
                
    def _set(self, dict_type):
        """
        initialize dictionary type to be used in learning process
        initialize document builder
        initialize feature extraction
        """       
        
        self.wdict = WordDictionary(self.src)    
        self.wdict.load(dict_type)
               
        self.tdict = TriggerDictionary(self.src)
        self.tdict.load(dict_type)
        
        self.doc_builder = DocumentBuilder(self.src, self.wdict, self.tdict)         
        self.extraction = FeatureExtraction(self.src, self.wdict, self.tdict)
        
    def get_docid_list(self, docid_list_fname):
        """
        return list of file
        """
        if not isinstance(docid_list_fname, list):
            # get list of doc ids from file
            path = self.src + '/' + docid_list_fname + self.DOCID_SUFFIX_EXT
            if not os.path.exists(path):
                raise ValueError(path + " is not exist")
            with open(path, 'r') as f: 
                doc_ids = json.loads(f.read())
        else:
            doc_ids = docid_list_fname
        
        return doc_ids
    
    def get_feature(self, doc_ids, step):
        """
        extract feature and return X, Y for a given step
        step are either one of these:
        'tp' => trigger-protein relation
        'tt' => trigger-trigger relation to predict regulation event with trigger argument  
        'tc' => trigger-theme-cause relation to predict regulation event with theme and cause (binary)
        't2' => trigger-theme1-theme2 relation to predict theme2 in binding (binary)
        """
        if step not in ['tt','tp','tc','t2','evt']:
            raise ValueError("only support step for tt, tp, tc, t2 and evt")
        
        X = []
        Y = []
        
        dt_start = dt.now()        
        
        # reset statistic of extraction
        self.extraction.reset_statistic()  
                      
        # init feature
        print "now extracting", len(doc_ids), "docs"
        for doc_id in doc_ids:             
            o_doc = self.doc_builder.build(doc_id)
            if step == 'tp':
                samples = self.extraction.extract_tp(o_doc)
            elif step == 'tt':
                samples = self.extraction.extract_tt(o_doc)
            elif step == 'tc':
                samples = self.extraction.extract_tc(o_doc)
            elif step == 't2':
                samples = self.extraction.extract_t2(o_doc)
            elif step == 'evt':
                samples =  self.extraction.extract_evt(o_doc)
            
            for sample in samples:
                X.append(sample[2])
                Y.append(sample[1])                   
        
        # print statistic
        pos = self.extraction.sample_pos
        neg = self.extraction.sample_neg
        stat = (pos, neg, pos + neg)
        print stat
        print "percentege of positif data:", pos * 100.0 / (pos + neg)        
        print "time to extract feature", dt.now() - dt_start
        
        return X,Y
    
    def learn_tp(self, docid_list_fname, grid_search):
        print 'learning trigger - protein relation'
        print '---------------------------------'
        # get list of file
        doc_ids = self.get_docid_list(docid_list_fname)
        
        # get features and target
        X, Y = self.get_feature(doc_ids, 'tp')
                        
        # init svm classifier
        svm = SVM(self.path, 'trig-prot','linear', grid_search = grid_search, class_weight = 'auto')        
        svm.create()
        
        # fit training data
        svm.learn(X, Y)        
        
    def learn_tt(self, docid_list_fname, grid_search):
        print 'learning trigger - trigger relation'
        print '----------------------------------'
        # get list of file
        doc_ids = self.get_docid_list(docid_list_fname)
        
        # get features and target
        X, Y = self.get_feature(doc_ids, 'tt')
                        
        # init svm classifier
        svm = SVM(self.path, 'trig-trig','linear', grid_search = grid_search, class_weight = 'auto')        
        svm.create()
        
        # fit training data
        svm.learn(X, Y)      
        
        
    def learn_tc(self, docid_list_fname, grid_search):
        print 'learning trigger - theme - cause relation'
        print '---------------------------------------'
        # get list of file
        doc_ids = self.get_docid_list(docid_list_fname)
        
        # get features and target
        X, Y = self.get_feature(doc_ids, 'tc')
        
        # init svm classifier
        svm = SVM(self.path, 'trig-theme-cause','linear', grid_search = grid_search, class_weight = 'auto')        
        svm.create()
        
        # fit training data
        svm.learn(X, Y) 
        
    def learn_t2(self, docid_list_fname, grid_search):
        print 'learning trigger - theme1 - theme2 relation'
        print '-----------------------------------------'
        # get list of file
        doc_ids = self.get_docid_list(docid_list_fname)
        
        # get features and target
        X, Y = self.get_feature(doc_ids, 't2')
        
        # init svm classifier
        svm = SVM(self.path, 'trig-theme1-2','linear', grid_search = grid_search, class_weight = 'auto')        
        svm.create()
        
        # fit training data
        svm.learn(X, Y) 
        
    def learn_evt(self, docid_list_fname):
        print 'learning trigger - protein simple relation'
        print '------------------------------------------'
        # get list of file
        doc_ids = self.get_docid_list(docid_list_fname)
        
        # get features and target
        X, Y = self.get_feature(doc_ids, 'evt')
                        
        # init svm classifier
        svm = SVM(self.path, 'evt','linear', grid_search = True, class_weight = 'auto')        
        svm.create()
        
        # fit training data
        svm.learn(X, Y)
        

if __name__ == "__main__":
                            
    source = "E:/corpus/bionlp2011/project_data"
    dict_type = "train"
    doc_ids = "train"
    learning = Learning(source, "test-model-00", dict_type)
    
    print "Learning Trigger-Protein \n ========================="
    learning.learn_tp(doc_ids, grid_search = True)
    
    print "Learning Trigger-Trigger \n ========================="
    learning.learn_tt(doc_ids, grid_search = True)
    #print learning.vec
    
        
        