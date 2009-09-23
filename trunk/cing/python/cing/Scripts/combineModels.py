#!/usr/bin/env python
__author__     = 'Charles Schwieters'

from sys import argv, stdout

files = argv[1:]

model=1
for file in files:
    print "MODEL %8d" % model
    stdout.write(open(file).read())
    print "ENDMDL"
    model += 1
    pass
