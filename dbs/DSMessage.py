'''
Created on Feb 15, 2023

@author: nigel
'''

from enum import Enum

class DSMessage(object):
    '''
    classdocs
    '''
    # Constants
    MCMDS = Enum('MCMDS', {'LGIN': 'LGIN', 'STOR': 'STOR', 'RETR': 'RETR','DELE': 'DELE',
                       'LGOT': 'LGOT', 'OKOK': 'OKOK','ERRO': 'ERRO', 'MENU': 'MENU', 'LIST':'LIST', 'NULL':'NULL'})

    PJOIN = '&'
    VJOIN = '{}={}'
    VJOIN1 = '='

    def __init__(self):
        '''
        Constructor
        '''
        self._cmd = DSMessage.MCMDS['OKOK']
        self._data = bytes() # bytearray mutable array, bytes() == b'' is immutable
        
    #===========================================================================
    # def __str__(self) -> str:
    #     '''
    #     Stringify - marshal
    #     '''
    #     return self.marshal()
    #===========================================================================
    
    def reset(self):
        self._cmd = DSMessage.MCMDS['OKOK']
        self._data = bytes()
    
    def setType(self, mtype: str):
        try:
            self._cmd = DSMessage.MCMDS[mtype]
        except:
            self._cmd = DSMessage.MCMDS['NULL']

        
    def getType(self) -> str:
        return self._cmd.value
    
    def setData(self, d: bytes):
        self._data = d
        
    def getData(self) -> bytes:
        return self._data
        
    def marshal(self) -> str:
        size = len(self._data)
        header = '{}{:04}'.format(self._cmd.value, size)
        return b''.join([header.encode('utf-8'), self._data])
    
    def unmarshal(self, value: bytes):
        self.reset()
        if value:
            self._cmd = DSMessage.MCMDS[value[0:4].decode('utf-8')]
            self._data = value[8:]
























