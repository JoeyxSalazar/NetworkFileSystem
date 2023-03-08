'''
Created on Feb 17, 2023

@author: Joey Salazar
'''

import socket
import hashlib 
import time
import mainhelp
from DSMessage import DSMessage
from DSComm import DSComm

current_user_hash = ''
signed_in = False

client = 50000
ds1 = 51000
ds2 = 51001
ds3 = 51002
ds4 = 51003

def hash_string(string_to_hash):
    hash_obj = hashlib.sha256(string_to_hash.encode())
    hex_string = hash_obj.hexdigest()
    return hex_string[:4]

def send_data(data, type, sock):
    mess = DSMessage()
    print('Type Before Set: ', type)
    mess.setType(type)
    if isinstance(data, bytes) == False:
        mess.setData(data.encode('utf-8'))
    else:
        mess.setData(data)
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

def sign_in_success(credentials, clisock):
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

def login(data, clisock):
    #print('Entered Login Protocol: ' + data)
    with open('userdb.txt', 'r') as file:
        for line in file:
            if data == line.rstrip():
                sign_in_success(data, clisock)
                return
        send_data('Error Signing In', 'ERRO', clisock)
    

def logout(data, clisock):
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

def menu(data, clisock):
    with open('menu.txt', 'r') as file:
        contents = file.read()
        send_data(contents, 'OKOK' ,clisock)
    return
        

def stor_file(data, clisock, ds1, ds2, ds3, ds4):
    '''
        Data contains 'fname:filecontents'
    '''
    #Extract data name, and data contents
    dname, dcontents = mainhelp.split_file_path(data)
    #Extract 4 equal parts from the content:
    A, B, C, D = mainhelp.split_file_into_four(dcontents)
    #Need to send parts to all 4 servers now, if all 4 accept, then continue
    global current_user_hash
    fname = current_user_hash + dname + ':'
    status = mainhelp.store_all_four(fname, A, B, C, D, ds1, ds2, ds3, ds4)
    #Need to check if overwriting
    if status == 'OKOK':                   
        with open('userdb.txt','a+') as file:
            file.seek(0)
            for line in file:
                print(line.strip())
                if line.strip() == (current_user_hash + dname):
                    send_data('Overwrote File!', 'OKOK', clisock)
                    return
            file.write('\n' + current_user_hash + dname)
            send_data('Stored File!', 'OKOK', clisock)  
    else:
        send_data('Couldn\'t store','ERRO',clisock )
        
    #except:
        #send_data('Couldn\'t communicate with dbserver', 'ERRO', clisock)

def retr_file(fname,  clisock, ds1 = None, ds2 = None, ds3 = None, ds4 = None):
    global current_user_hash
    name = current_user_hash + fname
    with open('userdb.txt','r') as file:
        for line in file:
            if line[4:] == fname and line[:4] == current_user_hash:
                try:
                    status, data = mainhelp.retr_protocol(name, ds1, ds2, ds3, ds4)
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

def dele_file(fname, clisock, ds1, ds2, ds3, ds4):
    global current_user_hash
    name = current_user_hash + fname
    with open('userdb.txt', 'r+') as file:
        lines = file.readlines()
        file.seek(0)  # move the file pointer back to the beginning
        found_file = False
        for line in lines:
            if line[:4] == current_user_hash and line[4:].rstrip() == fname:
                try:
                    status = mainhelp.dele_all_four(name, ds1, ds2, ds3, ds4)
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

def list_files(data, clisock):
    files = ''
    with open('userdb.txt','r') as file:
        for line in file:
            if current_user_hash in line:
                files += line[4:]
    if files == '':
        send_data('No files found/exist', 'ERRO', clisock)
    else:
        send_data(files, 'OKOK', clisock)

def decode_command(line, data, clisock, ds1, ds2, ds3, ds4):
    if signed_in == False:
        if line != 'LGIN':
            send_data('Use \'LGIN\' to login first!','ERRO',clisock )
        else:
            login(data, clisock)
    else:    
        if line == 'LGOT':
            logout(data, clisock)
        elif line == 'MENU':
            menu(data, clisock)
        elif line == 'STOR':
            stor_file(data, clisock, ds1, ds2, ds3, ds4)
        elif line == 'RETR':
            retr_file(data, clisock, ds1, ds2, ds3, ds4)
        elif line == 'DELE':
            dele_file(data, clisock, ds1, ds2, ds3, ds4)
        elif line == 'LIST':
            list_files(data, clisock)
        else:
            send_data('Cant Decode','ERRO',clisock )
    return
        
def main_protocol(clientsock, ds1 = None, ds2 = None, ds3= None, ds4 = None):
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
            decode_command(tipe, data, clientsock, ds1, ds2, ds3, ds4)


if __name__ == '__main__':
    #Connect to DSservers
    servers = [("localhost", 51000), ("localhost", 51001),("localhost", 51002),("localhost", 51003),]
    onl_servers = mainhelp.ConnectionProtocol(servers)
    '''
    #Connect to DBserver
    dbserv = socket.socket()
    dbserv.connect(('localhost', ds1))
    '''
    
    #Allow for Client Connection
    clientserv = socket.socket()
    clientserv.bind(("localhost", client))
    clientserv.listen(5)
    while True:
        print('Listening on ', client)
        clientsock, raddr = clientserv.accept()
        main_protocol(clientsock, onl_servers['ds1'], onl_servers['ds2'], onl_servers['ds3'], onl_servers['ds4'])
        clientsock.close()
    clientserv.close()
    for s in onl_servers.values():
        s.close()


    



        
    
