'''
Created on Feb 23, 2023

@author: nigel
'''
from DSComm import DSComm
from DSMessage import DSMessage
from DSFile import DSFile

class DSStoreProtocol(object):
    '''
    classdocs
    '''


    def __init__(self, comm : DSComm = -1):
        '''
        Constructor
        '''
        self._dscomm = comm
        
    def close(self):
        self._dscomm.close()
    
    # server needs
    def getRequest(self) -> DSMessage:
        return self._dscomm.recvMessage()
    
    def putResponse(self, resp : DSMessage):
        self._dscomm.sendMessage(resp)
    
    # client needs
    def sendRequest(self, req : DSMessage) -> DSMessage:
        self._dscomm.sendMessage(req)
        resp = self._dscomm.recvMessage()
        return resp
    
    # these are just for convience, the ops can create any message
    def storeFile(self, file : DSFile) -> DSMessage:
        req = DSMessage()
        req.setType('STOR')
        req.setData(file.marshal())
        return self.sendRequest(req)

    def retrieveFile(self, file : DSFile) -> DSMessage:
        req = DSMessage()
        req.setType('RETR')
        req.setData(file.marshal())
        return self.sendRequest(req)

    def deleteFile(self, file : DSFile):
        req = DSMessage()
        req.setType('DELE')
        req.setData(file.marshal())
        return self.sendRequest(req)
    
    