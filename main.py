'''
Created on 13 giu 2018

@author: jimmijamma
'''

from ITV_Station import ITV_Station
from ITV_System import ITVSystem
from ITV_User import ITVUser
from ITV_TelegramBot import ITV_TelegramBot
import ITV_ML_Trainer.ITV_LM_Trainer
from ITV_RiskScale import ITV_RiskScale
from ITV_WeatherForecast import WeatherForecast

if __name__ == '__main__':
    
    '''
    jf=open('chatIDs.JSON','w')
    data={}
    data['ID_list']=[]
    js=json.dumps(data)
    jf.write(js)
    jf.close()
    '''

    
    '''
    lm_t=ITV_ML_Trainer("/Users/jimmijamma/Desktop/Dataset.xlsx")
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
    system2=ITVSystem(user,loc_name="Torino",id=1)
    station2=ITV_Station(system2,id=2)
    station2.mqtt_start()
    station2.simulateSensors()
    
    wf=WeatherForecast(system2)
    wf.mqtt_start()
    wf.five_days_forecast()
    
    botty.mqtt_stop()
    riskscale.mqtt_stop()
    station2.mqtt_stop()
    wf.mqtt_stop()
    