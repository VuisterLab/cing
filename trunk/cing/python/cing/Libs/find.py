"""
Taken from O'Reilly book

Execute like (counting CING's code base lines; 110k+)
wc `python $CINGROOT/python/cing/Libs/find.py '*.py' $CINGROOT`
"""

import fnmatch
import os
import sys

def find2(pattern, startdir=os.curdir):
    "Renamed to distinguish from string's find and pylab's find"
    matches = []
    os.path.walk(startdir, findvisitor, (matches, pattern))
    matches.sort()
    return matches

def findvisitor((matches, pattern), thisdir, nameshere):
    for name in nameshere:
        if fnmatch.fnmatch(name, pattern):
            fullpath = os.path.join(thisdir, name)
            matches.append(fullpath)

if __name__ == '__main__':
    namepattern, startdir = sys.argv[1], sys.argv[2]
    for name in find2(namepattern, startdir):
        print name