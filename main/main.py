'''
Created on Feb 17, 2023

@author: Joey Salazar
'''

import socket
import hashlib 
import time
from DSMessage import DSMessage
from DSComm import DSComm

current_user_hash = ''
signed_in = False

client = 50000
storage = 51000

def hash_string(string_to_hash):
    hash_obj = hashlib.sha256(string_to_hash.encode())
    hex_string = hash_obj.hexdigest()
    return hex_string[:4]

def send_data(data, type, sock):
    mess = DSMessage()
    print('Type Before Set: ', type)
    mess.setType(type)
    mess.setData(data.encode('utf-8'))
    print('Typer After Set: ', mess.getType())
    comm = DSComm(sock)
    comm.sendMessage(mess)

def receive_data(dbsock):
    comm = DSComm(dbsock)
    while True:
        mess = comm.recvMessage()
        if mess:
            tipe = mess.getType()
            data = mess.getData().decode('utf-8')
            print(tipe,':',data)
            if tipe == 'OKOK' or tipe == 'ERRO':
                print()
                return tipe, data

def sign_in_success(credentials, clisock, dbsock):
    print('Login Success!')
    global current_user_hash
    current_user_hash = hash_string(credentials)
    global signed_in
    signed_in = True
    print('Hash: ', current_user_hash)
    '''Set Globals so that program knows someone is signed in'''
    send_data('Successful Login\nType \'MENU\' to display commands', 'OKOK', clisock)
    '''Send status to client'''
    '''Return to main protocol'''
    return

def login(data, clisock, dbsock):
    #print('Entered Login Protocol: ' + data)
    with open('userdb.txt', 'r') as file:
        for line in file:
            if data == line.rstrip():
                sign_in_success(data, clisock, dbsock)
                return
        send_data('Error Signing In', 'ERRO', clisock)
    

def logout(data, clisock, dbsock):
    try:
        global current_user_hash
        current_user_hash = ''
        global signed_in
        signed_in = False
        send_data('Successful Logout', 'OKOK', clisock)
        #Or break connection
    except:
        send_data('Error Logging Out', 'ERRO', clisock)
    return

def menu(data, clisock, dbsock):
    with open('menu.txt', 'r') as file:
        contents = file.read()
        send_data(contents, 'OKOK' ,clisock)
    return
        

def stor_file(data, clisock, dbsock):
    '''
        Data contains 'fname:filecontents'
    '''
#try:
#Split string into two parts, extract only the filename
    parts = data.split(':')
    dpath = parts[0]
    dcontents = parts[1]
    #if a full path was passed, we only need the name
    if '/' in dpath:
        pathparts = parts[0].split('/')
        dname = pathparts[-1]
    #if only the name was passed
    else:
        dname = parts[0]

    global current_user_hash
    #reconstruct data to send to dbserver
    newdata = current_user_hash + dname + ':' + dcontents
    send_data(newdata, 'STOR', dbsock)
    status, message = receive_data(dbsock)
    print('From DB\n\tStatus: ', status, '\t', 'Message: ', message)
    #Need to check if overwriting
    if status == 'OKOK':                    #--------------> DATA or OKOK?
        with open('userdb.txt','a') as file:
            file.write('\n' + current_user_hash + dname)
            send_data('Stored File!', 'OKOK', clisock)  
    else:
        send_data('Couldn\'t store','ERRO',clisock )
        
#except:
    #send_data('Couldn\'t communicate with dbserver', 'ERRO', clisock)

def retr_file(fname,  clisock, dbsock):
    '''
        1.)Send command to storage server along with filename
        2.)Receive data and status back
        .) If responses OKOK
                send to client
            else
                send client erro
    '''
    global current_user_hash
    name = current_user_hash + fname
    with open('userdb.txt','r') as file:
        for line in file:
            if line[4:] == fname and line[:4] == current_user_hash:
                try:
                    send_data(name, 'RETR', dbsock)
                    status, data = receive_data(dbsock)
                    if status == 'OKOK':            
                        send_data(data, 'DATA', clisock)
                        return
                    else:
                        send_data('Couldn\'t retreive file contents','ERRO',clisock )
                        return

                except:
                    send_data('Couldn\'t retreive file contents','ERRO',clisock )
                    return
           
        send_data('Couldn\'t find file','ERRO',clisock )

def dele_file(fname, clisock, dbsock):
    global current_user_hash
    name = current_user_hash + fname
    with open('userdb.txt', 'r+') as file:
        lines = file.readlines()
        file.seek(0)  # move the file pointer back to the beginning
        found_file = False
        for line in lines:
            if line[:4] == current_user_hash and line[4:].rstrip() == fname:
                try:
                    send_data(name, 'DELE', dbsock)
                    status, data = receive_data(dbsock)
                    if status == 'OKOK':
                        lines.remove(line)  # remove the line from the list
                        file.write(''.join(lines))  # write the updated list back to the file
                        file.truncate()  # truncate the remaining content
                        found_file = True
                        send_data('Successful Delete', 'OKOK', clisock)
                    else:
                        send_data('Couldn\'t delete file contents', 'ERRO', clisock)
                    break
                except:
                    send_data('Delete Exception', 'ERRO', clisock)
                    break
        
        if not found_file:
            send_data('File doesn\'t exist', 'ERRO', clisock)

def list_files(data, clisock, dbsock):
    files = ''
    with open('userdb.txt','r') as file:
        for line in file:
            if current_user_hash in line:
                files += line[4:] + '\n'
    if files == '':
        send_data('No files found/exist', 'ERRO', clisock)
    else:
        send_data(files, 'OKOK', clisock)


def data_in(data):
    pass

def okok_in(data):
    pass

def erro_in(data):
    pass



def decode_command(line, data, clisock, dbsock = None):
    if signed_in == False:
        if line != 'LGIN':
            send_data('Use \'LGIN\' to login first!','ERRO',clisock )
        else:
            login(data, clisock, dbsock)
    else:    
        if line == 'LGOT':
            logout(data, clisock, dbsock)
        elif line == 'MENU':
            menu(data, clisock, dbsock)
        elif line == 'STOR':
            stor_file(data, clisock, dbsock)
        elif line == 'RETR':
            retr_file(data, clisock, dbsock)
        elif line == 'DELE':
            dele_file(data, clisock, dbsock)
        elif line == 'LIST':
            list_files(data, clisock, dbsock)
        else:
            send_data('Cant Decode','ERRO',clisock )
    return
        
def main_protocol(clientsock, dbsock):
    comm = DSComm(clientsock)
    while True:
        print()
        print('Main Protocol')
        print('\tSigned in: ',signed_in)
        mess = comm.recvMessage()
        if mess:
            tipe = mess.getType()
            data = mess.getData().decode('utf-8')
            print('\t','CMD: ',tipe)
            print('\t', 'DATA: ', data, '\n')
            decode_command(tipe,data, clientsock, dbsock)


if __name__ == '__main__':
    #Connect to DBserver
    dbserv = socket.socket()
    dbserv.connect(('localhost', storage))
    #Allow for Client Connection
    clientserv = socket.socket()
    clientserv.bind(("localhost", client))
    clientserv.listen(5)
    while True:
        print('Listening on ', client)
        clientsock, raddr = clientserv.accept()
        main_protocol(clientsock, dbserv)
        clientsock.close()
    clientserv.close()
    dbserv.close()



    



        
    
