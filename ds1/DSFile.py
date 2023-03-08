'''
Created on Feb 15, 2023

@author: nigel
'''

class DSFile(object):
    '''
    classdocs
    '''

    PJOIN = b'&'
    VJOIN = '{}={}'
    VJOIN1 = '='

    def __init__(self, f : str):
        '''
        Constructor
        '''
        self._filename = f
        self._filesize = 0
        self._filedata = bytes()
        
    def hasData(self):
        return (self._filesize>0)
        
    def setFName(self, fname : str):
        self._filename = fname
        
    def getFName(self) -> str:
        return self._filename;
        
    def readData(self):
        fin = open(self._filename,'rb')
        self._filedata = fin.read()
        self._filesize = len(self._filedata)
        fin.close()
    
    def writeData(self):
        fout = open(self._filename,'wb')
        fout.write(self._filedata)
        fout.close()
    
    def marshal(self) -> bytes:
        #filename=name_of_file&size=size_of_file&file_data
        fname = DSFile.VJOIN.format('filename', self._filename).encode('utf-8')
        size = DSFile.VJOIN.format('size', self._filesize).encode('utf-8')
        return DSFile.PJOIN.join([fname, size, self._filedata])
    
    def unmarshal(self, value : bytes):
        if (value):
            finfo = value.split(DSFile.PJOIN)

            self._filename = finfo[0].split(b'=')[1].decode('utf-8')
            self._filesize = int(finfo[1].split(b'=')[1].decode('utf-8'))
            if self._filesize>0:
                self._filedata = finfo[2]
            else:
                self._filedata = bytes()
            