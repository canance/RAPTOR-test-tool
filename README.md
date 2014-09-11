RAPTOR_Test_Tool
================

Python implementation of a test server for RAPTOR programming.

Requires python 2.7

usage: server.py [-h] [-p folderpath] [--port port]

A test server for RAPTOR.

optional arguments:
  -h, --help            show this help message and exit
  -p folderpath, --path folderpath
                        Path to RAPTOR assignments directory.
  --port port           Port number to host server from. By default the port
                        is 10000.
                        

The assignment directory contains subdirectories for each assignment.  In each assignment directory
there can be multiple test directories.  Each test directory must contain an 'in.txt' file and an 'out.txt' file.
Each line of the 'in.txt' represents an input in RAPTOR; and each line of the 'out.txt' file represents an output in RAPTOR.

*NOTE: RAPTOR requires that a client's filename be the same as the assignment name.  For example:
        Assignment:  lab1
        RAPTOR file: lab1.rap
        
For an example try using the tests directory for your path and run it against a simple RAPTOR flowchart 
consisting of 2 inputs and print the sum.

Example:
python server.py --path tests/
