'''
Created on 15 giu 2018

@author: jimmijamma
'''
from sklearn.externals import joblib
import paho.mqtt.client as PahoMQTT
import json
from MQTT_classes import PublisherSubscriber

class ITV_RiskScale(PublisherSubscriber):
    '''
    classdocs
    '''
    def __init__(self):
        '''
        Constructor
        '''
        # class attributes
        self.pkl_model='LMmodel.pkl'
        self.max_risk=1
        
        # MQTT class override
        clientID='ITV_RiskScale'
        sub_topic='measurement/#'
        super(ITV_RiskScale,self).__init__(clientID=clientID,sub_topic=sub_topic)
        
    
        
    def myOnMessageReceived (self, paho_mqtt , userdata, msg):
        # A new message is received
        if msg.topic=='station':
            self.parseWeather(msg.payload)
        
        elif msg.topic=='forecast':
            self.parseForecast(msg.payload)
            
        print "received %s message" %msg.topic

        
    def parseWeather(self, payload):
        dict_s = payload
        data=json.loads(dict_s)
        chat_id=data['user']
        system=data['system']
        station=data['station']
        temp=data['temp']
        humidity=data['humidity']
        rain=data['rain']
        snow=data['snow']
        if temp<10:
            risk=0
        else:
            tuple=[[temp,humidity,rain+snow]]
            lw=self.computeLeafWetness(tuple)
            lw=lw[0]
            if lw>3:
                if lw<6:
                    risk=1
                else:
                    risk=2
                data2={}
                data2['user']=chat_id
                data2['system']=system
                data2['station']=station
                data2['risk']=risk
                message=json.dumps(data2)
                self.myPublish(topic='alert/weather', message=message)
                
    def parseForecast(self,payload):
        dict_s = payload
        data=json.loads(dict_s)
        chat_id=data['user']
        system=data['system']
        for el in data['measurement_list']:
            tuple=[[el['temp'],el['humidity'],el['rain']]]
            lw=self.computeLeafWetness(tuple)
            lw=lw[0]
            if lw>3:
                    if lw<6:
                        risk=1
                    else:
                        risk=2
                    data2={}
                    data2['user']=chat_id
                    data2['system']=system
                    data2['risk']=risk
                    message=json.dumps(data2)
                    self.myPublish(topic='alert/forecast', message=message)
        
        
    def computeLeafWetness(self, tuple):
        clf = joblib.load(self.pkl_model)
        lw=clf.predict(tuple)
        return lw