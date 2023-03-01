'''
Created on Feb 23, 2023

@author: nigel
'''
import os
from pathlib import Path
from DSStoreProtocol import DSStoreProtocol
from DSMessage import DSMessage
from DSFile import DSFile

class DSServerOps(object):
    '''
    classdocs
    '''


    def __init__(self, proto : DSStoreProtocol):
        '''
        Constructor
        '''
        self._spath = os.getcwd() + '/store/'
        self._sproto = proto
        self._route = {'STOR': self._doStore,
                       'DELE': self._doDelete,
                       'RETR': self._doRetrieve}
        
    def _getRequest(self) -> (str, DSFile):
        req = self._sproto.getRequest()
        reqcmd = req.getType()
        reqfile = DSFile('unk') # dummy name
        reqfile.unmarshal(req.getData())
        return reqcmd,reqfile
    
    def _putResponseFile(self, file : DSFile):
        resp = DSMessage()
        resp.setType('DATA')
        resp.setData(file.marshal())
        self._sproto.putResponse(resp)
            
    def _putResponseGood(self, message :  str):
        resp = DSMessage()
        resp.setType('OKOK')
        resp.setData(message.encode('utf-8'))
        self._sproto.putResponse(resp)
    
    def _putResponseError(self, message :  str):
        resp = DSMessage()
        resp.setType('ERRO')
        resp.setData(message.encode('utf-8'))
        self._sproto.putResponse(resp)
        
    def _doStore(self, file : DSFile):
        fullpath = self._spath + file.getFName()
        file.setFName(fullpath)
        file.writeData()
        self._putResponseGood('file saved')
    
    def _doDelete(self, file : DSFile):
        fullpath = self._spath + file.getFName() # set the store path
        fpath = Path(fullpath)
        if fpath.is_file():
            fpath.unlink()
            self._putResponseGood('file removed')
        else:
            self._putResponseError('file does not exist')
            
    
    def _doRetrieve(self, file : DSFile):
        fullpath = self._spath + file.getFName() # set the store path
        if Path(fullpath).exists():
            file.setFName(fullpath)
            file.readData()
            file.setFName(Path(fullpath).name) # remove the store path
            self._putResponseFile(file)  
        else:
            self._putResponseError('unknown file')    
            
    def run(self):
        print("Storage Location: "+self._spath)

        # only one request
        cmd, file = self._getRequest()
        self._route[cmd](file)
        self._sproto.close()
    