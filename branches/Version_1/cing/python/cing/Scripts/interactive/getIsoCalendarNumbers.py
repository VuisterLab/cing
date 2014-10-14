# python -u $CINGROOT/python/cing/Scripts/interactive/mouseBuffer3.py

from datetime import datetime
from numpy import * #@UnusedWildImport
dt = datetime.now()
print datetime.isocalendar(dt)

# Below is for a memory test which can show that python doesn't like to do over 2 G in any one chunk but can go higher with multiple chunks.
# a floating point in python is iimplemented as a C double
# on 32 bit executable this is 64 bits per double; 8 bytes
a = ones( (1024,1024,10) ) * 1.1
aSizeInMb = a.size * 8 / ( 1024 * 1024 )
print aSizeInMb
v = ones( (1024,1024,10) ) * 1.1
del( a ) # instant release.