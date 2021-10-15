#! /usr/bin/python3


import socket
import sys

import threading



def recv_main(recv_sock):
    # this is used to hold data which has been read from the socket, but not
    # interpteted into packet yet.
    pending = b""

    while True:
        # we get here when we're at the start of a new packet.  But we have
        # to scan the pending buffer first; maybe we've already some or all
        # of this packet, in a previous recv().  So we count forward,
        # through pending, until we find a newline (which is byte 10).  If
        # we ever run past the end of the pending array (maybe at the
        # beginning of this search, maybe later), we'll recv() to get more.

        len_len = 0
        while len_len == len(pending) or pending[len_len] != 10:   # 10 == ord('\n')
            if len_len == len(pending):
                more = recv_sock.recv(1024)
                if len(more) == 0:
                    return
                pending += more
            len_len += 1

        len_buf = pending[:len_len]
        pending = pending[len_len+1:]

        len_int = int(len_buf.decode())

        while len(pending) < len_int:
            more = recv(len_int-len(pending))
            if len(more) == 0:
                return
            pending += more
            assert len(pending) <= len_int

        msg     = pending[:len_int ].decode()
        pending = pending[ len_int:]

        print(f"MESSAGE RECEIVED: {msg}")
        


def main():
    conn_addr = sys.argv[1]
    conn_port = int(sys.argv[2])

    conn_sock = socket.socket()
    conn_sock.connect( (conn_addr,conn_port) )

    print("CONNECTED!")

    threading.Thread( target=recv_main, args=(conn_sock,) ).start()

    while True:
        try:
            buf = input()
        except EOFError:
            print("----- Input terminated, client will now close -----")
            conn_sock.shutdown(socket.SHUT_RDWR)
            break

        print(f"SENDING MESSAGE: {buf}")

        packet = f"{len(buf)}\n{buf}".encode()
        conn_sock.sendall(packet)

main()

