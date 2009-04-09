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
  print"*               For help: generate.py -h                 *"
  print"**********************************************************"
  print
  sys.stdout.flush()


# CHECK PYTHON VERSION
version = nmv_checkpython()

# READ THE QUEEN CONFIGURATION FILE
nmvconf = dct_read(os.path.join(sys.path[0],'queen.conf'))

# OPTION PARSER
usage = "usage: %prog [option] projectname [inputfile]"
parser = optparse.OptionParser(usage=usage,version="%prog 1.1")
parser.add_option("-c","--project",action="store_true",dest="create",
                  help="create project (no inputfile required)")
parser.add_option("-s","--pdb2seq",action="store_true",dest="pdb2seq",
                  help="generate sequence file from pdb")
parser.add_option("-p","--seq2psf",action="store_true",dest="seq2psf",
                  help="generate psf file from sequence")
parser.add_option("-t","--psf2tem",action="store_true",dest="psf2tem",
                  help="generate template from psf file")
parser.add_option("-a","--pdb2all",action="store_true",dest="pdb2all",
                  help="generate sequence,psf and template from pdb file")
parser.add_option("-x",action="store_true",dest="xplor",
                  default=0,help="XPLOR pdb file flag")
(options,args) = parser.parse_args()

# SHOW TEXT HEADER
txt_header()

# SET SOME PATHS
top = nmvconf["Q_TOP"]
pep = nmvconf["Q_PEP"]
par = nmvconf["Q_PAR"]
xpl = nmvconf["XPLOR"]

if len(args) >= 1:
  project = args[0]
  projectpath = os.path.join(nmvconf["Q_PROJECT"],project)
  # CREATE PROJECT
  if options.create:
    qn_createproject(nmvconf,project)
  # CHECK OF PATH EXISTS
  if os.path.exists(projectpath):
    # PDB2ALL
    if options.pdb2all:
      pdbfile = args[1]
      seqfile = os.path.join(projectpath,nmvconf["Q_SEQ"])
      if options.xplor: xplorflag = 1
      else: xplorflag = 0
      qn_pdb2seq(pdbfile,seqfile,xplorflag)
      patches = {}
      # CHECK FOR DISULFIDES
      disulfidefile = os.path.join(projectpath,nmvconf["Q_DISULFIDES"])
      if os.path.exists(disulfidefile):
        patches.update(qn_readdisulfides(disulfidefile))
      # CHECK FOR OTHER PATCHES
      patchesfile = os.path.join(projectpath,nmvconf["Q_PATCHES"])
      if os.path.exists(patchesfile):
        patches.update(qn_readpatches(patchesfile))
      # BUILD PSF FILE
      psffile = os.path.join(projectpath,nmvconf["Q_PSF"])
      xplor_buildstructure(psffile,seqfile,'sequence',top,pep,xpl,patches=patches)
      # RENUMBER PSF FILE
      inpsf = "%s.prenum"%psffile
      shutil.copy(psffile,inpsf)
      xplor_renumberpsf(inpsf,psffile,pdbfile,xplorflag)
      # BUILD TEMPLATE
      temfile = os.path.join(projectpath,nmvconf["Q_TEMPLATE"])
      xplor_generatetemplate(temfile,psffile,par,xpl)
    # PDB2SEQ
    if options.pdb2seq:
      pdbfile = args[1]
      seqfile = os.path.join(projectpath,nmvconf["Q_SEQ"])
      if options.xplor: xplorflag = 1
      else: xplorflag = 0
      qn_pdb2seq(pdbfile,seqfile,xplorflag)
    # SEQ2PSF
    if options.seq2psf:
      seqfile = args[1]
      psffile = os.path.join(projectpath,nmvconf["Q_PSF"])
      patches = {}
      # CHECK FOR DISULFIDES
      disulfidefile = os.path.join(projectpath,nmvconf["Q_DISULFIDES"])
      if os.path.exists(disulfidefile):
        patches.update(qn_readdisulfides(disulfidefile))
      # CHECK FOR OTHER PATCHES
      patchesfile = os.path.join(projectpath,nmvconf["Q_PATCHES"])
      if os.path.exists(patchesfile):
        patches.update(qn_readpatches(patchesfile))
      psffile = os.path.join(projectpath,nmvconf["Q_PSF"])
      xplor_buildstructure(psffile,seqfile,'sequence',top,pep,xpl,patches=patches)
    # PSF2TEM
    if options.psf2tem:
      psffile = args[1]
      temfile = os.path.join(projectpath,nmvconf["Q_TEMPLATE"])
      xplor_generatetemplate(temfile,psffile,par,xpl)
  else:
    error("Create project first (-c option)")

