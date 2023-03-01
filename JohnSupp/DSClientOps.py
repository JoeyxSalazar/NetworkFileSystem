'''
Created on Feb 23, 2023

@author: nigel
'''
import socket
from DSStoreProtocol import DSStoreProtocol
from DSComm import DSComm
from DSFile import DSFile


class DSClientOps(object):
    '''
    classdocs
    '''


    def __init__(self):
        '''
        Constructor
        '''
        self._sproto = DSStoreProtocol()
        self._hostname = ""
        self._port = -1
        self._connected = False
        
    def _connect(self):
        if not self._connected:
            commsoc = socket.socket()
            commsoc.connect((self._hostname,self._port))
            dscomm = DSComm(commsoc)
            self._sproto = DSStoreProtocol(dscomm)
            self._connected = True
            
    def _disconnect(self):
        if self._connected:
            self._sproto.close()
            self._connected = False
    
    def setServer(self, host : str, port : int):
        self._hostname = host
        self._port = port
        
    def storeFile(self, file : DSFile) -> (bool, str):
        if not self._connected:
            self._connect()
        resp = self._sproto.storeFile(file)
        self._disconnect()
        
        if resp.getType() == 'OKOK':
            return True, resp.getData().decode('utf-8')
        else:
            return False, resp.getData().decode('utf-8')
        
    def deleteFile(self, file : DSFile) -> (bool, str):
        if not self._connected:
            self._connect()
        resp = self._sproto.deleteFile(file)
        self._disconnect()
        
        if resp.getType() == 'OKOK':
            return True, resp.getData().decode('utf-8')
        else:
            return False, resp.getData().decode('utf-8')    
        
    def retrieveFile(self, file : DSFile) -> DSFile:
        if not self._connected:
            self._connect()
        resp = self._sproto.retrieveFile(file)
        self._disconnect()
        
        if resp.getType() == 'DATA':
            file.unmarshal(resp.getData())
        
        return file 
    