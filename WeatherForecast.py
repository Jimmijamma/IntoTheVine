'''
Created on 07 feb 2018

@author: jimmijamma
'''
import urllib
import json
import datetime

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
        self.date=datetime.datetime.utcfromtimestamp(self.idt)


class WeatherForecast(object):
    
    def __init__(self,lat,lon,APPID):
        self.lat=str(lat)
        self.lon=str(lon)
        self.APPID=APPID
        self.measurement_list=[]
        
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
    
if __name__ == '__main__':
    wf=WeatherForecast(lat=45.075,lon=8.3925,APPID='f8ac28f78069a7e511c00759939f94b4')
    wf.five_days_forecast()
        
    for m in wf.measurement_list:
        print m.date
        print m.cityname
        print str(m.rain_volume) + " mm/3h"
        print str(m.temp) + " deg"
        print str(m.humidity_perc)
        print 