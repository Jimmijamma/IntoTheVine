'''
Created on 23 giu 2018

@author: jimmijamma
'''
from MQTT_classes import Subscriber
import requests
import json
import time
import urllib

class ITV_ThingspeakAdaptor(Subscriber):
    '''
    classdocs
    '''

    def __init__(self):
        '''
        Constructor
        '''
        # MQTT class override
        clientID='ITV_ThingspeakAdaptor'
        sub_topic='alert/station'
        super(ITV_ThingspeakAdaptor,self).__init__(clientID=clientID,sub_topic=sub_topic)
        
        fp=open('ITV_ThingspeakAdaptor_config.JSON','r')
        self.conf=json.load(fp)
        fp.close()
        # loading the address of the Catalog
        catalog_ip=self.conf['catalog']['ip']
        catalog_port=self.conf['catalog']['port']
        self.catalog_url='http://'+str(catalog_ip)+':'+str(catalog_port)
        self.loadSettings_catalog()
        
    def loadSettings_catalog(self):
        res = urllib.urlopen(self.catalog_url+'/system_conf/thingspeak')
        res_obj=json.load(res)
        self.api_url=res_obj['url']
        
    def writeMeasurements(self,payload):
        
        dict_s = payload
        senML=json.loads(dict_s)
        clientID=senML['bn'].split('/')
        chat_id=clientID[1]
        station=clientID[2]
        
        res = urllib.urlopen(self.catalog_url+'/getUserInfo/'+str(chat_id))
        res_obj=json.load(res)
        l=res_obj['stations']
        for s in l:
            if s['station_id']==station:
                ts_key=s['thingspeak_key']
        
        for e in senML['e']:
            if e['n']=='temperature':
                temp=e['v']
            elif e['n']=='humidity':
                hum=e['v']
            elif e['n']=='rain':
                rain=e['v']
            elif e['n']=='leaf_wetness':
                lw=e['v']
            elif e['n']=='risk':
                risk=e['v']
            
        field1=str(temp)
        field2=str(hum)
        field3=str(rain)
        field4=str(lw)
        field5=str(risk)
        
        request_url=self.api_url.replace('<api_key>',ts_key).replace('<field1>',field1).replace('<field2>',field2).replace('<field3>',field3).replace('<field4>',field4).replace('<field5>',field5)
        requests.get(request_url)
        
    def mqtt_onMessageReceived(self, paho_mqtt, userdata, msg):
        Subscriber.mqtt_onMessageReceived(self, paho_mqtt, userdata, msg)
        self.writeMeasurements(msg.payload)
        
if __name__ == '__main__':
    
    ta=ITV_ThingspeakAdaptor()
    ta.mqtt_start()
    time.sleep(120)
    ta.mqtt_stop()


        
        