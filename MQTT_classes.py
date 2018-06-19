'''
Created on 18 giu 2018

@author: jimmijamma
'''
import paho.mqtt.client as PahoMQTT

class Publisher(object):
    '''
    classdocs
    '''
    def __init__(self, clientID):
        '''
        Constructor
        '''
        self.clientID = clientID
        self._paho_mqtt = PahoMQTT.Client(self.clientID, False) 
        self._paho_mqtt.on_connect = self.mqtt_onConnect
        self.broker='127.0.0.1'
        self.port=1883

    def mqtt_start (self):
        #manage connection to broker
        self._paho_mqtt.connect(self.broker, self.port)
        self._paho_mqtt.loop_start()

    def mqtt_stop (self):
        self._paho_mqtt.loop_stop()
        self._paho_mqtt.disconnect()
        
    def mqtt_onConnect(self, paho_mqtt, userdata, flags, rc):
        print "%s connected to message broker with result code: %s" %(self.clientID,str(rc))
        
    def mqtt_publish (self, topic, message):
        # publish a message with a certain topic
        self._paho_mqtt.publish(topic, message, 2)
        print "Message published by %s with topic %s"%(self.clientID,topic)
        
        
class Subscriber(object):
    
    def __init__(self,clientID,sub_topic):
        '''
        Constructor
        '''
        self.clientID = clientID
        self._paho_mqtt = PahoMQTT.Client(self.clientID, False) 
        self._paho_mqtt.on_connect = self.mqtt_onConnect
        self._paho_mqtt.on_message = self.mqtt_onMessageReceived
        self.broker='127.0.0.1'
        self.port=1883
        self.sub_topic = sub_topic

    def mqtt_start (self):
        #manage connection to broker
        self._paho_mqtt.connect(self.broker, self.port)
        self._paho_mqtt.loop_start()
        # subscribe for a topic
        self._paho_mqtt.subscribe(self.sub_topic, 2)

    def mqtt_stop (self):
        self._paho_mqtt.loop_stop()
        self._paho_mqtt.disconnect()
        
    def mqtt_onConnect (self, paho_mqtt, userdata, flags, rc):
        print "%s connected to message broker with result code: %s" %(self.clientID,str(rc))
        
    def mqtt_onMessageReceived (self, paho_mqtt , userdata, msg):
        print 'Message received with payload %s' %msg.payload
    
    
class PublisherSubscriber(object):
    
    def __init__(self, clientID, sub_topic):
        '''
        Constructor
        '''
        self.clientID = clientID
        self._paho_mqtt = PahoMQTT.Client(self.clientID, False) 
        self._paho_mqtt.on_connect = self.mqtt_onConnect
        self._paho_mqtt.on_message = self.mqtt_onMessageReceived
        self.broker='127.0.0.1'
        self.port=1883
        self.sub_topic = sub_topic

    def mqtt_start (self):
        #manage connection to broker
        self._paho_mqtt.connect(self.broker, self.port)
        self._paho_mqtt.loop_start()
        # subscribe for a topic
        self._paho_mqtt.subscribe(self.sub_topic, 2)

    def mqtt_stop (self):
        self._paho_mqtt.loop_stop()
        self._paho_mqtt.disconnect()
        
    def mqtt_onConnect (self, paho_mqtt, userdata, flags, rc):
        print "%s connected to message broker with result code: %s" %(self.clientID,str(rc))
        
    def mqtt_publish (self, topic, message):
        # publish a message with a certain topic
        self._paho_mqtt.publish(topic, message, 2)
        print "Message published by %s with topic %s"%(self.clientID,topic)