'''
Created on 18 giu 2018

@author: jimmijamma
'''
from MQTT_classes import Publisher, Subscriber
import time
import ITV_MachineLearning.ITV_ML_Trainer
import urllib
import json

#from pymongo import MongoClient

class Bello(Publisher):
    
    def __init__(self,clientID):
        super(Bello,self).__init__(clientID)
        
    def lol(self):
        super(Bello,self).mqtt_start()
        
class Brutto(Subscriber):
    
    def __init__(self,clientID,sub_topic):
        super(Brutto,self).__init__(clientID,sub_topic)
        
    def mqtt_onMessageReceived(self, paho_mqtt, userdata, msg):
        Subscriber.mqtt_onMessageReceived(self, paho_mqtt, userdata, msg)
        
    
    
       
if __name__ == '__main__':
    res = urllib.urlopen('http://127.0.0.1:8080/system_conf/ITV_TelegramBot')
    res_obj=json.load(res)
    print res_obj['token']