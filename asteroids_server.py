#! /usr/bin/python3


import socket
import sys

import threading



def worker_main(recv_sock, lock, return_socks_arr):
    # call a function which we can return out of, conveniently.  We'll do
    # thread-level cleanup when it returns
    worker_body(recv_sock, lock, return_socks_arr)

    lock.acquire()
    return_socks_arr.remove(recv_sock)
    lock.release()

    recv_sock.shutdown(socket.SHUT_RDWR)



def worker_body(recv_sock, lock, return_socks_arr):
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

        msg     = pending[:len_int ]
        pending = pending[ len_int:]

        print(f"MESSAGE RECEIVED FROM CLIENT fileno={recv_sock.fileno()} : {msg}")

        msg = len_buf + b"\n" + msg

        lock.acquire()
        for send_sock in return_socks_arr:
            if send_sock != recv_sock:
                send_sock.sendall(msg)
        lock.release()
        


def main():
    listen_port = int(sys.argv[1])

    server_sock = socket.socket()
    server_sock.bind( ("0.0.0.0",listen_port) )
    server_sock.listen(5)

    lock = threading.Lock()
    return_socks = []

    while True:
        (conn_sock,conn_addr) = server_sock.accept()

        lock.acquire()
        return_socks.append(conn_sock)
        lock.release()

        threading.Thread( target=worker_main, args=(conn_sock, lock, return_socks) ).start()

main()

