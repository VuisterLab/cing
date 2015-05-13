#!/usr/bin/env python

"""
Execute like (or better still browse to it).
wget http://localhost/cgi-bin/cingRdbServer/tryPythonCgiScript.py
"""

import os
import platform
import sys
import time

# CGI header
print "Content-Type: text/plain\n\n"
print "Hello world by hard link\n"

user = os.getenv("USER", "Unknown user")
machine = os.getenv("HOST", "Unknown host") #only works with (t)csh shell
osType = '.'
ncpus = '.'
on = "%s (%s/%s/%scores/%s)" % (machine, osType, platform.architecture()[0], ncpus, sys.version.split()[0])
at = time.asctime()
pid = os.getpid()
at = '(%d) ' %  pid + at
#    atForFileName = "%s" % at
#    atForFileName = re.sub('[ :]', '_', atForFileName)
print "User: %-10s on: %-42s at: %32s\n" % (user, on, at)

pythonPathByApache = os.getenv("PYTHONPATH", "Unknown path")
print "pythonPathByApache:         %s" % (pythonPathByApache)

# The PATH is the most difficult to patch
# Use: http://stackoverflow.com/questions/6833939/path-environment-variable-for-apache2-on-mac
# .:/opt/local/bin:/opt/local/sbin:/bin:/usr/java/bin:/usr/bin:/usr/sbin:/sbin:/usr/local/bin:/usr/bin/X11
pathByApache = os.getenv("PATH", "Unknown path")
print "pathByApache:               %s" % (pathByApache)

specialPathByApache = os.getenv("SPECIAL_PATH", "Unknown special path")
print "special pathByApache:       %s" % (specialPathByApache)

dPathByApache = os.getenv("D", "Unknown D path")
print "d pathByApache:             %s" % (dPathByApache)

log = sys.stderr.write
log('Hello CGI, is this not a problem')


from psycopg2.extras import DictCursor #@UnusedImport
print "Done with:             from psycopg2.extras import DictCursor"
