'''
Created on 21 feb 2018

@author: jimmijamma
'''

import paho.mqtt.client as PahoMQTT
import time
from datetime import datetime

class MyPublisher:
    def __init__(self, clientID):
        self.clientID = clientID

        # create an instance of paho.mqtt.client
        self._paho_mqtt = PahoMQTT.Client(self.clientID, False) 
        # register the callback
        self._paho_mqtt.on_connect = self.myOnConnect

    def start (self):
        #manage connection to broker
        self._paho_mqtt.connect('broker.hivemq.com', port=1883)
        print "connected"
        self._paho_mqtt.loop_start()

    def stop (self):
        self._paho_mqtt.loop_stop()
        self._paho_mqtt.disconnect()

    def myPublish(self, topic, message):
        # publish a message with a certain topic
        self. _paho_mqtt.publish(topic, message, 2)

    def myOnConnect (self, paho_mqtt, userdata, flags, rc):
        print ("Connected to message broker with result code: "+str(rc))



if __name__ == "__main__":
    test = MyPublisher("zzzzzzzzzzzzzzzz")
    print "starting..."
    test.start()
    print 'started'

    a = 0
    while (a < 20):
        now = time.time()
        message = str(578155659)
        print ("Publishing: '%s'" % (message))
        test.myPublish ('notify', message)     
        a += 1
        time.sleep(2)

    test.stop()
