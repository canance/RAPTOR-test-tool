"""
RAPTOR TEST SERVER

Author: Cory Nance
Date:   9 September 2014

An implementation of a RAPTOR test server.  Specifications can be found here:
http://raptor.martincarlisle.com/Implementing%20a%20RAPTOR%20test%20server.doc.
"""

import socket
import sys
import argparse
import os

from threading import Thread

HOST = ''
PORT = 10001
SOCKETSIZE = 1024

class RaptorConnection(Thread):

    def __init__(self, conn, caddress, path):
        self.conn = conn
        self.caddress = caddress
        self.path = path
        super(RaptorConnection, self).__init__()

    def run(self):
        try:
            print >>sys.stderr, 'connection from', self.caddress
            while True:
                data = self.conn.recv(SOCKETSIZE)
                if data:
                    print "%s: %s" % (self.caddress[0], data)
                    self.handledata(data)
        finally:
            # Clean up the connection
            self.conn.close()


    def handledata(self, data):
        data = data.strip().lower()
        #switch(data)
        if not data:
            return
        if data == 'directory':
            self.directory()
        elif data == 'ping':
            self.pong()
        else:
            self.filename(data)


    def filename(self, data):
        fpath = "%s/%s" % (self.path, data)
        if not os.path.isdir(fpath):
            self.conn.sendall("INVALID COMMAND OR ASSIGNMENT\r\n")
            return


    def directory(self):
        files = os.listdir(self.path)



        for f in files:
            if f[:1] == '.':
                continue
            if not os.path.isdir(self.path + '/' + f):
                continue
            self.conn.sendall(f + "\r\n")
        self.conn.sendall("EOF\r\n")

    def pong(self):
        self.conn.sendall('PONG!\r\n')

def main():
    parser = argparse.ArgumentParser(description="Compile, test, and grade Java files submitted via Moodle.")
    parser.add_argument('-p', '--path', metavar='FolderPath', type=str, help='Path to RAPTOR test directories.')
    args = parser.parse_args()

    path = args.path

    while not path:
        print "Please enter the path to the RAPTOR test directory.  Press enter to use the current directory."
        path = raw_input("directory [%s]: " % os.path.abspath(os.curdir))
        if not path:
            os.curdir
        if not os.path.isdir(path):
            path = False

    path = os.path.abspath(path)

    # Create a TCP/IP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Bind the socket to the port
    server_address = (HOST, PORT)
    print >>sys.stderr, 'starting up on %s port %s' % server_address
    sock.bind(server_address)

    # Listen for incoming connections
    sock.listen(5)

    try:
        while True:
            # Wait for a connection
            print >>sys.stderr, 'waiting for a connection'
            connection, client_address = sock.accept()
            rc = RaptorConnection(connection, client_address, path)
            rc.start()
    except KeyboardInterrupt:
        pass
    finally:
        sock.close()



if __name__ == '__main__':
    main()

