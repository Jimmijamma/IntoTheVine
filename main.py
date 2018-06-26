'''
Created on 13 giu 2018

@author: jimmijamma
'''

from ITV_TelegramBot import ITV_TelegramBot
from ITV_MachineLearning import ITV_MachineLearning
from ITV_RiskScale import ITV_RiskScale
from ITV_WeatherForecast import ITV_WeatherForecast
import time
   
    
if __name__ == '__main__':

    print
    print "Instantiating classes..."
    botty=ITV_TelegramBot()
    ml=ITV_MachineLearning()
    riskscale=ITV_RiskScale()

    
    print
    print "Starting up communications..."
    botty.mqtt_start()
    ml.mqtt_start()
    riskscale.mqtt_start()


    botty.start_polling()

    
    time.sleep(20)
    print
    
    print "Stopping MQTT..."
    ml.mqtt_stop()
    botty.mqtt_stop()
    riskscale.mqtt_stop()