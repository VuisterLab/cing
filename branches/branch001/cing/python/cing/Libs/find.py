"""
Taken from O'Reilly book
"""

__author__    = "$Author: jurgen $"
___revision__ = "$Revision: 1.1.1.1 $"
___date__     = "$Date: 2003/03/17 17:22:10 $"

"""
$Log: find.py,v $
Revision 1.1.1.1  2003/03/17 17:22:10  jurgen


Revision 1.2  2001/06/05 18:13:57  jurgen
Updated the cvs keywords in header.

"""

import fnmatch
import os
import sys

def find(pattern, startdir=os.curdir):
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
    for name in find(namepattern, startdir):
        print name