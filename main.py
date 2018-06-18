'''
Created on 13 giu 2018

@author: jimmijamma
'''

from ITV_Station import ITVStation
from ITV_System import ITVSystem
from ITV_User import ITVUser
from telegramBot import TelegramBot
from ITV_LM_Trainer import ITV_LM_Trainer
from ITV_RiskScale import ITV_RiskScale
from ITV_WeatherForecast import WeatherForecast

if __name__ == '__main__':
    
    '''
    lm_t=ITV_LM_Trainer("/Users/jimmijamma/Desktop/Dataset.xlsx")
    lm_t.parseDataset()
    lm_t.trainModel()
    lm_t.testModel()
    '''
    
    
    botty=TelegramBot('jimmijamma')
    botty.start_polling()
    botty.mqtt_start()
    
    riskscale=ITV_RiskScale()
    riskscale.mqtt_start()
 
    
    user=ITVUser(578155659)
    '''
    system=ITVSystem(user,loc_name="Torino",id=0)
    station=ITVStation(system,id=0)
    station.mqtt_start()
    station.simulateSensors()
    '''
    system2=ITVSystem(user,loc_name="Oslo",id=1)
    station2=ITVStation(system2,id=2)
    station2.mqtt_start()
    station2.simulateSensors()
    
    wf=WeatherForecast(system2)
    wf.mqtt_start()
    wf.five_days_forecast()
    