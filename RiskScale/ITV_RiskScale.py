'''
Created on 15 giu 2018

@author: jimmijamma
'''
import json
from MQTT_classes import PublisherSubscriber

class ITV_RiskScale(PublisherSubscriber):
    '''
    classdocs
    '''
    def __init__(self):
        '''
        Constructor
        '''
        # MQTT class override
        clientID='ITV_RiskScale'
        sub_topic='leaf_wetness/#'
        super(ITV_RiskScale,self).__init__(clientID=clientID,sub_topic=sub_topic)
        
    def mqtt_onMessageReceived(self, paho_mqtt, userdata, msg):
        PublisherSubscriber.mqtt_onMessageReceived(self, paho_mqtt, userdata, msg)
        # A new message is received
        risk=self.computeRisk(msg.payload)  
        if msg.topic=='leaf_wetness/station':
            reply_topic='alert/station'
            self.sendAlert(msg.payload, risk, reply_topic)
            
        elif msg.topic=='leaf_wetness/forecast':
            reply_topic='alert/forecast'
            self.sendAlert(msg.payload, risk, reply_topic)

    def computeRisk(self, payload):
        dict_s = payload
        senML=json.loads(dict_s)
        for e in senML['e']:
            if e['n']=='temperature':
                temp=e['v']
            if e['n']=='leaf_wetness':
                lw=e['v']
        if temp<10:
            risk=0
        else:
            if lw>3:
                if lw<6:
                    risk=1
                else:
                    risk=2
            else:
                risk=0
        return risk
    
    def sendAlert(self,payload,risk,reply_topic):
        
        if risk==-1:
            return
        
        else:
            dict_s = payload
            senML=json.loads(dict_s)
            senML['e'].append({'n': 'risk', 'u':None, 't': None, "v":risk})
            message=json.dumps(senML)
            self.mqtt_publish(topic=reply_topic, message=message)
            
if __name__ == '__main__':
    
    rs = ITV_RiskScale()
    rs.mqtt_start()