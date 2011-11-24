#!/usr/bin/env python
import os
import platform
import sys
import time
#from psycopg2.extras import DictCursor

# CGI header
print "Content-Type: text/plain\n\n"
print "Hello world by hard link\n"

user = os.getenv("USER", "Unknown user")
machine = os.getenv("HOST", "Unknown host") #only works with (t)csh shell
osType = None
ncpus = None
on = "%s (%s/%s/%scores/%s)" % (machine, osType, platform.architecture()[0], ncpus, sys.version.split()[0])
at = time.asctime()
pid = os.getpid()
at = '(%d) ' %  pid + at
#    atForFileName = "%s" % at
#    atForFileName = re.sub('[ :]', '_', atForFileName)
print "User: %-10s on: %-42s at: %32s\n" % (user, on, at)

pathByApache = os.getenv("PATH", "Unknown path")
print "pathByApache: %s\n" % (pathByApache)

specialPathByApache = os.getenv("SPECIAL_PATH", "Unknown special path")
print "special pathByApache: %s\n" % (specialPathByApache)

log = sys.stderr.write
log('Hello CGI, is this an error?\n')

