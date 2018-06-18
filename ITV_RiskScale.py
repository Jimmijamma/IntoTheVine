'''
Created on 15 giu 2018

@author: jimmijamma
'''
from sklearn.externals import joblib
import paho.mqtt.client as PahoMQTT
import json

class ITV_RiskScale(object):
    '''
    classdocs
    '''


    def __init__(self):
        '''
        Constructor
        '''
        self.pkl_model='LMmodel.pkl'
        self.max_risk=1
        
        # MQTT attributes
        self.clientID = 'ITV_RiskScale'
        self._paho_mqtt = PahoMQTT.Client(self.clientID, False)
        # register the callback
        self._paho_mqtt.on_connect = self.myOnConnect
        self._paho_mqtt.on_message = self.myOnMessageReceived
        self.sub_topic = '#'
        
    def mqtt_start (self):
        #manage connection to broker
        self._paho_mqtt.connect('127.0.0.1', 1883)
        self._paho_mqtt.loop_start()
        # subscribe for a topic
        self._paho_mqtt.subscribe(self.sub_topic, 2)

    def mqtt_stop (self):
        self._paho_mqtt.unsubscribe(self.sub_topic)
        self._paho_mqtt.loop_stop()
        self._paho_mqtt.disconnect()
        
    def myOnConnect (self, paho_mqtt, userdata, flags, rc):
        print ("Connected to message broker with result code: "+str(rc))
        
    def myPublish(self, topic, message):
        # publish a message with a certain topic
        self._paho_mqtt.publish(topic, message, 2)
        
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