'''
Created on 20 giu 2018

@author: jimmijamma
'''
import cherrypy
import json
import random

class ITV_Catalog(object):
    '''
    classdocs
    '''
    def __init__(self):
        '''
        Constructor
        '''
        self.DB_file='ITV_DB.JSON'
        fp=open(self.DB_file,'r')
        self.db=json.load(fp)
        fp.close()
        
    exposed=True
        
    def GET(self, *uri, **params):
        if uri[0] == 'system_conf':
            if len(uri)>1:
                for s in self.db['system']:
                    if s['service_id']==uri[1]:
                        return json.dumps(s)
        if uri[0] == 'set_ndaysforecast':
            for u in self.db['users']:
                if u['user_id']==int(uri[1]):
                    u['settings']['ndaysforecast']=int(uri[2])
                    self.update_db()
                    return
                
        if uri[0] == 'getUserSetting':
            for u in self.db['users']:
                if u['user_id']==int(uri[2]):
                    return json.dumps({uri[1]:u['settings'][uri[1]]})

    
    def PUT(self, *uri, **params):
        if uri[0] == 'add_user':
            json_string = cherrypy.request.body.read()
            obj=json.loads(json_string)
            users=self.db['users']
            f=False
            for u in users:
                if 'user_id' in u:
                    if u['user_id']==obj['user_id']:
                        f=True
            if f==False:
                users.append(obj)
                self.update_db()
                cherrypy.response.status = 201
                return 
            else:
                cherrypy.response.status = 400
                return json.dumps({'r':-1})
            
        elif uri[0] == 'add_station':
            json_string = cherrypy.request.body.read()
            request_obj=json.loads(json_string)
            self.add_station(request_obj)
            cherrypy.response.status = 201
            return
        
    def add_station(self, request_obj):
        users=self.db['users']
        for u in users:
            if u['user_id']==request_obj['user']:
                station={}
                station['id']=request_obj['id']
                station['lat']=request_obj['lat']
                station['long']=request_obj['long']
                station['system']=None
                u['stations'].append(station)
                break
        self.update_db()
        return
    
    def update_db(self):
        fp=open(self.DB_file,'w')
        json.dump(self.db, fp)
        fp.close()
    
        
if __name__ == '__main__':
    
    
    conf = {
        '/': {
            'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
            'tools.sessions.on': True
        }
    }
    #startCalculator()
    #startDiscography()
    cherrypy.tree.mount(ITV_Catalog(), '/',  conf)

    cherrypy.engine.start()
    cherrypy.engine.block()
    
    