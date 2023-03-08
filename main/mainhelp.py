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
            #s.settimeout(2)  # Set a timeout for the connection attempt
            s.connect(server)
            online_servers['ds'+str(i)] = s
            print(f"Connected to server {server[0]}:{server[1]}")
        except:
            print(f"Unable to connect to server {server[0]}:{server[1]}")
            online_servers['ds'+str(i)] = None
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

def split_bfile_half(bfile):
    part_len = math.ceil(len(bfile) / 2)
    parts = [bfile[i:i+part_len] for i in range(0, len(bfile), part_len)]
    # Pad the last part with zeros if necessary
    last_part_len = len(parts[-1])
    if last_part_len < part_len:
        parts[-1] = parts[-1] + '0'*(part_len - last_part_len)
    return parts[0], parts[1]

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
    main.send_data((fname+A+B).encode('utf-8'), 'STOR', ds1)
    stat1, d1 = main.receive_data(ds1)

    main.send_data((fname+C+D).encode('utf-8'), 'STOR', ds2)
    stat2, d2 = main.receive_data(ds2)

    main.send_data((fname+XOR_parts(A,C) + XOR_parts(B, D)).encode('utf-8'), 'STOR', ds3)
    stat3, d3 = main.receive_data(ds3)

    main.send_data((fname+XOR_parts(A, B, D) + XOR_parts(B, C)).encode('utf-8'), 'STOR', ds4)
    stat4, d4 = main.receive_data(ds4)

    if stat1 == 'OKOK' and stat2 == 'OKOK' and stat3 == 'OKOK' and stat4 == 'OKOK':
        return 'OKOK'
    else:
        return 'ERRO'
    
def dele_all_four(fname, ds1, ds2, ds3, ds4):
    main.send_data(fname, 'DELE', ds1)
    stat1, d1 = main.receive_data(ds1)

    main.send_data(fname, 'DELE', ds2)
    stat2, d2 = main.receive_data(ds2)

    main.send_data(fname, 'DELE', ds3)
    stat3, d3 = main.receive_data(ds3)

    main.send_data(fname, 'DELE', ds4)
    stat4, d4 = main.receive_data(ds4)

    if stat1 == 'OKOK' and stat2 == 'OKOK' and stat3 == 'OKOK' and stat4 == 'OKOK':
        return 'OKOK'
    else:
        return 'ERRO'
    
def retr_protocol(fname, ds1, ds2, ds3, ds4):
    #ds3 and ds4 online
    stat1 = 'ERRO'
    stat2 = 'ERRO'
    data = None
    try:
        if ds1 == None and ds2 == None:
            main.send_data(fname, 'RETR', ds3)
            stat1, d1 = main.receive_data(ds3)
            main.send_data(fname, 'RETR', ds4)
            stat2, d2 = main.receive_data(ds4)
            AC, BD = split_bfile_half(d1)
            ABD, BC = split_bfile_half(d2)
            A = XOR_parts(ABD, BD) 
            C = XOR_parts(A, AC)
            B = XOR_parts(BC, C)
            D = XOR_parts(ABD, A, B)
            data = A + B + C + D
            pass
        #ds2 and ds4 online
        elif ds1 == None and ds3 == None:
            main.send_data(fname, 'RETR', ds2)
            stat1, d1 = main.receive_data(ds2)
            main.send_data(fname, 'RETR', ds4)
            stat2, d2 = main.receive_data(ds4)
            C, D = split_bfile_half(d1)
            ABD, BC = split_bfile_half(d2)
            data = XOR_parts(ABD, D, XOR_parts(BC, C)) + XOR_parts(BC, C) + C + D
            pass
        #ds2 and ds3 online
        elif ds1 == None and ds4 == None:
            main.send_data(fname, 'RETR', ds2)
            stat1, d1 = main.receive_data(ds2)
            main.send_data(fname, 'RETR', ds3)
            stat2, d2 = main.receive_data(ds3)
            C, D = split_bfile_half(d1)
            AC, BD = split_bfile_half(d2)
            data = XOR_parts(AC, C) + XOR_parts(BD, D) + C + D
            pass
        #ds1 and ds4 online
        elif ds2 == None and ds3 == None:
            main.send_data(fname, 'RETR', ds1)
            stat1, d1 = main.receive_data(ds1)
            main.send_data(fname, 'RETR', ds4)
            stat2, d2 = main.receive_data(ds4)
            A, B = split_bfile_half(d1)
            ABD, BC = split_bfile_half(d2)
            data = A + B + XOR_parts(B, BC) + XOR_parts(A, B, ABD)
            pass
        #ds1 and ds3 online
        elif ds2 == None and ds4 == None:
            main.send_data(fname, 'RETR', ds1)
            stat1, d1 = main.receive_data(ds1)
            main.send_data(fname, 'RETR', ds3)
            stat2, d2 = main.receive_data(ds3)
            A, B = split_bfile_half(d1)
            AC, BD = split_bfile_half(d2)
            data = A + B + XOR_parts(A, AC) + XOR_parts(B, BD)
            pass
        #ds1 and ds2 online
        else:
            main.send_data(fname, 'RETR', ds1)
            stat1, d1 = main.receive_data(ds1)
            main.send_data(fname, 'RETR', ds2)
            stat2, d2 = main.receive_data(ds2)
            A, B = split_bfile_half(d1)
            C, D = split_bfile_half(d2)
            data = A + B + C + D
            pass
    except Exception as e:
        print(e)

    if stat1 == 'OKOK' and stat2 == 'OKOK':
        return 'OKOK', data
    else:
        return 'ERRO', data
    
