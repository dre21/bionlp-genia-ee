'''
Created on Sep 20, 2013

@author: Andresta
'''


from Prediction import Prediction

source = "E:/corpus/bionlp2011/project_data"
dict_type = "train"
dir_name = "test-model-008c"    
prediction = Prediction(source, dir_name, dict_type)

event_label = {"None":0,
               "Gene_expression":1,
               "Transcription":2,
               "Protein_catabolism":3,
               "Phosphorylation":4,
               "Localization":5,
               "Binding":6,
               "Regulation":7,
               "Positive_regulation":8,
               "Negative_regulation":9}

def predict_tp():
    doc_ids = 'dev'
    prediction.set_prediction_docs(doc_ids, is_test = False)
    return prediction.predict_tp(grid_search = True)
        
def analyze(event_name, Ypred, Ytest, Xinfo):       
    
    n_tp = 0
    n_fn = 0
    n_fp = 0
    n_mc = 0
    
    event_id = event_label[event_name]
    print "Analyze", event_name, "event on dev corpus"
    for i in range(0,len(Xinfo)):
        
        test = Ytest[i]
        pred = Ypred[i]
                
        if test != event_id and pred != event_id: continue
        
        info = Xinfo[i]
        
        o_doc = prediction.docs[info['doc']]
        o_sen = o_doc.sen[info['sen']]
        word = o_sen.words[info['t']]
        
        result = '-'
        if test == pred:
            result = 'TP'
            n_tp += 1
        elif test == 0:
            result = 'FP'
            n_fp += 1
        elif pred == 0:
            result = 'FN'
            n_fn += 1
        elif pred != test:
            result = 'MC'
            n_mc += 1 
        
        print info, word['string'], word['stem'], word['pos_tag'], test, pred, result
    
    print '-----------------------------------'
    print 'statisctic for', event_name
    print 'True positive:', n_tp
    print 'False positive:', n_fp
    print 'False negative:', n_fn
    print 'Miss classified:', n_mc
    print '\n\n\n'
        


if __name__ == '__main__':
    
    Ypred, Ytest, Xinfo = predict_tp()
    #analyze('Gene_expression', Ypred, Ytest, Xinfo)
    #analyze('Transcription', Ypred, Ytest, Xinfo)
    #analyze('Protein_catabolism', Ypred, Ytest, Xinfo)
    #analyze('Phosphorylation', Ypred, Ytest, Xinfo)
    #analyze('Localization', Ypred, Ytest, Xinfo)
    
    analyze('Regulation', Ypred, Ytest, Xinfo)
    analyze('Positive_regulation', Ypred, Ytest, Xinfo)
    analyze('Negative_regulation', Ypred, Ytest, Xinfo)
    