#!/usr/bin/env python
#@PydevCodeAnalysisIgnore # pylint: disable-all
from cing.Libs.NTutils import * #@UnusedWildImport
from queen.main import * #@UnusedWildImport

# THE TEXT HEADER
def txt_header():
  print"**********************************************************"
  print"*                      Q U E E N                         *"
  print"* QUantitative Evaluation of Experimental Nmr restraints *"
  print"**********************************************************"
  print"*     Written in 2003-2004 by s.nabuurs@cmbi.kun.nl      *"
  print"*     CMBI, University of Nijmegen, The Netherlands      *"
  print"**********************************************************"
  print"*              For help: restraints.py -h                *"
  print"**********************************************************"
  print
  sys.stdout.flush()

# CHECK PYTHON VERSION
version = nmv_checkpython()

# OPTION PARSER
usage = "usage: %prog [option] restraintfile"
parser = optparse.OptionParser(usage=usage,version="%prog 1.1")
parser.add_option("-c","--check",action="store_true",dest="check",
                  help="check restraint file")
parser.add_option("-g","--group",action="store_true",dest="group",
                  help="group restraint file in IR,SQ,MR and LR restraint files")
parser.add_option("-v","--visualize",action="store_true",dest="visualize",
                  help="visualize restraints in YASARA")
parser.add_option("-p",action="store",dest="pdbfile",
                  type="string",help="pdb file required for visualization")
parser.add_option("-n",action="store",dest="number",default=10000,
                  type="int",help="number of restraint to visualize")
parser.add_option("-o",action="store",dest="file",
                  type="string",help="output restraint file")
parser.add_option("-d",action="store_true",dest="dihedral",
                  help="read dihedral angle restraints")
(options,args) = parser.parse_args()


# SHOW TEXT HEADER
txt_header()

# DECIDE ON DISTANCE OR DIHEDRAL RESTRAINTS
if options.dihedral: type="DIHE"
else: type="DIST"
# GROUP RESTRAINTS
if options.group:
  if type!="DIST": nTerror("Only distance restraints can be grouped")
  else:
    groupout = rfile_group(args[0])
    filelist = groupout[0]
    irl,sql,mrl,lrl = groupout[1],groupout[2],groupout[3],groupout[4]
    rsum = irl+sql+mrl+lrl
    print "Wrote %i restraints to file."%rsum
    print "- %5i intra residual restraints (IR)."%irl
    print "- %5i sequential restraints (SQ)."%sql
    print "- %5i medium range restraints (MR)."%mrl
    print "- %5i long range restraints. (LR)"%lrl
    print
    print "The output files:"
    for file in filelist:
      print file
# CHECK RESTRAINTS
if options.check:
  tbl = args[0]
  restraints,doubles,selfrefs = rfile_check(tbl,options.file,type=type)
  print "The restraint file of type %s seems to contain:"%type
  print "- %5i valid restraints."%restraints
  print "- %5i double restraints."%doubles
  print "- %5i self referencing restraints."%selfrefs
# VISUALIZE RESTRAINTS
if options.visualize:
  # CHECK FOR YASARA
  if os.path.exists(nmvconf["YASARA"]):
    # CHECK IF A PDB FILE IS PROVIDED
    if not options.pdbfile: nTerror("Please provide a PDB file (-p PDBFILE option)")
    tbl = args[0]
    rfile_visualize(tbl,options.pdbfile,nmvconf["YASARA"],options.number)
  else:
    nTerror("YASARA not found! Adjust YASARA path in queen.conf")
