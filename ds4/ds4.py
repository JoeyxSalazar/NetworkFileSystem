'''
Created on Feb 17, 2023

@author: Joey Salazar
'''

import socket
import time
import os
from DSMessage import DSMessage
from DSComm import DSComm

middleware = 51003

def check_if_overwrite(fname):
    return os.path.exists('ABD/' + fname)

def overwrite(fname, cont1, cont2):
    file = open('ABD/' + fname, 'ab')
    file.seek(0)
    file.truncate()
    file.write(cont1)
    file.close()

    file1 = open('BC/' + fname, 'ab')
    file1.seek(0)
    file1.truncate()
    file1.write(cont2)
    file1.close()

def write_file(fname, cont1, cont2):
    with open('ABD/' + fname, 'wb') as file:
        file.write(cont1)
    with open('BC/' + fname, 'wb') as file1:
        file1.write(cont2)

def read_file(name):
    with open('ABD/'+ name, 'rb') as file:
        cont1 = file.read()
    with open('BC/'+ name, 'rb') as file:
        cont2 = file.read()
    return cont1 + cont2

# 'filename:file_contents'
# assume string is decoded already
def decode_file_contents(data):
    #string = data.decode('utf-8')
    filename, file_content = data.split(":",1)
    size_of_content = len(file_content)
    mid = len(file_content)//2
    return filename, size_of_content, file_content[:mid].encode('utf-8'), file_content[mid:].encode('utf-8')
    #filename = filename.strip("'")
    #file_content = file_content.strip("'")

def send_data(data, type, sock):
    mess = DSMessage()
    mess.setType(type)
    if isinstance(data, bytes) == False:
        mess.setData(data.encode('utf-8'))
    else:
        mess.setData(data)
    comm = DSComm(sock)
    comm.sendMessage(mess)


def stor_file(data, midsock):
    try:
        fname, size, content1, content2 = decode_file_contents(data)
        if check_if_overwrite(fname) == True:
            overwrite(fname, content1, content2)
            send_data('Existing file overwritten', 'OKOK', midsock)
        else:
            write_file(fname, content1, content2)
            send_data('File stored', 'OKOK', midsock)
    except Exception as E:
        send_data('Exception raised: ' + E, 'ERRO', midsock)


def retr_file(fname, midsock):
    try:
        send_data(read_file(fname), 'OKOK', midsock)
    except:
        send_data('Error Retrieving', 'ERRO', midsock)
    #Fill protocol here

def dele_file(fname, midsock):
    try:
        file_path = 'ABD/' + fname
        file_path1 = 'BC/' + fname
        if os.path.exists(file_path) and os.path.exists(file_path1):
            os.remove(file_path)
            os.remove(file_path1)
            send_data(fname +' deleted', 'OKOK', midsock)
    except:
        send_data('Error Deleting', 'ERRO', midsock)
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