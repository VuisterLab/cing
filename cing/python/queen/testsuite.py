#!/usr/bin/env python
#@PydevCodeAnalysisIgnore

# ADD QUEEN SOURCE TO SYSTEM PATH
import sys,os

sys.path += [os.path.join(sys.path[0],'src/py'),
             os.path.join(sys.path[0],'src/c'),
             os.path.join(sys.path[0],'src/3rd-party')]

# DO IMPORTS
import optparse
from qn import *

# THE TEXT HEADER
def txt_header():
  print"**********************************************************"
  print"*                      Q U E E N                         *"
  print"* QUantitative Evaluation of Experimental Nmr restraints *"
  print"**********************************************************"
  print"*     Written in 2003-2004 by s.nabuurs@cmbi.kun.nl      *"
  print"*     CMBI, University of Nijmegen, The Netherlands      *"
  print"**********************************************************"
  print"*                    testsuite.py                        *"
  print"**********************************************************"
  print

txt_header()

# CHECK PYTHON
print "Checking your Python version."
print "  Found Python version %s."%sys.version.split()[0]
nmv_checkpython()
print

# READ THE QUEEN CONFIGURATION FILE
print "Checking your configuration file (queen.conf)."
nmvconf = dct_read(os.path.join(sys.path[0],'queen.conf'))
print "  Checking if Q_PATH is correct...",
if not os.path.normpath(nmvconf["Q_PATH"])==os.path.normpath(os.getcwd()):
  print "No."
  error("  Please set Q_PATH to the QUEEN installation directory.")
else:
  print "Yes."
print "  Checking if Q_PROJECT exists...",
if not os.path.exists(nmvconf["Q_PROJECT"]):
  print "No."
  error("  Please set Q_PROJECT to your projects directory.")
else:
  print "Yes."
print "  Checking if XPLOR path is correct...",
if not os.path.exists(nmvconf["XPLOR"]):
  print "No."
  error("  Please set the correct path for XPLOR")
else:
  print "Yes."
print

print "Testing QUEEN..."
# TEST WITH THE EXAMPLE
print "  Temporarily switching Q_PROJECT to the example/ directory..."
nmvconf["Q_PROJECT"]=nmvconf["Q_PATH"]
project,dataset = 'example','all'
# SETUP QUEEN
print "  Initializing QUEEN...",
queen = qn_setup(nmvconf,project,0,1)
xplr  = qn_setupxplor(nmvconf,project)
print "Ok."
print "  Reading test set of restraints...",
table = nmv_adjust(queen.table,'test')
r = restraint_file(table,'r')
r.read()
print "Ok."
print "  Calculating and validating output...",
sys.stdout.flush()
score = queen.uncertainty(xplr,{"DIST":r.restraintlist})
print score
if "%13.11f"%score=="4.55017471313":
  print "Installation ok."
else:
  print "Problem."
  print "  Outcome of procedure not as expected."
  print
  print "Please don't change the restraint file 'test.tbl' in the example directory!"
  print "If you did so, please restore the directory to it's original state"
  print "and run the testsuite again."
print
