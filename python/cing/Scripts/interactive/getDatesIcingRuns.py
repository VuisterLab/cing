'''
Created on Sep 8, 2010
This script can generate the input data for:
$CINGROOT/Documentation/usage/perMonthRuns.numbers

# on server as root
python $C/python/cing/Scripts/interactive/getDatesIcingRuns.py > t.txt
# on client
scp -P 39676 localhost-nmr:/Users/jd/t.txt .
# in Numbers
# drag into empty table from Finder and adjust the definitions in histogram table
# and histogram graph.
# Note that the file names shouldn't be entered into public domain as they are secret;-)
@author: jd
'''

from glob import glob
import os
import time

os.chdir('/Library/WebServer/Documents/tmp/cing/ano')

fileList = glob('*')
for file in fileList:
#    file = fileList[0]
    fMtime = os.path.getmtime(file) # Gives float of seconds since epoch .
    tt = timetuple = time.localtime(fMtime)
    #dt = datetime.datetime(tt.tm_year, tt.tm_mon, tt.tm_mday)
#    print '%04d-%02d-%02d,%s' % (tt.tm_year, tt.tm_mon, tt.tm_mday, file) # insist on CSV!
    print '%04d-%02d-%02d' % (tt.tm_year, tt.tm_mon, tt.tm_mday)
