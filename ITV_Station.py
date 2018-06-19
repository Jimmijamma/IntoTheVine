'''
Created on 13 giu 2018

@author: jimmijamma
'''
import json
import urllib
from MQTT_classes import Publisher

class ITV_Station(Publisher):
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
        
        id_string = 'ITV_Station'+'-'+self.system.user.id+'-'+self.system.id+'-'+self.id
        super(ITV_Station,self).__init__(clientID=id_string)
        
    def simulateSensors(self):
        temp,humidity,rain,snow,clouds=self.parseWeatherJSON()
        thingspeak_url='https://api.thingspeak.com/update?api_key=OMNCGQBADQGJYUOQ'
        thingspeak_url+='&field1='+str(temp)
        thingspeak_url+='&field2='+str(humidity)
        thingspeak_url+='&field3='+str(snow+rain)
        urllib.urlopen(thingspeak_url)
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
        self.mqtt_publish(topic='measurement/station/'+self.system.user.id+'/'+self.system.id+'/'+self.id, message=message)
        
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
        