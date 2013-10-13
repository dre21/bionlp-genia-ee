'''
Created on Sep 10, 2013

@author: Andresta
'''
import os, json

from datetime import datetime as dt
from model.Dictionary import WordDictionary, TriggerDictionary
from model.Document import DocumentBuilder
from features.FeatureExtraction import FeatureExtraction
from classifier.SVM import SVM
from corpus.GeniaA2Writer import GeniaA2Writer as A2Writter


class Prediction(object):
    '''
    classdocs
    '''
    
    # suffix and extension of id file
    DOCID_SUFFIX_EXT = "_doc_ids.json"
    
    # directory for saving svm model
    MODEL_DIR = "/model"
    
    # directory for saving output a2 file
    OUT_DIR = "/result"

    # list of event name
    EVENT_NAME = ["None",
                  "Gene_expression",
                  "Transcription",
                  "Protein_catabolism",
                  "Phosphorylation",
                  "Localization",
                  "Binding",
                  "Regulation",
                  "Positive_regulation",
                  "Negative_regulation"]
        

    def __init__(self, source, dir_name, dict_type):
        '''
        Constructor
        '''
        self.src = source
        self._model_path = '' 
        self._out_path = ''
        self.set_path(source, dir_name)
        
        self.dict_type = dict_type
        self.wdict = None
        self.tdict = None
        self.doc_builder = None
        self.extraction = None      
        
        self.docs = {}          
        
        self._set(dict_type)
    
    def _set(self, dict_type):
        """
        initialize dictionary type to be used in feature extraction process
        initialize document builder
        initialize feature extraction
        """       
        
        self.wdict = WordDictionary(self.src)    
        self.wdict.load(dict_type)
               
        self.tdict = TriggerDictionary(self.src)
        self.tdict.load(dict_type)
        
        self.doc_builder = DocumentBuilder(self.src, self.wdict, self.tdict)         
        self.extraction = FeatureExtraction(self.src, self.wdict, self.tdict)
        
        self.a2 = A2Writter(self._out_path)
        
    def set_path(self, source, dir_name):
        """
        check whether given dir_name is exist
        raise error if it does not exist
        return full _model_path of dir_name
        """
        # model path
        path = source + self.MODEL_DIR + '/' + dir_name
        if not os.path.exists(path):
            raise ValueError(path + "does not exist!!, chose another dir_name for prediction")        
        self._model_path = path
        
        # output path
        path = source + self.OUT_DIR + '/' + dir_name
        if not os.path.exists(path):
            os.makedirs(path)        
        self._out_path = path 
       
        
    def get_feature(self, step):
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
        info = []
        
        dt_start = dt.now()        
        
        # reset statistic of extraction
        self.extraction.reset_statistic()
                      
        # init feature
        print "now extracting", len(self.docs), "docs"
        for doc_id in self.docs.keys():             
            o_doc = self.docs[doc_id]
            if step == 'tp':
                samples = self.extraction.extract_tp(o_doc)
            elif step == 'tt':
                samples = self.extraction.extract_tt(o_doc)
            elif step == 'tc':
                samples = self.extraction.extract_tc(o_doc)
            elif step == 't2':
                samples = self.extraction.extract_t2(o_doc)
            elif step == 'evt':
                samples = self.extraction.extract_evt(o_doc)
            
            for sample in samples:
                X.append(sample[2])
                Y.append(sample[1])      
                info.append(sample[0])             
                
        print "time to extract feature", dt.now() - dt_start
        
        return X,Y, info
    
    def set_prediction_docs(self,docid_list_fname, is_test = True):
        """
        build a document to be predicted
        """
        dt_start = dt.now()      
        self.docs = {}
        # get list of file
        doc_ids = self.get_docid_list(docid_list_fname)
        
        print "now building", len(doc_ids), "docs"
        for doc_id in doc_ids:
            self.docs[doc_id] = self.doc_builder.build(doc_id, is_test)
            
        print "finish built docs in:", dt.now() - dt_start

    def update_doc(self, list_info, list_target, arg1_name, arg2_name = ''):
        """
        add relation and trigger in the document
        """
        for i in range(0,len(list_info)):
            target = list_target[i]
            if target < 1: continue
            info = list_info[i]
            doc_id = info["doc"]
            if info.get('a2',-1) < 0:
                # only argument 1
                self.docs[doc_id].add_relation(info['sen'], self.EVENT_NAME[target], info['t'], info['a'], arg1_name)
            else:
                self.docs[doc_id].add_relation(info['sen'], self.EVENT_NAME[target], info['t'], info['a'], arg1_name, info['a2'], arg2_name)

    def update_doc_info(self, list_info, list_target, arg_name, arg_type):
        """
        update trigger and relation of document
        """
        for i in range(0,len(list_info)):
            target = list_target[i]
            if target < 1: continue
            info = list_info[i]
            doc_id = info["doc"]
            self.docs[doc_id].update(info['sen'], info['t'], self.EVENT_NAME[target], info['a'], arg_name, arg_type)
            
    def update_doc_relation(self, rel_type, list_info, list_target):
        """
        update only relation of document
        """
        for i in range(0,len(list_info)):
            target = list_target[i]
            if target == 1:
                info = list_info[i]
                doc_id = info["doc"]
                
                if rel_type == 'cause':
                    arg = info['c']
                else:
                    arg = info['a2']
                self.docs[doc_id].update_relation(rel_type, info['sen'], info['t'], arg)

    
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
    
    def predict_tp(self, grid_search = True):
        """
        return prediction of given docid_list
        """
        if self.docs == {}:
            raise ValueError("docs have not been created. call set_prediction_docs first!")
        # get list of file
        #doc_ids = self.get_docid_list(docid_list_fname)
        
        # get features and target
        X, Y, info = self.get_feature('tp')
        
        # init svm classifier
        svm = SVM(self._model_path, "trig-prot", "linear", grid_search = grid_search, class_weight = 'auto')
        svm.load()
        
        return svm.predict(X), Y, info
        
    def predict_tt(self, grid_search = True):
        """
        return prediction of given docid_list
        """
        if self.docs == {}:
            raise ValueError("docs have not been created. call set_prediction_docs first!")
        # get list of file
        #doc_ids = self.get_docid_list(docid_list_fname)
        
        # get features and target
        X, Y, info = self.get_feature('tt')
        
        # init svm classifier
        svm = SVM(self._model_path, "trig-trig", "linear", grid_search = grid_search, class_weight = 'auto')
        svm.load()
        
        return svm.predict(X), Y, info
    
    def predict_tc(self, grid_search = True):
        if self.docs == {}:
            raise ValueError("docs have not been created. call set_prediction_docs first!")
        # get list of file
        #doc_ids = self.get_docid_list(docid_list_fname)
        
        # get features and target
        X, Y, info = self.get_feature('tc')
        
        # init svm classifier
        svm = SVM(self._model_path, "trig-theme-cause", "linear", grid_search = grid_search, class_weight = 'auto')
        svm.load()
        
        return svm.predict(X), Y, info
    
    def predict_t2(self, grid_search = True):
        if self.docs == {}:
            raise ValueError("docs have not been created. call set_prediction_docs first!")

        # get features and target
        X, Y, info = self.get_feature('t2')
        
        # init svm classifier
        svm = SVM(self._model_path, "trig-theme1-2", "linear", grid_search = grid_search, class_weight = 'auto')
        svm.load()
        
        return svm.predict(X), Y, info
    
    def predict_evt(self):
        """
        return simple event prediction of given docid_list
        """
        if self.docs == {}:
            raise ValueError("docs have not been created. call set_prediction_docs first!")
        # get list of file
        #doc_ids = self.get_docid_list(docid_list_fname)
        
        # get features and target
        X, Y, info = self.get_feature('evt')
        
        # init svm classifier
        svm = SVM(self._model_path, "evt", "linear", grid_search = True, class_weight = 'auto')
        svm.load()
        
        return svm.predict(X), Y, info
    
    def predict(self, docid_list_fname, write_result = True):
        
        # create document object for prediction
        print '\ncreate document object for prediction'
        print '-------------------------------------'
        self.set_prediction_docs(docid_list_fname)
        
        # predict trigger-protein relation
        print '\npredict trigger-protein relation'
        print '--------------------------------'
        Ypred, _, info = self.predict_tp(grid_search = True)
        # update document
        self.update_doc_info(info, Ypred, "Theme", "P")
        
        for i in range(0,2):
            # predict trigger-trigger relation
            print '\npredict trigger-trigger relation step',i
            print '------------------------------------------'
            Ypred, _, info = self.predict_tt(grid_search = True)
            self.update_doc_info(info, Ypred, "Theme", "E")
        
        # predict trigger-theme-cause relation
        print '\npredict trigger-theme-cause relation'
        print '-------------------------------------'
        Ypred, _, info = self.predict_tc(grid_search = True)
        self.update_doc_relation('cause', info, Ypred)
        
        # predict theme2 relation
        print '\npredict theme2 relation'
        print '-----------------------'
        Ypred, _, info = self.predict_t2(grid_search = True)
        self.update_doc_relation('theme2', info, Ypred)
        
        # write a2
        if write_result:
            self.write_result()
        
    def predict2(self, docid_list_fname, write_result = True):
        # create document object for prediction
        print '\ncreate document object for prediction'
        print '-------------------------------------'
        self.set_prediction_docs(docid_list_fname)
        
        # predict trigger-protein relation
        print '\npredict trigger-protein simple relation'
        print '---------------------------------------'
        Ypred, _, info = self.predict_evt()
        # update document
        self.update_doc(info, Ypred, "Theme", "P")
        
        # write a2
        if write_result:
            self.write_result()
        
    def write_result(self):
        print "now writing", len(self.docs), "docs result to", self._out_path
        for doc in self.docs.itervalues():
            self.a2.write(doc)
        
        