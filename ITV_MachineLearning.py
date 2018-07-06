'''
Created on 14 giu 2018

@author: jimmijamma
'''

import pandas as pd
import numpy as np
from sklearn import neural_network
import random
from sklearn.externals import joblib
from MQTT_classes import PublisherSubscriber
import json

class ITV_MachineLearning(PublisherSubscriber):
    '''
    classdocs
    '''

    def __init__(self):
        '''
        Constructor
        '''
        self.dataset="/Users/jimmijamma/Desktop/Dataset.xlsx"
        self.X=None
        self.Y=None
        self.X_train=None
        self.X_test=None
        self.Y_train=None
        self.Y_test=None
        self.pkl_model='MLmodel.pkl'
        
        # MQTT class override
        clientID='ITV_MachineLearning'
        sub_topic='measurement/#'
        super(ITV_MachineLearning,self).__init__(clientID=clientID,sub_topic=sub_topic)
        
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
        n_good=len(err[err<1])
        print np.mean(abs(err))
        print n_good*100.0/len(Y_pred)
        print err
        print zip(Y_pred,self.Y_test)
        
            
    def mqtt_onMessageReceived(self, paho_mqtt, userdata, msg):
        PublisherSubscriber.mqtt_onMessageReceived(self, paho_mqtt, userdata, msg)
        # A new message is received
        self.completeMeasurement(msg.payload,msg.topic)
            
    def completeMeasurement(self, payload, topic):
        dict_s = payload
        senML=json.loads(dict_s)
        for e in senML['e']:
            if e['n']=='temperature':
                temp=e['v']
            elif e['n']=='humidity':
                humidity=e['v']
            elif e['n']=='rain':
                rain=e['v']
        tuple_=[[temp,humidity,rain]]
        lw=self.computeLeafWetness(tuple_)
        lw=lw[0]
        if lw<0:
            lw=0
        senML['e'].append({'n': 'leaf_wetness', 'u':'h/day', 't': None, "v":lw})
        message=json.dumps(senML)
        reply_topic='leaf_wetness/'+topic.split('/')[1]
        self.mqtt_publish(topic=reply_topic, message=message)
          
    def computeLeafWetness(self, tuple):
        clf = joblib.load(self.pkl_model)
        lw=clf.predict(tuple)
        return lw
    
if __name__ == '__main__':
    
    ml = ITV_MachineLearning()