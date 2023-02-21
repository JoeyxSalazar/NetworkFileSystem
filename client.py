'''
Created on Feb 17, 2023

@author: Joey Salazar
'''

import socket
import time
from DSMessage import DSMessage
from DSComm import DSComm

middleware = 50000
def listen_for_response(sock):
    comm = DSComm(sock)
    while True:
        mess = comm.recvMessage()
        if mess:
            tipe = mess.getType()
            data = mess.getData().decode('utf-8')
            print(data)
            if tipe == 'OKOK' or tipe == 'ERRO':
                print()
                break


def ClientProtocol(sock):
    msg = DSMessage()
    line = input('Enter Command: ')
    msg.setType(line[:4])
    d = line[4:]
    data = d.encode('utf8')
    msg.setData(data)

    comm = DSComm(sock)
    comm.sendMessage(msg)
    listen_for_response(sock)



if __name__ == '__main__':
    mainserv = socket.socket()
    mainserv.connect(('localhost', middleware))
    while True:
        ClientProtocol(mainserv)
    mainserv.close()
    

