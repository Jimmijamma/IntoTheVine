'''
Created on 13 giu 2018

@author: jimmijamma
'''

from MachineLearning import ITV_MachineLearning.ITV_MachineLearning
from ITV_RiskScale import ITV_RiskScale
import time
   
    
if __name__ == '__main__':

    print
    print "Instantiating classes..."
    ml=ITV_MachineLearning()
    riskscale=ITV_RiskScale()

    
    print
    print "Starting up communications..."
    ml.mqtt_start()
    riskscale.mqtt_start()

    
    time.sleep(20)
    print
    
    print "Stopping MQTT..."
    ml.mqtt_stop()
    riskscale.mqtt_stop()