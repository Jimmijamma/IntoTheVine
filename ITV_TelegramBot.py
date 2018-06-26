'''
Created on 19 mag 2018

@author: jimmijamma
'''

from telegram.ext import Updater,CommandHandler,Filters,MessageHandler
import logging
import json
import urllib
from datetime import datetime
from MQTT_classes import Subscriber
from ITV_Util import ITV_Util
import requests


class ITV_TelegramBot(Subscriber):
    '''
    Class for sending notifications using Telegram
    '''
    
    def __init__(self):
        
        self.id='ITV_TelegramBot'

        config_json=self.loadConfig()
        self.token=config_json['token']
        self.updater=Updater(token=self.token)
        self.dispatcher = self.updater.dispatcher
        
        # for managing errors
        logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',level=logging.INFO)
        self.job_queue=self.updater.job_queue
        
        # MQTT override
        sub_topic='alert/#'
        super(ITV_TelegramBot,self).__init__(clientID=self.id,sub_topic=sub_topic)
        
        # Message handlers
        start_handler = CommandHandler('start', self.msg_start)
        self.dispatcher.add_handler(start_handler)
        echo_handler = MessageHandler(Filters.text, self.msg_echo)
        self.dispatcher.add_handler(echo_handler)
        
    def loadConfig(self):
        fp=open('ITV_TelegramBot_config.JSON','r')
        conf=json.load(fp)
        fp.close()
        self.catalog_ip=conf['catalog_ip']
        self.catalog_port=conf['catalog_port']
        # TelegramBot attributes
        res = urllib.urlopen('http://'+self.catalog_ip+':'+str(self.catalog_port)+'/system_conf/ITV_TelegramBot')
        res_obj=json.load(res)
        return res_obj

    def start_polling(self):
        # to start the bot
        self.updater.start_polling()
        print "Bot started polling."
        
    def msg_start(self, bot, update):
        chat_id=update.message.chat_id
        payload={}
        payload['chat_id']=chat_id
        payload['systems']=[]
        payload['conf']=[]
        payload=json.dumps(payload)
        r=requests.put('http://'+self.catalog_ip+':'+self.catalog_port+'/add_user',data=payload)
        r=r.status_code
        if r==201:
            text="Congratulations! You have just signed in IntoTheVine!\n"
            text+="Your ID is %s" %(chat_id)
        elif r==400:
            text="You have already an ITV account"
        bot.send_message(chat_id=chat_id, text=text)
        
    def msg_echo(self,bot, update):
        bot.send_message(chat_id=update.message.chat_id, text='Sorry, this is not a command. All commands start with \'/\'')
        
    def mqtt_onMessageReceived(self, paho_mqtt, userdata, msg):
        Subscriber.mqtt_onMessageReceived(self, paho_mqtt, userdata, msg)
        # A new message is received
        if msg.topic=='station':
            chat_id,message=self.parseWeather(msg.payload)
        elif msg.topic=='alert/station':
            chat_id,message=self.parseAlertStation(msg.payload)
        elif msg.topic=='alert/forecast':
            chat_id,message=self.parseAlertForecast(msg.payload)
        elif msg.topic=='alert/new_station':
            chat_id,message=self.sendAlertNewStation(msg.payload)
        def callback_now(bot,job,chat_id=chat_id,text=message):
            bot.send_message(chat_id=chat_id, text=text, parse_mode='HTML')
        self.job_queue.run_once(callback_now, when=0)
        
    def parseAlertStation(self, payload):
        dict_s = payload
        senML=json.loads(dict_s)
        clientID=senML['bn'].split('/')
        chat_id=clientID[1]
        system=clientID[2]
        station=clientID[3]
        alert_msg='<b>Alert!</b>\n'
        dot_list=''
        for e in senML['e']:
            if e['n']!='risk':
                if e['n']=='leaf wetness':
                    dot_list+='> %s = <b>%s %s</b>\n'%(e['n'],e['v'],e['u'])
                else:   
                    dot_list+='> %s = <b>%.2f %s</b>\n'%(e['n'],e['v'],e['u'])
            else:
                if e['v']==1:
                    msg1="Weather status at <b>station '%s'</b> of your <b>system '%s'</b> is worrying:\n"%(station,system)
                    msg2="You'd better administrate the treatment."
        
                elif e['v']==2:
                    msg1="Weather status at <b>station '%s'</b> of your system <b>'%s'</b> is <b>critic</b>:\n"%(station,system)
                    msg2="<b>Absolutely</b> administrate the treatment."
        alert_msg+=msg1+dot_list+msg2
        return chat_id,alert_msg
    
    def parseAlertForecast(self, payload):
        dict_s = payload
        senML=json.loads(dict_s)
        clientID=senML['bn'].split('/')
        chat_id=clientID[1]
        system=clientID[2]
        station=clientID[3]
        ut=ITV_Util()
        s_days=ITV_Util().checkDate(datetime.utcfromtimestamp(senML['bt']))
        last_update='(Last update: %s)\n'%s_days
        alert_msg='<b>Alert!</b>\n'
        dot_list=''
        for e in senML['e']:
            if e['n']!='risk' and e['n']!='t_start' and e['n']!='t_stop':
                if e['n']=='leaf wetness':
                    dot_list+='> %s = <b>%s %s</b>\n'%(e['n'],e['v'],e['u'])
                else:   
                    dot_list+='> %s = <b>%.2f %s</b>\n'%(e['n'],e['v'],e['u'])
            elif e['n']=='risk':
                if e['v']==1:
                    msg1="Forecast status at <b>station '%s'</b> of your <b>system '%s'</b> is worrying:\n"%(station,system)
                    msg2="You'd better administrate the treatment."
        
                elif e['v']==2:
                    msg1="Forecast status at <b>station '%s'</b> of your system <b>'%s'</b> is <b>critic</b>:\n"%(station,system)
                    msg2="<b>Absolutely</b> administrate the treatment."
            elif e['n']=='t_start':
                t_start=datetime.utcfromtimestamp(e['v'])
            elif e['n']=='t_stop':
                t_stop=datetime.utcfromtimestamp(e['v'])
        time_interval='Time interval: %s - %s\n'%(t_start,t_stop)
        alert_msg+=time_interval+msg1+dot_list+last_update+msg2
        return chat_id,alert_msg
    
    def sendAlertNewStation(self,payload):
        dict_s = payload
        obj=json.loads(dict_s)
        chat_id=obj['user']
        station_id=obj['id']
        longit=obj['long']
        lat=obj['lat']
        alert_msg='<b>Congratulations!</b>\n'
        alert_msg+='Your new station (id: %s) has been successfully installed at lat: %s, long: %s'%(str(station_id),str(lat),str(longit))
        return chat_id,alert_msg
        
if __name__ == '__main__':
    
    bot=ITV_TelegramBot()

 