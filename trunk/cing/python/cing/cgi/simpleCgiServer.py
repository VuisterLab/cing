#!PYTHON_EXECUTABLE
import os
print "Content-Type: text/html"     # HTML is following
print                               # blank line, end of headers
print "<TITLE>CGI script output</TITLE>"
print "<H1>This is my first CGI script</H1>"
print "Hello, worldddd!"
print "Hello, CING!"

# Localized by ant build.xml script.

import sys
sys.path.insert(0, "CING_ROOT_PYTHON")
#os.putenv('HOME', '/Users/jd/Sites/tmp/cing') # not recommended on mac os for memory leaks may occur.

# Note that other environment variables needed by CING need to be inhereted from
# the script that started apache by using the PassEnv directive in the apache
# settings file.

keyList = os.environ.keys()
keyList.sort()
for key in keyList:
    print "<p>key:", key, 'value:', os.environ[key]
    
# Localized by ant build.xml script.

from cgi import FieldStorage
from cing import cingDirTmp
import cgitb; 


#import cgi
#". Do not use "from cgi import *" -- the module defines all sorts of names for its own use or for backward compatibility that you don't want in your namespace.

cgitb.enable(display=0, logdir=cingDirTmp)

form = FieldStorage()
if not (form.has_key("ACCESS_KEY") and 
        form.has_key("PROJECT_FILE") 
        ):
    print "<H1>Error</H1>"
    print "Please fill in the name, addr and userfile fields."
    sys.exit(1)

print "<p>ACCESS_KEY:", form["ACCESS_KEY"].value
#print "<p>PROJECT_FILE:", form["PROJECT_FILE"].value


fileitem = form["PROJECT_FILE"]
if not fileitem.file:
    print "<H1>Error</H1>"
    print "Please provide a PROJECT_FILE actual file."
    sys.exit(1)
    
if fileitem.done == -1:
    print "<H1>Error</H1>"
    print "The send file was not 'done' please retry."
    sys.exit(1)
    
# It's an uploaded file; count lines
linecount = 0
while 1:
    line = fileitem.file.readline()
    if not line: break
    linecount +=  1
print "<p>file linecount:", `linecount`

#    If an error is encountered when obtaining the contents of an uploaded file (for example, when the user interrupts the form 
#submission by clicking on a Back or Cancel button) the done attribute of the object for the field will be set to the value -1.

