'''
Created on 19 giu 2018

@author: jimmijamma
'''
from datetime import datetime

class ITV_Util(object):
    '''
    classdocs
    '''


    def __init__(self):
        '''
        Constructor
        '''
        pass
    
    def checkDate(self,date):
        n_days=(datetime.today()-date).days
        if n_days==0:
            s_days='today'
        elif n_days==1:
            s_days='yesterday'
        elif n_days==-1:
            s_days='next 24 hours'
        else:
            s_days=str(n_days)+' days'
        return s_days