'''
Created on Feb 17, 2023

@author: Joey Salazar
'''

import socket
import time
from DSMessage import DSMessage
from DSComm import DSComm

middleware = 51000

# 'filename:file_contents'
# assume string is decoded already
def decode_file_contents(string):
    filename, file_content = string.split(":")
    size_of_content = len(file_content)
    return filename, size_of_content, file_content
    #filename = filename.strip("'")
    #file_content = file_content.strip("'")

def send_data(data, type, sock):
    mess = DSMessage()
    mess.setType(type)
    mess.setData(data.encode('utf-8'))
    comm = DSComm(sock)
    comm.sendMessage(mess)

def check_if_overwrite():
    pass

def overwrite():
    pass

def stor_file(data, midsock):
    try:
        fname, size, content = decode_file_contents(data)
    except:
        send_data('File contents not formatted correctly', 'ERRO', midsock)
    """
    Fill protocol here
    if check_if_overwrite() == True:
        overwrite()
    else:
    """
    print('Filename: ', fname, '\t', 'Contents: ', content)
    send_data(fname, 'OKOK', midsock)

def retr_file(fname, midsock):
    try:
        send_data('You called RETR', 'OKOK', midsock)
    except:
        send_data('File contents not formatted correctly', 'ERRO', midsock)
    #Fill protocol here

def dele_file(data, midsock):
    try:
        send_data('You called DELE', 'OKOK', midsock)
    except:
        send_data('File contents not formatted correctly', 'ERRO', midsock)
    #Fill protocol here
    

def decode_cmd(cmd, data, midsock):

    if cmd == 'STOR':
        stor_file(data, midsock)
    elif cmd == 'RETR':
        retr_file(data, midsock)
    elif cmd == 'DELE':
        dele_file(data, midsock)
    else:
        send_data('Invalid Command', 'ERRO', midsock)

def db_protocol(middlesock):
    comm = DSComm(middlesock)
    print('DB Protocol')
    while True:
        print('\tListening for message')
        mess = comm.recvMessage()
        if mess:
            tipe = mess.getType()
            data = mess.getData().decode('utf-8')
            print('Command:', tipe, '\t', 'Data: ', data)  
            decode_cmd(tipe, data, middlesock)

if __name__ == '__main__':
    '''Assume TCP Connections'''
    mainserv = socket.socket()
    mainserv.bind(("localhost", middleware))
    mainserv.listen(5)
    while True:
        print('Listening on ', middleware)
        middlesock, raddr = mainserv.accept()
        db_protocol(middlesock)
        middlesock.close()
    mainserv.close()