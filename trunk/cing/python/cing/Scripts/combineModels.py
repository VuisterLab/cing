#!/usr/bin/env python
__author__     = 'Charles Schwieters'

from sys import argv, stdout

files = argv[1:]

model=1
for f in files:
    print "MODEL %8d" % model
    stdout.write(open(f).read())
    print "ENDMDL"
    model += 1
# end for