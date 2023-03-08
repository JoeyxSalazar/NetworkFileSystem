'''
Created on Feb 17, 2023

@author: Joey Salazar
'''

import socket
import time
import os
from DSMessage import DSMessage
from DSComm import DSComm

middleware = 51002

def check_if_overwrite(fname):
    return os.path.exists('AC/' + fname)

def overwrite(fname, cont1, cont2):
    file = open('AC/' + fname, 'a')
    file.seek(0)
    file.truncate()
    file.write(cont1)
    file.close()

    file1 = open('BD/' + fname, 'a')
    file1.seek(0)
    file1.truncate()
    file1.write(cont2)
    file1.close()

def write_file(fname, cont1, cont2):
    with open('AC/' + fname, 'w') as file:
        file.write(cont1)
    with open('BD/' + fname, 'w') as file1:
        file1.write(cont2)

def read_file(name):
    with open('storage/'+name, 'r') as file:
        cont = file.read()
    return cont

# 'filename:file_contents'
# assume string is decoded already
def decode_file_contents(string):
    filename, file_content = string.split(":")
    size_of_content = len(file_content)
    mid = len(file_content)//2
    return filename, size_of_content, file_content[:mid], file_content[mid:]
    #filename = filename.strip("'")
    #file_content = file_content.strip("'")

def send_data(data, type, sock):
    mess = DSMessage()
    mess.setType(type)
    mess.setData(data.encode('utf-8'))
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
    except:
        send_data('File contents not formatted correctly', 'ERRO', midsock)


def retr_file(fname, midsock):
    try:
        send_data(read_file(fname), 'OKOK', midsock)
    except:
        send_data('Error Retrieving', 'ERRO', midsock)
    #Fill protocol here

def dele_file(fname, midsock):
    try:
        file_path = 'AC/' + fname
        file_path1 = 'BD/' + fname
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