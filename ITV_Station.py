'''
Created on 13 giu 2018

@author: jimmijamma
'''
import json
import urllib
from MQTT_classes import Publisher
import time
import requests
import random
import numpy as np

class ITV_Station(Publisher):
    '''
    classdocs
    '''
    def __init__(self):
        '''
        Constructor
        '''
        fp=open('ITV_Station_conf.JSON','r')
        self.conf=json.load(fp)
        fp.close()
        
        self.catalog_ip=self.conf['catalog']['ip']
        self.catalog_port=self.conf['catalog']['port']
        
        self.user=self.conf['station']['user']
        self.lat=self.conf['station']['lat']
        self.lon=self.conf['station']['long']
        is_new=self.conf['station']['is_new']
        self.appid='f8ac28f78069a7e511c00759939f94b4'
        self.installStation(is_new)
            
        id_string = 'ITV_Station/'+str(self.user)+'/'+str(self.id)
        super(ITV_Station,self).__init__(clientID=id_string)
        
    def installStation(self, is_new):
        self.was_new=False
        if is_new==True:
            self.was_new=True
            id=''.join(random.choice('0123456789abcdefghijklmnopqrstuvwyxz') for i in range(5))
            self.id=id
            self.conf['station']['id']=self.id
            self.conf['station']['is_new']=False
            fp=open('ITV_Station_conf.JSON','w')
            json.dump(self.conf, fp)
            fp.close()
            payload=json.dumps(self.conf['station'])
            r=requests.put('http://'+self.catalog_ip+':'+self.catalog_port+'/add_station',data=payload)
            sc=r.status_code
            #print"New station created with id: %s, user: %s, system %s"%(self.id,self.user,self.system)
        else:
            self.id=self.conf['station']['id']
        
    def simulateSensors(self):
        temp,humidity,rain,snow,clouds=self.http_getWeather()
        timestamp=time.time()
        senML={}
        senML['bn']=self.clientID
        senML['e']=[]
        senML['e'].append({'n': 'temperature', 'u': "degC", 't': timestamp, "v":temp})
        senML['e'].append({'n': 'humidity', 'u': "%", 't': timestamp, "v":humidity})
        senML['e'].append({'n': 'rain', 'u': "mm/3h", 't': timestamp, "v":rain+snow})
        senML['e'].append({'n': 'cloudiness', 'u': "%", 't': timestamp, "v":clouds})
        message=json.dumps(senML)
        self.mqtt_publish(topic='measurement/station', message=message)
        
    def http_getWeather(self):
        full_api_url='http://api.openweathermap.org/data/2.5/weather?lat='+self.lat+'&lon='+self.lon+'&APPID='+self.appid
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
    
    def http_getForecast(self):
        full_api_url='http://api.openweathermap.org/data/2.5/forecast'+'?lat='+self.lat+'&lon='+self.lon+'&APPID='+self.appid
        url = urllib.urlopen(full_api_url)
        output = url.read().decode('utf-8')
        raw_api_dict = json.loads(output)
        url.close()
        
        timestamp=time.time()
        m_list=[]
        for l in raw_api_dict['list']:
            idt=l['dt']
            temp=l['main']['temp']-273.15
            humidity=l['main']['humidity']
            clouds=l['clouds']['all']
            rain=0
            snow=0
            if 'snow' in l:
                if '3h' in l['snow']:
                    snow=l['snow']['3h']
            if 'rain' in l:
                if '3h' in l['rain']:
                    rain=l['rain']['3h']
            m_list.append([temp, humidity,rain, snow, clouds, idt])
        return m_list, timestamp
        
    def mqtt_sendForecast(self, m_list, timestamp):
        for ii in range(5):
            start=ii*8
            stop=start+7
            t=[]
            h=[]
            r=0
            for el in m_list[start:stop+1]:
                t.append(el[0])
                h.append(el[1])
                r+=el[2]+el[3]
            t_start=m_list[start][5]
            t_stop=m_list[stop][5]+(3600*3)
            senML={}
            senML['bn']=self.clientID
            senML['bt']=timestamp
            senML['e']=[]
            senML['e'].append({'n': 'temperature', 'u': "degC", 't': 0, "v":np.mean(t)})
            senML['e'].append({'n': 'humidity', 'u': "%", 't': 0, "v":np.mean(h)})
            senML['e'].append({'n': 'rain', 'u': "mm/3h", 't': 0, "v":r})
            senML['e'].append({'n': 't_start', 'u': 's', 't': 0, "v":t_start})
            senML['e'].append({'n': 't_stop', 'u': 's', 't': 0, "v":t_stop})
            js=json.dumps(senML)
            self.mqtt_publish(topic='measurement/forecast', message=js)
    
    def mqtt_start(self):
        Publisher.mqtt_start(self)
        if self.was_new==True:
            message=json.dumps(self.conf['station'])
            self.mqtt_publish(topic='alert/new_station', message=message)
            
    def routine(self):
        self.mqtt_start()
        a=0
        while (a<3):
            b=0
            m_list,timestamp=self.http_getForecast()
            self.mqtt_sendForecast(m_list, timestamp)
            time.sleep(2)
            while (b<3):
                self.simulateSensors()
                time.sleep(2)
                b+=1
            a+=1
        self.mqtt_stop()
    
if __name__ == '__main__':
    
    station=ITV_Station()
    station.routine()