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
import Adafruit_DHT
from threading import Thread

class ITV_Station(Publisher):
    '''
    classdocs
    '''
    def __init__(self):
        '''
        Constructor
        '''
        fp=open('ITV_Station_config.JSON','r')
        self.conf=json.load(fp)
        fp.close()
        # loading the address of the Catalog
        catalog_ip=self.conf['catalog']['ip']
        catalog_port=self.conf['catalog']['port']
        self.catalog_url='http://'+str(catalog_ip)+':'+str(catalog_port)
        # loading the station parameters
        self.user=self.conf['station']['user']
        self.lat=self.conf['station']['lat']
        self.lon=self.conf['station']['long']
        is_new=self.conf['station']['is_new']
        # install the station if it's the first startup
        self.was_new=False
        self.installStation(is_new)
        # load settings from the catalog
        self.loadSettings()
        # MQTT override
        id_string = 'ITV_Station/'+str(self.user)+'/'+str(self.id)
        super(ITV_Station,self).__init__(clientID=id_string)
    
    def loadSettings(self):
        res = urllib.urlopen(self.catalog_url+'/system_conf/openweathermap')
        res_obj=json.load(res)
        self.appid=res_obj['appid']
        self.weather_url=res_obj['weather_url'].replace('<lat>',self.lat).replace('<lon>',self.lon).replace('<appid>',self.appid)
        self.forecast_url=res_obj['forecast_url'].replace('<lat>',self.lat).replace('<lon>',self.lon).replace('<appid>',self.appid)
        
    def installStation(self, is_new):
        if is_new==True:
            self.was_new=True
            id=''.join(random.choice('0123456789abcdefghijklmnopqrstuvwyxz') for i in range(5))
            self.id=id
            self.conf['station']['id']=self.id
            self.conf['station']['is_new']=False
            fp=open('ITV_Station_config.JSON','w')
            json.dump(self.conf, fp)
            fp.close()
            payload=json.dumps(self.conf['station'])
            requests.put(self.catalog_url+'/add_station/',data=payload)
        else:
            self.id=self.conf['station']['id']
     
          
    def realSensor(self):
        sensor = Adafruit_DHT.DHT22
        pin = 2
        humidity, temperature = Adafruit_DHT.read_retry(sensor, pin)
        return humidity, temperature
    
            
    def simulateSensors(self):
        temp,humidity,rain,snow,clouds=self.http_getWeather()
        humidity,temp=self.realSensor()
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
        url = urllib.urlopen(self.weather_url)
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
        url = urllib.urlopen(self.forecast_url)
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
        res=requests.get(self.catalog_url+'/getUserInfo/'+str(self.user))
        ndaysforecast=res.json()['settings']['ndaysforecast']
        for ii in range(ndaysforecast):
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
    
    def sensor_routine(self, t_end):
        res=requests.get(self.catalog_url+'/getUserInfo/'+str(self.user))
        iw=res.json()['settings']['interval_weather']
        while time.time()<t_end:
            self.simulateSensors()
            time.sleep(iw/10)
            
    def forecast_routine(self, t_end):
        res=requests.get(self.catalog_url+'/getUserInfo/'+str(self.user))
        iw=res.json()['settings']['interval_forecast']
        while time.time()<t_end:
            m,t=self.http_getForecast()
            self.mqtt_sendForecast(m, t)
            time.sleep(iw/10)
    
    def global_routine(self):
        self.mqtt_start()
        t_end = time.time() + 80
        thread_w = Thread(target = self.sensor_routine, args=[t_end])
        thread_f = Thread(target = self.forecast_routine, args=[t_end])
        thread_w.start()

        thread_f.start()
        thread_w.join()
        thread_f.join()
        self.mqtt_stop()
    
if __name__ == '__main__':
    
    station=ITV_Station()
    station.global_routine()