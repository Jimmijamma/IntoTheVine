'''
Created on 13 giu 2018

@author: jimmijamma
'''

from ITV_Station import ITVStation
from ITV_System import ITVSystem
from ITV_User import ITVUser
from telegramBot import TelegramBot


if __name__ == '__main__':
    botty=TelegramBot('jimmijamma')
    botty.start_polling()
    botty.mqtt_start()
    
    user=ITVUser(578155659)
    system=ITVSystem(user,loc_name="Torino",id=0)
    station=ITVStation(system,id=0)
    station.mqtt_start()
    station.simulateSensors()
    
    system2=ITVSystem(user,loc_name="Dehli",id=1)
    station2=ITVStation(system2,id=2)
    station2.mqtt_start()
    station2.simulateSensors()