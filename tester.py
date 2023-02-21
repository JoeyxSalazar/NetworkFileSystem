'''
Created on Feb 15, 2023

@author: nigel
'''

from DSMessage import DSMessage

if __name__ == '__main__':
    mess1 = DSMessage()
    mess1.setType('DATA')
    mess1.setData(b'helloworld')
    print(mess1.marshal())
    
    mess2 = DSMessage()
    mess2.unmarshal(mess1.marshal())
    print(mess2.marshal())