'''
Created on 13 giu 2018

@author: jimmijamma
'''
from geopy.geocoders import Nominatim

class ITVSystem(object):
    '''
    classdocs
    '''

    def __init__(self, admin,loc_name,id):
        geolocator = Nominatim()
        location = geolocator.geocode(loc_name)
        if location!=None:
            self.loc_name=loc_name
            self.loc_lat=str(location.latitude)
            self.loc_long=str(location.longitude)
            state=location.address.split(',')[-1]
            print "Initialized system in %s,%s\nWith coordinates (%s,%s)"%(self.loc_name,state,self.loc_lat,self.loc_long)
            self.id=str(id)
            self.user=admin
            self.users_list=[]
            self.users_list.append(admin)
            self.sensors_list=[]
        else:
            print "No city was found with name: %s"%loc_name
            pass
        
    def addSensor(self,sensor):
        self.sensors_list.append(sensor)
        
    def addUser(self,user,mode):
        self.users_list.append(user)