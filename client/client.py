'''
Created on Feb 17, 2023

@author: Joey Salazar
'''

import socket
import time
from DSMessage import DSMessage
from DSComm import DSComm
from DSFile import DSFile

middleware = 50000
global retr_filename
retr_filename = ''
#data is the string of the file that we are retrieving
 

def listen_for_response(sock):
    comm = DSComm(sock)
    while True:
        mess = comm.recvMessage()
        if mess:
            tipe = mess.getType()
            data = mess.getData().decode('utf-8')
            if tipe == 'OKOK' or tipe == 'ERRO':
                print(tipe)
                print(data)
                break
            elif tipe == 'DATA':
                global retr_filename
                try:
                    print(retr_filename)
                    with open('downloads/' + retr_filename, 'w') as file:
                        file.write(data)
                        print(tipe)
                        print('File Retrieved! Look in \'downloads\' folder to access!')
                        break
                except:
                    print('Couldnt write to file')
                    break
            else:
                print('Unknown Error :/')
                print(tipe + ':' + data)
                break


def ClientProtocol(sock):
    while True:
        msg = DSMessage()
        line = input('Enter Command: ')
        #Extracts the command that we are going to execute, and extracts the file name
        msg.setType(line[:4])
        d = line[4:]
        #Keeps data if 'LIST' or 'LGIN' or 'LGOT' is called
        msg.setData(d.encode('utf-8'))


        if msg.getType() == 'RETR' or msg.getType() == 'STOR':
            global retr_filename
            if msg.getType() == 'RETR':
                retr_filename = d
                break
            else: #store
                conts = ''
                try:
                    with open(d, 'r') as file:
                        conts = file.read()
                    newdata = d + ':' + conts
                    msg.setData(newdata.encode('utf-8'))
                    break
                except:
                    print('Invalid path, try again')
        break
            #'Fname:file_data'

    #sends message to middleware
    comm = DSComm(sock)
    comm.sendMessage(msg)
    listen_for_response(sock)



if __name__ == '__main__':
    mainserv = socket.socket()
    mainserv.connect(('localhost', middleware))
    while True:
        ClientProtocol(mainserv)
    mainserv.close()
    
    

