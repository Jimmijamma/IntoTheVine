'''
Created on 14 giu 2018

@author: jimmijamma
'''

import pandas as pd
import numpy as np
from sklearn import datasets, linear_model, neural_network, cluster,svm,gaussian_process
from sklearn.metrics import mean_squared_error, r2_score
from sympy.polys.numberfields import IntervalPrinter
import random
from sklearn.externals import joblib
import sklearn

class ITV_ML_Trainer(object):
    '''
    classdocs
    '''

    def __init__(self, dataset):
        '''
        Constructor
        '''
        self.dataset=dataset
        self.X=None
        self.Y=None
        self.X_train=None
        self.X_test=None
        self.Y_train=None
        self.Y_test=None
        self.pkl_model='MLmodel.pkl'
        
    def parseDataset(self):
        mat=pd.read_excel(self.dataset)
        mat.as_matrix()
        mat=np.array(mat[2:])
        #col0=mat[:,0].astype(str)
        for ii, el in enumerate(mat[:,0]):
            mat[:,0][ii]=el.month
        mat=mat.astype(float)
        
        self.X=mat[:,1:4] # Temperature,Humidity,Rain
        self.Y=np.array(mat[:,-1]/60000) # Leaf Wetness
        '''
        self.Y[self.Y<180]=0
        self.Y[self.Y<600]=1
        self.Y[self.Y>=600]=2
        '''
        #self.Y=np.array(pd.cut(self.Y,bins=[-np.inf,60,600,np.inf], labels=[0,1,2]))
        #self.Y=np.array(pd.cut(self.Y,bins=[-np.inf,3,6,9,12,15,18,21,24,np.inf], labels=[0,3,6,9,12,15,18,21,24]))
        
        
    def trainModel(self, thr=0.1):
        n_el=int(thr*len(self.X))
        smpl=random.sample(range(0,len(self.X)),n_el)
        n_smpl=[]
        for ii in range(0,len(self.X)):
            if ii not in smpl:
                n_smpl.append(ii)
        self.X_test=self.X[smpl,:]
        self.Y_test=self.Y[smpl]
        self.X_train=self.X[n_smpl,:]
        self.Y_train=self.Y[n_smpl]
        
        #clf = neural_network.MLPClassifier(hidden_layer_sizes=1000,max_iter=200000)
        clf = neural_network.MLPRegressor(hidden_layer_sizes=1000,max_iter=200000)
        clf.fit(self.X_train, self.Y_train)
        joblib.dump(clf, self.pkl_model) 
        
    def testModel(self):
        clf = joblib.load(self.pkl_model)
        Y_pred=clf.predict(self.X_test)
        err=Y_pred-self.Y_test
        n_good=len(err[err==0])
        print np.mean(abs(err))
        print n_good*100.0/len(Y_pred)
        #print Y_pred,self.Y_test
        print err
        print zip(Y_pred,self.Y_test)
        #for el in list(set(Y_pred)):
            #print "%d: %d vs %d"%(el,len(Y_pred[Y_pred==el]),len(self.Y_test[self.Y_test==el]))
            #pass