import socket
import hashlib 
import time
import math
import main
from DSMessage import DSMessage
from DSComm import DSComm

def ConnectionProtocol(ds_servers):
    online_servers = {}
    i = 1
    for server in ds_servers:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(2)  # Set a timeout for the connection attempt
            s.connect(server)
            s.close()
            online_servers['ds'+str(i)] = s
            print(f"Connected to server {server[0]}:{server[1]}")
        except:
            print(f"Unable to connect to server {server[0]}:{server[1]}")
        i+=1

    # Check how many servers were successfully connected to
    if len(online_servers) == 4:
        print("Successfully connected to all 4 servers")
        return online_servers
    elif len(online_servers) == 2:
        print(f"Successfully connected to {len(online_servers)} servers: {online_servers}")
        return online_servers
    else:
        print("Unable to connect")

def split_file_into_four(file_string):
    part_len = math.ceil(len(file_string) / 4)
    parts = [file_string[i:i+part_len] for i in range(0, len(file_string), part_len)]
    # Pad the last part with zeros if necessary
    last_part_len = len(parts[-1])
    if last_part_len < part_len:
        parts[-1] = parts[-1] + '0'*(part_len - last_part_len)
    return parts[0], parts[1], parts[2], parts[3]

def split_file_path(data):
#Split string into two parts, extract only the filename
    parts = data.split(':')
    dpath = parts[0]
    dcontents = parts[1]
    #if a full path was passed, we only need the name
    if '/' in dpath:
        pathparts = parts[0].split('/')
        dname = pathparts[-1]
    else:
        dname = parts[0]
    return dname, dcontents

def XOR_parts(p1, p2, p3 = None):
    # Convert strings to binary
    p1b = bytes(p1, 'utf-8')
    p2b = bytes(p2, 'utf-8')
    p3b = bytes(p3, 'utf-8') if p3 else None
    # XOR binary strings
    result = bytearray()
    for i in range(len(p1b)):
        if p3b:
            result.append(p1b[i] ^ p2b[i] ^ p3b[i % len(p3b)])
        else:
            result.append(p1b[i] ^ p2b[i % len(p2b)])
    # Convert result back to string
    return result.decode('utf-8')

def store_all_four(fname, A, B, C, D, ds1, ds2, ds3, ds4):
    main.send_data(fname+A+B, 'STOR', ds1)
    stat1, d1 = main.receive_data(ds1)

    main.send_data(fname+C+D, 'STOR', ds2)
    stat2, d2 = main.receive_data(ds2)

    main.send_data(fname+XOR_parts(A,C) + XOR_parts(B, D), 'STOR', ds3)
    stat3, d3 = main.receive_data(ds3)

    main.send_data(fname+XOR_parts(A, B, D) + XOR_parts(B, C), 'STOR', ds4)
    stat4, d4 = main.receive_data(ds4)

    if stat1 == 'OKOK' and stat2 == 'OKOK' and stat3 == 'OKOK' and stat4 == 'OKOK':
        return 'OKOK'
    else:
        return 'ERRO'