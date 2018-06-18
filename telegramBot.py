'''
Created on 19 mag 2018

@author: jimmijamma
'''

from telegram.ext import Updater,CommandHandler,Filters,MessageHandler
import logging
import json
import paho.mqtt.client as PahoMQTT
import time


MIO_ID=578155659

def checklist(chat_id):
    jf=open('chatIDs.JSON','rb')
    jo=json.load(jf)
    jf.close()
    if chat_id not in jo['ID_list']:
        jo['ID_list'].append(chat_id)
        jf=open('chatIDs.JSON','wb')
        js=json.dumps(jo)
        jf.write(js)
        jf.close()
        return "Congratulations! You just activated IntoTheVine bot! Your ID is %d" %chat_id
    else:
        return "Your bot is already activated"
        
class TelegramBot(object):
    '''
    Class for sending notifications using Telegram
    '''
    
    def __init__(self, clientID):
        
        # TelegramBot attributes
        self.token='610146619:AAFydsAw1I2QTCRI2mHzSEkifekuI3VM5sU'
        self.updater=Updater(token=self.token)
        self.dispatcher = self.updater.dispatcher
        # for managing errors
        logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',level=logging.INFO)
        self.job_queue=self.updater.job_queue
        
        # MQTT attributes
        self.clientID = clientID
        self._paho_mqtt = PahoMQTT.Client(clientID, False)
        # register the callback
        self._paho_mqtt.on_connect = self.myOnConnect
        self._paho_mqtt.on_message = self.myOnMessageReceived
        self.topic = '#'
        
        start_handler = CommandHandler('start', self.msg_start)
        self.dispatcher.add_handler(start_handler)
        echo_handler = MessageHandler(Filters.text, self.msg_echo)
        self.dispatcher.add_handler(echo_handler)

    
    def start_polling(self):
        # to start the bot
        self.updater.start_polling()
        print "Bot started polling."
       
    def mqtt_start (self):
        #manage connection to broker
        self._paho_mqtt.connect('127.0.0.1', 1883)
        self._paho_mqtt.loop_start()
        # subscribe for a topic
        self._paho_mqtt.subscribe(self.topic, 2)

    def mqtt_stop (self):
        self._paho_mqtt.unsubscribe(self.topic)
        self._paho_mqtt.loop_stop()
        self._paho_mqtt.disconnect()
        
    def msg_start(self, bot, update):
        chat_id=update.message.chat_id
        jf=open('chatIDs.JSON','rb')
        jo=json.load(jf)
        jf.close()
        if chat_id not in jo['ID_list']:
            jo['ID_list'].append(chat_id)
            jf=open('chatIDs.JSON','wb')
            js=json.dumps(jo)
            jf.write(js)
            jf.close()
            text='Congratulations! You just activated IntoTheVine bot! Your ID is %d' %chat_id
        else:
            text="Your bot is already activated"
        bot.send_message(chat_id=update.message.chat_id, text=text)
        
    def msg_echo(self,bot, update):
        bot.send_message(chat_id=update.message.chat_id, text='Sorry, this is not a command. All commands start with \'/\'')
        print "%d sent a message" %update.message.chat_id

    def myOnConnect (self, paho_mqtt, userdata, flags, rc):
        print ("Connected to message broker with result code: "+str(rc))

    def myOnMessageReceived (self, paho_mqtt , userdata, msg):
        # A new message is received
        if msg.topic=='station':
            chat_id,message=self.parseWeather(msg.payload)
        elif msg.topic=='alert/weather':
            chat_id,message=self.parseAlertWeather(msg.payload)
        elif msg.topic=='alert/forecast':
            chat_id,message=self.parseAlertForecast(msg.payload)
        def callback_now(bot,job,chat_id=chat_id,text=message):
            bot.send_message(chat_id=chat_id, text=text, parse_mode='HTML')
        self.job_queue.run_once(callback_now, when=0)
        
        
    def parseWeather(self, payload):
        dict_s = payload
        data=json.loads(dict_s)
        chat_id=data['user']
        system=data['system']
        station=data['station']
        temp=data['temp']
        humidity=data['humidity']
        rain=data['rain']
        snow=data['snow']
        clouds=data['clouds']
        message="Weather status at <b>station '%s'</b> of your <b>system '%s'</b>:\n"%(station,system)
        message+='> temperature = <b>%.2f C</b>\n' %temp
        message+='> humidity = <b>%d %%</b>\n' %humidity
        message+='> rain = <b>%d mm/3h</b>\n' %rain
        message+='> snow = <b>%d mm/3h</b>\n' %snow
        message+='> cloudiness = <b>%d %%</b>\n' %temp
        return chat_id,message
    
    def parseAlertWeather(self, payload):
        dict_s = payload
        data=json.loads(dict_s)
        chat_id=data['user']
        system=data['system']
        station=data['station']
        risk=data['risk']
        if risk==1:
            message="ALERT! The situation at station %s of your system %s is worrying.\n" %(station,system)
            message+="You'd better administrate the treatment."
        elif risk==2:
            message="ALERT! The situation at station %s of your system %s is CRITIC.\n"%(station,system)
            message+="ABSOLUTELY administrate the treatment."
        return chat_id,message
    
    def parseAlertForecast(self, payload):
        dict_s = payload
        data=json.loads(dict_s)
        chat_id=data['user']
        system=data['system']
        risk=data['risk']
        if risk==1:
            message="ALERT! The forecast for your system %s is worrying.\n" %system
            message+="You'd better administrate the treatment."
        elif risk==2:
            message="ALERT! The forecast for your system %s is CRITIC.\n" %system
            message+="ABSOLUTELY administrate the treatment."
        return chat_id,message



if __name__ == '__main__':
    
    botty=TelegramBot('jimmijamma')
    botty.start_polling()
    botty.mqtt_start()
    
    
    
    '''
    jf=open('chatIDs.JSON','w')
    data={}
    data['ID_list']=[]
    js=json.dumps(data)
    jf.write(js)
    jf.close()
    '''
