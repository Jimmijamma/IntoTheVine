'''
Created on 13 giu 2018

@author: jimmijamma
'''

class ITVUser(object):
    '''
    classdocs
    '''


    def __init__(self,id):
        '''
        Constructor
        '''
        self.id=str(id)
        self.name=None
        self.surname=None
        self.email=None
        self.phone_number=None
        self.systems_list=[]
        
    