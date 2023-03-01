'''
Created on Feb 23, 2023

@author: nigel
'''

import socket
import os
from DSComm import DSComm
from DSStoreProtocol import DSStoreProtocol
from DSServerOps import DSServerOps


if __name__ == '__main__':
    
    # create the server socket
    #  defaults family=AF_INET, type=SOCK_STREAM, proto=0, filno=None
    serversoc = socket.socket()
    
    # bind to local host:5000
    serversoc.bind(("localhost",50000))
                   
    # make passive with backlog=5
    serversoc.listen(5)
    
    # wait for incoming connections
    while True:
        print("Listening on ", 50000)
        
        # accept the connection
        commsoc, raddr = serversoc.accept()
        
        # run the application protocol
        comm = DSComm(commsoc)
        proto = DSStoreProtocol(comm)
        sops = DSServerOps(proto)
        sops.run() # storage path is in DSStoreProtocol
    
    # close the server socket
    serversoc.close()
