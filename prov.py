'''
Created on 18 giu 2018

@author: jimmijamma
'''
from MQTT_classes import Publisher, Subscriber
import time

class Bello(Publisher):
    
    def __init__(self,clientID):
        super(Bello,self).__init__(clientID)
        
    def lol(self):
        super(Bello,self).mqtt_start()
        
class Brutto(Subscriber):
    
    def __init__(self,clientID,sub_topic):
        super(Brutto,self).__init__(clientID,sub_topic)
    
    
       
if __name__ == '__main__':
    b=Bello('Mori321412')
    s=Brutto('Msadas','ciao')
    s.mqtt_start()
    b.mqtt_start()
    
    time.sleep(5)
    b.mqtt_publish(topic='ciao', message='lolletto')
    time.sleep(5)
    b.mqtt_stop()
    s.mqtt_stop()