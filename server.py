"""
RAPTOR TEST SERVER

Author: Cory Nance
Date:   9 September 2014

An implementation of a RAPTOR test server.  Specifications can be found here:
http://raptor.martincarlisle.com/Implementing%20a%20RAPTOR%20test%20server.doc.
"""

import socket
import sys

from threading import Thread

HOST = 'localhost'
PORT = 10000
SOCKETSIZE = 1024

class RaptorConnection(Thread):

    def __init__(self, conn, caddress):
        self.conn = conn
        self.caddress = caddress
        super(RaptorConnection, self).__init__()

    def run(self):
        try:
            print >>sys.stderr, 'connection from', self.caddress
            while True:
                data = self.conn.recv(SOCKETSIZE).strip().lower()
                print "%s: %s" % (self.caddress[0], data)

                #switch(data)
                if data == 'directory':
                    self.conn.sendall("file1\nfile2\nfile3\n")
                elif data == 'ping':
                    self.conn.sendall("pong!\n")
                else:
                    self.conn.sendall("RECV your msg\n")
        finally:
            # Clean up the connection
            self.conn.close()


def main():
    # Create a TCP/IP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Bind the socket to the port
    server_address = (HOST, PORT)
    print >>sys.stderr, 'starting up on %s port %s' % server_address
    sock.bind(server_address)

    # Listen for incoming connections
    sock.listen(1)

    try:
        while True:
            # Wait for a connection
            print >>sys.stderr, 'waiting for a connection'
            connection, client_address = sock.accept()
            rc = RaptorConnection(connection, client_address)
            rc.start()
    except KeyboardInterrupt:
        pass
    finally:
        sock.close()



if __name__ == '__main__':
    main()

