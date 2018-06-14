'''
Created on 14 giu 2018

@author: jimmijamma
'''

import pandas as pd
import numpy as np
from sklearn import datasets, linear_model, neural_network, cluster,svm
from sklearn.metrics import mean_squared_error, r2_score
from sympy.polys.numberfields import IntervalPrinter

class ITV_LM_Trainer(object):
    '''
    classdocs
    '''

    def __init__(self, dataset):
        '''
        Constructor
        '''
        self.dataset=dataset
        
    def parseDataset(self):
        mat=pd.read_excel(self.dataset)
        mat.as_matrix()
        mat=np.array(mat[2:])
        #col0=mat[:,0].astype(str)
        for ii, el in enumerate(mat[:,0]):
            mat[:,0][ii]=el.month
        mat=mat.astype(float)
        
        X=mat[:,1:4] # Temperature,Humidity,Rain
        Y=mat[:,-1]*0.001 # Leaf Wetness
        print len(Y)
        return X,Y

        