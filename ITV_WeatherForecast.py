'''
Created on 18 giu 2018

@author: jimmijamma
'''
import urllib
import json
import datetime
import numpy as np
from MQTT_classes import Publisher

class Measurement(object):
    
    def __init__(self,idt,cityname,temp,pressure,humidity,cloudiness,wind,rain,snow):
        self.idt=idt
        self.cityname=cityname
        self.temp=temp
        self.pressure=pressure
        self.humidity_perc=humidity
        self.cloudiness_perc=cloudiness
        self.wind_speed=wind
        self.rain_volume=rain
        self.snow_volume=snow
        date_s=datetime.datetime.utcfromtimestamp(self.idt)
        self.date=str(date_s.day)+'/'+str(date_s.month)
        self.hour=':'.join(str(date_s).split()[1].split(':')[:2])


class WeatherForecast(Publisher):
    
    def __init__(self,system):
        self.system=system
        self.lat=self.system.loc_lat
        self.lon=self.system.loc_long
        self.APPID='f8ac28f78069a7e511c00759939f94b4'
        self.measurement_list=[]
        
        super(WeatherForecast,self).__init__(clientID='ITV_WeatherForecast')
        
    def five_days_forecast(self):
        self.measurement_list=[]
        full_api_url='http://api.openweathermap.org/data/2.5/forecast?lat='+self.lat+'&lon='+self.lon+'&APPID='+self.APPID
        url = urllib.urlopen(full_api_url)
        output = url.read().decode('utf-8')
        raw_api_dict = json.loads(output)
        url.close()
        
        cityname = raw_api_dict['city']['name']
        for l in raw_api_dict['list']:
            idt=l['dt']
            temp=l['main']['temp']-273
            pressure=l['main']['pressure']
            humidity_perc=l['main']['humidity']
            cloudiness_perc=l['clouds']['all']
            wind_speed=l['wind']['speed']
            rain_volume=0
            snow_volume=0
            if 'snow' in l:
                if '3h' in l['snow'] and '3h' in l['rain']:
                    rain_volume=l['rain']['3h']
                    snow_volume=l['snow']['3h']
            m=Measurement(idt,cityname,temp,pressure,humidity_perc,cloudiness_perc,wind_speed,rain_volume,snow_volume)
            self.measurement_list.append(m)
        data={}
        data['measurement_list']=[]
        data['user']=self.system.user.id
        data['system']=self.system.id
        for ii in range(5):
            start=ii*8
            stop=start+7
            t=[]
            h=[]
            r=0
            for el in self.measurement_list[start:stop+1]:
                t.append(el.temp)
                h.append(el.humidity_perc)
                r+=el.rain_volume+el.snow_volume
            msrmnt={}
            msrmnt['temp']=np.mean(t)
            msrmnt['humidity']=np.mean(h)
            msrmnt['rain']=r
            data['measurement_list'].append(msrmnt)
        js=json.dumps(data)
        self.mqtt_publish(topic='measurement/forecast', message=js)
        
    
    