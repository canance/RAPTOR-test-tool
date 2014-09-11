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
SOCKETSIZE = 1024


class RaptorConnection(Thread):
    def __init__(self, conn, caddress, path):
        self.conn = conn
        self.caddress = caddress
        self.path = path
        super(RaptorConnection, self).__init__()

    def run(self):
        try:
            print >> sys.stderr, 'connection from', self.caddress
            data = self.conn.recv(SOCKETSIZE)
            if data:
                print >> sys.stderr, "%s: %s" % (self.caddress[0], data)
                self.handledata(data)
        finally:
            # Clean up the connection
            self.conn.close()


    def handledata(self, data):
        """
        Handles incoming data from a thread's connection
        :param data: string of data
        :return:
        """
        data = data.strip().lower()
        if not data:
            return
        if data == 'directory':
            self.directory()
        elif data == 'ping':
            self.pong()
        else:
            self.filename(data)


    def filename(self, data):
        """
        Handles the case that RAPTOR requests a filename/assignment
        :param data: string representing the filename
        :return:
        """
        fpath = "%s/%s" % (self.path, data.lower())
        if not os.path.isdir(fpath):
            self.conn.sendall("INVALID COMMAND OR ASSIGNMENT\r\n")
            return
        # valid test folder
        self.conn.sendall('%d\r\n' % RaptorConnection.countdirs(fpath))

        for dir in RaptorConnection.getdirs(fpath):
            self.handletest(dir)


    def handletest(self, dir):
        """
        Handles giving the tests associated with an assignment.
        :param dir: string representing the directory of the assignment
        :return:
        """
        name = os.path.split(dir)[1]
        #send test data from in.txt
        with open(dir + '/in.txt', 'r') as f:
            data = f.readlines()
            for line in data:
                self.conn.sendall(line.replace('\n', '\r\n'))
            self.conn.sendall('EOF\r\n')

        data = ''
        resp = []
        done = False
        #recieve test data response until EOF is reached
        while not done:
            data = self.conn.recv(SOCKETSIZE)
            for s in data.split('\r\n'):
                if s.lower() == 'eof':
                    done = True
                    break
                if s.strip():
                    resp.append(s.strip())

        #compare RAPTOR response with out.txt
        correct = True
        with open(dir + '/out.txt', 'r') as f:
            data = f.readline()
            i = 0
            for line in data:
                if not line.strip():
                    continue
                try:
                    if line != resp[i]:
                        correct = False
                except:
                    correct = False
                i += 1
        correct = "CORRECT" if correct else "INCORRECT"
        self.conn.sendall(correct + '\r\n')

    @staticmethod
    def countdirs(path):
        """
        Count's the number of directories in a path.  Excludes files and '.' files/dirs
        :param path: string representing the directory to count from
        :return: count
        """
        files = os.listdir(path)
        count = 0
        for f in files:
            if f[:1] == '.':
                continue
            if not os.path.isdir(path + '/' + f):
                continue
            count += 1
        return count

    @staticmethod
    def getdirs(path):
        """
        Creates a list of subdirectories in a path
        :param path: string representing directory to list from
        :return: list of subdirecories
        """
        ret = []
        files = os.listdir(path)
        for f in files:
            if f[:1] == '.':
                continue
            if not os.path.isdir(path + '/' + f):
                continue
            ret.append(path + '/' + f)
        return ret

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
    #setup arg parser
    parser = argparse.ArgumentParser(description="A test server for RAPTOR.")
    parser.add_argument('-p', '--path', metavar='folderpath', type=str, help='Path to RAPTOR assignments directory.')
    parser.add_argument('--port', metavar='port', type=int, help='Port number to host server from.  By default the port is 10000.')

    print >> sys.stderr, "-->To quit press ctrl-c"
    args = parser.parse_args()

    path = args.path
    port = args.port

    if not port:
        port = 10000

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
    server_address = (HOST, port)
    print >> sys.stderr, 'starting up on %s port %s' % server_address
    sock.bind(server_address)

    # Listen for incoming connections
    sock.listen(5)

    try:
        while True:
            # Wait for a connection
            connection, client_address = sock.accept()
            #create and start a new thread to handle the connection
            rc = RaptorConnection(connection, client_address, path)
            rc.start()
    except KeyboardInterrupt:
        pass
    finally:
        sock.close()


if __name__ == '__main__':
    main()

