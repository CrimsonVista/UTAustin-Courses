#!/usr/bin/env python3

from struct import pack
from console import console

import socket
import sys
import time

if len(sys.argv) != 2:
    sys.exit("Usage: %s PORT" % sys.argv[0])

p = ("A"*29).encode('utf-8')

##
## Add your payload here.
##

port = int(sys.argv[1])
sock = socket.create_connection(('127.0.0.1', port),
                                socket.getdefaulttimeout(),
                                ('127.0.0.1', 0))
init = "A"*1023
sock.sendall(init.encode('utf-8'))
time.sleep(1)
sock.sendall(p)

console(sock)
