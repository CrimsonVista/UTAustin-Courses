import os
import select
import socket
import sys

def console(sock):
    stdin2sock = b''
    sock2stdout = b''

    sys.stdout.flush()
    sys.stderr.flush()

    rlist = [sys.stdin, sock]
    input_closed = False
    while True:
        wlist = []
        if stdin2sock:
            wlist.append(sock)
        elif input_closed:
            sock.shutdown(socket.SHUT_WR)
            input_closed = False
        if sock2stdout:
            wlist.append(sys.stdout)
        rs, ws, xs = select.select(rlist, wlist, [])
        if sys.stdin in rs:
            data = os.read(sys.stdin.fileno(), 4096)
            if data:
                stdin2sock += data
            else:
                rlist.remove(sys.stdin)
                input_closed = True
        if sock in rs:
            data = sock.recv(4096)
            if data:
                sock2stdout += data
            else:
                return
        if sys.stdout in ws:
            amount = os.write(sys.stdout.fileno(), sock2stdout)
            if amount:
                sock2stdout = sock2stdout[amount:]
            else:
                return
        if sock in ws:
            amount = sock.send(stdin2sock)
            if amount:
                stdin2sock = stdin2sock[amount:]
            else:
                rlist.remove(sys.stdin)
                stdin2sock = b''
