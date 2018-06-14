'''
Created on 13 giu 2018

@author: jimmijamma
'''
import json
import urllib
import paho.mqtt.client as PahoMQTT

class ITVStation(object):
    '''
    classdocs
    '''
    def __init__(self, system,id):
        '''
        Constructor
        '''
        self.id=str(id)
        self.system=system
        self.sensors_list=[]
        
        self.clientID = 'ITVStation'+'-'+self.system.user.id+'-'+self.system.id+'-'+self.id
        self._paho_mqtt = PahoMQTT.Client(self.clientID, False) 
        self._paho_mqtt.on_connect = self.myOnConnect
        self.topic='user/'+self.system.user.id+'/'+self.system.id+'/'+self.id+'/weather'
        
    def mqtt_start (self):
        #manage connection to broker
        self._paho_mqtt.connect('127.0.0.1', 1883)
        self._paho_mqtt.loop_start()

    def mqtt_stop (self):
        self._paho_mqtt.loop_stop()
        self._paho_mqtt.disconnect()
        
    def myPublish(self, topic, message):
        # publish a message with a certain topic
        self._paho_mqtt.publish(topic, message, 2)

    def myOnConnect (self, paho_mqtt, userdata, flags, rc):
        print "%s connected to MQTT broker with result code: %s"%(self.clientID,str(rc))
        
    def simulateSensors(self):
        temp,humidity,rain,snow,clouds=self.parseWeatherJSON()
        data={}
        data['user']=self.system.user.id
        data['system']=self.system.id
        data['station']=self.id
        data['temp']=temp
        data['humidity']=humidity
        data['rain']=rain
        data['snow']=snow
        data['clouds']=clouds
        message=json.dumps(data)
        self.myPublish(self.topic, message)
        
    def parseWeatherJSON(self):
        APPID='f8ac28f78069a7e511c00759939f94b4'
        full_api_url='http://api.openweathermap.org/data/2.5/weather?lat='+self.system.loc_lat+'&lon='+self.system.loc_long+'&APPID='+APPID
        url = urllib.urlopen(full_api_url)
        output = url.read().decode('utf-8')
        raw_dict= json.loads(output)
        url.close()
        temp=round(raw_dict['main']['temp']-273.15,2)
        humidity=raw_dict['main']['humidity']
        if 'rain' in raw_dict:
            rain=raw_dict['rain']['3h']
        else:
            rain=0
        if 'snow' in raw_dict:
            snow=raw_dict['snow']['3h']
        else:
            snow=0
        if 'clouds' in raw_dict:
            clouds=raw_dict['clouds']['all']
        return temp,humidity,rain,snow,clouds
        