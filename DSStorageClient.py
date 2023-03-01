'''
Created on Feb 28, 2023

@author: nigel
'''

from pathlib import Path
from DSFile import DSFile
from DSClientOps import DSClientOps

if __name__ == '__main__':
    client = DSClientOps()
    client.setServer('localhost', 50000)
    
    # STOR test
    # get filename from user
    fname = input('Enter file to store:')
    fpath = Path(fname)
    if fpath.exists():
        file = DSFile(fname)
        file.readData()
        file.setFName(fpath.name)
        ret, mess = client.storeFile(file)
        print(mess)
    else:
        print('unknown path, skipping')
        
    # RETR test
    # get filename from user
    fname = input('Enter file to retrieve:')
    file = DSFile(fname)
    file = client.retrieveFile(file)
    if file.hasData():
        # store locally with _1 appended
        file.setFName(file.getFName()+'_1')
        file.writeData()
        print('retrieve successful')
    else:
        print('retrieve failed')
        
    # DELE test
    # get filename from user
    fname = input('Enter file to delete:')
    file = DSFile(fname)
    ret, mess = client.deleteFile(file)
    print(mess)
    
    