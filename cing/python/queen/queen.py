#!/usr/bin/env python

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
  print"*                For help: queen.py -h                   *"
  print"**********************************************************"
  print
  sys.stdout.flush()

# CHECK PYTHON VERSION
version = nmv_checkpython()

# OPTION PARSER
usage = "usage: %prog [option] project dataset"
parser = optparse.OptionParser(usage=usage,version="%prog 1.1")
parser.add_option("-c","--check",action="store_true",dest='check',
                  help="check validity of dataset")
parser.add_option("-i","--icheck",action="store_true",dest='icheck',
                  help="iteratively check validity of restraints")
parser.add_option("-s","--Iset",action="store_true",dest="iset",
                  help="calculate set information")
parser.add_option("-u","--Iuni",action="store_true",dest="iuni",
                  help="calculate unique restraint information")
parser.add_option("-a","--Iave",action="store_true",dest="iave",
                  help="calculate average restraint information")
parser.add_option("-f","--Iavef",action="store_true",dest="iavef",
                  help="calculate average restraint information\
                  (faster, but less accurate algorithm)")
parser.add_option("-o","--Isort",action="store_true",dest="sort",
                  help="sort restraints by information")
parser.add_option("-p","--plot",action="store_true",dest="plot",
                  help="plot Iave versus Iuni")
parser.add_option("-m",action="store_true",dest="mpi",
                  default=0,help="mpi flag")
(options,args) = parser.parse_args()

# CHECK IF WE NEED TO IMPORT PYPAR
if options.mpi:
  import pypar
  numproc = pypar.size()
  myid = pypar.rank()
  sys.stdout.flush()
else:
  numproc,myid = 1,0


# READ THE QUEEN CONFIGURATION FILE
nmvconf = dct_read(os.path.join(sys.path[0],'queen.conf'))

# SHOW TEXT HEADER
if myid==0: txt_header()

# OPTIONS TAKE TWO ARGUMENTS
if len(args)==2:
  # PRINT WARNING FOR Iave CALCULATIONS
  if (options.iave or options.iavef) and numproc == 1:
    print "WARNING: You are running an Iave calculation on 1 processor."
    print "         This can be very time consuming, we suggest to run"
    print "         these calculations on a Linux cluster.\n"
  project = args[0]
  dataset = args[1]
  if numproc==1: print "Initializing QUEEN."
  else: print "Initializing QUEEN on processor %i of %i."%(myid+1,numproc)
  # SETUP QUEEN
  queen = qn_setup(nmvconf,project,myid,numproc)
  xplr  = qn_setupxplor(nmvconf,project)
  # TAKE THE SELECTED OPTION
  if options.check:
    # CHECK VALIDITY OF DATASET
    qn_checkdata(queen,xplr,dataset)
  if options.icheck:
    # ITERATIVELY CHECK VALIDITY OF RESTRAINTS
    qn_checkdata(queen,xplr,dataset,iterate=1)
  if options.iset:
    # CALCULATE SET INFORMATION
    qn_setinformation(queen,xplr,dataset)
  elif options.iuni:
    # CALCULATE Iuni
    qn_infuni(queen,xplr,dataset)
  elif options.iave:
    # CALCULATE Iave
    convcutoff = float(nmvconf["IAVE_CUTOFF"])
    qn_infave(queen,xplr,dataset,convcutoff=convcutoff)
  elif options.iavef:
    # CALCULATE Iavef
    ncycles = int(nmvconf["IAVEF_NCYCLES"])
    qn_infave_fast(queen,xplr,dataset,ncycles=ncycles)
  elif options.sort:
    # SORT RESTRAINTS WITH MOST INFORMATIVE FIRST
    qn_infsort(queen,xplr,dataset)
  elif options.plot:
    # PLOT Iave VS Iuni
    qn_avevsuni(queen,xplr,dataset)
    # WRITE SORTED RESTRAINTTABLE
    qn_sorttbl(queen,xplr,dataset)
else:
  error("Provide projectname and dataset as arguments")
